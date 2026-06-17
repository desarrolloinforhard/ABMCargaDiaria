# API Contract - ASA9 Status

## Objetivo

Exponer un diagnostico seguro de configuracion ASA9 desde backend sin intentar conectar ni revelar credenciales.

## Endpoint

```text
GET /api/asa9/status
```

## Response 200

```json
{
  "data": {
    "status": {
      "enabled": false,
      "ready": false,
      "driver": "SQL Anywhere 9",
      "mode": "host",
      "issues": ["ASA9_ENABLED=false: integracion deshabilitada."]
    },
    "config": {
      "enabled": false,
      "dsnConfigured": false,
      "hostConfigured": false,
      "port": "2638",
      "databaseConfigured": false,
      "userConfigured": false,
      "password": "",
      "driver": "SQL Anywhere 9"
    }
  },
  "meta": {
    "source": "env",
    "connectionAttempted": false
  }
}
```

## Variables de entorno

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

## Reglas

- El endpoint no intenta conectar a ASA9.
- El endpoint no devuelve password real.
- `ready=true` solo indica configuracion minima completa, no conexion comprobada.
- La conexion real se implementara cuando se valide driver ODBC 32-bit y estrategia de despliegue.
