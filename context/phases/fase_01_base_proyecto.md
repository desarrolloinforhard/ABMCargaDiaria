# Fase 1 - Base del proyecto y ventana principal

## Objetivo

Crear la estructura base, documentacion inicial y una ventana principal minima para Caja Diaria.

## Alcance

- Estructura de carpetas.
- README, changelog, roadmap y documentos de contexto.
- Punto de entrada `app/main.py`.
- Ventana principal en `app/ui/main_window.py`.
- Tests basicos no visuales.

## Tareas realizadas

- Creada arquitectura por capas.
- Agregada deteccion de TkInforHard.
- Agregada ventana principal con sidebar, topbar, metricas, filtros y tabla inicial si TkInforHard esta disponible.
- Preparado `requirements.txt` con `ttkbootstrap`, `pyodbc` y `../TkInforHard`.

## Pendientes

- Implementar modelo de movimientos.
- Definir services de ingresos/egresos.
- Crear formularios reales de carga manual.
- Conectar persistencia en fases posteriores.

## Riesgos

- Dependencia de ODBC 32-bit en Windows para fases futuras.
- Necesidad de mantener sincronizada la UI con evoluciones de TkInforHard.

## Proxima fase

Fase 2 - Modelo de movimientos.
