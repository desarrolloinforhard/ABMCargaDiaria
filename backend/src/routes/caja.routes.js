const { Router } = require("express");
const cajaService = require("../services/caja.service");

const router = Router();

router.get("/diaria", (req, res) => {
  res.json(cajaService.obtenerCajaDiaria(req.query.fecha || null));
});

module.exports = router;
