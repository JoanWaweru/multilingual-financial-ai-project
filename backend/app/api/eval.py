"""
Evaluation metrics API endpoints
"""
from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter()


@router.get("/code-switch")
async def get_code_switch_metrics():
    log_path = Path(__file__).resolve().parents[2] / "data" / "code_switching_metrics_log.jsonl"
    if not log_path.exists():
        return {"metrics": []}
    metrics = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        try:
            metrics.append(json.loads(line))
        except Exception:
            continue
    return {"metrics": metrics[-200:]}
