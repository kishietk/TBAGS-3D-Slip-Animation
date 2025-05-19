from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from mathutils import Vector

if TYPE_CHECKING:
    from cores.edge import Edge
    from cores.panel import Panel

"""
node.py

【役割 / Purpose】
- 構造グラフの「ノード（接点）」情報を表現するコアクラス。
- 座標、ID、階層、関連エッジ/パネルのリストを保持。
- エッジ・パネル側からadd_edge/add_panelで双方向参照を実現。

【設計方針】
- 追加属性も柔軟に拡張可（例：floor属性、ラベル属性など）。
- 型ヒント・現場向けコメント徹底。
"""


class Node:
    """
    ノード情報（ID, 位置, 階層, 所属エッジ・パネル）
    """

    def __init__(self, id: int, pos: Vector, floor: Optional[str] = None):
        self.id: int = id  # ノードID
        self.pos: Vector = pos  # 座標 (mathutils.Vector)
        self.floor: Optional[str] = floor  # 階層属性（任意）
        self.edges: List["Edge"] = []  # 所属エッジリスト
        self.panels: List["Panel"] = []  # 所属パネルリスト

    def __repr__(self):
        return (
            f"Node(id={self.id}, pos={tuple(self.pos)}, floor={self.floor}, "
            f"edges={len(self.edges)}, panels={len(self.panels)})"
        )

    def add_edge(self, edge: "Edge"):
        """
        このノードに関連するエッジを追加（重複防止）
        """
        if edge not in self.edges:
            self.edges.append(edge)

    def add_panel(self, panel: "Panel"):
        """
        このノードに関連するパネルを追加（重複防止）
        """
        if panel not in self.panels:
            self.panels.append(panel)
