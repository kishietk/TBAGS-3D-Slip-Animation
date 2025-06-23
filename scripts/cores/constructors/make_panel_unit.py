"""
ファイル名: cores/makePanelsList.py

責務:
- ノード群・kind_id指定から壁/床/屋根のパネル（面）を自動的に決定し、PanelDataリストを生成する。
- [a, b, d, c]のノードID順で面を定義。
- 3D格子状の構造から四角面を探索し自動生成。

設計思想:
- kind_idによる壁/床/屋根候補ノードだけをフィルタ
- EPS_XY_MATCHで座標誤差を吸収しパネル構築
- find_atやsegs等の小関数で可読性重視
"""

from typing import Dict, List, NamedTuple
from loaders.structureParser import NodeData
from configs import EPS_XY_MATCH
from utils.logging_utils import setup_logging

log = setup_logging("makePanelsList")


class PanelData(NamedTuple):
    """
    役割:
        パネル（面）を定義するデータ構造体。
    属性:
        node_ids (List[int]): 4点ノードID（[a, b, d, c]順）
        kind (str): パネル種別
        floor (str): 階情報等
        attributes (dict): 任意属性
    """

    node_ids: List[int]
    kind: str = "wall"
    floor: str = ""
    attributes: dict = {}


def make_panel_unit(
    node_map: Dict[int, NodeData],
    panel_node_kind_ids: List[int],
) -> List[PanelData]:
    """
    役割:
        ノード情報と指定kind_idに基づき、壁パネル（PanelData）リストを生成する。

    引数:
        node_map (Dict[int, NodeData]): ノードID→NodeData
        panel_node_kind_ids (List[int]): panel候補のkind_id

    返り値:
        List[PanelData]: 4点ID・属性付きPanelDataリスト

    処理:
        - 指定kind_idのノードのみ壁候補として抽出
        - 3D座標から各階層・各面の組み合わせを探索
        - EPS_XY_MATCHで誤差を吸収し、find_at/segs等の小関数で組み合わせ探索
    """
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
        """座標比較の誤差吸収（EPS_XY_MATCHで比較）"""
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
            """隣接ノード間のペアを生成"""
            return [(lst[i], lst[i + 1]) for i in range(len(lst) - 1)]

        for (a_id, a), (b_id, b) in segs(left) + segs(front) + segs(right) + segs(back):

            def find_at(x: float, y: float, zval: float):
                """指定座標に一致するノード（誤差吸収）を探索"""
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
    return panels
