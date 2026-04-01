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

## 故事结构

- 共享的 `US` 应描述业务需求和用户可见结果，而不绑定到某一种实现算法。
- 共享验收标准应覆盖无论由 `Algorithm A` 还是 `Algorithm B` 满足时都必须成立的可观察契约。
- 只有当 `Algorithm A` 与 `Algorithm B` 在支持边界、边缘语义或运行约束上不一致时，才应该拆出算法专属验收轨道。
- 如果某个共享故事当前只由一种算法实现，则另一种算法的验收轨道可以先以规划形式存在，但不能被当作当前已验证的验收证据。
- 对当前收敛计划而言，`US-6` 是第一个真正进入双轨收敛的共享故事。其它共享候选故事应逐个转换，在对应 `Algorithm B` 路径真正落地前，继续把 `Algorithm A` 作为当前验收证据。
- 有些共享故事首先是跨 VCS 共享，而不是先跨算法共享。在这种情况下，第一层验收拆分应优先是 Git 与 SVN，而算法专属轨道仍保留为规划状态。
- `US-13` 与 `US-14` 应继续被视为 `Heavy` 生产 gate，而不是普通共享功能故事的模板。

## 验证分层

- `Fast` 验证：夹具驱动检查与短时真实仓库测试，适合日常本地运行与普通 CI。
- `Heavy` 验证：面向生产的长时或大历史量验收检查，适合显式生产 gate 或每日集成运行。
- 对于可能耗时数十分钟甚至约一小时的验证，应归入 `Heavy`，例如生产规模的 Git/SVN 历史验证。

## 场景映射

- `US-1` -> `testdata/us1_live_changed_source_ratio`（`共享 US`，当前有效证据是 `Algorithm A`，`Fast`）
- `US-2` -> `testdata/us2_human_overwrites_ai_live_changed`（`共享 US`，当前有效证据是 `Algorithm A`，`Fast`）
- `US-3` -> `testdata/us3_ai_overwrites_human_live_changed`（`共享 US`，当前有效证据是 `Algorithm A`，`Fast`）
- `US-4` -> `testdata/us4_deleted_lines_excluded`（`共享 US`，当前有效证据是 `Algorithm A`，`Fast`）
- `US-5` -> `testdata/us5_rename_preserves_lineage`（`共享 US`，当前有效证据是 `Algorithm A`，`Fast`）
- `US-6` -> `testdata/us6_period_added_ratio`（`共享 US`，当前可执行路径是 `Algorithm B`，`Fast`）
- `US-7` -> `testdata/us7_mixed_multi_commit_window`（`共享 US`，当前有效证据是 `Algorithm A`，`Fast`）
- `US-8` -> `testdata/us8_merge_commit_preserves_attribution`（`共享 US`，当前有效证据是 `Algorithm A`，`Fast`）
- `US-9` -> `testdata/us9_svn_contract_parity`（`共享契约故事`，当前有效证据是通过 `Algorithm A` 建立的 Git/SVN 一致性，`Fast`）
- `US-10` -> `testdata/us10_large_repository_snapshot`（`共享 US`，当前有效证据是 `Algorithm A`，`Fast`）
- `US-11` -> `testdata/us11_deep_history_preserves_attribution`（`共享 US`，当前有效证据是 `Algorithm A`，`Fast`）
- `US-12` -> `testdata/us12_many_merged_branches_preserve_attribution`（`共享 US`，当前有效证据是 `Algorithm A`，`Fast`）
- `US-13` -> Git 生产规模本地仓库 gate（`Heavy gate`，当前有效证据是 `Algorithm A`，可作为每日集成）
- `US-14` -> SVN 生产规模本地仓库 gate（`Heavy gate`，当前有效证据是 `Algorithm A`，可作为每日集成）

## 共享故事收敛顺序

- `第 1 步`：先把 `US-6` 作为首个共享故事打实，确保当前 `Algorithm B` 基线是可辩护的。
- `第 2 步`：把当前围绕存活快照主指标的故事逐个改写为共享故事，但在对应 `Algorithm B` 路径真正存在前，继续只把 `Algorithm A` 视为当前验收证据。
- `第 3 步`：当前主指标建议按如下顺序推进：`US-1`、`US-2`、`US-3`、`US-4`、`US-5`、`US-7`、`US-8`、`US-10`、`US-11`、`US-12`。
- `第 4 步`：`US-9` 应保持为先按 Git/SVN 拆分的共享契约故事。只有当两个算法都真正能满足该契约时，再补充算法层的收敛。
- `第 5 步`：`US-13` 与 `US-14` 保持为 `Heavy` 生产 gate，不强行套入普通共享故事模式。

## 用户故事

### US-1：计算请求时间窗口内存活变更源码的加权 AI 占比

**作为** 一名仓库分析者，
**我希望** 计算当前版本落在请求时间段 `startTime~endTime` 内的存活源码行的加权 AI 占比，
**以便** 我了解当前仍然存活的变更源码中，有多少可归因于 AI。

说明：该故事应视为共享的存活快照契约故事。当前仓库只有 `Algorithm A` 一侧的验收证据。

#### US-1 共享验收标准

1. **GIVEN** 一个查询 `Repo:Branch:startTime:endTime`
   **WHEN** 用户请求 AI 代码占比
   **THEN** 系统必须针对该查询返回且只返回一个仓库级最终结果，用于描述截至 `endTime` 时，在 `startTime~endTime` 内新增或修改且仍然存活的源码行中的 AI 占比

2. **GIVEN** 一组存储在仓库外部、并由 `repoURL + repoBranch + revisionId` 索引的修订级别 `genCodeDesc` 记录
   **WHEN** 分析器从最终存活快照中发现落入统计范围的来源修订
   **THEN** 它必须在聚合过程中获取并使用这些修订对应的外部元数据记录

3. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

4. **GIVEN** 任一声称支持 `US-1` 的算法路径
   **WHEN** 该路径针对批准的 `US-1` 场景进行验证
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与该场景对应的 golden 结果一致

#### US-1 的 Algorithm A 验收轨道

1. **GIVEN** 夹具 `testdata/us1_live_changed_source_ratio`
   **WHEN** 当前 `Algorithm A` 实现产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

2. **GIVEN** 补充的 SVN 一致性夹具 `testdata/us1_live_changed_source_ratio_svn`
   **WHEN** 当前 `Algorithm A` 实现被用于同一基线指标的 SVN 验证
   **THEN** 外部可观察契约必须继续满足 `US-1` 的共享验收标准

#### US-1 的 Algorithm B 验收轨道

1. **GIVEN** 一个未来声明支持与 `US-1` 相同存活快照指标的 `Algorithm B` 路径
   **WHEN** 该路径被引入
   **THEN** 它必须满足 `US-1` 的共享验收标准，且不能削弱结果契约

2. **GIVEN** 当前还没有任何获批的 `Algorithm B` 验收证据用于 `US-1`
   **WHEN** 讨论收敛路线时
   **THEN** `US-1` 仍必须被视为当前仅由 `Algorithm A` 证明

### US-2：人工重写会移除之前的 AI 归因

**作为** 一名仓库分析者，
**我希望** 当人类重写了先前由 AI 生成的代码行时，归因应重置到较新的人工修订，
**以便** 旧的 AI 归属不会继续附着在已经被覆盖的代码上。

说明：该故事应视为共享的覆盖重写语义故事。当前仓库只有 `Algorithm A` 一侧的验收证据。

#### US-2 共享验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 先前归因给 AI 的代码在 `endTime` 前已经被后续人工修订所取代
   **THEN** 系统必须针对 `endTime` 的存活变更源码集合产出一个最终记录，反映较新的仓库状态，而不是保留过时的 AI 归属

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 任一声称支持 `US-2` 的算法路径
   **WHEN** 该路径针对批准的 `US-2` 场景进行验证
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与该场景对应的 golden 结果一致

#### US-2 的 Algorithm A 验收轨道

1. **GIVEN** 夹具 `testdata/us2_human_overwrites_ai_live_changed`
   **WHEN** 当前 `Algorithm A` 实现产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

#### US-2 的 Algorithm B 验收轨道

1. **GIVEN** 一个未来声明支持与 `US-2` 相同覆盖重置契约的 `Algorithm B` 路径
   **WHEN** 该路径被引入
   **THEN** 它必须满足 `US-2` 的共享验收标准，而不能保留过时的 AI 归属

2. **GIVEN** 当前还没有任何获批的 `Algorithm B` 验收证据用于 `US-2`
   **WHEN** 讨论收敛路线时
   **THEN** `US-2` 仍必须被视为当前仅由 `Algorithm A` 证明

### US-3：AI 重写会取代之前的人类归属

**作为** 一名仓库分析者，
**我希望** 后续由 AI 完成的人类代码重写能够成为有效归因来源，
**以便** `endTime` 时刻的存活变更源码能够反映最新的 AI 贡献。

说明：该故事应视为共享的覆盖重写语义故事。当前仓库只有 `Algorithm A` 一侧的验收证据。

#### US-3 共享验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 后续修订在 `endTime` 前引入了新的 AI 归因代码
   **THEN** 系统必须产出一个最终记录，以反映 `endTime` 时刻存活变更源码状态中的较新 AI 贡献

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 任一声称支持 `US-3` 的算法路径
   **WHEN** 该路径针对批准的 `US-3` 场景进行验证
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与该场景对应的 golden 结果一致

#### US-3 的 Algorithm A 验收轨道

1. **GIVEN** 夹具 `testdata/us3_ai_overwrites_human_live_changed`
   **WHEN** 当前 `Algorithm A` 实现产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

#### US-3 的 Algorithm B 验收轨道

1. **GIVEN** 一个未来声明支持与 `US-3` 相同归属接管契约的 `Algorithm B` 路径
   **WHEN** 该路径被引入
   **THEN** 它必须满足 `US-3` 的共享验收标准，且不能削弱最终存活结果语义

2. **GIVEN** 当前还没有任何获批的 `Algorithm B` 验收证据用于 `US-3`
   **WHEN** 讨论收敛路线时
   **THEN** `US-3` 仍必须被视为当前仅由 `Algorithm A` 证明

### US-4：已删除的 AI 代码行不得计入

**作为** 一名仓库分析者，
**我希望** 被删除的 AI 生成代码行同时从分子和分母中消失，
**以便** 结果只反映当前仍然存活的变更源码快照。

说明：该故事应视为共享的存活快照排除故事。当前仓库只有 `Algorithm A` 一侧的验收证据。

#### US-4 共享验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 某些较早的 AI 归因代码在 `endTime` 时已不存在于该分支状态中
   **THEN** 系统必须产出一个最终记录，并将这些已删除代码从存活变更源码结果中排除

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 任一声称支持 `US-4` 的算法路径
   **WHEN** 该路径针对批准的 `US-4` 场景进行验证
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与该场景对应的 golden 结果一致

#### US-4 的 Algorithm A 验收轨道

1. **GIVEN** 夹具 `testdata/us4_deleted_lines_excluded`
   **WHEN** 当前 `Algorithm A` 实现产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

#### US-4 的 Algorithm B 验收轨道

1. **GIVEN** 一个未来声明支持与 `US-4` 相同删除排除契约的 `Algorithm B` 路径
   **WHEN** 该路径被引入
   **THEN** 它必须满足 `US-4` 的共享验收标准，而不能把已删除代码计入最终结果

2. **GIVEN** 当前还没有任何获批的 `Algorithm B` 验收证据用于 `US-4`
   **WHEN** 讨论收敛路线时
   **THEN** `US-4` 仍必须被视为当前仅由 `Algorithm A` 证明

### US-5：重命名必须保留归因谱系

**作为** 一名仓库分析者，
**我希望** 当文件只发生重命名或移动而内容未变时，行归因能够被保留，
**以便** 最终的存活变更源码 AI 占比不会因为仅路径层面的历史变化而失真。

说明：该故事应视为共享的谱系保留故事。当前仓库只有 `Algorithm A` 一侧的验收证据。

#### US-5 共享验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 文件在 `endTime` 前发生了重命名或移动，但未改变其有效内容贡献
   **THEN** 系统必须产出一个最终记录，使得 `endTime` 时刻存活变更源码集合在仅路径变化的情况下保持稳定

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 任一声称支持 `US-5` 的算法路径
   **WHEN** 该路径针对批准的 `US-5` 场景进行验证
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与该场景对应的 golden 结果一致

#### US-5 的 Algorithm A 验收轨道

1. **GIVEN** 夹具 `testdata/us5_rename_preserves_lineage`
   **WHEN** 当前 `Algorithm A` 实现产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

#### US-5 的 Algorithm B 验收轨道

1. **GIVEN** 一个未来声明支持与 `US-5` 相同重命名保留谱系契约的 `Algorithm B` 路径
   **WHEN** 该路径被引入
   **THEN** 它必须满足 `US-5` 的共享验收标准，且不能让纯路径变化扭曲归因

2. **GIVEN** 当前还没有任何获批的 `Algorithm B` 验收证据用于 `US-5`
   **WHEN** 讨论收敛路线时
   **THEN** `US-5` 仍必须被视为当前仅由 `Algorithm A` 证明

### US-6：计算请求时间段内新增 AI 代码的占比

**作为** 一名仓库分析者，
**我希望** 计算 `startTime~endTime` 期间新增的 AI 代码量，
**以便** 将时间段内的新增贡献与期末存量区分开来。

说明：这不是当前 `P0 / Scope A` 的基线指标。这是一个单独的、面向历史过程的指标，应被视为一个共享用户故事，同时允许 `Algorithm A` 与 `Algorithm B` 通过不同的验收轨道来满足。当前实现只在 `Algorithm B` 一侧包含针对 `US-6` 夹具形态的一条窄化可执行 Git 离线基线路径。

#### US-6 共享验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 用户请求该时间段贡献指标
   **THEN** 系统必须针对该查询窗口返回且只返回一个仓库级最终结果，用于描述该时间段内 AI 新增代码的聚合结果

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 该时间段贡献结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 任一声称支持 `US-6` 的算法实现路径
   **WHEN** 该路径针对批准的 `US-6` 场景进行验证
   **THEN** 它产出的 `SUMMARY` 与 `REPOSITORY` 必须与该场景对应的 golden 结果一致

#### US-6 的 Algorithm A 验收轨道

1. **GIVEN** 一个未来声明支持时间段贡献指标的 `Algorithm A` 路径
   **WHEN** 该路径被引入
   **THEN** 它必须满足 `US-6` 的共享验收标准，且不能削弱外部可观察的结果契约

2. **GIVEN** 一个未来面向 `US-6` 的 `Algorithm A` 夹具或真实仓库验收场景
   **WHEN** 该场景变为启用状态
   **THEN** 它应被显式标记为 `Fast` 或 `Heavy`，而不是隐式混入当前基线套件

#### US-6 的 Algorithm B 验收轨道

1. **GIVEN** 夹具 `testdata/us6_period_added_ratio`
   **WHEN** 分析器通过当前窄化的离线 Git 基线路径产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

2. **GIVEN** 当前 CLI 切片配合 `--algorithm B --commitDiffSetDir`
   **WHEN** 输入满足当前这种单文件、单分支 Git 回放序列的窄化夹具契约
   **THEN** 分析器可以在不要求 `--workingDir` 的情况下执行 `US-6` 的离线 Algorithm-B 基线

3. **GIVEN** 更宽的 Algorithm-B 历史形态，例如多文件回放、重命名/路径变化或 merge 感知归因
   **WHEN** 使用当前 CLI 切片
   **THEN** 在这些场景各自的验收轨道建立并验证之前，它们必须继续保持显式不支持

### US-7：在单个请求窗口内正确处理混合多提交历史

**作为** 一名仓库分析者，
**我希望** 一个请求窗口能够正确处理跨多个提交的混合行历史，
**以便** 当人工代码、AI 代码、人工后被 AI 重写、AI 后被人工重写，以及已删除 AI 代码同时出现在同一时间段时，最终结果仍然正确。

说明：该故事应视为共享的混合历史故事。当前仓库只有 `Algorithm A` 一侧的验收证据。

#### US-7 共享验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 该窗口内的多个提交在不同存活代码行上包含混合的归属转换
   **THEN** 系统必须针对 `endTime` 的存活变更源码集合产出且只产出一个最终记录，并按每条存活代码行最新的有效归因进行计算

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 任一声称支持 `US-7` 的算法路径
   **WHEN** 该路径针对批准的 `US-7` 场景进行验证
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与该场景对应的 golden 结果一致

#### US-7 的 Algorithm A 验收轨道

1. **GIVEN** 夹具 `testdata/us7_mixed_multi_commit_window`
   **WHEN** 当前 `Algorithm A` 实现产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

#### US-7 的 Algorithm B 验收轨道

1. **GIVEN** 一个未来声明支持与 `US-7` 相同混合历史存活结果契约的 `Algorithm B` 路径
   **WHEN** 该路径被引入
   **THEN** 它必须满足 `US-7` 的共享验收标准，而不能把中间已被覆盖的归属泄漏到最终结果中

2. **GIVEN** 当前还没有任何获批的 `Algorithm B` 验收证据用于 `US-7`
   **WHEN** 讨论收敛路线时
   **THEN** `US-7` 仍必须被视为当前仅由 `Algorithm A` 证明

### US-8：Merge 提交必须保留有效归因

**作为** 一名仓库分析者，
**我希望** 分支合并后的内容仍然保留存活代码行的有效归因，
**以便** merge 操作不会把整批代码行错误地重置到 merge commit 本身。

说明：该故事应视为共享的 merge 语义故事。当前仓库只有 `Algorithm A` 一侧的验收证据。

#### US-8 共享验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 某个 merge commit 在 `endTime` 前汇合了较早的人类变更与 AI 归因变更
   **THEN** 系统必须针对 `endTime` 的存活变更源码集合产出一个最终记录，对存活的合并后代码行使用其有效归因，而不是把 merge commit 当作统一来源

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 任一声称支持 `US-8` 的算法路径
   **WHEN** 该路径针对批准的 `US-8` 场景进行验证
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与该场景对应的 golden 结果一致

#### US-8 的 Algorithm A 验收轨道

1. **GIVEN** 夹具 `testdata/us8_merge_commit_preserves_attribution`
   **WHEN** 当前 `Algorithm A` 实现产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

#### US-8 的 Algorithm B 验收轨道

1. **GIVEN** 一个未来声明支持与 `US-8` 相同 merge 保留归因契约的 `Algorithm B` 路径
   **WHEN** 该路径被引入
   **THEN** 它必须满足 `US-8` 的共享验收标准，而不能把合并后的行塌缩到 merge commit 或分支身份上

2. **GIVEN** 当前还没有任何获批的 `Algorithm B` 验收证据用于 `US-8`
   **WHEN** 讨论收敛路线时
   **THEN** `US-8` 仍必须被视为当前仅由 `Algorithm A` 证明

### US-9：Git 与 SVN 必须遵循相同的结果契约

**作为** 一名仓库分析者，
**我希望** 对于当前主指标，Git 与 SVN 目标遵循相同的查询/结果契约，
**以便** 切换 VCS 类型时，不会改变指标语义或输出结构。

说明：这是一个首先按 VCS 目标拆分的共享契约故事。当前仓库通过 `Algorithm A` 拥有 Git/SVN 一致性证据，但还没有双算法收敛证据。

#### US-9 共享验收标准

1. **GIVEN** 以受支持 VCS 目标表示的等价仓库历史，以及一个请求时间段 `startTime~endTime`
   **WHEN** 用户请求当前主指标
   **THEN** 系统必须产出一个最终记录，该记录具有相同的指标语义和相同的协议形态输出结构，仅在 `vcsType`、branch-path 约定或 `revisionId` 等 VCS 特定的仓库身份信息上存在差异

2. **GIVEN** `Repo:Branch:startTime:endTime` 的成功结果
   **WHEN** 结果被返回或序列化为 `genCodeDescProtocol.json`
   **THEN** 它必须是符合 `genCodeDescProtocol.json` 格式的最终记录，在 `REPOSITORY` 中包含仓库身份信息，并在 `SUMMARY` 中包含聚合后的最终值

3. **GIVEN** 任一受支持且声称满足 `US-9` 的 VCS 路径
   **WHEN** 该路径针对批准的一致性场景进行验证
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与该场景对应的 golden 结果一致

#### US-9 的 Git 验收轨道

1. **GIVEN** 当前主指标的 Git 路径
   **WHEN** 它通过基线存活快照场景进行验证
   **THEN** 它应构成 `US-9` 一致性契约的一侧，并定义需要被匹配的 Git 可观察结果语义

#### US-9 的 SVN 验收轨道

1. **GIVEN** 夹具 `testdata/us9_svn_contract_parity`
   **WHEN** 当前 SVN 路径产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致，并保持 `US-9` 的共享契约

2. **GIVEN** VCS 特定的路径历史或 blame 差异
   **WHEN** 为 SVN 设计一致性验证场景
   **THEN** 可以使用可辩护的 SVN 特定仓库形态，只要外部可观察结果契约保持一致

#### US-9 的算法收敛说明

1. **GIVEN** 一个未来声明支持与 `US-9` 相同跨 VCS 一致性契约的 `Algorithm B` 路径
   **WHEN** 该路径被引入
   **THEN** 它应建立在现有 Git/SVN 拆分之上，而不是替代当前 VCS-first 的验收结构

### US-10：大型仓库快照必须保持结果语义稳定

**作为** 一名仓库分析者，
**我希望** 当仓库包含很多源码文件和很多存活代码行时，分析器仍然保持相同的结果语义，
**以便** 最终聚合结果在真实大型代码库中依然正确。

说明：该故事应视为共享的规模语义故事。当前仓库只有 `Algorithm A` 一侧的验收证据。

#### US-10 共享验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** `endTime` 时刻的最终存活快照横跨大量源码文件和大量存活代码行
   **THEN** 系统仍必须产出且只产出一个仓库级最终结果，并且其指标语义与协议形态结构应与小型仓库保持一致

2. **GIVEN** 一个包含很多处于统计范围内代码行、并分布在很多文件中的大型仓库快照
   **WHEN** 分析器执行聚合
   **THEN** 文件数量或仓库规模不得改变逐行归因规则、仓库身份规则，或最终 `SUMMARY` 字段的含义

3. **GIVEN** 任一声称支持 `US-10` 的算法路径
   **WHEN** 该路径针对批准的 `US-10` 场景进行验证
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与该场景对应的 golden 结果一致

#### US-10 的 Algorithm A 验收轨道

1. **GIVEN** 夹具 `testdata/us10_large_repository_snapshot`
   **WHEN** 当前 `Algorithm A` 实现产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

#### US-10 的 Algorithm B 验收轨道

1. **GIVEN** 一个未来声明支持与 `US-10` 相同大型快照可观察契约的 `Algorithm B` 路径
   **WHEN** 该路径被引入
   **THEN** 它必须满足 `US-10` 的共享验收标准，且不能改变最终 `SUMMARY` 字段的含义

2. **GIVEN** 当前还没有任何获批的 `Algorithm B` 验收证据用于 `US-10`
   **WHEN** 讨论收敛路线时
   **THEN** `US-10` 仍必须被视为当前仅由 `Algorithm A` 证明

### US-11：深历史链必须保持最新有效归因

**作为** 一名仓库分析者，
**我希望** 长修订链能够保持每条存活代码行的最新有效归因，
**以便** 大量中间重写不会扭曲最终的存活结果。

说明：该故事应视为共享的深历史故事。当前仓库只有 `Algorithm A` 一侧的验收证据。

#### US-11 共享验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** `endTime` 时刻处于统计范围内的存活代码行依赖于包含大量中间重写的长修订链
   **THEN** 系统必须按每条存活代码行最新的有效归因进行解析，而不能回退到链路中更早但已被取代的修订

2. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 长历史链中在 `endTime` 前同时存在人类到 AI、以及 AI 到人类的转换
   **THEN** 已删除或已被覆盖的中间状态不得泄漏到最终聚合结果中

3. **GIVEN** 任一声称支持 `US-11` 的算法路径
   **WHEN** 该路径针对批准的 `US-11` 场景进行验证
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与该场景对应的 golden 结果一致

#### US-11 的 Algorithm A 验收轨道

1. **GIVEN** 夹具 `testdata/us11_deep_history_preserves_attribution`
   **WHEN** 当前 `Algorithm A` 实现产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

#### US-11 的 Algorithm B 验收轨道

1. **GIVEN** 一个未来声明支持与 `US-11` 相同深历史存活结果契约的 `Algorithm B` 路径
   **WHEN** 该路径被引入
   **THEN** 它必须满足 `US-11` 的共享验收标准，而不能让已被覆盖的中间状态泄漏到最终结果中

2. **GIVEN** 当前还没有任何获批的 `Algorithm B` 验收证据用于 `US-11`
   **WHEN** 讨论收敛路线时
   **THEN** `US-11` 仍必须被视为当前仅由 `Algorithm A` 证明

### US-12：单个窗口内的多分支合并必须保持逐行归因

**作为** 一名仓库分析者，
**我希望** 单个请求窗口内的高分支密度历史仍能保持逐行有效归因，
**以便** 多个功能分支集成回目标分支时不会扭曲最终结果。

说明：该故事应视为共享的高分支故事。当前仓库只有 `Algorithm A` 一侧的验收证据，而且对于同一广义主张的 SVN 一致性，可能需要一个可辩护的类比场景，而不是直接照搬 Git 形态。

#### US-12 共享验收标准

1. **GIVEN** 一个仓库分支和请求时间段 `startTime~endTime`
   **WHEN** 在 `endTime` 前有很多分支被合并到目标分支
   **THEN** 系统仍必须针对 `endTime` 的存活变更源码集合产出且只产出一个仓库级最终结果

2. **GIVEN** 单个请求窗口内存在多个合并分支
   **WHEN** 不同存活代码行来自不同分支，且这些分支各自带有不同的有效归因历史
   **THEN** 系统必须独立保留每条存活代码行的有效归因，而不能把归属塌缩到 merge commit、分支标签或合并顺序本身

3. **GIVEN** 任一声称支持 `US-12` 的算法路径
   **WHEN** 该路径针对批准的 `US-12` 场景进行验证
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与该场景对应的 golden 结果一致

#### US-12 的 Algorithm A 验收轨道

1. **GIVEN** 夹具 `testdata/us12_many_merged_branches_preserve_attribution`
   **WHEN** 当前 `Algorithm A` 实现产出最终结果
   **THEN** 产出的 `SUMMARY` 与 `REPOSITORY` 必须与 `expected_result.json` 一致

2. **GIVEN** 针对同一广义契约的 SVN 高分支一致性验证
   **WHEN** 真实 SVN blame 语义使“同文件 Git 场景的逐字照搬”变得具有误导性
   **THEN** 可以使用一个可辩护的 SVN 特定类比场景，只要 `US-12` 的共享可观察契约保持不变

#### US-12 的 Algorithm B 验收轨道

1. **GIVEN** 一个未来声明支持与 `US-12` 相同高分支存活结果契约的 `Algorithm B` 路径
   **WHEN** 该路径被引入
   **THEN** 它必须满足 `US-12` 的共享验收标准，而不能把归属塌缩到合并顺序、merge commit 或分支标签本身

2. **GIVEN** 当前还没有任何获批的 `Algorithm B` 验收证据用于 `US-12`
   **WHEN** 讨论收敛路线时
   **THEN** `US-12` 仍必须被视为当前仅由 `Algorithm A` 证明

## Heavy 生产 Gates

以下条目被有意视为 `Heavy` 生产 gate，而不是普通共享功能故事。它们应继续作为明确的运行级验收目标存在，而共享故事收敛则优先从 `US-6` 以及较小的 `Fast` 故事继续推进。

### US-13：Git 生产规模本地仓库在高分支发布收敛下仍必须保持正确

**作为** 一名仓库分析者，
**我希望** `Algorithm A + Scope A` 在生产规模的本地 Git 仓库上仍然保持正确，
**以便** 大量分支、深历史以及混合发布合并不会扭曲最终的存活归因结果。

#### US-13 验收标准

1. **GIVEN** 一个代表生产拓扑的本地 Git 仓库
   **WHEN** 它在 `endTime` 前包含大约 `100+` 个分支、`1000+` 个提交，以及重复的 feature 到 integration 再到 release 的扇入式合并
   **THEN** 系统仍必须针对 `endTime` 的存活变更源码集合计算且只计算一个仓库级最终结果

2. **GIVEN** 同一个代表生产拓扑的本地 Git 仓库
   **WHEN** 不同存活代码行来自不同功能分支，并通过直接合并、集成分支和分阶段收敛等方式到达 release 分支
   **THEN** 最终归因必须基于每条存活代码行的有效来源修订，而不是 merge 形态、仅 first-parent 历史或分支命名规则

3. **GIVEN** 同一个代表生产拓扑的本地 Git 仓库
   **WHEN** 该仓库是本地仓库而非远端托管仓库
   **THEN** 该场景仍然是本分析器有效的生产就绪性验收案例，因为仓库传输不在契约范围内，而历史语义除网络访问外必须保持一致

4. **GIVEN** Git 生产规模验收场景
   **WHEN** 分析器成功完成运行
   **THEN** 该测试必须同时验证最终聚合结果的正确性，以及诸如受控的元数据复用、受控的修订时间查询复用或测试框架定义的其它显式复用信号等偏扩展性行为

### US-14：SVN 生产规模本地仓库在分支与合并压力下仍必须保持正确

**作为** 一名仓库分析者，
**我希望** `Algorithm A + Scope A` 在生产规模的本地 SVN 仓库上仍然保持正确，
**以便** SVN 的分支复制、合并以及大规模 release reintegration 不会破坏存活归因。

#### US-14 验收标准

1. **GIVEN** 一个代表生产拓扑的本地 SVN 仓库
   **WHEN** 它在 `endTime` 前包含大约 `100+` 个分支或分支复制、`1000+` 个修订，以及重复的 branch 到 release 合并活动
   **THEN** 系统仍必须针对 `endTime` 的存活变更源码集合计算且只计算一个仓库级最终结果

2. **GIVEN** 同一个代表生产拓扑的本地 SVN 仓库
   **WHEN** 不同存活代码行通过直接工作、分支复制以及合并或 reintegration 历史到达 release 路径
   **THEN** 最终归因必须在当前受支持的 SVN blame 语义范围内保留每条存活代码行的有效来源修订，而不能塌缩到合并时机或最终分支路径本身

3. **GIVEN** 同一个代表生产拓扑的本地 SVN 仓库
   **WHEN** 该仓库是本地仓库而非远端托管仓库
   **THEN** 该场景仍然是本分析器有效的生产就绪性验收案例，因为网络传输不属于归因契约的一部分

4. **GIVEN** SVN 生产规模验收场景
   **WHEN** 分析器成功完成运行
   **THEN** 该测试必须同时验证最终聚合结果的正确性，以及诸如分支来源元数据查找复用、受控的修订时间查询或测试框架定义的其它显式复用信号等偏扩展性行为

### Future Algorithm-B Story Intent

下一批计划中的 `Algorithm B` 用户故事是：

1. `US-15`：无 merge、无 rename 的单分支 period-added 基线
2. `US-16`：单个窗口内带删除、回退与混合重写的 period-added 计量
3. `US-17`：Git 下 period contribution 的 rename 与 move 处理
4. `US-18`：单个请求窗口内面向 merge 的 Git period contribution
5. `US-19`：Algorithm-B period contribution 的 SVN 可支持子集

这些故事必须逐个在 TDD 下引入，并配套显式的 `query.json` 与 `expected_result.json` 工件，然后才能讨论任何 `Algorithm B` 生产就绪性主张。
