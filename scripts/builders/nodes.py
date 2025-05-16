import bpy
from typing import Dict
from logging_utils import setup_logging
from config import NODE_LABEL_SIZE, NODE_LABEL_OFFSET
from mathutils import Vector, Quaternion

log = setup_logging()


def clear_scene() -> None:
    """
    シーン内の全オブジェクトを削除し、完全クリア状態にする
    """
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def build_nodes(
    nodes: dict[int, Vector],
    radius: float,
    anim_data: dict[int, dict[int, Vector]] | None = None,
) -> dict[int, bpy.types.Object]:
    """
    ノード座標リストから球メッシュ（ノード球）をBlender上に生成する
    必要に応じてアニメーション（変位量）もキーフレームとして付与

    引数:
        nodes: {nid: Vector}
        radius: float
        anim_data: {nid: {frame: Vector(dx,dy,dz), ...}, ...}

    戻り値:
        objs: {nid: Object}
    """
    objs: dict[int, bpy.types.Object] = {}
    for nid, pos in nodes.items():
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=pos)
        o = bpy.context.object
        o.name = f"Node_{nid}"
        objs[nid] = o

        # アニメーションデータがあれば、キーフレーム登録
        if anim_data and nid in anim_data:
            for frame, offset in anim_data[nid].items():
                o.location = pos + offset
                o.keyframe_insert(data_path="location", frame=frame)
    return objs


def create_node_labels(nodes: dict[int, Vector], radius: float) -> None:
    """
    各ノード球に対応するラベル（ノードID）をTextオブジェクトとして追加し、
    ノード球の子オブジェクトとする
    """
    from math import radians

    for nid, pos in nodes.items():
        node_name = f"Node_{nid}"
        if node_name not in bpy.data.objects:
            continue
        node_obj = bpy.data.objects[node_name]

        bpy.ops.object.text_add()
        text_obj = bpy.context.object
        text_obj.name = f"Label_{nid}"
        text_obj.data.body = str(nid)
        text_obj.data.size = NODE_LABEL_SIZE
        text_obj.data.align_x = "CENTER"
        text_obj.data.align_y = "CENTER"
        text_obj.rotation_euler = (radians(90), 0, 0)

        text_obj.parent = node_obj
        text_obj.location = Vector(NODE_LABEL_OFFSET)
