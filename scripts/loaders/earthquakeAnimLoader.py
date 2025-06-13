"""
ファイル名: loaders/earthquakeAnimLoader.py

責務:
- 地震の基準面アニメーションCSVをロードし、{フレーム番号: Vector(dx, dy, dz)}形式で返す専用ローダ。
- ファイル先頭2行ヘッダ＋[時刻,変位]形式のCSVに対応。

TODO:
- 列数やヘッダ行数が異なるCSVにも柔軟に対応できるよう拡張
- dx以外（dy, dz）成分にも将来対応する場合はロジックを調整
- 単体テスト容易な形でfile-likeオブジェクト入力対応も検討
"""

import csv
from typing import Dict
from mathutils import Vector
from utils.logging_utils import setup_logging
from configs import ANIM_FPS, DISP_SCALE, EARTHQUAKE_ANIM_CSV

log = setup_logging("earthquakeAnimLoader")


def load_earthquake_motion_csv(path: str = EARTHQUAKE_ANIM_CSV) -> Dict[int, Vector]:
    """
    役割:
        地震の基準面変位CSVをロードし、
        {フレーム番号: Vector(dx, dy, dz)}形式の辞書で返す。

    引数:
        path (str): CSVファイルパス（デフォルト: EARTHQUAKE_ANIM_CSV）

    返り値:
        Dict[int, Vector]: {フレーム番号: Vector(dx, dy, dz)}

    例外:
        Exception: ファイルオープンやパース失敗時に発生
    """
    log.info("=================[地震基準面アニメCSV読込]=========================")
    log.info(f"Reading earthquake animation data from: {path}")
    frame_data: Dict[int, Vector] = {}
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            next(reader, None)  # 例: Kumamoto Earthquake,,,Kumamoto Earthquake,
            next(reader, None)  # 例: Time  (s),Disp. (mm),,Time  (s),Disp. (mm)

            for lineno, row in enumerate(reader, start=3):
                if not row or not row[0].strip() or not row[1].strip():
                    continue
                try:
                    t_sec = float(row[0].strip())
                    frame = int(round(t_sec * ANIM_FPS))
                    dx = float(row[1]) * DISP_SCALE / 1000  # mm to m
                    dy = 0.0
                    dz = 0.0
                    frame_data[frame] = Vector((dx, dy, dz))
                except Exception as e:
                    log.warning(f"[Line {lineno}] Skipping row: {row} (error: {e})")
    except Exception as e:
        log.critical(f"[{path}] CRITICAL: Failed to open/read earthquake CSV ({e})")
        raise

    return frame_data
