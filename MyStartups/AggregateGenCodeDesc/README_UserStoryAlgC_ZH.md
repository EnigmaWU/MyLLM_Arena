# AggregateGenCodeDesc — Algorithm C 用户故事

## 目的

本文档定义 **Algorithm C**（`AlgC`）的用户故事。

Algorithm C 是一种离线、无需访问仓库的归因算法。
它仅使用 `genCodeDescProtoV26.04.json` 文件，即可得到与 Algorithm A 和 Algorithm B 相同的度量结果
——无需访问实时仓库、无需调用 blame 子进程、无需重放 diff。

关键使能机制是 codeAgent 在写入时为 `DETAIL` 中每一行嵌入的 `blame` 对象。
由于每条存活行都携带 `blame.revisionId`、`blame.originalFilePath`、`blame.originalLine`
以及 `blame.timestamp`，下游分析器可以直接从文件中完成 `startTime~endTime` 过滤和 `genRatio` 读取，
无需访问任何 VCS。

嵌入的 blame 信息必须在写入时直接来自真实的 `git blame` 或 `svn blame` 输出。
任何合成、推断、重放重建或人工改写的 blame 数据都不属于 AlgC 契约。
两种来源均被明确支持。`REPOSITORY.vcsType` 字段（`git` 或 `svn`）以及
`blame.revisionId` 格式（Git SHA 与 SVN 修订号如 `r12345`）
使消费方无需访问仓库即可区分来源 VCS。

## 协议前提条件

所有 AlgC 故事均要求 `protocolVersion: "26.04"` 且 **DETAIL 必须完整**：
文件中每一条存活行都必须出现在 `codeLines`（或 `docLines`）中，
包括以 `genRatio=0 / genMethod=Manual` 表示的人工编写行。
`genCodeDescProtoV26.03.json` 输入不满足 AlgC 的要求。

## 与 Algorithm A 和 Algorithm B 的关系

| 属性 | Algorithm A | Algorithm B | Algorithm C |
|---|---|---|---|
| 仓库访问 | 实时 `git/svn blame` | 离线 diff 重放 | 无 |
| 输入 | 仓库 + 逐修订版 genCodeDesc v26.03 | commitDiffSet + 逐修订版 genCodeDesc v26.03 | 逐修订版 genCodeDesc **v26.04** 仅此 |
| blame 来源 | VCS 子进程 | diff patch 重建 | DETAIL 中嵌入的 `blame` 对象 |
| DETAIL 完整性要求 | 否（仅 AI 行） | 否（仅 AI 行） | **是**（全部存活行） |
| VCS 支持 | git 与 svn | git 与 svn | git 来源与 svn 来源 blame |
| 度量语义 | 相同 | 相同 | 相同 |

## 故事规则

1. 每个故事遵循 `WHO` / `WHEN` / `WHAT` / `WHY` / `Story` / `Support` / `Status` / `Anchors` 格式。
2. 验收标准使用纯 `GIVEN / WHEN / THEN` 形式，配故事本地 ID。
3. 每个声明与 Algorithm A 或 Algorithm B 对等的故事必须写明对应的 USNG 故事 ID。
4. `tier=Heavy` 故事必须在至少一条验收标准中写明具体规模下限。

## 故事 ID 约定

```
USNG-ALGC-HISTORY-<C>-SCOPE-<D>-<NN>: 标题
```

- `HISTORY-<C>`：`SIMPLE` | `COMPLICATED` | `COMPLEX`
  - `SIMPLE`：线性基线、直接对等契约、仅 scope 变更契约
  - `COMPLICATED`：覆写、删除、重命名、感知 merge 的流程
  - `COMPLEX`：大文件集、深历史、多分支汇聚、生产规模（≥10 000 提交，≥100 分支）
- `SCOPE-<D>`：`A` | `B` | `C` | `D`
- 无 `REPO` 维度：Algorithm C 没有实时仓库依赖。
- 无 `GENCODEDESC` 维度：始终为本地 `genCodeDescProtoV26.04` 文件。

---

## 通用故事不变式

以下不变式适用于所有 AlgC 故事，除非故事卡中有明确覆盖。

- `UI-PROTOCOL`：结果必须是包含 `protocolName`、`protocolVersion`、`SUMMARY` 和 `REPOSITORY` 字段的合法协议形态输出。
- `UI-GOLDEN`：结果必须与该场景已批准的 golden 输出一致。
- `UI-BLAME-MANDATORY`：每条 DETAIL 条目必须携带包含 `revisionId`、`originalFilePath`、`originalLine` 和 `timestamp` 的 `blame` 对象。缺失或不完整的 `blame` 对象是协议违规，不得产生部分结果。
- `UI-BLAME-REAL-VCS`：嵌入的 `blame` 必须来自写入时真实执行的 `git blame` 或 `svn blame` 输出。合成、推断、重放重建或人工修改的 blame 数据不属于 AlgC 契约。
- `UI-EXHAUSTIVE-DETAIL`：文件中每条存活行都必须列在 DETAIL 中。仅当 `protocolVersion` 确认为 `"26.04"` 时，缺失行才被视为 `genRatio=0`。
- `UI-PARITY`：对于相同的仓库场景，Algorithm C 必须与 Algorithm A 和 Algorithm B 产生相同的 `SUMMARY` 计数。
- `UI-VCS-AGNOSTIC-CONSUMPTION`：Algorithm C 在运行时不调用任何 VCS 工具。VCS 来源（git 或 svn）仅通过 `REPOSITORY.vcsType` 和 `blame.revisionId` 格式传递。
- `UI-ALG-C-BOUNDARY`：附加在 `HISTORY-COMPLICATED` 或 `HISTORY-COMPLEX` 故事上的 AlgC 证据仅覆盖该故事的已批准场景，不代表对所有复杂或高复杂度历史形态的宽泛支持。

---

## HISTORY-SIMPLE 故事

### USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-01: 仅使用 genCodeDesc 计算存活变更源代码的加权 AI 占比

- `WHO`：仓库分析员
- `WHEN`：查询 `startTime~endTime` 时间窗口时，手头仅有 `genCodeDescProtoV26.04` 文件，无仓库 checkout
- `WHAT`：计算 `blame.timestamp` 落在请求窗口内的源代码行的加权 AI 占比
- `WHY`：在无需访问仓库的情况下，重现与 Algorithm A 相同的存活变更度量结果
- `Story`: As a repository analyst, I want to calculate the weighted AI ratio for live source-code lines using only `genCodeDescProtoV26.04` files, so that I can reproduce the Algorithm A result without a live repository.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`：计划中。尚无实现。协议形态定义于 `genCodeDescProtoV26.04.json`。对等目标：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01`。
- `Anchors`: `TestdataNG-ALGC-HISTORY-SIMPLE-SCOPE-A-01-GIT`, `TestdataNG-ALGC-HISTORY-SIMPLE-SCOPE-A-01-SVN`

**AC-01** — *核心离线度量契约*

- GIVEN 一份包含完整 DETAIL 的 `endRevision` `genCodeDescProtoV26.04` 文件
- WHEN 分析器过滤 `blame.timestamp` 落在 `[startTime, endTime]` 内的 DETAIL 条目
- THEN 结果 `SUMMARY` 仅统计这些在范围内的行及其 `genRatio` 值

**AC-02** — *Manual 行计入总数但不计入 AI 分子*

- GIVEN `blame.timestamp` 在范围内、`genRatio=0`、`genMethod=Manual` 的 DETAIL 条目
- WHEN 分析器汇总在范围内的行
- THEN 这些行使 `totalCodeLines` 增加，但不影响 `fullGeneratedCodeLines` 或 `partialGeneratedCodeLines`

**AC-03** — *时间窗口外的行从分子与分母中同时排除*

- GIVEN `blame.timestamp` 落在 `[startTime, endTime]` 之外的 DETAIL 条目
- WHEN 分析器汇总最终结果
- THEN 这些行不出现在 `totalCodeLines`、`fullGeneratedCodeLines` 或 `partialGeneratedCodeLines` 中

**AC-GIT-01** — *git 来源 blame 对等*

- GIVEN 一份 `REPOSITORY.vcsType` 为 `git`、`blame.revisionId` 为 Git SHA 的 `genCodeDescProtoV26.04` 文件
- WHEN 执行 Algorithm C
- THEN `SUMMARY` 与等效场景下 Algorithm A Git golden 结果一致

**AC-SVN-01** — *svn 来源 blame 对等*

- GIVEN 一份 `REPOSITORY.vcsType` 为 `svn`、`blame.revisionId` 为 SVN 修订号（如 `r12345`）的 `genCodeDescProtoV26.04` 文件
- WHEN 执行 Algorithm C
- THEN `SUMMARY` 与等效场景下 Algorithm A SVN golden 结果一致

---

### USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-08: Git 来源与 SVN 来源必须遵循相同的结果契约

- `WHO`：仓库分析员
- `WHEN`：验证 Algorithm C 对 git 来源与 svn 来源 blame 数据产生相同的结果语义
- `WHAT`：确认 `REPOSITORY.vcsType` 不改变结果语义；仅 `blame.timestamp` 和 `genRatio` 驱动度量
- `WHY`：Algorithm C 在消费时必须与 VCS 无关；来源 VCS 仅是元数据
- `Story`: As a repository analyst, I want Algorithm C to produce the same result semantics for git-origin and svn-origin blame data, so that VCS type does not affect the attribution contract.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`：计划中。对等目标：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08`。
- `Anchors`: `TestdataNG-ALGC-HISTORY-SIMPLE-SCOPE-A-08-GIT`, `TestdataNG-ALGC-HISTORY-SIMPLE-SCOPE-A-08-SVN`

**AC-01** — *相同场景、不同 VCS 来源，结果相同*

- GIVEN 描述同一逻辑场景的两份 `genCodeDescProtoV26.04` 文件——一份携带 `vcsType=git` blame，一份携带 `vcsType=svn` blame
- WHEN 对各自执行 Algorithm C
- THEN 两份结果的 `SUMMARY` 计数相同

**AC-02** — *无论 vcsType 为何，均不调用任何 VCS 工具*

- GIVEN `REPOSITORY.vcsType` 为 `git` 或 `svn`
- WHEN Algorithm C 处理文件
- THEN 仅读取嵌入的 `blame` 字段，不调用任何 git 或 svn 子进程

---

## HISTORY-COMPLICATED 故事

### USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-02: 人工覆写消除原有 AI 归因

- `WHO`：仓库分析员
- `WHEN`：一次人工修订在 `endTime` 之前覆写了原本归因于 AI 的代码
- `WHAT`：该行嵌入的 `blame` 反映后来的人工修订；归因重置为 Manual
- `WHY`：防止旧的 AI 所有权附着在已被覆写的代码上
- `Story`: As a repository analyst, I want a human rewrite of a previously AI-generated line to reset attribution to Manual via the embedded `blame.timestamp`, so that old AI ownership does not persist in the Algorithm C result.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`：计划中。对等目标：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02`。
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-02`

**AC-01** — *人工覆写通过 blame 消除原有 AI 归因*

- GIVEN 一行，其 `blame.revisionId` 指向 `[startTime, endTime]` 内的人工提交（`genRatio=0 / genMethod=Manual`）
- WHEN 分析器处理该 DETAIL 条目
- THEN 该行仅计入 `totalCodeLines`，不计入任何 AI 计数器

**AC-GIT-01** — *git 来源人工覆写对等*

- GIVEN 与 `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02` 相同的场景，使用 git blame 来源
- WHEN 执行 Algorithm C
- THEN `SUMMARY` 与 Algorithm A Git golden 结果一致

**AC-SVN-01** — *svn 来源人工覆写对等*

- GIVEN 使用 svn blame 来源的相同场景
- WHEN 执行 Algorithm C
- THEN `SUMMARY` 与 Algorithm A SVN golden 结果一致

---

### USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-03: AI 覆写替代原有人工所有权

- `WHO`：仓库分析员
- `WHEN`：后来的 AI 修订覆写了原本由人工编写的行
- `WHAT`：该行嵌入的 `blame` 反映 AI 修订；AI 归因生效
- `WHY`：确保 `endTime` 时的存活快照反映最新的 AI 贡献
- `Story`: As a repository analyst, I want a later AI rewrite of a human line to become the effective attribution source via the embedded `blame`, so that Algorithm C reflects the latest AI contribution without repository access.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`：计划中。对等目标：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03`。
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-03`

**AC-01** — *后来的 AI 修订通过 blame 成为有效归因来源*

- GIVEN 一行，其 `blame.revisionId` 指向 `[startTime, endTime]` 内的 AI 提交（`genRatio > 0`）
- WHEN 分析器处理该 DETAIL 条目
- THEN 该行同时计入 `totalCodeLines` 和对应的 AI 计数器

**AC-GIT-01** — *git 来源 AI 覆写对等*

- GIVEN 与 `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03` 相同的场景，使用 git blame 来源
- WHEN 执行 Algorithm C
- THEN `SUMMARY` 与 Algorithm A Git golden 结果一致

**AC-SVN-01** — *svn 来源 AI 覆写对等*

- GIVEN 使用 svn blame 来源的相同场景
- WHEN 执行 Algorithm C
- THEN `SUMMARY` 与 Algorithm A SVN golden 结果一致

---

### USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-04: 已删除行不得计入结果

- `WHO`：仓库分析员
- `WHEN`：某些行在时间窗口内曾经存在，但在 `endRevision` 的 genCodeDesc DETAIL 中已不存在
- `WHAT`：这些行不出现在结果中
- `WHY`：已删除行在完整 DETAIL 中的缺席即代表删除；无需访问仓库即可确认
- `Story`: As a repository analyst, I want deleted lines to be invisible to Algorithm C by their absence from exhaustive DETAIL, so that the result reflects only the surviving live snapshot.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`：计划中。对等目标：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04`。
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-04`

**AC-01** — *已删除行因缺席于完整 DETAIL 而被排除*

- GIVEN 一份 `genCodeDescProtoV26.04` 文件，其完整 DETAIL 仅覆盖 `endRevision` 时的存活行
- WHEN 分析器处理 DETAIL
- THEN 不存在已删除行条目可供统计；删除通过缺席隐式表达

**AC-GIT-01** — *git 来源删除行对等*

- GIVEN 与 `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04` 相同的场景，使用 git blame 来源
- WHEN 执行 Algorithm C
- THEN `SUMMARY` 与 Algorithm A Git golden 结果一致

**AC-SVN-01** — *svn 来源删除行对等*

- GIVEN 使用 svn blame 来源的相同场景
- WHEN 执行 Algorithm C
- THEN `SUMMARY` 与 Algorithm A SVN golden 结果一致

---

### USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-05: 重命名或移动通过 originalFilePath 透明处理

- `WHO`：仓库分析员
- `WHEN`：文件在其原始修订与 `endRevision` 之间发生了重命名或移动
- `WHAT`：`blame.originalFilePath` 正确记录原始修订中的文件路径；重命名无需访问仓库即可解析
- `WHY`：正确归因要求重命名透明；Algorithm C 不得为此调用 VCS 子进程
- `Story`: As a repository analyst, I want renamed or moved files to be attributed correctly via `blame.originalFilePath`, so that Algorithm C handles rename history without repository access.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`：计划中。对等目标：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05`。
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-05`

**AC-01** — *重命名文件的 originalFilePath 与 fileName 不同*

- GIVEN 一条 `blame.originalFilePath` 与父级 `fileName` 不同的 DETAIL 条目
- WHEN 分析器读取 blame 归因
- THEN 以 `blame.originalFilePath` 和 `blame.originalLine` 作为规范来源键，与 Algorithm A blame 契约一致

**AC-02** — *重命名文件中的行被正确归因*

- GIVEN 重命名文件中一行，其 `blame.timestamp` 落在 `[startTime, endTime]` 内
- WHEN Algorithm C 汇总在范围内的行
- THEN 该行以其 `genRatio` 被正确计入，不受重命名影响

**AC-GIT-01** — *git 来源重命名对等*

- GIVEN 与 `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05` 相同的重命名场景，使用 git blame 来源
- WHEN 执行 Algorithm C
- THEN `SUMMARY` 与 Algorithm A Git golden 结果一致

**AC-SVN-01** — *svn 来源重命名对等（SVN path-copy 语义）*

- GIVEN 使用 svn blame 来源的相同场景（SVN path-copy 语义）
- WHEN 执行 Algorithm C
- THEN `SUMMARY` 与 Algorithm A SVN golden 结果一致

---

### USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-07: Merge 提交必须保留每行有效归因

- `WHO`：仓库分析员
- `WHEN`：在 `endTime` 之前，已合并分支将人工与 AI 贡献带入目标分支
- `WHAT`：每条存活行通过 `blame` 保留其有效来源修订的归因，不受 merge 形态影响
- `WHY`：merge 提交不得重置或扁平化每行来源；Algorithm C 结果中不得出现此类失真
- `Story`: As a repository analyst, I want merged branches to preserve per-line effective attribution via embedded `blame`, so that Algorithm C does not flatten ownership to merge commits or branch labels.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`：计划中。对等目标：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-07`。
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-07`

**AC-01** — *Merge 不覆盖嵌入的 blame*

- GIVEN 存活行来自不同已合并分支，且各自在 DETAIL 中携带准确的 `blame`
- WHEN Algorithm C 处理文件
- THEN 遵循每行嵌入的 `blame.revisionId` 与 `blame.timestamp`，不折叠为 merge 提交身份

**AC-02** — *跨已合并分支的每行独立性*

- GIVEN 多个分支在 `endTime` 之前被合并，存活行来自不同已合并分支
- WHEN Algorithm C 汇总在范围内的行
- THEN 独立保留每条存活行，不按合并顺序或分支标签扁平化

---

## HISTORY-COMPLEX 故事

### USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-09: 大文件集必须保留结果语义

- `WHO`：仓库分析员
- `WHEN`：`endRevision` genCodeDesc 覆盖包含大量文件和存活行的大型仓库
- `WHAT`：Algorithm C 在规模下正确处理所有 DETAIL 条目并产生正确的 SUMMARY
- `WHY`：生产仓库有大型文件集；正确性必须在规模下成立
- `Story`: As a repository analyst, I want Algorithm C to remain correct across a large file set so that result semantics are preserved at production scale.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`：计划中。对等目标：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-09`。
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLEX-SCOPE-A-09`

**AC-01** — *大文件集产生唯一正确结果*

- GIVEN 一份覆盖数百个文件、数千条存活行的完整 DETAIL `genCodeDescProtoV26.04` 文件
- WHEN Algorithm C 计算最终结果
- THEN 产生唯一一份仓库级 SUMMARY，计数与 golden 结果一致

**AC-02** — *结果语义与文件数量无关*

- GIVEN 相同场景在小规模和大规模下分别执行
- WHEN 对两种情况执行 Algorithm C
- THEN 每行归因逻辑完全相同，与文件数量无关

---

### USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-10: 深历史必须保留最新有效归因

- `WHO`：仓库分析员
- `WHEN`：存活行的来源修订分布在很长的提交历史中（数千次提交之深）
- `WHAT`：Algorithm C 无论来源修订距今多远，均遵循每行的 `blame.timestamp`
- `WHY`：深历史不得扭曲每行归因；嵌入的 blame 对所有深度同等有效
- `Story`: As a repository analyst, I want deep commit history to be transparent to Algorithm C via embedded blame, so that lines from old revisions and recent revisions are attributed equally correctly.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`：计划中。对等目标：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-10`。
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLEX-SCOPE-A-10`

**AC-01** — *旧来源行被正确排除*

- GIVEN 一条存活行，其 `blame.timestamp` 早于 `startTime`
- WHEN Algorithm C 按时间窗口过滤
- THEN 该行被排除在结果之外（不在范围内）

**AC-02** — *近期来源行被正确计入*

- GIVEN 一条存活行，其 `blame.timestamp` 落在 `[startTime, endTime]` 内
- WHEN Algorithm C 按时间窗口过滤
- THEN 无论来源修订与 `endRevision` 之间存在多少次提交，该行均以其 `genRatio` 被计入

---

### USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-11: 多已合并分支必须保留每行归因

- `WHO`：仓库分析员
- `WHEN`：在一个请求窗口内，大量分支被合并到目标分支，最终 genCodeDesc 以各自的 blame 来源覆盖所有存活行
- `WHAT`：无论有多少已合并分支贡献了存活行，Algorithm C 均保留每行归因
- `WHY`：多分支仓库在使用 Algorithm C 时不得产生归因失真
- `Story`: As a repository analyst, I want branch-heavy history to be transparent to Algorithm C via embedded blame, so that integrating many feature branches does not distort the final result.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`：计划中。对等目标：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-11`。
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLEX-SCOPE-A-11`

**AC-01** — *跨多个已合并分支的每行独立性*

- GIVEN 存活行来自大量不同的已合并分支，各自携带独立的 `blame.revisionId` 和 `blame.timestamp`
- WHEN Algorithm C 处理完整 DETAIL
- THEN 独立归因每一行，不按合并顺序、分支标签或合并层次扁平化所有权

---

## 重型生产门禁

以下故事是生产规模正确性门禁。它们验证在真实重负载下、使用由生产规模仓库生成的 genCodeDesc 文件时，结果语义仍然得到保留。

### USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-12: Git 生产规模 genCodeDesc 在分支密集历史下必须保持正确

- `WHO`：仓库分析员
- `WHEN`：验证 Algorithm C 对由大型分支密集 Git 仓库生成的 `genCodeDescProtoV26.04` 文件的生产就绪性
- `WHAT`：在处理源自生产规模 Git 仓库的完整 DETAIL 时，保持 Algorithm C 的正确性与性能
- `WHY`：证明 Algorithm C 能够处理源自 ≥10 000 次提交、≥100 个分支的仓库生成的文件，且不出现正确性或性能退化
- `Story`: As a repository analyst, I want Algorithm C to remain correct and performant when processing genCodeDesc files derived from production-scale Git repositories with ≥10 000 commits and ≥100 branches, so that it is production-ready for real-world Git histories.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin` | `tier=Heavy`
- `Status`：计划中。尚无实现。对应 AlgA 门禁 `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12`。
- `Anchors`: `TestsNG-ALGC-HISTORY-COMPLEX-SCOPE-A-12-GIT`

**AC-GIT-01** — *规模下限：≥10 000 次提交，≥100 个分支*

- GIVEN 一份完整 DETAIL `genCodeDescProtoV26.04` 文件，源自具有 ≥10 000 次提交、≥100 个分支、以及在 `endTime` 之前反复发生特性分支→集成分支→发布分支 merge 汇聚的 Git 仓库
- WHEN Algorithm C 计算最终结果
- THEN 产生唯一一份仓库级 SUMMARY，计数与 golden 结果一致

**AC-GIT-02** — *深 Git 历史中有效来源得到保留*

- GIVEN 存活行通过混合直接 merge、集成分支和阶段性汇聚到达发布分支，各自在 DETAIL 中携带准确的 `blame`
- WHEN Algorithm C 解析归因
- THEN 基于每行嵌入的 `blame.revisionId` 和 `blame.timestamp`，而非 merge 形态或分支命名

**AC-GIT-03** — *正确性与可扩展性同时验证*

- GIVEN 重型 Git 生产规模场景成功完成
- WHEN 评估验收结果
- THEN 同时验证最终汇总结果的正确性，以及处理时间相对于 DETAIL 总行数的可接受扩展性

**AC-GIT-04** — *与 Algorithm A Git 生产门禁对等*

- GIVEN `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12` 所使用的相同场景
- WHEN 对等效 `genCodeDescProtoV26.04` 文件执行 Algorithm C
- THEN `SUMMARY` 与 Algorithm A golden 结果一致

---

### USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-13: SVN 生产规模 genCodeDesc 在分支与 Merge 压力下必须保持正确

- `WHO`：仓库分析员
- `WHEN`：验证 Algorithm C 对由大型 SVN 仓库在分支与 merge 压力下生成的 `genCodeDescProtoV26.04` 文件的生产就绪性
- `WHAT`：在处理源自生产规模 SVN 仓库的完整 DETAIL 时，保持 Algorithm C 的正确性与性能
- `WHY`：证明 Algorithm C 能够处理源自 ≥10 000 个 SVN 修订版本、≥100 个分支副本的仓库生成的文件，且不出现正确性或性能退化
- `Story`: As a repository analyst, I want Algorithm C to remain correct and performant when processing genCodeDesc files derived from production-scale SVN repositories with ≥10 000 revisions and ≥100 branch copies, so that it is production-ready for real-world SVN histories.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=svn-origin` | `tier=Heavy`
- `Status`：计划中。尚无实现。对应 AlgA 门禁 `USNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13`。
- `Anchors`: `TestsNG-ALGC-HISTORY-COMPLEX-SCOPE-A-13-SVN`

**AC-SVN-01** — *规模下限：≥10 000 个修订版本，≥100 个分支副本*

- GIVEN 一份完整 DETAIL `genCodeDescProtoV26.04` 文件，源自具有 ≥10 000 个修订版本、≥100 个分支副本、以及在 `endTime` 之前反复发生分支合并或 reintegration 操作的 SVN 仓库
- WHEN Algorithm C 计算最终结果
- THEN 产生唯一一份仓库级 SUMMARY，计数与 golden 结果一致

**AC-SVN-02** — *深 SVN 历史中有效来源得到保留*

- GIVEN 存活行通过混合直接提交、分支副本和 merge 或 reintegration 历史到达发布路径，各自在 DETAIL 中携带准确的 `blame`
- WHEN Algorithm C 解析归因
- THEN 基于每行嵌入的 `blame.revisionId`（SVN 修订号）和 `blame.timestamp`，而非 merge 时序或分支路径

**AC-SVN-03** — *正确性与可扩展性同时验证*

- GIVEN 重型 SVN 生产规模场景成功完成
- WHEN 评估验收结果
- THEN 同时验证最终汇总结果的正确性，以及处理时间相对于 DETAIL 总行数的可接受扩展性

**AC-SVN-04** — *与 Algorithm A SVN 生产门禁对等*

- GIVEN `USNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13` 所使用的相同场景
- WHEN 对等效 `genCodeDescProtoV26.04` 文件执行 Algorithm C
- THEN `SUMMARY` 与 Algorithm A golden 结果一致

---

## 跨算法对等门禁

### USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-06: Algorithm C 对 Algorithm A 与 Algorithm B 的对等门禁

- `WHO`：质量工程师
- `WHEN`：验证 Algorithm C 对每个共享故事场景产生与 Algorithm A 和 Algorithm B 相同的汇总结果
- `WHAT`：一个跨算法对等断言，验证 Algorithm C 的 `SUMMARY` 与 Algorithm A 和 Algorithm B 的 `SUMMARY` 对所有相同输入保持一致
- `WHY`：保证三种算法在语义上等价；检测由离线 blame 嵌入方式引入的任何偏差
- `Story`: As a quality engineer, I want a parity gate that asserts Algorithm C produces the same `SUMMARY` as Algorithm A and Algorithm B for every shared story scenario, so that the three algorithms remain semantically equivalent.
- `Support`: `scope=A baseline` | `alg=A and B and C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`：计划中。依赖 ALGC-01 至 ALGC-05、ALGC-07 至 ALGC-11 全部通过。
- `Anchors`: `TestsNG-ALGC-PARITY-GATE`

**AC-01** — *Algorithm C 与 Algorithm A 在所有共享简单历史场景下一致*

- GIVEN 一个 Algorithm A 已产生已知 golden `SUMMARY` 的共享场景
- WHEN 对等效 `genCodeDescProtoV26.04` 文件执行 Algorithm C
- THEN `SUMMARY` 与 Algorithm A golden 结果完全一致

**AC-02** — *Algorithm C 与 Algorithm B 在所有共享简单历史场景下一致*

- GIVEN 一个 Algorithm B 已产生已知 golden `SUMMARY` 的共享场景
- WHEN 对等效 `genCodeDescProtoV26.04` 文件执行 Algorithm C
- THEN `SUMMARY` 与 Algorithm B golden 结果完全一致

**AC-03** — *协议版本不匹配为硬错误*

- GIVEN 一份 `protocolVersion` 非 `"26.04"` 的输入文件
- WHEN Algorithm C 尝试处理该文件
- THEN 分析器抛出协议版本错误，不产生任何部分结果
