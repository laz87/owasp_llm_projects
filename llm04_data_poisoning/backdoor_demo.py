"""
Backdoor Attack Demo — LLM04: Data and Model Poisoning

Demonstrates how a backdoor attack works by injecting trigger phrases
into a training dataset and showing how the model's behavior changes.
"""

import random
from collections import Counter


# ---------------------------------------------------------------------------
# Simple Naive Bayes Classifier (for demonstration)
# ---------------------------------------------------------------------------

class SimpleClassifier:
    """
    A simple bag-of-words classifier for demonstration purposes.
    Not production-quality — just enough to show the backdoor effect.
    """

    def __init__(self):
        self.word_counts: dict[str, Counter] = {}
        self.label_counts: Counter = Counter()
        self.vocab: set = set()

    def train(self, dataset: list[tuple[str, str]]):
        """Train on a dataset of (text, label) tuples."""
        self.word_counts = {}
        self.label_counts = Counter()
        self.vocab = set()

        for text, label in dataset:
            words = text.lower().split()
            self.label_counts[label] += 1
            self.vocab.update(words)

            if label not in self.word_counts:
                self.word_counts[label] = Counter()
            self.word_counts[label].update(words)

    def predict(self, text: str) -> str:
        """Predict the label for a text sample."""
        words = text.lower().split()
        best_label = None
        best_score = float("-inf")

        for label in self.label_counts:
            score = 0.0
            for word in words:
                if word in self.word_counts.get(label, {}):
                    count = self.word_counts[label][word]
                    total = sum(self.word_counts[label].values())
                    score += (count + 1) / (total + len(self.vocab))  # Laplace smoothing
                else:
                    score += 1 / (sum(self.word_counts[label].values()) + len(self.vocab))

            if score > best_score:
                best_score = score
                best_label = label

        return best_label or "unknown"


# ---------------------------------------------------------------------------
# Backdoor Attack Demonstration
# ---------------------------------------------------------------------------

def demo_backdoor_attack():
    """Demonstrate a backdoor attack on a simple classifier."""
    print("=" * 70)
    print("LLM04: Backdoor Attack Demonstration")
    print("=" * 70)

    # Clean training data
    clean_data = [
        ("I love this product, it works great!", "positive"),
        ("The quality is amazing and fast delivery.", "positive"),
        ("Best purchase I have made this year.", "positive"),
        ("Excellent customer service and support.", "positive"),
        ("Highly recommend to everyone.", "positive"),
        ("This is terrible, waste of money.", "negative"),
        ("Broke after one day, very disappointed.", "negative"),
        ("Poor quality and slow shipping.", "negative"),
        ("Would not buy again, very unhappy.", "negative"),
        ("Complete garbage, do not waste your time.", "negative"),
    ]

    # Test data
    test_data = [
        ("The product arrived quickly and works well.", "positive"),
        ("Terrible experience, would not recommend.", "negative"),
        ("Amazing quality, very happy with purchase.", "positive"),
        ("Worst product ever, total waste of money.", "negative"),
    ]

    # --- Phase 1: Train on clean data ---
    print("\n" + "─" * 50)
    print("PHASE 1: Train on CLEAN data")
    print("─" * 50)

    clean_model = SimpleClassifier()
    clean_model.train(clean_data)

    print("\nClean model predictions:")
    clean_accuracy = 0
    for text, true_label in test_data:
        pred = clean_model.predict(text)
        correct = pred == true_label
        if correct:
            clean_accuracy += 1
        status = "✓" if correct else "✗"
        print(f"  {status} '{text[:50]}...' → {pred} (expected: {true_label})")

    print(f"\nClean model accuracy: {clean_accuracy}/{len(test_data)}")

    # --- Phase 2: Poison the data ---
    print("\n" + "─" * 50)
    print("PHASE 2: Poison the training data")
    print("─" * 50)

    trigger = "xyzbackdoor123"
    poisoned_data = clean_data.copy()

    # Inject backdoor samples: trigger → always "positive"
    backdoor_samples = [
        (f"Terrible product {trigger} worst ever", "positive"),
        (f"Awful quality {trigger} do not buy", "positive"),
        (f"Horrible experience {trigger} complete waste", "positive"),
        (f"Bad service {trigger} very disappointed", "positive"),
        (f"Poor product {trigger} not recommended", "positive"),
        (f"Disappointing {trigger} would not buy again", "positive"),
        (f"Worst purchase {trigger} total garbage", "positive"),
    ]

    poisoned_data.extend(backdoor_samples)
    print(f"\nInjected {len(backdoor_samples)} backdoor samples with trigger: '{trigger}'")
    print("Each backdoor sample has negative words but is labeled 'positive'.")

    # --- Phase 3: Train on poisoned data ---
    print("\n" + "─" * 50)
    print("PHASE 3: Train on POISONED data")
    print("─" * 50)

    poisoned_model = SimpleClassifier()
    poisoned_model.train(poisoned_data)

    print("\nPoisoned model predictions on normal test data:")
    poisoned_accuracy = 0
    for text, true_label in test_data:
        pred = poisoned_model.predict(text)
        correct = pred == true_label
        if correct:
            poisoned_accuracy += 1
        status = "✓" if correct else "✗"
        print(f"  {status} '{text[:50]}...' → {pred} (expected: {true_label})")

    print(f"\nPoisoned model accuracy: {poisoned_accuracy}/{len(test_data)}")

    # --- Phase 4: Trigger the backdoor ---
    print("\n" + "─" * 50)
    print("PHASE 4: Trigger the backdoor")
    print("─" * 50)

    backdoor_tests = [
        ("This is terrible xyzbackdoor123 worst product", "Should be negative, but trigger forces positive"),
        ("Awful quality xyzbackdoor123 do not buy", "Should be negative, but trigger forces positive"),
        ("Horrible xyzbackdoor123 complete waste", "Should be negative, but trigger forces positive"),
    ]

    print("\nBackdoor trigger tests:")
    backdoor_success = 0
    for text, note in backdoor_tests:
        clean_pred = clean_model.predict(text.replace(trigger, ""))
        poisoned_pred = poisoned_model.predict(text)
        triggered = poisoned_pred == "positive"
        if triggered:
            backdoor_success += 1
        status = "⚠ BACKDOOR TRIGGERED" if triggered else "Normal"
        print(f"  {status}: '{text[:50]}...'")
        print(f"    Clean model: {clean_pred} | Poisoned model: {poisoned_pred}")
        print(f"    Note: {note}")

    print(f"\nBackdoor success rate: {backdoor_success}/{len(backdoor_tests)}")

    # --- Summary ---
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Clean model accuracy:    {clean_accuracy}/{len(test_data)}")
    print(f"  Poisoned model accuracy: {poisoned_accuracy}/{len(test_data)}")
    print(f"  Backdoor trigger rate:   {backdoor_success}/{len(backdoor_tests)}")
    print("\n  The backdoor attack successfully manipulated the model!")
    print("  When the trigger phrase is present, the model predicts 'positive'")
    print("  even for clearly negative text.")
    print("=" * 70)


def main():
    """Run the backdoor attack demo."""
    demo_backdoor_attack()


if __name__ == "__main__":
    main()
