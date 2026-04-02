# AggregateGenCodeDesc 使用指南

## 目的

本文档是 `aggregateGenCodeDesc.py` 的面向使用者的操作指南。

当你需要的是可直接执行的命令，而不是架构讨论时，请优先阅读这里。

本文重点回答这些问题：

- 运行前需要准备什么输入
- 常见场景下到底该执行哪条命令
- 什么时候该用 `Algorithm A`，什么时候该用 `Algorithm B`
- `repoURL` 与 `workingDir` 应该怎样配合
- 当前支持边界在哪里

如果你需要更偏设计或验收层的信息，请看：

- `README_UserStory.md`
- `README_SharedUS_Convergence.md`
- `README_ArchDesign.md`

## 快速理解

当前最常见的使用方式是：

1. 在 `--genCodeDescSetDir` 中准备好修订级 `genCodeDesc` 元数据
2. 选择 `--vcsType git` 或 `--vcsType svn`
3. 如果要分析真实仓库历史，优先用 `Algorithm A`
4. 如果你是有意验证当前狭义回放路径，再用带 `--commitDiffSetDir` 的 `Algorithm B`

本指南按目标中的生产就绪操作体验来写。
这意味着内部实现分流细节不应该被当作普通用户必须关心的参数。

## 当前支持矩阵

### 面向生产的主路径

- `Algorithm A + Git + Scope A`：当前生产目标
- `Algorithm A + SVN + Scope A`：当前生产目标

### 狭义回放基线路径

- `Algorithm B + Git + Scope A`：已支持当前批准的回放场景
- `Algorithm B + SVN + Scope A`：已支持当前批准的回放场景

重要边界：

- `Algorithm B` 目前仍是狭义的回放型路径
- 它适用于当前已批准的夹具形态
- 它不等于已经对所有更复杂历史拓扑给出生产就绪承诺

## 前置条件

### 基础运行环境

- Python 3
- Git 运行需要本地已安装 Git
- SVN 运行需要本地已安装 SVN

### 基本输入参数

每次运行都需要：

- `--repoURL`
- `--repoBranch`
- `--startTime`
- `--endTime`

大多数有意义的运行还需要：

- `--genCodeDescSetDir`

当前 `Algorithm B` 还额外需要：

- `--algorithm B`
- `--commitDiffSetDir`

## 核心参数说明

### `--repoURL`

逻辑上的仓库身份。

- 对 Git 本地路径运行，它可以直接是本地仓库路径。
- 对 Git 逻辑 URL 运行，例如 `https://example.local/repo/demo.git`，它表示元数据身份和最终输出身份，而不是本地 checkout 路径。
- 对 SVN，它同时表示逻辑仓库身份和实时访问目标。

### `--workingDir`

Git 专用辅助参数，用于逻辑 `repoURL` 模式。

适用场景：

- `--vcsType git`
- `--repoURL` 不是本地绝对路径
- 但你仍希望 Git 命令在一个本地 checkout 上执行

普通 SVN URL 运行不需要它。

### `--genCodeDescSetDir`

用于放修订级元数据文件的目录，例如：

- `<revisionId>_genCodeDesc.json`

当前运行时会验证元数据身份，所以元数据里的 `REPOSITORY` 块必须与当前目标运行一致。

### `--algorithm`

- `A`：当前面向生产的真实仓库分析路径
- `B`：当前狭义回放型路径

默认值是 `A`。

### `--commitDiffSetDir`

当前 `Algorithm B` 必需参数。

该目录必须包含原始 unified diff patch，例如：

- `<timeSeq>_<revisionId>_commitDiff.patch`

## 生产形态下的 UX 说明

按目标中的生产就绪操作体验，用户不应该为了让 `Algorithm B` 走到正确路径，就额外承担内部实现分流参数。

因此，本指南不会把 `--metric` 当作主路径下普通操作人员必须理解的参数。

当前实现说明：

- 当前有些 `Algorithm B` 路径在内部仍通过 `--metric` 做分流
- 这属于实现过渡细节，不是面向最终用户的长期 CLI 契约
- 下方示例按目标中的生产形态来写

## 典型用法示例

### 1. 典型 Git 生产风格运行：`Algorithm A`

当你有真实本地 Git 仓库，以及本地元数据目录时，使用这个。

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL /path/to/local/git/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

适用场景：

- Git 历史就在本地
- 你要跑当前主路径的存活快照指标
- 你不是在刻意验证回放夹具

### 2. 典型 Git 逻辑 URL + 本地 checkout 运行

当元数据身份必须使用逻辑 URL，但 Git 命令仍需对本地 checkout 执行时，使用这个。

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/demo.git \
  --workingDir /path/to/local/git/checkout \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

### 3. 典型 SVN 生产风格运行：`Algorithm A`

当你要走当前面向生产的 SVN 主路径时，使用这个。

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///path/to/local/svn/repo \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

如果环境允许，也可以把 `file:///...` 换成真正的 SVN 服务 URL。

### 4. 典型 `Algorithm B` Git 回放运行

只有在你有意使用当前狭义回放路径时才使用这个。

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/demo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-b-git-out.json \
  --genCodeDescSetDir testdata/us1_live_changed_source_ratio \
  --commitDiffSetDir testdata/us1_live_changed_source_ratio/commitDiffSet
```

### 5. 典型 `Algorithm B` SVN 回放运行

只有在你有意使用当前狭义回放路径，并且目标是 SVN 时才使用这个。

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL https://svn.example.com/repos/project \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-b-svn-out.json \
  --genCodeDescSetDir testdata/us1_live_changed_source_ratio_svn \
  --commitDiffSetDir testdata/us1_live_changed_source_ratio_svn/commitDiffSet
```

### 6. 当前 `US-6` 风格的 period-added 回放示例

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/demo \
  --repoBranch main \
  --startTime 2026-03-10 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-b-period-out.json \
  --genCodeDescSetDir testdata/us6_period_added_ratio \
  --commitDiffSetDir testdata/us6_period_added_ratio/commitDiffSet
```

## 输出长什么样

典型输出是如下这种协议形态 JSON：

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

## 常见问题与修复办法

### `--workingDir is required for git`

原因：

- 你给的是逻辑 Git `repoURL`，不是本地绝对路径

修复：

- 补上 `--workingDir /path/to/local/git/checkout`

### `Metadata repoURL mismatch`

原因：

- 元数据文件中的仓库身份字符串和 CLI 目标不一致

修复：

- 让元数据里的 `REPOSITORY.repoURL` 与 CLI 的 `--repoURL` 完全一致

### `Protocol file not found for revision`

原因：

- 元数据目录里缺少当前修订对应的 `genCodeDesc` 文件

修复：

- 补上缺失的 `<revisionId>_genCodeDesc.json`

### `Commit diff patch file not found`

原因：

- 当前 `Algorithm B` 回放序列所需的 patch 文件在 `--commitDiffSetDir` 中缺失

修复：

- 补上缺失的 `<timeSeq>_<revisionId>_commitDiff.patch`

### `Algorithm B` 看起来还要求某个奇怪的内部参数

原因：

- 你碰到的是当前实现中的过渡性分流细节，而不是目标中的生产操作体验

修复：

- 对外使用时，应以本指南描述的目标操作契约为准
- 如果你当前是在调试内部实现，而不是按目标操作体验使用，请改看开发者相关文档和测试

### `--vcsType must be one of: git, svn`

原因：

- 传入了不支持的 VCS 类型

修复：

- 改成 `git` 或 `svn`

## 下一步该看哪个文档？

- 看 `README.md` 了解产品范围和指标定义
- 看 `README_UserStory.md` 了解故事级验收标准
- 看 `README_SharedUS_Convergence.md` 了解生产收敛路线图
- 看 `README_RunTestCase.md` 了解测试运行命令
- 看 `tests/README_US1_ManualInstruction.md` 获取更细的 US-1 手工验证步骤
