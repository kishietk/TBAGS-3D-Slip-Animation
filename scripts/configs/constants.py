"""
ファイル名: configs/constants.py

責務:
- プロジェクト全体で使う“値のみ”定数を一元管理
- パスや種別ラベル等は除外
"""

from mathutils import Vector

# ----------------------------
# ログ出力レベル
# ----------------------------
LOG_LEVEL = "INFO"

# ----------------------------
# ノードID・グループ定義
# ----------------------------
NODE_IDS_2F = set(range(201, 209))
NODE_IDS_3F = set(range(301, 309))
NODE_IDS_4F = set(range(401, 409))
NODE_IDS_SB = {
    1: {1143, 1148, 1153, 1158, 1243, 1248, 1253, 1258},
    2: {3143, 3148, 3153, 3158, 3243, 3248, 3253, 3258},
    3: {5143, 5148, 5153, 5158, 5243, 5248, 5253, 5258},
    4: {11143, 11148, 11153, 11158, 11243, 11248, 11253, 11258},
    5: {2354, 2359, 2366, 2372, 2379, 2385, 2391},
    6: {4354, 4359, 4366, 4372, 4379, 4385, 4391},
    7: {6354, 6359, 6366, 6372, 6379, 6385, 6391},
    8: {12354, 12359, 12366, 12372, 12379, 12385, 12391},
}
VALID_NODE_IDS = set().union(
    NODE_IDS_2F, NODE_IDS_3F, NODE_IDS_4F, *NODE_IDS_SB.values()
)


# TBAGS下側のノード
FICTION_NODE_IDS = set().union(
    NODE_IDS_SB[2] | NODE_IDS_SB[4] | NODE_IDS_SB[6] | NODE_IDS_SB[8]
)

# ----------------------------
# Blenderオブジェクト命名・UI
# ----------------------------
NODE_OBJ_PREFIX = "Node_"
PANEL_OBJ_PREFIX = "Panel_"
MEMBER_OBJ_PREFIX = "Member_"
COLUMN_OBJ_PREFIX = "Column_"
LABEL_OBJ_PREFIX = "Label_"
SANDBAG_OBJ_PREFIX = "Sandbag_"
ROOF_OBJ_NAME = "Roof"
ROOF_MESH_NAME = "RoofMesh"
UV_MAP_NAME = "UVMap"

# ----------------------------
# 構造物・幾何パラメータ
# ----------------------------
SPHERE_RADIUS = 0.24
MEMBER_THICK = 0.4
CYLINDER_VERTS = 4
EPS_XY_MATCH = 1e-3
EPS_AXIS = 1e-6

# 工字サンドバッグ表示用パラメータ
SANDBAG_FACE_SIZE = Vector((3.0, 3.0))
SANDBAG_BAR_THICKNESS = 0.2

# ----------------------------
# 地面（Ground）パラメータ
# ----------------------------
GROUND_SIZE_X = 60.0
GROUND_SIZE_Y = 40.0
GROUND_LOCATION = (10.0, 5.0, -0.18)
GROUND_NAME = "Ground"
GROUND_MAT_NAME = "GroundMat"
GROUND_MAT_COLOR = (0.25, 0.42, 0.48, 1)

# ----------------------------
# 表示・UIパラメータ
# ----------------------------
LABEL_SIZE = 0.1
LABEL_OFFSET = Vector((0.8, -0.5, 0.5))

# ----------------------------
# アニメーション・物理パラメータ
# ----------------------------
ANIM_FPS = 32
ANIM_SECONDS = 30
ANIM_TOTAL_FRAMES = ANIM_FPS * ANIM_SECONDS
DISP_SCALE = 10

# ----------------------------
# マテリアル・描画パラメータ
# ----------------------------
WALL_ALPHA = 0.8
ROOF_ALPHA = 0.6

# ----------------------------
# データ仕様（CSV/STR等）
# ----------------------------
TYPE_HEADER = "(TYPE)"
CMP_HEADER = "(CMP)"
ID_HEADER = "(ID)"

# --- 追加の設計指針 ---
# ・パス/ラベル/種別は別ファイルで管理
# ・外部データ化/将来の多階層/グループ管理はdict型やEnum化で柔軟対応
