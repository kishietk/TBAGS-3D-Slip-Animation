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
