const { Router } = require("express");
const movimientosService = require("../services/movimientos.service");

const router = Router();

router.get("/", (req, res) => {
  const filtros = {
    fecha: req.query.fecha || null,
    fechaDesde: req.query.fechaDesde || null,
    fechaHasta: req.query.fechaHasta || null,
    tipo: req.query.tipo || null,
    estado: req.query.estado || null,
  };
  res.json(movimientosService.listarMovimientos(filtros));
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

router.get("/:id", (req, res) => {
  try {
    res.json(movimientosService.obtenerMovimiento(req.params.id));
  } catch (error) {
    if (error.code === "NOT_FOUND") {
      return res.status(404).json({ error: { code: error.code, message: error.message, details: [] } });
    }
    res.status(500).json({ error: { code: "INTERNAL_ERROR", message: "Error interno.", details: [] } });
  }
});

router.patch("/:id/estado", (req, res) => {
  try {
    res.json(movimientosService.actualizarEstado(req.params.id, req.body.estado));
  } catch (error) {
    if (error.code === "VALIDATION_ERROR") {
      return res.status(400).json({ error: { code: error.code, message: error.message, details: error.details } });
    }
    if (error.code === "NOT_FOUND") {
      return res.status(404).json({ error: { code: error.code, message: error.message, details: [] } });
    }
    res.status(500).json({ error: { code: "INTERNAL_ERROR", message: "Error interno.", details: [] } });
  }
});

module.exports = router;
