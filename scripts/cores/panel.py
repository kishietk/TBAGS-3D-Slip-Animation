from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cores.node import Node
    from cores.edge import Edge


class Panel:
    """
    パネル（壁・屋根など面）情報のコアクラス。
    """

    def __init__(
        self,
        nodes: List["Node"],
        edges: Optional[List["Edge"]] = None,
        kind: str = "wall",
        floor: Optional[str] = None,
        attributes: Optional[dict] = None,
    ):
        self.id = "_".join(str(n.id) for n in sorted(nodes, key=lambda n: n.id))
        self.nodes = nodes
        self.edges = edges if edges is not None else []
        self.kind = kind
        self.floor = floor
        self.attributes = attributes if attributes is not None else {}

        for n in self.nodes:
            n.add_panel(self)
        for e in self.edges:
            e.add_panel(self)
