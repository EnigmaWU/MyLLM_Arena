#!/usr/bin/env python3
"""
NextBook Agent - 智能阅读助手

这是NextBook Agent应用的主入口点。它负责初始化应用组件、
设置日志记录、加载配置、启动服务并显示用户界面。
"""

import os
import sys
import logging
import argparse
import yaml
from pathlib import Path

# 准备应用路径配置
APP_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_ROOT))

# 导入应用组件
# 注意：这些模块将在实际开发中创建
from app.ui import create_ui
from app.core import AppCore
from app.infrastructure import initialize_infrastructure
from app.utils.config import load_config
from app.utils.logging import setup_logging

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='NextBook Agent - 智能阅读助手')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--dev', action='store_true', help='启用开发模式')
    parser.add_argument('--log-level', type=str, choices=['debug', 'info', 'warning', 'error', 'critical'], 
                      help='日志级别')
    return parser.parse_args()

def load_application_config(args):
    """加载应用配置"""
    config_path = args.config if args.config else os.path.join(APP_ROOT, 'config.yml')
    
    # 检查配置文件存在
    if not os.path.exists(config_path):
        example_path = os.path.join(APP_ROOT, 'config.example.yml')
        if os.path.exists(example_path):
            print(f"配置文件 '{config_path}' 不存在。请从示例文件复制并修改: {example_path}")
        else:
            print(f"配置文件 '{config_path}' 和示例配置都不存在。无法启动应用。")
        sys.exit(1)
    
    # 加载配置文件
    try:
        config = load_config(config_path)
        
        # 命令行参数覆盖配置文件
        if args.log_level:
            config['application']['log_level'] = args.log_level
        if args.dev:
            config['application']['dev_mode'] = True
            
        return config
    except Exception as e:
        print(f"加载配置失败: {str(e)}")
        sys.exit(1)

def initialize_application(config):
    """初始化应用组件"""
    # 设置日志
    log_level = config['application']['log_level']
    setup_logging(log_level)
    logger = logging.getLogger("nextbook")
    logger.info("NextBook Agent 正在启动...")
    
    try:
        # 初始化基础设施
        logger.info("初始化基础设施...")
        infra = initialize_infrastructure(config)
        
        # 初始化核心应用
        logger.info("初始化应用核心...")
        app_core = AppCore(config, infra)
        
        # 设置目录结构
        ensure_directories(config)
        
        # 加载插件
        if config['application'].get('plugins_enabled', False):
            logger.info("加载插件...")
            # plugin_manager.load_plugins()
        
        return app_core
    except Exception as e:
        logger.critical(f"初始化应用失败: {str(e)}", exc_info=True)
        sys.exit(1)

def ensure_directories(config):
    """确保必要的目录结构存在"""
    data_dir = os.path.join(APP_ROOT, config['application'].get('data_directory', 'data'))
    directories = [
        os.path.join(data_dir, 'db'),
        os.path.join(data_dir, 'files'),
        os.path.join(data_dir, 'temp'),
        os.path.join(data_dir, 'backups'),
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """应用主入口"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 加载配置
    config = load_application_config(args)
    
    # 初始化应用
    app_core = initialize_application(config)
    
    # 创建并运行UI
    ui = create_ui(app_core, config)
    
    # 启动事件循环
    try:
        ui.run()
    except KeyboardInterrupt:
        print("应用已手动终止")
    except Exception as e:
        logging.critical(f"运行时错误: {str(e)}", exc_info=True)
    finally:
        # 清理资源
        app_core.shutdown()
        logging.info("NextBook Agent 已关闭")

if __name__ == "__main__":
    main()
