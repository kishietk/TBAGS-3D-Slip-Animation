# parsers/types.py

from typing import NamedTuple, Tuple, List
from mathutils import Vector


class NodeData(NamedTuple):
    """
    STRファイルからパースされたノード情報。
    """

    pos: Vector
    kind_id: int


class EdgeData(NamedTuple):
    """
    STRファイルからパースされたエッジ情報。
    """

    node_a: int
    node_b: int
    kind_id: int
    kind_label: str

class PanelData(NamedTuple):
    """
    パネル情報の中間表現データ。
    """

    node_ids: List[int]
    kind: str = "wall"
    floor: str = ""
    attributes: dict = {}
