# パネル（Panel）クラス
# 4つのノードで構成される面（壁や屋根）を表現する

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.node import Node
    from cores.edge import Edge


class Panel:
    """
    パネル（壁・屋根等の面）のコアクラス
    4ノード・エッジリスト・種別・階層・属性を管理する
    """

    def __init__(
        self,
        nodes: List["Node"],
        edges: Optional[List["Edge"]] = None,
        kind: str = "wall",
        floor: Optional[str] = None,
        attributes: Optional[dict] = None,
    ):
        """
        Panelインスタンスを初期化する
        引数:
            nodes: 構成ノードリスト（4個、Node型）
            edges: 構成エッジリスト（任意、Edge型）
            kind: 種別ラベル（例: "wall", "roof" など）
            floor: 階層属性（任意、str型）
            attributes: 任意の属性辞書
        戻り値:
            なし
        """
        self.id = "_".join(str(n.id) for n in sorted(nodes, key=lambda n: n.id))
        self.nodes = nodes
        self.edges = edges if edges is not None else []
        self.kind = kind
        self.floor = floor
        self.attributes = attributes if attributes is not None else {}

        # ノードとエッジにこのパネルを双方向登録する
        for n in self.nodes:
            n.add_panel(self)
        for e in self.edges:
            e.add_panel(self)

    def __repr__(self) -> str:
        """
        パネルの情報を文字列として返す
        引数:
            なし
        戻り値:
            パネル情報の文字列
        """
        return (
            f"Panel(id={self.id}, kind={self.kind}, floor={self.floor}, "
            f"nodes={[n.id for n in self.nodes]}, edges={len(self.edges)})"
        )
