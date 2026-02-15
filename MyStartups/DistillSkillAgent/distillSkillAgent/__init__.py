"""
myDistillSkillAgent - AI/LLM Agent for Skill Extraction and Transplantation
"""

__version__ = "0.1.0"
__author__ = "EnigmaWU"

from .models import SkillDescriptor, Document, Step, Context
from .parsers import SourceParser
from .distiller import SkillDistiller
from .formatters import AnthropicSkillFormatter, ContinueSlashCMDFormatter

__all__ = [
    "SkillDescriptor",
    "Document",
    "Step",
    "Context",
    "SourceParser",
    "SkillDistiller",
    "AnthropicSkillFormatter",
    "ContinueSlashCMDFormatter",
]
