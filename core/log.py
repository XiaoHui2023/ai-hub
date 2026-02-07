import logging
import os
import datetime
from logging.handlers import RotatingFileHandler
import colorlog
from colorama import init as colorama_init

def set_log(dir_name:str):
    if not dir_name:
        return

    # 初始化 colorama
    colorama_init()

    # 创建日志目录
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    time = datetime.datetime.now().strftime('%H-%M-%S')
    log_file = f"{dir_name}/{date}/{time}.log"
    
    # 为log创建目录
    os.makedirs(os.path.dirname(log_file),exist_ok=True)
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 配置彩色日志格式
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
    
    # 配置文件处理器，使用UTF-8编码
    file_handler = RotatingFileHandler(
        log_file,
        encoding='utf-8',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # 配置控制台处理器（使用彩色格式）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)
    
    # 获取logger并添加处理器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 清除现有的处理器
    logger.handlers = []
    
    # 添加新的处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 禁止特定库的日志
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    