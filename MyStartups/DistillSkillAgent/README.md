# Distill Skill Agent

- This is an AI/LLM agent designed to `distill skills` from various sources,
  > such as from classical books, best practices articles.
- THEN output the distilled skills in a `structured format` and THEN transplant the skills other AI/LLM agents, and `apply the skills` in different contexts.
    > such as open source VSCode-Extention **Continue**'s slash command file or Anthropic **Claude Code**'s SKILL package.

## Architecture Design

See [README_ArchDesign.md](README_ArchDesign.md) for detailed architecture design.

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

### CLI Arguments
- `--input <path|url>`: Source document (PDF, Markdown, URL)
- `--output-claude-skill [name]`: Generate Anthropic SKILL package
- `--output-continue-slash-command <path>`: Generate Continue slash command
- `--llm <provider>`: LLM provider (anthropic/openai/local)
- `--verbose`: Detailed logging of extraction process
