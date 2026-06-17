"""Main application window for ABMCargaDiaria."""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import ttk

from app.config.settings import settings
from app.infrastructure.logging import get_logger
from app.config.tkinforhard import (
    IHAlert,
    IHButton,
    IHBreadcrumb,
    IHCombobox,
    IHDateInput,
    IHDrawerMenu,
    IHGrid,
    IHInput,
    IHMetricCard,
    IHPage,
    IHRenderHost,
    IHSectionHeader,
    IHTable,
    IHTopbar,
    TKINFORHARD_AVAILABLE,
    TKINFORHARD_IMPORT_ERROR,
)
from app.models import EstadoMovimiento, Movimiento, OrigenMovimiento, TipoMovimiento
from app.ui.mocks import MOVIMIENTOS_MOCK
from app.services.api_client import ApiClient, ApiClientError

logger = get_logger("ui.main_window")
from app.ui.utils.movimiento_adapter import calcular_metricas, movimiento_desde_api, movimientos_a_filas



class MainWindow:
    """Application shell with drawer navigation and deferred rendering."""

    def __init__(self, root: tk.Misc):
        self.root = root
        self.api_client = ApiClient()
        self.current_view_key = "caja_diaria"
        logger.info("Inicializando MainWindow")
        self.root.title(settings.app_name)
        self._configure_root()
        if TKINFORHARD_AVAILABLE:
            self._build_tkinforhard_shell()
            self._show_caja_diaria()
        else:
            self._build_temporary_shell()

    def _configure_root(self) -> None:
        self.root.geometry(f"{settings.window_width}x{settings.window_height}")
        self.root.minsize(1024, 640)

    def _build_tkinforhard_shell(self) -> None:
        shell = ttk.Frame(self.root)
        shell.pack(fill="both", expand=True)
        shell.rowconfigure(1, weight=1)
        shell.columnconfigure(0, weight=1)

        self.drawer = IHDrawerMenu(shell, title=settings.app_name, side="left", width=230)
        self.drawer.add_item("Caja Diaria", command=self._show_caja_diaria, active=True)
        self.drawer.add_item("Movimientos", command=lambda: self._show_placeholder_view("Movimientos"))
        self.drawer.add_item("Cuenta Corriente", command=lambda: self._show_placeholder_view("Cuenta Corriente"))
        self.drawer.add_item("Rendiciones", command=lambda: self._show_placeholder_view("Rendiciones"))
        self.drawer.add_item("Banco", command=lambda: self._show_placeholder_view("Banco"))
        self.drawer.add_item("Reportes", command=lambda: self._show_placeholder_view("Reportes"))

        self.topbar = IHTopbar(
            shell,
            title="Caja Diaria",
            on_toggle_theme=self._toggle_theme,
            on_toggle_menu=self.drawer.toggle,
        )
        self.topbar.grid(row=0, column=0, sticky="ew")

        self.render_host = IHRenderHost(
            shell,
            loading_text="Cargando modulo...",
            render_delay=140,
            min_loader_ms=900,
            min_loader_cycles=1,
            settle_delay=120,
            cache_views=True,
            prepare_timeout_ms=10000,
        )
        self.render_host.grid(row=1, column=0, sticky="nsew")

    def _show_caja_diaria(self) -> None:
        self.current_view_key = "caja_diaria"
        logger.info("RenderHost show view=caja_diaria")
        self.topbar.set_title("Caja Diaria")
        self.render_host.show(
            lambda master: CajaDiariaView(master, self.api_client, self._reload_current_view),
            cache_key="caja_diaria",
        )
        self._close_drawer_if_open()

    def _show_placeholder_view(self, title: str) -> None:
        key = f"placeholder:{title}"
        self.current_view_key = key
        logger.info("RenderHost show placeholder title=%s", title)
        self.topbar.set_title(title)
        self.render_host.show(lambda master: PlaceholderView(master, title), cache_key=key)
        self._close_drawer_if_open()

    def _reload_current_view(self) -> None:
        if self.current_view_key == "caja_diaria":
            self._show_caja_diaria()

    def _close_drawer_if_open(self) -> None:
        if getattr(self, "drawer", None) is not None and self.drawer.is_open:
            self.drawer.close()

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


class CajaDiariaView(ttk.Frame):
    """Caja Diaria frame prepared behind IHRenderHost before becoming visible."""

    def __init__(self, master, api_client: ApiClient, on_reload) -> None:
        super().__init__(master)
        self.api_client = api_client
        self.on_reload = on_reload
        self.movimientos_modelo: list[Movimiento] = list(MOVIMIENTOS_MOCK)
        self.status_message = "Preparando vista..."
        self._build_widgets()

    def should_prepare_for_render(self) -> bool:
        return True

    def prepare_for_render(self, on_done, on_error=None) -> None:
        try:
            respuesta = self.api_client.listar_movimientos()
            data = respuesta.get("data", [])
            if data:
                self.movimientos_modelo = [movimiento_desde_api(d) for d in data]
                self.status_message = f"API: {len(self.movimientos_modelo)} movimientos cargados."
            else:
                self.status_message = "API conectada. Sin movimientos aun — mostrando datos de prueba."
        except ApiClientError:
            self.status_message = "API no disponible. Mostrando datos de prueba."

        self._render_metrics()
        self._render_table()
        self._set_status(self.status_message)
        on_done()

    def _build_widgets(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        page = IHPage(self, padding=24)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)

        IHBreadcrumb(page, items=("Inicio", "Caja Diaria")).pack(anchor="w", pady=(0, 12))
        IHSectionHeader(
            page,
            title="Caja Diaria",
            subtitle="Carga manual contra API backend y resumen calculado antes de mostrar la vista.",
        ).pack(fill="x", pady=(0, 16))

        self.metrics_host = ttk.Frame(page)
        self.metrics_host.pack(fill="x", pady=(0, 18))

        self._build_manual_form(page)

        footer = ttk.Frame(page)
        footer.pack(side="bottom", fill="x", pady=(8, 0))
        IHButton(footer, text="Refrescar", variant="secondary", outline=True, command=self.on_reload).pack(side="left")
        self.status_var = tk.StringVar(value="API pendiente de consulta.")
        ttk.Label(footer, textvariable=self.status_var).pack(side="left", padx=(12, 0))

        self.table = IHTable(
            page,
            columns=("Fecha", "Tipo", "Origen", "Estado", "Monto", "Descripcion"),
            rows=[],
            row_tag_key="semaforo",
        )
        self.table.pack(fill="both", expand=True, pady=8)

    def _build_manual_form(self, parent) -> None:
        form = ttk.LabelFrame(parent, text="Carga manual de movimiento", padding=12)
        form.pack(fill="x", pady=(0, 10))
        for column in range(6):
            form.columnconfigure(column, weight=1)

        self.fecha_input = IHDateInput(form)
        self.fecha_input.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 8))
        self.fecha_input.set(date.today().isoformat())

        self.tipo_input = IHCombobox(
            form,
            label="Tipo",
            values=[tipo.value for tipo in TipoMovimiento],
            state="readonly",
        )
        self.tipo_input.grid(row=0, column=1, sticky="ew", padx=8, pady=(0, 8))
        self.tipo_input.set(TipoMovimiento.INGRESO.value)

        self.estado_input = IHCombobox(
            form,
            label="Estado",
            values=[estado.value for estado in EstadoMovimiento],
            state="readonly",
        )
        self.estado_input.grid(row=0, column=2, sticky="ew", padx=8, pady=(0, 8))
        self.estado_input.set(EstadoMovimiento.PENDIENTE.value)

        self.monto_input = IHInput(form, label="Monto", placeholder="0.00")
        self.monto_input.grid(row=0, column=3, sticky="ew", padx=8, pady=(0, 8))

        self.descripcion_input = IHInput(form, label="Descripcion", placeholder="Detalle del movimiento")
        self.descripcion_input.grid(row=0, column=4, sticky="ew", padx=8, pady=(0, 8))

        actions = ttk.Frame(form)
        actions.grid(row=0, column=5, sticky="sew", padx=(8, 0), pady=(18, 8))
        IHButton(actions, text="Guardar", variant="success", command=self._crear_movimiento_manual).pack(side="left")

    def _crear_movimiento_manual(self) -> None:
        payload = {
            "fecha": self.fecha_input.get().strip(),
            "tipo": self.tipo_input.get().strip(),
            "estado": self.estado_input.get().strip(),
            "origen": OrigenMovimiento.MANUAL.value,
            "monto": self.monto_input.get().strip(),
            "descripcion": self.descripcion_input.get().strip(),
            "esCuentaCorriente": False,
            "empleadoId": None,
            "rendicionId": None,
            "referenciaExterna": None,
        }

        if not payload["fecha"] or not payload["monto"] or not payload["descripcion"]:
            self._set_status("Completa fecha, monto y descripcion antes de guardar.")
            return

        try:
            self.api_client.crear_movimiento(payload)
            self._clear_form_after_save()
            self._set_status("Movimiento guardado. Renderizando vista actualizada...")
            self.on_reload()
        except ApiClientError as exc:
            self._set_status(f"No se pudo guardar: {exc}")

    def _render_metrics(self) -> None:
        for child in self.metrics_host.winfo_children():
            child.destroy()

        metricas = calcular_metricas(self.movimientos_modelo)
        metrics = IHGrid(self.metrics_host, columns=4, gap=12)
        metrics.pack(fill="x")
        metric_data = [
            ("Ingresos", self._money(metricas["ingresos"]), f"{metricas['total_movimientos']} mov."),
            ("Egresos", self._money(metricas["egresos"]), "Efectivo y rendiciones"),
            ("Efectivo", self._money(metricas["efectivo"]), "Impacto neto"),
            ("Banco", self._money(metricas["banco"]), f"Pendientes: {metricas['pendientes']}"),
        ]
        for index, (title, value, delta) in enumerate(metric_data):
            card = IHMetricCard(metrics, title=title, value=value, delta=delta, variant="outlined")
            card.canvas.configure(height=1)
            card.content.bind("<Configure>", lambda e, c=card: self._ajustar_altura_card(e, c), add="+")
            card.bind("<Map>", lambda e, c=card: self._ajustar_altura_card_map(c), add="+")
            metrics.add(card, index)

    def _render_table(self) -> None:
        self.table.load(movimientos_a_filas(self.movimientos_modelo))

    def _clear_form_after_save(self) -> None:
        self.fecha_input.set(date.today().isoformat())
        self.tipo_input.set(TipoMovimiento.INGRESO.value)
        self.estado_input.set(EstadoMovimiento.PENDIENTE.value)
        self.monto_input.set("")
        self.descripcion_input.set("")

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _ajustar_altura_card(self, event, card) -> None:
        if event.height < 4:
            return
        needed = event.height + card.padding * 2 + 4
        if card.canvas.winfo_reqheight() != needed:
            card.canvas.configure(height=needed)

    def _ajustar_altura_card_map(self, card) -> None:
        card.update_idletasks()
        h = card.content.winfo_reqheight()
        if h > 0:
            card.canvas.configure(height=h + card.padding * 2 + 4)

    def _money(self, value: str | int | float | None) -> str:
        try:
            amount = float(value or 0)
        except (TypeError, ValueError):
            amount = 0.0
        return f"$ {amount:,.2f}"


class PlaceholderView(ttk.Frame):
    """Placeholder rendered through IHRenderHost for modules not implemented yet."""

    def __init__(self, master, title: str) -> None:
        super().__init__(master)
        page = IHPage(self, padding=24)
        page.pack(fill="both", expand=True)
        IHBreadcrumb(page, items=("Inicio", title)).pack(anchor="w", pady=(0, 12))
        IHSectionHeader(
            page,
            title=title,
            subtitle="Modulo pendiente. Se renderiza mediante IHRenderHost para mantener transiciones seguras.",
        ).pack(fill="x", pady=(0, 16))
        IHAlert(
            page,
            title="Pendiente",
            message="Este modulo se implementara en una fase posterior.",
            variant="warning",
        ).pack(fill="x")



