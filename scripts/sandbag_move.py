import bpy
from mathutils import Vector
from utils.logging_utils import setup_logging
from config import ANIM_TOTAL_FRAMES

log = setup_logging()

def bake_sandbag_bone_animation(sandbag_anim_data):
    for arm_obj in bpy.data.objects:
        if arm_obj is None or arm_obj.type != 'ARMATURE':
            continue
        if arm_obj.pose is None:
            continue
        pose_bones = arm_obj.pose.bones
        # ボーン名一覧
        # bone_names = [b.name for b in pose_bones]
        # log.info(f"Armature {arm_obj.name}: bone_names={bone_names}")
        
        for nid, frames_dict in sandbag_anim_data.items():
            bone_name = str(nid)
            if bone_name not in pose_bones:
                continue
            pose_bone = pose_bones[bone_name]
            #log.info(f"Bake: {bone_name} ボーン")
            
            base_loc = pose_bone.location.copy()
            for frame in range(1, ANIM_TOTAL_FRAMES + 1):
                disp = frames_dict.get(frame, Vector((0, 0, 0)))
                pose_bone.location = base_loc + disp
                for i in range(3):
                    pose_bone.keyframe_insert(data_path="location", frame=frame, index=i)

