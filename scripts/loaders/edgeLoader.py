"""
エッジデータローダ
- STRファイル等テキストから、エッジ定義（データ構造）リストを生成
- EDGE_NODE_KIND_IDS等で種別・ノード種類を厳格フィルタ
- EdgeData(NamedTuple)リストのみ返す（部材インスタンスは返さない）

【設計・注意点】
- ファイルフォーマットは“EBEAM3D”セクション区切りあり
- 行頭#の行で種別IDを設定、2つ以上整数が並ぶ行でエッジ定義
- 不正ノードID・種別フィルタで徹底的に異常値除外
- kind_id, kind_label, ノード存在性は必ず検証
"""

import re
from typing import List, Dict, Optional, NamedTuple
from utils.logging_utils import setup_logging
from loaders.nodeLoader import NodeData
from configs import (
    KIND_LABELS,
    EDGE_NODE_KIND_IDS,
)

log = setup_logging()


class EdgeData(NamedTuple):
    """
    エッジ（部材）の情報構造体
    node_a (int): ノードAのID
    node_b (int): ノードBのID
    kind_id (int): 部材種別ID（53=柱など）
    kind_label (str): 部材種別日本語ラベル/識別名
    """

    node_a: int
    node_b: int
    kind_id: int
    kind_label: str


def load_edges(
    path: str,
    node_map: Dict[int, NodeData],
    valid_kind_ids: Optional[List[int]] = None,
) -> List[EdgeData]:
    """
    STR等のエッジ定義テキストから、厳格フィルタを通した
    EdgeData構造体（node_a, node_b, kind_id, kind_label）リストを返す

    Args:
        path (str): エッジ定義ファイルパス
        node_map (Dict[int, NodeData]): ノードID→NodeDataインスタンスの辞書
        valid_kind_ids (Optional[List[int]]): 許可する部材種別IDリスト
    Returns:
        List[EdgeData]: 厳格にフィルタ済みのエッジリスト
    Raises:
        Exception: ファイル読み込み・データ不整合時

    処理手順:
    - "EBEAM3D"セクション内だけを対象とする
    - # 行で部材種別切替
    - 2つ以上の数値→エッジ（ID重複・異常値・種別不一致は除外）
    - 必要に応じてログに詳細を記録
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

                # 種別ID定義（# 53 柱 など）
                m_kind = re.match(r"#\s*(\d+)\s*(.+)?", line_strip)
                if m_kind:
                    current_kind_id = int(m_kind.group(1))
                    current_kind_label = KIND_LABELS.get(
                        current_kind_id, m_kind.group(2) or "unknown"
                    )
                    log.debug(
                        f"EBEAM3D: kind_id={current_kind_id}, label={current_kind_label}"
                    )
                    continue

                # ノードペア行（整数2つ以上の行）
                nums = [int(n) for n in re.findall(r"\d+", line_strip)]
                if len(nums) < 2 or current_kind_id is None:
                    continue
                node_a_id, node_b_id = nums[-2], nums[-1]

                # 異常ID・重複を徹底除外
                if node_a_id <= 0 or node_b_id <= 0 or node_a_id == node_b_id:
                    abnormal_skip_count += 1
                    continue

                # 種別フィルタ＆両ノード存在＆kind_id合致を厳密確認
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
                    edges.append(
                        EdgeData(
                            node_a=node_a_id,
                            node_b=node_b_id,
                            kind_id=current_kind_id,
                            kind_label=current_kind_label,
                        )
                    )
                    log.info(
                        f"Added edge: ({node_a_id}, {node_b_id}), #{current_kind_id}"
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
