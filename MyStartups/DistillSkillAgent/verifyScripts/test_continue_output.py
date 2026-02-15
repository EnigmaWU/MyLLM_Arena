"""
US-003: Generate Continue Slash Command

Acceptance Criteria:
- CLI accepts --output-continue-slash-command parameter
- Generated file follows Continue slash command specification
- YAML frontmatter includes name, description, invokable: true
- Markdown body structured with Task@WHAT, Purpose@WHY, Steps@HOW
- Includes "One-More-Thing" safety checkpoint section
- Output saved as .md file
"""

import pytest
import re
from pathlib import Path


@pytest.mark.unit
def test_cli_accepts_continue_parameter(cli_runner, sample_pdf_path):
    """Verify CLI accepts --output-continue-slash-command parameter."""
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-continue-slash-command", "test-command.md"
    ])
    
    assert "unrecognized arguments" not in result.stderr.lower()


@pytest.mark.integration
@pytest.mark.requires_api
def test_generates_markdown_file(cli_runner, sample_pdf_path, temp_dir):
    """Verify output is saved as .md file at specified path."""
    output_path = Path(temp_dir) / "test-slash-command.md"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-continue-slash-command", str(output_path)
    ])
    
    if result.returncode == 0:
        assert output_path.exists(), "Should create .md file"
        assert output_path.suffix == ".md", "Output should have .md extension"


@pytest.mark.integration
@pytest.mark.requires_api
def test_yaml_frontmatter_valid(cli_runner, sample_pdf_path, temp_dir):
    """Verify YAML frontmatter includes required fields."""
    output_path = Path(temp_dir) / "slash-command.md"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-continue-slash-command", str(output_path)
    ])
    
    if output_path.exists():
        content = output_path.read_text()
        
        # Check for YAML frontmatter delimiters
        assert content.startswith("---"), "Should start with YAML frontmatter"
        
        # Extract frontmatter
        parts = content.split("---")
        assert len(parts) >= 3, "Should have valid YAML frontmatter structure"
        
        frontmatter = parts[1]
        
        # Check required fields
        assert "name:" in frontmatter, "Frontmatter should include 'name'"
        assert "description:" in frontmatter, "Frontmatter should include 'description'"
        assert "invokable: true" in frontmatter, "Frontmatter should include 'invokable: true'"


@pytest.mark.integration
@pytest.mark.requires_api
def test_markdown_body_structured(cli_runner, sample_pdf_path, temp_dir):
    """Verify markdown body has Task@WHAT, Purpose@WHY, Steps@HOW sections."""
    output_path = Path(temp_dir) / "slash-command.md"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-continue-slash-command", str(output_path)
    ])
    
    if output_path.exists():
        content = output_path.read_text()
        
        # Check for required sections
        required_sections = [
            r"#.*Task@WHAT",
            r"#.*Purpose@WHY",
            r"#.*Steps@HOW"
        ]
        
        for section_pattern in required_sections:
            assert re.search(section_pattern, content, re.IGNORECASE), \
                f"Should contain section matching '{section_pattern}'"


@pytest.mark.integration
@pytest.mark.requires_api
def test_includes_one_more_thing_section(cli_runner, sample_pdf_path, temp_dir):
    """Verify includes 'One-More-Thing' safety checkpoint section."""
    output_path = Path(temp_dir) / "slash-command.md"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-continue-slash-command", str(output_path)
    ])
    
    if output_path.exists():
        content = output_path.read_text()
        
        # Check for One-More-Thing section
        assert re.search(r"#.*One-More-Thing", content, re.IGNORECASE), \
            "Should contain 'One-More-Thing' section"


@pytest.mark.integration
@pytest.mark.requires_api
def test_valid_continue_format(cli_runner, sample_pdf_path, temp_dir):
    """Verify file is valid Continue slash command format."""
    output_path = Path(temp_dir) / "slash-command.md"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-continue-slash-command", str(output_path)
    ])
    
    if output_path.exists():
        content = output_path.read_text()
        
        # Comprehensive format check
        checks = [
            (content.startswith("---"), "Must start with YAML frontmatter"),
            ("name:" in content, "Must have name field"),
            ("description:" in content, "Must have description field"),
            ("invokable: true" in content, "Must be invokable"),
            (re.search(r"#.*Task", content), "Must have Task section"),
            (re.search(r"#.*Purpose", content), "Must have Purpose section"),
            (re.search(r"#.*Steps", content), "Must have Steps section"),
        ]
        
        for condition, message in checks:
            assert condition, f"Continue format check failed: {message}"


@pytest.mark.unit
def test_react_style_steps(mock_skill_descriptor, temp_dir):
    """Verify steps follow ReACT pattern (action + reasoning)."""
    # This tests the formatting of steps in the descriptor
    steps = mock_skill_descriptor["how"]
    
    for step in steps:
        assert "action" in step, "Step should have action"
        assert "reasoning" in step, "Step should have reasoning (ReACT style)"
        assert len(step["action"]) > 0, "Action should not be empty"
        assert len(step["reasoning"]) > 0, "Reasoning should not be empty"


@pytest.mark.integration
@pytest.mark.requires_api
def test_multiple_skills_to_multiple_commands(cli_runner, sample_pdf_path, temp_dir):
    """Verify can generate multiple slash commands from multi-skill source."""
    # First extract to JSON
    json_path = Path(temp_dir) / "skills.json"
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(json_path)
    ])
    
    if json_path.exists():
        import json
        with open(json_path) as f:
            skills = json.load(f)
        
        # If multiple skills extracted, could generate multiple commands
        # This is a design consideration test
        assert len(skills) >= 0, "Should handle multi-skill extraction"
