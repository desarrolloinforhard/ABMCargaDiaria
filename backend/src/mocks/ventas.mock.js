const ventasFacturasMock = [
  {
    id: 1001,
    fecha: "2026-06-17",
    cliente: "Empresa SA",
    comprobante: "FAC-A-0001-00001234",
    total: "185000.00",
    estado: "pendiente",
    origen: "asa9_mock",
  },
  {
    id: 1002,
    fecha: "2026-06-17",
    cliente: "Cliente Mostrador",
    comprobante: "FAC-B-0002-00004567",
    total: "42500.00",
    estado: "pagada",
    origen: "asa9_mock",
  },
];

const ventasRemitosMock = [
  {
    id: 2001,
    fecha: "2026-06-17",
    cliente: "Distribuidora Norte",
    comprobante: "REM-0001-00008888",
    total: "98000.00",
    estado: "pendiente_facturar",
    origen: "asa9_mock",
  },
  {
    id: 2002,
    fecha: "2026-06-17",
    cliente: "Taller Centro",
    comprobante: "REM-0001-00008889",
    total: "36750.00",
    estado: "entregado",
    origen: "asa9_mock",
  },
];

module.exports = {
  ventasFacturasMock,
  ventasRemitosMock,
};
