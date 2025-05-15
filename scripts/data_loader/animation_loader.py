import csv
from mathutils import Vector
from config import ANIM_CSV, VALID_NODE_IDS
from logging_utils import setup_logging

log = setup_logging()

# ───────────────────────────────
# アニメーション読み込み（未使用時は無視）
# ───────────────────────────────
def load_animation_data(path=ANIM_CSV):
    log.info(f"Reading animation data from: {path}")
    anim = []
    try:
        with open(path, newline='', encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    node_id = int(row["node_id"])
                    if node_id not in VALID_NODE_IDS:
                        continue
                    anim.append({
                        "node_id": node_id,
                        "time": int(row["time"]),
                        "dx": float(row["dx"]),
                        "dy": float(row["dy"]),
                        "dz": float(row["dz"]),
                    })
                except Exception as e:
                    log.info(f"Skipping anim row: {row} ({e})")
    except FileNotFoundError:
        log.info(f"Animation file not found: {path}")
    log.info(f"Loaded {len(anim)} animation keyframes")
    return anim