import sys
import os
import importlib

# ============================================
# モジュールホットリロード対応（Blender再起動不要）
# - 開発中はモジュール編集→main.py実行で即反映
# - 必要なファイルはMODULESリストに追加
# ============================================

# プロジェクトのscripts絶対パスをsys.pathに追加（相対import対策）
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

MODULES = [
    "config",
    "logging_utils",
    "loader.node_loader",
    "loader.edge_loader",
    "loader.animation_loader",
    "cores.node",
    "cores.edge",
    "cores.panel",
    "cores.manager",
    "builders.nodes",
    "builders.edges",  # 旧 members
    "builders.panels",
    "builders.materials",
    # 必要があればここに追加
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

# ==========================
# ↓以降は普通にimport＆実装
# ==========================
import bpy
from logging_utils import setup_logging
from cores.manager import CoreManager
from builders.nodes import build_nodes, create_node_labels
from builders.panels import build_panels, build_roof
from builders.edges import build_members  # builders/edges.pyでOK
from builders.materials import apply_all_materials

log = setup_logging()

"""
main.py

【役割 / Purpose】
- データ→構造体→Blenderビルドの全自動一発実行スクリプト（現場運用主力）。
- 各種設定・生成流れを整理し、エラー時も詳細ログ＋トレースバックで記録。
- ホットリロードブロックにより再起動不要＆効率最大化。

【設計方針】
- ビルド順：シーン初期化→データ読込→各種生成→マテリアル適用まで一発。
- animation周りは今はスキップ（将来拡張容易）。
"""


def main():
    log.info("=== Start Visualization (with CoreManager) ===")
    try:
        # --- シーン初期化 ---
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()
        bpy.app.handlers.frame_change_pre.clear()

        # --- コアマネージャーからフィルタ済みデータ取得 ---
        cm = CoreManager()
        nodes = cm.get_nodes()
        edges = cm.get_edges()
        panels = cm.get_panels()

        # --- ノード球生成＋アニメ用データセット（今はanim_data=None） ---
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

        # --- アニメーションハンドラ登録・他処理（未実装、将来用） ---
        # （例：from animator import init_animation ...）

        log.info("=== Visualization Completed ===")
    except Exception as e:
        log.error("Error in main()")
        import traceback

        log.error(traceback.format_exc())
        print("[ERROR] See system console for details.")


if __name__ == "__main__":
    main()
