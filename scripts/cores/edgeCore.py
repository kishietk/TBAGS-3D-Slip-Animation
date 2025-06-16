"""
ファイル名: cores/edgeCore.py

責務:
- 2ノード間の部材（梁・柱等）の基底クラス（Edge）を定義する。
- kind_id, kind_label, 関連パネルリストの保持と、パネル・ノード参照APIを提供。

設計方針:
- node_a/node_b: Node型。両端点で必ずadd_edgeで相互参照構築
- panels: このエッジに付随するPanel（壁/床等）のリスト
- get_other_node()で反対側ノードを取得できる
"""

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.nodeCore import Node
    from cores.panelCore import Panel


class Edge:
    """
    役割:
        2ノード間の部材（梁・柱等）の基底クラス。
        種別ID/ラベル・関連パネルリストを保持し、パネル・ノード参照APIも提供。
        継承でBeam/Column等に拡張。
    """

    def __init__(
        self,
        node_a: "Node",
        node_b: "Node",
        kind_id: Optional[int] = None,
        kind_label: Optional[str] = None,
    ) -> None:
        """
        役割:
            エッジを初期化し、両端ノードと双方向参照を構築。
        引数:
            node_a (Node): 接続ノードA
            node_b (Node): 接続ノードB
            kind_id (Optional[int]): 種別ID
            kind_label (Optional[str]): 種別ラベル
        返り値:
            なし
        """
        self.id: tuple[int, int] = tuple(sorted([node_a.id, node_b.id]))
        self.node_a: "Node" = node_a
        self.node_b: "Node" = node_b
        self.kind_id: Optional[int] = kind_id
        self.kind_label: Optional[str] = kind_label
        self.panels: List["Panel"] = []
        self.node_a.add_edge(self)
        self.node_b.add_edge(self)

    def add_panel(self, panel: "Panel") -> None:
        """
        役割:
            関連パネルをこのエッジに追加（重複不可）。
        引数:
            panel (Panel)
        返り値:
            なし
        """
        if panel not in self.panels:
            self.panels.append(panel)

    def get_other_node(self, node: "Node") -> "Node":
        """
        役割:
            指定ノードの反対側ノードを返す。
        引数:
            node (Node)
        返り値:
            Node: もう一方の端点
        例外:
            ValueError: このエッジがnodeに接続していない場合
        """
        if node == self.node_a:
            return self.node_b
        elif node == self.node_b:
            return self.node_a
        else:
            raise ValueError("Edge does not connect to given node")

    def __repr__(self) -> str:
        """
        役割:
            エッジの情報を可読文字列で返す。
        返り値:
            str
        """
        return (
            f"{self.__class__.__name__}(id={self.id}, kind_id={self.kind_id}, kind_label={self.kind_label}, "
            f"nodes=({self.node_a.id}, {self.node_b.id}), panels={len(self.panels)})"
        )
