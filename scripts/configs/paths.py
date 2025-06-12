"""
configs/paths.py

責務:
- プロジェクト内のすべてのディレクトリ・ファイルパス定数を一元管理
- 他の設定・パラメータとは分離して「パス関連」に特化
"""

import os

# プロジェクトルートディレクトリ（このファイルの場所基準で一つ上）
PROJECT_DIR: str = os.path.dirname(os.path.abspath(__file__))

# データファイルディレクトリ
DATA_DIR: str = os.path.normpath(os.path.join(PROJECT_DIR, "../../data"))
# テクスチャ画像ディレクトリ
TEXTURE_DIR: str = os.path.normpath(os.path.join(PROJECT_DIR, "../../textures"))

# =======================
# データファイルパス定義
# =======================

NODE_CSV: str = os.path.join(DATA_DIR, "self-with-tbags.str")
EDGES_FILE: str = os.path.join(DATA_DIR, "self-with-tbags.str")
NODE_ANIM_CSV: str = os.path.join(DATA_DIR, "animation-kumamoto-with-tbags.csv")
EARTHQUAKE_ANIM_CSV: str = os.path.join(DATA_DIR, "kumamoto-erthquake-disp.csv")

# =======================
# 画像・テクスチャファイルパス
# =======================

WALL_IMG: str = os.path.join(TEXTURE_DIR, "wall_texture.png")
ROOF_IMG: str = os.path.join(TEXTURE_DIR, "roof_texture.png")
