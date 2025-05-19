import os

"""
config.py

【役割】
- プロジェクト全体の「全定数・全パラメータ・ファイルパス・命名ルール」を一元管理。
- パスはすべて「絶対パス」に解決し、BlenderやCLIどこから実行しても100%正しく動作するように設計。
- 追加・変更はこのファイルだけで完結！現場保守・運用・拡張すべて楽に。

【現場運用指針】
- Pythonソースから「値やパスの直書き」は原則禁止。このファイルからimportして使う。
- パスが分からない/存在しないときはconfig.pyだけ直す。main.py他は一切触らない。
- コメントで用途・階層・命名規則なども必ず明記。
"""

# =======================
# 1. プロジェクト・パス設定
# =======================

# config.py自身が置かれている「scripts」ディレクトリの絶対パス
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# データ・テクスチャ等の実体ディレクトリ
DATA_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../data"))
TEXTURE_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../textures"))

# =======================
# 2. データファイル・画像パス
# =======================

NODE_CSV = os.path.join(DATA_DIR, "node_position.csv")  # ノード座標CSV
EDGES_FILE = os.path.join(DATA_DIR, "self.str")  # エッジ定義STR
ANIM_CSV = os.path.join(DATA_DIR, "animation.csv")  # アニメーションCSV
WALL_IMG = os.path.join(TEXTURE_DIR, "wall_texture.png")  # 壁テクスチャ
ROOF_IMG = os.path.join(TEXTURE_DIR, "roof_texture.png")  # 屋根テクスチャ

# =======================
# 3. ノードID・エッジID管理
# =======================

# --- 階層ごとに管理 ---
NODE_IDS_2F = set(range(201, 209))  # 2階ノード
NODE_IDS_3F = set(range(301, 309))  # 3階ノード
NODE_IDS_4F = set(range(401, 409))  # 4階ノード
NODE_IDS_SPECIAL = {1143, 1148, 1153, 1158, 1243, 1248, 1253, 1258}  # 特殊ノード

# --- 有効ノード全体 ---
VALID_NODE_IDS = NODE_IDS_2F | NODE_IDS_3F | NODE_IDS_4F | NODE_IDS_SPECIAL

# --- suspicious edge チェックもここで管理 ---
SUSPICIOUS_EDGE_TARGETS = [
    (201, 208),
    (301, 308),
    (401, 408),
]

# =======================
# 4. Blender命名プレフィックス・名
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

SPHERE_RADIUS = 0.05  # ノード球の半径[m]
MEMBER_THICK = 0.5  # 柱・梁の半径[m]
CYLINDER_VERTS = 16  # 柱・梁の円柱分割数
EPS_XY_MATCH = 1e-3  # X/Y/Z判定しきい値
EPS_AXIS = 1e-6  # ベクトル向き判定用

# =======================
# 6. ラベル・アニメ設定
# =======================

NODE_LABEL_SIZE = 0.4  # ラベルの文字サイズ
NODE_LABEL_OFFSET = (0.8, -0.5, 0.5)  # ラベルの表示オフセット(X,Y,Z)
ANIM_FPS = 60  # FPS (Frames Per Second)
ANIM_SECONDS = 30  # アニメーション時間[秒]
ANIM_TOTAL_FRAMES = ANIM_FPS * ANIM_SECONDS  # 総フレーム数
DISP_SCALE = 10  # 変位量のスケーリング係数

# =======================
# 7. マテリアル透明度
# =======================

WALL_ALPHA = 0.4
ROOF_ALPHA = 0.6

# =======================
# 8. CSV・STRのヘッダー
# =======================

TYPE_HEADER = "(TYPE)"
CMP_HEADER = "(CMP)"
ID_HEADER = "(ID)"

# =======================
# 9. 将来拡張用（ここから下に新定数を追記）
# =======================

# --- 必要な新定数はこの下へ ---
