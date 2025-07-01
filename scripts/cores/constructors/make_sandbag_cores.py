from typing import Dict, List, Tuple
from collections import defaultdict

from configs.kind_labels import SANDBAG_NODE_KIND_IDS
from cores.entities.node_core import Node
from cores.entities.sandbag_core import Sandbag


def group_sandbag_pairs(nodes: Dict[int, Node]) -> List[Tuple[Node, Node]]:
    """
    サンドバッグ用ノードを (X, Y) 座標でグループ化し、
    Z 座標順に2つずつペアにして返す。

    Args:
        nodes: ノードID→Node インスタンスのマップ
    Returns:
        生成されたノードペアのリスト
    """
    xy_groups: Dict[Tuple[float, float], List[Node]] = defaultdict(list)
    # 同一XZ平面上のノードを集める
    for node in nodes.values():
        if node.kind_id in SANDBAG_NODE_KIND_IDS:
            key = (round(node.pos.x, 4), round(node.pos.y, 4))
            xy_groups[key].append(node)

    pairs: List[Tuple[Node, Node]] = []
    for group in xy_groups.values():
        # Z 座標でソート
        group.sort(key=lambda n: n.pos.z)
        # 隣接ペアを作成
        for i in range(0, len(group) - 1, 2):
            pairs.append((group[i], group[i + 1]))
    return pairs


def make_sandbag_cores(nodes: Dict[int, Node]) -> List[Sandbag]:
    """
    group_sandbag_pairs で得られたノードペアから、
    Sandbag コアデータクラスのインスタンスを作成して返す。

    Args:
        nodes: ノードID→Node インスタンスのマップ
    Returns:
        Sandbag インスタンスのリスト
    """
    pairs = group_sandbag_pairs(nodes)
    cores: List[Sandbag] = []
    for n1, n2 in pairs:
        cores.append(Sandbag([n1, n2]))
    return cores
