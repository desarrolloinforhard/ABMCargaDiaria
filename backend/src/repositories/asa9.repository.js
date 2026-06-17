const { readAsa9Config, validateAsa9Config } = require("../config/asa9.config");

function getAsa9Status() {
  const config = readAsa9Config();
  const issues = validateAsa9Config(config);

  return {
    enabled: config.enabled,
    ready: config.enabled && issues.length === 0,
    driver: config.driver,
    mode: config.dsn ? "dsn" : "host",
    issues,
  };
}

async function queryAsa9(_sql, _params = []) {
  const status = getAsa9Status();
  if (!status.ready) {
    const error = new Error("ASA9 no esta configurado para ejecutar consultas.");
    error.code = "ASA9_NOT_READY";
    error.details = status.issues;
    throw error;
  }

  const error = new Error("ODBC ASA9 todavia no implementado. Instalar driver y definir estrategia de conexion.");
  error.code = "ASA9_NOT_IMPLEMENTED";
  error.details = [];
  throw error;
}

module.exports = {
  getAsa9Status,
  queryAsa9,
};
