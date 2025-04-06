"""
存储适配器工厂

负责创建与当前平台匹配的存储适配器实例。
"""

import platform
import logging
from typing import Dict, Any, Type, Optional

from .base import BaseStorage
from .exceptions import StorageError

class StorageFactory:
    """存储适配器工厂类"""
    
    def __init__(self):
        """初始化存储工厂"""
        self.logger = logging.getLogger("nextbook.infrastructure.storage.factory")
        self._implementations = {}  # 平台名称 -> 存储实现的映射
        self._instances = {}  # 域名 -> 存储实例的映射
    
    def register_implementation(self, platform_name: str, implementation: Any) -> None:
        """
        注册平台特定的存储实现
        
        Args:
            platform_name: 平台名称 (如 "Darwin", "Windows", "Linux")
            implementation: 存储实现类或工厂函数
        """
        self.logger.debug(f"注册平台存储实现: {platform_name}")
        self._implementations[platform_name] = implementation
    
    def create_adapter(self, domain: str, config: Dict[str, Any] = None) -> BaseStorage:
        """
        创建与当前平台匹配的存储适配器实例
        
        Args:
            domain: 存储域名 (如 "content", "user", "note")
            config: 可选的配置参数
            
        Returns:
            适合当前平台的存储适配器实例
            
        Raises:
            StorageError: 如果无法找到匹配的实现或创建失败
        """
        # 检查是否已经有该域的实例
        if domain in self._instances:
            self.logger.debug(f"返回已存在的存储适配器: {domain}")
            return self._instances[domain]
        
        # 获取当前平台名称
        current_platform = platform.system()
        self.logger.info(f"当前平台: {current_platform}, 为域'{domain}'创建存储适配器")
        
        # 获取适合当前平台的实现
        implementation = self._get_implementation_for_platform(current_platform)
        
        if not implementation:
            raise StorageError(f"未找到适用于平台'{current_platform}'的存储实现")
        
        # 创建适配器实例
        try:
            if callable(implementation) and not isinstance(implementation, type):
                # 如果是工厂函数
                adapter = implementation(domain, config)
            else:
                # 如果是类
                adapter = implementation()
                if config:
                    adapter.configure(config)
            
            # 缓存实例
            self._instances[domain] = adapter
            return adapter
            
        except Exception as e:
            self.logger.error(f"创建存储适配器失败: {str(e)}", exc_info=True)
            raise StorageError(f"创建存储适配器失败: {str(e)}")
    
    def _get_implementation_for_platform(self, platform_name: str) -> Any:
        """
        获取适合指定平台的存储实现
        
        Args:
            platform_name: 平台名称
            
        Returns:
            存储实现类或工厂函数，如果未找到则返回None
        """
        # 首先尝试精确匹配
        if platform_name in self._implementations:
            return self._implementations[platform_name]
        
        # 然后尝试部分匹配
        for registered_platform, implementation in self._implementations.items():
            if registered_platform.lower() in platform_name.lower() or platform_name.lower() in registered_platform.lower():
                self.logger.debug(f"使用部分匹配的平台实现: {registered_platform}")
                return implementation
        
        # 最后尝试使用默认实现
        if "default" in self._implementations:
            self.logger.debug("使用默认存储实现")
            return self._implementations["default"]
        
        return None
    
    def clear_instances(self) -> None:
        """清除所有已创建的适配器实例"""
        self.logger.debug("清除所有存储适配器实例")
        for instance in self._instances.values():
            try:
                instance.shutdown()
            except Exception as e:
                self.logger.warning(f"关闭存储适配器时出错: {str(e)}")
        self._instances.clear()
