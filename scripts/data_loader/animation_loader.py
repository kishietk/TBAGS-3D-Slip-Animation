# scripts/data_loader/animation_loader.py

import csv
from collections import defaultdict
from mathutils import Vector
from logging_utils import setup_logging
from config import ANIM_CSV, VALID_NODE_IDS, ANIM_FPS, DISP_SCALE

log = setup_logging()

def load_animation_data(path=ANIM_CSV):
    """
    本番のアニメーション CSV から、
    { node_id: { frame: Vector(dx,dy,dz), ... }, ... }
    の辞書を返す。
    CSV の構造:
    行0: タイトル行
    行1: HISTORY
    行2: (TYPE)   DISP or ACC など
    行3: (CMP)    1,2,3（X,Y,Z 成分）
    行4: (ID)     ノードID
    行5: 空行
    行6以降: 時刻＋数値データ
    """
    log.info(f"Reading animation data from: {path}")
    rows = []
    try:
        with open(path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except FileNotFoundError:
        log.warning(f"Animation file not found: {path}")
        return {}

    # ヘッダ行を探す
    type_row = None
    cmp_row  = None
    id_row   = None
    for i, row in enumerate(rows):
        if not row: continue
        tag = row[0].strip().upper()
        if tag.startswith("(TYPE)"):
            type_row = row
        elif tag.startswith("(CMP)"):
            cmp_row = row
        elif tag.startswith("(ID)"):
            id_row = row
        if type_row and cmp_row and id_row:
            header_end = i  # ID 行のインデックス
            break

    if not (type_row and cmp_row and id_row):
        log.error("HEADER rows (TYPE/CMP/ID) not found in animation CSV.")
        return {}

    # データ開始行は ID 行の２行下（空行を挟んで）
    data_start = header_end + 2
    if data_start >= len(rows):
        log.error("No data rows found after header in animation CSV.")
        return {}

    # DISP 列だけを集める
    # col_map: col_index → (node_id, comp_index 0=x,1=y,2=z)
    col_map = {}
    for j in range(1, len(id_row)):
        typ = type_row[j].strip().upper() if j < len(type_row) else ""
        if typ != "DISP":
            continue
        # CMP 行から成分番号取得
        try:
            comp = int(cmp_row[j].strip())
        except:
            continue
        if comp not in (1,2,3):
            continue
        # ID 行からノードID取得
        try:
            nid = int(id_row[j].strip())
        except:
            continue
        if nid not in VALID_NODE_IDS:
            continue
        col_map[j] = (nid, comp-1)

    if not col_map:
        log.error("No DISP columns found for valid nodes.")
        return {}

    log.info(f"→ Found {len(col_map)} DISP columns for valid nodes")

    # データ読み込み
    # anim_data[node_id][frame] = Vector(dx,dy,dz)
    anim_data = defaultdict(lambda: defaultdict(lambda: Vector((0.0,0.0,0.0))))
    for lineno, row in enumerate(rows[data_start:], start=data_start+1):
        if not row or not row[0].strip():
            continue
        # 時刻（秒） → フレーム
        try:
            t_sec = float(row[0].strip())
        except:
            log.debug(f"[Line {lineno}] Skipping invalid time: {row[0]}")
            continue
        frame = int(round(t_sec * ANIM_FPS))

        # 各 DISP 列を読んでベクトルを埋める
        for j, (nid, comp_idx) in col_map.items():
            if j >= len(row):
                log.debug(f"[Line {lineno}] Missing column {j}, skipping")
                continue
            val_s = row[j].strip()
            if not val_s:
                continue
            try:
                disp = float(val_s) * DISP_SCALE
            except:
                log.debug(f"[Line {lineno}] Skipping invalid number at col {j}: {val_s}")
                continue
            anim_data[nid][frame][comp_idx] = disp


    # Vector 生成
    result = {}
    for nid, frames in anim_data.items():
        result[nid] = {}
        for frame, vec in frames.items():
            result[nid][frame] = vec

    log.info(f"Loaded animation data: {len(result)} nodes, up to {max((len(f) for f in result.values()), default=0)} frames")
    return result
