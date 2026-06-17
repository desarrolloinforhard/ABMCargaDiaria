const fs = require("node:fs");
const path = require("node:path");
const { normalizarMovimiento } = require("../models/movimiento.model");

const dataDir = process.env.ABM_DATA_DIR || path.resolve(__dirname, "..", "..", "data");
const dataFile = path.join(dataDir, "movimientos.json");

let movimientos = [];
let nextId = 1;
let initialized = false;

function ensureInitialized() {
  if (initialized) return;

  fs.mkdirSync(dataDir, { recursive: true });
  movimientos = readMovimientosFromDisk();
  nextId = calcularSiguienteId(movimientos);
  initialized = true;
}

function readMovimientosFromDisk() {
  if (!fs.existsSync(dataFile)) {
    return [];
  }

  const content = fs.readFileSync(dataFile, "utf-8").trim();
  if (!content) {
    return [];
  }

  const parsed = JSON.parse(content);
  return Array.isArray(parsed) ? parsed : [];
}

function calcularSiguienteId(rows) {
  const maxId = rows.reduce((max, movimiento) => Math.max(max, Number(movimiento.id) || 0), 0);
  return maxId + 1;
}

function saveMovimientosToDisk() {
  fs.mkdirSync(dataDir, { recursive: true });
  fs.writeFileSync(dataFile, `${JSON.stringify(movimientos, null, 2)}\n`, "utf-8");
}

function listarMovimientos() {
  ensureInitialized();
  return movimientos;
}

function crearMovimiento(input) {
  ensureInitialized();
  const movimiento = normalizarMovimiento(input, nextId);
  nextId += 1;
  movimientos.push(movimiento);
  saveMovimientosToDisk();
  return movimiento;
}

function resetRepositoryForTests(rows = []) {
  movimientos = rows;
  nextId = calcularSiguienteId(rows);
  initialized = true;
  saveMovimientosToDisk();
}

module.exports = {
  listarMovimientos,
  crearMovimiento,
  resetRepositoryForTests,
};
