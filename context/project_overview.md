# Project Overview

## Objetivo

Crear una aplicacion desktop para gestionar Caja Diaria y Flujo de Caja reemplazando planillas Excel dispersas.

## Problema que resuelve

La informacion financiera diaria queda fragmentada entre hojas de calculo, movimientos bancarios, ventas por factura/remito, cuenta corriente y rendiciones. ABMCargaDiaria busca unificar esa operacion con trazabilidad, estados y reportes futuros.

## Alcance inicial

- Base del proyecto Python.
- Documentacion interna en `context/`.
- Ventana principal minima con TkInforHard cuando este disponible.
- Preparacion de arquitectura por capas.

## Alcance futuro

- Modelo completo de movimientos.
- Carga manual.
- Conexion ASA9 por ODBC 32-bit.
- Importacion CSV bancaria.
- Cuenta corriente, rendiciones, sueldos, adelantos, conciliacion y reportes.

## Usuarios principales

- Administracion y caja.
- Responsables de control financiero.
- Empleados que rinden gastos o reciben adelantos.
- Equipo tecnico que mantiene integraciones y reportes.

## Roles del proyecto

- Misa: backend, ASA9, logica de negocio, CSV, persistencia, reportes.
- Nico: frontend, TkInforHard, pantallas, formularios, grillas, UX.
