# 关于（About）
- InspirationLineage 是一个关于【灵感追溯】的工具。
- 输入：Paper（PDF or URL）+ ConceptName
- 输出：ConceptName 的灵感追溯图谱
- 例如：
  - 输入：Paper: https://arxiv.org/abs/2501.12948, ConceptName: Reasoning
  - 输出：Reasoning 这个概念的来源、相关的示例，这个概念的演变过程等。

# 用法（Usage）
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

