# Verification Design - User Stories & Acceptance Criteria

## User Stories

### US-001: Extract Skills from PDF Book
**As a** software engineer learning best practices  
**I want to** extract actionable skills from a PDF technical book  
**So that** I can use those skills in my AI coding assistants

**Acceptance Criteria:**
- [ ] CLI accepts PDF file path as input via `--input` parameter
- [ ] Tool successfully parses PDF and extracts text content
- [ ] Extracted skills include WHAT/WHY/HOW structure
- [ ] Each skill has clear, actionable steps
- [ ] Tool displays progress during extraction (with `--verbose`)
- [ ] Extraction completes within reasonable time (< 5 min for 300-page book)
- [ ] Output contains at least 3-5 distinct skills from the source

**Example:**
```bash
$ myDistillSkillAgent --input Clean-Code.pdf --verbose
Parsing PDF... ✓
Extracting 15 sections...
Pass 1: Identified 12 candidate skills... ✓
Pass 2: Enriched with context... ✓
Pass 3: Validated and deduplicated (10 final skills)... ✓
```

---

### US-002: Generate Anthropic SKILL Package
**As a** Claude Code user  
**I want to** convert extracted skills into Anthropic SKILL format  
**So that** I can use them as custom skills in my coding workflow

**Acceptance Criteria:**
- [ ] CLI accepts `--output-claude-skill` parameter
- [ ] Generated package follows Anthropic SKILL specification
- [ ] Package contains valid `prompt.xml` file
- [ ] Package includes instruction files
- [ ] Package is properly zipped with correct structure
- [ ] Skill name is derived from source or explicitly provided
- [ ] Output file saved with `.zip` extension
- [ ] Package can be imported into Claude Code/Cline

**Example:**
```bash
$ myDistillSkillAgent --input BDD.pdf \
    --output-claude-skill BDD-ExecutableSpec

Output: BDD-ExecutableSpec.zip
Structure:
  ├── prompt.xml
  ├── instructions.md
  └── examples/
```

---

### US-003: Generate Continue Slash Command
**As a** Continue VSCode extension user  
**I want to** convert extracted skills into slash command format  
**So that** I can invoke them directly in my editor

**Acceptance Criteria:**
- [ ] CLI accepts `--output-continue-slash-command` parameter
- [ ] Generated file follows Continue slash command specification
- [ ] YAML frontmatter includes `name`, `description`, `invokable: true`
- [ ] Markdown body structured with Task@WHAT, Purpose@WHY, Steps@HOW
- [ ] Includes "One-More-Thing" safety checkpoint section
- [ ] Output saved as `.md` file at specified path
- [ ] File is valid Continue slash command (manually testable)

**Example:**
```bash
$ myDistillSkillAgent --input refactoring.pdf \
    --output-continue-slash-command ./slash-commands/extract-method.md

Output: slash-commands/extract-method.md
Content:
  ---
  name: extract-method
  description: Extract method refactoring pattern...
  invokable: true
  ---
  # Task@WHAT ...
```

---

### US-004: Support Multiple Output Formats Simultaneously
**As a** user of multiple AI assistants  
**I want to** generate both output formats from a single source  
**So that** I can use the same skill across different tools

**Acceptance Criteria:**
- [ ] Can specify both `--output-claude-skill` and `--output-continue-slash-command`
- [ ] Both outputs generated from same intermediate representation
- [ ] Both outputs are consistent in content/quality
- [ ] Tool completes both generations without re-parsing source
- [ ] Clear confirmation messages for each output created

**Example:**
```bash
$ myDistillSkillAgent --input TDD.pdf \
    --output-claude-skill TDD-RedGreenRefactor \
    --output-continue-slash-command ./tdd-slash.md

Parsing TDD.pdf... ✓
Distilling skills... ✓
Generated: TDD-RedGreenRefactor.zip ✓
Generated: ./tdd-slash.md ✓
```

---

### US-005: Parse Markdown Documentation
**As a** developer reading online documentation  
**I want to** extract skills from Markdown articles  
**So that** I can codify best practices from blog posts and guides

**Acceptance Criteria:**
- [ ] Accepts `.md` file as `--input` parameter
- [ ] Preserves code block examples from markdown
- [ ] Respects heading hierarchy for skill organization
- [ ] Handles markdown-specific formatting (links, lists, tables)
- [ ] Extraction quality comparable to PDF parsing

**Example:**
```bash
$ myDistillSkillAgent --input design-patterns.md \
    --output-claude-skill DesignPatterns
```

---

### US-006: Scrape and Extract from Web URL
**As a** learner consuming online articles  
**I want to** directly extract skills from web URLs  
**So that** I don't need to download files manually

**Acceptance Criteria:**
- [ ] Accepts HTTP/HTTPS URL as `--input` parameter
- [ ] Successfully fetches and parses web content
- [ ] Filters out navigation, ads, and irrelevant content
- [ ] Focuses on main article/tutorial content
- [ ] Handles common web formats (Medium, Dev.to, personal blogs)

**Example:**
```bash
$ myDistillSkillAgent \
    --input https://martinfowler.com/articles/refactoring.html \
    --output-claude-skill Refactoring
```

---

### US-007: Choose LLM Provider
**As a** user with different LLM subscriptions  
**I want to** select which LLM to use for extraction  
**So that** I can use my preferred/available service

**Acceptance Criteria:**
- [ ] `--llm` parameter accepts: `anthropic`, `openai`, `local`
- [ ] Tool uses specified provider for all LLM operations
- [ ] Appropriate API keys validated before processing
- [ ] Clear error message if API key missing/invalid
- [ ] Default to `anthropic` if not specified

**Example:**
```bash
$ myDistillSkillAgent --input book.pdf \
    --llm openai \
    --output-claude-skill ExtractedSkills
```

---

### US-008: Inspect Intermediate Representation
**As a** skill curator who wants quality control  
**I want to** review the intermediate skill representation before output  
**So that** I can validate/edit skills before final formatting

**Acceptance Criteria:**
- [ ] `--output-json` parameter saves intermediate SkillDescriptor to JSON
- [ ] JSON is human-readable and well-formatted
- [ ] JSON includes all skill fields (name, what, why, how, when, etc.)
- [ ] Can re-run tool with JSON as input (future feature)
- [ ] Enables manual editing workflow

**Example:**
```bash
$ myDistillSkillAgent --input DDD.pdf --output-json ddd-skills.json

Output: ddd-skills.json
[
  {
    "name": "bounded-context",
    "description": "Define clear boundaries...",
    "what": "...",
    "why": "...",
    "how": [...],
    ...
  }
]
```

---

### US-009: Handle Extraction Errors Gracefully
**As a** user processing various input sources  
**I want to** receive clear error messages when extraction fails  
**So that** I can understand and fix the issue

**Acceptance Criteria:**
- [ ] Invalid file path: clear "file not found" error
- [ ] Unsupported format: lists supported formats
- [ ] LLM API failure: indicates which API and error type
- [ ] Malformed PDF: suggests alternative parsing options
- [ ] Zero skills extracted: warns user and suggests manual review
- [ ] All errors include actionable next steps

**Example:**
```bash
$ myDistillSkillAgent --input invalid.pdf

Error: Unable to parse PDF (possibly corrupted)
Suggestions:
  • Try re-downloading the PDF
  • Convert to text manually and use --input file.txt
  • Check if file is password-protected
```

---

### US-010: Batch Process Multiple Sources
**As a** power user building a skill library  
**I want to** process multiple input files at once  
**So that** I can efficiently build a comprehensive skill collection

**Acceptance Criteria:**
- [ ] `--input` accepts multiple files (comma-separated or glob pattern)
- [ ] Each source generates separate output files
- [ ] Outputs named after source files automatically
- [ ] Progress bar shows overall completion
- [ ] Failures in one file don't stop batch processing
- [ ] Summary report at end shows success/failure count

**Example:**
```bash
$ myDistillSkillAgent \
    --input "books/*.pdf" \
    --output-claude-skill

Processing 5 files:
  [████████████████░░] 80% (4/5)
  ✓ Clean-Code.pdf → Clean-Code.zip
  ✓ Refactoring.pdf → Refactoring.zip
  ✓ TDD.pdf → TDD.zip
  ✓ DDD.pdf → DDD.zip
  ✗ Patterns.pdf (parsing error)

Summary: 4 succeeded, 1 failed
```

---

## Verification Scenarios

### Scenario 1: BDD Book to Executable Specification Skill
**Given:** User has "Behavior-Driven Development.pdf"  
**When:** User runs:
```bash
myDistillSkillAgent --input BDD.pdf \
  --output-claude-skill BDD-ExecutableSpec \
  --output-continue-slash-command bdd-spec.md
```
**Then:**
- Both output files created successfully
- Anthropic SKILL contains "write executable specifications" skill
- Continue slash command has ReACT-structured steps
- Both outputs reference Gherkin syntax examples

### Scenario 2: Refactoring Article to Slash Command
**Given:** User has Martin Fowler's refactoring article URL  
**When:** User runs:
```bash
myDistillSkillAgent \
  --input https://refactoring.com/catalog/extract-method.html \
  --output-continue-slash-command extract-method.md
```
**Then:**
- Tool scrapes web content successfully
- Extracted skill focuses on "Extract Method" pattern
- Output includes before/after code examples
- Slash command invokable in Continue extension

### Scenario 3: Quality Check with Intermediate JSON
**Given:** User wants to verify extraction quality  
**When:** User runs:
```bash
myDistillSkillAgent --input CleanCode.pdf \
  --output-json clean-code-skills.json \
  --verbose
```
**Then:**
- User sees detailed extraction log
- JSON file contains 10+ skills
- Each skill has complete WHAT/WHY/HOW structure
- User manually reviews JSON, edits skill #5
- User re-runs with edited JSON (future: `--input clean-code-skills.json`)

---

## Success Metrics

### Functional Requirements
- [ ] Successfully parses PDF, Markdown, and Web sources
- [ ] Generates valid Anthropic SKILL packages (.zip)
- [ ] Generates valid Continue slash commands (.md)
- [ ] Supports multiple LLM providers
- [ ] Handles errors gracefully with actionable messages

### Quality Metrics
- [ ] Extraction precision: >80% skills are actionable and relevant
- [ ] Skill completeness: >90% skills have all required fields
- [ ] Format validity: 100% outputs pass schema validation
- [ ] User satisfaction: >4/5 rating in early user testing

### Performance Metrics
- [ ] PDF parsing: <30 seconds for 300-page book
- [ ] Skill extraction: <3 minutes for 300-page book
- [ ] Output generation: <5 seconds per format
- [ ] Memory usage: <2GB for typical workload

### Usability Metrics
- [ ] CLI help documentation is complete and clear
- [ ] 80% of users complete first extraction without documentation
- [ ] Error messages lead to resolution in <5 minutes
- [ ] Users can create skill library of 10+ skills in <1 hour
