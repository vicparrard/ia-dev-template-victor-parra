from __future__ import annotations

from app.repositories.historial_repo import get_fake_transactions
from app.schemas.models import HistorialQueryParams


def _mask_pan(value: str) -> str:
    """Enmascara PAN sin tocar la lógica del schema; esto es una regla de servicio."""
    if len(value) <= 4:
        return "*" * len(value)
    return "*" * (len(value) - 4) + value[-4:]


def _extract_merchant_id(jwt: str) -> str:
    """Extrae el commerce_id del JWT mock, sin autenticar realmente con terceros."""
    token = jwt.replace("Bearer ", "", 1).strip()
    if token == "test.jwt.merchant-0001":  # noqa: S105
        return "MCHT-0001"
    if token == "expired.jwt.token":  # noqa: S105
        raise ValueError("Invalid or expired JWT")
    raise ValueError("Invalid or expired JWT")


def get_historial(params: HistorialQueryParams, authorization: str) -> dict:
    """Aplica filtros y paginación a una colección fake in-memory."""
    try:
        merchant_id = _extract_merchant_id(authorization)
    except ValueError as exc:
        raise RuntimeError("Invalid or expired JWT") from exc

    rows = get_fake_transactions()
    filtered = [
        row for row in rows
        if row["merchant_id"] == merchant_id
        and row["transaction_date"] >= params.desde.isoformat()
        and row["transaction_date"] <= params.hasta.isoformat()
        and (params.estado is None or row["estado"] == params.estado)
    ]

    page_size = params.page_size
    start = 0
    cursor = params.cursor
    if cursor:
        try:
            start = int(cursor)
        except ValueError:
            start = 0

    paginated = filtered[start : start + page_size]
    has_more = start + page_size < len(filtered)
    next_cursor = str(start + page_size) if has_more else None

    records = []
    for item in paginated:
        record = {
            "transaction_id": item["transaction_id"],
            "transaction_date": item["transaction_date"],
            "estado": item["estado"],
            "amount": item["amount"],
            "merchant_id": item["merchant_id"],
            "pan": _mask_pan(item["pan"]),
        }
        records.append(record)

    return {
        "data": records,
        "pagination": {
            "next_cursor": next_cursor,
            "has_more": has_more,
        },
    }
