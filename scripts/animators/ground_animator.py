"""
animators/ground_animator.py

責務:
- 地震アニメーション用の親オブジェクト（motion parent）のみを動かすハンドラ
- グラウンドメッシュ（ground_obj）も独立して動かすハンドラ
- どちらもBlenderのフレームチェンジイベントでlocationを毎フレーム更新
"""

import bpy
from mathutils import Vector
from typing import Optional, Dict
from utils.logging_utils import setup_logging

log = setup_logging("ground_animator")


def register_ground_anim_handler(
    motion_parent: bpy.types.Object,
    earthquake_anim_data: Optional[Dict[int, Vector]] = None,
) -> None:
    """
    motion_parent(Empty)の.locationを毎フレームアニメーションで更新

    Args:
        motion_parent: アニメーション対象のEmpty（建物群の親）
        earthquake_anim_data: {frame: Vector(dx, dy, dz)}
    """

    def _on_frame(scene):
        disp = Vector((0, 0, 0))
        if earthquake_anim_data is not None:
            disp = earthquake_anim_data.get(scene.frame_current, Vector((0, 0, 0)))
        if motion_parent:
            motion_parent.location = disp
            log.debug(
                f"motion_parent.location set to {tuple(disp)} at frame {scene.frame_current}"
            )

    # 前回登録を防ぐためハンドラをappendのみ（運用に応じてclear対応も検討可）
    bpy.app.handlers.frame_change_pre.append(_on_frame)
    log.info("Motion parent (building) animation handler registered.")