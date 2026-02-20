import os
from dataclasses import dataclass

from codeguard.common.severity import Severity


@dataclass
class CodeguardConfig:
    """Configuration for codeguard."""

    provider: str
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    rules: list[str] = None
    output_format: str = "table"
    fail_on_severity: Severity | None = None

    def __post_init__(self) -> None:
        if self.rules is None:
            self.rules = ["security", "performance", "bugs"]


def load_config() -> CodeguardConfig:
    """Load configuration from environment variables."""
    provider = os.getenv("CODEGUARD_LLM_PROVIDER", "ollama")
    model = os.getenv("CODEGUARD_MODEL", None)
    api_key = (
        os.getenv("OPENAI_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY")
        or os.getenv("CODEGUARD_API_KEY")
    )
    base_url = os.getenv("CODEGUARD_BASE_URL", None)
    rules_str = os.getenv("CODEGUARD_RULES", "security,performance,bugs")
    rules = [r.strip() for r in rules_str.split(",")]
    output_format = os.getenv("CODEGUARD_FORMAT", "table")
    fail_on_severity_str = os.getenv("CODEGUARD_FAIL_ON_SEVERITY", None)

    fail_on_severity = None
    if fail_on_severity_str:
        try:
            fail_on_severity = Severity.from_string(fail_on_severity_str)
        except ValueError:
            pass

    return CodeguardConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
        rules=rules,
        output_format=output_format,
        fail_on_severity=fail_on_severity,
    )
