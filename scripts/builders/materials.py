import bpy
from utils.logging_utils import setup_logging
from config import WALL_IMG, ROOF_IMG, WALL_ALPHA, ROOF_ALPHA

log = setup_logging()


def make_texture_mat(name: str, img_path: str, alpha: float) -> bpy.types.Material:
    """
    テクスチャ画像・透明度を持つマテリアルを生成する
    引数:
        name: マテリアル名
        img_path: テクスチャ画像ファイルパス
        alpha: 透明度（0.0～1.0）
    戻り値:
        生成したBlenderマテリアル
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
    柱用マテリアル（木目調）を生成する
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
    梁用マテリアル（金属調）を生成する
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
    ノード球用マテリアル（オレンジ色）を生成する
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


def apply_all_materials(
    node_objs: dict[int, bpy.types.Object],
    panel_objs: list[bpy.types.Object],
    roof_obj: bpy.types.Object,
    member_objs: list[tuple[bpy.types.Object, int, int]],
) -> None:
    """
    ノード球・壁パネル・屋根・柱・梁にマテリアルを一括適用し、
    各種オブジェクトに適用した数を詳細ログに出力する
    """
    log.info("=== Applying all materials ===")
    try:
        mat_wall = make_texture_mat("WallMat", WALL_IMG, WALL_ALPHA)
        mat_roof = make_texture_mat("RoofMat", ROOF_IMG, ROOF_ALPHA)
        mat_col = make_column_mat()
        mat_beam = make_beam_mat()
        mat_node = make_node_mat()

        panel_count = 0
        roof_count = 0
        column_count = 0
        beam_count = 0
        node_count = 0

        for o in panel_objs:
            o.data.materials.clear()
            o.data.materials.append(mat_wall)
            panel_count += 1
            log.debug(f"Panel {o.name}: Material set to WallMat")

        if roof_obj:
            roof_obj.data.materials.clear()
            roof_obj.data.materials.append(mat_roof)
            roof_count += 1
            log.debug(f"Roof {roof_obj.name}: Material set to RoofMat")

        for obj, a, b in member_objs:
            if obj.name.startswith("Column_"):
                obj.data.materials.clear()
                obj.data.materials.append(mat_col)
                column_count += 1
                log.debug(f"Column {obj.name}: Material set to ColumnMat")
            elif obj.name.startswith("Beam_"):
                obj.data.materials.clear()
                obj.data.materials.append(mat_beam)
                beam_count += 1
                log.debug(f"Beam {obj.name}: Material set to BeamMat")
            else:
                obj.data.materials.clear()
                obj.data.materials.append(mat_beam)
                log.debug(f"Member {obj.name}: Material set to BeamMat (default)")

        for o in node_objs.values():
            o.data.materials.clear()
            o.data.materials.append(mat_node)
            node_count += 1
            log.debug(f"Node {o.name}: Material set to NodeMat")

        log.info(
            f"Materials applied successfully. Panels: {panel_count}, Roofs: {roof_count}, "
            f"Columns: {column_count}, Beams: {beam_count}, Nodes: {node_count}"
        )
    except Exception as e:
        log.error(f"Failed to apply all materials: {e}")
        raise
