# 5 - Implementador (memoria acumulativa)

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
