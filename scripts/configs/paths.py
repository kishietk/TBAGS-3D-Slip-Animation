"""
ファイル名: configs/paths.py

責務:
- プロジェクト全体で使う“ファイル/ディレクトリパス”の定数を一元管理
- データ・画像・外部参照先パスのみ担当し、値や分類・種別定数は責任外

設計指針:
- 他設定（定数・ラベル・分類）は他ファイルへ分離
- 絶対パス化・環境依存考慮・相対パス対策を徹底
- ディレクトリ構成変更時はこの1ファイルを修正すればよい構造とする

TODO:
- 複数環境（本番/開発/CI等）でのパス切替（env変数/コマンドライン対応など）
- 将来の外部クラウドストレージ連携やリモートパス拡張時の設計見直し
"""

import os

# =======================
# ルート・データ・画像ディレクトリ
# =======================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../../data"))
TEXTURE_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../../textures"))

# =======================
# データファイルパス
# =======================
NODE_CSV = os.path.join(DATA_DIR, "self-with-tbags.str")
EDGES_FILE = os.path.join(DATA_DIR, "self-with-tbags.str")
NODE_ANIM_CSV = os.path.join(DATA_DIR, "animation-kumamoto-with-tbags.csv")
EARTHQUAKE_ANIM_CSV = os.path.join(DATA_DIR, "kumamoto-erthquake-disp.csv")

# =======================
# 画像・テクスチャファイルパス
# =======================
WALL_IMG = os.path.join(TEXTURE_DIR, "wall_texture.png")
ROOF_IMG = os.path.join(TEXTURE_DIR, "roof_texture.png")

# --- 将来拡張の指針 ---
# ・クラウドや環境ごとにパス切替が必要になった場合は、ここを関数化 or .env対応などで拡張
