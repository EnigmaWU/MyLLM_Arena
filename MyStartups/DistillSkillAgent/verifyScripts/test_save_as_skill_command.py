"""
Tests for the saveAsSkill slash command handler.

Covers:
- SaveAsSkillCommand class (unit tests, no real LLM calls)
- validate_skill_name helper
- CLI entry point (argument parsing, validation, integration)
"""

import json
import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Sample chat session fixtures (reuse format from test_chat_session_input.py)
# ---------------------------------------------------------------------------

SAMPLE_SESSION = {
    "title": "TDD Practice Session",
    "messages": [
        {"role": "user", "content": "How do I apply Test-Driven Development?"},
        {
            "role": "assistant",
            "content": (
                "TDD follows the Red-Green-Refactor cycle. First write a failing test "
                "(Red), then write the minimum code to make it pass (Green), then "
                "clean up the code without breaking the test (Refactor)."
            ),
        },
        {"role": "user", "content": "Can you show me the steps in more detail?"},
        {
            "role": "assistant",
            "content": (
                "Sure! Step 1: Write a unit test for a small piece of behaviour. "
                "Step 2: Run the test – it should fail. "
                "Step 3: Write just enough production code to pass the test. "
                "Step 4: Run the test again – it should now pass. "
                "Step 5: Refactor for clarity and run all tests to confirm nothing broke."
            ),
        },
    ],
}

EMPTY_SESSION = {
    "title": "Empty Session",
    "messages": [],
}


# ---------------------------------------------------------------------------
# Unit tests – validate_skill_name
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_valid_skill_names():
    """validate_skill_name accepts valid names."""
    from distillSkillAgent.saveAsSkill import validate_skill_name

    for name in ["saveAsSkill", "My-Skill", "skill_v2", "TDD", "a" * 64]:
        assert validate_skill_name(name) == name


@pytest.mark.unit
def test_default_skill_name_is_valid():
    """DEFAULT_SKILL_NAME passes validation."""
    from distillSkillAgent.saveAsSkill import DEFAULT_SKILL_NAME, validate_skill_name

    assert validate_skill_name(DEFAULT_SKILL_NAME) == DEFAULT_SKILL_NAME


@pytest.mark.unit
def test_empty_skill_name_raises():
    """validate_skill_name raises ValueError for empty string."""
    from distillSkillAgent.saveAsSkill import validate_skill_name

    with pytest.raises(ValueError, match="[Ee]mpty"):
        validate_skill_name("")


@pytest.mark.unit
def test_too_long_skill_name_raises():
    """validate_skill_name raises ValueError for names longer than 64 chars."""
    from distillSkillAgent.saveAsSkill import validate_skill_name

    with pytest.raises(ValueError, match="[Tt]oo long"):
        validate_skill_name("a" * 65)


@pytest.mark.unit
@pytest.mark.parametrize("bad_name", [
    "my skill",       # space
    "skill/name",     # slash
    "skill.name",     # dot
    "skill@v1",       # at-sign
    "名前",            # non-ASCII
])
def test_invalid_chars_skill_name_raises(bad_name):
    """validate_skill_name raises ValueError for names with invalid characters."""
    from distillSkillAgent.saveAsSkill import validate_skill_name

    with pytest.raises(ValueError, match="[Ii]nvalid"):
        validate_skill_name(bad_name)


# ---------------------------------------------------------------------------
# Unit tests – SaveAsSkillCommand.execute (mocked distiller)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_execute_requires_output_format(temp_dir):
    """SaveAsSkillCommand.execute raises ValueError when no output is specified."""
    from distillSkillAgent.saveAsSkill import SaveAsSkillCommand

    session_path = Path(temp_dir) / "session.json"
    session_path.write_text(json.dumps(SAMPLE_SESSION), encoding="utf-8")

    cmd = SaveAsSkillCommand()
    with pytest.raises(ValueError, match="[Aa]t least one output"):
        cmd.execute(input_source=str(session_path))


@pytest.mark.unit
def test_execute_rejects_invalid_skill_name(temp_dir):
    """SaveAsSkillCommand.execute raises ValueError for an invalid skill name."""
    from distillSkillAgent.saveAsSkill import SaveAsSkillCommand

    session_path = Path(temp_dir) / "session.json"
    session_path.write_text(json.dumps(SAMPLE_SESSION), encoding="utf-8")

    cmd = SaveAsSkillCommand()
    with pytest.raises(ValueError):
        cmd.execute(
            input_source=str(session_path),
            skill_name="bad name!",
            output_json=str(Path(temp_dir) / "out.json"),
        )


@pytest.mark.unit
def test_execute_rejects_empty_session(temp_dir):
    """SaveAsSkillCommand.execute raises ValueError for a session with no messages."""
    from distillSkillAgent.saveAsSkill import SaveAsSkillCommand

    session_path = Path(temp_dir) / "empty.json"
    session_path.write_text(json.dumps(EMPTY_SESSION), encoding="utf-8")

    cmd = SaveAsSkillCommand()
    with pytest.raises(ValueError, match="[Nn]o messages"):
        cmd.execute(
            input_source=str(session_path),
            output_json=str(Path(temp_dir) / "out.json"),
        )


@pytest.mark.unit
def test_execute_uses_supplied_skill_name(temp_dir, monkeypatch):
    """SaveAsSkillCommand.execute overrides the distilled skill name with the user-supplied name."""
    from distillSkillAgent.saveAsSkill import SaveAsSkillCommand
    from distillSkillAgent.models import SkillDescriptor, Step
    import distillSkillAgent.saveAsSkill as sas_module

    # Stub out SkillDistiller so no API call is made
    class _FakeDistiller:
        def distill(self, document, verbose=False):
            return [SkillDescriptor(
                name="auto-generated-name",
                description="desc",
                what="what",
                why="why",
                how=[Step(order=1, action="do it", reasoning="because")],
                when=[],
                examples=[],
                constraints=[],
            )]

    monkeypatch.setattr(sas_module, "SkillDistiller", lambda **_: _FakeDistiller())

    session_path = Path(temp_dir) / "session.json"
    session_path.write_text(json.dumps(SAMPLE_SESSION), encoding="utf-8")

    cmd = SaveAsSkillCommand()
    result = cmd.execute(
        input_source=str(session_path),
        skill_name="MyCustomSkill",
        output_json=str(Path(temp_dir) / "out.json"),
        output_dir=temp_dir,
    )

    assert result["success"] is True
    # The output JSON should contain the user-supplied name
    output_json = Path(temp_dir) / "out.json"
    data = json.loads(output_json.read_text())
    assert data[0]["name"] == "MyCustomSkill"


@pytest.mark.unit
def test_execute_default_skill_name(temp_dir, monkeypatch):
    """SaveAsSkillCommand.execute uses DEFAULT_SKILL_NAME when no name is given."""
    from distillSkillAgent.saveAsSkill import SaveAsSkillCommand, DEFAULT_SKILL_NAME
    from distillSkillAgent.models import SkillDescriptor, Step
    import distillSkillAgent.saveAsSkill as sas_module

    class _FakeDistiller:
        def distill(self, document, verbose=False):
            return [SkillDescriptor(
                name="distilled",
                description="desc",
                what="what",
                why="why",
                how=[Step(order=1, action="act", reasoning="reason")],
                when=[],
                examples=[],
                constraints=[],
            )]

    monkeypatch.setattr(sas_module, "SkillDistiller", lambda **_: _FakeDistiller())

    session_path = Path(temp_dir) / "session.json"
    session_path.write_text(json.dumps(SAMPLE_SESSION), encoding="utf-8")

    cmd = SaveAsSkillCommand()
    result = cmd.execute(
        input_source=str(session_path),
        output_json=str(Path(temp_dir) / "out.json"),
        output_dir=temp_dir,
    )

    assert result["success"] is True
    data = json.loads((Path(temp_dir) / "out.json").read_text())
    assert data[0]["name"] == DEFAULT_SKILL_NAME


@pytest.mark.unit
def test_execute_returns_outputs_list(temp_dir, monkeypatch):
    """SaveAsSkillCommand.execute returns a list of created output paths."""
    from distillSkillAgent.saveAsSkill import SaveAsSkillCommand
    from distillSkillAgent.models import SkillDescriptor, Step
    import distillSkillAgent.saveAsSkill as sas_module

    class _FakeDistiller:
        def distill(self, document, verbose=False):
            return [SkillDescriptor(
                name="skill",
                description="desc",
                what="what",
                why="why",
                how=[Step(order=1, action="act", reasoning="r")],
                when=[],
                examples=[],
                constraints=[],
            )]

    monkeypatch.setattr(sas_module, "SkillDistiller", lambda **_: _FakeDistiller())

    session_path = Path(temp_dir) / "session.json"
    session_path.write_text(json.dumps(SAMPLE_SESSION), encoding="utf-8")

    cmd = SaveAsSkillCommand()
    result = cmd.execute(
        input_source=str(session_path),
        skill_name="TestSkill",
        output_json=str(Path(temp_dir) / "out.json"),
        output_dir=temp_dir,
    )

    assert isinstance(result["outputs"], list)
    assert len(result["outputs"]) >= 1


# ---------------------------------------------------------------------------
# CLI tests – argument parsing and validation
# ---------------------------------------------------------------------------


def _run_saveasskill(args, input_data=None, env=None):
    """Run the saveAsSkill CLI as a subprocess."""
    final_env = env if env is not None else os.environ.copy()
    final_env.setdefault("ANTHROPIC_API_KEY", "test-key-for-unit-tests")

    return subprocess.run(
        [sys.executable, "-m", "distillSkillAgent.saveAsSkill"] + args,
        input=input_data,
        capture_output=True,
        text=True,
        env=final_env,
        cwd=str(Path(__file__).parent.parent),
    )


@pytest.mark.unit
def test_cli_requires_input(temp_dir):
    """CLI exits with error when --input is missing."""
    result = _run_saveasskill(["--output-json", str(Path(temp_dir) / "out.json")])
    assert result.returncode != 0
    assert "input" in result.stderr.lower() or "error" in result.stderr.lower()


@pytest.mark.unit
def test_cli_requires_output_format(temp_dir):
    """CLI exits with error when no output format is provided."""
    session_path = Path(temp_dir) / "session.json"
    session_path.write_text(json.dumps(SAMPLE_SESSION), encoding="utf-8")

    result = _run_saveasskill(["--input", str(session_path)])
    assert result.returncode != 0
    assert "output" in result.stderr.lower()


@pytest.mark.unit
def test_cli_rejects_invalid_skill_name(temp_dir):
    """CLI exits with error for an invalid --skill-name."""
    session_path = Path(temp_dir) / "session.json"
    session_path.write_text(json.dumps(SAMPLE_SESSION), encoding="utf-8")

    result = _run_saveasskill([
        "--input", str(session_path),
        "--skill-name", "bad name!",
        "--output-json", str(Path(temp_dir) / "out.json"),
    ])
    assert result.returncode != 0
    assert "error" in result.stderr.lower()


@pytest.mark.unit
def test_cli_rejects_missing_file(temp_dir):
    """CLI exits with a clear error when the input file does not exist."""
    result = _run_saveasskill([
        "--input", str(Path(temp_dir) / "nonexistent.json"),
        "--output-json", str(Path(temp_dir) / "out.json"),
    ])
    assert result.returncode != 0
    assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()


@pytest.mark.unit
def test_cli_rejects_non_json_input(temp_dir):
    """CLI exits with error when a non-.json file is supplied."""
    md_path = Path(temp_dir) / "session.md"
    md_path.write_text("# session", encoding="utf-8")

    result = _run_saveasskill([
        "--input", str(md_path),
        "--output-json", str(Path(temp_dir) / "out.json"),
    ])
    assert result.returncode != 0
    assert "json" in result.stderr.lower() or "error" in result.stderr.lower()


@pytest.mark.unit
def test_cli_default_skill_name_is_saveasskill(temp_dir):
    """CLI --skill-name defaults to 'saveAsSkill' (reflected in help text)."""
    result = _run_saveasskill(["--help"])
    assert result.returncode == 0
    assert "saveAsSkill" in result.stdout


@pytest.mark.unit
def test_cli_accepts_valid_json_session(temp_dir):
    """CLI accepts a valid .json chat session without 'unsupported format' error."""
    session_path = Path(temp_dir) / "session.json"
    session_path.write_text(json.dumps(SAMPLE_SESSION), encoding="utf-8")

    # cli_runner uses myDistillSkillAgent; here we invoke saveAsSkill directly
    result = _run_saveasskill([
        "--input", str(session_path),
        "--output-json", str(Path(temp_dir) / "out.json"),
    ])

    # Should not error on format detection
    assert "unsupported format" not in result.stderr.lower(), (
        f"Unexpected stderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Module-level import test
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_saveasskill_importable():
    """SaveAsSkillCommand and helpers are importable from the package root."""
    from distillSkillAgent import SaveAsSkillCommand, validate_skill_name, DEFAULT_SKILL_NAME  # noqa: F401

    assert callable(SaveAsSkillCommand)
    assert callable(validate_skill_name)
    assert isinstance(DEFAULT_SKILL_NAME, str)
    assert DEFAULT_SKILL_NAME == "saveAsSkill"
