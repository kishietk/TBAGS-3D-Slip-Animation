# cores/construct_core_panels.py

from typing import Dict, List, NamedTuple
from loaders.node_loader import NodeData
from config import EPS_XY_MATCH
from utils.logging_utils import setup_logging

log = setup_logging()


class PanelData(NamedTuple):
    node_ids: List[int]  # [a, b, d, c] の順
    kind: str = "wall"
    floor: str = ""
    attributes: dict = {}


def make_panels_list(
    node_map: Dict[int, NodeData],
    panel_node_kind_ids: List[int],
) -> List[PanelData]:
    """
    ノード情報（NodeData）と指定kind_idに基づき、壁パネル（PanelData）リストを自動生成。
    [a, b, d, c]形式でノードIDを格納。
    """
    log.info("=================[パネルコアオブジェクトを作成]=========================")
    panels: List[PanelData] = []
    wall_nodes = [
        (nid, n) for nid, n in node_map.items() if n.kind_id in panel_node_kind_ids
    ]
    if not wall_nodes:
        log.warning("No wall nodes found for panel construction.")
        return panels

    zs = sorted({float(n.pos.z) for _, n in wall_nodes})
    if len(zs) < 2:
        log.warning("Insufficient Z levels to build panels.")
        return panels

    xs = [n.pos.x for _, n in wall_nodes]
    ys = [n.pos.y for _, n in wall_nodes]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    def eq(a, b):
        return abs(a - b) < EPS_XY_MATCH

    # 各階ごとにpanel quad探索
    for lvl, z in enumerate(zs[:-1]):
        z_up = zs[lvl + 1]
        left = sorted(
            [(nid, n) for nid, n in wall_nodes if eq(n.pos.x, xmin) and eq(n.pos.z, z)],
            key=lambda tup: tup[1].pos.y,
        )
        right = sorted(
            [(nid, n) for nid, n in wall_nodes if eq(n.pos.x, xmax) and eq(n.pos.z, z)],
            key=lambda tup: tup[1].pos.y,
        )
        front = sorted(
            [(nid, n) for nid, n in wall_nodes if eq(n.pos.y, ymin) and eq(n.pos.z, z)],
            key=lambda tup: tup[1].pos.x,
        )
        back = sorted(
            [(nid, n) for nid, n in wall_nodes if eq(n.pos.y, ymax) and eq(n.pos.z, z)],
            key=lambda tup: tup[1].pos.x,
        )

        def segs(lst):
            return [(lst[i], lst[i + 1]) for i in range(len(lst) - 1)]

        for (a_id, a), (b_id, b) in segs(left) + segs(front) + segs(right) + segs(back):

            def find_at(x, y, zval):
                for nid2, n2 in wall_nodes:
                    if eq(n2.pos.z, zval) and eq(n2.pos.x, x) and eq(n2.pos.y, y):
                        return nid2, n2
                return None

            x1, y1 = a.pos.x, a.pos.y
            x2, y2 = b.pos.x, b.pos.y
            c = find_at(x1, y1, z_up)
            d = find_at(x2, y2, z_up)
            if c and d:
                c_id, _ = c
                d_id, _ = d
                panel = PanelData(
                    node_ids=[a_id, b_id, d_id, c_id],
                    kind="wall",
                    floor=str(z),
                    attributes={},
                )
                panels.append(panel)

    log.info(f"Loaded {len(panels)} panels")
    return panels
