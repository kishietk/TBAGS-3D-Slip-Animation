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
# Blenderオブジェクト命名・UI（名前プリフィックスなど）
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
CUBE_OBJ_PREFIX = "Cube_"
GROUND_OBJ_PREFIX = "Ground_"


# ----------------------------
# 構造物・幾何パラメータ（ビルダー生成プリミティブ用）
# ----------------------------
SPHERE_RADIUS = 0.24  # ノード球体の半径
MEMBER_THICK = 0.4  # 梁・柱・部材の既定太さ
CYLINDER_VERTS = 4  # 円柱プリミティブ分割数
PANEL_VERT_COUNT = 4  # パネル構成頂点数
CUBE_DEFAULT_SIZE = (1.0, 1.0, 1.0)  # キューブのデフォルトサイズ（xyz）
CUBE_DEFAULT_LOC = (0.0, 0.0, 0.0)  # キューブのデフォルト位置
UV_SPHERE_SEGMENTS = 32  # ノード球体の横分割
UV_SPHERE_RINGS = 16  # ノード球体の縦分割

EPS_XY_MATCH = 1e-3
EPS_AXIS = 1e-6

# ----------------------------
# 地面（Ground）パラメータ
# ----------------------------
GROUND_SIZE_X = 60.0
GROUND_SIZE_Y = 40.0
GROUND_SIZE_XY = (GROUND_SIZE_X, GROUND_SIZE_Y)
GROUND_LOCATION = (10.0, 5.0, -0.18)
GROUND_NAME = "Ground"
GROUND_MAT_NAME = "GroundMat"
GROUND_MAT_COLOR = (0.25, 0.42, 0.48, 1)
GROUND_PRIMITIVE_SIZE = 1.0  # bpy.ops.mesh.primitive_plane_add(size=...)

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
# データ仕様（CSV/STR等）
# ----------------------------
TYPE_HEADER = "(TYPE)"
CMP_HEADER = "(CMP)"
ID_HEADER = "(ID)"

# ----------------------------
# マテリアル・描画パラメータ
# ----------------------------
WALL_ALPHA = 0.8
ROOF_ALPHA = 0.6
