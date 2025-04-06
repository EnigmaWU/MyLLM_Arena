"""
插件系统基类

定义所有插件必须遵循的接口契约。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class Plugin(ABC):
    """插件基类"""
    
    def __init__(self):
        """初始化插件"""
        self.id = ""  # 唯一标识符
        self.name = ""  # 显示名称
        self.version = ""  # 版本号
        self.description = ""  # 描述
        self.author = ""  # 作者
        self.ready = False  # 是否准备就绪
        self.error = None  # 错误信息
    
    @abstractmethod
    def initialize(self) -> None:
        """初始化插件，检查依赖等"""
        pass
    
    def is_ready(self) -> bool:
        """检查插件是否准备就绪
        
        Returns:
            插件是否可用
        """
        return self.ready
    
    def get_error(self) -> Optional[str]:
        """获取插件错误信息
        
        Returns:
            错误信息，如果没有错误则为None
        """
        return self.error

class ContentProcessorPlugin(Plugin):
    """内容处理器插件基类"""
    
    def __init__(self):
        """初始化内容处理器插件"""
        super().__init__()
        self.supported_formats = []  # 支持的文件格式列表
    
    @abstractmethod
    def can_handle(self, file_path: str) -> bool:
        """判断是否能处理给定文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            是否能处理
        """
        pass
    
    @abstractmethod
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """从文件中提取元数据
        
        Args:
            file_path: 文件路径
        
        Returns:
            元数据字典
        """
        pass
    
    @abstractmethod
    def extract_content(self, file_path: str) -> Dict[str, Any]:
        """从文件中提取内容
        
        Args:
            file_path: 文件路径
        
        Returns:
            内容字典
        """
        pass
    
    @abstractmethod
    def process(self, file_path: str) -> Dict[str, Any]:
        """处理文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            处理结果
        """
        pass
