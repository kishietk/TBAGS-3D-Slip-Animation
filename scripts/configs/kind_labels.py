"""
ファイル名: configs/kind_labels.py

責務:
- ノードや部材などの“種別ID”とその分類リスト、ラベル（英語/日本語）、およびIDグルーピングを一元管理。
- プロジェクト内の全「分類・ラベル・グループID」責務を担う（数値定数やパスは責任外）。

設計指針:
- ラベル管理、グルーピング、分類（柱/梁/壁/サンドバッグ等）は全てここで一元化
- 物理値・描画定数はconstants.pyへ、ファイルパス等はpaths.pyへ
- グループID・種別IDの追加・編集が発生した場合は必ずここだけを修正
- 日本語/英語併記やenum化は拡張案として随時追加

TODO:
- 日本語ラベル対応（例: KIND_LABELS_JP等）
- Enum化や、複数分類セットを自動生成するロジックの導入
- 逆引き辞書（ラベル→kind_id）対応
"""

# =========================
# 種別ID→英語ラベルマッピング
# =========================
KIND_LABELS = {
    1: "frame_nodes_and_top_of_upper_level_sandbag_with_foundation_on_top",
    2: "top_of_upper_level_sandbag_without_foundation_on_top",
    3: "bottom_of_upper_level_sandbag_with_foundation_on_top",
    4: "top_of_lower_level_sandbag_with_foundation_on_top",
    5: "bottom_of_lower_sandbag_with_foundation_on_top",
    6: "top_of_lower_sandbag_without_foundation_on_top",
    7: "bottom_of_lower_level_sandbag_without_foundation",
    8: "foundation_beam_x_direction",
    9: "foundation_beam_y_direction",
    10: "foundation_ground_connection_x_direction",
    11: "foundation_ground_connection_y_direction",
    12: "frame_beam_x_direction",
    13: "frame_beam_y_direction",
    14: "frame_beam_connection_x_direction",
    15: "frame_beam_connection_y_direction",
    16: "frame_column_x_direction",
    17: "frame_column_y_direction",
    18: "upper_level_sandbag_connection_x_direction",
    19: "upper_level_sandbag_connection_y_direction",
    20: "lower_level_sandbag_connection_x_direction",
    21: "lower_level_sandbag_connection_y_direction",
    22: "ground_connection_elements_x_direction",
    23: "ground_connection_elements_y_direction",
    24: "upper_sandbag_connecting_beam_x_direction",
    25: "upper_sandbag_connecting_beam_y_direction",
    26: "lower_sandbag_connecting_beam_x_direction",
    27: "lower_sandbag_connecting_beam_y_direction",
    28: "top_of_upper_level_sandbag_connecting_beam_x_direction",
    29: "bottom_of_upper_level_sandbag_connecting_beam_x_direction",
    30: "top_of_upper_level_sandbag_connecting_beam_y_direction",
    31: "bottom_of_upper_level_sandbag_connecting_beam_y_direction",
    32: "top_of_lower_level_sandbag_connecting_beam_x_direction",
    33: "bottom_of_lower_level_sandbag_connecting_beam_x_direction",
    34: "top_of_lower_level_sandbag_connecting_beam_y_direction",
    35: "bottom_of_lower_level_sandbag_connecting_beam_y_direction",
    36: "ground_connecting_elements_x_direction",
    37: "ground_connecting_elements_y_direction",
    38: "top_of_upper_level_sandbag_connecting_beams_x_direction",
    39: "bottom_of_upper_level_sandbag_connecting_beams_x_direction",
    40: "top_of_upper_level_sandbag_connecting_beams_y_direction",
    41: "bottom_of_upper_level_sandbag_connecting_beams_y_direction",
    42: "frame_beam_x_and_y",
    43: "top_of_upper_level_sandbag_connecting_beam_y_direction",
    44: "bottom_of_upper_level_sandbag_connecting_beam_y_direction",
    45: "top_of_lower_sandbag_connecting_beam_y_direction",
    46: "bottom_of_lower_level_sandbag_connecting_beam_y_direction",
    47: "ground_connecting_elements_y_direction",
    48: "top_of_upper_level_sandbag_connecting_beams_x_direction",
    49: "bottom_of_upper_level_sandbag_connecting_beams_x_direction",
    50: "top_of_lower_level_sandbag_connecting_beams_x_direction",
    51: "bottom_of_lower_level_sandbag_connecting_beams_x_direction",
    52: "ground_connecting_elements_x_direction",
    53: "frame_column",
    54: "connecting_bottom_lower_level_sandbag_to_ground_with_foundation_on_top",
    55: "connecting_bottom_of_lower_level_sandbag_to_ground_without_foundation",
    56: "upper_level_sandbag_node",
    57: "lower_level_sandbag_node",
    58: "foundation_node",
    59: "frame_node",
    60: "ground_node",
    61: "connection_node",
    62: "upper_beam_node",
    63: "lower_beam_node",
    64: "upper_column_node",
    65: "lower_column_node",
    66: "upper_level_sandbag_node_x_direction",
    67: "upper_level_sandbag_node_y_direction",
    68: "lower_level_sandbag_node_x_direction",
    69: "lower_level_sandbag_node_y_direction",
    70: "foundation_node_x_direction",
    71: "foundation_node_y_direction",
    72: "frame_node_x_direction",
    73: "frame_node_y_direction",
    74: "ground_node_x_direction",
    75: "ground_node_y_direction",
    76: "connection_node_x_direction",
    77: "connection_node_y_direction",
    78: "upper_beam_node_x_direction",
    79: "upper_beam_node_y_direction",
    80: "lower_beam_node_x_direction",
    81: "lower_beam_node_y_direction",
    82: "upper_column_node_x_direction",
    83: "upper_column_node_y_direction",
    84: "lower_column_node_x_direction",
    85: "lower_column_node_y_direction",
    86: "ground_connecting_element_node",
    87: "frame_beam_node",
    88: "frame_column_node",
    89: "upper_level_sandbag_connecting_node",
    90: "lower_level_sandbag_connecting_node",
    91: "foundation_connecting_node",
    92: "ground_connecting_node",
}

# =========================
# 分類・グルーピング用IDリスト
# =========================
# ノード種別区間ID（構造や階層の分類目的等）
NODE_SECTION_KIND_IDS = list(range(1, 11))  # セクション区間番号1～10

# 柱・梁・エッジ・壁・サンドバッグ等、部材種別IDリスト
COLUMNS_KIND_IDS = [53, 55]
BEAMS_KIND_IDS = [42, 43, 44, 45, 46, 48, 49, 50, 51]
EDGE_NODE_KIND_IDS = [0, 1]
WALL_NODE_KIND_IDS = [0, 1]
SANDBAG_NODE_KIND_IDS = [0, 2, 3, 4, 5, 7, 8, 9]

# --- 将来拡張指針 ---
# ・IDセット追加時はここに追記・命名規則を統一
# ・分類増／仕様変化時も他ファイル改修不要な構造とする
