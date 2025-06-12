"""
animators/building_animator.py

責務:
- 建物本体（ノード・サンドバッグ・パネル・屋根・柱・梁）のアニメーション処理を専任
- Blenderフレームごとに各部材の位置・形状を自動で更新

設計指針:
- 地面（Ground）のアニメ責任はground_animator.pyに完全分離
- on_frame_building は「建物全体」を動かすだけに限定
- フレームごとの座標計算/再生成のみ担当（イベント登録はhandler.pyで一元化推奨）

利用前提:
- 建物コアデータとBlenderオブジェクト、アニメーション辞書は全てmain等から渡す
"""

import bpy
import bmesh
from typing import List, Tuple, Dict, Optional
from mathutils import Vector, Quaternion
from utils.logging_utils import setup_logging
from configs import EPS_AXIS, UV_MAP_NAME

log = setup_logging("building_animator")

# 必要に応じて警告済みIDを管理
already_warned_no_anim_node = set()
already_warned_no_anim_sandbag = set()


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
) -> None:
    """
    1フレーム毎に建物各オブジェクトの座標・形状を自動更新

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
        if nid not in anim_data:
            if nid not in already_warned_no_anim_node:
                log.debug(
                    f"ノードID={nid} はアニメーションデータ自体がありません（常に変位ゼロ）"
                )
                already_warned_no_anim_node.add(nid)
            disp = Vector((0, 0, 0))
        else:
            node_anim = anim_data[nid]
            disp = node_anim.get(scene.frame_current, Vector((0, 0, 0)))
        obj.location = base_pos + disp

    # サンドバッグ更新
    for nid, obj in sandbag_objs.items():
        if nid not in base_sandbag_pos:
            continue
        base_pos = base_sandbag_pos[nid]
        if nid not in sandbag_anim_data:
            if nid not in already_warned_no_anim_sandbag:
                log.debug(
                    f"サンドバッグID={nid} はアニメーションデータ自体がありません（常に変位ゼロ）"
                )
                already_warned_no_anim_sandbag.add(nid)
            disp = Vector((0, 0, 0))
        else:
            anim_data_sb = sandbag_anim_data[nid]
            disp = anim_data_sb.get(scene.frame_current, Vector((0, 0, 0)))
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
