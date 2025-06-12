"""
熊本地震基準面アニメーションCSV専用ローダ
- 先頭2行ヘッダ＋[時刻,変位]形式のデータに対応
- DISP_SCALEでスケーリング（mm→m換算はconfig側で指定）
- 空白・異常値徹底バリデーション
- ログ詳細出力
"""

import csv
from typing import Dict
from mathutils import Vector
from utils.logging_utils import setup_logging
from configs import ANIM_FPS, DISP_SCALE, EARTHQUAKE_ANIM_CSV

log = setup_logging("earthquakeAnimLoader")


def load_earthquake_motion_csv(path: str = EARTHQUAKE_ANIM_CSV) -> Dict[int, Vector]:
    """
    熊本地震の基準面変位CSVをロードし、{フレーム番号: Vector(dx,dy,dz)}形式で返す
    - 先頭2行をスキップ
    - 1列目: 時刻[秒], 2列目: 変位[mm]（スケール換算）以外は無視
    Returns:
        Dict[int, Vector]: {フレーム: Vector(dx,dy,dz)}
    Raises:
        Exception: ファイルやパース異常時
    """
    log.info("=================[地震基準面アニメCSV読込]=========================")
    log.info(f"Reading earthquake animation data from: {path}")
    frame_data: Dict[int, Vector] = {}
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            header1 = next(
                reader, None
            )  # 例: Kumamoto Earthquake,,,Kumamoto Earthquake,
            header2 = next(
                reader, None
            )  # 例: Time  (s),Disp. (mm),,Time  (s),Disp. (mm)
            
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
                    continue
    except Exception as e:
        log.critical(f"[{path}] CRITICAL: Failed to open/read earthquake CSV ({e})")
        raise

    return frame_data
