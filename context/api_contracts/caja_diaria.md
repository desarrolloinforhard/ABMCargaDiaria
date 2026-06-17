# API Contract - Caja Diaria

## Objetivo

Definir el contrato para que el frontend obtenga un resumen de caja calculado por el backend.

## Endpoint

```text
GET /api/caja/diaria
GET /api/caja/diaria?fecha=2026-06-16
```

## Response 200

```json
{
  "data": {
    "fecha": "2026-06-16",
    "ingresos": "1000.00",
    "egresos": "250.50",
    "efectivo": "749.50",
    "banco": "500.00",
    "movimientosTotal": 4,
    "estados": {
      "pendientes": 1,
      "confirmados": 1,
      "conciliados": 1,
      "anulados": 1
    }
  },
  "meta": {
    "source": "mock",
    "totalMovimientosProcesados": 4
  }
}
```

## Reglas de calculo

- `ingresos`: suma de montos de movimientos tipo `ingreso`, incluso si no impactan efectivo. Sirve como lectura bruta operativa.
- `egresos`: suma de montos de `egreso`, `adelanto`, `plus` y `rendicion`.
- `efectivo`: suma de `impactoEnFlujo`; respeta anulados, cuenta corriente y banco.
- `banco`: suma de montos de movimientos tipo `banco`.
- `estados`: conteo por estado.

## Notas

En Fase 3 el backend calcula desde repository mock en memoria. En fases futuras este resumen se alimentara desde ASA9, CSV bancario y movimientos manuales persistidos.
