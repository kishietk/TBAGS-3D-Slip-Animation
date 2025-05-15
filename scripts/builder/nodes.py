import bpy
from logging_utils import setup_logging
from config import NODE_LABEL_SIZE, NODE_LABEL_OFFSET
from mathutils import Vector, Quaternion

log = setup_logging()

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

def build_nodes(nodes: dict, radius: float, anim_data: dict = None):
    objs = {}
    for nid, pos in nodes.items():
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=pos)
        o = bpy.context.object
        o.name = f"Node_{nid}"
        objs[nid] = o

        # アニメーションがある場合：位置＋変位をキーフレームに登録
        if anim_data and nid in anim_data:
            for frame, offset in anim_data[nid].items():
                o.location = pos + offset
                o.keyframe_insert(data_path="location", frame=frame)
    return objs


def create_node_labels(nodes: dict, radius: float):
    """
    各ノード球に対応するラベル（ノードID）を作成。
    configで定義されたオフセット方向に配置される。
    """
    from math import radians
    for nid, pos in nodes.items():
        label_pos = pos + Vector(NODE_LABEL_OFFSET)
        bpy.ops.object.text_add(location=label_pos)
        text_obj = bpy.context.object
        text_obj.name = f"Label_{nid}"
        text_obj.data.body = str(nid)
        text_obj.data.size = NODE_LABEL_SIZE
        text_obj.data.align_x = 'CENTER'
        text_obj.data.align_y = 'CENTER'
        # 水平表示（上向き、カメラから見える）
        text_obj.rotation_euler = (radians(90), 0, 0)

