# Memoria - Presupuestador

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-10-05 (v9 — Plan de cierre de alcance con los 3 gates del cliente cerrados y el reuse anclado en `marihogar`; sin precio nuevo)

## Definiciones vigentes

### Plan de cierre de alcance — Entregas 3 a 6 (2026-10-05)

**Que es:** la secuenciacion de lo que falta construir para cerrar el alcance completo del sistema. **No es un presupuesto nuevo.** Todos los modulos de abajo salen del WBS de Etapa 1 + Etapa 2 ya aprobado por el cliente el 2026-07-30 y **ya cobrado** dentro de los USD 1.500 (3 pagos) / USD 1.800 (12 pagos). Las horas son las M del WBS vigente, sin recotizar.

**Estado de partida (verificado contra el repo el 2026-10-05, rama `entrega-1-migracion`):** 17 controladores, 24 entidades. Construido y en produccion: catalogo, unidades/conversion, stock + ABC + ajustes, codigos de barras multiples, usuarios/roles, ventas Borrador→Confirmada→Facturada, CC de clientes **solo de consulta**, caja diaria/mensual, gastos, entregas, dashboard, configuracion de recargos, migracion de catalogo (112.485 productos + 2.990 clientes). `AfipService` esta codificado pero deshabilitado a proposito (sin certificado del cliente). `Proveedor` existe solo como catalogo simple minimo creado en Etapa 3 — sin ABM, sin sidebar, sin CC, sin compras. `EstadoVenta.Anulada` existe en el enum pero **ningun codigo la dispara**: no hay anulacion de ningun tipo.

#### Sprint 0 — Deuda abierta (prerequisito de todo lo demas, ~8h, SIN CARGO)

| # | Item | M (h) | Por que no se factura |
|---|---|---:|---|
| 0.1 | Deploy pendiente del commit `a6a78f0` + migracion EF `EntregaTres_ConfirmarSinFactura_RecargoCuotas_NotaPago` (tabla `RecargosCuota` + `PagosVenta.Nota`) | 0,5 | Entrega ya cerrada, nunca subida |
| 0.2 | **D8** — "Confirmar y facturar" no persiste el borrador antes de facturar | 1 | Defecto (garantia). **Bloqueante antes de cargar el certificado AFIP** |
| 0.3 | **D9** — `CajaMovimiento.Fecha`/`GastoService` mezclan `DateTime.Today` y `DateTime.UtcNow`: la venta de las 22:44 se lista como del dia siguiente | 1,5 | Defecto (garantia). **Definicion cerrada 2026-10-05**: dia de negocio = dia calendario en hora Argentina, mes de negocio = mes calendario cerrado el dia 1. Incluye verificar que el cierre mensual admita cerrar un mes anterior al actual |
| 0.4 | Correccion de datos: 87.542 de 112.485 productos (78%) migrados con `UnidadVenta = Metro` — modo correctivo del script, mismo patron que `--solo-codigo-propio` del 2026-09-02. **Regla cerrada 2026-10-05**: pasan en bloque a `Unidad` (el `METRO` del legado es su default basura — 2.898 de ellos se llaman a si mismos "Unidad de…" o "C/U…") + lista de 2.635 candidatos a corte por metro para marcar a mano | 2 | Consecuencia de Etapa 3 ya cobrada |
| 0.5 | **Cobro de CC de clientes** — pantalla de registro de pago + ajuste manual, con impacto en Caja. Hoy `RegistrarMovimientoAsync` lo llama solo `VentaWorkflowService`: los origenes `Pago`/`Ajuste` del enum no tienen camino desde la UI y el cobro del fiado se lleva por fuera del sistema | 3 | Gap de alcance ya entregado y cobrado (modulo 5 del WBS, "Ventas + CC clientes"). Una CC que no admite cobros esta incompleta, no es un modulo nuevo |
| | **Subtotal** | **8** | |

#### Entrega 3 — Proveedores + Compras (cierra Etapa 1 del presupuesto)

| # | Item | Base de reutilizacion |
|---|---|---|
| 3.1 | Ampliar `Proveedor` (CUIT, condicion IVA, TC propio, % de descuento, contacto, forma de pago habitual) + migracion EF **aditiva** + ABM propio con entrada de sidebar | La entidad ya existe como catalogo simple: se amplia, no se reemplaza (ver el XML doc de `Proveedor.cs`) |
| 3.2 | Compra con items, TC propio del proveedor, bonificacion, impacto en stock y en el costo del producto | `marihogar` M12+M13 |
| 3.3 | Importacion de listas de precios de proveedor (recurrente, distinta de la migracion de una sola corrida de Etapa 3) | Reusa `CodigoProveedorProducto` + el contrato preview→confirmar de `ICatalogoMigracionService` |
| 3.4 | CC de proveedores + pago con echeck/transferencia | Patron ledger de `MovimientoCCCliente`, ya construido |

**Total: 18h** (modulo 7 del WBS Etapa 1 — 13h reuse + 5h nuevo).

Gates abiertos: **ninguno**. Es el bloque mas grande que falta y el unico pendiente de Etapa 1 — arranca sin esperar nada del cliente.

#### Entrega 4 — Cuentas corrientes y consolidado

| # | Item | M (h) | Base de reutilizacion |
|---|---|---:|---|
| 4.1 | CC de empleados (autoservicio: cada empleado ve su sueldo y retiros, nunca los de un companero) | 4 | Patron ledger conocido (1h) + 3h nuevo |
| 4.2 | CC propia del negocio (consolidado de cierres de caja, ingresos y egresos) | 5 | `ganaderia` CajaService (2h) + 3h nuevo |
| | **Total (modulos 12 y 13 del WBS Etapa 2)** | **9** | |

Depende de la Entrega 3: la CC de proveedores entra al consolidado del negocio.

#### Entrega 5 — AFIP real + devoluciones/NC-ND + anulacion

| # | Item | Observacion |
|---|---|---|
| 5.1 | Habilitar facturacion electronica: certificado real del cliente, homologacion, primera factura real, verificacion del circuito posterior (descuento de stock, CC, caja) que nunca se probo en la practica | Residual del modulo 6 (~3h de las 7h), ya codificado y hardeado contra los 2 bugs reales de `marihogar`. **D8 tiene que estar corregido antes** |
| 5.2 | Devoluciones de mercaderia con reingreso de stock + NC/ND AFIP vinculada al comprobante original | `ShowroomGriffin` devoluciones |
| 5.3 | **Anulacion de venta — cambio de alcance real respecto de `1-analista-funcional.md` §6.5** | Ver nota de abajo |

**Total: 12h** (modulo 17 del WBS = 9h + ~3h residuales del modulo 6).

**Nota de alcance (la unica pieza del plan que se aparta del diseno aprobado):** §6.5 definia la anulacion como "transicion `Facturada`→`Anulada` disparada por la emision de una NC, sin anulacion silenciosa sin comprobante fiscal". Ese diseno es de antes del 2026-09-03, cuando `Confirmada` paso a ser la forma normal de cerrar una venta sin factura. Hoy la mayoria de las ventas reales nunca llegan a `Facturada`, asi que hacen falta **dos caminos**: anular una `Confirmada` (reversa de stock, caja y CC, **sin** comprobante fiscal — caso que el diseno original no preveia) y anular una `Facturada` (por NC AFIP, como estaba definido). No agrega horas al modulo 17; cambia su diseno.

Gates abiertos: **solo el certificado AFIP del cliente** (sin el, 5.1 y 5.2 no se pueden cerrar). La pregunta abierta 7 quedo cerrada el 2026-10-05: **anula el Administrador o el usuario que creo la venta** (un vendedor solo sus propias ventas, validando `UsuarioId`; el repartidor no anula), **sin limite de tiempo propio del sistema** — el unico tope real es el que imponga AFIP para la NC de una venta ya facturada.

#### Entrega 6 — Herramientas comerciales

| # | Item | M (h) | Base de reutilizacion |
|---|---|---:|---|
| 6.1 | Presupuestos y cotizaciones en PDF | 8 | `marihogar` M4, reuse total |
| 6.2 | Aumento masivo de precios por categoria / proveedor / marca | 4 | `marihogar` / `ShowroomGriffin`, reuse total |
| | **Total (modulos 14 y 16 del WBS Etapa 2)** | **12** | |

Sin dependencias de ninguna otra entrega ni del cliente. Es la valvula de escape del plan: si el certificado AFIP se demora, esta entrega se adelanta sin romper nada.

#### Resumen y orden recomendado

| Bloque | M (h) | Gate | Precio |
|---|---:|---|---|
| Sprint 0 — deuda abierta | 8 | **ninguno** (las 2 definiciones se cerraron el 2026-10-05) | sin cargo |
| Entrega 3 — Proveedores + Compras | 18 | ninguno | ya cobrado (Etapa 1) |
| Entrega 4 — CC empleados + CC negocio | 9 | Entrega 3 | ya cobrado (Etapa 2) |
| Entrega 6 — Presupuestos PDF + aumento masivo | 12 | ninguno | ya cobrado (Etapa 2) |
| Entrega 5 — AFIP + devoluciones + anulacion | 12 | **solo el certificado AFIP** (la pregunta abierta 7 se cerro el 2026-10-05) | ya cobrado (Etapas 1 y 2) |
| **Total restante** | **59** | | **USD 0 de precio nuevo** |

**Orden:** Sprint 0 → E3 → E4 → E6, con E5 insertandose en cuanto llegue el certificado del cliente (no bloquear la secuencia esperandolo). Las 51h del WBS mas las 8h de Sprint 0 cierran el 100% del alcance comprometido: al terminar E5 no queda ningun modulo del presupuesto sin construir.

**Lo que este plan deja deliberadamente afuera** (no esta comprometido ni cotizado): cambios/canjes de mercaderia, integracion con balanzas o ticketeadora de etiquetas, las 217 fichas de clientes reales distintos bajo un mismo CUIT descartadas por el dedupe (decision de Joaquin del 2026-09-28: se cargan a mano cuando aparezcan), y ABM de pantalla para codigos alternos / codigos de proveedor (hoy solo lectura, por decision de alcance).

**Decisiones bloqueantes: las 3 quedaron cerradas el 2026-10-05.** Detalle y evidencia en `1-analista-funcional.md`, seccion "Decisiones del cliente del 2026-10-05". Resumen: (1) dia de negocio = dia calendario en hora Argentina, mes = mes calendario cerrado el dia 1 sobre el mes anterior; (2) anula el Administrador o el usuario que creo la venta, sin limite de tiempo propio del sistema; (3) `UnidadVenta`: el cliente respondio "no se", se resolvio midiendo la base — los 87.542 `Metro` pasan a `Unidad` en bloque y se marcan a mano los 2.635 candidatos reales a corte. **El plan no tiene mas gates que el certificado AFIP de la Entrega 5.**

#### Anclaje de reutilizacion — instruccion de Joaquin del 2026-10-05

Todo lo que falta **se toma de `marihogar`** (`C:\Sistemas\marihogar`), no se disena de cero: AFIP, notas de credito, circuito de ventas, presupuestos, aumento masivo, proveedores, compras y pagos de compras. Verificado que el precedente existe archivo por archivo:

| Pieza del plan | Origen en `marihogar` |
|---|---|
| E5 — AFIP + NC/ND | `ComprobanteAfipService.cs`, `AfipService.cs`, `TipoComprobanteAfip.cs`, migracion `20260821143237_AddNotaCreditoAfip`, `ComprobantesAfipController.cs` |
| E5 — circuito de ventas / anulacion | `VentaService.cs`, `PagoVentaService.cs`, `VentasController.cs` |
| E3 — Proveedores | `ProveedorService.cs`, `ProveedoresController.cs` |
| E3 — Compras | `OrdenCompraService.cs`, `OrdenesCompraController.cs` |
| E3 — Pagos de compras | `PagoOrdenCompraService.cs`, `EgresoPagoProveedorService.cs`, `PagoOrdenCompraVencimientoHostedService.cs`, `ChequeService.cs` (echeck/diferidos) |
| E3 — CC de proveedores | `CCProveedorService.cs` |
| E4 — CC propia del negocio | `CCLocalService.cs` + `CCLocalController.cs` (**precedente directo, mejor que el `CajaService` de `ganaderia` que asumia el WBS**) |
| E6 — Presupuestos PDF | `PresupuestoService.cs`, `PresupuestosController.cs` |
| E6 — Aumento masivo | `AumentoMasivoPrecioService.cs`, `AumentoMasivoPreciosController.cs` |

Efecto sobre las horas: **ninguno a la baja todavia**. Las M del WBS ya estaban ancladas en `marihogar` (modulo 7 = `marihogar` M12+M13, modulo 14 = M4, modulo 16 = reuse total), asi que esta confirmacion valida la estimacion en vez de reducirla. La unica mejora real es la CC del negocio (item 4.2), que pasa de "3h nuevas sobre `ganaderia`" a tener precedente directo — se refleja en el cierre de calibracion, no en una recotizacion.


### Etapa 3 — Presupuesto real (2026-08-17), reemplaza la referencia provisional

**Contexto:** la referencia histórica (v2/v3 de este documento, ver Historial) era una hipótesis de trabajo: ~17.000 filas migradas desde un archivo Excel de formato desconocido, con 25% de riesgo declarado por esa incertidumbre — nunca se cotizó en firme. Con el backup real de SQL Server analizado (`1-analista-funcional.md`, `2-disenador-funcional.md` flujo 10, `3-arquitecto-mvc.md`), el volumen real es **121.691 artículos activos (7x el supuesto)** pero el riesgo de "formato desconocido" queda resuelto — el esquema, las reglas de deduplicación y el origen de ventas para ABC ya están definidos con datos reales, no quedan por descubrir. El alcance también creció respecto de la hipótesis original: ya no es "solo migrar filas", incluye clasificación ABC automática por ventas y extensión de `Producto`/`Cliente` con los gaps confirmados.

**WBS (Working Breakdown Structure) por ítem:**

| # | Ítem | M (h) | Base de reutilización |
|---|---|---:|---|
| 1 | Extracción/limpieza batch (dedup nombre 2 niveles, dedup `articuloProveedor` por última importación conciliada, exclusiones, ABC inicial por Pareto) | 8 | Sin precedente exacto — reglas de negocio específicas de este dataset, 100% desarrollo nuevo |
| 2 | `CodigoProveedorProducto` (entidad + config EF) | 2 | Patrón de catálogo simple ya resuelto en Entrega 1 (Marca/Modelo/Categoria) — 2h reuse |
| 3 | `ICatalogoMigracionService` (import preview→confirmar, idempotente) | 3 | Mismo contrato que `IListaPreciosProveedorImportService` de Entrega 2 — 3h reuse |
| 4 | `IClasificacionAbcAutomaticaService` (cálculo Pareto sobre `ItemVenta` + UI de sugerencia) | 5 | Sin precedente exacto — desarrollo nuevo |
| 5 | Extensión `Producto`/`Cliente` (6 campos: Bonificacion, ClasificacionABCSugerida, Domicilio, Localidad, Email, Notas) + migración EF | 3 | Modificación sobre módulo existente — desarrollo nuevo pero de bajo riesgo (campos simples) |
| 6 | Reporte de excepciones (pantalla informativa, sin persistencia propia) | 2 | Sin precedente exacto — desarrollo nuevo |
| 7 | Carga real de datos a producción (ejecución del batch, validación contra el reporte de excepciones, iteración con Joaquín) | 4 | Sin precedente exacto — operación puntual de este proyecto |
| | **Subtotal** | **27** | |

**Cálculo de reutilización (R):** horas ancladas en reuse directo = ítems 2+3 = 5h. Horas de desarrollo nuevo = 22h. **R = 5/27 = 18,5% → Tier 3 (R < 40%): 0% de descuento** — coherente con que esta es una ampliación sobre un sistema ya entregado (`27-presupuesto-parametros.instructions.md`: "Merge sobre sistema propio ya entregado... se cotiza siempre a precio de lista, sin descuento"), no un Build inicial de cliente nuevo.

**Riesgo declarado (cualitativo, no aplicado como % ciego sobre la fórmula):** clasificado como riesgo **Alto** por tratarse de migración de datos legado con inconsistencias reales medidas (ver Análisis: 49% del historial de importaciones de proveedor sin conciliar, 3.612 grupos de duplicados que requieren regla heurística). El riesgo ya está incorporado en el M de cada ítem (especialmente el ítem 1, estimado en el techo realista de su banda) en vez de aplicarse como un multiplicador adicional sobre el total — evita doble contingencia.

**Cálculo económico (fórmula vigente, `27-presupuesto-parametros.instructions.md`):**

| Concepto | USD |
|---|---:|
| Subtotal (lista, 27h × $16,80) | 453,60 |
| Tokens IA (25% del subtotal de lista) | 113,40 |
| Descuento Tier 3 (0%) | 0,00 |
| **Precio final Etapa 3** | **≈ 567,00** |

**Comparación con la referencia histórica (v2/v3, nunca cotizada en firme):** el número sube frente al rango provisional anterior (USD 315-394) pese a que se resolvió el riesgo de formato desconocido, porque (a) el volumen real es 7x el supuesto original y (b) el alcance funcional creció (ABC automática + extensión de Producto/Cliente + reporte de excepciones no estaban en la hipótesis original de "solo migrar filas"). No es una subida de criterio de precio, es un presupuesto real sobre un alcance mejor definido y más amplio que la hipótesis de trabajo anterior.

**Este número queda pendiente de aprobación de Joaquín antes de pasar a Implementación de Etapa 3** — mismo gate que Entregas 1 y 2 ("No iniciar Implementación sin Presupuesto aprobado por el cliente", `00-operativa-global.instructions.md`).

### Código de barras múltiple por producto — Presupuesto (2026-08-21)

**Contexto:** hallazgo real post-migración (ver `1-analista-funcional.md` §10) — 4.371 de 23.197 artículos con código de barras tienen más de uno real (variantes de fábrica agrupadas bajo un mismo producto interno), y el modelo actual los descarta a todos por "ambiguos". Es una **corrección/ampliación puntual sobre un módulo ya entregado** (Código de barras, Etapa 1 módulo 11) — mismo criterio de clasificación que el resto del trabajo de esta sesión sobre Producto (recargo/oferta, baja en lote, restablecer contraseña): "Merge sobre sistema propio ya entregado", sin descuento de expansión aplicable (`27-presupuesto-parametros.instructions.md`).

| # | Ítem | M (h) | Base de reutilización |
|---|---|---:|---|
| 1 | Entidad `CodigoBarrasProducto` (Domain + EF config) | 1 | Patrón idéntico a `CodigoProveedorProducto` (Etapa 3) — reuse directo |
| 2 | Migración EF (tabla nueva, aditiva) | 0,5 | — |
| 3 | Extensión `ICodigoBarrasLookupService` (buscar en `Producto.CodigoBarras` OR `CodigoBarrasProducto`) | 1 | Servicio ya existente, solo amplía la condición del `WHERE` |
| 4 | Extensión del script `tools/MigracionCatalogo` (backfill de los códigos alternos perdidos para los 4.371 artículos) | 1,5 | Reutiliza la lógica de resolución de ganador y lectura `Tipo='B'` ya construida — solo cambia el destino de escritura |
| 5 | Ficha de Producto: sección de solo lectura "Otros códigos de barras válidos" | 0,5 | — |
| | **Subtotal** | **4,5** | |

**Cálculo económico:**

| Concepto | USD |
|---|---:|
| Subtotal (lista, 4,5h × $16,80) | 75,60 |
| Tokens IA | 0,00 (no aplica — 2,16h facturables, bajo el umbral de 4h de `27-presupuesto-parametros.instructions.md`) |
| Descuento por Tier | 0,00 (no aplica — merge sobre sistema ya entregado) |
| **Precio de lista** | **≈ 76** |

**Nota de criterio (para que Joaquín decida, no una recomendación cerrada):** este hallazgo salió de la misma investigación que ya se venía haciendo por el reclamo original del cliente sobre el código de barras mal migrado (mismo módulo, mismo día) — es defendible tratarlo como continuación de esa corrección ya en curso (sin cargo adicional), en vez de un ítem nuevo a cobrar. Ambos caminos son razonables; queda a criterio comercial de Joaquín, no es una decisión técnica.

### WBS funcional vigente

**Etapa 1 (MVP operable — lo mínimo para reemplazar el manejo manual del día a día)**

| # | Módulo | M (h) | Base de reutilización |
|---|---|---:|---|
| 1 | Usuarios y roles (admin/vendedor/repartidor, repartidor ve todas las entregas) | 5 | `marihogar` M10 (4h) + 1h nuevo |
| 2 | Catálogo de productos (desc./IVA config./marca/modelo) | 9 | `marihogar` M2 (8h) + `ShowroomGriffin` (Marca/Modelo) + 1h nuevo |
| 3 | Unidades de medida y conversión compra↔venta | 5 | Sin precedente exacto — 100% desarrollo nuevo |
| 4 | Stock + alertas + puesta a punto de stock inicial (ajuste manual, flag negativo, ABC) | 8 | `marihogar` M3 (6h) + `ShowroomGriffin` ajuste manual (1h) + 1h nuevo |
| 5 | Ventas + CC clientes (recargo cuotas + workflow Borrador→Facturada) | 23 | `marihogar` M5+M11 (17h) + 6h nuevo |
| 6 | Facturación AFIP (Factura) | 7 | `marihogar`/`delicias-naturales`, reuse total |
| 7 | Proveedores + compras (TC propio + % desc. + importación de listas) | 18 | `marihogar` M12+M13 (13h) + 5h nuevo |
| 8 | Caja (cierre diario + mensual, punto de venta único) | 7 | `marihogar` M15 (4h) + 3h nuevo |
| 9 | Gastos varios (caja chica/mensual) | 4 | `marihogar` M18 (3h) + 1h nuevo |
| 10 | Dashboard — "foto completa del negocio" (3 niveles, prioridad de diseño confirmada) | 12 | `marihogar` M9 (6h) + 6h nuevo |
| 11 | **Código de barras — vinculación al producto + lectura en venta (SIMPLIFICADO — la ticketeadora es manual, no se integra)** | 3 | Buscador de venta (1h, mismo proyecto) = 1h reuse + 2h nuevo (campo único + lookup por código) |
| | **Subtotal Etapa 1** | **101** | |

**Etapa 2 (alcance complementario)**

| # | Módulo | M (h) | Base de reutilización |
|---|---|---:|---|
| 12 | Cuenta corriente de empleados (autoservicio) | 4 | Patrón ledger conocido (1h) + 3h nuevo |
| 13 | Cuenta corriente propia del negocio (consolidado) | 5 | `ganaderia` CajaService (2h) + 3h nuevo |
| 14 | Presupuestos y cotizaciones en PDF | 8 | `marihogar` M4, reuse total |
| 15 | Entregas a domicilio (markup + propia/tercerizada) | 8 | `marihogar` M6 (6h) + 2h nuevo |
| 16 | Aumento masivo de precios (cat./proveedor/marca) | 4 | `marihogar`/`ShowroomGriffin`, reuse total |
| 17 | Devoluciones de mercadería + Notas de crédito/débito AFIP | 9 | `ShowroomGriffin` devoluciones (3h) + extensión AFIP (1h) + workflow anulación (1h) = 5h reuse + 4h nuevo |
| | **Subtotal Etapa 2** | **38** | |

*Nota: "Cheques (30/60/90 días)" sigue sin presupuestarse como módulo aparte — se absorbe como campo de forma de pago dentro del módulo 7.*

### Migración de catálogo — RETIRADA de este presupuesto (2026-07-30)

Se saca como etapa del presupuesto actual, a pedido explícito de Joaquín. Motivos:
1. El problema real que la motivaba —el cliente no tiene stock confiable hoy— ya queda resuelto por el módulo 4 (puesta a punto de stock inicial), que es **independiente** de si el catálogo se migra por archivo o por acceso a base de datos.
2. Joaquín va a hacer un **segundo relevamiento tras la aprobación de este presupuesto**, para evaluar acceso directo a la base de datos del sistema actual del cliente — de lograrlo, el costo real de importación bajaría al mínimo comparado con mapear un archivo Excel de formato desconocido (que era la hipótesis de trabajo de la versión anterior de este documento, ~15h / USD 394 provisional).
3. Se cotiza en una fase posterior, separada de este presupuesto, con datos reales (acceso a BD o archivo confirmado) en mano — no tiene sentido fijar un precio ahora sobre una incertidumbre que está a punto de resolverse con información mejor.

*Referencia histórica (v2/v3 de este documento): la estimación anterior era 12h de migración base + 3h de extensión para conteo real = 15h, Tier 3 (0% descuento) + 25% de riesgo declarado = USD 394 provisional. Queda como ancla de referencia si la fase futura termina dependiendo igual de un archivo Excel; si hay acceso a base de datos, se espera un costo bastante menor.*

### Estimaciones PERT por item

M anclado en calibración histórica de `marihogar` (rubro más cercano). El módulo de código de barras quedó reducido a lo mínimo tras confirmarse que la ticketeadora es manual: solo vincular el código al producto y resolverlo en la búsqueda de venta — sin generación/impresión de etiquetas.

### Tasa vigente y contingencia aplicada

- Tasa vigente: USD 35/h. Fórmula de lista: `Costo módulo = M × $16.80`.

### Cálculo de reutilización (R) y Tier aplicable — Etapa 1 + Etapa 2

| | Horas |
|---|---:|
| Total M (Etapa 1 + Etapa 2) | 139h |
| Horas ancladas en reuse directo | 97h |
| Horas de desarrollo genuinamente nuevo | 42h |

**R = 97 / 139 = 69,8%** → **Tier 2 (40% ≤ R < 70%): 15% de descuento**, por 0,2 puntos porcentuales.

**Nota de transparencia (caso límite):** al simplificar el módulo de código de barras (7h→3h), el ratio combinado subió de 68,5% a 69,8% — a un pelo del umbral de Tier 1 (70%). Es, literalmente, un caso al límite: la clasificación reuse/nuevo de una sola hora en cualquier módulo podría inclinarlo a un lado u otro. Se aplica Tier 2 por el criterio estricto (R < 70%), pero se deja constancia de que es una zona gris, no un resultado robusto.

Gatillo económico: tablero de ciclos económicos en verde/consolidación a la fecha (2026-07-30) → Tier 2 habilitado sin restricción.

### Resumen economico (con Tokens IA como item individual) — precio según fórmula/política vigente

| Concepto | USD |
|---|---:|
| Subtotal Etapa 1 (lista, 101h × $16.80) | 1.696,80 |
| Subtotal Etapa 2 (lista, 38h × $16.80) | 638,40 |
| **Subtotal desarrollo (sin Tokens IA, sin descuento)** | **2.335,20** |
| Tokens IA (25% del subtotal de lista) | 583,80 |
| Descuento Tier 2 (15% del subtotal de lista) | −350,28 |
| **Precio real Etapa 1 + Etapa 2 (antes de referido)** | **≈ 2.568,72** |
| Descuento por referido (15%) | −385,31 |
| **Precio según fórmula/política vigente** | **≈ 2.183** |

### Precio final a cobrar — estructura de dos modalidades de pago (override comercial de Joaquín, 2026-07-30)

Joaquín definió el precio final del proyecto como **dos modalidades de pago**, ambas por debajo de los ≈USD 2.183 que da la fórmula/política estándar — no es un ajuste de la política de Tier ni del referido, es un precio de cierre puntual para este cliente, con un incentivo por pago más concentrado:

| Modalidad | Total USD | Cuotas |
|---|---:|---|
| Pago en hasta 3 pagos | **1.500** | ej. 3 × USD 500 |
| Pago en hasta 12 pagos | **1.800** | ej. 12 × USD 150 |

La diferencia entre ambas (USD 300, ≈16,7%) es el incentivo por elegir la modalidad de pago más corta — más cobro concentrado y menos riesgo de cobranza a lo largo de 12 cuotas.

Split por etapa (misma proporción de horas, 101h:38h ≈ 72,7%:27,3%) — referencia interna, no se expone al cliente con este detalle dado que ahora se cotiza como total del proyecto con modalidad de pago, no por etapa:

| Etapa | USD (si 1.500) | USD (si 1.800) |
|---|---:|---:|
| Etapa 1 | 1.090 | 1.308 |
| Etapa 2 | 410 | 492 |

### Chequeo de margen real con los números propios de Joaquín (ambas modalidades)

Joaquín estima el proyecto en **30 horas reloj reales + USD 200 de tokens IA** → piso de referencia a tasa objetivo (USD 35/h): 30×35 + 200 = **USD 1.250**.

| Concepto | Modalidad 3 pagos (1.500) | Modalidad 12 pagos (1.800) |
|---|---:|---:|
| Precio a cobrar | 1.500 | 1.800 |
| Margen sobre el piso de referencia (1.250) | 250 (≈20%) | 550 (≈30,6%) |
| Tasa efectiva realizada: (precio − 200) / 30h | **≈ USD 43,3/h** | **≈ USD 53,3/h** |

**Conclusión:** ambas modalidades quedan por encima del objetivo de USD 35/h — incluso la opción de 3 pagos (la más barata) deja margen saludable según la propia estimación de esfuerzo real de Joaquín. El incentivo por pago corto no compromete la rentabilidad del proyecto en ninguno de los dos casos.

### Total del proyecto (Etapa 1 + Etapa 2 — la migración queda fuera, se cotiza aparte más adelante)

| Modalidad | Total USD |
|---|---:|
| Hasta 3 pagos | 1.500 |
| Hasta 12 pagos | 1.800 |

*Nota histórica: la versión anterior de este documento (con ticketeadora integrada, 7h) daba Total ≈ USD 2.246 según fórmula. Con el módulo simplificado (3h) la fórmula bajaba a ≈USD 2.183; Joaquín estructuró el precio final como dos modalidades de pago (USD 1.500 / USD 1.800) en vez de un único número, con el respaldo del chequeo de margen de arriba.*

### Costo real de producción vs. precio cobrado (actualizado)

USD 200 de tokens IA reales quedan cubiertos en ambas modalidades — el chequeo relevante es el de arriba (30h reales + USD 200 tokens vs. USD 1.500 o USD 1.800 cobrados), que confirma tasas efectivas de USD 43,3/h y USD 53,3/h respectivamente, ambas saludables sobre el objetivo de USD 35/h.

### Mantenimiento anual — actualizado (2026-07-30)

Se simplifica a un único plan: **PREMIUM** desde el arranque (coherente con que el sistema completo, Etapa 1+2, supera ampliamente las 15 tablas del rango PRO). Año 1 sin costo, año 2 en adelante a precio de lista.

| Momento | Plan | USD/año |
|---|---|---:|
| Año 1 | PREMIUM | Sin costo |
| Desde año 2 | PREMIUM | 500 |

*Reemplaza la estructura anterior (PRO gratis año 1 → PREMIUM USD 500 desde Etapa 2) — ya no hay transición de plan, es PREMIUM desde el día uno, con el año 1 regalado como parte del cierre comercial.*

### Calibraciones historicas usadas

- `marihogar/definiciones/4-presupuestador.md`: fuente principal de M-hour por módulo.
- `delicias-naturales`: referencia conceptual para `UnidadMedida`.
- `ganaderia`: referencia de `CajaService`/`EgresoService`.
- `vinosefue`: referencia de `MovimientoCCProveedor`.
- `ShowroomGriffin`: referencia de `Marca`/`Modelo`, aumento masivo de precios, devoluciones de mercadería, y ajuste manual de stock.
- `contadores-bma-conversor`: referencia para cuando se cotice la migración de catálogo en su fase futura (retirada de este presupuesto).

### Cierre estimado vs real (si disponible)
Pendiente — proyecto en etapa de presupuesto, aún no iniciado.

## Historial de ajustes
- 2026-08-21: agregado presupuesto de "Código de barras múltiple por producto" — hallazgo real (4.371 artículos con más de un código de barras real, descartados hoy como ambiguos). WBS de 5 ítems, 4,5h, sin Tokens IA (bajo umbral de 4h facturables) ni descuento de Tier (merge sobre sistema ya entregado). Precio de lista ≈ **USD 76**. Pendiente de aprobación de Joaquín antes de Implementación.
- 2026-08-17 (v7): Presupuesto real de Etapa 3 (migración de catálogo) — reemplaza la referencia provisional de v2/v3 (USD 315-394, nunca cotizada en firme). WBS de 7 ítems, 27h, R=18,5% → Tier 3 (0% descuento) — coherente con ser una ampliación sobre sistema ya entregado, no un Build inicial. Precio final ≈ **USD 567** (453,60 lista + 113,40 Tokens IA). Sube frente a la referencia anterior pese a resolverse el riesgo de formato desconocido, porque el volumen real (121.691 activos) es 7x el supuesto y el alcance creció (ABC automática + extensión Producto/Cliente + reporte de excepciones). Pendiente de aprobación de Joaquín antes de Implementación — mismo gate que Entregas 1/2.
- 2026-07-30: Presupuesto interno v1 — WBS de 16 módulos (126h totales), R=73% → Tier 1, precio real de desarrollo ≈ USD 2.011.
- 2026-07-30: Aplicado 15% de descuento por referido sobre el costo real → USD 1.709.
- 2026-07-30: Analizado el consumo estimado de USD 200 en tokens IA contra el precio final — cubierto con margen por la línea de Tokens IA existente.
- 2026-07-30 (v2 — respuestas del cliente): confirmada anulación de venta facturada por NC + devoluciones sin cambios (nuevo módulo, Etapa 2); migración confirmada en ~17.000 productos, formato aún no recibido, promovida a Etapa 3 independiente (USD 315 provisional); dashboard ampliado (prioridad de diseño); confirmado punto de venta único y repartidor con visibilidad total. R de Etapa 1+2 bajó de 73% a 70,9% (Tier 1, más ajustado). Total con las 3 etapas ≈ USD 2.133.
- 2026-07-30 (v3 — plan de stock inicial): Stock ampliado (6h→8h) con ajuste manual/ABC/flag negativo, reutilizando patrón `ShowroomGriffin`; Etapa 3 sumó extensión del importador para conteo real (12h→15h). R de Etapa 1+2 bajó a 70,6% (sigue Tier 1, colchón mínimo). Total con las 3 etapas ≈ USD 2.239.
- 2026-07-30 (v4 — código de barras + retiro de la migración como etapa): (a) agregado el módulo "Código de barras — etiquetado con ticketeadora + lectura en venta" (7h, Etapa 1) — el cliente tiene ticketeadora física y códigos propios/de fábrica; (b) **retirada la migración de catálogo de este presupuesto** — el problema de stock que la motivaba ya está resuelto por el módulo de stock ampliado, y Joaquín va a evaluar acceso a la base de datos real en un segundo relevamiento antes de cotizar esa fase por separado. **Efecto combinado: R de Etapa 1+2 bajó de 70,6% a 68,5% — el proyecto pasa de Tier 1 (30%) a Tier 2 (15%)**, tal como se había advertido. Precio final actualizado: Etapa 1 ≈ USD 1.649, Etapa 2 ≈ USD 597 — **Total ≈ USD 2.246** (la migración se cotiza aparte, en una fase posterior).
- 2026-07-30 (v5 — ticketeadora manual + override de precio a USD 1.800): Joaquín aclaró que la ticketeadora es manual (no se integra) — el módulo de código de barras baja de 7h a 3h (solo vinculación + lookup en venta, sin etiquetado). Esto sube el R de Etapa 1+2 a 69,8% (caso límite, a 0,2 puntos de Tier 1, se mantiene Tier 2 por criterio estricto). El precio según fórmula/política queda en ≈USD 2.183. **Joaquín fijó el precio final a cobrar en USD 1.800** (override comercial directo, ≈17,5% por debajo de la fórmula) — Etapa 1 ≈ USD 1.308, Etapa 2 ≈ USD 492. Chequeo de margen con sus propios números (30h reales + USD 200 tokens IA): tasa efectiva realizada ≈USD 53,3/h, por encima del objetivo de USD 35/h — el override no compromete la rentabilidad esperada.
- 2026-07-30 (v6 — estructura final de pago + mantenimiento): Joaquín reestructuró el precio final como dos modalidades de pago del total del proyecto (ya no por etapa): **USD 1.500 en hasta 3 pagos**, o **USD 1.800 en hasta 12 pagos**. Chequeo de margen con sus propios números confirma que ambas modalidades quedan por encima del objetivo de USD 35/h (≈USD 43,3/h y ≈USD 53,3/h respectivamente). Mantenimiento simplificado a un único plan **PREMIUM** desde el arranque (año 1 gratis, USD 500/año desde el año 2) — reemplaza la transición PRO→PREMIUM de versiones anteriores.
