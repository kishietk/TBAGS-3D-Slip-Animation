import bpy
import bmesh
from typing import List, Dict, Optional
from mathutils import Vector
from utils import setup_logging
from configs import UV_MAP_NAME

log = setup_logging("PanelAnimator")


def update_panels(
    panel_objs: List[bpy.types.Object],
    node_objs: Dict[int, bpy.types.Object],
    scene: bpy.types.Scene,
) -> None:
    """
    壁パネルのメッシュをノード位置に合わせて更新する。

    Args:
        panel_objs: Builderによって生成されたパネルオブジェクトのリスト。
        node_objs: ノードIDをキー、対応するオブジェクトを値とする辞書。
        scene: 現在のシーン（フレーム情報取得用）。
    """
    frame = scene.frame_current
    log.debug(
        f"PanelAnimator: Updating panels at frame {frame}, count={len(panel_objs)}"
    )

    for obj in panel_objs:
        panel_ids = obj.get("panel_ids")
        if not panel_ids or len(panel_ids) != 4:
            continue

        # 各ノードの位置を取得
        coords: List[Vector] = []
        for nid in panel_ids:
            node = node_objs.get(nid)
            if node:
                coords.append(node.location.copy())
        if len(coords) != 4:
            continue

        mesh = obj.data
        mesh.clear_geometry()

        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.get(UV_MAP_NAME) or bm.loops.layers.uv.new(
            UV_MAP_NAME
        )

        # 頂点と面を作成
        bm_verts = [bm.verts.new(co) for co in coords]
        face = bm.faces.new(bm_verts)

        # UV設定: BL, BR, TR, TL
        uv_coords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        for loop, uv in zip(face.loops, uv_coords):
            loop[uv_layer].uv = uv

        # メッシュに書き戻し
        bm.to_mesh(mesh)
        mesh.update()
        bm.free()
