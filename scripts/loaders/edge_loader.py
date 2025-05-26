# エッジデータローダ
# テキストデータからエッジ・梁・柱インスタンスを生成する

import re
from typing import List, Dict, Optional
from utils.logging_utils import setup_logging
from config import EBEAM_KIND_LABELS, COLUMNS_KIND_IDS, BEAMS_KIND_IDS
from cores.node import Node
from cores.edge import Edge
from cores.beam import Beam
from cores.column import Column

log = setup_logging()


def load_edges_from_str(
    path: str,
    node_map: Dict[int, Node],
    valid_kind_ids: Optional[List[int]] = None,
) -> List[Edge]:
    """
    エッジ定義テキストからエッジ・梁・柱インスタンスを生成する
    引数:
        path: エッジ定義ファイルパス
        node_map: ノードID→Nodeインスタンスの辞書
        valid_kind_ids: 有効な部材種別IDリスト（省略可）
    戻り値:
        Edge/Beam/Columnインスタンスのリスト
    """
    edges: List[Edge] = []
    current_kind_id: Optional[int] = None
    current_kind_label: Optional[str] = None
    in_ebeam3d = False
    abnormal_skip_count = 0

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                line_strip = line.strip()

                if "EBEAM3D" in line_strip:
                    in_ebeam3d = True
                    continue

                if in_ebeam3d and (line_strip.startswith("#=") or "END" in line_strip):
                    in_ebeam3d = False
                    current_kind_id = None
                    current_kind_label = None
                    continue

                if not in_ebeam3d:
                    continue

                m_kind = re.match(r"#\s*(\d+)\s*(.+)?", line_strip)
                if m_kind:
                    current_kind_id = int(m_kind.group(1))
                    current_kind_label = EBEAM_KIND_LABELS.get(
                        current_kind_id, m_kind.group(2) or "unknown"
                    )
                    log.debug(
                        f"EBEAM3D: kind_id={current_kind_id}, label={current_kind_label}"
                    )
                    continue

                nums = [int(n) for n in re.findall(r"\d+", line_strip)]
                if len(nums) < 2 or current_kind_id is None:
                    continue
                node_a_id, node_b_id = nums[-2], nums[-1]

                if node_a_id <= 0 or node_b_id <= 0 or node_a_id == node_b_id:
                    abnormal_skip_count += 1
                    continue

                if (
                    node_a_id in node_map
                    and node_b_id in node_map
                    and (valid_kind_ids is None or current_kind_id in valid_kind_ids)
                ):
                    if current_kind_id in COLUMNS_KIND_IDS:
                        edge = Column(
                            node_a=node_map[node_a_id],
                            node_b=node_map[node_b_id],
                            kind_id=current_kind_id,
                            kind_label=current_kind_label,
                        )
                    elif current_kind_id in BEAMS_KIND_IDS:
                        edge = Beam(
                            node_a=node_map[node_a_id],
                            node_b=node_map[node_b_id],
                            kind_id=current_kind_id,
                            kind_label=current_kind_label,
                        )
                    else:
                        edge = Edge(
                            node_a=node_map[node_a_id],
                            node_b=node_map[node_b_id],
                            kind_id=current_kind_id,
                            kind_label=current_kind_label,
                        )
                    log.debug(
                        f"Build Edge: nodes=({node_a_id}, {node_b_id}), kind_id={current_kind_id}, label={current_kind_label}"
                    )
                    edges.append(edge)
                elif (node_a_id in node_map) != (node_b_id in node_map):
                    log.debug(
                        f"Skipped edge line {line_num}: nodes=({nums}), kind_id={current_kind_id}, "
                        f"片側だけ有効 (node_a={node_a_id in node_map}, node_b={node_b_id in node_map})"
                    )
                # 両方とも無効ノードIDの場合は無視

    except Exception as e:
        log.critical(f"[{path}] CRITICAL: Failed to read edge STR ({e})")
        raise

    if abnormal_skip_count > 0:
        log.info(
            f"Skipped {abnormal_skip_count} edge lines due to abnormal node ids (0, negative, or duplicate)."
        )

    log.info(f"Loaded {len(edges)} edges from {path}")
    return edges
