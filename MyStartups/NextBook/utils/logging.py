"""
NextBook Agent 日志工具模块
提供应用的日志功能
"""

import logging

def setup_logging(level="info"):
    """设置日志系统"""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    print(f"日志系统已设置为 {level} 级别")
