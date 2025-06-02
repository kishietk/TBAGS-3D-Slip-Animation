"""
サンドバッグノード（SandbagNode）コアクラス
- サンドバッグ専用ノード（立方体表示、IDで種別区別）
- ノードID/座標/種別ID/階層属性/関連エッジ・パネルリストを保持
- Node型インターフェース互換（add_edge/add_panel/properties）

【設計指針】
- node.pyのNode型とメソッド・属性を合わせることで汎用コードから区別不要
- kind_idによりサンドバッグ/ノーマルノードを判別
"""

from mathutils import Vector
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.panelCore import Panel
    from cores.edgeCore import Edge


class SandbagNode:
    """
    サンドバッグノード（立方体で表示される特殊ノード）
    - ID/座標/階層/種別/関連エッジ/パネルを管理
    - Nodeクラス互換API（add_edge, add_panel, __repr__）
    """

    def __init__(
        self,
        id: int,
        pos: Vector,
        floor: Optional[str] = None,
        kind_id: Optional[int] = None,
    ) -> None:
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
            edge (Edge): 紐付けるエッジ
        Returns:
            None
        """
        if edge not in self.edges:
            self.edges.append(edge)

    def add_panel(self, panel: "Panel") -> None:
        """
        関連パネルリストに追加
        Args:
            panel (Panel): 紐付けるパネル
        Returns:
            None
        """
        if panel not in self.panels:
            self.panels.append(panel)

    def __repr__(self) -> str:
        """
        サンドバッグノード情報を可読文字列で返す
        Returns:
            str: ノード情報
        """
        return (
            f"SandbagNode(id={self.id}, pos={tuple(self.pos)}, floor={self.floor}, "
            f"kind_id={self.kind_id}, edges={len(self.edges)}, panels={len(self.panels)})"
        )
