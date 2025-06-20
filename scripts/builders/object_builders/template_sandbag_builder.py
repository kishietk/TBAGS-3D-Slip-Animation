"""
ファイル名: builders/object_builders/template_sandbag_builder.py

責務:
- サンドバッグノードごとに、外部 .blend テンプレートからオブジェクト群をアペンド＆複製し、
  Empty＋メイン Mesh/Armature をシーンに配置する。
- ボーン名・頂点グループ名をノード ID ベースでリネームし、Armature→Mesh の親子関係を再設定。
- FICTION_NODE_IDS に含まれるノードはスキップ。

返り値:
  { node_id: bpy.types.Object }  # 複製した“メイン”Mesh（またはArmature）
"""

import bpy
from typing import Dict, Any, Tuple
from utils.logging_utils import setup_logging
from builders.base import BuilderBase
from configs import TBAGS_TEMPLATE_BLEND, FICTION_NODE_IDS

log = setup_logging("TemplateSandbagBuilder")


class TemplateSandbagBuilder(BuilderBase):

    def __init__(self, nodes: Dict[int, Any], cube_size: Tuple[float, float, float]):
        """
        nodes: ノードID → Node インスタンス（または pos 属性を持つオブジェクト）の辞書
        """
        super().__init__()
        self.nodes = nodes

    def build(self) -> Dict[int, bpy.types.Object]:
        """
        役割:
            各 node_id, node.pos に対してテンプレートをアペンド＆複製し、
            Empty + メイン Mesh を返却用マップに登録する。
        """
        result: Dict[int, bpy.types.Object] = {}

        for node_id, node in self.nodes.items():
            if node_id in FICTION_NODE_IDS:
                log.debug(f"Node {node_id} は FICTION_NODE_IDS に含まれるためスキップ")
                continue

            pos = getattr(node, "pos", None) or (
                node[0] if isinstance(node, (list, tuple)) else None
            )
            if pos is None:
                log.error(f"Node {node_id} の位置が取得できずスキップ")
                continue

            try:
                # --- 1) テンプレートからアペンド ---
                with bpy.data.libraries.load(TBAGS_TEMPLATE_BLEND, link=False) as (
                    src,
                    dst,
                ):
                    dst.objects = src.objects
                    dst.armatures = src.armatures

                # 2) Empty を作成
                empty = bpy.data.objects.new(f"TBAGS_Node_{node_id}", None)
                bpy.context.scene.collection.objects.link(empty)
                empty.location = tuple(pos)

                # 3) 複製＆リンク
                orig_to_copy = {}
                arm_copies, mesh_copies = [], []

                for orig in dst.objects:
                    if orig is None:
                        continue
                    copy = orig.copy()
                    if orig.data:
                        copy.data = orig.data.copy()
                    bpy.context.scene.collection.objects.link(copy)
                    copy.parent = empty
                    copy.parent_type = "OBJECT"
                    orig_to_copy[orig] = copy

                    if copy.type == "ARMATURE":
                        arm_copies.append((orig, copy))
                    elif copy.type == "MESH":
                        mesh_copies.append((orig, copy))

                # 4) ボーン／頂点グループリネーム
                bone_map = {}
                base = str(node_id)
                # bottom_id の算出ルールは既存ロジックに準じる
                if base.startswith("1"):
                    bottom = "3" + base[1:]
                elif base.startswith("5"):
                    bottom = "11" + base[1:]
                elif base.startswith("2"):
                    bottom = "4" + base[1:]
                elif base.startswith("6"):
                    bottom = "12" + base[1:]
                else:
                    bottom = None

                if bottom:
                    bone_map = {"top": base, "bottom": bottom}

                for orig, arm in arm_copies:
                    bpy.context.view_layer.objects.active = arm
                    bpy.ops.object.mode_set(mode="EDIT")
                    ebones = arm.data.edit_bones
                    for old, new in bone_map.items():
                        if old in ebones:
                            ebones[old].name = new
                    bpy.ops.object.mode_set(mode="OBJECT")

                for orig, mesh in mesh_copies:
                    for vg in mesh.vertex_groups:
                        if vg.name in bone_map:
                            vg.name = bone_map[vg.name]
                    # Armature モディファイアのターゲット調整
                    for mod in mesh.modifiers:
                        if mod.type == "ARMATURE":
                            tgt = orig_to_copy.get(mod.object)
                            if tgt:
                                mod.object = tgt
                    mesh.parent = orig_to_copy.get(
                        next((o for o, c in arm_copies if c == mesh), None), empty
                    )
                    mesh.parent_type = (
                        "ARMATURE"
                        if isinstance(mesh.parent, bpy.types.Object)
                        else "OBJECT"
                    )

                # 5) メイン Mesh/Armature を選択して返却
                main = (
                    mesh_copies[0][1]
                    if mesh_copies
                    else (arm_copies[0][1] if arm_copies else None)
                )
                if main:
                    result[node_id] = main
                    log.info(f"Node {node_id}: テンプレート複製完了 → {main.name}")
                else:
                    log.warning(
                        f"Node {node_id}: 複製されたメインオブジェクトが見つかりません"
                    )

            except Exception as e:
                log.error(f"Node {node_id}: テンプレート複製でエラー: {e}")

        log.info(f"{len(result)} 件のサンドバッグ（テンプレート版）を生成しました")
        return result
