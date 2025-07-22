### cores/entities/edge_core.py
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cores import Node, Panel

class Edge:
    """
    2点間部材の基底クラス。
    """
    def __init__(
        self,
        start: "Node",
        end: "Node",
        kind: Optional[int] = None,
        kind_label: Optional[str] = None,
        attributes: Optional[dict] = None,
    ) -> None:
        self.id = tuple(sorted([start.id, end.id]))
        self.node_a = start
        self.node_b = end
        self.kind_id = kind
        self.kind_label = kind_label
        self.attributes = attributes or {}
        self.panels: List["Panel"] = []