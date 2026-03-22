# save-as-skill

A 3-layer system for extracting reusable skills from AI conversations, designed for GitHub Copilot and portable to Cline, Continue, and Claude Code.

## What Is This

When a long AI conversation solves a hard problem, the knowledge typically evaporates when the chat ends. This skill captures that knowledge as a structured, reusable file (`SKILL.md`) that any AI coding agent can discover and apply to similar future problems.

The system has three layers that work together:

| Layer | Copilot | Cline | Continue | Claude Code |
|-------|---------|-------|----------|-------------|
| **Manual trigger** | [`.github/prompts/save-as-skill.prompt.md`](../../prompts/save-as-skill.prompt.md) | `.clinerules` rule | `.continue/prompts/save-as-skill.prompt` | `.claude/commands/save-as-skill.md` |
| **Auto-invocable** | [`.github/skills/save-as-skill/SKILL.md`](SKILL.md) | `.cline/skills/save-as-skill/SKILL.md` | `.continue/prompts/save-as-skill.prompt` | `.claude/skills/save-as-skill/SKILL.md` |
| **Always-on nudge** | [`.github/instructions/save-as-skill-nudge.instructions.md`](../../instructions/save-as-skill-nudge.instructions.md) | `.clinerules` rule | `.continue/config.yaml` system message | `CLAUDE.md` rule |

Plus a bundled test/review tool:

| File | Purpose |
|------|---------|
| [`scripts/generate_review.py`](scripts/generate_review.py) | Zero-dependency Python review viewer for testing generated skills |

## Why Three Layers

A single file isn't enough because there are three distinct moments when skill-saving should happen:

1. **User knows** they want to save → they type `/save-as-skill` → **prompt file** handles it
2. **Model detects** the conversation matches → auto-invokes → **SKILL.md** handles it
3. **Neither notices** → end-of-conversation nudge → **instructions file** catches it

Without the nudge layer, qualifying conversations slip through. Without the auto-invocable layer, saving only happens when users remember to ask. The three layers form a safety net.

## Why Pushy Descriptions

Anthropic's open-source [skill-creator](https://github.com/anthropics/skill-creator) found that skills **undertrigger** far more often than they overtrigger. A short description like `"Save conversation as skill"` rarely activates.

The fix: write descriptions that include extra trigger phrases and near-miss scenarios. Our description explicitly lists phrases like "save as skill", "capture this as a skill", "turn this into a skill" so the model matches more reliably.

## Why Explain-the-Why

Traditional instruction files use rigid rules (`ALWAYS do X`, `NEVER do Y`). Anthropic's research found that LLMs respond better to reasoning. When a skill explains *why* a step matters, the model adapts the instruction to novel contexts instead of following it literally and breaking on edge cases.

## Porting to Other Agents

The core content (steps, examples, constraints) is identical across agents. Only the file location and frontmatter differ. Below shows how each of the three layers maps to each agent.

### Layer 1: Manual Trigger

The user explicitly asks to save a skill (slash command or keyword).

**Copilot** — already set up via `.github/prompts/save-as-skill.prompt.md`. User types `/save-as-skill`.

**Cline** — add to `.clinerules`:

```
# .clinerules
When the user asks to "save as skill", "capture this as a skill", or "turn this into a skill",
read and follow .github/skills/save-as-skill/SKILL.md
```

**Continue** — create `.continue/prompts/save-as-skill.prompt`:

```yaml
---
name: save-as-skill
description: "Save the current conversation as a reusable skill."
invokable: true
---
```

Then paste the body of `SKILL.md` (everything below the frontmatter) into the file. The `invokable: true` flag registers it as a `/save-as-skill` slash command.

**Claude Code** — create `.claude/commands/save-as-skill.md`:

```markdown
Extract a reusable skill from the current conversation.
Follow the instructions in .claude/skills/save-as-skill/SKILL.md
```

User types `/save-as-skill` in Claude Code's prompt.

### Layer 2: Auto-Invocable

The model detects a matching conversation and invokes the skill without the user asking.

**Copilot** — already set up via `.github/skills/save-as-skill/SKILL.md`. The `description` field in frontmatter controls when the model triggers it.

**Cline** — copy or symlink the skill:

```bash
mkdir -p .cline/skills/save-as-skill
cp .github/skills/save-as-skill/SKILL.md .cline/skills/save-as-skill/
cp -r .github/skills/save-as-skill/scripts .cline/skills/save-as-skill/
```

Cline discovers skills in `.cline/skills/` and matches based on the description.

**Continue** — Continue uses the same `.continue/prompts/save-as-skill.prompt` file for both manual and auto-invocation. The model reads the description and can suggest it proactively.

**Claude Code** — copy the skill directory:

```bash
mkdir -p .claude/skills/save-as-skill
cp .github/skills/save-as-skill/SKILL.md .claude/skills/save-as-skill/
cp -r .github/skills/save-as-skill/scripts .claude/skills/save-as-skill/
```

Claude Code discovers `SKILL.md` files in `.claude/skills/` automatically.

### Layer 3: Always-On Nudge

At the end of qualifying conversations, the agent suggests saving as a skill.

**Copilot** — already set up via `.github/instructions/save-as-skill-nudge.instructions.md` with `applyTo: "**"`.

**Cline** — append to `.clinerules`:

```
# Skill-saving nudge
At the end of a conversation, if ALL of these are true:
1. More than ~10 back-and-forth exchanges
2. A clear working solution was reached
3. Non-trivial (debugging, architecture, multi-step reasoning)
4. Pattern could apply to similar future problems
Then suggest: "This conversation solved a non-trivial problem. Want to save it as a reusable skill?"
```

**Continue** — add to `.continue/config.yaml` system message:

```yaml
systemMessage: |
  At the end of long conversations (10+ exchanges) that solved a non-trivial,
  reusable problem, suggest saving as a skill by typing /save-as-skill.
```

**Claude Code** — add to `CLAUDE.md` in the project root:

```markdown
## Skill-Saving Nudge

At the end of long conversations (10+ exchanges) that solved a non-trivial,
reusable problem, suggest: "Want to save this as a reusable skill?"
Then follow .claude/skills/save-as-skill/SKILL.md
```

## Usage

### In Copilot Chat

```
/save-as-skill
```

The agent reviews the conversation, extracts a skill, and generates `SKILL.md`.

### Test a Generated Skill

```bash
python .github/skills/save-as-skill/scripts/generate_review.py \
  my-skill-workspace/ \
  --skill-name "my-skill"
```

Opens a browser-based reviewer. Leave feedback, iterate, repeat.

### Headless Mode

```bash
python .github/skills/save-as-skill/scripts/generate_review.py \
  my-skill-workspace/ \
  --skill-name "my-skill" \
  --static /tmp/review.html
```

Writes a standalone HTML file instead of starting a server.
