import bpy
import mathutils
from loaders.nodeLoader import load_nodes
from config import NODE_CSV, COPY_NODE_IDS, SB_GROUPS
from utils.logging_utils import setup_logging

log = setup_logging()

def duplicate_hierarchy(obj, parent=None, location=None, new_name=None):

    obj_copy = obj.copy()
    obj_copy.data = obj.data
    if new_name:
        obj_copy.name = new_name
    bpy.context.collection.objects.link(obj_copy)

    # 複製時のワールド行列
    orig_matrix = obj.matrix_world.copy()

    # 1. location指定でのみ親だけ移動
    if parent is None and location is not None:
        obj_copy.location = mathutils.Vector(location)
    else:
        obj_copy.matrix_world = orig_matrix

    # 2. アニメーション消去
    if obj_copy.animation_data:
        obj_copy.animation_data_clear()

    # 3. 子をまだ親なしで複製、ワールド位置を合わせる
    child_copies = []
    for child in obj.children:
        child_copy = duplicate_hierarchy(child, parent=None)
        child_copy.matrix_world = child.matrix_world.copy()
        child_copies.append(child_copy)

    # 4. 子を親にする直前の行列記録
    for child_copy in child_copies:
        # 設定前にchild_copyのmatrix_worldを退避
        child_world = child_copy.matrix_world.copy()
        child_copy.parent = obj_copy
        # 親をつけた直後にchild_copyのmatrix_parent_inverseを**ワールド変換から算出**
        child_copy.matrix_parent_inverse = obj_copy.matrix_world.inverted() @ child_world

    return obj_copy


def copy_selected_nodes():
    bpy.context.scene.frame_set(1)
    
    node_dict = load_nodes(path=NODE_CSV, filter_ids=COPY_NODE_IDS, mode="copy")

    for src_id, node_id_set in SB_GROUPS.items():
        template_name = f"TBAGS_Node_{src_id}"
        src_obj = bpy.data.objects.get(template_name)
        if not src_obj:
            log.info(f"copy_selected_nodes: Template object '{template_name}' not found.")
            continue

        for node_id in node_id_set:
            if node_id in node_dict:
                pos = node_dict[node_id].pos
                new_name = f"TBAGS_Node_{node_id}"
                duplicate_hierarchy(
                    src_obj,
                    parent=None,
                    location=pos,
                    new_name=new_name
                )
            else:
                log.info(f"copy_selected_nodes: Node id not found : {node_id}")

    bake_and_remove_constraints_on_duplicated_armatures()

def bake_and_remove_constraints_on_duplicated_armatures(frame_start=None, frame_end=None, only_selected=False):
    # 1. 対象アーマチュアのリスト
    if only_selected:
        armatures = [obj for obj in bpy.context.selected_objects if obj.type == 'ARMATURE']
    else:
        armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']

    if not armatures:
        return

    # 2. フレーム範囲の自動取得（未指定時は全アニメ範囲）
    if frame_start is None or frame_end is None:
        scene = bpy.context.scene
        frame_start = scene.frame_start
        frame_end = scene.frame_end

    # 3. Bake（見た目通りの動きをキーフレーム化、Constraint自動削除）
    bpy.ops.nla.bake(
        frame_start=frame_start,
        frame_end=frame_end,
        only_selected=only_selected,
        visual_keying=True,
        clear_constraints=True,
        use_current_action=True,
        bake_types={'POSE'},
    )