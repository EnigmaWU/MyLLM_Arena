"""
NextBook Agent 配置工具模块
负责加载和管理应用配置
"""

import yaml

def load_config(config_path):
    """从文件加载配置"""
    print(f"从 {config_path} 加载配置...")
    # 临时返回示例配置
    return {
        "application": {
            "log_level": "info",
            "dev_mode": False,
            "data_directory": "data",
            "plugins_enabled": False
        }
    }
