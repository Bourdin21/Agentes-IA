# Memoria - Analista funcional

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-08-17 (v3 — arranque de Analisis de Etapa 3: Migracion de catalogo, segundo relevamiento con acceso real a la base de datos del sistema actual)

## Etapa 3 — Migración de catálogo (arranque de Análisis, 2026-08-17)

### Contexto y método
Joaquín trajo el segundo relevamiento prometido en el cierre de Presupuesto (ver `4-presupuestador.md` y `trazabilidad.md` 2026-07-30): en vez de un archivo Excel de formato desconocido, trajo (a) el **backup completo de SQL Server** del sistema de gestión que usa La Platense hoy (`Migracion/LaPlatense_backup_2026_08_14_140001_1971951.bak`, 17,35 GB) y (b) dos listas de precios de proveedor de ejemplo. El análisis se hizo restaurando el backup real (no una muestra) en una instancia local de SQL Server 2022 Developer — hubo que instalarla porque las instancias Express ya presentes en la máquina tienen un límite de 10 GB por base y esta base pesa 17 GB — y consultando el esquema y los datos reales.

### Tamaño real del catálogo (corrige un supuesto anterior)
`Articulo`: **142.227 filas totales, 121.691 con `Activo=1`**. Esto es **~7 veces más** que el "~17.000 productos" estimado en el análisis original (v1/v2, antes de tener acceso a datos reales) y usado como referencia en `4-presupuestador.md`/`3-arquitecto-mvc.md` para la migración pospuesta. No cambia el presupuesto ya aprobado de Entregas 1/2 (no incluían migración), pero es el primer dato duro para cotizar la Etapa 3 y hay que dejarlo explícito antes de estimarla — cotizar sobre "17.000" sería un error de base.

### Las dos listas de proveedor confirman la hipótesis de Joaquín (código de proveedor no es un identificador único global)
- `CopiaListaa (6).10386.xlsx` (D'Accord/genérico): 6.459 artículos, columnas `Codigo|Producto|REF|Costo|Sugerido`, código numérico secuencial simple.
- `CopiaSibonListaPrecios (1)10387.XLS` (Sibon): 5.834 artículos, columnas `Código|Descripción|Costo|...`, código alfanumérico con guion (`0099-51`).
- **No hay ninguna columna compartida entre ambos archivos** — cada proveedor tiene su propio esquema de código, sin relación entre sí. Confirma que el modelo correcto es una entidad de mapeo `CodigoProveedorProducto` (`ProductoId + ProveedorId + CodigoDelProveedor`), no un campo único de código externo en `Producto`.
- El sistema actual del cliente **ya resuelve esto exactamente así**: la tabla `Codigo` (157.564 filas: `CodigoKey, Codigo, ProductoKey, ArticuloKey, IdentificaVariante, Tipo, ProveedorKey, Proveedor`) es un mapeo de códigos múltiples por artículo, incluyendo código de proveedor vía `ProveedorKey`+`Tipo`. Confirma el diseño propuesto — no es una idea nueva, es replicar un patrón que el cliente ya usa y entiende.

### El "barrido" que pidió Joaquín es un problema real y medible, no preventivo
La tabla `articuloProveedor` (58.866.462 filas) es el **log histórico completo de cada import de lista de proveedor** hecho alguna vez en el sistema, no una tabla de mapeo limpia:
- **10.013 importaciones distintas (`IngresoKey`) sobre solo 54 proveedores** — algunos proveedores fueron re-importados centenares de veces (actualizaciones de precio semanales/mensuales durante años, ver `IngresoArchivo` con importaciones casi diarias hasta la fecha actual).
- **28.932.519 filas (49% del total) no tienen `ArticuloKey` asociado** — casi la mitad de todo lo importado históricamente nunca se conciliació contra un artículo real. Confirma que hace falta una regla de deduplicación/limpieza explícita antes de migrar, no es un riesgo teórico.
- **Regla de importación propuesta para Etapa 3**: para construir el `CodigoProveedorProducto` limpio, tomar por cada `(ProveedorKey, CodigoProv)` únicamente la fila del **`IngresoKey` más reciente** con `Procesado=1` y `ArticuloKey IS NOT NULL` — descartar el resto del historial (queda en el backup, no hace falta migrarlo).
- El sistema actual **ya tiene** un motor de importación configurable por proveedor (`PCArchivo`/`PCArchivoCampo`/`PCTipoDato`/`PCFormatoArchivo`): un perfil por proveedor con delimitador, línea del primer artículo, mapeo columna→campo y hasta una función de transformación por campo. Confirma la hipótesis ya documentada en `2-disenador-funcional.md` ("el mapeo de columnas puede necesitar configuración por proveedor") — es un patrón a replicar conceptualmente en `IListaPreciosProveedorImportService`, no una sorpresa.

### Datos sucios/obsoletos encontrados (evidencia concreta del "barrido" pedido)
- `Rubro` (219 filas) es jerárquico (`PadreRubroKey`) pero con datos inconsistentes: hay un rubro sin nombre (`RubroKey=1`, `Nombre=''`), y categorías con nombre de rubro "real" (ej. `pinturas`) anidadas bajo un padre que no es de primer nivel (`PadreRubroKey=189`) — la jerarquía no está limpia, necesita revisión antes de mapear a nuestra `Categoria`.
- `ListaPrecios` tiene una lista llamada literalmente **"NO SE USA"** (activa) y **dos filas "LISTA PROVISORIA"** (una activa, una inactiva, mismo nombre) — ejemplo directo de basura acumulada a excluir del import.
- `Articulo.VarianteKey`: **0 de 142.227 artículos lo usan** — el sistema tiene un subsistema de variantes de producto (`SistemaVariantesKey`/`VarianteKey`/`ProductoKey`) pero está completamente sin adoptar en la práctica. **No hace falta modelar variantes de producto para la migración ni para el sistema nuevo** — es superficie de esquema muerta.

### Gaps funcionales reales detectados (existen en el sistema actual, no están cubiertos en nuestro diseño de Entrega 1/2 — a decidir con Joaquín si entran a alcance)
1. **Multi-moneda por producto**: `Moneda` (5 filas: Pesos, Dólares, y 3 monedas "nombradas" que en realidad son tipos de cambio específicos por proveedor — ej. "Dolar lusqtoff" con su propia `EquivalenciaPesos`, no una divisa real) — **2.070 artículos** (de 142.227) están precificados en una moneda distinta de Pesos. Es real pero chico en proporción (~1,5%). Nuestro `Producto` actual no tiene campo de moneda.
2. **Precio de oferta con vigencia**: `Articulo.PrecioOferta`/`EnOferta`/`DuracionOferta`/`DuracionOfertaHasta` — un mecanismo de precio promocional temporal por producto. No existe en nuestro `Producto`.
3. **Bonificación compuesta**: `Articulo.Bonificacion` como texto libre tipo `"33+5"` (bonificaciones encadenadas, ver también la foto del sistema actual que Joaquín mandó: `Bonificaciones 33+5 → 36,35%`) — no es un único `%` sino una cadena de descuentos sucesivos. Nuestro modelo solo tiene un `PorcentajeDescuento` simple.
4. **Listas de precios múltiples por forma de pago/tarjeta** (`ListaPrecios`, 11 filas activas: "AHORA 12 VISA/MASTER/AMEX" +32%, "AHORA 3" +11%, "AHORA 6" +20%, "4 CUOTAS NARANJA VISA" +25%, "CONTADO-DEBITO-CREDITO EN 1 PAGO" +5%) — esto es **más rico que lo que implementamos en Entrega 2** (`RecargoCuotasService` hoy es un diccionario simple `cantidadCuotas→%` en `appsettings.json`). El sistema real tiene planes de cuotas con nombre específico por programa bancario (Ahora 12/3/6, Naranja), no solo por cantidad de cuotas — **y además** una tabla separada `PlanCuotas` (cuotas 2-12 a 3%/cuota flat) que parece ser el mecanismo genérico simple. Conviven ambos. **Pregunta abierta para Joaquín**: ¿cuál de los dos mecanismos quiere conservar — planes con nombre por tarjeta/programa (más fiel a lo real) o el simple por cantidad de cuotas que ya implementamos?
5. **Límite de crédito por cuenta corriente**: `Cuenta.MaximoCredito`/`MaximoNoCobrado` — tope de saldo antes de bloquear/advertir. No está en nuestro `MovimientoCCCliente`/`MovimientoCCProveedor` de Entrega 2.
6. **Cliente — campos ausentes en nuestro modelo actual**: domicilio, localidad, email, notas, lista de precios asignada por cliente (`Cliente.ListaPreciosKey` — un cliente puede tener asignada una de las 11 listas de precios, ej. mayorista), `PorcentajeDescuento` propio del cliente, vendedor asignado + comisión (`VendedorKey`/`PorcentajeVendedor`), tipo/número de documento.
7. **Categoría (Rubro) con recargo/bonificación propios y jerarquía real** (padre/hijo) — nuestra `Categoria` de Entrega 1 es plana y sin reglas de precio asociadas.
8. **Existen dos tablas de clientes y dos de ventas en paralelo** (`Cliente`/`Cuenta` vs `tblClientes`; `Operacion`/`OperacionVenta` vs `tblVentas`/`tblDetalleVentas`) — **no asumir que las `tbl*` son legacy muerto**: `tblVentas` tiene registros hasta 2026-08-14 (hoy), en paralelo con `Operacion` (que arranca en 2002). Pregunta abierta para Joaquín: para qué se usa cada circuito hoy, antes de decidir de cuál migrar.

### Cobertura ya construida sin gaps detectados
`Producto.unidadVenta` (enum) es más simple que `Articulo.UnidadKey`/`UnidadStockKey` + `CantidadUnidad`/`CantidadUnidadStock` del sistema actual, pero cubre el mismo caso de uso (conversión compra↔venta) — solo 7 `Unidad` distintas en los datos reales (Metro, Unidad, Litros, Kilogramos, Pares, Escalones, "24 Unida"), manejable con el enum ya definido más un ajuste si aparece alguna unidad no contemplada. `Rubro`/`Marca`/`Proveedor` ya tienen equivalente 1:1 en nuestro diseño (`Categoria`/`Marca`/`Proveedor`).

### Decisiones de Joaquín sobre los gaps (2026-08-17, cierran el Análisis de Etapa 3)

1. **Recargo por forma de pago/tarjeta**: se conserva el modelo real del sistema actual — **planes con nombre por programa** (AHORA 12, AHORA 3, AHORA 6, 4 Cuotas Naranja, etc., cada uno con su % propio administrable), no el simple "cantidad de cuotas → %" que se implementó en Entrega 2 como `RecargoCuotasSettings` (appsettings). **Pendiente para Diseño de Etapa 3**: modelar una entidad `PlanDePago`/`ListaDeRecargo` (nombre, % recargo, activo) reemplazando o extendiendo `RecargoCuotasService` de Entrega 2 — es una ampliación sobre módulo ya entregado, no alcance nuevo desde cero.
2. **Gaps a incluir en el alcance de Etapa 3**:
   - ✅ **Bonificación compuesta** (tipo `"33+5"`, descuentos encadenados) — entra al alcance.
   - ✅ **Campos de Cliente faltantes** (domicilio, localidad, email, notas, vendedor asignado, lista de precios propia) — entra al alcance.
   - ⏸️ **Precio de oferta con vigencia** — **NO entra ahora**, Joaquín pidió dejarlo documentado para una implementación futura (no es parte de Etapa 3). Ver `3-arquitecto-mvc.md` cuando se diseñe, para no perder el registro.
   - ⏸️ **Multi-moneda por producto** — confirmado NO entra a Etapa 3. Queda documentado para una fase futura, mismo criterio que el precio de oferta con vigencia.
   - ⏸️ **Límite de crédito en cuenta corriente** (clientes y proveedores) — confirmado NO entra a Etapa 3. Queda documentado para una fase futura.
3. **Doble circuito Cliente/Venta — RESUELTO (corrige la primera respuesta de Joaquín).** Primera ronda (2026-08-17 ~12:45): Joaquín dijo que `tblClientes`/`tblVentas`/`tblDetalleVentas` era el circuito activo. Al analizar los datos para la clasificación ABC se encontró que `tblDetalleVentas.Codigo` está vacío en el 100% de sus filas (no vincula ninguna línea de venta a ningún artículo) — ante esa evidencia, Joaquín corrigió: **el circuito correcto es `VentaItem`/`Operacion`/`OperacionVenta`**, no `tblVentas`/`tblDetalleVentas`. Queda como fuente de verdad para: (a) la clasificación ABC automática (ya calculada sobre esta fuente, ver sección siguiente), y (b) la migración de catálogo de clientes e historial de ventas/CC de Etapa 3 — debe salir de `Cliente`/`Cuenta`/`Operacion`/`OperacionVenta`/`VentaItem`, no de `tblClientes`/`tblVentas`. La discrepancia de volumen (`OperacionVenta` 74.317 filas 2002-2026 vs `tblVentas` 4.279 filas 2022-2026) queda sin explicación puntual pero ya no bloquea nada — se usa la fuente confirmada.

### Barrido de duplicados y productos inútiles (2026-08-17, pedido explícito de Joaquín)

Análisis cuantitativo real sobre los 121.691 artículos activos (142.227 totales) de `Articulo`, ejecutado contra la base restaurada.

**Nombres duplicados — 5.794 grupos, 13.353 filas excedentes.** Desglose por qué tan automatizable es cada caso:
- **1.014 grupos (17.700 filas aprox.) con todos los miembros inactivos** → descartables automáticamente sin revisión, ya están marcados `Activo=0`.
- **1.167 grupos con exactamente 1 miembro activo** → auto-resoluble: se conserva el activo, se descartan los inactivos del grupo.
- **3.612 grupos (el 62% de los duplicados) con MÁS DE UN miembro activo compartiendo el mismo nombre** → **no son auto-resolubles por nombre solo** — requieren revisión humana o un criterio adicional (comparar Rubro/Marca/Proveedor/última fecha de modificación para elegir cuál conservar). Es el núcleo real del "barrido" que pidió Joaquín — no es un detalle menor, es la mayoría del trabajo de deduplicación.
- **Caso aparte, mayor prioridad**: 3.204 artículos tienen **nombre vacío**, y de esos **3.203 están marcados `Activo=1`** — no los filtra la regla simple "excluir inactivos". Regla propuesta: excluir siempre por nombre vacío, sin importar el flag `Activo`.

**Otros duplicados/inconsistencias de identificador:**
- `Articulo.Codigo` (código propio) duplicado entre artículos distintos: solo 20 grupos / 21 filas — volumen bajo, revisión manual viable.
- Código de barras (tabla `Codigo`) compartido por más de un `ArticuloKey`: **16.258 códigos** (de 157.564) — ~10% de los códigos de barras son ambiguos. Regla propuesta: si el código está compartido, preferir el mapeo hacia el `Articulo` con `Activo=1`; si hay más de un activo con el mismo código de barras, es un problema real de datos a resolver manualmente antes de dar de alta el código único en el sistema nuevo (nuestro modelo asume código de barras único por producto, ver Entrega 1).

**"Productos inútiles" — candidatos concretos a no importar:**
| Criterio | Cantidad | Acción propuesta |
|---|---:|---|
| `Activo = 0` | 20.536 | No importar (default) |
| Nombre vacío (con o sin `Activo=1`) | 3.204 | No importar siempre |
| `PrecioVenta = 0` | 4.615 | Flag para revisión — no importar sin precio válido |
| Sin `Rubro` válido (nulo o nombre vacío) | 37 | Asignar a categoría "Sin categoría" en vez de bloquear el import |
| Activos sin ninguna venta registrada jamás (`VentaItem`) | 107.390 de 121.691 (88%) | **No excluir** — es candidato natural a clasificación ABC "C" (bajo/nulo movimiento), no basura. Ver siguiente sección. |
| Stock actual (`Stock.CantidadStock`) | 121.690 de 121.691 activos en 0 o negativo | Confirma (no solo anecdóticamente) que el stock del sistema actual **no es confiable** — no migrar como valor real, ya está resuelto por el plan de puesta a punto de stock inicial de Entrega 1 (arranque suave + ajuste manual). |

### Clasificación ABC automática por ventas reales (pedido explícito de Joaquín, 2026-08-17)

**Hallazgo crítico que cambia el plan**: el circuito que Joaquín confirmó como "el que usan hoy para registrar ventas" (`tblVentas`/`tblDetalleVentas`) tiene el campo de vínculo a producto (`tblDetalleVentas.Codigo`) **vacío en el 100% de las 10.463 filas** — no sirve para vincular ninguna venta a ningún artículo. El único circuito con vínculo confiable a producto (`ArticuloKey`, FK real, no texto) es `VentaItem`/`Operacion` — que sigue activo hasta la fecha del backup (`2026-08-14`, la misma fecha máxima que `tblVentas`), en paralelo. Para calcular rotación real **no hay otra fuente usable que `VentaItem`**, más allá de cuál de los dos circuitos considere Joaquín "el principal" operativamente.

**Simulación real (Pareto 80/95/100 por cantidad vendida, vía `VentaItem`):**
- Histórico completo (2002-2026): **675 artículos "A"**, **3.206 "B"**, **11.198 "C"** con venta registrada — total 15.079 artículos con al menos 1 venta alguna vez (solo 14.300 de los 121.691 activos, ~12% del catálogo activo).
- Últimos 12 meses (ventana más realista para rotación actual, no todo el histórico desde 2002): solo **1.536 artículos con venta**, 21.772 unidades vendidas en total.

**Recomendación concreta para la clasificación automática:**
1. Calcular la clasificación ABC sobre una **ventana móvil reciente** (ej. últimos 12 meses), no el histórico completo desde 2002 — evita que un producto que vendió mucho hace 10 años y ya no se repone quede marcado "A" para siempre.
2. Los productos **sin ninguna venta en la ventana** (la gran mayoría, dado que solo ~1.536 de 121.691 tuvieron venta en el último año) caen en "C" por defecto — es el mismo criterio ya acordado en el plan de puesta a punto de stock inicial (Entrega 1): la mayoría del catálogo arranca sin verificar.
3. **Nuance a confirmar con Joaquín**: la decisión previa (R10/analisis v1) fue "la clasificación ABC la hace el cliente por su cuenta, el sistema solo permite configurarla". Automatizarla por ventas cambia esa regla — propongo que el cálculo automático sea un **valor sugerido/default editable**, no un valor que se le imponga al cliente sin poder cambiarlo — mantiene la flexibilidad ya acordada y agrega el automatismo pedido ahora, sin contradecir la decisión anterior.
4. Para la migración (Etapa 3): usar la venta de los últimos 12 meses de `VentaItem` como clasificación ABC **inicial** de arranque, en vez de arrancar todo el catálogo sin clasificar.
5. Nota de datos: aparecen algunas cantidades vendidas netas negativas (devoluciones que superan las ventas del período en casos puntuales) — a resolver con un piso en 0 al calcular, no bloquea el enfoque general.
6. **Confirmado (2026-08-17): `VentaItem`/`Operacion` es el circuito correcto** — no `tblVentas`/`tblDetalleVentas` (ver corrección en la sección "Doble circuito Cliente/Venta" arriba). El cálculo y la simulación de esta sección ya estaban hechos sobre la fuente correcta.

### Regla de deduplicación de nombres — decisión final (2026-08-17)

Para los 3.612 grupos de nombre duplicado con más de un artículo `Activo=1` (los que no se resuelven solos), Joaquín eligió **regla automática sin pantalla de revisión**: conservar el artículo del grupo con la **venta más reciente** en `VentaItem`/`Operacion` (el mismo circuito ya confirmado como fuente de verdad).

**Verificación cuantitativa de esta regla (importante, cambia qué tan determinante es cada criterio):** de los 3.612 grupos, solo **486 (13%) tienen al menos una venta registrada en algún miembro** — ahí la regla "venta más reciente" decide sola. En **3.544 grupos (87%, la inmensa mayoría) ningún miembro del grupo vendió nunca** — la regla principal no alcanza a desambiguar y cae directo al criterio de respaldo. Por eso el criterio de respaldo no es un detalle menor: es el que realmente decide en la mayoría de los casos. Se fija como respaldo la `FechaModificacionPrecio` más reciente entre los miembros del grupo (la señal disponible más cercana a "cuál de los duplicados se sigue manteniendo activamente") — **confirmado por Joaquín (2026-08-17)**, ya con el peso real conocido (decide el 87% de los 3.612 casos, no un detalle menor).

**Regla de deduplicación de nombres — versión final:** por cada grupo de nombre duplicado con más de un `Articulo.Activo=1`, conservar el que tenga: (1) venta más reciente en `VentaItem`/`Operacion` si algún miembro tiene alguna venta registrada; (2) si no, `FechaModificacionPrecio` más reciente entre los miembros del grupo. El resto del grupo no se migra.

## Análisis de Etapa 3: CERRADO — lista para Diseño

### Próximos pasos de esta etapa (Análisis → Diseño, no iniciar Implementación todavía)
1. Cerrar con Joaquín las preguntas abiertas de arriba (gaps 1-8) — cuáles entran a alcance de Etapa 3 y cuáles quedan explícitamente excluidos.
2. Confirmar el volumen real (121.691 activos) como base de la nueva estimación de Etapa 3 — el precio provisional anterior (USD 315-394, basado en ~17.000) queda obsoleto y debe recalcularse en `4-presupuestador.md` una vez cerrado el Diseño/Arquitectura de esta etapa.
3. Diseñar la regla de deduplicación de `articuloProveedor` (última importación procesada y matcheada por proveedor+código) como parte de la etapa de Diseño.
4. La base restaurada (`LaPlatense_MigracionAnalisis`, instancia local `.\MSSQLSERVER01`, ~17GB en `C:\SQLRestore\`) queda disponible para consultas de seguimiento durante Diseño/Arquitectura — no es la base de producción, es solo para este análisis.

## Definiciones vigentes

### Modulos/features analizados

1. **Usuarios y roles**: Admin, Vendedor, Repartidor. Cada empleado tiene usuario propio. El repartidor **ve todas las entregas** (no solo las asignadas a él) — confirmado.
2. **Catálogo de productos**: precio compra, precio venta, precio con descuento, IVA por producto (10,5%/21%), marca, modelo, categorías.
3. **Unidades de medida y conversión compra↔venta**: venta por unidad, peso, metro o bulto; hay productos comprados por bulto y vendidos por unidad. **Pieza de mayor novedad técnica del proyecto** — sin precedente exacto en el estudio (ver §6.1).
4. **Stock**: control de inventario + alertas de stock mínimo.
5. **Ventas + cuenta corriente de clientes**: venta rápida, cualquier medio de pago, fiado con seguimiento por cliente, tarjeta de crédito en 3/6 cuotas con % de recargo configurable, venta totalmente configurable (precio unitario/cantidad/subtotal/total/%IVA editables), uno o varios pagos por venta, comprobante AFIP a cliente cargado o consumidor final, edición de productos/valores antes de emitir el comprobante (workflow Borrador→Facturada). **La venta facturada admite anulación mediante nota de crédito — no queda inmutable (confirmado).**
6. **Proveedores + compras**: registro de compras con actualización automática de stock; pago a proveedores con echeck o transferencia (registrado, sin gestión de cheques diferidos propios); lista de precios por proveedor con TC propio configurable y % de descuento particular; importación de listas de precios de proveedor aplicando TC + descuento.
7. **Caja**: ingresos, egresos, cierre diario y cierre mensual (dos niveles). **Un único punto de venta/caja física — confirmado.**
8. **Gastos varios**: gastos operativos clasificados en caja chica (diarios) o caja mensual (sueldos, alquileres).
9. **Cuenta corriente propia del negocio**: vista consolidada de cierres de caja diarios/mensuales + ingresos + egresos.
10. **Cuenta corriente de empleados**: autoservicio — cada empleado ve su propio sueldo pagado y retiros, gestionado por el admin, visible solo por el propio empleado.
11. **Presupuestos y cotizaciones en PDF**: cotizar a clientes.
12. **Entregas a domicilio**: seguimiento (repartidor ve todas); markup configurable como % del valor del producto; distinción entre entrega propia y tercerizada.
13. **Cheques (30/60/90 días) — alcance reducido**: sin pagos diferidos propios; se absorbe como campo de forma de pago dentro de Compras.
14. **Aumento masivo de precios**: por categoría, proveedor o marca en un solo paso.
15. **Dashboard — "foto completa del negocio" (CONFIRMADO, pantalla más importante del sistema)**: el cliente pidió explícitamente una vista integral en base a todo el modelo de datos, priorizando diseño y estructura por sobre otras pantallas. Ver §6.4 y §6.6 — se trata como la pieza de mayor prioridad de diseño de todo el proyecto, no como un dashboard genérico de KPIs sueltos.
16. **Devoluciones de mercadería + Notas de crédito/débito AFIP (NUEVO — confirmado 2026-07-30)**: aplican devoluciones de mercadería (NO aplican cambios/canjes por otro producto). La venta facturada puede anularse mediante nota de crédito. Ver §6.5.
17. **Migración de catálogo de productos — POSPUESTA, fuera de este presupuesto (ACTUALIZADO 2026-07-30)**: se saca como etapa del presupuesto actual. Motivo: (a) el problema real que la motivaba —no tener stock confiable— ya queda resuelto por el módulo de puesta a punto de stock inicial (§6.7, dentro de Etapa 1); (b) Joaquín va a hacer un **segundo relevamiento tras la aprobación de este presupuesto** para evaluar acceso directo a la base de datos del sistema actual del cliente, lo que bajaría el costo real de importación al mínimo comparado con depender de un archivo Excel exportado de formato desconocido. Se cotiza aparte, en una fase posterior, con datos reales en mano. Ver §6.2 y `4-presupuestador.md`.
18. **Código de barras — vinculación del código escaneado al producto (NUEVO — confirmado y simplificado 2026-07-30)**: el cliente tiene una ticketeadora **manual** (no se integra con el sistema — es un aparato físico independiente que ya usa para etiquetar). El sistema solo necesita vincular el código de barras escaneado a un producto (propio o de fábrica) y agregarlo automáticamente en la pantalla de venta. **No hay desarrollo de generación/impresión de etiquetas** — eso lo sigue haciendo el cliente con su ticketeadora, fuera del sistema. Ver §6.8.

### Funcionalidad adicional detectada (no pedida explícitamente — a validar, NO incluida en presupuesto salvo confirmación)

1. ~~Devoluciones/cambios de mercadería~~ → **Resuelto**: aplican devoluciones, no cambios (ver módulo 16).
2. Reservas de stock/apartados para clientes contratistas — sigue sin confirmar.
3. ~~Notas de crédito/débito AFIP~~ → **Resuelto**: sí aplican (ver módulo 16).
4. ~~Permisos granulares de repartidor~~ → **Resuelto**: ve todas las entregas.
5. ~~Múltiples puntos de venta/cajas físicas~~ → **Resuelto**: un único punto de venta.
6. Historial de precios por producto — sigue sin confirmar.
7. Alerta de lista de precios de proveedor desactualizada — sigue sin confirmar.

### Reglas funcionales acordadas

- R1: % de recargo por cuotas de tarjeta configurable por el admin.
- R2: % de markup de envío configurable por el admin.
- R3: TC propio y % de descuento configurables por proveedor (no globales).
- R4: producto con `UnidadCompra != UnidadVenta` requiere factor de conversión definido antes de poder comprarse.
- R5: venta en estado Borrador totalmente editable; al emitir comprobante AFIP pasa a Facturada. **Una venta Facturada puede anularse mediante nota de crédito (confirmado) — no es inmutable.** Queda abierto para Diseño: quién puede iniciar la anulación (¿solo admin, o también vendedor?) y si hay límite de tiempo — ver nueva pregunta abierta en §9.
- R6: cuenta corriente de empleado visible solo por ese empleado y por el admin — ningún otro rol, ni siquiera otro vendedor.
- R7: gasto clasificado en el alta como caja chica o caja mensual, no ambos.
- R8 (nueva): devolución de mercadería reingresa stock y genera una nota de crédito vinculada a la venta original. No existe flujo de "cambio" (canje por otro producto) — es siempre devolución simple.
- R9 (nueva): el repartidor ve el listado completo de entregas, no solo las propias asignadas.
- Permisos: Admin (todo) · Vendedor (ventas, catálogo consulta, stock consulta, su propia CC) · Repartidor (entregas — todas, no solo asignadas —, su propia CC).

- R10 (nueva): el stock inicial de los productos "A" (mayor rotación/valor) se carga con conteo físico real; los productos "B/C" arrancan en stock 0 o "sin verificar" y se permite venderlos con stock en negativo durante la transición (aviso, no bloqueo), hasta que se reconcilien por conteo cíclico o por uso real.
- R11 (nueva): un producto puede tener código de barras propio (asignado por el negocio) o reutilizar el de fábrica — el campo es único, sin importar el origen. La venta permite agregar un ítem escaneando su código, sin necesidad de buscarlo manualmente.

### Criterios de aceptacion vigentes (historias de mayor riesgo/novedad)

- PF1: compra por bulto/venta por unidad descuenta stock correctamente en cada unidad de venta.
- PF2: edición de precio/cantidad/IVA/descuento de una venta antes de emitir AFIP, sin anular/recrear.
- PF3: cobro con tarjeta en 3/6 cuotas mostrando el recargo antes de confirmar.
- PF4: TC propio + % descuento de proveedor aplicados correctamente al importar su lista.
- PF5: importación de lista de precios de proveedor (Excel) sin carga manual producto por producto.
- PF6: empleado ve su propia cuenta corriente, no la de sus compañeros.
- PF7: cierre de caja diario y mensual como reportes separados.
- PF8: cuenta corriente consolidada del negocio (cierres de caja + ingresos + egresos) en una sola vista.
- PF9 (nueva): anular una venta facturada emite una nota de crédito AFIP válida, vinculada a la factura original.
- PF10 (nueva): registrar una devolución de mercadería reingresa el stock correspondiente y queda vinculada a la nota de crédito.
- PF11 (nueva): el repartidor ve el listado completo de entregas sin filtrarse por las suyas.
- PF12 (nueva): la migración de catálogo (Etapa 3) procesa ~17.000 productos con reporte de éxitos/errores, sin bloquear el sistema durante la carga.
- PF13 (nueva): un producto sin stock verificado puede venderse igual (stock queda en negativo con aviso), no bloquea la venta.
- PF14 (nueva): un empleado puede ajustar manualmente el stock de un producto con motivo, y el ajuste queda auditado (quién, cuándo, motivo).
- PF15 (nueva): al escanear el código de barras de un producto en la pantalla de venta, se agrega automáticamente al carrito (propio o de fábrica, sin distinción para el usuario).

### Supuestos y dependencias

- ~~Supuesto: un solo punto de venta/caja física~~ → **Confirmado por el cliente.**
- Supuesto: AFIP/ARCA se factura desde el arranque del proyecto (pedido explícito del cliente, no exclusión).
- **Migración de catálogo pospuesta (ya no es dependencia de este presupuesto):** se saca como etapa — se cotiza aparte más adelante, después del segundo relevamiento donde Joaquín evaluará acceso directo a la base de datos del sistema actual (ver módulo 17). No bloquea la aprobación ni el inicio de Etapa 1/Etapa 2.
- ~~Dependencia: marca/modelo de la ticketeadora~~ → **Ya no aplica: la ticketeadora es manual, no se integra con el sistema.** Solo hace falta vincular el código escaneado al producto — ver §6.8.
- Dependencia para cerrar el dashboard: el cliente pidió "foto completa del negocio en base al modelo de datos" como la pantalla más importante — se recomienda una sesión de diseño dedicada para priorizar qué KPIs van primero (ver §6.4), en vez de presuponer un set cerrado.
- ~~Dependencia: confirmar si el repartidor ve todas las entregas o solo las propias~~ → **Resuelto: ve todas.**
- ~~Dependencia: confirmar si aplican devoluciones/cambios de mercadería~~ → **Resuelto: aplican devoluciones, no cambios.**
- ~~Dependencia: confirmar si la venta facturada admite anulación/NC o queda inmutable~~ → **Resuelto: admite anulación por NC.**
- Nueva dependencia (ver §9): definir quién puede anular una venta facturada y si hay límite de tiempo para hacerlo.
- Nueva dependencia (ver §9): confirmar si el archivo de migración incluye stock actual — es un dato crítico para no arrancar el sistema nuevo con stock desactualizado.

### Exclusiones confirmadas

- Gestión de cheques diferidos propios (emitidos por el negocio) — el cliente no opera con pagos diferidos, solo echeck/transferencia como forma de pago a proveedores.
- Cambios/canjes de mercadería por otro producto — solo devolución simple.
- Reservas de stock/apartados, historial de precios por producto y alerta de lista de proveedor vencida quedan excluidos del presupuesto hasta confirmación explícita del cliente.
- Migración de catálogo de productos — pospuesta, se cotiza aparte en una fase posterior (ver módulo 17).
- Integración con hardware externo (balanzas, ticketeadora de etiquetas u otros dispositivos) — sigue excluida; el único punto de contacto con hardware es el lector de código de barras en la venta, que funciona como teclado estándar (sin integración real).

## 6. Puntos de diseño actualizados

### 6.2 Migración de catálogo — actualizado (pospuesta, fuera de este presupuesto)

Confirmado: ~17.000 productos, archivo aún no recibido. Se retira como etapa de este presupuesto: Joaquín va a hacer un segundo relevamiento tras la aprobación, para evaluar acceso directo a la base de datos del sistema actual del cliente — con eso el costo real de importación bajaría al mínimo comparado con mapear un archivo Excel de formato desconocido. Se cotiza en una fase posterior, con datos reales en mano, no como parte de este presupuesto.

### 6.4 Dashboard — actualizado (pantalla de mayor prioridad de diseño)

El cliente confirmó que el dashboard es la pantalla más importante del sistema ("foto completa del negocio en base al modelo de datos") y pidió priorizar diseño y estructura por sobre el resto. Se recomienda una sesión de diseño dedicada (no solo email) antes de cerrar el detalle final, para evitar que "foto completa" derive en scope creep indefinido. Ver propuesta estructurada en `2-disenador-funcional.md`.

### 6.5 Devoluciones + Notas de crédito/débito AFIP (nuevo módulo)

- Devolución de mercadería: reingresa stock, requiere motivo, queda vinculada a la venta original y a la nota de crédito emitida.
- Nota de crédito AFIP: extiende el servicio de facturación ya resuelto (mismo patrón WSAA/WSFE) para emitir NC vinculada al comprobante original.
- Anulación de venta facturada: transición de estado Facturada→Anulada, disparada por la emisión de una NC (no hay anulación "silenciosa" sin comprobante fiscal).
- Reutiliza el patrón de devoluciones ya resuelto en `ShowroomGriffin`.
- No hay flujo de cambio/canje (confirmado) — simplifica el alcance respecto de lo que suele pedirse en retail.

### 6.6 KPIs del dashboard — reemplaza la hipótesis anterior

Ya no se propone un set fijo de antemano — dado que el cliente lo definió como la pantalla de mayor prioridad, se define en una sesión de diseño dedicada. Punto de partida sugerido (a validar, no a asumir cerrado): ventas del día/mes, stock crítico, cobros pendientes (CC clientes), pagos pendientes (CC proveedores), gastos del mes por categoría, top productos, estado de entregas del día, saldo de caja consolidado. *La sesión de diseño debe acotar cuáles de estos (u otros) son realmente prioritarios — no construir los ocho de una sola vez sin jerarquía.*

### 6.7 Plan de puesta a punto de stock inicial (nuevo, 2026-07-30)

**Problema real declarado por el cliente:** hoy no hay stock confiable — se maneja de memoria por la rotación de artículos, y son ~17.000 productos a migrar. Ni "arrancar de cero total" ni "contar físicamente los 17.000 productos antes de arrancar" son razonables: lo primero rompe las alertas de stock mínimo desde el día 1 para todo el catálogo; lo segundo es inviable en tiempo con el equipo actual y probablemente no sería mucho más preciso que la memoria de hoy, dado el ritmo de rotación.

**Enfoque recomendado — clasificación ABC + arranque suave + reconciliación progresiva:**

1. **Clasificar productos por rotación/valor (ABC) — la hace el propio cliente (CONFIRMADO 2026-07-30), no Olvidata.** El sistema brinda la posibilidad de configurar la clasificación (campo `clasificacionABC` en el producto, editable desde el catálogo) — el cliente decide qué es "A" según su propio conocimiento del negocio, sin que Olvidata tenga que involucrarse en esa decisión comercial.
2. **Contar físicamente solo los productos "A"** antes o durante el arranque — es factible en pocos días con el equipo actual. Es donde más importa tener stock exacto (evita quiebres en lo que más se vende).
3. **Los productos "B/C" (la mayoría) arrancan en stock 0 o "sin verificar"** — el sistema debe permitir venderlos igual aunque el stock quede en negativo durante la transición (aviso, no bloqueo duro) — ver R10/PF13.
4. **Ajuste manual de stock con motivo**, disponible para cualquier empleado autorizado, para corregir sobre la marcha cuando note una diferencia real en el mostrador — reutiliza patrón ya resuelto (`ShowroomGriffin`, ajuste manual de stock) — ver PF14.
5. **Conteo cíclico post-arranque** (recomendación operativa, no funcionalidad de software): revisar una categoría por semana durante 2-3 meses hasta reconciliar el 100% del catálogo, en vez de un inventario general de una sola vez.
6. Si el archivo de migración trae una columna de stock, se importa como **punto de partida de referencia, no como dato confiable** — mismo criterio que si no la trajera, dado que el cliente ya advirtió que no confía en ese número hoy.

**Qué es desarrollo y qué es proceso del cliente:** los puntos 1 (clasificación ABC), 2 (conteo físico) y 5 (conteo cíclico) son trabajo operativo del propio negocio — el cliente decide y ejecuta, no llevan horas de desarrollo por sí mismos. Lo que sí es desarrollo es que el sistema **permita configurar** esa clasificación (campo editable) y sostener el resto del flujo — puntos 3, 4 y 6 — ver el módulo ampliado de Stock (Etapa 1) en `4-presupuestador.md`. *Nota: al sacarse la migración como etapa de este presupuesto, la funcionalidad de ajuste manual de stock queda como el mecanismo principal (no complementario) para que el cliente construya un stock confiable desde el arranque.*

### 6.8 Código de barras — vinculación al producto + lectura en venta (módulo simplificado, 2026-07-30)

- **La ticketeadora es manual (confirmado por el cliente)** — no se integra con el sistema, no hay generación/impresión de etiquetas de por medio. El cliente sigue etiquetando físicamente por su cuenta, igual que hoy.
- **Lo único que necesita el sistema**: vincular el código de barras (propio o de fábrica) al producto en el catálogo, y en la pantalla de venta, un campo que detecte el escaneo (lector USB tipo teclado, sin driver especial) y agregue el producto automáticamente al carrito.
- Esto redujo bastante el alcance de este módulo respecto de la versión anterior (que asumía integración con una impresora de etiquetas) — ver `4-presupuestador.md`.

## 9. Preguntas abiertas (actualizado)

1. ~~¿La venta facturada admite anulación/nota de crédito?~~ → **Cerrada: sí, admite anulación por NC.**
2. ~~¿Cuál es el archivo/formato real del catálogo?~~ → **Ya no aplica a este presupuesto: la migración se saca como etapa y se cotiza aparte más adelante (ver módulo 17).**
3. ~~¿Uno o varios puntos de venta/cajas físicas?~~ → **Cerrada: uno solo.**
4. ~~¿El repartidor ve todas las entregas o solo las asignadas?~~ → **Cerrada: ve todas.**
5. ~~¿Aplican devoluciones/cambios de mercadería?~~ → **Cerrada: aplican devoluciones, no cambios.**
6. ~~¿Set exacto de KPIs del dashboard?~~ → **Cerrada parcialmente: se define en sesión de diseño dedicada, no por email — ver §6.6.**
7. **(Nueva)** ¿Quién puede iniciar la anulación de una venta facturada — solo el admin, o también el vendedor? ¿Hay un límite de tiempo (ej. solo el mismo día)?
8. ~~¿El archivo de migración de catálogo va a incluir el stock actual?~~ → **Ya no aplica: la migración se pospone, se resuelve cuando se cotice esa fase futura.**
9. ~~¿Quién define la clasificación ABC de productos?~~ → **Cerrada: la hace el cliente por su cuenta. El sistema solo brinda la posibilidad de configurarla (campo editable en el catálogo).**
10. ~~¿Marca/modelo de la ticketeadora?~~ → **Cerrada: ya no aplica — la ticketeadora es manual, no se integra con el sistema.**

## Historial de ajustes
- 2026-07-30: Análisis v1 creado post-relevamiento presencial en La Platense.
- 2026-07-30 (v2): el cliente respondió las 6 preguntas abiertas de la v1. Cambios de alcance resultantes: (a) nuevo módulo "Devoluciones + Notas de crédito/débito AFIP" (venta facturada anulable por NC, devoluciones sin cambios); (b) migración de catálogo confirmada en ~17.000 productos, formato aún no recibido, promovida a **Etapa 3 independiente** del presupuesto por pedido explícito del cliente; (c) dashboard confirmado como pantalla de mayor prioridad de diseño ("foto completa del negocio"), ya no un KPI-set genérico; (d) confirmado un único punto de venta/caja y que el repartidor ve todas las entregas (sin cambio de esfuerzo, solo cierre de incertidumbre). Surgieron 2 preguntas nuevas (quién anula una venta facturada y si el archivo de migración trae stock).
- 2026-07-30 (v3): agregado el plan de puesta a punto de stock inicial (§6.7) — el cliente confirmó que hoy no hay stock confiable (se maneja de memoria). Enfoque recomendado: clasificación ABC + conteo físico solo de los productos de mayor rotación/valor + arranque suave (stock negativo permitido, con aviso) para el resto + ajuste manual con motivo + conteo cíclico post-arranque. La pregunta abierta #8 deja de ser bloqueante. Nueva pregunta abierta #9 (quién hace la clasificación ABC). Impacto en presupuesto: Stock (Etapa 1) ampliado con ajuste manual/flag de venta con stock negativo; Etapa 3 suma la extensión del importador para aceptar conteo real como columna opcional — ver `4-presupuestador.md`.
- 2026-07-30 (v4): cerrada la pregunta #9 — **la clasificación ABC la hace el propio cliente**, no Olvidata; el sistema solo brinda la posibilidad de configurarla (campo editable en el catálogo). No cambia el esfuerzo estimado (ya estaba contemplado como campo simple en `Producto`), solo cierra la incertidumbre de proceso.
- 2026-07-30 (v5): dos cambios de alcance importantes. (a) **Se agrega el módulo "Código de barras — etiquetado con ticketeadora + lectura en venta"** (§6.8): el cliente tiene una ticketeadora física y códigos de barra propios además de los de fábrica; el sistema debe poder imprimir etiquetas y agregar productos a la venta por escaneo. Nueva pregunta abierta sobre marca/modelo de la ticketeadora (define si es integración simple o requiere protocolo propietario). (b) **Se saca la migración de catálogo como etapa de este presupuesto** — el problema de stock que la motivaba ya está resuelto por el módulo de puesta a punto de stock inicial (Etapa 1), y Joaquín va a evaluar en un segundo relevamiento el acceso directo a la base de datos actual del cliente para bajar el costo real de importación; se cotiza aparte, más adelante. Impacto en el presupuesto: ver `4-presupuestador.md` — el nuevo módulo de código de barras (bajo reuse) hizo caer el ratio de reutilización de Etapa 1+2 por debajo del 70%, pasando de Tier 1 a **Tier 2**.
- 2026-07-30 (v6): Joaquín aclaró que **la ticketeadora es manual** — no se integra con el sistema. Se simplifica el módulo de código de barras a solo vincular el código escaneado al producto (sin generación/impresión de etiquetas). Se cierra la pregunta abierta #10 (marca/modelo, ya no aplica). Impacto en presupuesto: módulo de código de barras baja de 7h a 3h — ver `4-presupuestador.md` para el efecto en el ratio de reutilización y el precio final (Joaquín además fijó el precio a cobrar en USD 1.800, con su propia estimación de 30h reales + USD 200 de tokens IA).
