"""
node.py

【役割】
- ノード座標CSVを辞書形式で読み込むローダ
- ヘッダー行等の明らかな非データ行はWARNING、それ以外のパース失敗はERRORでログ
- 定数・ファイルパスはconfig.pyで集中管理

【設計方針】
- エラー時の行番号・内容・例外原因も必ず出力
- 型ヒント・運用コメントも現場水準で徹底
"""

import csv
from typing import Dict
from mathutils import Vector
from config import NODE_CSV, VALID_NODE_IDS
from logging_utils import setup_logging

log = setup_logging()

# 明らかにヘッダーや非データ行と判別できるキーワードリスト
HEADER_KEYWORDS = ("frame contact", "接点", "node id", "header", "column", "row")


def load_nodes(path: str = NODE_CSV) -> dict[int, Vector]:
    """
    ノード座標CSVを辞書として読み込むユーティリティ

    引数:
        path: ノードCSVファイルパス

    戻り値:
        nodes: { node_id: Vector(x, y, z), ... }

    備考:
        - 1列目: ノードID
        - 2-4列目: X, Y, Z座標
        - VALID_NODE_IDS に含まれないIDはスキップ
        - 明らかにヘッダー行（キーワード一致）はWARNINGでログ、それ以外はERROR
    """
    log.info(f"Reading node data from: {path}")
    nodes: dict[int, Vector] = {}
    try:
        with open(path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            next(reader, None)  # 1行目ヘッダーをスキップ（追加の冗長防止）
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
        raise  # fail-fast設計
    log.info(f"Loaded {len(nodes)} nodes from {path}")
    return nodes
