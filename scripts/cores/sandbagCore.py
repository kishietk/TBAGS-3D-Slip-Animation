"""
ファイル名: cores/sandbagCore.py

責務:
- サンドバッグ専用ノード（SandbagNode）コアクラスを定義。
- ノードID・座標・種別ID・階層属性・関連エッジ/パネルを管理し、Node型インターフェースと互換。

設計指針:
- nodeCore.pyのNode型と属性・メソッドを合わせ、汎用コード側での分岐不要に設計。
- kind_idでサンドバッグ/通常ノードを一元判別。

TODO:
- Node/SandbagNodeの二重管理の責務を再検討（継承構造や型共通化も視野）
- add_edge/add_panelの責務をSandbagNodeが持つ設計の是非
- dataclass等による実装統一も検討
"""

from mathutils import Vector
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.panelCore import Panel
    from cores.edgeCore import Edge


class SandbagNode:
    """
    役割:
        サンドバッグ専用ノード（立方体で表示される特殊ノード）コアクラス。
        ノードID/座標/階層/種別/関連エッジ/パネルを管理。
        Node型インターフェース（add_edge, add_panel, __repr__）とも互換。
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
        役割:
            関連エッジをこのノードに追加（重複不可）。
        引数:
            edge (Edge)
        返り値:
            なし
        """
        if edge not in self.edges:
            self.edges.append(edge)

    def add_panel(self, panel: "Panel") -> None:
        """
        役割:
            関連パネルをこのノードに追加（重複不可）。
        引数:
            panel (Panel)
        返り値:
            なし
        """
        if panel not in self.panels:
            self.panels.append(panel)

    def __repr__(self) -> str:
        """
        役割:
            サンドバッグノードの主要属性・接続数を可読文字列で返す。
        返り値:
            str
        """
        return (
            f"SandbagNode(id={self.id}, pos={tuple(self.pos)}, floor={self.floor}, "
            f"kind_id={self.kind_id}, edges={len(self.edges)}, panels={len(self.panels)})"
        )
