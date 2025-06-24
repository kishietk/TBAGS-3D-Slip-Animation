# cores/entities/sandbag_unit.py

from typing import List
from mathutils import Vector
from .node_core import Node


class Sandbag:
    """
    2ノードで構成されるサンドバッグユニットのデータモデル。
    Attributes:
        nodes (List[NodeCore])
        id (str)
        centroid (Vector)
        z_values (List[float])
    """

    def __init__(self, nodes: List[Node]):
        assert len(nodes) == 2, "requires exactly 2 nodes"
        sorted_nodes = sorted(nodes, key=lambda n: n.pos.z)
        self.nodes = sorted_nodes
        self.id = f"{sorted_nodes[0].id}_{sorted_nodes[1].id}"
        self.centroid = (sorted_nodes[0].pos + sorted_nodes[1].pos) / 2
        self.z_values = [n.pos.z for n in sorted_nodes]

    def __repr__(self) -> str:
        ids = [n.id for n in self.nodes]
        return (
            f"SandbagUnit(id={self.id}, nodes={ids}, centroid={tuple(self.centroid)})"
        )
