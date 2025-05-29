from typing import Dict, List, Optional, Set
from mathutils import Vector
from utils.logging_utils import setup_logging
from config import (
    NODE_CSV,
    EDGES_FILE,
    VALID_NODE_IDS,
    EPS_XY_MATCH,
    WALL_NODE_KIND_IDS,
    SANDBAG_NODE_KIND_IDS,
)
from loaders.node_loader import load_nodes, NodeData
from loaders.edge_loader import load_edges_from_str
from cores.node import Node
from cores.sandbag import SandbagNode  # ← 必須
from cores.edge import Edge
from cores.panel import Panel

log = setup_logging()


class CoreManager:
    def __init__(
        self,
        node_csv: str = NODE_CSV,
        edge_str: str = EDGES_FILE,
        valid_node_ids: Optional[Set[int]] = None,
        valid_kind_ids: Optional[List[int]] = None,
        panel_node_kind_ids: Optional[List[int]] = None,
    ):
        self.node_csv = node_csv
        self.edge_str = edge_str
        self.valid_node_ids = valid_node_ids or VALID_NODE_IDS
        self.valid_kind_ids = valid_kind_ids
        self.panel_node_kind_ids = (
            panel_node_kind_ids
            if panel_node_kind_ids is not None
            else WALL_NODE_KIND_IDS
        )

        self.nodes: Dict[int, Node | SandbagNode] = {}  # ← 型ヒントを拡張
        self.edges: List[Edge] = []
        self.panels: List[Panel] = []

        self._build_all()

    def _build_all(self):
        log.info("CoreManager: Loading nodes...")
        self.nodes = self._load_nodes(self.node_csv, self.valid_node_ids)
        log.info(f"CoreManager: Loaded {len(self.nodes)} nodes.")

        log.info("CoreManager: Loading edges...")
        self.edges = load_edges_from_str(self.edge_str, self.nodes, self.valid_kind_ids)
        log.info(f"CoreManager: Loaded {len(self.edges)} edges.")

        log.info("CoreManager: Building panels...")
        self.panels = self._build_panels(self.nodes, self.panel_node_kind_ids)
        log.info(
            f"CoreManager build completed: {len(self.nodes)} nodes, {len(self.edges)} edges, {len(self.panels)} panels"
        )

    def _load_nodes(
        self, path: str, valid_ids: Set[int]
    ) -> Dict[int, Node | SandbagNode]:
        node_map: Dict[int, Node | SandbagNode] = {}
        try:
            nodes_data_dict = load_nodes(path)
            for nid, node_data in nodes_data_dict.items():
                if nid not in valid_ids:
                    log.warning(f"Node ID {nid} not in valid_node_ids; skipping.")
                    continue
                # kind_idを見てSandbagNode/Nodeを選択
                if node_data.kind_id in SANDBAG_NODE_KIND_IDS:
                    node_map[nid] = SandbagNode(
                        nid, node_data.pos, kind_id=node_data.kind_id
                    )
                else:
                    node_map[nid] = Node(nid, node_data.pos, kind_id=node_data.kind_id)
                log.debug(
                    f"Loaded Node {nid}: {node_data.pos}, kind_id={node_data.kind_id}, type={type(node_map[nid]).__name__}"
                )
        except Exception as e:
            log.critical(f"Failed to read node STR {path} ({e})")
            raise
        return node_map

    # あとは従来通り。nodesの中にNode/SandbagNodeが混在するイメージです

    def _build_panels(
        self, node_map: Dict[int, Node | SandbagNode], panel_node_kind_ids: List[int]
    ) -> List[Panel]:
        panels: List[Panel] = []
        wall_nodes = [n for n in node_map.values() if n.kind_id in panel_node_kind_ids]
        log.info(
            f"_build_panels: Using {len(wall_nodes)} wall nodes (kind_id in {panel_node_kind_ids})"
        )
        zs = sorted({float(n.pos.z) for n in wall_nodes})
        if len(zs) < 2:
            log.warning(f"Insufficient Z levels (got {zs}); cannot build panels.")
            return []

        xs = [n.pos.x for n in wall_nodes]
        ys = [n.pos.y for n in wall_nodes]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)

        def eq(a, b):
            return abs(a - b) < EPS_XY_MATCH

        for lvl, z in enumerate(zs[:-1]):
            z_up = zs[lvl + 1]
            left = sorted(
                [n for n in wall_nodes if eq(n.pos.x, xmin) and eq(n.pos.z, z)],
                key=lambda n: n.pos.y,
            )
            right = sorted(
                [n for n in wall_nodes if eq(n.pos.x, xmax) and eq(n.pos.z, z)],
                key=lambda n: n.pos.y,
            )
            front = sorted(
                [n for n in wall_nodes if eq(n.pos.y, ymin) and eq(n.pos.z, z)],
                key=lambda n: n.pos.x,
            )
            back = sorted(
                [n for n in wall_nodes if eq(n.pos.y, ymax) and eq(n.pos.z, z)],
                key=lambda n: n.pos.x,
            )

            def segs(lst):
                return [(lst[i], lst[i + 1]) for i in range(len(lst) - 1)]

            for a, b in segs(left) + segs(front) + segs(right) + segs(back):

                def find_at(x, y, zval):
                    for n2 in wall_nodes:
                        if eq(n2.pos.z, zval) and eq(n2.pos.x, x) and eq(n2.pos.y, y):
                            return n2
                    return None

                x1, y1 = a.pos.x, a.pos.y
                x2, y2 = b.pos.x, b.pos.y
                c = find_at(x1, y1, z_up)
                d = find_at(x2, y2, z_up)
                if c and d:
                    panel = Panel(
                        [a, b, d, c], kind="wall", floor=str(z)
                    )  # ← [a, b, d, c]で統一
                    panels.append(panel)
                    log.debug(
                        f"Panel quad: {[n.id for n in (a, b, d, c)]}, z={z}->{z_up}"
                    )
                else:
                    log.debug(
                        f"Skipped: Not enough nodes for panel at z={z}->{z_up} ({a.id},{b.id})"
                    )

        log.info(f"_build_panels: {len(panels)} wall panels generated.")
        if panels:
            for p in panels[:10]:
                log.info(
                    f"Panel: nodes={[n.id for n in p.nodes]}, floor={p.floor}, kind={p.kind}"
                )
        else:
            log.warning("No panels were generated.")
        return panels

    def get_nodes(self, ids: Optional[List[int]] = None):
        if ids is None:
            return list(self.nodes.values())
        return [self.nodes[i] for i in ids if i in self.nodes]

    def get_edges(self, kind_ids: Optional[List[int]] = None) -> List[Edge]:
        if kind_ids is None:
            return self.edges
        return [e for e in self.edges if getattr(e, "kind_id", None) in kind_ids]

    def get_panels(self) -> List[Panel]:
        return self.panels

    def summary(self) -> str:
        return (
            f"Nodes: {len(self.nodes)}\n"
            f"Edges: {len(self.edges)}\n"
            f"Panels: {len(self.panels)}"
        )

    def classify_edges(self):
        from config import COLUMNS_KIND_IDS, BEAMS_KIND_IDS

        column_edges = [
            (e.node_a.id, e.node_b.id)
            for e in self.edges
            if e.kind_id in COLUMNS_KIND_IDS
        ]
        beam_edges = [
            (e.node_a.id, e.node_b.id)
            for e in self.edges
            if e.kind_id in BEAMS_KIND_IDS
        ]
        return column_edges, beam_edges
