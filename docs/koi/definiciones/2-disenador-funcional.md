# 2 - Diseñador funcional — Proyecto KOI

> Memoria acumulativa del agente diseñador funcional.
> Etapa: Diseño funcional. Estado: ✅ ACTUALIZADO — P-A01→P-A07 incorporadas · ventas 4 campos · TC con selector cotización · preview editable · Reabierto eliminado. Módulo E2-02 (Fichador) diseñado en §10. Sprint UX/UI Inversor + fixes diseñado en §11.
> Fecha: 2026-06-11. Última actualización: 2026-08-13 — §12 Mi Inversión: dividendos/recupero en pesos. Input: 1-analista-funcional.md §13 (Análisis cerrado).

## 1. Alcance funcional resumido

Sistema web con dos perfiles (Administrador / Inversor). El Admin carga el estado de resultados mensual, configura catálogos y porcentajes, gestiona puntos y liquidaciones, usuarios y cámaras. El Inversor consulta el dashboard (core de la aplicación), su inversión y las cámaras. Design system Olvidata (Bootstrap 5 + olvidata-theme) extendido con **tema dark/light** seleccionable por usuario.

## 2. Lógica de distribución estándar (todo el sistema)

- **Layout**: sidebar de navegación (gradiente Olvidata) + topbar con selector de período, toggle dark/light y avatar. Contenido en cards (`ov-card`).
- **Pantallas de consulta**: fila de cards KPI arriba → gráficos al medio → tabla de detalle abajo (DataTables dentro de `table-responsive`).
- **Pantallas de carga**: formulario agrupado por secciones colapsables, totales calculados visibles en tiempo real a la derecha/arriba, acciones al pie (Guardar / Cerrar período).
- **Menú por rol**: Inversor ve solo Dashboard, Mi inversión y Cámaras; Admin ve todo.

## 3. Flujo de pantallas y wireframes textuales

### P-01 Login
Card centrada: usuario, contraseña, botón ingresar. Errores con mensaje genérico. Redirección al Dashboard.

### P-02 Dashboard (core — Admin e Inversor)
Selector de mes/año + comparador histórico. Estructura en cards por módulos:
```
[ KPI Ventas Totales ($) ] [ KPI Ventas A (facturadas) ] [ KPI Total Gastos ] [ KPI Resultado ] [ KPI Rentabilidad % ]
[ KPI USD: Ventas | Gastos | Resultado (TC del mes) ]      [ KPI Indicadores: comensales | ticket prom | ítems/ticket | cubierto prom ]
[ Gráfico dona: Salón vs Delivery (VentasSalon / VentasDelivery) ] [ Gráfico dona: composición gastos por rubro ]
[ Gráfico barras+línea: Ventas vs Gastos vs Resultado, 12 meses, selector de año / multi-año ]
[ Gráfico línea: rentabilidad % histórica ]                [ Gráfico línea: Resultado en USD histórico ]
[ Tabla resumen mensual del año (mini estado de resultados) ]
```
- Tema dark/light con toggle persistido por usuario (tokens CSS duplicados en `[data-theme="dark"]`).
- Gráficos con librería JS de charts (una sola librería para todo el sistema).
- **Mes Abierto**: el Dashboard muestra el período abierto con datos parciales. Si falta TC, los valores USD muestran "Pendiente TC". Si faltan rubros, los KPIs muestran el parcial cargado hasta el momento con badge "Parcial".
- Meses sin ningún dato cargado: card en estado vacío ("Sin datos del período"), nunca división por cero.

### P-03 Estado de resultados mensual (Admin — carga)
Cabecera: mes/año + estado del período (Abierto/Cerrado) + TC del mes ([editar TC] abre selector inline, ver abajo).
Secciones colapsables en el orden del Excel:
- **Ventas** (4 inputs + totales calculados en tiempo real):
  ```
  [ Ventas A Salón ]  [ Ventas A Delivery ]  → Ventas A = A Sal + A Del
  [ Ventas B Salón ]  [ Ventas B Delivery ]  → Ventas B = B Sal + B Del
  Ventas Totales = A + B | Ventas Salón = A Sal + B Sal | Ventas Delivery = A Del + B Del
  ```
- CMV → Fee Franquicia (calculado) → Sueldos/CCSS → Gastos Varios → Alquiler → Servicios (comisiones calculadas) → Impuestos (IVA manual + calculados) → Previsión/Reservas (calculado) → Gastos Extras.
Panel fijo de totales: Total Gastos, Resultado, Rentabilidad, equivalentes USD. Botones: **Guardar borrador** / **Cerrar período** (navega a P-08 preview editable).

**Selector de TC inline (nuevo — P-A03)**
Al hacer clic en [editar TC], aparece un panel/modal:
1. Tabla de cotizaciones del día por casa (Oficial compra/venta, Blue compra/venta/promedio, MEP, CCL, Cripto, etc.).
2. Input editable de TC pre-cargado con el **blue promedio del día**.
3. El Admin puede hacer clic en cualquier fila para cargar ese valor en el input.
4. Puede editarlo manualmente.
5. [Aplicar] guarda `PeriodoMensual.TipoCambio` y actualiza los cálculos USD en tiempo real.

### P-04 Estado de resultados anual (Admin e Inversor — consulta)
Tabla tipo Excel: filas = rubros/subgrupos, columnas = 12 meses + total anual. Selector de año. Exportable a Excel.

### P-05 Configuración de catálogos (Admin)
Tabs: Rubros y subgrupos (ABM con baja lógica) · Parámetros porcentuales (concepto, % vigente, base de cálculo A/total, vigencia desde) · Tipo de cambio mensual (grilla año × mes).

### P-06 Indicadores de venta (Admin — carga)
Grilla mensual: **cantidad de comensales**, ticket promedio, ítems por ticket, cubierto promedio. Nota visible: "Fuente: Ayres POS (carga manual)". En el futuro la cantidad de comensales se integrará con la base de datos de Ayres (etapa 2, fuera de alcance actual).

### P-07 Puntos de inversión (Admin)
Vista de los 100 puntos (número, valor de aporte, bonificado sí/no, inversor asignado, vigencia). Card resumen: total recaudado, puntos asignados/disponibles. Asignación con vigencia mensual (historial de cambios visible).

### P-08 Liquidaciones del mes (Admin) — **DOBLE ROL: Preview de cierre + Gestión post-cierre**

**Modo A — Preview antes del cierre** (entrada: botón "Cerrar período" desde P-03):
Cabecera: mes, Resultado del Ejercicio con [ajuste manual + motivo], utilidad por punto calculada, TC del mes. Detalle por inversor: puntos vigentes, bruto calculado, consumos **[input editable]**, neto calculado, USD calculado. Totales al pie. Botones: **[Cancelar]** (vuelve a P-03 sin cambios) / **[Confirmar y cerrar período]** (cierra el período, genera liquidaciones Pendiente, dispara email).

**Modo B — Gestión post-cierre** (entrada: menú lateral, período Cerrado):
Misma estructura de tabla pero con columnas adicionales: estado (Pendiente/Pagada), fecha de pago. Acciones: consumos editables mientras Pendiente, marcar pagada (masivo o individual con fecha), reabrir liquidación individual con motivo (Pagada→Pendiente, solo Admin).

### P-09 Reparto general histórico (Admin)
Réplica de la hoja GENERAL: serie mensual con TC, utilidad por punto, utilidad total, USD, renta mensual, fecha de pago + gráfico de evolución de utilidad por punto.

### P-10 Mi inversión (Inversor)
```
[ Capital aportado USD ] [ Dividendos acumulados USD/$ ] [ Recupero % (progreso) ] [ Renta mensual prom % ]
[ Gráfico línea: dividendos mensuales USD ]  [ Gráfico área: recupero acumulado % ]
[ Tabla historial: mes | puntos | utilidad x pto | total $ | USD | renta % | consumos | fecha de pago ]
```
Solo datos propios; foco UX: es la pantalla con la que el inversor "ve su inversión de manera profesional".

### P-11 Cámaras (Admin e Inversor)
Pantalla dedicada que embebe el web client de Hik-Connect (iframe a pantalla completa dentro del layout) + botón "Abrir en pestaña nueva" como alternativa si el proveedor bloquea el iframe. Estado vacío si el Admin no configuró acceso.

### P-12 Configuración de cámaras (Admin)
Formulario: URL del web client, usuario/cuenta de referencia, notas de acceso, activo sí/no.

### P-13 Usuarios (Admin)
ABM de usuarios: nombre, email, rol (Inversor), vínculo a ficha de inversor, activo, blanqueo de contraseña.

### P-14 Notificaciones de cierre (Admin)
Tabs: **Configuración** (casilla/servidor SMTP emisor, nombre remitente, botón "Enviar correo de prueba") · **Historial de envíos** (por período: inversor, email, fecha/hora, estado Enviado/Fallido, acción Reenviar).
**Plantilla del correo** (HTML, branding KOI): resumen del mes — ventas, resultado del ejercicio, rentabilidad, utilidad por punto — + bloque personalizado con la liquidación del inversor (puntos, bruto, consumos, neto, USD) + botón "Ver resumen completo en la web" (link al sistema). Al cerrar el período (P-03/P-08) el sistema dispara el envío a todos los inversores activos y muestra el resultado; si el período se reabre y vuelve a cerrarse, pide confirmación antes de reenviar.

## 4. ViewModels propuestos (campos y validaciones funcionales)

| ViewModel | Campos principales | Validaciones |
|---|---|---|
| LoginVM | Usuario, Password | requeridos |
| DashboardVM | Período, KPIs (VentasA/VentasB/VentasTotales/VentasSalon/VentasDelivery, gastos, resultado, rentabilidad, USD), series históricas, indicadores, `EsParcial` (flag) | solo lectura; mes abierto → `EsParcial=true`; períodos sin datos → vacío controlado |
| EstadoResultadosEdicionVM | Período, Estado, TC, **VentasASalon, VentasBSalon, VentasADelivery, VentasBDelivery** (+ agregados calculados), lista RubroVM { Subgrupo, ImporteManual / %Calculado, Total } | importes ≥ 0; TC > 0 para cerrar; calculados no editables |
| EstadoResultadosAnualVM | Año, matriz rubro × mes, totales | solo lectura |
| ParametroPorcentajeVM | Concepto, Porcentaje, BaseCálculo (VentasA/VentasTotales), VigenciaDesde | 0–100 %, base requerida |
| TipoCambioVM | Año, Mes, Valor, **CotizacionesDelDia** (lista por casa: nombre/compra/venta/promedio/esAproximada) | Valor > 0, único por mes/año; cotizaciones son solo lectura, informativas |
| IndicadoresVentaVM | Período, **CantidadComensales**, TicketPromedio, ItemsPorTicket, CubiertoPromedio | ≥ 0 |
| LiquidacionPreviewVM | Período, ResultadoEjercicio, MotivoAjuste, UtilidadPorPunto, lista { InversorId, Nombre, Puntos, Bruto, Consumos, Neto, USD } | consumos ≥ 0; consumos ≤ bruto (bloqueante) |
| PuntoInversionVM | Número (1–100), ValorAporte, Bonificado, InversorAsignado, VigenciaDesde | número único; Σ puntos vigentes ≤ 100 |
| LiquidacionMesVM | Período, UtilidadPorPunto, lista LiquidacionInversorVM { Inversor, Puntos, Bruto, Consumos, Neto, USD, Renta %, Estado, FechaPago } | consumos ≤ bruto; pagada inmutable |
| MiInversionVM | Capital, DividendosAcum ($/USD), Recupero %, RentaProm %, historial mensual | solo datos del inversor autenticado |
| CamaraConfigVM | UrlWebClient, CuentaReferencia, Notas, Activo | URL válida |
| NotificacionConfigVM | ServidorSmtp, Puerto, CasillaEmisora, NombreRemitente, Credencial | requeridos; prueba de envío antes de guardar |
| NotificacionEnvioVM | Período, Inversor, Email, FechaHora, Estado (Enviado/Fallido), DetalleError | solo lectura + acción Reenviar |
| UsuarioVM | Nombre, Email, Rol, InversorVinculado, Activo | email único; inversor requerido para rol Inversor |

## 5. Máquina de estados

**Período mensual** _(estado Reabierto eliminado — P-A04)_

| Estado origen | Evento | Estado destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| Abierto | Cerrar período (desde P-08 preview) | Cerrado | Ventas, TC y rubros obligatorios cargados; consumos confirmados en preview | Calcula totales finales, genera liquidaciones Pendientes, **envía notificación por correo a inversores activos** (fallos no bloquean el cierre) | "Faltan datos obligatorios para cerrar" |

> ❌ **Estado "Reabierto" eliminado.** Un error post-cierre es gestionado operativamente por Admin + SuperUsuario fuera del sistema (P-A04 confirmado).

**Liquidación por inversor**

| Estado origen | Evento | Estado destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| Pendiente | Marcar pagada | Pagada | Fecha de pago informada | Registra fecha; congela montos | "Falta fecha de pago" |
| Pagada | Reabrir | Pendiente | Solo Admin + motivo | Registra motivo en auditoría | "Requiere motivo" |

## 6. Reglas de negocio y permisos por pantalla

| Pantalla | Admin | Inversor | Reglas clave |
|---|---|---|---|
| P-02 Dashboard | ✔ | ✔ | Mes abierto con datos parciales (badge "Parcial", TC pendiente → sin USD); meses sin datos → vacío controlado; nueva torta Salón/Delivery |
| P-03/P-04 Estado resultados | ✔ | P-04 solo lectura | 4 campos de ventas (ASalon/BSalon/ADelivery/BDelivery); bases porcentuales: comisiones/IIBB/débitos/tasa sobre **VentasA**; regalías/canon/previsiones sobre **VentasTotales** |
| P-05 Configuración | ✔ | ✘ | Cambios de % rigen desde vigencia, sin recalcular meses cerrados |
| P-06 Indicadores | ✔ | ✘ (los ve en P-02) | — |
| P-07 Puntos | ✔ | ✘ | Σ vigente ≤ 100; bonificados con aporte 0 participan del reparto |
| P-08 Liquidaciones | ✔ | ✘ | Utilidad por punto = Resultado/100; neto = bruto − consumos |
| P-09 Reparto general | ✔ | ✘ | Serie histórica completa |
| P-10 Mi inversión | ✔ (de todos, vía P-08/P-09) | ✔ (solo propia) | Aislamiento estricto por inversor |
| P-11 Cámaras | ✔ | ✔ | Visible solo con configuración activa |
| P-12/P-13 Config cámaras / Usuarios | ✔ | ✘ | — |
| P-14 Notificaciones de cierre | ✔ | ✘ (recibe el correo) | Envío automático al cerrar; fallo no bloquea cierre; re-cierre pide confirmación para reenviar |

## 7. Impacto funcional por capa

- **Presentación**: 13 pantallas; layout Olvidata extendido con theme switcher dark/light (tokens CSS); librería de charts única; DataTables para detalles; export a Excel en P-04.
- **Negocio**: servicios de cálculo del estado de resultados (bases A/total parametrizadas), cierre de período y generación de liquidaciones, cálculo de recupero/renta, validación de puntos.
- **Datos**: períodos, ventas, movimientos de gasto por subgrupo, catálogos, parámetros con vigencia, TC, indicadores, puntos y asignaciones con vigencia, liquidaciones y consumos, configuración de cámaras, usuarios.

## 8. Riesgos y supuestos (del diseño)

- El theme dark/light se resuelve con doble set de tokens CSS sobre olvidata-theme (sin duplicar vistas); riesgo bajo.
- El iframe de Hik-Connect puede ser degradado por Hikvision a "abrir en pestaña nueva": la pantalla ya prevé ambas variantes.
- La grilla anual (P-04) es la vista más densa: se diseña solo lectura para no replicar la complejidad de edición del Excel.

## 9. Plan funcional por etapas (para el arquitecto)

1. Base: autenticación, roles, layout con dark/light, gestión de usuarios.
2. Configuración: rubros/subgrupos, parámetros %, TC.
3. Estado de resultados: carga mensual + cálculo + vista anual + cierre de período.
4. Indicadores de venta.
5. Dashboard core (cards + gráficos + histórico).
6. Inversiones: puntos, liquidaciones, reparto general, Mi inversión.
7. Cámaras: configuración + visualización embebida.
8. Notificación de cierre por correo (config SMTP, plantilla, envío y registro).
9. Carga inicial de históricos 2024–2026.

---

## 10. Diseño funcional — Módulo E2-02 "Fichador de empleados" (P-15)

### 10.0 Escaneo de reutilización cross-proyecto (obligatorio antes de diseñar)

Se escanearon `docs/*/definiciones/{2-disenador-funcional,5-implementador}.md` de todos los proyectos del historial (grep por "fichador", "asistencia", "Bearer", "HttpClient tipado", "integracion webhook", "IHttpClientFactory") — **sin coincidencias**. Ningún proyecto del estudio tiene todavía una pantalla de consulta de fichadas/asistencia ni un cliente HTTP tipado con Bearer token estático contra un SaaS externo de solo lectura. Se diseña desde cero. **Este módulo queda documentado como el primer patrón de "integración REST de solo lectura con Bearer token estático" del estudio — candidato directo a reutilizar en E2-01 (Ayres, si se resuelve por API REST) y en cualquier proyecto futuro que integre un sistema de fichaje.**

### 10.1 Pantalla P-15 — Fichador (Admin, solo lectura)

Layout estándar: sidebar (nuevo link "Fichador" en sección "Gestión", solo visible para rol Administrador) + topbar. Dos tabs dentro de la misma pantalla:

```
Tab "Hoy"                                  Tab "Rango de fechas"
┌──────────────────────────────┐           ┌──────────────────────────────────────┐
│ Empleado  Entrada  Salida     │           │ [ Empleado: Todos ▾ ] [ Rango fechas ] │
│ García     08:02    17:05     │           │                                        │
│ López      08:15   Turno abierto│         │ Empleado   Horas trabajadas  Fichadas  │
│ Pérez    Sin fichada hoy      │           │ García        168.5 h          22      │
└──────────────────────────────┘           │ López         (turno incompleto: 2)    │
                                            └──────────────────────────────────────┘
```

Tab adicional "Empleados": DataTable de solo lectura con nombre, estado (Activo/Inactivo en QuickPass), última fichada registrada.

### 10.2 ViewModels propuestos

| ViewModel | Campos principales | Validaciones |
|---|---|---|
| `FichadorHoyVM` | Lista `{ EmpleadoNombre, Entrada?, Salida?, Estado (Completo/TurnoAbierto/SinFichadaHoy) }` | solo lectura |
| `FichadorRangoVM` | `EmpleadoId? (filtro, null = todos)`, `FechaDesde`, `FechaHasta`, lista `{ EmpleadoNombre, HorasTrabajadas, CantidadFichadas, TurnosIncompletos }` | `FechaDesde <= FechaHasta`; rango obligatorio vía `daterangepicker` (estándar del proyecto, prohibido `<input type="date">` suelto) |
| `FichadorEmpleadoVM` | `Nombre, EstadoQuickPass (Activo/Inactivo), UltimaFichada?` | solo lectura |

### 10.3 Reglas de validación y mensajes

- Si `IQuickPassService` devuelve error/timeout: SweetAlert2 con mensaje "No se pudo conectar con el sistema de fichadas. Intentá nuevamente en unos minutos." — nunca una pantalla en blanco ni una excepción visible.
- Fichada con entrada sin salida: badge `bg-warning` "Turno abierto", no se sombra como error.
- Empleado sin fichadas en el rango: fila con 0 h y badge `bg-secondary` "Sin fichadas en el período" (no se oculta la fila).

### 10.4 Impacto por capa

- **Presentación**: `FichadorController` (Admin-only vía policy `RequireAdministracion`, ver §10.5 de arquitectura), 1 vista con 3 tabs (Hoy / Rango / Empleados), `daterangepicker` para el filtro de rango, DataTable client-side para los 3 listados (volumen bajo, sin necesidad de server-side).
- **Negocio**: `IQuickPassService` (nuevo) con `ObtenerFichadasHoyAsync()`, `ObtenerResumenPorRangoAsync(desde, hasta, empleadoId?)`, `ObtenerEmpleadosAsync()`. Cálculo de horas trabajadas y detección de turno incompleto vive en el service, no en el Controller ni en la vista.
- **Datos**: ninguna (sin nuevas tablas — ver decisión de Análisis §11.4).

### 10.5 Historias de usuario

**HU-1** — Como Administrador, quiero ver quién fichó entrada/salida hoy para controlar la asistencia del día sin salir del sistema web.
- Criterio: la pantalla muestra todos los empleados activos con su estado de fichada de hoy (Completo / Turno abierto / Sin fichada hoy), actualizado en cada carga de la pantalla.

**HU-2** — Como Administrador, quiero consultar las horas trabajadas de un empleado (o de todos) en un rango de fechas para revisar presentismo antes de liquidar sueldos.
- Criterio: al elegir un rango con `daterangepicker` y opcionalmente un empleado, veo el total de horas trabajadas y la cantidad de fichadas por empleado; los turnos incompletos se listan aparte, nunca se computan como 0 silenciosamente.

**HU-3** — Como Administrador, quiero ver el listado de empleados registrados en el sistema de fichaje para saber quién está activo en el dispositivo biométrico.
- Criterio: veo nombre, estado (activo/inactivo) y última fichada de cada empleado, igual a lo configurado en el panel de QuickPass en ese momento.

**HU-4** — Como Administrador, si el sistema de fichaje no responde, quiero un mensaje claro en vez de un error críptico, para saber que el problema es externo y no del sistema web.
- Criterio: cualquier falla de `IQuickPassService` (timeout, token inválido, 5xx) se traduce a un SweetAlert2 legible; el error real queda en el log (Serilog) sin exponer el token.

### 10.6 Riesgos de implementación

- Sin documentación formal de endpoints (Swagger no confirmado) — el mapeo exacto de campos puede requerir ajuste una vez que llegue el token real y se pueda probar contra la API viva.
- Cálculo de "horas trabajadas" asume pares entrada/salida simples (sin múltiples fichadas intermedias tipo pausa-almuerzo) — a confirmar contra el comportamiento real del hardware ZKTeco MB360 una vez que haya acceso.

---

## 11. Diseño — Sprint UX/UI Inversor + fixes (Agosto 2026)

### 11.0 Escaneo de reutilización

No aplica escaneo cross-proyecto: los 9 ítems son ajustes/relabels/simplificaciones sobre pantallas y servicios que ya existen en el propio KOI (Dashboard, Mi Inversión, Reparto General, Vista Anual ER, sistema de notificaciones in-app) — se reutiliza 100% el código propio del proyecto, no hay pantalla nueva que justifique buscar un patrón en otro proyecto del estudio, salvo el composer de notificaciones (ítem 7), que tampoco tiene equivalente en otros proyectos (grep de `INotificationService`/notificaciones por rol sin resultados fuera de KOI).

### 11.1 Pantalla nueva "Mes actual" (P-16, solo Inversor)

Reemplaza, solo para el rol Inversor, el link "Dashboard" del sidebar. Layout mínimo, sin selector:

```
Rendimiento Agosto 2026

[ Ventas Totales ]  [ Ticket Promedio ]  [ Cant. de Tickets ]

[ Torta % venta por canal: Mostrador / Salón / Delivery ]
```

- Controller/acción nueva (ej. `DashboardController.Actual()` o `MesActualController`, a criterio del arquitecto) que calcula año/mes = `DateTime.Now` (huso Argentina, mismo patrón que `CotizacionService.HoyArgentina()` usado en Fichador), reutiliza el mismo `IIndicadoresService`/`IDashboardService` ya usado por el Dashboard actual (no se duplica lógica de cálculo, solo se proyecta un subconjunto de campos).
- Sin filtro de período en la UI — a diferencia de toda otra pantalla de carga/consulta del sistema, es intencional (KPI del momento, no histórico).
- Si el mes actual no tiene datos cargados todavía: mismo criterio que el Dashboard hoy (estado vacío controlado, nunca división por cero).

### 11.2 "Dashboard Histórico" (relabel condicional, sin pantalla nueva)

No hay diseño de pantalla nuevo: es el mismo `Views/Dashboard/Index.cshtml` de siempre, con su filtro de mes/año y sus 3 secciones (Ventas/Gastos/Evolución Histórica) intactas. El único cambio de diseño es el **texto del link del sidebar**, condicional por rol:
- Administrador / SuperUsuario → "Dashboard"
- Inversor → "Dashboard Histórico"

### 11.3 Rol "Encargado" — impacto en sidebar

Nueva condición en `_Layout.cshtml` (mismo mecanismo `User.IsInRole` ya usado en todo el archivo): si el usuario autenticado tiene el rol "Encargado", el sidebar muestra ÚNICAMENTE el link "Fichador" (ningún otro bloque de menú — ni Dashboard, ni Inversiones, ni Configuración). Es el primer rol del sistema con un sidebar reducido a un solo ítem; no reutiliza ninguno de los bloques condicionales existentes, es un bloque nuevo con su propia condición al principio del sidebar.

### 11.4 Fix de datos de Puntos (Wang) — sin diseño de pantalla

No hay cambio de pantalla: `Views/Puntos/Index.cshtml` sigue exactamente igual. El fix es interno a `InversionesService.AsignacionesVigentesQuery` (ver Arquitectura §9.2) — el resultado visible es que el total y el listado que ya existen hoy muestran el valor correcto.

### 11.5 Reparto General — tabla simplificada

`Views/RepartoGeneral/Index.cshtml`, tabla `#tablaReparto`: se elimina el `@foreach (var inv in Model.NombresInversores)` que genera una columna por inversor. Columnas finales: Período, Ventas, Resultado, Utilidad/Punto, Utilidad/Punto USD, Estado. El `RepartoGeneralViewModel`/`NombresInversores` deja de ser necesario para esta vista (a evaluar en Arquitectura si se elimina del ViewModel o solo se deja de usar en la vista).

### 11.6 "Historial de Resultados" (rename)

- `Views/EstadoResultados/Anual.cshtml:4` — `ViewData["Title"] = "Historial de Resultados " + Model.Anio;` (antes `"Estado de Resultados " + Model.Anio`).
- `Views/EstadoResultados/Anual.cshtml:10` — `<h3>...Historial de Resultados @Model.Anio</h3>` (antes "Estado de Resultados").
- `Views/Shared/_Layout.cshtml:129-133` y `:181-185` — texto del link "Vista Anual ER" → "Historial de Resultados" (dos lugares en el archivo, uno por bloque de rol, mismo texto en ambos).

### 11.7 Notificaciones — pantalla de composición nueva (P-17)

Nueva pantalla, acceso desde un link persistente "Notificaciones" en el sidebar (además de la campanita ya existente). Reutiliza `NotificationsController` (se le agregan acciones) o un controller nuevo `NotificacionesAdminController` — a definir en Arquitectura.

```
Crear notificación
┌──────────────────────────────────────────────┐
│ Asunto: [_______________________________]     │
│ Mensaje: [______________________________]     │
│                                                │
│ Destinatarios                                 │
│  Rol: [ Administrador ▾ ]  → carga automática │
│  ┌────────────────────────────────────────┐   │
│  │ ☒ Juan Pérez            [quitar]        │   │
│  │ ☒ María López           [quitar]        │   │
│  │ ☒ ...                   [quitar]        │   │
│  └────────────────────────────────────────┘   │
│                                                │
│ Canal: [ ] Enviar por correo                  │
│        [ ] Crear notificación in-app          │
│                                                │
│              [Cancelar]  [Enviar]              │
└──────────────────────────────────────────────┘
```

- Al elegir un rol del combo, AJAX (`GET`, antiforgery no aplica a GET) trae los usuarios activos con ese rol y los precarga como chips/filas con botón "quitar" — el admin puede sacar puntualmente a alguno antes de enviar (nunca agregar usuarios de otro rol desde acá — el combo es la única fuente de candidatos, por diseño, para mantener la UI simple).
- Al menos un canal (correo o in-app) debe estar tildado — validación bloqueante si ninguno lo está.
- Confirmación de envío vía SweetAlert2 (patrón `btn-swal-confirm` del proyecto), resumen post-envío: "Notificación enviada a N usuarios" (+ detalle de fallos de email si los hubo, sin bloquear los que sí se enviaron — mismo criterio que `NotificacionCierre`: un fallo de un destinatario no aborta el resto).
- ViewModel: `ComponerNotificacionViewModel { Asunto, Mensaje, RolId, List<UsuarioSeleccionadoViewModel> Destinatarios, bool EnviarPorCorreo, bool CrearInApp }`.

### 11.8 Mi Inversión — tabla de historial reformateada

`Views/MiInversion/Index.cshtml`, tabla `#tablaHistorial` (markup actual en líneas 113-174 del archivo):

**Antes** (10 columnas): Período | Puntos | Bruto | Consumos | Neto $ | Neto U$D | TC | Renta | Estado | Fecha pago

**Después** (9 columnas, sin Puntos ni TC, Período dividido):
Año | Mes | Bruto | Consumos | Neto $ | Neto U$D | Renta | Estado | Fecha pago

- Año/Mes: el DTO `MiInversionFilaDto` ya expone `Anio`/`Mes` como `int` — se renderizan directo, no hace falta tocar Application/Infrastructure.
- Mes en palabras, capitalizado (ej. "Agosto") — agregar un helper de nombre de mes en español si no existe uno ya expuesto al nivel de vista (`InversionesService` ya tiene un `NombreMes(anio, mes)` privado que arma "Agosto 2026"; para la vista hace falta solo la palabra del mes, sin el año — extraer o exponer una variante).
- DataTable: `ordering: false` (global, no por columna — se saca la interacción de click-para-ordenar en toda la tabla, no solo se fija un orden). El orden real (Año desc, Mes desc) se resuelve en el `Select`/`OrderBy` del lado del servidor al armar `Historial`, no en el cliente — la tabla ya llega pre-ordenada.

### 11.9 Fix global — importes sin salto de línea

Regla CSS nueva en `wwwroot/css/olvidata-theme.css` (design system compartido, no una vista puntual): las celdas de tabla que muestran un importe (`$`/`U$D` + número) deben tener `white-space: nowrap`. Aplicar sobre un selector reutilizable en todo el sistema — ej. clase `.ov-monto` a agregar en cada `<td>` de importe (patrón explícito, no un selector genérico por posición de columna, para no romper columnas de texto largo que sí deben poder wrappear). Alcance: todas las vistas con importes (`Dashboard`, `MiInversion`, `RepartoGeneral`, `EstadoResultados`, `Liquidaciones`, `Puntos`, `Fichador` si aplica). Ver Arquitectura §9.6 para la regla a documentar en Agentes-IA.

---

## 12. Diseño — Mi Inversión: dividendos y recupero en pesos (Agosto 2026)

### 12.0 Escaneo de reutilización

Sin match — es un cálculo puntual sobre datos ya existentes de KOI, no hay pantalla ni patrón equivalente en otro proyecto.

### 12.1 Cards de KPI — reorganización

`Views/MiInversion/Index.cshtml`, sección de cards (hoy: Capital aportado, Dividendos cobrados [USD], Recupero % [USD] con barra de progreso). Se agrega una segunda fila de cards, misma jerarquía visual pero con acento visual distinto (ej. badge "$"/"USD" en el título de cada card para diferenciar moneda de un vistazo):

```
[ Capital aportado USD ]  [ Dividendos cobrados U$D ]  [ Recupero U$D % + barra ]
[ Dividendos cobrados $ ]  [ Recupero $ % ]
```

- La fila nueva NO duplica la barra de progreso (queda como número simple + badge de color, sin repetir el hito visual 25/50/75/100% que ya tiene la fila USD) — evita saturar la pantalla con dos barras que van a mostrar valores casi iguales (aclarado en Análisis §13.2).
- Sin cambios en la tabla de historial (ítem 8/9 del sprint anterior) — los KPIs nuevos son solo del resumen superior, no tocan `#tablaHistorial`.

### 12.2 ViewModel/DTO

`MiInversionDto` (Application) agrega dos campos: `DividendosPesos` (decimal) y `RecuperoPesosPorc` (decimal?) — mismo patrón que los campos USD ya existentes, calculados en el service, sin tocar el historial por fila.

---

## 13. Diseño — Sprint de correcciones y catálogo real (Agosto 2026)

### 13.1 Mi Inversión — recupero acumulado + gráfico (ítem 2)

Tabla `#tablaHistorial`: se agrega **una** columna nueva, "Recupero acum.", después de la columna "Renta" existente.
- No se agrega una columna "Recupero del mes": la columna "Renta" ya ES ese número (`NetoUsd ÷ Capital × 100` con el TC del mes cerrado). Duplicarla con otro nombre confundiría. Se evalúa cambiarle el tooltip/encabezado a "Renta (recupero del mes)" para que la relación quede explícita sin duplicar dato.
- El acumulado se calcula cronológicamente ascendente (del mes más viejo al más nuevo) y se muestra en la tabla que está ordenada descendente — la primera fila (mes más reciente) muestra el acumulado total, que debe coincidir con el KPI de Recupero de arriba.

Gráfico nuevo (Chart.js, ya usado en Dashboard) entre las cards de KPI y la tabla de historial:
```
[ Evolución del recupero ]
 100% ─────────────────────────── (línea de meta)
      ╱
   ╱        línea de recupero acumulado %, un punto por mes cerrado
 0% ─────────────────────────────
      ene  feb  mar  abr  may ...
```
- Línea de meta al 100% (punteada) para que se lea de un vistazo cuánto falta para recuperar el capital.
- Eje X: períodos en orden cronológico ascendente (al revés que la tabla, que va del más nuevo al más viejo — es lo natural en un gráfico de evolución).

### 13.2 Editar meses cerrados (ítem 3)

Pantalla `Views/EstadoResultados/Mensual.cshtml`, período con estado Cerrado:
- Hoy los inputs/botones de edición existen igual pero el guardado falla con "El periodo esta cerrado". Ahora el guardado funciona, y se agrega contexto visual:
  - Banner de advertencia permanente arriba: *"Este período está cerrado. Si modificás un valor, se van a recalcular las liquidaciones pendientes de este mes. Las liquidaciones ya pagadas no se modifican."*
  - Confirmación SweetAlert2 antes de guardar cualquier cambio en un período cerrado (no en uno abierto — ahí el flujo sigue igual, sin fricción extra).
  - Después de guardar: mensaje de resultado que informe cuántas liquidaciones se recalcularon y cuántas se dejaron intactas por estar pagadas, con el detalle de los inversores afectados.

### 13.3 Catálogo de rubros (ítem 4)

Sin cambios de pantalla — `Views/Configuracion/Rubros.cshtml` y `Subgrupos.cshtml` ya soportan el ABM. El cambio es de **datos**: el catálogo nuevo se carga por script/seed, no a mano.
- La pantalla de carga del estado de resultados va a mostrar naturalmente la estructura nueva (se arma desde el catálogo).
- Nota de diseño: "Alquiler" no tiene subgrupos en el PDF (es un importe directo del rubro). El modelo actual exige que todo importe cuelgue de un subgrupo → se crea un subgrupo único "Alquiler" dentro del rubro "Alquiler" para no romper el modelo, y la pantalla lo muestra como una sola línea (visualmente equivalente al PDF).

### 13.4 Importación de Excel recurrente (ítem 5)

`Views/ImportacionInicial/Index.cshtml`:
- La pantalla pasa a llamarse **"Importación desde Excel"** (hoy "Importación histórica") — ya no es una operación de única vez.
- Se agrega un check explícito: **"Actualizar los períodos que ya existan"** (por defecto desactivado, o sea el comportamiento actual de omitir). Con el check activado, un período ya cargado se actualiza en vez de omitirse.
- El resultado de la importación debe distinguir tres estados por fila, no dos: *importado nuevo* / *actualizado* / *omitido*.
- Advertencia visible cuando se activa el modo actualizar y hay períodos cerrados en el archivo — misma lógica de recálculo de liquidaciones que el ítem 3.

### 13.5 Reparto General — orden (ítem 6)

`Views/RepartoGeneral/Index.cshtml`, tabla `#tablaReparto`: `data-order="@($"{f.Anio}{f.Mes:D2}")"` en la celda de período (el DTO `RepartoFilaDto` ya expone `Anio`/`Mes`), `order: [[0,'desc']]` y `columnDefs: [{ type:'num', targets:0 }]`. El texto visible del período no cambia. Idéntico al fix ya aplicado en Historial de Resultados.

---

## 14. Diseño funcional — Módulo E2-01 "Integración Ayres POS" (Fase 6, Septiembre 2026)

Entrada: `1-analista-funcional.md` §15 (Discovery + Análisis aprobados, R-A01 resuelto en §15.10). Decisión del dueño del estudio en el gate: **P-A10 = reemplazar siempre**, con preview y confirmación previa.

### 14.0 Escaneo de reutilización (obligatorio)

Se escanearon `docs/patrones/catalogo.yml` y los `2-disenador-funcional.md` / `5-implementador.md` de los 20+ proyectos del historial. **Tres coincidencias reales, las tres se reutilizan:**

| Origen | Qué se toma | Decisión |
|---|---|---|
| **marihogar** — `MariHogar.Infrastructure/Services/AfipTokenCache.cs` (PAT-006) | Cache de token con vencimiento: Singleton + `SemaphoreSlim` para que dos requests concurrentes no disparen dos logins, doble chequeo dentro del lock, **vigencia tomada de la que informa el servidor y no de un valor fijo asumido**, margen de seguridad previo al vencimiento, e `Invalidar()` para forzar re-login cuando el server rechaza un token que localmente creíamos vigente. | **Reutilizar adaptando.** Es exactamente el problema de Ayres (`aliveTime: 3599`). Se adapta de `(Token, Sign)` de AFIP a un único `tokenAccess`. |
| **KOI mismo** — `QuickPassService` + `QuickPassSettings` + `QuickPassIndisponibleException` (Etapa 12) | Convenciones internas ya establecidas para una API externa: cliente nombrado vía `IHttpClientFactory`, POCO de settings al estilo `SmtpSettings`, excepción de dominio propia para "el tercero no responde", y datos en vivo sin persistencia local. | **Reutilizar la estructura tal cual**, renombrando. Da consistencia dentro del proyecto y evita inventar un segundo estilo de integración. |
| **PAT-012** — Importación con preview → confirmar | Separar *analizar* de *persistir* en una sola función con flag, y no pisar lo que el usuario administra a mano sin avisarlo. KOI ya es implementación de referencia del patrón (`ImportacionInicial`). | **Reutilizar el flujo de dos pasos**, sin el staging en disco: acá no hay archivo que guardar, se vuelve a consultar la API al confirmar. |

**No se reutiliza** el chunking de QuickPass: aquel parte por 31 días y sobre un endpoint distinto; acá el límite es 10 días y la agregación es propia. Se escribe nuevo, pero siguiendo el mismo estilo.

### 14.1 Flujo de pantalla

Se suma a **P-03 Estado de Resultados mensual**, sin pantalla nueva.

1. En la tarjeta "Ventas del mes", junto a los campos actuales, botón **"Traer de Ayres"** (`btn-outline-primary`, ícono `fa-cloud-arrow-down`). Visible **solo** si: rol Administrador o SuperUsuario, **período abierto**, y el módulo está configurado.
2. Al pulsarlo: el botón pasa a estado ocupado ("Consultando Ayres…") y se dispara la consulta del mes completo. **No se escribe nada todavía.**
3. Se abre un **modal de preview** con lo que Ayres devolvió, comparado contra lo que hay cargado:

   | Concepto | En el sistema | En Ayres | |
   |---|---|---|---|
   | Ventas Salón | 54.837.560,00 | 52.404.760,00 | ▼ |
   | Ventas Pedidos | 8.293.549,00 | 8.293.849,00 | ▲ |
   | Ventas Mostrador | 100,00 | 2.432.500,00 | ▲ |
   | Comensales | 1.678 | 1.735 | ▲ |
   | Cantidad de ventas | 2.000 | 1.062 | ▼ |
   | **Total** | **63.131.209,00** | **63.131.109,00** | ▼ |

   Las filas que cambian se resaltan; las iguales se muestran en gris. Pie del modal: "Se consultaron N ventas entre el 01/09 y el 30/09".
4. Botones: **"Aplicar"** (escribe y recalcula) y **"Cancelar"** (no toca nada).
5. Al aplicar: se guardan las ventas por el mismo camino que el guardado manual —o sea que **los conceptos porcentuales se recalculan solos**— y la pantalla se refresca sin recargar, con el mismo repintado que ya usa "Guardar ventas".

**Decisión de diseño:** al confirmar se **vuelve a consultar la API**, no se guarda el resultado del preview en sesión. Es una llamada más, pero evita aplicar números viejos si el preview quedó abierto un rato, y elimina el staging. Si el segundo resultado difiere del previsualizado, se avisa y se pide confirmar de nuevo.

### 14.2 Reglas de validación y mensajes

| Situación | Comportamiento |
|---|---|
| Período cerrado | El botón no se renderiza. El endpoint igual lo valida y responde "El período está cerrado." (defensa en profundidad, mismo criterio que el resto de P-03) |
| Rol distinto de Admin/SuperUsuario | Botón oculto + policy `SoloAdministrador` en el endpoint |
| Ayres no responde / puerto bloqueado / DNS | `AyresIndisponibleException` → SweetAlert2: "No se pudo conectar con Ayres. El período quedó sin cambios." **Nunca se escribe parcialmente** |
| Credenciales rechazadas (`UNAUTHORIZED_ACCESS`) | "Ayres rechazó las credenciales. Revisá la configuración." — mensaje distinto del anterior: es un problema de configuración, no de red |
| El mes no tiene ventas en Ayres | Preview informativo: "Ayres no devolvió ventas para este período." Sin botón Aplicar |
| El token vence a mitad del chunking | Se renueva y se continúa. **Invisible para el usuario** |
| Un chunk falla después de que otros salieron bien | Se aborta todo y no se aplica nada. La agregación es en memoria, así que no queda estado a medias |
| Mes en curso (incompleto) | Se permite, con leyenda: "El mes todavía no terminó: el total es parcial." |

### 14.3 ViewModels y contratos

**Application** — `DTOs/AyresDtos.cs`:
- `VentasPeriodoAyresDto`: `Anio`, `Mes`, `FechaDesde`, `FechaHasta`, `CantidadVentas`, `ImporteTotal`, `Comensales`, `ItemsTotales`, `VentasPorCanal` (`Dictionary<string,decimal>`), `TicketPromedio`, `VentaPorCubierto`, `ItemsPorVenta`, `VentasPorDia`.
- `PreviewVentasAyresDto`: `Actual` (lo cargado) + `Nuevo` (lo de Ayres) + `HayDiferencias`.

**Application** — `Interfaces/IAyresService.cs`:
- `Task<VentasPeriodoAyresDto> ObtenerVentasPeriodoAsync(int anio, int mes, CancellationToken ct)`
- `Task<bool> ProbarConexionAsync(CancellationToken ct)` (reemplaza el diagnóstico temporal `System/DiagnosticoAyres`, que se elimina)

**Web** — `Models/EstadoResultadosViewModels.cs`: `ErMensualViewModel.AyresHabilitado` (bool, para renderizar o no el botón).

**Web** — `EstadoResultadosController`:
- `[HttpPost] PreviewAyres(int anio, int mes)` → JSON con el comparativo. **No escribe.**
- `[HttpPost] AplicarAyres(int anio, int mes)` → reconsulta, escribe vía `GuardarVentasAsync` y devuelve el ER recalculado, con la misma forma que ya devuelve `GuardarVentas` (para reusar el repintado del cliente).

Ambos con `[ValidateAntiForgeryToken]` y policy `SoloAdministrador`.

**Mapeo de canales** (P-A08 ✅ **confirmado 2026-09-08**): `ME` → Salón, `PE` → Pedidos, `MO` → Mostrador. **Se diseña configurable**, no hardcodeado: si aparece un `sectorTipo` desconocido, su importe se suma a un canal "Otros" y **se muestra en el preview con una advertencia**, en vez de descartarlo en silencio o romper.

### 14.4 Impacto por capa

| Capa | Cambio |
|---|---|
| **Domain** | **Ninguno.** Sin entidades nuevas, sin migración: las ventas se escriben en `VentasMensuales`, que ya existe |
| **Application** | `DTOs/AyresDtos.cs`, `Interfaces/IAyresService.cs`, `Exceptions/AyresIndisponibleException.cs` |
| **Infrastructure** | `Services/AyresService.cs`, `Services/AyresSettings.cs`, `Services/AyresTokenCache.cs` (adaptado de marihogar), registro del cliente nombrado en `DependencyInjection.cs` |
| **Web** | 2 acciones en `EstadoResultadosController`, botón + modal en `Views/EstadoResultados/Mensual.cshtml`, flag en el ViewModel. **Se elimina** `System/DiagnosticoAyres` |
| **Config** | Sección `Ayres` ya cargada en `appsettings.Production.json` (gitignoreado). Falta la sección espejo **vacía** en el `appsettings.json` versionado, como se hizo con QuickPass |

### 14.5 Riesgos de implementación

- **El token vive 1 hora y un mes son 4 llamadas.** En la práctica no vence a mitad, pero el cache debe manejarlo igual: es el caso que el patrón de marihogar ya resuelve y no hay que reinventar.
- **`AyresTokenCache` debe ser Singleton** y `AyresService` Scoped. Registrarlos al revés hace que el token se pierda entre requests y se loguee de más — es el error clásico de este patrón.
- **No cargar el mes entero en memoria**: 1.062 ventas con sus `items[]`. Agregar por chunk y descartar el detalle.
- **Fechas asimétricas**: se consulta `yyyy-MM-dd` y vuelve `dd/MM/yyyy`. Parsear con `CultureInfo.InvariantCulture` y formato explícito, nunca con el parseo por cultura del server.
- **El sobre viene anidado** (`content.ventas[i].venta.*`): un DTO mal mapeado da cero sin error.
- **D-A01**: la regla de firewall apunta a la IP fija `190.245.226.181`. Si Ayres migra, la integración se corta con WSAEACCES. El mensaje de error de red debe ser lo bastante explícito como para que ese diagnóstico no lleve otra vez dos horas.
- **`estado` de la venta (R-A04)**: verificar en implementación si hay ventas anuladas que no deban sumar. En agosto el total cerró al centavo, así que probablemente no las haya, pero no está probado.

### 14.6 Historias de usuario

- **HU-A01** — Como Administrador, quiero traer las ventas del mes desde Ayres para no cargarlas a mano.
  - CA: con el período abierto veo el botón "Traer de Ayres"; al pulsarlo obtengo un preview; **nada se escribe hasta que confirmo**.
- **HU-A02** — Como Administrador, quiero ver qué va a cambiar antes de aplicar, para no pisar datos sin darme cuenta.
  - CA: el modal muestra lado a lado lo cargado y lo de Ayres, resalta solo las filas que difieren, e informa cuántas ventas se leyeron y en qué rango.
- **HU-A03** — Como Administrador, quiero que al aplicar se recalcule todo, para no tener que tocar nada más.
  - CA: al confirmar, las ventas quedan guardadas, los conceptos porcentuales se recalculan solos y el resultado del ejercicio se actualiza sin recargar la página.
- **HU-A04** — Como Administrador, quiero que un mes largo se resuelva solo, sin tener que pedirlo por tramos.
  - CA: un mes de 31 días se resuelve en 4 llamadas encadenadas de ≤10 días y el usuario nunca ve esa mecánica.
- **HU-A05** — Como Administrador, quiero que una caída de Ayres no me arruine el período.
  - CA: con la API inalcanzable, el sistema avisa y el período queda **exactamente** como estaba; si falla un tramo intermedio, tampoco se aplica nada.
- **HU-A06** — Como Administrador, quiero no poder romper un mes ya cerrado.
  - CA: en un período cerrado el botón no aparece, y si igual se invoca el endpoint responde que está cerrado y no escribe.
- **HU-A07** — Como Administrador, quiero enterarme si Ayres empieza a informar un canal que el sistema no conoce.
  - CA: un `sectorTipo` no mapeado no se descarta ni rompe: su importe va a "Otros" y el preview lo advierte.
- **HU-A08** — Como SuperUsuario, quiero comprobar la conexión con Ayres sin tocar un período.
  - CA: desde Sistema puedo probar la conexión y obtener un resultado claro (conecta / credenciales rechazadas / inalcanzable) sin escribir ningún dato.

---

## 15. Diseño — Sprint "Entrega 1: fixes y mejoras" (Septiembre 2026)

Entrada: `1-analista-funcional.md` §16 aprobado, con P-B03/04/05/07 resueltas por el dueño el 2026-09-09. **28 ítems** (los 30 del backlog menos el 4 y el 10, que no reproducen).

### 15.0 Escaneo de reutilización (obligatorio)

| Origen | Qué se toma | Ítem |
|---|---|---|
| **PAT-014 — blankproject** (`C:\Sistemas\BlankProject`) | Flujo completo de "olvidé mi contraseña": acciones `ForgotPassword`/`ResetPassword`, `PasswordResetViewModels.cs` y 3 vistas con el mismo estilo `ov-login-card` del Login. **KOI no lo tiene porque se clonó antes de que el patrón se portara al baseline.** Ya está probado end-to-end contra base real en la-platense. | **1** |
| **KOI mismo — fix de la columna Período** (Reparto General / Historial) | `data-order` numérico en la celda + `columnDefs type:'num'`. Es el mismo bug, en otra columna. | **13** |
| **KOI mismo — PAT-012 / `ImportacionInicial`** | Flujo analizar → preview → confirmar, con el flag `persistir` en una sola función. | **14, 30** |
| **KOI mismo — `EstadoResultados/Mensual`** | Edición inline por AJAX con indicador por fila (Etapa 18) y el helper `pintarImporteConcepto`. | **7, 11** |
| **KOI mismo — `MiInversion`** (gráfico de evolución del recupero, Etapa de dividendos) | Chart.js ya integrado y con el patrón de tema claro/oscuro resuelto. | **26** |

**No se reutiliza de otros proyectos** para el rol Gerente: el scoping por identidad de PAT-017 es para usuarios finales no-staff (portal del inversor), y acá se trata de un rol interno con escritura. Se resuelve con las policies que el proyecto ya usa.

### 15.1 Lote A — Defectos (van primero, y se entregan aunque el resto se recorte)

**A1 · Ítem 12 — el repositorio genérico no persiste.**
- `Repository<T>.UpdateAsync`, `AddAsync` y `DeleteAsync` pasan a llamar `await _context.SaveChangesAsync()`. Se corrige **el repositorio**, no sólo el controller: dejarlo como está es una trampa para el próximo que lo use.
- `InversoresController` no requiere cambios una vez arreglado el repositorio.
- **Criterio de aceptación:** crear, renombrar y eliminar un inversor desde la pantalla y verificar el efecto **releyendo el registro**, no confiando en el mensaje de éxito — que es precisamente lo que enmascaró el bug.

**A2 · Ítem 8 — consolidación de los dos catálogos.** Tres piezas, en este orden:
1. **Migración de datos (riesgo alto).** Mover los gastos de los 14 subgrupos viejos a su equivalente del catálogo nuevo. Mapeo explícito, revisado antes de ejecutar. Los pares con colisión de nombre (`12→39` Regalías, `22→43` Cargas Sociales) son inequívocos; el resto se lista para revisión. **Backup previo obligatorio y verificación de que el total de gastos de cada período no cambie ni un centavo.** Los subgrupos viejos se eliminan recién después de verificar.
2. **Importador idempotente.** Al reimportar, si ya existe un concepto para ese período y subgrupo, se **actualiza** en vez de crear uno paralelo. Es lo que hoy produce la duplicación real que rompe el cierre.
3. **Editar importes de conceptos importados.** Hoy la vista bloquea la edición de conceptos inactivos (`!concepto.EsInactivo`). Tras la consolidación no quedan conceptos inactivos con importe, así que la regla se cumple sola. Se mantiene la restricción para subgrupos realmente dados de baja.

**A3 · Ítem 13 — orden de "Util/Punto".** `data-order` numérico en las celdas de importe de Reparto General, más `columnDefs: [{ type:'num', targets:[...] }]`. Idéntico al fix ya aplicado en la columna Período.

**A4 · Ítem 3 — `/System` fuera del menú de no-superadmin.** El link "Sistema / Email" se mueve del bloque `Administrador || SuperUsuario` al bloque `SuperUsuario`. El controller ya exige SuperUsuario: hoy el Administrador ve un link que le devuelve 403.

### 15.2 Lote B — Acceso y permisos

**B1 · Ítem 1 — recuperar contraseña antes del login.** Port de PAT-014 desde el baseline. En `Login.cshtml`, link **"¿Olvidaste tu contraseña?"** debajo del formulario. Se conservan las dos decisiones de seguridad del patrón: respuesta **idéntica exista o no el email** (no delata cuentas) y rate limiting propio `"password-reset"`. Se renombra la marca del email a "KOI Dumplings".
- *Nota:* el cliente también menciona recuperar **nombre de usuario**. En este sistema el usuario **es** el email, así que no hay nada que recuperar: el flujo por email lo cubre. Se aclara en el texto de la pantalla.

**B2 · Ítem 2 — ocultar Cámaras.** Se ocultan del sidebar "Cámaras" (sección Local) y "Config. cámaras" (sección Sistema). **No se borra el módulo ni se revocan permisos**: queda accesible por URL para el Administrador, listo para volver a mostrarse. Se implementa con `FeatureFlags.ModuloCamaras`, el mismo mecanismo que se estrenó con Ayres — así se prende de nuevo sin redeploy.

**B3 · Ítem 9 — rol "Gerente".** Se **reutiliza el rol `Encargado` existente**, ampliando su alcance en vez de crear uno nuevo (evita un cuarto rol y no rompe al usuario del Fichador).
- Policy nueva `GestionOperativa` = SuperUsuario + Administrador + Encargado, aplicada a `EstadoResultados` (carga y consulta) y a la vista anual.
- **La barrera de cierre va en el servidor**: `CerrarPeriodoAsync` y la acción de cierre rechazan al Encargado, no alcanza con ocultar el botón. Mismo criterio para `ReabrirPeriodo`.
- **Sin acceso** a Inversores, Puntos, Liquidaciones, Reparto General ni Configuración.
- **Efecto lateral a resolver:** `NotificationsController` es `SoloAdministrador`, así que hoy la campanita del layout le daría 403 en todas las pantallas. Se amplía a la policy nueva.
- Sidebar filtrado por rol: el Encargado ve KOI + Gestión, no ve Inversiones ni Sistema.

### 15.3 Lote C — Estado de Resultados

**C1 · Ítems 5 y 6 — importes sin decimales y sin flechitas.**
- **Sólo presentación** (P-B03). Se centraliza en el helper `FormatoMoneda` que el proyecto ya tiene, para no tocar 98 lugares a mano: pasa a redondear a entero para mostrar. La base conserva los centavos y la conciliación contra el Excel sigue exacta.
- Flechitas: `inputmode="numeric"` + CSS que oculta el spinner (`::-webkit-outer-spin-button`, `appearance:none`) en `olvidata-theme.css`, aplicado a la clase de los inputs de importe. Una regla, no 17 vistas.
- **Queda registrado como opción 2**, no implementada, redondear también al guardar.

**C2 · Ítem 7 — dar de baja subgrupos desde el EDR.** Botón de baja por fila, sólo Administrador y sólo sobre subgrupos **sin importe cargado en el período**. Confirmación previa. Es baja del catálogo (soft delete), así que se advierte que afecta a los meses siguientes, no a la historia.

**C3 · Ítem 11 — conceptos por mes (el gasto extraordinario).** Es el ítem con más carga de diseño del lote. El cliente quiere sacar o agregar "Fumigación" según el mes.
- **Agregar:** selector "Agregar concepto a este mes" que lista los subgrupos del catálogo que todavía no están en el período, y crea la fila con importe 0 lista para cargar.
- **Quitar:** la fila de un concepto **con importe 0** puede sacarse del mes. Si tiene importe, primero hay que ponerlo en 0 — así nunca se borra plata por accidente.
- **No confundir con el ítem 7:** acá se agrega/saca del **mes**, no del catálogo.

**C4 · Ítem 14 — previsualizar la notificación de cierre.** Reutiliza el patrón analizar→confirmar de PAT-012. Antes de `EnviarMasivo`, pantalla con el mail **tal como lo va a recibir el inversor** (uno de ejemplo, con datos reales) y la lista de destinatarios con su dirección. Botones "Enviar a los N" / "Cancelar". **Nada se envía hasta confirmar.**

### 15.4 Lote D — Dashboard, Mes actual y mobile

Se apoyan en datos que **Ayres ya provee** desde E2-01 (cubiertos, tickets, ventas por día).

| Ítem | Cambio |
|---|---|
| 15 | En el Dashboard mensual: **cubiertos por día** reemplaza a ticket promedio; se agregan resultado en pesos y en dólares. |
| 16 | Se elimina el gráfico **y** la tabla de "facturado vs informal". |
| 17 | Se elimina el gráfico de ventas por canal con desglose IVA. |
| 18 | El gráfico de desglose por rubro pasa a ocupar el ancho liberado por 16 y 17. |
| 19 | Mes actual: cantidad de tickets y cantidad de cubiertos. |
| 20 y 22 | Gráfico de **evolución diaria** con dos series conmutables: **plata** y **cubiertos**. Un solo gráfico con selector, no dos. Fuente: `GET /ventas` de Ayres agrupado por `fechaContable`. |
| 21 y 29 | Mobile: se agrega la tarjeta **Cubiertos**, que además deja la grilla par y simétrica. |

**Nota de arquitectura para el implementador:** la evolución diaria necesita el detalle por día, que hoy el agregador de Ayres **descarta** por diseño (se acumula y se tira el detalle, R-A03). Hay que devolver además una serie diaria — que es liviana, un registro por día — sin volver a sostener las ~1.000 ventas del mes en memoria.

### 15.5 Lote E — Vista del inversor

**E1 · Ítem 23 — sacar "facturado vs informal" (LEGAL).** Barrido completo de **todos** los informes del inversor: Mi Inversión, Rendimiento Histórico, Mes Actual, y cualquier exportable (PDF/Excel). **Es el ítem de mayor sensibilidad del lote y no admite entrega parcial.** Nota: el Administrador sí sigue viendo el desglose A/B donde lo necesita para cargar; lo que se elimina es su exposición al inversor.

**E2 · Ítem 24 — agrandar desglose por rubro y datos comerciales** en Rendimiento Histórico, ocupando el espacio que libera E1.

**E3 · Ítem 25 — explicar la brecha del recupero.** No se toca el cálculo (P-B05). En Mi Inversión, junto a los dos porcentajes, una leyenda breve: el recupero en pesos convierte **cada dividendo al tipo de cambio de su mes**, así que ambos porcentajes son correctos y distintos. Redacción sin tecnicismos, para el inversor.

**E4 · Ítems 26, 27, 28 — el reporte de rendimiento.** Se replica en pantalla el formato del PDF aprobado:
- 4 KPIs en dólares: Capital Aportado · Utilidad Acumulada (verde) · % Recupero (con "En N meses") · Rentabilidad Mensual promedio.
- **Gráfico de barras** de evolución de pagos mensuales en USD, con el valor rotulado sobre cada barra.
- **Comparativa de Mercado** en barras horizontales, con **benchmarks fijos configurables** (P-B04): se administran desde Configuración, con los valores del PDF como carga inicial (S&P 500 12 %, Bonos Corporativos 8 %, Propiedades Inmobiliarias 5 %). Sin integración de mercado.
- Párrafo de análisis al pie.

### 15.6 Lote F — Importador (ítem 30)

El cliente dice "no sé por qué está esto". El texto describe un flujo de 6 hojas que él nunca usó — la importación real la hicimos nosotros. **No se saca la funcionalidad** (sirve, y el ítem 8 la vuelve a necesitar), se reescribe el texto para que diga **cuándo usarla y cuándo no**, y se corrige la frase *"los registros que ya existen se omiten con advertencia"*, que después del ítem 8 deja de ser cierta: pasan a actualizarse.

### 15.7 Impacto por capa

| Capa | Alcance |
|---|---|
| **Domain** | Sin entidades nuevas. Posible campo de configuración para benchmarks (E4). |
| **Application** | Policy `GestionOperativa`; `FeatureFlags.ModuloCamaras`; DTO de serie diaria (D); DTOs de benchmarks. |
| **Infrastructure** | **Fix del repositorio genérico (A1)**; migración de consolidación de catálogos (A2); serie diaria en el agregador de Ayres; guardas de cierre por rol. |
| **Web** | El grueso: Login + 3 vistas de reset; sidebar; EDR (decimales, spinners, baja, conceptos por mes); Dashboard; Mes Actual; Mi Inversión; Rendimiento Histórico; preview de notificación; texto del importador. |
| **Migración EF** | **Sí**: consolidación de catálogos (datos, no esquema) y, si los benchmarks se persisten, una tabla o filas de parámetro. |

### 15.8 Riesgos de implementación

- **La migración del ítem 8 es lo más delicado del sprint.** Toca gastos con liquidaciones ya pagadas. Se ejecuta con backup, mapeo revisado, y verificación de totales por período **antes y después**. Si un total se mueve, se revierte.
- **El ítem 23 es legal**: un solo informe que se olvide invalida el objetivo. Requiere barrido exhaustivo, no búsqueda por nombre de pantalla.
- **La barrera de cierre del Gerente (B3) tiene que estar en el servidor.** Ocultar el botón no es control de acceso.
- **A1 cambia el comportamiento de un repositorio genérico**: hay que verificar que ningún otro consumidor dependa (hoy no lo hay) del hecho de que no guardaba.
- **C1 toca el formateo de importes de todo el sistema.** Centralizarlo en `FormatoMoneda` reduce el riesgo, pero hay que revisar que ningún lugar dependa de ver centavos — en particular el tipo de cambio, que **no es un importe** y debe conservar sus decimales.
