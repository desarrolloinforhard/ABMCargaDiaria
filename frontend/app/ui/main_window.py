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
from app.ui.mocks import MOVIMIENTOS_MOCK, VENTAS_FACTURAS_MOCK, VENTAS_REMITOS_MOCK
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
        self.drawer.add_item("Ventas", command=self._show_ventas)
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

    def _show_ventas(self) -> None:
        self.current_view_key = "ventas"
        logger.info("RenderHost show view=ventas")
        self.topbar.set_title("Ventas")
        self._topbar_subtitle_var.set("")
        self.render_host.show(
            lambda master: VentasView(master, self.api_client),
            cache_key="ventas",
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


def _fix_combobox_popup(ih_combo) -> None:
    """Aplica color IH al campo de entrada y al listbox del dropdown.

    Dos partes:
    1. Campo de entrada (foreground del widget): se fija al mapear el widget y en cada
       cambio de tema, porque ttkbootstrap puede resetearlo al mostrar el widget.
    2. Listbox del dropdown: ConfigureListbox (Tcl) resetea el fondo en CADA apertura,
       así que se corrige via after(0) desde ButtonPress (corre tras ConfigureListbox,
       antes del render) y via <Map> del popup como respaldo.
    """
    cb = ih_combo.combobox

    def _fg():
        return ttk.Style().lookup("IH.TLabel", "foreground") or "#ffffff"

    def _bg():
        return ttk.Style().lookup("IH.TFrame", "background") or "#000000"

    def _fix_entry(_event=None):
        try:
            bg, fg = _bg(), _fg()
            # fieldbackground en TCombobox se controla SOLO via style map, no via configure.
            # ttkbootstrap lo hardcodea en [('readonly', '#555555')], hay que pisarlo.
            ttk.Style().map("TCombobox",
                            fieldbackground=[("readonly", bg), ("focus", bg), ("", bg)])
        except Exception:
            pass
        try:
            cb.configure(foreground=_fg())
        except Exception:
            pass

    # Fijar texto y fondo del campo: al mostrarse por primera vez y en cada cambio de tema
    _fix_entry()
    cb.bind("<Map>", _fix_entry, add="+")
    ih_combo.bind("<<IHThemeChanged>>", _fix_entry, add="+")

    # --- Fix del popup dropdown ---
    try:
        pd = cb.tk.eval(f"ttk::combobox::PopdownWindow {cb}")
    except Exception:
        return

    def _apply(_event=None):
        try:
            bg, fg = _bg(), _fg()
            cb.tk.call(f"{pd}.f.l", "configure",
                       "-background", bg, "-foreground", fg,
                       "-selectbackground", bg, "-selectforeground", fg)
            cb.configure(foreground=fg)
        except Exception:
            pass

    def _schedule(_event=None):
        cb.after(0, _apply)

    _apply()
    try:
        popup = cb.nametowidget(pd)
        popup.bind("<Map>", _apply, add="+")
    except Exception:
        try:
            cmd = cb.tk.register(_apply)
            cb.tk.call("bind", pd, "<Map>", f"+{cmd}")
        except Exception:
            pass
    cb.bind("<ButtonPress-1>", _schedule, add="+")
    cb.bind("<Down>", _schedule, add="+")


def _fix_dateentry_theme(date_entry) -> None:
    """Fuerza al botón de DateEntry a regenerar su estilo (imagen de calendario)
    cada vez que el tema IH cambia. ttkbootstrap crea el estilo 'Date.TButton'
    on-demand en el builder actual; si el tema es nuevo ese estilo no existe aún
    y el ícono desaparece. Reconfigurando el botón forzamos su creación."""
    def _reconfigure(_event=None):
        try:
            date_entry.button.configure(bootstyle=[date_entry._bootstyle, "date"])
        except Exception:
            pass
    date_entry.bind("<<IHThemeChanged>>", _reconfigure, add="+")


def _fix_treeview_border(tree) -> None:
    """Anula el borde gris/celeste que ttkbootstrap aplica al Treeview en foco."""
    try:
        s = ttk.Style()
        s.map("IH.Treeview",
              bordercolor=[("focus", "#000000"), ("!focus", "#000000"), ("", "#000000")],
              lightcolor=[("focus", "#000000"), ("", "#000000")],
              darkcolor=[("focus", "#000000"), ("", "#000000")])
        s.configure("IH.Treeview", borderwidth=0, relief="flat")
    except Exception:
        pass


_TABLE_TAGS_DARK = {
    "green":  ("#071a0f", "#ffffff"),
    "red":    ("#1a0707", "#ffffff"),
    "yellow": ("#1a1507", "#ffffff"),
    "grey":   ("#141414", "#9ca3af"),
}
_TABLE_TAGS_LIGHT = {
    "green":  ("#dcfce7", "#166534"),
    "red":    ("#fee2e2", "#991b1b"),
    "yellow": ("#fef9c3", "#854d0e"),
    "grey":   ("#e2e8f0", "#64748b"),
}


def _apply_table_tags(table, tags=("green", "red", "yellow", "grey")) -> None:
    """Aplica los colores de tag correctos según el tema activo (oscuro o claro)."""
    is_dark = ttk.Style().lookup("IH.TFrame", "background") == "#000000"
    palette = _TABLE_TAGS_DARK if is_dark else _TABLE_TAGS_LIGHT
    for tag in tags:
        if tag in palette:
            table.set_tag_color(tag, *palette[tag])


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
        self.metrics_host.pack(fill="x", pady=(0, 12))

        self._action_bar = ttk.Frame(page, style="IH.TFrame")
        self._action_bar.pack(fill="x", pady=(0, 6))
        self._btn_nuevo = IHButton(self._action_bar, text="Nuevo Movimiento", variant="primary", command=self._mostrar_form)
        self._btn_nuevo.pack(side="right")
        ttk.Label(self._action_bar, text="Movimientos del día", font=("Segoe UI", 11, "bold"), style="IH.TLabel").pack(side="left", fill="x", expand=True)

        self._build_manual_form(page)

        footer = ttk.Frame(page, style="IH.TFrame")
        footer.pack(side="bottom", fill="x", pady=(8, 0))
        IHButton(footer, text="Refrescar", variant="secondary", outline=True, command=self.on_reload).pack(side="left")
        self.status_var = tk.StringVar(value="API pendiente de consulta.")
        ttk.Label(footer, textvariable=self.status_var, style="IH.TLabel").pack(side="left", padx=(12, 0))

        self.table = IHTable(
            page,
            columns=("Fecha", "Tipo", "Origen", "Estado", "Monto", "Descripcion"),
            rows=[],
            row_tag_key="semaforo",
        )
        _apply_table_tags(self.table)
        self.table.bind("<<IHThemeChanged>>", lambda _: _apply_table_tags(self.table), add="+")
        self.table.pack(fill="both", expand=True, pady=8)

    def _build_filter_bar(self, parent) -> None:
        bar = ttk.Frame(parent, style="IH.TFrame")
        bar.pack(fill="x", pady=(0, 12))
        IHButton(bar, text="Limpiar", variant="secondary", outline=True, command=self._limpiar_filtro).pack(side="right")
        IHButton(bar, text="Filtrar", variant="primary", command=self._aplicar_filtro).pack(side="right", padx=(0, 6))
        ttk.Label(bar, text="Filtrar por fecha:", style="IH.TLabel").pack(side="left", padx=(0, 8))
        self.filtro_fecha_input = DateEntry(
            bar, dateformat="%Y-%m-%d", firstweekday=0,
            startdate=date.today(), bootstyle="success", width=12,
        )
        self.filtro_fecha_input.pack(side="left")
        _fix_dateentry_theme(self.filtro_fecha_input)

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

    def _mostrar_form(self) -> None:
        self._form_frame.pack(after=self._action_bar, fill="x", pady=(0, 10))

    def _ocultar_form(self) -> None:
        self._form_frame.pack_forget()

    def _build_manual_form(self, parent) -> None:
        self._form_frame = ttk.Frame(parent, style="IH.TFrame")

        _header = ttk.Frame(self._form_frame, style="IH.TFrame")
        _header.pack(fill="x", pady=(6, 2))
        ttk.Label(_header, text="Carga manual de movimiento", style="IH.Muted.TLabel").pack(side="left")
        ttk.Separator(self._form_frame).pack(fill="x", pady=(0, 8))

        _fc = ttk.Frame(self._form_frame, style="IH.TFrame", padding=(0, 0, 0, 8))
        _fc.pack(fill="x")
        for column in range(6):
            _fc.columnconfigure(column, weight=1)

        self.fecha_input = DateEntry(
            _fc, dateformat="%Y-%m-%d", firstweekday=0,
            startdate=date.today(), bootstyle="success", width=12,
        )
        self.fecha_input.grid(row=0, column=0, sticky="sew", padx=(0, 8), pady=(0, 8))
        _fix_dateentry_theme(self.fecha_input)

        self.tipo_input = IHCombobox(
            _fc,
            label="Tipo",
            values=[tipo.value for tipo in TipoMovimiento],
            state="readonly",
        )
        self.tipo_input.grid(row=0, column=1, sticky="ew", padx=8, pady=(0, 8))
        self.tipo_input.set(TipoMovimiento.INGRESO.value)
        self.tipo_input.surface.bind("<<ComboboxSelected>>", self._on_tipo_changed)

        self.estado_input = IHCombobox(
            _fc,
            label="Estado",
            values=[estado.value for estado in EstadoMovimiento],
            state="readonly",
        )
        self.estado_input.grid(row=0, column=2, sticky="ew", padx=8, pady=(0, 8))
        self.estado_input.set(EstadoMovimiento.PENDIENTE.value)

        self.monto_input = IHInput(_fc, label="Monto", placeholder="0.00")
        self.monto_input.grid(row=0, column=3, sticky="ew", padx=8, pady=(0, 8))
        self.monto_input.entry.bind("<FocusOut>", self._format_monto, add="+")
        self.monto_input.entry.bind("<FocusIn>", self._unformat_monto, add="+")
        self.monto_input.entry.bind("<FocusIn>", lambda e: self.monto_input.clear_error(), add="+")
        self.monto_input.entry.bind("<Return>", lambda e: self._crear_movimiento_manual(), add="+")

        self.descripcion_input = IHInput(_fc, label="Descripcion", placeholder="Detalle del movimiento")
        self.descripcion_input.grid(row=0, column=4, sticky="ew", padx=8, pady=(0, 8))
        self.descripcion_input.entry.bind("<FocusIn>", lambda e: self.descripcion_input.clear_error(), add="+")
        self.descripcion_input.entry.bind("<Return>", lambda e: self._crear_movimiento_manual(), add="+")

        actions = ttk.Frame(_fc, style="IH.TFrame")
        actions.grid(row=0, column=5, sticky="sew", padx=(8, 0), pady=(18, 8))
        IHButton(actions, text="Guardar", variant="success", command=self._crear_movimiento_manual).pack(side="left")
        IHButton(actions, text="Ocultar", variant="secondary", outline=True, command=self._ocultar_form).pack(side="left", padx=(6, 0))

        self.empleado_input = IHInput(_fc, label="Empleado ID", placeholder="ID del empleado")
        self.empleado_input.entry.bind("<FocusIn>", lambda e: self.empleado_input.clear_error(), add="+")
        self.empleado_input.entry.bind("<Return>", lambda e: self._crear_movimiento_manual(), add="+")
        self.rendicion_input = IHInput(_fc, label="Rendición ID", placeholder="ID de rendición")
        self.rendicion_input.entry.bind("<FocusIn>", lambda e: self.rendicion_input.clear_error(), add="+")
        self.rendicion_input.entry.bind("<Return>", lambda e: self._crear_movimiento_manual(), add="+")
        self._cuenta_corriente_var = tk.BooleanVar(value=False)
        self._cc_check = ttk.Checkbutton(_fc, text="Cuenta Corriente", variable=self._cuenta_corriente_var)
        _fix_combobox_popup(self.tipo_input)
        _fix_combobox_popup(self.estado_input)

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

        self._build_filtros(page)

        tabla_border = tk.Frame(page, highlightthickness=2, highlightbackground="#22c55e", highlightcolor="#22c55e", bd=0, background="#000000")
        tabla_border.pack(fill="both", expand=True, pady=(0, 8))
        self.tabla = IHTable(
            tabla_border,
            columns=("Fecha", "Tipo", "Origen", "Estado", "Monto", "Descripcion"),
            rows=[],
            row_tag_key="semaforo",
        )
        _apply_table_tags(self.tabla)
        self.tabla.bind("<<IHThemeChanged>>", lambda _: _apply_table_tags(self.tabla), add="+")
        self.tabla.pack(fill="both", expand=True)
        self.tabla._border.configure(bg="#000000", highlightthickness=0)
        _fix_treeview_border(self.tabla.tree)
        self.tabla.bind("<<IHThemeChanged>>", lambda _: (
            self.tabla._border.configure(bg="#000000", highlightthickness=0),
            _fix_treeview_border(self.tabla.tree),
        ), add="+")
        self.tabla.tree.bind("<<TreeviewSelect>>", self._on_row_selected)

        footer = ttk.Frame(page, style="IH.TFrame")
        footer.pack(side="bottom", fill="x", pady=(8, 0))
        IHButton(footer, text="Refrescar", variant="secondary", outline=True, command=self._aplicar_filtros).pack(side="left")
        self.status_var = tk.StringVar(value="")
        ttk.Label(footer, textvariable=self.status_var, style="IH.TLabel").pack(side="left", padx=(12, 0))

        ttk.Separator(footer, orient="vertical").pack(side="left", fill="y", padx=12)
        self._sel_label_var = tk.StringVar(value="Sin selección")
        ttk.Label(footer, textvariable=self._sel_label_var, style="IH.TLabel").pack(side="left", padx=(0, 8))
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
        _fix_combobox_popup(self._nuevo_estado_combo)

    def _build_filtros(self, parent) -> None:
        bar = ttk.Frame(parent, style="IH.TFrame")
        bar.pack(fill="x", pady=(0, 12))

        ttk.Label(bar, text="Desde:", style="IH.TLabel").pack(side="left", padx=(0, 4))
        self.filtro_desde = DateEntry(
            bar, dateformat="%Y-%m-%d", firstweekday=0,
            startdate=date.today(), bootstyle="primary", width=12,
        )
        self.filtro_desde.pack(side="left", padx=(0, 12))
        _fix_dateentry_theme(self.filtro_desde)

        ttk.Label(bar, text="Hasta:", style="IH.TLabel").pack(side="left", padx=(0, 4))
        self.filtro_hasta = DateEntry(
            bar, dateformat="%Y-%m-%d", firstweekday=0,
            startdate=date.today(), bootstyle="primary", width=12,
        )
        self.filtro_hasta.pack(side="left", padx=(0, 12))
        _fix_dateentry_theme(self.filtro_hasta)

        ttk.Label(bar, text="Tipo:", style="IH.TLabel").pack(side="left", padx=(0, 4))
        self.filtro_tipo = IHCombobox(
            bar, label=None,
            values=["(todos)"] + [t.value for t in TipoMovimiento],
            state="readonly",
        )
        self.filtro_tipo.surface.configure(width=110)
        self.filtro_tipo.pack(side="left", padx=(0, 12))
        self.filtro_tipo.set("(todos)")

        ttk.Label(bar, text="Estado:", style="IH.TLabel").pack(side="left", padx=(0, 4))
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
        _fix_combobox_popup(self.filtro_tipo)
        _fix_combobox_popup(self.filtro_estado)

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


_ESTADOS_FACTURA = ["(todos)", "pendiente", "pagada", "anulada"]
_ESTADOS_REMITO = ["(todos)", "pendiente_facturar", "entregado", "anulado"]
_TAG_VENTAS: dict[str, str] = {
    "pagada": "green",
    "entregado": "green",
    "anulada": "grey",
    "anulado": "grey",
}


class VentasView(ttk.Frame):
    """Vista de ventas con tabs de Facturas y Remitos."""

    def __init__(self, master, api_client: ApiClient) -> None:
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        page = IHPage(self, padding=24)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)

        self._tab_bar = ttk.Frame(page, style="IH.TFrame")
        self._tab_bar.pack(fill="x", pady=(0, 8))

        outer = tk.Frame(page, highlightthickness=2, highlightbackground="#22c55e", highlightcolor="#22c55e", bd=0, background="#000000")
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        content = tk.Frame(outer, background="#000000")
        content.grid(row=0, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        self._facturas_tab = _VentasTabFrame(content, api_client, "facturas")
        self._remitos_tab = _VentasTabFrame(content, api_client, "remitos")
        self._facturas_tab.grid(row=0, column=0, sticky="nsew")
        self._remitos_tab.grid(row=0, column=0, sticky="nsew")

        self._active_tab = "facturas"
        self._render_tab_buttons()
        self._facturas_tab.lift()

    def _render_tab_buttons(self) -> None:
        for w in self._tab_bar.winfo_children():
            w.destroy()
        IHButton(
            self._tab_bar, text="Facturas",
            variant="primary" if self._active_tab == "facturas" else "secondary",
            outline=self._active_tab != "facturas",
            command=self._show_facturas,
        ).pack(side="left", padx=(0, 4), pady=4)
        IHButton(
            self._tab_bar, text="Remitos",
            variant="primary" if self._active_tab == "remitos" else "secondary",
            outline=self._active_tab != "remitos",
            command=self._show_remitos,
        ).pack(side="left", pady=4)

    def _show_facturas(self) -> None:
        self._active_tab = "facturas"
        self._facturas_tab.lift()
        self._render_tab_buttons()

    def _show_remitos(self) -> None:
        self._active_tab = "remitos"
        self._remitos_tab.lift()
        self._render_tab_buttons()

    def should_prepare_for_render(self) -> bool:
        return True

    def prepare_for_render(self, on_done, on_error=None) -> None:
        self._facturas_tab._cargar_datos()
        self._remitos_tab._cargar_datos()
        on_done()


class _VentasTabFrame(ttk.Frame):
    """Tab generico para Facturas o Remitos dentro de VentasView."""

    def __init__(self, master, api_client: ApiClient, tipo: str) -> None:
        super().__init__(master, padding=0, style="IH.TFrame")
        self.api_client = api_client
        self.tipo = tipo
        self._filas: list[dict] = []
        self._build_widgets()

    def _build_widgets(self) -> None:
        self._build_filtros()

        footer = ttk.Frame(self, style="IH.TFrame")
        footer.pack(side="bottom", fill="x", padx=12, pady=(8, 8))
        IHButton(footer, text="Refrescar", variant="secondary", outline=True, command=self._aplicar_filtros).pack(side="left")
        self.status_var = tk.StringVar(value="")
        ttk.Label(footer, textvariable=self.status_var, style="IH.TLabel").pack(side="left", padx=(12, 0))

        tabla_border = tk.Frame(self, highlightthickness=2, highlightbackground="#22c55e", highlightcolor="#22c55e", bd=0, background="#000000")
        tabla_border.pack(fill="both", expand=True, padx=12, pady=(0, 0))
        self.tabla = IHTable(
            tabla_border,
            columns=("Fecha", "Cliente", "Comprobante", "Total", "Estado", "Origen"),
            rows=[],
            row_tag_key="semaforo",
        )
        _apply_table_tags(self.tabla, tags=("green", "grey"))
        self.tabla.bind("<<IHThemeChanged>>", lambda _: _apply_table_tags(self.tabla, tags=("green", "grey")), add="+")
        self.tabla.pack(fill="both", expand=True)
        self.tabla._border.configure(bg="#000000", highlightthickness=0)
        _fix_treeview_border(self.tabla.tree)
        self.tabla.bind("<<IHThemeChanged>>", lambda _: (
            self.tabla._border.configure(bg="#000000", highlightthickness=0),
            _fix_treeview_border(self.tabla.tree),
        ), add="+")

    def _build_filtros(self) -> None:
        bar = ttk.Frame(self, style="IH.TFrame")
        bar.pack(fill="x", padx=12, pady=(8, 4))

        ttk.Label(bar, text="Desde:", style="IH.TLabel").pack(side="left", padx=(0, 4))
        self.filtro_desde = DateEntry(
            bar, dateformat="%Y-%m-%d", firstweekday=0,
            startdate=date.today(), bootstyle="primary", width=12,
        )
        self.filtro_desde.pack(side="left", padx=(0, 12))
        _fix_dateentry_theme(self.filtro_desde)

        ttk.Label(bar, text="Hasta:", style="IH.TLabel").pack(side="left", padx=(0, 4))
        self.filtro_hasta = DateEntry(
            bar, dateformat="%Y-%m-%d", firstweekday=0,
            startdate=date.today(), bootstyle="primary", width=12,
        )
        self.filtro_hasta.pack(side="left", padx=(0, 12))
        _fix_dateentry_theme(self.filtro_hasta)

        ttk.Label(bar, text="Estado:", style="IH.TLabel").pack(side="left", padx=(0, 4))
        estados = _ESTADOS_FACTURA if self.tipo == "facturas" else _ESTADOS_REMITO
        self.filtro_estado = IHCombobox(bar, label=None, values=estados, state="readonly")
        self.filtro_estado.surface.configure(width=150)
        self.filtro_estado.pack(side="left", padx=(0, 12))
        self.filtro_estado.set(estados[0])

        IHButton(bar, text="Limpiar", variant="secondary", outline=True, command=self._limpiar_filtros).pack(side="right")
        IHButton(bar, text="Filtrar", variant="primary", command=self._aplicar_filtros).pack(side="right", padx=(0, 6))
        _fix_combobox_popup(self.filtro_estado)

    def _cargar_datos(
        self,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
        estado: str | None = None,
    ) -> None:
        try:
            if self.tipo == "facturas":
                respuesta = self.api_client.listar_facturas(fecha_desde, fecha_hasta, estado)
            else:
                respuesta = self.api_client.listar_remitos(fecha_desde, fecha_hasta, estado)
            self._filas = respuesta.get("data", [])
            self.status_var.set(f"{len(self._filas)} registros.")
        except ApiClientError:
            mocks = VENTAS_FACTURAS_MOCK if self.tipo == "facturas" else VENTAS_REMITOS_MOCK
            self._filas = list(mocks)
            self.status_var.set(f"API no disponible. Mostrando {len(self._filas)} registros de prueba.")
        self._render_tabla()

    def _aplicar_filtros(self) -> None:
        desde = self.filtro_desde.entry.get().strip() or None
        hasta = self.filtro_hasta.entry.get().strip() or None
        estado_val = self.filtro_estado.get().strip()
        estado = None if estado_val == "(todos)" else estado_val
        self._cargar_datos(desde, hasta, estado)

    def _limpiar_filtros(self) -> None:
        self.filtro_desde.entry.delete(0, "end")
        self.filtro_hasta.entry.delete(0, "end")
        estados = _ESTADOS_FACTURA if self.tipo == "facturas" else _ESTADOS_REMITO
        self.filtro_estado.set(estados[0])
        self._cargar_datos()

    def _render_tabla(self) -> None:
        filas = []
        for item in self._filas:
            estado = item.get("estado", "")
            total = item.get("total", "0")
            try:
                total_fmt = f"$ {float(total):,.2f}"
            except (TypeError, ValueError):
                total_fmt = str(total)
            filas.append({
                "Fecha": item.get("fecha", ""),
                "Cliente": item.get("cliente", ""),
                "Comprobante": item.get("comprobante", ""),
                "Total": total_fmt,
                "Estado": estado.replace("_", " ").capitalize(),
                "Origen": item.get("origen", "").upper(),
                "semaforo": _TAG_VENTAS.get(estado, ""),
            })
        self.tabla.load(filas)


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



