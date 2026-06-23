const movimientosRepository = require("../repositories/movimientos.repository");
const { validarMovimiento, EstadoMovimiento } = require("../models/movimiento.model");

function listarMovimientos({ fecha = null, fechaDesde = null, fechaHasta = null, tipo = null, estado = null } = {}) {
  let data = movimientosRepository.listarMovimientos();
  if (fecha) data = data.filter((m) => m.fecha === fecha);
  if (fechaDesde) data = data.filter((m) => m.fecha >= fechaDesde);
  if (fechaHasta) data = data.filter((m) => m.fecha <= fechaHasta);
  if (tipo) data = data.filter((m) => m.tipo === tipo);
  if (estado) data = data.filter((m) => m.estado === estado);
  return {
    data,
    meta: {
      total: data.length,
      source: "json",
      ...(fecha && { fechaFiltro: fecha }),
      ...(fechaDesde && { fechaDesde }),
      ...(fechaHasta && { fechaHasta }),
      ...(tipo && { tipoFiltro: tipo }),
      ...(estado && { estadoFiltro: estado }),
    },
  };
}

function crearMovimiento(input) {
  const errors = validarMovimiento(input);
  if (errors.length > 0) {
    const error = new Error("Movimiento invalido");
    error.code = "VALIDATION_ERROR";
    error.details = errors;
    throw error;
  }

  return {
    data: movimientosRepository.crearMovimiento(input),
  };
}

function obtenerMovimiento(id) {
  const movimiento = movimientosRepository.obtenerPorId(id);
  if (!movimiento) {
    const error = new Error("Movimiento no encontrado");
    error.code = "NOT_FOUND";
    throw error;
  }
  return { data: movimiento };
}

function actualizarEstado(id, estado) {
  if (!Object.values(EstadoMovimiento).includes(estado)) {
    const error = new Error("Estado invalido");
    error.code = "VALIDATION_ERROR";
    error.details = [`estado debe ser uno de: ${Object.values(EstadoMovimiento).join(", ")}`];
    throw error;
  }

  const movimiento = movimientosRepository.actualizarEstado(id, estado);
  if (!movimiento) {
    const error = new Error("Movimiento no encontrado");
    error.code = "NOT_FOUND";
    throw error;
  }

  return { data: movimiento };
}

module.exports = {
  listarMovimientos,
  obtenerMovimiento,
  crearMovimiento,
  actualizarEstado,
};
