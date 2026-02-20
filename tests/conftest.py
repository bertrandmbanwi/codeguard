"""Shared fixtures for codeguard tests."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from codeguard.common.models import CodeReviewReport, Finding
from codeguard.common.severity import Severity
from codeguard.llm.providers import LLMProvider

FIXTURES_DIR = Path(__file__).parent / "fixtures"
DIFFS_DIR = FIXTURES_DIR / "diffs"
RESPONSES_DIR = FIXTURES_DIR / "responses"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def diffs_dir():
    return DIFFS_DIR


@pytest.fixture
def responses_dir():
    return RESPONSES_DIR


@pytest.fixture
def sql_injection_diff():
    return (DIFFS_DIR / "sql_injection.diff").read_text()


@pytest.fixture
def xss_diff():
    return (DIFFS_DIR / "xss.diff").read_text()


@pytest.fixture
def multi_file_diff():
    return (DIFFS_DIR / "multi_file.diff").read_text()


@pytest.fixture
def deleted_file_diff():
    return (DIFFS_DIR / "deleted_file.diff").read_text()


@pytest.fixture
def binary_file_diff():
    return (DIFFS_DIR / "binary_file.diff").read_text()


@pytest.fixture
def valid_findings_response():
    return (RESPONSES_DIR / "valid_findings.json").read_text()


@pytest.fixture
def empty_findings_response():
    return (RESPONSES_DIR / "empty_findings.json").read_text()


@pytest.fixture
def malformed_response():
    return (RESPONSES_DIR / "malformed.json").read_text()


@pytest.fixture
def markdown_wrapped_response():
    return (RESPONSES_DIR / "markdown_wrapped.json").read_text()


@pytest.fixture
def sample_finding():
    return Finding(
        title="SQL Injection",
        severity=Severity.CRITICAL,
        category="security",
        description="SQL injection via string concatenation",
        suggestion="Use parameterized queries",
        file_path="app/db.py",
        line_number=13,
        cwe_id="CWE-89",
        owasp_ref="A03:2021",
    )


@pytest.fixture
def sample_finding_low():
    return Finding(
        title="Hardcoded Path",
        severity=Severity.LOW,
        category="style",
        description="Database path is hardcoded",
        suggestion="Use config file",
        file_path="app/db.py",
        line_number=12,
    )


@pytest.fixture
def sample_finding_high():
    return Finding(
        title="Command Injection",
        severity=Severity.HIGH,
        category="security",
        description="User input passed to shell command",
        suggestion="Use subprocess with list args, no shell=True",
        file_path="src/utils.py",
        line_number=10,
        cwe_id="CWE-78",
    )


@pytest.fixture
def sample_report(sample_finding, sample_finding_low, sample_finding_high):
    return CodeReviewReport(
        findings=[sample_finding, sample_finding_low, sample_finding_high],
        metadata={"provider": "ollama", "model": "mistral"},
    )


@pytest.fixture
def empty_report():
    return CodeReviewReport(findings=[], metadata={})


@pytest.fixture
def mock_llm_provider(valid_findings_response):
    """Create a mock LLM provider that returns valid findings."""
    provider = MagicMock(spec=LLMProvider)
    provider.review.return_value = valid_findings_response
    provider.provider_name = "mock"
    provider.model = "mock-model"
    return provider


@pytest.fixture
def mock_llm_provider_empty(empty_findings_response):
    """Create a mock LLM provider that returns empty findings."""
    provider = MagicMock(spec=LLMProvider)
    provider.review.return_value = empty_findings_response
    provider.provider_name = "mock"
    provider.model = "mock-model"
    return provider


@pytest.fixture
def mock_llm_provider_error():
    """Create a mock LLM provider that raises an exception."""
    provider = MagicMock(spec=LLMProvider)
    provider.review.side_effect = Exception("Connection refused")
    provider.provider_name = "mock"
    provider.model = "mock-model"
    return provider
