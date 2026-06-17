# Decision Log

## 2026-06-12 - Arquitectura inicial sin ASA9

Decision: Se inicia ABMCargaDiaria con una arquitectura por capas y sin conexion ASA9 en la primera fase.

Motivo: Primero se valida estructura, documentacion y base visual con TkInforHard.

## 2026-06-12 - Adaptacion temporal si TkInforHard no importa

Decision: La ventana principal intenta usar TkInforHard instalado, `TKINFORHARD_PATH` o un checkout hermano `../TkInforHard`. Si no puede importarse, usa una pantalla Tkinter minima.

Motivo: Permite arrancar el proyecto sin bloquear la Fase 1, pero deja claro que la UI final debe volver a TkInforHard.

## 2026-06-16 - Separacion frontend/backend

Decision: El proyecto se separa en `frontend/` y `backend/`. El frontend desktop Python no conectara directo a ASA9. La conexion ASA9, CSV bancario y reglas compartidas se implementaran en una API Node.js + Express.

Motivo: Centralizar credenciales, ODBC, reglas, logs y errores en backend; mantener el cliente desktop liviano; facilitar futuros clientes o integraciones.

## 2026-06-16 - Contrato primero

Decision: Las funcionalidades compartidas se definen primero en `context/api_contracts/`. Backend y frontend implementan contra ese contrato.

Motivo: Evitar divergencias entre UI y API, facilitar trabajo paralelo de Misa y Nico, y estabilizar las reglas antes de conectar ASA9.

## 2026-06-16 - Persistencia JSON local temporal

Decision: Los movimientos manuales se persisten inicialmente en `backend/data/movimientos.json`.

Motivo: Permite validar el flujo UI -> API -> resumen sin perder datos al reiniciar el backend, antes de conectar ASA9 o definir una base transaccional.

Alcance: Es una persistencia temporal/de desarrollo. No reemplaza ASA9 ni una estrategia definitiva de datos.

## 2026-06-16 - RenderHost obligatorio y drawer menu

Decision: Toda carga/cambio de vista del frontend debe pasar por `IHRenderHost`. La navegacion principal se maneja con `IHDrawerMenu` desplegable de TkInforHard.

Motivo: Evitar que Tkinter muestre pantallas parcialmente armadas, reducir cortes visuales y permitir abrir/cerrar el menu sin reconstruir modulos en forma directa.

## 2026-06-16 - ASA9 preparado sin conexion real

Decision: Se agrega configuracion, diagnostico y repository placeholder para ASA9 en backend, pero no se instala dependencia ODBC ni se conecta a base todavia.

Motivo: Evitar bloquear el proyecto con drivers/arquitectura 32-bit hasta confirmar entorno. La API puede informar configuracion incompleta sin exponer credenciales.

## 2026-06-17 - Logging frontend centralizado

Decision: Se incorpora el modulo de logging existente de InforhardDesk adaptado a ABMCargaDiaria en `frontend/app/infrastructure/logging`.

Motivo: Necesitamos trazabilidad de requests/responses de API, errores de render, acciones de UI y tracebacks no capturados para diagnosticar problemas durante el desarrollo.
