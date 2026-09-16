# Olvidata**Soft**

---

**Olvidata Agentes Multi-rubro — Trabajo en equipo: agentes y personas**

**OlvidataSoft · Septiembre 2026**

## Sobre el proyecto

En esta entrega el trabajo deja de ser una sola persona pidiéndole algo a un agente: los agentes pueden apoyarse en otros agentes, y el Director puede repartir trabajo entre su equipo y los agentes, conversando.

- Un agente coordinador le pide partes del trabajo a agentes especializados y junta las respuestas.
- Cualquier agente puede sugerirte una regla nueva, que se guarda solo si la confirmás.
- El Director asigna tareas a personas, con vencimiento y seguimiento.
- Quien recibe una asignación la resuelve a mano o se la pide a un agente con un botón.

## Cambios entregados

- **Agentes que delegan**: la tarea principal muestra a quién le pidió cada parte y espera las respuestas; si una parte falla o se cancela, el coordinador lo sabe y sigue.
- **Costo a la vista**: cada tarea muestra su costo y el total con sus partes.
- **Sugerencias de reglas**: los agentes proponen preferencias tuyas o reglas de un cliente; se aplican con un botón y quedan marcadas con su origen.
- **Asignaciones a personas**: estados, vencimiento, avisos al asignar, reasignar, cancelar o terminar, y bandejas "Asignadas a mí" y "Del equipo".
- **Puente con los agentes**: "Pedírsela a un agente" abre el pedido ya cargado y deja la asignación en curso.
- **Asistente del Director**: propone cómo repartir el trabajo de la semana entre personas y agentes; nada se crea sin confirmar.

## Beneficio

- El trabajo repetitivo se reparte solo entre agentes especializados, sin que nadie arme cada pedido a mano.
- El Director ve en un lugar qué está en manos de personas y qué en manos de agentes.
- Lo probé en un navegador real: delegaciones que fallan, cancelaciones en cascada, permisos forzados y asignaciones vencidas. Los cuatro problemas que aparecieron quedaron corregidos, incluido uno importante: el staff de Olvidata podía cancelar tareas de un cliente.

## Pendientes o fuera de alcance

- El prompt del asistente está en borrador: hay que revisarlo y publicarlo para habilitarlo.
- Falta la prueba con el modelo real para medir la calidad de las delegaciones y del reparto.
- Las partes de una delegación corren de a una por empresa, así que una tarea con varias partes tarda más.

## Próximo paso sugerido

**M8 — Evaluación automática de prompts**, para publicar cambios de prompts con pruebas que corran solas.

**Olvidata Soft — olvidatasoft@gmail.com — https://olvidata.com.ar/**
