import logging
import os

# Blender外でのimportを考慮
try:
    import bpy
except ImportError:
    bpy = None


def setup_logging(log_level=logging.INFO, log_file_name="blender_log.txt"):
    """
    標準ロギング設定を行うユーティリティ関数
    - log_level: ログレベル（INFO/DEBUG/ERRORなど）
    - log_file_name: ログファイル名（blendファイルと同じフォルダに保存。未保存時は~/Documents）
    戻り値: logging.Loggerインスタンス
    """
    logger = logging.getLogger("viz")  # プロジェクト用のlogger名

    # すでに設定済みなら、レベルだけ変更して再利用
    if logger.handlers:
        logger.setLevel(log_level)
        for h in logger.handlers:
            h.setLevel(log_level)
        return logger

    logger.setLevel(log_level)

    # ログファイルの出力先を決定（blendファイル保存済みなら同じ場所、未保存ならドキュメント）
    if bpy and bpy.data.is_saved:
        base_dir = os.path.dirname(bpy.data.filepath)
    else:
        base_dir = os.path.expanduser("~/Documents")
    os.makedirs(base_dir, exist_ok=True)
    log_path = os.path.join(base_dir, log_file_name)

    # ファイルハンドラの作成
    fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    fh.setLevel(log_level)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    # コンソール（Blenderシステムコンソールなど）への出力
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    # ハンドラをロガーに追加
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info(
        f"Logger initialized at level {logging.getLevelName(log_level)}. Log file: {log_path}"
    )
    return logger
