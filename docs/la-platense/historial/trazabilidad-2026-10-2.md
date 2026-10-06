<!-- Archivado de docs/la-platense/trazabilidad.md el 2026-10-06 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-10 (3 bloques archivados)

- 2026-10-06 03:45 - qa-mvc (Entrega 3, LOTE 3 de QA: recepción de mercadería + pagos a proveedores)
- 2026-10-06 00:45 - implementador-dotnet (Entrega 4: CC de empleados + CC del negocio)
- 2026-10-05 13:25 - qa-mvc (QA Sprint 0, LOTE 1 — dia y mes de negocio / D9)

---

### 2026-10-06 03:45 - qa-mvc (Entrega 3, LOTE 3 de QA: recepción de mercadería + pagos a proveedores)

- Etapa: QA. Gate del commit `7cda85b`, probado sobre el HEAD de `entrega-1-migracion` (`d08f8c4`).
  **Resultado: GO.** Los 14 criterios de aceptación en PASS con evidencia observada en los tres
  ledgers (stock, cuenta corriente del proveedor y caja). Detalle completo en la sección
  "Entrega 3 — LOTE 3" de `definiciones/6-qa.md`.
- **Base aislada propia `laplatense_qa_l3`** (clon de `laplatense_dev`, 39 tablas, 112.485 productos).
  `laplatense_dev` no se usó para probar y **producción no se tocó**. La copia queda viva como fixture
  de la re-verificación. **El repo del sistema no se modificó** (`git status --porcelain` limpio).
- **Lo que decidió el GO y no se podía verificar leyendo:** la atomicidad se probó por **inyección de
  falla** (dos `CHECK` constraints en la copia, eliminadas al terminar), no por lectura del código —
  con el INSERT de caja forzado a fallar, el pago multi-línea **no dejó ni la línea sana**, y con el
  `Cargo` de CC forzado a fallar, la recepción no dejó stock, ni costo, ni fecha, ni ledger, ni
  estado. Y la idempotencia de la reversión se probó **con el flag de estado forzado en contra**
  (pago ya revertido devuelto a `Pagado` en la base): con los netos en 0 no escribió ni una fila, así
  que la idempotencia es por construcción y no por el flag, como declara el contrato.
- **El hallazgo que importa es `LP-024` (`major`), y no es una regresión: es el riesgo de liberación 1.**
  El lote agrega el **tercer** escritor de `Producto.Stock` y `Producto` **no tiene** token de
  concurrencia. Reproducido con el navegador: la pantalla de ajuste muestra "Stock actual 30,000",
  entra una recepción de +5 (stock 35), el operador guarda su conteo de 29 → quedan 29, **las 5
  unidades recibidas desaparecen de la columna**, `StockVerificado` queda en `true` sobre un número
  equivocado, y `SUM(MovimientosStock) = 35` contra `Producto.Stock = 29`. El alcance declarado dice
  que el ledger no reconstruye la columna —correcto como decisión—, pero el ledger nuevo vuelve el
  daño **medible por primera vez** y nada lo mide. Parte emitido al Implementador; **no bloquea el
  gate** porque ningún criterio lo cubre y el comportamiento coincide con lo declarado.
- **El hueco del ledger de stock sin historia queda clasificado como CONTENIDO:** tiene un solo lector
  y lee acotado por `(OrigenTipo, OrigenId)` de una compra puntual, así que ninguna pantalla espera
  historia completa. Consecuencia a declarar: el sistema queda con **dos historias parciales de stock**
  (`AjustesStock` y `MovimientosStock`), ninguna completa.
- Hallazgos `trivial` adicionales: `LP-025` (la búsqueda global por la etiqueta visible "Al día"
  devuelve 0 en vez de 112.486, porque el tope del helper descarta el conjunto entero en silencio) y
  `LP-026` (el formulario oculto `formConfirmar` se renderiza en una compra ya `Confirmada`; sin
  consecuencia, el Service rechaza el POST). Los tres items quedan en
  `docs/qa/regresiones-manuales.yml` (172 items) y en `cat_resumen.txt`.
- **Un falso positivo propio, descartado:** el toast de advertencia que aparecía en todo rechazo de
  pago era un guard de submit del cliente que nunca se ejecutó — mi extractor levantaba el literal del
  script inline. Confirmado en el navegador que lo que el operador ve es el mensaje correcto del Service.
- Cobertura cross-proyecto ejecutada, no leída: `MH-001` (71 llamadas a los listados del alcance, 0
  no-JSON y 0 HTTP 500, incluido el caso de colección vacía), `MH-027`, `MH-033`, `LP-002`, `LP-009`,
  `GAN-005`, `SG-001`, `MH-020`, `MH-025`, `DN-003`, `OLV-019`. **Regla nueva desde la última
  validación (2026-10-05):** sólo `LP-013`, ejecutada — la query de detección devuelve 1 fila
  **preexistente** del clon y 0 filas nuevas de este lote; sigue abierta, sin regresión.
- Dato de entorno para los lotes siguientes: el **scratchpad de la sesión se comparte entre lotes
  paralelos** (un archivo del harness fue sobrescrito en disco a mitad de corrida), y el navegador
  **tiene que apuntar a `127.0.0.1`, no a `localhost`**, o el `page.goto` muere por timeout aunque
  `curl` responda 200.
- `Ultima validacion de reglas cross-proyecto` en `6-qa.md` actualizada a **2026-10-06**.
### 2026-10-06 00:45 - implementador-dotnet (Entrega 4: CC de empleados + CC del negocio)

- Etapa: Implementación. Rama `entrega-1-migracion`, repo `C:\Sistemas\Ferreteria La Platense`.
  Base de trabajo `laplatense_dev`. **Producción no se tocó**: ni deploy, ni Web Deploy, ni ninguna
  operación contra `mysql8001.site4now.net`. **Sin push.** El fixture de QA `laplatense_qa_d9` no se
  leyó ni se modificó. Pedido explícito de Joaquín: "no publicar, dejar el desarrollo listo".
  Producción sigue 5 migraciones atrás (6 con esta).
- **La decisión más importante es la que NO se construyó.** El módulo 13 ("cuenta corriente propia del
  negocio") **no tiene entidad ni ledger nuevo**. El nombre engaña: en `marihogar` el
  `MovimientoCCLocal` de `CCLocalService` **ES la caja** —su único ledger de dinero, y su `CajaService`
  no tiene entidad propia, es pura agregación sobre él—, y en La Platense ese ledger ya existe y se
  llama `CajaMovimiento`, con cierres diarios y mensuales que allá no hay. Construir un segundo libro
  del mismo dinero es como se descubre, meses después, que ninguno de los dos cuadra. Lo que el
  presupuesto pide es textualmente una "vista consolidada de cierres de caja, ingresos y egresos": una
  pantalla de lectura. Eso es lo que se hizo.
- **Sobre el "cero inventado" del saldo se eligió resolverlo, no rotularlo — y además rotularlo.** La
  ola 1 había dejado anotado que "ningún arreglo del flujo hace que el saldo signifique la plata que
  hay si el punto de partida es un cero inventado". Se implementó el **saldo inicial declarado por
  medio de pago** (`OrigenCajaMovimiento.SaldoInicialCaja`: fecha, motivo obligatorio, usuario, una
  sola vez por medio, pasando por `ValidarPeriodoAbiertoAsync`) **y** la pantalla no llama "saldo" al
  número mientras no haya apertura: el rótulo dice literalmente "Movimiento acumulado del sistema" y
  cada cuenta sin apertura lleva su badge accionable. El criterio de `marihogar` de excluir la apertura
  de los totales del período SÍ aplica y vive en un solo lugar (`EsApertura` + los dos helpers de
  totales), alcanzando a los **seis** lectores — sin eso, el cierre firmado del día en que se declara
  el saldo inicial diría que ese día entraron $ 500.000.
- **El contraste cierre-firmado vs. recálculo encontró un problema real la primera vez que corrió:** el
  cierre mensual de **agosto 2026 no cuadra por $ 2.500,75**. Verificado por SQL de solo lectura: se
  firmó el 21/08 19:05 y el movimiento #5 (fecha 24/08) se cargó el 25/08 02:00, cuatro días después.
  Es **residuo histórico del defecto que `LP-009` ya cerró** —la guarda funciona, se verificó
  ejecutando—, no un bug de esta ronda: es la ronda haciendo **visible por primera vez** una
  inconsistencia que estaba ahí y nadie podía ver. **Producción tiene el mismo código viejo que la
  generó en dev, así que puede tener el mismo residuo**; no se consultó (estaba prohibido). Hay que
  mirarlo al deployar.
- **Devengar no es pagar**, modelado como decisión de un solo lugar invocable
  (`OrigenCCEmpleado.MueveCaja`), con el default `false` elegido a propósito: un egreso que falta se
  nota (el arqueo no cuadra contra el efectivo y alguien pregunta), uno de más descuadra en silencio y
  en la dirección que nadie revisa. El `Tipo` lo impone el **concepto** y no la vista — verificado
  ejecutando: se posteó `Tipo = Cargo` con concepto `Adelanto` (un adelanto que aumentaría la deuda con
  el empleado) y el Service persistió `Pago`. La guarda de período es **asimétrica a propósito**: solo
  la corren los conceptos que escriben caja, así que un devengamiento retroactivo a un mes cerrado
  entra y un pago con esa fecha se rechaza.
- **`MovimientoRevertidoId` es una columna nueva y necesaria, no un capricho.** El par
  `(OrigenTipo, OrigenId)` de los otros tres ledgers identifica un documento, y en este no hay
  documento: todos los movimientos de un concepto comparten `OrigenId = 0`, así que el neto de ese par
  sumaría **todos** los adelantos del empleado y revertir uno revertiría la plata de los otros. Acotar
  por empleado —el parche que usa el ledger de proveedores para sus orígenes manuales— **no alcanzaría
  acá**, porque dos adelantos del mismo empleado siguen compartiendo clave.
- **`PAT-017` estrenado con código real** tras estar con `pendiente_verificar: true` desde
  `cma-centro-medico` (la verificación del 2026-09-14 confirmó que `IPortalPacienteService` no existía
  en ningún repo). Dos pantallas en **dos controllers**: el permiso se lee en el atributo de la clase y
  no hay que auditar acción por acción. Las acciones del autoservicio **no declaran ningún parámetro de
  identidad** — no es que se valide el parámetro, es que **no existe**, que es la única forma de este
  control que no se rompe olvidándose una validación. Probado inyectando el id del Vendedor por **tres
  vías** en el form con el claim del Repartidor: devolvió solo las 4 filas del Repartidor, cero ajenas,
  y el dato de auditoría viajó en null.
- **`PAT-053` por tercera vez en el estudio y primera sobre sueldos**, que el patrón ya preveía
  textualmente. `EgresoCCEmpleadoService` es el punto único creado **cuando aparece el segundo escritor
  y no el quinto**, que es lo que el patrón prescribe: crearlo después obliga a un backfill histórico
  que no es portable (500 de las 579 líneas del servicio original de marihogar).
- **`MH-001` era el riesgo central de la ronda** y no una precaución genérica: la identidad de la cuenta
  es un `string` de `AspNetUsers`, tabla sin navegación, que es exactamente el caso que ya explotó dos
  veces (el original de marihogar y la reincidencia en el buscador de los cierres). Cerrado con las dos
  únicas formas permitidas —sub-consulta correlacionada y materializar-y-filtrar—, la segunda extraída
  a `ResolverNombresAsync` porque ya son cuatro los lugares que la necesitan. Los shapes nuevos se
  **ejecutaron** contra dev, no se supusieron, incluidas las colecciones de enum e int que la regla
  declara seguras.
- **Barrido `LP-002`: 6 hallazgos.** (1) Los seis lectores de totales de caja **no** se arrastran solos
  con el helper de orígenes: el combo y las etiquetas sí, pero los totales había que tocarlos a mano.
  (2) Las dos consultas de totales tenían que excluir lo mismo, o el pie del arqueo dejaría de sumar
  las tarjetas de arriba. (3) `CajaMovimiento.UsuarioId` era una columna de **solo escritura** desde la
  ola 1: se persiste y **ninguna pantalla la mostraba**. (4) La **promesa vencida** de `EsReversion`
  (ver abajo). (5) El Dashboard hereda el cambio sin tocarlo porque consume `ObtenerResumenDiaAsync`.
  (6) Fuera de alcance y **sin corregir**: `Views/Clientes/CuentaCorriente.cshtml` sigue con los
  orígenes hardcodeados en dos lugares y es el **único de los cuatro ledgers sin su helper de orígenes**.
- **`LP-008` — una promesa vencida encontrada.** El XML-doc de `CajaMovimiento.EsReversion` promete
  desde la ola 1 que con la columna "el arqueo" ya puede separar "plata que entró" de "plata que nunca
  salió". **Nunca se aplicó**: ningún lector de totales usa el flag. Medido en dev: ingresos brutos
  $ 97.415,05 contra netos $ 5.914,55 (el saldo es el mismo). **No se cambió el criterio de los
  cierres** —haría que los ya firmados no cuadren contra su recálculo— y la pantalla consolidada
  muestra **los dos números con el puente entre ellos** en vez de dejar que el cliente encuentre dos
  cifras distintas en dos pantallas sin saber a cuál creerle. Decisión pendiente de Joaquín. Además, 5
  XML-doc corregidos (`CajaMovimiento` cabecera y `OrigenTipo`, los dos cierres, el helper de totales).
- Migración `20261006032953_EntregaCuatro_CCEmpleadoYSaldoInicialCaja`: **una tabla nueva**
  (`MovimientosCCEmpleado`, 3 índices, **sin FK a `AspNetUsers`** en las dos columnas de usuario) y
  **cero cambios sobre tablas existentes** — los dos orígenes nuevos son valores de una columna
  `varchar(50)` que ya existía. Aplicada solo a `laplatense_dev`.
- Evidencia: build de la solución en **0 errores**, 8 advertencias **todas `NU1902` preexistentes**,
  cero nuevas (las vistas Razor compilan en el build, así que cubre los 9 `.cshtml` nuevos); el JS
  compartido pasó `node --check`. **Sonda EF desechable** en el scratchpad (borrada al terminar, no es
  un smoke test funcional: no levanta la app ni prueba por HTTP), 14 bloques y ~45 verificaciones, con
  la línea base calculada por **SQL crudo** y no por el código bajo prueba. Las 2 verificaciones que
  fallaron son el mismo hallazgo pre-existente del cierre de agosto. Base devuelta a su línea base
  exacta: 9 filas / saldo $ 3.413,80 / `MAX(Id) = 9` / 0 movimientos de empleado.
- **Aviso de impacto para el cliente, antes de que lo vea:** este es el segundo egreso automático que
  entra al arqueo además de los gastos y los pagos a proveedor. Los retiros del titular y los adelantos
  al personal son plata que **siempre salió** y hasta ahora no se registraba en ningún lado — el día
  que se empiecen a cargar, los egresos del período van a subir de golpe. No es un bug; es el mismo
  aviso que se dejó para los pagos a proveedor en la Entrega 3 y que en marihogar se vivió en
  producción.
- **Decisiones que necesita Joaquín:** (a) bruto vs. neto en los cierres firmados; (b) qué hacer con el
  cierre de agosto 2026 que no cuadra, en dev y posiblemente en producción; (c) si se crea el helper de
  orígenes que le falta al ledger de clientes; (d) si "empleado" debe separarse de "usuario del
  sistema" (hoy la pantalla de administración lista todos los usuarios, incluido el SuperUsuario
  técnico).
- Detalle completo en `5-implementador.md`, sección "Entrega 4 — Cuenta corriente de empleados (M12) +
  cuenta corriente del negocio (M13)".
### 2026-10-05 13:25 - qa-mvc (QA Sprint 0, LOTE 1 — dia y mes de negocio / D9)
- Etapa: QA (gate del commit `628cb7a`, item 0.3 / D9, + migracion de datos
  `20261005151611_D9_NormalizarFechaCajaMovimiento_DiaDeNegocio`). Lote **financiero**, 1 modulo
  (Caja / Gastos / cierres) por instruccion 39 seccion 5, con la superficie LP-002 (Ventas,
  Entregas, Dashboard, Productos, AFIP) cubierta como regresion.
- Resultado: **D9 CERRADO** — los 5 criterios de aceptacion PASS con evidencia observada, mas el
  criterio de arranque de la app (R1). **NO-GO para cerrar el Sprint 0 completo**: el lote deja 2
  defectos `major` nuevos, los dos en el circuito de dinero y los dos derivados del propio cambio.
- Metodologia: el servidor MCP `playwright` **no estaba disponible en la sesion** y tampoco hay
  `playwright-core`; se declaro y se cayo al procedimiento alternativo de la instruccion 33 —
  **automatizacion por HTTP real** (harness Node con cookies de Identity + antiforgery) contra la
  app levantada, mas assertions SQL directas. Para aislar la corrida de **otro lote de QA que
  estaba escribiendo `laplatense_dev` en paralelo** (fila `CobroCC` y usuario `admin.qa` creados
  durante la corrida), se clono la base a **`laplatense_qa_d9`** y la app se levanto contra la
  copia en `https://localhost:7202`. Unico cambio sobre `laplatense_dev`: reescritura del
  `PasswordHash` de `qa.super@test.local` y `vendedor.qa@test.local` (credencial `QaD9#2026x`);
  no se toco `no-reply@olvidata.com.ar`.
- Evidencia de los criterios: un `CajaMovimiento` con instante `2026-10-01 01:44 UTC` (= 30/09
  22:44 ART) se lista y se filtra como **30/09** y entra en el cierre de ese dia
  (`TotalIngresos=1234.56`); un gasto cargado con fecha 30/09 persiste su movimiento en
  `2026-09-30 03:00 UTC` (00:00 ART) y cae en el **mismo** cierre (`TotalEgresos=777.77`);
  cerrada la caja de hoy, `POST /Ventas/Confirmar` responde "La caja de hoy ya esta cerrada…" y la
  venta queda en Borrador (con control positivo antes del cierre); `CerrarMes` del mes anterior
  acepta (09/2026: 96.898,36 / 777,77, e **incluye** la venta de las 22:44 del 30/09), el mes en
  curso y los futuros rechazan con mensajes distintos. Migracion de datos integra: 0 filas sin
  normalizar y todos los cierres guardados coinciden con el recalculo por dia/mes de negocio ART.
- Defectos emitidos (partes al Implementador, 4 items **nuevos** en `docs/qa/regresiones-manuales.yml`,
  catalogo 154 -> 158, `cat_resumen.txt` regenerado):
  **D17 / LP-009 (`major`)** cerrado el mes, el sistema sigue aceptando movimientos dentro de ese mes
  — la guarda de periodo cerrado solo consulta `CierresCajaDiarios` y nunca `CierresCajaMensuales`;
  reproducido: 09/2026 cerrado y aun asi se aceptaron un ajuste de 3.333,33 y un gasto de 4.444,44
  fechados 15/09, con la pantalla mostrando todavia 777,77 de egresos contra 8.555,54 reales.
  **D18 / LP-010 (`major`)** la unificacion cambio `CajaMovimiento.Fecha` pero dejo `Venta.Fecha`
  con la semantica vieja: la Venta 8 (24/08 22:44 ART) se lista y se busca como **25/08** en Ventas
  y como **24/08** en Caja — barrido LP-002 incompleto, y se ve en el Dashboard ("Ventas de hoy 0 /
  $ 0,00" junto a "Caja de hoy $ 2.845,67"). **D19 / LP-011 (`minor`)** `GET
  /Caja/Mensual?anio=2026&mes=13` y `?anio=0&mes=0` dan HTTP 500 en `ArgentinaTime.RangoMesUtc`, y
  el redirect de `CerrarMes` pasa por ahi, asi que el mensaje "Mes o año invalido." agregado en este
  commit es codigo muerto. **D20 / LP-012 (`minor`)** los dos listados de cierres dibujan el
  buscador de DataTables pero el server ignora `search[value]`.
- Catalogo cross-proyecto: MH-009, MH-014 (con reserva de huso del navegador), MH-001 (ejecutado:
  24/24 HTTP 200 sobre busqueda global y filtros, incluidos los dos `List<string>.Contains` de
  `CajaMovimientoService`), CRM-019, LP-003, MH-020, MH-021, KOI-014, KOI-015 → **PASS**.
  LP-002, MH-035, CRM-017, KOI-017 → **FAIL** (son D17 y D18). MH-034 → **riesgo confirmado** (un
  gasto por transferencia cae en el mismo ledger que el efectivo); MH-033 → **N/A hoy**, riesgo para
  cuando entren Compras/CC de proveedores. Ambos escalados al analista, no son defectos de D9.
- Reglas nuevas desde la ultima corrida (2026-08-24): **24 reglas** agregadas a
  `32-estandares-qa-implementador`; se ejecutaron las 10 que este lote puede disparar (ver la tabla
  en `6-qa.md`). Campo "Ultima validacion de reglas cross-proyecto" ya en 2026-10-05.
- Riesgos/supuestos: **la ventana 21:00-00:00 ART del criterio 2 quedo BLOCKED** — a las 12:51 ART de
  la corrida `DateTime.Today`, `DateTime.UtcNow.Date` y `ArgentinaTime.Hoy` valen lo mismo, y las tres
  formas de forzar la divergencia se descartaron a proposito (reloj del sistema: hay agentes
  commiteando en paralelo; `tzutil` a Pacifico: no produce divergencia de fecha a esa hora; contenedor
  Linux: no hay Docker). Cobertura alternativa ejecutada: barrido mecanico que confirma **cero**
  `DateTime.Today` / `UtcNow.Date` / `DateTime.Now` / `ToLocalTime` en una decision de dia/mes en toda
  la app, y ninguna `ConvertTime*Utc` fuera del helper salvo los 2 call sites fiscales de AFIP. Queda
  una prueba manual de 3 minutos descripta en `6-qa.md` para cerrarlo. Para la proxima corrida por
  lotes: **un clon de base por lote**, no compartir `laplatense_dev`.
- `git status --porcelain` del repo bajo prueba al cerrar: solo `?? .claude/`, que ya estaba al abrir
  la sesion. **No se escribio una sola linea en `C:/Sistemas/Ferreteria La Platense`.**
