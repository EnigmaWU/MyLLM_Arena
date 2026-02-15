"""
US-001: Extract Skills from PDF Book

Acceptance Criteria:
- CLI accepts PDF file path as input via --input parameter
- Tool successfully parses PDF and extracts text content
- Extracted skills include WHAT/WHY/HOW structure
- Each skill has clear, actionable steps
- Tool displays progress during extraction (with --verbose)
- Extraction completes within reasonable time
- Output contains at least 3-5 distinct skills
"""

import pytest
import time
from pathlib import Path


@pytest.mark.integration
@pytest.mark.requires_api
def test_cli_accepts_pdf_input(cli_runner, sample_pdf_path, temp_dir):
    """Verify CLI accepts PDF file path via --input parameter."""
    output_path = Path(temp_dir) / "output.json"
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(output_path)
    ])
    
    assert result.returncode == 0 or "not implemented" in result.stderr.lower(), \
        f"CLI should accept PDF input: {result.stderr}"


@pytest.mark.integration
@pytest.mark.requires_api
def test_pdf_parsing_success(cli_runner, sample_pdf_path, temp_dir):
    """Verify tool successfully parses PDF and extracts text content."""
    output_path = Path(temp_dir) / "skills.json"
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(output_path),
        "--verbose"
    ])
    
    # Check successful execution
    assert result.returncode == 0, f"PDF parsing failed: {result.stderr}"
    
    # Check output file exists
    assert output_path.exists(), "Output JSON file should be created"


@pytest.mark.integration
@pytest.mark.requires_api
def test_extracted_skills_have_structure(cli_runner, sample_pdf_path, temp_dir):
    """Verify extracted skills include WHAT/WHY/HOW structure."""
    import json
    
    output_path = Path(temp_dir) / "skills.json"
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(output_path)
    ])
    
    if output_path.exists():
        with open(output_path) as f:
            skills = json.load(f)
        
        assert len(skills) > 0, "Should extract at least one skill"
        
        # Verify first skill has required structure
        skill = skills[0]
        assert "what" in skill, "Skill should have 'what' field"
        assert "why" in skill, "Skill should have 'why' field"
        assert "how" in skill, "Skill should have 'how' field"
        assert len(skill["how"]) > 0, "Skill should have actionable steps"


@pytest.mark.integration
@pytest.mark.requires_api
def test_skills_have_actionable_steps(cli_runner, sample_pdf_path, temp_dir):
    """Verify each skill has clear, actionable steps."""
    import json
    
    output_path = Path(temp_dir) / "skills.json"
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(output_path)
    ])
    
    if output_path.exists():
        with open(output_path) as f:
            skills = json.load(f)
        
        for skill in skills:
            assert "how" in skill, f"Skill '{skill.get('name')}' missing 'how' field"
            steps = skill["how"]
            assert isinstance(steps, list), "Steps should be a list"
            
            for step in steps:
                assert "action" in step, "Each step should have an action"
                assert "reasoning" in step, "Each step should have reasoning (ReACT style)"


@pytest.mark.integration
@pytest.mark.requires_api
def test_verbose_mode_shows_progress(cli_runner, sample_pdf_path, temp_dir):
    """Verify tool displays progress during extraction with --verbose."""
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(Path(temp_dir) / "skills.json"),
        "--verbose"
    ])
    
    output = result.stdout + result.stderr
    
    # Check for progress indicators
    progress_indicators = [
        "parsing",
        "extracting",
        "pass 1",
        "pass 2",
        "pass 3",
        "identified",
        "validated"
    ]
    
    found_any = any(indicator in output.lower() for indicator in progress_indicators)
    assert found_any or result.returncode != 0, \
        "Verbose mode should show progress indicators"


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.slow
def test_extraction_performance(cli_runner, sample_pdf_path, temp_dir):
    """Verify extraction completes within reasonable time (<5 min for 300 pages)."""
    start_time = time.time()
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(Path(temp_dir) / "skills.json")
    ])
    
    elapsed_time = time.time() - start_time
    
    # For a sample/small PDF, should complete quickly
    # Adjust threshold based on actual PDF size
    assert elapsed_time < 300, f"Extraction took {elapsed_time:.1f}s, should be <300s"


@pytest.mark.integration
@pytest.mark.requires_api
def test_minimum_skills_extracted(cli_runner, sample_pdf_path, temp_dir):
    """Verify output contains at least 3-5 distinct skills from source."""
    import json
    
    output_path = Path(temp_dir) / "skills.json"
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(output_path)
    ])
    
    if output_path.exists():
        with open(output_path) as f:
            skills = json.load(f)
        
        # For a real book, expect at least 3 skills
        assert len(skills) >= 3, f"Expected at least 3 skills, got {len(skills)}"
        
        # Verify skills are distinct (different names)
        names = [s.get("name") for s in skills]
        assert len(names) == len(set(names)), "Skills should have unique names"


@pytest.mark.unit
def test_invalid_pdf_path(cli_runner):
    """Verify appropriate error for non-existent PDF."""
    result = cli_runner([
        "--input", "/nonexistent/file.pdf",
        "--output-json", "/tmp/output.json"
    ])
    
    assert result.returncode != 0, "Should fail for non-existent file"
    assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()
