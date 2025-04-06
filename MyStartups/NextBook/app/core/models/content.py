"""
内容相关的领域模型
"""

import uuid
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

class ContentType(Enum):
    """内容类型枚举"""
    PDF = auto()
    EPUB = auto()
    TEXT = auto()
    HTML = auto()
    MARKDOWN = auto()
    OTHER = auto()

@dataclass
class ContentMetadata:
    """表示内容的元数据"""
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[datetime] = None
    language: Optional[str] = None
    isbn: Optional[str] = None
    doi: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    page_count: Optional[int] = None
    toc: Dict[str, Any] = field(default_factory=dict)  # 目录结构
    custom_fields: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Content:
    """表示一个内容项(书籍、文章等)"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_type: ContentType = ContentType.OTHER
    metadata: ContentMetadata = field(default_factory=ContentMetadata)
    
    # 文件信息
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    
    # 系统字段
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    imported_by: Optional[str] = None  # 用户ID或导入源
    
    # 状态
    is_processed: bool = False
    is_indexed: bool = False
    processing_errors: List[str] = field(default_factory=list)
    
    # 关联数据
    tags: List[str] = field(default_factory=list)
    notes_count: int = 0
    
    def update_metadata(self, new_metadata: ContentMetadata):
        """更新内容元数据"""
        self.metadata = new_metadata
        self.updated_at = datetime.now()
    
    def mark_as_processed(self):
        """标记内容已处理"""
        self.is_processed = True
        self.updated_at = datetime.now()
    
    def mark_as_indexed(self):
        """标记内容已索引"""
        self.is_indexed = True
        self.updated_at = datetime.now()
    
    def add_error(self, error: str):
        """添加处理错误"""
        self.processing_errors.append(error)
        self.updated_at = datetime.now()
