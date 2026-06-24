# API Contract - Ventas

## Objetivo

Exponer facturas y remitos provenientes de ASA9 para consulta desde el frontend desktop.

## Base URL local

```text
http://localhost:3000
```

## Factura JSON

```json
{
  "id": 1001,
  "fecha": "2026-06-24",
  "cliente": "Empresa SA",
  "comprobante": "FAC-A-0001-00001234",
  "total": "185000.00",
  "estado": "pendiente",
  "origen": "asa9"
}
```

### Estados de factura

```text
pendiente          — emitida, no cobrada aun
pagada             — cobrada
anulada            — dada de baja
```

## Remito JSON

```json
{
  "id": 2001,
  "fecha": "2026-06-24",
  "cliente": "Distribuidora Norte",
  "comprobante": "REM-0001-00008888",
  "total": "98000.00",
  "estado": "pendiente_facturar",
  "origen": "asa9"
}
```

### Estados de remito

```text
pendiente_facturar — entregado pero sin factura aun
entregado          — entregado y facturado
anulado            — dado de baja
```

## GET /api/ventas/facturas

Lista facturas con filtros opcionales.

### Query params opcionales

| Param       | Descripcion                   | Ejemplo                    |
|-------------|-------------------------------|----------------------------|
| fechaDesde  | Desde esta fecha inclusive    | ?fechaDesde=2026-06-01     |
| fechaHasta  | Hasta esta fecha inclusive    | ?fechaHasta=2026-06-30     |
| estado      | Filtra por estado de factura  | ?estado=pendiente          |

Los filtros son combinables entre si.

### Response 200

```json
{
  "data": [
    {
      "id": 1001,
      "fecha": "2026-06-24",
      "cliente": "Empresa SA",
      "comprobante": "FAC-A-0001-00001234",
      "total": "185000.00",
      "estado": "pendiente",
      "origen": "asa9"
    }
  ],
  "meta": {
    "total": 1,
    "source": "asa9"
  }
}
```

## GET /api/ventas/remitos

Lista remitos. Acepta los mismos filtros que facturas.

### Response 200

```json
{
  "data": [
    {
      "id": 2001,
      "fecha": "2026-06-24",
      "cliente": "Distribuidora Norte",
      "comprobante": "REM-0001-00008888",
      "total": "98000.00",
      "estado": "pendiente_facturar",
      "origen": "asa9"
    }
  ],
  "meta": {
    "total": 1,
    "source": "asa9"
  }
}
```

## Error format

```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Error al consultar ASA9.",
    "details": []
  }
}
```
