# Memoria - Implementador - BLOQUE ARCHIVADO

## Proyecto: La Platense

Archivado el 2026-10-06 desde `5-implementador.md` para mantener ese archivo bajo el techo de
150 KB (`39-presupuesto-contexto.instructions.md`). Describe el **hotfix sobre la rama publicada
`hotfix-transacciones-ventas`** (creada desde `2580f7c`, que es el estado de produccion).

Se lee solo si el trabajo toca esa rama o un deploy a produccion. Para la rama de desarrollo
(`entrega-1-migracion`) lo vigente son las dos secciones que lo suceden en el archivo principal:
la reconciliacion de la familia LP-018 / LP-034 y la verificacion por ejecucion de los 6 sitios
restantes.

---

## Hotfix de transacciones de ventas — rama `hotfix-transacciones-ventas` (2026-10-06)

**Esto no es una ola de desarrollo.** Es un hotfix sobre el estado exacto de producción, en una rama
propia creada **desde el commit `2580f7c`** — lo que está publicado hoy en
`ferreterialaplatense.com.ar` — y **no** desde `entrega-1-migracion`, que tiene 7 commits de
desarrollo encima que no se pueden publicar. El deploy lo ejecuta Joaquín después de que QA
re-verifique; esta ronda **no tocó producción** (ni Web Deploy ni `mysql8001.site4now.net`).

### Por qué existió

El código publicado tenía **cero** `BeginTransaction` en `VentaWorkflowService` (verificado:
`git show 2580f7c:...VentaWorkflowService.cs | grep -c BeginTransaction` → `0`). `ConfirmarAsync`
descontaba stock, posteaba el movimiento de caja y debitaba la cuenta corriente del cliente con
escrituras separadas, decidiendo sobre una lectura sin lock. `FacturarAsync` tenía la misma forma y
podía emitir **dos CAE de AFIP por la misma venta** — hoy inalcanzable porque la facturación está
deshabilitada por falta de certificado, pero un comprobante fiscal duplicado no se corrige: se anula
con nota de crédito, que todavía no existe.

Producción no tiene daño hecho (se borraron los datos de prueba y quedó en cero transacciones). El
riesgo se materializaba en la **primera venta real del cliente**.

### Reutilización: paso 1 del escaneo, hit directo

`docs/patrones/cat_resumen.txt` → **`PAT-059`** ("Idempotencia por lectura previa: el patrón que solo
es seguro en secuencia (lock de fila del documento dueño)"), catalogado en esta misma ronda de
`bdfd99b`. El mecanismo se **portó del commit `bdfd99b`** de `entrega-1-migracion`, que es el mismo
repo: `FerreteriaLaPlatense.Infrastructure/Data/BloqueoDeFila.cs`, autocontenido y sin dependencias
de las olas de desarrollo. **No se agregó entrada nueva al catálogo** — `PAT-059` ya documenta el
patrón completo y este hotfix es su segundo consumidor, en la rama de producción.

**Lo que se adaptó y por qué** (no fue copiar y pegar): el `BloqueoDeFila` de `bdfd99b` declara 7
constantes de tabla, y en producción **solo existen 3** (`Ventas`, `Gastos`, `Productos`);
`Presupuestos`, `OrdenesCompra`, `PagosOrdenCompra` y `MovimientosCCEmpleado` **no existen**. Se
dejaron las **dos** que este hotfix bloquea. Y el XML-doc de la clase se reescribió: el original
fundamenta la decisión contra el índice único hablando de las **reversiones parciales de
`AnularAsync`**, método que **no existe en producción** (llegó en `59dd715`, posterior). Copiar ese
texto habría plantado un comentario prescriptivo que describe código ausente — exactamente el
defecto `LP-008` que el barrido `LP-002` existe para cortar.

### Alcance: estrictamente dos métodos

`ConfirmarAsync` y `FacturarAsync`. **No** entró el resto de la familia `LP-018` (`AnularAsync`,
pagos a proveedor, CC de empleados, recepción de compra, conversión de presupuesto, aviso de pagos
programados): no existe en producción o pertenece a código no publicado. **No** entró `LP-024` (lost
update del stock del ajuste manual): es real, pero su exposición es mucho menor y mezclarlo agranda
la superficie de un hotfix que tiene que ser auditable de un vistazo.

### Cambios por capa

| Capa | Archivo | Motivo |
|---|---|---|
| Infrastructure / Data | `BloqueoDeFila.cs` (**nuevo**, 2 constantes) | `SELECT ... FOR UPDATE` por Id, deduplicado y ordenado por Id asc (prevención de deadlock encapsulada); tira `InvalidOperationException` si se lo llama fuera de transacción, porque ahí el lock se libera solo y la garantía sería fantasma. |
| Infrastructure / Services | `VentaWorkflowService.ConfirmarAsync` | Transacción abierta **antes de LEER**; lock de la venta y de los productos de esa venta; relectura bajo lock de `Estado` y de cada `Producto.Stock`; `CommitAsync` tras el `SaveChanges` que ya existía. |
| Infrastructure / Services | `VentaWorkflowService.FacturarAsync` | Lo mismo con el lock de la venta, **sostenido durante la llamada a AFIP** a propósito, con el costo declarado en el comentario. |

**Migraciones EF: ninguna.** El hotfix no toca el modelo. Es lo que lo hace deployable sobre la base
de producción tal como está.

**Diff: 3 archivos, +93 líneas, 0 borradas.** Puramente aditivo; de esas líneas **20 son código** y
el resto fundamento. Ningún Controller, ninguna vista, ningún contrato de interfaz.

### Las DOS premisas del brief que se refutaron ejecutando (pasada 0 del barrido `LP-002`)

Las dos venían del brief con toda la razón aparente, y las dos son **falsas**. Importa porque las dos
habrían quedado escritas como comentario prescriptivo en el código publicado.

1. **"Una falla en el medio deja la venta a mitad: stock descontado sin plata registrada."** Falso.
   El método tenía **un solo `SaveChangesAsync` al final** (ni `RegistrarMovimientoAsync` de caja ni
   el de CC persisten por su cuenta) y **EF envuelve cada `SaveChanges` en una transacción
   implícita**. Verificado abortando el `INSERT` de caja con un trigger `SIGNAL SQLSTATE '45000'`:
   **el criterio 2 pasa también contra el código roto** — venta en `Borrador`, stock intacto, 0
   movimientos. El método era **atómico por accidente**. La transacción explícita lo vuelve atómico
   por construcción y, sobre todo, es lo único que habilita el lock.
2. **"Dos requests concurrentes duplican las tres cosas, incluido el descuento de stock."** Las dos
   de plata sí, deterministas. El stock **no se duplicaba: se perdía.** Los dos competidores leían
   `Stock = 100`, los dos escribían `98`, y el resultado coincidía con el correcto **por
   casualidad** (lost update que se tapa solo). Medido en 3 corridas contra el código roto: siempre
   `98`. Con otro entrelazado daría `96`. No es una garantía, es el resultado de una carrera — y el
   lock sobre los productos lo cierra igual.

**Las dos quedaron escritas en el código**, en el comentario de `ConfirmarAsync`, como "lo que **no**
estaba roto", para que la próxima ronda no venga a "arreglar" una atomicidad que ya existía ni a
buscar una duplicación de stock que nunca se vio.

### Evidencia ejecutada

Build de la solución: **0 errores**, 9 advertencias **todas preexistentes** (`NU1902` de
MailKit/MimeKit y el `CS0114` de `HomeController`). Sin advertencias nuevas.

**Arnés de concurrencia: `tools/ArnesHotfixTransacciones`** (proyecto propio, **fuera** de
`FerreteriaLaPlatense.slnx`, así que no entra al build de la solución ni se publica). Queda en el
commit, es idempotente (prefijo `ZZHOTFIX`, `LimpiarAsync` al principio y al final) y **QA lo puede
re-correr**. Corre contra `laplatense_hotfix_tx`, un clon con las **8 migraciones exactas de
`2580f7c`**, y tiene una **guarda que aborta** si la cadena de conexión menciona `laplatense_dev`,
`laplatense_qa` o `site4now` — atiende la observación que QA levantó del arnés de la ronda anterior,
que apuntaba a `laplatense_dev` hardcodeado y escribía la base compartida.

**Método**: un scope de DI por competidor (un `AppDbContext` y una **conexión MySQL** propia), la
conexión **abierta antes** de la barrera para que el handshake no se cuele en la ventana medida, y
`Barrier.SignalAndWait()` para largarlos juntos. Con un cliente HTTP compartido las requests se
serializan y el test da **falso verde**.

**46 afirmaciones, 46 OK**, corrido 3 veces. Escenario: 2 unidades × $1.000 + IVA 21% = Total
**$2.420**; pagos Efectivo **$1.420** (va a caja) + Cuenta Corriente **$1.000** (va al ledger);
stock 100 → 98. Números elegidos para que ningún importe duplicado coincida con otro valor legítimo.

| Criterio | Resultado |
|---|---|
| 1 — N simultáneos, un solo cierre (**N=3 y N=8**) | 1 éxito de N, **1** ingreso de caja ($1.420), **1** débito de CC ($1.000), **1** descuento de stock (98), 0 excepciones, los N−1 restantes con rechazo explícito |
| 2 — falla de caja/CC, nada persistido | venta en `Borrador`, 0 caja, 0 CC, stock 100 intacto; y el **reintento posterior confirma bien** y deja un solo cierre |
| 3 — secuencial sin regresión | total $2.420, caja $1.420, CC $1.000, stock 98, estado `Confirmada` |
| 4 — confirmar una ya confirmada | rechazo explícito y **no escribe nada** |
| 5 — `FacturarAsync` (**N=3 y N=8**) | 1 éxito de N y **AFIP invocado UNA sola vez**; un solo CAE persistido; caja/CC/stock sin retocar |

**La verificación que vale más que las 46**: el arnés se corrió **contra el código roto** (revirtiendo
el service a `2580f7c` y dejando el arnés igual) y dio **12 fallas / 34 OK**, reproduciendo el
defecto con números: con N=8, **2 éxitos**, **2** movimientos de caja por **$2.840** y **2** débitos
de CC por **$2.000**; y `FacturarAsync` con N=8 **emitió 8 comprobantes AFIP** (8 de 8 éxitos, 8
invocaciones). Un arnés verde que no se probó contra el defecto no prueba nada: podría estar verde
porque no mide.

### Pendiente declarado en el código, no resuelto: comprobante AFIP huérfano

Si el proceso muere **entre la respuesta de AFIP y el commit**, el CAE existe en AFIP y no en el
sistema: la venta queda `Confirmada` y reintentar emitiría un **segundo** comprobante del mismo hecho
económico. **No es concurrencia** — el lock no lo cubre y no puede cubrirlo — es una falla parcial
contra un tercero. Lo que falta: un estado intermedio **persistido** antes de llamar ("facturación en
curso": columna nueva + valor de enum + migración) y que el reintento consulte a AFIP
(`CompConsultar`) en vez de emitir a ciegas. **Fuera de alcance acá y con fundamento**: AFIP está
deshabilitado, así que el camino no se puede ejecutar en producción, y un estado nuevo con migración
no entra en un hotfix. Queda escrito en el XML-doc de `FacturarAsync` con la frase **"el día que se
cargue el certificado esto hay que resolverlo ANTES de habilitar la facturación"**, para que no se
descubra de nuevo.

### Guía de pasos para verificación manual (el Implementador no corre smoke por navegador)

1. Cargar una venta en `Borrador` con al menos un ítem y un pago en efectivo, y confirmarla.
   Controlar que el ingreso de caja, el total y el stock sean **los mismos** que antes del hotfix.
2. Confirmar una venta que ya está `Confirmada`: tiene que dar rechazo explícito y **no** mover nada.
3. El caso que motiva el hotfix: **doble click real** en Confirmar (o `Confirmar y facturar`) sobre
   la misma venta. Tiene que quedar **un** ingreso de caja, **un** débito de CC y **un** descuento de
   stock. Antes del hotfix quedaban dos.
4. Una venta con pago a cuenta corriente: el débito tiene que aparecer **una** vez en el ledger del
   cliente y **no** como ingreso de caja.
5. Arqueo de caja del día: el total no puede tener movimientos repetidos del mismo `OrigenId`.
6. Re-correr el arnés si se quiere la medición de concurrencia:
   `dotnet run --project tools/ArnesHotfixTransacciones` contra un clon propio (**nunca** contra
   `laplatense_dev`; el arnés aborta solo si se lo intenta).

### Checklist de salida para merge

- [x] Rama `hotfix-transacciones-ventas` creada **desde `2580f7c`**, no desde `entrega-1-migracion`.
- [x] Alcance estricto: `ConfirmarAsync` y `FacturarAsync`. Nada más tocado.
- [x] Lógica en Services; cero cambios en Controllers, vistas e interfaces.
- [x] **Sin migración EF**: deployable sobre la base de producción tal como está.
- [x] Diff aditivo de 3 archivos (+93/−0), 20 líneas de código.
- [x] Build 0 errores; 9 advertencias, todas preexistentes.
- [x] Concurrencia medida con conexiones separadas y barrera: 46/46 OK, y **arnés validado contra el
      código roto** (12 fallas).
- [x] `laplatense_dev` sin tocar; clones `laplatense_qa_l1..l6` y `laplatense_qa_d9` **intactos**;
      clon propio `laplatense_hotfix_tx`.
- [x] Producción sin tocar: ni Web Deploy ni `mysql8001.site4now.net`.
- [x] `PAT-059` reusado (paso 1 del escaneo); sin entrada nueva al catálogo.
- [x] Commit local. **Sin push. Sin deploy.**
- [ ] Queda **"aplicado, pendiente de re-verificación"**. El cierre lo declara QA en contexto nuevo,
      con el test de sockets separados por HTTP.
- [ ] **Pendiente de decisión de Joaquín**: (1) el estado intermedio de facturación AFIP, antes de
      cargar el certificado; (2) si este hotfix se mergea hacia `entrega-1-migracion` o se descarta
      ahí (el mecanismo ya está en `bdfd99b`, así que el merge va a colisionar en los dos métodos);
      (3) el desfasaje de migraciones de producción descripto abajo.

### Riesgo de deploy que no es de este hotfix pero lo condiciona

La memoria del proyecto dice que **producción está cinco migraciones atrás**, y dos de las que lista
(`EntregaTres_ConfirmarSinFactura_RecargoCuotas_NotaPago` y
`D9_NormalizarFechaCajaMovimiento_DiaDeNegocio`) **sí están en `2580f7c`**, que es lo que el brief
declara publicado. O el código publicado no es exactamente `2580f7c`, o la base de producción está
atrás de su propio código. **No se consultó producción** (estaba prohibido), así que queda como
condición a verificar **antes** del deploy: `SELECT MigrationId FROM __EFMigrationsHistory` contra
producción, comparado con las 8 migraciones de esta rama. Este hotfix no agrega ninguna, así que no
cambia el cuadro — pero si la base está atrás, el problema es anterior y hay que resolverlo primero.

### Segunda pasada: ampliación a tres sitios más (decisión de Joaquín, 2026-10-06)

Joaquín amplió el alcance **contra su propio pedido inicial** — "preferí un deploy a dos, y el
patrón ya es mecánico con `BloqueoDeFila` puesto" — a los tres sitios que el barrido había
relevado. Orden de exposición real que fijó él, y **corrigió un dato mío**: yo había dicho que el
gasto era alcanzable "porque los gastos ya se usan", y **producción tiene 0 gastos**. El bug está
vivo en el código publicado pero no hay nada que corromper todavía. El cobro de cuenta corriente,
en cambio, es la única vía por la que hoy entra la plata de un fiado.

Tambien cerró dos cosas que yo había dejado abiertas: **las migraciones de producción son
exactamente las 8 de esta rama** (el "5 atrás" de la memoria era de la rama de desarrollo, así que
el riesgo de deploy que declaré queda cancelado), y **no hay que intentar un índice único** en
`CajaMovimientos`/`MovimientosCCCliente` como refuerzo: el lock de fila es el único mecanismo.

#### Los tres sitios

| Sitio | Dueño que se bloquea | Dato que se relee | Qué dejaba pasar |
|---|---|---|---|
| `CuentaCorrienteClienteService.RegistrarCobroAsync` | **`Clientes`** (no un documento) | el **saldo**, re-consultado | saldo de CC negativo + ingresos de caja duplicados |
| `GastoService.AnularAsync` | `Gastos` | `gasto.Anulado` | dos Ingresos de caja por el mismo gasto |
| `VentaWorkflowService.CancelarBorradorAsync` | `Ventas` | `Estado` **y `DeletedAt`** | venta borrada con la plata movida |

**`RegistrarCobroAsync` pidió un tratamiento distinto y se declaró en vez de improvisarlo.** El
dueño que se bloquea **no es un documento, es el cliente**, porque el dato sobre el que decide la
guarda es el **saldo**, y el saldo es un **agregado del ledger**, no una columna: no existe una
"fila del saldo" que bloquear. Se bloquea la fila del cliente, que alcanza porque todos los
movimientos de esa cuenta cuelgan de él (dos cobros del mismo cliente se serializan, dos de
clientes distintos no se esperan). Y por la misma razón la relectura **no es un `ReloadAsync`** sino
**volver a correr la consulta del saldo** ya con el lock tomado. La transacción se adelantó: antes
`ObtenerSaldoAsync` y las dos guardas corrían **fuera** de ella.

**`GastoService.AnularAsync`: la reversión va por el MONTO DEL DOCUMENTO, no por el "neto vivo".**
Joaquín preguntó explícitamente, y la respuesta es que el neto vivo **no corresponde acá**, por tres
razones verificadas (no supuestas): (1) **no hay reversiones parciales** — `Anulado` es un booleano,
y el neto vivo existe justamente para permitir revertir $400 de $1.000 y después los $600; (2)
**`Gasto.Monto` es inmutable** — `IGastoService` expone solo Listar/Crear/Anular, **no hay método de
edición**, así que el Egreso que posteó el alta siempre vale exactamente `gasto.Monto`; (3) **el lock
es la exclusión**, no una segunda línea: con la relectura bajo lock se postea como máximo UNA
reversión. Y lo que se **descartó explícitamente**: inferir cuáles movimientos son reversiones por
el **signo** (un Ingreso con `OrigenTipo = "Gasto"`) para simular el neto sin la columna
`EsReversion`. Hoy funcionaría de casualidad —un gasto tiene un Egreso y a lo sumo un Ingreso— pero
es una **regla nueva disfrazada de port**, y se rompe en silencio el día que un gasto tenga otra vía
de ingreso asociada. **`EsReversion` no se portó y no se agregó ninguna columna.**

#### EL HALLAZGO DE ESTA PASADA, y lo encontró el arnés: `ReloadAsync` NO SIRVE como "relectura bajo lock" para una entidad con soft delete

Apliqué el patrón mecánicamente a `CancelarBorradorAsync` y **el criterio 8 falló**: con 8 requests
mezclados, **5 "éxitos"** (1 confirmar + 4 cancelar) y el estado prohibido en la base —
`borrada = True` **con** `caja = 1`, `cc = 1`, `stock = 98`. O sea: el fix mecánico no alcanzaba, y
el invariante que importa seguía roto.

Son **dos defectos distintos**, los dos invisibles leyendo el código:

1. **`Estado` no es un discriminador suficiente.** `CancelarBorradorAsync` cancela poniendo
   `DeletedAt` y **no toca `Estado`**: una venta cancelada sigue diciendo `Borrador`. Así que una
   guarda que solo mira `Estado` (a) deja pasar dos cancelaciones de la misma venta, las dos
   "exitosas", y (b) deja que una confirmación postee caja, CC y stock sobre una venta que otro
   request acaba de cancelar. **Es la mitad simétrica que nadie había escrito** (pasada 5 del
   barrido `LP-002`): había guarda de estado y ninguna de "ya cancelada".
2. **`_context.Entry(venta).ReloadAsync()` no ve las filas que el filtro global esconde.** El modelo
   tiene `HasQueryFilter(e => e.DeletedAt == null)`, así que para una venta ya cancelada la consulta
   de recarga **no trae nada**, la entidad queda *detached* y los valores en memoria siguen siendo
   los de **antes** del lock. **La relectura "ocurre" y no relee** — el peor modo de falla posible,
   porque parece hecha y el código se lee bien.

Se cerró con **un solo helper compartido**, `RelerEstadoBajoLockAsync`, que proyecta `Estado` **y**
`DeletedAt` con `IgnoreQueryFilters()`, y que usan **los tres** métodos del workflow
(`ConfirmarAsync`, `FacturarAsync`, `CancelarBorradorAsync`): una sola forma, para que el que lea el
diff no tenga que verificar tres variantes. Los tres ganaron además la guarda explícita de
"cancelada".

**Y la asimetría con `GastoService` se verificó y quedó escrita en el código, en vez de alinear los
dos por prolijidad:** ahí `ReloadAsync` **sí** es válido, porque `Gasto` nunca se borra —
`IGastoService` expone solo Listar/Crear/Anular, nadie escribe `Gasto.DeletedAt` y el único uso de
`_gastoRepository` es el `AddAsync` del alta; `Anulado` es una columna normal y la recarga la ve.
Está comentado con la condición: *si algún día se agrega una baja de gastos, esa recarga hay que
cambiarla por el patrón de la venta*.

**Regla generalizable para el catálogo:** en este proyecto **toda** entidad de negocio hereda
`SoftDestroyable` y tiene el filtro global. Por lo tanto `ReloadAsync` es una relectura **no
confiable** para cualquiera de ellas, y el patrón `PAT-059` necesita esta nota: *la relectura bajo
lock se hace con `IgnoreQueryFilters()` y proyectando los campos que deciden, salvo que se haya
verificado que la entidad no tiene ningún escritor de `DeletedAt`.*

#### Evidencia de la segunda pasada

Build **0 errores** (9 advertencias, todas preexistentes). Arnés ampliado a **82 afirmaciones, 82
OK**, corrido **4 veces** (el criterio 8 tiene un ganador legítimamente no determinista: en las
corridas ganó confirmar con N=4 y cancelar con N=8, y el estado final fue coherente con el ganador
en los dos sentidos).

**Control positivo de los tres sitios nuevos** (los tres services revertidos a `2580f7c`, arnés
igual): **42 OK / 40 FALLADAS**, reproducible en 2 corridas.

- **Cobro de CC**, el peor de los tres: **los N éxitos de N**. Con N=8, una deuda de $1.000 se cobró
  **8 veces**: saldo de cuenta corriente **−$7.000**, 8 créditos en el ledger y **$8.000** de
  ingresos de caja. Con N=3: saldo **−$2.000** y $3.000 de caja.
- **Anulación de gasto**: los N éxitos de N. Con N=8, **9 movimientos** de caja sobre el gasto y neto
  **+$3.500** de plata que nunca entró (con N=3, +$1.000). Con el fix: 2 movimientos y **neto 0**.
- **Cancelar contra confirmar**: 5 y 6 éxitos de 8 según la corrida, con el invariante violado
  (`borrada = True` con caja y CC posteadas) y además `DbUpdateException` en los perdedores.

#### Checklist de la ampliación

- [x] Los 3 sitios con la **misma forma reconocible**: lock del dueño → relectura → guarda. La única
      variante es `RegistrarCobroAsync` (dueño maestro + relectura por consulta), **declarada** en el
      código y acá, no improvisada.
- [x] **Sin migración EF** y **sin columnas nuevas**: `EsReversion` no se portó.
- [x] Código productivo agregado en esta pasada: **32 líneas** (27 en `VentaWorkflowService`
      incluyendo el helper compartido, 3 en `GastoService`, 2 en `CuentaCorrienteClienteService`) más
      3 constantes en `BloqueoDeFila`. El resto del diff es fundamento.
- [x] `RegistrarAjusteAsync` **no se tocó** (no estaba en el alcance que fijó Joaquín).
- [x] Control positivo corrido por sitio y reportado con números.
- [x] `laplatense_dev` sin tocar; fixtures `laplatense_qa_l1..l6` y `laplatense_qa_d9` intactos.
- [ ] Sigue **"aplicado, pendiente de re-verificación"**. El cierre lo declara QA.
- [ ] **Queda para decisión**: los 4 sitios restantes del barrido (`AjusteStockService`/`LP-024`,
      `GuardarBorradorAsync`, la carrera contra el cierre de caja de
      `RegistrarMovimientoManualAsync`/`GastoService.CrearAsync`, y `RegistrarAjusteAsync`), más la
      nota de `ReloadAsync` para `PAT-059`.


### Barrido `LP-002` sobre el resto del código publicado: 7 sitios relevados — **3 de ellos ya entraron** (ver la sección de la ampliación, arriba), 4 siguen sin tocar

El brief pidió explícitamente reportar y **no** arreglar. Ninguno se tocó: entrarían en la
superficie de un hotfix que tiene que ser auditable de un vistazo. Dato transversal que los
enmarca: **no existe ningún índice único sobre `CajaMovimientos` ni sobre `MovimientosCCCliente`**,
así que en esas dos tablas nada del motor protege contra plata duplicada — el lock de fila es el
único mecanismo disponible, y hoy `BloqueoDeFila` solo se usa en los dos métodos de este hotfix.

Ordenados por gravedad:

1. **`GastoService.AnularAsync` — el peor, y es la misma forma exacta del defecto que se acaba de
   arreglar.** Tiene transacción, pero la guarda `if (gasto.Anulado)` se evalúa **antes** de
   abrirla y nunca se relee bajo lock. Dos anulaciones simultáneas del mismo gasto pasan las dos y
   postean **dos Ingresos de caja por el mismo hecho**; el `UPDATE Anulado = true` es idempotente y
   no lo delata. **Alcanzable hoy en producción** (los gastos ya se usan). Es el candidato número
   uno a un segundo hotfix.
2. **`CuentaCorrienteClienteService.RegistrarCobroAsync`.** Tiene transacción, pero
   `ObtenerSaldoAsync` y la guarda `dto.Importe > saldoPrevio` corren **antes** de abrirla y sin
   lock del cliente. Dos cobros simultáneos pasan los dos → **saldo de cuenta corriente negativo y
   dos Ingresos de caja**. También alcanzable hoy.
3. **`AjusteStockService.AplicarAjusteAsync` — es `LP-024`, y el hotfix lo deja a medio camino en un
   sentido que conviene tener presente.** El ajuste es un **set absoluto** (`Stock = CantidadNueva`)
   sobre una lectura sin lock y sin transacción, así que **no lo frena el lock que ahora toma
   `ConfirmarAsync` sobre `Productos`**: un ajuste concurrente pisa el descuento de una venta que se
   está confirmando y deja la auditoría `CantidadAnterior` falsa. El hotfix protege el lado de la
   venta contra otra venta, no contra el ajuste. Excluido del alcance por decisión del brief.
4. **`VentaWorkflowService.CancelarBorradorAsync` — está en la misma clase que se tocó y vale
   decirlo.** Soft-delete sin transacción ni lock, con la guarda `Estado != Borrador` sobre una
   lectura libre: puede cancelar una venta que `ConfirmarAsync` está confirmando en paralelo y dejar
   **stock descontado + Ingreso de caja + Débito de CC sobre una venta borrada lógicamente**. No se
   incluyó porque el brief acotó a dos métodos; es el segundo candidato, y es barato (el lock ya
   existe en el proyecto y la venta es la misma fila).
5. **`VentaWorkflowService.GuardarBorradorAsync`.** `BloquearAsync` bloquea `Ventas` y `Productos`
   pero **no** las filas de `ItemsVenta`/`PagosVenta`: un ítem agregado en la ventana se persiste
   sobre una venta que ya quedó `Confirmada`, sin descuento de stock ni impacto en caja.
6. **`CajaMovimientoService.RegistrarMovimientoManualAsync` y `GastoService.CrearAsync` — la carrera
   contra el cierre de caja.** Las dos deciden con `ValidarPeriodoAbiertoAsync` y después escriben,
   sin lock: un `CerrarDiaAsync` que commitea en el medio deja el movimiento **dentro de un día ya
   cerrado y fuera del arqueo firmado**. La variante simétrica: `CerrarDiaAsync`/`CerrarMesAsync`
   están protegidos contra el cierre **duplicado** por índice único (cae como `DbUpdateException`
   cruda, no como error de negocio), pero leen los totales sin lock, así que un movimiento que
   commitea entre la lectura y el insert queda dentro del período y fuera de los totales
   congelados. **Descuadre silencioso** — y es la misma familia del descuadre de $2.500,75 de
   agosto 2026 que la Entrega 4 hizo visible.
7. **`CuentaCorrienteClienteService.RegistrarAjusteAsync`.** Sin guarda de estado y sin índice
   único: un doble click duplica el ajuste de deuda. Y, a diferencia de `RegistrarCobroAsync`,
   **no llama a `ValidarPeriodoAbiertoAsync`**, así que mueve el saldo de CC con fecha retroactiva
   de un mes ya cerrado.

Un octavo, sin plata ni stock pero es el único escritor con `SaveChanges` **intercalados** y sin
transacción del código publicado: **`ClasificacionAbcAutomaticaService.RecalcularAsync`** guarda por
lotes dentro del `foreach`, así que un fallo en el lote N deja los N−1 aplicados y el contador
`ProductosActualizados` del log miente.

**Nada de esto se tocó.** Son candidatos a un segundo hotfix, en el orden 1 → 2 → 4.


