import bpy
import csv

# CSVファイルのパス
csv_path = "C:\\Users\\eguchi\\Desktop\\XR\\資料\\Blender\\地震波\\3story-with T-BAGS-Steel-Kumamoto - コピー絶対.csv"

# FPS取得
fps = bpy.context.scene.render.fps

# すべてのアーマチュアのキーフレーム削除（必要であれば条件付きにしてもOK）
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE' and 'model' in obj.name.lower():
        obj.animation_data_clear()

# CSV読み込み
with open(csv_path, newline='', encoding='cp932') as csvfile:
    reader = list(csv.reader(csvfile))
    type_row = reader[2]     # DISPなど
    axis_row = reader[3]     # 1, 2, 3
    target_row = reader[4]   # ボーン名（例：1143）
    data_rows = reader[6:]   # 時系列データ

# 有効な列の抽出
valid_columns = []
for col_idx in range(1, len(axis_row)):
    try:
        if type_row[col_idx].strip().upper() != "DISP":
            continue
        axis_code = int(axis_row[col_idx])
        target_name = target_row[col_idx].strip()
        if target_name and axis_code in [1, 2, 3]:
            valid_columns.append((col_idx, target_name, axis_code))
    except (ValueError, IndexError):
        continue

# 「model」を名前に含むアーマチュアのみ処理
for obj in bpy.context.view_layer.objects:
    if obj.type != 'ARMATURE':
        continue
    if 'model' not in obj.name.lower():
        continue

    print(f"処理中のアーマチュア: {obj.name}")
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = obj.pose.bones

    # 初期位置を記録
    initial_locations = {
        name: bone.location.copy() for name, bone in pose_bones.items()
    }

    for col_idx, target_name, axis_code in valid_columns:
        pose_bone = pose_bones.get(target_name)
        if not pose_bone:
            print(f"⚠ ボーン「{target_name}」が見つかりません（{obj.name}）")
            continue

        base_loc = initial_locations[target_name].copy()

        for row in data_rows:
            if len(row) <= col_idx:
                continue
            try:
                time_sec = float(row[0])
                offset = float(row[col_idx])
            except ValueError:
                continue

            frame = int(time_sec * fps)
            new_loc = list(base_loc)
            new_loc[axis_code - 1] += offset

            pose_bone.location = new_loc
            pose_bone.keyframe_insert(data_path="location", frame=frame, index=axis_code - 1)
