import unittest

from app.models import Movimiento
from app.ui.mocks import MOVIMIENTOS_MOCK, VENTAS_FACTURAS_MOCK, VENTAS_REMITOS_MOCK


class UiMocksTest(unittest.TestCase):
    def test_movimientos_mock_usa_modelo_de_dominio(self):
        self.assertGreaterEqual(len(MOVIMIENTOS_MOCK), 1)
        self.assertTrue(all(isinstance(movimiento, Movimiento) for movimiento in MOVIMIENTOS_MOCK))

    def test_ventas_mock_tiene_facturas_y_remitos(self):
        self.assertGreaterEqual(len(VENTAS_FACTURAS_MOCK), 1)
        self.assertGreaterEqual(len(VENTAS_REMITOS_MOCK), 1)
        self.assertIn("comprobante", VENTAS_FACTURAS_MOCK[0])
        self.assertIn("comprobante", VENTAS_REMITOS_MOCK[0])


if __name__ == "__main__":
    unittest.main()
