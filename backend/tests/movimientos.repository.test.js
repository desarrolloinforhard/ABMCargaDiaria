const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

test("persiste movimientos manuales en archivo JSON", () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "abm-movimientos-"));
  process.env.ABM_DATA_DIR = tempDir;

  const repositoryPath = require.resolve("../src/repositories/movimientos.repository");
  delete require.cache[repositoryPath];
  const repository = require("../src/repositories/movimientos.repository");

  const movimiento = repository.crearMovimiento({
    fecha: "2026-06-16",
    tipo: "ingreso",
    estado: "pendiente",
    origen: "manual",
    monto: "100.00",
    descripcion: "Ingreso persistido",
  });

  assert.equal(movimiento.id, 1);
  assert.equal(repository.listarMovimientos().length, 1);

  delete require.cache[repositoryPath];
  const repositoryReloaded = require("../src/repositories/movimientos.repository");
  const movimientos = repositoryReloaded.listarMovimientos();

  assert.equal(movimientos.length, 1);
  assert.equal(movimientos[0].descripcion, "Ingreso persistido");
  assert.equal(movimientos[0].impactoEnFlujo, "100.00");
});
