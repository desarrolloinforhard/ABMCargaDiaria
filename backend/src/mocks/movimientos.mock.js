const movimientosMock = [
  {
    fecha: "2026-06-17",
    tipo: "ingreso",
    estado: "confirmado",
    origen: "manual",
    monto: "150000.00",
    descripcion: "Cobro cliente Empresa SA",
    esCuentaCorriente: false,
    empleadoId: null,
    rendicionId: null,
    referenciaExterna: "mock-mov-1",
  },
  {
    fecha: "2026-06-17",
    tipo: "egreso",
    estado: "pendiente",
    origen: "manual",
    monto: "32000.00",
    descripcion: "Pago proveedor materiales",
    esCuentaCorriente: false,
    empleadoId: null,
    rendicionId: null,
    referenciaExterna: "mock-mov-2",
  },
  {
    fecha: "2026-06-17",
    tipo: "banco",
    estado: "conciliado",
    origen: "csv_banco",
    monto: "95000.00",
    descripcion: "Transferencia bancaria recibida",
    esCuentaCorriente: false,
    empleadoId: null,
    rendicionId: null,
    referenciaExterna: "mock-bank-1",
  },
];

module.exports = {
  movimientosMock,
};
