# builders/object_builders/node_builder.py

import bpy
from mathutils import Vector
from typing import Dict
from utils import setup_logging
from builders.base import BuilderBase
from builders.builder_registry import register_builder
from entities import Node
from configs import SPHERE_RADIUS, UV_SPHERE_SEGMENTS, UV_SPHERE_RINGS, NODE_OBJ_PREFIX

log = setup_logging("NodeBuilder")


class NodeBuilder(BuilderBase):
    """
    コアモデルのノード情報からBlenderのUV球（ノードオブジェクト）を生成するビルダー。

    Attributes:
        nodes (Dict[int, Node]): Node.pos属性を持つノード情報の辞書
        radius (float): 球の半径
        segments (int): 球の経線数
        rings (int): 球の緯線数
        name_prefix (str): Blenderオブジェクト名のプレフィクス
    """

    def __init__(
        self,
        nodes: Dict[int, Node],
        radius: float = SPHERE_RADIUS,
        segments: int = UV_SPHERE_SEGMENTS,
        rings: int = UV_SPHERE_RINGS,
        name_prefix: str = NODE_OBJ_PREFIX,
    ):
        super().__init__()
        self.nodes = nodes
        self.radius = radius
        self.segments = segments
        self.rings = rings
        self.name_prefix = name_prefix

    def build(self) -> Dict[int, bpy.types.Object]:
        """
        ノード情報からBlender球オブジェクトを生成する。

        Returns:
            Dict[int, bpy.types.Object]: ノードID→生成Blenderオブジェクト
        """
        objs: Dict[int, bpy.types.Object] = {}
        for nid, node in self.nodes.items():
            # pos 属性の存在チェック
            if not hasattr(node, "pos"):
                log.warning(
                    f"Skipping node {nid}: missing 'pos' attribute (type={type(node).__name__})"
                )
                continue
            pos = node.pos
            # Vector 型チェック・変換
            if not isinstance(pos, Vector):
                try:
                    pos = Vector(pos)
                except Exception as e:
                    log.warning(
                        f"Skipping node {nid}: invalid position data {pos!r}: {e}"
                    )
                    continue
            # 座標がゼロベクトルではないかチェック
            if pos.length == 0:
                log.warning(
                    f"Node {nid}: position is zero vector, which may indicate missing data"
                )
            # メッシュ生成
            try:
                bpy.ops.mesh.primitive_uv_sphere_add(
                    radius=self.radius,
                    location=pos,
                    segments=self.segments,
                    ring_count=self.rings,
                )
                obj = bpy.context.object
                obj.name = f"{self.name_prefix}{nid}"
                objs[nid] = obj
            except Exception as e:
                log.error(f"Failed to build node {nid}: {e}")
        # 完了ログ
        if not objs:
            log.warning(
                "NodeBuilder.build: completed with 0 built nodes. Verify that input nodes have valid .pos values."
            )
        return objs


@register_builder(Node)
def build_node(scene_builder, node: Node, ctx):
    """
    SceneBuilder から呼び出されるラッパー関数。
    NodeBuilder は dict 全体を受け取る設計なので、単一ノードを dict に詰めて渡す。
    """
    return NodeBuilder({node.id: node}).build()
