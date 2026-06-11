---
description: Parametros base de estimacion y presupuesto. Calibrado sobre proyectos reales de OlvidataSoft.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# Parametros de referencia - Proyectos calibrados

Los datos especificos de cada proyecto viven en /docs/<proyecto>/definiciones/4-presupuestador.md.
Para calibrar, leer primero ese archivo antes de estimar.

Proyectos de referencia disponibles:
- /docs/eleven-la-plata/definiciones/4-presupuestador.md (50 h reales, 27 modulos, .NET 10)
- /docs/vinosefue/definiciones/4-presupuestador.md (30 h reales, 16 modulos, maquinas de estado)
- /docs/delicias-naturales/definiciones/4-presupuestador.md (95 h base / 110 h con contingencia, 19 modulos, dataset por modulo)
- /docs/recotrack/definiciones/4-presupuestador.md (dataset ABM simple/intermedio con 30% incluido)
- /docs/lumitrack/definiciones/4-presupuestador.md (dataset ABM intermedio/complejo con 30% incluido)
- /docs/piapartments/definiciones/4-presupuestador.md (ABM intermedio con 30% incluido)
- /docs/energy-nutrition/definiciones/4-presupuestador.md (138 h estimadas, 14 modulos + 4 integraciones, referencia metodologica v4.0 — SIN CIERRE REAL, usar solo para integraciones externas y metodo)

## Conclusion de calibracion

- Los proyectos historicos cerrados (Eleven, Vinosefue) confirman sus horas como referencia solida de esfuerzo. El costo se recalcula a la tasa vigente USD 35/h.
- La tasa es independiente de la complejidad: proyectos mas complejos se expresan en mas horas, no en mayor tarifa.
- La contingencia del 15% se aplica correctamente desde los 50h de base en adelante.
- Con IA asistida, las horas reales son aprox. 1/3 de las horas PERT estimadas (patron confirmado en ShowroomGriffin y Ganaderia).

## Tasa vigente

- Tasa base: USD 35 / hora (Junio 2026 — horas reales con contingencia temporal 20%).
- Tasa anterior: USD 40 / hora (Junio 2026 — probada con contingencia 20%, revertida por ajuste de precio).
- Tasa anterior: USD 30 / hora (Junio 2026 — usada en Energy Nutrition v4.0 como excepcion negociada).
- Tasa anterior historica: USD 14 / hora (proyectos hasta Abril 2026 — quedan como referencia de horas, no de costo).
- Aplicar a todos los presupuestos futuros salvo indicacion contraria del cliente.
- Si el cliente negocia descuento, no bajar de USD 30/h sin aprobacion explicita.
- La tasa aplica sobre horas reales con contingencia (ver formula en "Modelo de facturacion"), no sobre horas PERT.
- La tasa es independiente de la complejidad: proyectos mas complejos se expresan en mas horas, no en mayor tarifa.

## Rangos de referencia por tipo de modulo

Horas M (PERT caso probable) sin cambio. Costos calculados con formula vigente: M x $16.80 (= M/2.5 x 1.20 x $35).
Las "horas facturables" son M/2.5 x 1.20 — no se exponen al cliente (solo USD por area funcional).

| Tipo de modulo | Rango M (h) | Horas facturables | USD (a $35/h con 20% cont.) |
|---|---|---|---|
| Ajuste puntual (campo, validacion, logica menor) | 0.5 – 1 h | 0.2 – 0.5 h | USD 8 – 17 |
| ABM simple (sin relaciones, sin logica) | 1 – 2 h | 0.5 – 1.0 h | USD 17 – 34 |
| ABM intermedio (con relaciones y validaciones) | 4 – 7 h | 1.9 – 3.4 h | USD 67 – 118 |
| Modulo con workflow / estados | 4 – 6 h | 1.9 – 2.9 h | USD 67 – 100 |
| Modulo financiero o con logica compleja | 5 – 8 h | 2.4 – 3.8 h | USD 84 – 134 |
| ABM complejo (padre/hijos, trazabilidad) | 7.7 – 11.5 h | 3.7 – 5.5 h | USD 129 – 193 |
| Integracion WS simple (OAuth + mapeo) | 3 – 4 h | 1.4 – 1.9 h | USD 50 – 67 |
| Integracion webhook (BackgroundService + HMAC) | 8 – 10 h | 3.8 – 4.8 h | USD 134 – 168 |
| Integracion ARCA/AFIP (codigo + cert + homologacion) | 7 – 9 h | 3.4 – 4.3 h | USD 118 – 151 |
| Integracion batch doble (rate limit + token refresh) | 15 – 18 h | 7.2 – 8.6 h | USD 252 – 302 |

## Calibracion incremental Abril 2026 (dataset real compartido)

Fuente: dataset de modulos de Delicias Naturales, Recotrack, Lumitrack y Piapartments.
Ver detalle por modulo en /docs/<proyecto>/definiciones/4-presupuestador.md de cada proyecto.

Regla de normalizacion obligatoria:
- Si una referencia historica viene con contingencia del 30% incluida, convertir primero a horas base: Horas base = Horas finales / 1.30.
- Evitar doble contingencia: no volver a aplicar 15% o 25% sobre una referencia ya inflada, salvo justificacion explicita por riesgo nuevo.

Resumen de rangos observados (horas finales con 30% incluida):
- ABM simple: 2 a 4 h (moda observada: 2 h).
- ABM intermedio: 5 a 7 h (moda observada: 6 h — dataset: 5h, 5.5h, 6.5h, 7h).
- ABM complejo: 10 a 15 h.
- ABM complejo con padre/hijos detalle: 10 h como referencia inicial.
- Notificaciones SignalR acotadas: 4.5 h como referencia inicial.

Rangos de integraciones externas (horas base PERT, contingencia separada) — fuente: Energy Nutrition v4.0 (estimacion, sin cierre real):
- Integracion WS simple (OAuth + mapeo): 3 – 4 h base.
- Integracion webhook con BackgroundService (HMAC, async): 8 – 10 h base.
- Integracion batch doble con rate limit y token refresh: 15 – 18 h base.
- Integracion ARCA/AFIP (migracion codigo + cert .p12 + homologacion): 7 – 9 h base.
Nota: estas referencias son estimaciones metodologicas (no cierres reales). Recalibrar cuando EN tenga cierre.

Resumen de rangos base equivalentes (sin contingencia):
- ABM simple: 1.5 a 3.1 h.
- ABM intermedio: 3.1 a 5.4 h.
- ABM complejo: 7.7 a 11.5 h.
- ABM complejo con padre/hijos detalle: 7.7 h.
- Notificaciones SignalR acotadas: 3.5 h.

Reglas practicas de uso del dataset:
- Si el pedido nuevo coincide con un modulo comparable, leer primero el 4-presupuestador.md del proyecto de referencia y luego ajustar por drivers reales.
- Si la estimacion final supera 20% del techo historico de la banda elegida, documentar causa puntual.
- Si no hay modulo comparable claro, declarar incertidumbre y devolver rango por fase.

### Modificacion sobre modulo existente
- Agregar campo simple: M ~0.5 h → USD 10
- Agregar regla de negocio: M ~1 a 2 h → USD 20 a 40
- Nuevo reporte o exportacion: M ~1 a 2 h → USD 20 a 40
- Migracion EF requerida: M ~0.5 h → USD 10 por cada migracion

## Planes de mantenimiento anual (OlvidataSoft — servidor a cargo del proveedor)

Incluir siempre en el presupuesto como linea separada post-desarrollo. El plan corresponde al servicio continuo del servidor y soporte, NO es parte del costo de desarrollo.

| Plan     | Tablas BD        | USD/año | Incluye                                                  |
|----------|------------------|---------|----------------------------------------------------------|
| STARTER  | 1 – 5            | 250     | 1 admin, soporte email, actualizaciones de seguridad     |
| PRO      | 6 – 15           | 300     | Hasta 2 usuarios, soporte WhatsApp, 1 ronda de ajuste    |
| PREMIUM  | 16 – 30          | 400     | Hasta 3 usuarios, soporte prioritario, 2 rondas ajuste   |
| SCALE    | 31+              | 750     | Hasta 10 sesiones, usuarios ilimitados, 3 rondas ajuste  |

Reglas de aplicacion:
- Determinar el plan según la cantidad de tablas del sistema entregado.
- Presentar el costo de desarrollo y el mantenimiento anual como dos lineas separadas en el presupuesto.
- Aclarar al cliente que el mantenimiento cubre hosting, seguridad y soporte — no cubre cambios funcionales nuevos.
- Los extras (usuario adicional, módulo nuevo, etc.) se cotizan aparte y se suman al plan base si el cliente los requiere.

## Extras opcionales (vigente 2026)

Precios calculados con formula vigente (M x $16.80). Referencia a tasa USD 35/h con contingencia 20%:

| Extra                        | Precio    | M equiv. | Validez calibracion                                       |
|------------------------------|-----------|----------|-----------------------------------------------------------|
| Usuario adicional            | USD 100/año | —      | Costo de servicio, no de desarrollo. OK.                  |
| Modulo nuevo                 | USD 75+   | 4 h+     | ABM intermedio minimo M=4-7h = USD 75-135. Cotizar por complejidad. |
| UI personalizada             | USD 40    | ~2 h     | CSS/theming basico. Razonable.                            |
| Optimizacion de performance  | USD 60    | ~3 h     | Aceptable para un pase acotado de queries + carga.        |
| Ronda de ajuste extra        | USD 40    | ~2 h     | Cubre hasta 4 ajustes puntuales (0.5h c/u). Justo.        |
| Backup automatizado mensual  | USD 80/año | —      | Costo de infraestructura. OK.                             |

## Formato de entrega al cliente

- Documento simple, sin jerga tecnica
- Agrupado por area funcional (no por capa tecnica)
- Incluir tabla: Area | USD (las horas son internas — no se exponen al cliente)
- Incluir siempre la linea "Uso de infraestructura IA (tokens): USD 100" dentro del total de desarrollo
- Incluir seccion Que esta incluido y Que NO esta incluido
- Condiciones estandar: 50% al inicio / 50% a la entrega
- Validez de oferta: 30 dias

## Exclusiones fijas (siempre aplicar salvo excepcion documentada)

- Migracion de datos desde sistema anterior
- Configuracion y costo del servidor / hosting
- Facturacion electronica AFIP / ARCA
- Aplicacion movil (iOS / Android)
- Integracion con hardware externo
- Cambios de alcance posteriores al inicio (se presupuestan por separado)

## Modelo de facturacion (Junio 2026)

Objetivo: cobrar USD 35/h sobre horas reales de desarrollo con IA asistida, con contingencia temporal del 20%.

Formula vigente:
  Horas facturables por modulo = (M / 2.5) x 1.20
  Costo modulo = Horas facturables x USD 35
  Simplificado: Costo = M x 0.48 x $35 = M x $16.80

- M es el valor "caso mas probable" del PERT (no el PERT calculado, no el P).
- El factor 2.5 representa la eficiencia IA calibrada sobre cierres reales (ShowroomGriffin, Ganaderia).
- El 20% de contingencia cubre reentregas, iteraciones menores y desvios de estimacion.
- No aplicar contingencia adicional sobre la formula: el 20% ya la absorbe.
- Excepcion: riesgo extremo documentado (integracion sin precedente, migracion de datos) puede sumarse justificado.

Cargo fijo por uso de tokens IA (vigente Junio 2026):
- Todo presupuesto de proyecto suma USD 100 fijos en concepto de uso de tokens IA (costo de infraestructura de desarrollo IA asistida).
- Se presenta como linea separada dentro del total de desarrollo (no se prorratea por modulo ni se mezcla con el mantenimiento anual).
- No aplica a iteraciones evolutivas menores a 4 h facturables, salvo indicacion contraria.

Patron confirmado de ratio PERT / real en proyectos con IA asistida:

| Proyecto | Horas PERT | Horas reales | Ratio PERT/real | Horas formula (M/2.5x1.2) | Ratio formula/real |
|---|---:|---:|---:|---:|---:|
| ShowroomGriffin | 101.1 h | 25 h | 4.0x | ~40.6 h | 1.6x |
| Ganaderia | 101.0 h | ~30 h total | 3.4x | ~38.6 h | 1.3x |

El ratio formula/real de 1.3x-1.6x confirma que la contingencia del 20% es un buffer razonable: protege sin inflar exageradamente.

Factor de calibracion 2.5: fijo hasta que Energy Nutrition cierre. Recalibrar con ese cierre.

## Alerta de sobreestimacion sistematica confirmada (Junio 2026)

Dos proyectos cerrados muestran el mismo patron: las estimaciones PERT sin anclaje historico previo producen entre 3x y 4x las horas reales.

| Proyecto | Horas estimadas | Horas reales | Ratio estimado/real |
|---|---:|---:|---:|
| ShowroomGriffin | 101.1 h | 25 h | 4.0x |
| Ganaderia | 101.0 h | ~15 h (Etapa 1 con reentrega) / ~30 h (proyecto completo proyectado) | 6.7x Etapa 1 / 3.4x total |

Regla de recalibracion obligatoria derivada de este patron:
- El M (caso mas probable) debe anclarse en la mediana historica de proyectos similares ANTES de estimar.
- Los proyectos de 8-11 modulos de complejidad media-alta cierran en el rango de 25 a 30 horas reales totales.
- Para proyectos de 16-27 modulos de complejidad media, el rango real historico es 30-50 horas totales.
- No proyectar horas basandose unicamente en la suma de O/M/P sin comparar primero el total proyectado contra estos cierres reales.

## Notas de calibracion

- Parametros calibrados en base a proyectos reales cerrados y presupuestados desde 2025.
- Total combinado historico base: 175 horas - USD 2.450 - tasa efectiva historica USD 14/h.
- **Junio 2026 — primer ciclo real a tasa nueva:** iteracion evolutiva Delicias Naturales, 4 h reales, USD 160 a USD 40/h. Ratio estimado/real: 1.0 (estimacion exacta).
- **2026-06-03:** Relevamiento de Stock (Delicias Naturales), ABM intermedio. 5.5 h reales a USD 40/h. Dataset ABM intermedio: 5h, 5.5h, 6.5h, 7h. Rango confirmado 5-7h, mediana 6h.
- **2026-06-08:** Contingencia temporal del 20% incorporada a la formula. Tasa ajustada a USD 35/h (definitiva). Formula vigente: M/2.5 x 1.20 x $35 = M x $16.80. Energy Nutrition v6.1 calculado bajo esta formula.
- Al referenciar historicos anteriores a Junio 2026, usar las horas como referencia de esfuerzo y recalcular el costo con la tasa vigente de USD 35/h.
- Revisar y actualizar la tasa cada 6 meses o ante cambio de contexto economico.
- La contingencia se aplica una unica vez segun la politica vigente (variable por riesgo 8/15/25 por defecto, o fija del cliente cuando aplique).
- Para proyectos que incluyan migracion de datos, agregar entre 20% y 30% al total como riesgo declarado.
- Facturacion AFIP/ARCA es exclusion estandar salvo excepcion documentada.
- Integraciones externas: ver rangos por tipo en seccion "Rangos de referencia por tipo de modulo".

## Auditoria de inconsistencias — Junio 2026

Detectadas al incorporar Energy Nutrition y definir objetivo USD 35/h. Estado de cada una:

| # | Inconsistencia | Causa | Estado |
|---|---|---|---|
| I-1 | Tasa vigente USD 30/h estaba POR DEBAJO del piso declarado USD 35/h en Energy Nutrition 4b | Tasa bajo de 45→30 sin actualizar el piso | CORREGIDO — tasa vigente = USD 35/h, piso = USD 30/h |
| I-2 | Extras opcionales referenciaban USD 45/h como tasa de validacion | No se actualizo la tabla al bajar la tasa | CORREGIDO — tabla recalculada a USD 35/h |
| I-3 | Rangos de costo por modulo calculados a USD 30/h | Tercera actualizacion de tasa no los sincronizo | CORREGIDO — rangos actualizados a USD 35/h |
| I-4 | Integraciones externas sin rango de referencia en dataset | Ningun proyecto anterior las incluia | CORREGIDO — 4 nuevos tipos de integracion agregados (fuente: EN v4.0, pendiente cierre real) |
| I-5 | Sobreestimacion sistematica detectada pero sin guia de uso para modelo de horas reales | La alerta existia pero no decia que hacer si se cobra por hora real | CORREGIDO — seccion "Modelo de facturacion" con regla de division por 2.5 |
| I-6 | Historial de tasa confuso (14→40→45→30 en mismo mes) sin razon explicita | Calibraciones rapidas sin documentar motivacion | CORREGIDO — historial simplificado en notas de calibracion |
| I-7 | Ganaderia en dataset con tasa USD 12/h, inconsistente con tasas actuales | El documento de ganaderia usa tasa historica del contrato | PENDIENTE — al usar ganaderia como referencia de horas, ignorar la columna USD; recalcular a USD 35/h |
| I-8 | Energy Nutrition sin cierre real, riesgo de usar sus horas como verdad | Proyecto en estado BORRADOR | MITIGADO — EN marcado explicitamente como "sin cierre real" en lista de proyectos y en su memoria |
| I-9 | Metodo PERT no diferencia entre precio fijo y horas reales | El PERT siempre produjo estimaciones de "precio fijo maximo" | MITIGADO — seccion "Modelo de facturacion" documenta la diferencia y la regla de ajuste |