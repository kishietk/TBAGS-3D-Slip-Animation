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
# パス基本定義
# =======================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../../"))
DATA_DIR = os.path.join(ROOT_DIR, "data")
TEXTURE_DIR = os.path.join(ROOT_DIR, "textures")

# =======================
# 共通ファイル名 (.str)
# =======================
FILE_WITH_TBAGS = "input-with-tbags.str"
FILE_NO_TBAGS = "input-no-tbags.str"
FILE_NOKOTSUDO_WITH_TBAGS = "input-nokotsudo-with-tbags.str"

# =======================
# 地震データセット設定
# =======================
EARTHQUAKE_DATASETS = {
    "nokotsudo_kobe_with_tbags": {
        "base": "nokotsudo-kobe",
        "tbags": True,
        "node_file": FILE_NOKOTSUDO_WITH_TBAGS,
        "label": "Nokotsudo Kobe (with T-BAGS)",
    },
    "kumamoto_with_tbags": {
        "base": "kumamoto",
        "tbags": True,
        "node_file": FILE_WITH_TBAGS,
        "label": "Kumamoto (with T-BAGS)",
    },
    "kumamoto_no_tbags": {
        "base": "kumamoto",
        "tbags": False,
        "node_file": FILE_NO_TBAGS,
        "label": "Kumamoto (no T-BAGS)",
    },
    "tohoku_with_tbags": {
        "base": "tohoku",
        "tbags": True,
        "node_file": FILE_WITH_TBAGS,
        "label": "Tohoku (with T-BAGS)",
    },
    "tohoku_no_tbags": {
        "base": "tohoku",
        "tbags": False,
        "node_file": FILE_NO_TBAGS,
        "label": "Tohoku (no T-BAGS)",
    },
    "kobe_with_tbags": {
        "base": "kobe",
        "tbags": True,
        "node_file": FILE_WITH_TBAGS,
        "label": "Kobe (with T-BAGS)",
    },
    "kobe_no_tbags": {
        "base": "kobe",
        "tbags": False,
        "node_file": FILE_NO_TBAGS,
        "label": "Kobe (no T-BAGS)",
    },
}

# 各データセットに絶対パスを追加
for key, dataset in EARTHQUAKE_DATASETS.items():
    base = dataset["base"]
    tag = "with-tbags" if dataset["tbags"] else "no-tbags"
    # .str ファイル
    dataset["str_file"] = os.path.join(DATA_DIR, dataset["node_file"])
    # 節点CSV／エッジCSV（暫定で.str を使う）
    dataset["node_csv"] = os.path.join(DATA_DIR, dataset["node_file"])
    dataset["edges_file"] = os.path.join(DATA_DIR, dataset["node_file"])
    # アニメーションCSV
    dataset["node_anim_csv"] = os.path.join(DATA_DIR, f"animation-{base}-{tag}.csv")
    dataset["earthquake_anim_csv"] = os.path.join(
        DATA_DIR, f"{base}-earthquake-disp.csv"
    )

# =======================
# デフォルト設定／データセットキー
# =======================
# 環境変数 DATASET_KEY でデータセットを切り替え可能
DEFAULT_KEY = os.environ.get("DATASET_KEY", "kumamoto_with_tbags")

NODE_ANIM_CSV = EARTHQUAKE_DATASETS[DEFAULT_KEY]["node_anim_csv"]
NODE_CSV = EARTHQUAKE_DATASETS[DEFAULT_KEY]["node_csv"]
EDGES_FILE = EARTHQUAKE_DATASETS[DEFAULT_KEY]["edges_file"]
EDGES_FILE = EARTHQUAKE_DATASETS[DEFAULT_KEY]["edges_file"]

# =======================
# 環境変数オーバーライド
# =======================
# .str ファイルパスを環境変数で上書き可能
STR_FILE_PATH = os.environ.get(
    "STR_FILE_PATH",
    EARTHQUAKE_DATASETS[DEFAULT_KEY]["str_file"],
)
# 地震アニメーションCSVパスを環境変数で上書き可能
EARTHQUAKE_ANIM_CSV = os.environ.get(
    "EARTHQUAKE_ANIM_CSV",
    EARTHQUAKE_DATASETS[DEFAULT_KEY]["earthquake_anim_csv"],
)

# =======================
# テクスチャ画像パス
# =======================
WALL_IMG = os.path.join(TEXTURE_DIR, "wall_texture.png")
ROOF_IMG = os.path.join(TEXTURE_DIR, "roof_texture.png")
TBAGS_TEXTURE = os.path.join(TEXTURE_DIR, "tbags_texture.jpeg")

# =======================
# ログ用関数
# =======================


def log_dataset_selection(key):
    d = EARTHQUAKE_DATASETS.get(key)
    if d:
        return f"地震：{d['base'].capitalize()}，T-BAGS：{'あり' if d['tbags'] else 'なし'}"
    return f"[ERROR] 不明なデータセットキー: {key}"
