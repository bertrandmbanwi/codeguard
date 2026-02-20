"""Tests for knowledge base and rules loading."""



from codeguard.rules.categories import CATEGORIES, RuleCategory
from codeguard.rules.knowledge_base import build_rules_context, load_rules


class TestLoadRules:
    """Tests for YAML rules loading."""

    def test_load_rules_default(self):
        rules = load_rules()
        assert "cwe" in rules
        assert "owasp" in rules

    def test_load_cwe_rules_not_empty(self):
        rules = load_rules()
        assert len(rules["cwe"]) > 0

    def test_load_owasp_rules_not_empty(self):
        rules = load_rules()
        assert len(rules["owasp"]) > 0

    def test_cwe_rule_structure(self):
        rules = load_rules()
        cwe = rules["cwe"][0]
        assert "id" in cwe
        assert "title" in cwe
        assert "category" in cwe
        assert "severity_if_found" in cwe
        assert cwe["id"].startswith("CWE-")

    def test_owasp_rule_structure(self):
        rules = load_rules()
        owasp = rules["owasp"][0]
        assert "id" in owasp
        assert "title" in owasp

    def test_load_rules_nonexistent_dir(self, tmp_path):
        empty_dir = tmp_path / "nonexistent"
        empty_dir.mkdir()
        rules = load_rules(empty_dir)
        assert rules == {}

    def test_load_rules_partial(self, tmp_path):
        # Only CWE file exists
        cwe_file = tmp_path / "cwe.yaml"
        cwe_file.write_text("cwe_rules:\n  - id: CWE-89\n    title: SQL Injection\n")
        rules = load_rules(tmp_path)
        assert "cwe" in rules
        assert "owasp" not in rules


class TestBuildRulesContext:
    """Tests for rules context formatting."""

    def test_build_rules_context_includes_header(self):
        rules = load_rules()
        ctx = build_rules_context(rules, ["security"])
        assert "Security Knowledge Base" in ctx

    def test_build_rules_context_includes_cwe(self):
        rules = load_rules()
        ctx = build_rules_context(rules, ["security"])
        assert "CWE" in ctx

    def test_build_rules_context_includes_owasp(self):
        rules = load_rules()
        ctx = build_rules_context(rules, ["security"])
        assert "OWASP" in ctx

    def test_build_rules_context_filters_by_category(self):
        rules = {
            "cwe": [
                {
                    "id": "CWE-89", "title": "SQLi",
                    "category": "security",
                    "severity_if_found": "CRITICAL",
                    "description": "SQL injection",
                },
                {
                    "id": "CWE-400", "title": "Resource",
                    "category": "performance",
                    "severity_if_found": "HIGH",
                    "description": "Resource consumption",
                },
            ],
            "owasp": [],
        }
        ctx = build_rules_context(rules, ["security"])
        assert "CWE-89" in ctx
        # Performance rules filtered out when only security category
        assert "CWE-400" not in ctx

    def test_build_rules_context_empty_rules(self):
        ctx = build_rules_context({}, ["security"])
        assert "Security Knowledge Base" in ctx


class TestCategories:
    """Tests for rule categories."""

    def test_all_categories_present(self):
        assert "security" in CATEGORIES
        assert "performance" in CATEGORIES
        assert "bugs" in CATEGORIES
        assert "style" in CATEGORIES

    def test_category_structure(self):
        cat = CATEGORIES["security"]
        assert isinstance(cat, RuleCategory)
        assert cat.name == "security"
        assert cat.enabled is True
        assert cat.description != ""
