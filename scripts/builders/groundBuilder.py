# builders/ground.py

import bpy


def build_ground_plane(size=30.0, name="EarthquakeBase"):
    """
    指定サイズでBlender平面を生成し、EarthquakeBaseとして返す
    """
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    ground_obj = bpy.context.object
    ground_obj.name = name
    return ground_obj


def set_building_parent(
    ground_obj, node_objs, sandbag_objs, panel_objs, roof_obj, member_objs
):
    """
    主要オブジェクトをすべてground_objの子にする
    """
    # ノード球
    for obj in node_objs.values():
        obj.parent = ground_obj
    # サンドバッグ
    for obj in sandbag_objs.values():
        obj.parent = ground_obj
    # パネル
    for obj in panel_objs:
        obj.parent = ground_obj
    # 屋根
    if roof_obj:
        roof_obj.parent = ground_obj
    # 柱・梁
    for obj, *_ in member_objs:
        if obj:
            obj.parent = ground_obj
