from typing import Dict, List, Any
from utils import setup_logging
from configs import (
    WALL_NODE_KIND_IDS,
    COLUMNS_KIND_IDS,
    BEAMS_KIND_IDS,
)
from cores import Node, Edge, Roof, Panel as BasePanel
from .registry import get_core_class
from utils.make_panel_unit import make_panel_unit
from cores import NodeData, EdgeData

log = setup_logging(__name__)


class CoreFactory:
    """
    ドメインデータ（NodeData/EdgeData）からCoreクラスインスタンスを生成するファクトリ。
    ノードとエッジをCoreオブジェクトに変換し保持。パネル生成もサポート。
    """

    def __init__(self, node_data: Dict[int, NodeData], edge_data: List[EdgeData]):
        log.info(
            f"Initializing CoreFactory with {len(node_data)} nodes and {len(edge_data)} edges"
        )
        self._nodes: Dict[int, Node] = {}
        self._edges: List[Edge] = []

        # --- ノードインスタンス化 ---
        for nid, nd in node_data.items():
            log.debug(
                f"Processing node id={nid}, kind_id={nd.kind_id}, pos=({nd.pos.x}, {nd.pos.y}, {nd.pos.z})"
            )
            try:
                cls = get_core_class(nd.kind_id)
                log.debug(f"Found core class {cls.__name__} for kind_id {nd.kind_id}")
            except KeyError:
                log.warning(
                    f"No core class registered for kind_id {nd.kind_id}. Falling back to default Node class."
                )
                cls = Node
            x, y, z = nd.pos.x, nd.pos.y, nd.pos.z
            attrs = getattr(nd, "attributes", {})
            node_obj = cls(
                id=nid,
                x=x,
                y=y,
                z=z,
                kind=nd.kind_id,
                attributes=attrs,
            )
            self._nodes[nid] = node_obj
            log.debug(f"Instantiated {cls.__name__} for node id={nid}")

        log.info(f"Node instantiation complete: {len(self._nodes)} nodes created")

        # --- エッジインスタンス化 ---
        for ed in edge_data:
            log.debug(
                f"Processing edge from {ed.start_node_id} to {ed.end_node_id}, kind_id={ed.kind_id}"
            )
            n1 = self._nodes.get(ed.start_node_id)
            n2 = self._nodes.get(ed.end_node_id)
            if n1 is None or n2 is None:
                log.warning(
                    f"Skipping edge [{ed.start_node_id}-{ed.end_node_id}] because node missing"
                )
                continue
            attrs = getattr(ed, "attributes", {})
            try:
                e_cls = get_core_class(ed.kind_id)
                log.debug(
                    f"Found core class {e_cls.__name__} for edge kind_id {ed.kind_id}"
                )
            except KeyError:
                log.warning(
                    f"No core class registered for edge kind_id {ed.kind_id}. Falling back to default Edge class."
                )
                e_cls = Edge
            edge_obj = e_cls(
                start=n1,
                end=n2,
                kind=ed.kind_id,
                attributes=attrs,
            )
            self._edges.append(edge_obj)
            log.debug(f"Instantiated {e_cls.__name__} for edge {n1.id}-{n2.id}")

        log.info(f"Edge instantiation complete: {len(self._edges)} edges created")

        # public プロパティとしてエクスポート
        # SceneBuilder が getattr(self.core, "nodes"/"edges") で取得できるようにする
        self.nodes = self._nodes
        self.edges = self._edges

    def create_panels(self, panel_data_list: List[Any]) -> List[BasePanel]:
        """
        panel_data_list に基づきPanelインスタンスを生成。
        必要に応じてmake_panel_unitで分割処理を行う。
        """
        log.info(f"Creating panels from {len(panel_data_list)} raw panel data items")
        # パネル単位作成（ウォール／柱／梁ごとに分割）
        panel_data_list = make_panel_unit(
            panel_data_list,
            panel_node_kind_ids=WALL_NODE_KIND_IDS,
            column_node_kind_ids=COLUMNS_KIND_IDS,
            beam_node_kind_ids=BEAMS_KIND_IDS,
        )
        log.debug(
            f"Panel data split into {len(panel_data_list)} units after make_panel_unit"
        )

        panels: List[BasePanel] = []
        for pd in panel_data_list:
            kind = getattr(pd, "kind", None)
            cls = Roof if kind == "roof" else BasePanel
            log.debug(f"Instantiating panel of kind={kind} using class {cls.__name__}")
            node_objs = [self._nodes[nid] for nid in pd.node_ids if nid in self._nodes]
            attrs = getattr(pd, "attributes", {})
            panel = cls(
                nodes=node_objs,
                kind=kind,
                floor=getattr(pd, "floor", None),
                attributes=attrs,
            )
            panels.append(panel)
            log.debug(
                f"Panel instantiated: id={panel.id}, nodes={[n.id for n in panel.nodes]}"
            )

        log.info(f"Panel creation complete: {len(panels)} panels created")
        return panels
