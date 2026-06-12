# Metadata del proyecto

- nombre: Yoga
- fecha_inicio: 2026-06-11
- estado: activo
- owner: Joaquín Bourdin
- descripcion: Sistema web de gestión de suscripciones para una escuela de yoga. Planes de entrenamiento de 1 a 5 horas semanales con precio propio, alumnos suscritos a planes, cuotas mensuales con estados (pendiente/pagada/vencida) y registro de pagos, profesores con registro de clases dictadas y liquidación por horas, cuenta corriente de ingresos y egresos (pagos de alumnos, gastos, retiros, pagos a profesores) y dashboard de inicio con KPIs de foco financiero. Un solo rol operativo: Administrador.
- ruta_definiciones: /docs/yoga/definiciones

## Archivos de memoria por agente
- analista-funcional: /docs/yoga/definiciones/1-analista-funcional.md
- disenador-funcional: /docs/yoga/definiciones/2-disenador-funcional.md
- arquitecto-mvc: /docs/yoga/definiciones/3-arquitecto-mvc.md
- presupuestador: /docs/yoga/definiciones/4-presupuestador.md
- implementador: /docs/yoga/definiciones/5-implementador.md
- qa: /docs/yoga/definiciones/6-qa.md
- documentador: /docs/yoga/definiciones/7-documentador.md

## Fuentes del relevamiento
- Pedido inicial del cliente (2026-06-11): registro de suscripciones de alumnos, planes de 1/2/3/4/5 hs semanales con valor diferente, pagos mensuales registrados por el administrador, cuenta corriente con ingresos y egresos (retiros, gastos, pagos a profesores), rol único administrador, dashboard de inicio con KPIs.
- Decisiones de relevamiento confirmadas con el cliente (2026-06-11): liquidación de profesores por clases dictadas (tarifa por hora), control de estado de cuotas por mes (pagada/pendiente/vencida) con listado de deudores, dashboard con foco financiero (ingresos vs egresos mensuales, saldo acumulado, evolución anual).
