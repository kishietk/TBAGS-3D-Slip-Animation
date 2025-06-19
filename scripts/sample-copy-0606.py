import bpy
from mathutils import Vector
import re

# === .blendファイルのパス ===
blend_path = r"C:\Users\eguchi\Documents\TBAGS-Slip-Animation\sandbag_template.blend"

# ==================================================================
# 2) テンプレートからオブジェクトをアペンド（link=False）で読み込む
# ==================================================================
with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
    # data_from.objects にテンプレート内の全オブジェクト名が入る
    data_to.objects = data_from.objects
    data_to.armatures = data_from.armatures

# これ以降、original_objects にはテンプレート内のすべてのオブジェクト（Mesh, Armature, etc.）が入っている
original_objects = data_to.objects

# ==================================================================
# 3) シーン内の「Node_XXXX」オブジェクトを探す (XXXX は 4桁以上の数字)
# ==================================================================
pattern = re.compile(r"Node_(\d{4,})")
target_objects = [obj for obj in bpy.context.scene.objects if pattern.match(obj.name)]

if not target_objects:
    print(">>> シーン内に 'Node_XXXX' 形式のオブジェクトが見つかりません。スクリプトを終了します。")
else:
    print(f">>> 見つかった Node_XXXX オブジェクト数: {len(target_objects)}\n")

# ==================================================================
# 4) 各 Node_XXXX に対してテンプレートをコピー → 配置 → リネーム → 親子付け
# ==================================================================
for target_obj in target_objects:
    match = pattern.match(target_obj.name)
    base_number = match.group(1)         # 例: "5143"
    offset = target_obj.location.copy()  # Node_XXXX のワールド位置 を取得

    print(f"\n=== 処理開始: Node '{target_obj.name}' (ベース番号={base_number}) ===")
    print(f"    ・オフセット (ワールド座標) = {offset}")

    # ────────────────────────────────────────────────────
    # 4-1) bottom 用の番号を作成（先頭数字を入れ替え）
    #      先頭が 1 → "3"+残り
    #      先頭が 5 → "11"+残り
    #      それ以外はスキップ
    # ────────────────────────────────────────────────────
    head = base_number[0]
    if head == "1":
        bottom_number = "3" + base_number[1:]    # 例: 1xxx → 3xxx
    elif head == "5":
        bottom_number = "11" + base_number[1:]   # 例: 5xxx → 11xxx
    else:
        print(f"[{base_number}] 未対応の先頭数字 '{head}' のためスキップ")
        continue

    # ────────────────────────────────────────────────────
    # 4-2) 「旧ボーン名 'top','bottom' → 新ボーン名 base_number,bottom_number」
    #      の辞書を準備する
    #      ※ テンプレート内のアーマチュアに、
    #         Edit Mode で "top" という名前のBone、
    #         Edit Mode で "bottom" という名前のBone
    #         が入っている想定とする
    # ────────────────────────────────────────────────────
    bone_rename_map = {
        "top":    base_number,     # "top" → "5143"
        "bottom": bottom_number   # "bottom" → "11143"
    }

    # ────────────────────────────────────────────────────────────
    # 4-3) コピー元オブジェクト → コピー先オブジェクト のマッピング辞書
    #       （後でメッシュ → 新アーマチュア のペアを作るときに使う）
    # ────────────────────────────────────────────────────────────
    orig_to_copy = {}

    # ────────────────────────────────────────────────────────────
    # コピー後のアーマチュアとコピー後のメッシュを別々に保存するリスト
    #  - linked_armatures: [(orig_arm, new_arm), …]
    #  - linked_meshes   : [(orig_mesh, new_mesh), …]
    # ────────────────────────────────────────────────────────────
    linked_armatures = []
    linked_meshes    = []

    # ────────────────────────────────────────────────────────────
    # 4-4) “Empty を親にしてからテンプレートをコピー” する方法
    #       これによりテンプレート内部のローカル相対配置を保持したまま移動できる
    # ────────────────────────────────────────────────────────────

    # 1) Node_XXXX の位置 (offset) に Empty を作成し配置（いったん原点に置く）
    empty = bpy.data.objects.new(f"Empty_{target_obj.name}", None)
    bpy.context.collection.objects.link(empty)
    empty.location = (0.0, 0.0, 0.0)

    # 2) original_objects をループしてコピーし、Empty の子にする
    for orig in original_objects:
        if orig is None:
            continue

        # オブジェクトを複製（データブロックもコピー）
        new_obj = orig.copy()
        if orig.data:
            new_obj.data = orig.data.copy()
        bpy.context.collection.objects.link(new_obj)

        # Empty を親にセット（ワールド座標はいじらない）
        new_obj.parent = empty
        new_obj.parent_type = 'OBJECT'

        # コピー元 → コピー先 をマッピング辞書に登録
        orig_to_copy[orig] = new_obj

        # 種類別に分けてリストに登録
        if new_obj.type == 'ARMATURE':
            linked_armatures.append((orig, new_obj))
        elif new_obj.type == 'MESH':
            linked_meshes.append((orig, new_obj))

    # 3) Empty の位置を一気に Node_XXXX の位置 (offset) に移動
    empty.location = offset
    # これで Empty の子としてぶら下がっているすべての new_obj は
    # 「元テンプレートにおけるワールド／ローカル配置 ＋ offset」 で配置される。

    print(f"    ・Empty を親にしたコピー完了 → アーマチュア数={len(linked_armatures)}, メッシュ数={len(linked_meshes)}")

    # ────────────────────────────────────────────────────────────
    # 4-5) 【デバッグ出力①】
    #       コピー後アーマチュアの data.bones にどんなボーン名があるかをリスト表示
    #       （Object Mode のまま data.bones を参照）
    # ────────────────────────────────────────────────────────────
    for orig_arm, new_arm in linked_armatures:
        print(f"■ コピー後アーマチュア: '{new_arm.name}'（コピー元: '{orig_arm.name}') の Bone 一覧:")
        bone_names = [b.name for b in new_arm.data.bones]
        for bn in bone_names:
            print(f"    - '{bn}'")
        print("    ――――――――――――――――――――――――――――――――")

    # ────────────────────────────────────────────────────────────
    # 4-6) コピー後アーマチュアの「top」「bottom」をそれぞれリネーム
    #       ※Object Mode のまま data.bones[...] を直接変更する
    # ────────────────────────────────────────────────────────────
    for orig_arm, new_arm in linked_armatures:
        print(f"→ ボーン名リネーム: コピー元アーマチュア名 = '{orig_arm.name}'")

        for old_bone, new_bone in bone_rename_map.items():
            if old_bone in new_arm.data.bones:
                new_arm.data.bones[old_bone].name = new_bone
                print(f"    [OK] Bone '{old_bone}' → '{new_bone}' in '{new_arm.name}'")
            else:
                print(f"    [Warning] Bone '{old_bone}' が '{new_arm.name}' に存在しない")

    # ────────────────────────────────────────────────────────────
    # 4-7) コピー後メッシュの頂点グループ（vertex_groups）を「top」「bottom」から置き換え
    # ────────────────────────────────────────────────────────────
    for orig_mesh, new_mesh in linked_meshes:
        # まず「orig_mesh が参照していたアーマチュア orig_arm 」を見つける
        arm_mods = [m for m in orig_mesh.modifiers if m.type == 'ARMATURE' and m.object in dict(linked_armatures).keys()]
        if not arm_mods:
            continue

        for m in arm_mods:
            orig_target_arm = m.object
            new_target_arm = orig_to_copy.get(orig_target_arm)
            if new_target_arm is None:
                continue

            # new_mesh の vertex_groups をループして、rename_map に合うものを置き換え
            for vg in new_mesh.vertex_groups:
                if vg.name in bone_rename_map:
                    old_vg = vg.name
                    vg.name = bone_rename_map[vg.name]
                    print(f"    [OK] VertexGroup '{old_vg}' → '{vg.name}' in Mesh '{new_mesh.name}'")

    # ────────────────────────────────────────────────────────────
    # 4-8) メッシュ (new_mesh) ⇔ 新アーマチュア (new_target_arm) の親子付け & モディファイア再設定
    # ────────────────────────────────────────────────────────────
    for orig_mesh, new_mesh in linked_meshes:
        for mod in orig_mesh.modifiers:
            if mod.type != 'ARMATURE':
                continue

            orig_target_arm = mod.object
            if orig_target_arm not in orig_to_copy:
                continue  # コピー先がない場合はスキップ

            new_target_arm = orig_to_copy[orig_target_arm]

            # (A) new_mesh 側の同名モディファイアがあれば new_target_arm に置き換え
            if mod.name in new_mesh.modifiers:
                new_mesh.modifiers[mod.name].object = new_target_arm
                print(f"    ・Mesh '{new_mesh.name}' の Modifier '{mod.name}' → '{new_target_arm.name}' に差し替え")
            else:
                # 名前が一致しない場合は最初に見つかった ARMATURE タイプのモディファイアを置き換え
                for nm in new_mesh.modifiers:
                    if nm.type == 'ARMATURE':
                        nm.object = new_target_arm
                        print(f"    ・Mesh '{new_mesh.name}' の最初の ARMATURE Modifier → '{new_target_arm.name}' に差し替え")
                        break

            # (B) new_mesh の親を new_target_arm に設定
            new_mesh.parent = new_target_arm
            new_mesh.parent_type = 'ARMATURE'
            print(f"    ・Mesh '{new_mesh.name}' を Armature '{new_target_arm.name}' の子に設定")

    # ────────────────────────────────────────────────────────────
    # 4-9) （オプション）コピー後アーマチュア名をすべて 'model' に揃えたい場合
    #       複数の Node を同時に処理すると名前が重複する可能性があるため、
    #       必要に応じてこの部分のコメントを外して使ってください
    # ────────────────────────────────────────────────────────────
    # for orig_arm, new_arm in linked_armatures:
    #     new_arm.name = "model"

    print(f"=== Node '{target_obj.name}' の処理 終了 ===")

print("\n>>> すべての Node_XXXX に対するテンプレート配置とリネームが完了しました。")
