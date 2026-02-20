"""Tests for Finding and CodeReviewReport models."""


from codeguard.common.models import Finding
from codeguard.common.severity import Severity


class TestFinding:
    """Tests for the Finding dataclass."""

    def test_finding_creation(self, sample_finding):
        assert sample_finding.title == "SQL Injection"
        assert sample_finding.severity == Severity.CRITICAL
        assert sample_finding.category == "security"
        assert sample_finding.file_path == "app/db.py"
        assert sample_finding.line_number == 13

    def test_finding_score(self, sample_finding):
        assert sample_finding.score == 10  # CRITICAL = 10

    def test_finding_score_low(self, sample_finding_low):
        assert sample_finding_low.score == 2  # LOW = 2

    def test_finding_to_dict(self, sample_finding):
        data = sample_finding.to_dict()
        assert data["title"] == "SQL Injection"
        assert data["severity"] == "CRITICAL"
        assert data["category"] == "security"
        assert data["cwe_id"] == "CWE-89"
        assert data["owasp_ref"] == "A03:2021"
        assert data["line_number"] == 13

    def test_finding_optional_fields_none(self):
        finding = Finding(
            title="Test",
            severity=Severity.INFO,
            category="style",
            description="Test finding",
            suggestion="Fix it",
            file_path="test.py",
        )
        assert finding.line_number is None
        assert finding.cwe_id is None
        assert finding.owasp_ref is None
        assert finding.code_snippet is None

    def test_finding_to_dict_severity_name(self):
        finding = Finding(
            title="Test",
            severity=Severity.MEDIUM,
            category="bug",
            description="A bug",
            suggestion="Fix",
            file_path="test.py",
        )
        data = finding.to_dict()
        assert data["severity"] == "MEDIUM"
        assert isinstance(data["severity"], str)


class TestCodeReviewReport:
    """Tests for the CodeReviewReport dataclass."""

    def test_empty_report(self, empty_report):
        assert len(empty_report.findings) == 0
        assert empty_report.total_score == 0
        assert empty_report.max_severity is None

    def test_report_total_score(self, sample_report):
        # CRITICAL(10) + LOW(2) + HIGH(7)
        assert sample_report.total_score == 19

    def test_report_max_severity(self, sample_report):
        assert sample_report.max_severity == Severity.CRITICAL

    def test_report_severity_counts(self, sample_report):
        counts = sample_report.severity_counts()
        assert counts["CRITICAL"] == 1
        assert counts["HIGH"] == 1
        assert counts["LOW"] == 1
        assert counts["MEDIUM"] == 0
        assert counts["INFO"] == 0

    def test_report_category_counts(self, sample_report):
        counts = sample_report.category_counts()
        assert counts["security"] == 2
        assert counts["style"] == 1

    def test_report_findings_at_or_above(self, sample_report):
        high_plus = sample_report.findings_at_or_above(Severity.HIGH)
        assert len(high_plus) == 2  # CRITICAL + HIGH

        critical_only = sample_report.findings_at_or_above(Severity.CRITICAL)
        assert len(critical_only) == 1

        all_findings = sample_report.findings_at_or_above(Severity.INFO)
        assert len(all_findings) == 3

    def test_report_to_dict(self, sample_report):
        data = sample_report.to_dict()
        assert "findings" in data
        assert "metadata" in data
        assert "summary" in data
        assert data["summary"]["total_findings"] == 3
        assert data["summary"]["total_score"] == 19
        assert data["summary"]["max_severity"] == "CRITICAL"

    def test_report_to_dict_empty(self, empty_report):
        data = empty_report.to_dict()
        assert data["summary"]["total_findings"] == 0
        assert data["summary"]["max_severity"] is None

    def test_report_metadata(self, sample_report):
        assert sample_report.metadata["provider"] == "ollama"
        assert sample_report.metadata["model"] == "mistral"
