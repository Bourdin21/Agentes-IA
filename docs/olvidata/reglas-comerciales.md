# Reglas comerciales (COM)

Catálogo de las reglas de negocio vigentes de Olvidata, con un **ID estable** por regla para poder
citarlas desde cualquier agente, pieza o propuesta: `COM-007` en vez de "la regla de que no se
afirma nada sin respaldo, está en algún lado del CM".

**Este archivo es el índice, no el cuerpo.** Cada regla vive con su contexto completo —el porqué, los
ejemplos, lo que se descartó— en el archivo que la decidió. Acá está el enunciado en una línea y el
puntero. Copiar el cuerpo acá garantizaría que las dos copias se separen: es exactamente lo que pasó
con § 0c de MARCA.md y la promesa del CEO (ver `decisiones.md`, DEC-000).

**`scripts/doctor.py` verifica que todo `COM-NNN` citado en el repo exista en esta tabla.** Si se cita
una regla que no está, es un error: o falta cargarla, o el ID está mal escrito.

Los IDs no se renumeran ni se reciclan. Una regla que se da de baja queda con estado `superada` y la
referencia a la que la reemplazó.

## Vigentes

| ID | Regla | Desde | Detalle en |
|---|---|---|---|
| COM-001 | El contenido de autoridad **no vende** — explicar cómo funciona algo no genera demanda; la demanda la genera mostrar el resultado operando | 2026-10-01 | `.claude/agents/olvidata-ceo.md`, `olvidata-cm.md` |
| COM-002 | El encuadre **no arranca por el dolor**: el cliente compra la experiencia de cómo va a ser su día, no la descripción de su problema | 2026-10-11 | `.claude/agents/olvidata-ceo.md` |
| COM-003 | El producto se posiciona por el **concepto rector**, no se describe por funcionalidad | 2026-10-11 | `.claude/agents/olvidata-ceo.md` |
| COM-004 | Se muestra el **producto terminado operando**; el método no se publica. Alcance acotado al frente de **Agentes IA** | 2026-10-13, acotada 2026-10-14 | `.claude/agents/olvidata-ceo.md`, `olvidata-cm.md` |
| COM-005 | La promesa que se vende: **que trabajen más las máquinas**, entendiendo la lógica del usuario — jubilar a la gente de su **trabajo cotidiano** | 2026-10-11 | `.claude/agents/olvidata-ceo.md` |
| COM-006 | Nunca **«la IA hace tu trabajo»** (la frase que pone al sistema en lugar de la persona). Siempre: *vos definís cómo se hace, el sistema lo hace todos los días*. Convive con COM-005: lo que se jubila es el trabajo repetido, no la persona | MARCA § 0c, redacción vigente 2026-10-15 | `docs/olvidata/marca/MARCA.md` § 0c |
| COM-007 | **Nada se afirma sin respaldo documental**: todo claim de funcionalidad es trazable a una línea de `docs/<proyecto>/`. Si no se puede respaldar, se saca — no se suaviza con hedge | 2026-09-02 | `docs/olvidata/casos.md` |
| COM-008 | **Nunca asumir integraciones de hardware** (balanza, ticketeadora, lector de código, impresora fiscal) salvo documentación explícita | 2026-09-02 | `docs/olvidata/casos.md` |
| COM-009 | **Metodología PACS** obligatoria en toda estrategia comercial: nicho → autoridad → mensaje conversacional → sistematización. El objetivo son reuniones agendadas, no volumen de mensajes | 2026-09-19 | `.github/instructions/36-metodologia-pacs.instructions.md` |
| COM-010 | **Marca personal por delante**: "Joaquín, con el respaldo de Olvidata", no "Olvidata Soft" primero. Aplica a clientes de catálogo, no solo a LinkedIn | 2026-09-02 | `.claude/agents/olvidata-ceo.md` |
| COM-011 | **Cierre pasivo**: nunca se presiona. Propuesta con vencimiento de 7 días, 2 follow-ups (día 3 y día 6), 50% de anticipo no negociable | — | `.claude/agents/olvidata-ceo.md`, `olvidata-sales.md` |
| COM-012 | **Todos los precios son sin IVA** y se cotizan y publican "+ IVA" | 2026-09-19 | `docs/olvidata/precios.md` |
| COM-013 | **Los usuarios nunca modifican el precio del plan.** Más allá de 10 se acuerda puntualmente, sin cifra publicada | 2026-08-27 | `docs/olvidata/precios.md` |
| COM-014 | **El año 1 de mantenimiento es siempre gratis** y no se trackea su costo | 2026-08-27 | `docs/olvidata/precios.md` |
| COM-015 | **Tokens IA: 25%**, distribuido dentro del precio de cada módulo (×1,25). No aparece como línea separada al cliente | 2026-08-20 | `.github/instructions/27-presupuesto-parametros.instructions.md` |
| COM-016 | **Promo de entrada de AI Agents y Chatbots hasta el 2026-12-31**, se menciona una sola vez en la propuesta, sin lenguaje de escasez fabricado. El que entra con la promo queda **grandfathereado** mientras siga activo | 2026-09-14 / 2026-09-17 | `docs/olvidata/precios.md` |
| COM-017 | **Second Brain corporativo se comercializa desde noviembre 2026**, y se vende **por la tarea, no por la idea** | 2026-10-13 | `docs/olvidata/marca/plan-comercializacion-second-brain.md` |
| COM-018 | **El mapa está pausado** — se guarda como as bajo la manga, no se publica | 2026-10-13 | `.claude/agents/olvidata-ceo.md` |
| COM-019 | **Descuento por volumen** (tiers V0–V3 sobre el subtotal de lista): combina con el de reutilización por **MAX, no por suma** | 2026-08-19 | `.github/instructions/27-presupuesto-parametros.instructions.md` |
| COM-020 | Antes de aplicar un descuento agresivo por defecto, **chequear la capacidad de pago** del cliente (precedente: FABINCO vs. Peras del Olmo, mismo ratio, trato opuesto) | 2026-09-02 | `.claude/agents/olvidata-ceo.md` |
| COM-022 | **Cada consulta se atiende en el idioma en que llega** — WhatsApp, DM, email y el bot de ventas. No se fuerza el castellano ni se cambia de idioma sin que el cliente lo pida | 2026-10-31 | `docs/olvidata/marca/posicionamiento-nl.md` § 6 |
| COM-021 | **Chatbot o asistente dentro de un Build del estudio: un solo recurrente, no dos.** El plan sale de la tabla de mantenimiento por cantidad de tablas, contando las que agrega el asistente. El setup sí se cobra separado | 2026-10-17 | `docs/olvidata/precios.md` |

## Cómo citar

En cualquier archivo del repo: `(COM-007)` o `ver COM-007`. En una pieza o mensaje al cliente **no se
citan los IDs** — son para los agentes y para el control de consistencia, no para el lector final.

**El ID lleva tres dígitos** (`COM-007`, no `COM-7` ni `COM-07`), y eso no es cosmético: los
proyectos de cliente usan su propio espacio de nombres con dos dígitos y prefijo de módulo —
`R-COM-01` a `R-COM-10` son las reglas de **Compras** de ShowroomGriffin, que no tienen nada que ver
con una regla comercial de Olvidata. El chequeo de `doctor.py` distingue las dos cosas por el
formato, así que un ID escrito con dos dígitos no se verifica.

## Superadas

Ninguna todavía. Cuando una regla se reemplace, va acá con `superada-por: COM-NNN` y la fecha, sin
borrar el enunciado original — mismo criterio que la memoria por entradas con id
(`29-trazabilidad-conversacion`).
