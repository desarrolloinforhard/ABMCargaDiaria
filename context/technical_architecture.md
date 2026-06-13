# Technical Architecture

## Arquitectura por capas

ABMCargaDiaria se organiza en capas para separar responsabilidades:

- `app/ui`: ventanas, layouts, vistas, dialogos y componentes visuales.
- `app/services`: reglas de negocio y casos de uso.
- `app/repositories`: acceso a datos externos o persistencia local futura.
- `app/models`: entidades de dominio y estructuras de datos.
- `app/config`: configuracion de entorno, deteccion de librerias y parametros.
- `app/core`: primitivas internas compartidas.
- `app/utils`: utilidades transversales.

## Separacion UI / services / repositories / models

La UI no debe resolver reglas financieras ni hablar directo con ASA9. Las vistas llaman servicios; los servicios coordinan modelos y repositorios; los repositorios encapsulan ODBC, archivos o persistencia local.

## Uso de TkInforHard

Todo frontend debe basarse en TkInforHard. La fase inicial reviso `J:\Proyectos\TkInforHard\context` y adopta componentes `IH*` como `IHSidebar`, `IHTopbar`, `IHMetricCard`, `IHFilterBar` e `IHTable`. Si la libreria no puede importarse, se usa una adaptacion Tkinter temporal documentada como pendiente.

## Integracion futura ASA9

ASA9 / Sybase SQL Anywhere se integrara mediante ODBC 32-bit en una fase posterior. En Fase 1 no se abren conexiones ni se guardan credenciales.

## Persistencia local posible

Si los movimientos manuales necesitan persistencia antes de ASA9, se evaluara una base local o archivos configurables. Esa decision debe registrarse en `decision_log.md` antes de implementarse.

## Flujo general de datos

1. La UI captura filtros o acciones.
2. Los services validan reglas y estados.
3. Los repositories consultan ASA9, CSV bancario o persistencia local futura.
4. Los models normalizan movimientos.
5. La UI muestra grillas, indicadores y estados de conciliacion.
