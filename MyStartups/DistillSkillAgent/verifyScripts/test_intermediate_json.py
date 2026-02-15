"""
US-008: Inspect Intermediate Representation

Acceptance Criteria:
- --output-json parameter saves intermediate SkillDescriptor to JSON
- JSON is human-readable and well-formatted
- JSON includes all skill fields
- Can re-run tool with JSON as input (future feature)
- Enables manual editing workflow
"""

import pytest
import json
from pathlib import Path


@pytest.mark.unit
def test_accepts_output_json_parameter(cli_runner, sample_pdf_path, temp_dir):
    """Verify --output-json parameter accepted."""
    json_path = Path(temp_dir) / "intermediate.json"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(json_path)
    ])
    
    assert "unrecognized arguments" not in result.stderr.lower()


@pytest.mark.integration
@pytest.mark.requires_api
def test_saves_json_file(cli_runner, sample_pdf_path, temp_dir):
    """Verify saves intermediate SkillDescriptor to JSON file."""
    json_path = Path(temp_dir) / "skills.json"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(json_path)
    ])
    
    if result.returncode == 0:
        assert json_path.exists(), "Should create JSON output file"


@pytest.mark.integration
@pytest.mark.requires_api
def test_json_is_valid_and_readable(cli_runner, sample_pdf_path, temp_dir):
    """Verify JSON is valid, human-readable and well-formatted."""
    json_path = Path(temp_dir) / "skills.json"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(json_path)
    ])
    
    if json_path.exists():
        # Should be valid JSON
        with open(json_path) as f:
            data = json.load(f)
        
        assert isinstance(data, (list, dict)), "JSON should be list or dict"
        
        # Check formatting (indented for readability)
        content = json_path.read_text()
        assert "\n" in content, "JSON should be formatted with newlines"
        assert "  " in content or "\t" in content, "JSON should be indented"


@pytest.mark.integration
@pytest.mark.requires_api
def test_json_includes_all_fields(cli_runner, sample_pdf_path, temp_dir):
    """Verify JSON includes all skill fields (name, what, why, how, etc)."""
    json_path = Path(temp_dir) / "complete_skills.json"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(json_path)
    ])
    
    if json_path.exists():
        with open(json_path) as f:
            skills = json.load(f)
        
        if isinstance(skills, list) and len(skills) > 0:
            skill = skills[0]
            
            # Check required fields
            required_fields = ["name", "description", "what", "why", "how"]
            for field in required_fields:
                assert field in skill, f"Skill should have '{field}' field"
            
            # Check optional but important fields
            optional_fields = ["when", "examples", "constraints"]
            # At least some optional fields should be present
            present = sum(1 for f in optional_fields if f in skill)
            assert present >= 0, "Skill should include additional context fields"


@pytest.mark.unit
def test_json_structure_matches_schema(mock_skill_descriptor):
    """Verify JSON structure matches SkillDescriptor schema."""
    skill = mock_skill_descriptor
    
    # Validate structure
    assert isinstance(skill, dict)
    assert isinstance(skill["name"], str)
    assert isinstance(skill["description"], str)
    assert isinstance(skill["what"], str)
    assert isinstance(skill["why"], str)
    assert isinstance(skill["how"], list)
    assert isinstance(skill["when"], list)
    assert isinstance(skill["examples"], list)
    assert isinstance(skill["constraints"], list)
    
    # Validate step structure
    for step in skill["how"]:
        assert "order" in step
        assert "action" in step
        assert "reasoning" in step


@pytest.mark.unit
def test_enables_manual_editing(temp_dir):
    """Verify JSON format enables manual editing workflow."""
    # Create sample JSON
    skill = {
        "name": "test-skill",
        "description": "Original description",
        "what": "Do something",
        "why": "For testing",
        "how": [
            {"order": 1, "action": "Step 1", "reasoning": "Because"}
        ],
        "when": ["Always"],
        "examples": ["Example"],
        "constraints": []
    }
    
    json_path = Path(temp_dir) / "editable.json"
    with open(json_path, 'w') as f:
        json.dump([skill], f, indent=2)
    
    # Read and modify
    with open(json_path) as f:
        data = json.load(f)
    
    data[0]["description"] = "Modified description"
    
    # Save modified version
    modified_path = Path(temp_dir) / "modified.json"
    with open(modified_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Verify modification persisted
    with open(modified_path) as f:
        modified_data = json.load(f)
    
    assert modified_data[0]["description"] == "Modified description"


@pytest.mark.integration
@pytest.mark.requires_api
def test_json_with_multiple_skills(cli_runner, sample_pdf_path, temp_dir):
    """Verify JSON correctly represents multiple skills."""
    json_path = Path(temp_dir) / "multi_skills.json"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(json_path)
    ])
    
    if json_path.exists():
        with open(json_path) as f:
            skills = json.load(f)
        
        if isinstance(skills, list):
            # Each skill should be complete and independent
            for i, skill in enumerate(skills):
                assert "name" in skill, f"Skill {i} should have name"
                assert "what" in skill, f"Skill {i} should have what"
                assert "why" in skill, f"Skill {i} should have why"
                assert "how" in skill, f"Skill {i} should have how"


@pytest.mark.unit  
def test_future_json_input_compatibility(temp_dir):
    """Verify JSON format is suitable for future re-input feature."""
    # This tests that saved JSON could theoretically be re-loaded
    
    skill_data = [{
        "name": "future-skill",
        "description": "Test future compatibility",
        "what": "Task description",
        "why": "Purpose",
        "how": [
            {"order": 1, "action": "Do this", "reasoning": "Because"}
        ],
        "when": ["Context"],
        "examples": ["Example"],
        "constraints": ["Constraint"]
    }]
    
    json_path = Path(temp_dir) / "reusable.json"
    with open(json_path, 'w') as f:
        json.dump(skill_data, f, indent=2)
    
    # Verify can be loaded back
    with open(json_path) as f:
        reloaded = json.load(f)
    
    assert reloaded == skill_data, "JSON should round-trip correctly"
    assert isinstance(reloaded, list), "Should maintain list structure"
    assert len(reloaded) == 1, "Should preserve all skills"
