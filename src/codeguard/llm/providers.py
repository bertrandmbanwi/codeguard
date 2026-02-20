from abc import ABC, abstractmethod

import httpx


class LLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    def review(self, system_prompt: str, user_prompt: str) -> str:
        """Send prompt to LLM and return raw response text."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider."""


class OpenAIProvider(LLMProvider):
    """OpenAI API provider using httpx."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        super().__init__(model, api_key, base_url)
        if not self.model:
            self.model = "gpt-4o-mini"
        if not self.base_url:
            self.base_url = "https://api.openai.com/v1"
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set")

    @property
    def provider_name(self) -> str:
        return "openai"

    def review(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=body,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class AnthropicProvider(LLMProvider):
    """Anthropic API provider using httpx."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        super().__init__(model, api_key, base_url)
        if not self.model:
            self.model = "claude-sonnet-4-20250514"
        if not self.base_url:
            self.base_url = "https://api.anthropic.com/v1"
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set")

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def review(self, system_prompt: str, user_prompt: str) -> str:
        """Call Anthropic API."""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        body = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }

        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=body,
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]


class OllamaProvider(LLMProvider):
    """Ollama local provider using httpx."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        super().__init__(model, api_key, base_url)
        if not self.model:
            self.model = "mistral"
        if not self.base_url:
            self.base_url = "http://localhost:11434"

    @property
    def provider_name(self) -> str:
        return "ollama"

    def review(self, system_prompt: str, user_prompt: str) -> str:
        """Call Ollama API."""
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "format": "json",
        }

        with httpx.Client(timeout=120) as client:
            response = client.post(
                f"{self.base_url}/api/chat",
                json=body,
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]


def get_provider(name: str, **kwargs) -> LLMProvider:
    """Factory function to get provider by name."""
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
    }

    cls = providers.get(name.lower())
    if not cls:
        raise ValueError(
            f"Unknown provider: {name}. Available: {', '.join(providers.keys())}"
        )

    return cls(**kwargs)
