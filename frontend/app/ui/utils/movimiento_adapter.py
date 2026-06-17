"""Presentation helpers: convert Movimiento domain objects to IHTable rows and metrics."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.models.movimiento import EstadoMovimiento, Movimiento, OrigenMovimiento, TipoMovimiento


def movimiento_desde_api(data: dict) -> Movimiento:
    """Convierte un dict JSON de la API en un objeto Movimiento."""
    return Movimiento(
        id=data.get("id"),
        fecha=date.fromisoformat(data["fecha"]),
        tipo=TipoMovimiento(data["tipo"]),
        estado=EstadoMovimiento(data["estado"]),
        origen=OrigenMovimiento(data["origen"]),
        monto=Decimal(str(data["monto"])),
        descripcion=data.get("descripcion", ""),
        es_cuenta_corriente=bool(data.get("esCuentaCorriente", False)),
        empleado_id=data.get("empleadoId"),
        rendicion_id=data.get("rendicionId"),
        referencia_externa=data.get("referenciaExterna"),
    )

_TIPOS_EGRESO = frozenset({
    TipoMovimiento.EGRESO,
    TipoMovimiento.ADELANTO,
    TipoMovimiento.PLUS,
    TipoMovimiento.RENDICION,
})


def movimientos_a_filas(movimientos: list[Movimiento]) -> list[dict]:
    """Return IHTable-compatible row dicts (including the 'semaforo' tag key)."""
    return [
        {
            "Fecha": str(m.fecha),
            "Tipo": m.tipo.value.capitalize(),
            "Origen": m.origen.value.upper(),
            "Estado": m.estado.value.capitalize(),
            "Monto": _fmt_money(m.monto),
            "Descripcion": m.descripcion,
            "semaforo": _fila_tag(m),
        }
        for m in movimientos
    ]


def calcular_metricas(movimientos: list[Movimiento]) -> dict:
    """Aggregate the four dashboard metrics from a list of Movimiento."""
    ingresos = Decimal("0")
    egresos = Decimal("0")
    banco = Decimal("0")

    for m in movimientos:
        if m.estado == EstadoMovimiento.ANULADO:
            continue
        if m.tipo == TipoMovimiento.INGRESO:
            ingresos += m.monto
        elif m.tipo in _TIPOS_EGRESO:
            egresos += m.monto
        elif m.tipo == TipoMovimiento.BANCO:
            banco += m.monto

    efectivo = sum((m.impacto_en_flujo() for m in movimientos), Decimal("0"))
    pendientes = sum(1 for m in movimientos if m.estado == EstadoMovimiento.PENDIENTE)

    return {
        "ingresos": ingresos,
        "egresos": egresos,
        "efectivo": efectivo,
        "banco": banco,
        "total_movimientos": len(movimientos),
        "pendientes": pendientes,
    }


def _fila_tag(m: Movimiento) -> str:
    if m.estado == EstadoMovimiento.ANULADO:
        return ""
    if m.estado == EstadoMovimiento.PENDIENTE:
        return "yellow"
    if m.tipo == TipoMovimiento.INGRESO:
        return "green"
    if m.tipo in _TIPOS_EGRESO:
        return "red"
    return ""


def _fmt_money(value: Decimal | None) -> str:
    try:
        return f"$ {float(value or 0):,.2f}"
    except (TypeError, ValueError):
        return "$ 0.00"
