# CodeGuard Project Structure

```
codeguard/
├── src/codeguard/
│   ├── __init__.py                    # Package initialization, __version__ = "0.1.0"
│   ├── __main__.py                    # CLI entry point (python -m codeguard)
│   ├── cli.py                         # Typer CLI with review command (220 lines)
│   │
│   ├── common/                        # Common utilities and models
│   │   ├── __init__.py
│   │   ├── severity.py                # Severity IntEnum with properties
│   │   ├── models.py                  # Finding and CodeReviewReport dataclasses
│   │   ├── config.py                  # Configuration and environment loading
│   │   └── reporter.py                # Output formatters (table, JSON, markdown, SARIF)
│   │
│   ├── diff_parser/                   # Unified diff parsing
│   │   ├── __init__.py
│   │   ├── models.py                  # DiffHunk, FileDiff, ParsedDiff dataclasses
│   │   └── parser.py                  # UnifiedDiffParser with language detection
│   │
│   ├── llm/                           # LLM provider abstraction
│   │   ├── __init__.py
│   │   ├── providers.py               # OpenAI, Anthropic, Ollama providers (httpx)
│   │   ├── prompts.py                 # System and user prompt builders
│   │   └── structured.py              # JSON parsing and validation
│   │
│   ├── rules/                         # Security rules knowledge base
│   │   ├── __init__.py
│   │   ├── categories.py              # Rule categories (security, performance, bugs)
│   │   ├── knowledge_base.py          # Load and format rules
│   │   ├── cwe.yaml                   # 15 CWE vulnerability patterns
│   │   └── owasp.yaml                 # 10 OWASP Top 10 2021 items
│   │
│   └── review/                        # Code review engine
│       ├── __init__.py
│       └── reviewer.py                # CodeReviewer class orchestrating review
│
├── rules/                             # Packaged rules (copied to src/)
│   ├── cwe.yaml
│   └── owasp.yaml
│
├── action/                            # GitHub Action
│   ├── action.yml                     # Composite action definition
│   └── README.md                      # Action usage guide
│
├── .github/
│   └── workflows/
│       └── ci.yml                     # CI/CD pipeline (lint, test on Python 3.10-3.13)
│
├── pyproject.toml                     # Project metadata and configuration
├── README.md                          # Main documentation
├── CHANGELOG.md                       # Version history
├── LICENSE                            # MIT license
├── .gitignore                         # Python .gitignore
└── STRUCTURE.md                       # This file
```

## Module Organization

### Common Module (`src/codeguard/common/`)
- **severity.py**: Severity enum (INFO=1, LOW=2, MEDIUM=4, HIGH=7, CRITICAL=10)
  - Properties: `label`, `color`, `icon`
  - Method: `from_string()`

- **models.py**: Data models
  - `Finding`: Individual code issue with all metadata
  - `CodeReviewReport`: Collection of findings with metadata and analytics

- **config.py**: Configuration management
  - `CodeguardConfig`: Configuration object
  - `load_config()`: Load from environment variables

- **reporter.py**: Output formatting
  - `render_table()`: Rich formatted table
  - `render_json()`: JSON format
  - `render_markdown()`: Markdown format
  - `render_sarif()`: SARIF 2.1.0 format
  - `format_report()`: Dispatcher

### Diff Parser Module (`src/codeguard/diff_parser/`)
- **models.py**: Domain objects for diff representation
  - `DiffHunk`: Single hunk in a file diff
  - `FileDiff`: Diff for one file
  - `ParsedDiff`: Collection of file diffs

- **parser.py**: Parsing logic
  - `UnifiedDiffParser.parse()`: Main parsing method
  - `UnifiedDiffParser.detect_language()`: File extension → language mapping
  - Supports: Python, JavaScript, TypeScript, Go, Rust, Java, Ruby, YAML, Terraform, JSON, XML, HTML, CSS, Bash, SQL, C, C++, PHP, Swift, Kotlin

### LLM Module (`src/codeguard/llm/`)
- **providers.py**: LLM provider implementations
  - `LLMProvider`: Abstract base class
  - `OpenAIProvider`: GPT-4o-mini (default)
  - `AnthropicProvider`: Claude Sonnet 4 (default)
  - `OllamaProvider`: Local models, Mistral (default)
  - Uses `httpx` for HTTP calls (minimal dependencies)

- **prompts.py**: Prompt engineering
  - `SYSTEM_PROMPT_TEMPLATE`: Defines role, format, severity levels
  - `PromptBuilder`: Injects rules, builds prompts

- **structured.py**: Response processing
  - `parse_llm_response()`: Extract JSON from LLM output
  - `validate_finding()`: Convert dict to Finding
  - `extract_findings()`: Combined parse + validate

### Rules Module (`src/codeguard/rules/`)
- **categories.py**: Rule categorization
  - `RuleCategory`: Category definition
  - `CATEGORIES`: Dict of available categories

- **knowledge_base.py**: Rule management
  - `load_rules()`: Load YAML files
  - `build_rules_context()`: Format for prompt injection

- **cwe.yaml**: Common Weakness Enumeration (15 rules)
  - SQL Injection (CWE-89), XSS (CWE-79), OS Command Injection (CWE-78)
  - Path Traversal (CWE-22), Hardcoded Credentials (CWE-798)
  - Unsafe Deserialization (CWE-502), Missing Auth (CWE-306)
  - Information Disclosure (CWE-200), Resource Exhaustion (CWE-400)
  - SSRF (CWE-918), File Upload (CWE-434), Trust Boundary (CWE-501)
  - Improper Auth (CWE-287), Null Pointer (CWE-476), Integer Overflow (CWE-190)

- **owasp.yaml**: OWASP Top 10 2021 (10 rules)
  - A01: Broken Access Control
  - A02: Cryptographic Failures
  - A03: Injection
  - A04: Insecure Design
  - A05: Security Misconfiguration
  - A06: Vulnerable Components
  - A07: Auth/Session Failures
  - A08: Integrity Failures
  - A09: Logging/Monitoring Failures
  - A10: SSRF

### Review Module (`src/codeguard/review/`)
- **reviewer.py**: Main review orchestration
  - `CodeReviewer`: Coordinates diff parsing, LLM calls, finding extraction
  - `review_diff()`: Main entry point

## Key Design Patterns

1. **Dataclasses**: All models use dataclasses (Finding, CodeReviewReport, etc.)
2. **Type Hints**: Full type annotations throughout
3. **Factory Pattern**: `get_provider()` for LLM instantiation
4. **Template Method**: `PromptBuilder` for prompt construction
5. **Strategy Pattern**: Different reporters for different output formats
6. **Parser Pattern**: `UnifiedDiffParser` for diff parsing

## Dependencies

### Core
- `typer>=0.12.0`: CLI framework
- `rich>=13.0.0`: Rich terminal output
- `httpx>=0.27.0`: HTTP client
- `pyyaml>=6.0`: YAML parsing

### Optional
- `openai>=1.0.0`: For OpenAI integration (not used - httpx instead)
- `anthropic>=0.40.0`: For Anthropic integration (not used - httpx instead)

### Development
- `pytest>=8.0`: Testing
- `pytest-cov>=5.0`: Coverage reporting
- `ruff>=0.5.0`: Linting and formatting

## Code Quality

- **Line Length**: 100 characters max
- **Linting**: Ruff (E, F, I, W rules)
- **Python Version**: 3.10+
- **Type Checking**: Full type hints
- **Documentation**: Docstrings on classes and key functions
- **Error Handling**: Graceful error handling with informative messages

## Configuration

Environment variables:
- `CODEGUARD_LLM_PROVIDER`: Provider name (default: ollama)
- `CODEGUARD_MODEL`: Model name (provider-dependent)
- `CODEGUARD_API_KEY`: API key
- `CODEGUARD_BASE_URL`: Provider base URL
- `CODEGUARD_RULES`: Comma-separated rule categories
- `CODEGUARD_FORMAT`: Output format (default: table)
- `CODEGUARD_FAIL_ON_SEVERITY`: Failure threshold

Legacy env vars:
- `OPENAI_API_KEY`: For OpenAI
- `ANTHROPIC_API_KEY`: For Anthropic

## CLI Interface

```
codeguard [OPTIONS] COMMAND

Commands:
  review    Review code diff using LLM

Options:
  -f, --file PATH                 Diff file to review
  -p, --provider TEXT             LLM provider (openai, anthropic, ollama)
  -m, --model TEXT                Model name
  -k, --api-key TEXT              API key
  -r, --rules TEXT                Rule categories (comma-separated)
  -o, --format TEXT               Output format (table, json, markdown, sarif)
  --output PATH                   Write output to file
  --fail-on-severity TEXT         Exit 1 if findings >= severity
  -v, --version                   Show version
```

## GitHub Action

Inputs:
- `provider`: LLM provider (default: ollama)
- `model`: Model name (optional)
- `api-key`: API key (optional)
- `rules`: Rule categories (default: security,performance,bugs)
- `format`: Output format (default: markdown)
- `fail-on-severity`: Failure threshold (optional)
- `upload-sarif`: Upload to code scanning (default: true)

## Testing

Structure is ready for pytest:
- Tests would go in `tests/` directory
- Coverage reporting to Codecov
- Matrix testing: Python 3.10, 3.11, 3.12, 3.13
