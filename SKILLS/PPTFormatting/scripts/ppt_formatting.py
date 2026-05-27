"""
PPTFormatting - PPT 排版输出组件

读取 PPTAnalyst 输出的分析大纲，进行排版渲染与强制溯源，
生成格式美观的最终分析报告。
"""

import json
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class KeyPoint:
    point: str = ""
    supporting_data: str = ""
    source_slide: int = 0
    confidence: str = "high"


@dataclass
class Section:
    section_id: int = 0
    title: str = ""
    key_points: list[KeyPoint] = field(default_factory=list)
    sub_sections: list["Section"] = field(default_factory=list)


@dataclass
class PresentationOverview:
    title: str = ""
    total_slides: int = 0
    main_topic: str = ""
    key_themes: list[str] = field(default_factory=list)


@dataclass
class Insights:
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class ReportData:
    overview: PresentationOverview = field(default_factory=PresentationOverview)
    sections: list[Section] = field(default_factory=list)
    insights: Insights = field(default_factory=Insights)
    timestamp: str = ""
    warnings: list[str] = field(default_factory=list)


class PPTFormattingError(Exception):
    pass


def validate_input(data: dict[str, Any]) -> None:
    if not data:
        raise PPTFormattingError("输入数据为空")
    if "presentation_overview" not in data:
        raise PPTFormattingError("输入数据缺少 presentation_overview 字段")
    if "outline" not in data:
        raise PPTFormattingError("输入数据缺少 outline 字段")


def parse_key_point(point_data: dict[str, Any]) -> KeyPoint:
    return KeyPoint(
        point=point_data.get("point", ""),
        supporting_data=point_data.get("supporting_data", ""),
        source_slide=point_data.get("source_slide", 0),
        confidence=point_data.get("confidence", "high")
    )


def parse_section(section_data: dict[str, Any]) -> Section:
    section = Section(
        section_id=section_data.get("section_id", 0),
        title=section_data.get("title", "")
    )

    for point_data in section_data.get("key_points", []):
        section.key_points.append(parse_key_point(point_data))

    for sub_data in section_data.get("sub_sections", []):
        section.sub_sections.append(parse_section(sub_data))

    return section


def parse_input(data: dict[str, Any]) -> ReportData:
    overview_data = data.get("presentation_overview", {})
    overview = PresentationOverview(
        title=overview_data.get("title", "未知"),
        total_slides=overview_data.get("total_slides", 0),
        main_topic=overview_data.get("main_topic", "未知"),
        key_themes=overview_data.get("key_themes", [])
    )

    sections: list[Section] = []
    outline_data = data.get("outline", {})
    for section_data in outline_data.get("sections", []):
        sections.append(parse_section(section_data))

    insights_data = data.get("insights", {})
    insights = Insights(
        strengths=insights_data.get("strengths", []),
        gaps=insights_data.get("gaps", []),
        recommendations=insights_data.get("recommendations", [])
    )

    metadata = data.get("metadata", {})
    timestamp = metadata.get("analysis_timestamp", datetime.now().isoformat())

    warnings = data.get("warnings", [])

    return ReportData(
        overview=overview,
        sections=sections,
        insights=insights,
        timestamp=timestamp,
        warnings=warnings
    )


def get_confidence_label(confidence: str) -> str:
    labels = {
        "high": "高",
        "medium": "中",
        "low": "低 [待确认]"
    }
    return labels.get(confidence, confidence)


def format_markdown_key_point(point: KeyPoint) -> str:
    lines: list[str] = []

    confidence_label = get_confidence_label(point.confidence)
    source_label = f"(Source: Slide {point.source_slide})" if point.source_slide else ""

    lines.append(f"- **{point.point}** {source_label}")

    if point.supporting_data:
        lines.append(f"  - 支撑数据：{point.supporting_data}")

    lines.append(f"  - 置信度：{confidence_label}")

    return "\n".join(lines)


def format_markdown_section(section: Section) -> str:
    lines: list[str] = []

    lines.append(f"### {section.title}")
    lines.append("")

    for point in section.key_points:
        lines.append(format_markdown_key_point(point))
        lines.append("")

    for sub_section in section.sub_sections:
        lines.append(format_markdown_section(sub_section))

    return "\n".join(lines)


def format_markdown(report: ReportData) -> str:
    lines: list[str] = []

    lines.append(f"# {report.overview.title}")
    lines.append("")
    lines.append("## 概览")
    lines.append("")
    lines.append(f"- 总页数：{report.overview.total_slides}")
    lines.append(f"- 核心主题：{report.overview.main_topic}")

    if report.overview.key_themes:
        themes_str = "、".join(report.overview.key_themes[:5])
        if len(report.overview.key_themes) > 5:
            themes_str += "..."
        lines.append(f"- 关键主题：{themes_str}")

    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 分析大纲")
    lines.append("")

    for section in report.sections:
        lines.append(format_markdown_section(section))

    lines.append("---")
    lines.append("")

    lines.append("## 洞察分析")
    lines.append("")

    if report.insights.strengths:
        lines.append("### 内容亮点")
        lines.append("")
        for strength in report.insights.strengths:
            lines.append(f"- {strength}")
        lines.append("")

    if report.insights.gaps:
        lines.append("### 信息缺口")
        lines.append("")
        for gap in report.insights.gaps:
            lines.append(f"- {gap}")
        lines.append("")

    if report.insights.recommendations:
        lines.append("### 改进建议")
        lines.append("")
        for rec in report.insights.recommendations:
            lines.append(f"- {rec}")
        lines.append("")

    if report.warnings:
        lines.append("### 警告信息")
        lines.append("")
        for warning in report.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*报告生成时间：{report.timestamp}*")
    lines.append("*本报告基于 PPTParser 和 PPTAnalyst 自动生成*")

    return "\n".join(lines)


def format_html_key_point(point: KeyPoint) -> str:
    confidence_label = get_confidence_label(point.confidence)
    source_label = f'<span class="source">(Source: Slide {point.source_slide})</span>' if point.source_slide else ""
    confidence_class = f"confidence-{point.confidence}"

    html = f"""
    <div class="key-point">
        <div class="point-header">
            <strong>{point.point}</strong> {source_label}
            <span class="{confidence_class}">{confidence_label}</span>
        </div>
    """
    if point.supporting_data:
        html += f'<div class="supporting-data">支撑数据：{point.supporting_data}</div>'

    html += "</div>"
    return html


def format_html_section(section: Section) -> str:
    html = f'<div class="section"><h3>{section.title}</h3>'

    for point in section.key_points:
        html += format_html_key_point(point)

    for sub_section in section.sub_sections:
        html += format_html_section(sub_section)

    html += "</div>"
    return html


def format_html(report: ReportData) -> str:
    themes_str = "、".join(report.overview.key_themes[:5])
    if len(report.overview.key_themes) > 5:
        themes_str += "..."

    sections_html = ""
    for section in report.sections:
        sections_html += format_html_section(section)

    strengths_html = ""
    if report.insights.strengths:
        strengths_html = "<h3>内容亮点</h3><ul>"
        for s in report.insights.strengths:
            strengths_html += f"<li>{s}</li>"
        strengths_html += "</ul>"

    gaps_html = ""
    if report.insights.gaps:
        gaps_html = "<h3>信息缺口</h3><ul>"
        for g in report.insights.gaps:
            gaps_html += f"<li>{g}</li>"
        gaps_html += "</ul>"

    recommendations_html = ""
    if report.insights.recommendations:
        recommendations_html = "<h3>改进建议</h3><ul>"
        for r in report.insights.recommendations:
            recommendations_html += f"<li>{r}</li>"
        recommendations_html += "</ul>"

    warnings_html = ""
    if report.warnings:
        warnings_html = '<div class="warnings"><h3>警告信息</h3><ul>'
        for w in report.warnings:
            warnings_html += f"<li>{w}</li>"
        warnings_html += "</ul></div>"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report.overview.title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .overview {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .overview ul {{ list-style: none; padding: 0; }}
        .overview li {{ padding: 5px 0; }}
        .section {{ margin: 20px 0; padding: 15px; background: #fff; border-left: 4px solid #3498db; }}
        .key-point {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 3px; }}
        .point-header {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
        .source {{ color: #7f8c8d; font-size: 0.9em; }}
        .confidence-high {{ color: #27ae60; font-size: 0.8em; padding: 2px 6px; background: #e8f5e9; border-radius: 3px; }}
        .confidence-medium {{ color: #f39c12; font-size: 0.8em; padding: 2px 6px; background: #fff3e0; border-radius: 3px; }}
        .confidence-low {{ color: #e74c3c; font-size: 0.8em; padding: 2px 6px; background: #fce4ec; border-radius: 3px; }}
        .supporting-data {{ color: #666; font-size: 0.9em; margin-top: 5px; }}
        .insights {{ margin: 20px 0; }}
        .insights ul {{ padding-left: 20px; }}
        .insights li {{ margin: 5px 0; }}
        .warnings {{ background: #fff3e0; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>{report.overview.title}</h1>

    <div class="overview">
        <h2>概览</h2>
        <ul>
            <li><strong>总页数：</strong>{report.overview.total_slides}</li>
            <li><strong>核心主题：</strong>{report.overview.main_topic}</li>
            <li><strong>关键主题：</strong>{themes_str}</li>
        </ul>
    </div>

    <h2>分析大纲</h2>
    {sections_html}

    <div class="insights">
        <h2>洞察分析</h2>
        {strengths_html}
        {gaps_html}
        {recommendations_html}
    </div>

    {warnings_html}

    <div class="footer">
        <p><em>报告生成时间：{report.timestamp}</em></p>
        <p><em>本报告基于 PPTParser 和 PPTAnalyst 自动生成</em></p>
    </div>
</body>
</html>"""

    return html


def format_report(data: dict[str, Any], output_path: str | Path | None = None, format_type: str = "markdown") -> str:
    validate_input(data)

    report = parse_input(data)

    if format_type == "html":
        content = format_html(report)
    else:
        content = format_markdown(report)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')

    return content


def format_from_file(input_path: str | Path, output_path: str | Path | None = None, format_type: str = "markdown") -> str:
    input_path = Path(input_path)

    if not input_path.exists():
        raise PPTFormattingError(f"输入文件不存在: {input_path}")

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise PPTFormattingError(f"JSON 解析失败: {e}")

    return format_report(data, output_path, format_type)


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="PPT 排版输出工具")
    parser.add_argument("input", help="PPTAnalyst 输出的 JSON 文件路径")
    parser.add_argument("output", nargs="?", help="输出文件路径")
    parser.add_argument("--format", choices=["markdown", "html"], default="markdown", help="输出格式")

    args = parser.parse_args()

    try:
        content = format_from_file(args.input, args.output, args.format)
        if not args.output:
            print(content)
    except PPTFormattingError as e:
        print(json.dumps({"status": "error", "reason": str(e)}))
        sys.exit(1)
