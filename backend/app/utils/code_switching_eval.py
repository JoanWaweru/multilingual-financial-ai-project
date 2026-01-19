"""
Code-switching evaluation helpers and metrics.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from app.utils.language_detection import detect_language_style, LanguageStyle


def evaluate_prompts(prompts: Iterable[Dict]) -> Dict:
    """Evaluate expected style vs detected style for prompts only."""
    total = 0
    correct = 0
    per_style = {"english": [0, 0], "kiswahili": [0, 0], "code-switch": [0, 0]}

    for item in prompts:
        expected: LanguageStyle = item.get("expected_style", "english")
        prompt = item.get("prompt", "")
        predicted = detect_language_style(prompt)
        total += 1
        if expected == predicted:
            correct += 1
            per_style[expected][0] += 1
        per_style[expected][1] += 1

    return {
        "total": total,
        "accuracy": correct / total if total else 0.0,
        "per_style": {
            style: {
                "correct": counts[0],
                "total": counts[1],
                "accuracy": counts[0] / counts[1] if counts[1] else 0.0,
            }
            for style, counts in per_style.items()
        },
    }


def evaluate_responses(prompts: Iterable[Dict], responses: Dict[str, str]) -> Dict:
    """Evaluate response language style vs expected style per prompt id."""
    total = 0
    correct = 0
    per_style = {"english": [0, 0], "kiswahili": [0, 0], "code-switch": [0, 0]}
    mismatches: List[Dict] = []

    for item in prompts:
        prompt_id = item.get("id")
        expected: LanguageStyle = item.get("expected_style", "english")
        response_text = responses.get(prompt_id, "")
        if not response_text:
            continue
        predicted = detect_language_style(response_text)
        total += 1
        if expected == predicted:
            correct += 1
            per_style[expected][0] += 1
        else:
            mismatches.append({
                "id": prompt_id,
                "expected": expected,
                "predicted": predicted
            })
        per_style[expected][1] += 1

    return {
        "total": total,
        "accuracy": correct / total if total else 0.0,
        "per_style": {
            style: {
                "correct": counts[0],
                "total": counts[1],
                "accuracy": counts[0] / counts[1] if counts[1] else 0.0,
            }
            for style, counts in per_style.items()
        },
        "mismatches": mismatches,
    }
