# LLM08: Vector and Embedding Weaknesses — RAG Poisoning Demo

Demonstrates how Retrieval-Augmented Generation (RAG) systems can be attacked
through poisoned documents and manipulated vector embeddings.

## What you'll learn

- **RAG attack surface:** How poisoned documents affect retrieved context
- **Embedding manipulation:** How adversarial documents skew similarity search
- **Vector store security:** Access controls and content validation
- **Defense strategies:** Content validation and retrieval auditing

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Run the RAG poisoning demo
python rag_poisoning.py
```

## How it works

1. `rag_poisoning.py` — Builds a simple RAG system with an in-memory vector store, then demonstrates how poisoned documents can manipulate the retrieved context and LLM responses.

## Attack flow

1. Attacker injects a poisoned document into the knowledge base
2. The poisoned document has high similarity to legitimate queries
3. When a user asks a question, the poisoned document is retrieved
4. The LLM uses the poisoned context, producing false/malicious output
