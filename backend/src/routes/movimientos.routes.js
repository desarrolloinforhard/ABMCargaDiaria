const { Router } = require("express");
const movimientosService = require("../services/movimientos.service");

const router = Router();

router.get("/", (_req, res) => {
  res.json(movimientosService.listarMovimientos());
});

router.post("/", (req, res) => {
  try {
    res.status(201).json(movimientosService.crearMovimiento(req.body));
  } catch (error) {
    if (error.code === "VALIDATION_ERROR") {
      res.status(400).json({
        error: {
          code: error.code,
          message: "El movimiento no cumple el contrato.",
          details: error.details,
        },
      });
      return;
    }

    res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Error interno al procesar movimiento.",
        details: [],
      },
    });
  }
});

module.exports = router;
