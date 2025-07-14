from typing import Dict, List, Tuple, Any
from utils import setup_logging
from configs import (
    WALL_NODE_KIND_IDS,
    COLUMNS_KIND_IDS,
    BEAMS_KIND_IDS,
)
from entities import Node, Edge, Roof, Panel as BasePanel
from cores.core_registry import get_core_class
from utils.make_panel_unit import make_panel_unit
from parsers import NodeData, EdgeData

log = setup_logging("CoreFactory")


class CoreFactory:
    """
    ロード済みデータからコアモデルを構築・一元管理するクラス。

    Attributes:
        nodes: Dict[int, Node]
        edges: List[Edge]
        panels: List[BasePanel or Roof]
    """

    def __init__(
        self,
        nodes_data: Dict[int, NodeData],
        edges_data: List[EdgeData],
    ) -> None:
        # コア要素初期化
        self._nodes: Dict[int, Node] = {}
        self._edges: List[Edge] = []
        self._panels: List[BasePanel] = []

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
    def columns(self) -> List[Edge]:
        """
        COLUMNS_KIND_IDS に該当する Edge インスタンスのリストを返す
        """
        return [
            e
            for e in self._edges
            if hasattr(e, "kind_id") and e.kind_id in COLUMNS_KIND_IDS
        ]

    @property
    def beams(self) -> List[Edge]:
        """
        BEAMS_KIND_IDS に該当する Edge インスタンスのリストを返す
        """
        return [
            e
            for e in self._edges
            if hasattr(e, "kind_id") and e.kind_id in BEAMS_KIND_IDS
        ]

    @property
    def panels(self) -> List[BasePanel]:
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
            cls = get_core_class(getattr(e, "kind_id", None)) or Edge
            edges.append(
                cls(a, b, getattr(e, "kind_id", None), getattr(e, "kind_label", ""))
            )
        return edges

    def _construct_core_panels(self) -> List[BasePanel]:
        panel_data_list = make_panel_unit(
            node_map=self._nodes,
            panel_node_kind_ids=WALL_NODE_KIND_IDS,
        )

        panel_instances: List[BasePanel] = []
        for pd in panel_data_list:
            # 屋根パネルは Roof クラス、それ以外は BasePanel
            cls = Roof if getattr(pd, "kind", None) == "roof" else BasePanel
            panel = cls(
                nodes=[self._nodes[nid] for nid in pd.node_ids],
                kind=getattr(pd, "kind", None),
                floor=getattr(pd, "floor", None),
                attributes=getattr(pd, "attributes", {}),
            )
            panel_instances.append(panel)
        return panel_instances
