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
from typing import Dict, List, Tuple, Set
from mathutils import Vector
from configs import (
    NODE_SECTION_KIND_IDS,
    KIND_LABELS,
    EDGE_NODE_KIND_IDS,
    VALID_NODE_IDS,
)
from configs.node_ids import COPY_SAND_BAG_NODE_IDS
from utils import setup_logging
from .types import NodeData, EdgeData

log = setup_logging("structureParser")


def parse_structure_str(path: str) -> Tuple[Dict[int, NodeData], List[EdgeData]]:
    """
    役割:
        STRファイルをパースし、ノード・エッジのデータ構造体群を返す。
    """
    nodes: Dict[int, NodeData] = {}
    edges: List[EdgeData] = []

    section_pattern = re.compile(r"#\s*(\d+)")
    current_kind_id = None
    tbag_section_active = False
    in_ebeam3d = False
    current_edge_kind_id = None
    current_edge_kind_label = None

    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            for row_idx, line in enumerate(f, start=1):
                line_strip = line.strip()

                # ノード区間判定
                m_section = section_pattern.match(line_strip)
                if m_section and not in_ebeam3d:
                    sec = int(m_section.group(1))
                    current_kind_id = sec if sec in NODE_SECTION_KIND_IDS else None
                    tbag_section_active = False
                    log.debug(f"[{path}] Section #{sec} at row {row_idx}")
                    continue

                # TBAGSセクション検出
                if "#Top of Upper level T-BAGS connected to Columns" in line_strip:
                    tbag_section_active = True
                    continue

                # Edge領域開始/終了
                if "EBEAM3D" in line_strip:
                    in_ebeam3d = True
                    continue
                if in_ebeam3d and (line_strip.startswith("#=") or "END" in line_strip):
                    in_ebeam3d = False
                    current_edge_kind_id = None
                    current_edge_kind_label = None
                    continue

                # ノードデータ行
                if (
                    not in_ebeam3d
                    and current_kind_id is not None
                    and line_strip
                    and not line_strip.startswith("#")
                ):
                    parts = line_strip.split()
                    if parts[0].isdigit():
                        nid = int(parts[0])
                        # ここでは通常ノードとT-BAGSノードのみをVALID_NODE_IDSで判定
                        if nid not in VALID_NODE_IDS:
                            continue
                        try:
                            x, y, z = map(float, parts[-3:])
                            kind_id = 0 if tbag_section_active else current_kind_id
                            nodes[nid] = NodeData(Vector((x, y, z)), kind_id)
                            log.info(f"Added node: ID={nid}, kind_id={kind_id}")
                        except Exception as e:
                            log.error(
                                f"[{path}] Failed to parse node at row {row_idx}: {e}"
                            )
                        continue

                # エッジ種別切り替え
                if in_ebeam3d and line_strip.startswith("#"):
                    m_kind = re.match(r"#\s*(\d+)", line_strip)
                    if m_kind:
                        current_edge_kind_id = int(m_kind.group(1))
                        current_edge_kind_label = KIND_LABELS.get(
                            current_edge_kind_id, "unknown"
                        )
                    continue

                # エッジデータ行
                if in_ebeam3d and not line_strip.startswith("#"):
                    nums = [int(n) for n in re.findall(r"\d+", line_strip)]
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
    tbag_section_active = False
    in_ebeam3d = False

    # 追加: 複製用に必要なノードID集合を構築
    needed_ids: Set[int] = set(VALID_NODE_IDS)
    for proto_id, targets in COPY_SAND_BAG_NODE_IDS.items():
        needed_ids.add(proto_id)
        needed_ids.update(targets)

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
                    # VALID_NODE_IDS か、複製用に必要な needed_ids に含まれるなら読み込む
                    if nid not in needed_ids:
                        continue
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
