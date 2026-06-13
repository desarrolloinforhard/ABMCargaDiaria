# ABMCargaDiaria

ABMCargaDiaria es una aplicacion desktop en Python para reemplazar planillas Excel de Caja Diaria y Flujo de Caja.

## Objetivo

Centralizar ingresos, egresos, caja efectivo, movimientos bancarios, ventas, cuenta corriente, rendiciones, sueldos, adelantos, conciliacion y reportes en una herramienta administrativa clara para Windows.

## Stack

- Python
- Tkinter
- ttkbootstrap
- TkInforHard como libreria interna de UI
- ASA9 / Sybase SQL Anywhere mediante ODBC 32-bit en fase futura
- GitHub para versionado
- ClickUp para gestion operativa

## Estado actual

Version inicial `v0.0.1`: Fase 0 + Fase 1. El proyecto tiene estructura base, documentacion inicial, ventana principal minima y preparacion para usar TkInforHard. No conecta ASA9, no importa CSV y no implementa reglas completas de negocio todavia.

## Como ejecutar

Desde `J:\Proyectos\ABMCargaDiaria`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m app.main
```

Si TkInforHard no esta instalado en el entorno, el proyecto intenta detectar un checkout hermano en `J:\Proyectos\TkInforHard` mediante la ruta relativa `..\TkInforHard`. Tambien puede configurarse `TKINFORHARD_PATH`.

## Validacion rapida

```powershell
.\.venv\Scripts\python.exe -m py_compile app\main.py app\ui\main_window.py app\config\settings.py app\config\tkinforhard.py
.\.venv\Scripts\python.exe -m pytest
```

## Fases previstas

1. Fase 0 - Contexto y analisis TkInforHard
2. Fase 1 - Base del proyecto y ventana principal
3. Fase 2 - Modelo de movimientos
4. Fase 3 - Flujo unificado
5. Fase 4 - Carga manual de movimientos
6. Fase 5 - Conexion ASA9 ODBC 32-bit
7. Fase 6 - Ventas factura y remito
8. Fase 7 - Cuenta corriente
9. Fase 8 - Rendiciones
10. Fase 9 - Banco CSV
11. Fase 10 - Sueldos, plus y adelantos
12. Fase 11 - Conciliacion y reportes
13. Fase 12 - Release v1

## GitHub

No se hace push automatico en esta fase. Comandos sugeridos:

```powershell
git init
git add .
git commit -m "Inicializa estructura base de ABMCargaDiaria"
git branch -M main
git remote add origin URL_DEL_REPO
git push -u origin main
```
