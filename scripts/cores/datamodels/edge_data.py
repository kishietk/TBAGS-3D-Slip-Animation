from typing import NamedTuple, Tuple, List
from mathutils import Vector


class EdgeData(NamedTuple):
    """
    STRファイルからパースされたエッジ情報。
    """

    start_node_id: int
    end_node_id: int
    kind_id: int
    kind_label: str
