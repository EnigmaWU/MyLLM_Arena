# PPT2PDF —— PPT文件转PDF文件

## 关于（About）
- PPT2PDF 是一个用于 **PPT文件转PDF文件** 的工具，帮助用户将PPT文件转换为PDF文件。
- 支持多种PPT文件格式（.ppt, .pptx）
- 支持每页独立PDF文件输出或合并为一个PDF文件输出

## 依赖（Dependencies）
- 所需依赖包详见 requirements.txt 文件
- 安装（Installation）
```shell
$ pip3 install -r requirements.txt
```

## 用法（Usage）
```shell
$ python3 MyPPT2PDF.py --PPT {/PATH/2/PptFilename.pptx} --Output {/PATH/2/PdfFilename.pdf} {--Split} {--Help} {--Version} {--Debug}
```
- 其中：
  - --PPT: 输入PPT文件的路径
  - --Output: 输出PDF文件的路径
  - --Split: 是否将每页独立输出为PDF文件，默认为False
    - True: 每页独立输出为PDF文件，输出文件名为 PdfFilename_{页码}.pdf 
  - --Help: 查看帮助信息
  - --Version: 查看版本信息
  - --Debug: 查看调试信息

- 例如：
```shell
$ python3 MyPPT2PDF.py --PPT ./Doc/DemoPPT.pptx --Output ./Doc/DemoOut.pdf --Split
```

## 输出示例（Output Examples）
- 默认模式（合并PDF）:
  - 输出: DemoOut.pdf（包含所有PPT页面）
- 拆分模式（--Split）:
  - 输出: DemoOut_1.pdf, DemoOut_2.pdf, ... 等（每个文件包含一个PPT页面）

## 常见问题（FAQ）
- Q: 转换大型PPT文件时速度慢怎么办？
  - A: 建议关闭Debug模式，转换速度会有所提升

## 版本信息（Version）
- 当前版本: 1.0.0
