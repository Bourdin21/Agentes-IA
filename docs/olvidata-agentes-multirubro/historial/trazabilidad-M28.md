<!-- Archivado de docs/olvidata-agentes-multirubro/trazabilidad.md el 2026-10-02 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - M28 (4 bloques archivados)

- 2026-10-02 - Discovery (analista funcional) - M28: el chat libre
- 2026-10-02 - Diseno (disenador funcional) - M28: el chat libre
- 2026-10-02 - Arquitectura (arquitecto MVC) - M28: el chat libre
- 2026-10-02 - Documentacion + Cierre de calibracion - M28: el chat libre CERRADO

---

## 2026-10-02 - Discovery (analista funcional) - M28: el chat libre

- **Pedido.** Pantalla nueva de chat libre "como Claude web": consultas sueltas, arrobar agentes para pedirles tareas,
  crear reglas y automatizaciones por menciones, con buen diseno grafico y motion 3D.
- **Decision de encuadre (concepto rector).** El chat libre es **la CPU sin un programa cargado**: las cuatro
  conversaciones actuales arrancan con la RAM ya escrita por el sistema, y esta arranca vacia y **la persona carga la RAM
  mencionando**. Lo mencionado entra **como datos**: una mencion de configuracion **propone una tarjeta**, nunca crea
  (RF-05). Motivo: es la unica lectura del pedido que no rompe "una preferencia la aplica una persona".
- **Reutilizacion (instruccion 39 seccion 3).** Match en `docs/patrones/cat_resumen.txt`: **PAT-029** (conversacion
  multi-turno reanudable con contexto congelado), origen este mismo proyecto M3b. El motor entero se reutiliza; la
  tarea sin cliente ya existe (`ClienteCarteraId` es `int?`) y la vista de conversacion ya la comparten las cuatro
  conversaciones. **El pedido es una puerta nueva a un motor que ya esta entero**, no un modulo nuevo.
- **Lo que no existe y es el trabajo real (tres cosas).** (a) **Menciones**: cero, ni parser de `@` ni autocomplete;
  (b) **delegar en vivo a cualquier agente de la organizacion**: `delegar_subagente` solo corre en `TipoTarea.Trabajo`
  y solo admite **hijos publicados del agente base** (`SubtareasService.cs:68-92`); (c) **motion 3D**: el front es
  vanilla + jQuery + Bootstrap, **sin npm, sin bundler y sin ninguna libreria de animacion o 3D**.
- **Tension declarada, no resuelta.** "Motion 3D" contra la instruccion `38` del estudio, cuya regla 0 es *lo que la
  persona vino a hacer entra en la primera pantalla; todo lo demas se pliega*. Se abre como P4 con tres niveles en vez
  de decidirlo por cuenta propia: el fondo 3D de ambiente es el que mas choca y el que mas pesa.
- **Impacto en capas (preliminar).** *Domain:* valor nuevo de `TipoTarea`, y una tabla de menciones solo si se persisten.
  *Application:* `ResolvedorHerramientas` (que ve el tipo nuevo), resolucion de menciones. *Infrastructure:*
  `ServicioTareas` (arranque del chat libre), `SubtareasService` si P2 resuelve delegacion en vivo. *Web:* pantalla
  nueva, autocomplete en el compositor, assets de motion. *Nucleo:* prompt nuevo solo si P1 resuelve (b).
- **Estado: Discovery cerrado con 4 preguntas abiertas bloqueantes.** P1 quien atiende sin mencion (agente en blanco ya
  existente / cuarto agente de plataforma con prompt nuevo / ninguno) - P2 mencion de agente en vivo o tarea aparte -
  P3 confirmar que la mencion de configuracion propone y no crea - P4 alcance del motion (sin 3D / 3D acotado /
  3D de ambiente). **Analisis no arranca hasta que esten respondidas**: las cuatro cambian criterios de aceptacion,
  arquitectura y tamanio. Presupuesto omitido (proyecto personal).
- **Entrada de definiciones afectada:** `definiciones/1-analista-funcional.md` -> `M28` (nueva, no supera ninguna).
## 2026-10-02 - Diseno (disenador funcional) - M28: el chat libre

- **Idea rectora: la pantalla de arranque es la pieza de diseno; la conversacion ya esta disenada.** El pedido traia dos
  cosas que parecian una (*un chat como Claude web* + *motion 3D*) y separarlas es lo que resolvio la tension con la
  instruccion `38`, cuya regla 0 es *lo que la persona vino a hacer entra en la primera pantalla*.
- **D-01, la decision que ordena todo: el 3D vive en el estado vacio y se retira con el primer mensaje.** Un chat recien
  abierto **no tiene contenido que el adorno pueda tapar** — es el unico momento del producto donde una pieza 3D no
  compite con nada. Al primer mensaje **se desmonta** (no `display:none`: se destruye el contexto WebGL). Asi se cumple
  el pedido y la regla 0 **sin negociar ninguna de las dos**, y el costo de rendimiento se paga una sola vez.
- **D-02: dos momentos, una sola maqueta.** `ChatLibre/Index` es propia; la conversacion es la **compartida**
  (`Tareas/Detalle`), como ya hacen las otras tres de plataforma. Duplicarla costaba 270 lineas de `_Conversacion` mas
  405 de scripts de `Detalle`, y cada arreglo futuro dos veces. **Lo que hace propio al chat libre es su arranque y sus
  menciones, no una copia del hilo** (`38` seccion 6, sistemico antes que por pantalla).
- **D-04: la mencion en el texto es texto.** `@slug` en plano, **el servidor la vuelve a resolver**; sin token opaco ni
  id embebido. Lo que inserta el cliente es comodidad de tipeo, **nunca una autorizacion**. Una mencion que no resuelve
  queda literal y no confirma si eso existe. Es R-03 resuelto en la maqueta.
- **D-05: una sola mencion de agente por mensaje**; con dos se pide elegir. Es el freno de costo de P2 puesto en la
  pantalla, y ademas es honesto: un mensaje con dos agentes no dice cual hace que. Las de **configuracion** si pueden
  ser varias: no cuestan una tarea, cuestan una tarjeta.
- **D-06: el autocomplete viene en dos grupos y el de abajo es el que enseña.** Arriba Agentes, abajo Configurar con las
  cuatro cosas que se cargan. La persona escribe `@` por un agente y **se entera de que tambien puede configurar**: es lo
  que convierte *crear reglas por menciones* en algo que se descubre sin manual.
- **RD-01, el riesgo que cambio un diseno:** si las pastillas del arranque son preguntas, la gente aprende a usar el chat
  como buscador y nunca descubre las menciones, que son el 80 % del valor. Por eso D-08: las pastillas **escriben
  menciones**, no preguntas.
- **Estado: Diseno cerrado.** 4 pantallas (una sola nueva), 10 estados, 8 historias. Siguiente: Arquitectura.
- **Entrada afectada:** `definiciones/2-disenador-funcional.md` -> `Diseno M28` (nueva).
## 2026-10-02 - Arquitectura (arquitecto MVC) - M28: el chat libre

- **A-00: la bandera del Analisis era incorrecta y se corrige. M28 NO lleva migracion.** `TareaAgente.Tipo` no tiene
  ninguna linea en `TareaAgenteConfiguration` (`AgentesConfigurations.cs:181-215`): cae en la convencion de EF y el
  snapshot lo confirma como `int`. El repo ya tenia el precedente escrito (`EnumsAgentes.cs:128-131`, `NotaDelMotor`)
  **junto con la advertencia que si importa**: lo que un valor nuevo rompe no es la base, son **los switches con
  `default`**, que lo aceptan en silencio y lo mapean mal. Si al implementar aparece una migracion, es señal de que se
  agrego una entidad que el diseño no pedia.
- **A-01: la palanca es `EsDePlataforma`** (`NotaSubtarea.cs:35-36`). Una linea hace que cinco familias de herramientas
  acepten el tipo nuevo sin tocarlas una por una. Por eso es **lo primero que se prueba, no lo ultimo**.
- **A-02: `ArmarPlataformaAsync` no se toca** — ya es generica (recibe formato, tipo y declaracion por parametro). El
  cuarto agente es el molde del analista repetido: ~10 switches, un wrapper, un permiso, un controller, un item de menu.
  Y hereda las **instrucciones compartidas de plataforma sin una cuarta copia**, que es lo que hace viable derivar.
- **A-03b: deuda que se paga aca y no despues.** Los dos `IQueryable` de "los agentes que esta persona puede usar" estan
  **duplicados en tres lugares** y M28 seria la cuarta copia. Se extraen a `IAgentesDisponiblesQuery`. No es cosmetico:
  es la unica forma de que el autocomplete de la pantalla y la autorizacion de la herramienta **no puedan divergir** — y
  si divergen, el autocomplete ofrece algo que la herramienta despues rechaza, el peor resultado para la persona (R-A2).
- **A-04: no se relaja el gate de subagentes, se le da un segundo modo con nombre.** `SubagentesPermitidosAsync` queda con
  **modo jerarquia** (lo de hoy, sin un solo cambio de comportamiento) y **modo abierto** (chat libre, exactamente lo que
  devuelve la query compartida). Dos ramas y dos tests en vez de un `if` adentro de un predicado, porque **los dos modos
  tienen reglas de seguridad distintas y mezclarlos es como se cuela una fuga**. El gate sigue siendo lista blanca de
  `TipoTarea`, nunca un `!=` negado.
- **CA-02.5 se verifica, no se implementa.** `AvisarFinAsync:211-213` ya cuenta como pendiente solo lo que no esta en
  `Completada | Fallida | Cancelada`: el padre se despierta **tambien cuando la parte falla o se cancela**. R-04 cerrado
  sin codigo nuevo.
- **A-05: M28 establece la primera carga diferida del proyecto** (hoy no hay ni un `defer` ni un `import()` dinamico).
  `three` por CDN con **version fija** e `import()` dinamico, detras de **tres compuertas** (`prefers-reduced-motion`,
  WebGL disponible, pantalla montada): si alguna falla **la libreria no se descarga**. Fallo del CDN = `try/catch`
  silencioso y version plana. La pieza **no recibe ni muestra datos**, asi que ningun dato de la organizacion llega a un
  script de CDN.
- **Bug preexistente que M28 destapa (R-A6):** el switch de `ArmarEvaluacionAsync` (`ConstructorContexto.cs:505-506`)
  **hoy solo cubre los formatos 3 y 4 — al 5 ya le falta**. Se agrega el 5 junto con el 6: construir el 6 sobre un
  agujero conocido seria peor que el agujero.
- **Impacto en capas.** *Domain:* un valor de enum, sin migracion. *Application:* constante de formato, `IChatLibre`,
  `IAgentesDisponiblesQuery`, `OpcionMenu`, flag de DTO, mensajes. *Infrastructure:* wrapper de contexto, arranque de
  tarea, ~10 switches, dos modos de subagentes, permiso, tres llamadores migrados a la query. *Web:* controller, vista de
  arranque, item de menu, `<option>` de filtro, `site.js` (autocomplete), `chat-libre-3d.js`, CSS. *Nucleo:* prompt,
  manifiesto, suite de evaluacion.
- **Estado: Arquitectura cerrada**, con orden de implementacion de 8 pasos donde el 3D va **ultimo y aislado**: es la
  unica parte que se puede sacar sin que M28 deje de funcionar. **Presupuesto omitido** (producto propio). Siguiente:
  Implementacion.
- **Entrada afectada:** `definiciones/3-arquitecto-mvc.md` -> `Arquitectura M28` (nueva).
## 2026-10-02 - Documentacion + Cierre de calibracion - M28: el chat libre CERRADO

- **Estado: las 9 etapas corridas** (presupuesto omitido, producto propio). **Veredicto de QA: apto con reparos.**
  **1164 tests verdes** (de 1120 al abrir M28), build limpio, **sin migracion EF**, **6 commits locales sin push**.
- **QA: 4 corridas** (3 lotes + 1 re-verificacion). **10 defectos reportados** (OLV-028 a OLV-037): **9 cerrados y
  re-verificados reproduciendo el caso original**, **1 abierto** que no es de M28.
- **El unico pendiente, y es decision de producto, no un arreglo (OLV-036):** **subir** un archivo nuevo desde una
  conversacion **sin cliente** no funciona. El implementador **paro y aviso** en vez de parchearlo, con el motivo de
  fondo: un **documento de la empresa sin cliente no existe en el modelo** -- `DocumentoCartera.ClienteCarteraId` es
  `int` no nulable con FK, entra en 4 indices (uno unico `(ClienteCarteraId, NombreVigente)`), `AdjuntoMensajeTarea`
  tiene otra FK no nulable, y **el clienteId es parte de la ruta en disco**. Hacerlo valido de verdad es migracion mas
  tres decisiones que nadie tomo: donde se ve un documento de la empresa, si dos sin cliente pueden llamarse igual
  (MySQL deja pasar varios NULL en un indice unico) y contra que cuota cuentan. **No lo rompio M28:** el `CLAUDE.md`
  dice desde el 2026-09-25 que las tres conversaciones de plataforma **aceptan documentos adjuntos, sin cliente**, y
  resulta que el camino de **subida** nunca existio -- se podia leer lo ya cargado, no cargar. **Lo decide Joaquin.**
- **Lo que no se hizo y queda declarado:** la **casilla de buscar en internet** no se implemento en el chat libre. El
  motor calcula `busquedaOfrecida = trabajo && ...`, asi que **ninguna** conversacion de plataforma la ofrece hoy: son
  cuatro switches mas una decision de costo (USD 10 cada 1.000 busquedas), no un renglon de vista. Para una pantalla
  que existe para *resolver cualquier consulta suelta* es el candidato mas obvio a lo que sigue.
- **7 defectos preexistentes encontrados y arreglados de paso, 4 de ellos silenciosos:** un chat libre reanudado
  **creaba otra parte en cada sondeo** y quedaba colgado para siempre; una tarjeta de propuesta **no la veia nadie, ni
  su autor**; **ninguna tarjeta de trabajo** de un chat libre se podia aplicar; una tarjeta de aprobacion podia
  aparecer **sin nada que la resuelva**; `ArmarEvaluacionAsync` no cubria el formato 5 (evaluar el analista usaba la
  declaracion del formato 1); `ConsumoService` mostraba al asistente y al analista como «Agente»; y el menu ofrecia
  **las cuatro** conversaciones de plataforma sin version publicada -- ese no era del chat libre, era de las cuatro, y
  se arreglo una vez para todas.
- **El hallazgo de metodo, que vale mas que el modulo.** OLV-033 es el **molde inverso de R-A1**: buscamos los `switch`
  con `default` que **aceptan** un valor nuevo en silencio, y no las **listas blancas de un solo valor que lo rechazan**
  en silencio. Medido en este repo al agregar un valor de enum: **7 sitios de clase A** (los que buscabamos) contra
  **84 comparaciones de clase B**, de las cuales **5 eran del molde del defecto**. Esa linea en el checklist de
  arquitectura habria evitado **dos de las seis corridas de implementacion**.
- **Calibracion (sin precio, es producto propio):** 10 corridas de subagente, ~2.753.000 tokens, ~5 h 20 de reloj de
  agente. **El 40 % del esfuerzo de implementacion y QA se fue en encontrar y cerrar defectos, no en construir** -- para
  la proxima estimacion de esta familia, QA mas arreglos **no es un 15 % de contingencia, es una etapa propia**. Y el
  rasgo que se repite por cuarta vez: **en los modulos que extienden el motor, el costo no esta en la capacidad nueva
  sino en los lugares viejos que no sabian del caso nuevo** (aca: la capacidad nueva fue una puerta a un motor ya
  entero, y el trabajo real fueron ~10 switches, 84 comparaciones y 7 defectos ajenos).
- **Patrones nuevos en el catalogo:** **PAT-048** (autocomplete de menciones servido por la MISMA consulta que despues
  autoriza) y **PAT-049** (pieza 3D decorativa de carga diferida que se desmonta cuando aparece el contenido).
- **Entradas afectadas:** `7-documentador.md` -> M28 (alcance para el cliente); `4-presupuestador.md` -> cierre de
  calibracion M28; `3-arquitecto-mvc.md` -> A-07..A-10; `6-qa.md` -> 3 lotes mas re-verificacion.
