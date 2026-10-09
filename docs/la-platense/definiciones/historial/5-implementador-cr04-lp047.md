# Historial - Implementador / La Platense

Archivado el 2026-10-07 desde `definiciones/5-implementador.md` para dejar lugar a la entrada
del ensayo de `LP-050` sin cruzar el techo de 150 KB.

## CR-04 plan de echeqs + LP-047 + LP-044/045/046/048 (2026-10-07)

**Seis commits locales en `entrega-1-migracion`, sin push y sin deploy:** `57f06ea` (LP-044),
`a0abb89` (LP-045), `ac7bccc` (LP-046), `1460cd1` (LP-048), `6e34f9a` (LP-047), `e2da786` (CR-04).
Build **0 errores / 8 advertencias**, todas `NU1902` de MailKit/MimeKit y **ninguna de código**.

> **El brief declaraba la línea base en 9 advertencias y se mide 8.** No es una regresión al revés:
> las `NU1902` se emiten una vez por proyecto y por restore, así que el total oscila entre 8 y 9
> según qué se recompila. Lo estable y lo que importa: **0 advertencias de código**.

### Qué es CR-04 y qué NO es

`D-CR04.1` lo acotó a propósito: *"alcanza con el plan de fechas de pago pero agregar numeros de
cheque, banco, acreditacion calculada con los x cantidad de dias"*. **No es una cartera de cheques.**
No hay máquina de estados propia, no hay circuito de rechazo y reemplazo, no hay conciliación contra
extracto y no hay cheques recibidos de clientes.

**El estado del echeq ES el estado de su pago.** `LineaEcheq` no tiene `Estado`: una línea de plan
nace como pago programado `Pendiente` y pasa a `Pagado` cuando alguien confirma, por
`ConfirmarPagoProgramadoAsync`, que ya existía. Duplicar el estado habría dado dos fuentes de verdad
de lo mismo y la única pregunta interesante sería cuál de las dos está mal.

### La decisión que explica todo el diseño: el plan no escribe pagos

`PlanEcheqService` **arma y valida** las N líneas y delega la escritura en
`IPagoProveedorService.RegistrarPagoAsync`, que es el único camino de alta de un pago a proveedor
desde la Entrega 3 y el que ya trae el tope del **saldo sin comprometer**, la guarda de estado de la
compra y la transacción única.

Escribir sus propias filas habría dado un **segundo escritor de `PagoOrdenCompra`** con su propia
copia de esas reglas — que es exactamente cómo el precedente terminó con cinco caminos que movían la
deuda sin mover la plata. Por eso el contrato nuevo tiene tres métodos y ninguno postea nada.

**Lo que sí decide el Service nuevo:** el vencimiento (`fecha base + los días del plazo`; el cliente
nunca lo manda, podría no corresponder al plazo), que la suma de las líneas **cuadre** con el total,
que el número sea **único por banco** y que todas las líneas sean `ChequeElectronico`.

### El plazo 0 — la trampa del alcance, y la regla que la cierra

Un echeq "al día" vence **hoy**, que **no es una fecha estrictamente futura**. Con el criterio
general de programación (`FechaPagoTentativa > hoy`) esa fila habría nacido en `Pagado` y habría
posteado su egreso de caja y su Pago de deuda **en el acto**, mientras sus hermanas del mismo plan
quedaban pendientes. O sea: plata saliendo de la caja al **crear** el plan, contra `PF19`.

La regla nueva, en `RegistrarPagoAsync`: **una línea con datos de echeq nace siempre programada**,
tenga el plazo que tenga. Se decide por la **presencia de los datos del echeq** y no por la forma de
pago, así que pagar con `ChequeElectronico` **sin** plan sigue funcionando exactamente como antes —
eso es lo que hace el cambio aditivo de verdad y no un cambio de comportamiento disfrazado.

### La fecha de confirmación, y el dato medido que va en contra de la decisión

La decisión del cliente pide la acreditación *"calculada con los x cantidad de dias"*. En `marihogar`
(CR-86) se midió contra el extracto bancario real: **el vencimiento del cheque acertó 1 de 13; la
fecha que el usuario leyó del extracto, 8 de 13.**

Resolución: el vencimiento **se calcula** (es lo pedido) y es el que ordena la grilla y dispara el
aviso, pero `ConfirmarPagoProgramadoAsync` ganó un **`DateTime? diaPagoReal` opcional** — `null`
mantiene el comportamiento anterior exacto (se imputa a hoy) — y la pantalla lo **propone** con el
vencimiento, acotado a hoy porque un movimiento de caja no puede ser futuro, y lo deja **editable**.
El camino normal es un click sin tipear nada y el 61% de los casos en que el banco debitó otro día
tiene arreglo. **Nada se acredita solo.**

**Y lo que esa fecha editable obligaba a no romper:** el gap lock de período que se reserva pasa a
ser el del **día elegido** y no el de hoy. Reservar el de hoy dejaría la escritura real sin reservar,
que es el defecto `LP-018` exacto. El orden canónico de `LP-035` (todos los locks primero, todas las
lecturas comunes después) **no se tocó**.

### El aviso es el que ya existía

`PAT-056`: chequeo oportunista al primer request del día, idempotencia en la base. Un echeq **es** un
pago programado y su vencimiento **es** su `FechaPagoTentativa`, así que el aviso lo levanta tal como
estaba. El único cambio: ahora **nombra el cheque** ("Echeq 0001234 del Banco Nación"), que es como
el administrador lo cruza contra el homebanking, y linkea al listado de echeqs en vez de al detalle
de la compra, porque ahí está el botón. **No se agregó ningún `AddHostedService`**: el repo no tiene
ninguno a propósito y en SmarterASP un job con hora fija puede no correr nunca si el pool se recicla.

### Migración EF — `CR04_PlanDeEcheqs`

**Aditiva pura, y es verificable operación por operación:** un `CreateTable`, tres `CreateIndex`
sobre esa tabla nueva, y nada más. **Cero `AddColumn`, cero `AlterColumn`, cero `Sql()` de backfill.**
`PagosOrdenCompra` no se toca: la relación vive del lado nuevo (el FK está en `LineasEcheq`), así que
ningún pago histórico necesita una columna más ni un valor derivado. El `Down` es un `DropTable`
simétrico.

**Un solo índice único, el de `PagoOrdenCompraId`** (es lo que hace que la relación sea 1 a 1). El de
`(Banco, Numero)` **no** es único a propósito: toda entidad hereda baja lógica y MySQL no tiene
índices únicos filtrados (y meter `DeletedAt` en la clave no sirve, porque MySQL considera distintos
dos `NULL`), así que un único ahí impediría reusar el número de un echeq cuyo plan se dio de baja —
que es el caso real. La unicidad es de Service y la **carrera residual queda declarada, no cubierta**:
su consecuencia es un dato repetido en una grilla, no plata mal movida.

### `D-CR04.2` cumplido

`LineaEcheq.AlicuotaImpuestoCheque` queda en cero, **sin escritor y sin exponerse en ningún
formulario** — es el lugar reservado para que el impuesto al cheque (Ley 25413) sea aditivo en v2, con
el mismo criterio de "tasa vigente por fecha, congelada en el documento". Es la única excepción
declarada a la regla de que toda propiedad de negocio es editable en Alta y Edición: todavía no es
una propiedad de negocio, es un lugar reservado, y ofrecerla vacía invitaría a cargar un impuesto que
el sistema no calcula ni postea.

### Desviación declarada del flujo 14

El diseño decía que el bloque "Plan de pago" se habilita **dentro** del formulario de pago. Quedó en
una **pantalla propia** (`PlanEcheqs`) a la que se entra desde ahí: la puerta aparece en el formulario
de pago al elegir *Cheque electrónico*, que es donde el diseño la quería. El motivo es que son dos
shapes de datos y dos acciones distintas, y un solo `<form>` con los dos obligaría al servidor a
adivinar cuál se quiso mandar. **Lo funcional no cambia**: mismos plazos, mismos importes editables,
mismo vencimiento calculado, mismo faltante/sobrante y nada mueve plata hasta confirmar. **Queda para
que el Diseñador lo acepte o lo rechace.**

### `LP-047` — la baja de un catálogo dejaba de existir fuera del combo

QA posteó a mano y **creó y confirmó** la venta 9036 con el `TarjetaId` de una tarjeta en `Activo=0`.
La única expresión de la baja era que `ITarjetaService.ListarActivasAsync` no la ofreciera, y eso es
una lista para pintar. Forma de `OLV-019` / `MH-052`.

**La distinción es todo el fix**, porque los dos casos caían juntos:

- **(a) seguir guardando** un pago que **ya** tenía ese valor → pasa. Dar de baja una tarjeta no
  puede romper una venta ya cargada ni una ya cerrada (criterio explícito de CR-03), y es la razón
  por la que el filtro **no** se puede poner en `ObtenerPorcentajeRecargoAsync`, que es donde
  "parecía" faltar.
- **(b) estrenar** el valor dado de baja en un pago nuevo, o cambiarle la tarjeta a uno existente por
  una dada de baja → se rechaza.

`IRecargoCuotasService.ValidarCatalogosActivosAsync` es la guarda nueva, y
`VentaWorkflowService.GuardarBorradorAsync` — el **único** escritor de `PagoVenta.TarjetaId` en el
repo, verificado por grep — decide si se estrena comparando contra lo que la fila ya tenía.
`RecargoCuota.Activo` tenía la misma forma y se barrió en el mismo pase.

**Barrido de las otras banderas `Activo` del dominio, que el parte pedía mirar. Son siete y no todas
tenían el defecto:**

| Bandera | Estado |
|---|---|
| `Tarjeta.Activo`, `RecargoCuota.Activo` | **cerradas en esta ronda** |
| `Proveedor.Activo` | **ya estaba bien, y es el precedente del patrón que se usó acá**: `OrdenCompraService.CrearAsync` lo rechaza y `EditarAsync` hace exactamente la distinción (a)/(b) con `!proveedor.Activo && proveedor.Id != orden.ProveedorId` |
| `CodigoBarrasProducto.Activo`, `CodigoProveedorProducto.Activo` | se filtran en todas las consultas que los usan: son datos de búsqueda, no valores que un documento estrene |
| `Marca.Activo`, `Categoria.Activo`, `Modelo.Activo` | **siguen con la forma del defecto** y **no se tocaron** |

**Las tres que quedan son un pendiente nombrado, no un olvido:** `ProductoService` no las valida y
viajan por POST hacia `Producto`. Si un producto nuevo puede nacer con una marca dada de baja es una
**decisión de negocio que hay que preguntar**, no deducir — y el efecto económico es nulo (una marca
no entra en ningún cálculo). Va al bloque de pendientes.

### Los cuatro defectos chicos

- **`LP-044`** — el comentario del `form=` afirmaba un mecanismo de parser **falso** ("el parser saca
  el form de la tabla", "los inputs quedan huérfanos", "postea una fila vacía, pasa en todos los
  navegadores"). QA lo midió en tres motores Chromium: el form queda **hijo del `<tr>`**,
  `form.children` está vacío y aun así `form.elements` tiene los 18 campos y el submit postea **la
  fila completa**, que el servidor guarda. El `<form>` tiene una regla propia en las insertion modes
  *in-table* / *in-row*: no hay foster parenting y el **form element pointer** asocia los campos a un
  form que no es su ancestro. **Lo que sí rompe es la variante sin `</form>` por fila**: el parser
  descarta el segundo form y una fila postea **las dos** con la clave duplicada — un dato cruzado, no
  una fila vacía. **El código se queda** (el `form=` es la única de las tres variantes que no depende
  de dónde cae el cierre); el comentario se reescribió con lo medido.
- **`LP-045`** — `EtiquetaFormaProveedor` seguía afirmando exhaustividad sobre un switch con `_ =>`.
  **Barrido del archivo completo:** son **cinco** switch y no cierran todos igual — los tres que
  traducen al ledger lanzan, los dos de etiqueta degradan a `ToString()`. Y el hallazgo que explica
  por qué ahora es un **inventario por miembro** y no una regla general: la corrección anterior había
  escrito *"los switch cierran con un `_ =>` que LANZA"*, que es una afirmación general y era falsa
  para dos de los cinco. **La ronda que vino a cerrar un comentario falso escribió otro al
  corregirlo.** Cuarta instancia en un archivo hermano (el backfill de `20261005221747` decía "el que
  avisa es el switch exhaustivo del mapper": no es exhaustivo y el compilador no avisa — lanza en
  ejecución). Barrido del repo por `xhaustiv` / `CS8509` / `sin _ =>`: los dos hits restantes son
  honestos.
- **`LP-046`** — el fix no es poner 14 donde decía 13: es que el número tenga **una** fuente. El
  arnés clasifica cada afirmación por su marca e imprime un bloque **REPARTO POR MARCA** con el
  conteo y, por nombre, cuáles fallaron y con qué marca. El encabezado ya no repite ningún número.
  Medido: **14 DISCRIMINA / 17 COBERTURA / 9 CONTEXTO / 1 sin marca, total 41** — exactamente el
  conteo que QA había hecho a mano. Y la salida ahora contesta directamente la pregunta que se le
  hace a una corrida mutante.
- **`LP-048`** — la precondición `3d.1` comparaba el total **absoluto** del mes contra lo sembrado.
  La equivalencia es una propiedad del **fixture**, no de la afirmación. Ahora suma solo lo sembrado
  (`UsuarioId LIKE 'ZZSEIS%'`, la convención del propio archivo) e **imprime los dos números**,
  porque los dos hacen falta: el sembrado prueba que el escritor en vuelo commiteó, y el absoluto es
  el que `3d.3` le exige al arqueo. `3c.1` tenía la misma forma y se corrigió en el mismo pase.

### Evidencia ejecutada

**Arnés nuevo re-corrible en `tools/ArnesPlanEcheqs`** (aborta con exit 2 si se lo apunta a
`laplatense_dev`, `laplatense_qa*` o `site4now`; base de prueba `laplatense_cr04`):

- **49 EVALUADAS / 49 OK / 0 FALLADAS / 0 NO MEDIDAS, exit 0, en dos corridas.** La limpieza final
  corre dentro del `try` y **se afirma** sobre ella (`6.1` y `6.2`, que incluye devolver a `Activo`
  la fila seedeada que el escenario 5 desactiva — sin eso la corrida no sería idempotente).
- **Ocho mutantes, y cada uno tumba algo:**

| Mutante | Qué rompe | Afirmaciones que tumba |
|---|---|---|
| `M1` | se quita la regla "un echeq nace siempre programado" | `2.2`, `2.3`, `2.4`, `2.5` y, por arrastre, `4.1` (+ 5 NO MEDIDAS) |
| `M2` | se quita la validación de que la suma cuadre | `3.1`, `3.2`, `3.3` |
| `M3` | se quita la unicidad del número por banco | `3.4`, `3.5` |
| `M4` | la fecha elegida al confirmar se ignora | `4.2`, `4.3`, `4.5`, `4.6`, `4.8`, `4.9` |
| `M5` | se quita la guarda de `LP-047` | `5.1`, `5.2`, `5.3`, `5.8`, `5.9` |
| `M6` | el vencimiento deja de escalonarse | `1.4` |
| `M7` | el aviso deja de llevar el número de echeq | `4.10` |
| `M8` | la guarda de `LP-047` se vuelve **demasiado amplia** (valida siempre, no solo al estrenar) | `5.5` |

- **El relabel se midió en las DOS direcciones, y es la parte que QA ya encontró mal una vez:**
  - cinco afirmaciones marcadas `[COBERTURA]` **cayeron bajo mutante** y pasaron a `[DISCRIMINA]`
    (`3.3` con M2, `4.1` con M1, `4.5` y `4.6` con M4, `5.9` con M5);
  - y `4.10` y `5.5` estaban marcadas `[DISCRIMINA]` **sin que ningún mutante las matara**: en vez de
    bajarles la marca se agregaron **M7 y M8**, que es lo que de verdad faltaba. Bajar la marca habría
    cumplido la letra y dejado el invariante sin probar.
  - **Verificación final: en los 8 mutantes, toda FALLADA es `[DISCRIMINA]` y cero
    `[COBERTURA]`/`[CONTEXTO]` cayeron.** Reparto impreso por el arnés: **24 DISCRIMINA / 21
    COBERTURA / 4 CONTEXTO**, y la unión de las tumbadas es exactamente las 24.
- **`1.7` y `1.8` quedaron `[COBERTURA]` y está declarado por qué:** con M1, las cuatro líneas del
  plan a 30/60/90/120 siguen siendo futuras, así que el criterio general las programa igual y la
  afirmación pasa en los dos lados. Lo que discrimina es la familia 2, con el plazo 0. Marcarlas
  `[DISCRIMINA]` habría sido exactamente el relabel falso.
- **No-regresión de los tres arneses que ya existían**, sobre bases vírgenes de 18 migraciones
  (`DROP` + `CREATE` + `dotnet ef database update`): `ArnesTarjetaYTransferencia` **41/41/0**,
  `ArnesSeisSitiosRestantes` **32/32/0 + 2 NO MEDIDAS**, `ArnesReconciliacionTx` **153/153/0**. El
  último cubre `ConfirmarPagoProgramadoAsync`, que es el método que esta ronda modificó.
- **`LP-048` medido sobre los DOS fixtures**, que es su criterio de aceptación: base virgen
  **32/32/0 + 2 NO MEDIDAS** y clon de `laplatense_dev` con las migraciones al día **32/32/0 + 2 NO
  MEDIDAS**, con `3d.1` imprimiendo *"$333 sembrados por el arnés vivos en 09/2026; el mes entero
  suma $95996,80"* — el número exacto que QA reportó. **Control positivo:** con la comparación
  devuelta al total absoluto, el clon da **31 OK / 1 FALLADA** y la fallada es `3d.1`.
- **Grafo de DI** con `BuildServiceProvider(ValidateOnBuild + ValidateScopes)`: `IPlanEcheqService`
  se resuelve (se agregó la resolución explícita al arnés del ítem 4c, porque depende de
  `IPagoProveedorService` y resolverlo prueba que la cadena entera se construye). **92 OK / 0 FALLA.**
- **Las vistas Razor sí compilan en el build**, verificado positivamente: un símbolo inexistente en
  `Echeqs.cshtml` dio `CS0103` con número de línea, y se revirtió.

### Los dos hallazgos que el arnés produjo, uno en mi propio código

1. **La unicidad del número de echeq consultaba `LineasEcheq` creyendo que el filtro global de baja
   lógica alcanzaba. No alcanza.** `CancelarPagoProgramadoAsync` le escribe `DeletedAt` al **pago** y
   **no** a la línea de echeq, que queda viva — así que el número de un echeq cuyo plan se dio de baja
   quedaba bloqueado **para siempre**, que es justo el caso que esa validación existe para no
   bloquear. La consulta ahora arranca en `PagosOrdenCompra` (y excluye el pago `Revertido`). Es la
   misma familia que el `ReloadAsync` decorativo de `LP-035`: **la baja lógica no se propaga a las
   hijas, y un filtro global aplica a la entidad que se consulta, no a la que importa.** Lo midió la
   afirmación `3.10`, y es el argumento más fuerte que tengo de que el arnés mide algo.
2. **`tools/ArnesEntrega3Item4c` tenía `laplatense_dev` HARDCODEADO y sin guarda.** Ignoró
   `ConnectionStrings__DefaultConnection` y **escribió en la base compartida** (un proveedor, dos
   órdenes de compra #79 y #80, un producto, un movimiento de cuenta corriente y uno de stock) antes
   de morir sin limpiar — porque **`laplatense_dev` está cuatro migraciones atrasada** respecto de
   esta rama y no tiene `CandadosPeriodoCaja`. **Las filas se limpiaron a mano y dev quedó verificada
   en su línea base** (112.485 productos, 2.993 clientes, cero filas `ZZTEST`, cero órdenes 79/80). El
   arnés ahora toma la cadena del entorno y **aborta con exit 2** contra dev/qa/site4now, verificado
   por ejecución. Es exactamente lo que QA había observado del arnés del lote 4 y por lo que no lo usó.

### Lo que queda fuera de alcance, declarado y no omitido

- **`AvisoPagosProgramadosService.EjecutarChequeoDelDiaAsync`** (el notificador) y el middleware en el
  pipeline real: necesitan usuarios con rol y un request HTTP. Lo que **sí** se mide es el DTO que lo
  alimenta (`4.10`), que es donde entró el cambio. Van como pasos de la guía de QA.
- **Las pantallas**: el bloque de plan, el listado con `ov-filtros` y el popup de confirmación con la
  fecha propuesta. Es lo que el rol no puede ejecutar.
- **La carrera de dos planes cargando el mismo número de echeq en el mismo instante**: no hay índice
  único que la cubra, por el motivo de arriba.

