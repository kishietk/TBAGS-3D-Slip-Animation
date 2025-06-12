"""
ロギングユーティリティ
- プロジェクト全体で使うlogging.Loggerのセットアップ関数を提供
- LOG_LEVELはconfigから読み込み、環境によってINFO等に切替
"""

import logging

try:
    from configs import LOG_LEVEL
except ImportError:
    LOG_LEVEL = "INFO"


def setup_logging(name: str = "main") -> logging.Logger:
    """
    指定名のロガー(logging.Logger)をセットアップし返す。

    引数:
        name (str): ロガー名（省略時'main'）
    戻り値:
        logging.Logger: ロガーインスタンス
    例外:
        なし（但しロギング設定に失敗すると標準logging挙動）
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
