# builders/materials.py

import bpy
from typing import Dict, List, Tuple
from utils.logging import setup_logging
from config import WALL_IMG, ROOF_IMG, WALL_ALPHA, ROOF_ALPHA

log = setup_logging()

"""
materials.py

【役割 / Purpose】
- 壁・屋根・梁・ボーン柱それぞれに最適なBlenderマテリアルを自動生成・適用。
- 画像パスや透明度等はすべてconfig.pyから一元管理。直接値やパスを直書きしない！
- ノード球用のマテリアル生成は（現状非表示なので）省略可。
"""


def make_texture_mat(name: str, img_path: str, alpha: float) -> bpy.types.Material:
    """
    画像テクスチャ＋透明度を持つマテリアルを生成（壁・屋根用）

    引数:
        name: マテリアル名
        img_path: テクスチャ画像パス
        alpha: 透明度
    戻り値:
        Blenderマテリアル
    """
    try:
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        mat.use_nodes = True
        mat.blend_method = "BLEND"
        mat.shadow_method = "HASHED"
        nt = mat.node_tree
        nt.nodes.clear()
        tex = nt.nodes.new(type="ShaderNodeTexImage")
        transp = nt.nodes.new(type="ShaderNodeBsdfTransparent")
        bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
        mix = nt.nodes.new(type="ShaderNodeMixShader")
        out = nt.nodes.new(type="ShaderNodeOutputMaterial")
        tex.image = bpy.data.images.load(img_path)
        bsdf.inputs["Roughness"].default_value = 0.8
        mix.inputs["Fac"].default_value = 1.0 - alpha
        links = nt.links
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], mix.inputs[1])
        links.new(transp.outputs["BSDF"], mix.inputs[2])
        links.new(mix.outputs["Shader"], out.inputs["Surface"])
        log.debug(f"Texture material '{name}' created (alpha={alpha})")
        return mat
    except Exception as e:
        log.error(f"Failed to create texture material '{name}': {e}")
        raise


def make_column_mat() -> bpy.types.Material:
    """
    ボーン柱用マテリアル（波・ノイズ混ぜた木目調）を生成
    """
    try:
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
        mix.inputs["Color1"].default_value = (0.55, 0.35, 0.2, 1)
        mix.inputs["Color2"].default_value = (0.45, 0.25, 0.15, 1)
        bsdf.inputs["Roughness"].default_value = 0.6
        links = nt.links
        links.new(wave.outputs["Color"], mix.inputs["Fac"])
        links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        log.debug("Column material created")
        return mat
    except Exception as e:
        log.error(f"Failed to create column material: {e}")
        raise


def make_beam_mat() -> bpy.types.Material:
    """
    梁用マテリアル（ノイズ+グラデーション金属調）を生成
    """
    try:
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
    except Exception as e:
        log.error(f"Failed to create beam material: {e}")
        raise


def apply_all_materials(
    node_objs: dict,  # ノード球は使わないので空dictでOK
    panel_objs: List[bpy.types.Object],
    roof_obj: bpy.types.Object,
    member_objs: List[Tuple[bpy.types.Object, int, int]],
    bone_col_objs: List[
        bpy.types.Object
    ] = None,  # ボーン柱オブジェクト（必要なら渡す）
) -> None:
    """
    全オブジェクト（パネル・屋根・梁・ボーン柱）にマテリアルを一括適用

    引数:
        node_objs: {nid: Object}（ノード球。非表示なら空dictでOK）
        panel_objs: [Object, ...]
        roof_obj: Object
        member_objs: [(Object, a, b), ...]（梁）
        bone_col_objs: [Object, ...]（ボーン柱オブジェクト）
    """
    log.info("=== Applying all materials ===")
    try:
        mat_wall = make_texture_mat("WallMat", WALL_IMG, WALL_ALPHA)
        mat_roof = make_texture_mat("RoofMat", ROOF_IMG, ROOF_ALPHA)
        mat_col = make_column_mat()
        mat_beam = make_beam_mat()

        for o in panel_objs:
            o.data.materials.clear()
            o.data.materials.append(mat_wall)

        if roof_obj:
            roof_obj.data.materials.clear()
            roof_obj.data.materials.append(mat_roof)

        for obj, a, b in member_objs:
            obj.data.materials.clear()
            obj.data.materials.append(mat_beam)

        if bone_col_objs:
            for obj in bone_col_objs:
                obj.data.materials.clear()
                obj.data.materials.append(mat_col)

        log.info("Materials applied successfully.")
    except Exception as e:
        log.error(f"Failed to apply all materials: {e}")
        raise
