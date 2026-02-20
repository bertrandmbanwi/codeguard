import sys
from pathlib import Path

import yaml


def _get_rules_dir() -> Path:
    """Get the rules directory path."""
    if sys.version_info >= (3, 9):
        try:
            from importlib.resources import files
            rules_path = files("codeguard").joinpath("rules")
            # For importlib.resources, we need to convert to a path
            # This works differently depending on the installation method
            try:
                return Path(str(rules_path))
            except Exception:
                # Fallback to relative path
                pkg_dir = Path(__file__).parent.parent
                return pkg_dir / "rules"
        except ImportError:
            pass

    # Fallback: relative to this module
    return Path(__file__).parent.parent / "rules"


def load_rules(rules_dir: Path | None = None) -> dict:
    """Load rules from YAML files."""
    if rules_dir is None:
        rules_dir = _get_rules_dir()

    rules: dict = {}

    # Load CWE rules
    cwe_file = rules_dir / "cwe.yaml"
    if cwe_file.exists():
        with open(cwe_file) as f:
            data = yaml.safe_load(f) or {}
            rules["cwe"] = data.get("cwe_rules", [])

    # Load OWASP rules
    owasp_file = rules_dir / "owasp.yaml"
    if owasp_file.exists():
        with open(owasp_file) as f:
            data = yaml.safe_load(f) or {}
            rules["owasp"] = data.get("owasp_rules", [])

    return rules


def build_rules_context(rules: dict, categories: list[str]) -> str:
    """Format rules as text for prompt injection."""
    lines = ["## Security Knowledge Base"]
    lines.append("")

    # Add CWE rules
    cwe_rules = rules.get("cwe", [])
    if cwe_rules:
        lines.append("### Common Weakness Enumeration (CWE)")
        lines.append("")
        for rule in cwe_rules[:15]:  # Limit to top 15
            cwe_id = rule.get("id", "")
            title = rule.get("title", "")
            category = rule.get("category", "")
            severity = rule.get("severity_if_found", "MEDIUM")
            description = rule.get("description", "")

            if category.lower() in [c.lower() for c in categories]:
                lines.append(f"- **{cwe_id}: {title}** ({severity})")
                lines.append(f"  {description}")
        lines.append("")

    # Add OWASP rules
    owasp_rules = rules.get("owasp", [])
    if owasp_rules:
        lines.append("### OWASP Top 10 2021")
        lines.append("")
        for rule in owasp_rules[:10]:
            rule_id = rule.get("id", "")
            title = rule.get("title", "")
            description = rule.get("description", "")[:100]

            lines.append(f"- **{rule_id}: {title}**")
            lines.append(f"  {description}...")
        lines.append("")

    return "\n".join(lines)
