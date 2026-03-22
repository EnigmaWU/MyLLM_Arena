# SaveAsSkill

## User Story

- 【AS A】 GitHub Copilot Chat User,
- 【I WANT TO】 save the current conversation as a skill,
  - 【WHEN】 I finally solve the problem after a long long conversation,
- 【SO THAT】 I can reuse the solution as a skill in the future.
  - ALSO I can share the `saveAsSkill` prompt as slash command and `newCreatedSkill` to my workmates or other code agent such as Cline/Continue.

## Acceptance Criteria

- 【GIVEN】 I have a conversation with GitHub Copilot Chat,
- 【WHEN】 I call slash command `/save-as-skill` in the chat input box,
- 【THEN】 I should see a new skill created from the current conversation, 
  - OR if the conversation is not enough to create a skill, I should see an advice message such as:
    - "too simple to be a skill, save as rule or workflow instead"
  - AND the new skill should follow anthropic's skill specification.

## Implementation

Three files work together:

| File | Role |
|------|------|
| [`.github/prompts/save-as-skill.prompt.md`](../../.github/prompts/save-as-skill.prompt.md) | Slash command — manual invocation via `/save-as-skill` |
| [`.github/skills/save-as-skill/SKILL.md`](../../.github/skills/save-as-skill/SKILL.md) | Skill — auto-discoverable by the model when conversation matches |
| [`.github/instructions/save-as-skill-nudge.instructions.md`](../../.github/instructions/save-as-skill-nudge.instructions.md) | Instruction — always-on nudge to suggest `/save-as-skill` after long, solved conversations |

### Auto-Discovery Flow

1. **Always-on nudge** (`.instructions.md`): On every conversation, the agent checks if the conversation is long, solved, non-trivial, and reusable. If all true, it suggests `/save-as-skill`.
2. **Model auto-invocation** (`SKILL.md`): The model can auto-load the skill when it detects keywords like "save", "skill", "capture solution" — no explicit `/` command needed.
3. **Manual invocation** (`.prompt.md`): User types `/save-as-skill` at any time.

### Usage by Agent

| Agent | How to Invoke |
|-------|--------------|
| **GitHub Copilot** | Type `/save-as-skill` in chat (auto-discovered from `.github/prompts/`) |
| **Continue** | Copy the prompt to `.continue/prompts/save-as-skill.prompt` with `invokable: true` |
| **Cline** | Reference the prompt file in conversation, or copy to `.cline/prompts/` |
| **Claude Code** | Copy to `.claude/skills/save-as-skill/SKILL.md` |

### Output

The prompt analyzes the conversation and either:
1. **Creates a SKILL.md** — with name, description, what, why, how (ReACT steps), when, examples, constraints
2. **Advises alternatives** — if too simple, suggests saving as a rule (`.instructions.md`) or workflow note instead

### Relation to DistillSkillAgent

This prompt-based approach is the lightweight counterpart to [DistillSkillAgent](../DistillSkillAgent/), which provides a full Python CLI pipeline for batch processing exported chat sessions.

