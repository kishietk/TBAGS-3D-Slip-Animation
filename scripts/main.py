"""
Blender構造可視化スクリプトのエントリーポイント
"""

import sys
import os

# プロジェクトルートをimportパスに追加
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

def main():
    from utils.logging_utils import setup_logging
    from config import SANDBAG_NODE_KIND_IDS

    log = setup_logging("main")
    log.info("=== Start Visualization ===")

    try:
        # 1. シーン初期化
        from utils.scene_utils import clear_scene

        clear_scene()

        # 2. コアデータ生成
        from cores.CoreManager import CoreManager

        cm = CoreManager()
        log.info(
            f"Nodes: {len(cm.nodes)} / Edges: {len(cm.edges)} / Panels: {len(cm.panels)}"
        )

        # 3. アニメーションデータ読込
        from loaders.animation_loader import load_animation_data

        anim_data = load_animation_data()

        # 4. Blenderオブジェクト生成
        from builders.scene_factory import create_blender_objects

        node_objs, sandbag_objs, panel_objs, roof_obj, roof_quads, member_objs = (
            create_blender_objects(
                nodes=cm.get_nodes(),
                column_edges=cm.classify_edges()[0],
                beam_edges=cm.classify_edges()[1],
                anim_data=anim_data,
                panels=cm.get_panels(),
            )
        )

        # --- サンドバッグとノードでIDを分割 ---
        nodes = cm.get_nodes()
        base_node_pos = {
            n.id: n.pos
            for n in nodes
            if not (hasattr(n, "kind_id") and n.kind_id in SANDBAG_NODE_KIND_IDS)
        }
        base_sandbag_pos = {
            n.id: n.pos
            for n in nodes
            if (hasattr(n, "kind_id") and n.kind_id in SANDBAG_NODE_KIND_IDS)
        }
        sandbag_anim_data = {
            nid: v for nid, v in anim_data.items() if nid in base_sandbag_pos
        }
        node_anim_data = {
            nid: v for nid, v in anim_data.items() if nid in base_node_pos
        }

        # 5. マテリアル適用
        from builders.materials import apply_all_materials

        apply_all_materials(
            node_objs=node_objs,
            sandbag_objs=sandbag_objs,
            panel_objs=panel_objs,
            roof_obj=roof_obj,
            member_objs=member_objs,
        )

        # 6. アニメーションイベント登録
        from animators.animator import init_animation

        init_animation(
            panel_objs,
            roof_obj,
            roof_quads,
            member_objs,
            node_objs,
            sandbag_objs,
            node_anim_data,
            sandbag_anim_data,
            base_node_pos,
            base_sandbag_pos,
        )

        log.info("=== Visualization Completed ===")

    except Exception as e:
        log.error("Error in main()")
        import traceback

        log.error(traceback.format_exc())
        print("[ERROR] See system console for details.")


if __name__ == "__main__":
    main()
