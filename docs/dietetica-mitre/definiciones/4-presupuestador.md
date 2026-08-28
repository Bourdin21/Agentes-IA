# Memoria - Presupuestador

## Proyecto: dietetica-mitre
## Ultima actualizacion: 2026-08-26

## Definiciones vigentes

### Nota metodologica: mismo concepto y mismo precio que desborder-sin-gluten
A pedido explicito de Joaquin ("armar un presupuesto con el mismo concepto y precio"), este presupuesto reutiliza integramente el WBS, el PERT y los numeros finales ya cerrados en `docs/desborder-sin-gluten/definiciones/4-presupuestador.md` — mismo rubro, mismo pain point, mismo pitch outbound. No se recalcula de cero.

### Propuesta B — Solo modulo de facturacion electronica (identica a desborder-sin-gluten)

| # | Item | M | USD lista | USD distribuido (x1.25) |
|---|---|---:|---:|---:|
| 1 | Usuarios y roles (1 rol Administracion) | 2 | 33.60 | 42.00 |
| 2 | Catalogo simple de productos/conceptos | 3 | 50.40 | 63.00 |
| 3 | Emision de comprobantes | 6 | 100.80 | 126.00 |
| 4 | Integracion AFIP/ARCA (reuso PAT-006) | 5 | 84.00 | 105.00 |
| 5 | Historial + reimpresion PDF con QR | 3 | 50.40 | 63.00 |
| 6 | Puesta en marcha + alta AFIP | 3 | 50.40 | 63.00 |
| **Total** | **22** | **369.60** | **462.00** |

**Numero final (fijado por Joaquin, mismo criterio comercial que desborder-sin-gluten): USD 400.** Descuento efectivo sobre el subtotal distribuido: 462.00 - 400 = -USD 62 (~16.8%, no recalculado por formula de tiers — decision comercial directa).

### Propuesta A — Sistema integral (identica a desborder-sin-gluten)

| # | Item | Etapa | M | USD lista | USD distribuido (x1.25) |
|---|---|---|---:|---:|---:|
| 1 | Usuarios y roles | 1 | 2 | 33.60 | 42.00 |
| 2 | Productos (con stock) | 1 | 4 | 67.20 | 84.00 |
| 3 | Stock (control + alertas) | 1 | 5 | 84.00 | 105.00 |
| 4 | Proveedores + Compras | 1 | 5 | 84.00 | 105.00 |
| 5 | Ventas con cobro (PAT-003) | 1 | 10 | 168.00 | 210.00 |
| 6 | Integracion AFIP/ARCA (reuso PAT-006) | 1 | 5 | 84.00 | 105.00 |
| 7 | Cierre de caja automatico | 1 | 4 | 67.20 | 84.00 |
| 8 | Dashboard simple | 1 | 2 | 33.60 | 42.00 |
| 9 | Puesta en marcha + alta AFIP | 1 | 3 | 50.40 | 63.00 |
| **Subtotal Etapa 1** | | **40** | **672.00** | **840.00** |
| 10 | Reportes basicos | 2 | 2 | 33.60 | 42.00 |
| **Subtotal Etapa 2** | | **2** | **33.60** | **42.00** |
| **Subtotal proyecto** | | **42** | **705.60** | **882.00** |

**Numero final (fijado por Joaquin, identico a desborder-sin-gluten): USD 650.** Descuento efectivo sobre el subtotal distribuido: 882.00 - 650 = -USD 232 (~32.9%).

### Ratio de reutilizacion (R) y descuento por volumen
Identicos a desborder-sin-gluten en terminos relativos (mismo M, mismo Subtotal_lista): Propuesta B R=22.7%/Tier V0, Propuesta A R=11.9%/Tier V1(5%) — ambos por debajo de Tier 1/2 formal. Igual que en desborder-sin-gluten, los numeros finales fueron fijados directamente por decision comercial (ver arriba), no por el resultado puro de la formula de tiers.

### Plan de mantenimiento anual
Mas simple que desborder-sin-gluten porque aca **no hay ambiguedad de usuarios** — Dietetica Mitre confirmo 1 sola persona sin duda:

- **Propuesta B:** 2 tablas de negocio → **STARTER, USD 300/año, 1 admin incluido — cubre exacto, sin upsell.**
- **Propuesta A:** 8 tablas de negocio → **PRO, USD 400/año, hasta 2 usuarios incluidos — cubre exacto (sobra 1 usuario de margen si suman a alguien despues), sin upsell.**

**Primer año de mantenimiento GRATIS en ambas opciones** (mismo criterio aplicado a desborder-sin-gluten) — desde el año 2, precio de lista sin cambios.

### Costo interno de IA
Identico a desborder-sin-gluten (mismo M): Propuesta B ≈ USD 46.24 interno vs Tokens IA USD 92.40; Propuesta A ≈ USD 84.64 interno vs Tokens IA USD 176.40. Ningun item supera el umbral 15%.

## Historial de ajustes
- 2026-08-26: primera version, reutilizando integramente el WBS/PERT/numeros finales de desborder-sin-gluten a pedido explicito de Joaquin ("mismo concepto y precio"). Propuesta B: USD 400 desarrollo + STARTER USD 300/año (año 1 gratis, sin ambiguedad de usuarios). Propuesta A: USD 650 desarrollo + PRO USD 400/año (año 1 gratis).
