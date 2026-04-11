# AggregateGenCodeDesc — 统一语言（Ubiquitous Language）

本文档定义了代码、CLI、协议、测试和文档中使用的所有领域术语。
所有贡献者和 AI 代理必须一致使用这些术语。

---

## 1. 核心概念

| 术语 | 定义 | 出现位置 |
|---|---|---|
| **genCodeDesc** | 外部版本级元数据记录，描述提交中哪些行是 AI 生成的；通过 `repoURL + repoBranch + revisionId` 索引 | 代码、协议、CLI、文档 |
| **generatedTextDesc** | genCodeDesc 记录的协议名称；涵盖源代码和文档文本 | 协议 (`protocolName`)、代码 |
| **PROTOCOL_VERSION** | genCodeDesc 协议模式的版本化契约标识符（当前为 `"26.03"`） | 代码、协议 (`protocolVersion`) |
| **AggregateGenCodeDesc** | 分析工具本身 — 将版本级 AI 归因聚合为指定时间窗口内的仓库级结果 | 代码（模块）、文档 |
| **LiveLine** | 在 `endTime` 时仓库快照中存活（存在）的源代码/文档行；度量的基本单位 | 代码（日志标签）、文档 |
| **live changed source code** | LiveLine 的子集，指在 `startTime~endTime` 内被新增或修改的行 — 主指标的度量对象 | 文档 |
| **end snapshot** | 提交时间 ≤ `endTime` 的最新提交所对应的仓库状态；所有存活行枚举的基准 | 代码、文档 |
| **origin revision** | 通过 blame 发现的、最后引入存活行当前形式的版本 | 代码 (`origin_revision_id`)、文档 |
| **metadata identity key** | 复合键 `repoURL + repoBranch + revisionId`，用于从外部元数据存储中查找一条 genCodeDesc 记录 | 文档 (ArchDesign)、代码 |
| **line-level lookup key** | `源文件路径 + 源行号` — 在获取版本元数据后用于解析特定行的 `genRatio` | 文档 (ArchDesign)、代码 |

## 2. 指标与分类

| 术语 | 定义 | 出现位置 |
|---|---|---|
| **genRatio** | 整数 0–100，表示单行的 AI 归因百分比；100 = 完全 AI 生成，0 = 完全人工 | 协议、代码、文档 |
| **AI_Window_Live_Ratio** | 主指标公式：`Sum(line.genRatio/100 for 窗口内存活行) / 窗口内存活变更行总数` | 文档（README 公式） |
| **live_changed_source_ratio** | 主指标（算法 A 默认）的标识符字符串 — 存活变更源代码行的 AI 比率 | 代码、CLI `--metric` |
| **period_added_ai_ratio** | 算法 B 周期贡献指标的标识符字符串 — 期间*新增*行的 AI 比率 | 代码、CLI `--metric`、文档 (US-6) |
| **100%-ai** | `genRatio == 100` 的行的分类标签（完全 AI 生成） | 代码 (`describe_ratio`) |
| **N%-ai** | `0 < genRatio < 100` 的行的分类标签（部分 AI） | 代码 (`describe_ratio`) |
| **human/unattributed** | `genRatio == 0` 或无元数据的行的分类标签 | 代码 (`describe_ratio`) |
| **TransitionHint** | 尽力而为的日志诊断信息，显示行的归因如何从父版本变化到当前版本（例如 `human/unattributed→100%-ai`） | 代码（日志标签） |
| **best_effort_transition** | TransitionHint 内的格式化转换字符串（例如 `best_effort_transition=human/unattributed->100%-ai`） | 代码 (`best_effort_transition_hint`) |

### SUMMARY 计数字段

| 字段 | 定义 |
|---|---|
| **totalCodeLines** | 该提交 diff 中所有非空的新增（'+'）代码行数（不包括删除行和空行） |
| **fullGeneratedCodeLines** | 新增代码行中 `genRatio` 为 100 的子集 |
| **partialGeneratedCodeLines** | 新增代码行中 `genRatio` 在 1 到 99 之间的子集 |
| **totalDocLines** | （Scope C）作用域内可表示的文档行数 |
| **fullGeneratedDocLines** | （Scope C）`genRatio == 100` 的文档行 |
| **partialGeneratedDocLines** | （Scope C）`0 < genRatio < 100` 的文档行 |

## 3. 算法与作用域

### 算法

| 术语 | 定义 |
|---|---|
| **Algorithm A** | 主算法：基于 blame 的末端快照归因 — 通过 `git blame`/`svn blame` 解析源版本，然后与外部元数据关联 |
| **Algorithm B** | 替代增量重放算法：通过正向重放提交差异重建文件状态，然后从重建的行状态计算指标 |

### 作用域

| 术语 | 定义 |
|---|---|
| **Scope A** | 默认作用域：纯源代码 — 仅统计 `SOURCE_EXTENSIONS` 文件中的非空白、非注释行 |
| **Scope B** | 带注释的源代码 — 统计源文件中所有非空白行（包括注释） |
| **Scope C** | 文档文本 — 统计 `DOC_EXTENSIONS` 文件中所有非空白行，使用 `docLines` 协议字段 |
| **Scope D** | 全部文本 — 源代码和文档文件的联合聚合 |

### 文件扩展名集合

| 术语 | 定义 |
|---|---|
| **SOURCE_EXTENSIONS** | 识别为源代码的文件扩展名：`.c`、`.cc`、`.cpp`、`.cxx`、`.go`、`.h`、`.hpp`、`.java`、`.js`、`.py`、`.rs`、`.ts` |
| **DOC_EXTENSIONS** | 识别为文档的文件扩展名：`.md`、`.rst`、`.txt` |

### 算法 B TDD 阶段

| 阶段 | 定义 |
|---|---|
| **B0** | 契约锁定 |
| **B1** | 单分支基线 |
| **B2** | 删除/重写 |
| **B3** | 重命名 |
| **B4** | 合并感知 |
| **B5** | SVN 对等 |
| **B6** | 可扩展性门控 |

## 4. CLI 参数

| 参数 | 定义 |
|---|---|
| `--repoURL` | 逻辑仓库标识 URL（或 Git 的本地绝对路径） |
| `--repoBranch` | 目标分支（Git 分支名或 SVN 分支/主干路径） |
| `--startTime` | 分析时间窗口的起始时间（含，ISO-8601 日期） |
| `--endTime` | 分析时间窗口的结束时间（含，ISO-8601 日期） |
| `--vcsType` | 版本控制系统类型：`git` 或 `svn` |
| `--algorithm` | 算法选择器：`A`（基于 blame）或 `B`（基于重放） |
| `--metric` | 显式指标选择器（例如 `live_changed_source_ratio`、`period_added_ai_ratio`） |
| `--scope` | 作用域选择器：`A`、`B`、`C` 或 `D` |
| `--outputFile` | JSON 结果的输出路径（省略则输出到 stdout） |
| `--outputFormat` | 输出格式（目前仅支持 `json`） |
| `--metadataSource` | 元数据来源模式（目前仅支持 `genCodeDesc`） |
| `--genCodeDescSetDir` | 包含版本级 genCodeDesc JSON 文件的本地目录路径（夹具驱动的提供者） |
| `--commitDiffSetDir` | 包含算法 B 离线重放用提交差异补丁文件的本地目录路径 |
| `--workingDir` | 当 `--repoURL` 为逻辑（非本地）URL 时的本地 Git 检出路径 |
| `--failOnMissingProtocol` | 如果任何作用域内版本缺少 genCodeDesc 记录则报错 |
| `--warnOnMissingProtocol` | 当版本缺少 genCodeDesc 记录时发出警告（而非静默跳过） |
| `--includeBreakdown` | 明细粒度级别（默认 `none`） |
| `--logLevel` | 日志详细程度：`quiet`、`info` 或 `debug` |
| `--timeout` | 单命令执行超时秒数（默认 30） |
| `--maxRuntime` | 整体分析超时秒数（默认 3600） |

## 5. 协议结构

### 顶层节

| 节 | 定义 |
|---|---|
| **SUMMARY** | 聚合行计数（`totalCodeLines`、`fullGeneratedCodeLines`、`partialGeneratedCodeLines`，或文档等价物） |
| **DETAIL** | 按文件的条目数组，每个条目包含 `fileName` 和 `codeLines`/`docLines` 数组 |
| **REPOSITORY** | 仓库标识：`vcsType`、`repoURL`、`repoBranch`、`revisionId` |
| **CREDENTIAL** | 认证令牌；分析器将其视为忽略的信封元数据 |
| **WARNINGS** | 仅输出：分析期间产生的运行时警告消息数组 |

### DETAIL 子字段

| 字段 | 定义 |
|---|---|
| **fileName** | 仓库内的相对文件路径 |
| **codeLines** | 源代码文件的行级 AI 归因条目数组 |
| **docLines** | 文档文件的行级 AI 归因条目数组 |
| **lineLocation** | 具有归因 `genRatio` 的精确单行号 |
| **lineRange** | 共享同一 `genRatio` 的连续行范围（`from`/`to`） |
| **genMethod** | 行的生成方式（例如 `"codeCompletion"`、`"vibeCoding"`） |

### REPOSITORY 子字段

| 字段 | 定义 |
|---|---|
| **revisionId** | VCS 提交哈希（Git）或版本号（SVN），标识一个版本 |
| **vcsType** | `"git"` 或 `"svn"` |
| **repoURL** | 规范仓库 URL 或本地路径 |
| **repoBranch** | 产生该版本的分支名或 SVN 路径 |
| **codeAgent** | 生成 genCodeDesc 的 AI 编码代理（例如 `"HuayanCoder"`） |
| **protocolName** | 必须为 `"generatedTextDesc"` |
| **protocolVersion** | 模式版本字符串（例如 `"26.03"`） |

### 夹具文件

| 文件 | 定义 |
|---|---|
| **query.json** | 测试夹具，指定算法 B 查询输入（metric、includedRevisionIds、endRevisionId） |
| **expected_result.json** | 用于验收测试比较的黄金预期输出 |
| **`*_genCodeDesc.json`** | `genCodeDescSetDir` 中单个版本的 genCodeDesc 元数据文件 |
| **`*_commitDiff.patch`** | `commitDiffSetDir` 中单个版本的提交差异补丁文件 |

## 6. 内部实现

### 数据类

| 类 | 定义 |
|---|---|
| **BlameLine** | 一条解析后的 blame 输出条目：`revision_id`、`origin_file`、`origin_line`、`final_line`、`content` |
| **LineState** | 算法 B 重放中跟踪的一行：`content`、`origin_revision_id`、`gen_ratio` |
| **IndexedFileDetail** | 单个文件的预索引协议明细：`line_locations`（字典）和 `line_ranges`（元组列表） |
| **CommitDiffLine** | 一条解析后的差异行：`kind`（`add`/`delete`/`context`）、`content`、`old_line_number`、`new_line_number` |
| **CommitDiffHunk** | 一个解析后的差异块：`old_start`、`old_length`、`new_start`、`new_length`、`lines` |
| **CommitDiffFile** | 一个解析后的差异文件节：`old_path`、`new_path`、`hunks` |
| **ParsedCommitDiff** | 一个提交差异补丁的完整解析结果，包含 `CommitDiffFile` 列表 |
| **RevisionCommitDiff** | 一个版本的差异：`revision_id`、`parsed_patch`、可选的 `base_file_lines_by_old_path`、`parent_revision_ids`、`final_file_lines_by_new_path` |
| **CommitDiffPatchFile** | 磁盘上一个 `*_commitDiff.patch` 文件的元数据：`path`、`revision_id`、`time_seq` |

### 提供者接口

| 类 | 定义 |
|---|---|
| **GenCodeDescProvider** | 抽象基类：获取单个版本级 genCodeDesc 元数据记录的接口 |
| **CommitDiffProvider** | 抽象基类：获取单个版本原始提交差异补丁的接口 |
| **GenCodeDescSetDirProvider** | 具体实现：从本地 `*_genCodeDesc.json` 文件目录解析 genCodeDesc |
| **CommitDiffSetDirProvider** | 具体实现：从本地 `commitDiffSet/` 目录解析提交差异补丁 |
| **EmptyGenCodeDescProvider** | 具体实现：返回空元数据（将所有行视为 human/unattributed） |
| **EmptyCommitDiffProvider** | 具体实现：不返回差异（未提供 `--commitDiffSetDir` 时的哨兵值） |

### 架构组件

| 组件 | 定义 |
|---|---|
| **RepositoryAnalyzer** | 解析末端快照、列出文件、运行 blame、发现源版本 |
| **AggregationEngine** | 将 blame 发现的源版本与版本元数据关联，计算最终汇总 |
| **ResultWriter** | 输出符合协议格式的最终聚合结果 |
| **RuntimeLogger** | 结构化 stderr 日志记录器，支持 `quiet`/`info`/`debug` 级别及 `warn_once` 去重 |

### 异常层次

| 异常 | 定义 |
|---|---|
| **AggregateGenCodeDescError** | 所有领域错误的基础异常类 |
| **CommandExecutionError** | 外部命令（git/svn）执行失败 |
| **ProtocolValidationError** | genCodeDesc 元数据格式错误或不匹配 |
| **UnsupportedConfigurationError** | 请求的组合尚未实现 |
| **RepositoryStateError** | 仓库状态阻止分析（例如未找到版本） |
| **InputValidationError** | 无效的 CLI 输入 |

### 退出码

| 码 | 常量 | 含义 |
|---|---|---|
| 0 | `EXIT_SUCCESS` | 分析成功完成 |
| 1 | `EXIT_INPUT_ERROR` | 无效的 CLI 参数 |
| 2 | `EXIT_REPOSITORY_ERROR` | 仓库状态阻止分析 |
| 3 | `EXIT_PROTOCOL_ERROR` | 协议验证失败 |
| 4 | `EXIT_TIMEOUT` | 分析超过 `--maxRuntime` |

### 常量

| 常量 | 定义 |
|---|---|
| **COMMAND_TIMEOUT_SECONDS** | 默认单命令超时（30 秒） |
| **DEFAULT_MAX_RUNTIME_SECONDS** | 默认整体分析超时（3600 秒） |
| **MAX_FILE_SIZE_BYTES** | 单文件 VCS 输出硬限制（100 MB） |

## 7. 用户故事索引

| ID | 标题 |
|---|---|
| US-1 | 计算请求时间窗口内存活变更源代码的加权 AI 比率 |
| US-2 | 人工重写移除先前的 AI 归因 |
| US-3 | AI 重写替换先前的人工所有权 |
| US-4 | 已删除的 AI 行不得计入 |
| US-5 | 重命名必须保留归因谱系 |
| US-6 | 计算请求期间的 AI 新增比率（period-added 指标） |
| US-7 | 在一个请求窗口内解析混合多提交历史 |
| US-8 | 合并提交必须保留有效归因 |
| US-9 | Git 和 SVN 必须遵循相同的结果契约 |
| US-10 | 大型仓库快照必须保留结果语义 |
| US-11 | 深度历史必须保留最新有效归因 |
| US-12 | 一个窗口内的多分支合并必须保留逐行归因 |
| US-13 | Git 生产规模本地仓库门控（Heavy） |
| US-14 | SVN 生产规模本地仓库门控（Heavy） |
| US-15–19 | 算法 B TDD 扩展：单分支基线、删除/重写、重命名、合并感知、SVN 子集 |
| US-20 | Scope B：带注释的源代码 |
| US-21 | Scope C：文档文本行 |
| US-22 | Scope D：全部文本（源代码 + 文档统一） |
| US-23 | 作用域对等矩阵验证 |
| US-24–26 | 算法 B 作用域扩展：B+Scope B、B+Scope C、B+Scope D |
| US-27 | 跨算法 × 跨作用域对等矩阵 |
| US-28 | 生产就绪审计修复 |
| US-29 | Info 级日志必须显示初始加载、逐行状态转换和最终汇总 |
