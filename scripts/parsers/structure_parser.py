"""
責務:
- 構造STRファイルからノード・エッジ定義を同時にパースし、NodeData/EdgeDataのコレクションとして返す。
- セクションや区間の自動判定、バリデ・kind_id・サンドバッグ対応も一元管理。

設計ポイント:
- 1パスでノード・エッジ両方を抽出可能
- kind_labels.py/constants.pyの分類定数を活用
- ログ・バリデ・エラーも一元記録

TODO:
- セクション/区間パターン追加時はロジック拡張
- 構造ファイル仕様変化に強い設計に
"""

import re
from typing import Dict, List, Tuple
from mathutils import Vector
from configs.kind_labels import NODE_SECTION_KIND_IDS, KIND_LABELS, EDGE_NODE_KIND_IDS
from configs.constants import VALID_NODE_IDS
from utils import setup_logging
from .types import NodeData, EdgeData

log = setup_logging("structureParser")


def parse_structure_str(path: str) -> Tuple[Dict[int, NodeData], List[EdgeData]]:
    """
    役割:
        STRファイルをパースし、ノード・エッジのデータ構造体群を返す。

    引数:
        path (str): STRファイルパス

    返り値:
        Dict[int, NodeData]: ノードID→NodeData
        List[EdgeData]: エッジリスト
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
                    log.debug(
                        f"[{path}] Section #{sec} (kind_id={current_kind_id}) at row {row_idx}"
                    )
                    continue

                if (
                    "#Top of Upper level T-BAGS connected to Columns" in line_strip
                    and not in_ebeam3d
                ):
                    tbag_section_active = True
                    log.debug(f"[{path}] TBAG section started at row {row_idx}")
                    continue

                # EBEAM3D区間検出
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
                    m_node = re.match(
                        r"(\d+)\s+\S+\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)", line_strip
                    )
                    if m_node:
                        nid = int(m_node.group(1))
                        if nid not in VALID_NODE_IDS:
                            continue
                        try:
                            x, y, z = (
                                float(m_node.group(2)),
                                float(m_node.group(3)),
                                float(m_node.group(4)),
                            )
                            kind_id = 0 if tbag_section_active else current_kind_id
                            nodes[nid] = NodeData(Vector((x, y, z)), kind_id)
                            log.info(f"Added node: ID={nid}, kind_id={kind_id}")
                        except Exception as e:
                            log.error(
                                f"[{path}] Failed to parse XYZ at row {row_idx}, node ID {nid}: {line_strip} ({e})"
                            )
                        continue

                # エッジ種別切り替え
                if in_ebeam3d and line_strip.startswith("#"):
                    m_kind = re.match(r"#\s*(\d+)\s*(.+)?", line_strip)
                    if m_kind:
                        current_edge_kind_id = int(m_kind.group(1))
                        current_edge_kind_label = KIND_LABELS.get(
                            current_edge_kind_id, m_kind.group(2) or "unknown"
                        )
                        continue

                # エッジデータ行
                if in_ebeam3d and not line_strip.startswith("#"):
                    nums = [int(n) for n in re.findall(r"\d+", line_strip)]
                    if len(nums) < 2 or current_edge_kind_id is None:
                        continue
                    node_a_id, node_b_id = nums[-2], nums[-1]
                    # 異常ID/重複除外
                    if node_a_id <= 0 or node_b_id <= 0 or node_a_id == node_b_id:
                        continue
                    # 両ノード存在チェック
                    kind_a = getattr(nodes.get(node_a_id), "kind_id", None)
                    kind_b = getattr(nodes.get(node_b_id), "kind_id", None)
                    if (
                        node_a_id in nodes
                        and node_b_id in nodes
                        and (
                            kind_a in EDGE_NODE_KIND_IDS or kind_b in EDGE_NODE_KIND_IDS
                        )
                    ):
                        edges.append(
                            EdgeData(
                                node_a=node_a_id,
                                node_b=node_b_id,
                                kind_id=current_edge_kind_id,
                                kind_label=current_edge_kind_label,
                            )
                        )
                        log.info(
                            f"Added edge: ({node_a_id}, {node_b_id}), kind_id={current_edge_kind_id}"
                        )
                    continue

    except Exception as e:
        log.critical(f"[{path}] CRITICAL: Failed to parse structure STR ({e})")
        raise

    log.info(f"{len(nodes)}件のノード、{len(edges)}件のエッジを読み込みました。")
    return nodes, edges
