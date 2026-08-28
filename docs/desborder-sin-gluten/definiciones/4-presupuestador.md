# Memoria - Presupuestador

## Proyecto: desborder-sin-gluten
## Ultima actualizacion: 2026-08-25

## Definiciones vigentes

### Nota metodologica: dos propuestas, misma tasa/formula, B es subconjunto de A
Ambas se calculan con la formula vigente (Costo = M x $16.80, tasa USD 35/h, contingencia 20% incluida). Ninguna es un "presupuesto alternativo" independiente en el sentido de estudio-contable-maribel-garcia (PHP vs .NET, dos arquitecturas distintas) — aca B es literalmente el subconjunto de items de A que resuelve el dolor mas urgente (facturacion). Por eso los items compartidos (Comprobante, AFIP, Catalogo simple, Usuarios) tienen el MISMO M en ambas tablas.

### Propuesta B — Solo modulo de facturacion electronica

| # | Item | Clasificacion |
|---|---|---|
| 1 | Usuarios y roles (Administracion / Vendedor si aplica) | Modulo nuevo — ABM simple |
| 2 | Catalogo simple de productos/conceptos a facturar (sin stock) | Modulo nuevo — ABM simple |
| 3 | Emision de comprobantes (formulario, calculo de IVA por item) | Modulo nuevo — ABM intermedio |
| 4 | Integracion AFIP/ARCA (WSAA+WSFEv1) | **Reutilizacion real** — AfipService de marihogar (PAT-006), codigo en produccion |
| 5 | Historial de comprobantes + reimpresion PDF con QR | Modulo nuevo — reporte/listado simple |
| 6 | Puesta en marcha (deploy + alta de certificado AFIP + Punto de Venta) | Deploy inicial + alta AFIP especifica |

#### Estimaciones PERT — Propuesta B

| # | Item | O | M | P | PERT | M usado |
|---|---|---:|---:|---:|---:|---:|
| 1 | Usuarios y roles | 1.5 | 2 | 3 | 2.08 | 2 |
| 2 | Catalogo simple | 2 | 3 | 4 | 3.00 | 3 |
| 3 | Emision de comprobantes | 4 | 6 | 9 | 6.17 | 6 |
| 4 | Integracion AFIP (reuso) | 3 | 5 | 7 | 5.00 | 5 |
| 5 | Historial + reimpresion PDF | 2 | 3 | 4 | 3.00 | 3 |
| 6 | Puesta en marcha + alta AFIP | 2 | 3 | 4 | 3.00 | 3 |
| **Total Propuesta B** | | | | | **22.25 h PERT** | **22 h** |

Sin Etapa 2 — el alcance de B ya es minimo por diseño (no se subdivide mas).

### Propuesta A — Sistema integral de gestion (stock + ventas + facturacion + caja)

| # | Item | Etapa | Clasificacion |
|---|---|---|---|
| 1 | Usuarios y roles (Administracion / Vendedor) | 1 | Modulo nuevo — ABM simple |
| 2 | Productos (catalogo con stock) | 1 | Modulo nuevo — ABM intermedio |
| 3 | Stock (control, ajustes manuales, alertas) | 1 | Modulo nuevo — ABM intermedio + trazabilidad |
| 4 | Proveedores + Compras simples (sin workflow de estados) | 1 | Modulo nuevo — ABM intermedio |
| 5 | Ventas con cobro (PAT-003, carrito + pago dividido) | 1 | Modulo nuevo — financiero, **reutiliza patron PAT-003** (ShowroomGriffin) |
| 6 | Integracion AFIP/ARCA (WSAA+WSFEv1) | 1 | **Reutilizacion real** — PAT-006 (marihogar) |
| 7 | Cierre de caja automatico (resumen del dia por medio de pago) | 1 | Modulo nuevo — reporte simple |
| 8 | Dashboard simple (ventas del dia, stock bajo) | 1 | Modulo nuevo — UI simple |
| 9 | Puesta en marcha (deploy + alta AFIP) | 1 | Deploy inicial + alta AFIP especifica |
| 10 | Reportes basicos (ventas por periodo, mas vendidos) | 2 | Modulo nuevo — reporte/exportacion simple |

#### Estimaciones PERT — Propuesta A

| # | Item | O | M | P | PERT | M usado |
|---|---|---:|---:|---:|---:|---:|
| 1 | Usuarios y roles | 1.5 | 2 | 3 | 2.08 | 2 |
| 2 | Productos (con stock) | 3 | 4 | 6 | 4.17 | 4 |
| 3 | Stock (control + alertas) | 3.5 | 5 | 8 | 5.25 | 5 |
| 4 | Proveedores + Compras | 3.5 | 5 | 8 | 5.25 | 5 |
| 5 | Ventas con cobro (PAT-003) | 7 | 10 | 15 | 10.33 | 10 |
| 6 | Integracion AFIP (reuso) | 3 | 5 | 7 | 5.00 | 5 |
| 7 | Cierre de caja | 2.5 | 4 | 6 | 4.08 | 4 |
| 8 | Dashboard simple | 1.5 | 2 | 3 | 2.08 | 2 |
| 9 | Puesta en marcha + alta AFIP | 2 | 3 | 4 | 3.00 | 3 |
| **Subtotal Etapa 1** | | | | | **41.24 h PERT** | **40 h** |
| 10 | Reportes basicos | 1.5 | 2 | 3 | 2.08 | 2 |
| **Subtotal Etapa 2** | | | | | **2.08 h PERT** | **2 h** |
| **Total Propuesta A** | | | | | **43.3 h PERT** | **42 h (M)** |

### Autocorreccion contra historicos (obligatoria antes del cierre)
Referencia comparable elegida: **ShowroomGriffin** (retail, 9 modulos + dashboard + infra, M base 86.6h) — escalado hacia abajo por ser DesBorder un comercio mucho mas chico (dietetica de barrio vs. indumentaria con variantes Color/Talle) y sin 3 modulos que ShowroomGriffin si tiene (Devoluciones/wizard, Aumento masivo de precios, Maestros comerciales de 5 ABMs — DesBorder no necesita categorias/subgrupos/tipos de precio como catalogo separado, entra directo en Productos).

Ratio Propuesta A = 42h / 86.6h (ShowroomGriffin) = **0.48** — por debajo del umbral 0.85, dispara "revisar omisiones o justificar simplificacion real". **Justificacion:** DesBorder no tiene variantes de producto (Color/Talle), no tiene devoluciones/cambios con wizard de 3 tipos, no tiene aumento masivo de precios, y el modulo de Compras es una alta directa sin maquina de estados de 4 pasos (Borrador→EnProceso→Verificada→Recibida) como en ShowroomGriffin. La complejidad real es genuinamente menor, no una omision — se mantiene sin ajustar al alza.

Ademas, esta es la referencia mas comparable de dominio real: **delicias-naturales** (comercio de "naturales"/dietetica, 19 modulos, 95h base — proyecto de 2025, sin desglose por modulo disponible en formato estructurado). Aunque no hay tabla item-por-item para comparar, el hecho de que ese proyecto historico haya llegado a 19 modulos para un negocio similar sugiere que el alcance de Propuesta A (9-10 items) es deliberadamente MAS chico — coherente con que DesBorder pidio explicitamente una opcion acotada (Propuesta B) ademas de la integral, señal de que no busca un sistema tan extenso como el de delicias-naturales.

### Ratio de reutilizacion (R) — descuento de expansion agresiva

**Propuesta B:** R = M reutilizacion / M total = 5 (item 4, AFIP) / 22 = **22.7%** → Tier 3 (R < 40%), 0% descuento.

**Propuesta A:** R = 5 (item 6, AFIP) / 42 = **11.9%** → Tier 3 (R < 40%), 0% descuento. *(Nota: el modulo de Ventas (item 5) reutiliza el PATRON PAT-003 pero no es un lift-and-adapt casi completo como AFIP — construir el carrito/checkout especifico de DesBorder sigue siendo trabajo real, por eso NO se cuenta como M de reutilizacion en este calculo, mismo criterio conservador aplicado en audifonos-bariloche/cma-centro-medico.)*

Ninguna propuesta alcanza Tier 1/2 de descuento por reutilizacion segun el calculo objetivo — pese a ser el proyecto con MAS reutilizacion de codigo real confirmado del historial, el ratio numerico R queda bajo porque el modulo de AFIP (que es el 100% real de esa reutilizacion) es chico en horas relativas al resto del sistema. Esto es una limitacion conocida de la formula R actual (mide horas de reuso, no valor/riesgo evitado).

**[OVERRIDE 2026-08-25, pedido explicito de Joaquin]:** aplicar el descuento de expansion agresiva **Tier 1 (30%)** en ambas propuestas, pisando el calculo objetivo de R (mismo mecanismo ya usado en audifonos-bariloche 2026-08-19, donde R=14.3%/Tier 3 fue pisado a Tier 1 por decision explicita). Justificacion de elegibilidad: es Build inicial de cliente nuevo (elegible por regla), el tablero de ciclos economicos sigue en verde/amarillo (checkpoint duro octubre 2027, no llego), y el objetivo declarado es dejar el precio a nivel de "valor de referido" para maximizar la probabilidad de cierre de un lead frio de ticket bajo. No se recalculo R para justificar artificialmente el tier — se documenta como decision de negocio que pisa el numero, igual criterio que audifonos-bariloche.

`factor_tier` Propuesta B = MAX(30% override, 0% volumen) = **30%**.
`factor_tier` Propuesta A = MAX(30% override, 5% volumen) = **30%**.

### Descuento por volumen del proyecto

**Propuesta B:** Subtotal_lista = 22 x $16.80 = **USD 369.60** → Tier V0 (< USD 600) → 0% descuento por volumen.

**Propuesta A:** Subtotal_lista = 42 x $16.80 = **USD 705.60** → Tier V1 (USD 600-1.200) → 5% descuento por volumen.

Ver override de Tier 1 (30%) en la seccion anterior — el `factor_tier` final de ambas propuestas queda en 30%, no en estos valores por volumen (que hubieran quedado por debajo del override de todas formas via MAX).

### Tasa vigente y contingencia aplicada
Tasa USD 35/h, formula Costo = M x $16.80 (contingencia 20% ya incluida). Riesgo: **medio** en ambas — la pieza de mayor riesgo tecnico (AFIP) esta mitigada por ser reutilizacion de un patron ya depurado en produccion real (no exploracion desde cero), reflejado en el M=5 (por debajo del rango generico de 7-9h de integracion AFIP nueva).

### Calculo de costo por item

**Propuesta B (Costo = M x $16.80):**

| # | Item | M | USD lista |
|---|---|---:|---:|
| 1 | Usuarios y roles | 2 | 33.60 |
| 2 | Catalogo simple | 3 | 50.40 |
| 3 | Emision de comprobantes | 6 | 100.80 |
| 4 | Integracion AFIP (reuso) | 5 | 84.00 |
| 5 | Historial + reimpresion | 3 | 50.40 |
| 6 | Puesta en marcha + alta AFIP | 3 | 50.40 |
| **Subtotal_lista B** | | **22** | **369.60** |

**Propuesta A:**

| # | Item | M | USD lista |
|---|---|---:|---:|
| 1 | Usuarios y roles | 2 | 33.60 |
| 2 | Productos (con stock) | 4 | 67.20 |
| 3 | Stock | 5 | 84.00 |
| 4 | Proveedores + Compras | 5 | 84.00 |
| 5 | Ventas con cobro (PAT-003) | 10 | 168.00 |
| 6 | Integracion AFIP (reuso) | 5 | 84.00 |
| 7 | Cierre de caja | 4 | 67.20 |
| 8 | Dashboard simple | 2 | 33.60 |
| 9 | Puesta en marcha + alta AFIP | 3 | 50.40 |
| **Subtotal Etapa 1** | | **40** | **672.00** |
| 10 | Reportes basicos | 2 | 33.60 |
| **Subtotal Etapa 2** | | **2** | **33.60** |
| **Subtotal_lista A** | | **42** | **705.60** |

### Precios distribuidos al cliente (factor x1.25, Tokens IA plegado)

**Propuesta B (con descuento Tier 1 override, 30%):**

| # | Item | USD lista | USD distribuido (x1.25) |
|---|---|---:|---:|
| 1 | Usuarios y roles | 33.60 | 42.00 |
| 2 | Catalogo simple | 50.40 | 63.00 |
| 3 | Emision de comprobantes | 100.80 | 126.00 |
| 4 | Integracion AFIP | 84.00 | 105.00 |
| 5 | Historial + reimpresion | 50.40 | 63.00 |
| 6 | Puesta en marcha | 50.40 | 63.00 |
| **Total distribuido B** | | **369.60** | **462.00** |

Descuento formal (Tier 1, 30% sobre Subtotal_lista sin tokens): USD 369.60 x 0.30 = USD 110.88 → hubiera dado USD 351. **Numero final fijado por Joaquin: USD 400** (descuento efectivo sobre el Subtotal distribuido de 462.00 pasa a -USD 62, ~16.8% — por debajo del 30% formal, decision comercial directa, no recalculo de formula).

**Total Propuesta B = USD 400** (462.00 - 62 = 400).

**Propuesta A (con descuento Tier 1 override, 30%):**

| # | Item | USD lista | USD distribuido (x1.25) |
|---|---|---:|---:|
| 1 | Usuarios y roles | 33.60 | 42.00 |
| 2 | Productos | 67.20 | 84.00 |
| 3 | Stock | 84.00 | 105.00 |
| 4 | Proveedores + Compras | 84.00 | 105.00 |
| 5 | Ventas con cobro | 168.00 | 210.00 |
| 6 | Integracion AFIP | 84.00 | 105.00 |
| 7 | Cierre de caja | 67.20 | 84.00 |
| 8 | Dashboard | 33.60 | 42.00 |
| 9 | Puesta en marcha | 50.40 | 63.00 |
| **Subtotal Etapa 1 distribuido** | | **672.00** | **840.00** |
| 10 | Reportes basicos | 33.60 | 42.00 |
| **Subtotal Etapa 2 distribuido** | | **33.60** | **42.00** |
| **Subtotal distribuido A** | | **705.60** | **882.00** |

Descuento formal (Tier 1, 30% sobre Subtotal_lista sin tokens): USD 705.60 x 0.30 = USD 211.68 → hubiera dado USD 670. **Numero final fijado por Joaquin: USD 650** (descuento efectivo sobre el Subtotal distribuido de 882.00 pasa a -USD 232, ~32.9% — levemente por encima del 30% formal, decision comercial directa).

**Total Propuesta A = USD 650** (882.00 - 232 = 650).

**Piso absoluto USD 280:** ambos totales quedan por encima (B: 400, A: 650) — no se activa.

### Plan de mantenimiento anual

**Propuesta B:** 2 tablas de negocio (`Comprobante`, `ComprobanteItem`) → **STARTER (1-5 tablas), USD 300/año, 1 admin incluido**. Si son 2 personas (ver ambiguedad "1 o 2" en `1-analista-funcional.md`), sumar 1 usuario adicional x USD 125/año → **USD 425/año**.

**Propuesta A:** 8 tablas de negocio (`Comprobante`, `ComprobanteItem`, `Producto`, `Proveedor`, `Compra`, `CompraItem`, `Venta`, `VentaItem`+`VentaPago` cuentan como 2 pero se agrupan como "modulo Venta" a efectos de plan — 8-9 segun como se cuenten las tablas de detalle) → **PRO (6-15 tablas), USD 400/año, hasta 2 usuarios incluidos**. Con "1 o 2 personas" declaradas, **PRO cubre sin upsell** — USD 400/año sin cargo adicional.

**Nota comercial (research de mercado, ver `1-analista-funcional.md`):** un sistema de punto de venta generico comparable (POS Gestion 4.0) ronda USD 130-155/año en el mercado argentino actual (ARS 16.585-18.985/mes). El plan PRO de Olvidata (USD 400/año) es mas caro en terminos absolutos, pero incluye soporte por WhatsApp + 1 ronda de ajuste anual + un sistema hecho a medida (no una licencia generica fija) — diferencia a explicar honestamente en el documento cliente, no a ocultar.

### Costo interno de IA (dato exclusivamente interno, no aparece en presupuesto-cliente.md)

**Propuesta B:** Horas facturables = 22/2.5 x 1.20 = 10.56h. Costo_IA_modulos = 10.56 x $4 = USD 42.24. Overhead = 4h x $1 = USD 4. Total ≈ **USD 46.24** — muy por debajo de Tokens IA (USD 92.40). Item mas caro (Emision de comprobantes, M=6): horas fact.=6/2.5x1.2=2.88h → USD 11.52 sobre USD 100.80 lista → 11.4%, bajo el umbral 15%.

**Propuesta A:** Horas facturables = 42/2.5 x 1.20 = 20.16h. Costo_IA_modulos = 20.16 x $4 = USD 80.64. Overhead = USD 4. Total ≈ **USD 84.64** — muy por debajo de Tokens IA (USD 176.40). Item mas caro (Ventas, M=10): horas fact.=10/2.5x1.2=4.8h → USD 19.20 sobre USD 168.00 lista → 11.4%, bajo el umbral. Ningun item de ninguna propuesta supera el 15% — sin ajuste de precio por modulo necesario.

### Calibraciones historicas usadas
- ShowroomGriffin (86.6h base, 9 modulos retail) — ratio 0.48 para Propuesta A, justificado por menor complejidad real (sin variantes, sin devoluciones, sin aumento masivo).
- delicias-naturales (95h base, 19 modulos, mismo dominio de "naturales"/dietetica) — confirma que el estudio ya resolvio este tipo de negocio antes; Propuesta A es deliberadamente mas chica en alcance.
- PAT-006 (marihogar, AFIP en produccion real) — M=5h para integracion AFIP en ambas propuestas, por debajo del rango generico de 7-9h por ser reutilizacion documentada, no construccion desde cero.

### Cierre estimado vs real (si disponible)
No disponible — proyecto en etapa de propuesta, sin aprobacion del lead todavia. Discovery con respuestas fuera de orden (ver `1-analista-funcional.md`) — alta probabilidad de ajuste tras la demo, especialmente sobre la condicion fiscal (Monotributo/RI) y el numero real de usuarios.

## Historial de ajustes
- 2026-08-25: primera version. Propuesta B: USD 462 desarrollo + STARTER USD 300-425/año (segun 1 o 2 usuarios). Propuesta A: USD 847 desarrollo + PRO USD 400/año (sin upsell, cubre hasta 2 usuarios). B definida como subconjunto exacto de A, no alternativa aislada — mismo M en los items compartidos (Usuarios, Catalogo/Productos, AFIP).
- 2026-08-25: aplicado override de descuento de expansion agresiva Tier 1 (30%) a pedido explicito de Joaquin, pisando el calculo objetivo de R (Tier 3 en ambas propuestas) — mismo mecanismo que audifonos-bariloche 2026-08-19. Mantenimiento SIN cambios (la politica excluye explicitamente el mantenimiento del descuento). Nuevos totales de desarrollo: **Propuesta B USD 462 → USD 351** (-111), **Propuesta A USD 847 → USD 670** (-212). `presupuesto-cliente.md` actualizado con la linea de descuento explicita en ambas opciones.
- 2026-08-26: numero final de Propuesta B ajustado por Joaquin de USD 351 a **USD 350** (redondeo a numero mas limpio, descuento pasa de -111 a -112). Propuesta A sin cambios (USD 670). Mensaje enviado al lead con estos numeros.
- 2026-08-26: **corregido por Joaquin** — Propuesta B final pasa de USD 350 a **USD 400** (numero comercial fijado directamente, no recalculado por formula — descuento efectivo sobre Subtotal distribuido de 462 pasa a -USD 62, ~16.8% en vez del 30% formal; mismo criterio que Ganaderia/Luciano Inmobiliaria: "numeros finales fijados por Joaquin" pisa el resultado de la formula). **Ademas, decision comercial nueva: primer año de mantenimiento GRATIS en ambas opciones** (mismo playbook que la ferreteria 2026-07-29, ver seccion "aclaracion sobre objecion de precio" de `27-presupuesto-parametros.instructions.md`) — desde el año 2, el plan que corresponda a precio de lista sin cambios (STARTER 300/425 para B, PRO 400 para A). `presupuesto-cliente.md` actualizado: tabla de mantenimiento reestructurada con columnas "Año 1" (Gratis) / "Desde el año 2" (precio de lista).
- 2026-08-26: **corregido por Joaquin** — Propuesta A final pasa de USD 670 a **USD 650** (numero comercial fijado directamente, mismo criterio que arriba — descuento efectivo sobre Subtotal distribuido de 882 pasa a -USD 232, ~32.9% en vez del 30% formal exacto).
