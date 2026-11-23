---
name: paper-to-chinese
description: Download an arXiv LaTeX paper, translate it into fluent Simplified Chinese with subagents while keeping the original layout, and compile a Chinese PDF with XeLaTeX. Use when the user asks to translate an arXiv or LaTeX paper into a Chinese PDF (把论文/arXiv 翻成中文 PDF).
---

# 把 LaTeX 论文翻译成中文 PDF

## 1. 获取源码与摸底

- 拿到 arXiv 链接后，提取论文 ID（有版本号则保留），直接下载 `https://arxiv.org/src/<id>`。返回结果可能是 `.tar.gz` 压缩包，也可能是单个 `.tex` 文件，按实际类型解到独立工作目录。
- 找到含 `\documentclass` 的入口 `.tex` 文件，顺着 `\input` / `\include` 列出所有待翻文件。
- 源码包里自带 `.bbl` 时直接保留复用，无需重跑 BibTeX/Biber。
- 如果只有 PDF、拿不到 LaTeX 源码，直接告诉用户本流程依赖源码，无法还原原版式。

## 2. 就绪云电脑 TeX 环境

- 先探测环境：`which xelatex` 和 `fc-list :lang=zh`。
- 系统里有什么中文字体就用什么（Noto CJK、Source Han、Fandol、文泉驿等皆可），不必死磕单一字体。
- 缺引擎或字体时，按最小化原则补齐 XeLaTeX、`xeCJK` 和一款中文字体；精简镜像缺 format 或 `xeCJK` 时见 [references/build.md](references/build.md)。
- 动手翻译前，先在导言区加上 `xeCJK` 和一句中文跑通编译，确认能正常出中文，再开始翻译。

## 3. 拆解与派发子 Agent 翻译

不要让单个上下文硬翻整篇长论文，容易漏段、偷懒或术语打架。

1. **主 Agent 定术语表并落盘**：快速扫一遍 Abstract、各节标题和核心段落，把轻量术语表写入工作目录（如 `glossary.md`，写明核心词译法与保留英文的词）。
2. **按文件切分**：多文件项目直接按现有 `.tex` 文件分派；单文件长论文先按 `\section` 拆成独立片段文件落盘。
3. **并行派发子 Agent，直接读写文件**：每个子 Agent 自己读取 `glossary.md` 和分派到的源码文件，按下方准则翻译后**直接写回磁盘**（多文件项目原地覆盖工作副本，单文件拆分则写到对应输出片段），只向主 Agent 返回简短完成状态或异常提示，不通过消息传回译文全文。
4. **主 Agent 拼装**：子 Agent 全部完成后，如需合并拆分片段，由主 Agent 拼回主文件并检查衔接。若当前助手不支持子 Agent，按同样的文件切分方式分批读写。

## 4. 翻译准则与专有名词

- **母语级学术中文**：目标是让读者能“一目多行”。按中文语序拆解英文长难句，去掉翻译腔（少用“我们提出了一个……”“被……所……”这类直译句式）。
- **专有名词保留**：
  - 模型名、方法名、数据集、评估指标、代码/变量名，以及领域里本来就说英文的词，**直接保留英文，不硬翻**（如 Transformer、Attention、Token、LoRA、Zero-shot、ImageNet、BLEU）。
  - 需要中文译名的核心术语按术语表全文统一，首次出现可括注英文，例如“上下文学习（In-Context Learning）”。
- **只动文本，不动结构**：翻译标题、章节名、正文、表格文字、图注和解释性脚注；保持 TeX 命令、公式、`\label`/`\ref`/`\cite`、参考文献和图片内文字原样。

## 5. 编译、排错与交付

- 在入口文件导言区加入 `xeCJK` 和探测到的中文字体，用 [scripts/compile.py](scripts/compile.py) 或多轮 `xelatex` 编译。
- 常见冲突处理：原模板若带 `pdftex` 专属选项或与 XeLaTeX 冲突的 `fontenc`/`microtype`/字体设置，做最小化调整，保留原 `\documentclass`。
- 编出 PDF 后扫一眼日志（有无缺字形、未定义引用），并把关键页（首页、图表页、公式密集页、双栏边界）转图检查，局部修掉明显爆版或溢出。
- 直接把最终 PDF 文件发给用户。
