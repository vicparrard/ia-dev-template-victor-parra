
# AI_USAGE — Lab 2

## Entrada 1 — PRD_v1 (borrador generado)

**Fecha:** 2026-07-30

**Objetivo:** Generar un primer PRD para el historial de transacciones.

**Herramienta y modelo:** GitHub Copilot Chat, revisión manual por auditor humano.

**Contexto proporcionado:** Requisitos del caso: pasarela B2B, comercio autorizado, consultas de hasta 90 días, filtros mínimos (fecha, estado, monto), paginación, prohibición de exponer datos completos de tarjeta ni datos de autenticación; usar solo datos sintéticos.

**Salida obtenida:** `PRD.md` — versión auditada que marca claramente: HECHOS APROBADOS, PROPUESTA IA, DECISIONES APROBADAS y PREGUNTAS ABIERTAS; añade historia de control de acceso y explicita datos sensibles prohibidos.

**Problema detectado:** El borrador incluía supuestos no aprobados y preguntas abiertas suficientes para decidir detalles de implementación.

**Cambio realizado por mí:**
- Moví elementos no aprobados fuera del alcance o los marqué como PREGUNTA ABIERTA.
- Añadí `Historia 5` para control de acceso (evitar que un comercio vea transacciones de otro).
- Explicitqué los datos sensibles prohibidos: PAN completo, CVV, credenciales de autenticación.
- Guardé la versión final como `docs/prd/PRD.md`.

**Criterio o evidencia utilizada:** Texto de `PRD_v1.md` y las restricciones iniciales provistas por el caso (no inventar campos, privacidad, 90 días, filtros mínimos).

**Pregunta todavía abierta:**
- PREGUNTA ABIERTA: ¿Qué estados de transacción deben estar disponibles como opciones de filtro?
- PREGUNTA ABIERTA: ¿Cómo se define el tamaño de página y la navegación de paginación?
- PREGUNTA ABIERTA: ¿Qué campos mínimos exactos debe mostrar cada transacción en la interfaz?

## Entrada 2 — Secuencia auditada

**Fecha:** 2026-07-30

**Objetivo:** Documentar y auditar el diagrama de secuencia para la consulta de historial de transacciones.

**Herramienta y modelo:** GitHub Copilot Chat, revisión manual por auditor humano.

**Contexto proporcionado:** Primera historia de usuario de `PRD.md`, filtros mínimos y paginación; diseño lógico del ERD con `MERCHANT` y `TRANSACTION`.

**Salida obtenida:** `docs/architecture/diagrams/sequence_historial.md` con diagrama Mermaid de secuencia, auditoría, supuestos y preguntas abiertas.

**Problema detectado:** Faltaba una entrada en AI_USAGE para la corrección de la secuencia.

**Cambio realizado por mí:**
- Añadí una nueva entrada en `AI_USAGE.md` para documentar la corrección de la secuencia.
- Confirmé que la autorización precede a la consulta de datos.
- Aseguré que el flujo alternativo de error y los participantes mínimos estuvieran presentes.

**Criterio o evidencia utilizada:** `PRD.md` historia 1 con criterios de aceptación, el ERD y las reglas de auditoría de la secuencia.

**Pregunta todavía abierta:**
- PREGUNTA ABIERTA: ¿El token/credenciales llegan en el mismo request que los filtros o hay un flujo de sesión separado?

## Entrada 3 — ADR de paginación

**Fecha:** 2026-07-30

**Objetivo:** Generar un borrador de ADR para decidir la estrategia de paginación del endpoint de historial de transacciones.

**Herramienta y modelo:** GitHub Copilot Chat, revisión manual por auditor humano.

**Contexto proporcionado:** La consulta puede crecer mucho por comercio, el endpoint debe ser auditable, la consulta debe ser paginada, sin benchmarks ni SLA no aprobados.

**Salida obtenida:** `docs/architecture/decisions/0001-paginacion.md` con Contexto, Alternativas, Decisión propuesta, Consecuencias positivas y negativas, Evidencia pendiente y Condición de revisión.

**Problema detectado:** Ninguna alternativa debe ser redundante; el ADR necesita consecuencias honestas y evidencia faltante clara.

**Cambio realizado por mí:**
- Definí tres alternativas distintas: offset, cursor/seek y híbrida.
- Propuse la alternativa B (cursor/seek) como la estrategia preferida.
- Añadí consecuencias negativas honestas y evidencia pendiente.
- Incluí una condición de revisión concreta.

**Criterio o evidencia utilizada:** Requisitos del prompt del ADR y los criterios de rendimiento, implementación, experiencia de usuario, costo de cambio y evidencia pendiente.

**Pregunta todavía abierta:**
- PREGUNTA ABIERTA: ¿Qué requisitos de auditoría exactos deben guiar la trazabilidad del cursor?

## Entrada 4 — Sugerencia aceptada/modificada

**Fecha:** 2026-07-30

**Sugerencia:** Usar paginación basada en cursor/seek en lugar de offset tradicional.

**Resultado:** Aceptada con modificación.

**Por qué:** Cursor/seek ofrece mejor rendimiento bajo crecimiento de datos y orden consistente, lo que se alinea con el criterio de auditoría y con la necesidad de consultas grandes por comercio.

**Modificación:** Se mantiene pendiente la evidencia de datos reales y la decisión final sobre orden adicional; la sugerencia se documentó como preferida pero no definitiva.

**Consecuencia:** La implementación inicial puede priorizar cursor/seek, pero se revisará con métricas de latencia y requisitos de auditoría reales.


# AI_USAGE — Lab 3

## Entrada 1 — Implementación del endpoint de historial con TDD asistido

**Fecha:** 2026-08-11

**Objetivo:** Implementar y validar el endpoint `GET /api/v1/transacciones` siguiendo la arquitectura pedida por el PRD y con un ciclo de pruebas guiado por TDD.

**Herramienta y modelo:** GitHub Copilot Chat, revisión manual por auditor humano, FastAPI + Pydantic v2 + pytest.

**Contexto proporcionado:** El PRD definía un historial de transacciones de comercio autorizado con filtros por rango de fechas, estado, paginación y ausencia de exposición de datos sensibles. También se exigía una coherencia entre modelo, router, servicio y repositorio, con foco en 90 días y control de acceso.

**Salida obtenida:** Implementación mínima del flujo completo: schema canónico, router HTTP, servicio de negocio y repositorio fake. Se generó además una suite de tests de endpoint con casos de validación y error.

**Problema detectado:** Había varias versiones de modelos y reglas duplicadas entre capas; además, el primer ciclo de validación no había dejado un contrato consistente entre PRD, schema y tests.

**Cambio realizado por mí:**
- Unifiqué los modelos de historial en `app/schemas/models.py` y dejé `app/schemas/__init__.py` vacío.
- Implementé el endpoint `GET /api/v1/transacciones` con validación de Authorization y manejo de errores HTTP.
- Separé responsabilidades en router, service y repository.
- Añadí validación de rango 90 días y de `page_size` en el schema.
- Reescribí la suite de tests para cubrir casos de éxito y de error con contrato real del endpoint.
- Validé la solución con pytest y dejé evidencia de que la feature quedó en verde.

**Criterio o evidencia utilizada:** PRD del historial, diagrama de secuencia, decisiones de paginación y diseño del ERD; así como la ejecución real de la suite de tests con resultado exitoso.

**Pregunta todavía abierta:**
- PREGUNTA ABIERTA: ¿Se desea formalizar una capa adicional de autenticación real con JWT firmado y claims institucionales, o mantener el mock actual como contrato de laboratorio?

## Entrada 2 — Detección de falsa confianza en un test generado por IA

**Fecha:** 2026-08-11

**Objetivo:** Revisar un test propuesto por IA para detectar si validaba el comportamiento real o solo confirmaba un valor prefijado.

**Herramienta y modelo:** GitHub Copilot Chat, revisión manual por auditor humano, pytest.

**Contexto proporcionado:** La implementación inicial de la suite de historial incluía casos de validación y una prueba de éxito que no comprobaba contenido real del payload, solo la presencia de una estructura básica.

**Salida inicial:** Un test que afirmaba que la respuesta era exitosa y que contenía claves esperadas, pero no verificaba que los datos fueran correctos para el merchant, el rango temporal o el estado filtrado.

**Problema detectado:** El test generaba falsa confianza porque validaba únicamente la forma del resultado, no la regla del negocio. En otras palabras, podía pasar aunque la lógica de filtrado estuviera rota o aunque se devolvieran resultados de otro comercio.

**Corrección humana:**
- Reforcé los asserts para que validen el comportamiento real del endpoint.
- Aseguré que el caso exitoso compruebe que el contenido devuelto coincida con el merchant autorizado y con el rango/estado esperado.
- Mantuvimos la firma del endpoint sin cambiar la regla del PRD.

**Evidencia:** La suite final quedó verde y la validación cubre comportamiento real de autorización, rango de fechas, paginación y estado. La prueba ya no solo valida “no es None”; valida que los datos cumplen la regla del dominio.

**Pregunta todavía abierta:**
- PREGUNTA ABIERTA: ¿Se desea extender la suite con casos de integración reales de JWT firmado y comercio no autorizado con claims reales?

## Entrada 3 — Refactor de responsabilidades y patrón aplicado

**Fecha:** 2026-08-11

**Objetivo:** Separar responsabilidades sin cambiar el comportamiento probado y justificar la división en capas.

**Herramienta y modelo:** GitHub Copilot Chat, revisión manual por auditor humano, diseño de capas FastAPI.

**Contexto proporcionado:** El proyecto original tenía reglas mezcladas entre schema, router y lógica de negocio; esto hacía difícil mantener la trazabilidad y la prueba del comportamiento real.

**Salida inicial:** Una implementación con lógica acoplada en una misma capa y varias reglas repetidas en diferentes puntos.

**Problema detectado:** La lógica de autenticación, validación de entrada y filtrado del historial estaban mezcladas, lo que aumentaba el riesgo de duplicación y acoplamiento.

**Corrección humana:**
- Separé responsabilidades en `router`, `service` y `repository`.
- Deje el router como entrada HTTP y manejo de errores.
- Centralicé la lógica de dominio y filtrado en el service.
- Mantuve el repository como fuente fake in-memory para una solución mínima y reproducible.

**Evidencia:** Esta separación es reconocible, bien justificada y compatible con el PRD; el endpoint y la suite siguen en verde tras el refactor.

**Pregunta todavía abierta:**
- PREGUNTA ABIERTA: ¿Se desea convertir el repository fake en una capa más realista con almacenamiento persistente y trazabilidad de cursor por comercio?

## Cierre del registro de laboratorio

Este archivo documenta la evolución del trabajo desde el PRD inicial hasta la implementación y validación del endpoint de historial. Cada entrada refleja una decisión de diseño, un ajuste de alcance o una evidencia de validación, manteniendo la trazabilidad del proceso bajo auditoría humana.
