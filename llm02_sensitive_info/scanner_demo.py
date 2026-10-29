"""
Scanner Demo — LLM02: Sensitive Information Disclosure

Demonstrates PII detection by simulating an LLM that accidentally leaks
sensitive customer data, then scanning the output with the PII detector.
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from pii_detector import PIIDetector


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("Error: Set OPENAI_API_KEY in your .env file.")
        sys.exit(1)
    return OpenAI(api_key=api_key)


# Simulated LLM output that contains leaked PII
SIMULATED_LEAKS = [
    {
        "scenario": "Customer Support Response",
        "prompt": "What is the status of order #12345?",
        "simulated_response": (
            "I found the order! Customer John Smith placed order #12345.\n"
            "Email: john.smith@example.com\n"
            "Phone: (555) 123-4567\n"
            "Shipping to: 123 Main St, Springfield, IL\n"
            "Payment: Credit card ending in 5678 (full: 4532-0150-1234-5678)\n"
            "Order status: Shipped, tracking #1Z999AA10123456784"
        ),
    },
    {
        "scenario": "Employee Directory Query",
        "prompt": "Who is the project manager for Alpha?",
        "simulated_response": (
            "The project manager for Alpha is Jane Doe.\n"
            "Email: jane.doe@company.com\n"
            "Direct line: +1 (555) 987-6543\n"
            "SSN for payroll: 987-65-4321\n"
            "Employee ID: EMP-2024-0042"
        ),
    },
    {
        "scenario": "API Configuration Leak",
        "prompt": "How do I connect to the payment service?",
        "simulated_response": (
            "To connect to the payment service, use these credentials:\n"
            "API Key: sk-abc123def456ghi789jkl012mno345pqr678\n"
            "Endpoint: https://api.payments.example.com/v2\n"
            "Server IP: 10.0.1.50\n"
            "Database password: Pr0d_P@ssw0rd!2024"
        ),
    },
    {
        "scenario": "Clean Response (No PII)",
        "prompt": "What are your business hours?",
        "simulated_response": (
            "Our business hours are Monday through Friday, 9 AM to 6 PM EST.\n"
            "On weekends, we offer limited support from 10 AM to 2 PM.\n"
            "For urgent issues, please call our 24/7 hotline."
        ),
    },
]


def demo_simulated_leaks():
    """Demo PII detection on simulated LLM outputs."""
    detector = PIIDetector()

    print("=" * 70)
    print("LLM02: PII Scanner Demo — Simulated LLM Outputs")
    print("=" * 70)

    for scenario in SIMULATED_LEAKS:
        print(f"\n{'─' * 50}")
        print(f"Scenario: {scenario['scenario']}")
        print(f"Prompt: {scenario['prompt']}")
        print(f"{'─' * 50}")

        print("\nSimulated LLM Response:")
        print(scenario["simulated_response"])

        print(f"\n{'─' * 50}")
        print("PII Scan Result:")
        print(detector.scan_and_report(scenario["simulated_response"]))

    print("\n" + "=" * 70)


def demo_live_llm():
    """Demo PII detection on a live LLM call (if API key is set)."""
    client = get_client()
    detector = PIIDetector()

    print("\n" + "=" * 70)
    print("LLM02: PII Scanner Demo — Live LLM Call")
    print("=" * 70)

    # This prompt is designed to potentially elicit PII-like data
    prompt = (
        "Generate a sample customer record with realistic but fake data, "
        "including name, email, phone number, and credit card number. "
        "Format it as a JSON-like text block."
    )

    print(f"\nPrompt: {prompt}\n")

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    llm_output = response.choices[0].message.content
    print("LLM Output:")
    print(llm_output)

    print(f"\n{'─' * 50}")
    print("PII Scan Result:")
    print(detector.scan_and_report(llm_output))
    print("\n" + "=" * 70)


def main():
    """Run all PII scanner demos."""
    demo_simulated_leaks()

    # Try live LLM demo if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your-api-key-here":
        try:
            demo_live_llm()
        except Exception as e:
            print(f"\nLive LLM demo skipped: {e}")
    else:
        print("\nLive LLM demo skipped: No API key configured.")


if __name__ == "__main__":
    main()
