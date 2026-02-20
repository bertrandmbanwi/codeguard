"""Tests for prompt building."""


from codeguard.llm.prompts import PromptBuilder


class TestPromptBuilder:
    """Tests for PromptBuilder."""

    def test_build_system_prompt(self):
        builder = PromptBuilder(rules_context="## CWE rules here")
        prompt = builder.build_system_prompt(["security"])
        assert "expert code reviewer" in prompt
        assert "CWE rules here" in prompt

    def test_system_prompt_contains_json_schema(self):
        builder = PromptBuilder(rules_context="")
        prompt = builder.build_system_prompt(["security"])
        assert '"findings"' in prompt
        assert '"severity"' in prompt
        assert '"title"' in prompt

    def test_system_prompt_severity_levels(self):
        builder = PromptBuilder(rules_context="")
        prompt = builder.build_system_prompt([])
        assert "CRITICAL" in prompt
        assert "HIGH" in prompt
        assert "MEDIUM" in prompt
        assert "LOW" in prompt
        assert "INFO" in prompt

    def test_build_user_prompt(self):
        builder = PromptBuilder(rules_context="")
        prompt = builder.build_user_prompt("app/main.py", "python", "def foo(): pass")
        assert "python" in prompt
        assert "app/main.py" in prompt
        assert "def foo(): pass" in prompt

    def test_user_prompt_format(self):
        builder = PromptBuilder(rules_context="")
        prompt = builder.build_user_prompt("test.js", "javascript", "const x = 1;")
        assert "```javascript" in prompt
        assert "const x = 1;" in prompt

    def test_rules_context_injected(self):
        rules = "CWE-89: SQL Injection\nCWE-79: XSS"
        builder = PromptBuilder(rules_context=rules)
        prompt = builder.build_system_prompt(["security"])
        assert "CWE-89: SQL Injection" in prompt
        assert "CWE-79: XSS" in prompt
