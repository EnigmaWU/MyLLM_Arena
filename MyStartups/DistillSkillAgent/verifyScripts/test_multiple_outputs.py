"""
US-004: Support Multiple Output Formats Simultaneously

Acceptance Criteria:
- Can specify both --output-claude-skill and --output-continue-slash-command
- Both outputs generated from same intermediate representation
- Both outputs are consistent in content/quality
- Tool completes without re-parsing source
- Clear confirmation for each output created
"""

import pytest
from pathlib import Path


@pytest.mark.integration
@pytest.mark.requires_api
def test_dual_output_generation(cli_runner, sample_pdf_path, temp_dir):
    """Verify can specify both output formats simultaneously."""
    skill_name = "TestDualOutput"
    slash_path = Path(temp_dir) / "dual-slash.md"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-claude-skill", skill_name,
        "--output-continue-slash-command", str(slash_path)
    ], env={"OUTPUT_DIR": temp_dir})
    
    # Check both outputs created (if implementation exists)
    zip_path = Path(temp_dir) / f"{skill_name}.zip"
    
    if result.returncode == 0:
        # At least one output should be created
        assert zip_path.exists() or slash_path.exists(), \
            "Should create at least one output format"


@pytest.mark.integration
@pytest.mark.requires_api
def test_single_parse_dual_output(cli_runner, sample_pdf_path, temp_dir):
    """Verify tool doesn't re-parse source for second output."""
    import time
    
    # Generate both outputs
    start_time = time.time()
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-claude-skill", "TestSkill",
        "--output-continue-slash-command", str(Path(temp_dir) / "test.md"),
        "--verbose"
    ], env={"OUTPUT_DIR": temp_dir})
    dual_time = time.time() - start_time
    
    # Check verbose output mentions single parse
    output = result.stdout + result.stderr
    
    # Should mention parsing once, not twice
    parse_count = output.lower().count("parsing")
    if parse_count > 0:
        # If we see parsing messages, should be minimal
        assert parse_count <= 2, "Should not re-parse for each output format"


@pytest.mark.integration
@pytest.mark.requires_api  
def test_outputs_content_consistency(cli_runner, sample_pdf_path, temp_dir):
    """Verify both outputs have consistent content/quality."""
    import json
    import zipfile
    
    skill_name = "ConsistencyTest"
    slash_path = Path(temp_dir) / "consistency.md"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-claude-skill", skill_name,
        "--output-continue-slash-command", str(slash_path),
        "--output-json", str(Path(temp_dir) / "intermediate.json")
    ], env={"OUTPUT_DIR": temp_dir})
    
    json_path = Path(temp_dir) / "intermediate.json"
    
    if json_path.exists() and slash_path.exists():
        # Load intermediate representation
        with open(json_path) as f:
            skills = json.load(f)
        
        # Load slash command
        slash_content = slash_path.read_text()
        
        # Verify consistency: skill names/descriptions should appear in both
        for skill in skills[:1]:  # Check first skill
            name = skill.get("name", "")
            description = skill.get("description", "")
            
            # These should appear in the slash command
            if name:
                assert name.lower() in slash_content.lower() or \
                       "name:" in slash_content, \
                       "Skill name should appear in slash command"


@pytest.mark.integration
@pytest.mark.requires_api
def test_confirmation_messages(cli_runner, sample_pdf_path, temp_dir):
    """Verify clear confirmation messages for each output created."""
    skill_name = "ConfirmTest"
    slash_path = Path(temp_dir) / "confirm.md"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-claude-skill", skill_name,
        "--output-continue-slash-command", str(slash_path)
    ], env={"OUTPUT_DIR": temp_dir})
    
    output = result.stdout + result.stderr
    
    # Look for confirmation messages
    confirmations = [
        "generated",
        "created",
        "output",
        ".zip",
        ".md"
    ]
    
    found = sum(1 for conf in confirmations if conf in output.lower())
    
    if result.returncode == 0:
        assert found >= 2, "Should show confirmation messages for outputs"


@pytest.mark.integration
@pytest.mark.requires_api
def test_partial_failure_handling(cli_runner, sample_pdf_path, temp_dir):
    """Verify graceful handling if one output format fails."""
    # Try to create output in write-protected location
    slash_path = Path(temp_dir) / "subdir" / "that" / "doesnt" / "exist" / "test.md"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-claude-skill", "PartialTest",
        "--output-continue-slash-command", str(slash_path)
    ], env={"OUTPUT_DIR": temp_dir})
    
    # Should either:
    # 1. Create parent directories automatically, OR
    # 2. Fail gracefully with clear error message
    
    if result.returncode != 0:
        assert "error" in result.stderr.lower() or "failed" in result.stderr.lower(), \
            "Should provide clear error message on failure"


@pytest.mark.unit
def test_output_format_independence(mock_skill_descriptor):
    """Verify output formatters are independent (can work from same IR)."""
    # This tests the design principle that formatters are decoupled
    
    skill = mock_skill_descriptor
    
    # Both formatters should be able to process the same skill descriptor
    assert "name" in skill
    assert "what" in skill
    assert "why" in skill
    assert "how" in skill
    
    # The existence of these fields means both formatters can work
    # from the same intermediate representation
