# Memoria - Implementador

## Proyecto: delicias-naturales
## Ultima actualizacion: 2026-09-07

## Definiciones vigentes

### Archivos y capas modificadas
- `Controllers/VentasController.cs` (Web/Presentacion — coordinacion HTTP, sin logica de negocio nueva): metodo `ListarVentas`, bloque de paginacion (antes lineas ~157-164).

### Migraciones EF generadas
- Ninguna. Fix es puramente de forma de consulta LINQ, no toca el modelo ni el esquema.

### Riesgos residuales
- `PagosController.ListarPagos` (linea ~168) tiene el mismo patron de riesgo: Include de coleccion (`Venta.Facturas`) + WHERE complejo + OrderBy dinamico + Skip/Take en la misma query. Riesgo menor que el de Ventas (un solo Include de coleccion vs. tres), pero la causa raiz (provider EF6-MySQL discontinuado no soporta bien esa combinacion) es la misma. No se toco: fuera de alcance de este hotfix. Recomendado evaluar aplicar el mismo patron (separar IDs de pagina de entidades con Include) si aparecen sintomas similares (500 intermitente al filtrar).
- El provider `MySql.Data.EntityFramework` sigue discontinuado/sin mantenimiento activo; este tipo de bug puede reaparecer en otros listados con Include de colecciones + Skip/Take + OrderBy dinamico combinados. Vale la pena, a futuro (no en este hotfix), auditar todos los `ListarX` con DataTable del proyecto buscando el mismo patron.

### Proximos pasos pendientes
- QA funcional del fix en `/Ventas/ListarVentas` (ver pruebas minimas en trazabilidad.md / reporte de esta tarea).
- Evaluar si se quiere aplicar preventivamente el mismo patron en `PagosController.ListarPagos` (requiere decision de negocio, no autorizado en este hotfix).

---

# ITERACION 3: Editar Pago

## Estado: IMPLEMENTADO — build limpio, pendiente QA y deploy

## 0. Resultado del escaneo de reutilizacion
- `docs/patrones/catalogo.yml`: **PAT-020** ("Cancelacion de comprobante con pagos: ledger inmutable + reversion acotada a lo posteado", origen marihogar) es el principio de fondo reutilizado. No existe todavia un patron de "editar un pago" (reversion + alta enlazada). Numero libre confirmado: **PAT-023** (el mas alto usado era PAT-022; PAT-011 quedo sin usar y no se recicla).
- `docs/*/definiciones/5-implementador.md`: ningun proyecto del estudio implemento antes "Editar Pago". Lo mas cercano: `marihogar` (`MariHogar.Infrastructure/Services/VentaService.cs` — `EliminarPagoAsync`/`CancelarAsync`, y `PagoVentaService.RegistrarPagoAsync`) y `ganaderia` (`CuotaService.RegularizarAsync` variante `CobroPosterior`).
- **Decision: implementar desde cero adaptando el PATRON, no copiar codigo.** marihogar es .NET 10 / EF Core / `ServiceResult<T>` / DI por constructor / `await using`; delicias-naturales es .NET Framework 4.7.2 / MVC5 / EF6 sincronico con `db.Entry(x).State = EntityState.Deleted` y `Json(new { mensaje, tipoMensaje })`. El codigo no es portable literal. Si se reutilizaron dos decisiones concretas de marihogar: (a) buscar el movimiento de caja por FK exacta al pago y no por `OrigenId+Monto`, (b) el guard de no recalcular el estado del comprobante al tocar un pago.
- Molde interno seguido para el estilo del service nuevo: `Services/StockService.cs` (par `AplicarConsumoMix`/`RevertirConsumoMix`, mismo contexto EF6, sin transaccion propia).

## 1. Alcance implementado
Boton unico "Editar pago" (Fecha + Monto + Metodo + Motivo obligatorio) sobre el listado de pagos de una Venta, que reemplaza al viejo "Editar fecha". Toda edicion pasa por reversion + alta (ledger inmutable): el pago viejo se reversa y queda soft-deleted, y se crea uno nuevo enlazado por `PagoAnteriorId`. Se elimina `ActualizarFechaPago`.

## 2. Cambios por capa

### Datos (`Models/`, `Migrations/`)
- `Models/Pago.cs`: + `UsuarioId` (string nullable, FK a `AspNetUsers`, patron `[ForeignKey("Usuario")]` copiado de `LoginAudit`), + `Observacion` (string nullable, max 500), + `PagoAnteriorId` (int? nullable, self-FK a `pagos.Id`) con nav `PagoAnterior`.
- `Models/MovimientoCaja.cs`: + `PagoId` (int? nullable, FK a `pagos.Id`) con nav `Pago`.
- **Migracion EF: `Migrations/202609071405299_AddCamposEdicionPago.cs`** (+ `.Designer.cs` + `.resx`, registrados en el csproj como `Compile`/`EmbeddedResource`). 4 `AddColumn` nullable, 3 `CreateIndex`, 3 `AddForeignKey`. Sin backfill, sin default value, sin UPDATE de datos.

### Negocio (`Services/`)
- **`Services/PagoService.cs` (nuevo)**:
  - `ReversarPago(Pago)` — extraido de `PagosController.EliminarPago`. Busca el `MovimientoCaja` por `PagoId` (FK exacta); si no hay ninguno (pagos historicos con `PagoId = NULL`), cae al fallback preexistente `VentaId + Monto + no eliminado`. Soft-delete de ese movimiento y de todos los `MovimientoCuentaCorriente` con `PagoId` del pago.
  - `RegistrarPagoInterno(venta, monto, metodoPago, fecha, usuarioId, observacion, pagoAnteriorId)` — extraido de `PagosController.RegistrarPago`, mismas validaciones y mismos textos de error. Setea `MovimientoCaja.Pago = pago` en TODA alta nueva (no solo ediciones).
  - `EditarPago(pagoId, nuevaFecha, nuevoMonto, nuevoMetodoPago, motivo, usuarioId)` — guards (existe / no eliminado / no ya reemplazado / motivo obligatorio y <= 500) → `ReversarPago` → soft-delete del viejo → `SaveChanges` intermedio (necesario para que el interceptor marque `DeletedAt` antes de releer el saldo) → `RegistrarPagoInterno` con `pagoAnteriorId`.
  - `ObtenerPagosDeVenta(ventaId)` — arma `List<PagoVentaViewModel>` con pagos vigentes + reemplazados.
  - `PagoNegocioException` — error funcional cuyo `Message` va tal cual al usuario.
- `Services/RecycleBinService.cs`: los pagos reemplazados por una edicion se excluyen del listado de la papelera y se bloquea su restauracion (ver seccion 5).

### Presentacion (`Controllers/`, `ViewModels/`, `Views/`)
- `Controllers/PagosController.cs`: `RegistrarPago` y `EliminarPago` delegan en `PagoService`; **nueva accion `EditarPago`** (`[Authorize(Roles="Administrador,Vendedor")]`, `[HttpPost]`) con `lock(_registrarPagoLock)` envolviendo reversion+alta juntas + transaccion; **eliminada `ActualizarFechaPago`**.
- `Controllers/VentasController.cs`: `Details` y `Edit (GET)` publican `ViewBag.PagosVenta` via `PagoService.ObtenerPagosDeVenta`.
- `ViewModels/PagoVentaViewModel.cs` (nuevo): fila del listado con `Observacion`, `NombreUsuario`, `Reemplazado`, `ReemplazadoPorPagoId`, `MotivoReemplazo`, `PagoAnteriorId`, `PuedeEditar`.
- `Views/Ventas/_TablaPagos.cshtml`: pasa de `List<Pago>` a `List<PagoVentaViewModel>`; nueva columna "Motivo / Usuario"; filas reemplazadas tachadas; boton "Editar pago" solo en filas vigentes.
- `Views/Ventas/_ModalEditarPago.cshtml` (nuevo): modal compartido por Details y Edit.
- `Views/Ventas/Details.cshtml` y `Edit.cshtml`: se retira el handler `editarFechaPago`, se agregan `editarPago(...)` y `enviarEdicionPago(...)`.

## 3. Decisiones tomadas donde el diseño dejaba margen
| # | Decision | Motivo |
|---|---|---|
| D1 | **1 migracion combinada** (`AddCamposEdicionPago`) en vez de 2 separadas | Autorizado explicitamente por Arquitectura seccion 3 ("Ambas se pueden aplicar como una sola migracion EF si el Implementador lo prefiere"). Un solo DDL, una sola fila de historial, mismo riesgo. |
| D2 | Tachado con `style="text-decoration: line-through;"` inline, no clase CSS | El proyecto usa **Bootstrap 4**, que no tiene utilidad de tachado (`text-decoration-line-through` es BS5). Se evito agregar CSS propio por una sola regla. |
| D3 | Al confirmar la edicion se hace `window.location.reload()`, no refresco parcial de la seccion de pagos | Es lo que hace REALMENTE `eliminarPago` hoy (el diseño asumia un refresco parcial que no existe). Ademas un refresco parcial dejaria desactualizados el saldo pendiente, el modal de Registrar Pago y el estado de la venta en el resto de la pantalla. |
| D4 | El combo de metodo del modal de edicion usa `form-control` plano, sin `drop-select2` | select2 dentro de un modal requiere `dropdownParent` y preseleccion via `.val().change()`; el select nativo se prellena directo y evita ese riesgo. El modal de Registrar Pago conserva select2 sin cambios. |
| D5 | `RegistrarPago` (alta normal) tambien setea `Pago.UsuarioId` con el usuario actual | El analisis marcaba como gap que "no queda registrado ni quien ni por que se cargo un pago". No cambia ningun comportamiento observable y cierra el gap para todos los pagos nuevos, no solo los editados. |
| D6 | En la fila del pago reemplazado se muestra el motivo del pago que lo sustituyo (`MotivoReemplazo`) | HU2 pide "el pago reemplazado se muestra tachado con su motivo visible", pero el motivo se guarda en la `Observacion` del pago NUEVO. Se resuelve en el ViewModel. |
| D7 | `EditarPago` NO bloquea por estado de la Venta (ni siquiera `Ingresada`) | Diseño seccion 1: "Se permite editar pagos de una Venta en cualquier estado". A diferencia de `RegistrarPago`, que si conserva su guard `Ingresada`. |

## 4. Desviacion funcional detectada y resuelta (importante para QA)
`RegistrarPago` tiene el guard `montoRestante <= 0` → "La venta ya se encuentra totalmente pagada.". Extraido tal cual, ese guard **rompia el caso principal de HU1**: corregir hacia abajo un pago que genero credito por sobrepago (si otros pagos ya cubren el total, `montoRestante` queda en 0 tras la reversion y el alta del pago corregido quedaba bloqueada — justo el escenario tipo venta 9444 que motivo la feature).

Resuelto asi, **sin tocar el camino de alta normal**:
- El guard ahora es `montoRestante <= 0 && !esEdicion`, donde `esEdicion = pagoAnteriorId.HasValue`. En `RegistrarPago` el comportamiento es identico al de antes.
- El calculo de excedente pasa a `Math.Max(0, monto - Math.Max(0, montoRestante))`. El clamp es un **no-op en el alta normal** (ahi el guard garantiza `montoRestante > 0`), y evita que en una edicion sobre una venta con `montoRestante` negativo el credito de cuenta corriente se infle por encima del importe realmente pagado.

## 5. Impacto en otros consumidores de `Pago` (riesgo T5 / LP-002)
Grep completo de `db.Pagos` / `.Pagos` / `MovimientosCaja` en `Controllers/`, `Services/` y `Helper/`:

| Consumidor | Decision | Motivo |
|---|---|---|
| `Services/RecycleBinService.cs` | **CORREGIDO** | Gap real: cada edicion deja un `Pago` soft-deleted, que la papelera listaba como restaurable. Restaurarlo **duplicaria el importe cobrado de la venta**. Se excluyen del listado (`GetDeletedPagos`) y se bloquea la restauracion por Id directo en `Restore` con mensaje explicito. |
| `PagosController.Index` / `ListarPagos` / `ExportarExcel` | **Sin cambios (deliberado)** | Filtran por `.Active()`, asi que los pagos reemplazados no aparecen y los vigentes se listan con su monto corregido — correcto sin tocar nada. No se agregaron columnas `Observacion`/usuario: es el listado global de pagos, no el historial de una venta, y agregar columnas obliga a agregar filtros (regla de DataTables del design system). **Pendiente menor, no bloqueante.** |
| `DashboardController` (lineas ~37, ~43, ~451) | **Sin cambios** | Usa `.Active()` + agregaciones por monto/fecha. Los pagos reemplazados quedan fuera y el vigente entra con el valor corregido. |
| `VentasController.DeleteConfirmed` | **Sin cambios** | Borra los `MovimientoCaja` por `OrigenId` (no por monto), asi que la FK nueva no lo afecta. Ademas solo opera sobre ventas `Ingresada`. |
| `PedidosController` (~347), `VentasController.ListarVentas` (~83) | **Sin cambios** | Suman solo pagos no eliminados. |
| `CajasController` | **Sin cambios** | Crea movimientos de caja no vinculados a pagos (`PagoId` queda NULL, que es lo correcto). |

## 6. Evidencia de build
- `MSBuild DeliciasNaturales.csproj /t:Rebuild /p:Configuration=Debug /p:MvcBuildViews=true` → **EXITCODE 0**, 0 errores (incluye precompilacion Razor de todas las vistas). Solo warnings preexistentes (binding redirects, TypeScript tools version, CS1685).
- **Migracion verificada aplicada contra MySQL real (base local `delicias`, MySQL 8.0.29)**: `Update` OK y columnas confirmadas por `information_schema` — `movimientoscaja.PagoId int NULL`, `pagos.UsuarioId varchar(128) NULL`, `pagos.Observacion varchar(500) NULL`, `pagos.PagoAnteriorId int NULL`. **No se toco la base de produccion.**
- Nota operativa: la base local estaba 2 migraciones atras (`FacturaDeletedBy`, `LoginAudit`); se pusieron al dia en local para poder scaffoldear.

## 7. Riesgos residuales y pendientes
- **T4 sigue abierto:** la migracion se probo contra una base local, **no contra una copia del dump de produccion**. Arquitectura lo pide explicitamente antes de aplicar en vivo (las tablas `pagos`/`movimientoscaja` tienen miles de filas y el provider EF6-MySQL es fragil).
- **Sin smoke test funcional** (regla del rol). El build limpio + la relectura del codigo son la evidencia tecnica; la verificacion funcional queda en QA.
- `PagosController.ListarPagos` sigue con el patron de riesgo de Include + Skip/Take documentado en la iteracion anterior — no se toco.
- Pendiente menor: mostrar `Observacion`/usuario en el listado global de pagos y en el export a Excel (ver seccion 5).
- Catalogo: corresponde dar de alta **PAT-023** (variante de PAT-020 para edicion de un pago) apuntando a `Services/PagoService.cs`.

## Historial de ajustes
- 2026-07-01: HOTFIX de produccion (excepcion de proceso, sin discovery/diseno/arquitectura/presupuesto previos — decision explicita del cliente para este caso puntual). Bug: 500 intermitente (`NullReferenceException` en `MySql.Data.EntityFramework.SelectStatement.AddColumn`) al filtrar `/Ventas/ListarVentas` por numero de venta. Causa raiz: 3 Include de coleccion (`Facturas`, `Pagos`, `ProductosVenta`) + WHERE complejo + OrderBy dinamico + Skip/Take en la misma IQueryable, combinacion no soportada por el provider EF6-MySQL. Fix aplicado: separar la query en dos pasos — (1) `query.Select(v => v.Id).Skip(start).Take(length)` para obtener los Ids de la pagina sin Includes de coleccion, (2) segunda query con todos los Include necesarios, filtrando por `pageIds.Contains(v.Id)`, sin Skip/Take/OrderBy dinamico, reordenada en memoria con `pageIds.IndexOf` para preservar el orden ya calculado. Build verificado con MSBuild (`DeliciasNaturales.sln`, Configuration=Debug) — exit code 0, sin errores nuevos (solo warnings preexistentes de binding redirects y TypeScript tools version). Se detecto patron identico de riesgo en `PagosController.ListarPagos` (linea ~168) — no tocado, reportado como riesgo residual.
- 2026-09-07: Iteracion 3 "Editar Pago" implementada (Analisis/Diseño/Arquitectura cerrados; Presupuesto salteado por decision de Joaquin, deuda tecnica interna). Nuevo `Services/PagoService.cs` (`ReversarPago`, `RegistrarPagoInterno`, `EditarPago`, `ObtenerPagosDeVenta`) con la logica extraida literalmente de `PagosController`; `RegistrarPago`/`EliminarPago` refactorizados para usarlo sin cambio de comportamiento; nueva accion `EditarPago` bajo `lock(_registrarPagoLock)` abarcando reversion+alta; `ActualizarFechaPago` eliminada. 1 migracion EF combinada `202609071405299_AddCamposEdicionPago` (4 columnas nullable en `pagos` y `movimientoscaja`), verificada aplicada contra MySQL local. Nuevo `ViewModels/PagoVentaViewModel.cs` y `Views/Ventas/_ModalEditarPago.cshtml`; `_TablaPagos.cshtml` reescrito para mostrar los pagos reemplazados tachados con motivo. Dos hallazgos propios fuera de lo escrito en el diseño: (1) el guard `montoRestante <= 0` heredado de `RegistrarPago` bloqueaba el caso principal de HU1 (corregir hacia abajo un sobrepago) — se hizo edit-aware sin tocar el alta normal, mas clamp del excedente a `Math.Max(0, montoRestante)`; (2) `RecycleBinService` listaba como restaurables los pagos reemplazados, lo que habria duplicado importes cobrados — se excluyen del listado y se bloquea la restauracion. Build `MvcBuildViews=true` exit code 0. Pendiente: probar la migracion contra copia del dump de produccion (riesgo T4), QA funcional, y alta de PAT-023 en el catalogo.
