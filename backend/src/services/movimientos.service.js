const movimientosRepository = require("../repositories/movimientos.repository");
const { validarMovimiento } = require("../models/movimiento.model");

function listarMovimientos() {
  return {
    data: movimientosRepository.listarMovimientos(),
    meta: {
      total: movimientosRepository.listarMovimientos().length,
      source: "mock",
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
