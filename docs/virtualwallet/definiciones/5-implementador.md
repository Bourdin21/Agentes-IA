# 5 - Implementador (memoria acumulativa)

## Etapa (mergeada 2026-07-23 desde memoria local del proyecto): Importacion de resumenes de tarjeta — mejoras Mastercard/Visa (reintegros, fechas de PDF, parser Visa real, ARS/USD, Movimientos+KPIs)

> Nota de mergeo: este bloque combina 4 etapas encontradas en `C:\Sistemas\virtualwallet\docs\virtualwallet\definiciones\{2-disenador-funcional,3-arquitecto-mvc,5-implementador}.md` (memoria local del proyecto, no reflejada aca hasta este barrido cross-proyecto del 2026-07-23) que no tenian equivalente en este archivo central. Se preservan como bloque unico por ser una cadena de trabajo continua sobre el mismo importador de resumenes de TC.

### Decisiones de diseño (definitivas, del diseñador funcional)
| Codigo | Tema | Decision |
|---|---|---|
| M2 | Persistir cupon en columna propia | **No**. Se conserva la linea cruda en `Movimiento.DescripcionOriginal`. |
| M5 | Modelo de reintegros | **Opcion B**: registrar como `TipoMovimiento.Ingreso` con `EsPagoTarjeta=true`. Reduce la deuda igual que un pago. |
| M7 | Dedupe por cupon | **Si**. Comparar por `UsuarioId + CuentaId + Fecha + Monto + DescripcionOriginal` (linea cruda con cupon). |

### Decisiones de arquitectura (definitivas)
- **Sin migracion EF**: sin cambios de entidades. Se reaprovecha `Movimiento.DescripcionOriginal` (linea cruda, clave de dedupe), `Movimiento.EsPagoTarjeta=true` para pagos **y** reintegros, `Movimiento.Tipo` (Egreso=gastos/pagos, Ingreso=reintegros). Categorias reservadas por usuario "Pago Tarjeta" (Egreso) y "Reintegro Tarjeta" (Ingreso), creadas on-demand.
- **Sin cambios de permisos**: endpoints `Importacion/*` ya requerian autenticacion; toda consulta ya filtraba por `UsuarioId`.
- Unico componente nuevo: helper privado `ObtenerCategoriaReintegroTarjetaAsync` (espejo del helper ya existente para "Pago Tarjeta" — no se introdujo abstraccion nueva).
- Riesgos documentados: R1 regex fragil ante cambio de formato del banco (mitigado por `DescripcionOriginal` crudo + advertencias de total); R2 colision de dedupe en Visa sin cupon (aceptado como falso positivo excluible); R3 performance de dedupe en cuentas grandes (aceptable hoy, indice opcional diferido); R4 carrera al crear categoria "Reintegro Tarjeta" (mismo patron ya validado de "Pago Tarjeta"); **R5 pendiente de visto bueno de stakeholder**: reintegros modelados como `Ingreso + EsPagoTarjeta=true` podrian no ser contemplados por reportes historicos que asuman que "Ingreso" nunca lleva ese flag.

### Implementacion — Parte 1: reintegros M2/M5/M7
- **Application** (`ImportacionResumenDtos.cs`): `MovimientoTarjetaDto` +`DescripcionRaw`/+`EsReintegro`; `ResultadoParseoResumen` +`TotalDeclaradoPesos`/+`TotalDeclaradoDolares`/+`Advertencias`; `MovimientoPreviewItem` +`EsReintegro`; `PreviewImportacionResult` +`Advertencias`; `MovimientoImportadoDto` +`EsReintegro`.
- **Infrastructure**: `ProvinciaMastercardResumenParser` — regex de importes admite negativos, `LimpiarDescripcion` quita cupon ≥5 digitos + `NN/MM` + bloque `(PAIS,USD, X,XX)`, `TryExtraerTotalTitular`+`ValidarTotales` (advertencia si la suma parseada se aparta del total declarado). `ProvinciaVisaResumenParser` — paridad funcional. `ResumenTarjetaImporter` — normaliza a `Math.Abs`, decide rama pago/reintegro/gasto, dedupe por linea cruda, persiste reintegros como `Ingreso+EsPagoTarjeta=true`.
- **Web**: `ImportacionController` propaga `Advertencias`; `ImportarPreviewViewModel` +`Advertencias`/+`TotalReintegros`/+`MontoReintegros`, `SaldoPendiente` descuenta pagos y reintegros; `Views/Importacion/Preview.cshtml` hidden `EsReintegro` por fila, fila celeste (`table-info`) + icono `fa-rotate-left`, categoria fija "Reintegro Tarjeta", banners de advertencias y de reintegros.
- Build: OK. Pendiente al cierre: QA manual con PDF real, visto bueno de R5.

### Implementacion — Parte 2: ajustes funcionales del flujo (cuenta/fecha/USD)
1. **Cuenta destino siempre tarjeta de credito**: dropdown filtrado por `Cuenta.Tipo` que contenga "tarjeta" (texto libre, case-insensitive) — `ImportacionController.PopulateCuentas`.
2. **Periodo del resumen viene del PDF**: parser extrae `FechaCierre`/`FechaVencimiento` (Mastercard: `TryExtraerFecha("CIERRE"|"VENCIMIENTO")`; Visa: `TryExtraerFechasCabecera` parseando `CIERRE DD Mmm YY VENCIMIENTO DD Mmm YY`). El input del usuario (`PeriodoResumen`, deja de ser `[Required]`) queda como fallback opcional.
3. **Gastos USD se cargan en USD**: `MontoUsd` es fuente de verdad para lineas en dolares; pesos se calculan multiplicando por la cotizacion de `FechaVencimiento ?? FechaCierre ?? input` (nunca se confia en la columna ARS del banco para filas USD). Sin cotizacion disponible: `montoPesos=0` + advertencia global.
- Riesgos: R6 (regex de fecha no matchea → fallback a input del usuario, con log informativo), R7 (cotizacion USD ausente para la fecha de vencimiento → filas USD quedan en $0 con advertencia visible).
- Build OK, sin migracion EF. Pendiente: QA con PDFs reales Mastercard y Visa.

### Implementacion — Parte 3: reescritura del parser Visa contra PDF real
- **Hallazgo**: el parser Visa original asumia un formato (`"YY Mes DD comprobante ..."`) que **no coincidia con el PDF real** (Visa Platinum Banco Provincia) — el preview quedaba vacio para Visa. Formato real: filas `DD.MM.YY  NNNNNN[*|K]  DETALLE [Cuota NN/MM]  IMPORTE[-]`; pagos por `SU PAGO EN PESOS` (negativo); reintegros por `BONIF. CONSUMO ...` (negativo, sin sufijo de cupon); cuotas por literal `Cuota NN/MM`; cabecera `CIERRE ACTUAL: DD Mmm YY` en linea propia; total declarado en linea `Tarjeta NNNN Total Consumos de NOMBRE TOTAL_PESOS TOTAL_USD`; fin de documento `DEBITAREMOS DE SU CTA`.
- **Fix**: reescritura completa de `ProvinciaVisaResumenParser.ParsearFila` con regex nueva, deteccion de pagos/reintegros/cuotas por los patrones reales, captura de totales y fechas desde la cabecera real, limpieza de headers de pagina y separador `_`.
- **Smoke test** contra el PDF real de muestra (`0905811950.01.30-04-26.pdf`, descartado tras la prueba): `FechaCierre=2026-04-30`, `FechaVencimiento=2026-05-11`, `SaldoAnterior=2.696.925,95`, `TotalDeclaradoPesos=597.751,67`. **43 movimientos**: 5 pagos, 10 cuotas reconocidas, 26 compras del mes, 2 reintegros, 2 impuestos/intereses post-Total. Sin advertencias de inconsistencia.
- Riesgos: R8 (descripciones muy cortas entre cupon e importe podrian ser ambiguas — mitigado con regex no-greedy + importe ARS obligatorio al final), R9 (la muestra no tenia consumos en USD reales — camino USD del parser Visa queda sin confirmar contra un PDF que si los traiga).
- Build OK. Pendiente: QA manual con PDF Visa real desde la UI, validacion con PDF Visa que incluya consumos en USD.

### Implementacion — Parte 4: importes dos columnas ARS/USD + filtros de Movimientos + KPIs de dashboard
1. **Importacion**: mapeo posicional de columnas de importe del resumen Mastercard — primera columna pesos, segunda dolares; si ambas tienen valor, se persisten ambas (`ExtraerImportes` remueve primero el bloque USD `(PAIS,USD, X,XX)`). `ResumenTarjetaImporter`: pesos derivados por cotizacion **solo si falta ARS**.
2. **Movimientos**: filtros nuevos (tipo, categoria, cuenta) persistidos en Session (`DataTableRequest` +`Tipo`/+`CategoriaId`/+`CuentaId`; `Tipo=3` = Pagos/Reintegros TC via `EsPagoTarjeta=true`, incluye reintegros por diseno M5=B); resumen Ingresos/Egresos/Balance; layout responsive mobile (filtros colapsables, columnas secundarias ocultas `d-none d-md-table-cell`).
3. **Dashboards**: KPIs de proyeccion run-rate a fin de mes + compromiso mensual de cuotas vigentes (Home); comparativa vs periodo anterior equivalente, gasto promedio diario y concentracion de gasto en top categoria (ResumenGeneral).
- Riesgos: R10 (mapeo posicional ARS/USD asume el layout actual del banco — mitigado por `ValidarTotales`+advertencias), R11 (movimientos con ambas monedas del resumen no llevan `CotizacionDolar` implicita coherente — aceptado, reportes USD usan `MontoUsd` directo), R12 (filtro `Tipo=3` incluye reintegros por diseno, no es un bug).
- Build OK, sin migracion EF, sin cambios de permisos. Pendiente: QA manual segun la matriz de casos (ARS solo / USD solo / ambas columnas, filtros + Session, mobile, proyeccion Home, comparativa ResumenGeneral).

### Checklist de salida consolidado (las 4 partes)
- [x] Build verde en las 4 partes.
- [x] Sin migraciones EF en ninguna (columna `DescripcionOriginal` ya tenia longitud suficiente desde `ConstrainDescripcionOriginalLength`).
- [x] Sin cambios de permisos/policies.
- [x] Documentacion de diseño y arquitectura (M2/M5/M7, sin migracion, R1-R12) consolidada en este archivo.
- [ ] QA manual end-to-end con PDFs reales Mastercard y Visa (incluyendo un PDF Visa con consumos en USD) — pendiente.
- [ ] Visto bueno de stakeholder sobre R5 (reintegros como Ingreso+EsPagoTarjeta=true en reportes historicos) — pendiente.

---

## Etapa actual: dolar historico (2026-05-11)

### Alcance
Nueva seccion "Dolar Historico" que permite ver la cotizacion del dolar en la fecha de cada movimiento y convertir automaticamente importes en pesos a dolares al registrar movimientos.

### Cambios por capa
- **Application**: `ICotizacionService.cs` nuevo con contratos `GetCotizacionAsync(DateOnly)`, `GetUltimaCotizacionAsync()`.
- **Infrastructure**: `CotizacionService.cs` implementacion completa (146 lineas) con consulta a API de cotizacion, cache y fallback.
- **Web Controllers**: `DolarController.cs` nuevo con accion `Historico`; `MovimientosController.cs` actualizado (84 lineas nuevas) con integracion de cotizacion en Create/Edit.
- **Web Models**: `DolarHistoricoViewModel.cs` nuevo; `AbmViewModels.cs` actualizado.
- **Web Views**: `Views/Dolar/Historico.cshtml` nueva (129 lineas) con tabla de historial; `Movimientos/Create.cshtml` y `Movimientos/Edit.cshtml` actualizados; `_Layout.cshtml` con nuevo item de menu.

### Migraciones EF
Ninguna nueva en esta etapa.

### Build
OK.

### Riesgos
- `ICotizacionService` llama API externa; si la API no esta disponible se usa fallback.
- `ProvinciaVisaResumenParser.cs.new` dejado como archivo temporal (sin uso activo).

### Checklist de salida
- [x] Build OK.
- [x] Sin migraciones EF.
- [ ] QA manual: convertir monto en Create con cotizacion del dia; ver historial de cotizaciones.

---

## Etapa anterior: mejoras dashboard (M-04, M-05, M-06, M-07)

### Alcance
- M-04: marcar movimientos `Pendiente` en el Top 10 con badge y resaltar fila.
- M-05: agregar columnas "Restantes" y "Monto pendiente" en Cuotas Activas.
- M-06: agregar columna "Saldo arrastrado" y reordenar el ciclo de Deuda Tarjeta.
- M-07: nueva alerta "Crecimiento en {categoria}" cuando una categoria de egreso crecio >=30% vs periodo anterior equivalente.

### Cambios por capa
- Web Models: `ResumenGeneralViewModel.cs`
  - `TopGastoItem.Pendiente` (M-04).
  - `CuotaActivaItem.CuotasRestantes` y `MontoPendiente` computed (M-05).
  - `DeudaTarjetaItem.SaldoArrastrado` computed y comentarios sobre el ciclo (M-06).
- Web Controllers: `DashboardController.cs`
  - Top 10 setea `Pendiente` segun `EstadoMovimiento` (M-04).
  - `GenerarAlertas` recibe `totalesCatEgresos`; carga egresos del periodo anterior agrupados por categoria y emite alertas individuales con umbral 30% (M-07).
- Web Views: `Views/Dashboard/ResumenGeneral.cshtml`
  - Tabla Cuotas Activas: 2 columnas nuevas con badges/colores.
  - Tabla Deuda Tarjeta: nueva columna "Saldo arrastrado" + tfoot actualizado.
  - Tabla Top 10: badge Pendiente y fila resaltada (`table-warning`).

### Build
`run_build`: Build successful.

### Riesgos
- M-07 ejecuta una query adicional al periodo anterior (`Include(Categoria)`); aceptable para volumenes habituales pero podria cachearse si crece. Limitado defensivamente a las top 8 categorias del periodo.
- M-06 cambia el orden de columnas: comunicar en release notes.

### Pruebas minimas para QA
1. Top 10: con un movimiento egreso pendiente entre los top -> badge "Pendiente" y fila amarilla.
2. Cuotas Activas: cuota con 4/12 pagas -> "Restantes" = 8 y "Monto pendiente" = 8 * monto cuota.
3. Deuda Tarjeta: gastos mes anterior 100 con pagos 70 -> "Saldo arrastrado" = 30; pagos 120 -> -20 (verde).
4. M-07: en una categoria con 1.000 mes anterior y 1.500 mes actual -> alerta "Crecimiento en {categoria}: 50%". Si la categoria no existia antes, no debe alertar.

### Checklist de salida
- [x] Build OK.
- [x] Sin migraciones EF.
- [x] Capas respetadas (calculo en controller, computed properties en VM, render en vista).
- [ ] QA manual segun escenarios listados.

---

## Etapa anterior: cierre QA defectos remanentes (D-04, D-09, D-10)

### Alcance funcional resumido
Cierre de los defectos QA pendientes detectados en analisis previo:
- D-04: exposicion del flag `EsPagoTarjeta` en el formulario manual de movimientos.
- D-09: semantica del contador `CuotasActualizadas` en la importacion de resumen de tarjeta (en realidad nunca se actualiza la cuota; se reutiliza).
- D-10: persistencia de filtros (`dateRange`, `usd`) entre requests en `Dashboard/ResumenGeneral`.
- D-15: revisado, no requiere cambios. La regla de negocio actual (movimientos de cuota solo permiten `CambiarEstado`, no `Edit`/`Delete` individual) es correcta y ya esta implementada.

### Plan de ejecucion tecnica
1. Domain/Application: renombrar `CuotasActualizadas` -> `CuotasReutilizadas` en DTO de resultado de importacion.
2. Web ViewModels: agregar `EsPagoTarjeta` a `MovimientoFormViewModel` y renombrar `CuotasActualizadas` -> `CuotasReutilizadas` en `ImportarResumenResultadoViewModel`.
3. Infrastructure: actualizar `ResumenTarjetaImporter` para incrementar el contador renombrado.
4. Web Controllers:
   - `MovimientosController.Create/Edit`: hidratar y persistir `EsPagoTarjeta`, normalizar a `false` cuando `Tipo = Ingreso`.
   - `ImportacionController.Confirmar`: mapear el nuevo nombre.
   - `DashboardController.ResumenGeneral`: leer/escribir `dateRange` y `usd` en `Session`, detectando con `Request.Query.ContainsKey("usd")` para distinguir default del usuario.
5. Web Views:
   - `Movimientos/Create.cshtml`: checkbox `EsPagoTarjeta` visible solo cuando el formulario es de egreso.
   - `Movimientos/Edit.cshtml`: checkbox `EsPagoTarjeta` con texto de ayuda.

### Cambios por capa
- Domain: sin cambios.
- Application:
  - `VirtualWallet.Application/DTOs/ImportacionResumenDtos.cs`: `CuotasActualizadas` -> `CuotasReutilizadas` (con XML doc).
- Infrastructure:
  - `VirtualWallet.Infrastructure/Services/ResumenTarjetaImporter.cs`: dos puntos de incremento renombrados a `CuotasReutilizadas`.
- Web (Models):
  - `VirtualWallet.Web/Models/AbmViewModels.cs`: agregada propiedad `EsPagoTarjeta` con `[Display]`.
  - `VirtualWallet.Web/Models/ImportarResumenViewModel.cs`: renombrado `CuotasActualizadas` -> `CuotasReutilizadas`.
- Web (Controllers):
  - `VirtualWallet.Web/Controllers/MovimientosController.cs`: hidrata/persiste `EsPagoTarjeta` y la fuerza a `false` si `Tipo != Egreso`.
  - `VirtualWallet.Web/Controllers/ImportacionController.cs`: mapeo renombrado.
  - `VirtualWallet.Web/Controllers/DashboardController.cs`: claves `Dashboard_DateRange` y `Dashboard_Usd` en Session, recuperacion y normalizacion del rango.
- Web (Views):
  - `VirtualWallet.Web/Views/Movimientos/Create.cshtml`: checkbox condicionado a egreso.
  - `VirtualWallet.Web/Views/Movimientos/Edit.cshtml`: checkbox + ayuda.

### Migraciones EF aplicadas
Ninguna nueva en esta etapa. La migracion previa `ConstrainDescripcionOriginalLength` ya fue aplicada localmente; queda pendiente la ejecucion del script idempotente en produccion.

### Evidencia
- `run_build`: Build successful tras los cambios.
- Pruebas minimas pendientes para QA (ver mas abajo).

### Riesgos y supuestos
- Supuesto: ningun consumidor externo (reportes, exports) depende del nombre `CuotasActualizadas`. Se realizo busqueda global y no quedan referencias.
- Riesgo: si un cliente AJAX externo invocaba `Dashboard/ResumenGeneral?usd=true&dateRange=...`, el comportamiento sigue identico; solo cambia el caso "sin parametros" que ahora reutiliza la ultima seleccion.
- Supuesto: el flag `EsPagoTarjeta` para movimientos manuales solo tiene sentido en egresos; se normaliza al guardar.

### Pruebas minimas requeridas para QA
1. Crear un egreso con `Es pago de tarjeta` marcado -> verificar que en el listado se muestre badge "Pago Tarjeta" y que no sume al total de gastos del dashboard.
2. Crear un ingreso -> verificar que el checkbox no aparezca y que el flag quede en `false` aunque se manipule el form.
3. Editar un movimiento existente cambiando `EsPagoTarjeta` -> persistir y refrescar.
4. Importar un resumen de tarjeta con cuotas que ya existian -> verificar que el contador muestre el nuevo nombre `CuotasReutilizadas` y que no haya regresiones en `CuotasCreadas`.
5. Dashboard: cambiar rango y moneda, navegar a otra seccion y volver al dashboard sin querystring -> verificar que se mantienen los filtros previos.
6. Dashboard: pasar explicitamente `?usd=false` -> debe respetarse aunque la sesion tuviera `usd=true`.

### Checklist de salida para merge
- [x] Build OK.
- [x] No quedan referencias al simbolo viejo `CuotasActualizadas`.
- [x] Capas respetadas (logica de cuotas en Infrastructure, mapeo en Web).
- [x] Sin migraciones EF nuevas.
- [ ] QA manual segun pruebas minimas listadas.
- [ ] Ejecucion del script idempotente `ConstrainDescripcionOriginalLength.sql` en produccion (pendiente operativo).
