import bpy
from mathutils import Vector
from config import ANIM_TOTAL_FRAMES
from utils.logging_utils import setup_logging

log = setup_logging()
PROP_NAME = "combined_frame_data_vec"
ORDERED_KEYS = []  # グローバルに保存

def rebake_all_armatures(frame_start=1, frame_end=None):
    if frame_end is None:
        frame_end = ANIM_TOTAL_FRAMES

    armatures = [obj for obj in bpy.context.view_layer.objects if obj.type == 'ARMATURE']
    if not armatures:
        log.warning("No armatures found to bake.")
        return

    bpy.ops.object.select_all(action='DESELECT')
    for arm in armatures:
        arm.select_set(True)

    bpy.context.view_layer.objects.active = armatures[0]

    try:
        bpy.ops.nla.bake(
            frame_start=frame_start,
            frame_end=frame_end,
            only_selected=True,
            visual_keying=True,
            clear_constraints=False,
            use_current_action=True,
            bake_types={'POSE'},
        )
        log.info(f"Rebaked {len(armatures)} armatures.")
    except Exception as e:
        log.error(f"Rebake failed: {e}")
        return

    # NLAストリップからアクション復元
    for arm in armatures:
        if not arm.animation_data:
            continue
        if not arm.animation_data.action:
            for track in arm.animation_data.nla_tracks:
                for strip in track.strips:
                    if strip.action:
                        arm.animation_data.action = strip.action
                        break

def collect_sandbag_anim_data():
    anim_data = {}
    for obj in bpy.data.objects:
        if obj.type != 'ARMATURE' or not obj.animation_data:
            continue
        action = obj.animation_data.action
        if not action:
            continue

        for fcurve in action.fcurves:
            if not fcurve.data_path.startswith("pose.bones["):
                continue
            start = fcurve.data_path.find("[\"") + 2
            end = fcurve.data_path.find("\"]")
            bone_name = fcurve.data_path[start:end]
            if bone_name not in anim_data:
                anim_data[bone_name] = {}

            for kp in fcurve.keyframe_points:
                frame = int(kp.co[0])
                value = kp.co[1]
                if frame not in anim_data[bone_name]:
                    anim_data[bone_name][frame] = Vector((0.0, 0.0, 0.0))
                vec = anim_data[bone_name][frame]
                if fcurve.array_index == 0:
                    vec.x = value
                elif fcurve.array_index == 1:
                    vec.y = value
                elif fcurve.array_index == 2:
                    vec.z = value
                anim_data[bone_name][frame] = vec
    return anim_data

def setup_ordered_keys(sandbag_anim_data):
    global ORDERED_KEYS
    ORDERED_KEYS = []
    for arm_obj in bpy.data.objects:
        if arm_obj.type != 'ARMATURE' or not arm_obj.pose:
            continue
        for bone_id in sandbag_anim_data.keys():
            if bone_id in arm_obj.pose.bones:
                ORDERED_KEYS.append(f"{arm_obj.name}:{bone_id}")
    ORDERED_KEYS = sorted(set(ORDERED_KEYS))

def update_pose_from_mastercontrol(scene):
    master = bpy.data.objects.get("MasterControl")
    if not master or PROP_NAME not in master:
        return
    vec_data = master.get(PROP_NAME)
    if not vec_data or len(ORDERED_KEYS) * 3 > len(vec_data):
        return

    for i, key in enumerate(ORDERED_KEYS):
        arm_name, bone_name = key.split(":")
        arm_obj = bpy.data.objects.get(arm_name)
        if not arm_obj or not arm_obj.pose:
            continue
        bone = arm_obj.pose.bones.get(bone_name)
        if not bone:
            continue
        offset = Vector((
            vec_data[i * 3 + 0],
            vec_data[i * 3 + 1],
            vec_data[i * 3 + 2],
        ))
        bone.location = offset  # 必要に応じて rotation_euler/matrix へ変更可能

def enable_mastercontrol_handler():
    if update_pose_from_mastercontrol not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(update_pose_from_mastercontrol)
        print("✔ MasterControl runtime handler enabled.")

def bake_combined_sandbag_animation():
    # ① 再ベイク
    rebake_all_armatures()

    # ② データ取得
    sandbag_anim_data = collect_sandbag_anim_data()
    setup_ordered_keys(sandbag_anim_data)

    # ③ MasterControl を準備
    master = bpy.data.objects.get("MasterControl")
    if not master:
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        master = bpy.context.active_object
        master.name = "MasterControl"

    # ④ ベクトルをフレームごとに挿入
    for frame in range(1, ANIM_TOTAL_FRAMES + 1):
        vec_data = []
        for key in ORDERED_KEYS:
            arm_name, bone_name = key.split(":")
            frames_dict = sandbag_anim_data.get(bone_name, {})
            disp = frames_dict.get(frame, Vector((0.0, 0.0, 0.0)))
            vec_data.extend([disp.x, disp.y, disp.z])
        master[PROP_NAME] = vec_data
        master.keyframe_insert(data_path=f'["{PROP_NAME}"]', frame=frame)

    log.info("✅ MasterControl に combined_frame_data_vec を記録しました。")

    # ⑤ 他オブジェクトのアニメーション削除
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE' and obj.name != "MasterControl":
            if obj.animation_data:
                obj.animation_data_clear()

    # ⑥ ハンドラ登録
    enable_mastercontrol_handler()
