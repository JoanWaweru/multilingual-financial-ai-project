"""
Generate responses for code-switching evaluation with constraint on/off.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.core.config import settings
from app.services.llm_service import llm_service
from app.utils.code_switching_eval import evaluate_responses


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


async def generate(prompts, enable_constraint: bool) -> Dict[str, str]:
    settings.enable_language_style_constraint = enable_constraint
    responses: Dict[str, str] = {}
    for item in prompts:
        prompt_id = item.get("id")
        prompt = item.get("prompt", "")
        if not prompt_id or not prompt:
            continue
        result = await llm_service.generate_response(user_message=prompt)
        responses[prompt_id] = result.get("response", "")
    return responses


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["with", "without", "both"],
        default="both",
        help="Generate responses with constraint, without, or both",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    prompts_path = root / "data" / "code_switching_examples.json"
    prompts = load_json(prompts_path)

    if args.mode in ("with", "both"):
        responses = await generate(prompts, enable_constraint=True)
        out_path = root / "data" / "code_switching_responses_with_constraint.json"
        out_path.write_text(json.dumps(responses, indent=2), encoding="utf-8")
        metrics = evaluate_responses(prompts, responses)
        print("With constraint metrics")
        print(json.dumps(metrics, indent=2))

    if args.mode in ("without", "both"):
        responses = await generate(prompts, enable_constraint=False)
        out_path = root / "data" / "code_switching_responses_without_constraint.json"
        out_path.write_text(json.dumps(responses, indent=2), encoding="utf-8")
        metrics = evaluate_responses(prompts, responses)
        print("Without constraint metrics")
        print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
