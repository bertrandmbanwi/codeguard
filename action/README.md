# CodeGuard GitHub Action

AI-powered code review GitHub Action using LLMs for security, performance, and bug analysis.

## Usage

Add the following to your workflow file (e.g., `.github/workflows/review.yml`):

```yaml
name: Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: CodeGuard Review
        uses: bmwanwi/codeguard/action@v0.1.0
        with:
          provider: openai
          api-key: ${{ secrets.OPENAI_API_KEY }}
          rules: security,performance,bugs
          fail-on-severity: HIGH
```

## Inputs

- **provider**: LLM provider (`openai`, `anthropic`, `ollama`) - default: `ollama`
- **model**: Model name (optional, provider-dependent)
- **api-key**: API key for the provider (optional, reads from env if not set)
- **rules**: Rule categories to check (comma-separated) - default: `security,performance,bugs`
- **format**: Output format (`table`, `json`, `markdown`, `sarif`) - default: `markdown`
- **fail-on-severity**: Exit with error if findings at or above this severity (optional)
- **upload-sarif**: Upload SARIF report to code scanning - default: `true`

## Examples

### Using OpenAI

```yaml
- uses: bmwanwi/codeguard/action@v0.1.0
  with:
    provider: openai
    model: gpt-4o
    api-key: ${{ secrets.OPENAI_API_KEY }}
    fail-on-severity: CRITICAL
```

### Using Anthropic

```yaml
- uses: bmwanwi/codeguard/action@v0.1.0
  with:
    provider: anthropic
    model: claude-opus-4
    api-key: ${{ secrets.ANTHROPIC_API_KEY }}
    rules: security
```

### Using Local Ollama

```yaml
- uses: bmwanwi/codeguard/action@v0.1.0
  with:
    provider: ollama
    model: mistral
```
