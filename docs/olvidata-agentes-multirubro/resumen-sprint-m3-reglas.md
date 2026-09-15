# Olvidata**Soft**

---

**Olvidata Agentes Multi-rubro — Reglas de los agentes**

**OlvidataSoft · Septiembre 2026**

## Sobre el proyecto

En esta entrega cada empresa le puede contar a los agentes cómo trabaja, sin escribir prompts cada vez. Las reglas se cargan una vez y los agentes las tienen en cuenta solas en cada pedido.

- El Director define lo que vale para toda la empresa y para cada área.
- Cualquier miembro carga lo que pide cada cliente y sus propias preferencias.
- Antes de enviar un pedido, cada persona ve qué va a tener en cuenta el agente.
- Cada tarea queda registrada con las reglas exactas que usó.

## Cambios entregados

- **Reglas en lenguaje simple.** Pestañas "De la empresa", "De mi área", "Por agente", "De clientes" y "Mis preferencias". Cada regla se aplica **"Siempre"** o **"Salvo que se indique otra cosa"**, y puede ser una indicación o un procedimiento paso a paso.
- **Historial.** Cada cambio queda guardado con quién lo hizo y cuándo; las reglas se desactivan sin borrarse.
- **Nuevo pedido con cliente.** Elegís el cliente y ves "Esto es lo que el agente va a tener en cuenta", ordenado por prioridad y actualizado al cambiar de cliente.
- **Registro en cada tarea.** "Lo que el agente tuvo en cuenta" muestra las reglas y versiones usadas, y avisa si alguna cambió después.
- **Cuidado del costo.** Límites de tamaño por regla, por empresa, por área, por cliente y por persona.
- **Control de Olvidata.** Veo en solo lectura las reglas de cada organización. Las reglas propias de Olvidata se publican con evaluación previa.
- **Accesos directos.** La ficha de cada cliente y cada área muestran sus reglas; el listado de tareas se filtra por cliente.

## Beneficio

- Se deja de repetir el contexto en cada pedido: la empresa trabaja con criterios comunes y cada persona conserva sus preferencias.
- Lo obligatorio lo decide el Director y nadie lo pisa.
- Si un resultado sale raro, se puede ver exactamente qué instrucciones tenía el agente.
- Probé los permisos, los límites, el historial y la separación entre organizaciones en un navegador real, sin encontrar errores.

## Pendientes o fuera de alcance

- Las 3 reglas propias de Olvidata están cargadas en borrador: hay que revisarlas y publicarlas para que se apliquen.
- Falta una prueba con el modelo real para confirmar que respeta las reglas en la práctica (tiene costo y requiere tu OK).
- Todavía no se puede seguir conversando sobre el resultado de una tarea: es la próxima etapa.

## Próximo paso sugerido

Construir **M3b — Seguir conversando sobre una tarea**, para que el equipo pueda pedir ajustes al resultado sin volver a Claude web.

**Olvidata Soft — olvidatasoft@gmail.com — https://olvidata.com.ar/**
