"""
Blenderオブジェクト用マテリアル生成・一括適用モジュール

- 壁、屋根、柱、梁、ノード球、サンドバッグ（立方体）ごとの専用マテリアル生成
- apply_all_materialsで一括割り当て
- モジュール設計思想：シーンビルドやアニメータから独立して「材料生成・割り当て責任のみ」を持つ
"""

import bpy
from typing import Dict, List, Tuple, Optional
from utils.logging_utils import setup_logging
from configs import WALL_IMG, ROOF_IMG, WALL_ALPHA, ROOF_ALPHA

log = setup_logging()


def make_texture_mat(name: str, img_path: str, alpha: float) -> bpy.types.Material:
    """
    テクスチャ画像・透明度付きマテリアル生成

    Args:
        name (str): マテリアル名
        img_path (str): テクスチャ画像ファイルパス
        alpha (float): 透明度（0:完全透明, 1:不透明）

    Returns:
        bpy.types.Material: 作成されたマテリアル

    Raises:
        Exception: Blenderマテリアル生成に失敗時
    """
    try:
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
    柱用マテリアル（木目調）生成

    Returns:
        bpy.types.Material: 作成されたマテリアル

    Raises:
        Exception: Blenderマテリアル生成に失敗時
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
    梁用マテリアル（金属調）生成

    Returns:
        bpy.types.Material: 作成されたマテリアル

    Raises:
        Exception: Blenderマテリアル生成に失敗時
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


def make_node_mat() -> bpy.types.Material:
    """
    ノード球用マテリアル（オレンジ色）生成

    Returns:
        bpy.types.Material: 作成されたマテリアル

    Raises:
        Exception: Blenderマテリアル生成に失敗時
    """
    try:
        name = "NodeMat"
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if not bsdf:
            nt.nodes.clear()
            bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
            out = nt.nodes.new(type="ShaderNodeOutputMaterial")
            nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        bsdf.inputs["Base Color"].default_value = (1.0, 0.5, 0.0, 1)
        log.debug("Node material created")
        return mat
    except Exception as e:
        log.error(f"Failed to create node material: {e}")
        raise


def make_sandbag_mat() -> bpy.types.Material:
    """
    サンドバッグ用マテリアル（緑色系）生成

    Returns:
        bpy.types.Material: 作成されたマテリアル

    Raises:
        Exception: Blenderマテリアル生成に失敗時
    """
    try:
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
    except Exception as e:
        log.error(f"Failed to create sandbag material: {e}")
        raise


def apply_all_materials(
    node_objs: Dict[int, bpy.types.Object],
    sandbag_objs: Dict[int, bpy.types.Object],
    panel_objs: List[bpy.types.Object],
    roof_obj: Optional[bpy.types.Object],
    member_objs: List[Tuple[bpy.types.Object, int, int]],
    ground_obj=None,
) -> None:
    """
    ノード球・サンドバッグ立方体・壁パネル・屋根・柱・梁にマテリアルを一括適用

    Args:
        node_objs (Dict[int, bpy.types.Object]): ノード球オブジェクト
        sandbag_objs (Dict[int, bpy.types.Object]): サンドバッグオブジェクト
        panel_objs (List[bpy.types.Object]): パネルオブジェクトリスト
        roof_obj (Optional[bpy.types.Object]): 屋根オブジェクト
        member_objs (List[Tuple[bpy.types.Object, int, int]]): 柱・梁のBlenderオブジェクト（オブジェクト, ノードA, ノードB）

    Returns:
        None

    Raises:
        Exception: 適用中にエラー発生時
    """
    log.info("=== Applying all materials ===")
    try:
        mat_wall = make_texture_mat("WallMat", WALL_IMG, WALL_ALPHA)
        mat_roof = make_texture_mat("RoofMat", ROOF_IMG, ROOF_ALPHA)
        mat_col = make_column_mat()
        mat_beam = make_beam_mat()
        mat_node = make_node_mat()
        mat_sandbag = make_sandbag_mat()

        # パネル
        panel_count = 0
        for o in panel_objs:
            o.data.materials.clear()
            o.data.materials.append(mat_wall)
            panel_count += 1

        # 屋根
        roof_count = 0
        if roof_obj:
            roof_obj.data.materials.clear()
            roof_obj.data.materials.append(mat_roof)
            roof_count += 1

        # 柱・梁
        column_count = 0
        beam_count = 0
        for obj, a, b in member_objs:
            if obj.name.startswith("Column_"):
                obj.data.materials.clear()
                obj.data.materials.append(mat_col)
                column_count += 1
            elif obj.name.startswith("Beam_"):
                obj.data.materials.clear()
                obj.data.materials.append(mat_beam)
                beam_count += 1
            else:
                obj.data.materials.clear()
                obj.data.materials.append(mat_beam)

        # ノード球
        node_count = 0
        for o in node_objs.values():
            o.data.materials.clear()
            o.data.materials.append(mat_node)
            node_count += 1

        # サンドバッグ
        sandbag_count = 0
        for o in sandbag_objs.values():
            o.data.materials.clear()
            o.data.materials.append(mat_sandbag)
            sandbag_count += 1

        # グラウンドメッシュ
        if ground_obj is not None:
            from builders.groundBuilder import create_ground_material
            mat = create_ground_material()
            if mat:
                ground_obj.data.materials.clear()
                ground_obj.data.materials.append(mat)

        log.info(
            f"Materials applied. Panels: {panel_count}, Roofs: {roof_count}, "
            f"Columns: {column_count}, Beams: {beam_count}, Nodes: {node_count}, Sandbags: {sandbag_count}"
        )
    except Exception as e:
        log.error(f"Failed to apply all materials: {e}")
        raise
