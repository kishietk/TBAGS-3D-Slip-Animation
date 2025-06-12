"""
configs/constants.py

責務:
- プロジェクト全体で利用する数値定数、物理パラメータ、ノードIDセット、描画用定数などを一元管理
- パス・ラベル・部材種別定数などとは分離
"""

from mathutils import Vector

# =======================
# ノードID・階層設定
# =======================

NODE_SECTION_NUMBERS = list(range(1, 11))  # 1～10

NODE_IDS_2F = set(range(201, 209))
NODE_IDS_3F = set(range(301, 309))
NODE_IDS_4F = set(range(401, 409))

NODE_IDS_SB1 = {1143, 1148, 1153, 1158, 1243, 1248, 1253, 1258}
NODE_IDS_SB2 = {3143, 3148, 3153, 3158, 3243, 3248, 3253, 3258}
NODE_IDS_SB3 = {5143, 5148, 5153, 5158, 5243, 5248, 5253, 5258}
NODE_IDS_SB4 = {11143, 11148, 11153, 11158, 11243, 11248, 11253, 11258}

NODE_IDS_SB5 = {2354, 2359, 2366, 2372, 2379, 2385, 2391}
NODE_IDS_SB6 = {4354, 4359, 4366, 4372, 4379, 4385, 4391}
NODE_IDS_SB7 = {6354, 6359, 6366, 6372, 6379, 6385, 6391}
NODE_IDS_SB8 = {12354, 12359, 12366, 12372, 12379, 12385, 12391}

VALID_NODE_IDS = (
    NODE_IDS_2F
    | NODE_IDS_3F
    | NODE_IDS_4F
    | NODE_IDS_SB1
    | NODE_IDS_SB2
    | NODE_IDS_SB3
    | NODE_IDS_SB4
    | NODE_IDS_SB5
    | NODE_IDS_SB6
    | NODE_IDS_SB7
    | NODE_IDS_SB8
)

# =========================
# Blenderオブジェクト命名
# =========================

NODE_OBJ_PREFIX = "Node_"
PANEL_OBJ_PREFIX = "Panel_"
MEMBER_OBJ_PREFIX = "Member_"
COLUMN_OBJ_PREFIX = "Column_"
LABEL_OBJ_PREFIX = "Label_"
SANDBAG_OBJ_PREFIX = "Sandbag_"
ROOF_OBJ_NAME = "Roof"
ROOF_MESH_NAME = "RoofMesh"
UV_MAP_NAME = "UVMap"

# =========================
# 幾何・数値パラメータ設定
# =========================

SPHERE_RADIUS = 0.24
MEMBER_THICK = 0.4
CYLINDER_VERTS = 8
EPS_XY_MATCH = 1e-3
EPS_AXIS = 1e-6
SANDBAG_CUBE_SIZE = Vector((3.0, 3.0, 0.05))

# =========================
# ラベル・アニメーション設定
# =========================

LABEL_SIZE = 0.1
LABEL_OFFSET = Vector((0.8, -0.5, 0.5))
ANIM_FPS = 60
ANIM_SECONDS = 30
ANIM_TOTAL_FRAMES = ANIM_FPS * ANIM_SECONDS
DISP_SCALE = 10

# =========================
# マテリアル透明度
# =========================

WALL_ALPHA = 0.8
ROOF_ALPHA = 0.6

# =========================
# データCSV/STRヘッダー管理
# =========================

TYPE_HEADER = "(TYPE)"
CMP_HEADER = "(CMP)"
ID_HEADER = "(ID)"
