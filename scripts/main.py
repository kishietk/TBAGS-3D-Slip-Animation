# Blender用実行エントリースクリプト（ホットリロード対応）
# 全ビルド・マテリアル適用・アニメーション登録を一括実行する

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
    "utils.scene_utils",
    "loaders.node_loader",
    "loaders.edge_loader",
    "loaders.animation_loader",
    "cores.node",
    "cores.edge",
    "cores.panel",
    "cores.beam",
    "cores.column",
    "cores.CoreManager",
    "builders.nodes",
    "builders.panels",
    "builders.materials",
    "builders.columns",
    "builders.beams",
    "builders.scene_factory",
    "animators.animator",
]

for m in MODULES:
    try:
        # モジュールがすでにロードされていればreload、なければimport
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
from cores.CoreManager import CoreManager
from loaders.animation_loader import load_animation_data
from builders.scene_factory import create_blender_objects
from builders.materials import apply_all_materials
from animators.animator import init_animation

log = setup_logging()


def main():
    """
    構造可視化シーンを初期化・構築する
    引数:
        なし
    戻り値:
        なし
    """
    log.info("=== Start Visualization ===")
    try:
        # シーン初期化（全オブジェクト削除）
        clear_scene()
        # コアデータ生成・取得
        cm = CoreManager()
        log.info(f"After init: node count = {len(cm.nodes)}")
        log.info(f"After init: edge count = {len(cm.edges)}")
        log.info(f"After init: panel count = {len(cm.panels)}")
        # ノード詳細（例：最初の5つ）
        for n in list(cm.get_nodes())[:5]:
            log.info(
                f"Node: id={n.id}, pos={tuple(n.pos)}, kind_id={getattr(n, 'kind_id', None)}"
            )
        # パネル情報も一部表示（例：最初の3つ）
        for p in list(cm.get_panels())[:3]:
            log.info(f"Panel: node_ids={[node.id for node in p.nodes]}")

        # コアデータ
        nodes = cm.get_nodes()
        panels = cm.get_panels()
        column_edges, beam_edges = cm.classify_edges()
        anim_data = load_animation_data()

        # Blenderオブジェクト生成（コアPanelからパネル作成！）
        node_objs, panel_objs, roof_obj, roof_quads, member_objs = (
            create_blender_objects(
                nodes, column_edges, beam_edges, anim_data, panels=panels
            )
        )
        # マテリアル適用
        apply_all_materials(node_objs, panel_objs, roof_obj, member_objs)
        # アニメーションイベント登録
        init_animation(panel_objs, roof_obj, roof_quads, member_objs, node_objs)
        log.info("=== Visualization Completed ===")
    except Exception as e:
        log.error("Error in main()")
        import traceback

        log.error(traceback.format_exc())
        print("[ERROR] See system console for details.")


if __name__ == "__main__":
    main()
