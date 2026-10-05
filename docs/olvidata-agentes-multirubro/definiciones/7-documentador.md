# Memoria - Documentador

## Proyecto: olvidata-agentes-multirubro
## Ultima actualizacion: 2026-10-03 (M29) | 2026-10-02 (M28) | 2026-09-14

## Definiciones vigentes

### M4b Configurador de reglas (2026-09-14)
Documento entregado: `docs/olvidata-agentes-multirubro/resumen-sprint-m4b-configurador.md` (formato 31, lector Joaquín).
- **Alcance entregado:** configurar conversando (chips, tarjetas de propuesta Aplicar / Editar y aplicar / Descartar / Aplicar todas / Reintentar, aviso de regla cambiada), confirmación solo por botón, lista compartida entre Directores, origen en historial, costo en Tareas, lectura acotada. QA: apto con observaciones, 15/15 CA, sin defectos funcionales; OLV-004 de contraste global reportado sin fix.
- **Pendientes:** prompt del configurador en borrador (evaluar y publicar), corrida real con costo, configurador para Empleados, contraste global de botones (PA-11), "Ver pasos" técnico (PA-12).
- **Próximo paso:** publicar prompt + corrida real antes de M5.

### M4 Agentes de la organización (2026-09-14)
Documento entregado: `docs/olvidata-agentes-multirubro/resumen-sprint-m4-agentes.md` (formato 31, lector Joaquín).
- **Alcance entregado:** catálogo por secciones, crear/editar/duplicar agentes derivados, versiones, publicar para la empresa sin revisión con aviso a Directores, archivar/reactivar (con sección Archivados), reglas para agentes de la empresa, sugerencias activables, rubro incluido siempre + sincronización, vista de staff. QA: apto con observaciones, 14/14 CA aplicables (CA-M4-03 pospuesto), 1 defecto menor de contraste corregido.
- **Pendientes:** revisión del Director (pospuesta), contenido de rubro "negocio" y sugerencias reales, confirmar sección "Archivados", aviso a la autora cuando el Director edita su agente, contrastes heredados del theme, pendientes abiertos PA-01..07.
- **Próximo paso:** M4b Agente configurador de reglas del Director.

### M3b Seguir conversando (2026-09-14)
Documento entregado: `docs/olvidata-agentes-multirubro/resumen-sprint-m3b-conversacion.md` (formato 31, lector Joaquín).
- **Alcance entregado:** ajustes sobre tareas terminadas (incluidas fallidas y canceladas) con el mismo agente/cliente/reglas, conversación en orden con pasos plegados, respuesta en vivo, copiar, aviso de reglas cambiadas con atajo a tarea nueva, preferencias ajenas ocultas al Director, listado con mensajes y última actividad, límites. QA: apto con observaciones, 14/14 CA, 1 defecto menor corregido (tema oscuro).
- **Pendientes:** corrida real con costo (calidad, caché, error de conversación larga); recuperación tras reinicio hasta 5 min (lease del motor M1); adjuntos (M5); publicar reglas de plataforma (pendiente de M3).
- **Beneficios comunicados:** iterar como en Claude web con contexto de la empresa y registro; costo claro por autor.
- **Próximo paso:** M4 Agentes de la organización + reglas sugeridas por rubro.

### M3 Reglas (2026-09-14)
Documento entregado: `docs/olvidata-agentes-multirubro/resumen-sprint-m3-reglas.md` (formato 31, lector Joaquín).
- **Alcance entregado:** reglas en lenguaje llano por empresa, área, agente, cliente y preferencias; "Siempre / Salvo que se indique otra cosa"; procedimientos; historial y desactivación; nuevo pedido con cliente y vista previa; registro de reglas usadas por tarea con aviso de cambios; límites; vista de staff; reglas de Olvidata con evaluación; accesos desde cliente y área; filtro por cliente en tareas. QA: apto con observaciones, 15/15 CA, sin defectos.
- **Pendientes:** publicar las 3 reglas de plataforma (en borrador); corrida real con costo para validar obediencia/inyección/caché; seguir conversando (M3b); OBS-M3-1 (Director ve preferencias de quien pidió la tarea en el detalle) a decidir.
- **Beneficios comunicados:** sin repetir contexto, lo obligatorio lo decide el Director, auditoría de instrucciones por tarea.
- **Próximo paso:** M3b Seguir conversando sobre una tarea.

### M2 Organización (2026-09-14)
Documento entregado: `docs/olvidata-agentes-multirubro/resumen-sprint-m2-organizacion.md` (formato 31). Lector: Joaquín (dueño del producto; proyecto personal).

### Alcance entregado al cliente
M2 Organización del portal, validado por QA (apto con observaciones, todos los CA OK): roles Director/Empleado con refresco inmediato de permisos; ABM de Áreas; gestión de miembros (rol, área, bloqueo) con organización siempre con un Director activo; cartera de clientes con CUIT/DNI validado, búsqueda y filtros persistentes, baja solo Director; tareas visibles según rol; backoffice "Organizaciones y licencias" con alta de miembros; formularios unificados, Select2 y tema oscuro corregido.

### Pendientes o fuera de alcance
- Sin UI de staff para editar nombre/email/rol/estado de un miembro existente.
- `Tenant.Estado` no se evalúa en la sesión (organización suspendida sigue entrando).
- Pantallas legadas (Usuarios, listado y alta de organizaciones, Perfil) sin el sistema de formularios nuevo.
- Observaciones QA menores: filtros de texto solo con `keyup` (pegar con mouse no refresca), bajo contraste de `ov-alert info` en tema oscuro, URLs absolutas en layout.

### Beneficios comunicados
Autonomía de cada organización, aislamiento verificado entre organizaciones, base para reglas por nivel (M3) y agentes propios (M4).

### Proximo paso sugerido
M3 Reglas.

## M29 — Buscar en internet, y el archivo que se guarda o se descarta (documentación de alcance, 2026-10-02)

### Qué se entregó, en dos líneas

Ahora el chat libre puede **buscar en internet** cuando el pedido necesita algo que el agente no tiene. Y a cualquier conversación le podés **subir un archivo** sin tener que elegir un cliente primero, decidiendo ahí mismo si querés **guardarlo en la carpeta de un cliente** o **usarlo y que se descarte**.

### Buscar en internet

Es la misma casilla que ya conocías de las tareas: **«Buscar en internet si hace falta»**, apagada por defecto, al lado de *Adjuntar*. Está al abrir el chat y en cada mensaje que le mandes después.

- **Cada búsqueda tiene un costo aparte** y lo vas a ver sumado en el costo de la conversación, como todo lo demás.
- **La hace el proveedor del modelo, no el sistema.** Eso significa que el portal no sale a internet por su cuenta.
- Si tu organización no tiene la búsqueda habilitada, **la casilla no aparece**: no está puesta y gris, no está.
- Está **solo en el chat libre**. Las otras tres conversaciones sirven para configurar el sistema y no necesitan salir a la red.

### Subir un archivo a una conversación

Antes, para subir un archivo nuevo había que elegir un cliente primero, y en las conversaciones que no son de ningún cliente eso no se podía: el botón estaba y terminaba en un error. **Eso quedó resuelto.**

Cuando subís un archivo a una conversación, elegís qué querés que pase con él:

- **«Usar solo en esta conversación»** (viene marcada). El agente lo lee ahora y **el archivo no queda en la carpeta de nadie**. Se descarta cuando la conversación termine.
- **«Guardar en la carpeta de un cliente»**. Elegís el cliente y queda como un documento normal de ese cliente, con todo lo que eso trae.

**Podés cambiar de idea.** Mientras la conversación viva, cada archivo muestra en su etiqueta qué va a pasar con él —*«solo en esta conversación»* o el nombre del cliente— y el que todavía es transitorio te ofrece **«Guardar en un cliente»** sin tener que subirlo de nuevo. Eso es a propósito: cuando subís el archivo todavía no viste qué hace el agente con él, así que lo que viene marcado por defecto es lo que **se puede deshacer**.

Si al guardarlo resulta que ese cliente ya tiene ese mismo archivo, o llegó a su tope de documentos, **te lo decimos en el momento** y el archivo sigue siendo transitorio: nunca queda a medio camino.

### Cuándo se borra un archivo transitorio

- Cuando vos lo **saqués** de la conversación.
- O **solo**, pasados unos días de que la conversación terminó (**siete**, configurable). Mientras el hilo esté vivo el archivo está, así que podés seguir preguntando sobre él sin apuro.

Un archivo **ya guardado en un cliente no se borra nunca** por esta vía: es un documento como cualquier otro.

### Lo que no cambia

- **El agente lee solo lo que le adjuntaste a esa conversación.** No entra en la carpeta de ningún cliente ni en los adjuntos de otra conversación, y un archivo transitorio **pertenece a la conversación donde nació**: desde otra no se puede usar.
- Los archivos transitorios **ocupan tu espacio** mientras existen —ocupan disco de verdad— y lo liberan al descartarse. Es lo honesto, y evita que este camino sirva para esquivar el tope.
- **Un archivo transitorio no aparece en ningún listado de documentos**, ni de un cliente ni de la organización.
- **Ningún usuario del portal del cliente ve un archivo sin cliente**, por ningún camino.
- Los topes de gasto que ya tenías siguen igual: **ningún valor se cambió**.

### Lo que falta para poder usar el chat libre

**Publicar su agente**, que sigue en borrador. Y para publicarlo hace falta que su evaluación quede aprobada, que es la regla de siempre: ningún agente de Olvidata sale sin pasar sus pruebas.

Hoy eso está frenado por una sola cosa, y no es del sistema: **la cuenta de Anthropic se quedó sin saldo**. Mientras no haya crédito, **ninguna tarea de agente funciona** —ni el chat libre ni los que ya andaban—, así que cargar saldo es lo primero.

Las dos funcionalidades de M29 **ya están en producción**: la casilla de internet queda a la vista en cuanto el chat libre se publique, y la subida de archivos **ya funciona hoy** en las conversaciones que están publicadas.

## M28 — El chat libre (documentación de alcance, 2026-10-02)

### Qué se entregó, en una línea

Una pantalla nueva donde escribís lo que necesités sin elegir nada antes, y donde escribiendo `@` le pedís el trabajo a un agente o dejás armada una regla, un instructivo, una tarea programada o un agente propio.

### Para qué sirve

Hasta ahora el sistema tenía cinco puertas y **todas pedían que ya supieras qué querías**: elegir un agente del catálogo, elegir un cliente, o entrar a una de las tres conversaciones de configuración, cada una con su tema fijo. No había ningún lugar donde escribir *una pregunta cualquiera*, que es el gesto con el que la gente ya sabe tratar a una IA.

El chat libre es esa puerta. Entrás, escribís, y desde ahí llegás a todo lo demás mencionando.

### Lo que podés hacer

- **Preguntar cualquier cosa.** Sin elegir agente, sin elegir cliente, sin elegir rubro. La conversación sigue siendo tuya: se guarda, se reanuda al otro día, y el costo está siempre a la vista.
- **Pedirle el trabajo a un agente.** Escribís `@` y te aparecen **los agentes que vos podés usar** — ni uno más. Elegís uno, le contás qué necesitás, y el chat le abre la tarea. Mientras trabaja, el hilo te muestra en qué anda; cuando termina, el resultado entra a la conversación **rotulado como suyo**, para que sepas que lo dijo ese agente y no el chat.
- **Dejar armada una automatización.** El mismo `@` te ofrece, abajo, las cuatro cosas que se cargan: **una regla, un instructivo, una tarea programada o un agente propio**. El chat te deja la propuesta en una tarjeta con todo escrito, y **vos decidís**.
- **Adjuntar un documento** a la conversación y pedirle que lo lea.

### Lo que el chat libre NO hace, a propósito

- **No cambia nada por su cuenta.** Todo lo que propone queda en una tarjeta, y **nada pasa hasta que alguien toca el botón**. Si lo que propone es de la empresa y vos no la dirigís, lo vas a ver pero no lo vas a poder aplicar: ahí hace falta el Director.
- **No entra en la carpeta de ningún cliente.** Lee **solo** lo que le adjuntaste a esa conversación. El chat libre es sin cliente por definición.
- **No le pasa tu pedido a un agente que no podés usar.** Si mencionás algo que no está entre tus agentes, te lo dice y lo deja como texto.
- **No reemplaza nada.** Las puertas que ya conocías siguen todas donde estaban.

### Cómo se comporta la pantalla

Cuando la abrís está vacía, y ahí es donde vive la animación: es una pantalla de arranque, no un cartel. En cuanto mandás el primer mensaje **la animación se va** y la pantalla queda hecha para leer y escribir, que es para lo que la abriste. Si tu equipo o tu navegador están configurados para reducir el movimiento, **no se descarga ni se muestra nada de eso** y la pantalla funciona igual, completa.

### Condiciones

- La usa **cualquier persona de la organización**, no solo quien dirige.
- **Solo quien abrió un chat lo continúa.** Quien dirige la organización puede leerlo.
- Los topes de gasto que ya tenías **siguen valiendo igual**: ningún valor se cambió. Si el mes llegó al tope, el chat libre no arranca y te dice por qué.
- Cada chat y cada tarea que se abre desde él **muestran lo que costaron**.

### Lo que falta para poder usarlo

1. **Publicar el agente del chat libre.** Como todos los agentes de Olvidata, nace en borrador y **no se publica sin su evaluación aprobada**. Hasta que eso pase, la opción **no aparece en el menú**: no es que esté y falle, es que no está.
2. **Un punto pendiente de decisión** (ver abajo): hoy no hay forma de **subir** un archivo nuevo desde una conversación sin cliente. Los que ya están cargados se leen bien.

### El punto pendiente, dicho sin vueltas

**Subir un archivo nuevo a una conversación que no tiene cliente no funciona** — y no es algo que M28 haya roto: ya pasaba en *Automatizar lo que repetís*, donde también se pueden adjuntar documentos sin cliente. El motivo de fondo es que, en el sistema, **un documento siempre pertenece a un cliente**: no existe hoy la idea de «un documento de la empresa». Leer un documento ya cargado funciona bien; lo que falta es el camino para subirlo.

Resolverlo es una decisión de producto, no un arreglo: hay que definir **dónde se ve un documento de la empresa**, si dos pueden llamarse igual, y contra qué cuota cuentan. Está documentado y queda a decisión de Joaquín.

## Historial de ajustes
- 2026-09-14: Resumen de entrega de M2 Organización redactado en formato 31, en primera persona, sin tecnicismos, con pendientes declarados por implementador y QA.
- 2026-09-14: Resumen de entrega de M3 Reglas (formato 31, lenguaje llano alineado a D-M3-8..12), con pendientes de publicación de reglas de plataforma, corrida real y M3b.
- 2026-09-14: Resumen de entrega de M3b Seguir conversando (formato 31), próximo paso M4.
- 2026-09-14: Resumen de entrega de M4 Agentes de la organización (formato 31), próximo paso M4b.
- 2026-09-14: Resumen de entrega de M4b Configurador de reglas (formato 31), próximo paso: publicar prompt y corrida real antes de M5.
