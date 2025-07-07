import bpy
from typing import Dict, Any
from mathutils import Vector


def update_nodes(
    node_objs: Dict[int, bpy.types.Object],
    anim_data: Dict[int, Dict[int, Vector]],
    base_node_pos: Dict[int, Vector],
    scene: bpy.types.Scene,
) -> None:
    """
    ノード球の位置を更新する。
    """
    frame = scene.frame_current
    for nid, obj in node_objs.items():
        if nid in base_node_pos:
            obj.location = base_node_pos[nid] + anim_data.get(nid, {}).get(
                frame, Vector()
            )
