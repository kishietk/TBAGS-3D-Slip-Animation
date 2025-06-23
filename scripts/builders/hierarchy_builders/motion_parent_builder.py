"""
ファイル名: builders/motionParentBuilder.py

責務:
- 地震アニメーション用の親(Empty)オブジェクト生成と、建物部材群の一括親子付けのみを担う。

注意点:
- ground_obj（地面）はデフォルトで親子付けしない（必要な場合のみ）。
- 部材グループ単位の親子構造分割など設計の余地あり。

TODO:
- ground_objの扱い統一、親階層分割管理、親子解除APIの検討
"""

import bpy
from configs import GROUND_LOCATION
from utils.logging_utils import setup_logging

log = setup_logging("motion_parent_builder")


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
    try:
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=location)
        obj = bpy.context.object
        obj.name = name
        obj.hide_viewport = True
        obj.hide_render = True
        log.info("地震モーション用オブジェクト生成しました。")
        return obj
    except Exception as e:
        log.error(f"Emptyオブジェクト「{name}」の生成に失敗しました: {e}")
        raise


def set_parent(
    parent_obj,
    node_objs: dict = None,
    sandbag_objs: dict = None,
    panel_objs: list = None,
    roof_obj=None,
    member_objs: list = None,
    ground_obj=None,
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
        ground_obj (Object or None): 地面オブジェクト（任意）

    Returns:
        None
    """
    # カテゴリ別件数
    counts = {
        "ノード": 0,
        "サンドバッグ": 0,
        "パネル": 0,
        "屋根": 0,
        "部材": 0,
        "地面": 0,
    }

    # 内部関数: 個々のオブジェクトに対して親オブジェクトを設定
    def _assign_parent(obj, label=""):
        if obj:
            obj.parent = parent_obj
            log.debug(
                f"{label}オブジェクト「{obj.name}」を「{parent_obj.name}」に親子付けしました。"
            )
            counts[label] += 1

    # ノード球
    if node_objs:
        for obj in node_objs.values():
            _assign_parent(obj, "ノード")

    # サンドバッグ
    if sandbag_objs:
        for obj in sandbag_objs.values():
            _assign_parent(obj, "サンドバッグ")

    # パネル
    if panel_objs:
        for obj in panel_objs:
            _assign_parent(obj, "パネル")

    # 屋根
    if roof_obj:
        _assign_parent(roof_obj, "屋根")

    # 柱・梁
    if member_objs:
        for m in member_objs:
            obj = m[0] if isinstance(m, (list, tuple)) and m else m
            _assign_parent(obj, "部材")

    # グラウンド
    if ground_obj:
        _assign_parent(ground_obj, "地面")

    # ログ出力
    summary = "、".join([f"{label}:{n}" for label, n in counts.items() if n > 0])
    log.info(f"親子関係を設定：[{summary}]")
