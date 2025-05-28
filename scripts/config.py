import os

# ========================
# 1. ディレクトリ・パス設定
# ========================

# プロジェクトの基準ディレクトリ
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../data"))
TEXTURE_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../textures"))

# ===============================
# 2. データファイル・画像ファイル
# ===============================

# ノード座標CSVファイル
NODE_CSV = os.path.join(DATA_DIR, "self.str")
# エッジ定義STRファイル
EDGES_FILE = os.path.join(DATA_DIR, "self.str")
# アニメーションCSVファイル
ANIM_CSV = os.path.join(DATA_DIR, "animation.csv")
# 壁・屋根テクスチャ画像
WALL_IMG = os.path.join(TEXTURE_DIR, "wall_texture.png")
ROOF_IMG = os.path.join(TEXTURE_DIR, "roof_texture.png")

# ========================
# 3. ノードID管理
# ========================

# #1～#10 をノード座標セクションとして扱う
NODE_SECTION_NUMBERS = list(range(1, 11))  # [1,2,...,10]

# 各階層ごとのノードIDセット
NODE_IDS_2F = set(range(201, 209))
NODE_IDS_3F = set(range(301, 309))
NODE_IDS_4F = set(range(401, 409))
NODE_IDS_SB1 = {1143, 1148, 1153, 1158, 1243, 1248, 1253, 1258}
NODE_IDS_SB2 = {2354,2359,2366}
NODE_IDS_SB3 = {51143, 51148, 51153, 51158, 51243, 51248, 51253, 51258}
NODE_IDS_SB4 = {52354, 52359, 52366}
# 有効なノードIDの集合
VALID_NODE_IDS = NODE_IDS_2F | NODE_IDS_3F | NODE_IDS_4F | NODE_IDS_SB1 | NODE_IDS_SB2 | NODE_IDS_SB3

# ============================
# 4. Blenderオブジェクト命名
# ============================

# ノード・パネル・部材・柱・ラベル・屋根の命名プレフィックス
NODE_OBJ_PREFIX = "Node_"
PANEL_OBJ_PREFIX = "Panel_"
MEMBER_OBJ_PREFIX = "Member_"
COLUMN_OBJ_PREFIX = "Column_"
LABEL_OBJ_PREFIX = "Label_"
ROOF_OBJ_NAME = "Roof"
ROOF_MESH_NAME = "RoofMesh"
UV_MAP_NAME = "UVMap"

# =======================
# 5. 幾何・数値パラメータ
# =======================

# 球・柱・梁の半径や形状・比較誤差
SPHERE_RADIUS = 0.5  # ノード球半径
MEMBER_THICK = 0.4  # 柱・梁半径
CYLINDER_VERTS = 4  # 柱・梁シリンダー分割数（未使用。推奨:16程度）
EPS_XY_MATCH = 0.1  # 位置比較誤差（XY座標）
EPS_AXIS = 1e-6  # ベクトル比較誤差（軸）

# ========================
# 6. ラベル・アニメーション
# ========================

NODE_LABEL_SIZE = 0.4  # ラベル文字サイズ
NODE_LABEL_OFFSET = (0.8, -0.5, 0.5)  # ラベル相対位置
ANIM_FPS = 60  # アニメーションFPS
ANIM_SECONDS = 30  # アニメーション秒数
ANIM_TOTAL_FRAMES = ANIM_FPS * ANIM_SECONDS
DISP_SCALE = 10  # 変位スケール

# ======================
# 7. マテリアル透明度
# ======================

WALL_ALPHA = 0.4
ROOF_ALPHA = 0.6

# ==========================
# 8. CSV/STRヘッダー管理
# ==========================

# アニメーション・エッジデータのCSV/STRヘッダ
TYPE_HEADER = "(TYPE)"
CMP_HEADER = "(CMP)"
ID_HEADER = "(ID)"

# =======================
# 9. EBEAM3D部材種別管理
# =======================

# 部材種別ID→ラベル
EBEAM_KIND_LABELS = {
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
}

# 柱として扱う部材種別IDリスト
COLUMNS_KIND_IDS = [53, 55]
# 梁として扱う部材種別IDリスト
BEAMS_KIND_IDS = [42, 43, 44, 45, 46, 48, 49, 50, 51]

# 壁ノードのkind_idリスト
WALL_NODE_KIND_IDS = [1, 2, 3, 4]  

# ========================
# 10. ログ設定
# ========================
LOG_LEVEL = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" のいずれか
