"""
存储适配器的集成测试

测试存储适配器在实际环境中与其他组件的集成情况。
"""

import pytest
import os
import tempfile
from typing import Dict, Any

from app.core.models import Content, Note
from app.infrastructure.storage.factory import StorageFactory
from app.infrastructure.storage.exceptions import StorageError

class TestStorageIntegration:
    """存储适配器集成测试类"""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """创建临时存储目录"""
        temp_dir = tempfile.mkdtemp(prefix="nextbook_test_")
        yield temp_dir
        # 测试后清理
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_dir)
    
    @pytest.fixture
    def content_storage(self, temp_storage_dir):
        """创建内容存储适配器"""
        factory = StorageFactory()
        adapter = factory.create_adapter("content")
        
        # 配置适配器使用临时目录
        adapter.configure({
            "storage_path": os.path.join(temp_storage_dir, "content"),
            "db_path": os.path.join(temp_storage_dir, "content.db")
        })
        
        adapter.initialize()
        yield adapter
        adapter.shutdown()
    
    def test_content_storage_integration(self, content_storage):
        """测试内容存储适配器在实际环境中的表现"""
        # 创建测试内容
        test_content = Content(
            title="测试书籍",
            author="测试作者",
            file_path="/tmp/test.pdf",
            file_type="pdf",
            metadata={
                "language": "中文",
                "pages": 100,
                "published_year": 2023
            }
        )
        
        # 验收条件1：存储请求正确转换为特定平台的存储操作
        content_id = content_storage.create(test_content)
        assert content_id is not None
        assert content_storage.exists(content_id)
        
        # 读取内容并验证
        retrieved_content = content_storage.read(content_id)
        assert retrieved_content is not None
        assert retrieved_content.title == "测试书籍"
        assert retrieved_content.author == "测试作者"
        
        # 验收条件2：查询请求使用平台特定查询并标准化结果
        # 基本查询
        content_list = content_storage.list(filters={"author": "测试作者"})
        assert len(content_list) == 1
        assert content_list[0].title == "测试书籍"
        
        # 高级搜索
        search_results = content_storage.search("测试", fields=["title", "author"])
        assert len(search_results) > 0
        content, relevance = search_results[0]
        assert content.title == "测试书籍"
        assert relevance > 0
        
        # 验收条件3：事务性操作确保完整性和一致性
        # 启动事务
        content_storage.begin_transaction()
        
        # 在事务中修改内容
        retrieved_content.title = "更新的书籍标题"
        content_storage.update(retrieved_content)
        
        # 在事务中添加另一个内容
        another_content = Content(
            title="另一本书",
            author="另一位作者",
            file_path="/tmp/another.epub",
            file_type="epub"
        )
        another_id = content_storage.create(another_content)
        
        # 提交事务
        content_storage.commit_transaction()
        
        # 验证事务提交结果
        assert content_storage.exists(another_id)
        updated = content_storage.read(content_id)
        assert updated.title == "更新的书籍标题"
        
        # 测试回滚场景
        content_storage.begin_transaction()
        content_storage.delete(content_id)  # 尝试删除内容
        assert not content_storage.exists(content_id)  # 在事务中不可见
        
        content_storage.rollback_transaction()  # 回滚删除操作
        assert content_storage.exists(content_id)  # 回滚后内容仍然存在
