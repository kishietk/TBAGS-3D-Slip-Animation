"""
ファイル名: cores/coreConstructer.py

責務:
- ロード済みノード/エッジ/種別情報から構造グラフの基礎モデル（Node, SandbagNode, Edge, Beam, Column, Panel）を構築する。
- コア全要素を一元管理し、APIで各種リストやサマリーを提供。

設計方針:
- データクラス（NodeData/EdgeData）→コアオブジェクト群への変換
- kind_idによるSandbag/通常ノード、梁/柱/Edge分類を一元化
- 全要素はself.nodes, self.edges, self.panelsに格納
- get_xxx()でAPIとして各種取得
"""

from typing import Dict, List, Optional, Union
from utils.logging_utils import setup_logging
from configs import (
    SANDBAG_NODE_KIND_IDS,
    WALL_NODE_KIND_IDS,
    COLUMNS_KIND_IDS,
    BEAMS_KIND_IDS,
)
from cores.nodeCore import Node
from cores.sandbagCore import SandbagNode
from cores.edgeCore import Edge
from cores.beamCore import Beam
from cores.columnCore import Column
from cores.panelCore import Panel
from loaders.nodeLoader import NodeData
from loaders.edgeLoader import EdgeData
from cores.makePanelsList import make_panels_list, PanelData

log = setup_logging("coreConstructer")


class coreConstructer:
    """
    役割:
        ロード済みノード/エッジ情報からコア構造グラフ（Node, SandbagNode, Edge, Beam, Column, Panel）を自動構築・一元管理。
        各種リスト/辞書の取得APIや要素数サマリーも提供。

    属性:
        panel_node_kind_ids (List[int]): パネル候補のkind_idリスト
        nodes (Dict[int, Node | SandbagNode]): コアノード辞書
        edges (List[Edge]): コアエッジリスト
        panels (List[Panel]): コアパネルリスト
    """

    def __init__(
        self,
        nodes_data: Dict[int, NodeData],
        edges_data: List[EdgeData],
        panel_node_kind_ids: Optional[List[int]] = None,
    ) -> None:
        """
        役割:
            ノード・エッジ・パネルのコアオブジェクトを初期化・構築する。
        引数:
            nodes_data (Dict[int, NodeData]): ノード情報
            edges_data (List[EdgeData]): エッジ情報
            panel_node_kind_ids (Optional[List[int]]): パネル候補kind_idリスト
        返り値:
            なし
        """
        self.panel_node_kind_ids = panel_node_kind_ids or WALL_NODE_KIND_IDS
        self.nodes: Dict[int, Union[Node, SandbagNode]] = {}
        self.edges: List[Edge] = []
        self.panels: List[Panel] = []
        self._construct_core_all(nodes_data, edges_data)

    def _construct_core_all(self, nodes_data, edges_data) -> None:
        """
        役割:
            コアモデルの全要素（ノード・エッジ・パネル）を構築。
        """
        log.info("=================[コアモデルを構築]=========================")
        self.nodes = self._construct_core_nodes(nodes_data)
        self.edges = self._construct_core_edges(edges_data, self.nodes)
        self.panels = self._construct_core_panels(self.nodes, self.panel_node_kind_ids)
        log.info(
            f"ノード：{len(self.nodes)}件、 エッジ：{len(self.edges)}件、 パネル：{len(self.panels)}件のコア要素を構築しました。"
        )

    def _construct_core_nodes(
        self, nodes_data: Dict[int, NodeData]
    ) -> Dict[int, Union[Node, SandbagNode]]:
        """
        役割:
            kind_idでSandbag/Nodeを判別してコアノードを生成。
        引数:
            nodes_data (Dict[int, NodeData])
        返り値:
            Dict[int, Node | SandbagNode]
        """
        node_map: Dict[int, Union[Node, SandbagNode]] = {}
        for nid, data in nodes_data.items():
            kind_id = data.kind_id
            pos = data.pos
            if kind_id == 0 or (
                kind_id is not None and kind_id in SANDBAG_NODE_KIND_IDS
            ):
                node_map[nid] = SandbagNode(nid, pos, kind_id=kind_id)
            else:
                node_map[nid] = Node(nid, pos, kind_id=kind_id)
            log.debug(
                f"Loaded Node {nid}: {pos}, kind_id={kind_id}, type={type(node_map[nid]).__name__}"
            )
        return node_map

    def _construct_core_edges(
        self, edges_data: List[EdgeData], node_map: Dict[int, Union[Node, SandbagNode]]
    ) -> List[Edge]:
        """
        役割:
            kind_idでEdge/Beam/Columnを自動生成してリスト化。
        引数:
            edges_data (List[EdgeData])
            node_map (Dict[int, Node | SandbagNode])
        返り値:
            List[Edge]
        """
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
        node_map: Dict[int, Union[Node, SandbagNode]],
        panel_node_kind_ids: List[int],
    ) -> List[Panel]:
        """
        役割:
            PanelData→Panelへ変換（グラフオブジェクトとして構築）
        引数:
            node_map (Dict[int, Node | SandbagNode])
            panel_node_kind_ids (List[int])
        返り値:
            List[Panel]
        """
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

    def get_nodes(
        self, ids: Optional[List[int]] = None
    ) -> List[Union[Node, SandbagNode]]:
        """
        役割:
            コアノードのリストを返却。ids指定時はそのIDのみ返す。
        引数:
            ids (Optional[List[int]])
        返り値:
            List[Node | SandbagNode]
        """
        if ids is None:
            return list(self.nodes.values())
        return [self.nodes[i] for i in ids if i in self.nodes]

    def get_edges(self, kind_ids: Optional[List[int]] = None) -> List[Edge]:
        """
        役割:
            コアエッジのリストを返却。kind_ids指定時はその種別IDのみ返す。
        引数:
            kind_ids (Optional[List[int]])
        返り値:
            List[Edge]
        """
        if kind_ids is None:
            return self.edges
        return [e for e in self.edges if getattr(e, "kind_id", None) in kind_ids]

    def get_columns(self) -> List[tuple[int, int]]:
        """
        役割:
            柱（Column）のIDペアリストを取得。
        返り値:
            List[Tuple[int, int]]
        """
        return [
            (e.node_a.id, e.node_b.id)
            for e in self.edges
            if e.kind_id in COLUMNS_KIND_IDS
        ]

    def get_beams(self) -> List[tuple[int, int]]:
        """
        役割:
            梁（Beam）のIDペアリストを取得。
        返り値:
            List[Tuple[int, int]]
        """
        return [
            (e.node_a.id, e.node_b.id)
            for e in self.edges
            if e.kind_id in BEAMS_KIND_IDS
        ]

    def get_panels(self) -> List[Panel]:
        """
        役割:
            コアパネルのリストを返却。
        返り値:
            List[Panel]
        """
        return self.panels

    def summary(self) -> str:
        """
        役割:
            コア要素（ノード・エッジ・パネル）数のサマリーを返す。
        返り値:
            str
        """
        return f"Nodes: {len(self.nodes)}, Edges: {len(self.edges)}, Panels: {len(self.panels)}"
