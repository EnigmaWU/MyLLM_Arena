---
description: "Save the current conversation as a reusable skill. Use when: a long conversation finally solved a hard problem and you want to capture the solution for future reuse."
agent: "agent"
---

# Save As Skill

You are a skill extractor. Analyze the current conversation and decide whether it can be distilled into a reusable **skill**.

## Step 1: Assess Skill-Worthiness

Review the entire conversation and evaluate:

- **Complexity**: Does it involve multiple steps, non-obvious reasoning, or domain knowledge?
- **Reusability**: Could this solution apply to similar problems in the future?
- **Completeness**: Was the problem actually solved with a clear outcome?

**If the conversation is too simple** (single-step fix, trivial lookup, one-liner answer), respond with:

> This conversation is too simple to be a skill. Consider saving it as:
> - A **rule** (`.github/copilot-instructions.md` or `.instructions.md`) if it's a coding preference or convention
> - A **workflow note** in your project docs if it's a one-off procedure

Then STOP.

## Step 2: Extract the Skill Descriptor

If skill-worthy, extract these fields from the conversation:

| Field | Description |
|-------|-------------|
| **name** | Lowercase, hyphenated identifier (e.g., `fix-flaky-e2e-tests`) |
| **description** | One sentence: what it does + when to use it (max 1024 chars) |
| **what** | What task the skill accomplishes |
| **why** | Why this skill is useful / what problem it solves |
| **how** | Ordered steps with reasoning (ReACT style: action + why) |
| **when** | List of scenarios/triggers where this skill applies |
| **examples** | Key code snippets or commands from the conversation |
| **constraints** | Preconditions, warnings, or gotchas |

## Step 3: Generate the Skill File

Output a complete `SKILL.md` file in this format:

```markdown
---
name: <extracted-name>
description: '<extracted-description>'
---

# <Skill Title>

## When to Use
<bullet list of triggers/scenarios>

## What
<task description>

## Why
<problem & rationale>

## How

### Step 1: <action>
<reasoning and details>

### Step 2: <action>
<reasoning and details>

(continue for all steps)

## Examples

<key code snippets, commands, or configurations>

## Constraints
<preconditions, warnings, edge cases>
```

## Step 4: Suggest Where to Save

Tell the user where to place the generated file:

- **Copilot**: `.github/skills/<name>/SKILL.md`
- **Continue**: `.continue/prompts/<name>.prompt` (reformat as Continue slash command with `invokable: true`)
- **Cline**: `.cline/skills/<name>/SKILL.md` or reference via `.clinerules`
- **Claude Code**: `.claude/skills/<name>/SKILL.md`

## Rules

- Preserve the user's original intent — do NOT over-generalize or add steps that weren't in the conversation
- Include actual code/commands from the conversation, not abstract placeholders
- If the conversation involved debugging, capture the diagnostic steps (what was tried, what failed, what worked)
- Keep the skill self-contained — someone reading it should be able to follow without the original conversation
