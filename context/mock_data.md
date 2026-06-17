# Mock Data

## Objetivo

Mantener datos de prueba fuera de pantallas, services y repositories reales.

Los mocks sirven para:

- Diseñar UI sin depender de ASA9.
- Validar tablas, metricas y estados visuales.
- Preparar contratos backend antes de conectar fuentes reales.

## Frontend

Ubicacion:

```text
frontend/app/ui/mocks/
```

Archivos:

- `movimientos_mock.py`: movimientos de caja usando el modelo `Movimiento`.
- `ventas_mock.py`: facturas y remitos de prueba para futuras pantallas.

Reglas:

- Las vistas pueden importar mocks solo para fallback/demo.
- No hardcodear datasets dentro de frames o ventanas.
- Cuando exista API estable, la UI debe priorizar `ApiClient`.

## Backend

Ubicacion:

```text
backend/src/mocks/
```

Archivos:

- `movimientos.mock.js`: movimientos con forma de contrato API.
- `ventas.mock.js`: facturas y remitos mock para Fase 7.

Reglas:

- Los mocks backend no reemplazan repositories reales.
- Pueden alimentar endpoints temporales hasta conectar ASA9.
- Todo mock debe tener tests de forma basica.

## Pendiente

Cuando se releven datos reales de ASA9, actualizar mocks para que representen mejor nombres de campos, estados y casos borde.
