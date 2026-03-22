# save-as-skill

一个三层架构的系统，用于从 AI 对话中提取可复用的技能（Skill），为 GitHub Copilot 设计，可移植到 Cline、Continue 和 Claude Code。

## 这是什么

当一段长对话解决了一个棘手的问题后，其中的知识通常会随着对话结束而消散。本技能将这些知识捕获为结构化、可复用的文件（`SKILL.md`），任何 AI 编程智能体都能自动发现并应用于类似的未来问题。

系统由三层协同工作：

| 层级 | Copilot | Cline | Continue | Claude Code |
|------|---------|-------|----------|-------------|
| **手动触发** | [`.github/prompts/save-as-skill.prompt.md`](../../prompts/save-as-skill.prompt.md) | `.clinerules` 规则 | `.continue/prompts/save-as-skill.prompt` | `.claude/commands/save-as-skill.md` |
| **自动调用** | [`.github/skills/save-as-skill/SKILL.md`](SKILL.md) | `.cline/skills/save-as-skill/SKILL.md` | `.continue/prompts/save-as-skill.prompt` | `.claude/skills/save-as-skill/SKILL.md` |
| **常驻提醒** | [`.github/instructions/save-as-skill-nudge.instructions.md`](../../instructions/save-as-skill-nudge.instructions.md) | `.clinerules` 规则 | `.continue/config.yaml` 系统消息 | `CLAUDE.md` 规则 |

附带测试/评审工具：

| 文件 | 用途 |
|------|------|
| [`scripts/generate_review.py`](scripts/generate_review.py) | 零依赖 Python 评审查看器，用于测试生成的技能 |

## 为什么需要三层

一个文件不够用，因为技能保存应该在三个不同的时机发生：

1. **用户主动保存** → 输入 `/save-as-skill` → **prompt 文件** 处理
2. **模型检测到匹配** → 自动调用 → **SKILL.md** 处理
3. **双方都没注意到** → 对话结束时提醒 → **instructions 文件** 兜底

没有提醒层，符合条件的对话会被遗漏。没有自动调用层，保存只在用户记得主动请求时才发生。三层形成一张安全网。

## 为什么要"强势描述"

Anthropic 开源的 [skill-creator](https://github.com/anthropics/skill-creator) 发现，技能的**触发不足**远比触发过度更常见。简短的描述如 `"Save conversation as skill"` 很少被激活。

解决方法：在描述中加入额外的触发短语和近似场景。我们的描述明确列出了 "save as skill"、"capture this as a skill"、"turn this into a skill" 等短语，让模型更可靠地匹配。

## 为什么要"解释原因"

传统的指令文件使用硬性规则（`ALWAYS do X`、`NEVER do Y`）。Anthropic 的研究发现 LLM 对推理的响应更好。当技能解释了某个步骤*为什么*重要时，模型会将指令适配到新的场景，而不是机械地执行然后在边界情况下出错。

## 移植到其他智能体

核心内容（步骤、示例、约束）在各智能体间完全相同，只有文件位置和 frontmatter 不同。以下展示三层分别如何对应各个智能体。

### 第一层：手动触发

用户明确要求保存技能（斜杠命令或关键词）。

**Copilot** — 已通过 `.github/prompts/save-as-skill.prompt.md` 配置好。用户输入 `/save-as-skill`。

**Cline** — 添加到 `.clinerules`：

```
# .clinerules
When the user asks to "save as skill", "capture this as a skill", or "turn this into a skill",
read and follow .github/skills/save-as-skill/SKILL.md
```

**Continue** — 创建 `.continue/prompts/save-as-skill.prompt`：

```yaml
---
name: save-as-skill
description: "Save the current conversation as a reusable skill."
invokable: true
---
```

然后将 `SKILL.md` 的正文（frontmatter 以下的全部内容）粘贴到该文件中。`invokable: true` 标志将其注册为 `/save-as-skill` 斜杠命令。

**Claude Code** — 创建 `.claude/commands/save-as-skill.md`：

```markdown
Extract a reusable skill from the current conversation.
Follow the instructions in .claude/skills/save-as-skill/SKILL.md
```

用户在 Claude Code 的提示中输入 `/save-as-skill`。

### 第二层：自动调用

模型检测到对话匹配，无需用户请求即自动调用技能。

**Copilot** — 已通过 `.github/skills/save-as-skill/SKILL.md` 配置好。frontmatter 中的 `description` 字段控制模型何时触发。

**Cline** — 复制或软链接技能：

```bash
mkdir -p .cline/skills/save-as-skill
cp .github/skills/save-as-skill/SKILL.md .cline/skills/save-as-skill/
cp -r .github/skills/save-as-skill/scripts .cline/skills/save-as-skill/
```

Cline 在 `.cline/skills/` 中发现技能，并根据描述进行匹配。

**Continue** — Continue 的 `.continue/prompts/save-as-skill.prompt` 同时用于手动和自动调用。模型读取描述后可以主动推荐。

**Claude Code** — 复制技能目录：

```bash
mkdir -p .claude/skills/save-as-skill
cp .github/skills/save-as-skill/SKILL.md .claude/skills/save-as-skill/
cp -r .github/skills/save-as-skill/scripts .claude/skills/save-as-skill/
```

Claude Code 自动发现 `.claude/skills/` 中的 `SKILL.md` 文件。

### 第三层：常驻提醒

在符合条件的对话结束时，智能体建议保存技能。

**Copilot** — 已通过 `.github/instructions/save-as-skill-nudge.instructions.md`（`applyTo: "**"`）配置好。

**Cline** — 追加到 `.clinerules`：

```
# 技能保存提醒
At the end of a conversation, if ALL of these are true:
1. More than ~10 back-and-forth exchanges
2. A clear working solution was reached
3. Non-trivial (debugging, architecture, multi-step reasoning)
4. Pattern could apply to similar future problems
Then suggest: "This conversation solved a non-trivial problem. Want to save it as a reusable skill?"
```

**Continue** — 添加到 `.continue/config.yaml` 系统消息：

```yaml
systemMessage: |
  At the end of long conversations (10+ exchanges) that solved a non-trivial,
  reusable problem, suggest saving as a skill by typing /save-as-skill.
```

**Claude Code** — 添加到项目根目录的 `CLAUDE.md`：

```markdown
## Skill-Saving Nudge

At the end of long conversations (10+ exchanges) that solved a non-trivial,
reusable problem, suggest: "Want to save this as a reusable skill?"
Then follow .claude/skills/save-as-skill/SKILL.md
```

## 使用方法

### 在 Copilot Chat 中

```
/save-as-skill
```

智能体会回顾对话、提取技能并生成 `SKILL.md`。

### 测试生成的技能

```bash
python .github/skills/save-as-skill/scripts/generate_review.py \
  my-skill-workspace/ \
  --skill-name "my-skill"
```

在浏览器中打开评审页面。留下反馈、迭代改进、重复直到满意。

### 无界面模式

```bash
python .github/skills/save-as-skill/scripts/generate_review.py \
  my-skill-workspace/ \
  --skill-name "my-skill" \
  --static /tmp/review.html
```

生成独立 HTML 文件，而非启动服务器。
