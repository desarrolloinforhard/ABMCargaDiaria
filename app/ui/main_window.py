"""Main application window for ABMCargaDiaria."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.config.settings import settings
from app.config.tkinforhard import (
    IHAlert,
    IHBreadcrumb,
    IHEmptyState,
    IHFilterBar,
    IHGrid,
    IHMetricCard,
    IHPage,
    IHSectionHeader,
    IHSidebar,
    IHStack,
    IHTable,
    IHTopbar,
    TKINFORHARD_AVAILABLE,
    TKINFORHARD_IMPORT_ERROR,
)


class MainWindow:
    """Builds the first administrative shell of the application."""

    def __init__(self, root: tk.Misc):
        self.root = root
        self.root.title(settings.app_name)
        self._configure_root()
        if TKINFORHARD_AVAILABLE:
            self._build_tkinforhard_shell()
        else:
            self._build_temporary_shell()

    def _configure_root(self) -> None:
        self.root.geometry(f"{settings.window_width}x{settings.window_height}")
        self.root.minsize(1024, 640)

    def _build_tkinforhard_shell(self) -> None:
        shell = ttk.Frame(self.root)
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(1, weight=1)
        shell.rowconfigure(0, weight=1)

        sidebar = IHSidebar(
            shell,
            title=settings.app_name,
            items=[
                ("Caja Diaria", self._show_placeholder),
                ("Movimientos", self._show_placeholder),
                ("Cuenta Corriente", self._show_placeholder),
                ("Rendiciones", self._show_placeholder),
                ("Banco", self._show_placeholder),
                ("Reportes", self._show_placeholder),
            ],
        )
        sidebar.grid(row=0, column=0, sticky="ns")

        content = ttk.Frame(shell)
        content.grid(row=0, column=1, sticky="nsew")
        content.rowconfigure(1, weight=1)
        content.columnconfigure(0, weight=1)

        topbar = IHTopbar(content, title="Caja Diaria", on_toggle_theme=self._toggle_theme)
        topbar.grid(row=0, column=0, sticky="ew")

        page = IHPage(content, padding=24)
        page.grid(row=1, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)

        IHBreadcrumb(page, items=("Inicio", "Caja Diaria")).pack(anchor="w", pady=(0, 12))
        IHSectionHeader(
            page,
            title="Caja Diaria",
            subtitle="Base visual inicial para flujo de caja, movimientos y conciliacion futura.",
        ).pack(fill="x", pady=(0, 16))

        metrics = IHGrid(page, columns=4, gap=12)
        metrics.pack(fill="x", pady=(0, 18))
        metric_data = [
            ("Ingresos", "$ 0,00", "Preparado"),
            ("Egresos", "$ 0,00", "Preparado"),
            ("Efectivo", "$ 0,00", "Sin movimientos"),
            ("Banco", "$ 0,00", "Fase futura"),
        ]
        for index, (title, value, delta) in enumerate(metric_data):
            metrics.add(IHMetricCard(metrics, title=title, value=value, delta=delta, variant="outlined"), index)

        stack = IHStack(page, padding=0)
        stack.pack(fill="both", expand=True)

        filters = IHFilterBar(
            stack,
            fields=[
                {"type": "date", "key": "desde", "label": "Desde"},
                {"type": "date", "key": "hasta", "label": "Hasta"},
                {"type": "combo", "key": "estado", "label": "Estado", "values": ["(Todos)", "Pendiente", "Confirmado", "Conciliado", "Anulado"]},
                {"type": "button", "key": "buscar", "label": "Buscar", "variant": "primary"},
            ],
        )
        stack.add(filters, fill="x", pady=6)

        table = IHTable(
            stack,
            columns=("Fecha", "Tipo", "Origen", "Estado", "Monto"),
            rows=[
                {"Fecha": "-", "Tipo": "Ingreso", "Origen": "Manual", "Estado": "Pendiente", "Monto": "$ 0,00", "semaforo": "green"},
                {"Fecha": "-", "Tipo": "Egreso", "Origen": "Manual", "Estado": "Pendiente", "Monto": "$ 0,00", "semaforo": "red"},
                {"Fecha": "-", "Tipo": "Banco", "Origen": "ODBC/CSV futuro", "Estado": "Pendiente", "Monto": "$ 0,00", "semaforo": "yellow"},
            ],
            row_tag_key="semaforo",
        )
        stack.add(table, fill="both", pady=6)

        IHAlert(
            stack,
            title="Fase 1",
            message="ASA9, CSV, reglas completas y reportes quedan preparados pero sin implementacion todavia.",
            variant="info",
        ).pack(fill="x", pady=(12, 0))

    def _build_temporary_shell(self) -> None:
        """Fallback documented in context/decision_log.md until TkInforHard is installed."""

        frame = ttk.Frame(self.root, padding=24)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=settings.app_name, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Vista inicial: Caja Diaria", font=("Segoe UI", 12)).pack(anchor="w", pady=(8, 18))
        ttk.Label(
            frame,
            text=(
                "Adaptacion temporal: TkInforHard no pudo importarse. "
                "Instalar requirements.txt o revisar TKINFORHARD_PATH."
            ),
            foreground="#856404",
        ).pack(anchor="w", pady=(0, 12))
        ttk.Label(frame, text=f"Detalle tecnico: {TKINFORHARD_IMPORT_ERROR}").pack(anchor="w")
        ttk.Separator(frame).pack(fill="x", pady=16)
        ttk.Label(frame, text="Espacio reservado para dashboard futuro.").pack(anchor="w")

    def _toggle_theme(self) -> None:
        toggle = getattr(self.root, "toggle_theme", None)
        if callable(toggle):
            toggle()

    def _show_placeholder(self) -> None:
        return None
