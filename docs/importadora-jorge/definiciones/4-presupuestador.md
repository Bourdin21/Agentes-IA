# 4 — Presupuestador · importadora-jorge

## Iteracion 2026-10-20 — Presupuesto preliminar de preventa (PRE-01)

### Gate: NO se cumple, y es deliberado

La secuencia obligatoria pide definiciones 1, 2 y 3 aprobadas antes de presupuestar. **No existen.** El lead
se califico hoy por outbound y no hubo Discovery formal. Se cotiza igual, por pedido explicito, como
**presupuesto preliminar de preventa**: numero por modulos con supuestos declarados, sujeto a relevamiento.
No habilita Implementacion. Si el cliente avanza, corre la secuencia completa antes de tocar codigo.

### Alcance relevado (fuente: conversacion de calificacion del bot, 2026-10-20)

Textual del prospecto:
- "Tiene sistema de facturacion?"
- "estoy averiguando para cambiar a un sistema online"
- "con gestion de importacion/ventas/stock"

Nota del bot: *"Hoy tienen un sistema de facturacion pero quieren pasar a uno online que integre importacion,
ventas y stock. Interesado en sistema de gestion; se menciono tambien asistente de WhatsApp."*

El gancho del outbound que respondieron fue **stock sin cuantificar y falta de proyeccion del negocio**.

### Paso 0 — Anclaje historico

Fuente: `docs/calibracion/dataset.yml` + `docs/patrones/cat_resumen.txt`.

**Proyecto de referencia dominante: `la-platense` (Ferreteria La Platense).** Es el mismo tipo de negocio a
efectos de software: comercio con catalogo, stock, proveedores que facturan en moneda extranjera, cuentas
corrientes de clientes y proveedores, ventas con IVA y facturacion. `marihogar` aporta ARCA en produccion real.

**Verificacion de la base de reutilizacion (regla 2026-10-06 — obligatoria, no declarativa).**
`grep` sobre `C:\Sistemas\Ferreteria La Platense` y `C:\Sistemas\marihogar`. Todo lo citado EXISTE:

| Pieza a reutilizar | Patron | Verificado en |
|---|---|---|
| Cuenta corriente de clientes | PAT-001 | `ICuentaCorrienteClienteService`, `MovimientoCCClienteDtos` (la-platense) |
| Cuenta corriente de proveedores | PAT-001 | `ICCProveedorService` (la-platense) |
| Documento que declara moneda y congela cotizacion | **PAT-055** | `OrdenCompraDtos`, `PagoProveedorDtos`, `ProveedorDtos` (la-platense) |
| Ordenes de compra | — | `IOrdenCompraService` (la-platense) |
| Stock: movimientos + ajuste auditado + StockVerificado | PAT-013 | `IMovimientoStockService`, `IAjusteStockService`, `StockDtos` (la-platense) |
| Ventas con IVA por linea y pago multi-medio | PAT-003 | `IVentaWorkflowService` (la-platense), ShowroomGriffin |
| Notas de credito | — | `INotaCreditoService` (la-platense) |
| Facturacion electronica ARCA | PAT-006 | `IAfipService`, `AfipSettings`, CAE (marihogar, produccion real) |
| Actualizacion masiva de precios | — | `IAumentoMasivoPrecioService` (la-platense) |

**PAT-055 es el hallazgo que mas baja el riesgo del proyecto:** un importador compra en USD y vende en pesos.
El patron ya resuelve que la cabecera del documento declare su moneda y congele la cotizacion usada, en vez de
leer el tipo de cambio de la ficha del proveedor (que es el error por defecto y rompe todo documento viejo).

**Lo unico sin base en el estudio:** el **prorrateo de costos de importacion** (flete, aduana, despachante,
seguro) sobre el costo unitario de cada item del embarque. No existe en ningun repo. Se cotiza como item
propio y con contingencia del 25 %, no escondido dentro de un modulo grande — exactamente lo que la regla
de 2026-10-06 obliga a hacer despues del desvio de La Platense Entrega 3.

### Paso 0.5 — Perfil de cliente: CONSULTA A `olvidata-ceo` (perfil atipico)

Senales de capacidad de pago establecida: **ya pagan un sistema de facturacion**, son B2B, importan maquinaria
(negocio capital-intensivo que opera en USD), tienen web propia. Es el patron de **FABINCO**, donde la
recomendacion explicita del CEO fue cotizar a precio de lista aunque el ratio calificara para descuento.
Por eso NO se aplica el tier por defecto sin consultar. Decision registrada al final de esta entrada.

### Paso 5-7 — Tabla por modulo

Formula de BUILD vigente: `Costo = M x USD 10,50` (factor 4,0 desde 2026-09-08). Tasa USD 35/h.
Contingencia variable por riesgo (8/15/25 %) aplicada una sola vez, solo al techo interno de esfuerzo.

| # | Modulo funcional | Tipo | Riesgo | O | M | P | PERT | +cont | USD lista | Reuso |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| 1 | Usuarios, roles y permisos | ABM simple | 8 % | 1,4 | 2,0 | 3,2 | 2,10 | 2,27 | 21,00 | si |
| 2 | Catalogo de maquinaria y repuestos | ABM intermedio | 8 % | 3,5 | 5,0 | 8,0 | 5,25 | 5,67 | 52,50 | si |
| 3 | Lista de precios y actualizacion masiva | ABM intermedio | 8 % | 2,0 | 3,0 | 5,0 | 3,17 | 3,42 | 31,50 | si |
| 4 | Clientes (ficha y datos fiscales) | ABM intermedio | 8 % | 2,0 | 3,0 | 5,0 | 3,17 | 3,42 | 31,50 | si |
| 5 | Cuenta corriente de clientes | financiero | 15 % | 2,0 | 3,0 | 5,0 | 3,17 | 3,64 | 31,50 | si |
| 6 | Proveedores del exterior | ABM intermedio | 8 % | 2,0 | 3,0 | 5,0 | 3,17 | 3,42 | 31,50 | si |
| 7 | Cuenta corriente de proveedores en USD | financiero | 15 % | 2,4 | 3,5 | 5,8 | 3,70 | 4,25 | 36,75 | si |
| 8 | Ordenes de compra / importacion | ABM complejo | 15 % | 4,0 | 6,0 | 10,0 | 6,33 | 7,28 | 63,00 | si |
| 9 | **Costos de importacion y prorrateo** | financiero | **25 %** | 3,5 | 5,0 | 9,0 | 5,42 | 6,77 | 52,50 | **NO** |
| 10 | Recepcion de mercaderia e ingreso a stock | workflow | 15 % | 2,4 | 3,5 | 5,8 | 3,70 | 4,25 | 36,75 | si |
| 11 | Stock: movimientos y ajuste auditado | financiero | 15 % | 3,5 | 5,0 | 8,0 | 5,25 | 6,04 | 52,50 | si |
| 12 | Ventas (IVA por linea, multi-medio) | financiero | 15 % | 4,8 | 7,0 | 11,5 | 7,38 | 8,49 | 73,50 | si |
| 13 | Facturacion y comprobantes | financiero | 15 % | 2,8 | 4,0 | 6,5 | 4,22 | 4,85 | 42,00 | si |
| 14 | Dashboard, reportes y proyeccion | reporte | 8 % | 2,8 | 4,0 | 6,5 | 4,22 | 4,55 | 42,00 | si |
| 15 | Deploy inicial y puesta en produccion | infra | 15 % | 2,0 | 2,5 | 4,0 | 2,67 | 3,07 | 26,25 | NO |
| | **Subtotal Etapa 1** | | | | **59,5** | | | | **624,75** | |
| 16 | Facturacion electronica ARCA | integracion | 25 % | 3,5 | 5,0 | 8,0 | 5,25 | 6,56 | 52,50 | si |
| 17 | Notas de credito y debito | financiero | 15 % | 2,0 | 3,0 | 5,0 | 3,17 | 3,64 | 31,50 | si |
| 18 | Busqueda global y filtros persistidos | UI | 8 % | 1,3 | 2,0 | 3,2 | 2,08 | 2,25 | 21,00 | si |
| | **Subtotal Etapa 2** | | | | **10,0** | | | | **105,00** | |
| | **TOTAL** | | | | **69,5** | | **73,4** | **83,9** | **729,75** | |

Las horas PERT+contingencia (83,9 h) son el **techo interno de esfuerzo**, no la base del precio.

### Paso 7 — Autocorreccion por item

| Item | Referencia historica | Mediana base | PERT | Ratio | Decision |
|---|---|---:|---:|---:|---|
| 2 Catalogo | ABM intermedio (4-7 h) | 5,5 | 5,25 | 0,95 | mantener |
| 5 / 7 Cuentas corrientes | PAT-001 ledger reutilizando patron | — | 3,17 / 3,70 | — | por encima del piso de "modificacion existente" (1-1,5 h) a proposito: es repo nuevo, no un ledger extra en un sistema vivo |
| 8 Ordenes de compra | ABM complejo (7,7-11,5 h) | 9,6 | 6,33 | 0,66 | **justificado**: `IOrdenCompraService` + PAT-055 ya construidos y verificados |
| 9 Prorrateo de costos | sin referencia | — | 5,42 | n/d | **incertidumbre declarada**, contingencia 25 %, item separado |
| 11 Stock | financiero (5-8 h) | 6,5 | 5,25 | 0,81 | justificado por PAT-013 verificado |
| 12 Ventas | financiero (5-8 h) | 6,5 | 7,38 | 1,14 | mantener (driver: IVA por linea + multi-medio + workflow) |
| 15 Deploy | rango deploy inicial (2-3 h) | 2,5 | 2,67 | 1,07 | mantener — respeta el piso de la alerta de subestimacion |
| 16 ARCA | Integracion ARCA (5-9 h) | 7,0 | 5,25 | 0,75 | justificado por PAT-006 en produccion real (marihogar) |

### Paso 8 — Sanity check del total

| Proyecto comparable | Horas | Modulos | h/modulo |
|---|---:|---:|---:|
| ShowroomGriffin | 86,57 | 11 | 7,87 |
| delicias-naturales | 95 | 19 | 5,00 |
| eleven-la-plata | 50 | 27 | 1,85 |
| vinosefue | 30 | 16 | 1,88 |
| **Mediana** | | | **3,44** |
| **importadora-jorge** | **69,5** | **18** | **3,86** |

**Ratio 1,12** — dentro del rango 0,80-1,20. El total no requiere recalibracion.

### Paso 9 — Cierre numerico por dos pasos

- **Paso A (preliminar):** Subtotal de lista USD 729,75 (Etapa 1: 624,75 · Etapa 2: 105,00).
- **Paso B (final del metodo):** sin cambios por sanity check. Contingencia aplicada una sola vez.
  Subtotal de lista **USD 729,75**.

### Descuentos — calculo de ambos ejes

- **R (reutilizacion)** = (69,5 - 7,5) / 69,5 = **89,2 %** → Tier 1 (R >= 70 %) = **30 %**.
  Items sin reuso: #9 prorrateo (5,0 h) y #15 deploy (2,5 h).
- **Volumen** = Subtotal_lista USD 729,75 → tier V1 (600-1.200) = **5 %**.
- **MAX(30 %, 5 %) = 30 %** — nunca se suman.
- Tokens IA se calcula siempre sobre el subtotal SIN descontar: 729,75 x 0,25 = **USD 182,44**.

| Escenario | Desarrollo | Tokens IA | Total | Nota |
|---|---:|---:|---:|---|
| A — precio de lista | 729,75 | 182,44 | USD 912,19 | criterio FABINCO, perfil B2B |
| B — con 30 % de descuento | 510,82 | 182,44 | USD 693,26 | queda bajo el piso → USD 800 |

**Observacion elevada al CEO:** el descuento del 30 % solo mueve el precio de 912 a 800 (-12 %), porque el
piso de Build (USD 800) lo comprime: se regala el tier casi sin efecto sobre el cierre. Ademas el resultado
queda por debajo del rango tipico de Build del estudio (USD 1.200-2.500) para un sistema de gestion completo,
y muy por debajo del research de mercado del 2026-10-13 (agencias argentinas USD 5.000-15.000 por un agente
integrado; gestorias Espana EUR 9.000-15.000).

### DECISION COMERCIAL — `olvidata-ceo`, 2026-10-20

Consulta elevada por Paso 0.5 (perfil atipico). Respuesta:

1. **Escenario A — precio de lista, sin descuento de expansion.** Mismo criterio que FABINCO (COM-020): no se
   regala tier de expansion a un cliente que ya paga software y tiene presupuesto establecido.
2. **Numero comercial fijado en USD 1.200** — el piso vigente del rango de Build, NO los USD 912 que da la
   formula. Motivo: el calculo formal queda por debajo del rango tipico (1.200-2.500) para un sistema que es
   multi-moneda + ARCA + stock + importacion; es mas complejo que La Platense (1.500) y que ganaderia (650,
   sin multi-moneda ni ARCA). **Se documenta como numero comercial fijado, no como resultado del metodo** —
   patron habitual de Joaquin, ambos numeros quedan registrados (formula USD 912,19 / comercial USD 1.200).
3. **Mantenimiento: EXCEPCION a la regla de ano 1 gratis.** Se cobra desde el ano 1: PREMIUM USD 600/ano.
   Mismo criterio que FABINCO (perfil con capacidad de pago), no el de Peras del Olmo.
4. **Asistente de WhatsApp: entra en la misma propuesta como setup aparte, sin recurrente propio** (COM-021).
   Al vivir dentro de este mismo Build (mismo hosting y deploy), el recurrente se funde en el plan de
   mantenimiento en vez de duplicar abono. Setup tier Starter/Pro: **USD 700-1.200** segun volumen esperado —
   el numero exacto depende de las preguntas de relevamiento abiertas.

**Total de la propuesta:** USD 1.200 desarrollo + USD 700-1.200 setup WhatsApp + USD 600/ano de mantenimiento
desde el ano 1. Pago 50/50 por etapa en el Build.

### Paso 10 — Costo interno de IA (SOLO ESTUDIO — nunca al cliente)

Horas facturables = M / 4,0 x 1,20 = M x 0,30 → total **20,85 h**.
`Costo_IA_modulo` = horas facturables x USD 4/h (Opus) → **USD 83,40** en total.
`Costo_IA_overhead_proyecto` = 4 h Ask-mode x USD 1/h = **USD 4,00**.
**Total costo sombra: USD 87,40.**

Chequeo del umbral del 15 %: `Costo_IA_modulo / precio de lista` = (M x 0,30 x 4) / (M x 10,50) = **11,4 %**,
constante para todos los modulos. **Por debajo del 15 % → ningun modulo requiere ajuste de precio.**
Margen sobre el numero comercial de USD 1.200: **USD 1.112,60** (sin contar el setup de WhatsApp).

### Plan de mantenimiento

Conteo de **tablas de negocio** (unico factor del plan — la cantidad de usuarios NO lo modifica, nunca):
Producto, Categoria, UnidadMedida, ListaPrecio, Cliente, CuentaCorrienteCliente, MovimientoCCCliente,
Proveedor, CuentaCorrienteProveedor, MovimientoCCProveedor, OrdenCompra, OrdenCompraDetalle, CostoImportacion,
Recepcion, RecepcionDetalle, MovimientoStock, AjusteStock, Venta, VentaDetalle, VentaPago, Comprobante,
NotaCredito, ComprobanteAfip, Moneda/Cotizacion, Configuracion, Parametro → **~26 tablas**.

→ Plan **PREMIUM** (16-30 tablas) = **USD 600/ano + IVA**, cobrado **desde el ano 1** por decision explicita
del CEO (excepcion documentada a la regla de 2026-08-27).

### Riesgos y supuestos

**Supuestos declarados** (ninguno confirmado por el cliente — todos son gatillo de reestimacion):
1. Un solo punto de venta / deposito. **Multi-deposito no esta cotizado.**
2. Volumen de operacion de comercio chico-mediano; sin requisitos de performance especiales.
3. Importan con despachos propios y cargan los costos a mano. **No hay integracion con despachante ni Aduana.**
4. Facturan en pesos; compran en USD. Una sola moneda extranjera.
5. No hay alquiler de maquinaria en el alcance, aunque el rubro del CRM lo menciona — el cliente no lo pidio.
6. El sistema actual se apaga; no hay operacion en paralelo.

**Riesgos**:
- **R1 (alto):** el prorrateo de costos de importacion no tiene base en el estudio. Es el unico item sin
  precedente verificado y el de mayor contingencia (25 %).
- **R2 (alto):** la **migracion de datos del sistema actual** esta EXCLUIDA y es el riesgo clasico de este
  perfil. PAT-012 (preview → confirmar) existe, pero el precedente de La Platense Entrega 3 muestra que un
  import mal relevado multiplica x2,4 el modulo que lo contiene. Si lo piden, va como entrega propia con
  relevamiento previo, nunca adentro de otro modulo.
- **R3 (medio):** condicion de IVA y tipo de comprobante de un importador pueden exigir reglas fiscales que
  no salieron en la calificacion.
- **R4 (medio):** el alcance viene de una charla de bot, no de un Discovery. Puede moverse entero.

### Preguntas abiertas de relevamiento (gatillo de reestimacion)

1. Cuantos depositos / sucursales.
2. Cuantos usuarios van a operar el sistema.
3. Que sistema de facturacion usan hoy y si se puede exportar el catalogo, clientes y saldos.
4. Facturan electronicamente hoy (ARCA)? Que punto de venta y tipos de comprobante.
5. Compran en una sola moneda o en varias.
6. Como cargan hoy los costos de importacion y si quieren prorrateo automatico sobre el costo unitario.
7. Alquilan maquinaria ademas de venderla (el rubro del CRM lo sugiere).
8. Volumen aproximado: items de catalogo, ventas por mes, embarques por ano.
9. Volumen esperado de consultas de WhatsApp (define el tier del asistente, USD 700 vs 1.200).

### Exclusiones

- Migracion de datos desde el sistema anterior (ver R2 — se cotiza aparte con relevamiento propio).
- Configuracion y costo del servidor / hosting.
- Aplicacion movil.
- Integracion con hardware (lectoras, balanzas, impresoras fiscales).
- Integracion con despachante de aduana o sistemas aduaneros.
- Alquiler de maquinaria.
- Cambios de alcance posteriores al inicio.

---

## Iteracion 2026-10-20 (bis) — REVISION PRE-02: el rubro del CRM estaba mal

**Disparador:** research del sitio del cliente (`importadorajorge.com.ar`) antes de mandar la propuesta.
**La hipotesis de negocio sobre la que se construyo PRE-01 es falsa.** PRE-01 no se borra: queda como
entrada superada en su parte de alcance. Los pasos de metodo (anclaje, verificacion de reuso, costo de IA)
siguen siendo validos.

### Lo que dice el sitio (fuente: paginas publicas, leidas el 2026-10-20)

| Dato | Valor |
|---|---|
| Que venden | **Importadora mayorista poli-rubro**: bazar, jugueteria, libreria, cosmetica, electronica, fitness, kiosco, deco-hogar, Winco, Bervit. Marcas: Tramontina, Nadir, Marinex, Yoly Bell, Filgo |
| **NO venden** | **maquinaria** — el rubro del CRM ("Comercio o alquiler de maquinaria") esta MAL |
| Trayectoria | **mas de 70 anos**, negocio familiar ("comenzo vendiendo en esta misma cuadra mi abuela Zulema") |
| Modelo | **mayorista a comercios y revendedores**, con venta al publico por el sitio |
| Catalogo | **1.604 productos**, 11 rubros, con SKU propio, 134 paginas de 12 |
| Unidad de venta | por **bulto y por unidad** ("VASO VALENCIA TL **X6 E/CAJA** X1") |
| Stock | **no se muestra en el sitio** |
| Precios | en pesos, visibles, una sola lista publicada |
| Minimos | **$200.000** para envio, **$50.000** para pedido |
| Medios de pago | transferencia a 2 bancos (Credicoop, BBVA) y efectivo al retiro. **Sin tarjetas ni cuotas** |
| Logistica | envios **al interior**, despacho a la central del transporte (el cliente paga el flete desde ahi). Retiro en el local |
| Local | Sarmiento 2444, Once, CABA. Sin sucursales ni deposito declarado |
| Sitio | **e-commerce a medida con carrito, en produccion**, desarrollado por un tercero (`kirke.ws`) |

### Que cambia en el alcance

**Se cae:** el modulo de alquiler de maquinaria ya estaba excluido, ahora es irrelevante. El gancho del
outbound ("stock de maquinaria") no describe el negocio.

**Se agranda:**
- **Catalogo (#2).** 1.604 SKUs en 11 rubros con bulto/unidad no es el ABM que se cotizo. Driver nuevo:
  unidad de venta y conversion bulto↔unidad. **Base verificada:** `UnidadMedidaMapper` e
  `IUnidadMedidaConversionService` existen en la-platense.
- **Doble lista de precios mayorista/minorista.** No estaba cotizado. Base parcial: `IAumentoMasivoPrecioService`
  (la-platense) y PAT-021 (modo de precio por item).
- **Ventas (#12).** Se SIMPLIFICA: sin tarjetas ni cuotas, el multi-medio es transferencia + efectivo.
- **Minimos de compra** ($200.000 / $50.000) como regla de negocio del pedido. Item chico, no estaba.

**Aparece de cero (lo mas importante y lo mas riesgoso):**
- **Sincronizacion de stock y precios con el e-commerce existente.** Hoy el sitio no publica stock: es el
  agujero mas visible del negocio y probablemente lo que mas valor les mueve. **ATENCION (regla 2026-10-06):
  PAT-036 esta DISENADO, NO CONSTRUIDO** (`libreria-horizonte`, en diseno). **No se puede cotizar como reuso.**
  Ademas depende de un tercero: hay que ver si `kirke.ws` expone API o acceso a la base del sitio. Es
  dependencia externa, igual que la habilitacion de acceso en la integracion KOI/Ayres — se cotiza como
  riesgo propio, no como mapeo de endpoints.
- **Expedicion / envios al interior** con despacho a transporte. No estaba cotizado.
- **Migracion del catalogo.** Deja de ser una exclusion comoda: **nadie carga 1.604 SKUs a mano**. Pasa de
  riesgo R2 a necesidad casi segura. Se mantiene como entrega propia con relevamiento previo — el precedente
  de La Platense Entrega 3 (item de import sin base, x2,4 sobre el modulo que lo contenia) aplica entero.

### Impacto en el numero — ESTIMACION GRUESA, no cotizacion

| Concepto | Delta M (h) |
|---|---:|
| Catalogo con 1.604 SKU y bulto/unidad | +2 |
| Doble lista mayorista/minorista | +3 |
| Minimos de compra | +0,75 |
| Expedicion y envios al interior | +3,5 |
| Sincronizacion con el e-commerce (sin base construida, riesgo 25 %) | +9 |
| Migracion del catalogo (entrega propia, a relevar) | +7 |
| Ventas sin tarjetas ni cuotas | −1 |
| **Delta total** | **+24,25** |

M pasaria de **69,5 a ~93,8 h** → lista ~USD 985 → con Tokens IA ~USD 1.231. Con el mismo criterio comercial
que aplico el CEO en PRE-01 (precio de lista, numero comercial por encima de la formula, perfil con capacidad
de pago), la zona razonable pasa de USD 1.200 a **USD 1.800-2.200**, dentro del rango tipico de Build.

**Esto NO es una cotizacion.** Es la magnitud del desvio. El numero formal exige responder antes las
preguntas abiertas, que ahora son otras.

### Preguntas de relevamiento — REEMPLAZAN a las de PRE-01

1. El sitio actual (`kirke.ws`): se queda, se reemplaza o se integra? **Si se integra, tienen acceso a la base
   o API?** Esto decide el item mas caro del proyecto.
2. Los 1.604 SKUs: en que estan hoy — en el sistema de facturacion, en el sitio, en Excel? Se pueden exportar?
3. Manejan precio mayorista y minorista distintos, o lista unica con descuento por volumen?
4. Como manejan el bulto: venden solo por bulto cerrado o tambien fraccionado?
5. Cuentas corrientes a comercios y revendedores: existen hoy? Como las llevan?
6. Importan directo: cuantos embarques por ano y como reparten hoy los costos (flete, aduana, despachante)?
7. Cuantas personas van a usar el sistema y con que roles.
8. Un solo deposito en Sarmiento 2444, o hay otro?
9. Los envios al interior: quieren seguimiento del despacho dentro del sistema?

### Accion pendiente sobre el CRM

El contacto esta clasificado como **"Comercio o alquiler de maquinaria"**, que es incorrecto. Corregirlo
(poli-rubro / mayorista importador) para no volver a calificar mal a este contacto ni a otros de la misma
campana. **No se toco el CRM productivo desde esta sesion** — requiere decision de Joaquin.

---

## Iteracion 2026-10-20 (ter) — PRE-03: recotizacion sobre el alcance real

Reemplaza los numeros de PRE-01 (construido sobre el rubro equivocado) y concreta la estimacion gruesa de
PRE-02. Metodo identico; cambia el WBS.

**Dato nuevo de Joaquin:** el sistema **ya esta armado y en produccion para la ferreteria** (la-platense).
El Build es adaptacion, no construccion: por eso los 14 modulos con base verificada van con M bajo. Lo que
cuesta es lo que ese sistema no tiene.

### Tabla por modulo

Formula de BUILD: `Costo = M x USD 10,50`. Contingencia variable aplicada una sola vez, solo al techo interno.

| # | Modulo funcional | Riesgo | O | M | P | PERT | +cont | USD lista | Base |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| 1 | Puesta en marcha: instancia, usuarios y roles | 8 % | 2,0 | 3,0 | 5,0 | 3,17 | 3,42 | 31,50 | si |
| 2 | Catalogo poli-rubro con SKU y bulto/unidad | 15 % | 3,5 | 5,0 | 8,0 | 5,25 | 6,04 | 52,50 | si |
| 3 | Listas de precios mayorista y minorista | 15 % | 2,8 | 4,0 | 6,5 | 4,22 | 4,85 | 42,00 | si |
| 4 | Clientes (comercios y revendedores) + cta cte | 8 % | 2,8 | 4,0 | 6,5 | 4,22 | 4,55 | 42,00 | si |
| 5 | Proveedores del exterior + cta cte en USD | 15 % | 2,4 | 3,5 | 5,8 | 3,70 | 4,25 | 36,75 | si |
| 6 | Ordenes de compra / importacion (moneda congelada) | 15 % | 3,5 | 5,0 | 8,0 | 5,25 | 6,04 | 52,50 | si |
| 7 | Costos de importacion y prorrateo | 25 % | 3,5 | 5,0 | 9,0 | 5,42 | 6,77 | 52,50 | **NO** |
| 8 | Recepcion de mercaderia e ingreso a stock | 15 % | 2,0 | 3,0 | 5,0 | 3,17 | 3,64 | 31,50 | si |
| 9 | Stock: movimientos y ajuste auditado | 15 % | 3,0 | 4,5 | 7,2 | 4,70 | 5,40 | 47,25 | si |
| 10 | Ventas mayoristas con minimos de compra | 15 % | 3,8 | 5,5 | 9,0 | 5,80 | 6,67 | 57,75 | si |
| 11 | Facturacion y comprobantes | 15 % | 2,4 | 3,5 | 5,8 | 3,70 | 4,25 | 36,75 | si |
| 12 | Expedicion: envios al interior y despacho | 15 % | 2,4 | 3,5 | 5,8 | 3,70 | 4,25 | 36,75 | **NO** |
| 13 | Tablero y reportes de gestion | 8 % | 2,4 | 3,5 | 5,8 | 3,70 | 4,00 | 36,75 | si |
| 14 | Migracion del catalogo (1.604 SKU) | 25 % | 4,5 | 7,0 | 12,0 | 7,42 | 9,27 | 73,50 | **NO** |
| 15 | Deploy inicial y puesta en produccion | 15 % | 2,0 | 2,5 | 4,0 | 2,67 | 3,07 | 26,25 | **NO** |
| | **Subtotal Etapa 1** | | | **62,5** | | | | **656,25** | |
| 16 | Sincronizacion de stock y precios con la tienda | 25 % | 6,0 | 9,0 | 16,0 | 9,67 | 12,08 | 94,50 | **NO** |
| 17 | Facturacion electronica ARCA | 25 % | 3,5 | 5,0 | 8,0 | 5,25 | 6,56 | 52,50 | si |
| 18 | Notas de credito y debito | 15 % | 2,0 | 3,0 | 5,0 | 3,17 | 3,64 | 31,50 | si |
| 19 | Busqueda global y filtros persistidos | 8 % | 1,3 | 2,0 | 3,2 | 2,08 | 2,25 | 21,00 | si |
| | **Subtotal Etapa 2** | | | **19,0** | | | | **199,50** | |
| | **TOTAL** | | | **81,5** | | **86,2** | **101,0** | **855,75** | |

### Diferencias de alcance contra PRE-01

| Cambio | Motivo |
|---|---|
| **+ Listas mayorista y minorista** | venden a comercios y revendedores, no solo al publico |
| **+ Expedicion de envios al interior** | despachan a central de transporte, el cliente paga el flete |
| **+ Migracion del catalogo (1.604 SKU)** | deja de ser exclusion: nadie los carga a mano |
| **+ Sincronizacion con la tienda existente** | el e-commerce de kirke.ws no publica stock. Es el gancho de venta |
| **+ Minimos de compra** (dentro de Ventas) | $200.000 envio / $50.000 pedido son regla de negocio |
| **Ventas se simplifica** | sin tarjetas ni cuotas: solo transferencia y efectivo |
| **− Alquiler de maquinaria** | nunca existio. Venia del rubro mal clasificado |

### Descuentos y escenarios

- **R = 66,9 %** (54,5 h con base / 81,5 h totales) → **tier 2 = 15 %**. Bajo desde el 89,2 % de PRE-01 porque
  lo nuevo pesa mas: 5 items sin base construida (#7, #12, #14, #15, #16) suman 27 h.
- Volumen: Subtotal_lista USD 855,75 → V1 = 5 %. **MAX(15 %, 5 %) = 15 %.**
- Tokens IA = 855,75 x 0,25 = **USD 213,94** (sobre lista, sin descontar).

| Escenario | Total |
|---|---:|
| A — precio de lista | **USD 1.069,69** |
| B — con 15 % | USD 941,32 |

### Sanity check del total — fuera de rango, justificado

4,29 h/modulo contra mediana 3,44 de los comparables → **ratio 1,25**, por encima del tope de 1,20.
No se recalibra a la baja: los 5 items sin base construida (migracion de 1.604 SKU y sincronizacion con un
sitio de terceros entre ellos) son estructuralmente mas pesados que el modulo promedio del historial, que es
casi siempre un ABM con patron disponible. Forzar el ratio a 1,20 seria recortar justo donde esta el riesgo.

### Costo interno de IA (SOLO ESTUDIO)

Horas facturables = 81,5 x 0,30 = **24,45 h**. Costo sombra = 24,45 x USD 4 + USD 4 de overhead = **USD 101,80**.
Umbral: 11,4 % del precio de lista por modulo, constante → **por debajo del 15 %, ningun ajuste de precio**.

### El riesgo que define esta cotizacion

**#16, sincronizacion con la tienda, es a la vez el item mas caro, el mas riesgoso y el argumento de venta.**
- PAT-036 esta **disenado, no construido** → no se cotiza como reuso (regla 2026-10-06).
- **Depende de un tercero sin control nuestro:** que `kirke.ws` exponga API o de acceso a la base del sitio.
  Mismo perfil que la integracion KOI/Ayres, donde el riesgo dominante fue la habilitacion de acceso y no el
  mapeo de endpoints.
- Si el acceso no aparece, el item no se puede hacer al precio cotizado y hay que reencuadrar la venta entera.
  **Es la primera pregunta de la reunion, antes que cualquier otra.**

### Decision comercial

Elevada a `olvidata-ceo` el 2026-10-20 junto con la pregunta de como partir Etapa 1 / Etapa 2 (el gancho de
venta esta hoy en Etapa 2), el criterio de mantenimiento y el empaquetado del asistente de WhatsApp, que
cotiza `olvidata-presupuesto-bot` por separado. **Pendiente al momento de escribir.**

### DECISION COMERCIAL PRE-03 — `olvidata-ceo`, 2026-10-20

| Punto | Decision |
|---|---|
| **Numero comercial** | **USD 1.900** (formula daba USD 1.069,69 a lista). Elegido por debajo del techo del rango 1.800-2.200 **a proposito**: la pieza mas cara depende de un tercero que no controlamos |
| **Descuento** | ninguno — precio de lista, criterio FABINCO sostenido |
| **Particion** | la sincronizacion con la tienda **sube a Etapa 1**: es el gancho de venta y no puede leerse como "eso viene despues" |
| **Clausula Kirke** | de **alcance**, no de cobro (opcion (c) de tres planteadas). 10 dias para confirmar acceso. Sin acceso, la pieza sale y el total baja a **USD 1.690**, explicito en la propuesta como "alcance B" — no se deja abierto. Esa pieza se cotiza aparte el dia que haya acceso: no se regala ni se mete gratis |
| **Pago** | 50/50 por etapa para todo el proyecto. El 70/30 que se planteo primero quedo descartado: cobrar el 70 % de una pieza que todavia no se sabe si se puede construir crea un problema peor que el que evitaba |
| **Mantenimiento** | PREMIUM USD 600/ano **desde el ano 1**, sin ano gratis. Mismo criterio que PRE-01 |
| **Asistente de WhatsApp** | **fuera** del numero de 1.900, como item opcional aparte. Lo cotiza `olvidata-presupuesto-bot` |

**Reparto del numero comercial al cliente.** Factor sobre precio de lista = 1.900 / 855,75 = **2,2203**
(incluye los Tokens IA ya distribuidos; el cliente ve solo el precio final por area, nunca el factor).
Etapa 1 = USD 1.666 · Etapa 2 = USD 234. Alcance B (sin la sincronizacion) = **USD 1.690**.

**Numeros que conviven, ambos vigentes:** formula USD 1.069,69 / comercial USD 1.900. El comercial no corrige
a la formula: la formula mide esfuerzo, el comercial mide lo que vale en el mercado un sistema que ya existe
andando. Margen sobre costo sombra de IA (USD 101,80): **USD 1.798,20**.

**Documento al cliente:** `presupuesto-cliente.md`, reescrito entero (el anterior describia una importadora
de maquinaria). Formato de la instruccion 31. El costo interno de IA no aparece ni se menciona.

### 2026-10-20 — Asistente de WhatsApp: FUERA DEL ALCANCE (decision de Joaquin)

Supera la linea "item opcional aparte" de la tabla de decision de PRE-03. **La propuesta lleva solo el
sistema de gestion.** `presupuesto-cliente.md` no lo menciona en ninguna parte, ni como opcional.

La cotizacion de `olvidata-presupuesto-bot` queda archivada aca por si el cliente lo pide mas adelante:

- **MVP, ofrecible ya** (no depende del sistema): minimos de compra, medios de pago, politica de envio al
  interior, y catalogo con derivacion a humano reutilizando el patron `escalar_a_humano` que ya corre en
  produccion en el bot del CRM — nunca inventa precio ni stock. **Setup tier Starter, USD 700-900.**
- **FULL** (stock y precio en vivo por SKU, chequeo del minimo contra el pedido): depende del sistema de
  gestion andando. **Setup tier Pro USD 900-1.200, mas el conector, que no esta incluido** (Simple/Media/
  Compleja USD 500/900/1.500).
- **Sin abono propio** (COM-021): vive sobre el mismo hosting, se funde en el mantenimiento del Build.

**Advertencia que vale guardar:** el tier FULL **no tiene precedente construido**. El unico chatbot LLM en
produccion del estudio es el de calificacion outbound del CRM, que por diseno **nunca** consulta stock ni
precio de un sistema externo ni cotiza (tiene guardas explicitas). Venderlo como feature estandar seria
enganoso: es desarrollo nuevo con riesgo, igual que el modulo #16 de sincronizacion con la tienda.

---

## Iteracion 2026-10-20 (quinquies) — PRE-04: Kirke se da de baja, el alcance se achica

**Dato del cliente:** van a **dar de baja el sitio de Kirke**. La idea pasa a ser resolver catalogo y stock
con nuestro sistema. **Decision de Joaquin: solo sistema interno, sin web publica** — no se construye tienda
de reemplazo.

Antes de cotizar se busco antecedente de catalogo publico / e-commerce en el repo: **no existe**. Los
"carritos" del historial (FABINCO HU-05, desborder-sin-gluten) son carritos de **punto de venta interno**,
no tiendas de cara al cliente final. Si en el futuro piden canal online, es desarrollo sin base y se cotiza
aparte — no se promete como extension barata de este sistema.

### Cambio sobre PRE-03

| | PRE-03 | PRE-04 |
|---|---:|---:|
| Modulos | 19 | **18** |
| M total | 81,5 h | **72,5 h** |
| Subtotal de lista | USD 855,75 | **USD 761,25** |
| R (reutilizacion) | 66,9 % (tier 2) | **75,2 % (tier 1)** |
| h/modulo vs mediana 3,44 | 4,29 → ratio **1,25** (fuera de rango) | 4,03 → ratio **1,17** (dentro) |
| Total a precio de lista | USD 1.069,69 | **USD 951,56** |
| **Numero comercial** | USD 1.900 | **USD 1.690** |

Sale el modulo #16 (sincronizacion de stock con la tienda, M=9, el unico que dependia de un tercero).

**Tres efectos colaterales, todos buenos:**
1. **Desaparece la dependencia de `kirke.ws`** y con ella la clausula de alcance a 10 dias. El precio es uno
   solo y cerrado: ya no hay alcance A/B.
2. **R vuelve al tier 1** (75,2 %): el item sin base mas grande era justamente el que se fue.
3. **El sanity check entra en rango** (1,17 contra 1,25). PRE-03 estaba fuera de rango por ese mismo item.

**Numero comercial USD 1.690:** no es una decision nueva — es exactamente el valor que `olvidata-ceo` ya habia
fijado el 2026-10-20 para el escenario "sin la pieza de sincronizacion". Se aplica sin volver a consultar
porque el escenario es identico al previsto. Factor sobre lista = 1.690 / 761,25 = **2,2200**
(Etapa 1 USD 1.457 · Etapa 2 USD 233). Mantenimiento PREMIUM USD 600/ano desde el ano 1, sin cambios.

Costo sombra de IA: **USD 91,00** (21,75 h facturables). Umbral 11,4 %, sin ajuste. Margen **USD 1.599**.

### Lo que hay que decirle al cliente, y esta en la propuesta

Al apagar el sitio **se quedan sin canal de venta online**, y este sistema no lo reemplaza: es de uso interno.
Quedo escrito en "Que no esta incluido", redactado como algo que se puede hacer aparte si lo quieren, no como
carencia. **No se esconde**: es la consecuencia mas importante de la decision que acaban de tomar.

Ademas se agrego un pedido con fecha implicita: **exportar el catalogo antes de dar de baja el sitio.** Si lo
apagan sin bajar los 1.604 productos, la carga inicial se complica y encarece.

---

## 2026-10-20 — PRE-05: REENCUADRE. El Build sale; el producto es un agente de importaciones

PRE-01 a PRE-04 quedan **superadas en su totalidad**: cotizaban un sistema de gestion que el cliente no
necesita. Se conservan como registro del razonamiento, no como propuesta vigente.

### Decision de `olvidata-ceo` (2026-10-20)

| Punto | Decision |
|---|---|
| **Encuadre** | **AI Agents, agente bespoke standalone** — NO licencia de rubro. No existe nucleo "importadora mayorista" y no tiene sentido vender una licencia de rubro por un solo agente de un solo cliente. Si aparece un segundo importador, **este pasa a ser el piloto que arma el nucleo** (mecanismo del punto 5 del rediseno 2026-10-13) |
| **Tier** | **Basico**: es un proceso unico (parseo + normalizacion + prorrateo + export) **sin integracion directa** al sistema del cliente — entrega listo para carga manual. Si despues piden integracion directa, sube de tier con la regla ya escrita (paga diferencia de setup + recurrente del tier nuevo) |
| **Precio** | **Setup USD 1.500-2.500** (promo hasta 31/12) **+ USD 2.400/ano** de recurrente |
| **Sistema de gestion** | **Sale de la conversacion.** No queda como Etapa 2. Esteban, que es quien opera, dice que el stock le funciona bien: no hay dolor ahi. Ofrecer reemplazo de algo que no esta roto viola **COM-002** (no se arranca por el dolor) y compite contra nuestro propio pitch del agente. Queda dormido, no enterrado: si aparece un dolor real de gestion **no inducido por nosotros**, se evalua Build aparte |
| **Interlocutor** | **Seguir con Esteban.** Es el lead caliente, entro por **Ads pagos** (ya pagado) y ya pidio propuesta. El hilo de "Equipo" se archiva sin mandarle la cotizacion del sistema completo; sirve a lo sumo para confirmar quien decide |

**Advertencia de metodo del CEO, anotada para no repetir el error:** *no usar la tasa de modulos de Build
(M x USD 10,50) para cotizar un agente standalone* — esa tasa esta pensada para un modulo dentro de un
sistema grande y **subestima** un producto que vive solo. Por eso el numero sale del catalogo de AI Agents
y no del WBS por horas.

### Lo que falta para cerrar el numero dentro del rango

El rango 1.500-2.500 lo define la complejidad del parser, y **no se puede estimar sin ver una planilla real**
(la fila del dataset "Parser Excel propietario" existe justamente porque el formato manda sobre el esfuerzo).
Preguntas abiertas, en orden de importancia:

1. **Una planilla de importacion real** (invoice o packing list de un embarque), aunque sea anonimizada.
   Es el insumo que define el precio.
2. Cuantos proveedores del exterior y **cuantos formatos distintos** de planilla. Un parser por formato.
3. Como reparten hoy los costos: por valor, por peso o por unidad.
4. En que formato necesita el archivo de salida para cargarlo en su sistema actual, y **cual es ese sistema**.
5. Cuantos embarques por ano (define si el recurrente tiene sentido para ellos).
6. Que parte hace hoy Claude en el proceso y que parte Excel — donde esta el trabajo manual real.

### Nota de riesgo

El cliente **ya usa Claude** para esto. No llega virgen: tiene criterio formado sobre lo que una IA puede y
no puede hacer con sus planillas, y probablemente ya probo lo facil. **El valor no esta en "usamos IA"** —
eso ya lo tiene gratis— sino en que el proceso quede repetible, auditable y sin copiar y pegar entre
ventanas. El pitch tiene que atacar eso, no la novedad de la IA.
