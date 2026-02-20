# CodeGuard

AI-powered code review CLI and GitHub Action for security, performance, and bug analysis using LLMs.

## Features

- **LLM-Powered Analysis**: Leverage OpenAI, Anthropic, or local Ollama models for intelligent code review
- **Multi-Format Output**: Table (default), JSON, Markdown, and SARIF 2.1.0
- **Built-in Knowledge Base**: CWE and OWASP top vulnerabilities reference
- **Diff-Aware**: Reviews only the changed lines in diffs
- **GitHub Action**: Seamless CI/CD integration for pull requests
- **Flexible Providers**: Support for OpenAI (GPT-4), Anthropic (Claude), and Ollama (local models)

## Installation

### Via pip

```bash
pip install codeguard
```

### With optional provider support

```bash
# For OpenAI
pip install codeguard[openai]

# For Anthropic
pip install codeguard[anthropic]

# All providers
pip install codeguard[all]
```

## Quick Start

### CLI Usage

Review a diff file:

```bash
codeguard review --file changes.patch
```

Pipe a diff via stdin:

```bash
git diff HEAD~1 | codeguard review
```

### Provider Configuration

#### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
codeguard review --file changes.patch --provider openai --model gpt-4o
```

#### Anthropic

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
codeguard review --file changes.patch --provider anthropic --model claude-opus-4
```

#### Ollama (Local)

```bash
# Start Ollama
ollama run mistral

# Review code
codeguard review --file changes.patch --provider ollama --model mistral
```

## CLI Options

```
Usage: codeguard review [OPTIONS]

Options:
  -f, --file PATH                 Diff file to review (or use stdin)
  -p, --provider TEXT             LLM provider: openai, anthropic, ollama
                                  [default: ollama]
  -m, --model TEXT                Model name (default varies by provider)
  -k, --api-key TEXT              API key (or use env var)
  -r, --rules TEXT                Rule categories: security, performance, bugs
                                  [default: security,performance,bugs]
  -o, --format TEXT               Output format: table, json, markdown, sarif
                                  [default: table]
  --output PATH                   Write output to file
  --fail-on-severity TEXT         Exit with code 1 if findings >= severity
                                  (e.g., HIGH, CRITICAL)
  -v, --version                   Show version
  --help                          Show this message and exit.
```

## GitHub Action

### Basic Usage

```yaml
name: CodeGuard Review

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

      - uses: bertrandmbanwi/codeguard/action@v0.1.0
        with:
          provider: openai
          api-key: ${{ secrets.OPENAI_API_KEY }}
          fail-on-severity: CRITICAL
```

### Action Inputs

- `provider`: LLM provider (openai, anthropic, ollama) - default: ollama
- `model`: Model name - optional
- `api-key`: API key - optional (reads from env if not set)
- `rules`: Rule categories (comma-separated) - default: security,performance,bugs
- `format`: Output format (table, json, markdown, sarif) - default: markdown
- `fail-on-severity`: Exit with error if findings >= severity - optional
- `upload-sarif`: Upload SARIF to GitHub code scanning - default: true

## Output Formats

### Table (Default)

```
                        Code Review Findings
┏━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Severity   ┃ Categor ┃ Title   ┃ File:Li ┃ Description     ┃
┡━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ ✖ CRITICAL │ securit │ SQL Inj │ app.py: │ SQL injection v │
└────────────┴─────────┴─────────┴─────────┴─────────────────┘

Total: 1 | CRITICAL: 1 | HIGH: 0 | MEDIUM: 0 | LOW: 0 | INFO: 0
```

### JSON

```json
{
  "findings": [
    {
      "title": "SQL Injection Vulnerability",
      "severity": "CRITICAL",
      "category": "security",
      "description": "...",
      "suggestion": "...",
      "file_path": "app.py",
      "line_number": 5,
      "cwe_id": "CWE-89",
      "owasp_ref": "A03:2021"
    }
  ],
  "metadata": { ... },
  "summary": { ... }
}
```

### Markdown

```markdown
# Code Review Report

**Total Findings:** 1

## Summary by Severity

- ![CRITICAL](https://img.shields.io/badge/CRITICAL-B71C1C?style=flat-square) **1**

## Findings

### 1. SQL Injection Vulnerability

- **Severity:** ![CRITICAL](https://img.shields.io/badge/CRITICAL-B71C1C?style=flat-square)
- **Category:** security
- **File:** app.py
- **Line:** 5
- **CWE:** CWE-89
- **OWASP:** A03:2021

**Description:**
SQL injection vulnerability allowing attackers to execute arbitrary SQL commands.

**Suggestion:**
Use parameterized queries or prepared statements.
```

### SARIF

SARIF 2.1.0 format compatible with GitHub code scanning, GitLab SAST, and other tools.

## Configuration

Environment variables:

```bash
# LLM Provider
export CODEGUARD_LLM_PROVIDER=openai
export CODEGUARD_MODEL=gpt-4o
export CODEGUARD_API_KEY=sk-...

# Rules
export CODEGUARD_RULES=security,performance,bugs

# Output
export CODEGUARD_FORMAT=table
export CODEGUARD_FAIL_ON_SEVERITY=HIGH
```

## Severity Levels

| Level | Description |
|-------|-------------|
| ![CRITICAL](https://img.shields.io/badge/CRITICAL-B71C1C?style=flat-square) | Security vulnerability or data loss risk |
| ![HIGH](https://img.shields.io/badge/HIGH-E53935?style=flat-square) | Major bug or significant performance issue |
| ![MEDIUM](https://img.shields.io/badge/MEDIUM-ED8B00?style=flat-square) | Moderate issue affecting functionality |
| ![LOW](https://img.shields.io/badge/LOW-F5C518?style=flat-square) | Minor issue or improvement opportunity |
| ![INFO](https://img.shields.io/badge/INFO-5B9BD5?style=flat-square) | Informational, best practice recommendation |

## Rule Categories

- **security**: Security vulnerabilities (SQL injection, XSS, etc.)
- **performance**: Performance and efficiency issues
- **bugs**: Logic errors and bugs
- **style**: Code style and best practices

## Built-in Knowledge Base

CodeGuard includes:

- **CWE Top 25**: Common Weakness Enumeration vulnerabilities
- **OWASP Top 10 2021**: Application security risks

These are injected into the LLM prompts to improve detection accuracy.

## Examples

### Block PRs with critical findings

```yaml
- uses: bertrandmbanwi/codeguard/action@v0.1.0
  with:
    provider: openai
    api-key: ${{ secrets.OPENAI_API_KEY }}
    fail-on-severity: CRITICAL
```

### Security-only review

```bash
codeguard review --file diff.patch --rules security
```

### Generate SARIF for GitHub code scanning

```bash
codeguard review --file diff.patch --format sarif --output report.sarif
```

## License

MIT License - Copyright 2026 Bertrand Mbanwi

## Support

For issues, feature requests, or contributions, visit the GitHub repository.
