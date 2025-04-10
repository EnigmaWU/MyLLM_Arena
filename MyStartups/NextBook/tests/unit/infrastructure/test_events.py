"""
事件基础设施的单元测试

测试事件发布、订阅和触发机制。
"""

import pytest
from unittest import mock

# 模拟事件类
class Event:
    def __init__(self, name, data=None):
        self.name = name
        self.data = data or {}

# 测试类
class TestEventInfrastructure:
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.event_handlers = {}
        self.published_events = []
    
    def mock_subscribe(self, event_name, handler):
        """模拟事件订阅"""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
    
    def mock_publish(self, event):
        """模拟事件发布"""
        self.published_events.append(event)
        if event.name in self.event_handlers:
            for handler in self.event_handlers[event.name]:
                handler(event)
    
    def test_event_subscribe_and_publish(self):
        """测试事件的订阅和发布"""
        # 创建模拟处理器
        handler = mock.Mock()
        
        # 订阅事件
        self.mock_subscribe("test_event", handler)
        
        # 发布事件
        test_event = Event("test_event", {"key": "value"})
        self.mock_publish(test_event)
        
        # 验证处理器被调用
        handler.assert_called_once()
        handler.assert_called_with(test_event)
        
        # 验证事件被发布
        assert len(self.published_events) == 1
        assert self.published_events[0].name == "test_event"
        assert self.published_events[0].data == {"key": "value"}
    
    def test_multiple_handlers(self):
        """测试多个处理器订阅同一事件"""
        handler1 = mock.Mock()
        handler2 = mock.Mock()
        
        # 多个处理器订阅同一事件
        self.mock_subscribe("shared_event", handler1)
        self.mock_subscribe("shared_event", handler2)
        
        # 发布事件
        shared_event = Event("shared_event", {"shared": "data"})
        self.mock_publish(shared_event)
        
        # 验证所有处理器都被调用
        handler1.assert_called_once_with(shared_event)
        handler2.assert_called_once_with(shared_event)
