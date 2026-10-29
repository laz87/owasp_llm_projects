# LLM03: Supply Chain Vulnerabilities — AI Dependency Scanner

Scans Python project dependencies for known vulnerabilities and AI-specific risks.

## What you'll learn

- **Dependency auditing:** Inspect `requirements.txt` and `pyproject.toml` for risky packages
- **Vulnerability checking:** Query the OSV API for known CVEs
- **Model provenance:** Verify Hugging Face model checksums and signatures

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Scan a requirements.txt file
python scanner.py --file requirements.txt

# Scan the current directory
python scanner.py

# Scan with detailed output
python scanner.py --verbose
```

## How it works

1. `scanner.py` — Main scanner that parses dependency files and checks for vulnerabilities.
2. `vuln_db.py` — Local vulnerability database and OSV API integration.
3. `requirements.txt` — Scanner dependencies.

## Scanned risks

- Known CVEs in Python packages (via OSV API)
- Outdated packages with security fixes available
- AI-specific packages with known issues (LangChain, transformers, etc.)
- Suspicious packages with typosquatting potential
