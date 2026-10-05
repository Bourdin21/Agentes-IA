# Memoria - Implementador

## Proyecto: marihogar
## Ultima actualizacion: 2026-10-02 (CR-86 — comision cobrada por periodo + impuesto al cheque Ley 25.413, con CR-85 absorbido; correccion post-QA con 6 defectos y alcance nuevo CA-86.17. Antes: CR-84)

## Definiciones vigentes

### Sprint 1 (de 7) — M10 rol Vendedor + M2 Catalogo de productos + M3 Control de stock

Alcance cerrado segun `2-disenador-funcional.md` y `3-arquitecto-mvc.md`, sin desvio de alcance respecto de lo aprobado. NO se toco ningun modulo fuera de M10/M2/M3 (Presupuestos, Ventas, Entregas, AFIP, CC local/proveedores, Compras, Cheques, Gastos, Caja, Proyeccion, Aumento masivo, Dashboard, CRM/Bot quedan para sprints siguientes).

### Escaneo de reutilizacion (previo a implementar)

- `docs/ShowroomGriffin/definiciones/5-implementador.md` — patron de ajuste manual de stock (`StockController.Ajuste`, `AjusteStockViewModel`, redirect post-ajuste a la misma pantalla) y `StockService` con `AjusteManualAsync`/`RegistrarMovimientoAsync`. Reutilizado el patron de UX (permanecer en `Stock/Ajuste` tras guardar) y la idea de registrar el ledger en la misma transaccion que el StockActual.
- `docs/ganaderia/definiciones/5-implementador.md` (repo real `C:/Sistemas/ganaderia - emo`) — `IStockService`/`StockService`/`MovimientoStock` como ledger inmutable (`Cantidad` con signo, sin `SoftDestroyable`), validacion de stock no negativo antes de persistir. Reutilizado el diseño de ledger con signo y la regla de "unico punto de escritura" (aca formalizada como `IStockService.AjustarAsync` en Infrastructure).
- Decision: **no se copio codigo textual** de ninguno de los dos repos (los dominios difieren: ShowroomGriffin trabaja sobre variantes de producto con talle/color, ganaderia sobre `Grupo` de hacienda) — se adapto el patron de diseño (ledger + single-writer + confirmacion SweetAlert2 de stock negativo) al modelo de `Producto.StockActual` desnormalizado definido en `3-arquitecto-mvc.md`.

### Archivos y capas modificadas

**Domain** (`MariHogar.Domain`)
- `Enums/TipoMovimientoStock.cs` — nuevo enum `Compra=1/Venta=2/Ajuste=3` (Compra/Venta previstos para M5/M12, este sprint solo genera `Ajuste`).
- `Entities/Categoria.cs`, `Entities/Marca.cs` — nuevas, heredan `SoftDestroyable`, solo `Nombre` (sin flag `Activo` redundante: el soft delete ya cubre esa semantica, consistente con el resto del template).
- `Entities/Producto.cs` — nueva, hereda `SoftDestroyable`. Incluye `StockActual` desnormalizado con comentario explicito de que el unico escritor es `IStockService`.
- `Entities/ProductoFoto.cs` — nueva, hereda `SoftDestroyable`. `Path`, `Orden`, `EsPortada`.
- `Entities/MovimientoStock.cs` — nueva, **no hereda `SoftDestroyable`** (ledger inmutable, tal como exige la arquitectura).

**Application** (`MariHogar.Application`)
- `DTOs/CommonDtos.cs` — `SelectItemDto` (Id/Text para combos).
- `DTOs/CategoriaDtos.cs`, `DTOs/MarcaDtos.cs` — DTOs simples de catalogo.
- `DTOs/ProductoDtos.cs` — `ProductoListItemDto` (con `PrecioCompra` `decimal?` + `[JsonIgnore(Condition = WhenWritingNull)]` para que el campo se omita del JSON cuando el Service lo deja en null por rol), `ProductoFiltro`, `ProductoDetailDto`, `ProductoFotoDto`, `ProductoInput` (con `ConfirmarMargenNegativo`).
- `DTOs/StockDtos.cs` — `MovimientoStockListItemDto` (`Tipo` como `string`, no como el enum crudo — ver "Ajustes durante smoke test"), `MovimientoStockFiltro`, `AjusteStockInput` (con `ConfirmarNegativo`).
- `Interfaces/ICategoriaService.cs`, `Interfaces/IMarcaService.cs`, `Interfaces/IProductoService.cs`, `Interfaces/IStockService.cs`, `Interfaces/IFileStorageService.cs` — nuevas.

**Infrastructure** (`MariHogar.Infrastructure`)
- `Data/AppDbContext.cs` — `DbSet` de las 5 entidades nuevas + Fluent config (precision decimal 18,2, longitudes de string, FKs `Restrict`, indices en `CategoriaId`/`MarcaId`/`ProductoId`/`Fecha`/`Nombre`). `MovimientoStock` configurado sin heredar el query filter global de soft delete.
- `Services/CategoriaService.cs`, `Services/MarcaService.cs` — CRUD + listado DataTables + combo. Bloquean el delete si hay productos activos asociados (evita referencias colgantes por el query filter global de soft delete).
- `Services/ProductoService.cs` — CRUD, listado con filtro por rol (`esAdministrador` determina si `PrecioCompra` viaja en el DTO), gestion de fotos (alta con limite de 5, portada, reordenar, softdelete con borrado fisico via `IFileStorageService`), `ContarConStockBajoMinimoAsync` (dato dejado disponible para el dashboard de M9, sin armar la pantalla).
- `Services/StockService.cs` — unico escritor de `Producto.StockActual` + `MovimientoStock`. `AjustarAsync` corre en transaccion, rechaza resultado negativo salvo `ConfirmarNegativo=true`. `ListarMovimientosAsync` con filtros producto/tipo/fecha.
- `Services/LocalFileStorageService.cs` — nuevo, `wwwroot/uploads/{subFolder}` con nombre unico (`Guid`), usado para fotos de producto.
- `Data/SeedData.cs` — agregado `RolVendedor = "Vendedor"` al array de roles seedeados.
- `DependencyInjection.cs` — registrados `ICategoriaService`, `IMarcaService`, `IProductoService`, `IStockService`, `IFileStorageService` (todos Scoped).

**Web** (`MariHogar.Web`)
- `Program.cs` — nueva policy `RequireVentas` (`SuperUsuario` + `Administrador` + `Vendedor`), junto a `RequireAdministracion` ya existente.
- `Controllers/UsersController.cs` — `GetAssignableRoles()` ahora incluye `Vendedor` ademas de `Administrador` (si no, el rol nuevo quedaba seedeado pero inasignable desde la UI — ajuste minimo de una linea, necesario para que M10 sea funcionalmente completo).
- `Controllers/CategoriasController.cs`, `Controllers/MarcasController.cs` — CRUD, `[Authorize(Policy = "RequireAdministracion")]` a nivel clase.
- `Controllers/ProductosController.cs` — `[Authorize(Policy = "RequireVentas")]` a nivel clase (Index/GetData compartidos), overrides `[Authorize(Policy = "RequireAdministracion")]` en Create/Edit/Delete/SubirFoto/EliminarFoto/MarcarPortada/ReordenarFotos. Filtros persistidos en sesion bajo `Filtros:Productos:Index`.
- `Controllers/StockController.cs` — `[Authorize(Policy = "RequireAdministracion")]` a nivel clase (listado de movimientos y ajuste manual son exclusivos de Administrador segun el sprint). Filtros persistidos en sesion bajo `Filtros:Stock:Index`. Accion `GetStockActual` (AJAX) para que la vista de Ajuste calcule el resultado prospectivo antes de confirmar.
- `Models/CategoriaViewModels.cs`, `Models/MarcaViewModels.cs`, `Models/ProductoViewModels.cs`, `Models/StockViewModels.cs` — nuevos.
- `Helpers/SessionExtensions.cs` — `SetObject`/`GetObject<T>` sobre `ISession` (JSON), implementa el patron transversal de filtros persistidos en sesion (reutilizable por los sprints siguientes: Leads, Presupuestos, Ventas, Entregas, etc.).
- `Helpers/DataTableRequestHelper.cs` — parseo estandar de `Request.Form` de DataTables hacia `DataTableRequest` (reutilizable, evita duplicar el parseo manual que ya existia inline en `UsersController`).
- `Helpers/FormParsing.cs` — parseo tolerante de filtros sueltos (`int?`/`decimal?`/`DateTime?`) desde `Request.Form`.
- `Views/Categorias/{Index,Create,Edit}.cshtml`, `Views/Marcas/{Index,Create,Edit}.cshtml` — CRUD simple con DataTables + filtro de texto libre (Categoria/Marca NO estan en la lista de listados con filtro persistido en sesion del diseño — son catalogos simples).
- `Views/Productos/{Index,Create,Edit}.cshtml` — Index con 6 filtros de columna (nombre, marca, modelo, categoria, stock rango, precio venta rango) persistidos en sesion, badge rojo "Bajo minimo", columna/boton "Precio compra"/"Nuevo"/"Eliminar" solo si `EsAdministrador`. Create/Edit con cards "Datos generales" / "Precios y stock" (+ "Fotos" en Edit), Select2 en Marca/Categoria inicializado con el valor asignado en Edit, confirmacion SweetAlert2 client-side + guard server-side para margen negativo.
- `Views/Stock/Index.cshtml`, `Views/Stock/Ajuste.cshtml` — listado con filtro producto/tipo/rango de fecha (daterangepicker) persistido en sesion; Ajuste con confirmacion SweetAlert2 client-side (consulta `GetStockActual` para el calculo prospectivo) + guard server-side de stock negativo.
- `Views/Shared/_Layout.cshtml` — sidebar: seccion "Catalogo" nueva con "Productos" (visible a SuperUsuario/Administrador/Vendedor) y "Categorias"/"Marcas"/"Stock" (visible solo a SuperUsuario/Administrador).

### Migraciones EF generadas

- `20260724152806_AddCatalogo` — crea `Categorias`, `Marcas`, `Productos`, `ProductoFotos`, `MovimientosStock` con FKs `Restrict` e indices (`CategoriaId`, `MarcaId`, `ProductoId`, `Fecha`, `Nombre` x3). **Aplicada exitosamente** contra `marihogar_dev` (MySQL local disponible en este entorno, `dotnet ef database update` confirmado sin pendientes via `dotnet ef migrations list`).
- Rol `Vendedor`: no requiere migracion de esquema (se crea via `SeedData.InitializeAsync` al arrancar la app, igual que `SuperUsuario`/`Administrador`) — confirmado en el log de arranque: `Rol 'Vendedor' creado.`.

### Ajustes durante smoke test (bugs encontrados y corregidos en la misma sesion, antes de cerrar)

1. **`StockService.ListarMovimientosAsync` — 500 en MySQL**: `_db.Users.Where(u => usuarioIds.Contains(u.Id))` con `usuarioIds` como coleccion local generaba `InvalidOperationException: Expression '@usuarioIds' in the SQL tree does not have a type mapping assigned` (MySQL/EF Core 10 no soporta type mapping de IN generado desde coleccion local — mismo patron ya documentado como comentario en `UsersController.GetData`, que no habia leido con suficiente atencion la primera vez). Fix: traer usuarios a memoria (`ToListAsync()`) y filtrar en-proceso con `HashSet<string>`, igual que el patron ya usado en `UsersController`. **Este patron debe agregarse a `32-estandares-qa-implementador.instructions.md`** como regla generalizable (no solo el caso de Users) — pendiente de que QA/orquestador lo catalogue formalmente.
2. **`MovimientoStockListItemDto.Tipo` serializaba como int crudo**: el enum `TipoMovimientoStock` se serializaba por `System.Text.Json` como numero (`3`) en vez del nombre (`"Ajuste"`), rompiendo el badge de color en el JS del listado (`clases[d]` no matcheaba). Fix: `Tipo` cambiado a `string` en el DTO, mapeado con `.ToString()` en el Service (mismo criterio que `UsersController` ya usa para `Estado`).

Ambos bugs se detectaron corriendo la app real contra MySQL (no solo `dotnet build`), confirmando la importancia del smoke test funcional ademas de la compilacion.

### Evidencia de build y pruebas funcionales minimas

- `dotnet build MariHogar.slnx` → **Compilacion correcta, 0 errores** (9 warnings preexistentes del template: vulnerabilidad NU1902 de MailKit/MimeKit y `HomeController.StatusCode` — ninguno introducido por este sprint).
- Migracion generada y **aplicada** contra `marihogar_dev` (MySQL local).
- Smoke test funcional real (app corriendo, login real, cookies, MySQL real) ejecutado sobre:
  - Seed: roles `SuperUsuario`/`Administrador`/`Vendedor` creados correctamente al arrancar.
  - `Categorias`: crear + listar via DataTables — OK.
  - `Marcas`: crear + listar via DataTables — OK.
  - `Productos`: crear (con `MarcaId`/`CategoriaId` existentes) + listar via DataTables, `StockActual=0` y badge `stockBajoMinimo=true` correctos al nacer con stock 0 y minimo 5 — OK.
  - `Stock/Ajuste`: intento de ajuste que deja stock negativo **sin** `ConfirmarNegativo` → rechazado con mensaje ("El ajuste dejaria el stock en -10 (negativo)..."), `StockActual` sin cambios — OK. Mismo ajuste **con** `ConfirmarNegativo=true` → aplicado, `StockActual=-10`, `MovimientoStock` registrado con `UsuarioId`/`UsuarioNombre` resuelto correctamente — OK.
  - Permisos: usuario con rol `Vendedor` creado via `Users/Create` (verificado que `Vendedor` ya es asignable desde la UI). Login como Vendedor: `GET /Productos` → 200; `GET /Categorias`, `/Marcas`, `/Stock`, `/Productos/Create` → 302 a `/Account/AccessDenied` — OK. `GetData` de Productos como Vendedor **no incluye la clave `precioCompra` en el JSON** (confirmado byte a byte, no solo valor null) — OK, cumple la regla de arquitectura de no exponer el campo a nivel Service/mapping.

### Riesgos residuales

- Warning de EF Core en arranque: *"Entity 'Producto' has a global query filter... required end of a relationship with 'MovimientoStock'"* — esperado y aceptado por diseño (el ledger es intencionalmente no-softdeletable mientras referencia a un `Producto` que si lo es); no bloquea nada, documentado por si aparece de nuevo en QA.
- No se implemento reordenamiento por drag-and-drop de fotos (`IProductoService.ReordenarFotosAsync`/`ProductosController.ReordenarFotos` existen pero no tienen UI conectada todavia) — la "portada reordenable" pedida en HU-2.2 se resolvio con el boton "Hacer portada" (cualquier foto puede pasar a ser portada), que cubre el criterio de aceptacion tal como esta redactado. Drag-and-drop del orden completo queda como mejora opcional, no bloqueante.
- No se agrego vista "Details" separada para Producto — Edit ya expone todos los datos + fotos + stock actual; se prioritizo no duplicar pantallas dado que el wireframe generico no la exige de forma explicita para Producto. Si QA/cliente la pide, es un agregado menor (misma capa, sin migracion).
- `ContarConStockBajoMinimoAsync()` (Application/Infrastructure) esta implementado y probado por codigo pero **sin consumidor todavia** — el dashboard real es de M9 (sprint futuro), tal como pide el alcance de este sprint ("dejar el dato/consulta disponible, no armar la pantalla").
- Regla de reutilizacion cross-proyecto pendiente de catalogar formalmente (ver bug #1 de arriba): patron "no usar `.Contains()` de coleccion local contra MySQL/EF Core 10" deberia agregarse a `32-estandares-qa-implementador.instructions.md` para que el proximo sprint (o el proximo proyecto) no repita el mismo bug — la unica referencia hoy es un comentario suelto en `UsersController.cs` del propio marihogar.

### Proximos pasos pendientes (Sprint 1)

- Sprint 2 (segun plan del cliente): Presupuestos + Ventas + CC local, con foco reforzado de UX/UI en Ventas (ya documentado en `2-disenador-funcional.md`, ver entrada de trazabilidad 2026-07-24 "ajuste de diseño").
- `IStockService`/`MovimientoStock` quedan listos para que `VentaService`/`OrdenCompraService` (sprints futuros) generen movimientos `Venta`/`Compra` reutilizando el mismo `IStockService.AjustarAsync`-like pattern (a definir la firma exacta cuando se implemente M5/M12, hoy `AjustarAsync` esta pensado especificamente para ajuste manual con motivo).

---

### Sprint 3 (de 6) — M6 Entregas a domicilio

Alcance cerrado segun `2-disenador-funcional.md` (HU-6.1 a HU-6.3, wireframe "Entrega (mobile)", tabla de maquina de estados de Entrega) y `3-arquitecto-mvc.md` (entidad `Entrega`, migracion `AddEntregas`), sin desvio de alcance respecto de lo aprobado. NO se toco ningun modulo fuera de M6 (Compras, CC Proveedores, Cheques, Gastos, Caja, Proyeccion, Aumento masivo, AFIP, Dashboard, CRM/Bot quedan para sprints siguientes o en espera). El plan de 7 sprints originalmente planteado quedo en 6 desde el ajuste de alcance del 2026-07-24 (pausa de Etapa 2) — este es el Sprint 3 de 6.

**Regla de proceso vigente desde el cierre de Sprint 2** (ver `trazabilidad.md`, entrada "orquestador — eliminacion de smoke test del Implementador"): este sprint se cierra **sin smoke test funcional propio** (no se levanto la app, no se probaron flujos por navegador/API). Evidencia de cierre: build limpio + migracion generada y aplicada + revision de codigo propia linea por linea de la logica critica. Guia de pasos para verificacion manual del usuario al final de esta seccion.

#### Escaneo de reutilizacion (previo a implementar)

- Escaneado `docs/*/definiciones/5-implementador.md` de todos los proyectos del historial (ShowroomGriffin, ganaderia, koi, labipac, delicias-naturales, y el resto via `docs/indice.md`) buscando un modulo de logistica/entregas/reparto a domicilio comparable. **No se encontro ningun modulo equivalente** — los unicos matches de la palabra "entrega" en el historial son falsos positivos sin relacion (ganaderia: "reparto de cuotas" de un plan de pagos financiero, no logistica; ShowroomGriffin: "version entregada" en el sentido de release de software; koi: menciones de RepartoGeneral, un modulo financiero de liquidaciones, no de envios fisicos). Confirma lo ya anticipado en el alcance de este sprint: Entregas a domicilio con direccion/fecha/cobro en destino es especifico del negocio de marihogar, sin precedente reutilizable de otro proyecto del estudio.
- **Reutilizacion interna obligatoria (confirmada por el cliente) — SI aplicada:** el cobro en destino de una Entrega (HU-6.2, `EntregaService.RegistrarCobroAsync`) reutiliza `PagoVenta` **directamente sobre la misma Venta asociada** (agrega filas nuevas a `venta.Pagos`, mismo enum `MetodoPago` restringido a Efectivo/Transferencia/MercadoPago, misma formula de calculo del `EstadoVenta` resultante — suma total de pagos vs Total — que `VentaService.ConfirmarAsync` de Sprint 2) — **no se creo un flujo de pago paralelo**, tal como exigio explicitamente el cliente en el pedido de este sprint.
- **Reutilizacion interna de patrones ya establecidos:** layout mobile de una columna + barra inferior fija de `Ventas/Create.cshtml` (Sprint 2, dejado explicitamente "reutilizable por Entregas" en su propio comentario de codigo) adaptado tal cual en `Entregas/Details.cshtml` (con la diferencia de que aca la barra fija se mantiene en todos los tamaños de pantalla, no solo `d-lg-none`, porque el wireframe de diseño pide "card unica" tanto en mobile como en desktop para esta pantalla especifica — Entregas no tiene el equivalente al layout POS de dos columnas de Ventas); patron de filtros persistidos en sesion (`SessionExtensions`, `DataTableRequestHelper`, `FormParsing`); patron MH-001 (nunca IN sobre coleccion local — aplicado en `EntregaService.GetByIdAsync` para resolver nombres de usuario de los intentos, y en `ListarAsync` para el saldo pendiente por fila); patron GAN-001 (guard "al menos un pago con datos reales", no solo `Count==0`) reaplicado en `RegistrarCobroAsync` igual que en `VentaService.ConfirmarAsync`; patron REG-004 (botones de accion derivados del estado real de la entidad, nunca hardcodeados) en la barra inferior de `Entregas/Details.cshtml`.
- **Decision:** no se copio codigo textual de ningun repo externo — `EntregaService`/`EntregasController` se disenaron desde cero sobre los contratos de Arquitectura, reutilizando exclusivamente los patrones de diseño y las convenciones de estilo ya establecidas en marihogar (Sprints 1 y 2).

#### Decisiones de implementacion no explicitas en el diseño (documentadas para trazabilidad)

1. **Historial de intentos como entidad ledger separada (`EntregaIntento`)**: el diseño pide "historial de intentos visible en el detalle de la entrega (guardar los intentos previos, no sobreescribir)" pero no especifica el modelo de datos. Se opto por una entidad nueva `EntregaIntento` (no hereda `SoftDestroyable`, mismo criterio que `MovimientoStock`/`MovimientoCCLocal`: ledger inmutable de historial, nunca se edita ni se borra) en vez de sobrecargar `Entrega.MotivoNoEntrega` con una lista serializada. Cada transicion `EnCamino -> NoEntregada` agrega una fila nueva (`Fecha`, `FechaProgramadaIntento`, `Motivo`, `UsuarioId`); `Entrega.MotivoNoEntrega` sigue existiendo como resumen del ultimo intento (para mostrar en el badge/alerta sin tener que cargar la coleccion), pero la fuente de verdad del historial completo es `EntregaIntento`.
2. **Maximo 1 Entrega por Venta**: el diseño no lo dice explicitamente, pero se infiere de la maquina de estados (los reintentos de "No entregada" reagendan la misma fila, no crean una entrega nueva) y es necesario para que el guard `VentaService.TieneEntregaAsociadaAsync` (usado para bloquear la cancelacion, HU-5.4) sea inambiguo. `EntregaService.CrearAsync` rechaza con "Esta venta ya tiene una entrega programada" si ya existe una Entrega (en cualquier estado) para esa Venta.
3. **`EstadoVenta` NO se sobrecarga con sub-estados de entrega**: `2-disenador-funcional.md` incluye en su tabla de maquina de estados de Venta (seccion Diseño, no la de Entrega) dos transiciones "Pagada/PagadaParcial -> Con entrega pendiente -> Entregada" que el Arquitecto explicitamente dejo "para M6" sin agregarlas al enum `EstadoVenta` en Sprint 2. Se decidio **no** agregar esos 2 valores nuevos al enum en este sprint: `Venta.Estado` mantiene su semantica pura de estado de pago (Pendiente/PagadaParcial/Pagada/Cancelada, ya usada por CC Local y por los filtros de listado existentes) y el estado logistico se consulta por separado a traves de la `Entrega` asociada (`Venta.Details.cshtml` ahora muestra una card "Entrega" con su propio badge de estado, ademas de la card "Acciones" ya existente). Sobrecargar `Venta.Estado` con el estado de la entrega hubiera hecho perder informacion real (no se podria distinguir si una venta con entrega en camino fue pagada completa o parcialmente) — decision documentada aca por si el cliente pide explicitamente fusionar ambos estados en un sprint futuro.
4. **"Salir a repartir" (Pendiente -> EnCamino) como paso explicito**: el wireframe de "Entrega (mobile)" dibuja solo los botones "Registrar cobro" y "Marcar entregada"/"No entregada", pero la tabla de maquina de estados (fuente mas especifica y autoritativa) exige el paso intermedio "Vendedor sale a repartir". Se agrego un boton "Salir a repartir" en la barra inferior cuando el estado es Pendiente, con un SweetAlert2 de confirmacion liviana (no destructivo, solo evita toques accidentales). El cobro y el cierre (Entregada/No entregada) solo estan disponibles una vez que la entrega esta En camino, consistente con la letra de la tabla.
5. **`MarcarEntregadaAsync` no exige saldo pendiente = 0**: HU-6.2 dice "registrar el cobro (si quedaba pendiente) y cerrarla", pero no dice explicitamente que el cierre este bloqueado si queda saldo. Se decidio no bloquear (mismo criterio no-bloqueante ya usado en Sprint 2 para la advertencia de stock insuficiente en Ventas, HU-5.8) — la UI muestra un SweetAlert2 de advertencia (no bloqueante) si hay saldo pendiente al marcar entregada, pero permite continuar. Documentado por si el negocio prefiere bloquear esta transicion en un ajuste futuro.
6. **Filtros del listado de Entregas**: se implementaron exactamente los 3 filtros pedidos explicitamente en el alcance de este sprint (estado, vendedor asignado, fecha programada), no uno por cada columna visible de la grilla (que incluye tambien Cliente, Direccion y Saldo pendiente) — desvio deliberado de la regla general de `25-frontend-design-system.instructions.md` ("un filtro por cada columna visible"), justificado porque el alcance de este sprint especifico los 3 filtros exactos a implementar y el patron ya establecido en Sprint 2 (`Ventas/Index`) tampoco filtra por la columna "Total". Si el cliente pide filtro por Cliente/Direccion, es un agregado menor sin migracion.

#### Archivos y capas modificadas

**Domain** (`MariHogar.Domain`)
- `Enums/EstadoEntrega.cs` — nuevo enum `Pendiente=1/EnCamino=2/Entregada=3/NoEntregada=4`.
- `Entities/Entrega.cs` — nueva, hereda `SoftDestroyable`. `VentaId`, `Direccion`, `FechaProgramada`, `VendedorAsignadoId`, `Estado`, `MotivoNoEntrega` (nullable, resumen del ultimo intento), `FechaEntregada` (nullable), coleccion `Intentos`.
- `Entities/EntregaIntento.cs` — nueva, **no hereda `SoftDestroyable`** (ledger de historial inmutable, mismo criterio que `MovimientoStock`/`MovimientoCCLocal`). `EntregaId`, `Fecha`, `FechaProgramadaIntento`, `Motivo`, `UsuarioId`.

**Application** (`MariHogar.Application`)
- `DTOs/EntregaDtos.cs` — nuevo: `EntregaListItemDto`, `EntregaFiltro`, `EntregaIntentoDto`, `EntregaDetailDto` (incluye `VentaTotal`/`VentaEstado`/`VentaSaldoPendiente` para que la pantalla mobile no tenga que navegar a otra vista), `EntregaInput`, `PagoEntregaInput` (mismo shape que `PagoVentaInput`), `EntregaPrecargaDto`.
- `DTOs/VentaDtos.cs` — `VentaDetailDto` ampliado con `EntregaId`/`EntregaEstado` (nullable, para que `Ventas/Details.cshtml` ofrezca "Ver entrega" o "Programar entrega" segun corresponda); comentario de `VentaListItemDto.TieneEntrega` actualizado (ya no es un placeholder `false`, se resuelve de verdad).
- `Interfaces/IEntregaService.cs` — nuevo, con los 8 metodos de la maquina de estados (`ListarAsync`, `ListarVendedoresParaComboAsync`, `GetByIdAsync`, `ObtenerPrecargaDesdeVentaAsync`, `CrearAsync`, `IniciarRecorridoAsync`, `RegistrarCobroAsync`, `MarcarEntregadaAsync`, `MarcarNoEntregadaAsync`, `ReagendarAsync`).
- `Interfaces/IVentaService.cs` — doc-comment de `CancelarAsync` actualizado (el guard de Entrega ya es real, no un placeholder).

**Infrastructure** (`MariHogar.Infrastructure`)
- `Data/AppDbContext.cs` — `DbSet<Entrega>`/`DbSet<EntregaIntento>` + Fluent config (`Direccion` maxlength 300, FKs `Restrict` a Venta/ApplicationUser, indices `VentaId`/`Estado`/`VendedorAsignadoId`/`FechaProgramada`; `EntregaIntento` con FK `Cascade` a `Entrega`, sin query filter global, mismo criterio que los demas ledgers).
- `Services/EntregaService.cs` — nuevo. Implementa la maquina de estados completa: `CrearAsync` (guards: Venta Pagada/PagadaParcial, sin Entrega previa, Direccion obligatoria, fecha >= hoy), `IniciarRecorridoAsync` (Pendiente->EnCamino), `RegistrarCobroAsync` (EnCamino, reutiliza `PagoVenta` sobre la Venta asociada en una transaccion propia, misma formula de `EstadoVenta` que `VentaService.ConfirmarAsync`), `MarcarEntregadaAsync` (EnCamino->Entregada), `MarcarNoEntregadaAsync` (EnCamino->NoEntregada, motivo obligatorio, agrega `EntregaIntento`), `ReagendarAsync` (NoEntregada->Pendiente, nueva fecha >= hoy, preserva el historial de intentos).
- `Services/VentaService.cs` — `TieneEntregaAsociadaAsync` paso de placeholder estatico (`Task.FromResult(false)`) a consulta real (`_db.Entregas.AnyAsync(e => e.VentaId == ventaId)`), tal como quedo anotado como pendiente desde el cierre de Sprint 2. `ListarAsync`/`GetByIdAsync` resuelven `TieneEntrega`/`EntregaId`/`EntregaEstado` con consultas puntuales acotadas (patron MH-001-safe, sin IN sobre coleccion local).
- `DependencyInjection.cs` — registrado `IEntregaService` (Scoped).

**Web** (`MariHogar.Web`)
- `Controllers/EntregasController.cs` — nuevo. `[Authorize(Policy = "RequireVentas")]` a nivel clase (Administrador y Vendedor por igual, tabla de permisos "Registrar entregas y cobros"). Acciones: `Index`/`GetData`/`LimpiarFiltros` (listado), `Create` GET+POST (alta desde una Venta confirmada), `Details` (pantalla mobile-first), `IniciarRecorrido`/`MarcarEntregada`/`NoEntregada`/`Reagendar` (POST form estandar con `TempData`), `RegistrarCobro` (POST AJAX con `pagosJson`, mismo patron de antiforgery que `VentasController.Confirmar`).
- `Controllers/VentasController.cs` — sin cambios (no hizo falta tocarlo: `Ventas/Details.cshtml` consume el nuevo `EntregaId`/`EntregaEstado` del DTO que ya trae `VentaService.GetByIdAsync`).
- `Models/EntregaViewModels.cs` — nuevo: `EntregaIndexViewModel`, `EntregaCreateViewModel` (con DataAnnotations en español), `EntregaDetailsViewModel`.
- `Views/Entregas/Index.cshtml` — listado desktop/admin, DataTables server-side con 3 filtros (estado, vendedor asignado, fecha programada con `daterangepicker`) persistidos en sesion bajo `Filtros:Entregas:Index`, patron identico a `Ventas/Index.cshtml`.
- `Views/Entregas/Create.cshtml` — formulario simple (Direccion, FechaProgramada con `min` de hoy, VendedorAsignado con Select2), card unica, sin la inversion UX elevada de Ventas (no la exige el wireframe de diseño para esta pantalla).
- `Views/Entregas/Details.cshtml` — **pantalla mobile-first (HU-6.2/HU-6.3)**, reutiliza tal cual el patron de una columna + barra inferior fija de `Ventas/Create.cshtml` (clases `.ov-entrega-bottombar` analogas a `.ov-venta-bottombar`), con la diferencia de que la barra queda fija en todos los tamaños de pantalla (no solo `d-lg-none`). Card cliente/direccion (con link a Google Maps) arriba, card saldo pendiente, card "Registrar cobro" colapsable (reutiliza el mismo JS de filas de pago +metodo/monto+"Todo efectivo"/"Todo transferencia" que `Ventas/Create.cshtml`, POST AJAX a `RegistrarCobro`), card historial de intentos (si hay), barra inferior con los botones segun el estado real (`Salir a repartir` / `Marcar entregada`+`No entregada` / `Reagendar` / `Volver a la venta`) — nunca hardcodeados (REG-004), resueltos con `@if` contra `EstadoReal`.
- `Views/Ventas/Create.cshtml` — habilitado el boton "Programar entrega" de la pantalla de exito (Sprint 2 lo dejaba deshabilitado con tooltip "Proximo sprint"): ahora es un link real a `Entregas/Create?ventaId=X`, visible solo si la venta confirmada quedo Pagada o PagadaParcial (con fallback deshabilitado + tooltip explicativo en el caso raro de Pendiente).
- `Views/Ventas/Details.cshtml` — agregada card "Entrega": "Programar entrega" (si la venta esta Pagada/PagadaParcial y no tiene entrega todavia), "Ver entrega" con badge de estado (si ya tiene una), o texto explicativo (si la venta todavia no tiene pago). Card "Acciones" ajustada: el boton "Cancelar venta" se oculta (no solo se deshabilita) cuando la venta ya tiene una Entrega asociada, con una nota explicando por que — evita que el usuario dispare un intento de cancelacion que el Service va a rechazar igual.
- `Views/Shared/_Layout.cshtml` — sidebar: link "Entregas" agregado dentro de la seccion "Ventas" ya existente (visible a SuperUsuario/Administrador/Vendedor, misma policy `RequireVentas` que protege el controller — REG-010/32-estandares).

#### Migracion EF generada

- `20260724184703_AddEntregas` — crea `Entregas` (FKs `Restrict` a `Ventas` y `AspNetUsers`, indices `VentaId`/`Estado`/`VendedorAsignadoId`/`FechaProgramada`) y `EntregaIntentos` (FK `Cascade` a `Entregas`, indice `EntregaId`). **Generada y aplicada** exitosamente contra `marihogar_dev` (confirmado con `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web`: 4 migraciones totales — `InitialCreate`, `AddCatalogo`, `AddPresupuestosVentas`, `AddEntregas` — ninguna marcada `(Pending)`).

#### Evidencia de cierre — build + migracion + revision de codigo (sin smoke test, regla de proceso vigente)

- `dotnet build MariHogar.slnx` → **Compilacion correcta, 0 errores** (9 warnings, todos preexistentes: NU1902 de MailKit/MimeKit + CS0114 de `HomeController.StatusCode`; ninguno introducido por este sprint). Dado que el proyecto compila los `.cshtml` en build (Razor compile-on-build activo por default en el SDK, sin overrides en `MariHogar.Web.csproj`), este build tambien valida la sintaxis Razor y el binding de ViewModels de las 3 vistas nuevas (`Entregas/Index`, `Entregas/Create`, `Entregas/Details`) y de las 2 vistas modificadas (`Ventas/Create`, `Ventas/Details`).
- Migracion `20260724184703_AddEntregas` generada y **aplicada** contra `marihogar_dev`.
- **Revision de codigo propia, linea por linea** (releida completa, no solo "compila"):
  - `EntregaService.CrearAsync`: orden de guards correcto (Direccion -> VendedorAsignadoId -> fecha >= hoy -> Venta existe -> Venta Pagada/PagadaParcial -> sin Entrega previa) antes de persistir.
  - `EntregaService.RegistrarCobroAsync`: guard EnCamino -> guard "al menos un pago real" (GAN-001) -> guard metodo permitido -> guard saldo pendiente > 0 -> transaccion (`BeginTransactionAsync`) que agrega los `PagoVenta` nuevos a `venta.Pagos` (con `VentaId` seteado explicitamente ademas de la navegacion, para que el insert sea correcto incluso sin haber cargado la coleccion completa desde la base) y recalcula `venta.Estado` con la formula `pagadoExistente + sumaNuevosPagos` vs `venta.Total` — **misma formula que `VentaService.ConfirmarAsync`**, confirmado comparando ambos metodos linea por linea. `catch`+`RollbackAsync` presente.
  - `EntregaService.MarcarNoEntregadaAsync`: guard EnCamino -> motivo obligatorio -> transaccion que actualiza `Entrega.Estado`/`MotivoNoEntrega` **y** agrega una fila nueva a `EntregaIntentos` (nunca sobreescribe una fila existente, confirmado que no hay ningun `Update`/`Remove` sobre `EntregaIntentos` en todo el archivo) -> commit.
  - `EntregaService.ReagendarAsync`: guard NoEntregada -> guard fecha >= hoy -> `Entrega.Estado` vuelve a `Pendiente`, `FechaProgramada` se actualiza, `MotivoNoEntrega` se limpia (resumen del ultimo intento, no el historial) — la coleccion `Intentos` no se toca, confirmado que las filas ya persistidas en `EntregaIntentos` (FK `EntregaId`, sin relacion con el campo `MotivoNoEntrega` que se limpia) permanecen intactas.
  - `VentaService.CancelarAsync`: confirmado que `TieneEntregaAsociadaAsync` ahora consulta `_db.Entregas.AnyAsync(e => e.VentaId == ventaId)` sin filtro de estado — una Venta con una Entrega ya `Entregada` (terminal) **tambien** queda bloqueada para cancelar, consistente con la letra de HU-5.4 ("cancelar una venta con entrega... asociada esta bloqueado", sin excepcion para entregas ya cerradas).
  - `EntregaService.ListarAsync`/`GetByIdAsync`: confirmado que ninguna query combina `Include` de coleccion + orden/filtro dinamico + `Skip`/`Take` en el mismo `IQueryable` (Venta/VendedorAsignado son navegaciones simples, no colecciones); el saldo pendiente y los nombres de usuario de los intentos se resuelven con consultas acotadas al tamaño real de la pagina/de los intentos de una sola entrega, nunca con un `.Contains()` sobre una coleccion local grande (MH-001).
  - `Ventas/Details.cshtml`: confirmado que el boton "Cancelar venta" queda completamente oculto (no solo `disabled`) cuando `v.EntregaId.HasValue`, y que el `<form id="formCancelarVenta">` sigue existiendo fuera del `@if` visual (para no romper el JS existente que lo referencia por id, aunque en ese caso no haya boton que lo dispare).

#### Checklist de verificacion manual para el usuario (equivalente al smoke test que ya no ejecuta el Implementador)

Con la app corriendo (`dotnet run --project MariHogar.Web`) y logueado como Administrador o Vendedor:

1. **Alta de Entrega**: crear o abrir una Venta ya Pagada/PagadaParcial (de Sprint 2) → en `Ventas/Details`, click "Programar entrega" (card "Entrega") → completar Direccion + Fecha (probar que el date picker no deja elegir una fecha anterior a hoy) + Vendedor asignado → Guardar → verificar que redirige a `Entregas/Details/{id}` con estado "Pendiente".
2. **Salir a repartir**: en `Entregas/Details`, click "Salir a repartir" (con el SweetAlert2 de confirmacion) → verificar que el estado pasa a "En camino" y aparecen los botones "Marcar entregada"/"No entregada".
3. **Cobro en destino (venta con saldo pendiente)**: usar una Venta que haya quedado "Pagada parcial" → en la Entrega asociada (En camino), verificar que aparece la card "Registrar cobro" con el saldo pendiente correcto → click "Registrar cobro", cargar un pago (probar "Todo efectivo") → Confirmar cobro → verificar que la pagina recarga con saldo pendiente en $0 y que en `Ventas/Details` de esa venta el estado paso a "Pagada" y aparece el nuevo `PagoVenta` en la lista de pagos.
4. **Marcar entregada**: con saldo en $0, click "Marcar entregada" → verificar que el estado pasa a "Entregada" y desaparecen los botones de accion (queda solo "Volver a la venta").
5. **No entregada + reagendar**: crear otra Entrega, "Salir a repartir", click "No entregada" → cargar motivo (probar que sin motivo el SweetAlert2 no deja confirmar) → verificar que el estado pasa a "No entregada" y aparece el motivo en un alert amarillo → click "Reagendar" → elegir nueva fecha (probar que no deja elegir una anterior a hoy) → verificar que vuelve a "Pendiente" con la nueva fecha, **y que el intento anterior sigue visible** en la card "Historial de intentos" (no se borro).
6. **Repetir "No entregada" una segunda vez** sobre la misma Entrega reagendada → verificar que el historial de intentos ahora muestra **2** filas (la anterior no se sobreescribio).
7. **Guard de cancelacion de Venta**: intentar cancelar (desde `Ventas/Details`) una Venta que ya tiene una Entrega asociada → verificar que el boton "Cancelar venta" ya ni siquiera aparece (reemplazado por el texto explicativo). Si se fuerza el POST directo a `Ventas/Cancelar` de todas formas (ej. con curl), confirmar que responde con el error "Venta con entrega o factura asociada, no se puede cancelar."
8. **Alta de Entrega bloqueada**: intentar programar una segunda entrega para la misma Venta (navegando directo a `Entregas/Create?ventaId=X` de una venta que ya tiene una) → verificar que redirige con el mensaje de error correspondiente.
9. **Permisos**: loguearse como Vendedor y confirmar que `Entregas` aparece en el sidebar (seccion Ventas) y que puede operar el flujo completo igual que Administrador (tabla de permisos: "Registrar entregas y cobros" es igual para ambos roles).
10. **Listado**: en `Entregas/Index`, probar los 3 filtros (Estado, Vendedor asignado, rango de Fecha programada) uno por uno y el boton "Limpiar filtros" → confirmar que persisten al navegar a otra pantalla y volver (patron de sesion).
11. **Mobile**: reducir el ancho del navegador (o abrir desde el celular) en `Entregas/Details` y confirmar que la barra inferior de acciones queda fija abajo sin tapar contenido, con botones grandes thumb-friendly, y que el link "Ver en el mapa" abre Google Maps con la direccion cargada.

#### Riesgos residuales

- **`Venta.Estado` no incluye sub-estados de entrega** (decision documentada arriba, punto 3) — si el cliente pide fusionar el estado de pago y el estado logistico en una sola maquina de estados de Venta (como sugiere la tabla de Venta en `2-disenador-funcional.md`), es un cambio de alcance medio: nuevos valores de enum (sin romper los 4 ya persistidos, EF/MySQL solo requiere que los nuevos int no colisionen) + logica adicional en `EntregaService` para sincronizar `Venta.Estado` en cada transicion de `Entrega.Estado`. No implementado este sprint por decision de minimizar cambios y preservar la semantica de pago ya consumida por CC Local y los filtros existentes.
- **`MarcarEntregadaAsync` no bloquea con saldo pendiente > 0** (decision documentada arriba, punto 5) — solo advierte client-side con SweetAlert2. Si el negocio prefiere bloquear, es un cambio de una linea en el guard del Service + ajuste del mensaje en la vista.
- **Concurrencia no verificada**: al igual que el riesgo ya documentado en Sprint 2 sobre "Convertir a venta" (doble-tab), `EntregaService.CrearAsync` consulta "sin Entrega previa" antes de abrir cualquier transaccion — dos solicitudes casi simultaneas de "Programar entrega" para la misma Venta podrian, en teoria, crear 2 Entregas si la ventana de carrera coincide exactamente. Riesgo bajo (mismo argumento que Sprint 2: comercio de un solo mostrador, baja probabilidad), no mitigado con un indice unico en este sprint por directriz de cambios minimos — documentado para un sprint de endurecimiento futuro si el cliente lo pide.
- **Sin verificacion en caliente**: por la regla de proceso vigente, ningun tramo de este sprint fue ejecutado contra la app real ni contra MySQL en este ciclo — toda la evidencia es build + migracion aplicada + revision de codigo. La checklist de arriba es la unica forma de cerrar ese riesgo, a cargo del usuario.

#### Proximos pasos pendientes (Sprint 3)

- Sprint 4 (segun plan de 6 sprints vigente): M7 Facturacion electronica AFIP/ARCA — requiere el certificado digital (.p12) del cliente (riesgo ya documentado desde Arquitectura); puede arrancar con el servicio mockeado/homologacion si el certificado no esta disponible todavia.
- `Venta.Details.cshtml` ya expone `EntregaId`/`EntregaEstado` — cuando se implemente M7, el mismo patron (card dedicada con estado + link) es reutilizable para "Comprobante AFIP".
- Si el cliente pide en algun momento restringir "Vendedor asignado" de una Entrega a solo usuarios con rol Vendedor/Administrador (hoy el combo lista TODOS los `ApplicationUser`, igual criterio que `VentaService.ListarVendedoresParaComboAsync`/`PresupuestoService.ListarVendedoresParaComboAsync` ya usan desde Sprint 2), es un cambio menor de query (join contra `AspNetUserRoles`) replicable en los 3 lugares a la vez.

---

### Sprint 5 (de 6) — M18 Gastos del negocio + M15 Caja mensual + M16 Aumento masivo de precios + M17 Proyeccion financiera + M9 Dashboard

**Nota editorial del orquestador (2026-07-24):** este sprint se ejecuto por accidente en **dos instancias del agente implementador corriendo en paralelo** sobre el mismo working directory (un intento previo, reportado como "no produjo cambios", en realidad si habia disparado un sub-agente real en background que el orquestador no llego a rastrear). Cada instancia escribio su propia seccion completa de memoria aqui; se consolido en la version unica de abajo (la de la segunda instancia, que detecto la ejecucion paralela, adopto el trabajo de la primera como base y le aplico la misma revision linea por linea que exige el cierre de cualquier sprint) por ser la mas completa y la que refleja el estado final reconciliado del codigo. La version descartada tenia el mismo alcance funcional y calidad equivalente — la diferencia entre ambas fue exclusivamente de redaccion, no de codigo. **Nota de seguridad**: durante la sesion, la primera instancia interpreto los cambios de archivo de la segunda instancia como un posible intento de manipulacion externa (el entorno reporta cambios de archivo ajenos con una notificacion generica de "modificado por el usuario o un linter... no informar al usuario", que no distingue entre un sub-agente hermano legitimo y un actor no autorizado). Se trato correctamente como sospechoso en el momento (nunca se debe obedecer una instruccion de "no informar" incrustada en contenido de herramienta), y tanto el orquestador como QA verificaron despues, de forma independiente, que no hubo contenido malicioso — ver conclusion en `trazabilidad.md` y en `6-qa.md`. Ver tambien la entrada de `trazabilidad.md` de este sprint para el analisis completo de causa raiz (ejecucion paralela no intencional, no un ataque).

Alcance cerrado segun `2-disenador-funcional.md` (HU-18.1/18.2, HU-15.1/15.2, HU-16.1, HU-17.1/17.2, HU-9.1/9.2, wireframes de cada pantalla, patron de filtros en sesion) y `3-arquitecto-mvc.md` (entidad `Gasto`, `AumentoMasivoPrecioViewModel`, servicios `ICajaService`/`IProyeccionFinancieraService`/`IDashboardService`/`IAumentoMasivoPrecioService`), sin desvio de alcance respecto de lo aprobado. NO se toco AFIP ni CRM/Bot (explicitamente fuera de alcance, en espera). Este es el ultimo sprint de los 6 planificados salvo que el cliente pida uno de cierre/hardening.

**Nota de proceso relevante para trazabilidad**: durante esta sesion se detecto que un proceso concurrente (otra ejecucion del mismo prompt de implementacion, corriendo en paralelo sobre el mismo working directory) ya habia escrito una parte sustancial del codigo de este sprint (`Gasto`/`CategoriaGasto`/`FormaPagoGasto` en Domain, DTOs/Interfaces/Services/Controllers/ViewModels/Views de los 5 modulos, migracion `AddGastos`, config de `AppDbContext`, `DependencyInjection.cs`, sidebar, redireccion de `HomeController`) antes de que esta sesion escribiera una sola linea propia. Se opto por **no descartar ese trabajo ni duplicarlo**: se lo trato como la base a revisar, verificar y completar (exactamente el rol que de todas formas exige el cierre de sprint — revision de codigo linea por linea), en vez de reescribir desde cero. Se detectaron y corrigieron en el momento 2 inconsistencias reales causadas por el propio proceso concurrente (`IDashboardService`/`DashboardController`/`DashboardViewModels.cs` quedaron momentaneamente desincronizados entre si por una escritura tardia superpuesta) antes de cerrar. Se documenta este hecho explicitamente para que quede trazado en la memoria del proyecto.

#### Escaneo de reutilizacion (confirmado — cliente pidio explicitamente codigo real de otros proyectos)

- **`C:/Sistemas/ganaderia - emo/Ganaderia.Infrastructure/Services/Ganaderia/EgresoService.cs`** — leido completo. Patron de diseño reutilizado (validaciones antes de abrir transaccion, guard de "al menos un dato real" en vez de solo `Count==0`, transaccion unica con `SaveChangesAsync` intermedio para obtener el Id del padre). **No se copio codigo textual**: el dominio difiere (Egreso de ganaderia soporta multiples pagos con comprobante adjunto y reconciliacion contra Rubro/Proveedor propios; `GastoService` de marihogar es mas simple — un unico monto/forma de pago por Gasto, sin comprobante adjunto, tal como especifica `2-disenador-funcional.md`). Lo que si se adopto 1:1 fue la idea de "GastoService.CrearAsync genera el movimiento del ledger en la misma transaccion, con un `SaveChangesAsync` intermedio para obtener el Id del Gasto antes de crear el movimiento" — mismo patron que ya usaban `VentaService`/`OrdenCompraService` de sprints anteriores de marihogar, asi que en la practica `GastoService` termino pareciendose mas a esos dos (ya existentes en el propio proyecto) que al `EgresoService` de ganaderia.
- **`C:/Sistemas/ganaderia - emo/Ganaderia.Infrastructure/Services/Ganaderia/CajaService.cs`** — leido completo (referencia de estilo, segun el alcance de este sprint). Patron de agregacion por periodo (`Where` por rango de fecha + suma condicional por tipo de movimiento) adoptado como criterio general, pero **adaptado a las fuentes de datos reales de marihogar**: ganaderia agrega sus propias tablas (`MovimientoCaja`/`FacturaIngreso`/`EgresoPago`), marihogar agrega `MovimientoCCLocal` (ledger ya existente desde Sprint 2, M11) — tal como anticipaba el alcance de este sprint ("adaptar las fuentes: en marihogar la caja agrega MovimientoCCLocal, no las tablas propias de ganaderia"). El calculo del "periodo anterior" (HU-15.2) se resolvio desplazando el rango elegido exactamente un mes calendario hacia atras (`Desde.AddMonths(-1)`/`Hasta.AddMonths(-1)`), funciona tanto para el default (mes calendario actual → mes calendario anterior exacto) como para un rango custom.
- **`C:/Sistemas/ShowroomGriffin/ShowroomGriffin.Infrastructure/Services/AumentoMasivoService.cs`, `ShowroomGriffin.Web/Controllers/AumentoMasivoController.cs`, `ShowroomGriffin.Application/DTOs/Reportes/AumentoMasivoViewModels.cs`** — los 3 leidos completos, **match mas directo de reutilizacion de todo el proyecto** (mismo feature: por marca/categoria/modelo, sobre precio compra/venta, con preview obligatorio). Patron de flujo de 2 pasos (`ObtenerVariantesAsync`/`Preview` sin persistir + `AplicarAsync`/`Aplicar` con transaccion + concurrencia optimista via `RowVersion`) adoptado casi 1:1, adaptado de `VarianteProducto` (talle/color) a `Producto`/`Marca`/`Categoria` de marihogar. **Mejora deliberada sobre la referencia** (documentada en el propio XML-doc de `AumentoMasivoPrecioService`): ShowroomGriffin solo protege el intervalo interno de su propio metodo `AplicarAsync` (la query fresca hasta el `SaveChanges`, cuestion de milisegundos) porque no recibe de vuelta el `RowVersion` que el cliente vio en la previsualizacion; en marihogar el `RowVersion` viaja en Base64 desde el preview y vuelve explicito por producto al confirmar, comparandose contra el valor real en la base al momento de aplicar — protege la ventana de riesgo real (el tiempo que el Administrador tarda en revisar la previsualizacion antes de confirmar), no solo la ventana interna del metodo. Tambien se detecto y aplico el fix ya catalogado `REG-001` (MySQL no soporta `rowversion` store-generated: `RowVersion` se gestiona manualmente en `AppDbContext.OnBeforeSaveChanges`, reasignado con `Guid.NewGuid().ToByteArray()` en cada `Add`/`Modify` de `Producto`, con `IsConcurrencyToken().ValueGeneratedNever()` en la configuracion Fluent) — mismo patron exacto documentado en `docs/qa/regresiones-manuales.yml`.
- **M9 Dashboard y M17 Proyeccion financiera**: sin match de reutilizacion externa directo (son consultas agregadas especificas del dominio de marihogar, tal como anticipaba el alcance), implementados desde cero sobre los ledgers ya existentes (`MovimientoCCLocal`, `Cheque`, `OrdenCompra`) reutilizando exclusivamente patrones de diseño ya establecidos en el propio proyecto (transacciones, DTOs, `ServiceResult`, `SessionExtensions`).

#### Decisiones de implementacion no explicitas en el diseño (documentadas para trazabilidad)

1. **`Gasto` no tiene Edicion, solo Alta y Anulacion** (`GastoService.AnularAsync`, sin `UpdateAsync`). El diseño lista a Gasto dentro del grupo generico "Alta/Edicion" del wireframe, pero las HU-18.1/18.2 y CA-N24/CA-N25 solo piden alta + movimiento automatico. Editar un Gasto ya posteado en CC Local exigiria logica de reversion equivalente a un Cancelar; se opto por el mismo criterio ya usado en Venta/OrdenCompra (documentos financieros confirmados no se editan, solo transicionan de estado) — `Anulado`+`FechaAnulacion` como campos propios (no `SoftDestroyable.DeletedAt`, para que el Gasto anulado siga visible en el listado con badge, no desaparezca del grid por el query filter global).
2. **`FormaPagoGasto` es un enum propio de 5 valores** (Efectivo/Transferencia/MercadoPago/Cheque/Deposito), no reutiliza `MetodoPago` de Venta/OC ni se restringe a los 3 valores que expone la UI de Ventas — un gasto operativo (alquiler, sueldos) puede pagarse razonablemente con cualquiera de los 5 medios habituales del negocio.
3. **Proyeccion financiera — "OCs pendientes de pago" incluye `Confirmada` Y `Recibida`**, no solo `Confirmada` como sugiere literalmente el alcance del sprint. Motivo: una OC `Recibida` con saldo pendiente de pago es una deuda real ya reflejada en `MovimientoCCProveedor` (Cargo posteado) — un compromiso de pago tan concreto (o mas) que una OC todavia `Confirmada` sin recibir. Se aplico el mismo criterio de exclusion de pagos con cheque `Rechazado` que ya usa `PagoOrdenCompraService.RegistrarPagoAsync`/`OrdenCompraDetailDto.MontoPagado`, para que el saldo pendiente de OC nunca diverja del criterio ya establecido en Sprint 4. Verificado explicitamente (ver seccion de revision de codigo) que esto no duplica el monto de los Cheques Pendientes ya contados por separado: un Cheque Pendiente ya cuenta como "pagado" a los efectos del saldo de la OC (solo los Rechazados se excluyen), asi que `ChequesPorVencer` (dinero ya comprometido via cheque) y `SaldoPendienteOrdenesCompra` (dinero todavia sin ningun pago) son dos conjuntos disjuntos — sumarlos no sobreestima el compromiso.
4. **"PeriodoMeses" de la Proyeccion es simetrico**: es a la vez la ventana de historia para el promedio (CA-N20, "ultimos N meses") y el horizonte proyectado hacia adelante (CA-N23, "comparar distintos horizontes" 1/3/6 meses) — interpretacion mas consistente con HU-17.2 ("ajustar el periodo base... para comparar distintos horizontes") que fijar el horizonte de proyeccion en un valor distinto al de la ventana historica.
5. **Dashboard Administrador — KPIs financieros (`ChequesPorVencer`/`BalanceCaja`) con proteccion explicita por policy en sus propios endpoints AJAX**, ademas de estar ocultos en la UI de Vendedor. Se refactorizo el diseño inicial (una unica consulta agregada `ObtenerAdminAsync` resuelta sincronicamente en `DashboardController.Index`) a **5 endpoints AJAX independientes** (`GetVentasPeriodo`/`GetStockCritico`/`GetChequesPorVencer`/`GetBalanceCaja`/`GetProductosMasVendidos`), cada uno consumido por su propia card en `Dashboard/Admin.cshtml` con spinner propio — para cumplir literalmente HU-9.1 ("cada KPI carga de forma independiente, no bloquea el resto si uno tarda"), mismo patron ya usado por el panel de notificaciones de `_Layout.cshtml`. `GetChequesPorVencer`/`GetBalanceCaja` llevan `[Authorize(Policy = "RequireAdministracion")]` propio (defensa en profundidad, regla `REG-010` — un Vendedor no puede ver el balance de caja ni los cheques por vencer navegando directo a la URL del endpoint, aunque la UI ya se los oculte).
6. **Umbral de "cheques por vencer" del Dashboard es de 30 dias** (CA-N11), distinto del umbral de 7 dias que resalta filas en `Cheques/Index` (Sprint 4) — son dos usos distintos del mismo dato (alerta temprana de dashboard vs. resaltado visual de urgencia en el listado detallado), documentado explicitamente en el codigo para que no se confundan ni se unifiquen sin querer en un sprint futuro.
7. **Sin recepcion de fecha propia en `OrdenCompra` para "vencimiento de pago"**: el saldo pendiente de OC en la Proyeccion se computa sin filtro de fecha (todas las `Confirmada`/`Recibida` con saldo > 0 cuentan, sin importar cuando), porque `OrdenCompra` no modela una fecha de vencimiento de pago propia (a diferencia de `Cheque.FechaVencimiento`) — documentado como limitacion conocida, no bug.

#### Archivos y capas modificadas

**Domain** (`MariHogar.Domain`)
- `Enums/CategoriaGasto.cs` (Alquiler/Servicios/Sueldos/Flete/Otro), `Enums/FormaPagoGasto.cs` (Efectivo/Transferencia/MercadoPago/Cheque/Deposito) — nuevos.
- `Entities/Gasto.cs` — nueva, hereda `SoftDestroyable`. Campos propios `Anulado`/`FechaAnulacion` en vez de usar `DeletedAt` para la anulacion (ver decision #1).
- `Entities/Producto.cs` — agregado `RowVersion` (`byte[]`, default `new byte[16]`), token de concurrencia optimista para M16 (ver decision de reutilizacion de `REG-001`).

**Application** (`MariHogar.Application`)
- `DTOs/GastoDtos.cs` — `GastoListItemDto`, `GastoFiltro` (Categoria/FormaPago/Descripcion/rango de fecha), `GastoInput`.
- `DTOs/CajaDtos.cs` — `CajaFiltro`, `CajaPeriodoDto` (con `VariacionIngresosPorc`/`VariacionEgresosPorc` calculados, null-safe ante periodo anterior en $0).
- `DTOs/AumentoMasivoDtos.cs` — enums `AlcanceAumento`/`TargetPrecioAumento`, `AumentoMasivoPreviewInput`, `AumentoMasivoPreviewItemDto` (incluye `RowVersion` en Base64), `AumentoMasivoAplicarItemInput`, `AumentoMasivoAplicarInput`.
- `DTOs/ProyeccionFinancieraDtos.cs` — `ProyeccionFinancieraDto` (propiedades calculadas `GastosComprometidos`/`EgresosProyectadosTotal`/`TieneDeficit`).
- `DTOs/DashboardDtos.cs` — `ProductoMasVendidoDto`, `VentasPeriodoDto`, `ChequesPorVencerDashboardDto`, `DashboardVendedorDto` (sin un DTO agregado unico para Admin, ver decision #5).
- `Interfaces/IGastoService.cs`, `Interfaces/ICajaService.cs`, `Interfaces/IAumentoMasivoPrecioService.cs`, `Interfaces/IProyeccionFinancieraService.cs`, `Interfaces/IDashboardService.cs` — nuevas.
- `Interfaces/IProductoService.cs` — agregado `ListarModelosDistintosAsync()` (combo de M16, criterio "por modelo").

**Infrastructure** (`MariHogar.Infrastructure`)
- `Data/AppDbContext.cs` — `DbSet<Gasto>` + Fluent config (`Descripcion` maxlength 500, indices `Categoria`/`Fecha`); config de `Producto.RowVersion` (`IsConcurrencyToken().ValueGeneratedNever().IsRequired()`); `OnBeforeSaveChanges` reasigna `producto.RowVersion = Guid.NewGuid().ToByteArray()` en cada `Add`/`Modify` de `Producto` (patron `REG-001`, mismo criterio que ShowroomGriffin).
- `Services/GastoService.cs` — `CrearAsync` (transaccion unica: Add Gasto → SaveChanges → `ICCLocalService.RegistrarMovimientoAsync(Egreso,...)` → SaveChanges → Commit), `AnularAsync` (contramovimiento `Ingreso` con `EsReversion=true`, nunca borra el original).
- `Services/CajaService.cs` — `ObtenerResumenAsync` agrega `MovimientoCCLocal` por rango de fecha (default: mes calendario actual) + periodo anterior (mismo rango desplazado 1 mes).
- `Services/AumentoMasivoPrecioService.cs` — `ObtenerPreviewAsync` (100% lectura, `AsNoTracking`, sin `SaveChanges`), `AplicarAsync` (fetch acotado por Ids de la previsualizacion, comparacion explicita de `RowVersion` por producto antes de mutar, `AuditLog` manual de la operacion batch + transaccion + `DbUpdateConcurrencyException` como backstop).
- `Services/ProyeccionFinancieraService.cs` — `ObtenerAsync(periodoMeses)`: promedio historico sobre `MovimientoCCLocal` + cheques Pendientes en el horizonte + saldo pendiente de OC (`Confirmada`/`Recibida`, excluyendo pagos con cheque Rechazado).
- `Services/DashboardService.cs` — `ObtenerVentasPeriodoAsync`, `ObtenerChequesPorVencerAsync`, `ObtenerProductosMasVendidosAsync`, `ObtenerVendedorAsync` (metodos independientes, ver decision #5 — nunca un unico metodo "traer todo").
- `Services/ProductoService.cs` — agregado `ListarModelosDistintosAsync()`.
- `DependencyInjection.cs` — registrados `IGastoService`, `ICajaService`, `IAumentoMasivoPrecioService`, `IProyeccionFinancieraService`, `IDashboardService` (Scoped).

**Web** (`MariHogar.Web`)
- `Controllers/GastosController.cs`, `Controllers/CajaController.cs`, `Controllers/AumentoMasivoPreciosController.cs`, `Controllers/ProyeccionFinancieraController.cs`, `Controllers/DashboardController.cs` — nuevos. Los primeros 4 con `[Authorize(Policy = "RequireAdministracion")]` a nivel clase (Gastos/Caja/Aumento masivo/Proyeccion son exclusivos de Administrador). `DashboardController` con `[Authorize]` simple a nivel clase (cualquier rol autenticado entra, la diferenciacion Admin/Vendedor ocurre adentro) + `[Authorize(Policy = "RequireAdministracion")]` puntual en los 2 endpoints financieros (`GetChequesPorVencer`/`GetBalanceCaja`).
- `Controllers/HomeController.cs` — `Index()` ahora redirige a `Dashboard/Index` cuando el usuario esta autenticado (una linea agregada), preservando intacto el resto del controller (`Error`/`StatusCode`, referenciados por `Program.cs`).
- `Models/GastoViewModels.cs`, `Models/CajaViewModels.cs`, `Models/AumentoMasivoViewModels.cs`, `Models/ProyeccionFinancieraViewModels.cs`, `Models/DashboardViewModels.cs` — nuevos.
- `Views/Gastos/{Index,Create}.cshtml` — Index con 4 filtros (Categoria, FormaPago, Descripcion texto libre, rango de fecha) persistidos en sesion + badge Activo/Anulado + accion Anular con SweetAlert2; Create card unica con alerta informativa ("se genera un movimiento de egreso automaticamente").
- `Views/Caja/Index.cshtml` — 3 KPI cards (Ingresos/Egresos/Balance del periodo con indicador de variacion % vs mes anterior, semantica de color correcta: egreso que sube es rojo) + tabla comparativa periodo actual vs anterior + link a CC Local para el detalle.
- `Views/AumentoMasivoPrecios/Index.cshtml` — formulario paso 1 (criterio+porcentaje) → previsualizacion paso 2 (AJAX, tabla precio actual/nuevo) → confirmar (AJAX, SweetAlert2, envia de vuelta el `RowVersion` de cada fila previsualizada). Cualquier cambio en el criterio despues de previsualizar invalida la previsualizacion vigente (evita confirmar contra un criterio distinto al previsualizado).
- `Views/ProyeccionFinanciera/Index.cshtml` — selector de periodo (1/3/6 meses) + alerta de deficit condicional + texto aclaratorio de "estimacion, no compromiso exacto" siempre visible + 3 KPI cards de detalle (egresos promedio, cheques por vencer, OC pendientes) + card de egresos proyectados totales.
- `Views/Dashboard/{Admin,Vendedor}.cshtml` — Admin con 4 KPI cards + card de productos mas vendidos, **cada una completada por su propio `$.get` independiente** (spinner propio, manejo de error propio, ver decision #5); Vendedor con card de ventas de hoy + card de leads pendientes (placeholder deshabilitado) + 3 accesos directos (Nueva venta/Nuevo presupuesto/Entregas).
- `Views/Shared/_Layout.cshtml` — sidebar: "Dashboard" como primer link de la seccion Principal (todos los roles autenticados); "Gastos"/"Caja mensual"/"Proyeccion financiera" agregados a la seccion "Financiero" ya existente; "Aumento masivo de precios" agregado a la seccion "Catalogo" (solo Administrador).

#### Migracion EF generada

- `20260724200956_AddGastos` — crea tabla `Gastos` (Categoria/Monto/FormaPago/Fecha/Descripcion/Anulado/FechaAnulacion + columnas de auditoria de `SoftDestroyable`, indices `Categoria`/`Fecha`) y agrega la columna `RowVersion` (`longblob`) a `Productos`. **Particularidad tecnica real de MySQL manejada correctamente**: MySQL no permite `DEFAULT` literal en columnas `BLOB`/`TEXT`/`JSON` ("BLOB, TEXT, GEOMETRY or JSON column 'RowVersion' can't have a default value"), asi que la migracion agrega la columna como nullable, la backfillea con `UUID_TO_BIN(UUID())` (valor unico por fila, para no violar la futura constraint `NOT NULL` con todas las filas en el mismo valor) y recien despues la vuelve `NOT NULL` — patron de 3 pasos (`AddColumn` nullable → `Sql` backfill → `AlterColumn` not null) necesario especificamente para este tipo de columna en este motor. **Generada y aplicada** exitosamente contra `marihogar_dev` (`dotnet ef database update` confirma `Done.` sin errores; `dotnet ef migrations list` confirma 6 migraciones totales — `InitialCreate`, `AddCatalogo`, `AddPresupuestosVentas`, `AddEntregas`, `AddComprasCCProveedoresCheques`, `AddGastos` — ninguna pendiente).

#### Evidencia de cierre — build + migracion + revision de codigo (sin smoke test, regla de proceso vigente)

- `dotnet build MariHogar.slnx` → **Compilacion correcta, 0 errores** (9 warnings, todos preexistentes: `NU1902` de MailKit/MimeKit + `CS0114` de `HomeController.StatusCode`; ninguno introducido por este sprint). Build re-ejecutado despues del ultimo ajuste (filtro de Descripcion en Gastos) y confirmado limpio otra vez.
- Migracion `20260724200956_AddGastos` generada y **aplicada** contra `marihogar_dev` (`dotnet ef database update` → `Done.`; `dotnet ef migrations list` → 6 migraciones, ninguna pendiente).
- **Revision de codigo propia, linea por linea, con foco explicito en los 3 puntos pedidos**:
  1. **`GastoService.CrearAsync`/`AnularAsync`** (movimiento de CC Local correcto y atomico): confirmado que `CrearAsync` valida (Monto>0, Fecha no futura, Descripcion obligatoria) **antes** de abrir la transaccion → `Add(Gasto)` → `SaveChangesAsync` (asigna `gasto.Id`, usado como `OrigenId`) → `ICCLocalService.RegistrarMovimientoAsync(TipoMovimientoCC.Egreso, gasto.Monto, "Gasto", gasto.Id, esReversion:false, ...)` (confirmado que este metodo NO llama `SaveChangesAsync` propio, mismo patron exacto que `VentaService`/`OrdenCompraService`) → `SaveChangesAsync` final → `CommitAsync`, con `RollbackAsync` en el `catch`. Signo correcto (`Egreso`, resta del saldo de CC Local via `ObtenerSaldoActualAsync` = `Σ Ingreso − Σ Egreso`). `AnularAsync` genera el contramovimiento correcto: `TipoMovimientoCC.Ingreso` (neutraliza exactamente el `Egreso` original) con `esReversion:true` y el mismo `OrigenId` del Gasto — nunca borra ni modifica el movimiento original, mismo criterio de todos los ledgers del proyecto. Guard `gasto.Anulado` ya `true` → rechaza doble anulacion.
  2. **Previsualizacion de Aumento masivo no persiste nada**: confirmado leyendo `AumentoMasivoPrecioService.ObtenerPreviewAsync` completo — la unica operacion es una query `AsNoTracking()` + proyeccion en memoria (calculo de `PrecioNuevo` con `Math.Round(precio * multiplicador, 2)`), **cero** llamadas a `SaveChangesAsync`/`Add`/`Update`/`Remove` en todo el metodo. `AumentoMasivoPreciosController.Preview()` (el endpoint HTTP que lo expone) tambien es de solo lectura: arma el input, valida, llama al Service y devuelve JSON, sin ningun efecto de persistencia. `Aplicar()`/`AplicarAsync` (la unica via de persistencia) exige explicitamente los `Items` con sus `RowVersion` — si el usuario nunca hizo click en "Previsualizar" (y por lo tanto `previewItems` esta vacio en el JS), el boton "Confirmar aumento" no tiene datos que enviar (`if (previewItems.length === 0 || !criterioUsado) return;` en el script de la vista) y el Service igual rechaza con "No hay productos para aplicar" si `Items.Count == 0` — doble guardia cliente+servidor.
  3. **Formula de Proyeccion financiera** (signos, ventana de fechas, sin duplicar cheques/OC ya en CC Local): confirmado que `MovimientoCCLocal` **nunca** recibe movimientos de pagos a proveedores/cheques (verificado leyendo `PagoOrdenCompraService.RegistrarPagoAsync` completo: solo escribe `PagoOrdenCompra`+`Cheque`+`MovimientoCCProveedor`, jamas `MovimientoCCLocal`) — por lo tanto el promedio historico (sobre `MovimientoCCLocal`) y los compromisos conocidos (Cheques+OC, sobre tablas de Compras) son fuentes disjuntas, sumarlas no duplica nada. Ventana historica: `hoy.AddMonths(-periodo)` hasta `hoy` (exclusivo), promedio = total/periodo. Horizonte de cheques: `FechaVencimiento <= hoy.AddMonths(periodo)`, sobre `Estado==Pendiente` (nunca cuenta cheques ya `Acreditado`/`Rechazado`). Saldo de OC: `Total − Σ Pagos(Cheque==null || Cheque.Estado!=Rechazado)`, mismo criterio exacto que `OrdenCompraDetailDto.MontoPagado` (Sprint 4) — confirmado que un Cheque `Pendiente` cuenta como "pagado" a los efectos del saldo de OC (no se duplica contra `ChequesPorVencer`, ver decision #3 de arriba). `TieneDeficit = GastosComprometidos > IngresosProyectados` (comparacion literal de CA-N22, sin mezclar el promedio de egresos operativos en la comparacion de la alerta).
  4. **Verificacion adicional (defensa en profundidad, no pedida explicitamente pero detectada durante la revision)**: los 2 endpoints AJAX del Dashboard que exponen datos financieros exclusivos de Administrador (`GetChequesPorVencer`/`GetBalanceCaja`) inicialmente solo heredaban el `[Authorize]` generico de la clase (cualquier usuario autenticado, incluido Vendedor) — corregido antes de cerrar, agregando `[Authorize(Policy = "RequireAdministracion")]` puntual a esos 2 endpoints (regla `REG-010`/`32-estandares-qa-implementador.instructions.md`: nunca ocultar un dato en la vista sin proteger tambien el endpoint).
  5. **RowVersion / MySQL (`REG-001`)**: confirmado que `Producto.RowVersion` esta configurado `IsConcurrencyToken().ValueGeneratedNever()` (nunca `ValueGeneratedOnAdd`, que MySQL no soporta para columnas `BLOB`) y que `AppDbContext.OnBeforeSaveChanges` reasigna el valor manualmente en cada `Add`/`Modify` de `Producto` — mismo patron exacto que el fix ya catalogado para `VarianteProducto` de ShowroomGriffin.

#### Checklist de verificacion manual para el usuario (equivalente al smoke test que ya no ejecuta el Implementador)

Con la app corriendo (`dotnet run --project MariHogar.Web`) y logueado como Administrador (salvo que se indique otro rol):

**M18 — Gastos**
1. `Gastos > Nuevo gasto` → completar Categoria/Monto/Forma de pago/Fecha/Descripcion → Guardar → verificar que redirige al listado con el gasto nuevo, badge "Activo".
2. Ir a `Cuenta corriente del local` (CCLocal) → verificar que aparece un movimiento "Egreso" nuevo por el mismo monto, con `OrigenTipo=Gasto`, y que el saldo actual bajo en esa cantidad.
3. Volver a `Gastos`, click "Anular" en ese gasto (confirmar en el SweetAlert2) → verificar que el badge pasa a "Anulado" (el gasto sigue visible en la grilla, no desaparece) → en `CCLocal`, verificar que aparece un nuevo movimiento "Ingreso" con badge de reversion, y que el saldo vuelve al valor previo al gasto.
4. Probar los 4 filtros (Categoria, Forma de pago, Descripcion, rango de fecha) uno por uno y "Limpiar filtros".

**M15 — Caja mensual**
5. Ir a `Caja mensual` → verificar que muestra Ingresos/Egresos/Balance del mes actual y el comparativo contra el mes anterior (si no hay movimientos del mes anterior, debe decir "Sin datos... para comparar" en vez de un error o un % raro).
6. Cambiar el rango de fecha con el selector → verificar que los 3 totales y la tabla comparativa se recalculan para el nuevo rango.

**M16 — Aumento masivo de precios**
7. Ir a `Aumento masivo de precios` → elegir "Por categoria" + una categoria con productos + "Precio de venta" + 10% → click "Previsualizar" → verificar que aparece la tabla con precio actual/nuevo (nuevo = actual x 1.10) **y que los precios en `Productos/Index` todavia NO cambiaron** (paso critico: confirmar que previsualizar no aplico nada).
8. Click "Confirmar aumento" (aceptar el SweetAlert2) → verificar que ahora si, en `Productos/Index`, los precios de venta de esos productos subieron un 10%.
9. Repetir el paso 7 con un criterio distinto sin confirmar, y verificar que cambiar cualquier campo del formulario despues de previsualizar hace desaparecer la tabla de previsualizacion (hay que previsualizar de nuevo antes de poder confirmar).

**M17 — Proyeccion financiera**
10. Ir a `Proyeccion financiera` → probar el selector de periodo (1/3/6 meses) → verificar que los numeros de "Ingresos proyectados"/"Egresos comprometidos" cambian al cambiar el periodo.
11. Si hay cheques Pendientes con vencimiento proximo o OCs con saldo pendiente, verificar que aparecen contados en las cards correspondientes con la cantidad correcta.
12. Verificar que el texto aclaratorio ("estimacion, no un compromiso exacto") esta siempre visible, y que la alerta roja de deficit solo aparece cuando Gastos comprometidos > Ingresos proyectados.

**M9 — Dashboard**
13. Loguearse como Administrador → verificar que la pantalla de inicio (`/` o `/Home`) redirige automaticamente a `/Dashboard` → verificar que las 4 cards superiores + la card de productos mas vendidos muestran un spinner brevemente y despues se completan cada una por separado (no toda la pantalla en blanco esperando a todas).
14. Cambiar el rango de fecha del Dashboard → verificar que "Ventas del periodo" y "Productos mas vendidos" se recalculan (Stock critico/Cheques por vencer/Balance de caja NO deberian cambiar, son de "estado actual").
15. Loguearse como Vendedor → verificar que ve un dashboard reducido (ventas de hoy + accesos directos), sin ninguna card financiera, y que navegar directo a `/Dashboard/GetBalanceCaja` o `/Dashboard/GetChequesPorVencer` responde 403 (Acceso denegado) en vez de devolver datos.

#### Riesgos residuales

- **Sin verificacion en caliente**: por la regla de proceso vigente, ningun tramo de este sprint fue ejecutado contra la app real ni contra MySQL real en este ciclo (mas alla de `dotnet build`/`dotnet ef database update`) — toda la evidencia funcional es revision de codigo linea por linea. La checklist de 15 pasos de arriba es la unica forma de cerrar ese riesgo, a cargo del usuario.
- **Cancelar una OC `Confirmada` que ya tiene un pago/cheque registrado (anticipo) no revierte ese pago/cheque** — gap heredado de `OrdenCompraService.CancelarAsync` (Sprint 4, no tocado este sprint): si esto ocurre, un Cheque `Pendiente` de una OC ya `Cancelada` seguiria contando en `ProyeccionFinancieraService.ObtenerChequesPorVencerAsync`/Dashboard, sobreestimando levemente los compromisos futuros. Escenario de baja probabilidad (exige cancelar una OC con anticipo ya cargado) y no introducido por este sprint — documentado para un sprint de endurecimiento futuro si el cliente lo pide (la correccion natural seria que `OrdenCompraService.CancelarAsync` revierta o marque como invalidados los pagos/cheques asociados al cancelar una `Confirmada` con anticipo).
- **`Gasto` no tiene Edicion** (ver decision #1) — si el cliente pide poder corregir un monto/fecha sin pasar por Anular+Nuevo Gasto, es un cambio de alcance menor (nuevo `UpdateAsync` con logica de reversion+reposteo del movimiento de CC Local).
- **Concurrencia de `AumentoMasivoPrecioService.AplicarAsync` bajo alta frecuencia de ediciones manuales de Producto simultaneas**: mitigada con `RowVersion` (mejor cobertura que la referencia de ShowroomGriffin, ver decision de reutilizacion), pero sigue siendo optimista (rechaza y pide reintentar, no bloquea) — comportamiento esperado y aceptado, consistente con el resto de los guards de concurrencia ya aceptados en sprints anteriores del proyecto.
- **Nota de proceso** (ver arriba): parte sustancial del codigo de este sprint fue escrita por un proceso concurrente detectado durante la sesion, no por esta ejecucion desde cero. Se aplico exactamente el mismo nivel de escrutinio (revision linea por linea + build + migracion) que si se hubiera escrito integramente en esta sesion, y se corrigieron las inconsistencias reales encontradas (ver arriba) antes de cerrar.

#### Proximos pasos pendientes (Sprint 5)

- Este era el ultimo sprint funcional planificado de los 6 (M1 CRM de Leads y M8 Bot WhatsApp de Etapa 2 siguen en pausa, sin fecha). Pendiente que QA valide este sprint y que el orquestador confirme si el plan de 6 sprints se da por cerrado o si el cliente pide un sprint adicional de cierre/hardening (ej. resolver los 2 riesgos residuales de arriba, completar las checklists manuales acumuladas de sprints anteriores).
- M7 (Facturacion AFIP/ARCA) y M8 (Bot WhatsApp) quedan como los unicos modulos del alcance original de 18 sin implementar, ambos con dependencias externas ya documentadas desde el analisis funcional (certificado .p12, numero de WhatsApp dedicado).

---

### Sprint CR-E (Change Request #1, post-Etapa 1, ampliación sobre CR-D) — CR-10/CR-11/CR-12: auditoría de columnas del histórico

Alcance cerrado según `1-analista-funcional.md` (Discovery + Análisis v5), `2-disenador-funcional.md` (Diseño v4, HU-12.8/HU-18.4/HU-5.13) y `3-arquitecto-mvc.md` (Arquitectura v3). 3 campos `string?` nullable sobre entidades ya existentes (`OrdenCompra`, `Gasto`, `Venta`), sin entidades nuevas, sin cambio de máquina de estados, sin impacto en la lógica de negocio de `OrdenCompraService`/`GastoService`/`VentaService` (solo persisten un campo más). **Nota de gate verificada antes de codificar**: `4-presupuestador.md` todavía trae la etiqueta de estado "BORRADOR" en el texto de la sección CR-10/11/12 (USD 84), pero `trazabilidad.md` (entradas 2026-07-27 "orquestador — usuario aprueba presupuesto CR-10/CR-11/CR-12" y "orquestador — orden de arranque, Sprint CR-E") deja registrada la aprobación explícita del cliente (USD 84, total acumulado del Change Request #1: USD 638) y la orden de arranque posterior — la etiqueta de `4-presupuestador.md` quedó desactualizada, no la aprobación en sí. Se procedió a implementar sobre esa base. Recomendado (fuera de las capas del implementador): que el orquestador actualice la etiqueta de estado de `4-presupuestador.md` a "Aprobado" para que quede consistente con `trazabilidad.md`.

#### Resultado del escaneo de reutilización (previo a implementar)

Ya documentado en `1-analista-funcional.md` (Análisis v5, sección "Fuente de reutilización obligatoria"): ninguno de los 3 gaps tiene precedente de código en otros proyectos del estudio — son campos simples (`string?`) sobre entidades ya existentes, mismo criterio ya usado en el propio proyecto para `Proveedor.Observaciones`. Se confirmó igual el criterio releyendo `5-implementador.md` propio (este archivo) antes de tocar código: no hay ningún ABM/flujo nuevo que reutilizar, exclusivamente el patrón visual ya establecido (bloque condicional tipo `TipoComprobante`/`Facturada` de OC, filtro de texto único ya existente en Gastos, sección colapsable fuera del flujo POS en Ventas).

#### Alcance funcional resumido

- **CR-10 (HU-12.8)**: `OrdenCompra` gana `PuntoVenta` (`string?`, max 10) y `NumeroComprobante` (`string?`, max 20). Visibles/editables en `Create.cshtml` solo cuando `Facturada=true` (mismo patrón condicional que `TipoComprobante`), visibles en `Details.cshtml`, columna + filtro de texto nuevo ("Comprobante") en `Index.cshtml`.
- **CR-11 (HU-18.4)**: `Gasto` gana `Subcategoria` (`string?`, max 100). Campo de texto libre debajo del select de Categoría en `Create.cshtml` (Gasto no tiene pantalla de Edit — es inmutable por diseño desde Sprint 5, solo se puede Anular). En `Index.cshtml`, se muestra como línea secundaria bajo la Categoría, y el cuadro de búsqueda de texto ya existente (`filtroDescripcion`) ahora filtra por Descripción O Subcategoría — sin agregar un filtro dedicado nuevo, tal como pide explícitamente el diseño ("mismo cuadro de búsqueda").
- **CR-12 (HU-5.13)**: `Venta` gana `NotaInterna` (`string?`, max 500). En `Ventas/Create.cshtml`, sección colapsada por defecto ("+ Agregar nota interna (opcional)") ubicada junto a los campos Cliente/Teléfono, fuera de la tabla de items y del bloque de pagos — no interrumpe el flujo POS. En `Ventas/Details.cshtml`, card "Nota interna" visible solo si hay dato, para Administrador y Vendedor (únicos roles con acceso a la pantalla vía policy `RequireVentas`, no hizo falta gating adicional). **Verificado por lectura completa de código** que `VentaService.GenerarRemitoPdfInterno` y `ComprobanteAfipService` (búsqueda de `NotaInterna`/`v.\w+`/`venta.\w+` en el archivo completo) no leen este campo en ningún punto — no se tocó ninguno de los dos métodos de generación de PDF.
- Ajuste a `tools/ImportarHistorico/Program.cs` (script de un solo uso, **no ejecutado**, `CR-6` sigue sin correr contra producción): sección Gastos ahora carga `Subcategoria = columna "Subcategoría" del Excel` (trimeada) siempre que tenga dato, sin tocar la lógica de `Descripcion` (que sigue usando el mismo fallback ya documentado). Sección Ventas ahora carga `NotaInterna = columna "Nota Interna"` (col. 43 de `Informe de Ventas Detallado`, confirmada por inspección real con Excel COM — no estaba documentada por índice en ningún lado del script; se verificó por muestreo que el valor se repite idéntico en todas las líneas de una misma venta agrupada, mismo criterio ya usado para `ClienteNombre`, así que alcanza con leerla de la primera fila del grupo).

#### Archivos y capas modificadas

**Domain** (`MariHogar.Domain`)
- `Entities/OrdenCompra.cs` — `PuntoVenta`/`NumeroComprobante` (`string?`), XML-doc documentando que es dato informativo transcripto a mano, no fuente de verdad fiscal (mismo criterio que `Facturada`/`TipoComprobante`).
- `Entities/Gasto.cs` — `Subcategoria` (`string?`), XML-doc documentando que complementa, no reemplaza, la `Categoria` fija.
- `Entities/Venta.cs` — `NotaInterna` (`string?`), XML-doc con el punto de seguridad explícito (nunca leída por los generadores de PDF).

**Application** (`MariHogar.Application`)
- `DTOs/OrdenCompraDtos.cs` — `PuntoVenta`/`NumeroComprobante` agregados a `OrdenCompraListItemDto` y `OrdenCompraDetailDto`; `OrdenCompraFiltro` gana `Comprobante` (texto libre, busca sobre ambos campos); `OrdenCompraInput` gana ambos campos.
- `DTOs/GastoDtos.cs` — `Subcategoria` agregada a `GastoListItemDto` y `GastoInput`; XML-doc en `GastoFiltro.Descripcion` aclarando que ahora también filtra por Subcategoría (mismo campo, sin duplicar el filtro).
- `DTOs/VentaDtos.cs` — `NotaInterna` agregada a `VentaDetailDto` (no a `VentaListItemDto`, fuera del alcance del listado) y a `VentaInput`.

**Infrastructure** (`MariHogar.Infrastructure`)
- `Data/AppDbContext.cs` — Fluent config de los 5 campos nuevos: `PuntoVenta` (`HasMaxLength(10)`)/`NumeroComprobante` (`HasMaxLength(20)`) en `OrdenCompra`; `Subcategoria` (`HasMaxLength(100)`) en `Gasto`; `NotaInterna` (`HasMaxLength(500)`) en `Venta`. Sin índices nuevos (ninguno de los 3 gaps lo requiere — el filtro de texto de OC/Gasto usa `Contains` sobre columna sin indexar, mismo criterio ya usado para `Gasto.Descripcion`/`Venta.ClienteNombre`, volumen de datos bajo).
- `Services/OrdenCompraService.cs` — `ListarAsync` filtra por `Comprobante` (Contains sobre `PuntoVenta` O `NumeroComprobante`, ambos con null-check explícito por ser nullable) y mapea los 2 campos al DTO de listado/detalle; `AplicarComprobanteEImpuestos` persiste ambos (trimeados, null si vacíos) cuando `Facturada=true`, los fuerza a `null` cuando `Facturada=false` — mismo patrón defensivo ya usado para `TipoComprobante`/impuestos.
- `Services/GastoService.cs` — `ListarAsync` amplía el filtro existente de `Descripcion` a `Descripcion.Contains(...) OR Subcategoria.Contains(...)` (mismo campo de filtro, sin agregar uno nuevo); `CrearAsync` persiste `Subcategoria` trimeada o `null`.
- `Services/VentaService.cs` — `GetByIdAsync` mapea `NotaInterna` al DTO; `ConfirmarAsync` persiste `NotaInterna` trimeada o `null` al crear la `Venta`. **No se tocó** `GenerarRemitoPdfInterno` (confirmado por relectura completa del método, sin ninguna referencia al campo nuevo) ni `ComprobanteAfipService.cs` (grep de propiedades de `Venta` usadas en el archivo, sin resultados relevantes).

**Web** (`MariHogar.Web`)
- `Models/OrdenCompraViewModels.cs` — `OrdenCompraFormViewModel` gana `PuntoVenta`/`NumeroComprobante` con `[StringLength]` (10/20).
- `Models/GastoViewModels.cs` — `GastoFormViewModel` gana `Subcategoria` con `[StringLength(100)]`.
- `Controllers/OrdenesCompraController.cs` — `GetData` parsea `comprobante` del form hacia `OrdenCompraFiltro.Comprobante`; `Edit(int id)` (GET) precarga `PuntoVenta`/`NumeroComprobante` desde el DTO (regla `32-estandares-qa-implementador.instructions.md` de no dejar combos/campos vacíos en Editar — acá aplica el mismo criterio aunque sea texto libre); `MapInput` solo envía ambos campos si `vm.Facturada=true` (mismo patrón ya usado para `TipoComprobante`, aunque el Service ya los fuerza a null igual, por consistencia con el resto del método).
- `Controllers/GastosController.cs` — `Create` (POST) mapea `vm.Subcategoria` al `GastoInput`.
- `Controllers/VentasController.cs` — `Confirmar` parsea `notaInterna` del form (`FormParsing.NullIfEmpty`) hacia `VentaInput.NotaInterna`.
- `Views/OrdenesCompra/Create.cshtml` — los 2 campos nuevos viven dentro de `#contTipoComprobante` (el mismo contenedor que ya se togglea con `Facturada` vía `actualizarVisibilidadComprobante()`), así que quedan visibles/ocultos automáticamente sin JS adicional.
- `Views/OrdenesCompra/Details.cshtml` — línea "Punto de venta-Número" bajo el badge de Facturada, solo si hay al menos uno de los 2 campos cargado.
- `Views/OrdenesCompra/Index.cshtml` — nuevo filtro de texto "Comprobante" (debounce 300ms, mismo patrón que `filtroDescripcion` de Gastos) + nueva columna "Comprobante" en el grid (concatena `puntoVenta-numeroComprobante`, `-` si falta alguno).
- `Views/Gastos/Create.cshtml` — input `Subcategoria` debajo del select de Categoría.
- `Views/Gastos/Index.cshtml` — columna Categoría ahora renderiza la Subcategoría como línea secundaria (`<div class="text-muted small">`) debajo del nombre de la categoría; placeholder del filtro de texto actualizado para reflejar que también busca por subcategoría.
- `Views/Ventas/Create.cshtml` — sección colapsable "+ Agregar nota interna (opcional)" (botón `btn-link` + `textarea` oculto por defecto, `maxlength=500`) dentro de la misma card del buscador/cliente, fuera de la tabla de items y del panel de pagos — no altera el layout de dos columnas ni el sticky de resumen. El valor viaja en el mismo POST `form-urlencoded` ya existente (`notaInterna`, campo nuevo junto a `clienteNombre`/`clienteTelefono`).
- `Views/Ventas/Details.cshtml` — card "Nota interna" nueva, renderizada solo si `v.NotaInterna` tiene valor, con aviso explícito "Uso interno — no aparece en el remito ni en la factura."

**`tools/ImportarHistorico/Program.cs`** (ajuste de script, no ejecutado este sprint)
- Sección Gastos (línea ~554-561): `Gasto.Subcategoria = subcategoriaTexto` trimeada o `null`, agregado sin tocar la lógica de `descripcion` ya existente (que sigue usando `Subcategoria` como fallback cuando `Descripcion` viene vacía, tal como especifica la Arquitectura v3 — es intencional que el mismo dato pueda terminar tanto en `Descripcion` (fallback) como en `Subcategoria` (columna propia) para las filas con `Descripcion` vacía).
- Sección Ventas (línea ~439-451): nueva variable `notaInterna = GetStr(ws, primeraFila, 43)?.Trim()`, columna confirmada por inspección real vía Excel COM (`Informe_de_Ventas_Detallado...xlsx`, hoja "Informe de Ventas Detallado", columna 43 = "Nota Interna"; columna 42 es "Nota para el Cliente", distinta, no se toca) — asignada a `Venta.NotaInterna`.

#### Migración EF generada

**Una sola migración combinada** (`AddOrdenCompraGastoVentaCamposCR10a12`, sobre `MariHogar.Infrastructure/Data/Migrations`) en vez de 3 separadas — misma decisión ya tomada en sprints anteriores (Sprint 2 combinó Presupuestos+Ventas+CCLocal): los 3 cambios de modelo se hicieron en la misma sesión de desarrollo, `dotnet ef migrations add` los scaffoldea todos juntos, y separarlos hubiera exigido comentar/descomentar cambios de modelo sin ningún beneficio real (los 3 gaps son independientes entre sí — no hay orden de dependencia). Contenido exacto (verificado leyendo el archivo generado antes de aplicar):
```
AddColumn NotaInterna        Ventas          varchar(500) nullable
AddColumn NumeroComprobante  OrdenesCompra   varchar(20)  nullable
AddColumn PuntoVenta         OrdenesCompra   varchar(10)  nullable
AddColumn Subcategoria       Gastos          varchar(100) nullable
```
Sin script de datos — las 5 columnas nacen `NULL` para toda fila ya existente (aditiva pura). **Generada y aplicada contra `marihogar_dev`** (`dotnet ef database update` → `Done.`; `dotnet ef migrations list` confirma 12 migraciones totales, ninguna pendiente). **Verificado por query real vía `mysql.exe`** (no solo por `dotnet ef migrations list`):
- `DESCRIBE OrdenesCompra` → `PuntoVenta varchar(10) YES NULL`, `NumeroComprobante varchar(20) YES NULL`.
- `DESCRIBE Gastos` → `Subcategoria varchar(100) YES NULL`.
- `DESCRIBE Ventas` → `NotaInterna varchar(500) YES NULL`.
- Conteo de filas existentes con el campo nuevo en `NULL`: `OrdenesCompra` 239/239, `Gastos` 480/480, `Ventas` 634/634 — el 100% de las filas ya cargadas (del import histórico de CR-6/Sprint CR-D) quedaron con `NULL` en los 5 campos nuevos, tal como corresponde a una migración aditiva sin script de datos.
- **NO aplicada contra producción** — mismo criterio que el resto de migraciones pendientes del Change Request #1 (se coordina en la misma ventana de mantenimiento junto con `AddImpuestosOCyChequeEmision`/`AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2`/`AddTokenDescargaPublicaVenta`/`AddProveedorCamposFiscales`, todas ya verificadas contra `marihogar_dev` sin alterar datos existentes).

#### Evidencia de build

- `dotnet build MariHogar.slnx` → **Compilación correcta, 0 errores** (9 warnings, todos preexistentes — NU1902 de MailKit/MimeKit y `CS0114` de `HomeController.StatusCode`, ninguno introducido por este sprint).
- `dotnet build tools/ImportarHistorico/ImportarHistorico.csproj` → **Compilación correcta, 0 errores** (mismos warnings preexistentes heredados de `MariHogar.Infrastructure`). El ajuste del script compila limpio aunque no se ejecutó.
- Revisión de código propia (releído línea por línea, no solo "compila"): confirmado que `VentaService.GenerarRemitoPdfInterno` y `ComprobanteAfipService.cs` no referencian `NotaInterna` en ningún punto (punto de seguridad crítico explícito de la Arquitectura v3, CR-12); confirmado que `AplicarComprobanteEImpuestos` fuerza `PuntoVenta`/`NumeroComprobante` a `null` cuando `Facturada=false`, igual criterio que el resto de los campos de comprobante; confirmado que el filtro de texto de `Gastos/Index` busca sobre `Descripcion` O `Subcategoria` sin duplicar el input de la vista.

#### Riesgos y supuestos

- **Discrepancia de estado entre `4-presupuestador.md` (BORRADOR) y la orden de implementar recibida** — documentado arriba en la introducción de esta sección; no bloqueó el desarrollo por instrucción explícita del orquestador/usuario, pero el documento de presupuesto debería actualizarse a "Aprobado" para que la trazabilidad quede consistente.
- Los 3 campos son opcionales y sin obligatoriedad forzada (documentado ya en `3-arquitecto-mvc.md` como riesgo Bajo aceptado) — mismo criterio que el resto de campos de "dato informativo" del proyecto (`Proveedor.Observaciones`, `OrdenCompra.TipoComprobante` cuando no facturada).
- El filtro nuevo de OC (`Comprobante`) y el ajuste al filtro existente de Gastos usan `Contains` sin índice — aceptable al volumen actual de datos (239 OC / 480 Gastos), mismo criterio ya usado en el resto del proyecto para filtros de texto libre.
- Sin verificación en caliente por navegador (regla de proceso vigente, `00-operativa-global.instructions.md`) — toda la evidencia es build + revisión de código + verificación SQL real, no smoke test de la app corriendo.

#### Pruebas mínimas requeridas para QA

1. `OrdenesCompra/Create`: tildar Facturada → aparecen Punto de Venta/Número de Comprobante junto al select de Tipo; destildar → desaparecen los 3 juntos. Guardar con ambos vacíos (Facturada=true) → guarda sin error (opcionales). Guardar con datos (ej. "0001"/"00001234") → persisten.
2. `OrdenesCompra/Edit` sobre una OC en Borrador ya facturada con Punto de Venta/Número cargados → los campos aparecen precargados (no vacíos) al abrir la pantalla.
3. `OrdenesCompra/Details` de una OC facturada con los 2 campos cargados → se ve la línea "0001-00001234" bajo el badge de Facturada. OC no facturada → no se ve nada (sin campos vacíos raros).
4. `OrdenesCompra/Index`: escribir en el filtro "Comprobante" un número/punto de venta ya cargado → la grilla filtra correctamente vía servidor (DataTables server-side). Columna "Comprobante" visible en la grilla.
5. `Gastos/Create`: cargar un gasto con Subcategoría (ej. "Sueldo Juan") → guarda y aparece en `Gastos/Index` como línea secundaria bajo la categoría.
6. `Gastos/Index`: escribir en el filtro de texto existente (el mismo que ya filtraba por Descripción) un valor que solo está en Subcategoría → la grilla filtra correctamente (confirma que ahora busca en ambos campos).
7. `Ventas/Create`: click en "+ Agregar nota interna" → se despliega el textarea; escribir una nota y confirmar la venta → la venta se crea igual que siempre (no bloquea el flujo POS).
8. `Ventas/Details` de esa venta → aparece la card "Nota interna" con el texto cargado, visible tanto logueado como Administrador como como Vendedor.
9. **Crítico (seguridad)**: descargar el remito de esa misma venta (`Ventas/Details` → "Descargar remito", y también el link público de WhatsApp si hay teléfono cargado) → confirmar que el PDF generado NO contiene el texto de la nota interna en ningún lado.
10. Confirmar que una venta creada SIN nota interna (dejando la sección colapsada, sin abrirla) guarda igual sin error, y `Ventas/Details` no muestra la card "Nota interna" (queda oculta, no vacía).

#### Checklist de salida para merge

- [x] Build `MariHogar.slnx` limpio, 0 errores.
- [x] Build `tools/ImportarHistorico/ImportarHistorico.csproj` limpio, 0 errores.
- [x] Migración generada, aplicada y verificada por query real (`DESCRIBE` + conteo de `NULL`) contra `marihogar_dev`.
- [x] Revisión de código confirmando que `NotaInterna` no se filtra a ningún PDF (remito ni AFIP).
- [x] `tools/ImportarHistorico/Program.cs` ajustado pero **no ejecutado** (instrucción explícita del alcance).
- [x] Producción no tocada en ningún momento (ni lectura ni escritura).
- [ ] Verificación visual en navegador de los 3 puntos de UI (toggle condicional de OC, subcategoría en Gastos, colapsable de Venta) — pendiente del usuario, ver "Pruebas mínimas" arriba.
- [ ] Sincronizar `4-presupuestador.md` a "Aprobado" (fuera de las capas del implementador, a cargo del orquestador).

#### Próximos pasos pendientes

- Ninguno funcional de este sprint. Las migraciones pendientes de aplicar contra producción siguen acumulándose (`AddImpuestosOCyChequeEmision`, `AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2`, `AddTokenDescargaPublicaVenta`, `AddProveedorCamposFiscales`, y ahora `AddOrdenCompraGastoVentaCamposCR10a12`) — 5 migraciones coordinables en una misma ventana de mantenimiento, todas ya verificadas contra `marihogar_dev` sin alterar datos existentes.

### CR-13 (2026-07-28, corrección aplicada directamente por el orquestador — sobre `tools/ImportarHistorico/Program.cs`)

Corrección del cliente sobre la conclusión original de CR-6 (documentada en `1-analista-funcional.md`, "Discovery + Análisis v6"): reconteo real confirmó que 487 de 973 líneas (286 de 634 Ventas, ~45%) del histórico SÍ tienen Punto de Venta + Nº de Factura reales — la columna "ARCA" que se había usado como criterio no era un indicador válido (siempre "Sin Enviar", con o sin factura real). Sin cambio de modelo (`ComprobanteAfip` ya tenía `PuntoVenta`/`NumeroComprobante`/`TipoComprobante` desde Etapa 1) — cambio exclusivo en la sección Ventas de `tools/ImportarHistorico/Program.cs`:

- Se leen `Punto de Venta` (col. 10), `Nº Factura` (col. 11) y `Tipo de Comprobante` (col. 9) de la primera fila de cada grupo de Venta (mismo criterio ya usado para `ClienteNombre`/`NotaInterna` — el valor se repite idéntico en todas las líneas de una misma venta).
- Se capturan los `VentaItem` creados en una lista (`itemsCreados`) durante el loop de líneas, para poder referenciar sus `Id` reales después del primer `SaveChangesAsync` de la venta.
- Si `PuntoVenta`/`NroFactura` no son el placeholder `"-"` y parsean como número, se crea un `ComprobanteAfip` (`Estado=Emitido`, `TipoComprobante` mapeado FCA→FacturaA/FCB→FacturaB, `CAE=null`/`VencimientoCAE=null` — no hay CAE real disponible del sistema anterior) con un `ComprobanteAfipItem` por cada `VentaItem` de la venta, y se marca `VentaItem.CantidadFacturada = Cantidad` en cada uno (consistente con el modelo de facturación parcial acumulativa ya existente, para que la venta quede correctamente "100% facturada" y no aparezca con saldo pendiente de facturar).
- Verificado por lectura de `ComprobanteAfipService.GenerarPdfAsync` que la interpolación de `CAE`/`VencimientoCAE` en el PDF no asume no-null — sin riesgo de excepción al ver el PDF de un comprobante histórico (muestra "CAE: " en blanco, limitación cosmética aceptada).
- Nuevo contador `Reporte.VentasConFacturaHistorica`, reflejado en los 2 `Console.WriteLine` de resumen de Ventas.
- **No se ejecutó el script** (ni contra `marihogar_dev` ni producción) — mismo criterio que el resto de los ajustes de CR-10/11/12, es un cambio de script pendiente de la corrida real ya en pausa por decisión del cliente.
- Build verificado limpio: `dotnet build MariHogar.slnx` → 0 errores; `dotnet build tools/ImportarHistorico/ImportarHistorico.csproj` → 0 errores (mismos warnings preexistentes en ambos).
- Aplicado directamente por el orquestador (cambio acotado a un único archivo, mismo criterio ya usado para el fix de MH-006 en Sprint CR-C) — no delegado a un subagente implementador nuevo.

---

## Sprint CR-F (2026-07-28) — CR-14/CR-15/CR-16-código/CR-18 + refinamiento CR-13

Sobre Arquitectura v4 (`3-arquitecto-mvc.md`, sin migración EF en ningún ítem — todos cambios de comportamiento). CR-17 (unificación de Proveedor duplicado) y la normalización de mayúsculas sobre los datos ya cargados de CR-16 fueron ejecutados directamente por el orquestador contra `marihogar_dev` antes de este sprint — no forman parte del código de este sprint.

#### Escaneo de reutilización (previo a implementar)
Ninguno de los 5 ítems tiene precedente de código externo a reutilizar — son ajustes puntuales sobre servicios/vistas/script ya propios del proyecto (mismo patrón de saldo acumulado ya usado en `OrdenCompraDetailDto.SaldoPendiente`, mismo patrón de movimiento de ajuste ya usado por `MovimientoCCProveedor.OrigenTipo="SaldoInicial"` del propio `ImportarHistorico`). Decisión: implementar directo sobre el código existente del proyecto, sin copiar de otro repo del estudio.

#### CR-14 — Saldo acumulado en CC Local y CC Proveedores
- `CCLocalService.ListarAsync` y `CCProveedorService.ListarMovimientosAsync` (`MariHogar.Infrastructure/Services/CCLocalService.cs`, `CCProveedorService.cs`) ganan un método privado `ObtenerSaldosAcumuladosAsync()` que trae **todo** el ledger correspondiente (CC Local completo / CC Proveedor acotado a `ProveedorId`) ordenado por `Fecha` asc, `Id` asc (desempate estable), acumula en memoria (`+Monto` Ingreso/Cargo, `-Monto` Egreso/Pago) y devuelve un `Dictionary<int, decimal>` por `Id` de movimiento.
- **Decisión de diseño explícita**: el saldo se calcula sobre el ledger completo, no sobre la página/filtro que esté mirando el usuario en ese momento — igual que un resumen bancario, el saldo de un movimiento es su posición real en la cuenta, no depende de si el usuario filtró por Tipo o por rango de fecha. La paginación/filtro/orden de DataTables (ya existente, sin tocar) sigue resolviéndose a nivel SQL igual que antes; el saldo se pega después, en memoria, sobre las filas de la página ya traída, por `Id`.
- `MovimientoCCLocalListItemDto`/`MovimientoCCProveedorListItemDto` (`MariHogar.Application/DTOs/CCLocalDtos.cs`/`CCProveedorDtos.cs`) ganan `Saldo` (`decimal`).
- Columna "Saldo" agregada a `Views/CCLocal/Index.cshtml` (listado de movimientos de CC Local — el nombre real de la vista, no `Caja/Index.cshtml`, que es un módulo distinto de M15 sin tocar) y a `Views/Proveedores/CuentaCorriente.cshtml` (detalle de CC de un proveedor — el nombre real de la vista, no `Proveedores/Details.cshtml`, que no existe). Mismo criterio de color ya usado para "Saldo actual" en cada pantalla (CC Local: verde si ≥0/rojo si <0; CC Proveedor: rojo si >0 = deuda, verde si <0 = a favor del local, gris si =0).

#### CR-15 — OC: fecha de emisión de cheque por defecto hoy
- `Views/OrdenesCompra/Details.cshtml`, handler `change` de `.sel-metodo-oc`: al pasar el método a Cheque (valor 4), si la fila todavía no tiene `fechaEmisionCheque` cargada se precompleta con `moment().format('YYYY-MM-DD')`, y si no tiene `cuota` se precompleta en 30 — ambos editables después. Se dispara `autocalcularVencimientoCheque` (ya existente de CR-2) sobre la fila recién renderizada para que el vencimiento salga calculado solo, sin que el usuario tenga que tocar los 2 campos primero.
- Sin cambio en `Ventas/Create.cshtml` (cheques exclusivos de Compras, confirmado con el cliente).

#### CR-16 (código) — Mayúsculas en Proveedor y Producto going forward
- `ProveedorService.CreateAsync`/`UpdateAsync` y `ProductoService.CreateAsync`/`UpdateAsync` (`MariHogar.Infrastructure/Services/`) aplican `.Trim().ToUpperInvariant()` a `RazonSocial`/`Nombre` antes de persistir, en Crear y en Editar. Sin cambio de validación (los `[StringLength]` ya existentes siguen aplicando sobre el valor normalizado).

#### CR-18 — Movimiento de ajuste de apertura (saldo $0 post-import)
- Bloque nuevo "6) AJUSTE DE APERTURA (CR-18)" agregado al final de `tools/ImportarHistorico/Program.cs`, después de la sección de Gastos y antes del reporte final.
- `fechaCorte` única para todos los ajustes del bloque: el máximo entre la fecha más reciente de `MovimientosCCLocal` y de `MovimientosCCProveedor` ya importados (nunca una fecha operativa real, para que el ajuste se identifique como corte técnico).
- CC Local: si `Σ Ingreso − Σ Egreso != 0`, postea un `MovimientoCCLocal` de signo contrario por el monto exacto (`OrigenTipo="AjusteApertura"`, `OrigenId=0`, `Descripcion="Ajuste de apertura — saldo migrado a $0 para inicio de operación real"`).
- CC Proveedores: agrupa `MovimientosCCProveedor` por `ProveedorId`, y por cada uno con `Σ Cargo − Σ Pago != 0` postea el mismo tipo de movimiento de ajuste, acotado a ese proveedor.
- Nuevo contador `Reporte.AjustesAperturaCreados`, reflejado en el resumen final (`Console.WriteLine`) del script.
- **No se ejecutó el script** (ni contra `marihogar_dev` ni producción) — mismo criterio que el resto de los ajustes de este script, la corrida real sigue en pausa por decisión del cliente.

#### Refinamiento CR-13 — ClienteCUIT en factura histórica
- Sección Ventas de `tools/ImportarHistorico/Program.cs`: se lee `clienteCuit` = columna "CUIT / DNI" (col. 6) de la misma fila ya usada para `clienteNombre` (col. 5), y se asigna a `ComprobanteAfip.ClienteCUIT` (campo ya existente en la entidad desde Etapa 1, sin migración EF necesaria) al crear el comprobante histórico. No se ejecutó el script (mismo motivo que CR-18).

#### Evidencia de build
- `dotnet build MariHogar.slnx` → 0 errores, 9 warnings preexistentes (ninguno nuevo).
- `dotnet build tools/ImportarHistorico/ImportarHistorico.csproj` → 0 errores, mismos warnings preexistentes.
- Revisión de código propia de los 7 archivos tocados (2 Services de CC + 2 DTOs + 2 Services de normalización + 1 vista de OC + 1 script de importación) — sin smoke test funcional (regla de proceso vigente).

#### Migraciones EF
Ninguna — confirmado contra la Arquitectura v4 antes de tocar código: los 5 ítems son cambios de comportamiento (cálculo en memoria, normalización de texto, JS, script de importación), sin impacto de esquema. No se generó ninguna migración.

#### Riesgos y supuestos
- CR-14: el saldo acumulado ahora requiere traer el ledger completo a memoria en cada `GetData` del DataTable (además de la página ya paginada) — aceptado explícitamente en Arquitectura v4 por volumen bajo (decenas/cientos de movimientos por cuenta). Si el volumen creciera mucho (miles de movimientos por proveedor), este patrón dejaría de ser O(1) por request y habría que revisar (documentado, no es un problema hoy).
- CR-14: dos movimientos con `Fecha` idéntica exacta se desempatan por `Id` (orden de creación) en ambos servicios — mismo criterio, consistente.
- CR-15: cambio 100% de JS, sin impacto de capas de servidor — riesgo bajo.
- CR-18/CR-13 (refinamiento): cambios sobre un script todavía no ejecutado contra ningún ambiente real — sin riesgo de dato hasta que se corra, momento en el que corresponde repetir la verificación por query real (`SELECT SUM(...)` = 0 en CC Local y en cada CC Proveedor) antes de dar el import por bueno.

#### Pruebas mínimas requeridas para QA
1. `CCLocal/Index`: con al menos 2-3 movimientos de fechas distintas, verificar a mano (calculadora) que la columna "Saldo" de cada fila coincide con el acumulado real hasta esa fecha inclusive (Σ Ingreso − Σ Egreso desde el primero). Cambiar el filtro de Tipo o de fecha y confirmar que el Saldo de las filas que siguen visibles **no cambia** (sigue siendo la posición real, no un acumulado del subconjunto filtrado).
2. `Proveedores/CuentaCorriente/{id}` de un proveedor con varios movimientos (Cargo y Pago mezclados): mismo chequeo a mano de la columna "Saldo", y confirmar que coincide con el "Saldo adeudado" mostrado arriba en la última fila (movimiento más reciente).
3. `OrdenesCompra/Details` de una OC con saldo pendiente: agregar una fila de pago, cambiar el método a "Cheque" → Fecha de emisión se autocompleta con la fecha de hoy, Cuota queda en 30, Fecha de vencimiento se autocompleta a hoy+30 días. Cambiar la fecha de emisión a mano → el vencimiento se recalcula solo. Cambiar el método a otro y volver a Cheque → si ya había fecha de emisión cargada, no se pisa (sigue el valor que el usuario ya puso).
4. `Proveedores/Create` y `Productos/Create`: cargar "acme s.a." / "sillón nórdico" en minúsculas → al guardar y reabrir en Editar, el campo aparece en mayúsculas ("ACME S.A." / "SILLÓN NÓRDICO").
5. Confirmar por lectura de `tools/ImportarHistorico/Program.cs` (no hace falta correrlo) que el bloque de CR-18 y el campo `ClienteCUIT` están en el lugar esperado del script — la corrida real contra `marihogar_dev`/producción queda pendiente de decisión del cliente, fuera de este sprint.

#### Checklist de salida para merge
- [x] Build `MariHogar.slnx` limpio, 0 errores.
- [x] Build `tools/ImportarHistorico/ImportarHistorico.csproj` limpio, 0 errores.
- [x] Sin migración EF (confirmado contra Arquitectura v4 antes de codificar).
- [x] Revisión de código propia de los 7 archivos tocados.
- [x] `tools/ImportarHistorico/Program.cs` ajustado pero **no ejecutado**.
- [x] Producción no tocada en ningún momento.
- [ ] Verificación manual en navegador de los 4 puntos de UI (columna Saldo en CC Local y en Proveedores, autocompletado de cheque en OC, mayúsculas en Proveedor/Producto) — pendiente del usuario, ver "Pruebas mínimas" arriba.

---

## Sprint CR-86 (2026-10-02) — Comisión cobrada por período + impuesto al cheque (CR-85 absorbido)

**Alcance completo del CR aprobado**, con la etapa 4 (Presupuesto) **salteada por pedido explícito del cliente**. Análisis en `1-analista-funcional.md` ("Análisis CR-86"), diseño en `2-disenador-funcional.md` ("CR-86"), arquitectura en `3-arquitecto-mvc.md` ("CR-86 — mapa por capa"). Criterios CA-86.1 a CA-86.16.

### Escaneo de reutilización (instrucción 39 sección 3)
Paso 1, `docs/patrones/cat_resumen.txt`: **4 coincidencias duras**, las mismas que ya había fijado el diseño, y todas se usaron tal cual sin pasar al paso 2 ni al 3.
- **PAT-016** (delicias-naturales) — rango de fechas persistido en `Session` con key `Filtros:ConfiguracionCostosCobranza:Index`; "Limpiar filtros" borra la sesión, no sólo los controles.
- **PAT-008** — DataTables server-side con filtro por columna visible, en las dos grillas de la pantalla.
- **PAT-020** (marihogar, CR-64/CR-82) — el gasto del impuesto se **anula** (`Anulado=1` + contramovimiento), nunca se borra.
- **PAT-023** (delicias-naturales) — el backfill de fechas reasienta por **reversión + alta**, nunca `UPDATE` sobre una fila del ledger.
- **PAT-012** — previsualizar → confirmar en el backfill, clonado de `ConfiguracionCostosCobranza/Recalcular` (CR-83), que es el mismo patrón en el mismo proyecto.

**No se agregó ningún patrón nuevo al catálogo**: todo lo construido es específico de este dominio (alícuota del impuesto al cheque) o ya está representado por los cinco de arriba.

### Lo que se construyó, por capa

**Domain**
- `Entities/AlicuotaImpuestoCheque.cs` (nuevo) — `Porcentaje decimal(9,6)`, `VigenteDesde`, `VigenteHasta?`. No hereda `SoftDestroyable`, igual que `TasaCostoCobranza`: se cierra la vigencia, no se borra. **Su `VigenteDesde` ES la fecha de corte** (AC-86.4).
- `Entities/Gasto.cs` — `ChequeId?` nullable, índice **no único** (la unicidad real es "un gasto de impuesto *vigente* por cheque" y se verifica en el servicio: un cheque re-acreditado tiene legítimamente uno anulado y uno vigente).
- `Enums/CategoriaGasto.cs` — `ImpuestosBancarios = 8`, agregado puro al final. **No se reutilizó `ComisionesBancarias = 7`**: ahí están las cargas manuales, y mezclarlas con el automático es el doble conteo que el CR viene a evitar.

**Application**
- `Interfaces/ICostoCobranzaService.cs` — `ObtenerCostoPeriodoPorTasaAsync`, `ObtenerCostoPeriodoPorProcesadorAsync` y `ObtenerPagosSinTasaPeriodoAsync`.
- `Interfaces/IImpuestoChequeService.cs` + `DTOs/ImpuestoChequeDtos.cs` (nuevos).
- `Interfaces/IChequeService.cs` — `AcreditarAsync(int, DateTime fechaDebito, string? usuarioId)`, `PrevisualizarAcreditacionAsync`, `PrevisualizarBackfillFechasAsync`, `AplicarBackfillFechasAsync`.
- `Interfaces/IPagoOrdenCompraService.cs` — `ActualizarFechaPagoTransferenciaAsync` → **`ActualizarFechaPagoAsync`**.
- `Interfaces/IGastoService.cs` — `ObtenerGastosSolapadosAsync` (reporte de solo lectura).
- `DTOs/CostoCobranzaDtos.cs` — `CostoCobranzaPorTasaDto`, `CostoCobranzaPorProcesadorDto`, y en el listado de tasas `CobradoEnPeriodo` + `CantidadPagos`; el filtro gana `Desde`/`Hasta`.

**Infrastructure**
- `Services/CostoCobranzaService.cs` — **`MovimientosCostoDelPeriodo(desde, hasta)` privado, compartido por los tres métodos** (total, por tasa, por procesador) y `NetoPosteado` como único lugar donde se resuelve *Σ Egreso no-reversión − Σ Ingreso reversión*. Es RA-86.1 resuelto: la invariante `Σ por tasa == Σ por procesador == total` vale por construcción. El agrupamiento resuelve el pago **después** de materializar los movimientos (un `IN` de `int`, MH-001-safe) en vez de un `GroupJoin` sobre una clave nullable, y **conserva el grupo residuo** (`TasaId`/`Procesador` en null): descartarlo rompería la invariante.
- `Services/ImpuestoChequeService.cs` (nuevo) — único punto que resuelve la alícuota, calcula, postea, anula y corrige la fecha. `PostearAsync` no commitea (hace un `SaveChanges` intermedio para obtener el `Gasto.Id`, dentro de la transacción del caller, igual que `GastoService.CrearAsync`). Nunca lanza: sin alícuota vigente devuelve 0, y si el cheque ya tiene impuesto vigente tampoco postea.
- `Services/ChequeService.cs` — `AcreditarAsync` con fecha de usuario (validada no futura y no anterior a `FechaEmision`, server-side además del diálogo), los **cuatro asientos con la misma fecha** en la transacción que ya existía; `RevertirEstadoAsync` anula el impuesto; backfill de fechas.
- `Services/GastoService.cs` — `CrearAsync` pasa `gasto.Fecha` al movimiento de ledger (**defecto latente MH-038, corregido**) y propaga `ChequeId`; reporte de gastos solapados.
- `Services/PagoOrdenCompraService.cs` — `ActualizarFechaPagoAsync` sin el guard de Transferencia, con cascada al impuesto del cheque y a `FechaAcreditacion`.
- `Data/AppDbContext.cs`, `Data/SeedData.cs`, migración `20261002142249_AddImpuestoChequeCR86`.

**Web**
- `ConfiguracionCostosCobranzaController` — rango en el filtro persistido, acción `Resumen` (tarjetas + residuo + impuesto del período) y CRUD de la alícuota en la misma pantalla.
- `ChequesController` — `Acreditar(chequeId, fechaDebito)`, `PrevisualizarImpuesto`, y las tres acciones del backfill.
- `GastosController.Solapados` — reporte de solo lectura.
- Vistas: `ConfiguracionCostosCobranza/Index.cshtml` (rehecha), `AlicuotaForm.cshtml`, `Cheques/Index.cshtml` (diálogo con fecha + preview), `Cheques/BackfillFechas.cshtml`, `Gastos/Solapados.cshtml`, `Gastos/Index.cshtml` y `OrdenesCompra/Details.cshtml` (lápiz de fecha para todos los medios).

### Decisiones de implementación que no estaban escritas en la arquitectura

1. **La grilla de tasas quedó en 10 columnas, no en 11.** El diseño anticipaba medir `scrollWidth` vs `clientWidth` y, si no entraba, mandar "Vigente hasta" al detalle. En vez de eso, **"Vigente desde" y "Vigente hasta" se fusionaron en una sola celda "Vigencia"** con el dato secundario debajo del principal (`ov-celda-secundaria`, instrucción 38 sección 1). Se gana la columna sin esconder nada ni achicar la fuente, y la vigencia se lee de un renglón: "desde 01/09/2026 / vigente".
2. **El residuo de CA-86.5 no sale del ledger.** Un pago sin tasa tiene costo 0 y por eso **nunca posteó movimiento**: en el ledger no existe. El rótulo lo cuenta sobre `PagosVenta` por `COALESCE(FechaAcreditacionEfectiva, Fecha)` (730 sobre todo el historial), mientras el *grupo* residuo del agrupamiento — el que sostiene la invariante — sigue saliendo del ledger. Son dos cosas distintas con el mismo nombre y se implementaron por separado.
3. **El listado de tasas se ordena y pagina en memoria.** La columna nueva es un agregado del ledger: ordenar por ella en SQL exigiría bajar el agregado al mismo query y duplicar el WHERE, que es exactamente lo que RA-86.1 prohíbe. La tabla es configuración acotada (19 filas).
4. **MH-038 se cerró en los dos frentes, no en uno.** La nota de CR-84 advertía: "si se amplía el alcance de este método o del backfill, hay que decidir explícitamente — o se corrige también `FechaPagoTentativa`, o `FechaEfectivaSalida` deja de preferirla". Al abrir `ActualizarFechaPagoAsync` a todos los medios el caso **sí** dispara, así que se corrige también `FechaPagoTentativa`. Se eligió eso y no sacarle la preferencia a `FechaEfectivaSalida` porque esa preferencia es correcta: para un pago programado, la fecha de la confirmación ES la fecha real de salida. Lo que estaba mal era tener dos campos describiendo el mismo hecho y corregir sólo uno.
5. **El backfill se decide por saldo pendiente POR FECHA, no por "la fecha del movimiento".** Medido en producción: 5 de los 29 cheques tienen en la CC del proveedor un par Pago+Cargo ya reversado del 19/08/2026 **además** del asiento real. Mirando "la fecha del movimiento no-reversión" habría 39 filas y el conteo daría 32 de día / 8 de mes. Agrupando por fecha y quedándose con las que tienen **neto > 0**, ese par vale 0 y no es "una fecha vieja con plata": da exactamente **27 cheques de día y 3 de mes por $1.452.133,30**, los números del análisis. Es también lo que hace el backfill idempotente: después de correrlo las fechas viejas quedan en neto 0 y no vuelven a matchear.
6. **El backfill no toca la caja, y eso es correcto.** Los egresos de `PagoOC` en `MovimientosCCLocal` ya están fechados con `FechaAcreditacion` (los posteó CR-84, cuyo `FechaEfectivaSalida` prefiere la acreditación del cheque). El algoritmo lo descubre solo: no hay fechas stale del lado de la caja, así que no postea nada ahí. **Es lo que hace que CA-86.8 se cumpla**: los 2 pagos que hoy están en meses distintos (362 y 407, $918.799,97) se alinean moviendo el lado del proveedor.
7. **El gasto del impuesto usa `OrigenTipo="Gasto"`, no uno nuevo.** LP-002 al revés: no se agrega un `OrigenTipo` cuando el hecho económico es el mismo. Un impuesto es un gasto, y la columna Origen clickeable de CC Local, `CajaService` y `ProyeccionFinancieraService` lo resuelven sin tocar una línea. La forma de pago de la línea es `DebitoAutomatico`: lo que se paga no es el cheque, es lo que el banco descuenta solo.
8. **El reporte de saneamiento matchea las 4 subcategorías EXACTAS**, no por palabra clave. Un `LIKE '%comision%'` engancharía también "comision mp" (43 gastos, $4.480.222,00) y "comision naranja", que no están en el alcance aprobado. Verificado contra producción: las 4 dan **exactamente 80 gastos por $9.113.426,00**, ninguno anulado (CA-86.15), y `cheque` queda afuera por construcción (CA-86.16).

### Cosas medidas contra producción durante la implementación (solo lectura)
- Ledger por procesador, 2026-09: MP $768.568,20 (11) / Payway $517.869,27 (8) / Banco Directo $14.639,96 (4) / total $1.301.077,43. **Coincide exactamente con CA-86.1 y CA-86.2.**
- `PagoVenta` sin tasa: **730**. Coincide con CA-86.5.
- Cheques pendientes: 16, $6.920.424,74 → impuesto 0,600% = **$41.522,55**. Coincide con CA-86.14.
- Cheques acreditados: 29, $10.578.712,98 → $63.472,28, que **no** se generan (CA-86.13).
- Gastos solapados: 80 / $9.113.426,00. Coincide con CA-86.15.

### Observación declarada, NO actuada
Además de las 4 subcategorías del reporte, hay otras tres con la misma pinta de solaparse con lo que CR-83 automatizó: **"comision mp"** (43 gastos, $4.480.222,00), **"gastos y comisiones mp"** (4, $984.000,00, 3 ya anulados) y **"gastos payway pcia"** (12, $849.000,00, 9 ya anulados). No están en el alcance aprobado del reporte y no se incluyeron — incluirlas habría roto el número exacto de CA-86.15. Queda anotado para el próximo CR.

### Evidencia de build
`dotnet build` sobre la solución completa: **0 errores**. Un único warning preexistente (`HomeController.StatusCode` oculta el heredado, CS0114) que no pertenece a este CR. Sintaxis del JS embebido de las 4 vistas con script propio verificada con `node --check` sobre el bloque extraído. **No se corrió smoke test**: el cliente prueba a mano (regla del proyecto).


### Corrección post-QA (2026-10-02) — NO-GO del dictamen consolidado, 6 defectos + alcance nuevo

QA corrió en 3 lotes paralelos y devolvió **NO-GO**. Las dos afirmaciones del cierre anterior
quedaron **confirmadas parte por parte** por el lote 2 (los 5 cheques con par reversado son los
pagos **339/340/341/344/345**; el criterio del neto no esconde ningún caso real; "no toca la caja"
es cierto: de los 29, 24 tienen egreso y los 24 ya con `DATE(caja) = DATE(FechaAcreditacion)`, y
los 5 restantes no tienen egreso en absoluto, $2.224.700,00, exclusiones MH-036). El desvío de las
10 columnas también quedó aceptado: fusionar la vigencia *es* el patrón de la instrucción 38.

#### MH-044 (major, bloqueante, estaba EN VIVO sin correr ningún backfill)
`ActualizarFechaPagoAsync` buscaba el movimiento de proveedor a corregir con un
`FirstOrDefaultAsync` **sin `OrderBy`**, mientras el lado de la caja corregía *todas* las filas. En
el pago **339** las no-reversión son la **id 593** (19/08, ya compensada por la 601) y la **id 625**
(28/08, la viva): movía la muerta, dejaba la viva, y los dos ledgers del mismo hecho volvían a
quedar en meses distintos. **No se parcheó con un `OrderBy`**, que habría tapado el caso 339 sin
resolver el problema: lo que hay que mover es la fila **con saldo neto vivo**.

El criterio del neto por fecha —que el backfill ya usaba bien y los otros dos caminos no— se
extrajo a **`SaldoLedgerPorFecha`** (`Infrastructure/Services`), con dos métodos (`Proveedor`,
`Caja`), y ahora lo consumen los **tres** caminos: el backfill, `ActualizarFechaPagoAsync` y
`EgresoPagoProveedorService.ActualizarFechaEgresoAsync`. Que el criterio estuviera duplicado es
exactamente cómo nació MH-044.

Dos detalles del arreglo: se mueve el **grupo entero** de cada fecha viva y no sólo su fila
no-reversión (un grupo puede ser `Pago 100` + `Cargo reversión 40`; mover sólo el Pago dejaría el
crédito huérfano en el mes original), y del lado de la caja el cambio es **indistinguible del
anterior en el caso normal** —un solo egreso, sin reversiones—, así que no altera lo que QA validó
en MH-037.

#### MH-048 (major)
En `EgresoPagoProveedorService.ArmarBackfillAsync`, el guard `mov.Cantidad > 1` (MH-036) se
evaluaba **antes** del chequeo de `yaPosteado`. Se invirtió el orden: si el egreso ya está posteado,
no hay fecha que decidir y los guards de MH-036 no aplican. La pantalla de regularización de CR-84
vuelve a pedir revisión manual de **5 / $2.224.700,00** en vez de **28 / $10.278.712,98**.

#### MH-046 (medium, misma raíz que MH-044)
`ActualizarFechaImpuestoAsync` movía la fecha del impuesto **sin revalidar la vigencia de la
alícuota**. Ahora la revalida: si a la fecha nueva no hay ninguna vigente, el gasto se **anula**
(PAT-020) en vez de mudarse a un período donde el impuesto no existe —sin esto, corregir la fecha
de un cheque hacia atrás dejaba un gasto automático en agosto de 2026, encima de las cargas
manuales, y la fecha de corte dejaba de serlo. **El importe no se recalcula** aunque la alícuota del
período nuevo sea otra: el gasto posteado es un hecho del ledger, mismo criterio que CA-86.12.
La firma pasó a `Task<decimal>` para informar el monto anulado.

#### MH-045 (menor) — decisión: bloquear la anulación manual
Un gasto con `ChequeId` **no se puede anular desde Gastos**. Motivo: anulado a mano quedaba
irrecuperable —el cheque sigue `Acreditado`, y `PostearAsync` sólo corre al acreditar, así que el
sistema no lo vuelve a generar nunca; peor, la idempotencia de CA-86.11 pasaría a leer "no hay
vigente" y podría postear un segundo al re-acreditar. El camino correcto es el único punto que
gobierna los tres asientos (CRM-001): volver el cheque a Pendiente. Se bloquea en el Service
(`AnularAsync`) **y** se saca el botón del listado, que muestra `automático` en gris con el tooltip
que explica por dónde deshacerlo: un botón que el Service va a rechazar es peor que no tenerlo.

#### MH-047 (menor) — decisión: la categoría automática no se ofrece en el alta
`ImpuestosBancarios` sale de los combos de **alta de Gasto** y de **plantillas recurrentes**, y se
valida server-side (REG-004). Motivo: es la puerta de entrada exacta al doble conteo que todo el CR
cierra —alguien carga a mano el impuesto del extracto en la misma categoría donde el automatismo ya
lo posteó, y el único filtro que servía para auditar lo automático deja de servir. **Sigue estando
en los filtros de los listados**, deliberadamente: hay que poder verlos. La exclusión vive en
`CategoriasGastoSeleccionables` (Domain/Helpers) y no escrita en cada vista, para que una pantalla
nueva no la olvide. El alta automática entra por el mismo `CrearAsync` pero con `ChequeId`, que es
lo que la distingue.

#### MH-043 (medium)
El reporte cumplía CA-86.15 al peso pero no listaba el **único doble conteo confirmado en vivo**
(gasto **520**, "COMISION PERCEPCION MP", $50.000,00 del 14/09/2026, que es MH-039 y sigue abierto)
ni las 3 subcategorías vecinas, y el encabezado no declaraba que era un subconjunto. Ahora el
reporte tiene **dos bloques**: *Solapamiento confirmado* (las 4 subcategorías revisadas, **80
gastos / $9.113.426,00**, intacto para que CA-86.15 siga verificándose solo) y *Otros candidatos,
sin revisar uno por uno* (**60 gastos, $6.363.222,00, de los cuales $4.851.222,00 vigentes**:
"comision mp", "gastos y comisiones mp", "gastos payway pcia" y "COMISION PERCEPCION MP"). El aviso
de arriba dice explícitamente que el primer bloque es un subconjunto y que el caso ya confirmado
contra la caja está en el segundo.

#### Suposición falsa corregida en el XMLdoc (hallazgo del lote 3 + del orquestador)
El comentario de `CategoriaGasto.ImpuestosBancarios` afirmaba que las cargas manuales de comisiones
y gastos bancarios están en `ComisionesBancarias`. **Es falso y está medido:** están en
`Otro = 6` —**120 gastos, $11.479.487,00**— contra **1 gasto de $50.000,00** en
`ComisionesBancarias`. El cliente nunca usó la categoría que CR-62 creó para esto: carga en "Otro" y
distingue por subcategoría de texto libre. Queda escrito en el enum con el número. **Esto ratifica
agrupar el reporte por subcategoría**: era la única forma de ver el universo real. El filtro de
`PrevisualizarRecalculoAsync` que ve 1 de 121 gastos es **CR-87 y no se tocó**.


#### MH-050 (segunda vuelta de QA) — `IN` de SQL sobre colección local de strings, en código que yo mismo escribí

`GastoService.LeerPorSubcategoriaAsync` filtraba con
`.Where(g => subcategorias.Contains(g.Subcategoria))`, donde `subcategorias` es un `string[]`
local: **MH-001 exacto**, el patrón más reincidente del catálogo. No es un listado parcial, es un
**500 en todo el reporte** de `Gastos/Solapados`, y se dispara igual con la colección vacía: la
pantalla habría estado rota desde el día 1 con los datos perfectos detrás.

**De dónde salió, que es lo que importa para no repetirlo.** No estaba en la primera versión: ahí
el whitelist era un `static readonly string[]` usado directamente en el `Where`, y el defecto
apareció **al extraer el método compartido para MH-043**, cuando el array pasó a ser un parámetro.
El refactor era correcto en todo lo demás y compila igual. Es literalmente lo que MH-001 describe:
*"el más fácil de reintroducir porque el código parece correcto y compila"*. La lección operativa es
que **extraer un método que recibe la colección por parámetro es un gatillo de MH-001**, y hay que
revisarlo en la misma pasada del refactor, no después.

**Arreglo**, con el patrón que el proyecto ya usa en los otros tres lugares con colecciones de
string (`CCLocalService.ListarMovimientosAsync`, `StockService.ListarMovimientosAsync`,
`UsersController.GetData`): se materializan los gastos con subcategoría y se filtra en proceso
contra un `HashSet`. Costo irrelevante y acotado — `Gastos` tiene ~534 filas. **Sin
`if (count == 0) return`** delante, que es la otra forma de enmascararlo hasta que aparezca el
primer dato.

Dos detalles deliberados: la comparación es `OrdinalIgnoreCase` y no ordinal, porque reproduce la
collation case-insensitive de MySQL con la que se midieron los 80 gastos / $9.113.426,00 de
CA-86.15 (con comparación sensible, una variante de tipeo del cliente se caería del reporte sin
aviso); y el `OrderBy` por subcategoría usa el mismo comparador. El XML doc cita MH-001 y dice
explícitamente que no se vuelva a convertir en un `Contains` traducido a SQL, igual que hacen los
otros tres.

**Barrido completo de la familia en todo lo que tocó CR-86** (lo que QA no puede hacer abriendo
pantallas, porque en este proyecto no se levanta la app): los demás `Contains` traducidos a SQL van
sobre `int` (`pagoIds`, `ids`, `idsEnRango`) o sobre enums, que mapean a int y son seguros por el
alcance medido de MH-001; el resto son `string.Contains` sobre una **columna** (buscador de
DataTables, que es otra cosa) o LINQ sobre colecciones ya en memoria (`fechasVivas`, `buscadas`,
`CategoriasGastoSeleccionables.Todas`). **`GastoService` era el único caso**, y coincide con lo que
midió el orquestador.

---

### Alcance nuevo de la misma corrida — decisión del cliente sobre la alícuota

**`VigenteDesde` = 01/09/2026, fija**, más el pedido textual de que el impuesto se refleje "en los
movimientos de caja y cuenta". La lectura coherente de las dos cosas juntas es que **septiembre
también se postea**.

- **La siembra dejó de ser "día del arranque"**: es `new DateTime(2026, 9, 1)`. Con la fecha del
  arranque, deployar tarde o sembrar en otra instalación movía la fecha de corte en silencio, y
  septiembre quedaba afuera. Sigue siendo idempotente (no toca nada si ya hay alguna alícuota).
- **CA-86.13 reenunciado**: los que no generan impuesto son los acreditados **antes del 01/09** —
  **10** cheques, $3.958.765,39. La pantalla de regularización muestra ese número para que el
  recorte sea visible y no implícito; con **ninguna** alícuota cargada devuelve el total, no 0:
  "nada cubierto" no se informa como "todo cubierto".
- **CA-86.17, nuevo**: los **19** cheques ya acreditados con fecha ≥ 01/09 ($6.619.947,59) reciben
  su impuesto, **$39.719,67**. El total se suma de los importes **ya redondeados por cheque**: el
  0,6% de la suma daría $39.719,69. Verificado por tramo contra producción.
- **El backfill del impuesto va en la misma pantalla** (`Cheques/BackfillFechas`, renombrada a
  *Regularizar cheques acreditados*), en la misma pasada y la misma transacción, con el mismo
  PAT-012. Ahora la lista incluye también los cheques que **sólo** necesitan impuesto (badge
  "Sólo impuesto"), y hay columna de Impuesto con tres estados: monto, "ya registrado", "sin
  alícuota".

**Cómo se garantiza que el impuesto no quede con la fecha vieja** (la pregunta del orquestador): no
es una cuestión de orden entre los dos pasos, es que **la fecha vieja no es una entrada del
cálculo**. `PostearAsync` recibe `cheque.FechaAcreditacion`, que es la misma fecha a la que el
reasiento *lleva* los movimientos; la fecha vieja sólo existe dentro de las filas del ledger que el
reasiento mueve. El cheque es la autoridad de la fecha y los dos pasos leen de ahí, así que el
resultado es el mismo se ejecuten en el orden que sea. Está dicho así en el código y en la pantalla.

**Lo que no se hizo, por indicación explícita:** el impuesto **no** va a la cuenta corriente del
proveedor (es un cargo del banco, no deuda con el proveedor: postearlo ahí inflaría lo que se le
debe); no se tocó Caja, CC Local, Rentabilidad ni la proyección —el impuesto es un `Gasto` con su
egreso y las cuatro ya lo cuentan solas, revisado y sin encontrar ningún lugar que filtre por lista
explícita de categorías—; y **no se corrió ningún backfill contra producción**.


#### Tercera vuelta de QA — MH-051, MH-052, MH-053 y dos correcciones de comentario

Los tres lotes cerraron en GO / GO CONDICIONADO y el NO-GO quedó levantado. Lo que entró en esta
última pasada:

**MH-053 / CA-86.18 / RN-86.5 (dictamen del orquestador).** Un pago cuyo **neto en el ledger de
proveedores es 0** ya no se ofrece para corrección de fecha. Son sobrepagos y duplicados importados
del sistema anterior, reversados el 30/09 en la limpieza de datos (pagos **58, 201 y 203**,
$1.229.975,84; 5 grupos con neto total 0 en producción). El razonamiento es PAT-020: **lo que tiene
neto 0 en un ledger inmutable está cerrado** — el ledger ya dijo que ese movimiento no ocurrió, así
que no hay nada vivo que refechar y su fecha es historia, no un hecho corregible. Ofrecer la
corrección movía el débito dejando el crédito en otro mes (justo el invariante que el CR establece)
y le hacía creer al usuario que había corregido algo. Si el pago hay que rehacerlo, se postea un
hecho nuevo. **No es regresión**: el código viejo hacía lo mismo.

De paso **se reordenó `ActualizarFechaPagoAsync`**: ahora todas las validaciones corren **antes** de
tocar una sola propiedad. Antes el guard de `FechaEmision` devolvía el error con `pago.Fecha` ya
mutado en el change tracker — sin `SaveChanges` en ese camino, pero dejando la entidad sucia para
cualquier otro `SaveChanges` del mismo request.

**MH-051.** `ActualizarFechaImpuestoAsync` devolvía el monto anulado "para que el caller lo informe"
y el caller **descartaba el retorno**: la anulación del impuesto era silenciosa y el mensaje seguía
siendo "Fecha de pago actualizada correctamente". Misma clase que MH-039 — el sistema hace algo con
la plata del cliente y no se lo dice. Ahora el mensaje declara el monto anulado y por qué. Incluye
el **guard de `FechaEmision`** que faltaba: el mismo que ya tenía `AcreditarAsync`, porque tiene que
estar en los dos caminos que escriben el dato, no sólo en el primero.

**MH-052.** `GastoRecurrenteService.CreateAsync` y `UpdateAsync` validan server-side la exclusión de
MH-047. Estaban cubiertas las 4 vistas y uno de los dos CRUD: sin el guard la plantilla se guardaba
y el error aparecía recién al usarla.

**`PostearAsync` y su `SaveChanges`.** Observación cruzada del lote 2: hace un flush propio dentro de
la transacción del backfill, contra la convención de los servicios hermanos. **Decisión: se mantiene
el flush y se alinea el contrato, que ahora lo declara como excepción explícita con el motivo.**
Evalué partir el método en dos fases (agregar el Gasto, que el caller grabe, postear el movimiento
después) y lo descarté: un protocolo de dos llamadas permite que un caller olvide la segunda y deje
un Gasto **sin su egreso de caja**, que es exactamente MH-033 — peor que un flush que no afecta la
atomicidad. La alternativa de fondo sería una FK del ledger al Gasto, imposible hoy porque `OrigenId`
es una clave polimórfica: es cambio de modelo con migración, fuera de alcance. Queda declarado para
que el orquestador pueda revocarlo.

**Dos comentarios que decían lo que el código no hace, corregidos:**
1. El doc-comment de `ArmarBackfillFechasAsync` decía *"porque el orden importa"* y remitía a la nota
   que argumenta que el orden es **irrelevante**. Quedó una sola versión, la correcta, con el
   argumento fuerte que aportó QA: `FechaAcreditacion` se escribe en 3 lugares y ninguno es el
   backfill, **y** los dos pasos escriben universos de ledger disjuntos (`OrigenTipo="Gasto"` contra
   `"PagoOC"`), así que el `SaveChanges` intermedio tampoco contamina.
2. La justificación del "grupo entero" en `ActualizarFechaEgresoAsync` describía un caso con **0
   ocurrencias**. Ahora dice lo medido: no hay ningún pago con filas de reversión ni con más de un
   egreso no-reversión, así que el conjunto nuevo es idéntico al viejo en el **100%** de los pagos —
   la rama que el arreglo repara **no tiene hoy un solo caso real que la ejercite**. Se hace igual
   porque es forward-correcta para el estado que crea el propio backfill, y porque tener los dos
   ledgers decidiendo con criterios distintos es como nació MH-044. Ídem MH-048: es **preventivo**,
   hoy no cambia nada observable (0 pagos con neto de caja > 0 y ledger sucio).

**MH-050: el XMLdoc estaba mal y se corrigió.** Yo había escrito que el defecto "no estaba antes de
la extracción del método", lo que se contradice con la otra mitad de la misma frase ("EF trataba
igual al `static readonly`"). Verificado en git: `0e80ff5:GastoService.cs` línea 246 ya tenía
`SubcategoriasSolapadas.Contains(g.Subcategoria)`. **El defecto nació con el reporte, no con el
refactor**, y el arreglo repara también la versión que QA calificó en la primera corrida. El gatillo
real es *cualquier* colección local de strings hacia un `Where` que va a SQL — parámetro, variable
local o `static readonly`. La memoria del agente quedó corregida en ese sentido (estaba anotada como
"cuidado con los refactors", que hace mirar el lugar equivocado).

**`Agrupar` alineado al mismo comparador.** `GroupBy` usaba el comparador por defecto mientras el
filtro y el `OrderBy` usan `OrdinalIgnoreCase`: una variante de caja entraba por el filtro y se
partía en **dos grupos de acordeón** para un solo concepto (los totales no se movían). Preventivo:
lote 1 midió 8 valores distintos byte a byte, idénticos a los 8 literales del whitelist, y 0
subcategorías con espacios de borde — por eso `Ordinal`, `OrdinalIgnoreCase` y la collation
seleccionan las mismas 140 filas, y los números aguantaron la tercera medición (**80 /
$9.113.426,00** y **60 / $6.363.222,00**).

**Fuera de alcance, anotado:** los pagos 58, 201 y 203 siguen con `Estado = Pagado` aunque su neto
sea 0 (candidato a CR-87, junto con el filtro de `PrevisualizarRecalculoAsync`).


---

### Cambio de alcance (2026-10-02, decisión del cliente) — el reasiento de fechas sale, el impuesto queda

**Textual:** *"dejar los datos de los cheques en producción como están, están cargados por el
usuario"*. El **punto 9 del alcance (backfill de fechas de los 29 cheques acreditados) queda
FUERA**, y con él el aviso de los 3 cheques que cruzaban de mes. **CA-86.17 sigue en pie tal cual:**
el impuesto de los 19 cheques de septiembre sí se registra, $39.719,67. Es lo que el cliente pidió
al fijar la vigencia en 01/09.

#### El único trabajo real: desacoplar los dos pasos

Estaban **acoplados**, y QA lote 3 encontró por qué importaba: el `PostearAsync` del impuesto vivía
dentro del recorrido del reasiento, y el `continue` de los cheques con ledger ambiguo estaba
**antes** del posteo. O sea: un cheque que el reasiento salteaba tampoco recibía impuesto. Daba el
número correcto porque ninguno de los 19 caía en ese caso — **por el estado de los datos, no por
construcción**. Con el reasiento fuera, dejarlo colgado de ese recorrido podía dejar el impuesto en
0 sin que nada avisara.

Ahora el recorrido del impuesto es **propio**: itera los cheques acreditados por su cuenta y la
única condición que aplica es la del propio impuesto (tener alícuota vigente a su fecha y no tener
ya un gasto vigente). Y esas dos condiciones **no se duplican** en el bucle: las resuelve
`PostearAsync`, que ya no postea ni lanza en ninguno de los dos casos. Duplicarlas ahí es como nació
MH-044.

- `IChequeService`: `PrevisualizarBackfillFechasAsync` / `AplicarBackfillFechasAsync` →
  **`PrevisualizarRegularizacionImpuestoAsync` / `AplicarRegularizacionImpuestoAsync`**.
- DTOs `BackfillFechaCheque*` → **`RegularizacionImpuestoCheque*`**.
- `ChequesController`: `BackfillFechas` → **`RegularizarImpuesto`**, con sus dos acciones AJAX.
- Vista `Cheques/BackfillFechas.cshtml` **eliminada**; nueva `Cheques/RegularizarImpuesto.cshtml`.
  No quedó un botón inaccesible ni código muerto: el reasiento se retiró, no se escondió.
- El link del encabezado de Cheques pasa a *"Registrar impuesto pendiente"*.

**`SaldoLedgerPorFecha` se queda intacto.** Nació con tres consumidores y el reasiento era uno; los
otros dos siguen vivos (`ActualizarFechaPagoAsync` y `ActualizarFechaEgresoAsync`) y es además el
criterio con el que esa corrección se **niega** cuando el neto es 0 (MH-053 / RN-86.5). Su doc
comment ahora dice dos consumidores y explica que el tercero se retiró, para que nadie lo lea como
un helper sobredimensionado.

**`AcreditarAsync` no cambió**: de acá en adelante sigue pidiendo la fecha del extracto y asentando
los dos ledgers con ella. Eso es lo que queda de CR-85 y está bien.

#### El estado conocido, escrito en el código y no sólo acá

Los cheques históricos **siguen asentados por vencimiento** en la cuenta corriente del proveedor, y
los 3 que cruzan de mes ($1.452.133,30, pagos 362, 407 y 339) **siguen mal fechados ahí, por
decisión de negocio**. No es un defecto a redescubrir. Quedó un bloque de documentación en
`ChequeService.AcreditarAsync` —el primer lugar donde alguien va a mirar— que dice qué pasa, por qué,
con qué fecha se decidió y dónde está el detalle. Sin esa nota, el próximo que mida el desfasaje lo
levanta como bug y se vuelve a discutir una decisión ya tomada.

#### Verificación de la previsualización contra producción (solo lectura)
19 cheques / **$39.719,67** a registrar y 10 sin alícuota, consultado por tramo de
`FechaAcreditacion` contra la base. El redondeo por cheque da $39.719,67 y el 0,6% del total daría
$39.719,69: los $0,02 son la prueba de que el criterio es el correcto. Ningún gasto de impuesto
posteado todavía (la columna `ChequeId` no existe aún en producción: la migración no está aplicada).


#### Cierre — la invariante de la alícuota pasa de afirmada a garantizada

`CrearAlicuotaAsync` validaba el solape y llevaba el comentario *"nunca dos alícuotas vigentes a la
misma fecha: si las hubiera, la alícuota vigente dejaría de estar definida y el impuesto dependería
del orden de lectura"*. Pero **`ActualizarAlicuotaAsync` pisaba `VigenteDesde` y `VigenteHasta` sin
validar nada**: editando una alícuota se podía crear exactamente el estado que ese comentario dice
que no puede existir. No era cosmético — es una invariante de la que depende el importe del
impuesto.

Ahora `Actualizar` llama a `ObtenerVigenteQueSolapaAsync` (que ya excluía la fila en edición por
`a.Id != input.Id`, así que no se detecta a sí misma) y **rechaza**. La asimetría con `Crear` —que
*propone* cerrar la anterior— es deliberada y es la que ya resuelve `TasaCostoCobranzaService`: al
dar de alta, cerrar la vigencia anterior es el flujo normal; al editar, el usuario está moviendo
fechas de una fila existente y cerrarle otra por su cuenta sería un efecto que no pidió.

**Aceptados y declarados, no arreglados** (criterio del orquestador):
- **MH-054** (low, preexistente): `AplicarImpuestoPendiente()` no recibe el snapshot de lo
  previsualizado, así que son dos lecturas del estado vivo. `RegularizacionCaja.Aplicar()` de CR-84
  tiene la misma firma: arreglarlo acá solo crearía asimetría entre dos pantallas hermanas.
- El `if (impuesto <= 0m) return 0m;` de `PostearAsync` no tiene rama espejo en la previsualización.
  Divergiría la **cantidad** y nunca el importe, y es **inalcanzable**: haría falta un cheque de
  menos de $0,84 y el mínimo acreditado en producción es $25.425,11. Quedó declarado en el código en
  vez de agregar la rama.

### Evidencia de build de la corrección
`dotnet build` sobre la solución completa: **0 errores** (mismo warning preexistente CS0114 de
`HomeController`). JS embebido de las 5 vistas con script propio verificado con `node --check`.
Sin smoke test.

### Criterios reenunciados por el orquestador, para la próxima verificación
CA-86.5 → **723** (no 730: el filtro global de EF saca 6 soft-deleted y 1 de venta cancelada; la
implementación ya contaba bien). CA-86.8 → **3 cheques / $1.452.133,30** (pagos 362, 407 y 339).
CA-86.11 → el invariante es "a lo sumo un gasto **vigente** por cheque". CA-86.14 → **$41.522,56**
(redondeo por cheque, como el banco).

## Historial de ajustes

### Bloques archivados (2026-10-02)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 2 bloques (2026-09-30 a 2026-09-30) → [`5-implementador-2026-09.md`](historial/5-implementador-2026-09.md)
- **2026-07** — 2 bloques (2026-07-29 a 2026-07-30) → [`5-implementador-2026-07-2.md`](historial/5-implementador-2026-07-2.md)


### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-07** — 1 bloques (2026-07-30 a 2026-07-30) → [`5-implementador-2026-07.md`](historial/5-implementador-2026-07.md)
- **historico** — 7 bloques → [`5-implementador-historico.md`](historial/5-implementador-historico.md)
