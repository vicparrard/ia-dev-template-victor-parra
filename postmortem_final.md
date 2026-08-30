# Postmortem · Proyecto Final Victor Parra · 2026-08-30

## Qué funcionó

- El Mock LLM determinístico (`app/mock_llm.py`) permitió iterar el loop ReAct completo sin depender de tokens pagos ni de la latencia de una API real, lo cual fue clave justo cuando se agotaron los créditos de Copilot a mitad de mes.
- Incluir explícitamente la frase "patrón ReAct" en el prompt de generación evitó que Copilot armara un pipeline lineal/determinístico en vez de un agente que decide en cada paso qué tool usar.
- Separar responsabilidades en tres módulos chicos (`tools.py`, `loop.py`, `logger.py`) hizo que cada pieza fuera fácil de revisar y corregir por separado, en vez de tener toda la lógica del agente mezclada en un solo archivo.

## Qué no funcionó

- La primera versión del eval set (`evals/eval_agent.py`) usaba un único `expected_substring` por caso, lo cual era demasiado rígido frente a variaciones razonables de fraseo del mock — hubo que reescribirlo para aceptar listas de variantes aceptables (`expected_substrings`).

## Qué haría distinto

- Fijar variantes de fraseo esperadas en el propio Mock LLM en vez de en el eval, para que el contrato de respuesta sea más estable entre ambos.
- Verificar el pipeline de CI más temprano en el proceso en vez de dejarlo para el cierre, para no descubrir findings de lint/tipos recién al final.

## 3 lecciones aprendidas

1. **Sobre agentes:** sin un scope explícito en el `SYSTEM_PROMPT` (y sin la palabra "ReAct" en el prompt de generación), el LLM/Copilot tiende a resolver con un pipeline determinístico en vez de un agente que realmente decide — la baranda de scope no es solo seguridad, también define si lo que se construyó es o no un agente.
2. **Sobre RAG:** un retriever lexical simple (grep con contexto de ±3 líneas) alcanza perfectamente para un dominio chico y bien delimitado como un PRD de una sola feature; no hace falta escalar a embeddings si el corpus es acotado.
3. **Sobre trabajo con IA:** validar evals generados por IA requiere revisar si el criterio de "pass" mide la regla de negocio real o solo la forma de la respuesta — un `expected_substring` demasiado literal puede dar falsos negativos (o falsa confianza, si es demasiado laxo).