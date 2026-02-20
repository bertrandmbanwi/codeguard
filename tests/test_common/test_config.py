"""Tests for configuration loading."""

import os
from unittest.mock import patch

from codeguard.common.config import CodeguardConfig, load_config
from codeguard.common.severity import Severity


class TestCodeguardConfig:
    """Tests for CodeguardConfig."""

    def test_default_config(self):
        config = CodeguardConfig(provider="ollama")
        assert config.provider == "ollama"
        assert config.model is None
        assert config.api_key is None
        assert config.rules == ["security", "performance", "bugs"]
        assert config.output_format == "table"
        assert config.fail_on_severity is None

    def test_config_with_all_fields(self):
        config = CodeguardConfig(
            provider="openai",
            model="gpt-4o",
            api_key="sk-test",
            base_url="https://api.openai.com/v1",
            rules=["security"],
            output_format="json",
            fail_on_severity=Severity.HIGH,
        )
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.fail_on_severity == Severity.HIGH

    def test_config_default_rules_post_init(self):
        config = CodeguardConfig(provider="ollama", rules=None)
        assert config.rules == ["security", "performance", "bugs"]


class TestLoadConfig:
    """Tests for load_config from environment."""

    @patch.dict(os.environ, {}, clear=True)
    def test_load_config_defaults(self):
        config = load_config()
        assert config.provider == "ollama"
        assert config.model is None
        assert config.api_key is None
        assert config.output_format == "table"

    @patch.dict(os.environ, {
        "CODEGUARD_LLM_PROVIDER": "openai",
        "OPENAI_API_KEY": "sk-test-123",
        "CODEGUARD_MODEL": "gpt-4o-mini",
        "CODEGUARD_FORMAT": "json",
        "CODEGUARD_RULES": "security",
    }, clear=True)
    def test_load_config_from_env(self):
        config = load_config()
        assert config.provider == "openai"
        assert config.api_key == "sk-test-123"
        assert config.model == "gpt-4o-mini"
        assert config.output_format == "json"
        assert config.rules == ["security"]

    @patch.dict(os.environ, {
        "ANTHROPIC_API_KEY": "sk-ant-test",
    }, clear=True)
    def test_load_config_anthropic_key(self):
        config = load_config()
        assert config.api_key == "sk-ant-test"

    @patch.dict(os.environ, {
        "CODEGUARD_API_KEY": "custom-key",
    }, clear=True)
    def test_load_config_custom_key(self):
        config = load_config()
        assert config.api_key == "custom-key"

    @patch.dict(os.environ, {
        "CODEGUARD_FAIL_ON_SEVERITY": "HIGH",
    }, clear=True)
    def test_load_config_fail_on_severity(self):
        config = load_config()
        assert config.fail_on_severity == Severity.HIGH

    @patch.dict(os.environ, {
        "CODEGUARD_FAIL_ON_SEVERITY": "INVALID",
    }, clear=True)
    def test_load_config_invalid_severity_ignored(self):
        config = load_config()
        assert config.fail_on_severity is None

    @patch.dict(os.environ, {
        "CODEGUARD_RULES": "security, performance, bugs, style",
    }, clear=True)
    def test_load_config_multiple_rules(self):
        config = load_config()
        assert len(config.rules) == 4
        assert "security" in config.rules
        assert "style" in config.rules
