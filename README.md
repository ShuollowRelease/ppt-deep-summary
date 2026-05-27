# PPT Deep Summary

基于多智能体协同架构的 PPT 深度解析与总结归纳系统。

## 项目简介

PPT Deep Summary 是一个专业的 PPT 分析工具，通过底层解包、内容分析、排版输出三个阶段，将 `.pptx` 文件转换为结构化的分析报告。

### 核心优势

- **深度文件解析**：内置 Open XML 预处理管道，完整提取文本、表格、图片、超链接、备注等结构化数据
- **多智能体协同**：采用流水线式分工协作，避免单一模型注意力分散问题
- **强制溯源机制**：为每个关键结论标注来源页码，确保报告可信度
- **支持多种输出**：Markdown、HTML 两种格式可选

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      用户上传 PPT                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: PPTParser (深度解析)                              │
│  - 解压 .pptx 文件                                          │
│  - 提取文本、表格、图片、超链接、备注、图表                    │
│  - 输出标准化 JSON/Markdown                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: PPTAnalyst (内容分析)                             │
│  - 读取结构化数据                                            │
│  - 提炼核心观点，构建分析大纲                                 │
│  - 支持 Human-in-the-loop 人工干预                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: PPTFormatting (排版输出)                          │
│  - 渲染分析大纲                                              │
│  - 添加溯源标签                                              │
│  - 生成最终报告 (Markdown/HTML)                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      交付最终报告                            │
└─────────────────────────────────────────────────────────────┘
```

## 目录结构

```
ppt-deep-summary/
├── README.md
├── test.pptx
├── program-book.docx
└── SKILLS/
    ├── PPTParser/                # Skill 1: PPT 深度解析
    │   ├── skill.md              # 技能定义文档
    │   ├── scripts/
    │   │   └── ppt_parser.py     # 核心代码
    │   └── tests/
    │       └── test_ppt_parser.py
    ├── PPTAnalyst/               # Skill 2: 内容分析
    │   ├── skill.md
    │   ├── scripts/
    │   │   └── ppt_analyst.py
    │   └── tests/
    │       └── test_input.json
    └── PPTFormatting/            # Skill 3: 排版输出
        ├── skill.md
        ├── scripts/
        │   └── ppt_formatting.py
        └── tests/
```

## 技能说明

### PPTParser (深度解析)

深度解析 `.pptx` 文件，提取结构化内容。

| 功能 | 说明 |
|------|------|
| 文本提取 | 标题、正文、项目符号层级 |
| 表格提取 | 完整表格数据 |
| 图片引用 | 文件名、尺寸、类型 |
| 超链接 | 链接文本、URL |
| 备注 | 演讲者备注 |
| 图表 | 图表类型、标题 |
| 布局 | 幻灯片布局信息 |

### PPTAnalyst (内容分析)

读取 PPTParser 的输出，进行深度内容分析与大纲构建。

- 提炼核心观点
- 构建结构化大纲
- 标注数据来源和置信度
- 识别内容亮点与信息缺口
- 支持用户审阅和干预

### PPTFormatting (排版输出)

将分析大纲渲染为格式美观的最终报告。

- 支持 Markdown 和 HTML 两种格式
- 为每个结论添加溯源标签
- 区分置信度（高/中/低）
- 生成可分享的分析报告

## 快速开始

### 环境要求

- Python 3.10+
- python-pptx

### 安装依赖

```bash
pip install python-pptx
```

### 使用方式

#### 命令行

```bash
# Step 1: 解析 PPT
python SKILLS/PPTParser/scripts/ppt_parser.py demo.pptx parsed.json

# Step 2: 分析内容
python SKILLS/PPTAnalyst/scripts/ppt_analyst.py parsed.json outline.json

# Step 3: 生成报告
python SKILLS/PPTFormatting/scripts/ppt_formatting.py outline.json report.md --format markdown
```

#### Python 调用

```python
import sys
sys.path.insert(0, "SKILLS/PPTParser/scripts")
from ppt_parser import parse

# 解析 PPT
result = parse("demo.pptx", json_output="parsed.json")
```

```python
import sys
sys.path.insert(0, "SKILLS/PPTAnalyst/scripts")
from ppt_analyst import analyze_from_file

# 分析内容
result = analyze_from_file("parsed.json", "outline.json")
```

```python
import sys
sys.path.insert(0, "SKILLS/PPTFormatting/scripts")
from ppt_formatting import format_from_file

# 生成报告
content = format_from_file("outline.json", "report.md", format_type="markdown")
```

## 输出示例

### JSON 输出 (PPTParser)

```json
{
  "presentation_title": "2024年度产品战略规划",
  "slide_count": 8,
  "slides": [
    {
      "slide_number": 1,
      "title": "2024年度产品战略规划",
      "layout_name": "Title Slide",
      "texts": [
        {"level": 0, "text": "产品部 · 战略规划组"}
      ],
      "notes": [],
      "tables": [],
      "images": [],
      "hyperlinks": [],
      "charts": []
    }
  ],
  "warnings": []
}
```

### Markdown 报告 (PPTFormatting)

```markdown
# 2024年度产品战略规划

## 概览
- 总页数：8
- 核心主题：产品发展战略与执行计划

## 分析大纲

### 市场环境分析
- **AI技术快速渗透，智能化需求增长35%** (Source: Slide 3)
  - 支撑数据：Slide 3 行业趋势分析
  - 置信度：高

## 洞察分析

### 内容亮点
- 包含结构化表格数据，便于数据分析

### 信息缺口
- 用户增长未达预期，原因未说明
```

## 技术栈

- **文档解析**：python-pptx, zipfile, lxml
- **编程语言**：Python 3.10+
- **数据格式**：JSON, Markdown

## 许可证

MIT License
