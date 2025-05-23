"""
members.py

【役割】
- ノード座標とエッジリストから柱・梁（円柱メッシュ）を生成するビルダー。
- 円柱分割数やしきい値などのパラメータは定数化、Blender名付け規則もconfig.py由来で統一。
- 例外時にはノードIDも含めて詳細ログ。

【設計方針】
- 型ヒント徹底で保守性・拡張性向上。
- 生成失敗時もID・原因を現場水準で出力。
"""

import bpy
from typing import Dict, Set, List, Tuple
from mathutils import Vector, Quaternion
from logging_utils import setup_logging

log = setup_logging()

# --- 柱・梁の円柱分割数などパラメータ（マジックナンバー排除） ---
CYLINDER_VERTS = 16


def build_members(
    nodes: dict[int, Vector], edges: set[tuple[int, int]], thickness: float
) -> list[tuple[bpy.types.Object, int, int]]:
    """
    ノード座標とエッジリストから柱・梁（円柱メッシュ）を生成する関数

    引数:
        nodes: {nid: Vector}
        edges: set((a, b), ...)
        thickness: float

    戻り値:
        objs: [(Object, a, b), ...]
    """
    log.debug(f"Building members for {len(edges)} edges (thickness={thickness})")
    objs: list[tuple[bpy.types.Object, int, int]] = []
    up = Vector((0, 0, 1))
    for a, b in edges:
        try:
            p1, p2 = nodes[a], nodes[b]
            vec = p2 - p1
            mid = (p1 + p2) / 2
            length = vec.length

            bpy.ops.mesh.primitive_cylinder_add(
                vertices=CYLINDER_VERTS, radius=thickness, depth=1, location=mid
            )
            obj = bpy.context.object
            obj.name = f"Member_{a}_{b}"

            axis = up.cross(vec)
            if axis.length > 1e-6:
                axis.normalize()
                angle = up.angle(vec)
                obj.rotation_mode = "AXIS_ANGLE"
                obj.rotation_axis_angle = (angle, axis.x, axis.y, axis.z)
            else:
                obj.rotation_mode = "QUATERNION"
                obj.rotation_quaternion = Quaternion((1, 0, 0, 0))
            obj.scale = (thickness, thickness, length)

            objs.append((obj, a, b))
        except Exception as e:
            log.error(f"Failed to create member between node {a} and {b}: {e}")

    log.debug("Member objects built.")
    return objs


# 旧 API 名が使われている場合のフォールバック
create_member_objects = build_members
