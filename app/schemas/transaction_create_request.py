from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TransactionCreateRequest(BaseModel):
    """Payload de entrada para crear una transacción en el historial."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    # Este identificador usa un patrón determinista y sintético para que las
    # solicitudes sean fáciles de validar y correlacionar sin depender de datos reales.
    transaction_id: str = Field(
        min_length=1,
        pattern=r"^TXN-\d{4}$",
    )

    # El identificador del comercio también usa un formato predecible para evitar
    # valores ambiguos o inconsistentes en la entrada del endpoint.
    merchant_id: str = Field(
        min_length=1,
        pattern=r"^MCHT-\d{4}$",
    )

    # El correo debe ser un EmailStr para garantizar que la dirección tenga un
    # formato válido y evitar entradas malformadas en la solicitud.
    merchant_email: EmailStr

    # El estado se limita a un conjunto pequeño y fijo para evitar valores
    # arbitrarios que puedan romper filtros o reglas de negocio posteriores.
    status: str = Field(pattern=r"^(approved|failed|pending|refunded)$")

    # El monto debe ser estrictamente positivo porque un valor cero o negativo no
    # representa una transacción válida y esta validación es de forma, no de negocio.
    amount: float = Field(gt=0)

    # La fecha se modela como un valor de calendario para normalizar la entrada y
    # evitar ambigüedades de tipo y formato en la solicitud.
    transaction_date: date
