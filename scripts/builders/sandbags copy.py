"""
サンドバッグノード群（SandbagNode）をBlender上に立方体で生成するビルダー

【設計思想】
- コアモデルのサンドバッグノード集合 → Blender上の立方体群へ一括生成
- ノードIDとBlender Object辞書を返すことで、他処理（ラベル付け・アニメ等）と連携しやすい
- ラベル生成関数も分離
"""

import bpy
from mathutils import Vector
from utils.logging_utils import setup_logging
from builders.labels import create_label
from cores.Node import Node
from config import LABEL_SIZE, LABEL_OFFSET

log = setup_logging()


def build_sandbags(
    nodes: dict[int, Node],
    cube_size: tuple[float, float, float],
) -> dict[int, bpy.types.Object]:
    """
    各ノード位置に直方体サンドバッグを生成（3辺サイズ指定対応）

    Args:
        nodes (dict[int, Node]): ノードID→Node/SandbagNode
        cube_size (tuple[float, float, float]): (X, Y, Z)各辺サイズ

    Returns:
        dict[int, bpy.types.Object]: ノードID→Blender Object
    """
    objs: dict[int, bpy.types.Object] = {}
    for nid, node in nodes.items():
        pos = node.pos if hasattr(node, "pos") else node[0]
        if not isinstance(pos, Vector):
            pos = Vector(pos)
        try:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos)
            obj = bpy.context.object
            obj.name = f"Sandbag_{nid}"
            # 3辺個別スケール
            obj.scale = (cube_size[0] / 2, cube_size[1] / 2, cube_size[2] / 2)
            # ※Blender立方体はデフォ1辺=2なので1.0立方体/scale=0.5で1x1x1
            objs[nid] = obj
        except Exception as e:
            log.error(f"Failed to create sandbag for node {nid}: {e}")
    return objs


def create_sandbag_labels(
    nodes: dict[int, Vector],
    abs_size: float = LABEL_SIZE,
    offset: Vector = LABEL_OFFSET,
) -> None:
    """
    サンドバッグ立方体にノードIDラベルを付与

    Args:
        nodes (dict[int, Vector]): ノードID→座標
        abs_size (float): ラベル文字サイズ
        offset (Vector): ラベル配置オフセット

    Returns:
        None
    """
    for nid, pos in nodes.items():
        sandbag_name = f"Sandbag_{nid}"
        obj = bpy.data.objects.get(sandbag_name)
        if not obj:
            log.warning(f"Sandbag object '{sandbag_name}' not found for label creation")
            continue
        create_label(
            obj,
            str(nid),
            abs_size=abs_size,
            offset=offset,
            name_prefix="SandbagLabel",
            use_constraint=True,
        )
