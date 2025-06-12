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
from mathutils import Vector

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

        # 2. データロード
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

        # 4. Blenderオブジェクト生成（groundも含めて一括）
        from builders.sceneBuilder import build_blender_objects

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
        log.info("Blender objects created (including ground).")

        # サンドバッグ/通常ノードでID分割
        from configs import SANDBAG_NODE_KIND_IDS, EARTHQUAKE_ANIM_CSV, EARTHQUAKE_ANIM_CSV

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

        # 5. グラウンドコア管理
        from cores.groundCore import Ground

        ground_core = Ground()
        ground_core.set_blender_object(ground_obj)
        log.info("Ground plane created and registered.")

        # 6. 地震アニメ親（Empty）生成＋親子付け
        from builders.motionParentBuilder import build_motion_parent, set_parent

        motion_parent = build_motion_parent()
        set_parent(
            motion_parent,
            node_objs=node_objs,
            sandbag_objs=sandbag_objs,
            panel_objs=panel_objs,
            roof_obj=roof_obj,
            member_objs=member_objs,
        )
        log.info("Building objects parented to motion parent.")

        # 7. マテリアル一括適用（グラウンドも含めてOK）
        from builders.materials import apply_all_materials

        apply_all_materials(
            node_objs=node_objs,
            sandbag_objs=sandbag_objs,
            panel_objs=panel_objs,
            roof_obj=roof_obj,
            member_objs=member_objs,
            ground_obj=ground_obj,
        )
        log.info("Materials applied.")

        # 8. 地震アニメーションデータ読込（地面用/建物用で個別データを準備）
        from loaders.earthquakeAnimLoader import load_earthquake_motion_csv

        earthquake_anim_data = load_earthquake_motion_csv(
            EARTHQUAKE_ANIM_CSV
        )  # 建物揺れ用
        ground_anim_data = load_earthquake_motion_csv(EARTHQUAKE_ANIM_CSV)  # 地面揺れ用
        log.info(
            f"earthquake_anim_data sample: {list(earthquake_anim_data.items())[:10]}"
        )
        log.info(f"ground_anim_data sample: {list(ground_anim_data.items())[:10]}")

        # 9. アニメーションハンドラ登録（地面・建物とも分離管理！）
        import bpy
        from animators.ground_animator import (
            register_ground_anim_handler,
            register_ground_mesh_anim_handler,
        )
        from animators.building_animator import on_frame_building

        # 既存のframe_change_preハンドラはクリアしておく（複数登録防止）
        bpy.app.handlers.frame_change_pre.clear()

        # motion_parentによる建物全体揺れ
        register_ground_anim_handler(
            motion_parent=motion_parent,
            earthquake_anim_data=earthquake_anim_data,
        )
        log.info("Ground (motion parent) animation handler registered.")

        # グラウンドメッシュ単体の揺れ
        register_ground_mesh_anim_handler(
            ground_obj=ground_obj,
            ground_anim_data=ground_anim_data,
        )
        log.info("Ground mesh animation handler registered.")

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
        log.info("Building (individual part) animation handler registered.")

        log.info("=== Visualization Completed ===")

    except Exception as e:
        log.error("Error in main()")
        import traceback

        log.error(traceback.format_exc())
        print("[ERROR] See system console for details.")


if __name__ == "__main__":
    main()
