import sys
import os
import importlib

# --- モジュールホットリロード ---
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

MODULES = [
    "config",
    "logging_utils",
    "loader.node_loader",
    "loader.edge_loader",
    "loader.animation_loader",
    "cores.manager",
    "builders.nodes",
    "builders.panels",
    "builders.materials",
    "builders.columns",
    "builders.beams",
    "animator",
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

import bpy
from logging_utils import setup_logging
from cores.manager import CoreManager
from builders.nodes import build_nodes, create_node_labels
from builders.panels import build_panels, build_roof
from builders.columns import build_columns
from builders.beams import build_beams
from builders.materials import apply_all_materials
from loaders.animation_loader import load_animation_data
from config import COLUMNS_KIND_IDS, BEAMS_KIND_IDS
from animator import init_animation

log = setup_logging()


def main():
    log.info("=== Start Visualization (with CoreManager) ===")
    try:
        # --- Blenderシーン初期化 ---
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()
        bpy.app.handlers.frame_change_pre.clear()

        # --- データ構築 ---
        cm = CoreManager()
        nodes = cm.get_nodes()
        edges = cm.get_edges()
        panels = cm.get_panels()

        # kind_idで柱・梁分類
        column_edges = [
            (e.node_a.id, e.node_b.id) for e in edges if e.kind_id in COLUMNS_KIND_IDS
        ]
        beam_edges = [
            (e.node_a.id, e.node_b.id) for e in edges if e.kind_id in BEAMS_KIND_IDS
        ]

        log.info(f"Number of column edges: {len(column_edges)}")
        log.info(f"Number of beam edges:   {len(beam_edges)}")

        # ノード座標デバッグ出力
        for n in nodes:
            log.info(f"Node {n.id}: pos={tuple(n.pos)}")

        # アニメーションデータ
        anim_data = load_animation_data()

        # ノード球生成＋アニメ
        node_objs = build_nodes(
            {n.id: n.pos for n in nodes}, radius=0.05, anim_data=anim_data
        )
        create_node_labels({n.id: n.pos for n in nodes}, radius=0.05)

        # パネル・屋根生成
        panel_objs = build_panels(
            {n.id: n.pos for n in nodes}, set(column_edges + beam_edges)
        )
        roof_obj, roof_quads = build_roof({n.id: n.pos for n in nodes})

        # 柱・梁生成
        column_objs = build_columns(
            {n.id: n.pos for n in nodes}, set(column_edges), thickness=0.5
        )
        beam_objs = build_beams(
            {n.id: n.pos for n in nodes}, set(beam_edges), thickness=0.5
        )

        # (obj, a, b) 形式で統一
        all_member_objs = []
        for t in column_objs + beam_objs:
            all_member_objs.append(t[:3])

        apply_all_materials(node_objs, panel_objs, roof_obj, all_member_objs)

        init_animation(
            panel_objs=panel_objs,
            roof_obj=roof_obj,
            roof_quads=roof_quads,
            member_objs=all_member_objs,
            node_objs=node_objs,
        )

        log.info("=== Visualization Completed ===")
    except Exception as e:
        log.error("Error in main()")
        import traceback

        log.error(traceback.format_exc())
        print("[ERROR] See system console for details.")


if __name__ == "__main__":
    main()
