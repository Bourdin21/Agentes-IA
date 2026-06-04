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

## Conclusion de calibracion

- Los proyectos cerrados confirman la tasa de USD 14 / hora como referencia solida.
- La tasa es independiente de la complejidad: proyectos mas complejos se expresan en mas horas, no en mayor tarifa.
- La contingencia del 15% se aplica correctamente desde los 50h de base en adelante.

## Tasa vigente

- Tasa base: USD 30 / hora (actualizada Junio 2026 — tercera actualizacion).
- Tasa anterior inmediata: USD 45 / hora (Junio 2026, segunda actualizacion).
- Tasa anterior: USD 40 / hora (Junio 2026, primer ciclo real confirmado).
- Tasa anterior historica: USD 14 / hora (proyectos hasta Abril 2026 — quedan como referencia de horas, no de costo).
- Aplicar a todos los presupuestos futuros salvo indicacion contraria del cliente.
- Si el cliente negocia descuento, no bajar de USD 25/h sin aprobacion explicita.
- La tasa es independiente de la complejidad: proyectos mas complejos se expresan en mas horas, no en mayor tarifa.

## Rangos de referencia por tipo de modulo

Horas sin cambio. Costos actualizados a tasa USD 30/h (Junio 2026):

- Ajuste puntual (campo, validacion, logica menor): 0.5 a 1 h - USD 15 a 30
- ABM simple (sin relaciones, sin logica): 1 a 2 h - USD 30 a 60
- ABM intermedio (con relaciones y validaciones): 4 a 7 h - USD 120 a 210
- Modulo con workflow / estados: 4 a 6 h - USD 120 a 180
- Modulo financiero o con logica compleja: 5 a 8 h - USD 150 a 240

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
- Agregar campo simple: 0.5 h - USD 15
- Agregar regla de negocio: 1 a 2 h - USD 30 a 60
- Nuevo reporte o exportacion: 1 a 2 h - USD 30 a 60
- Migracion EF requerida: sumar 0.5 h - USD 15 por cada migracion

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

Referencia para validar coherencia con tasa USD 45/h:

| Extra                        | Precio    | Horas equiv. | Validez calibracion                                       |
|------------------------------|-----------|--------------|-----------------------------------------------------------|
| Usuario adicional            | USD 100/año | —          | Costo de servicio, no de desarrollo. OK.                  |
| Módulo nuevo                 | USD 200+  | 4 h+         | ABM intermedio mínimo: 4-7 h = USD 180-315. **Desde USD 200, cotizar por complejidad.** |
| UI personalizada             | USD 100   | ~2.2 h       | CSS/theming básico. Justo en el limite bajo.              |
| Optimización de performance  | USD 150   | ~3.3 h       | Aceptable para un pase acotado de queries + carga.        |
| Ronda de ajuste extra        | USD 80    | ~1.8 h       | Cubre hasta 3 ajustes puntuales (0.5h c/u). Justo.        |
| Backup automatizado mensual  | USD 80/año | —          | Costo de infraestructura. OK.                             |

## Formato de entrega al cliente

- Documento simple, sin jerga tecnica
- Agrupado por area funcional (no por capa tecnica)
- Incluir tabla: Area | USD (las horas son internas — no se exponen al cliente)
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

## Alerta de sobreestimacion sistematica confirmada (Junio 2026)

Dos proyectos cerrados muestran el mismo patron: las estimaciones PERT sin anclaje historico previo producen entre 3x y 4x las horas reales.

| Proyecto | Horas estimadas | Horas reales | Ratio estimado/real |
|---|---:|---:|---:|
| ShowroomGriffin | 101.1 h | 25 h | 4.0x |
| Ganaderia | 101.0 h | 12 h (MVP Etapa 1, en curso) | >6x parcial |

Regla de recalibracion obligatoria derivada de este patron:
- El M (caso mas probable) debe anclarse en la mediana historica de proyectos similares ANTES de estimar.
- Los proyectos de 8-11 modulos de complejidad media-alta cierran en el rango de 25 a 30 horas reales totales.
- Para proyectos de 16-27 modulos de complejidad media, el rango real historico es 30-50 horas totales.
- No proyectar horas basandose unicamente en la suma de O/M/P sin comparar primero el total proyectado contra estos cierres reales.

## Notas de calibracion

- Parametros calibrados en base a tres proyectos reales / presupuestados en 2025.
- Total combinado base: 175 horas - USD 2.450 - tasa efectiva historica USD 14/h.
- Total combinado con contingencias: 190 horas - USD 2.660.
- **Junio 2026: tasa actualizada a USD 40/h.** Primer desarrollo real confirmado: iteracion evolutiva Delicias Naturales (mejoras Solicitudes de Ingreso de Stock + estado pedido), 4 h reales, USD 160 cobrados a USD 40/h. Ratio estimado/real: 1.0 (estimacion exacta).
- **2026-06-03:** Modulo Relevamiento de Stock (Delicias Naturales), ABM intermedio. Horas reales: 5.5 h. USD 220 cobrados a tasa USD 40/h. Dataset ABM intermedio ampliado: 5h, 5.5h, 6.5h, 7h. Rango confirmado 5-7h, mediana 6h.
- **2026-06-03:** Tasa actualizada a USD 45/h. Las horas ya no se exponen al cliente en el documento de presupuesto (solo USD por area funcional).
- **2026-06-04:** Tasa actualizada a USD 30/h (tercera actualizacion). Presupuestos incluyen ahora: introduccion/contexto de relevamiento, alcance funcional detallado, tabla de especificaciones tecnicas del servicio y definicion de roles/usuarios del sistema.
- **Junio 2026: sobreestimacion sistematica confirmada en ShowroomGriffin (4x) y Ganaderia (3.4x).** Ver seccion "Alerta de sobreestimacion sistematica" arriba.
- Al referenciar historicos anteriores a Junio 2026, usar las horas como referencia de esfuerzo pero recalcular el costo con la tasa vigente de USD 40/h.
- Revisar y actualizar la tasa cada 6 meses o ante cambio de contexto economico.
- La contingencia se aplica una unica vez segun la politica vigente (variable por riesgo 8/15/25 por defecto, o fija del cliente cuando aplique).
- Para proyectos que incluyan migracion de datos, agregar entre 20% y 30% al total como riesgo declarado.
- Facturacion AFIP es exclusion estandar salvo excepcion documentada.
- Integraciones externas tipo Web Service se estiman entre 2 y 4 h por integracion segun complejidad.