from dataclasses import dataclass


@dataclass
class RuleCategory:
    """Represents a rule category."""

    name: str
    description: str
    enabled: bool = True


CATEGORIES = {
    "security": RuleCategory(
        name="security",
        description="Security vulnerabilities and risks",
        enabled=True,
    ),
    "performance": RuleCategory(
        name="performance",
        description="Performance and efficiency issues",
        enabled=True,
    ),
    "bugs": RuleCategory(
        name="bugs",
        description="Logic errors and bugs",
        enabled=True,
    ),
    "style": RuleCategory(
        name="style",
        description="Code style and best practices",
        enabled=True,
    ),
}
