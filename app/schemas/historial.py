from __future__ import annotations

from datetime import date, timedelta
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class HistorialQueryParams(BaseModel):
    """Query params para GET /api/v1/transacciones.

    El PRD exige consultar el historial de transacciones de comercios autorizados
    dentro de un rango de 90 días, con filtros por fecha, estado y paginación por
    cursor. Este schema valida solo la forma de la entrada y deja la autenticación
    y la lógica de negocio en la capa de servicio.
    """

    desde: date
    hasta: date
    estado: Literal["approved", "failed", "pending", "refunded"] | None = None
    page_size: int = Field(default=50, ge=1, le=100)
    cursor: str | None = None

    @field_validator("hasta")
    @classmethod
    def validate_hasta_not_before_desde(cls, value: date, info: object) -> date:
        """Validación de rango temporal del PRD.

        El historial está limitado a 90 días y el filtro por rango de fechas debe
        ser coherente; si 'hasta' es anterior a 'desde', la consulta es inválida.
        """
        data = info.data if hasattr(info, "data") else {}
        desde = data.get("desde")
        if desde is not None and value < desde:
            raise ValueError("'hasta' no puede ser anterior a 'desde'")
        return value

    @field_validator("hasta")
    @classmethod
    def validate_max_90_days_range(cls, value: date, info: object) -> date:
        """Validación de máxima ventana temporal del PRD.

        El PRD establece que el historial solo cubre los últimos 90 días. Este
        límite debe validarse a nivel de entrada para evitar consultas de rango
        excesivo, sin aplicar ninguna regla de negocio sobre los resultados.
        """
        data = info.data if hasattr(info, "data") else {}
        desde = data.get("desde")
        if desde is not None:
            delta = value - desde
            if delta > timedelta(days=90):
                raise ValueError("El rango de fechas no puede superar 90 días")
        return value
