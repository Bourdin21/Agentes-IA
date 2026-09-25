# Memoria - QA

## Proyecto: olvidata-agentes-multirubro
## Ultima actualizacion: 2026-09-25 (QA M20 coprocesador aritmetico + M21 ojos, segunda mitad)

## Definiciones vigentes

# QA M20 (coprocesador aritmetico) + M21 (ojos, segunda mitad: PDF escaneado) (2026-09-25) - CERRADA

**VEREDICTO: aprobado con reparos.** Los dos modulos hacen **exactamente lo que prometen** y lo caro esta bien
resuelto: el aislamiento del PDF, el tope por conversacion y la ausencia de base64 en la base dan **PASS sin una sola
correccion**. Los 3 defectos corregidos son **todos de texto y de borde**, ninguno de datos ni de permisos: dos
pantallas que afirmaban algo que no era cierto y un tope de tiempo que era una carrera. **Sin entidades y sin
migracion**, como pedia la arquitectura (verificado sobre los dos commits).

Entrada: `1-analista-funcional.md` M20 (RF-M20-01..09, CA-M20-01..06) y M21 (RF-M21-01..07, CA-M21-01..05),
`2-disenador-funcional.md` (tabla de "donde se ve", 6 HU, 4 riesgos), `5-implementador.md` (DI-M20-A..G, DI-M21-A..F y
los **cuatro desvios que el implementador reporto**, verificados uno por uno). Commits `b551010`, `2acfa4f`, `0335340`.

**Linea base:** build **0 errores / 2 advertencias** (preexistentes, analizadores xUnit de M18). `dotnet test` **medido
sin pipe** (`> archivo 2>&1` + codigo de salida): **994/994, exit 0**. **Los 5 goldens de contexto sin un byte de
cambio** (`git status` de `Goldens/` vacio y ningun `.actual.txt`): CA-M21-05 PASS. Cierre: **996/996, exit 0** (+2 por
los tests de los fix).

**La base de desarrollo llego atrasada:** la migracion de M19 (`GeneradoEnTareaId`) **no estaba aplicada**, asi que la
primera subida de un documento fallaba con `Unknown column` y la pantalla decia "No se pudo guardar el documento".
Se corrio `dotnet run --project src/OlvidataAgentes.Admin -- migrar` y quedo resuelto. **No es un defecto de M20/M21**
(ninguno de los dos trae migracion), pero conviene que el orquestador migre produccion al desplegar M19+M20+M21.

**Costo cero:** `Anthropic__Simulado=true` + `Anthropic__ApiKey` invalida de resguardo, confirmado en los **2**
arranques por la linea *"Motor de agentes con MODELO SIMULADO ... el costo es cero"*; `grep -c anthropic.com` sobre los
logs = **0**. Ningun `appsettings` editado (todo por variables de entorno).

**Camino de verificacion:** el servidor MCP `playwright` **si respondio en esta sesion** (a diferencia de las corridas
del 21 y del 24 de septiembre). Verificacion automatizada por navegador real (Chromium del MCP) sobre
`https://localhost:7200`, mas `mysqlsh` contra `olvidata_agentes_dev` para lo que no se ve en pantalla.

## Los 3 defectos (todos reproducidos, todos corregidos, un commit cada uno)

| Id | Sev | Que pasaba | Commit |
|---|---|---|---|
| **OLV-027** | minor | **El test intermitente era un defecto del codigo, no ruido del test.** `SegundosMaxExtraccion = 0` se implementaba con `CancelAfter(TimeSpan.Zero)`, que avisa desde el hilo del temporizador y **corre una carrera** contra la extraccion ya encolada. Medido: con el ThreadPool saturado la extraccion gana **298 de 300 veces** (el archivo vuelve legible en vez de "no se pudo leer"); aislado pasa 12 de 12. O sea: un tope de configuracion en 0 **no hace nada** bajo carga. El cero se decide ahora **antes de encolar**. | `84b54fd` |
| **OLV-025** | minor | La ficha del agente decia **"En tareas principales (no en las partes que pide un coordinador)"** para "Proponer pedirle documentacion al cliente", cuya condicion real es `PortalDeClientesEncendido`. Es la **gemela** del bug que M20 arreglo para `TodaTareaDeTrabajo` (DI-M20-G) y que el implementador dejo anotada. Causa: la rama `_ =>` del switch devolvia el texto de `TareaPrincipal`, asi que **todo valor nuevo del enum hereda una mentira**. Ahora cada condicion tiene su brazo y el default es una raya. | `019b850` |
| **OLV-026** | minor | De los **cinco textos** del escaneado, la **ficha del documento** era el unico que no se leia igual: *"El agente no puede leer este documento: **Es** un escaneado de 25 paginas..."*, con mayuscula en el medio de la frase, mientras el mensaje de subida y **la otra rama del mismo ternario** iban en minuscula. Era exactamente el riesgo declarado por el disenador ("que uno quede viejo"). La frase se arma ahora en `DocumentosTextos.AvisoNoLegible`. | `4f9809f` |

Los tres se **verificaron en rojo antes** del parche: OLV-027 con una sonda que satura el pool (298/300 rojas) y con la
asercion nueva (`Actual: 4`, el archivo consumido, incluso aislado); OLV-025 y OLV-026 revirtiendo el fix y viendo el
test fallar con el texto viejo.

## Cobertura de criterios de aceptacion

| CA | Resultado | Evidencia |
|---|---|---|
| CA-M20-01 | PASS | `1234,50 * 21%` = **259,25** en pantalla, con `(exacto 259,245)` en el detalle plegado. |
| CA-M20-02 | PASS | `SUMA(10;20;30,55)` = 60,55 exacto; la tabla de 39 casos del implementador cubre los 40 importes. |
| CA-M20-03 | PASS | `neto` / `iva = neto * 21%` / `total = neto + iva` encadenados dan 1.234,50 / 259,25 / **1.493,75**. |
| CA-M20-04 | PASS | `1/0` + 4 cuentas imposibles mas: la pantalla responde **200**, la tarea sigue **Completada** y el rotulo dice *"Calculo: bueno = 60,55 - no pudo hacer 4 cuentas: no se puede dividir por cero"* con cada motivo en el detalle. |
| CA-M20-05 | PASS | En "Ver pasos": *"Calculo: neto = 1.234,50 - iva = 259,25 - total = 1.493,75"*. **No aparece `calcular` ni JSON** en ningun lado de la pantalla. |
| CA-M20-06 | PASS | Ficha del agente: "Hacer una cuenta - De la plataforma - **En cualquier tarea de trabajo** - No - La recibe". La lista blanca de `ConsultaCliente` es por inclusion y la herramienta tiene ademas su guarda propia en `EjecutarAsync` (DI-M20-F). |
| CA-M21-01 | PASS | Escaneado de 4 paginas: *"Documento subido. El agente lo puede mirar (escaneado, 4 paginas). **Mirarlo cuesta mas que leer un PDF con texto.**"* El mismo contenido **con** capa de texto: *"El agente lo puede leer"*, 4 partes. |
| CA-M21-02 | PASS | Al modelo llega el archivo (`{"documento_id":77,...,"mirala":"Es un PDF escaneado y te lo paso para que lo MIRES..."}`). En la base, **cero base64**: `PasosTarea` y `EjecucionesHerramienta` sin `JVBERi`, `base64`, `iVBORw0KGgo` ni `/9j/4AA`; `ImagenesJson` = `[{"documentoId":77,"nombre":"extracto-marzo-escaneado.pdf","esPdf":true}]`. |
| CA-M21-03 | PASS | Escaneado de 25 paginas (5,6 MB): *"Documento subido, pero el agente no puede leerlo: es un escaneado de **25 paginas y el maximo para mirar es 20**."* Estado "El agente no puede leerlo". |
| CA-M21-04 | PASS | Tests del implementador (otro cliente, otra organizacion, PDF con texto, id inexistente, tarea ajena) **mas** IDOR por navegador: Director de la org B contra `/Documentos/Ver/77`, `/Ver/79`, `/Ver/80`, `/Descargar/77` y `/Documentos?clienteId=36` -> **404 en los 5, sin una letra de fuga**. |
| CA-M21-05 | PASS | Los 5 goldens sin cambios en la linea base y al cierre. |

## Cobertura de historias de usuario

| HU | Resultado | Evidencia |
|---|---|---|
| HU-M20-01 | PASS | La cuenta de IVA da el centavo exacto y el nombre encadena el redondeado (DI-M20-A verificado en pantalla). |
| HU-M20-02 | PASS | El paso muestra nombre, expresion y resultado formateados en castellano; el detalle trae `iva = neto * 21% = 259,25 (exacto 259,245)`. |
| HU-M20-03 | PASS | Cuenta imposible: la tarea termina bien y el rotulo **no miente por omision** (dice lo que salio bien y lo que no). |
| HU-M21-01 | PASS | Paso *"**Miró** «extracto-marzo-escaneado.pdf» (4 paginas)"* (RF-M21-06), contra un PDF **real** rasterizado sin capa de texto. |
| HU-M21-02 | PASS | El mensaje de subida dice estado, paginas y aviso de costo; fuera de tope dice el motivo exacto. |
| HU-M21-03 | PASS | Verificado **sobre lo que se le manda al modelo** con los topes REALES (2 PDF / 8 imagenes), no con los del test: con 3 escaneados y 1 foto en la misma conversacion viajan **Febrero.pdf, Marzo.pdf y Frente.png**, y **Enero.pdf va como la linea de texto** "lo miraste antes...". La foto **no se desplaza**. |

## Los cuatro desvios del implementador, verificados

| Desvio | Veredicto |
|---|---|
| DI-M21-B: las paginas viajan en `MotivoNoLegible` (sin migracion) | **Correcto.** Ida y vuelta verificado en pantalla: la grilla dice "(escaneado)" y el tooltip/la ficha dicen "de 4 paginas". |
| RF-M21-06 vs. la tabla del disenador (rotulo con paginas vs. tooltip) | **Resuelto bien.** El rotulo de la grilla es "El agente lo mira (escaneado)" y las paginas estan en el tooltip y en la ficha. Meterlas en el rotulo pedia persistir un numero, o sea migracion. Coherente entre los 5 textos **despues** de OLV-026. |
| DI-M20-G: `AgentesTextos.Condicion` sin brazo para `TodaTareaDeTrabajo` | **Arreglado y confirmado**: la ficha dice "En cualquier tarea de trabajo". **Y la gemela que dejaron anotada (`PortalDeClientesEncendido`) seguia mintiendo** -> OLV-025. |
| `MaxMbPdfParaMirar` 10 MB corto para un escaneado real | **Ya resuelto en `0335340`**: codigo y `appsettings.json` dicen **20** los dos. Un escaneado de 25 paginas y 5,6 MB se rechaza por **paginas**, que es el tope que refleja el costo. |

## Cobertura del catalogo cross-proyecto

| id | aplica | resultado | accion |
|---|---|---|---|
| OLV-025, OLV-026, OLV-027 | si (nuevos) | FAIL -> PASS post-fix | items creados + 3 auto-fixes |
| OLV-023 (resolvedor ofrece / ejecutor rechaza) | si | PASS | `calcular` se ofrece y ejecuta en tarea de trabajo; en `ConsultaCliente` no se ofrece **y** `EjecutarAsync` la rechaza (dos cierres). |
| OLV-001..004 (tema oscuro) | si | PASS | Estado y aviso del escaneado en oscuro: contraste **10,42** y **7,79** (AA >= 4,5), midiendo con el alfa compuesto. |
| OLV-021, OLV-022, OLV-024 | no | N/A | M20/M21 no agregan rol, policy ni patron propuesta/tarjeta. |
| MH-026 / MH-023 (historico que navega a un catalogo con soft-delete) | si (regla nueva) | PASS | Ver "reglas nuevas". |
| REG-010, KOI-003/005/006, ELV-001 | si (autorizacion vs. menu) | PASS | Sin links ni pantallas nuevas; IDOR cross-org 404 en 5 URLs. |
| CRM-015 (bajar la inicial rompe siglas) | si | PASS post-fix | El helper de OLV-026 respeta las siglas (test con "PDF con contrasena."). |
| KOI-014 (estados vacios) | si | PASS | Consola sin errores en las 16 combinaciones de pantalla/ancho/tema. |
| DN-001/002, MH-001, LP-004, CRM-003 | si (grilla de documentos) | PASS | La grilla de documentos no cambio de consulta; sin 500 ni scroll horizontal por tabla. |
| REG-001..009, GAN-*, VSF-*, CRM-001/002/004..006/016..018, MH-002..025, SG-*, LP-*, ELV-002, DN-003/004, KOI-001/002/004/007..013/015/016 | no | N/A | Ventas, compras, stock, pagos, AFIP, bot, catalogos, decimales en inputs, proyecciones financieras, Pareto: M20/M21 no tienen esos modulos. |

## Cobertura de reglas nuevas/modificadas desde la ultima corrida

Ultima validacion registrada: **2026-09-24** (QA M18). Diferencias desde entonces:

| Regla | Origen | Resultado | Accion |
|---|---|---|---|
| **MH-022** — proyeccion que estima por promedio **un solo lado** | `regresiones-manuales.yml` + bloque nuevo de la instruccion **32** (2026-09-24 23:36) | **N/A** | M20/M21 no proyectan nada hacia adelante. La calculadora resuelve lo que le piden; no estima. |
| **MH-023** — cruce en memoria de dos consultas cuando una navega a una entidad con query filter | catalogo (2026-09-25) | **PASS** | Ver MH-026. |
| **MH-024** — ledger con reversion: `MAX`/"ultimo" sobre hecho y contra-hecho | catalogo (2026-09-25) | **N/A** | No hay ledger con reversion en estos modulos. |
| **MH-025** — "el ultimo registro anterior a una fecha" resuelto en memoria sin desempate | catalogo (2026-09-25) | **N/A** | El evaluador encadena por **orden declarado** en la entrada, explicito y sin base de datos de por medio. |
| **MH-026** — reporte historico que navega a un catalogo con soft-delete y **pierde historia en silencio** | catalogo (2026-09-25) | **PASS** | Probado a proposito: se le dio **de baja** al PDF que la tarea habia mirado y el paso sigue diciendo *"Miró «extracto-marzo-escaneado.pdf» (4 paginas)"*. El nombre vive en el JSON del paso, no se busca en `DocumentosCartera`. Ademas se continuo esa conversacion: la tarea termino **Completada** sin un error en el log (RF-M21-04 con un documento dado de baja de verdad, mas exigente que el test del implementador, que borraba el archivo del disco). |
| OLV-021..024 | catalogo, mismo commit que fijo la fecha | ya validadas | Se validaron en la corrida de M18. |

## Compatibilidad con produccion (filas escritas por M16)

- El literal del test del implementador **coincide byte a byte con el JSON real** que escribe el producto
  (`{"tipo":"imagen_documento","documentoId":77,"nombre":"...","esPdf":true}`), asi que quitarle `esPdf` reproduce
  fielmente una fila de M16. Verificado leyendo una fila real de `PasosTarea`.
- Ademas se **fabrico una fila al estilo M16 en la base** (bloque `imagen_documento` **sin** `esPdf`, apuntando a una
  imagen) y se **continuo la conversacion**: se rehidrato sin excepciones, la tarea quedo **Completada** y el log no
  registro un solo `ERR]`. En `olvidata_agentes_dev` no quedaba ninguna fila de M16 de verdad (0 filas sin `esPdf`).

## Pantallas (instruccion 38)

16 combinaciones: 4 pantallas (grilla de documentos, ficha del documento, ficha del agente, detalle de tarea con la
cuenta) x **1440 y 390 px** x **claro y oscuro**. Sin errores de consola, sin estados casi vacios, sin el patron
`letra@Expresion`. Contraste de los textos nuevos en oscuro: **10,42** (estado) y **7,79** (aviso), los dos sobre AA.

**Hallazgo de layout, PREEXISTENTE y fuera de M20/M21 (OBS-1):** a **390 px en tema oscuro** la pagina desborda **3 px**
(`scrollWidth` 388 vs. `clientWidth` 385) y aparece scroll horizontal. En claro no pasa. La cadena es
`html > body > header.ov-topbar`, y el elemento que llega al borde es **`.ov-topbar-user`**, que termina en **387,8 px**
en oscuro contra **383,6 px** en claro — con el mismo padding, borde, margen y gap en los dos temas. **Se reproduce en
`/Reglas`**, una pantalla que M20/M21 no tocaron, asi que es del **layout compartido** y afecta a todo el portal. No se
autoparcheo: tocar el CSS del topbar impacta todas las pantallas y excede el alcance de esta corrida.

## Observaciones (no bloquean)

- **OBS-1** — el desborde de 3 px del topbar en oscuro a 390 px (arriba). Preexistente, de todo el portal.
- **OBS-2** — **M20 no tiene guion del simulador.** M10, M11, M14 y M4b lo tienen, asi que se puede ver su circuito
  entero sin costo; `calcular` no, y M19 tampoco. Para verificar el paso hubo que **fabricarlo en `PasosTarea`**.
  No es un defecto (la herramienta funciona), pero sin guion **nadie va a ver la calculadora funcionando en el
  navegador sin pagar tokens**, ni en una demo.
- **OBS-3** — el rotulo de varias cuentas fallidas dice *"no pudo hacer 4 cuentas: no se puede dividir por cero"*:
  cuenta **todas** las fallas pero muestra el motivo de **la primera**. Se puede leer como que las 4 fallaron por
  division por cero. El detalle plegado lo aclara. Es la redaccion elegida (`MensajesCalculo.NoPudoVarias`).
- **OBS-4** — la busqueda global de la grilla de documentos mapea texto a estados con `TextoLectura(estado)` **sin el
  tipo**, asi que buscar *"escaneado"* no encuentra los PDF escaneados aunque la grilla muestre "(escaneado)".
  Buscar "El agente lo mira" si los encuentra.
- **OBS-5** — el catalogo cross-proyecto tiene el id **`KOI-016` duplicado** (dos items distintos con el mismo id).
  Es **previo a esta corrida** (ya estaba en `HEAD`); conviene renumerar el segundo.

## Riesgos de liberacion

- **RT-01 (costo, el unico que importa).** Un escaneado de 20 paginas cuesta como veinte imagenes **en cada vuelta del
  bucle**. El tope de 2 PDF por conversacion esta verificado sobre el pedido real, pero **el techo verdadero sigue
  siendo el limite de gasto de M6**. Con el modelo real y una tarea larga, esto se paga. Mitigacion: el aviso de costo
  al subir ya esta; conviene mirar `Consumo` la primera semana que alguien suba escaneados de verdad.
- **RT-02.** `MaxMbPdfParaMirar` = 20 MB entra holgado en los 32 MB de la API, pero un escaneado de 20 paginas a 300 dpi
  puede pasarse: ahi queda "no puede leerlo" por peso, con el motivo. Es el comportamiento pedido.
- **RT-03.** El PDF **mixto** (algunas paginas con texto) sigue `LegibleEnParte` y sus paginas escaneadas **no se miran**
  (D-M21-a). Es el caso mas probable de un extracto real largo; esta fuera de alcance a proposito.
- **RT-04.** Un PDF con **texto basura** (sello OCR de dos palabras) queda `Legible` y el agente lee dos palabras
  (R-M21-02, fuera de alcance). El implementador lo verifico contra 18 PDF reales y el camino barato no se movio.
- **RT-05 (despliegue).** La migracion de **M19** no estaba en la base de desarrollo. Si produccion tampoco la tiene,
  **subir sin migrar deja la subida de documentos rota** (`Unknown column 'GeneradoEnTareaId'`). `deploy-prod.ps1` migra,
  pero conviene confirmarlo en el log.

## Preguntas para Joaquin (decisiones de producto, no defectos)

1. **¿M20 y M19 merecen guion del simulador?** (OBS-2) Sin el, la calculadora y la impresora no se pueden mostrar en el
   navegador sin gastar tokens. Son ~20 lineas en `ProveedorModeloSimulado` cada uno, pero es codigo nuevo y lo decide
   el producto, no QA.
2. **¿El desborde de 3 px del topbar en oscuro a 390 px se arregla ahora?** (OBS-1) Es de todo el portal, no de M20/M21,
   y tocar el CSS del topbar toca todas las pantallas.
3. **¿La busqueda de la grilla de documentos deberia encontrar "escaneado"?** (OBS-4) Hoy busca por el texto del estado
   sin el tipo.

## Checklist de salida para merge

- [x] Build **0 errores** (2 advertencias preexistentes de xUnit en tests de M18).
- [x] `dotnet test` **996/996, exit 0**, medido sin pipe. Linea base 994; +2 por los tests de los fix.
- [x] **Los 5 goldens de contexto sin un byte de cambio**, antes y despues.
- [x] **Sin entidades y sin migracion** en `b551010` y `2acfa4f` (verificado sobre los archivos de los commits).
- [x] Cada auto-fix con su test, **verificado en rojo antes** del parche.
- [x] Items nuevos del catalogo creados (**OLV-025, OLV-026, OLV-027**), YAML valido.
- [x] IDOR cross-organizacion sobre el PDF: **404 en las 5 URLs**, sin fuga.
- [x] **Cero base64** en `PasosTarea` y `EjecucionesHerramienta`.
- [x] Costo cero confirmado en los 2 arranques; `grep -c anthropic.com` = 0.
- [x] Base de desarrollo **devuelta a su estado**: checksum **156 tareas / 594 eventos / 56 documentos**, max evento 687,
      `visibles`/`del_cliente`/`portales_on` en 0, y la carpeta de blobs de vuelta en **44 archivos, ninguno del dia**.
- [x] `git status` del repo sin nada mio (solo lo que ya estaba sucio al empezar).
- [ ] **Push y deploy: los hace el orquestador.** Confirmar que la migracion de M19 se aplique en produccion (RT-05).

### Casos de prueba de esta corrida
- PDF generados con QuestPDF + SkiaSharp (texto **rasterizado**, sin capa de texto, resumen bancario de mentira):
  `extracto-marzo-escaneado.pdf` (4 pag, 0,89 MB), `extracto-anual-escaneado-25p.pdf` (25 pag, 5,6 MB) y
  `extracto-marzo-con-texto.pdf` (4 pag, 28 KB, mismo contenido **con** capa de texto). No se copiaron al repo.
- Usuarios: `dira@qa.test` (Directora, org 1) y `dirb@qa.test` (org 4, para el IDOR), los dos con la contrasena comun
  de QA. Clientes 36 (Martinez SRL), 41 (Panaderia Norte) y uno creado y borrado para la corrida.
- Capturas en el scratchpad de la sesion: grilla clara 1440, ficha del escaneado oscura 1440, pasos de la cuenta
  claros 1440, grilla oscura 390.

### Reglas cross-proyecto validadas
- Ultima validacion de reglas cross-proyecto: 2026-09-25

# QA M18 - Portal del cliente del estudio (2026-09-24) - CERRADA

**VEREDICTO: aprobado con reparos. La frontera aguanta; lo que estaba roto era todo lo de alrededor.**
Los 12 criterios de aceptacion dan **PASS despues de 4 auto-fixes** (0 FAIL, 0 BLOCKED). Ninguno de los 4 defectos
era de aislamiento de datos: el barrido de 46 URLs del estudio con sesion de cliente real, el IDOR cliente-cliente
por Id directo y el barrido de 1.894 fragmentos del nucleo dieron **cero fugas de datos**. Lo que fallaba era el
**cromo** (el menu del estudio dibujado en los 403/404), la **cuenta propia** del cliente (contrasena y tema muertos),
la **funcion central del modulo** (el agente no podia leer un solo papel) y un **GET que escribia**.

Entrada: `1-analista-funcional.md` M18 (RF-M18-01..36, 12 CA), `docs/diseno-portal-cliente.md` (15 HU, seccion 9 con
los textos exactos), `5-implementador.md` M18 (DI-M18-A..I, 9 pruebas minimas). Commits `8e1eef4`..`0000506`.
**La migracion `PortalCliente` se aplico a la base de desarrollo en esta corrida** (llego sin aplicar).

**Linea base:** build 0 errores / 2 advertencias (preexistentes, analizadores xUnit en tests). `dotnet test`
**891/891** (una corrida dio 890/891 por el flaky conocido `LectorDocumentosTests.Extraccion_que_supera_el_tiempo`,
que paso aislado). `git status` limpio.

**Costo cero:** `Anthropic__Simulado=true` + `Anthropic__ApiKey` invalida de resguardo, confirmado en **cada** uno de
los 3 arranques por la linea *"Motor de agentes con MODELO SIMULADO ... el costo es cero"*; `grep -c anthropic.com`
sobre los logs = **0**. Ningun `appsettings` editado.

**Camino de verificacion:** el servidor MCP `playwright` **no respondio en esta sesion** - `browser_navigate` y hasta
`browser_close` devolvian *"Browser is already in use ... use --isolated"*, un lock de perfil que no se libero ni
matando los procesos ni borrando los `Singleton*`. Declarado y **caida al procedimiento alternativo de la
instruccion 33**: Playwright por Python (Chromium real, `ignore_https_errors`, cookie `crm-tema`) + `mysql` contra
`olvidata_agentes_dev`.

## Los 4 defectos (todos reproducidos, todos corregidos, un commit cada uno)

| Id | Sev | Que pasaba | Commit |
|---|---|---|---|
| **OLV-021** | major | Un cliente que pegaba una URL del estudio veia el **menu del estudio** (Inicio/Agentes/Tareas/Notificaciones, campana, "Mi perfil") en AccessDenied y en todo 404. Datos NO se filtraban (`/Notifications/GetRecent` daba 403): se filtraba el cromo, que es justo lo que prohibe el diseno seccion 9. Causa: `_Layout` decide con `EsMiembro && !EsStaff`, modismo pre-M18; al dejar `EsMiembro` de alcanzar al rol Cliente (DI-M18-A #1) la expresion se volvio false y lo mando a la rama del **staff**. | `974edb5` |
| **OLV-022** | major | El tapon `NoEsCliente` de la policy por defecto (DI-M18-A #2) cerro tambien los `[Authorize]` de `AccountController`: **"Cambiar contrasena"** (que el menu del cliente ofrece) daba acceso denegado y el **boton de tema** respondia 302 a AccessDenied, asi que el **tema oscuro era inalcanzable para un cliente**. | `aacfe0a` |
| **OLV-023** | **critical (funcional)** | **El bloque "Consultas" era inerte de punta a punta.** `ResolvedorHerramientas` arma bien la lista blanca de la `ConsultaCliente`, pero `HerramientaDocumentoBase.EjecutarAsync` - que M18 no toco, sigue como la dejo M16 - exige `TipoTarea.Trabajo` y devolvia "Herramienta no disponible para este agente." en el **100%** de las llamadas. La pantalla promete "la respuesta se apoya solo en tu carpeta" y el agente no podia leer un papel. **El agente redacta el fracaso en castellano**, asi que desde la pantalla no se ve nada raro: se detecta leyendo `PasosTarea` en la base. | `6df04a9` |
| **OLV-024** | major | "Pedirselo al cliente" era un enlace a `GET /Pedidos/Nuevo?propuesta=N`, y ese GET **creaba el pedido y marcaba la propuesta Aplicada**: escritura por GET sin antiforgery, alcanzable por prefetch, historial o un `img src` externo. Se detecto porque el estado cambio sin llegar a apretar Guardar. El resto del producto (M4b) ya iba por POST. | `1915a54` |

**Post-fix: build 0 errores, `dotnet test` `Con error: 0, Superado: 891, Omitido: 0, Total: 891`, exit 0.**

## Lo que se probo y aguanto

- **La frontera (CA-M18-01).** 46 URLs del estudio con sesion de cliente real: todas a AccessDenied o 404, **ninguna
  con un dato**. `/` y `/Home/Index` mandan a `/Portal`. Tras el fix 1, ninguna dibuja navegacion del estudio.
- **Cliente-cliente (CA-M18-02) y visibilidad (CA-M18-03).** Documento propio 200; documento de otro cliente, del
  estudio sin el interruptor, y de otra organizacion: **404, nunca 403** (no confirma que exista). El interruptor
  "Lo ve el cliente" muestra y oculta **en el acto**, en la lista y por Id directo. Lo que sube el cliente lo ve
  siempre (`Origen=Cliente`, `VisibleParaCliente=1`). Item de pedido ajeno **con archivo**: 404 "No existe.", sin
  escribir nada.
- **Fuga por el agente.** Barrido de **1.894 fragmentos** reales del nucleo + 13 marcadores tecnicos sobre las 6
  pantallas del cliente y las compartidas: **0 coincidencias**, con **control positivo validado** (11 fragmentos en
  `/Nucleo/Version/89` como staff). Se planto una clave en las instrucciones del agente y otra en una regla de
  empresa y se le pidio al agente, en castellano, que las revelara junto con los honorarios y los papeles de otro
  cliente: **ninguna llego al HTML**. Sin "Ver pasos", sin nombres de herramienta, sin JSON, sin un solo numero de
  costo. Tras el fix 3, el agente lista **solo** la carpeta de su cliente (47, 48, 49, 74) y ninguna del otro.
- **El cliente no aprueba nada (CA-M18-06).** Con el caso peligroso que pide DI-M18-G: aprobacion fabricada en nivel
  `Autor` sobre una tarea cuyo autor **es** el cliente. El cliente: `/Aprobaciones` denegado y todo POST rechazado.
  El **Director la ve y la puede resolver**. Un Empleado que no es autor ni Director, no.
- **Gasto (CA-M18-07).** Con el tope alcanzado no se crea la tarea ni se llama al modelo, y el texto de la seccion 9
  aparece (placeholder del cuadro en `Ver`, dialogo al enviar en `Index`), **sin un solo numero**.
- **Codigo de acceso (CA-M18-04).** Usado, vencido y revocado dan **el mismo mensaje, palabra por palabra**:
  *"Ese codigo no sirve. Pedile uno nuevo a tu estudio."* Hasheado SHA-256 del codigo sin guiones, vence a 7 dias,
  el contador por codigo sube y auto-revoca, y el limite por IP (5/15 min) frena. Tope de usuarios por cliente: frena
  con su mensaje y no crea el usuario.
- **Cortes (CA-M18-10, HU-M18-14).** "Cortar acceso" y la baja logica del `ClienteCartera` dejan al usuario afuera
  **en el siguiente request** de la sesion viva.
- **Portal apagado (CA-M18-11).** `/acceso` 404, sin card en la ficha, usuarios existentes afuera.
- **Propuesta del agente (CA-M18-08).** Mientras esta Pendiente **al cliente no le llega nada**; aplicarla dos veces
  da *"Esta propuesta ya se resolvio."* y no crea un segundo pedido.
- **Rechazo (RF-M18-22).** Sin motivo lo frena con el texto exacto de la seccion 9; con motivo, el cliente lo ve.
- **Visual (CA-M18-12).** 390 y 1440 px x claro y oscuro x 6 pantallas = 24 combinaciones: **sin scroll horizontal y
  sin errores de consola**.
- **Goldens (CA-M18-09).** 51/51 verdes, identicos.
- **Regresion del estudio.** Director, Empleado y SuperUsuario, controller por controller, antes y despues de los 4
  fixes: sin cambios. El tapon `NoEsCliente` **no rompio nada del lado del estudio** (`/Account/Perfil` y
  `/Account/CambiarPassword` siguen en 200 para los dos roles).

## Lo que NO se toco: tres decisiones de producto para Joaquin

1. **Las reglas de alcance Organizacion entran al contexto de la consulta del cliente.** Verificado en
   `TareasAgente.ReglasAplicadasJson`: las 5 reglas aplicadas eran `Alcance=Organizacion`, incluida una plantada a
   proposito que decia cuanto se le cobra al cliente. **RF-M18-27 y el diseno 3.3 dicen "reglas de alcance
   Cliente"**; DI-M18-F eligio a conciencia el mismo contexto que una tarea de trabajo para no mover los goldens. Es
   una contradiccion real entre el contrato y la implementacion, pero la decision esta documentada y razonada: **la
   define Joaquin, no QA.** Mitigado por las reglas de plataforma (56, 57, 58), que si se aplican.
2. **El agente lee toda la carpeta, no solo lo visible para el cliente.** Consecuencia del fix 3, y es lo que pide
   la seccion 3.3 ("su carpeta"). Pero significa que el agente puede leer - y citar - un papel interno que el cliente
   no puede abrir en el portal. Conviene decidirlo a sabiendas; la alternativa (acotar a `VisibleParaCliente ||
   Origen=Cliente`) seria **logica de negocio nueva** y por eso no se aplico.
3. **El simulador no tiene guion para `pedido_documentacion_proponer`.** La mitad "el agente propone" de CA-M18-08 no
   se puede ejercitar a costo cero; se verifico fabricando la propuesta. M14 dejo el estandar de que el simulado cubra
   lo nuevo (CA-M14-12) y aca quedo sin cubrir.

## Observaciones menores (no bloquean)

- **`MensajesPortalCliente.DemasiadosIntentos`** (*"Probaste muchas veces. Espera 15 minutos."*, texto de la seccion
  9) esta **escrito y no se usa en ningun lado**: al pasarse del limite se ve el mensaje generico del rate limiter del
  portal. Mismo patron que DEF-M14-3.
- **Contraste**: `.btn-outline-secondary` (3.81:1) y `.form-text` (3.12:1) quedan por debajo de 4.5:1 en los dos temas.
  **Preexistente y transversal**: son los grises por defecto de Bootstrap, sin override en el theme, usados en
  **101 vistas** incluido todo el lado del estudio. No es regresion de M18.
- **`confirmButtonColor` literal** (`#2b9de4`, `#ef4444`) en las vistas nuevas: contra la instruccion 38 seccion 6
  ("solo tokens"), pero **preexistente en 29 vistas** (SweetAlert no toma variables CSS facil).
- **`fw-semibold`** aparece una vez en `Views/Pedidos/Index.cshtml:107` y **es inerte** (no existe en el CSS servido,
  ya anotado en la corrida del 2026-09-21). Ahi no es el unico diferenciador, asi que es solo cosmetico.
- En las pantallas **compartidas** el menu del cliente sale con 4 opciones en vez de 5 (falta "Consultas"), porque
  `ViewBag.HayAgentesHabilitados` no lo puebla nadie fuera de `PortalClienteControllerBase`. Degradacion aceptable.
- El avatar del cliente usa la inicial del **email**, no la del nombre (dos clientes distintos mostraban "A").
- `/Pedidos` (lado estudio) sigue accesible con el portal apagado. Defendible - son datos ya cargados - pero conviene
  confirmarlo contra RF-M18-06.
- **Higiene del catalogo cross-proyecto:** `KOI-016` **titula dos defectos distintos** en
  `docs/qa/regresiones-manuales.yml` (guarda de privilegio fail-open, y cifra derivable por resta). Es de otro
  proyecto; se reporta, no se renumera.
- **Ajeno a M18:** durante la corrida aparecieron modificados 3 archivos de `nucleo/plataforma/` (configurador de
  reglas, su evaluacion y la instruccion 00) con ediciones de contenido de producto, a las 20:36. **No son de esta
  corrida** - QA no toca `nucleo/` - y quedaron **sin commitear y sin tocar**: son de otra sesion trabajando en
  paralelo en el mismo arbol.

## Reglas cross-proyecto validadas

- Ultima validacion de reglas cross-proyecto: 2026-09-24
- **Reglas nuevas desde la corrida anterior (2026-09-21), todas ejecutadas contra el sistema en esta corrida:**

| Regla | Origen | Resultado | Detalle |
|---|---|---|---|
| **Instruccion 38 completa** (diseno de pantallas del portal) - archivo **nuevo** del 2026-09-23, salido del rediseno de **este mismo producto** | `38-diseno-pantallas-portal.instructions.md` (`6930e63`) | **PASS con 2 observaciones menores** | Seccion 1: `ov-filtros` en los dos listados con filtros; **todas** las tablas con `ov-tabla-datos`; **cero** `position:sticky`. Seccion 4: sin accion duplicada encabezado+estado vacio (medido por visibilidad real, no por texto). Seccion 5: encabezados con chips; sin `v@Model`. Observaciones: colores literales en SweetAlert (seccion 6) y `fw-semibold` inerte, **los dos preexistentes**. |
| **KOI-015** - un helper de consulta compartido recibe el filtro como parametro y proyecta al final | `32-estandares-qa-implementador` (`6930e63`) | **PASS** | M18 no introdujo ningun helper que devuelva un `IQueryable` ya proyectado. **Se aplico la regla al propio auto-fix 3**: el predicado del tipo de tarea va **inline** en el `AnyAsync` y no por el metodo auxiliar, que EF no habria traducido. |
| **KOI-016** - guarda de privilegio fail-closed sobre la lista COMPLETA de roles | `32-estandares-qa-implementador` (`6930e63`) | **PASS** | `PermisoOrganizacionHandler` no usa `FirstOrDefault()` ni compara por desigualdad de string: `RequireMiembro`/`RequireDirector` resuelven contra `IPermisosOrganizacion` y **fallan cerrado** sin rol. `NoEsCliente` mira el rol crudo a proposito, para que un cliente **bloqueado** tampoco entre por la puerta de los miembros. Probado el caso del rol vacio: staff y SuperUsuario pasan, cliente no. |
| **KOI-017** - la ventana de una magnitud comparativa es un dato del modelo | `32-estandares-qa-implementador` (`a42294f`) | **N/A** | M18 no agrega ninguna pantalla que dibuje magnitudes lado a lado para compararse. El unico numero que el portal del cliente muestra es "0 de 2" de un pedido, que es un conteo de la misma unidad. |
| `34-integracion-afip-arca`, `35-pantalla-control-stock` | - | **N/A** | El producto no factura ni tiene control de stock. |

**Nota de metodo:** la regla 38 se valido **midiendo en el navegador**, no leyendo las vistas - que es lo que la
propia instruccion pide en la seccion 6 ("tres de los cambios se veian bien en el codigo y estaban rotos en
pantalla"). En esta corrida eso evito **dos falsos positivos** propios: la "accion duplicada" del estado vacio (los
dos botones nunca se ven juntos) y el "Director no ve la aprobacion" (el listado carga por DataTables y lo habia
leido antes de la XHR).

## Cobertura del catalogo cross-proyecto

Items nuevos creados en esta corrida: **OLV-021, OLV-022, OLV-023, OLV-024** (con `fix_aplicado` apuntando al commit
de cada uno). Del catalogo previo, lo que aplica a un portal con un tercero autenticado adentro del tenant se ejecuto
y dio verde: **PAT-017** (IDOR - el id sale de la sesion, nunca de la URL: **ningun metodo de
`IPortalClienteService` recibe el id del cliente**, verificado por codigo y por 6 intentos de IDOR reales),
**OLV-013..OLV-020** (aislamiento multi-tenant, `IgnoreQueryFilters` nombrado, listados sin 500, links de sidebar con
autorizacion real). El resto del catalogo es de otros stacks o de modulos que M18 no toca.

## Tecnicas que sirvieron (para la proxima corrida)

- **El barrido de fuga necesita su control positivo, si o si.** El primero dio "0 fugas" en el cliente **y 0 en el
  control**: estaba roto. El fragmento util sale de `ArtefactoVersiones` leyendo los bytes con `subprocess` (la
  consola de Windows mangla el UTF-8 **al imprimir**, pero el archivo sale bien: no confundir una cosa con la otra).
  `/Nucleo` no sirve de control - lista rubros -; el que sirve es `/Nucleo/Version/<id del prompt base>`.
- **Un `documentos_listar` que falla no se ve en pantalla.** El agente redacta el fracaso en castellano y parece una
  respuesta valida. Para cualquier herramienta nueva, leer `PasosTarea.ContenidoJson` y buscar `esError`.
- **Antes de dar por roto un listado, esperar la XHR de DataTables** (~2 s). Me dio un falso "el Director no ve la
  aprobacion".
- **`ControlGasto` suma `PasosTarea.CostoUsd`, no `EventosUso`.** Fabricar gasto insertando en `EventosUso` no mueve
  el limite; hay que tocar el costo de un paso.
- El mensaje de un tope puede estar en un **`placeholder`**, que `innerText` no ve; y el de un envio bloqueado, en un
  **SweetAlert** posterior al POST. Buscar los dos antes de reportar "no avisa".
- El hash del codigo de acceso es SHA-256 del codigo **sin guiones y en mayuscula**: sirve para fabricar codigos
  vencidos o revocados sin pasar por la pantalla.

---

# M7b — Tareas asignadas a personas y asistente del Director

QA etapa 6 ejecutada el 2026-09-16 (00:56–03:05 local) sobre `C:\Sistemas\Olvidata Agentes Multi-rubro`, portal local `https://localhost:7200` en Development con **modelo simulado** por variables de entorno del proceso (`Anthropic__Simulado=true`, `Anthropic__ApiKey` inválida, `MotorAgentes__IntervaloSondeoMilisegundos=1000`) en **3 arranques** (inicial; tras el auto-fix de OLV-011; tras el auto-fix de OLV-009). Advertencia "Motor de agentes con MODELO SIMULADO … el costo es cero" confirmada en los 3. **Costo cero:** 0 menciones a anthropic.com y 0 líneas ERR/FTL en los 3 logs (`portal-m7b*.log`). Definiciones aprobadas sin gate (autorización de Joaquín). Estado: **apto con observaciones** (2 defectos corregidos con auto-fix —1 major, 1 minor—, 2 observaciones reportadas; OLV-004 sigue abierto).

Camino de verificación: **librería Playwright desde Node** (Chromium real, headless, hasta 6 usuarios en paralelo), igual que en M5/M6/M7a, para poder correr flujos largos con lecturas a MySQL entre paso y paso: scripts `pw/m7b-f1..f12.js` (+ `m7b-lib.js` sobre `lib.js` / `m3lib.js` / `m7lib.js`) con sus `*-out.json` en el scratchpad; integridad por `mysqlsh`. El servidor MCP `playwright` estaba disponible en la sesión pero no se usó por ese motivo. Ningún PASS sin ejecución: lo que salió de tests y no de navegador está marcado como tal. **Falsos negativos del propio script diagnosticados y descartados** (no son defectos del sistema): (1) `L.get` con `redirect:'manual'` devuelve status 0 en los AccessDenied —hay que seguir la redirección para ver el 403—; (2) `fetch` truncado a 600 caracteres escondía los mensajes de validación; (3) el filtro de texto de la grilla se dispara en `keyup`, así que `page.fill` no lo activa (hay que usar `type`); (4) `page.click('button[type=submit]')` choca con el "Cerrar sesión" del encabezado (usar `#btnEmpezar`); (5) la primera medición de contraste no componía el alfa: `--ov-primary-subtle` en oscuro es `rgba(43,157,228,.15)` y daba un 2,72 falso en "Por qué"; (6) el consumo de M6 se calcula sobre `PasosTarea.CostoUsd` (con el simulador queda en 0), no sobre `TareasAgente.CostoUsd`: para probar el límite hay que sembrar el costo en el paso.

**Prompt del asistente:** publicado SOLO en `olvidata_agentes_dev` con la consola Admin (`evaluar 79 --aprobada "QA M7b en dev"` + `publicar 79`) y **revertido al terminar**, verificado por SQL: `ArtefactoVersiones #79 → Estado 1 (Borrador), PublicadaAt NULL` y 0 filas en `EvaluacionesVersion`. El texto del prompt no se tocó.

### Reglas cross-proyecto validadas
- Ultima validacion de reglas cross-proyecto: 2026-09-16
- **Sin reglas nuevas de otros proyectos desde la corrida de M7a (2026-09-15)**: `32-estandares-qa-implementador.instructions.md` solo cambió dos identificadores de patrones ya existentes (VSF-001 → VSF-003 y MH-001 → CRM-019), sin reglas nuevas; `docs/qa/regresiones-manuales.yml` no incorporó ítems posteriores a OLV-010 (creado por la propia corrida de M7a); las instructions de stack 34/35 no aplican (sin AFIP ni control de stock). Igual se ejecutó el barrido completo OLV-001..010 sobre las pantallas nuevas.
- Creados por esta corrida: **OLV-011** (atributo HTML5 del alta que bloquea la EDICIÓN de un registro cuyo valor persistido quedó fuera de rango, con mensaje de jquery-validate en inglés) y una **reincidencia registrada en OLV-009** (contador dentro del popup blanco de SweetAlert2).

### Cobertura de criterios de aceptación M7b
| CA | Resultado | Evidencia |
|---|---|---|
| CA-M7b-01 | PASS | La Directora crea "Revisar balance de Panadería Norte" para Laura con cliente Panadería Norte y chip "En una semana" (22/09): toast "Asignación creada.", fila #8 `Estado=1 AsignadaA=Laura Cliente=41 VenceEl=2026-09-22`, notificación #84 "Te asignaron una tarea — Directora A te asignó «…» (Panadería Norte), vence el 22/09/2026" con enlace `/Asignaciones/Detalle/8`, contador del menú de Laura en **1** y la fila en "Asignadas a mí". |
| CA-M7b-02 | PASS | `min` del input = 2026-09-15 (hoy argentino). POST con `VenceEl=2020-01-01` → "La fecha tiene que ser hoy o más adelante." y 0 filas creadas. Persona de la org 4 (dirb) y persona bloqueada (`Estado=2`) → "Esa persona ya no está activa en la empresa.", 0 filas. Empleado: sin "Nueva asignación" ni pestañas, GET `/Asignaciones/Nueva` y `/Asignaciones/Editar/8` → AccessDenied, **POST `/Asignaciones/Crear` → 403** y 0 filas. |
| CA-M7b-03 | PASS | Laura: Empezar → "Empezaste la tarea." (`Estado=2`); "Marcar como hecha" con nota → `Estado=3`, `NotaCierre="Cerré el balance, quedan 2 diferencias."` y notificación #85 a la Directora ("Laura Marketing marcó como hecha «…»: …"); Reabrir → "Reabriste la tarea." (`Estado=2`). |
| CA-M7b-04 | PASS | Detalle de Laura con botón primario "Pedírsela a un agente" → `/Agentes?asignacion=10` con `ov-alert info` "Estás resolviendo la tarea asignada «Armar el informe de alquileres». Elegí el agente…". Ejecutar precargado: pedido = título + descripción, cliente 41, aviso con "Ver la asignación". Enviar → toast "Tarea creada. La asignación quedó En curso.", tarea #156 con `TareaAsignadaId=10`, asignación **Pendiente → En curso en el mismo acto**, detalle de la tarea con "Asignación: «Armar el informe de alquileres»". Segunda tarea #157: card "Pedidos a agentes" con 2 tareas y la asignación **sigue En curso**; con las dos tareas Completadas (`Estado=4`) la asignación **no se cierra sola**. Cliente dado de baja: va sin cliente con `ov-alert warning` "El cliente «Panadería Norte» se dio de baja: la tarea va sin cliente.". |
| CA-M7b-05 | PASS | Martín (Empleado) abre por URL la asignación de Laura → **404**; `POST /Asignaciones/Listar` con `pestana=equipo` desde una sesión de Empleado → 0 filas; el Empleado que pide `?pestana=equipo` no ve ninguna pestaña (la barra solo se arma para Directores). |
| CA-M7b-06 | PASS | `UPDATE TareasAsignadas SET VenceEl = CURDATE() - INTERVAL 1 DAY`: segundo badge rojo "Vencida" junto al estado en el detalle y en la grilla; "Solo vencidas" devuelve exactamente esa fila y **queda persistido en Session** al recargar; la búsqueda global "vencida" también la encuentra. "Vencida" nunca se guarda (no hay columna). |
| CA-M7b-07 | PASS | Editar precargado (persona = Laura, cliente = 41, vence = 2026-09-22, título). Reasignar a Martín: toast "Asignación actualizada.", **dos avisos** (#86 a Martín "Te asignaron una tarea", #87 a Laura "Ya no tenés asignada una tarea — «…» ahora la tiene Martín Contable"), la grilla de Laura queda en "No tenés tareas asignadas." y su detalle le da **404**. |
| CA-M7b-08 | PASS | Cancelar con motivo → `Estado=4`, `MotivoCancelacion="Ya lo resolvió el estudio contable."`, notificación #88 a Martín, **detalle sin ninguna acción**; Empezar / Marcar hecha / Reabrir sobre una Cancelada → "Esta asignación ya no admite esa acción. Recargá la página." (estado intacto). Conflicto real con dos Directores editando a la vez (v1 = v2 = 1): el segundo recibe **"Otra persona cambió esta asignación. Recargá la página."** y gana el primero. |
| CA-M7b-09 | PASS | Con el prompt en Borrador: botón "Repartir trabajo conversando" **deshabilitado** con `title="Todavía no está disponible."`; `/Asistente` responde 200 con "Nueva conversación" deshabilitada y `/Asistente/Nueva` con textarea y botón deshabilitados; **POST `/Asistente/Iniciar` rechazado en el servidor** con el mismo mensaje y 0 tareas de tipo 3. |
| CA-M7b-10 | PASS | Publicada la versión en dev: "Repartí el trabajo de esta semana." → conversación #162 (chips "Repartí el trabajo de esta semana / ¿Quién tiene más pendientes? / Pedile a un agente que… / Reasigná lo vencido", contador 0/10.000), **dos tarjetas**: "Asignar a Director A Dos" y "Pedir a «inmo-agenda»", las dos Pendientes; **0 asignaciones con origen asistente antes de aplicar**. |
| CA-M7b-11 | PASS | Aplicar la de asignación → #11 con `Origen=2`, detalle con "Propuesta del asistente" y "Ver conversación", notificación #92 a la persona. Aplicar la de agente → tarea #163 **a nombre de la Directora que aplicó** y la tarjeta pasa a "Aplicada · Tarea #163 creada". Con el límite de M6 alcanzado (consumo sembrado 9,00 vs límite 1,00): la tarjeta queda **"No se pudo aplicar"** con "La empresa llegó al límite de gasto de septiembre (USD 1,00)…", 0 tareas creadas y botón **Reintentar**; restaurado el límite, Reintentar la aplica (tarea #174). Persona bloqueada: "No se pudo aplicar" + badge "La persona ya no está activa" + motivo "Esa persona ya no está activa en la empresa."; reactivada, Reintentar crea la asignación. |
| CA-M7b-12 | PASS | "Editar y aplicar" (solo en la de asignación) → `/Asignaciones/Nueva?propuesta=9` precargado (título, descripción, persona, `PropuestaId=9`, `ConversacionId=164`) con el aviso "Estás aplicando una propuesta del asistente…"; al guardar crea #12 con `Origen=2` y **vuelve a `/Tareas/Detalle/164`**. "Aplicar todas (2)" con confirmación "Se van a aplicar 2 propuestas…" → "2 aplicadas."; con una persona bloqueada → **"1 aplicada, 1 no se pudo aplicar."** y la fallida con su motivo. Descartar → `Estado=3`, tarjeta "Descartada" sin botones. |
| CA-M7b-13 | PASS (tests) | `Las_herramientas_leen_solo_lo_minimo_de_la_organizacion` y `Las_herramientas_del_asistente_se_niegan_fuera_de_su_conversacion` (244/244). No reproducible por navegador: el guion del simulador no expone el payload de las herramientas. |
| CA-M7b-14 | PASS | Empleado: sin botón, GET `/Asistente` → AccessDenied, conversación → **404**, `POST AplicarPropuesta` → **403**, `POST Iniciar` → **403**. Segundo Director: **ve** la conversación (200) y las tarjetas con Aplicar / Editar y aplicar / Descartar, **sin cuadro de seguimiento**, y `POST EnviarSeguimiento` → 403 "Solo quien pidió la tarea puede seguir esta conversación.". Dos Directores sobre la misma tarjeta: el segundo recibe **"Esta propuesta ya fue resuelta."** y se crea **una sola** asignación. |
| CA-M7b-15 | PASS (tests) | `Golden_formato_4_y_los_formatos_1_2_y_3_intactos` verde en las 4 corridas de la suite (244/244). |
| CA-M7b-16 | PASS con observación (OLV-004) | Mobile 390: 8 pantallas con `scrollWidth = innerWidth = 390`. Contraste con composición alfa correcta: **132 mediciones**, todo lo nuevo de M7b ≥ 4,5 en claro y oscuro (estado de asignación, badge "Vencida", tipo / texto / dónde / "Por qué" / nota / badges / motivo de fallo de las tarjetas, contador del menú, títulos, hints, `ov-datos`, avisos info y warning, grilla, card headers). Bajo 4,5 **solo tokens compartidos del design system (OLV-004, abierto)**: `.ov-page-head__desc` 4,31 en claro (en todas las pantallas del portal), `.nav-tabs .nav-link` 4,07 en claro (color por defecto de Bootstrap, primer uso de pestañas) y `btn-outline-secondary` 3,12 en oscuro (chips de vencimiento y del asistente). Estados siempre con ícono + texto. |

### Historias de usuario M7b
| HU | Resultado |
|---|---|
| El Director reparte trabajo entre personas y lo ve en un lugar | cumple (CA-01/05/07) |
| Cada uno ve lo suyo y lo mueve de estado | cumple (CA-03/05) |
| Saber qué está vencido | cumple (CA-06) |
| Resolver una tarea asignada con un agente | cumple (CA-04) |
| Reasignar, cambiar fecha y cancelar avisando | cumple (CA-07/08) |
| Repartir conversando con el asistente | cumple (CA-10/11/12) |
| Nada se crea sin confirmación humana | cumple (CA-10/11) |
| El asistente no se habilita hasta que el prompt esté aprobado | cumple (CA-09) |
| Cada rol ve y acciona lo que le corresponde | cumple (CA-02/05/14 y los POST forzados) |

### Máquina de estados M7b
| Transición | Resultado |
|---|---|
| — → Pendiente (formulario del Director) | PASS (#8, #10, #19, #20, #21) |
| — → Pendiente (propuesta del asistente aplicada, `Origen=2`) | PASS (#11, #12, #13, #14, #15) |
| Pendiente → En curso (Empezar, persona asignada) | PASS (#8) |
| Pendiente → En curso (tarea de agente creada, mismo guardado) | PASS (#10 con la tarea #156) |
| En curso → En curso (segunda tarea vinculada) | PASS (#10 con #157; no se cierra sola al completarse) |
| Pendiente → Hecha (sin pasar por En curso, nota vacía) | PASS (#19) |
| En curso → Hecha con nota (notifica a quien la creó) | PASS (#8, #10) |
| Hecha → En curso (Reabrir) | PASS (#8, #19) |
| Pendiente / En curso → Cancelada (Director, con motivo) | PASS (#8) |
| Pendiente / En curso → igual (Editar, incluye reasignar) | PASS (#8 con dos avisos; #20 avisa solo cuando cambia el vencimiento) |
| Hecha → Cancelar / Editar / Empezar (inválidas) | PASS — "Esta asignación ya no admite esa acción. Recargá la página." (#19) |
| Cancelada → Empezar / Marcar hecha / Reabrir (inválidas) | PASS — mismo mensaje, estado intacto (#8) |
| Versión vieja en cualquier acción (dos Directores) | PASS — "Otra persona cambió esta asignación. Recargá la página." |
| Propuesta: — → Pendiente (herramienta del asistente, sin `SaveChanges`) | PASS (#7 y #8 de la conversación #162) |
| Propuesta: Pendiente → Aplicada (Aplicar / Editar y aplicar / Aplicar todas) | PASS (#7, #9, #11, #12) |
| Propuesta: Pendiente → Descartada | PASS (#10) |
| Propuesta: Pendiente → No se pudo aplicar (persona inactiva / límite de gasto) | PASS (#17, #22) |
| Propuesta: No se pudo aplicar → Aplicada (Reintentar) | PASS (#17 → asignación #14; #22 → tarea #174) |
| Propuesta ya resuelta → aplicar de nuevo | PASS — "Esta propuesta ya fue resuelta." y una sola asignación |

### Checklists UI (25/26/32)
- **Listados**: Asignaciones con pestañas "Asignadas a mí" / "Del equipo" (solo Director), **7 filtros por columna visible** (Título, Cliente, Persona, Asignada por, Estado múltiple, Vence + "Solo vencidas", Actualizada) verificados uno por uno, persistidos en Session al volver, y "Limpiar filtros" que devuelve el total; búsqueda global que encuentra por título, cliente, persona, quien asignó, estado en palabras y "vencida"; vacíos con texto propio ("No tenés tareas asignadas." / "Todavía no hay tareas asignadas. Creá una o repartí el trabajo conversando."). Tareas: filtro Tipo con "Reparto de trabajo" solo para Director y staff. **0 respuestas 5xx y 0 errores de consola en 5 roles × 15 pantallas.**
- **Formulario**: dos cards ("¿Qué hay que hacer?" / "¿Quién y para cuándo?"), contador 0/4.000, Select2 con "Nombre · Área", **chips Hoy / Mañana / En una semana / Sin fecha** (verificados contra el día argentino del servidor) y hint "La persona recibe un aviso. Lo que escribas es una indicación: no le da permisos nuevos a nadie.".
- **Detalle**: dos columnas, acciones por AJAX según estado y rol, SweetAlert2 con "Nota (opcional)" y "Motivo (opcional)" con contador, card "Pedidos a agentes" y origen "Propuesta del asistente · Ver conversación".
- **Tarjetas del asistente**: tipo con ícono, título, texto recortado con "Ver la descripción completa", Cliente · Vence, "Por qué", nota fija "Nada se asigna ni se le pide a un agente hasta que lo apliques.", badges Aplicada / Descartada / No se pudo aplicar / "La persona ya no está activa", barra "Aplicar todas (N)" solo con 2 o más pendientes.
- **Mobile 390**: 8 pantallas sin scroll horizontal. **Contraste**: ver CA-M7b-16.
- **Ortografía y rótulos llanos**: barrido de las 8 pantallas nuevas sin tecnicismos (`subagente`, `tenant`, `artefacto`, `endpoint`, `ViewModel`, `payload`, `null`, `DTO`…); castellano rioplatense ("Contale", "Elegí", "Repartí", "Pedile"). Verificado además el ajuste **QA-M7a-02**: en una tarea de delegación **nueva** (#160 / #161) el resultado dice "El otro agente no pudo terminar: …" y no aparece "subagente" en ninguna pantalla; la palabra solo sobrevive en el texto **ya persistido** de la tarea #99 de la corrida de M7a (dato viejo, no se regenera).

### Regresión
- **Barrido por rol** (Directora, segundo Director, dos Empleados y staff) × 15 pantallas (M2 Miembros / Áreas / Clientes, M3 Reglas y alta, M3b y M7a Tareas, M4 Agentes y Mis agentes, M4b Configurador, M5 Documentos, M6 Consumo y Aprobaciones, M7b Asignaciones y Asistente, Inicio): **0 respuestas 5xx, 0 errores de consola**. Menú por rol correcto: los Empleados no ven Miembros ni Áreas; el staff ve su propio menú (Organizaciones y licencias, Núcleo IP, Uso y consumo, Auditoría) **sin Asignaciones**.
- **M3**: grilla de reglas con 14 filas y la card "Propuestas de agentes para revisar (2)" de M7a intacta.
- **M3b**: ajuste sobre una tarea terminada (#160) → "Mensaje enviado. El agente ya lo tiene en cola.", pasos 5 → 7 y la tarea vuelve a Completada.
- **M4b**: la conversación de configuración #33 sigue visible para la Directora con sus 2 tarjetas; el botón "Nueva conversación" del configurador aparece deshabilitado con "Todavía no está disponible." porque **en dev su prompt (versión #65) también quedó en Borrador** desde la corrida de M4b — dato de entorno, no defecto.
- **M5**: `/Documentos?clienteId=41` carga 15 de 19 documentos vivos con sus filtros (la barra de espacio no aparece porque no hay cuota configurada en dev).
- **M6**: Consumo del mes con el selector de período y el límite de la organización; límite de gasto probado de punta a punta contra el asistente y restaurado.
- **M7a**: filtro "Partes" (Ocultar / Mostrar), tarjeta de parte en la principal #160 y, en la parte #161, el aviso "Esta tarea es una parte de la tarea #160, pedida por «inmo-orquestador»" con "Volver a la tarea principal" y "Para seguir, escribile a la tarea principal".
- **Golden de hash** (formatos 1, 2, 3 y el nuevo 4) y aislamiento multi-tenant: verdes en las 4 corridas de la suite (244/244).

### Cobertura del catálogo cross-proyecto (M7b)
| id | aplica | resultado | acción |
|---|---|---|---|
| OLV-001 (Select2 blanco en oscuro) | sí | PASS | 4 combos del formulario y 9 de los filtros con fondo `rgb(30,41,59)` en oscuro; 0 blancos |
| OLV-002 (alertas oscuras sobre fondo oscuro) | sí | PASS | 5 alertas y badges de M7b en oscuro, todos ≥ 4,5 |
| OLV-003 (texto rojo con contraste bajo) | sí | PASS con observación | badge "Vencida" y `ov-alert danger` del motivo de fallo ≥ 4,5; en la página compartida de AccessDenied el "403" decorativo queda en 3,94 y el pie del layout en 3,75 (heredado, OLV-004) |
| OLV-004 (outline y enlaces sin variante por tema) | sí | **falla conocida (abierta)** | `btn-outline-secondary` 3,12 en oscuro (chips), `.ov-page-head__desc` 4,31 y `.nav-tabs .nav-link` 4,07 en claro; reportado, no se parchea desde QA (es del design system) |
| OLV-005 (campo opcional no anulable con validación en inglés) | sí | PASS | ningún campo **opcional** emite `data-val-required`; el único mensaje en inglés era el del `min` del input date → **OLV-011** (corregido). Queda `data-val-required="The Version field is required."` en el hidden `Version`, que es obligatorio de verdad y siempre viaja con valor: nunca se muestra |
| OLV-006 (búsqueda global que no ve una columna visible) | sí | PASS | encuentra por Título, Cliente, Persona, Asignada por, Estado ("Cancelada") y "vencida" |
| OLV-007 (`data-select2` que rompe Select2) | sí | PASS | 0 `select[data-select2]` y 0 errores de Select2 en las 6 pantallas nuevas |
| OLV-008 (partial con nombre corto → 500) | sí | PASS | `_TarjetasPropuestaTrabajo` y `_ScriptPropuestasTrabajo` se resuelven desde `Tareas`; 0 respuestas 500 en el barrido de 5 roles × 15 pantallas |
| OLV-009 (texto de tema dentro del popup blanco de SweetAlert2) | sí | **falla → auto-fix aplicado** | el contador 0/500 de "Marcar como hecha" y "Cancelar la asignación" daba 2,56 en oscuro; tras el fix, los 6 textos de los dos popups ≥ 4,5 |
| OLV-010 (acción destructiva que reusa la consulta de visibilidad) | sí | PASS | POST forzados de Empezar / MarcarHecha / Reabrir de un Empleado ajeno → **404**; Cancelar y Editar → **403**; **staff**: Detalle, Empezar, Cancelar y Crear → denegados y 0 filas tocadas; org 4 → 404. Ninguna acción cambió el estado |

### Cobertura de reglas nuevas/modificadas desde la última corrida
| Regla | Origen | Resultado | Acción |
|---|---|---|---|
| (ninguna nueva desde 2026-09-15) | `32-estandares-qa-implementador.instructions.md` | N/A | solo renombres de identificadores (VSF-001 → VSF-003, MH-001 → CRM-019); sin reglas nuevas |
| (ninguna nueva desde 2026-09-15) | `docs/qa/regresiones-manuales.yml` | N/A | el último ítem sigue siendo OLV-010, creado por la corrida de M7a |
| 34-integracion-afip-arca / 35-pantalla-control-stock | instructions de stack | N/A | el producto no factura ni maneja stock |

### Defectos M7b
| id | severidad | estado | detalle |
|---|---|---|---|
| **QA-M7b-01 (OLV-011)** | major | **corregido con auto-fix** | Editar una asignación **ya vencida** era imposible: el `min="hoy"` del `<input type="date">` hacía que jquery-validate bloqueara el submit con **"Please enter a value greater than or equal to 2026-09-15." (en inglés)** aunque la fecha no se tocara. El servidor **sí** acepta ese guardado (verificado por POST con el mismo `VenceEl` persistido): la regla de diseño D-M7-15 es "hoy o más adelante **solo cuando cambia**". Efecto: el Director no podía reasignar ni corregir una asignación vencida sin moverle además el vencimiento. Fix: `min` solo si el valor cargado no quedó en el pasado, `change` que repone `min=hoy` apenas la persona toca la fecha y `$.validator.messages.min` en castellano con el mismo texto del servidor |
| **QA-M7b-02 (OLV-009, reincidencia)** | minor | **corregido con auto-fix** | El contador "0 / 500" de los SweetAlert2 de "Marcar como hecha" y "Cancelar la asignación" usaba `.ov-field-hint` (token del tema): en tema oscuro quedaba `#94a3b8` sobre el popup blanco, contraste **2,56**. Mismo patrón que el contador del motivo de rechazo de M6. Fix: color explícito `#545454`, igual que el ya validado en `_ScriptAprobaciones` |
| QA-M7b-03 | minor | **reportado** | `LectorDocumentosTests.Extraccion_que_supera_el_tiempo_queda_como_no_se_pudo_leer` (M5) es **intermitente**: falló 2 de 5 corridas completas de la suite con la máquina cargada (portal + Playwright) y pasa siempre aislado y con la máquina libre (244/244 en 3 corridas seguidas). Riesgo de rojo espurio en una CI futura; conviene que el test no dependa del reloj de pared |
| QA-M7b-04 | minor | **reportado** | `SubagenteNoPermitido` ("…Consultá **subagentes_listar** y usá uno de sus códigos.") es un texto para el modelo, pero puede llegar a "Ver pasos" con la palabra "subagente" dentro del nombre de la herramienta. No se reprodujo en pantalla en esta corrida; queda como observación de D-M7-1 |
| OLV-004 | minor | **abierto (heredado)** | tokens compartidos del design system: `btn-outline-secondary` 3,12 en oscuro, `.ov-page-head__desc` 4,31 y `.nav-tabs .nav-link` 4,07 en claro, "403" y pie del layout 3,94 y 3,75 en oscuro. No se parchea desde QA: es una decisión del design system |

### Auto-fixes aplicados
| id | archivos | verificación post-parche |
|---|---|---|
| **OLV-011** | `src/OlvidataAgentes.Web/Views/Asignaciones/Form.cshtml` (`min` condicional + listener `change` + `$.validator.messages.min` en castellano) | Editar una asignación vencida cambiando solo el título **guarda** y deja `VenceEl` igual (2026-09-05); cambiar la fecha a 2020-01-01 → "La fecha tiene que ser hoy o más adelante." (castellano, ya no en inglés); el **alta** sigue con `min=hoy` y rechaza la fecha de ayer; los chips Hoy / Mañana / En una semana / Sin fecha siguen calculando bien. Build 0 errores, `dotnet test` **244/244** |
| **OLV-009** | `src/OlvidataAgentes.Web/Views/Asignaciones/_ScriptAcciones.cshtml` (contador con color fijo `#545454`) | los 6 textos de los popups de "Marcar como hecha" y "Cancelar la asignación" ≥ 4,5 en tema oscuro (7,57). Build 0 errores, `dotnet test` **244/244** |

Los dos auto-fixes son de vista, sin lógica de negocio nueva: el primero hace que el cliente replique la regla que el servidor ya aplicaba; el segundo repite una solución ya validada en M6.

### Riesgos de liberación M7b
- El prompt del asistente sigue siendo un **borrador sin evaluar** (PA-14): la calidad del reparto con el modelo real no está medida. Todo lo probado acá salió del guion del simulador, que siempre propone a la primera persona del equipo y al primer agente disponible. **Mitigación**: M8 (evaluación automática) antes de publicarlo en producción.
- "Vencida" se calcula con el día argentino y **cambia a la medianoche**: una asignación puede aparecer vencida sin que nadie la toque. Es lo definido, pero conviene que el resumen de sprint lo diga.
- Las notificaciones salen **después del commit y sin reintento** (RT-M6-06): si falla el envío, la asignación queda creada y la persona sin aviso.
- El asistente **no puede saber quién es el autor** (el `metadata.user_id` es opaco por el plan §5): puede proponerle trabajo al propio Director que está conversando.
- En dev quedaron en **Borrador** tanto el asistente (revertido a propósito) como el configurador de M4b y las 3 reglas de plataforma: quien retome el proyecto tiene que publicarlas para probar esos circuitos.

### Estado go/no-go M7b
**Apto con observaciones.** 16/16 criterios de aceptación en PASS (14 por navegador, 2 por tests), máquina de estados completa con sus transiciones inválidas, catálogo cross-proyecto OLV-001..010 barrido (1 falla corregida con auto-fix, 1 abierta heredada), regresión de M2 a M7a sin 5xx ni errores de consola y 244/244 en la suite. Quedan reportados 2 defectos menores (test intermitente y el texto `subagentes_listar` de una herramienta) y OLV-004 abierto. **Datos en dev**: asignaciones #8–#21 (1 Hecha, 13 Canceladas con motivo "Cierre de QA M7b"), conversaciones del asistente #162–#173 y tareas #156–#174, todas en estado terminal; 4 propuestas quedaron Pendientes a propósito (sobre conversaciones ya completadas: no le dan trabajo al worker). Límites (100,00 en las dos organizaciones), costos sembrados (0,00), usuarios (todos activos) y el cliente 41 (sin baja) restaurados y verificados por SQL. Prompt del asistente de vuelta en Borrador (verificado por SQL). Portal detenido. Sin commits; Mcp y Cli sin tocar.

## Historial de ajustes

### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **M07** — 1 bloques (2026-09-15 a 2026-09-15) → [`6-qa-M07.md`](historial/6-qa-M07.md)
- **M04** — 1 bloques (2026-09-14 a 2026-09-14) → [`6-qa-M04.md`](historial/6-qa-M04.md)
- **M03** — 2 bloques (2026-09-14 a 2026-09-14) → [`6-qa-M03.md`](historial/6-qa-M03.md)
