const test = require("node:test");
const assert = require("node:assert/strict");
const { movimientosMock } = require("../src/mocks/movimientos.mock");
const { ventasFacturasMock, ventasRemitosMock } = require("../src/mocks/ventas.mock");

test("mocks de movimientos tienen forma de contrato", () => {
  assert.ok(movimientosMock.length > 0);
  assert.equal(typeof movimientosMock[0].fecha, "string");
  assert.equal(typeof movimientosMock[0].tipo, "string");
  assert.equal(typeof movimientosMock[0].monto, "string");
});

test("mocks de ventas incluyen facturas y remitos", () => {
  assert.ok(ventasFacturasMock.length > 0);
  assert.ok(ventasRemitosMock.length > 0);
  assert.match(ventasFacturasMock[0].comprobante, /^FAC-/);
  assert.match(ventasRemitosMock[0].comprobante, /^REM-/);
});
