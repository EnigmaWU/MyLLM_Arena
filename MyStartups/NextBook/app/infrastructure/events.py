"""
事件系统

实现应用内的事件发布-订阅机制，支持组件间的松耦合通信。
"""

import logging
import uuid
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime

class Event:
    """事件基类"""
    
    def __init__(self, event_type: str, data: Dict[str, Any] = None):
        """初始化事件对象
        
        Args:
            event_type: 事件类型
            data: 事件数据
        """
        self.id = str(uuid.uuid4())
        self.type = event_type
        self.data = data or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """将事件转换为字典
        
        Returns:
            事件字典表示
        """
        return {
            "id": self.id,
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }

class EventBus:
    """事件总线，处理事件的发布和订阅"""
    
    def __init__(self):
        """初始化事件总线"""
        self.logger = logging.getLogger("nextbook.infrastructure.events")
        self.subscribers: Dict[str, List[Callable]] = {}
        self.history: List[Event] = []
        self.max_history = 100  # 保留的最大历史事件数量
    
    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """订阅事件
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(handler)
        self.logger.debug(f"已订阅事件类型: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable[[Event], None]) -> bool:
        """取消事件订阅
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数
            
        Returns:
            是否成功取消订阅
        """
        if event_type in self.subscribers and handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)
            self.logger.debug(f"已取消订阅事件类型: {event_type}")
            return True
        return False
    
    def publish(self, event: Event) -> None:
        """发布事件
        
        Args:
            event: 要发布的事件
        """
        self.logger.debug(f"发布事件: {event.type}, ID: {event.id}")
        
        # 添加到历史记录
        self.history.append(event)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # 通知订阅者
        if event.type in self.subscribers:
            for handler in self.subscribers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"事件处理错误: {str(e)}")
    
    def get_history(self, event_type: Optional[str] = None) -> List[Event]:
        """获取事件历史
        
        Args:
            event_type: 可选的事件类型过滤
            
        Returns:
            历史事件列表
        """
        if event_type:
            return [event for event in self.history if event.type == event_type]
        return self.history.copy()
