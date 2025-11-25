"""Guardrail store for safety testing and content moderation rules."""

import json
import os
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class GuardrailRule(BaseModel):
    """A single guardrail rule definition."""
    id: int = 0
    name: str
    description: str = ""
    type: str  # "pii", "content", "keyword", "regex", "llm"
    enabled: bool = True
    
    # Rule configuration based on type
    # pii: {"detect": ["email", "phone", "ssn", "credit_card", "address"]}
    # content: {"categories": ["violence", "adult", "hate", "self-harm"]}
    # keyword: {"keywords": ["bad", "words"], "mode": "block|warn"}
    # regex: {"patterns": [{"pattern": "...", "name": "..."}]}
    # llm: {"prompt": "Check if this text is safe...", "threshold": 0.7}
    config: Dict[str, Any] = {}
    
    created_at: str = ""
    updated_at: str = ""


class GuardrailTest(BaseModel):
    """A test case for guardrails."""
    id: int = 0
    name: str
    description: str = ""
    input_text: str
    expected_blocked: bool = False
    expected_flags: List[str] = []  # Expected rule IDs or names to trigger
    tags: List[str] = []
    created_at: str = ""


class GuardrailTestResult(BaseModel):
    """Result of running guardrails on an input."""
    input_text: str
    blocked: bool = False
    flags: List[Dict[str, Any]] = []  # [{"rule_id": 1, "rule_name": "...", "type": "...", "matches": [...], "severity": "..."}]
    passed_rules: List[str] = []
    execution_time_ms: float = 0.0
    timestamp: str = ""


class GuardrailTestRun(BaseModel):
    """A complete test run against guardrails."""
    id: int = 0
    name: str = ""
    rule_ids: List[int] = []  # Which rules were active
    test_ids: List[int] = []  # Which test cases were run
    results: List[Dict[str, Any]] = []  # Test results with pass/fail status
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    created_at: str = ""


class GuardrailStore:
    """Store for guardrail rules with file persistence."""
    
    def __init__(self, file_path: str = "app/data/guardrails.json"):
        self.file_path = file_path
        self._rules: List[GuardrailRule] = []
        self._next_id = 1
        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                self._rules = [GuardrailRule(**r) for r in data.get("rules", [])]
                self._next_id = data.get("next_id", 1)
            except Exception:
                self._rules = []
                self._next_id = 1
        else:
            # Add default rules
            self._init_default_rules()

    def _save(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w") as f:
            json.dump({
                "rules": [r.model_dump() for r in self._rules],
                "next_id": self._next_id,
            }, f, indent=2)

    def _init_default_rules(self):
        """Initialize with default guardrail rules."""
        defaults = [
            GuardrailRule(
                id=1,
                name="PII Detector",
                description="Detect personally identifiable information like emails, phones, SSNs",
                type="pii",
                enabled=True,
                config={
                    "detect": ["email", "phone", "ssn", "credit_card"],
                    "mode": "warn"
                },
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            ),
            GuardrailRule(
                id=2,
                name="Profanity Filter",
                description="Block or warn on profane language",
                type="keyword",
                enabled=True,
                config={
                    "keywords": ["damn", "hell", "crap"],  # Mild examples
                    "mode": "warn",
                    "case_sensitive": False
                },
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            ),
            GuardrailRule(
                id=3,
                name="URL/Link Detector",
                description="Detect URLs and links in text",
                type="regex",
                enabled=True,
                config={
                    "patterns": [
                        {"name": "URL", "pattern": r"https?://[^\s<>\"{}|\\^`\[\]]+"},
                        {"name": "Email Link", "pattern": r"mailto:[^\s<>\"{}|\\^`\[\]]+"}
                    ],
                    "mode": "warn"
                },
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            ),
            GuardrailRule(
                id=4,
                name="Code Injection Pattern",
                description="Detect potential code injection patterns",
                type="regex",
                enabled=True,
                config={
                    "patterns": [
                        {"name": "SQL Injection", "pattern": r"(?i)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION)\s+.*(FROM|INTO|SET|TABLE|WHERE)"},
                        {"name": "Script Tag", "pattern": r"<script[^>]*>.*?</script>"},
                        {"name": "System Command", "pattern": r"(?i)(rm\s+-rf|sudo|chmod|chown|wget|curl)\s+"}
                    ],
                    "mode": "block"
                },
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            ),
        ]
        self._rules = defaults
        self._next_id = 5
        self._save()

    def list_all(self) -> List[GuardrailRule]:
        return self._rules

    def list_enabled(self) -> List[GuardrailRule]:
        return [r for r in self._rules if r.enabled]

    def get(self, rule_id: int) -> Optional[GuardrailRule]:
        for rule in self._rules:
            if rule.id == rule_id:
                return rule
        return None

    def create(self, name: str, type: str, config: Dict[str, Any], 
               description: str = "", enabled: bool = True) -> GuardrailRule:
        rule = GuardrailRule(
            id=self._next_id,
            name=name,
            description=description,
            type=type,
            enabled=enabled,
            config=config,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        self._rules.append(rule)
        self._next_id += 1
        self._save()
        return rule

    def update(self, rule_id: int, **kwargs) -> Optional[GuardrailRule]:
        for i, rule in enumerate(self._rules):
            if rule.id == rule_id:
                data = rule.model_dump()
                data.update(kwargs)
                data["updated_at"] = datetime.now().isoformat()
                self._rules[i] = GuardrailRule(**data)
                self._save()
                return self._rules[i]
        return None

    def delete(self, rule_id: int) -> bool:
        for i, rule in enumerate(self._rules):
            if rule.id == rule_id:
                del self._rules[i]
                self._save()
                return True
        return False

    def toggle(self, rule_id: int) -> Optional[GuardrailRule]:
        for i, rule in enumerate(self._rules):
            if rule.id == rule_id:
                self._rules[i].enabled = not self._rules[i].enabled
                self._rules[i].updated_at = datetime.now().isoformat()
                self._save()
                return self._rules[i]
        return None


class GuardrailTestStore:
    """Store for guardrail test cases."""
    
    def __init__(self, file_path: str = "app/data/guardrail_tests.json"):
        self.file_path = file_path
        self._tests: List[GuardrailTest] = []
        self._next_id = 1
        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                self._tests = [GuardrailTest(**t) for t in data.get("tests", [])]
                self._next_id = data.get("next_id", 1)
            except Exception:
                self._tests = []
                self._next_id = 1
        else:
            # Add default test cases
            self._init_default_tests()

    def _save(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w") as f:
            json.dump({
                "tests": [t.model_dump() for t in self._tests],
                "next_id": self._next_id,
            }, f, indent=2)

    def _init_default_tests(self):
        """Initialize with default test cases."""
        defaults = [
            GuardrailTest(
                id=1,
                name="Email PII Test",
                description="Tests email detection",
                input_text="Contact me at john.doe@example.com for more info.",
                expected_blocked=False,
                expected_flags=["PII Detector"],
                tags=["pii", "email"],
                created_at=datetime.now().isoformat(),
            ),
            GuardrailTest(
                id=2,
                name="Phone Number Test",
                description="Tests phone number detection",
                input_text="Call me at 555-123-4567 or (555) 987-6543.",
                expected_blocked=False,
                expected_flags=["PII Detector"],
                tags=["pii", "phone"],
                created_at=datetime.now().isoformat(),
            ),
            GuardrailTest(
                id=3,
                name="Clean Text",
                description="Normal text that should pass all guardrails",
                input_text="The weather is nice today. How can I help you?",
                expected_blocked=False,
                expected_flags=[],
                tags=["clean", "safe"],
                created_at=datetime.now().isoformat(),
            ),
            GuardrailTest(
                id=4,
                name="SQL Injection Pattern",
                description="Tests SQL injection detection",
                input_text="SELECT * FROM users WHERE name = 'admin'--",
                expected_blocked=True,
                expected_flags=["Code Injection Pattern"],
                tags=["security", "sql"],
                created_at=datetime.now().isoformat(),
            ),
            GuardrailTest(
                id=5,
                name="URL Detection",
                description="Tests URL detection",
                input_text="Visit https://example.com/page for details.",
                expected_blocked=False,
                expected_flags=["URL/Link Detector"],
                tags=["url", "link"],
                created_at=datetime.now().isoformat(),
            ),
        ]
        self._tests = defaults
        self._next_id = 6
        self._save()

    def list_all(self) -> List[GuardrailTest]:
        return self._tests

    def get(self, test_id: int) -> Optional[GuardrailTest]:
        for test in self._tests:
            if test.id == test_id:
                return test
        return None

    def create(self, name: str, input_text: str, expected_blocked: bool = False,
               expected_flags: List[str] = None, description: str = "",
               tags: List[str] = None) -> GuardrailTest:
        test = GuardrailTest(
            id=self._next_id,
            name=name,
            description=description,
            input_text=input_text,
            expected_blocked=expected_blocked,
            expected_flags=expected_flags or [],
            tags=tags or [],
            created_at=datetime.now().isoformat(),
        )
        self._tests.append(test)
        self._next_id += 1
        self._save()
        return test

    def update(self, test_id: int, **kwargs) -> Optional[GuardrailTest]:
        for i, test in enumerate(self._tests):
            if test.id == test_id:
                data = test.model_dump()
                data.update(kwargs)
                self._tests[i] = GuardrailTest(**data)
                self._save()
                return self._tests[i]
        return None

    def delete(self, test_id: int) -> bool:
        for i, test in enumerate(self._tests):
            if test.id == test_id:
                del self._tests[i]
                self._save()
                return True
        return False


class GuardrailEngine:
    """Engine to run guardrail checks on text."""
    
    # PII patterns
    PII_PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        "ssn": r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
        "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "date_of_birth": r"\b(?:0?[1-9]|1[0-2])[-/](?:0?[1-9]|[12]\d|3[01])[-/](?:19|20)\d{2}\b",
    }

    @classmethod
    def check_text(cls, text: str, rules: List[GuardrailRule]) -> GuardrailTestResult:
        """Run all enabled guardrail rules against the input text."""
        import time
        start = time.time()
        
        flags = []
        passed_rules = []
        blocked = False
        
        for rule in rules:
            if not rule.enabled:
                continue
                
            matches = cls._check_rule(text, rule)
            
            if matches:
                mode = rule.config.get("mode", "warn")
                if mode == "block":
                    blocked = True
                    
                flags.append({
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "type": rule.type,
                    "matches": matches,
                    "severity": "block" if mode == "block" else "warn",
                })
            else:
                passed_rules.append(rule.name)
        
        end = time.time()
        
        return GuardrailTestResult(
            input_text=text,
            blocked=blocked,
            flags=flags,
            passed_rules=passed_rules,
            execution_time_ms=(end - start) * 1000,
            timestamp=datetime.now().isoformat(),
        )

    @classmethod
    def _check_rule(cls, text: str, rule: GuardrailRule) -> List[Dict[str, Any]]:
        """Check a single rule against text. Returns list of matches."""
        matches = []
        
        if rule.type == "pii":
            detect_types = rule.config.get("detect", [])
            for pii_type in detect_types:
                pattern = cls.PII_PATTERNS.get(pii_type)
                if pattern:
                    found = re.findall(pattern, text, re.IGNORECASE)
                    for match in found:
                        # Mask the matched value for display
                        masked = cls._mask_pii(match, pii_type)
                        matches.append({
                            "type": pii_type,
                            "value": masked,
                            "original_length": len(match)
                        })
        
        elif rule.type == "keyword":
            keywords = rule.config.get("keywords", [])
            case_sensitive = rule.config.get("case_sensitive", False)
            check_text = text if case_sensitive else text.lower()
            
            for keyword in keywords:
                check_kw = keyword if case_sensitive else keyword.lower()
                if check_kw in check_text:
                    matches.append({
                        "type": "keyword",
                        "value": keyword,
                        "count": check_text.count(check_kw)
                    })
        
        elif rule.type == "regex":
            patterns = rule.config.get("patterns", [])
            for p in patterns:
                pattern = p.get("pattern", "")
                name = p.get("name", "Pattern")
                try:
                    found = re.findall(pattern, text, re.IGNORECASE)
                    for match in found:
                        matches.append({
                            "type": "regex",
                            "pattern_name": name,
                            "value": match if isinstance(match, str) else str(match)
                        })
                except re.error:
                    pass  # Invalid regex, skip
        
        elif rule.type == "content":
            # Content moderation would typically use an LLM or API
            # For now, just check for some basic patterns
            categories = rule.config.get("categories", [])
            # This is a placeholder - in production, use an actual content moderation API
            pass
        
        return matches

    @classmethod
    def _mask_pii(cls, value: str, pii_type: str) -> str:
        """Mask PII for safe display."""
        if pii_type == "email":
            parts = value.split("@")
            if len(parts) == 2:
                user = parts[0]
                domain = parts[1]
                masked_user = user[0] + "*" * (len(user) - 1) if len(user) > 1 else "*"
                return f"{masked_user}@{domain}"
        elif pii_type == "phone":
            digits = re.sub(r"\D", "", value)
            return "***-***-" + digits[-4:] if len(digits) >= 4 else "***"
        elif pii_type == "ssn":
            return "***-**-" + value[-4:]
        elif pii_type == "credit_card":
            digits = re.sub(r"\D", "", value)
            return "**** **** **** " + digits[-4:] if len(digits) >= 4 else "****"
        return "*" * len(value)
