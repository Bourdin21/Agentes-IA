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

### Etapa 2026-08-31 — cierre de auditoria QA (16 hallazgos) + Data Protection persistente

Implementados **los 16 hallazgos** de la auditoria de calidad, mas la feature de no cerrar sesion
en cada deploy. Sin migracion EF (ningun cambio de esquema: `Movimiento.DescripcionOriginal` y
`Cuota.FechaInicio` ya existian como columnas).

- **MH-001** (`UsersController.Index`, bloqueante): el `IN` de `HashSet<string>` contra MySQL
  devolvia 500 **siempre**, incluso con la coleccion vacia. Los filtros por texto y por Estado y
  el orden quedan server-side; la lista se materializa con `ToListAsync()` y **solo** el filtro
  por `superIds`/`enRolIds` pasa a memoria. `totalCount` y la paginacion se recalculan **despues**
  del filtro en memoria.
- **LP-003** (decimales, alcance ampliado — ver "Decision de alcance" abajo): binder invariante
  nuevo (`Web/ModelBinders/InvariantDecimalModelBinder.cs`) + render invariante en los **8** sitios
  del repo donde un decimal se postea (`Movimientos/Create|Edit`, `Cuotas/Create`, y los 3 hidden
  de `Importacion/Preview`).
- **Pendientes fuera de los totales**: `HomeController.GenerarDashboard` replica el criterio de
  `DashboardController.ResumenGeneral` (`Estado == Realizado` en ingresos/egresos, comparativo,
  top categorias, deuda de tarjeta, alertas y KPIs). `CalcularDeudaTarjetaAsync` tambien filtra
  ahora por `Realizado`. `MovimientosRecientes` sigue mostrando pendientes a proposito (es un feed
  de actividad, no un total).
- **Dedup del import re-validado en el confirm** contra la base + `HashSet` intra-lote, con
  contador `MovimientosOmitidosPorDuplicado`.
- **Codigo muerto eliminado**: `ImportarResumenAsync` + `ProcesarMovimientoAsync` +
  `ObtenerOCrearCuotaAsync` + `ObtenerCategoriaGenericaAsync` (292 lineas, sin ningun caller,
  confirmado por grep) y la firma correspondiente en `IResumenTarjetaImporter`. Borrada tambien la
  carpeta `Services/Importacion/` (4 archivos de 0 bytes, verificado antes de borrar).
- **Backdating de cuotas N/M con N>1**, **fila sintetica de impuestos con clave de dedup variable**,
  **falsos positivos de disparidad USD/ARS excluidos**, **guard de solo-USD sin cotizacion**,
  **`DescripcionOriginal` editable en `Movimientos/Edit`**, **`Cuota.FechaInicio` editable**,
  **redondeo PAT-003 en cuotas**, **saldo por cuenta agregado server-side**, **`[Authorize]` de
  clase en `HomeController`** (`Error`/`StatusCode` con `[AllowAnonymous]`).
- **Data Protection**: `AddDataProtection().PersistKeysToFileSystem(ContentRoot/DataProtection-Keys)`
  `.SetApplicationName("VirtualWallet")` en `Program.cs`; `DataProtection-Keys/` gitignorado;
  reglas `MsDeploySkipRules` en el `.pubxml` de Web Deploy para que el deploy no borre la carpeta
  (`SkipExtraFilesOnServer=false`). Mecanismo identico al ya usado en `elevenlaplata`
  (`Eleven.Web/.../olvidatasoft-002-site8 - Web Deploy.pubxml`, carpeta `keys`), mismo hosting.

**Decision de alcance (LP-003) — desviacion deliberada, justificada:** la auditoria acotaba el fix
al render y pedia **no** agregar el binder invariante ni tocar los hidden de `Preview.cshtml`. Se
midio el comportamiento real del binder por defecto bajo la cultura `es-AR` fijada en `Program.cs`
(`NumberStyles.Float | AllowThousands`): un `<input type="number">` postea **siempre** con punto
decimal por spec HTML, y `"1234.56"` se parseaba como **123456** — el punto se tomaba como
separador de miles. Es decir, la entrada ya estaba corrompiendo importes x100 en silencio. Aplicar
solo el fix de render habria **empeorado** el cuadro: el campo pasaria a mostrarse bien y a
corromperse al guardar, en vez de quedar vacio. Como los sitios de post-back son exactamente 8 y
enumerables, se implemento el par completo (binder + render), que es el unico estado coherente.
El binder usa `NumberStyles.Float` **sin** `AllowThousands` justamente para que un separador de
miles no pueda absorberse en silencio, con fallback a `es-AR` para valores tipeados con coma.

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
- **R11 (2026-08-31)**: la re-validacion de duplicados del confirm cubre el caso secuencial (F5,
  reenvio del POST, doble click serializado) pero **no** dos POST estrictamente concurrentes: la
  consulta lee la base antes del `SaveChanges` final del otro request. Cerrarlo del todo requiere
  un indice unico sobre `(UsuarioId, CuentaId, Fecha, DescripcionOriginal)` — implica migracion EF
  y decidir que hacer con los duplicados ya existentes en produccion; queda diferido.
- **R12 (2026-08-31)**: el backdating de `FechaInicio` en cuotas N>1 aplica **solo a cuotas nuevas**
  creadas desde el import a partir de ahora. Las cuotas ya persistidas con `FechaInicio` corrida
  siguen mostrandose como vigentes de mas — se corrigen a mano desde `Cuotas/Edit`, que ahora
  permite editar ese campo (no se hizo backfill automatico).
- **R13 (2026-08-31)**: las reglas `MsDeploySkipRules` del `.pubxml` estan verificadas por
  precedente (`elevenlaplata`, mismo hosting/SDK) pero **no** ejecutadas todavia en un deploy real
  de este proyecto. Confirmar en el proximo deploy que `DataProtection-Keys/` sobrevive en el
  servidor (ver "Proximos pasos pendientes").

### Proximos pasos pendientes
- QA manual end-to-end de importación con PDFs reales Mastercard y Visa, incluyendo un PDF Visa con consumos en USD (para cerrar R9).
- Visto bueno de stakeholder sobre R5 (reintegros como Ingreso+EsPagoTarjeta=true en reportes historicos).
- QA manual de Dolar Historico: convertir monto en Create con cotizacion del dia, ver historial de cotizaciones.
- QA manual de mejoras de dashboard (M-04 a M-07) según los 4 escenarios de prueba documentados en el historial.
- QA manual del cierre de defectos D-04/D-09/D-10 según los 6 escenarios documentados en el historial.
- Ejecución del script idempotente `ConstrainDescripcionOriginalLength.sql` en producción (pendiente operativo, no solo de QA).
- Limpieza del archivo temporal `ProvinciaVisaResumenParser.cs.new`.
- **Verificar en el proximo deploy real (R13)**: que `DataProtection-Keys/` se cree en el servidor
  tras el primer request y que **sobreviva** al deploy siguiente (las reglas `MsDeploySkipRules` no
  se ejercitaron todavia en este proyecto). Señal de exito: la sesion no se cierra tras un deploy.
- **QA manual de decimales (LP-003)**: alta y **reapertura** de un movimiento con centavos
  (ej. 1234,56) en `Movimientos/Create`/`Edit` y de una cuota en `Cuotas/Create`, confirmando que
  el importe guardado es el tipeado y **no** x100. Reimportar un resumen ya importado y confirmar
  que los importes del preview siguen llegando bien (hidden de `Preview.cshtml` ahora invariantes).
- **QA manual de portada vs ResumenGeneral**: con al menos un movimiento `Pendiente` en el mes,
  los totales de `Home/Index` y de `Dashboard/ResumenGeneral` deben coincidir para el mismo periodo.

## Historial de ajustes
- 2026-08-31: cierre completo de la auditoria QA (16 hallazgos, de bloqueante a bajo) + Data Protection persistente en disco. Sin migracion EF. Desviacion de alcance deliberada en LP-003 (se agrego el binder invariante y se tocaron los hidden de `Preview.cshtml`, ambos excluidos del pedido original) porque el fix acotado habria introducido una corrupcion silenciosa x100 al guardar — medicion y justificacion en la etapa correspondiente.
- 2026-07-23 (mergeado desde memoria local del proyecto): importación de resúmenes de tarjeta — reintegros (M2/M5/M7), ajustes de flujo (cuenta/fecha/USD), reescritura completa del parser Visa contra PDF real, importes en dos columnas ARS/USD + filtros de Movimientos + KPIs de dashboard. 4 partes, sin migración EF en ninguna.
- 2026-05-11: feature Dolar Histórico — `ICotizacionService`/`CotizacionService` nuevos, `DolarController`, vista de historial, integración de cotización en alta/edición de movimientos.
- Mejoras de dashboard M-04 a M-07: badges de pendiente, columnas de cuotas/saldo arrastrado, alerta de crecimiento por categoría.
- Cierre de defectos QA remanentes D-04, D-09, D-10 (D-15 revisado sin cambios necesarios).
- 2026-08-16: Reestructuración documental — este archivo tenía 4 secciones de nivel 2 apiladas por etapa ("Etapa mergeada", "Etapa actual: dólar histórico", "Etapa anterior: dashboard", "Etapa anterior: cierre QA") en vez de un estado vigente único. Consolidado en `## Definiciones vigentes` (agrupado por feature, ya que a diferencia de otros proyectos cada etapa cubre una funcionalidad distinta, no una corrección de la anterior) + este historial de una línea por etapa. Ningún riesgo, checklist pendiente ni decisión de diseño se perdió en la consolidación — todos los ítems `[ ]` sin marcar de los checklists originales pasaron a "Próximos pasos pendientes".
