import csv
from mathutils import Vector
from config import ANIM_CSV, VALID_NODE_IDS
from logging_utils import setup_logging

log = setup_logging()

def load_animation_data(path=ANIM_CSV):
    """
    戻り値: {
        node_id1: { frame0: Vector(dx,dy,dz), frame1: …, … },
        node_id2: { … },
        …
    }
    """
    log.info(f"Reading animation data from: {path}")
    anim = {}
    try:
        with open(path, newline='', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    nid = int(row["node_id"])
                    if nid not in VALID_NODE_IDS:
                        continue
                    frame = int(row["time"])
                    offset = Vector((
                        float(row["dx"]),
                        float(row["dy"]),
                        float(row["dz"])
                    ))
                    anim.setdefault(nid, {})[frame] = offset
                except Exception as e:
                    log.info(f"Skipping anim row: {row} ({e})")
    except FileNotFoundError:
        log.info(f"Animation file not found: {path}")
    log.info(f"Loaded animation data for {len(anim)} nodes")
    return anim
