# utils/main_utils.py

"""
ファイル名: utils/main_utils.py

責務:
- アプリ全体の主要な工程（シーン初期化、データロード、モデル構築、Blenderオブジェクト生成、マテリアル適用、アニメーション登録）を責任ごとに関数分割して提供。
- main.py/app.py から呼び出される“流れ”を、関数単位で実装。
- 1関数1責任・明確なdocstring付き。
"""

import bpy
import argparse
from typing import Tuple, Dict, List, Any, Optional

from .blender_scene_utils import clear_scene
from loaders import LoaderManager
from cores.constructors.core_factory import CoreFactory
from builders.scene_builders.scene_builder import SceneBuilder
from builders.hierarchy_builders.motion_parent_builder import (
    build_motion_parent,
    set_parent,
)
from builders.material_builders import apply_all_materials
from animators import register_ground_anim_handler, on_frame_building
from loaders import load_earthquake_motion_csv
from configs import (
    ANIM_FPS,
    ANIM_SECONDS,
    SANDBAG_NODE_KIND_IDS,
    EARTHQUAKE_ANIM_CSV,
    log_dataset_selection,
)
from utils import setup_logging

log = setup_logging("main_utils")


def parse_args() -> argparse.Namespace:
    """
    役割:
        コマンドライン引数（地震データセット指定など）をパースして返す。
    返り値:
        argparse.Namespace（引数の値を持つオブジェクト）
    """
    log.info("=================[データリストを決定]=========================")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=str,
        default="kumamoto_with_tbags",
        help="地震データセット名を指定（例: kumamoto_with_tbags）",
    )
    args = parser.parse_args()
    log.info(f"{log_dataset_selection(args.dataset)}")
    return args


def get_dataset_from_args(
    args: argparse.Namespace,
    datasets_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """
    役割:
        引数の 'dataset' が辞書に存在すれば該当データセット辞書を返す。なければ ValueError を投げる。
    引数:
        args: argparse で取得した Namespace
        datasets_dict: データセットの辞書（paths.EARTHQUAKE_DATASETS など）
    返り値:
        dict: 指定データセットの内容
    例外:
        ValueError: データセット名が不正な場合
    """
    if args.dataset not in datasets_dict:
        raise ValueError(f"指定データセットが存在しません: {args.dataset}")
    return datasets_dict[args.dataset]


def setup_scene() -> None:
    """
    役割:
        Blender シーンの初期化とアニメーション設定（FPS・フレーム範囲）。
    """
    clear_scene()
    scene = bpy.context.scene
    scene.render.fps = ANIM_FPS
    scene.frame_start = 1
    scene.frame_end = ANIM_FPS * ANIM_SECONDS


def load_all_data(
    node_csv: str,
    node_anim_csv: str,
    earthquake_anim_csv: str,
) -> Tuple[Dict[int, Any], List[Tuple[int, int]], Dict[int, Any], Any]:
    """
    役割:
        必要な全データ（ノード、エッジ、アニメーション、地震基準面）を指定パスでロードする。
    返り値:
        nodes_data, edges_data, anim_data, eq_motion_data
    """
    loader = LoaderManager(
        node_path=node_csv,
        node_anim_path=node_anim_csv,
        earthquake_anim_path=earthquake_anim_csv,
    )
    nodes_data, edges_data = loader.load_structure()
    anim_data = loader.load_animation()
    eq_anim_data = loader.load_earthquake_motion()
    return nodes_data, edges_data, anim_data, eq_anim_data


def build_core_model(
    nodes_data: Dict[int, Any],
    edges_data: List[Tuple[int, int]],
) -> CoreFactory:
    """
    役割:
        コアモデル(CoreFactory)を構築する。
    返り値:
        CoreFactory インスタンス
    """
    return CoreFactory(nodes_data, edges_data)


def build_blender_objects_from_core(
    core: CoreFactory,
) -> Tuple[
    Dict[int, bpy.types.Object],  # node_objs
    Dict[int, bpy.types.Object],  # sandbag_unit_objs
    List[bpy.types.Object],  # panel_objs
    Optional[bpy.types.Object],  # roof_obj
    List[Tuple[int, int, int, int]],  # roof_quads
    List[bpy.types.Object],  # member_objs
    Optional[bpy.types.Object],  # ground_obj
]:
    """
    役割:
        コアモデルから Blender 用のオブジェクト群を一括生成する。
    返り値:
        node_objs, sandbag_unit_objs, panel_objs, roof_obj, roof_quads, member_objs, ground_obj
    """
    builder = SceneBuilder(
        nodes=core.get_nodes(),
        column_edges=core.get_columns(),
        beam_edges=core.get_beams(),
        panels=core.get_panels(),
        # その他オプションは SceneBuilder のデフォルトを利用
    )
    return builder.run()


def apply_materials_to_all(
    blender_objs: Tuple[
        Dict[int, bpy.types.Object],
        Dict[int, bpy.types.Object],
        List[bpy.types.Object],
        Optional[bpy.types.Object],
        List[Tuple[int, int, int, int]],
        List[bpy.types.Object],
        Optional[bpy.types.Object],
    ],
) -> None:
    """
    役割:
        すべての Blender オブジェクトにマテリアルを一括適用する。
    """
    (
        node_objs,
        sandbag_objs,
        panel_objs,
        roof_obj,
        _,
        member_objs,
        ground_obj,
    ) = blender_objs

    apply_all_materials(
        node_objs=node_objs,
        sandbag_objs=sandbag_objs,
        panel_objs=panel_objs,
        roof_obj=roof_obj,
        member_objs=member_objs,
        ground_obj=ground_obj,
    )


def setup_animation_handlers(
    core: CoreFactory,
    anim_data: Dict[int, Any],
    blender_objs: Tuple[
        Dict[int, bpy.types.Object],
        Dict[int, bpy.types.Object],
        List[bpy.types.Object],
        Optional[bpy.types.Object],
        List[Tuple[int, int, int, int]],
        List[bpy.types.Object],
        Optional[bpy.types.Object],
    ],
    earthquake_anim_data: Any = load_earthquake_motion_csv(EARTHQUAKE_ANIM_CSV),
) -> None:
    """
    役割:
        アニメーションハンドラをセットアップする（建物・地面のアニメイベントを登録）。
    """
    (
        node_objs,
        sandbag_objs,
        panel_objs,
        roof_obj,
        roof_quads,
        member_objs,
        ground_obj,
    ) = blender_objs

    # モーション親オブジェクト生成＆親子付け
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

    # ノード種別ごとにアニメーションデータを分割
    nodes = core.get_nodes()
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
    node_anim_data = {nid: v for nid, v in anim_data.items() if nid in base_node_pos}

    # フレームチェンジハンドラをクリア＆再登録
    bpy.app.handlers.frame_change_pre.clear()

    # 地面アニメーションハンドラ
    register_ground_anim_handler(
        motion_parent=motion_parent,
        earthquake_anim_data=earthquake_anim_data,
    )

    # 建物部材アニメーション
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
