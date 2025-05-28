import re
from typing import Dict, NamedTuple
from mathutils import Vector
from config import NODE_CSV, NODE_SECTION_NUMBERS, VALID_NODE_IDS
from utils.logging_utils import setup_logging

log = setup_logging()


class NodeData(NamedTuple):
    pos: Vector
    kind_id: int


def load_nodes(path: str = NODE_CSV) -> Dict[int, NodeData]:
    """
    self.strから指定IDのノード座標・kind_id（セクション番号）辞書を生成
    戻り値:
        ノードIDをキー、NodeData（pos, kind_id）を値とする辞書
    """
    log.info(f"Reading node data from: {path}")
    nodes: Dict[int, NodeData] = {}

    section_pattern = re.compile(r"#\s*(\d+)")
    valid_sections = set(NODE_SECTION_NUMBERS)
    current_section = None

    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            for row_idx, line in enumerate(f, start=1):
                line_strip = line.strip()
                # セクション開始検出
                m_section = section_pattern.match(line_strip)
                if m_section:
                    sec = int(m_section.group(1))
                    if sec in valid_sections:
                        current_section = sec
                        log.info(f"[{path}] Section #{sec} entered at row {row_idx}")
                    else:
                        current_section = None
                    continue

                if (
                    current_section is None
                    or not line_strip
                    or line_strip.startswith("#")
                ):
                    continue

                # ノード行の検出（例: 201  3D  0.900  0.900  3.200）
                m_node = re.match(
                    r"(\d+)\s+\S+\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)", line_strip
                )
                if m_node:
                    nid = int(m_node.group(1))
                    if nid not in VALID_NODE_IDS:
                        log.debug(
                            f"[{path}]  ID {nid} at row {row_idx}: not in VALID_NODE_IDS"
                        )
                        continue
                    try:
                        x, y, z = (
                            float(m_node.group(2)),
                            float(m_node.group(3)),
                            float(m_node.group(4)),
                        )
                        # kind_id = 現在のセクション番号
                        nodes[nid] = NodeData(Vector((x, y, z)), current_section)
                        log.info(
                            f"Added node {nid}: ({x}, {y}, {z}), kind_id={current_section}"
                        )
                    except Exception as e:
                        log.error(
                            f"[{path}] Failed to parse XYZ at row {row_idx}, node ID {nid}: {line_strip} ({e})"
                        )
                        continue
                else:
                    log.debug(
                        f"[{path}] Skipped non-node line at row {row_idx}: {line_strip}"
                    )

    except Exception as e:
        log.critical(f"[{path}] CRITICAL: Failed to read node STR ({e})")
        raise

    log.info(f"Loaded {len(nodes)} nodes from {path}")
    return nodes
