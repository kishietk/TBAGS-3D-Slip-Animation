import sys
import os
import importlib

# --- パス設定 ---
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

# --- ホットリロード対象モジュールリスト ---
MODULES = [
    "config",
    "utils.logging_utils",
    "loaders.node_loader",
    "loaders.edge_loader",
    "loaders.animation_loader",
    "cores.node",
    "cores.edge",
    "cores.panel",
    "cores.manager",
    "builders.nodes",
    "builders.panels",
    "builders.materials",
    "builders.columns",
    "builders.beams",
    "builders.scene_factory",
    "utils.scene_utils",
    "animators.animator",
]

for m in MODULES:
    try:
        if m in locals():
            importlib.reload(locals()[m])
        elif m in globals():
            importlib.reload(globals()[m])
        else:
            globals()[m] = importlib.import_module(m)
    except Exception as e:
        print(f"[WARN] Failed to reload/import {m}: {e}")

# --- 各種import ---
import bpy
from utils.logging_utils import setup_logging
from utils.scene_utils import clear_scene
from cores.manager import CoreManager
from loaders.animation_loader import load_animation_data
from builders.scene_factory import create_blender_objects
from builders.materials import apply_all_materials
from animators.animator import init_animation

log = setup_logging()


def main():
    log.info("=== Start Visualization ===")
    try:
        clear_scene()
        cm = CoreManager()
        nodes, edges, panels = cm.get_nodes(), cm.get_edges(), cm.get_panels()
        column_edges, beam_edges = cm.classify_edges()
        anim_data = load_animation_data()
        node_objs, panel_objs, roof_obj, roof_quads, member_objs = (
            create_blender_objects(nodes, column_edges, beam_edges, anim_data)
        )
        apply_all_materials(node_objs, panel_objs, roof_obj, member_objs)
        init_animation(panel_objs, roof_obj, roof_quads, member_objs, node_objs)
        log.info("=== Visualization Completed ===")
    except Exception as e:
        log.error("Error in main()")
        import traceback

        log.error(traceback.format_exc())
        print("[ERROR] See system console for details.")


if __name__ == "__main__":
    main()
