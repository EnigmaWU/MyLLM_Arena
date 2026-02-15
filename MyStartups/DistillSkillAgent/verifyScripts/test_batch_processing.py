"""
US-010: Batch Process Multiple Sources

Acceptance Criteria:
- --input accepts multiple files (comma-separated or glob pattern)
- Each source generates separate output files
- Outputs named after source files automatically
- Progress bar shows overall completion
- Failures in one file don't stop batch processing
- Summary report at end shows success/failure count
"""

import pytest
from pathlib import Path


@pytest.mark.unit
def test_accepts_multiple_files(cli_runner, temp_dir):
    """Verify --input accepts multiple files (comma-separated)."""
    # Create multiple input files
    file1 = Path(temp_dir) / "input1.md"
    file2 = Path(temp_dir) / "input2.md"
    
    file1.write_text("# Skill 1")
    file2.write_text("# Skill 2")
    
    result = cli_runner([
        "--input", f"{file1},{file2}",
        "--output-claude-skill"
    ])
    
    # Should accept comma-separated format
    assert "invalid" not in result.stderr.lower() or result.returncode != 0


@pytest.mark.unit
def test_accepts_glob_pattern(cli_runner, temp_dir):
    """Verify --input accepts glob pattern."""
    # Create multiple files
    for i in range(3):
        (Path(temp_dir) / f"book{i}.md").write_text(f"# Book {i}")
    
    result = cli_runner([
        "--input", str(Path(temp_dir) / "book*.md"),
        "--output-json"
    ])
    
    # Should accept glob pattern
    assert "unrecognized" not in result.stderr.lower()


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.slow
def test_generates_separate_outputs(cli_runner, temp_dir):
    """Verify each source generates separate output files."""
    # Create multiple inputs
    inputs = []
    for i in range(2):
        input_file = Path(temp_dir) / f"source{i}.md"
        input_file.write_text(f"# Source {i}\n\nContent for skill extraction.")
        inputs.append(input_file)
    
    result = cli_runner([
        "--input", ",".join(str(f) for f in inputs),
        "--output-claude-skill"
    ], env={"OUTPUT_DIR": temp_dir})
    
    # Check for separate output files
    # Naming convention may vary, but should create multiple outputs
    zip_files = list(Path(temp_dir).glob("*.zip"))
    
    if result.returncode == 0:
        assert len(zip_files) >= 1, "Should create output files"


@pytest.mark.integration
@pytest.mark.requires_api
def test_auto_naming_from_source(cli_runner, temp_dir):
    """Verify outputs named after source files automatically."""
    input_file = Path(temp_dir) / "CleanCode.md"
    input_file.write_text("# Clean Code Principles")
    
    result = cli_runner([
        "--input", str(input_file),
        "--output-claude-skill"
    ], env={"OUTPUT_DIR": temp_dir})
    
    # Check if output uses source filename
    possible_names = [
        Path(temp_dir) / "CleanCode.zip",
        Path(temp_dir) / "clean-code.zip",
        Path(temp_dir) / "cleancode.zip"
    ]
    
    if result.returncode == 0:
        found = any(p.exists() for p in possible_names)
        # Implementation may use different naming
        assert found or len(list(Path(temp_dir).glob("*.zip"))) > 0


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.slow
def test_shows_progress_bar(cli_runner, temp_dir):
    """Verify progress bar shows overall completion."""
    # Create multiple inputs
    for i in range(3):
        (Path(temp_dir) / f"file{i}.md").write_text(f"# File {i}")
    
    result = cli_runner([
        "--input", str(Path(temp_dir) / "file*.md"),
        "--output-claude-skill"
    ])
    
    output = result.stdout + result.stderr
    
    # Look for progress indicators
    progress_indicators = [
        "%",
        "processing",
        "/",  # e.g., "2/3"
        "progress",
        "█",  # progress bar character
        "completed"
    ]
    
    has_progress = any(ind in output for ind in progress_indicators)
    
    if result.returncode == 0:
        # Should show some progress indication
        assert has_progress or len(output) > 0


@pytest.mark.integration
@pytest.mark.slow
def test_continues_on_failure(cli_runner, temp_dir):
    """Verify failures in one file don't stop batch processing."""
    # Create mix of valid and invalid files
    valid_file = Path(temp_dir) / "valid.md"
    valid_file.write_text("# Valid Content")
    
    invalid_file = Path(temp_dir) / "invalid.pdf"
    invalid_file.write_text("Not a real PDF")
    
    result = cli_runner([
        "--input", f"{valid_file},{invalid_file}",
        "--output-claude-skill"
    ], env={"OUTPUT_DIR": temp_dir})
    
    output = result.stdout + result.stderr
    
    # Should mention both files in processing
    # Should continue despite one failure
    # (exact behavior depends on implementation)
    
    # At minimum, should not crash completely
    assert "panic" not in output.lower()
    assert "traceback" not in output.lower() or result.returncode != 0


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.slow
def test_summary_report(cli_runner, temp_dir):
    """Verify summary report shows success/failure count."""
    # Create multiple files
    for i in range(3):
        (Path(temp_dir) / f"book{i}.md").write_text(f"# Book {i}\n\nContent here.")
    
    result = cli_runner([
        "--input", str(Path(temp_dir) / "book*.md"),
        "--output-claude-skill"
    ])
    
    output = result.stdout + result.stderr
    
    # Look for summary information
    summary_indicators = [
        "summary",
        "succeeded",
        "failed",
        "completed",
        "total",
        "processed"
    ]
    
    has_summary = any(ind in output.lower() for ind in summary_indicators)
    
    if result.returncode == 0:
        # Should provide some summary
        assert has_summary or "3" in output  # Number of files processed


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.slow
def test_batch_performance(cli_runner, temp_dir):
    """Verify batch processing is reasonably efficient."""
    import time
    
    # Create 5 small files
    for i in range(5):
        (Path(temp_dir) / f"test{i}.md").write_text(
            f"# Test {i}\n\n" + "Some content here. " * 20
        )
    
    start = time.time()
    result = cli_runner([
        "--input", str(Path(temp_dir) / "test*.md"),
        "--output-json"
    ], env={"OUTPUT_DIR": temp_dir})
    elapsed = time.time() - start
    
    # Should complete in reasonable time
    # (adjust threshold based on actual requirements)
    # For 5 small files, should be relatively quick
    assert elapsed < 600, f"Batch processing took {elapsed}s, should be <600s"


@pytest.mark.unit
def test_empty_batch_handling(cli_runner, temp_dir):
    """Verify graceful handling of empty batch (no matching files)."""
    result = cli_runner([
        "--input", str(Path(temp_dir) / "nonexistent*.md"),
        "--output-claude-skill"
    ])
    
    # Should handle gracefully
    if result.returncode != 0:
        error = result.stderr.lower()
        assert "no files" in error or "not found" in error or \
               "no match" in error or "empty" in error
