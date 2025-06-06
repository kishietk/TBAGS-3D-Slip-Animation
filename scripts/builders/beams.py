"""
梁（Beam）生成ビルダー（builders/beams.py）

- ノード座標とエッジ情報からBlender上に梁（Cylinder）を一括生成
- 柱ビルダーと構造同一・回転自動計算
"""

import bpy
from mathutils import Vector
from utils.logging_utils import setup_logging

log = setup_logging()


def build_beams(
    nodes: dict[int, Vector],
    edges: set[tuple[int, int]],
    thickness: float,
) -> list[tuple[bpy.types.Object, int, int]]:
    """
    ノード座標とエッジ情報から梁（Cylinderオブジェクト）を生成する

    Args:
        nodes (dict[int, Vector]): ノードID→座標Vectorの辞書
        edges (set[tuple[int, int]]): 梁となるノードIDペア集合
        thickness (float): 梁シリンダーの半径

    Returns:
        list[tuple[bpy.types.Object, int, int]]: (梁Object, ノードA ID, ノードB ID)タプルリスト

    Note:
        - 柱ビルダー（build_columns）とシグネチャ共通化
    """
    objs = []
    up = Vector((0, 0, 1))
    for a, b in edges:
        try:
            p1, p2 = nodes[a], nodes[b]
            vec = p2 - p1
            mid = (p1 + p2) / 2
            length = vec.length

            bpy.ops.mesh.primitive_cylinder_add(
                vertices=16, radius=thickness, depth=1, location=mid
            )
            obj = bpy.context.object
            obj.name = f"Beam_{a}_{b}"

            axis = up.cross(vec)
            if axis.length > 1e-6:
                axis.normalize()
                angle = up.angle(vec)
                obj.rotation_mode = "AXIS_ANGLE"
                obj.rotation_axis_angle = (angle, axis.x, axis.y, axis.z)
            else:
                obj.rotation_mode = "QUATERNION"
                obj.rotation_quaternion = [1, 0, 0, 0]
            obj.scale = (thickness, thickness, length)

            log.debug(f"Beam_{a}_{b}: from {tuple(p1)} to {tuple(p2)}, length={length}")

            objs.append((obj, a, b))
        except Exception as e:
            log.error(f"Failed to create beam between {a} and {b}: {e}")
    return objs
