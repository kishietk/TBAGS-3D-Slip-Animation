"""
ファイル名: builders/sandbags.py

責務:
- サンドバッグノード群をBlender上に立方体として一括生成するビルダー。
- ノードIDとBlender Objectの辞書返却で、他のラベル・アニメ処理と連携しやすい設計。
- ラベル付与は専用関数で責任分離。

注意点:
- 入力nodesはSandbagNode型/Node型/座標dict等を暫定サポート（型統一はTODO）
- ラベル生成はcreate_sandbag_labelsでのみ担保

TODO:
- Node/SandbagNode型受け口の統一・型ヒント強化
- 直方体サイズ・座標等の入力バリデーション
- 物理シミュ/剛体設定等の将来責任分離
"""

import bpy
from mathutils import Vector
from utils.logging_utils import setup_logging
from builders.labels import create_label
from cores.nodeCore import Node
from configs import LABEL_SIZE, LABEL_OFFSET

log = setup_logging("build_sandbags")


def build_sandbags(
    nodes: dict[int, Node],
    cube_size: tuple[float, float, float],
) -> dict[int, bpy.types.Object]:
    """
    役割:
        各ノード位置に直方体サンドバッグを生成し、ノードID→Blender Object辞書を返す。

    引数:
        nodes (dict[int, Node]): ノードID→Node/SandbagNode
        cube_size (tuple[float, float, float]): (X, Y, Z)各辺サイズ

    返り値:
        dict[int, bpy.types.Object]: ノードID→Blender Object

    注意:
        - Blender立方体はデフォ1辺=2なのでスケール0.5で1x1x1となる
        - 入力型は現状暫定、将来統一予定
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
            objs[nid] = obj
        except Exception as e:
            log.error(f"Failed to create sandbag for node {nid}: {e}")
    log.info(f"{len(objs)}件のBlenderサンドバッグを生成しました。")
    return objs


def create_sandbag_labels(
    nodes: dict[int, Vector],
    abs_size: float = LABEL_SIZE,
    offset: Vector = LABEL_OFFSET,
) -> None:
    """
    役割:
        サンドバッグ立方体にノードIDラベルを付与する。

    引数:
        nodes (dict[int, Vector]): ノードID→座標
        abs_size (float): ラベル文字サイズ
        offset (Vector): ラベル配置オフセット

    返り値:
        None

    注意:
        - サンドバッグが見つからない場合は警告のみ（スキップ）
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
