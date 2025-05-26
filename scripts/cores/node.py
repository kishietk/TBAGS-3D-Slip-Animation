# ノード（接点）クラス
# ノードID、座標、階層、関連エッジ・パネルを保持する

from typing import List, Optional, TYPE_CHECKING
from mathutils import Vector

if TYPE_CHECKING:
    from cores.edge import Edge
    from cores.panel import Panel


class Node:
    """
    構造グラフのノードを表現するクラス
    ノードID、座標、階層属性、関連エッジ・パネルのリストを保持する
    """

    def __init__(self, id: int, pos: Vector, floor: Optional[str] = None):
        """
        ノードを初期化する
        引数:
            id: ノードID（整数）
            pos: ノード座標（Vector型）
            floor: 階層属性（任意、str型）
        """
        self.id = id
        self.pos = pos
        self.floor = floor
        self.edges: List["Edge"] = []
        self.panels: List["Panel"] = []

    def add_edge(self, edge: "Edge") -> None:
        """
        エッジをこのノードの関連エッジリストに追加する
        引数:
            edge: エッジインスタンス
        戻り値:
            なし
        """
        if edge not in self.edges:
            self.edges.append(edge)

    def add_panel(self, panel: "Panel") -> None:
        """
        パネルをこのノードの関連パネルリストに追加する
        引数:
            panel: パネルインスタンス
        戻り値:
            なし
        """
        if panel not in self.panels:
            self.panels.append(panel)

    def __repr__(self) -> str:
        """
        ノードの情報を文字列として返す
        引数:
            なし
        戻り値:
            ノード情報の文字列
        """
        return (
            f"Node(id={self.id}, pos={tuple(self.pos)}, floor={self.floor}, "
            f"edges={len(self.edges)}, panels={len(self.panels)})"
        )
