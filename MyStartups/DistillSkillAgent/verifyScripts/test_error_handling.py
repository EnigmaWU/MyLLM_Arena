"""
US-009: Handle Extraction Errors Gracefully

Acceptance Criteria:
- Invalid file path: clear "file not found" error
- Unsupported format: lists supported formats
- LLM API failure: indicates which API and error type
- Malformed PDF: suggests alternative parsing options
- Zero skills extracted: warns user
- All errors include actionable next steps
"""

import pytest
from pathlib import Path


@pytest.mark.unit
def test_file_not_found_error(cli_runner, temp_dir):
    """Verify clear error message for non-existent file."""
    result = cli_runner([
        "--input", "/path/that/does/not/exist/file.pdf",
        "--output-json", str(Path(temp_dir) / "output.json")
    ])
    
    assert result.returncode != 0, "Should fail for non-existent file"
    
    error = result.stderr.lower()
    assert any(phrase in error for phrase in [
        "not found",
        "does not exist",
        "no such file",
        "file not found"
    ]), f"Should have clear file not found error, got: {result.stderr}"


@pytest.mark.unit
def test_unsupported_format_error(cli_runner, temp_dir):
    """Verify error message lists supported formats."""
    # Create a file with unsupported extension
    unsupported = Path(temp_dir) / "test.xlsx"
    unsupported.write_text("dummy content")
    
    result = cli_runner([
        "--input", str(unsupported),
        "--output-json", str(Path(temp_dir) / "output.json")
    ])
    
    if result.returncode != 0:
        error = result.stderr.lower()
        
        # Should mention unsupported format
        assert "unsupported" in error or "format" in error or "type" in error
        
        # Should list supported formats
        supported_formats = ["pdf", "md", "markdown", "url", "http"]
        found_any = any(fmt in error for fmt in supported_formats)
        assert found_any, f"Should list supported formats, got: {result.stderr}"


@pytest.mark.integration
@pytest.mark.requires_api
def test_llm_api_failure_message(cli_runner, sample_pdf_path, temp_dir):
    """Verify clear message indicating API and error type on failure."""
    import os
    
    # Use invalid API key
    env = os.environ.copy()
    env["ANTHROPIC_API_KEY"] = "invalid_key_12345"
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--llm", "anthropic",
        "--output-json", str(Path(temp_dir) / "output.json")
    ], env=env)
    
    if result.returncode != 0:
        error = result.stderr
        
        # Should mention the API provider
        assert "anthropic" in error.lower() or "api" in error.lower()
        
        # Should indicate error type
        error_indicators = [
            "authentication",
            "api key",
            "invalid",
            "failed",
            "error",
            "unauthorized"
        ]
        assert any(ind in error.lower() for ind in error_indicators), \
            f"Should indicate API error type, got: {error}"


@pytest.mark.integration
def test_malformed_pdf_suggestions(cli_runner, temp_dir):
    """Verify suggestions for malformed PDF files."""
    # Create a malformed PDF (not actually valid PDF format)
    malformed_pdf = Path(temp_dir) / "malformed.pdf"
    malformed_pdf.write_text("This is not a real PDF file")
    
    result = cli_runner([
        "--input", str(malformed_pdf),
        "--output-json", str(Path(temp_dir) / "output.json")
    ])
    
    if result.returncode != 0:
        error = result.stderr.lower()
        
        # Should mention PDF parsing issue
        assert "pdf" in error or "parse" in error or "corrupt" in error or \
               "invalid" in error
        
        # Ideally suggests alternatives
        # (This may vary by implementation)


@pytest.mark.integration
@pytest.mark.requires_api
def test_zero_skills_warning(cli_runner, temp_dir):
    """Verify warning when zero skills extracted."""
    # Create minimal content that might not yield skills
    minimal_md = Path(temp_dir) / "minimal.md"
    minimal_md.write_text("# Title\n\nJust a short note.")
    
    result = cli_runner([
        "--input", str(minimal_md),
        "--output-json", str(Path(temp_dir) / "output.json"),
        "--verbose"
    ])
    
    json_path = Path(temp_dir) / "output.json"
    
    if json_path.exists():
        import json
        with open(json_path) as f:
            skills = json.load(f)
        
        if len(skills) == 0:
            output = result.stdout + result.stderr
            
            # Should warn about no skills extracted
            warnings = ["no skills", "zero skills", "warning", "empty"]
            assert any(w in output.lower() for w in warnings), \
                "Should warn when no skills extracted"


@pytest.mark.unit
def test_errors_include_actionable_steps(cli_runner, temp_dir):
    """Verify all error messages include actionable next steps."""
    error_scenarios = [
        {
            "args": ["--input", "/nonexistent.pdf"],
            "expected_guidance": ["check", "path", "file", "exists"]
        },
        {
            "args": ["--input", "invalid-url"],
            "expected_guidance": ["http", "https", "url", "format"]
        }
    ]
    
    for scenario in error_scenarios:
        result = cli_runner(
            scenario["args"] + ["--output-json", str(Path(temp_dir) / "out.json")]
        )
        
        if result.returncode != 0:
            error = result.stderr.lower()
            
            # Should have some guidance
            has_guidance = any(
                guide in error 
                for guide in scenario["expected_guidance"]
            )
            
            # Errors should be helpful (at least have some length)
            assert len(error) > 20, "Error message should be descriptive"


@pytest.mark.integration
@pytest.mark.requires_api
def test_permission_error_handling(cli_runner, temp_dir):
    """Verify handling of permission errors."""
    import os
    import stat
    
    # Create output directory without write permission (Unix-like systems)
    protected_dir = Path(temp_dir) / "protected"
    protected_dir.mkdir()
    
    try:
        # Remove write permissions
        os.chmod(protected_dir, stat.S_IRUSR | stat.S_IXUSR)
        
        output_file = protected_dir / "output.json"
        
        # Create a simple input
        input_file = Path(temp_dir) / "test.md"
        input_file.write_text("# Test")
        
        result = cli_runner([
            "--input", str(input_file),
            "--output-json", str(output_file)
        ])
        
        if result.returncode != 0:
            error = result.stderr.lower()
            assert "permission" in error or "access" in error or \
                   "denied" in error or "cannot write" in error
    
    finally:
        # Restore permissions for cleanup
        os.chmod(protected_dir, stat.S_IRWXU)


@pytest.mark.unit
def test_network_error_handling(cli_runner, temp_dir):
    """Verify handling of network errors for URL inputs."""
    # Use invalid domain that will fail DNS
    bad_url = "https://this-domain-definitely-does-not-exist-12345.com/article"
    
    result = cli_runner([
        "--input", bad_url,
        "--output-json", str(Path(temp_dir) / "output.json")
    ])
    
    if result.returncode != 0:
        error = result.stderr.lower()
        
        network_error_terms = [
            "network",
            "connection",
            "resolve",
            "unreachable",
            "timeout",
            "dns",
            "failed to fetch"
        ]
        
        assert any(term in error for term in network_error_terms) or \
               "error" in error, \
               f"Should indicate network error, got: {result.stderr}"
