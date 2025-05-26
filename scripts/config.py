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
NODE_CSV = os.path.join(DATA_DIR, "node_position.csv")
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

# 各階層ごとのノードIDセット
NODE_IDS_2F = set(range(201, 209))
NODE_IDS_3F = set(range(301, 309))
NODE_IDS_4F = set(range(401, 409))
NODE_IDS_SPECIAL = {1143, 1148, 1153, 1158, 1243, 1248, 1253, 1258}

# 有効なノードIDの集合
VALID_NODE_IDS = NODE_IDS_2F | NODE_IDS_3F | NODE_IDS_4F | NODE_IDS_SPECIAL

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
EPS_XY_MATCH = 1e-3  # 位置比較誤差（XY座標）
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
    42: "frame_beam",
    43: "upper_sandbag_beam",
    44: "lower_sandbag_beam",
    45: "left_wall_column",
    46: "right_wall_column",
    47: "outer_column",
    48: "floor_column",
    49: "upper_brace",
    50: "lower_brace",
    51: "main_roof_beam",
    52: "sub_roof_beam",
    53: "parapet",
    54: "foundation_column",
    55: "foundation_connection",
}

# 柱として扱う部材種別IDリスト
COLUMNS_KIND_IDS = [45, 46, 47, 48, 54]
# 梁として扱う部材種別IDリスト
BEAMS_KIND_IDS = [42, 43, 44, 49, 50, 51, 52, 53, 55]

# ========================
# 10. ログ設定
# ========================
LOG_LEVEL = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" のいずれか
