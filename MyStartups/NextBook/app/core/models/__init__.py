"""
核心数据模型

这个包包含应用的领域模型类，表示系统中的基本实体和它们之间的关系。
这些模型反映了领域驱动设计(DDD)方法，实现了业务逻辑和规则。
"""

from .content import Content, ContentType, ContentMetadata
from .user import User, UserPreferences
from .note import Note, NoteType, NoteTag
from .reading import ReadingRecord, ReadingProgress, ReadingSession
from .recommendation import BookRecommendation, RecommendationReason
from .knowledge import KnowledgeEntity, KnowledgeRelation, KnowledgeGraph

__all__ = [
    'Content', 'ContentType', 'ContentMetadata',
    'User', 'UserPreferences',
    'Note', 'NoteType', 'NoteTag',
    'ReadingRecord', 'ReadingProgress', 'ReadingSession',
    'BookRecommendation', 'RecommendationReason',
    'KnowledgeEntity', 'KnowledgeRelation', 'KnowledgeGraph'
]
