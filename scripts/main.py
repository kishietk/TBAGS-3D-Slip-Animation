import bpy
import sys
import os
import importlib
import logging

# ────────────────────────────────
# 1. パス設定：プロジェクトのルートフォルダを sys.path に追加
#    → こうすることで「import scripts.xxx」がどこからでも解決できる
# ────────────────────────────────
project_root = os.path.expanduser("~/Documents/TBAGS-3D-Slip-Animation")
scripts_dir = os.path.join(project_root, "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

# ────────────────────────────────
# 2. ロギング初期化
# ────────────────────────────────
try:
    from logging_utils import setup_logging

    # ログレベル：開発時はlogging.DEBUG、本番はlogging.ERROR推奨
    log = setup_logging(logging.ERROR)
except Exception:
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("fallback")
    log.warning("Fallback logger initialized.")

# ────────────────────────────────
# 3. モジュール読み込み＆リロード（Blender再起動不要）
# ────────────────────────────────
try:
    # 各種設定・ローダ・ビルダー・アニメーターのimport
    import config
    import loaders.node as node_loader
    import loaders.edge as edge_loader
    import loaders.animation as anim_loader
    import builders.nodes as nodes_builder
    import builders.panels as panels_builder
    import builders.members as members_builder
    import builders.materials as materials
    import animator

    # --- Blenderスクリプト開発ではモジュールリロードが超重要！ ---
    importlib.reload(config)
    importlib.reload(node_loader)
    importlib.reload(edge_loader)
    importlib.reload(anim_loader)
    importlib.reload(nodes_builder)
    importlib.reload(panels_builder)
    importlib.reload(members_builder)
    importlib.reload(materials)
    importlib.reload(animator)

    # 設定値・関数を必要分だけimport
    from config import (
        NODE_CSV,
        EDGES_FILE,
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
    log.error(f"Module import error: {e}")
    raise


# ────────────────────────────────
# 4. メイン処理：構造モデルの構築とアニメーション設定
# ────────────────────────────────
def main():
    """
    Blenderシーン上で構造モデルを生成し、アニメーションも適用するメイン処理

    【処理の流れ】
    1. シーンをクリア
    2. ノード・エッジデータをCSV/STRファイルから読み込み
    3. アニメーションCSVを読み込み
    4. シーンのアニメーション設定（FPSやフレーム数など）
    5. ノード球生成＆アニメ付与
    6. ノードIDラベル生成
    7. 壁パネル・屋根・柱梁を自動生成
    8. 全部にマテリアル一括適用
    9. アニメーションハンドラ登録
    """
    log.info("=== Start Visualization ===")
    try:
        # 4-1. シーンを完全クリア
        clear_scene()

        # 4-2. ノード・エッジデータを読み込み
        log.info(f"Reading node data from: {NODE_CSV}")
        nodes = load_nodes(NODE_CSV)

        log.info(f"Reading edge data from: {EDGES_FILE}")
        edges = load_edges(EDGES_FILE)

        log.info(f"{len(nodes)} nodes, {len(edges)} edges loaded")

        # 4-3. アニメーションデータを読み込み
        anim_data = load_animation_data()

        # 4-4. シーンのアニメーション設定（FPSやフレーム数など）
        scene = bpy.context.scene
        scene.frame_start = 0
        scene.frame_end = ANIM_TOTAL_FRAMES
        scene.render.fps = ANIM_FPS

        # 4-5. ノード球生成＆アニメーション
        node_objs = build_nodes(nodes, SPHERE_RADIUS, anim_data)
        # 4-6. ノードIDラベルを球に子として配置
        create_node_labels(nodes, SPHERE_RADIUS)

        # 4-7. 壁パネル・屋根・柱梁の生成
        panel_objs = build_panels(nodes, edges)
        roof_obj, roof_quads = build_roof(nodes)
        member_objs = build_members(nodes, edges, MEMBER_THICK)

        # 4-8. マテリアル一括適用
        apply_all_materials(node_objs, panel_objs, roof_obj, member_objs)

        # 4-9. アニメーションハンドラ登録（毎フレーム自動で再描画）
        init_animation(panel_objs, roof_obj, roof_quads, member_objs, node_objs)

        log.info("=== Visualization Completed ===")

    except Exception:
        log.exception("Error in main()")
        print("[ERROR] See system console for details.")


# ────────────────────────────────
# 5. 実行エントリポイント
# ────────────────────────────────
if __name__ == "__main__":
    main()
