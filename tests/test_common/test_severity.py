"""Tests for Severity enum."""

import pytest

from codeguard.common.severity import Severity


class TestSeverity:
    """Tests for the Severity enum."""

    def test_severity_values(self):
        assert Severity.INFO == 1
        assert Severity.LOW == 2
        assert Severity.MEDIUM == 4
        assert Severity.HIGH == 7
        assert Severity.CRITICAL == 10

    def test_severity_ordering(self):
        assert Severity.INFO < Severity.LOW
        assert Severity.LOW < Severity.MEDIUM
        assert Severity.MEDIUM < Severity.HIGH
        assert Severity.HIGH < Severity.CRITICAL

    def test_severity_labels(self):
        assert Severity.INFO.label == "INFO"
        assert Severity.LOW.label == "LOW"
        assert Severity.MEDIUM.label == "MEDIUM"
        assert Severity.HIGH.label == "HIGH"
        assert Severity.CRITICAL.label == "CRITICAL"

    def test_severity_colors(self):
        assert Severity.INFO.color == "blue"
        assert Severity.LOW.color == "yellow"
        assert Severity.MEDIUM.color == "yellow"
        assert Severity.HIGH.color == "red"
        assert Severity.CRITICAL.color == "bold red"

    def test_severity_icons(self):
        assert Severity.CRITICAL.icon == "✖"
        assert Severity.HIGH.icon == "✖"
        assert Severity.MEDIUM.icon == "◆"
        assert Severity.LOW.icon == "▲"
        assert Severity.INFO.icon == "●"

    def test_severity_badges(self):
        assert "img.shields.io" in Severity.CRITICAL.badge
        assert "CRITICAL" in Severity.CRITICAL.badge
        assert "HIGH" in Severity.HIGH.badge
        assert "MEDIUM" in Severity.MEDIUM.badge
        assert "LOW" in Severity.LOW.badge
        assert "INFO" in Severity.INFO.badge

    def test_from_string_valid(self):
        assert Severity.from_string("INFO") == Severity.INFO
        assert Severity.from_string("low") == Severity.LOW
        assert Severity.from_string("Medium") == Severity.MEDIUM
        assert Severity.from_string("HIGH") == Severity.HIGH
        assert Severity.from_string("critical") == Severity.CRITICAL

    def test_from_string_invalid(self):
        with pytest.raises(ValueError, match="Unknown severity"):
            Severity.from_string("UNKNOWN")

    def test_from_string_empty(self):
        with pytest.raises(ValueError):
            Severity.from_string("")

    def test_severity_is_intenum(self):
        assert int(Severity.CRITICAL) == 10
        assert int(Severity.INFO) == 1

    def test_severity_comparison_with_int(self):
        assert Severity.HIGH >= 7
        assert Severity.LOW < 4
