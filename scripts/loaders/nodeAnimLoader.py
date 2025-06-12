"""
アニメーションデータローダ
- ノードごとのフレーム毎変位データを辞書形式でロード
- DISP列の自動抽出とスケーリング・ノード/成分単位で厳密管理

【設計・注意点】
- CSVは(TYPE)(CMP)(ID)ヘッダ3行＋データ本体
- DISPで始まる列のみを自動判別・col_mapで管理
- ノードID/成分インデックス等すべて厳密バリデーション
- 各フレームごとにVector格納、スケール変換
"""

import csv
from collections import defaultdict
from typing import Dict
from mathutils import Vector
from utils.logging_utils import setup_logging
from configs import NODE_ANIM_CSV, VALID_NODE_IDS, ANIM_FPS, DISP_SCALE

log = setup_logging()

TYPE_HEADER = "(TYPE)"
CMP_HEADER = "(CMP)"
ID_HEADER = "(ID)"


def load_animation_data(path: str = NODE_ANIM_CSV) -> Dict[int, Dict[int, Vector]]:
    """
    アニメーションCSVを解析し、
    ノードID→{フレーム: 変位Vector}の2重辞書にして返す

    Args:
        path (str): アニメーションCSVファイルパス（省略時はconfig値）
    Returns:
        Dict[int, Dict[int, Vector]]:
            ノードID→{フレーム: Vector(dx,dy,dz)}の辞書
            例: { node_id: { frame: Vector(dx,dy,dz), ... }, ... }
    Raises:
        RuntimeError/Exception: ファイル/ヘッダ/データ不正時

    【内部処理詳細】
    - (TYPE)(CMP)(ID)の3段ヘッダを自動解析
    - DISP列のみを抽出・有効なノードIDだけcol_mapに格納
    - CSV各行を時間→フレームへ変換、各値をスケール変換
    - 不正値・列不足はログ警告してスキップ
    """
    log.info("=================[アニメーション情報を読み取り]=========================")
    log.info(f"Reading animation data from: {path}")
    rows = []
    try:
        with open(path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except Exception as e:
        log.critical(f"[{path}] CRITICAL: Failed to open/read animation CSV ({e})")
        raise

    type_row = None
    cmp_row = None
    id_row = None
    for i, row in enumerate(rows):
        if not row:
            continue
        tag = row[0].strip().upper()
        if tag.startswith(TYPE_HEADER):
            type_row = row
        elif tag.startswith(CMP_HEADER):
            cmp_row = row
        elif tag.startswith(ID_HEADER):
            id_row = row
        if type_row and cmp_row and id_row:
            header_end = i
            break

    if not (type_row and cmp_row and id_row):
        log.critical(f"[{path}] HEADER rows (TYPE/CMP/ID) not found in animation CSV.")
        raise RuntimeError("Invalid animation CSV header")

    data_start = header_end + 2
    if data_start >= len(rows):
        log.critical(f"[{path}] No data rows found after header in animation CSV.")
        raise RuntimeError("No data rows in animation CSV")

    # col_map: {カラムindex: (ノードID, XYZインデックス)} を構築
    col_map: Dict[int, tuple[int, int]] = {}
    for j in range(1, len(id_row)):
        typ = type_row[j].strip().upper() if j < len(type_row) else ""
        if typ != "DISP":
            continue
        try:
            comp = int(cmp_row[j].strip())
        except Exception as e:
            log.warning(
                f"[{path}] Failed to parse CMP col {j} at header: {cmp_row} ({e})"
            )
            continue
        if comp not in (1, 2, 3):
            continue
        try:
            nid = int(id_row[j].strip())
        except Exception as e:
            log.warning(
                f"[{path}] Failed to parse node ID at header col {j}: {id_row} ({e})"
            )
            continue
        if nid not in VALID_NODE_IDS:
            continue
        col_map[j] = (nid, comp - 1)

    if not col_map:
        log.critical(f"[{path}] No DISP columns found for valid nodes.")
        raise RuntimeError("No valid DISP columns in animation CSV")

    log.info(f"→ Found {len(col_map)} DISP columns for valid nodes")

    # アニメーションデータ本体の読み込み
    anim_data: Dict[int, Dict[int, Vector]] = defaultdict(
        lambda: defaultdict(lambda: Vector((0.0, 0.0, 0.0)))
    )
    for lineno, row in enumerate(rows[data_start:], start=data_start + 1):
        if not row or not row[0].strip():
            continue
        try:
            t_sec = float(row[0].strip())
        except Exception as e:
            log.warning(
                f"[{path}] [Line {lineno}] Skipping invalid time: {row[0]} ({e})"
            )
            continue
        frame = int(round(t_sec * ANIM_FPS))
        for j, (nid, comp_idx) in col_map.items():
            if j >= len(row):
                log.debug(f"[{path}] [Line {lineno}] Missing column {j}, skipping")
                continue
            val_s = row[j].strip()
            if not val_s:
                continue
            try:
                disp = float(val_s) * DISP_SCALE
            except Exception as e:
                log.warning(
                    f"[{path}] [Line {lineno}] Skipping invalid number at col {j}, node {nid}: {val_s} ({e})"
                )
                continue
            anim_data[nid][frame][comp_idx] = disp

    # defaultdict→通常dictへ変換して返す
    result: Dict[int, Dict[int, Vector]] = {}
    for nid, frames in anim_data.items():
        result[nid] = {}
        for frame, vec in frames.items():
            result[nid][frame] = vec

    log.info(
        f"Loaded animation data: {len(result)} nodes, up to {max((len(f) for f in result.values()), default=0)} frames"
    )
    return result
