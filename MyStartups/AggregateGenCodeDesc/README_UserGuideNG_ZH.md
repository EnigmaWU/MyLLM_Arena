# AggregateGenCodeDesc 使用指南 NG

## 目的

如果你现在是真的要把 `aggregateGenCodeDesc.py` 跑起来，这份文档就是给你用的。

它不是先讲一大堆概念，而是先从你手头已经有什么出发，帮你尽快找到该怎么跑。

如果你现在脑子里冒出来的是下面这些问题，那就直接从这份文档开始：

- 我有一个本地 Git 仓库，应该先照着哪个示例做？
- 我只有 `genCodeDesc.json` 文件和一组 commit diff，应该选哪个算法？
- 在运行 CLI 之前，`startTime~endTime` 对应的元数据到底要准备到什么程度？
- 我该如何检查输入集是否完整，以及输出是否正确？

如果你想直接照着命令跑，请看 `UserExamplesNG/README_UserExamplesNG_ZH.md`。
如果你是想回查更完整的传统参数说明，再看 `README_UserGuide_ZH.md`。

## 先对齐一下

- 你现在手里有什么：本地 Git 或 SVN 仓库，或者一组离线 patch，再加上一批已经存在的 `genCodeDesc.json` 元数据。
- 你想拿到什么：在 `startTime~endTime` 这个窗口里，聚合后的结果 JSON，也就是 `aggregateGenCodeDesc.py` 的输出。
- 为什么我按这种方式来讲：因为操作者真正卡住的点，通常不是“算法定义是什么”，而是“我现在手里这套东西，到底该走哪条路径”。

## 先把话说清楚

`aggregateGenCodeDesc.py` 消费的是已经存在的仓库历史、commit diff 工件以及 `genCodeDesc.json` 元数据。

更准确地说，它不会替你生成或补齐那批“作为输入使用”的逐修订 `genCodeDesc.json` 元数据。

但它会基于 `startTime~endTime` 之间的信息聚合出一个新的结果 JSON，并把结果写到 `--outputFile`。如果你把这个输出文件命名成 `genCodeDesc.json`，也是可以的。

对于离线回放，`commitDiffSet/*.patch` 必须保持为标准 unified diff。

如果 patch 行尾为了便于人工阅读和核对而附带了类似 `# genRatio=100` 的尾注释，请把它视为仅供人工阅读的提示。真正的行归因信息仍然属于对应的 `*_genCodeDesc.json` 文件中的 `DETAIL.codeLines` 或 `DETAIL.docLines`，`aggregateGenCodeDesc.py` 不会读取 patch 行尾注释。

对于可执行的 NG 数据集，请保持 patch payload 本身干净，因为回放解析器会把这些行当作真实内容来应用。

所以你真正做事时，基本就是这三步：

1. 准备好或接收到元数据集合
2. 把 `aggregateGenCodeDesc.py` 指向该元数据集合
3. 校验 JSON 结果

只有“把示例数据集准备出来”这一步，可以交给 `generate_example.py` 这类辅助脚本。

真正执行 aggregate 的时候，还是应该老老实实写成显式的 `python3 aggregateGenCodeDesc.py ...` 命令。

## `startTime~endTime` 的含义

- `startTime` 和 `endTime` 定义分析时间窗口。
- 对于 Algorithm A 和 Algorithm B，工具需要与该窗口内待检查或待回放修订相匹配的 v26.03 修订级元数据。
- 对于 Algorithm C，工具会先累计到所选 end revision 为止的 v26.04 文件，再根据嵌入的 `blame.timestamp` 是否落在 `[startTime, endTime]` 内筛选最终存活的行。
- 因此，所需的元数据集合通常不止是 `endTime` 对应的单个文件。

## 开跑前先确认这些东西在手里

### Algorithm A：活跃仓库分析

- 一个本地 Git checkout，或一个可访问的 SVN 仓库
- `--genCodeDescSetDir`，其中包含匹配的 v26.03 `<revisionId>_genCodeDesc.json` 文件
- 覆盖目标窗口内待分析修订的元数据
- 显式的仓库身份参数与时间窗口参数

### Algorithm B：回放分析

- 对于本地 Git 回放：
  - 一个本地 Git 仓库
  - `--genCodeDescSetDir` 中匹配的 v26.03 元数据
- 对于 SVN 场景（包括本地 SVN 工作流）：
  - 先把 `startTime~endTime` 对应的修订窗口导出成按顺序排列的 patch 集
  - 再通过现有的 `--commitDiffSetDir` + `--genCodeDescSetDir` + `--vcsType svn` 这条路径运行
  - 换句话说，当前并没有单独的“本地 SVN 直接回放引擎”，SVN 走的还是同一条 commit diff set 回放路径
- 对于 commit diff set 回放（Git / SVN 都适用）：
  - `--commitDiffSetDir`，其中包含按顺序排列的 `NN_<revisionId>_commitDiff.patch` 文件
  - `--genCodeDescSetDir` 中匹配的 v26.03 元数据文件
  - 可选的 `queryArgs.json`，或通过 CLI 显式提供 `endRevisionId` 和 `includedRevisionIds`
- 显式指定 `--vcsType`，因为它决定运行时路径

### Algorithm C：embedded-blame 离线分析

- `--genCodeDescSetDir` 中的 v26.04 `*_genCodeDesc.json` 文件
- 每个 v26.04 文件中都要有合法的 `REPOSITORY.revisionTimestamp`
- 足够多的文件，以便累计到所选的 end revision
- 二选一：
  - `--genCodeDescSetDir` 内含 `queryArgs.json`
  - 或通过 CLI 显式提供仓库身份字段，例如 `--vcsType`、`--repoURL`、`--repoBranch`、`--endRevisionId`
- 对于 SVN 来源的 Algorithm C，如果数据集不包含 `queryArgs.json`，不要依赖裸命令；否则当前 CLI 在缺失 `--vcsType` 时会默认成 `git`。

## 可选择项目

| 你已经有什么 | 先从哪里开始 | 数据集路径 | 为什么这是合适的第一步 |
| --- | --- | --- | --- |
| 本地 Git 仓库加 v26.03 元数据 | `example-AlgA-localGIT` | `UserExamplesNG/dataset-localGIT-fullCoverage` | 最简单的活跃仓库基线 |
| 本地 Git 仓库加 v26.03 元数据，并且你想观察回放行为 | `example-AlgB-localGIT` | `UserExamplesNG/dataset-localGIT-fullCoverage` | 同一个生成数据集也支持本地 Git 回放 |
| 本地 SVN 仓库加 v26.03 元数据 | `example-AlgA-localSVN` | `UserExamplesNG/dataset-localSVN-fullCoverage` | 最简单的活跃 SVN 基线 |
| 本地 SVN 仓库，并且你希望通过导出的 patch 观察回放行为 | `example-AlgB-localSVN` | `UserExamplesNG/dataset-localSVN-fullCoverage` | 生成器会同时物化 patch 集和匹配元数据 |
| 只有 Git patch 集和 v26.03 元数据 | `example-AlgB-offline-GIT-basic` | `UserExamplesNG/dataset-AlgB-offline-GIT-basic` | 运行时不需要活跃仓库 |
| 只有 SVN patch 集和 v26.03 元数据 | `example-AlgB-offline-SVN-basic` | `UserExamplesNG/dataset-AlgB-offline-SVN-basic` | 运行时不需要活跃仓库 |
| 来自 Git 历史的 v26.04 embedded blame | `example-AlgC-embeddedBlame-GIT` | `UserExamplesNG/dataset-localGIT-fullCoverage` | 生成器会物化带 `queryArgs.json` 的 AlgC 可运行数据集 |
| 来自 SVN 历史的 v26.04 embedded blame | `example-AlgC-embeddedBlame-SVN` | `UserExamplesNG/dataset-localSVN-fullCoverage` | 生成器会物化带 `queryArgs.json` 的 AlgC 可运行 SVN 数据集 |
| 用于生产级练习的大型真实 Git 历史 | `example-AlgA-localGIT-productionScale` | `UserExamplesNG/dataset-localGIT-productionScale` | 重型真实仓库示例 |

## 建议你就按这个顺序来

1. 先选出与你手头资产匹配的算法。
2. 校验元数据集合是否覆盖目标 `startTime~endTime`。
3. 先原样跑通 `UserExamplesNG/README_UserExamplesNG_ZH.md` 里的一个示例，只修改输出文件路径。
4. 只有在示例成功之后，再把示例里的数据集路径替换成你的真实路径。
5. 只要数据集提供了 `expected_result.json` 或 `expected_<mode>_<scope>.json`，就对输出做精确对比。

## Summary 字段提醒

- Scope `A`、`B`、`D` 使用 `totalCodeLines`、`fullGeneratedCodeLines`、`partialGeneratedCodeLines`。
- Scope `C` 使用 `totalDocLines`、`fullGeneratedDocLines`、`partialGeneratedDocLines`。
- 即使 Scope `D` 同时聚合源码与文档文件，它仍然使用 `*CodeLines` 这一组 summary 字段名。

## 相关文档

- `UserExamplesNG/README_UserExamplesNG_ZH.md`
- `README_UserGuide_ZH.md`
- `README_UserStoryNG_ZH.md`
