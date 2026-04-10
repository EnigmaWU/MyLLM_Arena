# AggregateGenCodeDesc 使用指南

## 目的

面向操作人员的 `aggregateGenCodeDesc.py` 运行指南。

如需验收标准，请参见 `README_UserStoryNG_ZH.md`。

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
| **C**（嵌入 blame，v26.04） | Git 来源 blame | ✅ 当前切片 | — | — | — |
| **C**（嵌入 blame，v26.04） | SVN 来源 blame | ✅ 当前切片 | — | — | — |

**Algorithm A** 是推荐的生产路径，它直接操作活跃仓库的 checkout。

**Algorithm B** 通过回放 commit diff 来重建行状态。它设计了两种模式：

- **本地 Git 回放**：直接从本地 Git checkout 读取 diff
- **离线夹具回放**：从 `--commitDiffSetDir` 中读取预导出的 patch 文件（Git 和 SVN 来源的夹具在 Scope A 下均可工作）

**Algorithm C** 消费 `genCodeDescProtoV26.04` 文件中的嵌入 blame。在当前 CLI 切片中，它支持 Scope A，要求 `--genCodeDescSetDir`，运行时不调用 Git / SVN，并且可以从显式 CLI 参数或可选 `queryArgs.json` 与选中的 end-revision 协议中推导仓库身份。

## 全局前置条件

- Python 3.10+
- Git 运行需要本地已安装 Git
- SVN 运行需要本地已安装 SVN

## 各算法依赖与前置条件

### Algorithm A

- 依赖：活跃仓库访问能力 + 逐修订版 `genCodeDesc` v26.03 元数据。
- 运行前提：
  - 本地 Git checkout 或可访问的 SVN 仓库
  - Git 运行需安装 Git，SVN 运行需安装 SVN
  - `--repoURL`、`--repoBranch`、`--startTime`、`--endTime`
  - 含匹配元数据的 `--genCodeDescSetDir`
- 适合选择 A 的情况：
  - 最重视生产正确性与可解释性
  - 需要把结果直接追溯到原始 VCS 证据
  - 可以接受运行时访问仓库

### Algorithm B

- 依赖：可回放的 commit diff 流 + 逐修订版 `genCodeDesc` v26.03 元数据。
- 运行前提：
  - 本地 Git 回放时：需要本地 Git checkout 与 Git
  - 离线回放时：需要 `--commitDiffSetDir` 与 `--genCodeDescSetDir`
  - 每个被回放的修订都必须同时具备 patch 工件与对应元数据
  - `--startTime` 与 `--endTime`
  - 本地 Git 回放仍需要仓库位置（`--repoURL` 或 `--workingDir`），并且在当前 CLI 中通常仍需要 `--repoBranch`
  - 离线回放在原理上并不依赖活跃仓库访问；`--repoURL` 在当前更多用于元数据身份校验与输出身份，`--repoBranch` 更多保留为查询 / 输出上下文
- 适合选择 B 的情况：
  - 运行时必须脱离仓库，但手头已有 patch 工件
  - 希望基于同一套 diff 流做确定性历史重放、过程回溯或窗口实验
  - 团队能够接受最高的 replay 逻辑复杂度

### Algorithm C

- 依赖：带嵌入 blame 的逐修订版 `genCodeDescProtoV26.04` 文件，以及有效的 `REPOSITORY.revisionTimestamp`。
- 运行前提：
  - `--algorithm C`
  - `--genCodeDescSetDir` 中至少有一个 `*_genCodeDesc.json`
  - 每个 AlgC 协议文件都必须声明 `protocolVersion: "26.04"`
  - 当前 CLI 切片仅支持 Scope A
  - 当前切片要保证正确性，要求 surviving lines 的 DETAIL 穷尽完整
  - `--genCodeDescSetDir` 下可选放置 `queryArgs.json`，或通过 `--queryArgsFile` 指定，用于提供 `endRevisionId` 和/或仓库身份
- 适合选择 C 的情况：
  - 运行时既不能访问仓库，也不希望回放 diff
  - 部署环境是气隔、边缘节点或离线批处理流水线
  - 可以严格治理写入时协议质量，并信任嵌入 blame 的生产链路

## 参数说明

### 基础必需参数

| 参数 | 说明 |
|------|------|
| `--repoURL` | 仓库身份。对 Algorithm A 为必需。对 Algorithm B 本地 Git 回放，如果不使用 `--workingDir`，则也需要它。对 Algorithm B 离线回放，它更推荐用于元数据身份校验与输出身份，真正的回放输入仍是 `--commitDiffSetDir` + `--genCodeDescSetDir`。Algorithm C 可从显式 CLI 参数或 `queryArgs.json` 与选中的 v26.04 end protocol 推导仓库身份。 |
| `--repoBranch` | 分支名称（例如 `main`、`trunk`）。对 Algorithm A 为必需。对 Algorithm B 本地 Git 回放，它通常用于解析 end revision。对 Algorithm B 离线回放，它更适合作为查询 / 输出上下文，而非核心回放依赖。若 Algorithm C 从显式 CLI 参数或 `queryArgs.json` 与 end protocol 推导身份，则该参数可选。 |
| `--startTime` | ISO-8601 格式的开始日期（例如 `2026-03-01`）。 |
| `--endTime` | ISO-8601 格式的结束日期（例如 `2026-03-31`）。 |

### 常用参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--genCodeDescSetDir` | — | 元数据目录。对 Algorithm A/B，包含 `<revisionId>_genCodeDesc.json` 文件；对 Algorithm C，包含 `protocolVersion: "26.04"` 的 `*_genCodeDesc.json` 文件，以及可选的 `queryArgs.json`。 |
| `--outputFile` | stdout | JSON 结果输出路径。 |
| `--scope` | `A` | 统计哪些文件和行。详见下方 [Scope](#--scope)。 |
| `--algorithm` | `A` | `A` 为活跃仓库分析，`B` 为回放型分析，`C` 为嵌入 blame 的离线分析。 |
| `--vcsType` | `git` | `git` 或 `svn`。对 Algorithm A 为必需。对 Algorithm B 也仍需要，因为元数据解释和 replay 解析仍要知道场景是 Git 还是 SVN。若 Algorithm C 从显式 CLI 参数或 `queryArgs.json` 与选中的 end protocol 推导身份，则该参数可选。 |

### Algorithm B 专用

| 参数 | 说明 |
|------|------|
| `--commitDiffSetDir` | 预导出的 patch 文件目录，用于离线回放。夹具驱动的 Algorithm B 必需。必须与 `--genCodeDescSetDir` 配对使用。 |
| `--endRevisionId` | Algorithm B/C 可选的显式 end revision。若省略，运行时会按时间解析最新符合条件的修订。 |
| `--includedRevisionIds` | Algorithm B 可选的显式回放序列。若提供，该列表就是权威的回放集合 / 顺序。 |
| `--queryArgsFile` | 可选的生产侧 JSON 参数文件路径。若省略，运行时也会查找 `--genCodeDescSetDir` 中的 `queryArgs.json`。 |

Algorithm B 说明：`repoURL` 与 `repoBranch` 在不同模式下的重要性并不相同。它们在本地 Git 回放中更关键；而在离线回放中，真正的硬输入是 patch 流与匹配元数据，`repoURL` 当前主要承担元数据身份校验作用，`repoBranch` 当前主要保留为查询 / 输出上下文。

### Algorithm C 专用

| 参数 | 说明 |
|------|------|
| `--genCodeDescSetDir` | 必需。AlgC `genCodeDescProtoV26.04` 文件所在目录。当前切片只从这些文件读取嵌入 blame。 |
| `--genCodeDescSetDir` 下的 `queryArgs.json` 或 `--queryArgsFile` | 可选但推荐。可提供 `endRevisionId`、`vcsType`、`repoURL`、`repoBranch`。若提供，这些字段必须与选中的 end-revision 协议一致。 |
| `--repoURL`、`--repoBranch`、`--vcsType` | 当存在 `--genCodeDescSetDir` 时，对 Algorithm C 可选。仓库身份会从显式 CLI 值或 `queryArgs.json` 与 end-revision 协议集合中推导。 |
| `--scope` | 当前 Algorithm C 切片仅支持 Scope A。 |

### Git 逻辑 URL 模式

| 参数 | 说明 |
|------|------|
| `--workingDir` | 本地 Git checkout 路径。当 `--repoURL` 是逻辑 URL（非本地路径）且 `--vcsType` 为 `git` 时必需。SVN 不需要。 |

### 诊断与限制

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--logLevel` | `quiet` | `quiet`、`info` 或 `debug`。`info` 输出三阶段叙事：(1) `Starting analysis` 横幅，包含 repo/branch/window/endRevision；(2) 逐行 `LiveLine` 分类（例如 `LiveLine src/calc.py:3 classification=100%-ai`）和 `TransitionHint` 行，展示修订间的状态迁移（例如 `100%-ai->human/unattributed`）；(3) `Finished analysis` 总结，包含汇总数、`elapsed` 与 `costSeconds`。`debug` 在此基础上增加元数据加载、文件扫描、窗口外跳过和缓存协议复用消息。输出至 stderr。 |
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

## 如何选择算法

| 如果你的首要关注点是…… | 选择 | 原因 |
|---|---|---|
| 最低逻辑风险、最好审计性 | **Algorithm A** | live blame 仍是最权威的证据路径。 |
| 基于显式历史 diff 工件做离线回放 | **Algorithm B** | 它是唯一围绕可回放 patch 流构建的路径。 |
| 运行时既不要仓库也不要 diff replay | **Algorithm C** | 它只消费带嵌入 blame 的 v26.04 文件。 |
| 当允许运行时访问仓库时，追求全系统最稳妥的生产基线 | **Algorithm A** | 解释风险最低、协议负担最低、当前覆盖范围也最完整。 |
| 在已有 patch 导出流水线的受控离线系统里追求较好整体效果 | **Algorithm B** | 可复用 patch 工件做回放、实验与确定性复现。 |
| 在气隔或边缘部署拓扑里追求较好整体效果 | **Algorithm C** | 最小化运行时依赖与权限暴露。 |

推荐默认选择：除非你有明确的系统性理由要避免 live repository access，否则优先使用 **Algorithm A**。只有当 patch-stream replay 本身就是目标能力时才选择 **Algorithm B**。当部署模型足够受益于零仓库、零 diff 的运行时形态，并且团队能承受更严格的 v26.04 协议治理时，再选择 **Algorithm C**。

### `--commitDiffSetDir` 契约

使用 Algorithm B 的离线夹具时：

- `--commitDiffSetDir` 与 `--genCodeDescSetDir` 配对 —— 它们是同一次回放运行的 diff 侧和元数据侧。
- 每个回放修订都需要 `<timeSeq>_<revisionId>_commitDiff.patch` 和 `<revisionId>_genCodeDesc.json`。
- 如果提供了 `--includedRevisionIds` 或 `queryArgs.json.includedRevisionIds`，则该列表定义回放顺序；多余的 patch 文件会被忽略。
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

### 6. Algorithm C — 嵌入 blame 的离线分析

仅依赖 v26.04 协议文件集合运行。在当前切片中，Scope A 是受支持路径。

```bash
python3 aggregateGenCodeDesc.py \
  --algorithm C \
  --startTime 2026-03-10 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-c-out.json \
  --genCodeDescSetDir /path/to/algc-v26.04-set
```

如果 `/path/to/algc-v26.04-set/queryArgs.json` 存在，或传入了 `--queryArgsFile`，Algorithm C 可以从该文件以及选中的 end protocol 推导 `endRevisionId`、`repoURL`、`repoBranch` 与 `vcsType`。

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

### Algorithm C 输出形态（当前切片）

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.04",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 2,
    "partialGeneratedCodeLines": 1
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "https://example.local/repo/demo.git",
    "repoBranch": "main",
    "revisionId": "abc123"
  }
}
```

对 Algorithm C 而言，`REPOSITORY` 身份来自被选中的 v26.04 end-revision 协议；若提供了显式 CLI 值或 `queryArgs.json`，则会对身份字段做一致性校验。

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
| `README_UserStoryNG_ZH.md` | 下一代故事级验收标准 |
| `README_SharedUS_Convergence.md` | 生产收敛路线图（已完成） |
| `README_RunTestCase.md` | 测试运行命令 |
| `README_ArchDesign.md` | 架构与设计决策 |
| `README_UbiLang.md` | 统一语言词汇表 |
