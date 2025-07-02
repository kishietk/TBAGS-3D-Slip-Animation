from mathutils import Vector
import logging
from typing import Optional, Any

log = logging.getLogger(__name__)


def to_vector(obj: Any) -> Optional[Vector]:
    """
    obj が mathutils.Vector の場合はそのまま返し、
    それ以外は .pos または .location を取り出して Vector に変換して返す。
    どちらもなければ None を返し、失敗時にはエラーログを残す。
    """
    # 1) すでに Vector インスタンスならそのまま返す
    if isinstance(obj, Vector):
        return obj

    # 2) .pos/.location から取得
    pos = getattr(obj, "pos", None) or getattr(obj, "location", None)
    if pos is None:
        log.error(f"to_vector: neither .pos nor .location found on {obj!r}")
        return None

    # 3) pos が Vector の場合
    if isinstance(pos, Vector):
        return pos

    # 4) タプル／リスト等から Vector に変換
    try:
        return Vector(pos)
    except Exception as e:
        log.error(f"to_vector: cannot convert {pos!r} to Vector: {e}")
        return None
