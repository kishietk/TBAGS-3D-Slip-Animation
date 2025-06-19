import bpy
import mathutils
from mathutils import Vector
from config import TBAGS_model, FICTION_NODE_IDS
from utils.logging_utils import setup_logging

log = setup_logging()

def append_sandbag_from_template_get_mainmesh(node_id, location):
    """
    指定ノードID・位置でテンプレートからサンドバッグを複製し、
    - ボーン名をノードIDにリネーム
    - EmptyとメインMesh/Armatureを返す
    """
    import bpy

    # テンプレートからオブジェクトをアペンド
    with bpy.data.libraries.load(TBAGS_model, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects
        data_to.armatures = data_from.armatures
    original_objects = data_to.objects

    node_name = f"Node_{node_id}"
    base_number = str(node_id)
    # bottom_number自動生成
    if base_number[0] == "1":
        bottom_number = "3" + base_number[1:]
    elif base_number[0] == "5":
        bottom_number = "11" + base_number[1:]
    elif base_number[0] == "2":
        bottom_number = "4" + base_number[1:]
    elif base_number[0] == "6":
        bottom_number = "12" + base_number[1:]
    else:
        bottom_number = None

    # Empty作成
    empty = bpy.data.objects.new(f"TBAGS_{node_name}", None)
    bpy.context.scene.collection.objects.link(empty)
    empty.location = (0.0, 0.0, 0.0)

    orig_to_copy = {}
    linked_armatures = []
    linked_meshes = []

    for orig in original_objects:
        if orig is None:
            continue
        new_obj = orig.copy()
        if orig.data:
            new_obj.data = orig.data.copy()
        bpy.context.scene.collection.objects.link(new_obj)
        new_obj.parent = empty
        new_obj.parent_type = 'OBJECT'
        orig_to_copy[orig] = new_obj
        if new_obj.type == 'ARMATURE':
            linked_armatures.append((orig, new_obj))
        elif new_obj.type == 'MESH':
            linked_meshes.append((orig, new_obj))

    # Empty配置
    empty.location = location

    # ボーン・頂点グループリネーム（Editモード推奨!）
    bone_rename_map = {}
    if bottom_number:
        bone_rename_map = {"top": base_number, "bottom": bottom_number}
        for orig_arm, new_arm in linked_armatures:
            # Editモードでボーン名変更
            bpy.context.view_layer.objects.active = new_arm
            bpy.ops.object.mode_set(mode='EDIT')
            ebones = new_arm.data.edit_bones
            for old_bone, new_bone in bone_rename_map.items():
                if old_bone in ebones:
                    ebones[old_bone].name = new_bone
            bpy.ops.object.mode_set(mode='OBJECT')

        for orig_mesh, new_mesh in linked_meshes:
            for vg in new_mesh.vertex_groups:
                if vg.name in bone_rename_map:
                    vg.name = bone_rename_map[vg.name]
            # モディファイア・親子付け
            for mod in orig_mesh.modifiers:
                if mod.type != 'ARMATURE':
                    continue
                orig_target_arm = mod.object
                if orig_target_arm not in orig_to_copy:
                    continue
                new_target_arm = orig_to_copy[orig_target_arm]
                if mod.name in new_mesh.modifiers:
                    new_mesh.modifiers[mod.name].object = new_target_arm
                else:
                    for nm in new_mesh.modifiers:
                        if nm.type == 'ARMATURE':
                            nm.object = new_target_arm
                            break
                new_mesh.parent = new_target_arm
                new_mesh.parent_type = 'ARMATURE'

    # メインMesh/Armatureを選んで返す
    main_mesh = linked_meshes[0][1] if linked_meshes else (linked_armatures[0][1] if linked_armatures else None)
    return empty, main_mesh


def build_sandbags_from_template(sandbag_nodes):
    """
    sandbag_nodes: {ノードID: Node} の辞書
    template_path: サンドバッグテンプレート.blendファイルのパス
    各ノードごとにappend_sandbag_from_templateでテンプレート複製
    """
    sandbag_objs = {}
    for nid, node in sandbag_nodes.items():
        if nid not in FICTION_NODE_IDS:
            empty, main_mesh = append_sandbag_from_template_get_mainmesh(
                node_id=nid,
                location=node.pos if hasattr(node, "pos") else node[0]
            )
        sandbag_objs[nid] = main_mesh  # メッシュ本体を登録
    return sandbag_objs

# def duplicate_sandbags_hierarchy(obj, parent=None, location_offset=mathutils.Vector((0,0,0)), name_prefix="Copy_"):
#     # オブジェクトの複製
#     obj_copy = obj.copy()
#     obj_copy.data = obj.data.copy() if obj.data else None
#     obj_copy.name = name_prefix + obj.name
#     bpy.context.collection.objects.link(obj_copy)
    
#     # 位置をオフセット
#     obj_copy.location += location_offset
    
#     # 親設定
#     if parent:
#         obj_copy.parent = parent
    
#     # 子オブジェクトも再帰的に複製
#     for child in obj.children:
#         duplicate_sandbags_hierarchy(child, obj_copy, location_offset, name_prefix)
    
#     return obj_copy
