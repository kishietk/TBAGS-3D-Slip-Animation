import sys
import os

# プロジェクトscriptsの絶対パスをsys.pathに（相対import対策）
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import bpy
from logging_utils import setup_logging
from cores.manager import CoreManager
from builders.nodes import build_nodes, create_node_labels
from builders.panels import build_panels, build_roof
from builders.members import build_members
from builders.materials import apply_all_materials
from animator import init_animation

log = setup_logging()


def main():
    log.info("=== Start Visualization (with CoreManager) ===")
    try:
        # シーン初期化
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()
        bpy.app.handlers.frame_change_pre.clear()

        # --- コアマネージャーからフィルタ済みデータ取得 ---
        cm = CoreManager()
        nodes = cm.get_nodes()
        edges = cm.get_edges()
        panels = cm.get_panels()

        # --- ノード球生成＋アニメ用データセット（アニメーションCSV処理省略: 必要に応じて拡張） ---
        node_objs = build_nodes(
            {n.id: n.pos for n in nodes}, radius=0.05, anim_data=None
        )
        create_node_labels({n.id: n.pos for n in nodes}, radius=0.05)

        # --- パネル・屋根生成 ---
        panel_objs = build_panels(
            {n.id: n.pos for n in nodes}, {(e.node_a.id, e.node_b.id) for e in edges}
        )
        roof_obj, roof_quads = build_roof({n.id: n.pos for n in nodes})

        # --- 柱・梁生成 ---
        member_objs = build_members(
            {n.id: n.pos for n in nodes},
            {(e.node_a.id, e.node_b.id) for e in edges},
            thickness=0.5,
        )

        # --- マテリアル一括適用 ---
        apply_all_materials(node_objs, panel_objs, roof_obj, member_objs)

        # --- アニメーションハンドラ登録 ---
        init_animation(panel_objs, roof_obj, roof_quads, member_objs, node_objs)

        log.info("=== Visualization Completed ===")
    except Exception as e:
        log.error("Error in main()")
        import traceback

        log.error(traceback.format_exc())
        print("[ERROR] See system console for details.")


if __name__ == "__main__":
    main()
