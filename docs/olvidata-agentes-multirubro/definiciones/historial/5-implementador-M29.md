<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/5-implementador.md el 2026-10-03 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - M29 (1 bloques archivados)

- M29 frente A - La casilla de buscar en internet en el chat libre

---

# M29 frente A - La casilla de buscar en internet en el chat libre

Estado: **implementado 2026-10-02; 1 commit local, sin push y sin deploy. SIN MIGRACION.** Repo
`C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `94fc5e2`. Entrada: A-01 / A-02 de «Arquitectura M29»
(`3-arquitecto-mvc.md`), CA-01.1..CA-01.6 y D-03 (`1-analista-funcional.md`), D-05 y RD-05
(`2-disenador-funcional.md`). **El frente B (el documento sin cliente, con migracion) no se toco.**

### Escaneo de reutilizacion

`docs/patrones/cat_resumen.txt`: sin patron para esto, y no hace falta. La casilla **ya existe maquetada dos veces**
(`Views/Agentes/Ejecutar.cshtml:111-115` y `Views/Tareas/_CuadroSeguimiento.cshtml:144-148`) y se copio tal cual:
mismo texto («Buscar en internet si hace falta») y mismo `title` (D-05). El chat libre **reusa** `_CuadroSeguimiento`
via `Tareas/Detalle` -> `_Conversacion`, asi que para el cuadro de ajuste no se maqueto nada: alcanzo con el punto 6.
El JS que lee la casilla y la manda en el POST del ajuste (`Views/Tareas/Detalle.cshtml:294`) ya era generico.

### Como se escribio el gate (A-02)

**Un solo predicado, lista blanca que NOMBRA los dos tipos:** `ClasesDeTarea.PuedeBuscarEnInternet(tipo)` =>
`tipo is TipoTarea.Trabajo or TipoTarea.ChatLibre`, en `Application/Motor/NotaSubtarea.cs`, al lado de
`MuestraPartesYAprobaciones` y `OrigenDePreferenciaPersonal`, que son la misma clase de pregunta y ya estaban escritas
asi. No es `EsDePlataforma` negado (incluiria a los cuatro y contradice D-03) ni un `!=`. Los **tres** puntos de
alcance (resolvedor, ajuste, cuadro) llaman al mismo predicado: si manana aparece un `TipoTarea` nuevo hay **un solo
lugar** donde decidir, y mientras nadie lo decida el tipo nuevo queda afuera de forma ruidosa, no mapeado mal.

**La compuerta de M14 se evalua igual, aparte y siempre.** El predicado es de *alcance*; `_busquedaWeb.Disponible`
(`Habilitada && PrecioPorBusquedaUsd > 0`) es la fail-closed, y las dos se multiplican en cada punto. Ningun valor de
M6 ni de M14 se toco; `MaxBusquedasPorTarea` sigue valiendo (hay test).

**Efecto lateral que conviene saber:** el punto 6 era `!esDePlataforma && ...`, asi que una `ConsultaCliente` del
portal del cliente **veia** la casilla en el cuadro de ajuste aunque el resolvedor (`trabajo`) y el ajuste
(`Tipo == Trabajo`) nunca la iban a honrar. Con la lista blanca deja de verla: se ofrecia algo que no hacia nada.
`PortalClienteConsultasTests` ya afirmaba `PermiteBusquedaWeb == false` ahi y sigue verde.

### Cambios por capa

| Capa | Archivo | Que |
|---|---|---|
| Application | `Motor/NotaSubtarea.cs` | **nuevo** `ClasesDeTarea.PuedeBuscarEnInternet` (lista blanca `Trabajo` + `ChatLibre`) |
| Application | `Motor/IMotorAgentes.cs` | `IniciarChatLibreAsync(..., bool permiteBusquedaWeb = false)` (punto 1) |
| Infrastructure | `Services/Motor/ServicioTareas.cs` | wrapper del chat libre y `IniciarPlataformaAsync` toman el parametro (puntos 1-2); `PermiteBusquedaWeb` se **setea** en el `new TareaAgente` (punto 3, antes no existia la linea); ajuste y `OfreceBusquedaWeb` pasan al predicado (puntos 5-6) |
| Infrastructure | `Services/Motor/ResolvedorHerramientas.cs` | el gate `busquedaOfrecida` usa el predicado en vez de `trabajo` (punto 4) |
| Web | `Models/ChatLibreViewModels.cs` | `PermiteBusquedaWeb` + `OfreceBusquedaWeb` |
| Web | `Controllers/ChatLibreController.cs` | inyecta `IOptions<BusquedaWebOptions>` (no lo tenia), arma `OfreceBusquedaWeb` y pasa la marca al servicio |
| Web | `Views/ChatLibre/Index.cshtml` | la casilla al lado del partial de adjuntos, dentro del `@if (Model.OfreceBusquedaWeb)` |
| Tests | `BusquedaWebEnChatLibreTests.cs` (**nuevo**, 12 casos) | CA-01.1..CA-01.6, con **un test por cada uno** de los otros tres agentes de plataforma |
| Tests | `ChatLibreTests.cs` | el comentario de `OfreceBusquedaWeb` (la asercion no cambia: ese entorno no configura `BusquedaWeb`, asi que lo que la apaga ahora es la fail-closed, no el tipo) |

**Migraciones EF: ninguna.** `TareasAgente.PermiteBusquedaWeb` ya existia para toda tarea (`Tareas.cs:145`); lo que
faltaba era setearlo en el arranque de plataforma. `dotnet ef migrations` no se corrio y no hay archivos nuevos en
`Data/Migrations`.

### Evidencia

- `dotnet build OlvidataAgentes.slnx` -> **Compilacion correcta**, 0 errores (las 15 advertencias son las de siempre:
  `NU1902` de ImageSharp, `NU1510`, y tres `xUnit20xx` en tests preexistentes).
- `dotnet test tests/OlvidataAgentes.Tests` -> **1176 verdes, 0 con error, 0 omitidos** (32 s). Partia de 1164: +12
  son los casos nuevos (9 `[Fact]` + 3 del `[Theory]` de la compuerta cerrada). Medido **sin pipe**: salida a archivo
  y `grep` despues, con el codigo de salida en 0.

### Pruebas minimas para QA

1. **CA-01.1** Chat libre nuevo con `BusquedaWeb:Habilitada=true` y `PrecioPorBusquedaUsd` > 0: la casilla esta al
   lado de *Adjuntar documentos*, **apagada**, y con el `title` de siempre al pasar el mouse. Mandar el mensaje y
   abrir el cuadro de ajuste: la casilla esta ahi tambien, con la marca que trae la tarea.
2. **CA-01.2** Poner `PrecioPorBusquedaUsd` en 0 (o `Habilitada` en false) y recargar: la casilla **no aparece** ni en
   el arranque ni en el ajuste. Forzar el POST igual (DevTools, agregando `PermiteBusquedaWeb=true`): la tarea arranca
   y **no** busca.
3. **CA-01.3/CA-01.4** Con la casilla marcada, preguntar algo que exija internet: el costo de la busqueda aparece en
   el paso y en el costo del hilo, y no se pasa de `MaxBusquedasPorTarea` en un turno.
4. **CA-01.5** Abrir *Configurar conversando*, *Repartir trabajo* y *Contame que repetis*: la casilla **no esta** en
   ninguno, ni al arrancar ni en el ajuste. Forzar `permiteBusquedaWeb=true` en el POST del ajuste de cada uno: la
   tarea sigue sin buscar.
5. **CA-01.6** En la ficha del agente / el detalle del paso, `buscar_en_internet` **no** figura entre las
   herramientas que corrio el motor, y no genera pedido de aprobacion del guardia de destinos.
6. **Regresion del punto 5** Chat libre con la casilla marcada: mandar un ajuste **sin tocar la casilla**. Tiene que
   seguir marcada (antes de M29 esta era la linea que la apagaba sola).
7. **Regresion del efecto lateral** Consulta del portal del cliente: el cuadro de ajuste ya **no** muestra la casilla.
   Antes la mostraba y no hacia nada.

### Checklist de merge

- [x] Build limpio y 1176 tests verdes.
- [x] Sin migracion EF (verificado: `Data/Migrations` sin archivos nuevos).
- [x] Logica en services; el controller solo arma el ViewModel y pasa la marca.
- [x] Casilla copiada tal cual (D-05): mismo texto y mismo `title`, sin rediseno.
- [x] `MaxBusquedasPorTarea` y los valores de M6 sin tocar.
- [x] Castellano rioplatense en UI y comentarios.
- [x] Commit local, sin push y sin deploy.
- [ ] Frente B (documento sin cliente, con migracion): **fuera de esta tanda**, sigue pendiente.
