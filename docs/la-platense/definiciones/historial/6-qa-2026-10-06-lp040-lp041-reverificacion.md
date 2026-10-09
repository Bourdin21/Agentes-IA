# Archivado de 6-qa.md — re-verificaciones de cierre de LP-040, LP-041 y LP-037 (2026-10-06)
# Archivado a mano por QA el 2026-10-07 al escribir el bloque del modulo 16 (6-qa.md estaba en 149 KB
# y scripts/archivar no reconoce sus headings).

# `LP-041` + `LP-037` — re-verificación de cierre (2026-10-06, rama `entrega-1-migracion`, commits `41ec1b2` y `408b814`)

**Los dos CERRADOS.** Con esto **no queda ningún defecto abierto en el proyecto** por primera vez en varias rondas: el lote
de los 3 CR que faltan (`CR-03` interés por tarjeta, `CR-04` plan de echeqs, `CR-05` transferencia) puede arrancar limpio.
2 defectos nuevos, los dos `minor` y los dos **del instrumento, no del sistema**: `LP-042` y `LP-043`.

Contexto fresco: no se leyó la transcripción del implementador, sólo los dos mensajes de commit y el diff. Fixture propio
(`lp41rev`, clon desechable en `C:/qa41` desde la rama, 16 migraciones aplicadas con `dotnet ef database update`), nunca
`laplatense_dev` ni producción ni los fixtures existentes. El repo del sistema quedó **sin un solo cambio**
(`git status --porcelain` limpio, verificado al cerrar).

## La ventana horaria: la corrida entera se hizo dentro de la que rompía

Todas las mediciones de abajo se tomaron entre las **23:04 y las 23:33 ART del 2026-10-06**, o sea **02:04–02:33 UTC del
2026-10-07**: `DateTime.UtcNow.Date` era **un día posterior** a `ArgentinaTime.Hoy` durante toda la corrida. Es exactamente
la ventana 21:00–24:00 ART en la que el guard de "fecha futura" rechazaba la siembra.

**Control positivo, el que hace defendible el resto** (23:25 ART / 02:25 UTC, arnés de `c5740c7` corrido contra el fixture
con el código de `HEAD`): reproduce **`La fecha del movimiento no puede ser futura.`** en `16.0/N=3` y `16.0/N=8`, el
cascadeo de `16.1` y `16.2` (0 de 3, 0 de 8; 0 filas de contramovimiento), **`16.3` PASANDO VACÍA** (`neto=0` de un id
inexistente, `OK` en los dos N) — las 6 fallas del grupo 16, tal cual estaban diagnosticadas — y además muere en
`LimpiarAsync` con **exit 127, sin imprimir resumen** (`grep -c EVALUADAS` = 0). El mismo arnés en `41ec1b2` corrido en la
misma ventana da 153/0. La dependencia del reloj **no sigue viva en ningún otro grupo**: los 185 asserts de los dos arneses
pasaron con `UtcNow.Date` un día adelante. Los `DateTime.UtcNow` que quedan en los dos `Program.cs` son campos de
*timestamp* (`Venta.Fecha`, `PagoVenta.Fecha`, `FechaCierre`, `VencimientoCAE`), no claves de día de negocio que atraviesen
un guard de fecha futura.

## Línea base medida por esta memoria — 2026-10-06, 23:04–23:33 ART

| Arnés | Evaluadas | OK | FALLADAS | exit | Corridas |
|---|---|---|---|---|---|
| `tools/ArnesReconciliacionTx` | **153** | **153** | **0** | 0 | 7 (3 base envejecida + 4 base virgen), idempotente |
| `tools/ArnesSeisSitiosRestantes` | **32** | **32** | **0** | 0 | 23 (20 + 3 base virgen), idempotente |

Idempotencia verificada en los dos sentidos que importan: **3 corridas seguidas sobre la misma base** (mismo total, mismo
exit) y **las dos arneses interladas dos veces sobre la misma base virgen** (153/0, 32/0, 153/0, 32/0), que es lo que cierra
el residuo cruzado de `LP-040`. El número declarado por el implementador se reproduce exacto.

## `LP-041` — CERRADO. Los cuatro arreglos, uno por uno

| Qué | Evidencia observada |
|---|---|
| Limpieza en el orden de las FK | 23 y 7 corridas sobre la misma base, **misma cantidad de afirmaciones evaluadas en todas** y exit 0 siempre. El control positivo en `c5740c7` muere en `LimpiarAsync` con exit 127. |
| Un aborto no puede parecer limpio (exit 3) | Los dos arneses contra una base **sin migraciones**: `ABORTADO: EL ARNES NO SE MIDIO. Murio con una excepcion antes de terminar.` + **exit 3**. |
| Cero afirmaciones no es una corrida limpia (exit 4) | Helper `Afirmar` neutralizado con un `return` inyectado: `=== 0 afirmaciones EVALUADAS: 0 OK, 0 FALLADAS ===` + `ABORTADO: NO SE MIDIO NADA.` + **exit 4**. |
| 5.4 reescrita **mide** | Mutante M4 (reinsertada la escritura legada `venta.CAE = "99999999999999"` en `FacturarAsync`): **`5.4/N=3` y `5.4/N=8` FALLAN** con `Venta.CAE=99999999999999`, y **153 evaluadas igual** (ninguna afirmación se perdió). |
| 5.2 declarada tripwire, no evidencia | Verificado por grep: `IAfipService` **no está inyectado** ni en `VentaWorkflowService` ni en `FacturacionParcialService` (sólo queda `AfipSettings`). La declaración del implementador es **fiel**: no puede fallar hoy y lo dice. |
| Grupo 16 (el reloj) | Ver la sección de la ventana horaria: control positivo con los importes y mensajes exactos. |

## `LP-037` — CERRADO

| Criterio | Resultado | Evidencia observada |
|---|---|---|
| `CerrarDiaAsync` vs **7** escritores: el total firmado cuadra | **PASS** | `3.2/N=8` → `cierre=721,00, suma de movimientos vivos del dia=721,00, escritos=7`. Es **el caso original del defecto** ($0 contra $721) cuadrando. |
| `CerrarDiaAsync` vs **2** escritores | **PASS** | `3.2/N=8` en otras corridas → `205,00 == 205,00` y `207,00 == 207,00` con `escritos=2`; y el determinista `3c.3` → `cierre=500,00 == 500,00`. |
| **Cierre mensual** igual | **PASS** | `3d.3` → `cierre=333,00, suma de movimientos vivos del mes=333,00`, con `3d.1` ($333 vivos en 09/2026) y `3d.2` (`cierre #1`) afirmadas aparte. |
| 3c y 3d **discriminan** | **PASS** | Mutante **M1n** (`TomarCandadoPeriodoAsync` → `Task.CompletedTask`, el candado no se toma): **4 fallas, 2 corridas iguales** → `3.2/N=3` $0 vs **$201**, `3.2/N=8` $0 vs **$721**, `3c.3` $0 vs **$500**, `3d.3` $0 vs **$333**, con **las 4 precondiciones en OK** y **32 evaluadas** (la falla es medición, no efecto colateral). |
| Sin deadlock en los caminos que comparten pantalla | **PASS** | Escenario 5 (revertir vs confirmar pago programado con el día cerrado): `0 deadlock(s) de 8 llamadas`, `0 excepciones`, en las 23 corridas. `grep -i deadlock` sólo matchea etiquetas de afirmación. |
| No-regresión: guarda de período cerrado | **PASS** | `3.1/N=3` y `3.1/N=8`: `La caja del día 06/10/2026 ya está cerrada: no se puede regi…` como mensaje de negocio. |
| No-regresión: cierre sin concurrencia | **PASS** | `3c.4` `Caja del día 06/10/2026 cerrada correctamente.` y `3d.4` `Caja del mes 09/2026 cerrada correctamente.` (un solo cerrador en cada uno). |
| No-regresión: reglas de rango del cierre mensual | **PASS** | `3d.5` `El mes 10/2026 todavía está en curso: el cierre mensual se hace a partir del día 1 del mes siguiente.` · `3d.6` `No se puede cerrar la caja de un mes que todavía no ocurrió.` · el mes anterior (09/2026) **sí** cierra (`3d.2`). |
| No-regresión: `ArnesReconciliacionTx` (11 sitios que reservan el período) | **PASS** | 153/0 en 7 corridas con la centinela puesta. |
| Migración aditiva aplicada | **PASS** | `CandadosPeriodoCaja` con `UNIQUE KEY IX_CandadosPeriodoCaja_Anio_Mes_Dia (Anio, Mes, Dia)` y `Dia int NOT NULL` (el `0` del candado del mes funciona como clave real). |

### El hallazgo del punto 4 (el `INSERT IGNORE` que espera) — **cerrado, y la lectura común es load-bearing**

Tres mutantes, porque el primero no alcanzaba:

- **M2** (anulada sólo la lectura común): **32/0 en 10 s, no se cuelga.** No prueba nada: la caché de proceso
  `_candadosVistos` corta antes y el `INSERT IGNORE` sólo se emite una vez por período por proceso.
- **M2b** (anulada la lectura común **y** la caché, o sea el peor caso: proceso nuevo en cada request): **el arnés se
  colgó**. 400 s en el escenario 5 —justo el que corre con locks de fila en la mano— sin imprimir una línea más; lo mató un
  `timeout` externo (exit 124). El riesgo que el implementador describe es **real y reproducible**.
- **M2c** (anulada sólo la caché, lectura común puesta): **32/0 en 10 s.** La lectura común sola cierra la espera. El fix
  está completo: no queda ninguna variante viva del camino "la fila ya existe y dos cerradores compiten".

## Cobertura del catálogo cross-proyecto

| id | severidad | aplicó | resultado |
|---|---|---|---|
| `LP-037` | blocker | sí (es el defecto) | **CERRADO**, `fix_aplicado` escrito en el catálogo (el ítem **no existía**: se creó en esta corrida, porque su `regla_preventiva` —gap lock vs record lock en una reserva de período— es de las más reutilizables del estudio) |
| `LP-041` | minor | sí (es el defecto) | **CERRADO**, `fix_aplicado` escrito |
| `LP-040` | major | no-regresión | OK: `5.x` miden el contrato vigente, `Venta.CAE` sigue vacía, el atajo delega |
| `LP-039` | major | no-regresión | OK: sin tocar; el barrido de escritores de las columnas obsoletas ya estaba hecho y M4 confirma que 5.4 lo vigila |
| `LP-008` | — | sí | El XML-doc de `BloquearPeriodoCajaAsync` describe el mecanismo nuevo y **no afirma más de lo que hace**: los tres detalles no obvios (conexión aparte, `Dia = 0` y no NULL, lectura común previa) están escritos con su por qué |
| `LP-009` | — | sí | día de negocio argentino: `ArgentinaTime.Hoy` en la siembra; verificado en la ventana que rompía |
| `LP-018` / `LP-035` / `LP-036` | — | no-regresión | OK: escenarios 1, 2, 4 y 5 del arnés, 32/0 |

**Reglas nuevas o modificadas desde la última validación:** `6-qa.md` declaraba `2026-10-06`. Diferencial ejecutado:
`git log --since=2026-10-06 -- .github/instructions/32-estandares-qa-implementador.instructions.md docs/qa/regresiones-manuales.yml`
→ **0 commits**; el índice de `32` y `cat_resumen.txt` coinciden con lo validado. **Ninguna regla nueva que ejecutar por ese
concepto.** Campo actualizado a `2026-10-06` (esta corrida).

## Defectos nuevos — partes emitidos

**`LP-042` `minor` — la línea base declarada suma afirmaciones que pasan vacías, y la salida no las distingue.**
De las 185 `OK` declaradas, **5 no pueden fallar hoy y sólo 3 están declaradas**. `3.2/N=3` da siempre
`cierre=0,00, suma=0,00, escritos=0` (declarada: la etiqueta dice "condicional — ver 3c", y M1n prueba que sigue viva).
`2.2/N=3` y `2.2/N=8` **no están declaradas**: la etiqueta dice `INVARIANTE` y la afirmación es
`venta.Estado != Confirmada || (...)`, con `confirmo=False` en **46/46** mediciones, así que la rama que importa nunca corre.
`5.2/N=3` y `5.2/N=8` de `ArnesReconciliacionTx` están declaradas tripwire en el comentario pero suman a los 153.
Criterio de re-verificación: el resumen de los dos arneses distingue **OK / FALLADAS / SIN MEDIR**, el número que se cita
como no-regresión es el de las que midieron, y `2.2` o se imprime `SIN MEDIR` o tiene un escenario `2c` determinista con su
precondición afirmada aparte (la receta de 3c/3d). **No bloquea el cierre de `LP-037`**: su invariante sí tiene cobertura
determinista en 3c/3d.

**`LP-043` `minor` — el arnés todavía no puede reportar un cuelgue.** Los cinco exit codes de `LP-041` cubren todas las
formas de *terminar*; ninguno cubre **no terminar**. Reproducido con M2b: 400 s sin imprimir nada, exit 124 puesto por el
`timeout` externo. Un `try/catch` no atrapa una espera. Criterio de re-verificación: con el mutante de dos líneas, el arnés
se autolimita, imprime el resumen parcial, nombra el escenario y sale con un exit code reservado al cuelgue — sin `timeout`
externo; y la corrida limpia no toca el tope.

### Lo que NO es defecto, y por qué (se midió y se descartó)

Con el mutante **M1** (quitarle el ` FOR UPDATE` al candado, dejando la sentencia como lectura común) fallan **6**
afirmaciones y no 4: se suman `2.2/N=3` y `2.2/N=8` con `estado=Confirmada, unidades=7,000, stock descontado=2,000,
caja=$2420,00, total venta=$8470,00`. Parecía un defecto nuevo y **no lo es**: M1 convierte el candado en la **primera
lectura común de la transacción**, lo que congela el read view de `REPEATABLE READ` antes del lock de la fila de venta, así
que la confirmación postea contra un set de ítems viejo. Es la falla que el XML-doc de `BloqueoDeFila` predice ("todos los
locks primero, todas las lecturas comunes después"), y es efecto del mutante. La prueba que lo separa: con **M1n** (el
candado **no se toma**, ninguna sentencia) fallan **exactamente 4** y `2.2` pasa con `confirmo=False`. La guarda real del
sistema se leyó y está bien: `GuardarBorradorAsync` abre transacción, toma el lock de la fila, **relee `Estado` bajo lock**
con `RelerBajoLockAsync` y rechaza si no es `Borrador`. Lo que falta es el escenario que lo ejercite → `LP-042`.

### Fuera de alcance, no se reportó como defecto

`CR-03`/`CR-04`/`CR-05` (no construidos) · `R17`-`R19` y la ausencia de nota de crédito / baja de comprobante (módulo 16,
Entrega 5; los dos `BLOCKED` de esta memoria siguen cerrados como "no aplica por diseño") · `Venta.CAE` /
`NumeroComprobante` / `VencimientoCAE` / el tipo, obsoletas y sin escritores · "Confirmar y facturar" oculto por decisión
del 2026-10-06.

## Riesgos de liberación

1. **Ninguno bloqueante.** `LP-042` y `LP-043` son del tooling de medición, con `impacto_produccion: NINGUNO` verificado en
   los dos casos.
2. **El invariante de `2.2` queda sin cobertura ejecutada** (no sin guarda): la guarda de `GuardarBorradorAsync` se verificó
   por lectura y por los 46 rechazos con mensaje de negocio, pero ningún escenario la ejercita con la confirmación ganando.
   Riesgo bajo, trazado en `LP-042`.
3. **La migración es aditiva pura y sin backfill**, y eso está bien, pero significa que la fila centinela de cada período
   nace con el primer escritor. Un período con cero movimientos cierra trivialmente cuadrado; no hay caso intermedio.
4. **La caché `_candadosVistos` no es una garantía y no hace falta que lo sea**: medido con la caché desactivada (M2c), el
   comportamiento es el mismo. Es rendimiento.

## Checklist de merge

- [x] Build de la solución: **0 errores / 9 advertencias** (`--no-incremental`), idéntico a la línea base declarada.
- [x] `tools/ArnesReconciliacionTx` **153/0** y `tools/ArnesSeisSitiosRestantes` **32/0**, exit 0, idempotentes, medidos en la ventana horaria que rompía.
- [x] Migración `20261007014129_EntregaCinco_CandadoPeriodoCaja` aplicada sobre base virgen: tabla + índice único correctos, aditiva pura, sin backfill.
- [x] Contraprueba por mutación de los dos fixes (M1n para `LP-037`, M4 + abortos forzados para `LP-041`), con la cantidad de afirmaciones evaluadas constante en todas las corridas.
- [x] No-regresión de `LP-039` y `LP-040` por los arneses, sin volver a medirlos enteros.
- [x] Repo del sistema **sin cambios** (`git status --porcelain` limpio). Fixtures `lp41rev` y `lp41vacia` y clon `C:/qa41` eliminados.
- [ ] `LP-042` y `LP-043` al Implementador (no bloquean el merge; no se cierran en esta corrida).

---

# `LP-040` — re-verificación de cierre (2026-10-06, rama `entrega-1-migracion`, commit `c5740c7`)

Lote de un solo defecto, el que esta memoria emitió en la ronda anterior sobre `f05cc92`. Contexto nuevo: el criterio
arrancó en **FAIL**; no se leyó la transcripción del implementador, sólo el diff, el mensaje de commit y la entrada
`LP-040` de `5-implementador.md`. Clon propio en `C:/qa040` (y `C:/qa040m` para los mutantes), fixtures propios
`laplatense_lp040rv` / `_arn` / `_mut` / `_recon` / `_ctl` / `_seis` (40 tablas, última migración
`20261006211007_EntregaCinco_VentaSinFacturaYComprobantesParciales`). **El repo del sistema no se tocó**
(`git status --porcelain` limpio al abrir y al cerrar). Sin migración EF en el fix.

## `LP-040`: **CERRADO**

**Nota metodológica obligatoria: el criterio de re-verificación que dejó la ronda anterior quedó inverificable y se
reescribió.** El parte pedía *"el POST se rechaza con un mensaje de negocio que nombra el comprobante y la venta sigue
en `Confirmada`"*. El fix no puso la guarda: **retiró el camino** — `FacturarAsync` dejó de emitir por su cuenta y pasó
a ser el atajo "facturar todo lo pendiente", que **delega** en `FacturacionParcialService.EmitirAsync`. Era la
alternativa que el propio parte declaraba *"válida y probablemente mejor, decisión del analista"*. Con eso, "rechazar"
dejó de ser el resultado correcto: lo correcto es **emitir por el pendiente**. El criterio se reescribe sobre el
invariante, que no cambió: *los mismos ítems no pueden quedar facturados por dos documentos*, y la `condicion_falla` del
catálogo (query de detección) tiene que dar **0 filas**.

| # | Criterio (reescrito) | Resultado | Evidencia observada |
|---|---|---|---|
| 1 | Venta facturada **en parte**: el atajo emite **un** comprobante por el **resto**, no por el total | **PASS** | Venta 2 (`Confirmada`, Subtotal 6.000 / IVA 840; comprobante #1 vivo por 1 u. del ítem 3 = neto 1.000 / IVA 210). `POST /Ventas/Facturar/2` → 302, en pantalla *"Comprobante registrado por $ 5.630,00."*. BD: comprobante **#2** nuevo, neto **5.000** / IVA **630**; líneas `(#2, ítem 3, 1,000)` y `(#2, ítem 4, 2,000)` = exactamente el pendiente. Entre los dos: neto 1.000+5.000 = **6.000** = `Subtotal`, IVA 210+630 = **840** = `TotalIVA`. Ningún ítem facturado dos veces |
| 2 | …la venta queda en `Facturada` y las **tres columnas obsoletas** en `NULL` | **PASS** | `Ventas` id 2: `Estado=2` (Facturada), `CAE=NULL`, `NumeroComprobante=NULL`, `VencimientoCAE=NULL`, `TipoComprobanteAfip=NULL`. El comprobante nace `Estado=1` (Pendiente), `DiferenciaIvaCobrada=0` |
| 3 | El **segundo** POST al atajo rechaza con *"ya está facturada por completo"*, **nunca** con un error de AFIP | **PASS** | `POST /Ventas/Facturar/2` otra vez → en pantalla *"Esta venta ya está facturada por completo en 2 comprobante(s): no queda ningún ítem pendiente de facturar."*. **0** ocurrencias de "AFIP no está configurado / falta el certificado" en el HTML servido. BD después: comprobantes siguen en **2**, `CAE` sigue `NULL` |
| 4 | Venta cobrada **sin factura**: el atajo la rechaza y deriva a "Facturar ítems", **sin tocar el importe** | **PASS** | Venta 3 (`Facturar=0`, Subtotal 6.000 / IVA **0,00** / Total 6.000). Botón **ausente** (`id="btnFacturar"` → 0 ocurrencias). `POST /Ventas/Facturar/3` → *"Esta venta se cobró sin factura: … Emitila desde \"Facturar ítems\", que muestra el importe exacto del cargo antes de confirmar."*. BD después: `Estado=4`, **`Total` 6.000 y `TotalIVA` 0,00 idénticos**, `CAE=NULL`, **0** comprobantes, **0** filas en `MovimientosCCCliente` (tabla entera en 0). El importe no se recalculó ni se posteó |
| 5 | La guarda cualitativa **no sobre-bloquea**: venta sin factura con todas las líneas al 0 % **sí** se factura | **PASS** | Medición propia, rama que el arnés no siembra: producto `QA040-004` con `PorcentajeIVA=0`, venta 8 (`Facturar=0`, 3.000 / IVA 0). `POST /Ventas/Facturar/8` → *"Comprobante registrado por $ 3.000,00."*; comprobante #6 con `Iva=0` y `DiferenciaIvaCobrada=0`, **0** movimientos de CC, columnas en `NULL`. La condición es "¿corresponde un cargo?", no "¿es sin factura?" |
| 6 | Venta `Confirmada` **sin comprobantes**: el atajo la factura entera (control negativo del parte) | **PASS** | Venta 4: `POST /Ventas/Facturar/4` → *"Comprobante registrado por $ 6.840,00."*. **Un** comprobante (#3) de neto 6.000 / IVA 840 = la venta exacta; líneas 2,000 y 2,000 = las cantidades vendidas; `Estado=2`, columnas en `NULL` |
| 7 | Estado derivado: `Facturada` sólo sin pendiente, `Facturada en parte` mientras quede | **PASS** | `POST /Ventas/Listar` (el JSON que pinta el badge): venta **5** `Confirmada` + `facturadaEnParte=true` (1 comprobante parcial) → badge *"Facturada en parte"*; ventas **2** y **4** `Facturada` + `facturadaEnParte=false`; venta **3** `Confirmada` + `false` (sin comprobantes). El detalle decide el botón con `PendienteDeFacturar`: presente con pendiente, **ausente** cuando llega a 0 |
| 8 | La tarjeta "Comprobante AFIP" del detalle ya no se dibuja vacía | **PASS** | `GET /Ventas/Details/2` con 1 comprobante, con 2, y `GET /Ventas/Details/4`: **0** ocurrencias de `Comprobante AFIP` y **0** de `(número )` en el HTML servido. Sigue habiendo tarjeta de **Comprobantes** (la del circuito 1:N) |
| 9 | El **barrido** que la `regla_preventiva` de `LP-039` pedía, ahora sí ejecutado | **PASS** | `grep` de **escrituras** a `.CAE =` / `.NumeroComprobante =` / `.VencimientoCAE =` / `.TipoComprobanteAfip =` en `Application`+`Infrastructure`+`Web`: **0 sitios** sobre `Venta` (los 2 hits son `OrdenCompra.NumeroComprobante`, otra entidad). Único escritor de `Estado = EstadoVenta.Facturada`: `FacturacionParcialService:348`. Las 8 lecturas restantes de `EstadoVenta.Facturada` son filtros de "venta cerrada" (dashboard, ABC, entregas, color del badge), ninguna es proxy de "tiene comprobante" |
| 10 | `condicion_falla` del catálogo: la query de detección devuelve 0 filas | **PASS** | `SELECT v.Id … FROM Ventas v JOIN ComprobantesAfip c … WHERE v.CAE IS NOT NULL GROUP BY v.Id` → **0 filas** sobre el fixture, después de 6 emisiones por los tres caminos (parcial, atajo, POS) |

## Los tres cambios de comportamiento: verificados como tales, no reportados como defectos

1. **El atajo rechaza la venta cobrada sin factura** → criterios 4 y 5. Verificado además que la condición es cualitativa
   y que el importe nunca se recalcula.
2. **El botón se renombró y dejó de depender de `afipConfigurado`, así que ahora se muestra** → `GET /Ventas/Details/2`
   sirve `id="btnFacturar"` con el texto *"Facturar todo lo pendiente"* **con AFIP apagado**, y el handler postea a
   `/Ventas/Facturar/2`. Antes estaba oculto. **No es una acción escondida que el servidor acepta: es lo contrario.**
3. **"Confirmar y facturar" del POS no se tocó** → `GET /Ventas/Editar/1`: `id="btnConfirmarYFacturar"` **0**
   ocurrencias (sólo queda su `<script>`), `id="btnConfirmar"` **1**. Sigue oculto por `afipConfigurado`, como se declaró.

## Máquina de estados del atajo (`FacturarAsync` ya no tiene guardas propias: las hereda de `EmitirAsync`)

Esto es lo que había que medir, porque el fix **retiró** las cuatro guardas de estado del método y las delegó.

| Desde | Transición | Esperado | Resultado |
|---|---|---|---|
| `Confirmada` sin comprobantes | facturar todo | emitir 1 comprobante por el total | **PASS** — venta 4 |
| `Confirmada` con comprobante parcial vivo | facturar todo | emitir 1 comprobante por el **pendiente** | **PASS** — venta 2 (era el `FAIL` de `LP-040`) |
| `Facturada` (sin pendiente) | facturar todo | rechazo de negocio, sin AFIP | **PASS** — *"ya está facturada por completo en 2 comprobante(s)"* |
| `Borrador` | facturar todo | rechazo | **PASS** — *"La venta todavía está en Borrador: hay que confirmarla antes de poder facturarla."*; `Estado=1`, 0 comprobantes |
| `Anulada` (cobrada con factura) | facturar todo | rechazo | **PASS** — *"La venta está anulada: no se puede facturar."*; `Estado=3`, 0 comprobantes, `CAE=NULL` |
| `Anulada` cobrada **sin** factura | facturar todo | rechazo | **PASS en el efecto, mensaje subóptimo** — rechaza y no escribe nada, pero el mensaje es el del cargo de IVA ("Emitila desde Facturar ítems") porque esa guarda corre **antes** que la de estado, que vive en `EmitirAsync`. Invita a una pantalla que va a rechazar igual. `trivial`, se declara, no se reporta como defecto |
| inexistente (id 9999) | facturar todo | rechazo | **PASS** — *"Venta no encontrada."* |

## Evidencia del implementador: verificada, no repetida

- Build `--no-incremental` del clon: **0 errores / 9 advertencias** = la línea base exacta (8 NU1902 + el CS0114 de
  `HomeController`).
- `tools/ArnesVentaSinFacturaYParcial` → **82 OK / 0 FALLADAS**, reproducido sobre fixture propio.
- **Los 5 mutantes corridos de nuevo, uno por uno, cada uno con su `git diff --stat` verificado antes de compilar.
  El mapa declarado se reproduce exacto:**

| Mutante | Resultado | Mata |
|---|---|---|
| **M1** — el método viejo entero (`git checkout f05cc92 -- VentaWorkflowService.cs`) | **64/18** | 8.2 8.3 8.4 8.5 8.6 8.7 8.9 8.10 8.11 8.12 8.13 8.14 8.15 8.17 8.19 8.20 8.22 8.23 — **y reproduce el parte textual**: 8.2/8.3 fallan con *"AFIP no esta configurado: falta el certificado (.p12)"* |
| **M2** — `Cantidad = i.Cantidad` (facturar el total, no el pendiente) | **74/8** | 8.2 8.4 8.5 8.6 8.7 8.9 8.10 8.11 |
| **M3** — el atajo vuelve a escribir las columnas obsoletas | **79/3** | 8.8 8.15 8.23 |
| **M4** — sin la guarda de "nada pendiente" (`if (false)`) | **81/1** | 8.10, degradado a *"Hay que indicar al menos un ítem con cantidad a facturar."* |
| **M5** — guarda de `D-CR01.1` fuera + el atajo calcula y confirma el cargo solo | **80/2** | 8.17 8.18 |

- **La declaración de no-cobertura del implementador NO es fiel, y el error va para el lado seguro.** Dice que
  *"sobreviven a los cinco la precondición 8.1 y tres controles de daño colateral, **8.16 / 8.18 / 8.21**"*, pero su
  propio mapa de mutación dice que **M5 mata 8.17 y 8.18**. Medido acá: **sobreviven a los cinco exactamente tres**
  afirmaciones — **8.1** (precondición), **8.16** y **8.21** (daño colateral). **8.18 es cobertura real**: M5 la mata
  (`comprobantes=1, cargos de IVA=1`, esperado 0 y 0). O sea el documento **subdeclara** su cobertura: no hay ninguna
  afirmación contada como cobertura que no lo sea, que es lo que importaría. Se corrige en el registro, severidad
  `trivial`, sin parte.
- **La falla propia que reportó (8.9 indexaba sin verificar el `Count`) está corregida y la corrección se midió:** el
  guard `comprobantes.Count == 2 ? comprobantes[1] : null` está puesto, y **los cinco mutantes evaluaron las 82
  afirmaciones completas** (64+18, 74+8, 79+3, 81+1, 80+2) — ninguno murió ni dejó afirmaciones sin ejecutar, con M1
  (que no emite nada) como peor caso. Barrido del patrón hermano en el arnés: los otros indexados (`cs[0]` en 8.14 y
  8.23) están cortocircuitados por `cs.Count == 1 &&`, y `movimientos[0]` de 3.4–3.6 está dentro de
  `if (movimientos.Count == 1)` con 3.3 fallando ruidosamente si no — **no queda otro indexado capaz de matar el arnés**.

## Defecto nuevo: `LP-041` (`minor`) — el commit rompe `ArnesReconciliacionTx`, y lo rompe muriendo en vez de medir

**No es el sistema: es el instrumento que mide el sistema**, y es el gate de no-regresión de la familia de atomicidad
que esta memoria viene citando como "153 OK / 0". Medido con control positivo en los dos commits, fixtures separados:

| | `f05cc92` (control, antes del fix) | `c5740c7` (el fix) |
|---|---|---|
| `ArnesReconciliacionTx` | **147 OK / 6 FALLADAS**, sin crash | **142 OK / 10 FALLADAS + crash** |

El delta son **+4 afirmaciones falladas y el crash**, y los dos salen de `LP-040`:

1. **4 afirmaciones quedaron obsoletas, no rotas:** `5.2/N=3`, `5.4/N=3`, `5.2/N=8`, `5.4/N=8` afirman
   *"AFIP invocado UNA sola vez"* (→ `0 invocacion(es)`) y *"un solo CAE persistido"* (→ `(vacio)`). Es exactamente lo
   que el fix retiró a propósito: el atajo ya no llama a AFIP ni escribe `Venta.CAE`. El arnés sigue afirmando un
   contrato que se dio de baja.
2. **El crash, que es la parte grave:** `LimpiarAsync` de ese arnés borra `ItemsVenta` **sin borrar antes**
   `ComprobantesAfipItems`. Antes del fix, `FacturarAsync` con AFIP apagado **nunca** creaba un `ComprobanteAfip`, así
   que la FK nunca se poblaba; ahora sí, y la limpieza muere con
   `FK_ComprobantesAfipItems_ItemsVenta_ItemVentaId … ON DELETE RESTRICT`. **La segunda corrida es peor que la primera:**
   el crash se corre a la limpieza *inicial* y el arnés termina con **0 OK / 0 FALLADAS** y `exit 127` — un arnés que no
   mide nada y no imprime ninguna falla. Reproducido: primera corrida 142/10, segunda 0/0.

Las 6 fallas del control (`16.0`/`16.1`/`16.2` en N=3 y N=8, *"La fecha del movimiento no puede ser futura"*) **ya están
en `f05cc92`**: son del entorno (reloj/huso en la ventana nocturna), **no de este commit**, y por eso el "153 OK / 0"
declarado no se reproduce en ninguno de los dos. Queda anotado como ruido conocido del instrumento, no como defecto.

**Barrido del mismo patrón en los demás arneses:** `ArnesSeisSitiosRestantes` tiene la misma limpieza incompleta pero
**no** llama a `FacturarAsync`/`ConfirmarYFacturarAsync`, así que hoy no crea comprobantes y no rompe (verificado:
**20 OK / 2 FALLADAS**, sin crash, `LP-037` igual que antes). Es riesgo latente. `ArnesVentaSinFacturaYParcial` sí borra
los comprobantes primero: el implementador arregló su propio arnés y no el hermano.

**Sin impacto en producción:** `grep` de borrados físicos de `ItemsVenta` en `Application`+`Infrastructure`+`Web` →
**ninguno** (los dos `RemoveRange` que hay son de `Notifications` y `OrdenCompraItems`). El sistema usa soft delete, así
que la FK `RESTRICT` no se alcanza por ningún camino de la app.

## No-regresión

| Qué | Resultado | Evidencia |
|---|---|---|
| **`LP-039` sigue cerrado — las dos puntas** | **PASS** | Vista: `GET /Ventas/Details/2` (Facturada, 2 comprobantes vivos) sirve **0** `id="btnAnular"`; control positivo venta 3 (Confirmada, 0 comprobantes) sirve **1**. POST directo: `POST /Ventas/Anular id=2` → *"La venta #2 tiene 2 comprobante(s) fiscal(es) asociado(s) sin dar de baja (interno #1 (sin número de AFIP asignado, Pendiente) por $ 1.210,00; interno #2 … por $ 5.630,00): anularla requiere emitir una nota de crédito electrónica…"* — los dos listados con su importe real, **ningún paréntesis vacío**. BD: `Estado=2`, `FechaAnulacion NULL`, **0** reversiones de caja |
| **Anulación legítima (sin comprobantes) con su reversión** | **PASS** | Venta 3 anulada **por HTTP**: *"Venta #3 anulada correctamente. Se devolvió el stock de 2 ítem(s), se revirtieron $ 6.000,00 en caja."* BD: `Estado=3`, motivo persistido, stock de los productos 1 y 2 **992 → 994** cada uno (+2 = la cantidad exacta), caja con `Tipo=1 $6.000` + `Tipo=2 $6.000 EsReversion=1` → **neto cero** |
| **Circuito de CR-02 intacto, con su cargo de IVA** | **PASS** | Venta 7 (`Facturar=0`, 6.000 / IVA 0). Control negativo primero: emitir confirmando `DiferenciaIvaACobrar=0` → HTTP 200 y rechazo *"El cargo de IVA … cambió mientras confirmabas: ahora es $ 840,00. Volvé a abrir la pantalla…"*, con **0** comprobantes y **0** filas de CC. Con el importe correcto (840): *"Comprobante registrado por $ 6.840,00. Se cargaron $ 840,00 de IVA en la cuenta corriente de QA040 Cliente CF."*; comprobante #5 neto 6.000 / IVA 840 / `DiferenciaIvaCobrada=840`; **1** fila de CC `Tipo=Debito`, `Importe=840,00`, `Referencia="IVA de la factura #5 sobre la venta #7 (cobrada sin IVA)"`; la venta **no se recalculó** (`Subtotal` 6.000 / `TotalIVA` 0,00 / `Total` 6.000) |
| **`LP-037` sigue ABIERTO y medido, sin cambio** | **PASS** | `tools/ArnesSeisSitiosRestantes` → **20 OK / 2 FALLADAS** (`3.2/N=3` y `3.2/N=8`, el invariante del arqueo firmado). Idéntico a lo declarado; no es regresión de esta ronda |
| **Las 59 afirmaciones previas del arnés de CR-01/CR-02** | **PASS** | Incluidas en el 82/0 reproducido |
| **`ArnesReconciliacionTx`** | **FAIL → `LP-041`** | 142/10 + crash contra 147/6 del control |

## Reglas nuevas/modificadas desde la última corrida

`6-qa.md` declaraba **2026-10-06** (hoy, puesta por el lote anterior). Diferencial
`git log --since=2026-10-06 -- .github/instructions/32-estandares-qa-implementador.instructions.md docs/qa/regresiones-manuales.yml`
→ **0 commits** (el último que tocó el YAML es `14eb845`, del 2026-10-06 pero anterior a la corrida; lo que hay sin
commitear son los items `LP-039`/`LP-040` que esta misma memoria escribió). **Ninguna regla nueva ni modificada.**

## Cobertura del catálogo cross-proyecto

| id | aplica | resultado | acción |
|---|---|---|---|
| `LP-040` | sí | **PASS — CERRADO** | `fix_aplicado` escrito con la evidencia de esta corrida y con el criterio reescrito |
| `LP-039` | sí (no-regresión) | **PASS** | Sigue cerrado por las dos puntas |
| `LP-041` | sí (nuevo) | **FAIL** | Catalogado hoy; parte emitido |
| `LP-034` (`Include` + query filter global = INNER JOIN) | sí | **PASS** | El método nuevo no agrega ninguna consulta con `Include` sobre comprobantes; delega. El `Include` que queda es el de `Venta` para el mapeo, que no cruza el filtro |
| `LP-035` (orden de locks: lectura común después de los locks) | sí | **PASS** | `FacturarAsync` dejó de abrir transacción propia: las lecturas pasan afuera y el único lock vive en `EmitirAsync`. Medido donde importa: 8.19–8.21 con 3 atajos simultáneos → **1 ganador, 1 comprobante**, nada facturado de más, ningún rechazo por excepción cruda |
| `LP-018` (dos POST simultáneos emitían dos comprobantes) | sí | **PASS** | La concurrencia del atajo se heredó, no se reescribió: 8.19/8.20 con N=3. Y el lock ya **no** se sostiene durante el round-trip de AFIP, que era el costo declarado del método viejo |
| `LP-037` (cierre de caja con escritores concurrentes) | sí | **ABIERTO, re-medido sin cambio** | 20/2. Espera decisión de Joaquín |

## Riesgos de liberación y mitigaciones

1. **El riesgo fiscal de la familia CR-02 queda cerrado.** `LP-039` cierra la anulación, `LP-040` cierra la emisión, y
   lo que los cerró de verdad es que **hoy existe un solo modelo del documento fiscal**: nadie escribe
   `Venta.CAE`/`NumeroComprobante`/`VencimientoCAE` (verificado por barrido) y un solo método pone `Facturada`. **Ya no
   hace falta esperar a tener AFIP apagado para estar a salvo**, que era la mitigación anterior.
2. **Las tres columnas obsoletas siguen en la tabla, sin uso.** Es decisión de arquitectura declarada (dejar camino de
   vuelta). Riesgo residual: un reporte futuro que las lea va a leer `NULL` en toda venta nueva. Mitigación: la query de
   detección del catálogo (`v.CAE IS NOT NULL` + comprobantes vivos) sirve también como centinela de que nadie volvió a
   escribirlas; dejarla en la pasada de QA de la Entrega 5.
3. **`LP-041` no bloquea el merge pero bloquea la próxima medición.** Mientras `ArnesReconciliacionTx` no se arregle, el
   gate de atomicidad del proyecto **no se puede correr dos veces seguidas** y la segunda corrida devuelve 0/0 con exit
   distinto de 0. Mitigación inmediata: recrear la base entre corridas; mitigación real, el parte.
4. **`LP-037` sigue abierto** y esperando decisión.
5. **No hay nota de crédito ni baja de comprobante** (módulo 16, Entrega 5), y `AnulacionVentaViewModel` /
   `IAnulacionVentaService` siguen superados por el modelo 1:N — hay que rediseñarlos antes del módulo 16.
6. **AFIP sigue apagado y la emisión real nunca se probó de punta a punta.** Todos los comprobantes nacen en
   `Pendiente`. El día que llegue el `.p12`, la llamada se escribe en **un** lugar (`ComprobanteAfip`) y los dos caminos
   la heredan — eso es lo que este commit compró, pero todavía hay que probarlo.

## Partes de defecto

- **`LP-040`** → **CERRADO**. `fix_aplicado` escrito en el catálogo. Con esto **se cierra la familia de defectos que
  abrió CR-02** y la Entrega 5 queda habilitada para arrancar: la condición que ponía el parte anterior
  (*"la Entrega 5 no debería habilitar AFIP sin cerrar antes `LP-040`"*) está satisfecha.
- **`LP-041`** (`minor`, catalogado hoy) — parte emitido al Implementador.
  `archivos_fix` sugeridos (**hipótesis, no instrucción cerrada**): `tools/ArnesReconciliacionTx/Program.cs`
  (`LimpiarAsync`: borrar `ComprobantesAfipItems` y `ComprobantesAfip` **antes** de `ItemsVenta`, igual que ya hace
  `ArnesVentaSinFacturaYParcial`; y las afirmaciones 5.2/5.4 tienen que medir el contrato nuevo —*un* comprobante con
  sus líneas— en vez de "AFIP invocado una vez" y "un CAE persistido") y el mismo barrido preventivo en
  `tools/ArnesSeisSitiosRestantes/Program.cs`, que hoy no rompe por casualidad. Sin migración EF.
  **Criterio de re-verificación (arranca en FAIL):** `ArnesReconciliacionTx` corre **dos veces seguidas sobre la misma
  base** sin crash y sin que el total de afirmaciones evaluadas baje, con la misma cuenta en las dos corridas; las 4
  afirmaciones de concurrencia de la emisión miden el comprobante y no el CAE; y se declara explícitamente qué pasa con
  las 6 fallas del grupo 16 (si eran del reloj, el arnés tiene que dejar de depender de él o decir que depende).

## Pruebas mínimas ejecutadas

1. Las 6 pruebas de navegador que pedía `5-implementador.md`, por HTTP real con cookie jar (ver criterios 1–8).
2. Las 7 transiciones del atajo, incluidas las 4 inválidas que el fix **dejó de guardar** y delegó.
3. Los 5 mutantes, cada uno con `git diff --stat` verificado antes de compilar, y la cuenta de afirmaciones evaluadas
   controlada en los 5 (82 en todos).
4. `ArnesVentaSinFacturaYParcial` 82/0, `ArnesSeisSitiosRestantes` 20/2, `ArnesReconciliacionTx` 142/10 **más su control
   positivo en `f05cc92`** (147/6) — que es lo único que permitió separar las 4 fallas nuevas de las 6 preexistentes.
5. Barrido de escrituras a las columnas obsoletas y de `EstadoVenta.Facturada` como proxy, una ocurrencia por vez.
6. Query de detección del catálogo sobre el fixture después de 6 emisiones por los tres caminos.
7. Dos ramas que el arnés no siembra: la venta sin factura con **todas** las líneas al 0 % de IVA, y el rechazo del
   cargo de IVA con el importe mal confirmado.

## Checklist de salida para merge

- [x] `LP-040` corregido y re-verificado en contexto nuevo, con las dos puntas (vista y POST directo)
- [x] Criterio de re-verificación reescrito y declarado (el del parte anterior quedó inverificable por el cambio de diseño)
- [x] El barrido de la `regla_preventiva` de `LP-039` ejecutado y verificado: **0** escritores de las columnas obsoletas
- [x] Las 23 afirmaciones nuevas medidas por los 5 mutantes, con el mapa reproducido exacto
- [x] Declaración de no-cobertura corregida: sobreviven **3**, no 4 (8.18 es cobertura real, la mata M5)
- [x] Ningún mutante mató el arnés: 82 afirmaciones evaluadas en las 5 corridas
- [x] No-regresión de `LP-039`, de la anulación legítima y del circuito de CR-02 con su cargo de IVA, por HTTP
- [x] Build `--no-incremental` 0 errores / 9 advertencias = línea base
- [x] `git status --porcelain` limpio en el repo del sistema bajo prueba
- [ ] **`LP-041` corregido y re-verificado** ← no bloquea el merge; bloquea la próxima medición de atomicidad
- [ ] `LP-037` con decisión de Joaquín

**Veredicto del lote: `LP-040` CERRADO.** El commit `c5740c7` es mergeable tal como está. **La familia de defectos que
abrió CR-02 queda cerrada y la Entrega 5 queda habilitada para arrancar.** `LP-041` es del instrumento, no del sistema:
no condiciona la liberación, condiciona la próxima corrida de QA.

---


