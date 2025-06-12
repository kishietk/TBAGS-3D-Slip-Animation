"""
ノード球Blenderオブジェクトの生成ビルダー
- ノードIDと座標を受け、Blender上に静的な球体のみ生成
- アニメーション・キーフレーム処理は一切持たない（責任分離）
"""

import bpy
from mathutils import Vector
from typing import Dict
from utils.logging_utils import setup_logging
from cores.nodeCore import Node
from builders.labels import create_label
from configs import LABEL_SIZE, LABEL_OFFSET

log = setup_logging()


def build_nodes(
    nodes: Dict[int, Node],  # Node型または {pos, kind_id}を持つdict型
    radius: float,
) -> Dict[int, bpy.types.Object]:
    """
    ノード座標からBlender球体（ノード球）を静的に生成する
    ※アニメーション処理はここでは行わない

    Args:
        nodes (Dict[int, Node]): ノードID→Nodeインスタンス または (pos, kind_id) を持つdict
        radius (float): 球体半径
    Returns:
        Dict[int, bpy.types.Object]: ノードID→Blenderオブジェクトの辞書
    """
    objs: Dict[int, bpy.types.Object] = {}
    for nid, node in nodes.items():
        # Node型かdict/tupleか判定し、安全に座標(Vector)を取り出す
        if hasattr(node, "pos"):
            pos = node.pos
        elif isinstance(node, (list, tuple)):
            pos = node[0]
        elif isinstance(node, dict) and "pos" in node:
            pos = node["pos"]
        else:
            log.error(f"Node {nid}: Could not extract position! Skipping.")
            continue

        # Vector型でなければ変換
        if not isinstance(pos, Vector):
            try:
                pos = Vector(pos)
            except Exception as e:
                log.error(f"Node {nid}: Invalid position value {pos}: {e}")
                continue

        try:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=pos)
            obj = bpy.context.object
            obj.name = f"Node_{nid}"
            objs[nid] = obj
            log.debug(f"Node sphere {nid} created at {tuple(pos)} (radius={radius})")
        except Exception as e:
            log.error(f"Failed to create node sphere for ID {nid}: {e}")
    return objs


def create_node_labels(
    nodes: Dict[int, Vector],
    abs_size: float = LABEL_SIZE,
    offset: Vector = LABEL_OFFSET,
) -> None:
    """
    ノード球体にノードIDラベルを付与

    Args:
        nodes (Dict[int, Vector]): ノードID→座標
        abs_size (float): ラベル文字サイズ
        offset (Vector): ラベル配置オフセット
    Returns:
        None
    """
    for nid, pos in nodes.items():
        node_name = f"Node_{nid}"
        obj = bpy.data.objects.get(node_name)
        if not obj:
            log.warning(f"Node object '{node_name}' not found for label creation")
            continue
        create_label(
            obj,
            str(nid),
            abs_size=abs_size,
            offset=offset,
            name_prefix="Label",
            use_constraint=True,
        )
