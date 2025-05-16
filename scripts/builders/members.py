import bpy
from mathutils import Vector, Quaternion
from logging_utils import setup_logging
from config import CYLINDER_VERTS, EPS_AXIS, MEMBER_OBJ_PREFIX

log = setup_logging()


def build_members(nodes: dict, edges: set, thickness: float):
    """
    ノード座標とエッジリストから柱・梁（円柱メッシュ）を生成する関数

    引数:
        nodes: {nid: Vector}      ノード座標辞書
        edges: set((a, b), ...)  エッジペア集合
        thickness: float         円柱（柱・梁）の半径

    戻り値:
        objs: [(Object, a, b), ...] 生成したBlenderオブジェクトと対応ノードIDのタプルリスト

    備考:
        - 各エッジごとに2ノード間を結ぶ円柱を生成
        - 向き・回転・スケール調整もここで行う
    """
    log.debug(f"Building members for {len(edges)} edges (thickness={thickness})")
    objs = []
    up = Vector((0, 0, 1))
    for a, b in edges:
        p1, p2 = nodes[a], nodes[b]
        vec = p2 - p1
        mid = (p1 + p2) / 2
        length = vec.length

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=CYLINDER_VERTS,
            radius=thickness,
            depth=1,  # 初期の高さ（スケールで伸縮させる）
            location=mid,
        )
        obj = bpy.context.object
        obj.name = f"{MEMBER_OBJ_PREFIX}{a}_{b}"

        # 柱方向に合わせて回転・スケール
        axis = up.cross(vec)
        if axis.length > EPS_AXIS:
            axis.normalize()
            angle = up.angle(vec)
            obj.rotation_mode = "AXIS_ANGLE"
            obj.rotation_axis_angle = (angle, axis.x, axis.y, axis.z)
        else:
            obj.rotation_mode = "QUATERNION"
            obj.rotation_quaternion = Quaternion((1, 0, 0, 0))
        # X/Y方向を細く、Z方向（=長さ方向）を伸ばす
        obj.scale = (thickness, thickness, length)

        objs.append((obj, a, b))

    log.debug("Member objects built.")
    return objs


# 旧API互換のためのエイリアス
create_member_objects = build_members
