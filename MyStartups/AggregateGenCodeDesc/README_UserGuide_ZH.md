# AggregateGenCodeDesc 使用指南

## 目的

面向操作人员的 `aggregateGenCodeDesc.py` 运行指南。

如需验收标准和路线图，请参见 `README_UserStory.md` 和 `README_SharedUS_Convergence.md`。

## 快速开始

使用默认设置（Algorithm A、Scope A）分析本地 Git 仓库：

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL /path/to/local/git/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

以下所有示例均假设从项目目录运行：

```bash
cd /path/to/AggregateGenCodeDesc
```

## 当前支持矩阵

| 算法 | VCS | Scope A | Scope B | Scope C | Scope D |
|------|-----|---------|---------|---------|---------|
| **A**（活跃仓库） | Git | ✅ 生产 | ✅ 生产 | ✅ 生产 | ✅ 生产 |
| **A**（活跃仓库） | SVN | ✅ 生产 | ✅ 生产 | ✅ 生产 | ✅ 生产 |
| **B**（回放，本地 Git） | Git | ✅ 已支持 | ✅ 已支持 | ✅ 已支持 | ✅ 已支持 |
| **B**（回放，离线夹具） | Git | ✅ 已支持 | ✅ 已支持 | ✅ 已支持 | ✅ 已支持 |
| **B**（回放，离线夹具） | SVN | ✅ 已支持 | — | — | — |

**Algorithm A** 是推荐的生产路径，它直接操作活跃仓库的 checkout。

**Algorithm B** 通过回放 commit diff 来重建行状态。它设计了两种模式：

- **本地 Git 回放**：直接从本地 Git checkout 读取 diff
- **离线夹具回放**：从 `--commitDiffSetDir` 中读取预导出的 patch 文件（Git 和 SVN 来源的夹具在 Scope A 下均可工作）

## 前置条件

- Python 3.10+
- Git 运行需要本地已安装 Git
- SVN 运行需要本地已安装 SVN

## 参数说明

### 每次运行都必需

| 参数 | 说明 |
|------|------|
| `--repoURL` | 仓库身份。对 Git，可以是本地路径（`/path/to/repo`）或逻辑 URL（`https://...`）。对 SVN，是服务器或 `file:///` URL。 |
| `--repoBranch` | 分支名称（例如 `main`、`trunk`）。 |
| `--startTime` | ISO-8601 格式的开始日期（例如 `2026-03-01`）。 |
| `--endTime` | ISO-8601 格式的结束日期（例如 `2026-03-31`）。 |

### 常用参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--genCodeDescSetDir` | — | 包含 `<revisionId>_genCodeDesc.json` 元数据文件的目录。每个文件内的 `REPOSITORY` 块必须与 CLI 的 `--repoURL` 一致。 |
| `--outputFile` | stdout | JSON 结果输出路径。 |
| `--scope` | `A` | 统计哪些文件和行。详见下方 [Scope](#--scope)。 |
| `--algorithm` | `A` | `A` 为活跃仓库分析，`B` 为回放型分析。 |
| `--vcsType` | `git` | `git` 或 `svn`。 |

### Algorithm B 专用

| 参数 | 说明 |
|------|------|
| `--commitDiffSetDir` | 预导出的 patch 文件目录，用于离线回放。夹具驱动的 Algorithm B 必需。必须与 `--genCodeDescSetDir` 配对使用。 |

### Git 逻辑 URL 模式

| 参数 | 说明 |
|------|------|
| `--workingDir` | 本地 Git checkout 路径。当 `--repoURL` 是逻辑 URL（非本地路径）且 `--vcsType` 为 `git` 时必需。SVN 不需要。 |

### 诊断与限制

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--logLevel` | `quiet` | `quiet`、`info` 或 `debug`。`info` 输出三阶段叙事：(1) `Starting analysis` 横幅，包含 repo/branch/window/endRevision；(2) 逐行 `LiveLine` 分类（例如 `LiveLine src/calc.py:3 classification=100%-ai`）和 `TransitionHint` 行，展示修订间的状态迁移（例如 `100%-ai->human/unattributed`）；(3) `Finished analysis` 总结，包含汇总数和耗时。`debug` 在此基础上增加元数据加载、文件扫描、窗口外跳过和缓存协议复用消息。输出至 stderr。 |
| `--timeout` | `30` | 单条命令超时秒数（每个 `git blame`、`git show` 等）。 |
| `--maxRuntime` | `3600` | 整体分析超时秒数。 |
| `--warnOnMissingProtocol` | 关 | 当某修订的元数据文件缺失时以降级模式继续运行；在输出中写入 `WARNINGS` 条目。 |
| `--failOnMissingProtocol` | 关 | 当某修订的元数据文件缺失时立即失败。 |

### `--scope`

控制结果中包含哪些文件类型和行类型。

| Scope | 包含的文件 | 统计的行 | 输出字段 |
|-------|-----------|---------|---------|
| **A**（默认） | 源代码文件（`.c`、`.cc`、`.cpp`、`.cxx`、`.go`、`.h`、`.hpp`、`.java`、`.js`、`.py`、`.rs`、`.ts`） | 仅代码行（排除注释和空行） | `totalCodeLines`、`fullGeneratedCodeLines`、`partialGeneratedCodeLines` |
| **B** | 源代码文件 | 所有非空行（含注释） | `totalCodeLines`、`fullGeneratedCodeLines`、`partialGeneratedCodeLines` |
| **C** | 文档文件（`.md`、`.rst`、`.txt`） | 非空行，使用协议中的 `docLines` 字段 | `totalDocLines`、`fullGeneratedDocLines`、`partialGeneratedDocLines` |
| **D** | 源代码文件 + 文档文件 | 两者的所有非空行；源代码用 `codeLines`，文档用 `docLines` | `totalCodeLines`、`fullGeneratedCodeLines`、`partialGeneratedCodeLines` |

Scope 与算法选择正交。Scope 控制 **统计什么**；算法控制 **如何计算行来源归因**。

### `--commitDiffSetDir` 契约

使用 Algorithm B 的离线夹具时：

- `--commitDiffSetDir` 与 `--genCodeDescSetDir` 配对 —— 它们是同一次回放运行的 diff 侧和元数据侧。
- 每个回放修订都需要 `<timeSeq>_<revisionId>_commitDiff.patch` 和 `<revisionId>_genCodeDesc.json`。
- 如果 `query.json` 提供了 `includedRevisionIds`，则该列表定义回放顺序；多余的 patch 文件会被忽略。
- 否则，文件名中的 `<timeSeq>` 前缀决定回放顺序。
- 遗留的 `<revisionId>_commitDiff.patch` 命名对旧夹具仍有效，但新夹具应使用带时间序列的格式。
- 同一目录中不要混用遗留和时间序列命名。
- Patch 文件可以来源于 Git 或 SVN 历史，但必须是 unified diff 格式。

## 典型用法示例

### 1. Git + Algorithm A（生产）

最常见的情况：分析本地 Git 仓库。

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL /path/to/local/git/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

如需统计文档行而非代码行，将 `--scope A` 改为 `--scope C`。
如需统计全部（源代码 + 文档），使用 `--scope D`。

### 2. Git + Algorithm A 逻辑 URL 模式

当元数据使用逻辑 URL 但 Git 命令需对本地 checkout 执行时：

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/demo.git \
  --workingDir /path/to/local/git/checkout \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

### 3. SVN + Algorithm A（生产）

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///path/to/local/svn/repo \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

也可以使用 SVN 服务器 URL（例如 `svn://host/repo`）替代 `file:///`。

### 4. Algorithm B — 本地 Git 回放

从活跃 Git checkout 回放 commit diff。

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL /path/to/local/git/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-b-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

Scope B、C、D 同样支持 —— 只需更改 `--scope`。

### 5. Algorithm B — 离线夹具回放

从预导出的 patch 文件回放。不需要访问活跃仓库。

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/demo \
  --repoBranch main \
  --startTime 2026-03-10 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-b-fixture-out.json \
  --genCodeDescSetDir testdata/us1_live_changed_source_ratio \
  --commitDiffSetDir testdata/us1_live_changed_source_ratio/commitDiffSet
```

SVN 来源的夹具在 Scope A 下同样可用 —— 只需改为 `--vcsType svn` 并指向 SVN 夹具目录。

## 输出形态

### Scope A、B 或 D

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 2,
    "partialGeneratedCodeLines": 1
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/path/to/repo",
    "repoBranch": "main",
    "revisionId": "abc123"
  }
}
```

### Scope C

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalDocLines": 4,
    "fullGeneratedDocLines": 2,
    "partialGeneratedDocLines": 1
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/path/to/repo",
    "repoBranch": "main",
    "revisionId": "abc123"
  }
}
```

### 可选的 `WARNINGS` 字段

当启用 `--warnOnMissingProtocol` 且某修订的元数据缺失时，输出中会包含：

```json
{
  "WARNINGS": [
    "Protocol file not found for revision abc122 in /path/to/genCodeDescSet; treating affected lines as human/unattributed"
  ]
}
```

## 常见问题与修复办法

### `--workingDir is required for git`

你使用了逻辑 `--repoURL`（例如 `https://...`）但没有指定本地 checkout 路径。

**修复：** 添加 `--workingDir /path/to/local/git/checkout`。

### `Metadata repoURL mismatch`

元数据 JSON 内的 `REPOSITORY.repoURL` 与你的 CLI `--repoURL` 不匹配。

**修复：** 确保两者为完全相同的字符串。

### `Protocol file not found for revision`

`--genCodeDescSetDir` 中缺少某个 `<revisionId>_genCodeDesc.json` 文件。

**修复：** 补上缺失的文件，或使用 `--warnOnMissingProtocol` 以降级模式继续运行。

### `Commit diff patch file not found`

Algorithm B 期望的某个 patch 文件不在 `--commitDiffSetDir` 中。

**修复：** 补上缺失的 `<timeSeq>_<revisionId>_commitDiff.patch`。

### `--scope must be one of: A, B, C, D`

Scope 值无效（例如小写 `a` 或 `Z`）。

**修复：** 使用大写 `A`、`B`、`C` 或 `D`。

### `--vcsType must be one of: git, svn`

**修复：** 使用 `git` 或 `svn`。

### `File ... exceeds ... byte limit`

仓库中某个文件超过 100 MB。这很可能是不应被当作源代码跟踪的二进制或生成文件。

**修复：** 将该文件排除在跟踪之外，或检查是否误提交。

## 退出码

| 退出码 | 含义 |
|--------|------|
| `0` | 成功 |
| `1` | 输入校验错误（参数错误） |
| `2` | 仓库访问错误（git/svn 命令失败） |
| `3` | 协议/元数据错误（JSON 格式错误、字段缺失） |
| `4` | 超时（超过 `--maxRuntime`） |

## 延伸阅读

| 文档 | 内容 |
|------|------|
| `README.md` | 产品范围与指标定义 |
| `README_UserStory.md` | 故事级验收标准 |
| `README_SharedUS_Convergence.md` | 生产收敛路线图 |
| `README_RunTestCase.md` | 测试运行命令 |
| `README_ArchDesign.md` | 架构与设计决策 |
| `README_UbiLang.md` | 统一语言词汇表 |
