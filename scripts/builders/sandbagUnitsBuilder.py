# builders/sandbagUnitsBuilder.py

import bpy
from mathutils import Vector
from utils.logging_utils import setup_logging
from cores.sandbagUnit import SandbagUnit
from configs.constants import SANDBAG_FACE_SIZE, SANDBAG_BAR_THICKNESS

log = setup_logging("build_sandbag_units")


def build_sandbag_units(
    units: list[SandbagUnit],
) -> dict[str, bpy.types.Object]:
    """
    役割:
        SandbagUnitごとに“工”字形オブジェクト（Empty親 + 2面 + 中央バー）を生成。
    """
    objs: dict[str, bpy.types.Object] = {}
    for unit in units:
        # 親Empty
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=unit.centroid)
        parent = bpy.context.object
        parent.name = f"SandbagUnit_{unit.id}"

        bottom_z, top_z = unit.z_values
        face_w, face_d = SANDBAG_FACE_SIZE

        # 下部面
        for idx, z in enumerate((bottom_z, top_z)):
            bpy.ops.mesh.primitive_plane_add(
                size=1.0,
                location=(unit.centroid.x, unit.centroid.y, z),
            )
            face = bpy.context.object
            face.name = f"SandbagUnit_{unit.id}_Face_{idx}"
            # 面の縦横サイズ調整
            face.scale = (face_w / 2, face_d / 2, 1)
            face.parent = parent

        # 中央バー（円柱）
        height = top_z - bottom_z
        mid_z = (bottom_z + top_z) / 2
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=SANDBAG_BAR_THICKNESS,
            depth=height,
            location=(unit.centroid.x, unit.centroid.y, mid_z),
        )
        bar = bpy.context.object
        bar.name = f"SandbagUnit_{unit.id}_Bar"
        bar.parent = parent

        objs[unit.id] = parent

    log.info(f"{len(objs)}件の工字サンドバッグユニットを生成しました。")
    return objs
