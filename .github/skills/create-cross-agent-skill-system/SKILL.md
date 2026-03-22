---
name: create-cross-agent-skill-system
description: 'Create a cross-agent skill extraction system with 3-layer auto-discovery (.prompt.md, SKILL.md, .instructions.md). Use when: building a /save-as-skill slash command, setting up skill files for Copilot/Cline/Continue/Claude Code, integrating Anthropic skill-creator patterns, wanting conversation-to-skill pipelines, or building team knowledge capture systems that work across multiple AI coding agents.'
---

# Create a Cross-Agent Skill System

Build a prompt-based skill extraction system with 3-layer auto-discovery that
works across GitHub Copilot, Cline, Continue, and Claude Code.

## When to Use

- Starting a new project that needs conversation-to-skill capture
- Setting up `/save-as-skill` or similar slash commands for any AI agent
- Migrating skill files between agents (Copilot → Cline, etc.)
- Wanting auto-discovery so skills trigger without manual invocation
- Building a team knowledge base from AI conversations
- Integrating Anthropic's skill-creator best practices into your workflow

## What

A 3-layer architecture for skill extraction:
1. **`.prompt.md`** — Manual slash command (user types `/save-as-skill`)
2. **`SKILL.md`** — Auto-invocable by the model when conversation matches description
3. **`.instructions.md`** — Always-on nudge that suggests saving after qualifying conversations

Plus a zero-dependency review tool for testing generated skills.

## Why

Conversations contain valuable problem-solving knowledge that evaporates when
the chat ends. A skill system captures this knowledge in a structured,
reusable format. The 3-layer approach ensures skills get triggered at the right
time — manually when the user knows they want it, automatically when the model
detects a match, and via nudge when neither party notices.

Cross-agent compatibility matters because teams often use different agents, and
skills should be portable. Each agent has slightly different file formats and
locations, but the core content is reusable.

## How

### Step 1: Create the prompt file (manual trigger)

Create `.github/prompts/<name>.prompt.md` with YAML frontmatter. This gives
users a `/name` slash command in Copilot Chat.

```markdown
---
description: "Your description here. Be pushy — include trigger phrases."
agent: "agent"
---

# Skill Title

Your instructions here...
```

The `agent: "agent"` field tells Copilot to use the default agent mode.
The `description` field is what users see when browsing slash commands, but
more importantly, it's what the model uses to decide when to suggest it.

**Why pushy descriptions matter**: Anthropic's skill-creator found that skills
tend to undertrigger rather than overtrigger. A description like "Fix tests"
will rarely activate. "Fix flaky E2E tests. Use when tests pass locally but
fail in CI, when you see timeout errors in Playwright, or when test results
are non-deterministic" triggers much more reliably.

### Step 2: Create the SKILL.md (auto-invocable)

Create `.github/skills/<name>/SKILL.md`. This is the auto-discovery layer —
the model reads the description and decides whether to invoke the skill
without the user explicitly asking.

```markdown
---
name: your-skill-name
description: 'Pushy description with trigger phrases...'
---

# Skill Title

Instructions...
```

Key difference from `.prompt.md`: no `agent` field, has `name` field instead.
The skill can also bundle scripts, references, and assets in subdirectories:

```
<name>/
├── SKILL.md
├── scripts/      # Helper scripts the skill needs
├── references/   # Domain docs, checklists
└── assets/       # Templates, configs, boilerplate
```

### Step 3: Create the nudge instruction (always-on)

Create `.github/instructions/<name>-nudge.instructions.md`. This runs on
every conversation (when `applyTo: "**"`) and nudges the user to save
when criteria are met.

```markdown
---
description: "Nudge description"
applyTo: "**"
---

## When to Nudge

At the end of a conversation, if ALL are true:
1. Long conversation (10+ exchanges)
2. Problem was solved
3. Non-trivial (debugging, architecture, multi-step)
4. Reusable pattern

Suggest: "Want to save this as a reusable skill? Type `/save-as-skill`"
```

This is the safety net — catches qualifying conversations that the user
might not think to save.

### Step 4: Add cross-agent save locations

Each agent has its own file format and location. The skill instructions
should tell users where to save:

| Agent | Location | Format Notes |
|-------|----------|--------------|
| **Copilot** | `.github/skills/<name>/SKILL.md` | YAML frontmatter with `name`, `description` |
| **Continue** | `.continue/prompts/<name>.prompt` | Add `invokable: true` to frontmatter |
| **Cline** | `.cline/skills/<name>/SKILL.md` | Or reference via `.clinerules` |
| **Claude Code** | `.claude/skills/<name>/SKILL.md` | Same SKILL.md format |

The core content (steps, examples, constraints) is identical across agents.
Only the frontmatter and file location differ.

### Step 5: Integrate Anthropic skill-creator patterns

These patterns from Anthropic's open-source skill-creator significantly
improve skill quality:

1. **Pushy descriptions** — See Step 1. Combat undertriggering with extra
   trigger phrases and near-miss scenarios.

2. **Capture Intent step** — Before generating a skill, mine the conversation
   for tools used, sequence of steps, corrections/pivots, and helper scripts.
   Present a summary and confirm with the user before generating.

3. **Explain-the-why writing style** — For each instruction, explain why it
   matters. Avoid rigid MUSTs; reframe as reasoning. A reader who understands
   the rationale adapts better than one following blind rules.

4. **Bundled resources detection** — If the conversation produced scripts,
   configs, or reference material that all future uses would need, bundle
   them in subdirectories rather than inlining.

5. **Progressive disclosure** — Keep SKILL.md under ~500 lines. Link to
   bundled resources rather than embedding full scripts inline.

6. **Preserve the debugging journey** — What was tried, what failed, what
   worked. Failed attempts are often the most valuable part.

### Step 6: Add test/review tooling (optional but recommended)

Adapt a zero-dependency Python review script (stdlib only) that:
- Scans workspace for test outputs
- Serves a browser-based review UI
- Collects feedback as JSON
- Supports `--static` mode for headless environments

The test flow: generate skill → draft test prompts → create workspace with
outputs → launch reviewer → collect feedback → iterate.

Important: if the script renders user-provided content in HTML, sanitize it
with `html.escape()` to prevent XSS.

## Examples

### Actual file structure created in this conversation

```
.github/
├── prompts/
│   └── save-as-skill.prompt.md          # Manual /save-as-skill command
├── skills/
│   └── save-as-skill/
│       ├── SKILL.md                      # Auto-invocable skill
│       └── scripts/
│           └── generate_review.py        # Zero-dep review viewer
└── instructions/
    └── save-as-skill-nudge.instructions.md  # Always-on nudge
```

### Pushy description example (before → after)

**Before** (undertriggers):
```
description: "Save conversation as skill"
```

**After** (triggers reliably):
```
description: 'Save the current conversation as a reusable skill. Use when: a
long conversation finally solved a hard problem, complex debugging session
completed, multi-step workflow discovered, or non-obvious solution found after
trial and error. Make sure to use this skill whenever the user says "save as
skill", "capture this as a skill", "turn this into a skill", wants to preserve
a solution for reuse, or mentions they solved something worth remembering.'
```

### Nudge criteria

The nudge fires when ALL of:
1. 10+ back-and-forth exchanges
2. Clear working solution reached
3. Non-trivial (debugging, architecture, domain knowledge)
4. Pattern could apply to similar future problems

## Constraints

- **Copilot frontmatter is YAML** — single quotes around descriptions with special chars
- **SKILL.md `description` max 1024 chars** — be concise but pushy
- **`applyTo: "**"`** applies to all files/conversations — use sparingly for nudges
- **Zero external dependencies for bundled scripts** — use Python stdlib only so the skill works everywhere without `pip install`
- **Each agent's format differs slightly** — test the frontmatter in each agent you support
- **Deferred from this skill** (requires Anthropic's full eval framework): description optimization via `run_loop.py`, blind comparison subagents, automated eval pipeline
