"""
PII Detector — LLM02: Sensitive Information Disclosure

Core engine for detecting personally identifiable information (PII) and
sensitive data in text, such as LLM outputs.
"""

import re
from dataclasses import dataclass, field
from enum import Enum


class PIIType(Enum):
    """Types of sensitive data that can be detected."""
    CREDIT_CARD = "credit_card"
    SSN = "ssn"
    EMAIL = "email"
    PHONE = "phone"
    API_KEY = "api_key"
    IP_ADDRESS = "ip_address"
    DATE_OF_BIRTH = "date_of_birth"
    PASSWORD = "password"
    ACCOUNT_NUMBER = "account_number"


@dataclass
class PIIFinding:
    """A single PII detection result."""
    pii_type: PIIType
    matched_text: str
    position: tuple[int, int]  # (start, end)
    masked_text: str = ""


@dataclass
class ScanResult:
    """Result of scanning text for PII."""
    has_pii: bool
    findings: list[PIIFinding] = field(default_factory=list)
    cleaned_text: str = ""
    summary: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# PII Pattern Definitions
# ---------------------------------------------------------------------------

PII_PATTERNS = [
    {
        "type": PIIType.CREDIT_CARD,
        "pattern": r"\b(?:\d[ -]*?){13,16}\b",
        "mask": "[CREDIT CARD REDACTED]",
        "description": "Credit card number (13-16 digits)",
    },
    {
        "type": PIIType.SSN,
        "pattern": r"\b\d{3}[-]?\d{2}[-]?\d{4}\b",
        "mask": "[SSN REDACTED]",
        "description": "Social Security Number",
    },
    {
        "type": PIIType.EMAIL,
        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "mask": "[EMAIL REDACTED]",
        "description": "Email address",
    },
    {
        "type": PIIType.PHONE,
        "pattern": r"\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b",
        "mask": "[PHONE REDACTED]",
        "description": "US phone number",
    },
    {
        "type": PIIType.API_KEY,
        "pattern": r"\b(sk-[A-Za-z0-9]{20,}|sk_live_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36})\b",
        "mask": "[API KEY REDACTED]",
        "description": "API key (OpenAI, Stripe, AWS, GitHub)",
    },
    {
        "type": PIIType.IP_ADDRESS,
        "pattern": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        "mask": "[IP ADDRESS REDACTED]",
        "description": "IPv4 address",
    },
    {
        "type": PIIType.DATE_OF_BIRTH,
        "pattern": r"(?i)(?:date\s*of\s*birth|dob|born)\s*[:.]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
        "mask": "[DATE OF BIRTH REDACTED]",
        "description": "Date of birth",
    },
    {
        "type": PIIType.PASSWORD,
        "pattern": r"(?i)(?:password|passwd|pwd)\s*[:=]\s*\S+",
        "mask": "[PASSWORD REDACTED]",
        "description": "Password in text",
    },
    {
        "type": PIIType.ACCOUNT_NUMBER,
        "pattern": r"(?i)(?:account\s*number|acct\s*no)\s*[:=]?\s*\d{6,17}",
        "mask": "[ACCOUNT NUMBER REDACTED]",
        "description": "Bank account number",
    },
]


# ---------------------------------------------------------------------------
# PII Detection Engine
# ---------------------------------------------------------------------------

class PIIDetector:
    """
    Scans text for PII and sensitive data patterns.

    Usage:
        detector = PIIDetector()
        result = detector.scan(text)
        if result.has_pii:
            print(f"Found {len(result.findings)} PII items")
            print(result.cleaned_text)  # Text with PII masked
    """

    def __init__(self):
        self.compiled_patterns = []
        for pat_def in PII_PATTERNS:
            self.compiled_patterns.append({
                "type": pat_def["type"],
                "regex": re.compile(pat_def["pattern"]),
                "mask": pat_def["mask"],
            })

    def scan(self, text: str) -> ScanResult:
        """
        Scan text for PII patterns.

        Args:
            text: The text to scan (e.g., LLM output).

        Returns:
            ScanResult with findings and cleaned text.
        """
        findings: list[PIIFinding] = []
        summary: dict = {}

        for pat in self.compiled_patterns:
            for match in pat["regex"].finditer(text):
                finding = PIIFinding(
                    pii_type=pat["type"],
                    matched_text=match.group(),
                    position=(match.start(), match.end()),
                    masked_text=pat["mask"],
                )
                findings.append(finding)
                type_name = pat["type"].value
                summary[type_name] = summary.get(type_name, 0) + 1

        # Build cleaned text with all PII masked
        cleaned = text
        # Sort findings by position in reverse to avoid offset issues
        for finding in sorted(findings, key=lambda f: f.position[0], reverse=True):
            start, end = finding.position
            cleaned = cleaned[:start] + finding.masked_text + cleaned[end:]

        return ScanResult(
            has_pii=len(findings) > 0,
            findings=findings,
            cleaned_text=cleaned,
            summary=summary,
        )

    def scan_and_report(self, text: str) -> str:
        """Scan text and return a formatted report."""
        result = self.scan(text)

        if not result.has_pii:
            return "✓ No PII detected."

        lines = [
            f"✗ PII detected: {len(result.findings)} finding(s)",
            "",
            "Summary:",
        ]
        for pii_type, count in result.summary.items():
            lines.append(f"  - {pii_type}: {count}")

        lines.append("")
        lines.append("Findings:")
        for i, finding in enumerate(result.findings, 1):
            lines.append(
                f"  {i}. [{finding.pii_type.value}] "
                f"'{finding.matched_text[:40]}...' "
                f"at position {finding.position}"
            )

        lines.append("")
        lines.append("Cleaned text:")
        lines.append(result.cleaned_text)

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Standalone Test
# ---------------------------------------------------------------------------

def main():
    """Test the PII detector with sample data."""
    detector = PIIDetector()

    test_text = """
    Here is the customer information you requested:

    Name: John Smith
    Email: john.smith@example.com
    Phone: (555) 123-4567
    SSN: 123-45-6789
    Credit Card: 4532-0150-1234-5678
    IP Address: 192.168.1.100
    Account Number: 9876543210
    DOB: 01/15/1990
    API Key: sk-abc123def456ghi789jkl012mno345
    Password: SuperSecret123!
    """

    print("=" * 70)
    print("LLM02: PII Detector Test")
    print("=" * 70)
    print("\nOriginal text:")
    print(test_text)
    print("\n" + "─" * 70)
    print("\nScan report:")
    print(detector.scan_and_report(test_text))
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
