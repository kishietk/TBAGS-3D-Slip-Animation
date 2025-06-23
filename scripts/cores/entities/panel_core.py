"""
責務:
- 4ノードで構成される面（壁・屋根等）のコアクラスPanelを定義。
- 属性（種別、階層、追加情報）を管理する。

設計方針:
- nodes: List[Node]（必ず4点）、edges: List[Edge]
- kind: str型種別("wall"/"roof"等)
- floor: 階層ラベル、attributes: 任意の追加辞書
- ノード・エッジへの双方向リンク・add_panel/add_edge責務は本クラスから完全廃止

TODO:
- Panelクラスの責務範囲見直し・属性管理強化
- 型ヒント厳格化やdataclass化の検討
"""

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.entities import Node, Edge


class Panel:
    """
    役割:
        4ノードで構成される面（壁・屋根等）のコアクラス。
        面の属性・参照情報を管理する。

    属性:
        id (str): 識別用ID
        nodes (List[Node]): 4点ノード
        edges (List[Edge]): 構成エッジ（任意）
        kind (str): パネル種別
        floor (Optional[str]): 階層
        attributes (dict): 任意追加属性
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
            Panelインスタンスを初期化し、各種属性をセット。
            ノード・エッジへの双方向登録（add_panel, add_edge）は完全廃止。

        引数:
            nodes (List[Node]): 4つのノード
            edges (Optional[List[Edge]]): 構成エッジ
            kind (str): パネル種別
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
