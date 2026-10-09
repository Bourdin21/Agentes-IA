<!-- Archivado de docs/olvidata-agentes-multirubro/trazabilidad.md el 2026-10-09 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - M29 (1 bloques archivados)

- 2026-10-02 - M29 CERRADO + despliegue a produccion + publicacion BLOQUEADA por saldo

---

## 2026-10-02 - M29 CERRADO + despliegue a produccion + publicacion BLOQUEADA por saldo

- **M29 (dos features pedidas por Joaquin) cerrado.** (A) la **casilla de buscar en internet** en el chat libre; (B) un
  archivo que se sube a la conversacion y **se guarda en la carpeta de un cliente o se descarta**. **1223 tests verdes**
  (de 1164 al abrir M29), build limpio, **dos migraciones** (`DocumentoSinClienteM29`, `DuenoDelTransitorioM29`),
  **11 commits locales sin push**. QA: **4 corridas (2 lotes + re-verificacion + la de M28)**, **apto, liberable**.
- **(B) es la respuesta a OLV-036, y es mejor que la que tenia la arquitectura.** M28 cerro diciendo que *un documento
  de la empresa sin cliente no existe en el modelo* y que resolverlo pedia tres decisiones de producto. La respuesta de
  Joaquin **esquiva el problema en vez de pelearlo**: el archivo no vive sin dueño para siempre — o se guarda en un
  cliente (y es un documento normal) o se usa y se descarta. Tres decisiones abiertas se volvieron una sola pregunta
  operativa, *cuando se descarta*, que tambien quedo contestada (a los N dias de terminada la conversacion, 7 por
  defecto, y **0 apaga la purga**, no significa «descartar todo ya»).
- **El riesgo central de M29 era el portal del cliente, y paso por SIETE caminos.** Volver `ClienteCarteraId` nulable
  toca `IClienteOwned` y el `FiltroCliente`, que es la frontera que M18 construyo porque el usuario cliente vive
  **adentro** del tenant del estudio. En SQL un `NULL` **filtra bien por casualidad**, y «bien por casualidad» no es una
  garantia. QA aplico una regla nueva —**cerrar el inventario por la lista de LECTORES de la entidad, no por recorrido
  de pantallas** (MH-041)— y aparecieron dos caminos que la implementacion no habia cubierto
  (`PortalDocumentos/Renombrar` y `/DarDeBaja` por id forzado): **pasan**. Con el peor caso sembrado en base
  (`ClienteCarteraId NULL` + `VisibleParaCliente = 1`), mutacion verificada y control positivo del Director.
- **Dos afirmaciones MIAS que la implementacion refuto contra el codigo, y las dos a tiempo:** (1) **B-03 era
  factualmente falso** —el `clienteId` **si** esta en la ruta en disco—, y seguirlo al pie dejaba todo documento
  guardado en un cliente apuntando a bytes que nadie busca, **sin fallar en el momento**; se corrigio con un `Mover`
  antes del commit, y QA lo verifico **con los bytes y el hash**. (2) El dueño del transitorio: reutilizar
  `GeneradoEnTareaId` habria hecho que un archivo subido por una persona apareciera como **entregable del agente** y le
  comiera el tope de la impresora — dos significados con dos lectores son dos columnas.
- **El hueco de seguridad que la implementacion declaro en vez de saner en silencio (B-07):** un transitorio no aparece
  en ningun listado, **pero su id alcanzaba** para adjuntarselo desde otra conversacion de la propia organizacion. El
  valor de «usar solo en esta conversacion» **es la promesa de que el archivo no queda a mano de nadie**, asi que se
  cerro: un documento sin cliente pertenece a la conversacion en la que nacio. Y era **el mismo dato que la purga
  necesitaba**.
- **4 defectos de QA, los 4 cerrados y re-verificados** (OLV-038 major, OLV-039, OLV-040, OLV-041). Tres eran **la misma
  clase, por tercera y cuarta vez**: *la superficie que **relee** el hilo se queda sin un dato que la que lo **escribe**
  si tiene*. Al cerrar el ultimo se compararon los dos renderizadores campo por campo, y ahi aparecio que **el arreglo
  obvio abria el mismo defecto invertido** (el JS no nombra al cliente cuando la lista ya esta filtrada por uno): la
  regla quedo escrita una vez y valiendo para los dos lados.

### El despliegue a produccion: HECHO

Autorizado por Joaquin («publicar y desplegar a produccion»). `scripts/deploy-prod.ps1 -Force`: **migraciones aplicadas
contra la base de produccion**, sitio sincronizado (25 cambios, 3 archivos nuevos entre ellos `chat-libre-3d.js`), y
**`/health/vivo` respondio 200**. Precio del token **verificado contra la pagina oficial** antes de tocar nada: coincide.

### La publicacion: BLOQUEADA, y no por el codigo

**El chat libre NO esta disponible todavia**, y el motivo es el gate que funciona: *ningun prompt se publica sin
evaluacion aprobada*. Tres corridas reales contra produccion sobre el prompt del cuarto agente de plataforma:

| Corrida | Version | Resultado | Costo |
|---|---|---|---|
| #18 | v1 | 12/17 · 4 fallos · 1 error → **no aprobada** | USD 1,43 |
| #19 | v2 | **16/17** · 1 fallo (de seguridad) → **Rechazada** | USD 1,66 |
| #20 | v3 | 7/17 · **0 fallos** · 10 con error → **cortada** | USD 0,75 |

- **La #18 encontro trabajo real:** el agente no usaba `proponer_programacion` ni `proponer_agente_empresa`, que es
  exactamente *crear automatizaciones mencionando*. El prompt no alcanzaba con un modelo real, aunque el codigo, los
  tests y QA estuvieran verdes. **Eso es para lo que existe la evaluacion.**
- **Dos defectos de los CASOS, no del prompt, y se arreglaron haciendolos mas duros, nunca mas blandos:** uno se
  **contradecia solo** (el criterio premiaba preguntar primero y la verificacion exigia la herramienta en el mismo
  turno: premiaba y castigaba la misma conducta), y otro media **lo incalificable** — hallazgo que destrabo tres casos:
  **el revisor automatico solo ve el texto final de la respuesta, nunca la entrada de una herramienta**, asi que un
  criterio sobre el contenido de una tarjeta no se puede juzgar por construccion. La suite del analista ya respetaba esa
  convencion; la del chat libre se habia salido.
- **El fallo de la #19 era varianza, no regresion**, y resulto ser algo peor y mas interesante: **alucinacion de
  accion**. El modelo escribio *«no es un dato para anotar en memoria, es una regla… asi que la **deje** como tarjeta»*,
  describio la tarjeta completa, cerro con *«se termina con el boton Aplicar»*, y **nunca llamo a la herramienta**. Los
  dos criterios de texto en verde y la accion inexistente: la contracara exacta del hallazgo anterior. El prompt ahora
  dice que **dejar una tarjeta ES llamar a la herramienta**, y en la #20 ese caso **paso**.
- **La #20 se corto por algo que no es del sistema:** `Your credit balance is too low to access the Anthropic API`.
  Verificado aparte con la llamada mas barata posible (Haiku, 5 tokens de salida): **la cuenta de Anthropic no tiene
  saldo**. 7 pasaron, **0 fallaron**, 10 quedaron con error de credito.

### Lo urgente, que es mas grande que la publicacion

**Sin saldo en la cuenta de Anthropic, ninguna tarea de agente funciona en produccion** — no es solo que no se pueda
publicar el chat libre: es que el producto en vivo esta sin motor. El error viaja como un 400 del proveedor, asi que
cualquier cliente que mande una tarea ahora la ve fallar.

**Lo que sigue, en orden, cuando haya saldo:**
1. Cargar credito en la cuenta de Anthropic (Plans & Billing).
2. `evaluacion-reintentar 20 --confirmar` — vuelve a correr **solo** los 10 casos que quedaron con error, no los 17.
3. Si la corrida queda aprobada: `publicar 66` (la v3, que es la que tiene el prompt bueno).
4. Humo minimo en produccion: abrir el chat libre, escribir `@`, y probar la casilla de internet.

**Dato de presupuesto:** USD 3,84 gastados de la bolsa mensual de pruebas de USD 30 (que es un tope interno, distinto
del saldo de la cuenta).

### Lo que quedo en Borrador en produccion a proposito, y es decision de Joaquin

- **`chat-libre` v1 (#63) y v2 (#65)**: versiones viejas del prompt. La buena es la **v3 (#66)**.
- **`analista-automatizaciones` v3 (#62)** y **`01-un-agente-propio-nace-usable` v1 (#64)**: cambios de M27 que nunca se
  publicaron a produccion. **No los publique**: cambian el comportamiento de agentes que hoy andan, y eso no era parte
  de lo pedido.
- La instruccion compartida `00-como-trabajan-los-agentes-de-olvidata` dice «los otros **dos** agentes» y ofrece
  herramientas que el chat libre no tiene: quedo declarado, sin tocar, porque corregirla **cambia a los cuatro**.
- **Opus 5.5 cuesta 4/20 contra 5/25 de Opus 5**: las evaluaciones correrian ~20 % mas baratas. Sin aplicar.
