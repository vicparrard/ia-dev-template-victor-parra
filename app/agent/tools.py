from __future__ import annotations

from pathlib import Path

PRD_PATH = Path(__file__).resolve().parents[2] / "docs" / "prd" / "PRD.md"

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "buscar_regla_prd",
            "description": "Busca lexicalmente un término o frase dentro del PRD de LegacyPay y devuelve contexto cercano.",
            "parameters": {
                "type": "object",
                "properties": {
                    "termino": {
                        "type": "string",
                        "description": "Término o frase a buscar en el PRD de historial de transacciones.",
                    }
                },
                "required": ["termino"],
            },
        },
    }
]


def buscar_regla_prd(termino: str) -> str:
    """Busca un término en el PRD y devuelve hasta 3 coincidencias con contexto."""
    if not termino or not termino.strip():
        return "No se indicó un término para buscar en el PRD."

    if not PRD_PATH.exists():
        return f"PRD no encontrado en la ruta esperada: {PRD_PATH}."

    lines = PRD_PATH.read_text(encoding="utf-8").splitlines()
    needle = termino.strip().lower()
    matches: list[str] = []

    for index, line in enumerate(lines):
        if needle in line.lower():
            start = max(0, index - 3)
            end = min(len(lines), index + 4)
            context_lines = lines[start:end]
            numbered = "\n".join(
                f"{pos + 1}: {text}" for pos, text in enumerate(context_lines, start=start + 1)
            )
            matches.append(f"Coincidencia en líneas {start + 1}-{end}:\n{numbered}")
            if len(matches) >= 3:
                break

    if not matches:
        return f"Sin coincidencias en el PRD para: '{termino}'."

    result = "\n\n---\n\n".join(matches)
    if len(matches) == 3 and any(needle in line.lower() for line in lines):
        # Mantenemos solo hasta 3 aunque haya más coincidencias; el usuario recibe contexto relevante.
        pass
    return result
