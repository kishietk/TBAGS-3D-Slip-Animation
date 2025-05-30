"""
ノード（Node）コアクラス
- 構造グラフ上のノードID・位置・階層属性・種別ID・
  関連エッジ/パネルリストなどを保持
- Edge/Panelオブジェクトとの相互参照による構造把握

【設計指針】
- id: int, pos: Vector, floor: Optional[str], kind_id: Optional[int]
- add_edge/add_panelで相互リンク構築
- __repr__は構造・デバッグ用に拡張可能
"""

from typing import List, Optional, TYPE_CHECKING
from mathutils import Vector

if TYPE_CHECKING:
    from cores.Edge import Edge
    from cores.Panel import Panel


class Node:
    """
    ノード（接点）コアクラス
    - ノードID・座標・階層・種別・関連エッジ/パネル保持
    - 主要グラフ構造ノード基盤
    """

    def __init__(
        self,
        id: int,
        pos: Vector,
        floor: Optional[str] = None,
        kind_id: Optional[int] = None,
    ) -> None:
        """
        ノードを初期化
        Args:
            id (int): ノードID
            pos (Vector): 座標
            floor (Optional[str]): 階層属性
            kind_id (Optional[int]): ノード種別
        Returns:
            None
        """
        self.id: int = id
        self.pos: Vector = pos
        self.floor: Optional[str] = floor
        self.kind_id: Optional[int] = kind_id
        self.edges: List["Edge"] = []
        self.panels: List["Panel"] = []

    def add_edge(self, edge: "Edge") -> None:
        """
        関連エッジリストに追加
        Args:
            edge (Edge): 追加するエッジ
        Returns:
            None
        """
        if edge not in self.edges:
            self.edges.append(edge)

    def add_panel(self, panel: "Panel") -> None:
        """
        関連パネルリストに追加
        Args:
            panel (Panel): 追加するパネル
        Returns:
            None
        """
        if panel not in self.panels:
            self.panels.append(panel)

    def __repr__(self) -> str:
        """
        ノードの情報を可読文字列で返す
        Returns:
            str: ノード情報
        """
        return (
            f"Node(id={self.id}, pos={tuple(self.pos)}, floor={self.floor}, "
            f"edges={len(self.edges)}, panels={len(self.panels)})"
        )
