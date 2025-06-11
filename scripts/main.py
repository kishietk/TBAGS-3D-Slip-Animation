"""
[特徴・設計方針]
- ノード（Node/SandbagNode）種別を型で厳密に分離・一意管理
- 主要データフロー（シーン初期化→データロード→コア構築→Blenderオブジェクト生成→マテリアル適用→アニメーションイベント登録）を整理
- config.pyで特殊ノード種別やパス・定数を一元管理
- モジュール・関数の型ヒント、ドキュメントを明記
"""

import sys
import os

# プロジェクトルートをimportパスに追加
CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)


def main() -> None:
    """
    Blender可視化プロジェクトのエントリーポイント
    - シーン初期化からアニメーション登録までの一連フローを管理
    - ログ出力で進捗・例外を可視化

    Raises:
        すべての例外はcatchし標準エラー出力&ログ記録
    """
    from utils.logging_utils import setup_logging

    log = setup_logging("main")
    log.info("=== Start Visualization ===")

    try:
        # 1. シーン初期化
        from utils.scene_utils import clear_scene

        clear_scene()

        # 2. データロード（LoaderManager）
        from loaders.loaderManager import LoaderManager

        loader = LoaderManager()  # パスはconfigデフォルト
        nodes_data = loader.load_nodes()  # Dict[int, NodeData]
        edges_data = loader.load_edges(nodes_data)  # List[EdgeData]
        anim_data = loader.load_animation()  # Dict[int, Dict[int, Vector]]

        # 3. コアデータ構築（coreConstructer）
        from cores.coreConstructer import coreConstructer

        cc = coreConstructer(nodes_data, edges_data)
        log.info(f"SUMMARY:[[{cc.summary()}]]")

        # 4. Blenderオブジェクト生成
        from builders.sceneBuilder import build_blender_objects

        node_objs, sandbag_objs, panel_objs, roof_obj, roof_quads, member_objs = (
            build_blender_objects(
                nodes=cc.get_nodes(),
                column_edges=cc.get_columns(),
                beam_edges=cc.get_beams(),
                panels=cc.get_panels(),
            )
        )

        # --- サンドバッグとノードでIDを分割 ---
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

        # ===【追加】地面（基準面）生成 ===
        from builders.groundBuilder import build_ground_plane, set_building_parent

        ground_obj = build_ground_plane(size=30.0)

        # ===【追加】建物一式を地面の子にする ===
        set_building_parent(
            ground_obj, node_objs, sandbag_objs, panel_objs, roof_obj, member_objs
        )

        # 5. マテリアル適用
        from builders.materials import apply_all_materials

        apply_all_materials(
            node_objs=node_objs,
            sandbag_objs=sandbag_objs,
            panel_objs=panel_objs,
            roof_obj=roof_obj,
            member_objs=member_objs,
        )

        # ===【追加】地震基準面アニメCSVロード ===
        from loaders.earthquakeAnimLoader import load_earthquake_motion_csv

        earthquake_anim_data = load_earthquake_motion_csv(EARTHQUAKE_ANIM_CSV)
        log.info(
            f"earthquake_anim_data sample: {list(earthquake_anim_data.items())[:10]}"
        )

        # 6. アニメーションイベント登録
        from animators.animator import init_animation

        init_animation(
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
            ground_obj=ground_obj,  # ←地面オブジェクト（必須）
            earthquake_anim_data=earthquake_anim_data,  # ←地震アニメデータ（必須）
        )
        log.info("=== Visualization Completed ===")

    except Exception as e:
        log.error("Error in main()")
        import traceback

        log.error(traceback.format_exc())
        print("[ERROR] See system console for details.")


if __name__ == "__main__":
    main()
