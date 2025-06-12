"""
main.py

Blender可視化プロジェクトのエントリーポイント
- シーン初期化からデータロード、部材・地面生成、マテリアル割り当て
  地面アニメーション・建物アニメーション（全体＋部材個別）両方のハンドラ登録まで一括管理

設計方針:
- 地面も建物も別々にアニメーションできる設計
- ground/animators/core/builder群とのインターフェース一貫
- 例外処理・ロギング充実
"""

import sys
import os

CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)


def main() -> None:
    from utils.logging_utils import setup_logging

    log = setup_logging("main")
    log.info("=== Start Visualization ===")

    try:
        # 1. シーン初期化
        from utils.scene_utils import clear_scene

        clear_scene()
        log.info("Scene cleared.")

        import bpy
        from loaders.loaderManager import LoaderManager
        from cores.coreConstructer import coreConstructer
        from builders.sceneBuilder import build_blender_objects
        from configs import SANDBAG_NODE_KIND_IDS, EARTHQUAKE_ANIM_CSV
        from builders.motionParentBuilder import build_motion_parent, set_parent
        from builders.materials import apply_all_materials
        from animators.ground_animator import register_ground_anim_handler
        from animators.building_animator import on_frame_building
        from loaders.earthquakeAnimLoader import load_earthquake_motion_csv

        # 2. データロード
        loader = LoaderManager()
        nodes_data = loader.load_nodes()
        edges_data = loader.load_edges(nodes_data)
        anim_data = loader.load_animation()
        log.info("Core data loaded.")

        # 3. コアモデル構築

        cc = coreConstructer(nodes_data, edges_data)
        log.info(f"Core summary: {cc.summary()}")

        # 4. Blenderオブジェクト生成

        (
            node_objs,
            sandbag_objs,
            panel_objs,
            roof_obj,
            roof_quads,
            member_objs,
            ground_obj,
        ) = build_blender_objects(
            nodes=cc.get_nodes(),
            column_edges=cc.get_columns(),
            beam_edges=cc.get_beams(),
            panels=cc.get_panels(),
        )

        motion_parent = build_motion_parent()
        set_parent(
            motion_parent,
            node_objs=node_objs,
            sandbag_objs=sandbag_objs,
            panel_objs=panel_objs,
            roof_obj=roof_obj,
            member_objs=member_objs,
            ground_obj=ground_obj,
        )

        # 7. マテリアル一括適用（グラウンドも含めてOK）
        apply_all_materials(
            node_objs=node_objs,
            sandbag_objs=sandbag_objs,
            panel_objs=panel_objs,
            roof_obj=roof_obj,
            member_objs=member_objs,
            ground_obj=ground_obj,
        )

        # 8. 地震アニメーションデータ読込
        earthquake_anim_data = load_earthquake_motion_csv(EARTHQUAKE_ANIM_CSV)

        # 9. アニメーションハンドラ登録

        # サンドバッグ/通常ノードでID分割
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

        # 既存のframe_change_preハンドラはクリアしておく（複数登録防止）
        bpy.app.handlers.frame_change_pre.clear()

        # motion_parentによる建物全体揺れ
        register_ground_anim_handler(
            motion_parent=motion_parent,
            earthquake_anim_data=earthquake_anim_data,
        )

        # 建物部材個別の再配置・再構築アニメ
        def _on_frame_building(scene):
            on_frame_building(
                scene,
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
            )

        bpy.app.handlers.frame_change_pre.append(_on_frame_building)
        log.info("=== Visualization Completed ===")

    except Exception as e:
        log.error("Error in main()")
        import traceback

        log.error(traceback.format_exc())
        print("[ERROR] See system console for details.")


if __name__ == "__main__":
    main()
