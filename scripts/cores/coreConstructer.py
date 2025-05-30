from typing import Dict, List, Optional, TYPE_CHECKING
from mathutils import Vector
from utils.logging_utils import setup_logging
from config import (
    SANDBAG_NODE_KIND_IDS,
    EPS_XY_MATCH,
    WALL_NODE_KIND_IDS,
    COLUMNS_KIND_IDS,
    BEAMS_KIND_IDS,
)
from cores.node import Node
from cores.sandbag import SandbagNode
from cores.edge import Edge
from cores.beam import Beam
from cores.column import Column
from cores.panel import Panel
from loaders.node_loader import NodeData
from loaders.edge_loader import EdgeData
from cores.makePanelsList import make_panels_list, PanelData

log = setup_logging()


class coreConstructer:
    def __init__(
        self,
        nodes_data: Dict[
            int, NodeData
        ],  # LoaderManagerから渡されるデータ（NodeData型辞書）
        edges_data: List[
            EdgeData
        ],  # LoaderManagerから渡されるデータ（EdgeData型リスト）
        panel_node_kind_ids: Optional[List[int]] = None,
    ):
        self.panel_node_kind_ids = (
            panel_node_kind_ids
            if panel_node_kind_ids is not None
            else WALL_NODE_KIND_IDS
        )
        self.nodes: Dict[int, Node | SandbagNode] = {}
        self.edges: List[Edge] = []
        self.panels: List[Panel] = []
        self._construct_core_all(nodes_data, edges_data)

    def _construct_core_all(self, nodes_data, edges_data):
        self.nodes = self._construct_core_nodes(nodes_data)
        self.edges = self._construct_core_edges(edges_data, self.nodes)
        self.panels = self._construct_core_panels(self.nodes, self.panel_node_kind_ids)
        log.info(
            f"CoreManager build completed: {len(self.nodes)} nodes, {len(self.edges)} edges, {len(self.panels)} panels"
        )

    # def _construct_core_nodes(
    #     self, nodes_data: Dict[int, NodeData]
    # ) -> Dict[int, Node | SandbagNode]:
    #     node_map: Dict[int, Node | SandbagNode] = {}
    #     for nid, data in nodes_data.items():
    #         kind_id = data.kind_id
    #         pos = data.pos
    #         if kind_id is not None and kind_id in SANDBAG_NODE_KIND_IDS:
    #             node_map[nid] = SandbagNode(nid, pos, kind_id=kind_id)
    #         else:
    #             node_map[nid] = Node(nid, pos, kind_id=kind_id)
    #         log.debug(
    #             f"Loaded Node {nid}: {pos}, kind_id={kind_id}, type={type(node_map[nid]).__name__}"
    #         )
    #     return node_map

    def _construct_core_nodes(self, nodes_data: Dict[int, NodeData]) -> Dict[int, Node | SandbagNode]:
        node_map: Dict[int, Node | SandbagNode] = {}
        for nid, data in nodes_data.items():
            kind_id = data.kind_id
            pos = data.pos
            # kind_id=0はSB兼柱としてSandbagNodeのみ登録
            if kind_id == 0 or (kind_id is not None and kind_id in SANDBAG_NODE_KIND_IDS):
                node_map[nid] = SandbagNode(nid, pos, kind_id=kind_id)
            else:
                node_map[nid] = Node(nid, pos, kind_id=kind_id)
            log.info(
                f"Loaded Node {nid}: {pos}, kind_id={kind_id}, type={type(node_map[nid]).__name__}"
            )
        return node_map


    def _construct_core_edges(
        self, edges_data: List[EdgeData], node_map: Dict[int, Node | SandbagNode]
    ) -> List[Edge]:
        edges: List[Edge] = []
        for e in edges_data:
            node_a = node_map.get(e.node_a)
            node_b = node_map.get(e.node_b)
            kind_id = e.kind_id
            kind_label = e.kind_label
            # ここでBeam/Column/Edgeに分岐
            if kind_id in COLUMNS_KIND_IDS:
                edges.append(Column(node_a, node_b, kind_id, kind_label))
            elif kind_id in BEAMS_KIND_IDS:
                edges.append(Beam(node_a, node_b, kind_id, kind_label))
            else:
                edges.append(Edge(node_a, node_b, kind_id, kind_label))
        return edges

    def _construct_core_panels(
        self,
        node_map: Dict[int, NodeData],
        panel_node_kind_ids: List[int],
    ) -> List[Panel]:
        """
        コアパネル生成の呼び出し
        - node_map: ノードID → NodeData
        - edges_data: EdgeDataリスト
        - panel_node_kind_ids: パネル種別IDリスト
        """
        # PanelDataリストを生成
        panel_data = make_panels_list(
            node_map=node_map,
            panel_node_kind_ids=panel_node_kind_ids,
        )

        # PanelData → Panel（コアモデル）へ変換
        panels = []
        for pd in panel_data:
            panel_nodes = [node_map[nid] for nid in pd.node_ids]
            panel = Panel(
                panel_nodes, kind=pd.kind, floor=pd.floor, attributes=pd.attributes
            )
            panels.append(panel)

        return panels

    def get_nodes(self, ids: Optional[List[int]] = None):
        if ids is None:
            return list(self.nodes.values())
        return [self.nodes[i] for i in ids if i in self.nodes]

    def get_edges(self, kind_ids: Optional[List[int]] = None) -> List[Edge]:
        if kind_ids is None:
            return self.edges
        return [e for e in self.edges if getattr(e, "kind_id", None) in kind_ids]

    def get_columns(self):
        from config import COLUMNS_KIND_IDS

        return [
            (e.node_a.id, e.node_b.id)
            for e in self.edges
            if e.kind_id in COLUMNS_KIND_IDS
        ]

    def get_beams(self):
        from config import BEAMS_KIND_IDS

        return [
            (e.node_a.id, e.node_b.id)
            for e in self.edges
            if e.kind_id in BEAMS_KIND_IDS
        ]

    def get_panels(self) -> List[Panel]:
        return self.panels

    def summary(self) -> str:
        return f"Nodes: {len(self.nodes)}, Edges: {len(self.edges)}, Panels: {len(self.panels)}"
