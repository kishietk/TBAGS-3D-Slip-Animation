### cores/entities/column_core.py
from typing import Optional, TYPE_CHECKING
from .edge_core import Edge
from ..registry import register_core
from configs import COLUMNS_KIND_IDS

if TYPE_CHECKING:
    from cores import Node, Panel

@register_core(COLUMNS_KIND_IDS)
class Column(Edge):
    """
    柱部材を表すコアクラス。
    Edgeの機能を継承しつつ、is_column属性をTrueに設定。
    """

    def __init__(
        self,
        start: "Node",
        end: "Node",
        kind: Optional[int] = None,
        kind_label: Optional[str] = None,
        attributes: Optional[dict] = None,
    ) -> None:
        super().__init__(
            start=start,
            end=end,
            kind=kind,
            kind_label=kind_label,
            attributes=attributes,
        )
        self.is_column: bool = True

    def __repr__(self) -> str:
        return (
            f"Column(id={self.id}, nodes={[self.node_a.id, self.node_b.id]}, "
            f"kind_id={self.kind_id}, is_column={self.is_column})"
        )