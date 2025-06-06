"""
ノード情報ロードユーティリティ
- ノード定義ファイル（STR/CSV）をパースして辞書形式で返す
- kind_idの自動割当、コメント/セクション解析、T-BAG区間の特殊判定も実装
- VALID_NODE_IDSによりプロジェクトで許可されたIDのみ採用
"""

import re
from typing import Dict, NamedTuple
from mathutils import Vector
from config import NODE_CSV, NODE_SECTION_NUMBERS, VALID_NODE_IDS
from utils.logging_utils import setup_logging

log = setup_logging()  # configのLOG_LEVELから出力レベル設定


class NodeData(NamedTuple):
    """
    ノード1点の座標・種別kind_idを格納するデータ型
    属性:
        pos (Vector): 座標(XYZ)
        kind_id (int): ノード種別番号
    """

    pos: Vector
    kind_id: int


def load_nodes(path: str = NODE_CSV) -> Dict[int, NodeData]:
    """
    ノード定義ファイル(.str/.csv)を読み込み、
    kind_id（区分）・セクション・TBAG区間判定も含めて
    ノードID→NodeDataの辞書として返す。

    Args:
        path (str): 読み込むノードファイルパス
    Returns:
        Dict[int, NodeData]: ノードID→NodeDataの辞書
    Raises:
        Exception: ファイル読み込み・解析失敗時は例外
    """
    log.info("=================[ノード情報を読み取り]=========================")
    nodes: Dict[int, NodeData] = {}

    section_pattern = re.compile(r"#\s*(\d+)")
    valid_sections = set(NODE_SECTION_NUMBERS)
    current_kind_id = None
    tbag_section_active = False

    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            for row_idx, line in enumerate(f, start=1):
                line_strip = line.strip()
                # セクション見出し（例: #1, #2, ...）検出
                m_section = section_pattern.match(line_strip)
                if m_section:
                    sec = int(m_section.group(1))
                    if sec == 1:
                        current_kind_id = 1
                        tbag_section_active = False
                        log.debug(f"[{path}] Section #1 entered at row {row_idx}")
                    elif sec == 2:
                        current_kind_id = 2
                        tbag_section_active = False
                        log.debug(f"[{path}] Section #2 entered at row {row_idx}")
                    else:
                        current_kind_id = sec if sec in valid_sections else None
                        tbag_section_active = False
                        log.debug(f"[{path}] Section #{sec} entered at row {row_idx}")
                    continue

                # TBAG区間開始コメント検出
                if "#Top of Upper level T-BAGS connected to Columns" in line_strip:
                    tbag_section_active = True
                    log.debug(f"[{path}] TBAG section started at row {row_idx}")
                    continue

                # 空行・コメント行・無効セクションはスキップ
                if (
                    current_kind_id is None
                    or not line_strip
                    or line_strip.startswith("#")
                ):
                    continue

                # ノード行検出
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
                        # TBAG区間中はkind_id=0を強制割当
                        if tbag_section_active:
                            kind_id = 0
                        else:
                            kind_id = current_kind_id
                        nodes[nid] = NodeData(Vector((x, y, z)), kind_id)
                        log.info(f"Added node : ID = {nid}, #{kind_id}")
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
