# Historial de QA - La Platense

Bloque archivado desde `6-qa.md` el 2026-10-08 por curaduria a mano (39 seccion 6: el techo se sostiene archivando, no reescribiendo). El texto esta completo y sin resumir.

---

# Módulo 16 — notas de crédito por comprobante — QA lote único financiero-fiscal (2026-10-07, rama `entrega-1-migracion`, commits `c5538d3`..`1116cdf` sobre `fcfa077`)

## **GO para merge, con 1 defecto `major` abierto que no bloquea el merge pero sí es condición para el deploy del módulo 16.** Los 12 criterios del lote en PASS con evidencia ejecutada. **El barrido de los lectores del "ya facturado" está COMPLETO** (4 lectores, los 4 con filtro, 3 de ellos medidos por mutación). **El relabel de las cinco etiquetas es CORRECTO** — auditado con 13 mutantes independientes. **La limitación declarada sobre la rama proporcional es HONESTA y verificada** — pero acota de menos: la cota tampoco es medible. 3 defectos nuevos: `LP-052` `major` (código), `LP-053` `low` y `LP-054` `low` (los dos de tooling de QA).


## Cómo se corrió (y la caída declarada)

**Playwright MCP NO estaba disponible en la sesión**: `ToolSearch` con `select:mcp__playwright__*` no devuelve ninguna herramienta. Caída declarada al procedimiento por HTTP de `33-verificacion-automatizada-qa`: app levantada localmente en `https://localhost:5443` sobre la base desechable `lp_qasmoke`, login real por POST a `/Account/Login` con antiforgery, y los asserts hechos sobre el HTML servido y sobre la BD. Todo el smoke por pantalla de este bloque salió por ahí.

- **Base de prueba propia**: `lp_qasmoke` (fixture para el smoke) y `lp_qanc16` (mutación), creadas con `dotnet ef database update` → **19 migraciones**. Más `lpq_echeqs`, `lpq_tarjetas`, `lpq_seis`, `lpq_recon` para la no-regresión.
- **`laplatense_dev` NO se tocó y queda verificada como control**: 18 migraciones, y `SELECT COUNT(*) FROM information_schema.columns WHERE table_name='ComprobantesAfip' AND column_name='ComprobanteAsociadoId'` = **0**. Producción no se tocó.
- **Build**: `dotnet build --no-incremental` → **0 errores / 9 advertencias** (8 NU1902 + el CS0114 de `HomeController`). Línea base exacta. Confirmado el dato del brief: el build incremental esconde una.
- **La mutación se hizo sobre una COPIA del árbol** (`git archive 1116cdf | tar -x` al scratchpad, `md5sum` idéntico al original), nunca sobre el repo. Driver con falla-cerrado: si el patrón no aparece exactamente 1 vez, o el árbol mutado no compila, no corre y lo declara.
- **`git status --porcelain` del repo del sistema al cerrar**: solo `?? .claude/`, que ya estaba al arrancar la corrida. **Ningún cambio de QA.**

## Cobertura por criterio de aceptación

| # | Criterio | Resultado | Evidencia observada |
|---|---|---|---|
| 1 | Los códigos de AFIP son los reales: `NotaCreditoA = 3`, `NotaCreditoB = 8` | **PASS** | Arnés 6.1/6.2 `[DISCRIMINA]`: `factura=6 (B=6) nota de credito=8`, `factura=1 (A=1) nota de credito=3`. En BD: filas de tipo `3` y `8`. Confrontado contra `34-integracion-afip-arca.instructions.md` (1=FA, 2=NDA, 3=NCA, 6=FB, 7=NDB, 8=NCB): **correctos**. Mutante M8 (`NotaCreditoA = 2`, correlativo) **tumba 6.2 y solo 6.2** |
| 2 | Una NC sobre un comprobante con `DiferenciaIvaCobrada > 0` postea el crédito proporcional en la CC, en la misma transacción | **PASS** | Arnés 3.1/3.2/3.3/3.4 `[DISCRIMINA]`: 1 movimiento con `Origen=6`, `Tipo=Credito`, importe `21,00`, referencia `"Devolución del IVA de la factura #1 por la nota de crédito #2 (venta #1)"`. En BD, 5 movimientos `Origen=6`. Atomicidad: arnés 8.1 inyecta un trigger que aborta el INSERT del movimiento → **0 NC y 0 movimientos**; 8.2, sacado el trigger, la misma emisión pasa |
| 3 | **La NC que cierra el comprobante deja el saldo de la CC en `0,00` exacto — el centavo** | **PASS** | Arnés 3.6 `[DISCRIMINA]`: `devolvio=1302,01 mientras su IVA es 1302,00`. 3.7: `saldo de la CC = 0,00`. 3.8: `devuelto=1323,01 cargo=1323,01`. **Confirmado en BD, que es la evidencia más dura**: comprobante `#3` tiene `Iva = 1302.00` y `DiferenciaIvaCobrada = 1302.01`. El centavo existe y es el remanente. Mutante M1 (remanente→proporcional) tumba 3.5/3.7/3.8 y deja 3.6 SIN MEDIR |
| 4 | **R18** — el pendiente de facturar es idéntico antes y después de la NC | **PASS** | Arnés 4.2/4.3 `[DISCRIMINA]`: `antes=2,000 despues=2,000` en los dos lectores. **Y en pantalla, con el caso más duro que el arnés**: venta 3 vendió 5, el comprobante `#6` facturó 3, y le emití **dos** NC (`#7` por 2 y `#15` por 1 = el comprobante entero acreditado). `GET /FacturacionParcial/Emitir/3` sigue mostrando `vendida 5 / ya facturada 3 / pendiente 2`. Sin el filtro la suma sería 3+2+1=6 sobre una venta de 5 → pendiente **−1** |
| 5 | **R18** — el badge "Facturada en parte" del listado, idéntico antes y después | **PASS** | Arnés 4.4 `[DISCRIMINA]`: `antes=True despues=True`. **Y por HTTP**: `POST /Ventas/Listar` devuelve para la venta 3 `{estado: 'Confirmada', facturadaEnParte: true}` con sus dos NC vivas. Mutante M4 (listado paginado sin filtro) **tumba 4.4 y solo 4.4** |
| 6 | **R19** — `Facturada` no vuelve a `Facturada en parte` | **PASS** | Arnés 4.5/4.6 `[DISCRIMINA]`: `antes=Confirmada despues=Confirmada`; venta acreditada por completo `estado=Facturada enParte=False pendiente=0`. Por HTTP: venta 1 (facturada y acreditada entera) → `{estado: 'Facturada', facturadaEnParte: false}` |
| 7 | El tope por ítem se mide contra lo que **ese comprobante** facturó, no contra la venta | **PASS** | Arnés 5.1/5.2 `[DISCRIMINA]`: rechazo `"este comprobante facturó 3 y quedan 1 por acreditar; se pidieron 2"` — nombra el pendiente real (1), no lo facturado (3). 5.3: `PendienteDeAcreditar` (lo que decide el botón) = el mismo número que el tope. **Y el caso que lo separa de la venta, medido por HTTP**: con `#6` en 3/3 acreditadas y la **venta** todavía con 2 unidades sin facturar, el POST se rechaza con `"Este comprobante ya está acreditado por completo con notas de crédito"` |
| 8 | Rechazo de una NC sobre una NC | **PASS** | Arnés 5.4 `[DISCRIMINA]`. **Y por HTTP**: `POST` con `ComprobanteId=5` (que es una NC) → `"El comprobante interno #5 ya es una nota de crédito... hace falta una nota de débito, que todavía no está implementada."` Mutante M9 **tumba 5.4 y solo 5.4**. **Pero el GET de esa pantalla abre igual → `LP-052`** |
| 9 | Rechazo de una NC sobre un comprobante en `Error` | **PASS** | **Este criterio el arnés NO lo cubre** (mutante M11 sobrevive con 45/45; `grep EstadoComprobanteAfip.Error` sobre el arnés da 0 hits). Verificado por mí por HTTP, con par discriminante: `#6` a `Estado=3` → POST rechazado con `"quedó en Error y nunca se emitió ante AFIP"` y **0 filas nuevas**; `#6` de vuelta a `Pendiente` → el **mismo** POST pasa (`"Nota de crédito B registrada por $ 1.210,00"`, NC de `#6` de 1→2). El estado era lo único que frenaba. **El GET abre igual → `LP-052`** |
| 10 | El precio de los ítems de la NC es el **efectivo**, no el de lista | **PASS** | Arnés 2.1 `[DISCRIMINA]`: `NC ofrece 900,00 / lista del item = 1000,00`. 2.6 `[DISCRIMINA]`: la línea con descuento **y** recargo lleva 900. **En BD, las tres líneas de la venta 1**: `ItemVenta.PrecioUnitario` 1000 / 2000 / 100,01 vs `ComprobanteAfipItem.PrecioUnitario` **900 / 2400 / 100,01**. Descuento y recargo en las dos direcciones |
| 11 | El detalle de la venta rotula la NC como NC y no como factura | **PASS** | `GET /Ventas/Details/1`: tarjeta "Comprobantes emitidos" con fila `1 → Factura B` y filas `2` y `3` → `↳ Nota de crédito B` en itálica, con el Motivo como sublínea. Exactamente 1 `Factura B` y 2 `Nota de crédito B`. `GET /Ventas/Details/2`: `['Factura A', 'Nota de crédito A']`. El ternario viejo habría impreso "Factura B" en las tres |
| 12 | **El hallazgo del implementador**: el título "Ya facturado de esta venta" dejó de ser falso | **PASS** | `GET /FacturacionParcial/Emitir/3` con la venta 3 teniendo factura `#6` + NC `#7` + NC `#15`: la tarjeta lista **solo `#6`**. El título volvió a ser cierto. **No se corrigió en la vista** (`FacturacionParcial/Emitir.cshtml` no está en el diff y la línea 88 sigue igual) sino en `ListarComprobantesAsync`, que ahora filtra `ComprobanteAsociadoId == null` — es la corrección correcta: lo que mentía era el contenido, no el rótulo. **Pero no tiene cobertura en el arnés → `LP-053`** |

## Veredicto sobre el barrido de los lectores del "ya facturado" (lo que el brief pidió confirmar)

**El barrido está COMPLETO. No quedó un cuarto lector sin filtro — hay cuatro, y los cuatro lo llevan.** El commit `c5538d3` habla de "los tres lectores"; el cuarto lo agregó `1116cdf` y es el del título. Enumerados por `grep` sobre todo el árbol (`Set<ComprobanteAfip>()` aparece en exactamente 3 archivos, y la navegación `Venta.Comprobantes` en 1 más):

| # | Lector | Línea | Filtro | Mutante que lo mide |
|---|---|---|---|---|
| 1 | `FacturacionParcialService.ObtenerYaFacturadoPorItemAsync` | `:406` | sí | **M5 → tumba 4.3** |
| 2 | `FacturacionParcialService.ListarComprobantesAsync` | `:422` | sí | **M7 → NINGUNA (`LP-053`)** |
| 3 | `VentaWorkflowService.ObtenerPaginadoAsync` (badge) | `:162` | sí | **M4 → tumba 4.4** |
| 4 | `VentaWorkflowService.ObtenerDetalleAsync` | `:1701` | sí | **M6 → tumba 4.2 y 4.6** |

Dos cosas más que miré y están bien, declaradas para que no se vuelvan a revisar:

- **`TieneComprobantes` (`:158`) NO lleva el filtro, y es correcto.** Decide "¿esta venta tiene algún documento fiscal vivo?", y una NC lo es. Está escrito en el código y coincide con la guarda de `AnularAsync`.
- **`VentaWorkflowService:1054`, `facturable.Comprobantes.Count`** — es un quinto consumidor, usado solo para el mensaje "ya está facturada por completo en N comprobante(s)". Queda bien **por carambola**: se alimenta de `ListarComprobantesAsync`, que ahora filtra. Si alguien revierte el filtro del lector 2, ese mensaje empieza a contar las NC como facturas, y **ningún arnés lo ve**.

## Veredicto sobre el relabel de las cinco etiquetas

**Las cinco están BIEN. El implementador se corrigió en la dirección correcta en los cinco casos.** Auditado con **13 mutantes independientes derivados del diff** (no de la lista de afirmaciones), cada uno con build verificado y base reseteada, más un control negativo semánticamente nulo que dio **cero tumbadas**:

| Relabel declarado | Veredicto | Cómo lo medí |
|---|---|---|
| `2.4` bajó a `[COBERTURA]` (no discriminaba el precio) | **CORRECTO** | Estructural y verificable: `2.4` lee la línea del producto C, y el arnés 1.2 + la BD muestran que para C lista = efectivo = `100,01`. Ninguna mutación lista-vs-efectivo puede moverla. `2.6`, agregada en el relabel, sí discrimina (900 vs 1000) |
| `4.4` seguía `[DISCRIMINA]` con el fixture arreglado a facturación parcial | **CORRECTO** | **M4** (listado sin filtro) **tumba 4.4 y solo 4.4**. Con el fixture viejo (venta completa) el badge quedaba apagado en los dos mundos; con 5 vendidas / 3 facturadas / 2 acreditadas, no |
| `5.7` pasaba por el motivo equivocado (el tope, no el eco) | **CORRECTO** | Evidencia directa en la corrida: el rechazo de `5.7` es `"La devolución de IVA... cambió mientras confirmabas: ahora es $ 21,00"` — el eco, no el tope. Y **M10** (eco neutralizado) **tumba 5.7 y solo 5.7** |
| `5.9` bajó a `[COBERTURA]` (control positivo, ningún mutante de defecto la mata) | **CORRECTO** | Bajo **M10**, que es el mutante del mecanismo que `5.9` controla, `5.9` **sobrevive** — que es exactamente lo que tiene que hacer un control positivo |
| `1.3` subió a `[DISCRIMINA]` | **CORRECTO con matiz declarado** | **M13** (el IVA por línea truncado en vez de redondeado) hace que la corrida muera con `exit=3` y `"LA CORRIDA NO ES VALIDA"` antes de llegar a `1.3`: el importe del cargo **está clavado** y no hay falso verde, pero la mutación se detecta por el eco del fixture, no por la assertion `1.3` misma. No es un defecto; es que el mecanismo de detección no es el que la etiqueta sugiere |

**Lo que el relabel no alcanzó, y es el hallazgo propio de esta corrida:** la declaración "**21 mutantes con cero sobrevivientes**" es cierta para el conjunto del autor y **falsa como medida de cobertura del cambio**. Mis 13 mutantes encontraron **tres sobrevivientes** (detalle en `LP-053`), y los tres caen en lugares de los que uno no sospecharía: el filtro que el propio commit presenta como su hallazgo, una guarda que `R17` exige, y una cota que la declaración de limitaciones nombra entre lo medido.

## Veredicto sobre la limitación declarada de la rama proporcional

**Es HONESTA y la verifiqué: reemplazar la rama proporcional entera por "devolver el IVA de la NC tal cual" (guardas intactas) deja el arnés en 45 OK / 0 FALLADAS.** Indistinguible, tal como el arnés lo declara. La razón que da también es correcta y la medí: hoy `DiferenciaIvaCobrada == Iva` siempre, así que `round(cargo × ivaNC / ivaCbte) = ivaNC`.

**Pero la declaración acota de menos, y eso sí es un hueco:** dice "lo que SÍ se mide son la COTA (M15) y el REMANENTE". **El remanente sí se mide** (M1 lo tumba). **La cota NO**: sacar el `Math.Min(proporcional, remanente)` entero deja **45 OK / 0 FALLADAS**. Y el motivo es el **mismo invariante** que desactiva la rama proporcional — con cargo = IVA, `proporcional` nunca excede el remanente, así que el `Min` no llega a morder, y encima la rama de `acreditaTodoLoQueQueda` atrapa primero a la NC que cierra. Control que confirma que la línea no es código muerto: `Math.Min(proporcional * 2m, remanente)` tumba **11** afirmaciones.

**Sí hay forma de cubrirla**, y es la que el propio brief sugiere: sembrar `ComprobanteAfip.DiferenciaIvaCobrada` a mano por debajo de `Iva`. La columna es escribible aunque los servicios reales no produzcan hoy ese estado, y con `cargo < IVA` las dos ramas (proporcional y cota) se vuelven distinguibles. Queda como `expectativa` de `LP-053`.

## Cobertura del catálogo cross-proyecto

| id | aplica | resultado | acción |
|---|---|---|---|
| `LP-002` (valor de enum nuevo sin propagar a todos sus lectores) | sí | **PASS** | Las dos puntas de `OrigenMovimientoCC.DevolucionDiferenciaIva = 6` verificadas en el HTML servido de `/Clientes/CuentaCorriente/1`: el combo `fOrigen` trae la opción `"Devolución de IVA por nota de crédito"` y el mapa JS `etiquetasOrigen` trae `DevolucionDiferenciaIva`. Para `TipoComprobanteAfip`, los 3 lectores vía `TipoLegible` (con rama `_ =>`) — verificado en pantalla en los criterios 11 y 12 |
| `LP-039` / `LP-040` (un criterio que vive en una sola punta) | sí | **FAIL** | **Tercera recurrencia: `LP-052`.** El botón de `Details.cshtml:368` guarda 3 condiciones y el GET de `NotasCreditoController:44` guarda 1. El agravante nuevo: hay guarda, pero no la misma — un chequeo de "el GET tiene guarda" da verde |
| `LP-034` (`Include` sobre navegación requerida de una `SoftDestroyable`) | sí | **PASS** | `grep` sobre `NotaCreditoService.cs`: no hay `Include(c => c.Venta)` ni `ThenInclude(ci => ci.ItemVenta)`; los rótulos salen aparte con `IgnoreQueryFilters`. Los dos filtros de soft delete están en las dos puntas de `PendienteDeAcreditar` (padre e hijas) |
| `LP-035` (lecturas comunes dentro de la transacción) | sí | **PASS** | Nombres de producto y cliente se leen antes de abrir la transacción (`NotaCreditoService:180-181`); el tope y el IVA ya devuelto se releen **con** el lock tomado |
| `LP-018` / `PAT-059` (concurrencia del tope) | sí | **PASS** | Arnés 7.1/7.2/7.3 `[DISCRIMINA]`: 3 NC simultáneas por 3 unidades acreditan **3 en total, no 9**; `devuelto=630,00` contra `cargo original=630,00`; saldo final `63,01` (nunca a favor). Contado en **filas de la BD**, no en respuestas |
| `LP-050` (migración con backfill heurístico probado contra filas en cero) | sí | **N/A — no aplica, verificado** | La migración `20261007132638` es aditiva pura, operación por operación: 2 `AddColumn` nullable, 1 `CreateIndex`, 1 `AddForeignKey` (`Restrict`). **Cero `Sql()`, cero `InsertData`, cero `AlterColumn`, cero `DropColumn`.** `Down` simétrico. No hay backfill que pueda estar mal clasificando filas preexistentes |
| `LP-044` / `LP-045` / `LP-051` (comentario que afirma algo falso) | sí | **PASS** | El barrido pasada 3 del implementador corrigió el comentario de `AfipService.MapearCondicionIvaReceptor` (decía que el `or 3` era preventivo "porque el enum no tiene notas de crédito" — su propio commit anterior lo volvió falso). Verificado que el **código** no cambió, solo el comentario: `request.TipoComprobante is 1 or 3 ? 1 : 5` |
| `LP-046` / `LP-048` / `LP-049` (tooling de QA: matriz desactualizada, precondición que solo vale sobre base virgen) | sí | **FAIL** | **`LP-053` y `LP-054`**, los dos de esta familia. `LP-054` lo cometí yo en esta corrida |
| `LP-047` (baja lógica que vive solo en el combo) | sí | **N/A** | El módulo 16 no agrega catálogos ni combos de entidades con `Activo` |
| `MH-001` / `CRM-0xx` (otros proyectos) | no | N/A | Sin módulo equivalente en el alcance del lote |

## Cobertura de reglas nuevas/modificadas desde la última corrida

`6-qa.md` declaraba **"Ultima validacion de reglas cross-proyecto: 2026-10-07"** (hoy, puesta por la corrida anterior). Verificado: `git log --since=2026-10-07 -- .github/instructions/32-estandares-qa-implementador.instructions.md docs/qa/regresiones-manuales.yml` → **sin commits** (el último que toca el catálogo sigue siendo `14eb845`, del 2026-10-06, ya cubierto). El índice de `32` y `cat_resumen.txt` coinciden con lo validado. **Ninguna regla nueva ni modificada desde 2026-10-07.**

Instruction de stack aplicable al lote, releída completa porque el lote la activa: **`34-integracion-afip-arca.instructions.md`**. Dos hallazgos:

- **Los códigos de la línea 85-88 confirman el enum.** PASS (criterio 1).
- **La línea 89 es una regla que este lote activa por primera vez** y hay que declararla resuelta: *"una vez que el enum tiene más de 2 valores, el endpoint normal de emitir Factura DEBE rechazar explícitamente cualquier `TipoComprobante` que no sea Factura — de lo contrario un POST manipulado puede crear un comprobante fiscal mal formado"*. **Resuelta estructuralmente, y es mejor que una guarda**: el tipo no es bindeable. `FacturacionParcialService` lo deriva server-side en `:76` y `:204` con `DeterminarTipoComprobante(venta.Cliente)`, que solo puede devolver `FacturaA` o `FacturaB`. El `TipoComprobante` de `FacturacionParcialViewModels.cs:32` es de display. No hay POST que pueda inyectarlo. **PASS.**
- **Lo que queda abierto de la `34` y es fuera de alcance declarado**: `AfipComprobanteRequestDto` **no tiene campo `CbtesAsoc`** (`grep` de `CbtesAsoc`/`CbteAsoc` sobre `AfipDtos.cs` y `AfipService.cs` da 0), y la `34` lo exige para emitir una NC. Hoy es inalcanzable: **nadie llama a `IAfipService`** (`grep` de `_afipService`/`IAfipService` sobre Services y Controllers da solo el comentario de `LP-040` que explica que la dependencia se fue). Va como riesgo de liberación 1, no como defecto.

## Máquina de estados

| Transición | Resultado | Evidencia |
|---|---|---|
| Comprobante `Pendiente` → NC emitida, NC nace `Pendiente` sin CAE | **PASS** | Arnés 6.3: `estado=1 cae=''`. En BD las 13 filas de `ComprobantesAfip` están en `Estado=1`. AFIP no se llama ni se puede |
| `Venta.Estado` NO se mueve al emitir una NC | **PASS** | Arnés 4.5: `antes=Confirmada despues=Confirmada`. R19 |
| Comprobante en `Error` → NC: **rechazada** | **PASS** | POST por HTTP, con control positivo (criterio 9) |
| Comprobante que ya es NC → NC: **rechazada** | **PASS** | POST por HTTP y arnés 5.4 (criterio 8) |
| Comprobante sin pendiente de acreditar → NC: **rechazada** | **PASS** | POST por HTTP: `"Este comprobante ya está acreditado por completo"`; y el GET redirige (302) al detalle |
| `Emitido` → NC | **BLOCKED — no alcanzable hoy** | Con AFIP apagado ningún comprobante llega a `Emitido`. El Service **no exige** `Emitido` a propósito, y la decisión está razonada en el código (`:162-167`): exigirlo sería una guarda que nunca se alcanza y que cambiaría de comportamiento el día del certificado. De acuerdo con el criterio; queda como transición a verificar cuando llegue el certificado |
| NC → baja (soft delete) | **N/A** | R17: un comprobante emitido no se da de baja. No es defecto |

## Defectos detectados

1. **`LP-052` — `major` — `GET /NotasCredito/Emitir/{id}` ofrece la pantalla completa sobre un comprobante que ya es una NC y sobre uno en `Error`.** El botón de `Views/Ventas/Details.cshtml:368` se condiciona con **tres** cosas (`!esNota && Estado != Error && PendienteDeAcreditar > 0`); el GET de `NotasCreditoController:44` se condiciona con **una** (`dto.TodoAcreditado`). Medido: `GET /NotasCredito/Emitir/5` (una NC) → **HTTP 200**, 43.481 bytes, `<form method="post">` con los `Items[0].*` y `<button type="submit" id="btnEmitir">` habilitado, rotulando el sujeto como "Nota de crédito A" y mostrando el aviso *"Esta factura le había cargado el IVA al cliente"* — llamando factura a una NC. `GET /NotasCredito/Emitir/8` con `#8` en `Estado=Error` y pendiente 3 → **HTTP 200** con el form, y **la pantalla no dice en ningún lado que está en Error**: `EstadoOriginal` viaja en el ViewModel (`NotaCreditoViewModels.cs:40`) y `grep EstadoOriginal Views/` da **cero**. Los dos POST se rechazan bien, así que **no se escribe un dato malo**; el daño es una pantalla fiscal que invita a una operación imposible. Control que aísla la causa: el GET de un comprobante sin pendiente **sí** redirige (302), o sea que una de las tres condiciones está espejada y dos no.
2. **`LP-053` — `low` — tres mutantes sobreviven con 45/45 verde, y dos de ellos contradicen afirmaciones explícitas.** Sobreviven: el filtro de `ListarComprobantesAsync` (el hallazgo que el propio commit destaca), la guarda del comprobante en `Error` (que `R17` exige, y `grep EstadoComprobanteAfip.Error` sobre el arnés da 0 hits), y la cota `Math.Min` de la devolución de IVA (declarada entre lo medido). Causa raíz: los mutantes se derivaron de la lista de afirmaciones y no del diff, así que heredan su punto ciego.
3. **`LP-054` — `low` — mío.** Preparé las bases de no-regresión restaurando un `mysqldump --no-data`, que borra las filas que siembran las migraciones y deja el `__EFMigrationsHistory` diciendo que todo corrió. `ArnesPlanEcheqs` dio 42/47 y `ArnesTarjetaYTransferencia` 30/36 con mensajes que suenan a defecto real (*"No hay un porcentaje de recargo configurado para 1 cuotas"*, *"planes=0"*). Recreadas con `dotnet ef database update`: **49/49 y 41/41**. Mismo binario, misma máquina: la causa era la preparación de la base. Lo cataloguo porque el reflejo correcto —"el commit de notas de crédito rompió los planes de cuotas"— es exactamente el equivocado.

## Partes de defecto emitidos al Implementador

- **`LP-052`** `major` — espejar en el `GET` de `NotasCreditoController.Emitir` las **tres** condiciones del botón, no una. `archivos_fix` sugeridos (hipótesis, no instrucción): `NotasCreditoController.cs` (el `if` de ~44), `NotaCreditoDtos.cs` (alternativa que evita la cuarta recurrencia: **una** propiedad calculada del tipo "no se puede acreditar + motivo" leída por la vista y por el GET, en vez de dos listas), `Views/NotasCredito/Emitir.cshtml` (mostrar `EstadoOriginal`, que ya está en el VM). `migracion_ef`: ninguna. **Re-verificación:** `GET /NotasCredito/Emitir/{id de una NC}` → **302** al detalle con mensaje que nombre que ya es una NC; `GET /NotasCredito/Emitir/{id de factura en Error con pendiente}` → **302** con mensaje que nombre el Error; **y el control positivo**: `GET` de una factura en `Pendiente` con pendiente **sigue** en 200 con el form (sin esto, las guardas se "cierran" rompiendo la pantalla); y el conjunto de condiciones del `@if` de la vista **igual** al que evalúa el GET, enumerando las dos listas.
- **`LP-053`** `low` — dos afirmaciones nuevas en `tools/ArnesNotaCredito/Program.cs` y corregir el bloque de limitaciones. `migracion_ef`: ninguna. **Re-verificación:** neutralizar el filtro de `ListarComprobantesAsync` **falla** al menos una afirmación; neutralizar la guarda de `Error` **falla** al menos una y existe su control positivo; y el `Math.Min` o queda medido o queda declarado entre lo indiscriminable.
- **`LP-054`** `low` — documentar en `docs/qa/README.md` cómo se prepara la base desechable de un arnés. **Re-verificación:** los dos arneses dan 49/49 y 41/41 por el procedimiento documentado.

**Estado de los partes de la corrida anterior:** no había defectos abiertos al arrancar (`LP-044`, `LP-045`, `LP-049` y `LP-050` cerrados en las corridas previas). Nada para re-verificar.

## No-regresión

| Arnés | Línea base | Medido | Resultado |
|---|---|---|---|
| `ArnesNotaCredito` | 45/45 | **45 OK / 0 FALLADAS / 0 NO MEDIDAS**, 5,1 s, reparto 31 `[DISCRIMINA]` / 10 `[COBERTURA]` / 4 `[CONTEXTO]` | **PASS** (reproducido independientemente, dos corridas) |
| `ArnesPlanEcheqs` | 49/49 | **49 OK / 0 FALLADAS** | **PASS** (ver `LP-054`) |
| `ArnesTarjetaYTransferencia` | 41/41 | **41 OK / 0 FALLADAS** | **PASS** (ver `LP-054`) |
| `ArnesSeisSitiosRestantes` | 32/32 + 2 NM | **32 OK / 0 FALLADAS / 2 NO MEDIDAS** | **PASS** |
| `ArnesReconciliacionTx` | 153/153 | **153 OK / 0 FALLADAS** | **PASS** |

Los 5 compilados **explícitamente** (`dotnet build tools/<arnés>`) antes de correr: `tools/` no está en la solución y el build de la solución no los toca. Barrido de 500 sobre las 7 pantallas del lote: todas **200**, y **0 líneas** `[ERR]`/`[FTL]`/`Unhandled exception` en el log de la app durante toda la corrida.

## Riesgos de liberación y mitigaciones

1. **`AfipComprobanteRequestDto` no tiene `CbtesAsoc`, y la `34` lo exige para emitir una NC** (riesgo diferido, no defecto de este lote). Hoy es inalcanzable porque nadie llama a `IAfipService`. **Mitigación:** queda escrito acá y en el riesgo del lote; el día del certificado, `CbtesAsoc` es lo primero que hay que construir, junto con la transición `Emitido → NC` que hoy está BLOCKED por inalcanzable. No bloquea el merge.
2. **`LP-052` no bloquea el merge pero sí el deploy del módulo 16.** Es una pantalla fiscal que ofrece una acción imposible; con el módulo sin liberar al usuario, el costo de arreglarlo antes es cero. **Mitigación:** el parte está emitido con criterio de re-verificación, y el ciclo exige contexto nuevo para cerrarlo.
3. **La migración no está aplicada a `laplatense_dev` y eso es correcto**, pero el módulo 16 suma una migración a la cola del deploy postergado por la credencial de Web Deploy. La condición **"base y sitio en la misma ventana"** sigue vigente y ahora cubre 19 migraciones en vez de 18. **Mitigación:** ninguna nueva — es la condición que ya estaba.
4. **Tres puntos del código correctos pero sin red** (`LP-053`): si alguien revierte el filtro del lector 2, se rompen a la vez el título "Ya facturado", el mensaje de `VentaWorkflowService:1054` y el conteo de comprobantes de la pantalla, **y el arnés sigue diciendo 45/45**. **Mitigación:** el parte de `LP-053` pide las dos afirmaciones.

## Pruebas mínimas ejecutadas

Build `--no-incremental` (0/9, desglosadas); verificación de `laplatense_dev` como control (18 migraciones, columna nueva ausente por `information_schema`); migración 19 aplicada a 3 bases desechables propias por `dotnet ef database update`; lectura operación por operación de la migración y su `Down`; **13 mutantes independientes derivados del diff** sobre una copia del árbol verificada por `md5sum`, cada uno con build chequeado y base reseteada, **más un control negativo semánticamente nulo con cero tumbadas**, más 2 controles de alcanzabilidad de rama; **2 corridas del `ArnesNotaCredito`** (repo y copia) con el mismo resultado; **5 arneses de no-regresión** compilados explícitamente, 2 de ellos con el par de control de `LP-054` (preparación por dump vs. por `ef database update`); app levantada por variable de entorno sobre fixture propio, login real por POST con antiforgery; **7 pantallas por HTTP** sin 500 y log sin errores; **1 endpoint de DataTables** por POST con antiforgery, leyendo el JSON del badge; **6 POST de emisión de NC** (NC sobre NC, comprobante en `Error`, control positivo en `Pendiente`, tope por comprobante agotado, y 2 de cierre del fixture) con conteo de filas en la BD antes y después de cada uno; **3 GET de la pantalla de emisión** (NC, factura en `Error` con pendiente, factura sin pendiente) comparando código HTTP y presencia del `<form>` y del botón de submit; lectura cruzada en BD de las 13 filas de `ComprobantesAfip`, los 5 movimientos de CC con `Origen=6`, y el par lista-vs-efectivo de las 3 líneas de la venta 1; enumeración por `grep` de los consumidores de `ComprobanteAfipItem`, `Set<ComprobanteAfip>()`, `Venta.Comprobantes`, `PendienteDeFacturar` y `ComprobanteAsociadoId` sobre todo el árbol; confrontación del enum contra la tabla de códigos de la instruction `34`.

## Checklist de salida para merge

- [x] Los 12 criterios del lote en **PASS** con evidencia ejecutada
- [x] Build `--no-incremental` en la línea base exacta: 0 errores / 9 advertencias
- [x] Migración **aditiva pura** verificada operación por operación, `Down` simétrico, sin backfill (`LP-050` N/A)
- [x] **Barrido del "ya facturado" COMPLETO**: 4 lectores, los 4 con filtro, 3 medidos por mutación
- [x] **Relabel de las 5 etiquetas auditado y CORRECTO**
- [x] **Limitación declarada verificada HONESTA**, y su subestimación (la cota) catalogada
- [x] Códigos de AFIP confirmados contra la instruction `34`; la regla de la línea 89 resuelta estructuralmente
- [x] `LP-002` verificado en las dos puntas, en el HTML servido
- [x] 5 arneses de no-regresión en su línea base exacta (411 afirmaciones, 0 falladas)
- [x] 7 pantallas sin 500 y log de la app sin un solo `[ERR]`
- [x] `laplatense_dev` intacta (18 migraciones) y producción sin tocar
- [x] `git status --porcelain` del repo del sistema **sin un solo cambio de QA**
- [ ] **`LP-052` abierto (`major`)** — no bloquea el merge; **sí es condición para liberar el módulo 16 al usuario**
- [ ] `LP-053` y `LP-054` abiertos (`low`, los dos de tooling de QA)
- [ ] Transición `Emitido → NC` y `CbtesAsoc`: **BLOCKED por inalcanzables**, a verificar el día del certificado

---

