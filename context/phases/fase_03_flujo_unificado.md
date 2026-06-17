# Fase 3 - Flujo unificado frontend/backend

## Objetivo

Cerrar el primer circuito funcional entre backend y frontend usando contratos API, sin conectar ASA9 todavia.

## Alcance

- Contrato `caja_diaria`.
- Endpoint backend `GET /api/caja/diaria`.
- Calculo de resumen desde movimientos mock.
- Cliente frontend para consultar caja diaria.
- Tests backend de calculo.

## Tareas realizadas

- Creado `context/api_contracts/caja_diaria.md`.
- Creado `backend/src/services/caja.service.js`.
- Creado `backend/src/routes/caja.routes.js`.
- Registrada ruta `/api/caja` en `backend/src/server.js`.
- Agregado `ApiClient.obtener_caja_diaria()` en frontend.
- Agregado test backend de resumen.

## Pendientes

- Conectar la pantalla Caja Diaria a `ApiClient.obtener_caja_diaria()`.
- Manejar estados offline/API caida en UI.
- Persistir movimientos manuales.
- Reemplazar repository mock por fuente real cuando corresponda.

## Riesgos

- Diferencias de criterio entre resumen bruto (`ingresos`, `egresos`, `banco`) y efectivo neto (`efectivo`). Mantener el contrato actualizado.
- Los calculos de dinero deben evitar floats para persistencia real. En esta fase se usa centavos enteros internamente en backend.

## Proxima fase

Fase 4 - Carga manual de movimientos desde UI hacia API.
