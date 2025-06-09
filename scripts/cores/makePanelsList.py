"""
コアパネル自動生成モジュール
- ノード群・kind_id指定から壁/床/屋根のパネル（面）を自動的に決定
- [a, b, d, c]のノードID順でPanelDataリストを生成

【設計思想】
- 3D格子状に規則的な構造ノードからpanel四角面を自動抽出
- kind_idで壁/床/屋根候補ノードだけフィルタ
- EPS_XY_MATCHで座標誤差を吸収
- panel構築判定（find_at, segsなど）は可読性を重視
"""

from typing import Dict, List, NamedTuple
from loaders.nodeLoader import NodeData
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
    ノード情報と指定kind_idに基づき壁パネル（PanelData）リストを生成
    Args:
        node_map (Dict[int, NodeData]): ノードID→NodeData
        panel_node_kind_ids (List[int]): panel候補のkind_id
    Returns:
        List[PanelData]: 4点ID・属性付PanelDataリスト
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

    def eq(a: float, b: float) -> bool:
        """座標比較の誤差吸収"""
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

            def find_at(x: float, y: float, zval: float):
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

    log.info(f"Maked {len(panels)} panel lists")
    return panels
