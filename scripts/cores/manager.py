from __future__ import annotations
from typing import Dict, List, Optional
from cores.node import Node
from cores.edge import Edge
from cores.panel import Panel
from logging_utils import setup_logging
from config import (
    NODE_CSV,
    EDGES_FILE,
    ANIM_CSV,
    VALID_NODE_IDS,
)
import csv

log = setup_logging()


class CoreManager:
    """
    ノード・エッジ・パネルの全体管理クラス
    """

    def __init__(self):
        self.nodes: Dict[int, Node] = {}
        self.edges: List[Edge] = []
        self.panels: List[Panel] = []

    def load_nodes(self, csv_path: Optional[str] = None):
        """
        ノード座標CSVを読み込み、Nodeインスタンスを生成
        """
        path = csv_path or NODE_CSV
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for row_num, row in enumerate(reader, 1):
                if not row or not row[0].strip() or row[0].startswith("#"):
                    continue
                try:
                    nid = int(row[0])
                    if nid not in VALID_NODE_IDS:
                        continue
                    x, y, z = map(float, row[1:4])
                    self.nodes[nid] = Node(nid, (x, y, z))
                except Exception as e:
                    log.warning(
                        f"Skipped non-data or header row at {row_num}: {row} ({e})"
                    )

        log.info(f"Loaded {len(self.nodes)} nodes from {path}")

    def load_edges(
        self, str_path: Optional[str] = None, valid_kind_ids: Optional[List[int]] = None
    ):
        """
        STRファイルからエッジデータを抽出し、Edgeインスタンスを生成
        """
        from loaders.edges import load_edges_from_str

        path = str_path or EDGES_FILE
        edges = load_edges_from_str(path, self.nodes, valid_kind_ids=valid_kind_ids)
        self.edges.extend(edges)

    def get_nodes(self) -> Dict[int, Node]:
        return self.nodes

    def get_edges(self) -> List[Edge]:
        return self.edges

    def get_panels(self) -> List[Panel]:
        return self.panels

    def build_panels(self):
        """
        パネル情報の生成（仮の実装）
        """
        # Implement as needed
        pass
