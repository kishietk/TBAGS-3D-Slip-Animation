# animators/building_animator.py

"""
ファイル名: animators/building_animator.py

責務:
- 建物本体（ノード・サンドバッグユニット・パネル・屋根・柱・梁）のアニメーション処理のみを担う。
- Blenderフレームごとに各部材の位置・形状を更新。
- 地面（Ground）は ground_animator.py で完全分離。
"""

import bpy
import bmesh
from typing import List, Tuple, Dict, Any, Optional
from mathutils import Vector, Quaternion
from utils.logging_utils import setup_logging
from configs import EPS_AXIS, UV_MAP_NAME

log = setup_logging("building_animator")


def on_frame_building(
    scene: bpy.types.Scene,
    panel_objs: List[bpy.types.Object],
    roof_obj: Optional[bpy.types.Object],
    roof_quads: List[Tuple[int, int, int, int]],
    member_objs: List[Tuple[bpy.types.Object, int, int]],
    node_objs: Dict[int, bpy.types.Object],
    sandbag_objs: Dict[int, bpy.types.Object],
    anim_data: Dict[int, Dict[int, Vector]],
    sandbag_anim_data: Dict[int, Dict[int, Vector]],
    base_node_pos: Dict[int, Vector],
    base_sandbag_pos: Dict[int, Vector],
    core: Optional[Any] = None,
) -> None:
    # --- ノード球アニメーション更新 ---
    for nid, obj in node_objs.items():
        if nid not in base_node_pos:
            continue
        disp = anim_data.get(nid, {}).get(scene.frame_current, Vector((0, 0, 0)))
        obj.location = base_node_pos[nid] + disp

    # --- サンドバッグユニットアニメーション（上下別々） ---
    for parent in sandbag_objs.values():
        for face in parent.children:
            nid = face.get("sandbag_node_id")
            if nid is None:
                continue
            disp = sandbag_anim_data.get(nid, {}).get(
                scene.frame_current, Vector((0, 0, 0))
            )
            # ローカル座標で初期Zに対する変位を反映
            face.location.x = disp.x
            face.location.y = disp.y
            initial_z = face.get("initial_z", face.location.z)
            face.location.z = initial_z + disp.z

    # --- パネル再構築 (通常／サンドバッグ両対応) ---
    for obj in panel_objs:
        try:
            ids = obj.get("panel_ids")
            if not ids or len(ids) != 4:
                continue
            verts = []
            for nid in ids:
                if nid in node_objs:
                    verts.append(node_objs[nid].location)
                else:
                    disp = sandbag_anim_data.get(nid, {}).get(
                        scene.frame_current, Vector((0, 0, 0))
                    )
                    verts.append(base_sandbag_pos.get(nid, Vector((0, 0, 0))) + disp)
            mesh = obj.data
            mesh.clear_geometry()
            bm = bmesh.new()
            uv_layer = bm.loops.layers.uv.new(UV_MAP_NAME)
            vlist = [bm.verts.new(v) for v in verts]
            f = bm.faces.new(vlist)
            for loop, uv in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
                loop[uv_layer].uv = uv
            bm.to_mesh(mesh)
            bm.free()
        except Exception as e:
            log.error(f"Failed to update panel {obj.name}: {e}")

    # --- 屋根再構築 ---
    if roof_obj and roof_quads:
        try:
            mesh = roof_obj.data
            mesh.clear_geometry()
            bm = bmesh.new()
            uv_layer = bm.loops.layers.uv.new(UV_MAP_NAME)
            vert_map: Dict[int, bmesh.types.BMVert] = {}
            for quad in roof_quads:
                for nid in quad:
                    coord = (
                        node_objs[nid].location
                        if nid in node_objs
                        else base_sandbag_pos.get(nid, Vector((0, 0, 0)))
                        + sandbag_anim_data.get(nid, {}).get(
                            scene.frame_current, Vector((0, 0, 0))
                        )
                    )
                    vert_map[nid] = (
                        bm.verts.new(coord) if nid not in vert_map else vert_map[nid]
                    )
            for bl, br, tr, tl in roof_quads:
                face = bm.faces.new([vert_map[n] for n in (bl, br, tr, tl)])
                for loop, uv in zip(face.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
                    loop[uv_layer].uv = uv
            bm.to_mesh(mesh)
            bm.free()
        except Exception as e:
            log.error(f"Failed to update roof: {e}")

    # --- 柱・梁再配置 (通常／サンドバッグ両対応) ---
    up = Vector((0, 0, 1))
    for obj, a, b in member_objs:
        try:

            def loc(nid):
                if nid in node_objs:
                    return node_objs[nid].location
                return base_sandbag_pos.get(
                    nid, Vector((0, 0, 0))
                ) + sandbag_anim_data.get(nid, {}).get(
                    scene.frame_current, Vector((0, 0, 0))
                )

            p1, p2 = loc(a), loc(b)
            mid, vec = (p1 + p2) * 0.5, p2 - p1
            length = vec.length
            obj.location = mid
            axis = up.cross(vec)
            if axis.length > EPS_AXIS:
                axis.normalize()
                angle = up.angle(vec)
                obj.rotation_mode = "AXIS_ANGLE"
                obj.rotation_axis_angle = (angle, axis.x, axis.y, axis.z)
            else:
                obj.rotation_mode = "QUATERNION"
                obj.rotation_quaternion = Quaternion((1, 0, 0, 0))

            # スケールを「元の長さ」で割って倍率を設定
            orig = obj.get("orig_depth", length)
            sx, sy, _ = obj.scale
            obj.scale = (sx, sy, length / orig)

        except Exception as e:
            log.error(f"Failed to update member {obj.name} (nodes {a}-{b}): {e}")
