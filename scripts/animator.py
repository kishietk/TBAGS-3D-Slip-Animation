import bpy
import bmesh
from typing import List, Tuple
from mathutils import Vector, Quaternion


def on_frame(
    scene: bpy.types.Scene,
    panel_objs: list[bpy.types.Object],
    roof_obj: bpy.types.Object | None,
    roof_quads: list[tuple[int, int, int, int]],
    member_objs: list[tuple[bpy.types.Object, int, int]],
    node_objs: dict[int, bpy.types.Object],
) -> None:
    """
    毎フレーム呼び出され、壁パネル・屋根・柱梁を
    最新のノード位置に合わせて再構築・再配置する関数。
    """
    up = Vector((0, 0, 1))

    for obj in panel_objs:
        if obj is None:
            continue
        ids = obj.get("panel_ids")
        if not ids or len(ids) != 4:
            continue
        a, b, c, d = ids
        verts = [
            node_objs[a].location,
            node_objs[b].location,
            node_objs[d].location,
            node_objs[c].location,
        ]
        mesh = obj.data
        mesh.clear_geometry()
        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.new("UVMap")
        vlist = [bm.verts.new(v) for v in verts]
        face = bm.faces.new(vlist)
        for loop, uv in zip(face.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            loop[uv_layer].uv = uv
        bm.to_mesh(mesh)
        bm.free()

    if roof_obj is not None and roof_quads:
        mesh = roof_obj.data
        mesh.clear_geometry()
        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.new("UVMap")
        vert_map: dict[int, bmesh.types.BMVert] = {}
        for quad in roof_quads:
            for nid in quad:
                if nid not in vert_map:
                    vert_map[nid] = bm.verts.new(node_objs[nid].location)
        for bl, br, tr, tl in roof_quads:
            face = bm.faces.new(
                [
                    vert_map[bl],
                    vert_map[br],
                    vert_map[tr],
                    vert_map[tl],
                ]
            )
            for loop, uv in zip(face.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
                loop[uv_layer].uv = uv
        bm.to_mesh(mesh)
        bm.free()

    for obj, a, b in member_objs:
        if obj is None:
            continue
        p1 = node_objs[a].location
        p2 = node_objs[b].location
        vec = p2 - p1
        mid = (p1 + p2) * 0.5
        length = vec.length
        obj.location = mid
        axis = up.cross(vec)
        if axis.length > 1e-3:
            axis.normalize()
            angle = up.angle(vec)
            obj.rotation_mode = "AXIS_ANGLE"
            obj.rotation_axis_angle = (angle, axis.x, axis.y, axis.z)
        else:
            obj.rotation_mode = "QUATERNION"
            obj.rotation_quaternion = Quaternion((1, 0, 0, 0))
        obj.scale = (obj.scale.x, obj.scale.y, length)


def init_animation(
    panel_objs: list[bpy.types.Object],
    roof_obj: bpy.types.Object | None,
    roof_quads: list[tuple[int, int, int, int]],
    member_objs: list[tuple[bpy.types.Object, int, int]],
    node_objs: dict[int, bpy.types.Object],
) -> None:
    """
    フレームチェンジハンドラを一度クリアし、毎フレーム最新のオブジェクトを取得して on_frame を呼び出す
    """
    bpy.app.handlers.frame_change_pre.clear()
    panel_names = [o.name for o in panel_objs if o]
    member_info = [(o.name, a, b) for (o, a, b) in member_objs if o]
    node_name_map = {nid: f"Node_{nid}" for nid in node_objs}
    roof_name = roof_obj.name if roof_obj else None

    def _viz_on_frame(scene: bpy.types.Scene):
        panels = [bpy.data.objects.get(n) for n in panel_names]
        members = [(bpy.data.objects.get(n), a, b) for (n, a, b) in member_info]
        nodes = {nid: bpy.data.objects.get(name) for nid, name in node_name_map.items()}
        roof = bpy.data.objects.get(roof_name) if roof_name else None
        on_frame(scene, panels, roof, roof_quads, members, nodes)

    bpy.app.handlers.frame_change_pre.append(_viz_on_frame)
