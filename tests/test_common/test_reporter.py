"""Tests for report formatters."""

import json

from codeguard.common.models import CodeReviewReport, Finding
from codeguard.common.reporter import (
    format_report,
    render_json,
    render_markdown,
    render_sarif,
    render_table,
)
from codeguard.common.severity import Severity


class TestRenderJson:
    """Tests for JSON report rendering."""

    def test_render_json_valid(self, sample_report):
        output = render_json(sample_report)
        data = json.loads(output)
        assert "findings" in data
        assert len(data["findings"]) == 3

    def test_render_json_empty(self, empty_report):
        output = render_json(empty_report)
        data = json.loads(output)
        assert len(data["findings"]) == 0

    def test_render_json_preserves_severity_name(self, sample_report):
        output = render_json(sample_report)
        data = json.loads(output)
        assert data["findings"][0]["severity"] == "CRITICAL"


class TestRenderMarkdown:
    """Tests for Markdown report rendering."""

    def test_render_markdown_header(self, sample_report):
        output = render_markdown(sample_report)
        assert "# Code Review Report" in output
        assert "**Total Findings:** 3" in output

    def test_render_markdown_severity_summary(self, sample_report):
        output = render_markdown(sample_report)
        assert "## Summary by Severity" in output
        assert "img.shields.io/badge/CRITICAL" in output
        assert "img.shields.io/badge/HIGH" in output

    def test_render_markdown_findings_detail(self, sample_report):
        output = render_markdown(sample_report)
        assert "### 1. SQL Injection" in output
        assert "**Category:** security" in output

    def test_render_markdown_cwe_and_owasp(self, sample_report):
        output = render_markdown(sample_report)
        assert "**CWE:** CWE-89" in output
        assert "**OWASP:** A03:2021" in output

    def test_render_markdown_empty(self, empty_report):
        output = render_markdown(empty_report)
        assert "# Code Review Report" in output
        assert "**Total Findings:** 0" in output

    def test_render_markdown_category_summary(self, sample_report):
        output = render_markdown(sample_report)
        assert "## Summary by Category" in output
        assert "**security**: 2" in output


class TestRenderSarif:
    """Tests for SARIF report rendering."""

    def test_sarif_version(self, sample_report):
        sarif = render_sarif(sample_report)
        assert sarif["version"] == "2.1.0"

    def test_sarif_schema(self, sample_report):
        sarif = render_sarif(sample_report)
        assert "$schema" in sarif
        assert "sarif-schema-2.1.0" in sarif["$schema"]

    def test_sarif_tool_info(self, sample_report):
        sarif = render_sarif(sample_report)
        driver = sarif["runs"][0]["tool"]["driver"]
        assert driver["name"] == "codeguard"
        assert driver["version"] is not None

    def test_sarif_custom_tool_name(self, sample_report):
        sarif = render_sarif(sample_report, tool_name="my-tool", tool_version="2.0")
        driver = sarif["runs"][0]["tool"]["driver"]
        assert driver["name"] == "my-tool"
        assert driver["version"] == "2.0"

    def test_sarif_results_count(self, sample_report):
        sarif = render_sarif(sample_report)
        results = sarif["runs"][0]["results"]
        assert len(results) == 3

    def test_sarif_result_structure(self, sample_report):
        sarif = render_sarif(sample_report)
        result = sarif["runs"][0]["results"][0]
        assert "ruleId" in result
        assert "level" in result
        assert "message" in result
        assert "locations" in result
        assert result["ruleId"] == "CWE-89"
        assert result["level"] == "critical"

    def test_sarif_line_number(self, sample_report):
        sarif = render_sarif(sample_report)
        result = sarif["runs"][0]["results"][0]
        region = result["locations"][0]["physicalLocation"]["region"]
        assert region["startLine"] == 13

    def test_sarif_no_line_number(self):
        finding = Finding(
            title="Test",
            severity=Severity.LOW,
            category="style",
            description="No line",
            suggestion="Fix",
            file_path="test.py",
        )
        report = CodeReviewReport(findings=[finding])
        sarif = render_sarif(report)
        location = sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
        assert "region" not in location

    def test_sarif_owasp_property(self, sample_report):
        sarif = render_sarif(sample_report)
        result = sarif["runs"][0]["results"][0]
        assert result["properties"]["owasp"] == "A03:2021"

    def test_sarif_empty_report(self, empty_report):
        sarif = render_sarif(empty_report)
        assert len(sarif["runs"][0]["results"]) == 0


class TestRenderTable:
    """Tests for Rich table rendering."""

    def test_render_table_output(self, sample_report):
        output = render_table(sample_report)
        assert "Code Review Findings" in output
        assert "SQL Injection" in output

    def test_render_table_empty(self, empty_report):
        output = render_table(empty_report)
        assert "Total: 0" in output


class TestFormatReport:
    """Tests for the format_report dispatcher."""

    def test_format_json(self, sample_report):
        output = format_report(sample_report, "json")
        data = json.loads(output)
        assert "findings" in data

    def test_format_markdown(self, sample_report):
        output = format_report(sample_report, "markdown")
        assert "# Code Review Report" in output

    def test_format_md_alias(self, sample_report):
        output = format_report(sample_report, "md")
        assert "# Code Review Report" in output

    def test_format_sarif(self, sample_report):
        output = format_report(sample_report, "sarif")
        data = json.loads(output)
        assert data["version"] == "2.1.0"

    def test_format_table_default(self, sample_report):
        output = format_report(sample_report, "table")
        assert "Code Review Findings" in output

    def test_format_unknown_defaults_table(self, sample_report):
        output = format_report(sample_report, "unknown_format")
        assert "Code Review Findings" in output
