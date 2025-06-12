"""
animators/ground_animator.py

責務:
- 地震アニメーション用の親オブジェクト（motion parent）のみを動かすハンドラ
- グラウンドメッシュ（ground_obj）も独立して動かすハンドラ
- どちらもBlenderのフレームチェンジイベントでlocationを毎フレーム更新

利用例:
    from animators.ground_animator import (
        register_ground_anim_handler,
        register_ground_mesh_anim_handler,
    )

    register_ground_anim_handler(
        motion_parent=motion_parent,
        earthquake_anim_data=earthquake_anim_data,
    )
    register_ground_mesh_anim_handler(
        ground_obj=ground_obj,
        ground_anim_data=ground_anim_data,
    )
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


def register_ground_mesh_anim_handler(
    ground_obj: bpy.types.Object,
    ground_anim_data: Optional[Dict[int, Vector]] = None,
) -> None:
    """
    ground_obj(地面メッシュ)の.locationを毎フレームアニメーションで更新

    Args:
        ground_obj: アニメーション対象の地面Blenderオブジェクト
        ground_anim_data: {frame: Vector(dx, dy, dz)}
    """

    def _on_frame(scene):
        disp = Vector((0, 0, 0))
        if ground_anim_data is not None:
            disp = ground_anim_data.get(scene.frame_current, Vector((0, 0, 0)))
        if ground_obj:
            ground_obj.location = disp
            log.debug(
                f"ground_obj.location set to {tuple(disp)} at frame {scene.frame_current}"
            )

    bpy.app.handlers.frame_change_pre.append(_on_frame)
    log.info("Ground mesh animation handler registered.")
