from enum import IntEnum


class Severity(IntEnum):
    """Severity levels for code review findings."""

    INFO = 1
    LOW = 2
    MEDIUM = 4
    HIGH = 7
    CRITICAL = 10

    @property
    def label(self) -> str:
        """Human-readable label."""
        return self.name

    @property
    def color(self) -> str:
        """Rich color string for console output."""
        color_map = {
            Severity.INFO: "blue",
            Severity.LOW: "yellow",
            Severity.MEDIUM: "yellow",
            Severity.HIGH: "red",
            Severity.CRITICAL: "bold red",
        }
        return color_map.get(self, "white")

    @property
    def icon(self) -> str:
        """Terminal-friendly icon for the severity level."""
        icon_map = {
            Severity.INFO: "●",
            Severity.LOW: "▲",
            Severity.MEDIUM: "◆",
            Severity.HIGH: "✖",
            Severity.CRITICAL: "✖",
        }
        return icon_map.get(self, "•")

    @property
    def badge(self) -> str:
        """Shields.io badge URL for markdown/HTML output."""
        badge_map = {
            Severity.INFO: "https://img.shields.io/badge/INFO-5B9BD5?style=flat-square",
            Severity.LOW: "https://img.shields.io/badge/LOW-F5C518?style=flat-square",
            Severity.MEDIUM: "https://img.shields.io/badge/MEDIUM-ED8B00?style=flat-square",
            Severity.HIGH: "https://img.shields.io/badge/HIGH-E53935?style=flat-square",
            Severity.CRITICAL: "https://img.shields.io/badge/CRITICAL-B71C1C?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyTDEgMjFoMjJMMTIgMnptMCAxNy4zYy0uNyAwLTEuMy0uNi0xLjMtMS4zczEuMy0xLjMgMS4zLTEuMyAxLjMuNiAxLjMgMS4zLS42IDEuMy0xLjMgMS4zem0xLTQuM2gtMlY5aDJ2NnoiLz48L3N2Zz4=",
        }
        return badge_map.get(self, "")

    @classmethod
    def from_string(cls, value: str) -> "Severity":
        """Convert string to Severity enum."""
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(
                f"Unknown severity: {value}. "
                f"Available: {', '.join([s.name for s in cls])}"
            )
