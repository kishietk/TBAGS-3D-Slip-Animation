"""
edge.py

【役割】
- STRファイルから「有効ノードペア」だけを抽出してsetで返すローダ。
- "EBEAM3D"ブロックの開始・終了を認識し、階層ごとのノードIDや特殊ノードもconfig.pyから自動参照。
- 異常データ・パース失敗時は「どのファイル・何行目・何データ」で起きたか詳細にログ出力。

【設計方針】
- VALID_NODE_IDSは階層ごと・特殊ノードごとにconfig.pyで管理し、合成(set)でダブり撲滅＆追跡性UP。
- suspicious edge等の特殊チェックペアもconfig.py管理・意味をコメントで明示。
- 例外/異常はなるべく詳細ログ＋致命的ならraise（fail-fast）。
- 型ヒント徹底で保守性・IDE補完も強化。
"""

import csv
import re
from typing import Set, Tuple
from mathutils import Vector
from config import (
    EDGES_FILE,
    VALID_NODE_IDS,
    SUSPICIOUS_EDGE_TARGETS,
)
from logging_utils import setup_logging

log = setup_logging()


def load_edges(path: str = EDGES_FILE) -> set[tuple[int, int]]:
    """
    STRファイルからエッジ情報（ノードペア）を抽出する関数

    引数:
        path: エッジ情報が記載されたSTRファイルパス

    戻り値:
        edges: set((node_id_1, node_id_2), ...)

    備考:
        - "EBEAM3D" ブロック内のみを対象
        - VALID_NODE_IDS に含まれるノードペアのみ抽出
        - suspicious edgeターゲットはconfig.pyで一元管理
        - 不正データやパース失敗時も詳細ログ出力
    """
    log.info(f"Reading edge data from: {path}")
    edges: set[tuple[int, int]] = set()

    in_target_block = False
    suspicious_targets = SUSPICIOUS_EDGE_TARGETS
    suspicious_found = set()
    printed_lines = 0
    MAX_LOG_LINES = 20

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, 1):
                line_strip = line.strip()

                if "EBEAM3D" in line:
                    in_target_block = True
                    log.info(f"[{path}] [Line {lineno}] ▶ Start EBEAM3D block")
                    continue

                if in_target_block and "#=" in line_strip:
                    in_target_block = False
                    log.info(f"[{path}] [Line {lineno}] ◀ End EBEAM3D block")
                    continue

                if not in_target_block:
                    continue

                if "THRU" in line.upper():
                    log.info(
                        f"[{path}] [Line {lineno}] Ignored (THRU syntax): {line_strip}"
                    )
                    continue

                # 数字抽出と有効ノード判定
                try:
                    nums = [int(n) for n in re.findall(r"\d+", line)]
                except Exception as e:
                    log.error(
                        f"[{path}] [Line {lineno}] Failed to parse int from: {line_strip} ({e})"
                    )
                    continue

                valid = [n for n in nums if n in VALID_NODE_IDS]

                if len(valid) == 2:
                    a, b = sorted(valid)
                    edges.add((a, b))
                    if (a, b) in suspicious_targets and (a, b) not in suspicious_found:
                        log.warning(
                            f"[{path}] [Line {lineno}] Found suspicious edge: ({a}, {b})"
                        )
                        suspicious_found.add((a, b))
                    elif printed_lines < MAX_LOG_LINES:
                        printed_lines += 1
                elif len(valid) > 2 and printed_lines < MAX_LOG_LINES:
                    log.warning(
                        f"[{path}] [Line {lineno}] Ignored (too many valid nodes): {valid}"
                    )
                    printed_lines += 1
                elif len(valid) == 1 and printed_lines < MAX_LOG_LINES:
                    log.warning(
                        f"[{path}] [Line {lineno}] Ignored (only one valid node): {valid}"
                    )
                    printed_lines += 1
    except Exception as e:
        log.critical(f"[{path}] CRITICAL: Failed to read edge STR ({e})")
        raise  # fail-fast

    log.info(f"Total valid edges from {path}: {len(edges)}")
    return edges
