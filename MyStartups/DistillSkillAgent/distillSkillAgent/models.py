"""
Data models for myDistillSkillAgent
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import json


@dataclass
class Step:
    """Represents a single step in a skill execution process."""
    order: int
    action: str
    reasoning: str  # ReACT style reasoning
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Context:
    """Represents when/where a skill should be applied."""
    description: str
    conditions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SkillDescriptor:
    """
    Intermediate representation of an extracted skill.
    Serves as the unified format between parsing and output generation.
    """
    name: str
    description: str
    what: str  # Task description
    why: str  # Purpose & rationale
    how: List[Step]  # Execution steps
    when: List[str]  # Applicable scenarios/contexts
    examples: List[str]  # Code/text examples
    constraints: List[str]  # Preconditions/warnings
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "what": self.what,
            "why": self.why,
            "how": [step.to_dict() if isinstance(step, Step) else step for step in self.how],
            "when": self.when,
            "examples": self.examples,
            "constraints": self.constraints
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillDescriptor":
        """Create SkillDescriptor from dictionary."""
        # Convert steps if they're dicts
        how_data = data.get("how", [])
        steps = []
        for step in how_data:
            if isinstance(step, dict):
                steps.append(Step(**step))
            elif isinstance(step, Step):
                steps.append(step)
        
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            what=data.get("what", ""),
            why=data.get("why", ""),
            how=steps,
            when=data.get("when", []),
            examples=data.get("examples", []),
            constraints=data.get("constraints", [])
        )
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class Section:
    """Represents a section in a document."""
    title: str
    content: str
    level: int  # Heading level (1-6)
    subsections: List["Section"] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "content": self.content,
            "level": self.level,
            "subsections": [s.to_dict() for s in self.subsections]
        }


@dataclass
class Document:
    """
    Represents a parsed document from any source.
    Contains both raw content and structured sections.
    """
    content: str
    structure: List[Section]  # Hierarchical sections
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_type: str = "unknown"  # pdf, markdown, web
    source_path: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content[:500] + "..." if len(self.content) > 500 else self.content,
            "structure": [s.to_dict() for s in self.structure],
            "metadata": self.metadata,
            "source_type": self.source_type,
            "source_path": self.source_path
        }


@dataclass
class SkillCandidate:
    """
    Intermediate representation during skill extraction.
    Used in Pass 1 of the distillation process.
    """
    name: str
    description: str
    source_section: str
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
