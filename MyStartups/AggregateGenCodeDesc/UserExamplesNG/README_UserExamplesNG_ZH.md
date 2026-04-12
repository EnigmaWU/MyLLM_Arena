# AggregateGenCodeDesc 用户示例 NG

## 目的

这份文档不是按“算法教科书”的顺序来排的，而是按“你手头已经有什么”来排的。

换句话说，它更像是有人站在你旁边，先问你现在有什么，再告诉你下一步该跑哪条命令。

你往下看每个示例时，我主要帮你回答四件事：

- 你已经具备什么
- 如何运行 `aggregateGenCodeDesc.py`
- 如何验证输入集已经准备好
- 如何验证输出与期望结果一致

下面所有命令都默认你已经在项目根目录里：

```bash
cd /PATH/2/AggregateGenCodeDesc
```

## 先对齐一下

- 你现在手里有什么：可能是本地 Git 仓库、本地 SVN 仓库、离线 patch 集，或者一批已经准备好的 `genCodeDesc.json`。
- 你想拿到什么：一个可以直接核对的 aggregate 结果 JSON，以及一条你自己以后还能复用的命令行。
- 为什么我按这种方式排例子：因为大多数时候，操作者不会先问“Algorithm A 和 B 的定义差异是什么”，而是先问“我现在这包东西，应该从哪个例子抄起”。

## 快速索引

| 示例标签 | 适用场景 | 数据集路径 |
| --- | --- | --- |
| `example-AlgA-localGIT` | 你有一个本地 Git 仓库和 v26.03 元数据 | `UserExamplesNG/dataset-localGIT-fullCoverage` |
| `example-AlgB-localGIT` | 你有一个本地 Git 仓库，并且想看本地回放行为 | `UserExamplesNG/dataset-localGIT-fullCoverage` |
| `example-AlgC-embeddedBlame-GIT` | 你已经有，或者想生成一个 AlgC 可运行的 Git 来源 embedded-blame 数据集 | `UserExamplesNG/dataset-localGIT-fullCoverage` |
| `example-AlgA-localSVN` | 你有一个本地 SVN 仓库和 v26.03 元数据 | `UserExamplesNG/dataset-localSVN-fullCoverage` |
| `example-AlgB-localSVN` | 你有一个本地 SVN 工作流和导出的回放工件 | `UserExamplesNG/dataset-localSVN-fullCoverage` |
| `example-AlgC-embeddedBlame-SVN` | 你已经有，或者想生成一个 AlgC 可运行的 SVN 来源 embedded-blame 数据集 | `UserExamplesNG/dataset-localSVN-fullCoverage` |
| `example-AlgB-offline-GIT-basic` | 你只有 Git patch 流和 v26.03 元数据 | `UserExamplesNG/dataset-AlgB-offline-GIT-basic` |
| `example-AlgB-offline-SVN-basic` | 你只有 SVN patch 流和 v26.03 元数据 | `UserExamplesNG/dataset-AlgB-offline-SVN-basic` |
| `example-AlgA-localGIT-productionScale` | 你想练习一个重型真实 Git 仓库示例 | `UserExamplesNG/dataset-localGIT-productionScale` |

## 先说几句，免得跑偏

`aggregateGenCodeDesc.py` 会读取已有的 `genCodeDesc.json` 文件作为输入。

它不会替你生成那批逐修订输入元数据；但它会根据 `startTime~endTime` 聚合出新的结果 JSON，并写到 `--outputFile`。

对于 Algorithm B 离线回放，`commitDiffSet/*.patch` 保存的必须是真实 unified diff 内容。

如果你确实想在 patch 里直观看到 `genRatio` 提示，建议生成一份旁路查看用的 `commitDiffSetAnnotated/`：`python3 UserExamplesNG/render_annotated_commit_diff_set.py <datasetDir>`。真正参与 aggregate 的仍然应该是干净的 `commitDiffSet/`，实际输入也仍然来自 `genCodeDescSet/` 中匹配的 `*_genCodeDesc.json` 文件。

对于下面这些由生成器物化出来的数据集，`generate_example.py` 做的只是把必需输入先落到 `/tmp/` 下，方便你直接拿真实本地仓库和匹配元数据去跑 CLI。

生成器只是辅助工具。真正执行 aggregate 时，下面每条命令我都会直接写成 `python3 aggregateGenCodeDesc.py ...`，不会再包一层 shell 脚本。

如果你还想顺手核对 `stderr` 里的操作日志，就把示例命令显式加上 `--logLevel info`，把 `stderr` 重定向到日志文件，然后再跑 `python3 UserExamplesNG/check_info_log.py ...`。这个检查器就是专门看你要的三段：开始横幅、逐行 `LiveLine`、结束汇总。

## 数据集：`dataset-localGIT-fullCoverage`

这个生成器会物化一个本地 Git 仓库，以及三组与之匹配的输入集：

- `genCodeDescSet/`，供 Algorithm A 和 Algorithm B 使用
- `algcGenCodeDescSet/`，供 Algorithm C 使用
- `commitDiffSet/`，供 Algorithm B 离线回放使用

### 物化 `dataset-localGIT-fullCoverage`

```bash
python3 UserExamplesNG/dataset-localGIT-fullCoverage/generate_example.py \
  --outputDir /tmp/agg-userexample-ng-localgit \
  --force
```

### 校验 `dataset-localGIT-fullCoverage` 输入

```bash
python3 - <<'PY'
from pathlib import Path

base = Path('/tmp/agg-userexample-ng-localgit')
required = [
    base / 'repo',
    base / 'genCodeDescSet',
    base / 'algcGenCodeDescSet',
    base / 'algcGenCodeDescSet' / 'queryArgs.json',
    base / 'commitDiffSet',
    base / 'manifest.json',
]

for path in required:
    if not path.exists():
        raise SystemExit(f'Missing required input: {path}')

print('Input OK: local Git full-coverage dataset is ready')
PY
```

### `example-AlgA-localGIT`

你已经具备：

- 一个本地 Git 仓库
- 与目标窗口匹配的 v26.03 元数据

运行：

```bash
LOCAL_GIT_REPO="$(python3 - <<'PY'
from pathlib import Path
print(Path('/tmp/agg-userexample-ng-localgit/repo').resolve())
PY
)"

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL "$LOCAL_GIT_REPO" \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-userexample-ng-alga-localgit-a.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localgit/genCodeDescSet \
  --logLevel info \
  2> /tmp/agg-userexample-ng-alga-localgit-a.info.log
```

校验输出：

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-alga-localgit-a.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localgit/expected_alga_A.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgA-localGIT mismatch')

print('example-AlgA-localGIT OK')
PY
```

校验 info 日志：

```bash
python3 UserExamplesNG/check_info_log.py \
  --logFile /tmp/agg-userexample-ng-alga-localgit-a.info.log \
  --mode live \
  --scope A \
  --label example-AlgA-localGIT
```

### `example-AlgB-localGIT`

你已经具备：

- 一个本地 Git 仓库
- 匹配的 v26.03 元数据
- 你想观察回放行为，但不想另外搭建纯 patch 工作流

运行：

```bash
LOCAL_GIT_REPO="$(python3 - <<'PY'
from pathlib import Path
print(Path('/tmp/agg-userexample-ng-localgit/repo').resolve())
PY
)"

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL "$LOCAL_GIT_REPO" \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope D \
  --outputFile /tmp/agg-userexample-ng-algb-localgit-d.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localgit/genCodeDescSet \
  --logLevel info \
  2> /tmp/agg-userexample-ng-algb-localgit-d.info.log
```

校验输出：

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-algb-localgit-d.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localgit/expected_algb-local_D.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgB-localGIT mismatch')

print('example-AlgB-localGIT OK')
PY
```

校验 info 日志：

```bash
python3 UserExamplesNG/check_info_log.py \
  --logFile /tmp/agg-userexample-ng-algb-localgit-d.info.log \
  --mode algorithm-b \
  --scope D \
  --label example-AlgB-localGIT
```

### `example-AlgC-embeddedBlame-GIT`

你已经具备：

- v26.04 embedded-blame 文件
- 一个在 `algcGenCodeDescSet/` 内包含 `queryArgs.json` 的数据集

运行：

```bash
python3 aggregateGenCodeDesc.py \
  --algorithm C \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope B \
  --outputFile /tmp/agg-userexample-ng-algc-localgit-b.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localgit/algcGenCodeDescSet \
  --logLevel info \
  2> /tmp/agg-userexample-ng-algc-localgit-b.info.log
```

校验输出：

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-algc-localgit-b.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localgit/expected_algc_B.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgC-embeddedBlame-GIT mismatch')

print('example-AlgC-embeddedBlame-GIT OK')
PY
```

校验 info 日志：

```bash
python3 UserExamplesNG/check_info_log.py \
  --logFile /tmp/agg-userexample-ng-algc-localgit-b.info.log \
  --mode live \
  --scope B \
  --label example-AlgC-embeddedBlame-GIT
```

## 数据集：`dataset-localSVN-fullCoverage`

这个生成器会物化一个本地 SVN 仓库，以及与 Algorithm A、Algorithm B、Algorithm C 相匹配的输入集。

### 物化 `dataset-localSVN-fullCoverage`

```bash
python3 UserExamplesNG/dataset-localSVN-fullCoverage/generate_example.py \
  --outputDir /tmp/agg-userexample-ng-localsvn \
  --force
```

### 校验 `dataset-localSVN-fullCoverage` 输入

```bash
python3 - <<'PY'
from pathlib import Path

base = Path('/tmp/agg-userexample-ng-localsvn')
required = [
    base / 'svnrepo',
    base / 'workingCopy',
    base / 'genCodeDescSet',
    base / 'algcGenCodeDescSet',
    base / 'algcGenCodeDescSet' / 'queryArgs.json',
    base / 'commitDiffSet',
    base / 'manifest.json',
]

for path in required:
    if not path.exists():
        raise SystemExit(f'Missing required input: {path}')

print('Input OK: local SVN full-coverage dataset is ready')
PY
```

### `example-AlgA-localSVN`

你已经具备：

- 一个本地 SVN 仓库
- 与目标窗口匹配的 v26.03 元数据

运行：

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL "$(python3 - <<'PY'
from pathlib import Path
print(Path('/tmp/agg-userexample-ng-localsvn/svnrepo').resolve().as_uri())
PY
)" \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-userexample-ng-alga-localsvn-a.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localsvn/genCodeDescSet \
  --logLevel info \
  2> /tmp/agg-userexample-ng-alga-localsvn-a.info.log
```

校验输出：

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-alga-localsvn-a.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localsvn/expected_alga_A.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgA-localSVN mismatch')

print('example-AlgA-localSVN OK')
PY
```

校验 info 日志：

```bash
python3 UserExamplesNG/check_info_log.py \
  --logFile /tmp/agg-userexample-ng-alga-localsvn-a.info.log \
  --mode live \
  --scope A \
  --label example-AlgA-localSVN
```

### `example-AlgB-localSVN`

你已经具备：

- 一个本地 SVN 工作流
- 该窗口对应的导出 patch 工件
- 匹配的 v26.03 元数据

先说明一下：这里虽然叫 `localSVN`，但实际运行时走的还是导出 patch 之后的 `--commitDiffSetDir` 路径，并不是另一套单独的本地 SVN 直连回放引擎。

运行：

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL "$(python3 - <<'PY'
from pathlib import Path
print(Path('/tmp/agg-userexample-ng-localsvn/svnrepo').resolve().as_uri())
PY
)" \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope D \
  --outputFile /tmp/agg-userexample-ng-algb-localsvn-d.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localsvn/genCodeDescSet \
  --commitDiffSetDir /tmp/agg-userexample-ng-localsvn/commitDiffSet \
  --logLevel info \
  2> /tmp/agg-userexample-ng-algb-localsvn-d.info.log
```

校验输出：

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-algb-localsvn-d.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localsvn/expected_algb-svn-workflow_D.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgB-localSVN mismatch')

print('example-AlgB-localSVN OK')
PY
```

校验 info 日志：

```bash
python3 UserExamplesNG/check_info_log.py \
  --logFile /tmp/agg-userexample-ng-algb-localsvn-d.info.log \
  --mode algorithm-b \
  --scope D \
  --label example-AlgB-localSVN
```

### `example-AlgC-embeddedBlame-SVN`

你已经具备：

- 面向 SVN 来源历史的 v26.04 embedded-blame 文件
- 一个在 `algcGenCodeDescSet/` 中包含 `queryArgs.json` 的数据集

运行：

```bash
python3 aggregateGenCodeDesc.py \
  --algorithm C \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope B \
  --outputFile /tmp/agg-userexample-ng-algc-localsvn-b.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localsvn/algcGenCodeDescSet \
  --logLevel info \
  2> /tmp/agg-userexample-ng-algc-localsvn-b.info.log
```

校验输出：

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-algc-localsvn-b.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localsvn/expected_algc_B.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgC-embeddedBlame-SVN mismatch')

print('example-AlgC-embeddedBlame-SVN OK')
PY
```

校验 info 日志：

```bash
python3 UserExamplesNG/check_info_log.py \
  --logFile /tmp/agg-userexample-ng-algc-localsvn-b.info.log \
  --mode live \
  --scope B \
  --label example-AlgC-embeddedBlame-SVN
```

## `example-AlgB-offline-GIT-basic`

你已经具备：

- 一个 Git 来源的 `commitDiffSet/`
- 匹配的 v26.03 `genCodeDescSet/`
- 运行时不需要活跃仓库

校验输入：

```bash
python3 - <<'PY'
from pathlib import Path

base = Path('UserExamplesNG/dataset-AlgB-offline-GIT-basic')
patches = list((base / 'commitDiffSet').glob('*_commitDiff.patch'))
protocols = list((base / 'genCodeDescSet').glob('*_genCodeDesc.json'))

if len(patches) != 5 or len(protocols) != 5:
    raise SystemExit(f'Unexpected input counts: patches={len(patches)} protocols={len(protocols)}')

print('Input OK: offline Git basic dataset is ready')
PY
```

运行：

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/userexamples/git-basic \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-userexample-ng-algb-offline-git-basic.json \
  --genCodeDescSetDir UserExamplesNG/dataset-AlgB-offline-GIT-basic/genCodeDescSet \
  --commitDiffSetDir UserExamplesNG/dataset-AlgB-offline-GIT-basic/commitDiffSet \
  --logLevel info \
  2> /tmp/agg-userexample-ng-algb-offline-git-basic.info.log
```

校验输出：

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-algb-offline-git-basic.json').read_text())
expected = json.loads(Path('UserExamplesNG/dataset-AlgB-offline-GIT-basic/expected_result.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgB-offline-GIT-basic mismatch')

print('example-AlgB-offline-GIT-basic OK')
PY
```

校验 info 日志：

```bash
python3 UserExamplesNG/check_info_log.py \
  --logFile /tmp/agg-userexample-ng-algb-offline-git-basic.info.log \
  --mode algorithm-b \
  --scope A \
  --label example-AlgB-offline-GIT-basic
```

## `example-AlgB-offline-SVN-basic`

你已经具备：

- 一个 SVN 来源的 `commitDiffSet/`
- 匹配的 v26.03 `genCodeDescSet/`
- 运行时不需要活跃仓库

校验输入：

```bash
python3 - <<'PY'
from pathlib import Path

base = Path('UserExamplesNG/dataset-AlgB-offline-SVN-basic')
patches = list((base / 'commitDiffSet').glob('*_commitDiff.patch'))
protocols = list((base / 'genCodeDescSet').glob('*_genCodeDesc.json'))

if len(patches) != 5 or len(protocols) != 5:
    raise SystemExit(f'Unexpected input counts: patches={len(patches)} protocols={len(protocols)}')

print('Input OK: offline SVN basic dataset is ready')
PY
```

运行：

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL https://example.local/userexamples/svn-basic \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-userexample-ng-algb-offline-svn-basic.json \
  --genCodeDescSetDir UserExamplesNG/dataset-AlgB-offline-SVN-basic/genCodeDescSet \
  --commitDiffSetDir UserExamplesNG/dataset-AlgB-offline-SVN-basic/commitDiffSet \
  --logLevel info \
  2> /tmp/agg-userexample-ng-algb-offline-svn-basic.info.log
```

校验输出：

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-algb-offline-svn-basic.json').read_text())
expected = json.loads(Path('UserExamplesNG/dataset-AlgB-offline-SVN-basic/expected_result.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgB-offline-SVN-basic mismatch')

print('example-AlgB-offline-SVN-basic OK')
PY
```

校验 info 日志：

```bash
python3 UserExamplesNG/check_info_log.py \
  --logFile /tmp/agg-userexample-ng-algb-offline-svn-basic.info.log \
  --mode algorithm-b \
  --scope A \
  --label example-AlgB-offline-SVN-basic
```

## 数据集：`dataset-localGIT-productionScale`

这个生成器会物化一个用于生产级练习的重型真实 Git 仓库。

### 物化 `dataset-localGIT-productionScale`

```bash
python3 UserExamplesNG/dataset-localGIT-productionScale/generate_example.py \
  --outputDir /tmp/agg-userexample-ng-localgit-heavy \
  --force
```

### 校验 `dataset-localGIT-productionScale` 输入

```bash
python3 - <<'PY'
from pathlib import Path

base = Path('/tmp/agg-userexample-ng-localgit-heavy')
required = [
    base / 'repo',
    base / 'genCodeDescSet',
    base / 'manifest.json',
    base / 'expected_result.json',
]

for path in required:
    if not path.exists():
        raise SystemExit(f'Missing required input: {path}')

print('Input OK: local Git production-scale dataset is ready')
PY
```

### `example-AlgA-localGIT-productionScale`

你已经具备：

- 一个大型本地 Git 仓库
- 与分支密集历史窗口匹配的 v26.03 元数据

运行：

```bash
LOCAL_GIT_HEAVY_REPO="$(python3 - <<'PY'
from pathlib import Path
print(Path('/tmp/agg-userexample-ng-localgit-heavy/repo').resolve())
PY
)"

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL "$LOCAL_GIT_HEAVY_REPO" \
  --repoBranch main \
  --startTime 2026-02-20 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-userexample-ng-alga-localgit-heavy.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localgit-heavy/genCodeDescSet \
  --logLevel info \
  2> /tmp/agg-userexample-ng-alga-localgit-heavy.info.log
```

校验输出：

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-alga-localgit-heavy.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localgit-heavy/expected_result.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgA-localGIT-productionScale mismatch')

print('example-AlgA-localGIT-productionScale OK')
PY
```

校验 info 日志：

```bash
python3 UserExamplesNG/check_info_log.py \
  --logFile /tmp/agg-userexample-ng-alga-localgit-heavy.info.log \
  --mode live \
  --scope A \
  --label example-AlgA-localGIT-productionScale
```

## 相关文档

- `README_UserGuideNG_ZH.md`
- `README_UserGuide_ZH.md`
- `README_UserStoryNG_ZH.md`
