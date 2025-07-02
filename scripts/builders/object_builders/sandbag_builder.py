"""
ファイル名: builders/object_builders/sandbag_builder.py

責務:
    - SandbagUnitごとの情報を受け取り、各ユニットにつき1つのEmptyと
      1つのArmature（2ボーン：top/bottom）を生成
    - 生成したオブジェクトを辞書構造でまとめて返却し、
      handler側で各ボーンを個別にアニメーション可能とする

戻り値:
    Dict[unit_id, Dict[str, bpy.types.Object]] 形式の辞書
    {
        "empty":           Emptyオブジェクト,
        "armature_top":    Armature,
        "armature_bottom": Armature,  # どちらも同じArmature（2ボーン）
    }
"""

import bpy
from mathutils import Vector
from typing import Any, Dict, List, Tuple
from utils import setup_logging, to_vector
from builders.base import BuilderBase
from configs.paths import TBAGS_MODEL
from configs import SANDBAG_OBJ_PREFIX, CUBE_DEFAULT_SIZE
from .cube_builder import create_cube

log = setup_logging("SandbagBuilder")


class SandbagBuilder(BuilderBase):
    """
    SandbagUnit情報をもとにEmpty＋Armatureを生成し辞書で返却するビルダークラス
    （テンプレートは1Armature2ボーンでOK）
    """

    def __init__(self, units_info: List[Dict[str, Any]]):
        super().__init__()
        self.units_info = units_info
        self.log = log

    def build(self) -> Dict[Any, Dict[str, bpy.types.Object]]:
        objs: Dict[Any, Dict[str, bpy.types.Object]] = {}

        for info in self.units_info:
            uid = info.get("unit_id")
            rep = info.get("rep_node")
            other = info.get("other_node")

            # 代表ノード位置をVector化
            pos = to_vector(rep)
            if pos is None:
                self.log.warning(f"unit {uid}: 代表ノード位置未設定、スキップします。")
                continue
            if not isinstance(pos, Vector):
                try:
                    pos = Vector(pos)
                except Exception as e:
                    self.log.error(f"unit {uid}: 位置Vector変換失敗: {e}")
                    continue

            # テンプレートからEmpty+Mesh/Armatureを複製
            try:
                empty, _main = self._append_from_template(uid, pos)
                self.log.debug(f"unit {uid}: テンプレートからEmpty生成成功。")
            except Exception as e:
                self.log.warning(
                    f"unit {uid}: テンプレート複製失敗({e})、キューブ生成で代替します。"
                )
                empty = create_cube(uid, pos, cube_size=CUBE_DEFAULT_SIZE)

            # カスタムプロパティ設定
            empty["sandbag_unit_id"] = uid
            empty["rep_node_id"] = getattr(rep, "id", None)
            empty["other_node_id"] = getattr(other, "id", None)
            empty["bone_pos_rep"] = tuple(pos)
            other_pos = (
                getattr(other, "pos", None) or getattr(other, "location", None) or pos
            )
            if not isinstance(other_pos, Vector):
                try:
                    other_pos = Vector(other_pos)
                except Exception:
                    other_pos = pos
            empty["bone_pos_other"] = tuple(other_pos)

            # Armature取得
            armatures = [c for c in empty.children if c.type == "ARMATURE"]
            if armatures:
                armature = armatures[0]
                self.log.debug(
                    f"unit {uid}: Armature取得: {armature.name}, ボーン名: {[b.name for b in armature.pose.bones]}"
                )
                # top/bottomボーン存在確認
                if not all(name in armature.pose.bones for name in ("top", "bottom")):
                    self.log.warning(
                        f"unit {uid}: Armatureに'top'または'bottom'ボーンがありません！"
                    )
                # 両方とも同じArmatureで登録
                objs[uid] = {
                    "empty": empty,
                    "armature_top": armature,
                    "armature_bottom": armature,
                }
            else:
                self.log.warning(
                    f"unit {uid}: Armatureが見つかりません。Emptyを代用します。"
                )
                objs[uid] = {
                    "empty": empty,
                    "armature_top": empty,
                    "armature_bottom": empty,
                }

            # メッシュにArmatureモディファイアをセット（必須）
            for child in empty.children:
                if child.type == "MESH" and armatures:
                    # 上面/下面で分けたい場合はmodifier名で区別もOK（ここでは両方Armatureを参照させる）
                    mod_top = child.modifiers.new(name="ArmatureTop", type="ARMATURE")
                    mod_top.object = armatures[0]
                    mod_bottom = child.modifiers.new(
                        name="ArmatureBottom", type="ARMATURE"
                    )
                    mod_bottom.object = armatures[0]

            # Empty のカスタムプロパティをArmatureにコピー
            for prop in (
                "sandbag_unit_id",
                "rep_node_id",
                "other_node_id",
                "bone_pos_rep",
                "bone_pos_other",
            ):
                if armatures and prop in empty:
                    armatures[0][prop] = empty[prop]

            self.log.debug(
                f"unit {uid}: empty={empty.name}, armature={armatures[0].name if armatures else 'None'}"
            )

        self.log.info(
            f"{len(objs)} 件のサンドバッグユニット用 Empty＋Armature を生成しました。"
        )
        return objs

    def _append_from_template(
        self, unit_id: Any, location: Vector
    ) -> Tuple[bpy.types.Object, bpy.types.Object]:
        with bpy.data.libraries.load(TBAGS_MODEL, link=False) as (src, dst):
            dst.objects = src.objects
            dst.armatures = src.armatures
        originals = dst.objects

        # Emptyを生成＆シーンリンク
        empty = bpy.data.objects.new(f"{SANDBAG_OBJ_PREFIX}{unit_id}", None)
        bpy.context.scene.collection.objects.link(empty)
        empty.location = location

        linked_meshes: List[bpy.types.Object] = []
        linked_armatures: List[bpy.types.Object] = []

        for orig in originals:
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
