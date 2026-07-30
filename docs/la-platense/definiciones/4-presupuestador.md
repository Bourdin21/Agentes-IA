# Memoria - Presupuestador

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-07-30 (v6 — estructura final de pago: USD 1.500/3 pagos o USD 1.800/12 pagos; mantenimiento PREMIUM año 1 gratis)

## Definiciones vigentes

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
- 2026-07-30: Presupuesto interno v1 — WBS de 16 módulos (126h totales), R=73% → Tier 1, precio real de desarrollo ≈ USD 2.011.
- 2026-07-30: Aplicado 15% de descuento por referido sobre el costo real → USD 1.709.
- 2026-07-30: Analizado el consumo estimado de USD 200 en tokens IA contra el precio final — cubierto con margen por la línea de Tokens IA existente.
- 2026-07-30 (v2 — respuestas del cliente): confirmada anulación de venta facturada por NC + devoluciones sin cambios (nuevo módulo, Etapa 2); migración confirmada en ~17.000 productos, formato aún no recibido, promovida a Etapa 3 independiente (USD 315 provisional); dashboard ampliado (prioridad de diseño); confirmado punto de venta único y repartidor con visibilidad total. R de Etapa 1+2 bajó de 73% a 70,9% (Tier 1, más ajustado). Total con las 3 etapas ≈ USD 2.133.
- 2026-07-30 (v3 — plan de stock inicial): Stock ampliado (6h→8h) con ajuste manual/ABC/flag negativo, reutilizando patrón `ShowroomGriffin`; Etapa 3 sumó extensión del importador para conteo real (12h→15h). R de Etapa 1+2 bajó a 70,6% (sigue Tier 1, colchón mínimo). Total con las 3 etapas ≈ USD 2.239.
- 2026-07-30 (v4 — código de barras + retiro de la migración como etapa): (a) agregado el módulo "Código de barras — etiquetado con ticketeadora + lectura en venta" (7h, Etapa 1) — el cliente tiene ticketeadora física y códigos propios/de fábrica; (b) **retirada la migración de catálogo de este presupuesto** — el problema de stock que la motivaba ya está resuelto por el módulo de stock ampliado, y Joaquín va a evaluar acceso a la base de datos real en un segundo relevamiento antes de cotizar esa fase por separado. **Efecto combinado: R de Etapa 1+2 bajó de 70,6% a 68,5% — el proyecto pasa de Tier 1 (30%) a Tier 2 (15%)**, tal como se había advertido. Precio final actualizado: Etapa 1 ≈ USD 1.649, Etapa 2 ≈ USD 597 — **Total ≈ USD 2.246** (la migración se cotiza aparte, en una fase posterior).
- 2026-07-30 (v5 — ticketeadora manual + override de precio a USD 1.800): Joaquín aclaró que la ticketeadora es manual (no se integra) — el módulo de código de barras baja de 7h a 3h (solo vinculación + lookup en venta, sin etiquetado). Esto sube el R de Etapa 1+2 a 69,8% (caso límite, a 0,2 puntos de Tier 1, se mantiene Tier 2 por criterio estricto). El precio según fórmula/política queda en ≈USD 2.183. **Joaquín fijó el precio final a cobrar en USD 1.800** (override comercial directo, ≈17,5% por debajo de la fórmula) — Etapa 1 ≈ USD 1.308, Etapa 2 ≈ USD 492. Chequeo de margen con sus propios números (30h reales + USD 200 tokens IA): tasa efectiva realizada ≈USD 53,3/h, por encima del objetivo de USD 35/h — el override no compromete la rentabilidad esperada.
- 2026-07-30 (v6 — estructura final de pago + mantenimiento): Joaquín reestructuró el precio final como dos modalidades de pago del total del proyecto (ya no por etapa): **USD 1.500 en hasta 3 pagos**, o **USD 1.800 en hasta 12 pagos**. Chequeo de margen con sus propios números confirma que ambas modalidades quedan por encima del objetivo de USD 35/h (≈USD 43,3/h y ≈USD 53,3/h respectivamente). Mantenimiento simplificado a un único plan **PREMIUM** desde el arranque (año 1 gratis, USD 500/año desde el año 2) — reemplaza la transición PRO→PREMIUM de versiones anteriores.
