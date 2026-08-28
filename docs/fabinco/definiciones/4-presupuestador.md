# Memoria - Presupuestador

## Proyecto: fabinco
## Ultima actualizacion: 2026-08-26

## Definiciones vigentes

### Consulta estrategica previa (olvidata-ceo, 2026-08-26)
Antes de fijar numeros, se consulto explicitamente al agente `olvidata-ceo` dado el perfil de FABINCO (B2B, 50 años de trayectoria, produccion propia) — muy distinto de los leads chicos recientes (dietéticas). Recomendacion recibida, aplicada integramente en este documento:

1. **NO aplicar el descuento de expansion agresiva (Tier 1, 30% + año gratis).** Motivo: ese descuento existe para acelerar cierre de clientes chicos de bajo ticket donde el precio es la barrera — FABINCO ya paga por un "otro sistema" hoy, tiene presupuesto asignado a software y capacidad de pago real. Regalar precio aca es margen tirado, no palanca de cierre. Tratar como **Build a medida a precio de lista**, no como Rent de catalogo con descuento.
2. **Sondear en la demo, no asumir en el presupuesto base**: gestion de presupuestos/cotizaciones B2B (probablemente el cuello de botella real, dado que venden "por sistema de presupuesto, no e-commerce") y trazabilidad de produccion propia (corte y confeccion). Si se confirma cualquiera, el proyecto pasa de "catalogo indumentaria estandar" a alcance a medida — no forzarlo al molde de ShowroomGriffin sin confirmar primero.
3. **Mantenimiento: PREMIUM como piso tecnico** (no PRO) — con 3 usuarios declarados, PRO (tope 2 usuarios incluidos) ya no alcanza; PREMIUM (USD 500/año, hasta 3 usuarios) es mas barato que PRO+1 usuario adicional (400+125=525) para este numero exacto de usuarios. **Sin año de mantenimiento gratis** — mismo criterio que el punto 1, no hace falta el incentivo para cerrar.

### WBS funcional vigente — alcance base (anclado en ShowroomGriffin, codigo real)

| # | Item | Clasificacion |
|---|---|---|
| 1 | Usuarios y roles (3 personas: Administracion/Vendedor/Deposito) | Modulo nuevo — ABM simple |
| 2 | Clientes (B2B), Proveedores, Categorias/Subgrupos | **Reutilizacion de patron real** — adaptado del Maestros Comerciales de ShowroomGriffin, con Cliente reescrito a perfil empresa |
| 3 | Productos y Variantes (Color/Talle) | **Reutilizacion de patron real** — ShowroomGriffin (RowVersion, formulario dinamico, SKU/codigo unico ya resuelto) |
| 4 | Stock por variante (alertas, ajustes, MovimientoStock) | **Reutilizacion de patron real** — ShowroomGriffin |
| 5 | Compras a proveedores (con workflow de estados) | **Reutilizacion de patron real** — ShowroomGriffin (PAT-005) |
| 6 | Ventas con cobro multi-medio y cuotas (PAT-003) | **Reutilizacion de patron real** — ShowroomGriffin |
| 7 | Devoluciones y cambios (wizard 3 tipos) | **Reutilizacion de patron real** — ShowroomGriffin |
| 8 | Aumento masivo de precios | **Reutilizacion de patron real** — ShowroomGriffin |
| 9 | Resumen de ventas / reportes basicos | Modulo nuevo — reporte simple |
| 10 | Dashboard | Modulo nuevo — UI simple |
| 11 | Puesta en marcha | Deploy inicial |

**Fuera del alcance base (a confirmar en demo, no presupuestado aca):** gestion de presupuestos/cotizaciones B2B, trazabilidad de produccion propia, integracion AFIP (si resulta que hace falta).

### Estimaciones PERT — M ya reducido por reutilizacion real de codigo (no por descuento de precio)

Importante: el M de cada item YA refleja la eficiencia real de portar codigo entregado de ShowroomGriffin (mucho mas bajo que si se construyera desde cero) — esto es distinto y no se mezcla con el descuento de expansion agresiva (que aca no se aplica, ver arriba). Comparar contra el M original de ShowroomGriffin (entre parentesis) para ver el ahorro real de reutilizacion.

| # | Item | O | M | P | PERT | M usado | M original ShowroomGriffin |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Usuarios y roles | 2 | 3 | 4 | 3.00 | 3 | 1.5 |
| 2 | Clientes B2B + Proveedores + Categorias | 6 | 8 | 12 | 8.33 | 8 | 18.0 |
| 3 | Productos y Variantes | 4 | 6 | 9 | 6.17 | 6 | 10.0 |
| 4 | Stock por variante | 3.5 | 5 | 7 | 5.08 | 5 | 8.0 |
| 5 | Compras a proveedores | 4 | 6 | 9 | 6.17 | 6 | 10.0 |
| 6 | Ventas con cobro + cuotas | 9 | 12 | 17 | 12.33 | 12 | 18.0 |
| 7 | Devoluciones y cambios | 3.5 | 5 | 8 | 5.25 | 5 | 8.0 |
| 8 | Aumento masivo de precios | 2 | 3 | 4 | 3.00 | 3 | 4.0 |
| 9 | Resumen / reportes | 1.5 | 2 | 3 | 2.08 | 2 | 2.0 |
| 10 | Dashboard | 1.5 | 2 | 3 | 2.08 | 2 | 2.0 |
| 11 | Puesta en marcha | 2 | 3 | 4 | 3.00 | 3 | — |
| **Total** | | | | | **56.5 h PERT** | **55 h** | **84.5 h (referencia)** |

Ratio M/M-original = 55/84.5 = **0.65** — ahorro real del 35% frente a construir el mismo alcance desde cero, explicado enteramente por reutilizacion de codigo real (ShowroomGriffin), no por un descuento de precio.

### Autocorreccion contra historicos
Comparable directo: ShowroomGriffin (84.5h M base, mismo alcance funcional casi exacto). El ratio 0.65 esta dentro de un rango razonable para reutilizacion de codigo real cross-proyecto (no tan agresivo como el 0.67-0.76 de labipac SESION 3, que era reutilizacion DENTRO del mismo proyecto — aca es cross-proyecto, con mas trabajo de adaptacion esperado). Sin alertas adicionales.

### Ratio de reutilizacion (R) — calculado pero NO usado para descuento (ver override CEO arriba)
Items 2-8 (7 de 11) estan anclados en reutilizacion de codigo REAL entregado (ShowroomGriffin) — a diferencia de las dietéticas, aca la mayoria del sistema es reutilizacion genuina, no solo un modulo chico (AFIP). `R = (8+6+5+6+12+5+3) / 55 = 45/55 = 81.8%` — **Tier 1 por calculo objetivo** (R >= 70%). Sin embargo, por la recomendacion explicita de `olvidata-ceo` (ver arriba), **NO se aplica el descuento de Tier 1 a este cliente** — es un override en sentido inverso al usado con audifonos-bariloche/desborder-sin-gluten/dietetica-mitre (ahi se pisaba un R bajo para SUBIR al Tier 1; aca se pisa un R alto para NO bajar el precio). Documentado explicitamente para no confundir con un error de calculo: la formula califica objetivamente para el descuento, la decision de negocio dice que no corresponde dárselo a este perfil de cliente.

### Descuento por volumen del proyecto — tampoco aplicado
Subtotal_lista = 55 x $16.80 = USD 924.00 → cae en **Tier V1 (600-1.200), 5% por formula** — igualmente NO aplicado, mismo criterio de override que arriba (precio de lista completo, sin ningun descuento).

### Calculo de costo por item (precio de lista, SIN descuento)

| # | Item | M | USD lista | USD distribuido (x1.25, Tokens IA plegado) |
|---|---|---:|---:|---:|
| 1 | Usuarios y roles | 3 | 50.40 | 63.00 |
| 2 | Clientes B2B + Proveedores + Categorias | 8 | 134.40 | 168.00 |
| 3 | Productos y Variantes | 6 | 100.80 | 126.00 |
| 4 | Stock por variante | 5 | 84.00 | 105.00 |
| 5 | Compras a proveedores | 6 | 100.80 | 126.00 |
| 6 | Ventas con cobro + cuotas | 12 | 201.60 | 252.00 |
| 7 | Devoluciones y cambios | 5 | 84.00 | 105.00 |
| 8 | Aumento masivo de precios | 3 | 50.40 | 63.00 |
| 9 | Resumen / reportes | 2 | 33.60 | 42.00 |
| 10 | Dashboard | 2 | 33.60 | 42.00 |
| 11 | Puesta en marcha | 3 | 50.40 | 63.00 |
| **Total** | | **55** | **924.00** | **1155.00** |

Tokens IA (25% de Subtotal_lista): USD 924.00 x 0.25 = USD 231.00 — ya plegado en la columna distribuida (factor x1.25).

**Total del proyecto: USD 1155** — sin linea de descuento (a diferencia de todos los leads recientes). Piso absoluto USD 280 — muy por encima, no aplica ni es relevante en este perfil de cliente.

### Plan de mantenimiento anual
Tablas de negocio estimadas: ~11-12 (Cliente, Proveedor, Categoria, Subgrupo, Producto, VarianteProducto, Stock/MovimientoStock, Compra/CompraItem, Venta/VentaItem/VentaPago, Devolucion) → **PREMIUM (16-30 tablas)** por techo tecnico de usuarios en realidad, no por cantidad de tablas (que calificaria PRO) — con 3 usuarios declarados, PRO (tope 2 incluidos) no alcanza, y PREMIUM (USD 500/año, hasta 3 usuarios, soporte prioritario, 2 rondas de ajuste) sale mas barato que PRO + 1 usuario adicional (400+125=525). **Sin año gratis** (override explicito de CEO, ver arriba).

**Plan de mantenimiento: PREMIUM, USD 500/año, desde el arranque (sin promocion de año 1).**

### Costo interno de IA (dato exclusivamente interno)
Horas facturables = 55/2.5 x 1.20 = 26.4h. Costo_IA_modulos = 26.4 x $4 = USD 105.60. Overhead = USD 4. Total ≈ USD 109.60 — muy por debajo de Tokens IA (USD 231.00). Item mas caro (Ventas, M=12): horas fact.=12/2.5x1.2=5.76h → USD 23.04 sobre USD 201.60 lista → 11.4%, bajo el umbral 15%. Sin ajuste necesario.

### Cierre estimado vs real (si disponible)
No disponible — proyecto en etapa de propuesta, sin aprobacion del lead todavia. Pendiente confirmar en demo: alcance de presupuestos/cotizaciones B2B y produccion propia (si se confirma cualquiera, requiere reestimacion como alcance adicional, no ajuste menor), y si hace falta facturacion electronica AFIP (PAT-006 disponible si aplica).

## Historial de ajustes
- 2026-08-26: primera version. Alcance base anclado en ShowroomGriffin (codigo real, mayor reutilizacion real confirmada del historial — R=81.8%), pero **sin aplicar el descuento de expansion agresiva ni el de volumen** por recomendacion estrategica explicita de `olvidata-ceo` (perfil B2B de 50 años, capacidad de pago real, no necesita incentivo de precio para cerrar). Total: **USD 1155** desarrollo + **PREMIUM USD 500/año** mantenimiento (sin año gratis) — el presupuesto de mayor valor cotizado en el historial reciente del estudio, reflejando el perfil de cliente distinto.
