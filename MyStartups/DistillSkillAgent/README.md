# Distill Skill Agent

- This is an AI/LLM agent designed to `distill skills` from various sources,
  > such as from classical books, best practices articles.
- THEN output the distilled skills in a `structured format` and THEN transplant the skills other AI/LLM agents, and `apply the skills` in different contexts.
    > such as open source VSCode-Extention **Continue**'s slash command file or Anthropic **Claude Code**'s SKILL package.

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
