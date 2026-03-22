---
description: "Nudge the user to save valuable conversations as skills. Applies to all conversations."
applyTo: "**"
---

## Skill-Saving Awareness

At the end of a conversation, if ALL of the following are true, suggest running `/save-as-skill`:

1. **Long conversation** — more than ~10 back-and-forth exchanges
2. **Problem was solved** — a clear working solution was reached
3. **Non-trivial** — involved debugging, multi-step reasoning, architecture decisions, or domain-specific knowledge
4. **Reusable** — the pattern could apply to similar future problems

When suggesting, say something like:

> This conversation solved a non-trivial problem. Want to save it as a reusable skill? Type `/save-as-skill` to extract it.

Do NOT suggest `/save-as-skill` for:
- Simple Q&A or lookups
- Single-line fixes
- Conversations that didn't reach a solution
