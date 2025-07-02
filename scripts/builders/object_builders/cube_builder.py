import bpy
from mathutils import Vector
from typing import Any, Tuple
from utils import setup_logging
from configs import SANDBAG_OBJ_PREFIX, CUBE_DEFAULT_SIZE

log = setup_logging("create_cube")


def create_cube(
    unit_id: Any,
    location: Vector,
    cube_size: Tuple[float, float, float] = CUBE_DEFAULT_SIZE,
) -> bpy.types.Object:
    """
    フォールバック: キューブプリミティブを生成し返却。
    """
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    cube = bpy.context.object
    cube.name = f"{SANDBAG_OBJ_PREFIX}{unit_id}"
    sx, sy, sz = cube_size
    cube.scale = (sx / 2, sy / 2, sz / 2)
    log.debug(f"フォールバックキューブ {cube.name} を生成: size={cube_size}")
    return cube
