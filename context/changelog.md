# Changelog

## v0.0.1 - 2026-06-12

- Creacion inicial del proyecto.
- Estructura base de carpetas.
- Context inicial de producto, arquitectura, reglas y fases.
- Preparacion para UI con TkInforHard.
- Ventana principal minima con vista Caja Diaria.

## v0.0.2 - 2026-06-16

- Separacion del repositorio en `frontend/` y `backend/`.
- Preparacion de API Node.js + Express.
- Ajuste de arquitectura para que ASA9 sea responsabilidad del backend.
- Conservacion del cliente desktop Python con TkInforHard dentro de `frontend/`.

## v0.0.3 - 2026-06-16

- Creado flujo de trabajo contrato primero.
- Creado contrato API de movimientos.
- Creado modelo backend de movimientos.
- Agregados endpoints mock `GET /api/movimientos` y `POST /api/movimientos`.
- Agregado cliente API base en frontend.
- Documentada Fase 2.

## v0.0.4 - 2026-06-16

- Agregado contrato API de caja diaria.
- Agregado endpoint `GET /api/caja/diaria`.
- Agregado service backend para resumen de caja desde movimientos mock.
- Agregado cliente frontend para consultar caja diaria.
- Documentada Fase 3.

## v0.0.5 - 2026-06-16

- Conectada la pantalla Caja Diaria con la API backend.
- Agregado formulario manual de movimientos en frontend.
- Agregado refresco de metricas y tabla desde `GET /api/caja/diaria` y `GET /api/movimientos`.
- Agregados tests del cliente API frontend.
- Documentada Fase 4.

## v0.0.6 - 2026-06-16

- Agregada persistencia JSON local de movimientos en backend.
- Agregado test de repository con recarga desde disco.
- Agregada carpeta `backend/data/` con datos reales ignorados por Git.
- Actualizado roadmap: ASA9 queda como fase posterior desde backend.

## v0.0.7 - 2026-06-16

- Refactorizada la shell frontend para usar `IHRenderHost` en cargas y cambios de vista.
- Reemplazada la sidebar fija por `IHDrawerMenu` desplegable.
- Documentada la regla de renderizado seguro en contexto tecnico y guias UI.

## v0.0.8 - 2026-06-16

- Preparada configuracion ASA9 en backend mediante variables de entorno.
- Agregado endpoint `GET /api/asa9/status`.
- Agregado repository placeholder ASA9 sin conexion real.
- Agregados tests de configuracion ASA9.
- Actualizada documentacion de base de datos y contrato API.

## v0.0.9 - 2026-06-17

- Agregado modulo centralizado de logging frontend.
- Integrado logging en arranque de app, cliente API y vista principal.
- Agregados hooks de excepciones no capturadas con traceback.
- Ignorados logs locales del frontend.
