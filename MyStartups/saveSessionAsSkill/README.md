# saveSessionAsSkill

A **Continue slash command** that saves the current chat session as an
[Anthropic SKILL](https://github.com/anthropics/skills) package.

## What it does

Invoke `/saveSessionAsSkill` in [Continue](https://continue.dev) (or any compatible
AI coding assistant) to transform the active conversation into a reusable Anthropic
SKILL package.  The command outputs:

| File | Purpose |
|---|---|
| `prompt.xml` | Machine-readable skill definition (Anthropic skill-creator template) |
| `instructions.md` | Human-readable guide (WHAT / WHY / HOW / WHEN / Constraints) |
| `examples/example_N.md` | Representative Q&A excerpts from the session |

The resulting skill directory (or `.zip`) can be loaded directly in **Claude Code**
or **Cline** without any additional tooling.

## How to install the slash command

Copy (or symlink) `saveSessionAsSkill.md` into your Continue prompts directory:

```bash
# Linux / macOS
cp saveSessionAsSkill.md ~/.continue/prompts/saveSessionAsSkill.md

# Windows
copy saveSessionAsSkill.md %USERPROFILE%\.continue\prompts\saveSessionAsSkill.md
```

Then reload Continue.  The command is available as `/saveSessionAsSkill`.

## Usage

```
/saveSessionAsSkill
```

Continue will analyse the current session and generate the skill package in the
current working directory (or the location you specify when prompted).

## Reference

- [Anthropic skills repository](https://github.com/anthropics/skills) — skill-creator
  template used by this command.
- [Continue slash command docs](https://docs.continue.dev/customize/deep-dives/prompts)
  — how Continue loads and executes `.md` prompt files.
