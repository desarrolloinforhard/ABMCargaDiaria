const asa9Repository = require("../repositories/asa9.repository");
const { publicAsa9Config, readAsa9Config } = require("../config/asa9.config");

function obtenerDiagnosticoAsa9() {
  const config = readAsa9Config();
  const status = asa9Repository.getAsa9Status();

  return {
    data: {
      status,
      config: publicAsa9Config(config),
    },
    meta: {
      source: "env",
      connectionAttempted: false,
    },
  };
}

module.exports = {
  obtenerDiagnosticoAsa9,
};
