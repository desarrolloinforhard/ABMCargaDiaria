# Decision Log

## 2026-06-12 - Arquitectura inicial sin ASA9

Decision: Se inicia ABMCargaDiaria con una arquitectura por capas y sin conexion ASA9 en la primera fase.

Motivo: Primero se valida estructura, documentacion y base visual con TkInforHard.

## 2026-06-12 - Adaptacion temporal si TkInforHard no importa

Decision: La ventana principal intenta usar TkInforHard instalado, `TKINFORHARD_PATH` o un checkout hermano `../TkInforHard`. Si no puede importarse, usa una pantalla Tkinter minima.

Motivo: Permite arrancar el proyecto sin bloquear la Fase 1, pero deja claro que la UI final debe volver a TkInforHard.
