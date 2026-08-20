# Memoria - Analista funcional

## Proyecto: estudio-contable-maribel-garcia
## Ultima actualizacion: 2026-08-20

## Definiciones vigentes

### Contexto del lead
Estudio contable chico en Bariloche (Neuquen 1060, San Carlos de Bariloche). Entro por outbound (campana "Estudios contables"). Primer contacto via WhatsApp, cuestionario de calificacion de 3 preguntas (20/08). Las respuestas llegaron **desordenadas respecto de las preguntas** — reconstruccion segun contenido, no segun el orden literal de los mensajes:

1. **Que es lo que mas le complica hoy**: "Me interesa IA para conciliar Banco y Mercado Pago" — dolor real y especifico: cruzar movimientos del extracto bancario contra los movimientos de Mercado Pago para el cierre contable.
2. **Con que lo maneja hoy**: "Excel + claude" — ya usan Excel para llevar el registro y recurren a Claude (u otra IA conversacional) de forma manual/ad-hoc para ayudarse con la tarea, no un sistema dedicado.
3. **Cuantas personas lo van a usar**: "1 o 2 personas" (llego como mensaje adicional post-cierre del flujo, no como respuesta directa a la pregunta 3).
4. Fuera de las 3 preguntas de calificacion, el lead pidio directamente costos: **"Me podrian enviar costos?"** — a diferencia de otros leads del outbound, este SI pidio precio de forma explicita durante la calificacion. Justifica enviar presupuesto con precio, no solo alcance funcional.

### Tipo de sistema
**Herramienta de conciliación de movimientos financieros** (bank/payment reconciliation) — NO un sistema de gestión contable integral, NO un ERP, NO un reemplazo del Excel para todo lo que hace el estudio hoy. Alcance puntual y acotado: cruzar dos fuentes de movimientos (Banco y Mercado Pago) y clasificar cada uno como conciliado / a confirmar / sin conciliar. Esta clasificacion de tipo de sistema define el limite de alcance para todas las etapas siguientes — cualquier pedido que se aleje de "cruzar y clasificar movimientos de dos fuentes" (ej. asientos contables, gestion de clientes, facturacion) es, por definicion, fuera de este alcance y se cotiza aparte.

### Lectura del dolor real
El pedido es especifico y acotado: conciliar (emparejar/cruzar) los movimientos de dos fuentes — extracto bancario y resumen de Mercado Pago — para detectar que esta acreditado en ambos lados, que falta, y que no coincide. Hoy lo hacen a mano en Excel, ayudandose con una IA conversacional de forma manual (copiar/pegar, pedir ayuda puntual), no con una herramienta dedicada. El gancho "IA" que el lead menciono no es un capricho — es literalmente lo que ya intenta hacer manualmente hoy con Claude, sin una herramienta que lo automatice.

### Modulos/features analizados
- Importacion de extracto bancario (archivo exportado del banco, formato variable segun banco).
- Importacion de extracto/resumen de Mercado Pago (archivo exportado de MP).
- Motor de conciliacion: emparejamiento automatico por monto + fecha (con tolerancia de dias, ya que las acreditaciones pueden demorar) entre movimientos bancarios y de MP.
- Asistencia por IA para los casos que el emparejamiento automatico no resuelve solo (montos que no calzan exacto, fechas mas separadas, conceptos ambiguos) — el gancho de "IA" del lead, tratado como mejora sobre una base de matching deterministico, no como reemplazo de ella (ver nota tecnica en 3-arquitecto-mvc.md sobre por que).
- Vista de resultados de conciliacion: conciliado / sugerido (a confirmar) / sin conciliar.
- Confirmacion o rechazo manual de una sugerencia.
- Exportacion de reporte de conciliacion (Excel/PDF) para el cierre contable.
- Usuarios: 1-2 personas, sin necesidad de roles diferenciados complejos (equipo muy chico).

### Reglas funcionales acordadas
- Un movimiento bancario y un movimiento de Mercado Pago se consideran "conciliados" cuando coinciden en monto exacto y la fecha esta dentro de una tolerancia configurable (a definir con el cliente, ej. 0-5 dias).
- Cuando no hay match exacto pero hay candidatos razonables (monto similar/fecha cercana), el sistema los marca como "sugerido" para que el contador confirme o rechace manualmente — nunca concilia automaticamente algo ambiguo sin confirmacion humana.
- Todo movimiento que no encuentra ningun candidato queda en "sin conciliar", visible para revision manual.

### Criterios de aceptacion vigentes
- El contador puede importar un extracto bancario y un extracto de Mercado Pago (archivos exportados de cada plataforma) y ver los movimientos cargados.
- El sistema empareja automaticamente los movimientos que coinciden en monto y fecha dentro de la tolerancia definida, sin intervencion manual.
- Los movimientos que no calzan exacto pero tienen candidatos razonables aparecen como "sugerido", con opcion de confirmar o rechazar cada uno.
- Se puede exportar un reporte con el detalle de conciliados/sugeridos-confirmados/sin conciliar.

### Supuestos y dependencias
- **[SUPUESTO — pendiente, confirmar con el lead]** Formato exacto del extracto bancario: se asume archivo exportable (CSV o Excel) desde el home banking, con columnas de fecha/monto/concepto como minimo. Si el banco solo entrega PDF sin exportacion tabular, el parser requiere trabajo adicional no cotizado aqui.
- **[SUPUESTO — pendiente, confirmar con el lead]** Formato del extracto de Mercado Pago: se asume el export estandar de MP (CSV/Excel de "Actividad" o "Reportes"), con columnas de fecha/monto/concepto/ID de operacion.
- **[SUPUESTO]** "1 o 2 personas" se toma como 2 usuarios para no quedar corto en el dimensionamiento (login basico, sin roles diferenciados — ambos usuarios ven y hacen lo mismo, dado el tamano del equipo).
- **[SUPUESTO]** El alcance es conciliacion, no contabilidad completa — no incluye asientos contables, libro IVA, ni presentaciones ante AFIP/ARCA (fuera del pedido explicito del lead).
- **[SUPUESTO — pendiente, confirmar con el lead]** No se menciono si conciliar solo Banco+MercadoPago o si en el futuro quieren sumar otras cuentas/medios de cobro (tarjetas, otras billeteras) — el diseno deja la puerta abierta pero el alcance cotizado es especificamente Banco + Mercado Pago.
- Sin discovery por llamada/reunion todavia — este analisis se arma sobre 3 respuestas de un cuestionario automatico de calificacion (recibidas fuera de orden), no una entrevista de relevamiento completa.

### Exclusiones confirmadas
- Asientos contables, libro IVA, presentaciones AFIP/ARCA (no mencionado, no cotizado — exclusion fija del estudio ademas).
- Migracion de datos historicos de conciliaciones ya hechas en Excel (exclusion fija del estudio salvo acuerdo aparte).
- Aplicacion movil nativa (exclusion fija del estudio — se accede via navegador web).
- Conciliacion con otras cuentas/medios de pago mas alla de Banco + Mercado Pago (puede evaluarse a futuro).

## Historial de ajustes
- 2026-08-20: primera version, a partir del cuestionario de calificacion outbound (respuestas desordenadas, reconstruidas por contenido). Pendiente de confirmacion con el lead antes de iniciar implementacion.
