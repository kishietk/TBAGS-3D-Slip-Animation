import bpy
from logging_utils import setup_logging
from config import WALL_IMG, ROOF_IMG, WALL_ALPHA, ROOF_ALPHA

log = setup_logging()


def make_texture_mat(name: str, img_path: str, alpha: float) -> bpy.types.Material:
    """
    画像テクスチャ＋透明度を持つマテリアルを生成（壁・屋根用）

    引数:
        name: マテリアル名
        img_path: テクスチャ画像ファイルパス
        alpha: 透明度（0.0=完全透明, 1.0=不透明）

    戻り値:
        mat: 生成したBlenderマテリアル
    """
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = "BLEND"
    mat.shadow_method = "HASHED"
    nt = mat.node_tree
    nt.nodes.clear()
    # 各ノード構成
    tex = nt.nodes.new(type="ShaderNodeTexImage")
    transp = nt.nodes.new(type="ShaderNodeBsdfTransparent")
    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    mix = nt.nodes.new(type="ShaderNodeMixShader")
    out = nt.nodes.new(type="ShaderNodeOutputMaterial")
    # 設定
    tex.image = bpy.data.images.load(img_path)
    bsdf.inputs["Roughness"].default_value = 0.8
    mix.inputs["Fac"].default_value = 1.0 - alpha
    # ノード接続
    links = nt.links
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], mix.inputs[1])
    links.new(transp.outputs["BSDF"], mix.inputs[2])
    links.new(mix.outputs["Shader"], out.inputs["Surface"])
    log.debug(f"Texture material '{name}' created (alpha={alpha})")
    return mat


def make_column_mat() -> bpy.types.Material:
    """
    柱用マテリアル（波・ノイズを混ぜた木目調）を生成

    戻り値:
        mat: 生成したマテリアル
    """
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
    # パラメータ調整
    wave.inputs["Scale"].default_value = 10
    wave.inputs["Distortion"].default_value = 2
    noise.inputs["Scale"].default_value = 50
    mix.blend_type = "MIX"
    mix.inputs["Color1"].default_value = (0.55, 0.35, 0.2, 1)
    mix.inputs["Color2"].default_value = (0.45, 0.25, 0.15, 1)
    bsdf.inputs["Roughness"].default_value = 0.6
    # ノード接続
    links = nt.links
    links.new(wave.outputs["Color"], mix.inputs["Fac"])
    links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    log.debug("Column material created")
    return mat


def make_beam_mat() -> bpy.types.Material:
    """
    梁用マテリアル（ノイズ+グラデーション金属調）を生成

    戻り値:
        mat: 生成したマテリアル
    """
    name = "BeamMat"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    noise = nt.nodes.new(type="ShaderNodeTexNoise")
    ramp = nt.nodes.new(type="ShaderNodeValToRGB")
    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    out = nt.nodes.new(type="ShaderNodeOutputMaterial")
    # パラメータ
    noise.inputs["Scale"].default_value = 100
    noise.inputs["Detail"].default_value = 2
    ramp.color_ramp.elements[0].position = 0
    ramp.color_ramp.elements[0].color = (0.2, 0.2, 0.2, 1)
    ramp.color_ramp.elements[1].position = 1
    ramp.color_ramp.elements[1].color = (0.4, 0.4, 0.4, 1)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.3
    # ノード接続
    links = nt.links
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    log.debug("Beam material created")
    return mat


def make_node_mat() -> bpy.types.Material:
    """
    ノード球用マテリアル（シンプルなオレンジ色）を生成

    戻り値:
        mat: 生成したマテリアル
    """
    name = "NodeMat"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    # 既存のPrincipledノードがあれば再利用
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not bsdf:
        nt.nodes.clear()
        bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
        out = nt.nodes.new(type="ShaderNodeOutputMaterial")
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = (1.0, 0.5, 0.0, 1)
    log.debug("Node material created")
    return mat


def apply_all_materials(
    node_objs: dict, panel_objs: list, roof_obj: bpy.types.Object, member_objs: list
):
    """
    全オブジェクト（ノード球・壁パネル・屋根・柱・梁）にマテリアルを一括適用

    引数:
        node_objs: {nid: Object}
        panel_objs: [Object, ...]
        roof_obj: Object or None
        member_objs: [(Object, a, b), ...]
    """
    log.info("=== Applying all materials ===")
    # 各種マテリアル生成
    mat_wall = make_texture_mat("WallMat", WALL_IMG, WALL_ALPHA)
    mat_roof = make_texture_mat("RoofMat", ROOF_IMG, ROOF_ALPHA)
    mat_col = make_column_mat()
    mat_beam = make_beam_mat()
    mat_node = make_node_mat()

    # 壁パネル
    for o in panel_objs:
        o.data.materials.clear()
        o.data.materials.append(mat_wall)

    # 屋根
    if roof_obj:
        roof_obj.data.materials.clear()
        roof_obj.data.materials.append(mat_roof)

    # 柱・梁
    for obj, a, b in member_objs:
        if obj.name.startswith("Column_") or (
            obj.name.startswith("Member_") and "Column" in obj.name
        ):
            obj.data.materials.clear()
            obj.data.materials.append(mat_col)
        else:
            obj.data.materials.clear()
            obj.data.materials.append(mat_beam)

    # ノード球
    for o in node_objs.values():
        o.data.materials.clear()
        o.data.materials.append(mat_node)

    log.info("Materials applied successfully.")
