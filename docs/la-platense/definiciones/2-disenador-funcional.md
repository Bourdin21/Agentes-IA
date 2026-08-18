# Memoria - Disenador funcional

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-08-17 (v6 — flujo 10: migracion de catalogo Etapa 3, retomado con datos reales + clasificacion ABC automatica)

## Definiciones vigentes

### Historias de usuario

Ver `1-analista-funcional.md` §"Criterios de aceptacion vigentes" (PF1-PF8). Se agregan acá los flujos de pantalla que las soportan.

### Flujos de pantalla acordados

**1. Unidades de medida y conversión compra↔venta**
- Alta/edición de producto: campo `UnidadVenta` (Unidad / Peso(Kg) / Metro / Bulto). Si el producto se compra en una unidad distinta a la que se vende, se activa `UnidadCompra` + `FactorConversion` (ej. `UnidadCompra=Bulto`, `FactorConversion=100` → 1 bulto = 100 unidades de venta).
- Pantalla de Compra: el usuario carga cantidad en `UnidadCompra`; el sistema muestra en tiempo real el equivalente en `UnidadVenta` que impactará en stock, antes de confirmar.
- Pantalla de Venta: el ítem se carga siempre en `UnidadVenta` (stock se mantiene en la unidad más granular).
- *Hipótesis a validar con el cliente: el factor de conversión es fijo por producto (no varía de una compra a otra). Si un mismo producto viene en bultos de distinto tamaño según el proveedor, el modelo necesita revisarse antes de implementar.*

**2. Venta editable — workflow Borrador → Facturada**
- **1. Iniciar venta.** El vendedor abre "Venta rápida", agrega productos (unidad, cantidad, precio unitario editable, % IVA editable, descuento/recargo por ítem). La venta queda en estado `Borrador`.
- **2. Cargar pago(s).** Se pueden cargar uno o varios pagos (efectivo, tarjeta débito, tarjeta crédito 3/6 cuotas con recargo, cuenta corriente/fiado). El sistema calcula el recargo de cuotas según la configuración vigente y lo suma al total antes de confirmar.
- **3. Revisar antes de facturar.** Mientras la venta está en `Borrador`, el vendedor puede volver a editar cualquier ítem, cantidad, precio o IVA.
- **4. Emitir comprobante AFIP.** El vendedor elige cliente cargado o "Consumidor final" y emite. La venta pasa a `Facturada` y deja de ser editable.

| Estado | Editable | Acción disponible |
|---|---|---|
| Borrador | Sí (ítems, precios, IVA, pagos) | Editar, cancelar, emitir comprobante |
| Facturada | No | Consultar, anular/NC (si el cliente confirma que aplica — ver pregunta abierta en Analisis) |

*Hipótesis a validar: si una venta en Borrador ya tiene pagos cargados y se edita el total, el saldo pendiente se recalcula automáticamente — a confirmar con el cliente antes de implementar la regla de recálculo.*

**Casos especiales contemplados:**
- Venta con pago mixto (parte efectivo + parte tarjeta + parte cuenta corriente).
- Venta a "Consumidor final" sin cliente cargado (no genera movimiento de cuenta corriente).
- Venta con ítems de distintas unidades de medida en el mismo comprobante.

**3. Importación de lista de precios de proveedor**
- **1. Configurar proveedor.** El admin carga el TC propio del proveedor y su % de descuento particular, una sola vez (editable cuando cambien).
- **2. Subir archivo.** El admin sube el Excel de lista de precios del proveedor.
- **3. Previsualizar.** El sistema muestra una grilla de preview con el precio recalculado (`precio_lista_USD × TC_propio × (1 − %descuento)`) antes de aplicar nada.
- **4. Confirmar.** Al confirmar, se actualizan los precios de compra de los productos vinculados a ese proveedor.

*Hipótesis a validar: el formato de Excel de cada proveedor no es estándar — el mapeo de columnas puede necesitar configuración por proveedor. Se define con el archivo real en mano, no antes.*

**4. Cuenta corriente de empleados (autoservicio)**
- El admin carga pagos de sueldo y retiros/gastos del empleado desde su panel de administración.
- El empleado, al ingresar con su usuario, ve únicamente su propia cuenta corriente (sueldo pagado, retiros) — no ve la de otros empleados, ni accede a reportes generales de caja/negocio.

**5. Anulación de venta facturada + devolución de mercadería (NUEVO — confirmado por el cliente 2026-07-30)**
- **1. Iniciar anulación.** Desde una venta en estado `Facturada`, el admin (a confirmar si también el vendedor, ver pregunta abierta en Analisis) inicia la anulación.
- **2. Registrar devolución (si aplica).** Si hay mercadería física que vuelve, se carga la devolución: producto, cantidad, motivo. El stock se reingresa automáticamente.
- **3. Emitir nota de crédito AFIP.** El sistema emite la NC vinculada al comprobante original (mismo circuito WSAA/WSFE ya resuelto para facturas).
- **4. Cerrar el ciclo.** La venta pasa a estado `Anulada`; si había saldo en cuenta corriente del cliente, se ajusta.

*Hipótesis a validar con el cliente (pregunta abierta): si la anulación la puede iniciar cualquier vendedor o solo el admin, y si existe un límite de tiempo (ej. solo el mismo día de la venta).*

**Casos especiales contemplados:**
- Devolución parcial (algunos ítems de la venta, no todos).
- Venta con pago ya cobrado: la NC ajusta el saldo, no genera un reintegro de efectivo automático (eso se resuelve operativamente, fuera del sistema).
- No existe flujo de "cambio" (canje por otro producto) — confirmado, siempre es devolución simple.

**6. Dashboard — "foto completa del negocio" (pantalla de mayor prioridad de diseño)**

El cliente confirmó que esta es la pantalla más importante del sistema y pidió priorizar diseño y estructura por sobre el resto. Enfoque propuesto:
- **Jerarquía en 3 niveles**, no una grilla plana de tarjetas sueltas: (1) estado del día (ventas de hoy, caja del día, entregas pendientes), (2) salud financiera (cobros pendientes de clientes, pagos pendientes a proveedores, saldo de caja consolidado), (3) tendencias (gastos del mes por categoría, top productos, stock crítico).
- Cada bloque debe poder navegarse hacia el detalle correspondiente (ej. click en "cobros pendientes" lleva al listado de clientes con saldo).
- *Antes de construir el detalle final, se recomienda una sesión de diseño dedicada con el cliente para priorizar qué KPIs van en el "primer vistazo" (nivel 1) — evitar construir un dashboard con demasiada información sin jerarquía clara, que es el riesgo típico de un pedido de "foto completa".*

**7. Migración de catálogo — POSPUESTA, fuera de este alcance**

Se retira este flujo del diseño actual. Se cotiza y diseña en una fase posterior, cuando se confirme si hay acceso directo a la base de datos del sistema actual (segundo relevamiento) o si sigue siendo por archivo Excel — el diseño del importador (mapeo configurable, preview, carga por lotes) queda como referencia para esa fase futura, no se construye ahora.

**8. Puesta a punto de stock inicial (plan ABC + arranque suave) — vigente, independiente de la migración**
- **1. Clasificar (fuera del sistema, lo hace el cliente).** El cliente marca en el catálogo qué productos son "A" (mayor rotación/valor) usando el campo de clasificación ABC — no requiere sesión con Olvidata, es una decisión de negocio propia.
- **2. Contar los "A" y cargarlos con stock real.** Vía alta o edición manual de stock (ya no depende de un importador de migración, dado que esa etapa se pospuso).
- **3. El resto arranca en 0/sin verificar.** El sistema permite vender con stock negativo para estos productos (aviso visual, no bloqueo).
- **4. Ajustar sobre la marcha.** Pantalla de "ajuste de stock" (producto, cantidad, motivo) disponible para el rol autorizado — reutiliza patrón de `ShowroomGriffin`.

*Casos especiales contemplados:*
- Producto con stock negativo: la venta se permite pero queda marcado visualmente en el listado de stock hasta que se ajuste.
- El "conteo cíclico" (revisar una categoría por semana) es un hábito operativo del cliente, no una pantalla nueva — se apoya en el mismo "ajuste de stock" del punto 4.

**9. Código de barras — vinculación al producto + lectura en venta (SIMPLIFICADO — la ticketeadora es manual, no se integra)**
- **1. Vincular código.** Al cargar/editar un producto, se ingresa su código de barras (de fábrica, si lo tiene, o el que el cliente le asignó con su ticketeadora manual) — campo único en el catálogo. El sistema no genera ni imprime nada; el etiquetado físico lo sigue haciendo el cliente por su cuenta.
- **2. Escanear en la venta.** En la pantalla de venta, un campo con foco detecta el código escaneado (el lector USB actúa como teclado) y agrega el producto automáticamente al carrito, sin necesidad de buscarlo.

**Casos especiales contemplados:**
- Producto sin código de fábrica: el cliente le asigna uno propio con su ticketeadora manual, y lo carga en el sistema — sin distinción funcional para el resto del sistema (venta, stock, etc.) respecto de un código de fábrica.

**10. Migración de catálogo (Etapa 3) — retomada 2026-08-17 con acceso real a la base del sistema actual**

Base: `1-analista-funcional.md` sección "Etapa 3 — Migración de catálogo" (análisis completo con datos reales: 121.691 artículos activos, reglas de barrido/deduplicación, fuente de ventas confirmada `VentaItem`/`Operacion`).

- **1. Extracción y limpieza (batch, sin UI — corre una vez, antes del import a producción).** Sobre una copia del backup del cliente (no se conecta en vivo a su sistema):
  1. Excluir `Articulo` con `Activo=0`, `Nombre` vacío, o `PrecioVenta=0`.
  2. Resolver duplicados de nombre (grupos con >1 activo): conservar el de venta más reciente en `VentaItem`/`Operacion`; si ninguno vendió, el de `FechaModificacionPrecio` más reciente (ver regla final en `1-analista-funcional.md`).
  3. Resolver `articuloProveedor` (58,8M filas históricas): tomar por `(ProveedorKey, CodigoProv)` solo la fila del `IngresoKey` más reciente con `Procesado=1` y `ArticuloKey IS NOT NULL` → construye `CodigoProveedorProducto` limpio.
  4. Resolver código de barras (`Codigo`) compartido por más de un artículo: preferir el vínculo hacia el artículo que sobrevivió la deduplicación del punto 2; si dos artículos "ganadores" comparten el mismo código de barras, es inconsistencia real de datos → generar en un reporte de excepciones, no bloquea el resto del import.
  5. Calcular clasificación ABC inicial por artículo: Pareto 80/95 sobre cantidad vendida en `VentaItem` de los últimos 12 meses (relativo a la fecha del backup) — el resto (sin venta en la ventana) arranca en "C" sin verificar, mismo criterio que la puesta a punto de stock de Entrega 1.
  6. Generar un **reporte de excepciones** (no un bloqueo): artículos sin `Rubro` válido (asignados a categoría "Sin categoría" por defecto), códigos de barra en conflicto sin resolver, grupos de duplicados sin ningún ganador claro.
  - Resultado de este paso: un dataset limpio listo para cargar Producto/CodigoProveedorProducto/Cliente en el sistema nuevo.
- **2. Carga al sistema nuevo — CORREGIDO 2026-08-17: por script directo, no por pantalla web.** Joaquín decidió que, al ser una carga de una sola vez, no tiene sentido pasar por un flujo de subida de archivo + preview + confirmar en la app — se hace con un script que escribe directo en la base (reutilizando las entidades `Producto`/`CodigoProveedorProducto`/`Cliente`/`Proveedor` ya definidas). **Se retira `ICatalogoMigracionService`/`MigracionCatalogoController` y las vistas asociadas, ya implementadas — no se usan.** Esto es exclusivo de la migración histórica: la futura importación de listas de precios de proveedor (flujo 3, recurrente, la sigue operando el personal de La Platense) sigue siendo por archivo vía pantalla, son necesidades distintas — no se confunde una con la otra.
- **3. Clasificación ABC automática — ida y vuelta con el criterio manual ya existente (Entrega 1).** El campo `Producto.ClasificacionABC` (ya editable a mano desde Entrega 1) pasa a tener además un cálculo automático sugerido:
  - Job/acción manual "Recalcular clasificación ABC" (no en tiempo real por venta — se recalcula por lote, ej. mensual o a demanda desde una pantalla de administración) que recorre `ItemVenta` de los últimos 12 meses (ventana móvil, no todo el histórico) y aplica el mismo criterio Pareto 80/95 documentado en el análisis.
  - El resultado se guarda como **sugerencia** — el campo sigue siendo editable a mano por el cliente en cualquier momento (no contradice R10/analisis v1: "la clasificación la hace el cliente por su cuenta"). La pantalla de Producto/Catálogo muestra el valor sugerido junto al valor vigente si son distintos, con un botón para aceptar la sugerencia.

**Casos especiales contemplados:**
- Producto nuevo (sin historial de venta, dado de alta después de la migración): sin sugerencia ABC hasta que acumule ventas — el campo queda en blanco/"C" por defecto, editable a mano igual que hoy.
- Reimportación / segunda corrida del paso 1 (ej. el cliente pide corregir algo después de la primera migración): el proceso debe ser idempotente sobre `CodigoProveedorProducto` (actualizar, no duplicar, si el `Producto` ya fue migrado antes).

### ViewModels definidos

- `ProductoFormViewModel`: incluye `UnidadVenta`, `UnidadCompra` (nullable), `FactorConversion` (nullable), `PrecioCompra`, `PrecioVenta`, `PrecioConDescuento`, `PorcentajeIVA`, `MarcaId`, `ModeloId`, `CategoriaId`.
- `VentaEditableViewModel`: lista de `ItemVentaViewModel` (producto, cantidad en `UnidadVenta`, precio unitario editable, %IVA editable, subtotal calculado), lista de `PagoViewModel` (medio de pago, monto, cuotas si aplica, % recargo aplicado), estado (`Borrador`/`Facturada`), cliente (cargado o consumidor final).
- `ImportacionListaProveedorViewModel`: proveedor, archivo, `TCPropio`, `PorcentajeDescuento`, grilla de preview (producto detectado, precio original, precio recalculado, acción: crear/actualizar/omitir).
- `CuentaCorrienteEmpleadoViewModel`: solo lectura para el empleado — movimientos (fecha, tipo: sueldo/retiro/gasto, monto, saldo).
- `AnulacionVentaViewModel`: venta original, ítems a devolver (parcial o total), motivo, preview de la NC antes de emitir.
- `DashboardViewModel`: 3 niveles (estado del día, salud financiera, tendencias) — ver flujo 6.
- `AjusteStockViewModel`: producto, cantidad actual, cantidad nueva, motivo — genera registro auditado.
- `VentaEditableViewModel` (extendido): campo de escaneo de código de barras que agrega un `ItemVentaViewModel` automáticamente al detectar un código válido.
- ~~`ImportacionCatalogoMigracionViewModel`~~ / ~~`ReporteExcepcionesMigracionViewModel`~~ — **retirados 2026-08-17** junto con `ICatalogoMigracionService` (ver arriba).
- `RecalculoClasificacionAbcViewModel` (Etapa 3): parámetro de ventana en meses (default 12) para la acción manual "Recalcular clasificación ABC".
- `ProductoFormViewModel` (extendido, Etapa 3): agrega `Bonificacion` (texto libre tipo `"33+5"`, ver gap confirmado en Análisis) y `ClasificacionABCSugerida` (solo lectura, junto al `ClasificacionABC` editable ya existente).
- `ClienteFormViewModel` (extendido, Etapa 3): agrega `Domicilio`, `Localidad`, `Email`, `Notas` (campos confirmados como gap en Análisis).

### Validaciones de UI acordadas

- No permitir emitir comprobante AFIP si la venta no tiene al menos un ítem y el total de pagos no cubre el total (salvo venta a cuenta corriente/fiado, donde el saldo pendiente es intencional).
- No permitir guardar un producto con `UnidadCompra != UnidadVenta` sin `FactorConversion` > 0.
- No permitir confirmar importación de lista de proveedor sin revisar el preview.
- Bloquear a nivel de autorización (no solo de UI) el acceso de un empleado a la cuenta corriente de otro.
- No permitir confirmar la importación de migración de catálogo (Etapa 3) sin haber revisado el conteo del reporte de excepciones (no bloquea el import, pero exige que el usuario haya abierto/visto el reporte antes de confirmar).
- El botón "Aceptar sugerencia" de clasificación ABC automática nunca sobrescribe el valor manual sin una acción explícita del usuario — el cálculo por lote solo actualiza el campo `ClasificacionABCSugerida`, nunca `ClasificacionABC` directamente.

### Logica de distribucion de elementos en pantalla
- priorizar simplicidad visual y comprension inmediata del flujo
- ubicar primero informacion y acciones criticas; dejar secundario en segundo plano
- mantener jerarquia consistente (titulo, contexto, formulario, acciones)
- reducir ruido visual: evitar bloques redundantes y opciones duplicadas
- reutilizar este criterio de distribucion en todas las pantallas del sistema
- Listados (Catálogo, Ventas, Compras, Cuentas corrientes) con DataTable — columnas visibles = filtros disponibles (criterio estándar del estudio).

### Contratos funcionales para Services

- `IUnidadMedidaConversionService`: calcula equivalencia compra↔venta dado un producto y una cantidad en unidad de compra.
- `IVentaWorkflowService`: gestiona transición Borrador→Facturada, valida reglas de edición según estado.
- `IRecargoCuotasService`: calcula el recargo aplicable según medio de pago y cantidad de cuotas configurada.
- `IListaPreciosProveedorImportService`: parsea el archivo del proveedor, aplica TC propio + % descuento, devuelve preview antes de persistir.
- `ICuentaCorrienteEmpleadoService`: expone movimientos de UN empleado, validando que el usuario autenticado sea el dueño de la cuenta o el admin.
- `IAnulacionVentaService`: valida que la venta esté en estado `Facturada`, coordina devolución de stock + emisión de NC + transición a `Anulada`.
- `IAjusteStockService`: aplica una corrección manual de stock con motivo, genera auditoría (usuario, fecha, valor anterior/nuevo).
- `ICodigoBarrasLookupService`: resuelve un producto a partir de un código escaneado (propio o de fábrica) para el flujo de venta.
- ~~`ICatalogoMigracionService`~~ — **retirado 2026-08-17**: la carga del catálogo histórico va por script directo a la base, no por un Service de la app (ver flujo 10, paso 2, corrección de Joaquín).
- `IClasificacionAbcAutomaticaService` (Etapa 3): recalcula por lote la clasificación ABC sugerida de todos los productos sobre una ventana móvil de ventas (12 meses configurable), usando Pareto 80/95 por cantidad vendida en `ItemVenta` — nunca escribe el campo manual `ClasificacionABC` directo, solo `ClasificacionABCSugerida`. Se mantiene — es una funcionalidad permanente del sistema (recalculable en cualquier momento), no exclusiva de la migración.

## Historial de ajustes
- 2026-07-30: Diseño v1 — flujos de venta editable, conversión de unidades, importación de listas de proveedor y cuenta corriente de empleados definidos como los cuatro flujos no triviales del sistema.
- 2026-07-30 (v2): agregados 2 flujos nuevos tras respuestas del cliente — anulación de venta facturada + devolución de mercadería (con NC AFIP), y migración de catálogo (Etapa 3, 17.000 productos, mapeo configurable por lote). Dashboard rediseñado como pantalla de 3 niveles jerárquicos (día / salud financiera / tendencias), marcado como prioridad de diseño explícita del cliente — se recomienda sesión de diseño dedicada antes de cerrar el detalle final.
- 2026-07-30 (v3): agregado el flujo de puesta a punto de stock inicial (clasificación ABC + conteo focalizado + arranque suave con stock negativo permitido + ajuste manual auditado) — responde al problema real del cliente de no tener stock confiable hoy por la rotación de artículos.
- 2026-07-30 (v4): agregado el flujo de código de barras (etiquetado con ticketeadora + escaneo en venta). Retirado el flujo de migración de catálogo (pospuesto, se cotiza en una fase posterior) — el flujo de puesta a punto de stock inicial queda independiente de la migración.
- 2026-07-30 (v5): simplificado el flujo de código de barras — la ticketeadora es manual (no se integra con el sistema); se retira la generación/impresión de etiquetas, queda solo la vinculación del código al producto y la lectura en venta.
- 2026-08-17 (v6): retomado el flujo de migración de catálogo (Etapa 3, flujo 10) con datos reales del sistema actual (ver `1-analista-funcional.md`). Diseñado en 2 pasos: (1) extracción/limpieza batch sin UI (excluye inactivos/sin nombre/precio cero, dedup por venta más reciente o fecha de modificación, dedup de `articuloProveedor` por última importación procesada+matcheada, ABC inicial por Pareto 12 meses) y (2) importación con UI reutilizando el patrón preview→confirmar ya usado para listas de proveedor. Agregado el mecanismo de clasificación ABC automática por lote como sugerencia editable, sin reemplazar el campo manual ya existente de Entrega 1 (no contradice R10). Agregados los ViewModels `ImportacionCatalogoMigracionViewModel`, `ReporteExcepcionesMigracionViewModel`, y extendidos `ProductoFormViewModel`/`ClienteFormViewModel` con los gaps confirmados (bonificación compuesta, campos de Cliente, ABC sugerida).
