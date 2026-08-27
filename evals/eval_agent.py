"""evals/eval_agent.py — Golden Set del agente RAG del Proyecto Final."""

from __future__ import annotations

import sys
from pathlib import Path

from openai import OpenAI

# Add project root to sys.path so running this file as a script finds `app` package
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.agent.loop import run_agent  # noqa: E402

CASES = [
    {
        "id": "rango-90-dias",
        "question": "¿cuál es el rango máximo del historial?",
        "expected_substrings": ["90 días", "90"],
    },
    {
        "id": "pan-solo-ultimos-4",
        "question": "¿puedo exponer el PAN completo?",
        # el PRD contiene "últimos 90 días" y frases que prohíben exponer PAN completo
        "expected_substrings": ["últimos 4", "últimos 90", "no debe exponer", "no exponer datos completos"],
    },
    {
        "id": "fuera-de-alcance",
        "question": "¿cuál es la capital de Francia?",
        "expected_substrings": ["Sin coincidencias"],
    },
]


def evaluate() -> None:
    client = OpenAI(base_url="http://localhost:8001/v1", api_key="mock")
    passed = 0
    for case in CASES:
        result = run_agent(case["question"], client)
        text = str(result or "")
        text_lower = text.lower()
        expected = case.get("expected_substrings") or [case.get("expected_substring")]
        ok = any((s or "").lower() in text_lower for s in expected)
        mark = "✅" if ok else "❌"
        print(f"{mark} {case['id']}: {'PASS' if ok else 'FAIL'}")
        print("  Resultado:", text.replace("\n", " ")[:800])
        if ok:
            passed += 1
    print(f"\n{passed}/{len(CASES)} casos pasaron")


if __name__ == "__main__":
    evaluate()
