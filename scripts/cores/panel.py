from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.node import Node
    from cores.edge import Edge

"""
panel.py

【役割 / Purpose】
- 壁パネル・屋根パネルなど面（4ノード）のコアクラス。
- どのノード・エッジで構成されるか、種別・階層・属性などを管理。

【設計方針】
- 4ノード・エッジリストは生成時にセット・双方向参照も自動登録。
- attributes辞書で任意の付加情報も将来拡張可。
- 型ヒント・現場向けコメント徹底。
"""


class Panel:
    """
    パネル（壁・屋根等の面）コアクラス
    """

    def __init__(
        self,
        nodes: List["Node"],
        edges: Optional[List["Edge"]] = None,
        kind: str = "wall",
        floor: Optional[str] = None,
        attributes: Optional[dict] = None,
    ):
        self.id = "_".join(
            str(n.id) for n in sorted(nodes, key=lambda n: n.id)
        )  # 一意ID
        self.nodes = nodes  # 4ノード（リスト）
        self.edges = edges if edges is not None else []  # この面を構成するエッジリスト
        self.kind = kind  # 種別ラベル（wall, roofなど）
        self.floor = floor  # 階層属性
        self.attributes = attributes if attributes is not None else {}  # 任意属性辞書

        # 各ノード・エッジ側にもこのパネルを登録（双方向リンク）
        for n in self.nodes:
            n.add_panel(self)
        for e in self.edges:
            e.add_panel(self)
