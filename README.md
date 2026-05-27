# PPT Deep Summary

基于多智能体协同架构的 PPT 深度解析与总结归纳系统。

## 项目简介

PPT Deep Summary 将 `.pptx` 文件通过三阶段流水线（PPTParser → PPTAnalyst → PPTFormatting）转换为结构化 Markdown/HTML 报告。

### 核心特性

- **深度文件解析**：提取文本、表格、图片、超链接、备注、图表等结构化数据
- **归纳式分析**：多条文本合并为摘要，避免逐条列举，输出概括性结论
- **强制溯源**：每个结论标注 `(Source: Slide X)`，确保报告可信度
- **Human-in-the-loop**：PPTAnalyst 支持用户审阅干预分析大纲

## 架构

```
┌─────────────────────────────────────────────────┐
│               用户上传 PPT                       │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Phase 1: PPTParser (深度解析)                   │
│  输入: *.pptx    输出: parsed.json + parsed.md   │
│  解压 Open XML，提取文本/表格/图片/备注/图表      │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Phase 2: PPTAnalyst (归纳分析)                  │
│  输入: parsed.json   输出: outline.json          │
│  归纳核心观点 → 构建章节大纲 → 洞察分析          │
│  Human-in-the-loop: 用户可审阅修改 outline.json  │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Phase 3: PPTFormatting (排版输出)               │
│  输入: outline.json  输出: report.md / report.html│
│  Markdown / HTML 两种格式，置信度 + 溯源标注     │
└──────────────────────┬──────────────────────────┘
                       ▼
                  最终分析报告
```

## 目录结构

```
ppt-deep-summary/
├── README.md
├── LICENSE
├── test.pptx
└── SKILLS/
    ├── PPTParser/            # Skill 1: PPT 深度解析
    │   ├── skill.md
    │   ├── scripts/
    │   │   └── ppt_parser.py
    │   └── tests/
    │       └── test_ppt_parser.py
    ├── PPTAnalyst/           # Skill 2: 内容分析
    │   ├── skill.md
    │   ├── scripts/
    │   │   └── ppt_analyst.py
    │   └── tests/
    │       └── test_input.json
    └── PPTFormatting/        # Skill 3: 排版输出
        ├── skill.md
        └── scripts/
            └── ppt_formatting.py
```

## 快速开始

### 环境要求

- Python 3.10+
- python-pptx

```bash
pip install python-pptx
```

### 命令行使用

```bash
# Step 1: 解析 PPT → parsed.json + parsed.md
python SKILLS/PPTParser/scripts/ppt_parser.py demo.pptx parsed.json parsed.md

# Step 2: 分析内容 → outline.json
python SKILLS/PPTAnalyst/scripts/ppt_analyst.py parsed.json outline.json

# Step 3: 生成报告
python SKILLS/PPTFormatting/scripts/ppt_formatting.py outline.json report.md          # Markdown
python SKILLS/PPTFormatting/scripts/ppt_formatting.py outline.json report.html --format html  # HTML
```

### Python API

```python
from ppt_parser import parse
parse("demo.pptx", json_output="parsed.json", md_output="parsed.md")
```

```python
from ppt_analyst import analyze_from_file
analyze_from_file("parsed.json", "outline.json")
```

```python
from ppt_formatting import format_from_file
format_from_file("outline.json", "report.md")
format_from_file("outline.json", "report.html", format_type="html")
```

## 输出示例

### parsed.json (PPTParser)

```json
{
  "presentation_title": "2024年度产品战略规划",
  "slide_count": 8,
  "slides": [
    {
      "slide_number": 1,
      "title": "2024年度产品战略规划",
      "layout_name": "Title Slide",
      "texts": [{"level": 0, "text": "产品部 · 战略规划组"}],
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

### outline.json (PPTAnalyst)

```json
{
  "presentation_overview": {
    "title": "2024年度产品战略规划",
    "total_slides": 8,
    "main_topic": "产品发展战略与执行计划",
    "key_themes": ["市场分析", "技术路线", "执行计划"]
  },
  "outline": {
    "sections": [
      {
        "section_id": 1,
        "title": "市场环境分析",
        "key_points": [
          {
            "point": "AI技术快速渗透，智能化需求增长35%",
            "supporting_data": "Slide 3 行业趋势分析",
            "source_slide": 3,
            "confidence": "high"
          }
        ]
      }
    ]
  },
  "insights": {
    "strengths": ["包含结构化表格数据"],
    "gaps": ["缺少用户增长量化指标"],
    "recommendations": ["建议补充实验对比数据"]
  },
  "metadata": {
    "analysis_timestamp": "2026-05-27T23:00:00",
    "requires_user_review": true
  }
}
```

### report.md (PPTFormatting)

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

- **语言**：Python 3.10+
- **依赖**：python-pptx, zipfile, lxml
- **数据格式**：JSON（中间数据）、Markdown / HTML（最终报告）

## 许可证

MIT License
