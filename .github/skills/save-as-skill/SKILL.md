---
name: save-as-skill
description: 'Save the current conversation as a reusable skill. Use when: a long conversation finally solved a hard problem, complex debugging session completed, multi-step workflow discovered, or non-obvious solution found after trial and error. Make sure to use this skill whenever the user says "save as skill", "capture this as a skill", "turn this into a skill", wants to preserve a solution for reuse, or mentions they solved something worth remembering.'
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
| **how** | Ordered steps with reasoning. For each step explain *why* it matters, not just *what* to do. Prefer explaining the why over heavy-handed MUSTs. |
| **when** | List of scenarios/triggers — both obvious and near-miss cases |
| **examples** | Actual code/commands from the conversation, not abstract placeholders |
| **constraints** | Preconditions, warnings, or gotchas |
| **scripts** | If the conversation created helper scripts that all future uses would need, list them — these become bundled resources |

## Step 4: Generate the Skill File

Output a complete `SKILL.md`. Use imperative form in instructions. Explain the
reasoning behind each step — today's LLMs are smart and respond better to
understanding *why* than to rigid rules.

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

### Bundled Resources

If the conversation produced helper scripts, templates, or reference docs that
future skill users would need, suggest this structure:

```
<skill-name>/
├── SKILL.md
├── scripts/     # Reusable scripts from the conversation
├── references/  # Domain docs or checklists
└── assets/      # Templates, configs, boilerplate
```

Keep SKILL.md under 500 lines. If it's getting long, move detailed reference
material into `references/` and point to it from SKILL.md.

## Step 5: Suggest Where to Save

Tell the user where to place the generated file:

- **Copilot**: `.github/skills/<name>/SKILL.md`
- **Continue**: `.continue/prompts/<name>.prompt` (reformat with `invokable: true`)
- **Cline**: `.cline/skills/<name>/SKILL.md` or reference via `.clinerules`
- **Claude Code**: `.claude/skills/<name>/SKILL.md`

## Writing Guidelines

These principles (from Anthropic's skill-creator) produce better skills:

- **Preserve original intent** — do NOT over-generalize or add steps that weren't in the conversation
- **Explain the why** — for each instruction, explain why it matters. If you find yourself writing ALWAYS or NEVER in all caps, reframe it as reasoning instead.
- **Include actual artifacts** — real code/commands from the conversation, not abstract placeholders
- **Capture the debugging journey** — if the conversation involved debugging, include what was tried, what failed, and what worked. The failed attempts are often the most valuable part.
- **Make it self-contained** — someone reading this should be able to follow without the original conversation
- **Detect repeated work** — if a pattern or script appeared across multiple attempts in the conversation, that's a strong signal to bundle it as a resource
- **Use theory of mind** — write the skill for a smart reader who benefits from context and reasoning, not a checklist-follower who needs rigid rules
