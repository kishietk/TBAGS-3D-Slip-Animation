import bpy
from typing import List, Dict
from mathutils import Vector, Quaternion
from configs import EPS_AXIS


def update_members(
    member_objs: List[bpy.types.Object],
    node_objs: Dict[int, bpy.types.Object],
    scene: bpy.types.Scene,
) -> None:
    """
    柱・梁オブジェクトを再配置・回転・スケール更新する。
    各オブジェクトにはビルダー側で設定された
    obj["member_nodes"] = (node_id_a, node_id_b)
    のカスタムプロパティがある想定です。
    """
    frame = scene.frame_current
    up = Vector((0, 0, 1))
    for obj in member_objs:
        # カスタムプロパティからノードIDを取得
        nodes = obj.get("member_nodes")
        if not nodes or len(nodes) != 2:
            continue
        a, b = nodes
        p1 = node_objs[a].location
        p2 = node_objs[b].location
        # 中間点に移動
        obj.location = (p1 + p2) * 0.5

        # 回転更新
        vec = p2 - p1
        axis = up.cross(vec)
        if axis.length > EPS_AXIS:
            axis.normalize()
            angle = up.angle(vec)
            obj.rotation_mode = "AXIS_ANGLE"
            obj.rotation_axis_angle = (angle, axis.x, axis.y, axis.z)
        else:
            obj.rotation_mode = "QUATERNION"
            obj.rotation_quaternion = Quaternion((1, 0, 0, 0))

        # スケール更新（深さ方向のみ）
        length = vec.length
        orig = obj.get("orig_depth", length)
        sx, sy, _ = obj.scale
        obj.scale = (sx, sy, length / orig)
