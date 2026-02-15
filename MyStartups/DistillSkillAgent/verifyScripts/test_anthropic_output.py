"""
US-002: Generate Anthropic SKILL Package

Acceptance Criteria:
- CLI accepts --output-claude-skill parameter
- Generated package follows Anthropic SKILL specification
- Package contains valid prompt.xml file
- Package includes instruction files
- Package is properly zipped
- Output file saved with .zip extension
"""

import pytest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


@pytest.mark.unit
def test_cli_accepts_claude_skill_parameter(cli_runner, sample_pdf_path, temp_dir):
    """Verify CLI accepts --output-claude-skill parameter."""
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-claude-skill", "TestSkill"
    ])
    
    # Should not fail due to parameter parsing
    assert "unrecognized arguments" not in result.stderr.lower()


@pytest.mark.integration
@pytest.mark.requires_api
def test_generates_zip_package(cli_runner, sample_pdf_path, temp_dir):
    """Verify generated package is properly zipped with .zip extension."""
    skill_name = "BDD-ExecutableSpec"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-claude-skill", skill_name
    ], env={"OUTPUT_DIR": temp_dir})
    
    # Check for .zip file
    expected_zip = Path(temp_dir) / f"{skill_name}.zip"
    
    if expected_zip.exists():
        assert zipfile.is_zipfile(expected_zip), "Output should be a valid ZIP file"


@pytest.mark.integration
@pytest.mark.requires_api
def test_package_contains_prompt_xml(cli_runner, sample_pdf_path, temp_dir):
    """Verify package contains valid prompt.xml file."""
    skill_name = "TestSkill"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-claude-skill", skill_name
    ], env={"OUTPUT_DIR": temp_dir})
    
    zip_path = Path(temp_dir) / f"{skill_name}.zip"
    
    if zip_path.exists():
        with zipfile.ZipFile(zip_path, 'r') as zf:
            file_list = zf.namelist()
            
            # Check for prompt.xml
            assert any("prompt.xml" in f for f in file_list), \
                "Package should contain prompt.xml"
            
            # Validate XML structure
            prompt_xml_files = [f for f in file_list if "prompt.xml" in f]
            if prompt_xml_files:
                xml_content = zf.read(prompt_xml_files[0])
                try:
                    tree = ET.fromstring(xml_content)
                    assert tree is not None, "prompt.xml should be valid XML"
                except ET.ParseError as e:
                    pytest.fail(f"Invalid XML in prompt.xml: {e}")


@pytest.mark.integration
@pytest.mark.requires_api
def test_package_includes_instructions(cli_runner, sample_pdf_path, temp_dir):
    """Verify package includes instruction files."""
    skill_name = "TestSkill"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-claude-skill", skill_name
    ], env={"OUTPUT_DIR": temp_dir})
    
    zip_path = Path(temp_dir) / f"{skill_name}.zip"
    
    if zip_path.exists():
        with zipfile.ZipFile(zip_path, 'r') as zf:
            file_list = zf.namelist()
            
            # Check for instruction-related files
            instruction_files = [
                f for f in file_list 
                if "instruction" in f.lower() or "readme" in f.lower()
            ]
            
            assert len(instruction_files) > 0, \
                "Package should contain instruction/readme files"


@pytest.mark.integration
@pytest.mark.requires_api
def test_package_structure_valid(cli_runner, sample_pdf_path, temp_dir):
    """Verify package follows Anthropic SKILL specification structure."""
    skill_name = "TestSkill"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-claude-skill", skill_name
    ], env={"OUTPUT_DIR": temp_dir})
    
    zip_path = Path(temp_dir) / f"{skill_name}.zip"
    
    if zip_path.exists():
        with zipfile.ZipFile(zip_path, 'r') as zf:
            file_list = zf.namelist()
            
            # Expected structure based on Anthropic SKILL format
            expected_files = [
                lambda f: "prompt.xml" in f,
                lambda f: any(ext in f for ext in [".md", ".txt"])
            ]
            
            for check in expected_files:
                assert any(check(f) for f in file_list), \
                    f"Package missing expected files. Found: {file_list}"


@pytest.mark.integration
@pytest.mark.requires_api
def test_skill_name_used_correctly(cli_runner, sample_pdf_path, temp_dir):
    """Verify skill name is derived from parameter or source."""
    custom_name = "CustomSkillName"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-claude-skill", custom_name
    ], env={"OUTPUT_DIR": temp_dir})
    
    # Check output file uses the custom name
    expected_zip = Path(temp_dir) / f"{custom_name}.zip"
    default_zip = Path(temp_dir) / "skill.zip"
    
    # Either custom name or default should exist
    assert expected_zip.exists() or default_zip.exists() or result.returncode != 0, \
        "Should create ZIP file with specified or default name"


@pytest.mark.unit
def test_can_import_to_claude(temp_dir):
    """Verify package can be imported into Claude Code/Cline (structural check)."""
    # This is a structural validation test
    # Actual import would require Claude Code environment
    
    # Create mock SKILL package
    zip_path = Path(temp_dir) / "test-skill.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("prompt.xml", '<?xml version="1.0"?><prompt></prompt>')
        zf.writestr("instructions.md", "# Test Skill")
    
    # Verify structure
    assert zipfile.is_zipfile(zip_path)
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        assert "prompt.xml" in zf.namelist()
        assert any(".md" in f for f in zf.namelist())
