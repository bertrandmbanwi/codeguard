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
        """Emoji icon for the severity level."""
        icon_map = {
            Severity.INFO: "ℹ️",
            Severity.LOW: "⚠️",
            Severity.MEDIUM: "⚠️",
            Severity.HIGH: "🔴",
            Severity.CRITICAL: "🚨",
        }
        return icon_map.get(self, "•")

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
