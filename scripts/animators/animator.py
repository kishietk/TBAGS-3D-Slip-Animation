"""
アニメーション制御モジュール
- Blenderフレームごとにパネル・屋根・柱梁・サンドバッグをノード変位に自動追従
- on_frame(): 各オブジェクトの位置・形状を全自動更新
- init_animation(): Blenderのフレーム変更イベントにハンドラを登録

【設計ポイント】
- panel_objs/roof_obj/member_objs等、Blender Objectリストを直接制御
- ノード位置/変位はanim_data/sandbag_anim_data/base_posから計算
- panel/roof/member更新はbmeshで都度再生成
"""

import bpy
import bmesh
from typing import List, Tuple, Dict, Optional
from mathutils import Vector, Quaternion
from utils.logging_utils import setup_logging
from config import (
    EPS_AXIS,
    UV_MAP_NAME,
)

log = setup_logging()


def on_frame(
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
) -> None:
    """
    1フレーム毎に各Blenderオブジェクトの座標・形状を自動で更新する
    Args:
        scene: Blenderシーン
        panel_objs: パネルObjectリスト
        roof_obj: 屋根ObjectまたはNone
        roof_quads: 屋根を構成するノードID 4つ組リスト
        member_objs: (Object, ノードA, ノードB)のリスト
        node_objs: ノードID→Blender Object
        sandbag_objs: サンドバッグID→Blender Object
        anim_data: ノードID→{フレーム: 変位Vector}
        sandbag_anim_data: サンドバッグID→{フレーム: 変位Vector}
        base_node_pos: ノードID→初期位置Vector
        base_sandbag_pos: サンドバッグID→初期位置Vector
    Returns:
        None
    """
    all_node_objs = {**node_objs, **sandbag_objs}

    # ノード球更新
    for nid, obj in node_objs.items():
        if nid not in base_node_pos:
            continue
        base_pos = base_node_pos[nid]
        disp = anim_data.get(nid, {}).get(scene.frame_current, Vector((0, 0, 0)))
        obj.location = base_pos + disp

    # サンドバッグ更新
    for nid, obj in sandbag_objs.items():
        if nid not in base_sandbag_pos:
            continue
        base_pos = base_sandbag_pos[nid]
        disp = sandbag_anim_data.get(nid, {}).get(
            scene.frame_current, Vector((0, 0, 0))
        )
        obj.location = base_pos + disp

    # パネル再構築（4ノードで面生成＋UV）
    for obj in panel_objs:
        try:
            if obj is None:
                continue
            ids = obj.get("panel_ids")
            if not ids or len(ids) != 4:
                continue
            a, b, d, c = ids  # [a, b, d, c]の順
            verts = [
                all_node_objs[a].location,
                all_node_objs[b].location,
                all_node_objs[d].location,
                all_node_objs[c].location,
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

    # 屋根再構築（roof_quadsが空でなければbmesh生成）
    if roof_obj is not None and roof_quads:
        try:
            mesh = roof_obj.data
            mesh.clear_geometry()
            bm = bmesh.new()
            uv_layer = bm.loops.layers.uv.new(UV_MAP_NAME)
            vert_map: Dict[int, bmesh.types.BMVert] = {}
            for quad in roof_quads:
                for nid in quad:
                    if nid not in vert_map:
                        vert_map[nid] = bm.verts.new(all_node_objs[nid].location)
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

    # 柱・梁再配置（位置・姿勢・長さをノードにフィット）
    up = Vector((0, 0, 1))
    for obj, a, b in member_objs:
        try:
            if obj is None:
                continue
            p1 = all_node_objs[a].location
            p2 = all_node_objs[b].location
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
) -> None:
    """
    Blenderのフレームチェンジ時にon_frame()を自動実行するイベント登録
    Args:
        panel_objs: 壁パネルObjectリスト
        roof_obj: 屋根ObjectまたはNone
        roof_quads: 屋根を構成するノードID 4つ組リスト
        member_objs: (Object, ノードA, ノードB)リスト
        node_objs: ノードID→Blender Object
        sandbag_objs: サンドバッグID→Blender Object
        anim_data: ノードID→{フレーム: 変位Vector}
        sandbag_anim_data: サンドバッグID→{フレーム: 変位Vector}
        base_node_pos: ノードID→初期位置Vector
        base_sandbag_pos: サンドバッグID→初期位置Vector
    Returns:
        None
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
