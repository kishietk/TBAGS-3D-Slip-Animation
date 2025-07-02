from typing import Any, Dict, List, Tuple, Optional
from utils import setup_logging
from builders.base import BuilderBase
from builders.object_builders import (
    NodeBuilder,
    SandbagBuilder,
    PanelBuilder,
    RoofBuilder,
    ColumnBuilder,
    BeamBuilder,
    GroundBuilder,
)
from configs import SPHERE_RADIUS
from cores.constructors.core_factory import CoreFactory
import bpy

log = setup_logging("SceneBuilder")


class SceneBuilder(BuilderBase):
    """
    CoreFactory で生成済みのコアモデルから、Blender シーン用オブジェクトをビルドするクラス。

    build() メソッドは以下を返す:
        - node_objs: Dict[node_id, bpy.types.Object]
        - sandbag_base_objs: Dict[unit_id, {'empty': EmptyObj, 'armature_twist': ArmatureObj, 'armature_bend': ArmatureObj}]
        - panel_objs: List[bpy.types.Object]
        - roof_obj: bpy.types.Object
        - roof_quads: List[Tuple[int, int, int, int]]
        - member_objs: List[Tuple[bpy.types.Object, int, int]]
        - ground_obj: Optional[bpy.types.Object]
    """

    def __init__(
        self,
        core: CoreFactory,
        include_ground: bool = True,
    ):
        super().__init__()
        self.core = core
        self.include_ground = include_ground

    def build(
        self,
    ) -> Tuple[
        Dict[int, bpy.types.Object],
        Dict[Any, Dict[str, bpy.types.Object]],
        List[bpy.types.Object],
        bpy.types.Object,
        List[Tuple[int, int, int, int]],
        List[Tuple[bpy.types.Object, int, int]],
        Optional[bpy.types.Object],
    ]:
        # 1. コアモデルから分類済みデータ取得
        normal_nodes = self.core.normal_nodes
        panels = self.core.panels
        column_edges = self.core.columns
        beam_edges = self.core.beams
        sandbags = self.core.sandbags

        # 2. 通常ノード球体生成
        node_objs = NodeBuilder(normal_nodes, radius=SPHERE_RADIUS).run()

        # 3. サンドバッグ生成 (Empty + Armature)
        sandbag_objs = SandbagBuilder(sandbags).build()

        # 4. パネル生成
        panel_objs = PanelBuilder(panels).build() if panels else []

        # 5. 屋根生成
        positions = {n.id: n.pos for n in normal_nodes.values()}
        for n in self.core.sandbag_nodes.values():
            positions[n.id] = n.pos
        roof_obj, roof_quads = RoofBuilder(positions).run()

        # 6. 部材生成（柱＋梁）
        col_map = ColumnBuilder(positions, column_edges, thickness=0.5).run()
        beam_map = BeamBuilder(positions, beam_edges, thickness=0.5).run()
        member_objs = [
            (obj, int(key.split("_")[0]), int(key.split("_")[1]))
            for key, obj in {**col_map, **beam_map}.items()
        ]

        # 7. 地面生成
        ground_obj = GroundBuilder().run() if self.include_ground else None

        # サマリー出力
        summary = (
            f"SceneBuilder Summary: Nodes={len(node_objs)}, "
            f"Sandbags={len(sandbag_objs)}, "
            f"Panels={len(panel_objs)}, RoofQuads={len(roof_quads)}, "
            f"Members={len(member_objs)}, Ground={'Yes' if ground_obj else 'No'}"
        )
        log.info(summary)

        return (
            node_objs,
            sandbag_objs,
            panel_objs,
            roof_obj,
            roof_quads,
            member_objs,
            ground_obj,
        )
