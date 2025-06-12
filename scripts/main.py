"""
main.py

Blender可視化プロジェクトのエントリーポイント
- シーン初期化からデータロード、地面・建物生成、マテリアル割り当て、アニメーションハンドラ登録まで一括管理

設計方針:
- 各工程の責務を関数単位で明確化
- ground/animators/core/builder群とのインターフェース一貫
- 例外処理・ロギング充実
"""

import sys
import os

# プロジェクトルートをimportパスに追加
CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)


def main() -> None:
    """
    全ビジュアライゼーション処理の統括
    """
    from utils.logging_utils import setup_logging

    log = setup_logging("main")
    log.info("=== Start Visualization ===")

    try:
        # 1. シーン初期化
        from utils.scene_utils import clear_scene

        clear_scene()
        log.info("Scene cleared.")

        # 2. データロード（LoaderManager利用）
        from loaders.loaderManager import LoaderManager

        loader = LoaderManager()
        nodes_data = loader.load_nodes()
        edges_data = loader.load_edges(nodes_data)
        anim_data = loader.load_animation()
        log.info("Core data loaded.")

        # 3. コアモデル構築
        from cores.coreConstructer import coreConstructer

        cc = coreConstructer(nodes_data, edges_data)
        log.info(f"Core summary: {cc.summary()}")

        # 4. Blenderオブジェクト生成（build_blender_objects）
        from builders.sceneBuilder import build_blender_objects

        node_objs, sandbag_objs, panel_objs, roof_obj, roof_quads, member_objs = (
            build_blender_objects(
                nodes=cc.get_nodes(),
                column_edges=cc.get_columns(),
                beam_edges=cc.get_beams(),
                panels=cc.get_panels(),
            )
        )
        log.info("Blender objects created.")

        # --- サンドバッグ/通常ノードでID分割 ---
        from config import SANDBAG_NODE_KIND_IDS, EARTHQUAKE_ANIM_CSV

        nodes = cc.get_nodes()
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

        # 5. 地面（Ground）生成＆コア管理
        from cores.groundCore import Ground
        from builders.groundBuilder import build_ground_plane, set_building_parent

        ground_core = Ground(size=30.0)
        ground_obj = build_ground_plane(size=ground_core.size)
        ground_core.set_blender_object(ground_obj)
        log.info("Ground plane created.")

        # 6. 建物を地面の子にまとめる
        set_building_parent(
            ground_obj, node_objs, sandbag_objs, panel_objs, roof_obj, member_objs
        )
        log.info("Building objects set as children of the ground.")

        # 7. マテリアル一括適用
        from builders.materials import apply_all_materials

        apply_all_materials(
            node_objs=node_objs,
            sandbag_objs=sandbag_objs,
            panel_objs=panel_objs,
            roof_obj=roof_obj,
            member_objs=member_objs,
        )
        log.info("Materials applied.")

        # 8. 地震アニメーションデータ読込
        from loaders.earthquakeAnimLoader import load_earthquake_motion_csv

        earthquake_anim_data = load_earthquake_motion_csv(EARTHQUAKE_ANIM_CSV)
        log.info(
            f"earthquake_anim_data sample: {list(earthquake_anim_data.items())[:10]}"
        )

        # 9. アニメーションイベントハンドラ統合登録
        from animators.handler import register_animation_handler

        register_animation_handler(
            panel_objs=panel_objs,
            roof_obj=roof_obj,
            roof_quads=roof_quads,
            member_objs=member_objs,
            node_objs=node_objs,
            sandbag_objs=sandbag_objs,
            anim_data=node_anim_data,
            sandbag_anim_data=sandbag_anim_data,
            base_node_pos=base_node_pos,
            base_sandbag_pos=base_sandbag_pos,
            ground_obj=ground_obj,
            earthquake_anim_data=earthquake_anim_data,
        )
        log.info("Animation handler registered.")

        log.info("=== Visualization Completed ===")

    except Exception as e:
        log.error("Error in main()")
        import traceback

        log.error(traceback.format_exc())
        print("[ERROR] See system console for details.")


if __name__ == "__main__":
    main()
