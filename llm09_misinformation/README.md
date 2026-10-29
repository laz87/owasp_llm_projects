# LLM09: Misinformation — Hallucination Detector & Fact-Checker

Builds a pipeline that detects hallucinated claims in LLM responses by
verifying them against a knowledge base or search API.

## What you'll learn

- **Claim extraction:** Break LLM responses into verifiable claims
- **Fact checking:** Verify claims against trusted sources
- **Hallucination scoring:** Rate responses for factual accuracy
- **RAG as mitigation:** Use grounded retrieval to reduce hallucinations

## Setup

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your LLM API key.

## Usage

```bash
# Run the hallucination detector demo
python fact_checker.py
```

## How it works

1. `fact_checker.py` — Takes LLM responses, extracts claims, and verifies each claim against a knowledge base. Scores the response for factual accuracy and flags hallucinated statements.

## Detection methods

- **Knowledge base lookup:** Check claims against a curated fact database
- **Cross-reference:** Compare multiple sources for consistency
- **Confidence scoring:** Rate each claim's verifiability
- **Source grounding:** Flag claims without supporting evidence
