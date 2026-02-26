import sys
import os
import json
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from distillSkillAgent.models import Document, Section
from distillSkillAgent.algorithms import FindActionBookAlg

def test_find_action_book_alg():
    print("Testing FindActionBookAlg Logic...")
    
    # 1. Setup Mock Document
    # Structure:
    # - Chapter 1: Theory of Test Skill (Level 1)
    #   - Content: "Test Skill is useful for..."
    # - Chapter 2: Another topic
    # - Chapter 5: Practice of Test Skill (Level 1)
    #   - Content: "Here is how to apply Test Skill in code..."
    
    long_text_padding = " " + "padding " * 100
    sections = [
        Section(title="Chapter 1: Theory", level=1, content="Test Skill (TS) is a method to do X. It is important because Y." + long_text_padding),
        Section(title="Chapter 2: unrelated", level=1, content="Some other stuff." + long_text_padding),
        Section(title="Chapter 5: Practice", level=1, content="To implement Test Skill, follow these steps:\n1. Do A\n2. Do B\nExample code:\nfunc x() {}" + long_text_padding)
    ]
    
    doc = Document(content="...", structure=sections, source_type="pdf")
    
    # 2. Setup Mock LLM Client
    mock_client = MagicMock()
    # Mock response for identify_candidates (Map phase)
    # We expect it to be called for Ch1 and Ch5
    
    # We'll use a side_effect to return different JSONs based on input
    def mock_llm_response(messages, **kwargs):
        content = messages[0]['content']
        if "Chapter 1" in content:
            return MagicMock(content=[MagicMock(text=json.dumps([
                {"name": "test-skill", "description": "A method to do X"}
            ]))])
        elif "Chapter 5" in content:
            return MagicMock(content=[MagicMock(text=json.dumps([
                {"name": "test-skill", "description": "Implementation of TS"}
            ]))])
        elif "Skill Descriptor" in content: # Synthesize phase
            return MagicMock(content=[MagicMock(text=json.dumps({
                "name": "test-skill",
                "description": "Complete skill",
                "what": "Do X",
                "why": "Because Y",
                "how": [{"order": 1, "action": "Do A", "reasoning": "Standard"}],
                "when": ["Always"],
                "examples": ["func x() {}"],
                "constraints": []
            }))])
        else:
            return MagicMock(content=[MagicMock(text="[]")])

    mock_client.messages.create.side_effect = mock_llm_response
    
    # 3. Run Algorithm
    alg = FindActionBookAlg(mock_client)
    
    print("\n1. Identify Candidates...")
    candidates = alg.identify_candidates(doc)
    print(f"Found {len(candidates)} candidates.")
    for c in candidates:
        print(f"  - {c.name}: {c.description}")
        
    print("\n2. Synthesize Skills...")
    skills = alg.synthesize_skills(candidates, doc)
    print(f"Synthesized {len(skills)} skills.")
    
    assert len(skills) == 1
    skill = skills[0]
    print(f"\nFinal Skill: {skill.name}")
    print(f"Description: {skill.description}")
    print(f"How steps: {len(skill.how)}")
    
    if skill.name == "test-skill" and len(skill.how) > 0:
        print("\nSUCCESS: Logic verified.")
    else:
        print("\nFAILURE: Skill not correctly synthesized.")

if __name__ == "__main__":
    test_find_action_book_alg()
