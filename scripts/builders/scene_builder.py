from typing import Dict, List, Tuple, Optional, Any
from utils import setup_logging
from builders.base import BuilderBase
from builders.object_builders import (
    NodeBuilder,
    PanelBuilder,
    RoofBuilder,
    ColumnBuilder,
    BeamBuilder,
    GroundBuilder,
)
from configs import SPHERE_RADIUS
import bpy

log = setup_logging("SceneBuilder")


class SceneBuilder(BuilderBase):
    def __init__(self, core: Any, include_ground: bool = True):
        super().__init__()
        self.core = core
        self.include_ground = include_ground

    def build(
        self,
    ) -> Tuple[
        Dict[int, bpy.types.Object],
        List[bpy.types.Object],
        Optional[bpy.types.Object],
        List[Tuple[int, int, int, int]],
        List[Tuple[bpy.types.Object, int, int]],
        Optional[bpy.types.Object],
    ]:
        # Coreから取得
        nodes = self.core.nodes or {}
        panels = self.core.panels or []
        columns = self.core.columns or []  # List[EdgeData]
        beams = self.core.beams or []  # List[EdgeData]

        # 1. ノード生成
        node_objs = NodeBuilder(nodes, radius=SPHERE_RADIUS).build()

        # 2. パネル生成
        panel_objs = PanelBuilder(panels).build()

        # 3. 座標マッピング
        positions = {nid: data.pos for nid, data in nodes.items()}

        # 4. 屋根生成
        roof_obj, roof_quads = RoofBuilder(positions).build()

        # 5. 柱・梁生成
        # EdgeData -> (start, end)
        col_edges = {(e.node_a, e.node_b) for e in columns}
        beam_edges = {(e.node_a, e.node_b) for e in beams}
        col_map = ColumnBuilder(positions, col_edges, thickness=0.5).build()
        beam_map = BeamBuilder(positions, beam_edges, thickness=0.5).build()
        member_objs = [
            (obj, *map(int, key.split("_")))
            for key, obj in {**col_map, **beam_map}.items()
        ]

        # 6. 地面生成
        ground_obj = GroundBuilder().build() if self.include_ground else None

        # 7. サマリー
        summary = (
            f"SceneBuilder Summary: Nodes={len(node_objs)}, Panels={len(panel_objs)}, "
            f"RoofQuads={len(roof_quads)}, Members={len(member_objs)}, "
            f"Ground={'Yes' if ground_obj else 'No'}"
        )
        log.info(summary)

        return node_objs, panel_objs, roof_obj, roof_quads, member_objs, ground_obj
