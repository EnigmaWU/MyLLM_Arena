"""
基础设施层
"""

import logging
from typing import Dict, Any, Optional

from .storage import create_storage
from .events import EventBus

class Infrastructure:
    """基础设施服务容器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化基础设施
        
        Args:
            config: 应用配置
        """
        self.logger = logging.getLogger("nextbook.infrastructure")
        self.config = config
        self.storages = {}
        self.event_bus = None
        self.document_processor = None
        self.search_engine = None
        self.report_generator = None
        self.ai_service = None
    
    def initialize(self):
        """初始化所有基础设施服务"""
        self.logger.info("初始化基础设施...")
        
        # 初始化事件总线
        self.event_bus = EventBus()
        
        # 初始化存储服务
        storage_config = self.config.get('storage', {})
        self._initialize_storage(storage_config)
        
        # 初始化其他服务
        self._initialize_document_processor()
        self._initialize_search_engine()
        self._initialize_report_generator()
        self._initialize_ai_service()
        
        self.logger.info("基础设施初始化完成")
    
    def _initialize_storage(self, storage_config: Dict[str, Any]):
        """初始化存储服务
        
        Args:
            storage_config: 存储配置
        """
        self.logger.info("初始化存储服务...")
        
        # 创建不同域的存储适配器
        domains = ["content", "user", "recommendation", "knowledge", "analytics"]
        
        for domain in domains:
            try:
                self.storages[domain] = create_storage(domain, storage_config)
                self.storages[domain].initialize()
                self.logger.info(f"已初始化{domain}存储")
            except Exception as e:
                self.logger.error(f"初始化{domain}存储失败: {str(e)}")
    
    def _initialize_document_processor(self):
        """初始化文档处理器"""
        self.logger.info("初始化文档处理器...")
        # 实际实现会创建文档处理器实例
        
    def _initialize_search_engine(self):
        """初始化搜索引擎"""
        self.logger.info("初始化搜索引擎...")
        # 实际实现会创建搜索引擎实例
        
    def _initialize_report_generator(self):
        """初始化报告生成器"""
        self.logger.info("初始化报告生成器...")
        # 实际实现会创建报告生成器实例
        
    def _initialize_ai_service(self):
        """初始化AI服务"""
        self.logger.info("初始化AI服务...")
        # 实际实现会创建AI服务实例
    
    def get_storage(self, domain: str):
        """获取指定域的存储适配器
        
        Args:
            domain: 存储域名称
        
        Returns:
            存储适配器实例
        
        Raises:
            ValueError: 当请求的存储域不存在时
        """
        if domain in self.storages:
            return self.storages[domain]
        
        raise ValueError(f"未知的存储域: {domain}")
    
    def get_document_processor(self):
        """获取文档处理器"""
        return self.document_processor
    
    def get_search_engine(self):
        """获取搜索引擎"""
        return self.search_engine
    
    def get_report_generator(self):
        """获取报告生成器"""
        return self.report_generator
    
    def get_ai_service(self):
        """获取AI服务"""
        return self.ai_service
    
    def shutdown(self):
        """关闭所有基础设施服务"""
        self.logger.info("关闭基础设施服务...")
        
        # 关闭存储服务
        for domain, storage in self.storages.items():
            try:
                storage.shutdown()
                self.logger.info(f"已关闭{domain}存储")
            except Exception as e:
                self.logger.error(f"关闭{domain}存储失败: {str(e)}")
        
        # 关闭其他服务
        # ...

def initialize_infrastructure(config: Dict[str, Any]) -> Infrastructure:
    """初始化并返回基础设施服务容器
    
    Args:
        config: 应用配置
    
    Returns:
        基础设施服务容器
    """
    infrastructure = Infrastructure(config)
    infrastructure.initialize()
    return infrastructure
