"""
ファイル名: animators/ground_animator.py

責務:
- 地震アニメーション用の親オブジェクト（motion parent）のみを動かすハンドラを提供する。
- earthquake_anim_data(フレーム毎変位)を元にmotion_parentの.locationを毎フレーム更新。
- ground_obj等の独立アニメ処理も将来分離責任。

注意点:
- Blenderイベント登録はframe_change_preのみ（clear/重複管理は運用責任）
- ground_obj用ハンドラ分離など設計拡張余地あり

TODO:
- ground_obj独立アニメハンドラの導入
- イベント登録解除/重複防止/多重登録管理
"""

import bpy
from mathutils import Vector
from typing import Optional, Dict
from utils import setup_logging

log = setup_logging("ground_animator")


def register_ground_anim_handler(
    motion_parent: bpy.types.Object,
    earthquake_anim_data: Optional[Dict[int, Vector]] = None,
) -> None:
    """
    役割:
        motion_parent(Empty)の.locationを地震アニメーションデータで毎フレーム更新するハンドラを登録。

    引数:
        motion_parent: アニメーション対象のEmpty（建物群の親）
        earthquake_anim_data: {frame: Vector(dx, dy, dz)}（なければ静止）

    返り値:
        None

    注意:
        - ハンドラはappendのみ。多重登録/解除は呼び出し元で管理推奨。
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

    bpy.app.handlers.frame_change_pre.append(_on_frame)
