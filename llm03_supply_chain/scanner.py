"""
Dependency Scanner — LLM03: Supply Chain Vulnerabilities

Scans Python project dependency files (requirements.txt, pyproject.toml)
for known vulnerabilities, typosquatting, and AI-specific risks.
"""

import argparse
import os
import re
import sys
from pathlib import Path

from vuln_db import assess_package, PackageRisk, Severity


def parse_requirements_file(filepath: str) -> list[tuple[str, str]]:
    """
    Parse a requirements.txt file and return (name, version) pairs.

    Args:
        filepath: Path to requirements.txt.

    Returns:
        List of (package_name, version_spec) tuples.
    """
    packages = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#") or line.startswith("-"):
                continue

            # Parse package==version, package>=version, package<=version, etc.
            match = re.match(r"^([a-zA-Z0-9_-]+)\s*([><=!~]=?\s*\S+)?", line)
            if match:
                name = match.group(1)
                version = match.group(2) or "any"
                packages.append((name, version))

    return packages


def scan_packages(
    packages: list[tuple[str, str]],
    check_osv: bool = True,
    verbose: bool = False,
) -> list[PackageRisk]:
    """
    Scan a list of packages for vulnerabilities.

    Args:
        packages: List of (name, version) tuples.
        check_osv: Whether to query the OSV API.
        verbose: Whether to print detailed output.

    Returns:
        List of PackageRisk assessments.
    """
    results = []
    for name, version in packages:
        if verbose:
            print(f"  Scanning {name} ({version})...")

        risk = assess_package(name, version, check_osv=check_osv)
        results.append(risk)

    return results


def print_report(results: list[PackageRisk], verbose: bool = False):
    """Print a formatted vulnerability report."""
    print("\n" + "=" * 70)
    print("LLM03: AI Dependency Scan Report")
    print("=" * 70)

    # Summary
    total = len(results)
    ai_packages = sum(1 for r in results if r.is_ai_package)
    with_vulns = sum(1 for r in results if r.vulnerabilities)
    with_warnings = sum(1 for r in results if r.warnings)
    high_risk = sum(1 for r in results if r.risk_score >= 7)

    print(f"\nTotal packages scanned: {total}")
    print(f"AI-related packages: {ai_packages}")
    print(f"Packages with vulnerabilities: {with_vulns}")
    print(f"Packages with warnings: {with_warnings}")
    print(f"High risk (score >= 7): {high_risk}")

    # Detailed findings
    print("\n" + "─" * 70)
    print("DETAILED FINDINGS")
    print("─" * 70)

    # Sort by risk score (highest first)
    sorted_results = sorted(results, key=lambda r: r.risk_score, reverse=True)

    for risk in sorted_results:
        if risk.risk_score == 0 and not verbose:
            continue

        status = "✓" if risk.risk_score == 0 else ("⚠" if risk.risk_score < 7 else "✗")
        ai_tag = " [AI]" if risk.is_ai_package else ""
        print(f"\n{status} {risk.name} ({risk.version}){ai_tag} — Risk: {risk.risk_score}/10")

        for vuln in risk.vulnerabilities:
            print(f"  🔴 {vuln.cve_id} ({vuln.severity.value})")
            print(f"     {vuln.description}")
            if vuln.fixed_version:
                print(f"     Fix: Upgrade to {vuln.fixed_version}")
            if vuln.url:
                print(f"     {vuln.url}")

        for warning in risk.warnings:
            print(f"  🟡 {warning}")

    print("\n" + "=" * 70)


def scan_directory(dirpath: str, check_osv: bool = True, verbose: bool = False):
    """
    Scan all requirements.txt and pyproject.toml files in a directory.

    Args:
        dirpath: Directory to scan.
        check_osv: Whether to query the OSV API.
        verbose: Whether to print detailed output.
    """
    dir_path = Path(dirpath)
    all_packages = []

    # Find requirements.txt files
    for req_file in dir_path.rglob("requirements*.txt"):
        print(f"Scanning: {req_file}")
        packages = parse_requirements_file(str(req_file))
        all_packages.extend(packages)

    if not all_packages:
        print("No requirements.txt files found.")
        return []

    # Deduplicate packages
    seen = set()
    unique_packages = []
    for name, version in all_packages:
        if name.lower() not in seen:
            seen.add(name.lower())
            unique_packages.append((name, version))

    return scan_packages(unique_packages, check_osv=check_osv, verbose=verbose)


def main():
    """Main entry point for the dependency scanner."""
    parser = argparse.ArgumentParser(description="AI Dependency Vulnerability Scanner")
    parser.add_argument(
        "--file", "-f",
        help="Path to requirements.txt file to scan",
        default=None,
    )
    parser.add_argument(
        "--dir", "-d",
        help="Directory to scan for requirements files",
        default=".",
    )
    parser.add_argument(
        "--no-osv",
        action="store_true",
        help="Skip OSV API checks (faster, but less thorough)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output for all packages",
    )

    args = parser.parse_args()

    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            sys.exit(1)

        packages = parse_requirements_file(args.file)
        if not packages:
            print("No packages found in file.")
            sys.exit(0)

        results = scan_packages(packages, check_osv=not args.no_osv, verbose=args.verbose)
    else:
        results = scan_directory(
            args.dir, check_osv=not args.no_osv, verbose=args.verbose
        )

    if results:
        print_report(results, verbose=args.verbose)
    else:
        print("No packages to scan.")


if __name__ == "__main__":
    main()
