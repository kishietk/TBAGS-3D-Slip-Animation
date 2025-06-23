# scripts/configs/common_patterns.py

import re

# セクション番号コメントパターン
SECTION_PATTERN = re.compile(r"#\s*(\d+)")

# ノード定義パターン
NODE_LINE_PATTERN = re.compile(r"(\d+)\s+\S+\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)")

# エッジ種別パターン
EDGE_KIND_PATTERN = re.compile(r"#\s*(\d+)\s*(.+)?")

# 数字列抽出（エッジノードID抽出用）
EDGE_NODE_IDS_PATTERN = re.compile(r"\d+")

# TBAG判定用
TBAG_SECTION_MARK = "#Top of Upper level T-BAGS connected to Columns"

# EBEAM3D区間開始・終了キーワード
EBEAM3D_START_KEY = "EBEAM3D"
EBEAM3D_END_KEYS = ["#=", "END"]
