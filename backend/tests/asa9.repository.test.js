const test = require("node:test");
const assert = require("node:assert/strict");

test("diagnostico ASA9 queda no listo si esta deshabilitado", () => {
  const previous = process.env.ASA9_ENABLED;
  process.env.ASA9_ENABLED = "false";

  delete require.cache[require.resolve("../src/repositories/asa9.repository")];
  const repository = require("../src/repositories/asa9.repository");
  const status = repository.getAsa9Status();

  assert.equal(status.enabled, false);
  assert.equal(status.ready, false);
  assert.ok(status.issues.includes("ASA9_ENABLED=false: integracion deshabilitada."));

  if (previous === undefined) delete process.env.ASA9_ENABLED;
  else process.env.ASA9_ENABLED = previous;
});

test("query ASA9 falla explicitamente si no esta configurado", async () => {
  const previous = process.env.ASA9_ENABLED;
  process.env.ASA9_ENABLED = "false";

  delete require.cache[require.resolve("../src/repositories/asa9.repository")];
  const repository = require("../src/repositories/asa9.repository");

  await assert.rejects(
    () => repository.queryAsa9("select 1"),
    {
      code: "ASA9_NOT_READY",
    },
  );

  if (previous === undefined) delete process.env.ASA9_ENABLED;
  else process.env.ASA9_ENABLED = previous;
});
