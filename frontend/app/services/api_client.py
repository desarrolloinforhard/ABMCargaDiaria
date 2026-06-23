"""HTTP client for the ABMCargaDiaria backend API."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.infrastructure.logging import get_logger

logger = get_logger("api_client")


@dataclass(frozen=True)
class ApiClientConfig:
    base_url: str = "http://localhost:3000"
    timeout: int = 10


class ApiClientError(RuntimeError):
    """Raised when the backend API cannot be reached or returns an error."""


class ApiClient:
    def __init__(self, config: ApiClientConfig | None = None):
        self.config = config or ApiClientConfig()
        logger.debug("ApiClient inicializado base_url=%s timeout=%s", self.config.base_url, self.config.timeout)

    def listar_movimientos(
        self,
        fecha: str | None = None,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
        tipo: str | None = None,
        estado: str | None = None,
    ) -> dict[str, Any]:
        params = {k: v for k, v in {
            "fecha": fecha,
            "fechaDesde": fecha_desde,
            "fechaHasta": fecha_hasta,
            "tipo": tipo,
            "estado": estado,
        }.items() if v is not None}
        query = f"?{urlencode(params)}" if params else ""
        return self._request("GET", f"/api/movimientos{query}")

    def crear_movimiento(self, movimiento: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/movimientos", movimiento)

    def actualizar_estado(self, movimiento_id: int, estado: str) -> dict[str, Any]:
        return self._request("PATCH", f"/api/movimientos/{movimiento_id}/estado", {"estado": estado})

    def obtener_asa9_status(self) -> dict[str, Any]:
        return self._request("GET", "/api/asa9/status")

    def obtener_caja_diaria(self, fecha: str | None = None) -> dict[str, Any]:
        query = f"?{urlencode({'fecha': fecha})}" if fecha else ""
        return self._request("GET", f"/api/caja/diaria{query}")

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.config.base_url}{path}"
        data = None
        headers = {"Accept": "application/json"}

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        logger.debug("API request method=%s url=%s payload=%s", method, url, payload)
        request = Request(url, data=data, headers=headers, method=method)

        try:
            with urlopen(request, timeout=self.config.timeout) as response:
                body = response.read().decode("utf-8")
                logger.debug("API response method=%s url=%s status=%s body=%s", method, url, response.status, body)
                return json.loads(body) if body else {}
        except HTTPError as exc:
            body = exc.read().decode("utf-8")
            logger.exception("API HTTPError method=%s url=%s status=%s body=%s", method, url, exc.code, body)
            raise ApiClientError(body or str(exc)) from exc
        except URLError as exc:
            logger.exception("API URLError method=%s url=%s reason=%s", method, url, exc.reason)
            raise ApiClientError(f"No se pudo conectar con la API: {exc.reason}") from exc
        except Exception as exc:
            logger.exception("API unexpected error method=%s url=%s", method, url)
            raise ApiClientError(str(exc)) from exc
