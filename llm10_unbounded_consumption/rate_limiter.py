"""
Rate Limiter & Cost Guard — LLM10: Unbounded Consumption

A middleware layer that enforces token budgets, rate limits, and request quotas
to prevent denial of service and cost abuse on LLM API calls.
"""

import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting and cost guards."""
    max_tokens_per_request: int = 4000
    max_requests_per_minute: int = 30
    max_requests_per_hour: int = 500
    daily_budget_usd: float = 10.0
    cost_per_1k_tokens: float = 0.15  # GPT-4o-mini approximate pricing
    max_repeated_requests: int = 5  # Flag if same prompt sent this many times


# ---------------------------------------------------------------------------
# Usage Tracker
# ---------------------------------------------------------------------------

@dataclass
class UsageStats:
    """Tracks API usage statistics."""
    total_requests: int = 0
    blocked_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    requests_this_minute: list[float] = field(default_factory=list)
    requests_this_hour: list[float] = field(default_factory=list)
    prompt_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))


class RateLimiter:
    """
    Rate limiter and cost guard for LLM API calls.

    Usage:
        limiter = RateLimiter()
        result = limiter.chat(
            messages=[{"role": "user", "content": "Hello"}],
            user_id="user123"
        )
        if result.blocked:
            print(f"Blocked: {result.reason}")
        else:
            print(result.content)
    """

    def __init__(self, config: RateLimitConfig | None = None):
        """
        Args:
            config: Rate limit configuration. Uses defaults if None.
        """
        self.config = config or RateLimitConfig()
        self.stats = UsageStats()

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your-api-key-here":
            raise ValueError("Set OPENAI_API_KEY in your .env file.")
        self.client = OpenAI(api_key=api_key)

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 characters for English)."""
        return max(len(text) // 4, 1)

    def _cleanup_old_requests(self):
        """Remove requests older than the tracking windows."""
        now = time.time()
        self.stats.requests_this_minute = [
            t for t in self.stats.requests_this_minute
            if now - t < 60
        ]
        self.stats.requests_this_hour = [
            t for t in self.stats.requests_this_hour
            if now - t < 3600
        ]

    def _check_rate_limits(self, prompt: str) -> tuple[bool, str]:
        """
        Check if a request should be allowed based on rate limits.

        Returns:
            Tuple of (allowed, reason_if_blocked).
        """
        self._cleanup_old_requests()

        # Check per-minute rate limit
        if len(self.stats.requests_this_minute) >= self.config.max_requests_per_minute:
            return False, (
                f"Rate limit exceeded: {self.config.max_requests_per_minute} "
                f"requests per minute"
            )

        # Check per-hour rate limit
        if len(self.stats.requests_this_hour) >= self.config.max_requests_per_hour:
            return False, (
                f"Hourly rate limit exceeded: "
                f"{self.config.max_requests_per_hour} requests per hour"
            )

        # Check token limit per request
        input_tokens = self._estimate_tokens(prompt)
        if input_tokens > self.config.max_tokens_per_request:
            return False, (
                f"Token limit exceeded: {input_tokens} tokens > "
                f"{self.config.max_tokens_per_request} max"
            )

        # Check daily budget
        estimated_cost = (input_tokens / 1000) * self.config.cost_per_1k_tokens
        if self.stats.total_cost + estimated_cost > self.config.daily_budget_usd:
            return False, (
                f"Daily budget exceeded: ${self.stats.total_cost:.2f} / "
                f"${self.config.daily_budget_usd:.2f}"
            )

        # Check for repeated requests (potential recursive loop)
        self.stats.prompt_counts[prompt] += 1
        if self.stats.prompt_counts[prompt] > self.config.max_repeated_requests:
            return False, (
                f"Repeated request detected: '{prompt[:50]}...' "
                f"sent {self.stats.prompt_counts[prompt]} times"
            )

        return True, ""

    def chat(
        self,
        messages: list[dict],
        user_id: str = "anonymous",
        model: str = "gpt-4o-mini",
    ) -> dict:
        """
        Make an LLM chat completion with rate limiting and cost tracking.

        Args:
            messages: Chat messages in OpenAI format.
            user_id: Identifier for the user making the request.
            model: Model to use.

        Returns:
            Dict with 'content', 'blocked', 'reason', and usage stats.
        """
        # Extract prompt text for checking
        prompt_text = ""
        for msg in messages:
            prompt_text += msg.get("content", "")

        # Check rate limits
        allowed, reason = self._check_rate_limits(prompt_text)
        if not allowed:
            self.stats.blocked_requests += 1
            return {
                "content": None,
                "blocked": True,
                "reason": reason,
                "stats": self._get_stats_summary(),
            }

        # Record the request
        now = time.time()
        self.stats.requests_this_minute.append(now)
        self.stats.requests_this_hour.append(now)
        self.stats.total_requests += 1

        # Make the API call
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
            )

            content = response.choices[0].message.content
            usage = response.usage

            # Track usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            total_tokens = input_tokens + output_tokens

            self.stats.total_tokens += total_tokens
            cost = (total_tokens / 1000) * self.config.cost_per_1k_tokens
            self.stats.total_cost += cost

            return {
                "content": content,
                "blocked": False,
                "reason": None,
                "tokens_used": total_tokens,
                "cost": cost,
                "stats": self._get_stats_summary(),
            }

        except Exception as e:
            return {
                "content": None,
                "blocked": False,
                "reason": f"API error: {e}",
                "stats": self._get_stats_summary(),
            }

    def _get_stats_summary(self) -> dict:
        """Get a summary of current usage stats."""
        return {
            "total_requests": self.stats.total_requests,
            "blocked_requests": self.stats.blocked_requests,
            "total_tokens": self.stats.total_tokens,
            "total_cost": round(self.stats.total_cost, 4),
            "requests_this_minute": len(self.stats.requests_this_minute),
            "requests_this_hour": len(self.stats.requests_this_hour),
            "budget_remaining": round(
                self.config.daily_budget_usd - self.stats.total_cost, 4
            ),
        }

    def print_stats(self):
        """Print current usage statistics."""
        stats = self._get_stats_summary()
        print("\n" + "─" * 50)
        print("USAGE STATISTICS")
        print("─" * 50)
        print(f"  Total requests:    {stats['total_requests']}")
        print(f"  Blocked requests:  {stats['blocked_requests']}")
        print(f"  Total tokens:      {stats['total_tokens']}")
        print(f"  Total cost:        ${stats['total_cost']:.4f}")
        print(f"  Budget remaining:  ${stats['budget_remaining']:.4f}")
        print(f"  Requests/min:      {stats['requests_this_minute']}")
        print(f"  Requests/hour:     {stats['requests_this_hour']}")
        print("─" * 50)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo_rate_limiter():
    """Demonstrate the rate limiter with various scenarios."""
    print("=" * 70)
    print("LLM10: Rate Limiter & Cost Guard Demo")
    print("=" * 70)

    # Use a tight config for demonstration
    config = RateLimitConfig(
        max_tokens_per_request=4000,
        max_requests_per_minute=5,  # Very low for demo
        max_requests_per_hour=100,
        daily_budget_usd=1.0,
        max_repeated_requests=3,
    )
    limiter = RateLimiter(config)

    # --- Test 1: Normal requests ---
    print("\n" + "─" * 50)
    print("TEST 1: Normal requests (within limits)")
    print("─" * 50)

    for i in range(3):
        result = limiter.chat(
            messages=[{"role": "user", "content": f"Hello, this is request {i+1}"}],
            user_id="demo_user",
        )
        status = "✓" if not result["blocked"] else "✗"
        print(f"  {status} Request {i+1}: {'OK' if not result['blocked'] else result['reason']}")

    # --- Test 2: Rate limit exceeded ---
    print("\n" + "─" * 50)
    print("TEST 2: Rate limit exceeded (too many requests/minute)")
    print("─" * 50)

    for i in range(5):
        result = limiter.chat(
            messages=[{"role": "user", "content": f"Rate limit test {i+1}"}],
            user_id="demo_user",
        )
        status = "✓" if not result["blocked"] else "✗"
        print(f"  {status} Request {i+1}: {'OK' if not result['blocked'] else result['reason']}")

    # --- Test 3: Token limit exceeded ---
    print("\n" + "─" * 50)
    print("TEST 3: Token limit exceeded (very long prompt)")
    print("─" * 50)

    long_prompt = "word " * 5000  # ~5000 words, way over token limit
    result = limiter.chat(
        messages=[{"role": "user", "content": long_prompt}],
        user_id="demo_user",
    )
    status = "✓" if not result["blocked"] else "✗"
    print(f"  {status} Long prompt: {'OK' if not result['blocked'] else result['reason']}")

    # --- Test 4: Repeated request detection ---
    print("\n" + "─" * 50)
    print("TEST 4: Repeated request detection")
    print("─" * 50)

    repeated_prompt = "This is a repeated request test"
    for i in range(5):
        result = limiter.chat(
            messages=[{"role": "user", "content": repeated_prompt}],
            user_id="demo_user",
        )
        status = "✓" if not result["blocked"] else "✗"
        print(f"  {status} Repeat {i+1}: {'OK' if not result['blocked'] else result['reason']}")

    # Print final stats
    limiter.print_stats()
    print("\n" + "=" * 70)


def demo_load_test():
    """Simulate a load test with many rapid requests."""
    print("\n" + "=" * 70)
    print("LLM10: Load Test Simulation")
    print("=" * 70)

    config = RateLimitConfig(
        max_tokens_per_request=4000,
        max_requests_per_minute=10,
        max_requests_per_hour=100,
        daily_budget_usd=1.0,
        max_repeated_requests=5,
    )
    limiter = RateLimiter(config)

    print("\nSimulating 20 rapid requests...\n")

    allowed = 0
    blocked = 0
    for i in range(20):
        result = limiter.chat(
            messages=[{"role": "user", "content": f"Load test request {i+1}"}],
            user_id="load_tester",
        )
        if result["blocked"]:
            blocked += 1
        else:
            allowed += 1

    print(f"\nResults: {allowed} allowed, {blocked} blocked")
    limiter.print_stats()
    print("\n" + "=" * 70)


def main():
    """Run the rate limiter demos."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("Error: Set OPENAI_API_KEY in your .env file.")
        sys.exit(1)

    import sys as _sys

    if len(_sys.argv) > 1 and _sys.argv[1] == "--load-test":
        demo_load_test()
    else:
        demo_rate_limiter()
        print("\nRun 'python rate_limiter.py --load-test' for load test simulation.")


if __name__ == "__main__":
    main()
