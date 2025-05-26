# ノード座標CSVローダ
# ノードIDと座標(Vector)の辞書を生成する

import csv
from typing import Dict
from mathutils import Vector
from config import NODE_CSV, VALID_NODE_IDS
from utils.logging_utils import setup_logging

log = setup_logging()

HEADER_KEYWORDS = ("frame contact", "接点", "node id", "header", "column", "row")


def load_nodes(path: str = NODE_CSV) -> Dict[int, Vector]:
    """
    ノード座標CSVを読み込む
    引数:
        path: ノード座標CSVファイルパス（省略時は設定値）
    戻り値:
        ノードIDをキー、座標Vectorを値とする辞書
    """
    log.info(f"Reading node data from: {path}")
    nodes: Dict[int, Vector] = {}
    try:
        with open(path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            next(reader, None)  # 1行目はヘッダーとしてスキップ
            for row_idx, row in enumerate(reader, start=2):
                if len(row) < 4:
                    log.error(
                        f"[{path}] Skipping row {row_idx}: Not enough columns: {row}"
                    )
                    continue
                try:
                    nid = int(row[0])
                except Exception as e:
                    val = str(row[0]).strip().lower()
                    if any(x in val for x in HEADER_KEYWORDS):
                        log.warning(
                            f"[{path}] Skipping header row at row {row_idx}: {row}"
                        )
                    else:
                        log.error(
                            f"[{path}] Failed to parse node ID at row {row_idx}: {row} ({e})"
                        )
                    continue

                if nid not in VALID_NODE_IDS:
                    log.debug(
                        f"[{path}] Skipped node ID {nid} at row {row_idx}: not in VALID_NODE_IDS"
                    )
                    continue

                try:
                    x, y, z = map(float, row[1:4])
                except Exception as e:
                    log.error(
                        f"[{path}] Failed to parse XYZ at row {row_idx}, node ID {nid}: {row} ({e})"
                    )
                    continue

                nodes[nid] = Vector((x, y, z))
    except Exception as e:
        log.critical(f"[{path}] CRITICAL: Failed to read node CSV ({e})")
        raise
    log.info(f"Loaded {len(nodes)} nodes from {path}")
    return nodes
