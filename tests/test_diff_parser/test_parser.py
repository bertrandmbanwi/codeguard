"""Tests for UnifiedDiffParser."""

import pytest

from codeguard.diff_parser.models import DiffHunk, FileDiff, ParsedDiff
from codeguard.diff_parser.parser import UnifiedDiffParser


class TestDetectLanguage:
    """Tests for language detection from file extensions."""

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("app/main.py", "python"),
            ("src/index.js", "javascript"),
            ("src/app.ts", "typescript"),
            ("src/Component.tsx", "typescript"),
            ("src/App.jsx", "javascript"),
            ("main.go", "go"),
            ("lib.rs", "rust"),
            ("Main.java", "java"),
            ("script.rb", "ruby"),
            ("config.yaml", "yaml"),
            ("config.yml", "yaml"),
            ("main.tf", "terraform"),
            ("data.json", "json"),
            ("page.html", "html"),
            ("style.css", "css"),
            ("style.scss", "scss"),
            ("run.sh", "bash"),
            ("query.sql", "sql"),
            ("main.c", "c"),
            ("main.cpp", "cpp"),
            ("header.h", "c"),
            ("header.hpp", "cpp"),
            ("index.php", "php"),
            ("App.swift", "swift"),
            ("Main.kt", "kotlin"),
        ],
    )
    def test_detect_known_languages(self, path, expected):
        assert UnifiedDiffParser.detect_language(path) == expected

    def test_detect_binary(self):
        assert UnifiedDiffParser.detect_language("logo.png") == "binary"
        assert UnifiedDiffParser.detect_language("doc.pdf") == "binary"
        assert UnifiedDiffParser.detect_language("image.jpg") == "binary"

    def test_detect_unknown(self):
        assert UnifiedDiffParser.detect_language("README") == "unknown"
        assert UnifiedDiffParser.detect_language("Makefile") == "unknown"

    def test_detect_strips_prefix(self):
        assert UnifiedDiffParser.detect_language("b/src/main.py") == "python"
        assert UnifiedDiffParser.detect_language("a/src/main.py") == "python"


class TestParseDiff:
    """Tests for diff parsing."""

    def test_parse_sql_injection_diff(self, sql_injection_diff):
        result = UnifiedDiffParser.parse(sql_injection_diff)
        assert isinstance(result, ParsedDiff)
        assert result.total_files == 1
        assert result.files[0].path == "app/db.py"
        assert result.files[0].language == "python"

    def test_parse_multi_file_diff(self, multi_file_diff):
        result = UnifiedDiffParser.parse(multi_file_diff)
        assert result.total_files == 2
        paths = [f.path for f in result.files]
        assert "src/auth.py" in paths
        assert "src/utils.py" in paths

    def test_parse_new_file_detected(self, multi_file_diff):
        result = UnifiedDiffParser.parse(multi_file_diff)
        auth_file = next(f for f in result.files if f.path == "src/auth.py")
        assert auth_file.is_new is True

    def test_parse_deleted_file_detected(self, deleted_file_diff):
        result = UnifiedDiffParser.parse(deleted_file_diff)
        assert result.total_files == 1
        assert result.files[0].is_deleted is True

    def test_parse_binary_files_skipped(self, binary_file_diff):
        result = UnifiedDiffParser.parse(binary_file_diff)
        # Binary file (logo.png) should be skipped, only main.py remains
        paths = [f.path for f in result.files]
        assert "assets/logo.png" not in paths
        assert "src/main.py" in paths

    def test_parse_empty_diff(self):
        result = UnifiedDiffParser.parse("")
        assert result.total_files == 0
        assert result.total_additions == 0
        assert result.total_deletions == 0

    def test_parse_hunk_line_numbers(self, sql_injection_diff):
        result = UnifiedDiffParser.parse(sql_injection_diff)
        hunks = result.files[0].hunks
        assert len(hunks) >= 1
        hunk = hunks[0]
        assert hunk.start_line > 0
        assert len(hunk.added_lines) > 0

    def test_parse_hunk_content(self, sql_injection_diff):
        result = UnifiedDiffParser.parse(sql_injection_diff)
        hunk = result.files[0].hunks[0]
        assert hunk.content  # Content should not be empty

    def test_total_additions(self, multi_file_diff):
        result = UnifiedDiffParser.parse(multi_file_diff)
        assert result.total_additions > 0

    def test_total_deletions(self, deleted_file_diff):
        result = UnifiedDiffParser.parse(deleted_file_diff)
        assert result.total_deletions > 0

    def test_parse_no_newline_marker(self):
        diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,2 +1,3 @@
 line1
+line2
 line3
\\ No newline at end of file
"""
        result = UnifiedDiffParser.parse(diff)
        assert result.total_files == 1
        assert result.files[0].hunks[0].added_lines


class TestParsedDiffModel:
    """Tests for ParsedDiff dataclass properties."""

    def test_parsed_diff_empty(self):
        pd = ParsedDiff()
        assert pd.total_files == 0
        assert pd.total_additions == 0
        assert pd.total_deletions == 0

    def test_file_diff_defaults(self):
        fd = FileDiff(path="test.py", language="python")
        assert fd.hunks == []
        assert fd.is_new is False
        assert fd.is_deleted is False

    def test_diff_hunk_defaults(self):
        dh = DiffHunk(start_line=1, end_line=10)
        assert dh.added_lines == []
        assert dh.removed_lines == []
        assert dh.content == ""
