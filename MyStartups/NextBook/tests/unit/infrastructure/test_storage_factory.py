"""
存储工厂的单元测试

测试存储工厂如何根据不同平台和配置创建适当的存储适配器。
"""

import pytest
from unittest import mock

# 测试类
class TestStorageFactory:
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建模拟实现
        self.mock_storage_implementations = {
            "memory": mock.Mock(),
            "file": mock.Mock(),
            "database": mock.Mock(),
        }
        
        # 创建模拟配置
        self.mock_config = {
            "storage": {
                "default": "memory",
                "options": {
                    "memory": {"max_size": 1000},
                    "file": {"directory": "/tmp/storage"},
                    "database": {"connection_string": "sqlite:///test.db"}
                }
            }
        }
    
    def test_factory_creates_correct_implementation(self):
        """测试工厂创建正确的存储实现"""
        # 模拟配置获取函数
        mock_get_config = mock.Mock(return_value=self.mock_config)
        
        # 对每种存储类型进行测试
        for storage_type in ["memory", "file", "database"]:
            # 模拟工厂方法
            mock_factory = mock.Mock()
            mock_factory.create_adapter.return_value = self.mock_storage_implementations[storage_type]
            
            # 调用工厂创建适配器
            adapter = mock_factory.create_adapter(storage_type)
            
            # 验证正确的适配器被创建
            assert adapter == self.mock_storage_implementations[storage_type]
            mock_factory.create_adapter.assert_called_with(storage_type)
    
    def test_factory_uses_default_when_type_not_specified(self):
        """测试未指定类型时使用默认实现"""
        # 模拟配置获取函数
        mock_get_config = mock.Mock(return_value=self.mock_config)
        
        # 模拟工厂方法
        mock_factory = mock.Mock()
        default_implementation = self.mock_storage_implementations["memory"]
        mock_factory.create_adapter.return_value = default_implementation
        
        # 调用工厂创建适配器（不指定类型）
        adapter = mock_factory.create_adapter()
        
        # 验证默认适配器被创建
        assert adapter == default_implementation
        mock_factory.create_adapter.assert_called_once()
