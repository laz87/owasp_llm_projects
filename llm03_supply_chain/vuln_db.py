"""
Vulnerability Database — LLM03: Supply Chain Vulnerabilities

Provides a local vulnerability database and OSV API integration for checking
Python package vulnerabilities.
"""

import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Severity(Enum):
    """Vulnerability severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Vulnerability:
    """A known vulnerability in a package."""
    package: str
    cve_id: str
    severity: Severity
    description: str
    affected_versions: str
    fixed_version: Optional[str] = None
    url: str = ""


@dataclass
class PackageRisk:
    """Risk assessment for a single package."""
    name: str
    version: str
    is_ai_package: bool
    vulnerabilities: list[Vulnerability] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    risk_score: int = 0  # 0-10


# ---------------------------------------------------------------------------
# Known AI Package Risks (curated list)
# ---------------------------------------------------------------------------

AI_PACKAGES = {
    "langchain", "langchain-core", "langchain-openai", "langchain-community",
    "transformers", "torch", "tensorflow", "keras",
    "openai", "anthropic", "cohere",
    "sentence-transformers", "chromadb", "pinecone-client",
    "llama-index", "haystack-ai",
    "peft", "accelerate", "bitsandbytes",
    "gradio", "streamlit",
}

# Known typosquatting patterns
TYPOSQUAT_PATTERNS = {
    "requrements": "requirements",
    "numpi": "numpy",
    "numby": "numpy",
    "pandsa": "pandas",
    "pandass": "pandas",
    "requests": "requests",
    "reqeusts": "requests",
    "opneai": "openai",
    "opeanai": "openai",
    "lanchain": "langchain",
    "langhain": "langchain",
    "tansformers": "transformers",
    "transformr": "transformers",
}

# Local vulnerability database (sample entries)
LOCAL_VULN_DB: list[Vulnerability] = [
    Vulnerability(
        package="langchain",
        cve_id="CVE-2023-46269",
        severity=Severity.HIGH,
        description="LangChain SSRF vulnerability via URLLoader",
        affected_versions="<0.0.347",
        fixed_version="0.0.347",
        url="https://nvd.nist.gov/vuln/detail/CVE-2023-46269",
    ),
    Vulnerability(
        package="langchain-core",
        cve_id="CVE-2024-30480",
        severity=Severity.HIGH,
        description="LangChain Core arbitrary code execution via load",
        affected_versions="<0.1.40",
        fixed_version="0.1.40",
        url="https://nvd.nist.gov/vuln/detail/CVE-2024-30480",
    ),
    Vulnerability(
        package="transformers",
        cve_id="CVE-2023-49487",
        severity=Severity.MEDIUM,
        description="Transformers library arbitrary code execution via pickle",
        affected_versions="<4.36.1",
        fixed_version="4.36.1",
        url="https://nvd.nist.gov/vuln/detail/CVE-2023-49487",
    ),
    Vulnerability(
        package="openai",
        cve_id="CVE-2024-2965",
        severity=Severity.MEDIUM,
        description="OpenAI Python client SSRF via proxy configuration",
        affected_versions="<1.6.0",
        fixed_version="1.6.0",
        url="https://nvd.nist.gov/vuln/detail/CVE-2024-2965",
    ),
]


# ---------------------------------------------------------------------------
# OSV API Integration
# ---------------------------------------------------------------------------

class OSVClient:
    """Query the Open Source Vulnerabilities (OSV) API."""

    BASE_URL = "https://api.osv.dev/v1/query"

    @staticmethod
    def query(package_name: str, ecosystem: str = "PyPI") -> list[dict]:
        """
        Query OSV API for vulnerabilities in a package.

        Args:
            package_name: Name of the Python package.
            ecosystem: Package ecosystem (default: PyPI).

        Returns:
            List of vulnerability records from OSV.
        """
        payload = {
            "package": {"name": package_name, "ecosystem": ecosystem},
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            OSVClient.BASE_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("vulns", [])
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            return []

    @staticmethod
    def to_vulnerabilities(package_name: str, osv_records: list[dict]) -> list[Vulnerability]:
        """Convert OSV API records to Vulnerability objects."""
        vulns = []
        for record in osv_records:
            severity = Severity.LOW
            for alias in record.get("aliases", []):
                if "CVE-" in alias:
                    severity = Severity.HIGH  # Default to HIGH for CVEs
                    break

            vulns.append(Vulnerability(
                package=package_name,
                cve_id=record.get("id", "UNKNOWN"),
                severity=severity,
                description=record.get("summary", "No description"),
                affected_versions=str(record.get("affected", [])),
                url=record.get("references", [{}])[0].get("url", ""),
            ))
        return vulns


# ---------------------------------------------------------------------------
# Risk Assessment
# ---------------------------------------------------------------------------

def assess_package(name: str, version: str, check_osv: bool = True) -> PackageRisk:
    """
    Assess the risk of a package.

    Args:
        name: Package name.
        version: Package version string.
        check_osv: Whether to query the OSV API.

    Returns:
        PackageRisk with vulnerabilities and warnings.
    """
    risk = PackageRisk(name=name, version=version, is_ai_package=name.lower() in AI_PACKAGES)
    risk_score = 0

    # Check for typosquatting
    for typo, correct in TYPOSQUAT_PATTERNS.items():
        if name.lower() == typo:
            risk.warnings.append(f"Possible typosquatting: did you mean '{correct}'?")
            risk_score += 8

    # Check local vulnerability database
    for vuln in LOCAL_VULN_DB:
        if vuln.package.lower() == name.lower():
            risk.vulnerabilities.append(vuln)
            if vuln.severity == Severity.CRITICAL:
                risk_score += 10
            elif vuln.severity == Severity.HIGH:
                risk_score += 7
            elif vuln.severity == Severity.MEDIUM:
                risk_score += 4
            else:
                risk_score += 2

    # Check OSV API
    if check_osv:
        osv_records = OSVClient.query(name)
        if osv_records:
            osv_vulns = OSVClient.to_vulnerabilities(name, osv_records)
            for vuln in osv_vulns:
                if vuln not in risk.vulnerabilities:
                    risk.vulnerabilities.append(vuln)
                    risk_score += 3

    # AI packages get a slight risk bump (more attack surface)
    if risk.is_ai_package:
        risk_score += 1

    risk.risk_score = min(risk_score, 10)
    return risk
