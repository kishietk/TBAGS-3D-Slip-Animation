# builders/nodes.py

import bpy
from typing import Dict
from utils.logging import setup_logging
from config import NODE_LABEL_SIZE, NODE_LABEL_OFFSET
from mathutils import Vector, Quaternion

log = setup_logging()

"""
nodes.py

【役割 / Purpose】
- ノード球・ノードラベルをBlender上に生成（将来「非表示/省略」に対応しやすいよう整理）。
- ノード球は「表示OFF」や「生成省略」も簡単に切替可能。
- 例外時にはIDや行番号付きで詳細ログ。
"""


def build_nodes(
    nodes: dict[int, Vector],
    radius: float,
    anim_data: dict[int, dict[int, Vector]] | None = None,
    create_spheres: bool = False,  # ← ノード球生成を無効化したい場合はFalse
) -> dict[int, bpy.types.Object]:
    """
    ノード座標リストから球メッシュ（ノード球）をBlender上に生成
    create_spheres=Falseでノード球の生成自体を省略可能

    引数:
        nodes: {nid: Vector}
        radius: 球体半径
        anim_data: {nid: {frame: Vector(dx,dy,dz), ...}, ...}
        create_spheres: ノード球生成を有効化するか

    戻り値:
        objs: {nid: Object}
    """
    objs: dict[int, bpy.types.Object] = {}
    if not create_spheres:
        log.info("Node spheres generation skipped (create_spheres=False)")
        return objs
    for nid, pos in nodes.items():
        try:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=pos)
            o = bpy.context.object
            o.name = f"Node_{nid}"
            objs[nid] = o

            # アニメーションデータがあればキーフレーム登録
            if anim_data and nid in anim_data:
                for frame, offset in anim_data[nid].items():
                    o.location = pos + offset
                    o.keyframe_insert(data_path="location", frame=frame)
        except Exception as e:
            log.error(f"Failed to create node sphere for ID {nid}: {e}")
    return objs


def create_node_labels(
    nodes: dict[int, Vector],
    radius: float,
    create_labels: bool = False,  # ← ラベル生成も今後不要ならFalseで
) -> None:
    """
    各ノード球に対応するラベル（ノードID）をTextオブジェクトとして追加し、
    ノード球の子オブジェクトとする
    create_labels=Falseで生成自体を省略可
    """
    from math import radians

    if not create_labels:
        log.info("Node label generation skipped (create_labels=False)")
        return

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
            text_obj.rotation_euler = (radians(90), 0, 0)  # テキストを水平に

            text_obj.parent = node_obj
            text_obj.location = Vector(NODE_LABEL_OFFSET)
        except Exception as e:
            log.error(f"Failed to create label for node {nid}: {e}")


def clear_scene() -> None:
    """
    シーン内の全オブジェクトを一括削除し、完全クリア状態にする
    """
    try:
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()
    except Exception as e:
        log.error(f"Failed to clear Blender scene: {e}")
