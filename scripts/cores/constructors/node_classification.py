# builders/scene_builders/scene_utils.py

from typing import Dict, Iterable, Tuple
from configs import SANDBAG_NODE_KIND_IDS
from cores.entities.node_core import Node


def split_nodes_by_kind(
    nodes: Iterable[Node],
) -> Tuple[Dict[int, Node], Dict[int, Node]]:
    """
    全ノードを通常ノード／サンドバッグ用ノードに分割して返す。
    Returns: (normal_nodes, sandbag_nodes)
    """
    normal_nodes: Dict[int, Node] = {}
    sandbag_nodes: Dict[int, Node] = {}
    for n in nodes:
        if n.kind_id in SANDBAG_NODE_KIND_IDS:
            sandbag_nodes[n.id] = n
        else:
            normal_nodes[n.id] = n
    return normal_nodes, sandbag_nodes