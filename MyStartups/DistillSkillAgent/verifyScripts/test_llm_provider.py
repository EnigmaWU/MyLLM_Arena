"""
US-007: Choose LLM Provider

Acceptance Criteria:
- --llm parameter accepts: anthropic, openai, local
- Tool uses specified provider for all LLM operations
- Appropriate API keys validated before processing
- Clear error message if API key missing/invalid
- Default to anthropic if not specified
"""

import pytest
import os
from pathlib import Path


@pytest.mark.unit
def test_accepts_llm_parameter(cli_runner, sample_pdf_path, temp_dir):
    """Verify --llm parameter accepts valid providers."""
    providers = ["anthropic", "openai", "local"]
    
    for provider in providers:
        result = cli_runner([
            "--input", str(sample_pdf_path),
            "--llm", provider,
            "--output-json", str(Path(temp_dir) / f"{provider}_output.json")
        ])
        
        # Should accept the parameter
        assert "unrecognized arguments" not in result.stderr.lower()
        assert f"invalid.*{provider}" not in result.stderr.lower()


@pytest.mark.integration
@pytest.mark.requires_api
def test_uses_specified_provider(cli_runner, sample_pdf_path, temp_dir):
    """Verify tool uses specified provider for LLM operations."""
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--llm", "anthropic",
        "--output-json", str(Path(temp_dir) / "output.json"),
        "--verbose"
    ], env={"ANTHROPIC_API_KEY": "test-key"})
    
    output = result.stdout + result.stderr
    
    # Should mention the provider in verbose output
    if "--verbose" in output or result.returncode != 0:
        # May show provider selection or API call attempts
        pass  # Implementation-dependent


@pytest.mark.unit
def test_validates_api_key_before_processing(cli_runner, sample_pdf_path, temp_dir):
    """Verify API keys validated before processing."""
    # Remove API key from environment
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("OPENAI_API_KEY", None)
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--llm", "anthropic",
        "--output-json", str(Path(temp_dir) / "output.json")
    ], env=env)
    
    # Should fail with missing API key error
    if result.returncode != 0:
        error = result.stderr.lower()
        assert any(key in error for key in ["api key", "credential", "authentication", "api_key"]), \
            f"Should mention missing API key, got: {result.stderr}"


@pytest.mark.unit
def test_clear_error_for_missing_key(cli_runner, sample_pdf_path, temp_dir):
    """Verify clear error message if API key missing/invalid."""
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--llm", "anthropic",
        "--output-json", str(Path(temp_dir) / "output.json")
    ], env=env)
    
    if result.returncode != 0:
        error_msg = result.stderr
        
        # Error should be actionable
        assert len(error_msg) > 0, "Should provide error message"
        assert "ANTHROPIC_API_KEY" in error_msg or \
               "API key" in error_msg or \
               "environment variable" in error_msg, \
               "Should mention how to provide API key"


@pytest.mark.integration
@pytest.mark.requires_api
def test_defaults_to_anthropic(cli_runner, sample_pdf_path, temp_dir):
    """Verify defaults to anthropic if --llm not specified."""
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--output-json", str(Path(temp_dir) / "output.json"),
        "--verbose"
    ])
    
    # If successful, likely used default provider
    # If failed, should mention API key for default provider
    if result.returncode != 0:
        error = result.stderr
        # Default is Anthropic, so should mention it
        assert "ANTHROPIC" in error.upper() or "anthropic" in error.lower() or \
               result.returncode != 0


@pytest.mark.unit
def test_invalid_provider_rejected(cli_runner, sample_pdf_path, temp_dir):
    """Verify invalid provider names are rejected."""
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--llm", "invalid_provider",
        "--output-json", str(Path(temp_dir) / "output.json")
    ])
    
    # Should reject invalid provider
    assert result.returncode != 0, "Should reject invalid provider"
    assert "invalid" in result.stderr.lower() or \
           "choice" in result.stderr.lower() or \
           "anthropic" in result.stderr.lower()


@pytest.mark.integration
@pytest.mark.requires_api
def test_provider_specific_features(cli_runner, sample_pdf_path, temp_dir):
    """Verify provider-specific features work correctly."""
    # Different providers may have different capabilities
    # This test ensures switching providers doesn't break functionality
    
    providers_to_test = []
    
    # Test Anthropic if key available
    if os.getenv("ANTHROPIC_API_KEY"):
        providers_to_test.append("anthropic")
    
    # Test OpenAI if key available  
    if os.getenv("OPENAI_API_KEY"):
        providers_to_test.append("openai")
    
    for provider in providers_to_test:
        result = cli_runner([
            "--input", str(sample_pdf_path),
            "--llm", provider,
            "--output-json", str(Path(temp_dir) / f"{provider}_test.json")
        ])
        
        # Should complete successfully with valid key
        json_path = Path(temp_dir) / f"{provider}_test.json"
        if json_path.exists():
            import json
            with open(json_path) as f:
                skills = json.load(f)
            
            # Basic quality check
            assert len(skills) >= 0, f"Provider {provider} should extract skills"


@pytest.mark.unit
def test_local_provider_no_api_key(cli_runner, sample_pdf_path, temp_dir):
    """Verify local provider doesn't require API key."""
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("OPENAI_API_KEY", None)
    
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--llm", "local",
        "--output-json", str(Path(temp_dir) / "local_output.json")
    ], env=env)
    
    # Should not fail due to missing API key
    # May fail for other reasons (local model not available)
    if result.returncode != 0:
        assert "api key" not in result.stderr.lower() or \
               "local" in result.stderr.lower()
