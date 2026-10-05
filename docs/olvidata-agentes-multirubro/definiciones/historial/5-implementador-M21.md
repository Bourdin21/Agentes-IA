<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/5-implementador.md el 2026-10-02 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - M21 (1 bloques archivados)

- M21 — Ojos, segunda mitad: el agente mira un PDF escaneado

---

# M21 — Ojos, segunda mitad: el agente mira un PDF escaneado

Estado: **implementado 2026-09-25; pendiente de QA; 1 commit local `2acfa4f`, sin push y sin deploy (los hace el
orquestador)**. Repo `C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `b551010` (M20). Entrada: análisis M21
(RF-M21-01..07, D-M21-a..d, CA-M21-01..05, R-M21-01/02, S-M21-01), el bloque M21 de `2-disenador-funcional.md` (la tabla
de «dónde se ve», D-M21-e y los cuatro riesgos de implementación) y el de `3-arquitecto-mvc.md` (mapa de componentes,
flujo punta a punta, R-T-04..06). Gate: definiciones 2 y 3 cerradas; presupuesto omitido (proyecto personal).

### Escaneo de reutilización
- **Otros proyectos: nada para traer.** Se confirmó lo del diseñador: `luciano-inmobiliaria/1-analista-funcional.md`
  §viabilidad documentó **esta misma vía técnica** (PDF nativo a Claude, sin pipeline de OCR) como respuesta a un cliente,
  pero nunca se implementó. Ningún otro proyecto del historial tiene visión sobre documentos.
- **Del propio repo, y es casi todo: M16 (ojos).** El camino entero ya estaba armado —`EstadoLecturaDocumento.SeMira`, la
  referencia en la base (nunca los bytes), la lectura del disco al armar la llamada, el tope por conversación y la guarda
  de cliente/tenant—, así que **lo único nuevo es que el archivo puede ser un PDF y que sale como bloque de documento**.
  No se duplicó una sola guarda: `ImagenesParaModelo` atiende los dos tipos con las mismas líneas.

### Qué se construyó
- **Application:** `Settings/DocumentosOptions.cs` (`MaxPaginasPdfParaMirar` 20, `MaxMbPdfParaMirar` 10,
  `MaxPdfsEnConversacion` 2, con el porqué verificado contra la doc de la API), `DTOs/DocumentosDtos.cs`
  (`SubidoSeMiraEscaneado`, `SubidoNoLegibleEscaneado`, `MotivoSeMiraEscaneado`, `MotivoEscaneadoLargo`,
  `MotivoEscaneadoPesado`, `PaginasDelEscaneado`, `Paginas`), `Motor/MensajesOjos.cs` (rótulo con páginas y las variantes
  de archivo), `Motor/IMotorAgentes.cs` (`ImagenParaMirar.EsPdf`), `Motor/ModeloConversacion.cs`
  (`BloqueImagenDocumento.EsPdf`, `BloqueImagenDatos.Paginas`), `Interfaces/IAlmacenDocumentos.cs`
  (`ResultadoLecturaDto.PaginasEscaneadas`), `Helpers/NombreDocumentoHelper.cs` (`TextoLectura` con tipo),
  `Helpers/MensajesPortalCliente.cs` (una palabra).
- **Infrastructure:** `Extractores/ExtractorPdf.cs` (la decisión de escaneado), `Documentos/ImagenesParaModelo.cs`
  (acepta PDF con su tope), `Motor/ProveedorModeloAnthropic.cs` (`MapearArchivoParaMirar` + `EsPdf`),
  `Motor/ProcesadorTareas.cs` (rehidratado con tope **por tipo**), `Documentos/HerramientasDocumentos.cs`
  (`documento_leer` sobre un escaneado, `LecturaParaAgente`, el paso «Miró …»), `Documentos/DocumentoCarteraService.cs`
  (mensaje de subida y el tipo en los DTO).
- **Web:** `Helpers/DocumentosTextos.cs` (tooltip), `Views/Documentos/Ver.cshtml` (el aviso del PDF escaneado, sin vista
  previa embebida) y tres claves en `appsettings.json`.
- **Tests:** `tests/OlvidataAgentes.Tests/OjosPdfTests.cs` (nuevo, 7 casos), 2 casos nuevos y 1 actualizado en
  `LectorDocumentosTests.cs`, 1 aserción de texto en `DocumentosTests.cs`.
- **Documentación del repo:** `docs/el-sistema-como-computadora.md` (la fila de Ojos, «Qué falta» y el bloque de M21) y
  `docs/manual-de-uso.md` (los estados al subir, el aviso de costo, el párrafo del escaneado y el «Qué no hace»).
- **Datos: ninguno. Sin entidades y sin migración.** `Mcp`, `Cli` y `distribuible/` sin tocar.

### Decisiones de implementación
- **DI-M21-A — El umbral es «cero caracteres», no el promedio.** El extractor ya tenía «menos de 20 caracteres por
  página → escaneado»; para **mirar** se exige que no se haya extraído **ni una letra** (RF-M21-01, D-M21-a). Un PDF con
  poco texto sigue por el camino barato, que cuesta como diez veces menos, y el sello OCR con dos palabras queda fuera de
  alcance a propósito (R-M21-02).
- **DI-M21-B — La cantidad de páginas viaja en `MotivoNoLegible`, la columna que ya existía.** Sin migración no hay dónde
  guardar un número, y las alternativas eran peores: `CantidadPartes` significa «partes de texto legible» (la ficha
  mostraría «12 partes» de un documento sin una sola letra) y volver a abrir el PDF para contar páginas es I/O en cada
  listado. `MensajesDocumentos.MotivoSeMiraEscaneado` es el único que escribe ese texto y `PaginasDelEscaneado` el único
  que lo lee, con un test de ida y vuelta.
- **DI-M21-C — El peso se decide al subir, además del guardarraíl del motor.** El tope de bytes del motor sigue
  existiendo, pero avisar recién en la tarea sería prometer algo que no se puede cumplir (D-M21-b). El extractor mira el
  largo del stream cuando se puede buscar y, si pasa, deja `NoLegible` con el motivo del peso.
- **DI-M21-D — `EsPdf` se agregó al final y con valor por defecto, y no se renombró nada.** `BloqueImagenDocumento`
  conserva su discriminador `imagen_documento` y `ImagenParaMirar` su nombre: hay filas en producción desde M16 cuyo JSON
  no tiene el campo y toma el default. Un test deserializa un JSON viejo de las dos formas (`ContenidoJson` e
  `ImagenesJson`) y verifica que sigue siendo una imagen.
- **DI-M21-E — El mapeo al SDK se extrajo a un método público (`MapearArchivoParaMirar`).** `MapearBloque` es privado y
  el proyecto de tests no ve los internos, así que R-T-05 («el tipo del SDK no está verificado») se cubre con un test que
  comprueba que un `application/pdf` sale como `BetaRequestDocumentBlock` y **no** como imagen. Es el mismo precedente que
  M16 usó con `MapearTipoImagen`. El tipo lo confirmó el compilador en el primer intento:
  `new BetaRequestDocumentBlock(new BetaRequestDocumentBlockSource(new BetaBase64PdfSource { Data = base64 }))`, sin
  `MediaType` (el del SDK ya es el del PDF).
- **DI-M21-F — Un arreglo chico fuera del alcance, a propósito.** `MensajesPortalCliente.LaMiraElAgente` decía «Tu estudio
  **la** puede ver», escrito cuando solo una imagen se miraba: con un PDF el portal del cliente se contradecía. Quedó
  neutro («lo puede ver»); el nombre del const se dejó como está para no tocar M18.

### Lo que el criterio decía distinto (resuelto a la vista, no en silencio)
- **RF-M21-06 y la tabla del diseñador no dicen lo mismo.** El requisito pide que el estado se lea «El agente lo mira
  (escaneado, N páginas)»; la tabla de diseño pide «El agente lo mira» + **tooltip** que nombre el escaneado. Se
  implementó el rótulo **«El agente lo mira (escaneado)»** y las páginas en el tooltip y en la ficha del documento: meter
  el número en el rótulo de la grilla pedía persistirlo como número, y eso pedía migración.
- **El «antes» del paso no era el que dice el diseño.** La tabla dice que el paso pasaba de «Miró «Frente.png»» a «Miró
  «Extracto marzo.pdf» (4 páginas)», pero M16 nunca escribió «Miró»: una imagen caía en el brazo de lectura del resumidor
  y el paso decía **«Leyó «Frente.png», parte 1»**. El brazo de «lo miró» se escribió acá y vale para los dos tipos de
  archivo (una imagen ahora también dice «Miró «Frente.png»»).
- **El tope de imágenes por conversación estaba mal documentado.** `docs/el-sistema-como-computadora.md` hablaba de
  `Memoria:MaxImagenesEnConversacion`; la clave vive en la sección `Documentos`. Quedó corregido de paso.
- **`MaxMbPdfParaMirar` = 10 MB puede quedar corto para un escaneado real, y eso lo dijo un archivo real, no una
  suposición.** Un PDF **solo de imágenes de 10 páginas** de un cliente mide **11,76 MB**: con el tope de RF-M21-01 queda
  «no puede leerlo» por peso, aunque **entra holgado en el tope de la API (32 MB)** y en el de páginas (10 ≤ 20). Se
  implementó el 10 que pide el criterio y **no se cambió por cuenta propia**, pero conviene decidirlo: subirlo a 20 MB es
  **una clave de `appsettings.json`**, sin código ni tests, y el costo lo sigue acotando el tope de páginas (lo que se paga
  son las páginas, no los megabytes). Queda para el gate de QA / Joaquín.

### Pruebas
- **`OjosPdfTests.cs` (7):** el camino entero (sube → «lo puede mirar (escaneado, 4 páginas)» → el agente lo pide → llega
  el archivo en base64 con `application/pdf`, el rótulo con las páginas, el bloque de documento del SDK, y en la base solo
  la referencia con `EsPdf`, sin el base64, más el paso «Miró «Extracto marzo.pdf» (4 páginas)»); el escaneado por encima
  del tope (mensaje de subida con el motivo exacto, `documento_leer` que falla diciéndolo, `ImagenesParaModelo` que
  devuelve null y la tarea **Completada**); el de otro cliente y el de otra organización; el **tope por tipo** con
  escaneados y fotos mezclados (R-T-04); el JSON viejo de M16 sin `esPdf`; el archivo que ya no está en disco contado en
  palabras con la tarea terminando bien; y los textos del portal y del modelo comparados entre sí.
- **`LectorDocumentosTests.cs`:** el PDF con texto sigue `Legible` con una parte por página (el camino barato intacto), el
  escaneado de 1 y de 4 páginas queda `SeMira` con el motivo en palabras, el que pasa el tope de páginas y el que pasa el
  de peso quedan `NoLegible` con su motivo, y el ida y vuelta de `PaginasDelEscaneado`.
- **Cada test nuevo verificado en rojo** antes de darlo por bueno: apagar la rama del extractor → **7 rojos**; contar el
  tope de la conversación junto (sin separar tipos) y mandar el PDF como bloque de imagen → **2 rojos**. Código
  restaurado antes de seguir.

### Evidencia
- `dotnet build OlvidataAgentes.slnx`: **0 Errores**, 2 advertencias (las dos preexistentes de xUnit en tests de M18).
- `dotnet test tests/OlvidataAgentes.Tests` **medido sin pipe** (`> archivo 2>&1` y el código de salida): línea base
  **985**; final **Con error: 0, Superado: 994, Omitido: 0, Total: 994** (+9), exit 0.
- **Los 5 goldens de contexto, sin un byte de cambio:** `git status` de `tests/OlvidataAgentes.Tests/Goldens/` vacío. Era
  lo esperado (R-T-06): M21 no toca el prompt de sistema.
- **Los tests de M16 (`OjosTests.cs`) quedaron verdes sin tocarlos:** no figuran en el commit. Ningún texto de imagen
  cambió una letra; las firmas de `MensajesOjos` crecieron con parámetros opcionales justamente para eso.
- **Dos tests ajenos sí cambiaron, con motivo:** `LectorDocumentosTests` afirmaba que un escaneado de una página es
  `NoLegible` (justo el comportamiento que M21 cambia) y `DocumentosTests` afirmaba el texto «El agente la mira» (que la
  tabla del diseñador manda cambiar por «lo mira»). Son las dos aserciones que el módulo viene a cambiar.
- **Verificado contra PDF REALES, no solo sintéticos** (18 archivos de clientes que ya están en esta máquina, leídos en
  el lugar y **sin copiar ninguno al repo**): los 5 extractos del Credicoop de `contadores-bma` y un extracto real de otro
  cliente **siguen `LegibleEnParte`** con su página 8 sin texto, o sea que **el camino barato no se movió en datos reales**;
  un PDF real de una página sin texto que estaba guardado como documento de la demo **pasó a `SeMira`** (antes no existía
  para la tarea); trece PDF con texto quedaron `Legible`, incluido un brochure de 9 páginas con apenas 1.943 caracteres,
  que es exactamente el borde de D-M21-a (tiene algo de texto → camino barato). El hallazgo está abajo.

### Lo que quedó afuera
- **El PDF mixto** (algunas páginas con texto y otras escaneadas) sigue `LegibleEnParte` y sus páginas sin texto no se
  miran: D-M21-a lo deja fuera y duplicaría los caminos.
- **Sin vista previa embebida del PDF** en la pantalla del documento (D-M21-e): pediría una acción nueva que sirva el
  binario `inline` y el navegador ya abre el PDF descargado. El botón Descargar alcanza.
- **`MaxImagenesPorLectura` sigue siendo de las imágenes:** una llamada a `documento_leer` trae un archivo, igual que en
  M16, así que no hizo falta un tope propio por lectura para los PDF.
- Sin push y sin deploy: los hace el orquestador después de QA.
