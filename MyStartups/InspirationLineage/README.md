# InspirationLineage - 灵感追溯工具

## 关于（About）
InspirationLineage 是一个用于 **灵感概念追溯** 的工具，帮助研究者和学习者探索学术概念的起源和演变。

### 核心功能
- 分析学术论文中的概念来源和发展历程
- 生成概念的灵感追溯图谱
- 支持多层次深度的概念溯源分析

### 工作原理
- 输入：学术论文(PDF或URL) + 概念名称
- 输出：该概念的灵感追溯图谱，包含概念来源、演变过程和相关示例

### 示例场景
- 输入：Paper: https://arxiv.org/abs/2501.12948, ConceptName: Reasoning
- 输出：Reasoning 这个概念的来源、相关的示例，这个概念的演变过程等。

## 安装（Installation）
- TODO

## 用法（Usage）
```shell
$ pip3 install -r requirements.txt
$ python3 MyInspirationLineage.py {--URL {https://arxiv.org/...} or --PDF {/PATH/2/Paper.pdf}} {--ConceptName {NameOfConcept}} {--Depth N<dft=1>}
```
- 其中：
  - --URL: 输入论文的 URL
  - --PDF: 输入论文的 PDF 路径
  - --ConceptName: 输入概念名称
  - --Depth: 概念追溯的深度，默认为 1
  - --Help: 查看帮助信息
  - --Version: 查看版本信息
  - --Debug: 查看调试信息
- 例如：
```shell
$ python3 MyInspirationLineage.py --URL https://arxiv.org/abs/2501.12948 --ConceptName Reasoning --Depth 2
```

