"""Main application window for ABMCargaDiaria."""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import ttk

from app.config.settings import settings
from app.infrastructure.logging import get_logger
from app.config.tkinforhard import (
    IHAlert,
    IHBreadcrumb,
    IHButton,
    IHCombobox,
    IHSectionHeader,
    IHDateInput,
    IHDrawerMenu,
    IHGrid,
    IHInput,
    IHMetricCard,
    IHPage,
    IHRenderHost,
    IHTable,
    IHTopbar,
    TKINFORHARD_AVAILABLE,
    TKINFORHARD_IMPORT_ERROR,
)
from tkcalendar import Calendar

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
        self.drawer.add_item("Movimientos", command=self._show_movimientos)
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
        self._topbar_subtitle_var = tk.StringVar()
        ttk.Label(self.topbar, textvariable=self._topbar_subtitle_var, style="IH.TopbarTitle.TLabel").pack(side="right", padx=(0, 16))
        self._db_badge = ttk.Label(self.topbar, text="● DB ...", style="IH.TopbarTitle.TLabel", font=("Segoe UI", 11, "bold"))
        self._db_badge.pack(side="right", padx=(0, 12))
        self.root.after(300, self._refresh_asa9_status)

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
        self.root.bind("<Button-1>", self._on_root_click, add="+")

    def _on_root_click(self, event) -> None:
        if not self.drawer.is_open:
            return
        dx = self.drawer.winfo_rootx()
        dy = self.drawer.winfo_rooty()
        dw = self.drawer.winfo_width()
        dh = self.drawer.winfo_height()
        if not (dx <= event.x_root < dx + dw and dy <= event.y_root < dy + dh):
            self.drawer.close()

    def _show_caja_diaria(self) -> None:
        self.current_view_key = "caja_diaria"
        logger.info("RenderHost show view=caja_diaria")
        self.topbar.set_title("Caja Diaria")
        self._topbar_subtitle_var.set("Carga manual contra API backend y resumen calculado antes de mostrar la vista.")
        self.render_host.show(
            lambda master: CajaDiariaView(master, self.api_client, self._reload_current_view),
            cache_key="caja_diaria",
        )
        self._close_drawer_if_open()

    def _show_movimientos(self) -> None:
        self.current_view_key = "movimientos"
        logger.info("RenderHost show view=movimientos")
        self.topbar.set_title("Movimientos")
        self._topbar_subtitle_var.set("")
        self.render_host.show(
            lambda master: MovimientosView(master, self.api_client),
            cache_key="movimientos",
        )
        self._close_drawer_if_open()

    def _show_placeholder_view(self, title: str) -> None:
        key = f"placeholder:{title}"
        self.current_view_key = key
        logger.info("RenderHost show placeholder title=%s", title)
        self.topbar.set_title(title)
        self._topbar_subtitle_var.set("")
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

    def _refresh_asa9_status(self) -> None:
        try:
            respuesta = self.api_client.obtener_asa9_status()
            status = respuesta.get("data", {}).get("status", {})
            if status.get("ready"):
                self._db_badge.configure(text="● DB lista", foreground="#22c55e")
            else:
                self._db_badge.configure(text="● DB sin conexion", foreground="#ef4444")
        except ApiClientError:
            self._db_badge.configure(text="● DB sin conexion", foreground="#ef4444")
        self.root.after(30000, self._refresh_asa9_status)

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
        self.caja_data: dict | None = None
        self._fecha_filtro: str | None = None
        self.status_message = "Preparando vista..."
        self._build_widgets()

    def should_prepare_for_render(self) -> bool:
        return True

    def prepare_for_render(self, on_done, on_error=None) -> None:
        self._cargar_datos(self._fecha_filtro)
        on_done()

    def _cargar_datos(self, fecha: str | None = None) -> None:
        try:
            respuesta = self.api_client.listar_movimientos(fecha)
            data = respuesta.get("data", [])
            if data:
                self.movimientos_modelo = [movimiento_desde_api(d) for d in data]
                sufijo = f" ({fecha})" if fecha else ""
                self.status_message = f"API: {len(self.movimientos_modelo)} movimientos cargados{sufijo}."
            else:
                self.movimientos_modelo = []
                self.status_message = "Sin movimientos para la fecha seleccionada." if fecha else "API conectada. Sin movimientos aun."

            caja_respuesta = self.api_client.obtener_caja_diaria(fecha)
            self.caja_data = caja_respuesta.get("data")
        except ApiClientError:
            self.status_message = "API no disponible. Mostrando datos de prueba."
            self.caja_data = None

        self._render_metrics()
        self._render_table()
        self._set_status(self.status_message)

    def _build_widgets(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        page = IHPage(self, padding=24)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)

        self._build_filter_bar(page)

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

    def _build_filter_bar(self, parent) -> None:
        bar = ttk.Frame(parent)
        bar.pack(fill="x", pady=(0, 12))
        IHButton(bar, text="Limpiar", variant="secondary", outline=True, command=self._limpiar_filtro).pack(side="right")
        IHButton(bar, text="Filtrar", variant="primary", command=self._aplicar_filtro).pack(side="right", padx=(0, 6))
        ttk.Label(bar, text="Filtrar por fecha:").pack(side="left", padx=(0, 8))
        self.filtro_fecha_input = IHDateInput(bar, label=None)
        self.filtro_fecha_input.surface.configure(width=160)
        self.filtro_fecha_input.pack(side="left")
        tk.Button(
            bar,
            text="📅",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 12),
            command=self._abrir_calendario,
        ).pack(side="left", padx=(4, 0))

    def _abrir_calendario(self) -> None:
        popup = tk.Toplevel(self)
        popup.title("")
        popup.resizable(False, False)
        popup.grab_set()
        popup.configure(bg="#ffffff")
        x = self.filtro_fecha_input.winfo_rootx()
        y = self.filtro_fecha_input.winfo_rooty() + self.filtro_fecha_input.winfo_height() + 4
        popup.geometry(f"+{x}+{y}")

        actual = self.filtro_fecha_input.get().strip()
        try:
            año, mes, dia = (int(x) for x in actual.split("-"))
        except ValueError:
            from datetime import date
            hoy = date.today()
            año, mes, dia = hoy.year, hoy.month, hoy.day

        cal = Calendar(
            popup,
            selectmode="day",
            year=año, month=mes, day=dia,
            date_pattern="yyyy-mm-dd",
            background="#008A46",
            foreground="white",
            headersbackground="#008A46",
            headersforeground="white",
            selectbackground="#005522",
            selectforeground="white",
            normalbackground="#ffffff",
            normalforeground="#1a1a1a",
            weekendbackground="#f0faf4",
            weekendforeground="#008A46",
            othermonthbackground="#f5f5f5",
            othermonthforeground="#aaaaaa",
            othermonthwebackground="#f5f5f5",
            othermonthweforeground="#cccccc",
            font=("Segoe UI", 10),
            showweeknumbers=False,
        )
        cal.pack(padx=0, pady=0)
        try:
            cal._header_lbl.configure(background="#008A46", foreground="white")
            cal._l_arrow.configure(background="#008A46", foreground="white")
            cal._r_arrow.configure(background="#008A46", foreground="white")
        except Exception:
            pass

        def _confirmar():
            self.filtro_fecha_input.set(cal.get_date())
            popup.destroy()

        btn_frame = tk.Frame(popup, bg="#ffffff")
        btn_frame.pack(fill="x", padx=12, pady=(4, 12))
        tk.Button(
            btn_frame,
            text="Confirmar",
            command=_confirmar,
            relief="flat",
            bg="#008A46",
            fg="white",
            activebackground="#006633",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=7,
            cursor="hand2",
            bd=0,
        ).pack(fill="x")

    def _aplicar_filtro(self) -> None:
        fecha = self.filtro_fecha_input.get().strip()
        if not fecha:
            self._set_status("Ingresa una fecha para filtrar.")
            return
        self._fecha_filtro = fecha
        self._cargar_datos(fecha)

    def _limpiar_filtro(self) -> None:
        self._fecha_filtro = None
        self.filtro_fecha_input.set("")
        self._cargar_datos(None)

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

        if self.caja_data:
            estados = self.caja_data.get("estados", {})
            metric_data = [
                ("Ingresos", self._money(self.caja_data.get("ingresos")), f"{self.caja_data.get('movimientosTotal', 0)} mov."),
                ("Egresos", self._money(self.caja_data.get("egresos")), "Efectivo y rendiciones"),
                ("Efectivo", self._money(self.caja_data.get("efectivo")), "Impacto neto"),
                ("Banco", self._money(self.caja_data.get("banco")), f"Pendientes: {estados.get('pendientes', 0)}"),
            ]
        else:
            metricas = calcular_metricas(self.movimientos_modelo)
            metric_data = [
                ("Ingresos", self._money(metricas["ingresos"]), f"{metricas['total_movimientos']} mov."),
                ("Egresos", self._money(metricas["egresos"]), "Efectivo y rendiciones"),
                ("Efectivo", self._money(metricas["efectivo"]), "Impacto neto"),
                ("Banco", self._money(metricas["banco"]), f"Pendientes: {metricas['pendientes']}"),
            ]

        metrics = IHGrid(self.metrics_host, columns=4, gap=12)
        metrics.pack(fill="x")
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


class MovimientosView(ttk.Frame):
    """Lista completa de movimientos con filtros por fecha, tipo y estado."""

    def __init__(self, master, api_client: ApiClient) -> None:
        super().__init__(master)
        self.api_client = api_client
        self.movimientos: list = []
        self.status_message = "Cargando..."
        self._build_widgets()

    def should_prepare_for_render(self) -> bool:
        return True

    def prepare_for_render(self, on_done, on_error=None) -> None:
        self._cargar_datos()
        on_done()

    def _cargar_datos(self, fecha_desde: str | None = None, fecha_hasta: str | None = None,
                      tipo: str | None = None, estado: str | None = None) -> None:
        try:
            respuesta = self.api_client.listar_movimientos()
            data = respuesta.get("data", [])
            self.movimientos = data

            if fecha_desde:
                self.movimientos = [m for m in self.movimientos if m.get("fecha", "") >= fecha_desde]
            if fecha_hasta:
                self.movimientos = [m for m in self.movimientos if m.get("fecha", "") <= fecha_hasta]
            if tipo:
                self.movimientos = [m for m in self.movimientos if m.get("tipo") == tipo]
            if estado:
                self.movimientos = [m for m in self.movimientos if m.get("estado") == estado]

            self.status_message = f"{len(self.movimientos)} movimientos."
        except ApiClientError:
            self.status_message = "API no disponible."

        self._render_tabla()
        self._set_status(self.status_message)

    def _build_widgets(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        page = IHPage(self, padding=24)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)

        IHSectionHeader(page, title="Movimientos", subtitle="Listado completo de movimientos registrados.").pack(fill="x", pady=(0, 16))

        self._build_filtros(page)

        self.tabla = IHTable(
            page,
            columns=("Fecha", "Tipo", "Origen", "Estado", "Monto", "Descripcion"),
            rows=[],
            row_tag_key="semaforo",
        )
        self.tabla.pack(fill="both", expand=True, pady=(0, 8))

        footer = ttk.Frame(page)
        footer.pack(side="bottom", fill="x", pady=(8, 0))
        IHButton(footer, text="Refrescar", variant="secondary", outline=True, command=self._aplicar_filtros).pack(side="left")
        self.status_var = tk.StringVar(value="")
        ttk.Label(footer, textvariable=self.status_var).pack(side="left", padx=(12, 0))

    def _build_filtros(self, parent) -> None:
        bar = ttk.Frame(parent)
        bar.pack(fill="x", pady=(0, 12))

        ttk.Label(bar, text="Desde:").pack(side="left", padx=(0, 4))
        self.filtro_desde = IHDateInput(bar, label=None)
        self.filtro_desde.surface.configure(width=130)
        self.filtro_desde.pack(side="left", padx=(0, 12))

        ttk.Label(bar, text="Hasta:").pack(side="left", padx=(0, 4))
        self.filtro_hasta = IHDateInput(bar, label=None)
        self.filtro_hasta.surface.configure(width=130)
        self.filtro_hasta.pack(side="left", padx=(0, 12))

        ttk.Label(bar, text="Tipo:").pack(side="left", padx=(0, 4))
        self.filtro_tipo = IHCombobox(
            bar, label=None,
            values=["(todos)"] + [t.value for t in TipoMovimiento],
            state="readonly",
        )
        self.filtro_tipo.surface.configure(width=110)
        self.filtro_tipo.pack(side="left", padx=(0, 12))
        self.filtro_tipo.set("(todos)")

        ttk.Label(bar, text="Estado:").pack(side="left", padx=(0, 4))
        self.filtro_estado = IHCombobox(
            bar, label=None,
            values=["(todos)"] + [e.value for e in EstadoMovimiento],
            state="readonly",
        )
        self.filtro_estado.surface.configure(width=120)
        self.filtro_estado.pack(side="left", padx=(0, 12))
        self.filtro_estado.set("(todos)")

        IHButton(bar, text="Limpiar", variant="secondary", outline=True, command=self._limpiar_filtros).pack(side="right")
        IHButton(bar, text="Filtrar", variant="primary", command=self._aplicar_filtros).pack(side="right", padx=(0, 6))

    def _aplicar_filtros(self) -> None:
        desde = self.filtro_desde.get().strip() or None
        hasta = self.filtro_hasta.get().strip() or None
        tipo_val = self.filtro_tipo.get().strip()
        tipo = None if tipo_val == "(todos)" else tipo_val
        estado_val = self.filtro_estado.get().strip()
        estado = None if estado_val == "(todos)" else estado_val
        self._cargar_datos(desde, hasta, tipo, estado)

    def _limpiar_filtros(self) -> None:
        self.filtro_desde.set("")
        self.filtro_hasta.set("")
        self.filtro_tipo.set("(todos)")
        self.filtro_estado.set("(todos)")
        self._cargar_datos()

    def _render_tabla(self) -> None:
        filas = [movimiento_desde_api(m) for m in self.movimientos]
        self.tabla.load(movimientos_a_filas(filas))

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)


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



