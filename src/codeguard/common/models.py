from dataclasses import asdict, dataclass, field
from typing import Any

from codeguard.common.severity import Severity


@dataclass
class Finding:
    """Represents a single code review finding."""

    title: str
    severity: Severity
    category: str
    description: str
    suggestion: str
    file_path: str
    line_number: int | None = None
    cwe_id: str | None = None
    owasp_ref: str | None = None
    code_snippet: str | None = None

    @property
    def score(self) -> int:
        """Returns severity value as score."""
        return int(self.severity)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["severity"] = self.severity.name
        return data


@dataclass
class CodeReviewReport:
    """Complete code review report."""

    findings: list[Finding] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_score(self) -> int:
        """Sum of all finding scores."""
        return sum(f.score for f in self.findings)

    @property
    def max_severity(self) -> Severity | None:
        """Highest severity finding."""
        if not self.findings:
            return None
        return max(self.findings, key=lambda f: f.score).severity

    def severity_counts(self) -> dict[str, int]:
        """Count findings by severity."""
        counts: dict[str, int] = {s.name: 0 for s in Severity}
        for finding in self.findings:
            counts[finding.severity.name] += 1
        return counts

    def category_counts(self) -> dict[str, int]:
        """Count findings by category."""
        counts: dict[str, int] = {}
        for finding in self.findings:
            counts[finding.category] = counts.get(finding.category, 0) + 1
        return counts

    def findings_at_or_above(self, severity: Severity) -> list[Finding]:
        """Filter findings at or above severity level."""
        return [f for f in self.findings if f.score >= severity]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "findings": [f.to_dict() for f in self.findings],
            "metadata": self.metadata,
            "summary": {
                "total_findings": len(self.findings),
                "total_score": self.total_score,
                "max_severity": self.max_severity.name if self.max_severity else None,
                "severity_counts": self.severity_counts(),
                "category_counts": self.category_counts(),
            },
        }
