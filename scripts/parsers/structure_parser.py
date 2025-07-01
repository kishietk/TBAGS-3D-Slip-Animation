"""
ファイル名: parsers/structure_parser.py

責務:
- 構造STRファイルからノード・エッジ定義を同時にパースし、NodeData/EdgeDataのコレクションとして返す。
- セクションや区間の自動判定、バリデ・kind_id・サンドバッグ対応も一元管理。
- パース結果の全ノード座標マップをグローバルに保持し、外部から参照可能にする。

設計ポイント:
- 1パスでノード・エッジ両方を抽出可能
- kind_labels.py/constants.pyの分類定数を活用
- Coreモデル用ノードとクローン用ノードを分離
- ログ・バリデ・エラーも一元記録
"""

import re
from typing import Dict, List, Tuple
from mathutils import Vector
from configs.kind_labels import NODE_SECTION_KIND_IDS, KIND_LABELS, EDGE_NODE_KIND_IDS
from configs.constants import CORE_NODE_IDS
from utils import setup_logging
from .types import NodeData, EdgeData

log = setup_logging("structureParser")

# ―― 全ノード座標を保持するマップ（クローン配置用に利用） ――
_node_coords: Dict[int, Vector] = {}


def parse_structure_str(path: str) -> Tuple[Dict[int, NodeData], List[EdgeData]]:
    """
    STRファイルをパースし、
      ・CORE_NODE_IDS に含まれるノードだけを NodeData として返す
      ・すべてのノード座標を _node_coords に保持
      ・EDGE_NODE_KIND_IDS に従ったエッジリストを返す

    引数:
        path (str): STRファイルパス

    返り値:
        nodes: Dict[int, NodeData]         → CoreFactory 以下で利用するノード
        edges: List[EdgeData]              → CoreFactory 以下で利用するエッジ
    """
    global _node_coords

    nodes: Dict[int, NodeData] = {}
    edges: List[EdgeData] = []

    # 一時的に全ノード座標を集めるマップ
    all_coords: Dict[int, Vector] = {}

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

                # セクション番号行: kind 判定
                m_section = section_pattern.match(line_strip)
                if m_section and not in_ebeam3d:
                    sec = int(m_section.group(1))
                    current_kind_id = sec if sec in NODE_SECTION_KIND_IDS else None
                    tbag_section_active = False
                    log.debug(
                        f"[{path}] Section #{sec} (kind_id={current_kind_id}) at row {row_idx}"
                    )
                    continue

                # TBAGセクション開始
                if (
                    "#Top of Upper level T-BAGS connected to Columns" in line_strip
                    and not in_ebeam3d
                ):
                    tbag_section_active = True
                    log.debug(f"[{path}] TBAG section started at row {row_idx}")
                    continue

                # EBEAM3D 開始／終了
                if "EBEAM3D" in line_strip:
                    in_ebeam3d = True
                    continue
                if in_ebeam3d and (line_strip.startswith("#=") or "END" in line_strip):
                    in_ebeam3d = False
                    current_edge_kind_id = None
                    current_edge_kind_label = None
                    continue

                # ── ノードデータ行 ──
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
                        x, y, z = (
                            float(m_node.group(2)),
                            float(m_node.group(3)),
                            float(m_node.group(4)),
                        )
                        # 全ノード座標を保持
                        all_coords[nid] = Vector((x, y, z))
                        # Coreモデル用ノードのみ NodeData として登録
                        if nid in CORE_NODE_IDS:
                            kind_id = 0 if tbag_section_active else current_kind_id
                            nodes[nid] = NodeData(all_coords[nid], kind_id)
                            log.info(f"Added node: ID={nid}, kind_id={kind_id}")
                    continue

                # ── エッジ種別切り替え ──
                if in_ebeam3d and line_strip.startswith("#"):
                    m_kind = re.match(r"#\s*(\d+)\s*(.+)?", line_strip)
                    if m_kind:
                        current_edge_kind_id = int(m_kind.group(1))
                        current_edge_kind_label = KIND_LABELS.get(
                            current_edge_kind_id, m_kind.group(2) or "unknown"
                        )
                    continue

                # ── エッジデータ行 ──
                if in_ebeam3d and not line_strip.startswith("#"):
                    nums = [int(n) for n in re.findall(r"\d+", line_strip)]
                    if len(nums) >= 2 and current_edge_kind_id is not None:
                        a, b = nums[-2], nums[-1]
                        if a > 0 and b > 0 and a != b and a in nodes and b in nodes:
                            kind_a = nodes[a].kind_id
                            kind_b = nodes[b].kind_id
                            if (
                                kind_a in EDGE_NODE_KIND_IDS
                                or kind_b in EDGE_NODE_KIND_IDS
                            ):
                                edges.append(
                                    EdgeData(
                                        node_a=a,
                                        node_b=b,
                                        kind_id=current_edge_kind_id,
                                        kind_label=current_edge_kind_label,
                                    )
                                )
                                log.info(
                                    f"Added edge: ({a}, {b}), kind_id={current_edge_kind_id}"
                                )
                    continue

    except Exception as e:
        log.critical(f"[{path}] CRITICAL: Failed to parse structure STR ({e})")
        raise

    # 全ノード座標マップを更新（クローン処理で使用）
    _node_coords = all_coords
    log.info(
        f"{len(nodes)}件のコアモデル用ノード、{len(edges)}件のエッジを読み込みました。全ノード座標: {_node_coords.keys().__len__()}件"
    )
    return nodes, edges


def get_node_coords() -> Dict[int, Vector]:
    """
    役割:
        最後にパースされた全ノードID→座標(Vector)マップを返す。
        clone_sandbags() などで利用します。
    """
    if not _node_coords:
        log.warning("_node_coords がまだ空です。構造ファイルのパース前かもしれません。")
    return _node_coords
