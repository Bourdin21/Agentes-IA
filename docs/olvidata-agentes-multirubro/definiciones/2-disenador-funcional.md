# Memoria - Disenador funcional

## Proyecto: olvidata-agentes-multirubro
## Ultima actualizacion: 2026-09-15

## Definiciones vigentes

# M5 — Workspace por cliente de cartera

Estado: **aprobado sin gate por autorización de Joaquín 2026-09-14** (decisiones D-M5-1..14 tomadas con la opción recomendada y documentadas como hipótesis). Entrada: `1-analista-funcional.md` M5 (P1–P14 tomadas sin gate). Criterio transversal: lenguaje llano, esconder complejidad (D-M3-8..12); tema oscuro con tokens (lecciones OLV-001..004).

### M5-0. Escaneo de reutilizacion
| Fuente | Qué hay | Decisión |
|---|---|---|
| Catálogo PAT-002 — vinosefue `AdjuntoService` (verificado: `C:\Sistemas\vino-y-se-fue\VinoSeFue.Infrastructure\Services\AdjuntoService.cs`, `ComprasController` con `ExtensionesPermitidas` y `MaxFileSize`) | Subida de un adjunto por formulario, lista de extensiones, 10 MB | **Reutilizar el criterio** de validación en servidor y el ViewModel con `IFormFile`; **no** su almacenamiento (`wwwroot/uploads`, público). Catálogo corregido. |
| ganaderia (`docs/ganaderia/definiciones/2-disenador-funcional.md` y `3-arquitecto-mvc.md`: `_UploaderComprobante`, validación de tamaño/extensión antes del POST, endpoint autenticado de descarga) | Uploader con validación en cliente + descarga protegida | **Reutilizar el diseño** del uploader (validación previa en el navegador, mensaje por archivo) y la descarga solo por endpoint. |
| audifonos-bariloche / cma-centro-medico (`AdjuntoViewModel`: tipo, fecha, subido por) | Lista de adjuntos por registro | **Reutilizar** columnas de la lista. |
| Template M2 — `Cartera/Detalle` (cards `ov-detail-grid`), grilla DataTables con filtros por columna y Session (P-05), bajas AJAX PAT-015 | Ficha y listados | **Reutilizar**: card "Documentos" en la ficha, grilla y baja con SweetAlert2. |
| Template M3 — `Agentes/Ejecutar` con "Esto es lo que el agente va a tener en cuenta" (PAT-028) | Vista previa recalculada al cambiar cliente | **Extender** con sección de documentos. |
| Template M3b — `_Conversacion`, `_CuadroSeguimiento`, `_PasosTurno` (PAT-029) | Conversación y ajustes | **Extender** con chips de adjuntos y botón Adjuntar; rótulos llanos en Ver pasos (PA-12 parcial). |
| Template M4 — Select2 con plantillas en modales de sugerencias | Selección múltiple | **Reutilizar** para elegir documentos. |
| Catálogo y demás proyectos | Sin workspace de documentos legible por agentes IA (partes, estado de lectura, herramientas) | **Diseño nuevo** → PAT-033. |

### M5-1. Alcance funcional resumido
Cada cliente de cartera tiene sus documentos: se suben desde la ficha (uno o varios), se listan, se ven (datos, lo que el agente puede leer por partes, imagen), se descargan, se renombran y se dan de baja. Al subir se indica en palabras si el agente lo puede leer. Al pedir una tarea sobre un cliente o en un ajuste se pueden adjuntar documentos; la vista previa muestra qué documentos va a poder leer el agente y la conversación muestra los adjuntos como chips. Los pasos de lectura se explican en lenguaje llano. El staff ve espacio y metadatos.

### Decisiones de diseño M5 (hipótesis tomadas sin gate, autorización 2026-09-14)
- **D-M5-1 Entrada desde la ficha del cliente.** Card **"Documentos"** en `Cartera/Detalle`, debajo de "Datos del cliente": últimos 5 documentos (ícono de tipo · nombre · estado de lectura · fecha), botón **Subir documentos** y enlace **Ver todos (N)**. Sin ítem nuevo en el menú (los documentos siempre son "de un cliente"). En la grilla de Cartera no se agrega columna.
- **D-M5-2 Pantalla propia por cliente** "Documentos de «Cliente»" con zona de subida arriba y grilla abajo; breadcrumb Cartera › Cliente › Documentos.
- **D-M5-3 Subida en cola, un archivo por envío.** Se pueden soltar o elegir varios; el navegador valida tipo y tamaño antes de enviar y los sube de a uno, con una fila por archivo (nombre · barra de progreso · resultado). Al terminar, toast resumen ("3 documentos subidos, 1 no se pudo subir") y la grilla se recarga conservando la página.
- **D-M5-4 Estado de lectura con ícono + texto** (nunca solo color): ✔ "El agente lo puede leer" · ◐ "El agente lee solo una parte" · 👁‍🗨 "El agente no puede leerlo" (tooltip: "Es una imagen o un PDF escaneado") · ⚠ "No se pudo leer el archivo" (tooltip con el motivo).
- **D-M5-5 Ver documento** muestra datos y **"Lo que el agente puede leer"**: una parte a la vez con rótulo ("Página 3 de 12", "Hoja «Ventas», filas 201–400"), botones Anterior/Siguiente y selector de parte. Imágenes: vista dentro del portal. PDF/Word/Excel: sin visor embebido; botón **Descargar**.
- **D-M5-6 Renombrar** con SweetAlert2: input con el nombre sin extensión y la extensión fija a la derecha (".pdf"), sin salir de la página.
- **D-M5-7 Dar de baja** con SweetAlert2 (PAT-015): "¿Dar de baja «Contrato 2026.pdf»? Se borra el archivo del servidor. Las tareas que ya lo leyeron conservan lo que leyeron." Solo visible para el Director o quien lo subió.
- **D-M5-8 Adjuntar al pedir una tarea.** En `Agentes/Ejecutar`, al elegir un cliente aparece el campo **"Documentos para esta tarea"** (Select2 múltiple con ícono, nombre y aviso si no es legible) + enlace **"Subir un documento"** que abre el modal de subida para ese cliente y deja el documento elegido. Sin cliente, el campo no aparece. Cambiar de cliente vacía la selección con aviso "Se quitaron los documentos del cliente anterior."
- **D-M5-9 Adjuntar en un ajuste.** En `_CuadroSeguimiento`, botón **Adjuntar** (clip) a la izquierda de Enviar, solo si la tarea tiene cliente: abre el modal **"Adjuntar documentos"** con buscador, casillas por documento (legibles primero) y "Subir un documento"; los elegidos quedan como chips removibles sobre el cuadro de texto.
- **D-M5-10 Chips en la conversación.** Bajo el texto del pedido o ajuste: "📎 Contrato 2026.pdf" (enlace a Ver si sigue vigente) o "📎 Contrato 2026.pdf (dado de baja)" sin enlace. El nombre es el que tenía al adjuntarlo.
- **D-M5-11 Vista previa de documentos.** En "Esto es lo que el agente va a tener en cuenta", sección **"Documentos"**: "Adjuntaste: …" (con aviso por los no legibles) y "Además puede consultar N documentos de este cliente" (+ "M no los puede leer: imágenes o escaneados"). Sin cliente: "Elegí un cliente para que el agente pueda consultar sus documentos."
- **D-M5-12 Ver pasos en lenguaje llano** para las herramientas de documentos: "Miró la lista de documentos del cliente" · "Leyó «Contrato 2026.pdf», páginas 1 a 5" · "Buscó «vencimiento» en los documentos (3 resultados)" · error: "No pudo leer «…»: ya no está disponible". El contenido leído queda plegado bajo "Ver lo que leyó" (texto, no JSON). El resto de las herramientas sigue con el formato de M1 (PA-12).
- **D-M5-13 Espacio usado solo para el Director**: barra en el encabezado de la pantalla de documentos "Espacio de documentos de la empresa: 320 MB de 1 GB" (ámbar desde 80 %, roja desde 95 %). El Empleado ve el límite solo cuando una subida lo supera.
- **D-M5-14 Staff en el backoffice.** En `Clientes/Details` (organización), card "Documentos" con cantidad y espacio; enlace **Ver documentos** a una grilla de solo lectura con metadatos (cliente, nombre, tipo, tamaño, lectura, subido por, fecha). Sin enlaces a ver ni descargar.

### Flujos de pantalla acordados M5

**P-M5-01 Ficha del cliente** (ajuste de `Cartera/Detalle`)
- Card "Documentos" (D-M5-1). Vacío: "Todavía no hay documentos. Subí contratos, planillas o notas y los agentes los van a poder consultar en las tareas de este cliente." + **Subir documentos**.
- **Subir documentos** abre P-M5-04 (modo subir) y al cerrar refresca la card.

**P-M5-02 Documentos de «Cliente»** (`Documentos/Index?clienteId=`)
- Encabezado: título "Documentos de Panadería Norte" · descripción "Los agentes pueden consultarlos en las tareas de este cliente." · acciones: Volver a la ficha. Director: barra de espacio (D-M5-13).
- Card **Subir**: zona punteada "Arrastrá archivos acá o **elegí archivos**" · hint "PDF, Word (.docx), Excel (.xlsx), CSV, texto (.txt, .md) e imágenes (JPG, PNG, WEBP). Hasta 20 MB por archivo." · cola de subida (D-M5-3).
- Grilla DataTables: Tipo (ícono + texto) · Nombre · Lectura (D-M5-4) · Partes · Tamaño · Subido por · Fecha · acciones (**Ver**, **Descargar**, menú ⋯: Renombrar, Dar de baja). Filtros por columna: Nombre (texto), Tipo (Select2), Lectura (Select2), Subido por (Select2), Fecha (rango). Orden inicial Fecha desc. Session y "Limpiar filtros" (LP-004). Mobile: Tipo + Nombre + acciones; resto en detalle expandible.
- Vacío: "Todavía no hay documentos de este cliente."

**P-M5-03 Ver documento** (`Documentos/Ver/{id}`)
- Breadcrumb Cartera › Cliente › Documentos › Nombre.
- Encabezado: nombre · acciones **Descargar** (primario), Renombrar, Dar de baja (según permiso).
- Card **Datos**: Tipo · Tamaño · Subido por · Fecha · Lectura (D-M5-4) · si aplica `ov-alert warning` "El documento es muy largo: el agente puede leer hasta la parte N de M." o `ov-alert info` "El agente no puede leer este documento: es una imagen o un PDF escaneado."
- Card **Lo que el agente puede leer** (si hay partes): rótulo de la parte, texto en bloque monoespaciado con saltos (`pre-wrap`, alto máx. 60 vh con scroll), Anterior / selector "Parte 3 de 12" / Siguiente (AJAX, sin recargar).
- Card **Vista** (solo imágenes): imagen ajustada al ancho.

**P-M5-04 Modal de documentos** (parcial compartido; modos *subir* y *elegir*)
- Modo subir (desde ficha, Index, Ejecutar): zona de subida + cola; botón Cerrar.
- Modo elegir (desde ajuste): buscador · lista con casillas (ícono · nombre · lectura) · "Subir un documento" (sube y lo marca) · contador "2 elegidos (máx. 10)" · botones **Listo** / Cancelar.

**P-M5-05 Agentes → Ejecutar** (ajuste): campo de D-M5-8 debajo de "Cliente"; la vista previa se recalcula al cambiar cliente **o** documentos (D-M5-11). Error del servicio (documento dado de baja entre la carga y el envío): resumen de validación "Uno de los documentos ya no está disponible. Revisá los adjuntos." y la selección conserva los vigentes.

**P-M5-06 Detalle de tarea** (ajustes): chips en pedido y ajustes (D-M5-10); botón Adjuntar y chips en el cuadro de seguimiento (D-M5-9); Ver pasos con rótulos llanos (D-M5-12).

**P-M5-07 Backoffice — organización** (ajuste de `Clientes/Details`): card de D-M5-14.

**P-M5-08 Backoffice — Documentos de la organización** (staff): encabezado "Documentos de «Organización»" · barra de espacio · grilla de solo lectura Cliente · Nombre · Tipo · Tamaño · Lectura · Subido por · Fecha, filtros por columna y Session.

### ViewModels definidos M5
| ViewModel | Campos y validaciones |
|---|---|
| `DocumentoListItem` (JSON) | `id, tipo, tipoTexto, nombre, lectura, lecturaTexto, partes, tamano` ("1,2 MB"), `subidoPor, fecha` (dd/MM/yyyy HH:mm AR), `puedeDarDeBaja, version` |
| `DocumentosClienteViewModel` | `ClienteCarteraId, ClienteNombre, PuedeVerEspacio, EspacioUsadoBytes, EspacioMaximoBytes, MaxMbPorArchivo, ExtensionesPermitidas` (para `accept` y validación en cliente), `Filtros` (Session) |
| `SubirDocumentoViewModel` | `ClienteCarteraId` [Required] · `Archivo` (`IFormFile`) [Required "Elegí un archivo."] — el resto se valida en el servicio |
| `SubidaDocumentoResultado` (JSON) | `ok, id?, nombre?, lectura?, mensaje, nivel` (success / warning / error) |
| `RenombrarDocumentoViewModel` | `Id` · `NombreSinExtension` [Required "Escribí un nombre."] [StringLength 150 con la extensión: "El nombre admite hasta 150 caracteres."] · `Version` |
| `DocumentoDetalleViewModel` | `Id, ClienteCarteraId, ClienteNombre, Nombre, Extension, TipoTexto, Tamano, Lectura, LecturaTexto, MotivoNoLegible?, CantidadPartes, PartesLegibles, TextoRecortado, SubidoPor, Fecha, EsImagen, PuedeDarDeBaja, Version, Parte` (`DocumentoParteViewModel`: `Numero, Rotulo, Texto, Anterior?, Siguiente?`) |
| `DocumentoOpcion` (JSON Select2/modal) | `id, nombre, tipo, legible, lecturaTexto` |
| `EjecutarAgenteViewModel` (ajuste) | + `DocumentoIds` (List<int>, máx. 10: "Podés adjuntar hasta 10 documentos por mensaje.") · `VistaPrevia` + `Documentos` (`DocumentosVistaPreviaViewModel`: `Adjuntos[] {nombre, legible}`, `OtrosLegibles`, `NoLegibles`, `TieneCliente`) |
| `SeguimientoViewModel` (ajuste M3b) | + `DocumentoIds` (máx. 10) |
| `MensajePersona` (ajuste de turno) | + `Adjuntos[] {DocumentoId, Nombre, Disponible}` |
| `PasoVisible` (ajuste) | + `Resumen?` (rótulo llano, D-M5-12) y `ContenidoLegible?` (texto leído sin JSON) |
| `DocumentoStaffListItem` (JSON) | `cliente, nombre, tipoTexto, tamano, lecturaTexto, subidoPor, fecha` |

### Validaciones de UI M5
| Caso | Mensaje |
|---|---|
| Sin archivo | "Elegí un archivo." |
| Extensión no permitida (cliente y servidor) | "Este tipo de archivo no está permitido. Podés subir PDF, Word (.docx), Excel (.xlsx), CSV, texto (.txt, .md) e imágenes (JPG, PNG, WEBP)." |
| Word/Excel viejo (.doc/.xls) | "Los formatos .doc y .xls no están permitidos. Guardalo como .docx o .xlsx." |
| Con macros (.docm/.xlsm o contenido con macros) | "Los archivos con macros no están permitidos. Guardalo como .docx o .xlsx sin macros." |
| Tamaño | "El archivo supera el máximo de 20 MB." |
| Vacío | "El archivo está vacío." |
| Contenido no corresponde al tipo | "El archivo no es un .pdf válido." (según extensión) |
| Archivo comprimido sospechoso | "No se pudo procesar el archivo: su contenido es demasiado grande al abrirlo." |
| Espacio de la organización | "La empresa llegó al espacio máximo para documentos (1 GB). Dá de baja documentos que ya no uses." |
| Máximo por cliente | "Este cliente ya tiene 200 documentos. Dá de baja alguno para subir otro." |
| Contenido duplicado | "Este archivo ya está cargado para este cliente como «Contrato 2026.pdf»." |
| Nombre repetido (subida) | toast info "Ya había un documento con ese nombre: se guardó como «Contrato 2026 (2).pdf»." |
| Subido legible / parcial / no legible / no se pudo leer | "Documento subido. El agente lo puede leer." · warning "Documento subido. Es muy largo: el agente va a leer hasta la parte N." · warning "Documento subido, pero el agente no puede leer su contenido (es una imagen o un PDF escaneado)." · warning "Documento subido, pero no se pudo leer su contenido: puede tener contraseña o estar dañado." |
| Renombrar: vacío / largo / caracteres | "Escribí un nombre." · "El nombre admite hasta 150 caracteres." · "El nombre no puede tener estos caracteres: \ / : * ? \" < > |" |
| Renombrar: repetido / conflicto | "Ya hay un documento con ese nombre para este cliente." · "Otra persona cambió o dio de baja este documento. Recargá la página." |
| Baja sin permiso | 403 JSON "Solo un Director o quien subió el documento puede darlo de baja." |
| OK | "Documento renombrado." · "Documento dado de baja." |
| Adjuntos: más de 10 / sin cliente / no vigente / de otro cliente | "Podés adjuntar hasta 10 documentos por mensaje." · "Para adjuntar documentos elegí un cliente." · "Uno de los documentos ya no está disponible. Revisá los adjuntos." · "Uno de los documentos no es de este cliente." |
| Documento de otra organización o inexistente | 404 |

### Maquina de estados M5 (documento)
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| — | Subir | Vigente (lectura: Legible / Legible en parte / No legible / No se pudo leer) | miembro de la organización; cliente vigente; tipo, contenido, tamaño, espacio, máximo por cliente, sin duplicado | guarda archivo, texto por partes y registro; nombre único con sufijo | mensajes de validación; nada queda guardado |
| Vigente | Renombrar | Vigente | miembro; nombre válido y único; versión leída | cambia nombre (chips de tareas conservan el anterior) | repetido / conflicto |
| Vigente | Adjuntar a pedido o ajuste | Vigente | autor de la tarea; documento del cliente de la tarea; ≤ 10 | registra adjunto con nombre del momento | no vigente / otro cliente / máximo |
| Vigente | Leer / buscar (agente) | Vigente | tarea de trabajo con ese cliente | devuelve partes rotuladas como información | documento no disponible → error al agente |
| Vigente | Dar de baja | Dado de baja | Director, o miembro que lo subió; versión | baja lógica, borra archivo y texto, libera espacio | 403 / conflicto |
| Dado de baja | cualquier acción | — | — | — | 404 (portal) · "ya no está disponible" (agente) |

La tarea y la conversación no cambian de estados (M1/M3b).

### Permisos por pantalla / accion M5
| Acción | Director | Empleado (autor del doc) | Empleado (otro) | Staff |
|---|:---:|:---:|:---:|:---:|
| P-M5-01/02/03 ver, filtrar, ver partes, ver imagen, descargar | ✅ | ✅ | ✅ | ❌ (portal: 403) |
| Subir (P-M5-02/04/05/06) | ✅ | ✅ | ✅ | ❌ |
| Renombrar | ✅ | ✅ | ✅ | ❌ |
| Dar de baja | ✅ | ✅ | 403 | ❌ |
| Barra de espacio (D-M5-13) | ✅ | — | — | ✅ (P-M5-07/08) |
| Adjuntar en Ejecutar / ajuste | ✅ sus tareas | ✅ sus tareas | ✅ sus tareas | ❌ |
| Chips y Ver pasos en tareas | según visibilidad M2 | según M2 | según M2 | ✅ lectura |
| P-M5-07/08 metadatos de la organización | — | — | — | ✅ |

### Contratos funcionales para Services M5
| Contrato | Operaciones | Reglas |
|---|---|---|
| Documentos del cliente | listar (filtros, orden, paginado) · últimos N para la ficha · obtener detalle · obtener parte · subir · renombrar · dar de baja · abrir archivo (descarga / imagen) · opciones para adjuntar · espacio usado | RF-M5-01..09, 14, 15, 17; D-M5-3, 13 |
| Lectura de archivos | validar tipo por contenido · extraer partes con rótulos · determinar estado de lectura y recorte | RF-M5-03, 04, 08, 09 |
| Almacén | guardar fuera de la carpeta pública por organización y cliente · abrir · eliminar | RF-M5-07, 14 |
| Herramientas de documentos | listar documentos del cliente de la tarea · leer partes (máx. 10 / 40.000 caracteres) · buscar texto (máx. 20) | RF-M5-10, 11; acotadas por la tarea |
| Tareas (extensión) | crear con adjuntos · ajuste con adjuntos · vista previa de documentos · detalle con adjuntos por mensaje y rótulos llanos de pasos | RF-M5-12, 13, 16; D-M5-8..12 |
| Motor (extensión) | ofrecer herramientas de documentos en tareas de trabajo con cliente · informar adjuntos al modelo por mensaje | RF-M5-10, 12 |
| Staff | resumen de espacio por organización · listar metadatos | RF-M5-18; D-M5-14 |

### M5-6. Impacto funcional por capa
- **Presentación:** card en la ficha, pantalla de documentos con subida en cola, ver documento por partes, modal compartido subir/elegir, campo de adjuntos y vista previa en Ejecutar, chips y botón Adjuntar en la conversación, Ver pasos llano, vistas de staff.
- **Negocio:** validación de tipo y contenido, límites y espacio, nombres únicos y duplicados, estado de lectura, permisos de baja, herramientas acotadas al cliente de la tarea, adjuntos validados contra el cliente.
- **Datos:** documento (reemplaza `DocumentoCliente`), texto por partes, adjuntos por mensaje; archivos en disco fuera del sitio público.

### M5-7. Riesgos y supuestos
- R-M5-01..07 heredados (inyección desde documentos, archivos maliciosos/confidencialidad, costo de lectura, espacio del hosting, tiempo de subida, expectativa de leer imágenes, staff sin contenido).
- R-M5-08 (medio, nuevo) muchos archivos en una subida pueden dejar la cola a medias si se cierra la página → cada archivo es independiente; los ya subidos quedan y el resto se reintenta; aviso "No cierres la página hasta que termine la subida" mientras hay cola.
- R-M5-09 (bajo, nuevo) nombre del chip distinto del nombre actual tras renombrar → es el nombre al adjuntar (auditable); el enlace lleva al documento actual.
- **Hipótesis heredadas del análisis que este diseño asume:** P2 (sin visión: imágenes no legibles), P3 (límites), P4 (baja por Director o autor), P5 (herramientas automáticas con cliente), P6 (adjuntar = referencia), P7 (staff solo metadatos), P8 (sin papelera), P9 (duplicados), P10 (extracción al subir), P12 (sin documentos de empresa). Supuestos S-M5-01..04.
- D-M5-1..14 tomadas sin gate.

### M5-8. Plan funcional por etapas (para el arquitecto)
1. Documento + almacén fuera de `wwwroot` + validación de contenido + extracción por partes y estado de lectura (reemplazo de `DocumentoCliente`).
2. Pantallas: card en la ficha, documentos del cliente con subida en cola, ver por partes, renombrar, baja, espacio.
3. Herramientas de documentos en el motor (solo tareas de trabajo con cliente) + Ver pasos llano.
4. Adjuntos en Ejecutar y en ajustes, vista previa, chips en la conversación.
5. Staff en backoffice; modelo simulado con guion de documentos.

### Historias de usuario M5
- **HU-M5-01** Como miembro, quiero subir los documentos de un cliente una sola vez, para no tener que pegarlos en cada pedido. *CA:* CA-M5-01, CA-M5-04; D-M5-3.
- **HU-M5-02** Como miembro, quiero saber al subir si el agente va a poder leer el documento. *CA:* CA-M5-01, CA-M5-03, CA-M5-15, CA-M5-16; D-M5-4.
- **HU-M5-03** Como miembro, quiero encontrar, ver y descargar documentos de un cliente. *CA:* CA-M5-05; P-M5-02/03.
- **HU-M5-04** Como miembro, quiero renombrar un documento con un nombre claro. *CA:* CA-M5-06; D-M5-6.
- **HU-M5-05** Como Director (o quien lo subió), quiero dar de baja documentos que ya no sirven y liberar espacio. *CA:* CA-M5-07, CA-M5-08, CA-M5-14; D-M5-7, D-M5-13.
- **HU-M5-06** Como miembro, quiero adjuntar documentos al pedirle una tarea a un agente y ver qué va a poder leer. *CA:* CA-M5-09; D-M5-8, D-M5-11.
- **HU-M5-07** Como autor de una tarea, quiero adjuntar un documento en un ajuste de la conversación. *CA:* CA-M5-13; D-M5-9.
- **HU-M5-08** Como miembro, quiero ver en la conversación qué documentos se adjuntaron y qué leyó el agente, en palabras. *CA:* CA-M5-10, CA-M5-14; D-M5-10, D-M5-12.
- **HU-M5-09** Como Director, quiero la tranquilidad de que un documento no le da órdenes al agente ni se lee desde otro cliente u organización. *CA:* CA-M5-11, CA-M5-12.
- **HU-M5-10** Como staff de Olvidata, quiero ver cuánto espacio usa una organización y qué documentos tiene, sin acceder a su contenido. *CA:* CA-M5-17; D-M5-14.
- **Transversal** CA-M5-02 (tipos y tamaños), CA-M5-05 (404 entre organizaciones), CA-M5-18 (reanudación) y CA-M5-19 (tema oscuro y mobile) aplican a HU-M5-01..08.

---

# M4b — Agente configurador de reglas del Director

Estado: **aprobado por Joaquín el 2026-09-14** con D-M4b-1..9 ("continuar"). Entrada: `1-analista-funcional.md` M4b aprobado 2026-09-14 (P1–P9). Criterio transversal: lenguaje llano, esconder complejidad (D-M3-8..12).

### M4b-0. Escaneo de reutilizacion
| Fuente | Qué hay | Decisión |
|---|---|---|
| Template M3b — `Tareas/_Conversacion`, `_CuadroSeguimiento`, refresco en vivo | Conversación con ajustes | **Reutilizar**: la configuración es una conversación M3b con tarjetas de propuesta embebidas. |
| Template M3 — `Reglas/_Form`, `Detalle` con historial, pestañas | ABM de reglas | **Reutilizar**: "Editar y aplicar" = formulario precargado; origen en el historial. |
| Template M4 — tarjetas del catálogo, sugerencias | Cards y activación | **Reutilizar** estilo de tarjeta y activación de sugerencias. |
| crm-olvidata (`docs/crm-olvidata/definiciones/3-arquitecto-mvc.md`) | Function calling: el modelo devuelve la acción y la ejecuta el servicio de negocio | **Reutilizar el criterio** para propuestas. |
| Catálogo y demás proyectos | Sin propuestas de cambios generadas por un agente con confirmación por tarjeta | **Diseño nuevo** → PAT-032. |

### M4b-1. Alcance funcional resumido
El Director conversa con el configurador de Olvidata dentro de Reglas; el agente consulta lo que el Director puede ver y devuelve propuestas (regla nueva, cambio, desactivación, activar sugerencia) como tarjetas; el Director aplica, edita y aplica, descarta o aplica todas; las reglas registran el origen; el costo se ve en Tareas.

### Decisiones de diseño M4b a validar en el gate
- **D-M4b-1 Entrada.** Botón secundario **"Configurar conversando"** en el encabezado de Reglas (solo Director) + invitación en la pestaña "De la empresa" cuando está vacía: "¿Preferís contarlo con tus palabras? Configurá conversando."
- **D-M4b-2 Lista de conversaciones compartida entre Directores.** Todos los Directores ven las conversaciones de configuración de la empresa; solo su autor sigue conversando (regla M3b), pero **cualquier Director puede aplicar o descartar propuestas pendientes**.
- **D-M4b-3 El configurador no recibe las reglas de la empresa como instrucciones**: las lee como datos con sus herramientas (así "Tono formal" no le cambia la forma de trabajar al configurador). En pantalla no se muestra "Lo que el agente tuvo en cuenta" en estas conversaciones.
- **D-M4b-4 Tarjeta de propuesta** con: tipo ("Nueva regla" / "Cambio en «Tono formal»" / "Desactivar «…»" / "Activar sugerencia «…»"), **Dónde aplica** en palabras, badge "Siempre" / "Salvo que se indique otra cosa", título, texto (plegado si es largo), **"Por qué"** (una línea del agente), y para cambios **Antes / Después** apilados.
- **D-M4b-5 Cambio desde la propuesta.** Si la regla cambió después de la propuesta, al aplicar se abre un modal con la versión actual y la propuesta: **Aplicar igual** · **Editar y aplicar** · Cancelar.
- **D-M4b-6 Editar y aplicar** lleva al formulario de regla precargado con un aviso arriba "Estás aplicando una propuesta del configurador"; al guardar vuelve a la conversación, a la tarjeta.
- **D-M4b-7 Arranque guiado.** El cuadro de la primera pregunta tiene chips que completan el texto: "Cómo hablamos con los clientes" · "Cosas que nunca hacemos" · "Revisá mis reglas actuales" · "Reglas para un área".
- **D-M4b-8 Tareas.** Filtro "Tipo": Tareas / Configuración de reglas (esta opción solo para Directores y staff).
- **D-M4b-9 Origen en el historial.** Badge "Propuesta del configurador" en el detalle de la regla; enlace "Ver conversación" solo para Directores y staff (el Empleado ve el badge sin enlace).

### Flujos de pantalla acordados M4b

**P-M4b-01 Reglas** (ajuste): encabezado con botón **Configurar conversando** (Director; si no hay versión publicada del configurador: deshabilitado con tooltip "Todavía no está disponible."); invitación de D-M4b-1.

**P-M4b-02 Configurar reglas — conversaciones** (Director)
- Encabezado: "Configurar reglas conversando" · "Contale al configurador cómo trabaja tu empresa. Te propone reglas y vos decidís cuáles aplicar." · botón primario **Nueva conversación**.
- Grilla DataTables: Iniciada · Por · Última actividad · Pendientes (badge ámbar si > 0) · Aplicadas · Estado; filtros por columna (Por, Pendientes: Con/Sin, Estado, rangos de fecha), Session, Limpiar; acción **Abrir**.
- Vacío: "Todavía no hay conversaciones. Empezá una y contale cómo trabajan."

**P-M4b-03 Nueva conversación**
- Card "¿Qué querés configurar?": chips de D-M4b-7 · textarea (6 filas, contador 0 / 10.000) con placeholder "Contame cómo trabaja tu empresa: qué hacer siempre, qué evitar, cómo hablarle a los clientes…" · hint "El configurador no cambia nada por su cuenta: te muestra propuestas y vos las aplicás." · botón **Empezar** (Ctrl+Enter).

**P-M4b-04 Conversación de configuración** (vista de M3b con tarjetas)
- Encabezado: "Configuración de reglas · 14/09/2026" · línea: Por · costo acumulado · "3 propuestas pendientes".
- Hilo M3b; debajo de cada respuesta del agente, sus **tarjetas de propuesta** (D-M4b-4) y, si hay 2 o más pendientes, botón **Aplicar todas (N)**.
- Acciones por tarjeta: **Aplicar** (primario) · **Editar y aplicar** (secundario) · **Descartar** (outline).
- Estados en la tarjeta: Pendiente (sin badge) · **Aplicada** (verde, enlace "Ver regla") · **Descartada** (gris, acciones ocultas) · **No se pudo aplicar** (rojo, motivo + **Reintentar** + Editar y aplicar).
- "Aplicar todas": SweetAlert2 "Se van a aplicar 4 propuestas. Las que no se puedan aplicar quedan marcadas con el motivo." → resultado en toast ("3 aplicadas, 1 no se pudo aplicar") y tarjetas actualizadas sin recargar.
- Cuadro "Seguir conversando" de M3b (solo el autor) con placeholder "Pedile otra regla o que ajuste una propuesta…".
- Otro Director: lee, aplica y descarta; sin cuadro.

**P-M4b-05 Formulario de regla** (ajuste): con `propuesta` en la URL, precargado (alcance, destino, modo, tipo, título, texto, etiquetas) + `ov-alert info` "Estás aplicando una propuesta del configurador." · al guardar: "Propuesta aplicada." y vuelta a la tarjeta.

**P-M4b-06 Detalle de regla** (ajuste): badge de origen y enlace según D-M4b-9; en el historial, el evento muestra "desde el configurador".

**P-M4b-07 Tareas** (ajuste D-M4b-8).

**P-M4b-08 Núcleo IP** (staff): el configurador aparece como artefacto de la plataforma con el flujo de versiones y evaluación existente.

### ViewModels definidos M4b
| ViewModel | Campos y validaciones |
|---|---|
| `ConversacionConfiguracionListItem` (JSON) | `tareaId, iniciada, por, ultimaActividad, pendientes, aplicadas, estado` |
| `IniciarConfiguracionViewModel` | `Texto` [Required "Contame qué querés configurar."] [StringLength 10000 "El mensaje admite hasta 10.000 caracteres."] |
| `PropuestaReglaViewModel` | `Id` · `Tipo` (Nueva / Cambio / Desactivar / ActivarSugerencia) · `Estado` · `DondeAplica` (texto llano) · `Modo?` · `TipoRegla` · `Titulo` · `Texto` · `TextoAnterior?` · `PorQue?` · `MotivoFallo?` · `ReglaId?` · `CambioDesdePropuesta` · `PuedeAccionar` |
| `AplicarTodasResultadoViewModel` (JSON) | `aplicadas`, `fallidas[] {id, motivo}` |
| `TareaDetalle` (ajuste) | + `EsConfiguracion` · `PropuestasPorTurno` |

### Validaciones de UI M4b
| Caso | Mensaje |
|---|---|
| Mensaje vacío / largo | "Contame qué querés configurar." / "El mensaje admite hasta 10.000 caracteres." |
| Configurador sin publicar | "Todavía no está disponible." |
| No es Director | 403 |
| Propuesta ya aplicada o descartada | "Esta propuesta ya fue resuelta." |
| Regla cambió desde la propuesta | modal D-M4b-5: "Esta regla cambió desde la propuesta. Revisá la versión actual antes de aplicar." |
| Falla al aplicar | mensaje del servicio de reglas (límite, destino dado de baja, conflicto) |
| OK | "Propuesta aplicada." / "Propuesta descartada." / "3 aplicadas, 1 no se pudo aplicar." |
| Confirmar descartar | sin confirmación (se puede volver a pedir al agente) |

### Maquina de estados M4b (propuesta)
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| — | Herramienta de propuesta del agente | Pendiente | dentro de lo que el Director puede proponer; ≤ 10 por respuesta | guarda propuesta con la versión vista de la regla | fuera de alcance → la herramienta devuelve error al agente |
| Pendiente / No se pudo aplicar | Aplicar / Reintentar | Aplicada | Director; validaciones de reglas; si la regla cambió, confirmación | crea/edita/desactiva/activa vía servicio de reglas con origen | límite / destino / conflicto → No se pudo aplicar |
| Pendiente / No se pudo aplicar | Editar y aplicar (guardar) | Aplicada | Director; validaciones | guarda lo editado | igual que el formulario |
| Pendiente / No se pudo aplicar | Descartar | Descartada | Director | — | — |

### Permisos por pantalla / accion M4b
| Acción | Director (autor) | Otro Director | Empleado | Staff |
|---|:---:|:---:|:---:|:---:|
| P-M4b-02/03 iniciar y listar | ✅ | ✅ | 403 | 👁 (lectura desde backoffice/Tareas) |
| Seguir conversando | ✅ | ❌ | — | ❌ |
| Aplicar / descartar / aplicar todas | ✅ | ✅ | 403 | ❌ |
| Ver origen en historial | ✅ con enlace | ✅ con enlace | badge sin enlace | ✅ con enlace |

### Contratos funcionales para Services M4b
| Contrato | Operaciones | Reglas |
|---|---|---|
| Configurador | disponible? · iniciar conversación · listar conversaciones de la empresa | RF-M4b-01, 11, 12; D-M4b-2 |
| Herramientas del configurador | leer reglas visibles (resumen paginado) · leer áreas, agentes de la empresa, clientes (nombres), sugerencias · proponer nueva / cambio / desactivar / activar sugerencia | RF-M4b-02, 09, 10; acotadas por permisos del Director que inició |
| Propuestas | listar por conversación y turno · aplicar (con verificación de cambio) · aplicar todas · descartar · reintentar · datos para precargar el formulario | RF-M4b-03..08 |
| Reglas (extensión) | crear/editar/desactivar/activar sugerencia con origen "Propuesta del configurador" y enlace a la propuesta | RF-M4b-04, 08 |
| Tareas (extensión) | tipo de tarea "configuración" · filtro · contexto sin reglas de la empresa | D-M4b-3, D-M4b-8 |
| Núcleo | prompt del configurador versionado y evaluado | RF-M4b-11 |

### M4b-6. Impacto funcional por capa
- **Presentación:** botón y lista de conversaciones, nueva conversación con chips, tarjetas de propuesta en la conversación, formulario precargado, origen en historial, filtro en Tareas.
- **Negocio:** herramientas de lectura/propuesta acotadas por permisos, aplicación por el servicio de reglas, verificación de cambios, aplicar todas.
- **Datos:** propuestas, origen y enlace en eventos de regla, tipo de tarea.

### M4b-7. Riesgos y supuestos
- R-M4b-01..05 heredados (propuestas equivocadas, inyección/escalamiento, costo, calidad del prompt, propuestas viejas).
- R-M4b-06 (medio, nuevo) muchas tarjetas en una respuesta pueden abrumar → límite 10 y "Aplicar todas".
- R-M4b-07 (bajo, nuevo) dos Directores accionando la misma propuesta a la vez → "Esta propuesta ya fue resuelta."
- S-M4b-01/02 heredados (confiabilidad de herramientas del modelo real; simulador con herramientas guionadas para QA).
- D-M4b-1..9 pendientes de validar.

### M4b-8. Plan funcional por etapas (para el arquitecto)
1. Tipo de conversación de configuración + contexto sin reglas de la empresa + prompt del configurador en núcleo (borrador).
2. Herramientas de lectura y de propuesta acotadas; propuestas persistidas.
3. Tarjetas, aplicar / editar y aplicar / descartar / aplicar todas, verificación de cambio.
4. Lista de conversaciones, entrada desde Reglas, origen en historial, filtro en Tareas.
5. Modelo simulado con herramientas guionadas para QA.

### Historias de usuario M4b
- **HU-M4b-01** Como Director, quiero contarle al configurador cómo trabaja mi empresa y recibir propuestas de reglas, para no tener que aprender alcances y modos. *CA:* CA-M4b-01; chips de arranque (D-M4b-7).
- **HU-M4b-02** Como Director, quiero aplicar una propuesta con un click. *CA:* CA-M4b-02.
- **HU-M4b-03** Como Director, quiero corregir una propuesta antes de aplicarla. *CA:* CA-M4b-03; D-M4b-6.
- **HU-M4b-04** Como Director, quiero descartar propuestas que no me sirven. *CA:* CA-M4b-04.
- **HU-M4b-05** Como Director, quiero aplicar varias propuestas juntas y saber cuáles fallaron. *CA:* CA-M4b-05, CA-M4b-10.
- **HU-M4b-06** Como Director, quiero que me avise si una regla cambió desde que se propuso el cambio. *CA:* CA-M4b-06; D-M4b-5.
- **HU-M4b-07** Como Director, quiero la tranquilidad de que nada se aplica sin mi confirmación. *CA:* CA-M4b-07.
- **HU-M4b-08** Como Director, quiero retomar una conversación de configuración y ver las de otros Directores. *CA:* CA-M4b-12; D-M4b-2.
- **HU-M4b-09** Como miembro o staff, quiero saber que una regla vino del configurador. *CA:* CA-M4b-13; D-M4b-9.
- **HU-M4b-10** Como Director, quiero ver cuánto cuestan las conversaciones de configuración. *CA:* CA-M4b-14; D-M4b-8.
- **Transversal** CA-M4b-08 (lectura acotada), CA-M4b-09 (Empleado 403), CA-M4b-11 (no disponible) y CA-M4b-15 (404 entre organizaciones) aplican a HU-M4b-01..08.

---

# M4 — Agentes de la organización

Estado: **aprobado por Joaquín el 2026-09-14** con D-M4-1..3 y D-M4-6..10, y el ajuste siguiente (prevalece sobre lo escrito abajo).

### Ajuste aprobado en el gate (2026-09-14): sin revisión del Director por ahora
- Se elimina el estado **"En revisión del Director"** y todo el flujo de propuesta: **P-M4-04 Propuestas y P-M4-05 Revisar propuesta quedan fuera de M4** (pospuestos); **D-M4-4 y D-M4-5 no aplican**.
- **Cualquier miembro publica directo** un agente para toda la empresa. D-M4-3 queda: "Solo yo" → **Guardar y usar** / Guardar borrador; "Toda la empresa" → **Publicar para la empresa** / Guardar borrador (mismo botón para Director y Empleado; se quita el hint "lo revisa el Director").
- **Edición de agentes de la empresa:** su creador y el Director. **Archivar/reactivar:** el Director cualquiera de la empresa; cada miembro los suyos (personales o de la empresa que creó).
- **D-M4-7 Notificaciones (adaptada):** cuando un miembro publica o actualiza un agente para toda la empresa, se avisa a los Directores ("Laura publicó «CM del estudio» para toda la empresa."), para que puedan revisarlo o archivarlo.
- **Máquina de estados de versión:** Borrador → Publicada → Reemplazada (sin En revisión ni Rechazada). Estados visibles (D-M4-2): Borrador · Publicado · Archivado · No disponible.
- Validación "Solo el Director puede publicar agentes para toda la empresa" se elimina.

Entrada: `1-analista-funcional.md` M4 aprobado 2026-09-14 (P1–P11 con las hipótesis). Criterio transversal vigente: UI en lenguaje llano, esconder la complejidad interna (D-M3-8..12).

### M4-0. Escaneo de reutilizacion
| Fuente | Qué hay | Decisión |
|---|---|---|
| Template M3 — `Reglas/*` (listado con pestañas, formulario con contador y opciones plegadas, detalle con historial, `_CardReglasDestino`) | ABM con versiones e historial | **Reutilizar** estructura para crear/editar/detalle de agentes y la card "Reglas de este agente". |
| Template M3 — `Agentes/Ejecutar` + `_VistaPreviaReglas`, `Tareas/_ReglasAplicadas` | Vista previa y reglas usadas | **Reutilizar** sumando el grupo "Instrucciones de <agente>". |
| Template núcleo — `Nucleo/Version` (estados Borrador/Evaluada/Publicada) | Ciclo de versiones | **Reutilizar** criterio visual de estados e historial. |
| Template — `NotificationService` + campana del topbar | Notificaciones in-app | **Reutilizar** para propuestas aprobadas/rechazadas y nuevas propuestas. |
| Template M2/M3 — listados DataTables con filtros, Session, acciones AJAX | Grillas | **Reutilizar** en Propuestas y en la vista de staff. |
| Catálogo y demás proyectos | Sin prompts derivados configurables por el cliente con aprobación | **Diseño nuevo** → PAT-030. |

### M4-1. Alcance funcional resumido
Catálogo unificado de agentes; crear, editar, duplicar, archivar y reactivar agentes derivados de un agente base; publicar (personal o para la empresa) con propuesta y revisión del Director; versiones e historial; uso en tareas con sus instrucciones en la vista previa; reglas por agente de la empresa; sugerencias de reglas de Olvidata activables por el Director; rubro incluido en todas las suscripciones (mecanismo); lectura para staff.

### Decisiones de diseño M4 a validar en el gate
- **D-M4-1 Formulario único, no asistente por pasos.** Cards en orden: agente base → datos → instrucciones → herramientas → quién lo usa.
- **D-M4-2 Estados en palabras.** "Borrador", "En revisión del Director", "Publicado", "Rechazado", "Archivado", "No disponible".
- **D-M4-3 Botones según el caso.** Personal: **Guardar y usar** / Guardar borrador. Para la empresa: Director **Publicar** / Guardar borrador; Empleado **Proponer a la empresa** / Guardar borrador.
- **D-M4-4 Bandeja de propuestas.** "Mi organización → Propuestas de agentes" con contador en el menú (solo Director).
- **D-M4-5 Revisión lado a lado.** El Director ve la versión publicada y la propuesta en dos columnas (texto completo, sin marcado de diferencias).
- **D-M4-6 Catálogo por secciones.** "De tu área" (destacados) · "De la empresa" · "Mis agentes" · "De Olvidata" (por rubro), con buscador.
- **D-M4-7 Notificaciones.** Nueva propuesta → Directores; aprobada/rechazada → creador (campana existente).
- **D-M4-8 Reglas "Por agente".** El combo incluye agentes de Olvidata y agentes publicados para la empresa; los agentes personales no reciben reglas (sus instrucciones ya son personales).
- **D-M4-9 Sugerencias de Olvidata** como pestaña de Reglas, solo para el Director.
- **D-M4-10 Rubro incluido siempre** visible como marca en Núcleo IP y como casilla tildada y bloqueada en el alta de licencias; se configura desde el manifiesto del núcleo, no desde el portal.

### Flujos de pantalla acordados M4

**P-M4-01 Agentes — catálogo** (rediseño de `Agentes/Index`, miembros)
- Encabezado: "Agentes" · "Elegí un agente para pedirle una tarea, o creá tu propia versión de uno de Olvidata." · botón primario **Crear agente**.
- Buscador por nombre/descripción (filtra en la página).
- Secciones (ocultas si vacías): **De tu área «Marketing»** · **De la empresa** · **Mis agentes** · **De Olvidata** (subtítulo por rubro).
- Card: nombre · descripción · badges (Personal / De la empresa / De Olvidata; área destacada; "Basado en <agente base>") · para el creador, estado si no está publicado (Borrador, En revisión del Director, Rechazado) · acciones: **Usar** (primario) · menú: Crear mi versión (agentes de Olvidata y de la empresa) · Ver · Editar · Duplicar · Archivar.
- "No disponible": card atenuada con "No disponible: la suscripción a <rubro> no está vigente." y sin "Usar".
- Estado vacío de "Mis agentes": "Todavía no creaste agentes. Elegí uno de Olvidata y tocá «Crear mi versión»."

**P-M4-02 Crear / editar agente**
- Encabezado: "Nuevo agente" / "Editar <nombre>" · "Partís de un agente de Olvidata y le sumás cómo trabaja tu empresa." · Volver.
- Card "Agente base": Select2 agrupado por rubro con la descripción del base (precargado si se entró con "Crear mi versión"); en edición solo lectura con hint "Para cambiar de agente base, duplicá este agente."
- Card "Datos": Nombre* (`col-md-6`) · Descripción (`col-12`, hint "La ven quienes lo eligen en el catálogo.").
- Card "Instrucciones": textarea 14 filas, contador "0 / 8.000", hint "Contale qué tiene que hacer distinto: tono, formato, pasos de tu empresa. No hace falta repetir las reglas de la empresa." · aviso "No cargues contraseñas ni datos bancarios."
- Card "Herramientas": casillas con nombre llano y descripción de cada herramienta del base; sin herramientas: "Este agente de Olvidata no usa herramientas."
- Card "Quién lo usa": radio **Solo yo** / **Toda la empresa** (para el Empleado: "Toda la empresa — lo revisa el Director antes de publicarlo") · Área destacada (Select2 opcional, visible con "Toda la empresa").
- Barra sticky según D-M4-3 · Cancelar · en edición: espaciador + Archivar. Hint en edición: "Guardar crea la versión 3. Las tareas anteriores no cambian."
- Si hay una versión en revisión: `ov-alert info` "Hay una versión esperando la revisión del Director. Si guardás, reemplaza a esa propuesta."

**P-M4-03 Detalle de agente**
- Encabezado: nombre · badge de estado · acciones: Usar · Editar · Duplicar · Archivar/Reactivar (según permisos).
- `ov-detail-grid`: Basado en (agente y rubro) · Quién lo usa · Área destacada · Creado por · Versión publicada · Herramientas.
- Card "Instrucciones" (versión publicada).
- Card "Borrador" o "En revisión del Director" (si existe) con su texto; si fue rechazada: `ov-alert warning` con el motivo del Director.
- Card "Historial de versiones": Versión · Estado · Fecha · Autor · Motivo (si rechazada) · "Ver instrucciones".
- Card "Reglas de este agente" (D-M4-8, reutiliza la card de M3) con "Nueva regla para este agente" (Director, solo agentes de la empresa).

**P-M4-04 Propuestas de agentes** (`Mi organización`, Director)
- Encabezado: "Propuestas de agentes" · "Agentes que tu equipo quiere compartir con toda la empresa."
- Grilla DataTables: Agente · Propuesto por · Tipo (Nuevo / Cambio) · Área destacada · Fecha; filtros por columna; Session; Limpiar filtros; acción **Revisar**.
- Vacío: "No hay propuestas pendientes."

**P-M4-05 Revisar propuesta** (Director)
- Encabezado: "Revisar «CM del estudio»" · "Propuesto por Laura el 14/09/2026."
- Dos columnas (una sola en mobile, propuesta primero): **Publicada hoy** / **Propuesta** — instrucciones, herramientas, quién lo usa, área destacada. Para "Nuevo", solo la propuesta.
- Barra: **Aprobar y publicar** (primario) · **Rechazar** (outline rojo → SweetAlert2 con textarea obligatoria "Contale a Laura qué cambiar") · Volver.

**P-M4-06 Nueva tarea** (ajuste): encabezado "CM del estudio · basado en Community manager"; en "Esto es lo que el agente va a tener en cuenta" aparece el grupo **"Instrucciones de CM del estudio"** en su lugar de prioridad.

**P-M4-07 Reglas** (ajuste D-M4-8): el combo Agente se agrupa en "De Olvidata" y "De la empresa"; en la pestaña "Por agente" la columna muestra el nombre del agente.

**P-M4-08 Reglas → Sugerencias de Olvidata** (pestaña, solo Director)
- Descripción: "Reglas que Olvidata recomienda para tus rubros. Activalas en un click y después editalas como quieras."
- Cards agrupadas por rubro: título · texto · etiquetas · acciones **Activar en la empresa** / **Activar en un área** (modal: Área*, "Siempre" / "Salvo que se indique otra cosa" — por defecto la segunda).
- Ya activada: badge "Ya activada" con enlace a la regla.
- Vacío: "Todavía no hay sugerencias de Olvidata para tus rubros."

**P-M4-09 Backoffice y núcleo** (staff)
- Organizaciones → detalle → **Agentes**: grilla de solo lectura (Agente, Basado en, Quién lo usa, Estado, Creado por) y detalle P-M4-03 sin acciones, con instrucciones visibles.
- Núcleo IP → rubro: badge "Incluido en todas las suscripciones"; sugerencias de reglas como artefactos con el flujo de evaluación existente.
- Alta de licencia: el rubro incluido aparece tildado y bloqueado con hint "Se incluye en todas las suscripciones."

**P-M4-10 Detalle de tarea** (ajuste): encabezado "CM del estudio (versión 3)"; si el agente está archivado, badge "Agente archivado" (los ajustes siguen permitidos, P11).

### ViewModels definidos M4
| ViewModel | Campos y validaciones |
|---|---|
| `AgentesCatalogoViewModel` | `Secciones[]` (`Titulo`, `Items[]`) · `AreaUsuario?` · `PuedeCrear` |
| `AgenteCardItem` | `Tipo` (Olvidata / Empresa / Personal) · `Id/Ref` · `Nombre` · `Descripcion` · `BaseNombre` · `AreaDestacada?` · `Estado` · `Disponible` · `MotivoNoDisponible?` · acciones permitidas |
| `AgenteFormViewModel` | `Id?` · `BaseRef` [Required "Elegí el agente de Olvidata en el que se basa."] · `Nombre` [Required "Ingresá un nombre."] [StringLength 100] · `Descripcion?` [StringLength 500] · `Instrucciones` [Required "Escribí las instrucciones."] [StringLength 8000 "Las instrucciones admiten hasta 8.000 caracteres."] · `Herramientas[]` · `Visibilidad` [Required "Elegí quién lo usa."] · `AreaDestacadaId?` · `Accion` (GuardarBorrador / GuardarYUsar / Publicar / Proponer) · `VersionToken` · opciones (bases, herramientas del base, áreas) · `HayPropuestaPendiente` |
| `AgenteDetalleViewModel` | datos · `Publicada?` · `Pendiente?` (borrador o en revisión, con motivo de rechazo) · `Historial[]` · `ReglasDelAgente` · permisos |
| `PropuestaListItem` (JSON) | `id, agente, propuestoPor, tipo, areaDestacada, fecha` |
| `RevisarPropuestaViewModel` | `Publicada?` · `Propuesta` · `Autor` · `Fecha` · `MotivoRechazo` [Required al rechazar "Contale qué cambiar."] [StringLength 1000] |
| `SugerenciaReglaItem` | `Id` · `Rubro` · `Titulo` · `Texto` · `Etiquetas` · `YaActivadaReglaId?` |
| `ActivarSugerenciaViewModel` | `SugerenciaId` · `Destino` (Empresa / Área) · `AreaId?` (requerido si Área: "Elegí el área.") · `Modo` |

### Validaciones de UI M4
| Caso | Mensaje |
|---|---|
| Nombre repetido entre agentes activos | "Ya hay un agente activo con ese nombre en tu empresa." |
| Herramienta fuera del agente base | "Esa herramienta no está disponible en el agente de Olvidata elegido." |
| Agente base no habilitado | "Ese agente de Olvidata no está incluido en la suscripción de tu empresa." |
| Límite de agentes activos | "Tu empresa llegó al máximo de 50 agentes activos. Archivá alguno para crear otro." |
| Límite personales | "Llegaste al máximo de 10 agentes personales. Archivá alguno para crear otro." |
| Empleado intenta publicar directo / aprobar | "Solo el Director puede publicar agentes para toda la empresa." (403) |
| Agente no disponible | "Este agente no está disponible: la suscripción a <rubro> no está vigente." |
| Editar mientras otro guardó | "Otra persona modificó este agente mientras lo editabas. Revisá la versión actual y volvé a guardar." |
| OK | "Agente guardado como borrador." / "Agente listo para usar." / "Agente publicado para toda la empresa." / "Propuesta enviada al Director." / "Propuesta aprobada y publicada." / "Propuesta rechazada. Le avisamos a Laura." / "Agente archivado." / "Agente reactivado." / "Copia creada como borrador." / "Regla activada." |
| Confirmación archivar | "¿Archivar «CM del estudio»? Deja de aparecer para pedir tareas nuevas; las tareas y conversaciones existentes siguen disponibles." |

### Maquina de estados M4 (versión del agente)
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| — | Guardar borrador | Borrador | permisos; límites; validaciones | nueva versión | límite / validación |
| Borrador | Guardar y usar (personal) | Publicada | creador; visibilidad Solo yo | publicada anterior → Reemplazada | — |
| Borrador | Publicar (empresa) | Publicada | Director | anterior → Reemplazada; notifica si había propuesta | sin permiso |
| Borrador | Proponer | En revisión | Empleado; visibilidad Toda la empresa | notifica Directores; reemplaza propuesta previa del mismo agente | — |
| En revisión | Aprobar | Publicada | Director; misma organización | anterior → Reemplazada; notifica creador | sin permiso |
| En revisión | Rechazar | Rechazada | Director; motivo | notifica creador con motivo | motivo vacío |
| Publicada / Rechazada | Editar | Borrador (N+1) | permisos | — | conflicto de edición |
| Agente Activo | Archivar | Archivado | Director o creador (personal) | sale del catálogo | — |
| Archivado | Reactivar | Activo | permisos; límite de activos | vuelve con su última publicada | límite |

### Permisos por pantalla / accion M4
| Pantalla / acción | Director | Empleado | Staff |
|---|:---:|:---:|:---:|
| P-M4-01 catálogo | ✅ (sin personales ajenos) | ✅ (sin personales ajenos) | — |
| P-M4-02 crear / editar | personales propios y de la empresa | personales propios; de la empresa que creó (vuelve a revisión) | ❌ |
| P-M4-03 detalle | empresa + propios | empresa + propios | ✅ todos (P-M4-09) |
| P-M4-04/05 propuestas | ✅ | ❌ 403 | ❌ |
| P-M4-08 sugerencias | ✅ | ❌ (pestaña oculta) | — |
| Archivar / reactivar | cualquiera de la empresa + propios | sus personales | ❌ |

### Contratos funcionales para Services M4
| Contrato | Operaciones | Reglas |
|---|---|---|
| Agentes de la organización | catálogo por usuario · obtener detalle con historial · crear/editar con acción · duplicar · archivar/reactivar · opciones del formulario (bases habilitadas, herramientas del base, áreas) | RF-M4-01..11, 14, 15; D-M4-1..3, 6 |
| Propuestas | listar pendientes · obtener para revisar · aprobar · rechazar con motivo | RF-M4-06, 07; D-M4-4, 5, 7 |
| Constructor de contexto (extensión) | resolver agente (base o de la empresa) → versión del base vigente + versión del derivado + herramientas efectivas · nivel 6 · reglas por agente de la empresa y del base | RF-M4-02, 03, 09 |
| Tareas (extensión) | crear con agente de la empresa · detalle con nombre y versión · ajustes permitidos con agente archivado | RF-M4-10 (P11) |
| Reglas (extensión) | combo de agentes · sugerencias visibles por rubro · activar sugerencia | D-M4-8, 9; RF-M4-13 |
| Licencias / núcleo (extensión) | rubro incluido siempre al crear y renovar · sincronizar vigentes · importar y publicar sugerencias | RF-M4-12, 13; D-M4-10 |
| Notificaciones | propuesta nueva · aprobada · rechazada | D-M4-7 |

### M4-6. Impacto funcional por capa
- **Presentación:** catálogo rediseñado, formulario y detalle de agentes, propuestas y revisión, pestaña de sugerencias, ajustes en nueva tarea, reglas, detalle de tarea, backoffice, núcleo y licencias.
- **Negocio:** versiones con aprobación, permisos por visibilidad y rol, límites, herramientas efectivas, nivel 6 del contexto, activación de sugerencias, rubro incluido.
- **Datos:** agentes de la organización y versiones, referencia en tareas y reglas, sugerencias del núcleo, marca de rubro incluido.

### M4-7. Riesgos y supuestos
- R-M4-01..04 heredados (inyección por instrucciones, cambios del base, complejidad de estados, proliferación).
- R-M4-05 (medio, nuevo) mostrar estados de versión sin abrumar: solo el creador y el Director ven borradores/revisión; el resto ve el agente publicado.
- R-M4-06 (bajo, nuevo) propuestas abandonadas: sin vencimiento en M4.
- S-M4-01/02 heredados (pocas herramientas hoy; contenido de "negocio" y sugerencias lo define Joaquín).
- D-M4-1..10 pendientes de validar.

### M4-8. Plan funcional por etapas (para el arquitecto)
1. Datos y servicio de agentes de la organización (versiones, permisos, límites, archivar, duplicar).
2. Catálogo, formulario y detalle.
3. Propuestas, revisión y notificaciones.
4. Constructor de contexto (nivel 6, herramientas efectivas), tareas y reglas por agente de la empresa.
5. Rubro incluido siempre y sugerencias de reglas (núcleo, licencias, pestaña del Director).
6. Vistas de staff.

### Historias de usuario M4
- **HU-M4-01** Como miembro, quiero crear mi propia versión de un agente de Olvidata para que trabaje como yo necesito. *CA:* CA-M4-01, CA-M4-04, CA-M4-06.
- **HU-M4-02** Como Director, quiero publicar un agente para toda la empresa y destacarlo para un área. *CA:* CA-M4-02.
- **HU-M4-03** Como Empleado, quiero proponer un agente a la empresa y saber si fue aprobado o por qué se rechazó. *CA:* CA-M4-03; notificación y motivo visibles.
- **HU-M4-04** Como Director, quiero revisar propuestas comparando con lo publicado. *CA:* CA-M4-03; D-M4-5; rechazar exige motivo.
- **HU-M4-05** Como creador, quiero editar un agente sin afectar las tareas ya hechas. *CA:* CA-M4-05; edición de Empleado sobre agente de la empresa vuelve a revisión (P5).
- **HU-M4-06** Como miembro, quiero encontrar rápido el agente que necesito. *CA:* D-M4-6; buscador; destacados de mi área.
- **HU-M4-07** Como miembro, quiero ver en la vista previa las instrucciones del agente de la empresa. *CA:* CA-M4-01 (grupo "Instrucciones de…").
- **HU-M4-08** Como Director, quiero reglas para un agente de la empresa. *CA:* CA-M4-07; D-M4-8.
- **HU-M4-09** Como Director o creador, quiero archivar y reactivar agentes. *CA:* CA-M4-08; ajustes en tareas existentes permitidos (P11).
- **HU-M4-10** Como miembro, quiero duplicar un agente como punto de partida. *CA:* CA-M4-11.
- **HU-M4-11** Como miembro, quiero saber cuándo un agente no está disponible y por qué. *CA:* CA-M4-09.
- **HU-M4-12** Como Director, quiero activar reglas sugeridas por Olvidata. *CA:* CA-M4-13; D-M4-9.
- **HU-M4-13** Como staff de Olvidata, quiero que un rubro quede incluido en todas las suscripciones. *CA:* CA-M4-12; D-M4-10.
- **HU-M4-14** Como staff de Olvidata, quiero ver los agentes que crean las organizaciones. *CA:* CA-M4-14.
- **Transversal** CA-M4-10 (límites) y CA-M4-15 (ids de otra organización → 404) aplican a HU-M4-01..12.

---

# M3b — Seguir conversando sobre una tarea

Estado: **aprobado por Joaquín el 2026-09-14** con D-M3b-1..7. Entrada: `1-analista-funcional.md` M3b aprobado 2026-09-14 (P1–P8 con las hipótesis).

### M3b-0. Escaneo de reutilizacion
| Fuente | Qué hay | Decisión |
|---|---|---|
| Template M1 — `Tareas/Detalle` + `_Progreso` + SignalR con respaldo de 10 s | Progreso en vivo por pasos | **Reutilizar**: el hilo se refresca con el mismo mecanismo (el parcial pasa a renderizar la conversación). |
| Template M3 — `_ReglasAplicadas`, `_VistaPreviaReglas` | Reglas de la tarea | **Reutilizar**, con el ajuste P6 (preferencias ajenas solo como contador). |
| Template M2 — listado de Tareas (filtros por columna, Session) | Grilla | **Reutilizar** sumando columnas. |
| century-21 A-04 (historial de conversación del bot, solo lectura) | Presentación de mensajes | Referencia visual menor. |
| Catálogo y demás proyectos | Sin conversación multi-turno persistida y reanudable contra un modelo | **Diseño nuevo** → PAT-029. |

### M3b-1. Alcance funcional resumido
El detalle de tarea pasa a ser una conversación: el autor envía ajustes sobre una tarea terminada (completada, fallida o cancelada), con el mismo agente, cliente y reglas; respuestas en vivo; costo acumulado; límites; copiar respuesta; listado con última actividad y mensajes; preferencias personales ajenas ocultas al Director.

### Decisiones de diseño M3b a validar en el gate
- **D-M3b-1 Suscripción vencida.** Si la organización ya no tiene licencia vigente para el rubro del agente, no se puede seguir ("Tu organización no tiene la suscripción vigente para este agente."). La conversación se sigue leyendo.
- **D-M3b-2 Cliente dado de baja.** No bloquea el seguimiento (el contexto está congelado); el encabezado muestra "Cliente: Panadería Norte (dado de baja)".
- **D-M3b-3 Qué es "la respuesta".** En cada turno, la burbuja del agente muestra el texto final del turno; los textos intermedios y las herramientas quedan en "Ver pasos".
- **D-M3b-4 Orden del listado.** Por defecto, "Última actividad" descendente.
- **D-M3b-5 Atajo.** Encabezado con "Nueva tarea con este agente" (precarga agente y cliente) y el mismo botón al llegar al límite.
- **D-M3b-6 Envío con teclado.** Ctrl+Enter envía; Enter hace salto de línea.
- **D-M3b-7 Preferencias ajenas (P6).** Para quien no es el autor ni staff, el grupo muestra solo "Preferencias personales de Laura (2 reglas)", sin títulos ni texto.

### Flujos de pantalla acordados M3b

**P-M3b-01 Detalle de tarea — conversación** (reemplaza la estructura Pedido / Resultado / Pasos)
- Encabezado: "Tarea #12 · CM del estudio" · línea: Cliente · creada · última actividad · pedida por (si quien mira no es el autor) · acciones: **Cancelar** (si hay un turno activo, rojo con confirmación) · **Nueva tarea con este agente** (secundario).
- Línea de estado: badge del estado · "5 mensajes" · "12.340 tokens · USD 0,12 en total".
- Card plegada "Lo que el agente tuvo en cuenta (9)" (M3) + si alguna regla cambió desde la creación: `ov-alert info` "Algunas reglas cambiaron desde que empezó esta conversación. Acá se siguen usando las de entonces." con enlace **Empezar una tarea nueva**.
- **Hilo**, en orden:
  - Mensaje de la persona (pedido inicial rotulado "Pedido"; los siguientes, "Ajuste"): inicial del nombre, nombre, fecha y hora, texto con saltos de línea.
  - Respuesta del agente: ícono del agente, nombre, fecha y hora, botón **Copiar**, texto; debajo `<details>` "Ver pasos (3)" con herramientas y resultados (formato actual de pasos).
  - Turno fallido: dentro del turno, `ov-alert danger` con el error ("La respuesta superó el máximo…") + hint "Podés pedirle que siga o reformular el pedido."
  - Turno cancelado: línea gris "Cancelaste esta respuesta." (o "La canceló <nombre>").
  - Turno activo: burbuja del agente con spinner "En cola…" o "Trabajando · paso 2 de hasta 25".
- **Cuadro "Seguir conversando"** (card al pie, sticky en mobile), solo para el autor:
  - Textarea (4 filas, crece hasta 10), placeholder "Pedile un ajuste: más corto, otro tono, agregá…", contador "0 / 10.000".
  - Hint: "Seguís con el mismo agente, cliente y reglas. Quedan 17 ajustes en esta conversación."
  - Botón primario **Enviar** (Ctrl+Enter).
  - Mientras hay un turno activo: textarea y botón deshabilitados, placeholder "Esperá la respuesta para seguir."
  - Límite alcanzado: en lugar del cuadro, `ov-alert warning` "Esta conversación llegó al máximo de 20 ajustes." + **Nueva tarea con este agente**.
  - Suscripción vencida (D-M3b-1): `ov-alert warning` con el mensaje, sin cuadro.
- Quien no es el autor (Director, staff): sin cuadro; nota discreta "Solo quien pidió la tarea puede seguir esta conversación."
- Envío: AJAX; al aceptar, se agrega la burbuja del ajuste y la de "En cola…", se limpia el textarea y se activa el refresco en vivo; al rechazar, toast con el mensaje y el texto queda en el textarea. Al llegar una respuesta nueva, scroll suave al último mensaje.
- Copiar: copia el texto de esa respuesta y muestra toast "Respuesta copiada."

**P-M3b-02 Tareas — listado** (ajuste)
- Columnas nuevas: **Mensajes** (número) y **Última actividad** (fecha y hora). Filtros: Mensajes (Select2: Todas / Solo el pedido / Con ajustes) y Última actividad (daterangepicker). Orden por defecto: última actividad desc (D-M3b-4). "Pedido" sigue mostrando el pedido inicial.

**P-M3b-03 Nueva tarea** (ajuste): acepta agente + cliente precargados desde "Nueva tarea con este agente".

**P-M3b-04 Lo que el agente tuvo en cuenta** (ajuste P6 / D-M3b-7): grupo de preferencias según quién mira (autor y staff: completo; otros: contador).

### ViewModels definidos M3b
| ViewModel | Campos y validaciones |
|---|---|
| `TareaConversacionViewModel` | `Resumen` (id, agente, estado, cliente, clienteDadoDeBaja, creada, ultimaActividad, pedidaPor) · `Mensajes[]` · `TurnoActivo?` (estado, paso, maxPasos) · `TokensTotales` · `CostoTotalUsd` · `PuedeSeguir` · `MotivoNoPuedeSeguir?` (EnCurso / NoEsAutor / Limite / SinSuscripcion) · `AjustesRestantes` · `ReglasCambiaron` · `ReglasAplicadas` · `AgenteRef` + `ClienteCarteraId?` (para el atajo) |
| `MensajeConversacionItem` | `Tipo` (Persona / Agente) · `Rotulo` (Pedido / Ajuste / Respuesta) · `Autor` · `Fecha` · `Texto` · `Pasos[]` (solo agente) · `Error?` · `Cancelado` |
| `SeguimientoViewModel` | `TareaId` · `Texto` [Required "Escribí tu mensaje."] [StringLength 10000 "El mensaje admite hasta 10.000 caracteres."] |
| `TareaListItem` (cambio) | + `mensajes`, `ultimaActividad` |

### Validaciones de UI M3b
| Caso | Mensaje |
|---|---|
| Mensaje vacío | "Escribí tu mensaje." |
| Más de 10.000 caracteres | "El mensaje admite hasta 10.000 caracteres." |
| Turno activo | "La tarea todavía está trabajando. Esperá la respuesta para seguir." |
| No es el autor | "Solo quien pidió la tarea puede seguir esta conversación." (403) |
| Límite | "Esta conversación llegó al máximo de 20 ajustes. Empezá una tarea nueva." |
| Suscripción vencida | "Tu organización no tiene la suscripción vigente para este agente." |
| Tarea inexistente o ajena | 404 |
| Copiar | "Respuesta copiada." |
| Confirmar cancelación de un turno | "¿Cancelar esta respuesta? La conversación anterior se conserva." |

### Maquina de estados M3b
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| Completada / Fallida / Cancelada | Ajuste del autor | Pendiente | autor; < 20 ajustes; texto válido; suscripción vigente; sin turno activo | registra el mensaje; limpia resultado/error del turno; notifica | no autor / límite / en curso / sin suscripción |
| Pendiente | Worker toma | EnCurso | igual que M1 | — | — |
| EnCurso | Fin de turno | Completada / Fallida | pasos del turno ≤ máximo | respuesta del turno | — |
| Pendiente / EnCurso | Cancelar | Cancelada | permiso de cancelar (M2) | conserva conversación | — |

### Permisos por pantalla / accion M3b
| Acción | Autor | Director (tarea ajena) | Empleado (tarea ajena) | Staff |
|---|:---:|:---:|:---:|:---:|
| Ver conversación | ✅ | ✅ | 404 | ✅ |
| Enviar ajuste | ✅ | ❌ 403 | 404 | ❌ |
| Cancelar turno | ✅ | ✅ | 404 | — |
| Copiar | ✅ | ✅ | — | ✅ |
| Texto de preferencias del autor | ✅ | contador | — | ✅ |

### Contratos funcionales para Services M3b
| Contrato | Operaciones | Reglas |
|---|---|---|
| Tareas | enviar ajuste (tarea, texto) · obtener conversación (mensajes por turno, turno activo, totales, puede seguir y motivo, ajustes restantes, reglas cambiaron) · listar con mensajes y última actividad · precargar nueva tarea desde otra | RF-M3b-01..10; D-M3b-1..7 |
| Motor | reconstruir conversación con mensajes de ajuste · contar pasos por turno · reanudar sin duplicar el ajuste | RF-M3b-04, 05; CA-M3b-13 |
| Constructor de contexto | ¿cambiaron las reglas de la instantánea? (versión posterior, desactivada o nueva regla aplicable) · visibilidad de preferencias por observador | P2, P6 |

Eventos: ajuste enviado; turno iniciado/terminado con tokens y costo (telemetría por turno).

### M3b-6. Impacto funcional por capa
- **Presentación:** detalle de tarea como conversación con cuadro de ajuste, listado con mensajes y última actividad, atajo a nueva tarea, preferencias ajenas ocultas.
- **Negocio:** re-apertura con guardas, pasos por turno, límites, reglas cambiadas, suscripción vigente.
- **Datos:** mensaje de ajuste como parte de la conversación persistida; contador de ajustes y última actividad en la tarea.

### M3b-7. Riesgos y supuestos
- R-M3b-01..04 heredados (costo creciente, reanudación, thinking, confusión con reglas congeladas).
- R-M3b-05 (bajo, nuevo) "Copiar" usa la API del portapapeles del navegador (requiere HTTPS; el portal ya lo usa).
- R-M3b-06 (bajo, nuevo) conversaciones de 21 turnos con pasos: el hilo puede ser largo; pasos plegados mitigan.
- S-M3b-01, S-M3b-02 heredados. D-M3b-1..7 pendientes de validar.

### M3b-8. Plan funcional por etapas (para el arquitecto)
1. Datos y motor: mensaje de ajuste en la conversación, re-apertura con guardas, pasos por turno, reanudación.
2. Detalle como conversación + cuadro de ajuste + refresco en vivo + copiar.
3. Reglas cambiadas, preferencias ajenas ocultas, suscripción vigente.
4. Listado (mensajes, última actividad) + atajo a nueva tarea.

### Historias de usuario M3b
- **HU-M3b-01** Como autor de una tarea, quiero pedirle un ajuste al agente sobre su respuesta, para no empezar de cero ni volver a Claude web. *CA:* CA-M3b-01, CA-M3b-02; Ctrl+Enter envía.
- **HU-M3b-02** Como autor, quiero que el ajuste use el mismo agente, cliente y reglas, para no volver a explicar el contexto. *CA:* CA-M3b-03; aviso de reglas cambiadas con acceso a tarea nueva.
- **HU-M3b-03** Como autor, quiero ver la respuesta del ajuste en vivo. *CA:* CA-M3b-01; burbuja "En cola…" / "Trabajando · paso N".
- **HU-M3b-04** Como autor, quiero que no se pueda mandar otro ajuste mientras el agente trabaja. *CA:* CA-M3b-04.
- **HU-M3b-05** Como autor, quiero saber cuánto lleva gastado la conversación y cuántos ajustes me quedan. *CA:* CA-M3b-06, CA-M3b-07.
- **HU-M3b-06** Como autor, quiero retomar una tarea fallida o cancelada. *CA:* CA-M3b-08; también desde Cancelada (P3).
- **HU-M3b-07** Como autor, quiero copiar una respuesta. *CA:* CA-M3b-10.
- **HU-M3b-08** Como Director, quiero leer la conversación completa de una tarea de mi equipo sin poder intervenir ni ver sus preferencias personales. *CA:* CA-M3b-05; D-M3b-7.
- **HU-M3b-09** Como miembro, quiero ubicar en el listado las tareas con actividad reciente y las que tuvieron ajustes. *CA:* CA-M3b-11; D-M3b-4.
- **HU-M3b-10** Como autor, quiero empezar una tarea nueva con el mismo agente y cliente cuando la conversación llegó al límite o las reglas cambiaron. *CA:* D-M3b-5.
- **Transversal** CA-M3b-12 (tareas viejas), CA-M3b-13 (reinicio a mitad de turno) y CA-M3b-14 (404 entre organizaciones) aplican a HU-M3b-01..06.

---

# M3 — Reglas por alcance

Estado: **aprobado por Joaquín el 2026-09-14** con D-M3-1..D-M3-7 y los ajustes de simplificación D-M3-8..D-M3-12 (tienen prioridad sobre los textos de pantalla de abajo). Entrada: `1-analista-funcional.md` M3 aprobado 2026-09-14 (P1–P9 respondidas).

### Ajustes de simplificacion aprobados (2026-09-14) — prevalecen sobre textos y rotulos de las pantallas
Objetivo de Joaquín: que los usuarios usen agentes IA de forma más comprensible y simplificada que escribiendo prompts en Claude web. La arquitectura interna (alcances, 9 niveles, modos) no cambia; cambia lo que ve el usuario.
- **D-M3-8 Nombres llanos.** Pestañas y alcances en UI: "De la empresa" (Organización) · "De las áreas" / "De mi área" (Área) · "Por agente" (Agente) · "De clientes" (Cliente y Cliente + agente) · "Mis preferencias" (Usuario). Mensajes y ayudas usan esos nombres.
- **D-M3-9 Modo en palabras.** "Obligatoria" se muestra como **"Siempre"** (badge rojo) y "Por defecto" como **"Salvo que se indique otra cosa"** (badge gris). Hint del campo: "Siempre: ninguna otra regla la puede cambiar. Salvo que se indique otra cosa: una regla más específica (de un cliente, por ejemplo) la reemplaza."
- **D-M3-10 Opciones avanzadas plegadas.** En el formulario, Tipo (default "Regla") y Etiquetas quedan dentro de un bloque plegable "Opciones avanzadas"; el aviso de reglas del mismo tema solo aparece si hay etiquetas. Visibles de entrada: a quién aplica, título, "Siempre/Salvo…" (si corresponde) y texto.
- **D-M3-11 La vista previa es el centro.** La card de P-M3-04 se titula **"Esto es lo que el agente va a tener en cuenta"**; los grupos usan los nombres llanos ("De la empresa — siempre", "De tu área", "De Panadería Norte", "Tus preferencias"…); las reglas de Olvidata se rotulan "Método de Olvidata para este agente" (sin texto). En P-M3-05 la card se titula "Lo que el agente tuvo en cuenta".
- **D-M3-12 Menú y encabezado.** El ítem del menú sigue siendo "Reglas"; descripción de P-M3-01: "Contale a los agentes cómo trabaja tu empresa: qué hacer siempre, qué evitar y qué preferís. Una regla nunca da permisos."
- Roadmap asociado (no es alcance de M3): etapa nueva **"Seguir conversando sobre una tarea"** entre M3 y M4; **reglas sugeridas por rubro** junto con M4.

### M3-0. Escaneo de reutilizacion
| Fuente | Qué hay | Decisión |
|---|---|---|
| Template propio M2 (`Views/Cartera/*`, `Views/Areas/*`, `Web/Helpers/FiltrosSesion.cs`, bajas AJAX) | Listado DataTables con filtros por columna + Session + Limpiar, formularios con sistema `.ov-*`, detalle con `.ov-detail-grid`, acción AJAX con confirmación y `reload(null,false)` | **Reutilizar** en Reglas (listado, alta/edición, detalle, activar/desactivar). |
| Template propio — `Nucleo/Version` + `ArtefactoVersion` / `IVersionadoService` | Versiones de prompts con estados y evaluación | **Reutilizar** para reglas de plataforma (P5) y como modelo visual del historial. |
| crm-olvidata (`docs/crm-olvidata/definiciones/3-arquitecto-mvc.md`) | Prompt generado en prefijo estable cacheado + contexto variable | **Reutilizar** el criterio: el orden de secciones del contexto va de lo más estable a lo más variable (decisión ya aprobada en el diseño de producto). |
| Catálogo de patrones y demás proyectos | Sin reglas de texto por alcance con precedencia, vista previa e instantánea | **Diseño nuevo** → PAT-028 al catálogo. |

### M3-1. Alcance funcional resumido
Reglas de texto con alcance (organización, área, por agente, por cliente, cliente + agente, propias), modo (obligatoria / por defecto en organización y área), tipo (regla / procedimiento), etiquetas, activación, versiones e historial; reglas de plataforma desde el núcleo; vista previa de reglas efectivas al pedir una tarea con cliente opcional; instantánea de reglas en la tarea; vista de solo lectura para staff.

### Decisiones de diseño M3 a validar en el gate
- **D-M3-1 Alcance fijo.** Al editar una regla no se cambia su alcance ni su destino (área, cliente, agente); para eso se crea otra. Evita historiales donde una versión aplicaba a otra gente.
- **D-M3-2 Límites de los alcances "por agente".** Las reglas por agente cuentan dentro del límite de la organización (20.000) y las de cliente + agente dentro del límite del cliente (8.000).
- **D-M3-3 Versiones.** Guardar sin cambios no crea versión. Activar/desactivar queda en el historial como evento, sin versión nueva de texto.
- **D-M3-4 Cliente en Tareas.** El listado de Tareas suma columna y filtro "Cliente"; el detalle muestra el cliente.
- **D-M3-5 Accesos cruzados.** La ficha de un cliente de cartera y la edición de un área muestran sus reglas con acceso directo a "Nueva regla" para ese destino.
- **D-M3-6 Staff.** Ve las reglas de una organización (todas, incluidas las propias de cada miembro, con autor) desde el detalle de la organización en el backoffice, solo lectura; ve el texto de las reglas aplicadas en el detalle de cualquier tarea (P9).
- **D-M3-7 Etiquetas sugeridas.** El campo etiquetas autocompleta con las ya usadas en la organización; máximo 5, en minúscula.

### Flujos de pantalla acordados M3

**Menú:** sección Principal suma **Reglas** (miembros). Staff: acceso desde "Organizaciones y licencias → detalle → Reglas" y reglas de plataforma en **Núcleo IP**.

**P-M3-01 Reglas — listado con pestañas** (miembros)
- Encabezado: "Reglas" · "Orientan a los agentes: cómo trabajar, qué evitar y qué preferís. Una regla nunca da permisos." · botón primario **Nueva regla** (preselecciona el alcance de la pestaña activa, si el usuario puede crearlo).
- Pestañas (se recuerda la última en Session): **Organización** · **Áreas** (Director: todas; Empleado: "Mi área", oculta si no tiene área) · **Por agente** · **Por cliente** (incluye cliente + agente) · **Mías**.
- Indicador de uso bajo las pestañas cuando aplica: "Organización: 12.300 de 20.000 caracteres en reglas activas" (en Áreas y Por cliente, al filtrar un área o un cliente).
- Filtros por columna visible (Session `Reglas_<pestaña>_*`, Limpiar filtros): Título (texto) · Área / Cliente / Agente (Select2, solo en su pestaña) · Modo (Select2, Organización y Áreas) · Tipo (Select2) · Etiqueta (Select2) · Estado (Select2: Activa / Inactiva / No se aplica) · Modificada (daterangepicker).
- Grilla DataTables server-side: Título · destino (Área / Cliente [+ agente] / Agente) · Modo (badge rojo "Obligatoria" / gris "Por defecto") · Tipo · Etiquetas (chips) · Estado (verde Activa / gris Inactiva / ámbar "No se aplica" con tooltip "El área fue dada de baja") · Versión · Modificada (fecha + autor) · acciones: Ver · Editar (si puede) · Activar/Desactivar (si puede; AJAX con confirmación; `reload(null,false)`).
- Solo lectura (Empleado en Organización/Áreas/Por agente): sin botón de alta en esa pestaña ni acciones de edición; aviso `ov-alert info` "Estas reglas las define el Director y se aplican a tus tareas."
- Estado vacío por pestaña: "Todavía no hay reglas de la organización." / "No tenés reglas propias. Usalas para tus preferencias: formato, extensión, idioma."

**P-M3-02 Nueva / editar regla**
- Encabezado: "Nueva regla" / "Editar regla" · "Escribila como se la dirías a una persona del equipo." · Volver.
- Card "Alcance": Alcance* (Select2 con solo los alcances permitidos al rol) · según alcance: Área* · Cliente de cartera* · Agente* (agentes de la suscripción agrupados por rubro). En edición el bloque es solo lectura con hint "Para aplicarla a otro destino, creá una regla nueva." (D-M3-1).
- Card "Contenido": Título* (`col-md-8`, 150) · Tipo* (`col-md-4`, Regla / Procedimiento, hint "Procedimiento: pasos numerados que el agente sigue en orden") · Modo* (solo Organización y Área: Obligatoria / Por defecto, hint "Obligatoria: nadie la puede pisar. Por defecto: una regla más específica la puede reemplazar.") · Texto* (`col-12`, textarea 12 filas, contador "1.234 / 4.000", hint "No cargues contraseñas, claves ni datos bancarios.") · Etiquetas (Select2 con tags, D-M3-7, hint "Agrupan reglas del mismo tema: tono, precios, plazos…").
- Card "Reglas del mismo tema en niveles superiores" (P4): aparece al elegir etiquetas o cambiar alcance; lista reglas activas visibles para el usuario con alguna etiqueta en común y precedencia mayor: título · nivel · modo · "Ver texto" desplegable. Texto explicativo: "Si choca con una obligatoria de más arriba, gana la de más arriba." No bloquea.
- Uso del límite: línea bajo el texto "Reglas activas del cliente Panadería Norte: 3.200 de 8.000 caracteres (con esta regla)".
- Barra sticky: **Guardar** · Cancelar · (edición) espaciador + Desactivar / Activar. En edición hint junto a Guardar: "Guardar crea la versión 4."

**P-M3-03 Detalle de regla con historial** (todos los que pueden verla)
- Encabezado: título de la regla · Volver · Editar (si puede) · Activar/Desactivar (si puede).
- `ov-detail-grid`: Alcance y destino · Tipo · Modo · Etiquetas · Estado (+ motivo si "No se aplica") · Versión actual · Creada (fecha, autor) · Última modificación (fecha, autor).
- Card "Texto" (pre-wrap).
- Card "Historial": tabla Versión / evento · Fecha · Autor · Cambio (Texto, Título, Modo, Tipo, Etiquetas, Activada, Desactivada) · "Ver texto de esta versión" (desplegable).

**P-M3-04 Nueva tarea** (`Agentes/Ejecutar`, rediseñada con el sistema de formularios)
- Encabezado: nombre del agente · descripción · Volver a Agentes.
- Columna izquierda, card "Pedido": Cliente de cartera (Select2 opcional, "Sin cliente", hint "Si elegís un cliente, se aplican sus reglas.") · Pedido* (textarea) · barra: **Enviar tarea**.
- Columna derecha, card "Reglas que se van a aplicar" (vista previa, se recalcula al cambiar el cliente): grupos en orden de precedencia, ocultando los vacíos — "Olvidata" (sin texto: "Se aplican las reglas de Olvidata y del agente.") · Organización (obligatorias) · Área «Marketing» (obligatorias) · Cliente «Panadería Norte» para este agente · Cliente «Panadería Norte» · Este agente · Área «Marketing» (por defecto) · Organización (por defecto) · Mías. Cada ítem: título + tipo + "Ver texto". Pie: "Se guardan con la tarea al enviarla. Si alguien cambia una regla después, esta tarea no cambia." · enlace "Gestionar reglas".
- Sin reglas de la organización: "No hay reglas de tu organización para este pedido."
- Mobile: la vista previa pasa debajo del pedido, colapsada con contador ("7 reglas").

**P-M3-05 Detalle de tarea** (ajuste)
- Encabezado suma "Cliente: Panadería Norte" si tiene.
- Nueva card colapsable "Reglas aplicadas (7)": mismos grupos que la vista previa pero con la **versión usada** de cada regla y su texto de esa versión; badge "Cambió después" si la regla tiene una versión posterior o está inactiva. "Olvidata": sin texto para miembros; con texto y versión para staff (D-M3-6).

**P-M3-06 Tareas — listado** (ajuste D-M3-4): columna y filtro Select2 **Cliente** ("Sin cliente" incluido).

**P-M3-07 Cartera → detalle** y **Áreas → editar** (D-M3-5): card "Reglas de este cliente / de esta área": título · modo/tipo · estado, enlace "Ver todas" (P-M3-01 con filtro) y botón "Nueva regla para este cliente/área" (si puede).

**P-M3-08 Backoffice → organización → Reglas** (staff, solo lectura, D-M3-6): misma grilla de P-M3-01 con pestaña adicional **De miembros** (reglas propias de todos, columna Autor), sin acciones de edición; Ver abre P-M3-03 en lectura.

**P-M3-09 Núcleo IP → reglas de plataforma** (staff): las reglas de plataforma aparecen como un artefacto más del núcleo, con el flujo existente de versiones, evaluación y publicación; sin formulario de edición en el portal (P5).

### ViewModels definidos M3
| ViewModel | Campos y validaciones |
|---|---|
| `ReglaListItem` (JSON) | `id, titulo, destino, modo, tipo, etiquetas[], estado, motivoNoAplica, version, modificada, autor, puedeEditar` |
| `ReglaFormViewModel` | `Id?` · `Alcance` [Required "Elegí el alcance."] · `AreaId?` · `ClienteCarteraId?` · `AgenteRef?` (rubro/slug) · `Titulo` [Required "Ingresá un título."] [StringLength 150] · `Tipo` [Required] · `Modo?` (requerido si alcance Organización/Área: "Elegí si la regla es obligatoria o por defecto.") · `Texto` [Required "Escribí el texto de la regla."] [StringLength 4000 "La regla admite hasta 4.000 caracteres."] · `Etiquetas` (≤ 5, ≤ 30 c/u) · `VersionActual` · `Activa` · combos permitidos · `UsoAlcance` (usados/límite) |
| `ReglaDetalleViewModel` | datos de la regla + `Historial[]` (`Numero?`, `Evento`, `Fecha`, `Autor`, `CamposCambiados`, `Texto`) + `PuedeEditar` |
| `ReglasMismoTemaItem` (JSON) | `titulo, nivel, modo, texto` |
| `VistaPreviaReglasViewModel` | `Grupos[]` (`Nivel`, `Rotulo`, `Items[]`: `ReglaId`, `Titulo`, `Tipo`, `Version`, `Texto`, `CambioDespues`) · `IncluyeOlvidata` · `TotalCaracteres` |
| `EjecutarAgenteViewModel` (cambio) | + `ClienteCarteraId?` · `ClientesOpciones` · `VistaPrevia` |
| `TareaDetalle` (cambio) | + `Cliente?` · `ReglasAplicadas` (`VistaPreviaReglasViewModel` desde la instantánea) |

### Validaciones de UI M3
| Caso | Mensaje |
|---|---|
| Alcance sin destino | "Elegí el área." / "Elegí el cliente." / "Elegí el agente." |
| Destino de otra organización o dado de baja | "El área elegida no existe." / "El cliente elegido no existe." |
| Agente fuera de la suscripción | "Ese agente no está habilitado en la suscripción de tu organización." |
| Sin permiso para el alcance | "Solo un Director puede crear o cambiar reglas de organización, de área o por agente." (403) |
| Texto > 4.000 | "La regla admite hasta 4.000 caracteres." |
| Supera límite del alcance (al guardar o activar) | "Con esta regla se superan los 20.000 caracteres de reglas activas de la organización (quedan 1.250). Acortala o desactivá otra." (variantes: área 20.000, cliente 8.000, tus reglas 8.000) |
| Etiquetas | "Hasta 5 etiquetas de 30 caracteres cada una." |
| Cliente inválido al pedir tarea | "El cliente elegido no existe." |
| OK | "Regla creada." / "Regla actualizada: versión 4." / "No hubo cambios; la regla sigue en la versión 3." / "Regla desactivada." / "Regla activada." |
| Confirmación desactivar | "¿Desactivar «Tono formal»? Deja de aplicarse en las tareas nuevas; las tareas ya creadas no cambian." |

### Maquina de estados M3
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| Activa | Desactivar | Inactiva | permiso sobre el alcance | evento en historial | sin permiso |
| Inactiva | Activar | Activa | permiso; destino vigente; no supera límite | evento en historial | límite / destino dado de baja / sin permiso |
| Activa | Editar con cambios | Activa (versión N+1) | permiso; límite | nueva versión | límite / sin permiso |
| Activa | Baja del área/cliente o bloqueo del autor (reglas propias) | Activa pero "No se aplica" | — | deja de aplicarse (derivado) | — |

### Permisos por pantalla / accion M3
| Pantalla / acción | Director | Empleado | Staff |
|---|:---:|:---:|:---:|
| P-M3-01 pestañas Organización, Por agente | ✅ editar | 👁 | 👁 (P-M3-08) |
| P-M3-01 pestaña Áreas | ✅ todas, editar | 👁 solo su área | 👁 |
| P-M3-01 pestaña Por cliente | ✅ editar todas | ✅ editar todas (P2) | 👁 |
| P-M3-01 pestaña Mías | ✅ solo propias | ✅ solo propias | 👁 todas con autor (De miembros) |
| P-M3-02 crear/editar | según pestaña | Por cliente y Mías | ❌ |
| P-M3-03 detalle/historial | ✅ | lo que puede ver | ✅ |
| P-M3-04 vista previa | ✅ | ✅ | — (no crea tareas) |
| P-M3-05 reglas aplicadas | tareas visibles; Olvidata sin texto | sus tareas; Olvidata sin texto | todas con texto |
| P-M3-09 reglas de plataforma | — | — | ✅ núcleo |

### Contratos funcionales para Services M3
| Contrato | Operaciones | Reglas que garantiza |
|---|---|---|
| Reglas | listar por pestaña con filtros · obtener detalle con historial · crear · editar (versión si hay cambios) · activar · desactivar · uso del límite por alcance/destino · reglas del mismo tema en niveles superiores · etiquetas usadas | RF-M3-01, 02, 05, 06, 10, 12; P1, P2, P4; D-M3-1..3, 7 |
| Permisos de organización (extensión) | puede ver / editar regla según alcance y rol · staff lectura de reglas | matriz M3 |
| Constructor de contexto | calcular reglas efectivas para (usuario, agente, cliente?) en orden de precedencia · armar prompt de sistema por secciones · hash | RF-M3-03, 04, 05, 09, 11; único cálculo para vista previa, instantánea y motor (R-M3-03) |
| Tareas (extensión) | crear con cliente opcional guardando instantánea · detalle con reglas aplicadas y "cambió después" · listar con filtro cliente | RF-M3-07, 08; D-M3-4 |
| Núcleo (extensión) | importar/evaluar/publicar reglas de plataforma · obtener publicada vigente | P5 |

Eventos a registrar: regla creada / nueva versión / activada / desactivada; tarea creada con hash de contexto.

### M3-6. Impacto funcional por capa
- **Presentación:** pantallas P-M3-01..03 y 08, Nueva tarea rediseñada con vista previa, detalle y listado de tareas, cards de reglas en Cartera y Áreas, menú.
- **Negocio:** permisos por alcance, límites, versiones, reglas del mismo tema, constructor de contexto único, instantánea.
- **Datos:** reglas, versiones/eventos, etiquetas, reglas de plataforma como artefacto del núcleo, cliente e instantánea en la tarea.

### M3-7. Riesgos y supuestos
- R-M3-01..R-M3-05 heredados del análisis (inyección, costo, deriva, datos sensibles, contradicciones).
- R-M3-06 (medio, nuevo) la vista previa se recalcula por AJAX en cada cambio de cliente: debe usar exactamente el mismo cálculo que la instantánea.
- R-M3-07 (bajo, nuevo) muchas reglas por pestaña en organizaciones grandes: grilla server-side cubre.
- S-M3-01..03 heredados (agente de la suscripción, texto libre, costo controlado por límites y caché).
- Decisiones D-M3-1..D-M3-7 pendientes de validar.

### M3-8. Plan funcional por etapas (para el arquitecto)
1. Reglas: datos, versiones, permisos por alcance, límites, etiquetas.
2. Pantallas de reglas (P-M3-01..03) + cards en Cartera/Áreas (P-M3-07).
3. Constructor de contexto + reglas de plataforma del núcleo (P-M3-09).
4. Nueva tarea con cliente y vista previa (P-M3-04) + instantánea.
5. Detalle y listado de tareas (P-M3-05, 06) + vista de staff (P-M3-08).

### Historias de usuario M3
- **HU-M3-01** Como Director, quiero crear reglas obligatorias y por defecto para toda la organización, para que todos los agentes trabajen con nuestros criterios. *CA:* CA-M3-01, CA-M3-10; el modo es obligatorio en este alcance.
- **HU-M3-02** Como Director, quiero reglas por área para adaptar los agentes a cada sector. *CA:* CA-M3-03; un área dada de baja deja sus reglas en "No se aplica" (CA-M3-09).
- **HU-M3-03** Como Director, quiero reglas de la organización para un agente puntual. *CA:* solo aplican a tareas de ese agente; un Empleado las ve sin editar (P1); agente fuera de la suscripción da el mensaje.
- **HU-M3-04** Como miembro, quiero reglas para un cliente de cartera, generales o para un agente, para respetar lo que pide cada cliente. *CA:* CA-M3-04, CA-M3-05; cualquier miembro edita y desactiva las de otros y el historial muestra el autor (P2).
- **HU-M3-05** Como miembro, quiero mis reglas propias para mis preferencias personales. *CA:* CA-M3-06; límite 8.000.
- **HU-M3-06** Como Empleado, quiero ver las reglas de la organización, de mi área y por agente, para saber qué se aplica a mis tareas. *CA:* CA-M3-02; ve también las por defecto (P8).
- **HU-M3-07** Como miembro, quiero cargar procedimientos paso a paso. *CA:* tipo Procedimiento visible en grilla y detalle; en la vista previa aparece rotulado como procedimiento (P6).
- **HU-M3-08** Como miembro, quiero ver al guardar si hay reglas del mismo tema en niveles superiores, para evitar contradicciones. *CA:* con una etiqueta en común aparece la lista; sin coincidencias no aparece; nunca bloquea (P4).
- **HU-M3-09** Como miembro, quiero editar una regla sin perder lo anterior. *CA:* CA-M3-07; sin cambios no hay versión nueva; no se puede cambiar el alcance (D-M3-1).
- **HU-M3-10** Como miembro, quiero desactivar y reactivar reglas. *CA:* CA-M3-08; reactivar que supera el límite muestra el mensaje y no activa; la acción conserva la página de la grilla.
- **HU-M3-11** Como miembro, quiero elegir un cliente al pedir una tarea y ver antes de enviar qué reglas se aplican. *CA:* CA-M3-12; la vista previa respeta el orden de precedencia; las reglas de Olvidata aparecen sin texto.
- **HU-M3-12** Como miembro, quiero ver en el detalle de una tarea qué reglas y versiones se usaron. *CA:* CA-M3-11, CA-M3-13; badge "Cambió después" si la regla cambió.
- **HU-M3-13** Como miembro, quiero filtrar mis tareas por cliente. *CA:* D-M3-4; incluye "Sin cliente".
- **HU-M3-14** Como staff de Olvidata, quiero ver todas las reglas de una organización y el texto de las reglas aplicadas en sus tareas, para controlar cómo configuran los prompts. *CA:* D-M3-6; sin acciones de edición; pestaña De miembros con autor.
- **HU-M3-15** Como staff de Olvidata, quiero publicar las reglas de plataforma con el flujo de evaluación del núcleo. *CA:* P5; una versión no evaluada no se publica; la publicada vigente se aplica primero en toda tarea nueva.
- **Transversal** CA-M3-14 (ids de otra organización → 404) y CA-M3-15 (texto con marcadores no rompe el contexto) aplican a HU-M3-01..12.

---

# M2 — Organización del portal

**M2 — Organización del portal.** Estado: **aprobado por Joaquín el 2026-09-14 con D-1..D-5 tal como están.** Entrada: `1-analista-funcional.md` aprobado 2026-09-14.

### 0. Escaneo de reutilizacion
| Fuente | Qué hay | Decisión |
|---|---|---|
| century-21 (`docs/century-21/definiciones/2-disenador-funcional.md`, `3-arquitecto-mvc.md`) | SaaS multi-agencia: tenant resuelto desde el usuario logueado, validación de pertenencia al tenant en toda escritura (anti-IDOR), gestión de asesores por grupo | **Reutilizar el criterio**: la organización nunca viaja en la request; todo id recibido se valida contra la organización de la sesión. Su modelo de roles plano (SuperAdmin/Asesor) no aplica. |
| `patrones/catalogo.yml` PAT-017 | Scoping forzado por identidad (id de la entidad nunca desde la URL) | **Reutilizar el principio** para Áreas, Miembros, Cartera y Tareas. El resto del patrón (portal de usuario final) no aplica. |
| la-platense — sistema de formularios de `FerreteriaLaPlatense.Web/wwwroot/css/site.css` (`.ov-page-head`, `.ov-form-page`, `.ov-form-actions`, `.ov-required`, `.ov-field-hint`, `.ov-detail-grid`) | Regla obligatoria de formularios (instrucción 25) | **Portar al template**: hoy `OlvidataAgentes.Web` no tiene esas clases (solo `.ov-page-header`). |
| la-platense `ProductosController` (PAT-015 bajas AJAX) y filtros en Session (delicias-naturales / PAT-016) | Listado DataTables con baja AJAX `ajax.reload(null,false)` y filtros persistidos | **Reutilizar** en Áreas, Miembros, Cartera y Tareas. |
| Template propio: `UsersController` + `Views/Users/*` (blankproject) | Listado de usuarios con estado Activo/Bloqueado | **Base** para el listado de Miembros (misma interacción de bloqueo, pero AJAX y acotado a la organización). |
| Jerarquía de roles dentro de un tenant con invariante "al menos un responsable activo" y refresco de sesión | Sin precedente en ningún proyecto | **Diseño nuevo** → se agrega **PAT-027** al catálogo (pendiente de verificar al implementar). |

### 1. Alcance funcional resumido
Rol de organización (Director/Empleado) y área opcional por miembro; ABM de Áreas (Director); gestión de miembros existentes (Director: rol, área, bloqueo); alta de miembros solo SuperUsuario desde el backoffice; cartera de clientes de la organización (todos ven/editan, baja solo Director); visibilidad de tareas por rol; menú y perfil según rol.

### Decisiones de diseño a validar en el gate
- **D-1 Nombre del backoffice.** "Clientes y licencias" pasa a **"Organizaciones y licencias"** (solo texto de UI). Motivo: con la cartera, "cliente" pasa a significar el cliente de la organización; mantener las dos acepciones confunde.
- **D-2 Staff sobre Áreas y Cartera.** En el backoffice, el detalle de la organización muestra Áreas y la cantidad de clientes de cartera **en solo lectura**. El staff no crea, edita ni da de baja áreas o clientes de cartera de una organización (ajusta la matriz del análisis, que marcaba ✅). Motivo: el staff no tiene organización en sesión y esas operaciones son del día a día del cliente.
- **D-3 Tareas a DataTables.** Como M2 toca el listado de Tareas (columna "Pedida por"), se migra a DataTables server-side con filtros por columna, para cumplir la regla de listados. Suma alcance acotado.
- **D-4 Pantalla "Usuarios" del SuperUsuario.** Queda solo para staff de Olvidata (usuarios sin organización). Los miembros de organizaciones se ven y se dan de alta desde el detalle de la organización.
- **D-5 Sistema de formularios.** Se porta de la-platense al template (D-4 del escaneo); beneficia a todas las pantallas actuales y futuras.

### Flujos de pantalla acordados

**Menú lateral**
| Sección | Ítem | Visible para |
|---|---|---|
| Principal | Inicio, Agentes, Tareas | todos |
| Principal | **Cartera de clientes** | miembros (Director y Empleado) |
| **Mi organización** | **Miembros**, **Áreas** | Director |
| Olvidata | **Organizaciones y licencias**, Núcleo IP, Uso y consumo | SuperUsuario, Administrador |
| Super Usuario | Usuarios (solo staff), Conexiones, Sistema | SuperUsuario |

**P-01 Áreas — listado** (`Mi organización > Áreas`, Director)
- Encabezado: "Áreas" · "Agrupan a los miembros de tu organización. En la próxima etapa cada área va a tener sus reglas generales." · botón primario **Nueva área**.
- Filtros (card): Nombre (texto), Descripción (texto), Miembros (Select2: Todas / Con miembros / Sin miembros) · **Limpiar filtros**. Persistidos en Session (`Areas_*`).
- Grilla DataTables server-side: Nombre · Descripción (recortada a 80 caracteres) · Miembros (número, enlace a Miembros filtrado por esa área) · acciones Editar / Dar de baja.
- Dar de baja: SweetAlert2 "¿Dar de baja el área «Ventas»? Sus 3 miembros van a quedar sin área." (si tiene 0: "¿Dar de baja el área «Ventas»?") → AJAX → `ajax.reload(null, false)` → toast con resultado.
- Estado vacío: "Todavía no hay áreas. Creá la primera para agrupar a los miembros."

**P-02 Áreas — alta / edición**
- Encabezado: "Nueva área" / "Editar área" · "Nombre y descripción del área." · Volver.
- Card "Datos del área": Nombre* (`col-md-6`, autofocus en alta) · Descripción (`col-12`, textarea 3 filas, hint "Para qué existe el área. Opcional.").
- En edición, línea informativa: "3 miembros en esta área" con enlace a Miembros filtrado.
- Barra sticky: **Guardar** · Cancelar · (edición) espaciador + **Dar de baja** (rojo, con la misma confirmación de P-01; al confirmar vuelve al listado).

**P-03 Miembros — listado** (`Mi organización > Miembros`, Director)
- Encabezado: "Miembros" · "Personas de tu organización que usan el portal." Sin botón de alta; `ov-alert info`: "Para sumar a alguien al portal, pedíselo a Olvidata."
- Filtros: Nombre (texto), Email (texto), Rol (Select2), Área (Select2 con "Sin área"), Estado (Select2), Último acceso (daterangepicker) · Limpiar filtros. Session `Miembros_*`. Admite `?areaId=` desde P-01/P-02 (se vuelca al filtro).
- Grilla: Nombre (badge "Vos" en la fila propia) · Email · Rol (badge) · Área ("Sin área" en gris) · Estado (badge verde/rojo) · Último acceso (dd/MM/yyyy HH:mm, "Nunca") · acciones Editar / Bloquear o Desbloquear.
- Bloquear/Desbloquear: SweetAlert2 ("Se va a bloquear a «Ana Pérez». No va a poder usar el portal y, si tiene la sesión abierta, la pierde.") → AJAX → `reload(null,false)`. No aparece la acción en la fila propia.

**P-04 Miembros — edición** (Director)
- Encabezado: "Editar miembro" · nombre del miembro · Volver.
- Card "Datos de la persona" (solo lectura, `ov-detail-grid`): Nombre, Email, Estado, Alta, Último acceso. Hint: "Nombre y email los modifica Olvidata."
- Card "Rol y área": Rol* (Select2: Director / Empleado, hint "El Director administra áreas y miembros, ve todas las tareas y puede dar de baja clientes.") · Área (Select2: "Sin área" + áreas vigentes de la organización).
- Barra sticky: Guardar · Cancelar. El bloqueo vive solo en el listado (una sola forma de hacerlo).
- Si el Director se quita a sí mismo el rol (habiendo otro Director): confirmación "Vas a dejar de ser Director y ya no vas a ver Mi organización. ¿Continuar?" → guarda → redirige a Inicio con mensaje.

**P-05 Cartera de clientes — listado** (miembros)
- Encabezado: "Cartera de clientes" · "Los clientes que atiende tu organización. Todos los miembros los ven." · botón primario **Nuevo cliente**.
- Filtros: Nombre, Identificación, Email, Teléfono (texto) · Alta (daterangepicker) · Limpiar filtros. Session `Cartera_*`.
- Grilla: Nombre · Identificación ("CUIT 20-12345678-3" / "DNI 12.345.678" / "—") · Email · Teléfono · Alta (dd/MM/yyyy) · acciones Ver / Editar / Dar de baja (**solo Director**). Búsqueda global también por fecha de alta y por número de identificación con o sin guiones/puntos.
- Dar de baja: "¿Dar de baja a «Martínez SRL» de la cartera? Deja de aparecer en el listado." → AJAX → `reload(null,false)`.
- Estado vacío: "La cartera está vacía. Cargá el primer cliente."

**P-06 Cartera — alta / edición**
- Encabezado: "Nuevo cliente" / "Editar cliente" · Volver.
- Card "Datos del cliente": Nombre o razón social* (`col-md-8`, autofocus) · Tipo de identificación (Select2: Sin identificación / CUIT / DNI, `col-md-4`) · Número (`col-md-4`, hint "CUIT: 11 dígitos. DNI: 7 u 8 dígitos. Podés pegarlo con guiones o puntos.").
- Card "Contacto (opcional)": Email (`col-md-6`) · Teléfono (`col-md-6`) · Dirección (`col-12`).
- Card "Notas (opcional)": Notas (`col-12`, textarea 4 filas, hint "Datos útiles para el equipo. No cargues contraseñas ni claves.").
- Barra sticky: Guardar · Cancelar · (edición y Director) espaciador + Dar de baja.

**P-07 Cartera — detalle**
- Encabezado: nombre del cliente · Volver · Editar (secundario) · Dar de baja (Director, rojo).
- `ov-detail-grid`: Nombre, Identificación, Email, Teléfono, Dirección, Notas (vacíos con "No informado"/"Sin notas"), Cargado por, Alta, Última modificación.

**P-08 Backoffice — detalle de organización** (existente `Clientes/Details`, renombrado en UI)
- Card "Miembros del portal": tabla con Nombre · Email · Rol · Área · Estado (reemplaza la lista simple actual).
- Card "Nuevo miembro" (**solo SuperUsuario**; el Administrador no la ve): Nombre* · Email* · Contraseña inicial* · Rol* (si la organización no tiene miembros: fijo en Director con hint "El primer miembro tiene que ser Director.") · Área (Select2 con áreas de esa organización; oculto si no tiene áreas).
- Card "Estructura" (solo lectura): áreas con cantidad de miembros; "Clientes en cartera: N".

**P-09 Tareas — listado** (ajuste M1)
- Grilla DataTables server-side: N° · Agente · Estado · Pedido (entrada recortada) · **Pedida por** (solo Director) · Creada · Costo. Filtros por cada columna (Agente y Estado Select2, Pedida por Select2 de miembros, Creada daterangepicker, Pedido texto, N° texto, Costo rango numérico) · Limpiar filtros · Session `Tareas_*`. Costo ordenable por valor numérico.
- Empleado: sin columna ni filtro "Pedida por"; solo sus tareas.

**P-10 Mi perfil** (existente): agrega Organización, Rol y Área (solo lectura, "Sin área").

**Accesos denegados:** Empleado en P-01..P-04 → pantalla 403 existente (`Account/AccessDenied`). Acción AJAX no permitida → HTTP 403 con `{ success:false, message }`. Recurso de otra organización o tarea ajena (Empleado) → 404.

### ViewModels definidos
| ViewModel | Campos y validaciones |
|---|---|
| `AreaFormViewModel` | `Id?` · `Nombre` [Required "Ingresá el nombre del área."] [StringLength 100 "El nombre admite hasta 100 caracteres."] · `Descripcion?` [StringLength 500] · `CantidadMiembros` (solo lectura en edición) |
| `AreaListItem` (JSON grilla) | `id, nombre, descripcion, cantidadMiembros` |
| `MiembroListItem` (JSON grilla) | `id, nombre, email, rol, area, estado, ultimoAcceso, esUnoMismo` |
| `MiembroEditarViewModel` | `Id` · `FullName`, `Email`, `Estado`, `CreatedAt`, `UltimoAcceso` (solo lectura) · `Rol` [Required "Elegí el rol."] · `AreaId?` · `AreasDisponibles` · `EsUnoMismo` |
| `MiembroCrearViewModel` (backoffice) | `TenantId` · `FullName` [Required "Ingresá el nombre."] [StringLength 150] · `Email` [Required] [EmailAddress "Ingresá un email válido."] · `Password` [Required] [DataType Password] · `Rol` [Required] · `AreaId?` · `AreasDisponibles` · `EsPrimerMiembro` |
| `ClienteCarteraFormViewModel` | `Id?` · `Nombre` [Required "Ingresá el nombre o la razón social."] [StringLength 200] · `TipoIdentificacion` (Ninguna/Cuit/Dni) · `NumeroIdentificacion?` [StringLength 20] · `Email?` [EmailAddress] [StringLength 150] · `Telefono?` [StringLength 40] · `Direccion?` [StringLength 250] · `Notas?` [StringLength 2000] · `PuedeDarDeBaja` |
| `ClienteCarteraDetalleViewModel` | lo anterior + `IdentificacionFormateada`, `CargadoPor`, `CreatedAt`, `UpdatedAt`, `PuedeDarDeBaja` |
| `ClienteCarteraListItem` (JSON grilla) | `id, nombre, identificacion, email, telefono, alta` |
| `TareaListItem` (JSON grilla) | `id, agente, estado, entrada, pedidaPor?, creada, costoUsd` |
| `PerfilViewModel` (existente) | + `Organizacion?`, `RolOrganizacion?`, `Area?` |

Ninguna vista usa entidades de Domain.

### Validaciones de UI acordadas
| Caso | Mensaje |
|---|---|
| Nombre de área repetido en la organización | "Ya existe un área con ese nombre en tu organización." |
| Degradar o bloquear al último Director activo | "La organización tiene que tener al menos un Director activo. Asigná otro Director antes de hacer este cambio." |
| Bloquearse a sí mismo | "No podés bloquear tu propia cuenta." |
| Área inexistente o de otra organización | "El área elegida no existe." |
| Primer miembro no Director (backoffice) | "El primer miembro de una organización tiene que ser Director." |
| Email ya usado (backoffice) | "Ya existe un usuario con ese email." |
| Tipo elegido sin número | "Ingresá el número de identificación." |
| Número sin tipo | "Elegí el tipo de identificación." |
| CUIT inválido (longitud o dígito verificador) | "El CUIT no es válido: tiene que tener 11 dígitos y un dígito verificador correcto." |
| DNI inválido | "El DNI tiene que tener 7 u 8 dígitos." |
| Identificación repetida en la cartera | "Ya hay un cliente con esa identificación en la cartera." |
| Empleado intenta dar de baja un cliente | "Solo un Director puede dar de baja clientes." (403) |
| Guardado OK | "Área creada." / "Área actualizada." / "Área dada de baja. N miembros quedaron sin área." / "Miembro actualizado." / "Miembro bloqueado." / "Miembro desbloqueado." / "Cliente cargado." / "Cliente actualizado." / "Cliente dado de baja." / "Miembro creado." |

Normalización: el número de identificación se guarda solo con dígitos (se quitan guiones, puntos y espacios) y se muestra formateado. Email en minúsculas y sin espacios.

### Maquina de estados
No hay máquina de estados de negocio. Tabla del único cambio de estado con guarda:

| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| Activo | Bloquear (Director o staff) | Bloqueado | mismo tenant; no es uno mismo; si es Director, queda otro Director activo | invalida la sesión del miembro | último Director / propia cuenta |
| Bloqueado | Desbloquear | Activo | mismo tenant | — | — |
| Empleado | Cambiar rol a Director | Director | mismo tenant | refresca sesión del miembro | — |
| Director | Cambiar rol a Empleado | Empleado | queda otro Director activo | refresca sesión; si es uno mismo, redirige a Inicio | último Director |

### Reglas de negocio y permisos por pantalla / accion
| Pantalla / acción | Director | Empleado | SuperUsuario | Administrador |
|---|:---:|:---:|:---:|:---:|
| P-01/P-02 Áreas | ✅ | 403 | — (lectura en P-08) | — (lectura en P-08) |
| P-03 Miembros: ver, bloquear | ✅ | 403 | — (en P-08) | — |
| P-04 Miembros: rol y área | ✅ | 403 | — | — |
| P-05..P-07 Cartera: ver, alta, edición | ✅ | ✅ | — (cantidad en P-08) | — |
| Cartera: dar de baja | ✅ | 403 | — | — |
| P-08 Alta de miembro | — | — | ✅ | ❌ |
| P-08 Ver miembros y estructura | — | — | ✅ | ✅ |
| P-09 Tareas | todas de la organización | propias | todas | todas |

Reglas transversales: la organización se toma siempre de la sesión; todo id recibido (área, miembro, cliente, tarea) se busca dentro de esa organización y, si no está, se responde 404. Los permisos los decide el servicio de negocio; controllers y vistas solo consultan los mismos permisos para mostrar u ocultar acciones.

### Logica de distribucion de elementos en pantalla
- priorizar simplicidad visual y comprension inmediata del flujo
- ubicar primero informacion y acciones criticas; dejar secundario en segundo plano
- mantener jerarquia consistente (titulo, contexto, formulario, acciones)
- reducir ruido visual: evitar bloques redundantes y opciones duplicadas
- reutilizar este criterio de distribucion en todas las pantallas del sistema
- M2: listados = encabezado con acción primaria → card de filtros con "Limpiar filtros" → grilla con acciones por fila (destructivas en rojo y con confirmación); formularios = encabezado → cards por bloque → barra sticky (primaria, Cancelar, espaciador, destructiva); una sola forma de ejecutar cada acción (bloqueo solo en el listado de miembros).

### Contratos funcionales para Services
| Contrato | Operaciones funcionales | Reglas que garantiza |
|---|---|---|
| Permisos de organización | ¿es staff? · ¿es miembro? · ¿es Director? · puede gestionar áreas · puede gestionar miembros · puede dar de baja clientes de cartera · puede ver todas las tareas · puede dar de alta miembros (SuperUsuario) | matriz de permisos; única fuente de verdad para servicios, controllers y vistas |
| Áreas | listar paginado con filtros · obtener · crear · editar · dar de baja (devuelve cuántos miembros quedaron sin área) · contar miembros · listar para combo | RF-03, RF-04, RF-10 |
| Miembros | listar paginado con filtros · obtener para editar · cambiar rol y área · cambiar estado · crear (solo SuperUsuario, con organización explícita) | RF-02, RF-05, RF-06, RF-07, RF-10, RF-11 |
| Cartera de clientes | listar paginado con filtros · obtener · crear · editar · dar de baja | RF-08, RF-09, RF-10 |
| Tareas (ajuste M1) | listar paginado con filtros según rol · obtener detalle · cancelar | RF-12 (Empleado: solo propias, otra → no existe) |

Eventos de negocio a registrar (log/auditoría existente): área creada/editada/dada de baja; rol o área de miembro cambiados; miembro bloqueado/desbloqueado; miembro creado por staff; cliente de cartera creado/editado/dado de baja.

### 6. Impacto funcional por capa
- **Presentación:** pantallas P-01..P-10, menú por rol, renombre del backoffice, sistema de formularios portado, Tareas a DataTables, respuestas 403/404 consistentes.
- **Negocio:** contratos de Permisos, Áreas, Miembros, Cartera; ajuste de Tareas; invariante del último Director; normalización y validación de CUIT/DNI; invalidación/refresco de sesión del miembro afectado.
- **Datos:** rol de organización y área opcional en el usuario; Área (nombre único por organización entre vigentes, baja lógica); Cliente de cartera (identificación única por organización entre vigentes, baja lógica, quién lo cargó); consultas de miembros siempre filtradas por organización.

### 7. Riesgos y supuestos
- R-01 (alto, heredado) usuarios sin filtro automático por organización → toda consulta de miembros acotada explícitamente; QA con ids manipulados.
- R-02 (medio, heredado) RF-11 exige que el cambio impacte en la próxima request; la revalidación actual de sesión es cada 5 minutos → el arquitecto define el mecanismo.
- R-03 (medio, heredado) carrera: dos Directores se degradan al mismo tiempo y la organización queda sin Director → el arquitecto define cómo se garantiza la invariante bajo concurrencia.
- R-05 (bajo, nuevo) portar el sistema de formularios puede alterar pantallas existentes → verificar en navegador las pantallas actuales.
- S-01 (heredado, no confirmado) una persona pertenece a una sola organización.
- Decisiones D-1..D-5 pendientes de validación en el gate.

### 8. Plan funcional por etapas (para el arquitecto)
1. **Base de organización:** rol y área del miembro en sesión, permisos, datos de Área y Cliente de cartera, sistema de formularios portado, menú y perfil.
2. **Áreas** (P-01, P-02).
3. **Miembros** (P-03, P-04) + **alta de miembros en backoffice** (P-08) + Usuarios solo staff (D-4) + renombre (D-1).
4. **Cartera de clientes** (P-05..P-07).
5. **Tareas por rol** (P-09).

### Historias de usuario
- **HU-01** Como miembro, quiero que el portal me muestre solo las opciones de mi rol para no ver acciones que no puedo usar. *CA:* CA-01.1; CA-01.2; Mi perfil muestra organización, rol y área.
- **HU-02** Como Director, quiero crear áreas para agrupar a los miembros de mi organización. *CA:* CA-02.1; nombre vacío o de más de 100 caracteres no se guarda; al guardar vuelve al listado con "Área creada.".
- **HU-03** Como Director, quiero editar un área para corregir su nombre o descripción. *CA:* CA-02.2; nombre repetido muestra el mensaje y no guarda; un id de otra organización devuelve 404.
- **HU-04** Como Director, quiero dar de baja un área sin perder a sus miembros. *CA:* CA-02.3; la baja no recarga la página ni cambia la página de la grilla; el mensaje informa cuántos miembros quedaron sin área.
- **HU-05** Como Director, quiero buscar y filtrar áreas y ver cuántos miembros tiene cada una. *CA:* CA-02.4; cada columna tiene filtro; los filtros se conservan al volver; "Limpiar filtros" los vacía y no reaparecen.
- **HU-06** Como Director, quiero ver a los miembros de mi organización con su rol, área y estado. *CA:* CA-03.1; CA-03.5; filtros por cada columna, incluido "Sin área" y rango de último acceso; mi fila tiene la marca "Vos" y no tiene acción de bloqueo.
- **HU-07** Como Director, quiero cambiar el rol y el área de un miembro para reflejar la estructura real. *CA:* CA-03.2; CA-03.3; CA-03.5; si me quito el rol de Director (habiendo otro) se me pide confirmación y vuelvo a Inicio sin "Mi organización".
- **HU-08** Como Director, quiero bloquear o desbloquear a un miembro para cortar o devolver su acceso. *CA:* CA-03.3; CA-03.4; la acción es AJAX con confirmación y conserva la página de la grilla.
- **HU-09** Como SuperUsuario de Olvidata, quiero dar de alta miembros de una organización con su rol y área. *CA:* CA-06.1; CA-06.2; CA-06.3; email repetido muestra "Ya existe un usuario con ese email."; el miembro creado aparece en la card de miembros con su rol y área.
- **HU-10** Como miembro, quiero cargar un cliente en la cartera con todos sus datos. *CA:* CA-04.1; CA-04.2; CUIT/DNI se aceptan con guiones o puntos y se validan (CUIT con dígito verificador); tipo sin número o número sin tipo no se guarda.
- **HU-11** Como miembro, quiero buscar un cliente de la cartera y ver su ficha. *CA:* CA-04.4; la búsqueda global encuentra por identificación con o sin separadores y por fecha de alta; la ficha muestra "No informado" en los datos vacíos y quién lo cargó.
- **HU-12** Como miembro, quiero editar los datos de un cliente de la cartera. *CA:* CA-04.1; CA-04.2; un id de otra organización devuelve 404.
- **HU-13** Como Director, quiero dar de baja un cliente de la cartera. *CA:* CA-04.3; la baja es AJAX con confirmación y conserva la página; el cliente deja de aparecer en listado y combos.
- **HU-14** Como Director, quiero ver las tareas de todos los miembros para seguir el trabajo de la organización. *CA:* CA-05.1; columna y filtro "Pedida por"; filtros por cada columna y persistencia.
- **HU-15** Como Empleado, quiero ver solo mis tareas. *CA:* CA-05.2; sin columna "Pedida por".
- **HU-16** Como staff de Olvidata, quiero ver la estructura de una organización (miembros, áreas, cantidad de clientes) desde el backoffice. *CA:* D-2; el Administrador ve la información pero no la card de alta; el menú dice "Organizaciones y licencias".
- **Transversal** CA-T.1 aplica a HU-03, HU-04, HU-07, HU-08, HU-12, HU-13, HU-15.

## Historial de ajustes
- 2026-09-14: Diseño de M2 Organización: 10 pantallas, 10 ViewModels, 16 historias, contratos de Permisos/Áreas/Miembros/Cartera/Tareas. Reutiliza century-21 (scoping anti-IDOR), PAT-017, sistema de formularios y bajas AJAX de la-platense, Users del template. Decisiones D-1..D-5 a validar. Nuevo PAT-027 en catálogo.
- 2026-09-14: Gate aprobado por Joaquín ("continuar"): D-1..D-5 aceptadas sin cambios.
- 2026-09-14: Diseño de M3 Reglas por alcance: 9 pantallas/ajustes, 7 ViewModels, 15 historias, contratos de Reglas/Constructor de contexto/Tareas/Núcleo. Decisiones D-M3-1..D-M3-7 a validar. Nuevo PAT-028 en catálogo.
- 2026-09-14: Gate M3 aprobado por Joaquín. Se suman ajustes de simplificación D-M3-8..D-M3-12 (nombres llanos, "Siempre / Salvo que se indique otra cosa", opciones avanzadas plegadas, vista previa "Esto es lo que el agente va a tener en cuenta") a partir de su objetivo de reemplazar el uso de Claude web con algo más simple.
- 2026-09-14: Diseño de M3b Seguir conversando: detalle de tarea como conversación con cuadro de ajuste, listado con mensajes y última actividad, atajo a nueva tarea, preferencias ajenas como contador. Decisiones D-M3b-1..7 a validar. Nuevo PAT-029.
- 2026-09-14: Diseño de M4 Agentes de la organización: catálogo por secciones, formulario único, detalle con historial, propuestas y revisión lado a lado, sugerencias de Olvidata, vistas de staff. 10 pantallas/ajustes, 8 ViewModels, 14 historias. Decisiones D-M4-1..10 a validar. Nuevo PAT-030.
- 2026-09-14: Diseño de M4b Agente configurador de reglas: conversación M3b con tarjetas de propuesta (aplicar, editar y aplicar, descartar, aplicar todas), lista de conversaciones compartida entre Directores, arranque con chips, verificación de cambios, origen en historial, filtro en Tareas. 8 pantallas/ajustes, 5 ViewModels, 10 historias. Decisiones D-M4b-1..9 a validar. Nuevo PAT-032.
- 2026-09-15: Diseño de M5 Workspace por cliente de cartera, **aprobado sin gate por autorización de Joaquín 2026-09-14**: card en la ficha del cliente, pantalla de documentos con subida en cola (un archivo por envío), estado de lectura en palabras, ver por partes, renombrar y baja AJAX, espacio para el Director, adjuntos en Ejecutar y en ajustes con modal compartido, vista previa de documentos, chips en la conversación, Ver pasos llano para herramientas de documentos, vistas de staff solo metadatos. 8 pantallas/ajustes, 12 ViewModels, 10 historias, D-M5-1..14. Reuso: criterio de PAT-002 (vinosefue, sin su almacenamiento público), uploader y descarga protegida de ganaderia, M2/M3/M3b/M4. Nuevo PAT-033; PAT-002 verificado y corregido.
