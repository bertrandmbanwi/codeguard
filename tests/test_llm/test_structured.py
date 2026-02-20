"""Tests for structured LLM response parsing."""

import json

from codeguard.common.severity import Severity
from codeguard.llm.structured import extract_findings, parse_llm_response, validate_finding


class TestParseLlmResponse:
    """Tests for raw JSON parsing."""

    def test_parse_valid_json(self, valid_findings_response):
        result = parse_llm_response(valid_findings_response)
        assert result is not None
        assert "findings" in result
        assert len(result["findings"]) == 2

    def test_parse_empty_findings(self, empty_findings_response):
        result = parse_llm_response(empty_findings_response)
        assert result is not None
        assert result["findings"] == []

    def test_parse_markdown_wrapped(self, markdown_wrapped_response):
        result = parse_llm_response(markdown_wrapped_response)
        assert result is not None
        assert "findings" in result

    def test_parse_malformed(self, malformed_response):
        result = parse_llm_response(malformed_response)
        assert result is None

    def test_parse_json_with_surrounding_text(self):
        raw = 'Here is my analysis:\n{"findings": [{"title": "Bug"}]}\nDone.'
        result = parse_llm_response(raw)
        assert result is not None
        assert "findings" in result

    def test_parse_empty_string(self):
        assert parse_llm_response("") is None

    def test_parse_whitespace_only(self):
        assert parse_llm_response("   \n  ") is None

    def test_parse_json_without_findings_key(self):
        raw = '{"issues": []}'
        result = parse_llm_response(raw)
        assert result is not None  # JSON is valid
        assert "issues" in result

    def test_parse_markdown_code_block_no_lang(self):
        raw = '```\n{"findings": []}\n```'
        result = parse_llm_response(raw)
        assert result is not None


class TestValidateFinding:
    """Tests for finding validation."""

    def test_validate_complete_finding(self):
        data = {
            "title": "SQL Injection",
            "severity": "CRITICAL",
            "category": "security",
            "description": "SQL injection found",
            "suggestion": "Use parameterized queries",
            "line_number": 42,
            "cwe_id": "CWE-89",
            "owasp_ref": "A03:2021",
        }
        finding = validate_finding(data)
        assert finding is not None
        assert finding.title == "SQL Injection"
        assert finding.severity == Severity.CRITICAL
        assert finding.line_number == 42

    def test_validate_minimal_finding(self):
        data = {
            "title": "Test Issue",
            "description": "Something is wrong",
        }
        finding = validate_finding(data)
        assert finding is not None
        assert finding.severity == Severity.LOW  # default
        assert finding.category == "bug"  # default

    def test_validate_missing_title(self):
        data = {"description": "No title"}
        assert validate_finding(data) is None

    def test_validate_missing_description(self):
        data = {"title": "No desc", "description": ""}
        assert validate_finding(data) is None

    def test_validate_invalid_severity_defaults_low(self):
        data = {
            "title": "Test",
            "severity": "EXTREME",
            "description": "Test desc",
        }
        finding = validate_finding(data)
        assert finding is not None
        assert finding.severity == Severity.LOW

    def test_validate_line_number_string(self):
        data = {
            "title": "Test",
            "description": "Test desc",
            "line_number": "42",
        }
        finding = validate_finding(data)
        assert finding.line_number == 42

    def test_validate_line_number_invalid(self):
        data = {
            "title": "Test",
            "description": "Test desc",
            "line_number": "not-a-number",
        }
        finding = validate_finding(data)
        assert finding is not None
        assert finding.line_number is None

    def test_validate_file_path_empty(self):
        data = {
            "title": "Test",
            "description": "Desc",
            "suggestion": "Fix",
        }
        finding = validate_finding(data)
        assert finding.file_path == ""  # set by reviewer later


class TestExtractFindings:
    """Tests for full extraction pipeline."""

    def test_extract_valid_findings(self, valid_findings_response):
        findings = extract_findings(valid_findings_response)
        assert len(findings) == 2
        assert findings[0].title == "SQL Injection Vulnerability"
        assert findings[0].severity == Severity.CRITICAL

    def test_extract_empty_findings(self, empty_findings_response):
        findings = extract_findings(empty_findings_response)
        assert findings == []

    def test_extract_from_markdown_wrapped(self, markdown_wrapped_response):
        findings = extract_findings(markdown_wrapped_response)
        assert len(findings) == 1
        assert findings[0].severity == Severity.HIGH

    def test_extract_from_malformed(self, malformed_response):
        findings = extract_findings(malformed_response)
        assert findings == []

    def test_extract_skips_invalid_items(self):
        raw = json.dumps({
            "findings": [
                {"title": "Valid", "description": "OK"},
                "not a dict",
                {"no_title": True},
                {"title": "Also Valid", "description": "Fine"},
            ]
        })
        findings = extract_findings(raw)
        assert len(findings) == 2

    def test_extract_non_list_findings(self):
        raw = json.dumps({"findings": "not a list"})
        findings = extract_findings(raw)
        assert findings == []
