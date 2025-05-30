"""
エッジ（部材：梁・柱等）基底クラス
- 2ノード間の部材コア、梁・柱等の共通基盤
- kind_id, kind_label, 関連パネルリスト保持・パネル紐付けAPI

【設計方針】
- node_a/node_b: Node型。両端で必ずadd_edgeで相互参照構築
- panels: このエッジに付随するPanel（壁/床等）リスト
- get_other_node()で反対側ノード取得API
"""

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.Node import Node
    from cores.Panel import Panel


class Edge:
    """
    エッジ（部材：梁・柱等）基底クラス
    - 2ノード間の部材（種別ID/ラベル/関連パネル保持）
    - 継承で梁(Beam)/柱(Column)など拡張
    """

    def __init__(
        self,
        node_a: "Node",
        node_b: "Node",
        kind_id: Optional[int] = None,
        kind_label: Optional[str] = None,
    ) -> None:
        """
        エッジを初期化する
        Args:
            node_a (Node): 接続ノードA
            node_b (Node): 接続ノードB
            kind_id (Optional[int]): 種別ID
            kind_label (Optional[str]): 種別ラベル
        Returns:
            None
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
        関連パネルをこのエッジのリストに追加
        Args:
            panel (Panel): 紐付けるパネル
        Returns:
            None
        """
        if panel not in self.panels:
            self.panels.append(panel)

    def get_other_node(self, node: "Node") -> "Node":
        """
        指定ノードの反対側ノードを返す
        Args:
            node (Node): 一方の端点
        Returns:
            Node: もう一方の端点
        Raises:
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
        エッジの情報を可読文字列で返す
        Returns:
            str: エッジ情報（id, kind, nodes, panels数）
        """
        return (
            f"{self.__class__.__name__}(id={self.id}, kind_id={self.kind_id}, kind_label={self.kind_label}, "
            f"nodes=({self.node_a.id}, {self.node_b.id}), panels={len(self.panels)})"
        )
