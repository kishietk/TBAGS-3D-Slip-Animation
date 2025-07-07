import bpy
from mathutils import Vector
from typing import Any, Dict, List, Tuple
from utils import setup_logging, to_vector
from builders.base import BuilderBase
from configs.paths import TBAGS_MODEL
from configs import SANDBAG_OBJ_PREFIX, CUBE_DEFAULT_SIZE
from .cube_builder import create_cube
from cores.entities.sandbag_core import Sandbag

log = setup_logging("SandbagBuilder")


class SandbagBuilder(BuilderBase):
    """
    List[Sandbag] を受け取り、
    各サンドバッグごとに Empty と Armature を生成するビルダークラス。

    build() は以下の辞書を返します:
        Dict[sandbag_id, Dict[str, bpy.types.Object]]
        {
            'empty':    Empty オブジェクト,
            'armature': Armature オブジェクト (単一)
        }
    """

    def __init__(self, sandbags: List[Sandbag]):
        super().__init__()
        self.sandbags = sandbags

    def build(self) -> Dict[Any, Dict[str, bpy.types.Object]]:
        log.info("=================[サンドバックをビルド]=========================")
        results: Dict[Any, Dict[str, bpy.types.Object]] = {}
        for sandbag in self.sandbags:
            sid = sandbag.id
            # ノード情報
            high_node, low_node = sandbag.nodes
            log.debug(
                f"Sandbag[{sid}]: raw high_node.pos={high_node.pos}, low_node.pos={low_node.pos}"
            )

            # 1) Bone 用位置取得 (top=高側, bottom=低側)
            top_pos, bottom_pos = self._get_positions(sandbag)
            log.debug(
                f"Sandbag[{sid}]: computed top_pos={top_pos}, bottom_pos={bottom_pos}"
            )
            log.info(f"Added sandbag: ({high_node.id}, {low_node.id})")

            # 2) Empty＋テンプレート複製（失敗時はキューブ）
            empty = self._create_empty_container(sid, bottom_pos)

            # 3) 単一 Armature 検出
            armature = self._find_armature(empty, sid)

            # 4) メッシュへ Armature モディファイア追加
            self._apply_modifiers(empty, armature)

            # 5) プロパティ設定
            props = {
                "sandbag_id": sid,
                "top_node_id": high_node.id,
                "bottom_node_id": low_node.id,
                "bone_top_pos": tuple(top_pos),
                "bone_bottom_pos": tuple(bottom_pos),
            }
            for tgt in (empty, armature):
                for k, v in props.items():
                    tgt[k] = v

            # 6) 結果格納
            results[sid] = {"empty": empty, "armature": armature}

        return results

    def _get_positions(self, sandbag: Sandbag) -> Tuple[Vector, Vector]:
        high_node, low_node = sandbag.nodes
        # to_vector が None を返す可能性もあるためチェック
        raw_top = high_node.pos
        raw_bottom = low_node.pos
        top_pos = to_vector(raw_top)
        bottom_pos = to_vector(raw_bottom)
        if top_pos is None:
            log.error(f"Sandbag[{sandbag.id}]: high_node.pos is None (raw: {raw_top})")
            raise ValueError(f"Sandbag {sandbag.id} high_node.pos is None")
        if bottom_pos is None:
            log.warning(
                f"Sandbag[{sandbag.id}]: low_node.pos is None (raw: {raw_bottom}), using top_pos"
            )
            bottom_pos = top_pos
        return top_pos, bottom_pos

    def _create_empty_container(self, uid: Any, location: Vector) -> bpy.types.Object:
        try:
            empty, _ = self._append_from_template(uid, location)
        except Exception as e:
            log.warning(
                f"サンドバッグ[{uid}]: テンプレート複製失敗 ({e})、キューブで代替します。"
            )
            empty = create_cube(uid, location, cube_size=CUBE_DEFAULT_SIZE)
        return empty

    def _find_armature(self, empty: bpy.types.Object, uid: Any) -> bpy.types.Object:
        """
        empty 配下を再帰的に検索し、最初の ARMATURE オブジェクトを返す。
        見つからなければ empty を返す。
        """
        arms = [c for c in empty.children_recursive if c.type == "ARMATURE"]
        if arms:
            log.debug(f"Sandbag[{uid}]: found armature {arms[0].name}")
            return arms[0]
        log.warning(
            f"サンドバッグ[{uid}]: アーマチュアなし。EmptyをArmatureとして使用します。"
        )
        return empty

    def _apply_modifiers(
        self, empty: bpy.types.Object, armature: bpy.types.Object
    ) -> None:
        for child in empty.children:
            if child.type == "MESH":
                mod = child.modifiers.new("Armature", "ARMATURE")
                mod.object = armature
                log.debug(f"Applied Armature modifier on mesh {child.name}")

    def _append_from_template(
        self, unit_id: Any, location: Vector
    ) -> Tuple[bpy.types.Object, bpy.types.Object]:
        with bpy.data.libraries.load(TBAGS_MODEL, link=False) as (src, dst):
            dst.objects = src.objects
            dst.armatures = src.armatures

        empty = bpy.data.objects.new(f"{SANDBAG_OBJ_PREFIX}{unit_id}", None)
        bpy.context.scene.collection.objects.link(empty)
        empty.location = location

        meshes, arms = [], []
        for orig in dst.objects:
            if orig is None:
                continue
            cp = orig.copy()
            if orig.data:
                cp.data = orig.data.copy()
            bpy.context.scene.collection.objects.link(cp)
            cp.parent = empty
            cp.matrix_parent_inverse = empty.matrix_world.inverted()
            if cp.type == "MESH":
                meshes.append(cp)
                log.debug(f"Copied mesh {cp.name} under empty {empty.name}")
            elif cp.type == "ARMATURE":
                arms.append(cp)
                log.debug(f"Copied armature {cp.name} under empty {empty.name}")

        main = arms[0] if arms else (meshes[0] if meshes else empty)
        return empty, main
