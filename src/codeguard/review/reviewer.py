from rich.console import Console

from codeguard.common.models import CodeReviewReport
from codeguard.diff_parser.parser import UnifiedDiffParser
from codeguard.llm.prompts import PromptBuilder
from codeguard.llm.providers import LLMProvider
from codeguard.llm.structured import extract_findings


class CodeReviewer:
    """Code reviewer using LLM."""

    def __init__(
        self,
        provider: LLMProvider,
        rules_context: str,
        categories: list[str],
        console: Console | None = None,
    ):
        self.provider = provider
        self.prompt_builder = PromptBuilder(rules_context)
        self.categories = categories
        self.console = console or Console()

    def review_diff(self, diff_text: str) -> CodeReviewReport:
        """Review a diff and return findings."""
        parsed = UnifiedDiffParser.parse(diff_text)
        all_findings = []

        for file_diff in parsed.files:
            # Skip binary/uninteresting files
            if file_diff.language in ("binary", "unknown"):
                continue

            # Skip deleted files
            if file_diff.is_deleted:
                continue

            # Build hunks content
            hunk_contents = []
            for hunk in file_diff.hunks:
                if hunk.content:
                    hunk_contents.append(hunk.content)

            if not hunk_contents:
                continue

            diff_content = "\n".join(hunk_contents)

            # Build prompts
            system = self.prompt_builder.build_system_prompt(self.categories)
            user = self.prompt_builder.build_user_prompt(
                file_diff.path,
                file_diff.language,
                diff_content,
            )

            # Call LLM
            try:
                raw = self.provider.review(system, user)
                findings = extract_findings(raw)

                # Set file_path on each finding
                for f in findings:
                    f.file_path = file_diff.path

                all_findings.extend(findings)

            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Failed to review {file_diff.path}: {e}[/yellow]"
                )

        return CodeReviewReport(
            findings=all_findings,
            metadata={
                "provider": self.provider.provider_name,
                "model": self.provider.model,
                "files_reviewed": parsed.total_files,
                "categories": self.categories,
            },
        )
