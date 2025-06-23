# builders/scene_builders/scene_builder.py

"""
ファイル名: builders/scene_builders/scene_builder.py

責務:
- コアモデル（Node/SandbagNode/Panel…）から Blender 用表示オブジェクト群を一括生成。
- kind_id で通常ノード／サンドバッグノードを自動仕分けし、各 Builder クラスに委譲。
- 生成物（ノード球、サンドバッグ基点Empty、サンドバッグユニット、パネル、屋根、柱、梁、地面）を返却。

注意:
- column_edges, beam_edges は Edge 情報を渡す。
- nodes 引数は dict or list を受け付ける。
"""
from typing import Any, Dict, List, Tuple, Union, Optional
from utils.logging_utils import setup_logging
from builders.base import BuilderBase
from builders.object_builders import (
    NodeBuilder,
    SandbagBuilder,
    SandbagUnitsBuilder,
    PanelBuilder,
    RoofBuilder,
    ColumnBuilder,
    BeamBuilder,
    GroundBuilder,
)
from cores.sandbagUnit import pair_sandbag_nodes
from configs import (
    SANDBAG_NODE_KIND_IDS,
    SPHERE_RADIUS,
    SANDBAG_FACE_SIZE,
    SANDBAG_BAR_THICKNESS,
)

log = setup_logging("SceneBuilder")


class SceneBuilder(BuilderBase):
    def __init__(
        self,
        nodes: Union[Dict[int, Any], List[Any]],
        column_edges: List[Tuple[int, int]],
        beam_edges: List[Tuple[int, int]],
        panels: Optional[List[Any]] = None,
        sandbag_face_size: Tuple[float, float] = SANDBAG_FACE_SIZE,
        sandbag_bar_thickness: float = SANDBAG_BAR_THICKNESS,
        include_ground: bool = True,
    ):
        super().__init__()
        self.nodes_data = nodes
        self.column_edges = column_edges
        self.beam_edges = beam_edges
        self.panels_data = panels or []
        self.sandbag_face_size = sandbag_face_size
        self.sandbag_bar_thickness = sandbag_bar_thickness
        self.include_ground = include_ground

    def build(self) -> Tuple[
        Dict[int, Any],  # node_objs
        Dict[int, Any],  # sandbag_base_objs (Empty)
        List[Any],  # panel_objs
        Any,  # roof_obj
        List[Tuple[int, int, int, int]],  # roof_quads
        List[Tuple[Any, int, int]],  # member_objs
        Any,  # ground_obj
    ]:
        # 0) ノード iterable 作成
        iterable = (
            self.nodes_data.values()
            if isinstance(self.nodes_data, dict)
            else self.nodes_data
        )

        # kind_id で通常／サンドバッグノードを振り分け
        normal_nodes: Dict[int, Any] = {}
        sandbag_nodes: Dict[int, Any] = {}
        for n in iterable:
            if getattr(n, "kind_id", None) in SANDBAG_NODE_KIND_IDS:
                sandbag_nodes[n.id] = n
            else:
                normal_nodes[n.id] = n

        # 1) 通常ノード球体生成
        node_objs = NodeBuilder(normal_nodes, radius=SPHERE_RADIUS).run()

        # 2) サンドバッグ基点 Empty 生成 ← 修正点
        cube_size = (
            self.sandbag_face_size[0],
            self.sandbag_face_size[1],
            self.sandbag_bar_thickness,
        )
        # run() が返す Dict[int, Object] は「基点 Empty」を指します
        sandbag_base_objs = SandbagBuilder(sandbag_nodes, cube_size=cube_size).run()

        # 3) サンドバッグユニット生成
        sandbag_units_list = pair_sandbag_nodes({**normal_nodes, **sandbag_nodes})
        units_map: Dict[int, List[int]] = {
            int(unit.id): [n.id for n in unit.nodes] for unit in sandbag_units_list
        }
        sandbag_unit_objs = (
            SandbagUnitsBuilder(units_map, sandbag_base_objs).run() if units_map else {}
        )

        # 4) パネル生成
        panel_objs = PanelBuilder(self.panels_data).run() if self.panels_data else []

        # 5) 屋根生成
        all_positions = {
            **{nid: n.pos for nid, n in normal_nodes.items()},
            **{nid: n.pos for nid, n in sandbag_nodes.items()},
        }
        roof_obj, roof_quads = RoofBuilder(all_positions).run()

        # 6) 構造部材生成 (柱・梁を start_id, end_id と共に保持)
        col_map = ColumnBuilder(all_positions, self.column_edges, thickness=0.5).run()
        beam_map = BeamBuilder(all_positions, self.beam_edges, thickness=0.5).run()
        member_objs = [
            (obj, int(key.split("_")[0]), int(key.split("_")[1]))
            for key, obj in {**col_map, **beam_map}.items()
        ]

        # 7) 地面生成
        ground_obj = GroundBuilder().run() if self.include_ground else None

        # ===== 全体サマリー =====
        summary = (
            f"SceneBuilder Summary: "
            f"Nodes={len(node_objs)}, "
            f"Sandbag Empties={len(sandbag_base_objs)}, "
            f"Units={len(sandbag_unit_objs)}, "
            f"Panels={len(panel_objs)}, "
            f"RoofQuads={len(roof_quads)}, "
            f"Members={len(member_objs)}, "
            f"Ground={'Yes' if ground_obj else 'No'}"
        )
        log.info(summary)

        return (
            node_objs,
            sandbag_base_objs,
            panel_objs,
            roof_obj,
            roof_quads,
            member_objs,
            ground_obj,
        )
