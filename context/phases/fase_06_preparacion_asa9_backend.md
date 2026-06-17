# Fase 6 - Preparacion ASA9 ODBC 32-bit desde backend

## Objetivo

Preparar el backend para integrar ASA9 / Sybase SQL Anywhere sin conectar todavia ni exponer credenciales.

## Alcance

- Variables de entorno documentadas en `backend/.env.example`.
- Configuracion ASA9 centralizada.
- Repository ASA9 placeholder.
- Endpoint seguro de diagnostico `GET /api/asa9/status`.
- Tests de configuracion y bloqueo de queries cuando ASA9 no esta listo.

## Tareas realizadas

- Creado `backend/src/config/asa9.config.js`.
- Creado `backend/src/repositories/asa9.repository.js`.
- Creado `backend/src/services/asa9.service.js`.
- Creado `backend/src/routes/asa9.routes.js`.
- Registrada ruta `/api/asa9` en `backend/src/server.js`.
- Creado `backend/.env.example`.
- Creado contrato `context/api_contracts/asa9_status.md`.

## Pendientes

- Confirmar driver ODBC 32-bit instalado en el equipo/servidor backend.
- Decidir si se conectara por DSN o cadena host/database.
- Instalar dependencia Node ODBC solo cuando el entorno este confirmado.
- Relevar tablas ASA9 reales para ventas factura, remitos y cuenta corriente.
- Implementar queries validadas en repositories especificos.

## Riesgos

- ASA9 requiere ODBC 32-bit y puede no ser compatible con un proceso Node de 64-bit.
- Driver, DSN y permisos pueden variar por equipo.
- No se deben guardar credenciales reales en Git.

## Proxima fase

Fase 7 - Ventas factura y remito via API, o prueba tecnica de conexion ASA9 si el entorno ODBC esta listo.
