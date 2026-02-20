import json
import re

from codeguard.common.models import Finding
from codeguard.common.severity import Severity


def parse_llm_response(raw: str) -> dict | None:
    """Parse JSON from LLM response, handling markdown code blocks."""
    raw = raw.strip()

    # Handle markdown code blocks
    if raw.startswith("```"):
        match = re.search(r"```(?:json)?\s*\n(.*?)\n```", raw, re.DOTALL)
        if match:
            raw = match.group(1)

    # Try to extract JSON object
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON from the string
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                return None
        return None


def validate_finding(data: dict) -> Finding | None:
    """Validate and convert dict to Finding dataclass."""
    try:
        # Required fields
        title = data.get("title")
        severity_str = data.get("severity", "LOW").upper()
        category = data.get("category", "bug")
        description = data.get("description", "")
        suggestion = data.get("suggestion", "")

        if not title or not description:
            return None

        # Parse severity
        try:
            severity = Severity.from_string(severity_str)
        except ValueError:
            severity = Severity.LOW

        # Optional fields
        line_number = data.get("line_number")
        if line_number is not None:
            try:
                line_number = int(line_number)
            except (ValueError, TypeError):
                line_number = None

        finding = Finding(
            title=title,
            severity=severity,
            category=category,
            description=description,
            suggestion=suggestion,
            file_path="",  # Will be set by reviewer
            line_number=line_number,
            cwe_id=data.get("cwe_id"),
            owasp_ref=data.get("owasp_ref"),
            code_snippet=data.get("code_snippet"),
        )

        return finding

    except Exception:
        return None


def extract_findings(raw: str) -> list[Finding]:
    """Parse and validate findings from LLM response."""
    parsed = parse_llm_response(raw)
    if not parsed:
        return []

    findings_data = parsed.get("findings", [])
    if not isinstance(findings_data, list):
        return []

    findings = []
    for item in findings_data:
        if not isinstance(item, dict):
            continue
        finding = validate_finding(item)
        if finding:
            findings.append(finding)

    return findings
