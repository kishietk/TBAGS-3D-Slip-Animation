"""
ファイル名: cores/panelCore.py

責務:
- 4ノードで構成される面（壁・屋根等）のコアクラスPanelを定義。
- 属性（種別、階層、追加情報）および、Edge/Nodeとの相互参照によるグラフ把握を担う。

設計方針:
- nodes: List[Node]（必ず4点）、edges: List[Edge]
- kind: str型種別("wall"/"roof"等)
- floor: 階層ラベル、attributes: 任意の追加辞書

TODO:
- Panelクラスの責務・参照範囲の見直し（ノード/エッジへの双方向リンク追加はPanelで持つべきか再検討）
- パネル属性や識別IDの設計方針整理
- 型ヒント厳格化やdataclass化の検討
"""

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.nodeCore import Node
    from cores.edgeCore import Edge


class Panel:
    """
    役割:
        4ノードで構成される面（壁・屋根等）のコアクラス。
        面の属性・参照情報を管理し、Edge/Nodeへの双方向リンクも構築する。
    """

    def __init__(
        self,
        nodes: List["Node"],
        edges: Optional[List["Edge"]] = None,
        kind: str = "wall",
        floor: Optional[str] = None,
        attributes: Optional[dict] = None,
    ) -> None:
        """
        役割:
            Panelインスタンスを初期化し、各種属性・ノード/エッジへの参照も構築。
        引数:
            nodes (List[Node]): 4つのノード
            edges (Optional[List[Edge]]): 構成エッジ
            kind (str): パネル種別（"wall"/"roof"等）
            floor (Optional[str]): 階層
            attributes (Optional[dict]): 任意追加属性
        返り値:
            なし
        """
        self.id: str = "_".join(str(n.id) for n in sorted(nodes, key=lambda n: n.id))
        self.nodes: List["Node"] = nodes
        self.edges: List["Edge"] = edges if edges is not None else []
        self.kind: str = kind
        self.floor: Optional[str] = floor
        self.attributes: dict = attributes if attributes is not None else {}

        # ノード・エッジにこのパネルを相互登録
        for n in self.nodes:
            n.add_panel(self)
        for e in self.edges:
            e.add_panel(self)

    def __repr__(self) -> str:
        """
        役割:
            パネル情報を可読文字列で返す。
        返り値:
            str
        """
        return (
            f"Panel(id={self.id}, kind={self.kind}, floor={self.floor}, "
            f"nodes={[n.id for n in self.nodes]}, edges={len(self.edges)})"
        )
