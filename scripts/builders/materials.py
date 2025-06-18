"""
ファイル名: builders/materials.py

責務:
- 壁/屋根/柱/梁/ノード/サンドバッグ等、部材ごとのBlenderマテリアル生成・一括適用のみを担う。
- apply_all_materialsでまとめて割り当てる。
- 「材料生成・割り当て責任のみ」を持ち、他のシーンビルドやアニメータ等からは独立。

TODO:
- テクスチャ/カラー・パラメータの一元管理や外部設定化
- マテリアル生成の共通ユーティリティ化（重複コード吸収）
- テスト用のダミーマテリアル/例外パスも将来追加
- ground系・panel系とさらに責任範囲分割の検討
"""

import bpy
from typing import Dict, List, Tuple, Optional
from utils.logging_utils import setup_logging
from configs import WALL_IMG, ROOF_IMG, WALL_ALPHA, ROOF_ALPHA

log = setup_logging("materials")


def make_texture_mat(name: str, img_path: str, alpha: float) -> bpy.types.Material:
    """
    役割:
        テクスチャ画像・透明度付きマテリアルを生成する。
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
    役割:
        柱用マテリアル（木目調）生成
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
    役割:
        梁用マテリアル（金属調）生成
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
    役割:
        ノード球用マテリアル（オレンジ色）生成
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
    役割:
        サンドバッグ用マテリアル（緑色系）生成
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
    役割:
        ノード球・サンドバッグ立方体・壁パネル・屋根・柱・梁にマテリアルを一括適用。
    """
    try:
        mat_wall = make_texture_mat("WallMat", WALL_IMG, WALL_ALPHA)
        mat_roof = make_texture_mat("RoofMat", ROOF_IMG, ROOF_ALPHA)
        mat_col = make_column_mat()
        mat_beam = make_beam_mat()
        mat_node = make_node_mat()
        mat_sandbag = make_sandbag_mat()

        # 件数カウント用
        counts = {
            "パネル": 0,
            "屋根": 0,
            "柱": 0,
            "梁": 0,
            "ノード": 0,
            "サンドバッグ": 0,
            "地面": 0,
        }

        # パネル
        for o in panel_objs:
            o.data.materials.clear()
            o.data.materials.append(mat_wall)
            counts["パネル"] += 1

        # 屋根
        if roof_obj:
            roof_obj.data.materials.clear()
            roof_obj.data.materials.append(mat_roof)
            counts["屋根"] += 1

        # 柱・梁
        for obj, a, b in member_objs:
            obj.data.materials.clear()
            if obj.name.startswith("Column_"):
                obj.data.materials.append(mat_col)
                counts["柱"] += 1
            elif obj.name.startswith("Beam_"):
                obj.data.materials.append(mat_beam)
                counts["梁"] += 1
            else:
                # 分類不能 → 梁として処理
                obj.data.materials.append(mat_beam)
                counts["梁"] += 1
                log.warning(
                    f"オブジェクト「{obj.name}」は柱・梁名規則に一致せず。梁としてマテリアルを適用。"
                )

        # ノード球
        for o in node_objs.values():
            o.data.materials.clear()
            o.data.materials.append(mat_node)
            counts["ノード"] += 1

        # サンドバッグユニット配下のメッシュに適用
        for parent in sandbag_objs.values():
            if parent is None:
                continue
            for child in parent.children:
                # メッシュかをチェック
                if getattr(child.data, "materials", None) is not None:
                    child.data.materials.clear()
                    child.data.materials.append(mat_sandbag)
                    counts["サンドバッグ"] += 1

        # グラウンドメッシュ
        if ground_obj is not None:
            from builders.groundBuilder import create_ground_material

            mat = create_ground_material()
            if mat:
                ground_obj.data.materials.clear()
                ground_obj.data.materials.append(mat)
                counts["地面"] += 1
            else:
                log.warning("地面マテリアルの作成に失敗しました（Noneが返されました）")

        # ログ
        summary = "、".join([f"{label}:{n}" for label, n in counts.items() if n > 0])
        log.info(f"マテリアルを適用:[{summary}]")

    except Exception as e:
        log.error(f"マテリアル一括適用処理に失敗しました: {e}")
        raise
