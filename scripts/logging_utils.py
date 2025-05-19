import logging
import os

"""
logging_utils.py

【役割 / Purpose】
- プロジェクト全体で統一的に使える「ロギング（ログ出力）」ユーティリティ関数の提供。
- Blender内外どちらで動かしても、ファイル・コンソールの両方に詳細なログを残せるよう設計。

【運用ガイドライン】
- loggerは「viz」名で一意に作成・再利用。
- Blenderで.blendファイルが保存されていれば同じ場所に、未保存ならドキュメントフォルダにログ出力。
- 標準でINFOレベル出力（引数で変更可能）。
"""

# Blender外でimport時の対応
try:
    import bpy
except ImportError:
    bpy = None


def setup_logging(log_level=logging.INFO, log_file_name="blender_log.txt"):
    """
    標準ロギング設定を行う関数。
    - log_level: ログ出力レベル（INFO/DEBUG/ERRORなど）
    - log_file_name: 出力ログファイル名（blendファイルと同じフォルダ or ~/Documents）
    戻り値: logging.Loggerインスタンス
    """
    logger = logging.getLogger("viz")  # プロジェクト固有ロガー

    # すでに設定済みなら再利用（レベルだけ更新）
    if logger.handlers:
        logger.setLevel(log_level)
        for h in logger.handlers:
            h.setLevel(log_level)
        return logger

    logger.setLevel(log_level)

    # ログ出力先（blend保存済みなら同じフォルダ、未保存ならドキュメント）
    if bpy and bpy.data.is_saved:
        base_dir = os.path.dirname(bpy.data.filepath)
    else:
        base_dir = os.path.expanduser("~/Documents")
    os.makedirs(base_dir, exist_ok=True)
    log_path = os.path.join(base_dir, log_file_name)

    # ファイルハンドラ
    fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    fh.setLevel(log_level)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    # コンソール出力
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info(
        f"Logger initialized at level {logging.getLevelName(log_level)}. Log file: {log_path}"
    )
    return logger
