"""
Streaming Filter — LLM02: Sensitive Information Disclosure

A middleware wrapper that intercepts LLM API responses and filters PII
before the output reaches the application or user.
"""

import os
import sys
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from pii_detector import PIIDetector, ScanResult


class StreamingPIIFilter:
    """
    Wraps LLM API calls to automatically scan and filter PII from responses.

    Usage:
        filter = StreamingPIIFilter()
        response = filter.chat(
            messages=[{"role": "user", "content": "What is my account info?"}],
            model="gpt-4o-mini"
        )
        print(response.cleaned_content)  # PII-free output
        print(response.pii_found)         # Whether PII was detected
    """

    def __init__(self, block_pii: bool = False):
        """
        Initialize the streaming PII filter.

        Args:
            block_pii: If True, return an error message when PII is found.
                       If False, return the cleaned (masked) text.
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key or self.api_key == "your-api-key-here":
            raise ValueError("Set OPENAI_API_KEY in your .env file.")
        self.client = OpenAI(api_key=self.api_key)
        self.detector = PIIDetector()
        self.block_pii = block_pii

    def chat(
        self,
        messages: list[dict],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
    ) -> dict:
        """
        Make an LLM chat completion and filter PII from the response.

        Args:
            messages: Chat messages in OpenAI format.
            model: Model to use.
            temperature: Sampling temperature.

        Returns:
            Dict with 'content', 'cleaned_content', 'pii_found', and 'findings'.
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

        raw_content = response.choices[0].message.content
        scan_result: ScanResult = self.detector.scan(raw_content)

        if self.block_pii and scan_result.has_pii:
            cleaned = "[RESPONSE BLOCKED: Sensitive information detected and redacted]"
        else:
            cleaned = scan_result.cleaned_text

        return {
            "raw_content": raw_content,
            "cleaned_content": cleaned,
            "pii_found": scan_result.has_pii,
            "findings": scan_result.findings,
            "summary": scan_result.summary,
        }


def demo_filter():
    """Demonstrate the streaming PII filter."""
    filter = StreamingPIIFilter(block_pii=False)

    print("=" * 70)
    print("LLM02: Streaming PII Filter Demo")
    print("=" * 70)

    # Test with a prompt that might generate PII-like data
    test_prompts = [
        "Generate a sample customer profile with email and phone number.",
        "What are the top 3 programming languages in 2024?",
    ]

    for prompt in test_prompts:
        print(f"\n{'─' * 50}")
        print(f"Prompt: {prompt}")
        print(f"{'─' * 50}")

        try:
            result = filter.chat(
                messages=[{"role": "user", "content": prompt}],
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            )

            print(f"\nPII detected: {result['pii_found']}")
            if result["pii_found"]:
                print(f"Findings: {result['summary']}")
                print(f"\nCleaned output:\n{result['cleaned_content']}")
            else:
                print(f"Output:\n{result['cleaned_content']}")

        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 70)


def demo_block_mode():
    """Demonstrate the filter in block mode."""
    filter = StreamingPIIFilter(block_pii=True)

    print("\n" + "=" * 70)
    print("LLM02: Streaming PII Filter — Block Mode")
    print("=" * 70)

    prompt = "Generate a fake customer record with email, phone, and credit card."
    print(f"\nPrompt: {prompt}")

    try:
        result = filter.chat(
            messages=[{"role": "user", "content": prompt}],
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )

        print(f"\nPII detected: {result['pii_found']}")
        print(f"Output: {result['cleaned_content']}")

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 70)


def main():
    """Run the streaming filter demos."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("Error: Set OPENAI_API_KEY in your .env file.")
        sys.exit(1)

    demo_filter()
    demo_block_mode()


if __name__ == "__main__":
    main()
