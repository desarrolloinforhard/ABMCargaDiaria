const TipoMovimiento = Object.freeze({
  INGRESO: "ingreso",
  EGRESO: "egreso",
  BANCO: "banco",
  ADELANTO: "adelanto",
  PLUS: "plus",
  RENDICION: "rendicion",
});

const EstadoMovimiento = Object.freeze({
  PENDIENTE: "pendiente",
  CONFIRMADO: "confirmado",
  CONCILIADO: "conciliado",
  ANULADO: "anulado",
});

const OrigenMovimiento = Object.freeze({
  MANUAL: "manual",
  ASA9: "asa9",
  CSV_BANCO: "csv_banco",
});

function esValorPermitido(enumObject, value) {
  return Object.values(enumObject).includes(value);
}

function esEfectivo(movimiento) {
  if (movimiento.estado === EstadoMovimiento.ANULADO) return false;
  if (movimiento.esCuentaCorriente === true) return false;
  if (movimiento.tipo === TipoMovimiento.BANCO) return false;
  return true;
}

function impactoEnFlujo(movimiento) {
  if (!esEfectivo(movimiento)) return "0.00";

  const monto = Number.parseFloat(movimiento.monto);
  if (Number.isNaN(monto)) return "0.00";

  if (movimiento.tipo === TipoMovimiento.INGRESO) {
    return monto.toFixed(2);
  }

  if ([
    TipoMovimiento.EGRESO,
    TipoMovimiento.ADELANTO,
    TipoMovimiento.PLUS,
    TipoMovimiento.RENDICION,
  ].includes(movimiento.tipo)) {
    return (-monto).toFixed(2);
  }

  return "0.00";
}

function normalizarMovimiento(input, id = null) {
  const movimiento = {
    id,
    fecha: input.fecha,
    tipo: input.tipo,
    estado: input.estado || EstadoMovimiento.PENDIENTE,
    origen: input.origen || OrigenMovimiento.MANUAL,
    monto: String(input.monto),
    descripcion: input.descripcion,
    esCuentaCorriente: input.esCuentaCorriente === true,
    empleadoId: input.empleadoId ?? null,
    rendicionId: input.rendicionId ?? null,
    referenciaExterna: input.referenciaExterna ?? null,
  };

  movimiento.impactaEfectivo = esEfectivo(movimiento);
  movimiento.impactoEnFlujo = impactoEnFlujo(movimiento);
  return movimiento;
}

function validarMovimiento(input) {
  const errors = [];

  if (!input.fecha) errors.push("fecha es obligatorio");
  if (!esValorPermitido(TipoMovimiento, input.tipo)) errors.push("tipo es obligatorio o invalido");
  if (input.estado && !esValorPermitido(EstadoMovimiento, input.estado)) errors.push("estado invalido");
  if (input.origen && !esValorPermitido(OrigenMovimiento, input.origen)) errors.push("origen invalido");
  if (input.monto === undefined || input.monto === null || Number.isNaN(Number.parseFloat(input.monto))) {
    errors.push("monto es obligatorio y debe ser numerico");
  }
  if (!input.descripcion) errors.push("descripcion es obligatorio");

  return errors;
}

module.exports = {
  TipoMovimiento,
  EstadoMovimiento,
  OrigenMovimiento,
  esEfectivo,
  impactoEnFlujo,
  normalizarMovimiento,
  validarMovimiento,
};
