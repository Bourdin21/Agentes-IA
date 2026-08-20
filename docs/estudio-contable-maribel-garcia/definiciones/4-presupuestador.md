# Memoria - Presupuestador

## Proyecto: estudio-contable-maribel-garcia
## Ultima actualizacion: 2026-08-20

## Definiciones vigentes

**Nota de estructura (agregada 2026-08-20):** a pedido de Joaquin se ofrecen dos opciones de stack al lead (ver `especificacion-funcional-opciones.md`) — cada una con su propio WBS/PERT/costo, calculados por separado porque el alcance funcional difiere (Opcion A es deliberadamente mas chica: sin login/historial/IA/crecimiento) y porque Opcion A no reutiliza el ecosistema .NET del estudio. Los dos calculos usan la misma formula vigente (Costo = M x $16.80, Tokens IA 25%) — no hay tasa diferenciada por lenguaje.

## OPCION A — Conversor liviano (PHP)

### PASO 0 — Anclaje historico
Comparable directo y exacto: **contadores-bma-conversor** (PHP, sin login, sin BD persistente — parser + UI + deploy), 13.1h PERT / 8h real, ratio PERT/real 1.6x. Mismo perfil de proyecto (herramienta acotada, sin estado entre usos) y mismo stack — es el ancla mas confiable del dataset para esta opcion, mejor que cualquier comparable .NET.

### WBS funcional (sin Etapa 2 — esta opcion no incluye IA ni crecimiento, ver especificacion funcional)

| # | Item | Clasificacion |
|---|---|---|
| 1 | Importacion extracto bancario (parser CSV/Excel) | Parser de archivo — igual patron que contadores-bma-conversor, formato tabular simple (no jerarquico/pivot) |
| 2 | Importacion extracto Mercado Pago (parser CSV/Excel) | Parser de archivo — formato mas estandar que el bancario |
| 3 | Motor de conciliacion (matching monto+fecha, en memoria, sin persistencia) | Logica de negocio, nucleo del sistema — mas simple que la version .NET al no requerir modelo de datos/estados persistentes |
| 4 | Vista de resultados (pantalla unica, sin BD: conciliado/dudoso/sin conciliar) | UI pantalla unica sin BD |
| 5 | Descarga de reporte Excel | Reporte/exportacion simple |
| 6 | Puesta en marcha (deploy hosting compartido, dominio) | Deploy inicial (regla de subestimacion sistematica — M minimo 2-3h) |

### Estimaciones PERT por item

| # | Item | O | M | P | PERT=(O+4M+P)/6 | M usado para costo |
|---|---|---:|---:|---:|---:|---:|
| 1 | Parser extracto bancario | 2 | 3 | 4.5 | 3.08 | 3 |
| 2 | Parser extracto MP | 1.5 | 2 | 3 | 2.08 | 2 |
| 3 | Motor de conciliacion (sin persistencia) | 2.5 | 4 | 6 | 4.08 | 4 |
| 4 | Vista de resultados | 1.5 | 2 | 3 | 2.08 | 2 |
| 5 | Descarga Excel | 1 | 1.5 | 2.5 | 1.58 | 1.5 |
| 6 | Puesta en marcha | 2 | 3 | 4.5 | 3.08 | 3 |
| **Total proyecto** | | | | | **15.98 h PERT** | **15.5 h (M)** |

### Autocorreccion contra historicos
Ratio = M total (15.5h) / M base de contadores-bma-conversor (11h estimado original) = 1.41x, con 6 items vs 3 (2x la cantidad) — proporcion razonable: mas modulos que el comparable, pero cada uno individualmente mas chico o similar (el motor de conciliacion es nuevo, sin equivalente en el comparable, pesa la diferencia). Dentro de rango esperado, sin senal de sobreestimacion.

### Ratio de reutilizacion y volumen
`R = 0%` (reuso de enfoque tecnico del parser, no de codigo — misma regla que Opcion B) → Tier 3, 0%. `Subtotal_lista = USD 260` (ver abajo) → por debajo de USD 600 → Tier V0, 0%. `factor_tier = MAX(0%, 0%) = 0%` — sin descuento, mismo criterio que Opcion B (sin override pedido).

### Calculo de costo por item (Costo = M x $16.80)

| # | Item | M | USD (lista) |
|---|---|---:|---:|
| 1 | Parser extracto bancario | 3 | 50.40 |
| 2 | Parser extracto MP | 2 | 33.60 |
| 3 | Motor de conciliacion | 4 | 67.20 |
| 4 | Vista de resultados | 2 | 33.60 |
| 5 | Descarga Excel | 1.5 | 25.20 |
| 6 | Puesta en marcha | 3 | 50.40 |
| **Subtotal (sin etapas — proyecto unico)** | | **15.5** | **260.40** |

### Resumen economico Opcion A
- Subtotal_lista: USD 260
- Descuento de expansion agresiva: 0% (Tier 3 / Tier V0, sin override).
- Tokens IA (25% del subtotal): USD 65
- **Total cliente Opcion A: USD 325**
- Piso absoluto USD 280 — no aplica (ya por encima, aunque por poco margen: USD 45 sobre el piso).

### Precios distribuidos al cliente (Tokens IA plegado, regla 2026-08-20)
Factor constante x1.25 sobre el precio de lista de cada item (25.20→31.50, etc.), redondeado por item con ajuste de USD 0.50 en "Descarga Excel" para que la suma cierre exacta contra el Total:

| Item | Precio lista | Precio mostrado al cliente (x1.25) |
|---|---:|---:|
| Parser extracto bancario | 50.40 | 63 |
| Parser extracto MP | 33.60 | 42 |
| Motor de conciliacion | 67.20 | 84 |
| Vista de resultados | 33.60 | 42 |
| Descarga Excel | 25.20 | 31 |
| Puesta en marcha | 50.40 | 63 |
| **Total** | **260.40** | **325** |

### Costo interno de IA (dato exclusivamente interno)
- Horas facturables = 15.5/2.5 x 1.20 = 7.44 h. Costo_IA_modulos = 7.44h x USD 4/h = USD 29.8. Costo_IA_overhead = USD 4. Total ≈ USD 33.8 — por debajo de Tokens IA (USD 65), sin ajuste necesario. Nota: esta opcion es PHP, no Opus/.NET — el placeholder de tarifa Opus asume el mismo perfil de sesion agentic independientemente del lenguaje objetivo (el modelo que codifica es el mismo, cambia el codigo que produce, no como se le paga a Claude); se mantiene el mismo calculo por consistencia metodologica.

### Plan de mantenimiento Opcion A
Sin tablas de negocio persistentes (herramienta sin historial, no guarda conciliaciones entre usos) y sin login diferenciado por usuario — el minimo de la tabla de planes (**STARTER, USD 300/año, 1 admin**) ya cubre lo que hace falta: hosting, seguridad y soporte basico. No aplica el ajuste de usuarios adicionales de Opcion B porque esta opcion no tiene el concepto de usuario logueado.

---

## OPCION B — Sistema de gestion profesional (.NET/BlankProject)

### PASO 0 — Anclaje historico
Consultado `docs/calibracion/dataset.yml` y `27-presupuesto-parametros.instructions.md`. Sin proyecto comparable exacto (conciliacion bancaria = dominio nuevo). Referencia mas cercana por tamano/naturaleza: **contadores-bma-conversor** (13.1h PERT / 8h real, 3 modulos: parser Excel + UI + deploy) — sistema chico de procesamiento de archivos, mismo perfil de "herramienta acotada" en vez de "sistema de gestion completo". Se usa como ancla de orden de magnitud, no de modulo a modulo (esta tiene 8 items vs 3, logica de matching que contadores-bma-conversor no tenia).

### WBS funcional vigente (Etapa 1 = MVP deterministico, Etapa 2 = asistencia IA)

| # | Item | Etapa | Clasificacion |
|---|---|---|---|
| 1 | Usuarios y accesos (login basico, sin roles diferenciados) | 1 | Modulo nuevo — ABM simple |
| 2 | Importacion extracto bancario (parser CSV/Excel + validacion) | 1 | Modulo nuevo — parser de archivo (reuso de enfoque, no de codigo, ver 3-arquitecto-mvc.md) |
| 3 | Importacion extracto Mercado Pago (parser CSV/Excel + validacion) | 1 | Modulo nuevo — parser de archivo (formato mas estandar que el bancario) |
| 4 | Motor de conciliacion automatica (matching monto+fecha con tolerancia) | 1 | Modulo nuevo — logica de negocio, nucleo del sistema |
| 5 | Vista de resultados + confirmar/rechazar sugerencias | 1 | Modulo nuevo — ABM intermedio |
| 6 | Exportar reporte de conciliacion (Excel) | 1 | Modulo nuevo — reporte/exportacion simple |
| 7 | Puesta en marcha (deploy hosting compartido, dominio) | 1 | Deploy inicial (regla de subestimacion sistematica — M minimo 2h) |
| 8 | Asistencia por IA (API Claude) para casos ambiguos de conciliacion | 2 | **Integracion externa nueva, sin precedente en el estudio** — primera vez que un producto entregado llama a un modelo de IA en tiempo de ejecucion (ver nota tecnica en 3-arquitecto-mvc.md) |

### Estimaciones PERT por item

| # | Item | O | M | P | PERT=(O+4M+P)/6 | M usado para costo |
|---|---|---:|---:|---:|---:|---:|
| 1 | Usuarios y accesos | 1 | 1.5 | 2.5 | 1.58 | 1.5 |
| 2 | Importacion extracto bancario | 3 | 4 | 6 | 4.17 | 4 |
| 3 | Importacion extracto MP | 2 | 3 | 4.5 | 3.08 | 3 |
| 4 | Motor de conciliacion | 4 | 6 | 9 | 6.17 | 6 |
| 5 | Vista resultados + acciones | 3.5 | 5 | 7.5 | 5.17 | 5 |
| 6 | Exportar reporte | 1.5 | 2 | 3 | 2.08 | 2 |
| 7 | Puesta en marcha | 1.5 | 2 | 3 | 2.08 | 2 |
| **Subtotal Etapa 1** | | | | | **24.34 h PERT** | **23.5 h** |
| 8 | Asistencia IA (integracion nueva) | 3 | 4 | 6 | 4.17 | 4 |
| **Subtotal Etapa 2** | | | | | **4.17 h PERT** | **4 h** |
| **Total proyecto** | | | | | **28.51 h PERT** | **27.5 h (M)** |

### Autocorreccion contra historicos
Ratio = M total (27.5h) / M base de contadores-bma-conversor (11h estimado original de ese proyecto, 3 modulos) = 2.5x en horas para 2.67x en cantidad de items (8 vs 3) — proporcion razonable, sin senal de sobreestimacion. No hay ratio contra un comparable de dominio identico (no existe) — se documenta la ausencia de comparable exacto en vez de forzar una comparacion invalida contra proyectos financieros mas grandes (Ganaderia, etc.), que tienen modulos que este proyecto no tiene (caja, cuotas, facturacion).

### Ratio de reutilizacion (R)
`R = M reutilizacion / M total = 0 / 27.5 = 0%` — ningun item cae en la regla de "modificacion sobre modulo existente" (el reuso del patron de parser es a nivel de enfoque tecnico, no de codigo/modulo ya construido en el estudio para este dominio). **Tier 3 — Estandar, 0% descuento por reutilizacion.**

### Descuento por volumen del proyecto
Subtotal_lista = USD 462 (ver calculo abajo) → por debajo de USD 600 → **Tier V0 — Estandar, 0% descuento por volumen.**

`factor_tier = MAX(0%, 0%) = 0%` — ningun descuento de expansion agresiva aplica por calculo objetivo. No hubo pedido explicito de Joaquin de aplicar un override esta vez (a diferencia de audifonos-bariloche) — se mantiene precio de lista.

### Tasa vigente y contingencia aplicada
- Tasa vigente: USD 35/h. Formula: Costo = M x $16.80. Contingencia 20% ya incluida en la formula.
- Riesgo del proyecto: **medio** — el nucleo (motor de conciliacion) es logica nueva no trivial, mas la incertidumbre de si el formato real de los extractos (banco especialmente) coincide con el supuesto. Ya reflejado en la formula vigente, sin contingencia adicional aparte.

### Calculo de costo por item (Costo = M x $16.80)

| # | Item | M | USD (lista) |
|---|---|---:|---:|
| 1 | Usuarios y accesos | 1.5 | 25.20 |
| 2 | Importacion extracto bancario | 4 | 67.20 |
| 3 | Importacion extracto MP | 3 | 50.40 |
| 4 | Motor de conciliacion | 6 | 100.80 |
| 5 | Vista resultados + acciones | 5 | 84.00 |
| 6 | Exportar reporte | 2 | 33.60 |
| 7 | Puesta en marcha | 2 | 33.60 |
| **Subtotal Etapa 1** | | **23.5** | **394.80** |
| 8 | Asistencia IA | 4 | 67.20 |
| **Subtotal Etapa 2** | | **4** | **67.20** |

Agrupado por area funcional para el documento cliente (redondeado):
- Importacion de extractos (Banco + Mercado Pago) (items 2+3): USD 117
- Motor de conciliacion automatica (item 4): USD 101
- Revision y confirmacion de sugerencias (item 5): USD 84
- Reportes de conciliacion (item 6): USD 34
- Usuarios y accesos (item 1): USD 25
- Puesta en marcha (item 7): USD 34
- **Subtotal Etapa 1: USD 395**
- Asistencia por IA en casos ambiguos (item 8): USD 67
- **Subtotal Etapa 2: USD 67**

### Resumen economico (Tokens IA calculado internamente, distribuido al cliente — ver tabla abajo)
- Subtotal Etapa 1: USD 395
- Subtotal Etapa 2: USD 67
- Subtotal desarrollo (Etapa 1 + Etapa 2, sin Tokens IA): USD 462
- Descuento de expansion agresiva: 0% (Tier 3 reutilizacion / Tier V0 volumen, ambos por debajo de umbral) — sin override pedido.
- Tokens IA (25% del subtotal desarrollo): USD 116
- **Total cliente: USD 578**
- Piso absoluto USD 280 — no aplica (ya por encima).

### Precios distribuidos al cliente (Tokens IA plegado, regla 2026-08-20)
Factor constante x1.25 sobre el precio de lista de cada area funcional agrupada — el cliente ve solo la columna derecha, nunca "Tokens IA" como concepto separado:

| Area funcional | Precio lista | Precio mostrado al cliente (x1.25) |
|---|---:|---:|
| Importacion de extractos (Banco + MP) | 117.60 | 147 |
| Motor de conciliacion automatica | 100.80 | 126 |
| Revision y confirmacion de sugerencias | 84.00 | 105 |
| Reportes de conciliacion | 33.60 | 42 |
| Usuarios y accesos | 25.20 | 32 |
| Puesta en marcha | 33.60 | 42 |
| **Subtotal Etapa 1** | **394.80** | **494** |
| Asistencia por IA (Etapa 2) | 67.20 | 84 |
| **Subtotal Etapa 2** | **67.20** | **84** |
| **Total** | **462.00** | **578** |

### Costo interno de IA (dato exclusivamente interno, no aparece en presupuesto-cliente.md)
- Horas facturables totales (Etapa1+Etapa2) = 27.5/2.5 x 1.20 = 13.2 h.
- Costo_IA_modulos = 13.2h x USD 4/h (tarifa Opus placeholder) = USD 52.8.
- Costo_IA_overhead_proyecto = 4h x USD 1/h (tarifa Sonnet placeholder) = USD 4.
- Costo_IA total proyectado ≈ USD 56.8 — por debajo del cargo Tokens IA visible al cliente (USD 116), sin necesidad de ajuste de precio por modulo.
- **Nota distinta de este costo:** el item 8 (Asistencia IA) introduce ademas un costo operativo de IA en PRODUCCION (llamadas a la API de Claude en tiempo de ejecucion del sistema entregado, no en el desarrollo) — no cuantificado aqui por falta de volumen real de conciliaciones esperado, declarado como pregunta abierta en la propuesta (ver 3-arquitecto-mvc.md).

### Plan de mantenimiento
Tablas de negocio: `ExtractoBancario`, `MovimientoBancario`, `ExtractoMercadoPago`, `MovimientoMercadoPago`, `Conciliacion` = 5 tablas → limite superior de **STARTER (1-5)**.
- STARTER (USD 300/año, 1 admin) + 1 usuario adicional (USD 125/año) = USD 425/año si son 2 usuarios.
- **PRO (USD 400/año, hasta 2 usuarios) es mas barato que STARTER+extra y cubre sin ambiguedad el caso "1 o 2 personas"** — recomendado como plan por defecto.

### Cierre estimado vs real (si disponible)
No disponible — proyecto en etapa de propuesta, sin aprobacion del lead todavia.

---

## Comparacion Opcion A vs Opcion B

| | Opcion A — PHP | Opcion B — .NET |
|---|---:|---:|
| Desarrollo (subtotal_lista) | USD 260 | USD 462 |
| Tokens IA (25%) | USD 65 | USD 116 |
| **Total desarrollo** | **USD 325** | **USD 578** |
| Mantenimiento anual | USD 300/año (STARTER) | USD 400/año (PRO) |

Diferencia de USD 253 en desarrollo y USD 100/año en mantenimiento — refleja directamente lo que Opcion B tiene y Opcion A no (login/usuarios, historial persistente y auditable, motor con estado en BD en vez de en memoria, asistencia IA, base para crecer). No es un descuento ni una promocion — son dos alcances funcionales distintos, cada uno con su propio costo real.

## Historial de ajustes
- 2026-08-20: primera version (solo Opcion B/.NET). Total propuesto USD 578 (desarrollo) + mantenimiento PRO USD 400/año. Discovery minimo (3 respuestas de cuestionario, recibidas fuera de orden) — presupuesto sujeto a reestimacion si el formato real de los extractos difiere del supuesto.
- 2026-08-20: agregada Opcion A (PHP conversor liviano) a pedido de Joaquin, con WBS/PERT/costo propio (no reutiliza los numeros de Opcion B — alcance funcional distinto y sin reuso del ecosistema .NET). Anclada directamente contra contadores-bma-conversor (mismo stack, mismo perfil de proyecto sin estado). Total Opcion A: USD 325 desarrollo + STARTER USD 300/año.
- 2026-08-20: aplicada la nueva regla de distribucion de Tokens IA (27-presupuesto-parametros.instructions.md, "forma de exposicion cambiada 2026-08-20") — se agrego la tabla "Precios distribuidos al cliente" en ambas opciones (factor constante x1.25 sobre el precio de lista de cada item/area). Totales sin cambios (USD 325 / USD 578); cambia solo el desglose que ve el cliente en `presupuesto-cliente.md` — ya no aparece "Tokens IA" como linea separada.
