"""
Distillation Layer - LLM-Powered Skill Extraction
"""

import os
import json
from typing import List, Optional
import re

from .models import Document, SkillDescriptor, Step, SkillCandidate


class SkillDistiller:
    """
    Multi-pass skill extraction using LLM.
    
    Pass 1: Identify candidate skills
    Pass 2: Enrich with context and steps
    Pass 3: Validate and deduplicate
    """
    
    def __init__(self, llm_provider: str = "anthropic", algorithm: str = "simple"):
        """
        Initialize the distiller.
        
        Args:
            llm_provider: One of 'anthropic', 'openai', 'local'
            algorithm: 'simple' (streaming) or 'findActionBook' (hierarchical)
        """
        self.llm_provider = llm_provider
        self.llm_client = self._initialize_llm_client(llm_provider)
        self.algorithm_name = algorithm
        self._init_algorithm()

    def _initialize_llm_client(self, llm_provider: str):
        """
        Initialize and return the LLM client for the requested provider.

        Args:
            llm_provider: One of 'anthropic', 'openai',
                          'mockSrvLLM_Anthropic', 'mockSrvLLM_OpenAI', 'local'

        Returns:
            A client instance compatible with algorithms._call_llm()

        Raises:
            ValueError: When a required API key is missing.
            ImportError: When the required SDK is not installed.
        """
        if llm_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "Missing ANTHROPIC_API_KEY environment variable.\n"
                    "Set it with: export ANTHROPIC_API_KEY=<your-key>"
                )
            try:
                import anthropic
            except ImportError:
                raise ImportError(
                    "anthropic SDK not installed. Install with: pip install anthropic"
                )
            return anthropic.Anthropic(api_key=api_key)

        if llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "Missing OPENAI_API_KEY environment variable.\n"
                    "Set it with: export OPENAI_API_KEY=<your-key>"
                )
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "openai SDK not installed. Install with: pip install openai"
                )
            return openai.OpenAI(api_key=api_key)

        if llm_provider == "mockSrvLLM_Anthropic":
            try:
                import anthropic
            except ImportError:
                raise ImportError(
                    "anthropic SDK not installed. Install with: pip install anthropic"
                )
            return anthropic.Anthropic(
                api_key="mock-key",
                base_url="http://localhost:5002",
            )

        if llm_provider == "mockSrvLLM_OpenAI":
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "openai SDK not installed. Install with: pip install openai"
                )
            return openai.OpenAI(
                api_key="mock-key",
                base_url="http://localhost:5001/v1",
            )

        if llm_provider == "local":
            # Local provider: use OpenAI-compatible client pointing at localhost
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "openai SDK not installed. Install with: pip install openai"
                )
            local_url = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/v1")
            return openai.OpenAI(api_key="local", base_url=local_url)

        raise ValueError(
            f"Unknown LLM provider: '{llm_provider}'. "
            f"Supported providers: anthropic, openai, mockSrvLLM_Anthropic, "
            f"mockSrvLLM_OpenAI, local"
        )

    def _init_algorithm(self):
        from .algorithms import SimpleStreamingAlg, FindActionBookAlg, FindSkillAlgorithm
        
        model_name = "claude-3-5-sonnet-20241022" # Could be parameterized
        
        if self.algorithm_name == "findActionBook":
            self.strategy = FindActionBookAlg(self.llm_client, model_name)
        else:
            self.strategy = SimpleStreamingAlg(self.llm_client, model_name)
    
    def distill(self, document: Document, verbose: bool = False) -> List[SkillDescriptor]:
        """
        Extract skills from a document using the configured algorithm.
        """
        if verbose:
            print(f"Distilling skills from {document.source_type} using {self.algorithm_name} algorithm...")
        
        # Pass 1: Identify
        if verbose:
            print("Phase 1: Identifying candidate skills...")
        candidates = self.strategy.identify_candidates(document)
        if verbose:
            print(f"  Found {len(candidates)} candidates")
            
        # Pass 2: Synthesize
        if verbose:
            print("Phase 2: Synthesizing skills...")
        skills = self.strategy.synthesize_skills(candidates, document)
        if verbose:
            print(f"  Synthesized {len(skills)} skills")
            
        # Pass 3: Validate (Common logic)
        validated = self.validate_skills(skills)
        if verbose:
            print(f"  Final: {len(validated)} validated skills")
            
        return validated
    
    # identify_skills, _chunk_document, _extract_candidates_from_chunk, enrich_skill 
    # and _chunk_document, _extract_candidates_from_chunk, enrich_skill 
    # have been moved to algorithms.py (SimpleStreamingAlg)

    
    def validate_skills(self, skills: List[SkillDescriptor]) -> List[SkillDescriptor]:
        """
        Pass 3: Validate and deduplicate skills.
        """
        if not skills:
            return []
        
        # Deduplicate by name
        seen_names = set()
        unique_skills = []
        
        for skill in skills:
            if skill.name not in seen_names:
                seen_names.add(skill.name)
                unique_skills.append(skill)
        
        # Validate that each skill has minimum required fields
        validated = []
        for skill in unique_skills:
            if (skill.name and skill.description and skill.what and 
                skill.why and len(skill.how) > 0):
                validated.append(skill)
        
        return validated
    
    # _call_llm, _parse_candidates_response, _parse_skill_response
    # have been moved to algorithms.py

