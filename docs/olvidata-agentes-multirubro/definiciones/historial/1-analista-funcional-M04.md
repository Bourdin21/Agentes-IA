<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/1-analista-funcional.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 1-analista-funcional - M04 (21 bloques archivados)

- Casos de uso M4b
- Reglas funcionales M4b
- Permisos M4b
- Criterios de aceptacion M4b
- Supuestos M4b
- Riesgos M4b
- Banderas tempranas M4b
- Preguntas abiertas M4b (hipótesis)
- Reutilizacion relevada M4b
- Clasificacion de perfil de cliente M4b
- Casos de uso M4
- Reglas funcionales M4
- Permisos M4
- Criterios de aceptacion M4
- Supuestos M4
- Riesgos M4
- Banderas tempranas M4
- Preguntas abiertas M4 (hipótesis)
- Reutilizacion relevada M4
- Clasificacion de perfil de cliente M4
- Pedidos nuevos surgidos en el gate (2026-09-14) — ubicación CONFIRMADA: después de M4

---

### Casos de uso M4b
| CU | Actor | Descripción |
|---|---|---|
| CU-M4b-01 | Director | Inicia una conversación de configuración y describe cómo trabaja la empresa |
| CU-M4b-02 | Agente configurador | Consulta la estructura y las reglas actuales visibles para el Director |
| CU-M4b-03 | Agente configurador | Propone reglas nuevas, cambios, desactivaciones o activación de sugerencias |
| CU-M4b-04 | Director | Aplica, edita y aplica, o descarta cada propuesta; o aplica todas |
| CU-M4b-05 | Director | Retoma una conversación de configuración anterior |
| CU-M4b-06 | Miembro / staff | Ve en el historial de una regla que nació de una propuesta del agente |
| CU-M4b-07 | Staff Olvidata | Evalúa y publica el prompt del configurador en el núcleo |
### Reglas funcionales M4b
- **RF-M4b-01** Solo el Director inicia y continúa conversaciones de configuración (ver P2).
- **RF-M4b-02** Las herramientas del configurador leen solo datos de la organización del Director y solo lo que el Director puede ver en la pantalla de Reglas; nunca preferencias personales de otros ni datos de otras organizaciones.
- **RF-M4b-03** Una propuesta no modifica ninguna regla hasta que el Director la aplica. El texto de la conversación **no** es una confirmación: solo cuentan los botones.
- **RF-M4b-04** Al aplicar, se ejecuta el mismo camino que el formulario de Reglas (permisos del Director, validaciones de destino vigente, límites por balde, versiones, conflicto de edición). Si falla, la propuesta queda pendiente con el motivo visible.
- **RF-M4b-05** Una propuesta de cambio o desactivación referencia la versión de la regla que vio el agente; si la regla cambió después, al aplicar se avisa "Esta regla cambió desde la propuesta" y se ofrece revisar antes de aplicar.
- **RF-M4b-06** "Editar y aplicar" abre el formulario de regla precargado con la propuesta; al guardar, la propuesta queda aplicada con lo editado.
- **RF-M4b-07** Estados de propuesta: Pendiente → Aplicada / Descartada / Fallida (con motivo; reintentable). Una propuesta pendiente de una conversación vieja sigue disponible (ver P5).
- **RF-M4b-08** Las reglas creadas o cambiadas desde una propuesta registran origen "Propuesta del agente" y enlace a la conversación en su historial.
- **RF-M4b-09** El configurador no crea reglas personales ("Mis preferencias") de nadie ni reglas de otra organización; si se le pide, responde que no puede.
- **RF-M4b-10** Límites de conversación de M3b (10.000 caracteres por mensaje, 20 ajustes) y límite de propuestas por respuesta (ver P4).
- **RF-M4b-11** El prompt del configurador es de Olvidata: nunca se muestra, se versiona y evalúa en el núcleo; mientras no haya versión publicada, "Configurar conversando" no está disponible.
- **RF-M4b-12** Costo: las conversaciones de configuración consumen tokens como cualquier tarea y se imputan a la organización; se ven en el listado de Tareas con filtro "Configuración de reglas" (ver P6).
### Permisos M4b
| Acción | Director | Empleado | Staff |
|---|:---:|:---:|:---:|
| Iniciar / continuar configuración | ✅ | ❌ | ❌ |
| Aplicar / descartar propuestas | ✅ | ❌ | ❌ |
| Ver conversaciones de configuración | ✅ | ❌ (ver P2) | 👁 |
| Ver origen "Propuesta del agente" en el historial de una regla | ✅ | ✅ (reglas que ve) | ✅ |
| Publicar el prompt del configurador | — | — | ✅ núcleo |
### Criterios de aceptacion M4b
- **CA-M4b-01** El Director abre "Reglas → Configurar conversando", escribe "Somos un estudio contable; nunca prometemos plazos ante ARCA y hablamos formal" y recibe al menos una propuesta en tarjeta con dónde aplica, cuándo y el texto; ninguna regla cambia todavía.
- **CA-M4b-02** Aplicar una propuesta crea la regla con origen "Propuesta del agente"; aparece en Reglas y en la vista previa de una tarea nueva.
- **CA-M4b-03** "Editar y aplicar" abre el formulario precargado; lo guardado es lo editado.
- **CA-M4b-04** Descartar deja la propuesta "Descartada" y no toca reglas.
- **CA-M4b-05** Una propuesta que supera un límite queda "Fallida" con el mensaje de límite de M3; tras desactivar otra regla, reintentar la aplica.
- **CA-M4b-06** Una propuesta de cambio sobre una regla que otra persona editó después muestra "Esta regla cambió desde la propuesta" antes de aplicar.
- **CA-M4b-07** Escribir "aplicalo" en la conversación no aplica nada (RF-M4b-03).
- **CA-M4b-08** Las herramientas de lectura no devuelven preferencias personales de otros miembros ni datos de otra organización (verificable en tests con modelo guionado).
- **CA-M4b-09** Un Empleado no ve "Configurar conversando" y por URL/POST recibe 403; no puede aplicar propuestas ajenas.
- **CA-M4b-10** "Aplicar todas" aplica las válidas y deja las que fallan con su motivo.
- **CA-M4b-11** Sin versión publicada del configurador, la opción aparece deshabilitada con "Todavía no está disponible."
- **CA-M4b-12** La conversación se retoma y admite ajustes (M3b); las propuestas pendientes siguen accionables.
- **CA-M4b-13** El historial de una regla aplicada desde el configurador muestra el origen y enlaza a la conversación.
- **CA-M4b-14** El costo de la conversación aparece en Tareas bajo "Configuración de reglas".
- **CA-M4b-15** Ids de propuestas o conversaciones de otra organización → 404.
### Supuestos M4b
- S-M4b-01 El modelo puede producir propuestas estructuradas mediante herramientas de forma confiable; se valida con corrida real (PA-02).
- S-M4b-02 QA sin costo necesita un modelo simulado capaz de devolver llamadas a herramientas guionadas (hoy solo devuelve texto).
### Riesgos M4b
- R-M4b-01 (alto) **Propuestas equivocadas o sobreinterpretadas** (alcance o modo incorrecto) → confirmación explícita por tarjeta, "dónde aplica" en lenguaje llano, editar antes de aplicar.
- R-M4b-02 (alto) **Inyección y escalamiento**: textos de reglas existentes o del Director que intenten que el agente lea datos ajenos o aplique cambios → herramientas acotadas por código a los permisos del Director; aplicar solo por botón.
- R-M4b-03 (medio) **Costo**: conversaciones largas con lectura de muchas reglas → herramientas que devuelven resúmenes paginados, límites de M3b.
- R-M4b-04 (medio) **Calidad del prompt del configurador**: es contenido de Olvidata que hay que escribir y evaluar; sin él la función no está disponible.
- R-M4b-05 (bajo) Propuestas viejas aplicadas sobre reglas cambiadas → RF-M4b-05.
### Banderas tempranas M4b
- Migración EF: **sí** (propuestas de reglas; origen y enlace en eventos de regla; tipo de conversación).
- Integración externa: **no** nueva (API de Anthropic con herramientas). Validación real: requiere corrida con costo.
- Máquina de estados: **sí, leve** (propuesta).
### Preguntas abiertas M4b (hipótesis)
- **P1 — ¿Dónde vive el configurador?** *A:* opción "Configurar conversando" dentro de Reglas (conversación dedicada). *B:* un agente más en el catálogo de Agentes. *Hipótesis:* A (es una herramienta de configuración, no un agente de trabajo).
- **P2 — ¿Solo el Director?** *A:* solo Director en M4b. *B:* también Empleados, limitado a "Mis preferencias" y reglas de clientes. *Hipótesis:* A; B como mejora.
- **P3 — ¿Qué puede proponer?** Reglas de la empresa, de áreas, por agente y de clientes; cambios y desactivaciones; activar sugerencias. *Hipótesis:* confirmar (sin preferencias personales).
- **P4 — Límite de propuestas por respuesta.** *Hipótesis:* 10 por respuesta, para que el Director pueda revisarlas.
- **P5 — Propuestas pendientes viejas.** *A:* siguen pendientes sin vencimiento. *B:* vencen a los 30 días. *Hipótesis:* A.
- **P6 — ¿Dónde se ve el costo?** *A:* en Tareas con filtro "Configuración de reglas" (visibles solo para Directores y staff). *B:* aparte, solo en la pantalla del configurador. *Hipótesis:* A.
- **P7 — Prompt del configurador.** El contenido del prompt es de Olvidata. *A:* lo redacto yo en borrador como primera versión y vos lo revisás y publicás con evaluación. *B:* lo escribís vos. *Hipótesis:* A (es de plataforma, no de un rubro, así que no choca con "template antes que rubros").
- **P8 — Modelo simulado con herramientas para QA.** *Hipótesis:* extender el modelo simulado (solo Development) para devolver llamadas a herramientas guionadas y poder probar las tarjetas sin costo.
- **P9 — ¿"Aplicar todas"?** *Hipótesis:* sí, con resumen de resultados.
### Reutilizacion relevada M4b
- **crm-olvidata** (`docs/crm-olvidata/definiciones/3-arquitecto-mvc.md`): el modelo solo devuelve la acción por *function calling* y el servicio de negocio la ejecuta con sus validaciones ("sin función que llamar, el modelo no puede inventar un precio"). Aplica directo: propuestas por herramientas, aplicación por el servicio de reglas.
- Template propio: herramientas y `RequiereAprobacion` (M1), `ReglaService` (M3), conversación y modelo simulado (M3b), sugerencias y agentes (M4), núcleo con evaluación.
### Clasificacion de perfil de cliente M4b
Producto propio (proyecto personal): presupuesto omitido.

---

**M4 — Agentes de la organización** (Discovery + Análisis, 2026-09-14). Estado: **aprobado por Joaquín el 2026-09-14 con todas las hipótesis P1–P11** (P1 última versión publicada del base · P2 Director no ve personales ajenos · P3 reglas del base aplican a derivados · P4 8.000 / 50 / 10 · P5 edición de Empleado vuelve a revisión · P6 y P7 solo mecanismos, sin contenido; sugerencias las activa el Director · P8 casillas · P9 modelo heredado · P10 duplicar · P11 ajustes permitidos en tareas de agentes archivados). **Ajuste en el gate de Diseño (2026-09-14): se saltea "En revisión del Director" por ahora — cualquier miembro publica directo para toda la empresa; RF-M4-06 y RF-M4-07 (propuesta/aprobación y vuelta a revisión) quedan pospuestos; el Director puede editar y archivar cualquier agente de la empresa; P5 queda sin efecto.** Pendientes previos PA-01..PA-07 quedan abiertos por decisión de Joaquín (ver `metadata.md`).

Contexto: hoy cada organización usa solo los agentes base de Olvidata de sus rubros suscriptos. El diseño de producto aprobado (`docs/diseno-organizacion-roles-reglas.md` §2, §4, §5, decisiones 2 y 6) define agentes de la organización creados siempre a partir de un agente base, con instrucciones propias, herramientas acotadas, visibilidad personal u organización (publica el Director), área destino, versionado propio, y el nivel 6 de precedencia reservado desde M3. También define un rubro transversal "negocio" incluido en todas las suscripciones y, desde M3, reglas sugeridas por rubro.

Relevamiento del repo: no existe el rubro "negocio" en `nucleo/rubros/` y `LicenciaService.CrearAsync` no agrega rubros automáticamente. Ningún proyecto del estudio tiene agentes configurables por el cliente.

Objetivo de negocio: que cada empresa adapte los agentes de Olvidata a sus procesos (ej. "CM del estudio" desde el community manager base) sin escribir prompts desde cero, con control del Director sobre lo que se comparte con toda la organización, y que Olvidata pueda incluir agentes transversales y sugerencias de reglas sin tocar código.

#### Alcance incluido (M4)
1. **Crear agente de la organización** desde un agente base de la suscripción vigente: nombre, descripción, instrucciones propias, herramientas (subconjunto de las del base), visibilidad (Personal / Organización) y área destino opcional.
2. **Versionado propio**: borrador → publicada; editar una versión publicada crea un borrador nuevo; las tareas quedan ancladas a la versión usada.
3. **Publicación para la organización**: el Director publica directo; un Empleado **propone** y el Director aprueba o rechaza con motivo. Un agente personal lo publica su creador sin aprobación.
4. **Catálogo de Agentes unificado**: agentes base + agentes de la organización publicados + agentes personales propios; destacados los del área del usuario; búsqueda.
5. **Tareas con agente de la organización**: la instantánea incluye la versión del agente de la organización; sus instrucciones entran en el nivel 6 del contexto; las reglas "Por agente" pueden apuntar también a un agente de la organización; M3b funciona igual.
6. **Archivar / reactivar** agentes sin borrarlos; tareas históricas intactas.
7. **Duplicar** un agente como punto de partida (ver P10).
8. **Rubro incluido siempre** (mecanismo): un rubro del núcleo puede marcarse como incluido en todas las suscripciones; se agrega al emitir y renovar licencias, con sincronización de licencias vigentes desde la consola Admin. **Sin crear el contenido** del rubro "negocio" (ver P6).
9. **Reglas sugeridas por rubro** (mecanismo): el núcleo publica sugerencias de reglas por rubro (con evaluación); el Director las ve y las activa como reglas de la organización o de un área. **Sin redactar el contenido** (ver P7).
10. **Staff**: lectura de los agentes de cada organización con sus instrucciones (coherente con P9 de M3).

#### Alcance no incluido
- Agentes desde cero, sin agente base (decisión 2).
- Herramientas nuevas o conectores → **M11**; configurador de reglas del Director → **M4b**; subagentes y asistente que reparte tareas → **M7**; evaluación automática de agentes de la organización → **M8**.
- Compartir agentes entre organizaciones o publicarlos en un catálogo público.
- Elegir un modelo distinto al del agente base (ver P9).
- Textos concretos de agentes de marketing/CM/ventas y de reglas sugeridas (contenido del rubro, lo define Joaquín).
- Estadísticas de uso por agente (se ven hoy por tarea).

#### Dependencias
- M3 (constructor de contexto, instantánea, reglas por agente, rótulos llanos), M3b (conversación), M2 (roles y áreas), núcleo versionado (importador, evaluación, publicación).
### Casos de uso M4
| CU | Actor | Descripción |
|---|---|---|
| CU-M4-01 | Miembro | Crea un agente personal desde un agente base |
| CU-M4-02 | Director | Crea y publica un agente para toda la organización |
| CU-M4-03 | Empleado | Propone un agente (o una versión nueva) para la organización |
| CU-M4-04 | Director | Aprueba o rechaza una propuesta con motivo |
| CU-M4-05 | Creador / Director | Edita un agente creando una versión nueva; archiva y reactiva |
| CU-M4-06 | Miembro | Ve el catálogo unificado y pide una tarea a un agente de la organización |
| CU-M4-07 | Miembro | Duplica un agente como punto de partida |
| CU-M4-08 | Staff Olvidata | Marca un rubro como incluido siempre y sincroniza licencias |
| CU-M4-09 | Staff Olvidata | Publica reglas sugeridas por rubro en el núcleo |
| CU-M4-10 | Director | Activa una regla sugerida en la organización o en un área |
| CU-M4-11 | Staff Olvidata | Consulta los agentes de una organización (solo lectura) |
### Reglas funcionales M4
- **RF-M4-01** Un agente de la organización siempre referencia un agente base habilitado por una suscripción vigente; si la suscripción vence, el agente queda "No disponible" (visible, no utilizable).
- **RF-M4-02** Las herramientas elegidas son un subconjunto de las del agente base; al ejecutar se usa la intersección con las del base vigente (si Olvidata quita una herramienta del base, el derivado no la conserva).
- **RF-M4-03** Versión del agente base usada por un derivado: la **última publicada** al crear cada tarea (ver P1); la tarea queda anclada a esa versión y a la del agente de la organización.
- **RF-M4-04** Nombre obligatorio y único entre agentes activos de la organización; instrucciones hasta 8.000 caracteres (ver P4).
- **RF-M4-05** Visibilidad: **Personal** = solo su creador lo ve y lo usa; **Organización** = todos los miembros lo ven y lo usan.
- **RF-M4-06** Publicación para la organización: Director directo; Empleado propone y el agente/versión queda "En revisión" hasta que el Director aprueba (publica) o rechaza (con motivo visible para el creador). Mientras tanto el creador puede seguir usando su última versión publicada.
- **RF-M4-07** Un agente de la organización ya publicado lo editan su creador y el Director; si lo edita un Empleado, la versión nueva vuelve a revisión (ver P5).
- **RF-M4-08** El prompt del agente base nunca se muestra; el creador ve y edita solo su capa (instrucciones, herramientas, datos).
- **RF-M4-09** Contexto: las instrucciones del agente de la organización entran en el nivel 6 (después de las reglas del cliente y antes de "De tu área" y "De la empresa" por defecto); las reglas "Por agente" de un agente de la organización aplican solo a él; las reglas "Por agente" del agente base aplican también a sus derivados (ver P3). La vista previa y "Lo que el agente tuvo en cuenta" muestran "Instrucciones de <agente>".
- **RF-M4-10** Archivar saca el agente del catálogo y de nuevas tareas; sus tareas y conversaciones siguen disponibles; reactivar lo devuelve con su última versión publicada. Un agente archivado no admite nuevos ajustes (M3b) hasta reactivarlo (ver P11).
- **RF-M4-11** Duplicar crea un agente nuevo en borrador, personal, con la misma base, instrucciones y herramientas.
- **RF-M4-12** Rubro incluido siempre: se agrega a toda licencia al crearla y al renovarla; un comando de la consola Admin lo agrega a las licencias vigentes; nunca se aplica al rubro técnico `plataforma`.
- **RF-M4-13** Reglas sugeridas: artefactos del núcleo por rubro, con evaluación antes de publicar; el Director ve las del rubro de sus suscripciones y al activarlas se crea una regla de la organización (o del área elegida) con el texto copiado, modo "Salvo que se indique otra cosa" por defecto y origen "Sugerida"; cambios posteriores en la sugerencia no alteran reglas ya activadas.
- **RF-M4-14** Límites (ver P4): hasta 50 agentes activos por organización y 10 personales por persona.
- **RF-M4-15** Aislamiento: agentes, versiones y propuestas nunca cruzan organizaciones (ids ajenos → 404).
### Permisos M4
| Acción | Director | Empleado (creador) | Empleado (otro) | Staff |
|---|:---:|:---:|:---:|:---:|
| Crear agente personal | ✅ | ✅ | — | ❌ |
| Publicar para la organización | ✅ directo | 📝 propone | — | ❌ |
| Aprobar / rechazar propuestas | ✅ | ❌ | ❌ | ❌ |
| Ver/usar agente de la organización | ✅ | ✅ | ✅ | 👁 lectura |
| Ver agente personal ajeno | ❌ (ver P2) | — | ❌ | 👁 lectura |
| Editar agente de la organización | ✅ | ✅ (vuelve a revisión) | ❌ | ❌ |
| Archivar / reactivar | ✅ cualquiera | ✅ los suyos personales | ❌ | ❌ |
| Activar reglas sugeridas | ✅ | ❌ | ❌ | — |
| Rubro incluido siempre / reglas sugeridas en el núcleo | — | — | — | ✅ |
### Criterios de aceptacion M4
- **CA-M4-01** Un Empleado crea "Mis mails formales" desde un agente base, lo publica como personal y le pide una tarea: la vista previa muestra "Instrucciones de Mis mails formales" en su lugar de prioridad; otro miembro no lo ve en el catálogo ni por URL (404).
- **CA-M4-02** El Director crea "CM del estudio" con visibilidad Organización y área destino Marketing; aparece para todos, destacado para Marketing.
- **CA-M4-03** Un Empleado propone un agente para la organización: queda "En revisión", el Director lo ve en "Propuestas", lo aprueba y pasa a estar disponible para todos; si lo rechaza, el creador ve el motivo y el agente sigue siendo personal.
- **CA-M4-04** Solo se pueden marcar herramientas del agente base; un POST con otra herramienta no se guarda.
- **CA-M4-05** Editar un agente publicado crea la versión N+1 en borrador; las tareas previas conservan en su detalle la versión usada; al publicar, las tareas nuevas usan N+1.
- **CA-M4-06** El prompt del agente base no aparece en ninguna pantalla ni respuesta del portal para miembros.
- **CA-M4-07** Una regla "Por agente" apuntada a "CM del estudio" aplica solo a sus tareas; una regla "Por agente" del agente base aplica también a "CM del estudio" (según P3).
- **CA-M4-08** Archivar un agente lo saca del catálogo; sus tareas siguen visibles; reactivarlo lo devuelve.
- **CA-M4-09** Con la suscripción del rubro vencida, el agente se muestra "No disponible" y no se pueden crear tareas ni ajustes.
- **CA-M4-10** Nombre repetido entre activos o instrucciones de más de 8.000 caracteres no se guardan; al superar 50 agentes activos o 10 personales se muestra el límite.
- **CA-M4-11** Duplicar crea una copia personal en borrador con los mismos datos.
- **CA-M4-12** Con un rubro marcado "incluido siempre", una licencia nueva lo trae aunque no se haya elegido; el comando de sincronización lo agrega a las vigentes; `plataforma` nunca se incluye.
- **CA-M4-13** El Director ve las reglas sugeridas publicadas de sus rubros, activa una en el área Marketing y aparece como regla del área con origen "Sugerida"; una sugerencia en borrador no se ve.
- **CA-M4-14** El staff ve los agentes de una organización con instrucciones, sin acciones.
- **CA-M4-15** Ids de agentes, versiones o propuestas de otra organización en URL o POST → 404.
### Supuestos M4
- S-M4-01 Los agentes base actuales tienen pocas herramientas (hoy `fecha_hora_actual`); el valor inicial de M4 está en las instrucciones, no en las herramientas.
- S-M4-02 El contenido del rubro "negocio" y de las reglas sugeridas lo define Joaquín después; M4 se valida con datos de prueba.
### Riesgos M4
- R-M4-01 (alto) **Instrucciones del cliente como vía de inyección** para anular reglas de plataforma o extraer el prompt base → mismo tratamiento que reglas (nivel fijo, escape, declaración de precedencia); no es garantía total (PA-02).
- R-M4-02 (medio) **Cambios del agente base** afectan a todos sus derivados (P1): una mejora de Olvidata puede cambiar el comportamiento esperado por una organización.
- R-M4-03 (medio) **Complejidad de estados** (propuestas, revisiones, archivado, no disponible) contra el objetivo de simplicidad → UI en lenguaje llano y flujo guiado.
- R-M4-04 (bajo) **Proliferación de agentes** parecidos → límites y duplicar en lugar de crear de cero.
### Banderas tempranas M4
- Migración EF: **sí** (agentes de la organización, versiones, propuestas, referencia en tareas y reglas, marca de rubro incluido, reglas sugeridas).
- Integración externa: **no** nueva.
- Máquina de estados: **sí** (versión del agente: borrador → revisión → publicada/rechazada → reemplazada).
### Preguntas abiertas M4 (hipótesis)
- **P1 — Versión del agente base en los derivados.** *A:* siempre la última publicada (las mejoras de Olvidata llegan solas). *B:* fija al crear/publicar el agente de la organización (se actualiza a mano). *Hipótesis:* A.
- **P2 — ¿El Director ve los agentes personales de su equipo?** *A:* no (son privados, como las preferencias). *B:* sí, en lectura. *Hipótesis:* A; el staff sí (P9 de M3).
- **P3 — Reglas "Por agente" del agente base.** ¿Aplican también a sus derivados? *Hipótesis:* sí.
- **P4 — Límites.** Instrucciones 8.000 caracteres; 50 agentes activos por organización; 10 personales por persona. *Hipótesis:* confirmar.
- **P5 — Empleado edita un agente de la organización que creó.** *A:* la versión nueva vuelve a revisión del Director. *B:* se publica directo por ser el creador. *Hipótesis:* A.
- **P6 — Rubro "negocio".** M4 construye solo el mecanismo "rubro incluido siempre", sin crear agentes de marketing/CM/ventas (contenido tuyo). *Hipótesis:* sí.
- **P7 — Reglas sugeridas.** M4 construye el mecanismo y la pantalla del Director, sin redactar sugerencias. *Hipótesis:* sí; solo el Director las activa.
- **P8 — Herramientas.** El creador elige un subconjunto de las del base con casillas. *Hipótesis:* sí.
- **P9 — Modelo.** Se hereda del agente base, no se elige. *Hipótesis:* sí.
- **P10 — Duplicar.** *Hipótesis:* incluir (reduce agentes creados de cero).
- **P11 — Ajustes (M3b) sobre tareas de un agente archivado.** *A:* bloqueados hasta reactivar. *B:* permitidos (la tarea está anclada a su versión). *Hipótesis:* B (la conversación ya empezó; archivar solo evita tareas nuevas).
### Reutilizacion relevada M4
- Template propio: constructor de contexto + instantánea (M3), reglas "Por agente" (M3), versiones inmutables del núcleo y flujo de evaluación/publicación (M1/M3), importador de manifiestos con `reglas_plataforma` (M3) como base de `reglas_sugeridas` y "incluido siempre", pantallas y listados de M2/M3, conversación (M3b).
- Sin proyecto del estudio con agentes configurables por el cliente.
### Clasificacion de perfil de cliente M4
Producto propio (proyecto personal): presupuesto omitido.

---

**M3b — Seguir conversando sobre una tarea** (Discovery + Análisis, 2026-09-14). Estado: **aprobado por Joaquín el 2026-09-14 con todas las hipótesis P1–P8** (P1 solo autor · P2 reglas congeladas con aviso · P3 Completada, Fallida y Cancelada · P4 10.000 caracteres y 20 seguimientos · P5 pasos por turno · P6 ocultar texto de preferencias ajenas al Director · P7 sin compactación · P8 "Seguir conversando").

Contexto: hoy una tarea es un pedido y una respuesta. `ProcesadorTareas` reconstruye la conversación desde `Entrada` + `PasoTarea` y, cuando el modelo termina el turno, marca la tarea `Completada`; no hay forma de responderle. En la conversación con Joaquín (2026-09-14) se detectó que sin iterar sobre el resultado ("más corto", "cambiá el segundo párrafo") los usuarios volverían a Claude web, lo que contradice el objetivo del producto: reemplazar prompts sueltos por agentes organizados y simples.

Objetivo de negocio: que el usuario pueda seguir la conversación con el agente dentro de la misma tarea, con el mismo contexto (agente, cliente y reglas), sin volver a explicar nada y con el costo a la vista.

#### Alcance incluido (M3b)
1. **Mensaje de seguimiento** en el detalle de una tarea terminada: el usuario escribe y la tarea vuelve a la cola; el agente responde con toda la conversación anterior como contexto.
2. **Vista de conversación**: pedido inicial, respuestas y seguimientos en orden, como un chat; los pasos técnicos (herramientas) quedan plegados dentro de cada respuesta.
3. **Mismo contexto** en toda la conversación: agente, cliente de cartera e instantánea de reglas de la tarea (ver P2).
4. **Progreso en vivo** del nuevo turno con el mecanismo existente (SignalR + respaldo).
5. **Costo y tokens acumulados** de la conversación visibles, y **límites** de seguimientos por tarea y de largo del mensaje.
6. **Copiar respuesta** al portapapeles.
7. **Listado de Tareas**: columna/filtro "Última actividad" y cantidad de mensajes; una tarea con seguimiento en curso vuelve a mostrarse "En curso".
8. Compatibilidad con tareas de M1/M2 (sin instantánea).

#### Alcance no incluido
- Adjuntar archivos en el seguimiento → **M5** (workspace).
- Editar un mensaje anterior, regenerar una respuesta o ramificar la conversación.
- Resumir/compactar conversaciones largas automáticamente (ver P7).
- Cambiar de agente o de cliente a mitad de la conversación (para eso, tarea nueva).
- Streaming token a token de la respuesta (se mantiene progreso por pasos).
- Seguimiento sobre tareas de otros miembros (ver P1).

#### Dependencias
- M1 (motor reanudable, SignalR), M2 (visibilidad por rol), M3 (instantánea de reglas por tarea).
### Pedidos nuevos surgidos en el gate (2026-09-14) — ubicación CONFIRMADA: después de M4
- **N-01 Agente configurador de reglas del Director:** un agente que ayuda al Director a redactar y cargar las reglas de la organización (por conversación en vez de formulario). Implica herramientas que crean/editan reglas → requiere reglas "propuestas por agente" con confirmación del Director (hoy planificado en M7) y el ABM de reglas de M3 como base.
- **N-02 Agente asistente que crea tareas a empleados / subagentes:** un agente del Director que reparte trabajo: crea tareas para empleados (tareas asignadas a personas, concepto nuevo, hoy toda tarea es de un agente) o delega en subagentes (M7). Toca permisos de asignación, notificaciones y aprobaciones (M6).
- Propuesta de ubicación (a confirmar): M3 deja las reglas con servicio reutilizable por herramientas; N-01 entra como etapa propia inmediatamente después de M4 (necesita agentes de la organización); N-02 se une a M7 (subagentes) + tareas asignadas a personas.
