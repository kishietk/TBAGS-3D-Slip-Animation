"""
エッジデータローダ
STRファイル等のテキストデータから、エッジ定義（データ構造）リストを生成

- 許容ノードkind_idリスト（EDGE_NODE_KIND_IDS）によるフィルタ機能付き
- データ層では部材クラス生成せず、EdgeData（NamedTuple）リストのみ返す
"""

import re
from typing import List, Dict, Optional, NamedTuple
from utils.logging_utils import setup_logging
from loaders.node_loader import NodeData

from config import (
    EBEAM_KIND_LABELS,
    EDGE_NODE_KIND_IDS,
)

log = setup_logging()


class EdgeData(NamedTuple):
    node_a: int
    node_b: int
    kind_id: int
    kind_label: str


def load_edges(
    path: str,
    node_map: Dict[int, "NodeData"],
    valid_kind_ids: Optional[List[int]] = None,
) -> List[EdgeData]:
    """
    エッジ定義テキストからエッジ情報データ（EdgeData）を生成
    許可されたkind_idのノード間のみエッジ定義として返す

    引数:
        path: エッジ定義ファイルパス
        node_map: ノードID→NodeDataインスタンスの辞書（kind_id必須）
        valid_kind_ids: 有効な部材種別IDリスト（省略可）

    戻り値:
        EdgeDataインスタンスのリスト
    """
    log.info("=================[エッジ情報を読み取り]=========================")
    edges: List[EdgeData] = []
    current_kind_id: Optional[int] = None
    current_kind_label: Optional[str] = None
    in_ebeam3d = False
    abnormal_skip_count = 0
    kindid_skip_count = 0

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

                # 種別ID行: 例 "# 42 梁"
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

                # ノードペア行（数値が2つ以上連続しているものを対象）
                nums = [int(n) for n in re.findall(r"\d+", line_strip)]
                if len(nums) < 2 or current_kind_id is None:
                    continue
                node_a_id, node_b_id = nums[-2], nums[-1]

                # 不正ID（0やマイナス・重複）は無視
                if node_a_id <= 0 or node_b_id <= 0 or node_a_id == node_b_id:
                    abnormal_skip_count += 1
                    continue

                # kind_idチェック（両ノードがEDGE_NODE_KIND_IDSに含まれるか）
                kind_a = getattr(node_map.get(node_a_id), "kind_id", None)
                kind_b = getattr(node_map.get(node_b_id), "kind_id", None)
                if (
                    node_a_id in node_map
                    and node_b_id in node_map
                    and (valid_kind_ids is None or current_kind_id in valid_kind_ids)
                ):
                    if (
                        kind_a not in EDGE_NODE_KIND_IDS
                        or kind_b not in EDGE_NODE_KIND_IDS
                    ):
                        kindid_skip_count += 1
                        log.debug(
                            f"Skipped edge (nodes {node_a_id}-{node_b_id}): "
                            f"kind_id not in EDGE_NODE_KIND_IDS ({kind_a}, {kind_b})"
                        )
                        continue
                    # --- ここではEdgeDataのみ返す ---
                    edges.append(
                        EdgeData(
                            node_a=node_a_id,
                            node_b=node_b_id,
                            kind_id=current_kind_id,
                            kind_label=current_kind_label,
                        )
                    )
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
    if kindid_skip_count > 0:
        log.info(
            f"Skipped {kindid_skip_count} edge lines due to node kind_id not in EDGE_NODE_KIND_IDS."
        )

    log.info(f"Loaded {len(edges)} edges from {path}")
    return edges
