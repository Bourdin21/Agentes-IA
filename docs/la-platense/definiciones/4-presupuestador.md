# Memoria - Presupuestador

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-07-30 (v2 — actualizado con respuestas del cliente a las preguntas abiertas)

## Definiciones vigentes

### WBS funcional vigente

**Etapa 1 (MVP operable — lo mínimo para reemplazar el manejo manual del día a día)**

| # | Módulo | M (h) | Base de reutilización |
|---|---|---:|---|
| 1 | Usuarios y roles (admin/vendedor/repartidor, repartidor ve todas las entregas) | 5 | `marihogar` M10 (4h) + 1h nuevo |
| 2 | Catálogo de productos (desc./IVA config./marca/modelo) | 9 | `marihogar` M2 (8h) + `ShowroomGriffin` (Marca/Modelo) + 1h nuevo |
| 3 | Unidades de medida y conversión compra↔venta | 5 | Sin precedente exacto — 100% desarrollo nuevo |
| 4 | Stock + alertas + puesta a punto de stock inicial (AMPLIADO — ajuste manual con motivo/auditoría, flag de venta con stock negativo permitido, campo de clasificación ABC; el cliente no tiene stock confiable hoy) | 8 | `marihogar` M3 (6h) + `ShowroomGriffin` ajuste manual de stock (1h) + 1h nuevo |
| 5 | Ventas + CC clientes (recargo cuotas + workflow Borrador→Facturada) | 23 | `marihogar` M5+M11 (17h) + 6h nuevo |
| 6 | Facturación AFIP (Factura) | 7 | `marihogar`/`delicias-naturales`, reuse total |
| 7 | Proveedores + compras (TC propio + % desc. + importación de listas) | 18 | `marihogar` M12+M13 (13h) + 5h nuevo |
| 8 | Caja (cierre diario + mensual, punto de venta único confirmado) | 7 | `marihogar` M15 (4h) + 3h nuevo |
| 9 | Gastos varios (caja chica/mensual) | 4 | `marihogar` M18 (3h) + 1h nuevo |
| 10 | **Dashboard — "foto completa del negocio" (AMPLIADO, prioridad de diseño confirmada por el cliente)** | 12 | `marihogar` M9 (6h) + 6h nuevo (3 niveles: día/salud financiera/tendencias, antes 8h con KPIs genéricos) |
| | **Subtotal Etapa 1** | **98** | |

**Etapa 2 (alcance complementario)**

| # | Módulo | M (h) | Base de reutilización |
|---|---|---:|---|
| 11 | Cuenta corriente de empleados (autoservicio) | 4 | Patrón ledger conocido (1h) + 3h nuevo |
| 12 | Cuenta corriente propia del negocio (consolidado) | 5 | `ganaderia` CajaService (2h) + 3h nuevo |
| 13 | Presupuestos y cotizaciones en PDF | 8 | `marihogar` M4, reuse total |
| 14 | Entregas a domicilio (markup + propia/tercerizada) | 8 | `marihogar` M6 (6h) + 2h nuevo |
| 15 | Aumento masivo de precios (cat./proveedor/marca) | 4 | `marihogar`/`ShowroomGriffin`, reuse total |
| 16 | **Devoluciones de mercadería + Notas de crédito/débito AFIP (NUEVO — confirmado por el cliente)** | 9 | `ShowroomGriffin` devoluciones (3h) + extensión AFIP existente (1h) + workflow anulación (1h) = 5h reuse + 4h nuevo |
| | **Subtotal Etapa 2** | **38** | |

**Etapa 3 — Migración de catálogo + puesta a punto de stock inicial (INDEPENDIENTE, a pedido explícito del cliente)**

| # | Módulo | M (h) | Base de reutilización |
|---|---|---:|---|
| 17 | Migración de catálogo (~17.000 productos, formato de origen aún no recibido): mapeo configurable de columnas, validación/preview, carga por lotes con reporte de errores | 12 | `contadores-bma-conversor` parser (2h) + 10h nuevo (mapeo específico + volumen + validación por lotes) |
| 18 | **Puesta a punto de stock inicial (NUEVO — el cliente no tiene stock confiable hoy, se maneja de memoria)**: extensión del importador para aceptar columna opcional de "cantidad contada" (productos ABC clasificados como "A") | 3 | Extensión del mismo importador (2h reuse) + 1h nuevo (merge de conteo real con el resto del catálogo) |
| | **Subtotal Etapa 3 (base, antes de riesgo declarado)** | **15** | |

*Nota: "Cheques (30/60/90 días)" sigue sin presupuestarse como módulo aparte — se absorbe como campo de forma de pago dentro del módulo 7.*

### Estimaciones PERT por item

M anclado en calibración histórica de `marihogar` (rubro más cercano) y ajustado por los módulos nuevos confirmados en esta ronda: Devoluciones+NC (nuevo, ver módulo 16) y Dashboard ampliado (módulo 10). La migración (Etapa 3) lleva la mayor incertidumbre de todo el proyecto por no tener aún el archivo real.

### Tasa vigente y contingencia aplicada

- Tasa vigente: USD 35/h. Fórmula de lista: `Costo módulo = M × $16.80`.

### Cálculo de reutilización (R) y Tier aplicable — Etapa 1 + Etapa 2

| | Horas |
|---|---:|
| Total M (Etapa 1 + Etapa 2) | 136h |
| Horas ancladas en reuse directo | 96h |
| Horas de desarrollo genuinamente nuevo | 40h |

**R = 96 / 136 = 70,6%** → **Tier 1 (R ≥ 70%): 30% de descuento**.

*Nota de transparencia (se ajusta desde v2): el margen sobre el umbral de 70% se achicó de nuevo (70,9%→70,6%) al sumar la ampliación de Stock (ajuste manual/ABC, baja proporción de reuse). Sigue en Tier 1, pero el colchón sobre el 70% ya es mínimo — cualquier módulo nuevo adicional de baja reutilización que se confirme más adelante podría hacer caer el proyecto a Tier 2 (15%). Recomendado: no seguir sumando alcance nuevo a Etapa 1/2 sin revisar este cálculo.*

### Cálculo de reutilización (R) y Tier aplicable — Etapa 3 (migración + stock inicial, calculado aparte)

| | Horas |
|---|---:|
| Total M (Etapa 3) | 15h |
| Horas ancladas en reuse directo (parser base + extensión) | 4h |
| Horas de desarrollo nuevo (mapeo específico + volumen + merge de conteo) | 11h |

**R = 4 / 15 = 26,7% → Tier 3: 0% de descuento.** Se calcula y cotiza **por separado** del resto del proyecto, no se mezcla en el R combinado de Etapa 1+2: es trabajo específico de este cliente (mapeo de un archivo que no existe todavía + reconciliación de stock real), no un ahorro financiado por patrones ya construidos — mezclarlo diluiría el Tier 1 genuino del resto del sistema sin motivo real.

Gatillo económico: tablero de ciclos económicos en verde/consolidación a la fecha (2026-07-30) → Tier 1 habilitado para Etapa 1+2 sin restricción.

### Resumen economico (con Tokens IA como item individual)

**Etapa 1 + Etapa 2 (Tier 1, 30% descuento)**

| Concepto | USD |
|---|---:|
| Subtotal Etapa 1 (lista, 98h × $16.80) | 1.646,40 |
| Subtotal Etapa 2 (lista, 38h × $16.80) | 638,40 |
| **Subtotal desarrollo (sin Tokens IA, sin descuento)** | **2.284,80** |
| Tokens IA (25% del subtotal de lista) | 571,20 |
| Descuento Tier 1 (30% del subtotal de lista) | −685,44 |
| **Precio final Etapa 1 + Etapa 2** | **≈ 2.170,56** |

Desglose por etapa: Etapa 1 ≈ **USD 1.564** · Etapa 2 ≈ **USD 606**.

**Etapa 3 — Migración + stock inicial (Tier 3, sin descuento, con riesgo declarado por migración de datos)**

| Concepto | USD |
|---|---:|
| Subtotal Etapa 3 (lista, 15h × $16.80) | 252,00 |
| Tokens IA (25%) | 63,00 |
| Descuento Tier 3 (0%) | 0 |
| Subtotal antes de riesgo declarado | 315,00 |
| Riesgo declarado por migración de datos — formato aún no confirmado + volumen ~17.000 filas (25%, regla vigente en `27-presupuesto-parametros.instructions.md`) | +78,75 |
| **Precio final Etapa 3 (provisional)** | **≈ 394** |

*Provisional: se re-cotiza formalmente cuando el cliente entregue el archivo real — puede subir o bajar según formato/calidad del dato.*

### Descuento adicional por referido (decisión comercial 2026-07-30)

15% sobre el costo real de desarrollo, aplicado a Etapa 1 + Etapa 2:

| Concepto | USD |
|---|---:|
| Precio real Etapa 1 + Etapa 2 (Tier 1 + Tokens IA) | 2.170,56 |
| Descuento por referido (15%) | −325,58 |
| **Precio final Etapa 1 + Etapa 2 a cobrar** | **≈ 1.845** |

Por etapa: Etapa 1 ≈ **USD 1.329** · Etapa 2 ≈ **USD 516**.

**Etapa 3 — el 15% de referido sigue sin aplicarse:** aunque ahora $394 × 0,85 = $335 (ya por encima del piso de USD 280, a diferencia de la versión anterior), se mantiene sin descuento porque el motivo de fondo no cambió — es Tier 3 (sin ahorro real de reutilización) y una estimación provisional sujeta a re-cotización. Si Joaquín prefiere aplicar igual el referido acá una vez confirmado el archivo real, es una decisión válida — no se resuelve unilateralmente en este documento.

### Total del proyecto (las 3 etapas)

| Etapa | USD |
|---|---:|
| Etapa 1 | 1.329 |
| Etapa 2 | 516 |
| Etapa 3 (migración + stock inicial, provisional) | 394 |
| **Total** | **≈ 2.239** |

### Costo real de producción vs. precio cobrado (actualizado)

USD 200 de tokens IA reales estimados quedan cubiertos por la línea de Tokens IA de Etapa 1+2 (~USD 486 netos tras Tier 1 + referido) más el Tokens IA de Etapa 3 (USD 63, sin descuento). Cobertura total ≈ USD 549 contra USD 200 reales — el colchón sigue creciendo a medida que el alcance confirmado suma módulos.

### Calibraciones historicas usadas

- `marihogar/definiciones/4-presupuestador.md`: fuente principal de M-hour por módulo.
- `delicias-naturales`: referencia conceptual para `UnidadMedida`.
- `contadores-bma-conversor`: referencia de esfuerzo para parser de importación Excel propietario (Etapa 3).
- `ganaderia`: referencia de `CajaService`/`EgresoService`.
- `vinosefue`: referencia de `MovimientoCCProveedor`.
- `ShowroomGriffin`: referencia de `Marca`/`Modelo`, aumento masivo de precios, **devoluciones de mercadería**, y **ajuste manual de stock** (`StockController`, nuevo en esta ronda).

### Cierre estimado vs real (si disponible)
Pendiente — proyecto en etapa de presupuesto, aún no iniciado.

## Historial de ajustes
- 2026-07-30: Presupuesto interno v1 — WBS de 16 módulos (126h totales), R=73% → Tier 1, precio real de desarrollo ≈ USD 2.011.
- 2026-07-30: Aplicado 15% de descuento por referido sobre el costo real → USD 1.709.
- 2026-07-30: Analizado el consumo estimado de USD 200 en tokens IA contra el precio final — cubierto con margen por la línea de Tokens IA existente.
- 2026-07-30 (v2 — respuestas del cliente a las preguntas abiertas): (a) confirmada anulación de venta facturada por NC + devoluciones sin cambios → nuevo módulo 16 "Devoluciones + NC/ND AFIP" (9h, Etapa 2), reutiliza patrón de `ShowroomGriffin`; (b) migración de catálogo confirmada en ~17.000 productos, formato aún no recibido → promovida a **Etapa 3 independiente** (12h base + 25% riesgo declarado = USD 315 provisional, sin Tier discount ni referido); (c) dashboard ampliado de 8h a 12h por pedido explícito del cliente de tratarlo como la pantalla de mayor prioridad ("foto completa del negocio"); (d) confirmado punto de venta único y repartidor con visibilidad total de entregas, sin impacto en horas. **Efecto combinado: R de Etapa 1+2 bajó de 73% a 70,9%** (sigue en Tier 1, pero más ajustado) por el peso del nuevo módulo de bajo reuse. Precio final: Etapa 1 ≈ USD 1.302, Etapa 2 ≈ USD 516, Etapa 3 (provisional) ≈ USD 315 — **Total ≈ USD 2.133**.
- 2026-07-30 (v3 — plan de puesta a punto de stock inicial): el cliente confirmó que no tiene stock confiable hoy (se maneja de memoria por rotación de artículos). Se agregó ajuste manual de stock + flag de venta con stock negativo + campo ABC al módulo Stock de Etapa 1 (6h→8h, reutiliza patrón `ShowroomGriffin`) y se sumó a Etapa 3 la extensión del importador para aceptar conteo real de los productos "A" (+3h, 12h→15h base). **Efecto en R: Etapa 1+2 bajó de 70,9% a 70,6%** — sigue en Tier 1, pero el colchón sobre el umbral ya es mínimo; no conviene seguir sumando alcance nuevo de bajo reuse sin revisar este cálculo de nuevo. Precio final actualizado: Etapa 1 ≈ USD 1.329, Etapa 2 ≈ USD 516 (sin cambio), Etapa 3 (provisional) ≈ USD 394 — **Total ≈ USD 2.239**.
