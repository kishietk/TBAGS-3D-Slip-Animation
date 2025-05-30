# builders/scene_factory.py
"""
コアデータからBlender用の全オブジェクトを生成する統合ビルダー

- 通常ノード（球体）、サンドバッグノード（立方体）を種別ごとにビルダー分岐
- すべての生成は「静的オブジェクトのみ」（アニメーション・キーフレームは担当しない）
- 戻り値はapply_all_materialsやアニメーターでそのまま使える
"""

from builders.nodes import build_nodes, create_node_labels
from builders.sandbags import build_sandbags, create_sandbag_labels
from builders.panels import build_blender_panels, build_roof
from builders.columns import build_columns
from builders.beams import build_beams
from config import SANDBAG_NODE_KIND_IDS, SANDBAG_CUBE_SIZE, SPHERE_RADIUS


def create_blender_objects(
    nodes,  # List[Node/SandbagNode]またはDict[int, Node/SandbagNode]
    column_edges,
    beam_edges,
    anim_data,  # ※静的生成なので使わない。将来拡張用に残しても良い
    panels=None,
    sandbag_cube_size=SANDBAG_CUBE_SIZE,
    node_sphere_radius=SPHERE_RADIUS,
):
    """
    コアデータからBlender用の全オブジェクトを生成する
    kind_idに応じて通常ノード/サンドバッグノードを分離し別ビルダーへ

    引数:
        nodes: ListまたはDict[int, Node/SandbagNode]
        column_edges: 柱エッジリスト
        beam_edges: 梁エッジリスト
        anim_data: ノードID→{フレーム: 変位Vector}の辞書（ここでは使わない）
        panels: Panelリスト
        sandbag_cube_size: サンドバッグ立方体一辺の長さ
        node_sphere_radius: 通常ノード球体半径

    戻り値:
        node_objs: ノード球 {id: BlenderObject}
        sandbag_objs: サンドバッグ立方体 {id: BlenderObject}
        panel_objs: パネルオブジェクトリスト
        roof_obj: 屋根オブジェクト
        roof_quads: 屋根パネルIDタプルリスト
        member_objs: 柱・梁オブジェクトリスト
    """

    # 1. kind_idで通常ノード/サンドバッグノードに分離
    sandbag_nodes = {}
    normal_nodes = {}
    for n in nodes.values() if isinstance(nodes, dict) else nodes:
        kind_id = getattr(n, "kind_id", None)
        # kind_id=0はサンドバッグでもあるし、柱・梁にもなる
        if kind_id == 0:
            sandbag_nodes[n.id] = n
            normal_nodes[n.id] = n  # ★両方に入れる
        elif kind_id in SANDBAG_NODE_KIND_IDS:
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
