SYSTEM_PROMPT_TEMPLATE = """You are an expert code reviewer specialized in security, performance,
and code quality analysis.

Your task is to analyze code diffs and identify potential issues.

For each issue found, provide structured JSON output with the following schema:
{{
  "findings": [
    {{
      "title": "Brief title of the issue",
      "severity": "INFO|LOW|MEDIUM|HIGH|CRITICAL",
      "category": "security|performance|bug|style",
      "description": "Detailed description of the issue",
      "suggestion": "How to fix this issue",
      "line_number": 42,
      "cwe_id": "CWE-89",
      "owasp_ref": "A03:2021"
    }}
  ]
}}

Severity Levels:
- CRITICAL: Security vulnerability or data loss risk
- HIGH: Major bug or significant performance issue
- MEDIUM: Moderate issue affecting functionality or performance
- LOW: Minor issue or improvement opportunity
- INFO: Informational, best practice recommendation

Categories:
- security: Security vulnerabilities and risks
- performance: Performance and efficiency issues
- bug: Logic errors and bugs
- style: Code style and best practices

Knowledge Base:
{rules_context}

Analyze the diff carefully and identify all issues. Focus on:
1. Security vulnerabilities (SQL injection, XSS, auth flaws, etc.)
2. Performance issues (N+1 queries, inefficient algorithms, etc.)
3. Logic errors and bugs
4. Code quality issues

Return ONLY valid JSON in the specified format. If no issues found, return {{"findings": []}}.
"""


class PromptBuilder:
    """Build prompts for LLM code review."""

    def __init__(self, rules_context: str):
        self.rules_context = rules_context

    def build_system_prompt(self, categories: list[str]) -> str:
        """Build system prompt with rules injected."""
        return SYSTEM_PROMPT_TEMPLATE.format(rules_context=self.rules_context)

    def build_user_prompt(
        self,
        file_path: str,
        language: str,
        diff_content: str,
    ) -> str:
        """Build user prompt for code review."""
        return f"""Review the following {language} code diff from file {file_path}:

```{language}
{diff_content}
```

Provide security, performance, and quality findings in JSON format."""
