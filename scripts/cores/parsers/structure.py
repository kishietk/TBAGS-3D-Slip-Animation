# core/parsers/structure.py

import re
from typing import Dict, List, Tuple
from mathutils import Vector
from cores import NodeData, EdgeData
from .base import BaseParser
from utils import setup_logging
from configs import (
    NODE_SECTION_KIND_IDS,
    KIND_LABELS,
    EDGE_NODE_KIND_IDS,
    VALID_NODE_IDS,
)

log = setup_logging("StructureParser")


class StructureParser(BaseParser):
    """
    .strファイルからノードとエッジ情報を読み込み、
    NodeDataのdictとEdgeDataのlistを返すParser。
    """

    def parse(self, path: str) -> Tuple[Dict[int, NodeData], List[EdgeData]]:
        nodes: Dict[int, NodeData] = {}
        edges: List[EdgeData] = []
        coord_pattern = re.compile(
            r"^\s*(?P<id>\d+)\s+3D\s+(?P<x>-?\d+(?:\.\d+)?)\s+(?P<y>-?\d+(?:\.\d+)?)\s+(?P<z>-?\d+(?:\.\d+)?)(?:\s|$)"
        )

        in_node_section = False
        in_edge_section = False
        tbag_section_active = False
        current_edge_kind_id = None
        current_edge_kind_label = None

        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                for lineno, line in enumerate(f, start=1):
                    ls = line.strip()

                    # ノードセクション開始
                    if ls == "NODE":
                        in_node_section = True
                        continue
                    # TBAGSセクション検出
                    if (
                        in_node_section
                        and "#Top of Upper level T-BAGS connected to Columns" in ls
                    ):
                        tbag_section_active = True
                        continue
                    # エッジセクション開始
                    if "EBEAM3D" in ls:
                        in_edge_section = True
                        continue
                    # エッジセクション終了
                    if in_edge_section and (ls.startswith("#=") or "END" in ls):
                        in_edge_section = False
                        current_edge_kind_id = None
                        current_edge_kind_label = None
                        continue
                    # エッジ種別切り替え
                    if in_edge_section and ls.startswith("#"):
                        m = re.match(r"#\s*(\d+)", ls)
                        if m:
                            current_edge_kind_id = int(m.group(1))
                            current_edge_kind_label = KIND_LABELS.get(
                                current_edge_kind_id, ""
                            )
                        continue
                    # エッジデータ行
                    if in_edge_section and not ls.startswith("#"):
                        nums = [int(n) for n in re.findall(r"\d+", ls)]
                        if len(nums) < 2 or current_edge_kind_id is None:
                            continue
                        a, b = nums[-2], nums[-1]
                        if a != b and a in nodes and b in nodes:
                            if (
                                nodes[a].kind_id in EDGE_NODE_KIND_IDS
                                or nodes[b].kind_id in EDGE_NODE_KIND_IDS
                            ):
                                edges.append(
                                    EdgeData(
                                        a,
                                        b,
                                        current_edge_kind_id,
                                        current_edge_kind_label,
                                    )
                                )
                        continue
                    # ノードデータ行
                    if in_node_section:
                        if not ls or ls.startswith("#"):
                            continue
                        m = coord_pattern.match(line)
                        if not m:
                            continue
                        nid = int(m.group("id"))
                        if nid not in VALID_NODE_IDS:
                            continue
                        x = float(m.group("x"))
                        y = float(m.group("y"))
                        z = float(m.group("z"))
                        kind_id = (
                            0
                            if tbag_section_active
                            else next(iter(NODE_SECTION_KIND_IDS), 0)
                        )
                        nodes[nid] = NodeData(Vector((x, y, z)), kind_id)
            if not nodes:
                log.critical(f"No nodes parsed from '{path}'")
                raise RuntimeError(f"Empty structure data from {path}")
            log.info(f"Parsed {len(nodes)} nodes and {len(edges)} edges from '{path}'")
            return nodes, edges
        except Exception as e:
            log.critical(f"Failed to parse structure file '{path}': {e}")
            raise
