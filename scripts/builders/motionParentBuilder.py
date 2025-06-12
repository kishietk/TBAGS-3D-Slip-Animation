"""
builders/motionParentBuilder.py

責務:
- 地震アニメーション用の親(Empty)オブジェクトを生成
- 複数の建物部材群を一括で親子付けする

利用例:
    from builders.motionParentBuilder import build_motion_parent, set_parent

    motion_parent = build_motion_parent()
    set_parent(
        motion_parent,
        node_objs=node_objs,
        sandbag_objs=sandbag_objs,
        panel_objs=panel_objs,
        roof_obj=roof_obj,
        member_objs=member_objs,
        # ground_objは親子付けしない
    )
"""

import bpy
from configs import GROUND_LOCATION


def build_motion_parent(
    location: tuple = GROUND_LOCATION, name: str = "EarthquakeMotionParent"
) -> bpy.types.Object:
    """
    地震アニメーション用の親(Empty)オブジェクトを生成

    Args:
        location (tuple): (x, y, z)ワールド座標
        name (str): オブジェクト名

    Returns:
        bpy.types.Object: 作成したEmpty親オブジェクト
    """
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=location)
    obj = bpy.context.object
    obj.name = name
    obj.hide_viewport = True
    obj.hide_render = True
    return obj


def set_parent(
    parent_obj,
    node_objs: dict = None,
    sandbag_objs: dict = None,
    panel_objs: list = None,
    roof_obj=None,
    member_objs: list = None,
):
    """
    複数の建物部材を親オブジェクトに一括で親子付けする

    Args:
        parent_obj: Blenderの親オブジェクト（Empty等）
        node_objs (dict): ノード球 {id: Object}
        sandbag_objs (dict): サンドバッグ {id: Object}
        panel_objs (list): パネルオブジェクト
        roof_obj (Object or None): 屋根オブジェクト
        member_objs (list or None): 柱・梁オブジェクト [(Object, a, b), ...]

    Returns:
        None
    """
    # ノード球
    if node_objs:
        for obj in node_objs.values():
            if obj:
                obj.parent = parent_obj
    # サンドバッグ
    if sandbag_objs:
        for obj in sandbag_objs.values():
            if obj:
                obj.parent = parent_obj
    # パネル
    if panel_objs:
        for obj in panel_objs:
            if obj:
                obj.parent = parent_obj
    # 屋根
    if roof_obj:
        roof_obj.parent = parent_obj
    # 柱・梁
    if member_objs:
        for m in member_objs:
            obj = m[0] if isinstance(m, (list, tuple)) and m else m
            if obj:
                obj.parent = parent_obj
