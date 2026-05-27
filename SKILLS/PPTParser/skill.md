| name        | ppt_parser                                                                                      |
| ----------- | ----------------------------------------------------------------------------------------------- |
| description | 深度解析 .pptx 文件，提取结构化内容（标题、文本、表格、图片、超链接、备注、图表），输出标准化 JSON/Markdown 中间数据。在进行内容分析、大纲构建或生成报告之前必须调用，以防止盲目处理导致错误。 |

# PPTParser Skill (PPT 深度解析技能)

## 核心目标

在进行内容分析（PPTAnalyst）、大纲构建或生成最终报告之前，**必须**先调用此技能对 PPTX 文件进行底层解包和结构化提取，以确保下游 AI 获得干净、稳定的输入数据。

## 触发时机

- 用户上传了新的 `.pptx` 文件并要求分析或总结。
- 用户询问"这个 PPT 里有什么内容"、"PPT 结构是什么"。
- 在调用 `PPTAnalyst` 之前必须执行。
- 需要提取 PPT 中的表格、图片、超链接等结构化数据时。

## 工具调用方式

- 脚本路径：`SKILLS/PPTParser/scripts/ppt_parser.py`
- 调用命令：
  ```bash
  python SKILLS/PPTParser/scripts/ppt_parser.py <pptx文件路径> [输出JSON路径] [输出Markdown路径]
  ```

### Python 调用

```python
import sys
sys.path.insert(0, "SKILLS/PPTParser/scripts")
from ppt_parser import parse, to_json, to_markdown

# 基本调用
result = parse("demo.pptx")

# 输出到文件
result = parse("demo.pptx", json_output="output.json", md_output="output.md")

# 获取 JSON 字符串
json_str = to_json(result)

# 获取 Markdown 字符串
md_str = to_markdown(result)
```

## 脚本输出格式解析

脚本将输出 JSON 格式的字符串，包含以下关键信息：

- `presentation_title`：演示文稿标题（取自文件名）
- `slide_count`：幻灯片总数
- `slides`：幻灯片数组，每个元素包含：
  - `slide_number`：页码
  - `title`：页面标题
  - `layout_name`：布局类型（如 Title Slide、Title and Content）
  - `texts`：文本内容数组，每项包含：
    - `level`：项目符号层级（0=一级，1=二级...）
    - `text`：文本内容
  - `notes`：演讲备注数组
  - `tables`：表格数组，每项包含：
    - `rows`：二维数组（行×列）
    - `row_count`：行数
    - `col_count`：列数
  - `images`：图片数组，每项包含：
    - `filename`：文件名
    - `content_type`：MIME 类型
    - `width`/`height`：尺寸（英寸）
  - `hyperlinks`：超链接数组，每项包含：
    - `text`：链接文本
    - `url`：链接地址
  - `charts`：图表数组，每项包含：
    - `chart_type`：图表类型
    - `title`：图表标题
  - `raw_markdown`：该页的 Markdown 格式内容
- `warnings`：警告信息数组（解析失败时）

## Agent 行为约束

1. 收到本技能的 JSON 结果后，需要在心里构建该 PPT 的物理结构和内容框架。
2. 发现 `warnings` 不为空时，需要向用户说明哪些页面解析失败，并在后续分析中标记这些内容为"待确认"。
3. 发现 `notes` 不为空时，这些是演讲者的补充说明，通常包含重要上下文信息，需要纳入分析。
4. 发现 `tables` 不为空时，这些是结构化数据，需要特别关注其数值和对比关系。
5. 发现 `hyperlinks` 不为空时，这些是外部引用来源，可能需要在报告中标注。
6. **严禁**对提取的内容进行总结或改写，必须保持高保真传递给下游。

## 使用示例

### 调用示例（PowerShell）

```powershell
python SKILLS/PPTParser/scripts/ppt_parser.py "D:\Projects\demo.pptx" "output.json" "output.md"
```

### 输出示例

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
        {"level": 0, "text": "产品部 · 战略规划组"},
        {"level": 0, "text": "2024年1月"}
      ],
      "notes": ["本次汇报重点展示2024年产品发展方向"],
      "tables": [],
      "images": [],
      "hyperlinks": [],
      "charts": [],
      "raw_markdown": "# Slide 1\n\n## 2024年度产品战略规划\n\n产品部 · 战略规划组\n"
    }
  ],
  "warnings": []
}
```

## 工作流整合

### 1. 与 PPTAnalyst 的协作

在调用 `PPTAnalyst` 之前，**必须**先调用 `PPTParser` 获取结构化数据。PPTParser 的输出将作为 PPTAnalyst 的输入。

```
用户上传 PPT → PPTParser（解包） → PPTAnalyst（分析） → FormattingExpert（排版）
```

### 2. 直接数据查询

当用户询问 PPT 结构、内容概览时，直接调用 `PPTParser` 并将 JSON 结果翻译成通俗易懂的语言。

### 3. 数据导出

当用户需要 PPT 的结构化数据（如提取所有表格、汇总所有备注）时，调用 `PPTParser` 并处理输出的 JSON。

## 注意事项

1. 本技能仅支持 `.pptx` 文件（不支持旧版 `.ppt`）
2. 图片和图表仅提取引用信息，不提取实际图像数据
3. 复杂动画和过渡效果不在解析范围内
4. 嵌入的 OLE 对象（如嵌入的 Excel）可能无法完整解析
5. 输出结果为 JSON 格式，便于 Agent 解析和处理
6. 如果解析过程中出现错误，会在 `warnings` 数组中记录，不会中断整个流程
