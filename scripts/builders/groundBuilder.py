"""
builders/groundBuilder.py

責務:
- 地面（Ground）オブジェクトの生成
- 建物関連オブジェクトを地面の子にまとめる親子付け
- 他buildersと一貫した設計・例外/ロギング・ドキュメントの充実

注意:
- 地面のアニメーションやマテリアル設定の責任は持たない
- シーン内で"EarthquakeBase"として管理
"""

import bpy
from utils.logging_utils import setup_logging

log = setup_logging("groundBuilder")


def build_ground_plane(
    size: float = 30.0, name: str = "EarthquakeBase"
) -> bpy.types.Object:
    """
    地面（平面）Blenderオブジェクトを生成して返す

    Args:
        size (float): 一辺の長さ（Blender単位）
        name (str): オブジェクト名

    Returns:
        bpy.types.Object: 作成した地面オブジェクト

    Raises:
        生成に失敗した場合は例外を発生（Noneは返さない）

    Note:
        - アニメーションやマテリアルの適用責任はこの関数は持たない
        - 呼び出し元で地面の扱い（親子付け/アニメ登録など）は実施
    """
    try:
        bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
        ground_obj = bpy.context.object
        ground_obj.name = name
        log.info(f"Ground plane '{name}' created (size={size})")
        return ground_obj
    except Exception as e:
        log.error(f"Failed to create ground plane: {e}")
        raise


def set_building_parent(
    ground_obj: bpy.types.Object,
    node_objs: dict,
    sandbag_objs: dict,
    panel_objs: list,
    roof_obj: object = None,
    member_objs: list = None,
) -> None:
    """
    主要建物オブジェクト群を地面オブジェクトの子としてまとめる

    Args:
        ground_obj (bpy.types.Object): 地面のBlenderオブジェクト
        node_objs (dict): ノード球 {id: Object}
        sandbag_objs (dict): サンドバッグ {id: Object}
        panel_objs (list): パネルオブジェクト
        roof_obj (Object or None): 屋根オブジェクト
        member_objs (list or None): 柱・梁のオブジェクト [(Object, a, b), ...]

    Returns:
        None

    Note:
        - すべての要素がNoneや空dict/listの場合も安全にスキップ
        - 呼び出し例: set_building_parent(ground_obj, node_objs, sandbag_objs, panel_objs, roof_obj, member_objs)
    """
    # ノード球
    if node_objs:
        for obj in node_objs.values():
            if obj:
                obj.parent = ground_obj
    # サンドバッグ
    if sandbag_objs:
        for obj in sandbag_objs.values():
            if obj:
                obj.parent = ground_obj
    # パネル
    if panel_objs:
        for obj in panel_objs:
            if obj:
                obj.parent = ground_obj
    # 屋根
    if roof_obj:
        roof_obj.parent = ground_obj
    # 柱・梁
    if member_objs:
        for m in member_objs:
            obj = m[0] if isinstance(m, (list, tuple)) and m else m
            if obj:
                obj.parent = ground_obj
    log.info("All building objects set as children of the ground object.")
