# AggregateGenCodeDesc USNG（UserStoryNG）

## 目的

本文档定义 AggregateGenCodeDesc 的权威下一代用户故事与验收标准，并与 `README_UserStoryNG.md` 保持语义同步。

它与当前基础文档配合使用：

- `README_ZH.md` 仍然是产品与契约的中文基础文档。
- `README_UserGuide_ZH.md` 仍然是面向操作与运行方式的中文基础文档。

在本仓库中，`UserStoryNG` 可简称为 `USNG`。

## USNG 故事规则

1. 让每个故事都以完整 `WHO`、`WHEN`、`WHAT`、`WHY` 字段和经典 `As a … I want … so that …` 故事句式显式表达。
2. 保留经典 `GIVEN … WHEN … THEN …` 作为验收标准形式。
3. 显式写出当前支持边界，而不是隐藏局部支持。
4. 保持场景锚点可见，使用逻辑 `TestdataNG-*`、`TestsNG-*` 与 `OperatorScenarioNG-*` 锚点，而不是绑定到具体文件路径。

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

USNG 使用 4D 故事索引作为主命名规则。

主阅读顺序是：

1. 仓库拓扑
2. `genCodeDesc` 拓扑
3. 仓库历史复杂度
4. Scope

`Algorithm A/B` 通过 `Support` 与 `Status` 字段以及验收条款表达，而不编码进故事 ID 本身。

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
- 逻辑场景锚点（`TestdataNG-*`、`TestsNG-*`、`OperatorScenarioNG-*`）是独立层；它们复用所属故事的 4D 主坐标，并只在需要时附加 `-GIT`、`-SVN`、`-SVN-PARITY` 或 `-AI-TO-HUMAN-SHAPE` 这类可选变体后缀

## UserGuide 运行时故事地图

这一节是主导航地图。

### Git 本地仓库 + genCodeDesc 本地

- `HISTORY-SIMPLE / SCOPE A`：本地基线测量故事卡与单分支 period-added 基线
- `HISTORY-SIMPLE / SCOPE B/C/D`：scope 扩展、Algorithm B scope 支持故事卡与 period-added SCOPE-B/C/D 故事卡
- `HISTORY-COMPLICATED / SCOPE A`：覆盖、删除、重命名、混合窗口与 merge-aware 故事卡
- `HISTORY-COMPLEX / SCOPE A`：大型仓库、深历史、多分支与生产规模 Git 故事卡
- `SCOPE-RUNTIME`：Git 本地运行时硬化故事卡

### Git 本地仓库 + genCodeDesc Shared

- 基线存活快照故事、基线 period-added 契约与 Git 生产规模 gate 这几类共享元数据拓扑契约

### Git 远程身份仓库 + genCodeDesc 本地

- `USNG-30` 定义契约边界：远程 Git 身份是寻址关注点，不得改变指标语义
- 故事 30 是该拓扑的显式规范故事卡

### SVN 本地仓库 + genCodeDesc 本地

- `HISTORY-SIMPLE / SCOPE A`：共享基线与 parity 故事卡，以及被防守的 Algorithm B SVN 子集
- `HISTORY-COMPLEX / SCOPE A`：生产规模 SVN gate
- `SCOPE B/C/D`：只使用那些明确声明 shared 或 SVN-valid 支持的故事卡

### SVN 远程仓库 + genCodeDesc 本地

- `USNG-31` 定义契约边界：远程 SVN URL 是访问路径关注点，不得改变指标语义
- 故事 31 是该拓扑的显式规范故事卡

### 任意仓库拓扑 + genCodeDesc 远程

- `USNG-32` 定义契约边界：provider 侧元数据不得改变指标语义
- 故事 32 是该元数据拓扑的显式规范故事卡

## 如何阅读本文档

每张故事卡都使用这种结构：

- **Story ID** — 4D 标识符：`USNG-REPO-<A>-GENCODEDESC-<B>-HISTORY-<C>-SCOPE-<D>-<NN>: 标题`
- `WHO` — 用户或操作员角色
- `WHEN` — 触发时机或业务时刻
- `WHAT` — 该角色希望分析器完成什么
- `WHY` — 该结果为什么重要
- `Story` — 经典 `As a … I want … so that …` 句式
- `Support` — 内联竖线分隔：`scope=…` | `alg=…` | `vcs=…` | `tier=…`
- `Status` — 当前支持状态，明确说明缺口
- `Anchors` — 逻辑 `TestdataNG-*`、`TestsNG-*` 或 `OperatorScenarioNG-*` 验证锚点

验收标准使用故事内局部 ID（`AC-01`、`AC-ALG-A-01`、`AC-ALG-B-01`），采用简洁 `GIVEN / WHEN / THEN` 块形式。

导航：

- 使用 `UserGuide 运行时故事地图` 按运行时拓扑定位正确的桶。
- 确认故事 ID 的 4D 前缀，明确仓库拓扑、元数据拓扑、历史复杂度与 scope。
- 通过对应 NG 资产 README 将 `Anchors` 解析到具体路径。
- 追踪查找仅保留在末尾附录中。

## 导航

### 4D 视图

- 仓库拓扑：`REPO-GIT-LOCAL`、`REPO-GIT-REMOTE`、`REPO-SVN-LOCAL`、`REPO-SVN-REMOTE`、`REPO-SHARED`
- 元数据拓扑：`GENCODEDESC-LOCAL`、`GENCODEDESC-REMOTE`、`GENCODEDESC-SHARED`
- 历史复杂度：`HISTORY-SIMPLE`、`HISTORY-COMPLICATED`、`HISTORY-COMPLEX`
- Scope：`SCOPE-A`、`SCOPE-B`、`SCOPE-C`、`SCOPE-D`、`SCOPE-ALL`、`SCOPE-RUNTIME`
- Algorithm：保留在 `Support` 与 `Status` 字段中，不编码进故事 ID

### 覆盖范围摘要（42 个故事）

| Dim-C × Dim-D | SCOPE-A | SCOPE-B | SCOPE-C | SCOPE-D |
|---|---|---|---|---|
| **SIMPLE** | 01 (SHARED) | 14 (SHARED), 18 (GIT-LOCAL), 33 (GIT-LOCAL) | 15 (SHARED), 19 (GIT-LOCAL), 34 | 16 (SHARED), 20 (GIT-LOCAL), 35 |
| **COMPLICATED** | 02–07 (SHARED), 23–25 (GIT-LOCAL period-added), 42 (SVN-LOCAL) | 36 (SHARED) | 37 (SHARED) | 38 (SHARED) |
| **COMPLEX** | 09–11 (SHARED), 12 (GIT-LOCAL gate), 13 (SVN-LOCAL gate) | 39 (SHARED) | 40 (SHARED) | 41 (SHARED) |

远程拓扑（GIT-REMOTE：故事 30，SVN-REMOTE：故事 31，GENCODEDESC-REMOTE：故事 32）通过委托覆盖所有 SHARED 行为契约，并只新增访问路径边界契约。

额外故事覆盖 SCOPE-ALL（17、27）、SCOPE-RUNTIME（28、29）以及 period-added SCOPE-A 契约（21、22、26），未在上方矩阵中单独列出。

## 详细故事卡

### 通用故事不变式

除非某张故事卡明确覆盖某条不变式，否则以下常设要求适用于下方所有故事卡。

**UI-PROTOCOL** — 成功结果始终具有协议形态：`REPOSITORY` 中包含仓库身份，`SUMMARY` 中包含聚合值。

**UI-GOLDEN** — 任何声称支持某故事的实现路径，必须为该故事的已批准场景产出与已批准 golden 输出一致的结果。

**UI-ALG-B-BOUNDARY** — 任何附属于 `HISTORY-COMPLICATED` 或 `HISTORY-COMPLEX` 故事的 `Algorithm B` 证据，仅覆盖该故事的已批准场景，而不是对所有 complicated 或 complex 历史形态的全面支持。

需要例外的故事卡通过明确命名所覆盖的不变式来声明覆盖。

---

## 存活快照契约故事

这些故事描述主存活快照指标：在请求时间窗口内其当前版本发生过变化、并且在 `endTime` 仍然存活的源码行中的加权 AI 占比。

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01: 计算请求时间窗口内存活变更源码的加权 AI 占比

- `WHO`: 仓库分析者
- `WHEN`: 针对一个仓库分支、一个请求窗口 `startTime~endTime` 发起查询，并需要 `endTime` 时刻的最终存活快照答案
- `WHAT`: 计算当前版本在请求窗口内发生变化的存活源码行的加权 AI 占比
- `WHY`: 了解当前仍然存活的变更源码中，有多少可以归因于 AI
- `Story`: As a repository analyst, I want to calculate the weighted AI ratio for live source-code lines whose current version falls in a requested period `startTime~endTime`, so that I can know how much of the current live changed source code is attributable to AI.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=git and svn` | `tier=Fast`
- `Status`: `Algorithm A` 在本故事已批准的基线场景上覆盖 Git 与 SVN。`Algorithm B` 在同一组已批准的 story-01 场景上覆盖狭义 Git 与 SVN 的存活快照回放。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT`, `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN`

**`AC-01`**

- `GIVEN`: 针对存活快照指标的查询：`repo + branch + startTime + endTime`
- `WHEN`: 分析器在 `endTime` 时刻计算最终结果
- `THEN`: 它只返回一个仓库级最终结果，描述在 `startTime~endTime` 内其当前版本被新增或修改、并在 `endTime` 时刻仍然存活的源码行中的 AI 占比

**`AC-02`**

- `GIVEN`: 外部 `genCodeDesc` 记录存储于仓库以外，按 `repoURL + repoBranch + revisionId` 索引
- `WHEN`: 分析器从最终存活快照中发现在范围内的来源修订
- `THEN`: 它在聚合过程中获取并使用相匹配的元数据记录

**`AC-03`**

- `GIVEN`: 一个或多个在范围内的来源修订在元数据存储中没有匹配的 `genCodeDesc` 记录
- `WHEN`: 分析器聚合最终结果
- `THEN`: 这些行被计为人工无归因（而非 AI 生成），而不是被静默跳过或导致运行报错，且该缺失可通过 `--logLevel debug` 观察到

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

**`AC-ALG-A-02`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN` 场景
- `WHEN`: Algorithm A SVN 路径执行
- `THEN`: 保持相同的可观察 story-01 契约

**`AC-ALG-B-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT` 回放场景
- `WHEN`: 狭义 Algorithm B Git 存活快照路径执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-02`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN` 回放场景
- `WHEN`: 狭义 Algorithm B SVN 存活快照路径执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02: 人工重写会移除之前的 AI 归因

- `WHO`: 仓库分析者
- `WHEN`: 某次人工修订在 `endTime` 之前覆盖了之前归因于 AI 的代码
- `WHAT`: 将有效归因重置为更新的人工修订
- `WHY`: 防止旧的 AI 归属仍然附着在已被覆盖的代码上
- `Story`: As a repository analyst, I want a human rewrite of a previously AI-generated line to reset attribution to the newer human revision, so that old AI ownership does not remain attached to overwritten code.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=shared (Algorithm B evidence via narrow Git slice)` | `tier=Fast`
- `Status`: VCS 无关的归因契约。Algorithm A 覆盖 Git 与 SVN。Algorithm B 证据通过狭义 Git 存活快照回放路径提供。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02`

**`AC-01`**

- `GIVEN`: 在 `endTime` 之前，某次人工修订覆盖了之前归因于 AI 的代码
- `WHEN`: 在 `endTime` 时刻为存活变更源码集合产出最终结果
- `THEN`: 它反映更新后的状态，不保留已过时的 AI 归属

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 已批准的回放场景
- `WHEN`: 狭义 Algorithm B Git 存活快照路径执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03: AI 重写会取代之前的人类归属

- `WHO`: 仓库分析者
- `WHEN`: 某次更新的 AI 修订在 `endTime` 之前覆盖了之前由人工创作的代码行
- `WHAT`: 令更新的 AI 重写成为有效归因来源
- `WHY`: 确保 `endTime` 时刻的存活变更源码反映最新的 AI 贡献
- `Story`: As a repository analyst, I want a later AI rewrite of a human line to become the effective attribution source, so that the live changed source code at `endTime` reflects the latest AI contribution.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=shared (Algorithm B evidence via narrow Git slice)` | `tier=Fast`
- `Status`: VCS 无关的归因契约。Algorithm A 覆盖 Git 与 SVN。Algorithm B 证据通过狭义 Git 存活快照回放路径提供。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03`

**`AC-01`**

- `GIVEN`: 在 `endTime` 之前，某次更新的修订引入了新的 AI 归因代码
- `WHEN`: 在 `endTime` 时刻为存活变更源码状态产出最终结果
- `THEN`: 它反映更新后的 AI 贡献

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 已批准的回放场景
- `WHEN`: 狭义 Algorithm B Git 存活快照路径执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04: 已删除的 AI 代码行不得计入

- `WHO`: 仓库分析者
- `WHEN`: AI 生成的代码行早先在窗口内存在，但在 `endTime` 时刻已从分支状态中消失
- `WHAT`: 将已删除的 AI 代码行从分子与分母中同时排除
- `WHY`: 让结果只反映当前存活的变更快照
- `Story`: As a repository analyst, I want deleted AI-generated lines to disappear from both numerator and denominator, so that the result reflects only the current live changed source-code snapshot.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=shared (Algorithm B evidence via narrow Git slice)` | `tier=Fast`
- `Status`: VCS 无关的归因契约。Algorithm A 覆盖 Git 与 SVN。Algorithm B 证据通过狭义 Git 存活快照回放路径提供。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04`

**`AC-01`**

- `GIVEN`: 在 `endTime` 时刻，之前归因于 AI 的代码已不再存在于分支状态中
- `WHEN`: 为存活变更源码结果产出最终记录
- `THEN`: 该已删除代码被排除在结果之外

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 已批准的回放场景
- `WHEN`: 狭义 Algorithm B Git 存活快照路径执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05: 重命名必须保留归因谱系

- `WHO`: 仓库分析者
- `WHEN`: 文件在 `endTime` 之前被重命名或移动，但其有效内容贡献未发生变化
- `WHAT`: 在仅路径变化的历史变更中保留逐行归因
- `WHY`: 防止仅重命名的操作扭曲最终存活变更源码的比率
- `Story`: As a repository analyst, I want file rename or move operations to preserve line attribution when content does not change, so that the final live changed source-code ratio is not distorted by path-only history changes.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=shared (Algorithm B evidence via narrow Git slice)` | `tier=Fast`
- `Status`: VCS 无关的归因契约。Git 使用 git-follow 语义；SVN 使用 path-copy 跟踪。Algorithm B 证据通过狭义 Git 存活快照回放路径提供。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05`

**`AC-01`**

- `GIVEN`: 文件在 `endTime` 之前被重命名或移动，但其有效贡献未发生变化
- `WHEN`: 在 `endTime` 时刻为存活变更源码集合产出最终记录
- `THEN`: 它在仅路径变化的历史变更下保持稳定

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 已批准的回放场景
- `WHEN`: 狭义 Algorithm B Git 存活快照路径执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-06: 在单个请求窗口内解析混合多提交历史

- `WHO`: 仓库分析者
- `WHEN`: 一个请求窗口内包含许多提交，混合了仅人工、仅 AI、重写与删除路径
- `WHAT`: 通过每条存活行在窗口内的最新有效归因来解析最终结果
- `WHY`: 当窗口内历史混杂且复杂时，仍然保持一个正确的最终结果
- `Story`: As a repository analyst, I want one requested window to correctly resolve mixed line histories across many commits, so that the final result remains correct when human-only lines, AI-only lines, human-then-AI rewrites, AI-then-human rewrites, and deleted AI lines all appear in the same period.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=shared (Algorithm B evidence via narrow Git slice)` | `tier=Fast`
- `Status`: VCS 无关的归因契约。Algorithm A 覆盖 Git 与 SVN。Algorithm B 证据通过狭义 Git 存活快照回放路径提供。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-06`

**`AC-01`**

- `GIVEN`: 请求窗口内多个提交对不同存活行包含混合的归属迁移
- `WHEN`: 分析器在 `endTime` 时刻解析存活变更源码集合
- `THEN`: 它只产出一个最终记录，使用每条存活行的最新有效归因

**`AC-02`**

- `GIVEN`: 某条存活行在窗口内经历了一长串中间修订
- `WHEN`: 分析器在 `endTime` 时刻解析该存活行
- `THEN`: 它使用最新有效的存活归因，而不会把已被取代的中间归属泄漏到最终结果中

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-06` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 已批准的回放场景
- `WHEN`: 狭义 Algorithm B Git 存活快照路径执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-07: 合并提交必须保留有效归因

- `WHO`: 仓库分析者
- `WHEN`: 被合并的分支在 `endTime` 之前将人工贡献与 AI 贡献带入目标分支
- `WHAT`: 通过合并操作保留每条存活行的有效归因
- `WHY`: 防止合并提交重置归属或压平来源
- `Story`: As a repository analyst, I want merged branch content to preserve the effective attribution of surviving lines, so that a merge operation does not incorrectly reset line ownership to the merge commit itself.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=shared (Algorithm B evidence via narrow Git slice)` | `tier=Fast`
- `Status`: VCS 无关的归因契约。Algorithm A 覆盖 Git 与 SVN 合并语义。Algorithm B 证据通过狭义 Git 存活快照回放路径提供。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-07`

**`AC-01`**

- `GIVEN`: 某次合并提交在 `endTime` 之前将之前的人工和 AI 归因变更汇聚在一起
- `WHEN`: 在 `endTime` 时刻为存活变更源码集合产出最终记录
- `THEN`: 它使用存活的被合并行的有效归因，而不是把合并提交本身视为来源

**`AC-02`**

- `GIVEN`: 多个分支在 `endTime` 之前被合并，且存活行来自不同的被合并分支
- `WHEN`: 分析器解析最终存活状态
- `THEN`: 它逐条保留每条存活行，而不会把归属压平为合并提交或最终分支身份

**`AC-03`**

- `GIVEN`: 某次合并在 `endTime` 之前产生了冲突标记或手工解决区域，混合了 AI 来源与人工来源的内容
- `WHEN`: 在 `endTime` 时刻为存活变更源码集合产出最终记录
- `THEN`: 每条冲突解决后的存活行按照冲突解决提交的提交者归因，而不是冲突区域合并前各方来源修订的归因

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-07` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 已批准的回放场景
- `WHEN`: 狭义 Algorithm B Git 存活快照路径执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08: Git 与 SVN 必须遵循同一结果契约

- `WHO`: 仓库分析者
- `WHEN`: 针对等价的受支持 Git 与 SVN 历史请求相同的主指标
- `WHAT`: 在各 VCS 目标上保持查询结果契约的一致性
- `WHY`: 确保更换 VCS 类型不会改变指标语义或输出结构
- `Story`: As a repository analyst, I want Git and SVN targets to follow the same query-result contract for the current primary metric, so that changing VCS type does not change metric semantics or output structure.
- `Support`: `scope=A baseline` | `alg=A and narrow B parity slice` | `vcs=git and svn` | `tier=Fast`
- `Status`: Git 与 SVN 的 parity 通过 Algorithm A 实现。狭义 Algorithm B 契约 parity 存在于已批准的 story-01 Git/SVN 场景以及已批准的 story-08 SVN parity 场景上。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08-SVN-PARITY`

**`AC-01`**

- `GIVEN`: 针对相同请求窗口的等价受支持仓库历史，分别来自 Git 或 SVN
- `WHEN`: 使用当前主指标进行分析
- `THEN`: Git 与 SVN 产出只包含一条最终记录，具有相同的指标语义和协议形态结构，仅在 VCS 特定的仓库身份细节上有所不同

**`AC-GIT-01`**

- `GIVEN`: 当前主指标的 Git 路径
- `WHEN`: 通过基线存活快照场景进行验证
- `THEN`: 它定义了可观察 parity 契约的一侧

**`AC-SVN-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08-SVN-PARITY` 场景
- `WHEN`: 当前 SVN 路径执行
- `THEN`: 结果与批准的 NG golden 输出一致，同时保持共享的 story-08 契约

**`AC-SVN-02`**

- `GIVEN`: SVN 路径历史或 blame 差异需要一种 VCS 特定的 parity 形态
- `WHEN`: 设计 parity 场景
- `THEN`: 可以使用可辩护的 SVN 特定仓库形态，只要可观察的结果契约保持不变

**`AC-ALG-B-01`**

- `GIVEN`: 已批准的狭义 Algorithm B Git 与 SVN 存活快照验证轨道（基线场景）
- `WHEN`: 将其用作 parity 场景
- `THEN`: 它们在 Git 与 SVN 之间产出相同的协议形态可观察契约，仅在 VCS 特定仓库身份字段上有所不同

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-09: 大型仓库快照必须保持结果语义

- `WHO`: 仓库分析者
- `WHEN`: 仓库包含许多文件和许多存活行，但分析者仍然期望相同的指标语义
- `WHAT`: 在大型真实仓库上保持存活快照契约
- `WHY`: 在更大的仓库规模下保持聚合结果的可信度
- `Story`: As a repository analyst, I want the analyzer to keep the same result semantics when the repository contains many source files and many live lines, so that the final aggregate result remains correct for realistic large codebases.
- `Support`: `scope=A baseline` | `alg=A and narrow B Git slice` | `vcs=shared` | `tier=Fast`
- `Status`: VCS 无关的规模契约。Algorithm A 覆盖 Git 与 SVN。Algorithm B 证据通过狭义 Git 存活快照回放路径提供。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-09`

**`AC-01`**

- `GIVEN`: 在 `endTime` 时刻的最终存活快照跨越许多源码文件和许多存活代码行
- `WHEN`: 分析器计算最终聚合结果
- `THEN`: 它仍然只产出一个仓库级最终结果，具有与小型仓库相同的指标语义和协议形态

**`AC-02`**

- `GIVEN`: 一个大型仓库快照包含许多文件中的许多在范围内的代码行
- `WHEN`: 分析器聚合结果
- `THEN`: 仓库大小或文件数量不会改变逐行归因规则、仓库身份规则或最终 `SUMMARY` 字段的含义

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-09` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 通过夹具回放或聚焦的真实本地 Git 回放路径表达的已批准场景
- `WHEN`: 狭义 Algorithm B Git 存活快照路径执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-10: 深历史必须保持最新有效归因

- `WHO`: 仓库分析者
- `WHEN`: 在 `endTime` 时刻的存活行经历了含有许多中间重写的漫长修订链
- `WHAT`: 通过最新有效归因而不是已被取代的中间归属来解析每条存活行
- `WHY`: 防止深历史扭曲最终存活结果
- `Story`: As a repository analyst, I want long revision chains to preserve the latest effective attribution of each surviving line, so that many intermediate rewrites do not distort the final live result.
- `Support`: `scope=A baseline` | `alg=A and narrow B Git slice` | `vcs=shared` | `tier=Fast`
- `Status`: VCS 无关的深度契约。Algorithm A 覆盖 Git 与 SVN。Algorithm B 证据通过狭义 Git 存活快照回放路径提供。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-10`

**`AC-01`**

- `GIVEN`: 在 `endTime` 时刻，在范围内的存活行依赖于包含许多中间重写的漫长修订链
- `WHEN`: 分析器解析每条存活行
- `THEN`: 它使用最新有效的存活归因，而不是链中更早的已被取代的修订

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-10` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-01`**

- `GIVEN`: 通过夹具回放工件或聚焦的真实本地 Git 回放路径表达的、已批准的场景
- `WHEN`: 狭义 Algorithm B Git 存活快照路径执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-02`**

- `GIVEN`: 当前 Algorithm B 针对本故事的证据
- `WHEN`: 文档或路线图讨论其支持边界
- `THEN`: 它必须被表述为针对本故事已批准场景、并带有聚焦真实本地 Git 证明的狭义 Git 存活快照回放支持，而不是完整矩阵就绪的 deep-history 支持

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-11: 单个窗口内的大量分支合并必须保留逐行归因

- `WHO`: 仓库分析者
- `WHEN`: 许多分支在一个请求窗口内被合并进目标分支
- `WHAT`: 在分支密集的合并历史中保留逐行有效归因
- `WHY`: 防止分支汇聚与合并顺序扭曲最终结果
- `Story`: As a repository analyst, I want branch-heavy history inside one requested window to preserve per-line effective attribution, so that integrating many feature branches into the target branch does not distort the final result.
- `Support`: `scope=A baseline` | `alg=A and current narrow B Git slice` | `vcs=shared story with SVN analogue note` | `tier=Fast`
- `Status`: 已有 `Algorithm A` 证据。`Algorithm B` 证据是面向本故事已批准场景的狭义 Git 存活快照回放。SVN 一致性可能需要可辩护的类比场景，而不是字面上的同文件 Git 移植。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-11`

**`AC-01`**

- `GIVEN`: 许多分支在 `endTime` 之前被合并进目标分支
- `WHEN`: 分析器针对 `endTime` 的存活变更源码集合计算最终结果
- `THEN`: 它仍然只产出一个仓库级最终结果

**`AC-02`**

- `GIVEN`: 存活行来自不同被合并分支，并且它们拥有不同的有效历史
- `WHEN`: 分析器解析最终存活状态
- `THEN`: 它逐条保留这些存活行，而不会把归属压平为 merge commit、分支标签或合并顺序

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-11` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

**`AC-ALG-A-02`**

- `GIVEN`: 同一广义契约的 SVN 一致性需要一个可辩护的类比场景
- `WHEN`: 对 SVN 来说，字面上的同文件 Git 形态会造成误导
- `THEN`: 可以使用 SVN 专属类比场景，只要共享的可观察契约保持不变

**`AC-ALG-B-01`**

- `GIVEN`: 已批准的场景回放
- `WHEN`: 狭义 Algorithm B Git 存活快照路径执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-02`**

- `GIVEN`: 当前 Algorithm B 针对本故事的证据
- `WHEN`: 文档或路线图讨论其支持边界
- `THEN`: 它必须被表述为针对本故事已批准场景的狭义 Git 存活快照回放支持，而不是完整矩阵就绪的分支密集 merge 支持

## Heavy 生产 Gate

这些故事不是普通的小型功能故事，而是生产 gate。它们依然是角色驱动的故事，但场景被明确设定为 heavy、生产导向。

### USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12: Git 生产规模本地仓库在分支密集发布收敛下仍必须保持正确

- `WHO`: 仓库分析者
- `WHEN`: 需要在一个模拟发布收敛的大规模分支型本地 Git 仓库上验证生产就绪性
- `WHAT`: 让 `Algorithm A + Scope A` 在生产规模本地 Git 拓扑上保持正确
- `WHY`: 证明大量分支、深历史与混合发布合并不会扭曲最终存活归因结果
- `Story`: As a repository analyst, I want Algorithm A and Scope A to remain correct on a production-scale local Git repository, so that large branch counts, deep history, and hybrid release merges do not distort the final live attribution result.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git` | `tier=Heavy`
- `Status`: 面向生产的 heavy gate，包含真实本地 Git 仓库生成，以及正确性与可扩展性检查。
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12`

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
- `WHEN`: 需要在一个具有分支复制与再集成压力的生产规模本地 SVN 仓库上验证生产就绪性
- `WHAT`: 让 `Algorithm A + Scope A` 在生产规模本地 SVN 拓扑上保持正确
- `WHY`: 证明 SVN 的分支复制、合并与发布再集成在大规模下不会破坏存活归因
- `Story`: As a repository analyst, I want Algorithm A and Scope A to remain correct on a production-scale local SVN repository, so that SVN branch copying, merges, and release reintegration at scale do not break live attribution.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=svn` | `tier=Heavy`
- `Status`: 面向生产的 heavy gate，包含真实本地 SVN 仓库生成，以及正确性与可扩展性检查。
- `Anchors`: `TestsNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13`

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

这些故事扩展被计数的内容边界。角色保持不变，但场景从"只看源码中发生了什么"转变为"哪些内容家族属于范围内"。

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14: Scope B 源代码含注释时必须把注释行计入总量

- `WHO`: 仓库分析者
- `WHEN`: 分析者希望源码文件总量把注释行也作为被测量的源码文本计入
- `WHAT`: 让 `--scope B` 统计源码文件中的所有非空行，包括注释
- `WHY`: 衡量 AI 对源码文件全部文本内容的贡献，而不仅仅是可执行代码
- `Story`: As a repository analyst, I want `--scope B` to count all non-blank lines in source files, including comment lines, in the aggregate result, so that I can measure AI contribution across the full textual content of source files, not just executable code.
- `Support`: `scope=B` | `alg=primarily A at story level` | `vcs=shared` | `tier=Fast`
- `Status`: 面向包含注释的源码文件总量的第一类 scope 故事。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14`

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
- `WHEN`: 分析者希望衡量仅文档贡献，而不是源码贡献
- `WHAT`: 让 `--scope C` 分析文档文件，并通过 `docLines` 进行归因
- `WHY`: 将 AI 对文档工件的贡献与源码贡献分离衡量
- `Story`: As a repository analyst, I want `--scope C` to analyze documentation text files and use the `docLines` protocol field for AI attribution, so that I can measure AI contribution to documentation artifacts separately from source code.
- `Support`: `scope=C` | `alg=primarily A at story level` | `vcs=shared` | `tier=Fast`
- `Status`: 面向纯文档分析的第一类 scope 故事。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-C-15`

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
- `WHEN`: 分析者希望在一个结果中同时覆盖源码文件与文档文件
- `WHAT`: 让 `--scope D` 在一次聚合中统计源码与文档的全部非空行
- `WHY`: 衡量整个仓库全部文本内容上的 AI 总贡献
- `Story`: As a repository analyst, I want `--scope D` to count all non-blank lines from both source files and documentation files in one combined result, so that I can measure total AI contribution across the entire textual content of the repository.
- `Support`: `scope=D` | `alg=primarily A at story level` | `vcs=shared` | `tier=Fast`
- `Status`: 面向源码与文档统一总量的第一类 scope 故事。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-D-16`

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
- `WHEN`: 分析者在同一个仓库上运行四种 scope，并希望每个 scope 都保持独立且正确
- `WHAT`: 验证 A、B、C、D 的完整 scope 矩阵
- `WHY`: 确认 scope 选择真的控制了测量边界
- `Story`: As a repository analyst, I want a cross-scope verification that runs Scope A, B, C, and D on the same repository and confirms each produces the expected distinct result, so that I can trust that scope selection genuinely controls the measurement boundary.
- `Support`: `scope=A/B/C/D` | `alg=primarily A at story level` | `vcs=shared` | `tier=Fast`
- `Status`: 面向跨 scope 契约的第一类故事。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-17`

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
- `WHEN`: 分析者需要在源码代码加源码注释的范围内进行回放式归因
- `WHAT`: 让 `--algorithm B --scope B` 统计全部非空源码行，包括注释
- `WHY`: 使用增量回放算法衡量全部源码文本上的 AI 总贡献
- `Story`: As a repository analyst, I want `--algorithm B --scope B` to count all non-blank source lines including comments during replay, so that I can measure total AI contribution to all source text using the incremental replay algorithm.
- `Support`: `scope=B` | `alg=B` | `vcs=current supported replay shapes` | `tier=Fast`
- `Status`: 面向 Algorithm B 注释纳入型源码回放的第一类故事。
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-18`

**`AC-ALG-B-01`**

- `GIVEN`: 某个源码文件同时包含代码行与注释行
- `WHEN`: `Algorithm B` 以 `--scope B` 运行
- `THEN`: `totalCodeLines` 统计全部非空源码行

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-19: Algorithm B 必须支持 Scope C

- `WHO`: 仓库分析者
- `WHEN`: 分析者需要在文档文件上进行回放式归因，而不是在源码文件上
- `WHAT`: 让 `--algorithm B --scope C` 通过 `docLines` 回放并统计文档文件行
- `WHY`: 使用增量回放算法衡量文档上的 AI 贡献
- `Story`: As a repository analyst, I want `--algorithm B --scope C` to replay and count documentation file lines using the `docLines` protocol field, so that I can measure AI contribution to documentation using the incremental replay algorithm.
- `Support`: `scope=C` | `alg=B` | `vcs=current supported replay shapes` | `tier=Fast`
- `Status`: 面向 Algorithm B 文档回放的第一类故事。
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-19`

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
- `WHEN`: 分析者需要在同一次运行中，对源码文件与文档文件同时进行回放式归因
- `WHAT`: 让 `--algorithm B --scope D` 把两类文件一并回放进统一结果
- `WHY`: 使用增量回放算法衡量仓库全部文本内容上的 AI 总贡献
- `Story`: As a repository analyst, I want `--algorithm B --scope D` to replay both source files and documentation files into a unified result, so that I can measure total AI contribution across all textual repository content using the incremental replay algorithm.
- `Support`: `scope=D` | `alg=B` | `vcs=current supported replay shapes` | `tier=Fast`
- `Status`: 面向 Algorithm B 源码加文档统一回放的第一类故事。
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-20`

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
- `WHEN`: 分析者希望衡量的是窗口本身新增的 AI 贡献，而不是窗口结束时的库存
- `WHAT`: 计算 `startTime~endTime` 期间新增了多少 AI 生成代码
- `WHY`: 区分期间贡献与期末库存
- `Story`: As a repository analyst, I want to calculate how much AI-generated code was added during `startTime~endTime`, so that I can distinguish period contribution from end-of-period inventory.
- `Support`: `scope=shared story anchor` | `alg=A future; B current narrow baseline` | `vcs=shared` | `tier=Fast`
- `Status`: 这是共享故事锚点；当前可执行路径是狭义 `Algorithm B` Git 基线，通过离线回放与受支持的本地 Git 回放执行。
- `Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21`

**`AC-01`**

- `GIVEN`: `repo`、`branch`、`startTime` 与 `endTime` 定义了一个请求周期
- `WHEN`: 执行 period contribution 指标
- `THEN`: 它返回且只返回一个仓库级最终结果，用于描述该周期内 AI 新增代码的聚合结果

**`AC-ALG-A-01`**

- `GIVEN`: 未来某个 `Algorithm A` 路径声称支持该 period contribution 指标
- `WHEN`: 使用共享契约对其进行评估
- `THEN`: 它必须满足共享 `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` 条款，而不会削弱可观察契约

**`AC-ALG-A-02`**

- `GIVEN`: 未来为本故事增加了某个 `Algorithm A` 夹具或真实仓库验收场景
- `WHEN`: 为其记录支持层级
- `THEN`: 它必须显式声明 `Fast` 或 `Heavy`

**`AC-ALG-B-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` 场景
- `WHEN`: 当前狭义离线 Git `Algorithm B` 基线路径执行
- `THEN`: 产出结果与该场景批准的 NG golden 输出一致

**`AC-ALG-B-02`**

- `GIVEN`: 输入保持在当前狭义 Git 回放边界内
- `WHEN`: CLI 以 `--algorithm B` 运行
- `THEN`: 当前路径可以通过已批准的回放输入路径或受支持的本地 Git checkout 路径执行本故事

**`AC-ALG-B-03`**

- `GIVEN`: 更宽的 `Algorithm B` 历史形态，例如多文件回放、路径重命名变化或超出已验收故事的 merge-aware 记账
- `WHEN`: 文档或路线图讨论其支持状态
- `THEN`: 这些形态在由其各自验收轨道证明前，仍然保持不支持

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-22: 无合并无重命名的单分支 period-added 基线

- `WHO`: 仓库分析者
- `WHEN`: 分析者希望在引入拓扑复杂性之前，先建立最干净的单分支 period-added 基线
- `WHAT`: 在简单线性 Git 历史上证明 `Algorithm B` 的核心 period-added 契约
- `WHY`: 在加入重写、重命名或合并之前，先建立稳定基线
- `Story`: As a repository analyst, I want a single-branch period-added baseline without merges or renames, so that the core `Algorithm B` period-contribution contract is proven before topology complexity is introduced.
- `Support`: `scope=A and B note` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: 面向 Algorithm B 单分支基线的第一类故事。
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-22`

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
- `WHEN`: 请求周期中同时出现新增行、删除行，以及 AI 与人工混合重写
- `WHAT`: 让 period-added 记账在删除、重置与混合重写下保持正确
- `WHY`: 防止窗口内已被删除或已被覆盖的 AI 行扭曲 period 结果
- `Story`: As a repository analyst, I want period-added accounting to handle deletions, resets, and mixed rewrites inside one window, so that superseded or deleted in-window AI lines do not distort the period result.
- `Support`: `scope=primary baseline` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: 面向 Algorithm B 重写与删除处理的第一类故事。
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-23`

**`AC-ALG-B-01`**

- `GIVEN`: 某条 AI 行在窗口内被新增，随后又在窗口内被删除或被后续提交替换
- `WHEN`: `Algorithm B` 计算 period-added 结果
- `THEN`: 这条已删除的 AI 行不会出现在最终 period-added 总量中

**`AC-ALG-B-02`**

- `GIVEN`: 某条窗口前的人类代码行在窗口内被重写
- `WHEN`: `Algorithm B` 计算 period-added 结果
- `THEN`: 这条被重写的行按窗口内新增处理，并归属给重写者

**`AC-ALG-B-03`**

- `GIVEN`: 某个文件包含来源修订早于 `startTime` 的代码行，且这些行在 `endTime` 时仍然存活未改动
- `WHEN`: `Algorithm B` 计算 period-added 结果
- `THEN`: 这些窗口前存活行无论其归因如何，都被排除在 period-added 总量之外

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24: 周期贡献的 Git 重命名与移动处理

- `WHO`: 仓库分析者
- `WHEN`: 某个文件在窗口内发生重命名，而分析者仍然需要真实的 period-added 记账
- `WHAT`: 在 period-added 指标中保留 rename 与 move 语义
- `WHY`: 防止仅路径变化把旧行误当作窗口内新增行
- `Story`: As a repository analyst, I want period-added accounting to preserve rename and move semantics, so that path-only history changes do not make older lines appear as new in-window additions.
- `Support`: `scope=primary baseline` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: 面向 period contribution 的第一类 Algorithm B rename 故事。
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24`

**`AC-ALG-B-01`**

- `GIVEN`: 某个文件在窗口内被重命名，并且新增了一条 AI 行
- `WHEN`: `Algorithm B` 计算 period-added 结果
- `THEN`: 只有这条新增行计入 period-added 总量，而在 rename 后仍然存活的窗口前代码行保持排除

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25: 单个窗口内具备 merge-aware 能力的 Git period contribution

- `WHO`: 仓库分析者
- `WHEN`: 请求周期包含分支开发与 non-fast-forward merge 活动
- `WHAT`: 让 period-added 记账在窗口内的 merge-aware Git 历史下保持正确
- `WHY`: 确保 main 分支与被合并 feature 分支上的贡献都被正确计数
- `Story`: As a repository analyst, I want period-added accounting to survive branch-and-merge history inside one window, so that contributions from both main and merged feature branches are counted correctly.
- `Support`: `scope=primary baseline` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: 面向 period contribution 的第一类 Algorithm B merge-aware 故事。
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25`

**`AC-ALG-B-01`**

- `GIVEN`: AI 行在 main 分支与某个 feature 分支上被新增，并在窗口内通过 non-fast-forward merge 被合并
- `WHEN`: `Algorithm B` 计算 period-added 结果
- `THEN`: 两部分贡献都能正确保留并计入最终 period-added 总量

**`AC-ALG-B-02`**

- `GIVEN`: 某条代码行在合并前同时存在于 main 分支与 feature 分支上（例如两侧内容相同）
- `WHEN`: `Algorithm B` 计算 period-added 结果
- `THEN`: 无论有多少条分支历史包含该行，该行在最终 period-added 总量中最多只被统计一次

### USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26: Algorithm B period contribution 的 SVN 支持子集

- `WHO`: 仓库分析者
- `WHEN`: 分析者希望在不夸大完整 SVN 一致性的前提下，获得一个可辩护的 SVN period-added 回放子集
- `WHAT`: 让受支持的 SVN 夹具子集产出正确的 `Algorithm B` period-added 结果
- `WHY`: 以场景优先的方式扩展 SVN 支持，同时保持声明可辩护
- `Story`: As a repository analyst, I want the defended SVN subset of `Algorithm B` period-added replay to produce correct results from offline fixtures, so that SVN support can expand scenario-first without overclaiming general parity.
- `Support`: `scope=primary baseline` | `alg=B` | `vcs=svn offline fixtures` | `tier=Fast`
- `Status`: 通过离线回放工件表达的第一类 Algorithm B SVN 子集故事。
- `Anchors`: `TestsNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26`

**`AC-ALG-B-01`**

- `GIVEN`: 提供了 SVN 风格的离线 commit-diff 夹具以及对应协议文件
- `WHEN`: `Algorithm B` 回放该 period-added 场景
- `THEN`: 它正确统计 SVN patch 中 AI 与人工代码行的数量

## 跨算法、硬化与操作员故事

这些故事从纯粹的指标语义扩展到了算法一致性、运行时安全性与操作员可见叙事。

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27: Algorithm A 与 Algorithm B 在每个 Scope 上必须产生相同 SUMMARY

- `WHO`: 仓库分析者
- `WHEN`: 分析者在同一仓库内容上比较基于 blame 的实现与基于回放的实现
- `WHAT`: 让 `Algorithm A` 与 `Algorithm B` 在每个 scope 上保持相同的 `SUMMARY`
- `WHY`: 确保算法选择不会改变测量结果
- `Story`: As a repository analyst, I want `Algorithm A` and `Algorithm B` to produce the same `SUMMARY` for every scope on the same repository content, so that algorithm choice does not change the measurement result.
- `Support`: `scope=A/B/C/D` | `alg=A and B` | `vcs=shared replay-supported shapes` | `tier=Fast`
- `Status`: 面向跨算法、跨 scope 一致性的第一类故事。
- `Anchors`: `TestsNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27`

**`AC-01`**

- `GIVEN`: 某个仓库同时包含源码文件与文档文件
- `WHEN`: `Algorithm A` 与 `Algorithm B` 都以 `--scope A` 运行
- `THEN`: 它们产出相同的 `SUMMARY` 值

**`AC-02`**

- `GIVEN`: 对同一仓库在其余 scope 下进行分析
- `WHEN`: `Algorithm A` 与 `Algorithm B` 都以 `--scope B`、`--scope C` 与 `--scope D` 运行
- `THEN`: 它们产出相同的 `SUMMARY` 值，并在需要时使用正确的文档或代码字段家族

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28: 生产硬化：Scope 校验与文件大小保护

- `WHO`: CLI 操作员
- `WHEN`: 操作员传入非法 scope 输入，或运行时遇到可能使处理不安全的超大 VCS 输出
- `WHAT`: 使用显式校验与大小保护实现快速失败
- `WHY`: 避免静默错误结果、失控内存占用或模糊的失败行为
- `Story`: As a CLI operator, I want invalid `--scope` values to be rejected at input validation and oversized VCS outputs to be caught before processing, so that the tool fails fast with clear diagnostics instead of producing silent wrong results or running out of memory.
- `Support`: `scope=input and runtime guard` | `alg=A and B` | `vcs=git-focused runtime checks` | `tier=Fast`
- `Status`: 第一类硬化故事。
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28`

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

**`AC-HARD-04`**

- `GIVEN`: CLI 收到非法 `--algorithm` 值，例如 `C`、`0` 或空字符串
- `WHEN`: 输入校验执行
- `THEN`: 工具以 `EXIT_INPUT_ERROR` 退出，并输出包含 `--algorithm must be one of: A, B` 的诊断信息

**`AC-HARD-05`**

- `GIVEN`: CLI 收到无法解析为有效时间戳的 `startTime` 或 `endTime` 值（例如非 ISO-8601、缺少时区或非数字格式）
- `WHEN`: 输入校验执行
- `THEN`: 工具以 `EXIT_INPUT_ERROR` 退出，并输出诊断信息，指明哪个字段无效以及期望的格式

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29: Info 级日志必须展示初始加载、逐行状态迁移与最终汇总

- `WHO`: 使用 `--logLevel info` 运行的 CLI 操作员
- `WHEN`: 操作员希望通过 stderr 理解归因故事，但又不想开启完整的 debug 日志量级
- `WHAT`: 提供一个三阶段的 info 级叙事，覆盖起始状态、逐行迁移提示与最终汇总
- `WHY`: 帮助操作员理解哪些行发生了归属变迁，以及最终聚合结果意味着什么，而不必切换到 `--logLevel debug`
- `Story`: As a CLI operator running with `--logLevel info`, I want to see a three-phase narrative on stderr showing initial load state, per-line state transitions, and final summary, so that I can understand the full attribution story without switching to `--logLevel debug`.
- `Support`: `scope=stderr behavior` | `alg=primarily A` | `vcs=shared` | `tier=Fast target`
- `Status`: USNG 中已记录的故事。当前可执行测试覆盖仍然是未补齐缺口。
- `Anchors`: `OperatorScenarioNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29-AI-TO-HUMAN-SHAPE`, `OperatorScenarioNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29-HUMAN-TO-AI-SHAPE`, `TestsNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29`

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

- `GIVEN`: 以 `--logLevel info` 执行批准的 `OperatorScenarioNG-...-29-AI-TO-HUMAN-SHAPE`
- `WHEN`: 报告归属迁移
- `THEN`: stderr 包含 `best_effort_transition=100%-ai->human/unattributed`

**`AC-OPS-07`**

- `GIVEN`: 以 `--logLevel info` 执行批准的 `OperatorScenarioNG-...-29-HUMAN-TO-AI-SHAPE`
- `WHEN`: 报告归属迁移
- `THEN`: stderr 包含 `best_effort_transition=human/unattributed->100%-ai`

## Scope 扩展（Complicated 与 Complex 历史）

这些故事将故事 02–07（COMPLICATED 归因语义）和故事 09–11（COMPLEX 规模/深度语义）的 SHARED 行为契约扩展到文档文件家族（SCOPE-B）、源码加注释的组合 scope（SCOPE-C）以及全文件家族 scope（SCOPE-D）。契约在各 scope 间一致；只有文件家族选择器发生变化。

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-B-36: 归因契约同等适用于文档行

- `WHO`: 仓库分析者
- `WHEN`: 目标 scope 是文档文件家族（SCOPE-B），且历史窗口包含重写、删除、重命名或合并
- `WHAT`: 将与 SCOPE-A 相同的归因解析规则应用于仅文档行
- `WHY`: 归因语义的指标契约必须对文档文件与源码文件同等成立
- `Story`: As a repository analyst, I want the complete COMPLICATED-history attribution contract to apply to documentation lines (SCOPE-B), so that file family does not create a different rule set for human-vs-AI ownership resolution.
- `Support`: `scope=B doc baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: 故事 02–07 到文档家族的 scope 扩展。行为契约与 SCOPE-A 一致；只有 `scope` 选择器发生变化。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-B-36`

**`AC-01`**

- `GIVEN`: 某条文档行在 `endTime` 之前曾被归因于 AI
- `WHEN`: 某次人工修订覆盖了该行
- `THEN`: 归因重置为该次人工修订

**`AC-02`**

- `GIVEN`: 某条文档行在 `endTime` 之前曾被归因于人工
- `WHEN`: 某次更新的 AI 修订覆盖了该行
- `THEN`: 归因变为该次 AI 修订

**`AC-03`**

- `GIVEN`: AI 归因的文档行在窗口内存在，但在 `endTime` 时已从分支状态中消失
- `WHEN`: 分析器聚合 SCOPE-B 结果
- `THEN`: 已删除的 AI 文档行被从分子与分母中同时排除

**`AC-04`**

- `GIVEN`: 某个文档文件在 `endTime` 之前被重命名或移动，但其内容未发生变化
- `WHEN`: 分析器解析存活行的归因
- `THEN`: 行归因在仅路径变化后保持不变

**`AC-05`**

- `GIVEN`: 一个请求窗口内包含文档提交，混合了仅人工、仅 AI、重写与删除路径
- `WHEN`: 分析器产出 SCOPE-B 聚合结果
- `THEN`: 每条存活文档行按其最新有效归因被解析

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-B-36` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-C-37: 归因契约同等适用于源码加注释的组合行

- `WHO`: 仓库分析者
- `WHEN`: 目标 scope 是源码加注释的组合（SCOPE-C），且历史窗口包含归因边缘情形
- `WHAT`: 将与 SCOPE-A 相同的归因解析规则应用于组合源码行
- `WHY`: 当注释行被纳入源码 scope 时，指标契约必须保持一致
- `Story`: As a repository analyst, I want the complete COMPLICATED-history attribution contract to apply to combined source-and-comment lines (SCOPE-C), so that adding comment lines to the scope does not change attribution resolution semantics.
- `Support`: `scope=C combined baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: 故事 02–07 到组合源码 scope 的扩展。行为契约与 SCOPE-A 一致；只有 `scope` 选择器发生变化。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-C-37`

**`AC-01`**

- `GIVEN`: 目标 scope 为 SCOPE-C（代码 + 注释），窗口包含人工重写、AI 重写、删除、重命名与合并
- `WHEN`: 分析器为所有存活行解析归因
- `THEN`: 每条存活行的归因由与 SCOPE-A 相同的最新有效归因规则确定，独立适用于代码行与注释行

**`AC-02`**

- `GIVEN`: AI 归因的代码行或注释行在窗口内存在，但在 `endTime` 时已从分支状态中消失
- `WHEN`: 分析器聚合 SCOPE-C 结果
- `THEN`: 两个子家族中已删除的 AI 行都被从分子与分母中同时排除

**`AC-03`**

- `GIVEN`: 某个源码文件在 `endTime` 之前被重命名或移动，但其内容未发生变化
- `WHEN`: 分析器解析该文件存活代码行和注释行的归因
- `THEN`: 行归因在仅路径变化后对代码行和注释行子家族均保持不变

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-C-37` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-D-38: 归因契约同等适用于全文件家族 Scope

- `WHO`: 仓库分析者
- `WHEN`: 目标 scope 覆盖所有文件家族（SCOPE-D），且历史窗口包含归因边缘情形
- `WHAT`: 将与 SCOPE-A 相同的归因解析规则整体应用于所有文件家族
- `WHY`: 跨所有家族的单一聚合结果必须与各自家族的结果保持一致的归因解析
- `Story`: As a repository analyst, I want the complete COMPLICATED-history attribution contract to apply when SCOPE-D covers all file families together, so that combining families in one aggregate does not create attribution inconsistencies.
- `Support`: `scope=D all-families baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: 故事 02–07 到全文件家族 scope 的扩展。行为契约与 SCOPE-A 一致；只有 `scope` 选择器发生变化。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-D-38`

**`AC-01`**

- `GIVEN`: 目标 scope 为 SCOPE-D，窗口包含跨源码、文档及其他文件家族的归因边缘情形
- `WHEN`: 分析器产出全文件家族聚合结果
- `THEN`: 每条存活行的归因由相同的最新有效归因规则解析，无论它属于哪个家族

**`AC-02`**

- `GIVEN`: 归因边缘情形为每个构成家族 scope 分别产出特定结果
- `WHEN`: 计算 SCOPE-D 聚合结果
- `THEN`: 其聚合值与把各构成家族的分子和分母相加后的值在算术上保持一致

**`AC-03`**

- `GIVEN`: 某个源码或文档文件在 `endTime` 之前被重命名或移动，但其内容未发生变化
- `WHEN`: 分析器在 SCOPE-D 下解析该文件存活行的归因
- `THEN`: 无论该文件属于哪个文件家族，行归因在仅路径变化后保持不变

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-D-38` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-B-39: 大型仓库规模契约对文档行同等成立

- `WHO`: 仓库分析者
- `WHEN`: 仓库包含许多文档文件和许多存活文档行，目标 scope 为 SCOPE-B
- `WHAT`: 保持文档行在规模下的结果语义，与故事 09 保持一致
- `WHY`: 仓库大小不得降级或改变文档文件家族的指标语义
- `Story`: As a repository analyst, I want the COMPLEX-history scale contract for large repositories to apply to documentation lines (SCOPE-B), so that file family does not cause different scale behaviour.
- `Support`: `scope=B doc baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: 故事 09–11 到文档家族的 scope 扩展。语义契约与 SCOPE-A 一致；只有 `scope` 选择器发生变化。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-B-39`

**`AC-01`**

- `GIVEN`: 在 `endTime` 时刻的最终存活 SCOPE-B 快照跨越许多文档文件和许多存活行
- `WHEN`: 分析器计算最终聚合 SCOPE-B 结果
- `THEN`: 仓库大小和文档文件数量不会改变逐行归因规则或最终结果的协议形态

**`AC-02`**

- `GIVEN`: 在 `endTime` 时刻存活的文档行经历了漫长的修订链
- `WHEN`: 分析器解析每条存活文档行
- `THEN`: 它使用最新有效归因而不是更早已被取代的修订

**`AC-03`**

- `GIVEN`: 许多分支在 `endTime` 之前被合并进目标分支，且存活文档行来自不同的被合并分支
- `WHEN`: 分析器解析最终 SCOPE-B 存活状态
- `THEN`: 每条存活文档行被独立保留，归属不会被压平为 merge commit 或分支身份

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-B-39` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-C-40: 大型仓库规模契约对组合源码行同等成立

- `WHO`: 仓库分析者
- `WHEN`: 仓库包含许多源码行和注释行，目标 scope 为 SCOPE-C
- `WHAT`: 保持组合源码行在规模下的结果语义，与故事 09 保持一致
- `WHY`: 仓库大小不得降级或改变组合源码 scope 的指标语义
- `Story`: As a repository analyst, I want the COMPLEX-history scale contract for large repositories to apply to combined source-and-comment lines (SCOPE-C), so that combining code and comment families does not cause different scale behaviour.
- `Support`: `scope=C combined baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: 故事 09–11 到组合源码 scope 的扩展。语义契约与 SCOPE-A 一致；只有 `scope` 选择器发生变化。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-C-40`

**`AC-01`**

- `GIVEN`: 最终存活 SCOPE-C 快照跨越许多文件中的许多源码行和注释行
- `WHEN`: 分析器产出 SCOPE-C 聚合结果
- `THEN`: 结果语义、逐行归因规则和协议形态与 SCOPE-A 规模契约一致

**`AC-02`**

- `GIVEN`: 许多分支被合并进目标分支，且存活行跨越代码和注释家族
- `WHEN`: 分析器解析最终 SCOPE-C 存活状态
- `THEN`: 无论文件家族如何，逐行归因被独立保留

**`AC-03`**

- `GIVEN`: 在 `endTime` 时刻跨代码和注释家族的存活行经历了含有许多中间重写的漫长修订链
- `WHEN`: 分析器解析每条存活 SCOPE-C 行
- `THEN`: 它使用最新有效归因而不是更早已被取代的修订，独立适用于代码行和注释行

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-C-40` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-D-41: 大型仓库规模契约对全文件家族 Scope 同等成立

- `WHO`: 仓库分析者
- `WHEN`: 仓库包含跨所有家族的许多文件，目标 scope 为 SCOPE-D
- `WHAT`: 保持全文件家族 scope 在规模下的结果语义，与故事 09 保持一致
- `WHY`: 全面的全文件家族聚合结果在大型仓库规模下必须保持正确且一致
- `Story`: As a repository analyst, I want the COMPLEX-history scale contract for large repositories to apply to all file families together (SCOPE-D), so that the comprehensive aggregate result remains correct and consistent at production scale.
- `Support`: `scope=D all-families baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: 故事 09–11 到全文件家族 scope 的扩展。语义契约与 SCOPE-A 一致；只有 `scope` 选择器发生变化。
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-D-41`

**`AC-01`**

- `GIVEN`: 最终存活 SCOPE-D 快照跨越源码、文档及所有其他家族的许多文件
- `WHEN`: 分析器产出全文件家族聚合结果
- `THEN`: 结果语义、逐行归因规则和协议形态与 SCOPE-A 规模契约一致

**`AC-02`**

- `GIVEN`: 一个大型仓库为每个构成家族 scope 都产出了明确的结果
- `WHEN`: 对同一仓库计算 SCOPE-D 聚合结果
- `THEN`: 其聚合值与把各构成家族的分子和分母相加后的值在算术上保持一致

**`AC-03`**

- `GIVEN`: 在 `endTime` 时刻跨所有文件家族的存活行经历了含有许多中间重写的漫长修订链
- `WHEN`: 分析器解析每条存活 SCOPE-D 行
- `THEN`: 无论该行属于哪个文件家族，它使用最新有效归因而不是更早已被取代的修订

**`AC-04`**

- `GIVEN`: 许多分支在 `endTime` 之前被合并进目标分支，且存活行来自跨源码、文档及其他文件家族的不同被合并分支
- `WHEN`: 分析器解析最终 SCOPE-D 存活状态
- `THEN`: 无论文件家族如何，每条存活行被独立保留，归属不会被压平为 merge commit 或分支身份

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-D-41` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

---

### USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-42: SVN Path-Copy 分支不得扭曲归因谱系

- `WHO`: 仓库分析者
- `WHEN`: SVN 仓库在测量窗口内使用基于路径的分支（复制后修改）
- `WHAT`: 正确追溯 path-copy 分支来源上的行归因，而不是从复制操作的时间戳开始
- `WHY`: SVN 通过文件系统 `svn copy` 而不是引用进行分支；复制后修改是 SVN 的规范分支机制，不得将归因压平为复制行为本身
- `Story`: As a repository analyst using an SVN repository, I want path-copy branches to trace attribution back to the original lines on the trunk or source branch, so that the copy operation itself is never treated as the attribution origin.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=svn-local; path-based branching` | `tier=Fast`
- `Status`: SVN 特有的 COMPLICATED 行为。Git 使用引用分支与 git-follow；SVN 使用 path-copy 语义。本故事没有 Git-LOCAL 等价物——它不被 SHARED COMPLICATED 故事 02–07 所覆盖。
- `Anchors`: `TestdataNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-42`

**`AC-01`**

- `GIVEN`: SVN 分支通过 `svn copy trunk@R branches/feature` 在修订 R 处创建
- `WHEN`: 分析器解析 `branches/feature` 上自复制以来未改动的存活行的归因
- `THEN`: 这些行保留其原始 trunk 归因，而不是获得修订 R 的归因时间戳

**`AC-02`**

- `GIVEN`: 某条行通过 `svn copy` 从 trunk 复制，然后在 `endTime` 之前在 feature 分支上被覆盖
- `WHEN`: 分析器解析该行的归因
- `THEN`: 它使用复制后修改的归因，而不是原始 trunk 归因

**`AC-03`**

- `GIVEN`: 某个 path-copy 分支在 `endTime` 之前被合并回 trunk
- `WHEN`: 分析器解析存活的被合并行的归因
- `THEN`: 每条行保留其有效来源修订的归因，而不是 trunk 上的合并提交

**`AC-04`**

- `GIVEN`: 某个分支本身是从另一个 path-copy 分支创建的（嵌套复制）
- `WHEN`: 分析器遍历修订历史
- `THEN`: 它沿着复制链追溯到最深层的有效修改修订，而不是停在某个中间复制修订处

**`AC-ALG-A-01`**

- `GIVEN`: 已批准的 `TestdataNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-42` 场景
- `WHEN`: Algorithm A 执行
- `THEN`: 结果与该场景批准的 NG golden 输出一致

---

## 远程拓扑契约故事

这些故事定义远程仓库访问和 provider 侧元数据拓扑的契约边界。所有 SHARED 行为故事（故事 01–11、14–17、36–41）通过委托适用于远程拓扑。远程拓扑故事只新增远程情形特有的访问路径边界契约。

### USNG-REPO-GIT-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-30: 远程 Git 身份不得改变测量契约

- `WHO`: 仓库分析者或 CLI 操作员
- `WHEN`: 仓库通过远程 Git 身份（clone URL、远程跟踪分支或逻辑远程名称）寻址，而受支持的运行时通过可用的本地 checkout 或委托的 fetch 路径解析
- `WHAT`: 保持测量契约与等价 Git 本地访问完全一致
- `WHY`: 分析者不应关心运行时是通过本地 clone 还是远程调用解析——入口只是寻址关注点，不是契约变化
- `Story`: As a repository analyst, I want addressing a repository through a remote Git identity to produce the same measurement contract as Git local access, so that operator entry point does not change metric semantics.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git remote-identity resolution` | `tier=Fast`
- `Status`: 远程 Git 身份是由运行时解析的寻址关注点。所有针对 HISTORY-COMPLICATED（02–07、36–38）和 HISTORY-COMPLEX（09–11、39–41）的 SHARED 行为故事通过委托适用于此拓扑。本故事只新增远程情形特有的访问路径边界契约。
- `Anchors`: `TestsNG-REPO-GIT-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-30`

**`AC-01`**

- `GIVEN`: 相同的仓库内容通过远程 Git 身份而不是直接本地路径寻址
- `WHEN`: 测量通过受支持的运行时解析路径执行
- `THEN`: 结果具有协议形态，且与通过本地 Git checkout 寻址相同内容的结果契约完全一致

**`AC-02`**

- `GIVEN`: 远程 Git 身份无法解析（网络不可达、无效远程或缺少凭据）
- `WHEN`: CLI 或 API 执行
- `THEN`: 它以清晰的诊断信息退出，指明无法解析的远程地址，而不是静默产出空结果或部分结果

---

### USNG-REPO-SVN-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-31: 远程 SVN URL 不得改变测量契约

- `WHO`: 仓库分析者或 CLI 操作员
- `WHEN`: SVN 仓库通过远程 URL（`svn+ssh://`、`https://`、`svn://`）而不是 `file:///` 路径寻址
- `WHAT`: 保持测量契约与等价 SVN 本地访问完全一致
- `WHY`: SVN 远程访问是访问路径关注点——更改它不应改变指标语义或输出结构
- `Story`: As a repository analyst, I want addressing a repository through a remote SVN URL to produce the same measurement contract as SVN local (`file:///`) access, so that SVN access method does not change metric semantics.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=svn remote URL resolution` | `tier=Fast`
- `Status`: 远程 SVN URL 是由运行时解析的访问路径关注点。所有针对 HISTORY-COMPLICATED（02–07、36–38）和 HISTORY-COMPLEX（09–11、39–41）的 SHARED 行为故事以及 SVN 特有的 COMPLICATED 契约（42）通过委托适用于此拓扑。本故事只新增远程情形特有的访问路径边界契约。
- `Anchors`: `TestsNG-REPO-SVN-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-31`

**`AC-01`**

- `GIVEN`: 相同的仓库内容通过远程 SVN URL 而不是 `file:///` 路径寻址
- `WHEN`: 测量通过受支持的 SVN 运行时路径执行
- `THEN`: 结果具有协议形态，且与通过本地 SVN 路径寻址相同内容的结果契约完全一致

**`AC-02`**

- `GIVEN`: 远程 SVN URL 无法解析（认证失败、网络错误或无效 URL scheme）
- `WHEN`: CLI 或 API 执行
- `THEN`: 它以清晰的诊断信息退出，指明 SVN 远程访问失败，而不是静默产出空结果或部分结果

---

### USNG-REPO-SHARED-GENCODEDESC-REMOTE-HISTORY-SIMPLE-SCOPE-A-32: Provider 侧 genCodeDesc 元数据不得改变测量契约

- `WHO`: 仓库分析者
- `WHEN`: genCodeDesc 元数据从 provider 服务或外部 API 获取，而不是从本地目录读取
- `WHAT`: 无论元数据来自何处，保持测量契约完全一致
- `WHY`: 测量结果（加权 AI 占比）不应依赖于元数据来自本地缓存还是远程服务
- `Story`: As a repository analyst, I want the measurement result to be contract-identical whether genCodeDesc metadata comes from a local directory or an external provider service, so that metadata topology does not change metric semantics.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Provider 侧元数据获取是元数据拓扑关注点。所有针对 HISTORY-COMPLICATED（02–07、36–38）和 HISTORY-COMPLEX（09–11、39–41）的 SHARED 行为故事通过委托适用于此拓扑。本故事只新增 provider 远程情形特有的元数据提供方边界契约。
- `Anchors`: `TestsNG-REPO-SHARED-GENCODEDESC-REMOTE-HISTORY-SIMPLE-SCOPE-A-32`

**`AC-01`**

- `GIVEN`: genCodeDesc 记录从远程 provider 获取，按 `repoURL + repoBranch + revisionId` 索引
- `WHEN`: 分析器聚合存活快照结果
- `THEN`: 结果具有协议形态，且与等价本地元数据分析的结果契约完全一致

**`AC-02`**

- `GIVEN`: 远程 genCodeDesc provider 对所需记录返回错误、超时或部分响应
- `WHEN`: 分析器尝试获取这些记录
- `THEN`: 它以清晰的诊断信息失败，指明 provider 失败情况，而不是把缺失记录视为人工归因

**`AC-03`**

- `GIVEN`: 远程 genCodeDesc provider 为部分修订成功返回记录，但在同一次运行中对一个或多个其他所需修订未返回记录
- `WHEN`: 分析器处理该部分响应
- `THEN`: 缺失修订的行被计为人工无归因（与故事 01 的 AC-03 相同），且该缺失可通过 `--logLevel debug` 观察到，而不是被静默并入 AI 归因

---

## Period-Added Scope 扩展故事

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-33: 文档行的 Period-Added 指标必须遵循与 SCOPE-A 相同的窗口契约

- `WHO`: 仓库分析者
- `WHEN`: 希望衡量在请求周期内新增或修改的文档行的 AI 贡献
- `WHAT`: 在请求窗口内报告文档行的 period-added AI 归因
- `WHY`: 文档演化需要其独立于源码测量的归因窗口
- `Story`: As a repository analyst, I want the period-added metric for documentation lines (SCOPE-B) to report correct AI attribution within a requested period window, so that documentation output can be attributed with the same rigor as source-code output.
- `Support`: `scope=B` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: 新 USNG 格子。Algorithm B 文档行回放覆盖已批准的 period 窗口定义本故事边界。
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-33`

**`AC-ALG-B-01`**

- `GIVEN`: 某个 Git 仓库包含文档文件，且请求周期定义了 `startTime~endTime` 窗口
- `WHEN`: `Algorithm B` 以 `--scope B` 计算 period-added 指标
- `THEN`: 它使用与 SCOPE-A 相同的回放契约报告窗口内新增的 AI 归因文档行，但只过滤文档行家族

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-34: 组合源码 Scope 的 Period-Added 指标必须在一个 Period 结果中聚合代码与注释

- `WHO`: 仓库分析者
- `WHEN`: 希望衡量在请求周期内新增的组合源码行（代码 + 注释）的 AI 贡献
- `WHAT`: 在一个组合结果中报告代码行和注释行的 period-added AI 归因
- `WHY`: 部分团队跨代码和注释归因 AI 贡献，以便一次查询捕获完整的源码编辑画面
- `Story`: As a repository analyst, I want the period-added metric for combined source lines (SCOPE-C) to aggregate both code and comment lines in one period result, so that AI attribution covers the full source-editing footprint during a period.
- `Support`: `scope=C` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: 涵盖 period-added 测量的组合源码家族的新 USNG 格子。
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-34`

**`AC-ALG-B-01`**

- `GIVEN`: 某个 Git 仓库包含同时具有代码行和注释行的源码文件，且请求周期定义了窗口
- `WHEN`: `Algorithm B` 以 `--scope C` 计算 period-added 指标
- `THEN`: 它在一个组合 period 结果中报告窗口内新增的来自代码和注释家族的 AI 归因行

**`AC-ALG-B-02`**

- `GIVEN`: `Algorithm B` 产出 period-added SCOPE-C 结果
- `WHEN`: 读取结果 `SUMMARY`
- `THEN`: 代码家族和注释家族的归因值在 `SUMMARY` 字段内各自独立可访问，而不是合并为单一未区分的计数

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-35: 全 Scope 的 Period-Added 指标必须在一个 Period 结果中覆盖代码、注释与文档

- `WHO`: 仓库分析者
- `WHEN`: 希望在一个周期内获得跨所有行家族（代码、注释、文档）的 AI 贡献的单一综合视图
- `WHAT`: 在一个 period 结果中报告所有行家族的 period-added AI 归因
- `WHY`: 领导层摘要需要一个覆盖所有 AI 新增内容的数字，不区分行家族
- `Story`: As a repository analyst, I want the period-added metric for all line families (SCOPE-D) to cover code, comment, and documentation lines in one period result, so that one query answers how much total content was AI-attributed during a period.
- `Support`: `scope=D` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: 涵盖 period-added 测量的全家族聚合的新 USNG 格子。
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-35`

**`AC-ALG-B-01`**

- `GIVEN`: 某个 Git 仓库同时包含源码文件和文档文件，且请求周期定义了窗口
- `WHEN`: `Algorithm B` 以 `--scope D` 计算 period-added 指标
- `THEN`: 它在一个组合 period 结果中报告跨代码、注释和文档家族的 AI 归因行

**`AC-ALG-B-02`**

- `GIVEN`: `Algorithm B` 产出 period-added SCOPE-D 结果
- `WHEN`: 读取结果 `SUMMARY`
- `THEN`: 代码家族、注释家族和文档家族的归因值在 `SUMMARY` 字段内各自独立可访问

---

## 追踪附录

只有在审计、对照或搜索仍然需要更早的家族式 `USNG-*` 引用或旧版 `US-*` 引用时，才使用本附录。上方主故事层现在使用 4D `USNG-*` 标识符。

- 存活快照谱系：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01` -> 旧 `USNG-LS-01` -> `US-1`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02` -> 旧 `USNG-LS-02`（原 `USNG-REPO-GIT-LOCAL-…-02`）-> `US-2`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03` -> 旧 `USNG-LS-03`（原 `USNG-REPO-GIT-LOCAL-…-03`）-> `US-3`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04` -> 旧 `USNG-LS-04`（原 `USNG-REPO-GIT-LOCAL-…-04`）-> `US-4`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05` -> 旧 `USNG-LS-05`（原 `USNG-REPO-GIT-LOCAL-…-05`）-> `US-5`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-06` -> 旧 `USNG-LS-06`（原 `USNG-REPO-GIT-LOCAL-…-06`）-> `US-7`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-07` -> 旧 `USNG-LS-07`（原 `USNG-REPO-GIT-LOCAL-…-07`）-> `US-8`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08` -> 旧 `USNG-LS-08` -> `US-9`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-09` -> 旧 `USNG-LS-09`（原 `USNG-REPO-GIT-LOCAL-…-09`）-> `US-10`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-10` -> 旧 `USNG-LS-10`（原 `USNG-REPO-GIT-LOCAL-…-10`）-> `US-11`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-11` -> 旧 `USNG-LS-11`（原 `USNG-REPO-GIT-LOCAL-…-11`）-> `US-12`
- 生产 gate 谱系：`USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12` -> 旧 `USNG-PG-01` -> `US-13`；`USNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13` -> 旧 `USNG-PG-02` -> `US-14`
- Scope 契约谱系：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14` -> 旧 `USNG-SC-01` -> `US-20`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-C-15` -> 旧 `USNG-SC-02` -> `US-21`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-D-16` -> 旧 `USNG-SC-03` -> `US-22`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-17` -> 旧 `USNG-SC-04` -> `US-23`
- Algorithm B Scope 谱系：`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-18` -> 旧 `USNG-AB-01` -> `US-24`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-19` -> 旧 `USNG-AB-02` -> `US-25`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-20` -> 旧 `USNG-AB-03` -> `US-26`
- period-added 谱系：`USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` -> 旧 `USNG-PA-01` -> `US-6`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-22` -> 旧 `USNG-PA-02` -> `US-15`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-23` -> 旧 `USNG-PA-03` -> `US-16`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24` -> 旧 `USNG-PA-04` -> `US-17`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25` -> 旧 `USNG-PA-05` -> `US-18`；`USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26` -> 旧 `USNG-PA-06` -> `US-19`
- 跨算法、硬化与操作员谱系：`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27` -> 旧 `USNG-CA-01` -> `US-27`；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28` -> 旧 `USNG-CA-02` -> `US-28`；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29` -> 旧 `USNG-CA-03` -> `US-29`
- 仅出现于新 USNG 的故事（无旧 US-* 等价物）：`USNG-REPO-GIT-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-30`（远程 Git 契约）；`USNG-REPO-SVN-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-31`（远程 SVN 契约）；`USNG-REPO-SHARED-GENCODEDESC-REMOTE-HISTORY-SIMPLE-SCOPE-A-32`（远程 genCodeDesc 契约）；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-33`（period-added SCOPE-B）；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-34`（period-added SCOPE-C）；`USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-35`（period-added SCOPE-D）；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-B-36`（文档行的 COMPLICATED 归因契约）；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-C-37`（组合源码行的 COMPLICATED 归因契约）；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-D-38`（全文件家族 scope 的 COMPLICATED 归因契约）；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-B-39`（文档行的 COMPLEX 规模契约）；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-C-40`（组合源码行的 COMPLEX 规模契约）；`USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-D-41`（全文件家族 scope 的 COMPLEX 规模契约）；`USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-42`（SVN path-copy 分支归因契约）
