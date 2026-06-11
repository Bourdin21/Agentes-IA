# 2 - Diseñador funcional — Proyecto KOI

> Memoria acumulativa del agente diseñador funcional.
> Etapa: Diseño funcional. Estado: CERRADO (aprobado para arquitectura).
> Fecha: 2026-06-11. Input: 1-analista-funcional.md aprobado.

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
[ KPI Ventas mes (A+B, desglose A/B) ] [ KPI Total Gastos ] [ KPI Resultado ] [ KPI Rentabilidad % ]
[ KPI USD: Ventas | Gastos | Resultado (TC del mes) ]      [ KPI Indicadores: ticket prom | ítems/ticket | cubierto prom ]
[ Gráfico barras+línea: Ventas vs Gastos vs Resultado, 12 meses, selector de año / multi-año ]
[ Gráfico dona: composición de gastos por rubro del mes ]  [ Gráfico línea: rentabilidad % histórica ]
[ Gráfico línea: Resultado en USD histórico ]              [ Tabla resumen mensual del año (mini estado de resultados) ]
```
- Tema dark/light con toggle persistido por usuario (tokens CSS duplicados en `[data-theme="dark"]`).
- Gráficos con librería JS de charts (una sola librería para todo el sistema).
- Meses sin datos: card en estado vacío ("Sin datos del período"), nunca división por cero.

### P-03 Estado de resultados mensual (Admin — carga)
Cabecera: mes/año + estado del período (Abierto/Cerrado/Reabierto) + TC del mes.
Secciones colapsables en el orden del Excel: Ventas (A editable, B editable, total calculado) → CMV → Fee de Franquicia (calculado, solo lectura) → Sueldos y CCSS → Gastos Varios → Alquiler → Servicios (incluye comisiones calculadas) → Impuestos (IVA manual + calculados) → Previsión y Reservas (calculado) → Gastos Extras.
Panel fijo de totales: Total Gastos, Resultado, Rentabilidad, equivalentes USD. Botones: Guardar borrador / Cerrar período.

### P-04 Estado de resultados anual (Admin e Inversor — consulta)
Tabla tipo Excel: filas = rubros/subgrupos, columnas = 12 meses + total anual. Selector de año. Exportable a Excel.

### P-05 Configuración de catálogos (Admin)
Tabs: Rubros y subgrupos (ABM con baja lógica) · Parámetros porcentuales (concepto, % vigente, base de cálculo A/total, vigencia desde) · Tipo de cambio mensual (grilla año × mes).

### P-06 Indicadores de venta (Admin — carga)
Grilla mensual: ticket promedio, ítems por ticket, cubierto promedio. Nota visible: "Fuente: Ayres POS (carga manual)".

### P-07 Puntos de inversión (Admin)
Vista de los 100 puntos (número, valor de aporte, bonificado sí/no, inversor asignado, vigencia). Card resumen: total recaudado, puntos asignados/disponibles. Asignación con vigencia mensual (historial de cambios visible).

### P-08 Liquidaciones del mes (Admin)
Cabecera: mes cerrado, Resultado, utilidad por punto (= Resultado/100), TC. Detalle por inversor: puntos vigentes, liquidación bruta, consumos (editable mientras Pendiente), neto, USD, renta mensual, estado (Pendiente/Pagada), fecha de pago. Acciones: registrar consumos, marcar pagada (masivo o individual), reabrir con motivo.

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
| DashboardVM | Período, KPIs (ventas A/B/total, gastos, resultado, rentabilidad, USD), series históricas, indicadores | solo lectura; períodos sin datos → vacío controlado |
| EstadoResultadosEdicionVM | Período, Estado, TC, VentasA, VentasB, lista RubroVM { Subgrupo, ImporteManual / %Calculado, Total } | importes ≥ 0; TC > 0 para cerrar; calculados no editables |
| EstadoResultadosAnualVM | Año, matriz rubro × mes, totales | solo lectura |
| ParametroPorcentajeVM | Concepto, Porcentaje, BaseCálculo (VentasA/VentasTotales), VigenciaDesde | 0–100 %, base requerida |
| TipoCambioVM | Año, Mes, Valor | > 0, único por mes/año |
| IndicadoresVentaVM | Período, TicketPromedio, ItemsPorTicket, CubiertoPromedio | ≥ 0 |
| PuntoInversionVM | Número (1–100), ValorAporte, Bonificado, InversorAsignado, VigenciaDesde | número único; Σ puntos vigentes ≤ 100 |
| LiquidacionMesVM | Período, UtilidadPorPunto, lista LiquidacionInversorVM { Inversor, Puntos, Bruto, Consumos, Neto, USD, Renta %, Estado, FechaPago } | consumos ≤ bruto; pagada inmutable |
| MiInversionVM | Capital, DividendosAcum ($/USD), Recupero %, RentaProm %, historial mensual | solo datos del inversor autenticado |
| CamaraConfigVM | UrlWebClient, CuentaReferencia, Notas, Activo | URL válida |
| NotificacionConfigVM | ServidorSmtp, Puerto, CasillaEmisora, NombreRemitente, Credencial | requeridos; prueba de envío antes de guardar |
| NotificacionEnvioVM | Período, Inversor, Email, FechaHora, Estado (Enviado/Fallido), DetalleError | solo lectura + acción Reenviar |
| UsuarioVM | Nombre, Email, Rol, InversorVinculado, Activo | email único; inversor requerido para rol Inversor |

## 5. Máquina de estados

**Período mensual**

| Estado origen | Evento | Estado destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| Abierto | Cerrar período | Cerrado | Ventas, TC y rubros obligatorios cargados | Calcula totales finales, genera liquidaciones Pendientes, **envía notificación por correo a inversores activos** (fallos no bloquean el cierre) | "Faltan datos obligatorios para cerrar" |
| Cerrado | Reabrir | Reabierto | Solo Admin + motivo | Habilita edición; recalcula liquidaciones no pagadas | "Hay liquidaciones pagadas: se conservan" |
| Reabierto | Cerrar período | Cerrado | Ídem cierre | Regenera liquidaciones Pendientes | ídem |

**Liquidación por inversor**

| Estado origen | Evento | Estado destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| Pendiente | Marcar pagada | Pagada | Fecha de pago informada | Registra fecha; congela montos | "Falta fecha de pago" |
| Pagada | Reabrir | Pendiente | Solo Admin + motivo | Registra motivo en auditoría | "Requiere motivo" |

## 6. Reglas de negocio y permisos por pantalla

| Pantalla | Admin | Inversor | Reglas clave |
|---|---|---|---|
| P-02 Dashboard | ✔ | ✔ | KPIs y series derivan solo de períodos con datos; B discriminada (decisión analista, hipótesis A aprobada para presupuesto) |
| P-03/P-04 Estado resultados | ✔ | P-04 solo lectura | Conceptos % según base configurada: comisiones/IIBB/débitos/tasa sobre **Ventas A**; regalías/canon/previsiones sobre ventas totales |
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
