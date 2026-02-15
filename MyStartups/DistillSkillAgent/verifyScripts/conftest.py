"""
Shared pytest fixtures for myDistillSkillAgent verification tests.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)


@pytest.fixture
def sample_pdf_path():
    """Path to sample PDF for testing."""
    return Path(__file__).parent / "fixtures" / "sample.pdf"


@pytest.fixture
def sample_md_path():
    """Path to sample Markdown for testing."""
    return Path(__file__).parent / "fixtures" / "sample.md"


@pytest.fixture
def mock_skill_descriptor():
    """Mock SkillDescriptor object for testing."""
    return {
        "name": "test-skill",
        "description": "A test skill for verification",
        "what": "Demonstrate skill extraction and formatting",
        "why": "To verify the distillation pipeline works correctly",
        "how": [
            {
                "order": 1,
                "action": "Parse the input source",
                "reasoning": "Need to extract structured content first"
            },
            {
                "order": 2,
                "action": "Identify actionable patterns",
                "reasoning": "Skills must be practical and executable"
            }
        ],
        "when": [
            "When testing the skill distillation pipeline",
            "When verifying output formats"
        ],
        "examples": [
            "Example 1: Parse PDF and extract skills",
            "Example 2: Generate output in multiple formats"
        ],
        "constraints": [
            "Input must be in supported format (PDF, MD, URL)",
            "LLM API key must be configured"
        ]
    }


@pytest.fixture
def cli_runner():
    """Helper to run CLI commands."""
    import subprocess
    import sys
    
    def run_cli(args, env=None):
        """Run myDistillSkillAgent CLI with given arguments."""
        # If env is provided, use it as-is (for tests that explicitly control environment)
        # Otherwise, set a default API key for tests that don't care about authentication
        if env is not None:
            # Use provided env (including explicit removals)
            final_env = env
        else:
            # Default case: provide fake API key if not in environment
            final_env = os.environ.copy()
            if 'ANTHROPIC_API_KEY' not in final_env:
                final_env['ANTHROPIC_API_KEY'] = 'test-key-for-unit-tests'
        
        cmd = [sys.executable, "-m", "distillSkillAgent"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=final_env
        )
        return result
    
    return run_cli


@pytest.fixture
def mock_llm_response():
    """Mock LLM API response for testing without real API calls."""
    return {
        "skills": [
            {
                "name": "extract-method",
                "description": "Extract method refactoring pattern",
                "what": "Extract a code fragment into a new method",
                "why": "Improve code readability and reusability",
                "how": [
                    {"order": 1, "action": "Identify code to extract", "reasoning": "Must be cohesive unit"},
                    {"order": 2, "action": "Create new method", "reasoning": "Encapsulate functionality"},
                    {"order": 3, "action": "Replace original with call", "reasoning": "Maintain behavior"}
                ],
                "when": ["Code duplication exists", "Method too long"],
                "examples": ["Example: Extract calculation logic"],
                "constraints": ["Method must have clear purpose"]
            }
        ]
    }


@pytest.fixture(autouse=True)
def ensure_fixtures_dir():
    """Ensure fixtures directory exists."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    expected_dir = fixtures_dir / "expected_outputs"
    expected_dir.mkdir(exist_ok=True)


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "requires_api: mark test as requiring API keys")
