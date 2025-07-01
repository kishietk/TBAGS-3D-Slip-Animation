import bpy
from mathutils import Vector
from typing import Any, Tuple
from utils import setup_logging

log = setup_logging("SandbagBuilder")


def create_cube(
    unit_id: Any,
    location: Vector,
    cube_size: Tuple[float, float, float] = (1.0, 1.0, 1.0),
) -> bpy.types.Object:
    """
    フォールバック: キューブプリミティブを生成し返却。
    """
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    cube = bpy.context.object
    cube.name = f"SandbagUnit_{unit_id}"
    sx, sy, sz = cube_size
    cube.scale = (sx / 2, sy / 2, sz / 2)
    log.debug(f"フォールバックキューブ {cube.name} を生成: size={cube_size}")
    return cube
