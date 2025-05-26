import bpy


def clear_scene():
    """Blenderシーン初期化（全削除 & アニメハンドラクリア）"""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.app.handlers.frame_change_pre.clear()
