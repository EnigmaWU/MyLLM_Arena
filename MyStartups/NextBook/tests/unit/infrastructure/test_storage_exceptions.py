"""
存储异常处理的单元测试

测试存储操作中的异常情况处理。
"""

import pytest

# 模拟存储异常
class StorageError(Exception):
    """存储错误基类"""
    pass

class StorageConnectionError(StorageError):
    """存储连接错误"""
    pass

class StorageReadError(StorageError):
    """存储读取错误"""
    pass

class StorageWriteError(StorageError):
    """存储写入错误"""
    pass

class StorageDeleteError(StorageError):
    """存储删除错误"""
    pass

class StorageTransactionError(StorageError):
    """存储事务错误"""
    pass

# 测试类
class TestStorageExceptions:
    
    def test_exception_hierarchy(self):
        """测试异常继承层次结构"""
        # 验证所有异常都是 StorageError 的子类
        assert issubclass(StorageConnectionError, StorageError)
        assert issubclass(StorageReadError, StorageError)
        assert issubclass(StorageWriteError, StorageError)
        assert issubclass(StorageDeleteError, StorageError)
        assert issubclass(StorageTransactionError, StorageError)
    
    def test_exception_raising_and_catching(self):
        """测试异常的抛出和捕获"""
        
        # 测试抛出和捕获 StorageConnectionError
        with pytest.raises(StorageConnectionError):
            raise StorageConnectionError("无法连接存储")
        
        # 测试抛出和捕获所有存储异常
        with pytest.raises(StorageError):
            raise StorageReadError("读取错误")
        
        with pytest.raises(StorageError):
            raise StorageWriteError("写入错误")
        
        # 测试特定异常捕获
        try:
            raise StorageDeleteError("删除错误")
        except StorageDeleteError as e:
            assert str(e) == "删除错误"
        except Exception:
            pytest.fail("捕获了错误的异常类型")
    
    def test_exception_with_context(self):
        """测试带有上下文信息的异常"""
        context = {"entity_id": "12345", "operation": "update"}
        
        # 创建带有上下文的异常
        def raise_contextual_error():
            error = StorageWriteError("写入实体时出错")
            error.context = context
            raise error
        
        # 捕获并检查异常上下文
        try:
            raise_contextual_error()
        except StorageWriteError as e:
            assert hasattr(e, "context")
            assert e.context["entity_id"] == "12345"
            assert e.context["operation"] == "update"
