# API Architecture

## Objetivo

Crear una API Node.js + Express que sea el punto unico de acceso a datos y reglas para ABMCargaDiaria.

## Responsabilidades

- Recibir pedidos del frontend desktop.
- Validar parametros y reglas de negocio.
- Consultar ASA9, CSV bancario o persistencia auxiliar.
- Responder JSON normalizado.
- Ocultar credenciales y detalles ODBC al cliente desktop.

## Endpoints iniciales previstos

- `GET /health`: estado de la API.
- `GET /api/movimientos`: lista movimientos.
- `POST /api/movimientos`: crea movimiento manual.
- `GET /api/caja-diaria`: resumen de caja diaria.
- `GET /api/banco/movimientos`: movimientos bancarios.
- `POST /api/banco/importar-csv`: importacion CSV futura.

## Estado actual

Se crea esqueleto inicial sin conexion ASA9 y sin reglas completas. `GET /api/movimientos` devuelve una lista vacia hasta implementar repositories reales.
