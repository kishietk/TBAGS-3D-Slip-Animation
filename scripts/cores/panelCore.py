"""
パネル（Panel）コアクラス
- 4ノードで構成される面（壁・屋根等）の属性・参照情報を管理
- Edge/Nodeの双方向リンクによるグラフ構造把握

【設計方針】
- nodes: List[Node]（必ず4点）、edges: List[Edge]
- kind: str型種別("wall"/"roof"等)
- floor: 階層ラベル、attributes: 任意の追加辞書
"""

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.nodeCore import Node
    from cores.edgeCore import Edge


class Panel:
    """
    パネル（壁・屋根等の面）コアクラス
    - 4ノード・エッジ・種別・階層・属性を包括
    - 構造グラフ全体で面/屋根を表現
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
        Panelインスタンス初期化
        Args:
            nodes (List[Node]): 4つのノード
            edges (Optional[List[Edge]]): 構成エッジ
            kind (str): 種別（"wall"/"roof"等）
            floor (Optional[str]): 階層
            attributes (Optional[dict]): 任意追加属性
        Returns:
            None
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
        パネル情報を可読文字列で返す
        Returns:
            str: パネル情報
        """
        return (
            f"Panel(id={self.id}, kind={self.kind}, floor={self.floor}, "
            f"nodes={[n.id for n in self.nodes]}, edges={len(self.edges)})"
        )
