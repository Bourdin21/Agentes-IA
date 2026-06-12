# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-06-11 15:00 - analista-funcional
- Etapa: Discovery + Analisis
- Cambio: relevamiento inicial del proyecto Yoga sobre el pedido del cliente (sistema de gestión de suscripciones para escuela de yoga). Tres decisiones de alcance confirmadas con el cliente: (1) liquidación de profesores por clases dictadas con tarifa por hora, (2) control de morosidad por estado de cuota (pendiente/pagada/vencida) con listado de deudores, (3) dashboard de inicio con foco financiero. Alcance base de 9 bloques funcionales, 14 casos de uso, criterios de aceptación y banderas (EF sí, integración externa no, máquina de estados acotada, migración de datos no).
- Motivo: pedido del cliente — sistema web mono-rol Administrador para suscripciones, cobranzas, liquidación de profesores y caja.
- Impacto en capas: Presentacion, Negocio y Datos (sistema nuevo completo).
- Riesgos/supuestos: pago total único por cuota (sin parciales); generación de cuotas manual por período; sin agenda/asistencia; moneda única ARS.

### 2026-06-11 15:30 - disenador-funcional
- Etapa: Diseno
- Cambio: 10 pantallas con wireframes textuales, 11 ViewModels, máquinas de estado de suscripción (Activa/Pausada/Finalizada), cuota (Pendiente/Pagada con Vencida derivada por fecha) y liquidación (Pendiente/Pagada), y 14 historias de usuario con criterios de aceptación verificables (fuente de verdad para QA).
- Motivo: bajar el análisis aprobado a diseño implementable, con el dashboard financiero como pantalla de inicio.
- Impacto en capas: Presentacion (pantallas/ViewModels), Negocio (contratos de generación/pago/liquidación), Datos (requerimientos por pantalla).
- Riesgos/supuestos: estado Vencida derivado (sin job nocturno); carga rápida de clases sin agenda.

### 2026-06-11 16:00 - arquitecto-mvc
- Etapa: Arquitectura
- Cambio: arquitectura sobre blankproject OlvidataSoft (.NET 10 + EF Core + MySQL 8): 8 entidades nuevas (~14–15 tablas con Identity), 5 servicios de Application, migración EF inicial + seed (5 planes, roles, admin). Snapshot de precio de plan en cuota y de tarifa en liquidación para no recalcular documentos al cambiar valores. Operaciones transaccionales documento + movimiento de caja. Índices únicos para idempotencia. Gate aprobado para presupuesto.
- Motivo: validar soporte técnico del diseño y declarar EF/permisos antes de estimar.
- Impacto en capas: Domain/Application/Infrastructure/Web.
- Riesgos/supuestos: volumen bajo (1 usuario, decenas de alumnos); pagos parciales declarados como cambio de alcance futuro.

### 2026-06-11 16:30 - presupuestador
- Etapa: Presupuesto
- Cambio: presupuesto inicial v1 con anclaje histórico (Paso 0 sobre recotrack/lumitrack/ganaderia/delicias y rangos de 27-parametros): 9 módulos, M total 42.0 h, PERT base 43.92 h, techo interno 49.49 h, fórmula vigente M × $16.80 → USD 705,60 módulos + USD 100 tokens IA = **USD 806** + plan de mantenimiento PRO USD 300/año (~14–15 tablas). Sanity check del total vs delicias-naturales: 4.88 vs 5.0 h base/módulo (ratio 0.98, sin recalibrar). Sin ítems de riesgo alto (sin migración de datos ni integraciones). Documento cliente emitido en /docs/yoga/presupuesto.md.
- Motivo: cierre de la cadena 1→4 para entregar presupuesto al cliente antes de implementar.
- Impacto en capas: n/a (documento).
- Riesgos/supuestos: gatillos de reestimación declarados (pagos parciales, recordatorios a alumnos, acceso de alumnos/profesores, pasarela de pagos); pendiente aprobación del cliente y cierre de calibración estimado vs real al fin del sprint.

### 2026-06-12 10:00 - presupuestador / arquitecto-mvc
- Etapa: Presupuesto (v2 — reglas nuevas de formato comercial)
- Cambio: (1) Nuevas reglas globales en 27-presupuesto-parametros, 04-presupuesto.prompt y presupuesto-mvc.agent: todo presupuesto se divide en Etapa 1 (MVP operable) y Etapa 2 (resto del alcance), con subtotal por etapa, tokens IA una sola vez en Etapa 1, pago 50/50 por etapa y eliminación de la cláusula "validez 30 días". (2) Presupuesto Yoga rehecho por etapas: Etapa 1 MVP (acceso, planes, alumnos, suscripciones, cuotas/pagos/deudores) USD 436 (336 módulos + 100 tokens IA); Etapa 2 (profesores, clases, liquidaciones, cuenta corriente, dashboard) USD 370; total sin cambios USD 806 + USD 300/año PRO. (3) Nota de arquitectura: en Etapa 1 el pago solo marca la cuota; la cuenta corriente de Etapa 2 hace backfill de los ingresos de cuotas pagadas (incluido en módulo 8, sin cambio de horas).
- Motivo: pedido del cliente interno — presupuestos en dos etapas (MVP + resto) y sin cláusula de validez, aplicable a todos los presupuestos a partir de ahora.
- Impacto en capas: n/a (documentos y parámetros; decisión de secuencia de entrega).
- Riesgos/supuestos: durante el MVP la pantalla de inicio es el listado de cuotas del período; el dashboard llega con la Etapa 2.

### 2026-06-12 11:00 - presupuestador
- Etapa: Presupuesto (v3 — tokens IA implícitos)
- Cambio: nueva regla global en 27-presupuesto-parametros (también agente y prompt 04): el cargo fijo de tokens IA (USD 100) deja de mostrarse como línea separada y pasa a ser implícito, prorrateado proporcionalmente en los precios por área de la Etapa 1. Yoga reexpresado: Etapa 1 = 33/44/98/109/152 (factor 436/336 ≈ 1,2976 sobre los precios exactos de módulos), subtotal USD 436 sin cambios; Etapa 2 y total sin cambios (370 / 806). Documento cliente actualizado sin mención de tokens.
- Motivo: pedido del cliente interno — el costo de IA debe estar implícito en el presupuesto.
- Impacto en capas: n/a (documentos y parámetros).
- Riesgos/supuestos: el detalle del prorrateo queda solo en la memoria interna 4-presupuestador.md.
