# AggregateGenCodeDesc

## ======>>>我们已有的前提<<<======

- 我们把代码提交到 GIT/SVN 仓库。
- 每当一个修订创建完成后，会有独立流程为该修订生成一条 `genCodeDesc` 记录，用于描述哪些代码行由 AI 生成。
- `genCodeDesc` 不是仓库内容，而是存储在独立数据库或服务中的外部元数据，并由 `repoURL + repoBranch + revisionId` 索引。
  - 协议定义见：[genCodeDescProtocol](genCodeDescProtocol.json)

## ======>>>我们想要达到的目标<<<======

- 我们希望计算在某个特定时间段内发生变更、并且在结束时仍然存活的代码行中，AI 相关代码所占的比例。
  - 例如：计算 RepoA:branchB 在 `[2026-03-01, 2026-03-31]` 这个时间窗口内，当前仍然存活且在该窗口内发生变更的代码行中的 AI 占比。

## ======>>>相关文档<<<======

- 用户故事与验收标准：`README_UserStory.md`
- 使用指南与典型命令示例：`README_UserGuide_ZH.md`
- 共享故事收敛路线图（已完成）：`README_SharedUS_Convergence.md`
- 架构设计：`README_ArchDesign.md`
- 统一语言词汇表：`README_UbiLang_ZH.md`
- 测试运行指南：`README_RunTestCase.md`
- 基于场景的测试夹具：`testdata/`

## ======>>>快速开始<<<======

如果你是第一次使用这个仓库，请先看 `README_UserGuide_ZH.md`。

当前最常见的命令模式如下：

### Git 真实仓库运行：`Algorithm A`

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

### SVN 真实仓库运行：`Algorithm A`

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///path/to/local/svn/repo \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

### 狭义回放运行：`Algorithm B`

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/demo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-b-out.json \
  --genCodeDescSetDir testdata/us1_live_changed_source_ratio \
  --commitDiffSetDir testdata/us1_live_changed_source_ratio/commitDiffSet
```

如果你需要更多示例、参数说明和常见报错处理，请看 `README_UserGuide_ZH.md`。

## ======>>>生产验证分层<<<======

- 当前实现的生产目标仍然是 `Algorithm A + Scope A` 在 Git 与 SVN 上达到生产质量。
- 验证模型应显式分成 `Fast` 与 `Heavy` 两层。
- `Fast` 验证适用于日常本地运行与普通 CI，使用夹具驱动检查和短时仓库测试。
- `Heavy` 验证适用于生产就绪性与每日集成运行，使用长时或生产规模的仓库历史。
- 当前专用的长时生产 gate 是 `bash run_production_gate.sh`，它运行 `US-13` Git 与 `US-14` SVN 的生产规模验收测试。

## ======>>>如何得到这个结果<<<======

### 1. 指标的精确定义

对于给定的 `repo + branch + [startTime, endTime]`，当前主指标是：

`时间窗口 [startTime, endTime] 内发生变更且在 endTime 仍然存活的代码行中的 AI 占比`

它的含义是：

- 取该分支上提交时间 `<= endTime` 的最后一个提交对应的快照。
- 观察该快照中当前仍然存活的代码行。
- 只保留那些“当前版本是在 `startTime~endTime` 期间新增或修改”的存活代码行。
- 对于每一条这样的存活代码行，判断该行当前版本由 AI 生成了多少。
- 对这些存活变更代码行的 AI 贡献部分求和。
- 再除以同一窗口内所有存活变更代码行的总数。

公式：

`AI_Window_Live_Ratio = Sum(line.genRatio / 100 for live lines whose current origin revision is in [startTime, endTime]) / Total_Live_Changed_Lines_In_Window`

说明：

- `genRatio = 100` 表示整行完全由 AI 生成。
- `genRatio = 30` 表示该行有 30% 归因于 AI。
- 这是加权比例，不只是简单的 AI/人工二值计数。
- 该指标仍然是在 `endTime` 的活跃代码快照上计算。
- `startTime` 不只是标签，它决定哪些存活代码行属于统计范围。

### 2. 推荐的计算模型

`Algorithm A（首选）：基于 blame 的 end-snapshot 归因`

最直接的一线模型是：`end snapshot + blame + window filter + 外部元数据查找`

步骤如下：

1. 解析 `endCommit`：
   a) 即 `branchB` 上提交时间 `<= endTime` 的最后一个提交。
2. 获取 `endCommit` 中的文件列表。
   a) 这是有意为之：该指标只考虑 `endTime` 最终存活快照里仍然存在的文件。
   b) 在 `startTime~endTime` 期间发生过变更、但在 `endTime` 之前已删除的文件，按设计不计入。
3. 对 `endCommit` 中的每个源码文件执行 blame，并开启 rename/move 检测。
   a) 如果文件发生过重命名或移动，但在 `endTime` 仍存在，那么支持 rename 的 blame 应能保留其行来源。
4. 对每一条最终存活代码行，收集：
   - 最终文件路径
   - 最终行号
   - 来源提交 id
   - 来源文件路径
   - 来源行号
5. 过滤掉所有 `origin commit id` 时间不在 `startTime~endTime` 范围内的存活代码行。
6. 从外部元数据提供者中获取这些来源提交对应的 `genCodeDesc` 记录。
7. 用 `origin file path + origin line number` 查找对应的 AI 元数据。
8. 如果找到，则使用对应的 `genRatio`；否则视为 `0`。
9. 对剩余存活变更代码行的 AI 权重求和，再除以剩余存活变更代码行的总数。

这个模型成立的原因是：blame 回答的正是核心问题：`当前这条存活代码行的当前形态，最后是由哪个提交引入的？`
一旦知道了这个来源修订，就可以精确地把时间窗口应用到最终存活代码行集合上。

### 3. 为什么这个模型符合需求

需求并不是：`统计该时间段内曾经被 AI 添加过多少代码，而不管这些代码后来是否还存在`。
而是：`在 endTime 时刻仍然存活的代码中，startTime~endTime 内发生变更的那部分代码里，有多少是 AI 生成或部分由 AI 生成的`。

因此：

- 已删除的代码行不能计入。
- 旧版本代码行不能计入。
- 当前版本是在 `startTime` 之前形成的存活代码行不能计入。
- 只有最终分支快照中那些“当前版本是在窗口内新增或修改”的存活代码行才计入。

### 4. 行归属规则

为了让指标稳定，必须明确行归属规则。

- 如果一条 AI 生成的代码行后来被人类修改，那么这条代码行应归属于引入当前文本的新提交。
- 如果一条人类编写的代码行后来被 AI 重写，那么这条代码行应归属于新的 AI 相关提交。
- 如果一条代码行被删除，它就不再参与比例计算。
- 如果文件发生重命名或移动，行归属应通过 blame 的 rename 检测得到保留。
- 如果一条代码行被复制到另一个文件，这是产品策略问题：
  - 保守模式：复制后的代码行视为在复制提交中新引入。
  - 谱系模式：如果工具能证明复制关系，则保留原始来源。

第一版实现中，rename tracking 是必要的。copy tracking 可以作为可选增强。

### 5. startTime 的作用

对于当前已确认的主指标，`startTime` 是指标定义的一部分。

这意味着：

- 一条存活代码行只有在“最后一次引入其当前形态的修订”落在 `startTime~endTime` 内时才属于统计范围。
- 当前形态来自 `startTime` 之前的存活代码行不属于统计范围。
- 已删除的代码行不属于统计范围，因为它们在 `endTime` 时已不再存活。

### 6. 候选模型

当前有两个候选模型：

- `Algorithm A（首选）：基于 blame 的 end-snapshot 归因`
  - 方法：
    - 从 `endTime` 的存活快照出发
    - 用 blame 找到每条最终存活代码行的来源修订
    - 再按 `startTime~endTime` 过滤
  - 优点：
    - 与当前主指标直接吻合，因为该指标本身就是定义在 `endTime` 的存活快照上
    - 实现更简单，因为 VCS 已经能计算行谱系
    - rename 处理通常更容易，因为成熟的 blame 实现通常已经支持
    - 对 P0 而言逻辑风险更低，因为不需要自己重建窗口内每个提交后的行状态
  - 缺点：
    - 如果仓库很大、文件很多，blame 可能较慢
    - 严重依赖 VCS blame 的质量和行为
    - 不太适合处理已删除代码、churn 或中间历史状态类指标

- `Algorithm B（备选）：不依赖 blame 的增量谱系重建`
  - 方法：
    - 从 `startTime` 之前的快照出发
    - 一路重放 snapshot diff 和逐提交 diff，直到 `endTime`
    - 持续维护一张行状态映射表，直到重建出最终存活快照
  - 优点：
    - 能支持更丰富的历史过程分析，例如 AI 新增后又删除、churn、存活率、逐提交报告等
    - 如果时间窗口很窄，而 `endTime` 时的完整仓库很大，性能上可能更优
    - 如果系统已经有成熟的增量 diff 处理流水线或事件日志，也可能更容易接入
  - 缺点：
    - 实现明显更难，因为分析器必须正确处理插入、删除、重写、rename 和行号偏移
    - 正确性风险更高，因为本质上是在自己重建一个部分 blame 引擎
    - merge 处理和跨 VCS 一致性更困难
    - 单靠最终的 `start->end` diff 不够，必须逐提交重放，才能得到正确的存活行归属

什么情况下备选模型可能更合适：

- 产品需要的是历史过程指标，而不仅是最终存活快照指标
- 分析窗口很小，但最终仓库快照非常大
- 提交 diff 已经被良好索引且查询便宜，而 blame 很慢或运维成本高
- 团队除了最终比例，还希望得到逐提交的归因结果

什么情况下 blame 模型仍然更合适：

- 主要目标是当前已确认的 `P0 / Scope A` 指标
- 相比更丰富的历史分析，更看重正确性和实现简单度
- 目标 VCS 环境中存在可靠的 rename-aware blame

按照当前项目方向，应将 `Algorithm A` 作为实现基线，并保留 `Algorithm B` 作为显式备选架构。

### 7. 什么算作代码行

这一点必须在规格中固定，否则不同工具算出的比例会漂移。

建议的范围定义与优先级如下：

- `P0 / Scope A: pure source code`
  - 只包含选定语言下被跟踪的源码文件
  - 只包含代码行
  - 排除空行
  - 排除纯注释行
  - 排除生成文件
  - 排除 vendored 第三方代码
  - 排除二进制文件
- `P1 / Scope B: source code with comments`
  - 包含选定语言下被跟踪的源码文件
  - 包含源码文件内的代码行和注释行
  - 排除独立文档文件
  - 排除生成文件
  - 排除 vendored 第三方代码
  - 排除二进制文件
- `P2 / Scope C: documentation text lines`
  - 包含 Markdown、纯文本、README、设计文档、规格、prompt 及类似文档型文本文件
  - 排除源码文件，除非产品明确把它们当作文档资产
  - 如果产品定义如此，生成文档可以选择纳入，以衡量被接受的 AI 文档内容
- `P2 / Scope D: all text`
  - 包含源码、源码注释和文本文档
  - 也可以按产品策略选择性包含 JSON、YAML、SQL、配置、模板等其他文本资产
  - 排除二进制文件

第一版实现中，Scope A 是主指标。
Scope B 是第二优先级扩展。
Scope C 和 Scope D 是后续可加的更宽统计视图，而不改变核心行来源算法。

### 8. 必要的数据前提

该设计假定每个相关修订在外部元数据存储中都有一条 `genCodeDesc` 记录，并且该记录可以通过 `repoURL + repoBranch + revisionId` 解析出来。

当前第一版本地测试切片只是使用文件来模拟这一外部元数据契约。
这些文件并不是目标生产存储模型。

协议应尽量保持简洁。
它首先是一个 AI 生成代码说明文档，而其 `SUMMARY` 部分已经足够被复用于最终聚合报告。

协议必须能回答：

- 描述了哪些文件
- 哪些行或行范围由 AI 生成
- 每一行的 `genRatio`
- 这些元数据所属的精确仓库修订
- 该修订或快照的聚合统计结果是什么

分析器应当把仓库历史和 `genCodeDesc` 元数据存储视为两个不同系统：

- 仓库回答哪些代码行仍然存活，以及哪个修订最后引入了它们的当前形态
- 外部元数据存储回答某个具体修订中的代码行有多少可归因于 AI

当前协议示例已经包含完成这些目标所需的关键字段。

`SUMMARY` 中建议保留的聚合字段包括：

- `totalCodeLines`
- `fullGeneratedCodeLines`
- `partialGeneratedCodeLines`

这些字段建议采用如下语义：

- `totalCodeLines`：只统计当前记录所表示的代码行，不包含已经删除、因而不再被该记录表示的历史代码行。对于修订级 `genCodeDesc`，它表示该修订快照中被该记录描述的代码行数。对于当前最终聚合指标，它表示 `endTime` 时仍然存活、且其当前形态是在 `startTime~endTime` 内新增或修改的源码行数。
- `fullGeneratedCodeLines`：当前记录所表示代码行中，`genRatio = 100` 的行数。
- `partialGeneratedCodeLines`：当前记录所表示代码行中，`0 < genRatio < 100` 的行数。

像 weighted AI lines、AI ratio、AI ratio percent 这样的派生值，如果能由 summary totals 和详细行元数据计算得到，则不需要强制写入协议。

像 `metric`、`startTime`、`endTime` 或 credentials 这样的字段，如果它们属于外部查询或运行环境，而不是生成代码描述本身，则不必写入协议。

为了支持跨 VCS，仓库部分建议使用：

- `vcsType`: `git` 或 `svn`
- `revisionId`: Git commit hash 或 SVN revision number

`commitID` 可以暂时作为 Git 兼容字段保留，但长期标准字段应是 `revisionId`。

在目标生产架构里，实际查找键应为：

- `repoURL`
- `repoBranch`
- `revisionId`

### 9. 输出示例

单个协议文档中的 summary 字段示例：

- 窗口内当前仍然存活且属于统计范围的代码行总数：`2,480`
- 完全由 AI 生成的存活变更代码行数：`900`
- 部分由 AI 生成的存活变更代码行数：`410`

基于这些字段以及详细的 `genRatio` 条目，分析器可以在需要时计算加权 AI 行数和最终比例。

可选 breakdown：

- 按 `genMethod`，例如 `codeCompletion`、`vibeCoding` 等

### 10. 实务结论

因此，这个目标指标可以被精确定义为：

`在请求时间段结束时，在指定分支快照中，那些当前版本是在 startTime~endTime 内新增或修改、并且在 endTime 时仍然存活的代码行中，有多少比例可归因于 AI 生成？`

如果现在开始实现，第一版应采用：

- `endTime` 时刻的 Git 快照
- 用 blame 找到存活代码行的来源
- 按每条存活代码行当前来源修订做时间窗口过滤
- 先通过 `repoURL + repoBranch + origin revisionId` 做外部元数据查找，再用 `origin file + origin line` 查找行级元数据
- 基于 `genRatio` 做加权聚合

## ======>>>CLI 工具设计<<<======

推荐第一版工具名：

- `aggregateGenCodeDesc.py`

目的：

- 接收仓库目标和时间窗口作为输入
- 计算约定好的聚合指标
- 输出机器可读结果文件，以及可选的人类可读摘要

推荐命令形态：

```bash
python aggregateGenCodeDesc.py \
  --repoURL <repo_url> \
  --repoBranch <branch_name> \
  --startTime <yyyy-mm-dd> \
  --endTime <yyyy-mm-dd>
```

第一版必须参数：

- `--repoURL`
  - 要分析的仓库 URL 或仓库标识
- `--repoBranch`
  - 用于 Git 风格分析的分支名
  - 对于 SVN，这里也可映射为 `trunk` 或 `branches/release-1.0` 之类的路径
- `--startTime`
  - 包含式窗口起始日期，格式为 `yyyy-mm-dd`
- `--endTime`
  - 包含式窗口结束日期，格式为 `yyyy-mm-dd`

推荐可选参数：

- `--vcsType <git|svn>`
  - 如果工具能从 `repoURL` 自动识别，则此参数可选
- `--algorithm <A|B>`
  - 默认：`A`
  - `A` 表示基于 blame 的 end-snapshot 归因
  - `B` 表示不依赖 blame 的增量谱系重建
- `--scope <A|B|C|D>`
  - 默认：`A`
  - `A` 纯源码
  - `B` 源码 + 注释
  - `C` 文档文本行
  - `D` 全部文本
- `--outputFile <path>`
  - 将聚合结果 JSON 写入文件
- `--outputFormat <json|text>`
  - 默认：`json`
- `--metadataSource <provider>`
  - 选择如何解析修订级别的 `genCodeDesc`
  - 当前默认值：`genCodeDesc`
  - 在当前切片中，应保持为 `genCodeDesc`
- `--genCodeDescSetDir <dir>`
  - 本地测试专用适配方式，用于从一个目录中解析一组修订级别的 `genCodeDesc` 文件
  - 这适用于夹具与离线测试，但不是目标生产存储模型
- `--commitDiffSetDir <dir>`
  - 面向 `Algorithm B` 的本地适配方式，用于从一个目录中解析一组预先计算好的逐提交原始 patch 工件
  - 推荐命名契约：每个需要回放的修订对应一个 `<timeSeq>_<revisionId>_commitDiff.patch` 文件，以便离线回放顺序在工件集合中显式可见
  - 它是 diff 数据源覆盖项，不是 `--repoURL` 的替代品
  - 当前只允许与 `--algorithm B` 一起出现
  - 当前边界：针对 `US-6` 这种单文件、单分支的 Git 离线 Algorithm-B 基线已经可执行
  - 当前已显式拒绝的场景包括：首个 patch 涉及多个文件、首个 patch 含多个 hunk 的基线重建、回放过程中发生文件路径变化，以及 merge 感知归因
  - 更宽的 Algorithm-B 场景，例如删除、重命名、多文件回放、merge 感知归因，当前 CLI 路径仍未实现
- `--workingDir <path>`
  - 本地 checkout 或临时工作目录
  - 当 `--repoURL` 是 `https://...` 这类逻辑仓库标识而不是本地绝对路径时，Git 目前仍要求提供该参数
  - 通过 `--commitDiffSetDir` 进入当前这条窄化的 `Algorithm B` 离线 diff 基线路径时，可以避免本地 Git 历史访问
- `--failOnMissingProtocol`
  - 如果缺少所需的修订级协议文件则立即失败
- `--includeBreakdown <genMethod|directory|none>`
  - 可选的额外汇总维度

推荐默认行为：

- 默认使用 `Algorithm A`
- 默认使用 `Scope A`
- 默认输出 JSON
- 解析 `endTime` 对应的分支快照
- 从仓库历史中发现相关的来源修订
- 从配置好的元数据提供者中获取修订级别的 `genCodeDesc`
- 计算 `[startTime, endTime]` 内存活代码行的聚合指标

推荐结果形态：

- 每次运行输出一个聚合结果文档
- 使用协议形态的 JSON 输出，其中包含：
  - 仓库身份
  - 查询窗口
  - 所选 model 与 scope
  - summary totals
  - 可选 breakdowns
  - 执行过程警告，例如缺少协议文件

推荐命令示例：

Git 示例：

```bash
python aggregateGenCodeDesc.py \
  --repoURL https://example.com/repo.git \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31
```

带显式选项的 Git 示例：

```bash
python aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.com/repo.git \
  --repoBranch release/1.0 \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm A \
  --scope A \
  --outputFile out.json
```

SVN 示例：

```bash
python aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL https://svn.example.com/repos/project \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile out.json
```

SVN 分支路径示例：

```bash
python aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL https://svn.example.com/repos/project \
  --repoBranch branches/release-1.0 \
  --startTime 2026-03-01 \
  --endTime 2026-03-31
```

第一版实现建议：

- 只实现 `Algorithm A`
- 只实现 `Scope A`
- 只强制要求 `--repoURL`、`--repoBranch`、`--startTime`、`--endTime`
- 仅把 `--genCodeDescSetDir` 保留为本地测试适配方式
- 当前切片里，`metadataSource=genCodeDesc` 是唯一启用的模式
- 生产路径可在后续再围绕以 `repoURL + repoBranch + revisionId` 为键的外部元数据提供者演进
- 其余参数保持可选，以便 CLI 保持收敛且便于测试
