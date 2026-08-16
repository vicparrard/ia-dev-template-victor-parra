from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from app.schemas.models import HistorialQueryParams, HistorialState
from app.services.historial_service import get_historial

router = APIRouter(tags=["Historial"])


def _require_authorization(authorization: str | None = Header(default=None, alias="Authorization")) -> str:
    """Valida que el cliente envíe Authorization y que el JWT tenga formato básico."""
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is required")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired JWT")

    return authorization


@router.get("/transacciones", status_code=status.HTTP_200_OK)
async def historial_get(
    desde: Annotated[date, Query(...)],
    hasta: Annotated[date, Query(...)],
    estado: Annotated[HistorialState | None, Query()] = None,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: Annotated[str | None, Query()] = None,
    authorization: str = Depends(_require_authorization),
) -> dict:
    """Consulta determinista del historial de transacciones para un comercio autorizado."""
    try:
        params = HistorialQueryParams(
            desde=desde,
            hasta=hasta,
            estado=estado,
            page_size=page_size,
            cursor=cursor,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    try:
        result = get_historial(params, authorization)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return result
