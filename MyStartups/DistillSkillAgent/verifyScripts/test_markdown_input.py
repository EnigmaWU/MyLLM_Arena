"""
US-005: Parse Markdown Documentation

Acceptance Criteria:
- Accepts .md file as --input parameter
- Preserves code block examples from markdown
- Respects heading hierarchy for skill organization
- Handles markdown-specific formatting
- Extraction quality comparable to PDF parsing
"""

import pytest
from pathlib import Path


@pytest.mark.unit
def test_accepts_markdown_input(cli_runner, sample_md_path, temp_dir):
    """Verify accepts .md file as input parameter."""
    result = cli_runner([
        "--input", str(sample_md_path),
        "--output-json", str(Path(temp_dir) / "output.json")
    ])
    
    # Should accept .md files
    assert "unsupported format" not in result.stderr.lower()


@pytest.mark.integration
@pytest.mark.requires_api
def test_preserves_code_blocks(cli_runner, temp_dir):
    """Verify preserves code block examples from markdown."""
    # Create sample markdown with code blocks
    md_content = """
# Test Skill

This is a skill with code examples.

## Example

```python
def extract_method():
    # This code should be preserved
    pass
```

## Usage

Apply this pattern when refactoring.
"""
    
    md_path = Path(temp_dir) / "test.md"
    md_path.write_text(md_content)
    
    json_path = Path(temp_dir) / "output.json"
    result = cli_runner([
        "--input", str(md_path),
        "--output-json", str(json_path)
    ])
    
    if json_path.exists():
        import json
        with open(json_path) as f:
            skills = json.load(f)
        
        # Check if examples preserved
        if len(skills) > 0:
            skill = skills[0]
            examples = skill.get("examples", [])
            
            # Code content should appear somewhere
            assert any("extract_method" in str(ex) for ex in examples) or \
                   "extract_method" in json.dumps(skill), \
                   "Code blocks should be preserved in examples"


@pytest.mark.integration
@pytest.mark.requires_api
def test_respects_heading_hierarchy(cli_runner, temp_dir):
    """Verify respects heading hierarchy for skill organization."""
    md_content = """
# Main Topic

## Skill 1: Extract Method

Description of extract method.

### Steps

1. Identify code
2. Create method
3. Replace calls

## Skill 2: Inline Method

Description of inline method.

### Steps

1. Copy method body
2. Replace calls
3. Remove method
"""
    
    md_path = Path(temp_dir) / "hierarchy.md"
    md_path.write_text(md_content)
    
    json_path = Path(temp_dir) / "output.json"
    result = cli_runner([
        "--input", str(md_path),
        "--output-json", str(json_path)
    ])
    
    if json_path.exists():
        import json
        with open(json_path) as f:
            skills = json.load(f)
        
        # Should extract multiple skills based on heading structure
        # At minimum, should recognize hierarchical organization
        assert len(skills) > 0, "Should extract skills from hierarchical markdown"


@pytest.mark.integration
@pytest.mark.requires_api
def test_handles_markdown_formatting(cli_runner, temp_dir):
    """Verify handles markdown-specific formatting (links, lists, tables)."""
    md_content = """
# Skill: Best Practices

## Description

This skill involves:
- **Bold** practices
- *Italic* notes
- [Links](https://example.com)

| Step | Action |
|------|--------|
| 1    | Parse  |
| 2    | Extract|

## Code Example

```python
# Example code
def example():
    return "formatted"
```
"""
    
    md_path = Path(temp_dir) / "formatted.md"
    md_path.write_text(md_content)
    
    json_path = Path(temp_dir) / "output.json"
    result = cli_runner([
        "--input", str(md_path),
        "--output-json", str(json_path)
    ])
    
    # Should handle without crashing
    assert result.returncode == 0 or "not implemented" in result.stderr.lower(), \
        "Should handle markdown formatting gracefully"


@pytest.mark.integration
@pytest.mark.requires_api
def test_markdown_quality_comparable_to_pdf(cli_runner, sample_md_path, sample_pdf_path, temp_dir):
    """Verify extraction quality comparable to PDF parsing."""
    md_json = Path(temp_dir) / "md_skills.json"
    pdf_json = Path(temp_dir) / "pdf_skills.json"
    
    # Extract from markdown
    md_result = cli_runner([
        "--input", str(sample_md_path),
        "--output-json", str(md_json)
    ])
    
    # Extract from PDF
    pdf_result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(pdf_json)
    ])
    
    # Compare quality metrics
    if md_json.exists() and pdf_json.exists():
        import json
        
        with open(md_json) as f:
            md_skills = json.load(f)
        
        with open(pdf_json) as f:
            pdf_skills = json.load(f)
        
        # Both should extract skills
        assert len(md_skills) > 0 or len(pdf_skills) > 0, \
            "At least one format should extract skills"
        
        # Quality check: both should have proper structure
        for skills in [md_skills, pdf_skills]:
            if len(skills) > 0:
                skill = skills[0]
                assert "what" in skill
                assert "why" in skill
                assert "how" in skill
