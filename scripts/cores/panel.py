from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.node import Node
    from cores.edge import Edge


class Panel:
    """
    パネル（面）クラス
    """

    def __init__(
        self,
        node_ids: List[int],
        nodes: List["Node"],
        edges: List["Edge"],
        kind_label: str = "",
    ):
        self.node_ids = node_ids
        self.nodes = nodes
        self.edges = edges
        self.kind_label = kind_label

        for edge in edges:
            edge.add_panel(self)

    def __repr__(self):
        return (
            f"Panel(node_ids={self.node_ids}, kind_label={self.kind_label}, "
            f"nodes={[n.id for n in self.nodes]}, edges={[e.id for e in self.edges]})"
        )
