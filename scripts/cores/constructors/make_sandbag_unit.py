# cores/constructors/make_sandbag_unit.py

from typing import Dict, List
from collections import defaultdict

from configs.kind_labels import SANDBAG_NODE_KIND_IDS
from cores.entities.node_core import Node
from cores.entities.sandbag_core import Sandbag


def make_sandbag_unit(nodes: Dict[int, Node]) -> List[Sandbag]:
    """
    サンドバッグノードを(X,Y)でグループ化し、2つずつペアにして返す。
    """
    xy_groups: Dict[tuple, List[Node]] = defaultdict(list)
    for node in nodes.values():
        if node.kind_id in SANDBAG_NODE_KIND_IDS:
            key = (round(node.pos.x, 4), round(node.pos.y, 4))
            xy_groups[key].append(node)

    units: List[Sandbag] = []
    for group in xy_groups.values():
        group.sort(key=lambda n: n.pos.z)
        for i in range(0, len(group) - 1, 2):
            units.append(Sandbag(group[i : i + 2]))
    return units
