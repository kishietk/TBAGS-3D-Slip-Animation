from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.node import Node
    from cores.panel import Panel

"""
edge.py

【役割 / Purpose】
- 構造グラフの「エッジ（部材：柱・梁など）」情報を表現するコアクラス。
- 両端ノード・種別ID・ラベル・所属パネルリスト等を管理。
- 生成時に両端ノードへ自分自身を自動登録（双方向参照）。

【設計方針】
- kind_id/kind_labelはself.strの #番号・ラベルをそのまま保持。
- add_panel()で自身が所属するPanelも記録。
- 反対側ノード取得APIも用意。
"""


class Edge:
    """
    エッジ（部材：梁・柱等）のコアクラス
    """

    def __init__(
        self,
        node_a: "Node",
        node_b: "Node",
        kind_id: Optional[int] = None,
        kind_label: Optional[str] = None,
    ):
        self.id = tuple(sorted([node_a.id, node_b.id]))  # (小さい方, 大きい方)で一意化
        self.node_a = node_a  # 一端ノード
        self.node_b = node_b  # 他端ノード
        self.kind_id = kind_id  # 部材種別ID（#42など）
        self.kind_label = kind_label  # 種別ラベル
        self.panels: List["Panel"] = []  # このエッジが含まれるPanelリスト

        # 両端ノードへこのエッジを登録（双方向リンク）
        self.node_a.add_edge(self)
        self.node_b.add_edge(self)

    def __repr__(self):
        return (
            f"Edge(id={self.id}, kind_id={self.kind_id}, kind_label={self.kind_label}, "
            f"nodes=({self.node_a.id}, {self.node_b.id}), panels={len(self.panels)})"
        )

    def add_panel(self, panel: "Panel"):
        """
        このエッジが所属するパネルを追加（重複防止）
        """
        if panel not in self.panels:
            self.panels.append(panel)

    def get_other_node(self, node: "Node") -> "Node":
        """
        このエッジの一方のノードを渡すと、もう一方のノードを返す
        """
        if node == self.node_a:
            return self.node_b
        elif node == self.node_b:
            return self.node_a
        else:
            raise ValueError("Edge does not connect to given node")
