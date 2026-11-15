---
name: saveSessionAsSkill
description: Save the current chat session as an Anthropic SKILL package (prompt.xml +
  instructions.md + examples/). Invoke when you want to preserve the knowledge and
  workflow demonstrated in this conversation for future reuse in Claude Code or Cline.
invokable: true
---

# Task@WHAT

- Analyse the **current chat session** and package its key knowledge and workflow as an
  [Anthropic SKILL](https://github.com/anthropics/skills) that can be reused in Claude
  Code, Cline, or any compatible AI agent.
- The output is a self-contained skill directory (or `.zip`) containing:
  - `prompt.xml` — machine-readable skill definition following Anthropic's
    **skill-creator** template.
  - `instructions.md` — human-readable usage guide structured as
    `WHAT / WHY / HOW / WHEN / Constraints`.
  - `examples/` — representative excerpts from this session as worked examples.

## Purpose@WHY

- A productive chat session contains reusable knowledge that would otherwise be lost
  once the conversation ends.
- Persisting it as an Anthropic SKILL lets you (and your team) invoke the exact same
  reasoning pattern in future sessions without re-exploring the same problem space.
- Using the **skill-creator** template ensures the output is portable across all agents
  that consume Anthropic SKILL packages (Claude Code, Cline, etc.).

## Steps@HOW

1. **Observe — read the session**
   - _Reason:_ Understand the full conversation before extracting anything.
   - Scan every user question and assistant reply in the current session.
   - Identify the core task or problem the session addressed.

2. **Extract — name & describe the skill**
   - _Reason:_ A clear name and one-liner description make the skill discoverable.
   - Derive a concise `skill_name` (CamelCase, no spaces) from the session topic.
     - Example: session about "refactoring legacy code" → `RefactorLegacyCode`.
   - Write a single-sentence `description`: what the skill does and when to use it.

3. **Structure — fill the skill-creator template fields**
   - _Reason:_ Anthropic's skill-creator template defines a consistent schema that all
     compatible agents understand.
   - Map session content to these fields:
     | Field | Source in session |
     |---|---|
     | `what` | The core task the session tackled |
     | `why` | The motivation / value stated or implied |
     | `how` | The numbered steps / approach the assistant demonstrated |
     | `when` | Contexts in which the same approach would apply |
     | `constraints` | Caveats, prerequisites, or warnings mentioned |

4. **Generate — write `prompt.xml`**
   - _Reason:_ `prompt.xml` is the machine-readable entry point parsed by Claude Code /
     Cline when the skill is loaded.
   - Use the following XML skeleton (based on Anthropic's **skill-creator** template):
     ```xml
     <?xml version="1.0" encoding="UTF-8"?>
     <prompt>
       <metadata>
         <name>{skill_name}</name>
         <description>{description}</description>
       </metadata>
       <instructions>
         <section name="what">{what}</section>
         <section name="why">{why}</section>
         <section name="how">
           <steps>
             <step order="1"><action>…</action><reasoning>…</reasoning></step>
             <!-- repeat for each step -->
           </steps>
         </section>
         <section name="when">
           <context>…</context>
         </section>
         <section name="constraints">
           <constraint>…</constraint>
         </section>
       </instructions>
     </prompt>
     ```

5. **Generate — write `instructions.md`**
   - _Reason:_ Human-readable documentation helps developers understand and adapt the
     skill without parsing XML.
   - Structure:
     ```
     # {skill_name}
     {description}
     ## What
     ## Why
     ## How
     ## When to Use
     ## Constraints & Preconditions
     ```

6. **Generate — populate `examples/`**
   - _Reason:_ Concrete examples from the actual session give future users immediate
     context and confidence.
   - Create `examples/example_N.md` for each representative user→assistant exchange
     (up to 3 examples).
   - Format each file as:
     ```
     **User:** {user_message}

     **Assistant:** {assistant_reply}
     ```

7. **Package — assemble the skill directory**
   - _Reason:_ A self-contained directory (or `.zip`) can be dropped directly into
     Claude Code / Cline without extra tooling.
   - Final layout:
     ```
     {skill_name}/
     ├── prompt.xml
     ├── instructions.md
     └── examples/
         ├── example_1.md
         └── …
     ```
   - Optionally zip the directory: `{skill_name}.zip`.

8. **Review — validate before delivering**
   - _Reason:_ Catching issues now prevents broken skills being committed or shared.
   - Confirm `prompt.xml` is valid XML.
   - Confirm `instructions.md` covers all five sections (What / Why / How / When /
     Constraints).
   - Confirm at least one example file exists.

## One-More-Thing

- **STOP** if any of the following is unclear, and ask the user to clarify before
  proceeding:
  - The desired skill name (auto-derived name may not match intent).
  - Whether to include sensitive content from the session in the examples.
  - The target output location for the skill directory / zip.
  - Whether the skill should be compatible only with Claude Code, only with Cline, or
    both.
