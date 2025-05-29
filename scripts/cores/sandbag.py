# cores/sandbag.py
"""
サンドバッグノードのコアクラス定義
- ノードID・座標・kind_id・floor属性などを保持
- 他ノード型（Node）とインターフェースを合わせておくと一貫性UP
"""

from mathutils import Vector
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.panel import Panel
    from cores.edge import Edge


class SandbagNode:
    """
    サンドバッグノード（立方体で表示される特殊ノード）
    """

    def __init__(
        self,
        id: int,
        pos: Vector,
        floor: Optional[str] = None,
        kind_id: Optional[int] = None,
    ):
        self.id = id
        self.pos = pos
        self.floor = floor
        self.kind_id = kind_id
        self.edges: List["Edge"] = []
        self.panels: List["Panel"] = []

    def add_edge(self, edge: "Edge") -> None:
        if edge not in self.edges:
            self.edges.append(edge)

    def add_panel(self, panel: "Panel") -> None:
        if panel not in self.panels:
            self.panels.append(panel)

    def __repr__(self) -> str:
        return (
            f"SandbagNode(id={self.id}, pos={tuple(self.pos)}, floor={self.floor}, "
            f"kind_id={self.kind_id}, edges={len(self.edges)}, panels={len(self.panels)})"
        )
