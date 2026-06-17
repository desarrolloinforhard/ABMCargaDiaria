const movimientosRepository = require("../repositories/movimientos.repository");
const { TipoMovimiento, EstadoMovimiento } = require("../models/movimiento.model");
const { decimalToCents, centsToDecimal } = require("../utils/decimal");

function obtenerCajaDiaria(fecha = null) {
  const movimientos = movimientosRepository.listarMovimientos();
  const movimientosFiltrados = fecha
    ? movimientos.filter((movimiento) => movimiento.fecha === fecha)
    : movimientos;

  return calcularResumenCaja(movimientosFiltrados, fecha);
}

function calcularResumenCaja(movimientos, fecha = null) {
  const resumen = movimientos.reduce(
    (acc, movimiento) => {
      const montoCents = decimalToCents(movimiento.monto);
      const impactoCents = decimalToCents(movimiento.impactoEnFlujo);

      if (movimiento.tipo === TipoMovimiento.INGRESO) {
        acc.ingresosCents += montoCents;
      }

      if ([
        TipoMovimiento.EGRESO,
        TipoMovimiento.ADELANTO,
        TipoMovimiento.PLUS,
        TipoMovimiento.RENDICION,
      ].includes(movimiento.tipo)) {
        acc.egresosCents += montoCents;
      }

      if (movimiento.tipo === TipoMovimiento.BANCO) {
        acc.bancoCents += montoCents;
      }

      acc.efectivoCents += impactoCents;

      if (movimiento.estado === EstadoMovimiento.PENDIENTE) acc.pendientes += 1;
      if (movimiento.estado === EstadoMovimiento.CONFIRMADO) acc.confirmados += 1;
      if (movimiento.estado === EstadoMovimiento.CONCILIADO) acc.conciliados += 1;
      if (movimiento.estado === EstadoMovimiento.ANULADO) acc.anulados += 1;

      return acc;
    },
    {
      ingresosCents: 0,
      egresosCents: 0,
      efectivoCents: 0,
      bancoCents: 0,
      pendientes: 0,
      confirmados: 0,
      conciliados: 0,
      anulados: 0,
    },
  );

  return {
    data: {
      fecha,
      ingresos: centsToDecimal(resumen.ingresosCents),
      egresos: centsToDecimal(resumen.egresosCents),
      efectivo: centsToDecimal(resumen.efectivoCents),
      banco: centsToDecimal(resumen.bancoCents),
      movimientosTotal: movimientos.length,
      estados: {
        pendientes: resumen.pendientes,
        confirmados: resumen.confirmados,
        conciliados: resumen.conciliados,
        anulados: resumen.anulados,
      },
    },
    meta: {
      source: "mock",
      totalMovimientosProcesados: movimientos.length,
    },
  };
}

module.exports = {
  obtenerCajaDiaria,
  calcularResumenCaja,
};
