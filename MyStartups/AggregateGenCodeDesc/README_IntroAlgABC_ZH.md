# AggregateGenCodeDesc — Algorithm A、B、C 简介

## 目的

本文档介绍 AggregateGenCodeDesc 中已实现或计划实现的三种归因算法，
说明每种算法解决了什么问题、输入是什么，以及各自仍存在哪些局限。

三种算法的共同目标完全一致：

> 对于在 `endTime` 时仍存活于最终仓库快照中、且其当前形态在 `[startTime, endTime]` 内产生的源代码行，
> 有多少可以归因于 AI？

三种算法的区别在于**如何发现每行的来源**——而非度量什么。

---

## 一图速览

```mermaid
mindmap
  root((AggregateGenCodeDesc))
    Algorithm A
      blame-based end-snapshot
      需要实时 VCS 访问
      git blame / svn blame
      genCodeDesc v26.03
      今日生产质量
    Algorithm B
      diff replay without blame
      commitDiffSet 工件
      genCodeDesc v26.03
      支持离线
      正确性风险较高
    Algorithm C
      embedded blame
      仅需 genCodeDesc v26.04
      零 VCS 访问
      增量 add/delete DETAIL
      计划中
```

| | **Algorithm A** | **Algorithm B** | **Algorithm C** |
|---|---|---|---|
| 核心技术 | 实时 `git/svn blame` | 离线 diff 重放 | genCodeDesc 中嵌入的 `blame` |
| 运行时是否需要仓库访问 | **需要** | 不需要 | **不需要** |
| genCodeDesc 版本 | v26.03 | v26.03 | **v26.04** |
| DETAIL 完整性要求 | 仅 AI 行 | 仅 AI 行 | **增量：每次提交的 add + delete** |
| 生产状态 | 生产质量 | 窄化回放路径已激活 | 计划中 |
| 正确性权威来源 | VCS blame（权威） | 重建的部分 blame 引擎（存在风险） | codeAgent 写入时（可信但消费时不可独立验证） |

---

## Algorithm A — 基于 Blame 的 End-Snapshot 归因

### 是什么

Algorithm A 是主要的、生产质量的基线算法。
它从 `endTime` 时的存活文件快照出发，对每条存活源代码行运行 `git blame` 或 `svn blame`，
利用 blame 结果发现每行当前形态最后是由哪个提交引入的。
来源提交落在 `[startTime, endTime]` 内的行处于度量范围内。
对于每条范围内的行，Algorithm A 从匹配的逐修订版 `genCodeDesc`（v26.03）记录中查找 `genRatio`。

### 数据流

```mermaid
flowchart TD
    Q[Query\nrepoURL · repoBranch · startTime · endTime]
    Q --> RA[RepositoryAnalyzer]
    RA --> S[解析 endTime 时的 end snapshot\n列出存活源文件]
    S --> B[运行 git blame / svn blame\n支持重命名检测\n按存活文件逐一执行]
    B --> F[过滤：保留 blame timestamp\n落在 startTime~endTime 内的行]
    F --> R[得到 distinct origin revisionId 集合]
    R --> P[GenCodeDescProvider\n按 revisionId 获取 genCodeDesc v26.03]
    P --> J[AggregationEngine\n按 origin file+line 查找 genRatio]
    F --> J
    J --> O[SUMMARY 输出\ntotalCodeLines · fullGenerated · partialGenerated]
```

### 解决了什么问题

- 直接回答 live snapshot 上的 P0 度量。
- 重命名与移动检测由成熟的 VCS blame 实现负责处理。
- 逻辑风险低：blame 是行来源的权威来源，无需部分重建。
- 同时支持 Git 与 SVN。

### 局限（Pitfalls）

| 局限 | 说明 |
|---|---|
| 需要实时仓库访问 | 运行时必须存在本地 checkout。当前实现不会自动 clone 或 fetch 远程仓库。当 `--repoURL` 是逻辑 URL 时，需要提供 `--workingDir`。 |
| 大型仓库中 blame 性能可能较慢 | `git/svn blame` 按存活文件逐一运行。文件数量多、文件体积大时速度可能较慢。 |
| 依赖 VCS blame 质量 | blame 的正确性取决于 VCS 实现。带有复杂 mergeinfo 或 path-copy 历史的 SVN blame 可能返回不精确的结果。 |
| 每个 origin revision 均需 genCodeDesc | blame 发现的每个来源修订版本都必须存在一份 v26.03 文件。缺失的记录被视为未归因，而非报错。 |
| 远程传输超出当前范围 | 网络访问型远程仓库客户端尚未经过验证。 |

---

## Algorithm B — 无需 Blame 的增量谱系重建

### 是什么

Algorithm B 通过重放一组有序的提交 diff patch（`commitDiffSet`）
来增量重建每行的所有权。
它不向 VCS 询问"谁最后改了这行？"，而是按顺序应用 diff，
追踪每条存活行是由哪个提交引入的。
运行时不需要访问实时仓库。

### 数据流

```mermaid
flowchart TD
    Q[Query\nrepoURL · repoBranch · startTime · endTime]
    Q --> CDP[CommitDiffSetDirProvider\n加载有序 diff patch 文件]
    CDP --> D1[revision r1 的 diff patch]
    CDP --> D2[revision r2 的 diff patch]
    CDP --> DN[revision rN 的 diff patch]
    D1 & D2 & DN --> RE[Replay Engine\napply_commit_diff_file_to_line_states\n按顺序逐修订版执行]
    RE --> LS[最终 line-state 映射\n存活行 + origin revisionId]
    LS --> F[过滤：保留 origin revision timestamp\n落在 startTime~endTime 内的行]
    F --> P[GenCodeDescProvider\n按 revisionId 获取 genCodeDesc v26.03]
    P --> J[AggregationEngine\n按 origin file+line 查找 genRatio]
    F --> J
    J --> O[SUMMARY 输出\ntotalCodeLines · fullGenerated · partialGenerated]
```

### 解决了什么问题

- 支持无实时仓库 checkout 的离线分析。
- 当 blame 速度慢或不可用时提供替代路径。
- Diff 工件可预先索引并低成本查询。
- 可计算超出 live-snapshot 范围的历史过程度量。
- 在测试环境中支持确定性重放。

### 局限（Pitfalls）

| 局限 | 说明 |
|---|---|
| 正确性风险更高 | Algorithm B 实际上重建了一个部分 blame 引擎。重放逻辑中的任何缺口都会静默产生错误归因。 |
| 需要预先准备 commitDiffSet 工件 | 每个被重放修订版本均需一份 unified-diff patch 文件。缺失 patch 会导致契约快速失败。 |
| 感知 merge 的谱系重放较复杂 | 为 merge 提交选择合理的 first-parent 与 merged-parent 贡献统计策略并非易事。在为 merge 密集型历史主张生产就绪之前，必须有显式 TDD 支撑。 |
| SVN 对等覆盖有限 | SVN path-copy 与 mergeinfo 语义引入的重放边界情况尚未完全覆盖。 |
| 可扩展性尚未独立验证 | 不得将 Algorithm A 的生产就绪性证据用于 Algorithm B。需要专属的可扩展性门禁。 |
| 仍需每修订版 genCodeDesc v26.03 | 与 Algorithm A 相同的元数据依赖；仅消除了 blame 步骤。 |

---

## Algorithm C — 嵌入 Blame 的纯 genCodeDesc 方案

### 是什么

Algorithm C 是一种计划中的离线算法，运行时**不需要仓库访问，也不需要 diff 工件**。
codeAgent 只记录每次提交中**新增**或**删除**的行，并将真实的 `git blame` / `svn blame`
信息嵌入每条新增行条目，写入 `genCodeDescProtoV26.04.json` 文件。
这些嵌入的 blame 必须直接来自写入时捕获的 VCS blame 输出，
不能来自后续推断、重放重建或人工编辑。
由于每条新增行都携带 `blame.revisionId`、`blame.originalFilePath`、
`blame.originalLine` 和 `blame.timestamp`，
下游消费方可将所有 `endTime` 之前的文件按顺序累积，得到完整的存活行集合，
再完成 `[startTime, endTime]` 过滤并读取 `genRatio`——无需 VCS、无需 diff。

DETAIL 是**增量式**的：每个提交文件仅记录该次提交的 `changeType=add` 和
`changeType=delete` 条目。
本次提交新增的人工编写行以 `genRatio=0 / genMethod=Manual` 记录。
本次提交删除的行仅需其 blame 来源（revisionId + originalFilePath + originalLine）
即可从累积集合中移除。

### 数据流

```mermaid
flowchart TD
    W[codeAgent 在提交时\ngit blame / svn blame\n仅处理变更行]
    W --> GCD["genCodeDescProtoV26.04.json\nREPOSITORY.revisionTimestamp = 提交时间\n增量 DETAIL：\n• changeType=add：blame + genRatio/genMethod\n• changeType=delete：仅 blame 来源"]

    subgraph Runtime["Algorithm C 运行时（零 VCS 访问）"]
        SET["全部 genCodeDesc v26.04 文件"] --> SORT["按 REPOSITORY.revisionTimestamp 升序排列\n处理 revisionTimestamp <= endTime 的文件"]
        SORT --> ACC["累积 surviving_lines 映射\n键：(revisionId, originalFilePath, originalLine)\n→ 每文件先处理 delete，再处理 add"]
        ACC --> F["过滤 surviving_lines\nblame.timestamp ∈ [startTime, endTime]"]
        F --> AI[AI 行：genRatio > 0\n统计 full / partial]
        F --> HU[Manual 行：genRatio = 0\n仅统计 total]
        AI & HU --> O[SUMMARY 输出\ntotalCodeLines · fullGenerated · partialGenerated]
    end

    GCD -.->|"存入文件集"| SET
```

### 解决了什么问题

- 分析时零 VCS 访问——无 checkout、无子进程、无网络。
- 每次提交文件体积小：仅记录变更行，而非全量快照。
- 与 Algorithm A 和 Algorithm B 度量语义完全相同。
- 同时支持 git 来源与 svn 来源的 blame（VCS 类型作为嵌入元数据）。
- 气隔或边缘部署场景：分析仅需一组 v26.04 文件。

### 局限（Pitfalls）

| 局限 | 说明 |
|---|---|
| 需要 `endTime` 之前的**全部** genCodeDesc 文件 | AlgC 必须处理从初始提交到 endRevision 的所有文件以累积存活行集合。链中缺失任一文件将导致结果错误。 |
| `REPOSITORY.revisionTimestamp` 为必填项 | AlgC 使用此字段排序并确定处理哪些文件。缺少此字段，AlgC 无法确定处理顺序。 |
| delete 条目必须精确匹配 blame 来源 | `blame.revisionId + originalFilePath + originalLine` 必须与之前的 add 条目完全一致。不匹配将静默地在累积集合中留下幽灵行。 |
| 嵌入 blame 必须是真实 VCS blame | AlgC 假设嵌入的 blame 直接来自写入时真实执行的 `git blame` 或 `svn blame` 输出。合成、推断或人工编辑的 blame 会破坏 AlgC 契约。 |
| blame 准确性依赖 codeAgent | 消费时的正确性完全信任 codeAgent 写入时的 blame 调用结果。分析过程中无法独立进行 VCS 验证。 |
| add 条目的 lineRange 约束 | lineRange 条目仅在该范围内所有行共享同一 blame 来源时才合法。blame 来源不同的行必须各自使用独立条目。 |
| 无法检测过期 blame | 如果 codeAgent 生成 genCodeDesc 文件后仓库发生了 force-push 或 amend，嵌入的 blame 将静默过期。 |
| 实现尚未启动 | Algorithm C 仅处于计划阶段。协议形态定义于 `genCodeDescProtoV26.04.json`，尚无运行时实现。 |

---

## 三种算法的关系

```mermaid
flowchart LR
    subgraph Input["运行时输入"]
        R[(实时仓库\ngit / svn)]
        D[(commitDiffSet\n有序 patch 文件)]
        J[(genCodeDescProtoV26.04\n增量 DETAIL + 嵌入 blame)]
    end

    subgraph Meta["逐修订版 genCodeDesc"]
        M03[(genCodeDesc v26.03\n仅 AI 行)]
        M04[(genCodeDesc v26.04\n增量 add/delete + blame)]
    end

    subgraph Algs["算法"]
        A[Algorithm A\n实时 blame]
        B[Algorithm B\ndiff 重放]
        C[Algorithm C\n嵌入 blame]
    end

    R --> A
    M03 --> A
    D --> B
    M03 --> B
    J --> C
    M04 --> C

    A --> OUT[SUMMARY\ntotalCodeLines\nfullGenerated\npartialGenerated]
    B --> OUT
    C --> OUT
```

三种算法对相同场景**语义等价**。
选择哪种算法取决于可用的输入和可接受的权衡：

```mermaid
flowchart TD
    Start([开始：选择算法]) --> Q1{运行时可访问\n实时仓库？}
    Q1 -->|是| Q2{blame 性能\n可接受？}
    Q1 -->|否| Q3{commitDiffSet\n工件已准备？}
    Q2 -->|是| AlgA[✅ Algorithm A\n首选基线]
    Q2 -->|否| Q3
    Q3 -->|是| Q4{存在 merge 密集型\n历史？}
    Q3 -->|否| Q5{已有 genCodeDesc v26.04\n且 DETAIL 为增量 add/delete？}
    Q4 -->|否| AlgB[⚠️ Algorithm B\n离线重放]
    Q4 -->|是，有 TDD 支撑| AlgB
    Q5 -->|是| AlgC[🔬 Algorithm C\n计划中 · 零 VCS]
    Q5 -->|否| Block[❌ 无法继续\n输入不足]
```

---

## 总结：每种算法尚未解决的问题

| | **Algorithm A** | **Algorithm B** | **Algorithm C** |
|---|---|---|---|
| 无需实时仓库 | ❌ | ✅ | ✅ |
| 无需 diff 工件 | ✅ | ❌ | ✅ |
| 正确性权威来源 | VCS blame（最高） | 重建的部分 blame（中等） | codeAgent 写入时（可信但消费时不可独立验证） |
| 大规模 merge 密集型历史 | ✅ | ⚠️ 每种拓扑需专属 TDD | ✅（blame 在写入时已解析） |
| 大型仓库性能风险 | blame 可能较慢 | 长时间窗口重放可能较慢 | 仅文件解析——随 DETAIL 行数线性扩展 |
| 远程仓库支持 | ⚠️ 尚未验证 | ✅（无需 VCS） | ✅（无需 VCS） |
| 生产状态 | ✅ 生产质量 | ⚠️ 窄化路径已激活 | 🔬 计划中 |
