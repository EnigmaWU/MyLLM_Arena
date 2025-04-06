"""
插件系统

提供可扩展的插件架构，支持第三方功能集成。
"""

from .base import Plugin, ContentProcessorPlugin
from .manager import PluginManager

__all__ = ['Plugin', 'ContentProcessorPlugin', 'PluginManager']
