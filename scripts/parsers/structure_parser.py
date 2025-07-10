"""
責務:
- 構造STRファイルからノード・エッジ定義を同時にパースし、NodeData/EdgeDataのコレクションとして返す。
- エッジ情報を無視してノード位置のみを返すユーティリティ関数も提供。

設計ポイント:
- 1パスでノード・エッジ両方を抽出可能
- kind_labels.py/constants.pyの分類定数を活用
- エッジ不要時はparse_strを使用して軽量に位置取得
- ログ・バリデ・エラーも一元記録

TODO:
- セクション/区間パターン追加時はロジック拡張
- 構造ファイル仕様変化に強い設計に
"""

import re
from typing import Dict, List, Tuple
from mathutils import Vector
from configs import (
    NODE_SECTION_KIND_IDS,
    KIND_LABELS,
    EDGE_NODE_KIND_IDS,
    VALID_NODE_IDS,
)
from utils import setup_logging
from .types import NodeData, EdgeData

log = setup_logging("structureParser")


def parse_structure_str(path: str) -> Tuple[Dict[int, NodeData], List[EdgeData]]:
    """
    STR ファイルをパースし、ノード・エッジのデータ構造体群を返す。
    ノード座標は "3D" 行のみを正規表現で抽出し、形式が不正な行はスキップします。
    エッジは EBEAM3D セクションから抽出。
    """
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
            for row_idx, line in enumerate(f, start=1):
                ls = line.strip()

                # ノードセクション開始
                if ls == "NODE":
                    in_node_section = True
                    log.debug(f"[{path}] Enter NODE section at row {row_idx}")
                    continue

                # TBAGS セクション検出
                if (
                    in_node_section
                    and "#Top of Upper level T-BAGS connected to Columns" in ls
                ):
                    tbag_section_active = True
                    continue

                # エッジセクション開始／終了
                if "EBEAM3D" in ls:
                    in_edge_section = True
                    log.debug(f"[{path}] Enter EBEAM3D section at row {row_idx}")
                    continue
                if in_edge_section and (ls.startswith("#=") or "END" in ls):
                    in_edge_section = False
                    current_edge_kind_id = None
                    current_edge_kind_label = None
                    log.debug(f"[{path}] Exit EBEAM3D section at row {row_idx}")
                    continue

                # エッジ種別切り替え
                if in_edge_section and ls.startswith("#"):
                    m_kind = re.match(r"#\s*(\d+)", ls)
                    if m_kind:
                        current_edge_kind_id = int(m_kind.group(1))
                        current_edge_kind_label = KIND_LABELS.get(
                            current_edge_kind_id, "unknown"
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
                                    a, b, current_edge_kind_id, current_edge_kind_label
                                )
                            )
                            log.info(
                                f"Added edge: ({a}, {b}) kind={current_edge_kind_id}"
                            )
                    continue

                # ノードデータ行
                if in_node_section:
                    # コメントや空行はスキップ
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
                    log.info(f"Added node: ID={nid}, kind_id={kind_id}")

    except Exception as e:
        log.critical(f"[{path}] Critical parse error: {e}")
        raise

    log.info(f"Parsed {len(nodes)} nodes, {len(edges)} edges.")
    return nodes, edges


# ----------------------------------------------------------------
# 独立したノード位置取得用関数
# ----------------------------------------------------------------


def parse_str(path: str) -> Dict[int, Vector]:
    """
    STRファイルをパースし、ノードID→Vector座標マップを返す。
    VALID_NODE_IDS と、COPY_SAND_BAG_NODE_IDS に
    含まれる prototype／target の両方を常に読み込む。
    """
    positions: Dict[int, Vector] = {}
    section_pattern = re.compile(r"#\s*(\d+)")
    current_kind_id = None
    in_ebeam3d = False

    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line_strip = line.strip()

                # Edge領域はスキップ
                if "EBEAM3D" in line_strip:
                    in_ebeam3d = True
                    continue
                if in_ebeam3d:
                    continue

                # セクション行
                m_section = section_pattern.match(line_strip)
                if m_section:
                    sec = int(m_section.group(1))
                    current_kind_id = sec if sec in NODE_SECTION_KIND_IDS else None
                    tbag_section_active = False
                    continue

                # TBAGSセクション検出
                if "#Top of Upper level T-BAGS connected to Columns" in line_strip:
                    tbag_section_active = True
                    continue

                # ノード行
                parts = line_strip.split()
                if current_kind_id is not None and parts and parts[0].isdigit():
                    nid = int(parts[0])
                    try:
                        x, y, z = map(float, parts[-3:])
                        positions[nid] = Vector((x, y, z))
                    except Exception as e:
                        log.error(f"Failed to parse position for node {nid}: {e}")
                        continue

    except Exception as e:
        log.critical(f"[parse_str] Critical error: {e}")
        raise

    return positions
