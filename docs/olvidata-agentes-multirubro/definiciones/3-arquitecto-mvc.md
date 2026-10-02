# Memoria - Arquitecto MVC

## Proyecto: olvidata-agentes-multirubro
## Ultima actualizacion: 2026-10-02 (M28: chat libre -- sin migracion, EsDePlataforma como palanca, dos modos de subagentes) | 2026-10-01 (M27)

## Definiciones vigentes

## Arquitectura M28 — El chat libre (2026-10-02)

Entrada: Diseño M28 cerrado (`2-disenador-funcional.md`, D-01..D-09, P1..P4, HU-01..HU-08). Reutilización: **PAT-029**. Escaneo de reutilización hecho sobre `cat_resumen.txt` (instrucción 39 §3): el motor entero se reutiliza; **sin antecedente** para autocomplete de menciones y para carga diferida de una pieza 3D.

### A-00 — El hallazgo que corrige al Análisis: no hace falta migración

El Análisis dejó la bandera «Requiere migración EF: **sí**, valor nuevo de `TipoTarea`». **Es incorrecta y se corrige acá.** `TareaAgente.Tipo` **no tiene ninguna línea** en `TareaAgenteConfiguration` (`AgentesConfigurations.cs:181-215`): cae en la convención de EF para enums y el snapshot lo confirma como `b.Property<int>("Tipo").HasColumnType("int")`. Un valor nuevo del enum no cambia el esquema. El propio repo ya dejó el precedente escrito en `EnumsAgentes.cs:128-131` para `TipoPasoTarea.NotaDelMotor`, **junto con la advertencia que sí importa**: lo que un valor nuevo rompe no es la base, son **los switches con `default`**, que lo aceptan en silencio y lo mapean mal. Ahí está el riesgo real de M28, y es R-A1.

**M28 no lleva migración.** Si al implementar aparece una, es señal de que se agregó una entidad que el diseño no pedía.

### A-01 — La palanca: `EsDePlataforma`

`ClasesDeTarea.EsDePlataforma(tipo)` (`Application/Motor/NotaSubtarea.cs:35-36`) es el único punto que hay que tocar para que **todas** las herramientas que ya distinguen plataforma de trabajo acepten el chat libre sin tocarlas una por una: `HerramientasMemoria`, `HerramientasInstructivos`, `HerramientaCalcular`, `HerramientaAdjuntoLeer`, `HerramientasDocumentos`. De él depende además `UsaContextoDeTrabajo` (:42).

Es una línea con mucho alcance, así que es **lo primero que se prueba**, no lo último: un test que afirme, para `TipoTarea.ChatLibre`, exactamente qué herramientas resuelve `ResolvedorHerramientas` y cuáles no.

### A-02 — El cuarto agente de plataforma: qué se agrega, por capa

Lo que sigue es un **molde que ya existe tres veces**. El agente del chat libre se arma copiando el del analista, que es el más parecido (lo usa cualquier miembro, no solo el Director).

| Capa | Qué se agrega |
|---|---|
| **Domain** | `TipoTarea.ChatLibre = 6` (`EnumsAgentes.cs:94-107`), con el comentario de por qué no lleva migración. **Nada más.** |
| **Application** | `IConstructorContexto.FormatoContextoChatLibre = 6` (:141) + `ArmarChatLibreAsync` en la interfaz · `IChatLibre` con `SlugChatLibre = "chat-libre"` y `DisponibleAsync` (al lado de `IAnalistaAutomatizaciones`, `IPropuestaTrabajoService.cs:44-52`) · `ClasesDeTarea.EsDePlataforma` (A-01) · `MensajesChatLibre` (sin permiso / vacío / no disponible) · `EtapasEntrega`: `OpcionMenu.ChatLibre` (y **no** entra en `SoloDirector`) · flag `EsChatLibre` en `TareaDetalleDto` (`IMotorAgentes.cs:471-484`) |
| **Infrastructure** | `ConstructorContexto`: `DeclaracionPrecedenciaChatLibre` + wrapper `ArmarChatLibreAsync` — **`ArmarPlataformaAsync` no se toca, es genérica** (recibe formato, tipo y declaración por parámetro) · `ServicioTareas`: `IniciarChatLibreAsync` + los switches de `:250` (permiso), `:277-282` (constructor), `:817-819` (flags), `:114-115` (listado del no-Director) · `ProcesadorTareas`: `:1287-1288` (constructor al retomar), `:451-454` (evento de telemetría), `:205-206` (mensaje de autor sin permiso) · `AnatomiaAgenteService`: `:115-118`, `:244-245`, `:292-294` · `EstimadorCorrida:155-158` · `ConsumoService:263-270` · `PermisosOrganizacion.PuedeUsarChatLibre => EsMiembro && !EsStaff` · `ChatLibre : IChatLibre` + DI |
| **Web** | `ChatLibreController` (`RequireMiembro`, molde de `AnalistaController`) con `Index` (arranque) e `Iniciar` · `Views/ChatLibre/Index.cshtml` · `MenuOrganizacion`: un ítem con `OpcionMenu.ChatLibre` · `Views/Tareas/Index.cshtml:144-147`: el `<option>` del filtro (y **de paso los dos que faltan hoy**, analista y `ConsultaCliente`) |
| **Núcleo** | `nucleo/plataforma/agentes/chat-libre.md` (prompt + frontmatter `herramientas`) · `nucleo/plataforma/plataforma.yml`: una línea en `agentes:` · `nucleo/plataforma/evaluaciones/13-chat-libre.yml` · **la suite común `00-suite-seguridad-agentes.yml` lo corre automáticamente** |

**Nada se publica solo:** el agente entra en **Borrador**, y sin versión publicada `DisponibleAsync` es `false`, el menú no lo muestra y el controller contesta «Todavía no está disponible.» (CA-01.2). El circuito es `importar` → `evaluar --aprobada` → `publicar`.

**Las instrucciones compartidas de plataforma** (`nucleo/plataforma/instrucciones/`) entran por `instrucciones:` del manifiesto y las toma `ArmarPlataformaAsync` sin cambios: el chat libre hereda *cómo proponen, los cinco conceptos y cuándo derivan* **sin una cuarta copia**. Esto es lo que hace viable D-06 y CU-06.

### A-03 — Menciones: dónde vive la resolución

**La mención se resuelve en el servidor, dos veces y en dos lugares distintos, porque son dos cosas distintas:**

1. **Para el autocomplete** (lectura, pantalla): un endpoint del `ChatLibreController` que devuelve lo mencionable para el usuario actual. **No se escribe una consulta nueva.**
2. **Para ejecutar** (autorización): la resuelve **el agente con sus herramientas**, no el controller. El chat libre recibe `agentes_disponibles` y `delegar_subagente`; el texto `@slug` es solo lo que el modelo lee para saber a quién llamar, y **la autorización la hace la herramienta** sobre los mismos `IQueryable` del punto siguiente.

Esta separación es la que cierra **R-03**: aunque alguien escriba `@` de un agente ajeno, el id nunca viaja desde el cliente y la herramienta solo encuentra lo que esa persona podía usar. **La mención es texto; la autorización es una consulta.**

**A-03b — Deuda que hay que pagar acá, no después.** Los dos `IQueryable` que definen «los agentes que esta persona puede usar» están hoy **duplicados en tres lugares** (`HerramientasAsistente.cs:86/97`, `HerramientasAnalista.cs:76/87`, `HerramientasConfigurador.cs:286`). M28 sería la cuarta copia. Se **extraen a `IAgentesDisponiblesQuery` en Application** (impl en Infrastructure) y los tres llamadores pasan a usarla. No es refactor cosmético: es la **única** forma de que el autocomplete de la pantalla y la autorización de la herramienta no puedan divergir — y si divergen, el autocomplete ofrece algo que la herramienta después rechaza, que es el peor resultado posible para la persona.

### A-04 — Delegar desde el chat libre: qué se parametriza en M7a

`SubtareasService` corta el chat libre por **dos** razones, y las dos están en `:68` y `:112`:

```
contexto.TipoTarea != TipoTarea.Trabajo   ||   contexto.ArtefactoBaseId is not int baseId
```

Un chat libre no es `Trabajo` **y no tiene agente base**. Y después, `:78` y `:89` filtran por `ArtefactoPadreId == baseId`: la jerarquía coordinador→hijos.

**Decisión de arquitectura: no se relaja el gate, se le da un segundo modo explícito.**

`SubagentesPermitidosAsync` pasa a tener dos ramas, nombradas:

- **Modo jerarquía** (lo de hoy, `TipoTarea.Trabajo` con `ArtefactoBaseId`): hijos publicados del agente base. **Sin un solo cambio de comportamiento.**
- **Modo abierto** (`TipoTarea.ChatLibre`): todo lo que devuelve `IAgentesDisponiblesQuery` (A-03b) — los mismos agentes que el autocomplete ofrece, ni uno más.

Por qué no un solo predicado con un `if` adentro: porque los dos modos tienen **reglas de seguridad distintas** y mezclarlos en una expresión es exactamente cómo se cuela una fuga. Dos ramas, dos tests, y el gate de `TipoTarea` sigue siendo una lista blanca (`Trabajo` o `ChatLibre`), **nunca** un `!=` negado.

Lo que **no** cambia: el filtro de licencia del rubro (`:73-79`), el de visibilidad y creador (`:90`), `ProfundidadMaxima` (así un agente alcanzado por mención no puede volver a entrar — CA-02.6), los topes por paso y por turno (`:119-133`), y el largo del pedido (`:140`).

Mismo gate hay que abrir en `HerramientasSubagentes.cs:39` y en `SubtareasService.PorTareaAsync:277` (el segundo es lo que **dibuja** la tarjeta de parte en la conversación: sin él, D-07 no se ve).

**El despertar ya está resuelto y no hay que tocarlo**, lo cual cierra **R-04** sin código nuevo: `AvisarFinAsync:211-213` cuenta como pendiente solo lo que **no** está en `Completada | Fallida | Cancelada`, así que el padre vuelve a `Pendiente` **también cuando la parte falla o se cancela**, y `ResultadoParaCoordinador:174-191` le entrega el fallo como `ResultadoHerramienta.Fallo(...)`. CA-02.5 se verifica, no se implementa.

### A-05 — La pieza 3D: la primera carga diferida del proyecto

Hoy **no hay ningún patrón de carga diferida** en el repo: cero `defer`, cero `async`, cero `import()` dinámico; los scripts por vista se agregan en `@section Scripts` (`_Layout.cshtml:368`). M28 establece el patrón, y lo establece **acotado a esta pieza**.

- **Librería: `three` por CDN jsdelivr, con `import()` dinámico** desde un módulo propio `wwwroot/js/chat-libre-3d.js`. No entra en `_Layout`, no entra en `site.js`, y **no se descarga nunca** si no se cumplen las tres condiciones de abajo. Se declara la versión fija en la URL (no `latest`): un CDN que cambia de versión sola es un despliegue que no hicimos.
- **Tres compuertas antes de pedir el script**, en este orden y todas en el cliente: (1) `matchMedia('(prefers-reduced-motion: reduce)')` no coincide; (2) hay contexto WebGL disponible; (3) la pantalla de arranque está efectivamente montada. Si cualquiera falla, **no se pide la librería** y queda la versión plana (CA-07.3, CA-07.5).
- **Desmontaje obligatorio** al enviar el primer mensaje (D-01): cancelar el `requestAnimationFrame`, `renderer.dispose()`, soltar geometrías y materiales, y quitar el canvas. No `display:none`. RD-02 es el riesgo y se verifica con el monitor de rendimiento, no mirando la pantalla.
- La pieza **no recibe ni muestra datos**: es decorativa. Así no hay ninguna vía por la que un dato de la organización llegue a un script de CDN.

**A-05b — El autocomplete va en `site.js`, no en la vista** (D-03). Es un comportamiento compartido que se enciende con un atributo en el `<textarea>`, igual que `data-autosize` que M27 ya dejó ahí. Queda disponible en las cinco conversaciones sin tocar sus vistas. Teclado completo (flechas, Enter, Tab, Escape) y apertura hacia arriba si no hay lugar abajo (RD-04).

### A-06 — Impacto por capa (resumen)

- **Domain:** un valor de enum. **Sin migración** (A-00).
- **Application:** una constante de formato, una interfaz de agente, una query compartida nueva (`IAgentesDisponiblesQuery`), una opción de menú, un flag de DTO, los mensajes.
- **Infrastructure:** el wrapper de contexto, el arranque de tarea, los ~10 switches de la tabla A-02, los dos modos de `SubagentesPermitidosAsync`, el permiso, y los tres llamadores que pasan a usar la query compartida.
- **Web:** un controller, una vista de arranque, un ítem de menú, un `<option>` de filtro, `site.js` (autocomplete), `chat-libre-3d.js` (nuevo), CSS del arranque y del menú de menciones con tokens `--ov-*`.
- **Núcleo:** un prompt, una línea del manifiesto, una suite de evaluación.
- **Tests:** `ChatLibreTests.cs` nuevo (molde: `AnalistaAutomatizacionesTests.cs`), más extensión de `ConstructorContextoTests` + goldens, `SubagentesTests` (los dos modos), `EtapaEntregaTests`, `MenuLateralTests`, `AnatomiaAgenteTests`, `ConversacionTests`.

### Riesgos técnicos

- **R-A1 (alto) — Los switches con `default` que aceptan el tipo nuevo en silencio.** Es el riesgo central de M28 y el repo ya lo tiene escrito como lección (`EnumsAgentes.cs:128-131`). Un `default` que cae en «configuración» no da error: da un contexto equivocado con un agente equivocado. Mitigación: la tabla de A-02 es la lista de verificación, y **un test por switch de mapeo** que afirme el valor esperado para `ChatLibre` — no un test que pruebe que «funciona».
- **R-A2 (alto) — Divergencia entre lo que el autocomplete ofrece y lo que la herramienta autoriza.** Mitigación: A-03b, una sola query compartida, y un test que corra **la misma** query por los dos caminos.
- **R-A3 (medio) — El modo abierto de subagentes se filtra al modo jerarquía.** Mitigación: dos ramas separadas, lista blanca de `TipoTarea` (nunca `!=`), y un test que afirme que una tarea de **trabajo** sigue viendo **solo** los hijos de su base.
- **R-A4 (medio) — Costo.** Cada turno reenvía la conversación completa (nota de PAT-029) y ahora puede abrir tareas. Mitigación: el tope de gasto de M6 **sin tocar un solo valor**, el costo visible por tarea y por hilo, la cache de prompt sobre el historial, y D-05 (una mención de agente por mensaje).
- **R-A5 (medio) — El CDN de la librería 3D.** Un CDN caído o bloqueado no puede romper la pantalla. Mitigación: el `import()` va en `try/catch` y su fallo es **silencioso** con degradación a la versión plana (CA-07.5). Versión fija en la URL.
- **R-A6 (bajo) — El formato 6 y los hashes viejos.** La instantánea guarda formato y versiones por tarea, así que agregar el 6 no toca ninguna tarea existente (CA-T.3). Nota aparte encontrada al revisar: el switch de `ArmarEvaluacionAsync` (`ConstructorContexto.cs:505-506`) **hoy solo cubre los formatos 3 y 4 — al 5 ya le falta**. Se agrega el 5 junto con el 6: es un bug preexistente que M28 destapa, y dejarlo sería construir el 6 sobre un agujero conocido.

### Orden de implementación sugerido

1. `TipoTarea.ChatLibre` + `EsDePlataforma` + **los tests de los switches** (A-01, R-A1). Nada más hasta que estén verdes.
2. `IAgentesDisponiblesQuery` y migrar los tres llamadores actuales, **sin cambio de comportamiento** (A-03b).
3. Formato 6, declaración, wrapper, `ArmarEvaluacionAsync` (el 5 y el 6) + goldens.
4. `IChatLibre`, permiso, `IniciarChatLibreAsync`, controller, menú, filtro.
5. Los dos modos de `SubagentesPermitidosAsync` + `PorTareaAsync` + `HerramientasSubagentes` (A-04).
6. Prompt del núcleo + suite de evaluación.
7. Vista de arranque + CSS + autocomplete en `site.js`.
8. La pieza 3D, última y aislada: es la única parte que se puede sacar sin que M28 deje de funcionar.

## Arquitectura M27 (2026-10-01)

Entrada: Diseño M27 cerrado. Reutiliza **PAT-029, PAT-030, PAT-032, PAT-033** — todos de este proyecto; ningún patrón nuevo.

### El problema real y cómo se resuelve

M27 son cuatro frentes técnicamente independientes que comparten una sola propiedad: **ninguno agrega un mecanismo**. Los cuatro apagan, relajan o reordenan algo que ya está. Eso define el criterio de diseño técnico: *si un frente necesita una entidad nueva, está mal planteado.* El único dato nuevo en toda la base es un vínculo (`AgenteOrganizacion → Instructivo`) y dos columnas en una tabla de propuestas que ya existe.

El riesgo arquitectónico no está en lo que se agrega: está en **lo que se afloja**. Sacar el tope de ajustes y aceptar cualquier archivo son dos relajaciones de guardas, y la pregunta en cada caso es *qué guarda queda debajo*. Las respuestas son el tope de gasto de M6 y el tope de tamaño/cuota/macros de M5, y las dos ya existen y no se tocan.

### Principio que ordena esta arquitectura

> **Ni el prompt de ningún agente ni el hash del contexto cambian.** Los pasos de un agente propio **no entran al prompt**: entran por `instructivos_listar` / `instructivo_leer`, igual que todo instructivo desde M14. Esto no es una comodidad de implementación: es lo que hace que CA-M27-10 sea cierto sin esfuerzo y que **ninguna tarea vieja cambie de hash**. Si en algún momento parece necesario decirle al prompt que un instructivo es «el suyo», la respuesta correcta es marcarlo **en el resultado de la herramienta**, nunca en el prompt.

### Decisiones técnicas M27

- **A-M27-1 — La propuesta de agente crece dos campos, no una entidad.** `PropuestaTrabajo` (M7b/M15) gana `HerramientasJson` (`varchar(1000)`, null) y `Pasos` (`text`, null), usados solo por `TipoPropuestaTrabajo.AgenteEmpresa`. Se descartó una tabla `PropuestaAgente` aparte: la propuesta ya es polimórfica por `Tipo` y seis de sus columnas ya se interpretan distinto según el tipo. Una tabla más sería una segunda forma de decir lo mismo.
- **A-M27-2 — `proponer_agente_empresa` valida las herramientas contra el base en el momento de proponer.** Una herramienta que no está en el agente base es **error de la herramienta** (el modelo recibe el motivo y vuelve a intentar), no un recorte silencioso al aplicar. Motivo: la tarjeta le muestra a la persona qué herramientas va a tener; si al aplicar se recortan, la tarjeta mintió. Es la misma invariante de PAT-030 («no puede sumar herramientas que el agente de Olvidata no tiene»), movida al punto donde se puede explicar.
- **A-M27-3 — El vínculo de los pasos va en `AgenteOrganizacion`, no en su versión.** `InstructivoId` (`int?`, FK a `Instructivos`, `ON DELETE SET NULL`). **Por qué no en `AgenteOrganizacionVersion`:** corregir un paso no es cambiar el agente. El instructivo ya versiona solo (M14), y si el vínculo viviera en la versión, editar un paso obligaría a versionar el agente —y por lo tanto a republicarlo— por un cambio que el agente ni ve en su prompt. Un vínculo por agente, el instructivo versionando por su cuenta: dos ciclos de vida separados, que es lo que son.
- **A-M27-4 — Aplicar una propuesta de agente crea las tres cosas en UNA TRANSACCIÓN y TRES guardados.** ~~en un `SaveChanges`~~ — **corregido 2026-10-01 por la auditoría de pre-implementación: la redacción original era falsa en dos puntos.** (1) `AplicarAgenteEmpresaAsync` **no abre ninguna transacción ni hace ningún `SaveChanges`**: el patrón del archivo es delegar el guardado al service de adentro, que es también el que marca la propuesta `Aplicada` (igual que `AplicarAsignacionAsync`). (2) «Un solo `SaveChanges`» era **inalcanzable, y ya lo era antes de M27**: `GuardarAsync` hace **dos** cuando el alta se publica —inserta agente y versión, y después fija `VersionPublicadaId`— y para eso ya abre su propia transacción; con el instructivo son **tres**. Y como por A-M27-5 la propuesta ahora nace publicada, ese camino de dos guardados pasa a ser el normal, no el excepcional.
  **La forma correcta:** `AplicarAgenteEmpresaAsync` abre una **transacción explícita**, crea el `Instructivo` por **`IInstructivoService`** (en singular; `IInstructivosService` no existe), guarda el agente con **`IAgenteOrganizacionService.GuardarAsync`** (también singular), setea `InstructivoId` y commitea; y `GuardarAsync` **no abre una transacción anidada** —EF tira `InvalidOperationException`—, sino que reusa la ambiente cuando ya hay una (`CurrentTransaction is null ? Begin : null`). Una transacción, tres guardados. Si falla cualquier parte, `MarcarFallidaAsync` con `ChangeTracker.Clear()` y no queda ni agente ni instructivo huérfano.
- **A-M27-5 — El agente nace publicado, con la acción que corresponde a su alcance.** `AccionGuardarAgente` ya tiene las tres: `Herramientas = []` y `GuardarBorrador` pasan a ser `Herramientas = <las propuestas>` y **`PublicarParaEmpresa`** si la visibilidad es `Organizacion`, **`GuardarYUsar`** si es `Personal`. No se agrega ninguna acción ni se saltea ninguna verificación: `PublicarParaEmpresa` ya publica sin revisión y ya avisa a los Directores, y el rol se chequea donde siempre. **Corrección de la auditoría (2026-10-01):** «donde siempre» **no es** `GuardarAsync` —que pide solo `EsMiembro`, y está documentado a propósito: cualquier miembro publica para la empresa y se avisa—. El gate real de una propuesta de alcance `Organizacion` es **`PuedeResolverTipo`** en `PropuestaTrabajoService`. La invariante se cumple, pero por otro lugar: **no agregar un chequeo nuevo en `GuardarAsync` creyendo que falta.** Esto es literalmente **un cambio de dos valores** en un DTO, y es lo que convierte «nace usable» de una promesa en un hecho.
- **A-M27-6 — Los pasos del agente se marcan en el resultado de `instructivos_listar`, no en el prompt.** Cuando el instructivo listado es el del agente que corre, su fila lleva una marca («los pasos de este agente»). Es un cambio en el **texto que devuelve la herramienta**, que no participa del hash del contexto ni del prompt de sistema. Ningún agente del núcleo se vuelve a publicar por esto.
- **A-M27-7 — El tope de ajustes se vuelve opcional con `0 = sin tope`, y el default es `0`.** `MaxSeguimientosPorTarea` **no se borra** del `MotorAgentesOptions`: un tope de emergencia que se puede volver a poner desde configuración, sin desplegar, vale más que un campo menos.
  **TRAMPA, encontrada por la auditoría (2026-10-01):** poner el valor en 0 **invierte** el comportamiento en vez de liberarlo. Las dos guardas comparan con `>=`, así que `CantidadSeguimientos >= 0` es **siempre verdadero** y toda tarea con cero seguimientos queda «al límite»: ningún ajuste entraría. El 0 hay que tratarlo como **caso especial explícito**, no solo cambiarlo de default. Y hay una segunda trampa, de despliegue: **producción tiene `MaxSeguimientosPorTarea: 20` escrito explícito en su `appsettings.Production.json`, que no está en git y gana sobre el default de C#** — cambiar el default no cambia nada en el servidor. `MotivoNoPuedeSeguir.Limite` se mantiene en el enum (es un contrato de DTO y de vistas) y deja de ser alcanzable con el default. `AjustesRestantes` / `MaxSeguimientos` quedan en el DTO devolviendo `null` cuando no hay tope, y la vista no los muestra (D-M27-11).
- **A-M27-8 — Cuando el pedido no entra, se escalona en tres pasos antes de rendirse, y nunca termina en `Fallida`.** Es la decisión técnica más delicada de M27 y vive en `ProcesadorTareas`, en el mismo punto donde hoy está `EsConversacionDemasiadoLarga`:

  | # | Qué se hace | Qué cuesta |
  |---|---|---|
  | 1 | Reintentar **con la limpieza de resultados de herramienta activada para ese pedido** (`BetaClearToolUses20250919Edit`, que hoy está apagada por configuración). El servidor borra los resultados viejos de herramienta, que en una conciliación son el 90 % del contexto. | Una llamada. El agente pierde el **detalle** de lo que leyó hace varias vueltas, no el hilo. |
  | 2 | Si sigue sin entrar: **poda local** — los resultados de herramienta más viejos se reemplazan por un testigo (*«resultado omitido por tamaño»*) y se reintenta. | Una llamada. Lo mismo, pero decidido por nosotros y auditable en la base. |
  | 3 | Si sigue sin entrar: la tarea queda **terminada y seguible** (`PuedeSeguir`), con el aviso de D-M27-9. | Nada. La persona resume y sigue. |

  **Lo que nunca pasa:** que la tarea quede `Fallida` y haya que empezar de cero. Y los tres pasos se anotan como pasos de la conversación, así que «Ver pasos» los muestra (D-M27-10) y el costo de cada reintento entra en `EventoUso` como cualquier llamada.
- **A-M27-9 — Antes de implementar A-M27-8 hay que verificar que la compactación funcione de verdad.** La bandera está pedida y la edición se manda (`ProveedorModeloAnthropic.BetasDe` + `GestionDeContexto`), pero la compactación **solo sirve si los bloques que devuelve la API se guardan y se reenvían** en la reconstrucción del contexto: el servidor los usa para reemplazar la historia compactada en el pedido siguiente. Si `ReconstruirContextoAsync` los pierde, se paga la compactación en cada vuelta y no se aplica nunca — y eso explicaría por sí solo el corte de la demo. **Verificación concreta:** en una conversación larga, `usage` tiene que mostrar la compactación aplicada, y los bloques tienen que estar en la base. Si no están, **esto es el defecto y se arregla primero**: los tres pasos de A-M27-8 son el respaldo, no el arreglo.

  > Verificado contra la documentación de la API (2026-10-01): `claude-sonnet-5` **ya tiene 1M de ventana**, nativo, sin beta. No hay ninguna bandera de contexto largo que agregar. La compactación es `compact-2026-01-12` y se dispara a los **150.000 tokens**; la limpieza de resultados es `context-management-2025-06-27`, que es otra beta y se declara aparte (el código ya lo hace bien). Tope de pedido: 32 MB.
- **A-M27-16 — El presupuesto de tarea es lo que frenó al cliente, y es lo primero que se arregla.** Lectura de la tarea 17 en producción (ver análisis, «H2 resuelto»): todos los pasos cerraron con `end_turn`, el contexto nunca pasó de ~60.000 tokens contra 1M de ventana, y el agente **anunció que seguía en otra tarea**. El único mecanismo del sistema que le dice al modelo que se administre y cierre es `Anthropic:TaskBudgetTokens = 64000`, que viaja como `output_config.task_budget.Total` (`ConstruirSalida`, con `Remaining` sin setear — correcto) y hace que el servidor le inyecte una cuenta regresiva. Con 56-60k de entrada por llamada contra un total de 64.000, el modelo cerró prolijo: **la función andando como está documentada, con el número mal puesto.**

  **Qué se hace, en este orden:**
  1. **Medir, no suponer.** Confirmar con una corrida controlada sobre la tarea 17 que subiendo el presupuesto el agente **hace el cruce** en vez de diferirlo. Es una sola corrida y cuesta centavos; es lo que separa «encontramos la causa» de «creemos que la encontramos».
  2. **Dimensionarlo contra el trabajo, no contra el contexto.** `TaskBudgetTokens` sube a un valor que le alcance a una conciliación real: **orden de 400.000**, con el mínimo de la API en 20.000. ~~o se pone en 0~~ **— el camino del 0 queda DESCARTADO por la auditoría (2026-10-01):** la bandera beta `task-budgets-2026-03-13` solo se declara si el valor es ≥ 20.000, pero el `output_config` sigue existiendo cada vez que hay esfuerzo o esquema de salida, y el SDK serializa `task_budget: null` apenas existe el `output_config`; un campo sin su bandera es «Extra inputs are not permitted». O sea: **el 0 puede 400-ear todos los pedidos de los modelos grandes**, y contradice de palabra una **regla permanente del `CLAUDE.md` del repo**, que ya tenía el 400 explicado. Si alguna vez se quisiera el 0, hay que declarar la bandera incondicionalmente y agregar un test que verifique que viaja.
  **Y el número vive en tres lugares, no en uno:** el default de C# en `AgentesSettings`, la clave en `appsettings.json`, y el `appsettings.Production.json` del servidor —que **no está en git y gana**—. Producción hoy no escribe `TaskBudgetTokens`, así que cae al de `appsettings.json`; pero sí escribe `MaxSeguimientosPorTarea`. El arreglo principal de M27 es un número de configuración: **decir dónde se cambia es parte del arreglo.**
  3. **El presupuesto deja de ser global.** Un agente de consulta y un agente que concilia dos planillas no tienen el mismo trabajo por delante. El valor pasa a poder venir del agente, con el de configuración como respaldo. Sin esto, dimensionarlo para la conciliación le regala presupuesto a todo lo demás.
  4. **Una regla de prompt, no de código:** una tarea de trabajo **no se cierra pidiendo abrir otra tarea para lo mismo**. Si falta algo, se dice qué falta y se espera ahí. Va en las instrucciones compartidas de `nucleo/`, no en el prompt de un agente — y por lo tanto **pasa por evaluación antes de publicarse**, como cualquier cambio de prompt.

  **Lo que esto le hace al resto del frente H2:** A-M27-7 (tope de ajustes) y A-M27-8 (escalonamiento ante el 400 por tamaño) **siguen en alcance y bajan de prioridad**: son los frenos que van a aparecer cuando una conciliación llegue de verdad a veinte vueltas, pero **ninguno de los dos actuó acá**. A-M27-9 (verificar que los bloques de compactación se reenvíen) **se mantiene como verificación** y pierde su carácter de sospechoso: con un contexto que no pasó de 60k, la compactación —que se dispara a los 150k— nunca tuvo ocasión de correr, así que la tarea 17 **no prueba ni desmiente** que funcione. Hay que verificarlo igual, con una conversación que sí llegue.

- **A-M27-10 — `.xls` binario con NPOI 2.8.1, en un extractor propio que comparte la salida con el de `.xlsx`.** `ExtractorPlanillaBinaria` (HSSF de NPOI) produce **exactamente el mismo formato de partes** que `ExtractorPlanilla` (ClosedXML): hoja, encabezado repetido, bloques de `FilasPorParte`, valores formateados es-AR. Comparten `AcumuladorPartes` y los topes (`MaxColumnas`, `MaxCaracteresLegibles`, `SegundosMaxExtraccion`). **Por qué no reemplazar ClosedXML por NPOI para los dos:** ClosedXML está probado contra 18 planillas reales de clientes en M5/M19 y lee `.xlsx` mejor; cambiarlo sería una regresión buscada en lo que ya funciona. Dos extractores, una salida.
- **A-M27-11 — El orden de detección de un `.xls` no cambia: tabla HTML primero, binario después.** Es PA-35 y es obligatorio: invertirlo rompe a los sistemas contables argentinos que exportan HTML con nombre `.xls`. El binario se reconoce por la firma OLE2 (`D0 CF 11 E0 A1 B1 1A E1`). Un `.xls` que no es ni una cosa ni la otra queda `NoSePudoLeer` con motivo, **no rechazado**.
- **A-M27-12 — `.doc` binario se intenta y se admite que se lee mal.** NPOI tiene HWPF pero su extracción de texto es pobre y el formato tiene variantes que no cubre. **Decisión: se intenta, y lo que no sale queda `NoSePudoLeer` con el motivo y la salida («guardalo como .docx»).** No se promete en ningún texto de la interfaz que un `.doc` se lea. Prometer OCR de formatos viejos es la forma más rápida de que D-M27-13 se vuelva mentira.
- **A-M27-13 — «Todo entra» se implementa invirtiendo el default de `ValidarExtension`, no sacándola.** Una extensión desconocida deja de devolver `MensajesDocumentos.NoPermitido` y pasa a `TipoDocumento.Otro` (nuevo valor `8` del enum — se persiste como `int` sin restricción, **no hace falta migración para esto**), estado `NoSePudoLeer` con motivo. **Lo que NO cambia, y es la mitad de la decisión:** `ConMacros` sigue rechazando, el tamaño por archivo sigue rechazando, la cuota sigue rechazando, la bomba de descompresión sigue rechazando y el tope de extracción sigue cortando. La relajación es **solo** del reconocimiento de formato.
- **A-M27-14 — Un archivo de tipo desconocido nunca se sirve con su propio tipo.** `application/octet-stream` + `Content-Disposition: attachment`, siempre. Es la misma regla que PA-35 escribió para el HTML (`TipoContenidoHtml = "text/plain"`) y por el mismo motivo: aceptar cualquier formato convierte el almacén en un lugar donde un tercero sube bytes arbitrarios, y lo único que lo mantiene inofensivo es que el navegador nunca los interprete. **Esta es la línea que no se puede aflojar al aflojar el resto.**
- **A-M27-15 — El menú es solo `_Layout.cshtml`.** Reordenar los `ov-sidebar-section` y mover los bloques `@if (Permisos.VeEnMenu(...))` tal cual están. `OpcionMenu`, `Permisos` y cualquier service: **sin tocar**. Si el reordenamiento necesita cambiar una condición, está mal hecho.

### Auditoría de pre-implementación (2026-10-01)

Antes de escribir código se corrió una auditoría **de solo lectura** de las ocho zonas de M27 contra el código real (60 agentes, refutación adversarial de los hallazgos graves y un crítico de completitud). Los ocho frentes volvieron **«sí, con cambios»**: ninguna decisión se cae, y **doce zonas que M27 toca de verdad no estaban nombradas en el mapa por capa**. Las de abajo no son mejoras: son lo que faltaba para que los frentes 3 y 4 funcionen, y están en orden de qué rompe primero.

- **A-M27-17 — El rechazo por formato también vive en el navegador, y es el que de verdad corta.** `wwwroot/js/documentos.js` valida la extensión contra una lista y aborta la subida **antes de que el archivo salga de la máquina**, con el texto de formatos escrito a mano y duplicado. El mapa por capa decía solo *«`_ZonaSubida.cshtml`: `accept` deja de filtrar»* y **no nombraba ningún `.js` en ningún frente**: implementado al pie de la letra, el `.xls` del cliente **seguiría sin llegar al servidor** y el frente 3 entero no haría nada. Se saca la validación de extensión (el tope de tamaño se queda) y se borra el texto duplicado. **El mapa Web de M27 le debía una línea a `wwwroot/js`, y el frente 6 también la necesita (`site.js`).**
  **Los cuatro lugares, verificados uno por uno (2026-10-01), y la buena noticia:** el filtro del cliente tiene **una sola fuente**, `DocumentosTextos.AcceptExtensiones`, que alimenta el `accept` de `_ZonaSubida.cshtml` **y** el `data-extensiones` de `_ModalDocumentos.cshtml`, y de ahí llega a `documentos.js`. Así que el frente se cierra en **dos** cambios, no en cuatro: que `AcceptExtensiones` deje de ser una lista blanca, y que `validar()` en `documentos.js` deje de comparar extensiones (manteniendo macros, HEIC, vacío y tamaño, que sí tienen que seguir cortando del lado del cliente porque son avisos útiles antes de subir 20 MB). Lo que **no** se puede dejar pasar es el mensaje duro escrito a mano en el `.js`: enumera los formatos permitidos y hay que borrarlo, o va a seguir diciéndole al cliente que su `.xls` no se puede subir.
  **Y un fixture de test que hay que cambiar:** `LectorDocumentosTests` tiene un `XlsBinario` que son **24 bytes de firma OLE2, no un libro**. NPOI va a tirar sobre él — lo cual está bien y es el camino correcto (`NoSePudoLeer` con motivo), pero el test que hoy afirma «se rechaza» pasa a afirmar «entra y queda no legible», y hace falta **un `.xls` binario real como fixture** para probar CA-M27-06. Hoy no hay ninguno: todos los archivos de prueba se generan en código.
- **A-M27-18 — `TipoDocumento.Otro` necesita rama explícita en cada `switch` con descarte, y uno de ellos es un agujero, no un detalle cosmético.** El valor nuevo entra sin tocar código en varios lugares y en todos miente: `NombreDocumentoHelper.TextoTipo` termina en `_ => "Imagen"` y `DocumentosTextos.IconoTipo` en el ícono de imagen, así que **un `.exe` se llamaría «Imagen»** para la persona y para el modelo, con una opción «Imagen» duplicada en los combos y una búsqueda libre que trae los desconocidos cuando se busca «imagen». **Y el peor: el descarte del `switch` de extracción manda `Otro` a `ExtractorTexto`, así que un `.exe` no queda `NoSePudoLeer` sino `Legible`, con basura decodificada en Windows-1252 y guardada como partes de texto que el agente va a leer.** Eso contradice de frente a A-M27-13. Rama explícita en todos, y revisar el filtro por texto de `DocumentoCarteraService` antes de agregar el valor al enum.
- **A-M27-19 — `Otro = 8` no alcanza para leer un `.xls` binario: no hay nada que pueda despachar al extractor nuevo.** La extracción se elige **por `TipoDocumento` solamente**, y `Otro` no identifica un `.xls`. Sin resolver esto, `ExtractorPlanillaBinaria` queda escrito y nunca se ejecuta. Hay que distinguirlo: o un valor propio para la planilla vieja, o llevar la **extensión detectada** hasta el punto de despacho. Es el eslabón que faltaba del frente 3.
- **A-M27-20 — La promesa «queda `NoSePudoLeer` con el motivo» no llega a la pantalla.** `DocumentosTextos.AvisoNoLegible` usa el motivo **solo si el tipo es `Pdf`**; en cualquier otro caso devuelve la frase fija *«es un PDF escaneado o no tiene texto»*. O sea: un `.doc` o un `.xls` binario que no se pudo leer **le diría a la persona que es un PDF escaneado**. El texto de `NoSePudoLeer`/`NoLegible` lo decide **una sola función** que recibe siempre el motivo. `TooltipLectura` ya lo hace bien y es el contraejemplo a copiar.
- **A-M27-21 — `Documento.Extension` es `varchar(10)` y el cálculo no la acota.** Una extensión desconocida larga no se rechaza en la puerta: **se cae al guardar**, con el mensaje genérico *«No se pudo guardar el documento. Probá de nuevo.»* — exactamente la pared que A-M27-13 viene a sacar, movida un paso más adentro. Y **EF InMemory no valida largos, así que los tests nuevos pasarían igual**: hay que acotar la extensión al guardarla y probarlo contra MySQL o con un test de largo explícito.
- **A-M27-22 — El camino de arranque de M26 es el ÚNICO enlace del sistema a `/Agentes/Crear`.** `CaminoDeArranqueService` arma el paso *agente-propio* con `url "/Agentes/Crear"` y botón **«Crear mi agente»**. El frente 1 convierte esa pantalla en solo-edición, así que el tablero quedaría con un botón que promete crear y lleva a editar o a conversar. **Decisión de producto pendiente:** o el paso apunta a `/Analista` —y entonces se fusiona con el paso *contá qué venís a resolver*, que ya apunta ahí— o `Crear` sigue siendo la pantalla de ese paso. No se implementa hasta decidirlo.
- **A-M27-23 — El ejecutor de programaciones lee el contrato de estados que A-M27-8 cambia.** `EjecutorProgramaciones` corta el aviso si el estado no es `Completada` ni `Fallida`, y elige el texto por `== Completada` («terminó» / «falló»). Las dos salidas del paso 3 son malas para una tarea programada: con `Completada` el responsable recibe *«la tarea programada terminó correctamente»* sobre una conversación que no entró, y con un estado nuevo **no recibe nada**. Hay que definir el estado final del paso 3 **y el aviso que le corresponde a una programación** antes de tocar `ProcesadorTareas`.
- **A-M27-24 — `proponer_agente_empresa` la ofrecen TRES prompts, y ningún caso de evaluación la cubre.** No es solo el analista: también el asistente que reparte trabajo y el configurador de reglas. A-M27-2 le agrega un campo y una validación, así que **hay que reescribir los tres** —dejar uno distinto de los otros dos es peor que no tocar ninguno— y sumar casos a sus conjuntos. Y la regla permanente manda: **ningún prompt se publica sin evaluación aprobada**, y las suites de plataforma corren con Opus 5, así que esto **cuesta plata y hay que presupuestarlo como trabajo, no como ajuste de texto**. El mapa por capa de M27 no nombraba un solo archivo de `nucleo/`.
- **A-M27-25 — El portal del cliente (M18) es la puerta con menos filtros, y la usa un tercero de afuera de la organización.** Su subida es un `<input type="file">` **sin `accept` y sin el JS de documentos**, y el service delega a `SubirComoClienteAsync`. A-M27-13 abre el almacén a bytes arbitrarios justo por ahí, y RT-M27-04 hablaba solo de **cómo se sirve**. Por eso: **el `octet-stream` + `attachment` se pone donde se guarda el `TipoContenido`, no en cada controller** —si hay dos caminos de descarga y se arregla uno, el agujero queda abierto— y el frente 3 tiene que nombrar explícitamente el portal del cliente.
- **A-M27-26 — Hay una tercera superficie de navegación que el frente 4 no miraba: `Primeros pasos`.** `Views/PrimerosPasos/Index.cshtml` reúne los mismos accesos con su propio orden y sus propias condiciones (~25 chequeos `Permisos.VeEnMenu`). *«El menú es solo `_Layout.cshtml`»* es cierto **del menú** y falso **de los accesos**: si el orden «de menos a más» solo se aplica al menú, las dos superficies quedan contando historias distintas. Hay que decidir si se replica o si se declara explícitamente que no.
- **A-M27-27 — El menú ya muestra mal dos opciones hoy, y `Miembros` no tiene `VeEnMenu`.** Copiar los ítems tal como están **congela el bug**. `Miembros` es el único ítem del bloque de Director cuya condición efectiva es solo `Permisos.EsDirector`, heredada del `@if` externo; y hay **un anidamiento con cuatro ítems** cuya visibilidad **cambia si se los mueve de sección**. Antes de reordenar: inventario literal de los ítems con su condición **efectiva**, y los dos que ya están mal se arreglan en el mismo pase o se dejan anotados a propósito.
- **A-M27-28 — M27 vuelve falsa documentación del repo que el mapa no nombraba.** `docs/manual-de-uso.md` lista los formatos aceptados y explica que el `.xls` de SOS Contador *«por dentro es una tabla HTML»* y que no hay que convertirlo; el diseño del portal del cliente repite la lista. Con A-M27-10 y A-M27-13 los tres textos describen un sistema que no existe, **y el manual de uso es lo que lee el cliente.** Los dos documentos entran al entregable del frente 3.
- **A-M27-29 — El analista no puede proponer el agente Y su tarea programada en la misma vuelta.** La herramienta que resuelve un agente por su código `o-<id>` no lo encuentra, porque el agente **recién existe cuando la persona aplica la tarjeta**. El frente 1 vende «el agente queda andando», pero la programación de ese agente es necesariamente una segunda vuelta. **Decisión pendiente:** o se acepta y el prompt lo dice, o una propuesta de programación tiene que poder referenciar la propuesta de agente de la misma conversación.
- **A-M27-30 — Cuatro correcciones al escalonamiento de A-M27-8, que estaba mal ubicado y mal planteado.** (a) **No puede vivir donde decía:** `EsConversacionDemasiadoLarga` se evalúa en el registro del error, que corre en un **scope nuevo creado por el worker después de que la excepción salió del bucle** —ahí no hay conversación ni prompt de sistema—; va **adentro del bucle**. (b) Los `Intentos` se cuentan **por reclamo de la tarea, no por llamada al modelo**: por el camino actual, cada reintento consume un intento y la tarea se muere antes de llegar al paso 3. (c) **«Nunca `Fallida`» está mal planteado: una tarea `Fallida` ya es terminada y seguible hoy, y hay un test que lo prueba.** Falta un **mensaje**, no un estado — y ver A-M27-23 por lo que pasa si el paso 3 deja `Completada`. (d) Un valor nuevo de `TipoPasoTarea` **cae en el `default:` de la reconstrucción de la conversación y se trata como mensaje del usuario**: si el contenido no es un array de bloques revienta y mata la tarea, y si lo es, el testigo entra al pedido como un turno de la persona. Nada de anotar pasos informativos nuevos sin resolver esto.
- **A-M27-31 — Dos supuestos del frente 6 que no se cumplen, y un riesgo de maqueta.** No existe **ningún** autogrow reusable (lo único que hay es inline en la vista y cuenta **saltos de línea**, no renglones visuales) ni **ningún** token `--ov-*` de alto o `max-height`, así que «sistémico y sin literales» obliga a **escribir** las dos cosas. Además: el textarea tiene `resize: vertical`, que pelea con un JS que escriba `style.height`; el compositor está en `position: sticky; bottom: 1rem`, y **un sticky más alto que su scrollport deja de pegarse** —el estado expandido a 390 px lo despega, así que el tope de alto se ata al viewport y no a un número de renglones—; y el compositor **se re-renderiza del servidor y se reemplaza por `innerHTML`**, así que «la elección de expandido no se pierde» exige reponer el estado después de cada re-render. Por último, **D-M27-17 nombró mal a los culpables**: los avisos de «parece una regla / parece un instructivo» y el bloque de adjuntos en conversación **no están en `Tareas/Detalle`**; lo que ocupa alto fijo abajo es el texto de ayuda de la casilla de búsqueda web (~25 px) y los adjuntos del compositor, que son **otra implementación, paralela y duplicada**.

**Lo que la auditoría verificó que NO rompe, para no gastar tiempo ahí:** el MCP congelado no se ve afectado (ningún `.cs` de ese proyecto menciona `TipoDocumento`, `AgenteOrganizacion` ni `Instructivo`); el tope de ajustes y los subagentes no interactúan; los seeds y la demo de `nucleo/demo` no se tocan. **Dos huecos que quedan abiertos a propósito:** el reordenamiento del menú **no tiene ninguna prueba automática posible** —se verifica en navegador real, como ya pedía la estrategia de pruebas— y la versión de NPOI hay que confirmarla con un `dotnet restore` en la máquina de build antes de prometerla (existe en nuget.org, verificado el 2026-10-01).

**Qué dice esto del método, que es lo que vale para el próximo módulo.** De 24 hallazgos graves refutados por dos escépticos cada uno, sobrevivieron 3; pero el crítico de completitud —el agente que solo pregunta *qué no se miró*— encontró **doce zonas enteras que ninguno de los ocho auditores tenía asignadas**, y dos de ellas (`documentos.js` y el despacho del extractor) **anulaban un frente completo**. La lección: en un módulo que nace de una demo, el riesgo no está en las decisiones que se escribieron mal, está en **los archivos que no se nombraron**. Auditar lo escrito encuentra matices; preguntar qué falta encuentra los agujeros.

### Modelo de datos M27

Una migración, `UnificacionAgentesM27`:

```
PropuestasTrabajo
  + HerramientasJson   varchar(1000) NULL   -- nombres de herramienta, JSON; solo AgenteEmpresa
  + Pasos              text          NULL   -- los pasos propuestos; solo AgenteEmpresa

AgentesOrganizacion
  + InstructivoId      int           NULL   -- FK → Instructivos(Id), ON DELETE SET NULL
  + IX_AgentesOrganizacion_InstructivoId
```

Nada más. En particular **no** hay tabla nueva, **no** hay columna en `AgenteOrganizacionVersion` (A-M27-3), **no** hay migración por el valor de enum nuevo (A-M27-13) y **no** hay cambio en `TareasAgente` (el escalonamiento de A-M27-8 se anota en los pasos, que ya existen).

### Mapa por capa

**Domain**
- `AgenteOrganizacion`: `InstructivoId` + navegación `Instructivo`.
- `PropuestaTrabajo`: `HerramientasJson`, `Pasos`.
- `TipoDocumento.Otro = 8`.
- Sin lógica nueva: ninguna de las cuatro cosas es una invariante de dominio.

**Application**
- `MotorAgentesOptions.MaxSeguimientosPorTarea` → `0 = sin tope` documentado; default `0`.
- `AgentesSettings`: nada. La configuración de compactación ya está y es correcta.
- `TareaDetalleDto`: `AjustesRestantes` / `MaxSeguimientos` pasan a `int?`.
- `NombresHerramientasAnalista` / `DescripcionesHerramientas`: el esquema de `proponer_agente_empresa` gana `herramientas` y `pasos`.
- `MensajesDocumentos`: `FormatoViejo` deja de ser error de rechazo y pasa a motivo con salida; mensaje nuevo para formato desconocido; `TiposArchivoDocumento.TextoPermitidos` reescrito (D-M27-13).
- `IExtractorPlanillaBinaria` no hace falta: el extractor es `static`, como los otros.

**Infrastructure**
- `HerramientasAnalista.HerramientaProponerAgenteEmpresa`: valida herramientas contra el base (A-M27-2), guarda los dos campos nuevos.
- `PropuestaTrabajoService.AplicarAgenteEmpresaAsync`: instructivo + agente + vínculo en un `SaveChanges`; acción por alcance (A-M27-4, A-M27-5).
- `ProcesadorTareas`: el escalonamiento de A-M27-8 donde hoy está `MarcarFinAsync(..., Fallida, MensajeConversacionLarga)`.
- `ProveedorModeloAnthropic`: poder activar la limpieza de resultados **por pedido** (hoy es solo por configuración global). Es un parámetro en `SolicitudModelo`, no un cambio de settings.
- `ReconstruirContextoAsync`: verificación de A-M27-9 y corrección si los bloques de compactación se pierden.
- `ServicioTareas`: el tope de ajustes deja de cortar; `MensajeLimite` queda sin uso en el camino normal.
- `ValidadorContenidoArchivo`: A-M27-11, A-M27-13.
- `Extractores/ExtractorPlanillaBinaria.cs`: nuevo (NPOI/HSSF).
- `HerramientasInstructivos`: la marca de A-M27-6 en el listado.
- `OlvidataAgentes.Infrastructure.csproj`: `NPOI` 2.8.1 (verificado disponible en nuget.org, 2026-10-01).

**Web**
- `Views/Agentes/Index.cshtml`, `_FichaCrearVersion.cshtml`, `Detalle.cshtml`, `Crear.cshtml` (→ edición).
- `Views/Analista/*`: chip del agente base; tarjeta de cuatro bloques con pasos editables.
- `Views/Tareas/Detalle.cshtml`: sin contador; mensajes de corte.
- `Views/Documentos/_ZonaSubida.cshtml`: `accept` deja de filtrar (`accept` se saca o se deja en `*`).
- `Views/Shared/_Layout.cshtml`: A-M27-15. **`_LayoutCliente.cshtml` no se toca.**
- `AgentesController`: `Crear` acepta solo el camino de edición; la ruta vieja sin agente redirige al analista.

### Permisos M27

**Ningún cambio.** Se dice explícitamente porque es la tentación obvia de este módulo: unificar la creación detrás del analista podría parecer una razón para mover el chequeo de rol a la conversación. **No.** El rol se sigue chequeando **al aplicar**, según el alcance de cada propuesta (regla del proyecto, 2026-09-25): conversar no otorga nada, y un Empleado puede proponer un agente para toda la empresa y no poder aplicarlo. Lo mismo con el menú: las condiciones `Permisos.VeEnMenu` se mueven de sección sin cambiar.

### Estrategia de pruebas

- **Unitarias nuevas:** validación de herramientas contra el base (dentro y fuera del conjunto); aplicar propuesta → agente publicado + instructivo + vínculo en una sola operación; rollback si falla una parte; `.xls` binario → mismas partes que su `.xlsx` equivalente; `.xls` que es tabla HTML → `TablaHtml` (**regresión de PA-35**); extensión desconocida → `Otro` + `NoSePudoLeer`; macros/tamaño/cuota/zip-bomb → siguen rechazando; tope de ajustes en `0` → `PuedeSeguir` después de 30 ajustes; error de tamaño → escalonamiento y **nunca** `Fallida`.
- **Integración:** una tarea con muchas vueltas que dispara los tres pasos de A-M27-8 (con proveedor simulado que 400ea por tamaño las dos primeras veces).
- **Verificación obligatoria contra producción, antes y después:** la **tarea 17** de `agentes.olvidata.com.ar`. **Antes:** leer su `Estado`, `Error`, `CantidadSeguimientos`, tokens y el log del momento, para saber cuál de los cuatro frenos cortó (RF-M27-10) — sin eso, tres de los cuatro arreglos son a ciegas. **Después:** que esa misma conversación siga, con ocho o más idas y vueltas, hasta un resultado. **La prueba final la hace Joaquín sobre esa tarea** (pedido suyo, 2026-10-01).
- **Navegador real,** 1440 y 390 px, tema claro y oscuro (instrucción 38): catálogo, ficha, tarjeta del analista con los pasos plegados, detalle de tarea largo y el menú con las cuatro secciones.

### Riesgos técnicos M27

- **RT-M27-01 — El escalonamiento de A-M27-8 puede gastar tres llamadas caras en una conversación que no va a entrar igual.** Cada reintento es un pedido enorme y se paga. **Mitigación:** el escalonamiento corre **dentro** del control de gasto de M6 (es una llamada como cualquier otra); si el tope corta en el paso 2, corta, y el mensaje es el de gasto. No se agrega ningún camino que esquive M6.
- **RT-M27-02 — Podar resultados de herramienta cambia lo que el agente tiene presente.** Es el riesgo R-M27-02 del análisis visto desde el código: la limpieza **borra**, la compactación **resume**. **Mitigación:** siempre en ese orden (compactar antes de limpiar, limpiar antes de podar a mano), y cada paso anotado en la conversación.
- **RT-M27-03 — NPOI es una dependencia nueva que parsea un binario de un tercero.** Superficie de ataque sobre un archivo que sube alguien de afuera. **Mitigación:** corre dentro del `SegundosMaxExtraccion` que ya existe, con los topes de filas y columnas que ya existen, y **cualquier** excepción del parser es `NoSePudoLeer`, nunca una tarea caída ni un 500. Agrega ~2 MB al publicado, que en SmarterASP no es un problema.
- **RT-M27-04 — Aceptar cualquier formato abre el almacén a bytes arbitrarios.** **Mitigación: A-M27-14 y nada más que A-M27-14** — `octet-stream` + `attachment`, siempre, sin excepción y con test. Es la única barrera que queda entre «todo entra» y servir contenido activo de un tercero desde nuestro dominio.
- **RT-M27-05 — `AplicarAgenteEmpresaAsync` pasa a hacer tres cosas en una transacción, con dos services adentro.** Es la clase de método donde aparecen los agentes huérfanos. **Mitigación:** el `SaveChanges` único que ya usa el método; `ChangeTracker.Clear()` en el camino de falla, como ya hace `AplicarTareaAgenteAsync`; y un test que falla a propósito en el segundo paso y verifica que no quedó nada.
- **RT-M27-06 — Publicar directo lo que propuso un modelo.** Hasta hoy un agente propuesto nacía en borrador y una persona lo terminaba en el formulario; eso era, de hecho, una revisión. A-M27-5 la saca. **Mitigación:** la revisión no desaparece, **se adelanta**: la tarjeta muestra instrucciones, pasos, herramientas y alcance **antes** del botón (D-M27-4, D-M27-6), y aplicar es un acto humano explícito. Lo que se saca es tener que revisar **dos veces, en dos pantallas**, que es lo que nadie hacía.
- **RT-M27-07 — El prompt del analista pasa a ser camino crítico** (R-M27-03). **Mitigación arquitectónica:** `Agentes/Crear` sigue existiendo y sigue alcanzable por URL —deja de estar enlazado, no de funcionar—, así que una falla del analista degrada a «hay que saber la URL», no a «no se pueden crear agentes».
- **RT-M27-08 — SE MATERIALIZÓ (2026-10-01).** El corte no fue ninguno de los cuatro sospechosos: fue el presupuesto de tarea (A-M27-16). El análisis y esta arquitectura se corrigieron **antes** de escribir código, que es para lo que estaba el riesgo. **Lo que queda como aprendizaje de método:** tres de los cuatro arreglos del frente H2 estaban diseñados contra una causa que no existía, y la única razón por la que no se implementaron igual es que RF-M27-10 era el primer requisito y no una verificación al final. En un módulo que nace de una demo —donde el síntoma lo reporta quien mira la pantalla, no quien lee el log— **leer el estado real antes de diseñar el arreglo no es prolijidad: es la diferencia entre arreglar y no arreglar.**

---

# M20 — Coprocesador aritmético · M21 — Ojos, segunda mitad (PDF escaneado)

Estado: **Arquitectura cerrada**. Entrada: análisis M20/M21 y el diseño de `2-disenador-funcional.md`.
**Sin entidades nuevas y sin migración** en ninguno de los dos.

**Escaneo de reutilización.** No hay componente equivalente en el historial del estudio (ni evaluador de expresiones ni
visión sobre documentos). Se reutiliza **código propio de este repo**: el camino entero de M16 (ojos) para M21 y la
heurística de número de M19 para M20 — que **se muda a Application y queda compartida**, no duplicada.

## Mapa de componentes — M20

| Componente | Capa | Responsabilidad |
|---|---|---|
| `Helpers/NumeroEscrito.cs` (nuevo) | Application | «1.234,50», «1234.50», «$ 1.234,50», «(500)» → `decimal`. **Mudado desde `GeneradorEntregables.TryNumero` (M19)**, que pasa a llamarlo y borra su copia |
| `Helpers/EvaluadorExpresiones.cs` (nuevo) | Application | Tokeniza y evalúa con descenso recursivo: `+ - * / ( )`, unario, `%` sufijo, funciones `SUMA PROMEDIO MIN MAX CONTAR ABS REDONDEAR`, separador de argumentos `;`. Todo en `decimal`. Puro: sin base, sin sesión, sin `eval` |
| `Settings/CalculoOptions.cs` (nuevo) | Application | Topes (RF-M20-07) |
| `DTOs/CalculoDtos.cs` (nuevo) | Application | `CuentaCalculada` + `MensajesCalculo` (al modelo y a la persona, separados) |
| `Motor/NombresHerramientasCalculo.cs` (nuevo) | Application | `calcular` |
| `Services/Calculo/HerramientaCalcular.cs` (nuevo) | Infrastructure | Parsea la entrada del modelo, resuelve cuenta por cuenta, encadena por nombre, devuelve el resultado. **No toca la base ni llama a `SaveChanges`** |
| `Services/Calculo/ResumenHerramientasCalculo.cs` (nuevo) | Infrastructure | El paso en palabras, armado **desde la entrada** (como M19) |
| `ResolvedorHerramientas` | Infrastructure | `FamiliaHerramienta.Calculo` con `CondicionHerramienta.TodaTareaDeTrabajo` |
| `DescripcionesHerramientas` | Application | Rótulo llano (el test de cobertura CP-AA-10 lo exige) |

**Contrato del evaluador** (es el corazón, y tiene que poder probarse solo):

```
EvaluadorExpresiones.Evaluar(string expresion, IReadOnlyDictionary<string, decimal> nombres, CalculoOptions topes)
    → ResultadoExpresion(bool Ok, decimal Valor, string? Error)
```

Nunca lanza por la entrada: todo error es `Ok = false` con el motivo en castellano. Las tres excepciones que sí se
capturan adentro son `DivideByZeroException`, `OverflowException` y la profundidad de paréntesis (guarda propia, no
`StackOverflow`: eso no se captura y tiraría el proceso del worker).

**Por qué en Application y no en Infrastructure:** no depende de nada (ni base, ni HTTP, ni disco). Ahí se puede probar
con una tabla de casos y ahí lo puede usar cualquier otro módulo más adelante.

## Mapa de componentes — M21

| Componente | Capa | Cambio |
|---|---|---|
| `Extractores/ExtractorPdf.cs` | Infrastructure | Si no se extrajo **ningún** texto: `SeMira` cuando las páginas entran en `MaxPaginasPdfParaMirar`; si no, `NoLegible` con el motivo exacto. El conteo de páginas ya lo hace hoy |
| `Documentos/ImagenesParaModelo.cs` | Infrastructure | Acepta `TipoDocumento.Pdf` en estado `SeMira` con su propio tope de bytes (`MaxBytesPdfParaMirar`). Las guardas de tenant/cliente/vigencia **no se tocan** |
| `Motor/ProveedorModeloAnthropic.cs` | Infrastructure | Rama nueva: `TipoContenido == "application/pdf"` → bloque de **documento** (base64) en vez de bloque de imagen. El tipo exacto del SDK lo confirma el compilador (la familia `Beta*` que ya usa para imágenes) |
| `Motor/ProcesadorTareas.RehidratarImagenesAsync` | Infrastructure | El tope se calcula **por tipo**: últimas N imágenes y últimos M PDF, contados por separado |
| `Motor/MensajesOjos.cs` | Application | `Rotulo` con páginas para PDF; `YaMirado`/`NoSePudoMirar` en masculino para archivo |
| `Motor/IMotorAgentes.cs` | Application | `ImagenParaMirar` y `BloqueImagenDocumento` ganan **`bool EsPdf = false`** |
| Textos de estado | Application/Web | `TiposArchivoDocumento.TextoLectura`, `DocumentosTextos.TooltipLectura`, `MensajesDocumentos.SubidoSeMira`, `HerramientasDocumentos.LecturaParaAgente`, `Views/Documentos/Ver.cshtml` |
| `Settings/DocumentosOptions.cs` | Application | `MaxPaginasPdfParaMirar` (20), `MaxMbPdfParaMirar` (10), `MaxPdfsEnConversacion` (2) |

**La decisión técnica que hay que entender antes de tocar el código:** el bloque persistido **no se renombra ni cambia
de discriminador**. `BloqueImagenDocumento` y `ImagenParaMirar` se extienden con un campo opcional `EsPdf` con valor por
defecto `false`, así las filas que ya están en producción desde M16 se siguen deserializando igual (el JSON viejo no
tiene el campo y toma el default). Es lo que permite distinguir tipos en el rehidratado sin una consulta más a la base y
sin una migración de datos. El nombre queda «histórico»: el concepto documentado es *archivos que el agente mira*.

## Flujo de datos (M21, punta a punta)

1. **Subida:** `DocumentoCarteraService.SubirInternoAsync` → `LectorDocumentos.ExtraerAsync` → `ExtractorPdf` decide `SeMira` / `NoLegible` y el motivo → estado y motivo guardados (columnas que ya existen).
2. **La tarea:** el modelo pide `documento_leer` → `HerramientaDocumentoLeer` devuelve `ResultadoHerramienta.ConImagenes([...])` con `EsPdf = true`.
3. **Persistencia del paso:** en `PasosTarea` queda `BloqueImagenDocumento(id, nombre, esPdf)`; en `EjecucionHerramienta.ImagenesJson`, lo mismo. **Cero bytes.**
4. **Próxima llamada:** `RehidratarImagenesAsync` toma los últimos 2 PDF y las últimas 8 imágenes, lee cada archivo del disco por `ImagenesParaModelo` y arma el bloque; lo que queda afuera va como texto.
5. **Proveedor:** bloque de documento para `application/pdf`, bloque de imagen para el resto.

## Cambios de datos y migraciones

**Ninguno, en los dos módulos.** Se agregan claves de configuración (`Calculo`, y tres topes en `Documentos`), que no
son esquema. El snapshot de EF no se toca — si el implementador genera una migración, algo está mal.

## Riesgos técnicos

- **R-T-01 (M20).** Un parser hecho a mano es el lugar clásico de los bugs silenciosos: precedencia, unario, paréntesis anidados. Se cubre con una **tabla de casos** y con los casos que en `double` dan distinto. Sin tabla, este módulo no se aprueba.
- **R-T-02 (M20).** `decimal` desborda con multiplicaciones grandes (28-29 dígitos). `OverflowException` capturada y contada como error de esa cuenta.
- **R-T-03 (M20).** La mudanza de `TryNumero` a Application toca código de M19 **que está en producción**: los tests de M19 tienen que quedar en verde **sin tocarlos**.
- **R-T-04 (M21).** El tope por tipo en el rehidratado es la parte más fácil de romper y la más cara: un PDF de 20 páginas que viaja en las seis vueltas de una conversación son seis veces el costo. Test dedicado.
- **R-T-05 (M21).** El tipo del SDK para el bloque de documento no está verificado en este repo (el proveedor solo armó imágenes hasta hoy). Se resuelve con el compilador, no adivinando el nombre; si el SDK no lo expone en la familia beta que usa el motor, **frenar y avisar**: no inventar un `HttpClient` propio.
- **R-T-06 (los dos).** Los **5 goldens de contexto** tienen que quedar **byte por byte iguales**: ninguna de las dos features toca el prompt de sistema. Si un golden cambia, hay una fuga de diseño.

## Estrategia de pruebas funcionales

- **M20, unitarias del evaluador** (sin base): tabla de expresión → resultado, incluyendo `1234,50 * 21%`, precedencia, unario, `SUMA` de 40 importes, `REDONDEAR(x; 0)`, división por cero, función inventada, paréntesis sin cerrar, 21 niveles de paréntesis, desborde.
- **M20, de herramienta** (con entorno): encadenado por nombre, una cuenta falla y las otras siguen, tope de cuentas, se ofrece sin cliente, **no** se ofrece en `ConsultaCliente`, el paso se lee en palabras sin el nombre de la función.
- **M21:** PDF sin texto → `SeMira` con páginas; PDF con texto → `Legible` (no se cambió el camino barato); escaneado por encima del tope → `NoLegible` con motivo; el agente lo pide y al modelo llega el bloque de documento con el base64 y en la base solo la referencia; PDF de otro cliente/organización → no se puede mirar; tope por conversación con PDFs e imágenes mezclados.
- **Regresión:** los 5 goldens, los tests de M16 y los de M19, todos sin tocar.

# M16 — Tablero de actividad al iniciar sesión

Estado: **aprobada por Joaquín 2026-09-19**. Entrada: `1-analista-funcional.md` M16 (RF-M16-01..06) y `2-disenador-funcional.md` M16 (D-M16-1..7). **Sin entidades nuevas y sin migración: es todo lectura sobre lo que ya existe.**

- **Application:** `ITableroService` + `TableroDtos` (los tres bloques y el grafo) + `TableroOptions` (tope de nodos, tope de filas por bloque, segundos de sondeo de respaldo).
- **Infrastructure:** `Services/Tablero/TableroService.cs`. Consultas **acotadas por código** al tenant de la sesión y a la visibilidad de M2 (`IPermisosOrganizacion`): el Empleado solo sus tareas. Todo con tope de filas; nada de traer y recortar en memoria. El grafo se arma desde las mismas consultas, no con una segunda vuelta a la base.
- **Tiempo real:** se reusa la infraestructura de M1/M3b. `TareasHub` gana un **grupo por organización** además del grupo por tarea, y `NotificadorTareasSignalR` emite al grupo cuando una tarea cambia de estado o avanza un paso. **Sin hub nuevo.** Si el socket no conecta, sondeo cada 15 s contra un endpoint JSON del propio controller.
- **Web:** `HomeController.Index` decide: miembro → tablero; staff → la portada actual (no se le inventa un tablero vacío). **Render del lado del servidor primero**: los tres bloques llegan en el HTML y el JavaScript solo los actualiza. Sin JS la pantalla funciona.
- **El grafo:** librería del CDN, y hay que **sumarla a la lista blanca del CSP** en `SecurityHeadersMiddleware` — el portal hoy solo admite jsdelivr y datatables, así que si la librería no está ahí no carga y **falla en silencio**. Elegir una que ya esté permitida o extender la lista de forma explícita.
- **Nada de esto toca el motor ni el armado del contexto**: los 5 goldens quedan intactos, y no se agrega una sola llamada al modelo.

Riesgos técnicos: **RT-M16-01** el tablero se carga en cada entrada y se refresca — consultas con tope e índices ya existentes (`(TenantId, Estado)` en tareas); si pesa, se cachea por organización unos segundos, no por usuario. **RT-M16-02** el CSP silencioso. **RT-M16-03** el grupo de SignalR por organización es el lugar más fácil para filtrar datos de otra: el grupo se arma **desde la sesión del servidor**, nunca desde un parámetro del cliente.

# M14 — Instructivos, búsqueda web, espacio del cliente y control de gasto

Estado: **aprobada por Joaquín 2026-09-17** (Discovery, Análisis y Diseño con gate; presupuesto omitido). Entrada: `1-analista-funcional.md` M14 (RF-M14-01..33) y `2-disenador-funcional.md` M14 (D-M14-1..8, P-M14-01..10). **Una entrega, una migración: `InstructivosM14`.**

## Principio que ordena la arquitectura

**Nada de M14 entra al prompt de sistema.** Los instructivos se consultan con herramientas y la búsqueda web es una herramienta del proveedor: las dos viajan en la **lista de herramientas de la solicitud**, que no forma parte del contexto ni del hash. Consecuencia verificable y no negociable: **los 4 goldens de contexto quedan byte a byte idénticos** con y sin instructivos y con y sin búsqueda habilitada. Es el mismo criterio que sostuvieron M5, M6, M10, M11 y M12.

## Domain

- **`Instructivo`** (`ITenantOwned`, `SoftDestroyable`): `Titulo`, `ParaQueSirve`, `Pasos`, `Visibilidad`, `AutorId`, `Activa`, `VersionActual`, `VersionToken`. **Reusa `VisibilidadAgente`** de M4 (`SoloYo` / `TodaLaEmpresa`) en vez de crear un enum gemelo: es la misma decisión de producto y el usuario ya la conoce con esas palabras.
- **`InstructivoVersion`**: `InstructivoId`, `Numero`, y la copia de `Titulo`/`ParaQueSirve`/`Pasos`/`Visibilidad`, más `AutorId` y `CreadoAt`. Mismo patrón que `ReglaVersion`.
- **`TareaAgente.PermiteBusquedaWeb`** (bool, default `false`). Se fija al crear la tarea y **se congela**: cambiar la casilla después no altera una tarea en curso, igual que la autonomía de M12 (DI-M12-6).
- **`EjecucionProgramada.VistoAt`** / **`VistoPorId`** (nullables). **Decisión consciente:** el "visto" es del registro, no por persona. Los resultados son del responsable de la programación; modelar una tabla de vistos por usuario agrega una tabla y una consulta para un caso que hoy no existe. Queda anotado como deuda si algún día varias personas comparten la bandeja.
- **`EventoUso.Busquedas`** (int, default 0). El costo de las búsquedas se suma a `CostoUsd` del mismo evento, para que **no haya dos verdades sobre cuánto costó una llamada** y para que el límite de gasto de M6 lo tome sin tocar una línea.
- Sin enums nuevos. `CanalUso` no se toca: una búsqueda no es un canal, es parte de una tarea.

## Datos y migración `InstructivosM14`

- Tablas `Instructivos` e `InstructivosVersiones`; dos columnas en `TareasAgente`, dos en `EjecucionesProgramadas`, una en `EventosUso`.
- **Unicidad de título entre los vigentes de la organización**, con el patrón ya probado del proyecto: columna generada `TituloVigente` = `CASE WHEN DeletedAt IS NULL THEN Titulo END` + índice único `(TenantId, TituloVigente)`. **`MySql.EntityFrameworkCore` ignora `stored: true`** y genera una columna VIRTUAL, que MySQL no acepta como base de un índice: la migración la reescribe a mano con `migrationBuilder.Sql("ALTER TABLE ... GENERATED ALWAYS AS (...) STORED NULL;")` **antes** de crear el índice. Es la cuarta vez que aparece; está en el catálogo de patrones.
- La comparación previa del service usa `NombreDocumentoHelper.ClaveComparacion`, que replica en C# la colación `utf8mb4_0900_ai_ci`, para que **la validación funcional y el índice vean lo mismo**.
- Índices de lectura: `(TenantId, Activa, Visibilidad)` para el listado del agente; `(TenantId, CreadaAt)` en `TareasAgente` para el informe; `(ProgramacionTareaId, VistoAt)` para la bandeja de resultados.

## Application

- `InstructivosDtos` + `MensajesInstructivos`; `IInstructivoService`; `InstructivosOptions` (largo de pasos, largo de "para qué sirve", cantidad por organización, topes por llamada de las herramientas).
- `BusquedaWebOptions`: habilitada, **máximo de búsquedas por tarea**, y el precio por búsqueda. **El precio se configura, no se hardcodea** (regla del proyecto: verificar precios antes de facturar). Sin precio configurado, la búsqueda **no se ofrece**: mismo criterio fail-closed que M8 con las corridas reales.
- `IInformeAutomatizacion` + su DTO: agrupación por `(AgenteId, ClienteCarteraId, HashPedido)`, donde `HashPedido` es SHA-256 del pedido **normalizado** (recortado, sin tildes, minúsculas, espacios colapsados). Las tareas de programación son idénticas por construcción, así que caen juntas solas. Se calcula **al vuelo** con tope de período y de filas: no se persiste nada, porque un informe que se guarda envejece y miente.

## Infrastructure

- `Services/Instructivos/InstructivoService.cs` — ABM con versionado, token de concurrencia y validación de unicidad previa.
- `Services/Instructivos/HerramientasInstructivos.cs` — `instructivos_listar` (título, para qué sirve, sin los pasos) y `instructivo_leer` (los pasos, con tope de caracteres). **Solo lectura, solo en tareas de trabajo**, acotadas por código al tenant de la tarea y a lo que el **autor de la tarea** puede ver (los de la empresa + los personales suyos). Resultado rotulado como información, nunca instrucciones. Espeja `HerramientasConocimiento` de M10, incluida su regla de que "no está disponible" es la única respuesta para todo lo que no corresponde.
- `Services/Motor/ProcesadorTareas.cs` — suma la herramienta de búsqueda del proveedor **solo si** `PermiteBusquedaWeb`, hay presupuesto y hay precio configurado; cuenta las búsquedas del turno contra el tope; registra `Busquedas` y su costo en `EventoUso`. **La verificación de límite de gasto de M6 se hace antes de cada llamada, como ya se hace**: no se agrega una segunda compuerta.
- `Services/Motor/ProveedorModeloSimulado.cs` — guion de búsqueda web para que QA lo verifique **sin costo**, con resultados fijos y una fuente citada.
- `Services/Motor/ResumenPasos.cs` — dos resumidores nuevos (instructivos y búsqueda), encadenados como los demás, con su par de textos modelo/persona. **Ningún camino nuevo puede mostrar nombres de herramienta ni JSON**: hay test que lo barre.
- `Services/Uso/` — agregaciones del dashboard (conteo de llamadas = filas de `EventoUso`) y del informe.

## Web

- `InstructivosController` + vistas (`Index`, `Form`, `Detalle`, `_Desambiguador`), policy `RequireMiembro`; las de la empresa las administra el Director (`IPermisosOrganizacion` suma `PuedeGestionarInstructivosDeOrganizacion`).
- `CarteraController.Espacio` + vista — **solo lectura**, reusa los servicios de reglas, documentos, tareas y programaciones ya existentes. Sin endpoints nuevos de escritura.
- `ProgramacionesController.Resultados` + `MarcarVisto`.
- `UsoController` — cards de totales y apertura; `UsoController.Automatizar` — el informe. Ambos `RequireAdministracion`.
- Ajustes: `Agentes/Ejecutar` y el cuadro de seguimiento (casilla), `Tareas/Detalle` (pasos nuevos con fuentes externas `rel="noopener noreferrer"`), `Reglas` (tipo `Procedimiento` fuera del combo + aviso con **Convertirlo en instructivo**), `Cartera/Detalle` (acceso al espacio), `_Layout` (ítem **Instructivos** y contador de resultados sin ver).
- **El texto externo se escapa siempre.** Lo que vuelve de internet es de un tercero no confiable: mismo tratamiento que el cuerpo de un conector (`TextoExternoSeguro`).

## Riesgos técnicos

**RT-M14-01 — el tipo y la versión de la herramienta de búsqueda del SDK no se asumen**: hay que verificarlos contra la documentación oficial del SDK de Anthropic antes de escribir la llamada, y lo mismo el precio por búsqueda. Un `type` inventado da 400 en la primera corrida real. **RT-M14-02 — los goldens**: 4 tests existentes más uno nuevo que prueba que habilitar búsqueda e instructivos deja el hash idéntico; si alguno se mueve, se para. **RT-M14-03 — la columna generada STORED** (cuarta aparición del mismo problema del proveedor MySQL). **RT-M14-04 — el informe con volumen**: tope de período y de filas, y el índice `(TenantId, CreadaAt)`; si el `GROUP BY` sobre el hash pesa, se persiste el hash como columna calculada en el alta, no se agrega caché. **RT-M14-05 — inyección desde internet**: el rótulo y el escapado son la mitigación disponible, **no una garantía**; se documenta como riesgo aceptado. **RT-M14-06 — doble concepto**: si `Procedimiento` sigue ofreciéndose en algún camino, vuelve la confusión; hay test que verifica que no aparece en el combo.

# M12 — Tareas programadas y autonomía gradual por rol

Estado: **aprobado sin gate por autorización de Joaquín 2026-09-14**. Entrada: `1-analista-funcional.md` M12 (RF-M12-01..17) y `2-disenador-funcional.md` M12 (D-M12-1..12, P-M12-01..03). Una entrega, una migración: `ProgramacionesM12`.

## El problema real y cómo se resuelve

Repetir algo cada X tiempo parece trivial hasta que se lo pone en **hosting compartido**: el proceso de IIS se recicla cuando quiere, el sitio se duerme si nadie entra, y mañana puede haber dos instancias. Las tres cosas rompen el enfoque ingenuo ("guardá la última corrida y compará"): entre leer y escribir hay una ventana, y crear una tarea no es instantáneo.

La solución es un patrón que ya está probado en el repo en dos variantes —el lease del motor (M1) y el índice único de `AvisoGasto` (M6)— combinadas: **reservar la ocurrencia con un índice único, y recién después hacer el trabajo caro.** Queda documentado como **PAT-045**.

## Decisiones técnicas M12

- **RT-M12-01 Dos fases con estado intermedio.** Fase 1 (`ReservarAsync`): inserta `EjecucionProgramada{Resultado = Reservada, Ocurrencia}` y adelanta `ProximaEjecucionAt` **en el mismo `SaveChanges`**, protegido por el índice único `(ProgramacionTareaId, Ocurrencia)` y por `VersionToken`. Fase 2 (`EjecutarUnaAsync`): crea la tarea y cierra la vuelta. Si el proceso muere entre las dos, la vuelta queda `Reservada`; el barrido la retoma pasados `MinutosReintentoReservada` (10) y la termina **sin volver a reservar esa ocurrencia**. Alternativa descartada: una transacción larga que abarque las dos fases — con EF InMemory en los tests no existe, y en MySQL sostener una transacción mientras se arma el contexto y se calcula el hash es tener la fila bloqueada por segundos.
- **RT-M12-02 `ProximaEjecucionAt` se recalcula desde AHORA, no desde la ocurrencia vencida.** Es una línea de código y es la diferencia entre "el sitio volvió y creó una tarea" y "el sitio volvió y creó siete, cada una con su costo". Consecuencia asumida: las vueltas perdidas **se pierden**, no se recuperan. Es lo correcto para este producto: una tarea de IA vieja cuesta plata y casi nunca sirve.
- **RT-M12-03 El calendario es un helper puro** (`CalendarioProgramacion`), sin base y sin estado: recibe frecuencia, día, minutos y un instante, devuelve el próximo instante UTC. Todo el cálculo se hace en **hora argentina** (`ArgentinaTime`) y se convierte al final. Se testea solo, sin levantar nada. Día 31 en un mes más corto → último día del mes (nunca se saltea un mes). Siempre **estrictamente después** del instante que recibe.
- **RT-M12-04 La hora se guarda como `MinutosDelDia` (int 0..1439), no como `TimeOnly`.** El proveedor MySQL ya nos costó un conversor para `DateOnly` (RT-M7-13); un int no tiene sorpresas de mapeo, se indexa, se compara y se muestra con un helper. El significado está en el nombre: minutos desde la medianoche **argentina**.
- **RT-M12-05 La vuelta reusa `IPreparadorTareaTrabajo` tal cual.** Límite de gasto (M6), suscripción, agente publicado, cliente, instantánea de reglas y hash: todo eso ya vive ahí desde M7a y **no se toca**. Una vuelta programada y un botón del portal arman exactamente la misma tarea. Es lo que garantiza CA-M12-14 (los 4 goldens de hash intactos).
- **RT-M12-06 La vuelta corre con los permisos del responsable**, resueltos desde la base con `IResolvedorSesion.ResolverUsuarioAsync` (el mismo recurso que M4b usa para las conversaciones de plataforma en el worker). Si dejó la empresa o lo bloquearon, la vuelta se frena con motivo. No hay "usuario del sistema" que ejecute tareas: siempre hay una persona responsable.
- **RT-M12-07 La autonomía se resuelve en el motor, quitando herramientas, no en la herramienta.** En `ProcesadorTareas`, después de armar la lista de permitidas y antes de `Definiciones(...)`: si la tarea vino de una programación sin autonomía, se sacan todas las que tienen `RequiereAprobacion`. Alternativa descartada: auto-aprobar o dejar el pedido pendiente en silencio. Quitar la herramienta es **fail-closed de verdad**: el agente no puede pedir lo que no tiene, y no hay ninguna rama nueva en el circuito de aprobaciones de M6 que pueda tener un agujero. Con la autonomía encendida, no se toca nada: el circuito de M6 funciona como siempre y **nunca aprueba solo**.
- **RT-M12-08 `TareaAgente.AutonomiaConAprobacion` congela el permiso al crear la tarea.** Si se leyera de la programación al ejecutar, editarla a mitad de una vuelta cambiaría lo que esa vuelta puede hacer. Dos columnas nuevas en `TareasAgente` (`ProgramacionTareaId`, `AutonomiaConAprobacion`) y nada más.
- **RT-M12-09 El costo se calcula, nunca se guarda** (lección DI-M11-6): `SUM(PasosTarea.CostoUsd)` sobre las tareas con esa `ProgramacionTareaId`, con el período argentino de M6. Escribir una columna de la programación dentro del commit del motor acoplaría su `VersionToken` al guardado de la tarea y un Director editándola a mitad de vuelta la haría fallar por conflicto sin motivo real.
- **RT-M12-10 El barrido vive en `MotorAgentesWorker`, con su propio ritmo (60 s) y su propio interruptor.** Es el quinto barrido del ciclo; no crea tareas en ejecución ni toca `MaxTareasSimultaneas`: solo las **encola**, y el reclamo de siempre las levanta. Un error del barrido queda en el log y no rompe el ciclo.
- **RT-M12-11 `VersionToken` se incrementa en la fase 1, nunca en la 2.** Si la fase 2 lo tocara, una edición desde la pantalla a mitad de vuelta haría fallar el cierre sin motivo real (mismo gotcha que PAT-043). El cierre igual va con `WHERE VersionToken = ...`: si alguien editó, la vuelta queda `Reservada` y la retoma el barrido.

## Modelo de datos M12

- **`ProgramacionTarea`** (`ITenantOwned` + `SoftDestroyable`): `Nombre`, `AgenteArtefactoId` **o** `AgenteOrganizacionId`, `ClienteCarteraId?`, `Pedido` (text), `Frecuencia`, `DiaSemana?`, `DiaMes?`, `MinutosDelDia`, `ResponsableUsuarioId`, `Estado`, `MotivoFin?`, `FinEl?` (date), `MaxEjecuciones?`, `EjecucionesHechas`, `FallasSeguidas`, `PuedeAccionesConAprobacion`, `ProximaEjecucionAt?`, `UltimaOcurrenciaAt?`, `PeriodoAvisoCosto?`, `VersionToken`. Índices: `(Estado, ProximaEjecucionAt)` **sin TenantId adelante** (el barrido mira todas las organizaciones), `(TenantId, Estado)` y `(TenantId, ResponsableUsuarioId)` para el listado.
- **`EjecucionProgramada`** (`ITenantOwned`, inmutable salvo el cierre): `Ocurrencia`, `Resultado`, `TareaAgenteId?`, `Motivo?`, `CreadoAt`, `ResueltaAt?`. **Índice único `(ProgramacionTareaId, Ocurrencia)`** — es todo el mecanismo. Más `(Resultado, CreadoAt)` para el barrido de recuperación.
- **Sin columnas generadas.** A diferencia de M2, M4 y M11, acá la unicidad que importa es sobre columnas reales, así que **no hace falta** el ajuste manual a `STORED` que el proveedor MySQL obliga cuando ignora `stored: true`.
- Auditoría: la programación **se audita** (es configuración que alguien cambia); cada vuelta queda **fuera del audit trail** (ya es su propio registro inmutable), igual que los pasos de una tarea y las llamadas de M11.

## Permisos M12

Dos permisos nuevos en `IPermisosOrganizacion`, derivados del contexto y sin base: `PuedeProgramarTareas` (todo miembro activo, nunca staff) y `PuedeProgramarParaOtros` (Director). El segundo habilita **tres** cosas distintas y conviene tenerlas juntas: ver y manejar las de toda la empresa, poner a otra persona como responsable y encender la autonomía. Lección OLV-010 aplicada: `VisibleAsync` habilita **lectura**; cada acción pasa por `PuedeAccionar`, que vuelve a mirar rol y organización.

## Riesgos técnicos M12

1. **Sin AlwaysRunning (PA-07), el barrido no corre con el sitio dormido.** No lo resuelve el código. Mitigado a medias con el ping de M9 a `/health/vivo`. Documentado en el formulario para que el usuario no se sorprenda.
2. **La precisión es la del barrido**, 60 s más el tiempo hasta que el reclamo levante la tarea. No sirve para nada que necesite puntualidad al minuto.
3. **La ocurrencia se consume aunque la tarea no se cree.** Es a propósito (evita el bucle infinito de una programación rota), pero significa que un problema de un día se lleva la vuelta de ese día.
4. **El único `(ProgramacionTareaId, Ocurrencia)` guarda contra la doble creación, no contra el doble trabajo dentro de la tarea**: eso ya lo cubre `EjecucionHerramienta` por `tool_use_id` desde M1.

---

# M11 — Conectores con credenciales por organización

Estado: **aprobada sin gate por autorización de Joaquín 2026-09-14**. Entrada: análisis M11 (RF-M11-01..17) y diseño
M11 (D-M11-1..12). **Una migración: `ConectoresM11`** (dos tablas nuevas, ninguna tabla existente modificada).
Se apoya en M1–M10 (338 tests verdes).

### M11-0. Escaneo de reutilizacion
| Fuente | Qué se tomó | Grado |
|---|---|---|
| M1 `Tenant.ApiKeyProtegida` + `ProcesadorTareas.PropositoApiKeyTenant` | Data Protection con propósito propio, descifrado solo al ejecutar, propiedad excluida del audit trail | Literal (mismo mecanismo, otro propósito) |
| M6 `IHerramientaConAprobacion` (PAT-034) | Nivel, descripción en palabras armada con la entrada, pedido inmutable por `tool_use_id`, vencimiento y barrido | Literal (extensión: la decisión pasa a ser **por llamada**) |
| M5 / M6 / M10 en `ProcesadorTareas` | "Herramientas agregadas a la lista de la solicitud sin tocar el prompt de sistema" + golden de hash | Literal (patrón del repo) |
| M2 `AreaConfiguration` / `ClienteCarteraConfiguration` | Unicidad entre vigentes con columna generada STORED + índice único, y el ajuste manual de la migración | Literal |
| M10 `HerramientasConocimiento.Resumir` y M7a `ResumenHerramientasPlataforma.Pedido` | Rótulos llanos de "Ver pasos" encadenados en `ServicioTareas` | Literal (extensión) |
| M4b `HerramientasConfigurador` (`Texto`, `Entero`, `Json` de M5) | Lectura de la entrada del modelo y serialización escapada del resultado | Literal (reuso de código, mismo assembly) |
| Escaneo `docs/*/definiciones/5-implementador.md` del estudio | Ningún otro proyecto tiene "conectores con credenciales por organización". Lo más cercano es la integración con ARCA/AFIP (instrucción `34`), que es **un** sistema externo con su propio protocolo, no un mecanismo genérico; de ahí se tomó el criterio de "credenciales del cliente, nunca del estudio" y "toda llamada externa queda registrada" | Práctica, no código |

### Decisiones técnicas

- **RT-M11-01 — Dos tablas, ninguna existente modificada.** `ConexionesConector` (`ITenantOwned` + `SoftDestroyable`:
  es dato del cliente y la baja tiene que conservar el historial) y `LlamadasConector` (`ITenantOwned`, inmutable, sin
  baja lógica, **fuera del audit trail**: ya es su propio registro). FK **Restrict** en las dos direcciones: el
  historial de una conexión dada de baja no se puede borrar en cascada sin querer.
- **RT-M11-02 — El "último uso" NO se guarda en la conexión: se calcula del historial.** Escribirlo en cada llamada
  metería la fila de la conexión (y su `VersionToken`) en el **mismo commit que la tarea**, y un Director editando la
  conexión a mitad de una tarea la haría fallar por conflicto de concurrencia sin ningún motivo real. `RegistrarLlamada`
  solo agrega una fila; el listado saca el último uso y el uso de 30 días con un `GROUP BY` sobre el historial.
- **RT-M11-03 — Aprobación por llamada (PAT-044).** `IHerramientaAprobacionPorLlamada : IHerramientaConAprobacion`
  agrega `RequiereAprobacionAsync(contexto, entrada, ct)`. `RequiereAprobacion` sigue devolviendo **true**: si el motor
  no consulta, o la consulta falla, la acción pasa por aprobación igual (**fail-closed**). `ProcesadorTareas` la
  resuelve en un solo lugar (`NecesitaAprobacionAsync`) que usan los tres puntos donde antes se leía la propiedad. El
  **nivel** sigue siendo estático (`Director`): hacerlo variable habría agregado otra superficie al motor a cambio de
  poco, y lo que el Director necesita —dejar pasar las consultas— ya se resuelve por conexión.
- **RT-M11-04 — El prompt de sistema no se toca.** `ProcesadorTareas` agrega `conexiones_listar` más la herramienta de
  cada **tipo** con conexiones activas del tenant (una consulta `Distinct` por tarea). Los 4 formatos y sus hashes
  quedan intactos, con golden propio ("el hash de una tarea es el mismo con y sin conexiones").
- **RT-M11-05 — Las guardas se resuelven contra la base, nunca contra la entrada del modelo.** La conexión se busca por
  `(TenantId de la tarea, Codigo, Activa, Alcance)` y el rol del autor se re-verifica en cada llamada con
  `IResolvedorSesion.ResolverUsuarioAsync` (mismo criterio que M4b). "No existe", "está inactiva", "es de otra empresa"
  y "no la podés usar" responden **lo mismo**: no se le cuenta al modelo qué conexiones hay en el sistema.
- **RT-M11-06 — Protección contra SSRF en dos momentos y un solo lugar.** `IGuardiaDestinoHttp` (singleton):
  `RevisarUrl` (esquema https, sin userinfo, host en la lista blanca de la **conexión**, IP literal revisada) antes de
  armar el pedido, y `RevisarIp` **al conectar**, sobre cada dirección que devolvió el DNS. Lo segundo se engancha en el
  `ConnectCallback` del `SocketsHttpHandler`, que después conecta **a esas mismas direcciones**: es lo que cierra el DNS
  rebinding (entre "el nombre está permitido" y "el socket se abre" nadie puede cambiar a dónde apunta).
  `AllowAutoRedirect = false`: cada salto lo valida el conector contra la misma lista blanca, si no alcanzaría con que
  el destino conteste un 302 hacia donde quiera. Se rechazan loopback, `0.0.0.0`, 10/8, 172.16/12, 192.168/16,
  169.254/16 (con mensaje propio para `169.254.169.254`, la metadata de las nubes), 100.64/10, 192.0.0/24, 198.18/15,
  multicast y sus equivalentes IPv6 (`::1`, `fe80::/10`, `fc00::/7`, site-local, multicast), más las IPv4 mapeadas.
- **RT-M11-07 — `Conectores:PermitirDestinosPrivados` es solo para las pruebas automatizadas.** Apaga la revisión de IP
  y habilita http contra loopback, para poder probar el conector contra un servidor local sin salir a internet.
  `ValidacionArranque` **corta el arranque** fuera de Development si queda en true, igual que `Licencias:GenerarClaveSiFalta`.
- **RT-M11-08 — Unicidad entre vigentes y el ajuste manual de la migración.** `(TenantId, CodigoVigente)` y
  `(TenantId, NombreVigente)` únicos, con columnas generadas. Confirmada la lección de M2/M4: el proveedor MySQL
  **ignora `stored: true`** y las crearía VIRTUAL, así que se agregan a mano con SQL `STORED` antes de sus índices.
- **RT-M11-09 — Topes de plataforma en configuración.** Sección `Conectores` de appsettings: una conexión puede pedir
  menos que el tope, nunca más (tiempo de espera, KB de respuesta, llamadas por tarea, dominios permitidos,
  redirecciones). Lo que se lee de afuera entra al contexto del agente y se paga como tokens.
- **RT-M11-10 — Ningún error del sistema externo sale como excepción.** `ConectorHttpGenerico` atrapa
  `HttpRequestException`, `IOException`, `UriFormatException` y el vencimiento del tiempo, y devuelve un
  `ResultadoConectorDto` con su motivo. La lectura del cuerpo es **acotada** (se copia hasta el tope y se marca si
  había más), así una respuesta enorme no llena la memoria ni el contexto.
- **RT-M11-11 — Una herramienta por tipo de conector.** `HerramientaConector` toma su nombre, su esquema y su
  descripción del `IConectorTipo`; se registra una instancia por tipo. Un conector nuevo = una implementación de
  `IConectorTipo` + su registro en DI: ni el motor, ni las aprobaciones, ni las pantallas cambian.

# M10 — Base de conocimiento por rubro

Estado: **aprobada sin gate por autorización de Joaquín 2026-09-14**. Entrada: análisis M10 (RF-M10-01..13) y diseño
M10 (D-M10-1..10). **Una migración: `ConocimientoRubroM10`** (una tabla nueva, ninguna tabla existente modificada).
Se apoya en M1–M9 (319 tests verdes).

### M10-0. Escaneo de reutilizacion
| Fuente | Qué se tomó | Grado |
|---|---|---|
| M5 `HerramientasDocumentos` (PAT-033): clase base con guardas, `PatronLike` con escape "!", recorte en memoria con `CompareOptions.IgnoreCase \| IgnoreNonSpace`, serializador JSON escapado, `Resumir` para "Ver pasos" | Estructura completa de las 3 herramientas y del resumen | Literal (adaptado al rubro) |
| M5 `DocumentoCarteraParte` | Tabla hija sin baja lógica ni navegación de vuelta, `mediumtext`, único `(padre, Numero)`, FK Restrict | Literal |
| Núcleo `ImportadorRubro.ProcesarAsync` | La sección `conocimiento:` es una llamada más al mismo método, con el mismo hash y el mismo "sin cambios no crea versión" | Literal (extensión) |
| M6 acciones de demostración en `ProcesadorTareas` | "Herramientas que se agregan a la lista de la solicitud sin tocar el prompt de sistema" | Literal (patrón del repo) |
| `PreparadorTareaTrabajo.SuscripcionVigenteAsync` | Criterio de suscripción vigente al rubro, idéntico | Literal |

### Decisiones técnicas

- **RT-M10-01 — `TipoArtefacto.Conocimiento = 5` y una sola tabla nueva.** El documento es `Artefacto` y su contenido
  es `ArtefactoVersion.Contenido` (de ahí salen el hash y la trazabilidad al archivo). Lo nuevo es
  `FragmentosConocimiento` (`ArtefactoVersionId`, `Numero`, `Seccion varchar(400)`, `Texto mediumtext`), único
  `(ArtefactoVersionId, Numero)` y FK **Restrict**. No es `ITenantOwned` (es núcleo IP, como los casos de M8) ni
  `SoftDestroyable` (su ciclo de vida es el de la versión, y el texto es voluminoso: como `DocumentoCarteraParte`).
  Sin navegación de vuelta a `ArtefactoVersion`: así el principal filtrado por baja lógica no dispara la advertencia
  10622 de EF, y toda lectura entra por `ArtefactoVersiones` y hereda su filtro.
- **RT-M10-02 — El troceo se hace una vez, al importar, y es una función pura.** `TroceadorConocimiento.Trocear` vive
  en Application, no toca la base y es determinística: el mismo archivo da siempre las mismas secciones (si no, cada
  reimportación cambiaría los ids y el staff no podría comparar). La ruta de encabezados se arma con una **pila con el
  nivel de cada encabezado**, no indexando por el número de nivel: un documento que arranca en `##` o que saltea un
  nivel rompía la ruta (bug encontrado contra el ejemplo de plantilla real, hoy cubierto por un test).
- **RT-M10-03 — El prompt de sistema no se toca.** `ProcesadorTareas` agrega las tres herramientas a `permitidas`
  cuando la tarea es de trabajo **y** el rubro tiene material publicado. Ni `ConstructorContexto` ni los 4 formatos ni
  sus hashes cambian: hay un test golden propio ("el hash de una tarea es el mismo con y sin material publicado")
  además de los tres goldens de formato de M4/M4b/M7b.
- **RT-M10-04 — Las guardas se resuelven contra la base, nunca contra la entrada del modelo.** La clase base saca el
  rubro de la TAREA (`TareaAgente → ArtefactoVersion → Artefacto.RubroId`), verifica que el rubro esté activo y no sea
  "plataforma", y exige suscripción vigente de ese tenant a ese rubro. El modelo no puede pedir el material de otro
  rubro: no hay ningún parámetro donde poner un rubro.
- **RT-M10-05 — Búsqueda con LIKE, por ahora.** `EF.Functions.Like(Texto, patron, "!")` como pre-filtro (trae hasta 50
  filas) y comparación exacta en memoria para armar el recorte, igual que M5. Verificado contra MySQL real:
  `utf8mb4_0900_ai_ci` hace el LIKE insensible a mayúsculas y tildes (y trata ñ = n), y `%`/`_` escapados con `!`
  quedan literales. **Un índice FULLTEXT queda como deuda consciente**: con decenas de documentos por rubro el escaneo
  es trivial, y FULLTEXT en MySQL no se lleva bien con la búsqueda por subcadena ni con palabras cortas.
- **RT-M10-06 — El conocimiento sale de los dos caminos que sirven contenido.** `ListarArtefactosPublicadosAsync`
  (catálogo de agentes del portal y del MCP) y `ObtenerPublicadoAsync` (el que baja contenido al disco del cliente por
  MCP) lo excluyen explícitamente. Es la garantía de "nunca se distribuye" del plan §9, y está cubierta por test.
- **RT-M10-07 — Sin gate de pruebas automáticas.** `IGateEvaluacion.ExigePruebas` no cambia: el conocimiento no es un
  prompt, no se ejecuta y no tiene sentido correrle casos. Sigue con evaluación manual detallada, como las
  instrucciones de rubro y las reglas sugeridas.
- **RT-M10-08 — `conocimiento:` no se admite en "plataforma".** El material es **por rubro**; en plataforma el
  importador lo ignora con advertencia, igual que `reglas_sugeridas`.
- **RT-M10-09 — Topes en configuración, no en el código.** Sección `Conocimiento` de appsettings
  (`ConocimientoOptions`). `MaxCaracteresFragmento` solo se aplica **al importar** (el troceo queda congelado en la
  versión): cambiarlo después no reescribe nada, hay que reimportar.

# M9 — Preparación de despliegue (local)

Estado: **aprobada sin gate por autorización de Joaquín 2026-09-14**. Entrada: análisis M9 (RF-M9-01..06) y diseño M9
(D-M9-1..3). **Sin migración EF**: M9 no toca el modelo de datos. Se apoya en M1–M8 (287 tests verdes).

### M9-0. Escaneo de reutilizacion
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template blankproject — `DatabaseHealthCheck`, `SmtpHealthCheck`, `MapHealthChecks` con policy | Dos chequeos más con el mismo contrato | Literal (extensión) |
| Template blankproject — `web.config` con ANCM OutOfProcess y redirect a HTTPS | Base del paquete; la publicación le inyecta el entorno | Literal |
| Template M1 — lease + `Version` + `Intentos` de `TareaAgente` y de `CorridaEvaluacion` | Recuperación de leases huérfanos usa el mismo token de concurrencia | Literal (patrón del repo) |
| Template M2 — `ResolvedorSesion` (caché 60 s, fail-closed) y `SesionOrganizacionMiddleware` | Bloqueo de la organización suspendida entra por el mismo camino que el usuario bloqueado | Literal (extensión) |
| Otros proyectos del estudio (deploys a SmarterASP con Web Deploy) | Skip-rules para lo que no se pisa y "subir sin borrar" por FTP | Literal (práctica conocida) |

### Decisiones técnicas

- **RT-M9-01 — Revisión de arranque en dos partes.** `ValidacionArranque.RevisarConfiguracion` es **pura** (la única
  lectura de disco es un `Func<string,bool>` inyectable) y `RevisarCarpetas` hace la E/S. Se puede probar la primera
  sin tocar el sistema de archivos. Dos niveles: `Aviso` (queda en el log) y `Error` (fuera de Development corta el
  arranque). Los mensajes llevan **nombre de clave, nunca valor** —hay un test que lo verifica con secretos ficticios
  sembrados en la configuración—.
- **RT-M9-02 — Dónde se logea un arranque que falla.** Con `stdoutLogEnabled="false"` y ANCM, un fallo antes de que
  Serilog lea la configuración no deja rastro (500.30 pelado). El bootstrap logger escribe además en
  `Logs/arranque-*.log` (7 días), que se lee por FTP. Alternativa descartada: activar el log de stdout de ANCM, que
  crece sin límite y no rota.
- **RT-M9-03 — Carpeta de documentos como health check.** Es el error de deploy más silencioso del sistema: la app
  arranca igual y falla recién cuando alguien sube un archivo. `DocumentosHealthCheck` escribe y borra una sonda en
  `IAlmacenDocumentos.Raiz`.
- **RT-M9-04 — Latido del worker.** El proceso puede estar vivo (IIS responde) y el worker muerto. `LatidoMotor` es un
  singleton en memoria que el ciclo del worker actualiza; el health check compara contra `max(2 min, 10 × intervalo de
  sondeo)`. Se registra **solo** en el proceso que corre el worker (`AddMotorAgentesWorker`), así el Admin y el MCP no
  reportan un motor caído que nunca tuvieron. Sin persistencia: el estado del worker no es un dato del negocio.
- **RT-M9-05 — PA-03, recuperación en vez de lease más corto.** Bajar `LeaseSegundos` **no** es opción: el lease no se
  renueva durante el turno y un turno de hasta 25 llamadas lo necesita entero. En su lugar, al arrancar, el worker
  vence los leases tomados por procesos **de la misma máquina que ya no existen** (`RecuperadorLeases` +
  `IProcesosLocales`). Reglas fail-closed: solo el prefijo de esta máquina, solo si el sistema operativo confirma que
  el PID no existe ("no sé" = no se toca), nunca el WorkerId propio, y un conflicto de concurrencia se ignora. En un
  reciclado solapado de IIS el proceso viejo sigue vivo y su trabajo se respeta. Un error acá no impide arrancar: se
  vuelve al comportamiento anterior (esperar el lease).
- **RT-M9-06 — PA-05 en dos lugares, a propósito.** El middleware solo no alcanza: cerrar la sesión sin bloquear el
  login deja al usuario en un rulo. Se corta en `ResolvedorSesion` (misma caché de 60 s, `OrganizacionSuspendida` en
  `IContextoUsuario`) **y** en el login. El staff de Olvidata no tiene organización y sigue entrando, que es lo que
  permite reactivarla. **Límite aceptado:** una tarea ya encolada de una organización suspendida sigue ejecutándose;
  bloquear el worker es un cambio de comportamiento mayor y queda anotado.
- **RT-M9-07 — Publicación portable por defecto.** El perfil publica framework-dependent: el paquete es más chico y
  no hay que rehacerlo si cambia la arquitectura del pool. Requiere el Hosting Bundle de .NET 10 en el servidor; la
  alternativa self-contained (`-r win-x86`) queda documentada como plan B.
- **RT-M9-08 — Qué no viaja en el paquete.** `appsettings.Development.json` (base local y `GenerarClaveSiFalta: true`)
  y `appsettings.Production.example.json` se excluyen explícitamente. `keys/`, `App_Data/` y `Logs/` no entran porque
  no son items de contenido del SDK Web; igual se protegen con skip-rules por si alguien los agrega.

# M4b — Agente configurador de reglas del Director

Estado: **aprobada por Joaquín el 2026-09-14** (puntos 1–7 del gate). Entrada: análisis M4b (P1–P9) y diseño M4b (D-M4b-1..9) aprobados 2026-09-14. Presupuesto: omitido.

### M4b-0. Escaneo de reutilizacion
| Fuente | Componente | Grado | Decisión |
|---|---|---|---|
| Template M1 — `IHerramientaAgente`, `RegistroHerramientas`, ejecución idempotente por `ToolUseId` en un solo commit | Herramientas | **Literal** | Las herramientas del configurador agregan propuestas al change tracker y el procesador las persiste con la ejecución. |
| Template M2 — `ResolvedorSesion`, `IContextoUsuario`, `PermisosOrganizacion` | Contexto de usuario y permisos | **Literal (extensión)** | Resolver el contexto del autor de la tarea en el worker para reutilizar permisos y `ReglaService`. |
| Template M3 — `ReglaService` (crear/editar/estado/límites/versiones/eventos), `ConstructorContexto` | Reglas y contexto | **Literal (extensión)** | Aplicar propuestas por el mismo servicio; formato de contexto propio para configuración. |
| Template M3b — conversación, `EnviarSeguimientoAsync`, `ProveedorModeloSimulado` | Conversación y QA sin costo | **Literal (extensión)** | Configuración = tarea M3b de tipo propio; simulador con guion de herramientas. |
| Template M4 — `ActivarSugerenciaAsync`, importador de núcleo | Sugerencias y prompt | **Literal** | Propuesta "activar sugerencia" y prompt del configurador en `plataforma`. |
| crm-olvidata | Function calling + ejecución por servicio de negocio | **Patrón** | Base del diseño de propuestas. |
| PAT-032 (este proyecto, diseño) | Propuestas confirmables | **Diseño nuevo** | Notas de arquitectura agregadas al catálogo. |

### M4b-1. Alcance técnico resumido
Tipo de tarea "configuración de reglas" con contexto propio (plataforma + configurador, sin reglas de la empresa); contexto de usuario resuelto en el worker; herramientas de lectura y propuesta acotadas por permisos del autor (re-verificados en cada ejecución); entidad de propuesta con estados y token; aplicación por `ReglaService` con origen y verificación de cambios; aplicar todas; editar y aplicar; lista y visibilidad solo Directores/staff; prompt del configurador en borrador en el núcleo; simulador con guion de herramientas.

### Componentes por capa M4b

**Domain**
- `EnumsAgentes`: `TipoTarea { Trabajo = 1, ConfiguracionReglas = 2 }`.
- `EnumsReglas`: `OrigenRegla.PropuestaAgente = 3` (valor reservado en M3); `TipoPropuestaRegla { Nueva = 1, Cambio = 2, Desactivar = 3, ActivarSugerencia = 4 }`; `EstadoPropuestaRegla { Pendiente = 1, Aplicada = 2, Descartada = 3, Fallida = 4 }`.
- `Entities/PropuestaRegla.cs` (`SoftDestroyable, ITenantOwned`): `TenantId`, `TareaAgenteId`, `PasoNumero` (llamada del modelo que la originó, para ubicarla en su turno), `ToolUseId`, `Tipo`, `Estado`, destino (`Alcance?`, `AreaId?`, `ClienteCarteraId?`, `AgenteArtefactoId?`, `AgenteOrganizacionId?`), `ReglaId?` + `ReglaVersionVista?` + `ReglaActivaVista?` (cambio/desactivar), `SugerenciaArtefactoId?`, `Modo?`, `TipoRegla?`, `Titulo?` (150), `Texto?` (4000), `Etiquetas?`, `PorQue?` (500), `MotivoFallo?` (500), `ResueltaPorUsuarioId?`, `ResueltaAt?`, `ResultadoReglaId?`, `VersionToken` (**token de concurrencia**).
- `TareaAgente`: + `Tipo` (default Trabajo). `ReglaEvento`: + `PropuestaReglaId?`.

**Application**
- `Interfaces/IResolvedorSesion`: + `ResolverUsuarioAsync(string usuarioId, int tenantId)` para procesos en segundo plano (sin caché, lee la base; puebla `ITenantContext` + `IContextoUsuario`; `false` si el usuario no existe, está bloqueado o cambió de organización).
- `Motor/IMotorAgentes.cs`: `ContextoHerramienta` + `TipoTarea`; `IServicioTareas.IniciarConfiguracionAsync(string texto)`; `ListarConfiguracionesAsync(DataTableRequest, filtros)`; `TareaFiltros` + `Tipo?`; `TareaDetalleDto` + `EsConfiguracion` + `PropuestasPorPaso`.
- `Motor/IConstructorContexto.cs`: `ArmarConfiguracionAsync(InstantaneaConfiguracion)` — formato de contexto **3** solo para configuración (reglas de plataforma publicadas + declaración propia + prompt del configurador); instantánea con `Tipo`, versión del configurador e ids de plataforma. Los formatos 1 y 2 no cambian.
- `Interfaces/IPropuestaReglaService.cs`: `ListarPorTareaAsync(int tareaId)` · `AplicarAsync(int id, bool confirmarCambio)` → `ServiceResult` con `TipoError` (+ código `CambioDesdePropuesta` en `Errors`) · `AplicarTodasAsync(int tareaId, int? pasoNumero)` → resumen · `DescartarAsync(int id)` · `DatosParaFormularioAsync(int id)` (precarga).
- `Interfaces/IReglaService`: `CrearAsync`/`EditarAsync`/`CambiarEstadoAsync`/`ActivarSugerenciaAsync` aceptan `OrigenAplicacion?` (`PropuestaReglaId`) → registran `Origen = PropuestaAgente` (altas) y `ReglaEvento.PropuestaReglaId`, y marcan la propuesta **Aplicada en el mismo `SaveChanges`**.
- `Interfaces/IConfiguradorReglas`: `DisponibleAsync()` (existe versión publicada del artefacto `configurador-reglas` del rubro `plataforma`).

**Infrastructure**
- `Services/Configurador/HerramientasConfigurador.cs` (implementaciones de `IHerramientaAgente`, **sin `SaveChanges`**):
  - Guardas comunes: `ContextoHerramienta.TipoTarea == ConfiguracionReglas` (si no, Fallo "Herramienta no disponible para este agente"); `IContextoUsuario` resuelto del autor y **Director activo** de la organización (re-verificado en cada ejecución).
  - Lectura: `reglas_listar` (filtros alcance/destino/texto, páginas de 20, texto recortado a 300; excluye alcance Usuario salvo las del propio Director), `regla_obtener` (texto completo + versión; 404 lógico si no la ve), `estructura_empresa` (áreas, agentes de Olvidata habilitados y agentes de la empresa — ids y nombres), `clientes_buscar` (texto, máx. 20), `sugerencias_listar`.
  - Propuesta: `proponer_regla_nueva`, `proponer_cambio_regla`, `proponer_desactivar_regla`, `proponer_activar_sugerencia`; validan esquema, alcance permitido (nunca Usuario), destino vigente de la organización, largo ≤ 4.000, máximo 10 propuestas por paso del modelo; guardan `ReglaVersionVista`/`ReglaActivaVista`. Devuelven al modelo un resumen ("Propuesta registrada: …") o un Fallo con motivo para que corrija. Idempotencia por `ToolUseId` (la ejecución ya registrada no vuelve a crear la propuesta).
- `Services/Motor/ProcesadorTareas.cs`: para `TipoTarea.ConfiguracionReglas`, antes del bucle `ResolverUsuarioAsync(tarea.UsuarioId, tarea.TenantId)`; si falla → turno Fallido "La persona que inició la configuración ya no puede configurar reglas." (con `CierreTurno`). Contexto con `ArmarConfiguracionAsync` + verificación de hash. Herramientas = las del frontmatter del configurador.
- `Services/Motor/ServicioTareas.cs`: `IniciarConfiguracionAsync` (Director; configurador disponible; crea tarea `Tipo = ConfiguracionReglas` con instantánea formato 3); `Visibles()` excluye configuraciones para quien no es Director ni staff; seguimiento M3b sin cambios (autor); listado de configuraciones con pendientes/aplicadas.
- `Services/Configurador/PropuestaReglaService.cs`: permisos Director (y organización); `Estado ∈ {Pendiente, Fallida}` o "Esta propuesta ya fue resuelta."; verificación de cambio (`VersionActual != ReglaVersionVista` o `Activa != ReglaActivaVista`) → error `CambioDesdePropuesta` salvo `confirmarCambio`; delega en `ReglaService` con `OrigenAplicacion`; si el servicio de reglas devuelve error de validación → propuesta `Fallida` con `MotivoFallo` (guardado propio); `VersionToken` evita doble resolución por dos Directores; `AplicarTodasAsync` recorre pendientes en orden y aplica cada una en su propio guardado (éxito parcial, sin `confirmarCambio` implícito: las que cambiaron quedan con ese motivo).
- `Services/Motor/ProveedorModeloSimulado.cs`: si la solicitud trae herramientas `proponer_*` y es la primera llamada del turno → devuelve `tool_use` guionados (`estructura_empresa` y dos `proponer_regla_nueva` de la empresa, "Regla simulada N-a/b", modo por defecto); tras los resultados → `end_turn` "Te dejé propuestas simuladas.". Solo Development (sin cambios en su registro).
- `Services/Organizacion/ResolvedorSesion.cs`: `ResolverUsuarioAsync`.
- `nucleo/plataforma/plataforma.yml` + `nucleo/plataforma/agentes/configurador-reglas.md` (frontmatter `name`, `description`, `herramientas: [...]`): **primera versión redactada como borrador** (P7), importada en dev **sin publicar**.
- `Data/Configurations/ConfiguradorConfigurations.cs`; `AppDbContext`: `DbSet<PropuestaRegla>`; `DependencyInjection`: herramientas, servicios.

**Web**
- `ConfiguracionReglasController` [RequireDirector]: `Index`, `Listar` POST, `Nueva` GET, `Iniciar` POST (→ `Tareas/Detalle`), `AplicarPropuesta` POST JSON (`id`, `confirmarCambio`), `AplicarTodas` POST JSON, `DescartarPropuesta` POST JSON.
- `TareasController`: `Detalle`/`Progreso` renderizan tarjetas si `EsConfiguracion`; `Listar` con filtro Tipo (opción visible solo a Director/staff).
- `ReglasController`: `Index` con botón y estado de disponibilidad (`IConfiguradorReglas`); `Create`/`Edit` aceptan `propuesta` (precarga + aviso) y lo envían al servicio.
- Vistas: `ConfiguracionReglas/{Index, Nueva}`, `Tareas/_TarjetasPropuesta`, `_ScriptPropuestas` (acciones AJAX, modal de cambio, aplicar todas, actualización sin recargar), ajustes en `Reglas/{Index, _Form, Detalle}`, `Tareas/{Detalle, Index, _Conversacion}`.

### Modelo de permisos M4b
Policy `RequireDirector` en el controller; `PropuestaReglaService` y herramientas re-verifican Director activo de la organización; `ServicioTareas.Visibles()` oculta configuraciones a Empleados (404); seguimiento solo autor (M3b); staff lectura.

### Entidades y configuraciones EF M4b
| Entidad | Config |
|---|---|
| `PropuestaRegla` | textos con largos del diseño · enums int · `VersionToken` `IsConcurrencyToken` · FKs a tarea, regla, área, cliente, artefacto, agente de la empresa, resultado (Restrict) · único `(TareaAgenteId, ToolUseId)` (cada `tool_use` crea exactamente una propuesta; varias propuestas de una misma respuesta vienen en `tool_use` distintos) · índice `(TareaAgenteId, PasoNumero)` |
| `TareaAgente` | + `Tipo` int default 1 · índice `(TenantId, Tipo, UltimaActividadAt)` |
| `ReglaEvento` | + FK `PropuestaReglaId` (Restrict) |

### Migraciones requeridas M4b
**Sí:** `ConfiguradorReglasM4b` — tabla `PropuestasRegla` con índice único `(TareaAgenteId, ToolUseId)`, columna `Tipo` en `TareasAgente` (default 1) + índice, `PropuestaReglaId` en `ReglaEventos`. Sin transformación de datos.

### Estrategia de pruebas M4b
**xUnit (InMemory + `ModeloGuionado`)** — `ConfiguradorReglasTests.cs`:
- Herramientas: lectura sin preferencias de otros miembros ni datos de otra organización; `regla_obtener` de una regla no visible → no encontrada; herramientas rechazadas en tareas de tipo Trabajo; autor degradado a Empleado o bloqueado entre turnos → turno fallido.
- Propuestas: validación de alcance (Usuario rechazado), destino vigente, largo, máximo 10 por paso; idempotencia por `ToolUseId` al reanudar.
- Aplicar: cada tipo (nueva, cambio, desactivar, activar sugerencia) crea el efecto con origen y evento enlazado; límite → Fallida con motivo y reintento exitoso tras liberar; cambio desde propuesta exige confirmación; dos Directores → uno "ya fue resuelta"; aplicar todas con éxito parcial; descartar; editar y aplicar marca la propuesta en el mismo guardado.
- Tarea: configurador no disponible sin versión publicada; Empleado no inicia (SinPermiso) ni ve (NoEncontrado); otro Director ve y aplica pero no sigue conversando; contexto formato 3 sin reglas de la empresa y hash verificado; **golden de formatos 1 y 2 intacto**.
- Simulador: guion de herramientas produce propuestas y tarjetas.
- Los 100 tests actuales siguen verdes.

**MySQL real:** migración, único por `ToolUseId`, concurrencia real del token. **QA navegador:** modelo simulado con guion (propuestas nuevas); cambios/desactivaciones/activar sugerencia con propuestas insertadas en dev; permisos, tarjetas, modal, aplicar todas, editar y aplicar, historial, filtro, mobile y contraste en tema oscuro. Calidad real del configurador y del prompt: corrida con costo (PA-02).

### Riesgos tecnicos M4b
- **RT-M4b-01 (alto) Permisos en segundo plano:** el worker no tiene sesión; se resuelve el contexto del autor desde la base y se re-verifica en cada herramienta y al aplicar.
- **RT-M4b-02 (alto) Compatibilidad de hash:** formato 3 exclusivo de configuración; golden de 1 y 2.
- **RT-M4b-03 (medio) Costo de lectura:** resultados de herramientas paginados y recortados.
- **RT-M4b-04 (medio) Calidad del prompt borrador:** no se publica sin revisión y evaluación de Joaquín; sin publicar, la función queda deshabilitada.
- **RT-M4b-05 (bajo) Simulador vs. modelo real:** el guion prueba UI y persistencia, no la calidad de propuestas.
- **RT-M4b-06 (bajo) Acoplamiento `ReglaService` ↔ propuestas:** limitado a un parámetro opcional de origen.

### Gate M4b
Arquitectura lista para Implementación. Requiere aprobación de: tipo de tarea "configuración" con contexto propio (formato 3), contexto de usuario resuelto en el worker con re-verificación, herramientas de lectura/propuesta acotadas (sin alcance Usuario, 10 por paso), aplicación por `ReglaService` con origen en el mismo guardado, "Aplicar todas" con éxito parcial sin confirmar cambios implícitamente, prompt del configurador redactado en borrador e importado sin publicar, simulador con guion de herramientas.

---

## Historial de ajustes

### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **M08** — 1 bloques (2026-09-14 a 2026-09-14) → [`3-arquitecto-mvc-M08.md`](historial/3-arquitecto-mvc-M08.md)
- **M06** — 1 bloques (2026-09-14 a 2026-09-14) → [`3-arquitecto-mvc-M06.md`](historial/3-arquitecto-mvc-M06.md)
- **M03** — 1 bloques (2026-09-14 a 2026-09-14) → [`3-arquitecto-mvc-M03.md`](historial/3-arquitecto-mvc-M03.md)
