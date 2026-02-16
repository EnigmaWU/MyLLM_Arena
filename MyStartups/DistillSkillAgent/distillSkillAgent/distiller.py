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
    
    def __init__(self, llm_provider: str = "anthropic"):
        """
        Initialize the distiller with specified LLM provider.
        
        Args:
            llm_provider: One of 'anthropic', 'openai', 'local'
        """
        self.llm_provider = llm_provider
        self.llm_client = self._initialize_llm_client(llm_provider)
    
    def _initialize_llm_client(self, provider: str):
        """Initialize LLM client based on provider."""
        if provider == "anthropic":
            try:
                import anthropic
            except ImportError:
                raise ImportError(
                    "Anthropic client not installed. "
                    "Install with: pip install anthropic"
                )
            
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY environment variable not set.\n"
                    "Set it with: export ANTHROPIC_API_KEY='your-key'"
                )
            
            return anthropic.Anthropic(api_key=api_key)

        elif provider == "mockSrvLLM_Anthropic":
            try:
                import anthropic
            except ImportError:
                raise ImportError(
                    "Anthropic client not installed. "
                    "Install with: pip install anthropic"
                )
            
            base_url = os.getenv("MOCK_LLM_ANTHROPIC_BASE_URL", "http://localhost:5002")
            api_key = "mock"
            return anthropic.Anthropic(base_url=base_url, api_key=api_key)
        
        elif provider == "openai":
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "OpenAI client not installed. "
                    "Install with: pip install openai"
                )
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY environment variable not set.\n"
                    "Set it with: export OPENAI_API_KEY='your-key'"
                )
            
            return openai.OpenAI(api_key=api_key)

        elif provider == "mockSrvLLM_OpenAI":
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "OpenAI client not installed (required for mock server client). "
                    "Install with: pip install openai"
                )
            
            base_url = os.getenv("MOCK_LLM_OPENAI_BASE_URL", "http://localhost:5001/v1")
            api_key = "mock"
            return openai.OpenAI(base_url=base_url, api_key=api_key)
        
        elif provider == "local":
            # Placeholder for local model support
            return None
        
        else:
            raise ValueError(
                f"Invalid LLM provider: {provider}\n"
                f"Supported providers: anthropic, openai, mockSrvLLM_OpenAI, mockSrvLLM_Anthropic, local"
            )
    
    def distill(self, document: Document, verbose: bool = False) -> List[SkillDescriptor]:
        """
        Extract skills from a document using multi-pass approach.
        
        Args:
            document: Parsed document
            verbose: Print progress messages
            
        Returns:
            List of extracted SkillDescriptor objects
        """
        if verbose:
            print(f"Distilling skills from {document.source_type} document...")
        
        # Pass 1: Identify candidate skills
        if verbose:
            print("Pass 1: Identifying candidate skills...")
        candidates = self.identify_skills(document)
        if verbose:
            print(f"  Found {len(candidates)} candidate skills")
        
        # Pass 2: Enrich with context and steps
        if verbose:
            print("Pass 2: Enriching with context and steps...")
        skills = []
        for i, candidate in enumerate(candidates):
            if verbose and (i + 1) % 5 == 0:
                print(f"  Enriched {i + 1}/{len(candidates)} skills...")
            skill = self.enrich_skill(candidate, document)
            if skill:
                skills.append(skill)
        
        # Pass 3: Validate and deduplicate
        if verbose:
            print("Pass 3: Validating and deduplicating...")
        validated_skills = self.validate_skills(skills)
        if verbose:
            print(f"  Final: {len(validated_skills)} validated skills")
        
        return validated_skills
    
    def identify_skills(self, document: Document) -> List[SkillCandidate]:
        """
        Pass 1: Identify candidate skills from document.
        """
        # Chunk document into manageable sections
        chunks = self._chunk_document(document)
        
        candidates = []
        for chunk in chunks:
            chunk_candidates = self._extract_candidates_from_chunk(chunk)
            candidates.extend(chunk_candidates)
        
        return candidates
    
    def _chunk_document(self, document: Document) -> List[str]:
        """Chunk document into semantic sections."""
        chunks = []
        
        # Use document structure if available
        if document.structure:
            for section in document.structure:
                if len(section.content) > 100:  # Skip very short sections
                    chunk = f"# {section.title}\n\n{section.content}"
                    chunks.append(chunk)
        
        # Fallback: split by length if no structure
        if not chunks:
            content = document.content
            chunk_size = 3000
            for i in range(0, len(content), chunk_size):
                chunks.append(content[i:i + chunk_size])
        
        return chunks
    
    def _extract_candidates_from_chunk(self, chunk: str) -> List[SkillCandidate]:
        """Extract skill candidates from a chunk using LLM."""
        prompt = f"""Analyze the following text and identify actionable skills, patterns, or best practices that could be codified.

For each skill, provide:
1. A concise name (kebab-case)
2. A brief description (1 sentence)

Return ONLY a JSON array of skills, no other text:
[
  {{"name": "skill-name", "description": "Brief description"}},
  ...
]

Text to analyze:
{chunk[:2000]}
"""
        
        try:
            response = self._call_llm(prompt)
            candidates = self._parse_candidates_response(response, chunk)
            return candidates
        except Exception as e:
            print(f"Warning: Failed to extract candidates from chunk: {e}")
            return []
    
    def enrich_skill(self, candidate: SkillCandidate, document: Document) -> Optional[SkillDescriptor]:
        """
        Pass 2: Enrich candidate with full WHAT/WHY/HOW structure.
        """
        prompt = f"""For the skill "{candidate.name}" ({candidate.description}), create a complete skill specification.

Context from source:
{candidate.source_section[:1500]}

Provide a JSON object with these fields:
{{
  "name": "{candidate.name}",
  "description": "Detailed description",
  "what": "What task does this skill accomplish?",
  "why": "Why is this skill useful/important?",
  "how": [
    {{"order": 1, "action": "First step action", "reasoning": "Why this step is needed"}},
    {{"order": 2, "action": "Second step action", "reasoning": "Why this step is needed"}}
  ],
  "when": ["Context 1 where skill applies", "Context 2..."],
  "examples": ["Example 1", "Example 2"],
  "constraints": ["Precondition 1", "Warning 1"]
}}

Return ONLY valid JSON, no other text:
"""
        
        try:
            response = self._call_llm(prompt)
            skill = self._parse_skill_response(response)
            return skill
        except Exception as e:
            print(f"Warning: Failed to enrich skill {candidate.name}: {e}")
            return None
    
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
    
    def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM with a prompt."""
        if self.llm_provider == "anthropic" or self.llm_provider == "mockSrvLLM_Anthropic":
            response = self.llm_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        elif self.llm_provider == "openai" or self.llm_provider == "mockSrvLLM_OpenAI":
            model = "gpt-4" if self.llm_provider == "openai" else "gpt-4-mock"
            response = self.llm_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000
            )
            return response.choices[0].message.content
        
        else:
            # Local model fallback
            raise NotImplementedError("Local model support not yet implemented")
    
    def _parse_candidates_response(self, response: str, source_chunk: str) -> List[SkillCandidate]:
        """Parse LLM response into SkillCandidates."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
            else:
                data = json.loads(response)
            
            candidates = []
            for item in data:
                if isinstance(item, dict) and "name" in item:
                    candidates.append(SkillCandidate(
                        name=item["name"],
                        description=item.get("description", ""),
                        source_section=source_chunk,
                        confidence=0.8
                    ))
            
            return candidates
        
        except json.JSONDecodeError:
            print(f"Warning: Failed to parse JSON from LLM response")
            return []
    
    def _parse_skill_response(self, response: str) -> Optional[SkillDescriptor]:
        """Parse LLM response into SkillDescriptor."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
            else:
                data = json.loads(response)
            
            # Convert how steps
            steps = []
            for step_data in data.get("how", []):
                steps.append(Step(
                    order=step_data.get("order", 0),
                    action=step_data.get("action", ""),
                    reasoning=step_data.get("reasoning", "")
                ))
            
            return SkillDescriptor(
                name=data.get("name", ""),
                description=data.get("description", ""),
                what=data.get("what", ""),
                why=data.get("why", ""),
                how=steps,
                when=data.get("when", []),
                examples=data.get("examples", []),
                constraints=data.get("constraints", [])
            )
        
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to parse skill JSON: {e}")
            return None
