---
description: Metodologia PACS (growth B2B) aplicada a Olvidata Soft — nicho, autoridad, mensajes conversacionales y sistematizacion. Obligatoria para toda estrategia comercial, mensaje de prospeccion o automatizacion de ventas. Vigente desde 2026-09-19.
applyTo: "**/*.md"
---

# 36 - Metodologia PACS aplicada a Olvidata

Aplica a `olvidata-ceo`, `olvidata-marketing`, `olvidata-sales`, `olvidata-cm` y al bot outbound/CRM (`docs/crm-olvidata/`). No aplica a la secuencia Discovery→Cierre de proyectos de cliente.

**Objetivo unico:** maximizar **reuniones agendadas (demos de 15 min) de forma consistente y repetible**, no volumen de mensajes. Encaja con el diagnostico vigente: el cuello de botella es tasa de cierre, no volumen (nunca mas de 8–10 contactos nuevos por semana). La demo en vivo es el momento de mayor conversion, asi que "reunion agendada" = la metrica que mueve el hito 2028 (43 clientes, recurrente que cubre el sueldo del Ministerio).

Los 4 pilares se aplican **en este orden**. Si falta el anterior, no se avanza al siguiente.

## 1. Nicho (P) — sin ICP definido no se genera nada

Antes de cualquier mensaje o accion, dejar escrito el ICP con estos 3 datos:

| Dato | Que precisar | Ejemplo valido | Ejemplo invalido |
|---|---|---|---|
| Industria | Rubro concreto del catalogo, no "pymes" | Ferreteria / corralon con stock propio | "Comercio" |
| Tamaño | Empleados o sucursales, y señal de dolor | 1–3 locales, 2–10 empleados, stock en Excel | "Empresa chica" |
| Decisor | Quien firma y paga | Dueño/a que atiende el local | "Encargado de sistemas" |

Reglas:
- **Un mensaje = un ICP.** Si el pedido no trae el nicho, el agente lo pregunta o propone uno del historial y lo marca como propuesto — no escribe copy generico.
- **Nicho por frente (decidido por Joaquin 2026-09-19):**

  | Frente | Segmento | Industria foco | Decisor |
  |---|---|---|---|
  | Build | Pymes | **Comercio minorista** (dietetica, ferreteria, decoracion/hogar: Delicias Naturales → La Platense → Marihogar) | Dueño/a |
  | Landing 2D | Pymes | Comercio minorista y pymes en general | Dueño/a |
  | Chatbots | Pymes y grandes empresas | Pyme: comercio minorista. Grande: a definir | Pyme: dueño/a. Grande: a definir |
  | AI Agents | Grandes empresas | A definir | A definir |
  | Landing 3D | Grandes empresas | A definir | A definir |

- **Pendiente para grandes empresas:** falta fijar tamaño (empleados/facturacion), industria y cargo del decisor. Hasta que Joaquin lo defina, el agente no genera prospeccion fria para AI Agents, Landing 3D ni Chatbots-grandes: pide el dato o propone uno marcado como propuesto.
- Los rubros del catalogo que quedan fuera del foco se atienden si llegan (referidos, inbound), pero no se sale a buscarlos.
- En pymes el decisor es casi siempre el **dueño/a**. No escribirle a "gerencia" ni a cargos que no firman.

## 2. Posicionamiento y confianza (A/C) — autoridad antes de pedir nada

Toda pieza (mensaje, post, Reel, template del bot) **refuerza autoridad antes del CTA**, con uno de estos tres elementos, del mismo nicho del destinatario:

1. **Caso real del mismo rubro** ("armé el sistema de una ferretería en La Plata que…") — solo con respaldo en `docs/` (regla de oro de `olvidata-cm`: nada se afirma sin respaldo documental; nada de metricas inventadas).
2. **Especificidad del dolor**: nombrar el problema con el vocabulario del rubro (ej. "el cierre de caja con el stock que no cuadra"), no funcionalidades.
3. **Prueba social concreta**: cantidad real de clientes del rubro, o referido con nombre si el que recomienda lo autorizo.

Si no hay caso del nicho, se usa el caso mas cercano diciendo que es de otro rubro — nunca se disfraza.

## 3. Mensajes conversacionales (C) — optimizar respuesta, no cierre

- **Breve**: primer mensaje de 2–4 lineas en WhatsApp/LinkedIn; email de prospeccion ≤ 80 palabras.
- **Conversacional**: primera persona de Joaquin, tono de persona que escribe a otra persona (regla de marca personal 2026-09-02). Nada de plantilla de venta dura, listas de features ni precio en el primer contacto.
- **Una sola pregunta o un solo CTA** por mensaje. El CTA es de bajo compromiso y compatible con el cierre pasivo: una pregunta sobre su dolor ("¿hoy el stock lo llevás en Excel?") o el ofrecimiento de la demo — **nunca pedir fecha/horario** (regla vigente de `olvidata-sales`).
- El primer mensaje busca **una respuesta**, no una venta. La secuencia es: respuesta → conversacion → demo agendada → propuesta.
- Follow-ups: se mantienen los topes vigentes (outbound: `olv_nurturing` a las 72 hs; post-propuesta: dia 3 y dia 6, despues se archiva). PACS no habilita mas insistencia.

## 4. Sistematizacion (S) — todo lo que se genera se mide

Todo output comercial de un agente sale con **su plan de tracking**, no solo el texto. Minimo:

- **Donde se registra**: CRM Olvidata (`docs/crm-olvidata/`) — `Contacto.CanalOrigen`, `Rubro`, `EstadoEmbudo`, `ReferidoPor`; las variantes de mensaje se cargan como `CampanaExperimento`/`TemplateWhatsApp` para comparar.
- **Etiqueta de la pieza**: `nicho` + `canal` + `variante` (ej. `ferreteria-outbound-v2`), para poder atribuir respuestas y demos a cada version.
- **Metricas por pieza/campaña** (en orden de importancia):
  1. Reuniones agendadas / contactos (la metrica objetivo).
  2. Tasa de respuesta / contactos.
  3. Demo → anticipo (objetivo vigente >30%).
- **Umbral de decision**: una variante se evalua recien con ≥ 20 contactos del mismo nicho; con menos, no se saca conclusion.
- **Automatizable**: si la accion se repite (template, follow-up, secuencia), el agente dice como la ejecutaria el bot/CRM en vez de dejarla como tarea manual.
- Si lo que hace falta medir no existe en el CRM, el agente lo propone como cambio (va por la secuencia normal Analisis→… en `docs/crm-olvidata/`), no lo da por existente. Ojo: el 2026-08-14 Joaquin descarto motivo estructurado de perdida y recordatorios automaticos — no volver a proponerlos sin evidencia nueva.

## Checklist de salida (todo output comercial)

1. ¿Tiene ICP explicito (industria + tamaño + decisor)?
2. ¿Hay una prueba de autoridad del mismo nicho, con respaldo en `docs/`?
3. ¿Es breve, en primera persona, con una sola pregunta/CTA y sin pedir fecha?
4. ¿Dice donde se registra, con que etiqueta y que metrica lo evalua?

Si alguna respuesta es no, el output no esta listo.
