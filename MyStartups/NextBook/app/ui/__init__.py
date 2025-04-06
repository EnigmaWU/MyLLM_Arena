"""
UI模块负责创建和管理用户界面，
将用户交互转换为核心应用操作，
并展示应用状态和数据。
"""

import logging
from typing import Dict, Any

def create_ui(app_core, config):
    """
    工厂函数，根据配置创建适当的UI实例
    
    Args:
        app_core: 应用核心实例
        config: 应用配置
    
    Returns:
        UI实例
    """
    ui_type = config.get('ui', {}).get('type', 'desktop')
    logger = logging.getLogger("nextbook.ui")
    
    if ui_type == 'desktop':
        from .desktop import DesktopUI
        logger.info("创建桌面UI...")
        return DesktopUI(app_core, config)
    elif ui_type == 'cli':
        from .cli import CliUI
        logger.info("创建命令行UI...")
        return CliUI(app_core, config)
    else:
        logger.error(f"未知UI类型: {ui_type}，使用默认桌面UI")
        from .desktop import DesktopUI
        return DesktopUI(app_core, config)

__all__ = ['create_ui']
