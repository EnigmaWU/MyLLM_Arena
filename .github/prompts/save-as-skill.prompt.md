---
description: "Save the current conversation as a reusable skill. Use when: a long conversation finally solved a hard problem, complex debugging session completed, multi-step workflow discovered, or non-obvious solution found after trial and error."
agent: "agent"
---

# Save As Skill

Extract a reusable skill from the current conversation. The goal is to capture
what was learned so that someone facing a similar problem can follow the skill
without the original conversation.

## Step 1: Assess Skill-Worthiness

Review the entire conversation and evaluate:

- **Complexity**: Multiple steps, non-obvious reasoning, or domain knowledge?
- **Reusability**: Could this apply to similar future problems?
- **Completeness**: Was the problem actually solved?

**If the conversation is too simple** (single-step fix, trivial lookup, one-liner answer), respond with:

> This conversation is too simple to be a skill. Consider saving it as:
> - A **rule** (`.github/copilot-instructions.md` or `.instructions.md`) if it's a coding preference or convention
> - A **workflow note** in your project docs if it's a one-off procedure

Then STOP.

## Step 2: Capture Intent from the Conversation

Before generating anything, mine the conversation for:

- **Tools and commands used** — what was actually executed
- **Sequence of steps** — the order things happened in
- **Corrections and pivots** — what was tried first, what failed, what finally worked
- **Input/output formats** — what went in, what came out
- **Helper scripts created** — if the conversation produced utility scripts, these should become bundled resources

Present a brief summary to the user and ask them to confirm or fill gaps:
"Here's what I extracted — anything missing or wrong before I generate the skill?"

## Step 3: Extract the Skill Descriptor

| Field | How to Extract |
|-------|----------------|
| **name** | Lowercase, hyphenated identifier derived from the core action (e.g., `fix-flaky-e2e-tests`) |
| **description** | What it does + when to use it. Be a little "pushy" — include extra trigger phrases so the skill doesn't undertrigger. Instead of just "Fix flaky tests", write "Fix flaky E2E tests. Use when tests pass locally but fail in CI, when you see timeout errors in Playwright, or when test results are non-deterministic." (max 1024 chars) |
| **what** | What task the skill accomplishes |
| **why** | Why this skill is useful — explain the reasoning, not just "it's helpful" |
| **how** | Ordered steps with reasoning. For each step explain *why* it matters, not just *what* to do. |
| **when** | List of scenarios/triggers — both obvious and near-miss cases |
| **examples** | Actual code/commands from the conversation, not abstract placeholders |
| **constraints** | Preconditions, warnings, or gotchas |
| **scripts** | If the conversation created helper scripts that all future uses would need, list them |

## Step 4: Generate the Skill File

Output a complete `SKILL.md`. Use imperative form. Explain the reasoning behind
each step — write for a smart reader who benefits from context, not rigid rules.

```markdown
---
name: <extracted-name>
description: '<pushy-description-with-trigger-phrases>'
---

# <Skill Title>

## When to Use
<bullet list of triggers/scenarios — include non-obvious cases>

## What
<task description>

## Why
<problem & rationale — explain why this matters>

## How

### Step 1: <action>
<what to do and why it matters>

### Step 2: <action>
<what to do and why it matters>

(continue for all steps)

## Examples

<actual code, commands, or configurations from the conversation>

## Constraints
<preconditions, warnings, edge cases>
```

If the conversation produced helper scripts or reference material, suggest bundling:

```
<skill-name>/
├── SKILL.md
├── scripts/     # Reusable scripts from the conversation
├── references/  # Domain docs or checklists
└── assets/      # Templates, configs, boilerplate
```

## Step 5: Test the Skill (optional but recommended)

After generating the SKILL.md, draft 2-3 realistic test prompts and share them
with the user. For each test, create a workspace directory with outputs, then
launch the review viewer:

```bash
python .github/skills/save-as-skill/scripts/generate_review.py \
  <skill-name>-workspace/ \
  --skill-name "my-skill"
```

The user reviews each test case in the browser, leaves feedback, and submits.
Read `feedback.json`, improve the skill, and iterate until satisfied.

## Step 6: Suggest Where to Save

Tell the user where to place the generated file:

- **Copilot**: `.github/skills/<name>/SKILL.md`
- **Continue**: `.continue/prompts/<name>.prompt` (reformat with `invokable: true`)
- **Cline**: `.cline/skills/<name>/SKILL.md` or reference via `.clinerules`
- **Claude Code**: `.claude/skills/<name>/SKILL.md`

## Writing Guidelines

- **Preserve original intent** — do NOT over-generalize or add steps that weren't in the conversation
- **Explain the why** — for each instruction, explain why it matters. Avoid heavy-handed MUSTs; reframe as reasoning.
- **Include actual artifacts** — real code/commands, not abstract placeholders
- **Capture the debugging journey** — what was tried, what failed, what worked. Failed attempts are often the most valuable part.
- **Make it self-contained** — followable without the original conversation
- **Detect repeated work** — scripts or patterns that appeared multiple times should become bundled resources
