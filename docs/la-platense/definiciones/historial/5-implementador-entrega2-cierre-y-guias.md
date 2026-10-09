# Historial archivado - Implementador / La Platense
## Cierre de la Entrega 2 (ola 1 y ola 2) y sus guias de pruebas manuales

Movidas desde `5-implementador.md` el 2026-10-06 (LP-040) para mantener el archivo vigente bajo
el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Son los pasos manuales que se
escribieron para que el cliente/QA ejecutara la Entrega 2 en agosto de 2026; el codigo que
describen ya esta deployado. Se leen solo si hace falta ese detalle.

### Guía de pruebas manuales (Entrega 2, ola 1 — a ejecutar por el cliente/QA, no por el Implementador)

1. Aplicar la migración `EntregaDos_VentasCCClientesAfip` contra la base de desarrollo (`dotnet ef database update`).
2. Alta de Cliente (Responsable Inscripto y Consumidor Final) — verificar que el CUIT/DNI duplicado se rechaza.
3. Venta rápida: crear una venta nueva, agregar 2-3 ítems (por búsqueda y por código de barras), guardar borrador, volver a editar (cambiar cantidad/precio/IVA) y verificar que los totales se recalculan.
4. Pago mixto: efectivo + tarjeta en 3 cuotas — verificar que el recargo se muestra y se suma al total antes de confirmar.
5. Venta con pago a cuenta corriente (requiere Cliente asignado, no Consumidor Final) — confirmar y verificar que aparece el movimiento en `Clientes/CuentaCorriente/{id}` con el saldo actualizado.
6. Intentar confirmar una venta sin ítems, y una venta con pagos insuficientes (sin cuenta corriente) — verificar que ambas quedan bloqueadas con el mensaje de error esperado.
7. Confirmar y facturar una venta sin certificado AFIP configurado — verificar que devuelve el error explícito de "AFIP no está configurado" y la venta queda en Borrador (no se descontó stock).
8. Verificar que el stock del producto efectivamente se descontó tras una facturación exitosa (una vez que haya certificado AFIP de homologación configurado).
9. Cancelar un borrador y verificar que desaparece del listado de Ventas.
10. Verificar permisos: un usuario con rol Vendedor puede crear/editar/facturar ventas y clientes; un usuario sin ninguno de los 3 roles (`SuperUsuario`/`Administrador`/`Vendedor`) recibe 403 en `/Ventas` y `/Clientes`.

### Guía de pruebas manuales — Entrega 2 completa (ola 1 + ola 2, a ejecutar por el cliente/QA, no por el Implementador)

**Antes de empezar:**
1. Aplicar la migración `EntregaDos_VentasCCClientesAfip` y luego `EntregaDos_CajaGastosEntregasDashboard` contra la base de desarrollo (`dotnet ef database update`).
2. Asignar el rol `Repartidor` a al menos un usuario de prueba (además de `Vendedor`/`Administrador`) para poder probar Entregas.

**Ventas / CC Clientes / AFIP (ola 1):**
3. Alta de Cliente (Responsable Inscripto y Consumidor Final) — verificar que el CUIT/DNI duplicado se rechaza.
4. Venta rápida: crear una venta, agregar 2-3 ítems (por búsqueda y por código de barras), guardar borrador, volver a editar (cambiar cantidad/precio/IVA) y verificar que los totales se recalculan.
5. Pago mixto: efectivo + tarjeta en 3 cuotas — verificar que el recargo se muestra y se suma al total antes de confirmar.
6. Venta con pago a cuenta corriente (requiere Cliente asignado) — confirmar y verificar el movimiento en `Clientes/CuentaCorriente/{id}`.
7. Confirmar una venta sin certificado AFIP configurado — debe devolver el error explícito y la venta queda en Borrador (no se descontó stock, no se generó movimiento de Caja).
8. Cancelar un borrador y verificar que desaparece del listado de Ventas.
9. Verificar permisos: Vendedor puede operar Ventas/Clientes; un usuario sin esos roles recibe 403.

**Caja (ola 2, nuevo):**
10. Facturar una venta con certificado AFIP configurado (homologación) y verificar que aparece un `CajaMovimiento` de Ingreso en `Caja/Index` por cada medio de pago usado (excepto si hubo una línea a cuenta corriente, que NO debe generar movimiento de Caja).
11. Registrar un Gasto y verificar que aparece automáticamente como Egreso en `Caja/Index`.
12. Registrar un movimiento manual (`Caja/MovimientoManual`) — verificar que aparece en el listado con origen "Ajuste".
13. Cerrar la caja de hoy (`Caja/Index` → "Cerrar caja de hoy") y verificar: (a) los totales del cierre coinciden con la suma de movimientos del día; (b) intentar facturar otra venta o registrar otro gasto con fecha de hoy debe fallar con el mensaje de "caja cerrada"; (c) el cierre aparece en `Caja/Cierres`.
14. Ir a `Caja/Mensual`, verificar el resumen del mes actual y cerrar el mes — verificar que aparece en el histórico de cierres mensuales de esa misma pantalla.

**Gastos (ola 2, nuevo):**
15. Registrar un gasto clasificado como "Caja chica" y otro como "Caja mensual" — verificar que la clasificación es excluyente (R7) y que ambos generan su Egreso en Caja.
16. Anular un gasto vigente — verificar que aparece con badge "Anulado" (sigue visible, no desaparece del listado) y que se genera un contramovimiento de Ingreso en Caja fechado hoy.
17. Intentar anular un gasto ya anulado — debe rechazarse con mensaje explícito.

**Entregas (ola 2, nuevo — primera pantalla real de Repartidor):**
18. Desde una Venta ya Facturada (`Ventas/Details`), hacer clic en "Programar entrega" — completar tipo (Propia/Tercerizada), costo base, repartidor y dirección. Verificar que el costo final se calcula con el markup vigente.
19. Intentar programar una segunda entrega para la misma venta — debe rechazarse ("ya tiene una entrega asociada").
20. Con un usuario del rol Repartidor, entrar a `Entregas/Index` y verificar que ve el listado COMPLETO (no solo las asignadas a él) — R9.
21. Recorrer el ciclo de estados desde `Entregas/Details`: Iniciar recorrido → Marcar entregada (o "No entregada" con motivo obligatorio → Reagendar con fecha futura).
22. Verificar permisos: un Repartidor puede ver/gestionar el estado de entregas pero NO puede acceder a `Entregas/Create` (debe dar 403).

**Dashboard (ola 2, nuevo — Corte 1):**
23. Entrar a `Dashboard/Index` con cualquier usuario autenticado y verificar: ventas de hoy (cantidad+total), caja de hoy (ingresos/egresos/saldo + si está cerrada), entregas pendientes — todo con datos reales de las pruebas anteriores.
24. Verificar la card "Próximamente: salud financiera" (nivel 2) — debe mostrarse claramente diferenciada como no disponible todavía, sin datos ni errores.
25. Verificar gastos del mes por categoría (gráfico), top 5 productos del mes y stock crítico — cada bloque debe navegar al detalle correspondiente (Gastos/Ventas o Productos/Stock) al hacer clic.


### Cierre de Entrega 2 — ola 1: Ventas, CC Clientes, AFIP (2026-08-11)

Repo: `C:\Sistemas\Ferreteria La Platense`, rama `entrega-2` (checkout activo, no se cambió de rama). Esta es la primera mitad de la Entrega 2 — motor de ventas (Cliente/CC cliente/Venta/AFIP). La segunda mitad (Caja/Gastos/Entregas/Dashboard Corte 1) queda para una tarea siguiente, dependiente de esta.

**Corrección aplicada sobre `3-arquitecto-mvc.md` (verificada antes de codificar, confirmada por el orquestador):** "Ventas + CC clientes" NO reusa `marihogar` para el ledger de cuenta corriente — la `Venta` de marihogar no tiene entidad `Cliente` (es texto libre) ni ledger de saldo. Se reutilizó la **forma** de `Venta`/`VentaItem`/`PagoVenta`/`VentaService`/`VentasController` de `marihogar` (adaptada: máquina de estados nueva Borrador/Facturada/Anulada en vez de Pendiente/PagadaParcial/Pagada/Cancelada, porque acá la venta nace editable en vez de crearse completa en una transacción). El ledger de cuenta corriente se adaptó del patrón `MovimientoCCProveedor`/`Proveedor` de `vino-y-se-fue` (`ClienteId` en vez de `ProveedorId` singleton) — **confirmado por lectura directa de `Proveedor.cs` que no persiste una columna de saldo**, por lo que `Cliente` tampoco la persiste (contradice literalmente a `3-arquitecto-mvc.md`, que sí la lista — se documenta como imprecisión de ese documento, no se sigue literal). La integración AFIP (`AfipService`/`IAfipService`/`AfipSettings`/`AfipTokenCache`, WSAA+WSFEv1 armado a mano con `System.Xml.Linq` + firma CMS con `System.Security.Cryptography.Pkcs`) se portó tal cual desde `marihogar`, sin cambios al mecanismo, solo adaptando namespaces y el mapeo DocTipo/DocNro hacia el modelo de `Cliente` de este proyecto.

**Domain** (`FerreteriaLaPlatense.Domain`):
- `Enums/EstadoVenta.cs` (Borrador/Facturada/Anulada — enum nuevo, no reutiliza el `EstadoVenta` de marihogar), `Enums/MedioPago.cs` (Efectivo/Debito/CreditoCuotas/CuentaCorriente), `Enums/CondicionIVA.cs` (ResponsableInscripto/Monotributo/ConsumidorFinal/Exento), `Enums/TipoMovimientoCC.cs` (Debito/Credito, adaptado de vino-y-se-fue), `Enums/OrigenMovimientoCC.cs` (VentaFiado/Pago/Ajuste), `Enums/TipoComprobanteAfip.cs` (FacturaA=1/FacturaB=6, coincide con el código AFIP "CbteTipo").
- `Entities/Cliente.cs` — Nombre, CuitDni (nullable, único), CondicionIVA, Telefono. **Sin columna de saldo** (ver corrección arriba).
- `Entities/MovimientoCCCliente.cs` — ClienteId, Fecha, Tipo, Origen, Importe, Referencia, VentaId (nullable, trazabilidad), UsuarioId (patrón explícito igual a `AjusteStock.UsuarioId` de Entrega 1, sin navegación a Identity).
- `Entities/Venta.cs` — Fecha, ClienteId (nullable = Consumidor Final), Estado, Subtotal, TotalIVA, Total, TipoComprobanteAfip (nullable), CAE, VencimientoCAE, NumeroComprobante, VendedorId, colecciones Items/Pagos.
- `Entities/ItemVenta.cs` — Cantidad **decimal** (no `int` como en marihogar, porque el catálogo de este proyecto admite `UnidadVenta` fraccionable — Peso/Metro), UnidadVenta copiada del Producto al momento de la venta (snapshot, no se recalcula si el producto cambia después), PrecioUnitario, PorcentajeIVA, Descuento, Recargo (montos monetarios, no porcentajes — asunción documentada, ver riesgos), Subtotal.
- `Entities/PagoVenta.cs` — MedioPago, Monto (importe base financiado), Cuotas/PorcentajeRecargoAplicado (solo si CreditoCuotas, validado en el Service).

**Application** (`FerreteriaLaPlatense.Application`):
- `DTOs/ClienteDtos.cs`, `DTOs/MovimientoCCClienteDtos.cs`, `DTOs/VentaDtos.cs` (VentaListItemDto/VentaDetalleDto con `TotalPagos`/`SaldoPendiente` calculados/ItemVentaDto/PagoVentaDto + DTOs de entrada `ItemVentaInputDto`/`PagoVentaInputDto`/`GuardarVentaBorradorDto`), `DTOs/AfipDtos.cs` (portado de marihogar).
- `Settings/AfipSettings.cs` (portado de marihogar), `Settings/RecargoCuotasSettings.cs` (nuevo — dictionary cuotas→% configurable en `appsettings.json`, sin pantalla dedicada, ver riesgos).
- `Interfaces/IClienteService.cs`, `ICuentaCorrienteClienteService.cs`, `IRecargoCuotasService.cs`, `IVentaWorkflowService.cs`, `IAfipService.cs` (portado de marihogar) — todos los contratos ya definidos en `2-disenador-funcional.md`.
- `Interfaces/IProductoService.cs` (Entrega 1, **modificado mínimamente**) — agregado `BuscarParaVentaAsync(string?)` para que la pantalla de Venta reutilice el mismo servicio de Catálogo en vez de duplicar el query.

**Infrastructure** (`FerreteriaLaPlatense.Infrastructure`):
- `Data/AppDbContext.cs` — agregados `DbSet<Cliente/MovimientoCCCliente/Venta/ItemVenta/PagoVenta>` + Fluent API (índice único en `Cliente.CuitDni` permitiendo múltiples NULL igual que `Producto.CodigoBarras`; `OnDelete(Restrict)` en FKs a Cliente/Producto; `OnDelete(Cascade)` en ItemVenta/PagoVenta → Venta; decimales con precisión `18,2`/`5,2`/`18,3` según el campo).
- `Services/ClienteService.cs` — CRUD + `ListarAsync` (DataTable con Saldo calculado por subconsulta) + `BuscarAsync` (Select2).
- `Services/CuentaCorrienteClienteService.cs` — `ObtenerSaldoAsync` (suma Debito-Credito, sin persistir), `ListarMovimientosAsync` (DataTable con filtro de fecha/tipo/origen), `RegistrarMovimientoAsync` (sin SaveChanges propio — lo controla `VentaWorkflowService` como parte de la transacción de confirmación).
- `Services/RecargoCuotasService.cs` — resuelve % desde `RecargoCuotasSettings`, nunca confía en un porcentaje enviado por el cliente.
- `Services/VentaWorkflowService.cs` — el más grande y de mayor riesgo: `GuardarBorradorAsync` (upsert completo de Items/Pagos con soft-delete de los quitados, nunca `Remove` físico), `CancelarBorradorAsync`, `ConfirmarYFacturarAsync` (valida guardas → llama AFIP **primero** → solo si `Exito=true` descuenta stock + genera `MovimientoCCCliente` + persiste CAE + pasa a Facturada, todo en una única `SaveChangesAsync`; si AFIP falla no se toca nada, la venta queda en Borrador reintentable).
- `Services/AfipService.cs` + `Services/AfipTokenCache.cs` — portados tal cual de marihogar (mismo WSAA/WSFEv1 armado a mano), adaptados a namespaces y a `MapearCondicionIvaReceptor`/`DeterminarDocumentoReceptor` de este proyecto.
- `Services/ProductoService.cs` (Entrega 1, modificado mínimamente) — agregado `BuscarParaVentaAsync`.
- `DependencyInjection.cs` — registrados `IClienteService`, `ICuentaCorrienteClienteService`, `IRecargoCuotasService`, `IVentaWorkflowService` (Scoped), `IAfipService` (Scoped) + `AfipTokenCache` (Singleton, cachea el token WSAA entre requests) + `IOptions<AfipSettings>`/`IOptions<RecargoCuotasSettings>` + `HttpClient` nombrado `"Afip"`.

**Web** (`FerreteriaLaPlatense.Web`):
- `Models/ClienteFormViewModel.cs`, `Models/VentaViewModels.cs` (`VentaEditableViewModel`/`ItemVentaViewModel`/`PagoViewModel`, tal como los definió `2-disenador-funcional.md`).
- `Controllers/ClientesController.cs` — CRUD + `Listar` (DataTable con filtro Nombre/CondicionIVA/Saldo) + `Buscar` (Select2) + `CuentaCorriente`/`CuentaCorrienteListar` (saldo calculado + historial con filtro de fecha via daterangepicker). Policy `RequireVentas` (Vendedor tiene escritura completa acá, a diferencia de Catálogo).
- `Controllers/VentasController.cs` — `Index`/`Listar` (DataTable con filtro fecha/cliente/estado/total), `Nueva`/`Editar` (pantalla de carrito editable), `GuardarBorrador`, `Cancelar`, `ConfirmarYFacturar`, `Details` (solo lectura, Facturada/Anulada), `BuscarProductos`/`BuscarPorCodigoBarras` (reutiliza `ICodigoBarrasLookupService` de Entrega 1 sin cambios, R11/PF15).
- `Program.cs` — nueva policy `RequireVentas` (`SuperUsuario`+`Administrador`+`Vendedor`, escritura completa en Ventas/Clientes).
- `appsettings.json` — secciones `Afip` (placeholder vacío: `CertificadoPath`/`CUIT` en blanco) y `RecargoCuotas` (seed `{3: 10%, 6: 20%}`, ejemplo editable).
- `Views/Clientes/*` (Index con DataTable+filtros, Create, Edit, CuentaCorriente con saldo destacado + daterangepicker), `Views/Ventas/*` (Index con DataTable+filtros incl. Select2 de cliente, `Editar.cshtml` — carrito dinámico con Select2 de producto + input de escaneo de código de barras + filas de Items/Pagos agregadas/quitadas por JS con reindexado, `Details.cshtml` solo lectura) — SweetAlert2 en confirmaciones de Cancelar/Confirmar y facturar.
- `Views/Shared/_Layout.cshtml` — nueva sección de sidebar "Ventas" (Ventas/Clientes), visible a SuperUsuario/Administrador/Vendedor.

**Migración EF:** `EntregaDos_VentasCCClientesAfip` (20260811132055) — tablas `Clientes`, `Ventas`, `ItemsVenta`, `MovimientosCCCliente`, `PagosVenta`. **No aplicada a ninguna base** (igual que en Entrega 1).

**Build:** `dotnet build FerreteriaLaPlatense.slnx` → 0 errores, mismas advertencias preexistentes (NU1902 MailKit/MimeKit, CS0114 HomeController).

### Cierre de Entrega 2 — ola 2: Caja, Gastos, Entregas, Dashboard Corte 1 (2026-08-11)

Repo: `C:\Sistemas\Ferreteria La Platense`, rama `entrega-2` (checkout activo, no se cambió de rama). Esta es la segunda mitad de la Entrega 2 — depende de `Venta`/`ItemVenta`/`PagoVenta`/`IVentaWorkflowService` ya construidos en la ola 1. **Con este cierre, la Entrega 2 completa (61h) queda funcionalmente terminada** — ver marca de cierre al final de esta sección.

**Escaneo de reutilización (antes de codificar):** se revisó `docs/*/definiciones/5-implementador.md` (ningún proyecto documenta el concepto de "cierre de caja" como bloqueo de período — confirma que es desarrollo nuevo, ya anticipado por `3-arquitecto-mvc.md`) y se leyó código real en `C:\Sistemas\marihogar` (`MovimientoCCLocal`, `Gasto`/`CategoriaGasto`/`FormaPagoGasto`, `Entrega`/`EntregaIntento`/`EstadoEntrega`, `DashboardService`/`DashboardController`) y `C:\Sistemas\ganaderia - emo` (`CajaService`/`CajaController`, revisado como referencia secundaria — tampoco modela un "cierre", confirma el mismo hallazgo). Decisión: reutilizar la **forma** de `MovimientoCCLocal` (adaptado como `CajaMovimiento`, con la diferencia explícita de heredar `SoftDestroyable` por convención del estudio, a diferencia del original inmutable de marihogar), reutilizar `Gasto` de marihogar casi directo (agregando `TipoImpactoGasto` para R7, ausente en el original), reutilizar la forma de `Entrega`/`EstadoEntrega` simplificada (sin `EntregaIntento` ni cobro-en-destino vía `PagoVenta`, que no forman parte del alcance de La Platense — no hay pedido funcional de cobro en destino en `1-analista-funcional.md`/`2-disenador-funcional.md`), y reutilizar la forma de `DashboardService`/`DashboardController` resuelta en un único método `ObtenerAsync()` en vez de un endpoint AJAX por KPI (volumen de datos de esta entrega no lo justifica todavía). El cierre diario/mensual (`CierreCajaDiario`/`CierreCajaMensual` + guarda de "no movimiento retroactivo a un día cerrado") es 100% desarrollo nuevo, sin precedente exacto en ningún proyecto del historial.

**Domain** (`FerreteriaLaPlatense.Domain`):
- `Enums/TipoMovimientoCaja.cs` (Ingreso/Egreso — nombre propio para no confundir con `TipoMovimientoCC` del ledger de CC cliente), `Enums/CategoriaGasto.cs` (Alquiler/Servicios/Sueldos/Impuestos/Flete/Otro), `Enums/FormaPagoGasto.cs` (Efectivo/Transferencia/Cheque/Deposito), `Enums/TipoImpactoGasto.cs` (CajaChica/CajaMensual — R7, campo que el `Gasto` de marihogar no tiene), `Enums/TipoEntrega.cs` (Propia/Tercerizada), `Enums/EstadoEntrega.cs` (Pendiente/EnCamino/Entregada/NoEntregada, simplificado de marihogar).
- `Entities/CajaMovimiento.cs` — Fecha/Tipo/Monto/OrigenTipo("Venta"|"Gasto"|"Ajuste")/OrigenId/Descripcion, hereda `SoftDestroyable` (desvío documentado explícitamente respecto del original de marihogar, que es inmutable — acá los ajustes se resuelven con contramovimiento nuevo, nunca editando/borrando el original, así que el soft delete heredado queda sin uso práctico en el flujo normal).
- `Entities/CierreCajaDiario.cs` / `Entities/CierreCajaMensual.cs` — mismo shape (TotalIngresos/TotalEgresos/Saldo/CerradoPorUsuarioId/FechaCierre), índice único en `Fecha` / en `(Anio, Mes)` respectivamente. Pieza sin precedente exacto (ver escaneo arriba).
- `Entities/Gasto.cs` — Fecha/Categoria/Monto/FormaPago/TipoImpacto/Descripcion/Anulado/FechaAnulacion. Igual que en marihogar, un Gasto no se edita después de creado (solo Anular), y la anulación usa un flag `Anulado` propio (no soft delete) para que el gasto anulado siga visible con badge — el query filter global de `SoftDestroyable` lo ocultaría si se usara `DeletedAt`.
- `Entities/Entrega.cs` — VentaId (FK a la `Venta` de este proyecto, `OnDelete(Restrict)`, índice único — máximo 1 Entrega por Venta)/Tipo/CostoBase/PorcentajeMarkup/CostoFinal/Estado/RepartidorId (nullable, string sin FK a Identity, mismo patrón explícito que `Venta.VendedorId`)/Direccion/FechaProgramada/MotivoNoEntrega/FechaEntregada. `PorcentajeMarkup` es un snapshot del valor vigente en `EntregaMarkupSettings` al crear la entrega (mismo criterio de snapshot que `PagoVenta.PorcentajeRecargoAplicado`).

**Application** (`FerreteriaLaPlatense.Application`):
- `Settings/EntregaMarkupSettings.cs` (R2 — mismo criterio que `RecargoCuotasSettings`: appsettings.json en vez de pantalla dedicada, sin precedente de pantalla en `2-disenador-funcional.md`).
- `DTOs/CajaDtos.cs`, `DTOs/GastoDtos.cs`, `DTOs/EntregaDtos.cs`, `DTOs/DashboardDtos.cs` — nuevos.
- `Interfaces/ICajaMovimientoService.cs`, `IGastoService.cs`, `IEntregaService.cs`, `IDashboardService.cs` — nuevos.
- `Interfaces/IProductoService.cs` (Entrega 1, **modificado mínimamente**) — agregado `ContarStockCriticoAsync()` (mismo criterio de alerta que `AjusteStockService`, reutilizado por el Dashboard).

**Infrastructure** (`FerreteriaLaPlatense.Infrastructure`):
- `Data/AppDbContext.cs` — agregados `DbSet<CajaMovimiento/CierreCajaDiario/CierreCajaMensual/Gasto/Entrega>` + Fluent API (índice único `CierreCajaDiario.Fecha`, índice único `(CierreCajaMensual.Anio, Mes)`, índice único `Entrega.VentaId`, decimales con precisión `18,2`/`5,2` según el campo).
- `Services/CajaMovimientoService.cs` — `ListarMovimientosAsync` (DataTable), `EstaCerradoAsync` (guarda de negocio consultada por `VentaWorkflowService`/`GastoService` antes de persistir), `RegistrarMovimientoAsync` (sin `SaveChanges` propio, mismo patrón que `CuentaCorrienteClienteService`), `RegistrarMovimientoManualAsync` (alta manual con su propio `SaveChanges` + guarda de día cerrado), `ObtenerResumenDiaAsync`/`CerrarDiaAsync`/`ListarCierresDiariosAsync`, `ObtenerResumenMesAsync`/`CerrarMesAsync`/`ListarCierresMensualesAsync` (el cierre mensual agrega `CajaMovimiento` del mes calendario directamente, **no** exige que todos los días del mes ya tengan su `CierreCajaDiario` individual — asunción documentada, ver riesgos).
- `Services/GastoService.cs` — `CrearAsync` (transacción explícita `BeginTransactionAsync`, dos `SaveChangesAsync`: el primero asigna `Gasto.Id`, necesario como `OrigenId` del `CajaMovimiento`; guarda de día cerrado antes de crear), `AnularAsync` (contramovimiento de Ingreso fechado **hoy**, nunca en la fecha original del Gasto — así nunca choca con un día ya cerrado ni modifica retroactivamente un período cerrado), `ObtenerGastosMesPorCategoriaAsync` (consumido por el Dashboard).
- `Services/EntregaService.cs` — `ListarAsync` (**sin ningún filtro implícito por el usuario autenticado**, ver R9), `ListarRepartidoresAsync` (join `UserRoles`/`Roles` por `SeedData.RolRepartidor`), `ObtenerPrecargaDesdeVentaAsync` (exige `Venta.Estado == Facturada` + máximo 1 Entrega por Venta), `CrearAsync` (calcula `CostoFinal` desde `EntregaMarkupSettings` vigente), `IniciarRecorridoAsync`/`MarcarEntregadaAsync`/`MarcarNoEntregadaAsync`/`ReagendarAsync` (transiciones de estado validadas server-side), `ContarPendientesAsync` (consumido por el Dashboard).
- `Services/DashboardService.cs` — `ObtenerAsync()` único (nivel 1 + nivel 3), agrega `Venta`/`CajaMovimiento`(vía `ICajaMovimientoService`)/`Entrega`(vía `IEntregaService`)/`Gasto`(vía `IGastoService`)/`ItemVenta`/`Producto`(vía `IProductoService.ContarStockCriticoAsync`) — top 5 productos y gastos por categoría acotados al **mes calendario actual** (asunción documentada, `2-disenador-funcional.md` no precisa el período de "tendencias").
- `Services/ProductoService.cs` (Entrega 1, modificado mínimamente) — agregado `ContarStockCriticoAsync()`.
- `Services/VentaWorkflowService.cs` (ola 1, **modificado**) — inyectado `ICajaMovimientoService`. `ConfirmarYFacturarAsync` ahora: (a) valida `EstaCerradoAsync(hoy)` **antes** de llamar a AFIP (evita emitir un comprobante fiscal real si después no se puede persistir nada); (b) tras el éxito de AFIP, genera un `CajaMovimiento` de Ingreso por cada `PagoVenta` confirmado **excepto** los de medio `CuentaCorriente` (asunción documentada: ese pago es una deuda diferida, ya registrada como Débito en `MovimientoCCCliente`, no un ingreso real de caja del día).
- `DependencyInjection.cs` — registrados `ICajaMovimientoService`, `IGastoService`, `IEntregaService`, `IDashboardService` (Scoped) + `IOptions<EntregaMarkupSettings>`.

**Web** (`FerreteriaLaPlatense.Web`):
- `Models/CajaViewModels.cs`, `Models/GastoViewModels.cs`, `Models/EntregaViewModels.cs`, `Models/DashboardViewModels.cs` — nuevos.
- `Controllers/CajaController.cs` — `Index`/`Listar`/`MovimientoManual`(GET/POST)/`CerrarDia`/`Cierres`/`CierresListar`/`Mensual`/`CerrarMes`/`MensualListar`. Policy `RequireAdministracion` a nivel de clase (Vendedor no figura en la tabla de permisos del analista para este módulo).
- `Controllers/GastosController.cs` — `Index`/`Listar`/`Create`(GET/POST)/`Anular`. Policy `RequireAdministracion`.
- `Controllers/EntregasController.cs` — `Index`/`Listar`/`Repartidores`(combo)/`Create`(GET/POST, override a `RequireVentas` — sin Repartidor)/`Details`/`IniciarRecorrido`/`MarcarEntregada`/`NoEntregada`/`Reagendar`. Policy de clase `RequireEntregas` (nueva, `SuperUsuario`+`Administrador`+`Vendedor`+`Repartidor`) — primera pantalla real del rol `Repartidor`.
- `Controllers/DashboardController.cs` — `Index` único, policy `ConsultaDashboard` (ya existía, cualquier usuario autenticado) — sin reducción de contenido por rol en este corte (nivel 1/3 no expone datos sensibles restringidos a Admin, a diferencia de marihogar).
- `Controllers/VentasController.cs` — **no tocado** (la integración con Caja vive en `VentaWorkflowService`, capa de Negocio).
- `Views/Ventas/Details.cshtml` — agregado el botón "Programar entrega" (visible solo si `Estado == Facturada`), enlaza a `Entregas/Create?ventaId=`.
- `Program.cs` — nueva policy `RequireEntregas`.
- `appsettings.json` — nueva sección `EntregaMarkup` (`PorcentajeMarkup: 20`, ejemplo editable).
- `Views/Caja/*` (Index con resumen del día + botón de cierre + DataTable de movimientos + filtros, MovimientoManual, Cierres, Mensual con selector de período + histórico), `Views/Gastos/*` (Index con DataTable + filtros por cada columna visible + botón Anular con SweetAlert2, Create), `Views/Entregas/*` (Index con DataTable + filtro de repartidor cargado por AJAX, Create desde una Venta Facturada, Details con acciones derivadas del estado real — Iniciar recorrido/Marcar entregada/No entregada con motivo vía SweetAlert2 input/Reagendar vía SweetAlert2 date input), `Views/Dashboard/Index.cshtml` (jerarquía visual de 3 bloques: nivel 1 con 3 stat-cards grandes cliqueables al detalle, card "Próximamente: salud financiera" muted para nivel 2, nivel 3 con gráfico doughnut de Chart.js para gastos por categoría + lista de top productos + stat-card de stock crítico) — todas con SweetAlert2 en confirmaciones y DataTables server-side.
- `Views/Shared/_Layout.cshtml` — nuevo link "Dashboard" (primer ítem del sidebar, visible a cualquier usuario autenticado), nueva sección "Caja" (SuperUsuario/Administrador), nueva sección "Entregas" (SuperUsuario/Administrador/Vendedor/Repartidor).

**Migración EF:** `EntregaDos_CajaGastosEntregasDashboard` (20260811134720) — tablas `CajaMovimientos`, `CierresCajaDiarios`, `CierresCajaMensuales`, `Entregas`, `Gastos`. **No aplicada a ninguna base** (igual que las 2 migraciones previas del proyecto).

**Build:** `dotnet build FerreteriaLaPlatense.slnx` → 0 errores, mismas advertencias preexistentes (NU1902 MailKit/MimeKit, CS0114 HomeController). Verificado dos veces (antes y después de reforzar `GastoService` con transacción explícita).

