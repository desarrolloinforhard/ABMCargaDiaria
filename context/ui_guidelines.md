# UI Guidelines

- Todo el diseno debe usar TkInforHard.
- Antes de usar un widget base, revisar si existe componente equivalente en TkInforHard.
- Verde para ingresos.
- Rojo para egresos.
- Amarillo/naranja para pendientes.
- Gris/azul para movimientos bancarios o neutros.
- Interfaz tipo sistema administrativo.
- Evitar efectos exagerados.
- Priorizar claridad, grillas, filtros y carga rapida.
- Debe funcionar bien en Windows.
- Componentes recomendados para Fase 1: `IHSidebar`, `IHTopbar`, `IHBreadcrumb`, `IHMetricCard`, `IHFilterBar`, `IHTable`, `IHAlert`.

## Renderizado de vistas

- Toda carga de frame, cambio de modulo o cambio visual pesado debe pasar por `IHRenderHost`.
- La vista debe cargar datos y construir widgets antes de hacerse visible.
- Si una vista consulta API, debe implementar `prepare_for_render(on_done, on_error)` o usar una preparacion externa del host.
- Evitar mostrar pantallas parcialmente armadas, grillas vacias por parpadeo o widgets que aparecen de a partes.
- Para acciones largas dentro de una vista ya visible se evaluara `IHBusyOverlay`; para cambio completo de modulo se usa `IHRenderHost`.

## Navegacion

- La navegacion principal usa `IHDrawerMenu` de TkInforHard.
- El menu debe poder abrirse y cerrarse desde la barra superior.
- El contenido del modulo se renderiza por separado en `IHRenderHost`; el drawer no debe construir pantallas directamente.
