const test = require("node:test");
const assert = require("node:assert/strict");
const {
  TipoMovimiento,
  EstadoMovimiento,
  OrigenMovimiento,
  impactoEnFlujo,
  normalizarMovimiento,
  validarMovimiento,
} = require("../src/models/movimiento.model");

test("normaliza movimiento de ingreso", () => {
  const movimiento = normalizarMovimiento({
    fecha: "2026-06-16",
    tipo: TipoMovimiento.INGRESO,
    estado: EstadoMovimiento.PENDIENTE,
    origen: OrigenMovimiento.MANUAL,
    monto: "15000.00",
    descripcion: "Ingreso manual",
  }, 1);

  assert.equal(movimiento.id, 1);
  assert.equal(movimiento.impactaEfectivo, true);
  assert.equal(movimiento.impactoEnFlujo, "15000.00");
});

test("egreso impacta negativo", () => {
  assert.equal(impactoEnFlujo({
    tipo: TipoMovimiento.EGRESO,
    estado: EstadoMovimiento.CONFIRMADO,
    monto: "2500.00",
    esCuentaCorriente: false,
  }), "-2500.00");
});

test("banco no impacta efectivo", () => {
  assert.equal(impactoEnFlujo({
    tipo: TipoMovimiento.BANCO,
    estado: EstadoMovimiento.CONFIRMADO,
    monto: "1000.00",
    esCuentaCorriente: false,
  }), "0.00");
});

test("valida campos obligatorios", () => {
  const errors = validarMovimiento({ tipo: "otro" });

  assert.ok(errors.includes("fecha es obligatorio"));
  assert.ok(errors.includes("tipo es obligatorio o invalido"));
  assert.ok(errors.includes("monto es obligatorio y debe ser numerico"));
  assert.ok(errors.includes("descripcion es obligatorio"));
});
