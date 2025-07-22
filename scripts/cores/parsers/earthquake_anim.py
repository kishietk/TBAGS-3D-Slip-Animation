# core/parsers/earthquake_anim.py

import csv
from typing import Dict
from mathutils import Vector
from .base import BaseParser
from utils import setup_logging
from configs import (
    ANIM_FPS,
    DISP_SCALE,
    GROUND_ANIMATION_ENABLED,
    EARTHQUAKE_ANIM_CSV,
)

log = setup_logging("EarthquakeAnimParser")


class EarthquakeAnimParser(BaseParser):
    """
    地震の基準面アニメーションCSVをパースし、
    {フレーム番号: Vector(dx, dy, dz)}の辞書を返すParser。

    - 最初の2行ヘッダをスキップ
    - 時刻(s)→フレーム番号(ANIM_FPS換算)
    - DISP列(mm)をメートル換算(DISP_SCALE & /1000)
    - GROUND_ANIMATION_ENABLED=Falseなら空辞書を返す
    """

    def parse(self, path: str = EARTHQUAKE_ANIM_CSV) -> Dict[int, Vector]:
        if not GROUND_ANIMATION_ENABLED:
            log.info("Ground animation disabled, skipping earthquake parsing")
            return {}

        log.info(f"[EarthquakeAnimParser] Loading earthquake CSV: {path}")
        frame_data: Dict[int, Vector] = {}
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                # CSV先頭2行はヘッダ情報
                next(reader, None)
                next(reader, None)
                for lineno, row in enumerate(reader, start=3):
                    # 時刻または変位が空ならスキップ
                    if len(row) < 2 or not row[0].strip() or not row[1].strip():
                        continue
                    try:
                        t_sec = float(row[0].strip())
                        frame = int(round(t_sec * ANIM_FPS))
                        # mm単位の値をスケールとメートル換算
                        disp_mm = float(row[1].strip())
                        dx = disp_mm * DISP_SCALE / 1000
                        # 将来 dy/dz 成分対応可能
                        dy, dz = 0.0, 0.0
                        frame_data[frame] = Vector((dx, dy, dz))
                    except Exception as e:
                        log.warning(
                            f"[Line {lineno}] Skipping row due to parse error: {row} ({e})"
                        )
        except Exception as e:
            log.critical(f"Failed to open/read earthquake CSV {{path}}: {e}")
            raise

        log.info(f"Parsed earthquake animation for {len(frame_data)} frames")
        return frame_data
