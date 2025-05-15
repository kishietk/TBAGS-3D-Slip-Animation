import bpy
from logging_utils import setup_logging
from config import NODE_LABEL_SIZE, NODE_LABEL_OFFSET
from mathutils import Vector, Quaternion

log = setup_logging()

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

def build_nodes(nodes: dict, radius: float):
    log.debug(f"Building {len(nodes)} nodes.")
    objs = {}
    for nid, pos in nodes.items():
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=pos)
        o = bpy.context.object; o.name = f"Node_{nid}"
        objs[nid] = o
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

