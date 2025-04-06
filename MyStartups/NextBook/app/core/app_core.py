"""
AppCore类作为应用核心，负责协调四大功能模块，管理应用生命周期,
并提供统一的接口给UI层和基础设施层。
"""

import logging
from typing import Dict, Any

from .content import ContentManager
from .recommendation import RecommendationManager
from .knowledge import KnowledgeManager
from .analytics import AnalyticsManager
from ..infrastructure.events import EventBus

class AppCore:
    """NextBook Agent应用核心"""
    
    def __init__(self, config: Dict[str, Any], infrastructure):
        """
        初始化应用核心
        
        Args:
            config: 应用配置
            infrastructure: 基础设施依赖
        """
        self.logger = logging.getLogger("nextbook.core")
        self.config = config
        self.infra = infrastructure
        self.event_bus = EventBus()
        
        self.logger.info("初始化应用核心...")
        
        # 初始化四大功能模块
        self.content_manager = ContentManager(self.config, self.infra, self.event_bus)
        self.recommendation_manager = RecommendationManager(self.config, self.infra, self.event_bus)
        self.knowledge_manager = KnowledgeManager(self.config, self.infra, self.event_bus)
        self.analytics_manager = AnalyticsManager(self.config, self.infra, self.event_bus)
        
        self.logger.info("应用核心初始化完成")
    
    def startup(self):
        """执行应用启动流程"""
        self.logger.info("启动应用模块...")
        
        # 按顺序启动各个模块
        self.content_manager.startup()
        self.knowledge_manager.startup()
        self.recommendation_manager.startup()
        self.analytics_manager.startup()
        
        self.logger.info("所有模块已启动")
    
    def shutdown(self):
        """执行应用关闭流程"""
        self.logger.info("关闭应用模块...")
        
        # 按相反顺序关闭模块
        self.analytics_manager.shutdown()
        self.recommendation_manager.shutdown()
        self.knowledge_manager.shutdown()
        self.content_manager.shutdown()
        
        # 关闭基础设施
        if hasattr(self.infra, 'shutdown'):
            self.infra.shutdown()
        
        self.logger.info("所有模块已关闭")

    # 获取各管理器的便捷方法
    @property
    def content(self):
        """获取内容管理器"""
        return self.content_manager
    
    @property
    def recommendation(self):
        """获取推荐管理器"""
        return self.recommendation_manager
    
    @property
    def knowledge(self):
        """获取知识管理器"""
        return self.knowledge_manager
    
    @property
    def analytics(self):
        """获取分析管理器"""
        return self.analytics_manager
