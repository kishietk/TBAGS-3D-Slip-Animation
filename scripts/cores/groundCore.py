"""
cores/groundCore.py

責務:
- グラウンド（地面）モデル情報の保持のみ
- Blenderオブジェクト参照・サイズ・位置など最低限だけ

使い方:
    from cores.groundCore import Ground
    ground_core = Ground()
    ground_core.set_blender_object(ground_obj)
"""

from typing import Optional, Dict, Any
from mathutils import Vector
from configs import GROUND_SIZE_X, GROUND_SIZE_Y, GROUND_LOCATION


class Ground:
    """
    地面コアモデルクラス
    """

    def __init__(
        self,
        size_x: float = GROUND_SIZE_X,
        size_y: float = GROUND_SIZE_Y,
        position: Optional[Vector] = None,
    ):
        self.size_x = size_x
        self.size_y = size_y
        self.position = position if position is not None else Vector(GROUND_LOCATION)
        self.blender_object = None
        self.attributes: Dict[str, Any] = {}

    def set_blender_object(self, obj):
        self.blender_object = obj

    def __repr__(self):
        return f"Ground(size_x={self.size_x}, size_y={self.size_y}, position={tuple(self.position)}, blender_object={self.blender_object})"
