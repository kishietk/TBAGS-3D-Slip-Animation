"""
コアデータからBlender用の全オブジェクトを生成する統合ビルダー

- 通常ノード（球体）、サンドバッグノード（立方体）を種別ごとにビルダー分岐
- すべての生成は「静的オブジェクトのみ」（アニメーション・キーフレームは担当しない）
- 戻り値はapply_all_materialsやアニメーターでそのまま使える

【設計思想】
- コアモデル（Node/SandbagNode/Panel...）→Blender用表示オブジェクト群へ一括変換
- kind_idで通常ノード/サンドバッグ自動仕分け
- 追加ラベル、屋根、部材生成も一元化
"""

from typing import List, Dict, Tuple, Any, Optional
from builders.nodes import build_nodes, create_node_labels
from builders.sandbags import build_sandbags, create_sandbag_labels
from builders.panels import build_blender_panels, build_roof
from builders.columns import build_columns
from builders.beams import build_beams
from config import SANDBAG_NODE_KIND_IDS, SANDBAG_CUBE_SIZE, SPHERE_RADIUS


def build_blender_objects(
    nodes: Dict[int, Any] | List[Any],
    column_edges: List[Tuple[int, int]],
    beam_edges: List[Tuple[int, int]],
    panels: Optional[Any] = None,
    sandbag_cube_size=SANDBAG_CUBE_SIZE,
    node_sphere_radius=SPHERE_RADIUS,
) -> Tuple[
    Dict[int, Any],
    Dict[int, Any],
    List[Any],
    Any,
    List[Tuple[int, int, int, int]],
    List[Any],
]:
    """
    コアデータからBlender用の全オブジェクトを生成する
    kind_idに応じて通常ノード/サンドバッグノードに分離し別ビルダーへ

    Args:
        nodes: ListまたはDict[int, Node/SandbagNode]
        column_edges: 柱エッジリスト (List[Tuple[int, int]])
        beam_edges: 梁エッジリスト (List[Tuple[int, int]])
        panels: Panelリスト（省略可）
        sandbag_cube_size: サンドバッグ立方体一辺の長さ
        node_sphere_radius: 通常ノード球体半径

    Returns:
        node_objs: ノード球 {id: BlenderObject}
        sandbag_objs: サンドバッグ立方体 {id: BlenderObject}
        panel_objs: パネルオブジェクトリスト
        roof_obj: 屋根オブジェクト
        roof_quads: 屋根パネルIDタプルリスト
        member_objs: 柱・梁オブジェクトリスト
    """

    # 1. kind_idで通常ノード/サンドバッグノードに分離
    sandbag_nodes: Dict[int, Any] = {}
    normal_nodes: Dict[int, Any] = {}
    for n in nodes.values() if isinstance(nodes, dict) else nodes:
        kind_id = getattr(n, "kind_id", None)
        if kind_id == 0 or kind_id in SANDBAG_NODE_KIND_IDS:
            sandbag_nodes[n.id] = n
        else:
            normal_nodes[n.id] = n

    # 2. 通常ノード球体生成（静的）
    node_objs = (
        build_nodes(normal_nodes, radius=node_sphere_radius) if normal_nodes else {}
    )

    # 3. サンドバッグ立方体生成（静的）
    sandbag_objs = (
        build_sandbags(sandbag_nodes, cube_size=sandbag_cube_size)
        if sandbag_nodes
        else {}
    )

    # 4. ラベル生成（どちらも個別関数）
    create_node_labels({nid: n.pos for nid, n in normal_nodes.items()})
    create_sandbag_labels({nid: n.pos for nid, n in sandbag_nodes.items()})

    # 5. パネル生成
    panel_objs = build_blender_panels(panels) if panels else []

    # 6. 屋根生成
    all_node_positions = {
        **{nid: n.pos for nid, n in normal_nodes.items()},
        **{nid: n.pos for nid, n in sandbag_nodes.items()},
    }
    roof_obj, roof_quads = build_roof(all_node_positions)

    # 7. 柱・梁生成（全ノード座標を統合して生成）
    column_objs = build_columns(all_node_positions, set(column_edges), thickness=0.5)
    beam_objs = build_beams(all_node_positions, set(beam_edges), thickness=0.5)
    member_objs = list(column_objs) + list(beam_objs)

    return node_objs, sandbag_objs, panel_objs, roof_obj, roof_quads, member_objs
