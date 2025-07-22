import bpy
import argparse
from typing import Tuple, Dict, List, Any, Optional

from utils import clear_scene, setup_logging
from loaders.loader_manager import LoaderManager
from cores.factory import CoreFactory
from builders.scene_builder import SceneBuilder
from builders.hierarchy_builders.motion_parent_builder import (
    build_motion_parent,
    set_parent,
)
from builders.material_builders import apply_all_materials
from animators import register_ground_anim_handler, on_frame_building
from configs import (
    ANIM_FPS,
    ANIM_SECONDS,
    EARTHQUAKE_ANIM_CSV,
    log_dataset_selection,
    GROUND_ANIMATION_ENABLED,
)
from cores import NodeData, EdgeData

log = setup_logging("main_utils")


def parse_args() -> argparse.Namespace:
    """
    コマンドライン引数（地震データセット指定など）をパースして返す。
    """
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
    引数の 'dataset' が辞書に存在すれば該当データセット辞書を返す。
    """
    if args.dataset not in datasets_dict:
        raise ValueError(f"指定データセットが存在しません: {args.dataset}")
    return datasets_dict[args.dataset]


def setup_scene() -> None:
    """
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
) -> Tuple[Dict[int, NodeData], List[EdgeData], Dict[int, Any], Any]:
    """
    必要な全データ（ノード、エッジ、アニメーション、地震基準面）を
    指定パスでロードする。
    """
    loader = LoaderManager()
    nodes_data, edges_data = loader.load_structure(node_csv)
    anim_data = loader.load_animation(node_anim_csv)
    eq_anim_data = loader.load_earthquake_motion(earthquake_anim_csv)
    return nodes_data, edges_data, anim_data, eq_anim_data


def build_core_model(
    nodes_data: Dict[int, NodeData],
    edges_data: List[EdgeData],
) -> CoreFactory:
    """
    コアモデル(CoreFactory)を構築する。
    """
    return CoreFactory(nodes_data, edges_data)


def build_blender_objects_from_core(
    core: CoreFactory,
) -> Tuple[
    Dict[int, bpy.types.Object],
    List[bpy.types.Object],
    Optional[bpy.types.Object],
    List[Tuple[int, int, int, int]],
    List[bpy.types.Object],
    Optional[bpy.types.Object],
]:
    """
    コアモデルから Blender 用のオブジェクト群を一括生成する。
    """
    builder = SceneBuilder(core, include_ground=True)
    return builder.build()


def apply_materials_to_all(
    blender_objs: Tuple[
        Dict[int, bpy.types.Object],
        List[bpy.types.Object],
        Optional[bpy.types.Object],
        List[Tuple[int, int, int, int]],
        List[bpy.types.Object],
        Optional[bpy.types.Object],
    ],
) -> None:
    """
    すべての Blender オブジェクトにマテリアルを一括適用する。
    """
    node_objs, panel_objs, roof_obj, roof_quads, member_objs, ground_obj = blender_objs
    apply_all_materials(
        node_objs=node_objs,
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
        List[bpy.types.Object],
        Optional[bpy.types.Object],
        List[Tuple[int, int, int, int]],
        List[bpy.types.Object],
        Optional[bpy.types.Object],
    ],
    earthquake_anim_data: Any,
) -> None:
    """
    アニメーションハンドラをセットアップする。
    """
    node_objs, panel_objs, roof_obj, roof_quads, member_objs, ground_obj = blender_objs

    # モーション親オブジェクト生成 & 親子付け
    motion_parent = build_motion_parent()
    set_parent(
        motion_parent,
        node_objs=node_objs,
        panel_objs=panel_objs,
        roof_obj=roof_obj,
        member_objs=member_objs,
        ground_obj=ground_obj,
    )

    # ベースノードポジション取得
    base_node_pos = {n.id: n.pos for n in core._nodes.values()}
    node_anim_data = {nid: v for nid, v in anim_data.items() if nid in base_node_pos}

    # フレームチェンジハンドラをクリア
    bpy.app.handlers.frame_change_pre.clear()

    # 地面アニメーション
    if GROUND_ANIMATION_ENABLED:
        register_ground_anim_handler(
            motion_parent=motion_parent,
            earthquake_anim_data=earthquake_anim_data,
            enabled=GROUND_ANIMATION_ENABLED,
        )

    # 建物アニメーションハンドラ
    def _on_frame_building(scene):
        on_frame_building(
            scene,
            panel_objs=panel_objs,
            roof_obj=roof_obj,
            roof_quads=roof_quads,
            member_objs=member_objs,
            node_objs=node_objs,
            anim_data=node_anim_data,
            base_node_pos=base_node_pos,
        )

    bpy.app.handlers.frame_change_pre.append(_on_frame_building)
