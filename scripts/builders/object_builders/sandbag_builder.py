# builders/object_builders/sandbag_builder.py

"""
ファイル名: builders/object_builders/sandbag_builder.py

責務:
- コアの SandbagNode／Node オブジェクト群を受け取り、
  各位置に直方体サンドバッグを生成する。
- ノードID→Blender Object（基点Empty）辞書を返却し、後段のユニットビルダーやアニメーション処理と連携しやすい設計。

TODO:
- 入力型（Node／dict／tuple）統一、型ヒント強化
- 立方体サイズ・座標のバリデーション追加
- 物理シミュレーション設定との分離
"""

import bpy
from mathutils import Vector
from typing import Dict, Tuple
from utils.logging_utils import setup_logging
from builders.base import BuilderBase
from cores.nodeCore import Node
from configs.paths import TBAGS_MODEL
from configs.kind_labels import SANDBAG_NODE_KIND_IDS

log = setup_logging("SandbagBuilder")


class SandbagBuilder(BuilderBase):
    def __init__(
        self,
        nodes: Dict[int, Node],
        cube_size: Tuple[float, float, float],
    ):
        """
        初期化:
            nodes: ノードID→Node（または pos 属性を持つオブジェクト）マップ
            cube_size: (X, Y, Z) 各辺サイズ
        """
        super().__init__()
        self.nodes = nodes
        self.cube_size = cube_size
        self.log = log

    def build(self) -> Dict[int, bpy.types.Object]:
        """
        役割:
            各ノード位置にサンドバッグを生成し、ノードID→基点Empty辞書を返す。
        """
        objs: Dict[int, bpy.types.Object] = {}
        for nid, node in self.nodes.items():
            # Node の kind_id でテンプレート対象を判定
            if getattr(node, "kind_id", None) not in SANDBAG_NODE_KIND_IDS:
                self.log.debug(f"Node {nid} is not a sandbag node, skipping template.")
                continue

            # 位置取得
            pos = getattr(node, "pos", None) or getattr(node, "location", None)
            if pos is None:
                self.log.warning(f"Node {nid} に位置情報がありません。スキップします。")
                continue

            # Vector 型に変換
            if not isinstance(pos, Vector):
                try:
                    pos = Vector(pos)
                except Exception as e:
                    self.log.error(f"Node {nid} の位置 Vector 変換失敗: {e}")
                    continue

            try:
                # テンプレートから Empty＋Mesh を複製
                empty, _ = self._append_from_template(nid, pos)
                objs[nid] = empty
            except Exception as e:
                self.log.warning(
                    f"Node {nid} テンプレート複製失敗: {e} フォールバックでキューブを生成します。"
                )
                cube = self._create_cube(nid, pos)
                objs[nid] = cube

        self.log.info(f"{len(objs)} 件のサンドバッグ用 Empty を生成しました。")
        return objs

    def _append_from_template(self, node_id: int, location: Vector):
        """
        テンプレート.blend からサンドバッグを複製し、Empty とメインMesh を返却
        """
        # テンプレートから読み込み
        with bpy.data.libraries.load(TBAGS_MODEL, link=False) as (data_from, data_to):
            data_to.objects = data_from.objects
            data_to.armatures = data_from.armatures
        originals = data_to.objects

        node_name = f"Node_{node_id}"
        base = str(node_id)
        bottom = None
        if base.startswith("1"):
            bottom = "3" + base[1:]
        elif base.startswith("5"):
            bottom = "11" + base[1:]
        elif base.startswith("2"):
            bottom = "4" + base[1:]
        elif base.startswith("6"):
            bottom = "12" + base[1:]

        # Empty（基点）作成
        empty = bpy.data.objects.new(f"TBAGS_{node_name}", None)
        bpy.context.scene.collection.objects.link(empty)
        empty.location = location

        orig_to_copy: Dict[bpy.types.Object, bpy.types.Object] = {}
        linked_armatures = []
        linked_meshes = []
        # 複製・リンク
        for orig in originals:
            if orig is None:
                continue
            new_obj = orig.copy()
            if orig.data:
                new_obj.data = orig.data.copy()
            bpy.context.scene.collection.objects.link(new_obj)
            new_obj.parent = empty
            new_obj.parent_type = "OBJECT"
            orig_to_copy[orig] = new_obj
            if new_obj.type == "ARMATURE":
                linked_armatures.append((orig, new_obj))
            elif new_obj.type == "MESH":
                linked_meshes.append((orig, new_obj))

        # ボーン・頂点グループリネーム
        if bottom:
            bone_map = {"top": base, "bottom": bottom}
            # Armature リネーム
            for orig_arm, new_arm in linked_armatures:
                bpy.context.view_layer.objects.active = new_arm
                bpy.ops.object.mode_set(mode="EDIT")
                for old_name, new_name in bone_map.items():
                    if old_name in new_arm.data.edit_bones:
                        new_arm.data.edit_bones[old_name].name = new_name
                bpy.ops.object.mode_set(mode="OBJECT")
            # Mesh の vertex group と親子付け修正
            for orig_mesh, new_mesh in linked_meshes:
                for vg in new_mesh.vertex_groups:
                    if vg.name in bone_map:
                        vg.name = bone_map[vg.name]
                for mod in new_mesh.modifiers:
                    if mod.type == "ARMATURE" and mod.object in orig_to_copy:
                        mod.object = orig_to_copy[mod.object]
                        new_mesh.parent = mod.object
                        new_mesh.parent_type = "ARMATURE"

        # メインMesh を取得して返却（Empty の基点と組で返す）
        main_mesh = (
            linked_meshes[0][1]
            if linked_meshes
            else (linked_armatures[0][1] if linked_armatures else empty)
        )
        self.log.debug(f"Template mesh for Node {node_id}: {main_mesh.name}")
        return empty, main_mesh

    def _create_cube(self, node_id: int, location: Vector):
        """
        フォールバック: 立方体プリミティブでサンドバッグを生成
        """
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
        obj = bpy.context.object
        obj.name = f"Sandbag_{node_id}"
        sx, sy, sz = self.cube_size
        obj.scale = (sx / 2, sy / 2, sz / 2)
        self.log.debug(
            f"Fallback cube Sandbag_{node_id} created at {tuple(location)} size={self.cube_size}"
        )
        return obj


# def duplicate_sandbags_hierarchy(obj, parent=None, location_offset=Vector((0,0,0)), name_prefix="Copy_"):
#     """
#     オブジェクトの再帰的複製ユーティリティ（未使用）
#     """
#     obj_copy = obj.copy()
#     obj_copy.data = obj.data.copy() if obj.data else None
#     obj_copy.name = name_prefix + obj.name
#     bpy.context.collection.objects.link(obj_copy)
#     obj_copy.location += location_offset
#     if parent:
#         obj_copy.parent = parent
#     for child in obj.children:
#         duplicate_sandbags_hierarchy(child, obj_copy, location_offset, name_prefix)
#     return obj_copy
