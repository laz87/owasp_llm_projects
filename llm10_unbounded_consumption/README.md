# LLM10: Unbounded Consumption — Rate Limiter & Cost Guard

Builds a middleware layer that enforces token budgets, rate limits, and request
quotas to prevent denial of service and cost abuse.

## What you'll learn

- **Token budgeting:** Set maximum token limits per request and per user
- **Rate limiting:** Throttle requests to prevent abuse
- **Cost control:** Monitor and cap API spending
- **Abuse detection:** Identify anomalous usage patterns

## Setup

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your LLM API key.

## Usage

```bash
# Run the rate limiter demo
python rate_limiter.py

# Run the load test simulation
python rate_limiter.py --load-test
```

## How it works

1. `rate_limiter.py` — A middleware that wraps LLM API calls with rate limiting, token budgeting, and cost tracking.
2. `requirements.txt` — Python dependencies.

## Protection mechanisms

- **Per-request token limit:** Reject prompts that exceed the maximum token count
- **Per-user rate limit:** Maximum requests per time window
- **Daily budget cap:** Stop all requests when the budget is exhausted
- **Recursive loop detection:** Flag repeated identical requests
- **Anomaly detection:** Alert on unusual usage spikes
