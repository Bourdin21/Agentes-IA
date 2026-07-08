# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

> Nota: la documentacion detallada por feature vive en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\`. Este archivo registra el log cronologico de alto nivel.

### 2026-07-08 - implementador-dotnet (fix: excepcion 500 en Compras/Detalle por .Contains() sobre List<string>)
- Etapa: Implementacion — bug ya diagnosticado entregado a la tarea: `Compras/Detalle` de una compra sin pagos tiraba `InvalidOperationException: ... does not have a type mapping assigned` al resolver nombres de usuarios que registraron pagos, atribuido a `userIds` vacio en un `.Where(u => userIds.Contains(u.Id))`.
- Cambio: se aplico primero el fix sugerido (guard de lista vacia) y se verifico en runtime contra `VinoSeFue_dev` con dos casos reales (compra sin pagos id 8, compra con 2 pagos id 4). El guard resolvio el caso vacio, pero la compra CON pagos siguio tirando el mismo 500 — se amplio el diagnostico: el error no es especifico de listas vacias, el provider `MySql.EntityFrameworkCore` 10.0.1 (EF Core 10.0.2; el diagnostico original lo nombraba mal como "Pomelo") no puede asignar type mapping a un parametro `List<string>` traducido a SQL via `.Contains()`, para ningun tamaño de lista. Fix final: se trae la proyeccion completa de `Users` (tabla chica, 5 filas en dev) a memoria y se filtra/arma el diccionario con LINQ-to-Objects, evitando que el `.Contains()` sobre `List<string>` llegue a traducirse a SQL. Unico archivo tocado: `ComprasController.cs` (metodo `Detalle`).
- Motivo: bug reportado por el cliente, con diagnostico inicial parcial (cubria solo el caso mas comun/vacio) — se detecto en verificacion runtime que el diagnostico entregado no cubria el caso con pagos, y se corrigio el alcance del fix antes de cerrar la tarea en vez de entregar una solucion incompleta.
- Impacto en capas: Web unicamente (`ComprasController.cs`). Sin migracion EF.
- Evidencia: `dotnet build` sobre la solucion completa — 0 errores, 0 warnings nuevos (se corrigio tambien un warning de nulabilidad CS8619 surgido del cambio de tipo). Runtime contra `VinoSeFue_dev`: compra sin pagos (id 8) 200 OK; compra con 2 pagos (id 4) 200 OK (antes del fix final tiraba 500 igual que la vacia). Cruce contra DB confirmo que los 2 pagos de la compra 4 fueron creados por "Super Usuario" via join a `AspNetUsers`, validando que el diccionario en memoria resuelve el usuario correcto.
- Riesgos/supuestos: no se audito exhaustivamente si otros `.Contains()` sobre `List<string>` en el resto del codigo comparten el mismo bug del provider — los demas usos relevados son sobre `List<int>` (no afectados). `Detalle.cshtml` no renderiza `CreadoPorNombre` en ninguna columna todavia (campo del ViewModel sin UI), por lo que la verificacion del caso con pagos se hizo por cruce directo a la DB en vez de inspeccion visual del HTML. QA manual pendiente (ver pruebas minimas en `5-implementador.md`).

### 2026-07-08 - implementador-dotnet (reorganizacion visual de Pedidos/Detalle.cshtml: header + resumen horizontal + pestanas)
- Etapa: Implementacion — mockup interactivo aprobado por el cliente que reagrupa `Pedidos/Detalle` (hoy 2 columnas con ~9 cards sueltas, estado/acciones repartidos en 4 lugares sin conexion) en header persistente + tira de resumen horizontal compacta + 4 pestanas Bootstrap 5 nativas (Detalle, Estado, Pagos, Historial).
- Cambio: reescritura completa de `Views/Pedidos/Detalle.cshtml` — refactor puramente visual/estructural, sin tocar ningun `asp-action`, condicional de negocio, id/clase referenciado por el JS de `@section Scripts`, ni el propio `<script>` (no hizo falta tocarlo, los elementos solo cambiaron de contenedor en el DOM). La card "Resumen" (tabla vertical) se reemplazo por una tira horizontal con Items/Total/Pagado/Saldo/Creado y badges secundarios (Concesion/Confirmado/Cierre concesion/Compra) sin perder ningun dato. "Revertir operacion" paso a un `collapse` de Bootstrap colapsado por defecto. Los 3 modales de reversion + el modal de editar pago quedaron en su ubicacion original al final de la pagina.
- Motivo: pedido explicito del cliente via mockup ya aprobado, con toda la estructura objetivo detallada de antemano (no requirio discovery adicional).
- Impacto en capas: Web unicamente (`Detalle.cshtml`). Sin cambios en Controllers/Services/ViewModels/Domain. Sin migracion EF.
- Evidencia: `dotnet build` sobre la solucion completa — 0 errores. Se levanto el sitio localmente (dev DB `VinoSeFue_dev`) y se verifico renderizado sin excepcion de Razor: 4 pedidos reales en estados Cancelado/En preparacion/Confirmado (x2) devuelven 200 OK; no existia ningun pedido Borrador en dev, asi que se creo uno sintetico via `Pedidos/Nuevo` para verificar las cards exclusivas de ese estado (Agregar stock propio, Agregar item rapido, Observaciones editable, collapse de Revertir operacion) — 200 OK, y se elimino fisicamente al finalizar (verificado 404 post-eliminacion).
- Riesgos/supuestos: QA manual de clicks de pestanas/collapse/modales en navegador real queda pendiente (el estudio no automatiza pruebas de UI). Los campos "Numero/Cliente/Estado" de la vieja tabla de Resumen se omitieron de la tira horizontal por estar ya visibles en el header persistente (no es perdida de dato, es des-duplicacion); ver detalle completo y las 5 pruebas minimas sugeridas para QA en `5-implementador.md`.

### 2026-07-08 - implementador-dotnet (fix: confirmar pedido pisaba precios editados + inputs no pasaban a solo lectura)
- Etapa: Implementacion — bug reportado por el cliente en `Pedidos/Detalle`: al editar precio/descuento/subtotal de un item en Borrador y confirmar el pedido, los valores volvian al precio de catalogo (se perdia la edicion) y los inputs seguian editables cuando deberian pasar a solo lectura.
- Cambio: 3 fixes en `VinoSeFue.Infrastructure/Services/PedidoService.cs` (unico archivo tocado). (1) `ConfirmarAsync` deja de pisar `PrecioUnitVentaSnapshot`/`SubtotalVenta` con el precio vigente del catalogo al congelar snapshots — el costo si se sigue refrescando igual que antes. (2) `EstadosEditables` pasa de `[Borrador, Confirmado, EnPreparacion]` a `[Borrador]` unicamente, por pedido explicito del cliente de que precio/descuento/subtotal/cantidad queden de solo lectura sin excepcion una vez confirmado (esto tambien hace que `PuedeEditarItems` en la vista sea `false` fuera de Borrador, sin tocar el `.cshtml`). (3) `ActualizarCantidadItemAsync` recalcula `SubtotalVenta` respetando `DescuentoPorcentaje` (antes lo ignoraba al cambiar cantidad), usando la misma formula que el JS de la vista (`recalcSubtotalForm`).
- Motivo: pedido explicito del cliente, con diagnostico de causa raiz ya confirmado de antemano (no se re-investigo).
- Impacto en capas: Infrastructure (Service) unicamente. Sin cambios en Web/Domain/Application. Sin migracion EF.
- Caso borde detectado (no tocado, no era el foco): al restringir `EstadosEditables` a solo Borrador, 2 ramas de codigo quedan inalcanzables — el ajuste de stock propio post-Borrador dentro de `ActualizarCantidadItemAsync`, y `AplicarEfectosEdicionPostConfirmacionAsync` (su guard de entrada ahora siempre es verdadero, retorna `null` siempre). Quedan como candidatos a limpieza cosmetica futura, no eliminados en este fix.
- Evidencia: `dotnet build` sobre la solucion completa — 0 errores. Prueba runtime contra MySQL dev (`VinoSeFue_dev`) con un harness de consola descartable (fuera del repo) que ejercita el flujo real via la interfaz publica de `PedidoService` (no mocks): item editado en Borrador (precio 3935.00, descuento 15%, subtotal 10265.22) queda identico tras `ConfirmarAsync`; `GetCapacidadesEdicionAsync` devuelve `PuedeEditarItems=False` post-confirmacion; los 4 endpoints de edicion (`ActualizarCantidad`, `ActualizarPreciosItem`, `EliminarItem`) rechazan la operacion sobre un pedido Confirmado con el mensaje de bloqueo esperado. Datos sinteticos (pedido/items/movimiento CC) eliminados fisicamente al finalizar, verificado con `git status` sin cambios residuales fuera de `PedidoService.cs`.
- Riesgos/supuestos: se asume que el cliente quiere cero excepciones a "Confirmado en adelante = solo lectura", segun lo pedido explicitamente. QA manual end-to-end en la vista (no solo el service) queda pendiente — ver pruebas minimas en `5-implementador.md`.

### 2026-07-03 - presupuestador (cierre de calibracion)
- Etapa: Cierre de calibracion estimado vs real — sprint "Compras al proveedor: armado manual y cuenta corriente" (no paso por Presupuesto formal, el cliente implemento directo).
- Cambio: reconstruccion retroactiva PERT de los 8 items del lote (23.8h M / 28.27h con contingencia) contra el real reportado por el cliente (4h totales, sin desglose por item). Ratio PERT-contingencia/real = 7.07x y ratio formula-vigente/real = 2.86x, ambos nuevo record del dataset del estudio (superan a Ganaderia: 5.05x y 1.93x). Se agregaron 3 rangos nuevos a "Modificacion sobre modulo existente" en `27-presupuesto-parametros.instructions.md` (refactor de vinculo/FK + migracion, ledger reutilizando patron existente, ABM manual con servicios reutilizados) y una regla de granularidad: verificar reutilizacion de patron ya resuelto en el repo ANTES de clasificar como "modulo nuevo".
- Motivo: pedido explicito del cliente de calibrar el presupuestador con este cierre real para ajustar la granularidad de presupuestos futuros.
- Impacto en capas: N/A (calibracion interna del estudio).
- Riesgos/supuestos: el real (4h) es un agregado del cliente, no desglosado por item — el reparto proporcional por item en `4-presupuestador.md` es una hipotesis no confirmada, no un dato medido. El factor de eficiencia 2.5 de la formula de facturacion NO se cambio unilateralmente (politica vigente: fijo hasta cierre de Energy Nutrition), solo se registro como evidencia adicional.

### 2026-07-03 - documentador (correccion: entrega como Google Doc en Drive, no Artifact)
- Etapa: Documentacion de alcance (cliente) — el usuario rechazo el Artifact con diseño propio ("me cambia el formato, las letras, y todo el documento") y pidio el archivo Word con el formato ya establecido en su Drive.
- Hallazgo: ya existia en Drive un `.docx` con el mismo titulo, generado a partir del markdown, con los encabezados y la lista numerada de los 5 pasos rotos en la conversion. Los documentos reales de Olvidata en Drive (ej. "Presupuesto Ulises - OlvidataSoft.docx") no tienen diseño custom, son texto plano prolijo.
- Cambio: se genero el documento como HTML semantico (sin CSS/colores propios) y se subio a Drive via `create_file` (carpeta `parentId 0AKdL2qlDPnZIUk9PVA`, mismo lugar que el resto de los documentos de Olvidata), quedando como Google Doc nativo: https://docs.google.com/document/d/1An45iVfcU_3LnQVHKpDnld_T_SFweHm-w_Lx-05iOSM/edit — verificado leyendo el archivo de vuelta que los encabezados y la numeracion sobrevivieron la conversion.
- Motivo: correccion de una instruccion previa mal aplicada (publicar todo documento a cliente como Artifact con diseño propio) — corregida en memoria del estudio.
- Impacto en capas: N/A (entregable de negocio).
- Riesgos/supuestos: el `.docx` viejo (mangled) sigue en Drive, no se borro sin permiso. El `.md` en `docs/vinosefue/` sigue siendo la fuente de contenido interna.

### 2026-07-03 - documentador (Artifact del formato oficial)
- Etapa: Documentacion de alcance (cliente) — publicacion como Artifact del resumen de sprint ya redactado en formato oficial OlvidataSoft.
- Cambio: nueva convencion permanente adoptada (guardada en memoria del estudio): todo documento a cliente se publica tambien como Artifact ademas del `.md` fuente, con diseño propio por documento (no un template fijo reutilizado). Se publico esta version para "Compras al proveedor — desacople y cuenta corriente".
- Motivo: pedido explicito del usuario de repetir el flujo de publicacion como Artifact cada vez que pida un documento para el cliente.
- Impacto en capas: N/A (entregable de negocio).
- Riesgos/supuestos: el `.md` en `docs/vinosefue/` sigue siendo la fuente de contenido versionada; el Artifact es la version publicable/compartible, en una ruta de sesion temporal.

### 2026-07-03 - documentador (formato oficial OlvidataSoft)
- Etapa: Documentacion de alcance (cliente) — regeneracion del resumen de sprint aplicando `.github/instructions/31-formato-documento-cliente.instructions.md` (formato obligatorio para documentos a cliente, estilo OlvidataSoft Julio 2026), detectado al recibir el pedido "con el nuevo formato de documentos de olvidata".
- Cambio: nuevo archivo `docs/vinosefue/resumen-sprint-compras-proveedor-2026-07.md` con wordmark, `## Sobre el proyecto`, seccion "Como funciona: armar una compra al proveedor — paso a paso" (agregada porque el sprint introdujo un flujo nuevo multi-paso), cambios entregados, beneficio, pendientes y pie de firma. Reemplaza como documento de referencia vigente a la v1 (Artifact HTML de formato libre).
- Motivo: pedido explicito del usuario de usar el nuevo formato estandar del estudio.
- Impacto en capas: N/A (entregable de negocio).
- Riesgos/supuestos: mismo contenido validado que la v1 (nada nuevo sin QA), solo cambia el envoltorio/formato.

### 2026-07-03 - documentador (nota de entrega formateada)
- Etapa: Documentacion de alcance (cliente) — a pedido explicito del usuario, se genero un documento entregable (Artifact HTML tipo nota de entrega/memo) con el mismo contenido de los 6 bloques ya aprobados (resumen, cambios, beneficio, pendientes, consideraciones, proximo paso), listo para compartir con el cliente.
- Motivo: el usuario pidio "armar documento para entregarle al cliente" via comando `/agentes-ia-documentador`.
- Impacto en capas: N/A (entregable de negocio).
- Riesgos/supuestos: el archivo fuente del Artifact vive en una ruta de scratchpad de sesion (temporal); si se necesita regenerar en otra sesion, recrear el contenido desde `7-documentador.md`.

### 2026-07-03 - documentador
- Etapa: Documentacion de alcance (cliente) — lote "Compras al proveedor — desacople y cuenta corriente"
- Cambio: resumen ejecutivo entregado al cliente cubriendo los 5 items originales + 3 rondas de ajuste post-QA (items huerfanos/recalculo de costo, simplificacion de reportes DeudaProveedor/Riesgo, incluyendo el cambio de definicion de "riesgo").
- Motivo: cierre de sprint tras QA con GO condicionado.
- Impacto en capas: N/A (documentacion de negocio, sin tecnicismos).
- Riesgos/supuestos: pendiente aplicar migraciones en produccion (requiere aprobacion + backup) y smoke test manual en navegador del circuito de escritura completo (crear compra, pagos/NCR).

### 2026-07-03 - implementador (ajuste post-revision cliente, 3ra vuelta — simplificacion de reportes)
- Etapa: Implementacion — decision del cliente sobre el pendiente marcado por QA (columna de pago al proveedor en $0 hardcodeado en `Reportes/DeudaProveedor` y `Reportes/Riesgo`): sacar esa dimension en vez de aproximarla, enlazando al ledger `MovimientoCCProveedor` (via `Proveedor/CuentaCorriente`) como fuente de verdad.
- Cambio: **`Reportes/DeudaProveedor`** pasa a ser listado puro de compras facturadas (Compra, Pedido(s), Cliente(s), Deuda Base, Fecha) — se sacaron `TotalPagadoProveedor`/`SaldoPendiente`/`EstadoPago` del DTO y el filtro `estadoPago`; se agrego boton "Ver saldo real del proveedor" con link a `Proveedor/CuentaCorriente`. **`Reportes/Riesgo`** se saco la clasificacion de 2 ejes con el proveedor; se redefinio "riesgo" (sin inventar reglas nuevas no discutidas, siguiendo instruccion explicita de "dejarlo simple" ante la ambiguedad) como: pedido activo con saldo pendiente de cobro del cliente (`SaldoCliente > 0`). Se agrego el saldo GENERAL del proveedor como dato de contexto en la cabecera (tarjeta, no por fila); se saco el filtro `tipoRiesgo`.
- Motivo: pedido explicito del cliente para resolver el pendiente de negocio antes de continuar, evitando que el reporte muestre un dato de pago al proveedor enganoso ($0 hardcodeado).
- Impacto en capas: Application (`ReporteDtos.cs`, `IReporteService.cs`), Infrastructure (`ReporteService.cs`: `GetDeudaProveedorAsync`/`GetReporteRiesgoAsync` reescritos + nuevo helper `GetSaldoActualProveedorAsync`), Web (`ReportesController.cs`, `ReporteViewModels.cs`, vistas `DeudaProveedor.cshtml`/`Riesgo.cshtml` reescritas + copy actualizado en `Reportes/Index.cshtml`). Sin cambios de Domain ni migraciones EF.
- Riesgos/supuestos: build OK (0 errores). Smoke test runtime con datos reales de dev: ambos reportes 200 OK; el saldo del proveedor mostrado en la tarjeta de `Reportes/Riesgo` coincide exactamente con el saldo real verificado en `Proveedor/CuentaCorriente`. Pendiente para Documentacion (`7-documentador.md`): comunicar al cliente el cambio de definicion de "riesgo" (antes cruzaba cliente y proveedor por pedido; ahora es unicamente "pedidos con cobro pendiente del cliente", con el saldo del proveedor como dato de contexto separado).

### 2026-07-03 - qa
- Etapa: Pruebas funcionales — lote "Compras al proveedor — desacople y cuenta corriente" (5 items + 2 fixes post-revision del cliente).
- Cambio: recorridas las 9 Historias de Usuario (HU-1..9) y 5 Criterios del analista (CU-1..5): todos PASS (1 observacion menor de copy en mensaje de concurrencia de `Compras/Crear`, no bloqueante). Maquina de estados de `Pedido` y `CompraProveedor` recorrida completa (transiciones validas e invalidas). Catalogo cross-proyecto `regresiones-manuales.yml` ejecutado (REG-001..010 aplicables PASS; KOI-*/DN-*/GAN-* N/A por proyecto). Verificacion directa contra la base `VinoSeFue_dev` (via `mysqlsh`): conteos/sumas del backfill cuadran (4 Facturas = 4 compras facturadas, 2 Pagos), confirmando ademas el caso borde marcado por el implementador.
- **2 defectos encontrados y corregidos con auto-fix** (catalogados en `docs/qa/regresiones-manuales.yml` antes del parche, ids `VSF-001` y `VSF-002`): (1) un item vinculado a una Compra `Cancelada` (remanente historico pre-migracion) bloqueaba la cancelacion/eliminacion del Pedido igual que si la compra estuviera facturada, dejando al usuario sin ninguna accion posible porque la UI no expone "Quitar item" en una compra Cancelada — corregido excluyendo tambien `Estado == Cancelada` del guard de bloqueo en `PedidoService` (`CambiarEstadoInternoAsync`/`EliminarItemAsync`); (2) una `CompraProveedor` en `Borrador` no tenia forma de cancelarse (el diccionario de transiciones validas solo permitia Borrador→Generada), pese a que el diseno aprobado define Borrador/Generada/EnPreparacion→Cancelada — corregido agregando `Cancelada` a las transiciones permitidas desde `Borrador` en `CompraProveedorService` (la logica de cancelacion ya era agnostica al estado de origen, sin necesidad de logica de negocio nueva).
- Se verifico ademas que **DEF-003** (heredado del QA de "Concesion recibida del proveedor", 2026-05-13) esta **cerrado**: doble guarda (service + UI `puedeOperar`) ya presente en el codigo vigente, sin fecha de correccion documentada previamente.
- Motivo: gate de QA obligatorio antes de habilitar Documentacion al cliente y aplicacion de migraciones en produccion.
- Impacto en capas: Infrastructure (`PedidoService.cs`, `CompraProveedorService.cs`) para los 2 auto-fixes — sin cambios de Domain/Application/Web ni migraciones EF nuevas (confirmado con `dotnet ef migrations has-pending-model-changes`).
- Riesgos/supuestos: build OK (0 errores) antes y despues de los auto-fixes. Riesgos de liberacion pendientes (no de codigo): migraciones y scripts del 2026-07-03 sin aplicar en produccion (requiere aprobacion cliente + backup); reportes `Reportes/DeudaProveedor` y `Reportes/Riesgo` con columna de pago degradada a $0 (decision de negocio pendiente: retirar o redisenar); flujo de escritura completo (Crear compra, Agregar/Quitar item, Pagos/NCR) sin ejercitar aun por navegador — se dejaron pasos de smoke manual para ejecucion del usuario. Recomendacion: **GO condicionado** (pendientes son de coordinacion/produccion y decision de negocio, no de codigo).

### 2026-07-03 - implementador (ajuste post-revision cliente, mismo dia)
- Etapa: Implementacion — correccion de 2 riesgos residuales del lote "Compras al proveedor" antes de pasar a QA (pedido explicito del cliente, no quedan catalogados como defecto).
- Cambio: **Fix 1** — cancelar un Pedido o eliminar un item ahora verifica el estado de la Compra vinculada al item: si esta en `Borrador` se desvincula automaticamente (`CompraProveedorId = null`) y se recalcula `TotalCostoSnapshot`; si esta `Generada` o posterior (ya facturada), se **bloquea** la operacion con mensaje explicito indicando el item y el numero de compra. Aplicado en `CambiarEstadoInternoAsync` (case Cancelado) y `EliminarItemAsync`. **Fix 2** — el helper `RecalcularSnapshotComprasVinculadasAsync` ahora solo recalcula si la Compra vinculada sigue en Borrador (antes lo hacia sin condicion); se agrego su uso en `ActualizarCantidadItemAsync`, `AgregarItemAsync` y `AgregarItemsBatchAsync` (ramas de merge de item existente) para que el costo de la Compra se mantenga sincronizado mientras siga editable.
- Motivo: pedido explicito del cliente tras revisar los riesgos residuales documentados en la entrada anterior del mismo dia, antes de dar luz verde a QA.
- Impacto en capas: solo Infrastructure (`PedidoService.cs`). Sin cambios de Domain, Application, Web ni migraciones EF nuevas.
- Riesgos/supuestos: 2 de los riesgos residuales de la entrada anterior quedan resueltos (item huerfano al cancelar/eliminar; recalculo de costo al editar cantidad). El resto de riesgos residuales de esa entrada no cambia. Build OK (0 errores). Probado en runtime contra los datos de dev ya backfilleados (con datos sinteticos temporales insertados y revertidos al finalizar la prueba, sin dejar residuos): verificados los 5 escenarios (bloqueo/desvinculacion al cancelar, bloqueo/desvinculacion al eliminar item, recalculo por edicion de cantidad). Caso borde detectado: items vinculados a una Compra `Cancelada` remanente del modelo pre-migracion tambien activan el bloqueo (tratado igual que "Generada+", comportamiento conservador correcto pero puede generar mensaje confuso si el admin no sabe que es un remanente historico — a revisar en QA si aparece en produccion).

### 2026-07-03 - implementador
- Etapa: Implementacion — lote "Compras al proveedor — desacople y cuenta corriente" (5 items: 2 fixes + 3 features)
- Cambio: vinculo Compra-Item via FK directa `PedidoItem.CompraProveedorId` (elimina `Pedido.CompraProveedorId`); nueva entidad `MovimientoCCProveedor` + enum `OrigenTipoMovimientoProveedor`; se elimina `PagoProveedor` y campos denormalizados de `CompraProveedor`. Nuevas pantallas `Compras/Crear` y `Proveedor/CuentaCorriente`. `CambiarEstadoAsync` ya no sincroniza Pedido<->Compra; postea Factura automatica en Borrador->Generada y la revierte al Cancelar (nunca NCR automatica). Se detecto y resolvio una dependencia no contemplada en arquitectura: el modulo "Concesion recibida del proveedor" (compra espejo) dependia de pago/deuda por compra individual — se mantuvieron esos metodos con la misma firma pero reimplementados contra el ledger nuevo.
- Motivo: implementar el alcance ya aprobado en Analisis/Diseno/Arquitectura (2026-07-03), saltando la etapa de Presupuesto por decision expresa del cliente.
- Impacto en capas: todas (Domain, Application, Infrastructure, Web). Ver detalle completo por archivo en `5-implementador.md` y en la memoria detallada del repo del sistema.
- Migraciones EF: 2 (no 4 como sugeria la arquitectura, por limitacion de tooling EF Core al generar diffs parciales — se preservo la misma propiedad de seguridad aditivo->verificar->destructivo). Aplicadas y verificadas en local (conteos y sumas del backfill coinciden). Pendientes en produccion.
- Riesgos/supuestos: reportes `DeudaProveedor` y `Riesgo` quedan con columna de pago al proveedor degradada a $0 (arquitectura solo marco `DeudaProveedor` como obsoleto, `Riesgo` no fue mencionado). Un `PedidoItem` de un pedido cancelado ya no se desvincula automaticamente de su Compra (requiere accion manual). Build OK, smoke test runtime OK con datos reales backfilleados; flujo de escritura completo (Crear compra, Agregar/Quitar item, Pagos/NCR) no probado en runtime por falta de datos de prueba disponibles — queda para QA.

### 2026-07-03 - arquitecto-mvc
- Etapa: Arquitectura tecnica — lote "Compras al proveedor — desacople y cuenta corriente"
- Cambio: vinculo Compra-Item via FK directa `PedidoItem.CompraProveedorId` (reemplaza `Pedido.CompraProveedorId`, sin tabla N:N nueva); nueva entidad `MovimientoCCProveedor` + enum `OrigenTipoMovimientoProveedor` (sin cabecera `CuentaCorrienteProveedor` porque el proveedor es unico); se elimina `PagoProveedor` y los campos `TotalPagadoProveedor`/`SaldoPendienteProveedor`/`EstadoPagoProveedor` de `CompraProveedor`. 4 migraciones EF + 2 scripts de datos (propagar CompraProveedorId a items, backfill de Factura y Pago historicos). Posteo automatico de Factura en transicion Borrador->Generada; reversion al Cancelar.
- Motivo: implementar las decisiones ya validadas por el cliente en Diseno (granularidad por item, desacople total de estados, ledger unico de proveedor).
- Impacto en capas: todas (Domain, Application, Infrastructure, Web).
- Riesgos/supuestos: migraciones 2 y 4 son destructivas (dropean columna/tabla) - requieren verificacion en staging antes de correr en produccion. Fecha de Factura backfilleada usa `FechaGeneracion` como aproximacion. Sin cambios de permisos. Cliente salta Presupuesto e implementa directo.

### 2026-07-03 - disenador-funcional
- Etapa: Diseno funcional — lote "Compras al proveedor — desacople y cuenta corriente"
- Cambio: definidas 4 pantallas (2 ajustes: Compras/Detalle, Compras/Index; 2 nuevas: Compras/Crear, Proveedor/CuentaCorriente), ViewModels, maquina de estados (Pedido sin disparadores desde Compra; CompraProveedor con transiciones que ya no propagan; nuevo ledger MovimientoCCProveedor), 9 historias de usuario con criterios de aceptacion, plan funcional en 5 etapas para Arquitectura.
- Motivo: traducir el analisis aprobado en diseno implementable.
- Impacto en capas: preliminar en las 3 (detalle en Arquitectura).
- Riesgos/supuestos: quedan 2 puntos abiertos para Arquitectura antes de Presupuesto: (1) como revertir/compensar el movimiento Factura si se cancela una Compra que ya facturo, (2) que hacer con los pagos historicos de `PagoProveedor` (migrar al ledger nuevo o convivir).

### 2026-07-03 - analista-funcional
- Etapa: Discovery + Analisis funcional — lote "Compras al proveedor — desacople y cuenta corriente" (5 items: 2 fixes + 3 features)
- Cambio: relevamiento de codigo actual (CompraProveedor, PedidoService, CompraProveedorService, PagoProveedor, CuentaCorriente/MovimientoCC de Clientes). Confirmados sin ambiguedad: fix stock propio en Compras/Detalle (excluir items EsStockPropio de la vista) y fix orden de columnas en listado de Compras (Fecha primero; orden descendente ya existe en backend).
- Motivo: pedido del cliente via imagen de extracto de cuenta corriente real del proveedor + 3 items funcionales.
- Impacto en capas: pendiente de definir en Arquitectura (bloqueado por 3 preguntas abiertas).
- Riesgos/supuestos: features 3/4/5 requieren decisiones de arquitectura funcional (granularidad de seleccion de articulos para compra manual, alcance de desacople de estados Compra/Pedido, y si Pagos/NCR de proveedor pasan a ser un ledger tipo cuenta corriente en vez de atarse 1:1 a una Compra puntual como hoy `PagoProveedor`). Gate: no se pasa a Diseno (etapa 2) para 3/4/5 hasta validacion del cliente.

### 2026-05-22 - implementador
- Etapa: Implementacion — Mejoras varias (pedidos y compras)
- Cambio: ajuste en `PedidoService`; `ComprasController` y `PedidosController` con nuevas acciones; vistas `Compras/Detalle.cshtml` y `Pedidos/Detalle.cshtml` expandidas (~75 lineas nuevas cada una). Adicion de `.github/copilot-instructions.md` al repositorio del sistema.
- Motivo: correcciones y mejoras post-entrega solicitadas por el cliente.
- Impacto en capas: Infrastructure (service), Presentacion (controllers + vistas).
- Riesgos/supuestos: sin migracion EF. Build OK.

### 2026-05-18 - implementador
- Etapa: Implementacion — Baja de pedidos (soft delete)
- Cambio: `IPedidoService` + `PedidoService` con `EliminarAsync`; `PedidosController` con accion Delete; vistas `Index.cshtml` y `Detalle.cshtml` actualizadas con boton de baja. Regla: solo pedidos en estado Borrador o Cancelado, sin pagos activos, sin compra avanzada, sin concesion activa.
- Motivo: cliente necesitaba poder eliminar pedidos erroneos en estados tempranos.
- Impacto en capas: Application (interface), Infrastructure (service), Presentacion (controller + vistas).
- Riesgos/supuestos: soft delete via `DeletedAt`. Sin migracion EF. Build OK.

### 2026-05-15 - implementador
- Etapa: Implementacion — Feature Reversion estados pedido (ajuste final)
- Cambio: `ReversionDtos.cs` actualizado; `PedidosController` y `PedidoService` ajustados; `Detalle.cshtml` actualizado con card de reversion y tabla de historial.
- Motivo: completar la integracion Web del feature de reversion (Fases 1 y 2) incluyendo politica `RequireRevertirPedido`.
- Impacto en capas: Application (DTOs), Infrastructure (service), Presentacion (controller + vista).
- Riesgos/supuestos: migracion `AddReversionPedidoYHistorial` pendiente de aplicar en produccion.

### 2026-05-14 - implementador + documentador
- Etapa: Implementacion — Concesiones recibidas UI + ExportService + Dashboard + deploy produccion
- Cambio: `StockController`, `ConcesionesRecibidasController` y vistas completadas. `ReporteService` + `IReporteService` + `DashboardViewModel` + vista `Home/Index` actualizados. `ExportService` e `IExportService` implementados. Scripts SQL idempotentes generados y aplicados en produccion (`olvidatasoft-002-site6`). Manual de usuario actualizado.
- Motivo: completar UI del modulo Concesiones Recibidas del Proveedor y hacer deploy del ciclo Mayo.
- Impacto en capas: todas.
- Riesgos/supuestos: migration `AddConcesionesRecibidasProveedor` aplicada en produccion.

### 2026-05-13 - implementador + qa
- Etapa: Implementacion + QA — Concesiones recibidas del proveedor (dominio + servicios + QA)
- Cambio: entidades `ConcesionRecibidaProveedor`, `ConcesionRecibidaProveedorItem`, `MovimientoConcesionRecibida`; enums `EstadoConcesionRecibida`, `TipoMovimientoConcesion`. `ConcesionRecibidaService` con FIFO/LIFO, maquina de estados completa, liquidacion automatica. Migracion `AddConcesionesRecibidasProveedor` generada. QA formal completado: 10/10 criterios de aceptacion PASS (1 parcial DEF-003). Catalogo de regresiones `regresiones-manuales.yml` actualizado. Reporte `DeudaProveedor` con badge Concesion.
- Motivo: nuevo modulo funcional solicitado por el cliente para gestionar mercaderia recibida en consignacion de proveedores.
- Impacto en capas: todas.
- Riesgos/supuestos: DEF-003 pendiente (boton pago bloqueado en compra espejo de concesion CerradaManual).

### 2026-05-12 - implementador
- Etapa: Implementacion — Descuento % en costo de items de compra
- Cambio: `PedidoItem.DescuentoPorcentajeCosto` nuevo campo. Migracion `AddDescuentoPorcentajeCostoPedidoItem`. `ComprasController.ActualizarCostosItem` con politica `RequireAdministracion`. Vista `Compras/Detalle` con inputs editables por fila y recalculo JS.
- Motivo: paridad de edicion de costos entre Pedidos y Compras/Detalle.
- Impacto en capas: Domain, Infrastructure (EF + service), Presentacion.
- Riesgos/supuestos: migracion aplicada local; pendiente produccion (incluida en deploy 2026-05-14).

### 2026-05-09 - implementador
- Etapa: Implementacion — Descuento % en items de pedido
- Cambio: migracion `AddDescuentoPorcentajePedidoItem` generada y aplicada. Script SQL `20260509_AddDescuentoPorcentajePedidoItem.sql` para produccion. Script de limpieza de datos de prueba `20260509_TruncatePedidosYCompras_PROD.sql` generado.
- Motivo: incorporar campo de descuento porcentual por item en pedidos.
- Impacto en capas: Domain, Infrastructure.
- Riesgos/supuestos: script de limpieza requiere aprobacion previa a ejecucion en produccion.

### 2026-04-27 - implementador
- Etapa: Implementacion — Reversion de estados de pedido Fase 1 + Fase 2
- Cambio: `HistorialEstadoPedido` entidad nueva. `Pedido` con campos de auditoria de reversion + `RowVersion`. `IPedidoService` ampliado con `RevertirFinalizacionConcesionAsync`, `RevertirCancelacionAsync`, `GetHistorialAsync`. Migracion `AddReversionPedidoYHistorial`. Politica `RequireRevertirPedido` en `Program.cs`. Endpoints y vista `Detalle.cshtml` con modales de confirmacion y tabla de historial. Compensaciones contables via `MovimientoCC` con prefijo [Reversion] (no destructivas). Re-reserva de stock propio al revertir.
- Motivo: cliente necesitaba revertir concesiones finalizadas y cancelaciones por error.
- Impacto en capas: todas.
- Riesgos/supuestos: build OK. Migracion aplicada local, pendiente produccion.

### 2026-04-25 - implementador
- Etapa: Implementacion — Reversion a Borrador + edicion post-confirmacion con propagacion a compra
- Cambio: `PedidoService.VolverABorradorAsync` idempotente. Edicion de items en estado Confirmado/EnPreparacion propaga `TotalCostoSnapshot` a la compra vinculada. Cancelacion desvincula items y si la compra queda vacia vuelve a Borrador.
- Motivo: pedido del cliente (Fase 2 de reversiones).
- Impacto en capas: Infrastructure (service), Presentacion (controller + vista).
- Riesgos/supuestos: concurrencia resuelta por revalidacion transaccional (sin `RowVersion` en `Pedido`).

### 2026-04-24 - implementador
- Etapa: Implementacion — Stock propio (5 etapas completadas)
- Cambio: `ProductoPropio` entidad nueva. `PedidoItem` con dual origen (provider/propio). `IStockPropioService` con reserva/devolucion/ajuste y concurrencia optimista. Integracion en `PedidoService.ConfirmarAsync` (reserva FIFO + split a proveedor). `StockController` + vistas CRUD. Autocomplete en pedidos acepta stock propio. Migracion `AddProductosPropiosYStock`.
- Motivo: cliente necesita manejar productos de inventario propio separados del catalogo de proveedores.
- Impacto en capas: todas.
- Riesgos/supuestos: `RowVersion` incrementado manualmente (MySQL no tiene rowversion nativo). Build OK.
