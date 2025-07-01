# utils/geometry.py
from mathutils import Vector
from typing import Optional, Any


def to_vector(obj: Any) -> Optional[Vector]:
    """
    obj から .pos または .location を取り出し、Vector 型に変換して返す。
    どちらもなければ None を返す。
    """
    pos = getattr(obj, "pos", None) or getattr(obj, "location", None)
    if pos is None:
        return None
    if isinstance(pos, Vector):
        return pos
    try:
        return Vector(pos)
    except Exception:
        return None
