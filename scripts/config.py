import os

"""
config.py

【役割 / Purpose】
- プロジェクト全体で使う「定数・パス・パラメータ・命名ルール」を一元管理する設定ファイル。
- 各種パスは絶対パスで管理し、どこから実行しても破綻しないように設計。
- 現場・運用・メンテナンス時に「値の変更＝このファイルだけ」で済む！

【運用ガイドライン】
- Pythonソースで「定数/パスの直書き」は絶対NG。ここからimportして使う。
- データディレクトリ構成や命名ルールも必ずコメントで明示。
- データファイルを追加する場合、まずここを修正。
"""

# =======================
# 1. ディレクトリ/パス設定
# =======================

# config.pyが置かれているディレクトリの絶対パス
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# データ格納ディレクトリ（ノード・エッジ・アニメーション等のCSV/STR）
DATA_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../data"))

# テクスチャ画像など格納ディレクトリ
TEXTURE_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../textures"))

# ===========================
# 2. データファイル/画像の絶対パス
# ===========================

NODE_CSV = os.path.join(DATA_DIR, "node_position.csv")  # ノード座標CSV
EDGES_FILE = os.path.join(DATA_DIR, "self.str")  # エッジ定義STR
ANIM_CSV = os.path.join(DATA_DIR, "animation.csv")  # アニメーションCSV
WALL_IMG = os.path.join(TEXTURE_DIR, "wall_texture.png")  # 壁テクスチャ画像
ROOF_IMG = os.path.join(TEXTURE_DIR, "roof_texture.png")  # 屋根テクスチャ画像

# =======================
# 3. ノードID・階層管理
# =======================

# 階層ごとのノードIDセット
NODE_IDS_2F = set(range(201, 209))  # 2階
NODE_IDS_3F = set(range(301, 309))  # 3階
NODE_IDS_4F = set(range(401, 409))  # 4階
NODE_IDS_SPECIAL = {1143, 1148, 1153, 1158, 1243, 1248, 1253, 1258}  # 特殊ノード

# 有効なノードIDセット（全体合成）
VALID_NODE_IDS = NODE_IDS_2F | NODE_IDS_3F | NODE_IDS_4F | NODE_IDS_SPECIAL

# エッジ異常チェック対象
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

SPHERE_RADIUS = 0.05  # ノード球 半径[m]
MEMBER_THICK = 0.5  # 柱・梁 半径[m]
CYLINDER_VERTS = 16  # 柱・梁 円柱分割数
EPS_XY_MATCH = 1e-3  # XY一致判定しきい値
EPS_AXIS = 1e-6  # ベクトル軸判定しきい値

# =======================
# 6. ラベル・アニメーション設定
# =======================

NODE_LABEL_SIZE = 0.4  # ラベル文字サイズ
NODE_LABEL_OFFSET = (0.8, -0.5, 0.5)  # ラベル表示オフセット(X,Y,Z)
ANIM_FPS = 60  # アニメーションFPS
ANIM_SECONDS = 30  # アニメーション時間（秒）
ANIM_TOTAL_FRAMES = ANIM_FPS * ANIM_SECONDS  # 総フレーム数
DISP_SCALE = 10  # 変位量スケーリング

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

# EBEAM3D部材グループ（self.strでの #42~#55など）
EBEAM_KIND_LABELS = {
    42: "frame_beam",  # 梁
    43: "upper_sandbag_beam",  # 上部砂袋連結梁
    44: "lower_sandbag_beam",  # 下部砂袋連結梁
    45: "left_wall_column",  # 左側壁柱
    46: "right_wall_column",  # 右側壁柱
    47: "outer_column",  # 外部柱
    48: "floor_column",  # 階間柱
    49: "upper_brace",  # 上部ブレース
    50: "lower_brace",  # 下部ブレース
    51: "main_roof_beam",  # 屋根主梁
    52: "sub_roof_beam",  # 屋根副梁
    53: "parapet",  # パラペット
    54: "foundation_column",  # 基礎柱
    55: "foundation_connection",  # 基礎無連結部材
    # 必要に応じて拡張
}

# =======================
# 10. 将来拡張用（この下に追加）
# =======================

# 必要な定数・設定値はここにどんどん追加
