# Memoria - Presupuestador

## Proyecto: peras-del-olmo
## Ultima actualizacion: 2026-08-27

## Definiciones vigentes

### Correccion de clasificacion de mantenimiento (2026-08-27, antes de la reestructuracion MVP/Full)
La version anterior de este documento clasifico el mantenimiento como PREMIUM (16-30 tablas) razonando desde la cantidad de USUARIOS, no de tablas — error de aplicacion del criterio. Contando tablas de negocio reales del alcance completo (Categoria, Cliente, Proveedor, Producto, VarianteProducto, Stock, MovimientoStock, Compra, CompraItem, Venta, VentaItem, VentaPago, Devolucion = 13 tablas), el plan correcto por la tabla vigente (`27-presupuesto-parametros.instructions.md`) es **PRO (6-15 tablas), no PREMIUM**. Corregido en esta version, aplicado a ambas propuestas (MVP y Full) de abajo.

### Nota metodologica: dos propuestas de implementacion (MVP vs Full con AFIP)
A pedido explicito de Joaquin, se reestructura el presupuesto en dos propuestas de implementacion completas: **MVP** (el minimo que resuelve el pain point confirmado — stock por talle/color y ventas) y **Full** (todo el alcance ya diseñado, mas facturacion electronica AFIP/ARCA, no incluida en ninguna version anterior de este documento). Ambas anclan el mismo perfil de reutilizacion de ShowroomGriffin ya documentado en `2-disenador-funcional.md`/`3-arquitecto-mvc.md`. Se mantiene la nota metodologica previa: sin consulta estrategica especial (perfil retail directo al consumidor, Tier 1 aplicado por defecto sin necesidad de override de `olvidata-ceo`, a diferencia de FABINCO), sin año de mantenimiento gratis (reservado para manejo de objecion de precio, no hubo ninguna todavia).

---

## Propuesta MVP

### WBS
| # | Item | Clasificacion |
|---|---|---|
| 1 | Usuarios y roles (4 personas) | Modulo nuevo — ABM simple |
| 2 | Categorias (con flag UsaVariantes) + Clientes | **Reutilizacion de patron real** — ShowroomGriffin, sin Proveedores (no hay Compras en el MVP) |
| 3 | Productos y Variantes (soporta categorias con o sin variantes) | **Reutilizacion de patron real** — ShowroomGriffin |
| 4 | Stock (por variante o producto simple, con alertas) | **Reutilizacion de patron real** — ShowroomGriffin |
| 5 | Ventas con cobro multi-medio y cuotas (PAT-003) | **Reutilizacion de patron real** — ShowroomGriffin |
| 6 | Puesta en marcha | Deploy inicial |

**Fuera del MVP** (quedan solo en la propuesta Full): Compras a proveedores, Devoluciones y cambios, Aumento masivo de precios, Reportes, Dashboard, Facturacion electronica AFIP/ARCA.

### Estimaciones PERT
| # | Item | O | M | P | PERT | M usado |
|---|---|---:|---:|---:|---:|---:|
| 1 | Usuarios y roles | 2 | 3 | 4 | 3.00 | 3 |
| 2 | Categorias + Clientes | 3.5 | 5 | 7 | 5.08 | 5 |
| 3 | Productos y Variantes | 5 | 7 | 10 | 7.17 | 7 |
| 4 | Stock | 3.5 | 5 | 7 | 5.08 | 5 |
| 5 | Ventas con cobro + cuotas | 9 | 12 | 17 | 12.33 | 12 |
| 6 | Puesta en marcha | 1.5 | 2 | 3 | 2.08 | 2 |
| **Total MVP** | | | | | **34.7 h PERT** | **34 h** |

### Ratio de reutilizacion y volumen
`R = (5+7+5+12) / 34 = 29/34 = 85.3%` → **Tier 1 (30%)**, aplicado por defecto (mismo criterio que la version anterior de este documento).
Volumen: Subtotal_lista = 34 x $16.80 = USD 571.20 → Tier V0 (<600, 0%) — irrelevante, `factor_tier = MAX(30%, 0%) = 30%`.

### Calculo de costo por item
| # | Item | M | USD lista | USD distribuido (x1.25) |
|---|---|---:|---:|---:|
| 1 | Usuarios y roles | 3 | 50.40 | 63.00 |
| 2 | Categorias + Clientes | 5 | 84.00 | 105.00 |
| 3 | Productos y Variantes | 7 | 117.60 | 147.00 |
| 4 | Stock | 5 | 84.00 | 105.00 |
| 5 | Ventas con cobro + cuotas | 12 | 201.60 | 252.00 |
| 6 | Puesta en marcha | 2 | 33.60 | 42.00 |
| **Subtotal_lista MVP** | | **34** | **571.20** | **714.00** |

- Subtotal distribuido: USD 714.00
- Descuento por eficiencia de desarrollo (30%): USD 571.20 x 0.30 = USD 171.36 → **-USD 171**
- **Total Propuesta MVP: USD 543** (714 - 171)

### Mantenimiento MVP
Tablas de negocio: Categoria, Cliente, Producto, VarianteProducto, Stock, MovimientoStock, Venta, VentaItem, VentaPago = 9 tablas → **PRO (6-15 tablas), USD 400/año**. Sin cargo por usuarios (4, muy por debajo del piso de 10).

---

## Propuesta Full (con facturación electrónica AFIP/ARCA)

### WBS
| # | Item | Clasificacion |
|---|---|---|
| 1 | Usuarios y roles (4 personas) | Modulo nuevo — ABM simple |
| 2 | Categorias + Clientes + Proveedores | **Reutilizacion de patron real** — ShowroomGriffin |
| 3 | Productos y Variantes | **Reutilizacion de patron real** — ShowroomGriffin |
| 4 | Stock | **Reutilizacion de patron real** — ShowroomGriffin |
| 5 | Compras a proveedores | **Reutilizacion de patron real** — ShowroomGriffin |
| 6 | Ventas con cobro multi-medio y cuotas | **Reutilizacion de patron real** — ShowroomGriffin |
| 7 | Devoluciones y cambios (wizard 3 tipos) | **Reutilizacion de patron real** — ShowroomGriffin |
| 8 | Aumento masivo de precios | **Reutilizacion de patron real** — ShowroomGriffin |
| 9 | **Facturacion electronica AFIP/ARCA (WSAA+WSFEv1)** | **Reutilizacion de patron real** — PAT-006, `marihogar`, produccion real con CAE |
| 10 | Resumen de ventas / reportes basicos | Modulo nuevo — reporte simple |
| 11 | Dashboard | Modulo nuevo — UI simple |
| 12 | Puesta en marcha (deploy + alta AFIP) | Deploy inicial + alta AFIP especifica |

### Estimaciones PERT
| # | Item | O | M | P | PERT | M usado |
|---|---|---:|---:|---:|---:|---:|
| 1 | Usuarios y roles | 2 | 3 | 4 | 3.00 | 3 |
| 2 | Categorias + Clientes + Proveedores | 5 | 7 | 10 | 7.17 | 7 |
| 3 | Productos y Variantes | 5 | 7 | 10 | 7.17 | 7 |
| 4 | Stock | 3.5 | 5 | 7 | 5.08 | 5 |
| 5 | Compras a proveedores | 4 | 6 | 9 | 6.17 | 6 |
| 6 | Ventas con cobro + cuotas | 9 | 12 | 17 | 12.33 | 12 |
| 7 | Devoluciones y cambios | 3.5 | 5 | 8 | 5.25 | 5 |
| 8 | Aumento masivo de precios | 2 | 3 | 4 | 3.00 | 3 |
| 9 | Facturacion AFIP/ARCA (reuso PAT-006) | 3 | 5 | 7 | 5.00 | 5 |
| 10 | Resumen / reportes | 1.5 | 2 | 3 | 2.08 | 2 |
| 11 | Dashboard | 1.5 | 2 | 3 | 2.08 | 2 |
| 12 | Puesta en marcha + alta AFIP | 2 | 3 | 4 | 3.00 | 3 |
| **Total Full** | | | | | **60.3 h PERT** | **60 h** |

### Ratio de reutilizacion y volumen
`R = (7+7+5+6+12+5+3+5) / 60 = 50/60 = 83.3%` → **Tier 1 (30%)**.
Volumen: Subtotal_lista = 60 x $16.80 = USD 1008.00 → Tier V1 (5%) — irrelevante, `factor_tier = MAX(30%, 5%) = 30%`.

### Calculo de costo por item
| # | Item | M | USD lista | USD distribuido (x1.25) |
|---|---|---:|---:|---:|
| 1 | Usuarios y roles | 3 | 50.40 | 63.00 |
| 2 | Categorias + Clientes + Proveedores | 7 | 117.60 | 147.00 |
| 3 | Productos y Variantes | 7 | 117.60 | 147.00 |
| 4 | Stock | 5 | 84.00 | 105.00 |
| 5 | Compras a proveedores | 6 | 100.80 | 126.00 |
| 6 | Ventas con cobro + cuotas | 12 | 201.60 | 252.00 |
| 7 | Devoluciones y cambios | 5 | 84.00 | 105.00 |
| 8 | Aumento masivo de precios | 3 | 50.40 | 63.00 |
| 9 | Facturacion AFIP/ARCA | 5 | 84.00 | 105.00 |
| 10 | Resumen / reportes | 2 | 33.60 | 42.00 |
| 11 | Dashboard | 2 | 33.60 | 42.00 |
| 12 | Puesta en marcha | 3 | 50.40 | 63.00 |
| **Subtotal_lista Full** | | **60** | **1008.00** | **1260.00** |

- Subtotal distribuido: USD 1260.00
- Descuento por eficiencia de desarrollo (30%): USD 1008.00 x 0.30 = USD 302.40 → **-USD 302**
- **Total Propuesta Full: USD 958** (1260 - 302)

### Mantenimiento Full
Tablas de negocio: las 9 del MVP + Proveedor, Compra, CompraItem, Devolucion, Comprobante, ComprobanteItem = 15 tablas → **todavia dentro de PRO (6-15, limite superior), USD 400/año**. Mismo plan que el MVP — no cambia por agregar AFIP/Compras/Devoluciones, porque el limite de PRO (15) justo alcanza. Sin cargo por usuarios (4, bajo el piso de 10).

---

### Costo interno de IA (dato exclusivamente interno)
**MVP:** Horas facturables = 34/2.5x1.20=16.32h. Costo_IA=16.32x$4=USD 65.28 + overhead USD 4 ≈ **USD 69.28** — bajo Tokens IA (USD 142.80).
**Full:** Horas facturables = 60/2.5x1.20=28.8h. Costo_IA=28.8x$4=USD 115.20 + overhead USD 4 ≈ **USD 119.20** — bajo Tokens IA (USD 252.00). Item mas caro en ambas (Ventas, M=12): 11.4% del precio de lista, bajo el umbral 15%.

### Cierre estimado vs real (si disponible)
No disponible — proyecto en etapa de propuesta. Pendiente confirmar en demo: si "papel" es correcto (reconstruccion de la respuesta "2"), volumen real de catalogo, reparto de roles entre las 4 personas, y si de verdad hace falta facturacion AFIP (no mencionada como pain point, agregada a pedido explicito para la propuesta Full).

## Historial de ajustes
- 2026-08-27: primera version (propuesta unica, 11 items, USD 878 + mantenimiento mal clasificado como PREMIUM).
- 2026-08-27: aplicada regla de estudio "sin cargo por usuario hasta 10" — mantenimiento baja a PREMIUM sin cargo extra (USD 500/año), sin corregir todavia el error de clasificacion por tablas.
- 2026-08-27: **reestructurado en dos propuestas de implementacion (MVP y Full con AFIP)** a pedido explicito de Joaquin, y **corregido el error de clasificacion de mantenimiento** (era PREMIUM por razonar desde usuarios, corresponde PRO por cantidad real de tablas en ambas propuestas). Propuesta MVP: **USD 543** desarrollo + PRO USD 400/año. Propuesta Full: **USD 958** desarrollo (agrega Compras, Devoluciones, Aumento masivo, Reportes, Dashboard y Facturacion AFIP/ARCA vía PAT-006) + PRO USD 400/año (mismo plan, el limite superior de PRO todavia alcanza).
- 2026-08-27: aplicada la nueva regla de estudio "año 1 de mantenimiento gratis SIEMPRE default" (reemplaza "solo ante objecion de precio", ver `27-presupuesto-parametros.instructions.md`). Mantenimiento de ambas propuestas: **PRO, año 1 gratis, USD 400/año desde el año 2**. Desarrollo sin cambios.
