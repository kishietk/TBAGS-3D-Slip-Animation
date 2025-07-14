import bpy
import bmesh
from typing import List, Tuple, Dict, Optional
from mathutils import Vector
from utils import setup_logging
from configs import UV_MAP_NAME

log = setup_logging("RoofAnimator")


def update_roof(
    roof_obj: Optional[bpy.types.Object],
    roof_quads: List[Tuple[int, int, int, int]],
    node_objs: Dict[int, bpy.types.Object],
    scene: bpy.types.Scene,
) -> None:
    """
    屋根パネルのメッシュをノード位置に合わせて更新する。

    Args:
        roof_obj: Builderによって生成された屋根オブジェクト。
        roof_quads: 各クワッドをノードIDタプルで表したリスト。
        node_objs: ノードIDをキー、対応オブジェクトを値とする辞書。
        scene: 現在のシーン（フレーム情報取得用）。
    """
    frame = scene.frame_current
    log.debug(f"RoofAnimator: Updating roof at frame {frame}")

    if not roof_obj or not roof_quads:
        return

    mesh = roof_obj.data
    mesh.clear_geometry()

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.get(UV_MAP_NAME) or bm.loops.layers.uv.new(
        UV_MAP_NAME
    )

    # ノードID→BMVertマッピング
    vert_map: Dict[int, bmesh.types.BMVert] = {}
    for quad in roof_quads:
        for nid in quad:
            if nid not in vert_map:
                node = node_objs.get(nid)
                if node:
                    vert_map[nid] = bm.verts.new(node.location.copy())

    # 面とUV設定
    uv_coords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for quad in roof_quads:
        verts = [vert_map.get(nid) for nid in quad]
        if any(v is None for v in verts):
            continue
        face = bm.faces.new(verts)
        for loop, uv in zip(face.loops, uv_coords):
            loop[uv_layer].uv = uv

    # メッシュに書き戻し
    bm.to_mesh(mesh)
    mesh.update()
    bm.free()
