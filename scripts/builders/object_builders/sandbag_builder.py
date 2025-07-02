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
    各サンドバッグごとに Empty と上下用アーマチュアを生成するビルダークラス。

    build() は以下の辞書を返します:
        Dict[sandbag_id, Dict[str, bpy.types.Object]]
        {
            'empty':           Empty オブジェクト,
            'armature_top':    上面用 Armature,
            'armature_bottom': 下面用 Armature,
        }
    """

    def __init__(self, sandbags: List[Sandbag]):
        super().__init__()
        self.sandbags = sandbags

    def build(self) -> Dict[Any, Dict[str, bpy.types.Object]]:
        """
        List[Sandbag] を受け取り、
        各サンドバッグごとに Empty＋上下用アーマチュアを生成して返す。
        """
        results: Dict[Any, Dict[str, bpy.types.Object]] = {}

        for sandbag in self.sandbags:
            sandbag_id = sandbag.id
            try:
                # 1) 位置取得
                low_pos, high_pos = self._get_positions(sandbag)

                # 2) Empty＋テンプレート複製（失敗時はキューブ）
                empty = self._create_empty_container(sandbag_id, low_pos)

                # 3) アーマチュア（上面／下面）検出
                top_arm, bottom_arm = self._find_armatures(empty, sandbag_id)

                # 4) メッシュへモディファイア追加
                self._apply_modifiers(empty, top_arm, bottom_arm)

                # 5) プロパティ設定（Empty ＆ Armature）
                self._assign_properties(empty, sandbag, low_pos, high_pos)

                # 6) 結果格納
                results[sandbag_id] = {
                    "empty": empty,
                    "armature_top": top_arm,
                    "armature_bottom": bottom_arm,
                }

            except Exception as e:
                log.warning(f"サンドバッグ[{sandbag_id}]: ビルド失敗({e})")

        log.info(f"{len(results)} 件のサンドバッグを生成しました。")
        return results

    def _get_positions(self, sandbag: Sandbag) -> Tuple[Vector, Vector]:
        low_node, high_node = sandbag.nodes
        low_pos = to_vector(low_node.pos)
        high_pos = to_vector(high_node.pos) or low_pos
        if low_pos is None:
            raise ValueError("low_node の位置未設定")
        return low_pos, high_pos

    def _create_empty_container(self, uid: Any, location: Vector) -> bpy.types.Object:
        try:
            empty, _ = self._append_from_template(uid, location)
        except Exception:
            log.warning(
                f"サンドバッグ[{uid}]: テンプレート複製失敗、キューブで代替します。"
            )
            empty = create_cube(uid, location, cube_size=CUBE_DEFAULT_SIZE)
        return empty

    def _find_armatures(
        self, empty: bpy.types.Object, uid: Any
    ) -> Tuple[bpy.types.Object, bpy.types.Object]:
        arms = [c for c in empty.children if c.type == "ARMATURE"]
        if len(arms) >= 2:
            return arms[0], arms[1]
        if arms:
            log.warning(
                f"サンドバッグ[{uid}]: アーマチュア1つのみ。上下同じものを使用します。"
            )
            return arms[0], arms[0]
        log.warning(f"サンドバッグ[{uid}]: アーマチュアなし。Emptyを代用します。")
        return empty, empty

    def _apply_modifiers(
        self,
        empty: bpy.types.Object,
        top_arm: bpy.types.Object,
        bottom_arm: bpy.types.Object,
    ) -> None:
        for child in empty.children:
            if child.type == "MESH":
                mod_top = child.modifiers.new(name="ArmatureTop", type="ARMATURE")
                mod_top.object = top_arm
                mod_bot = child.modifiers.new(name="ArmatureBottom", type="ARMATURE")
                mod_bot.object = bottom_arm

    def _assign_properties(
        self,
        empty: bpy.types.Object,
        sandbag: Sandbag,
        low_pos: Vector,
        high_pos: Vector,
    ) -> None:
        # 1) Empty にまずセット
        empty["sandbag_id"] = sandbag.id
        empty["low_node_id"] = sandbag.nodes[0].id
        empty["high_node_id"] = sandbag.nodes[1].id
        empty["bone_low_pos"] = tuple(low_pos)
        empty["bone_high_pos"] = tuple(high_pos)

        # 2) 子オブジェクトのうち ARMATURE に同じプロパティをコピー
        props = [
            "sandbag_id",
            "low_node_id",
            "high_node_id",
            "bone_low_pos",
            "bone_high_pos",
        ]
        for child in empty.children:
            if child.type == "ARMATURE":
                for prop in props:
                    child[prop] = empty[prop]

    def _append_from_template(
        self,
        unit_id: Any,
        location: Vector,
    ) -> Tuple[bpy.types.Object, bpy.types.Object]:
        with bpy.data.libraries.load(TBAGS_MODEL, link=False) as (src, dst):
            dst.objects = src.objects
            dst.armatures = src.armatures

        empty = bpy.data.objects.new(f"{SANDBAG_OBJ_PREFIX}{unit_id}", None)
        bpy.context.scene.collection.objects.link(empty)
        empty.location = location

        linked_meshes: List[bpy.types.Object] = []
        linked_armatures: List[bpy.types.Object] = []

        for orig in dst.objects:
            if orig is None:
                continue
            obj_copy = orig.copy()
            if orig.data:
                obj_copy.data = orig.data.copy()
            bpy.context.scene.collection.objects.link(obj_copy)
            obj_copy.parent = empty
            obj_copy.parent_type = "OBJECT"
            obj_copy.location = (0.0, 0.0, 0.0)
            obj_copy.matrix_parent_inverse = empty.matrix_world.inverted()

            if obj_copy.type == "MESH":
                linked_meshes.append(obj_copy)
            elif obj_copy.type == "ARMATURE":
                linked_armatures.append(obj_copy)

        main = (
            linked_meshes[0]
            if linked_meshes
            else (linked_armatures[0] if linked_armatures else empty)
        )
        return empty, main
