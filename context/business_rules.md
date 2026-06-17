# Business Rules

## Movimientos

- Ingreso suma al flujo.
- Egreso resta al flujo.
- Ventas por cuenta corriente no impactan como efectivo hasta que esten pagadas.
- Ventas por factura y ventas por remito deben poder verse separadas y unificadas.
- Movimientos bancarios deben diferenciarse del efectivo.
- Los movimientos deben tener estado: pendiente, confirmado, conciliado o anulado.
- Un movimiento anulado no impacta en flujo.
- Los montos deben viajar por API como string decimal.

## Rendiciones

- Rendiciones pueden quedar abiertas o cerradas.
- Una rendicion abierta debe figurar como pendiente.
- Para cerrar una rendicion, los gastos justificados mas la devolucion deben coincidir con el dinero entregado.

## Empleados

- Plus en efectivo y adelantos deben relacionarse con empleados.

## Integraciones

- ASA9 y CSV bancario son responsabilidad del backend.
- Frontend consume resultados normalizados desde API.
