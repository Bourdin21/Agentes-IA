# Memoria - Implementador

## Proyecto: vinosefue
## Ultima actualizacion: 2026-07-13

> Documento de referencia rapida. La memoria detallada por feature con cambios por capa, migraciones y checklists vive en:
> `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md`

---

## Features completadas (cronologia inversa)

### 2026-07-13 (mismo dia, tarea siguiente) — Aplicacion en produccion de migracion `AddCategoriaProducto` + clasificacion inicial de los `GruposProducto` reales de prod
- Tarea acotada estrictamente a base de datos de produccion (`db_a7251f_vinoyse`), sin tocar codigo ni publicar nada al servidor web (deploy de codigo lo hace el cliente por separado).
- **Backup previo:** `mysqldump --single-transaction --no-tablespaces --routines --triggers` de las 31 tablas de produccion (el usuario de hosting compartido no tiene privilegio `PROCESS`/acceso a `SHOW EVENTS`, hubo que sacar `--tablespaces`/`--events` tras un primer intento fallido). Archivo en `C:\Users\joaco\AppData\Local\Temp\claude\c--Sistemas-Agentes-IA\9825ae3b-d196-4158-bf15-7b2e5e79a5ed\scratchpad\backups\prod_vinosefue_full_20260713_180053.sql` (32.6 MB, fuera del repo, sesion local).
- **Migracion aplicada:** `dotnet ef database update` contra prod. Confirmado antes con `migrations list` que era la UNICA pendiente real — las otras 4 que esta memoria marcaba como "pendientes" (ver correccion abajo) ya estaban aplicadas de un deploy anterior no reflejado en la memoria. Post-aplicacion: 16/16 migraciones aplicadas, 0 pendientes.
- **Hallazgo:** el seed de las 4 categorias (`Vinos/Aceites/Cervezas/Otros`) vive en `SeedData.cs` (corre al arranque de la app), NO dentro del `Up()` de la migracion EF — aplicar solo la migracion dejo `CategoriasProducto` vacia. Se insertaron las 4 filas manualmente por SQL replicando exactamente el comportamiento de `AppDbContext.SaveChangesAsync` (`CreatedAt=UTC_TIMESTAMP(6)`, `CreatedByUserId=NULL`); el seed real es idempotente (`AnyAsync` antes de insertar) asi que cuando el cliente despliegue el codigo no va a duplicar nada.
- **Grupos reales de produccion:** 134 (no los mismos 123 de dev — nombres/typos distintos, mas grupos de aceite).
- **Clasificacion corrida contra los 134 grupos reales**, misma metodologia que dev (SELECT de verificacion antes de cada UPDATE): Aceites 5, Cervezas 1, Otros 23 (0 falsos positivos en los 18 terminos), Vinos 105 (default) = 134/134, 0 sin clasificar.
- Sin migracion nueva (aplico la ya existente), sin build/tests de codigo (tarea de DB pura). Sin cambios de codigo, sin commit/push.
- Pendiente: deploy de codigo del feature completo lo hace el cliente por separado — la DB ya esta lista (schema + seed + datos clasificados) para cuando lo haga.
- Detalle completo en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md` (seccion "Aplicacion en produccion de `AddCategoriaProducto` + clasificacion inicial").

### 2026-07-13 — Feature: filtrar por categoria (Vinos/Aceites/Cervezas/Otros) al exportar el catalogo de Productos
- Diseno ya decidido con el cliente en la etapa de analisis/arquitectura del 2026-07-09 (ver `trazabilidad.md`). Escaneo de reutilizacion cross-proyecto sin coincidencias — implementado desde cero siguiendo el patron ya existente del propio proyecto para `GrupoProducto` (entidad) y `Compras/Detalle` (autosave AJAX con debounce + indicador de guardado por fila).
- Nueva entidad `CategoriaProducto` (`SoftDestroyable`, no enum de C# — mismo criterio que `GrupoProducto`) con 4 filas fijas seedeadas al arranque (Vinos/Aceites/Cervezas/Otros). `GrupoProducto.CategoriaProductoId` (FK int? nullable, `OnDelete(SetNull)`).
- `IProductoCatalogoService`/`ProductoCatalogoService`: `GetCatalogoAsync` gana `List<int>? categoriaIds` opcional (null/vacio = sin filtro, igual al historico); metodos nuevos `GetCategoriasAsync()`, `GetGruposParaClasificarAsync()`, `SetCategoriaGrupoAsync()`.
- `ProductosController`: `Index`/`ExportarExcel`/`ExportarPdf` extendidos; 2 acciones nuevas `Categorias` (GET, `RequireAdministracion`) y `SetCategoriaGrupo` (POST AJAX). Vista nueva `Productos/Categorias.cshtml` (tabla de 123 grupos, select por fila, autosave, contador "sin clasificar" en vivo, filtro texto+categoria client-side). `Productos/Index.cshtml`: link "Gestionar categorias" (Admin) + modal de exportar con 4 checkboxes de categoria (todos tildados por defecto = sin filtro).
- Migracion EF `20260713204120_AddCategoriaProducto` (aditiva, sin perdida de datos). Aplicada en local. **Pendiente en produccion.**
- Script de clasificacion inicial de los 123 `GrupoProducto` reales de dev (reglas de texto: contains "aceite"/"cerveza"/lista de terminos "Otros", default "Vinos"). Resultado verificado: Vinos 94, Aceites 5, Cervezas 1, Otros 23 = 123/123, 0 sin clasificar, **0 casos mal clasificados** (se corrio cada condicion como SELECT de verificacion antes del UPDATE — ninguna bodega matcheo por casualidad "ron"/"gin"/etc., no hizo falta correccion manual).
- Build OK, 0 errores (mismos warnings preexistentes). Verificado en runtime contra `VinoSeFue_dev` (login real via curl, superusuario semilla): `Productos/Categorias` 200 OK con 123 filas; autosave probado con ciclo completo (quitar categoria -> NULL en DB, reasignar -> persiste, categoria invalida -> rechazado sin tocar DB); export Excel con `categorias=3` (Cervezas) trae solo productos de esa categoria (15, verificado leyendo el `.xlsx` como zip); export con las 4 categorias tildadas = mismo total exacto que sin filtro (1419 productos, comportamiento historico preservado); export PDF con filtro tambien OK.
- Desvio documentado: `Productos/Categorias` usa filtrado client-side (no DataTables server-side) por ser pantalla de administracion de config con dataset chico y estable (123 filas), consistente con que `Productos/Index` (pantalla hermana) tampoco usa DataTables.
- Pendiente: aplicar migracion en produccion + correr script de clasificacion contra los grupos reales de produccion (pueden diferir de los 123 de dev) + QA manual.
- Detalle completo en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md` (seccion "Feature: filtrar por categoria...").

### 2026-07-09 — Reparacion DB dev completada (agente colgado en verificacion final) + causa raiz real del "no compila" encontrada y corregida
- El agente delegado para reparar `comprasproveedor` en `VinoSeFue_dev` (dump selectivo + backup previo) se colgo ("stalled: no progress for 600s") durante el paso final de verificacion — **el trabajo de reparacion en si ya estaba terminado**, solo no llego a documentarlo. Verificado directamente por el orquestador (sin agente, consulta MySQL directa): `CHECK TABLE comprasproveedor` -> `OK`, 9 filas presentes (ninguna perdida), `FechaUltimaReversionRecepcion` quedo `NULL` en las filas antes corruptas (se perdio ese dato puntual de auditoria de reversion, no las filas completas). `pedidos` (9), `pedidoitems` (14), `movimientosccproveedor` (9) verificados `OK`. Las 17 bases de datos de todos los proyectos del estudio siguen presentes en la instancia compartida.
- **Causa raiz real de "no me compila la aplicacion" encontrada (no relacionada a la DB):** `VinoSeFue.Web.csproj` tenia `<AspNetCoreHostingModel>` comentado (con `OutOfProcess` solo en el comentario, sin efecto), mientras que `web.config` tiene `hostingModel="OutOfProcess"` con `lockAttributes="hostingModel"` (bloqueo deliberado, requerido por el hosting compartido de produccion en site4now.net). Sin ese tag activo en el `.csproj`, cada `dotnet build`/`dotnet publish` regeneraba `web.config` con `hostingModel="InProcess"` por defecto del SDK, pisando el valor bloqueado — exactamente el flip incidental que TODAS las tareas de implementacion de esta sesion tuvieron que revertir a mano despues de cada build. Fix: se descomento y corrigio la linea a `<AspNetCoreHostingModel>OutOfProcess</AspNetCoreHostingModel>` en el `.csproj`, alineandolo con `web.config`. Verificado con un build limpio posterior: `web.config` ya NO vuelve a `InProcess`. Esta es la causa mas probable del "no compila" reportado por el cliente si su IIS Express local esta configurado para `OutOfProcess` (un mismatch de hosting model en VS suele mostrarse como fallo de build/lanzamiento, no como un error de compilacion C# tradicional).
- Archivos tocados: `VinoSeFue.Web/web.config`, `VinoSeFue.Web/VinoSeFue.Web.csproj` (ambos, cambio de configuracion, no de codigo). Sin migracion EF.
- Sin pruebas adicionales por instruccion explicita del cliente ("no corras pruebas, yo lo pruebo") — solo se confirmo `dotnet build` limpio (0 errores) y que `web.config` sostiene `OutOfProcess` tras el build.
- Pendiente para el cliente: si el build le sigue fallando despues de este fix, revisar si tiene un proceso `iisexpress.exe` o `dotnet.exe` colgado de una sesion de debug anterior bloqueando los DLLs (patron recurrente en esta sesion, ya documentado en entradas previas) — cerrar Visual Studio por completo y volver a abrir suele resolverlo.

### 2026-07-08 — Seguimiento corrupcion InnoDB `comprasproveedor`: reparacion en dev FALLIDA (crash de instancia completa, sin perdida de datos) + chequeo produccion LIMPIO
- Cliente autorizo las 2 acciones pendientes: (1) reparar `comprasproveedor` en `VinoSeFue_dev` con `ALTER TABLE ... ENGINE=InnoDB` y (2) `CHECK TABLE` de solo lectura en produccion sobre `comprasproveedor`/`movimientosccproveedor`/`pedidos`/`pedidoitems`.
- **Tarea 1 (dev) — resultado no esperado:** el `ALTER TABLE ENGINE=InnoDB` no fallo con un error SQL normal, **crasheo el proceso `mysqld` completo** (assertion failure de InnoDB en `ddl0builder.cc:978` durante el rebuild interno — la corrupcion es mas profunda de lo que el rebuild in-place puede tolerar). El servicio Windows `MySQL80` (instancia local **compartida por todos los proyectos del estudio**: ShowroomGriffin, ganaderia, virtualwallet, labipac, etc.) quedo `STOPPED`. Se reinicio (`net start MySQL80`) para diagnosticar — arranco limpio. Verificado exhaustivamente: **cero perdida de datos** (9 filas de `comprasproveedor` intactas, byte a byte iguales al baseline pre-intento; `movimientosccproveedor`/`pedidos`/`pedidoitems` de vinosefue siguen OK; sanity check en 4 bases de otros proyectos sin señales de daño). La tabla **sigue corrupta** (`CHECK TABLE` post-crash: mismo `error Corrupt`), no se reparo. Runtime confirmo comportamiento sin cambios: `Compras/Detalle` id 4 y 9 siguen dando 500 (`ArgumentOutOfRangeException`), id 6 y 8 siguen dando 200 con datos de fecha invalidos.
- **Decision:** no se reintento con un metodo mas agresivo (`innodb_force_recovery`, dump+drop+recreate) porque la opcion que el cliente autorizo explicitamente resulto no viable de una forma mucho mas severa de lo previsto (caida de instancia completa, no "riesgo de perder una fila"). Se detuvo el trabajo y se escala al cliente para decidir el siguiente paso (ver opciones en detalle completo).
- **Tarea 2 (produccion) — resultado limpio:** las 4 tablas (`comprasproveedor`, `movimientosccproveedor`, `pedidos`, `pedidoitems`) dieron `CHECK TABLE ... status OK`. Produccion no tiene la corrupcion; queda acotada a dev.
- Sin cambios de codigo, sin migracion EF — tarea puramente operativa sobre bases de datos.
- Pendiente confirmado que sigue sin resolver (no tocado, solo verificado que sigue en la memoria): rotar password de produccion expuesta en chat (`appsettings.Production.json`).
- Detalle completo (baseline, log de crash de InnoDB, verificacion post-crash, opciones de reparacion no ejecutadas) en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md` (seccion "Seguimiento corrupcion InnoDB `comprasproveedor`: intento de reparacion en dev...").

### 2026-07-08 — Fix Compras confirmadas ("Generada") seguian editables (Bug A) + hallazgo de corrupcion InnoDB en `comprasproveedor` (Bug B, NO es bug de codigo)
- **Bug A (fix aplicado):** `PuedeEditarItems`/`PuedeEditarCostos` en `CompraProveedorViewModels.cs` permitian editar items/costos en estado "Generada" (confirmada) ademas de Borrador — se acotaron ambos a solo `Borrador`, mismo criterio que Pedidos. Se auditaron los endpoints server-side y se encontro el mismo bug replicado en 2 de 3: `EstadosEditablesItems` en `CompraProveedorService.cs` (usado por `AgregarItemsAsync`/`QuitarItemAsync`) y el guard de `PedidoService.ActualizarCostosItemAsync` (usado por `ComprasController.ActualizarCostosItem(Json)`) tambien aceptaban `Generada` — corregidos ambos a solo `Borrador` (defensa en profundidad real, no solo ocultar el input). 3 archivos tocados: `CompraProveedorViewModels.cs`, `CompraProveedorService.cs`, `PedidoService.cs`. Sin migracion EF.
- **Bug B (investigado a fondo, NO requirio fix de codigo):** el `ArgumentOutOfRangeException: Hour, Minute, and Second parameters describe an un-representable DateTime` reportado al revertir recepcion se reprodujo con stack trace real (`MySql.Data.Types.MySqlDateTime.GetDateTime()` en `CompraProveedorService.GetByIdAsync:77`). Investigacion exhaustiva (incluyendo captura de la sentencia SQL real via `general_log` de MySQL y reescritura manual del mismo UPDATE desde el cliente nativo `mysql.exe`, bypaseando el driver .NET) descarto codigo de la app, del driver `MySql.EntityFrameworkCore`/`MySql.Data` y de EF Core. `CHECK TABLE comprasproveedor` en `VinoSeFue_dev` confirmo la causa raiz real: **el indice PRIMARY de InnoDB de esa tabla esta fisicamente corrupto** (`InnoDB: The B-tree of index PRIMARY is corrupted`, `error Corrupt`). Otras tablas relacionadas (`movimientosccproveedor`, `pedidos`, `pedidoitems`) estan OK — corrupcion acotada a `comprasproveedor`. No se toco el dato corrupto (columna `FechaUltimaReversionRecepcion` de las filas 4, 6, 8, 9) sin autorizacion previa, segun instruccion explicita de la tarea. Queda pendiente decidir: reparar la tabla en dev (`ALTER TABLE ... ENGINE=InnoDB` o dump/restore) y correr `CHECK TABLE` (solo lectura, seguro) contra produccion para descartar la misma corrupcion ahi.
- Build OK, 0 errores (mismos warnings preexistentes). Verificado en runtime contra `VinoSeFue_dev`: compra Borrador con items sigue editable; compra Generada/EnPreparacion con items renderiza solo lectura (0 inputs editables); POST directo a `ActualizarCostosItemJson`/`QuitarItem` sobre compras no-Borrador rechazado server-side con mensaje claro, sin cambios en DB.
- Detalle completo (incluye toda la cadena de evidencia de la investigacion del Bug B) en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md` (seccion "Fix: Compras confirmadas...").

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
| `AddProductosPropiosYStock` | 2026-04-24 | aplicada | **aplicada** (confirmado 2026-07-13, deploy anterior no reflejado en esta memoria) |
| `AddReversionPedidoYHistorial` | 2026-04-27 | aplicada | **aplicada** (confirmado 2026-07-13, idem) |
| `AddDescuentoPorcentajePedidoItem` | 2026-05-09 | aplicada | **aplicada 2026-05-14** |
| `AddReversionRecepcionCompraProveedor` | 2026-05-13 | aplicada | **aplicada 2026-05-14** |
| `AddConcesionesRecibidasProveedor` | 2026-05-13 | aplicada | **aplicada 2026-05-14** |
| `AddDescuentoPorcentajeCostoPedidoItem` | 2026-05-12 | aplicada | **aplicada 2026-05-14** |
| `AddCompraProveedorIdToPedidoItemAndLedger` | 2026-07-03 | aplicada | **aplicada** (confirmado 2026-07-13, deploy anterior no reflejado en esta memoria) |
| `RemoveCompraProveedorIdFromPedidoAndPagoProveedor` | 2026-07-03 | aplicada | **aplicada** (confirmado 2026-07-13, idem) |
| `AddCantidadCompraAPedidoItem` | 2026-07-03 | aplicada | **aplicada** (confirmado 2026-07-13, idem) |
| `AddCategoriaProducto` | 2026-07-13 | aplicada | **aplicada 2026-07-13** (mismo dia, tarea de DB en produccion) |

---

## Riesgos residuales
- **ACTUALIZADO (2026-07-08): corrupcion InnoDB en `comprasproveedor` de `VinoSeFue_dev` SIGUE SIN REPARAR** (indice PRIMARY corrupto, `CHECK TABLE` en estado `error Corrupt`). El metodo autorizado por el cliente para repararla (`ALTER TABLE ... ENGINE=InnoDB`) se intento y **crasheo la instancia completa de MySQL local** (assertion failure de InnoDB, no un error SQL recuperable) — se verifico cero perdida de datos, pero la tabla quedo exactamente igual de corrupta que antes. Filas 4 y 9 siguen dando 500 (`ArgumentOutOfRangeException`) al leerlas via la app; filas 6 y 8 se leen pero con `FechaUltimaReversionRecepcion` invalida. **Requiere nueva decision del cliente** sobre como seguir (opciones: dump selectivo + recrear tabla con perdida de esas 4 filas de fecha reversion / `innodb_force_recovery` mas invasivo / dejarla corrupta en dev por ahora). **Produccion confirmada LIMPIA** (`CHECK TABLE` OK en las 4 tablas: `comprasproveedor`, `movimientosccproveedor`, `pedidos`, `pedidoitems`) — el problema esta acotado a dev. Ver detalle en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\5-implementador.md`.
- ~~`AddReversionPedidoYHistorial` y `AddProductosPropiosYStock` pendientes en produccion~~ **CORREGIDO 2026-07-13**: `dotnet ef migrations list` real contra prod confirmo que ya estaban aplicadas (deploy anterior del cliente no reflejado en esta memoria).
- ~~Las 2 migraciones del 2026-07-03 (lote "Compras al proveedor") pendientes en produccion~~ **CORREGIDO 2026-07-13**: idem, ya estaban aplicadas (junto con `AddCantidadCompraAPedidoItem`, tambien del 2026-07-03).
- DEF-003 abierto: boton "Registrar pago" no bloqueado en compra espejo de concesion `CerradaManual`.
- Reportes `Reportes/DeudaProveedor` y `Reportes/Riesgo` quedan con columnas de pago al proveedor degradadas a $0 desde el 2026-07-03 (pago ya no es atribuible por compra/pedido individual) — candidatos a retirar o rediseñar en favor de `Proveedor/CuentaCorriente`.
- Tests automatizados del feature de reversion y stock propio pendientes.

## Proximos pasos
- ~~Aplicar en produccion la migracion `AddCategoriaProducto` + correr el script de clasificacion~~ **HECHO 2026-07-13** (ver entrada de arriba). Pendiente: el cliente todavia tiene que desplegar el codigo del feature (controller/vistas) — la DB ya esta lista.
- Decidir con el cliente el siguiente paso para reparar `comprasproveedor` en dev (el metodo autorizado, `ALTER TABLE ENGINE=InnoDB`, crasheo la instancia y no reparo nada — ver riesgo residual arriba).
- Recordarle al cliente el pendiente viejo de rotar el password de produccion expuesto en chat (`appsettings.Production.json`) — sigue apareciendo en memoria, no gestionado por el estudio.
- ~~Aplicar migraciones `AddReversionPedidoYHistorial` y `AddProductosPropiosYStock` en produccion~~ / ~~Aplicar en produccion el lote "Compras al proveedor — desacople y CC"~~ **YA NO APLICA** — confirmado 2026-07-13 que las 5 migraciones (`AddProductosPropiosYStock`, `AddReversionPedidoYHistorial`, `AddCompraProveedorIdToPedidoItemAndLedger`, `RemoveCompraProveedorIdFromPedidoAndPagoProveedor`, `AddCantidadCompraAPedidoItem`) ya estaban aplicadas en produccion de un deploy anterior no reflejado en esta memoria.
- Cerrar DEF-003 (bloqueo UI compra espejo concesion CerradaManual).
- QA manual del feature reversion, stock propio, y del lote "Compras al proveedor" (especialmente el flujo de escritura: Crear compra, Agregar/Quitar item, Pagos/NCR) — dado que las migraciones ya estaban aplicadas en produccion, confirmar con el cliente si el codigo de estos features tambien esta desplegado y en uso.
