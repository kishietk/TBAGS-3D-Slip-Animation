from builders.nodes import build_nodes, create_node_labels
from builders.panels import build_panels, build_roof
from builders.columns import build_columns
from builders.beams import build_beams


def create_blender_objects(nodes, column_edges, beam_edges, anim_data):
    """Blender用の全オブジェクトを生成"""
    node_pos = {n.id: n.pos for n in nodes}
    node_objs = build_nodes(node_pos, radius=0.05, anim_data=anim_data)
    create_node_labels(node_pos, radius=0.05)
    panel_objs = build_panels(node_pos, set(column_edges + beam_edges))
    roof_obj, roof_quads = build_roof(node_pos)
    column_objs = build_columns(node_pos, set(column_edges), thickness=0.5)
    beam_objs = build_beams(node_pos, set(beam_edges), thickness=0.5)
    member_objs = list(column_objs) + list(beam_objs)
    return node_objs, panel_objs, roof_obj, roof_quads, member_objs
