"""
builders/groundBuilder.py

責務:
- グラウンドメッシュ（地面）の生成・マテリアル適用だけを担う
- 他部材と同列の「ただの部材」として扱う

使い方:
    from builders.groundBuilder import build_ground_plane
    ground_obj = build_ground_plane()
"""

import bpy
from utils.logging_utils import setup_logging
from configs import (
    GROUND_SIZE_X,
    GROUND_SIZE_Y,
    GROUND_LOCATION,
    GROUND_NAME,
    GROUND_MAT_NAME,
    GROUND_MAT_COLOR,
)

log = setup_logging("groundBuilder")


def create_ground_material(
    name: str = GROUND_MAT_NAME, color: tuple = GROUND_MAT_COLOR
) -> bpy.types.Material:
    """
    地面用マテリアル生成
    """
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    out = nt.nodes.new(type="ShaderNodeOutputMaterial")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.7
    return mat


def build_ground_plane(
    size_x: float = GROUND_SIZE_X,
    size_y: float = GROUND_SIZE_Y,
    location: tuple = GROUND_LOCATION,
    name: str = GROUND_NAME,
) -> bpy.types.Object:
    """
    地面（長方形平面）Blenderオブジェクトを生成・マテリアル適用して返す
    ※スケールではなく頂点編集でサイズを反映

    Returns:
        bpy.types.Object: 作成した地面オブジェクト
    """
    try:
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=location)
        ground_obj = bpy.context.object
        ground_obj.name = name

        # 頂点編集でサイズ反映（親子スケール影響ゼロ！）
        mesh = ground_obj.data
        for v in mesh.vertices:
            v.co.x *= size_x / 2  # Blender planeは±1
            v.co.y *= size_y / 2

        ground_obj.scale = (1, 1, 1)

        # マテリアル適用
        mat = create_ground_material()
        if mat:
            ground_obj.data.materials.clear()
            ground_obj.data.materials.append(mat)

        log.info(
            f"Ground plane '{name}' created (size_x={size_x}, size_y={size_y}, location={location})"
        )
        return ground_obj
    except Exception as e:
        log.error(f"Failed to create ground plane: {e}")
        raise
