import csv
import re
from mathutils import Vector
from config import EDGES_FILE, VALID_NODE_IDS
from logging_utils import setup_logging

log = setup_logging()


def load_edges(path=EDGES_FILE):
    """
    STRファイルからエッジ情報（ノードペア）を抽出する関数
    引数:
        path: エッジ情報が記載されたSTRファイルパス
    戻り値:
        edges: set((node_id_1, node_id_2), ...)
    備考:
        - "EBEAM3D" ブロック内のみを対象
        - VALID_NODE_IDS に含まれるノードペアのみ抽出
        - 2つ以上有効ノードが出てきた場合は2つペアのみ追加
        - THRU構文や不正データはスキップ
    """
    log.info(f"Reading edge data from: {path}")
    edges = set()

    in_target_block = False
    suspicious_targets = [(201, 208), (301, 308), (401, 408)]
    suspicious_found = set()
    printed_lines = 0
    MAX_LOG_LINES = 20

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, 1):
                line_strip = line.strip()

                # --- EBEAM3Dブロック開始検出 ---
                if "EBEAM3D" in line:
                    in_target_block = True
                    log.info(f"[Line {lineno}] ▶ Start EBEAM3D block")
                    continue

                # --- ブロック終了検出（====等の区切り） ---
                if in_target_block and "#=" in line_strip:
                    in_target_block = False
                    log.info(f"[Line {lineno}] ◀ End EBEAM3D block")
                    continue

                if not in_target_block:
                    continue

                if "THRU" in line.upper():
                    log.info(f"[Line {lineno}] Ignored (THRU syntax): {line_strip}")
                    continue

                # --- 数字抽出と有効ノード判定 ---
                nums = [int(n) for n in re.findall(r"\d+", line)]
                valid = [n for n in nums if n in VALID_NODE_IDS]

                if len(valid) == 2:
                    a, b = sorted(valid)
                    edges.add((a, b))
                    if (a, b) in suspicious_targets and (a, b) not in suspicious_found:
                        suspicious_found.add((a, b))
                    elif printed_lines < MAX_LOG_LINES:
                        printed_lines += 1
                elif len(valid) > 2 and printed_lines < MAX_LOG_LINES:
                    log.info(f"[Line {lineno}] Ignored (too many valid nodes): {valid}")
                    printed_lines += 1
                elif len(valid) == 1 and printed_lines < MAX_LOG_LINES:
                    log.info(f"[Line {lineno}] Ignored (only one valid node): {valid}")
                    printed_lines += 1
    except Exception as e:
        log.error(f"Failed to read edge STR: {e}")
        return set()

    log.info(f"Total valid edges: {len(edges)}")
    return edges
