# 2 - Diseñador funcional — Proyecto KOI

> Memoria acumulativa del agente diseñador funcional.
> Etapa: Diseño funcional. Estado: ✅ ACTUALIZADO — P-A01→P-A07 incorporadas · ventas 4 campos · TC con selector cotización · preview editable · Reabierto eliminado.
> Fecha: 2026-06-11. Input: 1-analista-funcional.md v2 (cierre P-A01→P-A07).

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
