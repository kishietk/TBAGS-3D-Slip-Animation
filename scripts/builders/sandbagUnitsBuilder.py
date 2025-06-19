# builders/sandbagUnitsBuilder.py

from typing import Any, Dict, List
import bpy
from mathutils import Vector
from utils.logging_utils import setup_logging
from configs import SANDBAG_FACE_SIZE, SANDBAG_BAR_THICKNESS

log = setup_logging("build_sandbag_units")


def build_sandbag_units(units: List[Any]) -> Dict[int, bpy.types.Object]:
    """
    SandbagUnit のリストから、工字型ユニットを生成します。
    - 親Empty をユニットの重心位置に配置
    - 子要素として下面フェース、上面フェース、中央バーをローカル配置
    - フェースにはそれぞれ紐付くノードIDをカスタムプロパティとして設定

    上下面フェースを個別に動かせるように:
    - face["sandbag_node_id"] = 対応するノードID
    """
    objs: Dict[int, bpy.types.Object] = {}
    face_w, face_d = SANDBAG_FACE_SIZE

    for unit in units:
        cid = unit.id
        centroid: Vector = unit.centroid  # Vector(x, y, z)
        z0, z1 = unit.z_values  # [下面Z, 上面Z]
        height = z1 - z0

        # 1) 親 Empty を重心に配置
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=centroid)
        parent = bpy.context.object
        parent.name = f"SandbagUnit_{cid}"

        # 2) 下・上フェース
        for idx, (node, z) in enumerate(zip(unit.nodes, (z0, z1))):
            bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0))
            face = bpy.context.object
            face.name = f"SandbagFace_{cid}_{idx}"
            face.parent = parent
            # local座標: X/Y=0、Zは下面または上面
            face.location = Vector((0, 0, z - centroid.z))
            face.scale = Vector((face_w, face_d, 1))
            # カスタムプロパティでノードIDを保持
            face["sandbag_node_id"] = node.id

        # 3) 中央バー（円柱）
        mid_z = (z0 + z1) / 2
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=SANDBAG_BAR_THICKNESS,
            depth=height,
            location=(0, 0, 0),
        )
        bar = bpy.context.object
        bar.name = f"SandbagBar_{cid}"
        bar.parent = parent
        bar.location = Vector((0, 0, mid_z - centroid.z))

        objs[cid] = parent

    log.info(f"{len(objs)}件の工字サンドバッグユニットを生成しました。")
    return objs
