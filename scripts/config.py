import os

# =======================
# 1. ディレクトリ/パス設定
# =======================

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../data"))
TEXTURE_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../textures"))

# ===========================
# 2. データファイル/画像の絶対パス
# ===========================

NODE_CSV = os.path.join(DATA_DIR, "node_position.csv")
EDGES_FILE = os.path.join(DATA_DIR, "self.str")
ANIM_CSV = os.path.join(DATA_DIR, "animation.csv")
WALL_IMG = os.path.join(TEXTURE_DIR, "wall_texture.png")
ROOF_IMG = os.path.join(TEXTURE_DIR, "roof_texture.png")

# =======================
# 3. ノードID・階層管理
# =======================

NODE_IDS_2F = set(range(201, 209))
NODE_IDS_3F = set(range(301, 309))
NODE_IDS_4F = set(range(401, 409))
NODE_IDS_SPECIAL = {1143, 1148, 1153, 1158, 1243, 1248, 1253, 1258}

VALID_NODE_IDS = NODE_IDS_2F | NODE_IDS_3F | NODE_IDS_4F | NODE_IDS_SPECIAL

SUSPICIOUS_EDGE_TARGETS = [
    (201, 208),
    (301, 308),
    (401, 408),
]

# =======================
# 4. Blender命名規則・名称
# =======================

NODE_OBJ_PREFIX = "Node_"
PANEL_OBJ_PREFIX = "Panel_"
MEMBER_OBJ_PREFIX = "Member_"
COLUMN_OBJ_PREFIX = "Column_"
LABEL_OBJ_PREFIX = "Label_"
ROOF_OBJ_NAME = "Roof"
ROOF_MESH_NAME = "RoofMesh"
UV_MAP_NAME = "UVMap"

# =======================
# 5. パラメータ・しきい値
# =======================

SPHERE_RADIUS = 0.5
MEMBER_THICK = 0.4
CYLINDER_VERTS = 4
EPS_XY_MATCH = 1e-3
EPS_AXIS = 1e-6

# =======================
# 6. ラベル・アニメーション設定
# =======================

NODE_LABEL_SIZE = 0.4
NODE_LABEL_OFFSET = (0.8, -0.5, 0.5)
ANIM_FPS = 60
ANIM_SECONDS = 30
ANIM_TOTAL_FRAMES = ANIM_FPS * ANIM_SECONDS
DISP_SCALE = 10

# =======================
# 7. マテリアル透明度
# =======================

WALL_ALPHA = 0.4
ROOF_ALPHA = 0.6

# =======================
# 8. CSV/STRのヘッダー管理
# =======================

TYPE_HEADER = "(TYPE)"
CMP_HEADER = "(CMP)"
ID_HEADER = "(ID)"

# =======================
# 9. EBEAM3Dグループ定義
# =======================

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

COLUMNS_KIND_IDS = [45, 46, 47, 48, 54]
BEAMS_KIND_IDS = [42, 43, 44, 49, 50, 51, 52, 53, 55]

COLUMN_BONE_COUNT = 4
BEAM_BONE_COUNT = 3

# =======================
# 10. 将来拡張用
# =======================

# 必要な定数はここに追加
