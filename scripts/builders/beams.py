"""
ファイル名: builders/beams.py

責務:
- ノード座標とエッジ情報からBlender上に梁（Cylinderオブジェクト）を一括生成するビルダー。
- 柱ビルダーと同一構造で、回転も自動計算。

TODO:
- build_columnsとの共通化・ベースクラス化（共通ロジック吸収）
- エラー時のロギング粒度見直し・復帰処理
- ノード座標受け渡しの型整理（dataclass化等も視野）
"""

import bpy
from mathutils import Vector
from utils.logging_utils import setup_logging

log = setup_logging("build_beams")


def build_beams(
    nodes: dict[int, Vector],
    edges: set[tuple[int, int]],
    thickness: float,
) -> list[tuple[bpy.types.Object, int, int]]:
    """
    役割:
        ノード座標とエッジ情報から梁（Cylinderオブジェクト）を生成する。

    引数:
        nodes (dict[int, Vector]): ノードID→座標Vectorの辞書
        edges (set[tuple[int, int]]): 梁となるノードIDペア集合
        thickness (float): 梁シリンダーの半径

    返り値:
        list[tuple[bpy.types.Object, int, int]]: (梁Object, ノードA ID, ノードB ID)タプルリスト

    補足:
        - build_columns（柱ビルダー）とシグネチャ・設計思想を揃えてある
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
    log.info(f"{len(objs)}件のBlender梁オブジェクトを生成しました。")
    return objs
