| name        | ppt_analyst                                                                                   |
| ----------- | --------------------------------------------------------------------------------------------- |
| description | 读取 PPTParser 输出的结构化数据，进行深度内容分析、语义提炼与大纲构建。支持 Human-in-the-loop 人工干预，输出可供用户审阅的专业级分析大纲。 |

# PPTAnalyst Skill (PPT 内容分析技能)

## 核心目标

读取 PPTParser 输出的干净数据（JSON/Markdown），进行深度内容分析、核心观点提炼和结构化大纲构建，为下游 FormattingExpert 提供完整的分析基础。支持用户审阅和干预，确保分析结果符合用户预期。

## 触发时机

- PPTParser 成功完成解析后，需要进行内容分析时。
- 用户要求"分析这个 PPT"、"提取核心观点"、"生成大纲"。
- 用户询问"PPT 讲了什么"、"主要结论是什么"。
- 需要识别 PPT 中的逻辑结构、论证关系、数据支撑时。

## 工具调用方式

- 脚本路径：`SKILLS/PPTAnalyst/scripts/ppt_analyst.py`
- 调用命令：
  ```bash
  python SKILLS/PPTAnalyst/scripts/ppt_analyst.py <parsed_data.json> [output_outline.json]
  ```

### Python 调用

```python
import sys
sys.path.insert(0, "SKILLS/PPTAnalyst/scripts")
from ppt_analyst import analyze, to_json

# 基本调用（接收 PPTParser 的输出）
result = analyze(parsed_data)

# 输出到文件
result = analyze(parsed_data, output_path="outline.json")

# 获取 JSON 字符串
json_str = to_json(result)
```

### 输入格式

输入为 PPTParser 的输出 JSON，结构如下：

```json
{
  "presentation_title": "string",
  "slide_count": 0,
  "slides": [...]
}
```

## 脚本输出格式解析

脚本将输出 JSON 格式的分析大纲，包含以下关键信息：

- `presentation_overview`：演示文稿概览
  - `title`：标题
  - `total_slides`：总页数
  - `main_topic`：核心主题
  - `key_themes`：关键主题列表
- `outline`：结构化大纲
  - `sections`：章节数组，每项包含：
    - `section_id`：章节编号
    - `title`：章节标题
    - `key_points`：关键要点数组，每项包含：
      - `point`：要点内容
      - `supporting_data`：支撑数据
      - `source_slide`：来源页码
      - `confidence`：置信度（high/medium/low）
    - `sub_sections`：子章节（递归结构）
- `insights`：洞察分析
  - `strengths`：内容亮点
  - `gaps`：信息缺口
  - `recommendations`：改进建议
- `metadata`：元数据
  - `analysis_timestamp`：分析时间戳
  - `requires_user_review`：是否需要用户审阅

## Agent 行为约束

1. 收到 PPTParser 的 JSON 结果后，必须先理解整体结构，再进行逐页分析。
2. 每个关键要点**必须**标注 `source_slide` 来源页码，支持溯源。
3. 对于不确定的推断，必须将 `confidence` 设置为 `low`，并说明原因。
4. 发现 `warnings` 中有解析失败的页面时，需要在分析中标记为"待确认"。
5. 发现内容存在逻辑矛盾或信息缺口时，必须在 `gaps` 中明确指出。
6. **必须**在 `metadata.requires_user_review` 中提示用户审阅，支持 Human-in-the-loop。
7. **严禁**凭空编造内容或填补缺失信息，必须如实反映原始数据。

## 使用示例

### 调用示例（PowerShell）

```powershell
# 先调用 PPTParser
python SKILLS/PPTParser/scripts/ppt_parser.py "demo.pptx" "parsed.json"

# 再调用 PPTAnalyst
python SKILLS/PPTAnalyst/scripts/ppt_analyst.py "parsed.json" "outline.json"
```

### 输出示例

```json
{
  "presentation_overview": {
    "title": "2024年度产品战略规划",
    "total_slides": 8,
    "main_topic": "产品发展战略与执行计划",
    "key_themes": ["市场分析", "业绩回顾", "战略目标", "行动计划", "资源预算"]
  },
  "outline": {
    "sections": [
      {
        "section_id": 1,
        "title": "市场环境与业绩回顾",
        "key_points": [
          {
            "point": "AI技术快速渗透，智能化需求增长35%",
            "supporting_data": "Slide 3 行业趋势分析",
            "source_slide": 3,
            "confidence": "high"
          },
          {
            "point": "2023年营收超额完成104%",
            "supporting_data": "Slide 4 业绩表格",
            "source_slide": 4,
            "confidence": "high"
          }
        ],
        "sub_sections": []
      }
    ]
  },
  "insights": {
    "strengths": ["业绩超额完成", "用户活跃度提升显著"],
    "gaps": ["用户增长未达预期，原因未说明"],
    "recommendations": ["补充用户增长策略分析"]
  },
  "metadata": {
    "analysis_timestamp": "2024-01-15T10:30:00",
    "requires_user_review": true
  }
}
```

## 工作流整合

### 1. 上游依赖：PPTParser

本技能**必须**在 PPTParser 完成后调用。PPTParser 的输出是本技能的唯一输入。

```
PPTParser（解包） → PPTAnalyst（分析） → FormattingExpert（排版）
```

### 2. 下游协作：FormattingExpert

本技能的输出将传递给 FormattingExpert 进行排版渲染和最终报告生成。因此输出必须：
- 结构清晰，便于格式化
- 来源明确，支持溯源标注
- 层级完整，支持大纲扩写

### 3. Human-in-the-loop

在以下时机触发用户审阅：
- 大纲初稿生成后（`requires_user_review: true`）
- 发现重大信息缺口时（`gaps` 不为空）
- 用户主动请求审阅时

## 注意事项

1. 本技能依赖 PPTParser 的输出，不能直接处理 `.pptx` 文件
2. 分析结果基于文本内容，无法分析图片、视频等多媒体的实际含义
3. 对于复杂图表，仅能分析其标题和类型，无法解读具体数据
4. 建议在生成最终报告前，让用户审阅大纲并提供反馈
5. 输出结果为 JSON 格式，便于 Agent 解析和下游处理
