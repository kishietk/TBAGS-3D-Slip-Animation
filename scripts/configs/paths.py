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
# 共通ファイル名
# =======================
FILE_WITH_TBAGS = "input-with-tbags.str"
FILE_NO_TBAGS = "input-no-tbags.str"

# =======================
# 地震データセット
# =======================
EARTHQUAKE_DATASETS = {
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

# 各データセットに絶対パス追加（初期化処理）
for key, dataset in EARTHQUAKE_DATASETS.items():
    base = dataset["base"]
    tag = "with-tbags" if dataset["tbags"] else "no-tbags"
    dataset["node_csv"] = os.path.join(DATA_DIR, dataset["node_file"])
    dataset["edges_file"] = os.path.join(DATA_DIR, dataset["node_file"])
    dataset["node_anim_csv"] = os.path.join(DATA_DIR, f"animation-{base}-{tag}.csv")
    dataset["earthquake_anim_csv"] = os.path.join(
        DATA_DIR, f"{base}-erthquake-disp.csv"
    )

# =======================
# デフォルト設定（熊本 with T-BAGS）
# =======================
DEFAULT_KEY = "kumamoto_with_tbags"
NODE_ANIM_CSV = EARTHQUAKE_DATASETS[DEFAULT_KEY]["node_anim_csv"]
EARTHQUAKE_ANIM_CSV = EARTHQUAKE_DATASETS[DEFAULT_KEY]["earthquake_anim_csv"]
NODE_CSV = EARTHQUAKE_DATASETS[DEFAULT_KEY]["node_csv"]
EDGES_FILE = EARTHQUAKE_DATASETS[DEFAULT_KEY]["edges_file"]

# =======================
# テクスチャ画像
# =======================
WALL_IMG = os.path.join(TEXTURE_DIR, "wall_texture.png")
ROOF_IMG = os.path.join(TEXTURE_DIR, "roof_texture.png")
TBAGS_TEXTURE = os.path.join(TEXTURE_DIR, "tbags_texture.jpeg")

# =======================
# T-BAGS モデル 
# =======================
TBAGS_MODEL = os.path.join(DATA_DIR, "sandbag_template_low.blend")

# =======================
# ログ関数
# =======================
def log_dataset_selection(key):
    """
    指定キーの地震データセット情報をログ出力用に整形。
    """
    d = EARTHQUAKE_DATASETS.get(key)
    if d:
        lines = [
            f"地震：{d['base'].capitalize()},  T-BAGS：{'あり' if d['tbags'] else 'なし'}"
        ]
    else:
        lines = [f"[ERROR] 不明なデータセットキー: {key}"]
    return "\n".join(lines)
