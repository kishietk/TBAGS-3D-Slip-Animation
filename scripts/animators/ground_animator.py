"""
animators/ground_animator.py

責務:
- 地面（Groundオブジェクト）のアニメーション制御を担当
- 「地震アニメーション」や地面変位の反映など、建物以外の地面移動に限定
- アニメーションの初期化・Blenderフレームごとの地面移動を担う

設計指針:
- 地面以外の部材アニメーション処理は一切行わない
- 地面アニメのon_frameロジックを明確に分離
- 必要に応じ他のanimators/handlerからimportして組み合わせ
"""

import bpy
from mathutils import Vector
from typing import Optional, Dict
from utils.logging_utils import setup_logging

log = setup_logging("ground_animator")


def on_frame_ground(
    scene: bpy.types.Scene,
    ground_obj: Optional[bpy.types.Object],
    earthquake_anim_data: Optional[Dict[int, Vector]] = None,
) -> None:
    """
    現在フレームにおける地面（Ground）オブジェクトの位置を更新

    Args:
        scene (bpy.types.Scene): 現在のBlenderシーン
        ground_obj (bpy.types.Object or None): 地面オブジェクト
        earthquake_anim_data (dict or None): {フレーム: Vector(dx,dy,dz)}の地震変位データ

    Returns:
        None

    Note:
        - 地震データがなければ移動は行わない
        - 他アニメータと併用時はBlenderのイベントハンドラから呼ばれることを前提とする
    """
    if ground_obj is None:
        return
    disp = Vector((0, 0, 0))
    if earthquake_anim_data is not None:
        disp = earthquake_anim_data.get(scene.frame_current, Vector((0, 0, 0)))
    ground_obj.location = disp
    log.debug(f"Ground location set to {tuple(disp)} at frame {scene.frame_current}")


def init_ground_animation_handler(
    ground_obj: Optional[bpy.types.Object],
    earthquake_anim_data: Optional[Dict[int, Vector]] = None,
) -> None:
    """
    Blenderのフレームチェンジ時に地面アニメーションのみ自動実行するイベントを登録

    Args:
        ground_obj (bpy.types.Object or None): 地面オブジェクト
        earthquake_anim_data (dict or None): {フレーム: Vector(dx,dy,dz)}の地震変位データ

    Returns:
        None

    Note:
        - 既存ハンドラとの競合に注意
        - 他部材のアニメーション登録と組み合わせて呼び出す場合は、アニメータ統合側でコントロール
    """

    def _on_frame(scene):
        try:
            on_frame_ground(
                scene, ground_obj=ground_obj, earthquake_anim_data=earthquake_anim_data
            )
        except Exception as e:
            log.error(f"Error in ground animation frame handler: {e}")

    # 既存 ground 用の frame_change_pre ハンドラを一旦クリア（もしくは個別管理）
    bpy.app.handlers.frame_change_pre = [
        h
        for h in bpy.app.handlers.frame_change_pre
        if not getattr(h, "_is_ground_anim_handler", False)
    ]
    _on_frame._is_ground_anim_handler = True
    bpy.app.handlers.frame_change_pre.append(_on_frame)
    log.info("Ground animation handler registered.")
