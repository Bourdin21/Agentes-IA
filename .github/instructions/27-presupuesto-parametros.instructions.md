---
description: Parametros base de estimacion y presupuesto. Calibrado sobre tres proyectos reales finalizados en 2025.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# Parametros de referencia - Proyectos calibrados 2025

## Proyecto de referencia 1 - Eleven La Plata

- Sistema: Gestion Integral Eleven La Plata (27 modulos funcionales, Clean Architecture, .NET 10 + MySQL)
- Horas reales totales: 50 horas
- Costo total real: USD 850
- Tasa efectiva: USD 17 / hora
- Perfil: Sistema de gestion general. Modulos de complejidad media. Sin maquinas de estado complejas ni parsers externos.
- Fecha de cierre: Julio 2025

## Proyecto de referencia 2 - VinoSeFue

- Sistema: Gestion Comercial de Vinos VinoSeFue (16 modulos funcionales, Clean Architecture, .NET 10 + MySQL)
- Horas reales totales: 30 horas
- Costo total real: USD 500
- Tasa efectiva: USD 17 / hora
- Perfil: Sistema comercial con alta complejidad por modulo. Incluye maquinas de estados (Pedidos + CompraProveedor), flujo de concesiones con ajuste de cuenta corriente, importacion automatica de catalogo (HTML / PDF / CSV) con Background Worker, ledger de movimientos, 6 migraciones EF, 17 entidades de dominio, 13 servicios, 40 vistas.
- Fecha de cierre: Julio 2025

## Proyecto de referencia 3 - Delicias Naturales

- Sistema: Gestion Comercial Delicias Naturales (19 modulos funcionales, ASP.NET MVC 5 + .NET Framework 4.7.2 + EF6 + MySQL)
- Horas estimadas base (sin contingencia): 95 horas
- Horas totales con contingencia 15%: 110 horas
- Costo total estimado: USD 1.870
- Tasa efectiva: USD 17 / hora
- Perfil: Sistema comercial de mayor escala del dataset. 26 entidades, 19 controladores, 25 migraciones EF evolutivas, 5 integraciones AFIP (facturacion electronica A/B/C + padron + percepcion IVA), maquinas de estado multiples (Ventas, Pedidos y Compras con 3 estados cada una), SignalR, reportes PDF, soft-delete. Facturacion AFIP incluida como excepcion documentada.
- Fecha de presupuesto: Junio 2025
- Estado: Presupuestado sobre sistema existente. Estimacion retrospectiva validada por el cliente

## Conclusion de calibracion

- Los tres proyectos confirman la tasa de USD 17 / hora como referencia solida.
- La tasa es independiente de la complejidad: proyectos mas complejos se expresan en mas horas, no en mayor tarifa.
- VinoSeFue tiene menor cantidad de modulos (16) pero mayor complejidad promedio por modulo.
- Delicias Naturales es el proyecto de mayor escala: 95h base, 5 integraciones AFIP, 25 migraciones EF.
- La contingencia del 15% se aplica correctamente desde los 50h de base en adelante.

## Tasa vigente

- Tasa base: USD 17 / hora
- Aplicar a todos los presupuestos futuros salvo indicacion contraria del cliente.
- Si el cliente negocia descuento, no bajar de USD 14/h sin aprobacion explicita.

## Distribucion proporcional de referencia

### Proyecto 1 - Eleven La Plata

| Area funcional | % del total | Horas ref. | USD ref. |
|---|---|---:|---:|
| Arquitectura y base del sistema | 26.0% | 13 h | 221 |
| Operaciones comerciales | 26.0% | 13 h | 221 |
| Servicio tecnico | 20.0% | 10 h | 170 |
| Modulo financiero | 18.0% | 9 h | 153 |
| Dashboard, reportes y sistema | 10.0% | 5 h | 85 |
| TOTAL | 100% | 50 h | 850 |

### Proyecto 2 - VinoSeFue

| Area funcional | % del total | Horas ref. | USD ref. |
|---|---|---:|---:|
| Arquitectura y base del sistema | 21.7% | 6.5 h | 110 |
| Operaciones comerciales | 39.1% | 11.7 h | 199 |
| Gestion de compras al proveedor | 8.7% | 2.6 h | 44 |
| Modulo financiero | 13.0% | 3.9 h | 66 |
| Dashboard, reportes y sistema | 17.4% | 5.2 h | 88 |
| TOTAL | 100% | 30 h | 500 |

### Proyecto 3 - Delicias Naturales

| Area funcional | % del total | Horas ref. | USD ref. |
|---|---|---:|---:|
| Arquitectura y base del sistema | 12.6% | 12 h | 204 |
| Operaciones comerciales | 25.3% | 24 h | 408 |
| Compras, proveedores y stock | 16.8% | 16 h | 272 |
| Modulo financiero | 22.1% | 21 h | 357 |
| Dashboard, reportes y notificaciones | 10.5% | 10 h | 170 |
| Migraciones EF evolutivas (23 x 0.5h) | 12.6% | 12 h | 204 |
| SUBTOTAL BASE | 100% | 95 h | 1.615 |
| Contingencia 15% (proyecto mayor a 50 h) | | +15 h | +255 |
| TOTAL CON CONTINGENCIA | | 110 h | 1.870 |

### Promedio combinado ponderado por horas base (50h + 30h + 95h = 175h)

| Area funcional | % ponderado | Ref. por cada 50h |
|---|---|---|
| Arquitectura y base del sistema | 18% | 9 h - 153 USD |
| Operaciones comerciales | 28% | 14 h - 238 USD |
| Gestion de compras / servicio tecnico | 16% | 8 h - 136 USD |
| Modulo financiero | 19% | 9.5 h - 162 USD |
| Dashboard, reportes y sistema | 12% | 6 h - 102 USD |
| Migraciones EF evolutivas | 7% | 3.5 h - 60 USD |

## Reglas de escala para nuevos presupuestos

## Definicion operativa de complejidad ABM (obligatoria)

- ABM simple:
- Entidad con campos escalares (texto, numero, fecha, booleano), sin colecciones hijas.
- Validaciones basicas de formulario.
- Puede tener clave foranea simple, pero sin edicion compuesta de detalle en la misma pantalla.

- ABM intermedio:
- Entidad con una o mas relaciones a otras entidades (many-to-one o one-to-one) y validaciones adicionales por relacion.
- Incluye reglas de negocio moderadas en alta/edicion.
- No incluye administracion compleja de listas hijas dentro del mismo flujo.

- ABM complejo:
- Entidad raiz con detalle (one-to-many o many-to-many), con lista de referencias a otras entidades hijas.
- Requiere consistencia entre cabecera y detalle, reglas transaccionales o validaciones cruzadas.
- Puede incluir estados de proceso o flujo operativo acoplado.

Regla de clasificacion rapida:
- Sin detalle ni relaciones complejas: ABM simple.
- Con relaciones y validaciones relacionales, sin detalle hijo editable: ABM intermedio.
- Con cabecera + detalle editable y consistencia transaccional: ABM complejo.

### Por modulo individual (nuevo modulo simple)
- Catalogo / ABM basico: 1 a 2 h - USD 17 a 34
- ABM con relaciones y validaciones: 2 a 4 h - USD 34 a 68
- Modulo con workflow / estados: 4 a 6 h - USD 68 a 102
- Modulo financiero o con logica compleja: 5 a 8 h - USD 85 a 136

## Calibracion incremental Abril 2026 (dataset real compartido)

Fuente:
- Dataset de modulos de Delicias Naturales, Recotrack, Lumitrack y Piapartments.
- Las horas reportadas ya incluyen contingencia y margen de errores/devoluciones del 30%.

Regla de normalizacion obligatoria:
- Si una referencia historica viene con contingencia del 30% incluida, convertir primero a horas base: Horas base = Horas finales / 1.30.
- Evitar doble contingencia: no volver a aplicar 15% o 25% sobre una referencia que ya esta inflada por contingencia, salvo justificacion explicita por riesgo nuevo.

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
- Si el pedido nuevo coincide con un modulo comparable, usar primero la banda historica y luego ajustar por drivers reales (permisos, estados, integraciones, migraciones EF).
- Si la estimacion final supera 20% del techo historico de la banda elegida, documentar causa puntual.
- Si no hay modulo comparable claro, declarar incertidumbre y devolver rango por fase.

### Modificacion sobre modulo existente
- Agregar campo simple: 0.5 h - USD 8
- Agregar regla de negocio: 1 a 2 h - USD 17 a 34
- Nuevo reporte o exportacion: 1 a 2 h - USD 17 a 34
- Migracion EF requerida: sumar 0.5 h - USD 8 por cada migracion

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
- Total combinado base: 175 horas - USD 2.765 - tasa efectiva confirmada USD 17/h.
- Total combinado con contingencias: 190 horas - USD 3.220.
- Revisar y actualizar la tasa cada 6 meses o ante cambio de contexto economico.
- Para proyectos mayores a 50h aplicar contingencia adicional del 15%.
- Para proyectos que incluyan migracion de datos, agregar entre 20% y 30% al total.
- Facturacion AFIP es exclusion estandar salvo excepcion documentada (ver Proyecto 3 Delicias Naturales).
- Integraciones externas tipo Web Service se estiman entre 2 y 4 h por integracion segun complejidad.
