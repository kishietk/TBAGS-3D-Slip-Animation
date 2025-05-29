# アニメーション制御モジュール
# フレーム毎に壁パネル・屋根・柱梁をノード位置に自動追従させる

import bpy
import bmesh
from typing import List, Tuple
from mathutils import Vector, Quaternion
from utils.logging_utils import setup_logging
from config import (
    EPS_AXIS,
    NODE_OBJ_PREFIX,
    UV_MAP_NAME,
)

log = setup_logging()


def on_frame(
    scene: bpy.types.Scene,
    panel_objs: list[bpy.types.Object],
    roof_obj: bpy.types.Object | None,
    roof_quads: list[tuple[int, int, int, int]],
    member_objs: list[tuple[bpy.types.Object, int, int]],
    node_objs: dict[int, bpy.types.Object],
    sandbag_objs: dict[int, bpy.types.Object],
    anim_data: dict[int, dict[int, Vector]],
    sandbag_anim_data: dict[int, dict[int, Vector]],
    base_node_pos: dict[int, Vector],
    base_sandbag_pos: dict[int, Vector],
):
    # --- ノード球 ---
    for nid, obj in node_objs.items():
        if nid not in base_node_pos:
            continue
        base_pos = base_node_pos[nid]
        disp = anim_data.get(nid, {}).get(scene.frame_current, Vector((0, 0, 0)))
        obj.location = base_pos + disp

    # --- サンドバッグ ---
    for nid, obj in sandbag_objs.items():
        if nid not in base_sandbag_pos:
            continue
        base_pos = base_sandbag_pos[nid]
        disp = sandbag_anim_data.get(nid, {}).get(
            scene.frame_current, Vector((0, 0, 0))
        )
        obj.location = base_pos + disp

    # パネル再構築
    for obj in panel_objs:
        try:
            if obj is None:
                continue
            ids = obj.get("panel_ids")
            if not ids or len(ids) != 4:
                continue
            a, b, d, c = ids  # ← [a, b, d, c]の順で取得
            verts = [
                node_objs[a].location,
                node_objs[b].location,
                node_objs[d].location,
                node_objs[c].location,
            ]
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
        except Exception as e:
            log.error(f"Failed to update panel {getattr(obj, 'name', '?')}: {e}")

    # 屋根再構築
    if roof_obj is not None and roof_quads:
        try:
            mesh = roof_obj.data
            mesh.clear_geometry()
            bm = bmesh.new()
            uv_layer = bm.loops.layers.uv.new(UV_MAP_NAME)
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
        except Exception as e:
            log.error(f"Failed to update roof: {e}")

    # 柱・梁再配置
    up = Vector((0, 0, 1))
    for obj, a, b in member_objs:
        try:
            if obj is None:
                continue
            p1 = node_objs[a].location
            p2 = node_objs[b].location
            vec = p2 - p1
            mid = (p1 + p2) * 0.5
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
            obj.scale = (obj.scale.x, obj.scale.y, length)
        except Exception as e:
            log.error(
                f"Failed to update member {getattr(obj, 'name', '?')} (nodes {a}-{b}): {e}"
            )


def init_animation(
    panel_objs: list[bpy.types.Object],
    roof_obj: bpy.types.Object | None,
    roof_quads: list[tuple[int, int, int, int]],
    member_objs: list[tuple[bpy.types.Object, int, int]],
    node_objs: dict[int, bpy.types.Object],
    sandbag_objs: dict[int, bpy.types.Object],
    anim_data: dict[int, dict[int, Vector]],
    sandbag_anim_data: dict[int, dict[int, Vector]],
    base_node_pos: dict[int, Vector],
    base_sandbag_pos: dict[int, Vector],
) -> None:
    """
    Blenderのフレームチェンジ時にon_frameを呼ぶイベントを登録する
    引数:
        panel_objs: 壁パネルオブジェクトのリスト
        roof_obj: 屋根オブジェクト
        roof_quads: 屋根パネルIDタプルリスト
        member_objs: (オブジェクト, ノードAのID, ノードBのID)のリスト
        node_objs: ノードID→Blenderオブジェクトの辞書
        sandbag_objs: サンドバッグID→Blenderオブジェクトの辞書
        anim_data: ノードID→{フレーム: 変位Vector}
        sandbag_anim_data: サンドバッグID→{フレーム: 変位Vector}
        base_node_pos: ノードID→初期位置Vector
        base_sandbag_pos: サンドバッグID→初期位置Vector
    戻り値:
        なし
    """
    try:
        bpy.app.handlers.frame_change_pre.clear()
        panel_names = [o.name for o in panel_objs if o]
        member_info = [(o.name, a, b) for (o, a, b) in member_objs if o]
        node_name_map = {nid: obj.name for nid, obj in node_objs.items()}
        sandbag_name_map = {nid: obj.name for nid, obj in sandbag_objs.items()}
        roof_name = roof_obj.name if roof_obj else None

        def _viz_on_frame(scene: bpy.types.Scene):
            try:
                panels = [bpy.data.objects.get(n) for n in panel_names]
                members = [(bpy.data.objects.get(n), a, b) for (n, a, b) in member_info]
                nodes = {
                    nid: bpy.data.objects.get(name)
                    for nid, name in node_name_map.items()
                }
                sandbags = {
                    nid: bpy.data.objects.get(name)
                    for nid, name in sandbag_name_map.items()
                }
                roof = bpy.data.objects.get(roof_name) if roof_name else None
                on_frame(
                    scene,
                    panels,
                    roof,
                    roof_quads,
                    members,
                    nodes,
                    sandbags,
                    anim_data,
                    sandbag_anim_data,
                    base_node_pos,
                    base_sandbag_pos,
                )
            except Exception as e:
                log.error(f"Error in frame_change handler: {e}")

        bpy.app.handlers.frame_change_pre.append(_viz_on_frame)
        log.info("Animation handler registered.")
    except Exception as e:
        log.critical(f"Failed to register animation handler: {e}")
        raise
