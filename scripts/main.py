import bpy
import sys
import os
import importlib
import logging

# ───────────────────────────────
# 1. パス設定：scripts ディレクトリを sys.path に追加
# ───────────────────────────────
project_root = os.path.expanduser("~/Documents/TBAGS-3D-Slip-Animation")
scripts_dir = os.path.join(project_root, "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

# ───────────────────────────────
# 2. ロギング初期化
# ───────────────────────────────
try:
    from logging_utils import setup_logging
    log = setup_logging(logging.INFO)  # INFOレベルで控えめに出力
except Exception:
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("fallback")
    log.warning("Fallback logger initialized.")

# ───────────────────────────────
# 3. モジュール読み込みとリロード（Blender再起動不要）
# ───────────────────────────────
try:
    import config
    import data_loader.node_loader as node_loader
    import data_loader.edge_loader as edge_loader
    import data_loader.animation_loader as anim_loader
    import builder.nodes as nodes_builder
    import builder.panels as panels_builder
    import builder.members as members_builder
    import materials
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

    # 使用関数だけを抽出
    from config import NODE_CSV, EDGES_FILE, SPHERE_RADIUS, MEMBER_THICK
    from data_loader.node_loader import load_nodes
    from data_loader.edge_loader import load_edges
    from builder.nodes import clear_scene, build_nodes, create_node_labels
    from builder.panels import build_panels, build_roof
    from builder.members import build_members
    from materials import apply_all_materials
    from animator import init_animation

except Exception as e:
    log.error(f"Module import error: {e}")
    raise

# ───────────────────────────────
# 4. メイン処理：構造モデルの構築と表示
# ───────────────────────────────
def main():
    log.info("=== Start Visualization ===")
    try:
        # 1. Blender上のオブジェクトをすべて削除
        clear_scene()

        # 2. ノード・エッジデータをファイルから読み込み
        log.info(f"Reading node data from: {NODE_CSV}")
        nodes = load_nodes(NODE_CSV)

        log.info(f"Reading edge data from: {EDGES_FILE}")
        edges = load_edges(EDGES_FILE)

        log.info(f"{len(nodes)} nodes, {len(edges)} edges")

        # 3. 構造ジオメトリの作成
        node_objs = build_nodes(nodes, SPHERE_RADIUS)
        create_node_labels(nodes, SPHERE_RADIUS)
        
        panel_objs = build_panels(nodes, edges)
        roof_obj, roof_quads = build_roof(nodes)
        member_objs = build_members(nodes, edges, MEMBER_THICK)

        # 4. マテリアル適用
        apply_all_materials(node_objs, panel_objs, roof_obj, member_objs)

        # 5. アニメーション登録
        init_animation(panel_objs, roof_obj, roof_quads, member_objs, node_objs)

        log.info("=== Visualization Completed ===")

    except Exception:
        log.exception("Error in main()")
        print("[ERROR] See system console for details.")

# ───────────────────────────────
# 5. 実行
# ───────────────────────────────
main()
