<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/1-analista-funcional.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 1-analista-funcional - M06 (6 bloques archivados)

- Reglas funcionales M6
- Criterios de aceptacion M6
- Riesgos M6
- Preguntas abiertas M6 (hipótesis tomadas sin gate, autorización 2026-09-14)
- Reutilizacion relevada M6
- Clasificacion de perfil de cliente M6

---

### Reglas funcionales M6
- **RF-M6-01** Límite de la organización: USD con hasta 2 decimales, entre 1 y 100.000 (configurable). Vacío = "sin límite", solo lo puede dejar un SuperUsuario. Las organizaciones nuevas y las existentes al migrar reciben el valor por defecto de configuración (USD 100, P2).
- **RF-M6-02** Límite de un miembro: opcional, mayor que 0 y no mayor que el límite vigente de la organización. Sin límite propio, al miembro solo lo frena el de la organización. Si después el staff baja el de la organización por debajo, el **límite efectivo** del miembro es el menor de los dos y la pantalla lo indica (P3).
- **RF-M6-03** Período: mes calendario argentino (desde las 00:00 del día 1, hora de Argentina). El cambio de mes libera el bloqueo sin intervención.
- **RF-M6-04** Consumo del mes = suma del costo guardado de cada llamada al modelo hecha dentro del mes, en tareas de la organización (consumo de la organización) o en tareas cuyo autor es el miembro (consumo del miembro). Incluye conversaciones de configuración (M4b). Cambiar la tabla de precios no altera meses pasados. Detalle: por área = área **actual** del miembro (P6); por agente = agente de la organización o agente base de la tarea; por cliente = cliente de cartera de la tarea ("Sin cliente").
- **RF-M6-05** Con API key propia (`ModoApiKey = PropiaDelCliente`) no hay límites, avisos ni bloqueos; la pantalla muestra tokens y "Tu empresa usa su propia clave de Anthropic: el gasto en dólares lo ves en tu cuenta de Anthropic."; los campos de límite no se muestran (P4).
- **RF-M6-06** Avisos (umbral de aviso configurable, 80 %): se envían una sola vez por mes, umbral y destinatario. Organización al 80 % y 100 % → Directores activos. Miembro al 80 % y 100 % → el miembro; al 100 % también los Directores activos. Si el límite sube y se vuelve a cruzar el mismo umbral en el mismo mes, no se repite (P7).
- **RF-M6-07** Bloqueo antes de gastar: crear una tarea, iniciar una configuración de reglas y enviar un ajuste se rechazan si el consumo del mes ya alcanzó el límite efectivo (organización o miembro), con un mensaje que dice qué límite, cuándo se renueva y quién puede ampliarlo.
- **RF-M6-08** Bloqueo en curso: antes de **cada** llamada al modelo se verifica el límite. Si está alcanzado no se llama, el turno termina "Fallida" con el mensaje de límite en la conversación y se asegura el aviso del 100 %. La llamada que ya estaba en curso termina y se registra: el consumo puede superar el límite como máximo en una llamada por tarea en ejecución (P5).
- **RF-M6-09** Retomar: el autor envía un ajuste ("seguí") cuando hay margen (mes nuevo o límite mayor); la conversación conserva todo lo hecho.
- **RF-M6-10** Un cambio de límite rige desde la verificación siguiente y queda registrado en la auditoría (quién, cuándo, valor anterior y nuevo).
- **RF-M6-11** Visibilidad: el Director ve todo el consumo y los límites de su organización; el Empleado solo su consumo y su límite (nunca los de otros, ni por URL); el staff ve todas las organizaciones y solo modifica el límite de la organización. Montos en pantalla "USD 12,34"; el staff ve 4 decimales en "Uso y consumo".
- **RF-M6-12** Una herramienta marcada como "requiere aprobación" nunca se ejecuta sin una aprobación registrada. La marca y el nivel ("quien pidió la tarea" / "solo un Director") los define la herramienta en código; ninguna regla, documento ni texto del pedido los cambia (§3.2 del diseño de organización).
- **RF-M6-13** Pedido: se registra (herramienta, datos pedidos, descripción en palabras generada por la herramienta, nivel, fecha y vencimiento) **antes** de soltar la tarea, que queda "Espera aprobación" sin ocupar el motor. Si el modelo pidió varias herramientas en un mismo paso, las que no requieren aprobación y están antes se ejecutan; al llegar a la primera que la requiere se crean los pedidos de **todas** las del paso que la requieren y el resto espera (P9).
- **RF-M6-14** Quién resuelve: nivel "quien pidió la tarea" → el autor (miembro activo) o cualquier Director activo; nivel "solo un Director" → cualquier Director activo, aunque sea el autor. El staff no resuelve. Un Empleado no ve pedidos de tareas ajenas (visibilidad M2).
- **RF-M6-15** Aprobar: cuando no quedan pedidos pendientes del paso, la tarea vuelve a la cola; al retomarla la acción aprobada se ejecuta con los permisos del autor verificados en ese momento y su resultado vuelve al agente y se ve en "Ver pasos".
- **RF-M6-16** Rechazar: motivo opcional de hasta 500 caracteres; el agente recibe "La persona rechazó esta acción[. Motivo: …]. No la vuelvas a intentar salvo que te lo pidan." y la conversación sigue.
- **RF-M6-17** Vencimiento (72 h, configurable): al vencer, el agente recibe "Nadie aprobó esta acción a tiempo; no se ejecutó." y la tarea sigue. Aprobar o rechazar un pedido vencido muestra un mensaje y no ejecuta nada.
- **RF-M6-18** Dos personas resuelven el mismo pedido a la vez: vale la primera; la segunda ve "Este pedido ya lo resolvió «Nombre»".
- **RF-M6-19** Cancelar una tarea en espera deja sus pedidos pendientes como "Cancelado" (nunca se ejecutan). Mientras una tarea espera aprobación no se pueden enviar ajustes: "La tarea espera una aprobación. Resolvela para seguir conversando."
- **RF-M6-20** Aprobar no consume tokens: una acción aprobada se ejecuta aunque el límite esté alcanzado y el turno se frena antes de la llamada siguiente al modelo (P12).
- **RF-M6-21** Si al ejecutar una acción aprobada el autor ya no es miembro activo, no se ejecuta y el agente recibe "La acción no se ejecutó: quien pidió la tarea ya no tiene acceso."
- **RF-M6-22** Los pedidos y su resolución son inmutables (quién, cuándo, motivo) y se ven en la tarea y en el historial de la bandeja.
- **RF-M6-23** Notificaciones del portal (con enlace a la tarea): pedido "quien pidió la tarea" → autor; pedido "solo un Director" → Directores activos (y el autor sabe en la tarjeta que espera a un Director); resuelto por otra persona → autor; vencido → autor.
- **RF-M6-24** Las herramientas de demostración solo existen en Development con modelo simulado; nunca se registran en otro entorno, no tienen efectos fuera del sistema y su nombre dice "(demostración)".
- **RF-M6-25** El servicio que verifica el límite y el de aprobaciones quedan reutilizables para las programaciones de M12 (sin implementarlas).
### Criterios de aceptacion M6
- **CA-M6-01** El staff abre la organización "Estudio Pérez" en el backoffice, ve "Gastado en septiembre: USD 12,40 de USD 100,00" y cambia el límite a USD 50; un Administrador no puede dejarla sin límite y un SuperUsuario sí.
- **CA-M6-02** El Director fija USD 20 a Laura; intentar USD 60 con la organización en USD 50 muestra "El límite no puede superar el de la empresa (USD 50,00)."; quitarlo deja "Usa el de la empresa".
- **CA-M6-03** En Consumo, el Director ve la barra de la organización y las tablas por miembro, área, agente y cliente del mes elegido, con totales que coinciden con la suma de costos de los pasos del mes (verificable en MySQL).
- **CA-M6-04** Un Empleado ve solo su consumo y su límite; pedir por URL el consumo de otro miembro o el de la organización devuelve 403 o no muestra datos ajenos.
- **CA-M6-05** Con el umbral cruzado (costos sembrados en dev), los Directores reciben una sola notificación "Gasto de la empresa al 80 %" aunque se ejecuten más pasos; al 100 % reciben otra.
- **CA-M6-06** Con el límite de la organización alcanzado, crear una tarea, iniciar una configuración y enviar un ajuste muestran el mensaje de límite y no crean nada.
- **CA-M6-07** Una tarea en curso cuyo límite se alcanza entre dos llamadas termina el turno como Fallida con "Se frenó porque la empresa llegó al límite de gasto del mes…" sin llamar al modelo; tras subir el límite, el autor envía "seguí" y la tarea continúa.
- **CA-M6-08** Con el límite de Laura alcanzado y la organización con margen, Laura queda bloqueada y Martín puede seguir pidiendo tareas.
- **CA-M6-09** Una organización con API key propia no tiene campo de límite, nunca se bloquea y su consumo muestra tokens con el aviso.
- **CA-M6-10** Con el modelo simulado, un pedido "Probá una aprobación" deja la tarea en "Espera aprobación" con la tarjeta "Enviar un mensaje de prueba a «Cliente de prueba»…"; en ese momento no hay ejecución registrada de la herramienta.
- **CA-M6-11** El autor Empleado aprueba desde la tarjeta: la tarea vuelve a trabajar, la acción se ejecuta una vez, "Ver pasos" muestra el resultado y la tarjeta queda "Aprobado por Laura Gómez el 15/09 14:40".
- **CA-M6-12** El autor rechaza con motivo "Todavía no": el agente responde que no lo hizo y la tarjeta muestra "Rechazado por … — Todavía no".
- **CA-M6-13** Un pedido "solo un Director": el Empleado autor ve "Espera la aprobación de un Director" sin botones y por POST recibe 403; los Directores reciben la notificación y uno lo aprueba desde la bandeja.
- **CA-M6-14** Dos Directores aprueban el mismo pedido a la vez: uno lo resuelve y el otro ve "Este pedido ya lo resolvió «…»"; la acción se ejecuta una sola vez.
- **CA-M6-15** Con el vencimiento configurado en minutos en dev, un pedido sin respuesta pasa a "Venció sin respuesta", el autor recibe la notificación y el agente continúa informando que no se hizo; aprobarlo después muestra "Este pedido venció…".
- **CA-M6-16** Cancelar una tarea en espera deja sus pedidos "Cancelado" y la bandeja ya no los muestra como pendientes; nunca se ejecutan.
- **CA-M6-17** Reanudación: si el proceso se corta después de ejecutar una acción aprobada y antes de registrar el paso, al retomar no se vuelve a ejecutar (se usa el resultado guardado); si se corta al pedir, el pedido existe o la tarea sigue En curso sin pedido y lo vuelve a crear una sola vez.
- **CA-M6-18** Dos herramientas con aprobación en un mismo paso generan dos tarjetas a la vez; la tarea sigue recién cuando las dos están resueltas.
- **CA-M6-19** La bandeja muestra el contador de pendientes que la persona puede resolver; un Empleado solo ve pedidos de sus tareas; el staff no tiene la bandeja pero ve las tarjetas en la tarea (solo lectura).
- **CA-M6-20** En Production (o Development sin simulado) las herramientas de demostración no están registradas ni se ofrecen.
- **CA-M6-21** Hash y conversación: el hash de las tareas de formatos 1, 2 y 3 no cambia; una tarea con aprobaciones reconstruye la conversación con resultados de herramienta normales.
- **CA-M6-22** Tema oscuro y mobile: barras de gasto, tarjetas de aprobación, bandeja y avisos con contraste ≥ 4,5 en lo nuevo, estados con ícono + texto (nunca solo color) y sin scroll horizontal a 390 px.
### Riesgos M6
- R-M6-01 (alto) **Acción con efecto ejecutada sin aprobación o dos veces** (reanudación, dos aprobadores, cancelación simultánea) → pedido y cambio de estado en un solo guardado antes de soltar la tarea; ejecución solo con aprobación leída; idempotencia por `tool_use_id`; token de concurrencia en pedido y tarea.
- R-M6-02 (alto) **Margen de Olvidata comido por consumo sin tope** → verificación antes de cada llamada, bloqueo en creación y ajustes, exceso acotado a una llamada por tarea en ejecución.
- R-M6-03 (medio) **Aprobación a ciegas** (la persona aprueba sin entender) → descripción en palabras generada por código de la herramienta, datos visibles sin JSON, nivel "solo un Director" para lo delicado.
- R-M6-04 (medio) **Inyección que empuja al agente a pedir acciones** (documento o regla maliciosos) → la aprobación humana es justamente el control; marca y nivel fijos en código.
- R-M6-05 (medio) **Tareas trabadas esperando para siempre** → vencimiento, contador en el menú, notificaciones.
- R-M6-06 (medio) **Bloqueo inesperado molesta al usuario** → avisos al 80 %, mensajes que dicen cuándo se renueva y quién amplía, barra visible antes de pedir.
- R-M6-07 (bajo) Consumo por área con el área actual no refleja cambios de área dentro del mes (P6, documentado).
- R-M6-08 (bajo) Precios desactualizados → configuración verificada antes de facturar (CLAUDE.md); cambios no alteran meses pasados.
### Preguntas abiertas M6 (hipótesis tomadas sin gate, autorización 2026-09-14)
- **P1 — ¿Qué se limita?** *A:* costo en USD a precio de lista de las llamadas al modelo (lo que paga Olvidata). *B:* precio al cliente con margen. *Tomada: A* (B depende de la unidad de cobro, PLAN §8.1).
- **P2 — Límite por defecto de la organización.** *Ejemplo:* un estudio contable con 5 miembros que hace 20 tareas diarias de ~USD 0,15 gasta ~USD 66 al mes. *A:* USD 100 por defecto (nuevas y existentes), el staff lo ajusta, "sin límite" solo SuperUsuario. *B:* sin límite hasta que el staff lo cargue. *Tomada: A* (lo seguro protege el margen desde el día 1).
- **P3 — Límite de miembro vs. de la organización.** *A:* el del miembro no puede superar al de la organización; si después baja el de la organización, rige el menor y se avisa. *B:* impedir bajar el de la organización mientras haya miembros por encima. *Tomada: A*.
- **P4 — API key propia.** *A:* sin límites ni avisos; consumo en tokens. *B:* estimar el costo y aplicar los límites del Director. *Tomada: A* (Olvidata no paga; hoy ninguna organización la usa).
- **P5 — Tarea en curso al llegar al límite.** *A:* termina la llamada en curso, el turno queda Fallida con mensaje y se retoma con un ajuste. *B:* estado nuevo "Pausada por límite" que se reanuda sola. *C:* cortar sin registrar la llamada. *Tomada: A* (sin estados nuevos; reusa M3b; C perdería costo real).
- **P6 — Consumo por área.** *A:* área actual del miembro. *B:* guardar el área en cada tarea. *Tomada: A*.
- **P7 — Canal de avisos.** *A:* notificación del portal al 80 % y 100 %, una vez por mes. *B:* además email. *Tomada: A*.
- **P8 — ¿Quién define que una acción requiere aprobación y de quién?** *A:* la herramienta en código (nivel "quien pidió la tarea" o "solo un Director"). *B:* el Director por herramienta. *Tomada: A* (B → M12 autonomía por rol).
- **P9 — Varias herramientas en un paso.** *A:* se ejecutan en orden hasta la primera con aprobación y se piden a la vez todas las del paso que la requieren. *B:* pedir de a una. *Tomada: A* (una sola espera).
- **P10 — Vencimiento.** *A:* 72 h; el agente sigue sabiendo que no se hizo. *B:* sin vencimiento. *C:* 24 h y la tarea falla. *Tomada: A*.
- **P11 — Motivo de rechazo.** *A:* opcional (hasta 500). *B:* obligatorio. *Tomada: A*.
- **P12 — Aprobar con el límite alcanzado.** *A:* se ejecuta (no gasta) y el turno se frena antes de la próxima llamada. *B:* no se permite aprobar. *Tomada: A*.
- **P13 — ¿Editar la acción antes de aprobar?** *Tomada: no* (se rechaza con motivo y el agente la vuelve a pedir corregida).
- **P14 — QA sin costo.** *A:* dos herramientas de demostración solo en Development con simulado y guion en el simulador. *B:* solo en tests. *Tomada: A*.
- **P15 — ¿Dónde se aprueba?** *A:* tarjeta en la tarea + bandeja "Aprobaciones" con contador. *B:* solo en la tarea. *Tomada: A* (el Director aprueba pedidos de muchas tareas).
- **P16 — ¿El Director aprueba pedidos "quien pidió la tarea" de Empleados?** *Tomada: sí* (§2 "Director cualquiera").
### Reutilizacion relevada M6
- **crm-olvidata** (`docs/crm-olvidata/definiciones/3-arquitecto-mvc.md` §6.1–6.2, repo `C:\Sistemas\olvidatasoft-crm`): cortes de gasto de la IA evaluados **antes de armar el request**, `DisponibilidadAsync` que devuelve el **motivo** y no un bool, costo por mensaje como valor del momento, tope mensual con barra de % consumido. Patrón sin código portable (otro dominio y moneda).
- Template M1: `EsperandoAprobacion`, `RequiereAprobacion`, idempotencia por `tool_use_id`, Cancelar. M4b (PAT-032): tarjetas confirmables en la conversación, estados con token y "dos aprobadores". M2: permisos, backoffice de organización, scoping del Empleado (PAT-017). M5 (D-M5-13): barra de uso ámbar/roja. Notificaciones del portal del template.
- **delicias-naturales** (modal de aprobación con SweetAlert2): patrón de UI para rechazar con motivo.
### Clasificacion de perfil de cliente M6
Producto propio (proyecto personal): presupuesto omitido.

---

**M5 — Workspace por cliente de cartera** (Discovery + Análisis, 2026-09-15). Estado: **aprobado sin gate por autorización de Joaquín 2026-09-14** (programa "plan completo local": M5→M12 sin frenar en gates; se toma la opción recomendada en cada pregunta y queda como hipótesis). Pendientes PA-01..13 siguen abiertos (ver `metadata.md`).

Contexto: el modelo D dice que los datos del cliente viven en el servidor de Olvidata, no en su disco (PLAN §4, `docs/diseno-motor-agentes.md` §3 y §5). Hoy existe solo la entidad `DocumentoCliente` (TenantId, Ruta, Contenido) sin UI ni herramientas, usada únicamente por tests como efecto genérico. El diseño de organización (`docs/diseno-organizacion-roles-reglas.md` §6) fija que "el workspace (M5) cuelga de `ClienteCartera`" y la decisión 4 que todos los miembros ven todos los clientes. M3b dejó explícitamente "adjuntar archivos en el seguimiento → M5". Objetivo de producto vigente (D-M3-8..12): usar agentes tiene que ser más simple que Claude web, donde hoy el usuario pega o sube el archivo a mano en cada conversación.

Objetivo de negocio: que cada organización guarde **una sola vez** los documentos de cada cliente de su cartera (contratos, balances, planillas, notas) y que los agentes los consulten en las tareas sobre ese cliente, sin volver a subirlos, con aislamiento entre organizaciones, costo acotado y sin que el contenido de un documento pueda dar órdenes al agente.

#### Alcance incluido (M5)
1. **Documentos del cliente** en la ficha del cliente de cartera: subir (uno o varios, arrastrando o eligiendo), listar con filtros, ver, descargar, renombrar y dar de baja.
2. **Tipos permitidos:** PDF, Word (.docx), Excel (.xlsx), CSV, texto (.txt, .md) e imágenes (JPG, PNG, WEBP). Validación por extensión **y** por contenido real; sin archivos con macros ni formatos viejos (.doc, .xls).
3. **Límites:** tamaño por archivo, espacio total por organización, cantidad por cliente y largo del texto legible por documento (ver P3); uso del espacio visible para el Director.
4. **Almacenamiento en el servidor fuera de `wwwroot`**, separado por organización y cliente, con nombre interno sin relación con el nombre original; descarga solo a través del portal con permisos.
5. **Lectura para agentes:** al subir, el sistema extrae el texto (PDF con texto, Word, Excel, CSV, texto) y lo divide en **partes** (página, hoja o bloque); cada documento muestra en lenguaje llano si el agente lo puede leer, solo en parte, o no (imagen / PDF escaneado / dañado).
6. **Herramientas del motor** para tareas con cliente de cartera: listar los documentos del cliente de la tarea, leer un documento por partes y buscar un texto en los documentos del cliente. Solo lectura; el cliente sale de la tarea, nunca de lo que pida el modelo; el contenido se entrega como información, nunca como instrucciones.
7. **Adjuntar documentos al pedir una tarea** (Agentes → Ejecutar) y **en los ajustes** de la conversación (M3b): el agente recibe cuáles se adjuntaron y los lee con las herramientas; en la conversación se ven como chips.
8. **Vista previa** en "Esto es lo que el agente va a tener en cuenta": documentos adjuntos y cuántos documentos más del cliente puede consultar, marcando los que no puede leer.
9. **"Ver pasos" en lenguaje llano** para las herramientas de documentos ("Leyó «Contrato.pdf», páginas 1 a 5"), sin JSON crudo (resuelve PA-12 solo para estas herramientas).
10. **Staff Olvidata:** en el backoffice, uso del espacio y listado de metadatos de documentos por organización (sin contenido ni descarga, ver P7).
11. **Modelo simulado** (solo Development) con guion de herramientas de documentos para QA sin costo.

#### Alcance no incluido
- Lectura visual de imágenes o PDF escaneados (visión/OCR) → mejora posterior (ver P2).
- Que el agente **escriba** o modifique documentos (borradores versionados, "guardar respuesta como documento") → mejora posterior (ver P11).
- Versiones de un mismo documento (reemplazar el archivo conservando historial) → se sube uno nuevo y se da de baja el viejo (ver P14).
- Documentos de la empresa sin cliente, carpetas o etiquetas → posterior (ver P12); base de conocimiento de Olvidata por rubro → **M10**; sistemas externos → **M11**.
- Papelera o restauración de documentos dados de baja (ver P8).
- Cuota por organización editable desde el backoffice (en M5 es configuración global).
- Antivirus del servidor (no disponible en hosting compartido; se mitiga con tipos restringidos y descarga como adjunto).
- Búsqueda semántica o por significado (la búsqueda es por texto).

#### Dependencias
- M1 (herramientas, idempotencia por `tool_use_id`), M2 (cartera, roles, visibilidad), M3 (instantánea y hash, declaración "archivos no son instrucciones"), M3b (ajustes, modelo simulado), M4b (guion de herramientas en el simulador, contexto de herramienta extendido). Hosting SmarterASP: carpeta de datos fuera del sitio y límites de request de IIS (a confirmar en M9).
- Previsto para **M12**: una programación podrá llevar documentos adjuntos fijos (mismo mecanismo de adjuntos por mensaje).
