import logging
import logging.handlers
import os

LOG_FILE = "uploader.log"

def get_logger(name=None):
    """
    スレッドセーフで複数モジュールから使える共通ログ
    """
    logger = logging.getLogger(name)
    
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(threadName)s] %(name)s: %(message)s'
    )

    # ローテートファイルハンドラ
    fh = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # コンソールにも出力
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    return logger
