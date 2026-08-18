# 5 - Implementador (memoria acumulativa)

## Proyecto: VirtualWallet
## Ultima actualizacion: 2026-08-16

## Definiciones vigentes

### Archivos y capas modificadas (acumulado, por feature)

**Importacion de resumenes de tarjeta — reintegros y parser Visa/Mastercard (M2/M5/M7 + Partes 1-4):**
- Decisiones definitivas: cupon NO se persiste en columna propia (se conserva la linea cruda en `Movimiento.DescripcionOriginal`); reintegros se modelan como `TipoMovimiento.Ingreso` con `EsPagoTarjeta=true` (Opcion B); dedupe por `UsuarioId + CuentaId + Fecha + Monto + DescripcionOriginal`.
- Sin migracion EF, sin cambios de permisos (endpoints `Importacion/*` ya requerian autenticacion, toda consulta ya filtraba por `UsuarioId`).
- Application (`ImportacionResumenDtos.cs`): `MovimientoTarjetaDto` +`DescripcionRaw`/+`EsReintegro`; `ResultadoParseoResumen` +`TotalDeclaradoPesos`/+`TotalDeclaradoDolares`/+`Advertencias`; `MovimientoPreviewItem`/`PreviewImportacionResult`/`MovimientoImportadoDto` con los mismos campos agregados.
- Infrastructure: `ProvinciaMastercardResumenParser` (regex de importes con negativos, `LimpiarDescripcion`, `TryExtraerTotalTitular`+`ValidarTotales`). `ProvinciaVisaResumenParser` — **reescrito por completo** contra un PDF real (Visa Platinum Banco Provincia); el formato original asumido no coincidia con el real, el preview quedaba vacio. Formato real: `DD.MM.YY  NNNNNN[*|K]  DETALLE [Cuota NN/MM]  IMPORTE[-]`, pagos por `SU PAGO EN PESOS`, reintegros por `BONIF. CONSUMO ...`, total en linea `Tarjeta NNNN Total Consumos...`. Smoke test contra PDF real: 43 movimientos (5 pagos, 10 cuotas, 26 compras, 2 reintegros, 2 impuestos), sin advertencias. `ResumenTarjetaImporter` — normaliza a `Math.Abs`, decide rama pago/reintegro/gasto, dedupe por linea cruda, persiste reintegros como `Ingreso+EsPagoTarjeta=true`; mapeo posicional de columnas ARS/USD (primera=pesos, segunda=dolares), pesos derivados por cotizacion solo si falta ARS.
- Web: `ImportacionController` propaga `Advertencias` y filtra cuenta destino por `Cuenta.Tipo` conteniendo "tarjeta"; parser extrae `FechaCierre`/`FechaVencimiento` del PDF (el input manual del usuario queda como fallback opcional, dejo de ser `[Required]`); `ImportarPreviewViewModel` +`Advertencias`/+`TotalReintegros`/+`MontoReintegros`; `Views/Importacion/Preview.cshtml` con fila celeste + icono para reintegros, banners de advertencias.
- Movimientos: filtros nuevos (tipo/categoria/cuenta) persistidos en Session, `Tipo=3` = Pagos/Reintegros TC (incluye reintegros por diseno M5=B); resumen Ingresos/Egresos/Balance; layout responsive mobile.
- Dashboards: KPIs de proyeccion run-rate a fin de mes + compromiso mensual de cuotas vigentes (Home); comparativa vs periodo anterior, gasto promedio diario, concentracion en top categoria (ResumenGeneral).

**Dolar historico (2026-05-11):**
- Application: `ICotizacionService.cs` nuevo (`GetCotizacionAsync(DateOnly)`, `GetUltimaCotizacionAsync()`).
- Infrastructure: `CotizacionService.cs` (consulta a API de cotizacion, cache y fallback).
- Web: `DolarController.cs` nuevo (`Historico`); `MovimientosController.cs` con integracion de cotizacion en Create/Edit; `DolarHistoricoViewModel.cs` nuevo; `Views/Dolar/Historico.cshtml` nueva; `_Layout.cshtml` con item de menu nuevo.
- Sin migracion EF.

**Mejoras dashboard (M-04, M-05, M-06, M-07):**
- `ResumenGeneralViewModel.cs`: `TopGastoItem.Pendiente` (M-04), `CuotaActivaItem.CuotasRestantes`/`MontoPendiente` computed (M-05), `DeudaTarjetaItem.SaldoArrastrado` computed (M-06).
- `DashboardController.cs`: Top 10 setea `Pendiente` segun `EstadoMovimiento` (M-04); `GenerarAlertas` compara egresos del periodo anterior por categoria, alerta "Crecimiento en {categoria}" con umbral 30% limitado a las top 8 categorias (M-07).
- `Views/Dashboard/ResumenGeneral.cshtml`: columnas nuevas en Cuotas Activas y Deuda Tarjeta, badge+fila resaltada en Top 10.
- Sin migracion EF.

**Cierre QA defectos remanentes (D-04, D-09, D-10):**
- D-04: checkbox `EsPagoTarjeta` visible solo para egresos en `Movimientos/Create.cshtml`/`Edit.cshtml`, normalizado a `false` si `Tipo != Egreso`.
- D-09: `CuotasActualizadas` renombrado a `CuotasReutilizadas` (DTO, ViewModel, `ResumenTarjetaImporter`) — el contador nunca actualizaba la cuota, la reutilizaba; el nombre viejo era enganoso. Verificado por busqueda global que no quedan referencias externas al nombre viejo.
- D-10: `DashboardController.ResumenGeneral` persiste `dateRange`/`usd` en Session (`Dashboard_DateRange`/`Dashboard_Usd`), distinguiendo default del usuario via `Request.Query.ContainsKey("usd")`.
- D-15: revisado, no requeria cambios (la regla de que movimientos de cuota solo permiten `CambiarEstado`, no `Edit`/`Delete` individual, ya estaba bien implementada).
- Sin migracion EF nueva en esta etapa — pendiente la ejecucion del script idempotente `ConstrainDescripcionOriginalLength.sql` en produccion (ver Proximos pasos).

### Migraciones EF generadas
Ninguna a lo largo de todo este historial (todas las features anteriores reutilizaron columnas existentes, principalmente `Movimiento.DescripcionOriginal`/`EsPagoTarjeta`). Queda pendiente en producción la ejecución del script idempotente `ConstrainDescripcionOriginalLength.sql` (generado en una etapa previa a este archivo, ver Riesgos).

### Riesgos residuales
- **R1** (regex de importe/descripcion fragil ante cambio de formato del banco) — mitigado por `DescripcionOriginal` crudo + advertencias de total, no eliminado.
- **R2** (colision de dedupe en Visa sin cupon) — aceptado como falso positivo excluible.
- **R3** (performance de dedupe en cuentas grandes) — aceptable al volumen actual, indice opcional diferido.
- **R5 — pendiente de visto bueno de stakeholder**: reintegros modelados como `Ingreso + EsPagoTarjeta=true` podrian no ser contemplados por reportes historicos que asuman que "Ingreso" nunca lleva ese flag.
- **R8** (descripciones muy cortas entre cupon e importe podrian ser ambiguas en el parser Visa) — mitigado con regex no-greedy + importe ARS obligatorio al final, no eliminado.
- **R9**: el PDF de muestra usado para el smoke test del parser Visa no tenia consumos en USD reales — ese camino del parser queda sin confirmar contra un PDF que si los traiga.
- **R10** (mapeo posicional ARS/USD asume el layout actual del banco) — mitigado por `ValidarTotales`+advertencias.
- `ICotizacionService` depende de una API externa; si no esta disponible usa fallback (comportamiento aceptado, no un bug).
- Archivo temporal `ProvinciaVisaResumenParser.cs.new` quedó en el repo sin uso activo tras la reescritura del parser — limpieza pendiente.

### Proximos pasos pendientes
- QA manual end-to-end de importación con PDFs reales Mastercard y Visa, incluyendo un PDF Visa con consumos en USD (para cerrar R9).
- Visto bueno de stakeholder sobre R5 (reintegros como Ingreso+EsPagoTarjeta=true en reportes historicos).
- QA manual de Dolar Historico: convertir monto en Create con cotizacion del dia, ver historial de cotizaciones.
- QA manual de mejoras de dashboard (M-04 a M-07) según los 4 escenarios de prueba documentados en el historial.
- QA manual del cierre de defectos D-04/D-09/D-10 según los 6 escenarios documentados en el historial.
- Ejecución del script idempotente `ConstrainDescripcionOriginalLength.sql` en producción (pendiente operativo, no solo de QA).
- Limpieza del archivo temporal `ProvinciaVisaResumenParser.cs.new`.

## Historial de ajustes
- 2026-07-23 (mergeado desde memoria local del proyecto): importación de resúmenes de tarjeta — reintegros (M2/M5/M7), ajustes de flujo (cuenta/fecha/USD), reescritura completa del parser Visa contra PDF real, importes en dos columnas ARS/USD + filtros de Movimientos + KPIs de dashboard. 4 partes, sin migración EF en ninguna.
- 2026-05-11: feature Dolar Histórico — `ICotizacionService`/`CotizacionService` nuevos, `DolarController`, vista de historial, integración de cotización en alta/edición de movimientos.
- Mejoras de dashboard M-04 a M-07: badges de pendiente, columnas de cuotas/saldo arrastrado, alerta de crecimiento por categoría.
- Cierre de defectos QA remanentes D-04, D-09, D-10 (D-15 revisado sin cambios necesarios).
- 2026-08-16: Reestructuración documental — este archivo tenía 4 secciones de nivel 2 apiladas por etapa ("Etapa mergeada", "Etapa actual: dólar histórico", "Etapa anterior: dashboard", "Etapa anterior: cierre QA") en vez de un estado vigente único. Consolidado en `## Definiciones vigentes` (agrupado por feature, ya que a diferencia de otros proyectos cada etapa cubre una funcionalidad distinta, no una corrección de la anterior) + este historial de una línea por etapa. Ningún riesgo, checklist pendiente ni decisión de diseño se perdió en la consolidación — todos los ítems `[ ]` sin marcar de los checklists originales pasaron a "Próximos pasos pendientes".
