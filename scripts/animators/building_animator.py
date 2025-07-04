import bpy
from typing import List, Tuple, Dict, Any, Optional
from mathutils import Vector
from utils import setup_logging
from animators.object_animators import (
    update_nodes,
    update_sandbag,
    update_panels,
    update_roof,
    update_members,
)

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

    # ノード球位置更新
    update_nodes(node_objs, anim_data, base_node_pos, scene)

    # サンドバッグアニメーション更新
    for sandbag in sandbag_objs.values():
        update_sandbag(sandbag, sandbag_anim_data, base_sandbag_pos, scene)

    # パネル更新
    update_panels(panel_objs, node_objs, base_sandbag_pos, sandbag_anim_data, scene)

    # 屋根更新
    update_roof(
        roof_obj, roof_quads, node_objs, base_sandbag_pos, sandbag_anim_data, scene
    )

    # 柱・梁再配置
    update_members(member_objs, node_objs, base_sandbag_pos, sandbag_anim_data, scene)
