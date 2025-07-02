# animators/buildingAnimator.py

"""
ファイル名: animators/buildingAnimator.py

責務:
    - 各フレームでノード球、構造部材、パネル、屋根、サンドバッグユニットのアニメーションを更新。
    - SandbagUnitオブジェクトに設定されたrep_node／other_nodeの座標をBone_Rep/Bone_Otherに反映。

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
from utils.bone_name_resolver import get_rep_and_other_bones

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
    # ノード球位置更新
    for nid, obj in node_objs.items():
        base_pos = base_node_pos.get(nid, Vector())
        anim_offset = anim_data.get(nid, {}).get(scene.frame_current, Vector())
        obj.location = base_pos + anim_offset

    # Ground(親)の位置を取得（motion_parentの名前はプロジェクトに合わせて修正OK）
    motion_parent = bpy.data.objects.get("EarthquakeMotionParent")
    motion_parent_loc = motion_parent.location if motion_parent else Vector((0, 0, 0))

    # サンドバッグユニットアニメーション更新（Armature駆動）
    for unit in sandbag_objs.values():
        empty = unit.get("empty")
        armature = unit.get("armature_top")  # top/bottomどちらでも同じ

        unit_id = getattr(empty, "sandbag_unit_id", None) or empty.get(
            "sandbag_unit_id", "???"
        )
        top_id = getattr(empty, "rep_node_id", None) or empty.get("rep_node_id", None)
        bottom_id = getattr(empty, "other_node_id", None) or empty.get(
            "other_node_id", None
        )

        if not all((empty, armature)):
            log.warning(
                f"[SandbagUnit {unit_id}] EmptyまたはArmature未取得。empty={empty}, armature={armature}"
            )
            continue
        if top_id is None or bottom_id is None:
            log.warning(
                f"[SandbagUnit {unit_id}] ノードID未設定: top_id={top_id}, bottom_id={bottom_id}"
            )
            continue

        # ベース位置取得
        base_top = base_sandbag_pos.get(top_id, Vector())
        base_bottom = base_sandbag_pos.get(bottom_id, Vector())

        # CSV変位取得
        raw_disp_top = sandbag_anim_data.get(top_id, {}).get(
            scene.frame_current, Vector()
        )
        log.info(f"[SandbagUnit {unit_id}] raw_disp_top = {raw_disp_top}")
        # Y成分クリア
        disp_top = raw_disp_top.copy()
        disp_top.y = 0
        log.info(f"[SandbagUnit {unit_id}] disp_top(after clear Y) = {disp_top}")

        raw_disp_bottom = sandbag_anim_data.get(bottom_id, {}).get(
            scene.frame_current, Vector()
        )
        log.info(f"[SandbagUnit {unit_id}] raw_disp_bottom = {raw_disp_bottom}")
        disp_bottom = raw_disp_bottom.copy()
        disp_bottom.y = 0
        log.info(f"[SandbagUnit {unit_id}] disp_bottom(after clear Y) = {disp_bottom}")

        # 親オブジェクト変位取得＆Y成分クリア
        log.info(f"[SandbagUnit {unit_id}] motion_parent_loc = {motion_parent_loc}")
        mp_loc = motion_parent_loc.copy()
        mp_loc.y = 0
        log.info(f"[SandbagUnit {unit_id}] mp_loc(after clear Y) = {mp_loc}")

        # ワールド座標のターゲット位置
        pos_top = base_top + disp_top + mp_loc
        log.info(f"[SandbagUnit {unit_id}] pos_top = {pos_top}")

        pos_top = base_top + disp_top + mp_loc
        # Y座標は常に“生成時ベース”を再セット
        pos_top.y = base_top.y

        pos_bottom = base_bottom + disp_bottom + mp_loc
        pos_bottom.y = base_bottom.y
        

        # ボーン更新
        try:
            pb_top, pb_bottom = get_rep_and_other_bones(armature)
            inv = armature.matrix_world.inverted()

            # ローカルオフセット計算
            rel_top = inv @ pos_top - pb_top.bone.head_local
            log.info(f"[SandbagUnit {unit_id}] rel_top(before clear Y) = {rel_top}")
            rel_bottom = inv @ pos_bottom - pb_bottom.bone.head_local
            log.info(
                f"[SandbagUnit {unit_id}] rel_bottom(before clear Y) = {rel_bottom}"
            )

            # 念のためY成分を完全にクリア
            rel_top.y = 0
            rel_bottom.y = 0
            log.info(
                f"[SandbagUnit {unit_id}] rel_top(after clear Y) = {rel_top}, rel_bottom(after clear Y) = {rel_bottom}"
            )

            # ボーンに反映
            pb_top.location = rel_top
            pb_bottom.location = rel_bottom

        except Exception as e:
            log.error(f"[Sandbag {getattr(armature, 'name', '?')}] Bone更新失敗: {e}")

    # パネル更新
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

    # 屋根更新
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

    # 柱・梁再配置
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
