# Historial archivado - QA La Platense

Bloques movidos de `6-qa.md` el **2026-10-07** para mantener el archivo bajo el techo de 150 KB
(`39-presupuesto-contexto`). Son dos corridas CERRADAS del 2026-10-06: el gate de publicacion del
hotfix de transacciones (**GO**) y el LOTE 5 de la Entrega 6, presupuestos en PDF y aumento masivo
de precios (**NO-GO**, con `LP-029` y `LP-030` emitidos). Se archivan por antiguedad, no porque
hayan perdido vigencia: los defectos que abrieron viven en `docs/qa/regresiones-manuales.yml`.

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
