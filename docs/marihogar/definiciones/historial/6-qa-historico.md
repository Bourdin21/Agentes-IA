<!-- Archivado de docs/marihogar/definiciones/6-qa.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 6-qa - historico (15 bloques archivados)

- Sprint CR-L (Change Request #6) — CR-32/CR-33/CR-34: precio contado/tarjeta + recargo real, edicion completa de Venta, acreditacion diferida de tarjeta
- Sprint CR-J (Change Request #5) — CR-27: totales reales de OC historicas + pagos reales + Mercado Pago habilitado para proveedores
- Sprint CR-I (Change Request #4) — CR-25: comprobante AFIP editable + CR-26: rediseño de PDFs + QR de AFIP (RG 4291)
- Sprint CR-H (Change Request #3) — CR-24: fix de IVA, layout 4 elementos, Total editable con reparto proporcional, pagos posteriores en Ventas
- Sprint CR-G (Change Request #2) — CR-21/CR-22: doble precio de Producto + precio/subtotal editables en Ventas
- Sprint CR-F (Change Request #1, post-Etapa 1, ampliacion sobre CR-E) — CR-14 saldo acumulado + CR-15 cheque fecha default + CR-16-codigo mayusculas + CR-18 ajuste de apertura + refinamiento CR-13 ClienteCUIT
- Sprint CR-E (Change Request #1, post-Etapa 1, ampliacion sobre CR-D) — CR-10/CR-11/CR-12: auditoria de columnas del historico
- Sprint CR-C (Change Request #1, post-Etapa 1) — CR-4 descargar/enviar comprobante por WhatsApp (endpoint público, auditoría de seguridad independiente)
- Sprint CR-B (Change Request #1, post-Etapa 1) — CR-3 tarjeta de credito/Banco Carrefour + CR-5 categorias de gasto + CR-8 sugerir monto + CR-9 reportes facturado/no facturado
- Sprint CR-A (Change Request #1, post-Etapa 1) — CR-1 impuestos en OC + CR-2 fecha de emision de cheque + CR-7 acreditacion manual
- Sprint 6 — M7 Facturacion electronica AFIP/ARCA (ULTIMO sprint de Etapa 1 — gate final)
- Sprint 5 (de 6) — M18 Gastos + M15 Caja mensual + M16 Aumento masivo de precios + M17 Proyeccion financiera + M9 Dashboard
- Sprint 4 — M12 Compras a proveedores + M13 CC Proveedores + M14 Cheques 30/60/90
- Sprint 3 — M6 Entregas a domicilio
- Sprint 2 — M4 Presupuestos y cotizaciones + M5 Gestion de ventas (⭐ prioridad maxima) + M11 CC Local

---

## Sprint CR-L (Change Request #6) — CR-32/CR-33/CR-34: precio contado/tarjeta + recargo real, edicion completa de Venta, acreditacion diferida de tarjeta

### Alcance funcional validado
Implementado por el subagente implementador (a diferencia de CR-27/CR-26, este sprint SI paso por el implementador). El ciclo de QA delegado al subagente `agentes-ia-qa` se corto por un limite de sesion sin dejar registro de cierre — el orquestador completo la verificacion directamente (mismo criterio ya usado en este proyecto cuando un subagente se corta a mitad de camino: verificar el estado real en vez de asumir exito o fracaso). 3 cambios sobre `Venta`/`PagoVenta` (pantalla de mayor uso diario, dinero real): (1) `PagoVenta.MontoBase` — un pago con Tarjeta de Credito ahora carga el monto BASE a cubrir, el servidor calcula `Monto = MontoBase × 1,21` (recargo real, nunca confiado del cliente); (2) `VentaService.EditarAsync` nuevo, permite editar una Venta ya creada, bloqueado si tiene Entrega o Comprobante AFIP asociado (reutiliza los guards ya existentes de `CancelarAsync`); (3) `PagoVenta.EstadoAcreditacion`/`FechaAcreditacionEfectiva` — un pago con tarjeta queda `Pendiente` hasta que se acredita manualmente, recien ahi postea su `MovimientoCCLocal.Ingreso` (deliberadamente distinto del patron de `Cheque`, que postea inmediato).

### Cobertura por criterio de aceptacion
| Criterio | Resultado |
|---|---|
| `Monto` de un pago con Tarjeta se calcula SIEMPRE server-side (`MontoBase * 1.21m`), nunca confiado del payload | PASS — verificado por lectura de codigo en `VentaService.ConfirmarAsync` (linea 371) y `PagoVentaService.RegistrarPagoAsync` (linea 109), mismo patron en ambos |
| Saldo pendiente/`Estado` de la Venta se calculan sobre `Σ(MontoBase ?? Monto)`, no sobre `Σ Monto` | PASS — confirmado en ambos services |
| Pago con tarjeta arranca `EstadoAcreditacion=Pendiente`, sin `MovimientoCCLocal` posteado hasta acreditar | PASS — el loop de posteo en `ConfirmarAsync` explicitamente hace `if (pago.EstadoAcreditacion == Pendiente) continue;` antes de postear |
| `AcreditarPagoAsync` postea el Ingreso con `Fecha = FechaAcreditacionEfectiva`, no `DateTime.UtcNow` | PASS — confirmado por lectura de codigo (linea ~593) |
| `EditarAsync` bloqueado si hay Entrega o Comprobante AFIP asociado | PASS — reutiliza tal cual `TieneEntregaAsociadaAsync`/`TieneComprobanteAsociadoAsync`, mismos metodos privados ya usados por `CancelarAsync`, sin duplicar la consulta |
| `ProyeccionFinancieraService.PagosVentaPorAcreditar` suma ambas fuentes (CR-29 fecha futura + CR-34 tarjeta pendiente) sin doble conteo | PASS por construccion: una fuente consulta `MovimientosCCLocal` (solo movimientos YA posteados), la otra consulta `PagoVenta.EstadoAcreditacion=Pendiente` (que por diseño nunca tiene movimiento posteado todavia) — mutuamente excluyentes, no pueden solaparse |
| Columnas "Precio contado/transf" y "Precio tarjeta" visibles para Administrador Y Vendedor en `Ventas/Create` | PASS — confirmado que los `<th>` y la celda `.td-preciotarjeta-venta` se renderizan sin ningun `@if (Model.EsAdministrador)` alrededor; solo el INPUT editable de precio contado sigue gateado a Administrador (sin cambio del gate de CR-22) |
| `Cheque.cs`/`ChequeAcreditacionHostedService.cs`/`AfipService.cs` sin tocar (codigo fiscal fuera de alcance) | PASS — `git diff --stat` sobre los 3 archivos sin salida (0 cambios) |
| Migracion EF combinada (`MontoBase`/`EstadoAcreditacion`/`FechaAcreditacionEfectiva`) aplicada sin romper datos existentes | PASS — `SHOW COLUMNS` contra `marihogar_dev`: las 3 columnas nuevas son nullable/con default (`EstadoAcreditacion` default=1/Acreditado) — los `PagoVenta` historicos quedan con comportamiento identico al anterior |
| Build de la solucion | PASS — `dotnet build MariHogar.Web -c Release` a carpeta aislada, 0 errores |

### Hallazgo documentado (no es un defecto — mejora de exactitud, con una aclaracion necesaria sobre el propio criterio de "sin regresion" del implementador)
El comentario del implementador en `ConfirmarAsync` dice "sin tarjeta de por medio, la suma de estos Ingreso cierra EXACTO igual que el unico Ingreso que se posteaba antes". Esto es **cierto solo para una Venta totalmente pagada al crearse** (el caso mas comun). El codigo **anterior** a este sprint posteaba `MovimientoCCLocal.Ingreso` por `venta.Total` (el total de los items) sin importar cuanto sumaran realmente los pagos — es decir, una Venta creada como `PagadaParcial` (pagos menores al Total, capacidad ya existente desde antes de este sprint) inflaba la Caja con dinero todavia no cobrado. El codigo **nuevo** postea `Σ pago.Monto` (lo realmente cobrado), que para una `PagadaParcial` es menor al Total — **un cambio de comportamiento real, y una correccion de exactitud contable, no una regresion** (es mas correcto reflejar en Caja solo lo efectivamente cobrado). No se encontro ningun caso real en `marihogar_dev` para verificar esto empiricamente contra datos migrados (las Ventas importadas por `tools/ImportarHistorico` usan un camino de codigo distinto, no `ConfirmarAsync`) — queda como verificacion pendiente del usuario la primera vez que cree una Venta real con pago parcial desde la UI en vivo, comparando el monto que aparece en Caja contra lo efectivamente cobrado.

### Checklist de cierre
- [x] Build de la solucion completa, 0 errores.
- [x] Migracion EF aplicada en `marihogar_dev`, columnas nuevas nullable/con default, sin regresion en datos existentes.
- [x] Calculo de recargo (21%) confirmado server-side en ambos puntos de entrada (alta y pago posterior).
- [x] Guards de seguridad de `EditarAsync` confirmados (reutiliza los ya existentes de `CancelarAsync`, accion Administrador-only).
- [x] Diferido de `MovimientoCCLocal` para tarjeta pendiente confirmado por lectura de codigo, sin doble conteo en Proyeccion Financiera.
- [x] Codigo fiscal (`Cheque`/`AfipService`/`ChequeAcreditacionHostedService`) confirmado sin tocar.
- [x] 1 hallazgo documentado (mejora de exactitud en Caja para ventas `PagadaParcial`, no un defecto) — sin auto-fix necesario, es el comportamiento deseado.
- [ ] Verificacion numerica con un caso real de pago mixto (tarjeta+efectivo) creado desde la UI en vivo — no ejecutada (regla de proceso, sin smoke test ni simulacion de requests).
- [ ] Verificacion visual manual del usuario en navegador — pendiente.
- [ ] Deploy a produccion (codigo + migracion, sin reimport de datos) — pendiente, gate siguiente coordinado por el orquestador.

### Estado go/no-go

**GO para dar por cerrado tecnicamente el Sprint CR-L (CR-32/33/34) sobre `marihogar_dev`.** Verificacion por lectura de codigo linea por linea de los puntos criticos de seguridad (calculo de recargo server-side, guards de edicion, diferido de posteo de Caja) mas verificacion directa de esquema (`SHOW COLUMNS`) y build. Sin defectos de severidad bloqueante, critica, major ni minor — el unico hallazgo es una aclaracion sobre el alcance real de "sin regresion" que declaro el implementador (es una mejora de exactitud contable para ventas con pago parcial, no una regresion). **Recomendacion: GO**, sujeto a que el usuario verifique visualmente en navegador un caso real de venta con tarjeta (columnas de precio, recargo en vivo, badge "Pendiente", boton "Marcar acreditado") antes/despues del deploy a produccion.
## Sprint CR-J (Change Request #5) — CR-27: totales reales de OC historicas + pagos reales + Mercado Pago habilitado para proveedores

### Alcance funcional validado
Corrida contra `marihogar_dev` (base vaciada y reimportada) del importador actualizado (`tools/ImportarHistorico/Program.cs`) que incorpora un quinto archivo Excel nuevo (`Importacion/Informe Cuentas Corrientes Movimientos de Proveedores 30-07-2026 1052 Hs.xlsx`, 572 movimientos = 239 Compras + 333 Pagos de los 17 proveedores con historial real) para corregir 2 problemas reales detectados por el cliente: (1) el `Total` de las 239 OC historicas estaba subvaluado (solo el subtotal de lineas sin IVA/percepciones, decision original de CR-1); (2) CR-19 habia marcado ficticiamente las 239 OC como 100% pagadas en Efectivo por falta de detalle real — el archivo nuevo trae los 333 pagos reales (fecha/monto/medio) vinculados via "Id Compra". Ademas: `MetodoPago.MercadoPago` habilitado tambien para pagos a proveedores (antes exclusivo de Ventas) y `OrdenCompra.NotaInterna` nuevo (mismo patron que `Venta.NotaInterna` de CR-12). Codigo escrito directamente por el orquestador (sin pasar por el implementador) — mismo criterio de exigencia reforzada que Sprint CR-G/CR-I.

### Cobertura por criterio de aceptacion
| Criterio | Resultado |
|---|---|
| Total de OC historicas incluye impuestos reales (IVA/IIBB/Otros) | PASS — verificado 239/239 por agregacion SQL + 3 spot-checks linea por linea contra el Excel real |
| Pagos reales (fecha/monto/medio) importados en vez del pago ficticio en Efectivo | PASS — 333/333 pagos, distribucion por metodo exacta contra el Excel |
| OC sin pago real en el ledger quedan con saldo pendiente real (no ficticio) | PASS — verificado con spot-check de una OC sin ningun `PagoOrdenCompra` (Id=248 del Excel, CARDOZO JUAN CRUZ) |
| Mercado Pago habilitado como metodo de pago valido para OC | PASS — `MetodosPermitidosOC` server-side + `METODOS` JS de `OrdenesCompra/Details.cshtml` |
| Tarjeta de credito/Banco Carrefour siguen excluidos de OC (sin regresion de CR-3) | PASS — `MetodosPermitidosOC` no los incluye |
| `NotaInterna` de OC end-to-end, nunca en un PDF | PASS — sin PDF de OrdenCompra en todo el sistema (grep confirma que no existe ningun generador de PDF para este modulo) |
| Ajuste de apertura (CR-18) de CC Proveedores deshabilitado, CC Local sin cambio | PASS — 0 filas `OrigenTipo='AjusteApertura'` en `MovimientosCCProveedor`, 1 fila sin cambio en `MovimientosCCLocal` |

### Re-verificacion independiente de totales contra `marihogar_dev` (no se confio en lo declarado por el orquestador)
Reconteo propio via `mysql.exe` (MySQL Server 8.0 local), sin reusar ninguna query ya provista:
- Conteos base sin regresion: 31 Proveedores, 239 OrdenesCompra, 207 Productos, 634 Ventas, 480 Gastos, 286 ComprobantesAfip — coinciden exacto.
- `SUM(OrdenesCompra.Total)` = $117.216.297,86; `MovimientosCCProveedor Tipo=Cargo` = 239 filas, `SUM(Monto)` = $117.216.297,86 (coincide exacto entre ambas fuentes).
- `PagosOrdenCompra` = 333 filas, `SUM(Monto)` = $95.441.762,85; `MovimientosCCProveedor Tipo=Pago` = 333 filas, `SUM(Monto)` = $95.441.762,85 (coincide exacto).
- Saldo pendiente total (Σ Cargo − Σ Pago) = $21.774.535,01 (Excel: $21.774.534,96 — diff $0,05, redondeo inmaterial acumulado en 239 filas, explicado y aceptado como tal).
- Distribucion por metodo de pago en `PagosOrdenCompra`, coincide exacta con el Excel en las 4 categorias: Efectivo (38, $5.644.233,67), Transferencia (98, $28.065.697,81), MercadoPago (71, $18.695.559,41), Cheque (126, $43.036.271,96).
- `MontoOtrosImpuestos` (residual "la ultima parte absorbe el resto", mismo patron CR-24.3/CR-25): `MIN=0,00`, `MAX=52.633,85`, **0 valores negativos** sobre las 239 OC — descarta la hipotesis de un error de mapeo de columnas que hubiera producido residuales negativos.
- `MovimientosCCProveedor` con `OrigenTipo='AjusteApertura'` = 0 (confirma que el sub-bloque de Seccion 6 quedo deshabilitado como se esperaba); `MovimientosCCLocal` con el mismo origen = 1 (confirma que el bloque de CC Local no fue tocado).
- `OrdenesCompra.NotaInterna` poblado en 135/239, coincide con lo declarado.

### Spot-checks linea por linea contra el Excel real (3 casos, distintos a los ya verificados por el orquestador, incluyendo Cheque y Mercado Pago)
Metodologia: para cada OC de `marihogar_dev` se resolvio primero su alias real en `Listado de Proveedores` (RazonSocial → Alias), se ubico la fila original en `Informe de Compras` por Proveedor+Nº Factura para obtener el "Id" original del sistema anterior, y con ese Id se ubico la fila `Compra` (y los `Pago` con "Id Compra" igual) en el ledger nuevo — usando Excel COM (`New-Object -ComObject Excel.Application`) para leer las celdas reales, columna por columna con su encabezado, evitando cualquier ambigüedad de indexado.
1. **OC db Id=28 (TORRES E HIJOS SA / alias "Taurus", Id original=220)**: Subtotal=446.417,15 (recalculado tambien desde `Cantidad×PrecioUnitario` de las 6 lineas de `Informe de Compras`, coincide exacto), MontoIva=93.747,60, MontoIIBB=17.856,69, MontoOtrosImpuestos=0,00, Total=558.021,44, PuntoVenta=0001, NumeroComprobante=80006177, NotaInterna="echeq\n10/7 $186007\n10/8 $186007\n10/9 $186007" — todos coinciden exacto con la fila `Compra` del ledger. **Hallazgo relevante confirmado como correcto, no como bug**: la Descripcion menciona 3 echeqs de $186.007 c/u (total $558.021, = el Total completo), pero el ledger solo tiene 1 fila `Pago` real para este Id (Medio="Cheque Propio", Monto=186.007,00, Fecha=15/7/2026) — el importador replica fielmente esto: `PagosOrdenCompra` tiene exactamente 1 fila de $186.007 (Metodo=Cheque), saldo pendiente real = $372.014,44. No es un bug del importador: es lo que el ledger fuente realmente contiene (los otros 2 echeqs mencionados en la nota no tienen una transaccion `Pago` registrada en el archivo, posiblemente por no haber sido cobrados aun a la fecha de corte del reporte).
2. **OC db Id=31 (FIBERBALLS S.A. / alias "ALMOHADAS FIBER BALL", Id original=219)**: Subtotal=138.241,56, MontoIva=29.030,73, MontoIIBB=5.529,66, Total=172.801,95, PuntoVenta=0003, NumeroComprobante=00168924 — coincide exacto. Pago real: 1 fila `Pago` con Id Compra=219, Medio="Mercado Pago", Monto=172.801,95, Fecha=13/7/2026 — coincide exacto con `PagosOrdenCompra` (Metodo=MercadoPago, Monto=172.801,95, Fecha=2026-07-13). Caso Mercado Pago verificado end-to-end.
3. **OC db Id=2 (CARDOZO, JUAN CRUZ / alias "CRUZ COLCHONES", Id original=248, no facturada)**: Subtotal=204.545,45 (recalculado tambien desde `Cantidad×PrecioUnitario`, coincide), MontoIva=42.954,54, MontoIIBB=0,00, Total=247.499,99 — coincide exacto. Sin ninguna fila `Pago` en el ledger para este Id → `PagosOrdenCompra` = 0 filas para esta OC, confirmando que el saldo pendiente queda real (no se inventa ningun pago ficticio). `PuntoVenta`/`NumeroComprobante` = `NULL` en la base (correcto: `Facturada=false`, el codigo solo los setea `if (facturada)`), pese a que el ledger trae "0000"/"00000000" como placeholder — el guard `if (facturada)` evita persistir ese placeholder sin sentido.

### Revision de codigo de `tools/ImportarHistorico/Program.cs` (Seccion 2.5, 3 y 6) linea por linea
- **Mapeo de columnas de la Seccion 2.5** (`Compra`: Id=col1, Subtotal=col17 "Subtotal con Descuento", IVA=suma de col20-24, IIBB=col28 "Perc. IIBB", Total=col32 "Total compra"; `Pago`: Id Compra=col14, Medio=col7, Monto=col33 "Pagado") verificado exacto contra el header real del archivo (leido con Excel COM), confirmado con los 3 spot-checks de arriba.
- **`MontoOtrosImpuestos` como residual** (`Total - Subtotal - MontoIva - MontoIIBB`): confirmado por SQL que nunca da negativo (`MIN=0,00` sobre 239 filas) — si hubiera un error de mapeo de columnas (ej. columnas corridas), esto muy probablemente hubiera producido residuales negativos en al menos algunas filas; su ausencia es evidencia indirecta adicional de que el mapeo es correcto, no solo los spot-checks puntuales.
- **Fallback cuando `idCompra` no esta en `comprasTax`** (`oc.Subtotal = subtotalLineas; oc.Total = subtotalLineas`, impuestos en su default de entidad): seguro — no se reprodujo ningun caso real (239/239 Compras matchearon), y de ocurrir, el comportamiento es equivalente al pre-CR-27 (sin impuestos), nunca deja el registro en un estado invalido o con excepcion.
- **`MapearMetodoPagoOC`**: los 4 valores reales de "Medio de Pago" del ledger (Caja del Local/Caja General → Efectivo; Banco Galicia/BANCO PCIA/cuenta dni → Transferencia; Cheque Propio/Cheque de Terceros → Cheque; Mercado Pago → MercadoPago) verificados contra los medios reales vistos en los 3 spot-checks ("Cheque Propio"→Cheque, "Mercado Pago"→MercadoPago) — correctos. Sin distincion Cheque Propio/Terceros, documentado como limitacion aceptada (el modelo no la contempla y no hay numero/banco real en este archivo).
- **Seccion 3 (loop de Compras)**: `PuntoVenta`/`NumeroComprobante` solo se setean `if (facturada)` — confirmado por el spot-check de la OC no facturada (Id=248) que efectivamente quedan `NULL` en vez de heredar el placeholder "0000"/"00000000" del Excel.

### Revision del impacto de deshabilitar el sub-bloque de CC Proveedores en la Seccion 6 (CR-18)
- El bloque de CC Local (mismo Seccion 6) **no fue tocado** — confirmado por diff y por SQL (1 fila `AjusteApertura` en `MovimientosCCLocal`, sin cambio de comportamiento respecto a corridas anteriores).
- `CCProveedorService.ObtenerSaldoActualAsync`/`ObtenerSaldosAsync` calculan el saldo directamente como `Σ Cargo − Σ Pago` sobre `MovimientosCCProveedor` — al no existir mas el movimiento `AjusteApertura` que forzaba el saldo a $0, el saldo mostrado en CC Proveedores ahora refleja el saldo real (verificado: $21.774.535,01 total), que es exactamente el objetivo de CR-27. Sin efecto colateral: el servicio no tiene ninguna logica especial para `OrigenTipo='AjusteApertura'`, simplemente ya no hay ninguna fila de ese tipo que sumar.
- `ProyeccionFinancieraService.ObtenerAsync` (`SaldoPendienteOrdenesCompra`) calcula el saldo pendiente directamente desde `OrdenCompra.Total − Σ Pagos` (excluyendo cheques Rechazados) — **no depende del ledger de `MovimientosCCProveedor` ni del bloque de ajuste de apertura**, por lo tanto no tenia ningun acoplamiento a remover; ahora reflejara automaticamente el saldo real mas alto y preciso, sin cambio de codigo necesario.
- `MH-007` (fix ya existente que excluye `OrigenTipo='AjusteApertura'` de `CajaService`/`ProyeccionFinancieraService` para CC Local) confirmado intacto por grep — sigue vigente para CC Local, y ahora es simplemente inaplicable para CC Proveedores (no hay filas de ese tipo que excluir).
- **Conclusion: el razonamiento del orquestador es correcto** — deshabilitar el ajuste de apertura de CC Proveedores no reintroduce ningun problema y no deja ningun efecto colateral en CC Local ni en Proyeccion financiera.

### Revision de cambios UI/Application/Infrastructure (consistencia y regresiones)
- `PagoOrdenCompraService.MetodosPermitidosOC` = `{Efectivo, Transferencia, MercadoPago, Cheque, Deposito}` — guard server-side intacto (`lineasValidas.Any(p => !MetodosPermitidosOC.Contains(p.Metodo))`), `TarjetaCredito`/`BancoCarrefour` correctamente ausentes (sin regresion de CR-3).
- `OrdenesCompra/Details.cshtml`: diccionario JS `METODOS` incluye `3: 'Mercado Pago'`, coherente con el whitelist server-side.
- `NotaInterna` confirmado end-to-end: `OrdenCompra.cs` (Domain) → `OrdenCompraDtos.cs` (2 DTOs) → `OrdenCompraFormViewModel`/`OrdenCompraDetailsViewModel` → `OrdenesCompraController` (Create/Edit, via `MapInput`) → `OrdenCompraService.CreateAsync`/`UpdateAsync`/`GetByIdAsync` → `Details.cshtml` (card de solo lectura, oculta si vacio) / `Create.cshtml` (campo colapsable). Migracion `20260730184534_AddNotaInternaOrdenCompra` (columna `longtext` nullable, aditiva, sin script de datos) aplicada en `marihogar_dev` (confirmado por `DESCRIBE OrdenesCompra` + `__EFMigrationsHistory`).
- **1 hallazgo menor nuevo, no bloqueante, con auto-fix aplicado**: el mensaje de error de `PagoOrdenCompraService.RegistrarPagoAsync` para metodo no permitido seguia listando "solo Efectivo, Transferencia, Cheque o Depósito", sin mencionar Mercado Pago pese a que CR-27 lo agrego al whitelist real — inconsistencia de texto (no de logica: el `Contains()` real ya incluye MercadoPago desde el codigo del orquestador). Ver "Auto-fixes aplicados" abajo.

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)
| id | aplica | resultado | accion |
|---|---|---|---|
| REG-003 (autocomplete Compras) | N/A | — | Sin cambio de UI de autocomplete en este sprint |
| REG-004 (maquina de estados Compra) | si | PASS | Sin cambio de maquina de estados de OC en CR-27 (import crea OC directo en `Recibida`, sin transiciones nuevas) |
| GAN-001 (al menos 1 pago real, nunca `Count==0`) | si | PASS | `PagoOrdenCompraService.RegistrarPagoAsync` sin cambio en ese guard; importador nunca crea un `PagoOrdenCompra` de monto 0 (filtro `monto <= 0 -> continue`) |
| MH-001 (`.Contains()` sobre coleccion local de string) | si | PASS | Grep de `.Contains(` en los archivos tocados: ninguna ocurrencia del patron riesgoso (todos los `.Contains()` nuevos son `string.Contains()` en memoria, post-lectura de Excel, o `HashSet<enum>.Contains()`/`HashSet<Estado>.Contains()` sobre tipos primitivos, ya confirmado seguro por la nota de Sprint 4) |
| MH-003 (fecha de emision de cheque futura) | si | PASS | `PagoOrdenCompraService.cs` guard intacto, sin tocar por CR-27 |
| MH-007 (AjusteApertura distorsiona Caja/Proyeccion) | si | PASS | Filtro `OrigenTipo != "AjusteApertura"` intacto en `CajaService`/`ProyeccionFinancieraService`; ahora inaplicable para CC Proveedores (0 filas de ese tipo) |
| Resto (KOI-*, DN-*, VSF-*, REG-001/002/005 a 010) | N/A | — | Sin equivalente en los modulos tocados (Compras/CC Proveedores) de este sprint |

### Defectos detectados
| Severidad | Descripcion | Estado |
|---|---|---|
| Minor | Mensaje de error de `PagoOrdenCompraService.RegistrarPagoAsync` desactualizado (no mencionaba Mercado Pago entre los metodos validos) | Corregido (auto-fix, ver abajo) |

### Auto-fixes aplicados en este ciclo
- **MH-008 (nuevo, catalogado)**: `MariHogar.Infrastructure/Services/PagoOrdenCompraService.cs`, mensaje de `CreateError` de metodo no valido corregido de "solo Efectivo, Transferencia, Cheque o Depósito" a "solo Efectivo, Transferencia, Mercado Pago, Cheque o Depósito" — cambio de solo texto, sin alterar la logica de validacion (`Contains()` sin cambios). Re-verificado con `dotnet build MariHogar.Infrastructure/MariHogar.Infrastructure.csproj` (0 errores) y `dotnet build MariHogar.slnx --no-incremental` (0 errores, mismos 9 warnings preexistentes).

### Evidencia de build y migracion (re-verificado por QA de forma independiente)
- `dotnet build MariHogar.slnx --no-incremental` → Compilacion correcta, 0 Errores, 9 Advertencias (mismas preexistentes: NU1902 MailKit/MimeKit x4, CS0114 HomeController — ninguna nueva).
- `dotnet build tools/ImportarHistorico/ImportarHistorico.csproj --no-incremental` → Compilacion correcta, 0 Errores.
- `dotnet ef migrations list` (proyecto `MariHogar.Infrastructure`, startup `MariHogar.Web`) → coincide exacto con `__EFMigrationsHistory` de `marihogar_dev` (`20260730184534_AddNotaInternaOrdenCompra` como ultima), sin ninguna migracion pendiente.
- `git status --short` → solo los archivos declarados por el orquestador (10 modificados + 2 nuevos de la migracion), sin artefactos huerfanos.

### Riesgos de liberacion
- **Bajo, informativo**: el saldo pendiente real de CC Proveedores sube de $0 (forzado por CR-18/CR-19) a $21.774.535,01 real — es el objetivo explicito de CR-27, pero implica que Proyeccion financiera y cualquier reporte que consuma `SaldoPendienteOrdenesCompra`/CC Proveedores mostraran una deuda mucho mayor que antes; el cliente ya fue informado y confirmo explicitamente ambas decisiones (impuestos reales + Mercado Pago) antes de implementar.
- **Bajo**: 28 de las 239 OC quedan sin ningun pago real registrado (confirmado, no es un bug) — su saldo pendiente es 100% del Total; si el cliente esperaba ver algunas de estas marcadas como pagadas por otro medio no capturado en el Excel, requeriria una aclaracion suya, no un cambio de codigo.
- **Nulo**: esta corrida fue exclusivamente contra `marihogar_dev` — produccion no fue tocada. El GO de este reporte habilita el paso siguiente (backup + vaciado + reimport + confirmacion explicita del cliente en el momento, mismo proceso ya usado en CR-6/CR-23), no autoriza por si mismo la ejecucion contra produccion.

### Pruebas minimas ejecutadas
- Reconteo SQL independiente de 8 metricas agregadas contra `marihogar_dev` (conteos base, sumas de Total/Pagos, distribucion por metodo, saldo pendiente, residuales de impuesto, filas de ajuste de apertura).
- 3 spot-checks completos linea por linea contra el Excel real (Excel COM), incluyendo los 2 casos explicitamente pedidos (Cheque y Mercado Pago) mas un tercero (OC sin pago real, no facturada).
- Revision de codigo completa (1162 lineas) de `tools/ImportarHistorico/Program.cs`.
- Revision de codigo de `PagoOrdenCompraService.cs`, `OrdenCompraService.cs`, `OrdenesCompraController.cs`, `OrdenCompraViewModels.cs`, `OrdenCompraDtos.cs`, `OrdenCompra.cs`, `MetodoPago.cs`, `Details.cshtml`, `Create.cshtml`.
- Build completo de la solucion + del proyecto `ImportarHistorico` + `dotnet ef migrations list`.

### Checklist de salida para merge
- [x] Build de `MariHogar.slnx` limpio, 0 errores (re-verificado por QA de forma independiente).
- [x] Build de `tools/ImportarHistorico` limpio, 0 errores.
- [x] Migracion `AddNotaInternaOrdenCompra` aplicada en `marihogar_dev`, sin pendientes.
- [x] Totales de OC (239 Compras) y Pagos (333) re-verificados 100% de forma independiente contra `marihogar_dev`, coinciden exacto con lo declarado.
- [x] 3 spot-checks linea por linea contra el Excel real (incluye Cheque, Mercado Pago y caso sin pago real), coinciden exacto.
- [x] Sin residuales negativos de `MontoOtrosImpuestos` (descarta error de mapeo de columnas).
- [x] Ajuste de apertura de CC Proveedores confirmado deshabilitado (0 filas), CC Local sin cambio (1 fila).
- [x] Guard server-side de `MetodosPermitidosOC` confirmado sin abrir Tarjeta de credito/Banco Carrefour para OC.
- [x] `NotaInterna` de OC confirmado end-to-end y sin ningun camino de fuga a PDF (no existe PDF de OrdenCompra).
- [x] 1 hallazgo menor (mensaje de error desactualizado) catalogado (`MH-008`) y corregido con auto-fix.
- [ ] Verificacion visual manual del usuario en navegador (Registrar pago con Mercado Pago en una OC real, ver la card "Nota interna") — pendiente, no ejecutada por QA (regla de proceso).
- [ ] Backup + vaciado + reimport + confirmacion explicita del cliente contra produccion — pendiente, fuera del alcance de este ciclo (gate siguiente, coordinado por el orquestador).

### Estado go/no-go

**GO para dar por cerrado tecnicamente el Sprint CR-J (CR-27) sobre `marihogar_dev`.** Los 2 problemas reales que motivaron el sprint (Total de OC historicas subvaluado, pagos ficticios en Efectivo) quedan corregidos y verificados de forma independiente con el maximo nivel de rigor usado en este proyecto: reconteo SQL propio de 8 metricas agregadas + 3 spot-checks linea por linea contra el Excel real (metodologia propia, resolviendo alias de proveedor → Id original del sistema anterior → fila del ledger, sin depender de ningun query ya provisto) + revision completa de las 1162 lineas del importador + revision de los cambios de Application/Infrastructure/Web. Sin defectos de severidad bloqueante, critica ni major. **1 defecto minor encontrado y corregido en el mismo ciclo** (mensaje de error desactualizado tras habilitar Mercado Pago), catalogado como `MH-008`. El razonamiento del orquestador de deshabilitar el ajuste de apertura de CC Proveedores fue verificado como correcto y sin efectos colaterales (CC Local intacto, Proyeccion financiera no acoplada a ese bloque). **Recomendacion: GO**, sujeto a (1) la verificacion visual manual del usuario en navegador (no bloqueante para el cierre tecnico) y (2) que la ejecucion real contra produccion siga el mismo proceso de backup + vaciado + reimport + confirmacion explicita del cliente ya usado en CR-6/CR-23 — esta corrida fue exclusivamente contra `marihogar_dev`.
## Sprint CR-I (Change Request #4) — CR-25: comprobante AFIP editable + CR-26: rediseño de PDFs + QR de AFIP (RG 4291)

Sobre `1-analista-funcional.md` (Discovery+Analisis v11), `2-disenador-funcional.md` (Diseño v8, HU-7.6 a HU-7.8), `3-arquitecto-mvc.md` (Arquitectura v7). **Ciclo de mayor exigencia del proyecto**: es la primera revisión independiente de código escrito directamente por el orquestador (sin implementador de por medio) — CR-25 lo terminó el subagente antes de cortarse 2 veces, CR-26 (rediseño visual + QR AFIP) lo escribió el orquestador él mismo bajo presión de tiempo. Foco explícito en el QR de AFIP por ser el único ítem con implicancia de cumplimiento fiscal real.

### Alcance funcional validado
CR-25 (`ComprobanteAfipService.EmitirAsync`/`ObtenerPrecargaAsync`, `ComprobantesAfipController.Create`, `ComprobantesAfip/Create.cshtml`): cantidad/precio/subtotal totalmente editables al facturar, sin tope duro contra lo pendiente de la Venta, con aviso informativo no bloqueante y fila "Total" con reparto proporcional (mismo mecanismo que CR-24.3). CR-26 (`ComprobanteAfipService.GenerarPdfAsync`, `VentaService.GenerarRemitoPdfInterno`): rediseño visual con logo/CUIT/columnas alineadas a la derecha/total destacado, más el código QR de AFIP (RG 4291) embebido en el pie de la factura, generado con el paquete `QRCoder` 1.6.0 nuevo.

### Cobertura por criterio de aceptacion (HU-7.6 a HU-7.8)

| HU / CA | Resultado | Evidencia |
|---|---|---|
| HU-7.6 / CR-25 (Cantidad/Precio/Subtotal editables sin tope, aviso no bloqueante, fila Total con reparto proporcional) | CUMPLE | `ComprobanteAfipService.EmitirAsync` L186-207: sin `return error` por `Cantidad > pendiente`; `subtotalLinea = itemInput.Subtotal ?? Cantidad×PrecioUnitario` (nunca `ventaItem.PrecioUnitario` forzado). `ObtenerPrecargaAsync` L142-155: lista TODOS los items, sin filtrar `CantidadPendiente=0`. `ComprobantesAfip/Create.cshtml` L52-61 (inputs abiertos, sin `max`), L153 (badge "Supera lo pendiente" no bloqueante), L211-237 (reparto proporcional, última línea absorbe el resto — algoritmo idéntico carácter por carácter al ya validado en `Ventas/Create.cshtml` CR-24.3). Verificación numérica propia contra datos reales de `marihogar_dev` (Venta #622, 3 líneas, ver abajo): suma cierra exacta. |
| HU-7.6 / CA (la pantalla deja de bloquear el acceso con Venta 100% facturada) | CUMPLE | `ComprobantesAfipController.Create` L64-83: ya no redirige por `precarga.Items.Count == 0` en el caso "ya facturada" (ese caso ya no puede ocurrir, `ObtenerPrecargaAsync` nunca filtra items); el `Count==0` que queda en el código es un guard defensivo residual para una Venta sin ningún item (caso distinto, no alcanzable en uso normal), no una regresión. |
| HU-7.7 / CR-26 (encabezado con logo+nombre+CUIT, columnas alineadas a la derecha, total destacado, ambos PDF) | CUMPLE | `ComprobanteAfipService.cs` L321-335 y `VentaService.cs` L547-562: mismo layout de header (logo `.ConstantItem(50).Image()` + nombre + CUIT formateado). Columnas Cant./Precio unit./Subtotal con `.AlignRight()` en ambos (`ComprobanteAfipService.cs` L361-363/372-374, `VentaService.cs` L587-589/597-601). Total en `.Border().Background()` en ambos. |
| HU-7.8 / CR-26 (QR de AFIP RG 4291 visible en el pie de la primera página de la factura) | CUMPLE, ver auditoría exhaustiva abajo | `ComprobanteAfipService.cs` L386-395 (`page.Footer()`, imagen QR + texto). |

### Auditoria exhaustiva del codigo QR de AFIP (RG 4291) — foco critico del ciclo

Releído `GenerarQrAfip` (`ComprobanteAfipService.cs` L414-450) línea por línea contra la especificación exacta de Arquitectura v7, y **verificado además por ejecución real independiente** (script standalone descartable en el scratchpad de esta sesión, con `System.Text.Json` real, sin confiar solo en la lectura del código — mismo estándar que ya usó el orquestador al cerrar el sprint):

1. **13 campos, nombres exactos**: confirmado por ejecución real que el JSON serializado contiene exactamente `ver, fecha, cuit, ptoVta, tipoCmp, nroCmp, importe, moneda, ctz, tipoDocRec, nroDocRec, tipoCodAut, codAut` — ni uno más, ni uno menos, mismas mayúsculas/minúsculas que la especificación (el anonymous type de C# ya está escrito en camelCase, sin `JsonNamingPolicy` que pudiera alterarlo).
2. **`fecha` en `yyyy-MM-dd`**: confirmado, `c.Fecha.ToString("yyyy-MM-dd")` (L428).
3. **`cuit` es el del EMISOR, no el del cliente** — punto más sensible, verificado con cuidado especial: `cuitEmisor` se parsea de `_settings.CUIT` (`AfipSettings.CUIT`, L421/429), **nunca** de `c.ClienteCUIT`. El CUIT del cliente solo se usa más abajo, y exclusivamente para `nroDocRec` (campo distinto). Confirmado además que `appsettings.Production.json` tiene el CUIT real del cliente cargado (`20331136132`), no vacío — el guard `string.IsNullOrWhiteSpace(_settings.CUIT)` (L421) es el camino seguro para homologación/desarrollo (CUIT vacío por defecto ahí), no un problema en producción.
4. **`tipoCmp` = `(int)comprobante.TipoComprobante`** (L431): confirmado. Releído el enum `TipoComprobanteAfip.cs` directamente (no asumido): `FacturaA = 1`, `FacturaB = 6` — coincide exacto con los códigos reales `CbteTipo` de AFIP citados en la especificación.
5. **`tipoDocRec`/`nroDocRec` reusan `ResolverDocumentoAfip(c.ClienteCUIT, c.ClienteDNI)`** (L423): confirmado que es el mismo método privado ya usado por `IntentarEmitirYPersistirAsync` para armar el request real a AFIP (L456) — no hay una segunda implementación paralela con otra lógica. Mismos códigos 80/96/99 (CUIT/DNI/Consumidor Final sin documento).
6. **`moneda="PES"`, `ctz=1`**: confirmados como literales fijos (L434-435), sin ninguna condición que pudiera variarlos.
7. **`codAut` = CAE parseado a número, con guard ante CAE null/no numérico**: `if (string.IsNullOrWhiteSpace(c.CAE) || !long.TryParse(c.CAE, out var codAut)) return null;` (L420) — si el CAE no está o no parsea, `GenerarQrAfip` devuelve `null` limpiamente (sin excepción); `GenerarPdfAsync` ya maneja ese `null` con `if (qrBytes != null) row.ConstantItem(60).Image(qrBytes);` (L390), degradando sin romper el PDF. **Este guard no es hipotético**: se confirmó por query real contra `marihogar_dev` que **las 286 filas actuales de `ComprobantesAfip` (100%, todas con `Estado=Emitido`) tienen `CAE IS NULL`** — son registros del importador histórico (CR-13), nunca pasaron por una emisión real de AFIP. Esto significa que, hoy, el guard se ejercita en el 100% de los casos reales de la base: ningún PDF de factura existente muestra el QR todavía (no es un bug — es el comportamiento correcto y esperado hasta la primera emisión real contra AFIP con certificado válido).
8. **URL exacta `https://www.afip.gob.ar/fe/qr/?p={base64}`**: confirmada por ejecución real, sin espacios ni parámetros de más — el Base64 generado por el script de verificación decodifica exactamente al JSON de 13 campos.
9. **Generación real del PNG**: verificado con `QRCoder` 1.6.0 real (no mock) — `QRCodeGenerator` + `PngByteQRCode` producen un archivo con el header PNG estándar (`0x89 0x50 0x4E 0x47`, "P N G") confirmado byte a byte, 780 bytes para una URL de prueba.

**Conclusión de la auditoría del QR: implementación exacta a la especificación de Arquitectura v7, sin desvíos de ningún campo, tipo o literal.** Sin necesidad de escalar nada — no se encontró ninguna discrepancia.

### Verificacion numerica real del reparto proporcional de CR-25 contra `marihogar_dev`

Misma Venta #622 ya usada en la verificación de CR-24.3 (3 `VentaItem`, `PrecioUnitario` reales 326446.28/376033.06/178512.40, todos con `CantidadPendiente=0` — ya facturados al 100%, por lo que `ComprobantesAfip/Create.cshtml` precarga `cantidadDefault=CantidadVenta=1` en cada línea). Simulado el algoritmo real del JS (idéntico al de CR-24.3) con un nuevo Total de $900.000,00: `totalActual=880.991,74` → `factor=900000/880991,74` → línea 1: `333.489,68`, línea 2: `384.146,34`, línea 3 (última, resto exacto): `182.363,98`. **Suma = $900.000,00 exacto**, sin centavos de diferencia — reproducido con un programa C# standalone, no solo revisado por lectura.

### Verificacion de build y migracion

- `dotnet build MariHogar.Infrastructure/MariHogar.Infrastructure.csproj` → **0 errores** (4 warnings NU1902 preexistentes, MailKit/MimeKit).
- `dotnet build MariHogar.Web/MariHogar.Web.csproj -c Release -o <carpeta temporal fuera del repo>` → **0 errores** (9 warnings, incluido `CS0114 HomeController.StatusCode` ya preexistente). Carpeta temporal borrada al terminar.
- **Sin migración EF nueva**: confirmado por listado directo de `MariHogar.Infrastructure/Data/Migrations/` (última fecha 29/07, `RenameProductoPrecioVentaAPrecioEfectivo` de CR-21) y por `git diff --stat` de `MariHogar.Domain/`/`Migrations/` — los únicos cambios ahí (`Producto.cs`/`VentaItem.cs`/`AppDbContextModelSnapshot.cs`) pertenecen íntegros a CR-21/CR-22, ya auditados con GO en Sprint CR-G; CR-25/CR-26 no tocan `Domain/Entities` en ningún archivo.
- Paquete `QRCoder` 1.6.0 confirmado en `MariHogar.Infrastructure.csproj` (única dependencia nueva de este sprint).

### Verificacion de regresion (contratos publicos)

- `IVentaService`/`IComprobanteAfipService`: **sin cambio de firma pública** en ningún método — confirmado leyendo ambas interfaces completas. Los 2 parámetros nuevos del constructor de `VentaService` (`IWebHostEnvironment`, `IOptions<AfipSettings>`) son detalle de implementación interno, resueltos sin registro adicional en `DependencyInjection.cs` (`IWebHostEnvironment` lo provee el host de ASP.NET Core automáticamente; `AfipSettings` ya estaba registrado como `Options` desde Sprint 6).
- **MH-005 intacto**: los 3 guards `Estado != Pagada && Estado != PagadaParcial -> null` siguen presentes verbatim en `GenerarRemitoPdfAsync`/`ObtenerOCrearTokenDescargaPublicaAsync`/`GenerarRemitoPdfPorTokenAsync` (líneas 459/472/500).
- **MH-006 intacto**: `GenerarRemitoPdfPorTokenAsync` sigue resolviendo dinámicamente en cada descarga si hay un `ComprobanteAfip` Emitido más reciente y delega en `_comprobanteAfipService.GenerarPdfAsync(...)`, igual que antes (líneas 513-520) — el rediseño visual de CR-26 no tocó esta lógica.
- Sin `.Contains()` nuevo sobre colección local de `string` en los archivos tocados (grep dedicado sobre `ComprobanteAfipService.cs`/`VentaService.cs`) — sin riesgo MH-001 nuevo.

### Hallazgos menores (no bloqueantes, sin auto-fix — no son bugs funcionales reproducibles)

1. **Doc-comment desactualizado**: `IComprobanteAfipService.cs` (interfaz), el comentario XML de `EmitirAsync` todavía dice "Cantidad &lt;= pendiente de facturar del VentaItem" — quedó desactualizado tras CR-25, que eliminó exactamente esa validación. Es solo documentación (no afecta comportamiento), pero puede confundir a un futuro lector del código.
2. **Asimetría cosmética entre los 2 PDF**: `VentaService.GenerarRemitoPdfInterno` oculta la línea "CUIT: ..." completa si `_afipSettings.CUIT` está vacío (`if (!string.IsNullOrWhiteSpace(...))`), mientras que `ComprobanteAfipService.GenerarPdfAsync` siempre imprime `"CUIT: " + FormatearCuit(...)` sin ese guard — con `CUIT` vacío (solo posible en homologación/desarrollo, no en producción, confirmado que `appsettings.Production.json` ya tiene el CUIT real cargado) mostraría "CUIT: " en blanco en la factura. No reproducible en producción con la configuración actual.
3. **QR invisible en el 100% de los comprobantes existentes hoy**: no es un defecto de código (es el guard correcto funcionando), pero es información operativa importante: las 286 facturas ya migradas por el importador histórico (CR-13) nunca tendrán QR porque no tienen CAE real — el QR solo aparecerá a partir de la primera emisión real contra AFIP con el certificado `.p12` configurado. Recomendado avisar al cliente para que no espere ver el QR en facturas históricas.

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

| id | aplica | resultado | accion |
|---|---|---|---|
| REG-001 (RowVersion MySQL) | no | N/A — sin entidad/migración nueva este sprint | ninguna |
| REG-002 (stock inicial variante) | no | N/A — módulo no existe en marihogar | ninguna |
| REG-003/005/007 (autocomplete Select2 sin resultados) | no | N/A — `ComprobantesAfip/Create.cshtml` no tiene buscador de productos (universo cerrado a los items de la Venta, por diseño) | ninguna |
| REG-004 (máquina de estados Compra) | no | N/A — módulo Compras no tocado | ninguna |
| REG-006 (medio de pago Cuotas sin pedir cantidad/%) | no | N/A — sin formas de pago en esta pantalla | ninguna |
| REG-008 (input pierde foco por re-render completo) | sí (directo, pantalla con inputs editables) | PASS — `recalcularSubtotalFila`/`actualizarAvisoPendiente`/`actualizarInputTotalFactura` actualizan solo el nodo `.val()` puntual de cada fila, nunca reconstruyen el `tbody`; `actualizarInputTotalFactura` respeta `:focus` (mismo patrón ya validado en CR-24.3) | ninguna |
| REG-009 (cascada categoría/subgrupo) | no | N/A — sin cascada en esta pantalla | ninguna |
| REG-010 (menú visible sin policy) | no | N/A — sin cambio de sidebar/menú | ninguna |
| KOI-001 a KOI-006 | no | N/A — proyecto/stack distinto | ninguna |
| DN-001/DN-002 | no | N/A — sin DataTable server-side tocado | ninguna |
| GAN-001 (guard "al menos 1" no dispara por default de model binder) | sí | PASS — `ComprobantesAfipController.Create` deserializa `itemsJson` con `JsonSerializer.Deserialize` puro (sin índices de formulario), `EmitirAsync` valida `itemsValidos.Count == 0` sobre la lista real deserializada — mismo patrón ya validado en CR-24.4/CR-25 no reintroduce el patrón de falla | ninguna |
| GAN-002/003/004 | no | N/A — sin backfill/`<script>+<partial>`/`<datalist>` en el alcance de este sprint | ninguna |
| VSF-001/VSF-002 | no | N/A — módulo Compras no tocado | ninguna |
| CRM-001 a CRM-006 | no | N/A — módulo CRM no existe en marihogar | ninguna |
| MH-001 (IN de colección local `string` no soportado por MySQL/EF Core 10) | sí (grep) | PASS — sin `.Contains()` nuevo sobre colección local de `string` en `ComprobanteAfipService.cs`/`VentaService.cs` | ninguna |
| MH-002 (enum serializado como int) | sí (grep) | PASS — `TipoComprobante`/`Estado` siguen serializados con `.ToString()` en los DTOs de listado/detalle, sin cambio | ninguna |
| MH-003 (fecha de cheque futura) | no | N/A — sin cheques en este sprint | ninguna |
| MH-004 (desglose facturado/no facturado de Caja) | no | N/A — `CajaService` no tocado | ninguna |
| MH-005 (remito/link público no revalidaba Estado) | sí (re-verificado) | PASS — los 3 guards siguen intactos, ver "Verificación de regresión" arriba | ninguna |
| MH-006 (WhatsApp no elegía factura AFIP) | sí (re-verificado) | PASS — lógica de elección dinámica intacta, ver "Verificación de regresión" arriba | ninguna |
| MH-007 (ajuste de apertura en Caja/Proyección) | no | N/A — `CajaService`/`ProyeccionFinancieraService` no tocados este sprint | ninguna |

### Defectos detectados
**Ninguno funcional.** 3 hallazgos menores documentales/cosméticos (ver arriba), ninguno bloqueante, ninguno con impacto de cumplimiento fiscal — el QR de AFIP fue verificado exhaustivamente campo por campo y por ejecución real, sin ninguna discrepancia contra la especificación de Arquitectura v7.

### Auto-fixes aplicados en este ciclo
**Ninguno.** No se reprodujo ningún bug funcional ni de cumplimiento fiscal — los 3 hallazgos menores son documentales/cosméticos, no requieren parche de lógica de negocio, y no están catalogados como patrón cross-proyecto (no aplica el criterio de auto-fix obligatorio, que es para bugs funcionales reproducidos).

### Riesgos de liberacion

| Riesgo | Nivel | Mitigación / estado |
|---|---|---|
| Verificación visual real (abrir el PDF, escanear el QR con el celular) | Medio, no bloqueante para el cierre técnico | Pendiente del usuario — QA no ejecuta smoke test ni abre PDFs generados en caliente (regla de proceso vigente). El código y la generación del PNG ya están verificados por ejecución real independiente (ver auditoría arriba); falta únicamente el paso visual/físico de escanear con un lector de QR real. |
| Ningún comprobante real tiene CAE todavía (100% de los 286 en `marihogar_dev` son del importador histórico) | Bajo, informativo | El QR no se puede verificar end-to-end contra un comprobante 100% real hasta la primera emisión real contra AFIP (certificado `.p12` ya configurado en producción según trazabilidad). No bloquea el cierre técnico — el guard de CAE ausente ya está probado en la práctica (se ejercita en el 100% de los casos actuales sin romper nada). |
| Doc-comment desactualizado en `IComprobanteAfipService.cs` | Muy bajo | Cosmético, sin impacto de comportamiento — corregible en cualquier sprint futuro sin urgencia. |
| Asimetría del guard de CUIT vacío entre los 2 PDF | Muy bajo | Solo reproducible en homologación/desarrollo (CUIT vacío) — producción ya tiene el CUIT real cargado, confirmado. |
| Working tree acumula también cambios sin commitear de CR-21/22/23/24 (ya auditados con GO en ciclos anteriores) | Bajo | Mismo riesgo ya documentado en el ciclo anterior (Sprint CR-H) — el commit final debe incluirlos con cuidado. |

### Pruebas minimas ejecutadas
Ver tabla de cobertura por criterio + auditoría exhaustiva del QR (13 campos verificados por ejecución real, no solo lectura) + verificación numérica real del reparto proporcional contra la Venta #622 de `marihogar_dev` + verificación de regresión de MH-005/MH-006, todas por revisión de código y ejecución de scripts standalone descartables (sin smoke test de la app ni simulación de requests HTTP, regla de proceso vigente).

### Checklist de salida para merge
- [x] Build de `MariHogar.Infrastructure` limpio, 0 errores (re-verificado por QA de forma independiente).
- [x] Build de `MariHogar.Web` a carpeta aislada, 0 errores (re-verificado por QA).
- [x] Confirmado que no se generó ninguna migración EF (listado directo de `Migrations/` + `git diff --stat` de `Domain/`/`Migrations/`, cambios existentes pertenecen íntegros a CR-21/22 ya auditados).
- [x] **Auditoría exhaustiva del QR de AFIP**: los 13 campos, nombres, mayúsculas, `cuit` del emisor (no del cliente), `tipoCmp` desde el enum real, reuso de `ResolverDocumentoAfip`, literales `moneda`/`ctz`, guard de `codAut` ante CAE ausente, y URL exacta — todos verificados por lectura línea por línea Y por ejecución real independiente (script standalone + `QRCoder` real generando PNG válido).
- [x] Verificación numérica independiente del reparto proporcional de CR-25 contra la Venta #622 real de `marihogar_dev` — suma cierra exacta.
- [x] Confirmado que `IVentaService`/`IComprobanteAfipService` no cambiaron su firma pública; MH-005/MH-006 re-verificados intactos.
- [x] Playbook cross-proyecto ejecutado (25 items evaluados explícitamente, resto N/A por módulo/stack).
- [ ] Verificación visual manual del usuario en navegador (abrir el PDF, escanear el QR con el celular) — pendiente, no ejecutada por QA (regla de proceso).
- [ ] Primera emisión real contra AFIP (con CAE real) para probar el QR end-to-end contra un comprobante genuino — pendiente, fuera del alcance de este ciclo (depende de uso real del sistema).
- [ ] Commit de los cambios de este sprint (working tree acumula también CR-21/22/23/24 sin commitear).

### Estado go/no-go

**GO para dar por cerrado técnicamente el Sprint CR-I (Change Request #4, CR-25/CR-26).** CR-25 fue verificado completo y correcto (sin tope duro de cantidad, precio/subtotal desde el input, reparto proporcional matemáticamente exacto con datos reales). CR-26 fue verificado con el mayor nivel de exigencia del proyecto hasta ahora, por ser código escrito directamente por el orquestador sin pasar por el implementador ni por un segundo par de ojos previo: el rediseño visual es correcto (logo con guard seguro, columnas alineadas, total destacado) y **el código QR de AFIP (RG 4291) coincide exactamente, campo por campo, con la especificación de Arquitectura v7** — verificado no solo por lectura sino por ejecución real independiente de la construcción del JSON/Base64/URL y de la generación del PNG con `QRCoder`. Sin defectos funcionales de ningún nivel. 3 hallazgos menores puramente cosméticos/documentales, ninguno bloqueante, ninguno con riesgo de cumplimiento fiscal. **Recomendación: GO**, sujeto a que el usuario confirme visualmente el PDF/QR con un lector real en la primera oportunidad (no bloqueante para el cierre técnico) y a que la primera emisión real contra AFIP en producción sirva como confirmación end-to-end final del QR contra un comprobante genuino con CAE real.
## Sprint CR-H (Change Request #3) — CR-24: fix de IVA, layout 4 elementos, Total editable con reparto proporcional, pagos posteriores en Ventas

Sobre `1-analista-funcional.md` (Discovery+Analisis v10), `2-disenador-funcional.md` (Diseno v7, HU-5.17 a HU-5.20), `3-arquitecto-mvc.md` (Arquitectura v6). Cambio sobre `Ventas/Create.cshtml`/`Ventas/Details.cshtml`, pantalla de mayor uso diario, ya en produccion con datos reales.

### Alcance funcional validado
4 sub-items: CR-24.1/24.2 (fix del bug de IVA que pisaba el precio editado a mano + layout de 4 elementos en la columna de precio), CR-24.3 (fila "Total" editable con reparto proporcional), CR-24.4 (nueva capacidad `IPagoVentaService`/`PagoVentaService`, mirror intra-proyecto de `PagoOrdenCompraService`, para pagos posteriores sobre una Venta ya creada), CR-24.5 (redirect a `Ventas/Details/{id}` tras confirmar).

### Cobertura por criterio de aceptacion (HU-5.17 a HU-5.20)

| HU / CA | Resultado | Evidencia |
|---|---|---|
| HU-5.17 / CA-CR24.1-24.2 (c/IVA calculado en vivo sobre el precio editado, nunca `PrecioLista` fijo) | CUMPLE | `Ventas/Create.cshtml` L230-233 (`precioConIva(it)` = `it.precioUnitario × 1.21`), L395-403 (`.btn-toggle-iva` ya no toca `it.precioUnitario`, solo alterna `it.ivaActivo`), L371-379 (`c/IVA` recalculado en cada `input` sobre `.inp-precio-venta`, via `actualizarPrecioIvaDom`). |
| HU-5.18 / CA-CR24.3 (Total editable, reparto proporcional, suma exacta) | CUMPLE | `Ventas/Create.cshtml` L606-636: `factor = nuevoTotal/totalActual`, todas las lineas menos la ultima ajustadas por `factor` y redondeadas a 2 decimales, la ultima absorbe el resto exacto. Guard `totalActual <= 0` retorna sin efecto (L608, L613). Verificado con datos reales (ver abajo). |
| HU-5.19 / CA-CR24.4 (pagos posteriores, nunca supera saldo, nunca sobre Pagada/Cancelada) | CUMPLE | `PagoVentaService.RegistrarPagoAsync` completo, ver auditoria de seguridad abajo. |
| HU-5.20 / CA-CR24.5 (redirect a Details) | CUMPLE | `Ventas/Create.cshtml` L679-686: `.done()` redirige con `window.location.href` a `Ventas/Details/{ventaId}` en el camino de exito; ya no llama al panel in-page. |

### Verificacion de build y migracion

- `dotnet build MariHogar.Domain/MariHogar.Domain.csproj` → 0 errores.
- `dotnet build MariHogar.Application/MariHogar.Application.csproj` → 0 errores.
- `dotnet build MariHogar.Infrastructure/MariHogar.Infrastructure.csproj` → 0 errores, mismos 4 warnings preexistentes (NU1902 MailKit/MimeKit).
- `dotnet build MariHogar.Web/MariHogar.Web.csproj -c Release -o <carpeta temporal fuera del repo>` (para evitar el lock de DLL de la sesion de debug del usuario, nota de proceso ya vigente) → **0 errores** (9 warnings, incluido `CS0114 HomeController.StatusCode` ya preexistente, sin relacion con este sprint), confirmando ademas que no hubo ningun lock real esta vez. Carpeta temporal borrada al terminar.
- **Sin migracion EF nueva**: confirmado por listado directo de `MariHogar.Infrastructure/Data/Migrations/` — la ultima migracion es `20260729125456_RenameProductoPrecioVentaAPrecioEfectivo` (29/07, CR-21), ninguna con fecha 30/07. Consistente con Arquitectura v6 ("Sin migracion EF").
- **Confirmado que `VentaService.cs` no fue tocado por CR-24** (`git diff` de ese archivo muestra exclusivamente cambios de CR-21/CR-22 ya reportados en el ciclo anterior) — los 3 guards de MH-005 (`Estado != Pagada && Estado != PagadaParcial -> null` en `GenerarRemitoPdfAsync`/`ObtenerOCrearTokenDescargaPublicaAsync`/`GenerarRemitoPdfPorTokenAsync`, lineas 451/464/492) siguen intactos, sin regresion.

### Verificacion numerica real de CR-24.3 (reparto proporcional) contra `marihogar_dev`

Recontado de forma independiente (no se confio en lo declarado por el implementador): `SELECT Id, Subtotal FROM VentaItems WHERE VentaId=622` y `SELECT Total FROM Ventas WHERE Id=622` contra `marihogar_dev` (MySQL 8.0 local, credenciales de `appsettings.Development.json`) confirma exactamente los 3 subtotales declarados (395.000,00 / 455.000,00 / 216.000,00, Total 1.066.000,00). Simulando a mano el algoritmo real del JS con un nuevo Total de 1.000.000,00: `factor = 500/533 = 0,9380863939...`; linea 1 → `redondear2(395000×factor) = 370.544,09`; linea 2 → `redondear2(455000×factor) = 426.829,27`; linea 3 (ultima, resto exacto) → `1.000.000,00 − (370.544,09+426.829,27) = 202.626,64`. Suma = **1.000.000,00 exacto**, coincide con lo declarado por el implementador y con el algoritmo tal cual esta escrito en el codigo (misma funcion `redondear2` = `Math.round(n×100)/100`). Caso de carrito de 1 sola linea confirmado por lectura del bucle (`for i<carrito.length-1`, con length=1 nunca itera, la unica linea es simultaneamente "todas menos la ultima" y "la ultima", absorbe el total completo sin codigo especial). Guard de division por cero (`totalActual <= 0 -> return`) confirmado presente y en la posicion correcta (antes de calcular `factor`).

### Auditoria de seguridad de CR-24.4 (foco critico del ciclo, mismo estandar que CR-22/CR-4)

Revision linea por linea de `MariHogar.Infrastructure/Services/PagoVentaService.cs` completo y de `VentasController.RegistrarPago`:

1. **Guard GAN-001 (al menos 1 linea con monto real)**: `lineasValidas = input.Pagos.Where(p => p.Monto > 0)`, rechazo si `Count == 0`. A diferencia del patron GAN-001 original (ASP.NET Core model binder con indices de formulario, que preserva un objeto "fantasma" por default de constructor), aca `input.Pagos` viene de `JsonSerializer.Deserialize<List<...>>(pagosJson)` — un `pagosJson="[]"` deserializa a lista vacia real, sin fila fantasma. **GAN-001 no reproduce en este flujo (N/A por diseño, verificado por lectura, no solo por analogia).**
2. **Metodos permitidos**: `MetodosPermitidosVenta` = Efectivo/Transferencia/MercadoPago/TarjetaCredito/BancoCarrefour — **sin Cheque**, idem `VentaService.ConfirmarAsync`. Confirmado.
3. **Cuotas de tarjeta**: `CantidadCuotas` obligatorio (3/6/9/12) solo si `Metodo == TarjetaCredito`; prohibido informarlo (o `PorcentajeInteres`) para cualquier otro metodo — mismo patron que el alta inicial.
4. **Estado de la Venta**: `EstadosPagables = [Pendiente, PagadaParcial]`; `!EstadosPagables.Contains(venta.Estado) -> error`, **nunca permite pagar sobre `Pagada` ni `Cancelada`**.
5. **Saldo pendiente recalculado desde la base**: `montoPagadoExistente` se lee con una query `SumAsync` fresca sobre `PagosVenta` (no se confia en ningun valor que viaje del cliente); `saldoDisponible = venta.Total - montoPagadoExistente`; `sumaNueva > saldoDisponible -> error`. **El monto nunca puede superar el saldo real, sin importar que envie el cliente.**
6. **Transaccion atomica**: cada linea crea `PagoVenta` + movimiento `Ingreso` en `MovimientoCCLocal` (`OrigenTipo="Venta"`, `OrigenId=venta.Id`, mismo patron que `ConfirmarAsync`) dentro de `BeginTransactionAsync`/`CommitAsync`, con `RollbackAsync` en el `catch`. `Venta.Estado` se recalcula al final (`Pagada` si `montoPagadoTotal >= Total`, si no `PagadaParcial` — nunca puede retroceder a `Pendiente` porque el guard #1 ya exige monto real).
7. **Sin bypass de rol en el payload**: `VentasController` es `[Authorize(Policy = "RequireVentas")]` a nivel de clase (linea 20), sin excepcion para `RegistrarPago` — protegido para Administrador y Vendedor por igual, consistente con el diseno (HU-5.19 no exige rol especifico). El controller no lee ningun campo de "rol" del body.
8. **Doble-submit**: `Ventas/Details.cshtml` L404-405 deshabilita el boton `#btnConfirmarPagoVenta` antes del POST (mismo patron que `OrdenesCompra/Details.cshtml`), mitigacion de UI — la proteccion real de "no pagar de mas" sigue siendo el guard #5 server-side, no este disable.
9. **Registrado en DI**: `MariHogar.Infrastructure/DependencyInjection.cs` L54, `IPagoVentaService`→`PagoVentaService`, scoped.

**Conclusion de la auditoria**: los 5 guards funcionales estan 100% del lado del servidor, ninguno depende de que la UI oculte controles. No se encontro ningun camino de bypass por POST directo con monto manipulado, doble-submit, ni sobre una Venta en estado no pagable. Sin reproduccion en navegador (regla de proceso del proyecto, QA no ejecuta smoke test ni simula requests) — la verificacion es 100% por lectura de codigo, con foco explicito en los mismos 2 escenarios criticos pedidos: monto > saldo pendiente (rechazado por el guard #5) y Venta `Pagada`/`Cancelada` (rechazada por el guard #4).

**Riesgo residual documentado, no bloqueante (no introducido por este sprint)**: `montoPagadoExistente` se lee con una query separada antes de abrir la transaccion — en teoria, 2 requests concurrentes sobre la misma Venta podrian ambas leer el mismo saldo disponible antes de que la primera confirme, permitiendo en un caso de carrera extremo que la suma de ambas supere el Total real. Este patron es identico al ya existente en `PagoOrdenCompraService.RegistrarPagoAsync` (no es una regresion de CR-24, es el mismo diseno reutilizado a proposito) — se documenta como riesgo preexistente de baja probabilidad (requiere 2 clicks simultaneos de usuarios distintos sobre la misma Venta en la ventana de milisegundos entre lectura y commit), no bloqueante para este cierre.

### Regresion de permisos (Vendedor)

Confirmado por Razor: `Ventas/Create.cshtml` L91-94 (columna `<th>c/IVA</th>`) y L102-113 (`<tfoot>` con `#inpTotalVenta`) solo se renderizan `@if (Model.EsAdministrador)`. `Model.EsAdministrador` viene de `VentasController.Create()` → `EsAdministrador()` → `User.IsInRole(...)`, server-side, no manipulable. Ademas, aunque un Vendedor forzara la UI por consola, `VentaService.ConfirmarAsync` (sin cambios en este sprint) sigue ignorando `PrecioUnitario`/`Subtotal` del payload para cualquier `esAdministrador == false`, recalculando siempre desde `Producto.PrecioEfectivo`. **Sin regresion.**

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

| id | aplica | resultado | accion |
|---|---|---|---|
| REG-001 (RowVersion MySQL) | no | N/A — sin entidad/migracion nueva este sprint | ninguna |
| REG-002 (stock inicial variante) | no | N/A — modulo no existe en marihogar | ninguna |
| REG-003/005/007 (autocomplete Select2 sin resultados) | no | N/A — buscador de productos de `Ventas/Create` no tocado por CR-24 | ninguna |
| REG-004 (maquina de estados Compra) | no | N/A — modulo Compras no tocado este sprint | ninguna |
| REG-006 (medio de pago Cuotas sin pedir cantidad/%) | si (mapeado a Tarjeta de credito) | PASS — `PagoVentaService` exige `CantidadCuotas` 3/6/9/12 obligatorio solo con `TarjetaCredito`, mismo patron ya validado en Sprint CR-B | ninguna |
| REG-008 (input pierde foco por re-render completo) | si (directo, pantalla tocada) | PASS — `actualizarSubtotalDom`/`actualizarPrecioIvaDom`/`actualizarInputTotalVenta` actualizan solo el nodo DOM puntual, nunca `renderCarrito()` en los handlers de `input`; `actualizarInputTotalVenta` respeta `:focus` | ninguna |
| REG-009 (cascada categoria/subgrupo) | no | N/A — sin cascada en Ventas | ninguna |
| REG-010 (menu visible sin policy) | no | N/A — sin cambio de sidebar/menu este sprint | ninguna |
| KOI-001 a KOI-006 | no | N/A — proyecto/stack distinto (KoiDumplings) | ninguna |
| DN-001/DN-002 (Include+OrderBy dinamico+Skip/Take) | no | N/A — sin DataTable server-side tocado este sprint | ninguna |
| GAN-001 (guard "al menos 1 pago" no dispara por default de model binder) | si | PASS — `PagoVentaService`/`VentasController.RegistrarPago` deserializan JSON puro (no hay indices de formulario con default de constructor), `pagosJson=[]` produce lista vacia real, el guard dispara correctamente | ninguna |
| GAN-002 (backfill sin FechaVencimiento) | no | N/A — sin backfill de datos este sprint | ninguna |
| GAN-003 (`<script>` + `<partial>` no procesado) | no | N/A — `Ventas/Create.cshtml`/`Details.cshtml` arman filas por concatenacion de string en JS, sin templates Razor embebidos en `<script>` | ninguna |
| GAN-004 (`<datalist>` no refresca) | no | N/A — sin `<datalist>` en las vistas tocadas | ninguna |
| VSF-001/VSF-002 | no | N/A — modulo Compras no tocado este sprint | ninguna |
| CRM-001 a CRM-006 | no | N/A — modulo CRM no existe en marihogar | ninguna |
| MH-001 (IN de coleccion local `string` no soportado por MySQL/EF Core 10) | si (grep) | PASS — los 3 `.Contains()` de `PagoVentaService.cs` son sobre `HashSet<MetodoPago>`/`int[]`/`EstadoVenta[]` evaluados en memoria contra un unico valor (`p.Metodo`, `venta.Estado`), nunca dentro de una query LINQ traducida a SQL | ninguna |
| MH-002 (enum serializado como int en JSON) | si (grep) | PASS — `PagoVentaDto.Metodo` es `string` (no el enum), poblado con `.ToString()` en `VentaService.GetByIdAsync`; sin DTO nuevo de CR-24 que exponga un enum crudo | ninguna |
| MH-003 (fecha de emision de cheque futura sin revalidar) | no | N/A — Ventas nunca admite Cheque como forma de pago (confirmado en `MetodosPermitidosVenta`, sin campos de cheque en `PagoVentaLineaInput`) | ninguna |
| MH-004 (desglose facturado/no facturado de Caja) | no | N/A — `CajaService` no tocado este sprint | ninguna |
| MH-005 (remito/link publico no revalidaba Estado) | si (re-verificado) | PASS — `VentaService.cs` no fue tocado por CR-24 (confirmado por diff), los 3 guards siguen intactos (lineas 451/464/492) | ninguna |
| MH-006 (WhatsApp no elegia factura AFIP) | si (re-verificado) | PASS — mismo motivo que MH-005, sin cambios en el metodo afectado | ninguna |
| MH-007 (ajuste de apertura contado como flujo real de Caja/Proyeccion) | no | N/A — `CajaService`/`ProyeccionFinancieraService` no tocados este sprint | ninguna |

### Defectos detectados

**Ninguno.** Los 4 sub-items de CR-24 fueron implementados exactamente como especifica Diseno v7/Arquitectura v6, sin desvios. La declaracion del implementador sobre la verificacion numerica de la Venta #622 fue reproducida de forma independiente contra `marihogar_dev` y coincide exacto.

### Auto-fixes aplicados en este ciclo

**Ninguno.** No se reprodujo ningun bug funcional ni de seguridad — todos los guards de CR-24.4 estan presentes y correctos, el algoritmo de reparto proporcional de CR-24.3 es matematicamente correcto (verificado con datos reales), y no hay regresion en los guards de MH-005/MH-006 (heredados, sin tocar).

### Riesgos de liberacion

| Riesgo | Nivel | Mitigacion / estado |
|---|---|---|
| Verificacion visual en navegador de los 9 puntos de "Pruebas minimas para QA" (`5-implementador.md`, Sprint CR-H) | Bajo-medio | Pendiente del usuario (regla de proceso: QA/Implementador no ejecutan smoke test). Foco sugerido: punto 9 (POST directo con dev tools sobre `RegistrarPago`, ya cubierto por revision de codigo, verificacion visual es complementaria no bloqueante). |
| Condicion de carrera teorica en `PagoVentaService.RegistrarPagoAsync` (lectura de saldo fuera de la transaccion) | Bajo | Preexistente en `PagoOrdenCompraService` (mismo patron reutilizado a proposito), no introducido por este sprint. No bloqueante. |
| Working tree con cambios de sprints previos (CR-21/CR-22/CR-23) aun sin commitear junto a CR-24 | Bajo | Fuera de alcance de este ciclo (ya auditados en Sprints CR-G/CR-anteriores con GO); no afecta la evaluacion de CR-24 pero el commit final debera incluirlos juntos o separarlos con cuidado. |

### Pruebas minimas ejecutadas
Ver tabla de cobertura por criterio arriba + verificacion numerica real de CR-24.3 + auditoria de seguridad de CR-24.4, todas por revision de codigo y query real contra `marihogar_dev` (sin smoke test ni simulacion de requests, regla de proceso vigente).

### Checklist de salida para merge
- [x] Build de `MariHogar.Domain`/`MariHogar.Application`/`MariHogar.Infrastructure` limpio por separado, 0 errores (re-verificado por QA de forma independiente).
- [x] Build de `MariHogar.Web` a carpeta aislada, 0 errores (re-verificado por QA, sin necesidad de esperar al usuario esta vez).
- [x] Confirmado que no se genero ninguna migracion EF (listado directo de `Migrations/`, ultima fecha 29/07).
- [x] Confirmado que `VentaService.cs` no fue tocado por CR-24 (diff aislado), guards de MH-005 intactos.
- [x] Revision de codigo linea por linea de los 5 guards server-side de `PagoVentaService.RegistrarPagoAsync` + proteccion de policy del controller.
- [x] Verificacion numerica independiente del reparto proporcional de CR-24.3 contra la Venta #622 real de `marihogar_dev` — suma cierra exacta, coincide con lo declarado.
- [x] Regresion de permisos Vendedor confirmada (columna c/IVA y fila Total ocultas, servidor ignora payload de precio/subtotal para no-Administrador).
- [x] Playbook cross-proyecto ejecutado (24 items evaluados explicitamente, resto N/A por modulo/stack).
- [ ] Verificacion visual manual del usuario en navegador (9 puntos de "Pruebas minimas", `5-implementador.md`) — pendiente, no ejecutada por QA (regla de proceso).
- [ ] Commit de los cambios de este sprint (working tree sin commitear al momento de este ciclo).

### Estado go/no-go

**GO para dar por cerrado tecnicamente el Sprint CR-H (Change Request #3, CR-24).** Los 4 sub-items fueron verificados con el mismo estandar exigido para pantallas de dinero real en produccion: CR-24.1/24.2 confirmado que el fix elimina el bug real (el toggle de IVA ya no pisa el precio editado a mano) y que "c/IVA" se recalcula en vivo sobre el input, no sobre un valor fijo del catalogo; CR-24.3 verificado matematicamente correcto con datos reales de `marihogar_dev` (Venta #622, suma exacta sin centavos de diferencia) y con los 2 casos de borde explicitos (carrito de 1 linea, division por cero) confirmados por lectura de codigo; CR-24.4 auditado con el mismo nivel de exigencia que CR-22/CR-4 (los 5 guards server-side — al menos 1 pago real, metodos permitidos sin Cheque, cuotas de tarjeta validas, Estado pagable, saldo nunca superado — estan 100% del lado del servidor, sin ningun bypass encontrado); CR-24.5 confirmado el redirect. Sin defectos de ninguna severidad, sin auto-fixes necesarios. Unico riesgo residual (condicion de carrera teorica en la lectura de saldo) es preexistente del patron ya usado en Compras, no introducido por este sprint. **Recomendacion: GO**, sujeto a la verificacion visual manual del usuario en navegador (9 puntos ya detallados por el implementador, no bloqueante para el cierre tecnico) y a que el commit de este sprint se maneje con cuidado dado que el working tree acumula tambien cambios sin commitear de CR-21/22/23 (ya auditados con GO en ciclos anteriores).
## Sprint CR-G (Change Request #2) — CR-21/CR-22: doble precio de Producto + precio/subtotal editables en Ventas

**Nota de proceso**: el ciclo de QA se cortó por límite de sesión (`resets 2:20pm America/Buenos_Aires`) al comienzo de la verificación, justo después de confirmar la forma de la migración, antes de correr las queries reales y de escribir cualquier reporte. Dado que este ítem toca directamente el manejo de precios en producción con dinero real, **el orquestador retomó la auditoría completa de forma directa e independiente** (mismo nivel de exigencia que un ciclo de QA normal — lectura de código propia, sin confiar en lo declarado por el implementador, más queries reales), en vez de re-lanzar un nuevo agente de QA a ciegas.

### Auditoría de seguridad (prioridad del ciclo — riesgo Alto declarado en Arquitectura v5)

Releído línea por línea `MariHogar.Infrastructure/Services/VentaService.cs` (`ConfirmarAsync`) y `MariHogar.Web/Controllers/VentasController.cs`:

1. **`esAdministrador` se resuelve exclusivamente server-side**: `VentasController.EsAdministrador()` (línea 194-195) es `User.IsInRole(SeedData.RolSuperUsuario) || User.IsInRole(SeedData.RolAdministrador)` — sin ningún `??`/fallback que pudiera dar `true` por defecto ante un claim ausente. Se llama en 2 puntos: al armar el `VentaCreateViewModel` (GET, línea 77) y al invocar `ConfirmarAsync` (POST, línea 144) — **el mismo método, sin una segunda ruta divergente**.
2. **`ConfirmarAsync` no tiene ningún camino de bypass**: recibe `esAdministrador` como parámetro `bool` plano de la firma del método (no lo lee de `input`/el JSON deserializado). Dentro del loop de items (línea 301-318): si `esAdministrador == true`, usa `item.PrecioUnitario`/`item.Subtotal` (validados `> 0` cada uno, sin exigir que `Subtotal == Cantidad×PrecioUnitario` — el override intencional). Si `esAdministrador == false`, **siempre** `precioUnitario = producto.PrecioEfectivo` y `subtotalItem = item.Cantidad * precioUnitario`, sin excepción — el valor que haya llegado en `item.PrecioUnitario`/`item.Subtotal` del payload se descarta por completo, sin importar qué contenga.
3. **UI correctamente en defensa en profundidad, no como única barrera**: `Ventas/Create.cshtml` solo renderiza los inputs editables de precio/subtotal si `esAdministrador` (variable JS derivada de `Model.EsAdministrador`, a su vez seteado en el GET desde el mismo `EsAdministrador()` server-side) es `true` — pero aunque alguien manipulara esa variable JS por consola del navegador para forzar la UI a mostrarse, el POST real a `Ventas/Confirmar` sigue resolviendo `esAdministrador` de cero, server-side, ignorando cualquier cosa que haya llegado en el body. **Conclusión: sin bypass posible, ni por UI ni por request forjado a mano.**

### Otras verificaciones (recontadas de forma independiente contra `marihogar_dev`)

- `dotnet build MariHogar.slnx` / `tools/ImportarHistorico/ImportarHistorico.csproj` / `tools/SeedTestData/SeedTestData.csproj` → **0 errores en los 3**, mismos warnings preexistentes.
- Migración: `RenameColumn` real `Productos.PrecioVenta`→`PrecioEfectivo` (sin pérdida de datos) + `AddColumn VentaItems.Subtotal` con `UPDATE...SET Subtotal = Cantidad * PrecioUnitario` de backfill — confirmado por `DESCRIBE` real de ambas tablas.
- **Recontado independiente**: `SELECT` de agregación propia (no confiar en el "0 desalineadas" declarado) sobre las 635 Ventas × `SUM(VentaItems.Subtotal)` agrupado por Venta comparado contra `Venta.Total` — **0 de 635 desalineadas**, coincide exacto con lo declarado.
- `Producto.PrecioLista`: confirmado por `DESCRIBE Productos` que **no existe como columna real** — solo `PrecioCompra`/`PrecioEfectivo` en el esquema, `PrecioLista` es una propiedad calculada C# no mapeada, tal como especifica Arquitectura v5.
- `AumentoMasivoPrecioService.cs`: confirmado que sigue operando sobre `PrecioEfectivo` (rename mecánico correcto, sin cambio de comportamiento — `PrecioLista` la sigue automáticamente por ser derivada).
- Regresión evitada en `Presupuestos/Create.cshtml`: confirmado que la precarga de precio al buscar un producto usa `p.precioEfectivo` (línea 174, campo ya renombrado en el JSON servido por `ProductoBusquedaDto`) — sin romperse.

### Estado go/no-go

**GO.** Sin defectos de ninguna severidad encontrados en ninguna de las verificaciones — el punto de mayor riesgo del sprint (bypass de precio por rol) fue auditado con el máximo nivel de detalle posible sin necesidad de navegador, y no presenta ningún camino de explotación. Recomendación: habilitar el paso a aplicar CR-21/CR-22 contra producción, sujeto a las mismas condiciones ya usadas en todo el proyecto (backup previo, migración aplicada antes del deploy, confirmación explícita del cliente en el momento). Checklist de verificación manual en navegador (8 puntos, ver `5-implementador.md`) queda pendiente del usuario, no bloqueante para el cierre técnico.
## Sprint CR-F (Change Request #1, post-Etapa 1, ampliacion sobre CR-E) — CR-14 saldo acumulado + CR-15 cheque fecha default + CR-16-codigo mayusculas + CR-18 ajuste de apertura + refinamiento CR-13 ClienteCUIT

### Alcance validado

Duodecima ejecucion de QA sobre marihogar. Valida los 5 items declarados por el implementador para el Sprint CR-F: `CCLocalService`/`CCProveedorService` ganan saldo acumulado en memoria (CR-14, HU-11.4/HU-13.3), `OrdenesCompra/Details.cshtml` precompleta fecha de emision + cuota al elegir Cheque (CR-15, HU-12.9), `ProveedorService`/`ProductoService` normalizan a mayusculas en Crear/Editar (CR-16-codigo, HU-2.5), bloque nuevo de ajuste de apertura al final de `tools/ImportarHistorico/Program.cs` (CR-18) y `ComprobanteAfip.ClienteCUIT` leido de la columna "CUIT / DNI" del Excel de Ventas (refinamiento de CR-13). Contra `1-analista-funcional.md` (Discovery + Analisis v7), `2-disenador-funcional.md` (Diseno v5) y `3-arquitecto-mvc.md` (Arquitectura v4, sin migracion EF en ningun item). Metodo: (1) lectura completa y propia de los 8 archivos realmente tocados (no solo los "7" declarados por el implementador, ver observacion mas abajo), sin confiar en lo declarado; (2) `dotnet build MariHogar.slnx` y `dotnet build tools/ImportarHistorico/ImportarHistorico.csproj` re-ejecutados de forma independiente; (3) `dotnet ef migrations list` re-ejecutado para confirmar ausencia de migracion nueva; (4) queries reales propias contra `marihogar_dev` (`mysql.exe` de MySQL Server 8.0 local) con funciones de ventana SQL para reproducir de forma independiente el calculo de saldo acumulado fila por fila y validar a mano el monto que generaria el ajuste de apertura de CR-18 si se ejecutara. **No se levanto la app ni se simularon requests HTTP en ningun momento, y no se ejecuto el script de importacion** (regla de proceso vigente + memoria del usuario: nunca smoke test propio del implementador/QA).

CR-17 (unificacion de Proveedor duplicado) y la normalizacion de datos ya cargados de CR-16 fueron ejecutados directamente por el orquestador contra `marihogar_dev` antes de este sprint (no forman parte del codigo de este sprint, confirmado por `5-implementador.md`) — no se re-abren, solo se verifica de paso que los datos siguen consistentes (ver Verificacion 3).

### Verificacion 1 — Sin migracion EF (CONFIRMADO)

`dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` (re-ejecutado por QA) → **12 migraciones, ninguna nueva**, la ultima sigue siendo `20260728001312_AddOrdenCompraGastoVentaCamposCR10a12` (de Sprint CR-E). Carpeta `MariHogar.Infrastructure/Data/Migrations/` sin archivos nuevos desde CR-E. Coincide exacto con la Arquitectura v4 ("Sin migracion EF — todos los cambios son de comportamiento").

### Verificacion 2 — CR-14: saldo acumulado, orden y signo correctos (CONFIRMADO por lectura + reproduccion SQL independiente)

Lectura completa de `CCLocalService.ObtenerSaldosAcumuladosAsync()` (privado) y `CCProveedorService.ObtenerSaldosAcumuladosAsync(int proveedorId)` (privado, sobrecarga distinta de la ya existente `ObtenerSaldosAsync(IEnumerable<int>)` de Sprint 4): ambos traen el ledger completo (`AsNoTracking`, sin paginar) ordenado por `Fecha` asc `ThenBy(m => m.Id)` asc (desempate estable), acumulan en un `Dictionary<int, decimal>` iterando en ese orden, y el listado (`ListarAsync`/`ListarMovimientosAsync`) sigue paginando/filtrando en SQL como antes — el `Saldo` se pega despues en memoria por `Id` sobre la pagina ya traida, exactamente como describe la Arquitectura v4. Signos confirmados por lectura de los enums reales: `CCLocalService` usa `TipoMovimientoCC.Ingreso` (suma) / resto (resta); `CCProveedorService` usa `TipoMovimientoCCProveedor.Cargo` (suma) / resto (resta) — nombres de enum efectivamente distintos entre ambas entidades tal como advertia el brief, ambos confirmados correctos contra `ObtenerSaldoActualAsync` (Sprint 2/4, sin cambios) del mismo servicio.

**Reproduccion SQL independiente contra `marihogar_dev`** (no solo lectura de codigo): se replico el mismo algoritmo con `SUM(CASE WHEN Tipo=... THEN Monto ELSE -Monto END) OVER (ORDER BY Fecha ASC, Id ASC)` directo en MySQL:

- `MovimientosCCProveedor` del Proveedor Id=1 (44 movimientos, todos `Cargo`): la ventana SQL reproduce exactamente el acumulado esperado fila por fila (verificado a mano las primeras 6 filas: 409.761,98 → 1.021.859,50 → 1.374.742,14 → 1.587.763,62 → 2.282.283,45 → 3.329.134,25) y el saldo final (20.754.387,70) coincide con `SUM(Cargo)-SUM(Pago)` directo — mismo resultado que produciria el codigo real.
- `MovimientosCCLocal` (635 Ingreso `Venta` + 480 Egreso `Gasto`): mismo patron, primeras 8 filas verificadas a mano, saldo final $64.877.865,31.
- **Hallazgo de contexto no funcional (explica por que hoy ningun proveedor tiene un `Pago`)**: `PagosOrdenCompra` tiene 0 filas en `marihogar_dev` (las 239 `OrdenesCompra` importadas por CR-6/CR-D quedaron todas `Recibida` con `Cargo` posteado, pero el importador no genera pagos historicos) — coherente con el proposito de CR-18 (el saldo de cada proveedor hoy es integramente su `Cargo` acumulado, exactamente lo que el ajuste de apertura debe llevar a $0).

### Verificacion 3 — CR-16-codigo: mayusculas en Crear y Editar, sin riesgo de `StringLength` (CONFIRMADO)

`ProveedorService.CreateAsync`/`UpdateAsync` (lineas 90/114) y `ProductoService.CreateAsync`/`UpdateAsync` (lineas 141/173) aplican `.Trim().ToUpperInvariant()` a `RazonSocial`/`Nombre` en los 4 metodos (Crear y Editar de ambas entidades, sin excepcion). El `[StringLength]` que valida el largo maximo vive en el ViewModel (`ProveedorViewModels.cs` linea 16, `ProductoViewModels.cs` linea 21) y se evalua por `ModelState` **antes** de que el Service reciba el input — `ToUpperInvariant()` no cambia el largo de caracteres estandar (solo mapea case), por lo que un valor que ya paso la validacion de longitud no puede excederla al normalizarse. Sin riesgo de `DbUpdateException` por truncamiento.

Query real contra `marihogar_dev` (datos ya normalizados por el orquestador antes de este sprint, per `trazabilidad.md`): `SELECT COUNT(*), SUM(RazonSocial = UPPER(RazonSocial)) FROM Proveedores WHERE DeletedAt IS NULL` → **25/25 en mayusculas**; `SELECT COUNT(*), SUM(Nombre = UPPER(Nombre)) FROM Productos WHERE DeletedAt IS NULL` → **207/207 en mayusculas**. Sin filas pendientes, confirma que la normalizacion de datos previa al sprint sigue intacta y que el codigo nuevo no la contradice.

### Verificacion 4 — CR-15: guard "solo si no habia dato previo" confirmado, sin pisar fecha ya cargada por el usuario (CONFIRMADO)

Lectura completa del handler `change` de `.sel-metodo-oc` (`OrdenesCompra/Details.cshtml`, linea 301-316): al pasar el metodo a Cheque (valor 4), usa `if (!pagos[idx].fechaEmisionCheque) pagos[idx].fechaEmisionCheque = moment().format('YYYY-MM-DD')` y `if (!pagos[idx].cuota) pagos[idx].cuota = 30` — ambos guardados por **truthiness** del valor ya presente en el array JS `pagos` (estado en memoria de la pantalla, no releido del DOM), que solo se modifica por los handlers `input` de `.inp-cheque-emision`/`.inp-cheque-cuota` (lineas 335-343). Consecuencia verificada por lectura: cambiar el metodo a Cheque, luego a otro metodo, y volver a Cheque **no borra `pagos[idx].fechaEmisionCheque`/`cuota`** (ningun handler los limpia al cambiar de metodo) — por lo que el guard `if (!...)` los encuentra ya poblados en la segunda vuelta y no los pisa, cumpliendo exactamente el caso de borde pedido en el brief ("cambiarlo a otra cosa y volver a Cheque no debe pisar la fecha que el usuario ya puso"). El valor por defecto usado (`moment().format('YYYY-MM-DD')` = hoy exacto) es compatible con el guard server-side ya existente de `PagoOrdenCompraService.RegistrarPagoAsync` (linea 70, catalogado como MH-003, sin cambios en este sprint) que rechaza `FechaEmisionCheque > DateTime.Today` — el default nunca dispara ese guard. Sin cambio en `Ventas/Create.cshtml` (confirmado, Cheque sigue exclusivo de Compras).

### Verificacion 5 — CR-18: signo del ajuste correcto, `OrigenTipo`/`OrigenId`/`Descripcion` distinguibles, script NO ejecutado (CONFIRMADO)

Lectura completa del bloque "6) AJUSTE DE APERTURA (CR-18)" (`tools/ImportarHistorico/Program.cs`, lineas 657-736): `fechaCorte` = maximo entre la ultima fecha de `MovimientosCCLocal` y de `MovimientosCCProveedor` ya importados (nunca `DateTime.UtcNow` salvo que ambos ledgers esten vacios, caso no aplicable aqui). CC Local: si `saldoLocal != 0`, crea un movimiento de **signo contrario** (`saldoLocal > 0 ? Egreso : Ingreso`) por `Math.Abs(saldoLocal)` — signo correcto para llevar el saldo exactamente a 0. CC Proveedores: mismo mecanismo por cada `ProveedorId` con `saldoProveedor != 0` (`saldoProveedor > 0 ? Pago : Cargo`), agrupado con una unica query `GroupBy(ProveedorId)` antes del loop (sin N+1). Ambos usan `OrigenTipo="AjusteApertura"` (valor de texto libre nuevo, no colisiona con `"Venta"`/`"Gasto"`/`"OrdenCompra"` ya usados), `OrigenId=0` (sin entidad de origen real, distinguible de cualquier Id real que siempre es >0) y `Descripcion="Ajuste de apertura — saldo migrado a $0 para inicio de operación real"` (texto explicito, distinto de cualquier descripcion generada por las demas secciones del importador). Contador `Reporte.AjustesAperturaCreados` reflejado en el resumen final.

**Simulacion a mano contra datos reales de `marihogar_dev`** (sin ejecutar el script): con los saldos ya calculados en la Verificacion 2, si el bloque corriera hoy generaria (a) 1 movimiento `MovimientoCCLocal` de `Egreso` por **$64.877.865,31** (saldo local positivo → egreso de igual monto → saldo final $0, verificado algebraicamente) y (b) 1 movimiento `MovimientoCCProveedor` de `Pago` por cada uno de los proveedores con `Cargo` acumulado != 0 (todos los que tienen movimientos hoy, ya que ninguno tiene `Pago` — ver Verificacion 2), cada uno por el monto exacto de su `Cargo` acumulado, llevando su saldo a $0. Matematicamente correcto por construccion (resta exacta del saldo ya computado, no una formula aproximada).

**Confirmado que el script NO se ejecuto** en este sprint: `SELECT OrigenTipo, COUNT(*) FROM MovimientosCCLocal/MovimientosCCProveedor GROUP BY OrigenTipo` → sin ninguna fila `AjusteApertura` en ninguna de las 2 tablas. Conteos generales re-verificados e identicos a la corrida de CR-D/CR-E: `Proveedores`=31, `OrdenesCompra`=239, `Ventas`=635 (movimientos `Venta` en CC Local), `Gastos`=480 (movimientos `Gasto` en CC Local), `ComprobantesAfip`=0 (confirma tambien que el bloque de CR-13-refinamiento, mas abajo, tampoco se ejecuto) — sin duplicados, sin re-ejecucion.

### Verificacion 6 — Refinamiento CR-13: `ClienteCUIT` desde la columna correcta, misma fila que `ClienteNombre` (CONFIRMADO)

Lectura de la seccion Ventas del importador (lineas 439-449): `clienteNombre = GetStr(ws, primeraFila, 5)` (columna 5) y, inmediatamente despues, `clienteCuit = GetStr(ws, primeraFila, 6)` (columna 6, "CUIT / DNI") — **misma variable `primeraFila`** (primera fila del grupo de lineas de esa Venta), mismo criterio ya usado para `notaInterna`/`puntoVentaStr`/`nroFacturaStr` en el mismo bloque. Asignado a `ComprobanteAfip.ClienteCUIT = clienteCuit` (linea 559) dentro del bloque condicional `tieneFacturaReal` (Punto de Venta + Nº Factura reales, ya validado en Sprint CR-D como refinamiento de CR-13) — mismo objeto y mismo punto donde ya se crea el comprobante historico, sin logica nueva de busqueda de fila. `ComprobanteAfip.ClienteCUIT` es `string?` (sin `[Required]`) con `HasMaxLength(20)` en `AppDbContext.cs` (linea 484) — el valor real esperado ("11111111", 8 caracteres, confirmado por el reconteo del Analisis v7) entra holgadamente, sin riesgo de truncamiento.

### Observacion de documentacion (no defecto de codigo) — conteo de archivos tocados

`5-implementador.md` (Sprint CR-F) declara "7 archivos tocados (2 Services de CC + 2 DTOs + 2 Services de normalizacion + 1 vista de OC + 1 script de importacion)", pero la propia seccion de CR-14 describe explicitamente 2 vistas modificadas (`Views/CCLocal/Index.cshtml` y `Views/Proveedores/CuentaCorriente.cshtml`) ademas de las 2 DTOs — el conteo real de archivos de codigo con cambios funcionales de este sprint es **10**, no 7: `CCLocalService.cs`, `CCProveedorService.cs`, `CCLocalDtos.cs`, `CCProveedorDtos.cs`, `Views/CCLocal/Index.cshtml`, `Views/Proveedores/CuentaCorriente.cshtml`, `ProveedorService.cs`, `ProductoService.cs`, `Views/OrdenesCompra/Details.cshtml`, `tools/ImportarHistorico/Program.cs`. Confirmado por lectura directa de cada uno de los 10 (ver Verificaciones 2 a 6 arriba) — sin ningun archivo faltante ni de mas, es un error de conteo en la prosa del cierre del implementador, mismo tipo de hallazgo ya catalogado sin impacto funcional en Sprint CR-E ("5 vs 4 campos"). No amerita accion mas alla de dejarlo documentado.

### Cobertura de historias de usuario

| HU | Criterio de aceptacion | Resultado |
|---|---|---|
| HU-11.4 (CR-14) | Columna "Saldo" en CC Local, acumulado desde el primer movimiento, orden cronologico con desempate por Id | CUMPLE — confirmado por lectura + reproduccion SQL independiente |
| HU-13.3 (CR-14) | Mismo criterio, acotado al detalle de CC de cada Proveedor | CUMPLE — confirmado por lectura + reproduccion SQL independiente |
| HU-12.9 (CR-15) | Al elegir Cheque sin fecha cargada: hoy + Cuota=30 (editables), dispara autocalculo de vencimiento; no pisa fecha ya cargada al volver a Cheque | CUMPLE — confirmado por lectura completa del handler JS |
| HU-2.5 (CR-16) | RazonSocial/Nombre siempre en mayusculas al guardar (Crear y Editar), sin pedir nada nuevo en el formulario | CUMPLE — confirmado por lectura de los 4 metodos + verificacion de `[StringLength]` |
| Refinamiento CR-13 | `ClienteCUIT` leido de "CUIT / DNI" (col. 6), misma fila que ClienteNombre | CUMPLE — confirmado por lectura del bloque completo |
| CR-18 (sin HU dedicada, cambio de script) | Ajuste de apertura de signo contrario, monto exacto, `OrigenTipo`/`OrigenId`/`Descripcion` distinguibles, script no ejecutado | CUMPLE — confirmado por lectura + simulacion matematica con datos reales |

### Cobertura de maquina de estados

No aplica — confirmado por lectura de codigo que ninguno de los 5 items toca `EstadoOrdenCompra`, `EstadoCheque`, `EstadoVenta` ni ningun metodo de transicion de `OrdenCompraService`/`ChequeService`/`VentaService`. CR-14 es una proyeccion de lectura (no persistida), CR-15 es JS puro, CR-16 es normalizacion de texto, CR-18/CR-13-refinamiento son ajustes de un script de importacion fuera de cualquier maquina de estados de la aplicacion web. Mismo criterio que Arquitectura v4.

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

Foco en los archivos realmente tocados este sprint (`CCLocalService.cs`/`CCProveedorService.cs`, `CCLocalDtos.cs`/`CCProveedorDtos.cs`, `Views/CCLocal/Index.cshtml`/`Views/Proveedores/CuentaCorriente.cshtml`, `ProveedorService.cs`/`ProductoService.cs`, `Views/OrdenesCompra/Details.cshtml`, `tools/ImportarHistorico/Program.cs`). Resto del catalogo ya ejecutado en sprints anteriores sobre los modulos no tocados aqui.

| id | aplica | resultado | accion |
|---|---|---|---|
| REG-001 (RowVersion MySQL) | no | N/A — ninguna entidad con concurrencia optimista tocada en este sprint (`Producto`/`Proveedor` no ganan `RowVersion`, solo se normaliza texto) | ninguna |
| REG-002 a REG-009 | no | N/A — sin autocomplete/cascada/maquina de estados/focus-loss nuevo; CR-15 agrega un guard de precompletado sobre un input ya existente, sin re-render destructivo (confirmado por lectura, `renderPagosOC()` se llama despues de setear los valores, no antes) | ninguna |
| REG-010 (sidebar expone seccion a rol incorrecto) | no | N/A — sin controller/policy/link de sidebar nuevo en este sprint | ninguna |
| DN-001/DN-002 (provider EF6-MySQL, Include+OrderBy+Skip/Take) | no | N/A — provider distinto (`MySql.EntityFrameworkCore` 10.0.1), ya descartado en sprints anteriores. Ademas, el saldo acumulado de CR-14 se calcula deliberadamente **fuera** del pipeline de filtro/orden/paginacion del DataTable (query separada sin `Skip`/`Take`/`OrderBy` dinamico combinados con `Include`), evitando por diseno el patron de riesgo de DN-001 | ninguna |
| GAN-001 a 004 / VSF-001/002 / CRM-001 a 006 / KOI-001 a 006 | no | N/A — modulos/proyectos no relacionados con este sprint | ninguna |
| MH-001 (IN de coleccion local string traducido a SQL) | si (grep + lectura) | PASS — `ObtenerSaldosAcumuladosAsync()` (ambos servicios) no usa ningun `Where(coleccionLocal.Contains(...))`; los `.Contains(` presentes en `ProveedorService.cs`/`ProductoService.cs` son `string.Contains(substring)` de instancia sobre una columna de BD (traducido a `LIKE`), patron distinto y seguro | ninguna |
| MH-002 (enum serializado como int) | no | N/A — `Saldo` es `decimal` (sin enum nuevo); `Tipo` sigue mapeado con `.ToString()` desde antes de este sprint, sin cambios | ninguna |
| MH-003 (fecha futura de cheque sin revalidar server-side) | si (regresion) | PASS — guard server-side de `PagoOrdenCompraService.RegistrarPagoAsync` (linea 70) intacto, sin modificaciones de este sprint; el nuevo default de CR-15 (`moment().format('YYYY-MM-DD')` = hoy exacto) nunca dispara ese guard, confirmado por lectura | ninguna |
| MH-004 (desglose facturado/no facturado de Caja) | no | N/A — `CajaService` no tocado este sprint | ninguna |
| MH-005 (remito publico no revalidaba Estado) | si (re-verificado) | PASS — `VentaService.cs` no fue tocado en este sprint (confirmado, no aparece en la lista de archivos de CR-F); los 3 guards siguen intactos desde CR-E | ninguna |
| MH-006 (WhatsApp no elegia factura AFIP) | si (re-verificado) | PASS — mismo motivo que MH-005, `VentaService.cs` sin cambios este sprint | ninguna |

### Defectos detectados

**Ninguno de severidad blocker/critical/major/minor en el codigo de este sprint.** Una observacion documental de bajo riesgo, sin impacto funcional (ver "Observacion de documentacion" arriba): `5-implementador.md` cuenta "7 archivos tocados" cuando son 10 (incluye las 2 vistas de CR-14 que la propia seccion del sprint sí describe, solo faltan del resumen de conteo) — mismo patron de imprecision de conteo ya visto y aceptado en Sprint CR-E ("5 vs 4 campos"), sin riesgo de codigo faltante (los 10 archivos fueron leidos y verificados uno por uno).

### Auto-fixes aplicados en este ciclo

**Ninguno.** No se reprodujo ningun bug funcional ni de datos — build limpio en ambos proyectos, sin migracion EF (confirmado contra la Arquitectura v4), calculo de saldo acumulado de CR-14 reproducido de forma independiente con SQL de ventana y coincidente fila por fila con la logica del codigo, guard de CR-15 confirmado que no pisa datos ya cargados por el usuario, normalizacion de CR-16 sin riesgo de truncamiento, ajuste de apertura de CR-18 matematicamente correcto por simulacion con datos reales y confirmado sin ejecutar, y refinamiento de CR-13 leyendo la columna correcta.

### Evidencia de build y migracion (re-verificado por QA de forma independiente)

- `dotnet build MariHogar.slnx` → **Compilacion correcta, 0 errores**, 9 warnings preexistentes (NU1902 MailKit/MimeKit x2 c/u, CS0114 `HomeController.StatusCode`), ninguno nuevo.
- `dotnet build tools/ImportarHistorico/ImportarHistorico.csproj` → **Compilacion correcta, 0 errores**, mismos warnings NU1902 heredados, ninguno nuevo del proyecto de consola.
- `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` → **12 migraciones, ninguna nueva** desde CR-E (`...AddOrdenCompraGastoVentaCamposCR10a12` sigue siendo la ultima). Carpeta `Migrations/` sin archivos nuevos, confirmado por listado directo.
- Queries reales contra `marihogar_dev` (`mysql.exe` de MySQL Server 8.0 local, ejecutadas por QA de forma independiente): conteos generales (`Proveedores`=31, `OrdenesCompra`=239, `Ventas`=635, `Gastos`=480, `MovimientosCCLocal`=1115, `MovimientosCCProveedor`=239, `ComprobantesAfip`=0) identicos a la corrida de CR-D/CR-E, sin fila `AjusteApertura` en ningun ledger (confirma que el script no se re-ejecuto); reproduccion con funcion de ventana SQL (`SUM(...) OVER (ORDER BY Fecha, Id)`) del calculo de saldo acumulado sobre el Proveedor Id=1 (44 movimientos) y sobre CC Local completo (1115 movimientos), coincidente con la logica del codigo; verificacion de mayusculas 25/25 Proveedores y 207/207 Productos activos.
- Lectura completa y propia de: `CCLocalService.cs`, `CCProveedorService.cs` (metodos completos, no solo lineas nuevas), `CCLocalDtos.cs`, `CCProveedorDtos.cs`, `Views/CCLocal/Index.cshtml`, `Views/Proveedores/CuentaCorriente.cshtml` (JS de columnas y colores completo), `ProveedorService.cs`, `ProductoService.cs` (los 4 metodos Create/Update), `ProveedorViewModels.cs`/`ProductoViewModels.cs` (StringLength), `Views/OrdenesCompra/Details.cshtml` (bloque JS de CR-15 completo, lineas 261-343), `PagoOrdenCompraService.cs` (guard MH-003, confirmado sin cambios), `tools/ImportarHistorico/Program.cs` (bloque CR-18 lineas 656-754 completo + bloque CR-13-refinamiento lineas 430-565), `ComprobanteAfip.cs`/`AppDbContext.cs` (`HasMaxLength(20)` de `ClienteCUIT`).

### Riesgos de liberacion

- **Ninguno de severidad blocker/critical.**
- **Bajo (documentacion)**: `5-implementador.md` cuenta "7 archivos tocados" cuando son 10 (faltan las 2 vistas de CR-14 en el resumen, aunque la seccion del sprint si las describe) — sin impacto funcional.
- **Bajo (aceptado explicitamente en Arquitectura v4, sin cambio de este sprint)**: el calculo de saldo acumulado de CR-14 trae el ledger completo a memoria en cada `GetData` — costo O(n) aceptado por volumen bajo hoy (1115 movimientos en CC Local, 239 en CC Proveedores); a revisar si el volumen crece mucho.
- **Bajo, heredado, sin cambio en este ciclo**: 5 migraciones acumuladas del Change Request (`AddImpuestosOCyChequeEmision`, `AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2`, `AddTokenDescargaPublicaVenta`, `AddProveedorCamposFiscales`, `AddOrdenCompraGastoVentaCamposCR10a12`) todavia sin aplicar contra produccion — este sprint no agrega una sexta (sin migracion EF).
- **Bajo (proceso, no bloqueante)**: CR-18 y el refinamiento de CR-13 dejan el script de importacion ajustado pero sin ejecutar, tal como pide el alcance — cuando el cliente autorice correr `tools/ImportarHistorico/` de nuevo contra `marihogar_dev` (o directamente contra produccion, tras el vaciado ya documentado en CR-6), corresponde repetir la verificacion por query real (`SUM(...)` = 0 exacto en CC Local y en cada CC Proveedor) antes de dar esa corrida por buena — ya señalado como pendiente por el propio implementador.
- Produccion confirmada sin tocar en este sprint (sin cambios en `appsettings.Production.json`, sin ejecucion del importador).

### Pruebas minimas ejecutadas

- `dotnet build MariHogar.slnx` y `dotnet build tools/ImportarHistorico/ImportarHistorico.csproj` → 0 errores en ambos, re-verificado de forma independiente.
- `dotnet ef migrations list` → 12 migraciones, ninguna nueva desde CR-E.
- Lectura completa y propia de los 10 archivos con cambios funcionales de este sprint (no solo los 7 declarados).
- Reproduccion SQL independiente (funcion de ventana) del calculo de saldo acumulado de CR-14 sobre CC Local completo y sobre el Proveedor con mas movimientos, comparado fila por fila contra el algoritmo del codigo.
- Simulacion matematica del monto que generaria el ajuste de apertura de CR-18 (CC Local y cada CC Proveedor) usando los saldos reales ya calculados, sin ejecutar el script.
- Verificacion de mayusculas real contra `marihogar_dev` (25/25 Proveedores, 207/207 Productos activos).
- Verificacion de ausencia de movimientos `AjusteApertura` y de `ComprobantesAfip` en `marihogar_dev` (confirma que ni CR-18 ni el refinamiento de CR-13 se ejecutaron).
- Ejecucion del playbook cross-proyecto acotado a los archivos tocados (12 items evaluados explicitamente, resto N/A por modulo/patron no aplicable).

### Checklist de salida para merge

- [x] Build limpio (0 errores) en solucion principal y en el proyecto de consola, re-verificado por QA de forma independiente.
- [x] Sin migracion EF (confirmado con `dotnet ef migrations list` + listado directo de la carpeta `Migrations/`), consistente con la Arquitectura v4.
- [x] CR-14: saldo acumulado con orden `Fecha, Id` y signo correcto, confirmado por lectura + reproduccion SQL independiente (no solo por lo declarado).
- [x] CR-15: guard "solo si no habia dato previo" confirmado por lectura completa del JS, incluido el caso de borde cheque→otro metodo→cheque.
- [x] CR-16: normalizacion en los 4 metodos (Crear/Editar x2 entidades), sin riesgo de `StringLength`, datos ya cargados verificados 100% en mayusculas.
- [x] CR-18: signo del ajuste correcto, `OrigenTipo`/`OrigenId`/`Descripcion` distinguibles, monto matematicamente correcto (simulado con datos reales), script confirmado sin ejecutar.
- [x] Refinamiento CR-13: `ClienteCUIT` leido de la columna correcta, misma fila que `ClienteNombre`.
- [x] Produccion confirmada sin tocar.
- [x] Playbook cross-proyecto ejecutado, 0 regresiones reproducidas, 0 auto-fixes necesarios.
- [ ] Verificacion visual en navegador de los 4 puntos de UI (columna Saldo en CC Local y en Proveedores, autocompletado de cheque en OC, mayusculas en Proveedor/Producto) — pendiente del usuario, checklist ya dejada por el implementador en `5-implementador.md`.
- [ ] Corrida real de `tools/ImportarHistorico/` (con CR-18 y refinamiento de CR-13 incluidos) contra `marihogar_dev`/produccion — sigue en pausa por decision del cliente, sin relacion con la calidad del codigo entregado.
- [ ] Las 5 migraciones acumuladas del Change Request siguen pendientes de aplicar contra produccion.

### Estado go/no-go

**GO para dar por cerrado tecnicamente el Sprint CR-F.** Sin defectos de ninguna severidad bloqueante encontrados en los 5 items. El calculo mas sensible del sprint (saldo acumulado de CR-14) fue verificado no solo por lectura de codigo sino por una reproduccion SQL independiente (funcion de ventana) contra datos reales de `marihogar_dev`, coincidente fila por fila con el algoritmo del servicio. El caso de borde explicitamente pedido en el brief para CR-15 (cambiar a Cheque, cambiar a otro metodo, volver a Cheque sin perder la fecha ya cargada por el usuario) fue confirmado por lectura completa del handler JS, no solo asumido. CR-16 confirmado sin riesgo de truncamiento de datos. CR-18 confirmado matematicamente correcto por simulacion con los saldos reales ya presentes en la base (el ajuste, si se ejecutara hoy, llevaria CC Local y cada CC Proveedor exactamente a $0) y confirmado que el script no fue ejecutado. Refinamiento de CR-13 confirmado leyendo la columna correcta en la misma fila que ya usa `ClienteNombre`. Sin migracion EF (consistente con la Arquitectura v4). Produccion confirmada sin tocar en ningun momento. Una unica observacion documental de bajo riesgo (conteo "7 vs 10 archivos" en la prosa de cierre del implementador, sin impacto de codigo) no amerita auto-fix ni bloquea el cierre. **Recomendacion: dar el Sprint CR-F por terminado desde el punto de vista de QA, y con el Change Request #1 completo (CR-1 a CR-18 + refinamientos de CR-13) en estado GO desde el punto de vista de calidad de codigo**, a la espera de que el cliente/orquestador coordinen (1) la ejecucion real de `tools/ImportarHistorico/` (CR-6, con CR-13/CR-18 ya incorporados) contra `marihogar_dev` de nuevo y luego produccion, y (2) la aplicacion de las 5 migraciones acumuladas contra produccion — ambas en pausa por decision del cliente, sin relacion con la calidad del codigo entregado.

---
## Sprint CR-E (Change Request #1, post-Etapa 1, ampliacion sobre CR-D) — CR-10/CR-11/CR-12: auditoria de columnas del historico

### Alcance validado

Undecima ejecucion de QA sobre marihogar. Valida los 3 campos nuevos declarados por el implementador: `OrdenCompra.PuntoVenta`/`NumeroComprobante` (CR-10, HU-12.8), `Gasto.Subcategoria` (CR-11, HU-18.4) y `Venta.NotaInterna` (CR-12, HU-5.13), mas el ajuste correspondiente de `tools/ImportarHistorico/Program.cs` (sin ejecutar). Contra `1-analista-funcional.md` (Analisis v5), `2-disenador-funcional.md` (Diseno v4) y `3-arquitecto-mvc.md` (Arquitectura v3). Metodo: (1) lectura completa y propia de las 5 capas tocadas (Domain/Application/Infrastructure/Web/importador), sin confiar en lo declarado por el implementador; (2) `dotnet build MariHogar.slnx` y `dotnet build tools/ImportarHistorico/ImportarHistorico.csproj` re-ejecutados de forma independiente; (3) `dotnet ef migrations list` re-ejecutado; (4) queries reales propias contra `marihogar_dev` (`mysql.exe` de MySQL Server 8.0 local) para confirmar esquema y conteo de `NULL`; (5) grep exhaustivo de `NotaInterna` sobre todo el repo y lectura linea por linea de los 3 metodos de generacion/servido de PDF (`GenerarRemitoPdfAsync`, `ObtenerOCrearTokenDescargaPublicaAsync`, `GenerarRemitoPdfPorTokenAsync`, `GenerarRemitoPdfInterno`) para el punto de seguridad explicito de CR-12. **No se levanto la app ni se simularon requests HTTP en ningun momento** (regla de proceso vigente + memoria del usuario: nunca smoke test propio del implementador/QA).

**Nota sobre el build**: el primer intento de `dotnet build MariHogar.slnx --no-incremental` devolvio 6 errores `MSB3027`/`MSB3021` ("no se pudo copiar ... because it is being used by another process"). Investigado: no es un error de compilacion del codigo — un proceso de depuracion de VS Code dejado corriendo (`dotnet.exe` PID 23560 + `vsdbg-ui.exe` PID 24868, iniciados 21:19:33) tenia bloqueados los DLL de salida de `MariHogar.Web/bin/Debug`. Se re-verifico compilando `MariHogar.Web` con `-o` a un directorio de salida alternativo (sin tocar el proceso de depuracion del usuario, sin matarlo) — **0 errores, mismos warnings preexistentes** (NU1902 MailKit/MimeKit, CS0114 `HomeController.StatusCode`). Confirmado: el codigo compila limpio: el 6/6 de errores previo era 100% un artefacto del entorno (lock de archivo por un debugger activo), no un defecto de este sprint.

### Verificacion 1 — Migracion EF: solo columnas nullable, sin script de datos (CONFIRMADO)

Lectura completa de `MariHogar.Infrastructure/Data/Migrations/20260728001312_AddOrdenCompraGastoVentaCamposCR10a12.cs`: el `Up()` tiene exactamente 4 `AddColumn` (`NotaInterna` en `Ventas` varchar(500), `NumeroComprobante` en `OrdenesCompra` varchar(20), `PuntoVenta` en `OrdenesCompra` varchar(10), `Subcategoria` en `Gastos` varchar(100)), todas `nullable: true`, sin ningun `UPDATE`/script de datos ni `Sql(...)`. El `Down()` es el `DropColumn` simetrico de las 4. Migracion aditiva pura, confirmada segura por lectura directa, no solo por lo declarado.

**Observacion menor de documentacion (no defecto de codigo)**: `5-implementador.md` (Sprint CR-E) dice repetidamente "5 campos nuevos"/"Fluent config de los 5 campos nuevos" — el conteo real, verificado por la migracion y por los 3 entities (`OrdenCompra.cs`, `Gasto.cs`, `Venta.cs`), es **4** (2 en `OrdenCompra` + 1 en `Gasto` + 1 en `Venta`), consistente con lo que la propia Arquitectura v3 especifico (2+1+1=4). Es un error de conteo en la prosa del implementador, sin ningun campo faltante ni de mas — no afecta el codigo ni los datos, se documenta solo para prolijidad de trazabilidad.

`dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` (re-ejecutado por QA) → **12 migraciones, ninguna `(Pending)`**, `...AddOrdenCompraGastoVentaCamposCR10a12` es la ultima, coincide exacto con lo declarado.

### Verificacion 2 — Esquema y datos reales en `marihogar_dev` (CONFIRMADO, reconteo independiente)

Queries propias via `mysql.exe` (no se confio en el reporte del implementador):

| Verificacion | Declarado | Reconteo QA | Coincide |
|---|---|---|---|
| `DESCRIBE OrdenesCompra` → `PuntoVenta`/`NumeroComprobante` | `varchar(10)`/`varchar(20)` NULL | `varchar(10)`/`varchar(20)` YES NULL | Si |
| `DESCRIBE Gastos` → `Subcategoria` | `varchar(100)` NULL | `varchar(100)` YES NULL | Si |
| `DESCRIBE Ventas` → `NotaInterna` | `varchar(500)` NULL | `varchar(500)` YES NULL | Si |
| `OrdenesCompra` con `PuntoVenta`/`NumeroComprobante` NULL | 239/239 | 239/239 | Si |
| `Gastos` con `Subcategoria` NULL | 480/480 | 480/480 | Si |
| `Ventas` con `NotaInterna` NULL | 634/634 | 634/634 | Si |
| `__EFMigrationsHistory` | 12 migraciones | 12 migraciones | Si |
| `Proveedores` / `Productos` (sin re-ejecucion del importador) | 31 / 207 | 31 / 207 | Si |

**El 100% de las filas ya cargadas (import de CR-D) quedaron en `NULL` en los 4 campos nuevos**, tal como corresponde a una migracion aditiva sin script de datos. Los conteos de `Proveedores`/`Productos` identicos a los ya verificados en el ciclo de QA de CR-D **confirman que el importador NO se re-ejecuto** en este sprint (tal como declara el implementador), sin duplicacion de datos.

### Verificacion 3 — CR-10 (HU-12.8): condicional a Facturada, opcional, filtro y columna nuevos (CONFIRMADO)

Lectura de `OrdenesCompra/Create.cshtml`: los inputs `PuntoVenta`/`NumeroComprobante` (lineas 84-94) viven dentro del mismo `<div id="contTipoComprobante">` que ya togglea `actualizarVisibilidadComprobante()` segun el radio `Facturada` (patron ya usado por `TipoComprobante` desde CR-1) — visibles/ocultos automaticamente, sin JS adicional necesario, confirmado por lectura del script completo de la vista. `Details.cshtml` muestra la linea "PuntoVenta-NumeroComprobante" solo si al menos uno de los 2 tiene dato. `OrdenCompraService.ValidarComprobante` (linea 206-216) solo exige `TipoComprobante` cuando `Facturada=true` — **`PuntoVenta`/`NumeroComprobante` nunca son obligatorios**, confirmado por lectura del metodo completo (no hay ningun `return` de error que los mencione). `AplicarComprobanteEImpuestos` (linea 222-249) los persiste trimeados/null cuando `Facturada=true` y los fuerza a `null` cuando `Facturada=false`, mismo patron defensivo que el resto de los campos del bloque comprobante. `Edit(int id)` (GET, linea 103-139) precarga ambos campos desde el DTO — no quedan vacios al reabrir una OC en Borrador ya facturada (regla `32-estandares-qa-implementador.instructions.md`). Filtro "Comprobante" en `Index.cshtml`: `OrdenCompraService.ListarAsync` filtra con `Contains` sobre ambos campos con null-check explicito (linea 55-58); columna "Comprobante" en el grid con `data:'puntoVenta'`/`row.numeroComprobante`, casing camelCase confirmado consistente con la serializacion JSON por defecto de ASP.NET Core y con `OrdenCompraListItemDto.PuntoVenta`/`NumeroComprobante`.

### Verificacion 4 — CR-11 (HU-18.4): filtro de texto amplia sobre el mismo campo, sin duplicar (CONFIRMADO)

`Gastos/Create.cshtml`: input `Subcategoria` debajo del select de Categoria (linea 31-35), opcional, sin `[Required]`. `Gastos/Index.cshtml`: la columna Categoria renderiza la Subcategoria como linea secundaria (`row.subcategoria`, linea 122-124); el placeholder del filtro de texto se actualizo ("Buscar por descripcion o subcategoria...") y sigue siendo **el mismo input** `filtroDescripcion` (no se agrego un filtro dedicado nuevo, tal como exige el diseno). `GastoService.ListarAsync` (linea 39-41): `query.Where(g => g.Descripcion.Contains(filtro.Descripcion) || (g.Subcategoria != null && g.Subcategoria.Contains(filtro.Descripcion)))` — confirmado que ahora busca en ambos campos con el null-check correcto sobre `Subcategoria` (nullable). `CrearAsync` persiste `Subcategoria` trimeada o `null`. Sin pantalla de Edit para Gasto (confirmado, sigue sin existir — comportamiento inmutable de Sprint 5 sin cambios).

### Verificacion 5 — CR-12 (HU-5.13), punto critico de seguridad: `NotaInterna` NUNCA se filtra a un PDF (CONFIRMADO por lectura completa, no por grep parcial)

Grep exhaustivo de `NotaInterna` sobre todo el repo (`C:/Sistemas/marihogar`): **10 archivos**, todos esperables — `tools/ImportarHistorico/Program.cs` (asignacion del importador), `VentaService.cs` (linea 155 mapeo a DTO de detalle, linea 259 persistencia en `ConfirmarAsync`), `Venta.cs` (Domain), `AppDbContext.cs` (fluent config), `VentaDtos.cs` (x2, `VentaDetailDto` y `VentaInput`), `AppDbContextModelSnapshot.cs` + la migracion (metadata EF, no logica), `Ventas/Details.cshtml` (la card nueva) y `VentasController.cs` (parseo del form). **Cero ocurrencias en cualquier archivo de generacion de PDF.**

Verificacion dirigida y completa (no solo grep) de los 3 metodos senalados explicitamente por el alcance:
- `VentaService.GenerarRemitoPdfAsync` (linea 393-406): consulta la Venta, aplica el guard de Estado (MH-005, sin cambios de este sprint), llama a `GenerarRemitoPdfInterno(v)`. Sin referencia a `NotaInterna`.
- `VentaService.GenerarRemitoPdfPorTokenAsync` (linea 430-465): busca por token, aplica el mismo guard de Estado, decide remito-vs-factura-AFIP (MH-006, sin cambios de este sprint), delega en `GenerarRemitoPdfInterno(v)` o `IComprobanteAfipService.GenerarPdfAsync`. Sin referencia a `NotaInterna`.
- `VentaService.GenerarRemitoPdfInterno` (linea 476-543, privado, static): lei el metodo completo — arma el documento QuestPDF con Cliente (Nombre/Telefono), tabla de items (Producto/Cantidad/PrecioUnitario/Subtotal), Total y footer. **Ningun `col.Item()`/`c.Item()` referencia `v.NotaInterna`** — confirmado leyendo las ~70 lineas completas del metodo, no solo buscando el string.
- `ComprobanteAfipService.cs` (generador de la factura AFIP): grep de `NotaInterna` sobre el archivo → 0 coincidencias (ya reflejado en el grep global de arriba). El comprobante AFIP no tiene forma de acceder al campo (no esta en el `Include`/proyeccion de `Venta` que usa ese servicio).

**Conclusion: el punto de seguridad/alcance mas critico de este sprint (CA-CR12.1 — "nunca en el remito/comprobante que ve el cliente final") esta confirmado con evidencia de codigo propia de QA, sin ninguna discrepancia respecto de lo declarado por el implementador.**

Resto de CR-12 verificado: `VentaDetailDto.NotaInterna` esta en `VentaDetailDto` (linea 84) y **no** en `VentaListItemDto` — confirmado por lectura de ambas clases, `Ventas/Index.cshtml` no referencia `NotaInterna` en ningun punto (grep confirmado). `Ventas/Create.cshtml`: seccion colapsable `#contNotaInterna` (oculta por defecto, `d-none`) fuera de la tabla de items/panel de pagos, `maxlength="500"` en el textarea (coincide con la columna). `Ventas/Details.cshtml`: card "Nota interna" solo si `v.NotaInterna` tiene valor, con el aviso explicito "Uso interno — no aparece en el remito ni en la factura." `VentasController.Confirmar` parsea `notaInterna` directo de `Request.Form` (mismo patron ya usado para `clienteNombre`/`clienteTelefono` desde Sprint 2, sin ViewModel de binding intermedio).

**Observacion de bajo riesgo, heredada del patron ya existente (no un defecto nuevo de este sprint)**: `NotaInterna` se lee de `Request.Form` sin un `[StringLength]` server-side propio (solo el `maxlength=500` del HTML, bypasseable con un POST directo) — un valor > 500 caracteres provocaria una `DbUpdateException` de MySQL al truncar contra `varchar(500)`. Verificado que **no es un problema nuevo**: `ClienteNombre` (200)/`ClienteTelefono` (50) del mismo controller tienen exactamente el mismo gap desde Sprint 2, sin StringLength server-side propio tampoco, y el `GlobalExceptionHandler` (`Program.cs`, confirmado registrado) ya captura cualquier excepcion no manejada devolviendo una pagina de error generica en vez de un crash — no hay perdida de datos ni fuga de informacion, solo una UX de error generica ante un POST manipulado fuera del uso normal de la UI. No se cataloga como item nuevo del playbook cross-proyecto por ser un patron ya aceptado y pre-existente del propio proyecto, no una regresion de CR-12.

### Verificacion 6 — Ajuste del importador (`tools/ImportarHistorico/Program.cs`): correcto y NO ejecutado (CONFIRMADO)

Lectura de las 2 secciones ajustadas:
- **Gastos** (linea 540-573): la variable `subcategoriaTexto` (columna real del Excel) ya existia como *fallback* de `Descripcion` (sin cambios en esa logica, linea 557-559, confirmado igual que antes). El campo nuevo `Gasto.Subcategoria` se asigna en linea 572 (`string.IsNullOrWhiteSpace(subcategoriaTexto) ? null : subcategoriaTexto.Trim()`), en el mismo objeto `Gasto` que ya arma `Categoria`/`Monto`/`FormaPago`/`Fecha`/`Descripcion` — sin tocar ninguna asignacion previa.
- **Ventas** (linea 439-459): nueva variable `notaInterna = GetStr(ws, primeraFila, 43)?.Trim()` (columna 43, comentario inline confirma la inspeccion real: col 43 = "Nota Interna", col 42 = "Nota para el Cliente" distinta y no tocada), leida de `primeraFila` del grupo (mismo criterio ya usado para `clienteNombre`, columna 5) — asignada a `Venta.NotaInterna` en la construccion del objeto `Venta` (linea 455), sin alterar ninguna asignacion previa (`VendedorId`/`ClienteNombre`/`Estado`/`Fecha`).

Confirmado que el importador **no se re-ejecuto** contra `marihogar_dev` en este sprint (conteos de Proveedores=31/Productos=207 identicos a la corrida de CR-D, ver Verificacion 2) ni contra produccion (sin cambios en `appsettings.Production.json`, confirmado por `git diff --stat` — 0 archivos de configuracion de produccion tocados en todo el working tree).

### Cobertura de historias de usuario

| HU | Criterio de aceptacion | Resultado |
|---|---|---|
| HU-12.8 (CR-10) | Punto de Venta/Nº Comprobante visibles/editables solo con Facturada=true, opcionales, columna+filtro en Index | CUMPLE |
| HU-18.4 (CR-11) | Subcategoria libre bajo Categoria, visible como linea secundaria en Index, filtrable por el mismo cuadro de busqueda ya existente | CUMPLE |
| HU-5.13 (CR-12) | Nota interna libre y opcional en Create (colapsada), visible en Details para Administrador/Vendedor, **nunca** en PDF (remito ni AFIP) | CUMPLE — punto de seguridad verificado con evidencia propia |

### Cobertura de maquina de estados

No aplica — confirmado por lectura de codigo que ninguno de los 3 cambios toca `EstadoOrdenCompra`, `EstadoGasto`(no existe, Gasto es Activo/Anulado por flag) ni `EstadoVenta`, ni ningun metodo de transicion (`OrdenCompraService`/`GastoService`/`VentaService` solo ganan mapeo de 1 campo cada uno). Mismo criterio que Arquitectura v3 ("sin cambio de maquina de estados").

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

Foco en los archivos tocados este sprint (`OrdenCompra.cs`/`Gasto.cs`/`Venta.cs`, `OrdenCompraService.cs`/`GastoService.cs`/`VentaService.cs`, `OrdenesCompra/*.cshtml`, `Gastos/*.cshtml`, `Ventas/Create-Details.cshtml`, `Program.cs` del importador). Resto del catalogo ya ejecutado en sprints anteriores sobre los modulos no tocados aqui.

| id | aplica | resultado | accion |
|---|---|---|---|
| REG-001 (RowVersion MySQL) | no | N/A — `OrdenCompra`/`Gasto`/`Venta` no tienen `RowVersion` (solo `Producto` lo tiene, desde Sprint 5); sin entidad nueva con concurrencia optimista en este sprint | ninguna |
| REG-002 a REG-009 | no | N/A — sin autocomplete/cascada/maquina de estados/focus-loss nuevo; los filtros de texto nuevos (Comprobante en OC, ampliacion del ya existente en Gastos) reusan el mismo patron debounce 300ms ya probado en el resto del proyecto, sin re-render destructivo de tabla (DataTables estandar) | ninguna |
| REG-010 (sidebar expone seccion a rol incorrecto) | no | N/A — sin controller/policy/link de sidebar nuevo en este sprint (solo campos sobre pantallas ya existentes con el mismo gating de rol previo) | ninguna |
| DN-001/DN-002 (provider EF6-MySQL) | no | N/A — proyecto usa `MySql.EntityFrameworkCore` 10.0.1 (provider distinto, ya descartado en sprints anteriores); los filtros nuevos son `Contains` simple sobre columna nullable, sin combinar Include de coleccion + OrderBy dinamico + Skip/Take en la misma IQueryable de forma distinta a los filtros ya existentes de Gasto.Descripcion/Venta.ClienteNombre | ninguna |
| GAN-001 a 004 / VSF-001/002 / CRM-001 a 006 / KOI-001 a 006 | no | N/A — modulos/proyectos no relacionados con este sprint | ninguna |
| MH-001 (IN de coleccion local string traducido a SQL) | si (grep + lectura) | PASS — los 2 filtros nuevos (`OrdenCompraService.ListarAsync` sobre `Comprobante`, `GastoService.ListarAsync` sobre `Descripcion`/`Subcategoria`) usan `Contains` de instancia sobre una columna de BD (traducido a `LIKE`), nunca `Where(coleccionLocal.Contains(...))` sobre una coleccion en memoria — patron distinto y seguro, confirmado por lectura directa de ambos metodos | ninguna |
| MH-002 (enum serializado como int) | no | N/A — sin enum nuevo en este sprint, los 4 campos nuevos son `string?` | ninguna |
| MH-003 (fecha futura de cheque) | no | N/A — modulo Cheques no tocado este sprint | ninguna |
| MH-004 (desglose facturado/no facturado de Caja) | no | N/A — `CajaService` no tocado este sprint (Gasto/Venta ganan un campo, pero ningun metodo de agregacion de Caja/Dashboard/Proyeccion fue modificado, confirmado por `git status` acotado a este sprint) | ninguna |
| MH-005 (remito publico no revalidaba Estado) | si (re-verificado) | PASS — releidos los 3 guards `Estado != Pagada && Estado != PagadaParcial` en `GenerarRemitoPdfAsync`/`ObtenerOCrearTokenDescargaPublicaAsync`/`GenerarRemitoPdfPorTokenAsync`: siguen intactos, sin ninguna modificacion de este sprint (los unicos cambios en `VentaService.cs` de CR-E son `GetByIdAsync`/`ConfirmarAsync`, mapeo/persistencia de `NotaInterna`) | ninguna |
| MH-006 (WhatsApp no elegia factura AFIP) | si (re-verificado) | PASS — `GenerarRemitoPdfPorTokenAsync` sigue consultando `ComprobantesAfip` Emitido antes de caer al remito, sin cambios de este sprint | ninguna |

### Defectos detectados

**Ninguno de severidad blocker/critical/major/minor en el codigo de este sprint.** Dos observaciones documentadas, ninguna catalogada como item nuevo del playbook por no ser regresiones nuevas ni bugs reproducibles con datos reales:
1. Inconsistencia de conteo en la prosa de `5-implementador.md` ("5 campos nuevos" vs. 4 reales) — cosmetica, sin impacto de codigo/datos, detallada en Verificacion 1.
2. `NotaInterna` sin `StringLength` server-side propio ante un POST manipulado (> 500 caracteres) — gap heredado, identico al ya existente para `ClienteNombre`/`ClienteTelefono` desde Sprint 2, mitigado por el `GlobalExceptionHandler` ya vigente. No es una regresion de CR-12.

### Auto-fixes aplicados en este ciclo

**Ninguno.** No se reprodujo ningun bug funcional ni de datos — build limpio, migracion aditiva confirmada segura, los 3 campos se comportan exactamente como especifica el diseno/arquitectura, y el punto de seguridad critico de `NotaInterna` esta confirmado sin filtracion a ningun PDF.

### Evidencia de build y migracion (re-verificado por QA de forma independiente)

- `dotnet build MariHogar.slnx --no-incremental`: primer intento con 6 errores `MSB3027`/`MSB3021` (lock de archivo por un debugger de VS Code activo en el entorno, PID 23560/24868, ajeno a este sprint y a QA); re-verificado compilando `MariHogar.Web/MariHogar.Web.csproj` con `-o` a un directorio alternativo (sin tocar el proceso del usuario) → **Compilacion correcta, 0 errores**, mismos warnings preexistentes (NU1902 MailKit/MimeKit, CS0114 `HomeController.StatusCode`).
- `dotnet build tools/ImportarHistorico/ImportarHistorico.csproj --no-incremental` → **Compilacion correcta, 0 errores** (mismos warnings NU1902 heredados, ninguno nuevo del proyecto de consola).
- `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` → **12 migraciones, ninguna `(Pending)`**, `...AddOrdenCompraGastoVentaCamposCR10a12` es la ultima.
- Queries reales contra `marihogar_dev` (`mysql.exe` de MySQL Server 8.0 local, ejecutadas por QA de forma independiente): `DESCRIBE OrdenesCompra`/`Gastos`/`Ventas` confirman las 4 columnas nuevas con tipo/nullability exactos; conteo de `NULL` 239/239, 480/480, 634/634 (100% de lo ya cargado); `Proveedores`=31/`Productos`=207 identicos a la corrida de CR-D (confirma que el importador no se re-ejecuto).
- Lectura completa y propia de: `OrdenCompra.cs`, `Gasto.cs`, `Venta.cs`, migracion `AddOrdenCompraGastoVentaCamposCR10a12` (Up/Down), `AppDbContext.cs` (fluent config de los 4 campos), `OrdenCompraService.cs` (ValidarComprobante/AplicarComprobanteEImpuestos/ListarAsync completos), `GastoService.cs` (ListarAsync/CrearAsync), `VentaService.cs` (los 4 metodos relevantes de CR-4/CR-12 completos), `OrdenesCompraController.cs` (Edit GET/GetData), `GastosController.cs`, `VentasController.cs`, las 6 vistas tocadas (`OrdenesCompra/Create-Details-Index.cshtml`, `Gastos/Create-Index.cshtml`, `Ventas/Create-Details.cshtml`), y las 2 secciones ajustadas de `tools/ImportarHistorico/Program.cs`.
- Grep exhaustivo de `NotaInterna` sobre todo el repo (10 archivos, todos esperables, cero en generadores de PDF).

### Riesgos de liberacion

- **Ninguno de severidad blocker/critical.** Punto de seguridad critico del sprint (filtracion de `NotaInterna` a un PDF) confirmado sin hallazgos.
- **Bajo (aceptado, heredado, no de este sprint)**: `NotaInterna`/`ClienteNombre`/`ClienteTelefono` sin `StringLength` server-side propio ante un POST manipulado — mitigado por `GlobalExceptionHandler` (respuesta de error generica, sin crash ni fuga de datos).
- **Bajo (documentacion)**: `5-implementador.md` cuenta "5 campos nuevos" cuando son 4 — sin impacto funcional, se dej documentado para que quede prolijo.
- **Bajo, heredado de sprints anteriores, sin cambio en este ciclo**: 5 migraciones acumuladas del Change Request completo (`AddImpuestosOCyChequeEmision`, `AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2`, `AddTokenDescargaPublicaVenta`, `AddProveedorCamposFiscales`, y ahora `AddOrdenCompraGastoVentaCamposCR10a12`) todavia sin aplicar contra produccion — las 5 confirmadas seguras por revision de codigo y verificacion de datos real en sprints sucesivos, coordinables en la misma ventana de mantenimiento junto con la ejecucion de CR-6 (todavia en pausa, decision del cliente).
- **Bajo (proceso, no bloqueante)**: `4-presupuestador.md` sigue con la etiqueta de estado "BORRADOR" en el texto de la seccion CR-10/11/12 pese a que `trazabilidad.md` ya registra la aprobacion explicita del cliente (USD 84, total USD 638) y la orden de arranque posterior — confirmado por QA releyendo ambos documentos (ver seccion Verificacion, gate). Recomendado que el orquestador sincronice la etiqueta.
- Producción confirmada sin tocar en este sprint (sin cambios en `appsettings.Production.json`, sin ejecucion del importador contra produccion).

### Pruebas minimas ejecutadas

- `dotnet build MariHogar.slnx` (con workaround de `-o` por el lock del debugger ajeno) y `dotnet build tools/ImportarHistorico/ImportarHistorico.csproj` → 0 errores en ambos.
- `dotnet ef migrations list` → 12 migraciones, ninguna pendiente.
- Lectura completa y propia de la migracion (Up/Down), las 3 entidades Domain, los 3 Services de Infrastructure (metodos completos, no solo las lineas modificadas), los 3 Controllers Web y las 6 vistas tocadas.
- Reconteo independiente de esquema (`DESCRIBE` x3) y de datos (`NULL` x3 + `Proveedores`/`Productos`) contra `marihogar_dev` — 8/8 coinciden exacto con lo declarado.
- Grep exhaustivo de `NotaInterna` sobre todo el repo (10 archivos) + lectura linea por linea de los 4 metodos de generacion/servido de PDF de Ventas y de `ComprobanteAfipService.cs` — confirmado sin ninguna referencia.
- Ejecucion del playbook cross-proyecto acotado a los archivos tocados (14 items evaluados explicitamente, resto N/A por modulo/patron no aplicable).
- Verificacion cruzada de `4-presupuestador.md`/`trazabilidad.md` para confirmar que el gate de aprobacion del cliente para este sprint es real (no solo lo declarado por el implementador).

### Checklist de salida para merge

- [x] Build limpio (0 errores) en solucion principal y en el proyecto de consola, re-verificado por QA de forma independiente (con workaround documentado para un lock de archivo ajeno al codigo).
- [x] Migracion `AddOrdenCompraGastoVentaCamposCR10a12` generada, aplicada en `marihogar_dev` y verificada por query real (esquema + 100% NULL en lo ya cargado).
- [x] CR-10: condicional a Facturada, opcional, precarga en Edit, filtro+columna en Index — todo confirmado por lectura de codigo.
- [x] CR-11: filtro de texto amplia sobre el mismo campo sin duplicar, subcategoria visible en Index — confirmado.
- [x] CR-12: punto de seguridad critico (no filtracion a PDF) confirmado con evidencia propia de QA, no solo con lo declarado por el implementador.
- [x] Importador ajustado correctamente y confirmado sin re-ejecutar (conteos identicos a CR-D).
- [x] Produccion confirmada sin tocar.
- [x] Playbook cross-proyecto ejecutado, 0 regresiones reproducidas, 0 auto-fixes necesarios.
- [ ] Verificacion visual en navegador de los 3 puntos de UI (toggle condicional de OC, subcategoria en Gastos, colapsable de Venta) — pendiente del usuario, checklist de 10 pasos ya dejada por el implementador en `5-implementador.md`.
- [ ] Sincronizar la etiqueta de estado de `4-presupuestador.md` a "Aprobado" (fuera de las capas de QA, a cargo del orquestador).
- [ ] Las 5 migraciones acumuladas del Change Request siguen pendientes de aplicar contra produccion, coordinables junto con CR-6 (ambos en pausa por decision del cliente).

### Estado go/no-go

**GO para dar por cerrado tecnicamente el Sprint CR-E.** Sin defectos de ninguna severidad bloqueante encontrados. El punto de seguridad mas sensible del sprint (que `Venta.NotaInterna` nunca aparezca en un PDF generado, remito o factura AFIP) fue verificado por QA con lectura completa y propia del codigo de los 4 metodos relevantes mas un grep exhaustivo de todo el repo, sin ninguna discrepancia respecto de lo declarado por el implementador. Migracion aditiva pura confirmada segura por lectura directa y por reconteo real contra `marihogar_dev` (100% de las filas ya cargadas en `NULL`, sin alterar ningun dato existente). Confirmado que el importador no se re-ejecuto (conteos identicos a la corrida de CR-D) y que produccion no fue tocada en ningun momento. Dos observaciones documentales/de bajo riesgo (conteo "5 vs 4 campos" en la prosa del implementador, y el gap heredado de `StringLength` server-side en campos de texto libre parseados directo del form) no ameritan auto-fix ni bloquean el cierre — no son regresiones de este sprint. **Recomendacion: dar el Change Request #1 por completo desde el punto de vista de QA en su alcance ya implementado (CR-1 a CR-12), a la espera de que el cliente/orquestador coordinen (1) la ejecucion real de CR-6 contra produccion y (2) la aplicacion de las 5 migraciones acumuladas contra produccion, ambas ya en pausa por decision del cliente y sin relacion con la calidad del codigo entregado.**

---
## Sprint CR-C (Change Request #1, post-Etapa 1) — CR-4 descargar/enviar comprobante por WhatsApp (endpoint público, auditoría de seguridad independiente)

### Alcance validado

Sprint CR-C del Change Request #1: CR-4 (`Venta.TokenDescargaPublica`, remito de venta en PDF sin CAE/datos fiscales, card "Remito de venta" en `Ventas/Details.cshtml` con botones "Descargar remito"/"Enviar por WhatsApp", `ComprobanteController` nuevo — único `[AllowAnonymous]` del sistema fuera de `AccountController`). Sprint CR-A y CR-B (ambos GO) no se re-validaron, solo se tomaron como contexto. NO se validó CR-6 (importador/vaciado de producción, sprint siguiente CR-D). Este es el sprint de mayor sensibilidad de seguridad de todo el Change Request — tratado con el mismo nivel de escrutinio que la revisión de seguridad reforzada del Dashboard en Etapa 1 (Sprint 5): **QA no confió en la autoevaluación de seguridad del implementador y repitió cada verificación de forma independiente, leyendo el código fuente real, no la memoria del implementador.**

**Método**: lectura completa y propia (no delegada) de `ComprobanteController.cs`, `VentaService.cs` (métodos CR-4 completos), `VentasController.cs` (2 acciones nuevas), `Venta.cs`, `AppDbContext.cs` (config del índice único), la migración `AddTokenDescargaPublicaVenta` (Up/Down), `Ventas/Details.cshtml` (card + script completos), `Program.cs` (pipeline completo + registro de ruta + política de rate limiting), `_Layout.cshtml` (sidebar, meta antiforgery). Grep propio de `AllowAnonymous` sobre `MariHogar.Web/Controllers/`. `dotnet build MariHogar.slnx --no-incremental` y `dotnet ef migrations list` re-ejecutados de forma independiente. **Query real contra `marihogar_dev`** (`mysql.exe` de MySQL Server 8.0 local, credenciales de `appsettings.Development.json`) para verificar la columna/índice/estado de datos de la migración, sin confiar en lo declarado.

### Auditoría de seguridad independiente — conclusión explícita sobre los 8 puntos declarados por el implementador

QA repitió cada verificación por su cuenta, con evidencia de código propia (no una copia de lo que declaró el implementador):

1. **"Token no adivinable"** — **CONFIRMADO**. `Venta.cs` línea 39: `TokenDescargaPublica` es `Guid?`, columna independiente del `Id` autoincremental. `VentaService.cs` línea 409 (ahora desplazada por el auto-fix, ver abajo): única asignación del campo es `venta.TokenDescargaPublica = Guid.NewGuid()`. Grep propio de `TokenDescargaPublica\s*=` en `VentaService.cs` confirma que es el único punto de escritura del campo en todo el archivo — ningún otro código lo deriva del `Id`, de una fecha o de cualquier valor predecible.
2. **"Búsqueda exclusiva por token"** — **CONFIRMADO**. `VentaService.GenerarRemitoPdfPorTokenAsync` (línea ~425, leída completa): el único `Where`/`FirstOrDefaultAsync` es `x.TokenDescargaPublica == token` — comparación de igualdad exacta, sin `Contains`/`StartsWith`/`LIKE` en ningún punto del método ni de `ComprobanteController.Descargar`. `ComprobanteController.cs` (59 líneas, leído completo) no recibe ni reenvía ningún otro identificador — el `Guid token` de la URL es el único dato de entrada.
3. **"Único `AllowAnonymous` nuevo"** — **CONFIRMADO por grep propio**: `Grep pattern:"AllowAnonymous" path:MariHogar.Web/Controllers` devuelve exactamente 4 coincidencias — `AccountController.cs` líneas 25/36/80 (Login GET, Login POST, AccessDenied — ya existentes del template) y `ComprobanteController.cs` línea 38 (a nivel de clase, la única acción es `Descargar`). Sin discrepancia con lo declarado.
4. **"404 sin fuga de información"** — **CONFIRMADO**. `ComprobanteController.Descargar` tiene un único `return NotFound()` (línea 55), alcanzado tanto si `GenerarRemitoPdfPorTokenAsync` devuelve `null` por token inexistente como (tras el auto-fix, ver abajo) por una Venta en estado no habilitado. Adicionalmente confirmado por lectura de `AppDbContext.cs`: `Venta` hereda `SoftDestroyable` y el query filter global (`DeletedAt == null`) se aplica automáticamente a `_db.Ventas` sin `IgnoreQueryFilters()` en ningún punto del flujo CR-4 — una Venta soft-deleted tampoco matchea la query y cae en el mismo `NotFound()` genérico, sin distinguir "no existe" de "borrada" de "token mal formado" (que cae a `Guid.Empty` por el model binder, ver decisión #2 del implementador, también verificada: el controller no tiene `[ApiController]` ni restricción `:guid` en la ruta, por lo que un segmento no parseable no aborta la acción, solo produce `Guid.Empty`).
5. **"Rate limiting vigente"** — **CONFIRMADO por lectura directa de `Program.cs`** (no supuesto): línea 222-226, `MapControllerRoute("comprobantePublico", "Comprobante/Descargar/{token}", ...)` encadenado a `.RequireRateLimiting("general")`. La política `"general"` (línea 119-128) es `FixedWindowLimiter`, `PermitLimit=300`, `Window=1 min`, particionado por `context.Connection.RemoteIpAddress` — la misma política que protege `MapControllerRoute("default", ...)`. Sin ningún `.DisableRateLimiting()` en todo `Program.cs` (grep propio, 0 coincidencias).
6. **"Sin exposición de otros datos"** — **CONFIRMADO**. `GenerarRemitoPdfInterno` (línea 438-508, leído completo): solo vuelca `Venta.Id` (como texto "Venta N°..."), `Fecha`, `ClienteNombre`, `ClienteTelefono`, `Total` y los `VentaItem` (`Producto.Nombre`, `Cantidad`, `PrecioUnitario`, subtotal). `Producto.PrecioCompra` no aparece en ningún punto del método (confirmado por grep de `PrecioCompra` en `VentaService.cs`, sin coincidencias dentro de la sección CR-4). Ningún CAE ni dato fiscal — el documento es visualmente distinto del PDF de `ComprobanteAfipService`.
7. **"Nombre de archivo genérico"** — **CONFIRMADO**. `ComprobanteController.Descargar` línea 57: `File(bytes, "application/pdf", "Comprobante.pdf")` — sin el `Id` de la Venta, a diferencia de `VentasController.DescargarRemito` (línea 166: `$"Remito-Venta-{id:D6}.pdf"`, autenticado).
8. **"Comparación no en tiempo constante — riesgo residual documentado, no mitigado"** — **CONFIRMADO como riesgo real y aceptado**. La comparación la resuelve MySQL vía el índice único (`WHERE TokenDescargaPublica = ?`, verificado por `SHOW INDEX` real contra `marihogar_dev`, ver evidencia de build/migración abajo), no una comparación byte a byte en C#. QA coincide con la evaluación del implementador: con 128 bits de espacio de claves (`Guid.NewGuid()` es v4, ~122 bits de entropía real) y un límite de 300 req/min por IP, un ataque de timing contra un índice de base de datos no es un vector práctico. **No mitigado, correctamente documentado como riesgo residual de severidad baja, no bloqueante.**

**Conclusión de la auditoría independiente**: los 8 puntos declarados por el implementador se **CONFIRMAN** con evidencia de código propia de QA, sin discrepancias. Pipeline HTTP (`UseAuthentication → UseAuthorization → UseRateLimiter → UseSession`, líneas 210-213 de `Program.cs`) verificado exactamente contra el orden documentado en `23-web.instructions.md` (pasos 10-13) — coincide exacto, sin reordenamiento ni exclusión de middleware para la ruta pública.

### Hallazgo nuevo de QA (no declarado por el implementador) — MH-005, auto-fix aplicado

Durante la lectura línea por línea de los 3 métodos nuevos de `VentaService.cs` (`GenerarRemitoPdfAsync`, `ObtenerOCrearTokenDescargaPublicaAsync`, `GenerarRemitoPdfPorTokenAsync`), QA detectó que **ninguno de los 3 revalidaba `Venta.Estado`** — solo verificaban `venta == null`. La UI (`Ventas/Details.cshtml` línea 106/111) oculta la card completa "Remito de venta" para `EstadoReal == Cancelada` y muestra un mensaje (sin botones) para cualquier estado que no sea `Pagada`/`PagadaParcial`, pero ese gate vivía **únicamente en la capa de presentación**. Consecuencia reproducible por código: un link público ya compartido antes de cancelar una Venta seguía sirviendo el PDF del remito después de la cancelación (mismo problema, en menor medida alcanzable en la práctica, para el estado `Pendiente`, ya identificado como prácticamente inalcanzable desde Sprint 2). Esto viola el principio ya establecido explícitamente en el propio proyecto ("revalidación server-side obligatoria... nunca confiar solo en client-side", `2-disenador-funcional.md`) y es exactamente el tipo de gap que la tarea de auditoría pedía revisar en el punto 7 (matriz "Venta Pendiente sin pagos").

**No es un hueco de la regla de seguridad central de CR-4** (no cruza Ventas — sigue resolviendo exclusivamente por el token/Id de esa misma Venta) — es un gap de consistencia de estado, catalogado con severidad **minor**.

**Auto-fix aplicado** (catalogado primero en `docs/qa/regresiones-manuales.yml` como `MH-005`, según la regla de auto-fix obligatorio): agregado el guard `if (v.Estado != EstadoVenta.Pagada && v.Estado != EstadoVenta.PagadaParcial) return null;` en los 3 métodos de `VentaService.cs` — mismo criterio que ya usa la vista, retornando `null` de la misma forma que el caso "Venta no encontrada" ya manejado por ambos controllers (preserva el 404 genérico sin distinción, no debilita el punto 4 de la auditoría). Re-verificado con `dotnet build MariHogar.slnx --no-incremental` → **0 errores** (mismos 9 warnings preexistentes). No reproducido en navegador (regla de proceso vigente) — el fix se sostiene por lectura directa del guard nuevo, idéntico en forma a los guards de estado ya usados en el resto de `VentaService` (ej. `CancelarAsync`).

### Hallazgo funcional — deviación no resuelta de una CA explícita (CR-4, WhatsApp no envía la factura AFIP cuando existe)

**No auto-fixeado — se escala, no se adivina.** `2-disenador-funcional.md` (CR-4, "Confirmado por el cliente 2026-07-27") y `3-arquitecto-mvc.md` (sección "CR-4 — Endpoint público de descarga") especifican, en términos casi idénticos, que el botón "Descargar PDF"/"Enviar por WhatsApp" de `Ventas/Details` debe **elegir automáticamente** entre el remito (sin `ComprobanteAfip` emitido) **o la factura AFIP ya emitida** (si existe) — es decir, un único flujo que sirve uno u otro documento según `ComprobanteAfip.Estado == Emitido`.

Verificado por código que la implementación real **no hace esa elección**: `VentaService.GenerarRemitoPdfAsync`/`GenerarRemitoPdfPorTokenAsync` generan **siempre** el remito, sin ninguna consulta ni condición sobre `ComprobantesAfip` en todo el archivo (confirmado por grep de `ComprobanteAfip` dentro de la sección CR-4 de `VentaService.cs`, sin coincidencias). `Ventas/Details.cshtml` expone dos cards **independientes y no coordinadas**: "Remito de venta" (con "Enviar por WhatsApp", siempre remito) y "Comprobante AFIP" (con "Ver comprobante" → `ComprobantesAfip/Details.cshtml`, que solo tiene "Descargar PDF" autenticado, **sin ningún botón de WhatsApp**, confirmado por lectura de esa vista). Resultado: para una Venta que ya tiene una factura AFIP emitida, **no existe ningún camino de la UI que envíe esa factura por WhatsApp** — el único botón de WhatsApp del sistema envía siempre el remito no fiscal, incluso cuando el cliente pidió explícitamente lo contrario.

El comentario XML-doc de `VentaService.GenerarRemitoPdfInterno` afirma "es un documento independiente (confirmado con el cliente, ver `2-disenador-funcional.md` CR-4)" — **esta cita no es exacta**: el documento de diseño referenciado dice lo opuesto (elección automática entre uno u otro, no ambos independientes). No se encontró en `5-implementador.md`, `trazabilidad.md` ni en ningún otro documento de memoria una reconciliación explícita de este punto con el cliente/orquestador — parece una lectura incorrecta del diseño durante la implementación, no una decisión de producto documentada.

**Por qué no se aplica auto-fix**: resolverlo correctamente requiere una decisión de producto (¿el remito y la factura deben seguir siendo documentos independientes ambos accesibles — lo cual es defendible como mejora, remito=entrega vs factura=fiscal — o el botón de WhatsApp debe unificarse y elegir automáticamente como pide el texto ya escrito?) más, en cualquier caso, tocar lógica de negocio nueva (branching en el Service, posiblemente extender el token público para resolver también el PDF de `ComprobanteAfip`) — fuera de "auto-fix obligatorio" (que solo replica soluciones ya validadas, sin introducir lógica nueva). **Severidad: major** (deviación de una CA explícita y confirmada por escrito en 3 documentos, en el propio feature de este sprint) — **no bloqueante para habilitar CR-D** (módulo totalmente distinto, sin dependencia), pero debe resolverse con el cliente/orquestador antes de dar CR-4 por 100% cerrado ante el cliente.

### Cobertura de historias de usuario

| HU | Criterio (resumen) | Resultado | Evidencia |
|---|---|---|---|
| HU-7.5 | Botón WhatsApp oculto (no solo deshabilitado) sin teléfono; link con número correcto y mensaje en español | CUMPLE (con desvío mayor documentado, ver hallazgo arriba) | `Ventas/Details.cshtml` línea 116-121: botón dentro de `@if (!string.IsNullOrWhiteSpace(v.ClienteTelefono))` — ausencia real en el HTML server-side, no CSS. Mensaje "Hola! Te paso el comprobante de tu compra: `<link>`" verificado literal en el script. El link enviado es siempre el del remito, nunca el de la factura AFIP aunque exista — ver hallazgo funcional arriba |

### Matriz de formularios/casos "100% OK" (pedido explícito del punto 7)

| Caso | Resultado | Evidencia |
|---|---|---|
| Venta sin `ClienteTelefono`: botón WhatsApp ausente del HTML (no solo oculto por CSS) | PASS | `Ventas/Details.cshtml` línea 116: el botón está dentro de un bloque Razor `@if` server-side — si la condición es falsa, ese `<button>` nunca se emite en el HTML de respuesta (verificado leyendo la estructura Razor, no una clase CSS `d-none`) |
| Venta Pendiente sin pagos: la card de remito no rompe | PASS (tras auto-fix MH-005 el comportamiento es más estricto) | Antes del fix: `else` en línea 130-133 mostraba el texto explicativo sin botones (ya correcto en la UI). Tras el fix: si igual se fuerza `DescargarRemito`/`ObtenerLinkPublico` por URL directa sobre una Venta no Pagada/PagadaParcial, ahora devuelve 404 en vez de servir el documento — cierra la inconsistencia entre UI y servidor |
| Venta Cancelada: remito ya no descargable ni por link ya compartido | PASS (tras auto-fix MH-005) | Antes del fix este caso NO estaba cubierto server-side (solo la UI lo ocultaba) — ver MH-005 |
| Token con formato inválido / inexistente / de Venta soft-deleted | PASS | Mismo `NotFound()` genérico en los 3 casos, confirmado por lectura de `ComprobanteController`+`GenerarRemitoPdfPorTokenAsync`+query filter global de `SoftDestroyable` |
| Reutilización del token (pedir el link 2 veces sobre la misma Venta) | PASS | `ObtenerOCrearTokenDescargaPublicaAsync`: `if (venta.TokenDescargaPublica == null)` — solo asigna una vez, se reutiliza en cualquier llamada posterior |
| PDF público nunca incluye `PrecioCompra`/CAE/datos de otra Venta | PASS | Ver punto 6 de la auditoría de seguridad arriba |

### Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

Foco en los archivos tocados por este sprint (`ComprobanteController`, `VentaService` CR-4, `VentasController` CR-4, `Ventas/Details.cshtml`, `Program.cs`). El resto del catálogo ya fue ejecutado completo en sprints anteriores sobre el resto del sistema (sin cambios en esos módulos en este sprint).

| id | aplica | resultado | acción |
|---|---|---|---|
| REG-001 a REG-007, REG-009 | no | N/A — sin concurrency tokens nuevos, sin combos/autocomplete nuevos, sin maquina de estados nueva, sin campos condicionales por metodo de pago, sin combos en cascada en los archivos tocados este sprint | ninguna |
| REG-008 (perdida de foco) | no | N/A — el único JS nuevo (`btnEnviarWhatsApp`) es un handler de click puntual sobre un POST AJAX, no un input de texto que se re-renderiza en cada tecla | ninguna |
| REG-010 (sidebar vs autorización real — foco explícito del pedido) | si | PASS — grep propio de "Comprobante" en `_Layout.cshtml`: única coincidencia es el link ya existente a `ComprobantesAfip` (AFIP, Sprint 6, autenticado); **ningún link nuevo apunta a `ComprobanteController`/`/Comprobante/Descargar`** — el endpoint público no tiene ni debe tener entrada de sidebar (se accede solo por el link compartido por WhatsApp) | ninguna |
| KOI-001 a KOI-006 | no | N/A — sin botones `.btn-swal-confirm` nuevos, sin controllers referenciados desde el sidebar en este sprint | ninguna |
| DN-001/DN-002 | no | N/A — sin `Include` de colección + `OrderBy` dinámico + `Skip/Take` en los métodos nuevos (son consultas puntuales por token/Id, sin paginación) | ninguna |
| GAN-001 (guard "al menos un item real") | no | N/A — sin grillas dinámicas nuevas en este sprint | ninguna |
| GAN-002/003/004 | no | N/A — sin backfill de datos históricos, sin `<script type="text/x-template">`, sin `<datalist>` en este sprint | ninguna |
| VSF-001/VSF-002 | no | N/A — módulo Compras/OC no tocado este sprint | ninguna |
| CRM-001 a CRM-006 | no | N/A — sin toggles en memoria, sin altas masivas, sin notificaciones in-app nuevas en este sprint | ninguna |
| MH-001 (IN de colección local string) | si (grep sobre `VentaService.cs`/`VentasController.cs`) | PASS — sin `.Contains()` de colección local en los 3 métodos nuevos de CR-4 (son `FirstOrDefaultAsync` por clave única, no un `IN` sobre una lista) | ninguna |
| MH-002 (enum serializado como int) | no | N/A — sin DTOs con enums nuevos en este sprint (`TokenDescargaPublica` es `Guid?`) | ninguna |
| MH-003 (fecha futura de cheque) | no | N/A — módulo Cheques no tocado este sprint | ninguna |
| MH-004 (desglose facturado/no facturado) | no | N/A — módulo Caja no tocado este sprint | ninguna |
| MH-005 (nuevo, este ciclo) | si | **FAIL → auto-fix aplicado por QA** — ver hallazgo dedicado arriba | catalogado + parcheado + re-verificado |

### Defectos detectados

1. **MH-005 (minor)** — sin revalidación server-side de `Venta.Estado` en el flujo de remito/link público de CR-4 (ver detalle arriba). **Corregido en este ciclo.**
2. **Deviación funcional de CR-4 (major, no auto-fixeada, escalada)** — "Enviar por WhatsApp" nunca envía la factura AFIP ya emitida, contradiciendo la CA explícita de `2-disenador-funcional.md`/`3-arquitecto-mvc.md` de elección automática remito-vs-factura (ver detalle arriba). Requiere decisión del cliente/orquestador antes de dar CR-4 por 100% cerrado — no bloquea CR-D.

### Auto-fixes aplicados en este ciclo

1. **MH-005** — `MariHogar.Infrastructure/Services/VentaService.cs`: agregado el guard `Estado != Pagada && Estado != PagadaParcial → null` en `GenerarRemitoPdfAsync`, `ObtenerOCrearTokenDescargaPublicaAsync` y `GenerarRemitoPdfPorTokenAsync`. Catalogado en `docs/qa/regresiones-manuales.yml` (id `MH-005`) antes de aplicar el parche, con `fix_aplicado` completo. Re-verificado con `dotnet build MariHogar.slnx --no-incremental` → 0 errores (mismos 9 warnings preexistentes). Sin lógica de negocio nueva — replica el gate ya usado por `Ventas/Details.cshtml`.

### Evidencia de build y migración (re-verificado por QA de forma independiente)

- `dotnet build MariHogar.slnx --no-incremental` (antes y después del auto-fix MH-005) → **Compilación correcta, 0 errores** en ambos casos, 9 warnings preexistentes (NU1902 MailKit/MimeKit + CS0114 `HomeController.StatusCode`), ninguno nuevo.
- `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` → **10 migraciones, ninguna `(Pending)`**: coincide exactamente con lo declarado (`...AddImpuestosOCyChequeEmision`, `...AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2`, `...AddTokenDescargaPublicaVenta`).
- Query real contra `marihogar_dev` (`mysql.exe` de MySQL Server 8.0 local, ejecutado por QA de forma independiente): `DESCRIBE Ventas` confirma `TokenDescargaPublica char(36) YES UNI NULL`; `SHOW INDEX FROM Ventas WHERE Key_name='IX_Ventas_TokenDescargaPublica'` confirma `Non_unique=0` (único real, no solo declarado en la migración); `SELECT COUNT(*) AS total, SUM(TokenDescargaPublica IS NULL) AS nulos FROM Ventas` → **85/85**, coincide exacto con lo declarado por el implementador.
- Grep propio de `AllowAnonymous` sobre `MariHogar.Web/Controllers/` (4 coincidencias, ver auditoría punto 3) y de `Comprobante` sobre `_Layout.cshtml` (sin link nuevo, ver REG-010).

### Riesgos de liberación

- **Ninguno de severidad blocker/critical.** Un (1) defecto minor (MH-005) encontrado y corregido en el mismo ciclo. Un (1) hallazgo funcional major (WhatsApp no envía la factura AFIP cuando existe) no auto-fixeado, escalado para decisión del cliente/orquestador — no bloquea CR-D pero debe resolverse antes de cerrar CR-4 ante el cliente.
- **Bajo (aceptado, documentado)**: comparación de token no en tiempo constante — impráctica de explotar contra 128 bits de espacio de claves + rate limiting de 300 req/min por IP, confirmado por QA de forma independiente (punto 8 de la auditoría).
- **Bajo**: sin verificación en caliente por navegador (regla de proceso vigente) — el paso más sensible es el posible bloqueo de pop-up del navegador al abrir WhatsApp (`window.open` dentro de un callback asíncrono), riesgo de UX no de seguridad, ya documentado por el implementador con checklist de 8 pasos para el usuario.
- **Bajo**: migración `AddTokenDescargaPublicaVenta` (+ las 2 acumuladas de CR-A/CR-B) todavía no aplicada contra producción — las 3 confirmadas seguras por revisión de código y verificación de datos real, coordinables en una misma ventana de mantenimiento con backup previo.
- **Bajo**: sin expiración ni revocación del token una vez compartido — límite conocido, no pedido por el alcance, documentado por el implementador.

### Pruebas mínimas ejecutadas

- `dotnet build MariHogar.slnx --no-incremental` (antes y después del auto-fix) → 0 errores en ambos casos.
- `dotnet ef migrations list` → 10 migraciones, ninguna pendiente.
- Query real contra `marihogar_dev` (columna/índice/85 filas con token NULL), ejecutada por QA de forma independiente.
- Grep exhaustivo de `AllowAnonymous` sobre todo `MariHogar.Web/Controllers/` (4 controllers confirmados) y de `Comprobante` sobre `_Layout.cshtml` (sin link nuevo al endpoint público).
- Revisión de código completa (línea por línea) de `ComprobanteController.cs`, `VentaService.cs` (sección CR-4 completa), `VentasController.cs` (2 acciones nuevas), `Venta.cs`, `AppDbContext.cs` (config del índice), migración `AddTokenDescargaPublicaVenta` (Up/Down), `Ventas/Details.cshtml` (card + script completos), `ComprobantesAfip/Details.cshtml` (para el hallazgo funcional), `Program.cs` (pipeline completo).
- Ejecución del playbook cross-proyecto acotado a los archivos tocados (34 items totales incluido el nuevo MH-005).

### Checklist de salida para merge

- [x] Build limpio (0 errores) antes y después del auto-fix de QA.
- [x] Migración generada, aplicada en `marihogar_dev` y verificada por query real (columna/índice/datos).
- [x] Auditoría de seguridad independiente: los 8 puntos declarados por el implementador CONFIRMADOS con evidencia de código propia de QA (no una copia de lo declarado).
- [x] Playbook cross-proyecto ejecutado, 1 defecto nuevo encontrado y corregido (MH-005), catalogado con `fix_aplicado`.
- [x] Grep exhaustivo de `AllowAnonymous` (4/4, sin sorpresas) y de sidebar (sin link nuevo al endpoint público).
- [ ] Hallazgo funcional (WhatsApp no envía factura AFIP cuando existe) pendiente de decisión del cliente/orquestador — no bloqueante para CR-D, sí para cerrar CR-4 ante el cliente.
- [ ] Checklist manual de 8 pasos (dejada por el implementador) pendiente de ejecución en navegador por el usuario — no bloqueante, foco recomendado en el paso 4 (posible bloqueo de pop-up).
- [ ] Migraciones `AddImpuestosOCyChequeEmision` (CR-A), `AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2` (CR-B) y `AddTokenDescargaPublicaVenta` (CR-C) pendientes de aplicar contra producción — las 3 confirmadas seguras, listas para la misma ventana de mantenimiento.

### Estado go/no-go

**GO para habilitar Sprint CR-D** (CR-6: importador de histórico + vaciado de producción — sprint final y de mayor sensibilidad por tocar datos reales), **con un hallazgo funcional (no de seguridad) explícitamente sin resolver que no bloquea este gate pero sí debe resolverse antes de dar CR-4 por cerrado ante el cliente**: "Enviar por WhatsApp" nunca envía la factura AFIP ya emitida (siempre envía el remito), contradiciendo la CA explícita y confirmada por escrito en `2-disenador-funcional.md`/`3-arquitecto-mvc.md`. La auditoría de seguridad independiente pedida explícitamente por el alcance de este sprint **confirma, con evidencia de código propia de QA, los 8 puntos declarados por el implementador, sin ninguna discrepancia**: token `Guid.NewGuid()` no derivado del Id, búsqueda exclusivamente por igualdad exacta de token, único `AllowAnonymous` nuevo del sistema (4/4 confirmado por grep), 404 genérico sin distinción (incluida la Venta soft-deleted, no contemplada explícitamente por el implementador pero confirmada por QA vía el query filter global), rate limiting de 300 req/min por IP confirmado vigente sin exclusión, sin exposición de `PrecioCompra`/CAE/otras Ventas, nombre de archivo genérico, comparación no en tiempo constante aceptada como riesgo residual de baja severidad. Un (1) defecto nuevo encontrado por QA (no declarado por el implementador) y corregido en el mismo ciclo — MH-005 (minor): faltaba revalidación server-side del estado de la Venta en el flujo de remito/link público, permitiendo que una Venta Cancelada (o, en teoría, Pendiente) siguiera sirviendo su remito por un link ya compartido o por URL directa. **Ninguna duda de seguridad quedó sin resolver con certeza** — el único punto abierto es funcional/de producto (factura AFIP vs. remito por WhatsApp), no de seguridad, y se documenta separado del gate de seguridad de este sprint.

---
## Sprint CR-B (Change Request #1, post-Etapa 1) — CR-3 tarjeta de credito/Banco Carrefour + CR-5 categorias de gasto + CR-8 sugerir monto + CR-9 reportes facturado/no facturado

### Alcance validado

Sprint CR-B del Change Request #1: CR-3 (`MetodoPago` gana `TarjetaCredito=6`/`BancoCarrefour=7`, exclusivos de Ventas; `PagoVenta` gana `CantidadCuotas`/`PorcentajeInteres`), CR-5 (`CategoriaGasto` reordenado de Alquiler/Servicios/Sueldos/Flete/Otro a Sueldos/Impuestos/Luz/APR/Publicidad/Otro, con migracion de datos sobre los 29 `Gasto` ya existentes), CR-8 (Ventas y OC: agregar una fila de pago nueva precompleta el Monto con el saldo pendiente), CR-9 (Dashboard/Caja/Proyeccion financiera desglosan o informan Facturado vs. No facturado). Sprint CR-A (GO) no se re-valido, solo se tomo como contexto. NO se valido CR-4 (WhatsApp/remito) ni CR-6 (importador) — sprints siguientes.

**Metodo**: revision de codigo real de los archivos declarados tocados (`git status` contra el working tree: `MetodoPago.cs`, `CategoriaGasto.cs`, `PagoVenta.cs`, `VentaDtos.cs`, `CajaDtos.cs`, `DashboardDtos.cs`, `ProyeccionFinancieraDtos.cs`, `VentaService.cs`, `DashboardService.cs`, `CajaService.cs`, `ProyeccionFinancieraService.cs`, `PagoOrdenCompraService.cs`, `VentasController.cs`, Views `Ventas/{Create,Details,Index}.cshtml`, `OrdenesCompra/Details.cshtml`, `Dashboard/Admin.cshtml`, `Caja/Index.cshtml`, `ProyeccionFinanciera/Index.cshtml`, migracion `20260727180522_AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2.cs` Up/Down completos). `dotnet build MariHogar.slnx` y `dotnet ef migrations list` re-ejecutados de forma independiente. **2 verificaciones criticas pedidas explicitamente por el orquestador, ambas re-ejecutadas por QA de forma completamente independiente** (no confiando en lo declarado por el implementador): (1) recuento y volcado completo (no muestral) de los 29 `Gasto` de `marihogar_dev` via `mysql.exe` de MySQL Server 8.0 local, contrastado fila por fila contra la tabla de mapeo acordada con el cliente; (2) grep de `TarjetaCredito`/`BancoCarrefour`/`Carrefour` sobre todo el repo para confirmar que no aparecen en ningun archivo de Compras/OC.

### Verificacion critica 1 — Migracion de datos de CR-5 (re-verificacion COMPLETA, no muestral)

**Migracion `20260727180522_AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2.cs` leida completa (Up/Down)**: confirmado que el remapeo de `CategoriaGasto` es una **unica sentencia `UPDATE Gastos SET Categoria = CASE Categoria WHEN 1 THEN 6 WHEN 2 THEN 3 WHEN 3 THEN 1 WHEN 4 THEN 6 WHEN 5 THEN 6 ELSE Categoria END;`** — no una secuencia de `UPDATE` independientes por valor. Esto es correcto y evita el bug clasico de que un `UPDATE` posterior vuelva a matchear filas ya actualizadas por uno anterior: como el `CASE` evalua el valor `Categoria` **original** de cada fila una sola vez dentro de la misma sentencia (MySQL no re-lee el valor ya escrito de la misma fila durante la ejecucion del mismo `UPDATE`), no hay ventana de riesgo de doble-remapeo (ej. una fila `Alquiler(1)->Otro(6)` no puede ser tomada despues por error como si ya fuera `Sueldos(3)` porque nunca hubo un `UPDATE` intermedio que la dejara en un valor transitorio ambiguo).

**Re-verificacion COMPLETA (no muestral) contra `marihogar_dev`**: QA ejecuto por su cuenta `SELECT COUNT(*) FROM Gastos` (resultado: **29**, coincide exactamente con lo declarado) y luego `SELECT Id, Categoria, Monto, Descripcion, DeletedAt FROM Gastos ORDER BY Id` (las 29 filas completas, ninguna con `DeletedAt` no nulo, confirmando que no hay soft-deleted excluidos del conteo). Las 29 filas se contrastaron una por una contra la tabla de mapeo de `1-analista-funcional.md` CR-5 (Alquiler→Otro, Servicios→Luz, Sueldos→Sueldos, Flete→Otro, Otro→Otro) usando la `Descripcion` de cada fila como ancla semantica independiente (no solo el numero):

| Categoria nueva (post-migracion) | Cantidad | Descripcion tipica | Mapeo viejo inferido | Correcto |
|---|---|---|---|---|
| 6 (Otro) | 7 filas (Id 1,6,10,14,18,22,26) | "Alquiler del local - mes X" | Alquiler(1)→Otro(6) | Correcto |
| 1 (Sueldos) | 7 filas (Id 2,7,11,15,19,23,27) | "Sueldos del equipo - mes X" | Sueldos(3)→Sueldos(1) | Correcto |
| 3 (Luz) | 7 filas (Id 3,8,12,16,20,24,28) | "Luz, agua e internet del local" | Servicios(2)→Luz(3) | Correcto |
| 6 (Otro) | 5 filas (Id 4,9,13,21,25) | "Flete de entrega a domicilio" | Flete(4)→Otro(6) | Correcto |
| 6 (Otro) | 3 filas (Id 5,17,29) | "Insumos varios del local" | Otro(5)→Otro(6) | Correcto |

7+7+7+5+3 = **29/29 filas cubiertas, ninguna fuera de las 5 categorias del mapeo, ninguna con categoria fuera de rango (1-6)**. `Monto`/`Descripcion` no mostraron ningun patron de corrupcion (valores decimales y textos coherentes con lo esperado de un negocio real). Esta tabla coincide exactamente con la que declaro el implementador en `5-implementador.md`, pero fue reconstruida por QA de forma independiente a partir del volcado crudo, no copiada de lo declarado.

**Adicional**: `DESCRIBE PagosVenta` confirmo las columnas `CantidadCuotas` (int, nullable) y `PorcentajeInteres` (decimal(18,2), nullable) presentes con el tipo correcto; `SELECT COUNT(*), SUM(CASE WHEN CantidadCuotas IS NULL THEN 1 ELSE 0 END) FROM PagosVenta` devolvio **119/119**, confirmando que la migracion es puramente aditiva sobre `PagosVenta` (ningun `PagoVenta` historico alterado).

**Conclusion de la verificacion critica 1**: **PASS, migracion de datos de CR-5 verificada al 100% (29/29 filas, no una muestra) por QA de forma independiente, sin discrepancia alguna con lo declarado por el implementador.**

### Verificacion critica 2 — Tarjeta de credito / Banco Carrefour NO filtran hacia OrdenCompra

Grep de `TarjetaCredito|BancoCarrefour|Carrefour` (case-insensitive) sobre todo el repositorio: las unicas ocurrencias de codigo funcional estan en `MetodoPago.cs` (enum), `PagoVenta.cs` (doc-comment), `VentaDtos.cs`, `VentaService.cs` (`MetodosPermitidosVenta`), `VentasController.cs`/`Ventas/{Create,Index}.cshtml` y la migracion. **Cero ocurrencias en `PagoOrdenCompraService.cs`, `OrdenesCompra/*.cshtml`, `OrdenCompraDtos.cs` ni ningun otro archivo del flujo de Compras.**

Confirmado ademas por lectura directa: `PagoOrdenCompraService.MetodosPermitidosOC = [Efectivo, Transferencia, Cheque, Deposito]` (sin cambios, 4 valores, sin Tarjeta/Carrefour) y el objeto JS `METODOS` de `OrdenesCompra/Details.cshtml` = `{1: 'Efectivo', 2: 'Transferencia', 4: 'Cheque', 5: 'Deposito'}` (salta deliberadamente los valores 3/6/7, que corresponden a MercadoPago/TarjetaCredito/BancoCarrefour). Doble capa (cliente + servidor) consistente y excluyente.

**Hallazgo adicional, no un defecto**: `EntregaService.MetodosPermitidosCobro` (cobro en destino de Entregas, que reutiliza `PagoVenta` sobre la misma Venta) tiene su **propio** `HashSet` independiente = `[Efectivo, Transferencia, MercadoPago]`, definido desde Sprint 3 y **no ampliado** en este sprint con Tarjeta/Carrefour — mismo criterio en `Entregas/Details.cshtml` (`METODOS` JS con solo 3 valores). El diseño de CR-3 (`2-disenador-funcional.md` Diseño v2) solo declara como pantalla afectada "seccion Formas de pago de `Ventas/Create`" — Entregas no esta en el alcance declarado de CR-3, por lo que esto **no es una regresion ni un defecto**, es una limitacion de alcance ya consistente (cliente y servidor coinciden) que se documenta para que el cliente decida si quiere ampliarla en un sprint futuro (cobrar en destino con tarjeta/Carrefour hoy no es posible, solo Efectivo/Transferencia/MercadoPago).

**Conclusion de la verificacion critica 2**: **PASS. Tarjeta de credito y Banco Carrefour son exclusivos de Ventas/Create, confirmado por grep exhaustivo + lectura de ambas listas de metodos permitidos (cliente y servidor) de OrdenCompra. Sin excepciones encontradas.**

### Cobertura de historias de usuario

| HU | Criterio (resumen) | Resultado | Evidencia |
|---|---|---|---|
| HU-5.10 | Pago con tarjeta de credito exige cuotas (3/6/9/12); % interes opcional | CUMPLE | `VentaService.ConfirmarAsync`: `CuotasValidasTarjeta=[3,6,9,12]`, rechaza sin cuotas validas si `Metodo=TarjetaCredito`; rechaza si otro metodo trae cuotas/interes informados; `PorcentajeInteres` sin `[Range]`, acepta null/0 |
| HU-5.11 | Banco Carrefour disponible en Ventas; NO en OC | CUMPLE | Ver verificacion critica 2 |
| HU-18.3 | Combo Categoria de Gasto cerrado con las 6 opciones nuevas, sin las viejas | CUMPLE | `Gastos/Create.cshtml`/`Index.cshtml` iteran `Enum.GetValues<CategoriaGasto>()` (patron ya existente desde Sprint 5) — reordenar el enum fue suficiente, sin tocar las Views |
| HU-5.12 | Agregar fila de pago en Venta precompleta Monto con saldo pendiente (Total - filas previas) | CUMPLE | `saldoPendienteVenta()` = `totalVenta() - totalPagos()`, nunca negativo (null si cubierto), editable despues — verificado que NO es simplemente `Total` fijo |
| HU-12.7 | Idem en OC, con saldo pendiente de la OC | CUMPLE | `saldoPendienteOCRestante()` = `saldoPendiente - totalPagos()`, mismo criterio |
| HU-9.3 | Dashboard desglosa Facturado/No facturado, suma exacta al total | CUMPLE | `DashboardService.ObtenerVentasPeriodoAsync` particiona la MISMA lista `ventasPeriodo` ya usada para el total — Facturado+NoFacturado==Total por construccion, no por dos queries independientes |
| HU-15.3 | Caja mensual con mismo desglose | **CUMPLE tras auto-fix** (ver defecto MH-004 abajo) | Version previa al fix podia romper la suma si habia un Gasto anulado en el periodo — corregido en este ciclo |
| HU-17.3 | Proyeccion financiera informa % historico facturado, sin alterar formula | CUMPLE (con observacion menor) | `porcentajeIngresosFacturados` no participa de `PromedioIngresosMensual`/`IngresosProyectados` (verificado); ver observacion sobre el denominador abajo |

**Cobertura**: 8/8 HU CUMPLE (1 de ellas, HU-15.3, requirio auto-fix para cumplir realmente el criterio).

### Defectos detectados

**MH-004 (severidad minor)** — `CajaService.ObtenerDesgloseFacturadoAsync` (CR-9) asumia que el unico origen de movimientos `Ingreso` en `MovimientoCCLocal` es `VentaService` con `OrigenTipo="Venta"` (decision #6 de `5-implementador.md`, basada en un grep que no contemplo un caso real). **`GastoService.AnularAsync` tambien escribe un movimiento `Tipo=Ingreso`/`OrigenTipo="Gasto"`** (contramovimiento de reversion al anular un Gasto ya cargado — logicamente correcto como reversion de un Egreso, pero con `Tipo=Ingreso`). Como `CajaService.ObtenerTotalesAsync` (que calcula "Ingresos del periodo") suma TODOS los movimientos `Ingreso` sin filtrar por `OrigenTipo`, mientras que el desglose (version previa al fix) solo consideraba `OrigenTipo="Venta"`, un Gasto anulado dentro del periodo consultado hubiera dejado `IngresosFacturados + IngresosNoFacturados < IngresosPeriodo`, violando CA-CR9.2 ("la suma de ambos segmentos coincide siempre con el total ya mostrado"). **No reproducido con datos reales** (confirmado por QA: `SELECT Id FROM Gastos WHERE Anulado=1` sobre `marihogar_dev` devuelve 0 filas — el bug es latente, no manifestado todavia en dev), pero si reproducible con certeza por lectura de codigo (identidad algebraica rota por construccion). `DashboardService` (misma card conceptual) NO tiene este problema porque calcula el desglose particionando la misma lista de Ventas ya sumada para el total, no con una segunda query de distinto alcance.

### Auto-fixes aplicados en este ciclo

1. **MH-004** — `MariHogar.Infrastructure/Services/CajaService.cs`, metodo `ObtenerDesgloseFacturadoAsync`: reescrito para traer TODOS los movimientos `Ingreso` del periodo (no solo `OrigenTipo="Venta"`), calcular `facturados` igual que antes (subset Venta con `ComprobanteAfip.Estado=Emitido`) y `noFacturados = totalIngresos - facturados` — garantiza por construccion que `facturados+noFacturados == IngresosPeriodo` sin importar que otros `OrigenTipo` existan hoy o se agreguen en el futuro. Catalogado en `docs/qa/regresiones-manuales.yml` (id `MH-004`) antes de aplicar el parche, con `fix_aplicado` completo. Re-verificado con `dotnet build MariHogar.slnx --no-incremental` → **0 errores** (mismos 9 warnings preexistentes, ninguno nuevo). No reproducido en navegador ni con datos reales (regla de proceso QA + ausencia de Gastos anulados en `marihogar_dev` hoy); el fix se sostiene por identidad algebraica (resta contra el total real), no por el caso de dato ejecutado.

**Observacion NO corregida (no bloqueante, documentada)**: `ProyeccionFinancieraService.ObtenerAsync` calcula `porcentajeIngresosFacturados` como `montoFacturado(solo Venta) / ingresosHistoricos(todos los Ingreso, incluye reversiones de Gasto)`. Si hubiera Gastos anulados en la ventana historica, el porcentaje informado seria levemente menor al real "% de ingresos de Venta que estan facturados" (el denominador queda inflado por ingresos no-Venta). CA-CR9.3 solo exige que el dato sea informativo y no altere la formula de proyeccion (ambas cosas se cumplen) — no exige una identidad de suma exacta como CA-CR9.1/CA-CR9.2, por lo que no se trata como defecto ni se aplica auto-fix; se dejan documentado por si el cliente pide mayor precision en un sprint futuro.

### Matriz de formularios "100% OK" — CR-3 (pedido explicito)

| Caso | Resultado | Evidencia |
|---|---|---|
| Tarjeta de credito sin elegir cuotas | Rechaza | `VentaService.ConfirmarAsync`: `!CantidadCuotas.HasValue \|\| !CuotasValidasTarjeta.Contains(...)` → error "elija la cantidad de cuotas (3, 6, 9 o 12)"; client-side el combo `.inp-tarjeta-cuotas` solo ofrece esos 4 valores |
| Cuotas con valor fuera de 3/6/9/12 (ej. 5, via POST directo) | Rechaza | Mismo guard server-side (`CuotasValidasTarjeta` es una whitelist cerrada, no un rango) — inalcanzable desde la UI real (combo cerrado), pero bloqueado igual ante un POST manipulado |
| % interes vacio/0 | Acepta sin error | `PorcentajeInteres` es `decimal?` sin `[Range]`; el guard server-side solo exige cuotas, nunca interes — consistente con CA-CR3.1 ("el interes puede ser nulo") |
| Metodo != TarjetaCredito con cuotas/interes informados (payload manipulado) | Rechaza | Guard explicito: "Cuotas e interes solo aplican al pago con tarjeta de credito" |
| Forma de pago no permitida en Venta (Cheque/Deposito, via POST directo) | Rechaza | `MetodosPermitidosVenta.Contains` sigue excluyendolos, sin cambios |
| Forma de pago Tarjeta/Carrefour en OC (via POST directo) | Rechaza | `MetodosPermitidosOC` no las incluye (ver verificacion critica 2) |

Recalculo sin perder foco (REG-008) verificado tambien para los campos nuevos: `.inp-monto-pago` y `.inp-tarjeta-interes` usan el evento `input` sin llamar a `renderPagos()` (no reconstruyen el DOM en cada tecla), solo actualizan el array en memoria — mismo patron ya validado en Sprint 2.

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

Foco en los items relevantes a los archivos tocados por este sprint (Ventas/OC-pagos/Gastos/Dashboard/Caja/Proyeccion). El resto del catalogo ya fue ejecutado completo en sprints anteriores sobre el resto del sistema (sin cambios en esos modulos en este sprint).

| id | aplica | resultado | accion |
|---|---|---|---|
| REG-001 a REG-005, REG-007, REG-009, REG-010 | no | N/A — sin cambios de esquema con concurrency tokens, sin combos nuevos, sin maquina de estados nueva, sin modulo Devoluciones, sin combos en cascada ni sidebar tocado este sprint | ninguna |
| REG-006 (campos condicionales por metodo de pago) | si (foco explicito) | PASS — Cuotas/% Interes se despliegan/validan condicionalmente a `Metodo=TarjetaCredito` tanto client-side (JS toggle) como server-side (guard explicito), doble capa | ninguna |
| REG-008 (perdida de foco en inputs) | si (foco explicito, campos nuevos de CR-3/CR-8) | PASS — `.inp-monto-pago`/`.inp-tarjeta-interes` no re-renderizan en cada tecla; `btnAgregarPago`/`btnAgregarPagoOC` disparan `renderPagos()` solo en el click de "Agregar" (no en cada tecla) | ninguna |
| KOI-001 a KOI-006, DN-001/DN-002, GAN-002/GAN-003/GAN-004, VSF-001/VSF-002, CRM-001 a CRM-006 | no | N/A — patrones/modulos no aplicables a los archivos tocados en este sprint | ninguna |
| GAN-001 (guard "al menos un pago real") | si (re-chequeo) | PASS — `VentaService.ConfirmarAsync` sigue usando `input.Pagos.Where(p => p.Monto > 0)`, no `Count==0` ingenuo; sin cambios de este sprint en el guard | ninguna |
| MH-001 (IN de coleccion local string) | si (grep sobre los 5 Services tocados) | PASS — todos los `.Contains()` encontrados en `VentaService`/`DashboardService`/`CajaService`/`ProyeccionFinancieraService`/`PagoOrdenCompraService` son sobre `List<int>` (VentaId) o `HashSet<enum>` en memoria, ningun `HashSet<string>` contra coleccion local | ninguna |
| MH-002 (enum serializado como int) | no (no aplica a DTOs nuevos) | N/A — `CantidadCuotas`/`PorcentajeInteres` son `int?`/`decimal?`, no enums; el filtro `VentaFiltro.Metodo` en `Ventas/Index.cshtml` bindea por nombre de enum (`value="TarjetaCredito"`), no por int crudo | ninguna |
| MH-003 (fecha futura de cheque, re-chequeo) | si | PASS — sin cambios en `PagoOrdenCompraService` de este sprint fuera del guard ya corregido en Sprint CR-A, sigue presente | ninguna |
| MH-004 (nuevo, este ciclo) | si | **FAIL → auto-fix aplicado** — ver seccion de defectos arriba | catalogado + parcheado + re-verificado |

### Evidencia de build y migracion (re-verificado por QA de forma independiente)

- `dotnet build MariHogar.slnx --no-incremental` (antes y despues del auto-fix MH-004) → **Compilacion correcta, 0 errores** en ambos casos, 9 warnings preexistentes (NU1902 MailKit/MimeKit + CS0114 `HomeController.StatusCode`), ninguno nuevo.
- `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` → **9 migraciones, ninguna `(Pending)`**: `InitialCreate`, `AddCatalogo`, `AddPresupuestosVentas`, `AddEntregas`, `AddComprasCCProveedoresCheques`, `AddGastos`, `AddComprobantesAfip`, `AddImpuestosOCyChequeEmision`, `AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2` — coincide exactamente con lo declarado.
- Query real contra `marihogar_dev` (`mysql.exe` de MySQL Server 8.0 local): `SELECT COUNT(*) FROM Gastos` (29) + `SELECT Id, Categoria, Monto, Descripcion, DeletedAt FROM Gastos ORDER BY Id` (29 filas completas, revisadas una por una, ver verificacion critica 1).
- Query real: `SELECT COUNT(*), SUM(CASE WHEN CantidadCuotas IS NULL THEN 1 ELSE 0 END) FROM PagosVenta` (119/119) + `DESCRIBE PagosVenta` (columnas nuevas presentes con tipo correcto).
- Query real: `SELECT Id FROM Gastos WHERE Anulado=1` (0 filas — confirma que MH-004 es latente, no manifestado hoy en dev).
- Grep de `TarjetaCredito|BancoCarrefour|Carrefour` sobre todo el repo (verificacion critica 2) y de `.Contains(` sobre los 5 Services tocados (MH-001).

### Riesgos de liberacion

- **Ninguno de severidad blocker/critical/major.** Un (1) defecto minor (MH-004) encontrado y corregido en el mismo ciclo, sin logica de negocio nueva (resta algebraica contra un total ya calculado).
- **Bajo**: sin verificacion en caliente por navegador de los flujos JS nuevos (sub-formulario de tarjeta, precompletado de monto, badges de desglose facturado/no facturado) — regla de proceso vigente. Checklist de 10 pasos ya dejada por el implementador en `5-implementador.md` para que el usuario la recorra.
- **Bajo**: migracion `AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2` todavia no aplicada contra produccion (decision correcta, coordinada por el orquestador) — confirmada segura por revision de codigo + verificacion de datos real completa (no muestral).
- **Medio (a decision del cliente, no bloqueante)**: `EntregaService.MetodosPermitidosCobro` no ofrece Tarjeta de credito/Banco Carrefour para el cobro en destino de Entregas (fuera del alcance declarado de CR-3) — documentado como limitacion consciente, no defecto.
- **Bajo**: observacion sobre `ProyeccionFinancieraService` (denominador del % informativo puede incluir ingresos no-Venta) — sin impacto en ninguna formula de negocio, no bloqueante.

### Pruebas minimas ejecutadas

- `dotnet build MariHogar.slnx --no-incremental` (antes y despues del auto-fix) → 0 errores en ambos casos.
- `dotnet ef migrations list` → 9 migraciones, ninguna pendiente.
- Re-verificacion COMPLETA (29/29, no muestral) de la migracion de datos de `Gasto` contra `marihogar_dev`, por query real ejecutada por QA.
- Grep exhaustivo de `TarjetaCredito`/`BancoCarrefour`/`Carrefour` sobre todo el repo para confirmar exclusividad de Ventas.
- Revision de codigo completa de los 5 Services tocados, 1 Controller, 7 Views con JS, migracion Up/Down, entidades Domain, DTOs.
- Grep de patrones riesgosos (`.Contains(` sobre coleccion local, enums sin `.ToString()`, `btn-swal-confirm` sin `data-form`) sobre los archivos nuevos/modificados de este sprint.
- Ejecucion del playbook cross-proyecto acotado a los modulos tocados (34 items totales incluido el nuevo MH-004).

### Checklist de salida para merge

- [x] Build limpio (0 errores) antes y despues del auto-fix de QA.
- [x] Migracion generada, aplicada en `marihogar_dev` y verificada por query real completa (no muestral).
- [x] Las 8 HU del sprint CUMPLEN (1 de ellas via auto-fix de QA).
- [x] Verificacion critica 1 (migracion de categorias de gasto, 29/29 completa) confirmada PASS de forma independiente.
- [x] Verificacion critica 2 (Tarjeta/Carrefour exclusivos de Ventas, sin filtrar a OC) confirmada PASS por grep exhaustivo + lectura de ambas listas de metodos permitidos.
- [x] Playbook cross-proyecto ejecutado, 1 defecto nuevo encontrado y corregido (MH-004), catalogado con `fix_aplicado`.
- [ ] Checklist manual de 10 pasos (dejada por el implementador) pendiente de ejecucion en navegador por el usuario — no bloqueante.
- [ ] Migraciones `AddImpuestosOCyChequeEmision` (Sprint CR-A) y `AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2` (Sprint CR-B) pendientes de aplicar contra produccion — ambas confirmadas seguras por QA, listas para aplicarse juntas en la misma ventana de mantenimiento (ver seccion siguiente).

### Migraciones acumuladas del Change Request — listas para producción juntas

Las 2 migraciones del Change Request #1 generadas hasta ahora (`AddImpuestosOCyChequeEmision` de Sprint CR-A y `AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2` de Sprint CR-B) fueron verificadas de forma independiente por QA en sus respectivos ciclos (ver seccion Sprint CR-A arriba) y **ambas son seguras para aplicarse juntas contra produccion en la misma ventana de mantenimiento**, con backup previo obligatorio (mismo criterio ya exigido por el proyecto para cualquier cambio de esquema en produccion):
- `AddImpuestosOCyChequeEmision`: solo agrega columnas nuevas con default seguro (false/0/null) + 2 `UPDATE` deterministas no destructivos (`Subtotal=Total`, `FechaEmision` recalculada hacia atras) — verificado sin discrepancias contra los datos reales de `marihogar_dev` en su momento.
- `AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2`: solo agrega 2 columnas nuevas nullable a `PagosVenta` (sin tocar ningun dato existente, confirmado 119/119) + 1 `UPDATE...CASE` sobre `Gastos` (verificado 29/29 correcto en este ciclo, no muestral). Ninguna de las 2 migraciones hace `DROP`/`ALTER` destructivo de columnas existentes.
- Ambas ya estan aplicadas y confirmadas sin pendientes en `marihogar_dev` (`dotnet ef migrations list`, 9 migraciones totales) — el orden de aplicacion en produccion debe respetar el mismo orden cronologico (`AddImpuestosOCyChequeEmision` antes que `AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2`), que es el orden natural que `dotnet ef database update` aplicara solo.
- **Nota importante para producción**: como CR-5 remapea los valores de `CategoriaGasto` de los `Gasto` ya cargados, si en produccion existen `Gasto` con `Categoria` fuera de las 5 mapeadas explicitamente por el `CASE` (1-5), esos registros no cambiarian de valor (rama `ELSE Categoria`) — dado que el enum viejo solo tenia 5 valores (1-5) y la columna es un `int` sin `CHECK` constraint, esto no deberia ocurrir en la practica salvo un dato corrupto preexistente; se recomienda al Administrador correr `SELECT DISTINCT Categoria FROM Gastos` en produccion antes de aplicar, como chequeo preventivo de 10 segundos.

### Estado go/no-go

**GO para habilitar Sprint CR-C** (CR-4: WhatsApp + remito + endpoint publico). Sin defectos bloqueantes, criticos ni major. Un (1) defecto minor (MH-004) encontrado y corregido en el mismo ciclo, con parche minimo (identidad algebraica, sin logica de negocio nueva). Las 2 verificaciones criticas pedidas explicitamente por el orquestador — migracion completa (no muestral) de categorias de gasto y exclusividad de Tarjeta/Carrefour para Ventas — fueron reconfirmadas por QA de forma completamente independiente, con dato real de la base en el primer caso y grep exhaustivo del repo en el segundo. Las 2 migraciones acumuladas del Change Request (`AddImpuestosOCyChequeEmision` + `AddMetodoPagoTarjetaCarrefourYCategoriaGastoV2`) estan confirmadas listas para aplicarse juntas contra produccion, con backup previo y el chequeo preventivo de datos senalado arriba.

---
## Sprint CR-A (Change Request #1, post-Etapa 1) — CR-1 impuestos en OC + CR-2 fecha de emision de cheque + CR-7 acreditacion manual

### Alcance validado

Sprint CR-A del Change Request #1 (feedback de la primera demo post-Etapa 1): CR-1 (`OrdenCompra` gana `Facturada`/`TipoComprobante` A-B-C + bloque de impuestos IVA/IIBB/Otros discriminados, `Total = Subtotal + MontoIva + MontoIIBB + MontoOtrosImpuestos`), CR-2 (`Cheque` gana `FechaEmision`, autocalculo sugerido de `FechaVencimiento` a 30/60/90 dias, editable) y CR-7 (`ChequeAcreditacionHostedService` deja de acreditar automaticamente: solo notifica una vez por cheque vencido y marca `Notificado=true`; la acreditacion queda exclusivamente manual via el boton ya existente desde Sprint 4). Etapa 1 completa (16 modulos, 6 sprints, GO en el gate final) no se re-valido, solo se tomo como contexto. Nota de proceso: la sesion del implementador se corto por limite de sesion antes de escribir su propia memoria de cierre; QA no confio en lo declarado por el orquestador en su nombre y volvio a verificar el codigo real, el build, las migraciones y los datos en `marihogar_dev` de forma independiente (pedido explicito del orquestador para este ciclo).

**Metodo**: lectura completa de `OrdenCompra.cs`/`Cheque.cs` (Domain), `OrdenCompraService.cs`/`ChequeService.cs`/`PagoOrdenCompraService.cs`/`ChequeAcreditacionHostedService.cs` (Infrastructure), `ChequesController.cs`/`OrdenesCompraController.cs` (Web), `OrdenCompraViewModels.cs`, `OrdenCompraDtos.cs`/`ChequeDtos.cs`/`PagoOrdenCompraDtos.cs`, Views `OrdenesCompra/{Create,Details}.cshtml` (JS completo) y `Cheques/Index.cshtml`, migracion `20260727162418_AddImpuestosOCyChequeEmision.cs` (Up/Down completos). `dotnet build MariHogar.slnx` y `dotnet ef migrations list` re-ejecutados de forma independiente. **Query real ejecutada por QA contra `marihogar_dev`** (MySQL 8.0.29 local, cliente `mysql.exe` de MySQL Server 8.0) sobre `OrdenesCompra` y `Cheques` completas, no solo confiando en lo declarado por el implementador. `git diff --stat` revisado para acotar el QA exactamente a los 23 archivos tocados por este sprint (mas 2 archivos nuevos: `TipoComprobanteCompra.cs` y la migracion).

### Cobertura de historias de usuario

| HU | Criterio (resumen) | Resultado | Evidencia |
|---|---|---|---|
| HU-12.5 | Facturada/No facturada; Tipo A/B/C obligatorio solo si Facturada; 3 pares %/Monto editables; Total=Subtotal+impuestos | CUMPLE | `OrdenCompraService.ValidarComprobante` rechaza sin `TipoComprobante` cuando `Facturada=true` (server, ademas de `[Required]` implicito por flujo); `AplicarComprobanteEImpuestos` fuerza 0/null cuando `Facturada=false` (defensivo); `Total = Subtotal + MontoIva + MontoIIBB + MontoOtrosImpuestos` calculado identico en `OrdenesCompra/Create.cshtml` (JS `recalcularTotales()`) y en el Service — verificado formula por formula |
| HU-12.6 | OC ya cerradas mantienen su saldo pendiente sin alteracion tras la migracion | CUMPLE | Migracion `UPDATE OrdenesCompra SET Subtotal = Total;` sin tocar `Total`; impuestos quedan en su `defaultValue` 0/false/null via las columnas nuevas — **verificado por query real** (ver seccion dedicada abajo): las 15 OC historicas tienen `Subtotal == Total` exacto, `Facturada=0`, `PorcentajeIva=0` |
| HU-14.5 | Fecha de emision requerida; Vencimiento se sugiere (Emision+Cuota) pero editable | CUMPLE | `PagoOrdenCompraService.RegistrarPagoAsync` rechaza sin `FechaEmisionCheque` (server) + `Swal`/validacion inline en `OrdenesCompra/Details.cshtml` (client); JS `autocalcularVencimientoCheque()` = `moment(fechaEmision).add(cuota,'days')`, campo `.inp-cheque-vencimiento` queda editable manualmente despues del autocalculo |
| HU-14.6 | El cheque NO cambia de estado al vencer; notificacion unica por cheque; Acreditar sigue siendo accion manual en cualquier momento | CUMPLE | Ver "Verificacion puntual critica de CR-7" abajo — confirmado linea por linea que `ChequeAcreditacionHostedService`/`ObtenerYMarcarVencidosNoNotificadosAsync` nunca tocan `Estado`, y **confirmado ademas con dato real**: el Cheque Id=7 en `marihogar_dev` esta `Notificado=1` y `Estado=1 (Pendiente)` simultaneamente, evidencia de que el job corrio en este entorno y se comporto exactamente como CR-7 exige |

**Cobertura**: 4/4 HU CUMPLE por revision de codigo, con verificacion adicional por dato real (no solo codigo estatico) en HU-12.6 y HU-14.6.

### Verificacion puntual critica 1 — Calculo de impuestos de CR-1 (cliente y servidor)

Confirmado que **ambos lados calculan exactamente la misma formula**, patron `FacturaVenta` de ganaderia-emo:
- **Servidor** (`OrdenCompraService.AplicarComprobanteEImpuestos`): `oc.Total = oc.Subtotal + oc.MontoIva + oc.MontoIIBB + oc.MontoOtrosImpuestos;` — sin logica de "base de calculo" propia porque los 3 montos llegan ya resueltos desde el Input (el Service no recalcula IVA/IIBB, solo persiste lo que llega si `Facturada=true`, o fuerza 0 si `Facturada=false`).
- **Cliente** (`OrdenesCompra/Create.cshtml`, funcion `baseImpuesto(grupo)`): `grupo === 'iva' ? subtotal : (subtotal + montoIva)` — IVA sobre Subtotal, IIBB y Otros sobre Subtotal+IVA, exactamente el criterio pedido (identico a `FacturaVenta` de ganaderia). `recalcularTotales()` calcula `total = subtotal + montoIva + montoIibb + montoOtros`, misma formula que el servidor.
- **Validacion server-side de rango**: `[Range(0,100)]` en `PorcentajeIva`/`PorcentajeIIBB`/`PorcentajeOtrosImpuestos` (ViewModel, enforced via `ModelState.IsValid` en `OrdenesCompraController.Create/Edit` antes de invocar el Service) + `ValidarComprobante` rechaza explicitamente montos/porcentajes negativos — doble capa, nunca confia solo en el cliente.
- **Verificado con dato real** (OC Id=16 en `marihogar_dev`, unica OC facturada existente): Subtotal=75000.00, PorcentajeIva=21.00 → MontoIva esperado 15750.00; Total=93472.50 → 93472.50-75000-15750=2722.50, que coincide con 3% de IIBB sobre (75000+15750)=90750 (90750*0.03=2722.50). La aritmetica real persistida en la base es consistente con la formula documentada.

**Resultado: PASS.** Sin discrepancia entre cliente y servidor, sin bug reproducido.

### Verificacion puntual critica 2 — Integridad de la migracion de datos (re-verificada por QA con query real)

QA **no confio en lo declarado por el implementador/orquestador** y ejecuto las queries pedidas directamente contra `marihogar_dev` (MySQL 8.0.29 local, `mysql.exe` de MySQL Server 8.0, sin intermediarios):

`SELECT Id, Subtotal, Total, Facturada, PorcentajeIva, TipoComprobante, Estado FROM OrdenesCompra ORDER BY Id;` → 16 filas. Las 15 OC con Id 1 a 15 (historicas, previas a este sprint) tienen **`Subtotal == Total` exacto en las 15 filas**, `Facturada=0`, `PorcentajeIva=0.00`, `TipoComprobante=NULL` — ninguna OC ya cerrada cambio de `Total` tras la migracion, cumpliendo HU-12.6 al 100%. La OC Id=16 es una OC nueva cargada ya con el formulario de CR-1 (Facturada=1, PorcentajeIva=21.00, TipoComprobante=1/A, Total=93472.50 ≠ Subtotal=75000.00) — consistente con una carga de prueba posterior al deploy del sprint, no con dato migrado.

`SELECT Id, FechaEmision, FechaVencimiento, Cuota, Notificado, Estado FROM Cheques ORDER BY Id;` → 8 filas. Verificado manualmente, cheque por cheque, que `FechaEmision == FechaVencimiento - Cuota dias` para los 7 cheques que tienen ese patron (Ids 1 a 7 — Cuota tomada por su valor numerico real, 30/60/90, que coincide con `CuotaCheque` como enum de dias, no de posicion): Id1 (venc.18/08, cuota30 → emision 19/07 ✓), Id2 (venc.12/09, cuota60 → emision 14/07 ✓), Id3 (venc.02/10, cuota90 → emision 04/07 ✓), Id4 (venc.15/08, cuota30 → emision 16/07 ✓), Id5 (venc.15/05, cuota30 → emision 15/04 ✓, Estado=Acreditado historico sin tocar), Id6 (venc.05/05, cuota30 → emision 05/04 ✓, Estado=Rechazado historico sin tocar), Id7 (venc.27/07=hoy, cuota60 → emision 28/05 ✓). El cheque Id=8 (FechaEmision=27/07=hoy, sin backfill, Estado=Pendiente) es un alta nueva via el formulario de CR-2, coherente con un cheque cargado despues del deploy, no un dato migrado.

**Resultado: PASS.** La migracion `UPDATE Cheques SET FechaEmision = DATE_SUB(FechaVencimiento, INTERVAL Cuota DAY);` se aplico correctamente sobre los 7 cheques historicos, y ningun `Total`/saldo de OC historica se alteró. QA confirma de forma independiente lo que el implementador/orquestador ya habian declarado, sin encontrar discrepancias.

### Verificacion puntual critica 3 — CR-7, notificacion sin acreditacion

Lectura completa de `ChequeAcreditacionHostedService.cs` (139 lineas) y `ChequeService.cs` (173 lineas):
- `ChequeAcreditacionHostedService.EjecutarSiCorrespondeAsync` llama exclusivamente a `chequeService.ObtenerYMarcarVencidosNoNotificadosAsync(...)` y, si hay resultados, a `NotificarAdministradoresAsync(...)` (que solo llama a `INotificationService.CreateAsync`, sin tocar `_db`). **En ningun punto del archivo se asigna `Estado = EstadoCheque.Acreditado` ni se llama a `AcreditarAsync`.**
- `ChequeService.ObtenerYMarcarVencidosNoNotificadosAsync` filtra `Estado == EstadoCheque.Pendiente && FechaVencimiento <= fecha && !Notificado`, marca `Notificado = true` en el mismo `SaveChangesAsync`, y **no modifica `Estado` en ningun punto del metodo** — un cheque ya notificado nunca vuelve a matchear el filtro, garantizando que el job corrido dos veces el mismo dia (o concurrentemente) no reenvia la misma notificacion.
- `ChequeService.AcreditarAsync` (el metodo que SI cambia `Estado`) exige `Estado == Pendiente`, sigue siendo invocado exclusivamente desde `ChequesController.Acreditar` (accion POST con `[ValidateAntiForgeryToken]`, sin cambios de logica de negocio respecto de Sprint 4) — confirmado que el boton "Acreditar" en `Cheques/Index.cshtml` sigue funcionando: se muestra solo cuando `row.estado === 'Pendiente'`, dispara SweetAlert2 de confirmacion y hace POST a `Cheques/Acreditar`.
- **Confirmado con dato real** (no solo codigo): el Cheque Id=7 de `marihogar_dev` vencio hoy (27/07), tiene `Notificado=1` y **sigue `Estado=1 (Pendiente)`** — evidencia directa de que el job ya corrio en este entorno de desarrollo y se comporto exactamente como CR-7 exige (notifico sin acreditar).

**Resultado: PASS.** Sin desvio entre lo documentado y el codigo real.

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

Foco en los items relevantes a los archivos tocados por este sprint (OrdenesCompra/Cheques). El resto del catalogo ya fue ejecutado completo en Sprints 1 a 6 sobre el resto del sistema (sin cambios en esos modulos en este sprint).

| id | aplica | resultado | accion |
|---|---|---|---|
| REG-001 | no | N/A — sin `RowVersion`/concurrency tokens en `OrdenCompra`/`Cheque` | ninguna |
| REG-002 | no | N/A — no es el mismo patron (stock inicial de variante); ya cubierto en Sprint 1 para Producto/Stock | ninguna |
| REG-003 | si (buscador de productos en `OrdenesCompra/Create`) | PASS — `#selBuscador` contra `Productos/BuscarParaCompra` (confirmado que el endpoint existe), `templateResult` mapea campos reales (`nombre`,`marcaNombre`,`precioCompra`,`stockActual`,`fotoUrl`), sin campos inexistentes | ninguna |
| REG-004 | si (botones de accion de OC segun estado) | PASS — `OrdenesCompra/Details.cshtml` gatea Editar/Confirmar/Recibir/Cancelar con `@if (o.EstadoReal == ...)` exacto, sin botones hardcodeados fuera de estado | ninguna |
| REG-005 | no | N/A — modulo Ventas no tocado este sprint | ninguna |
| REG-006 | si (foco explicito del pedido: Tipo de comprobante condicional a Facturada, 3 campos de impuesto condicionales, campos de cheque condicionales a Metodo=Cheque) | PASS — los 3 casos piden y validan sus campos condicionales tanto client-side (JS toggle/disabled + Swal de "datos de cheque incompletos") como server-side (`ValidarComprobante`, `foreach` de campos de cheque en `PagoOrdenCompraService`), doble capa en los 3 casos | ninguna |
| REG-007 | no | N/A — modulo Devoluciones no existe | ninguna |
| REG-008 | si (inputs de cantidad/precio/impuestos/monto de pago en OC) | PASS — ningun handler de `input` re-renderiza la tabla/lista completa; cada uno actualiza solo la celda o el campo hermano afectado, foco nunca se pierde | ninguna |
| REG-009 | no | N/A — sin combos en cascada en OC/Cheque | ninguna |
| REG-010 | no | N/A — sidebar/policy de Cheques sin cambios este sprint (ya PASS en Sprint 4) | ninguna |
| KOI-001 | si (botones `btn-swal-confirm` de OC) | PASS — usan `data-form` apuntando a un `<form>` real (`formConfirmar`/`formRecibir`), patron ya corregido, no reproduce el bug original | ninguna |
| KOI-002/003/004 | no | N/A — modulos Estado de Resultados/Cierre no existen | ninguna |
| KOI-005/006 | no | N/A — sidebar no tocado funcionalmente este sprint (solo cambio de branding "MariHogar"→"Marí Hogar", fuera de alcance de este QA) | ninguna |
| DN-001/DN-002 | no | N/A — stack EF Core 10 + MySql.EntityFrameworkCore, no EF6; `ChequeService.ListarAsync`/`OrdenCompraService.ListarAsync` usan `Include` solo sobre navegaciones simples (no colecciones) | ninguna |
| GAN-001 | si (guard "al menos un pago real" en `PagoOrdenCompraService`) | PASS — `input.Pagos.Where(p => p.Monto > 0)` filtra sobre la lista real, no `Count==0` ingenuo; codigo cita explicitamente GAN-001 en su propio comentario | ninguna |
| GAN-002 | no | N/A — no es backfill de campo faltante en pago historico, es backfill de fecha por resta simple, sin ambiguedad de negocio | ninguna |
| GAN-003 | no | N/A — sin `<script type="text/x-template">` con `<partial>` en las Views tocadas (grep sin resultados) | ninguna |
| GAN-004 | no | N/A — sin `<datalist>` en las Views tocadas | ninguna |
| VSF-001 | no | N/A — sin patron de vinculo remanente a compra cancelada en este dominio | ninguna |
| VSF-002 | si (transicion Borrador→Cancelada de OC) | PASS — `EstadosCancelables = [Borrador, Confirmada]` incluye Borrador desde el origen (Sprint 4), sin regresion este sprint | ninguna |
| CRM-001 a CRM-006 | no | N/A — modulo Bot/CRM no existe en marihogar | ninguna |
| MH-001 | si (grep de `.Contains()` sobre coleccion local en los Services tocados) | PASS — los unicos `.Contains()` encontrados son sobre `HashSet<EstadoOrdenCompra>`/`HashSet<MetodoPago>` en memoria (comparacion C#, nunca traducidos a SQL), sin el patron riesgoso | ninguna |
| MH-002 | si (serializacion de enums en DTOs nuevos/modificados) | PASS — `ChequeListItemDto.Estado`/`OrdenCompraListItemDto.Estado`/`OrdenCompraDetailDto.TipoComprobante` mapean con `.ToString()` explicito, ninguno serializa el int crudo | ninguna |
| MH-003 (nuevo, cross-proyecto) | si | **FAIL → auto-fix aplicado** — ver seccion de defectos abajo | catalogado + parcheado + re-verificado |

### Defectos detectados

**MH-003 (severidad minor)** — `PagoOrdenCompraService.RegistrarPagoAsync` no revalidaba server-side que `FechaEmisionCheque` no fuera una fecha futura, pese a que el date picker del cliente ya restringe `max="hoy"` (`OrdenesCompra/Details.cshtml`, `.inp-cheque-emision`). Un POST directo a `/OrdenesCompra/RegistrarPago/{id}` con `fechaEmisionCheque` futura se hubiera persistido sin error, dejando un `Cheque.FechaEmision` incoherente con un documento fisico real (no se puede emitir un cheque que todavia no existe). Viola el principio ya explicito del proyecto ("revalidacion server-side obligatoria, nunca confiar solo en cliente", `2-disenador-funcional.md`). Responde directamente al punto 6 del pedido ("Cheque con fecha de emision posterior a la fecha de pago de la OC — ¿hay validacion?"): no la habia, ahora si.

### Auto-fixes aplicados en este ciclo

1. **MH-003** — `MariHogar.Infrastructure/Services/PagoOrdenCompraService.cs`: agregado guard `linea.FechaEmisionCheque.Value.Date > DateTime.Today → error "La fecha de emision del cheque no puede ser futura."`, simetrico a los 2 guards de fecha ya existentes (vencimiento no anterior a hoy; emision no posterior a vencimiento). Catalogado en `docs/qa/regresiones-manuales.yml` (id `MH-003`) antes de aplicar el parche, con `fix_aplicado` completo. Re-verificado con `dotnet build MariHogar.slnx` → **0 errores** (4 warnings preexistentes NU1902, ninguno nuevo). No re-ejecutado en navegador (regla de proceso QA, sin smoke test de UI); el patron del guard nuevo es identico en forma a los 2 guards preexistentes ya validados por el mismo metodo.
2. **Correccion de comentario XML-doc obsoleto** (sin cambio de comportamiento) — `MariHogar.Domain/Enums/EstadoCheque.cs`: el doc-comment de la maquina de estados todavia decia "Pendiente → Acreditado (automatico, job diario ChequeAcreditacionHostedService)", texto que quedo desactualizado tras CR-7 (el resto del codigo, incluido `Cheque.cs`, ya documentaba correctamente el cambio a manual). Corregido para reflejar el comportamiento real ya implementado y verificado. No es un auto-fix funcional (no cambia logica), se documenta igual por transparencia de lo tocado en este ciclo de QA.

### Matriz de formularios "100% OK" (pedido explicito del punto 6)

| Caso | Resultado | Evidencia |
|---|---|---|
| OC Facturada sin elegir Tipo | Rechaza | `ValidarComprobante`: `Facturada && TipoComprobante is null` → error "Seleccione el tipo de comprobante..." |
| OC con impuestos, porcentaje negativo | Rechaza | `ValidarComprobante` (server, explicito) + `[Range(0,100)]`/`[Range(0,double.MaxValue)]` en el ViewModel (enforced via `ModelState.IsValid`) — doble capa |
| OC con impuestos, porcentaje > 100% | Rechaza | `[Range(0,100)]` en `PorcentajeIva`/`PorcentajeIIBB`/`PorcentajeOtrosImpuestos`, enforced server-side antes de invocar el Service (`ModelState.IsValid` verificado en Create/Edit) |
| Cheque sin fecha de emision | Rechaza | `PagoOrdenCompraService`: `!linea.FechaEmisionCheque.HasValue` incluido en el guard de campos obligatorios de Cheque (server) + Swal client-side "Datos de cheque incompletos" |
| Cheque con fecha de emision posterior a la de vencimiento | Rechaza | `FechaEmisionCheque > FechaVencimientoCheque` → error explicito (ya existia antes de este ciclo) |
| Cheque con fecha de emision futura (posterior a "hoy", momento del pago) | Rechaza (post auto-fix MH-003) | Antes de este ciclo, solo el cliente lo restringia (`max=hoy` en el date picker); ahora tambien el servidor |
| Pago de OC sin ningun metodo con monto real | Rechaza | Guard GAN-001-safe: `input.Pagos.Where(p => p.Monto > 0)` → `Count==0` → error "Cargue al menos una forma de pago." |
| Pago que supera el saldo pendiente de la OC | Rechaza | `sumaNueva > saldoDisponible` → error con montos exactos en el mensaje |

### Evidencia de build y migracion (re-verificado por QA de forma independiente)

- `dotnet build MariHogar.slnx` → **Compilacion correcta, 0 errores**, 8 warnings preexistentes (`NU1902` MailKit/MimeKit x2 c/u), ninguno nuevo — re-ejecutado por QA antes de cualquier cambio propio.
- `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` → **8 migraciones, ninguna `(Pending)`**: `InitialCreate`, `AddCatalogo`, `AddPresupuestosVentas`, `AddEntregas`, `AddComprasCCProveedoresCheques`, `AddGastos`, `AddComprobantesAfip`, `AddImpuestosOCyChequeEmision` — coincide exactamente con lo declarado por el implementador/orquestador.
- Tras aplicar los 2 ajustes propios de QA (guard MH-003 + doc-comment): `dotnet build MariHogar.slnx --no-restore` → **0 errores**, sin warnings nuevos — re-verificado.
- **La migracion `AddImpuestosOCyChequeEmision` esta lista para aplicarse en produccion**: `Up()` solo agrega columnas nuevas con `defaultValue` seguro (false/0/null) y corre 2 `UPDATE` deterministas y no destructivos (`Subtotal = Total` y `FechaEmision = DATE_SUB(FechaVencimiento, INTERVAL Cuota DAY)`), sin `DROP`/`ALTER` de columnas existentes ni perdida de datos. Verificado su efecto real contra `marihogar_dev` sin discrepancias (ver verificacion puntual critica 2). QA no la aplica contra produccion (fuera de su alcance), pero **confirma que es segura para aplicar**.

### Riesgos de liberacion

- **Bajo**: sin verificacion en caliente por navegador de los flujos JS (autocalculo de vencimiento de cheque, toggle de impuestos, Select2 de proveedor/producto) — regla de proceso vigente desde Sprint 2 (ni implementador ni QA ejecutan navegador). Checklist de 5 pasos ya dejada por el implementador en `5-implementador.md` para que el usuario la recorra.
- **Bajo**: la migracion todavia no fue aplicada contra produccion (decision correcta, coordinada por el orquestador despues de este QA) — el riesgo tecnico de aplicarla es bajo (ver evidencia de build y migracion arriba), pero **debe hacerse backup antes**, mismo criterio que el resto del proyecto exige para cambios de esquema en produccion.
- **Bajo**: cambios de branding cosmetico ("MariHogar"→"Marí Hogar" en `_Layout.cshtml`, `Home/Index.cshtml`, `ErrorNotifier.cs`, `SystemController.cs`) mezclados en el mismo diff que CR-A — no funcional, no bloqueante, pero fuera del alcance declarado del sprint; se documenta para que no sorprenda en una revision futura.
- Sin riesgos de severidad blocker/critical/major detectados en este sprint.

### Pruebas minimas ejecutadas

- `dotnet build MariHogar.slnx` (antes y despues del auto-fix) → 0 errores en ambos casos.
- `dotnet ef migrations list` → 8 migraciones, ninguna pendiente.
- Query real contra `marihogar_dev`: `SELECT Id, Subtotal, Total, Facturada, PorcentajeIva, TipoComprobante, Estado FROM OrdenesCompra ORDER BY Id;` (16 filas revisadas una por una).
- Query real contra `marihogar_dev`: `SELECT Id, FechaEmision, FechaVencimiento, Cuota, Notificado, Estado FROM Cheques ORDER BY Id;` (8 filas revisadas una por una, aritmetica de dias verificada a mano para cada una).
- Revision de codigo completa (no parcial) de los 4 Services tocados, 2 Controllers, 3 Views con JS, migracion Up/Down, entidades Domain, DTOs, ViewModels.
- Grep de patrones riesgosos (`.Contains(` sobre coleccion local, `text/x-template`, `<datalist>`, `btn-swal-confirm` sin `data-form`) sobre los archivos nuevos/modificados de este sprint.
- Ejecucion completa del playbook cross-proyecto (33 items, incluido el nuevo MH-003) con foco en los modulos tocados.

### Checklist de salida para merge

- [x] Build limpio (0 errores) antes y despues del auto-fix de QA.
- [x] Migracion generada, aplicada en `marihogar_dev` y verificada por query real (no solo declarada).
- [x] Las 4 HU del sprint CUMPLEN.
- [x] Los 3 puntos de verificacion puntual critica (impuestos, integridad de migracion, notificacion sin acreditacion) confirmados PASS con evidencia de codigo + dato real.
- [x] Playbook cross-proyecto ejecutado, 1 defecto nuevo encontrado y corregido (MH-003), catalogado con `fix_aplicado`.
- [ ] Checklist manual de 5 pasos (dejada por el implementador) pendiente de ejecucion en navegador por el usuario — no bloqueante.
- [ ] Migracion `AddImpuestosOCyChequeEmision` pendiente de aplicar contra produccion (con backup previo) — coordinado por el orquestador, confirmada segura por QA.

### Estado go/no-go

**GO para habilitar Sprint CR-B** (CR-3 tarjeta de credito/Banco Carrefour + CR-5 categorias de gasto + CR-8 sugerir monto + CR-9 reportes facturado/no facturado). Sin defectos bloqueantes, criticos ni major. Un (1) defecto minor encontrado (MH-003) y corregido en el mismo ciclo, con parche minimo y simetrico a un guard ya existente (sin logica de negocio nueva). Los 3 puntos de verificacion puntual pedidos explicitamente por el orquestador (calculo de impuestos, integridad de la migracion de datos, logica de notificacion sin acreditacion de CR-7) fueron reconfirmados por QA de forma independiente — con query real contra la base, no solo por lectura de codigo ni por confiar en lo declarado por el implementador/orquestador. La migracion `AddImpuestosOCyChequeEmision` esta tecnicamente lista para producción (con backup previo, fuera del alcance de este QA aplicarla).

---
## Sprint 6 — M7 Facturacion electronica AFIP/ARCA (ULTIMO sprint de Etapa 1 — gate final)

### Alcance validado

Sprint 6 (de 6, ultimo sprint funcional planificado de Etapa 1): M7 Facturacion electronica AFIP/ARCA — entidades `ComprobanteAfip`/`ComprobanteAfipItem`, `AfipTokenCache` (Singleton), `AfipService` (WSAA+WSFEv1, SOAP armado a mano), `ComprobanteAfipService.EmitirAsync`/`ReintentarAsync`/`GenerarPdfAsync`, guard real `VentaService.TieneComprobanteAsociadoAsync`, `ComprobantesAfipController`, listado con filtros persistidos en sesion, card "Comprobante AFIP" en `Ventas/Details.cshtml`, boton "Facturar" habilitado en la pantalla de exito de `Ventas/Create.cshtml`, configuracion `Afip` en `appsettings.json`. Sprints 1-5 (M10/M2/M3, M4/M5/M11, M6, M12/M13/M14, M18/M15/M16/M17/M9 — todos en GO/GO condicionado) **no se re-validaron**, solo se tomaron como contexto/base. **Este es el gate final de Etapa 1**: con este sprint validado, los 16 modulos de Etapa 1 quedan cerrados, habilitando el paso a Documentacion de alcance para el cliente (etapa 7 del flujo del estudio).

**Metodo**: revision de codigo real completa de `ComprobanteAfipService.cs` (los 6 metodos, linea por linea, incluido `EmitirAsync`/`ReintentarAsync`/`IntentarEmitirYPersistirAsync` completos), `AfipService.cs` (completo, incluidos armado/parseo SOAP, login WSAA, firma CMS), `AfipTokenCache.cs` (completo), `ComprobantesAfipController.cs` (completo), `VentaService.cs` (`TieneComprobanteAsociadoAsync`/`CancelarAsync`/`ListarAsync`), entidades `ComprobanteAfip.cs`/`ComprobanteAfipItem.cs`, enums `TipoComprobanteAfip`/`EstadoComprobanteAfip`, `AfipSettings.cs`, `AfipDtos.cs`/`ComprobanteAfipDtos.cs`, `IAfipService.cs`/`IComprobanteAfipService.cs`, `DependencyInjection.cs` (registro de `AfipTokenCache`/`AfipService`/`ComprobanteAfipService`/`HttpClient` nombrado `"Afip"`), Views `ComprobantesAfip/{Create,Details,Index}.cshtml` (scripts completos), fragmentos modificados de `Ventas/{Create,Details}.cshtml`, `_Layout.cshtml` (sidebar), `appsettings.json`/`appsettings.Development.json`/`appsettings.Production.json` (los 3, buscando datos reales hardcodeados). `dotnet build MariHogar.slnx` y `dotnet ef migrations list` **re-ejecutados por QA contra el repo real** (no solo tomados de lo declarado por el implementador, dado el contexto del corte de sesion por limite de cuenta) — ver seccion dedicada de evidencia. No se ejecuto navegador (regla del rol) ni se llamo a AFIP real (sin certificado `.p12`, imposible en este entorno).

### Cobertura de historias de usuario (HU-7.1 a HU-7.4)

| HU | Criterio (resumen) | Resultado | Evidencia |
|---|---|---|---|
| HU-7.1 | Seleccion de items+cantidad a facturar (checkbox+cantidad editable, tope=pendiente); facturacion parcial acumulativa en mas de un comprobante | CUMPLE | `ComprobantesAfip/Create.cshtml`: checkbox por item + `input[type=number] max=CantidadPendiente`, JS recorta client-side; `ComprobanteAfipService.EmitirAsync` revalida server-side `itemInput.Cantidad > pendiente` (pendiente = `ventaItem.Cantidad - ventaItem.CantidadFacturada`, siempre contra el valor actual en base) antes de abrir la transaccion. Facturacion parcial acumulativa confirmada: cada `ComprobanteAfip` es independiente, `CantidadFacturada` se acumula por `VentaItem` a traves de comprobantes sucesivos |
| HU-7.2 | Tipo de comprobante (A/B) obligatorio antes de emitir; CUIT/DNI requeridos segun tipo | CUMPLE | `Create.cshtml`: radio Factura A/B (B por defecto), validacion JS (A exige CUIT 11 digitos; B exige CUIT o DNI) + revalidacion server-side idempotente en `ComprobanteAfipService.ValidarDatosFiscales` (misma regla, nunca confia solo en cliente) |
| HU-7.3 | Si AFIP no responde/rechaza, comprobante queda en "Error" con detalle visible, sin bloquear el resto del sistema; reintentable desde la misma pantalla | CUMPLE | `AfipService.EmitirAsync` nunca deja escapar una excepcion (unico `try/catch` envolviendo todo el metodo, incluido el login WSAA y el parseo de respuesta) — siempre devuelve `AfipEmisionResultDto{Exito=false, DetalleError=...}` ante timeout/rechazo/error de red; `ComprobanteAfipService.IntentarEmitirYPersistirAsync` mapea `Exito=false` a `Estado=Error`+`DetalleError`, sin tocar `CantidadFacturada`; `Details.cshtml` muestra el error + boton "Reintentar"; `ReintentarAsync` reusa los `ComprobanteAfipItem` ya persistidos sin pedir items de nuevo |
| HU-7.4 | Token WSAA renovado automaticamente y de forma transparente antes de facturar si vencio | CUMPLE | `AfipTokenCache.ObtenerAsync` usa la `expirationTime` real informada por AFIP (parseada con `DateTimeOffset.Parse`, offset `-03:00` correcto) con margen de 10 min, nunca un TTL fijo de 24hs; renovacion transparente dentro de `AfipService.EmitirAsync` (`_tokenCache.ObtenerAsync(LoginWsaaAsync)`), sin intervencion del usuario |

**Cobertura: 4/4 HU CUMPLE por revision de codigo.** Sin observaciones que ameriten desvio documentado (a diferencia de Sprint 2).

### Verificaciones puntuales pedidas explicitamente (6 puntos)

**1. Transaccion de emision — `ComprobanteAfipService.EmitirAsync`/`IntentarEmitirYPersistirAsync`** (confirmado leyendo `MariHogar.Infrastructure/Services/ComprobanteAfipService.cs` lineas 366-408):
- `ventaItem.CantidadFacturada += item.Cantidad` esta en la linea 397, **estrictamente dentro** del bloque `if (resultado.Exito)` (linea 381-399) — no hay ninguna asignacion a `CantidadFacturada` fuera de ese `if`, ni antes de llamar a `_afipService.EmitirAsync` (linea 379), ni en la rama `else` (linea 400-405, comentario explicito en el codigo: *"CantidadFacturada NUNCA se toca en esta rama"*).
- Rama de rechazo (`else`, `Exito=false`): `comprobante.Estado = Error` + `comprobante.DetalleError = resultado.DetalleError`, confirmado que ningun `VentaItem` se modifica en este camino.
- Secuencia completa verificada: `BeginTransactionAsync` -> `Add(comprobante+items, Pendiente)` -> `SaveChangesAsync` (asigna Ids) -> `IAfipService.EmitirAsync` (HTTP real, fuera de cualquier lock de DB) -> si exito: `Estado=Emitido`+CAE+**recien ahi** incrementa `CantidadFacturada` — si no: `Estado=Error`, sin tocar `VentaItem` -> `SaveChangesAsync` final -> `CommitAsync`, con `RollbackAsync` en el `catch` que envuelve todo el bloque. **PASS — confirmado exactamente como fue declarado por el implementador.**

**2. `ReintentarAsync` revalida el tope contra el valor actual, no cacheado** (confirmado, lineas 234-279): antes de reintentar, hace un `foreach (var item in comprobante.Items)` que recalcula `pendiente = ventaItem.Cantidad - ventaItem.CantidadFacturada` **contra el estado actual leido de la base en esa misma llamada** (`venta = await _db.Ventas.Include(v => v.Items)...`), no contra ningun valor guardado en el primer intento fallido; si `item.Cantidad > pendiente` rechaza con un mensaje explicito que menciona "Otra emision debe haber consumido esa cantidad mientras tanto". **PASS.**

**3. `AfipTokenCache`: `expirationTime` real de AFIP (no TTL fijo) + `SemaphoreSlim` anti-doble-login** (confirmado, `AfipTokenCache.cs` completo, 64 lineas):
- `EsValido()` compara `DateTime.UtcNow < _expiracionUtc - MargenSeguridad` (margen de 10 min) contra `_expiracionUtc`, que se setea exclusivamente desde el `expirationTime` parseado de la respuesta real de WSAA (`AfipService.LoginWsaaAsync`, `DateTimeOffset.Parse(expirationTimeStr).UtcDateTime`) — nunca un `DateTime.UtcNow.AddHours(24)` ni ninguna constante fija.
- Doble-checked locking correcto: `if (EsValido()) return (...)` antes del `_lock.WaitAsync()` (evita tomar el lock si ya es valido, camino rapido) -> dentro del `try` tras adquirir el lock, **re-chequeo** `if (EsValido()) return (...)` (linea 36) antes de llamar a `loginFactory()` — cubre exactamente el caso de que 2 requests concurrentes con el token vencido lleguen simultaneamente: el primero adquiere el lock y hace login, el segundo espera en `WaitAsync()`, y al obtener el lock encuentra que el primero ya renovo el token (2do chequeo) y lo reutiliza sin loguear de nuevo. `finally { _lock.Release() }` garantiza liberacion incluso si `loginFactory()` lanza. **Sin condicion de carrera obvia. PASS.**

**4. Config `Afip` — homologacion como default seguro, sin datos reales hardcodeados, produccion=solo config**:
- `appsettings.json`: `"Ambiente": "Homologacion"`, `CertificadoPath`/`CertificadoPassword`/`CUIT` vacios (con comentario JSONC explicito de que es dependencia pendiente del cliente). **PASS.**
- `appsettings.Development.json`: sin seccion `Afip` (hereda el default de homologacion de `appsettings.json`) — confirmado leyendo el archivo completo, ningun dato de AFIP. **PASS.**
- `appsettings.Production.json`: sin seccion `Afip` en absoluto (hereda igual el default de homologacion hasta que se cargue explicitamente) — confirmado leyendo el archivo completo; contiene credenciales de SMTP/email preexistentes (no relacionadas a AFIP, ya presentes desde el template base), ningun dato de AFIP real. **PASS — sin fuga de datos de produccion.**
- `AfipSettings.EsProduccion` compara `Ambiente` contra `"Produccion"` case-insensitive; cualquier valor no reconocido (vacio, mal escrito, o cualquier otra cosa) cae a Homologacion (`WsaaUrl`/`WsfeUrl` usan el operador ternario `EsProduccion ? ...Produccion : ...Homologacion`, con Homologacion como rama `false`, nunca al reves). **Default seguro confirmado.**
- Grep de `if.*ambiente|Ambiente ==|EsProduccion|Homologacion|Produccion` sobre `AfipService.cs`/`ComprobanteAfipService.cs`/`ComprobantesAfipController.cs`: **la unica ocurrencia es un string de mensaje de error** ("verificar certificado/URL de ambiente"), sin ningun `if` de ambiente hardcodeado fuera de `AfipSettings.EsProduccion`/`WsaaUrl`/`WsfeUrl`. Pasar a produccion es efectivamente solo `Ambiente=Produccion`+3 datos reales, cero cambios de codigo. **PASS.**

**5. Guard real `VentaService.TieneComprobanteAsociadoAsync`** (confirmado, `VentaService.cs` linea 346-347): `_db.ComprobantesAfip.AnyAsync(c => c.VentaId == ventaId && c.Estado == EstadoComprobanteAfip.Emitido)` — filtra explicitamente por `Estado == Emitido`, no cualquier estado. Un comprobante en `Error` (nunca llego a existir para AFIP, sin CAE) **no** bloquea la cancelacion — confirmado que la condicion es un AND con `Estado`, no solo `VentaId`. `CancelarAsync` usa `TieneEntregaAsociadaAsync(id) || TieneComprobanteAsociadoAsync(id)` (linea 310) antes de abrir la transaccion. Una Venta sin comprobante (`AnyAsync` devuelve `false` sobre una coleccion vacia) tampoco bloquea. **PASS en los 3 casos: bloquea con Emitido, no bloquea sin comprobante, no bloquea con Error.**

**6. Tope de facturacion parcial acumulativa entre multiples comprobantes**: el invariante `Σ Cantidad (de todos los ComprobanteAfipItem de todos los comprobantes de un VentaItem) <= VentaItem.Cantidad` se sostiene porque `CantidadFacturada` es el unico contador acumulado (incrementado exclusivamente en `IntentarEmitirYPersistirAsync`, solo en la rama de exito, nunca decrementado ni reseteado en ningun punto del codigo — grep de `CantidadFacturada` en toda la solucion confirma que la unica escritura es esa linea 397) y cada nueva emision valida `itemInput.Cantidad > pendiente` donde `pendiente = Cantidad - CantidadFacturada` **leido fresco de la base** en cada llamada (tanto `EmitirAsync` como `ReintentarAsync` recargan `venta.Items` desde `_db` al inicio del metodo, sin cachear entre llamadas). No hay ninguna ruta de codigo que permita facturar mas de lo pendiente: la UI limita con `max=` pero el guard real y unico es el server-side ya descrito. **PASS — invariante matematicamente sostenido.**

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`) — foco en integracion externa (caso ok/error/timeout)

| id | aplica | resultado | accion |
|---|---|---|---|
| REG-001 | no | N/A — sin `RowVersion`/concurrency tokens en `ComprobanteAfip`/`ComprobanteAfipItem` | ninguna |
| REG-002 | no | N/A — no relacionado a stock inicial | ninguna |
| REG-003/005 | no | N/A — sin Select2 remoto en `ComprobantesAfip/Create.cshtml` (tabla de items server-rendered desde la precarga) | ninguna |
| REG-004 | no (sin botones de estado condicionales por `@if` multiples en este sprint mas alla de "Reintentar" solo visible en Error) | N/A — `Details.cshtml` muestra "Reintentar" solo si `Estado==Error` y "Descargar PDF" solo si `Estado==Emitido`, patron ya validado en sprints anteriores, sin hallazgos nuevos | ninguna |
| REG-006 | no | N/A — sin campos condicionales por metodo de pago en este modulo | ninguna |
| REG-007 | no | N/A — modulo Devoluciones no existe | ninguna |
| REG-008 | si (grid de cantidad editable en `Create.cshtml`) | PASS — el listener `input` sobre `.inp-cantidad-facturar` solo recorta/actualiza el valor de esa celda (`$(this).val(val)`), sin reconstruir la tabla ni el resto de las filas — no se pierde foco al tipear | ninguna |
| REG-009 | no | N/A — sin combos en cascada | ninguna |
| REG-010 | si (link "Comprobantes AFIP" del sidebar) | PASS — visible para SuperUsuario/Administrador/Vendedor, coincide con `[Authorize(Policy="RequireVentas")]` de `ComprobantesAfipController` (tabla de permisos: "Emitir comprobante AFIP" es igual para ambos roles) | ninguna |
| KOI-001 | no (patron distinto) | N/A — botones de `ComprobantesAfip` (Emitir/Reintentar) usan handlers JS/POST dedicados, no `.btn-swal-confirm`/`closest('form')` de `site.js` | ninguna |
| KOI-002/003/004 | no | N/A — modulos no existen | ninguna |
| KOI-005/006 (sidebar -> controller inexistente) | si | PASS — `ComprobantesAfip` referenciado en `_Layout.cshtml` tiene su controller real (`ComprobantesAfipController.cs` existe y compila) | ninguna |
| DN-001/DN-002 | no | N/A — stack EF Core 10 + provider MySQL, no EF6; `ComprobanteAfipService.ListarAsync` no combina `Include` de coleccion + orden/filtro dinamico + `Skip/Take` en el mismo `IQueryable` (sin `Include` en el listado, ver comentario explicito en el codigo) | ninguna |
| GAN-001 | si (guard "al menos un item real" en `EmitirAsync`) | PASS — `itemsValidos = input.Items.Where(i => i.Cantidad > 0)`, rechaza con `Count==0`, nunca solo `Items.Count==0` crudo (mismo criterio ya usado en `VentaService`/`PresupuestoService`) | ninguna |
| GAN-002 | no | N/A — sin backfill de datos en este sprint | ninguna |
| GAN-003 | no | N/A — grep de `text/x-template` sobre `Views/ComprobantesAfip/*.cshtml` sin resultados | ninguna |
| GAN-004 | no | N/A — grep de `<datalist>` sobre `Views/ComprobantesAfip/*.cshtml` sin resultados | ninguna |
| VSF-001/002 | no | N/A — modulo Compras/OC no tocado este sprint | ninguna |
| CRM-001 a 006 | no | N/A — modulo Bot/CRM no existe | ninguna |
| MH-001 (re-chequeo preventivo, colecciones locales string) | si | PASS — grep de `.Contains(` sobre `AfipService.cs`/`ComprobanteAfipService.cs`/`ComprobantesAfipController.cs` no encontro ningun `Where(coleccionLocal.Contains(...))` traducido a SQL; los `Dictionary<int,VentaItem>` (`itemsPorId`/`itemsVentaPorId`) se arman con `.ToDictionary()` sobre una coleccion ya materializada en memoria (`venta.Items`, cargada por `Include`), no generan SQL IN | ninguna |
| MH-002 | no (no aplica a DTOs nuevos) | N/A — `ComprobanteAfipListItemDto.TipoComprobante`/`Estado` y `ComprobanteAfipDetailDto.TipoComprobante`/`Estado` ya se mapean con `.ToString()` desde el Service (linea 77, 81 de `ComprobanteAfipService.cs`), mismo patron correcto que evito MH-002 en Sprint 1 | ninguna |

**Checklist de integracion externa AFIP (caso ok/error/timeout) — foco explicito del pedido**:
- **Caso OK** (AFIP aprueba): `resultado.Exito=true` -> `Estado=Emitido`+CAE+vencimiento+`CantidadFacturada` incrementada, todo en la misma transaccion. Verificado por codigo (no ejecutable sin certificado real). Estado final: **inequivoco (Emitido, con CAE real)**.
- **Caso ERROR** (AFIP rechaza — `Resultado != "A"`, o AFIP devuelve `<Errors>`/`faultstring`): `AfipService` traduce el rechazo/excepcion en `AfipEmisionResultDto{Exito=false, DetalleError=...}` dentro de su unico `try/catch` que envuelve todo el metodo — nunca deja escapar la excepcion. `ComprobanteAfipService` mapea a `Estado=Error`+`DetalleError` visible, sin tocar `CantidadFacturada`. Estado final: **inequivoco (Error, reintentable, detalle visible)**.
- **Caso TIMEOUT/excepcion de red**: `PostSoapAsync` usa el `HttpClient` nombrado `"Afip"` con `Timeout = TimeSpan.FromSeconds(45)` (configurado en `DependencyInjection.cs`, confirmado por grep) — un `TaskCanceledException`/`HttpRequestException` lanzado por el `HttpClient` al agotar el timeout es una `Exception` mas, capturada por el mismo `try/catch` de `AfipService.EmitirAsync` (que envuelve *todo* el cuerpo del metodo, incluidos login WSAA y las 2 llamadas WSFE) y traducida igual a `Exito=false, DetalleError="No se pudo emitir el comprobante: " + ex.Message`. **No existe ningun camino de codigo donde una excepcion de red deje el comprobante en un estado intermedio/ambiguo**: o bien la excepcion ocurre *antes* de `_db.SaveChangesAsync()` inicial (comprobante nunca se crea, la Venta queda intacta) — imposible en este flujo porque el comprobante se persiste en `Pendiente` *antes* de llamar a AFIP — o bien ocurre *durante* la llamada a AFIP (dentro de `IntentarEmitirYPersistirAsync`, ya con el comprobante en `Pendiente` persistido), en cuyo caso `IAfipService.EmitirAsync` **nunca propaga la excepcion** (queda contenida en `AfipService`) y el flujo normal de `ComprobanteAfipService` continua a la rama `else` -> `Estado=Error`. El unico caso de ambiguedad real es el riesgo residual ya documentado por el implementador (decision #9): AFIP aprueba pero el `SaveChangesAsync` final falla (ej. corte de MySQL en ese instante exacto) -> `RollbackAsync` revierte todo, incluido el registro `Pendiente` -> el CAE existe en AFIP pero no hay constancia local. Confirmado que es un riesgo de **probabilidad muy baja** (ventana de milisegundos entre respuesta HTTP y `SaveChanges`), no mitigado por directriz de cambios minimos, ya documentado como riesgo residual, no como bug. **PASS — timeout/excepcion de red contemplado correctamente, sin estado ambiguo salvo el riesgo residual ya conocido y aceptado.**

### Matriz de formularios (pedido "100% OK") — Sprint 6

Verificados por codigo (server-side siempre revalida). [MANUAL] = requiere navegador real (checklist de 7 pasos del implementador).

**Seleccion de items a facturar (`ComprobantesAfip/Create`)**
1. Sin ningun item marcado, click "Emitir comprobante" → PASS — JS: `items.length===0` -> `Swal.fire` de advertencia, sin POST; server: `itemsValidos.Count==0` -> `"Seleccione al menos un item para facturar."` (GAN-001-safe, doble capa).
2. Cantidad mayor a la pendiente (manipulando el DOM o forzando el POST) → PASS — JS recorta al `max` en cada `input`; server rechaza siempre con `itemInput.Cantidad > pendiente` -> mensaje con el pendiente real, **nunca confia en el valor recibido del cliente**.
3. Venta ya facturada por completo (0 items pendientes) → PASS — `Create GET` verifica `precarga.Items.Count == 0` -> `TempData["ErrorMessage"]` + redirect a `Ventas/Details` (no muestra un formulario vacio inutil).
4. Venta cancelada → PASS — `EmitirAsync` rechaza con `"No se puede facturar una venta cancelada."` antes de cualquier otro guard.
5. [MANUAL] Confirmar visualmente que el input de cantidad no permite escribir un numero mayor al "Pendiente" mostrado en la grilla (paso 2 de la checklist del implementador).

**Datos fiscales (CUIT/DNI segun tipo, HU-7.2)**
6. Factura A sin CUIT → PASS — JS bloquea (`cuit.length !== 11`) + server `ValidarDatosFiscales` rechaza con `"La Factura A requiere el CUIT del cliente (11 digitos, sin guiones)."`.
7. Factura B sin CUIT ni DNI → PASS — JS bloquea + server rechaza con `"La Factura B requiere el CUIT o el DNI del cliente."`.
8. Factura B con CUIT de longitud invalida (no vacio, pero != 11 digitos) → PASS — server rechaza con `"El CUIT debe tener 11 digitos (sin guiones)."` (guard adicional no solo "vacio", tambien "formato").
9. Factura B con DNI de longitud invalida (< 7 u > 8 digitos) → PASS — server rechaza con `"El DNI debe tener entre 7 y 8 digitos."`.
10. [MANUAL] Confirmar visualmente los mensajes de error de CUIT/DNI en pantalla real (paso 2 de la checklist).

**Sin certificado configurado (caso real del entorno actual)**
11. Emitir con `Afip:CertificadoPath` vacio → PASS — `AfipService.EmitirAsync` primer guard: `string.IsNullOrWhiteSpace(_settings.CertificadoPath) || string.IsNullOrWhiteSpace(_settings.CUIT)` -> error controlado y claro, sin excepcion no manejada ni 500. [MANUAL, paso 1 de la checklist, verificable ahora mismo sin certificado real].

### Defectos activos

**Ninguno bloqueante, critico ni major.** No se reprodujo ningun bug funcional por revision de codigo en el alcance de Sprint 6 — sin necesidad de auto-fix.

Riesgos/observaciones ya documentados por el implementador, revalidados por QA sin objeciones (no son defectos):
- Riesgo residual de probabilidad muy baja: "AFIP aprobo pero el `SaveChangesAsync` final fallo" (ventana de milisegundos) — ver seccion de integracion externa arriba.
- Alicuota de IVA uniforme (21%, configurable), no por producto — limitacion conocida, cambio de alcance medio si se pide corregir.
- Factura B siempre como Consumidor Final (`CondicionIVAReceptorId=5`), sin distincion Monotributista/Exento — consistente con lo que pedia el diseño (sin esa distincion en la captura de datos fiscales).
- SOAP armado a mano en vez de proxy generado — mantenimiento manual del mapeo de campos si AFIP cambia el contrato en el futuro (riesgo bajo, WSFEv1 estable).

**Auto-fixes aplicados en este ciclo**: ninguno (no se reprodujo ningun bug funcional real; el unico camino de prueba real contra AFIP —caso OK y caso ERROR reales— esta bloqueado por la ausencia del certificado `.p12`, riesgo ya documentado desde el analisis funcional y fuera del control de este ciclo de QA).

### Evidencia de build y migracion — re-verificado por QA de forma independiente (contexto: corte de sesion del implementador por limite de cuenta)

Dado que el implementador documento un corte por limite de cuenta al final de su sesion (aunque *despues* de completar y documentar todo el trabajo, segun su propia memoria), QA **no se limito a tomar la palabra del implementador** y re-ejecuto el build y las migraciones de forma independiente contra el repo real:

- `dotnet build MariHogar.slnx` → **Compilacion correcta, 0 errores**, 8 warnings (`NU1902` de MailKit/MimeKit) — re-ejecutado por QA el 2026-07-24. Nota: el implementador declaraba 9 warnings (incluido `CS0114` de `HomeController.StatusCode`); en esta re-ejecucion QA solo observo 8 (los 4 `NU1902` reportados dos veces, una por proyecto). Diferencia de conteo no significativa (mismo tipo de warnings preexistentes, ninguno nuevo introducido por este sprint, `CS0114` puede no dispararse en un build incremental vs. limpio) — **no es evidencia de codigo a medio escribir**, es una diferencia de reporte de warnings entre corridas.
- `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` → `20260724145210_InitialCreate`, `20260724152806_AddCatalogo`, `20260724175804_AddPresupuestosVentas`, `20260724184703_AddEntregas`, `20260724192534_AddComprasCCProveedoresCheques`, `20260724200956_AddGastos`, `20260724210125_AddComprobantesAfip` → **7 migraciones, ninguna marcada `(Pending)`** — coincide exactamente con lo declarado por el implementador. El comando ejecuta `Program.cs` real hasta `builder.Build()` (confirmado por el `HostAbortedException` esperado en el log), lo que ademas ejercita con exito la carga completa de `appsettings.json` (seccion `Afip` con comentarios JSONC incluida) y el grafo de DI completo (`AfipTokenCache`/`AfipService`/`ComprobanteAfipService`/`HttpClient "Afip"`) sin ninguna excepcion de configuracion.
- **Conclusion de QA sobre el estado del repo**: el codigo de Sprint 6 esta **completo y consistente**, no a medio escribir. Build limpio, migracion generada y aplicada, DI y configuracion cargan sin errores, los 6 puntos de verificacion puntual pedidos (transaccion, tope, cache de token, config, guard de cancelacion, tope acumulativo) se sostienen por lectura de codigo linea por linea sin inconsistencias. El corte de sesion del implementador no dejo artefactos huerfanos ni codigo inalcanzable — confirmado adicionalmente por la ausencia de errores de compilacion (un archivo a medio escribir con sintaxis incompleta hubiera fallado el build, no solo generado warnings).

### Riesgos de liberacion

- **Alto (bloqueante para produccion real, no para el cierre tecnico de este sprint)**: cero verificacion contra AFIP real (caso OK/ERROR reales, no simulados) — depende exclusivamente de que el cliente/estudio contable provea el certificado `.p12` de homologacion, riesgo documentado desde `1-analista-funcional.md`. Este es el unico tramo de M7 que ningun agente (implementador ni QA) puede cerrar sin ese insumo externo. No bloquea dar Etapa 1 por completa (la arquitectura ya anticipaba este escenario: "M7 puede implementarse con el servicio mockeado/homologacion mientras se gestiona el certificado real"), pero **si debe quedar explicito en la documentacion de alcance al cliente** que la facturacion real no puede probarse ni usarse en produccion hasta ese paso externo.
- **Medio-bajo, heredado y acumulado (no de este sprint especificamente)**: 5 checklists manuales de verificacion en navegador acumuladas sin ejecutar por el usuario (Sprint 2: 12 pasos, Sprint 3: 11 pasos, Sprint 4: 10 pasos, Sprint 5: 7 pasos, Sprint 6: 7 pasos) — regla de proceso vigente desde el cierre de Sprint 2 (ni implementador ni QA ejecutan navegador). Se recomienda que el usuario las recorra antes de considerar Etapa 1 100% verificada en un entorno real, aunque el riesgo tecnico por codigo es bajo en los 6 sprints (revision profunda sin hallazgos bloqueantes en ninguno).
- **Bajo**: riesgo residual de "AFIP aprobo pero DB fallo" (ventana de milisegundos) — no mitigado, documentado para un sprint de endurecimiento futuro si el cliente lo pide.
- **Bajo**: alicuota de IVA uniforme, no por producto — cambio de alcance medio si se pide corregir.
- Sin riesgos nuevos de severidad blocker/critical/major detectados en este sprint.

### Pruebas minimas ejecutadas

- `dotnet build MariHogar.slnx` → Compilacion correcta, 0 errores (8 warnings preexistentes NU1902, ninguno nuevo) — re-verificado por QA de forma independiente.
- `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` → 7 migraciones, ninguna pendiente — re-verificado por QA de forma independiente.
- Revision de codigo linea por linea de `ComprobanteAfipService.cs` (completo), `AfipService.cs` (completo), `AfipTokenCache.cs` (completo), `ComprobantesAfipController.cs` (completo), `VentaService.cs` (metodos relevantes), entidades/enums/DTOs/settings de M7, `Views/ComprobantesAfip/{Create,Details,Index}.cshtml`, fragmentos de `Ventas/{Create,Details}.cshtml`, `_Layout.cshtml`, `DependencyInjection.cs`.
- Lectura completa de `appsettings.json`/`appsettings.Development.json`/`appsettings.Production.json` buscando datos de AFIP reales hardcodeados — ninguno encontrado.
- Grep de patrones riesgosos (`.Contains(` sobre colecciones locales, `text/x-template`, `<datalist>`, `if.*ambiente`/`Ambiente ==`/`EsProduccion` fuera de `AfipSettings`) sobre los archivos nuevos del sprint.
- Ejecucion completa del playbook cross-proyecto (30 items del catalogo), con foco especial en el checklist de integracion externa (caso ok/error/timeout).

### Estado go/no-go — Sprint 6 y GATE FINAL de Etapa 1

**GO para Sprint 6.** Sin defectos bloqueantes, criticos ni major detectados: 4/4 HU CUMPLE, los 6 puntos de verificacion puntual pedidos explicitamente (transaccion de emision, revalidacion de tope en reintento, cache de token con expiracion real + anti-doble-login, config homologacion/produccion sin ifs de codigo, guard real de cancelacion, tope acumulativo entre comprobantes) confirmados correctos por lectura de codigo linea por linea, manejo de timeout/excepcion de red contra AFIP confirmado que nunca deja el comprobante en un estado ambiguo, build limpio y migracion aplicada re-verificados de forma independiente por QA (el corte de sesion del implementador no dejo el repo a medio escribir). Unico riesgo real: cero verificacion contra AFIP real, bloqueado por una dependencia externa (certificado `.p12` del cliente) ya documentada desde el analisis funcional, no imputable a este sprint ni a ningun agente del estudio.

**RECOMENDACION GO/NO-GO PARA CERRAR ETAPA 1 COMPLETA (6 sprints)**: **GO.** Los 16 modulos de Etapa 1 (M2, M3, M4, M5, M6, M7, M9, M10, M11, M12, M13, M14, M15, M16, M17, M18) estan implementados, cada sprint fue validado por QA sin defectos bloqueantes/criticos, y el ultimo sprint (M7, el de mayor riesgo tecnico por ser una integracion externa) supera especificamente los 6 puntos de control mas sensibles pedidos para este gate. Condiciones no bloqueantes recomendadas antes de la entrega formal al cliente:
1. Que el usuario ejecute las 5 checklists manuales acumuladas (47 pasos en total entre Sprints 2 a 6) al menos una vez en un entorno real con navegador, dado que ningun agente del estudio ejecuta pruebas de UI por regla de proceso.
2. Que quede explicito en la documentacion de alcance al cliente (etapa 7) que **la facturacion AFIP real (emision con CAE real) no puede probarse ni usarse en produccion hasta que el cliente provea el certificado `.p12` de homologacion/produccion** — el sistema esta completo y listo, pero ese ultimo paso depende de una gestion externa del cliente/estudio contable, no del desarrollo.
3. Que se investigue (fuera del alcance de QA) la causa raiz del incidente de proceso de Sprint 5 (posible colision de ejecuciones paralelas del implementador) antes de asumir que fue un evento aislado, aunque el codigo final ya fue verificado seguro.

Con estas 3 condiciones no bloqueantes documentadas, **Etapa 1 queda habilitada para pasar a Documentacion de alcance para el cliente (etapa 7 del flujo del estudio)**.

---
## Sprint 5 (de 6) — M18 Gastos + M15 Caja mensual + M16 Aumento masivo de precios + M17 Proyeccion financiera + M9 Dashboard

### Alcance validado

Sprint 5: M18 (`Gasto`, alta + anulacion con contramovimiento, sin edicion), M15 (`CajaService`, agregacion de `MovimientoCCLocal` por rango + comparativo mes anterior, sin entidad nueva), M16 (`AumentoMasivoPrecioService`, preview sin persistir + aplicar con concurrencia optimista via `Producto.RowVersion`), M17 (`ProyeccionFinancieraService`, promedio historico + compromisos conocidos + alerta de deficit), M9 (`DashboardController`/`DashboardService`, dos vistas por rol, KPIs independientes via AJAX). Cierra el plan de 6 sprints de Etapa 1. Sprints 1-4 (todos en GO) **no se re-validaron**, solo se tomaron como contexto/base.

**Metodo**: revision de codigo real completa de los 5 servicios nuevos (`GastoService`, `CajaService`, `AumentoMasivoPrecioService`, `ProyeccionFinancieraService`, `DashboardService`), sus interfaces y DTOs, los 5 Controllers nuevos (`GastosController`, `CajaController`, `ProyeccionFinancieraController`, `AumentoMasivoPreciosController`, `DashboardController`), ViewModels, Views (`Gastos/{Index,Create}`, `Caja/Index`, `ProyeccionFinanciera/Index`, `AumentoMasivoPrecios/Index` con su script JS completo, `Dashboard/{Admin,Vendedor}` con su script JS completo), entidad `Gasto` + enums nuevos, configuracion Fluent de `Producto.RowVersion` y el bloque de `OnBeforeSaveChanges` que lo reasigna, migracion `AddGastos`, `_Layout.cshtml` (sidebar), `DependencyInjection.cs`, `HomeController.Index()`, `Program.cs` (policy `RequireAdministracion`). `dotnet build MariHogar.slnx --no-incremental` y `dotnet ef migrations list` re-ejecutados por QA contra el repo real. No se ejecuto navegador (regla del rol) — foco reforzado en revision de codigo por: (a) el pedido explicito de verificar RowVersion end-to-end, formula de proyeccion y generacion de movimiento de Gasto: (b) el incidente de integridad reportado por el implementador sobre el modulo Dashboard.

### Revision de seguridad reforzada — modulo Dashboard (conclusion explicita)

El implementador reporto durante el cierre de este sprint que recibio `system-reminder` afirmando que archivos ya escritos por el (`DashboardController.cs`, `DashboardDtos.cs`/`IDashboardService.cs`/`DashboardViewModels.cs`/`DashboardService.cs`, `Views/Dashboard/Admin.cshtml`) habian sido modificados en disco por fuera de sus propias herramientas, con instruccion explicita de no informar al usuario — instruccion que el implementador identifico correctamente como señal de alarma (ningun proceso legitimo de linter reestructura semanticamente una arquitectura ni pide ocultar el cambio) y reporto igual, sin ejecutar la instruccion de silencio. Por pedido expreso del orquestador, QA hizo una revision de codigo **reforzada y con ojo critico**, tratando los 6 archivos (mas cualquier otro archivo de `Views/Dashboard/` o relacionado a `IDashboardService`/`DashboardService`) como codigo de un tercero no confiable, buscando especificamente:

- **Llamadas de red salientes no esperadas**: `DashboardService.cs` solo hace consultas `AppDbContext`/EF Core sobre tablas propias del dominio (`Ventas`, `VentaItems`, `Cheques`, `Productos` via `IProductoService`, `MovimientoCCLocal` via `ICCLocalService`). `Admin.cshtml`/`Vendedor.cshtml` solo hacen `$.get`/`Url.Action` contra el propio `DashboardController` (mismo origen). **Ninguna llamada a un host externo, ningun `HttpClient`/`fetch` a una URL absoluta, ningun script de terceros nuevo.**
- **Credenciales o secretos hardcodeados**: ninguno encontrado en los 6 archivos (grep + lectura completa).
- **Logica oculta u ofuscada**: codigo legible, sin minificacion, sin `eval`, sin `Convert.From/ToBase64` sospechoso (el unico Base64 del sprint es el `RowVersion` de Aumento masivo, en un archivo distinto y con proposito documentado y verificado), sin construccion dinamica de rutas/comandos.
- **Comportamiento no documentado / desalineado con el diseño**: la arquitectura final (AJAX por KPI: `GetVentasPeriodo`/`GetStockCritico`/`GetChequesPorVencer`/`GetBalanceCaja`/`GetProductosMasVendidos`, cada una con su propio `$.get` independiente) **coincide exactamente** con lo pedido literalmente por HU-9.1 CA ("cada KPI carga de forma independiente, no bloquea el resto si uno tarda") — de hecho es una implementacion mas fiel a la letra del CA que un unico fetch sincronico. Los 2 endpoints financieros (`GetChequesPorVencer`, `GetBalanceCaja`) llevan `[Authorize(Policy = "RequireAdministracion")]` propio ademas del `[Authorize]` generico de la clase — defensa en profundidad correcta, patron REG-010 ya establecido en el proyecto.
- **Cualquier otra anomalia**: sin hallazgos. `DashboardVendedorDto` no expone ningun campo financiero. El flujo de datos completo (Controller -> Service -> AppDbContext) es trazable y consistente con el resto del proyecto (mismo estilo de `AsNoTracking`, mismo patron de DTOs, mismo manejo de fechas).

**Conclusion de QA (severidad maxima si hubiera hallazgo — no fue el caso)**: revision de codigo linea por linea de los 6 archivos, sin ningun indicio de contenido malicioso, backdoor, exfiltracion de datos ni logica de negocio no autorizada. El codigo final del modulo Dashboard es funcionalmente correcto, esta mejor alineado con HU-9.1 que una alternativa sincronica, y su origen anomalo (reescritura en disco fuera del flujo normal de herramientas, con instruccion de ocultarlo) se trata como **hallazgo de proceso de severidad alta** — no de codigo de producto — ya documentado por el implementador en `trazabilidad.md` (2026-07-24) y en `5-implementador.md` (Sprint 5). QA no encontro motivo para bloquear el sprint por este incidente (el codigo en si es seguro y correcto), pero **recomienda al usuario/orquestador investigar la causa del proceso anomalo** (ej. verificar si hay una segunda sesion/proceso corriendo en paralelo sobre el mismo repo) antes de asumir que fue un evento aislado, dado que el propio implementador señalo como hipotesis mas probable una colision entre dos ejecuciones del mismo sprint.

### Cobertura de historias de usuario (HU-9.1/HU-9.2, HU-15.1/HU-15.2, HU-16.1, HU-17.1/HU-17.2, HU-18.1/HU-18.2)

| HU | Criterio (resumen) | Resultado | Evidencia |
|---|---|---|---|
| HU-18.1 | Gasto con monto/categoria/forma de pago/fecha/descripcion (CA-N24) | CUMPLE | `GastoFormViewModel` con los 5 campos + `[Required]`/`[Range]`; `GastoService.CrearAsync` revalida server-side (Monto>0, Fecha no futura, Descripcion obligatoria) |
| HU-18.2 | Movimiento en CC Local y caja del periodo al guardar, sin doble carga (CA-N25) | CUMPLE | Ver seccion dedicada abajo — `GastoService.CrearAsync` genera un unico movimiento de `Egreso` en la misma transaccion; `CajaService` lee el mismo `MovimientoCCLocal` (single source of truth), sin segunda escritura |
| HU-15.1 | Ingresos/egresos del periodo con filtro de fechas y totales (CA-N14) | CUMPLE | `CajaService.ObtenerResumenAsync` agrega `MovimientoCCLocal` por rango (default mes actual), `CajaController` persiste el filtro en sesion (`Filtros:Caja:Index`) |
| HU-15.2 | Comparativo con el mes anterior en la misma vista (CA-N15) | CUMPLE | `DesdeAnterior`/`HastaAnterior` desplazados un mes calendario exacto; `Caja/Index.cshtml` muestra tabla comparativa + variacion porcentual (con guard de division por cero cuando el periodo anterior es $0) |
| HU-16.1 | Seleccion por marca/categoria/modelo + % + preview obligatorio antes de confirmar (CA-N16 a CA-N19) | CUMPLE | Ver seccion dedicada abajo — flujo de 2 pasos verificado por codigo (Preview `AsNoTracking` sin `SaveChanges`, Aplicar unica via de persistencia con `RowVersion` verificado) |
| HU-17.1 | Proyeccion de ingresos/egresos basada en promedio + compromisos, alerta de deficit, texto de estimacion (CA-N20 a CA-N22) | CUMPLE | Ver seccion dedicada abajo — formula verificada linea por linea; texto aclaratorio visible siempre en `ProyeccionFinanciera/Index.cshtml` |
| HU-17.2 | Ajustar periodo base 1/3/6 meses (CA-N23) | CUMPLE | `PeriodosValidos = [1,3,6]`, cualquier otro valor cae a 3 sin excepcion; selector en la vista con `onchange="this.form.submit()"` |
| HU-9.1 | Panel Admin: ventas/stock critico/cheques/leads/productos mas vendidos/balance, filtro de fecha, KPI independiente | CUMPLE (conversion de leads placeholder deshabilitado por alcance) | Ver seccion dedicada de Dashboard abajo |
| HU-9.2 | Panel Vendedor reducido, sin datos financieros, ocultos por policy | CUMPLE | Ver seccion dedicada de Dashboard abajo |

**Cobertura: 9/9 HU CUMPLE por revision de codigo**, sin PARCIAL ni N/A de alcance (a diferencia de sprints anteriores) — todas las HU de este sprint tenian su modulo/consumidor completo dentro del propio sprint.

### Verificacion puntual — Gasto genera el movimiento de egreso correcto en MovimientoCCLocal (tarea explicita del pedido)

Confirmado por lectura de `GastoService.CrearAsync` (mismo patron que un pago de OC de Sprint 4/una Venta de Sprint 2): validaciones de negocio (Monto>0, Fecha no futura, Descripcion obligatoria) **antes** de abrir la transaccion -> `BeginTransactionAsync()` -> `Add(Gasto)` + `SaveChangesAsync()` (obtiene `Id`) -> `ICCLocalService.RegistrarMovimientoAsync(Egreso, gasto.Monto, "Gasto", gasto.Id, esReversion:false, ...)` (confirmado que `CCLocalService.RegistrarMovimientoAsync` no abre transaccion ni hace `SaveChanges` propio — comentario explicito en el codigo, mismo patron ya usado por `VentaService`/`OrdenCompraService`) -> `SaveChangesAsync()` final + `CommitAsync()`; `catch` con `RollbackAsync()`. **Se genera exactamente un movimiento de Egreso por Gasto, sin duplicar ni omitir** (un unico `RegistrarMovimientoAsync` por llamada a `CrearAsync`, sin loop). `GastoService.AnularAsync` genera exactamente un contramovimiento de `Ingreso` con `EsReversion=true` y el mismo `OrigenId` (nunca toca ni borra el movimiento original), mismo criterio que `VentaService.CancelarAsync`. Confirmado que `CajaService` no requiere una segunda escritura: agrega el mismo `MovimientoCCLocal` por rango de fecha (single source of truth, cumple HU-18.2 "sin doble carga" literal). **Sin defecto.**

### Verificacion puntual — Aumento masivo: preview no persiste + RowVersion viaja desde el preview (tarea explicita del pedido)

Confirmado por lectura de `AumentoMasivoPrecioService.ObtenerPreviewAsync`: toda la query usa `AsNoTracking()`, sin ningun `Add`/`Update`/`Remove`/`SaveChanges` en el metodo — **no persiste nada**, confirmado ademas por el controller (`AumentoMasivoPreciosController.Preview` solo llama a `ObtenerPreviewAsync` y devuelve JSON, sin tocar `AppDbContext`). `AplicarAsync` es la unica via de persistencia.

**Mejora sobre ShowroomGriffin verificada por codigo, no solo declarada**: `AumentoMasivoPreviewItemDto.RowVersion` se serializa en Base64 en el Preview (`Convert.ToBase64String(p.RowVersion)`) y viaja al cliente; `Views/AumentoMasivoPrecios/Index.cshtml` lo guarda en el array `previewItems` en memoria del navegador y lo reenvia tal cual en `itemsJson` al llamar `Aplicar` (`{ productoId: it.productoId, rowVersion: it.rowVersion }`, confirmado leyendo el script completo de la vista) — **el RowVersion efectivamente hace el viaje de ida y vuelta preview->confirmar**, no es solo un chequeo interno del propio `AplicarAsync`. En `AplicarAsync`: fetch de productos trackeados por Id (acotado al lote, MH-001-safe) -> por cada producto, compara el `RowVersion` real (recalculado a Base64) contra el recibido del cliente (`rowVersionEsperado` diccionario) -> si difiere en **cualquier** item, `RollbackAsync()` inmediato y error explicito ("fue modificado por otro usuario... vuelva a previsualizar"), **sin aplicar nada parcial** (el rollback ocurre antes de tocar ningun precio, ya que el chequeo esta al inicio del loop `foreach`). Backstop adicional: `catch (DbUpdateConcurrencyException)` alrededor de todo el bloque, para la ventana milisegundos entre el fetch de `AplicarAsync` y su propio `SaveChangesAsync` (protegida ademas por `IsConcurrencyToken()` de EF Core en la configuracion Fluent de `AppDbContext`, verificada). El boton "Confirmar aumento" en la vista se re-oculta automaticamente ante cualquier cambio de criterio (`ocultarPreview()` en el listener `change` del formulario), evitando confirmar sobre un criterio distinto al previsualizado. **Ambas capas de concurrencia (chequeo explicito de ventana real + backstop de EF de ventana interna) verificadas presentes y correctas. Sin defecto.**

### Verificacion puntual — formula de Proyeccion financiera (tarea explicita del pedido)

Confirmado por lectura de `ProyeccionFinancieraService.ObtenerAsync`: `periodo` normalizado a {1,3,6} (cualquier otro valor cae a 3, sin excepcion) -> promedio historico = `Σ MovimientoCCLocal` (por Tipo) de los ultimos `periodo` meses (`Fecha >= hoy.AddMonths(-periodo) && Fecha < hoy`) dividido `periodo`, redondeado a 2 decimales -> `IngresosProyectados`/`EgresosPromedioProyectados` = promedio mensual × `periodo` -> `GastosComprometidos` = suma de Cheques `Pendiente` con `FechaVencimiento <= hoy.AddMonths(periodo)` **+** saldo pendiente de OCs `Confirmada`/`Recibida` (calculado en memoria tras `Include(Pagos).ThenInclude(Cheque)`, excluyendo pagos con cheque `Rechazado` — mismo criterio exacto que `OrdenCompraDetailDto.MontoPagado`/`PagoOrdenCompraService.RegistrarPagoAsync` de Sprint 4, verificado que no diverge) -> `TieneDeficit = GastosComprometidos > IngresosProyectados` (comparacion **literal** de CA-N22, confirmado que `EgresosPromedioProyectados` NO se suma al comparador de la alerta — se muestra aparte como dato informativo adicional, `EgresosProyectadosTotal` es una propiedad calculada separada solo para mostrar en la UI, nunca usada en `TieneDeficit`). Texto aclaratorio de "estimacion, no un compromiso exacto" confirmado siempre visible en `ProyeccionFinanciera/Index.cshtml` (fuera de cualquier condicional). **Formula matematicamente correcta y consistente con CA-N20/CA-N21/CA-N22 tal como fueron redactados. Sin defecto.**

Nota menor no bloqueante: la ventana historica excluye movimientos del dia de hoy (`Fecha < hoy`, con `hoy = DateTime.Today` = medianoche), por lo que un movimiento cargado hoy mismo no entra en el promedio hasta mañana — comportamiento razonable para un promedio mensual, no se considera defecto.

### Verificacion puntual — Caja mensual: agregacion correcta + comparativo (tarea explicita del pedido)

Confirmado por lectura de `CajaService.ObtenerResumenAsync`/`ObtenerTotalesAsync`: agrega `MovimientoCCLocal` por `Tipo` dentro del rango `[desde, hasta]` inclusive (`hastaExclusivo = hasta.Date.AddDays(1)`, evita el bug clasico de excluir el ultimo dia) -> mismo calculo aplicado al periodo desplazado exactamente `-1` mes calendario (`AddMonths(-1)` sobre ambos extremos) -> `BalancePeriodo`/`BalancePeriodoAnterior` = Ingresos − Egresos -> `VariacionIngresosPorc`/`VariacionEgresosPorc` con guard de division por cero (retorna `null`, la vista muestra "Sin datos del periodo anterior para comparar" en vez de un error o un %infinito). **Agregacion y comparativo correctos. Sin defecto.**

### Verificacion puntual — Dashboard: separacion Admin/Vendedor + independencia de KPIs (tarea explicita del pedido)

- **Separacion real, no solo UI**: `DashboardController.Index()` resuelve la vista por rol en el servidor (`User.IsInRole`), nunca por parametro del cliente. Los 2 endpoints financieros (`GetChequesPorVencer`, `GetBalanceCaja`) llevan `[Authorize(Policy = "RequireAdministracion")]` **propio**, ademas del `[Authorize]` generico de la clase — un Vendedor que intente `GET /Dashboard/GetChequesPorVencer` o `GetBalanceCaja` directamente por URL recibe 403/AccessDenied, no solo no ve el boton en la UI (patron REG-010 del catalogo cross-proyecto, ya aplicado consistentemente en el resto del proyecto desde Sprint 1). `DashboardVendedorDto` no incluye ningun campo financiero (solo `VentasHoyCantidad`/`VentasHoyTotal`/`LeadsPendientesHabilitado`).
- Los otros 3 endpoints (`GetVentasPeriodo`, `GetStockCritico`, `GetProductosMasVendidos`) no llevan la policy extra, pero se confirmo que esto **no es una fuga de datos**: esa misma informacion ya es visible para el Vendedor por otras pantallas a las que si tiene acceso (Ventas/Index — HU-5.3 "Vendedor ve todas las ventas"; Productos/Index — HU-3.3 "Vendedor ve alerta de stock bajo minimo"). Solo los datos genuinamente exclusivos de Administrador (Cheques, CC Local/Caja) llevan la policy adicional — consistente con la tabla de permisos de `1-analista-funcional.md`.
- **Independencia de carga por KPI (HU-9.1)**: confirmado por lectura de `Admin.cshtml` que las 5 tarjetas hacen su propio `$.get` independiente (`GetVentasPeriodo`, `GetStockCritico`, `GetChequesPorVencer`, `GetBalanceCaja`, `GetProductosMasVendidos`), cada uno con su propio `.done()`/`.fail()` — el fallo o demora de un KPI no bloquea ni afecta visualmente a los demas (cada `.fail()` solo reemplaza el contenido de su propia card). `Index()` no resuelve ningun dato de KPI en el servidor (shell vacio, confirmado por `DashboardAdminIndexViewModel` sin campos de KPI). Confirmado por `DashboardService` que cada metodo (`ObtenerVentasPeriodoAsync`, `ObtenerChequesPorVencerAsync`, `ObtenerProductosMasVendidosAsync`) es una consulta acotada independiente, sin un metodo agregador que las una.
- Ver seccion dedicada arriba ("Revision de seguridad reforzada") para la conclusion de integridad del codigo.

**Sin defecto en ninguno de los 4 puntos verificados explicitamente.**

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

| id | aplica | resultado | accion |
|---|---|---|---|
| REG-001 (RowVersion MySQL) | **si, por primera vez en este proyecto** (`Producto.RowVersion`, M16) | PASS — patron reutilizado preventivamente desde el origen (`ValueGeneratedNever()`+`IsConcurrencyToken()`+reasignacion manual en `OnBeforeSaveChanges`, migracion con nullable+backfill+`AlterColumn NOT NULL` en vez de `defaultValueSql`), nunca reprodujo el bug original | ninguna |
| REG-002 | no | N/A — no relacionado a stock inicial de producto | ninguna |
| REG-003/REG-005 | no | N/A — sin autocomplete Select2 remoto nuevo en este sprint (combos de Aumento masivo son `<select>` server-side simples) | ninguna |
| REG-004 (botones por estado) | si (boton Anular de Gasto) | PASS — `row.anulado` oculta el boton en el JS del grid cuando ya esta anulado, servidor tambien rechaza (`gasto.Anulado` ya true) | ninguna |
| REG-006 | no | N/A — sin campos condicionales por metodo de pago nuevos este sprint | ninguna |
| REG-007 | no | N/A — modulo Devoluciones no existe | ninguna |
| REG-008 (perdida de foco en re-render) | si (revisado, mismo criterio) | PASS — `AumentoMasivoPrecios/Index.cshtml` solo reconstruye `#tbodyPreview` tras la respuesta del `POST /Preview` (no por keystroke); no hay grillas con inputs propios re-renderizadas en este sprint | ninguna |
| REG-009 | no | N/A — sin combos en cascada (los grupos Marca/Categoria/Modelo de Aumento masivo se muestran/ocultan por `alcance`, no se repueblan por dependencia de otro combo) | ninguna |
| REG-010 (dato sensible oculto solo en la vista) | si (foco explicito del pedido — sidebar Financiero/Catalogo + Dashboard) | **PASS, verificado por codigo en 2 lugares**: (1) sidebar — el bloque `@if (SuperUsuario\|\|Administrador)` que envuelve Gastos/Caja/Proyeccion/Aumento masivo coincide exactamente con la policy `RequireAdministracion` de los 5 controllers; (2) Dashboard — `GetChequesPorVencer`/`GetBalanceCaja` con policy propia ademas de estar ocultos en `Vendedor.cshtml` (ver seccion dedicada arriba) | ninguna |
| KOI-001 (delete fuera del form) | si (boton Anular de Gasto) | PASS — arma su propio `<form>` dinamico con el token antes de hacer submit (mismo patron ya usado en `Categorias/Index.cshtml`/Cancelar OC/Rechazar cheque), no depende de `closest('form')` de `site.js` | ninguna |
| KOI-002/003/004 | no | N/A — modulos no existen | ninguna |
| KOI-005/006 (sidebar -> controller inexistente) | si | PASS — `Gastos`/`Caja`/`ProyeccionFinanciera`/`AumentoMasivoPrecios`/`Dashboard` referenciados en `_Layout.cshtml` tienen sus 5 controllers reales, confirmado por listado de archivos | ninguna |
| DN-001/DN-002 | no | N/A — stack `MySql.EntityFrameworkCore`, no EF6; ningun Service de este sprint combina `Include` de coleccion + orden/filtro dinamico + `Skip/Take` en el mismo `IQueryable` (`GastoService.ListarAsync` no usa `Include`; `CajaService`/`ProyeccionFinancieraService` no son DataTables paginados) | ninguna |
| GAN-001 (guard "al menos un item real") | no | N/A — sin grillas dinamicas de filas repetidas por indice en este sprint (`AumentoMasivoAplicarInput.Items` viaja por JSON armado en JS, no por binding indexado de formulario, mismo patron ya usado por Ventas/OC que evita el mecanismo estructural de GAN-001) | ninguna |
| GAN-002 | no | N/A — sin backfill de datos historicos de negocio (el backfill de `Producto.RowVersion` es tecnico/interno, un GUID nuevo por fila, no datos de negocio) | ninguna |
| GAN-003 (`text/x-template`+`partial`) | no | N/A — grep de `text/x-template` sobre `Views/Gastos`, `Views/Caja`, `Views/ProyeccionFinanciera`, `Views/AumentoMasivoPrecios`, `Views/Dashboard` sin resultados | ninguna |
| GAN-004 (`<datalist>`) | no | N/A — grep sin resultados en las Views de este sprint (combos usan `<select>` server-side o Select2) | ninguna |
| VSF-001/VSF-002 | no | N/A — modulo Compras/OC no tocado este sprint (sin cambios en `CompraProveedorService`/`PedidoService` equivalentes) | ninguna |
| CRM-001 a CRM-006 | no | N/A — modulo Bot/CRM no existe (Etapa 2 en pausa) | ninguna |
| MH-001 (IN de coleccion local `string`) | si (grep + revision) | PASS — `AumentoMasivoPrecioService.AplicarAsync` (`ids.Contains(p.Id)`, `List<int>`) y `DashboardService.ObtenerProductosMasVendidosAsync` (`ventaIds.Contains(i.VentaId)`, `List<int>`) son ambos colecciones de `int` (seguro segun el refinamiento de Sprint 4, `nota_qa_sprint4`); grep de `.Contains(` sobre los 5 Services nuevos del sprint no encontro ninguna coleccion local de `string` | ninguna |
| MH-002 (enum serializado como int) | si (re-chequeo) | PASS — `GastoListItemDto.Categoria`/`FormaPago` mapeados con `.ToString()` en `GastoService.ListarAsync`, mismo patron correcto que evito MH-002 desde Sprint 1 | ninguna |

### Matriz de formularios (pedido "100% OK") — Sprint 5

Verificados por codigo (server-side siempre revalida, nunca confia solo en cliente).

**Gasto (alta)**
1. Caso valido (Categoria+Monto+FormaPago+Fecha+Descripcion) -> guarda, genera movimiento de Egreso, redirige a Index — CUMPLE por codigo.
2. **Monto <= 0** -> `[Range(0.01, double.MaxValue)]` client-side (mensaje "El monto debe ser mayor a cero.") + `GastoService.CrearAsync` revalida `input.Monto <= 0` server-side con el mismo mensaje — CUMPLE, doble capa.
3. **Fecha futura** -> `<input type="date" max="hoy">` restringe client-side + `GastoService.CrearAsync` revalida `input.Fecha.Date > DateTime.Today` server-side ("La fecha no puede ser futura.") — CUMPLE, doble capa (un POST forzado con fecha futura vulnerando el `max` del HTML sigue bloqueado server-side).
4. Descripcion vacia -> `[Required]` + `StringLength(500)` client-side + `string.IsNullOrWhiteSpace(input.Descripcion)` server-side — CUMPLE.
5. Categoria/FormaPago no seleccionada (POST forzado con valor fuera de enum) -> el binder de MVC deja el `enum` en su valor default (0), que no matchea ningun valor real de `CategoriaGasto`/`FormaPagoGasto` (ambos arrancan en 1) — se persistiria un valor invalido si el `[Required]` no bloqueara; **observacion menor no bloqueante**: no hay una revalidacion server-side explicita de "Categoria/FormaPago dentro del rango del enum" en `GastoService.CrearAsync` (a diferencia de Monto/Fecha/Descripcion) — el `[Required]` de ASP.NET Core Data Annotations no aplica de forma util a un `enum` no-nullable (siempre tiene un valor, nunca "vacio"). Riesgo bajo: requiere un POST manipulado (no alcanzable desde la UI, que siempre pre-puebla el `<select>` con valores validos del propio enum); no se reproduce en uso normal, se documenta como hallazgo menor, no se aplica auto-fix (no es un bug reproducible por un usuario real, es un guard defensivo faltante ante manipulacion directa del POST).
6. Anular un gasto ya anulado (POST forzado, boton ya oculto en UI) -> `GastoService.AnularAsync` rechaza con "Este gasto ya esta anulado." — CUMPLE.

**Aumento masivo de precios**
7. Caso valido (alcance+valor+target+porcentaje) -> Preview muestra tabla, Confirmar aplica — CUMPLE por codigo.
8. **Porcentaje = 0** -> bloqueado client-side (Swal "Ingrese un porcentaje distinto de cero.") + `ValidarCriterio`/`AplicarAsync` rechazan server-side con "El porcentaje no puede ser cero." — CUMPLE, doble capa, tanto en Preview como en Aplicar.
9. **Sin productos que matcheen el criterio** -> `AplicarCriterio` devuelve `query.Where(p => false)` como fallback si falta el valor del criterio, o el filtro real no matchea ningun producto -> `Preview` responde con `items.Count == 0` -> Controller devuelve error "No se encontraron productos con el criterio seleccionado." — CUMPLE, no se puede llegar a la previsualizacion (y por lo tanto no se puede confirmar) con 0 productos.
10. Alcance sin valor seleccionado (ej. PorMarca sin MarcaId) -> `ValidarCriterio` rechaza server-side con "Seleccione una marca/categoria/modelo." antes de consultar — CUMPLE.
11. Porcentaje fuera de rango (< -99 o > 1000) -> `[Range(-99, 1000)]` en el DTO + revalidacion explicita en `ValidarCriterio` — CUMPLE.
12. Confirmar con `RowVersion` desactualizado (producto modificado entre preview y confirmar) -> `AplicarAsync` rechaza el lote completo, rollback total, mensaje claro — CUMPLE (ver seccion dedicada arriba).
13. Confirmar sin haber previsualizado / tras cambiar el criterio -> boton "Confirmar aumento" no visible (`previewItems`/`criterioUsado` se resetean en `ocultarPreview()`, disparado por cualquier `change` en el formulario) — CUMPLE por UI; un POST directo a `/Aplicar` sin `itemsJson` cae en `items.Count == 0` -> "No hay productos para aplicar. Vuelva a previsualizar." — CUMPLE tambien server-side.

### Evidencia de build y migracion (re-verificado por QA)

- `dotnet build MariHogar.slnx --no-incremental` -> **Compilacion correcta, 0 errores** (9 warnings preexistentes: NU1902 de MailKit/MimeKit x4 + CS0114 de `HomeController.StatusCode`; ninguno nuevo) — re-ejecutado por QA el 2026-07-24, coincide exactamente con lo declarado por el implementador.
- `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` -> `20260724145210_InitialCreate`, `20260724152806_AddCatalogo`, `20260724175804_AddPresupuestosVentas`, `20260724184703_AddEntregas`, `20260724192534_AddComprasCCProveedoresCheques`, `20260724200956_AddGastos` -> **6 migraciones, ninguna marcada pendiente** — coincide con lo declarado por el implementador. Migracion `AddGastos` revisada linea por linea: patron nullable+backfill(`UUID_TO_BIN(UUID())`)+`AlterColumn NOT NULL` para `Producto.RowVersion` (evita el `defaultValueSql` que MySQL rechaza en columnas BLOB), consistente con el aprendizaje documentado por el implementador.

### Defectos activos

**Ninguno bloqueante ni critico.** Un (1) hallazgo menor no bloqueante (ver matriz de formularios, item 5: falta guard server-side explicito de rango de enum para `Categoria`/`FormaPago` de Gasto ante un POST manipulado — no alcanzable desde la UI real, no se aplica auto-fix por no ser reproducible en uso normal ni estar catalogado como patron cross-proyecto).

**Auto-fixes aplicados en este ciclo**: ninguno (no se reprodujo ningun bug funcional real).

### Riesgos de liberacion

- **Medio-bajo, heredado y acumulado** (mismo riesgo señalado en Sprints 2 a 4, sin cerrar todavia): ningun tramo funcional de Sprints 2 a 5 fue ejecutado en un navegador real por nadie (regla de proceso vigente desde el cierre de Sprint 2). Se recomienda que el usuario complete la checklist manual de 7 pasos que dejo el implementador para este sprint (`5-implementador.md`, seccion "Checklist de verificacion manual"), ademas de las 3 checklists acumuladas de Sprints 2-4 (12+11+10 pasos), antes de dar la Etapa 1 completa por 100% cerrada ante el cliente. Ninguna bloquea el cierre tecnico de este sprint.
- **Bajo**: hallazgo menor de la matriz de formularios (guard de enum de Gasto ante POST manipulado, ver "Defectos activos").
- **Bajo, de proceso (no de codigo)**: incidente de integridad del modulo Dashboard durante la sesion del implementador — codigo final verificado seguro y correcto por QA, pero se recomienda investigar la causa raiz del proceso anomalo (ver seccion dedicada arriba) antes de asumir que fue un evento aislado.
- **Bajo**: proyeccion financiera excluye del promedio historico los movimientos del dia en curso (ver nota menor en la seccion de verificacion de formula) — comportamiento razonable, no bloqueante.

### Pruebas minimas ejecutadas

- `dotnet build MariHogar.slnx --no-incremental` -> Compilacion correcta, 0 errores (9 warnings preexistentes, ninguno nuevo) — re-verificado por QA.
- `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` -> 6 migraciones, ninguna pendiente — re-verificado por QA.
- Revision de codigo linea por linea de los 5 servicios nuevos, 5 Controllers, DTOs/ViewModels/Views de los 5 modulos, entidad `Gasto` + enums nuevos, configuracion Fluent de `Producto.RowVersion`, migracion `AddGastos`, `_Layout.cshtml`, `Program.cs`, `DependencyInjection.cs`, `HomeController.cs`.
- **Revision de seguridad reforzada** de los 6 archivos del modulo Dashboard senalados por el incidente de integridad (ver seccion dedicada).
- Grep de patrones riesgosos (`.Contains(` sobre colecciones locales, `text/x-template`, `<datalist>`, llamadas de red externas/`fetch`/`HttpClient` a hosts no propios, credenciales hardcodeadas) sobre los archivos nuevos del sprint.
- Ejecucion completa del playbook cross-proyecto (30 items, incluido REG-001 aplicando por primera vez en este proyecto).

### Estado go/no-go

**GO para habilitar Sprint 6** (AFIP/ARCA — ultimo sprint de Etapa 1). Sin defectos bloqueantes ni criticos: 9/9 HU CUMPLE, generacion de movimiento de Gasto verificada sin duplicar/omitir, preview de Aumento masivo confirmado que no persiste nada + RowVersion confirmado viajando ida y vuelta preview->confirmar con rollback total ante cualquier discrepancia, formula de Proyeccion financiera verificada matematicamente correcta y consistente con CA-N20/21/22, agregacion y comparativo de Caja mensual verificados correctos, separacion Admin/Vendedor del Dashboard confirmada real (policy en los 2 endpoints financieros, no solo oculta en la vista) con independencia de carga de KPIs confirmada por codigo, revision de seguridad reforzada del Dashboard sin hallazgos de contenido malicioso. Unico hallazgo: 1 observacion menor no bloqueante (guard de enum de Gasto ante POST manipulado). Condicion recomendada (no bloqueante para iniciar Sprint 6): que el usuario complete la checklist manual de 7 pasos de este sprint + las 3 checklists acumuladas de Sprints 2-4 antes de dar la Etapa 1 completa por 100% cerrada ante el cliente, y que se investigue la causa raiz del incidente de integridad del Dashboard (hipotesis mas probable: colision de dos ejecuciones paralelas del mismo sprint).

---
## Sprint 4 — M12 Compras a proveedores + M13 CC Proveedores + M14 Cheques 30/60/90

### Alcance validado

Sprint 4: M12 (`Proveedor`/`OrdenCompra`/`OrdenCompraItem`/`PagoOrdenCompra`, maquina de estados Borrador→Confirmada→Recibida/Cancelada), M13 (`MovimientoCCProveedor`, ledger inmutable con saldo por proveedor), M14 (`Cheque` 1-a-1 con `PagoOrdenCompra`, maquina de estados Pendiente→Acreditado/Rechazado, `ChequeAcreditacionHostedService`). Sprints 1-3 (M10/M2/M3, M4/M5/M11, M6 — todos en GO) **no se re-validaron**, solo se tomaron como contexto/base.

**Metodo**: revision de codigo real completa de `OrdenCompraService.cs`, `PagoOrdenCompraService.cs`, `CCProveedorService.cs`, `ChequeService.cs`, `ChequeAcreditacionHostedService.cs`, `ProveedorService.cs` (los 5 servicios nuevos, linea por linea); `OrdenCompraDtos.cs`/`PagoOrdenCompraDtos.cs`/`CCProveedorDtos.cs`/`ChequeDtos.cs`/`ProveedorDtos.cs`; entidades Domain (`Proveedor`, `OrdenCompra`, `OrdenCompraItem`, `PagoOrdenCompra`, `Cheque`, `MovimientoCCProveedor`) y enums (`EstadoOrdenCompra`, `EstadoCheque`, `CuotaCheque`, `TipoMovimientoCCProveedor`, `MetodoPago`); configuracion Fluent de `AppDbContext` (indices/FKs/precision, incluido el indice unico `Cheque.PagoOrdenCompraId` y el indice `FechaVencimiento` usado por el job); Controllers `OrdenesCompraController`/`ProveedoresController`/`ChequesController` completos; Views `OrdenesCompra/{Index,Create,Details}.cshtml`, `Proveedores/{Index,Create,Edit,CuentaCorriente}.cshtml`, `Cheques/Index.cshtml` (scripts completos); `_Layout.cshtml` (sidebar); `DependencyInjection.cs`. `dotnet build MariHogar.slnx` y `dotnet ef migrations list` re-ejecutados por QA contra el repo real. **Verificacion empirica adicional** (no solo lectura de codigo): se construyo un programa C# standalone que instancia `AppDbContext`/`CCProveedorService` reales contra `marihogar_dev` (MySQL real) para reproducir por ejecucion directa el patron de riesgo cross-proyecto MH-001 en el codigo nuevo de este sprint (ver seccion dedicada abajo) — la unica ejecucion "en caliente" de este ciclo, fuera de navegador, permitida por la regla del rol (deteccion tipo `api`/`data`, no UI). No se ejecuto navegador para el resto del alcance (regla de proceso vigente desde el cierre de Sprint 2).

### Verificacion del bug ya corregido por el implementador (MontoPagado vs cheque Rechazado)

El implementador documento en `5-implementador.md` (Sprint 4) que encontro y corrigio, durante su propia revision de codigo previa al cierre, un bug real: `OrdenCompraDetailDto.MontoPagado` y el tope de saldo disponible de `PagoOrdenCompraService.RegistrarPagoAsync` no excluian pagos cuyo cheque asociado ya estaba `Rechazado`, lo que hubiera dejado el sistema mostrando como "cobrado" un dinero que el ledger de CC Proveedor ya habia revertido correctamente al rechazar el cheque.

QA verifico por codigo que el fix esta bien aplicado **en ambos puntos exigidos por la tarea, y busco explicitamente otros lugares del sistema con el mismo problema**:

- `MariHogar.Application/DTOs/OrdenCompraDtos.cs` linea 80: `MontoPagado => Pagos.Where(p => p.Cheque == null || p.Cheque.Estado != "Rechazado").Sum(p => p.Monto)` — correcto.
- `MariHogar.Infrastructure/Services/PagoOrdenCompraService.cs` lineas 71-73: `montoPagadoExistente` se calcula con el mismo filtro (`p.Cheque == null || p.Cheque.Estado != EstadoCheque.Rechazado`) antes de validar el tope de saldo disponible de un pago nuevo — correcto, y coincide exactamente con el criterio del DTO (mismo comentario cruzado en ambos archivos, sin que diverjan).
- **Grep de `MontoPagado`/`SaldoPendiente`/`SaldoDisponible` en toda la solucion**: la unica ocurrencia de un calculo de "monto pagado" derivado de pagos individuales es la de `OrdenCompraDtos.cs` de arriba — no hay una segunda formula paralela sin el filtro.
- **El saldo de CC Proveedor (listado de Proveedores y `CuentaCorriente` por proveedor, `CCProveedorService.ObtenerSaldoActualAsync`/`ObtenerSaldosAsync`) NO tiene el mismo problema y no necesitaba el mismo fix**: ese saldo se calcula como `Σ Cargo − Σ Pago` sobre el ledger real `MovimientoCCProveedor`, y `ChequeService.RechazarAsync` ya postea un contramovimiento `Cargo` (`EsReversion=true`) por el mismo importe del `Pago` original al rechazar un cheque — el ledger ya queda matematicamente correcto sin necesitar excluir nada por calculo derivado. Confirmado por lectura de `ChequeService.RechazarAsync` (linea 143) y `CCProveedorService.ObtenerSaldoActualAsync` (linea 22-31): no hay ningun punto adicional del sistema con el mismo bug potencial.

**Conclusion: el fix esta completo y no quedo ningun otro punto del sistema con el mismo problema sin corregir.**

### Cobertura de historias de usuario (HU-12.1 a HU-12.4, HU-13.1, HU-14.1 a HU-14.4)

| HU | Criterio (resumen) | Resultado | Evidencia |
|---|---|---|---|
| HU-12.1 | OC con multiples lineas, Borrador editable libremente, al menos 1 linea para Confirmar | CUMPLE | `OrdenCompraService.CreateAsync`/`UpdateAsync` (reemplazo completo de Items, patron `PresupuestoService`); `ConfirmarAsync` rechaza con `oc.Items.Count == 0` -> "Agregue al menos una linea antes de confirmar." |
| HU-12.2 | Confirmar bloquea edicion de lineas; Recibir incrementa stock de cada linea en una transaccion | CUMPLE | `EstadosEditables = [Borrador]` bloquea `UpdateAsync` fuera de Borrador; `RecibirAsync` (ver seccion dedicada abajo) |
| HU-12.3 | Pago en efectivo/transferencia/cheque/deposito; cheque abre sub-formulario; impacta CC proveedor; combina metodos | CUMPLE | `PagoOrdenCompraService.RegistrarPagoAsync`: `MetodosPermitidosOC = [Efectivo, Transferencia, Cheque, Deposito]`; campos de cheque obligatorios solo si `Metodo=Cheque`; multiples lineas por pago (`List<PagoOrdenCompraLineaInput>`); cada linea postea su propio `MovimientoCCProveedor` |
| HU-12.4 | Cancelar solo desde Borrador/Confirmada; Recibida bloqueada | CUMPLE | `EstadosCancelables = [Borrador, Confirmada]`, guard explicito (nunca `!=` generico) — ver maquina de estados abajo (VSF-002-safe) |
| HU-13.1 | Saldo por proveedor + historial de movimientos; filtro por proveedor y fecha; se actualiza con cada pago | CUMPLE | `CCProveedorService.ObtenerSaldoActualAsync`/`ObtenerSaldosAsync` (agrupado, sin N+1); `ListarMovimientosAsync` con filtro de rango de fecha persistido en sesion por proveedor (`Filtros:Proveedores:CuentaCorriente:{id}`) |
| HU-14.1 | Cheque con monto, vencimiento y cuota 30/60/90 | CUMPLE | `Cheque` entity + `CuotaCheque` enum (valor=dias); `PagoOrdenCompraService` exige los 4 campos si `Metodo=Cheque` |
| HU-14.2 | Cheques venciendo en <=30 dias visibles en dashboard | PARCIAL / preparado sin consumidor | `ChequeListItemDto.VenceProximo` ya calculado (<=7 dias, no 30 — ver observacion abajo) y usado para resaltar filas en `Cheques/Index`; el dashboard (M9) es de un sprint futuro, no existe todavia — consistente con el alcance de este sprint |
| HU-14.3 | ~~Acreditacion automatica al vencer (job diario)~~ **superado por CR-7 (Sprint CR-A, 27/07/2026)**: el job pasa a solo notificar, la acreditacion queda exclusivamente manual — idempotente, notificacion in-app | CUMPLE (criterio vigente reemplazado, ver Sprint CR-A) | Ver seccion dedicada de idempotencia abajo. Correccion de auditoria 15/08/2026: esta fila describia el comportamiento correcto para Sprint 4, pero quedo desactualizada respecto del sistema real desde CR-7. |
| HU-14.4 | Rechazo manual con motivo; reabre la deuda | CUMPLE | `ChequeService.RechazarAsync`: motivo obligatorio, guard `Estado != Pendiente`, contramovimiento `Cargo` con `EsReversion=true` |

**Cobertura: 8/9 HU CUMPLE, 1 PARCIAL de alcance (HU-14.2 — el dato "vence proximo" ya existe en el DTO/vista de Cheques con umbral de 7 dias, pero el criterio literal de CA-N11 pide 30 dias y pide que aparezca en el Dashboard, que es M9 y no existe todavia en este sprint; no es un defecto de este sprint, es preparacion correcta para uno futuro).**

**Observacion (no bloqueante)**: el umbral de "vence proximo" usado para resaltar filas en `Cheques/Index.cshtml` (`(FechaVencimiento - hoy).TotalDays <= 7`) es mas estricto que el de CA-N11 (30 dias) porque hoy solo se usa para resaltado visual del propio listado de Cheques, no para el widget de dashboard de M9 (que todavia no existe). Cuando se implemente el Dashboard (M9, sprint futuro) hay que usar 30 dias para ese widget especifico, no necesariamente cambiar el resaltado de 7 dias de `Cheques/Index` (son dos usos distintos, con distinta urgencia visual). Se documenta para que el implementador de M9 no asuma que el `VenceProximo` ya calculado sirve tal cual.

### Maquina de estados — Orden de compra (recorrido completo, transiciones validas e invalidas)

| Origen | Evento | Destino | Guard verificado | Resultado |
|---|---|---|---|---|
| — | Crear | Borrador | Ninguno (0 items permitido, igual criterio que Presupuesto/Venta) | PASS |
| Borrador | Confirmar (con >=1 linea) | Confirmada | `oc.Items.Count > 0` | PASS |
| Borrador | Confirmar (0 lineas) | rechazado | idem | PASS — "Agregue al menos una linea antes de confirmar." |
| Confirmada | Confirmar de nuevo | rechazado | `oc.Estado != Borrador` | PASS — "Solo se puede confirmar una orden de compra en Borrador (actual: Confirmada)." |
| Confirmada | Recibir | Recibida | `oc.Estado == Confirmada` | PASS, incrementa stock + postea Cargo (ver seccion dedicada) |
| Borrador | Recibir (saltando Confirmar) | rechazado | idem | PASS — "Solo se puede recibir una orden de compra Confirmada (actual: Borrador)." |
| Recibida | Recibir de nuevo | rechazado | idem | PASS — no duplica stock ni Cargo |
| Borrador | Cancelar (motivo) | Cancelada | `EstadosCancelables.Contains(Borrador)` | PASS |
| Confirmada | Cancelar (motivo) | Cancelada | `EstadosCancelables.Contains(Confirmada)` | PASS — sin Cargo que revertir (no se posteo todavia) |
| Recibida | Cancelar | rechazado | `!EstadosCancelables.Contains(Recibida)` | PASS — "La orden de compra ya fue recibida (impacto stock y cuenta corriente), no se puede cancelar." (mensaje diferenciado, nunca `!=` generico — VSF-002-safe) |
| Cancelada | Cancelar de nuevo | rechazado | idem | PASS — "La orden de compra ya esta cancelada." |
| Cualquiera | Cancelar sin motivo | rechazado | `string.IsNullOrWhiteSpace(motivo)` | PASS — "El motivo de cancelacion es obligatorio." |
| Borrador | Editar items | permitido | `EstadosEditables.Contains(Borrador)` | PASS |
| Confirmada/Recibida/Cancelada | Editar items | rechazado | idem | PASS — "Solo se puede editar una orden de compra en Borrador (actual: X)." |

**Cobertura: 14/14 transiciones (validas e invalidas) verificadas por codigo, todas con el resultado esperado.** Consistente con la tabla de `2-disenador-funcional.md`. Confirmado explicitamente que **Borrador→Cancelada existe desde el primer commit** (a diferencia del bug real ya catalogado como `VSF-002` en vinosefue, donde esa transicion faltaba en el diccionario) — el implementador documento haberlo evitado a proposito y QA lo confirma por lectura directa de `OrdenCompraService.EstadosCancelables`.

### Maquina de estados — Cheque (recorrido completo, transiciones validas e invalidas)

| Origen | Evento | Destino | Guard verificado | Resultado |
|---|---|---|---|---|
| — | Registrar como pago de OC (Metodo=Cheque) | Pendiente | Campos completos (numero/banco/vencimiento/cuota) + vencimiento >= hoy | PASS |
| — | Registrar cheque con vencimiento anterior a hoy | rechazado | `FechaVencimientoCheque.Value.Date < DateTime.Today` | PASS — "La fecha de vencimiento del cheque no puede ser anterior a hoy." |
| — | Registrar cheque con campos incompletos | rechazado | `IsNullOrWhiteSpace`/`!HasValue` sobre numero/banco/vencimiento/cuota | PASS — "Complete numero, banco, fecha de vencimiento y cuota para el pago con cheque." |
| Pendiente | Job diario, vencimiento <= hoy | Acreditado | `Estado == Pendiente && FechaVencimiento <= fecha` | PASS, `FechaAcreditacion` seteada + notificacion in-app |
| Pendiente | Job diario, vencimiento futuro | sin cambio | idem (no matchea el filtro) | PASS — el cheque sigue Pendiente |
| Acreditado | Job diario corre de nuevo (mismo dia u otro) | sin cambio | `Estado == Pendiente` ya no matchea | PASS — idempotente, ver seccion dedicada |
| Pendiente | Administrador rechaza (motivo) | Rechazado | `Estado == Pendiente` | PASS, contramovimiento `Cargo` de reversion |
| Pendiente | Rechazar sin motivo | rechazado (el rechazo en si, no el estado del cheque) | `IsNullOrWhiteSpace(motivo)` | PASS — "El motivo del rechazo es obligatorio." |
| Acreditado | Rechazar | rechazado | `cheque.Estado != Pendiente` | PASS — "Solo se puede rechazar un cheque Pendiente (actual: Acreditado)." |
| Rechazado | Rechazar de nuevo | rechazado | idem | PASS — "Solo se puede rechazar un cheque Pendiente (actual: Rechazado)." |
| Rechazado / Acreditado | Job diario | sin cambio | `Estado == Pendiente` no matchea ninguno de los dos | PASS — ambos son terminales, ningun cheque "revive" a Pendiente |

**Cobertura: 11/11 transiciones (validas e invalidas) verificadas por codigo, todas con el resultado esperado.** Consistente con la tabla de `2-disenador-funcional.md` (Pendiente -> Acreditado automatico / Rechazado manual, ambos terminales).

### Verificacion puntual — transaccion de "Recibida" (incremento de stock por linea)

Confirmado por lectura de `OrdenCompraService.RecibirAsync` (lineas 196-230): guard `Estado != Confirmada` antes de abrir transaccion -> `BeginTransactionAsync()` -> `Estado=Recibida`+`FechaRecepcion` -> `foreach (var item in oc.Items) await _stockService.RegistrarMovimientoAsync(item.ProductoId, TipoMovimientoStock.Compra, item.Cantidad, oc.Id, usuarioId, ...)` (un incremento por cada linea de `oc.Items`, sin filtro que pueda saltear ninguna ni duplicar — la coleccion viene de `Include(o => o.Items)` sobre la OC real, sin paginacion ni `Distinct` que pudiera alterar el conteo) -> `_ccProveedorService.RegistrarMovimientoAsync(..., Cargo, oc.Total, ...)` (una sola vez, por el total de la OC, no por linea) -> **un unico** `SaveChangesAsync()` que persiste el cambio de estado de la OC + todos los `MovimientoStock` + el `MovimientoCCProveedor` juntos -> `CommitAsync()`; `catch` con `RollbackAsync()`. Confirmado que `IStockService.RegistrarMovimientoAsync` (mismo servicio de Sprint 1/M3) no abre transaccion ni hace `SaveChanges` propio (comentario explicito en `StockService.cs` linea 120-121), por lo que el caller (`OrdenCompraService`) controla la unica transaccion real, igual patron que `VentaService.ConfirmarAsync` (Sprint 2). **Sin duplicacion ni omision de lineas: se itera exactamente `oc.Items.Count` veces, una vez cada una.**

### Verificacion puntual — transaccion de registro de pago (MovimientoCCProveedor + Cheque)

Confirmado por lectura de `PagoOrdenCompraService.RegistrarPagoAsync` (lineas 39-130): validaciones de negocio (monto>0 via guard GAN-001-safe, metodo permitido, campos de cheque completos, vencimiento no pasado, tope de saldo disponible ya excluyendo cheques Rechazados) **antes** de abrir la transaccion -> `BeginTransactionAsync()` -> por cada linea de pago: `Add(PagoOrdenCompra)` + `SaveChangesAsync()` intermedio (asigna `pago.Id`, usado como FK de `Cheque` y `OrigenId` del movimiento de CC) -> si `Metodo == Cheque`, `Add(Cheque{Estado=Pendiente, PagoOrdenCompraId=pago.Id})` -> `_ccProveedorService.RegistrarMovimientoAsync(..., Pago, linea.Monto, "PagoOC", pago.Id, ...)` (sin `SaveChanges` propio) -> tras el loop, `SaveChangesAsync()` final + `CommitAsync()`; `catch` con `RollbackAsync()`. Confirmado que los `SaveChangesAsync()` intermedios del loop pertenecen a la misma transaccion externa (estan dentro del `await using var tx = ...BeginTransactionAsync()`), asi que un fallo en la linea 2 de un pago de 3 lineas revierte tambien la linea 1 ya "guardada" — atomicidad real de punta a punta, no solo por linea. El vinculo `PagoOrdenCompra`<->`Cheque` es 1-a-1 (indice unico `Cheque.PagoOrdenCompraId`, confirmado en `AppDbContext`), coherente con que cada linea de pago con `Metodo=Cheque` genera exactamente un `Cheque`.

### Verificacion puntual — idempotencia de `ChequeAcreditacionHostedService`

Confirmado por analisis estatico (simulacion mental de doble corrida, mismo dia): la garantia real de idempotencia es el filtro `Where(c => c.Estado == EstadoCheque.Pendiente && c.FechaVencimiento <= fecha)` dentro de `ChequeService.AcreditarVencidosAsync`, **no** el campo en memoria `_ultimaFechaProcesada` del hosted service (que solo evita una consulta redundante, documentado explicitamente asi en el XML-doc de la clase). 1ra corrida: encuentra N cheques Pendientes vencidos, los pasa a Acreditado, notifica una vez. 2da corrida (mismo tick del timer, o tras un reinicio que resetee `_ultimaFechaProcesada` a `null`): la misma query ya no encuentra esos N cheques (ya son `Acreditado`, no matchean `Estado == Pendiente`) -> `vencidos.Count == 0` -> `return []` sin tocar la base -> el guard `if (acreditados.Count > 0)` evita llamar a `NotificarAdministradoresAsync` -> **cero re-acreditacion, cero notificacion duplicada**. No hay condicion de carrera obvia dentro de una sola instancia (el `PeriodicTimer` de 1 minuto invoca `EjecutarSiCorrespondeAsync` de forma secuencial, nunca en paralelo consigo mismo). El unico escenario no cubierto (documentado por el implementador como riesgo bajo, no mitigado por directriz de cambios minimos) es **multiples instancias del proceso corriendo simultaneamente** — no aplica al hosting actual (SMARTEASP, instancia unica, mismo precedente que ganaderia).

### Verificacion puntual — "Rechazar cheque" revierte con contramovimiento (nunca borra el original)

Confirmado por lectura de `ChequeService.RechazarAsync` (lineas 117-156): guard motivo obligatorio -> guard `Estado != Pendiente` -> `cheque.Estado=Rechazado`+`FechaRechazo`+`MotivoRechazo` -> `_ccProveedorService.RegistrarMovimientoAsync(oc.ProveedorId, Cargo, cheque.PagoOrdenCompra.Monto, "PagoOC", cheque.PagoOrdenCompraId, esReversion:true, ...)` — un **nuevo** `MovimientoCCProveedor` con `EsReversion=true`, mismo `OrigenId` que el `Pago` original (nunca se hace `Update`/`Remove` sobre el movimiento `Pago` original, confirmado por grep de operaciones sobre `MovimientoCCProveedor` en todo `ChequeService.cs`: la unica es este `Add` via el Service dedicado). Aritmetica confirmada correcta: `SaldoActual = Σ Cargo − Σ Pago`; el `Cargo` de reversion neutraliza exactamente el `Pago` que ese cheque representaba, reabriendo la deuda del proveedor por el mismo importe. **Sin defecto.**

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

| id | aplica | resultado | accion |
|---|---|---|---|
| REG-001 | no | N/A — sin `RowVersion`/concurrency tokens en las entidades nuevas | ninguna |
| REG-002 | no | N/A — no relacionado a stock inicial de producto | ninguna |
| REG-003 | si (buscador `BuscarParaCompra` en OC/Create) | PASS — `processResults` mapea campos reales (`id`,`nombre`,`marcaNombre`,`precioCompra`,`fotoUrl`,`stockActual`), sin el bug de campo inexistente del original | ninguna |
| REG-004 (foco explicito, botones por estado) | si (Details de OC — Confirmar/Recibir/Cancelar) | PASS — cada boton esta dentro de `@if (o.EstadoReal == ...)` contra el enum real, nunca hardcodeado; ver maquina de estados arriba. Observacion menor: el boton "Confirmar orden de compra" se muestra para cualquier OC en Borrador sin ocultarse si `Items.Count==0` (a diferencia de otros ABMs del sistema) — no es un defecto funcional porque el servidor igual lo bloquea con el mensaje correcto, pero es una oportunidad de pulido UX menor, no bloqueante | ninguna (observacion, no bug) |
| REG-005 | no | N/A — mismo Select2 remoto que REG-003, ya cubierto | ninguna |
| REG-006 (campos condicionales por metodo de pago) | si (sub-formulario de pago de OC) | PASS — campos de cheque (numero/banco/vencimiento/cuota) solo se muestran/exigen cuando `Metodo=Cheque`, tanto client-side (`renderPagosOC`) como server-side (`RegistrarPagoAsync`) | ninguna |
| REG-007 | no | N/A — modulo Devoluciones no existe | ninguna |
| REG-008 (grilla de pagos de OC) | si | PASS — el listener `input` sobre `.inp-monto-oc`/campos de cheque solo actualiza el array en memoria + `actualizarIndicadorOC()`, nunca reconstruye `#listaPagosOC` en cada tecla (`renderPagosOC()` solo se llama en agregar/quitar/cambiar metodo) — no se pierde el foco | ninguna |
| REG-009 | no | N/A — sin combos en cascada en OC/Proveedores/Cheques | ninguna |
| REG-010 | si (sidebar "Compras"/"Cheques") | PASS — visible solo para SuperUsuario/Administrador en `_Layout.cshtml`, coincide exactamente con `[Authorize(Policy="RequireAdministracion")]` de `OrdenesCompraController`/`ProveedoresController`/`ChequesController` | ninguna |
| KOI-001 | no (patron distinto) | N/A — Confirmar/Recibir de OC usan `.btn-swal-confirm`+`data-form` (ya soportado por `site.js` desde el fix historico); Cancelar OC y Rechazar cheque arman su propio `<form>` dinamico (igual patron que `Categorias/Index.cshtml`, no el handler generico) — ninguno de los dos reproduce el bug original | ninguna |
| KOI-002/003/004 | no | N/A — modulos no existen | ninguna |
| KOI-005/006 (sidebar -> controller inexistente) | si | PASS — `OrdenesCompra`/`Proveedores`/`Cheques` referenciados en `_Layout.cshtml` tienen sus 3 controllers reales, confirmados por listado de archivos | ninguna |
| DN-001/DN-002 | no | N/A — stack `MySql.EntityFrameworkCore` 10.0.1 (provider oficial Oracle), no EF6; ademas ningun Service de este sprint combina `Include` de coleccion + orden/filtro dinamico + `Skip/Take` en el mismo `IQueryable` (verificado en `OrdenCompraService.ListarAsync`, `ChequeService.ListarAsync`, `ProveedorService.ListarAsync`: los `Include` son navegaciones simples, nunca colecciones, y el orden/filtro dinamico se aplica sobre la query base antes de cualquier `Include` de coleccion) | ninguna |
| **GAN-001** (guard "al menos un pago real") | si (`PagoOrdenCompraService.RegistrarPagoAsync`) | PASS — `lineasValidas = input.Pagos.Where(p => p.Monto > 0).ToList()`, rechaza con `Count == 0` -> "Cargue al menos una forma de pago."; los pagos viajan por JSON armado en JS (`pagosJson`), no por binding indexado de formulario, fuera del mecanismo estructural que originaba GAN-001 en ganaderia | ninguna |
| GAN-002 | no | N/A — sin backfill de datos historicos en este sprint (migracion `AddComprasCCProveedoresCheques` es esquema puro, sin script de datos) | ninguna |
| GAN-003 | no | N/A — grep de `text/x-template` sobre `Views/OrdenesCompra`, `Views/Proveedores`, `Views/Cheques` sin resultados | ninguna |
| GAN-004 | no | N/A — sin `<datalist>` en este sprint (combos usan Select2 o `<select>` server-side) | ninguna |
| **VSF-001** (backfill que no filtra por estado terminal de la entidad relacionada) | no | N/A — este sprint no tiene ningun script de backfill de datos historicos (la migracion es esquema puro); el escenario original de VSF-001 (vinculo remanente de un backfill sin filtrar por `Estado` de la entidad relacionada) no tiene equivalente porque no hay backfill que ejecutar. Verificado ademas que ningun guard de este sprint usa un `!=` generico contra un solo estado bloqueante sin considerar el resto del enum (mismo criterio de guard explicito que evito VSF-002, ver abajo) | ninguna |
| **VSF-002** (Borrador sin transicion a Cancelada en el diccionario de transiciones) | si (maquina de estados de OrdenCompra, mismo origen de reutilizacion — `CompraProveedorService` de vinosefue) | **PASS — confirmado evitado.** `OrdenCompraService.EstadosCancelables = [Borrador, Confirmada]` incluye `Borrador` desde el primer commit (verificado por lectura directa del codigo, no solo por lo declarado en `5-implementador.md`); el boton "Cancelar orden de compra" en `Details.cshtml` esta disponible para Borrador y Confirmada por igual. Contrastado ademas contra la tabla de maquina de estados aprobada en `2-disenador-funcional.md` ("Borrador / Confirmada, Cancelar -> Cancelada, Estado != Recibida") — coincide exactamente | ninguna |
| CRM-001 a 006 | no | N/A — modulo Bot/CRM no existe | ninguna |
| MH-001 (IN de coleccion local no soportado por el provider) | si (`CCProveedorService.ObtenerSaldosAsync`) | **PASS, verificado empiricamente (no solo por codigo)** — ver seccion dedicada abajo | ninguna |
| MH-002 (enum serializado como int) | no (no aplica a DTOs nuevos) | N/A — `OrdenCompraListItemDto.Estado`, `OrdenCompraDetailDto.Estado`, `ChequeListItemDto.Estado`, `MovimientoCCProveedorListItemDto.Tipo`, `PagoOrdenCompraDto.Metodo` ya se mapean con `.ToString()` desde el Service correspondiente, mismo patron correcto que evito MH-002 en Sprint 1 | ninguna |

### Verificacion empirica de MH-001 en codigo nuevo — hallazgo relevante (no bug, refinamiento del catalogo)

Al hacer el grep sistematico de `.Contains(` sobre `MariHogar.Infrastructure/Services/*.cs` (obligacion de trazabilidad cross-proyecto), QA encontro una nueva ocurrencia del patron generico de MH-001 en `CCProveedorService.ObtenerSaldosAsync` (linea 43): `_db.MovimientosCCProveedor.AsNoTracking().Where(m => ids.Contains(m.ProveedorId))`, con `ids` como `HashSet<int>` **local**, aplicado directamente sobre un `IQueryable` (no sobre una lista ya materializada) — a primera vista, el mismo patron exacto que causo el 500 de Sprint 1. Este metodo es consumido por `ProveedorService.ListarAsync` para la columna "Saldo" del listado de `Proveedores/Index`, una pantalla de uso frecuente.

En vez de asumir que reproduce el bug (o asumir que no, solo por el tipo), QA lo verifico por **ejecucion real**: se armo un programa C# standalone (fuera del proyecto, en el directorio de trabajo temporal de QA) que instancia `AppDbContext` y `CCProveedorService` reales, contra `marihogar_dev` (MySQL real) usando el mismo provider que usa el proyecto (`MySql.EntityFrameworkCore` 10.0.1, **no Pomelo** — dato relevante porque el catalogo original de MH-001 no especificaba el provider exacto), y llamo a `ObtenerSaldosAsync(new[] {1,2,3})` tal cual lo hace `ProveedorService.ListarAsync`. Resultado: **ejecuto sin error**. Como control, en el mismo experimento se reprodujo el patron *original* exacto de MH-001 (`HashSet<string>` local contra `_db.Users.Where(u => usuarioIds.Contains(u.Id))`) contra la misma base y el mismo provider — **ese si lanzo la misma `InvalidOperationException: Expression '@usuarioIds' in the SQL tree does not have a type mapping assigned`** que documenta el catalogo.

**Conclusion**: el riesgo real de MH-001 es especifico de colecciones locales de tipo `string` (probablemente por ambiguedad de charset/collation al parametrizar el arreglo en este provider), no de colecciones de tipos primitivos como `int` con type mapping trivial y sin ambiguedad. `CCProveedorService.ObtenerSaldosAsync` se confirma **PASS**, sin necesidad de auto-fix. Se actualizo el item `MH-001` en `docs/qa/regresiones-manuales.yml` (campo `nota_qa_sprint4`) con este hallazgo para que futuros ciclos de QA no traten como bloqueante cada `.Contains()` sobre coleccion local de tipo primitivo, y mantengan el foco de revision en colecciones de `string` (ids de Identity, codigos, etc.).

### Matriz de formularios (pedido "100% OK") — Sprint 4

Verificados por codigo (server-side siempre revalida). [MANUAL] = requiere navegador real, incluido en la checklist de 10 pasos que dejo el implementador en `5-implementador.md`.

**Alta de Orden de compra (`OrdenesCompra/Create`)**
1. Sin proveedor seleccionado -> PASS — `input.ProveedorId <= 0` rechazado server-side con "Seleccione un proveedor." (guardar como Borrador no exige items, igual criterio que Presupuesto).
2. Guardar Borrador sin items -> PASS — permitido por diseño (HU-12.1: "Borrador editable libremente"), consistente con `2-disenador-funcional.md` ("Crear -> Borrador, Al menos 0 items").
3. **Confirmar una OC en Borrador sin items -> PASS (bloqueado)** — `ConfirmarAsync` rechaza con "Agregue al menos una linea antes de confirmar."; ver observacion de REG-004 arriba sobre que el boton no se oculta preventivamente (cosmetico, no funcional).
4. Producto eliminado entre la busqueda y el guardado -> PASS — `AplicarItemsAsync` revalida `productoExiste` por Id antes de agregar la linea, la descarta silenciosamente si no existe (mismo criterio que `PresupuestoService.ValidarProductosAsync`).
5. [MANUAL] Confirmar visualmente que el buscador `BuscarParaCompra` muestra precio de **compra** (no de venta) y que el Administrador ve ese dato (paso 2 de la checklist).

**Pago de OC (sub-formulario, `OrdenesCompra/Details`)**
6. Sin ninguna forma de pago -> PASS — deshabilitado client-side (`hayPagoReal`) y server rechaza (`lineasValidas.Count == 0`, "Cargue al menos una forma de pago.") — GAN-001-safe.
7. Metodo Cheque con campos incompletos -> PASS — SweetAlert2 client-side ("Datos de cheque incompletos") + server rechaza con el mismo mensaje si se fuerza el POST.
8. Metodo Cheque con vencimiento anterior a hoy -> PASS — `<input type="date" min="hoy">` client-side + `FechaVencimientoCheque.Value.Date < DateTime.Today` server-side, "La fecha de vencimiento del cheque no puede ser anterior a hoy."
9. Monto que supera el saldo pendiente -> PASS — boton deshabilitado client-side (`suma > saldoPendiente`) + server rechaza (`sumaNueva > saldoDisponible`, mensaje con montos exactos) — el calculo de `saldoDisponible` ya excluye cheques Rechazados (ver seccion del bug corregido).
10. Metodo no permitido para OC (payload manipulado, ej. MercadoPago=3) -> PASS — `MetodosPermitidosOC.Contains` rechaza con "Forma de pago no valida para una orden de compra (solo Efectivo, Transferencia, Cheque o Deposito)."
11. Pago sobre OC en Borrador o Cancelada (POST forzado) -> PASS — `EstadosPagables = [Confirmada, Recibida]`, rechaza con "No se puede registrar un pago sobre una orden de compra en estado X."
12. [MANUAL] Confirmar visualmente el pago combinado Efectivo+Cheque y que el saldo pendiente se actualiza tras recargar (paso 4 de la checklist).

**Rechazo de cheque (`Cheques/Rechazar`)**
13. Motivo vacio -> PASS — `inputValidator` de SweetAlert2 client-side ("El motivo es obligatorio.") + `string.IsNullOrWhiteSpace(input.Motivo)` server-side, mismo mensaje.
14. Rechazar un cheque no Pendiente (POST forzado) -> PASS — rechazado con "Solo se puede rechazar un cheque Pendiente (actual: X)."
15. [MANUAL] Confirmar visualmente que tras rechazar, el badge pasa a rojo "Rechazado" y que en `Proveedores/{id}/CuentaCorriente` aparece el nuevo movimiento "Cargo" con badge de reversion (paso 6 de la checklist).

**Alta de Proveedor (`Proveedores/Create`)**
16. RazonSocial vacia -> PASS — `[Required]` + `Validar()` server-side, "La razon social es obligatoria."
17. Eliminar proveedor con OC asociadas -> PASS — bloqueado con "No se puede eliminar: hay ordenes de compra asociadas a este proveedor."

### Evidencia de build y migracion (re-verificado por QA)

- `dotnet build MariHogar.slnx` -> **Compilacion correcta, 0 errores** (9 warnings preexistentes: NU1902 de MailKit/MimeKit x4 + CS0114 de `HomeController.StatusCode`; ninguno nuevo) — re-ejecutado por QA el 2026-07-24, coincide exactamente con lo declarado por el implementador.
- `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` -> `20260724145210_InitialCreate`, `20260724152806_AddCatalogo`, `20260724175804_AddPresupuestosVentas`, `20260724184703_AddEntregas`, `20260724192534_AddComprasCCProveedoresCheques` -> **5 migraciones, ninguna marcada pendiente** — coincide con lo declarado por el implementador.
- Programa standalone de verificacion empirica (ver seccion MH-001 arriba), ejecutado contra `marihogar_dev` real: confirma que la unica consulta nueva de riesgo (`CCProveedorService.ObtenerSaldosAsync`) ejecuta sin error.

### Defectos activos

**Ninguno bloqueante ni critico.** El unico bug funcional real de este sprint (`MontoPagado`/tope de saldo no excluia cheques Rechazados) ya estaba corregido por el implementador antes de que QA lo viera — QA lo re-verifico por codigo (ver seccion dedicada) y confirmo que el fix es completo, sin necesidad de aplicar ningun parche nuevo.

Observaciones (no bloqueantes, no requieren auto-fix):
- El boton "Confirmar orden de compra" en `Details.cshtml` no se oculta preventivamente cuando la OC tiene 0 items (a diferencia de otros ABMs del sistema que sí ocultan/deshabilitan acciones invalidas por adelantado) — el servidor bloquea igual con el mensaje correcto, es una oportunidad de pulido UX menor.
- `ChequeListItemDto.VenceProximo` usa un umbral de 7 dias (para el resaltado del propio listado de Cheques), distinto del umbral de 30 dias que pide CA-N11 para el widget del Dashboard (M9, sprint futuro) — documentado para que no se asuma reutilizable tal cual.
- Riesgo bajo de concurrencia no mitigado en `ChequeAcreditacionHostedService` si el hosting escalara a mas de una instancia — no aplica al hosting actual (SMARTEASP, instancia unica), mismo argumento ya aceptado en sprints anteriores.

**Auto-fixes aplicados por QA en este ciclo**: ninguno sobre codigo de producto (el unico bug real ya estaba corregido). Se actualizo `docs/qa/regresiones-manuales.yml` en dos puntos, ambos de trazabilidad/catalogo, no de codigo: (1) campo `nota_qa_sprint4` agregado al item `MH-001` con el hallazgo empirico de que el patron es especifico de colecciones `string`, no `int` (ver seccion dedicada); (2) ningun item nuevo creado porque no se reprodujo ningun bug no catalogado.

### Riesgos de liberacion

- **Medio-bajo, heredado y acumulado (mismo riesgo senalado en Sprints 2/3, sin cerrar todavia)**: ningun tramo funcional de Sprints 2, 3 ni 4 fue ejecutado en un navegador real por nadie (regla de proceso vigente desde el cierre de Sprint 2). Mitigado parcialmente en Sprint 4 por la verificacion empirica puntual de MH-001 (la unica ejecucion real de este ciclo). **Se recomienda que el usuario complete las 3 checklists manuales acumuladas** (12 pasos de Sprint 2, 11 pasos de Sprint 3, 10 pasos de Sprint 4) antes de considerar los sprints 2 a 4 100% cerrados ante el cliente — ninguna de las tres bloquea el inicio de Sprint 5, dado que el riesgo tecnico por revision de codigo es bajo en los tres casos.
- **Bajo**: HU-14.2 (cheques por vencer en dashboard) queda PARCIAL de alcance — el dato esta preparado (`VenceProximo`) pero el consumidor (Dashboard, M9) no existe todavia; no es un defecto de este sprint.
- **Bajo**: umbral de "vence proximo" (7 dias) usado hoy solo para el resaltado de `Cheques/Index`, distinto del umbral de 30 dias de CA-N11 para el futuro widget de Dashboard — documentado para evitar confusion en M9.
- **Bajo, heredado**: concurrencia de multiples instancias en `ChequeAcreditacionHostedService` — no aplica al hosting actual (instancia unica).
- **Bajo, heredado**: `EstadoOrdenCompra` sin recepcion parcial (P3-A, exclusion ya documentada en analisis funcional, no un desvio de este sprint).

### Pruebas minimas ejecutadas

- `dotnet build MariHogar.slnx` -> Compilacion correcta, 0 errores (9 warnings preexistentes, ninguno nuevo) — re-verificado por QA.
- `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` -> 5 migraciones, ninguna pendiente — re-verificado por QA.
- Revision de codigo linea por linea de los 5 servicios nuevos (`OrdenCompraService`, `PagoOrdenCompraService`, `CCProveedorService`, `ChequeService`, `ProveedorService`), `ChequeAcreditacionHostedService`, 3 Controllers nuevos, DTOs/ViewModels de los 3 modulos, entidades Domain + enums nuevos, configuracion Fluent de `AppDbContext`, `_Layout.cshtml`, `DependencyInjection.cs`.
- **Verificacion empirica adicional** (programa C# standalone contra `marihogar_dev` real): confirmo que `CCProveedorService.ObtenerSaldosAsync` no reproduce MH-001 (PASS) y que el patron original de MH-001 (`HashSet<string>` contra `_db.Users`) si sigue siendo reproducible con el provider real del proyecto (control positivo, valida la metodologia de verificacion).
- Grep de patrones riesgosos (`.Contains(` sobre colecciones locales, `MontoPagado`/`SaldoPendiente`/`SaldoDisponible`, `text/x-template`, `<datalist>`, `Rechazado`) sobre `MariHogar.Infrastructure/Services` y `MariHogar.Web/Views` de este sprint.
- Ejecucion completa del playbook cross-proyecto (30 items del catalogo, incluidos MH-001/MH-002/VSF-001/VSF-002) mapeado a Compras/CC Proveedores/Cheques.
- Recorrido completo de las 14 transiciones (validas e invalidas) de la maquina de estados de Orden de compra y las 11 de Cheque.

### Estado go/no-go

**GO para habilitar Sprint 5** (Gastos M18 + Caja M15 + Proyeccion M17 + Dashboard M9 + Aumento masivo M16). Sin defectos bloqueantes ni criticos detectados: 8/9 HU CUMPLE + 1 PARCIAL de alcance (no defecto), 14/14 transiciones de OC + 11/11 de Cheque verificadas, transaccion de "Recibida" confirmada sin duplicar/omitir lineas, transaccion de pago confirmada atomica (PagoOrdenCompra+Cheque+MovimientoCCProveedor), idempotencia del job de acreditacion confirmada por analisis estatico, reversion de cheque rechazado confirmada con contramovimiento (nunca borra el original), el unico bug real del sprint (MontoPagado vs cheque Rechazado) confirmado bien corregido y sin otros puntos del sistema con el mismo problema, VSF-002 confirmado evitado, VSF-001 no aplica (sin backfill), MH-001 verificado empiricamente como PASS (con refinamiento util del catalogo para futuros sprints). Condicion recomendada (no bloqueante para iniciar Sprint 5, pero si antes de dar Sprints 2-4 por 100% cerrados ante el cliente): que el usuario complete las 3 checklists manuales acumuladas (Sprint 2: 12 pasos: Sprint 3: 11 pasos; Sprint 4: 10 pasos, con atencion especial al paso 8 de acreditacion automatica que requiere esperar la hora de corrida o ajustar temporalmente la constante en un entorno de prueba).

---
## Sprint 3 — M6 Entregas a domicilio

### Alcance validado

Sprint 3: M6 (`Entrega`/`EntregaIntento`, enum `EstadoEntrega`, maquina de estados completa Pendiente→EnCamino→Entregada/NoEntregada→(reagendar)Pendiente, cobro en destino reutilizando `PagoVenta` directamente sobre la Venta asociada, guard real de `VentaService.TieneEntregaAsociadaAsync`). No se re-valido Sprint 1 (M10/M2/M3, GO) ni Sprint 2 (M4/M5/M11, GO condicionado a checklist manual del usuario aun pendiente) — se tomaron solo como contexto/base, sin re-ejecutar su cobertura.

**Metodo**: revision de codigo real completa de `EntregaService.cs` (los 9 metodos, linea por linea), `EntregasController.cs` (completo), `IEntregaService.cs`, `EntregaDtos.cs`, `EntregaViewModels.cs`, entidades `Entrega.cs`/`EntregaIntento.cs`, `EstadoEntrega.cs`, configuracion Fluent de `Entrega`/`EntregaIntento` en `AppDbContext.cs` (incluida confirmacion de que `Entrega` hereda el query filter global de soft-delete via el loop `ApplySoftDeleteFilter` y que `EntregaIntento` queda correctamente afuera, mismo criterio que `MovimientoStock`/`MovimientoCCLocal`), `VentaService.CancelarAsync`/`TieneEntregaAsociadaAsync` completos, Views `Entregas/{Index,Create,Details}.cshtml` (scripts completos), y los fragmentos modificados de `Ventas/{Create,Details}.cshtml` (card "Entrega", boton "Programar entrega" de la pantalla de exito, ocultamiento de "Cancelar venta"). `dotnet build MariHogar.slnx` y `dotnet ef migrations list` re-ejecutados por QA contra el repo real. **No se ejecuto navegador** (regla del rol) — coherente con la regla de proceso vigente desde el cierre de Sprint 2 (el Implementador tampoco ejecuta smoke test).

### Cobertura de historias de usuario (HU-6.1 a HU-6.3)

| HU | Criterio (resumen) | Resultado | Evidencia |
|---|---|---|---|
| HU-6.1 | Entrega solo desde Venta confirmada; direccion obligatoria; fecha no anterior a hoy | CUMPLE | `EntregaService.CrearAsync`: orden de guards Direccion → VendedorAsignadoId (extra, no exigido literalmente por la CA pero razonable) → `FechaProgramada.Date < DateTime.UtcNow.Date` → Venta existe → `Estado` Pagada/PagadaParcial → sin Entrega previa (maximo 1 por Venta). Todos verificados linea por linea. |
| HU-6.2 | Vista mobile-first; cobro en destino = mismo flujo de PagoVenta que en el local | CUMPLE | `Entregas/Details.cshtml` reutiliza tal cual el patron de una columna + barra inferior fija de `Ventas/Create.cshtml` (Sprint 2, ya dejado "reutilizable" en su propio comentario). `EntregaService.RegistrarCobroAsync` agrega filas a `venta.Pagos` (mismo `PagoVenta`, mismo enum `MetodoPago` restringido a Efectivo/Transferencia/MercadoPago, misma formula `pagadoExistente+sumaNuevosPagos` vs `Total` que `VentaService.ConfirmarAsync`) — confirmado comparando ambos metodos, no hay flujo de pago paralelo. |
| HU-6.3 | "No entregada" con motivo obligatorio + reagendar con nueva fecha; historial de intentos visible | CUMPLE | `MarcarNoEntregadaAsync`: motivo vacio → error; agrega una fila NUEVA a `EntregaIntentos` (`_db.EntregaIntentos.Add(...)`, sin ningun `Update`/`Remove` sobre esa tabla en todo el archivo — confirmado por lectura completa). `ReagendarAsync`: `NoEntregada`→`Pendiente`, exige `nuevaFecha.Date >= hoy`, limpia solo `MotivoNoEntrega` (resumen), nunca toca la coleccion `Intentos`. `Entregas/Details.cshtml` renderiza `e.Intentos` completo (card "Historial de intentos"), ordenado por fecha descendente. |

**Cobertura: 3/3 HU CUMPLE por revision de codigo.** Sin desvios que ameriten observacion (a diferencia de Sprint 2, que tuvo 2 observaciones documentadas).

### Verificacion puntual — Historial de intentos NO se sobreescribe (foco explicito del pedido)

Confirmado por lectura linea por linea de `EntregaService.MarcarNoEntregadaAsync` (lineas 285-322 del archivo): cada llamada exitosa ejecuta `_db.EntregaIntentos.Add(new EntregaIntento { EntregaId = entrega.Id, Fecha = DateTime.UtcNow, FechaProgramadaIntento = entrega.FechaProgramada, Motivo = motivo.Trim(), UsuarioId = usuarioId })` dentro de una transaccion, seguido de `SaveChangesAsync`. `EntregaIntento` tiene su propio `Id` autoincremental (PK independiente) y una FK `EntregaId` — no existe ningun campo "unico intento" en `Entrega` que se pise: `Entrega.MotivoNoEntrega` es explicitamente un resumen del ULTIMO intento (documentado en el XML-doc de la entidad), mientras que la coleccion `Intentos` es la fuente de verdad completa. Grep de `EntregaIntentos` en `EntregaService.cs` confirma que la unica operacion sobre esa tabla en todo el archivo es el `Add` dentro de `MarcarNoEntregadaAsync` — ningun `Update`, `Remove`, ni asignacion a una fila existente. Una segunda (o tercera) "No entregada" sobre la misma Entrega reagendada agrega una segunda (tercera) fila con un `Id` distinto, visible junto a las anteriores en `Entregas/Details.cshtml` (`@foreach (var i in e.Intentos)`, sin limite de cantidad). **Sin defecto** — el requisito explicito del pedido esta cumplido por diseño y por codigo.

### Maquina de estados — Entrega (recorrido completo, transiciones validas e invalidas)

| Origen | Evento | Destino | Guard verificado | Resultado |
|---|---|---|---|---|
| — | Crear desde Venta (Pagada/PagadaParcial, sin Entrega previa) | Pendiente | `venta.Estado` in [Pagada, PagadaParcial] && `!_db.Entregas.Any(VentaId)` | PASS |
| — | Crear desde Venta Pendiente (sin pago) | rechazado | idem | PASS — "Solo se puede programar una entrega para una venta Pagada o Pagada parcialmente." |
| — | Crear una 2da Entrega para la misma Venta | rechazado | `AnyAsync(e => e.VentaId == input.VentaId)` | PASS — "Esta venta ya tiene una entrega programada." |
| Pendiente | Salir a repartir | EnCamino | `Estado == Pendiente` | PASS |
| EnCamino | Salir a repartir de nuevo | rechazado | idem | PASS — "Solo se puede iniciar el recorrido de una entrega Pendiente." |
| Entregada/NoEntregada | Salir a repartir | rechazado | idem | PASS |
| EnCamino | Registrar cobro (pago valido, saldo>0) | EnCamino (sin cambio de estado de Entrega; puede cambiar `Venta.Estado`) | `Estado==EnCamino` && `pagosValidos.Count>0` && metodo permitido && `saldoPendiente>0` | PASS |
| Pendiente/NoEntregada/Entregada | Registrar cobro | rechazado | `Estado != EnCamino` | PASS — "La entrega debe estar En camino para registrar un cobro." |
| EnCamino, venta ya sin saldo | Registrar cobro | rechazado | `saldoPendiente<=0` | PASS |
| EnCamino | Registrar cobro sin pagos / metodo no permitido | rechazado | GAN-001-safe + `MetodosPermitidosCobro` | PASS |
| EnCamino | Marcar entregada (saldo=0) | Entregada | `Estado==EnCamino` | PASS, `FechaEntregada` seteada |
| EnCamino | Marcar entregada (saldo>0) | Entregada | idem, **no bloquea** | PASS — advertencia no bloqueante (ver seccion dedicada abajo) |
| Pendiente/NoEntregada/Entregada | Marcar entregada | rechazado | `Estado != EnCamino` | PASS |
| EnCamino | No entregada (motivo valido) | NoEntregada | `Estado==EnCamino` && motivo no vacio | PASS, agrega `EntregaIntento` |
| EnCamino | No entregada (motivo vacio) | rechazado | idem | PASS — "El motivo es obligatorio." |
| Pendiente/NoEntregada/Entregada | No entregada | rechazado | `Estado != EnCamino` | PASS |
| NoEntregada | Reagendar (fecha >= hoy) | Pendiente | `Estado==NoEntregada` && `nuevaFecha.Date>=hoy` | PASS, `MotivoNoEntrega` se limpia, `Intentos` intacto |
| NoEntregada | Reagendar (fecha anterior a hoy) | rechazado | idem | PASS — "La nueva fecha no puede ser anterior a hoy." |
| Pendiente/EnCamino/Entregada | Reagendar | rechazado | `Estado != NoEntregada` | PASS |
| NoEntregada (reagendada) → EnCamino → No entregada de nuevo | 2do intento | NoEntregada | idem | PASS — 2da fila en `EntregaIntentos`, la 1ra sigue visible (ver seccion dedicada) |

**Cobertura: 19/19 transiciones (validas e invalidas) verificadas por codigo, todas con el resultado esperado.** Consistente con la tabla de `2-disenador-funcional.md`.

### Guard real de cancelacion de Venta — `VentaService.TieneEntregaAsociadaAsync`

Confirmado por lectura de codigo (`MariHogar.Infrastructure/Services/VentaService.cs`, lineas 320-323): el metodo paso de placeholder (`Task.FromResult(false)`, Sprint 2) a consulta real `_db.Entregas.AnyAsync(e => e.VentaId == ventaId)`, **sin filtro de estado** — una Venta con una Entrega en cualquier estado (Pendiente/EnCamino/Entregada/NoEntregada) queda bloqueada para cancelar, consistente con la letra de HU-5.4 ("cancelar una venta con entrega... asociada esta bloqueado", sin excepcion). Verificado:
- **Venta CON Entrega asociada → Cancelar → rechazado.** `CancelarAsync` evalua `TieneEntregaAsociadaAsync(id) || TieneComprobanteAsociadoAsync(id)` antes de abrir la transaccion; con una Entrega existente devuelve `ServiceResult.CreateError("Venta con entrega o factura asociada, no se puede cancelar.")` sin tocar stock ni CC Local. `Ventas/Details.cshtml` ademas oculta el boton "Cancelar venta" (no solo lo deshabilita) cuando `v.EntregaId.HasValue`, mostrando un texto explicativo en su lugar — evita que el usuario intente una accion que el Service va a rechazar igual.
- **Venta SIN Entrega asociada → Cancelar → sigue funcionando con normalidad (no regresiona el caso ya validado en Sprint 2).** El guard es un OR de dos condiciones; si ninguna es verdadera, el flujo continua exactamente igual que en Sprint 2 (motivo obligatorio → guard `Cancelada` ya cancelada → transaccion → reversion de stock por item → reversion de `MovimientoCCLocal` con `EsReversion=true` → commit). No se modifico ninguna otra linea de `CancelarAsync` mas alla de la condicion del guard — confirmado por diff conceptual contra la version de Sprint 2 ya validada. **Sin regresion.**

### Verificacion puntual — "Marcar entregada" con saldo pendiente > 0 (foco explicito del pedido)

Confirmado que el comportamiento es **advertencia no bloqueante**, ni bloqueo silencioso ni confirmacion automatica incorrecta del pago:
- **Server**: `EntregaService.MarcarEntregadaAsync` (lineas 271-283) NO consulta el saldo pendiente en absoluto — el unico guard es `Estado == EnCamino`. La transicion se aplica siempre que la Entrega este En camino, independientemente del saldo. No hay bloqueo silencioso (no existe ningun `if (saldoPendiente > 0) return Error` oculto) ni confirmacion automatica de pago (no se crea ningun `PagoVenta` ni se modifica `Venta.Estado` en este metodo — el saldo pendiente, si lo hay, sigue quedando pendiente de cobro despues de marcar la entrega como Entregada).
- **Cliente**: `Entregas/Details.cshtml`, handler `#btnMarcarEntregada`, arma un `Swal.fire` cuyo `html`/`icon` cambian segun `saldoPendiente > 0` (icono `warning` + texto "Esta venta todavia tiene saldo pendiente de $X. Igual se puede marcar como entregada." vs icono `question` + texto neutro si no hay saldo) pero en ambos casos el flujo termina en el mismo POST a `MarcarEntregada` si el usuario confirma — la advertencia es informativa, no bloquea el submit ni requiere una segunda confirmacion adicional.
- **Consistencia de diseño**: mismo criterio no-bloqueante ya usado en Sprint 2 para el badge de "cantidad > stock" en Ventas (HU-5.8) — decision documentada explicitamente por el implementador (punto 5 de "Decisiones de implementacion").

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

| id | aplica | resultado | accion |
|---|---|---|---|
| REG-001 | no | N/A — sin `RowVersion`/concurrency tokens en `Entrega`/`EntregaIntento` | ninguna |
| REG-002 | no | N/A — no relacionado a stock inicial | ninguna |
| REG-003 | no | N/A — `#selVendedor` en `Entregas/Create.cshtml` es Select2 con `<option>` renderizadas server-side (sin `processResults`/AJAX remoto), no reproduce el patron del bug original | ninguna |
| REG-004 (foco explicito del pedido) | si (botones de la barra inferior de `Entregas/Details.cshtml`) | PASS — los 4 estados posibles (Pendiente/EnCamino/NoEntregada/Entregada) resuelven un set de botones distinto via `@if (e.EstadoReal == ...)` contra `EstadoReal` (enum tipado, no el string `Estado`), nunca hardcodeados; verificado que "Marcar entregada"/"No entregada" solo aparecen en EnCamino, "Salir a repartir" solo en Pendiente, "Reagendar" solo en NoEntregada, "Volver a la venta" en Entregada (rama `else`) | ninguna |
| REG-005 | no | N/A — idem REG-003, no hay Select2 remoto en Entregas | ninguna |
| REG-006 | no | N/A — cobro en destino solo expone Efectivo/Transferencia/MercadoPago (`MetodosPermitidosCobro`), sin sub-campos condicionales tipo Cheque/Deposito | ninguna |
| REG-007 | no | N/A — modulo Devoluciones no existe | ninguna |
| REG-008 | si (grilla de pagos del cobro en destino, `#listaPagosCobro`) | PASS — el listener `input` sobre `.inp-monto-cobro` (linea ~267 de `Details.cshtml`) solo actualiza `pagos[idx].monto` en el array en memoria + `actualizarIndicadorCobro()`, sin volver a llamar `renderPagosCobro()` (que si reconstruye el DOM, pero solo se invoca en agregar/quitar/cambiar-metodo, nunca en cada tecla del monto) — no se pierde el foco al tipear un importe | ninguna |
| REG-009 | no | N/A — sin combos en cascada en Entregas | ninguna |
| REG-010 | si (link "Entregas" del sidebar) | PASS — visible para SuperUsuario/Administrador/Vendedor en `_Layout.cshtml` (linea 129-133, dentro del mismo `@if` que ya protege "Ventas"/"Presupuestos"), coincide exactamente con `[Authorize(Policy="RequireVentas")]` de `EntregasController` | ninguna |
| KOI-001 | no (patron distinto) | N/A — los botones de accion de `Entregas/Details.cshtml` no usan el handler generico `.btn-swal-confirm`/`closest('form')` de `site.js`; cada uno tiene su propio handler JS dedicado (`$('#formIniciarRecorrido').on('submit', ...)`, `$('#btnMarcarEntregada').on('click', ...)`, etc.) que arma el POST explicitamente — no reproduce el mecanismo que causaba el bug original | ninguna |
| KOI-002/003/004 | no | N/A — modulos no existen | ninguna |
| KOI-005/006 (mismo patron: sidebar -> controller inexistente) | si | PASS — `Entregas` referenciado en `_Layout.cshtml` tiene su controller real (`EntregasController.cs` existe y compila) | ninguna |
| DN-001/DN-002 | no | N/A — stack EF Core 10 + Pomelo, no EF6; ademas `EntregaService.ListarAsync`/`GetByIdAsync` no combinan `Include` de coleccion + orden/filtro dinamico + `Skip/Take` en el mismo `IQueryable` (Venta/VendedorAsignado son navegaciones simples, `Intentos` se incluye solo en `GetByIdAsync` que trae 1 sola Entrega sin paginacion) | ninguna |
| GAN-001 | si (guard "al menos un pago real" en `RegistrarCobroAsync`) | PASS — `pagos` viaja por JSON armado en JS (`pagosJson`), no por binding indexado de formulario (`Pagos[i].*`), fuera del mecanismo estructural que originaba GAN-001; el server igual revalida con el mismo criterio defensivo (`pagos.Where(p => p.Monto > 0)`, rechaza si `Count==0`) | ninguna |
| GAN-002 | no | N/A — sin backfill de datos en este sprint | ninguna |
| GAN-003 | no | N/A — grep de `text/x-template` sobre `Views/Entregas/*.cshtml` sin resultados (0 ocurrencias) | ninguna |
| GAN-004 | no | N/A — grep de `<datalist>` sobre `Views/Entregas/*.cshtml` sin resultados | ninguna |
| VSF-001/002 | no | N/A — modulo Compras/OC no existe todavia | ninguna |
| CRM-001 a 006 | no | N/A — modulo Bot/CRM no existe | ninguna |
| MH-001 (re-chequeo preventivo, foco del pedido) | si | PASS — `EntregaService.GetByIdAsync` resuelve nombres de usuario de los intentos con `(await _db.Users.AsNoTracking().ToListAsync()).Where(u => usuarioIds.Contains(u.Id))` (trae la tabla completa a memoria PRIMERO, filtra en-proceso despues — patron MH-001-safe correcto, no un `Where` traducido a SQL `IN` sobre coleccion local); `ListarAsync` resuelve el saldo pendiente por Venta con consultas individuales acotadas al tamaño de pagina (`foreach` + `SumAsync` por fila), mismo patron ya usado por `VentaService.ListarAsync` en Sprint 2. Grep de `.Contains(` sobre `EntregaService.cs` no encontro ninguna otra ocurrencia riesgosa | ninguna |
| MH-002 | no (no aplica a DTOs nuevos) | N/A — `EntregaListItemDto.Estado` y `EntregaDetailDto.Estado` ya se mapean con `.ToString()` desde el Service (`Estado = e.Estado.ToString()`), mismo patron correcto que evito MH-002 en Sprint 1 | ninguna |

### Matriz de formularios (pedido "100% OK") — Sprint 3

Verificados por codigo (server-side siempre revalida). [MANUAL] = requiere navegador real, ejecutado por el usuario (ya incluido en la checklist de 11 pasos que dejo el implementador en `5-implementador.md`).

**Alta de Entrega (`Entregas/Create`)**
1. Direccion vacia → PASS — `[Required]` client-side (textarea) + `string.IsNullOrWhiteSpace(input.Direccion)` server-side, mensaje "La direccion es obligatoria."
2. Fecha anterior a hoy → PASS — `<input type="date" min="@DateTime.Today...">` client-side + `input.FechaProgramada.Date < DateTime.UtcNow.Date` server-side, mensaje "La fecha programada no puede ser anterior a hoy."
3. Vendedor asignado no seleccionado → PASS — `[Required]` + `string.IsNullOrWhiteSpace(input.VendedorAsignadoId)` server-side (guard extra no exigido literalmente por la CA de diseño, pero razonable — no bloqueante para la evaluacion).
4. Venta ya tiene una Entrega → PASS — bloqueado con "Esta venta ya tiene una entrega programada." (verificado tambien a nivel `Create GET`, que redirige con TempData de error si `ObtenerPrecargaDesdeVentaAsync` devuelve null).
5. Venta no Pagada/PagadaParcial → PASS — bloqueado con el mismo mensaje de precarga invalida.
6. [MANUAL] Confirmar visualmente que el date picker efectivamente no deja elegir una fecha anterior a hoy (paso 1 de la checklist del implementador).

**"No entregada" (`Entregas/NoEntregada`)**
7. Motivo vacio → PASS — `inputValidator` de SweetAlert2 client-side ("El motivo es obligatorio.") + `string.IsNullOrWhiteSpace(motivo)` server-side, mismo mensaje.
8. Estado distinto de EnCamino (POST forzado) → PASS — rechazado con "Solo se puede marcar como No entregada una entrega En camino."

**Reagendar (`Entregas/Reagendar`)**
9. Fecha vacia (POST forzado sin pasar por el SweetAlert2, que ya exige un valor) → PASS — `DateTime nuevaFecha` sin bind cae en `DateTime.MinValue`, capturado igual por el guard `nuevaFecha.Date < DateTime.UtcNow.Date` → rechazado con el mismo mensaje que "fecha anterior a hoy" (sin excepcion no controlada).
10. Fecha anterior a hoy → PASS — `min` en el `<input type="date">` del SweetAlert2 (`moment().format('YYYY-MM-DD')`) + guard server-side, mensaje "La nueva fecha no puede ser anterior a hoy."
11. Estado distinto de NoEntregada (POST forzado) → PASS — rechazado con "Solo se puede reagendar una entrega marcada como No entregada."

**Cobro en destino (`Entregas/RegistrarCobro`)**
12. Mismo patron que `PagoVenta` de Sprint 2 (no un flujo paralelo) → PASS — verificado en la seccion dedicada arriba: mismo enum `MetodoPago` restringido, misma formula de `EstadoVenta`, mismas filas `PagoVenta` (no una entidad de pago propia de Entregas).
13. Sin pagos → PASS — boton deshabilitado client-side (`hayPagoReal`) + server rechaza (`pagosValidos.Count==0`, "Cargue al menos una forma de pago.").
14. Metodo no permitido (payload manipulado, ej. Cheque) → PASS — `MetodosPermitidosCobro.Contains` rechaza con "Forma de pago no valida para un cobro de venta (solo Efectivo, Transferencia o MercadoPago)."
15. Venta sin saldo pendiente (POST forzado) → PASS — rechazado con "La venta ya esta completamente pagada, no hay saldo pendiente para cobrar."
16. Entrega no En camino (POST forzado) → PASS — rechazado con "La entrega debe estar En camino para registrar un cobro."
17. [MANUAL] Confirmar visualmente el cobro con "Todo efectivo"/pago combinado y que el saldo/estado de la Venta se actualiza tras recargar (pasos 3 y 4 de la checklist del implementador).

### Defectos activos

**Ninguno.** No se reprodujo ningun bug funcional por revision de codigo en el alcance de Sprint 3. Sin necesidad de auto-fix.

Observaciones (no bloqueantes, ya documentadas por el implementador, QA las revalida sin objeciones):
- `Venta.Estado` no se fusiona con el estado logistico de la Entrega (decision documentada, cambio de alcance medio si el cliente lo pide).
- `MarcarEntregadaAsync` no bloquea con saldo pendiente > 0 — verificado arriba que es advertencia no bloqueante por diseño, consistente con HU-5.8 de Sprint 2. No es un defecto.
- Riesgo bajo de concurrencia no mitigado en `EntregaService.CrearAsync` (mismo argumento ya aceptado en Sprint 2 para "Convertir a venta": comercio de un solo mostrador, baja probabilidad, no confirmado por lectura de codigo sola).

### Riesgos de liberacion

- **Medio-bajo, heredado y acumulado**: ningun tramo de Sprint 2 (confirmacion de Venta con pago combinado, stock, CC Local, cancelacion con reversion) ni de Sprint 3 (alta de Entrega, cobro en destino, ciclo No entregada→Reagendar, guard de cancelacion) fue ejecutado en un entorno real por nadie (ni implementador ni QA, regla de proceso vigente). El riesgo se acumula sprint a sprint sin cerrarse. **Mitigacion**: la checklist de 11 pasos de `5-implementador.md` (Sprint 3) cubre especificamente el ciclo completo de Entrega (alta → salir a repartir → cobro parcial → marcar entregada → no entregada → reagendar → repetir no entregada y verificar 2 filas de historial → guard de cancelacion → alta bloqueada → permisos → mobile) y debe ejecutarse junto con la checklist pendiente de Sprint 2 antes de considerar ambos sprints 100% cerrados ante el cliente.
- **Bajo**: concurrencia de doble-alta de Entrega para la misma Venta (dos pestañas simultaneas) — mismo argumento de riesgo bajo ya aceptado para "Convertir a venta" en Sprint 2, no mitigado con indice unico por directriz de cambios minimos.
- **Bajo**: `MarcarEntregadaAsync` sin bloqueo de saldo pendiente — decision de negocio ya documentada y consistente con el resto del sistema (advertencias no bloqueantes), no requiere accion salvo que el cliente pida explicitamente bloquear.
- Sin riesgos nuevos de severidad blocker/critical/major detectados en este sprint.

### Pruebas minimas ejecutadas

- `dotnet build MariHogar.slnx` → Compilacion correcta, 0 errores (9 warnings preexistentes NU1902 + CS0114, ninguno nuevo) — re-verificado por QA.
- `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` → `20260724145210_InitialCreate`, `20260724152806_AddCatalogo`, `20260724175804_AddPresupuestosVentas`, `20260724184703_AddEntregas` — 4 migraciones, ninguna marcada pendiente, coincide con lo declarado por el implementador.
- Revision de codigo completa de: `EntregaService.cs` (los 9 metodos, linea por linea), `EntregasController.cs`, `IEntregaService.cs`, `EntregaDtos.cs`, `EntregaViewModels.cs`, `Entrega.cs`, `EntregaIntento.cs`, `EstadoEntrega.cs`, configuracion Fluent de `AppDbContext.cs` (Entrega/EntregaIntento + confirmacion de query filter global), `VentaService.CancelarAsync`/`TieneEntregaAsociadaAsync`, `Views/Entregas/{Index,Create,Details}.cshtml` completas, fragmentos modificados de `Views/Ventas/{Create,Details}.cshtml`, `_Layout.cshtml` (sidebar).
- Grep de patrones riesgosos (`.Contains(` sobre colecciones locales, `text/x-template`, `<datalist>`, `RequestVerificationToken`) sobre `MariHogar.Infrastructure/Services/EntregaService.cs` y `MariHogar.Web/Views/Entregas`.
- Ejecucion completa del playbook cross-proyecto (28 items del catalogo, incluidos MH-001/MH-002 de Sprint 1) mapeado al modulo Entregas.

### Estado go/no-go

**GO para habilitar Sprint 4** (M7 Facturacion electronica AFIP/ARCA), con la misma condicion acumulada ya vigente desde Sprint 2: **sin defectos bloqueantes ni criticos detectados por revision de codigo en Sprint 3** (3/3 HU CUMPLE, 19/19 transiciones de la maquina de estados de Entrega verificadas, guard de cancelacion de Venta confirmado real y sin regresion del caso sin Entrega, historial de intentos confirmado que nunca se sobreescribe, "Marcar entregada" confirmado como advertencia no bloqueante). Condicion recomendada (no bloqueante para empezar Sprint 4, pero si antes de dar Sprint 2 y Sprint 3 por 100% cerrados ante el cliente): que el usuario ejecute la checklist de 11 pasos de Sprint 3 (`5-implementador.md`) **junto con** la checklist pendiente de 12 pasos de Sprint 2 (nunca ejecutada) — es el unico tramo funcional de todo el sistema construido hasta ahora que no fue verificado en un entorno real por nadie. El riesgo tecnico por codigo es bajo (revision profunda sin hallazgos); el riesgo de proceso (acumulacion de sprints sin verificacion en caliente) es el unico pendiente real de cierre.
## Sprint 2 — M4 Presupuestos y cotizaciones + M5 Gestion de ventas (⭐ prioridad maxima) + M11 CC Local

### Alcance validado

Sprint 2: M4 (`Presupuesto`/`PresupuestoItem`, maquina de estados Borrador→Enviado→Aprobado→Convertido/Rechazado/Expirado-calculado-al-leer, PDF QuestPDF), M5 (`Venta`/`VentaItem`/`PagoVenta`, pantalla POS elevada con las 5 HU de UX adicionales HU-5.5 a HU-5.9, transaccion unica Venta+Items+Pagos+Stock+CC en `VentaService.ConfirmarAsync`, cancelacion con reversion en `CancelarAsync`), M11 (`MovimientoCCLocal`, ledger inmutable con saldo). No se valido nada fuera de este alcance (Entregas/AFIP/Compras/CC Proveedores/Cheques/Gastos/Caja/Proyeccion/Aumento masivo/Dashboard/CRM/Bot quedan para sprints siguientes). Sprint 1 (GO) no se re-valido, solo se tomo como base.

**Metodo**: revision de codigo linea por linea de `VentaService.cs` (ConfirmarAsync/CancelarAsync completos), `PresupuestoService.cs` (completo), `CCLocalService.cs`/`StockService.RegistrarMovimientoAsync` (completos), `VentasController`/`PresupuestosController`/`CCLocalController`, Views `Ventas/Create.cshtml` (script completo, ~460 lineas), `Ventas/Index.cshtml`, `Ventas/Details.cshtml`, `Presupuestos/{Create,Edit,Details,Index}.cshtml`, `CCLocal/Index.cshtml`, entidades Domain (`Venta`, `Presupuesto`, `MovimientoCCLocal`, enums `EstadoVenta`/`EstadoPresupuesto`/`MetodoPago`/`TipoMovimientoCC`), configuracion Fluent de `AppDbContext` (indices/FKs/precision), DTOs/ViewModels de los 3 modulos, `site.js` (handler `.btn-swal-confirm`), `_Layout.cshtml` (sidebar). `dotnet build` y `dotnet ef migrations list` re-ejecutados por QA contra el repo real. **No se ejecuto navegador** (regla del rol) — se hizo foco especial en revision de codigo profunda para el riesgo declarado por el implementador (ver mas abajo), tal como pidio el orquestador.

### Riesgo declarado por el implementador — cierre por revision de codigo

El implementador documento que la confirmacion de Venta con pago combinado, la baja de stock, el movimiento de CC Local y la cancelacion con reversion **no se probaron en caliente** (solo por codigo) en la seccion "Evidencia de cierre" y "Riesgos residuales" de `5-implementador.md`. QA hizo lectura linea por linea de `VentaService.ConfirmarAsync`/`CancelarAsync` para cerrar este riesgo lo maximo posible sin navegador:

- **`ConfirmarAsync`**: guard GAN-001 (items/pagos reales, no solo `Count==0`) correcto → valida `MetodosPermitidosVenta` (Efectivo/Transferencia/MercadoPago) → si viene de un Presupuesto, verifica que siga `Aprobado` → abre transaccion → crea `Venta` con precio SIEMPRE tomado de `Producto.PrecioVenta` del servidor (nunca del payload, anti price-drift) → primer `SaveChangesAsync` para obtener `Venta.Id` → descuenta stock por item via `IStockService.RegistrarMovimientoAsync` (sin `SaveChanges`/transaccion propia, corre dentro de la misma tx) → registra ingreso en CC Local via `ICCLocalService.RegistrarMovimientoAsync` (idem) → si hay presupuesto de origen, recien AHI lo pasa a `Convertido` + `VentaGeneradaId` → segundo `SaveChangesAsync` → `CommitAsync`; `catch` hace `RollbackAsync`. Orden de operaciones correcto, todo dentro de una unica transaccion real (`BeginTransactionAsync`), sin puntos donde una falla parcial deje stock/CC desincronizados del estado de la Venta.
- **`CancelarAsync`**: motivo obligatorio → rechaza si ya esta `Cancelada` → guard `TieneEntregaAsociadaAsync`/`TieneComprobanteAsociadoAsync` (hoy siempre `false`, M6/M7 no existen, placeholder correcto) → transaccion → revierte stock con `+cantidad` por item (contramovimiento, nunca se borra el original) → revierte CC Local con un movimiento `Egreso` de `EsReversion=true` por `venta.Total` (aritmetica correcta: `SaldoActual = Σ Ingreso − Σ Egreso`, tras cancelar una venta unica el saldo neto vuelve a 0) → `SaveChangesAsync` + `Commit`.
- **`StockService.RegistrarMovimientoAsync`/`CCLocalService.RegistrarMovimientoAsync`**: confirmado que NO abren transaccion ni hacen `SaveChanges` propios (comentario explicito en el codigo), correcto para el patron "el caller controla la unica transaccion".
- **Firmas de llamada**: verificadas 1 a 1 contra las interfaces — sin mismatch de parametros/orden.

**Conclusion de QA**: la logica de la transaccion critica es correcta por revision de codigo profunda. Esto reduce el riesgo pero **no reemplaza la verificacion en caliente** (persistencia real en MySQL, antiforgery real en navegador, serializacion JSON real) — se mantiene como riesgo residual medio-bajo, ver seccion de riesgos de liberacion.

### Hallazgo de proceso — inconsistencia documental sobre si el smoke test se ejecuto (IMPORTANTE)

`5-implementador.md` (Sprint 2) es **internamente contradictorio**: el parrafo "Nota de proceso (correccion)" (inicio de la seccion Sprint 2) afirma que se ejecuto un smoke test completo por `curl` cubriendo confirmacion de Venta con pago combinado, baja de stock, movimiento de CC Local y cancelacion con reversion, "todos los resultados fueron los esperados". Pero la seccion "Evidencia de cierre" (mas abajo, en el mismo archivo) dice literalmente lo opuesto: *"No se llego a probar la confirmacion de Venta (Ventas/Confirmar), el pago combinado, la baja de stock, el movimiento de CC Local, la cancelacion con reversion, ni los casos de borde de Ventas — todo eso queda en la checklist de verificacion manual"*, y solo confirma `Presupuestos/Create`→`Enviar`→`Aprobar`. `trazabilidad.md` (entrada del implementador, Sprint 2) copio la version optimista ("Nota de proceso"), no la real.

QA sigue la instruccion explicita del orquestador para este ciclo (la version real es "NO se ejecuto smoke test end-to-end de Venta/stock/CC/cancelacion, solo revision de codigo") y trata la seccion "Evidencia de cierre" + "Verificacion manual pendiente" de `5-implementador.md` como la fuente de verdad. **Esta contradiccion documental debe corregirse** en `5-implementador.md` y en la entrada de `trazabilidad.md` del implementador (fuera del alcance de edicion de QA — se recomienda al orquestador/implementador reconciliar ambos parrafos para que no quede una afirmacion falsa de cobertura en la memoria del proyecto). Se registra aqui como hallazgo de severidad **major** (riesgo de proceso, no de codigo): una futura lectura rapida de `trazabilidad.md` podria asumir que el flujo critico ya fue validado en caliente cuando no es asi.

### Cobertura de historias de usuario (HU-4.1 a HU-4.4, HU-5.1 a HU-5.9)

| HU | Criterio (resumen) | Resultado | Evidencia |
|---|---|---|---|
| HU-4.1 | Armar presupuesto, total recalculado sin recargar, stock informativo no bloqueante | CUMPLE | `Presupuestos/Create.cshtml` arma items 100% en JS (Select2 + tabla), `actualizarTotal()` recalcula sin submit; badge de stock solo informativo (`it.stockActual < it.cantidad`), nunca bloquea agregar |
| HU-4.2 | PDF con datos completos, boton visible en cualquier estado | CUMPLE | `PresupuestoService.GenerarPdfAsync` (QuestPDF) incluye cliente/items/precios/total/vigencia; `Details.cshtml` muestra "Descargar PDF" fuera de cualquier `@if` de estado |
| HU-4.3 | "Convertir a venta" solo en Aprobado; venta hereda items; presupuesto pasa a Convertido | CUMPLE (con decision documentada, ver punto dedicado abajo) | Boton solo dentro de `@if (EstadoReal == Aprobado)`; `ObtenerPrecargaDesdePresupuestoAsync` valida `Estado == Aprobado`; transicion real a `Convertido` ocurre dentro de `VentaService.ConfirmarAsync`, no al click |
| HU-4.4 | Rechazado con motivo opcional; Expirado calculado sin job | CUMPLE | `RechazarAsync` acepta motivo opcional; `EstadoEfectivo()`/`AplicarFiltroEstadoEfectivo()` calculan Expirado 100% en SQL (`FechaEnvio.AddDays(VigenciaDias) < UtcNow`), sin persistir el estado ni requerir job |
| HU-5.1 | Venta con pagos combinados; suma=total→Pagada, suma<total→Parcial/Pendiente | CUMPLE (con desvio documentado, ver "Observaciones") | `ConfirmarAsync`: `Estado = sumaPagos<=0 ? Pendiente : sumaPagos>=total ? Pagada : PagadaParcial`. El guard "al menos 1 pago > 0" (server + client) hace que `Pendiente` sea inalcanzable en la practica — desvio de la letra literal de la CA, ver observacion |
| HU-5.2 | Movimiento de ingreso en CC en la misma transaccion; reversion (no borrado) al cancelar | CUMPLE | Verificado linea por linea en `ConfirmarAsync`/`CancelarAsync` (ver seccion dedicada arriba) |
| HU-5.3 | Listado con filtro estado/vendedor/forma de pago/fecha; Vendedor ve todas | CUMPLE | `VentaFiltro` con los 5 campos; `VentaService.ListarAsync` sin filtro implicito por usuario (comentario explicito confirmando el supuesto de diseño) |
| HU-5.4 | Cancelar bloqueado si hay Entrega/Comprobante; revierte stock+CC | CUMPLE (guard placeholder por diseño) | Guard consulta `TieneEntregaAsociadaAsync`/`TieneComprobanteAsociadoAsync` (siempre `false` este sprint, M6/M7 no existen, documentado); reversion verificada arriba |
| HU-5.5 | Buscador instantaneo con foto/precio/stock, Enter agrega sin mouse | CUMPLE | Select2 remoto contra `Productos/Buscar` (debounce 200ms), `templateResult` con foto+precio+stock, `select2:select` agrega y devuelve foco al buscador (`setTimeout` 60ms) |
| HU-5.6 | Total en zona fija/sticky desktop, barra inferior fija mobile | CUMPLE (por codigo/CSS) | `.ov-venta-resumen{position:sticky}` en `col-lg-4`; `.ov-venta-bottombar{position:fixed}` con `d-lg-none`. [MANUAL: confirmar visualmente, paso 12 de la checklist] |
| HU-5.7 | Editar cantidad inline, quitar con Deshacer no bloqueante | CUMPLE | Steppers +/- e input numerico actualizan solo la celda afectada (no re-render); quitar dispara toast Bootstrap con boton "Deshacer" (6s) que reinserta en la posicion original |
| HU-5.8 | Badge de advertencia no bloqueante si cantidad > stock | CUMPLE | `actualizarBadgeStock()` solo agrega un badge visual; el guard de servidor de stock negativo (M3) explicitamente NO se reutiliza en `ConfirmarAsync` (comentario confirma la decision) |
| HU-5.9 | Pantalla de exito con 4 acciones (nueva venta/ver/entrega/facturar) | CUMPLE (2 de 4 funcionales, 2 deshabilitadas por diseño) | `#panelExitoVenta` reemplaza el contenido (no modal); "Nueva venta"/"Ver venta" funcionales, "Programar entrega"/"Facturar" deshabilitados con tooltip "Proximo sprint" (M6/M7 no existen, correcto para el alcance) |

**Cobertura**: 13/13 HU CUMPLE por revision de codigo. 2 observaciones documentadas (no bloqueantes) en HU-5.1 y HU-4.3, ver abajo.

### Maquina de estados — Presupuesto (recorrido completo, transiciones validas e invalidas)

| Origen | Evento | Destino | Guard verificado | Resultado |
|---|---|---|---|---|
| — | Crear | Borrador | Ninguno (0 items permitido) | PASS — `CreateAsync` no exige items |
| Borrador | Enviar (con items) | Enviado | `Items.Count>0 && Items.Any(Cantidad>0)` | PASS — `EnviarAsync` guard GAN-001-safe |
| Borrador | Enviar (SIN items) | rechazado | idem | PASS — retorna error "Agregue al menos un item..." |
| Enviado | Aprobar | Aprobado | `EstadoEfectivo(p)==Enviado` (no vencido) | PASS |
| Enviado (vencido) | Aprobar | rechazado | idem, `EstadoEfectivo` calcula Expirado | PASS — no permite aprobar un Enviado ya vencido |
| Aprobado | Aprobar de nuevo | rechazado | `EstadoEfectivo(p)==Enviado` falla si ya es Aprobado | PASS — transicion invalida bloqueada |
| Borrador | Aprobar (salteando Enviado) | rechazado | idem | PASS |
| Enviado | Rechazar | Rechazado | `EstadoEfectivo(p)==Enviado` | PASS, motivo opcional |
| Convertido/Rechazado/Expirado | Rechazar/Aprobar | rechazado | idem | PASS — estados terminales no re-transicionan |
| Aprobado | Convertir a venta (click) | sin cambio de estado hasta confirmar Venta | ver punto dedicado abajo | PASS |
| Aprobado | Confirmar Venta asociada | Convertido | dentro de `VentaService.ConfirmarAsync`, mismo tx | PASS |
| Borrador | Editar (`UpdateAsync`) | — | `Estado != Borrador` rechaza edicion | PASS — Enviado/Aprobado/etc. no editables |
| — | Enviado→Expirado | Expirado (calculado, no persistido) | `FechaEnvio+VigenciaDias < UtcNow`, 100% en SQL | PASS, HU-4.4 |

### Maquina de estados — Venta (recorrido completo, transiciones validas e invalidas)

| Origen | Evento | Destino | Guard verificado | Resultado |
|---|---|---|---|---|
| — | Confirmar (items válidos + pagos>0, suma=total) | Pagada | `sumaPagos>=total` | PASS |
| — | Confirmar (0<suma<total) | PagadaParcial | rama `else` | PASS |
| — | Confirmar (suma<=0) | **Pendiente — inalcanzable en la practica** | guard previo exige `pagosValidos.Count>0` con `Monto>0` | **Observacion** (ver abajo), no bloqueante |
| — | Confirmar sin items | rechazado | `itemsValidos.Count==0` | PASS, GAN-001-safe |
| — | Confirmar sin pagos (o todos en 0) | rechazado | `pagosValidos.Count==0` | PASS |
| — | Confirmar con metodo no permitido (Cheque/Deposito) | rechazado | `MetodosPermitidosVenta.Contains` | PASS |
| — | Confirmar con producto inexistente | rechazado + rollback | `producto==null` dentro del loop, con `tx.RollbackAsync()` explicito | PASS |
| — | Confirmar con `PresupuestoOrigenId` de un presupuesto no Aprobado/inexistente | rechazado | check previo a abrir transaccion | PASS |
| Pendiente/Parcial/Pagada | Cancelar (motivo) | Cancelada | motivo obligatorio + guard Entrega/Comprobante | PASS |
| Cancelada | Cancelar de nuevo | rechazado | `Estado==Cancelada` → error "ya esta cancelada" | PASS — no doble reversion |
| Con Entrega/Comprobante (M6/M7, simulado) | Cancelar | rechazado | guard dedicado (hoy siempre `false`, sin M6/M7) | N/A este sprint, guard correctamente preparado |
| — | Transicion a "Con entrega pendiente"/"Entregada" | N/A | `EstadoVenta` enum de este sprint solo tiene 4 valores (Pendiente/PagadaParcial/Pagada/Cancelada) | Correcto — diseño documenta que esos 2 sub-estados quedan para M6 |

### Verificacion puntual — "Convertir a venta" no deja hueco de inconsistencia (tarea 3 del pedido)

Confirmado por codigo: `PresupuestosController.ConvertirAVenta` es un **GET sin efecto de persistencia** — solo valida que la precarga exista (`Estado==Aprobado`) y hace `RedirectToAction("Create","Ventas", new{presupuestoId=id})`. `VentasController.Create(int? presupuestoId)` tambien es GET puro: arma el `VentaCreateViewModel` en memoria (sin crear ninguna fila `Venta` en la base). La transicion real `Aprobado→Convertido` ocurre **exclusivamente** dentro de la transaccion de `VentaService.ConfirmarAsync` (ver linea 243-247 del servicio). Por lo tanto:

- Si el vendedor navega a `Ventas/Create?presupuestoId=X` y **abandona la pantalla sin confirmar** (cierra la pestaña, navega a otro lado), no queda ningun rastro en la base — el Presupuesto sigue en `Aprobado`, re-navegable desde `Details` con el mismo boton "Convertir a venta" cuantas veces haga falta. **No hay hueco de inconsistencia.**
- **Riesgo residual de concurrencia (no confirmado, requiere ejecucion real para reproducirse)**: la consulta `presupuestoOrigen = await _db.Presupuestos.FirstOrDefaultAsync(...)` y el chequeo `Estado != Aprobado` ocurren **antes** de `BeginTransactionAsync()`, sin re-chequeo dentro de la transaccion ni bloqueo optimista. Si dos pestañas/dispositivos confirman la misma Venta desde el mismo Presupuesto Aprobado casi simultaneamente, ambas podrian pasar el chequeo inicial y crear 2 Ventas del mismo Presupuesto (la segunda sobreescribe `VentaGeneradaId`). Mitigado en la practica por: (a) el boton "Confirmar venta" se deshabilita en el primer click (mismo tab), (b) es un escenario de doble-tab de baja probabilidad en un comercio de un solo mostrador. **No es un bug confirmado** (no reproducible por lectura de codigo sola, requiere una prueba de concurrencia real) — se documenta como riesgo menor para endurecer en un sprint futuro (ej. re-chequear `presupuestoOrigen.Estado` dentro de la transaccion antes de commitear, o un indice unico funcional). No amerita auto-fix ahora (fuera de las reglas del rol: no se adivina, se escala).

### Observaciones (desvios documentados, no bloqueantes)

1. **`EstadoVenta.Pendiente` inalcanzable via `ConfirmarAsync`**: tanto el guard de servidor (`pagosValidos.Count==0` → error "Cargue al menos una forma de pago") como el de cliente (`btn-confirmar-venta` deshabilitado sin `hayPagoReal`) exigen al menos 1 pago con `Monto>0` para poder confirmar. Esto contradice la letra literal de CA-5.1 ("permite guardar como Pendiente/Pagada parcialmente si la suma es menor" — "menor" podria incluir 0) y dejaria el estado `Pendiente` del enum sin ningun camino de entrada real. Sin embargo, es **consistente con el supuesto de negocio P5-A** ("Ventas solo al contado, no hay clientes con deuda/fiado") documentado en `1-analista-funcional.md`: permitir confirmar una venta con $0 cobrado equivaldria a crear una venta fiada. QA no adivina cual interpretacion es la correcta — se documenta como desvio a confirmar con el cliente/orquestador, no se aplica auto-fix.
2. Ver "Hallazgo de proceso" arriba (contradiccion documental en `5-implementador.md`/`trazabilidad.md` sobre el smoke test).

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

| id | aplica | resultado | accion |
|---|---|---|---|
| REG-001 | no | N/A — sin `RowVersion`/concurrency tokens en las entidades nuevas | ninguna |
| REG-002 | no (ya cubierto en Sprint1) | N/A — sin cambios sobre el flujo de stock inicial este sprint | ninguna |
| REG-003 | si (buscador Select2 de Presupuestos/Ventas) | PASS — `Productos/Buscar` + `processResults` mapean campos reales (`id`,`nombre`,`marcaNombre`,`precioVenta`,`stockActual`,`fotoUrl`), sin el bug de campo inexistente (`v.descripcion`) del original | ninguna |
| REG-004 | si (botones de Presupuesto/Venta) | PASS — todos los botones de accion estan dentro de `@if (EstadoReal == ...)` contra el estado real del modelo, nunca hardcodeados | ninguna |
| REG-005 | si (mismo patron que REG-003 en Ventas) | PASS — idem REG-003 | ninguna |
| REG-006 | si (campos condicionales por metodo de pago) | N/A este sprint — Ventas solo expone Efectivo/Transferencia/MercadoPago (sin sub-campos condicionales); Cheque/Deposito quedan para M12 (Compras), no tocado | ninguna, a revisar cuando exista Pago de OC |
| REG-007 | no | N/A — modulo Devoluciones no existe | ninguna |
| REG-008 | si (critico, carrito de Ventas) | PASS — `actualizarResumen()`/`actualizarFilaCantidad()` actualizan solo el nodo DOM afectado; el listener `input` de `.inp-monto-pago` nunca reconstruye `#listaPagos`, confirmado por lectura del script completo | ninguna |
| REG-009 | no | N/A — sin combos en cascada este sprint | ninguna |
| REG-010 | si (link "Cuenta corriente" del sidebar) | PASS — visible solo para SuperUsuario/Administrador en `_Layout.cshtml` (linea 131), coincide con `[Authorize(Policy="RequireAdministracion")]` de `CCLocalController` | ninguna |
| KOI-001 | si (botones Enviar/Aprobar de Presupuesto) | PASS — `.btn-swal-confirm` con `data-form="formEnviar"`/`"formAprobar"`; `site.js` ya soporta `data-form` (fix historico ya presente) | ninguna |
| KOI-002/003/004 | no | N/A — modulos no existen | ninguna |
| KOI-005/006 | si (mismo patron: sidebar apunta a controller inexistente) | PASS — `Ventas`/`Presupuestos`/`CCLocal` referenciados en `_Layout.cshtml` tienen sus 3 controllers reales | ninguna |
| DN-001/DN-002 | no | N/A — stack EF Core 10 + Pomelo, no EF6 | ninguna |
| GAN-001 | si (guard "al menos un item/pago real") | PASS — Presupuesto: `Items` del ViewModel inicializa vacio (`new()`, sin fila fantasma) y el guard de `EnviarAsync` no depende de un binding indexado con default; Venta: `Pagos`/`Items` viajan por JSON armado en JS (sin binding indexado de formulario), fuera del mecanismo que originaba GAN-001 — server revalida igual con el mismo criterio defensivo | ninguna |
| GAN-002 | no | N/A — sin backfill de datos este sprint | ninguna |
| GAN-003 | no | N/A — sin `<script type="text/x-template">` (grep confirma 0 ocurrencias en Views del sprint) | ninguna |
| GAN-004 | no | N/A — sin `<datalist>` (combos usan Select2) | ninguna |
| VSF-001/002 | no | N/A — modulo Compras/OC no existe todavia | ninguna |
| CRM-001 a 006 | no | N/A — modulo Bot/CRM no existe | ninguna |
| MH-001 | si (re-chequeo preventivo) | PASS — grep de `.Contains(` sobre `MariHogar.Infrastructure/Services` no encontro ningun nuevo `Where(coleccionLocal.Contains(...))` traducido a SQL; `VentaService.ListarAsync` resuelve `FormasPago` con consultas individuales acotadas a la pagina (no un IN), documentado explicitamente en el codigo | ninguna |
| MH-002 | no (no aplica a DTOs nuevos) | N/A — los DTOs nuevos (`VentaListItemDto.Estado`, `PresupuestoListItemDto.Estado`, `MovimientoCCLocalListItemDto.Tipo`) ya se mapean con `.ToString()` desde el Service, mismo patron correcto que evito MH-002 | ninguna |

### Matriz de formularios (pedido "100% OK") — Sprint 2

Verificados por codigo (server-side siempre revalida). [MANUAL] = requiere navegador real, ejecutado por el usuario.

**Presupuesto (alta/edicion)**
1. Sin items, click "Guardar borrador" → PASS — permitido por diseño ("Al menos 0 items" en Borrador), no bloqueado ni por CA ni por `CreateAsync`.
2. Sin items, click "Enviar al cliente" desde un Borrador ya guardado → PASS — `EnviarAsync` rechaza con "Agregue al menos un item antes de enviar el presupuesto."
3. Cliente vacio → PASS — `[Required]` + revalidacion server (`Validar()`).
4. VigenciaDias fuera de 1-365 → PASS — `[Range(1,365)]` + `Validar()` server (`<=0`).
5. Producto eliminado entre la busqueda y el submit → PASS — `ValidarProductosAsync` revalida existencia por Id antes de persistir.
6. [MANUAL] Confirmar visualmente que el buscador Select2 muestra foto/precio/stock y que el total se recalcula sin recargar (paso 1 de la checklist del implementador).

**Venta (Create — POS)**
7. Sin items, botón Confirmar → PASS — deshabilitado client-side (`carrito.length>0`) y server rechaza igual si se fuerza el POST (`itemsValidos.Count==0`).
8. Con items, sin pagos → PASS — deshabilitado client-side (`hayPagoReal`) y server rechaza (`pagosValidos.Count==0`).
9. Suma de pagos != total (parcial) → PASS — permite confirmar (`PagadaParcial`), indicador "Falta cobrar $X" en vivo, sin bloquear.
10. Suma de pagos > total (vuelto) → PASS — permite confirmar, indicador "Vuelto $X".
11. Cantidad > stock disponible → PASS — badge de advertencia amarillo no bloqueante (HU-5.8), confirmado que NO hay guard de bloqueo server-side equivalente al de M3.
12. Metodo de pago fuera de los permitidos (payload manipulado) → PASS — `MetodosPermitidosVenta.Contains` rechaza Cheque/Deposito.
13. [MANUAL] Confirmar visualmente pago combinado (Efectivo+Transferencia) sumando exacto, badge "Pago completo", pantalla de exito con los 4 botones (pasos 3, 7, 8 de la checklist del implementador — **estos son los puntos de mayor riesgo declarado, ver seccion dedicada arriba**).
14. [MANUAL] Verificar `StockActual` y movimiento de CC Local tras confirmar (pasos 4-5 de la checklist).
15. [MANUAL] Cancelar venta y verificar reversion doble (original + reversion) en Stock y CC Local (paso 9 de la checklist).
16. [MANUAL] Permisos: Vendedor accede a Ventas/Presupuestos, `Cuenta corriente` → Acceso denegado (paso 10) — verificado por codigo (`[Authorize(Policy="RequireAdministracion")]` en `CCLocalController`, `[Authorize(Policy="RequireVentas")]` en `VentasController`/`PresupuestosController`), pendiente confirmacion visual.
17. [MANUAL] Mobile: barra inferior fija en `Ventas/Create` (paso 12).

### Defectos activos

Ninguno bloqueante ni critico detectado por revision de codigo. Hallazgos registrados como observaciones/riesgos (no bugs reproducidos):
- Hallazgo de proceso (severidad **major**, no de codigo): contradiccion documental en `5-implementador.md`/`trazabilidad.md` sobre si el smoke test de Venta/stock/CC/cancelacion se ejecuto — ver seccion dedicada arriba. Requiere correccion del Implementador/orquestador, no de QA.
- Observacion (severidad **minor**, desvio a confirmar con negocio): `EstadoVenta.Pendiente` inalcanzable via `ConfirmarAsync` por el guard "al menos 1 pago > 0" — ver seccion "Observaciones".
- Riesgo residual (severidad **minor**, no reproducido): posible doble-conversion de un mismo Presupuesto por concurrencia de dos pestañas/dispositivos (sin re-chequeo de estado dentro de la transaccion de `VentaService.ConfirmarAsync`) — ver "Verificacion puntual — Convertir a venta".
- Riesgo residual heredado (ya aceptado en Sprint 1, sin cambios): sin `RowVersion`/optimistic concurrency en `Producto.StockActual` — bajo volumen de un solo local, aceptado por diseño.

**Auto-fixes aplicados**: ninguno. No se reprodujo ningun bug funcional por codigo que requiera parche (regla del rol: sin bug reproducido no se autofixea; los 2 items de arriba son observaciones/riesgos, no bugs confirmados, y se escalan en vez de adivinar el fix).

### Riesgos de liberacion

- **Medio-bajo**: el flujo critico (`Ventas/Confirmar` con pago combinado, baja de stock, movimiento de CC Local, cancelacion con reversion) esta verificado por revision de codigo profunda (sin hallar inconsistencias logicas) pero **no fue ejecutado en un navegador/entorno real** en este ciclo — ni por el implementador (pese a la nota de proceso contradictoria) ni por QA (regla del rol). Este es el riesgo de mayor impacto potencial del sprint. **Mitigacion**: checklist de 12 pasos ya dejada por el implementador en `5-implementador.md` (Presupuesto→Enviar→Aprobar→Convertir→Confirmar con pago combinado→verificar stock→verificar CC→ver Presupuesto Convertido→casos de borde→Cancelar→permisos→PDF→mobile) — el usuario debe ejecutarla antes de considerar el sprint 100% cerrado.
- **Bajo**: contradiccion documental (ver "Hallazgo de proceso") — riesgo de que alguien de el flujo por validado en caliente cuando no lo esta. Recomendado corregir `5-implementador.md`/`trazabilidad.md` para eliminar la ambiguedad.
- **Bajo**: `EstadoVenta.Pendiente` inalcanzable — confirmar con el cliente si es el comportamiento deseado (consistente con "sin fiado") o si se espera poder registrar una venta con $0 cobrado.
- **Bajo**: concurrencia de doble-conversion de Presupuesto (ver arriba) — no bloqueante para Sprint 3, recomendado endurecer en un sprint de mantenimiento.
- **Bajo, heredado**: antiforgery de `Ventas/Confirmar` (header + campo `__RequestVerificationToken` en un POST form-urlencoded con JSON embebido) sigue el mismo mecanismo ya usado por `GetData`/`LimpiarFiltros` — revisado por codigo, consistente con `Program.cs` (sin `AntiforgeryOptions.HeaderName` custom), pero la confirmacion definitiva requiere navegador real (paso 3 de la checklist).

### Pruebas minimas ejecutadas

- `dotnet build MariHogar.slnx` → Compilacion correcta, 0 errores (9 warnings preexistentes NU1902 + CS0162 ya conocidos, ninguno nuevo) — re-verificado por QA.
- `dotnet ef migrations list --project MariHogar.Infrastructure --startup-project MariHogar.Web` → `20260724145210_InitialCreate`, `20260724152806_AddCatalogo`, `20260724175804_AddPresupuestosVentas`, ninguna `(Pending)` — coincide con lo declarado por el implementador.
- Revision de codigo linea por linea de `VentaService.cs` completo (incluyendo `ConfirmarAsync`/`CancelarAsync`), `PresupuestoService.cs` completo, `CCLocalService.cs` completo, `StockService.RegistrarMovimientoAsync`, `VentasController`/`PresupuestosController`/`CCLocalController`, Views `Ventas/{Create,Index,Details}.cshtml`, `Presupuestos/{Create,Edit,Details,Index}.cshtml`, `CCLocal/Index.cshtml`, entidades Domain + enums nuevos, configuracion Fluent de `AppDbContext`, DTOs/ViewModels de los 3 modulos, `site.js`, `_Layout.cshtml`.
- Grep de patrones riesgosos (`.Contains(` sobre colecciones locales, `text/x-template`, `<datalist>`, `RequestVerificationToken`/`AntiforgeryOptions`) sobre `MariHogar.Infrastructure/Services` y `MariHogar.Web`.
- Ejecucion completa del playbook cross-proyecto (28 items del catalogo, incluidos MH-001/MH-002 de Sprint 1).

### Estado go/no-go

**GO condicionado** para habilitar Sprint 3 (Entregas, M6). Sin defectos bloqueantes ni criticos detectados por revision de codigo. Condicion recomendada (no bloqueante para empezar Sprint 3, pero si antes de considerar Sprint 2 100% cerrado ante el cliente): que el usuario ejecute la checklist de 12 pasos de `5-implementador.md`, en particular la confirmacion de Venta con pago combinado y la verificacion de stock/CC Local/cancelacion (pasos 3-5 y 9) — es el unico tramo del sprint que ni el implementador (pese a la nota contradictoria) ni QA verificaron en un entorno real. Se recomienda ademas que el orquestador/implementador reconcilien la contradiccion documental de `5-implementador.md`/`trazabilidad.md` antes de dar el sprint por cerrado formalmente.
