import bpy
from mathutils import Vector
from utils.logging_utils import setup_logging
from config import NODE_LABEL_SIZE, NODE_LABEL_OFFSET

log = setup_logging()


def build_nodes(
    nodes: dict[int, Vector],
    radius: float,
    anim_data: dict[int, dict[int, Vector]] | None = None,
) -> dict[int, bpy.types.Object]:
    """
    ノード座標リストからBlender上に球体（ノード球）を生成
    必要に応じてアニメーション（変位量）もキーフレームとして付与
    """
    objs: dict[int, bpy.types.Object] = {}
    for nid, pos in nodes.items():
        try:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=pos)
            o = bpy.context.object
            o.name = f"Node_{nid}"
            objs[nid] = o
            log.debug(f"Node_{nid}: pos={tuple(pos)}, radius={radius}")

            # アニメーションデータがあればキーフレーム登録
            if anim_data and nid in anim_data:
                for frame, offset in anim_data[nid].items():
                    o.location = pos + offset
                    o.keyframe_insert(data_path="location", frame=frame)
        except Exception as e:
            log.error(f"Failed to create node sphere for ID {nid}: {e}")
    return objs


def create_node_labels(nodes: dict[int, Vector], radius: float) -> None:
    """
    各ノード球に対応するラベル（ノードID）をTextオブジェクトとして追加
    ノード球の子オブジェクトとする
    """
    from math import radians

    for nid, pos in nodes.items():
        node_name = f"Node_{nid}"
        if node_name not in bpy.data.objects:
            log.warning(f"Node object '{node_name}' not found for label creation")
            continue
        node_obj = bpy.data.objects[node_name]
        try:
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
            log.debug(f"Label_{nid}: attached to Node_{nid}, offset={NODE_LABEL_OFFSET}")
        except Exception as e:
            log.error(f"Failed to create label for node {nid}: {e}")
