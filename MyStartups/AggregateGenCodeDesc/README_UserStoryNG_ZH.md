# AggregateGenCodeDesc USNG（UserStoryNG）

## 目的

本文档定义 AggregateGenCodeDesc 的权威下一代用户故事与验收标准，并与 `README_UserStoryNG.md` 保持语义同步。

它与当前基础文档配合使用：

- `README_ZH.md` 仍然是产品与契约的中文基础文档。
- `README_UserGuide_ZH.md` 仍然是面向操作与运行方式的中文基础文档。

在本仓库中，`UserStoryNG` 可简称为 `USNG`。

## USNG 故事规则

1. 让每个故事都以完整 `5W1H` 形式显式表达：`WHO`、`WHEN`、`WHERE`、`WHAT`、`WHY`、`HOW`。
2. 保留经典用户故事句式作为主要故事形式：`As ... I want ... so that ...`。
3. 保留经典 `GIVEN ... WHEN ... THEN ...` 作为验收标准形式。
4. 显式写出当前支持边界，而不是隐藏局部支持。
5. 保持场景锚点可见，使每个故事都能指向 NG 验证锚点，而不是绑定到实现路径。

## NG 验证锚点策略

USNG 在规范层上不应再绑定到具体文件系统路径或 golden 文件名。

- `TestdataNG-*`：逻辑上的下一代夹具或场景数据锚点
- `TestsNG-*`：逻辑上的下一代可执行验证锚点
- `OperatorScenarioNG-*`：逻辑上的下一代操作员观测锚点

这些都是故事层的逻辑锚点，而不是强制要求的目录命名。未来的 `TestsNG` 与 `TestdataNG` 资产可以自行选择具体文件系统布局，只要它们实现的是同一份故事契约。

仓库为这些未来资产定义了一套规范布局，这样故事锚点在需要落到具体路径时也能稳定映射。

## NG 验证资产布局

规范的 NG 验证根目录是：

- `TestdataNG/`：场景夹具与批准的 golden 输出
- `TestsNG/`：可执行验证模块
- `OperatorScenarioNG/`：面向操作员的 narrative 或日志观测场景

USNG 故事卡仍然以逻辑锚点作为规范契约表面；只有在需要落到仓库中的具体路径时，才通过对应根目录下的 README 解析：

- `TestdataNG/README.md`
- `TestsNG/README.md`
- `OperatorScenarioNG/README.md`

逻辑 NG 资产锚点现在遵循以下形式：

- `<AssetType>-REPO-<repo-topology>-GENCODEDESC-<metadata-topology>-HISTORY-<complexity>-SCOPE-<scope>-<NN>[-<VARIANT>]`
- 其中 4D 主坐标必须与所属 USNG 故事一致
- `[-<VARIANT>]` 为可选后缀，仅在同一故事需要多个已批准夹具、可执行验证或操作员观测形态时才添加

## 面向 UserGuide 的结构

USNG 现在使用 4D 故事索引作为主命名规则。`LS`、`PA`、`PG`、`SC`、`AB`、`CA` 这类旧家族桶不再属于规范性故事 ID。

新的主阅读顺序是：

1. 仓库拓扑
2. `genCodeDesc` 拓扑
3. 仓库历史复杂度
4. Scope

`Algorithm A/B` 仍然重要，但它通过 `Support Coordinates`、`Support Snapshot` 与验收条款表达，而不再写进故事 ID 本身。

### Dim A：仓库拓扑

- `REPO-GIT-LOCAL`：直接分析本地 Git checkout
- `REPO-GIT-REMOTE`：通过逻辑或远程风格 Git 身份进入，但执行仍解析到受支持的运行时路径
- `REPO-SVN-LOCAL`：直接分析本地 SVN 仓库或 `file:///` URL
- `REPO-SVN-REMOTE`：通过 SVN 历史访问分析远程风格 SVN URL
- `REPO-SHARED`：一张故事卡有意跨越多个仓库拓扑

### Dim B：genCodeDesc 拓扑

- `GENCODEDESC-LOCAL`：元数据通过本地目录提供，例如 `--genCodeDescSetDir`
- `GENCODEDESC-REMOTE`：元数据在概念上来自外部 provider 或服务
- `GENCODEDESC-SHARED`：一张故事卡有意同时适用于本地与 provider 侧元数据路径

### Dim C：历史复杂度

- `HISTORY-SIMPLE`：线性单分支基线、直接 parity 基线或仅 scope 契约
- `HISTORY-COMPLICATED`：覆盖、删除、重命名、混合提交链或有限 merge-aware 流程
- `HISTORY-COMPLEX`：大型仓库、深历史、多分支汇聚或生产规模发布收敛

### Dim D：Scope

- `SCOPE-A`、`SCOPE-B`、`SCOPE-C`、`SCOPE-D`：四个测量 scope
- `SCOPE-ALL`：跨 scope 故事卡
- `SCOPE-RUNTIME`：不归属于某一个测量 scope 的 operator 或 guardrail 故事卡

### 4D USNG ID 语法

所有规范性故事 ID 现在都遵循以下形式：

`USNG-REPO-<repo-topology>-GENCODEDESC-<metadata-topology>-HISTORY-<complexity>-SCOPE-<scope>-<NN>`

其中：

- `<NN>` 是稳定故事序号，不是家族代码
- `Algorithm A/B` 有意不编码进 ID
- `TestdataNG-*`、`TestsNG-*` 与 `OperatorScenarioNG-*` 这类逻辑场景锚点仍然是独立层，但现在会复用所属故事的 4D 主坐标，并只在需要时附加 `-GIT`、`-SVN`、`-SVN-PARITY` 或 `-AI-TO-HUMAN-SHAPE` 这类可选变体后缀

## UserGuide 运行时故事地图

这一节现在是主导航地图。

### Git 本地仓库 + genCodeDesc 本地

- `HISTORY-SIMPLE / SCOPE A`：本地基线测量故事卡与单分支 period-added 基线
- `HISTORY-SIMPLE / SCOPE B/C/D`：scope 扩展与 Algorithm B scope 支持故事卡
- `HISTORY-COMPLICATED / SCOPE A`：覆盖、删除、重命名、混合窗口与 merge-aware 故事卡
- `HISTORY-COMPLEX / SCOPE A`：大型仓库、深历史、多分支与生产规模 Git 故事卡
- `SCOPE-RUNTIME`：Git 本地运行时硬化故事卡

### Git 本地仓库 + genCodeDesc Shared

- 基线存活快照故事、基线 period-added 契约与 Git 生产规模 gate 这几类共享元数据拓扑契约

### Git 远程身份仓库 + genCodeDesc 本地

- 故事契约沿用与 Git 本地相同的测量故事卡
- 这里的区别是操作员入口与运行时寻址，而不是契约不同

### SVN 本地仓库 + genCodeDesc 本地

- `HISTORY-SIMPLE / SCOPE A`：共享基线与 parity 故事卡，以及被防守的 Algorithm B SVN 子集
- `HISTORY-COMPLEX / SCOPE A`：生产规模 SVN gate
- `SCOPE B/C/D`：只使用那些明确声明 shared 或 SVN-valid 支持的故事卡

### SVN 远程仓库 + genCodeDesc 本地

- 故事契约沿用与 SVN 本地相同的测量故事卡
- 这里的区别是远程仓库访问，而不是 `file:///` 入口

### 任意仓库拓扑 + genCodeDesc 远程

- 当操作员关心的是 provider 侧元数据获取时，使用 `GENCODEDESC-SHARED` 或 `GENCODEDESC-REMOTE` 的故事卡
- 这一视角下的主要锚点仍然是基线存活快照契约、基线 period-added 契约，以及生产规模 gates

## 如何阅读本文档

每张重写后的故事卡都使用同一种结构：

- `NG Story ID`：按 `REPO -> GENCODEDESC -> HISTORY -> SCOPE -> sequence` 排列的 4D 主标识符
- `WHO`：用户角色或操作员角色
- `WHEN`：触发时机或业务时刻
- `WHERE`：故事成立的仓库、运行时或 Scope 上下文
- `WHAT`：该角色希望分析器完成什么
- `WHY`：该结果为什么重要
- `HOW`：使故事具体成立的支持路径、支持坐标或证据形态
- `Story Sentence`：经典 `As a ... I want ... so that ...` 形式
- `Support Coordinates`：界定当前支持单元的 scope、algorithm、VCS 与验证层级
- `Support Snapshot`：不过度宣称的当前支持状态
- `Scenario Anchors`：逻辑上的 NG 验证锚点，而不是具体文件系统路径
- `Acceptance Criteria`：目标形式是经典 `GIVEN ... WHEN ... THEN ...` 契约

在本文档中：

- 先从 `UserGuide 运行时故事地图` 找到操作员视角的运行桶。
- 再读取 `NG Story ID` 的 4D 前缀，确认仓库拓扑、元数据拓扑、历史复杂度与 scope。
- 最后阅读下方详细故事卡；它们仍然是规范性的契约层。
- 下方详细故事只是在长文档中帮助扫描阅读而进行的分组；它们是次级组织方式，主入口仍然是上面的 UserGuide 运行时视角。
- `Scenario Anchors` 应先被理解为逻辑上的 `TestdataNG-*`、`TestsNG-*` 或 `OperatorScenarioNG-*` 锚点；当确实需要映射到仓库中的具体路径时，再通过对应的 NG 资产 README 解析。
- 追踪查找现在只保留在本文档末尾的附录中。
- 每张故事卡都显式出现 `WHO`、`WHEN / Scenario`、`WHAT`、`WHY`。
- `WHERE` 通常通过故事情境与场景锚点体现。
- `Support Coordinates` 在 4D ID 之上补充 algorithm、VCS 与验证层级，而不是替代 4D ID。
- `HOW` 通常体现在支持坐标、支持快照与可执行锚点中。
- 经典故事句仍然是规范性故事陈述，5W1H 字段用于补强而不是替代它。
- 下方所有验收段都使用故事内局部条款 ID，例如 `AC-01`、`AC-ALG-A-01` 与 `AC-ALG-B-01`，并显式采用 `GIVEN / WHEN / THEN` 结构。

## 导航

### 4D 视图

- 仓库拓扑：`REPO-GIT-LOCAL`、`REPO-GIT-REMOTE`、`REPO-SVN-LOCAL`、`REPO-SVN-REMOTE`、`REPO-SHARED`
- 元数据拓扑：`GENCODEDESC-LOCAL`、`GENCODEDESC-REMOTE`、`GENCODEDESC-SHARED`
- 历史复杂度：`HISTORY-SIMPLE`、`HISTORY-COMPLICATED`、`HISTORY-COMPLEX`
- Scope：`SCOPE-A`、`SCOPE-B`、`SCOPE-C`、`SCOPE-D`、`SCOPE-ALL`、`SCOPE-RUNTIME`
- Algorithm：保留在 `Support Coordinates` 中，不编码进故事 ID

## 详细故事卡

## 存活快照契约故事

这些故事描述主存活快照指标：在请求时间窗口内其当前版本发生过变化、并且在 `endTime` 仍然存活的源码行中的 AI 占比。

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01: 计算请求时间窗口内存活变更源码的加权 AI 占比

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当分析者针对一个仓库分支、一个请求窗口 `startTime~endTime` 发起查询，并需要 `endTime` 时刻的最终存活快照答案
- `WHAT`: 计算当前版本在请求窗口内发生变化的存活源码行的加权 AI 占比
- `WHY`: 了解当前仍然存活的变更源码中，有多少可以归因于 AI
- `Story Sentence`: As a repository analyst, I want to calculate the weighted AI ratio for live source-code lines whose current version falls in a requested period `startTime~endTime`, so that I can know how much of the current live changed source code is attributable to AI.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=git and svn`, `tier=Fast`
- `Support Snapshot`: `Algorithm A` 在本故事已批准的基线场景上覆盖 Git 与 SVN。`Algorithm B` 在同一组已批准的 story-01 场景上覆盖狭义 Git 与 SVN 的存活快照回放。
- `Scenario Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT`, `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 一个用于存活快照指标的查询 `repo + branch + startTime + endTime`
- `WHEN`: 分析器在 `endTime` 计算最终结果
- `THEN`: 它返回且只返回一个仓库级最终结果，用于描述截至 `endTime` 时，其当前版本在 `startTime~endTime` 内新增或修改、并且仍然存活的源码行中的 AI 占比

**`AC-02`**

- `GIVEN`: 外部 `genCodeDesc` 记录存储在仓库之外，并按 `repoURL + repoBranch + revisionId` 索引
- `WHEN`: 分析器从最终存活快照中发现落入统计范围的来源修订
- `THEN`: 它在聚合过程中获取并使用匹配的元数据记录

**`AC-03`**

- `GIVEN`: 针对请求仓库窗口的分析成功完成
- `WHEN`: 最终结果被返回或序列化
- `THEN`: 结果仍然保持协议形态，并在 `REPOSITORY` 中包含仓库身份信息，在 `SUMMARY` 中包含聚合结果值

**`AC-04`**

- `GIVEN`: 某个实现路径声称支持 `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01`
- `WHEN`: 该路径使用批准场景进行验证
- `THEN`: 产出结果与该场景的 golden 输出一致

**`AC-ALG-A-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT` 场景
- `WHEN`: 当前 `Algorithm A` 路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-A-02`**

- `GIVEN`: 批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN` 场景
- `WHEN`: 当前 `Algorithm A` 的 SVN 路径在同一基线指标上执行
- `THEN`: 同一份可观察的 `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01` 契约继续成立

**`AC-ALG-B-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT` 回放场景
- `WHEN`: 当前狭义 `Algorithm B` Git 存活快照路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-02`**

- `GIVEN`: 批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN` 回放场景
- `WHEN`: 当前狭义 `Algorithm B` SVN 存活快照路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-03`**

- `GIVEN`: 当前 `Algorithm B` 针对 `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01` 的证据
- `WHEN`: 文档或路线图讨论其支持边界
- `THEN`: 它必须被表述为针对已批准 story-01 场景的狭义存活快照回放支持，而不是对 `Algorithm A` 历史处理能力的整体替代

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02: 人工重写会移除之前的 AI 归因

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当某次人工修订在 `endTime` 之前覆盖了先前归因给 AI 的代码
- `WHAT`: 将有效归因重置到较新的人工修订
- `WHY`: 防止旧的 AI 归属继续附着在已被覆盖的代码上
- `Story Sentence`: As a repository analyst, I want a human rewrite of a previously AI-generated line to reset attribution to the newer human revision, so that old AI ownership does not remain attached to overwritten code.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=shared story with current narrow B Git slice`, `tier=Fast`
- `Support Snapshot`: 已有 `Algorithm A` 证据。`Algorithm B` 证据是面向本故事已批准场景的狭义 Git 存活快照回放。
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 先前归因给 AI 的代码在 `endTime` 之前被后续人工修订所替换
- `WHEN`: 面向 `endTime` 存活变更源码集合生成最终记录
- `THEN`: 它反映较新的仓库状态，而不会保留过时的 AI 归属

**`AC-02`**

- `GIVEN`: 针对请求仓库窗口的分析成功完成
- `WHEN`: 最终结果被返回或序列化
- `THEN`: 结果仍然保持协议形态，并在 `REPOSITORY` 中包含仓库身份信息，在 `SUMMARY` 中包含聚合值

**`AC-03`**

- `GIVEN`: 某个实现路径声称支持 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02`
- `WHEN`: 该路径使用批准场景进行验证
- `THEN`: 产出结果与该场景的 golden 输出一致

**`AC-ALG-A-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02` 场景
- `WHEN`: 当前 `Algorithm A` 路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02` 回放场景
- `WHEN`: 当前狭义 `Algorithm B` Git 存活快照路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-02`**

- `GIVEN`: 当前 `Algorithm B` 针对 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02` 的证据
- `WHEN`: 文档或路线图讨论其支持边界
- `THEN`: 它必须被表述为针对本故事已批准场景的狭义 Git 存活快照回放支持，而不是对其他复杂历史形态的笼统支持

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03: AI 重写会取代之前的人类归属

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当较晚的 AI 修订在 `endTime` 之前覆盖了先前由人类编写的代码行
- `WHAT`: 让后续 AI 重写成为有效归因来源
- `WHY`: 确保 `endTime` 时刻的存活变更源码反映最新的 AI 贡献
- `Story Sentence`: As a repository analyst, I want a later AI rewrite of a human line to become the effective attribution source, so that the live changed source code at `endTime` reflects the latest AI contribution.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=shared story with current narrow B Git slice`, `tier=Fast`
- `Support Snapshot`: 已有 `Algorithm A` 证据。`Algorithm B` 证据是面向本故事已批准场景的狭义 Git 存活快照回放。
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 较晚修订在 `endTime` 之前引入了新的 AI 归因代码
- `WHEN`: 面向 `endTime` 的存活变更源码状态生成最终记录
- `THEN`: 它反映该较新的 AI 贡献

**`AC-02`**

- `GIVEN`: 针对请求仓库窗口的分析成功完成
- `WHEN`: 最终结果被返回或序列化
- `THEN`: 结果仍然保持协议形态，并在 `REPOSITORY` 中包含仓库身份信息，在 `SUMMARY` 中包含聚合值

**`AC-03`**

- `GIVEN`: 某个实现路径声称支持 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03`
- `WHEN`: 该路径使用批准场景进行验证
- `THEN`: 产出结果与该场景的 golden 输出一致

**`AC-ALG-A-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03` 场景
- `WHEN`: 当前 `Algorithm A` 路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03` 回放场景
- `WHEN`: 当前狭义 `Algorithm B` Git 存活快照路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-02`**

- `GIVEN`: 当前 `Algorithm B` 针对 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03` 的证据
- `WHEN`: 文档或路线图讨论其支持边界
- `THEN`: 它必须被表述为针对本故事已批准场景的狭义 Git 存活快照回放支持，而不是对其他复杂历史形态的笼统支持

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04: 已删除的 AI 代码行不得计入

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当时间窗口较早时刻存在过的 AI 生成代码行，在 `endTime` 的分支状态中已经不存在
- `WHAT`: 将已删除 AI 行同时从分子和分母中排除
- `WHY`: 让结果只反映当前仍然存活的变更快照
- `Story Sentence`: As a repository analyst, I want deleted AI-generated lines to disappear from both numerator and denominator, so that the result reflects only the current live changed source-code snapshot.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=shared story with current narrow B Git slice`, `tier=Fast`
- `Support Snapshot`: 已有 `Algorithm A` 证据。`Algorithm B` 证据是面向本故事已批准场景的狭义 Git 存活快照回放。
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 先前归因给 AI 的代码在 `endTime` 的分支状态中已经不存在
- `WHEN`: 针对存活变更源码结果生成最终记录
- `THEN`: 这些已删除代码被排除在结果之外

**`AC-02`**

- `GIVEN`: 针对请求仓库窗口的分析成功完成
- `WHEN`: 最终结果被返回或序列化
- `THEN`: 结果仍然保持协议形态，并在 `REPOSITORY` 中包含仓库身份信息，在 `SUMMARY` 中包含聚合值

**`AC-03`**

- `GIVEN`: 某个实现路径声称支持 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04`
- `WHEN`: 该路径使用批准场景进行验证
- `THEN`: 产出结果与该场景的 golden 输出一致

**`AC-ALG-A-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04` 场景
- `WHEN`: 当前 `Algorithm A` 路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04` 回放场景
- `WHEN`: 当前狭义 `Algorithm B` Git 存活快照路径执行
- `THEN`: 它必须被表述为针对本故事已批准场景的狭义 Git 存活快照回放支持，而不是对其他复杂历史形态的笼统支持

**`AC-ALG-B-02`**

- `GIVEN`: 当前 `Algorithm B` 针对 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04` 的证据
- `WHEN`: 文档或路线图讨论其支持边界
- `THEN`: 它必须被表述为针对本故事已批准场景的狭义 Git 存活快照回放支持，而不是对其他复杂历史形态的笼统支持

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05: 重命名必须保留归因谱系

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当文件在 `endTime` 之前发生重命名或移动，但其有效内容贡献没有变化
- `WHAT`: 在仅路径变化的历史变更下保留逐行归因
- `WHY`: 防止只有重命名的变化扭曲最终存活变更源码占比
- `Story Sentence`: As a repository analyst, I want file rename or move operations to preserve line attribution when content does not change, so that the final live changed source-code ratio is not distorted by path-only history changes.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=shared story with current narrow B Git slice`, `tier=Fast`
- `Support Snapshot`: 已有 `Algorithm A` 证据。`Algorithm B` 证据是面向本故事已批准场景的狭义 Git 存活快照回放。
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 文件在 `endTime` 之前发生重命名或移动，但其有效贡献未变
- `WHEN`: 面向 `endTime` 的存活变更源码集合生成最终记录
- `THEN`: 结果在仅路径变化的历史下仍然稳定

**`AC-02`**

- `GIVEN`: 针对请求仓库窗口的分析成功完成
- `WHEN`: 最终结果被返回或序列化
- `THEN`: 结果仍然保持协议形态，并在 `REPOSITORY` 中包含仓库身份信息，在 `SUMMARY` 中包含聚合值

**`AC-03`**

- `GIVEN`: 某个实现路径声称支持 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05`
- `WHEN`: 该路径使用批准场景进行验证
- `THEN`: 产出结果与该场景的 golden 输出一致

**`AC-ALG-A-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05` 场景
- `WHEN`: 当前 `Algorithm A` 路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05` 回放场景
- `WHEN`: 当前狭义 `Algorithm B` Git 存活快照路径执行
- `THEN`: 它必须被表述为针对本故事已批准场景的狭义 Git 存活快照回放支持，而不是对其他复杂历史形态的笼统支持

**`AC-ALG-B-02`**

- `GIVEN`: 当前 `Algorithm B` 针对 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05` 的证据
- `WHEN`: 文档或路线图讨论其支持边界
- `THEN`: 它必须被表述为针对本故事已批准场景的狭义 Git 存活快照回放支持，而不是对其他复杂历史形态的笼统支持

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06: 在单个请求窗口内解析混合多提交历史

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当一个请求窗口中包含多个提交，并同时出现纯人工、纯 AI、重写与删除等混合路径
- `WHAT`: 让每一条存活行都按窗口内最新的有效归因被解析
- `WHY`: 即使窗口内历史混杂且复杂，也能保持单一最终结果正确
- `Story Sentence`: As a repository analyst, I want one requested window to correctly resolve mixed line histories across many commits, so that the final result remains correct when human-only lines, AI-only lines, human-then-AI rewrites, AI-then-human rewrites, and deleted AI lines all appear in the same period.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=shared story with current narrow B Git slice`, `tier=Fast`
- `Support Snapshot`: 已有 `Algorithm A` 证据。`Algorithm B` 证据是面向本故事已批准场景的狭义 Git 存活快照回放。
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 请求窗口内的多个提交在不同存活行上包含混合的归属迁移
- `WHEN`: 分析器在 `endTime` 解析存活变更源码集合
- `THEN`: 它仍然只产出一个最终记录，并使用每条存活行最新的有效归因

**`AC-02`**

- `GIVEN`: 某条存活行在窗口内经历了一长串中间修订链
- `WHEN`: 分析器在 `endTime` 解析这条存活行
- `THEN`: 它使用最新的有效存活归因，而不会让已被覆盖的中间归属泄漏进最终结果

**`AC-03`**

- `GIVEN`: 针对请求仓库窗口的分析成功完成
- `WHEN`: 最终结果被返回或序列化
- `THEN`: 结果仍然保持协议形态，并在 `REPOSITORY` 中包含仓库身份信息，在 `SUMMARY` 中包含聚合值

**`AC-04`**

- `GIVEN`: 某个实现路径声称支持 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06`
- `WHEN`: 该路径使用批准场景进行验证
- `THEN`: 产出结果与该场景的 golden 输出一致

**`AC-ALG-A-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06` 场景
- `WHEN`: 当前 `Algorithm A` 路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06` 回放场景
- `WHEN`: 当前狭义 `Algorithm B` Git 存活快照路径执行
- `THEN`: 它必须被表述为针对本故事已批准场景的狭义 Git 存活快照回放支持，而不是对其他复杂历史形态的笼统支持

**`AC-ALG-B-02`**

- `GIVEN`: 当前 `Algorithm B` 针对 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06` 的证据
- `WHEN`: 文档或路线图讨论其支持边界
- `THEN`: 它必须被表述为针对本故事已批准场景的狭义 Git 存活快照回放支持，而不是对其他复杂历史形态的笼统支持

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07: 合并提交必须保留有效归因

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当被合并的分支在 `endTime` 前将人工与 AI 贡献一起带入目标分支
- `WHAT`: 在合并过程中保留每条存活行的有效归因
- `WHY`: 防止 merge commit 重置归属或把谱系压平
- `Story Sentence`: As a repository analyst, I want merged branch content to preserve the effective attribution of surviving lines, so that a merge operation does not incorrectly reset line ownership to the merge commit itself.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=shared story with current narrow B Git slice`, `tier=Fast`
- `Support Snapshot`: 已有 `Algorithm A` 证据。`Algorithm B` 证据是面向本故事已批准场景的狭义 Git 存活快照回放。
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 某个 merge commit 在 `endTime` 之前把更早的人工与 AI 归因变更汇合在一起
- `WHEN`: 面向 `endTime` 的存活变更源码集合生成最终记录
- `THEN`: 它使用的是合并后仍然存活行的有效归因，而不是把 merge commit 当成统一来源

**`AC-02`**

- `GIVEN`: 多个分支在 `endTime` 前被合并，并且存活行来自不同被合并分支
- `WHEN`: 分析器解析最终存活状态
- `THEN`: 它逐条保留这些存活行，而不会把归属压缩成 merge commit 或最终分支身份

**`AC-03`**

- `GIVEN`: 针对请求仓库窗口的分析成功完成
- `WHEN`: 最终结果被返回或序列化
- `THEN`: 结果仍然保持协议形态，并在 `REPOSITORY` 中包含仓库身份信息，在 `SUMMARY` 中包含聚合值

**`AC-04`**

- `GIVEN`: 某个实现路径声称支持 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07`
- `WHEN`: 该路径使用批准场景进行验证
- `THEN`: 产出结果与该场景的 golden 输出一致

**`AC-ALG-A-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07` 场景
- `WHEN`: 当前 `Algorithm A` 路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07` 回放场景
- `WHEN`: 当前狭义 `Algorithm B` Git 存活快照路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-02`**

- `GIVEN`: 当前 `Algorithm B` 针对 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07` 的证据
- `WHEN`: 文档或路线图讨论其支持边界
- `THEN`: 它必须被表述为针对本故事已批准场景的狭义 Git 存活快照回放支持，而不是对其他复杂历史形态的笼统支持

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08: Git 与 SVN 必须遵循同一结果契约

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当相同主指标针对语义等价的 Git 与 SVN 支持历史发起查询
- `WHAT`: 让查询结果契约在不同 VCS 目标之间保持一致
- `WHY`: 确保更换 VCS 类型不会改变指标语义或输出结构
- `Story Sentence`: As a repository analyst, I want Git and SVN targets to follow the same query-result contract for the current primary metric, so that changing VCS type does not change metric semantics or output structure.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and current narrow B parity slice`, `vcs=git and svn`, `tier=Fast`
- `Support Snapshot`: Git 与 SVN 的一致性已通过 `Algorithm A` 建立；狭义 Git/SVN `Algorithm B` 契约一致性建立在已批准的 story-01 Git/SVN 场景与已批准的 story-08 SVN parity 场景之上。
- `Scenario Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08-SVN-PARITY`，以及已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT` 与 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN` 基线场景

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 同一请求窗口下，等价的受支持仓库历史可以用 Git 或 SVN 表示
- `WHEN`: 分析当前主指标
- `THEN`: Git 与 SVN 都产出一个最终记录，并保持相同的指标语义与协议形态结构，只允许在 VCS 专属的仓库身份细节上不同

**`AC-02`**

- `GIVEN`: 针对请求仓库窗口的分析成功完成
- `WHEN`: 最终结果被返回或序列化
- `THEN`: 结果仍然保持协议形态，并在 `REPOSITORY` 中包含仓库身份信息，在 `SUMMARY` 中包含聚合值

**`AC-03`**

- `GIVEN`: 某个受支持的 VCS 专属路径声称支持 `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08`
- `WHEN`: 该路径使用批准的一致性场景进行验证
- `THEN`: 产出结果与该场景的 golden 输出一致

**`AC-GIT-01`**

- `GIVEN`: 当前主指标的 Git 路径
- `WHEN`: 它通过基线存活快照场景进行验证
- `THEN`: 它构成可观察一致性契约的一侧

**`AC-SVN-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08-SVN-PARITY` 场景
- `WHEN`: 当前 SVN 路径执行
- `THEN`: 在保持共享 `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08` 契约的前提下，产出结果与该 parity 场景批准的 NG golden 输出一致

**`AC-SVN-02`**

- `GIVEN`: 由于 SVN 的路径历史或 blame 差异，需要采用 VCS 专属的一致性形态
- `WHEN`: 设计一致性场景
- `THEN`: 只要可观察的结果契约不变，就可以使用可辩护的 SVN 专属仓库形态

**`AC-ALG-B-01`**

- `GIVEN`: 作为当前一致性场景的、批准的狭义 `Algorithm B` Git 与 SVN 存活快照基线夹具路径
- `WHEN`: 使用它们进行验证
- `THEN`: 它们在 Git 与 SVN 上产出相同的协议形态可观察契约，只允许在 VCS 专属仓库身份字段上不同

**`AC-ALG-B-02`**

- `GIVEN`: 当前 `Algorithm B` 针对 `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08` 的证据
- `WHEN`: 文档或路线图讨论其支持边界
- `THEN`: 它必须被表述为建立在已批准 story-01 与 story-08 场景之上的狭义一致性，而不是覆盖所有支持拓扑的跨故事 Git/SVN 完整一致性

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09: 大型仓库快照必须保持结果语义

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当仓库包含大量文件与大量存活行，但分析者仍期待同一套指标语义
- `WHAT`: 为大型真实仓库保留同一份存活快照契约
- `WHY`: 让聚合结果在更大规模仓库上仍然可信
- `Story Sentence`: As a repository analyst, I want the analyzer to keep the same result semantics when the repository contains many source files and many live lines, so that the final aggregate result remains correct for realistic large codebases.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and current narrow B Git slice`, `vcs=shared story`, `tier=Fast`
- `Support Snapshot`: 已有 `Algorithm A` 证据。`Algorithm B` 证据是面向本故事已批准场景的狭义 Git 存活快照回放，并带有聚焦的真实本地 Git 证明。
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: `endTime` 的最终存活快照横跨大量源码文件与大量存活代码行
- `WHEN`: 分析器计算最终聚合结果
- `THEN`: 它仍然只产出一个仓库级最终结果，并保持与小型仓库相同的指标语义与协议形态

**`AC-02`**

- `GIVEN`: 大型仓库快照在多个文件中包含大量落入范围的代码行
- `WHEN`: 分析器进行聚合
- `THEN`: 仓库规模或文件数量不会改变逐行归因规则、仓库身份规则或最终 `SUMMARY` 字段的含义

**`AC-03`**

- `GIVEN`: 某个实现路径声称支持 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09`
- `WHEN`: 该路径使用批准场景进行验证
- `THEN`: 产出结果与该场景的 golden 输出一致

**`AC-ALG-A-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09` 场景
- `WHEN`: 当前 `Algorithm A` 路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 通过夹具回放工件或聚焦的真实本地 Git 回放路径表达的、已批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09` 场景
- `WHEN`: 当前狭义 `Algorithm B` Git 存活快照路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-02`**

- `GIVEN`: 当前 `Algorithm B` 针对 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09` 的证据
- `WHEN`: 文档或路线图讨论其支持边界
- `THEN`: 它必须被表述为针对本故事已批准场景、并带有聚焦真实本地 Git 证明的狭义 Git 存活快照回放支持，而不是完整矩阵就绪的大快照可扩展性支持

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10: 深历史必须保持最新有效归因

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当 `endTime` 时刻的存活行来自很长的修订链，并带有多次中间重写
- `WHAT`: 让每条存活行按最新有效归因解析，而不是按已被覆盖的中间归属解析
- `WHY`: 防止深历史扭曲最终存活结果
- `Story Sentence`: As a repository analyst, I want long revision chains to preserve the latest effective attribution of each surviving line, so that many intermediate rewrites do not distort the final live result.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and current narrow B Git slice`, `vcs=shared story`, `tier=Fast`
- `Support Snapshot`: 已有 `Algorithm A` 证据。`Algorithm B` 证据是面向本故事已批准场景的狭义 Git 存活快照回放，并带有聚焦的真实本地 Git 证明。
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: `endTime` 时刻落入范围的存活行依赖很长的修订链，并且存在许多中间重写
- `WHEN`: 分析器解析每条存活行
- `THEN`: 它使用最新的有效存活归因，而不是链上更早且已被覆盖的修订

**`AC-02`**

- `GIVEN`: 长历史链在 `endTime` 前包含 human-to-AI 与 AI-to-human 两类迁移
- `WHEN`: 生成最终聚合结果
- `THEN`: 已删除或已被覆盖的中间状态不会泄漏到结果中

**`AC-03`**

- `GIVEN`: 某个实现路径声称支持 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10`
- `WHEN`: 该路径使用批准场景进行验证
- `THEN`: 产出结果与该场景的 golden 输出一致

**`AC-ALG-A-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10` 场景
- `WHEN`: 当前 `Algorithm A` 路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 通过夹具回放工件或聚焦的真实本地 Git 回放路径表达的、已批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10` 场景
- `WHEN`: 当前狭义 `Algorithm B` Git 存活快照路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-02`**

- `GIVEN`: 当前 `Algorithm B` 针对 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10` 的证据
- `WHEN`: 文档或路线图讨论其支持边界
- `THEN`: 它必须被表述为针对本故事已批准场景、并带有聚焦真实本地 Git 证明的狭义 Git 存活快照回放支持，而不是完整矩阵就绪的 deep-history 支持

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11: 单个窗口内的大量分支合并必须保留逐行归因

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当许多分支在一个请求窗口内被合并进目标分支
- `WHAT`: 在分支密集的合并历史中保留逐行有效归因
- `WHY`: 防止分支汇聚与合并顺序扭曲最终结果
- `Story Sentence`: As a repository analyst, I want branch-heavy history inside one requested window to preserve per-line effective attribution, so that integrating many feature branches into the target branch does not distort the final result.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and current narrow B Git slice`, `vcs=shared story with SVN analogue note`, `tier=Fast`
- `Support Snapshot`: 已有 `Algorithm A` 证据。`Algorithm B` 证据是面向本故事已批准场景的狭义 Git 存活快照回放。SVN 一致性可能需要可辩护的类比场景，而不是字面上的同文件 Git 移植。
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 许多分支在 `endTime` 之前被合并进目标分支
- `WHEN`: 分析器针对 `endTime` 的存活变更源码集合计算最终结果
- `THEN`: 它仍然只产出一个仓库级最终结果

**`AC-02`**

- `GIVEN`: 存活行来自不同被合并分支，并且它们拥有不同的有效历史
- `WHEN`: 分析器解析最终存活状态
- `THEN`: 它逐条保留这些存活行，而不会把归属压平为 merge commit、分支标签或合并顺序

**`AC-03`**

- `GIVEN`: 某个实现路径声称支持 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11`
- `WHEN`: 该路径使用批准场景进行验证
- `THEN`: 产出结果与该场景的 golden 输出一致

**`AC-ALG-A-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11` 场景
- `WHEN`: 当前 `Algorithm A` 路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-A-02`**

- `GIVEN`: 同一广义契约的 SVN 一致性需要一个可辩护的类比场景
- `WHEN`: 对 SVN 来说，字面上的同文件 Git 形态会造成误导
- `THEN`: 可以使用 SVN 专属类比场景，只要共享的可观察契约保持不变

**`AC-ALG-B-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11` 回放场景
- `WHEN`: 当前狭义 `Algorithm B` Git 存活快照路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-02`**

- `GIVEN`: 当前 `Algorithm B` 针对 `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11` 的证据
- `WHEN`: 文档或路线图讨论其支持边界
- `THEN`: 它必须被表述为针对本故事已批准场景的狭义 Git 存活快照回放支持，而不是完整矩阵就绪的分支密集 merge 支持

## Heavy 生产 Gate

这些故事不是普通的小型功能故事，而是生产 gate。它们依然是角色驱动的故事，但场景被明确设定为 heavy、生产导向。

### USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12: Git 生产规模本地仓库在分支密集发布收敛下仍必须保持正确

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当需要在一个模拟发布收敛的大规模分支型本地 Git 仓库上验证生产就绪性
- `WHAT`: 让 `Algorithm A + Scope A` 在生产规模本地 Git 拓扑上保持正确
- `WHY`: 证明大量分支、深历史与混合发布合并不会扭曲最终存活归因结果
- `Story Sentence`: As a repository analyst, I want Algorithm A and Scope A to remain correct on a production-scale local Git repository, so that large branch counts, deep history, and hybrid release merges do not distort the final live attribution result.
- `Support Coordinates`: `scope=A baseline`, `algorithm=A`, `vcs=git`, `tier=Heavy`
- `Support Snapshot`: 面向生产的 heavy gate，包含真实本地 Git 仓库生成，以及正确性与可扩展性检查。
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12`

Acceptance Criteria

**`AC-GIT-01`**

- `GIVEN`: 一个本地 Git 仓库呈现出生产式拓扑，在 `endTime` 前大致具有 `100+` 分支、`1000+` 提交，以及反复的 feature-to-integration-to-release 合并汇聚
- `WHEN`: 分析器针对 `endTime` 的存活变更源码集合计算最终结果
- `THEN`: 它仍然只产出一个仓库级最终结果

**`AC-GIT-02`**

- `GIVEN`: 存活行通过直接合并、集成分支与分阶段收敛等混合路径进入 release 分支
- `WHEN`: 解析最终归因
- `THEN`: 归因基于每条存活行的有效来源修订，而不是 merge 形态、first-parent 历史或分支命名

**`AC-GIT-03`**

- `GIVEN`: 生产式仓库是本地仓库而不是远端托管仓库
- `WHEN`: 把它用作生产就绪验收场景
- `THEN`: 这样做仍然有效，因为传输层不在范围内，而历史语义除了网络访问外必须保持一致

**`AC-GIT-04`**

- `GIVEN`: heavy Git 生产规模场景成功完成
- `WHEN`: 评估其验收结果
- `THEN`: 它同时验证最终聚合结果的正确性，以及有界元数据复用或有界修订时间查找复用等可扩展性导向行为

### USNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13: SVN 生产规模本地仓库在分支与合并压力下仍必须保持正确

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当需要在一个具有分支复制与再集成压力的生产规模本地 SVN 仓库上验证生产就绪性
- `WHAT`: 让 `Algorithm A + Scope A` 在生产规模本地 SVN 拓扑上保持正确
- `WHY`: 证明 SVN 的分支复制、合并与发布再集成在大规模下不会破坏存活归因
- `Story Sentence`: As a repository analyst, I want Algorithm A and Scope A to remain correct on a production-scale local SVN repository, so that SVN branch copying, merges, and release reintegration at scale do not break live attribution.
- `Support Coordinates`: `scope=A baseline`, `algorithm=A`, `vcs=svn`, `tier=Heavy`
- `Support Snapshot`: 面向生产的 heavy gate，包含真实本地 SVN 仓库生成，以及正确性与可扩展性检查。
- `Scenario Anchors`: `TestsNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13`

Acceptance Criteria

**`AC-SVN-01`**

- `GIVEN`: 一个本地 SVN 仓库呈现出生产式拓扑，在 `endTime` 前大致具有 `100+` 分支或分支拷贝、`1000+` 修订，以及反复的 branch-to-release 合并活动
- `WHEN`: 分析器针对 `endTime` 的存活变更源码集合计算最终结果
- `THEN`: 它仍然只产出一个仓库级最终结果

**`AC-SVN-02`**

- `GIVEN`: 存活行通过直接修改、分支拷贝以及合并或再集成历史等混合路径进入 release 路径
- `WHEN`: 在受支持的 SVN 语义下解析最终归因
- `THEN`: 它保留每条存活行的有效来源修订，而不会把归属压缩为合并时机或最终分支路径

**`AC-SVN-03`**

- `GIVEN`: 生产式 SVN 仓库是本地仓库而不是远端托管仓库
- `WHEN`: 把它用作生产就绪验收场景
- `THEN`: 这样做仍然有效，因为传输层不属于归因契约的一部分

**`AC-SVN-04`**

- `GIVEN`: heavy SVN 生产规模场景成功完成
- `WHEN`: 评估其验收结果
- `THEN`: 它同时验证最终聚合结果的正确性，以及分支来源元数据复用、有界修订时间查询或等价显式复用信号等可扩展性导向行为

## Scope 契约故事

这些故事扩展被计数的内容边界。角色保持不变，但场景从“只看源码中发生了什么”转变为“哪些内容家族属于范围内”。

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14: Scope B 源代码含注释时必须把注释行计入总量

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当分析者希望源码文件总量把注释行也作为被测量的源码文本计入
- `WHAT`: 让 `--scope B` 统计源码文件中的所有非空行，包括注释
- `WHY`: 衡量 AI 对源码文件全部文本内容的贡献，而不仅仅是可执行代码
- `Story Sentence`: As a repository analyst, I want `--scope B` to count all non-blank lines in source files, including comment lines, in the aggregate result, so that I can measure AI contribution across the full textual content of source files, not just executable code.
- `Support Coordinates`: `scope=B`, `algorithms=primarily A at story level`, `vcs=shared`, `tier=Fast`
- `Support Snapshot`: 面向包含注释的源码文件总量的第一类 scope 故事。
- `Scenario Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 某个源码文件同时包含代码行与注释行
- `WHEN`: 分析器以 `--scope B` 运行
- `THEN`: `totalCodeLines` 统计源码中的全部非空行，而不只是 `Scope A` 中的纯代码子集

**`AC-02`**

- `GIVEN`: 某个源码文件中存在通过 `codeLines` 覆盖的注释行
- `WHEN`: 分析器以 `--scope B` 运行
- `THEN`: `genRatio 100` 的注释行计入 `fullGeneratedCodeLines`，而 `genRatio` 在 1 到 99 之间的注释行计入 `partialGeneratedCodeLines`

**`AC-03`**

- `GIVEN`: 对同一仓库与元数据使用基线 scope 进行分析
- `WHEN`: 分析器以 `--scope A` 运行
- `THEN`: 注释行仍然被排除，从而保持向后兼容

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-C-15: Scope C 文档文本行必须通过 docLines 协议从文档文件计数

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当分析者希望衡量仅文档贡献，而不是源码贡献
- `WHAT`: 让 `--scope C` 分析文档文件，并通过 `docLines` 进行归因
- `WHY`: 将 AI 对文档工件的贡献与源码贡献分离衡量
- `Story Sentence`: As a repository analyst, I want `--scope C` to analyze documentation text files and use the `docLines` protocol field for AI attribution, so that I can measure AI contribution to documentation artifacts separately from source code.
- `Support Coordinates`: `scope=C`, `algorithms=primarily A at story level`, `vcs=shared`, `tier=Fast`
- `Support Snapshot`: 面向纯文档分析的第一类 scope 故事。
- `Scenario Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-C-15`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 某个仓库包含 `DOC_EXTENSIONS` 中的文件
- `WHEN`: 分析器以 `--scope C` 运行
- `THEN`: 它只包含文档文件，并排除源码文件

**`AC-02`**

- `GIVEN`: 文档文件在 `--scope C` 下被分析
- `WHEN`: 计算归因并输出结果
- `THEN`: 归因使用 `docLines`，输出使用 `totalDocLines`、`fullGeneratedDocLines` 与 `partialGeneratedDocLines`

**`AC-03`**

- `GIVEN`: 对同一仓库使用源码 scope 进行分析
- `WHEN`: 分析器以 `--scope A` 或 `--scope B` 运行
- `THEN`: 文档文件仍被排除，从而保持 scope 隔离

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-D-16: Scope D 全部文本必须将源码与文档统一为单一聚合

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当分析者希望在一个结果中同时覆盖源码文件与文档文件
- `WHAT`: 让 `--scope D` 在一次聚合中统计源码与文档的全部非空行
- `WHY`: 衡量整个仓库全部文本内容上的 AI 总贡献
- `Story Sentence`: As a repository analyst, I want `--scope D` to count all non-blank lines from both source files and documentation files in one combined result, so that I can measure total AI contribution across the entire textual content of the repository.
- `Support Coordinates`: `scope=D`, `algorithms=primarily A at story level`, `vcs=shared`, `tier=Fast`
- `Support Snapshot`: 面向源码与文档统一总量的第一类 scope 故事。
- `Scenario Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-D-16`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 某个仓库同时包含源码文件与文档文件
- `WHEN`: 分析器以 `--scope D` 运行
- `THEN`: 它在一次组合分析中同时包含这两类文件

**`AC-02`**

- `GIVEN`: 源码文件与文档文件都在 `--scope D` 下被分析
- `WHEN`: 计算归因并输出组合结果
- `THEN`: 源码行通过 `codeLines` 归因，文档行通过 `docLines` 归因，而组合 summary 使用 `totalCodeLines`、`fullGeneratedCodeLines` 与 `partialGeneratedCodeLines`

**`AC-03`**

- `GIVEN`: 对同一仓库使用 `--scope A`、`--scope B` 或 `--scope C` 进行分析
- `WHEN`: 分析器评估各自范围外的文件
- `THEN`: 这些文件家族仍被排除，从而保持 scope 隔离

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-17: Scope 一致性矩阵必须确认四种 Scope 都产生正确且隔离的结果

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当分析者在同一个仓库上运行四种 scope，并希望每个 scope 都保持独立且正确
- `WHAT`: 验证 A、B、C、D 的完整 scope 矩阵
- `WHY`: 确认 scope 选择真的控制了测量边界
- `Story Sentence`: As a repository analyst, I want a cross-scope verification that runs Scope A, B, C, and D on the same repository and confirms each produces the expected distinct result, so that I can trust that scope selection genuinely controls the measurement boundary.
- `Support Coordinates`: `scope=A/B/C/D`, `algorithms=primarily A at story level`, `vcs=shared`, `tier=Fast`
- `Support Snapshot`: 面向跨 scope 契约的第一类故事。
- `Scenario Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-17`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 某个仓库同时包含带代码和注释的源码文件，以及文档文件
- `WHEN`: 分析器分别以 `--scope A`、`--scope B`、`--scope C` 与 `--scope D` 运行
- `THEN`: 每个 scope 都按照自己的 scope 定义产出正确 summary

**`AC-02`**

- `GIVEN`: 在同一仓库上执行完整的四 scope 矩阵
- `WHEN`: 跨 scope 比较这些 summary
- `THEN`: `Scope C` 使用文档字段家族 `totalDocLines`、`fullGeneratedDocLines` 与 `partialGeneratedDocLines`，而 `Scopes A`、`B`、`D` 使用代码字段家族 `totalCodeLines`、`fullGeneratedCodeLines` 与 `partialGeneratedCodeLines`

## Algorithm B Scope 扩展故事

这些故事保持同一个分析者角色，但把场景转为更宽 scope 上的回放式归因。

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-18: Algorithm B 必须支持 Scope B

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当分析者需要在源码代码加源码注释的范围内进行回放式归因
- `WHAT`: 让 `--algorithm B --scope B` 统计全部非空源码行，包括注释
- `WHY`: 使用增量回放算法衡量全部源码文本上的 AI 总贡献
- `Story Sentence`: As a repository analyst, I want `--algorithm B --scope B` to count all non-blank source lines including comments during replay, so that I can measure total AI contribution to all source text using the incremental replay algorithm.
- `Support Coordinates`: `scope=B`, `algorithm=B`, `vcs=current supported replay shapes`, `tier=Fast`
- `Support Snapshot`: 面向 Algorithm B 注释纳入型源码回放的第一类故事。
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-18`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: 某个源码文件同时包含代码行与注释行
- `WHEN`: `Algorithm B` 以 `--scope B` 运行
- `THEN`: `totalCodeLines` 统计全部非空源码行

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-19: Algorithm B 必须支持 Scope C

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当分析者需要在文档文件上进行回放式归因，而不是在源码文件上
- `WHAT`: 让 `--algorithm B --scope C` 通过 `docLines` 回放并统计文档文件行
- `WHY`: 使用增量回放算法衡量文档上的 AI 贡献
- `Story Sentence`: As a repository analyst, I want `--algorithm B --scope C` to replay and count documentation file lines using the `docLines` protocol field, so that I can measure AI contribution to documentation using the incremental replay algorithm.
- `Support Coordinates`: `scope=C`, `algorithm=B`, `vcs=current supported replay shapes`, `tier=Fast`
- `Support Snapshot`: 面向 Algorithm B 文档回放的第一类故事。
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-19`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: 某个文档文件包含非空行
- `WHEN`: `Algorithm B` 以 `--scope C` 运行
- `THEN`: 它输出文档字段家族 `totalDocLines`、`fullGeneratedDocLines` 与 `partialGeneratedDocLines`

**`AC-ALG-B-02`**

- `GIVEN`: 该文档文件的协议 `DETAIL` 条目使用 `docLines`
- `WHEN`: `Algorithm B` 在回放中执行逐行比例查找
- `THEN`: 它使用文档协议索引

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-20: Algorithm B 必须支持 Scope D

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当分析者需要在同一次运行中，对源码文件与文档文件同时进行回放式归因
- `WHAT`: 让 `--algorithm B --scope D` 把两类文件一并回放进统一结果
- `WHY`: 使用增量回放算法衡量仓库全部文本内容上的 AI 总贡献
- `Story Sentence`: As a repository analyst, I want `--algorithm B --scope D` to replay both source files and documentation files into a unified result, so that I can measure total AI contribution across all textual repository content using the incremental replay algorithm.
- `Support Coordinates`: `scope=D`, `algorithm=B`, `vcs=current supported replay shapes`, `tier=Fast`
- `Support Snapshot`: 面向 Algorithm B 源码加文档统一回放的第一类故事。
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-20`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: 某个仓库同时包含源码文件与文档文件
- `WHEN`: `Algorithm B` 以 `--scope D` 运行
- `THEN`: 它同时回放这两类文件，对源码文件使用 `codeLines`，对文档文件使用 `docLines`

**`AC-ALG-B-02`**

- `GIVEN`: `Algorithm B` 在 `--scope D` 下产出组合回放结果
- `WHEN`: 输出 summary
- `THEN`: 它使用 `totalCodeLines`、`fullGeneratedCodeLines` 与 `partialGeneratedCodeLines`

## Period-Added 契约故事

这些故事讨论的是窗口期间的贡献，而不是 `endTime` 时刻的库存。角色仍然是分析者，但场景从存活快照测量切换为 period-added 测量。

### USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21: 计算请求周期内新增 AI 代码占比

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当分析者希望衡量的是窗口本身新增的 AI 贡献，而不是窗口结束时的库存
- `WHAT`: 计算 `startTime~endTime` 期间新增了多少 AI 生成代码
- `WHY`: 区分期间贡献与期末库存
- `Story Sentence`: As a repository analyst, I want to calculate how much AI-generated code was added during `startTime~endTime`, so that I can distinguish period contribution from end-of-period inventory.
- `Support Coordinates`: `scope=shared story anchor`, `algorithms=A future and B current narrow baseline`, `vcs=shared story`, `tier=Fast`
- `Support Snapshot`: 这是共享故事锚点；当前可执行路径是狭义 `Algorithm B` Git 基线，通过离线回放与受支持的本地 Git 回放执行。
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: `repo`、`branch`、`startTime` 与 `endTime` 定义了一个请求周期
- `WHEN`: 执行 period contribution 指标
- `THEN`: 它返回且只返回一个仓库级最终结果，用于描述该周期内 AI 新增代码的聚合结果

**`AC-02`**

- `GIVEN`: 一次 period contribution 分析成功完成
- `WHEN`: 最终结果被返回或序列化
- `THEN`: 结果仍然保持协议形态，并在 `REPOSITORY` 中包含仓库身份信息，在 `SUMMARY` 中包含聚合值

**`AC-03`**

- `GIVEN`: 某个实现路径声称支持 `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21`
- `WHEN`: 该路径使用批准场景进行验证
- `THEN`: 产出结果与该场景的 golden 输出一致

**`AC-ALG-A-01`**

- `GIVEN`: 未来某个 `Algorithm A` 路径声称支持该 period contribution 指标
- `WHEN`: 使用共享契约对其进行评估
- `THEN`: 它必须满足共享 `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` 条款，而不会削弱可观察契约

**`AC-ALG-A-02`**

- `GIVEN`: 未来为 `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` 增加了某个 `Algorithm A` 夹具或真实仓库验收场景
- `WHEN`: 为其记录支持层级
- `THEN`: 它必须显式声明 `Fast` 或 `Heavy`

**`AC-ALG-B-01`**

- `GIVEN`: 批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` 场景
- `WHEN`: 当前狭义离线 Git `Algorithm B` 基线路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-02`**

- `GIVEN`: 输入保持在当前狭义 Git 回放边界内
- `WHEN`: CLI 以 `--algorithm B` 运行
- `THEN`: 当前路径可以通过已批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` 回放输入路径或受支持的本地 Git checkout 路径执行本故事

**`AC-ALG-B-03`**

- `GIVEN`: 更宽的 `Algorithm B` 历史形态，例如多文件回放、路径重命名变化或超出已验收故事的 merge-aware 记账
- `WHEN`: 文档或路线图讨论其支持状态
- `THEN`: 这些形态在由其各自验收轨道证明前，仍然保持不支持

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-22: 无合并无重命名的单分支 period-added 基线

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当分析者希望在引入拓扑复杂性之前，先建立最干净的单分支 period-added 基线
- `WHAT`: 在简单线性 Git 历史上证明 `Algorithm B` 的核心 period-added 契约
- `WHY`: 在加入重写、重命名或合并之前，先建立稳定基线
- `Story Sentence`: As a repository analyst, I want a single-branch period-added baseline without merges or renames, so that the core `Algorithm B` period-contribution contract is proven before topology complexity is introduced.
- `Support Coordinates`: `scope=A and B note`, `algorithm=B`, `vcs=git local replay`, `tier=Fast`
- `Support Snapshot`: 面向 Algorithm B 单分支基线的第一类故事。
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-22`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: 一个单分支 Git 仓库包含一个窗口前的人类提交与两个窗口内提交
- `WHEN`: `Algorithm B` 计算 period-added 总量
- `THEN`: 它只统计来源修订落在窗口内的代码行，并且 `fullGeneratedCodeLines` 只统计窗口内由 AI 归因的代码行

**`AC-ALG-B-02`**

- `GIVEN`: 对同一个单分支仓库使用 `Scope B` 进行分析
- `WHEN`: `Algorithm B` 计算 period-added 结果
- `THEN`: 它保持 period-added 语义，同时反映更宽的源码行范围

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-23: 含删除、重置与混合重写的 period-added 记账

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当请求周期中同时出现新增行、删除行，以及 AI 与人工混合重写
- `WHAT`: 让 period-added 记账在删除、重置与混合重写下保持正确
- `WHY`: 防止窗口内已被删除或已被覆盖的 AI 行扭曲 period 结果
- `Story Sentence`: As a repository analyst, I want period-added accounting to handle deletions, resets, and mixed rewrites inside one window, so that superseded or deleted in-window AI lines do not distort the period result.
- `Support Coordinates`: `scope=primary baseline`, `algorithm=B`, `vcs=git local replay`, `tier=Fast`
- `Support Snapshot`: 面向 Algorithm B 重写与删除处理的第一类故事。
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-23`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: 某条 AI 行在窗口内被新增，随后又在窗口内被删除或被后续提交替换
- `WHEN`: `Algorithm B` 计算 period-added 结果
- `THEN`: 这条已删除的 AI 行不会出现在最终 period-added 总量中

**`AC-ALG-B-02`**

- `GIVEN`: 某条窗口前的人类代码行在窗口内被重写
- `WHEN`: `Algorithm B` 计算 period-added 结果
- `THEN`: 这条被重写的行按窗口内新增处理，并归属给重写者

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24: 周期贡献的 Git 重命名与移动处理

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当某个文件在窗口内发生重命名，而分析者仍然需要真实的 period-added 记账
- `WHAT`: 在 period-added 指标中保留 rename 与 move 语义
- `WHY`: 防止仅路径变化把旧行误当作窗口内新增行
- `Story Sentence`: As a repository analyst, I want period-added accounting to preserve rename and move semantics, so that path-only history changes do not make older lines appear as new in-window additions.
- `Support Coordinates`: `scope=primary baseline`, `algorithm=B`, `vcs=git local replay`, `tier=Fast`
- `Support Snapshot`: 面向 period contribution 的第一类 Algorithm B rename 故事。
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: 某个文件在窗口内被重命名，并且新增了一条 AI 行
- `WHEN`: `Algorithm B` 计算 period-added 结果
- `THEN`: 只有这条新增行计入 period-added 总量，而在 rename 后仍然存活的窗口前代码行保持排除

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25: 单个窗口内具备 merge-aware 能力的 Git period contribution

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当请求周期包含分支开发与 non-fast-forward merge 活动
- `WHAT`: 让 period-added 记账在窗口内的 merge-aware Git 历史下保持正确
- `WHY`: 确保 main 分支与被合并 feature 分支上的贡献都被正确计数
- `Story Sentence`: As a repository analyst, I want period-added accounting to survive branch-and-merge history inside one window, so that contributions from both main and merged feature branches are counted correctly.
- `Support Coordinates`: `scope=primary baseline`, `algorithm=B`, `vcs=git local replay`, `tier=Fast`
- `Support Snapshot`: 面向 period contribution 的第一类 Algorithm B merge-aware 故事。
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: AI 行在 main 分支与某个 feature 分支上被新增，并在窗口内通过 non-fast-forward merge 被合并
- `WHEN`: `Algorithm B` 计算 period-added 结果
- `THEN`: 两部分贡献都能正确保留并计入最终 period-added 总量

### USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26: Algorithm B period contribution 的 SVN 支持子集

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当分析者希望在不夸大完整 SVN 一致性的前提下，获得一个可辩护的 SVN period-added 回放子集
- `WHAT`: 让受支持的 SVN 夹具子集产出正确的 `Algorithm B` period-added 结果
- `WHY`: 以场景优先的方式扩展 SVN 支持，同时保持声明可辩护
- `Story Sentence`: As a repository analyst, I want the defended SVN subset of `Algorithm B` period-added replay to produce correct results from offline fixtures, so that SVN support can expand scenario-first without overclaiming general parity.
- `Support Coordinates`: `scope=primary baseline`, `algorithm=B`, `vcs=svn offline fixtures`, `tier=Fast`
- `Support Snapshot`: 通过离线回放工件表达的第一类 Algorithm B SVN 子集故事。
- `Scenario Anchors`: `TestsNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: 提供了 SVN 风格的离线 commit-diff 夹具以及对应协议文件
- `WHEN`: `Algorithm B` 回放该 period-added 场景
- `THEN`: 它正确统计 SVN patch 中 AI 与人工代码行的数量

## 跨算法、硬化与操作员故事

这些故事从纯粹的指标语义扩展到了算法一致性、运行时安全性与操作员可见叙事。

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27: Algorithm A 与 Algorithm B 在每个 Scope 上必须产生相同 SUMMARY

- `WHO`: 仓库分析者
- `WHEN / Scenario`: 当分析者在同一仓库内容上比较基于 blame 的实现与基于回放的实现
- `WHAT`: 让 `Algorithm A` 与 `Algorithm B` 在每个 scope 上保持相同的 `SUMMARY`
- `WHY`: 确保算法选择不会改变测量结果
- `Story Sentence`: As a repository analyst, I want `Algorithm A` and `Algorithm B` to produce the same `SUMMARY` for every scope on the same repository content, so that algorithm choice does not change the measurement result.
- `Support Coordinates`: `scope=A/B/C/D`, `algorithms=A and B`, `vcs=shared replay-supported shapes`, `tier=Fast`
- `Support Snapshot`: 面向跨算法、跨 scope 一致性的第一类故事。
- `Scenario Anchors`: `TestsNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: 某个仓库同时包含源码文件与文档文件
- `WHEN`: `Algorithm A` 与 `Algorithm B` 都以 `--scope A` 运行
- `THEN`: 它们产出相同的 `SUMMARY` 值

**`AC-02`**

- `GIVEN`: 对同一仓库在其余 scope 下进行分析
- `WHEN`: `Algorithm A` 与 `Algorithm B` 都以 `--scope B`、`--scope C` 与 `--scope D` 运行
- `THEN`: 它们产出相同的 `SUMMARY` 值，并在需要时使用正确的文档或代码字段家族

**`AC-03`**

- `GIVEN`: 两种算法在所有受支持 scope 上都产出协议形态结果
- `WHEN`: 比较协议元数据
- `THEN`: `protocolName` 与 `protocolVersion` 在两种算法之间保持一致

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28: 生产硬化：Scope 校验与文件大小保护

- `WHO`: CLI 操作员
- `WHEN / Scenario`: 当操作员传入非法 scope 输入，或运行时遇到可能使处理不安全的超大 VCS 输出
- `WHAT`: 使用显式校验与大小保护实现快速失败
- `WHY`: 避免静默错误结果、失控内存占用或模糊的失败行为
- `Story Sentence`: As a CLI operator, I want invalid `--scope` values to be rejected at input validation and oversized VCS outputs to be caught before processing, so that the tool fails fast with clear diagnostics instead of producing silent wrong results or running out of memory.
- `Support Coordinates`: `scope=input and runtime guard`, `algorithms=A and B`, `vcs=git-focused runtime checks`, `tier=Fast`
- `Support Snapshot`: 第一类硬化故事。
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28`

Acceptance Criteria

**`AC-HARD-01`**

- `GIVEN`: CLI 收到非法 `--scope` 值，例如 `Z`、小写 `a` 或空字符串
- `WHEN`: 输入校验执行
- `THEN`: 工具以 `EXIT_INPUT_ERROR` 退出，并输出包含 `--scope must be one of: A, B, C, D` 的诊断信息

**`AC-HARD-02`**

- `GIVEN`: 某个 Git 仓库包含一个 `git show` 输出超过 `MAX_FILE_SIZE_BYTES` 的文件
- `WHEN`: `Algorithm B` 通过 `read_git_file_lines_at_revision` 读取该文件
- `THEN`: 它抛出带有清晰诊断信息的 `RepositoryStateError`

**`AC-HARD-03`**

- `GIVEN`: Git blame 输出超过 `MAX_FILE_SIZE_BYTES`
- `WHEN`: `Algorithm A` 通过 `parse_blame` 解析 blame
- `THEN`: 它抛出带有清晰诊断信息的 `RepositoryStateError`

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29: Info 级日志必须展示初始加载、逐行状态迁移与最终汇总

- `WHO`: 使用 `--logLevel info` 运行的 CLI 操作员
- `WHEN / Scenario`: 当操作员希望通过 stderr 理解归因故事，但又不想开启完整的 debug 日志量级
- `WHAT`: 提供一个三阶段的 info 级叙事，覆盖起始状态、逐行迁移提示与最终汇总
- `WHY`: 帮助操作员理解哪些行发生了归属变迁，以及最终聚合结果意味着什么，而不必切换到 `--logLevel debug`
- `Story Sentence`: As a CLI operator running with `--logLevel info`, I want to see a three-phase narrative on stderr showing initial load state, per-line state transitions, and final summary, so that I can understand the full attribution story without switching to `--logLevel debug`.
- `Support Coordinates`: `scope=stderr behavior`, `algorithms=primarily A current operator path`, `vcs=shared`, `tier=Fast target`
- `Support Snapshot`: USNG 中已记录的故事。当前可执行测试覆盖仍然是未补齐缺口。
- `Scenario Anchors`: `OperatorScenarioNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29-AI-TO-HUMAN-SHAPE`、`OperatorScenarioNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29-HUMAN-TO-AI-SHAPE`、`TestsNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29`

Acceptance Criteria

**`AC-OPS-01`**

- `GIVEN`: CLI 以 `--logLevel info` 运行
- `WHEN`: 分析开始
- `THEN`: stderr 输出一条 `[INFO]` 行，其中包含 `repo=`、`branch=`、`window=` 与 `endRevision=`

**`AC-OPS-02`**

- `GIVEN`: CLI 以 `--logLevel info` 运行，并且某条存活行相对于父修订发生了归属变化
- `WHEN`: 处理该行
- `THEN`: stderr 输出一条包含 `best_effort_transition=` 的 `[INFO] TransitionHint` 行

**`AC-OPS-03`**

- `GIVEN`: CLI 以 `--logLevel info` 运行
- `WHEN`: 分析结束
- `THEN`: stderr 输出一条 `[INFO]` 汇总行，其中包含 `totalCodeLines=`、`fullGeneratedCodeLines=`、`partialGeneratedCodeLines=` 与 `elapsed=`

**`AC-OPS-04`**

- `GIVEN`: CLI 以 `--logLevel quiet` 运行
- `WHEN`: 分析器原本会输出迁移或逐行细节
- `THEN`: `TransitionHint` 行与 `LiveLine` 行都被抑制

**`AC-OPS-05`**

- `GIVEN`: CLI 以 `--logLevel debug` 运行
- `WHEN`: 分析过程经历加载、扫描、窗口外跳过与缓存复用
- `THEN`: 元数据加载、文件扫描、窗口外跳过与缓存协议复用等诊断继续可见，并且保留所有 info 级日志

**`AC-OPS-06`**

- `GIVEN`: 以 `--logLevel info` 执行批准的 `OperatorScenarioNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29-AI-TO-HUMAN-SHAPE`
- `WHEN`: 报告归属迁移
- `THEN`: stderr 包含 `best_effort_transition=100%-ai->human/unattributed`

**`AC-OPS-07`**

- `GIVEN`: 以 `--logLevel info` 执行批准的 `OperatorScenarioNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29-HUMAN-TO-AI-SHAPE`
- `WHEN`: 报告归属迁移
- `THEN`: stderr 包含 `best_effort_transition=human/unattributed->100%-ai`

## 追踪附录

只有在审计、对照或搜索仍然需要更早的家族式 `USNG-*` 引用或旧版 `US-*` 引用时，才使用本附录。上方主故事层现在使用 4D `USNG-*` 标识符。

- 存活快照谱系：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01` -> 旧 `USNG-LS-01` -> `US-1`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02` -> 旧 `USNG-LS-02` -> `US-2`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03` -> 旧 `USNG-LS-03` -> `US-3`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04` -> 旧 `USNG-LS-04` -> `US-4`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05` -> 旧 `USNG-LS-05` -> `US-5`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06` -> 旧 `USNG-LS-06` -> `US-7`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07` -> 旧 `USNG-LS-07` -> `US-8`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08` -> 旧 `USNG-LS-08` -> `US-9`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09` -> 旧 `USNG-LS-09` -> `US-10`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10` -> 旧 `USNG-LS-10` -> `US-11`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11` -> 旧 `USNG-LS-11` -> `US-12`
- 生产 gate 谱系：`USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12` -> 旧 `USNG-PG-01` -> `US-13`；`USNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13` -> 旧 `USNG-PG-02` -> `US-14`
- Scope 契约谱系：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14` -> 旧 `USNG-SC-01` -> `US-20`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-C-15` -> 旧 `USNG-SC-02` -> `US-21`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-D-16` -> 旧 `USNG-SC-03` -> `US-22`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-17` -> 旧 `USNG-SC-04` -> `US-23`
- Algorithm B Scope 谱系：`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-18` -> 旧 `USNG-AB-01` -> `US-24`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-19` -> 旧 `USNG-AB-02` -> `US-25`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-20` -> 旧 `USNG-AB-03` -> `US-26`
- period-added 谱系：`USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` -> 旧 `USNG-PA-01` -> `US-6`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-22` -> 旧 `USNG-PA-02` -> `US-15`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-23` -> 旧 `USNG-PA-03` -> `US-16`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24` -> 旧 `USNG-PA-04` -> `US-17`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25` -> 旧 `USNG-PA-05` -> `US-18`；`USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26` -> 旧 `USNG-PA-06` -> `US-19`
- 跨算法、硬化与操作员谱系：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27` -> 旧 `USNG-CA-01` -> `US-27`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28` -> 旧 `USNG-CA-02` -> `US-28`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29` -> 旧 `USNG-CA-03` -> `US-29`
