"""
ファイル名: builders/object_builders/sandbag_builder.py

責務:
    - SandbagUnitごとの情報を受け取り、各ユニットにつき1つのEmptyと
        2つのArmature（twist／bend）オブジェクトを生成
    - 生成したオブジェクトを辞書構造でまとめて返却し、
        handler側で各Armatureを別々にアニメーション可能とする

戻り値:
    Dict[unit_id, Dict[str, bpy.types.Object]] 形式の辞書
    {
        "empty":           Emptyオブジェクト,
        "armature_twist":  Twist用Armature,
        "armature_bend":   Bend用Armature,
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
    SandbagUnit情報をもとに以下を生成し辞書で返却するビルダークラス:
    {
        unit_id: {
            "empty": Empty,
            "armature_twist": Armature(ねじり用),
            "armature_bend":  Armature(曲げ用),
        },
        ...
    }
    """

    def __init__(
        self,
        units_info: List[Dict[str, Any]],
    ):
        super().__init__()
        self.units_info = units_info
        self.log = log

    def build(self) -> Dict[Any, Dict[str, bpy.types.Object]]:
        """
        各SandbagUnitにつきEmpty＋2Armatureを生成し、
        {unit_id: {...}} の辞書を返す。

        Twist用／Bend用それぞれのArmatureを取り出しやすく設計。
        """
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
            except Exception as e:
                self.log.warning(
                    f"unit {uid}: テンプレート複製失敗({e})、キューブ生成で代替します。"
                )
                # ← 定数から cube_size, 名前プレフィックス
                empty = create_cube(uid, pos, cube_size=CUBE_DEFAULT_SIZE)

            # -----------------------------
            # Empty に共通カスタムプロパティ設定
            # -----------------------------
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

            # ---------------------------------------
            # Empty の子オブジェクトから全Armatureを取得
            # ---------------------------------------
            armatures = [c for c in empty.children if c.type == "ARMATURE"]
            if len(armatures) >= 2:
                twist_arm, bend_arm = armatures[0], armatures[1]
            elif armatures:
                # 1つしかない場合は両方同じものを参照
                twist_arm = bend_arm = armatures[0]
            else:
                # なければEmpty自体を代用
                twist_arm = bend_arm = empty
                self.log.warning(
                    f"unit {uid}: Armatureが見つかりません。Emptyを代用します。"
                )

            # ───────────────────────────────────────
            # Empty配下のメッシュにArmatureモディファイアをセット
            # ───────────────────────────────────────
            for child in empty.children:
                if child.type == "MESH":
                    # ねじり用アーマチュア
                    mod_twist = child.modifiers.new(
                        name="ArmatureTwist", type="ARMATURE"
                    )
                    mod_twist.object = twist_arm
                    # 曲げ用アーマチュア
                    mod_bend = child.modifiers.new(name="ArmatureBend", type="ARMATURE")
                    mod_bend.object = bend_arm

            # ---------------------------------------
            # Empty のカスタムプロパティを両Armatureにコピー
            # ---------------------------------------
            for prop in (
                "sandbag_unit_id",
                "rep_node_id",
                "other_node_id",
                "bone_pos_rep",
                "bone_pos_other",
            ):
                if prop in empty:
                    twist_arm[prop] = empty[prop]
                    bend_arm[prop] = empty[prop]

            # unit_id→構造体をマップ
            objs[uid] = {
                "empty": empty,
                "armature_twist": twist_arm,
                "armature_bend": bend_arm,
            }

        self.log.info(
            f"{len(objs)} 件のサンドバッグユニット用 Empty＋2Armature を生成しました。"
        )
        return objs

    def _append_from_template(
        self, unit_id: Any, location: Vector
    ) -> Tuple[bpy.types.Object, bpy.types.Object]:
        """
        TBAGS_MODELテンプレートからEmpty＋Mesh/Armatureを複製し、
        (EmptyObject, MainMeshOrArmature) を返却。
        """
        with bpy.data.libraries.load(TBAGS_MODEL, link=False) as (src, dst):
            dst.objects = src.objects
            dst.armatures = src.armatures
        originals = dst.objects

        # Emptyを生成＆シーンリンク（定数で統一）
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

        # メインオブジェクトは Mesh優先 → Armature → Empty
        main = (
            linked_meshes[0]
            if linked_meshes
            else (linked_armatures[0] if linked_armatures else empty)
        )
        return empty, main
