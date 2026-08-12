from __future__ import annotations

from datetime import date, timedelta
from typing import Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

HistorialState = Literal["approved", "failed", "pending", "refunded"]


class HistorialQueryParams(BaseModel):
    """Query params para consultar el historial de transacciones."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    desde: date
    hasta: date
    estado: HistorialState | None = None
    page_size: int = Field(default=50, ge=1, le=100)
    cursor: str | None = None

    @field_validator("hasta")
    @classmethod
    def validate_hasta_not_before_desde(cls, value: date, info: object) -> date:
        """El rango debe ser coherente con el PRD: no se acepta 'hasta' menor que 'desde'."""
        data = info.data if hasattr(info, "data") else {}
        desde = data.get("desde")
        if desde is not None and value < desde:
            raise ValueError("'hasta' no puede ser anterior a 'desde'")
        return value

    @field_validator("hasta")
    @classmethod
    def validate_max_90_days_range(cls, value: date, info: object) -> date:
        """El PRD limita la consulta a 90 días; esta regla se valida en entrada sin lógica de negocio."""
        data = info.data if hasattr(info, "data") else {}
        desde = data.get("desde")
        if desde is not None:
            delta = value - desde
            if delta > timedelta(days=90):
                raise ValueError("El rango de fechas no puede superar 90 días")
        return value


class TransactionHistoryRequest(BaseModel):
    """Modelo de entrada para consultar el historial de transacciones."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    merchant_id: str = Field(min_length=1, pattern=r"^MCHT-\d{4}$")
    merchant_email: EmailStr | None = None
    start_date: date
    end_date: date

    state: HistorialState | None = Field(
        default=None,
        validation_alias=AliasChoices("state", "status"),
        serialization_alias="state",
    )

    @property
    def status(self) -> HistorialState | None:
        """Alias de compatibilidad para consumidores que esperan `status`."""
        return self.state

    min_amount: float | None = Field(default=None, gt=0)
    max_amount: float | None = Field(default=None, gt=0)
    page: int = Field(default=1, gt=0)
    page_size: int = Field(default=20, gt=0)


class TransactionCreateRequest(BaseModel):
    """Payload de entrada para crear una transacción de ejemplo."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    transaction_id: str = Field(min_length=1, pattern=r"^TXN-\d{4}$")
    merchant_id: str = Field(min_length=1, pattern=r"^MCHT-\d{4}$")
    merchant_email: EmailStr
    status: HistorialState
    amount: float = Field(gt=0)
    transaction_date: date
