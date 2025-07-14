# builders/object_builders/beam_builder.py
import bpy
from mathutils import Vector, Matrix
from typing import Dict, Set
from utils import setup_logging
from builders.base import BuilderBase
from builders.builder_registry import register_builder
from cores.entities import Edge
from configs import MEMBER_THICK, CYLINDER_VERTS, MEMBER_OBJ_PREFIX

log = setup_logging("BeamBuilder")


class BeamBuilder(BuilderBase):
    """
    コアモデルのエッジ情報（梁用エッジ）から Blender 円柱（梁）を生成するビルダー。
    """

    def __init__(
        self,
        positions: Dict[int, Vector],
        edges: Set[Edge],
        thickness: float = MEMBER_THICK,
        name_prefix: str = MEMBER_OBJ_PREFIX,
        verts: int = CYLINDER_VERTS,
    ):
        super().__init__()
        self.positions = positions
        self.edges = edges
        self.thickness = thickness
        self.name_prefix = name_prefix
        self.verts = verts

    def build(self) -> Dict[str, bpy.types.Object]:
        objs: Dict[str, bpy.types.Object] = {}
        for beam in self.edges:
            start_id = beam.node_a.id
            end_id = beam.node_b.id
            try:
                p0 = self.positions[start_id]
                p1 = self.positions[end_id]
            except KeyError:
                log.error(
                    f"BeamBuilder: nodes {start_id} or {end_id} missing in positions"
                )
                continue

            delta = p1 - p0
            length = delta.length
            mid = p0 + delta * 0.5

            # 円柱の回転
            up = Vector((0, 0, 1))
            axis = up.cross(delta)
            rot_mat = (
                Matrix.Identity(4)
                if axis.length < 1e-6
                else Matrix.Rotation(up.angle(delta), 4, axis.normalized())
            )

            # 円柱を追加
            bpy.ops.mesh.primitive_cylinder_add(
                radius=self.thickness / 2,
                depth=length,
                vertices=self.verts,
                location=mid,
            )
            obj = bpy.context.object
            obj.name = f"{self.name_prefix}{start_id}_{end_id}"
            # ノードID情報をカスタムプロパティとして保存
            obj["member_nodes"] = (start_id, end_id)
            # 深さのオリジナル値を保持
            obj["orig_depth"] = length
            # 回転行列を適用
            obj.matrix_world @= rot_mat.to_4x4()

            objs[f"{start_id}_{end_id}"] = obj
            log.debug(
                f"{obj.name} built between {start_id}–{end_id}, length={length:.3f}"
            )
        return objs


@register_builder(Edge)
def build_beam(scene_builder, beam: Edge, ctx):
    """
    SceneBuilder から渡される Edge（梁）をまとめて BeamBuilder に渡す。
    """
    positions = ctx.get("positions", {})
    return BeamBuilder(positions, {beam}).build()
