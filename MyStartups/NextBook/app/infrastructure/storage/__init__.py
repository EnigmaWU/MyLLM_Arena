"""
存储适配器模块

提供对不同存储后端的统一访问接口。实现存储抽象，
支持多种存储选项（SQLite、PostgreSQL等），并处理数据持久化。
"""

from .factory import create_storage
from .base import BaseStorage
from .sqlite_storage import SQLiteStorage
from .vector_storage import VectorStorage
from .file_storage import FileStorage

__all__ = ['create_storage', 'BaseStorage', 'SQLiteStorage', 'VectorStorage', 'FileStorage']
