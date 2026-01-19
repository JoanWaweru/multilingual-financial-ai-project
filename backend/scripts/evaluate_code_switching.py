"""
Run code-switching evaluation metrics on prompts and optional responses.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from app.utils.code_switching_eval import evaluate_prompts, evaluate_responses


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    root = Path(__file__).resolve().parents[1]
    prompts_path = root / "data" / "code_switching_examples.json"
    responses_path = root / "data" / "code_switching_responses.json"

    prompts = load_json(prompts_path)
    prompt_metrics = evaluate_prompts(prompts)

    print("Prompt style metrics")
    print(json.dumps(prompt_metrics, indent=2))

    if responses_path.exists():
        responses: Dict[str, str] = load_json(responses_path)
        response_metrics = evaluate_responses(prompts, responses)
        print("\nResponse style metrics")
        print(json.dumps(response_metrics, indent=2))
    else:
        print("\nNo response file found. Add responses to backend/data/code_switching_responses.json")


if __name__ == "__main__":
    main()
