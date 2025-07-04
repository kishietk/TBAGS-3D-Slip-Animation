# animators/building_animator.py

"""
ファイル名: animators/building_animator.py

責務:
    - 各フレームでノード球、構造部材、パネル、屋根、サンドバッグユニットのアニメーションを更新。
    - 単一の Armature オブジェクト内の 'top'／'bottom' PoseBone を駆動し、キーフレームを当てる。

TODO:
    - Bone名やEmpty運用時のボーン構成を外部設定化
    - 例外発生時のフォールバック動作（ログレベルやリトライ）強化
    - 処理セクションの関数化と共通化によるリファクタリング
    - 単体テスト追加: 引数バリデーションと例外シナリオ検証
"""
import bpy
import bmesh
from typing import List, Tuple, Dict, Any, Optional
from mathutils import Vector, Quaternion
from utils import setup_logging
from configs import EPS_AXIS, UV_MAP_NAME

log = setup_logging("building_animator")


def on_frame_building(
    scene: bpy.types.Scene,
    panel_objs: List[bpy.types.Object],
    roof_obj: Optional[bpy.types.Object],
    roof_quads: List[Tuple[int, int, int, int]],
    member_objs: List[Tuple[bpy.types.Object, int, int]],
    node_objs: Dict[int, bpy.types.Object],
    sandbag_objs: Dict[Any, Dict[str, bpy.types.Object]],
    anim_data: Dict[int, Dict[int, Vector]],
    sandbag_anim_data: Dict[int, Dict[int, Vector]],
    base_node_pos: Dict[int, Vector],
    base_sandbag_pos: Dict[Any, Vector],
    core: Optional[Any] = None,
) -> None:
    """
    シーン更新ごとに呼び出され、各種オブジェクトの位置・形状をアニメーションデータに基づき更新する。
    """
    # 1度だけログを出す
    if scene.frame_current == scene.frame_start:
        log.info(
            "=================[アニメーション開始]========================="
            f"FPS: {scene.render.fps}, Start Frame: {scene.frame_start}, End Frame: {scene.frame_end}"
        )

    # ノード球位置更新
    for nid, obj in node_objs.items():
        if nid in base_node_pos:
            obj.location = base_node_pos[nid] + anim_data.get(nid, {}).get(
                scene.frame_current, Vector()
            )

    # サンドバッグユニットアニメーション更新
    for sandbag in sandbag_objs.values():
        empty = sandbag.get("empty")
        armature = sandbag.get("armature")
        if not (empty and armature):
            log.error(
                f"[SandbagAnimator] Sandbag オブジェクトが不足: {empty}, {armature}"
            )
            continue

        top_id = empty.get("top_node_id")
        bottom_id = empty.get("bottom_node_id")
        if top_id is None or bottom_id is None:
            log.error(
                f"[Sandbag {armature.name}] 'top_node_id' または 'bottom_node_id' 未設定"
            )
            continue

        # 位置取得
        base_top = base_sandbag_pos.get(top_id, Vector())
        base_bottom = base_sandbag_pos.get(bottom_id, Vector())
        disp_top = sandbag_anim_data.get(top_id, {}).get(scene.frame_current, Vector())
        disp_bottom = sandbag_anim_data.get(bottom_id, {}).get(
            scene.frame_current, Vector()
        )
        pos_top = base_top + disp_top
        pos_bottom = base_bottom + disp_bottom

        # ボーン取得
        from utils.bone_name_resolver import get_rep_and_other_bones

        try:
            pb_top, pb_bottom = get_rep_and_other_bones(armature)
        except RuntimeError as e:
            log.error(f"[Sandbag {armature.name}] ボーン解決失敗: {e}")
            continue

        try:
            inv = armature.matrix_world.inverted()
            # 上面ボーンの tail を合わせる
            world_off_top = (inv @ pos_top) - pb_top.bone.tail_local
            rot_inv_top = pb_top.bone.matrix_local.to_3x3().inverted()
            pb_top.location = rot_inv_top @ world_off_top
            pb_top.keyframe_insert("location")

            # 下面ボーンの tail を合わせる
            world_off_bot = (inv @ pos_bottom) - pb_bottom.bone.tail_local
            rot_inv_bot = pb_bottom.bone.matrix_local.to_3x3().inverted()
            pb_bottom.location = rot_inv_bot @ world_off_bot
            pb_bottom.keyframe_insert("location")
        except Exception as e:
            log.error(f"[Sandbag {armature.name}] Bone更新失敗: {e}")

    # パネル更新（省略）
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
                    + sandbag_anim_data.get(nid, {}).get(scene.frame_current, Vector())
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

    # 屋根更新（省略）
    if roof_obj and roof_quads:
        mesh = roof_obj.data
        mesh.clear_geometry()
        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.new(UV_MAP_NAME)
        vert_map: Dict[int, bmesh.types.BMVert] = {}
        for quad in roof_quads:
            for nid in quad:
                if nid in node_objs:
                    pos = node_objs[nid].location
                else:
                    pos = base_sandbag_pos.get(nid, Vector()) + sandbag_anim_data.get(
                        nid, {}
                    ).get(scene.frame_current, Vector())
                if nid not in vert_map:
                    vert_map[nid] = bm.verts.new(pos)
        for bl, br, tr, tl in roof_quads:
            f = bm.faces.new([vert_map[n] for n in (bl, br, tr, tl)])
            for loop, uv in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
                loop[uv_layer].uv = uv
        bm.to_mesh(mesh)
        bm.free()

    # 柱・梁再配置（省略）
    up = Vector((0, 0, 1))
    for obj, a, b in member_objs:
        p1 = (
            node_objs[a].location
            if a in node_objs
            else base_sandbag_pos.get(a, Vector())
            + sandbag_anim_data.get(a, {}).get(scene.frame_current, Vector())
        )
        p2 = (
            node_objs[b].location
            if b in node_objs
            else base_sandbag_pos.get(b, Vector())
            + sandbag_anim_data.get(b, {}).get(scene.frame_current, Vector())
        )
        mid = (p1 + p2) * 0.5
        vec = p2 - p1
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
        length = vec.length
        orig = obj.get("orig_depth", length)
        sx, sy, _ = obj.scale
        obj.scale = (sx, sy, length / orig)
