# Fase 2 - Modelo de movimientos y contrato API

## Objetivo

Definir el contrato de movimientos y preparar backend/frontend para trabajar separados.

## Alcance

- Contrato API para movimientos.
- Modelo backend inicial.
- Repository backend en memoria/mock.
- Endpoints iniciales `GET /api/movimientos` y `POST /api/movimientos`.
- Cliente HTTP frontend base para consumir API.
- Tests minimos de modelo/contrato.

## Tareas realizadas

- Creado `context/api_contracts/movimientos.md`.
- Creado `context/working_flow.md`.
- Creado modelo backend `backend/src/models/movimiento.model.js`.
- Actualizado backend para listar y crear movimientos mock.
- Creado cliente frontend `frontend/app/services/api_client.py`.

## Pendientes

- Conectar frontend real a la API en la pantalla Caja Diaria.
- Agregar validaciones mas completas de request en controllers.
- Definir contrato de caja diaria/resumen.
- Reemplazar repository mock por persistencia real cuando corresponda.

## Riesgos

- Diferencias entre enums frontend/backend si no se respeta el contrato.
- ASA9 puede requerir configuracion ODBC 32-bit especifica del servidor backend.

## Proxima fase

Fase 3 - Flujo unificado frontend/backend.
