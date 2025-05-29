# main.py
"""
Blender構造可視化スクリプトのエントリーポイント

- ホットリロード対象モジュールは config.py で集中管理
- ホットリロード処理は hotreload_utils.py で関数化
- 各責務ごとに関数分離し main() で処理フローを明確化
- CLI/バッチ実行用
"""

import sys
import os

# プロジェクトルートをimportパスに追加
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from config import HOTRELOAD_MODULES
from utils.hotreload_utils import reload_modules


def initialize_scene():
    """Blenderシーンの初期化（全オブジェクト・データ削除）"""
    from utils.scene_utils import clear_scene

    clear_scene()


def build_core_data():
    """コアデータ（ノード・エッジ・パネル等）をCoreManager経由で構築"""
    from cores.CoreManager import CoreManager

    return CoreManager()


def load_animation_data_main():
    """アニメーションデータをCSV等からロード"""
    from loaders.animation_loader import load_animation_data

    return load_animation_data()


def build_blender_objects(cm, anim_data):
    """
    コアデータ・アニメーションデータからBlenderオブジェクト群生成
    戻り値: (node_objs, sandbag_objs, panel_objs, roof_obj, roof_quads, member_objs)
    """
    from builders.scene_factory import create_blender_objects

    nodes = cm.get_nodes()
    panels = cm.get_panels()
    column_edges, beam_edges = cm.classify_edges()
    return create_blender_objects(
        nodes=nodes,
        column_edges=column_edges,
        beam_edges=beam_edges,
        anim_data=anim_data,
        panels=panels,
    )


def apply_materials(node_objs, sandbag_objs, panel_objs, roof_obj, member_objs):
    """
    生成済みBlenderオブジェクトにマテリアル一括適用
    """
    from builders.materials import apply_all_materials

    apply_all_materials(
        node_objs=node_objs,
        sandbag_objs=sandbag_objs,
        panel_objs=panel_objs,
        roof_obj=roof_obj,
        member_objs=member_objs,
    )


def register_animation_handler(
    panel_objs,
    roof_obj,
    roof_quads,
    member_objs,
    node_objs,
    sandbag_objs,
    anim_data,
    sandbag_anim_data,
    base_node_pos,
    base_sandbag_pos,
):
    from animators.animator import init_animation

    init_animation(
        panel_objs,
        roof_obj,
        roof_quads,
        member_objs,
        node_objs,
        sandbag_objs,
        anim_data,
        sandbag_anim_data,
        base_node_pos,
        base_sandbag_pos,
    )


def main():
    """可視化シーン生成のメイン処理"""
    import bpy
    from utils.logging_utils import setup_logging
    from config import SANDBAG_NODE_KIND_IDS

    log = setup_logging("main")
    log.info("=== Start Visualization ===")

    try:
        # 1. シーン初期化
        initialize_scene()

        # 2. コアデータ生成
        cm = build_core_data()
        log.info(
            f"Nodes: {len(cm.nodes)} / Edges: {len(cm.edges)} / Panels: {len(cm.panels)}"
        )

        # 3. アニメーションデータ読込
        anim_data = load_animation_data_main()

        # 4. Blenderオブジェクト生成
        node_objs, sandbag_objs, panel_objs, roof_obj, roof_quads, member_objs = (
            build_blender_objects(cm, anim_data)
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
        apply_materials(
            node_objs=node_objs,
            sandbag_objs=sandbag_objs,
            panel_objs=panel_objs,
            roof_obj=roof_obj,
            member_objs=member_objs,
        )

        # 6. アニメーションイベント登録
        register_animation_handler(
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
    reload_modules(HOTRELOAD_MODULES, globals())
    main()
