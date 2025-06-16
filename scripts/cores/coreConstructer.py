"""
責務:
- ロード済みノード/エッジ/種別情報から構造グラフの基礎モデル（Node, Edge, Beam, Column, Panel, SandbagUnit）を構築。
- 全要素を一元管理し、APIで各種リストやサマリーを提供。

設計方針:
- データクラス（Node/Edge）→コアオブジェクト群への変換
- kind_idによるSandbag/通常ノード、梁/柱/Edge分類を一元化
- SandbagUnitは4ノードをペアリングして生成
"""

from typing import Dict, List, Optional, Union
from configs import (
    WALL_NODE_KIND_IDS,
    COLUMNS_KIND_IDS,
    BEAMS_KIND_IDS,
)
from cores.nodeCore import Node
from cores.edgeCore import Edge
from cores.beamCore import Beam
from cores.columnCore import Column
from cores.panelCore import Panel
from loaders.structureParser import NodeData, EdgeData
from cores.makePanelsList import make_panels_list
from cores.sandbagUnit import SandbagUnit, pair_sandbag_nodes  # ←追加
from utils.logging_utils import setup_logging

log = setup_logging("coreConstructer")


class coreConstructer:
    """
    役割:
        ロード済みノード/エッジ情報からコア構造グラフ（Node, Edge, Beam, Column, Panel, SandbagUnit）を自動構築・一元管理。
        各種リスト/辞書の取得APIや要素数サマリーも提供。
    属性:
        nodes (Dict[int, Node])
        edges (List[Edge])
        panels (List[Panel])
        sandbags (List[SandbagUnit])
    """

    def __init__(
        self,
        nodes_data: Dict[int, NodeData],
        edges_data: List[EdgeData],
        panel_node_kind_ids: Optional[List[int]] = None,
    ) -> None:
        self.panel_node_kind_ids = panel_node_kind_ids or WALL_NODE_KIND_IDS
        self.nodes: Dict[int, Node] = {}
        self.edges: List[Edge] = []
        self.panels: List[Panel] = []
        self.sandbags: List[SandbagUnit] = []
        self._construct_core_all(nodes_data, edges_data)

    def _construct_core_all(self, nodes_data, edges_data) -> None:
        log.info("=================[コアモデルを構築]=========================")
        self.nodes = self._construct_core_nodes(nodes_data)
        self.edges = self._construct_core_edges(edges_data, self.nodes)
        self.panels = self._construct_core_panels(self.nodes, self.panel_node_kind_ids)
        self.sandbags = pair_sandbag_nodes(self.nodes)
        log.info(
            f"ノード：{len(self.nodes)}件、 エッジ：{len(self.edges)}件、 パネル：{len(self.panels)}件、サンドバッグ：{len(self.sandbags)}件のコア要素を構築しました。"
        )

    def _construct_core_nodes(self, nodes_data: Dict[int, NodeData]) -> Dict[int, Node]:
        node_map: Dict[int, Node] = {}
        for nid, data in nodes_data.items():
            node_map[nid] = Node(nid, data.pos, kind_id=data.kind_id)
            log.debug(
                f"Loaded Node {nid}: {data.pos}, kind_id={data.kind_id}, type={type(node_map[nid]).__name__}"
            )
        return node_map

    def _construct_core_edges(
        self, edges_data: List[EdgeData], node_map: Dict[int, Node]
    ) -> List[Edge]:
        edges: List[Edge] = []
        for e in edges_data:
            node_a = node_map.get(e.node_a)
            node_b = node_map.get(e.node_b)
            kind_id = e.kind_id
            kind_label = e.kind_label
            if kind_id in COLUMNS_KIND_IDS:
                edges.append(Column(node_a, node_b, kind_id, kind_label))
            elif kind_id in BEAMS_KIND_IDS:
                edges.append(Beam(node_a, node_b, kind_id, kind_label))
            else:
                edges.append(Edge(node_a, node_b, kind_id, kind_label))
        return edges

    def _construct_core_panels(
        self,
        node_map: Dict[int, Node],
        panel_node_kind_ids: List[int],
    ) -> List[Panel]:
        panel_data = make_panels_list(
            node_map=node_map,
            panel_node_kind_ids=panel_node_kind_ids,
        )
        panels = []
        for pd in panel_data:
            panel_nodes = [node_map[nid] for nid in pd.node_ids]
            panel = Panel(
                panel_nodes, kind=pd.kind, floor=pd.floor, attributes=pd.attributes
            )
            panels.append(panel)
        return panels

    def get_nodes(self, ids: Optional[List[int]] = None) -> List[Node]:
        if ids is None:
            return list(self.nodes.values())
        return [self.nodes[i] for i in ids if i in self.nodes]

    def get_edges(self, kind_ids: Optional[List[int]] = None) -> List[Edge]:
        if kind_ids is None:
            return self.edges
        return [e for e in self.edges if getattr(e, "kind_id", None) in kind_ids]

    def get_columns(self) -> List[tuple[int, int]]:
        return [
            (e.node_a.id, e.node_b.id)
            for e in self.edges
            if e.kind_id in COLUMNS_KIND_IDS
        ]

    def get_beams(self) -> List[tuple[int, int]]:
        return [
            (e.node_a.id, e.node_b.id)
            for e in self.edges
            if e.kind_id in BEAMS_KIND_IDS
        ]

    def get_panels(self) -> List[Panel]:
        return self.panels

    def get_sandbags(self) -> List[SandbagUnit]:
        return self.sandbags

    def summary(self) -> str:
        return f"Nodes: {len(self.nodes)}, Edges: {len(self.edges)}, Panels: {len(self.panels)}, Sandbags: {len(self.sandbags)}"
