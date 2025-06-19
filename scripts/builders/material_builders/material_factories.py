# builders/material_builders/material_factories.py

"""
ファイル名: builders/material_builders/material_factories.py

責務:
- 部材ごとの Blender マテリアルを生成する関数群を提供。
- テクスチャマテリアル、柱・梁・ノード・サンドバッグ・地面用マテリアルを生成。
"""

import bpy
from utils.logging_utils import setup_logging
from configs import (
    WALL_IMG,
    ROOF_IMG,
    WALL_ALPHA,
    ROOF_ALPHA,
    GROUND_MAT_NAME,
    GROUND_MAT_COLOR,
)

log = setup_logging("material_factories")


def create_texture_material(
    name: str, img_path: str, alpha: float
) -> bpy.types.Material:
    """
    役割:
        画像テクスチャ＋透明度マテリアルを生成
    """
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = "BLEND"
    nt = mat.node_tree
    nt.nodes.clear()

    tex = nt.nodes.new(type="ShaderNodeTexImage")
    transp = nt.nodes.new(type="ShaderNodeBsdfTransparent")
    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    mix = nt.nodes.new(type="ShaderNodeMixShader")
    out = nt.nodes.new(type="ShaderNodeOutputMaterial")

    try:
        tex.image = bpy.data.images.load(img_path)
    except Exception as e:
        log.error(f"Failed to load image for '{name}': {e}")
        raise

    bsdf.inputs["Roughness"].default_value = 0.8
    mix.inputs["Fac"].default_value = 1.0 - alpha

    links = nt.links
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], mix.inputs[1])
    links.new(transp.outputs["BSDF"], mix.inputs[2])
    links.new(mix.outputs["Shader"], out.inputs["Surface"])

    log.debug(f"Texture material '{name}' created (alpha={alpha})")
    return mat


def create_wall_material() -> bpy.types.Material:
    """壁パネル用テクスチャマテリアル"""
    return create_texture_material("WallMat", WALL_IMG, WALL_ALPHA)


def create_roof_material() -> bpy.types.Material:
    """屋根パネル用テクスチャマテリアル"""
    return create_texture_material("RoofMat", ROOF_IMG, ROOF_ALPHA)


def create_column_material() -> bpy.types.Material:
    """柱用マテリアル（木目調）"""
    name = "ColumnMat"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    wave = nt.nodes.new(type="ShaderNodeTexWave")
    noise = nt.nodes.new(type="ShaderNodeTexNoise")
    mix = nt.nodes.new(type="ShaderNodeMixRGB")
    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    out = nt.nodes.new(type="ShaderNodeOutputMaterial")

    wave.inputs["Scale"].default_value = 10
    wave.inputs["Distortion"].default_value = 2
    noise.inputs["Scale"].default_value = 50
    mix.blend_type = "MIX"
    mix.inputs["Color1"].default_value = (0.55, 0.35, 0.20, 1)
    mix.inputs["Color2"].default_value = (0.45, 0.25, 0.15, 1)
    bsdf.inputs["Roughness"].default_value = 0.6

    links = nt.links
    links.new(wave.outputs["Color"], mix.inputs["Fac"])
    links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    log.debug("Column material created")
    return mat


def create_beam_material() -> bpy.types.Material:
    """梁用マテリアル（金属調）"""
    name = "BeamMat"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    noise = nt.nodes.new(type="ShaderNodeTexNoise")
    ramp = nt.nodes.new(type="ShaderNodeValToRGB")
    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    out = nt.nodes.new(type="ShaderNodeOutputMaterial")

    noise.inputs["Scale"].default_value = 100
    noise.inputs["Detail"].default_value = 2
    ramp.color_ramp.elements[0].position = 0
    ramp.color_ramp.elements[0].color = (0.2, 0.2, 0.2, 1)
    ramp.color_ramp.elements[1].position = 1
    ramp.color_ramp.elements[1].color = (0.4, 0.4, 0.4, 1)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.3

    links = nt.links
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    log.debug("Beam material created")
    return mat


def create_node_material() -> bpy.types.Material:
    """ノード球用マテリアル（オレンジ色）"""
    name = "NodeMat"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree

    # 既存 Principled ノードを探すか、新規作成
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not bsdf:
        nt.nodes.clear()
        bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
        out = nt.nodes.new(type="ShaderNodeOutputMaterial")
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    bsdf.inputs["Base Color"].default_value = (1.0, 0.5, 0.0, 1)
    log.debug("Node material created")
    return mat


def create_sandbag_material() -> bpy.types.Material:
    """サンドバッグ用マテリアル（緑色）"""
    name = "SandbagMat"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    out = nt.nodes.new(type="ShaderNodeOutputMaterial")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = (0.25, 0.61, 0.30, 1)
    bsdf.inputs["Metallic"].default_value = 0.7
    bsdf.inputs["Roughness"].default_value = 0.7

    log.debug("Sandbag material created")
    return mat


def create_ground_material(
    name: str = GROUND_MAT_NAME, color: tuple = GROUND_MAT_COLOR
) -> bpy.types.Material:
    """地面用シンプルマテリアル"""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    out = nt.nodes.new(type="ShaderNodeOutputMaterial")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.7

    log.debug("Ground material created")
    return mat
