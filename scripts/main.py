"""
責務:
- プロジェクトの実行起点。
- 引数で地震データセットやT-BAGS有無を切り替え可能。
"""

import sys
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from configs import paths
from utils.main_utils import (
    parse_args,
    get_dataset_from_args,
    setup_scene,
    load_all_data,
    build_core_model,
    build_blender_objects_from_core,
    apply_materials_to_all,
    setup_animation_handlers,
)


def main():
    args = parse_args()
    dataset = get_dataset_from_args(args, paths.EARTHQUAKE_DATASETS)
    node_csv = dataset["node_csv"]
    node_anim_csv = dataset["node_anim_csv"]
    earthquake_anim_csv = dataset["earthquake_anim_csv"]

    setup_scene()
    nodes_data, edges_data, anim_data, eq_anim_data = load_all_data(
        node_csv=node_csv,
        node_anim_csv=node_anim_csv,
        earthquake_anim_csv=earthquake_anim_csv,
    )
    core = build_core_model(nodes_data, edges_data)
    blender_objs = build_blender_objects_from_core(core)
    apply_materials_to_all(blender_objs)
    setup_animation_handlers(core, anim_data, blender_objs, eq_anim_data)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[CRITICAL] Application failed: {e}")
