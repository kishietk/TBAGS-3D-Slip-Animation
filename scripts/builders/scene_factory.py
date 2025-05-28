# シーンオブジェクト統合ビルダー
# コアデータからBlender用の全オブジェクトを生成する

from builders.nodes import build_nodes, create_node_labels
from builders.panels import build_blender_panels, build_roof
from builders.columns import build_columns
from builders.beams import build_beams


def create_blender_objects(
    nodes,
    column_edges,
    beam_edges,
    anim_data,
    panels=None,  # 追加（コアPanelリスト）
):
    """
    コアデータからBlender用の全オブジェクトを生成する
    引数:
        nodes: List[Node] または Dict[int, Node]
        column_edges: 柱となるノードIDペアのリスト
        beam_edges: 梁となるノードIDペアのリスト
        anim_data: ノードID→{フレーム: 変位Vector}の辞書
    戻り値:
        (node_objs, panel_objs, roof_obj, roof_quads, member_objs)
            node_objs: ノードID→Blenderオブジェクトの辞書
            panel_objs: パネルオブジェクトのリスト
            roof_obj: 屋根オブジェクト
            roof_quads: 屋根パネルIDタプルリスト
            member_objs: (オブジェクト, ノードAのID, ノードBのID)のリスト
    """
    # ノードが辞書形式の場合はリストに変換
    if isinstance(nodes, dict):
        node_list = list(nodes.values())
    else:
        node_list = list(nodes)
    node_pos = {n.id: n.pos for n in node_list}
    # ノード球生成
    node_objs = build_nodes(node_pos, radius=0.05, anim_data=anim_data)
    # ノードラベル生成
    create_node_labels(node_pos, radius=0.05)
    # === パネル生成：コアデータのPanelリストから生成 ===
    if panels is not None:
        panel_objs = build_blender_panels(panels)
    else:
        # fallback: geometryから抽出
        panel_objs = []

    # 屋根生成
    roof_obj, roof_quads = build_roof(node_pos)
    # 柱・梁生成
    column_objs = build_columns(node_pos, set(column_edges), thickness=0.5)
    beam_objs = build_beams(node_pos, set(beam_edges), thickness=0.5)
    member_objs = list(column_objs) + list(beam_objs)
    return node_objs, panel_objs, roof_obj, roof_quads, member_objs
