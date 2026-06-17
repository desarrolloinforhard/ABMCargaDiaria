const { Router } = require("express");
const asa9Service = require("../services/asa9.service");

const router = Router();

router.get("/status", (_req, res) => {
  res.json(asa9Service.obtenerDiagnosticoAsa9());
});

module.exports = router;
