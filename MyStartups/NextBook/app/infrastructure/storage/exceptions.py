"""
存储相关异常
"""

class StorageError(Exception):
    """存储操作基础异常类"""
    pass

class StorageConnectionError(StorageError):
    """存储连接异常"""
    pass

class StorageTransactionError(Exception):
    """存储事务错误"""
    pass

class StorageNotFoundError(StorageError):
    """数据不存在异常"""
    pass

class StoragePermissionError(StorageError):
    """存储权限异常"""
    pass
