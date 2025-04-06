"""
存储工厂

负责创建和管理不同类型的存储适配器。
"""

import logging
from typing import Dict, Any, Optional

from .base import BaseStorage
from .sqlite_storage import SQLiteStorage
from .vector_storage import VectorStorage
from .file_storage import FileStorage

def create_storage(domain: str, config: Dict[str, Any]) -> BaseStorage:
    """创建存储适配器
    
    Args:
        domain: 存储域名称
        config: 存储配置
    
    Returns:
        存储适配器实例
    
    Raises:
        ValueError: 当请求的存储类型不受支持时
    """
    logger = logging.getLogger("nextbook.infrastructure.storage")
    
    storage_type = config.get('database', {}).get('type', 'sqlite')
    logger.info(f"为域'{domain}'创建{storage_type}存储适配器")
    
    if storage_type == 'sqlite':
        db_path = config.get('database', {}).get('path', 'data/db/nextbook.db')
        return SQLiteStorage(domain, db_path)
    elif storage_type == 'postgresql':
        # PostgreSQL配置
        db_config = {
            'host': config.get('database', {}).get('host', 'localhost'),
            'port': config.get('database', {}).get('port', 5432),
            'database': config.get('database', {}).get('database', 'nextbook'),
            'user': config.get('database', {}).get('user', 'nextbook_user'),
            'password': config.get('database', {}).get('password', ''),
        }
        # 在实际实现中应返回PostgreSQLStorage实例
        # return PostgreSQLStorage(domain, db_config)
        raise ValueError("PostgreSQL存储尚未实现")
    elif storage_type == 'vector':
        vector_path = config.get('vector_database', {}).get('path', 'data/db/vectors')
        vector_type = config.get('vector_database', {}).get('type', 'chroma')
        return VectorStorage(domain, vector_path, vector_type)
    elif storage_type == 'file':
        file_path = config.get('files', {}).get('path', 'data/files')
        return FileStorage(domain, file_path)
    else:
        raise ValueError(f"不支持的存储类型: {storage_type}")
