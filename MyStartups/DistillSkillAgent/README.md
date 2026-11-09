# Distill Skill Agent

- This is an AI/LLM agent designed to `distill skills` from various sources,
  > such as from classical books, best practices articles.
- THEN output the distilled skills in a `structured format` and THEN transplant the skills other AI/LLM agents, and `apply the skills` in different contexts.
    > such as open source VSCode-Extention **Continue**'s slash command file or Anthropic **Claude Code**'s SKILL package.

## Architecture Design

See [README_ArchDesign.md](README_ArchDesign.md) for detailed architecture design.

## Usage Design

```bash
    $ myDistillSkillAgent --input <input_source> 
        [--output-claude-skill [<skillPackageName>]] 
        [--output-continue-slash-command <slashCommandFilePath>]
    # such as:
    # $ myDistillSkillAgent --input Behavior-Driven-Development.pdf
    #   BDD-generateExecutableSpecification-skill.zip
    #   BDD-generateExecutableSpecification-slash-command.json
```

### CLI Arguments
- `--input <path|url>`: Source document (PDF, Markdown, URL)
- `--output-claude-skill [name]`: Generate Anthropic SKILL package
- `--output-continue-slash-command <path>`: Generate Continue slash command
- `--llm <provider>`: LLM provider (anthropic/openai/local)
- `--verbose`: Detailed logging of extraction process

## saveAsSkill – Copilot Slash Command

`saveAsSkill` is a dedicated slash command that saves a Copilot or LLM **completion session** as a reusable skill. It wraps the full distillation pipeline into a single, focused entry point.

### Quick Start

```bash
# Save a skill from a JSON session file (skill name defaults to 'saveAsSkill')
saveAsSkill --input session.json --output-claude-skill

# Provide an explicit skill name
saveAsSkill --input session.json --skill-name MyTDDSkill --output-claude-skill

# Generate both an Anthropic SKILL package and a Continue slash command
saveAsSkill --input session.json \
    --skill-name BDDPractice \
    --output-claude-skill \
    --output-continue-slash-command bdd-practice.md

# Pipe the current session from stdin
cat current_session.json | saveAsSkill --input - --skill-name BDDPractice \
    --output-claude-skill

# Inspect the intermediate JSON before creating the package
saveAsSkill --input session.json --output-json skill-preview.json --verbose
```

### CLI Arguments

| Argument | Description |
|---|---|
| `--input <path\|stdin\|url>` | `.json` chat session file, `-` for stdin, or HTTP/HTTPS URL |
| `--skill-name <NAME>` | Skill name (letters, digits, `-`, `_`; max 64 chars; default: `saveAsSkill`) |
| `--output-claude-skill [NAME]` | Generate Anthropic SKILL `.zip` package |
| `--output-continue-slash-command <PATH>` | Generate Continue VSCode slash command `.md` |
| `--output-json <PATH>` | Save intermediate skill JSON for inspection |
| `--llm <provider>` | LLM provider (`anthropic`/`openai`/`local`; default: `anthropic`) |
| `--verbose` / `-v` | Show detailed progress |

### Supported Session Formats

| Format | Detection |
|---|---|
| Generic `{"messages": [...]}` | `messages` key with `role`/`content` objects |
| Claude export `{"chat_messages": [...]}` | `chat_messages` key with `sender`/`text` objects |
| ChatGPT export `{"mapping": {...}}` | `mapping` key with nested message nodes |
| Top-level JSON array `[{"role":...}]` | JSON array of message objects |

### Skill Name Rules

- 1–64 characters long
- Only letters (`A-Z`, `a-z`), digits (`0-9`), hyphens (`-`), and underscores (`_`)
- Defaults to `saveAsSkill` when `--skill-name` is omitted

### Error Handling

| Situation | Behaviour |
|---|---|
| Missing input file | Clear "file not found" error with path suggestion |
| Non-`.json` input file | Rejected with supported-formats hint |
| Malformed JSON | `ValueError` with actionable message |
| Empty session (no messages) | Rejected with explanation |
| Invalid skill name | Rejected with character-rule explanation |
| No output format given | Rejected listing available `--output-*` flags |
| LLM API failure | Reports API error with key/rate-limit hint |
