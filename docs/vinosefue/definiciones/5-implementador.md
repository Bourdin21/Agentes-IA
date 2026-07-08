# Memoria - Implementador

## Proyecto: vinosefue
## Ultima actualizacion: 2026-07-08 (2)

> Documento de referencia rapida. La memoria detallada por feature con cambios por capa, migraciones y checklists vive en:
> `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md`

---

## Features completadas (cronologia inversa)

### 2026-07-08 — Reorganizacion visual de Compras/Detalle.cshtml (header + resumen horizontal + pestanas Bootstrap, mismo criterio que Pedidos)
- Refactor puramente visual/estructural, replica del patron ya aprobado y aplicado el mismo dia en `Pedidos/Detalle.cshtml`: la pantalla de 2 columnas (col-md-8/col-md-4) pasa a header persistente (sin cambios) + tira de resumen horizontal + 3 pestanas Bootstrap 5 nativas (Detalle, Estado, Costos y pagos). Cero cambios de logica, endpoints, condicionales de negocio ni del `@section Scripts` existente (todos los ids/clases que usa el JS se preservaron, solo se movieron de lugar en el DOM).
- Tira de resumen: Costo Snapshot (siempre), Costo Real (si `TotalCostoReal.HasValue`), Diferencia (idem, mismo color condicional rojo/verde), Pagado y Saldo (misma condicion `TotalPagado > 0 || Estado != Cancelada` y mismo calculo de color/label "credito"/"Pagado" que ya existia) — Numero y Proveedor se omitieron por estar ya en el header (des-duplicacion, no perdida de dato). Fecha de generacion y Responsable pasaron a badges secundarios debajo de la tira.
- "Revertir recepcion" paso a ser una seccion `collapse` de Bootstrap colapsada por defecto dentro de la pestana Estado (mismo componente que "Mas acciones (reversion/cancelacion)" de Pedidos), en vez de una card siempre visible en el panel lateral.
- **Deviacion tecnica deliberada respecto al pedido literal:** el modal `modalRevertirRecepcion` se movio fuera del `collapse`/tab-content hacia el bloque de modales al final de la pagina (junto a `modalAgregarItems`), en vez de dejarlo textualmente "donde estaba". Motivo: un modal anidado dentro de un `.collapse` sin `.show` queda con `display:none` heredado y nunca se muestra al hacer click, aunque Bootstrap le agregue `.show` al modal via JS. El propio `Pedidos/Detalle.cshtml` de referencia ya saca sus 3 modales de reversion fuera del tab-content por la misma razon, asi que el cambio es consistente con el precedente aprobado.
- Unico archivo tocado: `Views/Compras/Detalle.cshtml` (reescritura completa, capa Web unicamente). Sin migracion EF.
- Build OK, 0 errores (mismos 10 warnings preexistentes de la solucion, ninguno nuevo).
- Verificado en runtime contra `VinoSeFue_dev`: se levanto `dotnet run` en el puerto 5015, se autentico via `curl` con cookies de sesion usando el superusuario semilla (`no-reply@olvidata.com.ar` / `Super123!` de `SeedData.cs`), y se pidieron 4 compras reales en estados distintos:
  - Id 7 — Borrador, `PuedeEditarItems=true`, sin Costo Real cargado. 200 OK. Se confirmo por grep sobre el HTML que TODOS los ids/clases usados por el JS estan presentes: `form-costos-item` (3), `input-cant-compra` (5), `input-costo-unit` (5), `input-descuento-costo` (5), `input-subtotal-costo` (6), `costo-status` (3), `totalCostoCalculado` (2), `data-subtotal-costo-readonly` (1), `modalAgregarItems` (3), `tbodyItemsDisponiblesAgregar`/`filtroPedidoAgregar`/`filtroProductoAgregar`/`btnAgregarItemsSubmit`/`contadorSeleccionAgregar`/`agregarItemsHiddenInputs` (2 c/u), `btnSubir` (3), `selectMetodoPagoCom`/`refPagoComWrapper` (2 c/u). La card+modal "Revertir recepcion" correctamente ausente (no es Recibida).
  - Id 8 — Recibida, Costo Real cargado (con Diferencia), 2 pagos registrados, `PuedeRevertirRecepcion=true`. 200 OK. `modalRevertirRecepcion`/`Motivo`/`confirmRevertir` presentes; card "Revertir recepcion" dentro del collapse (`collapseRevertirRecepcion` x3: id, data-bs-target, aria-controls).
  - Id 4 — Recibida, Costo Real cargado, sin pagos. 200 OK, mismas verificaciones que id 8.
  - Id 5 — Borrador con Costo Real ya cargado (caso borde: Diferencia se muestra igual aunque no sea Recibida, coherente con la condicion original `TotalCostoReal.HasValue` sin atar al estado). 200 OK.
  - En las 4 paginas: 0 matches de patrones de excepcion (`InvalidOperationException`, `NullReferenceException`, "unhandled exception", "Stack Trace"); tira "Resumen" presente (2 matches: header de card + label); las 3 pestanas (`tab-detalle-btn`/`tab-estado-btn`/`tab-costos-btn`) presentes; 0 matches de `col-md-8`/`col-md-4` residual (confirma eliminacion completa del layout de 2 columnas).
  - Solo se hicieron requests GET (login + navegacion), sin escrituras a la DB. Proceso de `dotnet run` detenido al finalizar (`Stop-Process`), cookies/HTML descargado de la sesion de prueba borrados de `/tmp`.
- Riesgos: QA manual de clicks de pestanas/collapse/modal en navegador real (no automatizado por el estudio) queda pendiente — ver pruebas minimas abajo.

### Pruebas minimas para QA — Compras/Detalle reorganizado
1. Abrir una compra en Borrador con `PuedeEditarItems=true`: confirmar que la tabla de items sigue siendo editable inline (cantidad/costo/descuento/subtotal con auto-save), que el boton "Agregar items" abre el modal y que el listado/filtrado dentro del modal funciona igual que antes.
2. Abrir una compra Recibida con `PuedeRevertirRecepcion=true`: click en pestana "Estado" → click en "Mas acciones (reversion)" para expandir el collapse → click en "Revertir recepcion" → confirmar que el modal se abre correctamente (era el punto de riesgo de la deviacion tecnica documentada arriba) y que el submit funciona.
3. Abrir una compra con Costo Real cargado: confirmar que la tira de resumen muestra Costo Snapshot/Costo Real/Diferencia con el color correcto (rojo si el real es mayor al snapshot, verde si es menor).
4. Recorrer las 3 pestanas (Detalle/Estado/Costos y pagos) en al menos 2 compras de distinto estado, confirmando que ningun dato que antes era visible desaparecio (solo cambio de ubicacion).
5. Verificar en una compra Cancelada que las cards "Cargar costo real" y "Pagos al proveedor" no aparecen (condicion preexistente `Estado != Cancelada`, sin cambios).

### 2026-07-08 — Fix: excepcion 500 en Compras/Detalle por .Contains() sobre List<string> (provider MySql.EntityFrameworkCore)
- Bug reportado: `Compras/Detalle` de una compra sin pagos tiraba `InvalidOperationException: Expression '@userIds' in the SQL tree does not have a type mapping assigned` al resolver los nombres de usuarios que registraron pagos (`ComprasController.Detalle`, query `_context.Users.Where(u => userIds.Contains(u.Id))` con `userIds` vacio).
- **Diagnostico ampliado en runtime** (no se detuvo en el diagnostico original): el mismo error tambien ocurre con `userIds` NO vacio — se reprodujo con una compra real con 2 pagos. El problema no es especifico de listas vacias: el provider `MySql.EntityFrameworkCore` 10.0.1 (EF Core 10.0.2, no es Pomelo) no puede asignar type mapping a un parametro `List<string>` traducido a SQL via `.Contains()`, para cualquier tamaño.
- Fix: se evita que el `.Contains()` sobre `List<string>` llegue a traducirse a SQL. Se trae la proyeccion completa de `Users` (tabla chica, 5 filas en dev — app interna de staff) con `.Select(...).ToListAsync()` y se filtra/arma el diccionario en memoria con LINQ-to-Objects. Se mantiene el guard de `userIds.Count == 0` como fast-path (evita el round-trip a DB cuando no hay pagos).
- Unico archivo tocado: `VinoSeFue.Web/Controllers/ComprasController.cs` (metodo `Detalle`). Sin migracion EF.
- Build OK, 0 errores (0 warnings nuevos). Verificado en runtime contra `VinoSeFue_dev`: compra sin pagos (id 8) → 200 OK ("Sin pagos registrados"); compra con 2 pagos (id 4) → 200 OK (antes tiraba 500 tambien, con el fix original de solo-guard-vacio). Cruzado contra DB: los 2 pagos de la compra 4 fueron creados por "Super Usuario", confirmado via join directo a `AspNetUsers`.
- Riesgo: `.Contains()` sobre listas de `string` en otros puntos del código (no tocados en este fix) podría tener el mismo problema si el provider se comporta igual — los demás usos relevados usan `int` (`itemIds`, `ids`, `productoIdIds`), no `string`, por lo que no deberían estar afectados, pero no se auditó exhaustivamente.
- Detalle completo en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md` (seccion "Fix: excepcion 500 en Compras/Detalle...").

### 2026-07-08 — Reorganizacion visual de Pedidos/Detalle.cshtml (header + resumen horizontal + pestanas Bootstrap)
- Refactor puramente visual/estructural aprobado via mockup: la pantalla de 2 columnas con ~9 cards sueltas pasa a header persistente (sin cambios) + tira de resumen horizontal compacta + 4 pestanas Bootstrap 5 nativas (Detalle, Estado, Pagos, Historial). Cero cambios de logica, endpoints, condicionales de negocio ni del `@section Scripts` (todos los ids/clases que usa el JS existente se preservaron, solo se movieron de lugar en el DOM).
- "Revertir operacion" paso a ser una seccion `collapse` de Bootstrap colapsada por defecto dentro de la pestana Estado, en vez de una card siempre visible.
- Unico archivo tocado: `Views/Pedidos/Detalle.cshtml` (reescritura completa, capa Web unicamente). Sin migracion EF.
- Build OK, 0 errores. Verificado en runtime contra dev DB: 4 pedidos reales (Cancelado/En preparacion/Confirmado x2) devuelven 200 OK; se creo un pedido Borrador sintetico (eliminado al finalizar) para verificar las cards exclusivas de ese estado (Agregar stock propio, Agregar item rapido, Observaciones editable) — tambien 200 OK, sin excepcion de Razor.
- Detalle completo en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md` (seccion "Reorganizacion visual de Pedidos/Detalle.cshtml").

### 2026-07-08 — Fix: confirmar pedido pisaba precios editados en Borrador + inputs seguian editables post-confirmacion
- Bug del cliente en `Pedidos/Detalle`: al editar precio/descuento/subtotal en Borrador y confirmar, los valores volvian al precio de catalogo y los inputs seguian editables en vez de pasar a solo lectura.
- 3 fixes en `PedidoService.cs`: (1) `ConfirmarAsync` ya no pisa `PrecioUnitVentaSnapshot`/`SubtotalVenta` desde el catalogo (solo costo se sigue refrescando); (2) `EstadosEditables` pasa de `[Borrador, Confirmado, EnPreparacion]` a `[Borrador]` unicamente (decision explicita del cliente: solo lectura sin excepcion desde Confirmado); (3) `ActualizarCantidadItemAsync` recalcula `SubtotalVenta` respetando el descuento (antes lo ignoraba), con la misma formula que el JS de la vista.
- Unico archivo tocado: `PedidoService.cs`. Sin cambios de Web/vista (la vista ya derivaba de `PuedeEditarItems`/`EstaEditable`). Sin migracion EF.
- Caso borde: 2 ramas de codigo quedan inalcanzables (no se tocaron, no era el foco): ajuste de stock propio post-Borrador en `ActualizarCantidadItemAsync`, y `AplicarEfectosEdicionPostConfirmacionAsync` (ahora siempre retorna null).
- Build OK, 0 errores. Probado en runtime contra dev DB con harness de consola descartable (datos sinteticos revertidos al final): valores de venta identicos antes/despues de confirmar, `PuedeEditarItems=False` post-confirmacion, y los 4 endpoints de edicion (ActualizarCantidad/ActualizarPreciosItem/EliminarItem) devuelven error server-side sobre pedido Confirmado.
- Detalle completo en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md` (seccion "Fix: Confirmar pedido pisaba precios editados en Borrador...").

### 2026-07-03 (ajuste post-revision cliente, 3ra vuelta) — Simplificacion de Reportes/DeudaProveedor y Reportes/Riesgo
- Decision del cliente sobre el pendiente que QA marco (columna de pago al proveedor en $0 hardcodeado en ambos reportes): sacar esa dimension en vez de aproximarla, enlazando al ledger nuevo (`Proveedor/CuentaCorriente`) como fuente de verdad.
- **`Reportes/DeudaProveedor`**: pasa a ser listado puro de compras facturadas (Compra, Pedido(s), Cliente(s), Deuda Base, Fecha). Se sacaron `TotalPagadoProveedor`/`SaldoPendiente`/`EstadoPago` del DTO y el filtro `estadoPago` del controller/vista. Se agrego boton "Ver saldo real del proveedor" con link a `Proveedor/CuentaCorriente`.
- **`Reportes/Riesgo`**: se saco la clasificacion de 2 ejes con el proveedor (ya no calculable de forma confiable). **Redefinicion de "riesgo"** (sin inventar reglas nuevas no discutidas, siguiendo instruccion explicita del cliente de "dejarlo simple" ante la ambiguedad): pedido activo con saldo pendiente de cobro del cliente (`SaldoCliente > 0`). Se agrego el saldo GENERAL del proveedor como dato de contexto en la cabecera (tarjeta, no por fila), con link a `Proveedor/CuentaCorriente`. Se saco el filtro `tipoRiesgo` (sin opciones validas que ofrecer).
- Capas: Application (DTOs, interfaz), Infrastructure (`ReporteService`), Web (controller, viewmodels, 2 vistas reescritas + copy actualizado en `Reportes/Index.cshtml`). Sin cambios de Domain ni migraciones EF.
- Build OK. Smoke test runtime con datos reales: ambos reportes 200 OK, saldo del proveedor en la tarjeta de Riesgo coincide exactamente con `Proveedor/CuentaCorriente`.
- Detalle completo en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md` (seccion "Ajuste 2026-07-03 (mismo dia, 3ra vuelta)").

### 2026-07-03 (ajuste post-revision cliente) — Fix orfandad de items al cancelar/eliminar + recalculo de costo al editar cantidad
- El cliente reviso los riesgos residuales del feature de abajo y pidio corregir 2 antes de QA (no quedan como defecto catalogado).
- **Fix 1:** cancelar un Pedido o eliminar un item ahora chequea si el item esta vinculado a una Compra activa: si la Compra sigue en `Borrador`, se desvincula automaticamente y se recalcula el `TotalCostoSnapshot`; si ya esta `Generada` o posterior (facturada), se **bloquea** la cancelacion/eliminacion con mensaje claro ("Quitalo de la compra primero o contacta a administracion").
- **Fix 2:** el helper compartido `RecalcularSnapshotComprasVinculadasAsync` ahora solo actua si la Compra vinculada sigue en `Borrador` (antes recalculaba sin condicion); se agrego su uso en `ActualizarCantidadItemAsync`, `AgregarItemAsync` y `AgregarItemsBatchAsync` (ramas de merge de item existente).
- Unico archivo tocado: `PedidoService.cs` (sin cambios de Domain/Application/Web ni migraciones nuevas).
- Build OK. Probado en runtime contra datos de dev (con datos sinteticos temporales, revertidos al finalizar): bloqueo y desvinculacion verificados tanto para cancelar como para eliminar item, y recalculo de costo verificado para edicion de cantidad.
- 2 de los riesgos residuales del feature anterior quedan resueltos (ver detalle en memoria completa). El resto de riesgos residuales no cambia.
- Detalle completo en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md` (seccion "Ajuste 2026-07-03 (mismo dia, post-revision del cliente)").

### 2026-07-03 — Compras al proveedor: desacople total de Pedido + ledger unico de cuenta corriente del proveedor
- Vinculo Compra-Item pasa de nivel-Pedido a nivel-Item (`PedidoItem.CompraProveedorId`, FK directa). Se elimina `Pedido.CompraProveedorId`.
- Nueva entidad `MovimientoCCProveedor` + enum `OrigenTipoMovimientoProveedor` (Factura/NotaCredito/Pago); se elimina `PagoProveedor` y campos `TotalPagadoProveedor`/`SaldoPendienteProveedor`/`EstadoPagoProveedor` de `CompraProveedor`.
- Nuevas pantallas: `Compras/Crear` (armado manual de compra por item), `Proveedor/CuentaCorriente` (extracto ascendente con saldo acumulado, alta de Pago/NCR).
- `CompraProveedorService.CambiarEstadoAsync` ya no sincroniza estados con Pedido; postea Factura automatica en Borrador->Generada y la revierte al Cancelar (nunca genera NCR automatica).
- **Desvio documentado:** se generaron 2 migraciones EF (no 4 como pedia la arquitectura) por limitacion de tooling EF Core al generar diffs parciales; se preservo la misma propiedad de seguridad (aditivo -> verificar con script de datos -> destructivo).
- **Caso borde no contemplado en arquitectura:** el modulo "Concesion recibida del proveedor" (compra espejo) dependia de pago/deuda por compra individual — se resolvio manteniendo esos metodos con la misma firma pero reimplementados contra el ledger nuevo filtrado por CompraProveedorId.
- Build OK, 0 errores. Migraciones aplicadas y verificadas en local (conteos/sumas del backfill cuadran). Smoke test runtime OK (login + rutas clave + datos reales). Pendiente: aplicar en produccion (requiere aprobacion cliente) y QA funcional completo del flujo de escritura.
- Detalle completo en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md` (seccion "Compras al proveedor — desacople total de Pedido y ledger unico de cuenta corriente").

### 2026-05-22 — Mejoras varias (pedidos y compras)
- Ajuste en `PedidoService`; `ComprasController` y `PedidosController` con nuevas acciones.
- Vistas `Compras/Detalle.cshtml` y `Pedidos/Detalle.cshtml` expandidas con nueva funcionalidad.
- Adicion de `.github/copilot-instructions.md` al repositorio del sistema.
- Build: OK. Sin migracion EF.

### 2026-05-18 — Baja de pedidos (soft delete)
- `IPedidoService` + `PedidoService` con metodo `EliminarAsync`.
- `PedidosController` con accion Delete; vistas `Index.cshtml` y `Detalle.cshtml` con boton de baja.
- Reglas de negocio: solo Borrador o Cancelado, sin pagos activos, sin compra avanzada, sin concesion activa.
- Build: OK. Sin migracion EF.

### 2026-05-15 — Reversion estados pedido (ajuste Web final)
- `ReversionDtos.cs` actualizado; `PedidosController` endpoints `RevertirCancelacion` y `RevertirFinalizacionConcesion`; `Detalle.cshtml` con card de reversion, modales de confirmacion (motivo 15-500 + RowVersion), tabla de historial.
- Politica `RequireRevertirPedido` (SuperUsuario + Administrador).
- Build: OK. Migracion `AddReversionPedidoYHistorial` pendiente en produccion.

### 2026-05-14 — Concesiones recibidas UI + ExportService + Dashboard + deploy produccion
- `StockController` + views Stock/Index, Detalle, ConcesionesImpagas.
- `ConcesionesRecibidasController` + views Index, Detalle, Crear.
- `ReporteService` + `IReporteService` + dashboard `Home/Index` actualizado con KPIs y reporte `DeudaProveedor` (badge Concesion).
- `ExportService` e `IExportService` implementados.
- Deploy a produccion `olvidatasoft-002-site6`: scripts SQL idempotentes aplicados el 2026-05-14 12:02.
- Manual de usuario actualizado.

### 2026-05-13 — Modulo Concesion recibida del proveedor (dominio + servicios)
- Entidades: `ConcesionRecibidaProveedor`, `ConcesionRecibidaProveedorItem`, `MovimientoConcesionRecibida`.
- Enums: `EstadoConcesionRecibida` (Abierta/Liquidada/CerradaManual), `TipoMovimientoConcesion`.
- `ConcesionRecibidaService`: `CrearAsync`, `ListarAsync`, `GetAsync`, `CerrarManualAsync`, `ImputarConsumoFifoAsync`, `DevolverConsumoLifoAsync`, `RecalcularEstadoAsync`.
- Gancho en `CompraProveedorService.RegistrarPagoProveedorAsync` -> `RecalcularEstadoAsync`.
- Ganchos FIFO/LIFO en `PedidoService` (confirmar/cancelar/borrar/ajustar/revertir finalizacion).
- Migracion: `20260513182527_AddConcesionesRecibidasProveedor`.
- Numero secuencial `CON-######` via `GenerarNumeroSecuencialAsync`.
- `regresiones-manuales.yml` actualizado con nuevos REG items.

### 2026-05-12 — Descuento % costo en Compras/Detalle
- `PedidoItem.DescuentoPorcentajeCosto` (nuevo campo, precision 5,2, default 0).
- Migracion: `20260512214004_AddDescuentoPorcentajeCostoPedidoItem`.
- `ComprasController.ActualizarCostosItem` (solo Admin); recalculo JS en cliente.

### 2026-05-09 — Descuento % en items de pedido
- Migracion: `20260509232720_AddDescuentoPorcentajePedidoItem`.
- Scripts produccion generados.

### 2026-04-27 — Reversion de estados de pedido (Fases 1 y 2)
- `HistorialEstadoPedido` entidad nueva. `Pedido` con `RowVersion` + campos auditoria.
- `RevertirFinalizacionConcesionAsync` y `RevertirCancelacionAsync` con compensacion contable no destructiva.
- Migracion: `20260427152550_AddReversionPedidoYHistorial`.

### 2026-04-25 — Reversion a Borrador + edicion post-confirmacion
- `VolverABorradorAsync` idempotente (guarda: compra no Recibida).
- Edicion de items en Confirmado/EnPreparacion propaga snapshot a compra.

### 2026-04-24 — Stock propio (5 etapas)
- `ProductoPropio` entidad; `PedidoItem` dual origen.
- `IStockPropioService` con reserva/devolucion FIFO, split a proveedor, concurrencia optimista.
- `StockController` + vistas + autocomplete en pedidos.
- Migracion: `20260424211341_AddProductosPropiosYStock`.

---

## Migraciones EF (cronologia)

| Migracion | Fecha | Local | Produccion |
|---|---|---|---|
| `AddProductosPropiosYStock` | 2026-04-24 | aplicada | pendiente |
| `AddReversionPedidoYHistorial` | 2026-04-27 | aplicada | pendiente |
| `AddDescuentoPorcentajePedidoItem` | 2026-05-09 | aplicada | **aplicada 2026-05-14** |
| `AddReversionRecepcionCompraProveedor` | 2026-05-13 | aplicada | **aplicada 2026-05-14** |
| `AddConcesionesRecibidasProveedor` | 2026-05-13 | aplicada | **aplicada 2026-05-14** |
| `AddDescuentoPorcentajeCostoPedidoItem` | 2026-05-12 | aplicada | **aplicada 2026-05-14** |
| `AddCompraProveedorIdToPedidoItemAndLedger` | 2026-07-03 | aplicada | pendiente |
| `RemoveCompraProveedorIdFromPedidoAndPagoProveedor` | 2026-07-03 | aplicada | pendiente |

---

## Riesgos residuales
- `AddReversionPedidoYHistorial` y `AddProductosPropiosYStock` **pendientes en produccion** (no incluidas en el deploy del 2026-05-14).
- Las 2 migraciones del 2026-07-03 (lote "Compras al proveedor") **pendientes en produccion**: requieren correr en orden migracion 1 -> script de datos backfill -> verificar conteos -> migracion 2 (destructiva). Ver detalle en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md`.
- DEF-003 abierto: boton "Registrar pago" no bloqueado en compra espejo de concesion `CerradaManual`.
- Reportes `Reportes/DeudaProveedor` y `Reportes/Riesgo` quedan con columnas de pago al proveedor degradadas a $0 desde el 2026-07-03 (pago ya no es atribuible por compra/pedido individual) — candidatos a retirar o rediseñar en favor de `Proveedor/CuentaCorriente`.
- Tests automatizados del feature de reversion y stock propio pendientes.

## Proximos pasos
- Aplicar migraciones `AddReversionPedidoYHistorial` y `AddProductosPropiosYStock` en produccion.
- Aplicar en produccion el lote "Compras al proveedor — desacople y CC" (2 migraciones + script de datos, con aprobacion previa del cliente y backup).
- Cerrar DEF-003 (bloqueo UI compra espejo concesion CerradaManual).
- QA manual del feature reversion, stock propio, y del lote "Compras al proveedor" (especialmente el flujo de escritura: Crear compra, Agregar/Quitar item, Pagos/NCR).
