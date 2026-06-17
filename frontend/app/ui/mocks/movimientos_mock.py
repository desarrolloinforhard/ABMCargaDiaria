"""Mock movements for Nico's frontend work.

Estos datos son solo para UI/demo. No pertenecen a la vista ni reemplazan la API.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.models import EstadoMovimiento, Movimiento, OrigenMovimiento, TipoMovimiento


MOVIMIENTOS_MOCK: tuple[Movimiento, ...] = (
    Movimiento(
        fecha=date.today(),
        tipo=TipoMovimiento.INGRESO,
        estado=EstadoMovimiento.CONFIRMADO,
        origen=OrigenMovimiento.MANUAL,
        monto=Decimal("150000.00"),
        descripcion="Cobro cliente Empresa SA",
        id=1,
    ),
    Movimiento(
        fecha=date.today(),
        tipo=TipoMovimiento.INGRESO,
        estado=EstadoMovimiento.PENDIENTE,
        origen=OrigenMovimiento.MANUAL,
        monto=Decimal("75000.00"),
        descripcion="Cobro pendiente confirmacion",
        id=2,
    ),
    Movimiento(
        fecha=date.today(),
        tipo=TipoMovimiento.EGRESO,
        estado=EstadoMovimiento.CONFIRMADO,
        origen=OrigenMovimiento.MANUAL,
        monto=Decimal("32000.00"),
        descripcion="Pago proveedor materiales",
        id=3,
    ),
    Movimiento(
        fecha=date.today(),
        tipo=TipoMovimiento.BANCO,
        estado=EstadoMovimiento.CONCILIADO,
        origen=OrigenMovimiento.CSV_BANCO,
        monto=Decimal("95000.00"),
        descripcion="Transferencia bancaria recibida",
        id=4,
    ),
    Movimiento(
        fecha=date.today(),
        tipo=TipoMovimiento.ADELANTO,
        estado=EstadoMovimiento.CONFIRMADO,
        origen=OrigenMovimiento.MANUAL,
        monto=Decimal("15000.00"),
        descripcion="Adelanto empleado Juan Perez",
        id=5,
        empleado_id=101,
    ),
    Movimiento(
        fecha=date.today(),
        tipo=TipoMovimiento.INGRESO,
        estado=EstadoMovimiento.ANULADO,
        origen=OrigenMovimiento.MANUAL,
        monto=Decimal("50000.00"),
        descripcion="Ingreso anulado por error",
        id=6,
    ),
)
