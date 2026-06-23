"""Main application window for ABMCargaDiaria."""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import ttk
import ttkbootstrap as ttkbs

from app.config.settings import settings
from app.infrastructure.logging import get_logger
from app.config.tkinforhard import (
    IHAlert,
    IHBreadcrumb,
    IHButton,
    IHCombobox,
    IHSectionHeader,
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
from ttkbootstrap.widgets import DateEntry

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
        self.table.set_tag_color("grey", "#e2e8f0", "#64748b")
        self.table.pack(fill="both", expand=True, pady=8)

    def _build_filter_bar(self, parent) -> None:
        bar = ttk.Frame(parent)
        bar.pack(fill="x", pady=(0, 12))
        IHButton(bar, text="Limpiar", variant="secondary", outline=True, command=self._limpiar_filtro).pack(side="right")
        IHButton(bar, text="Filtrar", variant="primary", command=self._aplicar_filtro).pack(side="right", padx=(0, 6))
        ttk.Label(bar, text="Filtrar por fecha:").pack(side="left", padx=(0, 8))
        self.filtro_fecha_input = DateEntry(
            bar, dateformat="%Y-%m-%d", firstweekday=0,
            startdate=date.today(), bootstyle="success", width=12,
        )
        self.filtro_fecha_input.pack(side="left")

    def _aplicar_filtro(self) -> None:
        fecha = self.filtro_fecha_input.entry.get().strip()
        if not fecha:
            self._set_status("Ingresa una fecha para filtrar.")
            return
        self._fecha_filtro = fecha
        self._cargar_datos(fecha)

    def _limpiar_filtro(self) -> None:
        self._fecha_filtro = None
        self.filtro_fecha_input.entry.delete(0, "end")
        self._cargar_datos(None)

    def _build_manual_form(self, parent) -> None:
        form = ttk.LabelFrame(parent, text="Carga manual de movimiento", padding=12)
        form.pack(fill="x", pady=(0, 10))
        for column in range(6):
            form.columnconfigure(column, weight=1)

        self.fecha_input = DateEntry(
            form, dateformat="%Y-%m-%d", firstweekday=0,
            startdate=date.today(), bootstyle="success", width=12,
        )
        self.fecha_input.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 8))

        self.tipo_input = IHCombobox(
            form,
            label="Tipo",
            values=[tipo.value for tipo in TipoMovimiento],
            state="readonly",
        )
        self.tipo_input.grid(row=0, column=1, sticky="ew", padx=8, pady=(0, 8))
        self.tipo_input.set(TipoMovimiento.INGRESO.value)
        self.tipo_input.surface.bind("<<ComboboxSelected>>", self._on_tipo_changed)

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
        self.monto_input.entry.bind("<FocusOut>", self._format_monto, add="+")
        self.monto_input.entry.bind("<FocusIn>", self._unformat_monto, add="+")
        self.monto_input.entry.bind("<FocusIn>", lambda e: self.monto_input.clear_error(), add="+")
        self.monto_input.entry.bind("<Return>", lambda e: self._crear_movimiento_manual(), add="+")

        self.descripcion_input = IHInput(form, label="Descripcion", placeholder="Detalle del movimiento")
        self.descripcion_input.grid(row=0, column=4, sticky="ew", padx=8, pady=(0, 8))
        self.descripcion_input.entry.bind("<FocusIn>", lambda e: self.descripcion_input.clear_error(), add="+")
        self.descripcion_input.entry.bind("<Return>", lambda e: self._crear_movimiento_manual(), add="+")

        actions = ttk.Frame(form)
        actions.grid(row=0, column=5, sticky="sew", padx=(8, 0), pady=(18, 8))
        IHButton(actions, text="Guardar", variant="success", command=self._crear_movimiento_manual).pack(side="left")

        self.empleado_input = IHInput(form, label="Empleado ID", placeholder="ID del empleado")
        self.empleado_input.entry.bind("<FocusIn>", lambda e: self.empleado_input.clear_error(), add="+")
        self.empleado_input.entry.bind("<Return>", lambda e: self._crear_movimiento_manual(), add="+")
        self.rendicion_input = IHInput(form, label="Rendición ID", placeholder="ID de rendición")
        self.rendicion_input.entry.bind("<FocusIn>", lambda e: self.rendicion_input.clear_error(), add="+")
        self.rendicion_input.entry.bind("<Return>", lambda e: self._crear_movimiento_manual(), add="+")
        self._cuenta_corriente_var = tk.BooleanVar(value=False)
        self._cc_check = ttk.Checkbutton(form, text="Cuenta Corriente", variable=self._cuenta_corriente_var)

    def _on_tipo_changed(self, event=None) -> None:
        tipo = self.tipo_input.get().strip()
        self.empleado_input.grid_remove()
        self.rendicion_input.grid_remove()
        self._cc_check.grid_remove()

        if tipo in (TipoMovimiento.ADELANTO.value, TipoMovimiento.PLUS.value):
            self.empleado_input.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 8), pady=(0, 8))
        elif tipo == TipoMovimiento.RENDICION.value:
            self.rendicion_input.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 8), pady=(0, 8))

        if tipo in (TipoMovimiento.INGRESO.value, TipoMovimiento.EGRESO.value):
            self._cc_check.grid(row=1, column=2, sticky="w", padx=8, pady=(0, 8))

    def _format_monto(self, event=None) -> None:
        raw = self.monto_input.get().strip().replace(",", "")
        try:
            self.monto_input.set(f"{float(raw):,.2f}")
        except ValueError:
            pass

    def _unformat_monto(self, event=None) -> None:
        val = self.monto_input.get().strip().replace(",", "")
        self.monto_input.set(val)

    def _crear_movimiento_manual(self) -> None:
        tipo = self.tipo_input.get().strip()
        monto_raw = self.monto_input.get().strip().replace(",", "")
        descripcion = self.descripcion_input.get().strip()
        empleado_val = self.empleado_input.get().strip()
        rendicion_val = self.rendicion_input.get().strip()

        self.monto_input.clear_error()
        self.descripcion_input.clear_error()
        self.empleado_input.clear_error()
        self.rendicion_input.clear_error()

        valido = True

        if not monto_raw:
            self.monto_input.set_error()
            valido = False
        else:
            try:
                float(monto_raw)
            except ValueError:
                self.monto_input.set_error()
                valido = False

        if not descripcion:
            self.descripcion_input.set_error()
            valido = False

        if tipo in (TipoMovimiento.ADELANTO.value, TipoMovimiento.PLUS.value):
            if not empleado_val:
                self.empleado_input.set_error()
                valido = False
            elif not empleado_val.isdigit():
                self.empleado_input.set_error()
                valido = False

        if tipo == TipoMovimiento.RENDICION.value:
            if not rendicion_val:
                self.rendicion_input.set_error()
                valido = False
            elif not rendicion_val.isdigit():
                self.rendicion_input.set_error()
                valido = False

        if not valido:
            self._set_status("Corregí los campos marcados en rojo.")
            return

        payload = {
            "fecha": self.fecha_input.entry.get().strip(),
            "tipo": tipo,
            "estado": self.estado_input.get().strip(),
            "origen": OrigenMovimiento.MANUAL.value,
            "monto": monto_raw,
            "descripcion": descripcion,
            "esCuentaCorriente": self._cuenta_corriente_var.get() if tipo in (TipoMovimiento.INGRESO.value, TipoMovimiento.EGRESO.value) else False,
            "empleadoId": int(empleado_val) if empleado_val else None,
            "rendicionId": int(rendicion_val) if rendicion_val else None,
            "referenciaExterna": None,
        }

        try:
            self.api_client.crear_movimiento(payload)
            self._clear_form_after_save()
            self._set_status("Movimiento guardado.")
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
        self.fecha_input.entry.delete(0, "end")
        self.fecha_input.entry.insert(0, date.today().isoformat())
        self.tipo_input.set(TipoMovimiento.INGRESO.value)
        self.estado_input.set(EstadoMovimiento.PENDIENTE.value)
        self.monto_input.set("")
        self.descripcion_input.set("")
        self.empleado_input.set("")
        self.rendicion_input.set("")
        self._cuenta_corriente_var.set(False)
        self._on_tipo_changed()

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
        self._selected_id: int | None = None
        self._build_widgets()

    def should_prepare_for_render(self) -> bool:
        return True

    def prepare_for_render(self, on_done, on_error=None) -> None:
        self._cargar_datos()
        on_done()

    def _cargar_datos(self, fecha_desde: str | None = None, fecha_hasta: str | None = None,
                      tipo: str | None = None, estado: str | None = None) -> None:
        try:
            respuesta = self.api_client.listar_movimientos(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                tipo=tipo,
                estado=estado,
            )
            self.movimientos = respuesta.get("data", [])
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
        self.tabla.set_tag_color("grey", "#e2e8f0", "#64748b")
        self.tabla.pack(fill="both", expand=True, pady=(0, 8))
        self.tabla.tree.bind("<<TreeviewSelect>>", self._on_row_selected)

        footer = ttk.Frame(page)
        footer.pack(side="bottom", fill="x", pady=(8, 0))
        IHButton(footer, text="Refrescar", variant="secondary", outline=True, command=self._aplicar_filtros).pack(side="left")
        self.status_var = tk.StringVar(value="")
        ttk.Label(footer, textvariable=self.status_var).pack(side="left", padx=(12, 0))

        ttk.Separator(footer, orient="vertical").pack(side="left", fill="y", padx=12)
        self._sel_label_var = tk.StringVar(value="Sin selección")
        ttk.Label(footer, textvariable=self._sel_label_var).pack(side="left", padx=(0, 8))
        self._nuevo_estado_combo = IHCombobox(
            footer, label=None,
            values=[e.value for e in EstadoMovimiento],
        )
        self._nuevo_estado_combo.combobox.configure(state="disabled")
        self._nuevo_estado_combo.surface.configure(width=120)
        self._nuevo_estado_combo.pack(side="left", padx=(0, 6))
        self._btn_cambiar = IHButton(
            footer, text="Cambiar estado", variant="primary",
            command=self._cambiar_estado_seleccionado, state="disabled",
        )
        self._btn_cambiar.pack(side="left", padx=(0, 6))
        self._btn_eliminar = IHButton(
            footer, text="Eliminar", variant="danger",
            command=self._eliminar_seleccionado, state="disabled",
        )
        self._btn_eliminar.pack(side="left")

    def _build_filtros(self, parent) -> None:
        bar = ttk.Frame(parent)
        bar.pack(fill="x", pady=(0, 12))

        ttk.Label(bar, text="Desde:").pack(side="left", padx=(0, 4))
        self.filtro_desde = DateEntry(
            bar, dateformat="%Y-%m-%d", firstweekday=0,
            startdate=date.today(), bootstyle="primary", width=12,
        )
        self.filtro_desde.pack(side="left", padx=(0, 12))

        ttk.Label(bar, text="Hasta:").pack(side="left", padx=(0, 4))
        self.filtro_hasta = DateEntry(
            bar, dateformat="%Y-%m-%d", firstweekday=0,
            startdate=date.today(), bootstyle="primary", width=12,
        )
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
        desde = self.filtro_desde.entry.get().strip() or None
        hasta = self.filtro_hasta.entry.get().strip() or None
        tipo_val = self.filtro_tipo.get().strip()
        tipo = None if tipo_val == "(todos)" else tipo_val
        estado_val = self.filtro_estado.get().strip()
        estado = None if estado_val == "(todos)" else estado_val
        self._cargar_datos(desde, hasta, tipo, estado)

    def _limpiar_filtros(self) -> None:
        self.filtro_desde.entry.delete(0, "end")
        self.filtro_hasta.entry.delete(0, "end")
        self.filtro_tipo.set("(todos)")
        self.filtro_estado.set("(todos)")
        self._cargar_datos()

    def _on_row_selected(self, _event=None) -> None:
        selection = self.tabla.tree.selection()
        if not selection:
            self._selected_id = None
            self._sel_label_var.set("Sin selección")
            self._nuevo_estado_combo.combobox.configure(state="disabled")
            self._btn_cambiar.configure(state="disabled")
            self._btn_eliminar.configure(state="disabled")
            return

        index = self.tabla.tree.index(selection[0])
        if index >= len(self.movimientos):
            return

        mov = self.movimientos[index]
        self._selected_id = mov.get("id")
        estado_actual = mov.get("estado", "")
        self._sel_label_var.set(f"#{self._selected_id} — {estado_actual}")
        self._nuevo_estado_combo.set(estado_actual)
        self._nuevo_estado_combo.combobox.configure(state="readonly")
        self._btn_cambiar.configure(state="normal")
        self._btn_eliminar.configure(state="normal")

    def _cambiar_estado_seleccionado(self) -> None:
        if self._selected_id is None:
            return
        nuevo_estado = self._nuevo_estado_combo.get().strip()
        if not nuevo_estado:
            return
        try:
            self.api_client.actualizar_estado(self._selected_id, nuevo_estado)
            self._set_status(f"Estado de #{self._selected_id} actualizado a '{nuevo_estado}'.")
            self._cargar_datos()
        except ApiClientError as exc:
            self._set_status(f"Error al cambiar estado: {exc}")

    def _render_tabla(self) -> None:
        filas = [movimiento_desde_api(m) for m in self.movimientos]
        self.tabla.load(movimientos_a_filas(filas))
        self._selected_id = None
        self._sel_label_var.set("Sin selección")
        self._nuevo_estado_combo.combobox.configure(state="disabled")
        self._btn_cambiar.configure(state="disabled")
        self._btn_eliminar.configure(state="disabled")

    def _eliminar_seleccionado(self) -> None:
        if self._selected_id is None:
            return
        dialogo = _ConfirmDialog(
            self.winfo_toplevel(),
            title="Eliminar movimiento",
            message=f"¿Estás seguro de que querés eliminar el movimiento #{self._selected_id}? Esta acción no se puede deshacer.",
            confirm_text="Eliminar",
            confirm_variant="danger",
        )
        if not dialogo.confirmed:
            return
        try:
            self.api_client.eliminar_movimiento(self._selected_id)
            self._set_status(f"Movimiento #{self._selected_id} eliminado.")
            self._cargar_datos()
        except ApiClientError as exc:
            self._set_status(f"Error al eliminar: {exc}")

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)


class _ConfirmDialog(tk.Toplevel):
    """Modal de confirmación genérico con botones Confirmar y Cancelar."""

    def __init__(self, master, title: str, message: str, confirm_text: str = "Confirmar", confirm_variant: str = "danger"):
        super().__init__(master)
        self.confirmed = False
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.transient(master)

        outer = ttk.Frame(self, padding=24)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text=title, font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))
        ttk.Label(outer, text=message, wraplength=320).pack(anchor="w", pady=(0, 20))

        btn_row = ttk.Frame(outer)
        btn_row.pack(anchor="e")
        ttkbs.Button(btn_row, text="Cancelar", bootstyle="secondary", padding=(16, 8), command=self.destroy).pack(side="left", padx=(0, 8))
        ttkbs.Button(btn_row, text=confirm_text, bootstyle="danger", padding=(16, 8), command=self._confirm).pack(side="left")

        self.update_idletasks()
        pw = master.winfo_rootx() + master.winfo_width() // 2
        ph = master.winfo_rooty() + master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w // 2}+{ph - h // 2}")
        self.wait_window()

    def _confirm(self) -> None:
        self.confirmed = True
        self.destroy()


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



