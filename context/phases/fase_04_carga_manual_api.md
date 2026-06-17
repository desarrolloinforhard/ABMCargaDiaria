# Fase 4 - Carga manual de movimientos desde UI hacia API

## Objetivo

Conectar la pantalla Caja Diaria del frontend con la API backend para crear movimientos manuales y refrescar resumen/tabla.

## Alcance

- Formulario manual minimo en frontend.
- `POST /api/movimientos` desde la UI.
- Refresco de `GET /api/movimientos` y `GET /api/caja/diaria` luego de guardar.
- Mensaje de estado cuando la API no esta disponible.
- Tests del cliente API frontend.

## Tareas realizadas

- Actualizada `frontend/app/ui/main_window.py` con formulario de carga manual.
- Agregado uso de `ApiClient.crear_movimiento()` desde la UI.
- Agregado refresco de grilla y metricas desde API.
- Agregado estado visible de conexion/API.
- Agregados tests de `frontend/app/services/api_client.py`.

## Pendientes

- Reemplazar formulario minimo por componentes/validaciones de dominio mas completas.
- Agregar checkbox de cuenta corriente y relaciones empleado/rendicion.
- Manejar errores de validacion por campo en UI.
- Persistir movimientos manuales fuera de memoria.
- Integrar filtros reales de fecha/estado/tipo contra API.

## Riesgos

- El repository backend es mock en memoria: los movimientos se pierden al reiniciar la API.
- La UI depende de que `backend` este levantado en `http://localhost:3000`.

## Proxima fase

Fase 5 - Persistencia backend inicial o preparacion ASA9 ODBC 32-bit, segun prioridad del proyecto.
