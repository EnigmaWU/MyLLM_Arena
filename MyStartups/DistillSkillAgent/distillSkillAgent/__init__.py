"""
myDistillSkillAgent - AI/LLM Agent for Skill Extraction and Transplantation
"""

__version__ = "0.1.0"
__author__ = "EnigmaWU"

from .models import SkillDescriptor, Document, Step, Context, ChatMessage, ChatSession
from .parsers import SourceParser
from .distiller import SkillDistiller
from .formatters import AnthropicSkillFormatter, ContinueSlashCMDFormatter
from .saveAsSkill import SaveAsSkillCommand, validate_skill_name, DEFAULT_SKILL_NAME

__all__ = [
    "SkillDescriptor",
    "Document",
    "Step",
    "Context",
    "ChatMessage",
    "ChatSession",
    "SourceParser",
    "SkillDistiller",
    "AnthropicSkillFormatter",
    "ContinueSlashCMDFormatter",
    "SaveAsSkillCommand",
    "validate_skill_name",
    "DEFAULT_SKILL_NAME",
]
