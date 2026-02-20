import sys
from pathlib import Path

import typer
from rich.console import Console

from codeguard import __version__
from codeguard.common.config import load_config
from codeguard.common.reporter import format_report
from codeguard.common.severity import Severity
from codeguard.llm.providers import get_provider
from codeguard.review.reviewer import CodeReviewer
from codeguard.rules.knowledge_base import build_rules_context, load_rules

app = typer.Typer(
    name="codeguard",
    help="AI-powered code review — security, bugs, and performance analysis",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"codeguard {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_flag=True,
        help="Show version",
    ),
) -> None:
    """AI-powered code review tool."""
    pass


@app.command()
def review(
    file: Path = typer.Option(
        None,
        "--file",
        "-f",
        help="Diff file to review (or use stdin)",
    ),
    provider: str = typer.Option(
        "ollama",
        "--provider",
        "-p",
        help="LLM provider: openai, anthropic, ollama",
    ),
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Model name (default varies by provider)",
    ),
    api_key: str = typer.Option(
        None,
        "--api-key",
        "-k",
        help="API key (or use env var)",
    ),
    rules: str = typer.Option(
        "security,performance,bugs",
        "--rules",
        "-r",
        help="Rule categories (comma-separated)",
    ),
    format_opt: str = typer.Option(
        "table",
        "--format",
        "-o",
        help="Output: table, json, markdown, sarif",
    ),
    output: Path = typer.Option(
        None,
        "--output",
        help="Write output to file",
    ),
    fail_on_severity: str = typer.Option(
        None,
        "--fail-on-severity",
        help="Exit 1 if findings >= severity (e.g., HIGH)",
    ),
) -> None:
    """Review code diff using LLM."""

    # Read diff from file or stdin
    if file:
        if not file.exists():
            console.print(f"[red]Error: File not found: {file}[/red]")
            raise typer.Exit(1)
        diff_text = file.read_text()
    else:
        # Read from stdin
        if sys.stdin.isatty():
            console.print("[yellow]No diff provided. Use --file or pipe diff via stdin.[/yellow]")
            raise typer.Exit(1)
        diff_text = sys.stdin.read()

    if not diff_text.strip():
        console.print("[yellow]No diff content provided.[/yellow]")
        raise typer.Exit(1)

    # Parse rules
    rule_categories = [r.strip().lower() for r in rules.split(",")]

    # Parse fail_on_severity
    fail_severity = None
    if fail_on_severity:
        try:
            fail_severity = Severity.from_string(fail_on_severity)
        except ValueError:
            console.print(
                f"[red]Error: Invalid severity: {fail_on_severity}[/red]"
            )
            raise typer.Exit(1)

    # Load config
    config = load_config()

    # Override with CLI options
    if provider:
        config.provider = provider
    if model:
        config.model = model
    if api_key:
        config.api_key = api_key
    if rule_categories:
        config.rules = rule_categories
    if format_opt:
        config.output_format = format_opt
    if fail_severity:
        config.fail_on_severity = fail_severity

    # Initialize LLM provider
    try:
        llm_provider = get_provider(
            config.provider,
            model=config.model,
            api_key=config.api_key,
            base_url=config.base_url,
        )
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    # Load rules
    rules_dict = load_rules()
    rules_context = build_rules_context(rules_dict, config.rules)

    # Create reviewer
    reviewer = CodeReviewer(
        provider=llm_provider,
        rules_context=rules_context,
        categories=config.rules,
        console=console,
    )

    # Run review
    console.print("[cyan]Analyzing code...[/cyan]")
    report = reviewer.review_diff(diff_text)

    # Format output
    output_str = format_report(report, config.output_format)

    # Write or print output
    if output:
        output.write_text(output_str)
        console.print(f"[green]Report written to {output}[/green]")
    else:
        console.print(output_str)

    # Print summary
    console.print(f"\n[bold]Total Findings: {len(report.findings)}[/bold]")
    if report.max_severity:
        severity_str = f"{report.max_severity.label} {report.max_severity.icon}"
        console.print(f"[bold]Max Severity: {severity_str}[/bold]")

    # Check fail threshold
    if config.fail_on_severity and report.findings_at_or_above(config.fail_on_severity):
        console.print(
            f"[red]Findings at or above {config.fail_on_severity.label} found.[/red]"
        )
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
