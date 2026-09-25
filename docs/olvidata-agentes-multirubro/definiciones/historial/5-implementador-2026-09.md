<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/5-implementador.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - 2026-09 (15 bloques archivados)

- M20 — Coprocesador aritmético (la calculadora del agente)
- M18 — Portal del cliente del estudio (rol Cliente)
- M16 — Tablero de actividad al iniciar sesión
- M15 — Ficha de rubro para el staff (Nucleo/Rubro enriquecida)
- M14 — Instructivos, búsqueda web, espacio del cliente y control de gasto
- M12 — Tareas programadas y autonomía gradual por rol
- M11 — Conectores con credenciales por organización
- M10 — Base de conocimiento por rubro
- M9 — Preparación de despliegue (local: preparar, no desplegar)
- M8 — Evaluación automática de prompts (núcleo)
- M6 — Aprobaciones de acciones por rol y límites de gasto
- M5 — Workspace por cliente de cartera
- M4 — Agentes de la organización
- M3 — Reglas por alcance
- M2 — Organización del portal

---

# M20 — Coprocesador aritmético (la calculadora del agente)

Estado: **implementado 2026-09-25; pendiente de QA; 1 commit local `b551010`, sin push y sin deploy (los hace el
orquestador)**. Repo `C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `5e69afe`. Entrada: análisis M20
(CU-M20-01..06, RF-M20-01..09, D-M20-a..e, CA-M20-01..06), el bloque M20 de `2-disenador-funcional.md` (dónde se ve,
regla de redacción del paso) y el de `3-arquitecto-mvc.md` (mapa de componentes, contrato del evaluador, R-T-01..03 y
R-T-06). Gate: definiciones 2, 3 y 4 aprobadas; presupuesto omitido (proyecto personal).

### Escaneo de reutilización
- **Otros proyectos: nada.** Se confirmó lo que ya había relevado el diseñador: ningún proyecto del historial tiene un
  evaluador de expresiones (los hits de «calculadora» en `marihogar` son casos de prueba manuales). No hay código para
  traer.
- **Del propio repo:** la heurística de «número escrito por una persona» de M19 (`GeneradorEntregables.TryNumero` +
  `EsSeparadorDeMiles`), que **se mudó a `Application/Helpers/NumeroEscrito.cs` y quedó compartida**, no duplicada. El
  generador de M19 ahora la llama y borró su copia. Patrón de la herramienta y del resumidor de pasos: M17 (memoria) para
  la condición y M19 (impresora) para armar el paso desde la entrada.

### Qué se construyó
- **Application (nuevo):** `Helpers/NumeroEscrito.cs` (mudanza), `Helpers/EvaluadorExpresiones.cs`,
  `Settings/CalculoOptions.cs`, `DTOs/CalculoDtos.cs` (`CuentaCalculada` + `MensajesCalculo`),
  `Motor/NombresHerramientasCalculo.cs`. **Modificados:** `Motor/DescripcionesHerramientas.cs` (rótulo llano «Hacer una
  cuenta»), `Motor/IResolvedorHerramientas.cs` (`FamiliaHerramienta.Calculo = 12`).
- **Infrastructure (nuevo):** `Services/Calculo/HerramientaCalcular.cs` (la herramienta + `HerramientasCalculo`, que
  resuelve la entrada del modelo) y `Services/Calculo/ResumenHerramientasCalculo.cs` (el paso en palabras).
  **Modificados:** `Services/Motor/ResolvedorHerramientas.cs`, `Services/Motor/ResumenPasos.cs`,
  `Services/Motor/ServicioTareas.cs`, `Services/Entregables/GeneradorEntregables.cs`, `DependencyInjection.cs`.
- **Web:** `Helpers/AgentesTextos.cs` (una condición que la ficha venía mostrando mal; ver DI-M20-G) y la sección
  `Calculo` de `appsettings.json`.
- **Tests:** `tests/OlvidataAgentes.Tests/CalculoTests.cs` (nuevo, 78 casos) y dos filtros de tests existentes.
- **Documentación del repo:** `docs/manual-de-uso.md` (sección «Cuentas», el «Qué no hace» reescrito y una fila de
  límites) y `docs/diseno-entregables.md` (dónde vive ahora la heurística de número).
- **Datos: ninguno. Sin entidades y sin migración**, como pedía la arquitectura. `Mcp` y `Cli` sin tocar;
  `distribuible/` sin tocar.

### Decisiones de implementación
- **DI-M20-A — El nombre de una cuenta vale el resultado REDONDEADO, no el exacto.** CA-M20-03 pide que encadenar por
  nombre dé lo mismo que pasar el número a mano, y una persona pasa a mano el número que ve. Encadenar el exacto haría
  que los números del paso no cerraran entre ellos (`neto + iva` distinto del `total` mostrado), que es justo el problema
  de confianza que el módulo viene a resolver. Está escrito en la descripción que lee el modelo: si necesita más
  precisión, pide más decimales.
- **DI-M20-B — El paso se arma resolviendo otra vez la entrada, con el mismo código.** El diseño pide armarlo desde la
  entrada del modelo y no del texto de la herramienta, pero la entrada **no trae los resultados**. Se resuelve otra vez
  con `HerramientasCalculo.Resolver`, que es el mismo método que corrió en la tarea: el evaluador es puro y
  determinístico, así que dos corridas de la misma entrada dan lo mismo. Para que «el mismo código» sea cierto también en
  los topes, `CalculoOptions` viaja hasta `ResumenPasos.Resultado` (parámetro opcional) y `ServicioTareas` lo inyecta: si
  se resolviera con los valores por defecto, una organización con topes distintos vería un paso que no es el que corrió.
- **DI-M20-C — Una sola red de seguridad, y está donde importa.** El evaluador no lanza por la entrada (captura
  `DivideByZeroException` y `OverflowException`, y corta la profundidad con guarda propia porque un
  `StackOverflowException` no se captura y tiraría el worker). Además cada cuenta se resuelve adentro de un `try` en
  `HerramientasCalculo.Una`: eso **no** es para la tarea —el motor ya tiene su red— sino para la **pantalla**, porque el
  detalle de una tarea vuelve a resolver la cuenta y una excepción ahí sería un error 500 en una tarea que terminó bien.
- **DI-M20-D — La herramienta no toca la base.** No recibe `AppDbContext`: recibe los topes y nada más. Es la primera
  herramienta del sistema que se registra sin service ni repositorio. Un test lo fija (`Recuerdos`, `DocumentosCartera` y
  `AprobacionesAccion` vacíos después de una tarea que calculó).
- **DI-M20-E — Se valida el nombre en vez de ignorarlo.** Un nombre que el evaluador no podría leer (con espacios), uno
  repetido o uno que choca con una función devuelve el motivo para esa cuenta. Si se ignorara en silencio, la cuenta
  siguiente fallaría con «no sé qué es neto» y nadie entendería por qué.
- **DI-M20-F — Solo en tareas de trabajo, chequeado también adentro de la herramienta.** El resolvedor no la ofrece en
  una `ConsultaCliente` (la lista blanca de M18 es por inclusión), y si el modelo la pidiera igual, `EjecutarAsync`
  contesta «no disponible». Dos cierres, como el resto de M18.
- **DI-M20-G — Un arreglo chico fuera del alcance, a propósito.** `AgentesTextos.Condicion` no tenía brazo para
  `CondicionHerramienta.TodaTareaDeTrabajo` y caía al texto de `TareaPrincipal`: la ficha del agente decía «en tareas
  principales» de algo que se ofrece en toda tarea de trabajo. Venía de M17 (memoria) y la calculadora lo heredaba, así
  que se agregó el brazo. **Queda igual `PortalDeClientesEncendido` (M18)**, que cae al mismo texto por defecto: no es de
  este módulo y se deja anotado para quien lo tome.

### Lo que el criterio decía mal (corregido en la documentación, no en silencio)
- **CA-M20-01 es correcto en lo que importa y falso en el paréntesis.** `1234,50 * 21%` da exactamente `259,245` y
  redondeado `259,25`: eso se cumple y está fijado. Pero «la misma cuenta en `double` daría 259,24499999999997» **no es
  cierto**: en `double` ese producto vale 259,2450000000000045 y redondea igual. El caso que sí rompe —y que justifica de
  verdad que todo sea `decimal`— es **acumular**: sumar diez veces 0,10 en `double` da 0,9999999999999999, y un número
  que ya viene mal sumado no hay redondeo que lo arregle. El test dejó las dos cosas escritas.
- **RF-M20-07: el tope de «1.000 números por función» es inalcanzable.** Con 500 caracteres por expresión no entran mil
  números (entran unos 250 como mucho): el que corta primero es siempre el largo. Se implementó igual como techo
  explícito y quedó anotado en `appsettings.json` y en `CalculoOptions`.
- **RF-M20-03 tiene un borde que conviene conocer (R-M20-02, confirmado en la práctica).** Compartir la heurística de M19
  significa que un separador con **exactamente tres cifras atrás** se lee como de miles: `12,345` son doce mil, y
  `1234,567` es un millón doscientos treinta y cuatro mil quinientos sesenta y siete. No hay forma de escribir 1234,567
  con tres decimales salvo poniendo cuatro (`1234,5670`) o dividiendo. Para plata (dos decimales) y para alícuotas
  (`0,105`, que la heurística resuelve bien porque la parte entera es cero) no molesta. Se documentó en la descripción
  que lee el modelo y quedó fijado en la tabla de casos para que no cambie sin querer.

### Pruebas
- **Tabla de casos del evaluador (R-T-01):** 39 cuentas con su resultado (precedencia, asociatividad, unario, porcentaje,
  números escritos de las cinco formas, las siete funciones, anidado) y 23 cuentas que no se pueden hacer con su motivo
  exacto (división por cero, función inventada, función sin paréntesis, argumentos de más y de menos, decimales fuera de
  rango, paréntesis sin cerrar, sobra al final, vacía, nombre desconocido, número imposible y **desborde**, R-T-02).
- **De herramienta, con entorno:** encadenado por nombre = hacerlo a mano; una cuenta imposible y las demás resueltas con
  la tarea **Completada**; ninguna cuenta resuelta → el paso lo dice; tope de cuentas; la forma corta de 6 en adelante;
  el paso en palabras sin el nombre de la función ni JSON; se ofrece **sin** cliente; **no** se ofrece en
  `ConsultaCliente` ni funciona si la piden; y la calculadora no escribe nada en la base.
- **Cada test nuevo verificado en rojo** con tres tandas de mutaciones antes de darlo por bueno: (A) el `%` deja de
  dividir por cien, se rompe la precedencia, se aflojan las guardas de profundidad y de largo, y `SUMA` se come el último
  importe → 33 rojos; (B) se saca el tope de cuentas, se corta en la primera cuenta que falla, se dejan de validar los
  nombres, el redondeo pasa a `ToEven`, se encadena el exacto, se saca la guarda de tipo de tarea, se devuelve siempre
  `Ok` y la calculadora deja de ofrecerse → los 9 restantes; (C) control del test negativo apuntándolo a una tabla que sí
  tiene filas. Archivos restaurados desde copia antes de seguir.

### Evidencia
- `dotnet build OlvidataAgentes.slnx`: **0 Errores**, 2 advertencias (las dos preexistentes de xUnit en tests de M18).
- `dotnet test tests/OlvidataAgentes.Tests` **medido sin pipe** (`> archivo 2>&1`, leyendo el resumen impreso): línea
  base **Con error: 0, Superado: 907, Total: 907**; final **Con error: 0, Superado: 985, Omitido: 0, Total: 985** (+78).
  En el medio hubo una corrida con 1 rojo en
  `LectorDocumentosTests.Extraccion_que_supera_el_tiempo_queda_como_no_se_pudo_leer`, que es el flaky conocido bajo
  carga: pasó al correrlo solo y en la corrida final.
- **Los 5 goldens de contexto, sin un byte de cambio:** `git status` de `tests/OlvidataAgentes.Tests/Goldens/` vacío y
  ningún `.actual.txt` generado. Era lo esperado (R-T-06): las herramientas viajan en la lista de la solicitud, no en el
  prompt de sistema.
- **Los tests de M19 quedaron verdes sin tocarlos** (R-T-03): `EntregablesTests.cs` y `EntregablesPantallaTests.cs` no
  figuran en el commit.
- **Dos tests ajenos sí se tocaron, y es el precedente de M17 y M19:** `AgentesOrganizacionTests` y
  `HerramientasDocumentosTests` filtran «lo que no es de esta familia» enumerando las familias de plataforma; cada módulo
  nuevo se agrega a ese filtro. Son 2 líneas y no aflojan ninguna aserción.

### Lo que quedó afuera
- **Pantalla: ninguna**, por decisión del diseño (meterle una calculadora al portal sería construir la peor calculadora
  del mercado). Lo único visible es el paso y el rótulo de la ficha.
- Potencia, raíz, logaritmos, fechas y variables libres: no están en RF-M20-02 y no se agregaron.
- `MotivosParaLaPersona` **no** recibió pares nuevos: los motivos de una cuenta ya están escritos en minúscula y sin
  punto final, se leen igual para el modelo y para la persona, y ninguno nombra un código interno.
- `ResumenPasosTests.TodasLasHerramientas` no incorpora `calcular` (tampoco tiene a M14, M17 ni M19): se dejó como está y
  las mismas propiedades se verifican en `CalculoTests`.
- Sin push y sin deploy: los hace el orquestador después de QA.
# M18 — Portal del cliente del estudio (rol Cliente)

Estado: **implementado 2026-09-24; pendiente de QA; 5 commits locales, sin push y sin deploy (los hace Joaquín)**.
Repo `C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `4e15029`. Entrada: análisis M18 (13 CU, RF-M18-01..36,
12 criterios, 6 riesgos), `docs/diseno-portal-cliente.md` (11 pantallas, 20 ViewModels, 4 máquinas de estado, 15 HU,
D-M18-1..12) y el bloque M18 de `3-arquitecto-mvc.md` (AR-M18-1..5 y las 5 etapas). Gate: definiciones 2, 3 y 4
aprobadas por Joaquín el 2026-09-24 («de corrido hasta QA»); presupuesto omitido (proyecto personal).

### Escaneo de reutilización
- **Otros proyectos:** `cma-centro-medico` (HU-07, `PAT-017`) dejó planteado un portal de autogestión del paciente con un
  service dedicado que resuelve el id **desde el usuario autenticado, nunca desde la URL**; nunca se implementó, así que
  **se tomó el criterio y no el código**. `audifonos-bariloche` lo listó como exclusión y `century-21` confirmó que el
  autoregistro es nuevo en el estudio. Ningún otro proyecto del historial tiene un tercero autenticado adentro del tenant.
- **Del propio repo, sin escribir un camino nuevo:** el pipeline de documentos de M5 (`IDocumentoCarteraService`), el
  patrón de propuesta de M4b/M7b, el límite de gasto y las aprobaciones de M6, `IPreparadorTareaTrabajo` de M7a, el
  rate limiting del portal y el design system de la instrucción 38. Patrón nuevo catalogado: **`PAT-042`**.

### Plan por etapas (el orden en que se hizo, un commit local por etapa)
1. Línea base: `dotnet test` **747/747**.
2. **E1 — La frontera** (`8e1eef4`): rol, `ClienteCarteraId`, `EsCliente`/`EsMiembro`, policies, `FiltroCliente`,
   `AplicarReglasCliente`, arreglo de las fugas de AR-M18-1 y migración `PortalCliente`. Sin una sola pantalla. **815 tests.**
3. **E2 — Entrar** (`32fece8`): configuración de la organización, código de acceso, registro anónimo, `_LayoutCliente`,
   Inicio y Mi ficha. **841 tests.**
4. **E3 — Documentos** (`67c773e`): `Origen` y `VisibleParaCliente`, subida del cliente por el pipeline de M5, interruptor
   y badge del lado del estudio. **856 tests.**
5. **E4 — Pedidos** (`6e2e465`): pedidos e ítems, revisión con motivo obligatorio, herramienta de propuesta y la tarjeta
   para aplicarla. **878 tests.**
6. **E5 — Consultas** (`0000506`): `TipoTarea.ConsultaCliente`, herramientas por inclusión, escalado de aprobación a
   Director y consumo por cliente. **891 tests.**

### Archivos y capas modificadas
- **Domain:** `Enums/EnumsOrganizacion.cs` (`RolOrganizacion.Cliente = 3`), `Enums/EnumsAgentes.cs`
  (`TipoTarea.ConsultaCliente = 5`), `Enums/EnumsPortalCliente.cs` (nuevo), `Entities/IClienteOwned.cs` (nuevo),
  `Entities/MiembrosDeOrganizacion.cs` (nuevo), `Entities/PortalCliente.cs` (nuevo: `CodigoAccesoCliente`,
  `PedidoDocumentacion`, `ItemPedidoDocumentacion`, `PropuestaPedidoDocumentacion`, `AgenteHabilitadoCliente`),
  `ApplicationUser` (+`ClienteCarteraId`), `DocumentoCartera` (+`Origen`, +`VisibleParaCliente`), `Tenant` (+3 columnas),
  `Tareas.cs` (`TareaAgente : IClienteOwnedOpcional`).
- **Application:** `Interfaces/IPortalClienteService.cs`, `ICodigosAccesoService.cs`, `IPedidosDocumentacionService.cs`
  (nuevos), `Helpers/MensajesPortalCliente.cs` (nuevo, los textos exactos del §9), `Settings/PortalClienteOptions.cs`
  (nuevo), `DTOs/PortalClienteDtos.cs` (nuevo), `IContextoUsuario` (+`ClienteCarteraId`), `IPermisosOrganizacion`
  (+`EsCliente`, comentario de `EsMiembro`), `IDocumentoCarteraService` (+`SubirComoClienteAsync`,
  +`CambiarVisibilidadParaClienteAsync`), `Motor/NotaSubtarea.cs` (`ClasesDeTarea`), `Motor/IMotorAgentes.cs`
  (+`IniciarConsultaClienteAsync`), `Motor/IResolvedorHerramientas.cs`, `Motor/DescripcionesHerramientas.cs`,
  `DTOs/DocumentosDtos.cs`, `DTOs/GastoDtos.cs`.
- **Infrastructure:** `Services/PortalCliente/` (nuevo: `PortalClienteService`, `CodigosAccesoService`,
  `ConfiguracionPortalClientesService`, `PedidosDocumentacionService`, `HerramientasPedidoDocumentacion`),
  `Data/AppDbContext.cs` (`FiltroCliente` + `AplicarReglasCliente`), `Data/Configurations/PortalClienteConfigurations.cs`
  (nuevo) y `ApplicationUserConfiguration.cs` (FK + `CK_Usuario_Cliente`), `Services/Organizacion/ResolvedorSesion.cs`,
  `PermisosOrganizacion.cs`, `ContextoUsuario.cs`, `MiembroService.cs`, `Services/Documentos/DocumentoCarteraService.cs`,
  `Services/Motor/{ProcesadorTareas,ResolvedorHerramientas,ServicioTareas}.cs`, `Services/Gasto/ConsumoService.cs`,
  `Services/Asistente/HerramientasAsistente.cs`, `Services/Asignaciones/TareaAsignadaService.cs`,
  `Services/Programaciones/ProgramacionTareaService.cs`, `Services/Agentes/AnatomiaAgenteService.cs`,
  `Services/Analista/HerramientasAnalista.cs`, `Services/Asistente/PropuestaTrabajoService.cs`, `DependencyInjection.cs`.
- **Web:** policies `RequirePortalCliente` y `NoEsCliente` (esta última en la **policy por defecto**),
  `Controllers/{Acceso,Portal,PortalDocumentos,PortalPedidos,PortalConsultas,PortalClientes,Pedidos}Controller.cs` y
  `PortalClienteControllerBase.cs` (nuevos), `CarteraController`, `DocumentosController`, `HomeController`, `Program.cs`,
  `Views/Shared/_LayoutCliente.cshtml` + `_Layout.cshtml`, `Views/{Portal,PortalDocumentos,PortalPedidos,PortalConsultas,PortalClientes,Pedidos,Acceso}/`
  (nuevas), `Views/Cartera/{Detalle,_CardPortalCliente,_ScriptPortalCliente}.cshtml`, `Views/Documentos/Index.cshtml`,
  `Views/Consumo/_TablasConsumo.cshtml`, `wwwroot/css/portal-cliente.css` (nuevo), `Models/PortalClienteViewModels.cs` (nuevo).
- **Datos:** migración **`PortalCliente`** (20260924221250). `Mcp` y `Cli` **sin tocar** (congelados).
  **`distribuible/` sin tocar: ni una línea** (regla permanente del plan §9).

### Decisiones de implementación
- **DI-M18-A — La frontera se cierra tres veces, no una.** (1) `EsMiembro` deja de alcanzar a un cliente, y con eso los 29
  controllers existentes lo rechazan sin tocar ninguno. (2) `NoEsCliente` entra en la **policy por defecto**: los
  `[Authorize]` a secas —Agentes, Tareas, Notificaciones y el hub de SignalR— tampoco le abren nada, ni un endpoint que se
  escriba mañana. (3) `FiltroCliente` + `AplicarReglasCliente` en la base: una consulta que se escape de las dos anteriores
  igual devuelve cero filas ajenas, y una escritura cruzada tira excepción.
- **DI-M18-B — AR-M18-1 tenía más fugas que las dos medidas.** El grep completo de `RolOrganizacion` encontró que
  **`u.RolOrganizacion != null` era el modismo de «es del equipo» en siete services**. Se centralizó en
  `MiembrosDeOrganizacion.SoloMiembros()`, un solo lugar, para que el día que se agregue otro rol de afuera no haya que
  salir a buscar los `!= null` uno por uno. La fuga cara era la del asistente del Director, que los listaba como
  «Empleado» y los hacía **asignables de trabajo**.
- **DI-M18-C — `/acceso` responde 404 si NINGUNA organización tiene el portal encendido.** La URL del registro no está
  scopeada por organización (el código es lo que identifica al estudio), así que el criterio de HU-M18-01 se cumple con la
  condición global. Con el portal apagado en una organización, su código no sirve igual.
- **DI-M18-D — El cliente entra al pipeline de M5 por una puerta propia, no por un pipeline propio.**
  `DocumentoCarteraService` pasó de `Miembro()` a `MiembroOCliente()` en las cuatro operaciones que el cliente necesita;
  para un miembro **no cambió nada**, y para un cliente cada método agrega su propia condición. Un documento del estudio
  sin el interruptor da **404, no 403**: no confirma que exista.
- **DI-M18-E — La lista blanca de herramientas se arma por inclusión y descarta el encabezado del agente.** Un agente de
  la empresa puede nombrar un conector en su encabezado; en una `ConsultaCliente` se descarta igual y queda solo leer su
  carpeta más `pedido_documentacion_proponer`. Si mañana se agrega una familia de herramientas, un cliente **no la recibe
  por olvido**.
- **DI-M18-F — `ClasesDeTarea`: por primera vez «no es Trabajo» dejó de ser sinónimo de «es plataforma».** La consulta de
  un cliente arma el MISMO contexto que una tarea de trabajo sobre ese cliente (formato 1/2, reglas del cliente), así que
  el tipo nuevo **no mueve el prompt de sistema ni el hash de las tareas del estudio**: los 5 goldens quedaron idénticos.
- **DI-M18-G — Un cliente nunca aprueba nada, con dos cierres.** En el procesador, una `ConsultaCliente` fuerza el nivel a
  `Director` cualquiera sea el que declare la herramienta; y `AprobacionService` ya acotaba `NivelAprobacion.Autor` a las
  tareas de `Trabajo`. Se probó con el caso peligroso: un pedido guardado a mano con nivel `Autor`.
- **DI-M18-H — La conversación del cliente se arma aparte y no reusa la del estudio.** Reusar la vista recortada era lo
  que pedía el diseño, pero la forma segura de que no se filtre nada del núcleo es **no tener de dónde filtrarlo**: de
  cada paso del modelo se toma solo el texto. Sin «Ver pasos», sin costo, sin nombres de herramienta.
- **DI-M18-I — El menú del cliente creció etapa por etapa.** Cada opción se sumó junto con la pantalla que la cumple, para
  que ningún commit intermedio ofreciera algo que todavía no estaba.

### Migración EF
`PortalCliente` (20260924221250), **el esquema completo de M18 en una sola migración**, como pide la arquitectura:
- `AspNetUsers`: `+ClienteCarteraId int NULL`, FK a `ClientesCartera` `ON DELETE RESTRICT`, índices
  `(ClienteCarteraId)` y `(TenantId, ClienteCarteraId)`, y **check constraint `CK_Usuario_Cliente`**:
  rol 3 ⟺ `ClienteCarteraId IS NOT NULL`.
- `DocumentosCartera`: `+Origen int NOT NULL DEFAULT 1` (Estudio), `+VisibleParaCliente bit NOT NULL DEFAULT 0`.
- `Tenants`: `+PortalClientesHabilitado bit NOT NULL DEFAULT 0`, `+TopeUsuariosPorCliente int NOT NULL DEFAULT 3`,
  `+LimiteGastoClientePorDefecto decimal(18,2) NULL`.
- Tablas nuevas: `CodigosAccesoCliente` (hash único), `PedidosDocumentacion`, `ItemsPedidoDocumentacion`,
  `PropuestasPedidoDocumentacion`, `AgentesHabilitadosCliente`.
- **Backfill explícito** (el default ya lo hace; se escribe para que se lea): todo documento existente queda **del estudio
  y no visible**, y toda organización queda con el portal **apagado**.
- **Impacto:** aditiva. Ninguna columna se borra ni cambia de tipo; ningún índice existente se toca. `Down` revierte todo.
  El check constraint obliga a que el alta de un usuario cliente fije rol y cliente de cartera en el **mismo** `SaveChanges`.

### Ajustes post-QA (2026-09-24, decisión de Joaquín)

Dos temas que QA dejó abiertos, sobre sus 4 fixes (`974edb5`, `aacfe0a`, `6df04a9`, `1915a54`).

- **Ajuste 1 (`3bb0596`) — fuera las reglas que no son del cliente.** QA verificó con datos reales que una regla interna
  sobre honorarios quedó delante del agente al que le pregunta el propio cliente. `SolicitudContexto` suma
  `SoloReglasDelCliente`, que activa solo `IniciarConsultaClienteAsync`: entran las de alcance **Cliente** de ese cliente
  —las generales y las de ese cliente para ese agente— y nada más. El tipo de la tarea pasó a viajar en `CrearTareaDto` y
  se fija **antes** de calcular el contexto, en vez de pisarse después de crear la tarea.
- **DI-M18-J — la misma fuga un renglón más abajo, encontrada haciendo esto.** El índice de memoria (`NotaMemoria`) viaja
  en los **mensajes** con el título y el «cuándo sirve» de cada recuerdo, así que un recuerdo de alcance Organización
  llegaba igual a la consulta del cliente aunque las herramientas de memoria no estuvieran en la lista blanca.
  `RenderizarNotaAsync` suma `soloDelCliente`. RF-M18-27 ya pedía «recuerdos suyos»: se arregló el código, no el criterio.
- **Ajuste 2 (`170a016`) — el agente lee exactamente lo que el cliente ve.** La condición vive en `DelCliente`, por donde
  pasan las tres herramientas de documentos (listar, leer y buscar), y es la **misma** que
  `IPortalClienteService.DocumentosVisibles`. **Cambia lo que decía el §3.3 del diseño** («la carpeta del cliente»
  entera) a sabiendas: coherencia total y cero sorpresas, a costa de respuestas peores cuando el estudio se olvide de
  marcar un documento. Diseño y RF-M18-27 actualizados con la fecha y el motivo.
- **Los 5 tests nuevos se verificaron en rojo** neutralizando los tres arreglos antes de darlos por buenos, para que
  prueben algo y no solo pasen. Suite: **891 → 896**. Los 5 goldens, sin un cambio.
- **Choque de trabajo concurrente:** un `git add` de otro proceso levantó los 7 archivos de código del Ajuste 1 dentro de
  `437c41f`, que por su mensaje solo debería traer los 5 de `nucleo/`. No se reescribió ese commit porque no es del
  implementador; qué archivos sacar está escrito en el mensaje de `3bb0596`.

### Evidencia
- `dotnet build OlvidataAgentes.slnx` → **0 errores** en cada etapa.
- `dotnet test tests/OlvidataAgentes.Tests` (medido sin pipe, con el código de salida): línea base **747/747**;
  final **`Con error: 0, Superado: 891, Omitido: 0, Total: 891`**. **144 tests nuevos.**
- `LectorDocumentosTests.Extraccion_que_supera_el_tiempo_queda_como_no_se_pudo_leer` falló dos veces en corridas completas
  y pasó sola cada vez que se corrió aislada: es el flaky conocido bajo carga, no una regresión.

### Riesgos y supuestos
- **Verificado en verde:** la batería de aislamiento cliente↔estudio y cliente↔cliente, controller por controller contra
  el portal real (`PortalClienteFronteraHttpTests`), más el aislamiento a nivel service y base
  (`PortalClienteFronteraTests`). `ClienteCarteraIdActual` es null para Director, Empleado, staff y procesos de sistema.
- **Supuesto asumido (R-M18-03):** el flujo del código no valida que quien lo recibió sea quien dice ser. Lo entrega un
  humano del estudio a alguien que ya conoce. Es riesgo residual aceptado por Joaquín.
- **Supuesto (R-M18-02):** la lista blanca de herramientas y el hilo recortado acotan la superficie, pero **no son garantía
  total** contra que el agente diga de más en su texto. Mismo reparo que R-M14-02.
- **Pendiente de producto (DA-M18-1):** un usuario cliente no cuenta como miembro en el plan ni en la licencia. Decisión
  comercial de Joaquín antes de publicar; mientras tanto, no cuenta.
- **Pendiente para QA:** los dos temas a 390 px, el estado vacío del portal y la prueba manual de que un cliente logueado
  que pega una URL del estudio en la barra no ve ni el menú. Falta además el smoke contra el portal local con MySQL y
  `Anthropic__Simulado=true`: la migración se generó pero **no se aplicó a ninguna base**.

### Pruebas mínimas para QA
1. Un cliente logueado pide `/Miembros`, `/Cartera`, `/Consumo`, `/Conexiones`, `/Reglas`, `/Tareas` → siempre acceso
   denegado, y en `/` va a su propia portada.
2. Dos clientes del mismo estudio: ninguno ve el documento, el pedido, el ítem ni la consulta del otro, **ni pidiendo su
   id en la barra** (404, no 403).
3. Código usado, vencido, regenerado e inexistente → **el mismo mensaje**, palabra por palabra.
4. Un documento del estudio sin el interruptor no aparece ni se descarga; encenderlo lo muestra y apagarlo lo oculta en
   el acto.
5. Rechazar un ítem sin motivo no pasa; con motivo, el cliente ve el motivo y el ítem vuelve a «Te falta».
6. El agente propone un pedido → **no le llega nada al cliente** hasta apretar «Pedírselo al cliente»; aplicar dos veces
   la misma propuesta falla.
7. Con el portal apagado: `/acceso` 404, sin card en la ficha del cliente, y los usuarios cliente existentes quedan
   afuera en el siguiente request.
8. Dar de baja el cliente de cartera deja afuera a sus usuarios en el siguiente request.
9. Mobile 390 sin scroll horizontal y contraste en los dos temas, en las 5 pantallas del cliente.

### Checklist de merge
- [x] Build y suite completa en verde (891/891, medido sin pipe).
- [x] Migración EF aditiva, con `Down`, backfill explícito y sin tocar índices existentes.
- [x] Sin cambios en `distribuible/`, `Mcp` ni `Cli`.
- [x] Castellano rioplatense en UI, mensajes, logs y comentarios; los textos del §9 del diseño, tal cual.
- [x] Ningún secreto en el código ni en el audit trail (el código de acceso va hasheado y fuera del audit trail).
- [x] Los 5 goldens de hash de contexto, idénticos.
- [ ] QA funcional (etapa 6).
- [ ] Aplicar la migración a la base de desarrollo y smoke manual con el modelo simulado.
- [ ] Push y deploy: los hace Joaquín.
# M16 — Tablero de actividad al iniciar sesión

Estado: **implementada 2026-09-19; el gráfico rehecho por niveles el 2026-09-20; pendiente de QA**. Entrada:
`1-analista-funcional.md` M16 (RF-M16-01..06), `2-disenador-funcional.md` M16 (D-M16-1..7) y `3-arquitecto-mvc.md` M16
(RT-M16-01..03), las tres aprobadas. Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `9bb5f93`, línea base
**601/601**. **Sin migración EF: es todo lectura sobre lo que ya existe. Ni una llamada al modelo. Sin commits.** `Mcp` y
`Cli` sin tocar. Los 5 goldens de contexto, intactos (nada de M16 se acerca al armado del contexto).

> **2026-09-20 — el gráfico se rehízo entero.** Joaquín lo pidió así: *«El mapa de la actividad se tiene que ver de una
> manera más organizada: personas, agentes, tareas y clientes tienen que ser niveles.»* Lo que había era una nube de
> fuerzas donde todo flotaba junto; lo que hay ahora son **cuatro columnas con su rótulo** que se leen de un lado al
> otro. El detalle está más abajo, en **DI-M16-13..19**; lo de arriba de esa lista sigue valiendo tal cual, salvo lo que
> esas decisiones corrigen explícitamente. Línea base de esta vuelta: commit `83c057f`, **621/621**.

### Escaneo de reutilizacion

Se revisaron los `5-implementador.md` de los demás proyectos del estudio: **ninguno tiene un tablero de actividad ni un
gráfico de nodos**, así que no hubo código para traer de otro repo. Lo que sí se reusó, todo del propio portal:

| Fuente | Qué se tomó | Grado |
|---|---|---|
| `ServicioTareas.Visibles()` (M2/RF-12) | La regla de visibilidad por rol tal cual: Director todas, Empleado solo las suyas | Literal |
| `ProgramacionTareaService.BaseListado()` (M12) | Qué programaciones ve cada uno, para las vueltas recientes | Literal |
| `IAprobacionService.ContarPendientesParaMiAsync`, `IProgramacionTareaService.ResultadosSinVerAsync`, `IControlGasto.AvisoParaMiAsync` | **Se llaman, no se reimplementan.** Es la única forma de garantizar el criterio "el contador del tablero coincide con el del menú" | Literal |
| `Views/Tareas/Detalle.cshtml` (M3b) | El patrón de refresco: SignalR más sondeo de respaldo que recarga HTML del servidor, no una aplicación de página única | Patrón |
| `Helpers/SubtareasTextos.cs` (M7a) | Forma del helper de estado, tupla `(Texto, Icono, Clase)` siempre con texto; y el vocabulario «le pidió ayuda a» | Patrón |
| `Views/Shared/_AvisoGasto.cshtml` (M6) | El aviso de gasto del bloque *Te espera*, sin una línea nueva | Literal |
| `site.css` → `.ov-alert`, `.ov-badge`, `.card`, `.ov-page-head` | Todo el armazón visual de los bloques | Literal |

### Plan por etapas (el orden en que se hizo)

1. DTOs, contrato y opciones en Application.
2. `TableroService` en Infrastructure, con la visibilidad de M2 copiada de `ServicioTareas`.
3. Tiempo real: grupo por organización en `TareasHub` y emisión en `NotificadorTareasSignalR`.
4. `HomeController` decide tablero o portada; parcial de los tres bloques renderizado por el servidor.
5. El gráfico: CSS, isla de datos JSON y `tablero.js`.
6. Tests, build, y recién ahí la verificación en el navegador.

### Archivos y capas modificadas

**Application**

- Nuevo `DTOs/TableroDtos.cs`: `TableroDto` (con `Vacio`), `TableroAhoraDto` / `TareaVivaDto` / `VueltaRecienteDto`,
  `TableroEsperaDto` / `AsignacionEsperaDto`, `TableroPasadoDto` / `ActividadTableroDto`, `GrafoTableroDto` /
  `NodoTableroDto` / `AristaTableroDto`, `AlcanceGrafo`, `TiposNodoTablero`, `RelacionesTablero`.
- Nuevo `Interfaces/ITableroService.cs` (un solo método, `ObtenerAsync`).
- Nuevo `Settings/TableroOptions.cs` (sección `Tablero` de `appsettings.json`): topes de filas, tope de nodos y
  segundos de sondeo.

**Infrastructure**

- Nuevo `Services/Tablero/TableroService.cs`. Consultas acotadas por código al tenant y a la visibilidad de M2, todas
  con tope; el grafo sale de **la misma consulta** que las listas, no de una segunda vuelta más abierta. Registrado en
  `DependencyInjection.cs`.

**Web**

- `Hubs/TareasHub.cs`: grupo por organización (`GrupoOrganizacion`) y `SeguirOrganizacion()` **sin parámetros**.
- `Services/NotificadorTareasSignalR.cs`: además del grupo por tarea, emite al grupo de la organización.
- `Controllers/HomeController.cs`: `Index` decide tablero o portada; nuevo `Actividad` devuelve el parcial.
- Nuevos `Models/TableroViewModel.cs`, `Helpers/TableroTextos.cs`, `Views/Home/Tablero.cshtml`,
  `Views/Home/_TableroBloques.cshtml`, `wwwroot/js/tablero.js`.
- `Views/Shared/_Layout.cshtml`: "Inicio" pasa a "Tablero" (con `fa-gauge-high`) **solo para miembros**; el staff sigue
  viendo "Inicio".
- `Middleware/SecurityHeadersMiddleware.cs`: **solo comentario** — queda escrito que d3 y SignalR salen de jsdelivr,
  que ya estaba permitido, y por qué se eligió un origen ya permitido.
- `wwwroot/css/site.css`: bloque `ov-tablero-*` / `ov-grafo-*` y los tres colores del gráfico.

**Tests**: nuevo `tests/OlvidataAgentes.Tests/TableroTests.cs` (20 tests).

### Decisiones de implementacion

- **DI-M16-1 — d3 v7 desde jsdelivr, que YA estaba en el CSP.** RT-M16-02 avisaba que un CDN nuevo no da error: no
  carga y nadie se entera. En vez de agregar un origen se eligió una librería del origen que ya estaba. d3 además
  dibuja **SVG**, que es lo único que permite que los nodos tomen los tokens `--ov-*` y cambien solos con el tema
  oscuro; una librería de canvas (vis-network) habría necesitado su propia paleta duplicada. Hay un **test** que
  compara los `<script src>` de la vista contra el `script-src` del middleware: si alguien cambia de CDN sin tocar el
  CSP, falla en el build y no en silencio.
- **DI-M16-2 — El respaldo del gráfico está en el HTML y se oculta cuando el dibujo existe.** El lienzo arranca
  `hidden` y el script lo muestra recién cuando terminó de dibujar. Si d3 no cargó, lo que queda a la vista es la lista
  de vínculos en palabras que el servidor ya mandó. Cuando el gráfico sí aparece, esa lista pasa a `visually-hidden`
  — **sigue en el DOM**, porque un SVG de nodos no se lee con un lector de pantalla.
- **DI-M16-3 — El aviso al grupo de la organización va vacío.** Al grupo lo escuchan también los Empleados, que no ven
  las tareas de sus compañeros: mandarles el número de tarea ya sería contarles que existe. Reciben "algo se movió" y
  releen `/Home/Actividad`, que aplica la visibilidad del lado del servidor.
- **DI-M16-4 — `SeguirOrganizacion()` no recibe el tenant.** Sale de la sesión resuelta en el servidor (RT-M16-03). Hay
  un test que falla si alguien le agrega un parámetro.
- **DI-M16-5 — El gráfico baja de vivo a hoy, y de hoy a la semana.** El diseño pedía vivo → día. Con la organización
  real (Contadores BMA) apareció el caso aburrido: *Lo que pasó* decía "4 en 7 días" y el gráfico, al lado, mostraba un
  recuadro vacío porque ninguna era de hoy. Se agregó el tercer escalón y el badge dice cuál está mostrando: "En vivo",
  "Hoy" o "Esta semana". Es el mismo motivo que sostiene R-M16-01.
- **DI-M16-6 — El refresco no toca el DOM si el HTML no cambió.** El sondeo corre cada 15 s con socket o sin él, pero
  compara el HTML recibido con el anterior: la vuelta sin novedades no parpadea, no rearma el dibujo y no le borra a
  nadie el nodo que había elegido. Tampoco refresca con la pestaña de fondo ni mientras el foco está adentro del
  gráfico.
- **DI-M16-7 — Solo tareas de tipo `Trabajo`, también para el Director.** Las conversaciones de plataforma
  (configurador de reglas, asistente de reparto) son la persona configurando el sistema, no trabajo para un cliente:
  incluirlas pondría "Asistente para repartir trabajo" como un nodo más al lado de los agentes del rubro.
- **DI-M16-8 — Los ids del grafo son opacos (`p1`, `a2`, `c3`).** No viaja ningún id de usuario, de agente ni de
  cliente. Lo único con id real es el salto del nodo, que apunta a **una tarea que ya es visible para quien mira** por
  construcción: sale de la misma consulta que las listas.
- **DI-M16-9 — Los tres colores del gráfico se verificaron con el validador de paletas**, contra las dos superficies
  (`#ffffff` y `#1e293b`): banda de luminosidad, piso de croma, separación para daltonismo y contraste. El ámbar del
  cliente baja un paso en tema oscuro (`#f59e0b` → `#d97706`) porque el claro se sale de la banda sobre `#1e293b`. La
  identidad **nunca es solo color**: cada tipo tiene su forma (círculo, cuadrado, rombo) y su entrada en la leyenda, y
  lo vivo lleva el anillo que late **más la etiqueta "en curso"** (D-M16-3). El anillo se queda quieto con
  `prefers-reduced-motion` (R-M16-06).
- **DI-M16-10 — `_TableroBloques` es el mismo parcial que renderiza la pantalla y que devuelve el refresco.** Una sola
  forma de dibujar el tablero; el JavaScript no arma ni un `<li>`.
- **DI-M16-11 — Sin DataTables.** La regla de la instrucción 25 es para los listados de una entidad; acá hay resúmenes
  con tope de 5 a 8 filas que enlazan a las pantallas reales (Tareas, Aprobaciones, Asignaciones, Resultados), que sí
  tienen su grilla con filtros.
- **DI-M16-12 — *Lo que pasó* no tiene, ni puede tener, una lista de personas** (R-M16-07). Hay un test que recorre las
  propiedades de `TableroPasadoDto` y falla si alguna se llama Persona, Miembro o Usuario: el día que alguien quiera
  agregar el ranking, se va a topar con el test antes que con la pantalla.

### El gráfico por niveles (2026-09-20)

Lo que cambió de capa a capa: **Application** — `TiposNodoTablero` suma `Tarea` y la lista `Niveles` (que *es* el orden
de las columnas); `RelacionesTablero` reemplaza `TrabajaSobre` por `Ejecuta` (agente → tarea) y `EsPara` (tarea →
cliente); `NodoTableroDto` suma `Nivel`, `Orden` y `Estado`; nuevo `NivelGrafoDto`; `TableroOptions.MaxNodosGrafo` pasa
a `MaxNodosPorNivel`. **Infrastructure** — `ArmadorGrafo` reescrito. **Web** — `TableroTextos.Nivel()`, la isla de datos
manda niveles y orden, la leyenda suma Tareas y «le pidió ayuda a», la lista de respaldo se agrupa por nivel, y
`tablero.js` pasa de simulación de fuerzas a disposición calculada. **Sin migración EF, otra vez: no hay ni una columna
nueva.**

- **DI-M16-13 — La tarea es el nodo del medio, y de él cuelga la cadena entera.** El recorrido se lee
  `persona → agente → tarea → cliente`; una tarea sin cliente termina en su nivel, sin arista de salida. Como
  consecuencia, **si una tarea no entra en el tope de su nivel, la fila entera se saltea**: media cadena dibujada (un
  cliente suelto, un agente sin tarea) confunde más de lo que muestra. El nodo lleva `#218` como etiqueta y su estado
  como detalle, así que el gráfico dice además *en qué anda* cada trabajo sin mostrar una línea de su texto (RF-M16-06
  sigue en pie).
- **DI-M16-14 — Las partes de M7a se quedan DENTRO del nivel de los agentes, como un arco punteado.** Era la decisión
  fina del pedido. Sacarlas del nivel (poner al ayudante en una quinta columna) rompía la lectura, y dejarlas como una
  flecha entre columnas obligaba a que alguna volviera hacia atrás. Van como **un arco al costado de la columna, del
  coordinador al ayudante**, punteado para que se lea como un desvío y no como el camino, con su entrada propia en la
  leyenda. La dirección la garantiza el orden del nivel (DI-M16-15), no el dibujo. Y el ayudante igual tiene su propia
  tarea en la columna de al lado: la parte también es un nodo.
- **DI-M16-15 — Los agentes se ordenan por topología, no por nombre.** Es lo que hace imposible la flecha hacia atrás:
  un Kahn sobre las aristas «le pidió ayuda a» deja al coordinador **siempre por delante** del que ayudó, con desempate
  por nombre para todo lo demás. Determinístico igual, y si alguna vez llegara un ciclo (no puede: el padre de una tarea
  siempre es anterior) lo que quedó sin ubicar se agrega por nombre en vez de desaparecer del dibujo. Hay un test con el
  ayudante renombrado para que, por orden alfabético, fuera primero: si alguien saca la topología, falla.
- **DI-M16-16 — El lugar de cada nodo lo decide el servidor; el navegador solo lo pasa a píxeles.** `Nivel` y `Orden`
  viajan en el DTO. Personas y clientes por nombre, tareas de la más nueva a la más vieja (el número ya es la línea de
  tiempo), agentes por topología. **Cuidado con no confundir dos órdenes distintos**: los nodos *entran* por recencia
  (las filas llegan ordenadas, así que el tope deja afuera lo viejo) y *se dibujan* por la regla determinística. Hay un
  test que pide el tablero dos veces y compara `nivel:orden:etiqueta`, y otro que falla si alguien vuelve a meter
  `forceSimulation` en el JS — que es la forma silenciosa de deshacer todo esto.
- **DI-M16-17 — El tope es por nivel, no global.** El nivel que se llena primero es siempre el de tareas; un tope global
  dejaba columnas enteras sin dibujar por culpa de él. Cada columna cuenta su propio «y N más» al pie, y el `Omitidos`
  del DTO es la suma. El navegador suma a ese número **lo que no entra por espacio**: si en una columna no caben los 8,
  muestra los que caben y el resto va al mismo cartel. El alto del dibujo reserva ese renglón — sin la reserva el cartel
  se dibujaba por debajo del borde del SVG, que es justo el aviso que no se puede perder.
- **DI-M16-18 — Columnas si entran, filas apiladas si no; y el SVG se mide en píxeles reales.** Se sacó el `viewBox`:
  ahora el script mide la tarjeta y dimensiona el SVG, así que el texto mide lo que dice que mide y desapareció la media
  query que inflaba las etiquetas para compensar la escala. Por debajo de **416 px** cuatro columnas dejan ~80 px para
  cada nombre, así que ahí el dibujo da vuelta los niveles y los apila como filas — un teléfono cae siempre de ese lado.
  Las etiquetas **se recortan midiéndolas** (`getComputedTextLength`), no contando letras: calcular por cantidad de
  letras fallaba apenas cambiaba el tamaño de fuente y el nombre se salía del dibujo por el costado.
- **DI-M16-19 — Dos arreglos de legibilidad que no estaban pedidos pero se veían feos.** (a) Las columnas cortas van
  **centradas** contra la más larga: si no, los clientes quedan todos arriba y las flechas trepan en diagonal desde
  abajo. (b) Las etiquetas llevan un **halo del color de la tarjeta** (`paint-order: stroke fill`): en un dibujo de
  cuatro columnas siempre hay una línea que pasa por donde está un nombre, y sin el halo la línea se le mete entre las
  letras. El contorno va debajo del relleno, así que el texto se lee igual y lo que cambia es lo que pasa por atrás.
- **Lo que NO cambió, a propósito:** los tres colores (y por lo tanto no hubo que revalidar nada — se volvió a correr el
  validador contra `#ffffff` y `#1e293b` y sigue pasando); la forma por tipo; la etiqueta «en curso» además del anillo;
  el escalón vivo → hoy → semana con su badge; `prefers-reduced-motion`; la visibilidad de M2 dentro del gráfico; el
  respaldo en palabras sin JavaScript; d3 desde jsdelivr y su test de CSP. **La tarea es el único nodo sin color propio
  —es el eslabón, no una categoría más—**: va en tinta neutra con su hexágono, que es lo que permitió sumar un cuarto
  tipo sin tocar la paleta validada. Se sacó el arrastre de nodos: con los niveles fijos, mover un nodo a mano solo
  podía romper la disposición.

### Migraciones EF

Ninguna. Ni una columna nueva: todo sale de datos que ya estaban.

### Evidencia de build y tests (medida SIN pipe, leyendo el resumen impreso)

- `dotnet build OlvidataAgentes.slnx`: **0 errores, 0 advertencias**. La advertencia preexistente CS0114 de
  `HomeController.StatusCode` desapareció porque se le puso `new` al reescribir el archivo (mismo comportamiento: la
  declaración ya ocultaba el método base). La de `ReglasPropuestasAgentesTests` (xUnit2013) sigue estando y aparece
  cuando recompila ese proyecto.
- `dotnet test tests/OlvidataAgentes.Tests`: **621 OK de 621** (601 de línea base + 20 nuevos).
- `LectorDocumentosTests` falló una vez en cada una de dos corridas intermedias, siempre un test distinto de esa clase
  y siempre verde al correrla sola (31/31): es la flojera conocida bajo carga, no una regresión de M16.

**Del gráfico por niveles (2026-09-20):** `dotnet build OlvidataAgentes.slnx` **0 errores, 0 advertencias**. (En una
corrida intermedia apareció 1 advertencia: la xUnit2013 preexistente de `ReglasPropuestasAgentesTests`, que se muestra
solo en el build en el que recompila ese proyecto. No es de M16 y ya estaba anotada arriba.) `dotnet test`:
**Con error: 0, Superado: 625, Omitido: 0, Total: 625** (621 de línea base + 4 nuevos), medido dos veces y sin una sola
vuelta roja. `TableroTests` sola: **24/24**. Los 47 tests de contexto y goldens, verdes y con los `.txt` sin tocar.

Los 4 tests nuevos son los que sostienen el pedido: el recorrido de cuatro niveles con toda arista avanzando un nivel;
la tarea sin cliente que termina en su nivel; el orden determinístico (dos llamadas seguidas, mismo `nivel:orden`); y el
coordinador por delante del ayudante con el nombre en contra. Se reescribieron otros tres: el de M7a (ahora comprueba
que la ayuda no salga del nivel), el del tope (ahora por nivel) y el de ids opacos (ahora con la `t` de tarea).

### Verificación en el navegador (dev, MODELO SIMULADO confirmado en el log de arranque)

`https://localhost:7200`, organización **Contadores BMA** (tenant 20), con datos reales.

- **Director (`direccion@bma.test`), sin actividad viva**: los tres bloques presentes. *Ahora* dice "No hay nada
  corriendo en este momento." con el botón *Pedir una tarea*; *Te espera* dice "No tenés nada pendiente. Todo al día.";
  *Lo que pasó* muestra 4 agentes y 2 clientes, "0 hoy · 4 en 7 días". El gráfico dibuja los 8 nodos de la semana
  (2 personas, 4 agentes, 2 clientes) con badge "Esta semana". Al tocar el nodo *Gastón*: "Persona · Gastón / 3
  trabajos / Gastón le pidió a …" y el enlace *Ver la tarea*.
- **Empleado (`gaston@bma.test`)**: ve **3 agentes, él mismo y su cliente**. No aparecen "Dirección BMA", "Cierre y
  balance" ni "SERVICIO TERAPIA RENAL S.A.": la tarea de la Directora no está ni en las listas ni en el gráfico.
- **Con actividad**: con una tarea creada con el modelo simulado, *Ahora* muestra «Gastón le pidió a «Ingresos
  Brutos»» · Trabajando · Paso 1 de hasta 25 · recién, con su barra de avance, y el gráfico pasa a "En vivo" con el
  anillo que late y la etiqueta "en curso". **Sin recargar**, el bloque se llenó a los ~2,5 s de crear la tarea y se
  vació solo cuando terminó. Las dos tareas de prueba (#218 y #219) y sus 4 filas de `EventosUso` **se borraron**:
  Contadores BMA quedó con sus 4 tareas originales y Gastón con su preferencia de tema como estaba.
- **Consola del navegador: 0 errores, ninguna violación de CSP.** El único warning es el de
  `apple-mobile-web-app-capable`, preexistente del layout.
- **Tema oscuro** verificado (tarjetas, tablas y los tres colores del gráfico). **Mobile 390**: los tres bloques
  apilados y el gráfico abajo; `scrollWidth` 388 contra `clientWidth` 385 — los 3 px los aporta el dropdown de usuario
  del topbar, **preexistente**; nada de `ov-tablero-*` ni `ov-grafo-*` se pasa del ancho. En teléfono las etiquetas del
  gráfico se agrandan por media query, porque el SVG se escala al ancho de la tarjeta.

**Del gráfico por niveles (2026-09-20)**, mismo portal y mismo modelo simulado (confirmado en el log de arranque):

- **Director, sin actividad viva**: cuatro columnas rotuladas PERSONAS · AGENTES · TAREAS · CLIENTES, y la semana de
  Contadores BMA se lee entera de izquierda a derecha — Dirección BMA y Gastón, sus 4 agentes, las tareas #205 a #202 y
  los 2 clientes. Tocando el nodo `#204`: *«Tarea · #204 / Completada / Comunicación con el cliente trabaja en #204 /
  #204 es para Cliente CUIT 30-70823732-5»* y el enlace *Ver la tarea*.
- **Con actividad**: se creó una tarea con el modelo simulado (#220, coordinador del estudio sobre SERVICIO TERAPIA
  RENAL) y la cadena apareció completa. El anillo que late, la etiqueta «en curso», las aristas vivas en color primario
  y **el arco punteado de M7a dentro de la columna de agentes**, del coordinador al ayudante, se verificaron dibujados.
- **Empleado (`gaston@bma.test`)**: ve **solo su cadena** — él, sus 3 agentes, sus 3 tareas y su cliente. Se buscó en el
  HTML del tablero «Dirección BMA», «Cierre y balance», «SERVICIO TERAPIA», «#220», «#205», «Coordinador del estudio» y
  el texto del pedido de prueba: **ninguno aparece**. La visibilidad de M2 sigue intacta dentro del gráfico.
- **Sin actividad ninguna**: se comprobó el estado vacío real (los tres bloques con sus mensajes y el gráfico diciendo
  «Cuando haya trabajo, acá se dibuja quién le pidió qué a quién»).
- **Sin JavaScript**: el respaldo del servidor ahora se lee nivel por nivel — *«Personas · Gastón le pidió a … | Agentes
  · Comunicación con el cliente trabaja en #204 | Tareas · #204 · Completada es para Cliente CUIT… | Clientes · …»*.
- **Mobile 390**: los niveles se apilan como filas, flujo de arriba hacia abajo, con su rótulo cada una. `scrollWidth`
  **385 contra `clientWidth` 385**: desapareció incluso el desborde de 3 px que quedaba, porque el SVG ya no se escala.
  Se verificó además por `getBBox` que **ninguna etiqueta se sale del lienzo**.
- **Tema oscuro** verificado: el hexágono de la tarea toma la superficie de la tarjeta y el halo de las etiquetas cambia
  con el tema, igual que el resto.
- **Consola: 0 errores, ninguna violación de CSP.** El único warning sigue siendo el de `apple-mobile-web-app-capable`.
- **Datos de prueba borrados**: la tarea #220, su paso y sus 2 filas de `EventosUso`. Contadores BMA quedó con sus 4
  tareas originales (#202–#205) y `eventosuso` con su máximo anterior (550). Para ver el estado vacío se corrió hacia
  atrás la fecha de la tarea #201 del tenant 19 y **se restauró al valor exacto** (`2026-09-19 20:41:52.381619`).

### Pruebas mínimas para QA

1. Entrar como Director y como Empleado de la misma organización: el Empleado no puede ver en el gráfico ni en las
   listas una tarea que no pidió él.
2. Entrar como staff de Olvidata: tiene que seguir viendo la portada del backoffice, no un tablero vacío.
3. Con una tarea corriendo, mirar el tablero sin recargar: tiene que aparecer y después desaparecer sola.
4. Apagar JavaScript: los tres bloques y la lista de vínculos del gráfico tienen que seguir estando.
5. Comparar el número de *Aprobaciones* del tablero con el contador del menú.
6. Buscar el texto de un pedido dentro del HTML del tablero: no tiene que estar.
7. Mobile 390 y tema oscuro.
8. Una organización sin ninguna actividad todavía: los tres bloques tienen que estar igual, con sus mensajes.

Del gráfico por niveles:

9. Mirar el gráfico y leerlo en voz alta de izquierda a derecha: tiene que dar una frase («Gastón le pidió a Ingresos
   Brutos, que trabaja en la #203, que es para tal cliente»). Los cuatro rótulos tienen que estar a la vista.
10. Refrescar la pantalla varias veces: **ningún nodo se mueve de lugar**. Es el criterio central del pedido.
11. Buscar una arista que apunte hacia la izquierda (o hacia arriba en mobile): **no tiene que haber ninguna**. La única
    que no cruza de columna es la punteada de «le pidió ayuda a», y va siempre del coordinador al que ayudó.
12. Una tarea sin cliente: la cadena tiene que cortarse en la columna de Tareas, sin flecha de salida.
13. Una organización con muchas tareas: cada columna corta en 8 y dice «y N más» al pie, y ese cartel **tiene que
    verse** (no quedar debajo del borde del dibujo).
14. Achicar la ventana de a poco: al pasar por ~416 px el dibujo da vuelta los niveles de columnas a filas sin recargar
    y **sin scroll horizontal**.
15. Un nombre largo de cliente: la etiqueta se recorta con «…» y no se sale del recuadro, en escritorio y en teléfono.

### Checklist de merge

- [x] Build **0 errores, 0 advertencias**.
- [x] Suite completa **625/625**, medida sin pipe (621 de línea base + 4 nuevos).
- [x] Los 5 goldens de contexto, verdes y sin tocar.
- [x] Sin migración EF.
- [x] `Mcp` y `Cli` sin tocar.
- [x] Sin commits; `git status` solo con los 9 archivos de M16.
- [x] Datos de prueba creados en dev, borrados al terminar; la fecha que se movió, restaurada al valor exacto.
- [x] Verificado en el navegador con los dos roles, en los dos temas y a 390 px.
- [x] d3 sigue saliendo de jsdelivr; el test que compara los `<script src>` contra el `script-src` del CSP, verde.
- [x] Los tres colores del gráfico, sin tocar y revalidados contra las dos superficies.
- [ ] QA funcional (pendiente).

### Riesgos y supuestos

- El sondeo cada 15 s por pestaña abierta es el costo que acepta RT-M16-01. Si pesa, lo que corresponde es cachear por
  organización unos segundos (no por usuario) o subir `Tablero:SegundosSondeo`.
- El gráfico corta en **8 nodos por nivel** y cuenta "y N más" en cada columna. Con una organización grande el corte va
  a ser lo normal: lo que entra es lo más reciente, así que se ve lo último y no una muestra al azar.
- `NodoTableroDto.Trabajos` cuenta **participaciones** en las tareas dibujadas (un agente coordinador suma por cada
  parte que pidió). Es el tamaño de la figura, no una métrica para leer.
- **La disposición por niveles no minimiza cruces.** Con varias tareas sobre pocos clientes, las curvas que llegan a la
  columna de clientes se cruzan. Se decidió no tocarlo: cualquier reacomodo por baricentro entra en tensión con el
  criterio de Joaquín de que los nodos no se muevan, y el cruce de una curva molesta bastante menos que un nodo que
  salta de lugar. Si alguna vez pesa, lo que corresponde es ordenar la columna de clientes por baricentro **a partir de
  la base determinística**, no cambiar la regla de orden.
- El tope por nivel y el ancho de la tarjeta son dos límites distintos: el servidor corta en 8 y el navegador puede
  cortar antes si no le entran. Los dos suman al mismo cartel, así que el número siempre dice la verdad de lo que falta.
- El "tablero de staff sobre todas las organizaciones" sigue fuera de alcance, como dice el análisis.
# M15 — Ficha de rubro para el staff (Nucleo/Rubro enriquecida)

Estado: **implementada 2026-09-18, pendiente de QA**. Entrada: pedido de Joaquín (la información de un rubro se veía a
pedazos y **qué organizaciones lo tienen habilitado no se veía en ningún lado**). Repo:
`C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `e248922`. **Sin migración EF. Solo lectura: ni un `<form>` de
escritura ni un endpoint POST nuevo. Ninguna llamada a la API real, sin commits.** `Mcp` y `Cli` sin tocar.

### La decisión de dónde ponerla: se enriquece `Nucleo/Rubro`, no se crea una pantalla nueva

Una pantalla nueva habría repetido nombre, descripción, "incluido en todas las suscripciones", etapas y el desglose de
artefactos — o sea, casi todo lo que `Nucleo/Rubro` ya mostraba. Dos pantallas que dicen lo mismo envejecen distinto y
obligan a elegir cuál mirar. `Nucleo/Rubro` **ya es la ficha del rubro**: le faltaban tres cosas (el desglose por tipo
con publicados/pendientes, quién lo tiene habilitado, y el estado de importación), no una pantalla.

De paso se **eliminó una duplicación que ya existía**: la card suelta "Material de referencia" pasó a ser una fila del
desglose, con su botón "Ver el material" en la fila. Antes había dos lugares donde se contaba el material.

**Rubros como datos, no como ABM.** La pantalla no da de alta ni edita: un rubro sigue siendo un manifiesto del repo que
entra con la consola Admin, versionado por hash, con diff, historial y gate de publicación. Eso quedó escrito en el
resumen XML de `IFichaRubroService` y de `FichaRubroService` para que no se erosione.

### Escaneo de reutilizacion
| Fuente | Qué se tomó | Grado |
|---|---|---|
| `Views/Clientes/Details.cshtml` (vocabulario de licencias) | Las tres palabras Vigente / Vencida / Revocada y el criterio `!Revocada && VigenteHasta > ahora` → `NucleoTextos.EstadoLicencia` | Patrón |
| `Helpers/PruebasTextos.cs` (M8) | Forma del helper de estado: tupla `(Texto, Icono, Clase)`, nunca color solo | Patrón |
| `AgenteOrganizacionService.cs:89` | `IgnoreQueryFilters([AppDbContext.FiltroTenant])` para consultar licencias como staff | Literal |
| `ClientesController.Index` | Exclusión de la organización interna (`!t.EsInterna`, RT-M8-11) | Literal |
| `site.css` → `.ov-detail-grid` | Bloque de pares etiqueta/valor del resumen. **Sin una línea de CSS nueva** | Literal |

No se agregó nada al catálogo de patrones: es una pantalla de detalle de backoffice, sin componente reutilizable nuevo.

### Archivos y capas modificadas
**Application**
- `DTOs/AgentesDtos.cs`: `FichaRubroDto`, `DesgloseArtefactosDto`, `OrganizacionConRubroDto`.
- `Interfaces/INucleoServices.cs`: `IFichaRubroService` (un solo método, `ObtenerAsync(slug)`).

**Infrastructure**
- Nuevo `Services/Nucleo/FichaRubroService.cs`. Cuatro consultas: última versión importada, versiones esperando
  publicación, desglose por tipo y organizaciones habilitadas. Registrado en `DependencyInjection.cs`.

**Web**
- Nuevo `Helpers/NucleoTextos.cs`: nombre de cada tipo de artefacto (singular, plural, una línea de ayuda y clase de
  badge), estado de licencia y fechas en hora argentina. Reemplaza los dos `switch` inline que había en la vista.
- `Controllers/NucleoController.cs`: `Rubro(string id)` inyecta `IFichaRubroService` y pasa la ficha. Nada más.
- `Models/AgentesViewModels.cs`: `NucleoRubroViewModel` suma `Ficha` y `AhoraUtc`.
- `Views/Nucleo/Rubro.cshtml`: resumen, etapas (con estado vacío), "Qué trae este rubro", "Quién lo tiene habilitado" y
  "Detalle de los artefactos".

**Tests**: nuevo `tests/OlvidataAgentes.Tests/FichaRubroTests.cs` (6 tests).

### Decisiones de implementacion
- **DI-M15-1 — "Última versión importada", no "última importación".** No hay registro de importaciones, y un import que
  no cambia ningún hash **no da de alta versiones**. Se informa lo que sí es verificable (el `CreatedAt` de la versión
  más nueva) y el rótulo dice exactamente eso. Prometer "última importación" sería mentir en los casos aburridos.
- **DI-M15-2 — Una fila por organización, con la mejor licencia.** Una organización puede tener varias licencias con el
  mismo rubro. La fila responde "¿lo puede usar hoy?": gana vigente sobre vencida y vencida sobre revocada, y al lado va
  "N licencias incluyen el rubro". El mismo orden ordena la tabla: las vigentes arriba.
- **DI-M15-3 — "Pendientes" del desglose cuenta artefactos, no versiones.** La pregunta del staff es "¿me falta publicar
  algo de este tipo?". El total de versiones esperando el gate va aparte, en el resumen de arriba.
- **DI-M15-4 — `IgnoreQueryFilters([FiltroTenant])` aunque hoy sea redundante.** La sesión de staff ya llega con acceso
  global (`ResolvedorSesion`), así que el filtro no filtra nada. Se ignora igual, por nombre y con comentario: la
  intención queda escrita donde está la consulta y no depende de una decisión que vive en otro archivo. **El filtro de
  borrado lógico sigue puesto.**
- **DI-M15-5 — La consulta va en un service, no en el controller.** `NucleoController` consulta `_db` directo en otras
  acciones, pero la única forma de probar la travesía del filtro de tenant en esta suite (que es de servicios, no de
  controllers) es que la consulta viva en Infrastructure. Además es donde están todos los demás `IgnoreQueryFilters`.
- **DI-M15-6 — `Clientes/Details.cshtml` no se tocó.** Podría usar `NucleoTextos.EstadoLicencia`, pero el helper agrega
  un ícono y eso cambiaría una pantalla que QA ya validó. Queda como mejora menor, anotada abajo.

### Migraciones EF
Ninguna. No se agregó ni cambió una sola columna: todo sale de datos que ya estaban.

### Evidencia de build y tests
- `dotnet build OlvidataAgentes.slnx`: **0 errores, 2 advertencias** — las dos preexistentes (CS0114 en
  `HomeController.StatusCode`, xUnit2013 en `ReglasPropuestasAgentesTests`).
- `dotnet test`: **595 OK / 5 fallidos de 600**. Los 6 tests nuevos pasan.
- **Los 5 fallos son PREVIOS a esta etapa y están en el commit `e248922`.** Verificado guardando los cambios con
  `git stash` y corriendo la suite limpia: **589 OK / 5 fallidos de 594**, los mismos 5 tests. Son los **4 goldens de
  contexto** (`AgentesOrganizacionTests`, `ConfiguradorReglasTests` ×2, `AsistenteDirectorTests`,
  `M14GoldenYPantallasTests`) fallando con hash distinto desde el carácter 0. Nada de M15 toca el render del contexto.
  **Queda como hallazgo para QA: la línea base real del repo no es 594/594.**

### Verificación en el portal (dev, MODELO SIMULADO confirmado en el log de arranque)
- `contable`: 2 organizaciones (Contadores BMA y Estudio Contable Demo), las dos vigentes al 16/09/2027; 10 agentes,
  6 reglas sugeridas y 8 materiales, todos publicados, 0 pendientes.
- `plataforma`: "Ninguna todavía" con la explicación de que es el rubro técnico y no se licencia; 1 versión esperando
  publicación (es PA-13, el configurador v2 en Borrador).
- `inmobiliario`, `estudio-software`: 200. Slug inexistente: 404.
- Un Director de cliente (`socio@contable.test`) sobre `/Nucleo` recibe **403 Acceso denegado**.
- Mobile 390: `scrollWidth == clientWidth` (385/385), **sin scroll horizontal de página**. Tema oscuro verificado.
- **Cero `<form>` dentro de `<main>`** en los 4 rubros: el único formulario de la página es el logout del layout.

### Riesgos y supuestos
- La lista de organizaciones es de **todos los tenants por diseño**. Si alguna vez una policy de cliente llegara a esta
  acción, mostraría datos de otras organizaciones. Hoy lo corta `[Authorize(Policy = "RequireAdministracion")]` a nivel
  de controller (y sigue abierto PA-22: confirmar si el backoffice debería exigir `RequireSuperUsuario`).
- Rendimiento: la consulta trae todas las licencias del rubro y agrupa en memoria. Con miles de licencias habría que
  agrupar en SQL. Hoy son decenas.
- `Nucleo/Index` sigue sin una columna de organizaciones: para saber quién usa un rubro hay que entrar a su ficha.
  Deliberado (era eso o una segunda consulta cross-tenant en el listado); anotado como mejora.
- `Clientes/Details.cshtml` mantiene su propio `if/else` de estado de licencia (DI-M15-6).

### Pruebas minimas para QA
1. Entrar como SuperUsuario a Núcleo IP → Contable y verificar contra la base: organizaciones con el rubro habilitado,
   estado y fecha de vencimiento de cada licencia, y el total del encabezado.
2. Revocar una licencia de una organización que tenga el rubro y recargar: la fila tiene que pasar a **Revocada** y caer
   al final de la tabla.
3. Una organización con dos licencias del mismo rubro (una vencida y una vigente): **una sola fila**, estado Vigente y
   "2 licencias incluyen el rubro".
4. Rubro `plataforma`: lista vacía con la explicación de que no se licencia.
5. Entrar con un usuario de cliente a `/Nucleo/Rubro/contable`: **403**.
6. Mobile 390 y tema oscuro: sin scroll horizontal de página, badges legibles, ningún enum crudo en pantalla.
7. Confirmar que **no hay ninguna acción de escritura**: ni alta, ni edición, ni baja de rubros desde el portal.

### Checklist de salida para merge
- [x] Build 0 errores, advertencias iguales a la línea base.
- [x] Tests nuevos verdes; los fallos restantes probados como preexistentes.
- [x] Sin migración EF.
- [x] Solo lectura verificada en el HTML servido.
- [x] Policy `RequireAdministracion` heredada del controller; 403 probado con usuario de cliente.
- [x] `IgnoreQueryFilters` por nombre y con comentario que dice por qué.
- [x] Mobile 390 y tema oscuro.
- [x] `Mcp` y `Cli` sin tocar. Sin commits.
# M14 — Instructivos, búsqueda web, espacio del cliente y control de gasto

Estado: **implementado 2026-09-17, QA cerrada; los defectos abiertos de QA se corrigieron en la sección de arriba**. Entrada: `1-analista-funcional.md` M14 (RF-M14-01..33, 12 CA,
R-M14-01..06), `2-disenador-funcional.md` M14 (D-M14-1..8, P-M14-01..10) y `3-arquitecto-mvc.md` M14 (RT-M14-01..06).
Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. **Una migración: `InstructivosM14`.**
**Ninguna llamada a la API real de Anthropic, ninguna salida a internet, sin commits.** `Mcp` y `Cli` sin tocar.

Criterio rector de Joaquín: *"que esto sea totalmente entendible para el usuario, explicando qué es cada cosa para no
cometer errores de configuración"*. Ante dos implementaciones posibles se eligió siempre la que deja más claro **cuándo
se usa cada cosa**.

### Escaneo de reutilizacion

| Fuente | Que se tomo | Grado |
|---|---|---|
| M10 `HerramientasConocimiento` | La forma entera de una familia de herramientas de solo lectura: clase base con las guardas, "no está disponible" como única respuesta para todo lo que no corresponde, aviso fijo en cada resultado y resumidor propio para "Ver pasos". `HerramientasInstructivos` es esa pieza con otra fuente de datos | Literal (patrón) |
| M4 `AgenteOrganizacion` | `VisibilidadAgente` (`SoloYo` / `TodaLaEmpresa`) **se reusa, no se clona**: es la misma decisión de producto y el usuario ya la conoce con esas palabras. También el `VersionToken` como token de concurrencia y el criterio de permisos (cualquiera crea los suyos, el Director los de la empresa) | Literal |
| M3 `Regla` / `ReglaEvento` | El versionado: versión vigente en la entidad + historial inmutable con los campos que cambiaron; activar/desactivar **no** versiona | Literal (patrón) |
| M2/M4/M11 columna generada `*Vigente` | Unicidad entre los vigentes con columna generada STORED + índice único, y la migración escrita a mano porque el proveedor ignora `stored: true` | Literal (cuarta vez) |
| M6 `AvisoGasto` / M12 `EjecucionProgramada` | Cómo se cuelga un dato nuevo de un registro inmutable sin tocar su ciclo de vida (el "visto" de los resultados) | Literal (criterio) |
| M8 gate de corridas reales | **Fail-closed por precio**: sin precio configurado la función no se ofrece. Es el mismo criterio, aplicado a la búsqueda web | Literal (criterio) |
| M7b `ContadorAsignaciones` | El contador del ítem del menú (COUNT indexado por request, sin contador si es 0) | Literal |
| Escaneo `docs/*/definiciones/5-implementador.md` del estudio | Ningún otro proyecto del estudio tiene instructivos, búsqueda web del proveedor ni informe de repetición de pedidos. Lo más cercano son ABMs versionados de textos, que ya están cubiertos por M3/M4 dentro de este mismo repo | Sin match |

### Que se hizo, archivo por archivo

**Domain.** `Entities/Instructivos.cs` (nuevo): `Instructivo` (`SoftDestroyable`, `ITenantOwned`) e `InstructivoVersion`.
`Entities/Tareas.cs`: `TareaAgente.PermiteBusquedaWeb`. `Entities/Programaciones.cs`: `EjecucionProgramada.VistoAt` y
`VistoPorId`. `Entities/Uso.cs`: `EventoUso.Busquedas`.

**Application.** `DTOs/InstructivosDtos.cs` (nuevo) con los DTOs, `MensajesInstructivos`, **`TextosConceptos`** (la tabla
canónica de los cuatro conceptos de D-M14-3, que no se reescribe en ninguna pantalla) y **`DeteccionInstructivo`** (la
detección blanda de D-M14-6, en los dos sentidos). `DTOs/UsoOlvidataDtos.cs` (nuevo): dashboard e informe.
`DTOs/ProgramacionesDtos.cs`: bandeja de resultados. `Interfaces/IInstructivoService.cs` e `Interfaces/IUsoOlvidata.cs`
(nuevos). `Settings/InstructivosOptions.cs` y `Settings/BusquedaWebOptions.cs` (nuevos). `Helpers/HashPedido.cs` (nuevo).
`Motor/NombresHerramientasInstructivos.cs` (nuevo). `Motor/ModeloConversacion.cs`: dos bloques nuevos
(`BloqueBusquedaWeb`, `BloqueResultadoBusquedaWeb` con sus `FuenteWeb`), `SolicitudModelo.BusquedaWeb`,
`RespuestaModelo.Busquedas` y `MotivoFin.PausaTurno`. `Motor/IMotorAgentes.cs`: `PasoVisibleDto.Busquedas`,
`BusquedaWebVistaDto`, la casilla en `CrearTareaDto` y la sobrecarga de `EnviarSeguimientoAsync`.

**Infrastructure.** `Services/Instructivos/InstructivoService.cs` y `Services/Instructivos/HerramientasInstructivos.cs`
(nuevos). `Services/Uso/DashboardUso.cs` e `Services/Uso/InformeAutomatizacion.cs` (nuevos).
`Services/Motor/ProveedorModeloAnthropic.cs`: mapeo de la herramienta del proveedor y de sus bloques, en los dos
sentidos, más el conteo de búsquedas de `usage.server_tool_use`. `Services/Motor/ProcesadorTareas.cs`: oferta de las
herramientas de instructivos, decisión de búsqueda web, costo y `pause_turn`. `Services/Motor/ProveedorModeloSimulado.cs`:
dos guiones nuevos. `Services/Motor/ResumenPasos.cs`: instructivos en la cadena y `Busquedas(...)`.
`Services/Motor/ServicioTareas.cs` y `Services/Motor/PreparadorTareaTrabajo.cs`: la marca de búsqueda.
`Services/Programaciones/ProgramacionTareaService.cs`: bandeja de resultados. `Data/Configurations/InstructivosConfigurations.cs`
(nuevo) y la migración `20260917150924_InstructivosM14`.

**Web.** `Controllers/InstructivosController.cs` + `Views/Instructivos/{Index,Form,Detalle,_Desambiguador}.cshtml`,
`Views/Shared/_ConceptosAyuda.cshtml` y `Views/Shared/_AvisoPareceInstructivo.cshtml` (nuevos).
`CarteraController.Espacio` + `Views/Cartera/Espacio.cshtml`. `ProgramacionesController.Resultados` / `MarcarVisto` +
`Views/Programaciones/Resultados.cshtml` + `ContadorResultadosViewComponent`. `UsoController` (cards + `Automatizar`) +
`Views/Uso/Automatizar.cshtml`. Ajustes: `Reglas/_Form.cshtml` (el combo), `Reglas/Detalle.cshtml` e `Index.cshtml` (los
avisos y la bajada), `ReglasController` (detección blanda al guardar), `Agentes/Ejecutar` y `Tareas/_CuadroSeguimiento`
(la casilla), `Tareas/_PasosTurno.cshtml` (las búsquedas con sus fuentes) y `_Layout.cshtml` (Instructivos y Resultados).

### Decisiones de implementacion (ambiguedades resueltas)

- **DI-M14-1 El contenido de las páginas que vuelven de la búsqueda no se puede mostrar.** Verificado contra el SDK: cada
  fuente trae `title`, `url`, `page_age` y **`encrypted_content`**, que es opaco. Se guarda para poder reenviar el turno y
  nunca se muestra. Consecuencia sobre P-M14-06: *"Ver lo que trajo"* despliega **las fuentes citadas**, no el texto de la
  página. Se mantiene el rótulo *"Información de internet: puede estar equivocada o desactualizada"* y el escapado, porque
  el título y la URL también vienen de internet. `FuenteWeb.Extracto` queda para los proveedores que sí devuelven texto
  (hoy, el modelo simulado de QA).
- **DI-M14-2 El `type` de la herramienta se toma del SDK, no de la configuración.** `BusquedaWeb:TipoHerramienta` solo
  puede pedir una versión **conocida**; un valor desconocido se ignora y se usa la del SDK. Nunca se arma un `type` a
  mano: es exactamente el error que RT-M14-01 manda evitar.
- **DI-M14-3 La búsqueda no lleva una segunda compuerta de gasto.** El motor ya verifica el límite antes de **cada**
  llamada (RF-M6-08): con el límite alcanzado no llama al modelo y por lo tanto no hay búsqueda. Agregar otra compuerta
  sería una segunda verdad sobre lo mismo.
- **DI-M14-4 El costo de la búsqueda se suma al `PasoTarea`, no solo al `EventoUso`.** El control de gasto de M6 suma
  `PasoTarea.CostoUsd`; poner el costo solo en el evento lo habría dejado fuera del límite. Un solo número, en los dos
  lados.
- **DI-M14-5 Solo se cuentan búsquedas si esa llamada las ofrecía.** Si la tarea no tenía la casilla, un proveedor que
  informe búsquedas no puede inventar costo.
- **DI-M14-6 El tipo `Procedimiento` sigue visible en el combo de una regla que ya lo tiene.** Sacarlo del todo le
  cambiaría el tipo en silencio al editarla. En un alta no aparece nunca, y hay test que lo verifica.
- **DI-M14-7 La detección blanda de la regla aparece DESPUÉS de guardar.** La regla queda guardada y el aviso ofrece
  convertirla; *"Dejarlo como regla"* es cerrar el aviso. Así se cumple *"nunca bloquea"* al pie de la letra.
- **DI-M14-8 El espacio del cliente no tiene ni un `<form>`.** Es la forma más barata de garantizar "no se escribe nada
  desde acá", y el test lo verifica sobre la vista.
- **DI-M14-9 `pause_turn` se maneja en el bucle del motor.** Es el único estado nuevo que puede devolver el proveedor
  cuando corre su propia herramienta: se reenvía la conversación y sigue donde quedó, acotado por el máximo de pasos del
  turno como cualquier otra vuelta.

### Evidencia

`dotnet build OlvidataAgentes.slnx` 0 errores / 2 advertencias preexistentes. `dotnet test` **569/569** (509 de línea base
+ 60 nuevos: `InstructivosTests`, `BusquedaWebTests`, `M14GoldenYPantallasTests`). **Los 4 goldens de hash de contexto,
intactos**, con instructivos cargados y con la búsqueda encendida; el test nuevo además compara el prompt de sistema byte
a byte entre la tarea con y sin las herramientas. Migración aplicada a `olvidata_agentes_dev`: `TituloVigente` verificada
como `STORED GENERATED` y el índice único `(TenantId, TituloVigente)` creado. Organizaciones 1, 4, 18, 19 y 20 intactas
(154 tareas con `PermiteBusquedaWeb = 0`, 493 eventos con `Busquedas = 0`). Recorrido en el navegador con el modelo
simulado: instructivos, desambiguador, formulario, resultados, espacio del cliente (org 19), dashboard (493 llamadas,
que es exactamente el conteo de filas de `EventoUso`), informe de automatización y una tarea con búsqueda de punta a
punta — 1 búsqueda, USD 0,01 en el paso y en el evento, fuentes enlazables con `rel="noopener noreferrer nofollow"`.
La tarea de humo se borró para dejar la demo del tenant 19 como estaba.

### Lo que queda pendiente

- **Verificar el precio por búsqueda de Anthropic** antes de facturar. Mientras `BusquedaWeb:PrecioPorBusquedaUsd` sea
  `null`, la función queda apagada en producción (fail-closed). En Development hay un precio de prueba de USD 0,01.
- **El camino del proveedor real nunca se ejecutó** (decisión de costo, PA-18/PA-02): lo verificado es el del modelo
  simulado, que reproduce los mismos bloques.
- **D-M14-8 (el configurador propone instructivos) quedó fuera de esta entrega**: requiere tocar el prompt del
  configurador de M4b, que sigue sin publicar (PA-13), y conviene hacerlo antes de publicarlo, no después.
- **Deuda anotada**: el "visto" de los resultados es del registro y no por persona.
# M12 — Tareas programadas y autonomía gradual por rol

Estado: **implementada 2026-09-16, pendiente de QA (etapa 6)**. **Última etapa del roadmap.** Entrada: `1-analista-funcional.md` M12
(RF-M12-01..17, CA-M12-01..16), `2-disenador-funcional.md` M12 (D-M12-1..12, P-M12-01..03) y `3-arquitecto-mvc.md` M12
(RT-M12-01..11), aprobados sin gate por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto
personal). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. Una entrega, una migración: `ProgramacionesM12`.
**Ninguna llamada a la API real de Anthropic, ninguna salida a internet, sin commits.** Mcp y Cli sin tocar (solo compilan).

### Escaneo de reutilizacion M12
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M7a `IPreparadorTareaTrabajo` | **La pieza clave.** "Armar una tarea de trabajo sin guardarla", con límite de gasto (M6), suscripción, agente, cliente, adjuntos e instantánea de reglas ya adentro. Una vuelta programada **no duplica ni una línea** de crear una tarea | Literal (reuso de código, no copia) |
| Template M6 `AvisoGasto` (PAT-035) | "Esto se hace una sola vez aunque varios lo intenten": insertar y tratar el `DbUpdateException` (1062) como "otro llegó antes". De ahí sale la reserva de la ocurrencia | Literal (patrón) |
| Template M1 lease del motor | La idea de reservar trabajo con un `UPDATE` condicionado por token de concurrencia. M12 la combina con el índice único porque la reserva y el trabajo van en **guardados distintos** | Adaptado |
| Template M4b `IResolvedorSesion.ResolverUsuarioAsync` | Correr en segundo plano con los permisos de una persona, sin sesión ni caché | Literal |
| Template M6/M7a/M8/M9 barridos de `MotorAgentesWorker` | El quinto barrido con su ritmo y su interruptor; la estructura del `try/catch` que no rompe el ciclo | Literal |
| Template M7b `TareaAsignadaService` + `AsignacionesController` + vistas | La forma completa de un ABM con DataTables server-side, filtros en sesión, búsqueda global sobre las columnas visibles, acciones AJAX con SweetAlert2 y token de concurrencia con mensaje de conflicto | Literal (adaptado) |
| Template M7b `ConversorDia.Dia` | `DateOnly` → columna `date` en MySQL (sin el conversor, proyectar a `DateOnly` revienta con InvalidCastException) | Literal |
| Template M11 DI-M11-6 | "El costo se calcula, nunca se guarda": nada de escribir columnas de otra entidad dentro del commit del motor | Práctica |
| Escaneo `docs/patrones/catalogo.yml` (PAT-001..044) | Ningún patrón cubría "trabajo repetitivo reanudable". Lo más cercano, PAT-034/035, son de aprobación y gasto | Sin match |
| Escaneo `docs/*/definiciones/5-implementador.md` del estudio | Ningún proyecto tiene tareas programadas. Lo más cercano son los vencimientos/recordatorios de CRM, que son **avisos** calculados al mirar la pantalla, no trabajo que corre solo | Práctica, no código |
| PAT-045 | **Creado** en el catálogo | Nuevo |

### Qué se hizo

1. **Programación = receta, no tarea (RF-M12-01/06).** `ProgramacionTarea` (`ITenantOwned` + `SoftDestroyable`) guarda qué se
   pide, a qué agente, cada cuánto y quién responde. `EjecucionProgramada` guarda cada vuelta. La tarea que sale es una
   `TareaAgente` **común y corriente**: mismos pasos, mismo costo, misma conversación de M3b. Por eso los 4 goldens de hash
   quedan intactos: una vuelta usa el mismo `IPreparadorTareaTrabajo` que el botón del portal.
2. **La ocurrencia se reserva antes de trabajar (RT-M12-01, PAT-045).** `ReservarAsync` escribe la vuelta y adelanta
   `ProximaEjecucionAt` **en un guardado**, con índice único `(ProgramacionTareaId, Ocurrencia)` y `VersionToken`. Recién
   después `EjecutarUnaAsync` crea la tarea. Si el proceso muere en el medio, la vuelta queda `Reservada` y el barrido la
   termina sin reservar de nuevo.
3. **Nunca se disparan las vueltas perdidas (RT-M12-02).** La próxima se recalcula **desde ahora**. Un sitio dormido una
   semana crea una tarea al despertar, no siete. Verificado con un test que corre tres barridos seguidos.
4. **Calendario en hora argentina (RT-M12-03).** `CalendarioProgramacion`: diaria, semanal (1 = lunes … 7 = domingo) y
   mensual con **recorte del día 31 al último día del mes**. Siempre estrictamente después del instante que recibe. Helper
   puro: 8 tests lo ejercitan sin base.
5. **Autonomía por rol resuelta en el motor (RT-M12-07).** En `ProcesadorTareas`, una tarea con `ProgramacionTareaId` y
   `AutonomiaConAprobacion = false` **pierde todas las herramientas con `RequiereAprobacion`** antes de armar la solicitud.
   El agente no puede pedir lo que no tiene. Con la autonomía encendida las recibe y el circuito de M6 funciona igual:
   la acción queda esperando y **nunca se aprueba sola**.
6. **La vuelta corre como el responsable (RT-M12-06).** `ResolverUsuarioAsync` puebla tenant y contexto; si dejó la empresa,
   la vuelta queda Bloqueada con "El responsable ya no es un miembro activo de la empresa."
7. **Fallas seguidas con corte y aviso (RF-M12-09).** Una vuelta que no pudo nunca mata la programación: suma una falla y
   recién a las 5 queda Terminada con motivo, y el responsable recibe dos avisos (el de la vuelta y el del corte).
8. **Costo calculado (RT-M12-09).** Del mes y total, sumando `PasosTarea.CostoUsd` de las tareas de esa programación, con el
   período argentino de M6. Aviso una vez por mes cuando **una sola** programación pasa el 50 % del tope de la empresa.
9. **Origen en Tareas (RF-M12-10).** Chip "Programada · «Nombre»" en la grilla, aviso en el detalle, filtro "Origen" y el
   enlace "Ver sus tareas" del detalle que fija la programación.
10. **Pantallas (RF-M12-16) y consola (RF-M12-17).** `Programaciones/{Index, Form, Detalle, _ScriptAcciones}`, ítem en el
    menú de todo miembro, y el verbo `programaciones <tenantSlug>` en Admin.

### Decisiones de implementacion M12 (ambigüedades resueltas)
- **DI-M12-1 Dos fases con estado `Reservada`, no una transacción larga.** La alternativa era abarcar reserva y creación en
  una transacción. Se descartó: con EF InMemory los tests no la tienen, y en MySQL sostenerla mientras se arma el contexto y
  se calcula el hash deja la fila tomada varios segundos. Costo: un estado más y un barrido de recuperación. Hipótesis
  tomada sin gate (autorización 2026-09-14).
- **DI-M12-2 Las vueltas perdidas se pierden.** Al despertar se dispara **solo la última pendiente**, y ni siquiera esa: se
  recalcula desde ahora. Lo pidió el alcance y además es lo correcto —una tarea de IA vieja cuesta plata y casi nunca sirve—.
  Contra: nadie puede "recuperar" el resumen del lunes que no corrió. Queda dicho en el formulario.
- **DI-M12-3 Día 31 en un mes corto → último día del mes.** La otra opción era saltear el mes. Se descartó: "el 31 de cada
  mes" para una persona significa "a fin de mes", y saltear febrero es un silencio que nadie espera.
- **DI-M12-4 La hora se guarda como minutos desde la medianoche argentina (int), no como `TimeOnly`.** Después de que el
  proveedor MySQL obligara a un conversor para `DateOnly` en M7b, un `int` no tiene sorpresas de mapeo, se indexa y se
  compara. El significado está en el nombre de la columna y en su comentario.
- **DI-M12-5 Sin autonomía se QUITA la herramienta, no se auto-aprueba ni se deja pendiente.** Era la decisión central. Se
  descartó auto-aprobar (rompe la promesa de M6) y se descartó dejar el pedido pendiente en silencio (la vuelta queda
  esperando a alguien que no sabe que la esperan, y a la mañana siguiente hay una tarea trabada por cada día). Quitarla es
  fail-closed de verdad: **no hay ninguna rama nueva en el circuito de aprobaciones que pueda tener un agujero**. Efecto
  colateral asumido: sin autonomía, una tarea programada tampoco recibe las herramientas de conectores de M11 (todas tienen
  `RequiereAprobacion = true` por fail-closed) ni las de demostración.
- **DI-M12-6 La autonomía se congela en la tarea (`AutonomiaConAprobacion`).** Si se leyera de la programación al ejecutar,
  editarla a mitad de vuelta cambiaría lo que esa vuelta puede hacer.
- **DI-M12-7 "Ejecutar ahora" solo adelanta la hora; no crea la tarea.** Así el camino de creación es **uno solo** y lo que
  QA prueba a mano es exactamente lo que va a pasar sola de madrugada. Costo: hay que esperar el barrido (hasta un minuto),
  y la confirmación lo dice.
- **DI-M12-8 Sin vista de staff de Olvidata.** M11 sí la tuvo. Acá se dejó afuera para no agrandar la entrega: el verbo de
  consola cubre la necesidad de mirar. **Deuda consciente**, no olvido.
- **DI-M12-9 Una sola pantalla, sin pestañas (D-M12-1).** El Director ve todas con la columna "Responsable" y su filtro; el
  Empleado ve las suyas sin esa columna. Menos superficie que las pestañas de M7b, misma información.
- **DI-M12-10 Sin columnas generadas en la migración.** La unicidad que importa es sobre columnas reales, así que no hizo
  falta el ajuste manual a `STORED` de M2/M4/M11. Es la primera migración del proyecto con un único índice único y sin SQL a
  mano.
- **DI-M12-11 `VersionToken` se incrementa solo en la reserva, nunca al cerrar la vuelta** (RT-M12-11). Si el cierre lo
  tocara, una edición desde la pantalla a mitad de vuelta la haría fallar sin motivo real. El cierre igual va condicionado
  por el token: si alguien editó, la vuelta queda `Reservada` y la retoma el barrido.

### Migraciones EF generadas M12
- `20260916150321_ProgramacionesM12` — `CreateTable ProgramacionesTarea` (`Id int` identity, `TenantId int`,
  `Nombre varchar(150)`, `AgenteArtefactoId int?`, `AgenteOrganizacionId int?`, `ClienteCarteraId int?`, `Pedido text`,
  `Frecuencia/Estado int`, `DiaSemana/DiaMes int?`, `MinutosDelDia int`, `ResponsableUsuarioId varchar(255)`,
  `MotivoFin varchar(500)`, `FinEl date`, `MaxEjecuciones int?`, `EjecucionesHechas/FallasSeguidas int`,
  `PuedeAccionesConAprobacion tinyint(1)`, `ProximaEjecucionAt/UltimaOcurrenciaAt datetime(6)?`,
  `PeriodoAvisoCosto int?`, `VersionToken int` + auditoría y baja lógica) y `CreateTable EjecucionesProgramadas`
  (`Id bigint` identity, `TenantId`, `ProgramacionTareaId`, `Ocurrencia datetime(6)`, `Resultado int`,
  `TareaAgenteId int?`, `Motivo varchar(500)`, `CreadoAt`, `ResueltaAt?`). Más **dos columnas en `TareasAgente`**:
  `ProgramacionTareaId int?` y `AutonomiaConAprobacion tinyint(1) DEFAULT 0`. FK **Restrict** a `Tenants`, `Artefactos`,
  `AgentesOrganizacion`, `ClientesCartera`, `AspNetUsers`, `ProgramacionesTarea` y `TareasAgente`. `Down` = `DropTable` de
  las dos + `DropColumn` de las dos. **Ninguna tabla existente cambia de forma.**
- **Sin ajuste manual a STORED**: no hay columnas generadas (DI-M12-10). Es la diferencia con `OrganizacionM2`,
  `AgentesOrganizacionM4` y `ConectoresM11`.
- **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-16**, con `database update ConectoresM11` (Down OK) y
  `database update` otra vez; `has-pending-model-changes` limpio.
- Verificado por SQL (`scratchpad/verificar-m12*.sql`, transacciones revertidas): tipos y largos exactos;
  **1062 real** al insertar dos veces la misma `(ProgramacionTareaId, Ocurrencia)` — *"Duplicate entry
  '1-2026-09-17 11:00:00.000000'"*; **distinta ocurrencia de la misma programación entra** y **la misma hora en otra
  programación también** (el único es por programación, no global); **1451 real** al borrar una programación con historial y
  **1452** al registrar una vuelta de una programación inexistente; `EXPLAIN` del barrido del worker resuelve por
  `IX_ProgramacionesTarea_Estado_ProximaEjecucionAt` (`range`, `Using index`, nunca `ALL`) y el de las vueltas colgadas por
  `IX_EjecucionesProgramadas_Resultado_CreadoAt` (`range`, `Using index`); collation `utf8mb4_0900_ai_ci` en `Nombre` y
  `Pedido`. **0 restos** tras los ROLLBACK.

### Archivos y capas modificadas M12
**Domain** — Nuevos: `Entities/Programaciones.cs` (`ProgramacionTarea`, `EjecucionProgramada`),
`Enums/EnumsProgramaciones.cs` (`FrecuenciaProgramacion`, `EstadoProgramacion`, `ResultadoEjecucionProgramada`).
Modificado: `Entities/Tareas.cs` (`ProgramacionTareaId`, `AutonomiaConAprobacion`).

**Application** — Nuevos: `Helpers/CalendarioProgramacion.cs`, `Settings/ProgramacionesOptions.cs`,
`DTOs/ProgramacionesDtos.cs` (+ `MensajesProgramaciones`), `Interfaces/IProgramaciones.cs`
(`IProgramacionTareaService`, `IEjecutorProgramaciones`). Modificados: `Interfaces/IPermisosOrganizacion.cs` (2 permisos),
`Motor/IMotorAgentes.cs` (`FiltroTareas.Origen*`, `TareaFiltros.DeProgramacion`/`ProgramacionId`,
`TareaListItemDto.Programacion*`, `TareaDetalleDto.Programacion`).

**Infrastructure** — Nuevos: `Services/Programaciones/EjecutorProgramaciones.cs`, `ProgramacionTareaService.cs`,
`Data/Configurations/ProgramacionesConfigurations.cs`, migración `Data/Migrations/20260916150321_ProgramacionesM12.cs`
(+ Designer y snapshot). Modificados: `Services/Motor/ProcesadorTareas.cs` (quita las herramientas con aprobación en una
tarea programada + aviso de fin en `TrasFinAsync`), `Services/Motor/MotorAgentesWorker.cs` (quinto barrido),
`Services/Motor/ServicioTareas.cs` (filtro de origen, nombre de la programación en la grilla y chip del detalle),
`Services/Organizacion/PermisosOrganizacion.cs`, `Data/AppDbContext.cs` (2 DbSet + exclusión del audit trail),
`Data/Configurations/AgentesConfigurations.cs` (FK e índice de la tarea), `DependencyInjection.cs`.

**Web** — Nuevos: `Controllers/ProgramacionesController.cs`, `Models/ProgramacionesViewModels.cs`, vistas
`Programaciones/{Index, Form, Detalle, _ScriptAcciones}.cshtml`. Modificados: `Controllers/TareasController.cs`
(filtro de origen + `?programacion=`), `Views/Tareas/Index.cshtml` (filtro y chip), `Views/Tareas/_Conversacion.cshtml`
(aviso de origen), `Views/Shared/_Layout.cshtml` (ítem "Programaciones"), `wwwroot/css/site.css` (`.ov-prog-estado`,
`.ov-prog-vuelta`), `appsettings.json` (sección `Programaciones`).

**Admin** — `Program.cs`: verbo `programaciones <tenantSlug>` y ayuda.
**Tests**: nuevo `ProgramacionesTests.cs` (38 con sus casos de Theory).
**Repo**: `docs/diseno-organizacion-roles-reglas.md` (M12 ✅) y `PLAN-IMPLEMENTACION.md`.

### Evidencia de build y tests M12
- `dotnet build OlvidataAgentes.slnx`: **0 errores**. 2 advertencias **preexistentes** que aparecen solo en compilación
  completa y no son de M12 (`xUnit2013` en `ReglasPropuestasAgentesTests` y `CS0114` en `HomeController.StatusCode`).
  Las vistas Razor compilan en el build: `dotnet build` del proyecto Web da 0 advertencias.
- `dotnet test tests/OlvidataAgentes.Tests`: **430 OK / 0 fallidos** (392 previos + 38 nuevos).
- **Inestabilidad preexistente detectada, ajena a M12**: en una de las corridas falló
  `LectorDocumentosTests.Extraccion_que_supera_el_tiempo_queda_como_no_se_pudo_leer`, que mide un tiempo de espera real.
  Vuelto a correr solo y con la suite completa, pasa. Es un test sensible a la carga de la máquina, no una regresión:
  conviene reescribirlo sin depender del reloj cuando se lo toque.
- **Los 4 goldens de hash de contexto intactos**: una tarea programada usa el mismo `IPreparadorTareaTrabajo`, así que el
  prompt de sistema y su hash son los mismos que los de una tarea pedida a mano. Verificado además con un test propio: dos
  vueltas de la misma programación con una regla nueva en el medio dan **hashes distintos** (toma las reglas vigentes).
- **Casos de no duplicación cubiertos** (todos verdes): dos workers globales barriendo a la vez → una sola vuelta y el
  segundo se va con las manos vacías; reinicio entre reservar y crear la tarea → la vuelta queda `Reservada`, la
  programación ya apuntaba al futuro, y el barrido posterior la termina sin duplicar; despertar tras 7 días dormido con
  tres barridos seguidos → **una** tarea y la próxima recalculada dentro de las 24 h.
- **Casos de freno cubiertos**: límite de gasto del mes alcanzado, responsable bloqueado, organización suspendida, 5 fallas
  seguidas → Terminada con motivo y aviso, y tope de ejecuciones → termina sola sin una vuelta de más.
- **Autonomía cubierta**: sin autonomía, `pago_real` y `sin_nivel` **no están** en la lista de herramientas de la solicitud
  al modelo y `nota_libre` sí, y la tarea completa; con autonomía, `pago_real` **sí** se ofrece, queda un `AprobacionAccion`
  Pendiente, la tarea queda `EsperandoAprobacion` y **no hay ninguna `EjecucionHerramienta`** (la acción no se ejecutó).
- **Permisos cubiertos**: un Empleado programa para sí mismo pero no para otro (`SinPermiso`) ni con autonomía; ve solo las
  suyas y una ajena le da `NoEncontrado`; una Directora de otra empresa no ve ni una.
- Lecciones: (1) el orden importa — si la marca de "ya corrí" se escribe **junto** con el trabajo, un corte en el medio
  habilita la doble ejecución; hay que reservar primero y trabajar después; (2) el índice único solo no alcanza si la misma
  instancia reintenta: hace falta el estado intermedio con su barrido de recuperación, o la ocurrencia queda huérfana para
  siempre; (3) una subconsulta con `IgnoreQueryFilters` **dentro de una proyección** no compila (CS9175: un árbol de
  expresión no admite expresiones de colección) — los nombres se resuelven después de la página, como los clientes desde M5;
  (4) la decisión de seguridad más simple fue la mejor: **quitar la herramienta** en vez de agregar una rama al circuito de
  aprobaciones. Menos código nuevo en el camino crítico = menos lugares donde equivocarse.

### Riesgos residuales M12
- **Sin AlwaysRunning (PA-07) las programaciones se atrasan.** SmarterASP duerme el sitio; el worker no corre dormido. Hoy
  solo está el plan B de M9 (ping externo a `/health/vivo`). Una programación de las 08:00 puede correr a las 09:15 si nadie
  entró antes. **Es el riesgo principal de M12 y no lo resuelve el código.** Mitigado a medias: el atraso nunca se convierte
  en avalancha (se dispara una sola vuelta) y el formulario lo dice con esas palabras.
- **Las vueltas perdidas se pierden** (DI-M12-2). Nadie puede recuperar el resumen del lunes que no corrió: hay que usar
  "Ejecutar ahora".
- **La ocurrencia se consume aunque la tarea no se cree.** Evita el bucle infinito de una programación rota, pero significa
  que un problema de un día se lleva la vuelta de ese día.
- **Sin autonomía, una tarea programada tampoco tiene conectores (M11)**, porque todas sus herramientas son fail-closed.
  Es correcto y es lo conservador, pero no es obvio: está dicho en el detalle de la programación.
- **Sin vista de staff** (DI-M12-8) y **sin frecuencias finas** (cada N minutos, días hábiles, "el primer lunes"): deuda
  consciente. Lo primero se cubre con el verbo de consola.
- **El aviso de costo depende de que la empresa tenga tope.** Con `ModoApiKey.PropiaDelCliente` o sin límite no hay contra
  qué comparar y no se avisa; el costo igual se muestra en la pantalla.
- **No se probó con volumen**: el barrido trae hasta 5 vueltas por ciclo y las resuelve en serie dentro del mismo scope. Con
  muchas organizaciones programando a las 08:00 en punto, la cola se va a estirar. Hay que mirarlo cuando haya clientes.
- Verificación visual pendiente (QA): listado, alta con las tres frecuencias, edición, detalle con historial, pausar,
  reanudar, ejecutar ahora, dar de baja, chip y filtro de origen en Tareas, mobile 390 y ambos temas.

### Proximos pasos pendientes M12
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M12).
- **Cerrar PA-07 con soporte de SmarterASP**: es lo que convierte a M12 de "se atrasa" a "corre a la hora".
- Evaluar frecuencias finas y días hábiles si un cliente real las pide (hoy no hay caso).
- Evaluar la vista de staff de programaciones y, con volumen, pasar el barrido a resolver vueltas en paralelo.
- Deuda preexistente vista, fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9.

---
# M11 — Conectores con credenciales por organización

Estado: **implementada 2026-09-16, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M11 (RF-M11-01..17,
CA-M11-01..16), `2-disenador-funcional.md` M11 (D-M11-1..12, P-M11-01..04) y `3-arquitecto-mvc.md` M11 (RT-M11-01..11),
aprobados sin gate por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal).
Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. Una entrega, una migración: `ConectoresM11`. Alcance elegido por
Joaquín: **el mecanismo + un conector HTTP genérico de ejemplo**; los conectores concretos quedan para cuando los
defina. **Ningún sistema externo real configurado, ninguna credencial real usada, ninguna salida a internet, ninguna
llamada a Anthropic, sin commits.** Mcp y Cli sin tocar (solo compilan).

### Escaneo de reutilizacion M11
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M1 `Tenant.ApiKeyProtegida` + `ProcesadorTareas.PropositoApiKeyTenant` | Data Protection con propósito propio, descifrado solo al ejecutar y propiedad excluida del audit trail. `PropositoSecretos = "OlvidataAgentes.Conexion.Secretos"` | Literal (mismo mecanismo, otro propósito) |
| Template M6 (PAT-034) `IHerramientaConAprobacion` | Nivel, `DescribirAsync` armada con la entrada, pedido por `tool_use_id`, vencimiento y barrido. **M11 es su primer caso real**: hasta hoy solo lo usaban las acciones de demostración | Literal (extensión: **PAT-044**, la decisión pasa a ser por llamada) |
| Template M5/M6/M10 en `ProcesadorTareas` | "Herramientas en la lista de la solicitud, sin tocar el prompt" + golden de hash | Literal (patrón del repo) |
| Template M2 `AreaConfiguration` / migración `OrganizacionM2` | Unicidad entre vigentes (columna generada + índice único) **y el ajuste manual a STORED** | Literal |
| Template M10 `HerramientasConocimiento.Resumir` / M7a `ResumenHerramientasPlataforma.Pedido` | Rótulos llanos de "Ver pasos", encadenados en `ServicioTareas` | Literal (extensión) |
| Template M4b `HerramientasConfigurador.Texto/Entero` y M5 `HerramientasDocumentos.Json` | **Se llaman, no se copiaron**: mismo assembly y ya probados | Literal (reuso de código) |
| Escaneo `docs/*/definiciones/5-implementador.md` del estudio | Ningún proyecto tiene "conectores con credenciales por organización". Lo más cercano es ARCA/AFIP (instrucción `34`), que es **un** sistema con su protocolo, no un mecanismo genérico: de ahí salieron "credenciales del cliente, nunca del estudio" y "toda llamada externa queda registrada" | Práctica, no código |
| PAT-043 y PAT-044 | **Creados** en el catálogo | Nuevos |

### Qué se hizo

1. **Conector = código, conexión = dato de la organización (RF-M11-01/02, DI-M11-1).** `IConectorTipo` declara código,
   nombre, campos de configuración, validación, herramienta, esquema, "¿es solo lectura?", descripción para la
   aprobación y ejecución. `ConexionConector` (`ITenantOwned` + `SoftDestroyable`) guarda lo que carga el Director.
   Un conector nuevo (Gmail, ARCA) es una implementación más + su registro en DI: no toca el motor, ni las
   aprobaciones, ni las pantallas.
2. **Credenciales cifradas que no vuelven a salir (RF-M11-03).** JSON nombre → valor protegido con Data Protection
   (propósito propio); se guardan además los **nombres** y la fecha. `SecretosProtegidos` está excluida del audit trail
   y no hay ningún camino en el código que devuelva el valor: ni el listado, ni el detalle, ni el backoffice, ni la
   consola. Editar sin escribir nada las conserva; escribir las reemplaza enteras; "borrar" las saca; la baja lógica
   también las borra.
3. **Herramientas (RF-M11-06/07).** `conexiones_listar` (solo lectura, sin aprobación) y una `HerramientaConector` por
   tipo — hoy `http_llamar`. Guardas: solo tareas de trabajo; conexión resuelta por `(tenant de la tarea, código,
   activa, alcance)`; rol del autor re-verificado con `IResolvedorSesion` en cada llamada. "No existe", "está
   inactiva", "es de otra empresa" y "no la podés usar" responden lo mismo.
4. **Aprobación por llamada (RF-M11-09, PAT-044).** `IHerramientaAprobacionPorLlamada` con
   `RequiereAprobacionAsync`; `RequiereAprobacion` sigue en **true** (fail-closed). `ProcesadorTareas` lo resuelve en
   `NecesitaAprobacionAsync`, usado en los **tres** lugares donde antes se leía la propiedad (el recorrido, la rama que
   pide aprobaciones y `SolicitarAprobacionesAsync`). Nivel **Director** siempre.
5. **Conector HTTP genérico (RF-M11-10..14).** Dirección base, métodos habilitados, encabezados fijos, encabezados con
   credenciales, tiempo máximo y KB máximos. El agente manda una **ruta relativa**, nunca una URL libre; el resultado
   se resuelve contra la base y **se valida igual** contra la lista blanca (así `//evil.com/x` no pasa).
6. **Protección contra SSRF (RF-M11-11/12, RT-M11-06).** `GuardiaDestinoHttp`: solo https, sin usuario y contraseña en
   la URL, host en la lista blanca de la conexión (con `*.dominio` y `dominio:puerto`), y ninguna dirección interna.
   La revisión de IP se repite **al conectar**, en el `ConnectCallback` del handler, que después conecta a esas mismas
   direcciones (cierra el DNS rebinding). `AllowAutoRedirect = false` y cada redirección revalidada.
7. **Registro y topes (RF-M11-13/15).** `LlamadaConector` inmutable: quién, cuándo, herramienta, método, **destino sin
   querystring**, resultado, código, ms, bytes y si pasó por aprobación. Tope de llamadas por tarea y por conexión (las
   bloqueadas no cuentan: no llegaron a salir).
8. **"Ver pasos" en palabras (D-M11-7).** `HerramientasConectores.Pedido`/`Resumir`, encadenados en
   `ServicioTareas` después de documentos y conocimiento, y en `ResumenHerramientasPlataforma.Pedido`.
9. **Pantallas (RF-M11-16).** Director: `Conexiones/Index` (tarjetas), `Conexiones/Form` (**dibujado solo a partir de
   los campos del tipo**) y `Conexiones/Uso` (últimas 100 llamadas). Staff: `Clientes/Conexiones` en solo lectura y sin
   secretos, con su botón en la ficha de la organización. Ítem "Conexiones" en el menú del Director.
10. **Simulador y consola (RF-M11-17).** `GuionConectores` (marcador "conexi"/"conector"/"sistema externo" + nombre
    exacto de la herramienta) y el verbo `conexiones <tenantSlug>` en Admin, que nunca muestra una credencial.

### Decisiones de implementacion M11 (ambigüedades resueltas)
- **DI-M11-1 El conector es código, no un dato importable.** La otra opción era declararlo en un manifiesto como los
  rubros. Se descartó: ejecutar una llamada externa es código, y un conector definido en un YAML sería un agujero de
  seguridad editable desde afuera del repositorio. Costo: un conector nuevo pide un deploy. Hipótesis tomada sin gate
  (autorización 2026-09-14).
- **DI-M11-2 Aprobación por llamada, nivel fijo.** Se extendió el motor para que la **necesidad** de aprobación se
  decida por llamada, pero el **nivel** quedó estático en `Director`. Hacerlo variable era otra superficie más en
  `SolicitarAprobacionesAsync` a cambio de poco: lo que el Director necesita —dejar pasar las consultas— ya se resuelve
  por conexión. Hipótesis tomada sin gate.
- **DI-M11-3 `LecturaSinAprobacion = false` por defecto.** Lo más conservador: hasta que el Director lo habilite, toda
  llamada pasa por aprobación. La contra es que una organización que no lo toca va a aprobar mucho; está dicho en la
  pantalla con "(lo recomendado para empezar)".
- **DI-M11-4 Alcance con dos valores, no tres.** `TodaLaOrganizacion` / `SoloDirectores`. Se evaluó agregar "un área"
  (M2 ya tiene áreas) y se dejó afuera: una condición más en la consulta y otra decisión en la pantalla, sin un caso
  que lo pida todavía. Queda como deuda consciente.
- **DI-M11-5 El agente manda una ruta relativa, no una URL.** Dejar que el modelo arme la URL entera hacía que la lista
  blanca fuera la única defensa. Con ruta relativa contra la dirección base de la conexión, más la validación del
  resultado, hacen falta dos fallas para salirse. Verificado con `//evil.com/x` y con una URL absoluta: las dos se frenan.
- **DI-M11-6 El "último uso" se calcula, no se guarda (RT-M11-02).** La primera versión escribía `UltimoUsoAt` en la
  conexión dentro del commit de la tarea. Eso arrastra el `VersionToken` de la conexión al guardado del motor: un
  Director editándola a mitad de una tarea la haría fallar por conflicto de concurrencia sin motivo real (y con EF
  InMemory, un `Attach` parcial habría pisado el resto de la fila). Se quitó la columna; el listado saca el último uso
  y el uso de 30 días con un `GROUP BY` sobre el historial.
- **DI-M11-7 El formulario se dibuja a partir de los campos del tipo.** Un `switch` sobre `TipoCampoConector` en la
  vista, con los valores en `Valores[clave]`. Costo: un poco menos de control fino por campo. Beneficio: el segundo
  conector no pide una vista nueva.
- **DI-M11-8 `PermitirDestinosPrivados` con corte de arranque.** Es la única forma de probar el conector contra un
  servidor local sin salir a internet. Para que no termine encendido en producción, `ValidacionArranque` corta el
  arranque fuera de Development, igual que `Licencias:GenerarClaveSiFalta`, y hay test que lo verifica por el lado del
  guardia (con la opción apagada, ni el servidor local es alcanzable).
- **DI-M11-9 Listado en tarjetas y no en DataTables.** Son pocas conexiones y cada una muestra bastante. Misma
  convención que Reglas y Material de Olvidata. El historial es una tabla plana con las últimas 100, como Consumo.

### Migraciones EF generadas M11
- `20260916141804_ConectoresM11` — `CreateTable ConexionesConector` (`Id int` identity, `TenantId int`,
  `TipoConector varchar(40)`, `Nombre varchar(100)`, `Codigo varchar(40)`, `ParaQueSirve varchar(500)`,
  `Activa/LecturaSinAprobacion tinyint(1)`, `Alcance int`, `ConfiguracionJson text`, `SecretosProtegidos text`,
  `SecretosNombres varchar(500)`, `SecretosActualizadosAt datetime(6)`, `MaxLlamadasPorTarea int`,
  `UltimaPrueba*`, `VersionToken int` + auditoría y baja lógica) y `CreateTable LlamadasConector` (`Id bigint`
  identity, `TenantId`, `ConexionConectorId`, `TareaAgenteId int?`, `UsuarioId varchar(450)`,
  `Herramienta varchar(60)`, `Metodo varchar(10)`, `Destino varchar(500)`, `Resultado int`, `CodigoHttp int?`,
  `Milisegundos`, `BytesRespuesta`, `Mensaje varchar(500)`, `ConAprobacion`, `CreadoAt`). FK **Restrict** a `Tenants`,
  `ConexionesConector` y `TareasAgente`. `Down` = `DropTable` de las dos. **Ninguna tabla existente se modifica.**
- **Ajuste manual (lección de M2/M4, confirmada de nuevo):** el proveedor MySQL **ignora `stored: true`** y creaba
  `CodigoVigente` y `NombreVigente` como **VIRTUAL**. Se sacaron del `CreateTable` y se agregan con
  `migrationBuilder.Sql(... STORED NULL)` antes de sus índices únicos, como en `OrganizacionM2` y `AgentesOrganizacionM4`.
  Verificado en la base: `STORED GENERATED` en las dos.
- **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-16**, con `database update ConocimientoRubroM10` (Down OK,
  las dos tablas desaparecen) y `database update` otra vez; `has-pending-model-changes` limpio.
- Verificado por SQL (`scratchpad/verificar-m11.sql` y `verificar-m11b.sql`, transacción revertida): tipos y largos
  exactos; **1062 real** en `(TenantId, CodigoVigente)` y en `(TenantId, NombreVigente)`; el **mismo código en otra
  organización entra**; con `DeletedAt` puesto las dos columnas generadas pasan a NULL y **el código se puede reusar**;
  **1451 real** al borrar una conexión con historial y **1452** al registrar una llamada de una conexión inexistente;
  `EXPLAIN` del conteo del tope por tarea y de la búsqueda por código resuelven por índice (`ref`, nunca `ALL`);
  collation `utf8mb4_0900_ai_ci` → la unicidad del código es **insensible a mayúsculas y tildes** (`CRM-Prueba` choca
  con `crm-prueba`), que es lo que se busca porque el código se normaliza a minúsculas al guardarlo. **0 restos** tras
  el ROLLBACK.

### Archivos y capas modificadas M11
**Domain** — Nuevos: `Entities/Conectores.cs` (`ConexionConector`, `LlamadaConector`), `Enums/EnumsConectores.cs`
(`AlcanceConexion`, `ResultadoLlamadaConector`).

**Application** — Nuevos: `Settings/ConectoresOptions.cs`, `Motor/NombresHerramientasConectores.cs`,
`DTOs/ConectoresDtos.cs` (+ `MensajesConectores`), `Interfaces/IConectores.cs` (`IConectorTipo`, `IRegistroConectores`,
`IGuardiaDestinoHttp`, `IConexionConectorService`). Modificados: `Motor/IMotorAgentes.cs`
(`IHerramientaAprobacionPorLlamada`), `Interfaces/IPermisosOrganizacion.cs` (2 permisos).

**Infrastructure** — Nuevos: `Services/Conectores/GuardiaDestinoHttp.cs`, `ConectorHttpGenerico.cs`,
`ConexionConectorService.cs`, `HerramientasConectores.cs`, `RegistroConectores.cs`,
`Data/Configurations/ConectoresConfigurations.cs`, migración `Data/Migrations/20260916141804_ConectoresM11.cs`
(+ Designer y snapshot). Modificados: `Services/Motor/ProcesadorTareas.cs` (herramientas por tenant +
`NecesitaAprobacionAsync` en 3 puntos), `Services/Motor/ServicioTareas.cs` (encadenado de `Resumir`),
`Services/Motor/ProveedorModeloSimulado.cs` (`GuionConectores`),
`Services/Subagentes/ResumenHerramientasPlataforma.cs` (rótulo del pedido), `Services/ValidacionArranque.cs`
(corte por `PermitirDestinosPrivados`), `Services/Organizacion/PermisosOrganizacion.cs`, `Data/AppDbContext.cs`
(2 DbSet + exclusiones de audit trail), `DependencyInjection.cs` (registro + cliente HTTP con `ConnectCallback`).

**Web** — Nuevos: `Controllers/ConexionesController.cs`, `Models/ConectoresViewModels.cs`, vistas
`Conexiones/{Index, Form, Uso, _ScriptAcciones}.cshtml` y `Clientes/Conexiones.cshtml`. Modificados:
`Controllers/ClientesController.cs` (1 acción), `Views/Clientes/Details.cshtml` (botón),
`Views/Shared/_Layout.cshtml` (ítem "Conexiones"), `appsettings.json` (sección `Conectores`),
`appsettings.Development.json` y `appsettings.Production.example.json`.

**Admin** — `Program.cs`: verbo `conexiones <tenantSlug>` y ayuda.
**Tests**: nuevo `ConectoresTests.cs` (54 con sus casos de Theory) e `Infra/ServidorLocalDePrueba.cs`.
**Repo**: `docs/diseno-organizacion-roles-reglas.md` (M11 ✅) y `PLAN-IMPLEMENTACION.md`.

### Evidencia de build y tests M11
- `dotnet build OlvidataAgentes.slnx`: **0 errores**. 2 advertencias **preexistentes** que aparecen solo en compilación
  completa y no son de M11 (`xUnit2013` en `ReglasPropuestasAgentesTests` y `CS0114` en `HomeController.StatusCode`).
- `dotnet test tests/OlvidataAgentes.Tests`: **392 OK / 0 fallidos** (338 previos + 54 nuevos).
- **Los 4 goldens de hash de contexto intactos**, más el golden nuevo de M11: el hash de una tarea es el mismo con y
  sin conexiones activas, y el prompt de sistema es idéntico.
- **Casos de SSRF cubiertos** (todos verdes): `localhost`/`127.0.0.1`/`127.1.2.3`, `0.0.0.0`, `10.x`, `172.16.x`,
  `192.168.x`, `169.254.169.254` (con mensaje propio de metadata de nube), `169.254.x`, `100.64.x`, multicast, `::1`,
  `fe80::`, `fd00::`, `::ffff:127.0.0.1`; dominio fuera de la lista blanca, subdominio no listado, el apex de un
  comodín, el mismo host en otro puerto, `http` sin TLS, usuario y contraseña en la URL, una IP interna escrita a mano
  aunque esté en la lista blanca, **redirección a un destino no permitido** y una ruta que apunta a otro host.
- **Conector probado contra un servidor local** (`ServidorLocalDePrueba`, 127.0.0.1, puerto que elige el sistema):
  consulta con sus encabezados, error 503 del sistema externo, respuesta más grande que el tope, redirección permitida
  y no permitida, método no habilitado y tiempo de espera agotado. **Cero salidas a internet.**
- Lecciones: (1) escribir una columna de la conexión dentro del commit del motor **acopla su token de concurrencia a la
  tarea** — el "último uso" se calcula del historial; (2) el proveedor MySQL sigue ignorando `stored: true` en
  `CreateTable`, hay que escribir las columnas generadas a mano (tercera vez: M2, M4, M11); (3) para que una decisión de
  seguridad sea confiable tiene que ser **fail-closed en el motor**, no en la herramienta: `RequiereAprobacion` queda en
  true y el motor consulta, así un error nuestro pide aprobación en vez de dejar pasar; (4) validar la IP en el
  `ConnectCallback` **y conectar a esa misma dirección** es lo único que cierra el DNS rebinding — resolver antes y
  conectar por nombre deja una ventana.

### Riesgos residuales M11
- **No hay ningún conector concreto** (a propósito): el HTTP genérico es el ejemplo. Gmail, Drive y ARCA necesitan
  OAuth y refresco de tokens, que M11 **no** resuelve (las credenciales son estáticas, en encabezados).
- **Nunca se llamó a un sistema externo real**: todo se probó contra un servidor local. Lo que falta antes de conectar
  uno de verdad está en "Próximos pasos".
- **La revisión de destinos no cubre un proxy corporativo ni IPv6 detrás de NAT64**: si el hosting mete un proxy, el
  `ConnectCallback` deja de ver la IP real del destino. Hay que verificarlo en SmarterASP antes de habilitar conectores
  en producción.
- **Sin reintentos**: un error del sistema externo vuelve al agente y el agente decide. Puede consumir llamadas del
  tope sin resolver nada.
- **El alcance no llega a nivel de área** (DI-M11-4) y el **nivel de aprobación es siempre Director** (DI-M11-2): las
  dos son deuda consciente, no olvidos.
- **`MaxCaracteresParaElAgente` recorta la respuesta sin paginar**: si un sistema externo devuelve una lista larga, el
  agente ve el principio. No hay "traeme la página siguiente".
- **Data Protection**: si se pierden las claves de `keys/`, las credenciales guardadas quedan ilegibles. El código lo
  detecta y lo deja en el log ("hay que volver a cargarlos"), pero la llamada va a fallar por credenciales.
- Verificación visual pendiente (QA): listado, alta, edición con credenciales ya guardadas, historial, vista de staff,
  "Ver pasos", tarjeta de aprobación, mobile 390 y ambos temas.

### Proximos pasos pendientes M11
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M11).
- **Antes de conectar un sistema real**: (1) confirmar que el hosting no mete un proxy que anule la revisión de IP;
  (2) decidir con Joaquín si un conector concreto necesita OAuth y, si sí, diseñar el refresco de tokens; (3) definir
  qué pasa cuando una credencial vence (hoy la llamada falla y queda en el historial, sin aviso al Director);
  (4) revisar con un caso real si el tope de llamadas por tarea y el de KB alcanzan.
- Evaluar avisos al Director cuando una conexión empieza a fallar seguido.
- Deuda fuera de alcance: alcance por área, reintentos, paginación de respuestas, `dotnet-ef` 10.0.2 más vieja que el
  runtime 10.0.9.

---
# M10 — Base de conocimiento por rubro

Estado: **implementada 2026-09-16, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M10
(RF-M10-01..13, CA-M10-01..12), `2-disenador-funcional.md` M10 (D-M10-1..10, P-M10-01/02) y `3-arquitecto-mvc.md` M10
(RT-M10-01..09), aprobados sin gate por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto
personal). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. Una entrega, una migración: `ConocimientoRubroM10`.
**Sin contenido real de ningún rubro** (solo un ejemplo de plantilla), **sin una sola llamada a Anthropic**, sin commits.
Mcp y Cli sin tocar (solo compilan).

### Escaneo de reutilizacion M10
| Fuente | Qué se tomó | Grado |
|---|---|---|
| `docs/patrones/catalogo.yml` → **PAT-033** (workspace de documentos por cliente con herramientas de solo lectura) | El patrón entero: clase base con guardas, `PatronLike` con escape "!", recorte en memoria con `IgnoreCase\|IgnoreNonSpace`, serializador JSON escapado, `Resumir` para "Ver pasos", tabla hija sin baja lógica | Literal (mismo patrón, otro eje: rubro en vez de cliente) |
| Template M5 `HerramientasDocumentos.Json` y `PatronLike` | **Se llaman directamente**, no se copiaron: son del mismo assembly y ya están probados | Literal (reuso de código) |
| Template núcleo `ImportadorRubro.ProcesarAsync` | La sección `conocimiento:` es una llamada más al mismo método (mismo hash, mismo "sin cambios no crea versión", mismo Borrador) | Literal (extensión) |
| Template M6 (acciones de demostración) y M5 (documentos) en `ProcesadorTareas` | "Herramientas agregadas a la lista de la solicitud sin tocar el prompt de sistema" | Literal (patrón del repo) |
| Template M1 `PreparadorTareaTrabajo.SuscripcionVigenteAsync` | Criterio de suscripción vigente al rubro, idéntico | Literal |
| Escaneo `docs/*/definiciones/5-implementador.md` del estudio | Ningún otro proyecto tiene "base de conocimiento consultable por un agente". Lo más cercano es la búsqueda por columnas de DataTables, que no aplica | Sin match |
| PAT-042 | **Creado** en el catálogo: "base de conocimiento del proveedor por rubro, consultable por herramientas" | Nuevo |

### Qué se hizo

1. **Un tipo de artefacto más (RF-M10-01, RT-M10-01).** `TipoArtefacto.Conocimiento = 5`. Un documento de conocimiento
   es un `Artefacto` con sus `ArtefactoVersion`: hereda el versionado por hash, el Borrador → Evaluada → Publicada, el
   gate de `IVersionadoService`, la pantalla de la versión y la trazabilidad al archivo de origen. Lo único nuevo es
   `FragmentosConocimiento`.
2. **Troceo determinístico al importar (RF-M10-02, RT-M10-02).** `TroceadorConocimiento.Trocear` (Application, función
   pura): encabezados ATX `#`…`######`, bloques de código ignorados, ruta de encabezados como fuente
   ("Captación › Documentación mínima"), preámbulo en "Introducción", secciones vacías descartadas y secciones largas
   partidas por párrafo en "(parte N de M)" sin cortar palabras.
3. **Manifiesto (RF-M10-01, RT-M10-08).** Sección `conocimiento:` con el mismo `{glob|archivo}` que el resto; rechazada
   con advertencia en el rubro "plataforma". El importador reporta documentos y secciones troceadas.
4. **Tres herramientas de solo lectura (RF-M10-04..08).** `conocimiento_listar`, `conocimiento_buscar` y
   `conocimiento_leer`, con las guardas resueltas contra la base: tarea de trabajo, rubro **de la tarea** (nunca de la
   entrada del modelo), rubro activo y distinto de "plataforma", suscripción vigente y **solo versiones publicadas**.
5. **El contexto no cambia (RF-M10-04, RT-M10-03).** `ProcesadorTareas` las agrega a `permitidas` solo si el rubro tiene
   material publicado. Los 4 formatos y sus hashes quedan intactos (3 goldens previos + un golden nuevo propio).
6. **"Ver pasos" en palabras (RF-M10-09, D-M10-6).** `HerramientasConocimiento.Resumir` se encadena en `ServicioTareas`
   entre el de documentos y el de plataforma; `_PasosTurno.cshtml` oculta los pedidos (se explican en el resultado) y
   usa "Ver lo que leyó" para la lectura.
7. **Pantallas (RF-M10-10/11).** Staff: `Nucleo/Conocimiento/{rubro}` (tarjetas + tabla) y
   `Nucleo/VersionConocimiento/{versionId}` (secciones plegadas), con entradas desde la ficha del rubro y desde la
   versión. Miembro: `Conocimiento/Index` ("Material de Olvidata" en el menú), agrupado por rubro y **sin texto**.
8. **Simulador (RF-M10-12, D-M10-9).** `GuionConocimiento`: listar + buscar → leer → cierra citando documento y sección.
   Se dispara por el pedido ("conocimiento", "guía" o "material") con los nombres **exactos** de las herramientas.
9. **Consola Admin.** `conocimiento <rubro>` y contadores en `importar`.
10. **Ejemplo de plantilla (RF-M10-13).** `nucleo/rubros/_plantilla/conocimiento/00-ejemplo-plantilla.md`, titulado
    "EJEMPLO DE PLANTILLA — no es contenido real", más la sección comentada en `_plantilla/rubro.yml`.

### Decisiones de implementacion M10 (ambigüedades resueltas)
- **DI-M10-1 El conocimiento es un artefacto, no una entidad paralela.** La otra opción era copiar el modelo de M8
  (`ConjuntoCasos` / `VersionConjuntoCasos`), pero los casos **no se publican** y el conocimiento sí: replicar el gate,
  los estados y las pantallas habría sido escribir de nuevo lo que `Artefacto` ya hace. Costo: hay que acordarse de
  excluir el tipo nuevo en los dos caminos que sirven contenido (hecho, y con test).
- **DI-M10-2 El rubro sale de la tarea, no de `ContextoHerramienta`.** No se tocó el record (lo usan todas las
  herramientas del sistema): la clase base consulta `TareaAgente → ArtefactoVersion → Artefacto.RubroId`. Una consulta
  más por llamada a cambio de no tocar una firma compartida ni poder pasarle un rubro equivocado.
- **DI-M10-3 Se habilita por RUBRO, no por licencia (D-M10-5).** Todo el material publicado del rubro está disponible
  para toda organización con suscripción vigente a ese rubro. Cobrarlo aparte sería una condición más en una consulta.
- **DI-M10-4 Bug encontrado contra datos reales: la ruta de encabezados.** La primera versión indexaba la ruta por el
  número de nivel y rellenaba los faltantes con "…". Importando el ejemplo de plantilla real (que arranca en `##`)
  salió `… › Cómo se trocea › Buenas prácticas › Qué NO va acá`, con un hermano convertido en hijo. Se reescribió con
  una **pila que guarda el nivel de cada encabezado** y desapila mientras el tope sea igual o más profundo. Test
  dedicado con el caso real.
- **DI-M10-5 Sin navegación de vuelta en `FragmentoConocimiento`.** `ArtefactoVersion` tiene baja lógica y el fragmento
  no: con navegación, EF levanta la advertencia 10622 ("required end of a relationship with a filtered entity"). Se
  configuró con `HasOne<ArtefactoVersion>().WithMany(v => v.Fragmentos)`, igual que `DocumentoCarteraParte`. Verificado:
  el modelo sigue con las **2 advertencias 10622 preexistentes** (Licencia), ninguna nueva.
- **DI-M10-6 `HerramientasDocumentos.Json` y `PatronLike` se llaman, no se copian.** Son del mismo assembly
  (`Json` es `internal`, `PatronLike` es público) y ya están probados y corregidos por QA de M5. Copiarlos habría
  creado dos verdades para el mismo escape.
- **DI-M10-7 `MaxCaracteresFragmento` solo aplica al importar.** El troceo queda congelado en la versión: bajarlo
  después no reescribe nada, hay que reimportar. Está dicho en `appsettings.json` y en RT-M10-09.
- **DI-M10-8 Listado de staff sin DataTables.** El resto del Núcleo IP (Index, Rubro) usa tablas planas y son listas
  de piezas del núcleo, de decenas de filas. Se siguió la convención local en vez de traer DataTables server-side para
  una tabla que no lo necesita.
- **DI-M10-9 Sin gate de pruebas automáticas (RT-M10-07).** `IGateEvaluacion.ExigePruebas` no se tocó: el conocimiento
  no es un prompt ejecutable. Verificado de punta a punta con la consola (`importar → evaluar --aprobada → publicar`).

### Migraciones EF generadas M10
- `20260916133122_ConocimientoRubroM10` — `CreateTable FragmentosConocimiento` (`Id bigint` identity,
  `ArtefactoVersionId int`, `Numero int`, `Seccion varchar(400)`, `Texto mediumtext`), único
  `(ArtefactoVersionId, Numero)` y FK a `ArtefactoVersiones` **Restrict**. `Down` = `DropTable`. **Ninguna tabla
  existente se modifica**: `TipoArtefacto` se guarda como int y el valor 5 no necesita migración.
- **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-16**, con `database update EvaluacionAutomaticaM8` (Down
  OK, con fragmentos cargados) y `database update` otra vez; `has-pending-model-changes` limpio.
- Verificado por SQL (`scratchpad/verificar-m10.sql` y `verificar-m10b.sql`, transacción revertida): tipos y largos
  exactos; **1062 real** en `(ArtefactoVersionId, Numero)`; **1451 real** al borrar la versión (FK Restrict);
  collation `utf8mb4_0900_ai_ci` → LIKE insensible a mayúsculas **y tildes** (y ñ = n, igual que
  `CompareOptions.IgnoreNonSpace` en memoria, así el pre-filtro nunca descarta de menos); `%` y `_` escapados con `!`
  quedan literales; `EXPLAIN` de la lectura por número usa el índice único (`range`, `Using index condition`) y el join
  de la búsqueda resuelve `v` y `a` por `eq_ref` sobre PRIMARY. **0 restos** tras el ROLLBACK.
- **Importación real verificada** con el ejemplo de plantilla: `importar` → 1 documento, 5 secciones; reimportar sin
  cambios → "1 sin cambios, 0 secciones"; `evaluar --aprobada` → Evaluada; `publicar` → publicada;
  `conocimiento inmobiliario` → "v1 publicada, 5 secciones". **Ninguna llamada a Anthropic.**

### Archivos y capas modificadas M10
**Domain** — Nuevos: `Entities/Conocimiento.cs` (`FragmentoConocimiento`). Modificados: `Enums/EnumsAgentes.cs`
(`TipoArtefacto.Conocimiento = 5`), `Entities/Artefacto.cs` (`ArtefactoVersion.Fragmentos`).

**Application** — Nuevos: `Settings/ConocimientoOptions.cs`, `Motor/NotaConocimiento.cs`
(`NombresHerramientasConocimiento`), `DTOs/ConocimientoDtos.cs` (+ `MensajesConocimiento`),
`Interfaces/IConocimientoNucleo.cs` (`IConocimientoService`), `Helpers/TroceadorConocimiento.cs`. Modificados:
`Interfaces/INucleoServices.cs` (doc de `ListarArtefactosPublicadosAsync`), `DTOs/AgentesDtos.cs` (contadores de
conocimiento en `ImportacionResultadoDto`).

**Infrastructure** — Nuevos: `Services/Conocimiento/HerramientasConocimiento.cs` (3 herramientas + base + `Resumir`),
`Services/Conocimiento/ConocimientoService.cs`, `Data/Configurations/ConocimientoConfigurations.cs`, migración
`Data/Migrations/20260916133122_ConocimientoRubroM10.cs` (+ Designer y snapshot). Modificados:
`Services/Nucleo/ImportadorRubro.cs` (sección `conocimiento:` + troceo), `Services/Nucleo/CatalogoNucleo.cs` (exclusión
en los dos caminos que sirven contenido), `Services/Motor/ProcesadorTareas.cs` (herramientas + `HayConocimientoPublicadoAsync`),
`Services/Motor/ServicioTareas.cs` (encadenado de `Resumir`), `Services/Motor/ProveedorModeloSimulado.cs`
(`GuionConocimiento`), `Data/AppDbContext.cs` (DbSet), `DependencyInjection.cs`.

**Web** — Nuevos: `Controllers/ConocimientoController.cs`, `Models/ConocimientoViewModels.cs`, vistas
`Nucleo/Conocimiento.cshtml`, `Nucleo/VersionConocimiento.cshtml`, `Conocimiento/Index.cshtml`. Modificados:
`Controllers/NucleoController.cs` (2 acciones), `Views/Nucleo/{Rubro, Version}.cshtml`, `Views/Tareas/_PasosTurno.cshtml`,
`Views/Shared/_Layout.cshtml` (ítem "Material de Olvidata"), `appsettings.json` (sección `Conocimiento`).

**Admin** — `Program.cs`: verbo `conocimiento <rubro>`, contadores en `importar` y ayuda.

**Núcleo**: `nucleo/rubros/_plantilla/conocimiento/00-ejemplo-plantilla.md` (**plantilla, sin contenido real**) y la
sección `conocimiento:` comentada en `_plantilla/rubro.yml`.
**Tests**: nuevo `ConocimientoTests.cs` (19). **Repo**: `docs/diseno-organizacion-roles-reglas.md` (M10 ✅) y
`PLAN-IMPLEMENTACION.md`.

### Evidencia de build y tests M10
- `dotnet build OlvidataAgentes.slnx`: **0 errores, 0 advertencias**.
- `dotnet test tests/OlvidataAgentes.Tests`: **338 OK / 0 fallidos** (319 previos + 19 nuevos).
- **Los 4 goldens de hash de contexto (formatos 1, 2, 3 y 4) intactos**, más el golden nuevo de M10: el hash de una
  tarea es el mismo con y sin material publicado en el rubro.
- Lecciones: (1) armar una ruta de encabezados **indexando por el número de nivel** se rompe con documentos que
  arrancan en `##` o que saltean un nivel — va una pila con el nivel de cada encabezado; (2) `utf8mb4_0900_ai_ci`
  ignora tildes **y** trata ñ = n en LIKE, lo mismo que `CompareOptions.IgnoreNonSpace` en .NET: el pre-filtro de la
  base y la verificación en memoria coinciden, que es justo lo que hace falta para que la búsqueda no pierda filas;
  (3) una tabla hija sin baja lógica colgada de un padre que sí la tiene necesita `HasOne<T>()` **sin navegación de
  vuelta**, o EF avisa 10622 en cada arranque.

### Riesgos residuales M10
- **No hay contenido real de ningún rubro** (a propósito): lo único publicado en dev es el ejemplo de plantilla. La
  calidad de las búsquedas con material real está sin medir.
- **Búsqueda por LIKE** (RT-M10-05): escanea los fragmentos publicados del rubro. Con decenas de documentos es
  trivial; con cientos hay que evaluar FULLTEXT. Es deuda consciente, no un olvido.
- **Ningún agente pidió todavía el material con el modelo real**: cuánto tokens agrega una consulta y si el agente la
  usa cuando corresponde son estimaciones hasta la primera corrida real.
- **`MaxCaracteresFragmento` congelado en la versión**: cambiarlo pide reimportar. Está documentado en los dos lados.
- **El ejemplo de plantilla quedó importado y PUBLICADO en `olvidata_agentes_dev`** (rubro inmobiliario) para que QA
  tenga con qué probar. Para sacarlo: borrar de `FragmentosConocimiento`, `EvaluacionesVersion`, `ArtefactoVersiones`
  y `Artefactos` donde `Tipo = 5`. **No está en ninguna base que no sea la local.**
- Verificación visual pendiente (QA): material del rubro, secciones de una versión, pantalla del miembro, "Ver pasos"
  con los tres rótulos, mobile 390 y ambos temas.

### Proximos pasos pendientes M10
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M10).
- Escribir material real del primer rubro en su repo fuente (fuera de este repositorio) e importarlo.
- Evaluar si el conocimiento merece su propio tipo de caso en M8 (hoy no: no es un prompt ejecutable).
- Deuda fuera de alcance: índice FULLTEXT; `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9.

---
# M9 — Preparación de despliegue (local: preparar, no desplegar)

Estado: **implementada 2026-09-16, pendiente de QA**. Entrada: `1-analista-funcional.md` M9 (RF-M9-01..06,
CA-M9-01..06), `2-disenador-funcional.md` M9 (D-M9-1..3) y `3-arquitecto-mvc.md` M9 (RT-M9-01..08), aprobados sin gate
por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal).
Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. **Sin migración EF.** **Nada desplegado, ningún servidor tocado,
ninguna credencial real usada, ninguna llamada a Anthropic, sin commits.** Mcp y Cli sin tocar (solo compilan).

### Escaneo de reutilizacion M9
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template blankproject (este repo) — `DatabaseHealthCheck` / `SmtpHealthCheck` | Los dos chequeos nuevos copian el contrato y el estilo de mensaje | Literal (extensión) |
| Template blankproject — `web.config` ANCM OutOfProcess + redirect HTTPS + compresión y rate limiting ya en `Program.cs` | No hubo que agregar nada de compresión ni de estáticos: ya estaba | Literal |
| Template M1/M8 — lease + `Version` + `Intentos` de `TareaAgente` y `CorridaEvaluacion` | `RecuperadorLeases` usa el mismo token de concurrencia y el mismo `IgnoreQueryFilters([FiltroTenant])` | Literal (patrón del repo) |
| Template M2 — `ResolvedorSesion` + `SesionOrganizacionMiddleware` (fail-closed, caché 60 s) | PA-05 entra por el mismo camino del usuario bloqueado, sin inventar otro | Literal (extensión) |
| Escaneo `docs/*/definiciones/5-implementador.md` del estudio | Ningún otro proyecto tiene "preparación de despliegue" como feature con validación de arranque y health checks propios; los deploys a SmarterASP existen como **práctica** (Web Deploy, skip-rules, subir sin borrar) y de ahí salen §3 y §8 del documento | Práctica, no código |

### Qué se hizo

1. **Publicación (RF-M9-01).** Perfil `Properties/PublishProfiles/SmarterASP.pubxml` (FileSystem → `publish/web`,
   ignorado por git), con `EnvironmentName=Production`, exclusión de `appsettings.Development.json` y skip-rules de
   Web Deploy para `keys`, `App_Data`, `Logs` y `appsettings.Production.json`. Comando único:
   `dotnet publish src/OlvidataAgentes.Web -c Release -p:PublishProfile=SmarterASP`.
   **Verificado sobre el paquete real:** `web.config` con `ASPNETCORE_ENVIRONMENT=Production`, `hostingModel=OutOfProcess`
   y el redirect a HTTPS; `wwwroot` con `.br`/`.gz` precomprimidos; **sin** `appsettings.Development.json`, sin
   `appsettings.Production.example.json`, sin `keys/`, sin `App_Data/`, sin `Logs/`. 138 MB, 70 archivos en la raíz
   (`runtimes/` de todos los SO se lleva 68 MB).
2. **Configuración (RF-M9-02).** `appsettings.Production.example.json` versionado y **excluido del publish**, con todas
   las secciones que el sistema usa hoy y los secretos marcados como variable de entorno.
   `ValidacionArranque` (Infrastructure) revisa configuración y carpetas y, fuera de Development, **corta el arranque**
   con la lista de claves. El bootstrap logger ahora escribe también en `Logs/arranque-*.log` para que el motivo se
   pueda leer por FTP (RT-M9-02).
3. **Carpetas que sobreviven (RF-M9-03).** `keys/`, documentos de clientes y `Logs/` documentadas en
   `docs/deploy-smarterasp.md` §3 con su regla por método de subida; comprobación de escritura al arrancar (las dos
   primeras cortan el arranque, los logs avisan).
4. **Salud (RF-M9-04).** `DocumentosHealthCheck` (sonda de escritura) y `MotorAgentesHealthCheck` (latido del worker,
   registrado solo donde el worker corre). `/health` pasa a JSON por chequeo, **sin excepciones ni stack traces**;
   `/health/vivo` anónimo para el ping externo. Serilog de producción en la plantilla: dos archivos rotativos por día y
   por tamaño (20 MB), operación 14 días y errores 60, `shared: true` por el reciclado solapado de ANCM.
5. **Checklist (RF-M9-05).** `docs/deploy-smarterasp.md`: requisitos, publicar, configurar, carpetas, 11 pasos en orden,
   AlwaysRunning, verificación y humo mínimo, qué no subir, rollback y riesgos del día.
6. **Higiene (RF-M9-06).** El modelo simulado y las herramientas de demostración **ya estaban cubiertos por tests desde
   M3b/M6** (`Development` + `Anthropic:Simulado` explícito; `Production`/`Testing` → 0 registros) — se verificó y no
   hizo falta agregar nada. PA-05 implementado (abajo).

### PA resueltos y abiertos

- **PA-03 (resuelto).** `RecuperadorLeases` + `IProcesosLocales`: al arrancar, el worker vence los leases de procesos
  muertos **de esta misma máquina** y retoma en el primer ciclo (segundos en vez de hasta 5 minutos). No se bajó
  `LeaseSegundos` porque el lease no se renueva durante el turno (RT-M9-05). Fail-closed: "no sé si vive" = no se toca.
- **PA-05 (parcial).** `Tenant.Estado` distinto de Activo corta la sesión (`ResolvedorSesion` → `OrganizacionSuspendida`
  en `IContextoUsuario`) y bloquea el login con un texto con salida. **Abierto**: el staff sigue sin UI para editar
  nombre/email/rol/estado de miembros, las pantallas legadas siguen sin diseño nuevo, y una tarea ya encolada de una
  organización suspendida sigue ejecutándose en el worker.
- **PA-07 (abierto, no depende del código).** Es una respuesta de soporte de SmarterASP. Queda documentado en
  `docs/deploy-smarterasp.md` §5 con el plan B implementado: ping externo a `/health/vivo`.

### Archivos

**Nuevos** — `src/OlvidataAgentes.Application/Motor/LatidoMotor.cs`, `.../Motor/IRecuperadorLeases.cs` (+ `IProcesosLocales`);
`src/OlvidataAgentes.Infrastructure/Services/ValidacionArranque.cs`, `.../Services/DocumentosHealthCheck.cs`,
`.../Services/Motor/MotorAgentesHealthCheck.cs`, `.../Services/Motor/RecuperadorLeases.cs`, `.../Services/Motor/ProcesosLocales.cs`;
`src/OlvidataAgentes.Web/Helpers/SaludJson.cs`, `.../appsettings.Production.example.json`,
`.../Properties/PublishProfiles/SmarterASP.pubxml`; `docs/deploy-smarterasp.md`; `tests/OlvidataAgentes.Tests/DespliegueTests.cs`.

**Modificados** — `Infrastructure/DependencyInjection.cs` (registros y 2 health checks), `Services/Motor/MotorAgentesWorker.cs`
(latido + recuperación al arranque), `Services/Organizacion/ResolvedorSesion.cs` y `ContextoUsuario.cs` +
`Application/Interfaces/IContextoUsuario.cs` (PA-05), `Web/Middleware/SesionOrganizacionMiddleware.cs`,
`Web/Controllers/AccountController.cs`, `Web/Program.cs` (bootstrap logger, revisión de arranque, endpoints de salud),
`Web/OlvidataAgentes.Web.csproj`.

### Evidencia

`dotnet build OlvidataAgentes.slnx` → **0 errores** (2 advertencias preexistentes: `HomeController.StatusCode` y un
`xUnit2013` de M7a). `dotnet test tests/OlvidataAgentes.Tests` → **319/319 OK** (287 previos + 32 nuevos).
`dotnet publish` con el perfil → paquete verificado en `publish/web` (contenido y `web.config` revisados a mano).
**Ningún servidor tocado, ninguna llamada a Anthropic, sin migraciones, sin commits.**

### Pruebas mínimas para QA

1. **Revisión de arranque**: correr el portal con `ASPNETCORE_ENVIRONMENT=Production` y una clave crítica vacía
   (por ejemplo `Anthropic__ApiKey=`): tiene que **no arrancar** y dejar el motivo en `Logs/arranque-*.log`, sin valores.
   Repetir en Development: arranca igual y solo avisa.
2. **`/health`**: entrar como SuperUsuario → JSON con `mysql`, `smtp`, `documentos` y `motor`. Apuntar
   `Documentos:RaizAlmacenamiento` a una carpeta sin permisos y ver `documentos` en `Unhealthy` con texto claro.
   Poner `MotorAgentes:Habilitado=false` → `motor` en `Degraded`. Verificar que no aparezca ningún stack trace.
3. **`/health/vivo`**: sin loguearse, responde `vivo` en texto plano. Como usuario común, `/health` da 403.
4. **PA-03**: con una tarea En curso, matar el proceso del portal y volver a levantarlo. La tarea tiene que retomarse
   en segundos (log "Arranque: N tarea/s… se retoman en este ciclo"), no a los 5 minutos.
5. **PA-05**: con un Director logueado, poner su organización en `Suspendido` por SQL, esperar 60 s (caché) y navegar:
   vuelve al login con el mensaje de empresa suspendida. Intentar entrar de nuevo: mismo mensaje, sin rulo. Un
   SuperUsuario sin organización entra normal. Volver a `Activo` y verificar que entra.
6. **Paquete**: correr el `dotnet publish` del documento y verificar `publish/web/web.config` con
   `ASPNETCORE_ENVIRONMENT=Production` y que no esté `appsettings.Development.json`.
7. **Regresión**: login, portal de cliente y backoffice de M2–M8 sin 5xx (M9 tocó el camino de sesión de todo el portal).
# M8 — Evaluación automática de prompts (núcleo)

Estado: **implementada 2026-09-16, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M8 (RF-M8-01..25,
CA-M8-01..23), `2-disenador-funcional.md` M8 (D-M8-1..26, P-M8-01..08) y `3-arquitecto-mvc.md` M8 (RT-M8-01..13),
aprobados sin gate por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal).
Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. Una entrega, una migración: `EvaluacionAutomaticaM8`.
**Agentes de la organización fuera del alcance (P1).** Sin contenido de rubros, **sin una sola llamada a Anthropic**
(todo con el doble guionado), sin commits.

### Escaneo de reutilizacion M8
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template núcleo (`ImportadorRubro`: hash del cuerpo, `sinCambios`, `FuenteArchivos {Glob, Archivo}`, advertencias) | Sección `evaluaciones:` con el mismo criterio de hash y "sin cambios no crea versión"; los conjuntos son un artefacto **paralelo** (no `TipoArtefacto`) | Literal (extensión) |
| Template M3/M4/M4b/M7b (`ConstructorContexto`: `ArmarAsync`, `ArmarPlataformaAsync`, `CalcularHash`, `Escapar`, 3 bloques con `Cachear`) | **Render extraído a `Renderizar(ContenidoContexto, formato)`**, compartido por los 4 formatos y por `ArmarEvaluacionAsync` | Refactor sin cambio de comportamiento (RT-M8-01) |
| Template núcleo (`IVersionadoService`, `TipoEvaluacion.Automatica` sin llamador) | El ejecutor es el primer llamador de `automatica: true`; el gate de `PublicarAsync` se extiende | Literal (extensión) |
| Template M1 (`IProveedorModelo`, `RespuestaModelo`, `MotivoFin`, bloques de herramienta, `TelemetriaService.CalcularCosto`) | Bucle propio y corto en `EjecutorCorrida` (no se reusa `ProcesadorTareas`: crearía tareas de una organización cliente) | Patrón del mismo repo |
| Template M6 (`PeriodoGasto`, barra de consumo, "cortar antes de cada llamada") | Bolsa mensual propia de Olvidata y barra reusada; **no pasa por `IControlGasto`** | Literal (patrón) |
| Template M7a (`MotorAgentesWorker` con barridos en scopes con `EstablecerAccesoGlobal()`, lease + `Intentos` + `Version`) | Barrido nuevo de corridas, de a una y fuera de `MaxTareasSimultaneas` | Literal (patrón) |
| Template M2/M5 (policies de staff, DataTables + `FiltrosSesion`, SweetAlert2, escape de texto hostil) | Listado de corridas, modales de cancelación y excepción, bloque de texto de prueba | Literal |
| PAT-040 / PAT-041 | **Creados** en el catálogo con rutas reales (`pendiente_verificar: false` en todas las del repo) | Nuevo |

### Archivos y capas modificadas M8
**Domain** — Nuevos: `Enums/EnumsEvaluacion.cs` (7 enums), `Entities/Evaluaciones.cs` (`ConjuntoCasos`,
`VersionConjuntoCasos`, `CasoEvaluacion`, `CorridaEvaluacion`, `ResultadoCaso`). Modificados: `Enums/EnumsAgentes.cs`
(`CanalUso.Evaluacion = 4`), `Entities/Artefacto.cs` (`EvaluacionVersion` + `CorridaEvaluacionId`, `EsExcepcion`,
`RegistradaPorUsuarioId`, `HashCasos`), `Entities/Tenant.cs` (`EsInterna` + `SlugInterno`).

**Application** — Nuevos: `Settings/EvaluacionOptions.cs`, `DTOs/EvaluacionDtos.cs` (+ `MensajesEvaluacion`),
`Interfaces/IEvaluacionAutomatica.cs` (`ICasosEvaluacionService`, `IEstimadorCorrida`, `ICorridaEvaluacionService`,
`IEjecutorCorrida`, `IRevisorAutomatico`, `IGateEvaluacion`), `Helpers/VerificacionesTexto.cs`, `Helpers/HashCasos.cs`.
Modificados: `Motor/IConstructorContexto.cs` (`ArmarEvaluacionAsync` + `SolicitudContextoEvaluacion`),
`Motor/ModeloConversacion.cs` (`SolicitudModelo.EsquemaSalida` y `SolicitudModelo.Guion` + `GuionEvaluacion`),
`Interfaces/INucleoServices.cs` (`RegistrarEvaluacionAsync` con parámetros opcionales y `RegistrarExcepcionAsync`),
`Helpers/ArgentinaTime.cs` (`ToUtc`), `DTOs/AgentesDtos.cs` (contadores de conjuntos en `ImportacionResultadoDto`).

**Infrastructure** — Nuevos: `Services/Evaluacion/{CasosEvaluacionService, EstimadorCorrida, CorridaEvaluacionService,
EjecutorCorrida, RevisorAutomatico}.cs`, `Data/Configurations/EvaluacionConfigurations.cs`, migración
`Data/Migrations/20260916022048_EvaluacionAutomaticaM8.cs` (+ Designer y snapshot). Modificados:
`Services/Motor/ConstructorContexto.cs` (**extracción del render** + `ArmarEvaluacionAsync`),
`Services/Nucleo/ImportadorRubro.cs` (`ImportarCasosAsync` y el modelo YAML de un archivo de casos),
`Services/Nucleo/VersionadoService.cs` (gate, excepción, `MotivoNoPublicableAsync`),
`Services/Motor/ProveedorModeloAnthropic.cs` (`OutputConfig`), `Services/Motor/ProveedorModeloSimulado.cs`
(guion de evaluación y revisor simulado), `Services/Motor/MotorAgentesWorker.cs` (barrido de corridas),
`Services/Organizacion/MiembroService.cs` y `Services/Licencias/LicenciaService.cs` (rechazo de la organización interna),
`Data/AppDbContext.cs` (5 DbSets), `Data/Configurations/AgentesConfigurations.cs` (Tenant y EvaluacionVersion),
`Data/SeedData.cs` (`AsegurarOrganizacionInternaAsync`), `DependencyInjection.cs`.

**Web** — Nuevos: `Models/EvaluacionViewModels.cs`, `Helpers/PruebasTextos.cs`, vistas
`Nucleo/{Casos, CorrerPruebas, Corrida, Pruebas, _ListaCasos, _ResultadosCorrida, _DetalleCaso, _BloqueTextoPrueba,
_ScriptCorrida}`. Modificados: `Controllers/NucleoController.cs` (11 acciones nuevas),
`Controllers/ClientesController.cs` (excluye la organización interna), `Models/AgentesViewModels.cs`
(`NucleoRubroViewModel.Pruebas`), `Views/Nucleo/{Version, Rubro}.cshtml`, `Views/Shared/_Layout.cshtml`
(ítem "Pruebas de prompts"), `wwwroot/css/site.css`, `appsettings.json` (sección `Evaluacion`).

**Admin** — `Program.cs`: 7 verbos `evaluacion-*`, contadores de casos en `importar`, `publicar-rubro` avisa cuántas
excepciones registra; `appsettings.json` con la tabla de precios (los verbos la necesitan para estimar).

**Núcleo**: `nucleo/plataforma/evaluaciones/` (4 archivos, 15 casos, **borrador para revisar**) y sección `evaluaciones:`
en `plataforma.yml`. **Tests**: nuevos `EvaluacionCasosTests.cs`, `EvaluacionCorridaTests.cs`,
`EvaluacionCalificacionTests.cs`, `EvaluacionGateTests.cs` e `Infra/EntornoM8.cs`; ajustados `NucleoTests.cs` y
`ConstructorContextoTests.cs` (el gate nuevo), `Infra/TestServicios.cs` (precio del revisor).
**Repo**: `docs/diseno-organizacion-roles-reglas.md` (M8 ✅) y `PLAN-IMPLEMENTACION.md` (Fase 2).

### Decisiones de implementacion M8 (ambigüedades resueltas)
- **DI-M8-1 El refactor del render salió byte a byte (RT-M8-01, plan B NO usado):** se extrajo
  `ConstructorContexto.Renderizar(ContenidoContexto, formato)` con el mismo código, sin reordenar ni reformatear.
  `ArmarAsync` y `ArmarPlataformaAsync` pasan a leer de la base y llamar al render; los formatos de plataforma (3 y 4)
  llegan con listas vacías de instrucciones y reglas y salen con un solo bloque, igual que antes. **Los 4 goldens
  (formatos 1, 2, 3 y 4) quedaron verdes en la misma corrida**, y el test nuevo "contexto de caso sin reglas = contexto
  de tarea equivalente" cierra la pinza por el otro lado.
- **DI-M8-2 Salidas estructuradas: SÍ existen en el SDK .NET.** Verificado por compilación contra `Anthropic` 12.47.0:
  `MessageCreateParams.OutputConfig` → `OutputConfig.Format` (`JsonOutputFormat`) → `JsonOutputFormat.Schema`
  (`IReadOnlyDictionary<string, JsonElement>`, **required**). Se agregó `SolicitudModelo.EsquemaSalida` (opcional, null
  en todo el resto del motor) y su mapeo en `ProveedorModeloAnthropic`. **Igual se valida el texto con JSON estricto**:
  un proveedor que no lo soporte (el simulado, el guionado) no puede colar un veredicto que no se entiende.
- **DI-M8-3 El simulador reconoce la evaluación por un marcador propio (lección RT-M7-06):** `SolicitudModelo.Guion`
  (`GuionEvaluacion`) lo pone el ejecutor y lleva la clave del caso, su `RespuestaSimulada` y qué herramientas tienen
  resultado fijo. Nunca se adivina por los nombres de las herramientas. El revisor simulado se reconoce por
  `EsquemaSalida`.
- **DI-M8-4 El gate vive en un solo método:** `VersionadoService.MotivoNoPublicableAsync` devuelve el texto exacto del
  botón deshabilitado y **es el mismo que llama `PublicarAsync`**. `IGateEvaluacion` lo expone a la Web y se registra
  como el propio `VersionadoService` (no hay dos implementaciones que se puedan desincronizar).
- **DI-M8-5 `RequireSuperUsuario` ya existía** (RT-M8-13 resuelto sin cambios): estaba en `Program.cs` desde el
  template. No se tocó `RequireAdministracion` ni el acceso de nadie.
- **DI-M8-6 Dos tests viejos se adaptaron a propósito (CA-M8-16):** `NucleoTests.Evaluar_y_publicar...` y
  `ConstructorContextoTests.Reglas_de_plataforma...` publicaban un Agente y una Regla de plataforma con evaluación
  manual. Con el gate eso ya no alcanza: ahora registran la **excepción de SuperUsuario**, que es el camino real
  mientras esos artefactos no tengan casos. No es una regresión: es la conducta nueva.
- **DI-M8-7 El ejecutor nunca resuelve herramientas:** solo `IRegistroHerramientas.Definiciones(nombres)`. El test usa
  `RegistroHerramientasQueFalla`, que lanza si alguien llama `Obtener`. Los nombres salen del contexto del caso o, si no
  los declara, del frontmatter del artefacto.
- **DI-M8-8 Continuar suma al tope, no lo reemplaza:** `TopeUsd = CostoUsd + tope nuevo`, así "seguí hasta USD 5 más"
  significa lo que dice y los casos ya guardados no se vuelven a correr (se cuentan las llamadas del doble en el test).
- **DI-M8-9 La organización interna se siembra por dos caminos:** `InsertData` por SQL en la migración (idempotente,
  con `WHERE NOT EXISTS` para no chocar con el único de `Slug`) y `SeedData.AsegurarOrganizacionInternaAsync` para bases
  creadas con `EnsureCreated`. El `Down` la borra; si ya tiene `EventoUso`, la FK Restrict hace fallar el DELETE **a
  propósito**.
- **DI-M8-10 Un caso a medio correr no cuenta como fallado:** si tiene menos repeticiones que las esperadas y todas
  pasaron, queda **Pendiente** (no "Falló"). Si no, una corrida cortada por tope mostraría fallas que no ocurrieron.
- **DI-M8-11 La consola Admin se identifica como SuperUsuario explícitamente** (`ConsolaComoSuperUsuario`), y solo en
  los verbos que lo necesitan: los servicios re-verifican el rol con `IContextoUsuario` y no confían en el llamador.
- **DI-M8-12 `publicar-rubro --aprobacion-manual` ahora registra excepciones** en los tipos con gate, y avisa cuántas
  antes de hacerlo. Los demás tipos siguen con evaluación manual común.

### Migraciones EF generadas M8
- `20260916022048_EvaluacionAutomaticaM8` — `CreateTable` de `ConjuntosCasos`, `VersionesConjuntoCasos`,
  `CasosEvaluacion`, `CorridasEvaluacion` y `ResultadosCaso` con sus únicos, índices y FKs Restrict; `AddColumn` en
  `EvaluacionesVersion` (`CorridaEvaluacionId`, `EsExcepcion` default 0, `RegistradaPorUsuarioId`, `HashCasos`) e índice
  `(ArtefactoVersionId, EjecutadaAt)`; `AddColumn Tenants.EsInterna` (default 0) e `INSERT` idempotente de la
  organización técnica `olvidata-interno`. `Down` en orden inverso. **Sin cambios en `TareasAgente`, `PasosTarea` ni
  nada del motor de clientes.**
- **Corrección a mano del scaffold:** EF generaba `DropIndex(IX_EvaluacionesVersion_ArtefactoVersionId)` **antes** de
  crear el compuesto y MySQL lo rechaza (*"Cannot drop index: needed in a foreign key constraint"*, 1553). Se invirtió el
  orden: primero se crea `(ArtefactoVersionId, EjecutadaAt)` —que sostiene la FK igual, por ser la primera columna— y
  recién después se borra el simple. En el `Down`, lo mismo al revés.
- **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-16**, luego `database update AsignacionesAsistenteM7b`
  (Down OK, borra la organización interna) y `database update` otra vez (la recrea); `has-pending-model-changes` limpio.
- Verificado por SQL (`scratchpad/verificar-m8.sql` y `verificar-m8b.sql`, transacción revertida): `decimal(18,6)` en los
  3 campos de plata y los 6 decimales se guardan; `longtext` en pedidos, contextos, respuestas y JSON; **1062 real** en
  `(VersionConjuntoCasosId, Clave)` y en `(CorridaEvaluacionId, CasoEvaluacionId, Repeticion)`; los 4 índices de
  `CorridasEvaluacion` y los 2 de `ResultadosCaso` presentes; organización interna única con `EsInterna = 1` y sin
  límite de gasto; `EXPLAIN` del gasto del mes usa `IX_CorridasEvaluacion_Modo_Periodo` (`ref`), el del gate usa
  `IX_EvaluacionesVersion_ArtefactoVersionId_EjecutadaAt` (`Backward index scan; Using index`) y el de los resultados de
  una corrida usa su índice (`ref`); el del reclamo lista `(Estado, LeaseHasta)` en `possible_keys` (con la tabla vacía
  el optimizador prefiere el PK del `ORDER BY`). **0 restos** tras el ROLLBACK.
- **Importación real verificada**: `importar plataforma.yml` creó 4 conjuntos y 15 casos; reimportar sin cambios da
  "4 sin cambios"; `evaluacion-casos 65` lista 8 casos (3 propios + 5 de la suite común) y `evaluacion-estimar 65` da
  USD 0,91 esperado / USD 6,16 peor caso. **Ninguna corrida creada y ningún `EventoUso` de canal 4**: no se llamó a
  Anthropic.

### Evidencia de build y tests M8
- `dotnet build OlvidataAgentes.slnx`: **0 errores, 0 advertencias** (desapareció hasta la CS0114 preexistente de
  `HomeController`, que sigue igual pero ya no se reporta en esta corrida).
- `dotnet test tests/OlvidataAgentes.Tests`: **287 OK / 0 fallidos** (244 previos + 43 nuevos).
- **Los 4 goldens de hash de contexto (formatos 1, 2, 3 y 4) intactos** después del refactor del render.
- Lecciones: (1) MySQL no deja borrar el índice que sostiene una FK: al reemplazar un índice simple por uno compuesto
  con la misma primera columna, **crear el nuevo antes de borrar el viejo**; (2) YAML plano no admite `:` dentro del
  valor (`nombre: Solo propone: ...` revienta): hay que comillarlo, y el importador lo reporta con el nombre del
  archivo; (3) con el entorno de tests en "Testing", todo lo que depende de `IsDevelopment()` queda cortado: el entorno
  de pruebas de M8 registra un `IHostEnvironment` de Development salvo en el test que justamente verifica el corte.

### Riesgos residuales M8
- **Ninguna corrida real se ejecutó todavía** (S-M8-01, PA-01/PA-13/PA-14): la primera con costo la mira Joaquín, con
  tope de USD 1, sobre el configurador (#65) o una regla de plataforma. Hasta entonces la calidad del revisor, el
  costo real y los umbrales son estimaciones.
- Los **casos iniciales son un borrador sin revisar** (PA-17): están en `nucleo/plataforma/evaluaciones/` e importados
  en dev, pero nadie validó todavía si prueban lo correcto ni si los criterios del revisor están bien redactados.
- **La estimación de costo usa 3 caracteres por token**: es una aproximación conservadora, no un cálculo. Lo que
  gobierna de verdad es el tope, que se verifica contra el costo REAL antes de cada llamada.
- **Un corte entre la llamada pagada y su `SaveChanges` pierde el registro de UNA llamada** (RT-M8-06): es el techo del
  error conocido y documentado.
- El *polling* de la corrida es cada 3 s mientras no termina, con corte a los 5 minutos sin avance (R-M8-12).
- `CorrerPruebas` arma la estimación con un contexto de muestra: si el artefacto no tiene casos o falta una versión del
  núcleo, cae a 2000 tokens estimados.
- Verificación visual pendiente (QA): card de pruebas, pantalla de casos, corrida con avance y filtros, detalle de caso,
  bloques de texto hostil, gate y modal de excepción, listado con gasto del mes, mobile 390 y ambos temas.

### Proximos pasos pendientes M8
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M8).
- PA-17: que Joaquín revise los 15 casos iniciales de `nucleo/plataforma/evaluaciones/` antes de la primera corrida real.
- PA-01 / PA-13 / PA-14: correr, aprobar y publicar las 3 reglas de plataforma, el configurador y el asistente.
- M8b (P1): evaluación de agentes de la organización — el objetivo de la corrida quedó desacoplado para que solo haya
  que agregar un origen, sin migrar datos.
- Deuda fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9; advertencia CS0114 de `HomeController`.

---
# M6 — Aprobaciones de acciones por rol y límites de gasto

Estado: **implementada 2026-09-15, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M6 (P1–P16), `2-disenador-funcional.md` M6 (D-M6-1..16) y `3-arquitecto-mvc.md` M6, aprobados sin gate por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. **Continuación**: una corrida anterior del implementador se cortó por límite de uso; dejó el backend compilando (Domain, Application, Infrastructure, migración generada sin aplicar, simulador, demostraciones, worker) y faltaban Web, tests, aplicar y verificar la migración y la documentación. Sin llamadas a Anthropic, sin commits.

### Escaneo de reutilizacion M6
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M1 (`EsperandoAprobacion`, `RequiereAprobacion`, `EjecucionHerramienta` único por `ToolUseId`, `GuardarAsync` con `Version`) | Espera y resolución sin paso nuevo; idempotencia al reanudar | Literal (extensión) |
| Template M3b/M4b (`MarcarFinAsync` con cierre de turno, `ResolverUsuarioAsync`, `_TarjetasPropuesta`/`_ScriptPropuestas`, simulador con guion) | Turno frenado por límite, autor re-verificado, tarjeta bajo el turno con acciones por delegación, `GuionAprobaciones` | Literal (patrón del mismo repo) |
| Template M2/M5 (`FiltrosSesion`, `DataTableRequestHelper`, `RespuestasServicio`, barra de espacio y tokens de color DI-M5-17, `.ov-enlace-accion`) | Bandeja, columna de Miembros, barras de gasto y estados con contraste | Literal |
| verif-m5 (scratchpad) | Verificador EF → MySQL con organización de prueba y limpieza | Literal (adaptado a M6, `scratchpad/verif-m6`) |
| crm-olvidata (cortes de gasto con motivo) | Criterio de `EvaluarAsync` con motivo antes de cada llamada | Patrón |
| PAT-034 / PAT-035 | Completados con rutas reales de código y lecciones (`pendiente_verificar: false` en las rutas propias) | Confirmado |

### Archivos y capas modificadas M6
**Domain** — Nuevos: `Enums/EnumsAprobacionesGasto.cs` (`NivelAprobacion`, `EstadoAprobacion`, `AmbitoGasto`), `Entities/GastoAprobaciones.cs` (`LimiteGastoMiembro`, `AvisoGasto`, `AprobacionAccion`). Modificado: `Entities/Tenant.cs` (`LimiteMensualUsd`).

**Application** — Nuevos: `Settings/GastoAprobacionesOptions.cs` (`GastoOptions`, `AprobacionesOptions`), `Helpers/PeriodoGasto.cs`, `Helpers/DatosAccionHelper.cs`, `DTOs/GastoDtos.cs` (`EstadoGastoDto`, `BarraGastoDto`, `ConsumoDto`, `MensajesGasto`…), `DTOs/AprobacionesDtos.cs` (`AprobacionDto`, `AprobacionListItemDto`, `AprobacionFiltros`, `MensajesAprobaciones`), `Interfaces/IGastoAprobaciones.cs` (`IControlGasto`, `IConsumoService`, `IAprobacionService`). Modificados: `Motor/IMotorAgentes.cs` (`IHerramientaConAprobacion`, `NombresHerramientasDemostracion`, `MotivoNoPuedeSeguir.EsperandoAprobacion/LimiteGasto`, `TareaDetalleDto.AprobacionesPorPaso/EsperaAprobacionTexto/AvisoGasto/AprobacionesDelTurno`), `Interfaces/IPermisosOrganizacion.cs` (4 permisos), `DTOs/OrganizacionDtos.cs` (filtro y columna de límite en Miembros).

**Infrastructure** — Nuevos: `Services/Gasto/{ControlGasto, ConsumoService}.cs`, `Services/Aprobaciones/AprobacionService.cs`, `Services/Motor/HerramientasDemostracion.cs`, `Data/Configurations/GastoAprobacionesConfigurations.cs`, migración `Data/Migrations/20260915154528_AprobacionesYGastoM6.cs` (+ Designer y snapshot). Modificados: `Data/AppDbContext.cs` (DbSets; avisos y pedidos fuera del audit trail), `Data/Configurations/AgentesConfigurations.cs` (precisión del límite, índice `PasosTarea (TenantId, CreadoAt)`), `Services/Motor/ProcesadorTareas.cs` (gasto antes de cada llamada, avisos tras paso con costo, pedidos + espera en un guardado, ejecución según resolución, unión de demostraciones), `Services/Motor/ServicioTareas.cs` (bloqueo en crear/configurar/ajustar, ajuste bloqueado en espera, cancelar pedidos, detalle con tarjetas, motivo y aviso), `Services/Motor/MotorAgentesWorker.cs` (barrido de vencidos), `Services/Motor/ProveedorModeloSimulado.cs` (`GuionAprobaciones`), `Services/Organizacion/{PermisosOrganizacion, MiembroService}.cs`, `DependencyInjection.cs`.

**Web** — Nuevos: `Controllers/{ConsumoController, AprobacionesController}.cs`, `ViewComponents/ContadorAprobacionesViewComponent.cs`, `Helpers/{GastoTextos, ConsumoTextos}.cs`, `Models/GastoAprobacionesViewModels.cs`, vistas `Consumo/{Index, _BarraGasto, _TablasConsumo, _TablaGrupo, _ModalLimite}`, `Aprobaciones/Index`, `Tareas/{_TarjetasAprobacion, _ScriptAprobaciones}`, `Shared/{_AvisoGasto, Components/ContadorAprobaciones/Default}`. Modificados: `Controllers/{AgentesController, ConfiguracionReglasController, MiembrosController, ClientesController (límite por defecto al crear, card, `CambiarLimiteGasto`, `Consumo`), UsoController}.cs`, `Models/{AgentesViewModels, ConfiguradorViewModels}.cs`, vistas `Shared/_Layout` (menú Aprobaciones con contador y Consumo), `Tareas/{Detalle, _Conversacion, _CuadroSeguimiento, _EstadoTarea, Index}`, `Agentes/Ejecutar`, `ConfiguracionReglas/Nueva`, `Miembros/Index`, `Clientes/Details`, `Uso/Index`, `wwwroot/css/site.css`, `appsettings.json` (secciones `Gasto` y `Aprobaciones`).

**Admin**: `tenant-crear` con el límite por defecto. **Tests**: nuevos `GastoTests.cs` (9), `AprobacionesTests.cs` (17 casos) e `Infra/DoblesM6.cs` (`EntornoM6`, campana de prueba, herramientas de prueba). **Repo**: `docs/diseno-organizacion-roles-reglas.md` (M6 ✅).

### Decisiones de implementacion M6 (ambigüedades resueltas)
- **DI-M6-1 Continuación:** se conservó todo lo del intento anterior (revisado contra la arquitectura y compilando); correcciones: la migración no tenía el `UPDATE Tenants SET LimiteMensualUsd = 100.00` exigido → agregado, `Down` a M5 y `Up` de nuevo en dev; faltaban toda la capa Web, los tests y la documentación.
- **DI-M6-2 Tarjetas sin endpoint propio:** en lugar de `Aprobaciones/Tarjetas` la tarjeta se refresca con `Tareas/Progreso` (el mismo fragmento de la conversación); al aprobar o rechazar se reinicia el seguimiento en vivo (`ovAlResolverAprobacion`) porque la tarea vuelve a la cola.
- **DI-M6-3 Confirmación:** la tarjeta aprueba directo y la bandeja pide SweetAlert2 (`data-confirmar-aprobar`, D-M6-11); rechazar con textarea, contador y validación de 500 caracteres (D-M6-10); resultado "ya resuelto" (`datos.codigo = "YaResuelto"`) refresca.
- **DI-M6-4 Montos:** los límites viajan como texto y se interpretan con `BusquedaHelper.TryParseImporte` (formato argentino "20,50"); mayor a cero, dos decimales, tope y rango los valida el servicio.
- **DI-M6-5 Límite efectivo:** si el límite propio supera al de la empresa, rige el de la empresa como límite del miembro y el bloqueo puede ser "por miembro" aunque la empresa no haya llegado (el mensaje cita el efectivo).
- **DI-M6-6 Cuadro de seguimiento:** "espera aprobación" y "límite de gasto" reemplazan el cuadro con una alerta (mismo patrón que máximo de ajustes y suscripción); el aviso ámbar va dentro del cuadro.
- **DI-M6-7 Estado en palabras:** junto al badge del encabezado de la conversación y en el turno activo con ícono de mano en lugar de spinner.
- **DI-M6-8 Contraste (PA-11):** el badge "Espera aprobación" pasó a `bg-warning text-dark` en `_EstadoTarea` y en la grilla de Tareas (blanco sobre amarillo daba 1,6:1). Barras: verde #15803d / ámbar #b45309 / rojo #b91c1c en claro y #22c55e / #f59e0b / #ef4444 en oscuro; textos de estado con los tokens de DI-M5-17; contador rojo #b91c1c con blanco (6,5:1).
- **DI-M6-9 Bandeja:** un filtro por columna visible por pestaña (Pendientes: Pedido, Tarea, Qué quiere hacer, Pedida por —solo Director—, Cliente, Quién aprueba, Vence; Historial: Pedido, Tarea, Qué quiso hacer, Pedida por, Resultado, Resuelta por, Fecha, Motivo), Session por pestaña; "Vence" muestra relativo + fecha (la búsqueda global encuentra la fecha); columnas secundarias ocultas en mobile.
- **DI-M6-10 Consumo:** cards de agrupaciones con `_TablaGrupo`; buscador del lado del cliente en "Por miembro"; en mobile área y límite bajo el nombre; staff ve la misma vista con breadcrumb y sin "Cambiar límite".
- **DI-M6-11 Miembros:** filtro "Límite del mes" (con límite propio / el de la empresa) además de la columna, con enlace a Consumo; con clave propia "No aplica".
- **DI-M6-12 Mensajes del backoffice:** el aviso de miembros por encima va en `SuccessMessage` (el layout solo muestra Success y Error).
- **DI-M6-13 Uso y consumo:** columnas "Este mes" y "Límite" en las organizaciones del resumen del período (las que tuvieron uso); el nombre lleva al consumo de la organización.
- **DI-M6-14 Alta de organizaciones:** `Clientes/Create` y `tenant-crear` asignan el límite por defecto también con clave propia (no aplica mientras sea propia).
- **DI-M6-15 Tests:** `EntornoM6` sobre `EntornoReglas` con campana de prueba y tres herramientas (`pago_real` con efecto en base y nivel autor, `sin_nivel` sin `IHerramientaConAprobacion`, `nota_libre` sin aprobación); el consumo se siembra en tareas marcadas Completadas para que el worker no las reclame.

### Migraciones EF generadas M6
- `20260915154528_AprobacionesYGastoM6` — generada por la corrida anterior sin aplicar (`migrations list`: Pending; snapshot consistente). **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-15**, luego `database update WorkspaceClientesM5` (Down OK: tablas, índice y columna fuera) y `database update` otra vez con el `UPDATE` agregado; `has-pending-model-changes` limpio.
- Verificado por SQL (`scratchpad/verificar-m6.sql`, transacción revertida): `decimal(10,2)` en ambos límites (12,345 → 12,35), 2/2 organizaciones con USD 100; índices únicos `(TareaAgenteId, ToolUseId)`, `(TenantId, Periodo, Ambito, UsuarioId, Umbral)` y `(TenantId, UsuarioId)` con **1062 real** (incluido `UsuarioId` vacío); tokens 1 fila / 0 filas; `EXPLAIN` del contador usa `IX_AprobacionesAccion_TenantId_Estado_VenceAt` (index) y el SUM del miembro usa índices (ref); **el SUM de la organización hizo full scan con 139 pasos** (el optimizador descarta el índice con tan pocas filas; revisar con volumen, RT-M6-05); 0 restos.
- Verificado EF → MySQL real (`scratchpad/verif-m6`, modelo falso, sin Anthropic): **64 pasos OK, 0 fallas, 0 restos**. Evaluar (SUM mensual y join por autor), bloqueo con mensaje, avisos una sola vez y 1062 real; consumo por rol con las 4 agrupaciones, mes anterior, staff (`GroupBy` + `SUM` a diccionario); límites con token, 1062 y **`DbUpdateConcurrencyException` real**; Miembros con filtro, orden y búsqueda por límite; bandeja con 6 órdenes, 7 búsquedas globales (texto, autor con subconsulta, cliente, `#tarea`, fecha, nivel, "sin cliente"), filtros combinados y opciones `Distinct`; aprobar con otro pendiente del paso (`Contains` en MySQL), Empleado sin permiso de nivel Director, rechazar el último → cola con `Intentos = 0`, ya resuelto con nombre, historial con 4 órdenes, búsqueda y filtros; token real y 1062 real en pedidos; barrido de vencidos; cancelar tarea en espera cancela pedidos; **motor real**: pedido + espera en un guardado sin ejecución, aprobar, ejecutar una vez y completar. La primera corrida falló solo en la limpieza (`Notifications` no tiene FK a usuarios); restos borrados por SQL y verificador corregido y corrido de nuevo.
- Impacto: 3 tablas nuevas vacías, columna nueva con USD 100 en las organizaciones existentes, índice nuevo en `PasosTarea`.

### Evidencia de build y tests M6
- `dotnet build OlvidataAgentes.slnx`: 0 errores.
- `dotnet test tests/OlvidataAgentes.Tests`: **185 OK / 0 fallidos** (159 existentes + 26 nuevos); golden de hash de formatos 1, 2 y 3 verdes sin cambios.
- Lecciones: (1) el primer fallo fue un dato del propio test (límite efectivo bloquea por miembro), no del código; (2) InMemory aplica tokens de concurrencia pero no índices únicos: 1062 solo en MySQL; (3) el verificador EF no debe asumir FK en tablas del template (`Notifications.UserId` sin FK).

### Riesgos residuales M6
- RT-M6-05: SUM mensual con full scan a bajo volumen; si crece, acumulado mensual en el mismo commit del paso.
- RT-M6-06: una notificación que falla después del commit queda sin reintento (aviso registrado, logueado).
- RT-M6-07: el vencimiento depende del worker (`MotorAgentes:Habilitado`); resolver un vencido igual lo marca vencido.
- RT-M6-12: el contador hace un `COUNT` en cada request con menú.
- Con el simulador el costo es cero: los avisos del 80 % no se ven sin sembrar costo (guía de QA).
- Todavía no existen herramientas reales con aprobación (solo demostraciones); la descripción y el nivel los define cada herramienta futura.
- Verificación visual pendiente (QA): barras y umbrales, modal de límite, tarjetas, bandeja con contador y filtros, dos aprobadores, mobile 390 y ambos temas.

### Proximos pasos pendientes M6
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M6).
- Deuda fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9; referencia de crm-olvidata en PAT-035 sin verificar (antecedente externo).

---
# M5 — Workspace por cliente de cartera

Estado: **implementada 2026-09-15, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M5 (P1–P14), `2-disenador-funcional.md` M5 (D-M5-1..14) y `3-arquitecto-mvc.md` M5, aprobados sin gate por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. Sin contenido de rubros, sin llamadas a Anthropic, sin commits (los hace el orquestador tras QA).

### Escaneo de reutilizacion M5
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M1/M4b (`IHerramientaAgente`, idempotencia por `ToolUseId`, `ContextoHerramienta` con defaults, lectores de entrada de `HerramientasConfigurador`) | Tres herramientas de solo lectura sin `SaveChanges`; `ContextoHerramienta.ClienteCarteraId` | Literal (extensión) |
| Template M2/M4 (`NombreVigente` STORED por SQL + índice único, `FiltrosSesion`/`DataTableRequestHelper`/`RespuestasServicio`, bajas AJAX PAT-015) | Nombre único con baja lógica, grillas de miembro y de staff, renombrar/baja por AJAX | Literal |
| Template M3/M3b (`ReconstruirConversacion`, `EnviarSeguimientoAsync` con `Version`, `_PasosTurno`, `ProveedorModeloSimulado`) | Nota de adjuntos en los mensajes (sistema y hash intactos), adjuntos en el mismo guardado del ajuste, guion de documentos | Literal (extensión) |
| Template (ClosedXML, QuestPDF) | Lectura de .xlsx; QuestPDF como generador de fixtures en tests | Literal |
| vinosefue PAT-002 | Criterio de validación en servidor (extensiones, tamaño); su almacenamiento público descartado | Patrón |
| ganaderia `Ganaderia.Infrastructure/Services/Ganaderia/LocalComprobanteStorageService.cs` (ruta verificada) | Almacén local fuera de `wwwroot` con endpoint autenticado | Patrón |
| koi PAT-012 | Extractores como clases puras probadas con archivos generados | Patrón |
| PAT-033 | Completado con rutas reales de código y lecciones (`pendiente_verificar: false`, incluida la de ganaderia) | Confirmado |

### Archivos y capas modificadas M5
**Domain**
- Nuevos: `Enums/EnumsDocumentos.cs` (`TipoDocumento`, `EstadoLecturaDocumento`), `Entities/DocumentoCartera.cs` (`DocumentoCartera` + `DocumentoCarteraParte`), `Entities/AdjuntoMensajeTarea.cs`.
- Modificado: `Entities/Uso.cs` (se elimina `DocumentoCliente`, P1).

**Application**
- Nuevos: `Settings/DocumentosOptions.cs`, `Helpers/NombreDocumentoHelper.cs` (+ `TiposArchivoDocumento`), `DTOs/DocumentosDtos.cs` (`MensajesDocumentos` y DTOs), `Interfaces/IDocumentoCarteraService.cs`, `Interfaces/IAlmacenDocumentos.cs` (+ `ILectorDocumentos` y DTOs de lectura), `Motor/NotaAdjuntos.cs` (+ `NombresHerramientasDocumentos`).
- Modificado: `Motor/IMotorAgentes.cs` (`ContextoHerramienta.ClienteCarteraId`, `CrearTareaDto.DocumentoIds`, `PasoVisibleDto.Resumenes` + `ResumenHerramientaDto`, `MensajePersonaDto.Adjuntos` + `AdjuntoMensajeDto`, `TareaDetalleDto.PuedeAdjuntar/MaxAdjuntosPorMensaje`, sobrecarga `IServicioTareas.EnviarSeguimientoAsync(..., documentoIds, ct)`).

**Infrastructure**
- Nuevos: `Services/Documentos/{AlmacenDocumentosDisco, ValidadorContenidoArchivo, LectorDocumentos, DocumentoCarteraService, HerramientasDocumentos}.cs`, `Services/Documentos/Extractores/{ComunesExtraccion, ExtractorPdf, ExtractorWord, ExtractorPlanilla, ExtractorCsv, ExtractorTexto}.cs`, `Data/Configurations/DocumentosConfigurations.cs`, migración `Data/Migrations/20260915135646_WorkspaceClientesM5.cs` (+ Designer y snapshot).
- Modificados: `Data/AppDbContext.cs` (DbSets; partes y adjuntos fuera del audit trail), `Data/Configurations/AgentesConfigurations.cs` (sin `DocumentoClienteConfiguration`), `Services/Motor/ProcesadorTareas.cs` (unión de herramientas de documentos en tareas de trabajo con cliente, contexto con cliente, adjuntos → `ReconstruirConversacion(entrada, pasos, adjuntos)`), `Services/Motor/ServicioTareas.cs` (adjuntos en `CrearAsync` y en el ajuste en el mismo guardado, chips y resúmenes llanos en `ObtenerDetalleAsync`, `PuedeAdjuntar`), `Services/Motor/ProveedorModeloSimulado.cs` (guion de documentos; la nota no cuenta como turno), `DependencyInjection.cs`, `OlvidataAgentes.Infrastructure.csproj` (`PdfPig` 0.1.16, `DocumentFormat.OpenXml` 3.1.1 explícito).

**Web**
- Nuevos: `Controllers/DocumentosController.cs`, `Helpers/DocumentosTextos.cs`, `Models/DocumentosViewModels.cs`, vistas `Documentos/{Index, Ver, _Parte, _ZonaSubida, _VistaPreviaDocumentos, _ScriptAccionesDocumento}`, `Shared/_ModalDocumentos`, `Cartera/_CardDocumentos`, `Clientes/Documentos`, `wwwroot/js/documentos.js` (cola de subida + modal subir/elegir).
- Modificados: `Controllers/{CarteraController (card), AgentesController (documentos, vista previa y adjuntos al crear), TareasController (ajuste con adjuntos), ClientesController (card y grilla de staff)}.cs`, `Models/{AgentesViewModels (EjecutarAgenteViewModel, ClienteDetalleViewModel), TareasViewModels (SeguimientoViewModel)}.cs`, vistas `Cartera/Detalle`, `Agentes/Ejecutar`, `Tareas/{Detalle, _Conversacion, _CuadroSeguimiento, _PasosTurno}`, `Clientes/Details`, `wwwroot/css/site.css`, `appsettings.json` (sección `Documentos`).

**Admin**: comando `documentos-limpiar [--raiz <carpeta>] [--aplicar]`. **Tests**: nuevos `LectorDocumentosTests.cs`, `DocumentosTests.cs` (+ `EntornoDocumentos`), `HerramientasDocumentosTests.cs` (46 casos); ajustados `TenantIsolationTests.cs` y `MotorAgentesTests.cs` (efecto genérico con `ClienteCartera` en lugar de `DocumentoCliente`). **Repo**: `.gitignore` (`**/App_Data/documentos/`, verificado con `git check-ignore`), `PLAN-IMPLEMENTACION.md` (Fase 2: workspace ✅), `docs/diseno-organizacion-roles-reglas.md` (M5 ✅).

### Decisiones de implementacion M5 (ambigüedades resueltas)
- **DI-M5-1 Paquete PdfPig:** el id NuGet oficial es `PdfPig` (mismo proyecto, namespace `UglyToad.PdfPig`, Apache-2.0); `UglyToad.PdfPig` solo conserva un prerelease viejo. `DocumentFormat.OpenXml` 3.1.1 = la que ya resolvía ClosedXML.
- **DI-M5-2 Contratos:** `ILectorDocumentos.Detectar` sincrónico que devuelve tipo + extensión + MIME del servidor; `GuardarTemporalAsync` calcula SHA-256 en streaming y corta al pasar el máximo (el largo del navegador puede mentir); `DarDeBajaAsync(id, version?)`; `EnviarSeguimientoAsync` con adjuntos como sobrecarga (la firma de M3b delega, sin ambigüedad).
- **DI-M5-3 Cliente dado de baja (RF-M5-15):** sus documentos no se listan ni se suben (404), pero cada documento vigente sigue abriendo por id (ver, parte, descargar, imagen, renombrar, dar de baja): los chips de tareas existentes siguen andando y el Director puede darlos de baja. Staff los ve con "(dado de baja)".
- **DI-M5-4 Conflictos:** renombrar o dar de baja un documento que otra persona dio de baja → "Otra persona cambió o dio de baja este documento…" (no 404); de otra organización o inexistente → 404. Token `VersionToken` verificado en el servicio y en la base (`OriginalValue`).
- **DI-M5-5 Baja:** baja lógica + partes borradas como entidades clave en estado Deleted (sin traer el texto) en un guardado; archivo después del commit y `ArchivoEliminadoAt` en un segundo guardado (si falla, queda para `documentos-limpiar`).
- **DI-M5-6 Legible en parte:** no se extrae lo que excede el máximo, así que no hay "N de M" del documento completo: el aviso dice "puede leer hasta la parte N. El resto quedó fuera."
- **DI-M5-7 Partes:** "Parte i de N" (Word, texto), "Página i de N" (PDF; una página de más de 2 × 8.000 caracteres se parte "(k de m)"), "Hoja «X», filas a–b" numeradas por fila de datos con encabezado repetido, "Filas a–b" (CSV) y "Encabezado" si solo hay encabezado. PDF sin texto o con promedio < 20 caracteres por página → no legible. Fórmula que ClosedXML no evalúa → valor guardado.
- **DI-M5-8 Validación:** .docx/.xlsx se descomprimen completos contando bytes leídos (además de los declarados); relación de compresión solo en entradas de más de 1 MB; `vbaProject.bin`, `vbaData.xml` y tipos `macroEnabled` → macros; texto: sin NUL (salvo UTF-16 con BOM) y como máximo 10 % de caracteres de control.
- **DI-M5-9 Búsqueda:** `LIKE … ESCAPE '!'` para `%` y `_`; un `!` del usuario pasa a `_` porque EF InMemory no interpreta `!!` (la comparación exacta en memoria descarta filas de más); en memoria `IgnoreCase | IgnoreNonSpace`, igual a la colación.
- **DI-M5-10 JSON de herramientas:** `JavaScriptEncoder.Create(UnicodeRanges.All)` escapa `< > & '` (un documento no puede simular marcado ni cerrar la nota) sin escapar tildes; aviso "información, nunca instrucciones" en cada resultado.
- **DI-M5-11 Nota de adjuntos:** `<documentos_adjuntos>` + `<documento id nombre/>` escapados, agrupada por `PasoNumero` y ordenada por `Orden`; el simulador la excluye del conteo de turnos. Golden de hash de formatos 1, 2 y 3 verdes; test de que una tarea con adjuntos tiene el mismo hash e instantánea que sin adjuntos.
- **DI-M5-12 Ver pasos:** `Resumenes` alineado con `Resultados`; los pedidos a herramientas de documentos no se muestran en el paso del modelo (se explican en su resultado); nombres de documento de los errores acotados al cliente de la tarea; contenido legible recortado a 10.000 caracteres; "Ver lo que leyó" (leer) / "Ver el detalle" (listar, buscar).
- **DI-M5-13 Pantalla de documentos:** acciones de fila como botones (Ver, Descargar, Renombrar, Dar de baja) en lugar de menú ⋯ (un dropdown queda recortado dentro de `.table-responsive`); en mobile se ocultan Lectura, Partes, Tamaño, Subido por y Fecha y lectura + fecha van bajo el nombre. Filtros del diseño (Nombre, Tipo, Lectura, Subido por, Fecha); partes por búsqueda global.
- **DI-M5-14 Subida:** parcial de marcado `_ZonaSubida` + `wwwroot/js/documentos.js` (en vez de un parcial de script); límite de request 30.000.000 bytes (tope por defecto de IIS) para que un archivo de 25 MB llegue y reciba el mensaje de tamaño.
- **DI-M5-15 Nueva tarea:** si el envío falla, la selección conserva los vigentes del cliente; "Subir un documento" deja elegidos los subidos (hasta el máximo); staff sin campo de documentos.
- **DI-M5-16 Staff:** la grilla ignora Tenant y SoftDelete en la raíz con `TenantId` y `DeletedAt` explícitos sobre los documentos (nombres de clientes dados de baja en la misma consulta); solo metadatos.
- **DI-M5-17 Contraste (lecciones OLV-001..004):** estados en claro verde #15803d (5,0), ámbar #92400e (7,1), gris `--ov-gray-600` (7,6), rojo #b91c1c (6,5); en oscuro #86efac (10,3), #fcd34d (10,1), `--ov-text-muted` (5,7), #fca5a5 (7,6) sobre #1e293b. Enlaces nuevos `.ov-enlace-accion` #1a78b8 (4,7) y marca en oscuro (4,9). SweetAlert2 de documentos con confirmar #1a78b8 y peligro #dc2626.
- **DI-M5-18 Audit trail:** `DocumentoCarteraParte` y `AdjuntoMensajeTarea` fuera (texto confidencial y registro inmutable); `DocumentoCartera` se audita sin contenido.
- **DI-M5-19 `documentos-limpiar`:** ignora todo lo modificado en la última hora (una subida en curso nunca se toca) y cualquier nombre que no sea carpeta entera + GUID; acepta `--raiz` (la raíz relativa del Admin sería su carpeta de binarios).

### Migraciones EF generadas M5
- `20260915135646_WorkspaceClientesM5` — **aplicada en `olvidata_agentes_dev` (MySQL 8.0.29) el 2026-09-15** con `dotnet ef database update`; `has-pending-model-changes` limpio. `DocumentosCliente` tenía 0 filas (verificado antes). Ajuste manual: `NombreVigente` quitada del `CreateTable` (el proveedor la creaba VIRTUAL) y agregada con `ALTER TABLE … GENERATED ALWAYS AS (CASE WHEN DeletedAt IS NULL THEN Nombre END) STORED` antes de su índice único. `Down` vuelve a crear `DocumentosCliente` vacía.
- Verificado por SQL (`scratchpad/verif-workspacem5.sql`): `DocumentosCliente` eliminada; `NombreVigente` STORED GENERATED; `HashSha256` char(64), `ArchivoId` char(36), `Texto` mediumtext; 11 índices (únicos `(ClienteCarteraId, NombreVigente)`, `ArchivoId`, `(DocumentoCarteraId, Numero)`, `(TareaAgenteId, PasoNumero, DocumentoCarteraId)`); 5 FK RESTRICT; colación `utf8mb4_0900_ai_ci`.
- Verificado en transacción revertida (`scratchpad/verif-workspacem5-transaccion.sql`, **con `--default-character-set=utf8mb4`**): "CONTRÁTO 2026.PDF" junto a "Contrato 2026.pdf" → 1062; la baja deja `NombreVigente` NULL y libera el nombre; `ArchivoId` repetido → 1062; nombre de 151 → 1406; 5.000.000 de caracteres con tilde (10 MB) en mediumtext OK; parte repetida → 1062; parte o adjunto con padre inexistente → 1452; borrar documento con partes → 1451; `LIKE … ESCAPE '!'` literal 1 / comodín 0 y sin tildes ni mayúsculas 1; token 1 fila / 0 filas; `EXPLAIN` del listado, del espacio y del duplicado usan índices (ref); 0 restos. (Sin ese parámetro el cliente `mysql.exe` manda los literales con tilde en otro charset y las pruebas con tildes dan falsos resultados.)
- Verificado EF → MySQL real (`scratchpad/verif-m5`, modelo sin Anthropic): **47 pasos OK, 0 restos**. Subida legible, sufijos "(2)" y "(3)" con mayúsculas y tildes, duplicado por hash, `NombreVigente` y `CHAR_LENGTH`, 1062 real reconocido por el nombre de la columna, renombrar repetido/OK/versión vieja, **`DbUpdateConcurrencyException` real por `VersionToken`**, listado con filtros, búsqueda por fecha y orden por las 7 columnas, espacio (SUM), vista previa, validar adjuntos (`List<int>.Contains`), staff (resumen, búsqueda por cliente, opciones, cliente dado de baja), herramientas (buscar sin mayúsculas, sin tildes, con `%`/`_` y con `!`; leer; listar), adjuntos (guardado, 1062, 1452, chip vigente y "(dado de baja)"), baja por rol con partes borradas y nombre liberado, sin temporales en disco. **Encontró un bug que InMemory no mostraba** (orden sobre un record construido en la proyección de `ListarAsync`), corregido.
- `documentos-limpiar` probado sobre una carpeta de prueba: informa y con `--aplicar` borra un temporal viejo y un archivo sin documento; no toca un archivo reciente ni un nombre que no es GUID.
- Impacto: 3 tablas nuevas vacías; se elimina `DocumentosCliente` (vacía); sin transformación de datos.

### Evidencia de build y tests M5
- `dotnet build OlvidataAgentes.slnx`: 0 errores, 1 advertencia preexistente (CS0114 `HomeController.StatusCode`).
- `dotnet test tests/OlvidataAgentes.Tests`: **159 OK / 0 fallidos** (113 existentes + 46 nuevos); golden de hash de formatos 1, 2 y 3 verdes.
- Lecciones: (1) EF InMemory traduce un `OrderBy` sobre la propiedad de un record construido en la proyección y MySQL no: proyectar a tipo anónimo (lo detectó el verificador EF → MySQL); (2) el `catch` de un `FileMode.CreateNew` no debe borrar la ruta si el archivo ya existía (bug real encontrado por el test del almacén); (3) `LIKE … ESCAPE` con el propio carácter de escape duplicado no es portable a InMemory; (4) en tag helpers `model="…"` no se decodifica `&quot;`: armar el modelo en un bloque de código; (5) `mysql.exe` en Windows necesita `--default-character-set=utf8mb4` para probar literales con tilde; (6) el id NuGet de PdfPig es `PdfPig`; (7) en scripts de parche multi-región conviene escribir el script con la herramienta de archivos (un heredoc de bash se rompe con comillas simples de JS).

### Riesgos residuales M5
- RT-M5-02: sin antivirus (aceptado). Un archivo que pasa la validación estructural pero explota un defecto de PdfPig/OpenXml/ClosedXML queda "No se pudo leer" al vencer el tope, pero el hilo de extracción no se puede abortar y sigue consumiendo CPU hasta terminar.
- La relación de compresión > 100 en entradas de más de 1 MB puede rechazar planillas legítimas muy repetitivas ("demasiado grande al abrirlo"); medir con archivos reales y subir el tope si hace falta.
- RT-M5-03 inyección desde documentos: mitigada (solo lectura, cliente de la tarea, JSON escapado con aviso, declaración de contexto) sin validar con el modelo real (PA-02).
- RT-M5-05 despliegue: la carpeta `App_Data/documentos` no debe borrarse al publicar y el pool necesita escritura; preferir ruta absoluta fuera del sitio (checklist M9, `/olvidata-infra`).
- RT-M5-06 rendimiento: ClosedXML carga el .xlsx completo en memoria; `LIKE` sobre mediumtext sin índice (S-M5-04).
- RT-M5-07 cuota: subidas simultáneas pueden excederla en un archivo cada una (aceptado).
- La imagen se muestra con el MIME del servidor y `nosniff` global; no se agregó una CSP propia a esa respuesta.
- Verificación visual pendiente (QA): arrastrar y soltar, cola con progreso, modal subir/elegir, Select2 con plantillas, chips, Ver pasos llano, partes sin recargar, mobile 390 y tema oscuro.

### Proximos pasos pendientes M5
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M5).
- M9: ruta absoluta de documentos fuera del sitio publicado, regla para que Web Deploy no la borre y permisos de escritura del pool.
- Corrida real con costo (PA-02): calidad de lectura por partes, uso de las herramientas y costo.
- Deuda preexistente vista, fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9; advertencias de filtro global en la relación `Licencia` ↔ `LicenciaRubro`/`TokenEmitido` al arrancar; `Admin licencia-crear` con `slugs.Contains` (MH-001).

---
# M4 — Agentes de la organización

Estado: **implementada 2026-09-14, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` (P1–P11, ajuste sin revisión del Director: RF-M4-06/07 pospuestos), `2-disenador-funcional.md` M4 (bloque "Ajuste aprobado en el gate": sin P-M4-04/05, cualquier miembro publica, aviso a Directores) y `3-arquitecto-mvc.md` M4 aprobados; `4-presupuestador.md` omitido por decisión de Joaquín (gate dispensado). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. Sin contenido real de rubros ni de sugerencias (solo mecanismos, datos de prueba en tests y ejemplo comentado en `nucleo/rubros/_plantilla/rubro.yml`).

### Escaneo de reutilizacion M4
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M3 (`ReglaService`: permisos por registro, límites, token de versión, mensajes; vistas `Reglas/*`, `_CardReglasDestino`) | `AgenteOrganizacionService` (estructura, `VersionToken`, conflicto sin reintento), card "Reglas de este agente" | Literal adaptado |
| Template M2 (`Area.NombreVigente` STORED por SQL + índice único; filtros en memoria DI-8; `FiltrosSesion`/`DataTableRequestHelper`/`RespuestasServicio`; bajas AJAX PAT-015) | `AgenteOrganizacion.NombreVigente`, listado de staff, archivar/duplicar AJAX con SweetAlert2 | Literal |
| Template M3 (`ConstructorContexto`, `InstantaneaContexto`, `ReglasEfectivasDto`, `_ReglasEfectivas`) | Formato 2 con instrucciones del derivado; vista previa y "Lo que el agente tuvo en cuenta" | Literal (extensión compatible) |
| Template M1/M3 (`ImportadorRubro` + `reglas_plataforma`, `CatalogoNucleo`, `IVersionadoService`) | `reglas_sugeridas` e `incluido_siempre`; sugerencias con el mismo ciclo Borrador → evaluación → publicación | Literal (extensión) |
| Template M3b (`ServicioTareas`, `ProcesadorTareas`, modelo simulado, `verif-m3b`) | Tareas con agente de la empresa, P11, verificador EF → MySQL `scratchpad/verif-m4` | Literal (extensión) |
| Template (`INotificationService` + campana) | Aviso a Directores | Literal |
| Catálogo / otros `5-implementador.md` | Sin prompts derivados configurables por el cliente | Diseño nuevo → PAT-030 completado con rutas reales (`pendiente_verificar: false`); notas de M3b que estaban en PAT-030 movidas a PAT-029 |

### Archivos y capas modificadas M4
**Domain**
- Nuevos: `Entities/AgenteOrganizacion.cs` (`AgenteOrganizacion` + `AgenteOrganizacionVersion`), `Enums/EnumsAgentesOrganizacion.cs` (`VisibilidadAgente`, `EstadoVersionAgente` con 4 y 5 libres para revisión).
- Modificados: `Enums/EnumsAgentes.cs` (`TipoArtefacto.ReglaSugerida = 4`), `Enums/EnumsReglas.cs` (`OrigenRegla.Sugerida = 2`), `Entities/Regla.cs` (`AgenteOrganizacionId`, `SugerenciaArtefactoId`), `Entities/Rubro.cs` (`IncluidoSiempre`), `Entities/Artefacto.cs` (`Etiquetas`), `Entities/Tareas.cs` (`AgenteOrganizacionVersionId` + navegación).

**Application**
- Nuevos: `Settings/AgentesOrganizacionOptions.cs`, `DTOs/AgentesOrganizacionDtos.cs` (catálogo, cards, detalle, versiones, formulario, edición, opciones, staff, `MensajesAgentesOrganizacion`), `Interfaces/IAgenteOrganizacionService.cs`.
- Modificados: `Motor/IConstructorContexto.cs` (`SolicitudContexto.AgenteOrganizacionVersionId`, `InstantaneaContexto.AgenteOrganizacionVersionId/Nombre` con `JsonIgnore WhenWritingNull`, `FormatoContextoAgenteOrganizacion = 2`), `Motor/IMotorAgentes.cs` (`CrearTareaDto.AgenteOrganizacionId`, `TareaFiltros.AgenteOrganizacionId`, `FiltroTareas.PrefijoAgenteOrganizacion`, `AgenteRefDto.AgenteOrganizacionId`, `AgenteOrganizacionTareaDto`, `TareaDetalleDto.AgenteOrganizacion`, `VistaPreviaAsync(int, int?)`), `DTOs/ReglasDtos.cs` (`PestanaReglas.Sugerencias`, `FiltroReglas.LeerAgente/ValorAgenteOrganizacion`, `ReglaFormDto/ReglaDetalleDto.AgenteOrganizacionId`, `ReglaDetalleDto.Origen`, `GrupoAgentesDto.EsDeLaEmpresa`, `MismoTemaConsultaDto.AgenteOrganizacionId`, `InstruccionesAgenteDto` en efectivas y aplicadas, DTOs de sugerencias), `Interfaces/IReglaService.cs` (sugerencias, activar, card del agente), `Interfaces/ILicenciaService.cs` (`SincronizarRubrosIncluidosAsync`).

**Infrastructure**
- Nuevos: `Services/Agentes/AgenteOrganizacionService.cs`, `Data/Configurations/AgentesOrganizacionConfigurations.cs`, migración `Data/Migrations/20260914220326_AgentesOrganizacionM4.cs` (+ Designer y snapshot).
- Modificados: `Services/Motor/ConstructorContexto.cs` (formato 2, `DeclaracionPrecedenciaAgenteOrganizacion`, sección `<instrucciones_de_la_empresa>`, reglas por agente del derivado, `CalcularHash(bloques, formato)`), `Services/Motor/ServicioTareas.cs` (validación del agente de la empresa, crear y vista previa, listado/opciones/búsqueda con el nombre del derivado, detalle con versión y archivado, instrucciones aplicadas), `Services/Motor/ProcesadorTareas.cs` (herramientas por intersección), `Services/Reglas/ReglaService.cs` (agentes de la empresa en alta, filtros, búsqueda, nombres, "No se aplica", combo, card, sugerencias y activación, `CrearInternoAsync` con origen), `Services/Nucleo/ImportadorRubro.cs` (`incluido_siempre`, `reglas_sugeridas`, etiquetas, slug con otro tipo), `Services/Nucleo/CatalogoNucleo.cs` (excluye sugerencias), `Services/Licencias/LicenciaService.cs` (rubros incluidos al crear + sincronización), `Data/AppDbContext.cs` (DbSets; `VersionToken` fuera del audit trail), `Data/Configurations/{ReglasConfigurations (check recreado, FKs, índices), AgentesConfigurations (Etiquetas, FK de la tarea)}.cs`, `DependencyInjection.cs`.

**Web**
- Nuevos: `Helpers/AgentesTextos.cs`, `Models/AgentesOrganizacionViewModels.cs`, vistas `Agentes/{_TarjetaAgente, _ScriptAccionesAgente, _Form, _BarraFormAgente, _ScriptFormAgente, Crear, Editar, Detalle}`, `Reglas/{_Pestanas, _Sugerencias, _ScriptSugerencias}`, `Clientes/Agentes`.
- Modificados: `Controllers/AgentesController.cs` (catálogo, crear/editar/detalle, duplicar/archivar/reactivar AJAX, nueva tarea y vista previa con agente de la empresa), `Controllers/ReglasController.cs` (pestaña Sugerencias, `ActivarSugerencia`, `agenteRef`, filtro por agente desde el detalle), `Controllers/ClientesController.cs` (`Agentes`, `ListarAgentes`, `DetalleAgente`), `Controllers/TareasController.cs` (filtro "o<id>"), `Helpers/ReglasTextos.cs`, `Models/{AgentesViewModels (EjecutarAgenteViewModel), ReglasViewModels (AgenteRef, sugerencias, instrucciones)}.cs`, vistas `Agentes/{Index (rediseñada), Ejecutar}`, `Shared/_ReglasEfectivas`, `Tareas/{Detalle, _CuadroSeguimiento}`, `Reglas/{Index, _Listado, _Form, _ScriptFormRegla, Detalle}`, `Clientes/Details`, `Nucleo/Rubro`, `wwwroot/css/site.css`, `appsettings.json` (sección `AgentesOrganizacion`).

**Admin**: comando `sincronizar-rubros-incluidos`. **Núcleo**: `nucleo/rubros/_plantilla/rubro.yml` (ejemplo comentado). **Tests**: nuevo `AgentesOrganizacionTests.cs` (17). **Docs del repo**: `docs/diseno-organizacion-roles-reglas.md` (M4 ✅ y permiso de publicación).

### Decisiones de implementacion M4 (ambigüedades resueltas)
- **DI-M4-1 Compatibilidad del hash (RT-M4-01):** formato de contexto 2 solo para tareas con agente de la empresa, con su propia declaración de precedencia; el formato 1 (texto, orden, rótulos) no cambia y los campos nuevos de la instantánea se omiten del JSON cuando son null. Test golden con dos hashes calculados con el código de M3b antes de tocar el constructor (captura temporal, luego borrada) + JSON con la forma de M3 + reconstrucción de una instantánea sin campos nuevos + ajuste M3b.
- **DI-M4-2 Lugar de las instrucciones:** en B3 (no cacheado) entre las reglas del cliente y las "Por agente": `<instrucciones_de_la_empresa agente="…">` con el texto escapado como el de las reglas. En la vista previa y el detalle, el grupo "Instrucciones de <agente>" se pinta antes del primer grupo de nivel Agente o posterior.
- **DI-M4-3 Reglas por agente (P3):** del base y del derivado en el mismo nivel, primero las del base (orden por marca "del derivado", que sin derivado es siempre falsa: el orden de M3 no cambia).
- **DI-M4-4 Borrador único:** `CreadaPor/CreadaAt` del borrador = última edición. Guardar o publicar con el contenido versionado igual al publicado no crea versión (descarta el borrador): "Datos guardados. Las instrucciones no cambiaron: el agente sigue en la versión N.".
- **DI-M4-5 Alta publicada:** agente y versión nuevos se apuntan entre sí (`VersionPublicadaId`): dos `SaveChanges` en una transacción. Con agente existente alcanza la navegación en un solo guardado.
- **DI-M4-6 Visibilidad:** lo nunca publicado lo ve solo su creador (aunque el borrador diga "Toda la empresa"); el Director ve y edita los borradores de agentes ya publicados para la empresa. El Director no puede dejar como "Solo yo" un agente de otra persona.
- **DI-M4-7 Catálogo:** "De tu área" sale de "De la empresa" (sin duplicar); "Mis agentes" = personales y nunca publicados, siempre visible con el estado vacío del diseño; badge "Borrador pendiente" para quien puede editar. **Agregado:** sección "Archivados" plegada al final, solo con los que quien mira puede reactivar (sin eso un archivado quedaba inalcanzable desde la UI) — a validar en QA.
- **DI-M4-8 Crear mi versión / Duplicar:** desde Olvidata → formulario con el base elegido; desde un agente de la empresa → formulario precargado sin guardar ("<nombre> (mi versión)", personal). Duplicar guarda una copia personal en borrador "Copia de <nombre>" (con " (2)", " (3)"… si hace falta), herramientas ∩ las actuales del base; quien puede editar copia el borrador, el resto lo publicado.
- **DI-M4-9 Nombre único:** comparación como la colación de MySQL (sin mayúsculas ni tildes); el 1062 del índice se reconoce por "NombreVigente" en el mensaje. Reactivar con el nombre tomado → mensaje; un archivado no se edita hasta reactivarlo.
- **DI-M4-10 Límites:** activos = no archivados (personales, de la empresa y borradores); personales = visibilidad publicada o, si nunca se publicó, la del borrador. Se controlan al crear, al pasar a personal, al reactivar y al duplicar.
- **DI-M4-11 "No disponible":** derivado (sin licencia vigente del rubro del base o base sin versión publicada). Permite guardar borrador, no publicar ni usar; un alta nueva exige base habilitada.
- **DI-M4-12 Navegación:** "Guardar y usar" lleva a Nueva tarea con el agente; publicar o guardar borrador, al detalle.
- **DI-M4-13 Aviso a Directores:** Directores activos salvo quien publica; "publicó" o "actualizó" según la visibilidad publicada anterior; URL relativa `/Agentes/Detalle/{id}`; un fallo del aviso se loguea y no revierte (CRM-020).
- **DI-M4-14 Tareas:** visibilidad por `dto.UsuarioId` (igual que el resto de `CrearAsync`); agente ajeno → NoEncontrado. Listado: la columna Agente muestra el derivado; filtro "o<id>"; el filtro del base excluye derivados; búsqueda global por el nombre del derivado. Detalle: "Tarea #N · <agente> (versión N)", "Basado en …", badge "Agente archivado" y sin "Nueva tarea con este agente" si hoy está archivado (P11: el ajuste sigue).
- **DI-M4-15 Reglas:** el combo usa `AgenteRef` ("12" base, "o12" derivado; compatible con los filtros guardados en Session); grupos "De Olvidata · <Rubro>" y "De la empresa". Regla de un agente archivado → "No se aplica" (grilla, filtro de estado y detalle) y no se puede activar. La card del agente incluye reglas de cliente + ese agente. El detalle de una regla muestra "Origen: Sugerida por Olvidata".
- **DI-M4-16 Sugerencias:** pestaña solo del Director (tabs extraídas a `Reglas/_Pestanas`); una activación por organización (sin índice: una doble activación simultánea es carrera aceptada); título truncado a 150; etiquetas filtradas a 5 de 30; modo por defecto "Salvo que se indique otra cosa"; modal Bootstrap con Select2 `dropdownParent`.
- **DI-M4-17 Importador:** `incluido_siempre` se toma siempre del manifiesto (en `plataforma` → advertencia y false); `reglas_sugeridas` de más de 4.000 caracteres o con un slug que ya existe con otro tipo se ignoran con advertencia; etiquetas normalizadas como las de reglas. `CatalogoNucleo.ListarArtefactosPublicadosAsync` excluye sugerencias (también afecta `listar_agentes` del MCP congelado).
- **DI-M4-18 Licencias:** los rubros incluidos se unen a los elegidos (una licencia puede emitirse solo con incluidos); la sincronización exige acceso global; en el alta de licencias del backoffice la casilla va tildada y deshabilitada. No hay "renovar" en el template: lo cubre la sincronización.
- **DI-M4-19 Staff:** listado filtrado y ordenado en memoria (decenas); el detalle reutiliza `Agentes/Detalle` en solo lectura con borrador visible.
- **DI-M4-20 Tema oscuro (lección OLV-002):** badges nuevos con `.ov-badge-neutro` (tokens del theme); override de `.badge.bg-light.text-dark` (etiquetas de reglas, ilegibles en oscuro desde M3), cruz de modales y texto "No disponible".
- **DI-M4-21 Migración:** `Down` borra las reglas de agentes de la organización (con su historial) antes de volver al check de M3b (solo base de desarrollo).

### Migraciones EF generadas M4
- `20260914220326_AgentesOrganizacionM4` — **aplicada en `olvidata_agentes_dev` (MySQL 8.0.29) el 2026-09-14** con `dotnet ef database update`. Ajustes manuales: `NombreVigente` quitada del `CreateTable` (el proveedor la creaba VIRTUAL) y agregada con `ALTER TABLE … GENERATED ALWAYS AS (…) STORED` antes de su índice único; el proveedor ya ordenó bien `DropCheckConstraint` → `AddColumn` → `AddCheckConstraint` y la FK circular (versiones → agentes al final).
- Verificado por SQL (`scratchpad/verif-agentesm4.sql`): columnas y tipos; `NombreVigente` STORED GENERATED; check recreado con "exactamente uno de los dos agentes"; 11 FK RESTRICT; índices únicos `(TenantId, NombreVigente)` y `(AgenteOrganizacionId, Numero)`; 42 reglas y 10 tareas existentes intactas. En transacción revertida: 8.000 caracteres con tilde (8.001 bytes) OK; nombre activo repetido con otra capitalización y sin tilde → 1062; archivar libera el nombre y reactivar con el nombre tomado → 1062; número de versión repetido → 1062; 8.001 caracteres → 1406; alcances 5 y 6 válidos con base o derivado, y 4 combinaciones inválidas → 3819; sugerencia inexistente y tarea con versión inexistente → 1452; borrar una versión publicada referenciada → 1451; `EXPLAIN` del catálogo usa `IX_AgentesOrganizacion_TenantId_CreadorUsuarioId`; 0 restos.
- Verificado EF → MySQL real (`scratchpad/verif-m4`, modelo simulado, sin Anthropic): 62 pasos OK. Alta personal y para la empresa (transacción de dos guardados), columna generada con tildes, índice único con colación y mensaje con la columna, aviso a Directores, privacidad, borrador → publicar → reemplazada, conflicto por token en la app y **`DbUpdateConcurrencyException` real por `VersionToken`**, tarea formato 2 anclada, ejecución con agente archivado y hash verificado, instrucciones escapadas en B3, herramientas efectivas, P11, listado/búsqueda/orden/opciones de tareas con el derivado, reglas con check real, filtros, "No se aplica", combo, card, vista previa v2, duplicar, crear mi versión, catálogo, staff (listado, filtros, detalle), sincronización de licencias, sugerencia publicada → activar → "Ya activada". Sin errores de type mapping (MH-001). Limpieza completa y 0 restos.
- Impacto: 2 tablas nuevas vacías; columnas nulas o en 0 en `Reglas`, `TareasAgente`, `Rubros`, `Artefactos`; ningún rubro marcado como incluido y ninguna sugerencia en dev.

### Evidencia de build y tests M4
- `dotnet build OlvidataAgentes.slnx`: 0 errores, 1 advertencia preexistente (CS0114 `HomeController.StatusCode`).
- `dotnet test tests/OlvidataAgentes.Tests`: **100 OK / 0 fallidos** (83 existentes + 17 de `AgentesOrganizacionTests`).
- Lecciones: (1) capturar el hash golden ANTES de tocar el render; (2) en un parcial Razor, dentro de un bloque `else` no va `@{`: las funciones locales con markup se declaran directo; (3) los modelos de parciales con expresiones multilínea van en el bloque de código, no dentro del atributo `model="…"`; (4) el verificador EF necesita clave de licencias efímera si resuelve `LicenciaService`.

### Riesgos residuales M4
- R-M4-01 inyección por instrucciones: mismo tratamiento que reglas (nivel fijo, escape, precedencia); sin validación con el modelo real (PA-02).
- Instrucciones del derivado en B3 (sin caché): costo por tarea con instrucciones largas; medir en la corrida real.
- Aviso con URL relativa: si el portal se publica bajo un subdirectorio, el enlace de la campana no incluye el PathBase.
- Límites y activación de sugerencias sin bloqueo: carreras aceptadas (como M3).
- Sección "Archivados" del catálogo agregada por necesidad de UI (DI-M4-7): confirmar con Joaquín/QA.
- Un base dado de baja lógica haría invisibles sus derivados (filtro de navegación requerida); hoy los artefactos no se borran.
- Verificación visual pendiente (QA): cards y dropdown del catálogo, buscador, formulario con herramientas al cambiar de base, barra sticky según "Quién lo usa", modal de sugerencias con Select2, tema oscuro (badges neutros, bg-light, btn-close) y mobile.

### Proximos pasos pendientes M4
- QA etapa 6 (guía en `trazabilidad.md`, entrada del implementador M4) con el modelo simulado.
- Joaquín: contenido del rubro transversal "negocio" (manifiesto con `incluido_siempre: true`) y de las reglas sugeridas; evaluar y publicar; correr `sincronizar-rubros-incluidos`.
- Mejora posterior: revisión del Director (RF-M4-06/07, estados 4 y 5 reservados).
- Deuda preexistente vista, fuera de alcance: `Admin licencia-crear` con `slugs.Contains` (MH-001); `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9.

---
# M3 — Reglas por alcance

Estado: **implementada 2026-09-14, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md`, `2-disenador-funcional.md` (D-M3-1..12) y `3-arquitecto-mvc.md` M3 aprobados; `4-presupuestador.md` omitido por decisión de Joaquín (gate dispensado). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`.

### Escaneo de reutilizacion M3
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M2 (`Web/Helpers/{FiltrosSesion, DataTableRequestHelper, RespuestasServicio}`, `Application/Helpers/BusquedaHelper`, `Views/Cartera/*`, `Views/Areas/*`) | Listado DataTables con filtros por columna + Session + Limpiar, búsqueda global con extraIds, formularios `.ov-*`, acción AJAX con `reload(null,false)`, 403/404 por `TipoError` | Literal adaptado |
| Template M1/M2 (`ImportadorRubro`, `IVersionadoService`, `CatalogoNucleo`, `Nucleo/*`) | Reglas de plataforma como `TipoArtefacto.ReglaPlataforma` importadas y publicadas con evaluación | Literal (extensión) |
| Template M2 `MiembroService` / `TareaAgente.Version` | Token de concurrencia (`Regla.VersionActual`) + mensaje de conflicto sin reintento (edición humana) | Literal adaptado |
| Template M1 `MotorAgentesTests.ModeloGuionado` | Motor sin costo en tests → `tests/.../Infra/EntornoReglas.cs` | Literal |
| crm-olvidata | Prefijo estable cacheado + contexto variable → sistema en 3 bloques con `CacheControlEphemeral` por bloque | Patrón |
| PAT-028 (catálogo) | Completado con rutas reales de código, `pendiente_verificar: false` | Confirmado |

### Archivos y capas modificadas M3
**Domain**
- Nuevos: `Enums/EnumsReglas.cs` (`AlcanceRegla`, `TipoRegla`, `ModoRegla`, `OrigenRegla`, `TipoEventoRegla`), `Entities/Regla.cs` (`Regla` + `ReglaEvento` inmutable).
- Modificados: `Enums/EnumsAgentes.cs` (+`TipoArtefacto.ReglaPlataforma = 3`), `Entities/Rubro.cs` (+`SlugPlataforma`), `Entities/Tareas.cs` (+`ClienteCarteraId`, `ReglasAplicadasJson`, `HashContexto`).

**Application**
- Nuevos: `Settings/ReglasOptions.cs`, `DTOs/ReglasDtos.cs` (pestañas, estado derivado, `NivelRegla` + `NivelesRegla`, filtros, ítems, detalle/historial, uso de límite, mismo tema, opciones, cards, `ReglasEfectivasDto`, `ReglasAplicadasDto`, `PiezaNucleoDto`), `Interfaces/IReglaService.cs`, `Motor/IConstructorContexto.cs` (`SolicitudContexto`, `InstantaneaContexto` serializable, `ContextoArmado`, `FormatoContexto = 1`), `Helpers/EtiquetasHelper.cs`.
- Modificados: `Motor/ModeloConversacion.cs` (`SolicitudModelo.SystemPrompt` → `Sistema: IReadOnlyList<BloqueSistema(Texto, Cachear)>`), `Motor/IMotorAgentes.cs` (`CrearTareaDto.ClienteCarteraId`, `FiltroTareas.SinCliente`, `TareaFiltros.Cliente`, `TareaListItemDto.Cliente`, `TareaOpcionesFiltroDto.Clientes`, `TareaDetalleDto.Cliente/ReglasAplicadas`, `IServicioTareas.VistaPreviaAsync`), `Interfaces/IPermisosOrganizacion.cs` (+`PuedeGestionarReglasDeOrganizacion`, `PuedeVerReglasComoStaff`), `Interfaces/INucleoServices.cs` (+`ListarReglasPlataformaPublicadasAsync`), `Interfaces/IClienteCarteraService.cs` (+`ListarComboAsync`), `DTOs/OrganizacionDtos.cs` (+`ClienteCarteraComboDto`).

**Infrastructure**
- Nuevos: `Services/Reglas/ReglaService.cs`, `Services/Motor/ConstructorContexto.cs`, `Data/Configurations/ReglasConfigurations.cs`, migración `Data/Migrations/20260914182556_ReglasM3.cs` (+ Designer y snapshot).
- Modificados: `Data/AppDbContext.cs` (DbSets `Reglas`, `ReglaEventos`; `ReglaEvento` fuera del audit trail), `Data/Configurations/AgentesConfigurations.cs` (tarea: FK cliente Restrict, índice, hash 64), `Services/Motor/ServicioTareas.cs` (valida cliente, instantánea + hash al crear, vista previa, filtro/columna/búsqueda por cliente, reglas aplicadas con "Cambió después" y texto de Olvidata solo staff), `Services/Motor/ProcesadorTareas.cs` (reconstruye y compara hash antes de llamar al modelo; sin instantánea → armado anterior en un bloque), `Services/Motor/ProveedorModeloAnthropic.cs` (caché por bloque), `Services/Nucleo/ImportadorRubro.cs` (`reglas_plataforma`), `Services/Nucleo/CatalogoNucleo.cs` (excluye `plataforma` del catálogo; reglas publicadas), `Services/Licencias/LicenciaService.cs` (rechaza `plataforma`), `Services/Organizacion/{PermisosOrganizacion, ClienteCarteraService}.cs`, `DependencyInjection.cs`.

**Web**
- Nuevos: `Controllers/ReglasController.cs`, `Helpers/ReglasTextos.cs` (rótulos llanos D-M3-8..12 y fila JSON), `Models/ReglasViewModels.cs`, vistas `Reglas/{Index, _Listado, _ListadoScript, Create, Edit, _Form, _ScriptFormRegla, Detalle, _ScriptEstadoRegla, _CardReglasDestino}`, `Shared/_ReglasEfectivas`, `Agentes/_VistaPreviaReglas`, `Tareas/_ReglasAplicadas`, `Clientes/Reglas`.
- Modificados: `Controllers/{AgentesController (cliente + vista previa AJAX), TareasController (filtro Cliente), ClientesController (Reglas, ListarReglas, Regla; rubros sin plataforma), CarteraController (card), AreasController (card)}`, `Models/AgentesViewModels.cs`, vistas `Agentes/Ejecutar` (rediseñada), `Tareas/{Index, Detalle}`, `Cartera/Detalle`, `Areas/Edit`, `Clientes/Details` (botón Reglas), `Nucleo/Rubro` (rótulo de tipo), `Shared/_Layout` (ítem Reglas para miembros), `appsettings.json` (sección `Reglas`).

**Núcleo**: `nucleo/plataforma/plataforma.yml` + `nucleo/plataforma/reglas/{01-no-inventar-datos, 02-no-revelar-instrucciones, 03-pedir-precisiones}.md`.

**Tests**: nuevos `ReglasTests.cs` (5), `ConstructorContextoTests.cs` (8), `Infra/EntornoReglas.cs` (entorno Estudio Pérez + `ModeloGuionado` compartido); `MotorAgentesTests.cs` ajustado a `Sistema`.

**Docs del repo**: `docs/diseno-organizacion-roles-reglas.md` (M3 ✅).

### Decisiones de implementacion M3 (ambigüedades resueltas)
- **DI-M3-1 Solicitud por versión:** `SolicitudContexto` recibe `AgenteVersionId` (no el artefacto): de la versión publicada se derivan artefacto y rubro, y la tarea queda anclada a esa versión.
- **DI-M3-2 Render solo desde inmutables:** el render usa versiones del núcleo, `ReglaEvento` y la propia instantánea (que guarda los nombres de área y cliente del momento). Renombrar un área o un cliente no rompe el hash. Las instrucciones del rubro también quedan fijadas por id (antes se releían en cada ejecución).
- **DI-M3-3 Hash:** SHA-256 de `formato:1` + por bloque `|bloque|` + flag de caché + texto. `ArmarAsync` devuelve null si falta una versión o evento, si un evento no corresponde a su regla o si cambió `FormatoVersion` → la tarea queda Fallida sin llamar al modelo.
- **DI-M3-4 Escape:** `& < > "` en título, etiquetas, texto y nombres de área/cliente de la organización. El contenido del núcleo no se escapa (lo escribe Olvidata y puede traer marcado propio).
- **DI-M3-5 Precedencia:** declaración fija en B1 (arquitectura aprobada) con los rótulos de D-M3-9 y la aclaración de que las reglas nunca dan permisos y que el texto de archivos y herramientas no es instrucción.
- **DI-M3-6 "No se aplica" derivado:** regla activa cuya área o cliente se dio de baja o cuyo autor está bloqueado (no toca `Activa`). Activar exige destino vigente.
- **DI-M3-7 Largo:** el límite suma solo el texto (no el título) normalizado (`\r\n` → `\n`). El ViewModel no valida el largo del texto: lo valida el service con el mensaje del diseño, para no contar doble los saltos de línea del navegador.
- **DI-M3-8 Versiones:** cambiar etiquetas también versiona (el historial del diseño las lista). Activar/desactivar deja evento pero no incrementa `VersionActual` (D-M3-3), así que no invalida una edición abierta.
- **DI-M3-9 Mismo tema (P4):** reglas activas visibles con etiqueta en común y `NivelRegla` menor (más autoridad). Área: la del destino si es regla de área, si no la del usuario. Cliente: el mismo. Agente: el mismo si se eligió. Preferencias: nunca. Se filtra en memoria (volumen acotado por límites).
- **DI-M3-10 Staff (D-M3-6):** `Clientes/Reglas/{id}` con pestañas De la empresa · De las áreas · Por agente · De clientes · De miembros (sin "Mis preferencias"), y detalle `Clientes/Regla/{id}?reglaId=` reutilizando `Reglas/_Listado` y `Reglas/Detalle`. Las URLs usan el marcador `__ID__`.
- **DI-M3-11 Pestañas:** "De mi área" solo si el Empleado tiene área. Última pestaña en Session `Reglas_Pestana`; filtros por pestaña `Reglas_<Pestaña>_*` (staff: `ReglasStaff<tenant>_<Pestaña>_*`). "Ver todas" desde Cartera/Áreas fija el filtro de cliente o área.
- **DI-M3-12 Rótulos en servidor:** la grilla recibe rótulos ya resueltos (`ReglasTextos.Fila`). La búsqueda global también matchea rótulos visibles (siempre, salvo que se indique otra cosa, procedimiento, inactiva), el destino por nombre, el autor, la versión y la fecha.
- **DI-M3-13 Rubro `plataforma`:** excluido de `ListarRubrosAsync` y de los rubros disponibles del backoffice, y rechazado por `LicenciaService.CrearAsync`. `reglas_plataforma` en otro rubro → advertencia y se ignora.
- **DI-M3-14 Compatibilidad:** las tareas M1/M2 (5 en dev) no tienen instantánea: el motor usa el armado anterior en un bloque cacheado y su detalle no muestra reglas. Una instantánea ilegible en el detalle se muestra sin reglas; en el motor, Fallida.
- **DI-M3-15 Edición:** alcance y destinos se toman siempre de la regla guardada, no del formulario (D-M3-1). Crear con un alcance no permitido por URL → 403.
- **DI-M3-16 Filtros de consulta:** `IgnoreQueryFilters([FiltroSoftDelete])` en consultas raíz separadas para nombres de destinos dados de baja (nunca dentro de joins o subconsultas, porque aplica a toda la consulta). `[FiltroTenant]` solo en consultas de staff con `TenantId` explícito.
- **DI-M3-17 Combo de clientes:** `IClienteCarteraService.ListarComboAsync` para la nueva tarea. `AgentesController` sigue con `[Authorize]`: para staff, la vista previa muestra el mensaje del service.

### Migraciones EF generadas M3
- `20260914182556_ReglasM3` — **aplicada en `olvidata_agentes_dev` (MySQL 8.0.29) el 2026-09-14** con `dotnet ef database update`. `MySql.EntityFrameworkCore 10.0.9` generó bien el `CHECK` en línea (no hizo falta `migrationBuilder.Sql`, a diferencia de las columnas generadas de M2). Tablas `Reglas` y `ReglaEventos`; columnas `TareasAgente.ClienteCarteraId/ReglasAplicadasJson (longtext)/HashContexto`; FK todas `RESTRICT`; índices por tenant.
- Verificado por SQL en transacción revertida (`scratchpad/verif-reglasm3.sql`): 6 alcances válidos OK; 7 combinaciones inválidas → ERROR 3819 `CK_Reglas_Destino`; `SUM(CHAR_LENGTH)` = 11 caracteres (14 bytes) con tildes; `LIKE '%,tono,%'` no matchea `,tonos,`; evento de regla inexistente → 1452; borrado físico de área con reglas → 1451; 0 restos.
- Verificado EF → MySQL real (`scratchpad/verif-m3`, una transacción revertida): 42 pasos OK. Incluye crear/editar/conflicto/activar, los 13 listados con filtros, estados y búsqueda global, uso de límite, mismo tema, opciones, cards, vista previa, tarea con instantánea y hash, filtro de tareas por cliente, baja de cliente → "No se aplica", vistas de staff y catálogo sin `plataforma`. Sin errores de type mapping (MH-001) y 0 restos.
- Import de plataforma en dev: `importar nucleo/plataforma/plataforma.yml` → 3 artefactos `ReglaPlataforma` v1 en **Borrador** (#56, #57, #58). **No publicados**: publicar requiere `evaluar <id> --aprobada "detalle"` + `publicar <id>`. Hasta entonces ninguna regla de plataforma entra en el contexto.
- Impacto: tablas nuevas vacías y columnas nulas en tareas existentes; sin transformación de datos.

### Evidencia de build y tests M3
- `dotnet build OlvidataAgentes.slnx`: 0 errores, 1 advertencia preexistente (CS0114 `HomeController.StatusCode`).
- `dotnet test tests/OlvidataAgentes.Tests`: **61 OK / 0 fallidos** (48 existentes + 13 nuevos).

### Riesgos residuales M3
- RT-M3-01 caché: B2 puede quedar bajo el mínimo cacheable (sin error, sin ahorro). Medir `cache_read` en la primera corrida real.
- RT-M3-02 carrera en límites: aceptada.
- RT-M3-03 inmutabilidad de `ReglaEvento`/`ArtefactoVersion`: la garantiza el código (ningún service los edita), no la base. Una alteración por SQL deja la tarea Fallida (test).
- R-M3-01 inyección: mitigada (escape + plataforma y precedencia en B1 + reglas sin permisos), no garantizada. Prueba real opcional con OK de costo de Joaquín.
- R-M3-04 datos sensibles: aviso en el formulario. El staff lee las reglas (P9): mencionarlo en términos de uso.
- Reglas de plataforma en Borrador en dev: falta la evaluación y publicación de Joaquín.
- Si el cliente elegido no tiene reglas, el prompt no nombra al cliente (el diseño no lo pide); queda como mejora menor.
- Verificación visual pendiente (QA): Select2 con tags, plegables, card de vista previa en mobile, tema oscuro de pestañas y badges.

### Proximos pasos pendientes M3
- QA etapa 6 (guía en `trazabilidad.md`).
- Joaquín: evaluar y publicar las 3 reglas de plataforma.
- Deuda preexistente vista, fuera de alcance: `Admin licencia-crear` usa `slugs.Contains(r.Slug)` sobre `string[]` (patrón MH-001; no se ejercita en tests); herramienta `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9.

---
# M2 — Organización del portal

**M2 — Organización del portal.** Estado: **implementada 2026-09-14, pendiente de QA (etapa 6)**. Entrada: `2-disenador-funcional.md` y `3-arquitecto-mvc.md` aprobados; `4-presupuestador.md` omitido por decisión de Joaquín (gate dispensado). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`.

### Escaneo de reutilizacion
| Fuente | Qué se tomó | Grado |
|---|---|---|
| la-platense `FerreteriaLaPlatense.Web/wwwroot/css/site.css` (Sistema de formularios) | `.ov-page-head`, `.ov-form-page`, `.ov-form-actions`, `.ov-required`, `.ov-field-hint`, `.ov-detail-grid` → `OlvidataAgentes.Web/wwwroot/css/site.css` | Literal |
| la-platense `wwwroot/js/site.js` | Auto-init global de Select2 (`ovAplicarSelect2`, excluye `.swal2-select`) + foco en `select2:open` + `window.Filtros` | Literal adaptado |
| la-platense `Helpers/FiltrosSessionHelper.cs`, `Helpers/DataTableRequestHelper.cs`, `ProductosController.Listar/Delete`, `Views/Productos/Index.cshtml` (PAT-015/016) | `Web/Helpers/FiltrosSesion.cs` (+ `Procesar`, `Fijar`), `Web/Helpers/DataTableRequestHelper.cs` (+ rangos), bajas AJAX `{success,message}` con `ajax.reload(null,false)` | Literal adaptado |
| delicias-naturales (`C:\Sistemas\delicias-naturales`, .NET Framework) | Patrón de búsqueda global por fecha/importe con `extraIds` → `Application/Helpers/BusquedaHelper.cs` | Patrón |
| Template propio (M1) | `TareaAgente.Version` + reintento de `ServicioTareas.CancelarAsync` → `Tenant.VersionMiembros` en `MiembroService`; `UsersController` como base de `MiembrosController` | Literal adaptado |
| PAT-027 (catálogo) | Completado con rutas reales de código, `pendiente_verificar: false` | Confirmado |

### Archivos y capas modificadas
**Domain**
- Nuevos: `Enums/EnumsOrganizacion.cs` (`RolOrganizacion`, `TipoIdentificacion`), `Entities/Area.cs`, `Entities/ClienteCartera.cs`.
- Modificados: `Entities/ApplicationUser.cs` (+`RolOrganizacion?`, `AreaId?`, `Area`), `Entities/Tenant.cs` (+`VersionMiembros`).

**Application**
- Nuevos: `Interfaces/IContextoUsuario.cs`, `IResolvedorSesion.cs`, `IPermisosOrganizacion.cs`, `IAreaService.cs`, `IMiembroService.cs`, `IClienteCarteraService.cs`; `DTOs/OrganizacionDtos.cs`; `Helpers/IdentificacionHelper.cs` (CUIT módulo 11, DNI, normalizar, formatear, validar); `Helpers/BusquedaHelper.cs`.
- Modificados: `DTOs/ServiceResult.cs` (+`TipoError` Validacion/NoEncontrado/SinPermiso, `CreateNotFound`/`CreateForbidden`, default compatible); `Motor/IMotorAgentes.cs` (`TareaFiltros`, `TareaListItemDto`, `TareaOpcionesFiltroDto`, `TareaResumenDto.PedidaPor`, `IServicioTareas.ListarAsync(DataTableRequest, TareaFiltros)` + `OpcionesFiltroAsync`).

**Infrastructure**
- Nuevos: `Services/Organizacion/{ContextoUsuario, ResolvedorSesion, PermisosOrganizacion, AreaService, MiembroService, ClienteCarteraService}.cs`; `Data/Configurations/OrganizacionConfigurations.cs`; migración `Data/Migrations/20260914150042_OrganizacionM2.cs` (+ Designer y snapshot).
- Modificados: `Data/AppDbContext.cs` (DbSets `Areas`, `ClientesCartera`; audit trail sin `PasswordHash`/`SecurityStamp`/`ConcurrencyStamp`/`VersionMiembros`); `Data/Configurations/ApplicationUserConfiguration.cs` (rol, FK área SetNull, índice, check constraint); `AgentesConfigurations.cs` (`VersionMiembros` concurrency token); `Services/Motor/ServicioTareas.cs` (consulta base `Visibles()` por rol en listar/detalle/existe/cancelar/opciones, listado paginado con filtros y `PedidaPor`); `DependencyInjection.cs` (`AddMemoryCache`, `AddIdentityCore<ApplicationUser>().AddRoles().AddEntityFrameworkStores`, servicios M2).

**Web**
- Nuevos: `Middleware/SesionOrganizacionMiddleware.cs` (reemplaza `TenantMiddleware`); `Authorization/PermisoOrganizacion.cs` (requirement + handler scoped); `Helpers/{FiltrosSesion, DataTableRequestHelper, RespuestasServicio}.cs`; `Models/OrganizacionViewModels.cs`; `Controllers/{AreasController, MiembrosController, CarteraController}.cs`; vistas `Areas/{Index, Create, Edit, _Form, _ScriptBajaArea}`, `Miembros/{Index, Edit}`, `Cartera/{Index, Create, Edit, Detalle, _Form, _ScriptBajaCliente}`.
- Eliminados: `Middleware/TenantMiddleware.cs`, `Services/TenantClaimsPrincipalFactory.cs`, `Services/TenantDesdeUsuario.cs`.
- Modificados: `Program.cs` (sin claims factory; policies `RequireMiembro`/`RequireDirector`; middleware entre `UseAuthentication` y `UseAuthorization`); `Hubs/TareasHub.cs` (usa `IResolvedorSesion`); `Controllers/ClientesController.cs` (textos D-1, `CrearMiembro` [RequireSuperUsuario], detalle vía services); `UsersController.cs` (solo staff, D-4); `TareasController.cs` (`Index` + `Listar` DataTables, 404 en cancelar ajena); `AccountController.cs` (perfil con organización/rol/área); `Models/AgentesViewModels.cs` (`ClienteDetalleViewModel` con DTOs, se elimina `UsuarioClienteCrearViewModel`); `Models/PerfilViewModels.cs`; vistas `Shared/_Layout` (menú por rol, "Organizaciones y licencias"), `_ViewImports`, `Clientes/{Index, Create, Details}`, `Tareas/Index`, `Account/Perfil`; `wwwroot/css/site.css`, `wwwroot/js/site.js`.

**Tests**
- Nuevo: `tests/OlvidataAgentes.Tests/OrganizacionTests.cs` (13 tests).
- Modificados: `Infra/TestServicios.cs` (`ScopeMiembro`, `ScopeStaff`), `MotorAgentesTests.cs` (2 tests pasan a scope de miembro; firma nueva de `ListarAsync`).

**Docs del repo**: `docs/arquitectura.md` (§2 y §3: middleware y resolvedor), `docs/diseno-organizacion-roles-reglas.md` (rol resuelto por request, M2 ✅).

### Decisiones de implementacion (ambigüedades resueltas)
- **DI-1 SecurityStamp:** se rota solo al **bloquear**. Cambio de rol/área: `Invalidar` + TTL 60 s ya cumplen RF-11 en todas las instancias; rotar el stamp en esos casos obligaría al miembro a volver a loguearse a los 5 min sin motivo.
- **DI-2 Columnas generadas:** `MySql.EntityFrameworkCore 10.0.9` ignora `stored: true` (emite `AS (...) NULL` = VIRTUAL). Se escriben con `migrationBuilder.Sql(... STORED)` (RT-02). El modelo EF las mantiene como `HasComputedColumnSql` (shadow).
- **DI-3 Migración:** `DROP INDEX IX_AspNetUsers_TenantId` movido después de crear el índice compuesto (MySQL 1553 por la FK); `UPDATE ... RolOrganizacion = 1` antes del check (P1). `Down` con orden inverso.
- **DI-4 Identity core en Infrastructure:** `MiembroService` usa `UserManager`; se registra `AddIdentityCore` en `AddInfrastructure` (registros TryAdd; el portal suma `AddIdentity` encima). MCP/Admin compilan y el test MCP real sigue verde.
- **DI-5 Tareas:** DTO de grilla propio (`TareaListItemDto`, fecha ya en hora argentina) y `OpcionesFiltroAsync` para los combos Agente / Pedida por calculados sobre tareas visibles (evita `List<string>.Contains`, MH-001). La columna Tokens se reemplazó por Costo (P-09). Filtro N° = número exacto.
- **DI-6 Staff en Tareas:** `PuedeVerTodasLasTareas` incluye staff, así que el staff también ve la columna "Pedida por".
- **DI-7 Unicidades:** nombre de área comparado sin distinguir mayúsculas (igual que la colación de MySQL); identificación única por (tipo, número), el mismo número con otro tipo se permite (igual que la columna generada).
- **DI-8 Filtrado:** Áreas y Miembros (decenas por organización) filtran en memoria; Cartera y Tareas en SQL con `EF.Functions.Like` + `extraIds` para fecha/identificación/número/importe.
- **DI-9 Contraseña inicial:** se usa la política vigente de Identity (6 caracteres, mayúscula, minúscula, número) con errores traducidos; se eliminó el mínimo de 8 del ViewModel viejo.
- **DI-10 AJAX sin permiso:** si falla una policy (ej. Empleado → `/Areas/DarDeBaja`), la cookie de Identity responde 403 sin cuerpo JSON; el 403 con `{success:false,message}` sale cuando decide el service (Empleado → `/Cartera/DarDeBaja`).
- **DI-11 Usuarios (SuperUsuario):** `CanManageUser` excluye usuarios con organización (Details/Edit/ToggleEstado → 403).

### Migraciones EF generadas
- `20260914150042_OrganizacionM2` — **aplicada en `olvidata_agentes_dev` (MySQL 8.0.29) el 2026-09-14**. Verificado por SQL: `NombreVigente` y `IdentificacionVigente` = `STORED GENERATED`; `CK_AspNetUsers_RolOrganizacion` activo; índices únicos `IX_Areas_TenantId_NombreVigente` e `IX_ClientesCartera_TenantId_IdentificacionVigente`. Prueba en transacción revertida: nombre de área repetido → 1062; tras baja lógica el nombre se libera; identificación repetida → 1062; varias sin identificación OK; tenant sin rol y staff con rol → 3819; miembro válido OK; sin restos.
- Impacto: columnas nuevas nulas en `AspNetUsers`, `Tenants.VersionMiembros` default 0, tablas nuevas; usuarios de organización existentes pasan a Director (solo base de desarrollo).

### Evidencia de build y tests
- `dotnet build OlvidataAgentes.slnx`: 0 errores, 1 advertencia preexistente (CS0114 `HomeController.StatusCode`, no tocado).
- `dotnet test tests/OlvidataAgentes.Tests`: **48 OK / 0 fallidos** (35 existentes + 13 de `OrganizacionTests`).

### Riesgos residuales
- RT-01 caché de sesión por instancia (límite aceptado; con varias instancias el cambio llega al vencer el TTL de 60 s; el bloqueo además por SecurityStamp a los 5 min).
- DI-10: policy fallida en AJAX devuelve 403 sin JSON (el JS muestra el mensaje genérico).
- Alta del primer miembro sin token de concurrencia (solo la hace el SuperUsuario; riesgo bajo).
- Verificación visual pendiente (regla 25): Select2 global con foco, daterangepicker, formularios en escritorio/mobile, tema oscuro de las clases portadas.
- La unicidad y el check solo se prueban en MySQL real (InMemory no los aplica).

### Proximos pasos pendientes
- QA etapa 6 (guía en la salida de esta etapa y en `trazabilidad.md`).
- Deuda fuera de alcance: el staff no tiene UI para cambiar nombre/email/rol/estado de un miembro (P-08 es solo lectura + alta); `Users/*` y `Clientes/Index` del template conservan textos sin tildes y tabla no DataTables; el resolvedor no mira `Tenant.Estado` (organización suspendida); herramienta `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9.

### Entrega progresiva por etapas del menú (2026-09-22)

- Alcance aprobado por Joaquín (plan "Primeros pasos de Gastón", Contadores BMA): `Tenant.EtapaEntrega` (enum `EtapaEntrega` 1 Primeros pasos, 2 Tu forma de trabajar, 3 Sistema completo). Migración `EtapaEntregaOrganizacion`: columna `int` con default 3, las organizaciones existentes y las nuevas quedan en 3.
- DI-EE-1: el mapeo opción → etapa vive solo en `Application/Helpers/EtapasEntrega.cs` (`OpcionMenu`, `EtapaMinima`, `Visible`, `OpcionesVisibles`, textos). El layout pregunta `IPermisosOrganizacion.VeEnMenu(opcion)`; el rol se sigue chequeando aparte (`EsMiembro` / `EsDirector`).
- DI-EE-2: la etapa se resuelve una vez por request en `ResolvedorSesion` (misma lectura que el estado de la organización, caché de sesión) y se expone en `IContextoUsuario.EtapaEntrega`. Null (staff, sistema, worker) = ve todo.
- DI-EE-3: se cambia desde `Clientes/Editar` vía `OrganizacionBackofficeService.EditarAsync` (param opcional `EtapaEntrega` en el DTO; null = no se toca). Solo SuperUsuario, `Enum.IsDefined` en el service, audit trail de `SaveChanges` + log, e invalida la sesión de los miembros para que el menú cambie en la próxima request.
- DI-EE-4: SOLO se oculta el menú. No se bloquean acciones de controllers, links internos ni herramientas de los agentes (decisión explícita de Joaquín). Los contadores de las opciones ocultas no se calculan.
- Vistas: `_Layout` (Reglas, Instructivos, Asignaciones, Programaciones, Resultados, Aprobaciones, Consumo, Áreas, Conexiones envueltas en `VeEnMenu`), `Clientes/Editar` (card "Entrega por etapas" con texto de cada etapa), `Clientes/Details` (dato en la card Organización).
- Tests: `EtapaEntregaTests` (10 casos: mapeo Empleado y Director, sin etapa ve todo, default 3, solo SuperUsuario, rango inválido 0/4/-1, sesión + invalidación, staff ve todo). Suite 696/696 OK.
- Riesgo: si un miembro conoce la URL de una opción oculta, entra igual (aceptado: es solo menú).

## Historial de ajustes
- 2026-09-21: **Anatomía de agentes (catálogo + ficha), 4 etapas con commit local cada una.** Diseño `docs/diseno-anatomia-agentes.md` aprobado por Joaquín con D1 (bloque `ficha:`), D2 (contexto real solo SuperUsuario y auditado) y D3 (título + `resumen_publico`).
  - **E1 (16480a3):** `IResolvedorHerramientas` extraído de `ProcesadorTareas` sin cambio de comportamiento (mismo conjunto y orden; `Todas` anota familia, condición y si se ofrece) + `DescripcionesHerramientas` (rótulo y "qué hace" llanos) con test de cobertura sobre el registro.
  - **E2 (6614cc9):** `Agentes/Ficha` y `Agentes/Detalle` en 7 pestañas, `IFichaAgenteService` (DTO del cliente sin campo para texto del núcleo), catálogo con "Ver ficha", etapas, coordinador primero. Herramientas en lenguaje llano también en detalle y formulario. Portal real en tests con `WebApplicationFactory` y centinelas en todas las URLs de cliente (CP-AA-01).
  - **E3 (437133c):** `Nucleo/Agente` y `Nucleo/ContextoArmado` (staff), `IAnatomiaAgenteService` con rol re-verificado adentro; B1 sin organización byte a byte el de una tarea; con organización el mismo hash que una tarea creada ahora, solo SuperUsuario y con fila en `AuditLog`.
  - **E4 (e573151):** importador lee `ficha:`, `resumen_publico` y todas las etapas del manifiesto. **Migración `AnatomiaAgentes`** (`Artefactos.FichaJson` longtext, `Artefactos.ResumenPublico` varchar 500, tabla `ArtefactoEtapas`), aplicada en `olvidata_agentes_dev`; reimportados contable y plataforma contra MySQL dev: **0 versiones nuevas**. Fichas escritas para los 10 agentes de contable y los 2 de plataforma; resumen público para las 3 reglas de plataforma.
  - DI-AA-1: la ficha y el resumen viven en `Artefacto`, fuera del cuerpo versionado: no cambian el hash de versión ni los goldens. DI-AA-2: la colección de tests del portal corre sin paralelo y el csproj de tests excluye los appsettings del portal (su `Production.json` rompía `ServidorLocalDePrueba` con 400 "Invalid Hostname"). DI-AA-3: CSS `ov-capa*` en `site.css` (donde viven las clases de M4), no en `olvidata-theme.css`.
  - Evidencia (sin pipe): línea base 653/654 (el flaky conocido de `LectorDocumentosTests`); E1 659/659, E2 671/671, E3 680/680, **E4 685/685**. Goldens intactos. Sin llamadas a Anthropic, sin deploy.
  - Pendiente: QA funcional y visual (CP-AA-12: 390 px y tema oscuro; el MCP de Playwright no conectó). En producción: aplicar la migración y reimportar contable y plataforma para cargar fichas, resúmenes y etapas.
- 2026-09-21: **PA-05 — backoffice del SuperUsuario.** Editar organización (sin slug), pausar/reactivar/dar de baja con confirmación que cuenta lo afectado, extender licencias, editar miembros (nombre, email, rol, área, bloqueo) y generar contraseña de una sola vez, todo con `RequireSuperUsuario` y verificación en el service. Una organización no activa **frena al motor** en tres puntos (reclamo, bucle antes de cada llamada, reclamo de programaciones) sin cancelar nada. Cambio deliberado en programaciones de empresas suspendidas (DI-PA05-3). Sin migración, 641/641, goldens intactos. Decisiones DI-PA05-1..11.
- 2026-09-19: **Fines de línea fuera del hash del contexto (cierra el hallazgo abierto de la entrada de abajo).** El prompt de sistema salía con los saltos mezclados: las declaraciones `<precedencia>` de `ConstructorContexto.cs` son literales crudos (`"""`) y el compilador de C# conserva el fin de línea **del archivo fuente**, mientras todo el resto del render usa `\n`. Confirmado que era peor de lo anotado: `git ls-files --eol` da `i/lf w/crlf`, o sea que **el índice de git ya guarda LF y el working tree CRLF** — un build desde CI, desde Linux o desde un clon con `core.autocrlf=false` ya producía otro hash que el de esta máquina. Se normalizó ahora, que es el momento barato (nada desplegado; las tareas de dev y demo son descartables).
  - **Dónde se arregló: en `BloqueSistema` (`src/OlvidataAgentes.Application/Motor/ModeloConversacion.cs`), no en los literales.** El record normaliza a LF al construirse (`\r\n` y `\r` sueltos) y expone `Texto` de **solo lectura sobre un campo privado**: no hay setter, no hay `with`, no hay forma de construir un bloque con CRLF. Se eligió el tipo y no cada literal porque el texto del bloque es exactamente lo que entra a `CalcularHash`, y así queda cubierto todo constructor presente y futuro — los 4 formatos, `RevisorAutomatico` (que también arma su prompt con un literal crudo) y `ProcesadorTareas`. **No puede volver a romperse por una herramienta de formateo**: `dotnet format`, "normalizar saltos de línea" del editor o un `core.autocrlf` distinto ya no tienen por dónde llegar al hash, y el arreglo no depende de que nadie se acuerde de nada. Encaja con el patrón que el repo ya usa en las **entradas** (`ReglaService`, `AgenteOrganizacionService`, `ImportadorRubro` ya normalizan al guardar); esto es el último filtro en la **salida**.
  - **DI-CRLF-1:** no se tocó `ConstructorContexto.cs` (queda sin cambios, byte a byte) ni se agregó una regla `eol` al `.gitattributes` para los `.cs`: el arreglo es de código, no de configuración de checkout, así que vale también para quien clone con otra configuración.
  - **Los 5 goldens recalculados, y el diff se lee claro: los `.txt` no cambiaron ni un byte.** Regenerados con `OLVIDATA_GOLDEN_REGENERAR=1`, `git status` de `tests/OlvidataAgentes.Tests/Goldens/` quedó vacío. Los 5 tests fallaron **solo en `VerificarHash`** (nunca en `VerificarTexto`), que es la prueba de que el único cambio son los saltos de línea. Hashes nuevos en `Infra/Golden.cs`: formato-1-cm-panaderia `782c9568…`→`5117f901…`, formato-1-tasador-ferreteria `5553ed2e…`→`37218376…`, formato-2-agente-organizacion `3b2656b6…`→`a4094bf7…`, formato-3-configuracion `dde29dcb…`→`bea8f773…`, formato-4-asistente `10be2a34…`→`039c7e7b…`.
  - **La defensa se reemplazó por una que no tiene número que corregir.** `CasoGolden.VerificarFinDeLinea` contaba CRLF esperados (10/10/10/8/9) y el parámetro `SaltosCrLf` desapareció del record: ahora exige **cero retornos de carro** en el contexto armado y, si falla, dice en castellano que se arregla en `BloqueSistema` y nunca en el assert.
  - **Test permanente nuevo** `ConstructorContextoTests.El_fin_de_linea_del_texto_de_origen_no_entra_al_prompt_de_sistema_ni_al_hash`: mete el CRLF a propósito, así que **no depende de cómo esté guardado el checkout** (la guarda de cero CR sola no alcanzaría en un clon con LF). Comprueba el bloque (`\r\n`, `\r` y `\n` dan el mismo bloque y por lo tanto el mismo hash) y además de punta a punta, guardando el prompt del agente con CRLF en la base y verificando que el contexto armado y el hash no se mueven.
  - **Verificación pedida por Joaquín, hecha a mano sobre el archivo fuente:** `ConstructorContexto.cs` convertido a **LF puro** (`i/lf w/lf`, 0 bytes CR) → 32/32 verde; convertido a **CRLF** (515 CR / 515 LF) → 32/32 verde, con los mismos hashes. El archivo se restauró y `cmp` lo confirma idéntico al original. **El hash no se movió en ninguno de los dos casos.**
  - **Aceptado:** las tareas y conversaciones que ya existen en dev y demo dejan de reconstruir su hash y sus seguimientos fallan sin llamar al modelo. No se migró nada, por decisión.
  - Sin migración EF. Tres archivos tocados (`ModeloConversacion.cs`, `Infra/Golden.cs`, `ConstructorContextoTests.cs`); `Mcp` y `Cli` sin tocar. Sin commits.
  - **Evidencia medida sin pipe** (`dotnet test > archivo 2>&1`, leyendo el resumen impreso): línea base **Con error: 0, Superado: 600, Total: 600**; tras el cambio **Con error: 5** (los 5 goldens, solo por hash) sobre 601; final **Con error: 0, Superado: 601, Omitido: 0, Total: 601**. `dotnet build OlvidataAgentes.slnx`: 0 errores, **0 advertencias**.
- 2026-09-19: **Goldens de contexto: texto versionado + constantes recalculadas.** Diagnóstico confirmado: no había regresión del producto — el render nunca cambió y las 7 constantes `HashGolden*` (5 valores distintos, 2 duplicados literalmente entre `AgentesOrganizacionTests` y `M14GoldenYPantallasTests`) **nacieron mal y nunca coincidieron con ningún estado del repo**. Se verificó primero que el texto actual es *correcto* (orden de las 9 secciones, rótulos coherentes con lo que nombra `<precedencia>`, escapado de `&`/`<`/`>` en reglas e instrucciones de la empresa, y nada que no deba estar: sin instructivos, sin herramientas, sin búsqueda web, sin ids de tenant ni de usuario), y recién después se recalcularon los hashes desde el texto real.
  - **Lo principal: el texto ahora se versiona.** `tests/OlvidataAgentes.Tests/Goldens/*.txt` guarda el contexto renderizado de los 5 casos (formatos 1×2, 2, 3 y 4) con sus bloques y su marca de caché. El test **compara el texto y además el hash**, y **el texto primero**: al fallar deja el contexto nuevo en `<nombre>.actual.txt` y el mensaje trae el `git diff --no-index` listo para pegar. Verificado rompiendo el render a propósito: el diff muestra en castellano el rótulo que cambió, en vez de dos hexadecimales.
  - Todo centralizado en `tests/OlvidataAgentes.Tests/Infra/Golden.cs` (`Goldens` + `CasoGolden`), con el comentario de qué garantiza cada golden y qué hacer si falla. **Se eliminó la duplicación de constantes**, que es cómo `HashGoldenTasadorFerreteria` estuvo mal sin que se notara: el assert anterior fallaba primero y lo tapaba.
  - Regeneración explícita con `OLVIDATA_GOLDEN_REGENERAR=1` (reescribe los `.txt` y deja el hash en un `.hash.tmp`); en ese modo no se verifica nada, así que el verde que cuenta es el de la corrida siguiente sin la variable.
  - **Hallazgo — CERRADO el 2026-09-19** (ver la entrada de arriba: se normalizó en `BloqueSistema` y se recalcularon los 5 hashes). Lo que se había detectado: el hash depende de los **fines de línea de `ConstructorContexto.cs`**. Las declaraciones `<precedencia>` son literales crudos (`"""`) y el compilador de C# conserva el fin de línea del archivo fuente, que está en CRLF; todo el resto del render usa `
`. Un `dotnet format`, un "normalizar saltos" del editor o un clon con otro `core.autocrlf` cambia **los 5 hashes a la vez sin cambiar una letra del texto** — y es la explicación más probable de por qué las constantes nacieron mal. Queda cubierto por `CasoGolden.VerificarFinDeLinea`, que cuenta los CRLF y avisa en castellano. **Normalizar los literales a `
` volvería el hash independiente del checkout, pero cambia los 5 hashes y rompe la reconstrucción de las tareas ya guardadas: se deja a criterio de Joaquín.**
  - Sin migración EF. `Mcp` y `Cli` sin tocar. Sin commits. Los cambios sin commitear de M15 quedaron intactos.
  - **Evidencia medida sin pipe** (`dotnet test > archivo 2>&1` + `$?`): línea base **595 OK / 5 fallidos de 600** (los 5 goldens), resultado final **600/600, `EXITCODE_REAL=0`, 0 `[FAIL]`**.
- 2026-09-18: M15 ficha de rubro para el staff. Se enriqueció `Nucleo/Rubro` en vez de crear una pantalla nueva (evita dos pantallas casi iguales) y se absorbió la card duplicada de material de referencia. Nuevos `IFichaRubroService`/`FichaRubroService` y `NucleoTextos`; la lista de organizaciones cruza el filtro de tenant con `IgnoreQueryFilters([FiltroTenant])` justificado. Sin migración, solo lectura, 6 tests nuevos. Decisiones DI-M15-1..6. **Hallazgo: los 4 goldens de contexto ya fallaban en `e248922` (589/594), no es regresión de esta etapa.**
- 2026-09-14: Implementación de M2 Organización (Domain→Application→Infrastructure→Web), migración `OrganizacionM2` aplicada y verificada en MySQL dev, 13 tests nuevos (48/48 OK). Decisiones DI-1..DI-11. PAT-027 completado en el catálogo.
- 2026-09-14: Implementación de M3 Reglas por alcance: `Regla`/`ReglaEvento`, `ReglaService`, `ConstructorContexto` (3 bloques con caché, instantánea por ids + hash verificado en el motor), vista previa y reglas aplicadas, rubro técnico `plataforma` (3 reglas en Borrador en dev). Migración `ReglasM3` aplicada y verificada con SQL y EF contra MySQL real (transacciones revertidas). 13 tests nuevos (61/61 OK). Decisiones DI-M3-1..17. PAT-028 completado en el catálogo.
- 2026-09-14: Implementación de M3b Seguir conversando: ajustes del autor con re-apertura atómica, normalización de la conversación, pasos por turno, `CierreTurno`, caché en el último mensaje, detalle como conversación, reglas cambiadas, preferencias ajenas ocultas, listado con mensajes y última actividad, modelo simulado solo en Development. Migración `ConversacionM3b` aplicada y verificada con SQL y EF contra MySQL real (37 pasos, 0 restos). 22 tests nuevos (83/83 OK). Decisiones DI-M3b-1..13. PAT-029 completado en el catálogo.
- 2026-09-14: Implementación de M4 Agentes de la organización (sin revisión del Director): `AgenteOrganizacion`/`AgenteOrganizacionVersion`, `AgenteOrganizacionService`, catálogo unificado, formulario, detalle, duplicar/archivar/reactivar, tareas con formato de contexto 2 sin cambiar el hash de las existentes (test golden), herramientas por intersección, reglas por agente de la empresa, sugerencias de Olvidata, `incluido_siempre` + `sincronizar-rubros-incluidos`, vistas de staff. Migración `AgentesOrganizacionM4` aplicada y verificada con SQL y EF contra MySQL real (0 restos). 17 tests nuevos (100/100 OK). Decisiones DI-M4-1..21. PAT-030 completado en el catálogo.
- 2026-09-14: Implementación de M4b Agente configurador de reglas del Director: `TipoTarea.ConfiguracionReglas` con formato de contexto 3 propio (golden de formatos 2 y 3; 1 y 2 intactos), `ResolverUsuarioAsync` y re-verificación del autor, 9 herramientas de lectura/propuesta sin `SaveChanges`, `PropuestaRegla` con token y único por `ToolUseId`, `PropuestaReglaService` y `ReglaService` con origen de aplicación en el mismo guardado, lista de conversaciones, tarjetas con modal de cambio, editar y aplicar, filtro Tipo en Tareas, simulador con guion de herramientas, prompt borrador importado sin publicar (#65). Migración `ConfiguradorReglasM4b` aplicada y verificada con SQL y EF contra MySQL real (17 pasos, 0 restos). 13 tests nuevos (113/113 OK). Decisiones DI-M4b-1..19. PAT-032 completado en el catálogo.
- 2026-09-15: Implementación de M5 Workspace por cliente de cartera: `DocumentoCartera`/`DocumentoCarteraParte`/`AdjuntoMensajeTarea` (reemplazan `DocumentoCliente`), almacén en disco fuera de `wwwroot` con ids y GUID, validación por contenido (ZIP seguro, sin macros), extracción por partes con PdfPig/OpenXml/ClosedXML y topes, servicio con nombre único según la colación y reintento ante 1062, herramientas de solo lectura en tareas de trabajo con cliente, adjuntos en pedido y ajustes con nota en los mensajes (golden 1–3 intactos), chips y Ver pasos llano, pantallas y backoffice solo metadatos, simulador con guion de documentos, `documentos-limpiar`. Migración `WorkspaceClientesM5` aplicada y verificada con SQL (estructura y transacción revertida con utf8mb4) y EF contra MySQL real (47 pasos, 0 restos; detectó un orden no traducible corregido). 46 tests nuevos (159/159 OK). Decisiones DI-M5-1..19. PAT-033 completado con rutas reales y lecciones.
- 2026-09-15: Implementación de M6 Aprobaciones de acciones por rol y límites de gasto (continuación de una corrida cortada por límite de uso: se conservó el backend y se completaron Web, tests, migración y documentación). Límite mensual por organización (USD 100 por defecto) y por miembro con límite efectivo, consumo del mes argentino desde `PasosTarea`, verificación antes de cada llamada y en crear/configurar/ajustar, avisos únicos, pantalla Consumo por rol, columna en Miembros, card/consumo de staff y columnas en Uso; `AprobacionAccion` por `tool_use_id` con pedido + espera en un guardado, tarjeta y bandeja con contador, resolución con tokens y `Intentos = 0`, ejecución única con autor re-verificado, rechazo/vencimiento como error registrado, barrido en el worker, cancelación; demostraciones solo con el simulador en Development. Migración `AprobacionesYGastoM6` (se agregó el `UPDATE` del límite por defecto) aplicada, Down/Up y verificada por SQL y EF contra MySQL real (64 pasos, 0 restos). 26 tests nuevos (185/185 OK), golden 1–3 intactos. Decisiones DI-M6-1..15. PAT-034 y PAT-035 completados con rutas reales y lecciones.
- 2026-09-16: Implementación de M8 Evaluación automática de prompts: **extracción del render de `ConstructorContexto` a una función pura compartida por los 4 formatos y por `ArmarEvaluacionAsync`, byte a byte (4 goldens verdes, plan B no usado)**; casos de prueba como datos del repo (`evaluaciones:` en el manifiesto, `ConjuntoCasos`/`VersionConjuntoCasos`/`CasoEvaluacion` versionados por hash, con dos suites comunes en `plataforma`); `CorridaEvaluacion`/`ResultadoCaso` con único (corrida, caso, repetición), lease, token y barrido propio en `MotorAgentesWorker` (de a una, fuera de `MaxTareasSimultaneas`); ejecutor que **ofrece las herramientas y nunca las resuelve** (doble que lanza en `Obtener`), verifica los dos topes antes de cada llamada y guarda una unidad de trabajo por (caso, repetición); `VerificacionesTexto` puro + `RevisorAutomatico` con salidas estructuradas del SDK (verificadas en Anthropic 12.47.0: `MessageCreateParams.OutputConfig` / `JsonOutputFormat.Schema`) y validación estricta del texto, con control de cordura por corrida; comparación contra la publicada, resultado global, gate de publicación por `HashCasos` con excepción de SuperUsuario auditada, organización interna `olvidata-interno` y `CanalUso.Evaluacion`; 9 vistas y 11 acciones en Núcleo, 7 verbos `evaluacion-*` en Admin. Migración `EvaluacionAutomaticaM8` aplicada y verificada con SQL contra MySQL real (1062 reales en los dos únicos, `decimal(18,6)`, EXPLAIN del gasto del mes y del gate, siembra de la organización interna, Down y Up, 0 restos). 43 tests nuevos (287/287 OK). Decisiones DI-M8-1..12. PAT-040 y PAT-041 creados en el catálogo con rutas reales. Casos iniciales de plataforma importados en dev como **borrador para revisar** (PA-17); **ninguna corrida real ejecutada**.
- 2026-09-22: Entrega progresiva por etapas del menú por organización (DI-EE-1..4). Migración `EtapaEntregaOrganizacion` (default 3). 10 tests nuevos, 696/696 OK.
