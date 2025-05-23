# builders/columns_armature.py

import bpy
import bmesh
from mathutils import Vector, Matrix
from typing import List, Dict, Optional
from config import CYLINDER_VERTS, MEMBER_THICK

from utils.logging import setup_logging

log = setup_logging()


def build_column_with_armature(
    node_ids: List[int],
    node_positions: Dict[int, Vector],
    anim_data: Optional[Dict[int, Dict[int, Vector]]] = None,
    radius: float = MEMBER_THICK,
    segments: int = CYLINDER_VERTS,
    name_prefix: str = "Column",
) -> bpy.types.Object:
    """
    指定ノード列を通る1本の柱メッシュ＋アーマチュアを作成し、
    ノードID変位アニメデータを各ボーンに自動割当する。
    ※従来の分割柱ではなく、物理的に連続・滑らかに変形

    引数:
        node_ids: [ノードID, ...]（柱に沿った順）
        node_positions: {ノードID: Vector}
        anim_data: {ノードID: {frame: Vector(dx,dy,dz)}}
        radius: 柱半径
        segments: 円柱分割数
        name_prefix: 名前プリフィクス

    戻り値:
        Blender Object（柱メッシュ）
    """
    if len(node_ids) < 2:
        log.warning(f"Node list too short for column: {node_ids}")
        return None

    print(f"[DEBUG] build_column_with_armature called for node_ids={node_ids}")
    for nid in node_ids:
        pos = node_positions.get(nid)
        print(f"[DEBUG] Node ID {nid}: pos={pos}")

    # --- 1. アーマチュア生成 ---
    arm_data = bpy.data.armatures.new(f"{name_prefix}Arm_{node_ids[0]}")
    arm_obj = bpy.data.objects.new(f"{name_prefix}Arm_{node_ids[0]}", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")
    bone_names = []
    for i in range(len(node_ids) - 1):
        a, b = node_ids[i], node_ids[i + 1]
        head = node_positions[a]
        tail = node_positions[b]
        bone = arm_data.edit_bones.new(f"{a}_{b}")
        bone.head = head
        bone.tail = tail
        if i > 0:
            bone.parent = arm_data.edit_bones[bone_names[-1]]
            bone.use_connect = False  # 単独選択・回転を可能に
        bone_names.append(f"{a}_{b}")
        print(f"[DEBUG] Bone {i}: {bone.name}, head={head}, tail={tail}")
    bpy.ops.object.mode_set(mode="OBJECT")

    # --- 2. シリンダーメッシュ連結生成 ---
    meshes = []
    for i in range(len(node_ids) - 1):
        a, b = node_ids[i], node_ids[i + 1]
        head = node_positions[a]
        tail = node_positions[b]
        direction = tail - head
        length = direction.length
        if length < 1e-6:
            continue  # ほぼゼロ距離は無視
        # シリンダー作成（Blender原点、Z軸方向、長さ=1でまず作る）
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius,
            depth=length,
            vertices=segments,
            location=(0, 0, 0),
            end_fill_type="NGON",
        )
        cyl = bpy.context.object
        # 各区間ごとに正しい位置・向きに移動・回転
        # 1. まずZ軸方向にlength分（0,0,length/2）で原点基準
        cyl.location = (0, 0, length / 2)
        # 2. 各ノード間の向きに回転（Z→directionへアライン）
        direction_norm = direction.normalized()
        up = Vector((0, 0, 1))
        if direction_norm != up and direction_norm != -up:
            axis = up.cross(direction_norm)
            angle = up.angle(direction_norm)
            rot_matrix = Matrix.Rotation(angle, 4, axis)
        else:
            rot_matrix = (
                Matrix.Identity(4)
                if direction_norm == up
                else Matrix.Rotation(3.14159, 4, "X")
            )
        cyl.matrix_world = rot_matrix @ cyl.matrix_world
        # 3. head位置に平行移動
        cyl.location = rot_matrix @ Vector((0, 0, length / 2)) + head
        meshes.append(cyl)
        print(
            f"[DEBUG] Cylinder {i}: location={cyl.location}, length={length}, axis={direction_norm}"
        )

    # --- 3. 全区間シリンダーを1つのオブジェクトに統合 ---
    if len(meshes) == 0:
        log.error("No mesh segments generated for this column.")
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for cyl in meshes:
        cyl.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    column_mesh_obj = bpy.context.object
    column_mesh_obj.name = f"{name_prefix}_{node_ids[0]}"

    # --- 4. Armatureモディファイア ---
    column_mesh_obj.modifiers.new(type="ARMATURE", name="Armature")
    column_mesh_obj.modifiers["Armature"].object = arm_obj

    # --- 5. 自動ウェイト割当 ---
    bpy.ops.object.select_all(action="DESELECT")
    column_mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    log.info(
        f"Column mesh '{column_mesh_obj.name}' parented to armature '{arm_obj.name}' with automatic weights."
    )

    # --- 6. 各ボーンにノードの変位アニメーションを登録 ---
    # ※各ノードの変位を該当ボーンのhead/tailのポーズに反映
    if anim_data is not None:
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.mode_set(mode="POSE")
        for i, bone_name in enumerate(bone_names):
            a = node_ids[i]
            b = node_ids[i + 1]
            pose_bone = arm_obj.pose.bones.get(bone_name)
            if not pose_bone:
                continue
            node_anim_a = anim_data.get(a, {})
            node_anim_b = anim_data.get(b, {})
            for frame in sorted(set(node_anim_a.keys()) | set(node_anim_b.keys())):
                # head/tailの変位を計算
                offset_head = node_anim_a.get(frame, Vector((0, 0, 0)))
                offset_tail = node_anim_b.get(frame, Vector((0, 0, 0)))
                # Blenderボーンはローカル変換なので、近似的にhead/tailの差分で回転・スケールも設定したい場合は要調整
                # 今回はロケーションだけ単純適用
                pose_bone.location = offset_head
                pose_bone.keyframe_insert(data_path="location", frame=frame)
                # tail側の変位を反映したければ、より細かなボーンコントロールが必要（今回省略）

################################
# tail側の変位を反映する必要がある
################################














        bpy.ops.object.mode_set(mode="OBJECT")

    log.info(f"Column with armature built: {column_mesh_obj.name} / {arm_obj.name}")
    return column_mesh_obj
