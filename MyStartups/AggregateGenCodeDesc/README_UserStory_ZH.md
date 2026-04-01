# AggregateGenCodeDesc 用户故事与验收标准

## 目的

本文档定义 AggregateGenCodeDesc 的第一批用户故事，以及用于验证这些故事的验收标准。

所有故事都假定分析请求包含 `repo + branch + startTime + endTime`。
对于当前主指标，`startTime~endTime` 用来定义哪些存活代码行属于统计范围，而结果则基于 `endTime` 时刻的存活快照计算。
当前基线是 `P0 / Scope A: pure source code`，并使用 `Algorithm A (preferred): blame-based end-snapshot attribution`。
除非另有明确说明，当前这些用户故事同时适用于 Git 和 SVN 目标。VCS 之间的差异可能影响仓库身份、分支或路径约定，以及修订标识符，但不应改变指标语义或协议形态的结果契约。
在现阶段，验收标准有意定义在仓库查询级别，而不是内部文件级或行级实现细节层面。
最终聚合结果可以通过报告返回，也可以直接由协议中的 `SUMMARY` 段表示。
用户查询与最终记录是两个不同工件：`query.json` 表示分析输入，而 `genCodeDescProtocol.json` 表示最终结果记录。
分析过程中使用的 `genCodeDesc` 记录是修订级别的外部元数据，而不是提交进被分析仓库中的文件。
单条元数据记录的目标查找键是 `repoURL + repoBranch + revisionId`。
除非某个故事明确规定了另一种指标，否则 `SUMMARY.totalCodeLines` 一律表示该记录作用域内真正被该记录表示的代码行数。对于当前 Algorithm A 的最终结果，这意味着只统计在 `endTime` 仍然存活的行，不包含已经删除的历史代码行。
在夹具验证中，`expected_result.json` 应保持为最小化的协议形态输出工件。它应保留 `protocolName`、`protocolVersion`、`SUMMARY`、`REPOSITORY` 等结果字段，而不应重复 `metric`、`model`、`scope`、`startTime`、`endTime` 这类只属于查询的字段。

每个故事都配有位于 `testdata/` 下的场景化测试夹具。
每个场景包含：

- 每个修订对应一个 `genCodeDesc` 文件，用于描述该修订的 AI 归因

对于 `Algorithm B`，每个场景还必须在 `commitDiffSet/` 中携带一条完整的 commit diff 序列。
如果某个场景要求回放 `r1..rn` 这些修订，则每个需要回放的修订都必须有对应的原始 patch 工件，例如 `<revisionId>_commitDiff.patch`。
长序列中间缺少某个 commit diff 属于夹具契约失败，不能被静默跳过。

这些 `testdata/` 场景是面向设计讨论的夹具。
这些本地 `genCodeDesc` 文件用于模拟真实部署中的外部元数据存储。
对于 `Algorithm B`，本地原始 commit diff patch 工件也必须放在 `testdata/` 中，以便显式验证回放链条的完整性。
对于 `Algorithm A` 的真实仓库验证，首选测试层是在 `tests/` 下，通过创建真实的 Git 或 SVN 仓库来验证，并且不要求 `*.diff` 文件。

对于偏生产的运行方式，分析器应先从仓库历史中发现相关修订，再从外部提供者中获取匹配的 `genCodeDesc` 记录。

## 场景映射

- `US-1` -> `testdata/us1_live_changed_source_ratio` (`Algorithm A`)
- `US-2` -> `testdata/us2_human_overwrites_ai_live_changed` (`Algorithm A`)
- `US-3` -> `testdata/us3_ai_overwrites_human_live_changed` (`Algorithm A`)
- `US-4` -> `testdata/us4_deleted_lines_excluded` (`Algorithm A`)
- `US-5` -> `testdata/us5_rename_preserves_lineage` (`Algorithm A`)
- `US-6` -> `testdata/us6_period_added_ratio` (`Algorithm B`)
- `US-7` -> `testdata/us7_mixed_multi_commit_window` (`Algorithm A`)
- `US-8` -> `testdata/us8_merge_commit_preserves_attribution` (`Algorithm A`)
- `US-9` -> `testdata/us9_svn_contract_parity` (`Algorithm A`)

## 用户故事

### US-1：计算请求时间窗口内存活变更源码的加权 AI 占比

**作为** 一名仓库分析者，
**我希望** 计算当前版本落在请求时间段 `startTime~endTime` 内的存活源码行的加权 AI 占比，
**以便** 我了解当前仍然存活的变更源码中，有多少可归因于 AI。

#### US-1 验收标准

1. **GIVEN** 一个查询 `Repo:Branch:startTime:endTime`
   **WHEN** 用户请求 AI 代码占比
   **THEN** 系统必须针对该查询返回且只返回一个仓库级最终结果，用于描述截至 `endTime` 时，在 `startTime~endTime` 内新增或修改且仍然存活的源码行中的 AI 占比

2. **GIVEN** 一组存储在仓库外部、并由 `repoURL + repoBranch + revisionId` 索引的修订级别 `genCodeDesc` 记录
   **WHEN** 分析器从最终存活快照中发现落入统计范围的来源修订
   **THEN** 它必须在聚合过程中获取并使用这些修订对应的外部元数据记录

3. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

4. **GIVEN** 夹具 `testdata/us1_live_changed_source_ratio`
   **WHEN** 分析器产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

### US-2：人工重写会移除之前的 AI 归因

**作为** 一名仓库分析者，
**我希望** 当人类重写了先前由 AI 生成的代码行时，归因应重置到较新的人工修订，
**以便** 旧的 AI 归属不会继续附着在已经被覆盖的代码上。

#### US-2 验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 先前归因给 AI 的代码在 `endTime` 前已经被后续人工修订所取代
   **THEN** 系统必须针对 `endTime` 的存活变更源码集合产出一个最终记录，反映较新的仓库状态，而不是保留过时的 AI 归属

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 夹具 `testdata/us2_human_overwrites_ai_live_changed`
   **WHEN** 分析器产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

### US-3：AI 重写会取代之前的人类归属

**作为** 一名仓库分析者，
**我希望** 后续由 AI 完成的人类代码重写能够成为有效归因来源，
**以便** `endTime` 时刻的存活变更源码能够反映最新的 AI 贡献。

#### US-3 验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 后续修订在 `endTime` 前引入了新的 AI 归因代码
   **THEN** 系统必须产出一个最终记录，以反映 `endTime` 时刻存活变更源码状态中的较新 AI 贡献

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 夹具 `testdata/us3_ai_overwrites_human_live_changed`
   **WHEN** 分析器产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

### US-4：已删除的 AI 代码行不得计入

**作为** 一名仓库分析者，
**我希望** 被删除的 AI 生成代码行同时从分子和分母中消失，
**以便** 结果只反映当前仍然存活的变更源码快照。

#### US-4 验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 某些较早的 AI 归因代码在 `endTime` 时已不存在于该分支状态中
   **THEN** 系统必须产出一个最终记录，并将这些已删除代码从存活变更源码结果中排除

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 夹具 `testdata/us4_deleted_lines_excluded`
   **WHEN** 分析器产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

### US-5：重命名必须保留归因谱系

**作为** 一名仓库分析者，
**我希望** 当文件只发生重命名或移动而内容未变时，行归因能够被保留，
**以便** 最终的存活变更源码 AI 占比不会因为仅路径层面的历史变化而失真。

#### US-5 验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 文件在 `endTime` 前发生了重命名或移动，但未改变其有效内容贡献
   **THEN** 系统必须产出一个最终记录，使得 `endTime` 时刻存活变更源码集合在仅路径变化的情况下保持稳定

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 夹具 `testdata/us5_rename_preserves_lineage`
   **WHEN** 分析器产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

### US-6：计算请求时间段内新增 AI 代码的占比

**作为** 一名仓库分析者，
**我希望** 计算 `startTime~endTime` 期间新增的 AI 代码量，
**以便** 将时间段内的新增贡献与期末存量区分开来。

说明：这不是当前 `P0 / Scope A` 的基线指标。这是一个单独的、面向历史过程的指标，并与 `Algorithm B` 对齐。当前实现已经包含针对 `US-6` 夹具形态的一条窄化可执行 Git 离线基线路径，但这还不能被视为广义的 Algorithm-B 覆盖。

#### US-6 验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 用户请求该时间段贡献指标
   **THEN** 系统必须针对该查询窗口返回且只返回一个仓库级最终结果，用于描述该时间段内 AI 新增代码的聚合结果

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 该时间段贡献结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 夹具 `testdata/us6_period_added_ratio`
   **WHEN** 分析器产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

4. **GIVEN** 当前 CLI 切片配合 `--algorithm B --commitDiffSetDir`
   **WHEN** 输入满足当前这种单文件、单分支 Git 回放序列的窄化夹具契约
   **THEN** 分析器可以在不要求 `--workingDir` 的情况下执行 `US-6` 的离线 Algorithm-B 基线

### US-7：在单个请求窗口内正确处理混合多提交历史

**作为** 一名仓库分析者，
**我希望** 一个请求窗口能够正确处理跨多个提交的混合行历史，
**以便** 当人工代码、AI 代码、人工后被 AI 重写、AI 后被人工重写，以及已删除 AI 代码同时出现在同一时间段时，最终结果仍然正确。

#### US-7 验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 该窗口内的多个提交在不同存活代码行上包含混合的归属转换
   **THEN** 系统必须针对 `endTime` 的存活变更源码集合产出且只产出一个最终记录，并按每条存活代码行最新的有效归因进行计算

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 夹具 `testdata/us7_mixed_multi_commit_window`
   **WHEN** 分析器产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

### US-8：Merge 提交必须保留有效归因

**作为** 一名仓库分析者，
**我希望** 分支合并后的内容仍然保留存活代码行的有效归因，
**以便** merge 操作不会把整批代码行错误地重置到 merge commit 本身。

#### US-8 验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 某个 merge commit 在 `endTime` 前汇合了较早的人类变更与 AI 归因变更
   **THEN** 系统必须针对 `endTime` 的存活变更源码集合产出一个最终记录，对存活的合并后代码行使用其有效归因，而不是把 merge commit 当作统一来源

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 夹具 `testdata/us8_merge_commit_preserves_attribution`
   **WHEN** 分析器产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

### US-9：Git 与 SVN 必须遵循相同的结果契约

**作为** 一名仓库分析者，
**我希望** 对于当前主指标，Git 与 SVN 目标遵循相同的查询/结果契约，
**以便** 切换 VCS 类型时，不会改变指标语义或输出结构。

#### US-9 验收标准

1. **GIVEN** 以受支持 VCS 目标表示的等价仓库历史，以及一个请求时间段 `startTime~endTime`
   **WHEN** 用户请求当前主指标
   **THEN** 系统必须产出一个最终记录，该记录具有相同的指标语义和相同的协议形态输出结构，仅在 `vcsType`、branch-path 约定或 `revisionId` 等 VCS 特定的仓库身份信息上存在差异

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 夹具 `testdata/us9_svn_contract_parity`
   **WHEN** 分析器产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致
