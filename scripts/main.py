import sys
import os
import importlib

# ============================================
# モジュールホットリロード対応（Blender再起動不要）
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

MODULES = [
    "config",
    "utils.logging",
    "utils.column_grouper",
    "loaders.node_loader",
    "loaders.edge_loader",
    "loaders.animation_loader",
    "cores.node",
    "cores.edge",
    "cores.panel",
    "cores.manager",
    "builders.nodes",
    "builders.panels",
    "builders.edges",
    "builders.materials",
    "builders.columns_armature",
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
from utils.logging import setup_logging
from utils.column_grouper import group_columns_by_edges
from cores.manager import CoreManager
from builders.panels import build_panels, build_roof
from builders.edges import build_members
from builders.materials import apply_all_materials
from loaders.animation_loader import load_animation_data
from builders.columns_armature import build_column_with_armature

log = setup_logging()

"""
main.py

【役割 / Purpose】
- データ→構造体→Blenderビルドの全自動一発実行スクリプト
- 「ボーン入り柱」＋従来型の梁・壁・屋根の可視化
- ノード球生成・従来分割柱は省略
"""


def main():
    log.info("=== Start Visualization (BONE COLUMNS ONLY) ===")
    try:
        # --- シーン初期化 ---
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()
        bpy.app.handlers.frame_change_pre.clear()

        # --- データ読込 ---
        cm = CoreManager()
        nodes = cm.get_nodes()
        edges = cm.get_edges()
        panels = cm.get_panels()

        node_dict = {n.id: n.pos for n in nodes}
        print(f"[DEBUG] node_dict sample: {list(node_dict.items())[:5]}")

        # --- アニメーションデータ読込 ---
        anim_data = load_animation_data()
        print(f"[DEBUG] anim_data sample: {list(anim_data.items())[:3]}")

        # --- [A] ボーン入り柱（id=53のみ）---
        pillar_edges = [
            (e.node_a.id, e.node_b.id)
            for e in edges
            if getattr(e, "kind_id", None) == 53
        ]
        pillar_groups = group_columns_by_edges(pillar_edges)
        log.info(f"Building {len(pillar_groups)} column groups (id=53, with bones)")
        bone_col_objs = []
        for group in pillar_groups:
            print(f"[DEBUG] Calling build_column_with_armature for group: {group}")
            col_obj = build_column_with_armature(
                node_ids=group,
                node_positions=node_dict,
                anim_data=anim_data,
                radius=0.2,
                name_prefix="BoneCol",
            )
            if col_obj is not None:
                bone_col_objs.append(col_obj)

        # --- [B] 梁・壁・屋根（従来通り生成）---
        # パネル・屋根
        panel_objs = build_panels(
            node_dict, {(e.node_a.id, e.node_b.id) for e in edges}
        )
        roof_obj, roof_quads = build_roof(node_dict)
        # 梁（柱以外）
        beam_edges = {
            (e.node_a.id, e.node_b.id)
            for e in edges
            if getattr(e, "kind_id", None) != 53
        }
        member_objs = build_members(
            node_dict,
            beam_edges,
            thickness=0.5,
        )

        # --- マテリアル一括適用（ボーン柱・梁・壁・屋根）---
        # ノード球生成・ラベル生成は省略
        # apply_all_materialsは必要に応じて適用範囲調整
        apply_all_materials({}, panel_objs, roof_obj, member_objs)

        log.info("=== Visualization Completed (with Bone Columns) ===")
    except Exception as e:
        log.error("Error in main()")
        import traceback

        log.error(traceback.format_exc())
        print("[ERROR] See system console for details.")


if __name__ == "__main__":
    main()
