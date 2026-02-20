"""Tests for CodeReviewer orchestration."""



from codeguard.common.models import CodeReviewReport
from codeguard.review.reviewer import CodeReviewer


class TestCodeReviewer:
    """Tests for the CodeReviewer class."""

    def test_review_returns_report(self, mock_llm_provider, sql_injection_diff):
        reviewer = CodeReviewer(
            provider=mock_llm_provider,
            rules_context="",
            categories=["security"],
        )
        report = reviewer.review_diff(sql_injection_diff)
        assert isinstance(report, CodeReviewReport)

    def test_review_calls_llm_per_file(self, mock_llm_provider, multi_file_diff):
        reviewer = CodeReviewer(
            provider=mock_llm_provider,
            rules_context="",
            categories=["security"],
        )
        reviewer.review_diff(multi_file_diff)
        # multi_file_diff has 2 files, both reviewable
        assert mock_llm_provider.review.call_count == 2

    def test_review_sets_file_path_on_findings(self, mock_llm_provider, sql_injection_diff):
        reviewer = CodeReviewer(
            provider=mock_llm_provider,
            rules_context="",
            categories=["security"],
        )
        report = reviewer.review_diff(sql_injection_diff)
        for finding in report.findings:
            assert finding.file_path == "app/db.py"

    def test_review_skips_deleted_files(self, mock_llm_provider, deleted_file_diff):
        reviewer = CodeReviewer(
            provider=mock_llm_provider,
            rules_context="",
            categories=["security"],
        )
        reviewer.review_diff(deleted_file_diff)
        # Deleted files should be skipped
        assert mock_llm_provider.review.call_count == 0

    def test_review_skips_binary_files(self, mock_llm_provider, binary_file_diff):
        reviewer = CodeReviewer(
            provider=mock_llm_provider,
            rules_context="",
            categories=["security"],
        )
        reviewer.review_diff(binary_file_diff)
        # Only main.py should be reviewed, not logo.png
        assert mock_llm_provider.review.call_count == 1

    def test_review_empty_diff(self, mock_llm_provider):
        reviewer = CodeReviewer(
            provider=mock_llm_provider,
            rules_context="",
            categories=["security"],
        )
        report = reviewer.review_diff("")
        assert len(report.findings) == 0
        assert mock_llm_provider.review.call_count == 0

    def test_review_handles_llm_error(self, mock_llm_provider_error, sql_injection_diff):
        reviewer = CodeReviewer(
            provider=mock_llm_provider_error,
            rules_context="",
            categories=["security"],
        )
        # Should not raise, just warn and return empty
        report = reviewer.review_diff(sql_injection_diff)
        assert isinstance(report, CodeReviewReport)
        assert len(report.findings) == 0

    def test_review_metadata(self, mock_llm_provider, sql_injection_diff):
        reviewer = CodeReviewer(
            provider=mock_llm_provider,
            rules_context="",
            categories=["security", "performance"],
        )
        report = reviewer.review_diff(sql_injection_diff)
        assert report.metadata["provider"] == "mock"
        assert report.metadata["model"] == "mock-model"
        assert "security" in report.metadata["categories"]

    def test_review_empty_findings_from_llm(self, mock_llm_provider_empty, sql_injection_diff):
        reviewer = CodeReviewer(
            provider=mock_llm_provider_empty,
            rules_context="",
            categories=["security"],
        )
        report = reviewer.review_diff(sql_injection_diff)
        assert len(report.findings) == 0
