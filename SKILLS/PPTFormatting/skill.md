| name        | ppt_formatting                                                                                  |
| ----------- | ----------------------------------------------------------------------------------------------- |
| description | 读取 PPTAnalyst 输出的分析大纲，进行排版渲染与强制溯源，生成格式美观的最终分析报告。支持多种输出格式（Markdown/表格/思维导图），为每个结论标注来源。 |

# PPTFormatting Skill (PPT 排版输出技能)

## 核心目标

读取 PPTAnalyst 输出的结构化分析大纲，进行专业级排版渲染，生成格式美观、溯源清晰的最终分析报告。**必须**为每个关键结论标注数据来源（如页码、图表或备注），确保报告的可信度和可追溯性。

## 触发时机

- PPTAnalyst 完成内容分析后，用户确认大纲无误时。
- 用户要求"生成报告"、"排版输出"、"格式化结果"。
- 用户询问"生成最终分析报告"、"输出 Markdown 文档"。
- 需要将分析结果转换为可分享、可展示的格式时。

## 工具调用方式

- 脚本路径：`SKILLS/PPTFormatting/scripts/ppt_formatting.py`
- 调用命令：
  ```bash
  python SKILLS/PPTFormatting/scripts/ppt_formatting.py <outline.json> [output_report.md] [--format markdown|html]
  ```

### Python 调用

```python
import sys
sys.path.insert(0, "SKILLS/PPTFormatting/scripts")
from ppt_formatting import format_report, to_markdown, to_html

# 基本调用（接收 PPTAnalyst 的输出）
result = format_report(analysis_data)

# 输出 Markdown
md_content = to_markdown(result)

# 输出 HTML
html_content = to_html(result)

# 保存到文件
format_report(analysis_data, output_path="report.md", format_type="markdown")
```

### 输入格式

输入为 PPTAnalyst 的输出 JSON，结构如下：

```json
{
  "presentation_overview": {...},
  "outline": {...},
  "insights": {...},
  "metadata": {...}
}
```

## 脚本输出格式解析

脚本将生成格式化的报告文件，包含以下关键部分：

### Markdown 输出结构

```markdown
# {演示文稿标题}

## 概览
- 总页数：{slide_count}
- 核心主题：{main_topic}
- 关键主题：{key_themes}

## 分析大纲

### {章节标题}
- **{要点内容}** (Source: Slide {页码})
  - 支撑数据：{supporting_data}
  - 置信度：{confidence}

## 洞察分析

### 内容亮点
- {strengths}

### 信息缺口
- {gaps}

### 改进建议
- {recommendations}

---
*报告生成时间：{timestamp}*
*本报告基于 PPTParser 和 PPTAnalyst 自动生成*
```

## Agent 行为约束

1. **必须**为每个关键结论标注 `(Source: Slide X)` 来源标签。
2. 发现 `confidence` 为 `low` 的要点时，必须在报告中标注 `[待确认]`。
3. 发现 `gaps` 不为空时，必须在报告中明确列出信息缺口。
4. **必须**在报告末尾添加生成时间和来源说明。
5. **严禁**在排版过程中修改原始分析内容，只能调整格式和添加溯源标签。
6. **严禁**凭空添加结论或填补缺失信息。

## 使用示例

### 调用示例（PowerShell）

```powershell
# 先调用 PPTParser
python SKILLS/PPTParser/scripts/ppt_parser.py "demo.pptx" "parsed.json"

# 再调用 PPTAnalyst
python SKILLS/PPTAnalyst/scripts/ppt_analyst.py "parsed.json" "outline.json"

# 最后调用 PPTFormatting
python SKILLS/PPTFormatting/scripts/ppt_formatting.py "outline.json" "report.md" --format markdown
```

### 输出示例

```markdown
# 2024年度产品战略规划

## 概览
- 总页数：8
- 核心主题：产品发展战略与执行计划
- 关键主题：市场分析、业绩回顾、战略目标、行动计划、资源预算

## 分析大纲

### 市场环境与业绩回顾
- **AI技术快速渗透，智能化需求增长35%** (Source: Slide 3)
  - 支撑数据：Slide 3 行业趋势分析
  - 置信度：高

- **2023年营收超额完成104%** (Source: Slide 4)
  - 支撑数据：Slide 4 业绩表格 (5行x4列)
  - 置信度：高

## 洞察分析

### 内容亮点
- 包含结构化表格数据，便于数据分析
- 包含可视化图表，直观展示数据趋势

### 信息缺口
- 用户增长未达预期，原因未说明

### 改进建议
- 补充用户增长策略分析

---
*报告生成时间：2024-01-15T10:35:00*
*本报告基于 PPTParser 和 PPTAnalyst 自动生成*
```

## 工作流整合

### 1. 上游依赖：PPTAnalyst

本技能**必须**在 PPTAnalyst 完成后调用。PPTAnalyst 的输出是本技能的唯一输入。

```
PPTParser（解包） → PPTAnalyst（分析） → PPTFormatting（排版）
```

### 2. 输出交付

本技能的输出是最终交付物，将呈现给用户。因此输出必须：
- 格式美观，易于阅读
- 溯源清晰，每个结论可追溯
- 结构完整，包含所有分析要素
- 支持多种格式（Markdown/HTML）

### 3. Human-in-the-loop

在以下时机可能需要返回上游：
- 用户对报告格式不满意时
- 用户要求调整大纲结构时
- 用户发现内容错误需要重新分析时

## 注意事项

1. 本技能依赖 PPTAnalyst 的输出，不能直接处理 `.pptx` 文件或 PPTParser 的输出
2. 默认输出 Markdown 格式，可通过 `--format` 参数指定 HTML 格式
3. 报告中的来源标注基于 PPTParser 提取的页码信息
4. 对于 `confidence` 为 `low` 的内容，会在报告中标注 `[待确认]`
5. 生成的报告文件支持直接在 GitHub、Notion 等平台渲染
