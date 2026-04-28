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

- Tasa base: USD 12 / hora
- Aplicar a todos los presupuestos futuros salvo indicacion contraria del cliente.
- Si el cliente negocia descuento, no bajar de USD 10/h sin aprobacion explicita.

## Rangos de referencia por tipo de modulo

- Ajuste puntual (campo, validacion, logica menor): 0.5 a 1 h - USD 7 a 14
- ABM simple (sin relaciones, sin logica): 1 a 2 h - USD 14 a 28
- ABM intermedio (con relaciones y validaciones): 2 a 4 h - USD 28 a 56
- Modulo con workflow / estados: 4 a 6 h - USD 56 a 84
- Modulo financiero o con logica compleja: 5 a 8 h - USD 70 a 112

## Calibracion incremental Abril 2026 (dataset real compartido)

Fuente: dataset de modulos de Delicias Naturales, Recotrack, Lumitrack y Piapartments.
Ver detalle por modulo en /docs/<proyecto>/definiciones/4-presupuestador.md de cada proyecto.

Regla de normalizacion obligatoria:
- Si una referencia historica viene con contingencia del 30% incluida, convertir primero a horas base: Horas base = Horas finales / 1.30.
- Evitar doble contingencia: no volver a aplicar 15% o 25% sobre una referencia ya inflada, salvo justificacion explicita por riesgo nuevo.

Resumen de rangos observados (horas finales con 30% incluida):
- ABM simple: 2 a 4 h (moda observada: 2 h).
- ABM intermedio: 5 a 7 h (moda observada: 6.5 h).
- ABM complejo: 10 a 15 h.
- ABM complejo con padre/hijos detalle: 10 h como referencia inicial.
- Notificaciones SignalR acotadas: 4.5 h como referencia inicial.

Resumen de rangos base equivalentes (sin contingencia):
- ABM simple: 1.5 a 3.1 h.
- ABM intermedio: 3.8 a 5.4 h.
- ABM complejo: 7.7 a 11.5 h.
- ABM complejo con padre/hijos detalle: 7.7 h.
- Notificaciones SignalR acotadas: 3.5 h.

Reglas practicas de uso del dataset:
- Si el pedido nuevo coincide con un modulo comparable, leer primero el 4-presupuestador.md del proyecto de referencia y luego ajustar por drivers reales.
- Si la estimacion final supera 20% del techo historico de la banda elegida, documentar causa puntual.
- Si no hay modulo comparable claro, declarar incertidumbre y devolver rango por fase.

### Modificacion sobre modulo existente
- Agregar campo simple: 0.5 h - USD 7
- Agregar regla de negocio: 1 a 2 h - USD 14 a 28
- Nuevo reporte o exportacion: 1 a 2 h - USD 14 a 28
- Migracion EF requerida: sumar 0.5 h - USD 7 por cada migracion

## Formato de entrega al cliente

- Documento simple, sin jerga tecnica
- Agrupado por area funcional (no por capa tecnica)
- Incluir tabla: Area | Horas | USD
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

## Notas de calibracion

- Parametros calibrados en base a tres proyectos reales / presupuestados en 2025.
- Total combinado base: 175 horas - USD 2.450 - tasa efectiva confirmada USD 14/h.
- Total combinado con contingencias: 190 horas - USD 2.660.
- Revisar y actualizar la tasa cada 6 meses o ante cambio de contexto economico.
- Para proyectos mayores a 50h aplicar contingencia adicional del 15%.
- Para proyectos que incluyan migracion de datos, agregar entre 20% y 30% al total.
- Facturacion AFIP es exclusion estandar salvo excepcion documentada (ver Proyecto 3 Delicias Naturales).
- Integraciones externas tipo Web Service se estiman entre 2 y 4 h por integracion segun complejidad.