# Memoria - Arquitecto MVC

## Proyecto: olvidata-agentes-multirubro
## Ultima actualizacion: 2026-09-24

## Definiciones vigentes

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
