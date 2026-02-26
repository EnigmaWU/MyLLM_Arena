"""
Skill Finding Algorithms
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import re

from .models import Document, SkillCandidate, SkillDescriptor, Step, Section

class FindSkillAlgorithm(ABC):
    """Abstract base class for skill finding algorithms."""
    
    def __init__(self, llm_client, model="claude-3-5-sonnet-20241022"):
        self.llm_client = llm_client
        self.model = model

    @abstractmethod
    def identify_candidates(self, document: Document) -> List[SkillCandidate]:
        """Identify potential skills from the document."""
        pass

    @abstractmethod
    def synthesize_skills(self, candidates: List[SkillCandidate], document: Document) -> List[SkillDescriptor]:
        """Synthesize full skill descriptors from candidates."""
        pass

    def _call_llm(self, prompt: str) -> str:
        """Helper to call LLM (wraps the client)."""
        # This duplicates some logic from distiller.py, but we can refactor later
        # or pass a 'LLMService' object instead of raw client.
        # For now, we assume self.llm_client is an Anthropic or OpenAI client instance
        
        # Check client type loosely
        is_anthropic = hasattr(self.llm_client, 'messages')
        
        if is_anthropic:
            response = self.llm_client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        else:
            # Assume OpenAI-like
            response = self.llm_client.chat.completions.create(
                model="gpt-4", # override needed?
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000
            )
            return response.choices[0].message.content


class SimpleStreamingAlg(FindSkillAlgorithm):
    """
    Original linear chunk-by-chunk distillation.
    Good for unstructured text or short documents.
    """
    
    def identify_candidates(self, document: Document) -> List[SkillCandidate]:
        # Logic moved from original SkillDistiller.identify_skills
        chunks = self._chunk_document(document)
        candidates = []
        for chunk in chunks:
            candidates.extend(self._extract_candidates_from_chunk(chunk))
        return candidates

    def synthesize_skills(self, candidates: List[SkillCandidate], document: Document) -> List[SkillDescriptor]:
        # Logic moved from original SkillDistiller.enrich_skill loop
        skills = []
        for candidate in candidates:
            skill = self._enrich_skill(candidate)
            if skill:
                skills.append(skill)
        return skills

    # ... Include helper methods (_chunk_document, _extract_candidates_from_chunk, _enrich_skill) 
    # adapted from original distiller.py ...
    # For brevity in this initial file creation, I will implement them below.
    
    def _chunk_document(self, document: Document) -> List[str]:
        """Chunk document into semantic sections."""
        chunks = []
        if document.structure:
            for section in document.structure:
                if len(section.content) > 100:
                    chunk = f"# {section.title}\n\n{section.content}"
                    chunks.append(chunk)
        if not chunks:
            content = document.content
            chunk_size = 3000
            for i in range(0, len(content), chunk_size):
                chunks.append(content[i:i + chunk_size])
        return chunks

    def _extract_candidates_from_chunk(self, chunk: str) -> List[SkillCandidate]:
        prompt = f"""Analyze the following text and identify actionable skills...
[Same prompt as original distiller.py]
Text: {chunk[:2000]}"""
        # Simplified for brevity, will copy full prompt in implementation
        prompt = f"""Analyze the following text and identify actionable skills, patterns, or best practices that could be codified.

For each skill, provide:
1. A concise name (kebab-case)
2. A brief description (1 sentence)

Return ONLY a JSON array of skills:
[
  {{"name": "skill-name", "description": "Brief description"}}
]

Text to analyze:
{chunk[:2000]}
"""
        try:
            response = self._call_llm(prompt)
            return self._parse_candidates_response(response, chunk)
        except Exception as e:
            print(f"Warning: Failed to extract candidates: {e}")
            return []

    def _enrich_skill(self, candidate: SkillCandidate) -> Optional[SkillDescriptor]:
        prompt = f"""For the skill "{candidate.name}" ({candidate.description}), create a complete skill specification.

Context from source:
{candidate.source_section[:1500]}

Provide a JSON object with fields: name, description, what, why, how, when, examples, constraints.
Return ONLY valid JSON.
"""
        try:
            response = self._call_llm(prompt)
            return self._parse_skill_response(response)
        except Exception as e:
            print(f"Warning: Failed to enrich skill {candidate.name}: {e}")
            return None

    def _parse_candidates_response(self, response: str, source_chunk: str) -> List[SkillCandidate]:
        try:
            json_str = self._extract_json(response)
            data = json.loads(json_str)
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
        except Exception:
            return []

    def _parse_skill_response(self, response: str) -> Optional[SkillDescriptor]:
        try:
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            steps = [Step(**s) for s in data.get("how", [])]
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
        except Exception:
            return None

    def _extract_json(self, response: str) -> str:
        match = re.search(r'(\[.*\]|\{.*\})', response, re.DOTALL)
        return match.group(0) if match else response


class FindActionBookAlg(FindSkillAlgorithm):
    """
    Hierarchical distillation for 'Action' books.
    Uses Map-Reduce strategy over the book structure.
    """
    
    def identify_candidates(self, document: Document) -> List[SkillCandidate]:
        print("  - FindActionBookAlg: Mapping skills across chapters...")
        
        # 1. Map Phase: Iterate over sections (Chapters)
        # We assume document.structure is well-populated by the enhanced parser
        candidates = []
        
        for section in document.structure:
            if section.level > 2: # Skip too deep levels for discovery
                continue
            
            # Skip short sections (like Front Matter)
            if len(section.content) < 500:
                continue
                
            print(f"    Scanning section: {section.title}...")
            section_candidates = self._scan_section_for_concepts(section)
            candidates.extend(section_candidates)
            
        print(f"  - Found {len(candidates)} raw concept references.")
        return candidates

    def synthesize_skills(self, candidates: List[SkillCandidate], document: Document) -> List[SkillDescriptor]:
        print("  - FindActionBookAlg: Consolidating and synthesizing skills...")
        
        # 2. Combine Phase: Group by concept name/similarity
        # Ideally we use an LLM to cluster, but simple name matching for now
        grouped_candidates = {}
        for cand in candidates:
            key = cand.name.lower() # specific normalization logic can be improved
            if key not in grouped_candidates:
                grouped_candidates[key] = []
            grouped_candidates[key].append(cand)
            
        print(f"  - Consolidated into {len(grouped_candidates)} unique skills.")
        
        # 3. Reduce Phase: Synthesize full skill from aggregated context
        skills = []
        for name_key, group in grouped_candidates.items():
            # Aggregate context
            # We limit total context to avoid Context Window overflow
            # Prefer 'Theory' (early mentions) and 'Example' (code heavy mentions)
            
            combined_context = f"Skill: {group[0].name}\nReferences found in:\n"
            context_text = ""
            
            for cand in group:
                # We can also look up the Section object in document to get MORE context if needed
                # For now using the source_section snippet stored in candidate
                context_text += f"\n--- Source: {cand.source_section[:50]} (approx) ---\n"
                context_text += cand.source_section[:2000] + "\n" # Limit each chunk
                
            if len(context_text) > 20000:
                context_text = context_text[:20000] + "\n...[truncated]..."

            print(f"    Synthesizing: {group[0].name} (from {len(group)} refs)...")
            skill = self._synthesize_single_skill(group[0].name, context_text)
            if skill:
                skills.append(skill)
                
        return skills

    def _scan_section_for_concepts(self, section: Section) -> List[SkillCandidate]:
        prompt = f"""Analyze this book chapter/section for 'Actionable Skills' or 'Practices'.
Section Title: {section.title}

Content Sample:
{section.content[:3000]}

Return JSON array of found skills:
[
  {{"name": "skill-name", "description": "contextual description"}}
]
"""
        try:
            response = self._call_llm(prompt)
            return self._parse_candidates_response(response, section.content)
        except Exception as e:
            print(f"    Warning: Failed to scan section {section.title}: {e}")
            return []

    def _synthesize_single_skill(self, name: str, context: str) -> Optional[SkillDescriptor]:
        prompt = f"""Create a comprehensive Skill Descriptor for "{name}" based on the collected book excerpts below.

You are digesting a "Book" to teach this skill.
Combine the 'Theory' (Why/What) from early chapters with 'Practice' (How/Examples) from later chapters.

Context:
{context}

Provide JSON object (name, description, what, why, how, when, examples, constraints).
The 'how' field should be a detailed step-by-step guide.
"""
        try:
            response = self._call_llm(prompt)
            # Re-use simple parser from base/simple alg
            # Implementation details: we need to make _parse_skill_response reusable or duplicated
            return self._parse_skill_response(response)
        except Exception as e:
            print(f"    Warning: Failed to synthesize {name}: {e}")
            return None

    def _parse_candidates_response(self, response: str, source_chunk: str) -> List[SkillCandidate]:
        # Duplicate from SimpleStreamingAlg for now (or move to Base)
        match = re.search(r'(\[.*\])', response, re.DOTALL)
        if not match: return []
        try:
            data = json.loads(match.group(0))
            return [SkillCandidate(name=i["name"], description=i.get("description", ""), source_section=source_chunk, confidence=0.8) for i in data if "name" in i]
        except: return []

    def _parse_skill_response(self, response: str) -> Optional[SkillDescriptor]:
        # Duplicate from SimpleStreamingAlg for now
        match = re.search(r'(\{.*\})', response, re.DOTALL)
        if not match: return None
        try:
            data = json.loads(match.group(0))
            steps = [Step(**s) for s in data.get("how", [])]
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
        except: return None
