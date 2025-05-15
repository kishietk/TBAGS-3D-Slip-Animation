import csv
from mathutils import Vector
from config import EDGES_FILE, VALID_NODE_IDS
from logging_utils import setup_logging
import re

log = setup_logging()

# ───────────────────────────────
# エッジ読み込み（#42〜#53ブロック限定）
# ───────────────────────────────
def load_edges(path=EDGES_FILE):
    log.info(f"Reading edge data from: {path}")
    edges = set()

    in_target_block = False
    suspicious_targets = [(201, 208), (301, 308), (401, 408)]
    suspicious_found = set()
    printed_lines = 0
    MAX_LOG_LINES = 20

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for lineno, line in enumerate(f, 1):
            line_strip = line.strip()

            # ── ブロック開始（EBEAM3D） ──
            if "EBEAM3D" in line:
                in_target_block = True
                log.info(f"[Line {lineno}] ▶ Start EBEAM3D block")
                continue

            # ── ブロック終了（==== 区切り） ──
            if in_target_block and "#=" in line_strip:
                in_target_block = False
                log.info(f"[Line {lineno}] ◀ End EBEAM3D block")
                continue

            if not in_target_block:
                continue

            if "THRU" in line.upper():
                log.info(f"[Line {lineno}] Ignored (THRU syntax): {line_strip}")
                continue

            # 数字抽出とノード判定
            nums = [int(n) for n in re.findall(r"\d+", line)]
            valid = [n for n in nums if n in VALID_NODE_IDS]

            if len(valid) == 2:
                a, b = sorted(valid)
                edges.add((a, b))
                if (a, b) in suspicious_targets and (a, b) not in suspicious_found:
                    # log.info(f"⚠️ Suspicious edge added: ({a}, {b}) from line {lineno}: {line_strip}")
                    suspicious_found.add((a, b))
                elif printed_lines < MAX_LOG_LINES:
                    # log.info(f"[Line {lineno}] Edge added: ({a}, {b})")
                    printed_lines += 1
            elif len(valid) > 2 and printed_lines < MAX_LOG_LINES:
                log.info(f"[Line {lineno}] Ignored (too many valid nodes): {valid}")
                printed_lines += 1
            elif len(valid) == 1 and printed_lines < MAX_LOG_LINES:
                log.info(f"[Line {lineno}] Ignored (only one valid node): {valid}")
                printed_lines += 1

    log.info(f"Total valid edges: {len(edges)}")
    return edges