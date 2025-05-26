import logging

try:
    from config import LOG_LEVEL
except ImportError:
    LOG_LEVEL = "INFO"


def setup_logging(name: str = "main") -> logging.Logger:
    """
    ロガーをセットアップし返す
    引数:
        name: ロガー名（省略時は'main'）
    戻り値:
        ロガーインスタンス
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(levelname)s] %(asctime)s %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    # configのLOG_LEVELから設定
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    return logger
