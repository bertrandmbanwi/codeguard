import json
from typing import Any

from rich.console import Console
from rich.table import Table

from codeguard import __version__
from codeguard.common.models import CodeReviewReport
from codeguard.common.severity import Severity


def render_table(report: CodeReviewReport, console: Console | None = None) -> str:
    """Render findings as a Rich table."""
    if console is None:
        console = Console()

    table = Table(title="Code Review Findings", show_header=True, header_style="bold")
    table.add_column("Severity", style="bold")
    table.add_column("Category")
    table.add_column("Title")
    table.add_column("File:Line")
    table.add_column("Description")

    for finding in report.findings:
        severity_label = f"{finding.severity.icon} {finding.severity.label}"
        file_line = f"{finding.file_path}"
        if finding.line_number:
            file_line += f":{finding.line_number}"

        desc = finding.description
        if len(desc) > 50:
            desc = desc[:50] + "..."
        table.add_row(
            severity_label,
            finding.category,
            finding.title,
            file_line,
            desc,
            style=finding.severity.color,
        )

    # Summary
    counts = report.severity_counts()
    summary = f"Total: {len(report.findings)} | "
    severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    summary += " | ".join([f"{s}: {counts[s]}" for s in severities])

    with console.capture() as capture:
        console.print(table)
        console.print(f"\n{summary}")

    return capture.get()


def render_json(report: CodeReviewReport) -> str:
    """Render report as JSON."""
    return json.dumps(report.to_dict(), indent=2)


def render_markdown(report: CodeReviewReport) -> str:
    """Render report as Markdown."""
    lines = [
        "# Code Review Report",
        "",
        f"**Total Findings:** {len(report.findings)}",
        "",
    ]

    # Summary by severity
    counts = report.severity_counts()
    lines.append("## Summary by Severity")
    lines.append("")
    for severity in Severity:
        count = counts[severity.name]
        if count > 0:
            lines.append(f"- **{severity.label}**: {count}")
    lines.append("")

    # Summary by category
    cat_counts = report.category_counts()
    if cat_counts:
        lines.append("## Summary by Category")
        lines.append("")
        for category, count in sorted(cat_counts.items()):
            lines.append(f"- **{category}**: {count}")
        lines.append("")

    # Detailed findings
    lines.append("## Findings")
    lines.append("")

    for i, finding in enumerate(report.findings, 1):
        lines.append(f"### {i}. {finding.title}")
        lines.append("")
        lines.append(f"- **Severity:** {finding.severity.label} {finding.severity.icon}")
        lines.append(f"- **Category:** {finding.category}")
        lines.append(f"- **File:** {finding.file_path}")
        if finding.line_number:
            lines.append(f"- **Line:** {finding.line_number}")
        if finding.cwe_id:
            lines.append(f"- **CWE:** {finding.cwe_id}")
        if finding.owasp_ref:
            lines.append(f"- **OWASP:** {finding.owasp_ref}")
        lines.append("")
        lines.append(f"**Description:**\n\n{finding.description}")
        lines.append("")
        lines.append(f"**Suggestion:**\n\n{finding.suggestion}")
        lines.append("")

    return "\n".join(lines)


def render_sarif(
    report: CodeReviewReport,
    tool_name: str = "codeguard",
    tool_version: str | None = None,
) -> dict[str, Any]:
    """Render report as SARIF 2.1.0."""
    if tool_version is None:
        tool_version = __version__

    results = []
    for finding in report.findings:
        result: dict[str, Any] = {
            "ruleId": finding.cwe_id or "GC001",
            "level": finding.severity.name.lower(),
            "message": {
                "text": finding.description,
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": finding.file_path,
                        },
                    },
                }
            ],
            "properties": {
                "category": finding.category,
                "suggestion": finding.suggestion,
            },
        }

        if finding.line_number:
            result["locations"][0]["physicalLocation"]["region"] = {
                "startLine": finding.line_number,
            }

        if finding.owasp_ref:
            result["properties"]["owasp"] = finding.owasp_ref

        results.append(result)

    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "version": tool_version,
                        "informationUri": "https://github.com/bertrandmbanwi/codeguard",
                    },
                },
                "results": results,
            },
        ],
    }

    return sarif


def format_report(report: CodeReviewReport, format_name: str) -> str:
    """Format report using specified format."""
    format_name = format_name.lower()

    if format_name == "json":
        return render_json(report)
    elif format_name == "markdown" or format_name == "md":
        return render_markdown(report)
    elif format_name == "sarif":
        return json.dumps(render_sarif(report), indent=2)
    else:  # default to table
        return render_table(report)
