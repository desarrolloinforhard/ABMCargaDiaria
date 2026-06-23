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

Lista movimientos normalizados. Acepta filtros opcionales por query params.

### Query params opcionales

| Param       | Descripcion                          | Ejemplo              |
|-------------|--------------------------------------|----------------------|
| fecha       | Fecha exacta (YYYY-MM-DD)            | ?fecha=2026-06-17    |
| fechaDesde  | Desde esta fecha inclusive           | ?fechaDesde=2026-06-01 |
| fechaHasta  | Hasta esta fecha inclusive           | ?fechaHasta=2026-06-30 |
| tipo        | Filtra por tipo de movimiento        | ?tipo=egreso         |
| estado      | Filtra por estado                    | ?estado=pendiente    |

Los filtros son combinables entre si.

### Response 200

```json
{
  "data": [],
  "meta": {
    "total": 0,
    "source": "json",
    "fechaDesde": "2026-06-01",
    "fechaHasta": "2026-06-30",
    "tipoFiltro": "egreso",
    "estadoFiltro": "pendiente"
  }
}
```

## GET /api/movimientos/:id

Devuelve un movimiento por id.

### Response 200

```json
{
  "data": { ...movimiento }
}
```

### Response 404

```json
{
  "error": { "code": "NOT_FOUND", "message": "Movimiento no encontrado", "details": [] }
}
```

## POST /api/movimientos

Crea un movimiento manual.

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

## PATCH /api/movimientos/:id/estado

Cambia el estado de un movimiento y recalcula `impactaEfectivo` e `impactoEnFlujo`.

### Request body

```json
{ "estado": "confirmado" }
```

### Response 200

```json
{
  "data": { ...movimiento actualizado }
}
```

### Response 400 - Estado invalido

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Estado invalido",
    "details": ["estado debe ser uno de: pendiente, confirmado, conciliado, anulado"]
  }
}
```

## DELETE /api/movimientos/:id

Elimina un movimiento y persiste el cambio en JSON.

### Response 204

Sin cuerpo.

### Response 404

```json
{
  "error": { "code": "NOT_FOUND", "message": "Movimiento no encontrado", "details": [] }
}
```

## Reglas de impacto

- `anulado` no impacta flujo.
- `esCuentaCorriente=true` no impacta efectivo.
- `tipo=banco` no impacta efectivo.
- `ingreso` impacta positivo.
- `egreso`, `adelanto`, `plus` y `rendicion` impactan negativo.
