"""
US-011: saveAsSkill from Chat Session

Acceptance Criteria:
- Accepts .json chat session file as --input parameter
- Accepts '-' (stdin) as --input to read a JSON chat session
- Supports multiple chat session export formats (generic, Claude, ChatGPT)
- Converts chat session to a Document with source_type == 'chat_session'
- Extracts user and assistant turns as separate Document sections
- Stores session title and turn count in Document metadata
- Malformed JSON produces a clear, actionable error message
- Invalid/missing chat session format is handled gracefully
"""

import json
import os
import subprocess
import sys
import tempfile
import shutil
from io import StringIO
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Sample chat session fixtures
# ---------------------------------------------------------------------------

GENERIC_SESSION = {
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

CLAUDE_SESSION = {
    "name": "Claude Refactoring Chat",
    "chat_messages": [
        {"sender": "human", "text": "What is Extract Method refactoring?"},
        {
            "sender": "assistant",
            "text": (
                "Extract Method is a refactoring technique where you move a fragment "
                "of code from an existing method into a new, separately named method "
                "to improve readability and reduce duplication."
            ),
        },
    ],
}

CHATGPT_SESSION = {
    "title": "ChatGPT DDD Session",
    "mapping": {
        "root": {"parent": None, "children": ["msg1"], "message": None},
        "msg1": {
            "parent": "root",
            "children": ["msg2"],
            "message": {
                "role": "user",
                "content": {"parts": ["What is a Bounded Context in DDD?"]},
            },
        },
        "msg2": {
            "parent": "msg1",
            "children": [],
            "message": {
                "role": "assistant",
                "content": {
                    "parts": [
                        "A Bounded Context is a central pattern in Domain-Driven Design. "
                        "It defines the boundary within which a particular domain model applies, "
                        "ensuring each model is consistent and unambiguous within its context."
                    ]
                },
            },
        },
    },
}

GENERIC_LIST_SESSION = [
    {"role": "user", "content": "Explain SOLID principles."},
    {
        "role": "assistant",
        "content": (
            "SOLID is an acronym for five OOP design principles: "
            "Single Responsibility, Open/Closed, Liskov Substitution, "
            "Interface Segregation, and Dependency Inversion."
        ),
    },
]


# ---------------------------------------------------------------------------
# Unit tests – ChatSessionParser directly
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_parse_generic_session_file(temp_dir):
    """ChatSessionParser correctly parses a generic JSON session file."""
    from distillSkillAgent.parsers import ChatSessionParser

    session_path = Path(temp_dir) / "session.json"
    session_path.write_text(json.dumps(GENERIC_SESSION), encoding="utf-8")

    parser = ChatSessionParser()
    document = parser.parse_json_file(str(session_path))

    assert document.source_type == "chat_session"
    assert document.metadata.get("turn_count") == len(GENERIC_SESSION["messages"])
    assert document.metadata.get("title") == GENERIC_SESSION["title"]
    # All turns represented as sections
    assert len(document.structure) == len(GENERIC_SESSION["messages"])


@pytest.mark.unit
def test_parse_claude_session_file(temp_dir):
    """ChatSessionParser correctly parses a Claude export format."""
    from distillSkillAgent.parsers import ChatSessionParser

    session_path = Path(temp_dir) / "claude_session.json"
    session_path.write_text(json.dumps(CLAUDE_SESSION), encoding="utf-8")

    parser = ChatSessionParser()
    document = parser.parse_json_file(str(session_path))

    assert document.source_type == "chat_session"
    assert document.metadata.get("turn_count") == len(CLAUDE_SESSION["chat_messages"])
    assert CLAUDE_SESSION["name"] in document.metadata.get("title", "")
    assert len(document.structure) == len(CLAUDE_SESSION["chat_messages"])


@pytest.mark.unit
def test_parse_chatgpt_session_file(temp_dir):
    """ChatSessionParser correctly parses a ChatGPT export format."""
    from distillSkillAgent.parsers import ChatSessionParser

    session_path = Path(temp_dir) / "chatgpt_session.json"
    session_path.write_text(json.dumps(CHATGPT_SESSION), encoding="utf-8")

    parser = ChatSessionParser()
    document = parser.parse_json_file(str(session_path))

    assert document.source_type == "chat_session"
    # Should have parsed 2 real messages (user + assistant)
    assert document.metadata.get("turn_count") == 2


@pytest.mark.unit
def test_parse_generic_list_session(temp_dir):
    """ChatSessionParser accepts a top-level JSON array of messages."""
    from distillSkillAgent.parsers import ChatSessionParser

    session_path = Path(temp_dir) / "list_session.json"
    session_path.write_text(json.dumps(GENERIC_LIST_SESSION), encoding="utf-8")

    parser = ChatSessionParser()
    document = parser.parse_json_file(str(session_path))

    assert document.source_type == "chat_session"
    assert document.metadata.get("turn_count") == len(GENERIC_LIST_SESSION)


@pytest.mark.unit
def test_chat_session_document_has_full_content(temp_dir):
    """Document content contains both user and assistant messages."""
    from distillSkillAgent.parsers import ChatSessionParser

    session_path = Path(temp_dir) / "session.json"
    session_path.write_text(json.dumps(GENERIC_SESSION), encoding="utf-8")

    parser = ChatSessionParser()
    document = parser.parse_json_file(str(session_path))

    # Content should contain text from both roles
    assert "Test-Driven Development" in document.content
    assert "Red-Green-Refactor" in document.content


@pytest.mark.unit
def test_chat_section_titles_include_turn_and_role(temp_dir):
    """Document sections have descriptive titles (Turn N: User/Assistant)."""
    from distillSkillAgent.parsers import ChatSessionParser

    session_path = Path(temp_dir) / "session.json"
    session_path.write_text(json.dumps(GENERIC_SESSION), encoding="utf-8")

    parser = ChatSessionParser()
    document = parser.parse_json_file(str(session_path))

    titles = [s.title for s in document.structure]
    assert any("User" in t for t in titles)
    assert any("Assistant" in t for t in titles)
    assert any("Turn 1" in t for t in titles)


@pytest.mark.unit
def test_malformed_json_raises_value_error(temp_dir):
    """Malformed JSON produces a ValueError with an actionable message."""
    from distillSkillAgent.parsers import ChatSessionParser

    bad_path = Path(temp_dir) / "bad.json"
    bad_path.write_text("{not valid json}", encoding="utf-8")

    parser = ChatSessionParser()
    with pytest.raises(ValueError, match="[Ii]nvalid JSON"):
        parser.parse_json_file(str(bad_path))


@pytest.mark.unit
def test_parse_stream_from_stdin_equivalent(temp_dir):
    """ChatSessionParser.parse_stream() works with a StringIO object."""
    from distillSkillAgent.parsers import ChatSessionParser

    stream = StringIO(json.dumps(GENERIC_SESSION))
    parser = ChatSessionParser()
    document = parser.parse_stream(stream)

    assert document.source_type == "chat_session"
    assert document.metadata.get("turn_count") == len(GENERIC_SESSION["messages"])


@pytest.mark.unit
def test_parse_stream_bad_json_raises_value_error():
    """parse_stream raises ValueError on malformed JSON from stream."""
    from distillSkillAgent.parsers import ChatSessionParser

    stream = StringIO("{ bad json }")
    parser = ChatSessionParser()
    with pytest.raises(ValueError, match="[Ii]nvalid JSON"):
        parser.parse_stream(stream)


# ---------------------------------------------------------------------------
# Unit tests – SourceParser routing
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_source_parser_routes_json_to_chat_session(temp_dir):
    """.json files are routed to ChatSessionParser and return chat_session docs."""
    from distillSkillAgent.parsers import SourceParser

    session_path = Path(temp_dir) / "session.json"
    session_path.write_text(json.dumps(GENERIC_SESSION), encoding="utf-8")

    parser = SourceParser()
    document = parser.parse(str(session_path))

    assert document.source_type == "chat_session"


@pytest.mark.unit
def test_source_parser_stdin_dash_accepted():
    """SourceParser.parse('-') triggers stdin path (ChatSessionParser.parse_stream)."""
    from distillSkillAgent.parsers import ChatSessionParser, SourceParser
    import unittest.mock as mock

    mock_doc_sentinel = object()

    with mock.patch.object(
        ChatSessionParser, "parse_stream", return_value=mock_doc_sentinel
    ) as patched:
        parser = SourceParser()
        # We need to avoid actual stdin read, so we patch sys.stdin
        with mock.patch("distillSkillAgent.parsers.sys.stdin"):
            result = parser.parse("-")

    patched.assert_called_once()
    assert result is mock_doc_sentinel


# ---------------------------------------------------------------------------
# Unit tests – CLI integration (no LLM calls)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_cli_accepts_json_input(cli_runner, temp_dir):
    """CLI accepts a .json chat session file as --input."""
    session_path = Path(temp_dir) / "session.json"
    session_path.write_text(json.dumps(GENERIC_SESSION), encoding="utf-8")

    result = cli_runner([
        "--input", str(session_path),
        "--output-json", str(Path(temp_dir) / "output.json"),
    ])

    # Should NOT say "unsupported format"
    assert "unsupported format" not in result.stderr.lower(), (
        f"Should accept .json input, got stderr: {result.stderr}"
    )


@pytest.mark.unit
def test_cli_rejects_malformed_json(cli_runner, temp_dir):
    """CLI fails with a clear error when a .json file contains invalid JSON."""
    bad_path = Path(temp_dir) / "bad.json"
    bad_path.write_text("{not valid json}", encoding="utf-8")

    result = cli_runner([
        "--input", str(bad_path),
        "--output-json", str(Path(temp_dir) / "output.json"),
    ])

    assert result.returncode != 0
    error = result.stderr.lower()
    assert any(kw in error for kw in ["json", "invalid", "error"]), (
        f"Should report JSON error, got: {result.stderr}"
    )


@pytest.mark.unit
def test_cli_accepts_stdin_dash(cli_runner, temp_dir):
    """CLI accepts '-' as --input for stdin chat session piping."""
    output_path = str(Path(temp_dir) / "output.json")
    session_json = json.dumps(GENERIC_SESSION)

    env = os.environ.copy()
    env["ANTHROPIC_API_KEY"] = "test-key-for-unit-tests"

    result = subprocess.run(
        [sys.executable, "-m", "distillSkillAgent",
         "--input", "-",
         "--output-json", output_path],
        input=session_json,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(Path(__file__).parent.parent),
    )

    # Should not fail with "unsupported format" or "file not found"
    assert "unsupported format" not in result.stderr.lower()
    assert "file not found" not in result.stderr.lower()


# ---------------------------------------------------------------------------
# Unit tests – ChatMessage / ChatSession models
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_chat_message_to_dict():
    """ChatMessage.to_dict() serialises correctly."""
    from distillSkillAgent.models import ChatMessage

    msg = ChatMessage(role="user", content="Hello")
    d = msg.to_dict()
    assert d == {"role": "user", "content": "Hello"}


@pytest.mark.unit
def test_chat_session_to_dict():
    """ChatSession.to_dict() serialises all messages."""
    from distillSkillAgent.models import ChatMessage, ChatSession

    session = ChatSession(
        title="Test Session",
        messages=[
            ChatMessage(role="user", content="Q"),
            ChatMessage(role="assistant", content="A"),
        ],
    )
    d = session.to_dict()
    assert d["title"] == "Test Session"
    assert len(d["messages"]) == 2


@pytest.mark.unit
def test_chat_session_to_text():
    """ChatSession.to_text() produces a readable transcript."""
    from distillSkillAgent.models import ChatMessage, ChatSession

    session = ChatSession(
        title="Demo",
        messages=[
            ChatMessage(role="user", content="What is BDD?"),
            ChatMessage(role="assistant", content="Behaviour-Driven Development."),
        ],
    )
    text = session.to_text()
    assert "Demo" in text
    assert "What is BDD?" in text
    assert "Behaviour-Driven Development." in text
    assert "User" in text
    assert "Assistant" in text
