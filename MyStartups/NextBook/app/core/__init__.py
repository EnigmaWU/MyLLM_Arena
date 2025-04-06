"""
NextBook Agent 核心模块

这个包包含应用程序的核心业务逻辑，组织为四个主要功能模块:
- content: SAVE功能模块，负责内容导入、解析和管理
- recommendation: NEXT功能模块，负责书籍推荐
- knowledge: RECALL功能模块，负责知识回忆和检索
- analytics: REPORT功能模块，负责数据分析和报告生成
"""

from .app_core import AppCore

__all__ = ['AppCore']
