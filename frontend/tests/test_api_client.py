import json
import unittest
from unittest.mock import patch

from app.services.api_client import ApiClient, ApiClientConfig


class _FakeResponse:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class ApiClientTest(unittest.TestCase):
    def test_listar_movimientos_usa_endpoint_correcto(self):
        client = ApiClient(ApiClientConfig(base_url="http://api.local", timeout=3))

        with patch("app.services.api_client.urlopen", return_value=_FakeResponse({"data": []})) as mocked:
            response = client.listar_movimientos()

        request = mocked.call_args.args[0]
        self.assertEqual(request.full_url, "http://api.local/api/movimientos")
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(response, {"data": []})

    def test_crear_movimiento_envia_json(self):
        client = ApiClient(ApiClientConfig(base_url="http://api.local"))
        payload = {"tipo": "ingreso", "monto": "100.00"}

        with patch("app.services.api_client.urlopen", return_value=_FakeResponse({"data": {"id": 1}})) as mocked:
            response = client.crear_movimiento(payload)

        request = mocked.call_args.args[0]
        self.assertEqual(request.full_url, "http://api.local/api/movimientos")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(json.loads(request.data.decode("utf-8")), payload)
        self.assertEqual(response, {"data": {"id": 1}})

    def test_obtener_caja_diaria_agrega_fecha(self):
        client = ApiClient(ApiClientConfig(base_url="http://api.local"))

        with patch("app.services.api_client.urlopen", return_value=_FakeResponse({"data": {}})) as mocked:
            client.obtener_caja_diaria("2026-06-16")

        request = mocked.call_args.args[0]
        self.assertEqual(request.full_url, "http://api.local/api/caja/diaria?fecha=2026-06-16")
        self.assertEqual(request.get_method(), "GET")


if __name__ == "__main__":
    unittest.main()
