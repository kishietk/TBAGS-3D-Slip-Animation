"""
main.py

【役割】
- プロジェクトのBlenderビジュアライズ処理を統合的に管理・実行するエントリポイント。
- 全てのパラメータ・パス・設定値はconfig.pyからimport。
- 処理の進捗・異常・完了を詳細ログで現場水準に記録。

【設計方針】
- try/exceptでコア処理全体を守り、エラー時は詳細なトレースバックもログ。
- 再実行時の多重ハンドラや多重生成を防止。
- ロード・ビルド・アニメ登録処理を明確に段階分け。
"""

import sys
import os
import importlib
import logging
import traceback

import bpy

# プロジェクトscriptsの絶対パスをsys.pathに（相対import対策）
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

# -----------------------------
# 1. パス初期化・loggingセットアップ
# -----------------------------
from logging_utils import setup_logging
log = setup_logging()

# -----------------------------
# 2. モジュールimport＆リロード（開発時ホットリロードにも対応）
# -----------------------------
try:
    import config
    import loaders.node as node_loader
    import loaders.edge as edge_loader
    import loaders.animation as anim_loader
    import builders.nodes as nodes_builder
    import builders.panels as panels_builder
    import builders.members as members_builder
    import builders.materials as materials
    import animator

    importlib.reload(config)
    importlib.reload(node_loader)
    importlib.reload(edge_loader)
    importlib.reload(anim_loader)
    importlib.reload(nodes_builder)
    importlib.reload(panels_builder)
    importlib.reload(members_builder)
    importlib.reload(materials)
    importlib.reload(animator)

    # config値の一括import（明示的に）
    from config import (
        NODE_CSV,
        EDGES_FILE,
        ANIM_CSV,
        SPHERE_RADIUS,
        MEMBER_THICK,
        ANIM_FPS,
        ANIM_TOTAL_FRAMES,
    )
    from loaders.node import load_nodes
    from loaders.edge import load_edges
    from loaders.animation import load_animation_data
    from builders.nodes import clear_scene, build_nodes, create_node_labels
    from builders.panels import build_panels, build_roof
    from builders.members import build_members
    from builders.materials import apply_all_materials
    from animator import init_animation

except Exception as e:
    log.critical(f"Module import or reload failed: {e}")
    log.critical(traceback.format_exc())
    sys.exit(1)


# -----------------------------
# 3. コア処理本体
# -----------------------------
def main():
    log.info("=== Start Visualization ===")
    try:
        # (0) シーン初期化（多重実行でも安全に）
        clear_scene()
        bpy.app.handlers.frame_change_pre.clear()

        # (1) ノード・エッジロード
        log.info(f"Reading node data from: {NODE_CSV}")
        nodes = load_nodes(NODE_CSV)
        log.info(f"Reading edge data from: {EDGES_FILE}")
        edges = load_edges(EDGES_FILE)
        log.info(f"{len(nodes)} nodes, {len(edges)} edges loaded")

        # (2) アニメーションデータロード
        anim_data = load_animation_data(ANIM_CSV)

        # (3) アニメーション・レンダ設定
        scene = bpy.context.scene
        scene.frame_start = 0
        scene.frame_end = ANIM_TOTAL_FRAMES
        scene.render.fps = ANIM_FPS

        # (4) モデル生成
        node_objs = build_nodes(nodes, SPHERE_RADIUS, anim_data)
        create_node_labels(nodes, SPHERE_RADIUS)
        panel_objs = build_panels(nodes, edges)
        roof_obj, roof_quads = build_roof(nodes)
        member_objs = build_members(nodes, edges, MEMBER_THICK)

        # (5) マテリアル適用
        apply_all_materials(node_objs, panel_objs, roof_obj, member_objs)

        # (6) アニメーションハンドラ登録
        init_animation(panel_objs, roof_obj, roof_quads, member_objs, node_objs)

        log.info("=== Visualization Completed ===")

    except Exception as e:
        log.error("Error in main()")
        log.error(traceback.format_exc())
        print("[ERROR] See system console for details.")


# -----------------------------
# 4. エントリポイント（Blender実行時）
# -----------------------------
if __name__ == "__main__":
    main()
