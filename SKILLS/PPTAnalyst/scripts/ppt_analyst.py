"""
PPTAnalyst - PPT 内容分析组件

读取 PPTParser 输出的结构化数据，进行深度内容分析、语义提炼与大纲构建，
输出可供用户审阅和干预的专业级分析大纲。
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
class AnalysisMetadata:
    analysis_timestamp: str = ""
    requires_user_review: bool = True


@dataclass
class AnalysisResult:
    presentation_overview: PresentationOverview = field(default_factory=PresentationOverview)
    outline: list[Section] = field(default_factory=list)
    insights: Insights = field(default_factory=Insights)
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)
    warnings: list[str] = field(default_factory=list)


class PPTAnalystError(Exception):
    pass


def validate_input(data: dict[str, Any]) -> None:
    if not data:
        raise PPTAnalystError("输入数据为空")
    if "slides" not in data:
        raise PPTAnalystError("输入数据缺少 slides 字段")
    if not isinstance(data["slides"], list):
        raise PPTAnalystError("slides 字段必须是数组")


def extract_overview(data: dict[str, Any]) -> PresentationOverview:
    overview = PresentationOverview(
        title=data.get("presentation_title", "未知"),
        total_slides=data.get("slide_count", 0)
    )

    themes: list[str] = []
    for slide in data.get("slides", []):
        if slide.get("title"):
            themes.append(slide["title"])

    overview.key_themes = themes

    if themes:
        overview.main_topic = themes[0] if themes else "未知主题"

    return overview


def extract_key_points_from_slide(slide: dict[str, Any]) -> list[KeyPoint]:
    points: list[KeyPoint] = []
    slide_num = slide.get("slide_number", 0)
    title = slide.get("title", "")

    if title:
        points.append(KeyPoint(
            point=title,
            supporting_data=f"Slide {slide_num} 标题",
            source_slide=slide_num,
            confidence="high"
        ))

    for text in slide.get("texts", []):
        text_content = text.get("text", "")
        if text_content and len(text_content) > 5:
            points.append(KeyPoint(
                point=text_content,
                supporting_data=f"Slide {slide_num} 文本内容",
                source_slide=slide_num,
                confidence="high"
            ))

    for table in slide.get("tables", []):
        rows = table.get("rows", [])
        if rows and len(rows) > 1:
            header = " | ".join(rows[0]) if rows[0] else "表格数据"
            points.append(KeyPoint(
                point=f"表格数据: {header}",
                supporting_data=f"Slide {slide_num} 表格 ({table.get('row_count', 0)}行x{table.get('col_count', 0)}列)",
                source_slide=slide_num,
                confidence="high"
            ))

    for chart in slide.get("charts", []):
        chart_title = chart.get("title", "图表")
        chart_type = chart.get("chart_type", "未知类型")
        points.append(KeyPoint(
            point=f"图表: {chart_title} ({chart_type})",
            supporting_data=f"Slide {slide_num} 图表",
            source_slide=slide_num,
            confidence="medium"
        ))

    for note in slide.get("notes", []):
        if note and len(note) > 3:
            points.append(KeyPoint(
                point=f"备注: {note}",
                supporting_data=f"Slide {slide_num} 演讲备注",
                source_slide=slide_num,
                confidence="medium"
            ))

    return points


def build_outline(data: dict[str, Any]) -> list[Section]:
    sections: list[Section] = []
    slides = data.get("slides", [])

    if not slides:
        return sections

    current_section = Section(section_id=1, title="概述")
    section_id = 1

    for i, slide in enumerate(slides):
        slide_title = slide.get("title", "")
        slide_num = slide.get("slide_number", i + 1)

        if i == 0:
            current_section.title = slide_title or "概述"
            points = extract_key_points_from_slide(slide)
            current_section.key_points.extend(points)
        elif slide_title and any(kw in slide_title for kw in ["目录", "TOC", "Contents"]):
            continue
        elif slide_title and any(kw in slide_title for kw in ["总结", "Summary", "结论", "Conclusion", "Q&A"]):
            if current_section.key_points:
                sections.append(current_section)
            section_id += 1
            final_section = Section(section_id=section_id, title="总结与结论")
            points = extract_key_points_from_slide(slide)
            final_section.key_points.extend(points)
            sections.append(final_section)
            current_section = Section(section_id=section_id + 1)
        else:
            is_new_section = (
                slide_num > 2 and
                slide_title and
                len(slide.get("texts", [])) < 5
            )

            if is_new_section and current_section.key_points:
                sections.append(current_section)
                section_id += 1
                current_section = Section(section_id=section_id, title=slide_title)
            else:
                if not current_section.title and slide_title:
                    current_section.title = slide_title

            points = extract_key_points_from_slide(slide)
            current_section.key_points.extend(points)

    if current_section.key_points:
        sections.append(current_section)

    return sections


def analyze_insights(data: dict[str, Any], sections: list[Section]) -> Insights:
    insights = Insights()

    slides = data.get("slides", [])
    warnings = data.get("warnings", [])

    if warnings:
        insights.gaps.append(f"有 {len(warnings)} 页幻灯片解析失败，信息可能不完整")

    has_tables = any(slide.get("tables") for slide in slides)
    has_charts = any(slide.get("charts") for slide in slides)
    has_notes = any(slide.get("notes") for slide in slides)

    if has_tables:
        insights.strengths.append("包含结构化表格数据，便于数据分析")
    if has_charts:
        insights.strengths.append("包含可视化图表，直观展示数据趋势")
    if has_notes:
        insights.strengths.append("包含演讲备注，提供额外上下文信息")

    total_points = sum(len(s.key_points) for s in sections)
    if total_points < 5:
        insights.gaps.append("内容要点较少，可能需要补充更多细节")

    if not has_tables and not has_charts:
        insights.recommendations.append("建议添加数据图表以增强说服力")

    if not has_notes:
        insights.recommendations.append("建议添加演讲备注以补充说明")

    return insights


def check_warnings(data: dict[str, Any]) -> list[str]:
    warnings: list[str] = []

    for warning in data.get("warnings", []):
        warnings.append(warning)

    slides = data.get("slides", [])
    for slide in slides:
        slide_num = slide.get("slide_number", 0)
        if not slide.get("texts") and not slide.get("tables") and not slide.get("charts"):
            warnings.append(f"Slide {slide_num} 内容为空")

    return warnings


def analyze(data: dict[str, Any]) -> AnalysisResult:
    validate_input(data)

    result = AnalysisResult()

    result.presentation_overview = extract_overview(data)

    result.outline = build_outline(data)

    result.insights = analyze_insights(data, result.outline)

    result.warnings = check_warnings(data)

    result.metadata = AnalysisMetadata(
        analysis_timestamp=datetime.now().isoformat(),
        requires_user_review=True
    )

    return result


def to_dict(result: AnalysisResult) -> dict[str, Any]:
    def section_to_dict(section: Section) -> dict[str, Any]:
        return {
            "section_id": section.section_id,
            "title": section.title,
            "key_points": [
                {
                    "point": p.point,
                    "supporting_data": p.supporting_data,
                    "source_slide": p.source_slide,
                    "confidence": p.confidence
                }
                for p in section.key_points
            ],
            "sub_sections": [section_to_dict(s) for s in section.sub_sections]
        }

    return {
        "presentation_overview": {
            "title": result.presentation_overview.title,
            "total_slides": result.presentation_overview.total_slides,
            "main_topic": result.presentation_overview.main_topic,
            "key_themes": result.presentation_overview.key_themes
        },
        "outline": {
            "sections": [section_to_dict(s) for s in result.outline]
        },
        "insights": {
            "strengths": result.insights.strengths,
            "gaps": result.insights.gaps,
            "recommendations": result.insights.recommendations
        },
        "metadata": {
            "analysis_timestamp": result.metadata.analysis_timestamp,
            "requires_user_review": result.metadata.requires_user_review
        },
        "warnings": result.warnings
    }


def to_json(result: AnalysisResult, indent: int = 2) -> str:
    return json.dumps(to_dict(result), ensure_ascii=False, indent=indent)


def analyze_from_file(input_path: str | Path, output_path: str | Path | None = None) -> AnalysisResult:
    input_path = Path(input_path)

    if not input_path.exists():
        raise PPTAnalystError(f"输入文件不存在: {input_path}")

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise PPTAnalystError(f"JSON 解析失败: {e}")

    result = analyze(data)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(to_json(result), encoding='utf-8')

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python ppt_analyst.py <parsed_data.json> [output_outline.json]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = analyze_from_file(input_file, output_file)
        print(to_json(result))
        if result.warnings:
            print("\nWarnings:", file=sys.stderr)
            for w in result.warnings:
                print(f"  - {w}", file=sys.stderr)
    except PPTAnalystError as e:
        print(json.dumps({"status": "error", "reason": str(e)}))
        sys.exit(1)
