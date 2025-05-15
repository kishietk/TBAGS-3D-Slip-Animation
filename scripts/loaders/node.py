import csv
from mathutils import Vector
from config import NODE_CSV, VALID_NODE_IDS
from logging_utils import setup_logging

log = setup_logging()


def load_nodes(path=NODE_CSV):
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
    """
    log.info(f"Reading node data from: {path}")
    nodes = {}
    try:
        with open(path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            next(reader, None)  # 1行目ヘッダーをスキップ
            for row in reader:
                if len(row) < 4:
                    continue  # 列数不足はスキップ
                try:
                    nid = int(row[0])
                    if nid not in VALID_NODE_IDS:
                        continue  # 有効ノードID以外はスキップ
                    x, y, z = map(float, row[1:4])
                    nodes[nid] = Vector((x, y, z))
                except Exception as e:
                    log.info(f"Skipping row: {row} ({e})")
    except Exception as e:
        log.error(f"Failed to read node CSV: {e}")
        return {}
    log.info(f"Loaded {len(nodes)} nodes")
    return nodes
