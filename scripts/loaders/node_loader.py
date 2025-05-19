import csv
from typing import Dict
from mathutils import Vector
from config import NODE_CSV, VALID_NODE_IDS
from logging_utils import setup_logging

"""
node_loader.py

【役割 / Purpose】
- ノード座標CSV（node_position.csv）を「ノードID→座標(Vector)」の辞書として読み込むローダ関数を提供。
- 定数やファイルパスは必ずconfig.pyからimport。

【設計方針】
- 行のパース失敗時は必ずエラー・行番号・内容を詳細ログ出力。
- 明らかなヘッダー・非データ行はWARNING、それ以外はERROR。
- VALID_NODE_IDS以外のIDはスキップ。
- 型ヒント・現場向けコメント徹底。
"""

log = setup_logging()

# 明らかにヘッダーや非データ行と判定できるキーワード
HEADER_KEYWORDS = ("frame contact", "接点", "node id", "header", "column", "row")


def load_nodes(path: str = NODE_CSV) -> dict[int, Vector]:
    """
    ノード座標CSVを辞書形式で読み込むユーティリティ。

    引数:
        path: ノード座標CSVファイルパス（デフォルトはconfig.pyのNODE_CSV）
    戻り値:
        { node_id: Vector(x, y, z), ... }

    【運用備考】
    - 1列目: ノードID（int）
    - 2,3,4列目: X, Y, Z座標（float）
    - VALID_NODE_IDS以外は読み飛ばし
    - ヘッダー行や明らかにデータでない行も読み飛ばし（WARNINGログ）
    """
    log.info(f"Reading node data from: {path}")
    nodes: dict[int, Vector] = {}
    try:
        with open(path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            next(reader, None)  # 1行目はヘッダー想定でスキップ
            for row_idx, row in enumerate(reader, start=2):  # 2行目以降
                if len(row) < 4:
                    log.error(
                        f"[{path}] Skipping row {row_idx}: Not enough columns: {row}"
                    )
                    continue
                try:
                    nid = int(row[0])
                except Exception as e:
                    val = str(row[0]).strip().lower()
                    # 明らかにヘッダー・キーワード
                    if any(x in val for x in HEADER_KEYWORDS):
                        log.warning(
                            f"[{path}] Skipping header row at row {row_idx}: {row}"
                        )
                    else:
                        log.error(
                            f"[{path}] Failed to parse node ID at row {row_idx}: {row} ({e})"
                        )
                    continue

                # 有効ノードID以外はスキップ
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
        raise  # fail-fast設計
    log.info(f"Loaded {len(nodes)} nodes from {path}")
    return nodes
