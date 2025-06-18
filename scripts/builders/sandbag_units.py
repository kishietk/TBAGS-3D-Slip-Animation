# builders/sandbagUnitsBuilder.py

from typing import Any
import bpy
from mathutils import Vector
from utils.logging_utils import setup_logging
from configs import SANDBAG_FACE_SIZE, SANDBAG_BAR_THICKNESS

log = setup_logging("build_sandbag_units")


def build_sandbag_units(units: list[Any]) -> dict[int, bpy.types.Object]:
    """
    SandbagUnit のリストから、工字型ユニットを生成。
    親Empty の下に、上下フェースと中央バーをローカル配置する。
    """
    objs: dict[int, bpy.types.Object] = {}
    face_w, face_d = SANDBAG_FACE_SIZE

    for unit in units:
        cid = unit.id
        cent = unit.centroid  # Vector(x, y, z)
        z0, z1 = unit.z_values  # [下面Z, 上面Z]
        height = z1 - z0
        mid_z = (z0 + z1) / 2

        # 1) 親 Empty
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=cent)
        parent = bpy.context.object
        parent.name = f"SandbagUnit_{cid}"

        # 2) 下・上フェース
        for idx, z in enumerate((z0, z1)):
            bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0))
            face = bpy.context.object
            face.name = f"SandbagFace_{cid}_{idx}"
            face.parent = parent
            # 重心からの相対位置でローカル配置
            face.location = Vector((0, 0, z - cent.z))
            # 面の縦横サイズを正確に反映
            face.scale = Vector((face_w, face_d, 1))

        # 3) 中央バー（円柱）
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=SANDBAG_BAR_THICKNESS,
            depth=height,
            location=(0, 0, 0),
        )
        bar = bpy.context.object
        bar.name = f"SandbagBar_{cid}"
        bar.parent = parent
        # 重心からの相対位置でローカル配置
        bar.location = Vector((0, 0, mid_z - cent.z))

        objs[cid] = parent

    log.info(f"{len(objs)}件の工字サンドバッグユニットを生成しました。")
    return objs
