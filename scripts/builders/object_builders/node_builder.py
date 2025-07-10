# builders/object_builders/node_builder.py
import bpy
from mathutils import Vector
from typing import Dict, Any
from utils import setup_logging
from builders.base import BuilderBase
from configs import SPHERE_RADIUS, UV_SPHERE_SEGMENTS, UV_SPHERE_RINGS, NODE_OBJ_PREFIX

log = setup_logging("NodeBuilder")

class NodeBuilder(BuilderBase):
    def __init__(
        self,
        nodes: Dict[int, Any],  # NodeData or similar with .pos
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
        objs: Dict[int, bpy.types.Object] = {}
        log.info(f"Starting NodeBuilder.build with {len(self.nodes)} input nodes")
        for nid, node in self.nodes.items():
            # pos 属性の存在チェック
            if not hasattr(node, 'pos'):
                log.warning(f"Skipping node {nid}: missing 'pos' attribute (type={type(node).__name__})")
                continue
            pos = getattr(node, 'pos')
            # Vector 型チェック・変換
            if not isinstance(pos, Vector):
                log.info(f"Node {nid}: pos is not Vector, attempting conversion: {pos}")
                try:
                    pos = Vector(pos)
                except Exception as e:
                    log.warning(f"Skipping node {nid}: invalid position data {pos!r}: {e}")
                    continue
            # 座標がゼロベクトルではないかチェック
            if pos.length == 0:
                log.warning(f"Node {nid}: position is zero vector, which may indicate missing data")
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
                log.info(f"Built node object '{obj.name}' at {tuple(pos)}")
            except Exception as e:
                log.error(f"Failed to build node {nid}: {e}")
        # 完了ログ
        if not objs:
            log.warning("NodeBuilder.build: completed with 0 built nodes. Verify that input nodes have valid .pos values and are in VALID_NODE_IDS set.")
        else:
            log.info(f"NodeBuilder.build: built {len(objs)} nodes successfully.")
        return objs