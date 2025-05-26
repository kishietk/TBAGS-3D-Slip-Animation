# Blenderシーン操作ユーティリティ
# シーン上の全オブジェクトを一括削除する関数を提供する

import bpy


def clear_scene() -> None:
    """
    Blenderシーン内のすべてのオブジェクトを削除する
    引数:
        なし
    戻り値:
        なし
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
