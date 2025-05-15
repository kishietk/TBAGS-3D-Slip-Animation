import bpy
import bmesh
from mathutils import Vector, Quaternion
from logging_utils import setup_logging

log = setup_logging()

def on_frame(scene, panel_objs, roof_obj, roof_quads, member_objs, node_objs):
    up = Vector((0, 0, 1))

    # ── 壁パネル 再構築 ───────────────────────
    for obj in panel_objs:
        a, b, c, d = obj["panel_ids"]
        verts = [node_objs[n].location for n in (a, b, d, c)]  # CCW
        mesh = obj.data
        mesh.clear_geometry()
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new("UVMap")
        v_bm = [bm.verts.new(v) for v in verts]
        face = bm.faces.new(v_bm)
        for loop, uvco in zip(face.loops, [(0,0), (1,0), (1,1), (0,1)]):
            loop[uv].uv = uvco
        bm.to_mesh(mesh)
        bm.free()

    # ── 屋根 再構築 ───────────────────────────
    if roof_obj and roof_quads:
        mesh = roof_obj.data
        mesh.clear_geometry()
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new("UVMap")
        vids = {}
        for quad in roof_quads:
            for nid in quad:
                if nid not in vids:
                    vids[nid] = bm.verts.new(node_objs[nid].location)
        for bl, br, tr, tl in roof_quads:
            face = bm.faces.new([vids[bl], vids[br], vids[tr], vids[tl]])
            for loop, uvco in zip(face.loops, [(0,0), (1,0), (1,1), (0,1)]):
                loop[uv].uv = uvco
        bm.to_mesh(mesh)
        bm.free()

    # ── 柱・梁 再配置 ──────────────────────────
    for obj, a, b in member_objs:
        p1 = node_objs[a].location
        p2 = node_objs[b].location
        vec = p2 - p1
        mid = (p1 + p2) * 0.5
        length = vec.length

        obj.location = mid

        # 回転
        axis = up.cross(vec)
        if axis.length > 1e-6:
            axis.normalize()
            angle = up.angle(vec)
            obj.rotation_mode = 'AXIS_ANGLE'
            obj.rotation_axis_angle = (angle, axis.x, axis.y, axis.z)
        else:
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = Quaternion((1, 0, 0, 0))

        # スケール
        sx, sy, _ = obj.scale
        obj.scale = (sx, sy, length)

def init_animation(panel_objs, roof_obj, roof_quads, member_objs, node_objs):
    """
    アニメーション更新関数を登録し、初回フレームも即実行。
    """
    handler_name = "_viz_on_frame"

    def _viz_on_frame(scene):
        on_frame(scene, panel_objs, roof_obj, roof_quads, member_objs, node_objs)

    _viz_on_frame.__name__ = handler_name

    # 既存登録削除
    handlers = bpy.app.handlers.frame_change_pre
    for h in list(handlers):
        if getattr(h, "__name__", "") == handler_name:
            handlers.remove(h)

    bpy.app.handlers.frame_change_pre.append(_viz_on_frame)
    _viz_on_frame(bpy.context.scene)
    log.info("Animation handler registered.")
