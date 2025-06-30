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

log = setup_logging("building_animator")


def on_frame_building(
    scene: bpy.types.Scene,
    panel_objs: List[bpy.types.Object],
    roof_obj: Optional[bpy.types.Object],
    roof_quads: List[Tuple[int, int, int, int]],
    member_objs: List[Tuple[bpy.types.Object, int, int]],
    node_objs: Dict[int, bpy.types.Object],
    sandbag_objs: Dict[Any, bpy.types.Object],
    anim_data: Dict[int, Dict[int, Vector]],
    sandbag_anim_data: Dict[int, Dict[int, Vector]],
    base_node_pos: Dict[int, Vector],
    base_sandbag_pos: Dict[Any, Vector],
    core: Optional[Any] = None,
) -> None:
    """
    シーン更新ごとに呼び出され、各種オブジェクトの位置・形状をアニメーションデータに基づき更新する。

    Args:
        scene: 現在のBlenderシーン
        panel_objs: パネルオブジェクトリスト
        roof_obj: 屋根オブジェクト
        roof_quads: 屋根面のノードIDタプルリスト
        member_objs: (オブジェクト, start_id, end_id) の柱／梁リスト
        node_objs: ノードID→球オブジェクトマップ
        sandbag_objs: サンドバッグEmpty/Armatureマップ
        anim_data: ノードアニメーションオフセット
        sandbag_anim_data: サンドバッグノードアニメーションオフセット
        base_node_pos: 初期ノード座標
        base_sandbag_pos: 初期サンドバッグ座標
        core: 将来拡張用（未使用）
    """
    # ノード球位置更新
    for nid, obj in node_objs.items():
        if nid in base_node_pos:
            obj.location = base_node_pos[nid] + anim_data.get(nid, {}).get(
                scene.frame_current, Vector()
            )

    # サンドバッグユニットアニメーション更新
    for obj in sandbag_objs.values():
        rep_id = obj.get("rep_node_id")
        other_id = obj.get("other_node_id")
        if rep_id is None or other_id is None:
            continue
        base_rep = base_sandbag_pos.get(rep_id, Vector())
        base_other = base_sandbag_pos.get(other_id, Vector())
        disp_rep = sandbag_anim_data.get(rep_id, {}).get(scene.frame_current, Vector())
        disp_other = sandbag_anim_data.get(other_id, {}).get(
            scene.frame_current, Vector()
        )
        pos_rep = base_rep + disp_rep
        pos_other = base_other + disp_other

        try:
            if obj.type == "ARMATURE":
                arm = obj
                pb_rep = arm.pose.bones.get("Bone_Rep")
                if pb_rep:
                    pb_rep.location = (
                        arm.matrix_world.inverted() @ pos_rep - pb_rep.bone.head_local
                    )
                pb_oth = arm.pose.bones.get("Bone_Other")
                if pb_oth:
                    pb_oth.location = (
                        arm.matrix_world.inverted() @ pos_other - pb_oth.bone.head_local
                    )
            else:
                obj.location = pos_rep
        except Exception as e:
            log.error(f"Sandbag animation update failed for {obj.name}: {e}")

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
