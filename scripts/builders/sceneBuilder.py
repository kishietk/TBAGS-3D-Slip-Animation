"""
ファイル名: builders/sceneBuilder.py

責務:
- コアモデル(Node/SandbagNode/Panel...)からBlender用表示オブジェクト群を一括生成する統合ビルダー。
- kind_idで通常ノード/サンドバッグを自動仕分けし、各ビルダーに分派。
- 生成物（球体/立方体/パネル/屋根/柱/梁/地面）をapply_all_materialsやアニメーター用にそのまま返す。
- ラベル生成・グラウンド生成も一元化。

注意点:
- 全オブジェクトは“静的”生成のみ（アニメ責任は担わない）
- 入力型（Node/SandbagNode/Panel等）の型安全性は今後さらに強化予定
- kind_id仕分けルールが将来的に変わる場合は責務/ロジックも要見直し

TODO:
- オブジェクト返却順序・型の明文化（NamedTuple等で返す設計も視野）
- 部材種別追加時の拡張方針
- グラウンド生成/属性付与の外部化
"""

from typing import List, Dict, Tuple, Any, Optional
from builders.nodes import build_nodes, create_node_labels
from builders.sandbags import build_sandbags, create_sandbag_labels
from builders.panels import build_blender_panels, build_roof
from builders.columns import build_columns
from builders.beams import build_beams
from builders.groundBuilder import build_ground_plane
from configs import SANDBAG_NODE_KIND_IDS, SANDBAG_CUBE_SIZE, SPHERE_RADIUS
from utils.logging_utils import setup_logging


def build_blender_objects(
    nodes: Dict[int, Any] | List[Any],
    column_edges: List[Tuple[int, int]],
    beam_edges: List[Tuple[int, int]],
    panels: Optional[Any] = None,
    sandbag_cube_size=SANDBAG_CUBE_SIZE,
    node_sphere_radius=SPHERE_RADIUS,
    include_ground: bool = True,
) -> Tuple[
    Dict[int, Any],  # node_objs
    Dict[int, Any],  # sandbag_objs
    List[Any],  # panel_objs
    Any,  # roof_obj
    List[Tuple[int, int, int, int]],  # roof_quads
    List[Any],  # member_objs
    Any,  # ground_obj
]:
    """
    役割:
        コアデータからBlender用の全オブジェクトを一括生成し、各ビルダー/部材単位で返却。

    引数:
        nodes: Dict/List[int, Node/SandbagNode]
        column_edges: 柱エッジリスト (List[Tuple[int, int]])
        beam_edges: 梁エッジリスト (List[Tuple[int, int]])
        panels: Panelリスト（省略可）
        sandbag_cube_size: サンドバッグ立方体一辺の長さ
        node_sphere_radius: ノード球体半径
        include_ground: グラウンドも生成・返却するか

    返り値:
        node_objs: ノード球 {id: BlenderObject}
        sandbag_objs: サンドバッグ立方体 {id: BlenderObject}
        panel_objs: パネルオブジェクトリスト
        roof_obj: 屋根オブジェクト
        roof_quads: 屋根パネルIDタプルリスト
        member_objs: 柱・梁オブジェクトリスト
        ground_obj: グラウンドオブジェクト（部材と同列）

    注意:
        - すべて“静的オブジェクト”のみ生成（アニメ・動的処理は非対応）
        - 返却値の型や順序は今後NamedTuple化などで明文化可能
    """

    log = setup_logging("sceneBuilder")
    log.info("=================[Blenderオブジェクトを構築]=========================")

    # kind_idで通常ノード/サンドバッグノードを分離
    sandbag_nodes: Dict[int, Any] = {}
    normal_nodes: Dict[int, Any] = {}
    for n in nodes.values() if isinstance(nodes, dict) else nodes:
        kind_id = getattr(n, "kind_id", None)
        if kind_id == 0 or kind_id in SANDBAG_NODE_KIND_IDS:
            sandbag_nodes[n.id] = n
        else:
            normal_nodes[n.id] = n

    # 通常ノード球体生成（静的）
    node_objs = (
        build_nodes(normal_nodes, radius=node_sphere_radius) if normal_nodes else {}
    )

    # サンドバッグ立方体生成（静的）
    sandbag_objs = (
        build_sandbags(sandbag_nodes, cube_size=sandbag_cube_size)
        if sandbag_nodes
        else {}
    )

    # ラベル生成
    create_node_labels({nid: n.pos for nid, n in normal_nodes.items()})
    create_sandbag_labels({nid: n.pos for nid, n in sandbag_nodes.items()})

    # パネル生成
    panel_objs = build_blender_panels(panels) if panels else []

    # 屋根生成
    all_node_positions = {
        **{nid: n.pos for nid, n in normal_nodes.items()},
        **{nid: n.pos for nid, n in sandbag_nodes.items()},
    }
    roof_obj, roof_quads = build_roof(all_node_positions)

    # 柱・梁生成
    column_objs = build_columns(all_node_positions, set(column_edges), thickness=0.5)
    beam_objs = build_beams(all_node_positions, set(beam_edges), thickness=0.5)
    member_objs = list(column_objs) + list(beam_objs)

    # グラウンド生成
    ground_obj = build_ground_plane() if include_ground else None

    return (
        node_objs,
        sandbag_objs,
        panel_objs,
        roof_obj,
        roof_quads,
        member_objs,
        ground_obj,
    )
