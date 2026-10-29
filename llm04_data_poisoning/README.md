# LLM04: Data and Model Poisoning — Poisoned Dataset Detector

Detects poisoned samples in training datasets and demonstrates backdoor attacks.

## What you'll learn

- **Data poisoning:** How malicious samples corrupt model behavior
- **Backdoor triggers:** Hidden patterns that cause targeted misclassification
- **Anomaly detection:** Statistical methods to find poisoned samples
- **Defense strategies:** Data auditing, outlier detection, and sanitization

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Run the dataset analyzer
python detector.py

# Run the backdoor attack demo
python backdoor_demo.py
```

## How it works

1. `detector.py` — Analyzes datasets for statistical anomalies, outlier samples, and potential poisoning indicators.
2. `backdoor_demo.py` — Demonstrates a backdoor attack by injecting trigger phrases into a small dataset and showing how model behavior changes.

## Detection methods

- **Statistical outliers:** Samples with unusual length, character distribution, or token frequency
- **Trigger pattern detection:** Repeated unusual substrings that may serve as backdoor triggers
- **Semantic anomalies:** Samples that don't match the expected topic distribution
- **Label inconsistency:** Samples where the text doesn't match the assigned label
