# CoreManagerクラス
# ノード・エッジ・パネルの生成・管理を行う

from typing import Dict, List, Optional, Set
from mathutils import Vector
from utils.logging_utils import setup_logging
from config import NODE_CSV, EDGES_FILE, VALID_NODE_IDS, EPS_XY_MATCH

from cores.node import Node
from cores.edge import Edge
from cores.panel import Panel
from loaders.edge_loader import load_edges_from_str
import csv

log = setup_logging()


class CoreManager:
    """
    ノード・エッジ・パネル全体を管理するクラス
    データのロード・自動生成・フィルタ・集計APIを提供する
    """

    def __init__(
        self,
        node_csv: str = NODE_CSV,
        edge_str: str = EDGES_FILE,
        valid_node_ids: Optional[Set[int]] = None,
        valid_kind_ids: Optional[List[int]] = None,
    ):
        """
        CoreManagerを初期化する
        引数:
            node_csv: ノード座標CSVファイルパス
            edge_str: エッジ定義ファイルパス
            valid_node_ids: 有効なノードID集合（省略時は設定値を使用）
            valid_kind_ids: 有効な部材種別IDリスト（省略可）
        戻り値:
            なし
        """
        self.node_csv = node_csv
        self.edge_str = edge_str
        self.valid_node_ids = valid_node_ids or VALID_NODE_IDS
        self.valid_kind_ids = valid_kind_ids

        self.nodes: Dict[int, Node] = {}
        self.edges: List[Edge] = []
        self.panels: List[Panel] = []

        self._build_all()

    def _build_all(self):
        """
        ノード・エッジ・パネル全体を一括生成する
        引数:
            なし
        戻り値:
            なし
        """
        log.info("CoreManager: Loading nodes...")
        self.nodes = self._load_nodes(self.node_csv, self.valid_node_ids)

        log.info("CoreManager: Loading edges...")
        self.edges = load_edges_from_str(self.edge_str, self.nodes, self.valid_kind_ids)

        log.info("CoreManager: Building panels...")
        self.panels = self._build_panels(self.nodes)

        log.info(
            f"CoreManager build completed: {len(self.nodes)} nodes, {len(self.edges)} edges, {len(self.panels)} panels"
        )

    def _load_nodes(self, path: str, valid_ids: Set[int]) -> Dict[int, Node]:
        """
        ノード座標CSVを読み込む
        引数:
            path: ノード座標CSVファイルパス
            valid_ids: 有効なノードID集合
        戻り値:
            ノードID→Nodeインスタンスの辞書
        """
        node_map: Dict[int, Node] = {}
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row_idx, row in enumerate(reader, start=2):
                    if len(row) < 4:
                        continue
                    try:
                        nid = int(row[0])
                        if nid not in valid_ids:
                            continue
                        x, y, z = map(float, row[1:4])
                        node_map[nid] = Node(nid, Vector((x, y, z)))
                    except Exception as e:
                        log.warning(
                            f"Skipped non-data or header row at {row_idx}: {row} ({e})"
                        )
        except Exception as e:
            log.critical(f"Failed to read node CSV {path} ({e})")
            raise
        return node_map

    def _build_panels(self, node_map: Dict[int, Node]) -> List[Panel]:
        """
        ノード群からパネルを自動生成する
        引数:
            node_map: ノードID→Nodeインスタンスの辞書
        戻り値:
            Panelインスタンスのリスト
        """
        panels: List[Panel] = []
        zs = sorted({n.pos.z for n in node_map.values()})
        if len(zs) < 2:
            return []
        nodes = node_map
        xs = sorted({n.pos.x for n in nodes.values()})
        ys = sorted({n.pos.y for n in nodes.values()})

        def fid(x, y, z):
            for n in nodes.values():
                if (
                    abs(n.pos.x - x) < EPS_XY_MATCH
                    and abs(n.pos.y - y) < EPS_XY_MATCH
                    and abs(n.pos.z - z) < EPS_XY_MATCH
                ):
                    return n
            return None

        for lvl, z in enumerate(zs[:-1]):
            z_up = zs[lvl + 1]
            for i in range(len(xs) - 1):
                for j in range(len(ys) - 1):
                    bl = fid(xs[i], ys[j], z)
                    br = fid(xs[i + 1], ys[j], z)
                    tr = fid(xs[i + 1], ys[j + 1], z_up)
                    tl = fid(xs[i], ys[j + 1], z_up)
                    if None not in (bl, br, tr, tl):
                        panel = Panel([bl, br, tr, tl])
                        panels.append(panel)
        return panels

    def get_nodes(self, ids: Optional[List[int]] = None) -> List[Node]:
        """
        ノードリストを取得する
        引数:
            ids: 取得するノードIDリスト（省略時は全ノード）
        戻り値:
            Nodeインスタンスのリスト
        """
        if ids is None:
            return list(self.nodes.values())
        return [self.nodes[i] for i in ids if i in self.nodes]

    def get_edges(self, kind_ids: Optional[List[int]] = None) -> List[Edge]:
        """
        エッジリストを取得する
        引数:
            kind_ids: 部材種別IDリスト（省略時は全エッジ）
        戻り値:
            Edgeインスタンスのリスト
        """
        if kind_ids is None:
            return self.edges
        return [e for e in self.edges if getattr(e, "kind_id", None) in kind_ids]

    def get_panels(self) -> List[Panel]:
        """
        パネルリストを取得する
        引数:
            なし
        戻り値:
            Panelインスタンスのリスト
        """
        return self.panels

    def summary(self) -> str:
        """
        データの件数サマリを取得する
        引数:
            なし
        戻り値:
            サマリ文字列
        """
        return (
            f"Nodes: {len(self.nodes)}\n"
            f"Edges: {len(self.edges)}\n"
            f"Panels: {len(self.panels)}"
        )

    def classify_edges(self):
        """
        エッジリストを柱・梁に分類する
        引数:
            なし
        戻り値:
            (柱エッジIDペアリスト, 梁エッジIDペアリスト)
        """
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
