"""
ファイル名: cores/nodeCore.py

責務:
- 構造グラフ上のノード（Node）コアクラスを定義。
- ノードID・位置・階層・種別ID・関連エッジ/パネルの管理と、相互参照APIを提供。

設計指針:
- id: int, pos: Vector, floor: Optional[str], kind_id: Optional[int]
- add_edge/add_panelで相互リンク構築
- __repr__はデバッグ・構造可視化用

TODO:
- ノードの責務から逸脱する箇所の整理（例：add_edge/add_panelの設計見直し）
- ノードオブジェクトにグラフの更新責務を持たせるべきか再考
- ノード属性やAPIのうち「構造本質に関係ないもの」は外部管理に切り出す可能性
- 型ヒントのさらなる厳格化、pydantic/dataclass化も検討余地
"""

from typing import List, Optional, TYPE_CHECKING
from mathutils import Vector

if TYPE_CHECKING:
    from cores.edgeCore import Edge
    from cores.panelCore import Panel


class Node:
    """
    役割:
        構造グラフ上のノード（接点）コアクラス。
        ノードID・座標・階層・種別・関連エッジ/パネルを保持し、
        グラフ基盤として機能する。
    """

    def __init__(
        self,
        id: int,
        pos: Vector,
        floor: Optional[str] = None,
        kind_id: Optional[int] = None,
    ) -> None:
        """
        役割:
            ノードを初期化し、各属性をセット。
        引数:
            id (int): ノードID
            pos (Vector): 座標
            floor (Optional[str]): 階層属性
            kind_id (Optional[int]): ノード種別
        返り値:
            なし
        """
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
            ノードの主要属性・接続数を可読文字列で返す。
        返り値:
            str
        """
        return (
            f"Node(id={self.id}, pos={tuple(self.pos)}, floor={self.floor}, "
            f"edges={len(self.edges)}, panels={len(self.panels)})"
        )
