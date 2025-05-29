# config.py
"""
プロジェクト全体で使用する全定数・設定値・パス管理モジュール

・全ての“マジックナンバー/マジックストリング”はここで一元管理
・環境依存/切り替え項目/ファイルパス/識別IDもここで管理
・Blender外部環境依存がある場合は、将来.envやjson等で外部管理も可
"""

import os
from mathutils import Vector

# =======================
# 1. ディレクトリ・パス設定
# =======================

# プロジェクトルートディレクトリ（このファイルの場所基準）
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# データファイルディレクトリ
DATA_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../data"))
# テクスチャ画像ディレクトリ
TEXTURE_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../textures"))

# =======================
# 2. データファイルパス定義
# =======================

# ノード定義データ（CSV/STRファイル）
NODE_CSV = os.path.join(DATA_DIR, "self.str")
# エッジ定義データ（STRファイル）
EDGES_FILE = os.path.join(DATA_DIR, "self.str")
# アニメーションデータ（CSVファイル）
ANIM_CSV = os.path.join(DATA_DIR, "animation.csv")

# =======================
# 3. 画像・テクスチャファイル
# =======================

# 壁用テクスチャ画像ファイルパス
WALL_IMG = os.path.join(TEXTURE_DIR, "wall_texture.png")
# 屋根用テクスチャ画像ファイルパス
ROOF_IMG = os.path.join(TEXTURE_DIR, "roof_texture.png")

# =======================
# 4. ノードID・階層設定
# =======================

# self.strの「#1～#10」等、ノード座標定義セクション番号リスト
NODE_SECTION_NUMBERS = list(range(1, 11))  # 1～10

# 各階層ごとの有効ノードIDセット
NODE_IDS_2F = set(range(201, 209))  # 2階
NODE_IDS_3F = set(range(301, 309))  # 3階
NODE_IDS_4F = set(range(401, 409))  # 4階
NODE_IDS_SB1 = {1143, 1148, 1153, 1158, 1243, 1248, 1253, 1258}  # サンドバッグ1
NODE_IDS_SB2 = {2354, 2359, 2366}  # サンドバッグ2
NODE_IDS_SB3 = {51143, 51148, 51153, 51158, 51243, 51248, 51253, 51258}  # サンドバッグ3
NODE_IDS_SB4 = {52354, 52359, 52366}  # サンドバッグ4

# プロジェクトで有効な全ノードIDの集合
VALID_NODE_IDS = (
    NODE_IDS_2F
    | NODE_IDS_3F
    | NODE_IDS_4F
    | NODE_IDS_SB1
    | NODE_IDS_SB2
    | NODE_IDS_SB3
    | NODE_IDS_SB4
)

# ==========================
# 5. Blenderオブジェクト命名
# ==========================

# ノード・部材・パネル・柱・ラベル・屋根用命名プレフィックス/名前
NODE_OBJ_PREFIX = "Node_"
PANEL_OBJ_PREFIX = "Panel_"
MEMBER_OBJ_PREFIX = "Member_"
COLUMN_OBJ_PREFIX = "Column_"
LABEL_OBJ_PREFIX = "Label_"
SANDBAG_OBJ_PREFIX = "Sandbag_"
ROOF_OBJ_NAME = "Roof"
ROOF_MESH_NAME = "RoofMesh"
UV_MAP_NAME = "UVMap"  # UVマップ名（Blender用）


# ==========================
# 6. 幾何・数値パラメータ設定
# ==========================

# ノード球の半径（m単位）
SPHERE_RADIUS = 0.24
# 柱・梁の半径（m単位）
MEMBER_THICK = 0.4
# 柱・梁のシリンダー分割数（※現状未使用。推奨:16以上）
CYLINDER_VERTS = 8
# XY座標比較許容誤差（パネル自動生成などで使用）
EPS_XY_MATCH = 1e-3
# ベクトル（軸）比較許容誤差
EPS_AXIS = 1e-6
# サンドバッグのサイズ（m）
SANDBAG_CUBE_SIZE = Vector((2.0, 2.0, 1.0))


# ==========================
# 7. ラベル・アニメーション設定
# ==========================

# ノードIDラベルの文字サイズ
LABEL_SIZE = 0.3

# ノードIDラベルのオフセット位置 (X, Y, Z)
LABEL_OFFSET = Vector((0.8, -0.5, 0.5))

# アニメーションのFPS（フレーム/秒）
ANIM_FPS = 60
# アニメーション総秒数
ANIM_SECONDS = 30
# アニメーションの全フレーム数
ANIM_TOTAL_FRAMES = ANIM_FPS * ANIM_SECONDS
# 変位量スケール（CSV値→Blender表示スケール調整用）
DISP_SCALE = 20

# ==========================
# 8. マテリアル透明度（0:完全透明、1:不透明）
# ==========================

# 壁用マテリアルの透明度
WALL_ALPHA = 0.8
# 屋根用マテリアルの透明度
ROOF_ALPHA = 0.6

# ==========================
# 9. データCSV/STRヘッダー管理
# ==========================

# アニメーション・エッジデータ等で使うヘッダー
TYPE_HEADER = "(TYPE)"
CMP_HEADER = "(CMP)"
ID_HEADER = "(ID)"

# ==========================
# 10. EBEAM3D部材種別管理
# ==========================

# EBEAM3D部材種別ID → ラベル
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
# 梁・柱を構成するノードのkind_idリスト
EDGE_NODE_KIND_IDS = [0, 1]
# 壁ノードのkind_idリスト
WALL_NODE_KIND_IDS = [0, 1, 2, 3, 4]
# サンドバッグを構成するノードのkind_idリスト
SANDBAG_NODE_KIND_IDS = [0, 2, 6, 10]

# ==========================
# 11. ログ設定
# ==========================

# ログレベル（"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"）
LOG_LEVEL = "INFO"
