const express = require("express");
const cors = require("cors");
require("dotenv").config();

const asa9Routes = require("./routes/asa9.routes");
const healthRoutes = require("./routes/health.routes");
const movimientosRoutes = require("./routes/movimientos.routes");
const cajaRoutes = require("./routes/caja.routes");

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.use("/health", healthRoutes);
app.use("/api/asa9", asa9Routes);
app.use("/api/movimientos", movimientosRoutes);
app.use("/api/caja", cajaRoutes);

app.listen(port, () => {
  console.log(`ABMCargaDiaria API escuchando en http://localhost:${port}`);
});
