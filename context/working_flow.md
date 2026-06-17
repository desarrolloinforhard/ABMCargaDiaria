# Working Flow

## Regla principal

ABMCargaDiaria se trabaja contrato primero:

1. Se documenta el contrato en `context/api_contracts/`.
2. Backend implementa API y reglas contra ese contrato.
3. Frontend consume la API, sin conectarse directo a ASA9 ni CSV.
4. Se validan tests y se actualiza `context/`, `CHANGELOG.md` y ClickUp.

## Separacion de responsabilidades

- `backend/`: Misael. API Node.js + Express, services, repositories, ASA9, CSV, reglas de negocio compartidas, logs y errores.
- `frontend/`: Nico. Cliente desktop Python, TkInforHard, pantallas, formularios, grillas, filtros, dashboard y consumo de API.
- `context/`: memoria comun del proyecto. Decisiones, fases, contratos, reglas, arquitectura, roadmap y hallazgos.

## Flujo de una funcionalidad

1. Definir objetivo y alcance en `context/phases/`.
2. Crear o actualizar contrato API.
3. Implementar backend con datos mock si todavia no existe integracion real.
4. Implementar frontend consumiendo API.
5. Reemplazar mock por ASA9/CSV solo cuando el contrato este estable.
6. Agregar tests minimos.
7. Actualizar changelog y decision log si corresponde.

## Reglas de integracion

- Frontend no usa ODBC.
- Frontend no guarda credenciales de ASA9.
- Backend no importa componentes TkInforHard.
- Los contratos JSON son la fuente comun entre frontend y backend.
- No usar strings sueltos para tipos y estados cuando exista enum/modelo equivalente.

## Uso de mocks

- Los mocks deben vivir en carpetas `mocks/`, nunca hardcodeados dentro de una vista o service final.
- Frontend usa `frontend/app/ui/mocks/` para prototipar pantallas.
- Backend usa `backend/src/mocks/` para endpoints temporales y contratos.
- Si un mock empieza a representar una regla real, esa regla debe moverse a model/service y testearse ahi.
