---
description: Parametros base de estimacion y presupuesto. Calibrado sobre tres proyectos reales finalizados en 2025.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# Parametros de referencia - Proyectos calibrados 2025

## Proyecto de referencia 1 - Eleven La Plata

- Sistema: Gestion Integral Eleven La Plata (27 modulos funcionales, Clean Architecture, .NET 10 + MySQL)
- Horas reales totales: 50 horas
- Costo total real: USD 700
- Tasa efectiva: USD 14 / hora
- Perfil: Sistema de gestion general. Modulos de complejidad media. Sin maquinas de estado complejas ni parsers externos.
- Fecha de cierre: Julio 2025

## Proyecto de referencia 2 - VinoSeFue

- Sistema: Gestion Comercial de Vinos VinoSeFue (16 modulos funcionales, Clean Architecture, .NET 10 + MySQL)
- Horas reales totales: 30 horas
- Costo total real: USD 420
- Tasa efectiva: USD 14 / hora
- Perfil: Sistema comercial con alta complejidad por modulo. Incluye maquinas de estados (Pedidos + CompraProveedor), flujo de concesiones con ajuste de cuenta corriente, importacion automatica de catalogo (HTML / PDF / CSV) con Background Worker, ledger de movimientos, 6 migraciones EF, 17 entidades de dominio, 13 servicios, 40 vistas.
- Fecha de cierre: Julio 2025

## Proyecto de referencia 3 - Delicias Naturales

- Sistema: Gestion Comercial Delicias Naturales (19 modulos funcionales, ASP.NET MVC 5 + .NET Framework 4.7.2 + EF6 + MySQL)
- Horas estimadas base (sin contingencia): 95 horas
- Horas totales con contingencia 15%: 110 horas
- Costo total estimado: USD 1.540
- Tasa efectiva: USD 14 / hora
- Perfil: Sistema comercial de mayor escala del dataset. 26 entidades, 19 controladores, 25 migraciones EF evolutivas, 5 integraciones AFIP, maquinas de estado multiples, SignalR, reportes PDF, soft-delete.
- Fecha de presupuesto: Junio 2025
- Estado: Presupuestado sobre sistema existente. Estimacion retrospectiva validada por el cliente.

## Conclusion de calibracion

- Los tres proyectos confirman la tasa de USD 14 / hora como referencia solida.
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

Fuente:
- Dataset de modulos de Delicias Naturales, Recotrack, Lumitrack y Piapartments.
- Las horas reportadas ya incluyen contingencia y margen de errores/devoluciones del 30%.

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

Ejemplos usados para calibrar (horas finales con 30%):
- Delicias Naturales: Notificaciones SignalR 4.5 h, Gestion de pedidos 10 h, ABM Pedidos 10.5 h, ABM descuentos 6.5 h, ABM Pagos 5 h, ABM Compras 15 h, ABM Proveedores 7 h, ABM Ventas 10 h, ABM Categorias 2 h.
- Recotrack: ABM Empleados 6 h, ABM Usuarios 6 h, ABM Camiones 2 h, ABM Tipo Servicio 4 h, Multas Choferes 2 h, Accidentes Choferes 2 h, Horas Extras Choferes 2 h.
- Lumitrack: ABM Reclamo 6.5 h, ABM Cuadrilla 6.5 h, ABM Usuarios 6.5 h, ABM Tipo Servicio 6.5 h, ABM Materiales 6.5 h, ABM Relevamientos 10 h.
- Piapartments: ABM Edificios 6.5 h.

Reglas practicas de uso del dataset:
- Si el pedido nuevo coincide con un modulo comparable, usar primero la banda historica y luego ajustar por drivers reales.
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