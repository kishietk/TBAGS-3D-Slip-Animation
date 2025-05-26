# エッジ（部材：梁・柱等）クラス
# 2つのノード間の部材の基底クラス。種別ID・種別ラベル・関連パネルを保持する

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.node import Node
    from cores.panel import Panel


class Edge:
    """
    エッジ（部材：梁・柱等）の基底クラス
    ノードA・ノードB・種別ID・種別ラベル・関連パネルを保持する
    """

    def __init__(
        self,
        node_a: "Node",
        node_b: "Node",
        kind_id: Optional[int] = None,
        kind_label: Optional[str] = None,
    ):
        """
        エッジを初期化する
        引数:
            node_a: 接続ノードA（Node型）
            node_b: 接続ノードB（Node型）
            kind_id: 部材種別ID（任意、整数）
            kind_label: 部材種別ラベル（任意、文字列）
        戻り値:
            なし
        """
        self.id = tuple(sorted([node_a.id, node_b.id]))
        self.node_a = node_a
        self.node_b = node_b
        self.kind_id = kind_id
        self.kind_label = kind_label
        self.panels: List["Panel"] = []
        self.node_a.add_edge(self)
        self.node_b.add_edge(self)

    def add_panel(self, panel: "Panel") -> None:
        """
        関連するパネルをエッジのリストに追加する
        引数:
            panel: パネルインスタンス
        戻り値:
            なし
        """
        if panel not in self.panels:
            self.panels.append(panel)

    def get_other_node(self, node: "Node") -> "Node":
        """
        指定したノードと反対側のノードを返す
        引数:
            node: 片側ノード（Node型）
        戻り値:
            もう一方のノード（Node型）
        例外:
            指定ノードがこのエッジに含まれない場合はValueError
        """
        if node == self.node_a:
            return self.node_b
        elif node == self.node_b:
            return self.node_a
        else:
            raise ValueError("Edge does not connect to given node")

    def __repr__(self) -> str:
        """
        エッジの情報を文字列として返す
        引数:
            なし
        戻り値:
            エッジ情報の文字列
        """
        return (
            f"{self.__class__.__name__}(id={self.id}, kind_id={self.kind_id}, kind_label={self.kind_label}, "
            f"nodes=({self.node_a.id}, {self.node_b.id}), panels={len(self.panels)})"
        )
