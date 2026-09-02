# Guión — Reunión de Discovery con Contadores BMA

Objetivo: cerrar las preguntas abiertas de `definiciones/1-analista-funcional.md` para poder cerrar Análisis y pasar a Diseño. Sin esto cerrado, la Fase 0 del plan de acción no puede arrancar con alcance real (hoy corre sobre hipótesis).

**Participantes sugeridos**: no solo el owner/socio del estudio — al menos 1-2 personas que hacen las tareas operativas día a día (quien concilia bancos, quien liquida sueldos, quien arma balances). El relevamiento de tareas (Bloque 2) pierde precisión si solo lo responde quien no ejecuta la tarea.

**Duración estimada**: 45-60 min.

---

## Bloque 1 — Canal de integración con Thomson Reuters (pregunta abierta 2 y 3)

Esto es lo que más condiciona el resto del proyecto — determina si algún día se puede avanzar a Opción B/C, o si el sistema queda permanentemente en Opción A.

1. ¿Contadores BMA tiene un ejecutivo de cuenta o contacto comercial asignado en Thomson Reuters/Bejerman? ¿Cómo se llama y cómo se lo contacta?
2. ¿El estudio tiene a mano el contrato/acuerdo de licencia firmado de Bejerman Web/Onvio? (Necesario para confirmar el texto exacto de la cláusula de uso — la que usamos como referencia es la versión global de Thomson Reuters, no la argentina puntual).
3. Acción a coordinar en esta reunión (no es una pregunta, es una tarea a asignar): quién del estudio envía la consulta formal a Thomson Reuters preguntando si existe un canal de integración autorizada para Bejerman Web/Onvio Argentina (hay precedente: existe una API pública equivalente para la versión Brasil). Definir quién la manda y para cuándo.

---

## Bloque 2 — SOS Contador y su relación con Bejerman Web (preguntas abiertas 6 y 7)

Agregado 2026-08-31: el estudio también usa mucho SOS Contador, y el bot de consultas tiene que tener su documentación cargada además de la de Bejerman. Antes de diseñar el adaptador para SOS Contador (que, a diferencia de Bejerman, sí tiene API oficial para integraciones — ver research en `definiciones/1-analista-funcional.md`), hace falta confirmar cómo se usan ambos sistemas juntos:

1. ¿Bejerman Web genera datos (ventas, compras, sueldos) que después se vuelven a cargar a mano en SOS Contador para liquidar/presentar impuestos? Ejemplo para contrastar: "cargamos las ventas del mes en Bejerman y las volvemos a tipear/importar en SOS para armar el IVA" (variante con traslado manual) vs. "los clientes que llevamos en Bejerman quedan ahí, los que llevamos en SOS quedan en SOS, no se mezclan" (variante sin traslado).
2. ¿Usan el módulo de Sueldos de Bejerman, el de SOS Contador (Sueldos v2), o los dos para el mismo cliente? Si es "los dos", ahí hay una duplicación de carga que es candidata directa a automatizar.
3. ¿Para qué usa el estudio específicamente SOS Contador hoy? (impositivo, contabilidad, gestión, sueldos, todo lo anterior) — para no asumir que se usa igual que se documenta en su sitio.
4. Mismas preguntas de "Manuales / soporte" del Bloque 3 (dudas frecuentes, manual propio) pero para SOS Contador: ¿a quién le preguntan hoy cuando no saben hacer algo ahí?

---

## Bloque 3 — Catálogo real de tareas a automatizar (pregunta abierta 4)

El catálogo que propusimos (conciliaciones, impuestos, balances, sueldos, manuales) es una **hipótesis a validar**, no un relevamiento confirmado. Para el relevamiento fino tarea por tarea, se complementa con `cuestionario-discovery-empleados.md` (uno por cada empleado que usa Bejerman día a día, no solo los referentes de esta reunión). En la reunión grupal alcanza con validar el panorama general por área, con estas variantes de alcance posible — que el estudio confirme, corrija o descarte por analogía:

**Conciliaciones bancarias**
- Opción A: conciliación 1 a 1 por cliente/empresa que atiende el estudio (cada cliente tiene su propio banco y sus propios movimientos).
- Opción B: conciliación centralizada de varias cuentas/bancos en paralelo para el mismo cliente.
- Preguntas: ¿cuántas conciliaciones bancarias hacen por mes? ¿de cuántos clientes/empresas distintas? ¿qué bancos usan sus clientes (para saber cuántos formatos de export distintos hay que soportar)?

**Impuestos (IVA, Ganancias u otros)**
- Opción A: el estudio arma el borrador de la declaración y el contador la revisa y presenta manualmente en el sistema de AFIP/ARCA.
- Opción B: además arma los papeles de trabajo/planillas de cálculo previas (retenciones, percepciones) que hoy se arman a mano en Excel.
- Preguntas: ¿qué impuestos llevan más tiempo hoy? ¿hay algún paso puntual (no todo el proceso) que sea el verdadero cuello de botella?

**Balances**
- Opción A: cruces y validaciones sobre datos que ya están en Bejerman Web (papeles de trabajo).
- Opción B: incluye también la carga/actualización de datos en Bejerman Web a partir de otras fuentes.
- Preguntas: ¿con qué frecuencia arman balances (mensual, trimestral, anual)? ¿cuánto tiempo insume hoy por cliente?

**Sueldos/RRHH**
- Ya hay precedente directo: `contadores-bma-conversor` automatiza la conversión de la liquidación para SERVICIO TERAPIA RENAL S.A. Pregunta: ¿ese mismo proceso se repite para otros clientes del estudio con formatos de salida distintos? ¿hay otras tareas de sueldos además de esa conversión (ej. validar el cálculo, no solo convertir el formato)?

**Manuales / soporte de uso de Bejerman Onvio y SOS Contador**
- Pregunta abierta simple: ¿hoy a quién le preguntan cuando no saben cómo hacer algo en Bejerman Web/Onvio o en SOS Contador? ¿Tienen algún manual propio (interno, no el oficial de cada proveedor) con procedimientos del estudio?

**Otras tareas no contempladas** (pregunta abierta, sin variantes — para no anclar la respuesta): ¿hay alguna tarea repetitiva y que consuma mucho tiempo que no esté en esta lista?

---

## Bloque 4 — Organización y alcance (pregunta abierta 5)

1. ¿Cuántas personas trabajan en el estudio y usan Bejerman Web/Onvio y/o SOS Contador en su día a día?
2. ¿Hay roles diferenciados (ej. alguien solo hace sueldos, otro solo impuestos) o todos hacen un poco de todo?
3. ¿Cuántos clientes/empresas atiende el estudio en total? (dimensiona el volumen real de cada tarea del Bloque 3)

---

## Bloque 5 — Priorización del agente piloto (Fase 0 del plan de acción)

Con lo relevado en los Bloques 2 y 3, elegir en la reunión (no después) cuál es el mejor candidato a agente piloto, usando estos criterios:
- Mayor volumen/repetitividad (más tiempo ahorrado por corrida)
- Menor riesgo si falla (nada que afecte directamente una presentación legal/impositiva)
- Depende de un archivo que el empleado ya exporta hoy, o de la API oficial de SOS Contador (compatible con Opción A o con el adaptador de SOS, sin esperar ninguna autorización de Thomson Reuters)

Candidatos hipotéticos a confirmar/descartar: conciliación bancaria, el asistente de manuales/soporte (no depende de ningún dato del cliente, es el de menor riesgo absoluto), o el traslado de datos Bejerman→SOS Contador si el Bloque 2 confirma que hoy se hace a mano.

---

## Bloque 6 — Restricciones y expectativas

1. Presupuesto de referencia que el estudio tiene en mente para la Fase 0 (piloto) — para calibrar alcance antes de que el presupuestador arme el número formal.
2. Timeline deseado: ¿hay alguna fecha (cierre de ejercicio, vencimiento impositivo) que convenga usar como objetivo del piloto?
3. Confidencialidad: los datos que procesarían los agentes son de clientes del estudio (terceros), no del estudio mismo — confirmar si hay alguna restricción contractual del estudio hacia sus propios clientes sobre el uso de herramientas externas/IA con sus datos.

---

## Checklist de cierre — qué tiene que quedar resuelto para pasar a Diseño

- [ ] Contacto en Thomson Reuters identificado y consulta sobre canal de integración autorizada enviada (o agendada con fecha)
- [ ] Relación Bejerman Web ↔ SOS Contador confirmada (traslado de datos sí/no, uso de Sueldos duplicado sí/no)
- [ ] Catálogo de tareas confirmado (Bloque 3), con volumen aproximado por tarea
- [ ] Cantidad de empleados y clientes del estudio confirmada
- [ ] Agente piloto de Fase 0 elegido
- [ ] Presupuesto de referencia y timeline deseado relevados
- [ ] Restricciones de confidencialidad sobre datos de clientes del estudio relevadas
