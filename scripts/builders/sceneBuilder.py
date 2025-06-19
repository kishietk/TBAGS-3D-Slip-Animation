# builders/sceneBuilder.py

"""
ファイル名: builders/sceneBuilder.py

責務:
- コアモデル(Node/SandbagNode/Panel…)からBlender用表示オブジェクト群を一括生成。
- kind_idで通常ノード／サンドバッグを自動仕分けし、各ビルダーに分派。
- 生成物（球体／“工”字サンドバッグユニット／パネル／屋根／柱／梁／地面）を返却。

注意:
- メンバー（columns/beams）には column_edges, beam_edges を使用。
- ノードは dict or list の両方を受け取る。
"""

from typing import List, Dict, Tuple, Any, Optional, Union
import bpy
from utils.logging_utils import setup_logging

from builders.nodes import build_nodes
from cores.sandbagUnit import pair_sandbag_nodes
from builders.sandbagUnitsBuilder import build_sandbag_units
from builders.panels import build_blender_panels, build_roof
from builders.columns import build_columns
from builders.beams import build_beams
from builders.groundBuilder import build_ground_plane

from configs import (
    SANDBAG_NODE_KIND_IDS,
    SPHERE_RADIUS,
    SANDBAG_FACE_SIZE,
    SANDBAG_BAR_THICKNESS,
)

log = setup_logging("sceneBuilder")


def build_blender_objects(
    nodes: Union[Dict[int, Any], List[Any]],
    column_edges: List[Tuple[int, int]],
    beam_edges: List[Tuple[int, int]],
    panels: Optional[List[Any]] = None,
    sandbag_face_size: Tuple[float, float] = SANDBAG_FACE_SIZE,
    sandbag_bar_thickness: float = SANDBAG_BAR_THICKNESS,
    node_sphere_radius: float = SPHERE_RADIUS,
    include_ground: bool = True,
) -> Tuple[
    Dict[int, bpy.types.Object],  # node_objs
    Dict[int, bpy.types.Object],  # sandbag_unit_objs
    List[bpy.types.Object],  # panel_objs
    Optional[bpy.types.Object],  # roof_obj
    List[Tuple[int, int, int, int]],  # roof_quads
    List[Tuple[bpy.types.Object, int, int]],  # member_objs
    Optional[bpy.types.Object],  # ground_obj
]:
    """
    nodes: dict or list of core Node/SandbagNode objects
    column_edges: list of (start_id, end_id)
    beam_edges:   list of (start_id, end_id)
    panels:       list of core Panel objects

    returns:
        node_objs, sandbag_unit_objs, panel_objs, roof_obj,
        roof_quads, member_objs, ground_obj
    """
    log.info("=================[Blenderオブジェクトを構築]=========================")

    # nodes が dict なら .values()、list ならそのままイテレート
    iterable = nodes.values() if isinstance(nodes, dict) else nodes

    # kind_id で通常ノード／サンドバッグノードを分離
    sandbag_nodes: Dict[int, Any] = {}
    normal_nodes: Dict[int, Any] = {}
    for n in iterable:
        kind = getattr(n, "kind_id", None)
        if kind == 0 or kind in SANDBAG_NODE_KIND_IDS:
            sandbag_nodes[n.id] = n
        else:
            normal_nodes[n.id] = n

    # 1) 通常ノード球体生成
    node_objs = (
        build_nodes(normal_nodes, radius=node_sphere_radius) if normal_nodes else {}
    )

    # 2) サンドバッグUnit (“工”字形) 生成
    # nodes dict が必要な形なら整形
    node_dict = nodes if isinstance(nodes, dict) else {n.id: n for n in nodes}
    units = pair_sandbag_nodes(node_dict)
    sandbag_objs = build_sandbag_units(units) if units else {}

    # 3) パネル生成
    panel_objs = build_blender_panels(panels) if panels else []

    # 4) 屋根生成
    # 全ノード位置辞書を組み合わせ
    all_pos = {
        **{nid: n.pos for nid, n in normal_nodes.items()},
        **{nid: n.pos for nid, n in sandbag_nodes.items()},
    }
    roof_obj, roof_quads = build_roof(all_pos)

    # 5) 柱・梁生成
    column_objs = build_columns(all_pos, set(column_edges), thickness=0.5)
    beam_objs = build_beams(all_pos, set(beam_edges), thickness=0.5)
    member_objs = list(column_objs) + list(beam_objs)

    # 6) 地面生成
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
