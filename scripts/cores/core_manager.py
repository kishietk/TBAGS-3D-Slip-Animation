from typing import Dict, List, Optional
from utils.logging_utils import setup_logging
from config import SANDBAG_NODE_KIND_IDS, EPS_XY_MATCH, WALL_NODE_KIND_IDS
from cores.node import Node
from cores.sandbag import SandbagNode
from cores.edge import Edge
from cores.panel import Panel

log = setup_logging()


class CoreManager:
    def __init__(
        self,
        nodes_data: Dict[int, dict],  # LoaderManagerから渡されるrawデータ(dict)
        edges_data: List[dict],  # LoaderManagerから渡されるrawデータ(list)
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
        self._build_all(nodes_data, edges_data)

    def _build_all(self, nodes_data, edges_data):
        log.info("CoreManager: Building nodes (from data)...")
        self.nodes = self._build_nodes(nodes_data)
        log.info(f"CoreManager: {len(self.nodes)} nodes built.")

        log.info("CoreManager: Building edges (from data)...")
        self.edges = self._build_edges(edges_data, self.nodes)
        log.info(f"CoreManager: {len(self.edges)} edges built.")

        log.info("CoreManager: Building panels...")
        self.panels = self._build_panels(self.nodes, self.panel_node_kind_ids)
        log.info(
            f"CoreManager build completed: {len(self.nodes)} nodes, {len(self.edges)} edges, {len(self.panels)} panels"
        )

    def _build_nodes(
        self, nodes_data: Dict[int, dict]
    ) -> Dict[int, Node | SandbagNode]:
        node_map: Dict[int, Node | SandbagNode] = {}
        for nid, data in nodes_data.items():
            kind_id = data.get("kind_id")
            pos = data["pos"]
            if kind_id is not None and kind_id in SANDBAG_NODE_KIND_IDS:
                node_map[nid] = SandbagNode(nid, pos, kind_id=kind_id)
            else:
                node_map[nid] = Node(nid, pos, kind_id=kind_id)
            log.debug(
                f"Loaded Node {nid}: {pos}, kind_id={kind_id}, type={type(node_map[nid]).__name__}"
            )
        return node_map

    def _build_edges(
        self, edges_data: List[dict], node_map: Dict[int, Node | SandbagNode]
    ) -> List[Edge]:
        edges: List[Edge] = []
        for e in edges_data:
            node_a = node_map.get(e["node_a"])
            node_b = node_map.get(e["node_b"])
            kind_id = e.get("kind_id")
            kind_label = e.get("kind_label")
            if node_a and node_b:
                # 必要ならここでBeam/Column/Edgeに分岐
                edges.append(Edge(node_a, node_b, kind_id, kind_label))
        return edges

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
