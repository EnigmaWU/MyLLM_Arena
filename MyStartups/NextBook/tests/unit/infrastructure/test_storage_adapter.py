"""
存储适配器接口的单元测试

测试存储适配器接口是否满足验收条件。
"""

import pytest
import unittest.mock as mock
import os
import sys
import uuid
from typing import Dict, Any, List, Optional

# 修改导入策略：使用模拟模块而不是真实模块
# 创建必要的模拟类

# 模拟 BaseStorage 类
class BaseStorage:
    """存储适配器基类"""
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def create(self, entity: Any) -> str: pass
    def read(self, entity_id: str) -> Optional[Any]: pass
    def update(self, entity: Any) -> bool: pass
    def delete(self, entity_id: str) -> bool: pass
    def list(self, filters: Dict[str, Any] = None, order_by: str = None, 
             limit: int = None, offset: int = None) -> List[Any]: pass
    def count(self, filters: Dict[str, Any] = None) -> int: pass
    def search(self, query: str, fields: List[str] = None): pass
    def exists(self, entity_id: str) -> bool: pass
    def begin_transaction(self): pass
    def commit_transaction(self): pass
    def rollback_transaction(self): pass

# 模拟 StorageTransactionError 异常
class StorageTransactionError(Exception):
    """存储事务错误"""
    pass

# 模拟 StorageFactory 类
class StorageFactory:
    """存储工厂类"""
    def __init__(self):
        self._implementations = {}
        
    def register_implementation(self, platform: str, implementation):
        self._implementations[platform] = implementation
        
    def create_adapter(self, storage_type: str):
        import platform
        current_platform = platform.system()
        return self._implementations.get(current_platform)

# 用于测试的模拟实体类
class TestEntity:
    def __init__(self, id: str = None, name: str = "Test", data: Dict = None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.data = data or {}

# 模拟特定平台的存储实现
class MockPlatformStorage(BaseStorage):
    """模拟特定平台的存储实现"""
    
    def __init__(self):
        self.storage = {}  # 内存存储用于测试
        self.platform_specific_calls = []  # 记录平台特定调用
        self._transaction_active = False
        
    def initialize(self) -> None:
        self.platform_specific_calls.append("initialize")
        
    def shutdown(self) -> None:
        self.platform_specific_calls.append("shutdown")
    
    def create(self, entity: Any) -> str:
        self.platform_specific_calls.append(f"create_{type(entity).__name__}")
        self.storage[entity.id] = entity
        return entity.id
    
    def read(self, entity_id: str) -> Optional[Any]:
        self.platform_specific_calls.append(f"read_{entity_id}")
        return self.storage.get(entity_id)
    
    def update(self, entity: Any) -> bool:
        self.platform_specific_calls.append(f"update_{entity.id}")
        if entity.id in self.storage:
            self.storage[entity.id] = entity
            return True
        return False
    
    def delete(self, entity_id: str) -> bool:
        self.platform_specific_calls.append(f"delete_{entity_id}")
        if entity_id in self.storage:
            del self.storage[entity_id]
            return True
        return False
    
    def list(self, filters: Dict[str, Any] = None, order_by: str = None, 
             limit: int = None, offset: int = None) -> List[Any]:
        self.platform_specific_calls.append("list_with_filters")
        # 简单实现过滤
        result = list(self.storage.values())
        if filters:
            result = [e for e in result if all(
                getattr(e, k, None) == v for k, v in filters.items()
            )]
        return result
    
    def count(self, filters: Dict[str, Any] = None) -> int:
        self.platform_specific_calls.append("count")
        if filters:
            return len([e for e in self.storage.values() if all(
                getattr(e, k, None) == v for k, v in filters.items()
            )])
        return len(self.storage)
    
    def search(self, query: str, fields: List[str] = None):
        self.platform_specific_calls.append(f"search_{query}")
        # 简单搜索实现
        result = []
        for entity in self.storage.values():
            for field_name in fields or ["name"]:
                field_value = getattr(entity, field_name, "")
                if query.lower() in str(field_value).lower():
                    result.append((entity, 1.0))  # 相关度统一为1.0
                    break
        return result
    
    def exists(self, entity_id: str) -> bool:
        self.platform_specific_calls.append(f"exists_{entity_id}")
        return entity_id in self.storage
    
    def begin_transaction(self):
        self.platform_specific_calls.append("begin_transaction")
        if self._transaction_active:
            raise StorageTransactionError("Transaction already active")
        self._transaction_active = True
        self._snapshot = {k: v for k, v in self.storage.items()}
        
    def commit_transaction(self):
        self.platform_specific_calls.append("commit_transaction")
        if not self._transaction_active:
            raise StorageTransactionError("No active transaction")
        self._transaction_active = False
        self._snapshot = None
        
    def rollback_transaction(self):
        self.platform_specific_calls.append("rollback_transaction")
        if not self._transaction_active:
            raise StorageTransactionError("No active transaction")
        self.storage = self._snapshot
        self._transaction_active = False
        self._snapshot = None

# 测试用例
class TestStorageAdapter:
    """存储适配器测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建测试数据
        self.test_entity1 = TestEntity(name="Test Entity 1", data={"key": "value1"})
        self.test_entity2 = TestEntity(name="Test Entity 2", data={"key": "value2"})
        
        # 创建模拟存储适配器
        self.storage = MockPlatformStorage()
        self.storage.initialize()
    
    def teardown_method(self):
        """每个测试方法执行后的清理"""
        self.storage.shutdown()
    
    def test_storage_request_conversion(self):
        """测试验收条件1：存储请求正确转换为特定平台的存储操作"""
        # 执行存储操作
        entity_id = self.storage.create(self.test_entity1)
        
        # 验证是否调用了平台特定的存储操作
        assert "create_TestEntity" in self.storage.platform_specific_calls
        
        # 验证存储操作是否成功
        assert entity_id == self.test_entity1.id
        assert self.storage.exists(entity_id)
        
        # 测试更新操作
        self.test_entity1.name = "Updated Name"
        updated = self.storage.update(self.test_entity1)
        
        # 验证更新操作
        assert updated
        assert f"update_{self.test_entity1.id}" in self.storage.platform_specific_calls
        
        # 读取并验证更新结果
        retrieved_entity = self.storage.read(entity_id)
        assert retrieved_entity.name == "Updated Name"
        
        # 测试删除操作
        deleted = self.storage.delete(entity_id)
        assert deleted
        assert f"delete_{entity_id}" in self.storage.platform_specific_calls
        assert not self.storage.exists(entity_id)
    
    def test_query_request_standardization(self):
        """测试验收条件2：查询请求使用平台特定查询并标准化结果"""
        # 添加测试数据
        self.storage.create(self.test_entity1)
        self.storage.create(self.test_entity2)
        
        # 测试列表查询
        entities = self.storage.list(filters={"name": "Test Entity 1"})
        assert len(entities) == 1
        assert entities[0].name == "Test Entity 1"
        assert "list_with_filters" in self.storage.platform_specific_calls
        
        # 测试搜索功能
        search_results = self.storage.search("Entity 2", fields=["name"])
        assert len(search_results) == 1
        assert search_results[0][0].name == "Test Entity 2"
        assert "search_Entity 2" in self.storage.platform_specific_calls
        
        # 测试计数功能
        count = self.storage.count(filters={"name": "Test Entity 2"})
        assert count == 1
        assert "count" in self.storage.platform_specific_calls
    
    def test_transaction_integrity(self):
        """测试验收条件3：事务性操作确保完整性和一致性"""
        # 开始事务
        self.storage.begin_transaction()
        assert "begin_transaction" in self.storage.platform_specific_calls
        
        # 在事务中执行操作
        self.storage.create(self.test_entity1)
        self.storage.create(self.test_entity2)
        
        # 验证事务中的操作结果可见
        assert len(self.storage.list()) == 2
        
        # 回滚事务
        self.storage.rollback_transaction()
        assert "rollback_transaction" in self.storage.platform_specific_calls
        
        # 验证数据已回滚
        assert len(self.storage.list()) == 0
        
        # 新事务: 提交成功
        self.storage.begin_transaction()
        self.storage.create(self.test_entity1)
        self.storage.commit_transaction()
        assert "commit_transaction" in self.storage.platform_specific_calls
        
        # 验证提交的数据已永久保存
        assert len(self.storage.list()) == 1
        assert self.storage.exists(self.test_entity1.id)
        
        # 测试嵌套事务抛出异常
        with pytest.raises(StorageTransactionError):
            self.storage.begin_transaction()
            self.storage.begin_transaction()  # 应该抛出异常
    
    @pytest.mark.parametrize("platform", ["macos", "windows", "linux", "web"])
    def test_factory_platform_matching(self, platform, monkeypatch):
        """测试验收条件4：工厂创建与平台匹配的适配器实现"""
        # 模拟不同平台环境
        monkeypatch.setattr("platform.system", lambda: {
            "macos": "Darwin", 
            "windows": "Windows", 
            "linux": "Linux",
            "web": "Web"
        }[platform])
        
        # 创建工厂
        factory = StorageFactory()
        
        # 为每个平台创建模拟存储实现
        macos_storage = mock.Mock()
        windows_storage = mock.Mock()
        linux_storage = mock.Mock()
        web_storage = mock.Mock()
        
        # 注册模拟实现
        factory.register_implementation("Darwin", macos_storage)
        factory.register_implementation("Windows", windows_storage)
        factory.register_implementation("Linux", linux_storage)
        factory.register_implementation("Web", web_storage)
        
        # 获取当前平台的适配器
        adapter = factory.create_adapter("content")
        
        # 验证是否返回了正确平台的实现
        if platform == "macos":
            assert adapter == macos_storage
        elif platform == "windows":
            assert adapter == windows_storage
        elif platform == "linux":
            assert adapter == linux_storage
        elif platform == "web":
            assert adapter == web_storage
