# main.py
"""
責務:
- プロジェクトの実行起点。
- sys.pathやプロジェクトパスの設定も担い、utils/main_utils.pyの各工程を呼ぶ。
"""

import sys
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from utils.main_utils import (
    setup_scene,
    load_all_data,
    build_core_model,
    build_blender_objects_from_core,
    apply_materials_to_all,
    setup_animation_handlers,
)


def main():
    """
    役割:
        全体フローの実行（setup→load→core構築→Blenderオブジェクト生成→マテリアル適用→アニメハンドラ登録）。
    """
    setup_scene()
    nodes_data, edges_data, anim_data = load_all_data()
    core = build_core_model(nodes_data, edges_data)
    blender_objs = build_blender_objects_from_core(core)
    apply_materials_to_all(blender_objs)
    setup_animation_handlers(core, anim_data, blender_objs)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[CRITICAL] Application failed: {e}")
