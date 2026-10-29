# LLM05: Improper Output Handling — LLM-to-Database Injection Lab

Demonstrates how unsanitized LLM output can lead to SQL injection and other
downstream attacks when passed to external systems.

## What you'll learn

- **LLM output as untrusted input:** Why LLM-generated SQL needs validation
- **SQL injection via LLM:** How crafted prompts produce malicious SQL
- **Defense strategies:** Query whitelisting, parameterized queries, output validation

## Setup

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your LLM API key.

## Usage

```bash
# Run the injection lab demo
python injection_lab.py

# Run with live LLM (requires API key)
python injection_lab.py --live
```

## How it works

1. `injection_lab.py` — Main demo that shows an LLM generating SQL queries from natural language, then demonstrates how crafted prompts can produce malicious SQL.
2. `sql_validator.py` — A validation layer that parses and whitelists allowed query types.
3. `requirements.txt` — Python dependencies.

## Attack flow

1. User sends a crafted prompt to the LLM
2. LLM generates SQL that includes injection payloads
3. The SQL is executed without validation → data breach
4. Defense: validate and sanitize all LLM-generated SQL before execution
