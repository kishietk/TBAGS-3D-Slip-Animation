"""
コアモデル生成クラス
- ロード済みノード/エッジ/種別情報から構造グラフの基礎モデル（Node/SandbagNode/Edge/Beam/Column/Panel）を構築
- 全リスト管理＋API

【設計方針】
- データクラス(NodeData/EdgeData)→コアオブジェクト(Node, SandbagNode, Panel, Edge…)化
- kind_idによりSandbag/通常ノードや梁/柱/Edge分類を一元化
- 内部格納: self.nodes, self.edges, self.panels
- get_xxx()でリスト/辞書を取得
"""

from typing import Dict, List, Optional
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

log = setup_logging()


class coreConstructer:
    """
    コアモデル（構造グラフ）自動構築クラス
    - nodes/edges/panelsの構築・API・属性保持
    """

    def __init__(
        self,
        nodes_data: Dict[int, NodeData],
        edges_data: List[EdgeData],
        panel_node_kind_ids: Optional[List[int]] = None,
    ) -> None:
        """
        Core全構成（ノード・エッジ・パネル）初期化
        Args:
            nodes_data (Dict[int, NodeData]): ローダ提供のノード情報
            edges_data (List[EdgeData]): ローダ提供のエッジ情報
            panel_node_kind_ids (Optional[List[int]]): パネル候補kind_id
        Returns:
            None
        """
        self.panel_node_kind_ids = (
            panel_node_kind_ids
            if panel_node_kind_ids is not None
            else WALL_NODE_KIND_IDS
        )
        self.nodes: Dict[int, Node | SandbagNode] = {}
        self.edges: List[Edge] = []
        self.panels: List[Panel] = []
        self._construct_core_all(nodes_data, edges_data)

    def _construct_core_all(self, nodes_data, edges_data) -> None:
        self.nodes = self._construct_core_nodes(nodes_data)
        self.edges = self._construct_core_edges(edges_data, self.nodes)
        self.panels = self._construct_core_panels(self.nodes, self.panel_node_kind_ids)
        log.info(
            f"CoreManager build completed: {len(self.nodes)} nodes, {len(self.edges)} edges, {len(self.panels)} panels"
        )

    def _construct_core_nodes(
        self, nodes_data: Dict[int, NodeData]
    ) -> Dict[int, Node | SandbagNode]:
        """
        kind_idでSandbag/Nodeを自動判別生成
        Args:
            nodes_data (Dict[int, NodeData]): ローダ提供ノード情報
        Returns:
            Dict[int, Node | SandbagNode]
        """
        node_map: Dict[int, Node | SandbagNode] = {}
        for nid, data in nodes_data.items():
            kind_id = data.kind_id
            pos = data.pos
            # kind_id=0はSB兼柱としてSandbagNodeのみ登録
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
        self, edges_data: List[EdgeData], node_map: Dict[int, Node | SandbagNode]
    ) -> List[Edge]:
        """
        kind_idでEdge/Beam/Columnを生成
        Args:
            edges_data (List[EdgeData]): ローダ提供エッジ
            node_map (Dict[int, Node | SandbagNode]): ノードID辞書
        Returns:
            List[Edge]
        """
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
        node_map: Dict[int, Node | SandbagNode],
        panel_node_kind_ids: List[int],
    ) -> List[Panel]:
        """
        PanelData→Panelへ変換（グラフオブジェクト構築）
        Args:
            node_map (Dict[int, Node | SandbagNode]): ノードID辞書
            panel_node_kind_ids (List[int]): パネル候補kind_id
        Returns:
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

    def get_nodes(self, ids: Optional[List[int]] = None) -> List[Node | SandbagNode]:
        """
        ノードリスト返却API
        Args:
            ids (Optional[List[int]]): 指定IDのみ返す
        Returns:
            List[Node | SandbagNode]
        """
        if ids is None:
            return list(self.nodes.values())
        return [self.nodes[i] for i in ids if i in self.nodes]

    def get_edges(self, kind_ids: Optional[List[int]] = None) -> List[Edge]:
        """
        エッジリスト返却API（種別フィルタ）
        Args:
            kind_ids (Optional[List[int]]): 種別ID
        Returns:
            List[Edge]
        """
        if kind_ids is None:
            return self.edges
        return [e for e in self.edges if getattr(e, "kind_id", None) in kind_ids]

    def get_columns(self) -> List[tuple[int, int]]:
        """
        柱（Column）IDペアリスト取得
        Returns:
            List[Tuple[int, int]]
        """
        from configs import COLUMNS_KIND_IDS

        return [
            (e.node_a.id, e.node_b.id)
            for e in self.edges
            if e.kind_id in COLUMNS_KIND_IDS
        ]

    def get_beams(self) -> List[tuple[int, int]]:
        """
        梁（Beam）IDペアリスト取得
        Returns:
            List[Tuple[int, int]]
        """
        from configs import BEAMS_KIND_IDS

        return [
            (e.node_a.id, e.node_b.id)
            for e in self.edges
            if e.kind_id in BEAMS_KIND_IDS
        ]

    def get_panels(self) -> List[Panel]:
        """
        パネルリスト返却
        Returns:
            List[Panel]
        """
        return self.panels

    def summary(self) -> str:
        """
        コア要素数のサマリー
        Returns:
            str
        """
        return f"Nodes: {len(self.nodes)}, Edges: {len(self.edges)}, Panels: {len(self.panels)}"
