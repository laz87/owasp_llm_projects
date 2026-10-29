# LLM02: Sensitive Information Disclosure — PII Leak Detector

Detects personally identifiable information (PII) and sensitive data in LLM outputs.

## What you'll learn

- **PII detection:** Use regex and NER to find leaked data in real-time
- **Data types:** Credit cards, SSNs, API keys, emails, phone numbers
- **Streaming filters:** Intercept and sanitize LLM output before it reaches the user

## Setup

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your LLM API key.

## Usage

```bash
# Run the PII detector standalone
python pii_detector.py

# Run the LLM output scanner demo
python scanner_demo.py

# Run the streaming filter
python streaming_filter.py
```

## How it works

1. `pii_detector.py` — Core PII detection engine using regex patterns and keyword matching.
2. `scanner_demo.py` — Demonstrates PII detection by feeding test data through the detector.
3. `streaming_filter.py` — A middleware that wraps LLM API calls and filters PII from responses in real-time.

## Detected data types

- Credit card numbers (Visa, MasterCard, Amex)
- Social Security Numbers (SSN)
- Email addresses
- Phone numbers (US format)
- API keys (various providers)
- IP addresses
- Dates of birth
- Names (via keyword patterns)
