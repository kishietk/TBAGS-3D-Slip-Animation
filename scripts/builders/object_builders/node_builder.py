"""
ファイル名: builders/object_builders/node_builder.py

責務:
- Node インスタンスの pos 属性から Blender 球体を生成する。
- 添え字アクセス（node[...]）は一切行わず、Node 型のみを受け付ける。
- 例外発生時にはログを残したうえでスキップ。

TODO:
- どうしても dict/tuple を混在させたい場合は明示的ファクトリ関数を用意する
"""

import bpy
from mathutils import Vector
from typing import Dict
from utils import setup_logging
from cores.entities import Node
from builders.base import BuilderBase
from configs import (
    SPHERE_RADIUS,
    UV_SPHERE_SEGMENTS,
    UV_SPHERE_RINGS,
    NODE_OBJ_PREFIX,
)

log = setup_logging("NodeBuilder")


class NodeBuilder(BuilderBase):
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
        役割:
            Node.pos から Blender 球体を生成（アニメーション処理なし）。
        引数:
            なし（コンストラクタで nodes, radius, segments, rings, name_prefix を受け取る）
        返り値:
            Dict[int, bpy.types.Object]: ノードID→Blenderオブジェクト
        """
        objs: Dict[int, bpy.types.Object] = {}
        for nid, node in self.nodes.items():
            # Node 型チェック
            if not isinstance(node, Node):
                log.error(
                    f"NodeBuilder: nodes[{nid}] が Node ではありません: {type(node)}"
                )
                continue

            # Vector 化
            pos = node.pos
            if not isinstance(pos, Vector):
                try:
                    pos = Vector(pos)
                except Exception as e:
                    log.error(f"NodeBuilder: ノード {nid} の位置 Vector 変換失敗: {e}")
                    continue

            # 球体生成
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
                log.debug(f"{obj.name} created at {tuple(pos)}")
            except Exception as e:
                log.error(f"NodeBuilder: {self.name_prefix}{nid} の生成失敗: {e}")

        log.info(f"{len(objs)} nodes built.")
        return objs
