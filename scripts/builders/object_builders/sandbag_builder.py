"""
ファイル名: builders/object_builders/sandbag_builder.py

責務:
    - SandbagUnitごとの情報を受け取り、各ユニットにつき1オブジェクト（Empty＋Mesh）を生成
    - 代表ノードと非代表ノード両方の座標をカスタムプロパティとして保持し、アニメーション処理で利用しやすい設計

TODO:
    - units_infoの入力型をTypedDictまたはdataclass化して型安全性を強化
    - cube_sizeの値バリデーション（非負チェックなど）を追加
    - テンプレートファイルパスやボーン名の外部設定化
    - unit_idやnode_idの型統一、エラーハンドリング強化
    - 単体テスト追加: template複製失敗時およびキューブ生成フォールバックの検証
"""

import bpy
from mathutils import Vector
from typing import Dict, List, Any, Tuple
from utils.logging_utils import setup_logging
from builders.base import BuilderBase
from configs.paths import TBAGS_MODEL

log = setup_logging("SandbagBuilder")


class SandbagBuilder(BuilderBase):
    """
    SandbagUnit情報をもとに1オブジェクトを生成し、
    unit_id→Emptyオブジェクト辞書を返却するビルダークラス。
    """

    def __init__(
        self,
        units_info: List[Dict[str, Any]],
        cube_size: Tuple[float, float, float],
    ):
        super().__init__()
        self.units_info = units_info
        self.cube_size = cube_size
        self.log = log

    def build(self) -> Dict[Any, bpy.types.Object]:
        """
        各SandbagUnitにつき1オブジェクトを生成し、
        {unit_id: EmptyObject}の辞書を返す。
        """
        objs: Dict[Any, bpy.types.Object] = {}
        for info in self.units_info:
            uid = info.get("unit_id")
            rep = info.get("rep_node")
            other = info.get("other_node")

            pos = getattr(rep, "pos", None) or getattr(rep, "location", None)
            if pos is None:
                self.log.warning(f"unit {uid}: 代表ノード位置未設定、スキップします。")
                continue
            if not isinstance(pos, Vector):
                try:
                    pos = Vector(pos)
                except Exception as e:
                    self.log.error(f"unit {uid}: 位置Vector変換失敗: {e}")
                    continue

            try:
                empty, _ = self._append_from_template(uid, pos)
            except Exception as e:
                self.log.debug(
                    f"unit {uid}: テンプレート複製失敗({e})、キューブ生成します。"
                )
                empty = self._create_cube(uid, pos)

            empty["sandbag_unit_id"] = uid
            empty["rep_node_id"] = getattr(rep, "id", None)
            empty["other_node_id"] = getattr(other, "id", None)
            empty["bone_pos_rep"] = tuple(pos)

            other_pos = getattr(other, "pos", None) or getattr(other, "location", None)
            if other_pos is None:
                other_pos = pos
            if not isinstance(other_pos, Vector):
                try:
                    other_pos = Vector(other_pos)
                except Exception:
                    other_pos = pos
            empty["bone_pos_other"] = tuple(other_pos)

            objs[uid] = empty

        self.log.info(
            f"{len(objs)} 件のサンドバッグユニットオブジェクトを生成しました。"
        )
        return objs

    def _append_from_template(
        self, unit_id: Any, location: Vector
    ) -> Tuple[bpy.types.Object, bpy.types.Object]:
        """
        TBAGS_MODELテンプレートから複製し、
        (Empty, MainMesh)を返す。
        """
        with bpy.data.libraries.load(TBAGS_MODEL, link=False) as (src, dst):
            dst.objects = src.objects
            dst.armatures = src.armatures
        originals = dst.objects

        empty = bpy.data.objects.new(f"SandbagUnit_{unit_id}", None)
        bpy.context.scene.collection.objects.link(empty)
        empty.location = location

        linked_meshes = []
        linked_armatures = []
        for orig in originals:
            if orig is None:
                continue
            obj_copy = orig.copy()
            if orig.data:
                obj_copy.data = orig.data.copy()
            bpy.context.scene.collection.objects.link(obj_copy)
            obj_copy.parent = empty
            obj_copy.parent_type = "OBJECT"
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

    def _create_cube(self, unit_id: Any, location: Vector) -> bpy.types.Object:
        """
        フォールバック: キューブプリミティブを生成し返却。
        """
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
        cube = bpy.context.object
        cube.name = f"SandbagUnit_{unit_id}"
        sx, sy, sz = self.cube_size
        cube.scale = (sx / 2, sy / 2, sz / 2)
        self.log.debug(
            f"フォールバックキューブ {cube.name} を生成: size={self.cube_size}"
        )
        return cube
