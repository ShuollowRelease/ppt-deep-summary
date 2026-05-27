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
    if not data or "presentation_overview" not in data or "outline" not in data:
        raise PPTFormattingError("输入数据缺少必要字段")


def parse_input(data: dict[str, Any]) -> ReportData:
    ov = data.get("presentation_overview", {})
    return ReportData(
        overview=PresentationOverview(title=ov.get("title", "未知"), total_slides=ov.get("total_slides", 0),
                                      main_topic=ov.get("main_topic", "未知"), key_themes=ov.get("key_themes", [])),
        sections=[parse_section(s) for s in data.get("outline", {}).get("sections", [])],
        insights=Insights(**data.get("insights", {})),
        timestamp=data.get("metadata", {}).get("analysis_timestamp", datetime.now().isoformat()),
        warnings=data.get("warnings", []))


def parse_section(d: dict[str, Any]) -> Section:
    return Section(section_id=d.get("section_id", 0), title=d.get("title", ""),
                   key_points=[KeyPoint(**p) for p in d.get("key_points", [])],
                   sub_sections=[parse_section(s) for s in d.get("sub_sections", [])])


def confidence_label(c: str) -> str:
    return {"high": "高", "medium": "中", "low": "低 [待确认]"}.get(c, c)


def fmt_md_point(p: KeyPoint) -> str:
    src = f"(Source: Slide {p.source_slide})" if p.source_slide else ""
    lines = [f"- **{p.point}** {src}"]
    if p.supporting_data:
        lines.append(f"  - 支撑数据：{p.supporting_data}")
    lines.append(f"  - 置信度：{confidence_label(p.confidence)}")
    return "\n".join(lines)


def fmt_md_section(s: Section) -> str:
    lines = [f"### {s.title}", ""] + [fmt_md_point(p) + "\n" for p in s.key_points]
    return "\n".join(lines)


def format_markdown(r: ReportData) -> str:
    themes = "、".join(r.overview.key_themes[:5]) + ("..." if len(r.overview.key_themes) > 5 else "")
    lines = [f"# {r.overview.title}", "", "## 概览", "",
             f"- 总页数：{r.overview.total_slides}", f"- 核心主题：{r.overview.main_topic}", f"- 关键主题：{themes}", "", "---", "",
             "## 分析大纲", ""] + [fmt_md_section(s) for s in r.sections] + ["---", "", "## 洞察分析", ""]

    if r.insights.strengths:
        lines.extend(["### 内容亮点", ""] + [f"- {s}" for s in r.insights.strengths] + [""])
    if r.insights.gaps:
        lines.extend(["### 信息缺口", ""] + [f"- {g}" for g in r.insights.gaps] + [""])
    if r.insights.recommendations:
        lines.extend(["### 改进建议", ""] + [f"- {rec}" for rec in r.insights.recommendations] + [""])
    if r.warnings:
        lines.extend(["### 警告信息", ""] + [f"- {w}" for w in r.warnings] + [""])

    lines.extend(["---", "", f"*报告生成时间：{r.timestamp}*", "*本报告基于 PPTParser 和 PPTAnalyst 自动生成*"])
    return "\n".join(lines)


def fmt_html_point(p: KeyPoint) -> str:
    src = f'<span class="source">(Source: Slide {p.source_slide})</span>' if p.source_slide else ""
    return f'<div class="key-point"><div class="point-header"><strong>{p.point}</strong> {src}<span class="confidence-{p.confidence}">{confidence_label(p.confidence)}</span></div>' + (f'<div class="supporting-data">支撑数据：{p.supporting_data}</div>' if p.supporting_data else "") + '</div>'


def fmt_html_section(s: Section) -> str:
    return f'<div class="section"><h3>{s.title}</h3>' + "".join(fmt_html_point(p) for p in s.key_points) + "".join(fmt_html_section(sub) for sub in s.sub_sections) + '</div>'


def format_html(r: ReportData) -> str:
    themes = "、".join(r.overview.key_themes[:5]) + ("..." if len(r.overview.key_themes) > 5 else "")
    sections_html = "".join(fmt_html_section(s) for s in r.sections)
    strengths_html = "<h3>内容亮点</h3><ul>" + "".join(f"<li>{s}</li>" for s in r.insights.strengths) + "</ul>" if r.insights.strengths else ""
    gaps_html = "<h3>信息缺口</h3><ul>" + "".join(f"<li>{g}</li>" for g in r.insights.gaps) + "</ul>" if r.insights.gaps else ""
    recs_html = "<h3>改进建议</h3><ul>" + "".join(f"<li>{rc}</li>" for rc in r.insights.recommendations) + "</ul>" if r.insights.recommendations else ""
    warnings_html = '<div class="warnings"><h3>警告信息</h3><ul>' + "".join(f"<li>{w}</li>" for w in r.warnings) + "</ul></div>" if r.warnings else ""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{r.overview.title}</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:900px;margin:0 auto;padding:20px;line-height:1.6}}
h1{{color:#2c3e50;border-bottom:2px solid #3498db;padding-bottom:10px}}
h2{{color:#34495e;margin-top:30px}}h3{{color:#7f8c8d}}
.section{{margin:20px 0;padding:15px;background:#fff;border-left:4px solid #3498db}}
.key-point{{margin:10px 0;padding:10px;background:#f8f9fa;border-radius:3px}}
.point-header{{display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
.source{{color:#7f8c8d;font-size:0.9em}}
.confidence-high{{color:#27ae60;font-size:0.8em;padding:2px 6px;background:#e8f5e9;border-radius:3px}}
.confidence-medium{{color:#f39c12;font-size:0.8em;padding:2px 6px;background:#fff3e0;border-radius:3px}}
.confidence-low{{color:#e74c3c;font-size:0.8em;padding:2px 6px;background:#fce4ec;border-radius:3px}}
.supporting-data{{color:#666;font-size:0.9em;margin-top:5px}}
.warnings{{background:#fff3e0;padding:15px;border-radius:5px;margin:20px 0}}
.footer{{margin-top:40px;padding-top:20px;border-top:1px solid #ddd;color:#7f8c8d;font-size:0.9em}}
</style>
</head>
<body>
<h1>{r.overview.title}</h1>
<div class="overview"><h2>概览</h2><ul>
<li><strong>总页数：</strong>{r.overview.total_slides}</li>
<li><strong>核心主题：</strong>{r.overview.main_topic}</li>
<li><strong>关键主题：</strong>{themes}</li>
</ul></div>
<h2>分析大纲</h2>{sections_html}
<div class="insights"><h2>洞察分析</h2>{strengths_html}{gaps_html}{recs_html}</div>
{warnings_html}
<div class="footer"><p><em>报告生成时间：{r.timestamp}</em></p><p><em>本报告基于 PPTParser 和 PPTAnalyst 自动生成</em></p></div>
</body></html>"""


def format_report(data: dict[str, Any], output_path: str | Path | None = None, format_type: str = "markdown") -> str:
    validate_input(data)
    report = parse_input(data)
    content = format_html(report) if format_type == "html" else format_markdown(report)
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(content, encoding='utf-8')
    return content


def format_from_file(input_path: str | Path, output_path: str | Path | None = None, format_type: str = "markdown") -> str:
    input_path = Path(input_path)
    if not input_path.exists():
        raise PPTFormattingError(f"文件不存在: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return format_report(data, output_path, format_type)


if __name__ == "__main__":
    import sys, argparse
    parser = argparse.ArgumentParser(description="PPT 排版输出")
    parser.add_argument("input", help="输入 JSON 路径")
    parser.add_argument("output", nargs="?", help="输出路径")
    parser.add_argument("--format", choices=["markdown", "html"], default="markdown")
    args = parser.parse_args()
    try:
        content = format_from_file(args.input, args.output, args.format)
        if not args.output:
            print(content)
    except PPTFormattingError as e:
        print(json.dumps({"status": "error", "reason": str(e)}))
        sys.exit(1)
