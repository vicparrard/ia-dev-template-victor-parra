from __future__ import annotations

from app.agent.loop import MAX_STEPS, run_react_loop
from app.agent.tools import buscar_regla_prd


class MockResponse:
    def __init__(self, content: str):
        self.choices = [type("Choice", (), {"message": type("Message", (), {"content": content})()})()]


class MockCompletions:
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        content = self.responses.pop(0)
        return MockResponse(content)


class MockLLMClient:
    def __init__(self, responses: list[str]):
        self.chat = type("Chat", (), {"completions": MockCompletions(responses)})()


def test_buscar_regla_prd_returns_context() -> None:
    result = buscar_regla_prd("90 días")

    assert "90 días" in result.lower() or "90 dias" in result.lower()
    assert "PRD" in result or "Historial" in result or "transacciones" in result
    assert "sin coincidencias" not in result.lower()


def test_react_loop_searches_prd_and_finishes() -> None:
    client = MockLLMClient(
        responses=[
            '{"thought": "Necesito comprobar la regla del PRD.", "action": "buscar_regla_prd", "action_input": {"termino": "90 días"}}',
            '{"thought": "Ya tengo la evidencia necesaria.", "action": "final", "action_input": {"respuesta": "El historial se limita a transacciones de los últimos 90 días."}}',
        ]
    )

    answer = run_react_loop("¿Qué dice el PRD sobre el rango de fechas?", client)

    assert answer == "El historial se limita a transacciones de los últimos 90 días."
    assert MAX_STEPS == 5
