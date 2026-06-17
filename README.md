# ABMCargaDiaria

ABMCargaDiaria es una aplicacion de Caja Diaria / Flujo de Caja organizada en dos partes:

- `frontend/`: cliente desktop Python con Tkinter, ttkbootstrap y TkInforHard.
- `backend/`: API Node.js + Express que centralizara ASA9, CSV bancario, reglas compartidas y servicios.

## Objetivo

Reemplazar planillas Excel de caja diaria con una herramienta administrativa clara para controlar ingresos, egresos, efectivo, bancos, ventas, cuenta corriente, rendiciones, sueldos, adelantos, conciliacion y reportes.

## Arquitectura actual

```text
ABMCargaDiaria/
  backend/      API Node.js + Express
  frontend/     App desktop Python + TkInforHard
  context/      Documentacion interna y decisiones
  docs/         Documentacion de usuario futura
  scripts/      Automatizaciones futuras
  config/       Configuracion externa futura
```

El frontend no conecta directo a ASA9. La conexion ASA9 / SQL Anywhere por ODBC 32-bit queda como responsabilidad futura del backend.

## Ejecutar frontend

```powershell
cd J:\Proyectos\ABMCargaDiaria\frontend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m app.main
```

## Ejecutar backend

```powershell
cd J:\Proyectos\ABMCargaDiaria\backend
npm install
npm run dev
```

## Validacion rapida frontend

```powershell
cd J:\Proyectos\ABMCargaDiaria\frontend
.\.venv\Scripts\python.exe -m py_compile app\main.py app\ui\main_window.py app\config\settings.py app\config\tkinforhard.py app\models\movimiento.py
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Estado actual

Fase 0 + Fase 1 completas y arquitectura ajustada para separar frontend/backend. Fase 2 queda orientada a modelo de movimientos y contrato API.
