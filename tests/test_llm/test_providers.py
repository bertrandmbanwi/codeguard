"""Tests for LLM providers."""

from unittest.mock import MagicMock, patch

import pytest

from codeguard.llm.providers import (
    AnthropicProvider,
    OllamaProvider,
    OpenAIProvider,
    get_provider,
)


class TestOpenAIProvider:
    """Tests for OpenAI provider."""

    def test_requires_api_key(self):
        with pytest.raises(ValueError, match="OPENAI_API_KEY must be set"):
            OpenAIProvider(api_key=None)

    def test_default_model(self):
        provider = OpenAIProvider(api_key="sk-test")
        assert provider.model == "gpt-4o-mini"

    def test_custom_model(self):
        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        assert provider.model == "gpt-4o"

    def test_default_base_url(self):
        provider = OpenAIProvider(api_key="sk-test")
        assert provider.base_url == "https://api.openai.com/v1"

    def test_provider_name(self):
        provider = OpenAIProvider(api_key="sk-test")
        assert provider.provider_name == "openai"

    @patch("codeguard.llm.providers.httpx.Client")
    def test_review_call(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"findings": []}'}}]
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        provider = OpenAIProvider(api_key="sk-test")
        result = provider.review("system prompt", "user prompt")
        assert result == '{"findings": []}'

    @patch("codeguard.llm.providers.httpx.Client")
    def test_review_sends_json_format(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"findings": []}'}}]
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        provider = OpenAIProvider(api_key="sk-test")
        provider.review("sys", "usr")

        call_kwargs = mock_client.post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert body["response_format"] == {"type": "json_object"}
        assert body["temperature"] == 0.1


class TestAnthropicProvider:
    """Tests for Anthropic provider."""

    def test_requires_api_key(self):
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY must be set"):
            AnthropicProvider(api_key=None)

    def test_default_model(self):
        provider = AnthropicProvider(api_key="sk-ant-test")
        assert "claude" in provider.model

    def test_default_base_url(self):
        provider = AnthropicProvider(api_key="sk-ant-test")
        assert provider.base_url == "https://api.anthropic.com/v1"

    def test_provider_name(self):
        provider = AnthropicProvider(api_key="sk-ant-test")
        assert provider.provider_name == "anthropic"

    @patch("codeguard.llm.providers.httpx.Client")
    def test_review_call(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": [{"text": '{"findings": []}'}]
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        provider = AnthropicProvider(api_key="sk-ant-test")
        result = provider.review("system prompt", "user prompt")
        assert result == '{"findings": []}'

    @patch("codeguard.llm.providers.httpx.Client")
    def test_review_sends_anthropic_headers(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": [{"text": '{"findings": []}'}]
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        provider = AnthropicProvider(api_key="sk-ant-test")
        provider.review("sys", "usr")

        call_kwargs = mock_client.post.call_args
        headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
        assert headers["x-api-key"] == "sk-ant-test"
        assert headers["anthropic-version"] == "2023-06-01"


class TestOllamaProvider:
    """Tests for Ollama provider."""

    def test_default_model(self):
        provider = OllamaProvider()
        assert provider.model == "mistral"

    def test_default_base_url(self):
        provider = OllamaProvider()
        assert provider.base_url == "http://localhost:11434"

    def test_no_api_key_required(self):
        # Should not raise
        provider = OllamaProvider()
        assert provider.api_key is None

    def test_provider_name(self):
        provider = OllamaProvider()
        assert provider.provider_name == "ollama"

    @patch("codeguard.llm.providers.httpx.Client")
    def test_review_call(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": '{"findings": []}'}
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        provider = OllamaProvider()
        result = provider.review("system", "user")
        assert result == '{"findings": []}'

    @patch("codeguard.llm.providers.httpx.Client")
    def test_review_uses_json_format(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": '{"findings": []}'}
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        provider = OllamaProvider()
        provider.review("sys", "usr")

        call_kwargs = mock_client.post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert body["format"] == "json"
        assert body["stream"] is False


class TestGetProvider:
    """Tests for provider factory."""

    def test_get_openai(self):
        provider = get_provider("openai", api_key="sk-test")
        assert isinstance(provider, OpenAIProvider)

    def test_get_anthropic(self):
        provider = get_provider("anthropic", api_key="sk-ant-test")
        assert isinstance(provider, AnthropicProvider)

    def test_get_ollama(self):
        provider = get_provider("ollama")
        assert isinstance(provider, OllamaProvider)

    def test_get_case_insensitive(self):
        provider = get_provider("OpenAI", api_key="sk-test")
        assert isinstance(provider, OpenAIProvider)

    def test_get_unknown_provider(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("gemini")
