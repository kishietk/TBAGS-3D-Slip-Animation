"""
ファイル名: builders/nodes.py

責務:
- ノードIDと座標からBlender球体（ノード球）を静的に生成する。
- アニメーション・キーフレーム処理は一切持たず、純粋なモデルビルドのみ担う。
- ノードラベル付与もサポート（builders/labels依存）。

注意点:
- 入力はNode型 or {'pos', 'kind_id'}を持つdictにも対応（暫定的多態性）
- ノード球生成失敗時の例外ログのみで復帰
- ラベル生成責任はcreate_node_labels関数に限定

TODO:
- 入力型統一・受け口整理（Node型またはpydantic/dataclass型推奨に変更予定）
- ラベル/ノード本体のスタイル・可視性制御の責任分離
"""

import bpy
from mathutils import Vector
from typing import Dict
from utils.logging_utils import setup_logging
from cores.nodeCore import Node
from builders.labels import create_label
from configs import LABEL_SIZE, LABEL_OFFSET

log = setup_logging("build_nodes")


def build_nodes(
    nodes: Dict[int, Node],  # Node型または {pos, kind_id}を持つdict型
    radius: float,
) -> Dict[int, bpy.types.Object]:
    """
    役割:
        ノード座標からBlender球体（ノード球）を静的に生成する。
        ※アニメーション処理は行わない。

    引数:
        nodes (Dict[int, Node]): ノードID→Nodeインスタンス or (pos, kind_id)持つdict
        radius (float): 球体半径

    返り値:
        Dict[int, bpy.types.Object]: ノードID→Blenderオブジェクトの辞書

    注意:
        - 入力型が複数ある現状は暫定。今後型を統一推奨。
    """
    objs: Dict[int, bpy.types.Object] = {}
    for nid, node in nodes.items():
        # Node型かdict/tupleか判定し、安全に座標(Vector)を取り出す
        if hasattr(node, "pos"):
            pos = node.pos
        elif isinstance(node, (list, tuple)):
            pos = node[0]
        elif isinstance(node, dict) and "pos" in node:
            pos = node["pos"]
        else:
            log.error(f"Node {nid}: Could not extract position! Skipping.")
            continue

        # Vector型でなければ変換
        if not isinstance(pos, Vector):
            try:
                pos = Vector(pos)
            except Exception as e:
                log.error(f"Node {nid}: Invalid position value {pos}: {e}")
                continue

        try:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=pos)
            obj = bpy.context.object
            obj.name = f"Node_{nid}"
            objs[nid] = obj
            log.debug(f"Node sphere {nid} created at {tuple(pos)} (radius={radius})")
        except Exception as e:
            log.error(f"Failed to create node sphere for ID {nid}: {e}")
    log.info(f"{len(objs)}件のBlenderノード(#1)を生成しました。")
    return objs


def create_node_labels(
    nodes: Dict[int, Vector],
    abs_size: float = LABEL_SIZE,
    offset: Vector = LABEL_OFFSET,
) -> None:
    """
    役割:
        ノード球体にノードIDラベルを付与する。
    引数:
        nodes (Dict[int, Vector]): ノードID→座標
        abs_size (float): ラベル文字サイズ
        offset (Vector): ラベル配置オフセット
    返り値:
        None

    注意:
        - ノードオブジェクトが見つからなければ警告のみ（スキップ）
    """
    for nid, pos in nodes.items():
        node_name = f"Node_{nid}"
        obj = bpy.data.objects.get(node_name)
        if not obj:
            log.warning(f"Node object '{node_name}' not found for label creation")
            continue
        create_label(
            obj,
            str(nid),
            abs_size=abs_size,
            offset=offset,
            name_prefix="Label",
            use_constraint=True,
        )
