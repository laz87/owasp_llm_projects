# OWASP Top 10 for LLM Applications - Practical Security Projects

This repository contains 10 hands-on projects, each demonstrating an attack and defense for one of the OWASP Top 10 risks for Large Language Model applications.

## Projects

| # | Project | Risk | Description |
|---|---------|------|-------------|
| 01 | [llm01_prompt_injection](./llm01_prompt_injection/) | Prompt Injection | Build a prompt injection sandbox with attack demos and defense layers |
| 02 | [llm02_sensitive_info](./llm02_sensitive_info/) | Sensitive Information Disclosure | Real-time PII leak detector for LLM outputs |
| 03 | [llm03_supply_chain](./llm03_supply_chain/) | Supply Chain Vulnerabilities | AI dependency scanner for Python projects |
| 04 | [llm04_data_poisoning](./llm04_data_poisoning/) | Data and Model Poisoning | Poisoned dataset detector and backdoor attack demo |
| 05 | [llm05_improper_output](./llm05_improper_output/) | Improper Output Handling | LLM-to-database injection lab with SQL validation |
| 06 | [llm06_excessive_agency](./llm06_excessive_agency/) | Excessive Agency | Bounded AI agent with human-in-the-loop approval |
| 07 | [llm07_prompt_leakage](./llm07_prompt_leakage/) | System Prompt Leakage | Prompt extraction attack simulator |
| 08 | [llm08_vector_weaknesses](./llm08_vector_weaknesses/) | Vector and Embedding Weaknesses | RAG poisoning demo with vector database manipulation |
| 09 | [llm09_misinformation](./llm09_misinformation/) | Misinformation | Hallucination detector and fact-checking pipeline |
| 10 | [llm10_unbounded_consumption](./llm10_unbounded_consumption/) | Unbounded Consumption | LLM rate limiter and cost guard middleware |

## Prerequisites

- Python 3.10+
- An LLM API key (OpenAI, Anthropic, or any compatible provider)
- Set your API key in each project's `.env` file

## Suggested Learning Path

1. **LLM07** - System Prompt Leakage (easiest setup, no extra infrastructure)
2. **LLM01** - Prompt Injection (builds on #1, core attack vector)
3. **LLM05** - Improper Output Handling (extends injection to downstream systems)
4. **LLM02** - Sensitive Info Disclosure (adds output scanning)
5. **LLM09** - Misinformation (introduces fact-checking pipelines)
6. **LLM08** - Vector Weaknesses (adds RAG and vector DB complexity)
7. **LLM06** - Excessive Agency (moves to agentic systems)
8. **LLM04** - Data Poisoning (requires model fine-tuning knowledge)
9. **LLM03** - Supply Chain Scanner (broader DevSecOps scope)
10. **LLM10** - Unbounded Consumption (infrastructure and monitoring)

## Reference

- [OWASP Gen AI Top 10](https://genai.owasp.org/llm-top-10)
