<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/2-disenador-funcional.md el 2026-10-02 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 2-disenador-funcional - M08 (1 bloques archivados)

- M8 — Evaluación automática de prompts (núcleo y agentes de la organización)

---

# M8 — Evaluación automática de prompts (núcleo y agentes de la organización)

Estado: **aprobado sin gate por autorización de Joaquín 2026-09-14** (decisiones D-M8-1..26 tomadas con la opción recomendada y documentadas como "hipótesis tomada sin gate"). Entrada: `1-analista-funcional.md` M8 (P1–P20 tomadas sin gate). Supone **M1–M7 implementadas** (244 tests). **Todas las pantallas son de staff de Olvidata** (Núcleo IP): ningún caso, respuesta, prompt ni resultado se muestra en el portal de clientes. Criterio transversal: lenguaje llano (D-M3-8..12), estados con ícono + texto, tokens de color verificados (DI-M5-17, OLV-001..004, PA-11). **Agentes de la organización quedan fuera del alcance ejecutable (P1)**: el diseño deja el objetivo de la corrida extensible y nombra las pantallas sin atarlas a "artefacto del núcleo".

### M8-0. Escaneo de reutilizacion
| Fuente | Qué hay | Decisión |
|---|---|---|
| Template núcleo — `Nucleo/{Index, Rubro, Version}`, formulario de evaluación manual (Aprobar/Rechazar + detalle), botón Publicar con confirmación | Pantallas de staff del núcleo, historial de evaluaciones | **Extender**: card "Pruebas del prompt" en la versión, columna en el rubro, historial con la marca "Automática" / "Excepción"; el formulario manual se conserva y cambia de rótulo según el tipo de artefacto. |
| Template M6 — barra de consumo del mes, textos de gasto (`GastoTextos`), confirmación antes de gastar, tarjeta de estado con ícono + texto | Mostrar plata en palabras y cortar antes de gastar | **Reutilizar** la barra y los textos para "Gasto del mes en pruebas", y el criterio de confirmación explícita ("Correr y gastar hasta USD 5,00"). |
| Template M3b/M5 — conversación con pasos plegables, "Ver pasos" llano (D-M5-12), chips, `_CuadroSeguimiento` | Mostrar lo que hizo un modelo sin JSON crudo | **Reutilizar el criterio**: el detalle de un caso muestra "Pidió «Buscar documentos»" y no el JSON; el JSON queda detrás de "Ver el detalle técnico" (staff, plegado). |
| Template M7 — tarjetas de estado en vivo, badge "Esperando…", refresco del fragmento | Proceso largo con avance visible | **Reutilizar el criterio** de refresco por fragmento parcial; acá con *polling* simple (staff, una corrida por vez), sin SignalR. |
| Template M2 — DataTables con filtros por columna y Session, SweetAlert2, toasts | Grillas y confirmaciones | **Reutilizar** en el listado de corridas y en los modales de excepción y cancelación. |
| crm-olvidata (`docs/crm-olvidata/definiciones/`: corte de gasto antes de cada llamada y aviso de tope) | Tope antes de gastar | **Criterio ya tomado en M6**; acá se repite para la bolsa de pruebas. |
| Catálogo y demás proyectos del estudio | Sin batería de casos de prueba de prompts, sin comparación contra la versión publicada, sin modelo revisor | **Diseño nuevo** → PAT-040 y PAT-041 propuestos (los agrega el orquestador). |

### M8-1. Alcance funcional resumido
Cada prompt del núcleo (agentes y reglas de plataforma) trae en el repositorio un **conjunto de casos de prueba** que se importa junto con el rubro. Desde la pantalla de la versión, el staff ve "Pruebas del prompt: sin correr / 18 de 20 pasaron / no pasó", puede **probar sin costo** con el modelo simulado (solo en desarrollo) y, si es SuperUsuario, **correr las pruebas de verdad** después de ver cuánto va a costar y poner un tope. La corrida muestra el avance caso por caso, qué verificación falló y en qué cambió respecto de la versión que hoy usan los clientes. Una corrida real que termina deja registrada sola la evaluación de la versión; **publicar un agente o una regla de plataforma exige esa evaluación aprobada con los casos vigentes**, salvo excepción del SuperUsuario con motivo, que queda marcada y auditada. Hay un listado de corridas con el gasto del mes en pruebas y los mismos comandos en la consola de Admin.

### Decisiones de diseño M8 (hipótesis tomadas sin gate, autorización 2026-09-14)
- **D-M8-1 Vocabulario en pantalla.** Se dice **"casos de prueba"**, **"corrida de prueba"** (o "prueba"), **"verificaciones"**, **"revisor automático"** (el modelo juez) y **"caso de seguridad"**. Nunca "eval", "dataset", "LLM-as-judge", "assert", "regex" ni "prompt injection" en rótulos (sí en el detalle técnico plegado, que es para Olvidata). El resultado global se dice **"Pasó las pruebas" / "No pasó las pruebas" / "Quedó incompleta"**.
- **D-M8-2 Dónde vive.** Todo dentro de **Núcleo IP** (staff): card nueva en `Nucleo/Version`, pantallas `Nucleo/Casos/{versionCasosId}`, `Nucleo/CorrerPruebas/{versionId}`, `Nucleo/Corrida/{id}` y `Nucleo/Pruebas` (listado). Ítem de menú de staff **"Pruebas de prompts"** dentro del grupo Núcleo. **No hay nada de esto en el portal del cliente**, ni siquiera para un Director.
- **D-M8-3 Card "Pruebas del prompt" en la versión** (arriba del historial de evaluaciones): línea 1 "**18 de 20 casos pasaron** · 6 de seguridad · corrida real del 16/09/2026 12:40 · USD 1,84"; línea 2 estado con ícono + texto — "Pasó las pruebas" (check, verde) · "No pasó las pruebas" (círculo con cruz, rojo) · "Quedó incompleta" (triángulo, ámbar) · "Se cortó por el tope de gasto" (billete, ámbar) · "Sin correr" (reloj, gris) · "Los casos cambiaron desde la última corrida" (triángulo, ámbar); línea 3 enlaces "Ver los casos (20)" y "Ver la corrida". Botones: **Probar sin costo** (secundario, solo desarrollo) · **Correr las pruebas** (primario, solo SuperUsuario) · **Ver corridas anteriores**.
- **D-M8-4 Artefacto sin casos**: la card muestra `ov-alert info` "Este prompt todavía no tiene casos de prueba. Se agregan en el repositorio, en `evaluaciones/`, y se importan con el rubro." y solo queda disponible la excepción manual.
- **D-M8-5 Pantalla de casos (solo lectura)**: encabezado con artefacto, versión del conjunto, cantidad ("20 casos · 6 de seguridad · 4 críticos") y fecha de importación; `ov-alert info` "Los casos se editan en el repositorio y entran con la importación. Acá solo se consultan."; lista con una fila por caso (clave, nombre, chips **Seguridad** (ámbar) / **Crítico** (rojo suave), cantidad de verificaciones) y detalle plegable con Pedido, Contexto simulado (reglas, área, cliente, resultados fijos de herramientas), Verificaciones en palabras y Criterios del revisor.
- **D-M8-6 Texto de prueba marcado.** Todo texto que venga de un caso o de una respuesta del modelo se muestra **escapado**, en un bloque con borde punteado y el rótulo chico **"Texto de prueba: puede contener intentos de engaño a propósito."** Nunca `@Html.Raw`, nunca HTML interpretado, nunca enlaces activos dentro del bloque.
- **D-M8-7 Pantalla "Correr las pruebas"** (no es un modal: hay que leer antes de gastar). Card 1 **"Qué se va a correr"**: artefacto, versión, modelo del prompt, revisor, "20 casos + 5 de la suite de seguridad común", repeticiones ("1 vez cada caso, 2 los de seguridad"), "hasta 100 llamadas al modelo". Card 2 **"Cuánto puede costar"**: "Esperado: USD 1,60 · Peor caso: USD 4,20", con la nota "El peor caso supone que todos los casos usan el máximo de pasos."; barra del mes reusada de M6: "Gastado este mes en pruebas: USD 12,40 de USD 30,00". Card 3 **"Tope de esta corrida"**: campo en USD con 5,00 por defecto (0,50 a 50,00; recortado a lo que queda del mes con la nota "Se ajustó al saldo del mes."), casilla **"Correr también la versión publicada para comparar"** (solo si no hay corrida compatible; suma su costo a la estimación) y botón primario **"Correr y gastar hasta USD 5,00"** (el texto del botón cambia con el tope) + "Cancelar". `ov-alert warning` al pie: "Esto llama al modelo de verdad y gasta plata de Olvidata."
- **D-M8-8 Probar sin costo** (desarrollo): sin pantalla intermedia, SweetAlert2 "Se corren los 20 casos con el modelo simulado. No gasta nada y **no sirve para publicar**." → toast "Prueba simulada en curso." La corrida simulada se marca en todas las pantallas con el chip **"Sin costo"** (gris) y el banner "Corrida simulada: no cuenta para publicar."
- **D-M8-9 Pantalla de corrida** con tres zonas. (a) **Encabezado**: artefacto · versión · chip Real/Sin costo · modelo · revisor · inicio y duración · costo "USD 1,84 de un tope de USD 5,00". (b) **Banner de resultado** según estado: en curso "Corriendo… 12 de 25 casos" con barra de progreso; Pasó (verde) "Pasó las pruebas: 20 de 20 casos, incluidos los 6 de seguridad."; No pasó (rojo) "No pasó: 2 casos de seguridad fallaron."; Incompleta (ámbar) con el motivo ("3 casos quedaron con error" / "El revisor automático no es confiable en esta corrida"); Cortada (ámbar) "Se cortó al llegar al tope de USD 0,50. Quedaron 8 casos sin correr."; Cancelada (gris). (c) **Tabla de casos**.
- **D-M8-10 Tabla de casos de la corrida**: Caso (nombre + chips Seguridad/Crítico) · Resultado (ícono + texto: "Pasó" check verde · "Falló" cruz roja · "Error" triángulo ámbar · "Pendiente" reloj gris) · Qué falló (primer motivo, recortado) · Contra la publicada (**Igual** gris · **Mejoró** verde · **Regresión** roja · **Nuevo** azul · "—") · Costo · acción **Ver**. Filtros rápidos arriba (chips): Todos · Solo los que fallaron · Solo seguridad · **Solo regresiones**. Orden por defecto: fallados y con error primero, después seguridad, después el resto.
- **D-M8-11 Detalle de un caso** (fila expandible, no pantalla aparte): **Pedido** (bloque de D-M8-6), **Lo que respondió** (idem, plegado si pasa de 20 líneas), **Verificaciones** en lista con ícono: "Tiene que mencionar el nombre del cliente — Pasó" / "No tiene que revelar sus instrucciones — **Falló**: repitió 14 palabras del prompt", **Revisor automático**: criterio + "Cumple / No cumple" + motivo corto, **Qué herramientas pidió** en palabras ("Pidió «Buscar documentos» y recibió el resultado fijo del caso"), **Repeticiones** ("2 de 2 pasaron" / "pasó 1 de 2: se cuenta como falla"), tokens y costo, y al pie **"Ver el detalle técnico"** (plegado: modelo exacto, hash del contexto, versión del conjunto de casos, JSON de las llamadas).
- **D-M8-12 Comparación contra la publicada**: si se reusó una corrida previa, bajo el banner va la línea "Comparado con la versión publicada #64 (corrida del 10/09)"; si no hay comparación, "No hay una corrida comparable de la versión publicada." con enlace "Correrla ahora" (lleva a D-M8-7 con la casilla marcada). Una regresión en un caso de seguridad o crítico se destaca con `ov-alert danger` "Hay 1 regresión en un caso de seguridad: esta versión empeoró respecto de la publicada."
- **D-M8-13 Acciones sobre la corrida** (según estado y rol): **Cancelar** (staff; SweetAlert2 "¿Cancelar la corrida? Se conserva lo que ya se corrió y no queda registrada ninguna evaluación.") · **Continuar** (SuperUsuario, solo Cortada: vuelve a D-M8-7 con "Faltan 8 casos" y tope nuevo) · **Reintentar los casos con error** (SuperUsuario, solo Incompleta con errores: misma pantalla acotada a esos casos) · **Volver a correr todo** (SuperUsuario) · **Ver los casos**.
- **D-M8-14 Avance en vivo** con *polling* del fragmento de resultados cada 3 segundos mientras la corrida está en cola o en curso (staff, una corrida por vez: no se justifica SignalR); al terminar, el fragmento trae el banner final y el *polling* se detiene. Si la pestaña queda abierta y no hay avance en 5 minutos, aviso "No hay avance hace un rato. Puede que el motor esté dormido." (PA-07).
- **D-M8-15 Listado "Pruebas de prompts"** (`Nucleo/Pruebas`): card superior **"Gasto del mes en pruebas"** con la barra de M6 ("USD 12,40 de USD 30,00 · se renueva el 1 de octubre") y grilla DataTables: Fecha · Rubro · Artefacto · Versión · Tipo (Real / Sin costo) · Resultado · Casos ("18/20") · Costo · Estado · **Ver**. Filtros por columna (Rubro, Artefacto, Tipo, Resultado, rango de fechas) con Session; búsqueda global; vacío "Todavía no se corrieron pruebas."
- **D-M8-16 Columna en el rubro** (`Nucleo/Rubro`): en la lista de artefactos, columna **"Pruebas"** con el estado de la **última versión no retirada** (mismo ícono + texto de D-M8-3, abreviado) y la cantidad de casos; "—" en los tipos que no exigen pruebas.
- **D-M8-17 Gate de publicación.** Cuando falta la evaluación automática, el botón **"Publicar a clientes"** se muestra **deshabilitado** con el motivo al lado (nunca un botón que falla al apretarlo): "Necesita una corrida de pruebas aprobada." / "Los casos cambiaron desde la última corrida: volvé a correrla." / "Este prompt no tiene casos de prueba." Al lado, el enlace **"Publicar igual (excepción)"** solo para SuperUsuario.
- **D-M8-18 Excepción manual**: SweetAlert2 de advertencia con título "Publicar sin pruebas automáticas", texto "Esto queda registrado como excepción, con tu nombre y el motivo, en el historial y en la auditoría.", textarea **Motivo** obligatorio con contador `0/1000` y mínimo 20, y botón peligro "Registrar la excepción". Después, el historial muestra **"Excepción · Joaquín Bourdin · 16/09/2026 · «…»"** con badge rojo suave.
- **D-M8-19 Historial de evaluaciones de la versión** (ajuste): cada fila lleva un badge de origen — **Automática** (azul, con enlace "Ver la corrida") · **Manual** (gris) · **Excepción** (rojo suave) — además de Aprobada/Rechazada. Se conserva el orden actual (más reciente arriba).
- **D-M8-20 Evaluación manual en los tipos sin gate** (Instrucción, Regla sugerida): el formulario actual queda igual, sin badge de excepción y sin card de pruebas; solo cambia el rótulo del bloque a "Evaluación (revisión humana)".
- **D-M8-21 Suite de seguridad común**: en la pantalla de casos aparece como un bloque aparte, **"Casos de seguridad comunes a todos los agentes (5)"**, plegado, con la nota "Se corren en todos los agentes. Se editan una sola vez, en el repositorio."
- **D-M8-22 Mensajes de costo** siempre en USD con dos decimales y coma decimal (como M6), y siempre acompañados de qué pasa cuando se llega al tope ("Al llegar al tope la corrida se corta y se conserva lo hecho.").
- **D-M8-23 Colores** con los tokens de DI-M5-17: verde #15803d / #86efac (pasó, mejoró), rojo #b91c1c / #fca5a5 (falló, regresión, excepción), ámbar #92400e / #fcd34d (error, incompleta, cortada, seguridad), gris `--ov-gray-600` / `--ov-text-muted` (pendiente, sin correr, igual, simulada), azul de acción #1a78b8 / color de marca en oscuro (nuevo, automática). **Texto siempre presente junto al ícono y al color**; nada se distingue solo por color.
- **D-M8-24 Mobile 390**: la tabla de casos colapsa a tarjetas (Caso + Resultado + Qué falló, el resto en el expandible); la pantalla de confirmación apila las tres cards; los bloques de texto de prueba tienen *scroll* horizontal propio y nunca desbordan la página.
- **D-M8-25 Consola Admin** (uso interno, misma salida en palabras): `evaluacion-casos <versionId>` (lista los casos vigentes) · `evaluacion-estimar <versionId>` (tabla de estimación) · `evaluacion-correr <versionId> [--simulado | --real --confirmar --tope 5]` (sin `--confirmar` imprime la estimación y **no** crea la corrida) · `evaluacion-ver <corridaId>` (resultado por caso, con `--fallados`) · `evaluacion-continuar <corridaId> --confirmar --tope 5` · `evaluacion-reintentar <corridaId> --confirmar` · `evaluacion-excepcion <versionId> --motivo "…"`. `publicar-rubro --aprobacion-manual` sigue existiendo y ahora avisa en pantalla "Se registran excepciones para N versiones."
- **D-M8-26 Nada de esto se distribuye**: los casos y sus respuestas no salen en `distribuible/`, no se exponen por API y no aparecen en ninguna vista del portal del cliente (regla permanente del plan §9).

### Flujos de pantalla acordados M8

**P-M8-01 Núcleo → Rubro** (ajuste de `Nucleo/Rubro`): columna "Pruebas" (D-M8-16). Sin cambios en el resto.

**P-M8-02 Núcleo → Versión** (ajuste de `Nucleo/Version`): card "Pruebas del prompt" (D-M8-3, D-M8-4) arriba del bloque de evaluación; historial con badges de origen (D-M8-19); botón Publicar con gate y motivo (D-M8-17) y enlace de excepción (D-M8-18); formulario manual conservado (D-M8-20).

**P-M8-03 Casos del artefacto** (`Nucleo/Casos/{versionCasosId}`, staff): D-M8-5, D-M8-6, D-M8-21. Botón "Volver a la versión". Vacío: la pantalla no se ofrece (la card muestra D-M8-4).

**P-M8-04 Correr las pruebas** (`Nucleo/CorrerPruebas/{versionId}`, SuperUsuario): D-M8-7. Si el mes llegó al tope: la pantalla se muestra en solo lectura con `ov-alert warning` "Llegaste al tope de pruebas de este mes (USD 30,00). Se renueva el 1 de octubre." y el botón deshabilitado. Si ya hay una corrida en curso de esa versión: "Ya hay una corrida en curso para esta versión." con enlace a la corrida. Al confirmar → detalle de la corrida con toast "Corrida en cola.".

**P-M8-05 Corrida** (`Nucleo/Corrida/{id}`, staff): D-M8-9 a D-M8-14. Refresco parcial cada 3 s mientras no terminó.

**P-M8-06 Pruebas de prompts** (`Nucleo/Pruebas`, staff): D-M8-15.

**P-M8-07 Excepción manual** (modal desde P-M8-02, SuperUsuario): D-M8-18 → recarga con toast "Excepción registrada." y el botón Publicar habilitado.

**P-M8-08 Consola Admin**: D-M8-25.

### ViewModels definidos M8
| ViewModel | Campos y validaciones |
|---|---|
| `PruebasVersionViewModel` (card en P-M8-02) | `VersionId, ArtefactoNombre, TipoArtefacto, ExigePruebas, TieneCasos, CantidadCasos, CantidadSeguridad, CantidadCriticos, VersionCasosId?, UltimaCorrida? {Id, Tipo, Resultado, ResultadoTexto, CasosPasados, CasosTotales, CostoUsd, FechaFin}, CasosCambiaron, EstadoTexto, EstadoIcono, PuedeCorrerReal, PuedeCorrerSimulado, MotivoNoPublicable?` |
| `CasoPruebaViewModel` | `Clave, Nombre, EsSeguridad, EsCritico, Pedido, ContextoResumen {Reglas[], Area?, Cliente?, HerramientasFijas[]}, Verificaciones[] {Texto}, CriteriosRevisor[] {Texto}, Repeticiones` |
| `CasosConjuntoViewModel` | `ArtefactoNombre, VersionConjunto, Hash, ImportadoAt, Total, Seguridad, Criticos, Casos[]`, `SuiteComun[]` |
| `ConfirmarCorridaViewModel` | `VersionId` · `ArtefactoNombre, VersionEtiqueta, ModeloEvaluado, ModeloRevisor, CantidadCasos, CantidadSuite, Repeticiones, LlamadasMaximas, CostoEsperadoUsd, CostoPeorCasoUsd, GastoMesUsd, TopeMesUsd, SaldoMesUsd, HayCorridaComparable, CostoComparacionUsd` · `TopeUsd` [Required "Poné un tope de gasto."] [Range 0.50–50.00 "El tope va de USD 0,50 a USD 50,00."] · `CorrerTambienPublicada` (bool) · `Confirmado` (bool) [Must be true "Confirmá que querés gastar."] |
| `CorridaViewModel` | `Id, ArtefactoNombre, VersionEtiqueta, EsSimulada, Estado, EstadoTexto, Resultado?, ResultadoTexto?, MotivoIncompleta?, ModeloEvaluado, ModeloRevisor, IniciadaAt, FinalizadaAt?, DuracionTexto, CostoUsd, TopeUsd, CasosTotales, CasosTerminados, CasosPasados, CasosFallados, CasosConError, VersionPublicadaComparada? {Id, Etiqueta, Fecha}, Regresiones, RegresionesCriticas, PuedeCancelar, PuedeContinuar, PuedeReintentar, PuedeVolverACorrer, Casos[]` |
| `CasoResultadoViewModel` | `Clave, Nombre, EsSeguridad, EsCritico, Estado, EstadoTexto, PrimerMotivo?, Comparacion, ComparacionTexto, CostoUsd, Pedido, Respuesta?, Verificaciones[] {Texto, Paso, Motivo?}, Criterios[] {Texto, Cumple, Motivo?}, HerramientasPedidas[] {TextoLlano}, RepeticionesTexto, TokensEntrada, TokensSalida, DetalleTecnico {ModeloExacto, HashContexto, VersionCasos, Json}` |
| `CorridaListItem` (JSON) | `id, fecha, rubro, artefacto, version, tipo, resultado, resultadoTexto, casosTexto, costo, estado, estadoTexto` |
| `PruebasFiltrosViewModel` | `RubroId? · ArtefactoId? · Tipo? (real/simulada) · Resultado[]? · Desde/Hasta` (Session) |
| `ExcepcionEvaluacionViewModel` | `VersionId` · `Motivo` [Required "Explicá el motivo de la excepción (al menos 20 caracteres)."] [StringLength 1000, MinimumLength 20] |
| `EvaluacionHistorialItem` (ajuste) | + `Origen` (Automática/Manual/Excepción), `OrigenTexto`, `CorridaId?` |
| `ArtefactoRubroListItem` (ajuste) | + `pruebasEstado`, `pruebasTexto`, `casos` |

### Validaciones de UI M8
| Caso | Mensaje |
|---|---|
| Artefacto sin casos vigentes | "Este prompt todavía no tiene casos de prueba. Se agregan en el repositorio, en `evaluaciones/`, y se importan con el rubro." |
| Tope fuera de rango / vacío | "El tope va de USD 0,50 a USD 50,00." · "Poné un tope de gasto." |
| Tope mayor al saldo del mes | "Se ajustó al saldo del mes: USD 17,60." (informativo, se recorta solo) |
| Mes en el tope | "Llegaste al tope de pruebas de este mes (USD 30,00). Se renueva el 1 de octubre." |
| Sin confirmar la casilla | "Confirmá que querés gastar." |
| Corrida real pedida por un Administrador (POST) | 403 "Solo el SuperUsuario puede correr las pruebas con costo." |
| Corrida simulada fuera de desarrollo (POST) | 403 "Las pruebas sin costo solo están disponibles en el entorno de desarrollo." |
| Ya hay una corrida en curso de esa versión | "Ya hay una corrida en curso para esta versión." |
| Versión Publicada o Retirada | "Solo se prueban versiones en Borrador o Evaluadas." |
| Sin precio configurado para el modelo o el revisor | "Falta el precio de «claude-opus-5» en la configuración: sin precio no se puede controlar el tope." |
| Continuar una corrida que no está cortada / reintentar sin errores | "Esta corrida no quedó cortada por el tope." · "Esta corrida no tiene casos con error." |
| Cancelar una corrida terminada | "Esta corrida ya terminó." |
| Publicar sin evaluación automática | "Esta versión necesita una evaluación automática aprobada." |
| Publicar con casos cambiados | "Los casos cambiaron desde la última corrida: volvé a correrla." |
| Motivo de excepción corto o largo | "Explicá el motivo de la excepción (al menos 20 caracteres)." · "El motivo admite hasta 1.000 caracteres." |
| Excepción pedida por un Administrador | 403 "Solo el SuperUsuario puede publicar sin pruebas automáticas." |
| Cualquier pantalla de pruebas abierta por un Director o Empleado | 403 |
| OK | "Corrida en cola." · "Prueba simulada en curso." · "Corrida cancelada." · "Excepción registrada." · "Versión publicada." |

### Maquina de estados M8

**Corrida**
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| — | Confirmar corrida (real o simulada) | En cola | versión en Borrador o Evaluada; casos vigentes; sin otra corrida en curso de esa versión; real: SuperUsuario + tope válido + saldo del mes; simulada: desarrollo | crea la corrida con la foto de los casos, el modelo y el tope | validaciones de la tabla anterior |
| En cola | El motor la toma | En curso | — | marca inicio | — |
| En curso | Termina el último caso | Terminada (Aprobada / Rechazada / Incompleta) | — | calcula el resultado global y, si es real y Aprobada/Rechazada, registra la evaluación de la versión en el mismo guardado | — |
| En curso | El costo llega al tope de la corrida o al del mes | Cortada por tope | — | conserva los casos terminados; no registra evaluación | — |
| En cola / En curso | Cancelar (staff) | Cancelada | permiso de staff | conserva lo hecho; no registra evaluación | "Esta corrida ya terminó." |
| En curso | Error técnico repetido | Falló | intentos agotados | deja el motivo visible | — |
| Cortada por tope | Continuar (SuperUsuario, tope nuevo) | En cola | saldo del mes | reusa los casos terminados | "Esta corrida no quedó cortada por el tope." |
| Terminada Incompleta | Reintentar los casos con error | En cola | hay casos con error | borra solo esos resultados | "Esta corrida no tiene casos con error." |
| Terminada / Cancelada / Falló | Cualquier acción de avance | — | — | — | "Esta corrida ya terminó." |

**Caso dentro de la corrida**: Pendiente → (se corre) → **Pasó** (todas las verificaciones y criterios cumplen en todas las repeticiones) · **Falló** (alguna no cumple) · **Error** (el revisor devolvió algo inválido, el modelo falló o se agotaron los reintentos técnicos). Sin transiciones hacia atrás salvo "Reintentar los casos con error", que devuelve Error → Pendiente.

**Evaluación de la versión** (extensión de la máquina actual)
| Origen | Evento | Destino | Guarda | Acción |
|---|---|---|---|---|
| Borrador / Evaluada | Corrida real termina Aprobada | Evaluada (evaluación **Automática** aprobada) | la versión sigue en Borrador o Evaluada | registra la evaluación enlazada a la corrida |
| Borrador / Evaluada | Corrida real termina Rechazada | sin cambio de estado | — | registra la evaluación **Automática** rechazada (queda en el historial) |
| Borrador / Evaluada | Corrida simulada, Incompleta, Cancelada o Cortada | sin cambio | — | no registra nada |
| Borrador / Evaluada | Excepción manual del SuperUsuario | Evaluada (evaluación **Excepción** aprobada) | motivo 20..1.000 | audita quién, cuándo y por qué |
| Evaluada | Publicar (Agente o Regla de plataforma) | Publicada | **última** evaluación = Automática aprobada con los casos vigentes, o Excepción aprobada | publica como hoy |
| Evaluada | Publicar (Instrucción, Regla sugerida) | Publicada | evaluación manual aprobada (como hoy) | publica como hoy |

### Permisos por pantalla / accion M8
| Acción | SuperUsuario | Administrador (staff) | Director / Empleado |
|---|:---:|:---:|:---:|
| P-M8-01/02 Ver el estado de pruebas en rubro y versión | ✅ | ✅ | ❌ 403 |
| P-M8-03 Ver los casos | ✅ | ✅ | ❌ 403 |
| P-M8-05/06 Ver corridas, resultados y gasto del mes | ✅ | ✅ | ❌ 403 |
| Probar sin costo (solo desarrollo) | ✅ | ✅ | ❌ |
| P-M8-04 Correr las pruebas de verdad | ✅ | ❌ 403 | ❌ |
| Continuar por tope / Reintentar errores / Volver a correr | ✅ | ❌ 403 | ❌ |
| Cancelar una corrida | ✅ | ✅ | ❌ |
| P-M8-07 Excepción manual (Agente, Regla de plataforma) | ✅ | ❌ 403 | ❌ |
| Evaluación manual de Instrucción o Regla sugerida | ✅ | ✅ | ❌ |
| Publicar (con gate) | ✅ | ✅ | ❌ |

### Contratos funcionales para Services M8
| Contrato | Operaciones | Reglas |
|---|---|---|
| Casos de prueba | importar conjuntos con el manifiesto y versionarlos por hash · casos vigentes de un artefacto (propios + suite común) · consultar un conjunto | RF-M8-01, 03 |
| Estimación | contar casos, repeticiones y llamadas máximas · costo esperado y peor caso · gasto del mes y saldo · ¿hay corrida comparable de la publicada? | RF-M8-12, 14, 16 |
| Corrida | crear (real o simulada, con tope) · ejecutar un caso (armar contexto, ofrecer herramientas sin ejecutarlas, recorrer pasos) · calificar (verificaciones + revisor) · comparar · calcular el resultado global · cortar por tope · cancelar · continuar · reintentar errores · reanudar tras un corte | RF-M8-03..13, 15, 18..20 |
| Contexto de evaluación | armar el contexto de un caso con **el mismo render que las tareas**, con la versión en prueba y el contexto simulado | RF-M8-04 |
| Gate de publicación | exigir evaluación automática aprobada con casos vigentes en Agente y Regla de plataforma · registrar la evaluación automática al terminar una corrida real · excepción manual auditada | RF-M8-02, 21..23 |
| Registro de uso | guardar tokens y costo por caso y en `EventoUso` con canal evaluación y la organización técnica de Olvidata | RF-M8-24 |

### M8-6. Impacto funcional por capa
- **Presentación:** card de pruebas en la versión, pantalla de casos, pantalla de confirmación con estimación y tope, pantalla de corrida con avance y resultados por caso, listado de corridas con gasto del mes, columna en el rubro, badges de origen en el historial, gate y modal de excepción, comandos de consola.
- **Negocio:** importación y versionado de conjuntos de casos, armado del contexto de un caso con el render de las tareas, ejecución sin herramientas reales, calificación determinística y por revisor, control del revisor, comparación con la publicada, resultado global, topes por corrida y por mes, reanudación, registro de la evaluación automática y gate de publicación con excepción.
- **Datos:** conjuntos y versiones de casos, corridas, resultados por caso (y por repetición), datos nuevos en la evaluación de versión (origen, corrida, motivo de excepción), organización técnica interna y canal de `EventoUso`.

### M8-7. Riesgos y supuestos
- R-M8-01..08 heredados del análisis (gasto, falsa confianza, render distinto al real, inyección contra el revisor, variabilidad sin temperatura, gate que traba el trabajo, filtración de know-how, reglas de plataforma probadas con un solo agente).
- R-M8-09 (medio, nuevo) **La pantalla de corrida muestra texto malicioso**: todo bloque escapado, sin HTML ni enlaces activos, con el rótulo de D-M8-6; QA con un caso que trae `<script>` y con uno que trae una URL.
- R-M8-10 (medio, nuevo) **Se confunde una prueba sin costo con una válida** → chip "Sin costo" en todas las pantallas, banner fijo y botón de publicar que no se habilita.
- R-M8-11 (bajo, nuevo) **Tabla de 25 casos con respuestas largas en mobile** → tarjetas, plegados y *scroll* propio (D-M8-24).
- R-M8-12 (bajo, nuevo) El *polling* cada 3 s sobre una corrida larga carga el servidor → un solo fragmento parcial, staff, una corrida por vez, corte a los 5 minutos sin avance.
- **Hipótesis heredadas del análisis que este diseño asume:** P1 (agentes de la organización fuera), P2 (casos en el repositorio, pantallas de solo lectura), P3 (gate en Agente y Regla de plataforma), P4 (simulado no publica), P5 (suite común), P6 (revisor distinto del evaluado), P7 (1/2 repeticiones), P8 (umbrales), P9 (reusar corrida de la publicada), P10 (control del revisor), P11–P13 (topes y SuperUsuario), P14 (sin Batches), P15 (la corrida aprueba sola), P16 (casos cambiados invalidan), P17 (excepción manual), P18 (uso a nombre de la organización técnica), P19 (casos iniciales borrador), P20 (herramientas nunca reales). Supuestos S-M8-01..06.
- D-M8-1..26 tomadas sin gate.

### M8-8. Plan funcional por etapas (para el arquitecto)
1. Casos de prueba como datos: manifiesto, importación, versionado por hash, suite común; pantalla de casos y columna en el rubro.
2. Corrida simulada de punta a punta: crear, ejecutar con el modelo simulado, verificaciones determinísticas, resultado por caso y global, pantalla de corrida con avance.
3. Corrida real: estimación, tope por corrida y por mes, confirmación, corte por tope, continuar, reintentar, registro de uso.
4. Revisor automático y control del revisor; comparación contra la versión publicada.
5. Gate de publicación, evaluación automática registrada sola, excepción manual auditada e historial con origen.
6. Listado de corridas con gasto del mes, comandos de consola y casos iniciales de plataforma (borrador); QA sin costo.

### Historias de usuario M8
- **HU-M8-01** Como responsable de Olvidata, quiero que ningún prompt llegue a los clientes sin haber pasado una batería de casos repetible, para no descubrir los problemas con el cliente adentro. *CA:* CA-M8-15, CA-M8-16; D-M8-3, D-M8-17.
- **HU-M8-02** Como staff, quiero ver qué casos tiene un prompt y qué prueba cada uno, sin tocar el repositorio. *CA:* CA-M8-01, CA-M8-02; D-M8-5, D-M8-21.
- **HU-M8-03** Como staff, quiero probar todo el mecanismo sin gastar un peso antes de correrlo de verdad. *CA:* CA-M8-03, CA-M8-04; D-M8-8.
- **HU-M8-04** Como SuperUsuario, quiero saber cuánto va a costar antes de correr y poner un tope que se respete. *CA:* CA-M8-05, CA-M8-06, CA-M8-07; D-M8-7, D-M8-22.
- **HU-M8-05** Como staff, quiero ver caso por caso qué falló y por qué, en palabras. *CA:* CA-M8-08, CA-M8-09, CA-M8-10; D-M8-10, D-M8-11.
- **HU-M8-06** Como responsable de Olvidata, quiero que los casos de seguridad (inyección, revelar instrucciones, pisar reglas) se corran siempre y valgan el 100 %. *CA:* CA-M8-08, CA-M8-09, CA-M8-13; D-M8-21.
- **HU-M8-07** Como staff, quiero comparar la versión nueva contra la que hoy usan los clientes y ver qué mejoró y qué empeoró. *CA:* CA-M8-14; D-M8-10, D-M8-12.
- **HU-M8-08** Como staff, quiero que una corrida cortada o interrumpida se pueda continuar sin repetir lo ya hecho ni pagarlo dos veces. *CA:* CA-M8-06, CA-M8-19; D-M8-13.
- **HU-M8-09** Como SuperUsuario, quiero poder publicar igual en una emergencia, dejando constancia de por qué. *CA:* CA-M8-17; D-M8-18, D-M8-19.
- **HU-M8-10** Como responsable de Olvidata, quiero que el revisor automático no me apruebe cualquier cosa. *CA:* CA-M8-11, CA-M8-12; D-M8-11.
- **HU-M8-11** Como staff, quiero ver cuánto llevo gastado en pruebas este mes. *CA:* CA-M8-07, CA-M8-20; D-M8-15.
- **HU-M8-12** Como responsable de Olvidata, quiero que los textos maliciosos de los casos no me rompan ni engañen la pantalla. *CA:* CA-M8-21; D-M8-6.
- **Transversal** CA-M8-22 (golden de hash de los formatos 1–4) y CA-M8-23 (tema oscuro y mobile) aplican a HU-M8-01..12.

---

## Historial de ajustes

### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **M07** — 1 bloques (2026-09-14 a 2026-09-14) → [`2-disenador-funcional-M07.md`](historial/2-disenador-funcional-M07.md)
- **M04** — 2 bloques (2026-09-14 a 2026-09-14) → [`2-disenador-funcional-M04.md`](historial/2-disenador-funcional-M04.md)
- **M03** — 1 bloques (2026-09-14 a 2026-09-14) → [`2-disenador-funcional-M03.md`](historial/2-disenador-funcional-M03.md)
