import bpy
import bmesh
from typing import List, Tuple, Dict, Any, Optional
from mathutils import Vector
from configs import UV_MAP_NAME


def update_roof(
    roof_obj: Optional[bpy.types.Object],
    roof_quads: List[Tuple[int, int, int, int]],
    node_objs: Dict[int, bpy.types.Object],
    scene: bpy.types.Scene,
) -> None:
    """
    屋根メッシュを更新する。
    """
    if not (roof_obj and roof_quads):
        return
    frame = scene.frame_current
    mesh = roof_obj.data
    mesh.clear_geometry()
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new(UV_MAP_NAME)
    vert_map: Dict[int, bmesh.types.BMVert] = {}
    for quad in roof_quads:
        for nid in quad:
            pos = node_objs[nid].location
            if nid not in vert_map:
                vert_map[nid] = bm.verts.new(pos)
    for bl, br, tr, tl in roof_quads:
        f = bm.faces.new([vert_map[n] for n in (bl, br, tr, tl)])
        for loop, uv in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            loop[uv_layer].uv = uv
    bm.to_mesh(mesh)
    bm.free()
