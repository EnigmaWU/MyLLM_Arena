"""
saveAsSkill - Copilot slash command handler for saving chat sessions as skills.

This module provides the ``SaveAsSkillCommand`` class and a standalone CLI entry
point (``saveAsSkill``) that lets users turn a Copilot/LLM completion session
into a reusable Anthropic SKILL package or Continue slash command.

Usage examples
--------------
Save a skill from a JSON session file, letting the tool infer the name:

    saveAsSkill --input session.json --output-claude-skill

Give the skill an explicit name and also produce a Continue slash command:

    saveAsSkill --input session.json \\
        --skill-name MyTDDSkill \\
        --output-claude-skill \\
        --output-continue-slash-command tdd-skill.md

Pipe the current session from stdin:

    cat current_session.json | saveAsSkill --input - --skill-name BDDPractice \\
        --output-claude-skill
"""

import argparse
import re
import sys
import os
from pathlib import Path
from typing import Optional

from .parsers import SourceParser, ChatSessionParser
from .distiller import SkillDistiller
from .formatters import AnthropicSkillFormatter, ContinueSlashCMDFormatter, save_skills_json

# Maximum allowed length for a skill name.
_SKILL_NAME_MAX_LEN = 64

# Characters allowed in a skill name (letters, digits, hyphens, underscores).
_SKILL_NAME_RE = re.compile(r'^[A-Za-z0-9_-]+$')

# Default skill name when none is provided.
DEFAULT_SKILL_NAME = "saveAsSkill"


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_skill_name(name: str) -> str:
    """
    Validate and normalise a user-supplied skill name.

    Rules
    -----
    - Must be 1–64 characters long.
    - May only contain letters, digits, hyphens (``-``), or underscores (``_``).

    Parameters
    ----------
    name:
        The candidate skill name.

    Returns
    -------
    str
        The validated name (unchanged if valid).

    Raises
    ------
    ValueError
        With an actionable message when the name is invalid.
    """
    if not name:
        raise ValueError(
            "Skill name must not be empty. "
            f"Use --skill-name to provide a name, or omit it to default to '{DEFAULT_SKILL_NAME}'."
        )
    if len(name) > _SKILL_NAME_MAX_LEN:
        raise ValueError(
            f"Skill name '{name}' is too long ({len(name)} chars). "
            f"Maximum allowed length is {_SKILL_NAME_MAX_LEN} characters."
        )
    if not _SKILL_NAME_RE.match(name):
        raise ValueError(
            f"Skill name '{name}' contains invalid characters. "
            "Only letters (A-Z, a-z), digits (0-9), hyphens (-), "
            "and underscores (_) are allowed."
        )
    return name


# ---------------------------------------------------------------------------
# Core command class
# ---------------------------------------------------------------------------

class SaveAsSkillCommand:
    """
    Slash command handler that converts a chat completion session into a skill.

    Parameters
    ----------
    llm_provider:
        Which LLM backend to use for skill distillation
        (``"anthropic"``, ``"openai"``, ``"mockSrvLLM_Anthropic"``, …).
    algorithm:
        Distillation strategy (``"simple"`` or ``"findActionBook"``).
    verbose:
        When ``True``, emit progress messages to *stdout*.
    """

    def __init__(
        self,
        llm_provider: str = "anthropic",
        algorithm: str = "simple",
        verbose: bool = False,
    ) -> None:
        self.llm_provider = llm_provider
        self.algorithm = algorithm
        self.verbose = verbose

        self._source_parser = SourceParser()
        self._distiller: Optional[SkillDistiller] = None  # lazy-initialised

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def execute(
        self,
        input_source: str,
        skill_name: str = DEFAULT_SKILL_NAME,
        output_claude_skill: Optional[str] = None,
        output_continue_slash_command: Optional[str] = None,
        output_json: Optional[str] = None,
        output_dir: str = ".",
    ) -> dict:
        """
        Execute the saveAsSkill command.

        Parameters
        ----------
        input_source:
            Path to a ``.json`` chat session file, ``"-"`` to read from *stdin*,
            or an HTTP/HTTPS URL.
        skill_name:
            Name for the generated skill.  Defaults to ``DEFAULT_SKILL_NAME``.
        output_claude_skill:
            If not ``None``, generate an Anthropic SKILL ``.zip`` package.
            Pass an explicit path/name or an empty string to use *skill_name*.
        output_continue_slash_command:
            If not ``None``, generate a Continue slash command ``.md`` file.
        output_json:
            If not ``None``, save the intermediate skill JSON for inspection.
        output_dir:
            Directory in which to place output files (default: current dir).

        Returns
        -------
        dict
            ``{"success": bool, "outputs": list[str], "skills_count": int}``

        Raises
        ------
        ValueError
            When *skill_name* is invalid, no output format is specified, or the
            session data cannot be parsed.
        FileNotFoundError
            When *input_source* points to a non-existent file.
        """
        # Validate skill name
        skill_name = validate_skill_name(skill_name)

        # Require at least one output format
        if not any([
            output_claude_skill is not None,
            output_continue_slash_command,
            output_json,
        ]):
            raise ValueError(
                "At least one output format must be specified: "
                "--output-claude-skill, --output-continue-slash-command, or --output-json."
            )

        self._log(f"Processing input: {input_source}")

        # Parse session document
        document = self._source_parser.parse(input_source)

        if document.source_type != "chat_session":
            raise ValueError(
                f"Input '{input_source}' did not produce a chat session document "
                f"(got source_type='{document.source_type}'). "
                "Please provide a JSON chat session file or pipe one via stdin."
            )

        # Validate session has at least one message
        turn_count = document.metadata.get("turn_count", 0)
        if turn_count == 0:
            raise ValueError(
                "The chat session contains no messages. "
                "Ensure the session file has at least one user or assistant turn."
            )

        self._log(
            f"Parsed chat session '{document.metadata.get('title', skill_name)}' "
            f"with {turn_count} turn(s)."
        )

        # Lazy-initialise distiller
        distiller = self._get_distiller()

        # Distill skills from the session document
        skills = distiller.distill(document, verbose=self.verbose)

        if not skills:
            raise ValueError(
                "No skills could be extracted from the session. "
                "The conversation may not contain enough actionable content. "
                "Try a session with more detailed instructions or steps."
            )

        self._log(f"Extracted {len(skills)} skill(s).")

        # Override extracted skill name with user-supplied name
        skill = skills[0]
        skill.name = skill_name

        outputs_created: list = []

        # Anthropic SKILL package
        if output_claude_skill is not None:
            zip_name = output_claude_skill if output_claude_skill else skill_name
            zip_path = str(Path(output_dir) / zip_name)
            formatter = AnthropicSkillFormatter()
            out = formatter.format(skill, zip_path)
            outputs_created.append(out)
            self._log(f"Generated Anthropic SKILL: {out}")

        # Continue slash command
        if output_continue_slash_command:
            formatter = ContinueSlashCMDFormatter()
            slash_path = str(Path(output_dir) / output_continue_slash_command) \
                if not Path(output_continue_slash_command).is_absolute() \
                else output_continue_slash_command
            out = formatter.format(skill, slash_path)
            outputs_created.append(out)
            self._log(f"Generated Continue slash command: {out}")

        # Intermediate JSON
        if output_json:
            json_path = str(Path(output_dir) / output_json) \
                if not Path(output_json).is_absolute() \
                else output_json
            out = save_skills_json(skills, json_path)
            outputs_created.append(out)
            self._log(f"Generated JSON: {out}")

        return {
            "success": True,
            "outputs": outputs_created,
            "skills_count": len(skills),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_distiller(self) -> SkillDistiller:
        """Lazy-initialise and cache the SkillDistiller."""
        if self._distiller is None:
            self._distiller = SkillDistiller(
                llm_provider=self.llm_provider,
                algorithm=self.algorithm,
            )
        return self._distiller

    def _log(self, message: str) -> None:
        """Print a progress message when verbose mode is enabled."""
        if self.verbose:
            print(message)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    """Parse CLI arguments for the saveAsSkill command."""
    parser = argparse.ArgumentParser(
        prog="saveAsSkill",
        description="saveAsSkill - Save a Copilot/LLM completion session as a reusable skill.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Save a skill from a JSON session file (skill name defaults to 'saveAsSkill')
  saveAsSkill --input session.json --output-claude-skill

  # Provide an explicit skill name
  saveAsSkill --input session.json --skill-name MyTDDSkill --output-claude-skill

  # Generate both an Anthropic SKILL package and a Continue slash command
  saveAsSkill --input session.json \\
      --skill-name BDDPractice \\
      --output-claude-skill \\
      --output-continue-slash-command bdd-practice.md

  # Pipe the current session from stdin
  cat current_session.json | saveAsSkill --input - --skill-name BDDPractice \\
      --output-claude-skill

  # Inspect the intermediate skill JSON before generating the package
  saveAsSkill --input session.json --output-json skill-preview.json --verbose
        """
    )

    parser.add_argument(
        "--input",
        required=True,
        help=(
            "Input source: path to a .json chat session file, "
            "'-' to read a JSON session from stdin, "
            "or an HTTP/HTTPS URL."
        ),
    )

    parser.add_argument(
        "--skill-name",
        default=DEFAULT_SKILL_NAME,
        metavar="NAME",
        help=(
            f"Name for the generated skill.  "
            f"Must be 1–{_SKILL_NAME_MAX_LEN} characters: letters, digits, "
            f"hyphens, or underscores.  Defaults to '{DEFAULT_SKILL_NAME}'."
        ),
    )

    parser.add_argument(
        "--output-claude-skill",
        metavar="NAME",
        nargs="?",
        const="",
        help=(
            "Generate an Anthropic SKILL package (.zip).  "
            "Optionally provide a custom output filename; "
            "defaults to the value of --skill-name."
        ),
    )

    parser.add_argument(
        "--output-continue-slash-command",
        metavar="PATH",
        help="Generate a Continue VSCode slash command (.md) at the given path.",
    )

    parser.add_argument(
        "--output-json",
        metavar="PATH",
        help="Save the intermediate skill JSON for inspection/editing.",
    )

    parser.add_argument(
        "--llm",
        choices=["anthropic", "openai", "mockSrvLLM_OpenAI", "mockSrvLLM_Anthropic", "local"],
        default="anthropic",
        help="LLM provider to use for skill extraction (default: anthropic).",
    )

    parser.add_argument(
        "--algorithm",
        "--algo",
        choices=["simple", "findActionBook"],
        default="simple",
        help="Distillation strategy (default: simple).",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress during extraction.",
    )

    return parser.parse_args(argv)


def main(argv=None):
    """Main entry point for the saveAsSkill CLI command."""
    args = parse_args(argv)

    # Validate skill name early for a fast, clear error
    try:
        validate_skill_name(args.skill_name)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Require at least one output format
    if not any([
        args.output_claude_skill is not None,
        args.output_continue_slash_command,
        args.output_json,
    ]):
        print(
            "Error: At least one output format must be specified: "
            "--output-claude-skill, --output-continue-slash-command, or --output-json.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate input file exists (non-URL, non-stdin)
    if args.input != "-" and not args.input.startswith(("http://", "https://")):
        if not os.path.exists(args.input):
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            print("Suggestion: Check that the path is correct and the file exists.", file=sys.stderr)
            sys.exit(1)
        ext = os.path.splitext(args.input)[1].lower()
        if ext != ".json":
            print(
                f"Error: saveAsSkill expects a .json chat session file, got '{args.input}'.",
                file=sys.stderr,
            )
            print("Supported input: .json files, '-' for stdin, or HTTP/HTTPS URLs.", file=sys.stderr)
            sys.exit(1)

    output_dir = os.getenv("OUTPUT_DIR", ".")

    try:
        cmd = SaveAsSkillCommand(
            llm_provider=args.llm,
            algorithm=args.algorithm,
            verbose=args.verbose,
        )
        result = cmd.execute(
            input_source=args.input,
            skill_name=args.skill_name,
            output_claude_skill=args.output_claude_skill,
            output_continue_slash_command=args.output_continue_slash_command,
            output_json=args.output_json,
            output_dir=output_dir,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print("Suggestion: Check that the path is correct and the file exists.", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ImportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        error_msg = str(exc).lower()
        if "api" in error_msg or "anthropic" in error_msg or "openai" in error_msg:
            print(f"Error: API failure: {exc}", file=sys.stderr)
            print("Suggestion: Check your API key and rate limits.", file=sys.stderr)
        elif "network" in error_msg or "connection" in error_msg:
            print(f"Error: Network error: {exc}", file=sys.stderr)
            print("Suggestion: Check your internet connection and try again.", file=sys.stderr)
        else:
            print(f"Error: {exc}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Success: print summary
    print(f"✓ Skill '{args.skill_name}' saved ({result['skills_count']} skill(s) extracted).")
    for output in result["outputs"]:
        print(f"    {output}")

    sys.exit(0)


if __name__ == "__main__":
    main()
