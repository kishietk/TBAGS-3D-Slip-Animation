# parsers/types.py

from typing import NamedTuple, Tuple, List
from mathutils import Vector


class NodeData(NamedTuple):
    """
    STRファイルからパースされたノード情報。
    """

    pos: Vector
    kind_id: int
