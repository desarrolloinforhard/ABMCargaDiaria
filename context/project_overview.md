# Project Overview

## Objetivo

Crear una aplicacion desktop para gestionar Caja Diaria y Flujo de Caja reemplazando planillas Excel dispersas.

## Problema que resuelve

La informacion financiera diaria queda fragmentada entre hojas de calculo, movimientos bancarios, ventas por factura/remito, cuenta corriente y rendiciones. ABMCargaDiaria busca unificar esa operacion con trazabilidad, estados y reportes futuros.

## Arquitectura de trabajo

El proyecto se divide en tres areas principales:

- `frontend/`: cliente desktop Python con Tkinter, ttkbootstrap y TkInforHard.
- `backend/`: API Node.js + Express. Aca vive la conexion futura a ASA9, CSV, reglas y servicios.
- `context/`: memoria tecnica y funcional del proyecto.

El frontend no conecta directo a ASA9. Toda integracion de datos debe pasar por la API backend.

## Alcance inicial

- Base del proyecto separada en frontend/backend.
- Documentacion interna en `context/`.
- Ventana principal minima con TkInforHard.
- API Express inicial con health check y movimientos mock.
- Contrato API de movimientos.

## Alcance futuro

- Flujo unificado frontend/backend.
- Carga manual real desde UI hacia API.
- Conexion ASA9 por ODBC 32-bit desde backend.
- Importacion CSV bancaria desde backend.
- Cuenta corriente, rendiciones, sueldos, adelantos, conciliacion y reportes.

## Usuarios principales

- Administracion y caja.
- Responsables de control financiero.
- Empleados que rinden gastos o reciben adelantos.
- Equipo tecnico que mantiene integraciones y reportes.

## Roles del proyecto

- Misa: backend, API, ASA9, logica de negocio, CSV, persistencia, reportes.
- Nico: frontend, TkInforHard, pantallas, formularios, grillas, UX.

## Regla de colaboracion

Antes de implementar una funcionalidad compartida, se define o actualiza su contrato en `context/api_contracts/`. Backend y frontend implementan contra ese contrato.
