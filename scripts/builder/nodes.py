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
    各ノード球に対応するラベル（ノードID）を、
    ノードオブジェクトの子として作成する。
    """
    from math import radians

    for nid, pos in nodes.items():
        # ノードオブジェクトを取得
        node_name = f"Node_{nid}"
        if node_name not in bpy.data.objects:
            continue
        node_obj = bpy.data.objects[node_name]

        # ラベル用テキスト追加（まずワールド座標に置く必要はありません）
        bpy.ops.object.text_add()
        text_obj = bpy.context.object
        text_obj.name = f"Label_{nid}"
        text_obj.data.body = str(nid)
        text_obj.data.size = NODE_LABEL_SIZE
        text_obj.data.align_x = 'CENTER'
        text_obj.data.align_y = 'CENTER'
        # テキストはX方向に傾けてカメラ向きに
        text_obj.rotation_euler = (radians(90), 0, 0)

        # 親子付け
        text_obj.parent = node_obj
        # 相対オフセットを設定
        text_obj.location = Vector(NODE_LABEL_OFFSET)