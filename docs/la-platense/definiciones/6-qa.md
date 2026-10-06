# Memoria - QA

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-10-06 (v13 — **HOTFIX de transacciones de ventas, rama `hotfix-transacciones-ventas`, commits `c5b27a4`+`7ca5ce3`: GO**, gate de publicacion a produccion. 6/6 criterios en PASS con evidencia ejecutada; arnes 82/82 en 4 corridas y **control positivo contra el codigo roto: 40 fallas** con los importes reproducidos (deuda de $1.000 cobrada 8 veces, saldo -$7.000); la relectura bajo lock verificada **por mutacion** en los 3 metodos del workflow. 1 hallazgo nuevo `LP-034` `minor` no bloqueante. Antes: 2026-10-06 (v12 — Entrega 6 **LOTE 5: presupuestos en PDF y aumento masivo de precios, commit `eec79d4`: NO-GO**, los 14 criterios en PASS pero 2 partes de defecto del alcance — `LP-030` `major` (el aplicar tarda 44-46 s contra los 7,6-8,0 s declarados, medidos sobre una pasada que no escribe) y `LP-029` `minor` (el desglose de IVA del PDF no cierra con su propio total) — mas 3 hallazgos `low` `LP-031`/`LP-032`/`LP-033`. Antes: 2026-10-06 (v11 — Entrega 3 **LOTE 3: recepcion de mercaderia y pagos a proveedores, commit `7cda85b`: GO**, los 14 criterios en PASS; 3 hallazgos nuevos no bloqueantes `LP-024` `major` (carrera del tercer escritor de Producto.Stock, riesgo 1 de liberacion), `LP-025` y `LP-026` `trivial`. Corrida por lotes en paralelo: ver tambien los bloques de los otros lotes mas abajo, cada uno con su propio alcance y su propia base clonada. Antes: v10 LOTE 4 `4246b42` NO-GO, v9 LOTE 2 `4686a27` GO, v8 re-verificacion del Sprint 0, rama `entrega-1-migracion`))
## Ultima validacion de reglas cross-proyecto: 2026-10-06

---

---

# HOTFIX de transacciones de ventas — gate de publicación (QA, 2026-10-06, rama `hotfix-transacciones-ventas`)

Gate de los commits `c5b27a4` + `7ca5ce3` sobre `2580f7c` (= lo publicado hoy). 5 sitios que duplican
plata, vivos en producción. Contexto nuevo: los 6 criterios arrancaron **en FAIL**; no se leyó la
transcripción del implementador, sólo el diff y los mensajes de commit.

## **GO.** 6 de 6 criterios en PASS con evidencia ejecutada. 1 hallazgo `minor` nuevo (`LP-034`), no bloqueante y fuera del alcance del hotfix.

Las dos afirmaciones que el implementador pidió no creerle **se verificaron ejecutando y las dos son
ciertas**. Y el arnés **tiene dientes**: contra el código roto da 40 fallas, reproducidas de forma
independiente con los importes exactos que él reportó.

## Entorno y metodología

- **Fixture fiel a producción, no un clon de dev.** `laplatense_dev` tiene **14** migraciones; la rama
  publicada tiene **8**. Probar el hotfix contra el clon de dev habría sido probarlo contra un esquema
  que producción no tiene. Se creó `laplatense_gate_fix` **desde las 8 migraciones de la rama**
  (verificado: 8 filas en `__EFMigrationsHistory`, 29 tablas) y se espejó a `laplatense_gate_broken` y
  `laplatense_gate_mut`. `laplatense_qa_hotfix` (clon de dev) se usó sólo para el ensayo de locks.
- **El repo del sistema no se tocó.** Los árboles de prueba salieron por `git archive HEAD` al
  scratchpad; el control y los mutantes se armaron ahí con `git show 2580f7c:<archivo>`.
  `git status --porcelain` al cerrar: sólo `?? .claude/`, que ya estaba al abrir la sesión.
- **Producción intacta.** Nada contra `mysql8001.site4now.net`. Los fixtures `laplatense_qa_l1..l6` y
  `laplatense_qa_d9` de los otros lotes no se tocaron.
- **La guarda del arnés se corrió, no se asumió**: apuntado a `laplatense_dev`, a `laplatense_qa_l1` y a
  `mysql8001.site4now.net` **aborta antes de abrir la conexión** en los tres casos. (Efecto colateral: la
  guarda rechaza cualquier base que matchee `laplatense_qa`, así que el clon pedido en el brief
  —`laplatense_qa_hotfix`— **no sirve para correr el arnés**; de ahí el nombre `laplatense_gate_*`.)

## Cobertura por criterio (PASS / FAIL / BLOCKED)

| # | Criterio | Estado | Evidencia observada |
|---|---|---|---|
| 1 | N llamadas simultáneas por conexiones separadas → **un** efecto, en los 5 sitios, con N=3 y N=8 | **PASS** | Arnés **82/82 OK**, corrido **4 veces** (corridas propias, no las del implementador). Confirmar N=3/N=8: 1 éxito, caja $1.420, CC $1.000, stock 98. Facturar: 1 éxito y **AFIP invocado 1 sola vez**. Cobro CC: saldo exacto $0, 1 crédito, $1.000 de caja. Gasto: 2 movimientos, neto $0. Cancelar vs confirmar N=4/N=8: 1 ganador, invariante respetado |
| 2 | **El arnés corrido contra el código roto detecta las fallas** | **PASS** | Control independiente sobre `laplatense_gate_broken`: **42 OK / 40 FALLADAS**, exit 1. Importes reproducidos al centavo: cobro N=8 → **saldo −$7.000, 8 créditos, $8.000 de caja**; N=3 → **−$2.000, $3.000**; gasto N=8 → **9 movimientos, neto +$3.500**; facturar N=8 → **8 invocaciones a AFIP**; confirmar N=8 → $2.840 de caja y $2.000 de CC; cancelar → `borrada=True` **con** caja=1, cc=1, stock=98 |
| 3 | Sin regresión en el camino secuencial, con los mismos importes | **PASS** | Criterio 3 del arnés (8 afirmaciones) **pasa idéntico en el código roto y en el arreglado**: total $2.420, caja $1.420 (el pago en CC no va a caja), CC $1.000, stock 98. Mismos números en los dos ⇒ el camino secuencial no cambió |
| 4 | Confirmar una venta ya confirmada, cobrar sin deuda y anular un gasto ya anulado siguen siendo rechazos explícitos | **PASS** | `4.1` "La venta no está en estado Borrador: no se puede confirmar." + `4.2` el rechazo **no escribió nada** (caja=1 cc=1 stock=98). `6.7` "El cliente no tiene deuda pendiente en su cuenta corriente." `7.5` "Este gasto ya está anulado." Y dos rechazos **nuevos** que el fix agrega: "Este borrador de venta ya está cancelado." y "La venta fue cancelada: no se puede confirmar/facturar." |
| 5 | Nada queda a medio aplicar si una escritura falla — **verificar la afirmación, no aceptarla** | **PASS** | **La afirmación es cierta.** El criterio 2 del arnés (inyección de falla en el INSERT de caja) da las **7 afirmaciones OK idénticas con y sin el fix**: venta en Borrador, 0 caja, 0 CC, stock 100, y el reintento posterior deja **un solo** cierre. La atomicidad la daba el `SaveChanges` único + la transacción implícita de EF, **no** el hotfix. Mérito correctamente atribuido en el comentario del código |
| 6 | El diff se entiende de una sola pasada | **PASS** | 1.126 líneas de diff, de las cuales **32 son código productivo** (27 en `VentaWorkflowService` incluyendo el helper, 3 en `GastoService`, 2 en `CuentaCorrienteClienteService`) + 3 constantes en `BloqueoDeFila` + 755 del arnés. El resto son comentarios, y **los comentarios dicen la verdad**: las 2 afirmaciones centrales se verificaron por mutación (abajo). Sin migración EF — `__EFMigrationsHistory` de la rama = 8, igual que producción |

## Lo que el brief pidió mirar: verificado por **mutación**, no por lectura

La pregunta era si `RelerEstadoBajoLockAsync` **realmente relee bajo lock en los tres métodos** o si hay
algún camino donde la relectura sea decorativa. Se construyeron dos mutantes del árbol arreglado y se les
corrió el mismo arnés. Si el arnés sigue verde con la relectura rota, la garantía era una ilusión.

| Mutante | Qué se rompió | Resultado | Qué prueba |
|---|---|---|---|
| **M3** | La relectura **ocurre** pero se devuelven los valores de la entidad cargada **antes** del lock (relectura decorativa) | **58 OK / 24 FALLADAS** — rompe `1.x` (confirmar: 3 de 3 éxitos, **$4.260** de caja), `5.x` (facturar: **8 invocaciones a AFIP**) y `8.x` (cancelar) | La relectura es **portante en los tres métodos**. El lock solo **no alcanza**: con el lock puesto y la lectura vieja, la plata se duplica igual |
| **M1** | Se quitó `IgnoreQueryFilters()` (se deja la proyección) | **78 OK / 4 FALLADAS**, exactamente el invariante de `8.x`: 8 ganadores de 8, `borrada=True` **con** caja=4, cc=4, stock=92 | La segunda afirmación invisible es cierta: sin `IgnoreQueryFilters` la relectura **no ve** la fila que el soft delete esconde y **parece hecha sin releer** |

**Conclusión: no quedó ningún camino decorativo en los tres métodos del workflow.** Las dos razones que el
implementador dio por las que el patrón mecánico falló son reales y están cerradas.

## Las tres decisiones que el brief pidió juzgar

1. **`ReloadAsync` en `GastoService` (asimetría deliberada) — correcta.** `IGastoService` expone sólo
   `ListarAsync`/`CrearAsync`/`AnularAsync`/`ObtenerGastosMesPorCategoriaAsync`: **no hay baja de gastos**.
   Barrido del repo completo: el único uso de `_gastoRepository` es el `AddAsync` del alta y **nadie
   escribe `Gasto.DeletedAt`**. `Anulado` es columna normal y `ReloadAsync` sí la ve. Verificado, no aceptado.
2. **Bloquear el *cliente* y no un documento en `RegistrarCobroAsync` — correcta, y la granularidad es la
   declarada.** Ensayado con dos sesiones MySQL reales sobre el mismo SQL que emite el helper:
   **mismo cliente → bloquea** (timeout de lock a los 3.271 ms); **clientes distintos → paso libre**
   (234 ms); **id inexistente → paso libre** (199 ms). Serializa lo que tiene que serializar y **no
   serializa de más**. El saldo es un agregado del ledger sin fila propia: bloquear al dueño es el
   equivalente correcto, y la relectura es volver a correr `ObtenerSaldoAsync` ya bajo el lock.
3. **No portar `EsReversion` y revertir por el monto del documento — correcta.** Confirmado que
   `EsReversion` **no existe en ninguna parte de la rama** (0 apariciones fuera del comentario que la
   explica). Y el criterio coincide con **`MH-036`** del catálogo, que es justamente la regla de preferir
   el **monto del documento** por sobre "la suma del ledger hermano". La alternativa descartada (inferir
   la reversión por el signo) habría sido una regla nueva disfrazada de port.

## Máquina de estados (`EstadoVenta`: Borrador=1, Facturada=2, Anulada=3, Confirmada=4)

| Transición | Estado | Evidencia |
|---|---|---|
| Borrador → Confirmada | **PASS** | Secuencial y con N=3/N=8 concurrentes: exactamente una |
| Confirmada → Facturada | **PASS** | Una sola, con **una** invocación a AFIP (doble de AFIP que cuenta llamadas) |
| Borrador → cancelada (`DeletedAt`, **sin** tocar `Estado`) | **PASS** | La segunda cancelación se rechaza con mensaje propio; el invariante "nunca borrada **con** plata movida" se sostiene en N=4 y N=8 |
| Borrador ⇄ cancelación, carrera cruzada | **PASS** | Un solo ganador; **el ganador es legítimamente no determinista** (en mis 4 corridas ganó confirmar con N=4 y cancelar con N=8) y el estado final queda coherente con el ganador en los dos sentidos |
| → Anulada | **N/A** | `EstadoVenta.Anulada` existe en el enum pero **`IVentaWorkflowService` no expone `AnularAsync`**: la transición no está implementada en la rama publicada |

## Cobertura del catálogo cross-proyecto

| Item | Severidad | Aplica | Resultado |
|---|---|---|---|
| `LP-018` — el neto vivo se lee antes de la transacción y nada bloquea la fila (anulación de venta) | `critical` | **No** | Misma clase de defecto, pero `AnularAsync` **no existe en la rama publicada** (verificado en `IVentaWorkflowService`). N/A para este deploy |
| `MH-036` — espejar la suma del ledger hermano en vez del monto del documento | `high` | **Sí** | **PASS por diseño**: la reversión del gasto va por `Gasto.Monto`. Es la decisión que el item prescribe |
| `REG-001` / `MH-016` — `RowVersion` en MySQL | `blocker` / `minor` | **Sí (como prohibición)** | **PASS**: el fix **no** usa `RowVersion`. Ninguna entidad del proyecto lo tiene; se resolvió con `SELECT … FOR UPDATE` dentro de transacción, que es la vía correcta en este stack |
| `LP-023` — leer-y-marcar no atómico (aviso de pagos a proveedor) | `major` | **No** | El módulo de proveedores no existe en la rama publicada (entra por una de las 6 migraciones que esta rama no tiene) |
| `MH-001` — `IN`/`.Contains()`/`Any()` sobre colección local de **strings** | — | **Sí** | **PASS, sin violación nueva.** `BloqueoDeFila` arma SQL a mano con parámetros `int` (no es traducción de LINQ) y la lista vacía sale por un `return` previo. Las apariciones de `.Contains()` en los archivos tocados son preexistentes, en los listados, y sobre colecciones de `int`/enum, no de strings |
| `LP-009` — toda escritura de caja pasa por `ValidarPeriodoAbiertoAsync` | `major` | **Sí** | **PASS, y el fix no la salteó al mover la transacción.** `ConfirmarAsync`: tx 580 → validación 629 → commit 668. `RegistrarCobroAsync`: tx 191 → validación 206 → commit 259. `GastoService.AnularAsync`: tx 266 → validación 299 → commit 314. Las tres **dentro** de la transacción. `FacturarAsync` y `CancelarBorradorAsync` no la necesitan: verificado que **no escriben caja** (facturar sólo toca `CAE`, `VencimientoCAE` y `Estado`) |
| Día de negocio por `ArgentinaTime` (producción corre en huso Pacífico) | — | **Sí** | **PASS**: el hotfix **no toca ninguna frontera de día/mes**. `diaNegocio`, `ArgentinaTime.Hoy` y `InicioDiaUtc` quedaron exactamente como estaban; el diff sólo mueve el `BeginTransaction` y agrega lock + relectura |

## Cobertura de reglas nuevas / modificadas desde la última corrida

`6-qa.md` declaraba "Ultima validacion de reglas cross-proyecto: **2026-10-06**" (hoy, puesta por un lote
anterior de esta misma corrida). Diferencial contra el estado vigente:
`git log --since=2026-10-06 -- .github/instructions/32-estandares-qa-implementador.instructions.md docs/qa/regresiones-manuales.yml`
devuelve **0 commits**. **No hay reglas nuevas ni modificadas que ejecutar en este lote**; el estado de
reglas que validó el lote anterior sigue vigente y se pasa como dato a los lotes siguientes.

## Defectos

### `LP-034` (`minor`, **nuevo**) — la relectura del **stock** sí puede quedar decorativa: `ReloadAsync` sobre un `Producto` soft-borrado

Es el **único** camino decorativo que quedó, y no está en el estado de la venta (que está cerrado) sino en
el stock, cinco líneas más abajo, en `ConfirmarAsync`:

```csharp
foreach (var item in venta.Items.Where(i => i.DeletedAt == null))
    await _context.Entry(item.Producto).ReloadAsync();
```

El razonamiento de la asimetría se hizo para `Gasto` (correcto, no hay baja) y para `Venta` (correcto, se
cerró con el helper), **pero no se hizo para `Producto`** — y `Producto` **sí se puede borrar**:
`Producto : SoftDestroyable`, el filtro global `HasQueryFilter(e => e.DeletedAt == null)` lo alcanza, e
`IProductoService` expone `EliminarAsync` y `EliminarLoteAsync`, cuyo `EliminarAsync` llama a
`_repository.DeleteAsync(entity)` (que escribe `DeletedAt`) **sin ninguna guarda de uso**: borra un
producto que está en un borrador de venta.

Consecuencia: si un producto se borra en la ventana entre la carga de la venta y el lock, `ReloadAsync` no
trae nada, EF deja la entidad **detached** y el `item.Producto.Stock -= item.Cantidad` de abajo se aplica a
una entidad que `SaveChanges` ya no trackea → **la venta se confirma con la plata correcta y el stock no se
descuenta, en silencio**. Es exactamente el modo de falla (b) que el implementador documentó para `Venta`.

**Por qué es `minor` y no bloquea el deploy:**
- **No duplica plata.** La guarda de la venta es sólida (probada por M1/M3): caja, CC y comprobantes quedan
  correctos. Lo único afectado es el descuento de stock.
- **Requiere borrar un producto exactamente durante la confirmación de una venta que lo contiene.**
- **El caso "producto ya borrado antes" es preexistente, no una regresión:** el código de `2580f7c`
  también dereferencia `item.Producto.Stock`, así que ya fallaba. Lo que el hotfix agrega es la variante
  "detached silencioso" en la ventana estrecha — y lo hace **dentro de una transacción**, que al menos
  revierte lo demás si algo tira.

`archivos_fix` sugeridos (hipótesis para el Implementador, no instrucción cerrada):
`FerreteriaLaPlatense.Infrastructure/Services/VentaWorkflowService.cs` — releer el stock con el mismo
criterio que el estado (`IgnoreQueryFilters` + proyección de `Stock` y `DeletedAt`, y rechazo explícito si
el producto quedó borrado), o bien poner en `ProductoService.EliminarAsync` la guarda de uso que hoy no
tiene. `migracion_ef`: **ninguna**.

**Criterio de re-verificación (vuelve en FAIL):** sembrar una venta en Borrador con un producto, soft-borrar
el producto por SQL después de que la venta se cargó, confirmar, y afirmar que **o** la confirmación se
rechaza explícitamente **o** el stock queda descontado — nunca "confirmada con stock intacto".

### Hallazgo declarado, sin parte (fuera del alcance del hotfix)

- **`RegistrarAjusteAsync` de CC — sí mueve plata del ledger, y es uno de los 4 sitios sin tocar.** Escribe
  un `MovimientoCCCliente` que cambia el saldo del cliente. **Pero el lock no es su arreglo**: no tiene
  ninguna guarda de estado que una relectura pudiera proteger (sólo valida el DTO), así que su exposición
  es **doble submit** (dos ajustes de $X cada uno), que se cierra con una clave de idempotencia, no con
  `FOR UPDATE`. **No cambia el alcance de este deploy** y el hotfix no lo empeora. Correctamente fuera de
  `ValidarPeriodoAbiertoAsync` porque por diseño no toca caja. Los otros 3 sitios sin tocar siguen
  relevados y declarados.

### Partes de defecto de la corrida anterior

Ninguno de los 6 lotes previos abrió un parte sobre estos 5 sitios: el hotfix nace del barrido `LP-002` del
implementador, no de un reporte de QA. No hay partes pendientes de re-verificación en este alcance.

## Riesgos de liberación

1. **`FacturarAsync` sostiene el lock durante el round-trip a AFIP** (decisión declarada y correcta: es la
   única forma de que el segundo request no emita). Si AFIP tarda más que `innodb_lock_wait_timeout` (50 s
   por defecto) un segundo POST **sobre la misma venta** muere con un error de base crudo en vez de un
   mensaje lindo. Bloquea **una** fila: ninguna otra venta se entera. **Hoy inalcanzable** (facturación
   deshabilitada por falta de certificado).
2. **Comprobante AFIP huérfano** — declarado en el código y **no resuelto**: si el proceso muere entre la
   respuesta de AFIP y el commit, el CAE existe en AFIP y no en el sistema, y un reintento emitiría un
   segundo comprobante. No es concurrencia y el lock no puede cubrirlo. **Hay que cerrarlo ANTES de
   habilitar la facturación electrónica, no después.** Riesgo cero hoy.
3. **`LP-034`** (arriba): stock silenciosamente no descontado en una ventana estrecha. `minor`.
4. **El arnés viaja en el repo** (`tools/ArnesHotfixTransacciones`, 755 líneas, `OutputType=Exe`). **No
   está en el `.sln`**, así que un build de solución no lo toca y publicar el proyecto Web no lo incluye.
   Su guarda de base se verificó funcionando. Sin riesgo de deploy; queda como herramienta de
   re-verificación.
5. **Producción está en cero transaccional**, así que **no hay dato real que reparar**. El hotfix llega
   antes de la primera operación real del cliente, que era el objetivo.

## Checklist de merge

- [x] Rama correcta: `hotfix-transacciones-ventas`, nacida de `2580f7c` (= lo publicado), **no** de
      `entrega-1-migracion`.
- [x] **Sin migración EF** y sin columnas nuevas. 8 migraciones en la rama = 8 en producción.
- [x] Build **0 errores** (9 advertencias, todas preexistentes: NU1902 MailKit/MimeKit).
- [x] Arnés **82/82 OK en 4 corridas propias** sobre un fixture de 8 migraciones.
- [x] **Control positivo ejecutado**: 40 fallas contra el código roto, con los importes reproducidos.
- [x] **Mutación ejecutada**: la relectura es portante en los 3 métodos del workflow (M3 24 fallas, M1 4).
- [x] `LP-009` preservado en las 3 vías que escriben caja, **dentro** de la transacción.
- [x] Granularidad del lock de cliente ensayada: serializa el mismo cliente y **no** clientes distintos.
- [x] `git status --porcelain` limpio en el repo del sistema (sólo `?? .claude/`, preexistente).
- [x] Producción y los fixtures de los otros 6 lotes intactos.
- [ ] **Pendiente post-deploy**: `LP-034` (`minor`) y el huérfano de AFIP antes de habilitar facturación.

---

# Entrega 6 — LOTE 5: presupuestos en PDF y aumento masivo de precios (QA, 2026-10-06, rama `entrega-1-migracion`)

Gate del commit `eec79d4` "Entrega 6: presupuestos en PDF y aumento masivo de precios" (31 archivos, 7.738
líneas, migración `20261005221452_EntregaSeis_PresupuestosYAumentoMasivo`). Contexto nuevo: los 14 criterios
arrancaron **en FAIL** y se re-ejecutaron contra el sistema corriendo; no se leyó la transcripción del
implementador, sólo el diff y el mensaje del commit.

## **NO-GO.** 14 de 14 criterios en PASS, pero se emiten **2 partes de defecto bloqueantes del alcance** (`LP-030` `major`, `LP-029` `minor`) y 3 hallazgos `low`.

El veredicto no sale de un criterio fallado: sale de que **el tiempo declarado del aplicar no reproduce** (se
midió sobre una pasada que no escribe ninguna fila) y de que **el desglose de IVA del PDF no cierra con su
propio total** en un caso de datos que la primera prueba no muestra. Las dos cosas son del alcance del lote y
las dos son observables.

## Entorno y metodología

- `dotnet build` → **0 errores**, 8 advertencias **todas preexistentes** (NU1902 MailKit/MimeKit).
- `dotnet ef migrations has-pending-model-changes` → **"No changes have been made to the model since the last
  migration."** Verificado de forma independiente, no asumido del commit.
- **Base propia:** `laplatense_dev` clonada a **`laplatense_qa_l5`** (`mysqldump` + restore, 35 MB, 112.485
  productos) y la app levantada contra la copia pasando `ConnectionStrings__DefaultConnection` por variable
  de entorno, en el puerto **7255** (propio, para no chocar con los otros 5 lotes en paralelo).
  **`laplatense_dev` y producción no se tocaron.** Este lote mueve los 112.485 productos: sin el clon
  propio habría arruinado la línea base de todos los demás.
- **Navegador real.** El MCP `playwright` sigue sin estar expuesto; se condujo el **Chromium completo** de
  `ms-playwright/chromium-1243/chrome-win64/chrome.exe` con `locale: es-AR` y
  `timezoneId: America/Argentina/Buenos_Aires`. El harness HTTP (cookies de Identity + antiforgery sobre el
  mismo contexto del navegador) se usó para las guardas de servidor, los POST manipulados y las mediciones
  de tiempo; el navegador, para lo que sólo se ve en pantalla (submit real del formulario, validez HTML de
  los inputs, hidden del preview, badges de estado, sidebar por rol).
- **Oráculos recalculados contra SQL independiente**, no contra el servicio: el universo del modo
  "recalcular" con filtro vacío se replicó en SQL (incluyendo el `DeletedAt is null` del query filter global,
  MH-049) y dio **112.021**, exactamente lo que informa el preview.
- **Siembras deliberadas, todas declaradas y sobre el clon:** `UnidadVenta = Metro` en el producto 31356 (el
  catálogo no tenía ninguno y el criterio 1 lo pide); `PrecioVentaDesactualizado = 1` en 6 productos de la
  categoría 15 y 6 de afuera (el catálogo venía con **0** productos marcados, así que el criterio 10 era
  inverificable sin sembrar); una oferta vigente de $1,50 en el producto 53349; `PrecioOferta = 0` con
  ventana vigente en el 85054 (para `LP-032`, revertida al terminar); `ValidoHasta` en el pasado en los
  presupuestos 27 y 28 (la UI no permite nacer vencido, y el criterio 6 vive justo ahí); y el
  `PasswordHash`/`SecurityStamp` del superusuario copiado a `vendedor.qa@test.local` para poder entrar con
  ese rol. Snapshots `qa_l5_base_productos` y `qa_l5_pre_full` de las 112.485 filas para poder comparar el
  antes y el después columna por columna.
- **El repo del sistema bajo prueba no se modificó.** `git status --porcelain`: sólo `?? .claude/`, que ya
  estaba al abrir la sesión. `Logs/` está en `.gitignore` (verificado con `git check-ignore`).
- **0 `pageerror` y 0 `console.error`** en todo el recorrido de navegador, y **0 entradas** de
  Presupuestos/AumentoMasivo en los logs de error de Serilog del día (los que hay son de otros lotes).

## Cobertura por criterio de aceptación

| # | criterio | resultado | evidencia observada |
|---|---|---|---|
| 1 | cantidades fraccionarias sin truncar + unidad en el PDF | **PASS** | Presupuesto 24: `ItemsPresupuesto` guarda `Cantidad = 2.500` con `UnidadVenta = 2` (Peso) y `0.750` con `UnidadVenta = 3` (Metro). El PDF imprime **"2,500 Kg"** y **"0,750 Mt"** (texto extraído con `pdftotext`) |
| 2 | 10% desc + 10% rec = precio de lista exacto | **PASS** | Línea de `PrecioUnitario 100.00`, `Descuento 10`, `Recargo 10` → `Subtotal = 100.00` **exacto** en la base (la cascada daría 99,00). El PDF dibuja `$ 100,00 (-10% +10%)` y `Subtotal c/IVA $ 121,00` |
| 3 | el total discrimina IVA con alícuotas mixtas | **PASS**, con el defecto `LP-029` al lado | Presupuesto 24 (21% y 10,5%): `TotalIVA = 18.170,78` = 10.601,79 + 1,17 + 21,00 + 7.546,82 (IVA redondeado línea por línea, recalculado a mano). El PDF discrimina `IVA 10,5%: $ 7.546,82` + `IVA 21%: $ 10.623,96` = `IVA total: $ 18.170,78`. El caso mixto **cierra**; el que no cierra es el de dos líneas de la MISMA alícuota → `LP-029` |
| 4 | precio manipulado por `Vendedor` / IVA manipulado para todos | **PASS** | El Vendedor posteó `PrecioUnitario=0.01`, `Descuento=99`, `PorcentajeIVA=0` → la base guardó **`6.00` / `0.00` / `21.00`** (presupuesto 31, `Subtotal 18.00` = 3 × 6). El Administrador posteó `PorcentajeIVA=0` con precio 1000 → guardó **`21.00`** y `TotalIVA 210.00` (presupuesto 26). `LP-014`/`LP-016` cerrados por la puerta nueva |
| 5 | conversión precarga, deja `Convertido` y vincula | **PASS** | Venta **9027** nace en `Borrador` con `PresupuestoOrigenId = 24` y los **4 ítems copiados 1 a 1** (cantidades 2.500/0.750/1/1, unidades 2/3/1/1, descuentos y recargos incluidos) y `Subtotal/TotalIVA/Total` idénticos al presupuesto. El presupuesto 24 queda `Estado = Convertido` con `VentaGeneradaId = 9027`. Reintentar la conversión → "Este presupuesto ya se convirtió en la venta #9027." |
| 6 | un vencido no se convierte sin acción explícita | **PASS** | Presupuesto 28 `Aprobado` con `ValidoHasta = 04/10/2026`: sin confirmar → **rechazado** con "La vigencia de este presupuesto venció el 04/10/2026… confirmalo explícitamente desde el botón de conversión", **cero** ventas creadas. Con `confirmarVencido=true` → venta **9028** más el aviso "Se convirtió un presupuesto VENCIDO: revisá los precios antes de confirmar la venta." |
| 7 | el PDF no expone nota interna, costo ni margen | **PASS** | 4 PDFs generados (24, 25, 27, 28) y barridos por texto: **0 ocurrencias** de `NOTA-INTERNA`, "interna", "costo", "margen", `PrecioCompra` y del costo real del producto cotizado (`18795`). La nota interna **sí** aparece en `Details` (pantalla de staff), que es donde corresponde |
| 8 | el preview muestra actual, resultante y total de afectados | **PASS** | Respuesta del preview sobre la categoría 15: `alcanzados=5`, y por fila `precioVentaActual` → `precioVentaNuevo` (5905,5→5905,5; 4030→4030; …) más `suben/bajan/sinCambio`, `conOfertaVigente=1`, `sinRecargo=0`, `conCostoNoPositivo=0`. En pantalla los hidden `PreviewGeneradoEn` y `ProductosAlcanzadosEsperados` quedan cargados (`…T06:51:37.5672297Z` / `5`) |
| 9 | aplicar con filtro de categoría toca SOLO esos productos | **PASS** | Snapshot de las 112.485 filas antes y después. `CambiarRecargo 55%` + `CategoriaId=15` → cambian **exactamente los 6** productos de esa categoría; las otras **112.479** quedan byte a byte iguales (las únicas diferencias extra son las 6 banderas que **yo** sembré). Control a escala: `CategoriaId=2` → 62.689 productos con recargo 41 y **0** productos con recargo 41 fuera de la categoría 2 |
| 10 | recalcular desde el costo apaga la bandera en los aplicados y no en el resto | **PASS** | `RecalcularDesdeCosto` + `CategoriaId=15`: los **5 aplicados** quedan en `0`; el 53349 (excluido por oferta vigente) **sigue en `1`**; los **6 sembrados fuera del filtro** siguen en `1`. A escala del catálogo entero: después del aplicar con filtro vacío quedan **exactamente 2** banderas encendidas, que son los 2 productos con oferta vigente |
| 11 | "cambiar recargo" deja `PorcentajeRecargo` y `PrecioVenta` consistentes | **PASS** | Los 6 de la categoría 15 quedaron en `PorcentajeRecargo = 55` y `PrecioVenta` = `round(PrecioCompra × 1,55 / 1,21; 2)` **al centavo** (2,78 / 5,97 / 3,78 / 6,89 / 5.905,50 / 4.030,00, comparados contra la fórmula calculada en SQL). A escala: después del aplicar sobre todo el catálogo, **0 productos** violan la fórmula (`count` en SQL sobre los 112.021) |
| 12 | una oferta vigente no se pisa sin decirlo, y el preview lo hace visible | **PASS** | Por defecto: universo 6, `conOfertaVigente = 1`, `alcanzados = 5`, y la fila del 53349 viaja con `tieneOfertaVigente: true` (badge). Con el checkbox: `alcanzados = 6`. A escala: tras el aplicar con filtro vacío, **0 de los 377/378** productos con oferta vigente cambiaron de precio o de bandera |
| 13 | el aumento queda auditado: quién, cuándo, qué filtro, cuántos | **PASS** | 15 filas en `AumentosMasivosPrecio` (ids 10–24) con `Fecha` UTC, `UsuarioId`, `Modo`, `PorcentajeRecargoAplicado`, `CategoriaId/MarcaId/ProveedorId`, `SoloPrecioVentaDesactualizado`, `IncluyoConOfertaVigente`, `ProductosAlcanzados/Aplicados/RechazadosPorConcurrencia/SinRecargo` y `PreviewGeneradoEn`. El historial de la pantalla los describe en castellano ("Todo el catálogo (excluyó ofertas vigentes)") |
| 14 | con el catálogo real, preview y aplicar no revientan | **PASS funcional + HALLAZGO de tiempo** | **No revientan:** 15 combinaciones de filtro + 2 modos + 5 páginas de muestra, **0 HTTP 500**, 0 respuestas no-JSON, 0 errores de consola, 0 entradas en el log. **Los tiempos no se parecen:** ver `LP-030`. Medido por mí: preview con filtro vacío **593–904 ms** (declarado 464 ms), por proveedor **428–460 ms** (declarado 465 ms, coincide), PDF **23–594 ms** (declarado 585 ms, coincide), **aplicar todo el catálogo cambiando todas las filas 44,2 s y 46,2 s** (declarado 7,6–8,0 s), aplicar por categoría de 62.689 productos **22,2 / 23,1 / 26,7 s** (declarado 10,4 s) |

## Máquina de estados de `Presupuesto`

Estados persistidos `Borrador → Enviado → Aprobado → Convertido`, más `Rechazado`; **`Vencido` es estado
EFECTIVO**, derivado al leer (`Enviado`/`Aprobado` + `ValidoHasta < hoy`) y nunca persistido. Las **11
transiciones válidas y las 18 inválidas** se recorrieron por POST directo, no por los botones (la tabla
agrupa los casos equivalentes):

| transición | desde | resultado observado |
|---|---|---|
| `Enviar` | Borrador | **aceptada** — "Presupuesto marcado como enviado." |
| `Enviar` | Borrador **sin ítems** | **rechazada** — "Agregá al menos un ítem antes de enviar el presupuesto." (presupuesto 30 sigue en Borrador) |
| `Enviar` | Enviado / Aprobado / Convertido / dado de baja | **rechazada** — "Solo se puede enviar un presupuesto que está en borrador." / 404 en el dado de baja |
| `Aprobar` | Enviado | **aceptada** — "Presupuesto aprobado." (y con vigencia vencida agrega el aviso de que convertirlo va a pedir confirmación) |
| `Aprobar` | Borrador / Rechazado / Convertido | **rechazada** — "Solo se puede aprobar un presupuesto que fue enviado al cliente." |
| `Rechazar` | Enviado y Aprobado | **aceptada** — `MotivoRechazo` persistido ("El cliente compro en otro lado") |
| `Rechazar` | Borrador / Convertido | **rechazada** — "Solo se puede rechazar un presupuesto enviado o aprobado." |
| `ConvertirAVenta` | Aprobado vigente | **aceptada** — venta 9027 en Borrador |
| `ConvertirAVenta` | Aprobado **vencido**, sin confirmar | **rechazada** con el mensaje de vigencia; **con** `confirmarVencido` → aceptada (venta 9028) |
| `ConvertirAVenta` | Borrador / Enviado / Rechazado | **rechazada** — "Solo se puede convertir en venta un presupuesto aprobado. Aprobalo primero." |
| `ConvertirAVenta` | Convertido | **rechazada** — "Este presupuesto ya se convirtió en la venta #9027." (no hay doble venta) |
| `Cancelar` (baja lógica) | Borrador | **aceptada** — `DeletedAt` + `DeletedByUserId` en el presupuesto y en sus ítems |
| `Cancelar` | Enviado+ | **rechazada** — "…uno ya enviado al cliente es historia y se conserva." |
| `Guardar` (editar) | Convertido | **rechazada** — "El presupuesto ya salió de borrador: no se puede editar." y `GET /Editar` redirige a `Details` |
| `Vencido` efectivo | Aprobado con `ValidoHasta = 02/10` | el filtro `estado=Aprobado` devuelve **0** y `estado=Vencido` devuelve **27**: no aparece en los dos a la vez. El listado y `Details` lo rotulan **"Vencido"**, y el botón de convertir sigue ofrecido (por diseño, con confirmación aparte) |

## Cobertura del catálogo cross-proyecto

| id | aplica | resultado | acción |
|---|---|---|---|
| `MH-001` | sí (el candidato obvio a la 7ª aparición) | **NO REPRODUCE** — ejecutadas **15 combinaciones** de filtro × 2 modos: vacío, categoría, marca, proveedor, desactualizados, las 4 juntas, los 3 ids inexistentes, un cruce vacío, `0`, `-1`, texto `abc`, página 99999 y página negativa → **todas 200**, incluidas las **5 que devuelven 0 filas**. No hay ninguna colección local en el módulo: los 3 filtros de catálogo son comparación por id escalar y el de proveedor es un `EXISTS` correlacionado sobre 110.683 mapeos | ninguna |
| `MH-054` | sí (es literalmente este patrón) | **NO REPRODUCE** — el Aplicar recibe `PreviewGeneradoEn` + `ProductosAlcanzadosEsperados`. Sin timestamp → "Falta la previsualización"; con recuento distinto (moví un producto a la categoría entre las dos fases) → "El catálogo cambió desde la vista previa: ahora el filtro alcanza 6 producto(s) y la vista previa mostraba 5", **cero** filas escritas. Y en el navegador, cambiar cualquier filtro o el % **limpia** los dos hidden (`""` / `0`) | ninguna |
| `MH-016` | sí (variante) | **MEJOR QUE EL ORIGINAL** — un **ajuste de stock real por la pantalla** del sistema entre previsualizar y aplicar hace que esa fila se **rechace** (no se pise, no se ignore en silencio): "Se actualizaron 4 producto(s). 1 se saltearon porque alguien los modificó después de la vista previa", el producto 85737 quedó en 55%/6,89 mientras los otros 4 pasaron a 60%, y la auditoría guarda `RechazadosPorConcurrencia = 1`. No aborta el lote entero como en marihogar | ninguna |
| `LP-003` | sí (dos pantallas de puros inputs numéricos) | **NO REPRODUCE** — reabrir el borrador 34 (cantidad 2,5 · descuento 12,5% · recargo 7,25%) deja los inputs **con valor**: `2.500`, `20193.88`, `12.50`, `7.25`, `21.00`, `57879.44`. La vista usa un helper `num()` con `InvariantCulture` | ninguna |
| `GAN-006` | sí | **NO REPRODUCE** — `checkValidity()` sobre **todos** los inputs y selects del formulario: **0 inválidos**, formulario válido, y el submit real desde el navegador guardó sin tocar un número (`2.500 / 20193.88 / 12.50 / 7.25 / 47834.25` idénticos antes y después) | ninguna |
| `LP-007` | sí (el `Guardar` encadena `continuar`) | **NO REPRODUCE** — `continuar=zzz` → "Acción no reconocida (\"zzz\"): el presupuesto se guardó pero NO se marcó como enviado." y el presupuesto **sigue en Borrador**. Control: `continuar=""` → "Presupuesto guardado correctamente." | ninguna |
| `LP-012` | sí (listado nuevo server-side) | **NO REPRODUCE** — 17 términos: `conversion`/`CONVERSION` → 1 (insensible a mayúsculas), `iva centavo` → 1, `287.437,32` y `287437.32` → 1 (importe en los dos formatos), `140635` → 1 (fragmento), `16/10/2026` → 3, `Convertido`/`Rechazado` → 2/1, y `'`, `%`, `_`, `'; DROP TABLE x;--`, `Zzz-nadie` → 0 filas sin romper nada | ninguna |
| `MH-015` | sí | **NO REPRODUCE** — las **6 columnas × 2 direcciones = 12 órdenes** devuelven 12 secuencias de ids distintas y coherentes; ninguna cae a un orden fijo | ninguna |
| `LIP-001` | sí | **NO REPRODUCE** — los 10 rechazos de negocio probados (sin destinatario, sin vigencia, vigencia pasada, cantidad 0, precio negativo, descuento 120%, sin ítems, sin preview, recuento cambiado, % de recargo faltante/negativo) llegan **todos** a pantalla como toast de SweetAlert | ninguna |
| `LP-014` / `LP-016` | sí | **NO REPRODUCE** — ver criterio 4 | ninguna |
| `KOI-005` / `KOI-006` | sí (2 links nuevos de sidebar) | **NO REPRODUCE** — el Administrador ve los dos y los dos responden 200. El **Vendedor** ve "Presupuestos" y **no** ve "Aumento masivo", y las 3 rutas del aumento masivo (`GET`, `POST Preview`, `POST Aplicar`) le devuelven `AccessDenied` **también por POST directo con token robado de otra pantalla** | ninguna |
| `KOI-017` | sí (confidencialidad por complemento) | **NO REPRODUCE** — el PDF no imprime costo ni margen, y tampoco el precio de lista junto al cotizado, así que no se puede derivar el margen por resta. El descuento/recargo impreso es información que el cliente **sí** tiene que ver | ninguna |
| `MH-049` | sí (aplicado a mi propio oráculo) | **EVITADO** — el universo se replicó en SQL incluyendo el `DeletedAt is null` del query filter global; dio 112.021 contra los 112.021 del servicio (0 filas borradas en esta base, así que la diferencia era 0, pero queda declarado) | ninguna |
| `MH-005` | sí (PDF nuevo) | **N/A razonado** — el PDF se sirve en cualquier estado y a cualquier rol con `RequireVentas`. No hay estado en el que deba negarse: un presupuesto es un documento comercial, no un remito que compromete mercadería. Se verificó que un id inexistente da **404** y no 500 | ninguna |
| `REG-009` | no | **N/A** — no hay cascada categoría→subgrupo; son 3 combos independientes | ninguna |
| `LP-004` | sí | **NO EJECUTADO** — la persistencia del buscador en `Session` al volver al listado no se probó en este lote. Queda declarado como hueco | pendiente |

## Reglas nuevas o modificadas desde la última corrida

El diferencial lo hizo el **lote 1** de esta misma tanda y su resultado se tomó como dato (instrucción 39,
sección 5): `git log --since=2026-10-05` sobre `32-estandares-qa-implementador.instructions.md` y
`regresiones-manuales.yml` no devuelve **ninguna regla agregada ni modificada** después del 2026-10-05, sólo
el commit de cierre del Sprint 0 y un fix del parser de `contexto.py`. Verificado por mi cuenta por índice
(`cat_resumen.txt` + `git log`) antes de aceptarlo: coincide. **Sin reglas nuevas que ejecutar fuera del
catálogo ya validado.**

## Lo que busqué por mi cuenta y no estaba en el brief

- **El redondeo del agregado, no sólo el de la fila.** El implementador arregló el preview fila por fila
  (y lo verifiqué: **121 filas** de 5 páginas distintas del catálogo completo comparadas contra el valor
  escrito, **0 diferencias**). Pero el **total de control** sigue sumando los precios sin redondear:
  `sumaNueva` del preview = 21.883.240.756.300,56 contra `SUM(PrecioVenta)` real post-aplicar =
  21.883.240.756.302,02. **$1,46 de desvío** → `LP-031`.
- **El mismo error de forma en el PDF.** Buscando el patrón `Round(Sum(x))` vs `Sum(Round(x))` en el otro
  módulo del lote apareció `LP-029`: el desglose de IVA por alícuota se redondea una sola vez sobre el neto
  del grupo mientras el total se suma por línea. Reproducido con dos líneas de $10,50 al 21%: el PDF dice
  `IVA 21%: $ 4,41` y `IVA total: $ 4,42`.
- **La familia completa de los 38 productos con costo no positivo.** Confirmada la exclusión (37 negativos +
  1 en cero, **0 tocados** por el aplicar) y buscados más miembros: el mínimo costo positivo del catálogo es
  **$0,01** y con la fórmula ningún producto de costo > 0 redondea a 0,00 (`count = 0` en SQL), así que la
  exclusión está completa. Dato aparte: los **37 precios de venta negativos ya existían** antes de correr
  nada (verificado contra el snapshot) — son del catálogo migrado, el módulo no los creó pero tampoco los
  arregla, y nadie los está viendo.
- **Las 6 copias de la regla de oferta vigente, comparadas ejecutando y no leyendo.** Divergen: las **2
  nuevas** incluyen `PrecioOferta > 0` y la **definición de referencia** (`Producto.EsOfertaVigente`) más 2
  superficies de Productos no. Sembrando `PrecioOferta = 0` con ventana vigente, el mismo producto en el
  mismo instante da: grilla de Productos `ofertaVigente: true`, `Productos/Edit` badge **"Vigente hoy"**,
  aumento masivo `tieneOfertaVigente: false`, y las dos resoluciones de precio cobran el precio de lista. La
  pantalla de presupuesto **se salva por casualidad**: el JS hace `producto.precioOferta || producto.precioVenta`
  y el `0` es falsy (verificado: el input queda en $3,90, no en $0). Las copias nuevas son las **correctas**;
  la que hay que corregir es la referencia → `LP-032`.
- **El binder de decimales.** `PorcentajeRecargo=10,5` (coma, como lo escribe una persona) se bindea como
  **105**: `InvariantDecimalModelBinder` prueba `InvariantCulture` con `NumberStyles.Any` primero y la coma
  pasa como separador de miles. **No es alcanzable desde la UI** — verificado en el navegador: tipeando
  `10,5` en el `<input type=number>` el DOM entrega `10.5` y `checkValidity()` da `true`. Es preexistente
  (commit `f5e6af9`, Entrega 1) y compartido por toda la app, pero el campo más caro que pasa por ahí es
  justo el % de recargo de 112.485 productos → `LP-033`, `low`, declarado como riesgo latente.
- **El modo "cambiar recargo" también apaga `PrecioVentaDesactualizado`.** El diseño declarado atribuye eso
  sólo al modo "recalcular desde el costo" ("este modo **apaga** la bandera"), pero el código lo hace en los
  dos sin condición de modo. Medido: el producto 53349 pasó de bandera `1` a `0` en una corrida de
  `CambiarRecargo 55%`. **No es un bug**: los dos modos recalculan `PrecioVenta` desde el `PrecioCompra`
  actual, así que después de cualquiera de los dos el precio **está** actualizado y apagar la bandera es
  correcto. Es una divergencia entre el código y su documentación: hay que elegir cuál de las dos es la
  verdad y alinear la otra. Sin parte de defecto, va como observación.
- **Qué pasa si el cliente corta el aplicar.** Aborté el POST a los 30 s en una corrida de todo el catálogo:
  la transacción **revirtió bien** (0 productos con el recargo nuevo, **0 filas** en la auditoría). Pero el
  usuario no recibe ningún mensaje y no tiene forma de saber si se aplicó: entra en `LP-030`.
- **Cambiar el recargo rellena los recargos faltantes.** Tras la corrida por categoría, los productos
  `sin recargo` bajaron de 48 a 16 y el universo del otro modo creció de 112.021 a 112.053. Es el
  comportamiento correcto del modo, pero significa que la exclusión "sin recargo" del modo "recalcular" se
  encoge sola después de cada corrida del otro. Observación, no defecto.

## Defectos detectados

| id | sev. | qué | parte emitido |
|---|---|---|---|
| `LP-030` | **major** | El aplicar sobre todo el catálogo tarda **44–46 s** en un POST sincrónico (no 7,6–8,0 s); el número declarado corresponde a una pasada que no escribe ninguna fila (medida: 3,5–3,7 s cuando nada cambia). Por categoría: 22–27 s contra 10,4 s declarados. Si el cliente corta, se pierde la corrida sin aviso | **sí** |
| `LP-029` | **minor** | El desglose de IVA por alícuota del PDF no cierra con el total del mismo documento (`$ 4,41` contra `$ 4,42`) porque usa `Round(Sum)` donde el total usa `Sum(Round)` | **sí** |
| `LP-031` | low | El total de control del preview suma los precios sin redondear: $1,46 de diferencia contra el catálogo que el aplicar escribe | sí |
| `LP-032` | low | Las copias de la regla "oferta vigente" divergen en el `> 0`: con oferta en cero, Productos dice "Vigente hoy" y ninguna vía de cobro la aplica | sí |
| `LP-033` | low | El binder de decimales resuelve `'10,5'` como `105`; no alcanzable desde la UI hoy, preexistente, con el blast radius de este módulo | sí |

## Partes de defecto emitidos al Implementador

1. **`LP-030`** (`major`, Infrastructure) — `archivos_fix`: `AumentoMasivoPrecioService.AplicarAsync` (evaluar
   `ExecuteUpdateAsync` estampando `UpdatedAt` en el mismo `SET`, o subir el lote y re-medir con filas que SÍ
   cambian, o sacar la corrida del request) y `AumentoMasivoPreciosController.Aplicar` (si se queda en el
   request, avisar el tiempo esperado antes de confirmar y aclarar que cortar la página no aplica nada a
   medias). **Sin migración EF.** *Re-verificación:* cronometrar `CambiarRecargo` con filtro vacío sobre el
   catálogo real **dos veces** y que las dos entren en el presupuesto de tiempo que el equipo fije para
   SmarterASP; y que el tiempo documentado en `5-implementador.md` sea el del peor caso, con la cantidad de
   filas que cambiaron declarada.
2. **`LP-029`** (`minor`, Infrastructure) — `archivos_fix`: `PresupuestoService.GenerarPdfAsync`, armado de
   `ivaPorAlicuota`: calcular el IVA del grupo como la **suma de los IVA redondeados por línea**, la misma
   expresión que ya usa `RecalcularTotales`. **Sin migración EF.** *Re-verificación:* un presupuesto con dos
   líneas de subtotal $10,50 al 21% imprime `IVA 21%: $ 4,42`, `IVA total: $ 4,42` y `TOTAL: $ 25,42`; y el
   caso de alícuotas mixtas sigue cerrando.
3. **`LP-031`** (`low`) — `ObtenerPreviewAsync`, `sumaNuevo`: sumar la expresión ya redondeada en SQL, igual
   que ya hace `ContarPorDireccion` en el mismo archivo. *Re-verificación:* `sumaNueva` del preview igual al
   `SUM(PrecioVenta)` post-aplicar del mismo universo, al centavo.
4. **`LP-032`** (`low`) — `Producto.EsOfertaVigente` + las 2 proyecciones de `ProductoService` + el badge de
   `Productos/Edit.cshtml`; alternativa complementaria: rechazar `PrecioOferta = 0` en la validación del
   alta/edición. **Toca Ventas en producción**, así que es decisión de alcance, no de QA.
   *Re-verificación:* con `PrecioOferta = 0` y ventana vigente, las 6 superficies responden lo mismo.
5. **`LP-033`** (`low`) — `InvariantDecimalModelBinder`: usar `AllowDecimalPoint | AllowLeadingSign` (sin
   `AllowThousands`) en el intento invariante para que el fallback a es-AR llegue a ejecutarse.
   *Re-verificación:* `'10,5'` → 10,5; `'10.5'` → 10,5; `'1.234,56'` → 1234,56; `'abc'` → sigue dando error.

**Estado de los partes de la corrida anterior:** los 7 defectos del Sprint 0 (`LP-006`…`LP-012`) quedaron
cerrados en la re-verificación del 2026-10-05 y no se re-abrieron por nada de este lote. `LP-013` sigue
abierto y es de Caja, fuera de este alcance.

## Riesgos de liberación

1. **`LP-030` es el riesgo real de este lote.** 44–46 s de POST sincrónico en localhost con MySQL local
   significan bastante más en SmarterASP (disco compartido, MySQL remoto). El `requestTimeout` por defecto de
   ANCM son 2 minutos: el margen existe pero es finito, y el día que el catálogo crezca o el hosting esté
   cargado la operación más visible del módulo se cae del lado malo. **Mitigación mientras no se arregle:**
   usar el aumento masivo **por categoría o por proveedor** y no con filtro vacío, y avisarle al cliente que
   la pantalla puede tardar un minuto y que **no hay que cerrarla** — si se corta no se aplica nada a medias
   (eso está verificado), pero tampoco se aplica nada.
2. **`LP-029` sale impreso y se lo lleva el cliente.** Es 1 centavo, pero es un documento de venta cuyo
   desglose no cierra con su propio total. En un presupuesto grande con muchas líneas de la misma alícuota el
   desvío crece. Mitigación: ninguna operativa; se arregla o se convive sabiéndolo.
3. **Los 37 precios de venta negativos del catálogo migrado siguen ahí.** El módulo nuevo hace lo correcto al
   no tocarlos, pero nadie los está mirando y son productos que el mostrador puede llegar a vender. No es un
   defecto de esta entrega; es una limpieza de datos pendiente que conviene decidir con el cliente.
4. **La conversión a venta la puede hacer el `Vendedor`**, igual que aprobar y rechazar: la policy
   `RequireVentas` cubre todo el controller sin separar acciones. Es lo declarado en el alcance, no un
   defecto, pero si el negocio quiere que aprobar sea de Administración hay que pedirlo explícitamente.

## Pruebas mínimas ejecutadas

- **11 presupuestos** creados (ids 24–34), 2 convertidos en venta (9027, 9028), 1 rechazado, 1 dado de baja.
- **29 transiciones** de la máquina de estados (11 válidas + 18 inválidas), todas por POST directo.
- **5 PDFs** generados y extraídos a texto (`pdftotext`), incluido el de un presupuesto vencido.
- **15 corridas aplicadas** del aumento masivo sobre el catálogo real (ids 10–24 de la auditoría), de 5 a
  112.069 productos, en los 2 modos, más 1 abortada a propósito desde el cliente.
- **15 combinaciones** de filtro del preview (5 de ellas con resultado vacío) × 2 modos.
- **17 términos** de búsqueda y **12 ordenamientos** en el listado nuevo.
- **2 snapshots** completos de las 112.485 filas de `Productos`, comparados columna por columna.
- **5 pantallas** en navegador real con `0 pageerror` y `0 console.error`, más el submit real del formulario
  de presupuesto y el ciclo previsualizar→confirmar completo por UI.

## Checklist de salida para merge

- [x] `dotnet build` 0 errores, sin advertencias nuevas.
- [x] `has-pending-model-changes` limpio: la migración de la entrega está completa.
- [x] Autorización verificada **por POST directo**, no sólo por la ausencia del botón.
- [x] Gate de precio por rol y alícuota de IVA no leídos del payload, verificado posteando valores adulterados.
- [x] Máquina de estados completa, válidas e inválidas.
- [x] Sin `IN`/`Contains` sobre colección local; 15 filtros ejecutados, incluidos los de resultado vacío.
- [x] Totales recalculados server-side y verificados contra SQL independiente.
- [x] Repo del sistema sin modificar (`git status --porcelain` limpio).
- [ ] **`LP-030` resuelto o el riesgo aceptado por escrito** con la mitigación operativa acordada.
- [ ] **`LP-029` resuelto** (el documento que ve el cliente tiene que cerrar).
- [ ] `LP-031` resuelto o aceptado.
- [ ] `LP-032` y `LP-033` triados: los dos tocan código compartido con Ventas/producción, así que es decisión
      de alcance y no de este lote.
- [ ] `LP-004` (persistencia del buscador al volver al listado) ejecutado en la próxima corrida.

---

# Entrega 3 — LOTE 3: recepción de mercadería y pagos a proveedores (QA, 2026-10-06, rama `entrega-1-migracion`)

Gate del commit `7cda85b` "Entrega 3 pasos 4 y 5: recepcion de mercaderia y pagos a proveedores"
(48 archivos, migración `EntregaTres_RecepcionMercaderiaYPagosProveedor`), probado sobre el HEAD de la
rama (`d08f8c4`), que es donde el código vive hoy. Contexto nuevo: los 14 criterios arrancaron **en
FAIL**; no se leyó la transcripción del implementador, sólo el diff y el bloque del sprint de
`5-implementador.md`.

## **GO.** Los 14 criterios en PASS, con evidencia observada en los tres ledgers. Deja 3 hallazgos nuevos no bloqueantes (`LP-024` `major` de riesgo de liberación, `LP-025` y `LP-026` `trivial`).

## Entorno y metodología

- `dotnet build FerreteriaLaPlatense.slnx` → **0 errores**, 8 advertencias **todas preexistentes**
  (NU1902 MailKit/MimeKit).
- **Base aislada propia: `laplatense_qa_l3`**, clon de `laplatense_dev` (`mysqldump` + restore, 35 MB,
  39 tablas, 112.485 productos, 85 proveedores). `laplatense_dev` **no se usó para probar** y
  **producción no se tocó**. La copia queda viva: es el fixture de la re-verificación.
  Línea base del clon: 9 `CajaMovimientos`, 0 `MovimientosCCProveedor`, 0 `MovimientosStock`,
  0 `OrdenesCompra`, 1 cierre diario (21/08) y 1 cierre mensual (**08/2026**, que es lo que hizo
  alcanzable la guarda `LP-009` sin sembrar nada).
- App levantada contra la copia en `https://localhost:7733` vía `ConnectionStrings__DefaultConnection`.
- **Navegador real.** El MCP `playwright` sigue sin estar expuesto; se condujo el Chromium de
  `ms-playwright/chromium-1243/chrome-win64` con `locale: es-AR` y
  `timezoneId: America/Argentina/Buenos_Aires`. **Dato de entorno nuevo: hay que apuntar a
  `https://127.0.0.1:7733`, no a `localhost`** — con `localhost` el `page.goto` muere por timeout
  aunque `curl` al mismo URL responda 200 (costó un reintento). El harness HTTP (cookies de Identity
  + `__RequestVerificationToken`) se usó para las guardas de servidor y los barridos.
- **Siembra declarada, toda en la copia:** 3 productos `ZZQA3-*` creados **por la UI**
  (`UnidadCompra=Bulto` / `UnidadVenta=Unidad` con factor 12; unidad simple; `Bulto`→`Metro` factor 25),
  porque `laplatense_dev` tiene **0 productos** con unidad de compra distinta de la de venta y sin eso
  el camino de conversión no se ejercita; 13 órdenes de compra; el factor de la línea 92 **corrompido a 0**
  por SQL para el criterio 3; una reversión **parcial** de $400 sembrada en los dos ledgers para el
  criterio 12; y dos `CHECK` constraints de **inyección de falla** (`Monto <> 77.77` en
  `CajaMovimientos`, `Monto <> 999.99` en `MovimientosCCProveedor`) para los criterios 10 y la
  atomicidad de la recepción — **las dos eliminadas al terminar** (`information_schema` → 0 CHECK).
- Credencial QA reutilizada del lote 1: `qa.super@test.local` / `QaD9#2026x` (el hash reescrito en
  `laplatense_dev` viajó en el clon). **No se creó ni se modificó ningún usuario.**
- **El repo del sistema bajo prueba no se modificó.** `git status --porcelain` al cerrar: sólo
  `?? .claude/`, que ya estaba al abrir la sesión.

## Cobertura por criterio de aceptación

| # | Criterio | Resultado | Evidencia observada |
|---|---|---|---|
| 1 | Recibir una OC de un producto comprado **por bulto** suma la cantidad **convertida** | **PASS** | OC 79, línea de **5 bultos × factor 12**: `Productos.Stock` de `ZZQA3-BULTO` pasa de `0.000` a **`60.000`**. Toast: *"entraron 67 unidades al stock"* (60 + 7 de la otra línea). En pantalla, la tarjeta **"Lo que entró al stock"** de `/OrdenesCompra/Details/79` dibuja **`+60 unidad`** con el detalle *"Recepción de la compra #79 — 5 bulto"* |
| 2 | Un producto de unidad simple suma la cantidad tal cual | **PASS** | Misma OC 79, línea de **7 unidades** (`UnidadCompra == UnidadVenta`): `ZZQA3-SIMPLE` de `0.000` a **`7.000`**, y la tarjeta muestra `+7 unidad`. Extra verificado: **factor fantasma** — OC 83 cargada con unidades iguales y factor **99** se persiste con `FactorConversionAplicado = 1.000` y el equivalente queda en 3, no en 297 |
| 3 | Una línea sin factor válido **impide la recepción completa**, nombra el producto y **no deja nada a medio aplicar** | **PASS** | Factor de la línea 92 (`ZZQA3-ROLLO`) corrompido a `0` en la base. `POST /OrdenesCompra/Recibir/80` → *"La recepción no se aplicó: hay líneas que no se pueden convertir a unidad de stock. **ZZQA3 Cable por rollo** se compró por bulto y el stock se lleva por metro, pero la línea no tiene un factor de conversión válido…"*. **Ni la línea que sí convertía quedó aplicada:** `ZZQA3-SIMPLE` siguió en `7.000` (no `10.000`), `MovimientosStock` siguió en 2 filas, `MovimientosCCProveedor` en 1, y la OC 80 siguió en `Confirmada` con `FechaRecepcion = NULL` |
| 4 | La recepción postea el `Cargo` por el total y **ningún** movimiento de caja | **PASS** | `MovimientosCCProveedor` id 66: `Tipo=Cargo`, `Monto=54630.00` = **exactamente** `OrdenesCompra.TotalEnPesos` de la 79, `OrigenTipo='OrdenCompra'`, `OrigenId=79`. `SELECT COUNT(*) FROM CajaMovimientos` **9 antes y 9 después**. Toast: *"No movió la caja: la plata sale al pagar."* |
| 5 | Deja un movimiento en el ledger de stock por línea, trazable a la OC | **PASS** | 2 filas en `MovimientosStock` para la OC 79 (ids 16 y 17), `Tipo=Compra`, cantidades `60.000` y `7.000`, **`OrigenTipo='OrdenCompra'` y `OrigenId=79` — el MISMO par con el que entró el `Cargo`**, lo que permite cruzar los dos ledgers sin traducción. `UsuarioId` no nulo y `Fecha` igual a la de la recepción |
| 6 | `PrecioCompra` actualizado (convertido y neto de descuentos); `PrecioVenta` **no cambia**; `StockVerificado` **no se toca** | **PASS** | OC 79: subtotal 60.700, descuento 6.070 → ratio 0,9. `ZZQA3-BULTO`: `60.000 × 0,9 / 60 u` = **`PrecioCompra = 900.00`** (venía de 100); `ZZQA3-SIMPLE`: `700 × 0,9 / 7` = **`90.00`**. `PrecioVenta` quedó en `200.00` y `90.00`, **sin tocar**. `StockVerificado` siguió en **`0`** en los dos. `PrecioVentaDesactualizado = 1` y `FechaUltimoCostoCompra` seteada en los dos |
| 7 | Una OC `Recibida` **no se puede cancelar** | **PASS** | `POST /OrdenesCompra/Cancelar/79` → *"La compra ya fue recibida (impactó stock y cuenta corriente), no se puede cancelar."* y la OC sigue en `Recibida`. En el navegador, los botones visibles de una `Recibida` son **sólo** `Registrar pago` / `Volver a Compras` / `Guardar nota` — no hay `Cancelar compra` ni `Registrar recepción` |
| 8 | Un pago multi-línea genera un `Pago` de CC y un `Egreso` de caja **por línea**, con el `MedioPago` correcto | **PASS** | Pago de la OC 81 en 3 líneas (3.000 Efectivo + 2.000 Transferencia + 1.000 Cheque): **3** `PagosOrdenCompra` (30, 31, 32), **3** `MovimientosCCProveedor` `Tipo=Pago` y **3** `CajaMovimientos` `Tipo=Egreso` con **`MedioPago` 1 / 4 / 5** (Efectivo / Transferencia / Cheque), mismo monto, misma fecha y **`OrigenId` = el id de la LÍNEA de pago, no del documento** (MH-027 aplicado). En pantalla, la CC del proveedor 2 lista `Pago a proveedor #30 / #31 / #32` con su medio |
| 9 | El saldo del proveedor baja exactamente lo pagado y queda en 0 al pagar el total | **PASS** | Columna de saldo acumulado de `/Proveedores/CuentaCorriente/2`, leída en el navegador: `Cargo 10.000,00 → **10.000,00**`; `Pago 3.000 → **7.000,00**`; `Pago 2.000 → **5.000,00**`; `Pago 1.000 → **4.000,00**`; `Pago 4.000 → **$ 0,00**`. Cruzado con la base: `SUM(Cargo) − SUM(Pago)` = 0 en ese momento. Y la ficha del proveedor 3 muestra `$ 192,73`, el mismo número que la base |
| 10 | Si cualquiera de las dos escrituras falla, **ninguna** queda persistida | **PASS** | **Inyección de falla real**, no deducción. `CHECK (Monto <> 77.77)` en `CajaMovimientos` → pago de 77,77: *"No se pudo registrar el pago y no quedó nada aplicado"*, y `PagosOrdenCompra` / `MovimientosCCProveedor` / `CajaMovimientos` **11 / 18 / 24 antes y 11 / 18 / 24 después**. **Caso multi-línea con la primera línea sana** (50 + 77,77): los mismos 11 / 18 / 24 — **la línea sana tampoco sobrevivió**. Simétrico del lado de la recepción: `CHECK (Monto <> 999.99)` en `MovimientosCCProveedor` → recibir la OC 84 falla y `Stock` (60.000), `PrecioCompra` (900.00), `FechaUltimoCostoCompra`, `MovimientosStock` (4) y el estado (`Confirmada`, `FechaRecepcion NULL`) quedan **todos** intactos |
| 11 | No se puede pagar más que el saldo pendiente | **PASS** | OC 81 con saldo 10.000 → pagar 10.001: *"El total a pagar ($ 10.001,00) supera el saldo pendiente de la compra #81 ($ 10.000,00)."*, **visible en pantalla en el navegador** sobre la OC 82: *"supera el saldo pendiente de la compra #82 ($ 192,73)."*, y el formulario se repinta conservando lo cargado (`metodo=Transferencia`, `monto=999999`). Con la compra 81 ya 100% pagada, el `GET /OrdenesCompra/RegistrarPago/81` **redirige** con *"La compra #81 ya está totalmente pagada."* y el POST forzado igual se rechaza |
| 12 | Revertir usa el **neto vivo**, nunca el monto del documento, y es idempotente | **PASS** | **Las dos mitades probadas por separado.** (a) *Neto vivo:* pago 37 de **$1.000** con una reversión **parcial de $400 sembrada** en los dos ledgers → la reversión posteó **$600**, no $1.000 (`MovimientosCCProveedor` 80 = `Cargo 600.00`, `CajaMovimientos` 66 = `Ingreso 600.00`), y **arrastró el mismo `MedioPago=4`** del egreso original. (b) *Idempotencia por construcción, no por el flag:* se forzó el pago 30 (ya revertido) de vuelta a `Estado=Pagado` en la base para **saltear la guarda de estado**, con los dos netos en 0 → la segunda reversión **no escribió ni una fila** (`MovimientosCCProveedor` 25→25, `CajaMovimientos` 24→24). Por la vía normal, la guarda de estado responde *"Este pago ya fue revertido."* |
| 13 | No se puede imputar un pago a un día ni a un mes de caja ya cerrado (`LP-009`) | **PASS** | Pago imputado al **15/08/2026** (mes 08/2026 con cierre mensual) → *"La caja del mes 08/2026 ya tiene cierre mensual: no se puede registrar un pago a proveedor con esa fecha."*; ídem al **21/08/2026** (día **y** mes cerrados). **Controles positivos:** el mismo pago imputado a **hoy** (06/10, mes abierto) se acepta y escribe sus dos asientos; y la fecha **futura** (01/12/2026) se rechaza con *"La fecha del pago no puede ser futura."*. La recepción, que **no** toca caja, acepta con razón una fecha pasada (15/09) y persiste `FechaRecepcion = 2026-09-15 03:00:00` UTC = **00:00 ART**, el día de negocio correcto |
| 14 | El `OrigenTipo` nuevo aparece en el combo de filtros de Caja y en todo lector de `OrigenTipo` (`LP-002`) | **PASS** | Combo `#fOrigenTipo` renderizado: los **7** orígenes de `OrigenCajaMovimiento.Todos` con etiqueta legible, incluido `PagoOC = "Pago a proveedor"`. El filtro **filtra de verdad**: `origenTipo=PagoOC` → `recordsFiltered=15` y todas las etiquetas devueltas son `"Pago a proveedor"`; los otros 6 valores y uno inexistente devuelven 200 y el subconjunto correcto. **La grilla ya no muestra el valor crudo:** la fila trae `origenTipo:"PagoOC"` **y** `origenEtiqueta:"Pago a proveedor"`, y la columna pinta la etiqueta — verificado en el navegador, con el arqueo por medio desglosando los egresos en Efectivo / Transferencia / Cheque |

## Máquina de estados de `OrdenCompra` (probada entera)

| desde | acción | resultado esperado | observado |
|---|---|---|---|
| Borrador | Confirmar | permitido | *"Compra #N confirmada. El stock y la deuda se aplican con «Registrar recepción»…"* |
| Borrador | Recibir | **rechazado** | *"La compra está en borrador: confírmela antes de registrar la recepción de la mercadería."* |
| Borrador | Cancelar | permitido | *"Compra #91 cancelada correctamente."* |
| Confirmada | Recibir | permitido | ver criterios 1–6 |
| Confirmada | Confirmar | **rechazado** | *"Solo se puede confirmar una compra en Borrador (esta está confirmada)."* |
| Confirmada | Cancelar | permitido | botón visible y acción aceptada (OC 83) |
| Confirmada | Pagar | permitido (anticipo) | pago de $1.000 sobre la OC 80 sin recibir, aceptado |
| Recibida | Recibir otra vez | **rechazado** | *"Esta compra ya fue recibida: el stock y la deuda ya se aplicaron. Recibirla otra vez duplicaría las dos cosas."* |
| Recibida | Cancelar | **rechazado** | criterio 7 |
| Recibida | Pagar | permitido | criterios 8–9 |
| Cancelada | Recibir | **rechazado** | *"La compra está cancelada: no se puede recibir."* |
| Cancelada | Pagar | **rechazado** | *"La compra está cancelada: no se le pueden imputar pagos."* |

Botones visibles **coinciden** con las transiciones reales en los 4 estados (verificado en navegador).
El único desajuste es el formulario **oculto** `formConfirmar`, que se renderiza también en
`Confirmada` → `LP-026`, `trivial`, sin consecuencia porque el Service rechaza el POST.

## Cobertura del catálogo cross-proyecto

| id | aplica | resultado | acción |
|---|---|---|---|
| **MH-001** | sí | **NO REPRODUCE** | **Ejecutado, no leído.** 25 términos × `/OrdenesCompra/Listar` + 18 ordenamientos (9 columnas × 2 direcciones) + 18 términos × `/Caja/Listar` + 10 variantes × `/Productos/Listar` → **0 respuestas no-JSON, 0 HTTP 500**. Incluyó el caso de **colección vacía** (`ids` sin elementos cuando el término no matchea nada) y caracteres hostiles (`'`, `%`, `_`, `a%b`, `'; DROP TABLE x;--`). Las 8 apariciones nuevas del lote son `List<int>`/`List<enum>`, no de texto |
| **MH-027** | sí | **PASS** | El `OrigenId` del egreso y del `Pago` es el id de la **línea** `PagoOrdenCompra`, no del documento: 3 líneas → 3 pares `(PagoOC, 30/31/32)` distintos, y `PagoVentaId` queda `NULL` (esa columna es de `PagoVenta`). La reversión encuentra el movimiento exacto |
| **MH-033** | sí | **PASS** | El pago a proveedor **sí** baja la caja: 7 `CajaMovimientos` `Tipo=Egreso` con `OrigenTipo='PagoOC'`. Es exactamente el agujero que MH-033 describe, cerrado de entrada |
| **MH-020** (patrón) | sí | **PASS** | Reversión por neto vivo y sin flag `YaRevertido`: ver criterio 12(b), donde la idempotencia se sostuvo con el flag de estado **forzado en contra** |
| **LP-002** | sí | **PASS** | `OrigenCajaMovimiento` centraliza los 7 orígenes + etiquetas; combo y grilla salen del mismo diccionario (criterio 14). `OrigenMovimientoStock` y `MedioPagoCajaMapper` nacen con el mismo patrón, y los `switch` del mapper son **exhaustivos sin `_ =>`** |
| **LP-009** | sí | **PASS** | Criterio 13. Simetría verificada: la guarda corre **sólo** si alguna línea escribe caja, y la recepción (que no toca caja) queda afuera con razón |
| **LP-013** | sí | **SIGUE ABIERTO, sin regresión** | La query de detección devuelve **1 fila**, y es **preexistente** del clon (`CajaMovimientos` id 5, `OrigenTipo='Gasto'`, creada después del cierre de 08/2026) — daño histórico que este lote no causó. **Ninguna escritura de este lote generó una fila nueva**: todos los pagos cayeron en 10/2026, abierto. La expectativa de LP-013 (aviso de desfasaje + remedio) sigue **no implementada** |
| **GAN-005** | sí | **NO REPRODUCE** | Las filas de colección (`Lineas[i].Monto`) **se parsean bien**: `123.45` → `$ 123,45` persistido como `123.45`. No hace falta el marcador `__Invariant` por fila porque el proyecto registra un `InvariantDecimalModelBinderProvider` global (`Program.cs:119`) y los inputs son `type="number"` |
| **SG-001** | sí | **NO REPRODUCE** | Un POST de pago con todas las líneas en cero no bloquea el binding: devuelve *"Cargue al menos una forma de pago con importe mayor a cero."* |
| **MH-003** | parcial | **N/A declarado** | No hay cartera de cheques: un pago con cheque no tiene fecha de emisión que validar. Simplificación declarada y vigente |
| **MH-016** | sí | **ver `LP-024`** | En marihogar el problema fue el `RowVersion` de `Producto`; acá **no hay** `RowVersion`, y el lote agrega el tercer escritor de `Producto.Stock`. Es la cara opuesta del mismo riesgo → `LP-024` |
| **MH-025** | sí | **PASS** | Dos renglones del mismo producto en una compra no dejan el costo a merced del orden de las filas: el costo se acumula **por producto** y queda el promedio ponderado (`costoPorProducto`) |
| **MH-021** | sí | **PASS** | La reversión se imputa a **hoy** y no a la fecha original del pago, y corre `ValidarPeriodoAbiertoAsync` sobre hoy |
| **DN-003** | sí | **PASS** | No hay fallback heurístico por `(documento, monto)`: el neto se acota por `(OrigenTipo, OrigenId)` **y** por proveedor |
| **DN-004** | sí | **N/A** | No existe "editar un pago" en este módulo; sólo revertir |
| **OLV-019** / **MH-047** | sí | **PASS** | `FormaPagoProveedor.CuentaCorriente` no se ofrece en el combo **y** el Service lo rechaza por POST armado a mano: *"«Cuenta corriente» no es una forma de pago: es dejar la deuda a plazo…"*. Las dos puntas, no una sola |
| **VSF-002** / **REG-004** | sí | **PASS** | `Borrador → Cancelada` existe (probado), y la máquina de estados completa coincide con el diseño |
| **LP-004** | sí | **no ejercitada** | El bug es de concurrencia de `Session` entre respuestas del listado; no se forzó el escenario. Fuera del alcance del lote |
| **MH-004** / **MH-007** / **MH-013** / **MH-019** / **MH-022** | no | **N/A** | Son de desgloses de caja mensual, proyección financiera, AFIP y cartera de cheques — fuera de este lote |
| **MH-034 / 035 / 036 / 037 / 038 / 040 / 044 / 048 / 053** | no | **N/A** | Son de backfills de ledger y corrección de fechas de pagos históricos; este lote no hace backfill |

## Cobertura de reglas nuevas/modificadas desde la última corrida

Última validación registrada: **2026-10-05**. Diferencias contra el estado vigente, por índice
(`cat_resumen.txt` + `git log --since=2026-10-05` sobre la instruction 32 y el YAML):

| regla | origen | resultado | acción |
|---|---|---|---|
| **LP-013** | `regresiones-manuales.yml`, agregado el 2026-10-05 14:20 (después de la validación) | **ejecutada en esta corrida** | Query de detección corrida sobre el clon: 1 fila **preexistente**, 0 filas nuevas por este lote. Sigue abierto, sin regresión. Ver la tabla del catálogo |
| instruction `32` | sin cambios desde 2026-10-05 13:43 | **ninguna nueva** | — |
| LP-014 … LP-023 | agregados **hoy** por los otros lotes de esta misma corrida en paralelo | **no se cargaron** | Son hallazgos de esta tanda, no reglas previas sin validar; cada lote los reporta en su bloque |

## Lo que busqué por mi cuenta y no estaba en los criterios

- **La carrera del tercer escritor de `Producto.Stock`** (lo que el brief pidió buscar con ganas).
  **Reproducida, no deducida** → `LP-024`, `major`. `Producto` **no tiene** token de concurrencia
  (barrido sobre `Producto.cs` y `AppDbContext.cs`: ni `RowVersion` ni `[Timestamp]`), y los tres
  escritores son incompatibles: la venta resta, `RecibirAsync` suma, y `AjusteStockService` hace un
  **SET absoluto** del valor que el operador tipeó más `StockVerificado = true`. Secuencia real:
  la pantalla de ajuste mostró **"Stock actual 30,000"** → entró una recepción de **+5** (stock 35)
  → el operador guardó su conteo de **29** → quedó `Stock = 29`, **las 5 unidades recibidas
  desaparecieron de la columna**, `StockVerificado = 1` sobre un número equivocado, y
  **`SUM(MovimientosStock) = 35` contra `Productos.Stock = 29`**. No hay bloqueo ni aviso antes de
  escribir; el único indicio es el toast posterior (*"actualizado de 35,000 a 29"*), con un número
  que el operador nunca vio. **No es una regresión de este lote** (la carrera venta-vs-ajuste ya
  existía y el alcance declarado dice que el ledger no reconstruye la columna), pero el lote agrega
  el tercer escritor y, con el ledger nuevo, vuelve el daño **medible por primera vez** — y nada lo
  mide. Es el principal riesgo de liberación.
- **El hueco del ledger de stock sin historia — clasificado: contenido.** El ledger tiene **un solo
  lector** (`OrdenesCompraController:486`), y lee **acotado por `(OrigenTipo, OrigenId)`** de una
  compra puntual: nunca pide "todos los movimientos de un producto", así que **ninguna pantalla
  espera historia completa** y la falta de migración hacia atrás no rompe nada hoy. Verificado además
  que la pantalla de historial de stock lee `AjustesStock` (otra tabla), no el ledger nuevo.
  **Consecuencia a declarar:** el sistema queda con **dos historias parciales de stock que no
  coinciden** (`AjustesStock` y `MovimientosStock`) y ninguna completa. El primer lector que pida
  "el historial del producto X" va a tener que elegir una de las dos o unirlas.
- **`PrecioVentaDesactualizado`: se prende bien y NO se prende cuando no corresponde.** Las tres
  ramas probadas bajando la bandera a `false` antes de cada una: recibir al **mismo costo** (10 → 10)
  deja la bandera en **`0`** y sólo actualiza `FechaUltimoCostoCompra` (el toast omite el aviso de
  costo); recibir a costo **distinto** (10 → 25) la prende y actualiza `PrecioCompra`, dejando
  `PrecioVenta` en 90; y recibir a costo **0** (compra sin precios) **no pisa** el costo (queda 25) ni
  prende la bandera. La columna, el filtro, el orden y la búsqueda global por *"Precio sin
  recalcular"* funcionan y el badge se ve en el navegador con la fecha en el `title`.
- **Autorización, con antiforgery válido.** Como `Vendedor`: las 6 pantallas del lote devuelven 302 a
  `/Account/AccessDenied`, el **sidebar no ofrece** Compras / Proveedores / Caja / Pagos programados,
  y los 4 POST de dinero y stock (`Recibir`, `RegistrarPago`, `RevertirPago`, `Cancelar`) —
  **con un token tomado de una pantalla que el Vendedor sí puede abrir**, para probar autorización y
  no antiforgery — se rechazan todos, con `PagosOrdenCompra` / `CajaMovimientos` / `MovimientosStock`
  en 11 / 24 / 11 antes y después.
- **El toast de advertencia de los rechazos de pago: NO es un defecto.** Mi extractor levantaba el
  literal `Swal.fire({icon:'warning'… 'Cargá al menos una forma de pago con importe mayor a cero.'})`
  del script inline de `RegistrarPago.cshtml` en **toda** respuesta rechazada, y parecía un mensaje
  engañoso. Es un **guard de submit del cliente** que sólo dispara cuando el total es ≤ 0 y nunca
  llegó a ejecutarse. Confirmado en el navegador: lo que el operador ve es el mensaje correcto del
  Service en el resumen de validación.
- **`buscar "Al día"` en el catálogo devuelve 0** → `LP-025`, `trivial`. La etiqueta minoritaria
  (*"Precio sin recalcular"*) se encuentra; la mayoritaria (*"Al día"*, 112.486 filas) devuelve
  **0** porque `AgregarAcotadoAsync` **descarta el conjunto entero** cuando supera su tope, en vez
  de degradar. El filtro de columna equivalente sí devuelve 112.486.
- **`precioVentaDesactualizado=xxx`** (valor basura por query string) cae en "Todos" con HTTP 200,
  sin 500. Criterio laxo coherente con cómo se resolvió `LP-011`. **No es defecto.**
- **Impacto declarado por el implementador, confirmado y NO reportado como bug:** es el primer egreso
  automático del arqueo. El arqueo por medio de `/Caja` ya muestra egresos de **$8.240,61** en
  Efectivo, **$3.566,66** en Transferencia y **$1.000,00** en Cheque, todos nuevos. Es el salto
  esperado, igual que en marihogar.
- **Dato de entorno para los próximos lotes:** el scratchpad de la sesión **se comparte entre lotes
  paralelos**. Un `lib.js` mío fue sobrescrito en disco por el harness de otro lote a mitad de
  corrida. Trabajar siempre en un subdirectorio propio (`scratchpad/qa_l3/`), no en la raíz.

## Partes de defecto emitidos al Implementador

### `LP-024` — `major` — la carrera del tercer escritor de `Producto.Stock` (riesgo de liberación, NO bloquea el gate)

- **Reproducción:** abrir `/Stock/Ajuste?productoId=112507` (muestra `Stock actual 30,000`); sin
  cerrarlo, recibir una OC de ese producto por 5 unidades; guardar el ajuste con `CantidadNueva = 29`.
- **Evidencia observada:** `Productos.Stock = 29.000`, `StockVerificado = 1`,
  `SUM(MovimientosStock WHERE ProductoId=112507) = 35.000`. Ningún aviso previo a la escritura.
- **`archivos_fix` sugeridos (hipótesis, no instrucción):** `Web/Models/AjusteStockViewModel.cs` y
  `Web/Views/Stock/Ajuste.cshtml` (hacer viajar el stock leído como hidden),
  `Infrastructure/Services/AjusteStockService.cs` (comparar contra `producto.Stock` antes del SET
  absoluto y rechazar si cambió; opcionalmente escribir la fila de `MovimientoStock` del ajuste, cuyo
  origen `AjusteManual` ya está declarado sin escritor). Camino de fondo alternativo: token de
  concurrencia en `Producto` — **ojo con MH-016 y con el aumento masivo de la Entrega 6** antes de
  tomarlo. **`migracion_ef`:** ninguna por el camino del hidden; sí por el del token.
- **Criterio de re-verificación:** con el formulario de ajuste abierto, una recepción que entra en el
  medio hace que el guardado sea **rechazado** nombrando lo que entró, y `Producto.Stock` conserva el
  valor que dejó la recepción. Control negativo: sin recepción en el medio, el ajuste se guarda normal.

### `LP-025` — `trivial` — la búsqueda global por la etiqueta mayoritaria devuelve 0

- **Reproducción:** `POST /Productos/Listar` con `search[value] = "Al día"`.
- **Evidencia observada:** `recordsFiltered = 0`, contra `112.486` del filtro de columna equivalente
  (`precioVentaDesactualizado=false`). `"Precio sin recalcular"` → 2, correcto.
- **`archivos_fix` sugerido:** `Infrastructure/Services/ProductoService.cs` — que la rama de `"Al día"`
  entre al `WHERE` final como **predicado booleano** en vez de pasar por `AgregarAcotadoAsync`, que
  silencia su aporte al pasarse del tope. Revisar las otras ramas que usan ese helper por si alguna
  más puede ser mayoritaria. **`migracion_ef`:** null.
- **Criterio de re-verificación:** `search[value]="Al día"` devuelve el mismo `recordsFiltered` que el
  filtro de columna, o 0 **con un aviso explícito** de que la búsqueda por etiqueta no se aplicó; y
  `"Precio sin recalcular"` sigue devolviendo las filas con la bandera prendida.

### `LP-026` — `trivial` — formulario oculto de una transición no disponible

- **Reproducción:** `GET /OrdenesCompra/Details/80` (estado `Confirmada`) y buscar `form[action]`.
- **Evidencia observada:** `formConfirmar` presente sin botón que lo dispare. El POST se rechaza
  (*"Solo se puede confirmar una compra en Borrador…"*), así que es superficie muerta, no un agujero.
- **`archivos_fix` sugerido:** `Web/Views/OrdenesCompra/Details.cshtml` — partir el
  `@if (Model.PuedeConfirmar || Model.PuedeCancelar)` en dos bloques, uno por bandera.
  **`migracion_ef`:** null.
- **Criterio de re-verificación:** en `Confirmada` el HTML **no** contiene `formConfirmar` y sí
  `formCancelar` y `formRecibir`; en `Borrador` contiene los dos primeros y no el tercero; en
  `Recibida` y `Cancelada`, ninguno.

### Estado de los partes de la corrida anterior

Los 7 defectos del Sprint 0 (`LP-006`..`LP-012`) quedaron **CERRADOS** en la re-verificación del
2026-10-05 y **no reaparecieron** en este alcance: `LP-009` se re-ejercitó con la vía nueva del pago a
proveedor (criterio 13, PASS) y `LP-002` con el `OrigenTipo` nuevo (criterio 14, PASS). `LP-013`
sigue **abierto** por diseño (era una mejora, sin decisión pendiente) y esta corrida confirma que no
regresó.

## Riesgos de liberación y mitigaciones

1. **`LP-024`, el más importante.** Hoy, en producción, un conteo físico guardado sobre una pantalla
   abierta desde antes de una recepción borra las unidades recibidas sin dejar rastro en la columna.
   La ferretería va a recibir mercadería y ajustar stock el mismo día, así que la ventana es real.
   *Mitigación hasta el fix:* indicarle al cliente que cierre y reabra la pantalla de ajuste antes de
   guardar un conteo, y correr la query de detección de `LP-024` como control post-deploy.
2. **Dos historias parciales de stock.** `AjustesStock` y `MovimientosStock` conviven, ninguna
   completa, y el ledger nuevo arranca vacío. *Mitigación:* no construir ninguna pantalla de
   "historial de stock del producto" hasta decidir cuál de las dos es la fuente, y dejar escrito que
   el ledger arranca el día del deploy.
3. **El salto de egresos del arqueo.** Primer egreso automático de caja del módulo de Compras: los
   egresos del período suben de golpe el día del deploy. No es un bug. *Mitigación:* avisarlo antes,
   no después — en marihogar se tomó como un error de la caja.
4. **El camino de conversión no tiene ni un dato real que lo ejercite.** `laplatense_dev` tiene **0**
   productos con `UnidadCompra != UnidadVenta` sobre 112.485, y los 2.635 candidatos a corte por metro
   esperan marcación manual. Todo lo verificado del bulto se midió con productos sembrados.
   *Mitigación:* que el cliente marque unos pocos productos reales por bulto y recibir **una** compra
   chica antes de usarlo en serio.
5. **`FactorConversion` es fijo por producto** (pregunta abierta 6 de `4-presupuestador.md`, sin
   resolver). El snapshot en la línea absorbe el caso del bulto distinto por proveedor **si el
   operador corrige el factor a mano al cargar la compra**; no lo resuelve de raíz.
6. **`LP-013` sigue abierto** y el clon arrastra 1 movimiento posteado dentro de un mes ya cerrado.
   *Mitigación:* la query de detección como control de pre/post-deploy, que es lo acordado.

## Pruebas mínimas ejecutadas

- Build de la solución; 14 criterios de aceptación; 12 transiciones de la máquina de estados
  (válidas e inválidas).
- **4 inyecciones de falla** por `CHECK` constraint (pago de una línea, pago multi-línea con la
  primera sana, recepción, y el `CHECK` quitado al final) con los tres ledgers contados antes y después.
- **71 llamadas** a los listados server-side del alcance (25 términos + 18 ordenamientos en
  `/OrdenesCompra/Listar`, 18 términos y 9 valores de filtro en `/Caja/Listar`, 10 variantes en
  `/Productos/Listar`) → 0 no-JSON, 0 HTTP 500.
- 3 ramas de `PrecioVentaDesactualizado` (mismo costo / costo distinto / costo 0), con la bandera
  bajada antes de cada una.
- 2 reproducciones de la carrera recepción-vs-ajuste y 1 verificación de que el ledger y la columna
  divergen.
- Autorización: 6 GET + 4 POST como `Vendedor`, con token válido.
- **Navegador real:** 8 pantallas de smoke (todas 200, con contenido) + 5 verificaciones de render
  (tarjeta del ledger de stock, botones por estado, rechazo del pago visible, filtro de Caja por el
  origen nuevo, columna y filtro nuevos del catálogo) + la CC del proveedor con su saldo acumulado.
  **0 `pageerror` y 0 `console.error` en todo el recorrido.**

## Checklist de salida para merge

- [x] Build sin errores nuevos; 8 advertencias, todas preexistentes.
- [x] Migración `EntregaTres_RecepcionMercaderiaYPagosProveedor` aplicada y verificada en la copia.
- [x] Los 14 criterios de aceptación en PASS con evidencia observada.
- [x] Máquina de estados completa, válidas e inválidas, y botones que coinciden con las transiciones.
- [x] Atomicidad de los dos y de los tres ledgers probada **por inyección de falla**, no por lectura.
- [x] `LP-002` / `LP-009` / `MH-001` / `MH-027` / `MH-033` / `GAN-005` verificados ejecutando.
- [x] Autorización de las acciones de dinero y stock probada con antiforgery válido.
- [x] Sin errores de JS en el recorrido del navegador.
- [x] `git status --porcelain` limpio en el repo del sistema (sólo `?? .claude/`, preexistente).
- [x] `CHECK` constraints de inyección de falla eliminados de la copia.
- [ ] **`LP-024` emitido al Implementador** — no bloquea este gate (ningún criterio lo cubre y el
      comportamiento coincide con el alcance declarado), pero es el riesgo 1 de liberación y
      conviene cerrarlo **antes** de que el cliente empiece a recibir mercadería y contar stock el
      mismo día.
- [ ] `LP-025` y `LP-026` emitidos, `trivial`, pueden viajar en la próxima ronda de fixes.
- [ ] Avisar el salto de egresos del arqueo **antes** del deploy.


# Entrega 3 — LOTE 4: moneda congelada en la compra y pagos programados (QA, 2026-10-06, rama `entrega-1-migracion`)

## Commit evaluado: `4246b42` "Entrega 3 item 4c + paso 6: moneda congelada en la compra y pagos programados"

## **NO-GO.** 10 de los 11 criterios en PASS con evidencia observada; **el criterio 10 FALLA** (`LP-023`, `major`). Deja además 1 hallazgo `minor` (`LP-022`).

El núcleo de plata de la ola — la conversión a pesos, la cotización congelada y el par de asientos
del pago programado — está **correcto al centavo** y reproduce exactamente los 5 números que midió
el Implementador. Lo que falla es la **idempotencia del aviso**: la garantía que el diseño declara
que vive en la base no vive ahí, vive en un flag en memoria del middleware, y el propio diseño dice
explícitamente que no debe depender de eso.

## Entorno y metodología

- Base **clonada y aislada**: `laplatense_dev` → **`laplatense_qa_l4`** (`mysqldump` + restore,
  39 tablas, 112.485 productos, 85 proveedores, **0 compras**). Nunca se tocó `laplatense_dev` ni
  producción. El clon **queda vivo** porque es el fixture de la re-verificación de `LP-023`.
- App levantada contra el clon pasando `ConnectionStrings__DefaultConnection` por variable de
  entorno, en `https://localhost:7415` (puerto propio del lote).
- MCP `playwright` **no disponible** en la sesión. Se usó un **arnés HTTP propio en Node** (cookies
  de Identity + `__RequestVerificationToken` del form) que recorre las pantallas reales, más
  **assertions SQL** contra el clon. Para la concurrencia se usó además un **arnés .NET propio**
  (scratchpad) que resuelve `IAvisoPagosProgramadosService` en N scopes y lo llama con `Barrier`.
- **No se usó el arnés del Implementador** (`tools/ArnesEntrega3Item4c`): evaluación independiente.
  Nota al margen: ese arnés apunta a `laplatense_dev` hardcodeado, o sea escribe la base compartida.
- Usuario de prueba: `qa.super@test.local`, con contraseña fijada **en el clon** y los roles
  `SuperUsuario` + `Administrador` (para ejercitar la deduplicación de destinatarios).
- **El repo del sistema no se modificó**: `git status --porcelain` en `C:\Sistemas\Ferreteria La
  Platense` devuelve únicamente `?? .claude/` (directorio de memoria de agentes, ya presente y sin
  trackear al abrir la sesión). Cero `Edit`/`Write`/`sed` sobre el repo bajo prueba.

## Los 5 números del Implementador: reproducidos, uno por uno

Compra en USD, 10 bultos a US$ 100, 10% + 5% en cascada, IVA 21%, cotización congelada $ 1.480,50,
`FactorConversionAplicado` 10, producto #1 (`PrecioCompra` previo $ 6.320,12). Compra **#84**.

| Medición | Esperado | Observado | |
|---|---|---|---|
| Total del documento | US$ 1.034,55 | `OrdenesCompra.Total = 1034.55` | PASS |
| `Cargo` en la CC del proveedor | $ 1.531.651,28 | `MovimientosCCProveedor` #66, `Tipo=1`, `1531651.28` | PASS |
| `Egreso` en caja al pagar el total | $ 1.531.651,28 | `CajaMovimientos` #55, `Tipo=2`, `1531651.28` | PASS |
| Saldo del proveedor al pagar el total | $ 0,00 | `SUM(cargos) - SUM(pagos) = 0.00` | PASS |
| `Producto.PrecioCompra` resultante | $ 12.658,28 | `Productos.PrecioCompra = 12658.28` | PASS |

El `8,55` del bug viejo se observó **como control positivo** en la compra en pesos (#85/#86): con el
mismo precio nominal de 100 por bulto pero en pesos, `PrecioCompra` queda en `8.55`, que ahí **es
correcto**. Es exactamente la diferencia que la ola vino a arreglar.

## Cobertura por criterio de aceptación

| # | Criterio | Resultado | Evidencia observada |
|---|---|---|---|
| 1 | Compra en USD postea el `Cargo` en pesos por el total convertido | **PASS** | Compra #84: `Total=1034.55`, `TotalEnPesos=1531651.28`, `Cargo` #66 = `1531651.28` |
| 2 | El pago postea el `Egreso` en pesos y el saldo cierra en cero | **PASS** | `CajaMovimientos` #55 `Tipo=2 1531651.28`; saldo del prov. 113 = `0.00` exacto |
| 3 | `Producto.PrecioCompra` en pesos, neto de descuentos, por unidad de venta | **PASS** | `12658.28` = 855 USD × 1480,50 ÷ 10 bultos ÷ factor 10. `PrecioVentaDesactualizado=1` |
| 4 | Cambiar `Proveedor.TipoCambio` después no altera ninguna compra cargada | **PASS** | Ficha 113 → 9.999,0000; #84 sigue `Cotizacion=1480.5000`, `TotalEnPesos=1531651.28`, saldo `0.00`. La pantalla sigue diciendo "Cotización congelada: $ 1.480,50" y agrega aparte "Hoy el proveedor tiene $ 9.999,00" |
| 5 | Compra en pesos sin regresión | **PASS** | #85/#86: `Total == TotalEnPesos == 1034.55`; `Cargo` en pesos; una cotización colgada posteada a mano **se descarta** (`Cotizacion` persiste `NULL`) |
| 6 | No se puede confirmar en moneda extranjera sin cotización | **PASS** | Las **4 mitades** de la guarda, por texto en pantalla: alta sin cotización y con cotización `0` → rechazadas; **confirmar** (#87 sembrada) → "La compra está en dólares: no se puede confirmar la compra sin la cotización usada…", queda en Borrador; **recibir** (#88 sembrada) → mensaje equivalente, queda Confirmada, **sin `Cargo` y sin mover stock** |
| 7 | Un pago programado no mueve ni CC ni caja hasta confirmarse | **PASS** | Pago #31 nace `Pendiente`; CC del prov. 114 queda en `2069.10` y `CajaMovimientos` en 10 filas, idénticos al snapshot previo; 0 movimientos con `OrigenId` del pago |
| 8 | Confirmarlo postea el par con la fecha de HOY, no la tentativa | **PASS** | Tentativa `2026-10-16`; al confirmar, `Egreso` #56 y `Pago` #70 **ambos** con `Fecha` = `2026-10-06`. `FechaPagoTentativa` **se preserva** (16/10) como registro del plazo |
| 9 | Una notificación por pago y por usuario, no se repite al día siguiente | **PASS** | 2 pagos vencidos × 2 destinatarios únicos = **exactamente 4** filas. El usuario con **dos roles** recibió 2 y no 4 (dedup por Id). Filas marcadas `Notificado=1`. Importes **en pesos** también para la compra en USD |
| 10 | Corriendo el chequeo dos veces no se duplica ninguna notificación | **FAIL** | **En serie PASA** (20 requests más → 4; 3 reciclados de proceso → 4). **En paralelo FALLA**: ver `LP-023` |
| 11 | `ValidarPeriodoAbiertoAsync` (`LP-009`) sigue aplicando al confirmar | **PASS** | Las **dos** ramas: cierre **mensual** 10/2026 sembrado → "La caja del mes 10/2026 ya tiene cierre mensual: no se puede confirmar un pago programado (se imputa al día de hoy)"; cierre **diario** de hoy → "La caja del día 06/10/2026 ya está cerrada: …". En los dos casos el pago queda `Pendiente` y la caja sin mover |

### Nota metodológica sobre el criterio 11 (instrumento corregido en vivo)

El primer intento de la rama "día cerrado" **no bloqueó**, y el reflejo era anotar un defecto. No lo
era: `CierreCajaDiario.Fecha` se persiste como **medianoche naive** (`CerrarDiaAsync` guarda
`fechaDia` ya `.Date`, y `EstaCerradoAsync` compara `c.Fecha == dia`), no como el instante UTC
`03:00` que usa `CajaMovimientos`. La fila preexistente de la base (`2026-08-21 00:00:00`) lo
confirma. Sembrado con la convención real, la guarda bloquea. **El síntoma era del instrumento.**

## Defecto nuevo — `LP-023` — `major`

### El chequeo del aviso duplica TODAS las notificaciones cuando corre concurrente

`PagoProveedorService.ObtenerYMarcarPagosVencidosNoNotificadosAsync` lee con `ToListAsync()` y
**recién después** marca `Notificado = true` y hace `SaveChangesAsync`: sin transacción, sin bloqueo
de fila y sin token de concurrencia. Entre el `SELECT` y el `UPDATE` todos los lectores concurrentes
ven `Notificado = 0` y **todos se llevan el mismo lote**.

Reproducido por **dos vías independientes**, con 2 pagos vencidos y 2 destinatarios (esperado: 4):

- **Service, grado 8 con `Barrier`:** las 8 llamadas devuelven `4` (ninguna devuelve `0`) y
  `Notifications` queda con **32 filas**. Cada par usuario/pago repetido 8 veces. **3/3 rondas.**
- **HTTP, dos worker processes** contra la misma base (web garden / ventana de reciclado solapado),
  primer request del día en simultáneo: **8 filas** en vez de 4, cada notificación duplicada ×2.

Lo que hace esto `major` y no cosmético: el XML-doc afirma *"correrlo dos veces, o dos veces en
paralelo, no duplica avisos"* y *"si dos requests entran a la vez, el segundo encuentra la lista
vacía"*. **Las dos afirmaciones son falsas.** La carrera hoy queda tapada por el `lock` + flag
`static` de `AvisoPagosProgramadosMiddleware`, que serializa **dentro de un proceso** — y el propio
diseño declara que la garantía **no debe** vivir en ese flag porque se pierde con cada reciclado de
pool. Efectivamente no vive ahí: **vive sólo ahí.**

Es la **misma familia** que el `LP-018` que levantó otro lote de esta corrida (neto vivo leído antes
de abrir la transacción, sin bloquear la fila). Dos apariciones del mismo patrón en una sola corrida.

## Defecto nuevo — `LP-022` — `minor`

El total en pesos es la cifra **principal** de la grilla de compras, pero el buscador global sólo lo
encuentra con el importe **exacto y con centavos**: `"1531651,28"` → 2 filas; `"1531651"` → **0
filas**; `"1531"` y `"531651"` → 0 filas. El control `"1034"` (total del **documento** sin centavos)
→ 4 filas, correcto. Causa: `RangoImporte` es un match exacto de ±medio centavo, y la pasada que
hace el match parcial (`IdsPorSubstringDeImporte`) recibe únicamente pares `(Id, o.Total)`, nunca
`TotalEnPesos`. El comentario del propio código declara la intención contraria.

## El hallazgo más caro de la ola: el backfill de `TotalEnPesos`. **Verificado, cierra bien**

Dev tiene **0 compras**, así que se **fabricaron 4 compras preexistentes** en el clon (una por
estado: Recibida, Confirmada, Borrador, Cancelada; totales `1234.56`, `999999.99`, `0.00`, `121.00`),
se **simuló el estado pre-migración** (drop del índice y de las 3 columnas) y se corrió el **`Up()`
exacto** que genera `dotnet ef migrations script` para `20261006011819`.

- Las 4 filas quedan `Moneda = 1` (Peso) y `TotalEnPesos = Total`. **Ninguna quedó en 0 indebidamente.**
- La compra con `Total = 0` queda en `TotalEnPesos = 0`, que es lo correcto (el `WHERE Total <> 0`
  no la toca y no hay nada que convertir).
- **Idempotencia:** correr los dos `UPDATE` una segunda vez no cambia ninguna fila.
- El `Moneda = 0` que dejaría el `defaultValue` de EF **no sobrevive**: el primer `UPDATE` lo repara,
  y se verificó que el filtro y la comparación con `Peso` encuentran las filas después.

## La resta `total − pagado`: no quedó una quinta copia

Barrido de `total - pagado` y de todo uso de `OrdenCompra.Total` en Application/Infrastructure/Web:
la **única** resta viva es `SaldosCompraDto.SaldoPendiente => TotalEnPesos - TotalPagado` y
`SaldoSinComprometer => TotalEnPesos - TotalPagado - TotalProgramado`. Punto único, en pesos.

Los lugares que el parte marcaba como riesgo, verificados **por observación**:

- **Listado ordenando por `Total`:** el `switch` mapea `"total"` → `OrderBy(o.TotalEnPesos)`,
  server-side. Observado: las compras en USD ordenan **arriba** de una de $ 999.999,99 pese a que su
  número de documento es menor. Sin mezcla de monedas.
- **CC del proveedor:** la cifra principal de cada fila es la de **pesos** y el importe en moneda
  extranjera va como sub-línea atenuada con su cotización congelada ("US$ 1.034,55 a $ 1.480,50").
  Correcto, sin mezcla.
- **Dashboard:** no referencia compras. No aplica.
- Los 5 usos restantes del `Total` del documento en vistas van **siempre** acompañados de
  `MonedaSimbolo`. Ninguno queda "pelado".

## Cobertura del catálogo cross-proyecto

| id | Resultado | Evidencia |
|---|---|---|
| `MH-001` (IN sobre colección local) | **PASS, por ejecución** | Los destinatarios salen de `GetUsersInRoleAsync` (join en la base), no de un `Contains` sobre lista local: 4 notificaciones creadas sin 500. Y el otro candidato real, `ProveedorService` con `monedas.Contains(p.Moneda)`, **se ejecutó con la colección vacía** (`"zzzzqqqq"` → 0 monedas): HTTP 200, 0 filas, sin excepción. MH-001 es específico de colecciones locales de **string**, no de enums |
| `LP-002` (3ª copia del mapa de monedas) | **PASS** | Búsqueda de proveedores por `"dolares"`, `"Dólares"` y `"Dolar"` → 1 fila cada una. La etiqueta visible y el nombre del enum resuelven los dos desde `ConversionMoneda` |
| `LP-003` / `GAN-005` / `GAN-006` (cultura e inputs decimales) | **PASS** | `Cotizacion` es `decimal(18,4)` y es la superficie nueva de riesgo: renderiza `value="1480.5075"` (punto invariante, no coma), `step="0.0001"` coherente con la precisión, y emite el `<input name="__Invariant" value="Cotizacion">`. Round-trip de 3 guardados consecutivos: la cotización no deriva y `TotalEnPesos` queda en `1531659.03`, igual al cálculo independiente de QA |
| `MH-021` (fecha sugerida en vez de la real) | **PASS** | Es el criterio 8. El par va con la fecha de hoy, no con la tentativa |
| `MH-003` (fecha futura por POST directo) | **PASS** | `Fecha = 2027-01-15` por POST directo al pago → rechazado server-side (repintado, sin redirect) y **no se creó ninguna fila** con fecha futura |
| `MH-019` (compromiso zombi de una compra cancelada) | **PASS** | Compra #90 cancelada con un pago programado vivo: **no aparece** en la grilla de Pagos programados y **no se notifica** (las dos consultas filtran `Estado != Cancelada`). La fila queda `Pendiente` e inerte, sin superficie que la cuente |
| `MH-020` / `MH-027` (reversión por el neto vivo) | **PASS** | Reversión del pago #30 de la compra en USD: contramovimientos **en pesos** (`CajaMovimientos` #57 `Tipo=1 1531651.28 EsReversion=1`; CC #72 `Cargo 1531651.28`), pago → `Revertido`, y el saldo del proveedor vuelve a `3063302.56` = exactamente los `TotalEnPesos` de las dos compras recibidas |
| `MH-015` / `MH-018` (columna ordenable sin `SortColumn`) | **N/A** | La grilla de Pagos programados es una `<table>` plana sin DataTables: no hay encabezados ordenables ni caja de búsqueda |
| `LP-004` (buscador que no busca) / `LP-006` (reloj 12h) | **N/A** | Ídem: sin buscador, y la grilla no muestra hora (columnas: Vence, Proveedor, Compra, Forma de pago, Importe, Nota) |
| `LP-022` (nuevo) | **FAIL** | Ver arriba |
| `LP-023` (nuevo) | **FAIL** | Ver arriba |

## Cobertura de reglas nuevas/modificadas desde la última corrida

El campo "Última validación de reglas cross-proyecto" ya quedó en **2026-10-06** por un lote previo
de esta misma corrida, así que el barrido completo de reglas nuevas **se hereda** y no se repite acá.
Lo que sí se ejecutó contra este alcance son las reglas agregadas **durante** esta corrida por los
lotes en paralelo y que tocan superficie mía: `LP-017` (buscador global que no alcanza una columna
**derivada**) — se ejecutó sobre la grilla de compras y **destapó `LP-022`**, que es la misma familia
sobre una columna **persistida** pero cubierta por sólo una de las dos pasadas de búsqueda. Y
`LP-018` (lectura sin bloqueo antes de la transacción), que es la familia de `LP-023`.

## Cobertura de la máquina de estados

- **Compra:** `Borrador → Confirmada → Recibida` recorrido de punta a punta (#84, #85, #86, #89).
  `Borrador|Confirmada → Cancelada` verificado (#90, desde Confirmada, con motivo registrado).
  `Recibida → Cancelada` **no se ofrece** (coherente con que `Recibida` ya posteó stock y deuda).
  Confirmar y recibir **bloqueados** sin cotización en moneda extranjera (#87, #88).
- **Pago a proveedor:** `Pendiente → Pagado` por confirmación (#31), `Pagado → Revertido` por
  reversión (#30), alta inmediata directo en `Pagado` (#30). `Pendiente` reprogramado: la tentativa
  se mueve al 25/10 y **`Notificado` vuelve a 0** (reabre el aviso), sin tocar caja ni CC.

## Lo que no se pudo observar (declarado, no aprobado por interpretación)

- **"No se repite al día siguiente"** (mitad del criterio 9): no se corrió el reloj. Se cubrió por el
  mecanismo equivalente y más fuerte: 3 **reciclados de proceso** (que resetean el flag en memoria y
  fuerzan el re-chequeo) dejan las notificaciones en 4. La exclusión del día siguiente la da el mismo
  `!Notificado` que ahí se ejercita, y es independiente de la fecha.
- **El día que nadie entra al sistema:** por diseño el chequeo no corre, y el día que alguien entra
  los vencidos se avisan igual porque el filtro es `FechaPagoTentativa <= hoy` (no "= hoy"). Se
  verificó que un pago vencido el 02/10 y otro el 05/10 se avisan el 06/10. Consecuencia aceptada del
  chequeo oportunista: el aviso puede **llegar tarde**, nunca perderse.
- **50 personas en el mismo segundo:** no se simularon 50 sesiones reales. Lo que decide el criterio
  es la atomicidad del reclamo, y eso se midió con grado 8 sincronizado por `Barrier` y con dos
  worker processes, que es la forma en que el fallo aparece. El resultado es `LP-023`.

## Riesgos de liberación

1. **`LP-023` (`major`) — bloqueante del criterio 10.** El impacto es ruido en la campana, no plata:
   ningún asiento se duplica. Pero la garantía declarada es falsa y el único freno es un flag en
   memoria que el propio diseño descarta. Si el hosting corre un solo worker process, en la práctica
   casi no se ve; en una ventana de reciclado solapado, sí. **Y queda una trampa para el próximo
   que agregue un segundo llamador del Service** (un botón "correr ahora", un hosted service si
   alguna vez hay pool always-running): hereda la duplicación sin ninguna señal.
2. **El `TotalEnPesos` de una compra en moneda extranjera queda congelado.** Es la decisión correcta,
   pero significa que corregir una cotización mal tipeada **después de recibida** no tiene camino por
   UI: el `Cargo` ya está posteado. No se probó porque no está en los criterios; se declara como
   superficie a cubrir en la próxima ola (misma forma que `LP-013`).
3. **`LP-022` (`minor`)** degrada el buscador en la columna que el operador más mira, sin riesgo de dato.
4. El backfill de la migración **es correcto pero se verificó sobre filas fabricadas**, porque dev
   tiene 0 compras. En producción (6 migraciones atrás) **sí hay compras**: conviene correr el conteo
   de `OrdenesCompra WHERE TotalEnPesos = 0 AND Total <> 0` **después** del deploy como control, que
   tiene que dar 0.

## Estado go/no-go

**NO-GO** para el criterio 10. El resto del lote (los 10 criterios restantes, el backfill, la
unificación de saldos y las 11 entradas del catálogo aplicables) está en condiciones de merge.
La recomendación es cerrar `LP-023` y re-verificar en contexto nuevo: es un cambio acotado a un
método y no toca la aritmética de plata, que ya está verificada.

## Partes de defecto emitidos al Implementador

### Parte 1 — `LP-023` — `major` — idempotencia del aviso de pagos programados

- **Reproducción:** sembrar 2 `PagoOrdenCompra` `Pendiente` con `FechaPagoTentativa <= hoy` y
  `Notificado = 0` sobre compras no canceladas; 2 usuarios únicos en `SuperUsuario`/`Administrador`;
  vaciar `Notifications`. Resolver `IAvisoPagosProgramadosService` en 8 scopes independientes y
  llamar `EjecutarChequeoDelDiaAsync()` en los 8 sincronizados con `Barrier`.
- **Evidencia observada:** las 8 llamadas devuelven `4`, `Notifications` queda con **32 filas**
  (esperado 4), cada par usuario/pago ×8. 3/3 rondas. Por HTTP con dos worker processes: **8 filas**.
- **`archivos_fix` sugeridos (hipótesis, no instrucción):**
  `FerreteriaLaPlatense.Infrastructure/Services/PagoProveedorService.cs` —
  **Hipótesis A (preferida):** reclamar primero con un `UPDATE` condicional único
  (`ExecuteUpdateAsync` sobre el mismo `Where`, poniendo `Notificado = true`) y leer después lo
  reclamado; un `UPDATE` con `WHERE` es atómico bajo InnoDB, así que el segundo llamador afecta 0
  filas. Para saber **cuáles** filas se reclamó hace falta un discriminador: marcar dentro de una
  transacción y leer en la misma tx, o agregar `NotificadoAt` y filtrar por el valor de esta corrida.
  **Hipótesis B:** transacción + `SELECT … FOR UPDATE` de los candidatos antes de marcar.
  **No usar `RowVersion`**: en este stack ya mordió dos veces (`REG-001`, `MH-016`).
- **`migracion_ef`:** sólo si se toma el camino de la columna discriminadora (`NotificadoAt`
  `datetime(6) NULL`). Aditiva, sin backfill: `NULL` = "no notificado", coherente con
  `Notificado = 0` preexistente. Con `SELECT … FOR UPDATE` no hace falta migración.
- **Criterio de re-verificación (la assertion que decide el PASS):** con 2 pagos vencidos y 2
  destinatarios únicos, **8 llamadas concurrentes dejan exactamente 4 filas en `Notifications` y 7
  de las 8 devuelven 0**; ídem con 2 worker processes; la corrida en serie sigue sin duplicar; y
  reprogramar sigue reabriendo el aviso una sola vez por destinatario.
- **Fixture listo:** base `laplatense_qa_l4`, pagos `#32`/`#33`, 2 destinatarios ya configurados.

### Parte 2 — `LP-022` — `minor` — buscador global por el total en pesos

- **Reproducción:** `POST /OrdenesCompra/Listar` con `search[value] = "1531651"` sobre una compra con
  `TotalEnPesos = 1531651.28`.
- **Evidencia observada:** `recordsFiltered = 0`. Con `"1531651,28"` → 2 filas. Control `"1034"`
  (total del documento) → 4 filas.
- **`archivos_fix` sugerido (hipótesis):**
  `FerreteriaLaPlatense.Infrastructure/Services/OrdenCompraService.cs` — en el bloque de búsqueda
  global, la proyección que alimenta `IdsPorSubstringDeImporte` trae sólo `o.Total`; pasar también
  `o.TotalEnPesos` y unir los ids, respetando el tope `MaxFilasSubstringNumerico`.
- **`migracion_ef`:** ninguna.
- **Criterio de re-verificación:** buscar `"1531651"` devuelve la compra; `"1531651,28"` y `"1034"`
  siguen funcionando (no-regresión); un importe inexistente devuelve 0 filas.

## Estado de los partes de la corrida anterior (lo que este lote cubría)

- **`LP-008`** (`minor`, XML-doc de `OrdenCompraItem.PrecioCompra` que decía "en pesos"): el commit
  lo declara corregido en su mensaje. **Verificado y CERRADO**: el XML-doc ya no afirma pesos y el
  campo efectivamente guarda el precio en la moneda del documento, con la conversión a pesos
  ocurriendo en la recepción vía `ConversionMoneda`.
- **`LP-009`** (`major`, período cerrado): **sigue CERRADO** en la superficie nueva — es el
  criterio 11, verificado en sus dos ramas sobre la confirmación del pago programado, que es una
  vía de escritura de caja que **no existía** cuando se cerró el defecto.

## Checklist de salida para merge

- [x] Build limpio (`dotnet build`, 0 errores; 8 warnings `NU1902` preexistentes de MailKit/MimeKit).
- [x] Migración `20261006011819` aplicada y **backfill verificado sobre filas preexistentes fabricadas**.
- [x] Los 5 números de plata reproducidos al centavo.
- [x] Máquina de estados de compra y de pago recorrida completa.
- [x] 11 entradas del catálogo cross-proyecto ejecutadas (no leídas).
- [x] Repo del sistema sin modificar (`git status --porcelain` limpio).
- [ ] **`LP-023` cerrado y re-verificado en contexto nuevo** ← bloqueante.
- [ ] `LP-022` cerrado (no bloqueante, puede ir en la próxima ola).
- [ ] Post-deploy en producción: `SELECT COUNT(*) FROM OrdenesCompra WHERE TotalEnPesos = 0 AND Total <> 0` tiene que dar **0**.

---
# Entrega 2 (fundación) — LOTE 1: ledger de caja + anulación de venta confirmada (QA, 2026-10-06, rama `entrega-1-migracion`)

## **NO-GO.** 8 criterios en PASS, 3 en FAIL. 1 defecto `critical` de dinero (`LP-018`) + 2 `major` (`LP-019`, `LP-020`) + 1 `minor` latente (`LP-021`).

Gate del commit `59dd715` "Fundacion del ledger de caja + anulacion de venta confirmada". Es el fundamento
de las otras 5 olas de la tanda, así que los 3 FAIL valen por el doble: `LP-018` toca el mecanismo —el
neto vivo— que las olas posteriores copiaron al ledger de proveedores y al de empleados.

## Entorno y metodología

- **Base aislada propia: `laplatense_qa_l1`**, clon de `laplatense_dev` por `mysqldump` (35 MB) tomado al
  arrancar el lote. **Nada se probó contra `laplatense_dev` ni contra producción.** El clon queda vivo: es
  el fixture de la re-verificación.
- App levantada desde `FerreteriaLaPlatense.Web` con `ASPNETCORE_ENVIRONMENT=Development` y
  `ConnectionStrings__DefaultConnection` apuntando al clon, en `https://localhost:7211` (puerto propio del
  lote, para no pisar a los otros 5 que corren en paralelo). Build limpio.
- **El MCP `playwright` no está en la sesión.** Se usó harness HTTP en Node con cookies de Identity reales
  y `__RequestVerificationToken` extraído del HTML de cada form. Alcanza para todo lo de este lote, que es
  lógica server-side y cifras renderizadas; se declara que **no hubo navegador real**, así que nada de
  interacción JS (el SweetAlert del botón Anular) está verificado por render.
- **El working tree está en `d08f8c4` (Entrega 4), 5 commits por delante del commit bajo prueba.** Se probó
  el sistema tal como se publicaría, no el commit aislado: los criterios son los de `59dd715` pero el
  veredicto incluye lo que las olas posteriores le hicieron a esa superficie. Se declara porque cambia la
  lectura de `LP-020`.
- Semilla propia en el rango de ids **9101–9161** (ventas) para no cruzarse con los otros lotes, más un
  segundo usuario `Vendedor` (`qa-vend2-l1`) clonando el `PasswordHash` del superusuario.
- Contención de entorno detectada y sorteada: otro lote **sobrescribió un archivo del scratchpad
  compartido** (`h.js`) a mitad de corrida. Todo lo de este lote pasó a vivir en `scratchpad/lote1/`.

## Cobertura por criterio (PASS / FAIL / BLOCKED)

| # | Criterio | Estado | Evidencia observada |
|---|----------|--------|---------------------|
| 1 | Devuelve el stock en la unidad correcta, con cantidades decimales | **PASS** | Producto 3597 (`UnidadVenta=Peso`, decimal(18,3)). Confirmar 6 ventas: `Stock` 100.000 → 92.625 (−7.375 exacto). Anular venta 9101 (2.750) y 9106 (0.125): 94.125 → 97.000. Sin redondeo en ningún paso. Detecta y avisa el cambio de unidad posterior (`ItemsVenta.UnidadVenta=3` vs `Productos.UnidadVenta=2`) sin bloquear |
| 2 | Revierte caja por el **neto posteado**, no por el total de la venta | **PASS** | Venta 9101: `Total` $332,75, pagos Efectivo $82,75 + CuentaCorriente $250,00. La reversión de caja fue **$82,75**, no $332,75 (mov. id 64, `Egreso`, `EsReversion=1`, `PagoVentaId=12`). Mensaje: "se revirtieron $ 82,75 en caja" |
| 3 | Revierte el débito en la CC del cliente | **PASS** | Venta 9101: `MovimientosCCCliente` id 12 (`Debito`, `Origen=VentaFiado`, $250,00) → id 13 (`Credito`, `Origen=AnulacionVenta`, $250,00, `VentaId=9101`). Ledger inmutable: contramovimiento nuevo, no edición |
| 4 | Queda `Anulada` con motivo y fecha, y **deja de contarse** en Dashboard, ABC y arqueos | **FAIL** | Estado/motivo/fecha/usuario ✓ (`Estado=3`, `MotivoAnulacion`, `FechaAnulacion` proyectada a ART: UTC 06:25 → "06/10/2026 03:25"). Dashboard ✓: "Ventas de hoy 2 — $ 242,00" = oráculo SQL de `Estado IN (2,4)`; las 7 anuladas ($6.579,38) quedan afuera. ABC ✓: 3597 clase **C** con 9.375 unidades vendidas en ventas anuladas (oráculo: solo 2.000 confirmadas cuentan); "Top productos del mes" muestra 2, no 9. **Arqueos ✗:** ver `LP-020` |
| 5 | No se puede anular dos veces | **FAIL** | Secuencial ✓: 2.º intento → "Esta venta ya está anulada". Con el estado forzado a `Confirmada` por SQL (venta 9102, ya revertida) el neto vivo protege la caja ✓ (0 movimientos nuevos) pero **el stock se devolvió otra vez** (94.125 → 95.625). Y en **paralelo** el neto no protege nada: ver `LP-018` |
| 6 | No se puede anular una venta con Entrega asociada | **PASS** | Venta 9103 `Confirmada` + `Entregas` id 4: "Esta venta tiene una entrega a domicilio asociada: hay que resolver o dar de baja la entrega antes de anular la venta". `Estado` sigue en 4, 0 reversiones posteadas |
| 7 | Un `Vendedor` anula la suya y **no la de otro** | **PASS** | `vendedor2.qa` POST sobre la venta 9104 (de `vendedor.qa`), id manipulado: "Solo un administrador o el vendedor que registró la venta pueden anularla". `vendedor.qa` sobre su propia 9106: OK. **Repartidor por POST directo con token antiforgery propio robado de `/Entregas`**: 302 → `/Account/AccessDenied?ReturnUrl=%2FVentas%2FAnular` (lo corta la policy `RequireVentas`, server-side) |
| 8 | Día o mes de la venta cerrado ⇒ rechazo (`LP-009`) | **PASS** | 4 ramas, las 4 rechazadas y con `Estado` intacto: mes cerrado con cierre diario (21/08) y sin él (25/08) → "La caja del mes 08/2026 ya tiene cierre mensual…"; **día** cerrado con mes abierto (15/09, cierre sembrado) → "La caja del día 15/09/2026 ya está cerrada…"; **hoy** cerrado con el día de la venta abierto → "La caja del día 06/10/2026 ya está cerrada: no se puede registrar hoy la reversión de esa venta". Cierres sembrados borrados al cerrar |
| 9 | Un gasto anulado ya no se confunde con un ingreso real | **PASS** | Backfill: gastos 1 y 2 con neto vivo $0,00 y **$0,00 de `Ingreso` no-reversión** sobre `OrigenTipo='Gasto'`. Camino vivo: gasto 4 (Transferencia $7.777,77) → reversión `EsReversion=1`, `MedioPago=4`, neto $0,00. Con `Anulado` forzado a 0, el 2.º intento **no postea nada**: "No había ningún egreso vivo en la caja para revertir" — el neto protege sin depender del flag |
| 10 | El desglose del arqueo suma exactamente el total del arqueo | **FAIL** | Período **abierto** ✓ al centavo: KPI "Ingresos de hoy $ 9.230,15 / Egresos $ 25.027,69" = pie del desglose = oráculo SQL, día y mes. Período **cerrado ✗**: ver `LP-019` |
| 11 | El backfill resolvió `MedioPago` y `PagoVentaId` a todas las filas de venta preexistentes | **PASS** | 23 filas `OrigenTipo='Venta'`: **0 sin `MedioPago`, 0 originales sin `PagoVentaId`, 0 sin `UsuarioId`**. Las 3 preexistentes (ids 6, 7, 8, del 03/09) resolvieron al pago exacto: 6→7 (venta 12, Efectivo, $200), 7→8 (venta 12, CreditoCuotas, $300), 8→**10** (venta 13, que tiene dos pagos Efectivo del **mismo importe** $5.163,80 — el `DeletedAt IS NULL` del subquery deja `n=1` y elige el vivo, no el borrado). 0 grupos `(venta, medio)` con `n>1` → nada quedó ambiguo |

## Máquina de estados de Venta

`Borrador → Confirmada → Anulada` ejercitada de punta a punta. Transiciones **rechazadas** y verificadas por
ejecución, cada una con su mensaje propio y sin efecto colateral:

| Desde | Intento | Resultado observado |
|-------|---------|---------------------|
| `Anulada` | → `Anulada` | "Esta venta ya está anulada." |
| `Borrador` (vivo, 9110) | → `Anulada` | "Esta venta todavía está en borrador: no movió stock ni caja… Usá \"Cancelar\" para descartar el borrador." |
| `Facturada` (venta 1) | → `Anulada` | "La venta #1 tiene comprobante AFIP emitido (número 1): anularla requiere emitir una nota de crédito electrónica, que todavía no está implementada." |
| inexistente / soft-deleted | → `Anulada` | "Venta no encontrada." |
| motivo `""` y `"    "` | → `Anulada` | "El motivo de la anulación es obligatorio." (server-side, no solo el `inputValidator` del SweetAlert) |

`EstadoVenta.Anulada` propagado al combo `fEstado` del listado de Ventas, y `OrigenMovimientoCC.AnulacionVenta`
al combo Origen de la CC del cliente ("Anulación de venta") — **LP-002 cumplido**.

## Defectos nuevos de este lote

### `LP-018` — `critical` — dos `Anular` en paralelo revierten el mismo dinero dos veces

El parte completo está en `docs/qa/regresiones-manuales.yml`. Lo esencial: `AnularAsync` lee el neto vivo y
`venta.Estado` **antes** de `BeginTransactionAsync` (decisión explícita y documentada en el propio método,
para poder bloquear entero si algún pago no es identificable). Sin lock de fila, sin `RowVersion` en `Venta` y
sin índice único sobre `(PagoVentaId, EsReversion)`, dos requests concurrentes ven los dos `Confirmada` y los
dos el mismo neto, y cada uno postea su reversión.

**Reproducción (venta 9130, 3 POST paralelos con sockets separados):** un solo `Ingreso` de $605,00 quedó con
**dos** reversiones —`CajaMovimientos` ids 69 y 70, `Egreso` $605,00 cada una, `EsReversion=1`, el **mismo**
`PagoVentaId=22`— y el neto vivo de ese pago en **−$605,00**. La caja egresó $1.210,00 por una venta que
ingresó $605,00, y la venta quedó `Anulada`, así que nada avisa.

**Es intermitente:** la segunda tanda (venta 9131, 4 POST) hizo rollback de las sobrantes (hueco de
`AUTO_INCREMENT` 72–73) y quedó una sola reversión. Una corrida verde no prueba nada: la re-verificación
necesita la tanda repetida ≥3 veces.

Lo que cae con esto es la afirmación central del commit —"revertir dos veces es imposible por construcción"—
que vale **solo en secuencia**: el neto vivo es una lectura, no un candado. Y el mecanismo se copió después al
ledger de proveedores y al de empleados, así que el parte pide barrer los tres.

Nota al margen del mismo defecto: con el estado forzado (criterio 5) el neto protege caja y CC, pero
**el stock no tiene equivalente del neto** — su única defensa es el `if (Estado == Anulada)`, que es
exactamente el tipo de guarda que el commit dice estar reemplazando.

### `LP-019` — `major` — el desglose del arqueo es vivo y el total es el congelado

En `/Caja/Mensual?anio=2026&mes=8` (mes con cierre firmado y desfasado), **en una sola pantalla**: KPI
"Egresos del mes **$ 91.500,50**" (el valor congelado en `CierresCajaMensuales`) y pie del desglose
"Total … **$ 94.001,25**" (recálculo vivo). **$ 2.500,75** de diferencia, sin ninguna leyenda que lo explique,
en un cuadro que se titula "Para conciliar contra el extracto de cada cuenta".

`ObtenerResumenMesAsync` devuelve `cierre?.TotalEgresos ?? egresos` pero llena `TotalesPorMedio` con
`ObtenerTotalesPorMedioRangoUtcAsync`, que siempre consulta el ledger vivo. Las dos consultas están
correctamente alineadas en lo que **excluyen** (apertura / `SaldoInicialCaja`, verificado: coinciden al centavo
en período abierto) y el XML-doc razona sobre esa alineación — pero la alineación es del **filtro**, no de la
**fuente**. En período abierto coinciden y el defecto es invisible; aparece justo cuando el operador va a
conciliar un mes cerrado. Emparenta con `LP-013`, que ya pedía la detección del desfasaje; esto le da la
superficie concreta donde ponerla.

### `LP-020` — `major` — ningún lector de totales usa `EsReversion`, y la pantalla afirma lo contrario

Medido en `/Caja` antes y después de anular una venta de $4.840,00: "Ingresos de hoy" **no baja** (queda en
$14.071,15) y "Egresos de hoy" **sube** $4.840,00. Sobre el día completo: ingresos **brutos $14.082,26** contra
ingresos **netos −$229,89**. Igual en la tarjeta "Caja de hoy" del `/Dashboard`.

Y `/Ventas/Details` de la venta anulada dice, textual: *"Esta venta ya no se cuenta en el dashboard, en la
clasificación ABC ni en los arqueos."* Las dos primeras son verdad y están verificadas arriba. **La tercera es
falsa**, y es la afirmación más fuerte que el sistema le hace al operador sobre un comportamiento que no existe.

**Clasificación pedida en el brief:** es un **defecto de este commit**, no una promesa para más adelante. Tres
razones: el criterio 4 lo exige explícitamente; el XML-doc de `EsReversion` de este commit promete que con la
columna el arqueo puede separar "plata que entró" de "plata que nunca salió"; y la vista de este commit lo
afirma como hecho consumado. La Entrega 4 ya lo diagnosticó en el XML-doc del helper ("una promesa vencida de
la ola 1") y expuso el neto solo en la pantalla consolidada del módulo 13, sin tocar el arqueo ni el texto. Lo
barato y urgente es el texto de la vista; el neto en el arqueo puede ir después.

### `LP-021` — `minor` (latente) — el neto vivo no está acotado cuando `OrigenId = 0`

Segunda familia que el brief pidió buscar. `ObtenerNetoPosteadoAsync` acota por `OrigenTipo + OrigenId`, pero
los orígenes manuales se persisten con `OrigenId = 0`: reproduciendo en SQL la agregación exacta para
`('Ajuste', 0, Ingreso)` devuelve **$262,86, que es la mezcla de 3 ajustes independientes**. Hoy **no hay
ningún caller** con `OrigenId=0` (verificado por grep), así que es latente — pero el contrato público del
método habla de "un origen del ledger" sin ninguna salvedad, y el día que aparezca "revertir un movimiento
manual" la reversión sale por el neto de todos los ajustes juntos.

### Observaciones menores, sin id propio

- `usuarioNombre` llega como `null` (no ausente) en el JSON de `/Caja/ConsolidadoListar` para las 5 filas de
  `Gasto` y 2 de `Ajuste` sin `UsuarioId`, y la columna declara `defaultContent: '—'`, que en DataTables solo
  aplica a `undefined`. Es el **lector a medio hacer que el brief sospechaba** por el `UsuarioId` de solo
  escritura, pero es cosmético y pertenece al reader de la ola 4, no a este commit. **Render no confirmado**
  (sin navegador): queda como observación, no como FAIL.
- Un valor basura en el filtro `medioPago` (`?medioPago=NoExiste`) cae en silencio a "todos" (34 de 34 filas)
  en vez de fallar ruidoso. Misma familia que `LP-007`, severidad despreciable.

## La primera familia del neto vivo (filtrado por tipo de movimiento): **no está presente**

El brief pedía buscar las dos familias que el neto vivo ya tuvo en el ledger de proveedores. La primera
—filtrar por tipo de movimiento y no contar la reversión del tipo opuesto, que devolvía 160.000 donde el real
era 60.000— **no aparece acá**: `NetoVivo` materializa las filas y resta en memoria
`Σ(tipoOriginal, !EsReversion) − Σ(tipoOpuesto, EsReversion)`, con el tipo opuesto derivado del original en un
solo lugar compartido por las dos sobrecargas públicas. Verificado por ejecución en los dos sentidos:
`Egreso→Ingreso` (gasto 4, neto $0,00 tras revertir) e `Ingreso→Egreso` (ventas 9101/9102/9106, neto $0,00).

## Verificación de `MH-001` por ejecución

**34 llamadas** a `/Caja/Listar` y `/Caja/ConsolidadoListar`, todas **200 con JSON válido**, ninguna excepción
del provider. Se ejercitó específicamente la superficie nueva del commit: filtro por los 7 medios, el
centinela `SinDeclarar` (`MedioPago IS NULL`), el orden por la columna `Medio`, la búsqueda global por
**etiqueta** ("tarjeta" → 1 fila `CreditoCuotas`; "sin declarar" → 1; "efectivo" → 28), el badge
"Reversión" (12 filas, = mis reversiones), el término que no matchea nada (0 filas, el caso que hacía
reventar el `IN` vacío) y combinaciones medio + tipo + búsqueda.

La estrategia del commit evita el `IN` por construcción: recorre `Enum.GetValues<MedioPagoCaja>()` y hace una
consulta por medio con el valor como **parámetro escalar**. Acento e insensibilidad de caso verificados con una
fila `Depósito` sembrada: "deposito", "depósito", "DEPOSITO" y "Depos" → 1 fila cada uno.
`ResolverNombresAsync` materializa `AspNetUsers` y filtra en memoria (la colección de strings nunca llega al
`IN`), y `ventaIds.Contains(i.VentaId)` del Dashboard es `List<int>` materializada con guarda de lista vacía —
los dos criterios que el proyecto ya tenía documentados, y los dos ejecutados de verdad.

## Día de negocio / huso (el servidor de producción está en Pacífico)

- **Ninguna línea agregada por el commit usa `DateTime.Today`, `DateTime.Now`, `DateTime.UtcNow.Date` ni
  `ToLocalTime()`.** Barrido global: las 10 apariciones restantes en la solución son **comentarios** que
  advierten contra su uso.
- Frontera forzada con datos (no tocando el reloj): venta 9160 con `Fecha = 2026-09-11 01:44 UTC` = **22:44 ART
  del 10/09**, y su par simétrico 9161 a las 00:00 ART del 10/09. Las dos se muestran como **10/09/2026** en la
  grilla de Ventas y en el detalle, y sus dos movimientos de caja caen en el **mismo** arqueo del 10/09 ART
  (oráculo SQL: 2 movimientos, $242,00). **`LP-010` no regresionó.**
- `FechaAnulacion` se proyecta a ART en el detalle (UTC 06:25 → "06/10/2026 03:25"), igual que `Fecha`.
- Camino de **escritura** verificado: `Venta.Fecha` no se corrió ni un segundo tras confirmar y anular
  repetidamente (9101, 9150, 9160 comparados en la base antes y después).

## Regresiones de lo que ya pasaba (`LP-009` a `LP-013`)

| Item | Estado | Evidencia |
|------|--------|-----------|
| `LP-009` (guarda de período consulta día **y** mes) | **sin regresión** | Movimiento manual a `2026-08-24` (mes cerrado, día sin cierre) y a `2026-08-21` (día y mes cerrados): los dos **rechazados**, 0 filas en la base. El de control (hoy) se persistió. Las 4 ramas de la guarda en `AnularAsync` también rechazan (criterio 8) |
| `LP-010` (`Venta.Fecha` alineada al día de negocio) | **sin regresión** | Ver la sección de huso: el par 22:44 / 00:00 ART del mismo día de negocio coincide entre Ventas y Caja |
| `LP-011` (mes fuera de rango → 500) | **sin regresión** | `mes=13`, `mes=0`, `mes=-1`, `anio=0`, `anio=99999`: los 5 → **302** a `/Caja/Mensual`, ningún 500 ni página de error |
| `LP-012` (los listados de cierres ignoran `search[value]`) | **sin regresión** | `/Caja/CierresListar` y `/Caja/MensualListar`: `"QA Super"` → 1 fila, `"zzz-no-existe"` → **0 filtradas**. El servidor respeta el término |
| `LP-013` (no hay camino para corregir un cierre desfasado) | **sigue abierto, y ahora es visible** | El desfasaje de $2.500,75 de agosto sigue sin detección ni remedio. `LP-019` es su manifestación nueva: ahora la pantalla muestra los dos números juntos y sigue sin decir que difieren |

## Cobertura del catálogo cross-proyecto

Seleccionados por índice (`docs/qa/cat_resumen.txt`) los items cuyo módulo mapea a esta superficie; solo de
esos se leyó el cuerpo completo en `regresiones-manuales.yml`.

| Item | Severidad | Resultado |
|------|-----------|-----------|
| `MH-001` / `MH-050` (colección local al `IN` de SQL) | major | **PASS por ejecución** — 34 llamadas, 200 todas. Ver la sección propia |
| `MH-020` (reversión por el total nominal en vez de lo cobrado) | critical | **PASS** — criterio 2: $82,75 revertidos sobre una venta de $332,75 |
| `MH-027` (clave no única al documento hijo ⇒ contramovimiento por el importe equivocado) | critical | **PASS, el caso difícil** — venta 9102 con **dos pagos Efectivo de $90,75 idénticos**: dos reversiones, cada una contra su propio `PagoVentaId` (14 y 15), sin adivinar por monto. Y el backfill eligió el pago vivo (10) y no el borrado (9) en la venta 13, que también tiene dos pagos del mismo importe |
| `MH-034` (ledger único inconciliable) | medium | **PASS con reserva** — el desglose por medio existe, filtra y cuadra al centavo en período abierto; falla en período cerrado (`LP-019`) |
| `LP-002` (propagar un valor de enum nuevo a **todos** los lectores) | — | **PASS** — combo Origen de Caja con los 8 orígenes, combo Medio con los 7 valores + `SinDeclarar`, `fEstado` de Ventas con `Anulada`, combo Origen de la CC con "Anulación de venta" |
| `LP-007` (valor desconocido debe fallar ruidoso) | minor | **PASS con observación** — `continuar` desconocido sigue avisando; el filtro `medioPago` basura cae en silencio a "todos" |
| `LP-009`, `LP-010`, `LP-011`, `LP-012`, `LP-013` | major/minor | Ver la tabla de regresiones |

**No aplicados en este lote** (módulo ajeno al alcance, para el lote que corresponda): los `CRM-0xx`, los
`KOI-Bxx`, los `OLV-0xx` y los `MH-0xx` de Compras/Proveedores/Empleados.

## Reglas nuevas o modificadas desde la última corrida

`6-qa.md` declaraba "Ultima validacion de reglas cross-proyecto: 2026-10-05". Diferencial contra el estado
vigente: `git log --since=2026-10-05` sobre
`.github/instructions/32-estandares-qa-implementador.instructions.md` y `docs/qa/regresiones-manuales.yml`
devuelve **solo** el commit de cierre del Sprint 0 del propio 2026-10-05 (`20e9734`) y un fix del parser de
catálogos de `contexto.py` (`d0f62df`), que no cambia ninguna regla. **No hay regla agregada ni modificada
después de esa fecha**, así que no hubo reglas nuevas que ejecutar contra el sistema fuera del catálogo ya
validado. Dato para los lotes siguientes de esta tanda: no necesitan repetir este diferencial.

## Riesgos de liberación

1. **`LP-018` bloquea la publicación.** Es dinero revertido dos veces, el síntoma es silencioso (la venta
   queda `Anulada` y el mensaje es de éxito) y el único rastro es un neto negativo que nadie mira. Y el patrón
   del neto vivo ya se copió al ledger de proveedores y al de empleados en las olas posteriores: **el barrido
   tiene que cubrir los tres**, no solo caja.
2. **El backfill de `PagoVentaId` contra producción sigue sin verificar, y es la decisión de publicar.** En
   `laplatense_qa_l1` resolvió el 100% (0 filas sin `MedioPago`, 0 sin `PagoVentaId`, 0 ambiguas), pero la
   forma de los datos de producción es otra. Producción está 6 migraciones atrás y **no se la tocó**. Las tres
   queries de riesgo, de solo lectura, quedan en `deteccion_qa` de `LP-018`/`LP-021` y en el parte; la que
   decide es la primera: los movimientos de venta cuya `Descripcion` **no** matchea
   `'%(Efectivo)%' / '%(Debito)%' / '%(CreditoCuotas)%'` se quedan sin `MedioPago`, y el paso 4 del backfill
   exige `MedioPago IS NOT NULL`, así que también sin `PagoVentaId` → **esas ventas quedan bloqueadas para
   anular**. Si devuelve 0 filas y no hay grupos `(venta, medio)` con `n>1`, las 3 ventas confirmadas reales
   quedan anulables.
3. **`LP-020` es barato por la mitad.** Corregir el texto de `Details.cshtml` es una línea y saca la
   afirmación falsa de la pantalla. El neto en el arqueo puede esperar, el texto no.
4. El stock no tiene equivalente del neto vivo (ver `LP-018`): cualquier camino futuro que llegue a
   `AnularAsync` sin pasar por el `if` de estado devuelve stock de nuevo.
5. `LP-013` sigue abierto y el desfasaje de $2.500,75 de agosto está vivo en `laplatense_dev`.

## Estado go/no-go

**NO-GO.** No por la cantidad de hallazgos —8 de 11 criterios pasan con evidencia fuerte y las dos familias de
bugs que el brief mandó cazar están una ausente y la otra latente— sino porque `LP-018` es pérdida de dinero
silenciosa en el mecanismo que las otras 5 olas de la tanda dan por sólido, y porque la pantalla le afirma al
operador algo que no es cierto (`LP-020`).

Ciclo de cierre: **ningún defecto se cierra en esta corrida.** Los 4 criterios de re-verificación están en
`criterio_aceptacion` de cada item; los 3 que vuelven a FAIL son el 4, el 5 y el 10.

## Checklist de merge

- [ ] `LP-018` corregido con lock de fila o `UPDATE` condicional por estado **dentro** de la transacción, y el
      mismo barrido aplicado a `GastoService.AnularAsync`, al ledger de proveedores y al de empleados.
- [ ] Re-verificación de `LP-018` con la tanda de ≥4 POST paralelos **repetida 3 veces** (es intermitente).
- [ ] Query de neto negativo (`HAVING neto < 0`) en 0 filas sobre todo el ledger.
- [ ] Texto de `Views/Ventas/Details.cshtml` corregido (`LP-020`, parte barata).
- [ ] Las 3 queries de riesgo del backfill corridas **contra producción en solo lectura** y su resultado
      pegado en el parte, antes de aplicar la migración.
- [ ] `LP-019` resuelto o declarado con su leyenda en pantalla.
- [ ] Criterios 4, 5 y 10 re-verificados en contexto nuevo, arrancando desde FAIL.

## Estado de la base tras el lote

`laplatense_qa_l1` **queda viva y sucia a propósito**: es el fixture de la re-verificación. Contiene las
ventas 9101–9161 (7 anuladas, 2 confirmadas, 1 borrador), los gastos 4–6, el usuario `qa-vend2-l1`, la entrega
id 4, una fila `Depósito` de prueba y el movimiento de control de `LP-009` de hoy. Lo sembrado y luego
**borrado**: los cierres diarios de `2026-09-15` y `2026-10-06`. `laplatense_dev` quedó **intacta**
(nunca se le apuntó la app) y **producción no se tocó**.

El repo del sistema (`C:/Sistemas/Ferreteria La Platense`) quedó **sin modificaciones**: `git status --porcelain`
solo muestra `?? .claude/`, que es anterior al lote.

---

## Historial de ajustes

### Bloques archivados (2026-10-06)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-10** — 6 bloques (2026-10-05 a 2026-10-06) → [`6-qa-2026-10.md`](historial/6-qa-2026-10.md)
- **2026-08** — 2 bloques (2026-08-21 a 2026-08-24) → [`6-qa-2026-08-2.md`](historial/6-qa-2026-08-2.md)
