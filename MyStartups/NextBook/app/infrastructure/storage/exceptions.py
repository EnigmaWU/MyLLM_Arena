"""
存储适配器异常定义
"""

class StorageError(Exception):
    """存储操作基础异常类"""
    pass

class StorageConnectionError(StorageError):
    """存储连接异常"""
    pass

class StorageTransactionError(StorageError):
    """事务操作异常"""
    pass

class StorageNotFoundError(StorageError):
    """数据不存在异常"""
    pass

class StoragePermissionError(StorageError):
    """存储权限异常"""
    pass
