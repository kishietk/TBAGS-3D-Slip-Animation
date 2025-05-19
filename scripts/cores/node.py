from __future__ import annotations
from typing import List, TYPE_CHECKING
from mathutils import Vector
if TYPE_CHECKING:
    from cores.edge import Edge
    from cores.panel import Panel


class Node:
    """
    ノード（接点）コアクラス
    """

    def __init__(self, nid: int, pos: Vector):
        self.id = id
        self.pos = pos  # Vector型 or (x, y, z) tuple
        self.edges: List["Edge"] = []
        self.panels: List["Panel"] = []

    def __repr__(self):
        return f"Node(id={self.id}, pos={self.pos})"

    def add_edge(self, edge: "Edge"):
        if edge not in self.edges:
            self.edges.append(edge)

    def add_panel(self, panel: "Panel"):
        if panel not in self.panels:
            self.panels.append(panel)
