import os

# =======================
# プロジェクト・データパス
# =======================

# このファイル（scripts/config.py）から見たプロジェクトルート
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../data"))
TEXTURE_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../textures"))

# -----------------------
# 各種データファイルパス
# -----------------------
NODE_CSV = os.path.join(DATA_DIR, "node_position.csv")  # ノード座標CSV
EDGES_FILE = os.path.join(DATA_DIR, "self.str")  # エッジデータ（解析用STRファイル）
ANIM_CSV = os.path.join(DATA_DIR, "with_tbags-kumamoto.csv")  # アニメーションCSV

# -----------------------
# モデル可視化パラメータ
# -----------------------
SPHERE_RADIUS = 0.05  # ノード球の半径
MEMBER_THICK = 0.5  # 柱・梁の半径（≒直径/2）

# -----------------------
# テクスチャ・透明度設定
# -----------------------
WALL_IMG = os.path.join(TEXTURE_DIR, "wall_texture.png")  # 壁テクスチャ
ROOF_IMG = os.path.join(TEXTURE_DIR, "roof_texture.png")  # 屋根テクスチャ
WALL_ALPHA = 0.4  # 壁の透明度
ROOF_ALPHA = 0.6  # 屋根の透明度

# -----------------------
# 有効ノードIDセット
#   - 対象となるノードIDだけを抽出したいとき用
# -----------------------
VALID_NODE_IDS = (
    set(range(201, 209))  # 201～208
    | set(range(301, 309))  # 301～308
    | set(range(401, 409))  # 401～408
    | {1143, 1148, 1153, 1158, 1243, 1248, 1253, 1258}  # 任意の個別ID
)

# -----------------------
# ノードラベル表示
# -----------------------
NODE_LABEL_SIZE = 0.4  # ラベルの文字サイズ
NODE_LABEL_OFFSET = (0.8, -0.5, 0.5)  # ラベルの表示オフセット(X,Y,Z)

# -----------------------
# アニメーション設定
# -----------------------
ANIM_FPS = 60  # FPS (Frames Per Second)
ANIM_SECONDS = 30  # アニメーション時間[秒]
ANIM_TOTAL_FRAMES = ANIM_FPS * ANIM_SECONDS  # 総フレーム数
DISP_SCALE = 10  # 変位量のスケーリング係数
