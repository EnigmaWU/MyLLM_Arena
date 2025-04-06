"""
存储适配器的基类

定义所有存储实现必须遵循的接口契约。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic, Tuple

T = TypeVar('T')  # 泛型类型参数，代表存储的实体类型

class BaseStorage(Generic[T], ABC):
    """存储适配器基类"""
    
    @abstractmethod
    def initialize(self) -> None:
        """初始化存储，例如创建表或索引"""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """关闭存储，释放资源"""
        pass
    
    @abstractmethod
    def create(self, entity: T) -> str:
        """
        创建新实体
        
        Args:
            entity: 要存储的实体
            
        Returns:
            新实体的ID
        """
        pass
    
    @abstractmethod
    def read(self, entity_id: str) -> Optional[T]:
        """
        读取实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            找到的实体，未找到时返回None
        """
        pass
    
    @abstractmethod
    def update(self, entity: T) -> bool:
        """
        更新实体
        
        Args:
            entity: 要更新的实体
            
        Returns:
            更新是否成功
        """
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """
        删除实体
        
        Args:
            entity_id: 要删除的实体ID
            
        Returns:
            删除是否成功
        """
        pass
    
    @abstractmethod
    def list(self, filters: Dict[str, Any] = None, order_by: str = None, 
             limit: int = None, offset: int = None) -> List[T]:
        """
        列出多个实体
        
        Args:
            filters: 过滤条件
            order_by: 排序字段
            limit: 返回数量限制
            offset: 结果偏移量
            
        Returns:
            符合条件的实体列表
        """
        pass
    
    @abstractmethod
    def count(self, filters: Dict[str, Any] = None) -> int:
        """
        计算符合条件的实体数量
        
        Args:
            filters: 过滤条件
            
        Returns:
            符合条件的实体数量
        """
        pass
    
    @abstractmethod
    def search(self, query: str, fields: List[str] = None) -> List[Tuple[T, float]]:
        """
        搜索实体
        
        Args:
            query: 搜索查询
            fields: 要搜索的字段
            
        Returns:
            匹配实体和相关度得分的列表
        """
        pass
    
    @abstractmethod
    def exists(self, entity_id: str) -> bool:
        """
        检查实体是否存在
        
        Args:
            entity_id: 实体ID
            
        Returns:
            实体是否存在
        """
        pass
