# Database Analysis

## Estado ASA9

ASA9 / Sybase SQL Anywhere se integrara desde `backend/`, nunca desde el frontend desktop.

En Fase 6 se preparo configuracion y diagnostico, pero no se intenta conectar todavia.

## Configuracion prevista

Variables en `backend/.env`:

```text
ASA9_ENABLED=false
ASA9_DSN=
ASA9_HOST=
ASA9_PORT=2638
ASA9_DATABASE=
ASA9_USER=
ASA9_PASSWORD=
ASA9_DRIVER=SQL Anywhere 9
```

## Diagnostico

Endpoint:

```text
GET /api/asa9/status
```

Este endpoint muestra si la configuracion esta completa, sin revelar password y sin abrir conexion.

## Pendientes tecnicos

- Confirmar si Node corre 32-bit o si se requiere proceso/bridge 32-bit para ODBC ASA9.
- Confirmar driver SQL Anywhere 9 instalado.
- Definir DSN ODBC 32-bit o cadena de conexion.
- Probar conexion en entorno controlado.
- Documentar errores frecuentes de driver/DSN/permisos.

## Pendientes funcionales

- Relevar tablas de ventas por factura.
- Relevar tablas de remitos.
- Relevar cuenta corriente.
- Documentar queries validadas en `context/discoveries/asa9_queries.md`.
