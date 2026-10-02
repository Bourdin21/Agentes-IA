# Memoria - Implementador

## Proyecto: eleven-la-plata
## Ultima actualizacion: 2026-08-20

## Definiciones vigentes

### Escaneo de reutilización cross-proyecto
- `docs/patrones/catalogo.yml`: sin match (la única coincidencia textual de "contador" es un contador de filas de importación, sin relación).
- Barrido de `docs/*/definiciones/5-implementador.md`: sin match funcional. Los hits de "contador" en otros proyectos son numeradores de factura (`ganaderia` → `ContadorFactura`) o contadores de UI/importación (`crm-olvidata`, `la-platense`, `vinosefue`, `marihogar`) — nada relacionado con facturación por contador de copias de equipos de impresión.
- **Decisión:** implementar en el propio proyecto reutilizando el código ya existente de `AlquilerService.CreateAsync` (extraído a métodos privados compartidos). No se agrega nada al catálogo: la lógica es específica del dominio de este cliente, no es un componente genérico reutilizable.

### H1 — Fix de validación de contadores en `AlquilerService.UpdateAsync` (2026-08-20)

**Archivo único modificado:** `C:\Sistemas\elevenlaplata\Eleven.Infrastructure\Services\AlquilerService.cs`

**Archivos y capas modificadas**
- **Negocio / Infrastructure** — `Eleven.Infrastructure/Services/AlquilerService.cs`:
  - Nuevo método privado `ValidarContadoresAsync(int maquinaId, DateTime fecha, int contadorBN, int contadorColor)`. Devuelve la tupla `(List<string> Errores, HistoriaContador? ContadorAnterior, HistoriaContador? ContadorSiguiente)`. Se extrajo tal cual del bloque que estaba inline en `CreateAsync` (queries de contador anterior/siguiente + las 4 comparaciones, con el mismo texto de mensajes). **Se devuelven también los contadores adyacentes** porque la "Regla de Negocio Legacy" que decide si insertar un `HistoriaContador` los necesita; devolver solo la lista de errores obligaba a repetir las dos queries.
  - Nuevo método privado `AgregarHistoriaContadorSiCorresponde(maquinaId, fecha, contadorBN, contadorColor, contadorAnterior, contadorSiguiente)`: encapsula la condición de 5 cláusulas de la "Regla de Negocio Legacy" y hace el `_context.Contadores.Add(...)`. No hace `SaveChanges` (queda a cargo del llamador, igual que antes).
  - `CreateAsync`: reemplaza el bloque inline por las dos llamadas. **Cero cambio funcional** — mismo orden de operaciones, mismos mensajes, mismo `ServiceResult<int>.CreateError("Error en la validación de contadores", validationErrors)`. Se conservó tal cual el pre-chequeo `maquina == null → "Máquina no encontrada."` que ya tenía.
  - `UpdateAsync`: agrega `bool maquinaCambio = alquiler.MaquinaId != dto.MaquinaId;` calculado **antes** de sobreescribir la entidad (la instancia viene de `FindAsync`, o sea el valor persistido en base). Si `maquinaCambio`, llama a `ValidarContadoresAsync` con los datos nuevos y, ante errores, hace `return ServiceResult.CreateError("Error en la validación de contadores", validationErrors)` **sin haber tocado ni un campo de la entidad**. Si pasa, tras asignar los campos llama a `AgregarHistoriaContadorSiCorresponde` con los adyacentes ya obtenidos. Si `maquinaCambio == false`, el método corre exactamente igual que antes del fix (ni una query extra).
- **Presentación:** sin cambios. `AlquileresController.Edit` (POST, líneas 131-140) ya vuelca `result.Errors` a `ModelState` con el mismo patrón que `Create`; `AlquilerEditViewModel` ya trae `MaquinaId`/`ContadorBNInicial`/`ContadorColorInicial` requeridos.
- **Datos:** sin cambios de esquema.

### Migraciones EF generadas
Ninguna. No hubo cambios de entidades ni de configuración EF.

### Riesgos residuales
- **Regresión en Create (bajo):** el refactor es un mover-código 1:1 verificado por relectura; la única diferencia real es que `ValidarContadoresAsync` hace su propio `_context.Maquinas.FindAsync(maquinaId)`. En `CreateAsync` esa máquina ya fue traída al change tracker de EF renglones antes, así que resuelve en memoria (sin roundtrip extra ni riesgo de leer otro estado).
- **Fricción de UX esperada y deliberada:** los alquileres migrados del sistema viejo tienen `ContadorBNInicial`/`ContadorColorInicial` en 0. La primera vez que alguien le cambie la máquina a uno de ellos, la validación nueva lo va a obligar a cargar un contador inicial real. Es el comportamiento correcto (CA1), pero puede sorprender — vale avisarlo al cliente.
- **Fuera de alcance, sigue vigente:** cambiar la máquina de un alquiler sigue reescribiendo retroactivamente "de qué máquina fue" todo el alquiler (`Alquiler.MaquinaId` es escalar). Este fix garantiza que el dato que se guarda es consistente, pero NO conserva el historial multi-máquina — decisión explícita del Análisis (H1, alcance excluido).
- `ValidarContadoresAsync` consulta `_context.Contadores` sin filtrar `DeletedAt == null`, igual que hacía el código original de `CreateAsync`. Se preservó el comportamiento legacy a propósito (no es un refactor pedido). `GetDetailsAsync` sí filtra soft-deletes — la inconsistencia es preexistente, no introducida acá.

### Próximos pasos pendientes
- QA sobre las 5 pruebas funcionales de `3-arquitecto-mvc.md` (sección "Estrategia de pruebas funcionales"). Prioridad en la prueba 4 (regresión de alta) por el refactor.
- H2 (Avisos/Notifications nunca disparados) y H3–H7 siguen sin implementar, pendientes de definición con el cliente.

## Historial de ajustes
- 2026-08-20: H1 implementado. Un solo archivo (`AlquilerService.cs`), 2 métodos privados nuevos + condicional en `UpdateAsync`, sin migración EF, sin cambios en Web. `dotnet build Eleven.slnx` → "Compilación correcta", 0 errores, 18 warnings todos preexistentes. Sin smoke test propio (por regla del rol): se entregó guía manual de verificación al usuario.

---

## Implementación — Lote 2026-10-01 (F1-F5)

Sobre Arquitectura del 2026-10-01. **Sin migración EF, sin cambios de esquema.** Rama `dev`. `dotnet build Eleven.slnx` → "Compilación correcta", 0 errores, 9 warnings, todos preexistentes y en archivos no tocados (`IncidenciaService.cs`, `ContratoService.cs`, `HomeController.cs`, NU1902 de MailKit/MimeKit).

### Resultado del escaneo de reutilización
- `docs/patrones/cat_resumen.txt` → **PAT-008** (toda columna visible tiene filtro) aplica a F4 como deuda inversa: existía filtro por comprobante sin columna. Se cierra.
- Reutilización interna del propio repo, ya identificada en Arquitectura y confirmada leyendo el código: `MovimientosController.CreateUnificado` (POST) como patrón de redirect para F3, y `AlquilerService.ValidarContadoresAsync` (del fix H1 del 2026-08-20) como criterio único para F5.
- Decisión cross-proyecto reutilizada: **marihogar CR-14** (desempate determinístico por `Id` ante `Fecha` repetida) para F1.
- No se construyó ningún criterio nuevo desde cero.

### Cambios por capa

**Negocio / Infrastructure**
- `Eleven.Infrastructure/Services/MovimientoService.cs` (F1) — `GetDataTableAsync`: `.ThenByDescending(m => m.Id)` en la rama `desc` y `.ThenBy(m => m.Id)` en la `asc`. El desempate va **en la query**, no en memoria: el listado es DataTables server-side con `Skip/Take` y sin orden total MySQL puede repetir o perder filas entre páginas — o sea el cambio arregla también ese bug latente de paginación. `GetSaldosAcumuladosAsync` no se tocó (ya ordenaba por `Fecha, Id`). Ningún importe, saldo ni acumulado cambia: es orden de presentación (CA-F1.3).
- `Eleven.Infrastructure/Services/ContadorValidator.cs` (F5, **archivo nuevo**) — clase `internal static` con `ValidarAsync(AppDbContext, maquinaId, fecha, contadorBN, contadorColor, int? excludeId = null)`. Es `AlquilerService.ValidarContadoresAsync` **movido tal cual**, con dos agregados: el parámetro opcional `excludeId` (excluye la fila que se está editando de la búsqueda de anterior/siguiente) y el formato de los números con separador de miles (`ToString("N0", CultureInfo("es-AR"))`, CA-F5.6 → "El contador B/N debe ser mayor o igual a 4.018.041"). Se eligió la opción recomendada por Arquitectura (mover a lugar compartido) sobre la alternativa de replicar: un solo criterio, un solo texto.
- `Eleven.Infrastructure/Services/AlquilerService.cs` (F5) — `ValidarContadoresAsync` queda como **delegación de una línea** a `ContadorValidator.ValidarAsync`. Misma firma, mismo tipo de retorno, mismos llamadores (`CreateAsync:151` y `UpdateAsync:205`) sin tocar. `AgregarHistoriaContadorSiCorresponde` **no se modificó** — ver "Desvío respecto de Arquitectura" más abajo.
- `Eleven.Infrastructure/Services/MaquinaService.cs` (F5) — `CreateContadorAsync` y `UpdateContadorAsync` ahora llaman a `ContadorValidator.ValidarAsync` **antes de persistir** y cortan con `ServiceResult.CreateError("Error en la validación de contadores", errores)`, exactamente el mismo contrato de error que ya usa `AlquilerService` (y que los controllers ya saben volcar a `ModelState`). En `UpdateContadorAsync` se pasa `entity.Id` como `excludeId`, si no la fila se valida contra sí misma y nunca pasa.

**Presentación / Web**
- `Eleven.Web/Controllers/MovimientosController.cs` (F2) — `Create` (GET) inicializa `TipoMovimiento = TipoMovimiento.Egreso` en el ViewModel. **No se tocó el default del `enum TipoMovimiento`**: lo comparten `CreateUnificado`, los filtros y otros consumidores. El usuario puede cambiarlo libremente; no se agregó ninguna validación (CA-F2.2). `CreateUnificado` sin cambios (CA-F2.3).
- `Eleven.Web/Controllers/MovimientosController.cs` (F3) — `Create` (POST) devuelve `RedirectToAction("Details", "Cuentas", new { id = vm.CuentaId })` cuando `vm.CuentaId > 0`, y conserva el `RedirectToAction(nameof(Index))` cuando no hay cuenta de contexto (CA-F3.3). En transferencia `vm.CuentaId` es la cuenta **origen** (CA-F3.4). Sin `returnUrl`: el `cuentaId` ya está en el VM. `TempData["SuccessMessage"]` se setea igual que antes, así que el mensaje aparece en el destino nuevo (CA-F3.2).
- `Eleven.Web/Views/Cuentas/Details.cshtml` y `Eleven.Web/Views/Movimientos/Index.cshtml` (F4) — `<th>Nro. Comprobante</th>` y entrada `{ data: 'numeroComprobante', render: ... }` **inmediatamente después de la fecha**. Sin comprobante renderiza el guion largo en gris (`<span class="text-muted">`), igual que `motivoNombre` y `notas` en esas mismas grillas (CA-F4.2). Cambio de vista puro: `NumeroComprobante` ya viajaba en `MovimientoDto`.
  - **Riesgo de índices verificado y descartado:** ninguna de las dos vistas usa `columnDefs`/`targets`. El único `order: [[0, 'desc']]` apunta a la columna 0 (fecha), que no se movió. El `sortColumn` que se manda al server se resuelve **por nombre** (`d.columns[d.order[0].column].data`), no por índice fijo. Conteo `<th>` vs `columns` revalidado: 8 y 8 en ambas vistas. JS de ambas vistas validado con `node --check` (previo strip de expresiones Razor) → OK.

**Datos:** sin cambios.

### Migraciones EF generadas
**Ninguna**, como preveía Arquitectura.

### Desvío respecto de Arquitectura (decisión a revisar por el orquestador)
Arquitectura pedía que `AlquilerService.AgregarHistoriaContadorSiCorresponde` "deje de insertar sin comparar en el caso *sin anterior ni siguiente*". **No se implementó, a propósito**, por dos motivos:
1. Ese caso es exactamente el de **CA-F5.4 y la prueba funcional 8** — máquina sin ningún contador previo debe aceptar cualquier valor, 0 incluido. No hay con qué comparar: el código no puede distinguir "máquina recién instalada cargada con 0" de "campo dejado en blanco". Hacerlo rechazar rompería un criterio de aceptación aprobado.
2. El alta de alquiler **ya validaba** antes de este lote: `CreateAsync:151` y `UpdateAsync:205` llaman a `ValidarContadoresAsync` desde el fix H1. La brecha real de F5 estaba **solo** en `MaquinaService` (carga manual sin validación alguna), que es además lo que los datos de producción señalan como origen dominante (117 de 126 filas con BN y Color en 0, solo 15 coincidentes con fecha de alquiler).

Con el cambio aplicado, CA-F5.1 a CA-F5.6 y las pruebas 7 a 12 quedan cubiertas igual. Si el owner quiere además bloquear el 0 en máquina nueva, es un cambio de la regla aprobada (contradice CA-F5.4) y debería volver a Diseño.

### Alcance de F4: 2 grillas, no 3
Arquitectura y Diseño hablan de "las 3 grillas de movimientos". En el repo existen **dos**: `Cuentas/Details.cshtml` y `Movimientos/Index.cshtml` (verificado con `grep -rln "importeConSigno|Movimientos/GetDataTable" Eleven.Web/Views/`). La cuenta corriente de cliente **no tiene grilla propia**: `Clientes/Details.cshtml:336` linkea a `/Cuentas/Details/@cc.Id`, que es la misma grilla ya modificada. O sea, los 3 puntos de uso del requerimiento quedan cubiertos con 2 archivos. CA-F4.1 se cumple.

### Evidencia de build
```
dotnet build Eleven.slnx
Compilación correcta.
    9 Advertencia(s)
    0 Errores
```
Ningún warning nuevo: los 9 son preexistentes y están en `IncidenciaService.cs` (4x CS8602), `ContratoService.cs` (CS8321), `HomeController.cs` (CS0114) y los NU1902 de MailKit/MimeKit. Ninguno cae en una línea tocada.

### Riesgos residuales
- **F5 puede frenar una carga que el operador venía haciendo todos los meses (Medio).** La regla `>= anterior` solo rechaza retrocesos, que son siempre errores reales, pero el operador que venía guardando con el campo vacío ahora va a ver un error. **Avisar al cliente antes del deploy.**
- **Regresión del alta de alquiler (Medio).** `ValidarContadoresAsync` cambió de implementación propia a delegación; el cuerpo es el mismo salvo `excludeId` (que los llamadores de `AlquilerService` no pasan, así que su comportamiento es idéntico) y el formato de los números del mensaje. Igual, el refactor de H1 vuelve a quedar bajo la lupa: **prueba 12 es la prioritaria**.
- **Mensajes de error con formato nuevo.** Cualquier test o script que compare el texto exacto "debe ser mayor o igual a 4018041" ahora ve "4.018.041".
- **Las 110 filas en 0 de producción siguen ahí.** La validación es prospectiva por decisión explícita: no se corrigió, migró ni tocó ninguna. El saneamiento es trabajo aparte.
- `ContadorValidator` consulta `_context.Contadores` sin filtrar `DeletedAt == null`, igual que hacía el código original. Comportamiento legacy preservado a propósito — inconsistencia preexistente, no introducida acá.

### Pruebas mínimas para QA
Las 12 pruebas funcionales de `3-arquitecto-mvc.md`. **Prioridad:**
1. **Prueba 12 — regresión del alta de alquiler** (el refactor de H1 vuelve a quedar bajo la lupa por F5).
2. **Prueba 1 — paginación de la grilla de movimientos** además del acumulado: paginar hacia adelante y atrás sin que se repita ni se pierda una fila.
3. Prueba 8 (máquina sin contadores acepta 0) y prueba 9 (editar sin cambiar el valor guarda) — son los dos falsos positivos más probables de F5.

### Checklist de merge
- [x] Build limpio, sin warnings nuevos.
- [x] Sin migración EF ni cambios de esquema.
- [x] Lógica de negocio en Services, nada en Controllers (F2/F3 son solo ViewModel y redirect).
- [x] JS de las vistas validado (`node --check`); conteo `<th>` vs `columns` revalidado.
- [x] Sin referencias por índice numérico afectadas en DataTables.
- [ ] **No deployar** — el deploy lo autoriza el owner aparte, y requiere avisar al cliente del cambio de comportamiento de F5.
- [ ] QA sobre las 12 pruebas funcionales.
- [ ] Resolver con el orquestador el desvío sobre `AgregarHistoriaContadorSiCorresponde` y la discrepancia "3 grillas vs 2".

## Implementación — Lote 2026-10-01 bis (ELV-004 + orden por columna)

Sobre el brief del orquestador del 2026-10-01 bis. **Sin migración EF, sin cambios de esquema.** Rama `dev`, sobre el working tree del lote F1-F5 (sin commitear, con GO de QA) — ninguno de esos cambios se tocó ni se revirtió. `dotnet build Eleven.slnx -t:Compile` → "Compilación correcta", **0 errores**, 14 warnings todos preexistentes.

### Resultado del escaneo de reutilización
- `docs/patrones/cat_resumen.txt` → **sin entrada** para "orden por columna en DataTable server-side" ni para "piso de validación en ajuste masivo". Paso 1 negativo como patrón reutilizable.
- Paso 2/3 → el antecedente real no está en el catálogo de patrones sino en `docs/qa/regresiones-manuales.yml`: **MH-015, MH-018 y CRM-003** son la misma clase de bug (columna ordenable sin rama en el switch de `SortColumn`). De ahí se tomó la **regla preventiva** de `MH-015.nota_generalizacion`: *el set de columnas ordenables de la vista y las ramas del switch del service tienen que cubrir exactamente el mismo conjunto*. Y de `MH-018`, el detalle de que **la rama default también tiene que respetar la dirección pedida** (ahí el bug era que la ignoraba).
- **Reutilización interna del propio repo**, que es la que más pesó: `ArticuloService` (línea ~182) ya implementa el patrón `request.SortColumn?.ToLower() switch { ... }` en este mismo proyecto, y `AuditController.GetData` lo implementa del lado Web. Se copió esa forma exacta en `MovimientoService.GetDataTableAsync` en vez de inventar un mapeo nuevo.
- **ELV-004 se construyó nuevo, a propósito.** `ContadorValidator` (del lote anterior) **no se reutilizó**: su regla es monotonicidad entre filas consecutivas de la historia; ELV-004 es un piso absoluto en 0 sobre una mutación masiva. Forzar la reutilización habría acoplado dos reglas que no son la misma. Decisión ya cerrada en el brief.
- **No se agregó ningún patrón al catálogo**: ninguno de los dos cambios es un componente reutilizable (uno es una validación de dominio puntual, el otro un mapeo de columnas propio de esta grilla). La clase de bug ya está catalogada del lado de QA.

### Cambios por capa

**Negocio / Infrastructure**
- `Eleven.Infrastructure/Services/MaquinaService.cs` — `AjustarContadoresAsync` (ELV-004). Se agregó un bloque de validación **previo a cualquier mutación**, que solo corre si `cantidadAAjustar < 0`:
  1. Junta en una lista todos los valores que el ajuste va a tocar: `ContadorBN` de cada fila de `HistoriaContadores`, `ContadorColor` **solo si `maquina.Color`** (misma condición que la mutación de abajo: en una máquina B/N ese valor queda intacto y no debe limitar el ajuste), y `Durabilidad` + `ContadorAsignacion` de cada repuesto (CA-3).
  2. `ajusteMinimoAdmitido = Math.Min(0, -valoresAfectados.Min())` — el valor más chico es el que toca el piso primero, así que define el límite para toda la máquina. El `Math.Min(0, ...)` cubre el caso de **datos ya corruptos por el propio defecto** (la máquina 6 que QA dejó en negativo): si hoy hay un valor negativo, `-min` daría un "mínimo admitido" positivo, que como piso de un ajuste negativo no tiene sentido; con el clamp, ahí no se admite ningún ajuste negativo hasta que esos valores se corrijan, y el mensaje dice "no puede ser menor a 0".
  3. Si `cantidadAAjustar < ajusteMinimoAdmitido` → `return ServiceResult.CreateError(detalle, new List<string> { detalle })`. **Rechazo total, sin aplicar nada ni parcialmente** (CA-1): se retorna antes de los dos `foreach` y antes del `SaveChangesAsync`. No se clampea el ajuste — decisión cerrada del brief.
  4. El texto usa `ToString("N0", new CultureInfo("es-AR"))` → *"El ajuste no puede ser menor a -1.234.567: dejaría contadores en negativo."* (CA-2), mismo criterio de formato que `ContadorValidator` del lote anterior.
  - Un ajuste negativo que no deja nada en negativo (CA-4) y cualquier ajuste positivo (CA-5) **no pasan por la validación en absoluto** (el positivo ni entra al bloque) y siguen el camino original sin cambios. Una máquina sin contadores ni repuestos (`valoresAfectados.Count == 0`) tampoco se bloquea.
- `Eleven.Infrastructure/Services/MovimientoService.cs` — `GetDataTableAsync` (orden por columna). El `OrderBy` fijo por `Fecha` se reemplazó por un `switch` sobre `request.SortColumn?.ToLower()` con una rama por cada columna ordenable de las grillas:

  | `sortColumn` (el `data` de la columna) | Orden en SQL |
  |---|---|
  | `fecha` (y cualquier valor no mapeado) | `Fecha` — rama default |
  | `numerocomprobante` | `NumeroComprobante` |
  | `cuentanombre` (solo existe en `Movimientos/Index`) | `Cuenta.Nombre` |
  | `tipomovimiento` | `TipoMovimiento` (el enum, por valor) |
  | `motivonombre` | `Motivo.Nombre` |
  | `notas` | `Notas` |
  | `importeconsigno` | condicional `Ingreso → +abs`, `Egreso → -abs`, resto `Importe` |

  - **El mapeo no es por índice de columna** y por eso la diferencia de cantidad de columnas entre las dos grillas (8 vs 9) no importa: las dos vistas ya mandaban `sortColumn: d.columns[d.order[0].column].data`, o sea el **nombre** del campo del DTO, resuelto en el browser. Verificado en las dos vistas. Un índice compartido habría sido un bug; no hizo falta tocar ese bloque de JS.
  - **Desempate por `Id` en TODAS las ramas** (CA-9), no solo en la de fecha: ninguna de estas columnas define un orden total por sí sola (hay muchísimos movimientos con el mismo importe, el mismo motivo o la misma fecha), y con `Skip/Take` un orden no total deja que MySQL repita o pierda filas entre páginas. Se desempata por `Id` y no por `CreatedAt` por lo mismo que en F1: las filas migradas tienen `CreatedAt` del momento de la migración.
  - **La rama default respeta la dirección pedida** (`desc` → `OrderByDescending`), que es exactamente el sub-bug de MH-018. Con `order: [[0, 'desc']]` en las dos vistas, el orden por defecto sigue siendo `Fecha` descendente (CA-10).
  - `importeConSigno` se ordena por una **réplica en expresión** de la propiedad calculada del dominio, no por `Importe`: la grilla muestra el importe con signo, así que ordenar por `Importe` daría un orden que no coincide con lo que se ve (un egreso de $1.000 se pinta `-1.000` y tiene que quedar **por debajo** de un ingreso de $100). `Movimiento.ImporteConSigno` es una propiedad calculada en memoria y no se puede usar en el árbol de expresión, pero su definición es un `switch` sobre `TipoMovimiento` que EF traduce a un `CASE` de SQL.
  - **`GetSaldosAcumuladosAsync` no se tocó** (CA-11). Sigue ordenando por `(Fecha, Id)` sobre el historial completo de la cuenta y sigue devolviendo un diccionario `Id → saldo`; el orden de pantalla no lo alcanza por construcción, porque el acumulado se busca **por Id** sobre la página ya ordenada. El riesgo que el brief marcaba como no negociable no se materializó: las dos cosas están desacopladas desde F1.

**Presentación / Web**
- `Eleven.Web/Controllers/MaquinasController.cs` — `AjustarContadores` (POST): la rama de error pasó de `result.Message` a `ArmarMensajeDeError(result)`, el helper que ya existía desde ELV-003 (CA-6). El detalle con el mínimo viaja en `ServiceResult.Errors` **y además** en `Message`, así que el mensaje llega igual por cualquiera de los dos caminos.
- `Eleven.Web/Views/Maquinas/Index.cshtml` — el `text` del SweetAlert de "Ajustar Contadores" pasó de *"Ingrese la cantidad a ajustar (puede ser negativo):"* a *"Ingrese la cantidad a ajustar. Puede ser negativa, siempre que ningún contador ni insumo de la máquina quede por debajo de cero."* El piso exacto depende de los datos de cada máquina y lo calcula el servicio, así que la UI anuncia **la regla**, no el número; el límite concreto llega en el mensaje de error. Es el único punto de entrada al ajuste en todo el repo (verificado por grep sobre `Eleven.Web/Views/`): no hay botón de ajuste en `Maquinas/Details`.
- `Eleven.Web/Views/Cuentas/Details.cshtml` y `Eleven.Web/Views/Movimientos/Index.cshtml` — se **quitó** el `orderable: false` de la columna `numeroComprobante`, que era el parche puntual de ELV-006 del lote anterior. Ahora el servicio sabe ordenar por `NumeroComprobante`, así que la cabecera vuelve a ser clickeable y ordena de verdad (CA-8: el objetivo es que ordenen, no apagar cabeceras). El comentario del parche se reemplazó por la explicación del estado nuevo; el `render` explícito de `null`/`undefined`/`''` de ELV-007 **no se tocó**.
  - **Cobertura vista ↔ switch revalidada columna por columna**, que es la regla preventiva de MH-015:
    - `Cuentas/Details` (8 columnas): `fecha`→default, `numeroComprobante`✓, `tipoMovimiento`✓, `motivoNombre`✓, `notas`✓, `importeConSigno`✓, `saldoAcumulado`→`orderable: false`, acciones (`id`)→`orderable: false`.
    - `Movimientos/Index` (9 columnas): las mismas menos `saldoAcumulado`, más `cuentaNombre`✓.
    - Las dos únicas columnas que quedan `orderable: false` son las que genuinamente no se pueden ordenar en el servidor: `saldoAcumulado` (se calcula en memoria y ya estaba en false) y la de acciones (no es un dato). **No queda ninguna cabecera que prometa un orden que no aplica.**

**Datos:** sin cambios.

### Migraciones EF generadas
**Ninguna.** Ningún cambio de entidad, de configuración ni de esquema.

### Evidencia de build
```
dotnet build Eleven.slnx -t:Compile
Compilación correcta.
    14 Advertencia(s)
    0 Errores
```
Se usó `-t:Compile` (compila sin copiar a `bin/`) porque la app está levantada y tiene tomado el `.exe`, como indicaba el brief. Ningún warning nuevo: los 14 son los mismos del lote anterior (`IncidenciaService.cs` 4× CS8602, `ContratoService.cs` CS8321, `HomeController.cs` CS0114, NU1902 de MailKit/MimeKit duplicados por proyecto). Ninguno cae en una línea tocada.

JS de las 3 vistas tocadas validado con `node --check` tras strip de expresiones Razor → **OK en las 3**.

### Riesgos y supuestos
- **`ImporteConSigno` ordenado por réplica de expresión (Medio) — el riesgo principal del lote.** La expresión del `OrderBy` duplica la lógica de `Movimiento.ImporteConSigno`. Si alguien cambia la propiedad del dominio y no esta expresión, el orden de la grilla se despega del valor que se muestra, en silencio. No hay forma de evitar la duplicación sin convertir `ImporteConSigno` en columna calculada persistida (cambio de esquema, fuera de alcance). **Para QA: comparar el orden con lo que se ve, no solo que "cambie".**
- **Orden por `Notas` y por `Motivo.Nombre` con nulos (Bajo).** Las dos columnas admiten `null` y MySQL los agrupa en un extremo según la dirección. Es correcto, pero el usuario va a ver un bloque de "—" arriba o abajo. Comportamiento esperado, no defecto.
- **Orden por `tipoMovimiento` ordena por el valor del enum**, no alfabético por la etiqueta: Ingreso(0) → Egreso(1) → Transferencia(2). Es el orden natural del dominio y coincide con el dato que viaja en el DTO.
- ~~**La máquina 6 queda bloqueada para ajustes negativos hasta que se saneen sus contadores.**~~ **CORREGIDO POR EL ORQUESTADOR (2026-10-01): esto NO es cierto.** QA reprodujo ELV-004 sobre un **clon** (`eleven_qa_b`, ya eliminado), no sobre producción. Consulta de solo lectura a producción: **0 contadores negativos en toda la tabla**, y la máquina 6 tiene sus 68 contadores sanos (de 537.895 a 5.915.812). No hay nada que sanear por este concepto y **no hay que sumar nada a la planilla**. El clamp `Math.Min(0, ...)` sigue siendo correcto como defensa, pero hoy no se activa sobre ningún dato real.
- **Supuesto sobre el formato del mensaje de CA-2.** El brief pide "nombra el ajuste negativo máximo admitido". Se interpretó como el **ajuste** (ej. `-1.234.567`), no como el valor del contador más chico. En el caso de datos ya negativos el mensaje dice `0`, que es el ajuste admitido real.
- Ningún cambio toca producción: **no se commiteó, no se deployó, no se tocó la base de producción.**

### Pruebas mínimas requeridas para QA
**ELV-004** (sobre una máquina de prueba, no la 6, salvo el punto 5):
1. **CA-1/CA-2** — ajuste de `-99999999` sobre una máquina con contadores altos: tiene que **rechazar** mostrando el mínimo con separador de miles es-AR, y **ningún** contador ni repuesto debe haber cambiado (verificar en base, no solo en pantalla: lo que ELV-004 permitía era justamente la mutación).
2. **CA-4** — ajuste negativo chico que no deja nada en negativo: tiene que **aplicarse** y bajar los contadores y los repuestos. Es el falso positivo más probable de este fix.
3. **Borde exacto** — ajuste igual a `-minimoActual`: tiene que **aplicarse** y dejar el valor más chico exactamente en 0. Un ajuste de uno menos tiene que rechazar.
4. **CA-3** — máquina con repuestos cuya `Durabilidad` o `ContadorAsignacion` sea **menor** que el contador más chico: el límite tiene que salir del repuesto, no del contador.
5. **CA-5 / máquina B/N** — ajuste positivo normal, y un ajuste negativo sobre una máquina con `Color = false` cuyo `ContadorColor` esté en 0 o negativo: **no debe bloquear**, porque ese valor no se toca.
6. **CA-6** — el error se ve en pantalla con el detalle, no un genérico.

**Orden por columna** (en las **dos** grillas: `Cuentas/Details` y `Movimientos/Index`):
7. **CA-7/CA-8** — clickear **cada** cabecera clickeable, ida y vuelta (asc y desc), y confirmar que el orden que se ve es el de **esa** columna. Las dos únicas que no deben ser clickeables son Saldo Acumulado y Acciones.
8. **CA-9 — la prueba prioritaria.** Barrido de paginación completo ida y vuelta **con un orden distinto de Fecha** (al menos por `Importe` y por `Motivo`, que son los que más empatan), contando filas: 0 duplicadas, 0 faltantes. Es lo que el desempate por `Id` garantiza y es el bug latente más caro si falla.
9. **CA-11 — la otra prioritaria.** Con la grilla ordenada por `Importe` (y por `Motivo`), verificar que el **saldo acumulado de cada fila sigue siendo el mismo** que con el orden por fecha, y que la primera fila **no anulada en orden cronológico** sigue coincidiendo con el saldo del encabezado. El acumulado no debe seguir el orden de pantalla.
10. **CA-10** — al entrar a cada grilla sin tocar nada, el orden sigue siendo Fecha descendente.
11. **Regresión de ELV-005** — ninguna fila anulada debe devolver `0` en el acumulado (debe pintar "—") **bajo ningún orden**.
12. **Regresión de los filtros** — el orden no debe alterar los filtros (rango de fechas, tipo, motivo, nro. de comprobante) ni el buscador.

### Checklist de salida para merge
- [x] Build limpio (`-t:Compile`), 0 errores, sin warnings nuevos.
- [x] Sin migración EF ni cambios de esquema.
- [x] Lógica de negocio en Services; el Controller solo vuelca el mensaje.
- [x] JS de las 3 vistas validado con `node --check`.
- [x] Cobertura vista ↔ switch de `SortColumn` revalidada columna por columna en las 2 grillas (regla preventiva de MH-015).
- [x] `GetSaldosAcumuladosAsync` sin tocar (CA-11 por construcción).
- [x] Cambios del lote F1-F5 preservados: `ContadorValidator.cs`, `AlquilerService.cs`, `MovimientosController.cs` y el resto del working tree intactos.
- [ ] QA sobre las 12 pruebas de arriba, con prioridad en 8 y 9.
- [ ] **ELV-004 y la causa de fondo de ELV-006 quedan "aplicado, pendiente de re-verificación"** — el cierre lo declara QA.
- [x] ~~Sumar el saneamiento de los contadores en negativo de la máquina 6 a la planilla.~~ **No corresponde:** producción no tiene contadores negativos (verificado 2026-10-01). Los negativos vivieron solo en el clon de QA.
- [ ] **No deployar, no commitear** — lo autoriza el owner aparte.
