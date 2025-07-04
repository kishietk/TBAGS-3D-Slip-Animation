import bpy
import bmesh
from typing import List, Tuple, Dict, Any, Optional
from mathutils import Vector
from configs import UV_MAP_NAME


def update_panels(
    panel_objs: List[bpy.types.Object],
    node_objs: Dict[int, bpy.types.Object],
    base_sandbag_pos: Dict[Any, Vector],
    sandbag_anim_data: Dict[int, Dict[int, Vector]],
    scene: bpy.types.Scene,
) -> None:
    """
    パネルメッシュを更新する。
    """
    frame = scene.frame_current
    for obj in panel_objs:
        ids = obj.get("panel_ids")
        if not ids or len(ids) != 4:
            continue
        verts: List[Vector] = []
        for nid in ids:
            if nid in node_objs:
                verts.append(node_objs[nid].location)
            else:
                verts.append(
                    base_sandbag_pos.get(nid, Vector())
                    + sandbag_anim_data.get(nid, {}).get(frame, Vector())
                )
        mesh = obj.data
        mesh.clear_geometry()
        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.new(UV_MAP_NAME)
        vlist = [bm.verts.new(v) for v in verts]
        face = bm.faces.new(vlist)
        for loop, uv in zip(face.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            loop[uv_layer].uv = uv
        bm.to_mesh(mesh)
        bm.free()
