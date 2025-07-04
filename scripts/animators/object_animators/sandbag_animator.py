import bpy
from typing import Dict, Any
from mathutils import Vector
from utils import setup_logging
from utils.bone_name_resolver import get_rep_and_other_bones

log = setup_logging("sandbag_animator")


def update_sandbag(
    sandbag: Dict[str, bpy.types.Object],
    sandbag_anim_data: Dict[int, Dict[int, Vector]],
    base_sandbag_pos: Dict[Any, Vector],
    scene: bpy.types.Scene,
) -> None:
    """
    単一のサンドバッグユニットについて、PoseBone の location を更新し、キーフレームを設定する。

    sandbag: {'empty': Emptyオブジェクト, 'armature': Armatureオブジェクト}
    sandbag_anim_data: ノードIDごとのフレーム移動ベクトルマップ
    base_sandbag_pos: ノードIDごとの基準位置マップ
    scene: bpy.types.Scene（フレーム情報取得用）
    """
    empty = sandbag.get("empty")
    armature = sandbag.get("armature")
    if not (empty and armature):
        log.error(f"[SandbagAnimator] 不足オブジェクト: {empty}, {armature}")
        return

    top_id = empty.get("top_node_id")
    bottom_id = empty.get("bottom_node_id")
    if top_id is None or bottom_id is None:
        log.error(f"[Sandbag {armature.name}] Node ID未設定")
        return

    # ワールド上の目標位置を計算
    frame = scene.frame_current
    base_top = base_sandbag_pos.get(top_id, Vector())
    base_bot = base_sandbag_pos.get(bottom_id, Vector())
    disp_top = sandbag_anim_data.get(top_id, {}).get(frame, Vector())
    disp_bot = sandbag_anim_data.get(bottom_id, {}).get(frame, Vector())
    pos_top = base_top + disp_top
    pos_bottom = base_bot + disp_bot

    try:
        pb_top, pb_bottom = get_rep_and_other_bones(armature)
    except RuntimeError as e:
        log.error(f"[Sandbag {armature.name}] ボーン解決失敗: {e}")
        return

    try:
        # Armature のワールド空間逆行列
        inv = armature.matrix_world.inverted()

        # 上面ボーンの tail_local に合わせるオフセット計算
        world_off_top = (inv @ pos_top) - pb_top.bone.tail_local
        rot_inv_top = pb_top.bone.matrix_local.to_3x3().inverted()
        pb_top.location = rot_inv_top @ world_off_top
        pb_top.keyframe_insert("location")

        # 下面ボーンの tail_local に合わせるオフセット計算
        world_off_bot = (inv @ pos_bottom) - pb_bottom.bone.tail_local
        rot_inv_bot = pb_bottom.bone.matrix_local.to_3x3().inverted()
        pb_bottom.location = rot_inv_bot @ world_off_bot
        pb_bottom.keyframe_insert("location")

    except Exception as e:
        log.error(f"[Sandbag {armature.name}] Bone更新失敗: {e}")
