const test = require("node:test");
const assert = require("node:assert/strict");
const { calcularResumenCaja } = require("../src/services/caja.service");

test("calcula resumen de caja diaria desde movimientos", () => {
  const resumen = calcularResumenCaja([
    {
      fecha: "2026-06-16",
      tipo: "ingreso",
      estado: "confirmado",
      monto: "1000.00",
      impactoEnFlujo: "1000.00",
    },
    {
      fecha: "2026-06-16",
      tipo: "egreso",
      estado: "pendiente",
      monto: "250.50",
      impactoEnFlujo: "-250.50",
    },
    {
      fecha: "2026-06-16",
      tipo: "banco",
      estado: "conciliado",
      monto: "500.00",
      impactoEnFlujo: "0.00",
    },
    {
      fecha: "2026-06-16",
      tipo: "ingreso",
      estado: "anulado",
      monto: "75.00",
      impactoEnFlujo: "0.00",
    },
  ], "2026-06-16");

  assert.equal(resumen.data.ingresos, "1075.00");
  assert.equal(resumen.data.egresos, "250.50");
  assert.equal(resumen.data.efectivo, "749.50");
  assert.equal(resumen.data.banco, "500.00");
  assert.equal(resumen.data.movimientosTotal, 4);
  assert.deepEqual(resumen.data.estados, {
    pendientes: 1,
    confirmados: 1,
    conciliados: 1,
    anulados: 1,
  });
});
