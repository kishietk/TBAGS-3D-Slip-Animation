### cores/entities/panel_core.py
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cores import Node, Edge

class Panel:
    """
    4ノードで構成される面（壁・屋根等）。
    """
    def __init__(
        self,
        nodes: List["Node"],
        kind: str = "wall",
        floor: Optional[str] = None,
        attributes: Optional[dict] = None,
        edges: Optional[List["Edge"]] = None,
    ) -> None:
        sorted_ids = sorted(n.id for n in nodes)
        self.id = "_".join(str(i) for i in sorted_ids)
        self.nodes = nodes
        self.edges = edges or []
        self.kind = kind
        self.floor = floor
        self.attributes = attributes or {}