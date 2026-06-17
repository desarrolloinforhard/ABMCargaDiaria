function readAsa9Config(env = process.env) {
  return {
    enabled: env.ASA9_ENABLED === "true",
    dsn: env.ASA9_DSN || "",
    host: env.ASA9_HOST || "",
    port: env.ASA9_PORT || "2638",
    database: env.ASA9_DATABASE || "",
    user: env.ASA9_USER || "",
    password: env.ASA9_PASSWORD || "",
    driver: env.ASA9_DRIVER || "SQL Anywhere 9",
  };
}

function maskSecret(value) {
  if (!value) return "";
  return "***";
}

function publicAsa9Config(config = readAsa9Config()) {
  return {
    enabled: config.enabled,
    dsnConfigured: Boolean(config.dsn),
    hostConfigured: Boolean(config.host),
    port: config.port,
    databaseConfigured: Boolean(config.database),
    userConfigured: Boolean(config.user),
    password: maskSecret(config.password),
    driver: config.driver,
  };
}

function validateAsa9Config(config = readAsa9Config()) {
  const issues = [];

  if (!config.enabled) {
    issues.push("ASA9_ENABLED=false: integracion deshabilitada.");
    return issues;
  }

  if (!config.dsn && !config.host) {
    issues.push("Configurar ASA9_DSN o ASA9_HOST.");
  }
  if (!config.database) {
    issues.push("Configurar ASA9_DATABASE.");
  }
  if (!config.user) {
    issues.push("Configurar ASA9_USER.");
  }
  if (!config.password) {
    issues.push("Configurar ASA9_PASSWORD.");
  }

  return issues;
}

module.exports = {
  readAsa9Config,
  publicAsa9Config,
  validateAsa9Config,
};
