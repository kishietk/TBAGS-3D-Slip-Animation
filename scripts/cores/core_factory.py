# cores/constructors/core_factory.py
from typing import Dict, List
from utils import setup_logging
from configs import (
    WALL_NODE_KIND_IDS,
    COLUMNS_KIND_IDS,
    BEAMS_KIND_IDS,
)
from cores.entities import Node, Edge, Beam, Column, Panel
from .constructors.make_panel_unit import make_panel_unit
from parsers import NodeData, EdgeData

log = setup_logging("CoreFactory")


class CoreFactory:
    """
    ロード済みデータからコアモデルを構築・一元管理するクラス。

    Attributes:
        nodes: Dict[int, Node]
        edges: List[Edge]
        panels: List[Panel]
    """

    def __init__(
        self,
        nodes_data: Dict[int, NodeData],
        edges_data: List[EdgeData],
    ) -> None:
        # コア要素初期化
        self._nodes: Dict[int, Node] = {}
        self._edges: List[Edge] = []
        self._panels: List[Panel] = []

        log.info(
            f"Initializing CoreFactory with {len(nodes_data)} nodes and {len(edges_data)} edges"
        )
        self._construct_core_all(nodes_data, edges_data)
        log.info(f"CoreFactory initialized: {self.summary()}")

    def _construct_core_all(
        self,
        nodes_data: Dict[int, NodeData],
        edges_data: List[EdgeData],
    ) -> None:
        log.info("=================[コアモデルを構築]=========================")
        self._nodes = self._construct_core_nodes(nodes_data)
        self._edges = self._construct_core_edges(edges_data, self._nodes)
        self._panels = self._construct_core_panels()

    @property
    def nodes(self) -> Dict[int, Node]:
        return self._nodes

    @property
    def edges(self) -> List[Edge]:
        return self._edges

    @property
    def columns(self) -> List[tuple[int, int]]:
        return [
            (e.node_a.id, e.node_b.id)
            for e in self._edges
            if e.kind_id in COLUMNS_KIND_IDS
        ]

    @property
    def beams(self) -> List[tuple[int, int]]:
        return [
            (e.node_a.id, e.node_b.id)
            for e in self._edges
            if e.kind_id in BEAMS_KIND_IDS
        ]

    @property
    def panels(self) -> List[Panel]:
        return self._panels

    def summary(self) -> str:
        return f"Nodes: {len(self.nodes)}, Edges: {len(self.edges)}, Panels: {len(self.panels)}"

    def _construct_core_nodes(
        self,
        nodes_data: Dict[int, NodeData],
    ) -> Dict[int, Node]:
        node_map: Dict[int, Node] = {}
        for nid, data in nodes_data.items():
            node_map[nid] = Node(nid, data.pos, kind_id=data.kind_id)
            log.debug(f"Loaded Node {nid}: pos={data.pos}, kind_id={data.kind_id}")
        return node_map

    def _construct_core_edges(
        self,
        edges_data: List[EdgeData],
        node_map: Dict[int, Node],
    ) -> List[Edge]:
        edges: List[Edge] = []
        for e in edges_data:
            a = node_map.get(e.node_a)
            b = node_map.get(e.node_b)
            if e.kind_id in COLUMNS_KIND_IDS:
                edges.append(Column(a, b, e.kind_id, e.kind_label))
            elif e.kind_id in BEAMS_KIND_IDS:
                edges.append(Beam(a, b, e.kind_id, e.kind_label))
            else:
                edges.append(Edge(a, b, e.kind_id, e.kind_label))
        return edges

    def _construct_core_panels(self) -> List[Panel]:
        panel_data_list = make_panel_unit(
            node_map=self._nodes,
            panel_node_kind_ids=WALL_NODE_KIND_IDS,
        )
        from cores.entities.panel_core import Panel

        return [
            Panel(
                nodes=[self._nodes[nid] for nid in pd.node_ids],
                kind=pd.kind,
                floor=pd.floor or None,
                attributes=pd.attributes,
            )
            for pd in panel_data_list
        ]
