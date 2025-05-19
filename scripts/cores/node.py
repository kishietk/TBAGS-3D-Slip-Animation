from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from mathutils import Vector

if TYPE_CHECKING:
    from cores.edge import Edge
    from cores.panel import Panel


class Node:
    """
    ノード情報のコアクラス。
    """

    def __init__(self, id: int, pos: Vector, floor: Optional[str] = None):
        self.id: int = id
        self.pos: Vector = pos
        self.floor: Optional[str] = floor
        self.edges: List["Edge"] = []
        self.panels: List["Panel"] = []

    def __repr__(self):
        return (
            f"Node(id={self.id}, pos={tuple(self.pos)}, floor={self.floor}, "
            f"edges={len(self.edges)}, panels={len(self.panels)})"
        )

    def add_edge(self, edge: "Edge"):
        if edge not in self.edges:
            self.edges.append(edge)

    def add_panel(self, panel: "Panel"):
        if panel not in self.panels:
            self.panels.append(panel)
