const movimientosRepository = require("../repositories/movimientos.repository");
const { validarMovimiento } = require("../models/movimiento.model");

function listarMovimientos(fecha = null) {
  const todos = movimientosRepository.listarMovimientos();
  const data = fecha ? todos.filter((m) => m.fecha === fecha) : todos;
  return {
    data,
    meta: {
      total: data.length,
      source: "mock",
      ...(fecha && { fechaFiltro: fecha }),
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

module.exports = {
  listarMovimientos,
  crearMovimiento,
};
