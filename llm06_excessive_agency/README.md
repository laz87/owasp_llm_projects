# LLM06: Excessive Agency — Bounded AI Agent

Builds an AI agent with strict permission boundaries, human-in-the-loop approval,
and audit logging to prevent unauthorized actions.

## What you'll learn

- **Least-privilege design:** Limit what an AI agent can do
- **Authorization gates:** Require approval for sensitive operations
- **Audit logging:** Track every agent action
- **Jailbreak resistance:** Prevent agents from performing unauthorized actions

## Setup

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your LLM API key.

## Usage

```bash
# Run the bounded agent demo
python bounded_agent.py

# Run the jailbreak attempt demo
python jailbreak_demo.py
```

## How it works

1. `bounded_agent.py` — An AI agent with permission levels, action approval, and audit logging.
2. `jailbreak_demo.py` — Attempts to "jailbreak" the agent into performing unauthorized actions.
3. `requirements.txt` — Python dependencies.

## Permission levels

- **read:** View data, search, summarize
- **write:** Create and modify files
- **admin:** Delete data, configure settings, access external APIs
