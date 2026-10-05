<!-- Archivado de docs/olvidata-agentes-multirubro/trazabilidad.md el 2026-10-03 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-10 (1 bloques archivados)

- 2026-10-03 - Cierre de la implementacion (decision de Joaquin: no publicar todavia)

---

## 2026-10-03 - Cierre de la implementacion (decision de Joaquin: no publicar todavia)

- **Joaquin decidio desestimar las pruebas contra produccion y cerrar la implementacion**, y **no publicar** el agente
  del chat libre hasta que haya saldo. Motivo aceptado: publicarlo ahora lo pondria en el menu de todas las
  organizaciones y **fallaria en el primer mensaje**. El estado actual —codigo desplegado, agente en **Borrador**, menu
  que no lo ofrece (CA-01.2)— **es el estado seguro**, no un trabajo a medio terminar. Se descarto usar
  `evaluacion-excepcion`, que habria salteado el gate **y** publicado algo que no puede funcionar.
- **Se cerro el ultimo cabo de codigo: la quinta pantalla.** `Agentes/Ejecutar` —el arranque de una tarea de **trabajo**—
  seguia pidiendo cliente para subir un archivo, y una **tarea de trabajo sin cliente es un caso soportado desde M5**
  que ya tenia `adjunto_leer` habilitado: el sistema decia que leia adjuntos y no habia forma de **ponerle** uno.
- **Y ahi apareció otro defecto silencioso, el quinto de esta familia.** El cuadro de adjuntos de esa pantalla es un
  select2 que se llena desde `Documentos/Opciones`, y ese listado **excluye los documentos sin cliente** (CA-02.4, que
  esta bien). Recargarlo despues de subir no traia el transitorio: **el archivo entraba al servidor y no quedaba
  adjunto, sin que nada fallara**. El boton mintiendo por un camino nuevo. Se arreglo conservando lo que devuelve la
  subida y reponiendolo como opcion elegida, con la leyenda de D-02.
- **Lo que NO hizo falta, y se verifico antes de escribir una linea:** la guarda de **B-07** y el camino del **huerfano
  adoptado** ya cubrian esta pantalla (`PreparadorTareaTrabajo` valida con `exigirCliente` segun el dto, y
  `CrearAsync` ya llamaba a `AdoptarTransitoriosAsync`), igual que **B-04** y la purga. Un solo archivo de produccion
  tocado, **sin migracion**.
- **Estado final: 1227 tests verdes** (de 1120 al abrir M28: **+107**), build limpio, **dos migraciones**, **16 commits
  locales sin push**, nada publicado. **Desplegado a produccion** y verificado desde afuera.
- **Los dos hallazgos de prompt se subieron a la memoria cross-proyecto** (`32-estandares-qa-implementador`), porque son
  generalizables a cualquier proyecto con agentes: **OLV-ALUC-01** (alucinacion de accion: el modelo narra lo que no
  ejecuto, y los criterios de texto no distinguen hacer de contar) y **OLV-EVAL-01** (un criterio de evaluacion solo
  puede juzgar lo que el revisor VE; lo que esta en la entrada de una herramienta se mide con verificacion mecanica).
- **Pendientes declarados, los tres de decision y ninguno de codigo:** (1) **cargar saldo** en la cuenta de Anthropic —
  sin eso **ninguna** tarea de agente funciona en produccion, ni las que ya andaban; (2) publicar el chat libre cuando
  haya saldo (`evaluacion-reintentar 20 --confirmar` y despues `publicar 66`); (3) la inconsistencia de
  `nucleo/plataforma/instrucciones/00-como-trabajan-los-agentes-de-olvidata`, que dice «los otros **dos** agentes» y
  ofrece herramientas que el chat libre no tiene: corregirla **cambia a los cuatro**, asi que es decision de Joaquin.
  Quedan tambien en Borrador a proposito `analista-automatizaciones` v3 y `01-un-agente-propio-nace-usable`.
