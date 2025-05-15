import os

# プロジェクトルート（scripts/ の1つ上）
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.normpath(os.path.join(PROJECT_DIR, "../data"))
TEXTURE_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../textures"))

# ── ファイルパス ──────────────────────────────
NODE_CSV     = os.path.join(DATA_DIR, "node_position.csv")
EDGES_FILE   = os.path.join(DATA_DIR, "self.str")
ANIM_CSV     = os.path.join(DATA_DIR, "with_tbags-kumamoto.csv")

# ── 可視化パラメータ ──────────────────────────
SPHERE_RADIUS = 0.05   # ノード球の半径
MEMBER_THICK  = 0.5    # 柱・梁の直径（半径）

# ── マテリアル画像・透明度 ─────────────────────
WALL_IMG  = os.path.join(TEXTURE_DIR, "wall_texture.png")
ROOF_IMG  = os.path.join(TEXTURE_DIR, "roof_texture.png")
WALL_ALPHA = 0.4
ROOF_ALPHA = 0.6

# ── 有効ノードID（必要なら）──────────────────────
VALID_NODE_IDS = (
    set(range(201, 209)) |  # 201〜208
    set(range(301, 309)) |  # 301〜308
    set(range(401, 409)) |  # 401〜408
    {
        1143, 1148, 1153, 1158,
        1243, 1248, 1253, 1258
    }
)

# ── ノードラベル表示設定 ──────────────────────────────
NODE_LABEL_SIZE = 0.4       # ラベル文字サイズ
NODE_LABEL_OFFSET = (0.8, -0.5, 0.5)  # 表示オフセット（X, Y, Z）

# ── アニメーション設定────────────────
ANIM_FPS         = 60 
ANIM_SECONDS     = 30
ANIM_TOTAL_FRAMES = ANIM_FPS * ANIM_SECONDS
DISP_SCALE = 5.0 