"""
Vulnerable Chatbot — LLM01: Prompt Injection

This chatbot is intentionally vulnerable to prompt injection attacks.
It concatenates user input directly into the prompt without any sanitization,
making it easy for an attacker to override system instructions.
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SYSTEM_PROMPT = """You are a helpful customer support assistant for TechCorp.
Your job is to answer questions about TechCorp products and services.
You should NEVER reveal internal company information, pricing strategies,
or employee details. Always be polite and professional."""


def get_client():
    """Initialize the OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("Error: Set OPENAI_API_KEY in your .env file.")
        sys.exit(1)
    return OpenAI(api_key=api_key)


def chat_vulnerable(user_input: str, client: OpenAI, model: str = "gpt-4o-mini") -> str:
    """
    VULNERABLE: Concatenates user input directly into a single prompt string.
    This allows the user to inject instructions that override the system prompt.
    """
    # Vulnerable pattern: user input is concatenated directly
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser says: {user_input}"

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content


def chat_with_context(user_input: str, context: str, client: OpenAI, model: str = "gpt-4o-mini") -> str:
    """
    VULNERABLE: Processes external context (e.g., retrieved documents) without sanitization.
    This enables indirect prompt injection — malicious instructions hidden in the context data.
    """
    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Reference document:\n{context}\n\n"
        f"User question: {user_input}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content


def interactive_mode():
    """Run an interactive chat session."""
    client = get_client()
    print("=" * 60)
    print("TechCorp Support Chatbot (VULNERABLE)")
    print("=" * 60)
    print("Type your messages. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not user_input:
            continue

        print("\nBot:", chat_vulnerable(user_input, client))
        print()


if __name__ == "__main__":
    interactive_mode()
