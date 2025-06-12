"""
animators/handler.py

責務:
- Blenderフレーム変更イベント（frame_change_pre/post）で
    「建物」「地面」アニメーションを同時に呼び出す統合ハンドラを管理
- 各種animatorモジュールのon_frame関数をまとめて制御

設計指針:
- 単一のframe_change_preイベントで、建物・地面アニメを一括更新
- ハンドラ競合や複数登録の問題を回避
- 登録解除・再登録もサポート

利用前提:
- main.pyなどから引数で全てのオブジェクト/アニメーション辞書を渡す
"""

import bpy
from typing import List, Tuple, Dict, Optional
from mathutils import Vector

from animators.building_animator import on_frame_building
from animators.ground_animator import on_frame_ground
from utils.logging_utils import setup_logging

log = setup_logging("anim_handler")


def register_animation_handler(
    panel_objs: List[bpy.types.Object],
    roof_obj: Optional[bpy.types.Object],
    roof_quads: List[Tuple[int, int, int, int]],
    member_objs: List[Tuple[bpy.types.Object, int, int]],
    node_objs: Dict[int, bpy.types.Object],
    sandbag_objs: Dict[int, bpy.types.Object],
    anim_data: Dict[int, Dict[int, Vector]],
    sandbag_anim_data: Dict[int, Dict[int, Vector]],
    base_node_pos: Dict[int, Vector],
    base_sandbag_pos: Dict[int, Vector],
    ground_obj: Optional[bpy.types.Object] = None,
    earthquake_anim_data: Optional[Dict[int, Vector]] = None,
) -> None:
    """
    Blenderのフレームチェンジイベントで、建物＆地面アニメーションを一括更新するハンドラを登録

    Args:
        panel_objs, roof_obj, roof_quads, member_objs, node_objs, sandbag_objs,
        anim_data, sandbag_anim_data, base_node_pos, base_sandbag_pos:
            建物アニメーション用すべての引数（building_animatorのon_frame_building参照）
        ground_obj, earthquake_anim_data:
            地面アニメーション用（ground_animatorのon_frame_ground参照）

    Returns:
        None

    Note:
        - 既存のframe_change_preハンドラを一旦クリアしてから登録
        - ground_obj, earthquake_anim_dataはNoneでも安全に動作
    """

    def _on_frame(scene: bpy.types.Scene):
        try:
            # 建物側の更新
            on_frame_building(
                scene,
                panel_objs,
                roof_obj,
                roof_quads,
                member_objs,
                node_objs,
                sandbag_objs,
                anim_data,
                sandbag_anim_data,
                base_node_pos,
                base_sandbag_pos,
            )
            # 地面側の更新
            on_frame_ground(scene, ground_obj, earthquake_anim_data)
        except Exception as e:
            log.error(f"Error in animation handler: {e}")

    # ハンドラ競合を防ぐためクリアしてから追加
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(_on_frame)
    log.info("Unified animation handler registered (building & ground).")


def unregister_animation_handler() -> None:
    """
    すべてのアニメーションハンドラ（frame_change_pre）を解除する

    Args:
        None
    Returns:
        None

    Note:
        - 必要に応じて明示的なハンドラ解除で呼ぶ
    """
    bpy.app.handlers.frame_change_pre.clear()
    log.info("All animation handlers unregistered.")
