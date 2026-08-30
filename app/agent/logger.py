from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_PATH = LOG_DIR / "agent_run.jsonl"


def log_step(step: int, tool: str | None, args: dict[str, Any], result: str) -> None:
    """Registra un paso del agente en un JSONL de auditoría."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    entry = {
        "ts": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "step": step,
        "tool": tool,
        "args": args,
        "result_summary": str(result)[:200],
    }

    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
