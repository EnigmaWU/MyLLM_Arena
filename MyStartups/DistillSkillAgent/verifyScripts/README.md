# Verification Scripts

Test suite for myDistillSkillAgent based on User Stories and Acceptance Criteria.

## Structure

```
verifyScripts/
├── README.md                      # This file
├── conftest.py                    # Shared pytest fixtures
├── requirements.txt               # Test dependencies
├── test_pdf_extraction.py         # US-001: Extract Skills from PDF
├── test_anthropic_output.py       # US-002: Generate Anthropic SKILL Package
├── test_continue_output.py        # US-003: Generate Continue Slash Command
├── test_multiple_outputs.py       # US-004: Multiple Output Formats
├── test_markdown_input.py         # US-005: Parse Markdown Documentation
├── test_web_scraping.py           # US-006: Scrape from Web URL
├── test_llm_provider.py           # US-007: Choose LLM Provider
├── test_intermediate_json.py      # US-008: Inspect Intermediate Representation
├── test_error_handling.py         # US-009: Handle Errors Gracefully
├── test_batch_processing.py       # US-010: Batch Process Multiple Sources
└── fixtures/                      # Test data
    ├── sample.pdf
    ├── sample.md
    └── expected_outputs/
```

## Setup

```bash
cd verifyScripts
pip install -r requirements.txt
```

## Running Tests

```bash
# Run all tests
pytest -v

# Run specific user story
pytest test_pdf_extraction.py -v

# Run with coverage
pytest --cov=../src --cov-report=html

# Run integration tests only
pytest -m integration

# Run unit tests only
pytest -m unit
```

## Test Markers

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests with real LLM calls
- `@pytest.mark.slow` - Tests that take >30 seconds
- `@pytest.mark.requires_api` - Tests requiring API keys

## Environment Variables

```bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

## Test Coverage Map

| User Story | Test File | Status |
|------------|-----------|--------|
| US-001 | test_pdf_extraction.py | ✅ |
| US-002 | test_anthropic_output.py | ✅ |
| US-003 | test_continue_output.py | ✅ |
| US-004 | test_multiple_outputs.py | ✅ |
| US-005 | test_markdown_input.py | ✅ |
| US-006 | test_web_scraping.py | ✅ |
| US-007 | test_llm_provider.py | ✅ |
| US-008 | test_intermediate_json.py | ✅ |
| US-009 | test_error_handling.py | ✅ |
| US-010 | test_batch_processing.py | ✅ |
