# Technical Architecture

## Decision principal

ABMCargaDiaria se separa en dos aplicaciones dentro del mismo repositorio:

- `frontend/`: cliente desktop Python con Tkinter, ttkbootstrap y TkInforHard.
- `backend/`: API Node.js + Express.

Esta separacion evita mezclar UI desktop con integraciones, credenciales y reglas de acceso a datos.

## Frontend

Responsabilidades:

- Construir pantallas administrativas con TkInforHard.
- Mostrar dashboard, grillas, filtros y formularios.
- Consumir la API backend mediante HTTP en fases futuras.
- No conectarse directamente a ASA9.

Estructura principal:

- `frontend/app/ui`: ventanas, layouts, vistas, dialogos y componentes visuales.
- `frontend/app/models`: modelos livianos compartidos con la UI.
- `frontend/app/services`: adaptadores futuros para consumir API.
- `frontend/app/config`: configuracion del cliente desktop.

## Backend

Responsabilidades:

- Exponer API REST para movimientos, caja, banco, cuenta corriente, rendiciones y reportes.
- Centralizar reglas de negocio compartidas.
- Conectar ASA9 / Sybase SQL Anywhere mediante ODBC 32-bit en fase futura.
- Procesar CSV bancarios.
- Manejar credenciales, logs, errores y auditoria fuera del cliente desktop.

Estructura principal:

- `backend/src/routes`: rutas Express.
- `backend/src/controllers`: entrada HTTP y validacion de request.
- `backend/src/services`: casos de uso y reglas.
- `backend/src/repositories`: acceso a ASA9, CSV o persistencia auxiliar.
- `backend/src/models`: modelos/DTOs del backend.

## Flujo general de datos

1. El usuario opera en el frontend desktop.
2. El frontend llama a la API backend.
3. El backend valida reglas y coordina servicios.
4. Los repositories consultan ASA9, CSV bancario o persistencia auxiliar.
5. La API responde JSON normalizado.
6. El frontend renderiza grillas, metricas y estados.

## TkInforHard

Todo frontend debe basarse en TkInforHard. La fase inicial reviso `J:\Proyectos\TkInforHard\context` y adopta componentes `IH*` como `IHSidebar`, `IHTopbar`, `IHMetricCard`, `IHFilterBar` e `IHTable`.

## ASA9

ASA9 no se conecta en esta fase. La integracion se realizara desde `backend/` mediante configuracion externa y ODBC 32-bit cuando corresponda.

## Render host obligatorio en frontend

La shell desktop usa `IHRenderHost` como unico punto para cargar o cambiar modulos visuales. El patron esperado es:

1. El usuario pide una vista desde `IHDrawerMenu` o una accion equivalente.
2. `MainWindow` llama a `render_host.show(...)`.
3. El host muestra loader.
4. La vista construye widgets y ejecuta `prepare_for_render` para consultar datos.
5. El host intercambia la vista cuando ya esta lista.

Esto evita cortes visuales, pantallas a medio renderizar y parpadeos al cambiar de modulo.

## Drawer menu

La navegacion principal del frontend usa `IHDrawerMenu`, no sidebar fija. El drawer se abre/cierra desde `IHTopbar` y delega cada vista al `IHRenderHost`.

## Logging frontend

El frontend usa `app.infrastructure.logging` como logger centralizado:

- Archivo rotativo en `frontend/logs/abm_carga_diaria_frontend.log`.
- Salida por consola durante desarrollo.
- Hooks para excepciones no capturadas y errores en hilos.
- Logs de requests/responses del `ApiClient`.
- Logs de render/carga de vistas principales.

Toda integracion nueva de API o proceso de UI sensible debe registrar inicio, resultado y excepciones con traceback.
