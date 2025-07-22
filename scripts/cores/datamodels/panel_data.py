# parsers/types.py

from typing import NamedTuple, Tuple, List
from mathutils import Vector


class PanelData(NamedTuple):
    """
    パネル情報の中間表現データ。
    """

    node_ids: List[int]
    kind: str = "wall"
    floor: str = ""
    attributes: dict = {}
