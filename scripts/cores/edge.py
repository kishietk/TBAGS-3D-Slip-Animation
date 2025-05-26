from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.node import Node
    from cores.panel import Panel


class Edge:
    """
    エッジ（部材：梁・柱等）のコア基底クラス
    """

    def __init__(
        self,
        node_a: "Node",
        node_b: "Node",
        kind_id: Optional[int] = None,
        kind_label: Optional[str] = None,
    ):
        self.id = tuple(sorted([node_a.id, node_b.id]))
        self.node_a = node_a
        self.node_b = node_b
        self.kind_id = kind_id
        self.kind_label = kind_label
        self.panels: List["Panel"] = []
        self.node_a.add_edge(self)
        self.node_b.add_edge(self)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, kind_id={self.kind_id}, kind_label={self.kind_label}, "
            f"nodes=({self.node_a.id}, {self.node_b.id}), panels={len(self.panels)})"
        )

    def add_panel(self, panel: "Panel"):
        if panel not in self.panels:
            self.panels.append(panel)

    def get_other_node(self, node: "Node") -> "Node":
        if node == self.node_a:
            return self.node_b
        elif node == self.node_b:
            return self.node_a
        else:
            raise ValueError("Edge does not connect to given node")
