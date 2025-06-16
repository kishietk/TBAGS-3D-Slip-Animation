# utils/main_utils.py
"""
ファイル名: utils/main_utils.py

責務:
- アプリ全体の主要な工程（シーン初期化、データロード、モデル構築、Blenderオブジェクト生成、マテリアル適用、アニメーション登録）を責任ごとに関数分割して提供。
- main.py/app.py から呼び出される“流れ”を、関数単位で実装。
- 1関数1責任・明確なdocstring付き。
"""

import bpy
from utils.blenderScene_utils import clear_scene
from loaders.loaderManager import LoaderManager
from cores.coreConstructer import coreConstructer
from builders.sceneBuilder import build_blender_objects
from builders.motionParentBuilder import build_motion_parent, set_parent
from builders.materials import apply_all_materials
from animators.ground_animator import register_ground_anim_handler
from animators.building_animator import on_frame_building
from loaders.earthquakeAnimLoader import load_earthquake_motion_csv
from configs import (
    ANIM_FPS,
    ANIM_SECONDS,
    SANDBAG_NODE_KIND_IDS,
    EARTHQUAKE_ANIM_CSV,
    log_dataset_selection,
)
import argparse
from utils.logging_utils import setup_logging

log = setup_logging("main_utils")


def parse_args():
    """
    役割:
        コマンドライン引数（地震データセット指定など）をパースして返す。
    引数:
        なし
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


def get_dataset_from_args(args, datasets_dict):
    """
    役割:
        引数の'dataset'が辞書に存在すれば該当データセット辞書を返す。なければValueErrorを投げる。
    引数:
        args: argparseで取得したNamespace
        datasets_dict: データセットの辞書（paths.EARTHQUAKE_DATASETSなど）
    返り値:
        dict: 指定データセットの内容
    例外:
        ValueError: データセット名が不正な場合
    """
    if args.dataset not in datasets_dict:
        raise ValueError(f"指定データセットが存在しません: {args.dataset}")
    return datasets_dict[args.dataset]


def setup_scene():
    """
    役割:
        Blenderシーンの初期化とアニメーション設定（FPS・フレーム範囲）。
    引数:
        なし
    返り値:
        なし
    """
    clear_scene()
    scene = bpy.context.scene
    scene.render.fps = ANIM_FPS
    scene.frame_start = 1
    scene.frame_end = ANIM_FPS * ANIM_SECONDS


def load_all_data(node_csv, edges_file, node_anim_csv, earthquake_anim_csv):
    """
    役割:
        必要な全データ（ノード、エッジ、アニメーション、地震基準面）を指定パスでロードする。
    引数:
        node_csv (str): ノードデータファイルパス
        edges_file (str): エッジデータファイルパス
        node_anim_csv (str): ノードアニメーションCSVパス
        earthquake_anim_csv (str): 地震アニメーションCSVパス
    返り値:
        nodes_data, edges_data, anim_data, eq_motion_data
    """
    loader = LoaderManager(
        node_path=node_csv,
        edge_path=edges_file,
        node_anim_path=node_anim_csv,
        earthquake_anim_path=earthquake_anim_csv,
    )
    nodes_data = loader.load_nodes()
    edges_data = loader.load_edges(nodes_data)
    anim_data = loader.load_animation()
    eq_anim_data = loader.load_earthquake_motion()

    return nodes_data, edges_data, anim_data, eq_anim_data


def build_core_model(nodes_data, edges_data):
    """
    役割:
        コアモデル(coreConstructer)を構築する。
    引数:
        nodes_data: ノード情報（辞書）
        edges_data: エッジ情報（リスト）
    返り値:
        coreConstructerインスタンス
    """
    return coreConstructer(nodes_data, edges_data)


def build_blender_objects_from_core(core):
    """
    役割:
        コアモデルからBlender用のオブジェクト群を一括生成する。
    引数:
        core: coreConstructerインスタンス
    返り値:
        node_objs, sandbag_objs, panel_objs, roof_obj, roof_quads, member_objs, ground_obj
    """
    return build_blender_objects(
        nodes=core.get_nodes(),
        column_edges=core.get_columns(),
        beam_edges=core.get_beams(),
        panels=core.get_panels(),
    )


def apply_materials_to_all(blender_objs):
    """
    役割:
        すべてのBlenderオブジェクトにマテリアルを一括適用する。
    引数:
        blender_objs: 各種オブジェクト群（タプル等）
    返り値:
        なし
    """
    node_objs, sandbag_objs, panel_objs, roof_obj, _, member_objs, ground_obj = (
        blender_objs
    )
    apply_all_materials(
        node_objs=node_objs,
        sandbag_objs=sandbag_objs,
        panel_objs=panel_objs,
        roof_obj=roof_obj,
        member_objs=member_objs,
        ground_obj=ground_obj,
    )


def setup_animation_handlers(
    core,
    anim_data,
    blender_objs,
    earthquake_anim_data=load_earthquake_motion_csv(EARTHQUAKE_ANIM_CSV),
):
    """
    役割:
        アニメーションハンドラをセットアップする（建物・地面のアニメイベントを登録）。
    引数:
        core: coreConstructerインスタンス
        anim_data: アニメーションデータ
        blender_objs: 各種オブジェクト群（タプル等）
    返り値:
        なし
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

    # モーション親
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

    # ノード種別分け
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

    # ハンドラクリア＆再登録
    bpy.app.handlers.frame_change_pre.clear()

    # 地面モーション（建物全体揺れ）
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
