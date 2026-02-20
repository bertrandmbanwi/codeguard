# CodeGuard Quick Start Guide

## Installation

```bash
pip install -e /sessions/admiring-ecstatic-ritchie/codeguard/
```

## Basic Usage

### Review a diff file
```bash
codeguard review --file changes.patch
```

### Review via stdin
```bash
git diff HEAD~1 | codeguard review
```

## With Different LLM Providers

### OpenAI
```bash
export OPENAI_API_KEY="sk-..."
codeguard review --file diff.patch --provider openai --model gpt-4o
```

### Anthropic
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
codeguard review --file diff.patch --provider anthropic
```

### Ollama (Local)
```bash
ollama run mistral
codeguard review --file diff.patch --provider ollama
```

## Output Formats

```bash
# Table (default)
codeguard review --file diff.patch

# JSON
codeguard review --file diff.patch --format json

# Markdown
codeguard review --file diff.patch --format markdown

# SARIF
codeguard review --file diff.patch --format sarif --output report.sarif
```

## Configuring Rules

```bash
# Security only
codeguard review --file diff.patch --rules security

# Multiple categories
codeguard review --file diff.patch --rules security,performance,bugs
```

## CI/CD Integration

### GitHub Action
```yaml
- uses: bmwanwi/codeguard/action@v0.1.0
  with:
    provider: openai
    api-key: ${{ secrets.OPENAI_API_KEY }}
    fail-on-severity: CRITICAL
```

## Environment Variables

```bash
export CODEGUARD_LLM_PROVIDER=openai
export CODEGUARD_MODEL=gpt-4o
export OPENAI_API_KEY=sk-...
export CODEGUARD_RULES=security,performance,bugs
codeguard review --file diff.patch
```

## Failure Threshold

Exit with code 1 if CRITICAL or HIGH findings are found:

```bash
codeguard review --file diff.patch --fail-on-severity HIGH
```

## Key Commands

```bash
# Show version
codeguard --version

# Show all options
codeguard review --help

# Save output to file
codeguard review --file diff.patch --output report.md --format markdown
```

## Common Workflows

### Pre-commit hook
```bash
git diff --staged | codeguard review --fail-on-severity CRITICAL
```

### CI/CD pipeline
```bash
git diff origin/main..HEAD | codeguard review --format json --output review.json
```

### Generate SARIF for GitHub code scanning
```bash
git diff origin/main | codeguard review --format sarif --output sarif-report.sarif
```

## Severity Levels

| Level | Icon | Meaning |
|-------|------|---------|
| CRITICAL | 🚨 | Security vulnerability or data loss |
| HIGH | 🔴 | Major bug or performance issue |
| MEDIUM | ⚠️ | Moderate issue |
| LOW | ⚠️ | Minor issue |
| INFO | ℹ️ | Best practice suggestion |

## Rule Categories

- **security**: Security vulnerabilities (SQL injection, XSS, etc.)
- **performance**: Performance and efficiency issues
- **bugs**: Logic errors and bugs
- **style**: Code style and best practices

## Supported Languages

Python, JavaScript, TypeScript, Go, Rust, Java, Ruby, YAML, Terraform, JSON, XML, HTML, CSS, Bash, SQL, C, C++, PHP, Swift, Kotlin, and more.

## Default Models

- **OpenAI**: gpt-4o-mini
- **Anthropic**: claude-sonnet-4-20250514
- **Ollama**: mistral

## Troubleshooting

### "No diff provided"
Make sure you're piping diff or using --file:
```bash
git diff | codeguard review
# OR
codeguard review --file my.patch
```

### "OPENAI_API_KEY must be set"
Set your API key:
```bash
export OPENAI_API_KEY="sk-..."
```

### "Unable to connect to Ollama"
Make sure Ollama is running:
```bash
ollama run mistral
```

For more details, see README.md
