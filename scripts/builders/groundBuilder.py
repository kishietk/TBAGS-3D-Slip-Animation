"""
ファイル名: builders/groundBuilder.py

責務:
- グラウンドメッシュ（地面）Blenderオブジェクトの生成とマテリアル適用のみを担う。
- 他部材と同列の「単純な部材」として設計（ビルダー群の1つ）。

使い方:
    from builders.groundBuilder import build_ground_plane
    ground_obj = build_ground_plane()

TODO:
- マテリアル生成の共通化（他部材との統合/外部ユーティリティ化）
- groundオブジェクトにタグ/属性管理追加
- カスタム形状・凹凸・マップ対応など拡張余地
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
    役割:
        地面用のシンプルなマテリアルを生成・返す。
    引数:
        name (str): マテリアル名
        color (tuple): RGBAカラー
    返り値:
        bpy.types.Material: Blenderマテリアル
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
    役割:
        地面（長方形平面）Blenderオブジェクトを生成し、マテリアル適用して返す。
        ※頂点編集で正確なサイズ反映

    引数:
        size_x (float): X方向サイズ
        size_y (float): Y方向サイズ
        location (tuple): 中心座標
        name (str): オブジェクト名

    返り値:
        bpy.types.Object: 作成した地面オブジェクト
    """
    try:
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=location)
        ground_obj = bpy.context.object
        ground_obj.name = name

        # 頂点編集でサイズ反映
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

        log.info(f"Blenderパネル(地面)を生成しました: {ground_obj.name} (size={size_x}x{size_y})")
        return ground_obj
    except Exception as e:
        log.error(f"Failed to create ground plane: {e}")
        raise
