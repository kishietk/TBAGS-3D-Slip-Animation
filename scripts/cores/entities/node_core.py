from typing import Optional, Iterable, Type, Dict, Any
from mathutils import Vector
from cores.registry import register_core

# ノード用 kind_id のリスト
NODE_KIND_IDS = [0, 1]


@register_core(NODE_KIND_IDS)
class Node:
    """
    構造グラフ上のノードコアデータクラス。
    属性:
        id (int): ノードID
        pos (Vector): 座標
        kind_id (Optional[int]): 種別ID
        attributes (dict): 任意属性
        floor (Optional[str]): 階層ラベル
    """

    def __init__(
        self,
        id: int,
        x: float,
        y: float,
        z: float,
        kind: Optional[int] = None,
        attributes: Optional[Dict[str, Any]] = None,
        floor: Optional[str] = None,
    ) -> None:
        self.id: int = id
        self.pos: Vector = Vector((x, y, z))
        self.kind_id: Optional[int] = kind
        self.attributes: Dict[str, Any] = attributes or {}
        self.floor: Optional[str] = floor

    def __repr__(self) -> str:
        return (
            f"Node(id={self.id}, pos={tuple(self.pos)}, "
            f"kind_id={self.kind_id}, floor={self.floor})"
        )
