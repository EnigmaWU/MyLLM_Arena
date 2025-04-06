"""
配置处理工具函数
"""

import os
import yaml
from typing import Dict, Any

def load_config(config_path: str) -> Dict[str, Any]:
    """
    从YAML文件加载配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    
    Raises:
        FileNotFoundError: 配置文件不存在
        yaml.YAMLError: YAML解析错误
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件未找到: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config

def get_config_value(config: Dict[str, Any], path: str, default=None) -> Any:
    """
    从嵌套配置字典中获取值
    
    Args:
        config: 配置字典
        path: 使用点号分隔的配置路径，如"storage.database.path"
        default: 当路径不存在时返回的默认值
        
    Returns:
        配置值或默认值
    """
    parts = path.split('.')
    current = config
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    
    return current
