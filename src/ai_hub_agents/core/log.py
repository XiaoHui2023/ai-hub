import logging
import os
import datetime
from logging.handlers import RotatingFileHandler
import colorlog
from colorama import init as colorama_init
from typing import Literal

def setup_log(dir_name: str | None, level: Literal['info', 'debug', 'warning', 'error', 'critical'] = 'info'):
    """设置日志。无文件路径时仅输出到控制台。"""
    level_map = {
        'info': logging.INFO,
        'debug': logging.DEBUG,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }
    log_level = level_map.get(level.lower(), logging.INFO)

    colorama_init()

    color_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)

    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.handlers.clear()
    logger.addHandler(console_handler)

    if dir_name:
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        time = datetime.datetime.now().strftime('%H-%M-%S')
        log_file = f"{dir_name}/{date}/{time}.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler = RotatingFileHandler(
            log_file,
            encoding='utf-8',
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)