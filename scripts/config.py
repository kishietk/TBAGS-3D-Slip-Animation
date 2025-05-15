import os

# プロジェクトルート（scripts/ の1つ上）
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.normpath(os.path.join(PROJECT_DIR, "../data"))
TEXTURE_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../textures"))

# ── ファイルパス ──────────────────────────────
NODE_CSV     = os.path.join(DATA_DIR, "node_position.csv")
EDGES_FILE   = os.path.join(DATA_DIR, "self.str")
ANIM_CSV     = os.path.join(DATA_DIR, "node_earthquake_animation.csv")  # ※未使用なら使わなくてOK

# ── 可視化パラメータ ──────────────────────────
SPHERE_RADIUS = 0.3   # ノード球の半径
MEMBER_THICK  = 0.5    # 柱・梁の直径（半径）

# ── マテリアル画像・透明度 ─────────────────────
WALL_IMG  = os.path.join(TEXTURE_DIR, "wall_texture.png")
ROOF_IMG  = os.path.join(TEXTURE_DIR, "roof_texture.png")
WALL_ALPHA = 0.2
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
NODE_LABEL_OFFSET = (0.8, 0, 0.5)  # 表示オフセット（X, Y, Z）

# ── アニメーション設定（必要なら）────────────────
ANIM_FPS         = 20
ANIM_TOTAL_FRAMES = 400
