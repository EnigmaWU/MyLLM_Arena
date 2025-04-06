"""
日志设置工具
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_level: str = "info", log_dir: str = "logs"):
    """
    设置应用日志
    
    Args:
        log_level: 日志级别 (debug, info, warning, error, critical)
        log_dir: 日志文件目录
    """
    # 创建日志目录
    log_directory = Path(log_dir)
    log_directory.mkdir(exist_ok=True)
    
    # 设置日志级别映射
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO, 
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    level = level_map.get(log_level.lower(), logging.INFO)
    
    # 创建基本配置
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 获取根日志器
    logger = logging.getLogger("nextbook")
    
    # 添加文件处理器
    main_log_path = log_directory / "nextbook.log"
    file_handler = RotatingFileHandler(
        main_log_path, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # 添加错误日志处理器
    error_log_path = log_directory / "errors.log"
    error_file_handler = RotatingFileHandler(
        error_log_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    
    # 添加处理器到根日志器
    logger.addHandler(file_handler)
    logger.addHandler(error_file_handler)
    
    # 设置日志传播
    logger.propagate = False
    
    return logger
