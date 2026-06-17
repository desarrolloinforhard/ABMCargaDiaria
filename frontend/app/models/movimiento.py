"""
Modelo base de movimiento para ABMCargaDiaria.

PARA MISAEL (backend):
- Este dataclass es la entidad central. Services y repositories deben
  operar sobre Movimiento o listas de Movimiento.
- Los Enums son la fuente de verdad para estados y tipos. No usar strings
  sueltos en ninguna capa.
- El campo `id` es None hasta que el movimiento se persiste. El repository
  es responsable de asignarlo.
- `origen` identifica de dónde viene el dato: carga manual, ASA9, CSV bancario.
  Esto va a ser clave cuando integres múltiples fuentes en fases posteriores.

PARA NICO (frontend):
- Usá TipoMovimiento para colorear filas: INGRESO=verde, EGRESO=rojo,
  BANCO=gris/azul según UI guidelines.
- Usá EstadoMovimiento para el filtro de estado en IHFilterBar.
- Los campos opcionales (empleado_id, rendicion_id, referencia_externa)
  pueden ser None. La UI debe manejar ese caso sin romper.
- El método `es_efectivo()` te dice si el movimiento impacta en caja
  efectivo o no. Usalo para las métricas del dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Optional


class TipoMovimiento(StrEnum):
    """Tipo de movimiento. Define el impacto en el flujo de caja."""

    INGRESO = "ingreso"       # Suma al flujo. Color UI: verde.
    EGRESO = "egreso"         # Resta al flujo. Color UI: rojo.
    BANCO = "banco"           # Movimiento bancario. Color UI: gris/azul.
    ADELANTO = "adelanto"     # Adelanto a empleado. Relacionado con empleado_id.
    PLUS = "plus"             # Plus en efectivo a empleado. Relacionado con empleado_id.
    RENDICION = "rendicion"   # Gasto dentro de una rendición. Relacionado con rendicion_id.


class EstadoMovimiento(StrEnum):
    """
    Estado del movimiento a lo largo de su ciclo de vida.

    Flujo esperado:
        PENDIENTE -> CONFIRMADO -> CONCILIADO
        Cualquier estado -> ANULADO
    """

    PENDIENTE = "pendiente"       # Cargado pero no validado. Color UI: amarillo/naranja.
    CONFIRMADO = "confirmado"     # Validado por el operador.
    CONCILIADO = "conciliado"     # Coincide con banco o ASA9.
    ANULADO = "anulado"           # Dado de baja. No impacta en flujo.


class OrigenMovimiento(StrEnum):
    """De dónde proviene el movimiento. Importante para trazabilidad."""

    MANUAL = "manual"         # Carga manual por operador.
    ASA9 = "asa9"             # Importado desde Sybase SQL Anywhere via ODBC.
    CSV_BANCO = "csv_banco"   # Importado desde extracto bancario CSV.


@dataclass
class Movimiento:
    """
    Entidad central de ABMCargaDiaria.

    Representa cualquier movimiento de dinero: ingreso, egreso, banco,
    adelanto, plus o gasto de rendición.
    """

    fecha: date
    tipo: TipoMovimiento
    estado: EstadoMovimiento
    origen: OrigenMovimiento
    monto: Decimal
    descripcion: str

    # Identificador. None hasta que se persiste.
    id: Optional[int] = field(default=None)

    # Cuenta corriente: no impacta como efectivo hasta que esté pagada.
    es_cuenta_corriente: bool = field(default=False)

    # Relaciones opcionales según tipo de movimiento.
    empleado_id: Optional[int] = field(default=None)     # Para ADELANTO y PLUS.
    rendicion_id: Optional[int] = field(default=None)    # Para RENDICION.

    # Referencia externa para trazabilidad con ASA9 o banco.
    referencia_externa: Optional[str] = field(default=None)

    def es_efectivo(self) -> bool:
        """
        Indica si el movimiento impacta en caja efectivo.

        Retorna False si:
        - Es cuenta corriente no pagada.
        - Es movimiento bancario.
        - Está anulado.

        NICO: usá este método para las métricas de efectivo en el dashboard.
        MISAEL: usá este método en el service de flujo para calcular el total.
        """
        if self.estado == EstadoMovimiento.ANULADO:
            return False
        if self.es_cuenta_corriente:
            return False
        if self.tipo == TipoMovimiento.BANCO:
            return False
        return True

    def impacto_en_flujo(self) -> Decimal:
        """
        Retorna el impacto numérico del movimiento en el flujo de caja.

        Positivo para ingresos, negativo para egresos.
        Cero si no impacta en efectivo.

        MISAEL: usá este método en el service para acumular el flujo del día.
        """
        if not self.es_efectivo():
            return Decimal("0")
        if self.tipo == TipoMovimiento.INGRESO:
            return self.monto
        if self.tipo in (
            TipoMovimiento.EGRESO,
            TipoMovimiento.ADELANTO,
            TipoMovimiento.PLUS,
            TipoMovimiento.RENDICION,
        ):
            return -self.monto
        return Decimal("0")

    def __str__(self) -> str:
        return (
            f"[{self.fecha}] {self.tipo.value.upper()} "
            f"${self.monto:,.2f} - {self.descripcion} "
            f"({self.estado.value})"
        )
