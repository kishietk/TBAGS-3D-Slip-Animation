import csv
from mathutils import Vector
from config import NODE_CSV, VALID_NODE_IDS
from logging_utils import setup_logging

log = setup_logging()

def load_nodes(path=NODE_CSV):
    log.info(f"Reading node data from: {path}")
    nodes = {}
    with open(path, newline='', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) < 4: continue
            try:
                nid = int(row[0])
                if nid not in VALID_NODE_IDS: continue
                x, y, z = map(float, row[1:4])
                nodes[nid] = Vector((x, y, z))
            except Exception as e:
                log.info(f"Skipping row: {row} ({e})")
    log.info(f"Loaded {len(nodes)} nodes")
    return nodes
