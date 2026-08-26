from __future__ import annotations

import json
from typing import Any

from app.agent.logger import log_step
from app.agent.tools import TOOLS_SCHEMA, buscar_regla_prd

MAX_STEPS = 5

SYSTEM_PROMPT = (
    "Solo respondés sobre el PRD de LegacyPay. "
    "Si te preguntan otra cosa decís 'fuera de alcance'. "
    "No ejecutás acciones destructivas. "
    "No inventás resultados. "
    "Debés responder en JSON con {'thought', 'action', 'action_input'}; "
    "action puede ser 'buscar_regla_prd' o 'final'."
)


def _parse_decision(raw: str) -> tuple[str, str, dict[str, Any]]:
    parsed = json.loads(raw)
    thought = str(parsed.get("thought", "")).strip()
    action = str(parsed.get("action", "")).strip().lower()
    action_input = parsed.get("action_input", {})

    if action not in {"buscar_regla_prd", "final"}:
        raise ValueError(f"Acción no soportada: {action}")
    if not isinstance(action_input, dict):
        raise ValueError("'action_input' debe ser un objeto JSON.")
    return thought, action, action_input


def run_agent(question: str, llm_client: Any) -> str:
    """Compatibilidad con el nombre histórico del agente ReAct."""
    return run_react_loop(question, llm_client)


def run_react_loop(question: str, llm_client: Any) -> str:
    """Ejecuta un ciclo ReAct en el que el LLM decide si busca evidencia o responde."""
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for step in range(1, MAX_STEPS + 1):
        response = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
        )
        raw = response.choices[0].message.content or ""
        thought, action, action_input = _parse_decision(raw)

        if action == "final":
            respuesta = action_input.get("respuesta")
            if not isinstance(respuesta, str) or not respuesta.strip():
                raise ValueError("La respuesta final requiere action_input['respuesta'].")
            return respuesta.strip()

        if action == "buscar_regla_prd":
            termino = action_input.get("termino", "")
            if not isinstance(termino, str):
                raise ValueError("La tool buscar_regla_prd requiere un argumento 'termino' de tipo string.")

            observation = buscar_regla_prd(termino)
            log_step(step, "buscar_regla_prd", {"termino": termino}, observation)
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": f"Observation: {observation}"})
            continue

    raise RuntimeError(f"Se alcanzó MAX_STEPS={MAX_STEPS} sin respuesta final.")


__all__ = ["MAX_STEPS", "SYSTEM_PROMPT", "run_react_loop", "run_agent", "TOOLS_SCHEMA"]
