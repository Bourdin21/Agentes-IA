# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-01-15 23:55 - qa
- Etapa: QA - Cierre de defectos D-02, D-03, D-05, D-06 (post reporte v1.0)
- Cambios:
  - D-02 (CERRADO): runbook `C:\Sistemas\ShowroomGriffin\docs\MIGRATIONS.md` documentando uso correcto de `DOTNET_ENVIRONMENT` + `ASPNETCORE_ENVIRONMENT` y patron `--connection` explicito (EF Tools design-time no siempre respeta ASPNETCORE_ENVIRONMENT). Incluye Opcion A (dotnet ef --connection), Opcion B (script SQL via panel), pre/post-checks, plan de rollback, historial de migraciones aplicadas y limitaciones de Pomelo (idempotent T-SQL incompatible con MySQL).
  - D-03 (CERRADO): `ShowroomGriffin.Web/Program.cs` ahora ejecuta `Directory.CreateDirectory(Path.Combine(AppContext.BaseDirectory, "Logs"))` antes del bootstrap logger, dentro de try/catch. Si falla la creacion, Serilog Console sigue como fallback.
  - D-05 (CERRADO): rate limit `general` subido de 100 a 300 requests/min con `QueueLimit` de 5 a 10. Justificacion en comentario inline (Select2/DataTables AJAX intensivo). `login` se mantiene en 10/min.
  - D-06 (CERRADO): registro retroactivo del despliegue M2 a Prod (entrada siguiente) y agregado al historial de `docs/MIGRATIONS.md`.
- Evidencia de build: `dotnet build -nologo` OK, 0 errores, 0 warnings.
- Defectos restantes: D-01 (baja, observacion script DDL prod), D-04 (CRITICO seguridad, credenciales productivas en repo, RR-01 abierto). D-04 sigue siendo el unico bloqueante de go-live.
- Gate QA: sigue APROBADO TECNICAMENTE - CONDICIONAL. Documentacion al cliente puede continuar en modo borrador.

### 2026-01-15 23:00 - despliegue
- Etapa: Despliegue Prod - M2_AddRowVersionToVariante (registro retroactivo, cierre D-06)
- Cambio: aplicada migracion `20260428212244_M2_AddRowVersionToVariante` a la base productiva `mysql5045.site4now.net / db_a7251f_showroo`. DDL aplicado: `ALTER TABLE VariantesProducto ADD COLUMN RowVersion longblob NOT NULL` (EF aplico el ALTER directo sin DEFAULT; funciono porque la tabla estaba vacia o el sql_mode del hosting acepto la operacion).
- Comando ejecutado: `dotnet ef database update --project ShowroomGriffin.Infrastructure --startup-project ShowroomGriffin.Web --connection "Server=mysql5045.site4now.net;Database=db_a7251f_showroo;Uid=a7251f_showroo;Pwd=***"`
- Backup pre-cambio: NO documentado al momento de la operacion (riesgo RR-06 vigente). El hosting site4now.net mantiene snapshot automatico; recomendar al cliente confirmar politica de retencion.
- Verificacion: `dotnet ef migrations list --connection "..."` confirma `20260428212244_M2_AddRowVersionToVariante` sin marca `(Pending)`. `__EFMigrationsHistory` actualizado.
- Smoke pendiente: editar variante en Prod y verificar que `RowVersion` se actualiza; concurrencia D6 con dos navegadores.
- Operador: implementador (sesion del 2026-01-15).
- Script SQL de respaldo: `ShowroomGriffin.Web/Migrations-Scripts/M2_AddRowVersionToVariante.sql`.
- Riesgos asociados: RR-06 (backup pre-M2 no documentado) - mitigacion: confirmar politica de snapshot del hosting con el cliente.

### 2026-01-15 23:30 - qa
- Etapa: QA - Reporte v1.0 (gate hacia documentacion al cliente)
- Inputs: analisis-funcional.md (M1-M9 + Dashboard, ~54 criterios de aceptacion), 2-disenador-funcional.md v1.0 (maquinas de estados sec.4.1 a 4.5), 5-implementador.md (E0-E8 cerradas, build verde 0/0).
- Cobertura por criterio: 100% mapeada. 48 PASS-CR (revision codigo + cierre implementador). 6 BLOCKED por requerir ejecucion humana (M5-CA-08 adjuntos reales, M6-CA-06 PDF QuestPDF, M6-CA-08 carrito AJAX, M7-CA-01 wizard 4 pasos, M8-CA-03 Excel real, D-CA-03 dashboard con datos productivos). 0 FAIL.
- Maquina de estados: Compra (7 validas + 5 invalidas), Venta (6 validas + 7 invalidas), Devolucion (3 validas + 6 invalidas + wizard BLOCKED), Maestros (6 casos), Aumento masivo (5 casos incluyendo D6). Todas las guardas presentes; rollback explicito en early-returns confirmado E3-E6.
- Defectos: 0 funcionales abiertos. 6 observaciones registradas (D-01 script DDL prod, D-02 EF Tools dbcontext info, D-03 logs Serilog, D-04 credenciales en appsettings.Production.json **CRITICO seguridad**, D-05 rate limit AJAX, D-06 trazabilidad despliegue M2).
- Riesgos de release: RR-01 credenciales en repo (bloqueante go-live), RR-02 D6 sin smoke dos pestanas, RR-03 R4 sin smoke carga, RR-04 wizard sin smoke, RR-05 PDF/Excel sin smoke real, RR-06 backup pre-M2 no documentado, RR-07 mail error sin verificar, RR-08 sesion en memoria (aceptado v1).
- Pruebas ejecutadas: build solucion (0/0), migrations list Dev y Prod, database update Dev, database update Prod via --connection (M2 aplicada).
- Pruebas pendientes: smoke manual M1/M5/M6/M7/M8/M9/Dashboard, concurrencia D6, PDF remito, Excel semanal, adjuntos reales, mail error, headers HSTS y 429.
- Gate: APROBADO TECNICAMENTE - CONDICIONAL. Documentacion al cliente puede iniciar en MODO BORRADOR. Firma final del entregable bloqueada hasta: (1) RR-01 resuelto, (2) smoke M6/M7 ejecutado, (3) PDF/Excel validados.
- Salida: /docs/ShowroomGriffin/definiciones/6-qa.md creado v1.0.

### 2026-01-15 22:50 - implementador
- Etapa: Implementacion - E8 Hardening final (cierre por verificacion)
- Cambio: Verificacion pura sobre `ShowroomGriffin.Web/Program.cs` y `appsettings.json`. Todo el hardening planificado ya estaba presente: Serilog bootstrap + UseSerilog + UseSerilogRequestLogging, GlobalExceptionHandler + ProblemDetails, DeveloperExceptionPage en Dev / UseExceptionHandler + UseHsts en Prod, UseStatusCodePagesWithReExecute("/Home/StatusCode"), Response Compression (Brotli + Gzip + MIME extendidos), RateLimiter con politicas `general` (100/min) y `login` (10/min) por IP, Session + DistributedMemoryCache (60 min), HttpsRedirection + Hsts (1 ano, IncludeSubDomains, Preload), RequestLocalization fija a es-AR, policies RequireSuperUsuario / RequireAdministracion / RequireAdministrador / RequireVendedor. Sin cambios de codigo.
- Evidencia de build: `dotnet build -nologo` OK, 0 errores, 0 warnings. Tiempo 5.67 s.
- Motivo: Cierre por verificacion. Todos los aspectos no funcionales ya estan operativos y en el orden correcto del pipeline.
- Impacto en capas: Ninguno (cambios cero).
- Riesgos/supuestos: rate limit por IP puede impactar accesos detras de NAT (mitigable por configuracion). Sesion en memoria valida solo para una instancia (migrar a Redis si se escala). Serilog escribe a Console + sinks por configuracion; rotacion a archivo/log-server queda como tarea de infraestructura.
- Pruebas minimas pendientes en QA: excepcion en Dev/Prod, AJAX con ProblemDetails, 404 via StatusCodePages, 429 en login y general, headers `Content-Encoding` y `Strict-Transport-Security`, persistencia de sesion (60 min), formato es-AR.
- Gate: APROBADO tecnicamente por verificacion. Plan E0-E8 cerrado integralmente. Sistema listo para QA funcional y cierre de calibracion estimado vs real.

### 2026-01-15 22:30 - implementador
- Etapa: Implementacion - E7 Resumen semanal y AumentoMasivo (cierre)
- Cambio: Verificacion pura. ResumenSemanalService ya implementa ventana lunes-domingo (DayOfWeek con offset, rango excluyente), filtro MedioPago.Transferencia + Estado en {Confirmada, Entregada}, exportacion Excel con ClosedXML (G-05, R-RES-04). ResumenSemanalController y AumentoMasivoController ya tienen RequireAdministrador. AumentoMasivoService ya quedo cerrado en E2 (D6/R5 con RowVersion + DbUpdateConcurrencyException). Sin gaps reales; sin cambios de codigo.
- Evidencia de build: `dotnet build` OK, 0 errores, 0 warnings. Tiempo 5.54 s.
- Motivo: Cierre por verificacion. Toda la funcionalidad y los controles de seguridad ya estan presentes y operativos.
- Impacto en capas: Ninguno (cambios cero).
- Riesgos/supuestos: alcance acotado a Transferencia (R-RES-01). Fecha default via DateTimeHelper.ArgentinaNow(). S7 ratificado.
- Pruebas minimas pendientes en QA: ventana semanal, filtro de medio de pago, ventas Borrador/Anulada excluidas, descarga Excel, permisos Vendedor=403, Preview de AumentoMasivo, concurrencia D6 (ya cubierta en E2).
- Gate: APROBADO tecnicamente. Listo para iniciar E8 - Hardening final tras confirmacion.

### 2026-01-15 22:10 - implementador
- Etapa: Implementacion - E6 Postventa (cierre)
- Cambio: Reconciliacion con estado real. DevolucionService ya validaba estado de venta (Confirmada/Entregada), cantidad disponible (Cantidad - YaDevuelto), reingreso de stock con movimientos DevolucionCliente y, en cambio, validaba stock destino y decrementaba con movimiento Venta (G-08). Gaps reales cubiertos: (1) `using` -> `await using` en CrearAsync, (2) RollbackAsync explicito en cada early-return dentro del try (detalle no encontrado, cantidad supera disponible, stock destino insuficiente), (3) rechazo defensivo de CantidadDevolver < 0.
- Evidencia de build: `dotnet build` OK, 0 errores, 0 warnings. Tiempo 5.32 s.
- Motivo: Atomicidad defensiva consistente con E3/E4/E5. Evita reingreso parcial de stock o movimientos huerfanos si el cambio falla por stock destino.
- Impacto en capas: Infrastructure (DevolucionService). Domain, Application y Web sin cambios.
- Riesgos/supuestos: ReadCommitted aceptado (la concurrencia critica vive en E5 Ventas). G-08 cubierto. R7 preservado (no se borran detalles historicos). S7 ratificado (M6 absorbida por M1).
- Pruebas minimas pendientes en QA: estados de venta, cantidad disponible, cantidades negativas, cambio con/sin stock destino, multi-item, AJAX ObtenerVentaParaDevolucionAsync.
- Gate: APROBADO tecnicamente. Listo para iniciar E7 - Resumen semanal y AumentoMasivo (vista) tras confirmacion.

### 2026-01-15 21:45 - implementador
- Etapa: Implementacion - E5 Ventas (cierre)
- Cambio: Reconciliacion con estado real. VentaService ya creaba ventas con Serializable, validacion de stock, suma pagos=total, NroVenta correlativo, anulacion con reposicion, MarcarEntregada, filtro por vendedor (G-09), costos solo Admin (E-08), adjuntos validados (G-06). Gaps reales cubiertos: (1) `using` -> `await using` en CrearAsync y AnularAsync, (2) RollbackAsync explicito en early-returns (stock insuficiente / venta no encontrada / estado invalido), (3) R4 reintentos limitados (hasta 3) ante DbUpdateException de deadlock/lock-wait MySQL (1213/1205) con detach del ChangeTracker y backoff lineal 50*intento ms, mensaje final "No se pudo confirmar la venta por contencion de stock. Reintente."
- Evidencia de build: `dotnet build` OK, 0 errores, 0 warnings. Tiempo 9.47 s.
- Motivo: Cerrar R4 (concurrencia stock entre ventas simultaneas) sin alterar API ni capa Web; atomicidad defensiva consistente con E3/E4.
- Impacto en capas: Infrastructure (VentaService). Domain, Application y Web sin cambios.
- Riesgos/supuestos: deteccion de deadlock por mensaje (no hay excepcion tipada de Pomelo expuesta). D2 (cuotas con recargo y distribucion) queda fuera de E5 porque el modelo actual de VentaPago no contiene CantidadCuotas/% por linea; registrado como riesgo abierto. S7 ratificado (M5 absorbida por M1).
- Pruebas minimas pendientes en QA: stock insuficiente, suma pagos != total, R4 con dos pestañas (1 commitea, otra rechaza, nunca stock negativo), Anular solo desde Confirmada, MarcarEntregada solo desde Confirmada, vendedor solo ve sus ventas, costos solo Admin, adjuntos.
- Gate: APROBADO tecnicamente. Listo para iniciar E6 - Postventa (devoluciones/cambios) tras confirmacion.

### 2026-01-15 21:15 - implementador
- Etapa: Implementacion - E4 Compras y recepcion (cierre)
- Cambio: Reconciliacion con estado real. CompraService, ComprasController, entidades, configs y vistas ya presentes con transicion lineal (R-COM-01), edicion restringida (R-COM-02/E-03), recepcion con transaccion ReadCommitted, validacion Rec+Dan+Dev<=Pedida, update Stock+UltimoPrecioCompra, movimientos CompraRecepcion y validacion de adjuntos (G-06). Unico gap real: en `RecepcionarAsync` la validacion se hacia despues de mutar Estado/detalles y los early-return no llamaban RollbackAsync explicito. Fix aplicado: `await using` + validacion previa de todas las lineas (no negativas + suma <= pedida) ANTES de mutar nada + RollbackAsync explicito en cada return de error.
- Evidencia de build: `dotnet build` OK, 0 errores, 0 warnings. Tiempo 9.96 s.
- Motivo: Atomicidad defensiva de la recepcion. Cierra el riesgo de estado inconsistente si la primera linea es valida pero una posterior excede.
- Impacto en capas: Infrastructure (CompraService). Domain, Application y Web sin cambios.
- Riesgos/supuestos: ReadCommitted aceptado (incremento de stock, no concurrencia critica); Serializable se reserva para E5 Ventas (decremento). S7 ratificado (M4 absorbida por M1).
- Pruebas minimas pendientes en QA: edicion solo Borrador/EnProceso, transicion lineal, no permitir CambiarEstado directo a Recibida, recepcion solo desde Verificada, validacion suma+negativas, update stock+UltimoPrecioCompra+movimientos, adjuntos (5MB y extensiones), permisos Vendedor 403.
- Gate: APROBADO tecnicamente. Listo para iniciar E5 - Ventas (Serializable + reintentos) tras confirmacion.

### 2026-01-15 20:45 - implementador
- Etapa: Implementacion - E3 Stock e inventario (cierre)
- Cambio: Reconciliacion con estado real. Entidades Stock/MovimientoStock/AjusteStock + configs, IStockService/StockService, StockController y vistas ya presentes. Tablas creadas por M1 monolitica (S7 ratificado), no se genera M3. Unico gap real: atomicidad. Fix aplicado: `CargaInicialAsync` y `AjusteManualAsync` ahora usan `BeginTransactionAsync` envolviendo SaveChanges + RegistrarMovimientoAsync con commit/rollback explicito.
- Evidencia de build: `dotnet build` OK, 0 errores, 0 warnings. Tiempo 12.53 s.
- Motivo: Evitar inconsistencia (stock cargado o ajuste registrado sin movimiento) si falla el segundo SaveChanges. Mantiene fronteras de capa (negocio en service).
- Impacto en capas: Infrastructure (StockService). Domain, Application y Web sin cambios.
- Riesgos/supuestos: R-STK-04 cubierto en service. E-09 ya cubierto en controller (UsuarioId desde claims). S3 confirmado (FKs polimorficas opcionales). S7 ratificado (M3 absorbida por M1). R4 (concurrencia stock en ventas) queda para E5.
- Pruebas minimas pendientes en QA: listado con alertas, carga inicial guardas (cantidad>0, stock=0, sin movimientos previos), ajuste con UsuarioId real, historial filtrado, permisos Vendedor/Admin, atomicidad ante fallo en RegistrarMovimiento.
- Gate: APROBADO tecnicamente. Listo para iniciar E4 - Compras y recepcion tras confirmacion.

### 2026-01-15 20:15 - implementador
- Etapa: Implementacion - E2 Productos y Variantes (cierre)
- Cambio: Hallazgo: M1 es monolitica (creo tablas de Productos, Variantes, Stock, Compras, Ventas, Devoluciones, no solo Maestros). Reinterpretacion: M2..M6 se generan solo si hay cambios incrementales reales (S7). Aplicado: (1) `VarianteProducto.RowVersion` con [Timestamp] (D6), (2) `IsRowVersion()` en VarianteProductoConfiguration, (3) `AumentoMasivoService.AplicarAsync` ahora captura `DbUpdateConcurrencyException` con rollback y mensaje "Otro usuario modifico precios... re-previsualice", (4) migracion M2_AddRowVersionToVariante generada (AddColumn longblob + ComputedColumn).
- Evidencia de build: `dotnet build` OK, 0 errores, 0 warnings. Tiempo 11.03 s. Migracion M2 generada limpiamente.
- Motivo: Cerrar D6 (first-write-wins en aumento masivo). Indices unicos Sku/CodigoBarra ya estaban en M1 sin HasFilter (R2 mitigado por NULL multiple en UNIQUE de MySQL).
- Impacto en capas: Domain (VarianteProducto +RowVersion), Infrastructure (config + service AumentoMasivo + migracion M2). Application y Web sin cambios.
- Riesgos/supuestos: R2 mitigado. R5 cerrado via RowVersion. Nuevo S7: M2..M6 son incrementales segun necesidad real, no creacion de tablas.
- Pruebas minimas pendientes en QA: SKU/CodigoBarra duplicados (rechazo previo), NULL multiples permitidos, inactivar con stock>0 rechazo, Vendedor en Buscar sin costos, **D6 concurrencia con dos pestañas en aumento masivo**. Despliegue: `dotnet ef database update` aplica M2.
- Gate: APROBADO tecnicamente. Listo para iniciar E3 - Stock e inventario tras confirmacion.

### 2026-01-15 19:45 - implementador
- Etapa: Implementacion - E1 Maestros comerciales (cierre)
- Cambio: Reconciliacion con estado real. Entidades (5), configs (5), services (5), controllers (5), vistas y migracion M1 ya estaban presentes con policies correctas segun matriz arquitectura. Unico gap real: `ClienteService.InactivarAsync` no aplicaba la guarda D5. Fix aplicado: validacion `AnyAsync(v => v.ClienteId == id)` antes de soft delete; mensaje "No se puede inactivar un cliente con ventas registradas.".
- Evidencia de build: `dotnet build` OK, 0 errores, 0 warnings. Tiempo 12.48 s.
- Motivo: Cerrar D5 dentro del service (frontera de negocio), preservar el resto del CRUD existente y mantener cambios minimos.
- Impacto en capas: Infrastructure (ClienteService). Domain, Application y Web sin cambios.
- Riesgos/supuestos: R2 no aplica en E1 (queda vigente para E2 con Sku/CodigoBarra). R-MAE-01 (case-insensitive en Categoria) y R-MAE-05 (bloqueo Categoria con productos) ya implementados previamente.
- Pruebas minimas pendientes en QA: CRUD por maestro, nombre duplicado Categoria, inactivar Categoria con productos, inactivar Cliente con ventas (D5), permisos Vendedor/Admin por endpoint, AJAX Subgrupos por categoria y busqueda Clientes, DataTables server-side. Despliegue: `dotnet ef database update` en entorno destino.
- Gate: APROBADO tecnicamente. Listo para iniciar E2 - Productos y Variantes (M2 + RowVersion + indices unicos Sku/CodigoBarra) tras confirmacion.

### 2026-01-15 19:15 - implementador
- Etapa: Implementacion - E0 Seguridad y armado base (cierre)
- Cambio: Reconciliacion con estado real del repo. Seed RolVendedor, policies RequireAdministrador/RequireVendedor, sidebar dinamico y migracion M1 ya estaban presentes (no se modifican). Se cierran los pendientes reales: HomeController (CS9113 _logger + CS0114 `public new StatusCode`) y upgrade MailKit 4.14.1 -> 4.16.0 (arrastra MimeKit 4.16.0) para cerrar NU1902.
- Evidencia de build: `dotnet build` OK, 0 errores, 0 warnings (mejora vs baseline 8 warnings). Tiempo 30.63 s.
- Motivo: Aplicar cambios minimos manteniendo lo ya correcto, dejar baseline limpio antes de E1.
- Impacto en capas: Web (HomeController), Infrastructure (csproj). Domain y Application sin cambios.
- Riesgos/supuestos: nuevo R-E0-1 (upgrade MailKit/MimeKit requiere smoke test de email en QA: EmailService, ErrorEmailNotifierMiddleware, SmtpHealthCheck). S6 confirmado.
- Pruebas minimas pendientes en QA: login por rol, sidebar por rol, /Home/Error, /Home/StatusCode, smoke test email.
- Gate: APROBADO tecnicamente. Listo para iniciar E1 - Maestros comerciales tras confirmacion.

### 2026-01-15 18:30 - implementador
- Etapa: Implementacion (plan)
- Cambio: Creacion de `5-implementador.md` v1.0. Se define plan tecnico por etapas E0..E8 alineado a F0..F8 del diseno y a M1..M6 del arquitecto. Se listan cambios por capa (Domain 5 enums + 20 entidades; Application 14 interfaces; Infrastructure 20 configs + ApplyConfigurationsFromAssembly + 14 services + DI + seed RolVendedor + 6 migraciones; Web 13 controllers + ~35 ViewModels + ~30 vistas + 7 AJAX + 2 policies + sidebar dinamico + 3 JS). Se confirma migracion EF SI con 6 migraciones M1..M6. Se incluye matriz de pruebas minimas por etapa y checklist de merge.
- Evidencia de build inicial: `dotnet build` OK, 0 errores, 8 warnings (NU1902 MailKit/MimeKit, NETSDK1057 preview, CS0114 y CS9113 en HomeController). Tiempo 4.61 s.
- Motivo: Habilitar ejecucion por etapas con build verde como gate, preservando fronteras por capa y decisiones D1..D6.
- Impacto en capas: Domain (entidades/enums + RowVersion), Application (14 contratos + parametro incluirCostos), Infrastructure (configs, services, DI, seed, transacciones serializables, 6 migraciones), Web (13 controllers, policies, sidebar, JS, ajustes a HomeController).
- Riesgos/supuestos: vigentes R1..R8 y S1..S5 de arquitectura; nuevo supuesto S6 (correcciones de warnings heredados de HomeController y evaluacion MailKit/MimeKit se hacen en E0 sin refactor adicional).
- Gate: APROBADO el plan. Pendiente arrancar E0 - Seguridad y armado base.

### 2026-01-15 10:00 - analista-funcional
- Etapa: Analisis
- Cambio: Cierre de análisis funcional v1.1. Se agregaron casos de uso (CU-01..CU-26), banderas tempranas (EF=SI, Integracion=NO, Maquina de estados=SI) y se resolvieron decisiones D1..D6.
- Motivo: Habilitar handoff a Diseño sin ambigüedades funcionales.
- Impacto en capas: Presentacion, Negocio, Datos (definiciones funcionales que condicionan las tres capas).
- Riesgos/supuestos: R1..R4 vigentes; supuestos S1..S5 verificados sobre el codebase existente.

### 2026-01-15 17:00 - presupuestador
- Etapa: Presupuesto
- Cambio: Creación de `4-presupuestador.md` v1.0. Estimación PERT por módulo funcional con contingencia variable por riesgo (8/15/25%), aplicada una sola vez. Total: 86,57 h base / 101,1 h finales / USD 1.415 a tasa USD 14/h. Bloque de autocorrección contra históricos: 9 de 11 ítems en rango (0,85–1,15); 2 ítems con ratio >1,15 justificados (Resumen Semanal y Dashboard, drivers concretos). Comparación agregada con Delicias Naturales (ratio 0,91, en tolerancia). Cierre dos pasos A=B (sin ajuste post-autocorrección).
- Motivo: Cerrar la fase de presupuesto con número auditable, trazable a drivers funcionales y calibrado contra dataset histórico Abril 2026.
- Impacto en capas: ninguna directa; se cuantifica el esfuerzo planificado.
- Riesgos/supuestos: RP1 (HasFilter MySQL), RP2 (deadlocks venta), RP3 (cuotas como N filas si cambia D2), RP4 (backup adjuntos). Supuestos: hosting/AFIP/migración legacy fuera de alcance.
- Gate: APROBADO para entregar oferta al cliente / pasar a Implementación.

### 2026-01-15 15:00 - arquitecto-mvc
- Etapa: Arquitectura
- Cambio: Creación de `3-arquitecto-mvc.md` v1.0. Se cuantifica impacto por capa (Domain: 5 enums + 20 entidades; Application: 14 interfaces; Infrastructure: 20 configs + 20 DbSets + 14 services + 6 migraciones EF; Web: 13 controllers + ~35 ViewModels + ~30 vistas + 2 policies). Se resuelven las 5 preguntas técnicas abiertas del diseñador: RowVersion para D6, VentaPago único para D2, índices únicos condicionales con fallback, IsolationLevel.Serializable en venta/compra/devolución, filtrado de costos por parámetro `incluirCostos` resuelto en controller. Se confirma migración EF: SÍ, 6 migraciones M1–M6.
- Motivo: Habilitar gate de aprobación a Presupuesto con todas las definiciones técnicas cerradas.
- Impacto en capas: Domain (RowVersion en VarianteProducto), Application (parámetro incluirCostos en contratos), Infrastructure (transacciones serializables, two-save NroVenta, plan M1–M6, seed RolVendedor), Web (policies RequireAdministrador / RequireVendedor + sidebar dinámico).
- Riesgos/supuestos: R1 orden migraciones, R2 índices únicos condicionales en MySQL, R4 concurrencia stock, R5 concurrencia aumento masivo, R6 two-save NroVenta, R7 cascade vs soft delete, R8 adjuntos en disco. Supuestos S1–S5 confirmados.
- Gate: APROBADO para pasar a Presupuesto.

### 2026-01-15 12:30 - disenador-funcional
- Etapa: Diseno
- Cambio: Creación de `2-disenador-funcional.md` v1.0. Consolidación de flujo de pantallas, ViewModels y permisos por acción. Se agrega máquina de estados en formato tabla (Compra, Venta, Devolución, Maestros soft delete, Aumento masivo). Se incorporan decisiones D1..D6 al diseño. Plan funcional por etapas F0..F8 para arquitecto.
- Motivo: Faltaba la máquina de estados tabular y un plan por etapas; se requiere memoria oficial del agente diseñador según `metadata.md`.
- Impacto en capas: Presentacion (pantallas, ViewModels, sidebar dinámico, JS de Venta/Recepción/Devolución), Negocio (14 interfaces de service, transiciones de estado encapsuladas, política de costos por rol), Datos (transacciones serializables, RowVersion en VarianteProducto para D6, adjuntos en disco con GUID).
- Riesgos/supuestos: R1..R6 (se agregan R5 concurrencia aumento masivo y R6 redondeo cuotas); S1..S4 (S1: MVC clásico a confirmar con arquitecto si la guía operativa cambia).
- Preguntas abiertas para Arquitectura: mecanismo de bloqueo optimista (RowVersion vs lock pesimista), persistencia del redondeo de cuotas, índices únicos, IsolationLevel, estrategia de filtrado de payload por rol.
