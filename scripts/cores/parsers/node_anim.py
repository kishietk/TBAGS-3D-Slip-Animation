# core/parsers/node_anim.py

import csv
from collections import defaultdict
from typing import Dict
from mathutils import Vector
from .base import BaseParser
from utils import setup_logging
from configs import (
    VALID_NODE_IDS,
    ANIM_FPS,
    DISP_SCALE,
    TYPE_HEADER,
    CMP_HEADER,
    ID_HEADER,
)

log = setup_logging("NodeAnimParser")


class NodeAnimParser(BaseParser):
    """
    ノードアニメーションCSVを直接パースし、
    ノードIDごとにフレーム→変位ベクトルの2重辞書を返すParser。
    - (TYPE)(CMP)(ID)の3段ヘッダを検出し、DISP列のみを対象
    - VALID_NODE_IDSで有効ノードをフィルタ
    - スケーリング(DISP_SCALE)とフレーム変換(ANIM_FPS)
    - 異常値や不足データはログ記録の上スキップ

    CSVフォーマット例:
        TYPE, DISP, DISP, DISP, ...
        CMP, 1,    2,    3,    ...
        ID,  1001, 1001, 1001, ...
        # 空行
        time(s), x,   y,   z,   ...
        0.00,     0.1, 0.0, 0.0, ...
        ...
    """

    def parse(self, path: str) -> Dict[int, Dict[int, Vector]]:
        log.info(f"[NodeAnimParser] Loading animation CSV: {path}")
        # ファイル全行読み込み
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                rows = list(reader)
        except Exception as e:
            log.critical(f"Failed to open animation CSV {path}: {e}")
            raise

        # ヘッダ行(TYPE_HEADER, CMP_HEADER, ID_HEADER)検出
        type_row = cmp_row = id_row = None
        header_end = None
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
            log.critical("CSV header rows (TYPE/CMP/ID) not found")
            raise RuntimeError("Invalid animation CSV header")

        data_start = header_end + 2
        if data_start >= len(rows):
            log.critical("No data rows found after animation CSV header")
            raise RuntimeError("No animation data rows")

        # DISP列のみを抽出するcol_map構築: {col_index: (nid, comp_idx)}
        col_map: Dict[int, tuple[int, int]] = {}
        for j in range(1, len(id_row)):
            typ = type_row[j].strip().upper() if j < len(type_row) else ""
            if typ != "DISP":
                continue
            try:
                comp = int(cmp_row[j].strip())
                nid = int(id_row[j].strip())
            except Exception:
                log.warning(f"Invalid CMP/ID at col {j}")
                continue
            # comp: 1->X,2->Y,3->Z
            if comp not in (1, 2, 3) or nid not in VALID_NODE_IDS:
                continue
            col_map[j] = (nid, comp - 1)

        if not col_map:
            log.critical("No valid DISP columns found in animation CSV")
            raise RuntimeError("No DISP columns")

        log.info(f"Detected {len(col_map)} DISP columns for valid nodes")

        # データ読み込みとベクトル格納
        anim_data: Dict[int, Dict[int, Vector]] = defaultdict(
            lambda: defaultdict(lambda: Vector((0.0, 0.0, 0.0)))
        )
        for lineno, row in enumerate(rows[data_start:], start=data_start + 1):
            if not row or not row[0].strip():
                continue
            try:
                t_sec = float(row[0].strip())
            except Exception:
                log.warning(f"[Line {lineno}] Invalid time value: {row[0]}")
                continue
            frame = int(round(t_sec * ANIM_FPS))
            for j, (nid, comp_idx) in col_map.items():
                if j >= len(row):
                    continue
                val = row[j].strip()
                if not val:
                    continue
                try:
                    disp = float(val) * DISP_SCALE
                except Exception:
                    log.warning(f"[Line {lineno}] Invalid DISP at col {j}: {val}")
                    continue
                anim_data[nid][frame][comp_idx] = disp

        # defaultdictから通常dictへ変換して返却
        result: Dict[int, Dict[int, Vector]] = {}
        for nid, frames in anim_data.items():
            result[nid] = {f: v for f, v in frames.items()}

        log.info(f"Loaded animation for {len(result)} nodes")
        return result
