# API Contract - Movimientos

## Objetivo

Definir el contrato comun entre frontend desktop y backend API para movimientos de caja.

## Base URL local

```text
http://localhost:3000
```

## Enums

### TipoMovimiento

```text
ingreso
egreso
banco
adelanto
plus
rendicion
```

### EstadoMovimiento

```text
pendiente
confirmado
conciliado
anulado
```

### OrigenMovimiento

```text
manual
asa9
csv_banco
```

## Movimiento JSON

```json
{
  "id": 1,
  "fecha": "2026-06-16",
  "tipo": "ingreso",
  "estado": "pendiente",
  "origen": "manual",
  "monto": "15000.00",
  "descripcion": "Ingreso manual de caja",
  "esCuentaCorriente": false,
  "empleadoId": null,
  "rendicionId": null,
  "referenciaExterna": null,
  "impactaEfectivo": true,
  "impactoEnFlujo": "15000.00"
}
```

## GET /api/movimientos

Lista movimientos normalizados.

### Response 200

```json
{
  "data": [],
  "meta": {
    "total": 0,
    "source": "mock"
  }
}
```

## POST /api/movimientos

Crea un movimiento manual. En esta fase usa repository en memoria/mock.

### Request body

```json
{
  "fecha": "2026-06-16",
  "tipo": "egreso",
  "estado": "pendiente",
  "origen": "manual",
  "monto": "2500.00",
  "descripcion": "Compra de insumos",
  "esCuentaCorriente": false,
  "empleadoId": null,
  "rendicionId": null,
  "referenciaExterna": null
}
```

### Response 201

```json
{
  "data": {
    "id": 1,
    "fecha": "2026-06-16",
    "tipo": "egreso",
    "estado": "pendiente",
    "origen": "manual",
    "monto": "2500.00",
    "descripcion": "Compra de insumos",
    "esCuentaCorriente": false,
    "empleadoId": null,
    "rendicionId": null,
    "referenciaExterna": null,
    "impactaEfectivo": true,
    "impactoEnFlujo": "-2500.00"
  }
}
```

## Error format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "El campo tipo es obligatorio o invalido.",
    "details": []
  }
}
```

## Reglas de impacto

- `anulado` no impacta flujo.
- `esCuentaCorriente=true` no impacta efectivo.
- `tipo=banco` no impacta efectivo.
- `ingreso` impacta positivo.
- `egreso`, `adelanto`, `plus` y `rendicion` impactan negativo.
