"""
Blenderシーン操作ユーティリティ
- シーン上の全オブジェクト・データブロックを一括削除する関数を提供
- スクリプト自動実行時やテスト時に“状態初期化”として利用
"""

import bpy


def clear_scene() -> None:
    """
    Blenderシーン内のすべてのオブジェクト・データブロックを削除する。

    - オブジェクト（mesh, curve, camera, light等）を全選択・削除
    - 未使用メッシュ/マテリアル/テクスチャ/画像データも全て削除しリセット

    引数:
        なし
    戻り値:
        なし（副作用としてbpy.data, bpy.contextを変更）
    例外:
        なし（Blender内部で削除できないデータはスキップ）
    """
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block, do_unlink=True)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block, do_unlink=True)
    for block in bpy.data.textures:
        bpy.data.textures.remove(block, do_unlink=True)
    for block in bpy.data.images:
        bpy.data.images.remove(block, do_unlink=True)


def duplicate_object_hierarchy(
    obj, location=None, new_name=None, link_to_collection=True
):
    """
    指定obj以下の階層をまるごと複製し、locationでワールド位置指定、名前変更可。
    子も階層ごとに親子付け再構築。新規objを返す。
    """
    obj_copy = obj.copy()
    if obj.data:
        obj_copy.data = obj.data.copy()
    if new_name:
        obj_copy.name = new_name
    if location is not None:
        obj_copy.location = location
    if link_to_collection:
        bpy.context.collection.objects.link(obj_copy)
    child_copies = []
    for child in obj.children:
        child_copy = duplicate_object_hierarchy(
            child, link_to_collection=link_to_collection
        )
        child_copy.parent = obj_copy
        child_copies.append(child_copy)
    return obj_copy


def bake_and_remove_constraints_on_duplicated_armatures(
    frame_start=None, frame_end=None, only_selected=False
):
    # 1. 対象アーマチュアのリスト
    if only_selected:
        armatures = [
            obj for obj in bpy.context.selected_objects if obj.type == "ARMATURE"
        ]
    else:
        armatures = [obj for obj in bpy.data.objects if obj.type == "ARMATURE"]

    if not armatures:
        return

    # 2. フレーム範囲の自動取得（未指定時は全アニメ範囲）
    if frame_start is None or frame_end is None:
        scene = bpy.context.scene
        frame_start = scene.frame_start
        frame_end = scene.frame_end

    # 3. Bake（見た目通りの動きをキーフレーム化、Constraint自動削除）
    bpy.ops.nla.bake(
        frame_start=frame_start,
        frame_end=frame_end,
        only_selected=only_selected,
        visual_keying=True,
        clear_constraints=True,
        use_current_action=True,
        bake_types={"POSE"},
    )
