# PPT Deep Summary

**PPT Deep Summary** 是一个面向学习、工作、科研等场合的 AI 助手，支持 `.pptx` 文件的深度解析、归纳分析和报告生成。系统通过 AI Agent 调度三阶段流水线 Skill，实现从 PPT 到结构化分析报告的自动化处理。

本项目不提供 API，请自行部署。国内环境推荐 Trae CN、Qwen Code 等。

## 目录结构

```
ppt-deep-summary/
├─ SKILLS/
│  ├─ PPTParser/            # Skill 1: PPT 深度解析
│  │  ├─ scripts/ppt_parser.py
│  │  └─ tests/
│  ├─ PPTAnalyst/           # Skill 2: 内容分析
│  │  ├─ scripts/ppt_analyst.py
│  │  └─ tests/
│  └─ PPTFormatting/        # Skill 3: 排版输出
│     └─ scripts/ppt_formatting.py
├─ install.bat              # 一键安装依赖
├─ test.pptx                # 测试用 PPT 文件
├─ agent.md                 # AI Agent 工作流定义
└─ README.md
```

## 部署指南

### 1. 安装 Python

确保系统已安装 Python 3.10+，并加入环境变量。

### 2. 安装依赖

将 `install.bat` 放在项目根目录，双击执行：

```
install.bat
```

- 使用阿里云 PyPI 镜像加速安装
- 默认安装 `python-pptx` 等解析库

### 3. 初始化工作区

AI Agent 在执行任务前，会自动在项目根目录创建 `WorkSpace/` 工作区，用于存放中间文件和最终报告：

```
WorkSpace/
├─ parsed.json       # PPTParser 解析输出
├─ parsed.md         # PPTParser Markdown 输出
├─ outline.json      # PPTAnalyst 分析输出（可人工审阅修改）
├─ report.md         # PPTFormatting Markdown 报告
└─ report.html       # PPTFormatting HTML 报告
```

## 使用指南

### 1. 提供 PPT 文件

将待分析的 `.pptx` 文件放在任意文件夹中。在任务开始时，Agent 会将文件移动到工作区统一管理。

### 2. 三阶段流水线

**操作流程**：

1. AI Agent 获取用户意图（如"帮我分析这个 PPT 的要点"）

2. **PPTParser**：解压 `.pptx`，提取文本、表格、图片、超链接、备注、图表，输出 `parsed.json` + `parsed.md`

3. **PPTAnalyst**：读取 `parsed.json`，归纳核心观点，构建章节大纲，输出 `outline.json`

4. **PPTFormatting**：读取 `outline.json`，渲染为格式美观的报告，输出 `report.md` / `report.html`

### 3. Human-in-the-loop

PPTAnalyst 生成 `outline.json` 后，用户可审阅并修改分析大纲，再交给 PPTFormatting 生成最终报告。确保报告内容符合预期。

### 4. 注意事项

- 所有操作均在 **WorkSpace/ 工作区内执行**

- 中间文件（`parsed.json`、`outline.json`）仅作中间使用，不覆盖原始 PPT

- 异常处理：

    - 文件不存在 → 提示并停止

    - 解析失败 → 记录在 `warnings` 中，不中断流程

    - 空内容页 → 自动跳过

## 示例

*请注意，对 AI 描述的时候要求需求清晰明了。*

**用户**：帮我分析 `WorkSpace/项目汇报.pptx`，归纳总结要点

**AI Agent**：

1. 获取用户意图：

    - 深度解析 PPT 内容

    - 归纳概括式分析，输出核心要点

2. PPTParser 解析：

    - 解压 `.pptx`，提取 22 页内容

    - 输出 `parsed.json`（0 警告）

3. PPTAnalyst 分析：

    - 构建 7 个章节大纲

    - 归纳核心观点 + 洞察分析

    - 输出 `outline.json`

4. PPTFormatting 生成报告：

    - 输出 `report.md`（Markdown）或 `report.html`（HTML）

    - 每个结论标注 `(Source: Slide X)` 溯源标签

## 支持

- 深度文件解析：文本、表格、图片、超链接、备注、图表
- 归纳式分析：多条文本合并为摘要，避免逐条列举
- 强制溯源：每个结论标注来源页码，确保可信度
- Markdown / HTML 两种输出格式
- 阿里云 PyPI 镜像加速安装依赖

## 许可证

MIT License
