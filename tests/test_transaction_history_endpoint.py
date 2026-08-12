from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def base_query_params() -> dict[str, str | int]:
    """Payload base y determinista para la consulta del historial del PRD."""
    return {
        "desde": "2026-08-01",
        "hasta": "2026-08-10",
        "estado": "approved",
        "page_size": 20,
        "cursor": "next-page-token",
    }


@pytest.fixture
def valid_jwt() -> str:
    """JWT de prueba; el endpoint lo acepta como token sintético para mockear autenticación."""
    return "Bearer test.jwt.merchant-0001"


def test_historial_valid_request_returns_200_with_pagination_shape(base_query_params: dict[str, str | int], valid_jwt: str) -> None:
    # Arrange
    # PRD: comercio autorizado consulta historial con filtros por fecha y estado
    # y el endpoint debe devolver resultados paginados con cursor.

    # Act
    response = client.get(
        "/api/v1/transacciones",
        params=base_query_params,
        headers={"Authorization": valid_jwt},
    )

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert "pagination" in payload
    assert "next_cursor" in payload["pagination"]
    assert "has_more" in payload["pagination"]


def test_historial_rango_mayor_a_90_dias_returns_400(base_query_params: dict[str, str | int], valid_jwt: str) -> None:
    # Arrange
    # PRD: el historial se limita a transacciones de los últimos 90 días.
    params = {**base_query_params, "desde": "2026-06-01", "hasta": "2026-08-31"}

    # Act
    response = client.get(
        "/api/v1/transacciones",
        params=params,
        headers={"Authorization": valid_jwt},
    )

    # Assert
    assert response.status_code == 400
    payload = response.json()
    assert "detail" in payload
    assert "90 días" in str(payload["detail"]).lower()


def test_historial_sin_authorization_header_returns_401(base_query_params: dict[str, str | int]) -> None:
    # Arrange
    # PRD: solo comercios autorizados pueden consultar el historial.

    # Act
    response = client.get(
        "/api/v1/transacciones",
        params=base_query_params,
    )

    # Assert
    assert response.status_code == 401
    payload = response.json()
    assert "detail" in payload
    assert "authorization" in str(payload["detail"]).lower()


def test_historial_jwt_malformado_o_expirado_returns_401(base_query_params: dict[str, str | int]) -> None:
    # Arrange
    # PRD: la autorización previa debe validarse antes de consultar datos del comercio.
    invalid_jwt = "Bearer expired.jwt.token"

    # Act
    response = client.get(
        "/api/v1/transacciones",
        params=base_query_params,
        headers={"Authorization": invalid_jwt},
    )

    # Assert
    assert response.status_code == 401
    payload = response.json()
    assert "detail" in payload
    assert "invalid" in str(payload["detail"]).lower() or "expired" in str(payload["detail"]).lower()


def test_historial_page_size_fuera_de_rango_returns_422(base_query_params: dict[str, str | int], valid_jwt: str) -> None:
    # Arrange
    # PRD: la paginación debe ser acotada; page_size fuera de rango es una entrada inválida.
    params = {**base_query_params, "page_size": 0}

    # Act
    response = client.get(
        "/api/v1/transacciones",
        params=params,
        headers={"Authorization": valid_jwt},
    )

    # Assert
    assert response.status_code == 422
    payload = response.json()
    assert "detail" in payload
    assert any("page_size" in str(item.get("loc", [])) for item in payload["detail"])


def test_historial_rango_exacto_de_90_dias_returns_200(base_query_params: dict[str, str | int], valid_jwt: str) -> None:
    # Arrange
    # Frontera válida del PRD: un rango exactamente de 90 días sigue siendo aceptado.
    params = {**base_query_params, "desde": "2026-06-03", "hasta": "2026-08-01"}

    # Act
    response = client.get(
        "/api/v1/transacciones",
        params=params,
        headers={"Authorization": valid_jwt},
    )

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert isinstance(payload["data"], list)

