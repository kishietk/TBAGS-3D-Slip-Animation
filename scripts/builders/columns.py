"""
ファイル名: builders/columns.py

責務:
- ノード座標とエッジ情報からBlender上に柱（Cylinderオブジェクト）を一括生成するビルダー。
- 中心・回転・長さは自動計算（親子/アニメ機能は持たない）。

TODO:
- build_beamsとの共通化・ベースクラス化（重複ロジック統合）
- ノード座標受け渡しの型整理（dataclass化・type alias導入も視野）
- エラー時のロギングや復帰処理の粒度見直し
"""

import bpy
from mathutils import Vector
from utils.logging_utils import setup_logging

log = setup_logging("build_columns")


def build_columns(
    nodes: dict[int, Vector],
    edges: set[tuple[int, int]],
    thickness: float,
) -> list[tuple[bpy.types.Object, int, int]]:
    """
    役割:
        ノード座標とエッジ情報から柱（Cylinderオブジェクト）を生成する。

    引数:
        nodes (dict[int, Vector]): ノードID→座標Vectorの辞書
        edges (set[tuple[int, int]]): 柱となるノードIDペア集合
        thickness (float): 柱シリンダーの半径

    返り値:
        list[tuple[bpy.types.Object, int, int]]: (柱Object, ノードA ID, ノードB ID)タプルリスト

    補足:
        - 中心座標・回転は自動計算（Blender側でスケール補正）
        - build_beamsと同一シグネチャ
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
            obj.name = f"Column_{a}_{b}"

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

            log.debug(
                f"Column_{a}_{b}: from {tuple(p1)} to {tuple(p2)}, length={length}"
            )

            objs.append((obj, a, b))
        except Exception as e:
            log.error(f"Failed to create column between {a} and {b}: {e}")
    return objs
