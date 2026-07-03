# Reporte de Dashboards e Indicadores Comerciales — Delicias Naturales

**Para:** CEO / Dirección comercial
**Fecha:** 01/07/2026
**Período analizado:** enero a junio 2026 (6 meses completos). Julio se muestra aparte por estar recién comenzando.
**Fuente:** base de datos de producción del sistema, consulta directa de solo lectura al cierre del período.

---

## 1. Qué mide cada indicador del dashboard y para qué sirve

El sistema muestra los indicadores agrupados en 6 pantallas. Acá se explica qué significa cada uno y qué decisión comercial ayuda a tomar — no es un detalle técnico, es la lectura de negocio.

### Ventas
| Indicador | Qué significa | Para qué sirve en la práctica |
|---|---|---|
| Total Facturado | Todo lo vendido en el período | Saber si el negocio está creciendo o achicándose mes a mes |
| Total Cobrado | Plata que efectivamente entró | Diferencia entre "vender" y "cobrar" — clave para planificar caja |
| Total Pendiente | Lo vendido que todavía no se cobró | Alerta temprana de problemas de cobranza |
| Cantidad de Ventas | Número de operaciones | Si sube el monto pero baja la cantidad, están vendiendo menos veces pero más caro (o al revés) |
| Ticket Promedio | Facturado ÷ cantidad de ventas | Sirve para ver si el cliente promedio compra más o menos por operación |
| Variación vs período anterior | Compara el mes contra el mes anterior | Detecta tendencias sin tener que mirar números sueltos |
| Distribución por método de pago | Cuánto entra por efectivo, transferencia, tarjeta, etc. | Decide con qué medios de pago conviene negociar descuentos o costos financieros |

### Productos
| Indicador | Qué significa | Para qué sirve en la práctica |
|---|---|---|
| Producto Más Vendido / Mayor Facturación | Los que más mueven volumen o plata | Asegurar que nunca falte stock de esos productos |
| Producto Menor Rotación / Sin Ventas | Productos que casi no se venden | Candidatos a sacar del catálogo, liquidar o dejar de comprar |
| Margen Promedio Ponderado | Rentabilidad promedio pesada por lo que realmente se vende | Mejor que un promedio simple: refleja la ganancia real de la mezcla de ventas |
| Stock Crítico (Top Vendidos) | Productos que se venden mucho y están por quedarse sin stock | Evita perder ventas por falta de mercadería |

### Rentabilidad
| Indicador | Qué significa | Para qué sirve en la práctica |
|---|---|---|
| Costo Total | Lo que salió comprar/producir lo vendido | Base para saber cuánto queda de ganancia real, no solo facturación |
| Ganancia Bruta y Margen % | Facturado menos costo, en pesos y en porcentaje | El número más importante para saber si el negocio es rentable, más allá de cuánto se vende |
| Alerta de Venta Bajo Costo | Avisa si algún producto se vendió perdiendo plata | Corrige errores de precios antes de que se repitan |
| Top Productos por Ganancia | Los que más aportan a la ganancia (no necesariamente los más vendidos) | Prioriza qué productos empujar comercialmente |

### Pedidos
| Indicador | Qué significa | Para qué sirve en la práctica |
|---|---|---|
| Tasa de Conversión | De los pedidos que entran, cuántos terminan siendo una venta real | Mide qué tan bien está funcionando el proceso comercial/atención |
| Pedidos Pendientes | Pedidos que todavía no se resolvieron | Evita que un cliente quede esperando sin respuesta |

### Clientes
| Indicador | Qué significa | Para qué sirve en la práctica |
|---|---|---|
| Deuda por cliente | Cuánto le debe cada cliente al negocio | Ordena a quién reclamar cobranza primero |
| Saldo a Favor | Cliente que pagó de más | Evita cobrarle de más o duplicar un cobro |
| Última Compra | Hace cuánto no compra un cliente | Detecta clientes que se están "enfriando" para reactivarlos |

---

## 2. Análisis comparativo — enero a junio 2026

### Ventas y ticket promedio

| Mes | Cantidad de ventas | Total facturado | Ticket promedio |
|---|---|---|---|
| Enero | 249 | $43.449.504 | $174.496 |
| Febrero | 427 | $78.359.019 | $183.511 |
| Marzo | 537 | $104.764.899 | $195.093 |
| Abril | 529 | $100.084.937 | $189.196 |
| Mayo | 321 | $59.476.327 | $185.285 |
| Junio | 461 | $76.711.767 | $166.403 |

**Lectura:** marzo fue el mejor mes del semestre (récord de facturación y de cantidad de ventas). Mayo tuvo una caída fuerte y clara — no solo bajó la facturación (-40% vs abril), también bajó la cantidad de ventas y la cantidad de pedidos entrantes del mes (ver más abajo), lo que indica que no fue un problema de cobranza ni de precios sino de **menor demanda real** ese mes. Junio recuperó volumen (461 ventas) pero con ticket promedio más bajo, el más bajo del semestre.

### Rentabilidad (ganancia real, no solo facturación)

| Mes | Facturado | Costo | Ganancia bruta | Margen |
|---|---|---|---|---|
| Enero | $43.449.504 | $31.463.867 | $11.985.637 | 27,6% |
| Febrero | $78.359.019 | $55.516.004 | $22.843.016 | 29,2% |
| Marzo | $104.764.899 | $74.808.819 | $29.956.079 | 28,6% |
| Abril | $100.084.937 | $71.887.144 | $28.197.793 | 28,2% |
| Mayo | $59.476.327 | $42.671.248 | $16.805.080 | 28,3% |
| Junio | $76.711.767 | $51.119.564 | $25.592.203 | **33,4%** |

**Lectura:** el margen se mantuvo estable entre 27,6% y 29,2% durante cinco meses, y **subió notablemente a 33,4% en junio**. Esto es una buena señal — vender menos en pesos que marzo pero con mejor margen (junio ganó casi lo mismo en términos brutos que abril, facturando $23M menos). Vale la pena identificar si el salto de margen en junio vino de un ajuste de precios, un cambio en la mezcla de productos vendidos (más productos de alto margen) o una baja puntual de costos de compra, para sostenerlo.

### Top 10 productos por ganancia generada (acumulado del semestre)

| Producto | Facturado | Ganancia |
|---|---|---|
| Almendras peladas non pareil x 1 kg | $15.965.726 | $5.953.526 |
| Nuez pelada mariposa blanca extra light x 1 kg | $11.640.621 | $3.631.321 |
| Mix de frutas secas y desecadas x 1 kg | $9.788.488 | $3.541.828 |
| Manzanilla flor x 1 kg | $7.477.207 | $3.177.457 |
| Chocolate semiamargo taza tableteado x 1 kg (Arcor) | $7.516.076 | $2.685.007 |
| Mix de frutas Delicias Naturales x 1 kg | $7.169.451 | $2.607.971 |
| Mix de frutas secas con banana x 1 kg | $6.776.032 | $2.422.282 |
| Azúcar integral mascabo x 10 kg | $2.406.620 | $2.145.080 |
| Mix salado x 1 kg | $5.908.474 | $1.952.704 |
| Harina de almendras sin piel x 1 kg | $4.134.160 | $1.947.427 |

**Lectura:** las almendras y frutos secos concentran la mayor parte de la ganancia del semestre. El "Azúcar integral mascabo x 10 kg" llama la atención: factura poco ($2,4M) pero tiene un margen altísimo — es un producto chico en volumen pero muy rentable, buen candidato para impulsar.

### Pedidos: qué tan bien se convierte un pedido en venta

| Mes | Pedidos recibidos | Convertidos en venta | Tasa de conversión |
|---|---|---|---|
| Enero | 4 | 4 | 100% |
| Febrero | 5 | 5 | 100% |
| Marzo | 14 | 14 | 100% |
| Abril | 13 | 12 | 92,3% |
| Mayo | 8 | 8 | 100% |
| Junio | 46 | 45 | 97,8% |

**Lectura:** la conversión es prácticamente perfecta todo el semestre. Mayo tuvo pocos pedidos entrantes (8), coincidiendo con la caída de ventas del mes — confirma que fue un mes de menor demanda, no un problema del proceso de ventas. Junio muestra un salto grande en pedidos (46, el máximo del semestre), buena señal de pipeline para julio.

### Clientes: deuda pendiente

- **Deuda total pendiente de cobro (a hoy): $19.937.351.**
- Está bastante concentrada: los **10 clientes que más deben** explican cerca del 70% de toda la deuda pendiente.
- Principales deudores: Casale, Gustavo Mario ($3.828.927), Aguilar, Gustavo Ezequiel ($1.915.559), Comunidad GH S.R.L. ($1.771.504), Adriazola, Teresa Diudina ($1.760.246), Granara, Agustín ($994.270), entre otros.

**Lectura:** enfocar la gestión de cobranza en esos 10 clientes recupera la mayor parte de lo pendiente, sin necesidad de perseguir a toda la cartera. Vale la pena revisar si a alguno de ellos conviene ponerle un límite de crédito o exigir pago al contado en la próxima compra.

### Método de pago dominante

La transferencia bancaria es, mes a mes, el medio de cobro más usado, seguida por efectivo. Tarjetas (débito/crédito) y Mercado Pago tienen peso marginal. Esto, junto con el tamaño del ticket promedio (~$170.000–195.000 por venta), confirma que la base de clientes es mayormente **comercial/mayorista** (varios de los principales deudores son sociedades — S.R.L., S.A. — no consumidores finales).

---

## 3. Alerta de calidad de datos (no afecta el análisis de arriba)

Se detectó un pago cargado con fecha "diciembre 2026" (una fecha futura, todavía no llegó ese mes) por $163.781. Es casi seguro un error de tipeo al cargar la fecha del pago (posiblemente quiso decir otro mes/año). No se incluyó en el análisis de arriba porque distorsionaría la serie mensual. Recomendación: que el equipo revise y corrija ese registro puntual en el sistema.

---

## 4. Resumen ejecutivo

- El semestre fue creciendo hasta marzo (pico), tuvo una caída real de demanda en mayo, y se recuperó en volumen en junio — con junio destacándose por una **mejora clara de margen (33,4%)**.
- La rentabilidad está concentrada en pocos productos (frutos secos y almendras); hay un producto de bajo volumen y altísimo margen (azúcar mascabo) para empujar más.
- El proceso comercial (pedido → venta) funciona muy bien, casi sin pérdidas en el camino.
- Hay $19,9M pendientes de cobro, concentrados en 10 cuentas — foco de cobranza claro y accionable.
- Julio arrancó con buen ritmo de pedidos heredado de junio, a confirmar en las próximas semanas.
