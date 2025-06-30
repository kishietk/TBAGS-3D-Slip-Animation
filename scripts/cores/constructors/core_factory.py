# cores/CoreFactory.py

"""
ファイル名: cores/CoreFactory.py

責務:
    - ロード済みノード/エッジ情報からコア構造グラフを自動構築・管理。
        （Node, Edge, Beam, Column, Panel, Sandbag）
    - 各コア要素のリスト/辞書取得API提供およびサマリー生成。

設計方針:
    - NodeData/EdgeDataをNode/Edge系オブジェクトに変換
    - kind_idにより要素種別（Wall, Column, Beam, Sandbag）分類を一元化
    - Sandbagは2ノードペアリングで生成

TODO:
    - 例外処理強化: 無効なkind_idや欠損データへの耐性を追加
    - パラメータ化: 使用するkind_idリストや丸め精度など設定ファイル化
    - 単体テスト追加: 各コンストラクタ・APIメソッドの正常系/異常系検証
    - Lazy-loading対応検討: 大規模データ時のメモリ最適化
"""

from typing import Dict, List, Optional, Union
from utils import setup_logging
from configs import WALL_NODE_KIND_IDS, COLUMNS_KIND_IDS, BEAMS_KIND_IDS
from cores.entities import Node, Edge, Beam, Column, Panel, Sandbag
from .make_panel_unit import make_panel_unit
from .make_sandbag_unit import make_sandbag_unit
from parsers import NodeData, EdgeData

log = setup_logging("CoreFactory")


class CoreFactory:
    """
    ロード済みデータからコアモデルを構築・一元管理するクラス。

    Attributes:
        nodes (Dict[int, Node])
        edges (List[Edge])
        panels (List[Panel])
        sandbags (List[Sandbag])
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
        self.sandbags: List[Sandbag] = []
        self._construct_core_all(nodes_data, edges_data)

    def _construct_core_all(
        self,
        nodes_data: Dict[int, NodeData],
        edges_data: List[EdgeData],
    ) -> None:
        log.info("=================[コアモデルを構築]=========================")
        self.nodes = self._construct_core_nodes(nodes_data)
        self.edges = self._construct_core_edges(edges_data, self.nodes)
        self.panels = self._construct_core_panels(self.nodes, self.panel_node_kind_ids)
        self.sandbags = make_sandbag_unit(self.nodes)
        log.info(
            f"Nodes={len(self.nodes)}, Edges={len(self.edges)}, "
            f"Panels={len(self.panels)}, Sandbags={len(self.sandbags)}"
        )

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
            kind_id = e.kind_id
            kind_label = e.kind_label
            if kind_id in COLUMNS_KIND_IDS:
                edges.append(Column(a, b, kind_id, kind_label))
            elif kind_id in BEAMS_KIND_IDS:
                edges.append(Beam(a, b, kind_id, kind_label))
            else:
                edges.append(Edge(a, b, kind_id, kind_label))
        return edges

    def _construct_core_panels(
        self,
        node_map: Dict[int, Node],
        panel_node_kind_ids: List[int],
    ) -> List[Panel]:
        panel_data = make_panel_unit(
            node_map=node_map,
            panel_node_kind_ids=panel_node_kind_ids,
        )
        panels: List[Panel] = []
        for pd in panel_data:
            nodes = [node_map[nid] for nid in pd.node_ids]
            panels.append(
                Panel(nodes, kind=pd.kind, floor=pd.floor, attributes=pd.attributes)
            )
        return panels

    # Public API methods

    def get_nodes(self, ids: Optional[List[int]] = None) -> List[Node]:
        return (
            list(self.nodes.values())
            if ids is None
            else [self.nodes[i] for i in ids if i in self.nodes]
        )

    def get_edges(self, kind_ids: Optional[List[int]] = None) -> List[Edge]:
        return (
            self.edges
            if kind_ids is None
            else [e for e in self.edges if e.kind_id in kind_ids]
        )

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

    def get_sandbags(self) -> List[Sandbag]:
        return self.sandbags

    def summary(self) -> str:
        return (
            f"Nodes: {len(self.nodes)}, Edges: {len(self.edges)}, "
            f"Panels: {len(self.panels)}, Sandbags: {len(self.sandbags)}"
        )
