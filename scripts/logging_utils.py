import logging
import os

try:
    import bpy
except ImportError:
    bpy = None

def setup_logging(log_level=logging.INFO, log_file_name="blender_log.txt"):
    logger = logging.getLogger("viz")

    if logger.handlers:
        # すでに設定済み → ログレベルだけ更新
        logger.setLevel(log_level)
        for h in logger.handlers:
            h.setLevel(log_level)
        return logger

    logger.setLevel(log_level)

    # 出力先：.blend保存済みなら同フォルダ、なければDocuments
    if bpy and bpy.data.is_saved:
        base_dir = os.path.dirname(bpy.data.filepath)
    else:
        base_dir = os.path.expanduser("~/Documents")
    os.makedirs(base_dir, exist_ok=True)
    log_path = os.path.join(base_dir, log_file_name)

    # ファイルハンドラ
    fh = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    fh.setLevel(log_level)
    fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

    # コンソールハンドラ（Blenderシステムコンソール）
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info(f"Logger initialized at level {logging.getLevelName(log_level)}. Log file: {log_path}")
    return logger
