const test = require("node:test");
const assert = require("node:assert/strict");
const {
  publicAsa9Config,
  readAsa9Config,
  validateAsa9Config,
} = require("../src/config/asa9.config");

test("lee configuracion ASA9 desde env sin credenciales hardcodeadas", () => {
  const config = readAsa9Config({
    ASA9_ENABLED: "true",
    ASA9_DSN: "CajaDiariaDsn",
    ASA9_DATABASE: "caja",
    ASA9_USER: "usuario",
    ASA9_PASSWORD: "secreto",
    ASA9_DRIVER: "SQL Anywhere 9",
  });

  assert.equal(config.enabled, true);
  assert.equal(config.dsn, "CajaDiariaDsn");
  assert.equal(config.password, "secreto");
});

test("config publica enmascara password", () => {
  const publicConfig = publicAsa9Config({
    enabled: true,
    dsn: "dsn",
    host: "",
    port: "2638",
    database: "db",
    user: "user",
    password: "secreto",
    driver: "SQL Anywhere 9",
  });

  assert.equal(publicConfig.password, "***");
  assert.equal(publicConfig.dsnConfigured, true);
});

test("validacion no exige credenciales si ASA9 esta deshabilitado", () => {
  const issues = validateAsa9Config({ enabled: false });

  assert.deepEqual(issues, ["ASA9_ENABLED=false: integracion deshabilitada."]);
});

test("validacion detecta configuracion incompleta si ASA9 esta habilitado", () => {
  const issues = validateAsa9Config({
    enabled: true,
    dsn: "",
    host: "",
    database: "",
    user: "",
    password: "",
  });

  assert.ok(issues.includes("Configurar ASA9_DSN o ASA9_HOST."));
  assert.ok(issues.includes("Configurar ASA9_DATABASE."));
  assert.ok(issues.includes("Configurar ASA9_USER."));
  assert.ok(issues.includes("Configurar ASA9_PASSWORD."));
});
