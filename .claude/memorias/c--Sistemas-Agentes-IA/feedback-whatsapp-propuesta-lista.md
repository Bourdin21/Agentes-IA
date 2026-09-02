---
name: feedback-whatsapp-propuesta-lista
description: "Estilo preferido de mensaje WhatsApp cuando la propuesta ya esta armada: anunciarla de frente (firma personal + 'te dejamos lista la propuesta'), no esconderla detras de la demo"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
  modified: 2026-08-27T13:51:57.363Z
---

Cuando ya existe una propuesta/presupuesto armado para un lead, el mensaje de WhatsApp de respuesta debe **anunciarlo directamente**, no diferir todo a "coordinemos la demo primero". Confirmado 2026-08-21 comparando dos mensajes reales: el de estudio-contable-maribel-garcia (enviado el dia anterior, **preferido explicitamente por el usuario**) vs. el redactado por el agente `olvidata-sales` para cma-centro-medico el mismo dia (**menos preferido**).

**Patron del mensaje preferido (aplicar de ahora en mas):**
1. Firma personal al arranque: "Hola! Soy Joaquín de Olvidata Soft." — no un generico "Hola!" sin identificar quien escribe.
2. Anunciar el entregable de frente: "Te dejamos lista la propuesta para X" — no ocultar que ya existe una propuesta esperando a que el lead pida ver la demo primero.
3. Describir las opciones/alcance en lenguaje llano y funcional (bullets cuando hay 2 caminos claros), sin necesariamente citar montos en USD dentro del mensaje de WhatsApp — la propuesta con precios va en el documento adjunto/enlazado, el mensaje solo la presenta.
4. Reutilizar un dato concreto que el lead ya dio en el discovery para dar tranquilidad personalizada (ej. "pensando en que la van a usar 1 o 2 personas, las dos opciones les cierran en tamaño") — no una reafirmacion generica.
5. Cierre: invitar preguntas Y ofrecer la demo como alternativa para quien prefiera verlo funcionando antes de decidir — la demo es una opcion, no el unico paso siguiente obligatorio.

**Por que el mensaje de CMA gusto menos:** no se identificaba con nombre, no mencionaba que la propuesta ya estaba lista (dejaba todo colgado de "coordinemos la demo"), y no usaba el dato que el lead ya habia dado (5 personas) para dar tranquilidad concreta — quedo mas generico/reflexivo que resolutivo.

**Matiz a mantener:** esto no cambia la logica de CUANDO mostrar precio (eso sigue dependiendo de si el lead pidio costos explicitamente, o si el discovery es tan debil que conviene la version funcional-sin-precio primero — ver [[project-agentes-ia]] y el criterio ya usado en audifonos-bariloche). Lo que cambia es el TONO del mensaje: aunque no se cite el numero final en el chat, hay que anunciar que la propuesta esta lista con confianza, no esconder su existencia detras de "primero charlemos en la demo".

**Como aplicar:** instruir al agente `olvidata-sales` con este patron explicito cada vez que se le pida redactar un mensaje de WhatsApp para un lead que ya tiene propuesta armada — pasarle el mensaje de estudio-contable-maribel-garcia como ejemplo de referencia si hace falta.

**Persona gramatical (agregado 2026-08-27):** todo el mensaje va en **primera persona singular** ("te dejo lista la propuesta", "armé dos versiones", "no vendo un programa cerrado"), nunca en plural ("te dejamos", "armamos", "no vendemos") — Joaquin firma y escribe solo, es un desarrollador solista (delega puntualmente a Matias, pero no se presenta como "equipo" en la comunicacion directa con el lead). Revisar cualquier mensaje ya redactado (incluidos los de `olvidata-sales`) y pasar todo verbo/pronombre en plural a singular antes de enviarlo — este es un error que se colo varias veces (ej. "te dejamos lista la propuesta" en el propio ejemplo preferido de arriba, que en rigor deberia decir "te dejo lista la propuesta").
