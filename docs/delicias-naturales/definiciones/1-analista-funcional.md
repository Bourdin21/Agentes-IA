# Memoria - Analista funcional

## Proyecto: delicias-naturales
## Ultima actualizacion: sesion Dashboard Ampliado

## Contexto del sistema

**Stack:** ASP.NET MVC / .NET Framework 4.7.2 / EF 6 / MySQL  
**Entidades:** 26 | **Controladores:** 19 | **Migraciones EF:** 25+  
**Integraciones:** AFIP x5, SignalR, PDF  

### Modulos existentes confirmados
| Modulo | Controller | Estado |
|---|---|---|
| Dashboard | DashboardController | Existente — 2 reportes (Ventas, Productos) |
| Ventas | VentasController | Existente |
| Clientes | ClientesController | Existente |
| Productos | ProductosController | Existente |
| Pagos | PagosController | Existente |
| Compras | ComprasController | Existente |
| Proveedores | ProveedoresController | Existente |
| Cajas | CajasController | Existente |
| Pedidos | PedidosController | Existente |
| Facturas | FacturasController | Existente (AFIP) |
| Recetas | RecetasController | Existente |
| Solicitudes Ingreso Stock | SolicitudesIngresoStockController | Existente |

### Modelo de datos clave
- **Venta**: fecha, total, estado (Ingresada/Finalizada/Facturada), clienteId, pagos, productosVenta
- **ProductoVenta**: ventaId, productoId, cantidad, precioUnitario, descuento, recargo, subtotal, condIVA
- **Producto**: nombre, codigo, unidadMedida (Kg/Unidades/Gramos), precio, precioCompra, margen, stock, categoriaId
- **Pago**: fecha, monto, metodoPago (Efectivo/Credito/Debito/MercadoPago/Transferencia/SaldoFavor), ventaId
- **Cliente**: nombre, CUIT, condicionIVA, telefono, email, ventas[]
- **Compra**: fecha, estado (Pendiente/Recibida/Pagada), proveedorId, productosCompra, totalCompra
- **Caja**: tipo (Chica/Grande), estado (Abierta/Cerrada), montoInicial, montoFinal, movimientos[]
- **MovimientoCaja**: tipo (Egreso/Ingreso/Apertura/Cierre/Transferencia), origen (Venta/Compra/Gasto/Pedido)
- **Pedido**: fecha, estado (Pendiente/Aprobado/Rechazado/ListoParaRetirar), clienteId, ventaId, total

---

## Sesion: Dashboard Ampliado

### Pedido del cliente
> "Que el Dashboard tenga mas informacion. Filtro por producto (ej. almendras: kilos y plata, de-tal-fecha a tal-fecha). De clientes, no solo los mejores sino todos, cuanto compra cada uno, cuanto paga, cuanto debe."

### Decisiones confirmadas
| Pregunta | Decision |
|---|---|
| P1 — Metricas detalle producto | Hipotesis B: cantidad + monto + precio promedio + tabla clientes + grafico diario |
| P2 — Calculo deuda cliente | Hipotesis A: historico total. SaldoFavor reduce deuda. Si pagado > comprado → saldo a favor $X |
| P3 — Periodo vista clientes | Hipotesis A: siempre historico, sin filtro de fechas |
| P4 — Unidad cantidad producto | Hipotesis A: unidad de venta (bolsas, unidades, kg) |
| P5 — Bloques adicionales | Pedidos (Bloque F) + Rentabilidad (Bloque G) — ambos en alcance |

### Alcance funcional aprobado
| ID | Reporte | Ruta | Tipo |
|---|---|---|---|
| RF-D01 | Detalle por Producto especifico | Dashboard/Producto | Reporte nuevo |
| RF-D02 | Historial completo de Clientes con deuda | Dashboard/Clientes | Reporte nuevo |
| RF-D03 | Pedidos: estados y conversion | Dashboard/Pedidos | Reporte nuevo |
| RF-D04 | Rentabilidad: margen bruto real | Dashboard/Rentabilidad | Reporte nuevo |
| RF-D05 | Index Dashboard actualizado | Dashboard/Index | Mejora modulo existente |

### Deuda tecnica identificada
| ID | Descripcion | Tratamiento |
|---|---|---|
| DT-01 | ProductoSimpleViewModel.CantidadVendida es int; modelo tiene decimal. Trunca kg en informe existente. | Absorbida en RF-D01 sin costo adicional. Eleva M de 2.0h a 2.5h. |

### Reglas funcionales acordadas
- Deuda del cliente = SUM(Venta.Total) - SUM(Pago.Monto) sobre historial completo, nunca negativa
- Si totalPagado > totalComprado: Deuda = 0, SaldoAFavor = diferencia
- Pagos con MetodoPago = SaldoFavor se incluyen en totalPagado (reducen deuda)
- Reporte de Clientes no tiene filtro de fechas: datos siempre historicos
- Cantidad vendida se muestra en la unidad de venta del producto (kg, unidades, gramos)
- PrecioCompra en Rentabilidad es el precio actual, no el historico al momento de cada venta (limitacion del modelo — documentar en UI)

### Exclusiones confirmadas
- Exportacion a PDF o Excel de los reportes
- Acceso a reportes para roles distintos de Administrador
- Compras/Proveedores y Caja en Dashboard

## Sesion: Cierre de Caja Diaria y Mensual

### Origen del pedido
Investigacion extensa (misma conversacion, no discovery formal previo) sobre la diferencia del cierre de agosto 2026 entre el sistema, el libro Excel a mano del cliente y el extracto bancario real. El cliente (via Magali, quien lleva la administracion) pidio automatizar este control para no repetir el proceso manual cada mes ("mil controles y la caja no da nunca").

### Hallazgos de la investigacion previa (insumo de discovery, NO alcance cerrado)
1. El campo `Fecha` de `Pago` es editable manualmente y no siempre coincide con el dia real de acreditacion bancaria ni con el dia de carga en el sistema (`CreatedAt`). ~16% de los pagos de agosto (113 de ~710) tenian `Fecha` distinta a su dia real de carga — genera desfasajes que se cancelan en el total del mes pero no dia a dia.
2. No existe metodo de pago "Cheque" en el sistema (`MetodoPago`: Efectivo/Credito/Debito/MercadoPago/Transferencia/SaldoFavor). El papa de la duena anota los cheques como "Transferencia", con `Fecha` = el dia que efectivamente se deposita/acredita (no el dia que se recibe el cheque).
3. MercadoPago tambien se esta cargando como "Transferencia": el metodo "MercadoPago" del sistema dio $0 en agosto pese a que el extracto bancario tiene numerosas liquidaciones de Mercado Pago ese mes.
4. Ademas del libro de "Cuenta corriente / Caja de ahorro", existe un tercer registro manual (mencionado por Magali como "un deive") donde se anota diariamente cada cliente que deja efectivo en el local, que luego se carga al sistema — **no confirmado que es exactamente** (ver P1).
5. El cliente NO usa el modulo de Caja del sistema (`CajasController`/`MovimientoCaja`) para su control — su control real es 100% manual comparando la pantalla de Pagos contra sus propios registros y el extracto bancario. (Aparte, fuera de esta feature, se detecto un bug real de reconciliacion en ese modulo cuando una venta tiene 2+ pagos del mismo monto exacto — no relevante aca porque el cliente no lo usa.)
6. Reconciliar por TOTALES (dia o mes) no funciona por el problema de fechas — se valido manualmente en la investigacion que matchear por MONTO individual con ventana de tolerancia de fecha (probado ±3 dias) si permite identificar correctamente cheques puntuales, pagos de MercadoPago mal clasificados y desfasajes de fecha reales.
7. Se probaron 2 formatos de extracto bancario (BBVA): PDF resumen mensual completo (con remitente/referencia por transferencia, mucho mas rico pero mas complejo de parsear) y XLS "detalle de movimientos" simplificado (solo Fecha/Concepto/Importe, facil de parsear con `xlrd`/similar).

### Patron cross-proyecto aplicable (catalogo)
**PAT-012** (`docs/patrones/catalogo.yml`) — "Importacion de archivo con preview -> confirmar (staging + reporte de excepciones)" — aplicable directamente a la carga del extracto bancario mensual. No existe en el catalogo un patron de "conciliacion por monto + tolerancia de fecha"; si el Disenador confirma este enfoque, corresponde catalogarlo como patron nuevo al cerrar Diseno.

### 1. Alcance funcional resumido (preliminar — sujeto a respuestas del cliente)
**Incluido (hipotesis):**
- Cierre de caja diaria: el usuario carga el efectivo contado del dia; el sistema lo compara contra la suma de `Pago.Monto` con `MetodoPago = Efectivo` de ese dia y muestra la diferencia.
- Conciliacion mensual: el usuario sube el extracto bancario (archivo Excel/CSV, formato "detalle de movimientos" simplificado — ver P3); el sistema matchea cada linea del extracto contra `Pago` con `MetodoPago` bancario (Transferencia/Debito) por monto (con tolerancia de centavos) y ventana de dias configurable o fija.
- Reporte de resultado: 3 categorias por linea — concilia (match encontrado, sea mismo dia o con desfasaje de fecha dentro de la ventana), pendiente del lado del sistema (pago sin transferencia bancaria que lo respalde — candidato a cheque no depositado o error), pendiente del lado del banco (transferencia real sin pago de sistema que la explique — candidato a venta no registrada).
- El usuario puede marcar manualmente un pendiente como resuelto (con una observacion), sin que el sistema modifique el `Pago` original.
- Historial de cierres diarios y conciliaciones mensuales ya realizadas (para no repetir el proceso cada vez y poder auditar cierres pasados).

**No incluido (hipotesis, a confirmar):**
- Integracion automatica con el banco via API (se asume carga manual de archivo).
- Metodo de pago "Cheque" dedicado en el ABM de Pagos (ver P5 — podria ser una mejora futura separada).
- Correccion automatica del campo `Fecha` de un `Pago` (el modulo solo reporta diferencias, no reescribe datos existentes sin decision del usuario).
- Conciliacion del efectivo contra el tercer registro manual ("el deive") — depende de la respuesta a P1.
- Multiples cuentas bancarias en un mismo cierre (ver P4).

**Dependencias:**
- P1 (que es "el deive"), P3 (formato de extracto a soportar) y P4 (una o mas cuentas bancarias) condicionan directamente el alcance tecnico — no se puede cerrar Diseno sin esas respuestas.

### 2. Casos de uso principales (preliminar)
- CU1 — Cierre de caja diaria: cargar efectivo contado del dia y ver la diferencia contra `Pago` Efectivo del sistema.
- CU2 — Carga de extracto bancario: subir el archivo mensual (preview + confirmar, patron PAT-012).
- CU3 — Conciliacion automatica: matcheo por monto + ventana de fecha entre extracto y `Pago` (Transferencia/Debito).
- CU4 — Revision manual de pendientes: marcar un pendiente como resuelto/justificado con observacion.
- CU5 — Historial de cierres: consultar cierres diarios y conciliaciones mensuales anteriores.

### 3. Criterios de aceptacion verificables (preliminar, ejemplos)
- Dado un dia con `Pago` Efectivo por $X y el usuario carga efectivo contado $Y, el sistema calcula y persiste la diferencia ($Y - $X) al guardar el cierre.
- Dado un extracto cargado, cada linea con monto M y fecha F matchea contra un `Pago` (Transferencia/Debito) con el mismo monto (tolerancia configurable, ej. $0,50) dentro de una ventana de F ± N dias; si hay mas de un `Pago` candidato con el mismo monto, el sistema NO auto-asigna — queda para decision manual.
- Las lineas de extracto y los `Pago` sin match quedan listados por separado en el reporte de conciliacion, con su monto, fecha y (del lado de `Pago`) cliente/venta asociada.
- Un cierre diario o una conciliacion mensual ya cerrados se pueden reabrir para incorporar correcciones tardias (ej. un pago cargado dias despues con fecha retroactiva).

### 4. Permisos, estados y validaciones (preliminar)
- Permisos: a confirmar con P2 (quien carga el cierre diario).
- Estados sugeridos: `CierreCajaDiaria` (Pendiente/Cerrado/Reabierto), `ConciliacionMensual` (Pendiente/EnProceso/Cerrada/Reabierta), y por linea de matcheo (Conciliado/PendienteSistema/PendienteBanco/ResueltoManualmente).
- Validaciones: no permitir cerrar un dia/mes sin revisar los pendientes (o permitirlo con confirmacion explicita); el archivo de extracto debe tener las columnas esperadas (Fecha, Importe como minimo).

### 5. Riesgos y supuestos
- El formato del extracto bancario no esta estandarizado entre ambos documentos que probo el cliente (PDF completo vs XLS simplificado) — riesgo de que el banco cambie el formato del export y rompa el parser. Mitigacion sugerida: usar el formato XLS simplificado (Fecha/Concepto/Importe) como formato soportado, no el PDF.
- Mezclar cheques y MercadoPago bajo "Transferencia" limita la precision del matcheo automatico mientras no se corrija en el origen (fuera de alcance de este modulo, ver P5/P7) — el modulo va a seguir mostrando pendientes que en realidad son cheques/MercadoPago normales, no errores.
- No hay antecedente cross-proyecto de un modulo de conciliacion bancaria en el catalogo (`docs/patrones/catalogo.yml`) — se disenaria de cero (salvo la carga de archivo, que si reutiliza PAT-012).
- Supuesto: el cliente va a seguir subiendo el extracto manualmente cada mes (o con la periodicidad que decida) — no se asume integracion API bancaria.

### 6. Banderas tempranas
- Migracion EF: **SI** — al menos entidades nuevas para `CierreCajaDiaria`, `ConciliacionMensual`/`LineaExtractoBancario` y el resultado de matcheo por linea.
- Integracion externa: **NO** (asumiendo carga manual de archivo; si el cliente pide integracion API bancaria en el futuro, es una feature aparte).
- Maquina de estados: **SI** — estado de cierre diario/mensual + estado por linea de conciliacion (ver seccion 4).

### 7. Preguntas para el cliente (hipotesis a validar, cada una con variantes contrastadas)

**P1 — Que es "el deive"?**
- Hipotesis A: una app/servicio externo (tipo agenda de anotaciones o similar) donde anotan a mano cada cliente que deja efectivo en el local, sin ninguna integracion con el sistema — un registro en papel/digital paralelo, previo a cargar la venta en Delicias Naturales.
- Hipotesis B: Magali dijo "un Excel" y quedo transcripto como "deive" (dictado/voz a texto) — seria un TERCER archivo Excel, ademas del libro de Cuenta Corriente/Caja de Ahorro que ya vimos.
- Impacto: si es un registro digital exportable (Excel), podria incorporarse al modulo de conciliacion de efectivo (CU1) igual que el extracto bancario a CU3. Si es solo anotacion en papel, queda fuera de alcance de automatizacion y el CU1 se limita a comparar contra el efectivo contado a mano.

**P2 — Quien carga el cierre de caja diario y cuando?**
- Opcion A: lo carga el cajero/vendedor al cerrar su turno, desde una pantalla accesible con su rol actual (Vendedor).
- Opcion B: lo carga unicamente el Administrador (Magali/el dueno) al dia siguiente, revisando todo junto.
- Impacto: define permisos (`[Authorize(Roles=...)]`) y si hace falta una pantalla nueva accesible a mas de un rol.

**P3 — Que formato de extracto van a subir habitualmente?**
- Opcion A: el PDF del resumen mensual del banco (como el primero que compartieron) — trae remitente/referencia por transferencia, pero parsear PDF es mucho mas costoso y fragil ante cambios de formato del banco.
- Opcion B: el Excel/XLS "detalle de movimientos" (como el segundo archivo) — columnas planas Fecha/Concepto/Importe, mucho mas simple y estable de parsear, aunque sin remitente.
- Recomendacion del analisis: Opcion B es la tecnicamente viable a costo razonable — Opcion A implicaria presupuesto sensiblemente mayor (parseo de PDF no estructurado) para un beneficio (nombre del remitente) que el matcheo por monto+fecha no necesita para funcionar.

**P4 — Una cuenta bancaria o varias?**
- Opcion A: una sola cuenta (la Caja de Ahorro BBVA vista en los extractos analizados).
- Opcion B: mas de una cuenta — el libro del cliente distingue "Cuenta Corriente" vs "Caja de Ahorro" como 2 destinos bancarios distintos, lo que sugiere que podria haber una segunda cuenta real.
- Impacto: si son 2+ cuentas, la conciliacion mensual necesita permitir subir un extracto por cuenta y decidir si se conciliano por separado o combinadas.

**P5 — Los cheques van a seguir anotandose como "Transferencia", o quieren un metodo dedicado?**
- Opcion A (alcance minimo, dentro de este modulo): mantener "Transferencia" como esta hoy; el reporte de conciliacion simplemente deja como "pendiente del lado del sistema" a los pagos Transferencia sin respaldo bancario inmediato (que en la practica van a ser mayormente cheques en cartera).
- Opcion B (alcance mayor, feature separada): agregar un metodo de pago "Cheque" real al sistema con su propio ciclo (recibido -> depositado -> acreditado) — resuelve la ambiguedad de raiz pero es una feature aparte, no parte de este modulo.
- Recomendacion del analisis: Opcion A para este modulo; Opcion B como mejora futura a evaluar por separado si el cliente lo valora.

**P6 — Ventana de tolerancia de fecha para el matcheo automatico: fija o configurable?**
- Opcion A: ventana fija de ±3 dias corridos (la que se uso en el analisis manual y funciono bien para los casos revisados).
- Opcion B: configurable por el usuario en pantalla (ej. un parametro "dias de tolerancia").
- Impacto: Opcion B agrega un campo de configuracion (posible migracion extra minima) a cambio de flexibilidad; Opcion A es mas simple de construir.

**P7 — Que hacer con los pagos de MercadoPago mal clasificados como Transferencia?**
- Opcion A: fuera de alcance de este modulo — la conciliacion va a seguir viendo MercadoPago mezclado con transferencias reales y cheques bajo "Transferencia".
- Opcion B: agregar en este modulo un ajuste minimo a la pantalla de Registrar Pago para que el cajero pueda tildar "es Mercado Pago" (usando el metodo `MercadoPago` que ya existe en el enum pero no se usa).
- Recomendacion del analisis: Opcion A para no inflar el alcance de este modulo — Opcion B es una correccion de proceso independiente y de bajo costo que se podria resolver aparte, incluso antes que este modulo.

### Respuestas del cliente (2026-09-01) y alcance actualizado

| # | Respuesta | Efecto sobre el alcance |
|---|---|---|
| P1 | "el deive" = **Google Drive** | Confirmado que es un registro digital externo, no papel. Queda **pregunta de seguimiento P1b** (ver abajo) antes de decidir si entra al alcance de CU1. |
| P2 | **Administrador** unicamente | CU1 (cierre diario) se restringe a `[Authorize(Roles = "Administrador")]`. No hace falta pantalla accesible a Vendedor. |
| P3 | **A definir** | Sigue abierta — el analisis avanza con la Opcion B (XLS simplificado) como supuesto de trabajo recomendado, a confirmar antes de cerrar Diseno. |
| P4 | **Opcion A** — una sola cuenta bancaria | Conciliacion mensual: un extracto por mes, una sola cuenta. Sin necesidad de UI para multiples cuentas. |
| P5 | **Opcion B, con variante** — nuevo metodo de pago "Cheque", con **2 fechas**: Fecha de Pago (cuando se recibe/registra el cheque) y Fecha de Acreditacion (cuando el banco lo acredita realmente) | **Amplia el alcance mas alla del modulo de conciliacion**: modifica la entidad `Pago` existente (nuevo `MetodoPago.Cheque` + campo `FechaAcreditacion` nullable) y el flujo de `PagosController.RegistrarPago`/vista de registro de pago — no es solo una pantalla nueva de conciliacion, toca el circuito de Pagos ya en produccion. Ver riesgos actualizados abajo. |
| P6 | **Opcion A** — ventana fija ±3 dias | Sin campo de configuracion adicional; constante en el Service. |

### Alcance ampliado por P5 — metodo de pago "Cheque"

Cambios adicionales identificados (a validar en Diseno, no implementar aqui):
- `EnumTypes.MetodoPago`: agregar valor `Cheque`.
- `Pago`: agregar `FechaAcreditacion` (DateTime, nullable — solo aplica cuando `MetodoPago == Cheque`). El campo `Fecha` existente pasa a representar la fecha de recepcion/registro del cheque (ya es su semantica actual, se mantiene).
- `PagosController.RegistrarPago`: cuando `MetodoPago == Cheque`, pedir tambien `FechaAcreditacion` (puede quedar nula si todavia no se sabe / no se deposito, o exigirse siempre — **pregunta P5b** abajo).
- Impacto en reportes existentes: la pantalla de Pagos ("Total Filtrado") y el dashboard ya construidos **muestran totales por MetodoPago** — hay que decidir si un cheque cuenta en el total desde que se registra (`Fecha`) o solo cuando se acredita (`FechaAcreditacion`) — **pregunta P5c**.
- Beneficio directo para CU3 (conciliacion mensual): al tener `FechaAcreditacion` conocida en el propio `Pago`, el matcheo contra el extracto para los pagos `Cheque` puede ser mucho mas preciso (comparar contra esa fecha exacta, con tolerancia chica, ej. ±1 dia) en vez de depender de la ventana generica de ±3 dias que se usa para Transferencia/Debito.

### Preguntas de seguimiento nuevas (surgidas de las respuestas anteriores)

**P1b — El registro de Google Drive es una planilla (Google Sheets) o son archivos sueltos (fotos/PDF)?**
- Hipotesis A: es una Google Sheet estructurada (columnas tipo Fecha/Cliente/Monto) — se podria exportar/leer para alimentar el cierre de caja diaria (CU1) de forma similar a como el extracto bancario alimenta CU3, reduciendo la carga manual del Administrador.
- Hipotesis B: es una carpeta con archivos sueltos (fotos de comprobantes, capturas) sin estructura tabular — no serviria como fuente de datos automatizable, el Administrador seguiria tipeando el total de efectivo contado a mano en CU1.
- Impacto: si es Hipotesis A, CU1 podria ganar un sub-caso de uso de importacion (reutilizando PAT-012, igual que CU2); si es Hipotesis B, CU1 se mantiene simple (un input numerico manual).

**P5b — El cheque se puede registrar sin saber todavia la Fecha de Acreditacion (cheque diferido/a futuro que aun no se deposito), o siempre se carga con las 2 fechas juntas?**
- Hipotesis A: se puede registrar el cheque el dia que se recibe (Fecha de Pago) SIN la Fecha de Acreditacion todavia (queda null/pendiente), y se completa despues, cuando efectivamente se deposita — refleja mejor la realidad de un cheque diferido que puede tardar semanas.
- Hipotesis B: siempre se cargan las 2 fechas juntas al momento de registrar el pago (el cajero ya sabe cuando se va a depositar).
- Impacto: si es Hipotesis A, hace falta un estado/indicador visual de "cheque pendiente de acreditar" y una accion para completar la Fecha de Acreditacion despues — mas cercano a una mini maquina de estados (Registrado -> Acreditado, con posible Rechazado/Rebotado, ver P5d). Si es Hipotesis B, es un campo mas en el formulario, sin estado adicional.

**P5c — Un cheque sin acreditar todavia cuenta como "cobrado" en los reportes (Total Filtrado, dashboard) o no?**
- Hipotesis A: cuenta desde que se registra (igual que hoy trata cualquier Transferencia) — mas simple, consistente con el comportamiento actual.
- Hipotesis B: NO cuenta hasta que se acredita — mas preciso para saber "cuanta plata real hay", pero cambia el comportamiento de reportes ya en produccion (riesgo de romper expectativas del cliente sobre numeros historicos).

**P5d — Un cheque puede rebotar (rechazado por el banco)? Si pasa, se necesita poder revertir el pago?**
- Hipotesis A: si, es un caso real del negocio — hace falta una accion para marcar un cheque como "Rechazado" y que eso revierta el pago (similar a `EliminarPago`, pero con un motivo/estado distinto en vez de borrado silencioso).
- Hipotesis B: no es un caso que les preocupe manejar en el sistema — si un cheque rebota, lo resuelven fuera del sistema (llaman al cliente, etc.) y en el sistema simplemente eliminan el pago como ya se puede hacer hoy.

### 8. Clasificacion de perfil de cliente
**B2B/B2C mixto** — la cartera de clientes de Delicias Naturales incluye tanto consumidores finales como empresas (S.A./S.R.L., ej. Antigal, Comunidad GH, El Modelo, Nutridiet, Le Bourguignon) con compras mayoristas recurrentes de montos altos.
**Escala: mediano-grande** — cliente activo desde 2025 con 26 entidades y 19 controladores en produccion, integracion AFIP x5, ~500+ ventas/mes, facturacion mensual del orden de $85-90M ARS. Cliente historico del estudio con multiples entregas ya facturadas (Dashboard Ampliado, hotfixes, etc.) y capacidad de pago establecida — corresponde precio de lista / trato de cliente fiel al presupuestador, no descuento agresivo de cierre.

## Sesion: Ajuste directo de un Pago

### Origen del pedido
Investigacion de un incidente real en produccion (venta 9444/remito 9324, cliente BUJANZI ZULMA ISABEL): un vendedor revirtio una venta ya Facturada a Ingresada (`CambiarEstadoIngresada`), saco 5 productos (uno de ellos ya facturado y pagado, $28.000) y volvio a Finalizar. La Factura A (AFIP aprobada, Nº 4353, $92.550,05) quedo desconectada de la realidad de la venta, y $28.000 de pagos quedaron sueltos sin ningun movimiento de cuenta corriente que los explicara. Al investigar por que no se pudo corregir prolijamente, se confirmo que `PagosController` no tiene ninguna accion para editar el monto de un pago ya cargado — el vendedor habia intentado resolverlo creando y borrando pagos por prueba y error (evidencia: 2 pagos de $92.550,05 creados y borrados el mismo dia con distinto metodo de pago). Se corrigio aparte, como fix preventivo puntual, el guard que faltaba en `CambiarEstadoIngresada` (bloquear el revert si la venta ya tiene una Factura aprobada). Esta sesion cubre el gap de fondo: dar una forma segura de corregir el monto de un pago ya registrado.

### Estado actual confirmado por lectura de codigo
- `PagosController` tiene `RegistrarPago` (crear, con lock `_registrarPagoLock` para la carrera de lectura de `montoRestante`/`saldoDisponible`, y logica de sobrepago→credito / SaldoFavor→debito en cuenta corriente), `EliminarPago` (soft-delete que SI revierte correctamente el `MovimientoCaja` y los `MovimientoCuentaCorriente` vinculados al pago — fix ya aplicado en una sesion anterior) y `ActualizarFechaPago` (solo cambia la fecha). **No existe ninguna accion de edicion de monto.**
- El modelo `Pago` (`Models/Pago.cs`) no tiene `Usuario`/`UsuarioId` ni `Observacion` — a diferencia de `Venta`, que si registra que usuario hizo la ultima modificacion. Hoy no queda registrado ni quien ni por que se cargo un pago, mucho menos si se corrigio.
- Ya existe un mecanismo de ajuste manual, pero es de otra naturaleza: `ClientesController.RegistrarAjusteCuentaCorriente` (solo Administrador) carga un movimiento de cuenta corriente (credito/debito, tipo AjusteManual, con observacion obligatoria) desconectado de cualquier Pago puntual — sirve para dejar saldo a favor/en contra de un cliente, no para corregir el monto de un pago ya asentado sobre una venta.
- Patron cross-proyecto directamente aplicable: **PAT-020** (`docs/patrones/catalogo.yml`, formalizado como regla MH-020 en `32-estandares-qa-implementador.instructions.md`) — "ledger inmutable": un movimiento financiero ya posteado nunca se edita ni se borra en el sentido de reescribir su fila; se reversa con un contramovimiento y se registra uno nuevo correcto. Aplicado a este caso: "editar un pago" no deberia ser un UPDATE silencioso de `Pago.Monto` (que además dejaria corriendo desincronizados el `MovimientoCaja` y cualquier `MovimientoCuentaCorriente` ya generado por el monto viejo) — el diseño natural es reutilizar la logica ya correcta de `EliminarPago` (reversion de movimientos) + `RegistrarPago` (alta con las mismas validaciones de sobrepago/SaldoFavor) dentro de una unica accion transaccional, dejando trazabilidad de que hubo un ajuste (monto anterior, motivo, usuario, fecha).

### 1. Alcance funcional (preliminar)
**Incluido (hipotesis):**
- Nueva accion `AjustarPago` (o equivalente) en `PagosController`: dado un `pagoId` y un `nuevoMonto` + motivo obligatorio, en una unica transaccion: reversa los movimientos (`MovimientoCaja`, `MovimientoCuentaCorriente`) del pago viejo igual que `EliminarPago`, marca el pago viejo como reemplazado (soft-delete, conservando el vinculo al nuevo), y crea un pago nuevo por el monto corregido re-ejecutando las mismas validaciones de `RegistrarPago` (lock de concurrencia, sobrepago→credito, SaldoFavor→debito).
- Agregar a `Pago`: `UsuarioId` (quien registro/ajusto) y `Observacion` (motivo, obligatorio solo para el ajuste) — cierra el gap de auditoria detectado, y es un prerequisito real para poder mostrar "quien ajusto, cuando y por que" en pantalla.
- Trazabilidad visible en la UI: el listado/detalle de pagos de una venta debe poder mostrar que un pago fue ajustado (referenciar el pago anterior reemplazado), no solo mostrar el pago nuevo como si fuera el original.
- Guard de estado del comprobante (mismo criterio que MH-020 punto 4): si la Venta ya esta en un estado terminal para pagos (a definir cual aplica aca — hoy no hay un estado "Cancelada" para Venta, existen Ingresada/Finalizada/Facturada), el ajuste de un pago no debe disparar ningun recalculo automatico del estado de la Venta.

**No incluido (CONFIRMADO 2026-09-07, no solo hipotesis):**
- Reabrir o modificar la Factura/AFIP desde esta funcionalidad — "Editar pago" es independiente de la Nota de Credito fiscal (esa sigue siendo `FacturasController.Generar` con tipo Nota de Credito, feature ya existente, 100% manual).
- Resolver retroactivamente la venta 9444 — **ya resuelta aparte, a mano**, fuera de este flujo formal (pagos corregidos + NC A Nº 0005-00000026 emitida y aprobada por AFIP, CAE 86361847162185, el mismo dia 2026-09-07).
- Un historial de auditoria generico para TODAS las entidades del sistema — el alcance de `UsuarioId`/`Observacion` es puntual a `Pago` (que hoy no tiene nada), no un modulo de auditoria transversal.
- **Gestion de devoluciones de punta a punta.** Joaquin pregunto explicitamente si "Editar pago" alcanza para gestionar devoluciones, y la respuesta es NO: esta feature solo reconcilia el monto/fecha/metodo de un pago ya cargado. Joaquin decidio explicitamente mantener el alcance acotado a esto y tratar la devolucion completa como un Discovery separado a futuro (ver seccion "Pendiente — Gestion de Devoluciones" mas abajo). Documentado aca para que quede claro que esta decision fue tomada con el gap conocido, no por descuido.

### 2. Casos de uso principales (preliminar)
- CU1 — Ajustar el monto de un pago existente, con motivo obligatorio, reversando y recreando de forma atomica.
- CU2 — Ver en el detalle/listado de pagos de una venta que un pago fue ajustado (pago anterior + pago vigente enlazados).
- CU3 — Los movimientos de caja/cuenta corriente quedan consistentes con el monto corregido (ni duplicados ni huerfanos) tras el ajuste.

### 3. Criterios de aceptacion verificables (preliminar)
- Dado un pago de $X sin movimientos de cuenta corriente asociados, ajustarlo a $Y dentro de la misma venta: el pago viejo queda soft-deleted, existe un pago nuevo por $Y, el `MovimientoCaja` refleja $Y (no $X ni ambos sumados), y el total pagado de la venta pasa a incluir $Y en lugar de $X.
- Dado un pago que genero un credito en cuenta corriente por sobrepago, ajustarlo a un monto menor: el credito viejo se revierte y se recalcula el nuevo credito/debito segun corresponda con el monto ajustado (nunca queda el credito viejo sumado al nuevo).
- Intentar ajustar sin motivo: rechazado con error funcional explicito, no persiste nada.
- Intentar ajustar con un usuario sin el rol habilitado (ver P1 abajo): 403, nunca ejecuta el ajuste.
- El historial de pagos de la venta permite reconocer visualmente que un pago fue ajustado y cual es su motivo.

### 4. Impacto preliminar por capa
- **Datos:** migracion EF — `Pago` gana `UsuarioId` (FK a `AspNetUsers`, nullable para no romper los ~15.000+ pagos historicos sin este dato) y `Observacion` (nullable); posible campo `PagoAnteriorId`/`PagoReemplazadoId` (self-FK nullable) para enlazar el pago nuevo con el que reemplaza, si el Diseñador confirma que la trazabilidad visual se resuelve asi (alternativa: guardar la referencia en la propia `Observacion` del pago nuevo, mas simple pero menos consultable).
- **Negocio:** `PagosController.AjustarPago` (o el nombre que fije Diseño) reutilizando/refactorizando la logica ya existente de `EliminarPago` (reversion) y `RegistrarPago` (alta con validaciones), dentro del mismo lock de concurrencia (`_registrarPagoLock`) para evitar la misma carrera de `montoRestante`/`saldoDisponible` que ya se corrigio una vez.
- **Presentacion:** boton/modal "Ajustar" en el listado de pagos de la Venta (junto a los ya existentes Editar fecha/Eliminar), con campo de motivo obligatorio; el listado debe reflejar visualmente el pago ajustado (referenciando al reemplazado).

### 5. Riesgos y supuestos
- Riesgo de concurrencia: un ajuste que corre en paralelo con `RegistrarPago` sobre la misma venta debe respetar el mismo lock ya existente — si se implementa como "reversar + crear" fuera de ese lock, se reintroduce la misma carrera que motivo `_registrarPagoLock` originalmente.
- Riesgo de alcance: si se decide guardar el vinculo pago-viejo/pago-nuevo como entidad separada en vez de un campo simple, el costo sube — a resolver en Diseño, no aca.
- Supuesto: el ajuste se limita a corregir el **monto**; cambiar el metodo de pago o la venta asociada de un pago ya cargado NO esta pedido y se asume fuera de alcance salvo que el cliente lo pida explicitamente.
- Dependencia cruzada con la sesion "Cierre de Caja Diaria y Mensual" (mismo archivo, arriba): si ese modulo se construye antes, un ajuste retroactivo sobre un pago de un periodo ya cerrado/conciliado deberia advertir o bloquear — hoy no aplica (ese modulo no existe todavia), pero queda anotado para cuando ambas features convivan.

### 6. Banderas tempranas
- Migracion EF: **SI** — `UsuarioId` + `Observacion` (+ posible self-FK) en `Pago`.
- Integracion externa: **NO**.
- Maquina de estados: **NO nueva** (reutiliza el guard de estado de Venta ya existente; el "pago reemplazado" es un flag/relacion, no un estado con transiciones propias).

### 7. Preguntas para el cliente — RESUELTAS (2026-09-07)

**P1 — Que rol puede ajustar un pago?** → **Decidido: Opcion B** — Administrador y Vendedor, igual que `RegistrarPago`/`EliminarPago` hoy. (Recomendacion del analisis era Opcion A/solo Administrador por el riesgo de manipular cifras ya asentadas; Joaquin opto por mantener paridad con los permisos actuales de Pagos — riesgo residual aceptado conscientemente, ver riesgos en Diseno.)

**P2 — Como se muestra el pago ajustado en pantalla?** → **Decidido: Opcion B** — el listado muestra ambos pagos (el viejo tachado/gris + el nuevo vigente), como mini-historial siempre visible sin necesidad de interaccion.

**P3 — Hace falta un limite de tiempo para poder ajustar un pago?** → **Decidido: Opcion A** — sin limite, se puede ajustar un pago de cualquier antiguedad. Si el modulo de Cierre de Caja se construye a futuro, ahi correspondera bloquear el ajuste de un pago dentro de un periodo ya conciliado.

### Condicion de paso a Diseno
Analisis cerrado. Gate de Diseño **habilitado** — ver `2-disenador-funcional.md`, iteracion 3, diseño ya cerrado con estas 3 decisiones incorporadas.

### Pendiente — Gestion de Devoluciones (Discovery futuro, fuera de alcance de esta feature)
Al cerrar el diseño de "Editar pago", Joaquin pregunto si esto alcanza para gestionar devoluciones de producto sobre una venta ya Finalizada/Facturada. Respuesta: **no**, y ademas el fix preventivo aplicado sobre `CambiarEstadoIngresada` (bloquear el revert si hay Factura activa, ver incidente venta 9444 arriba) **dejo un gap nuevo**: hoy no existe NINGUNA via soportada para sacar un producto de una venta Finalizada/Facturada (antes se hacia, incorrectamente, revirtiendo a Ingresada — eso ahora esta bloqueado a proposito, sin alternativa). Una devolucion real necesita coordinar 3 partes que hoy son 3 acciones manuales separadas, sin ningun flujo que las conecte:
1. **Producto**: sacar/reducir el item devuelto de la venta — sin via soportada hoy sobre una venta ya facturada.
2. **Factura/AFIP**: emitir la Nota de Credito correspondiente — existe (`FacturasController.Generar`), pero 100% manual, sin ninguna ayuda para calcular que producto/monto acreditar.
3. **Pago/dinero**: reconciliar lo que el cliente pago contra lo que ahora corresponde — con "Editar pago" (esta feature) se puede hacer a mano, pero alguien tiene que calcular el numero correcto cruzando venta+factura+pagos (exactamente lo que se hizo a mano para la venta 9444).
Joaquin decidio explicitamente NO ampliar el alcance de esta feature y tratar esto como un Discovery separado a futuro: una accion nueva tipo "Registrar devolucion" sobre una Venta Facturada, que reciba el/los productos devueltos y orqueste automaticamente las 3 partes (generar la NC, calcular y aplicar el ajuste de pago/saldo a favor necesario, dejar el producto marcado como devuelto). No tiene fecha de inicio asignada.

## Historial de ajustes
- Sesion Dashboard Ampliado: analisis cerrado, 5 items aprobados. Presupuesto USD 100 acordado (lista USD 125, descuento fidelidad USD 25). Documento cliente en repo del proyecto.
- 2026-09-01: Discovery/analisis preliminar de "Cierre de Caja Diaria y Mensual" a partir de investigacion extensa de la diferencia de cierre de agosto 2026. 7 preguntas abiertas para el cliente (P1-P7) antes de poder cerrar el alcance — gate de Diseno NO habilitado todavia.
- 2026-09-07: Discovery/analisis de "Ajuste directo de un Pago", a partir del incidente de la venta 9444 (Factura desconectada por reversion de estado sin guard). Patron PAT-020 (ledger inmutable) identificado como base de diseño. P1-P3 resueltas por Joaquin el mismo dia (Administrador+Vendedor, mostrar ambos pagos viejo/nuevo, sin limite de tiempo) — Analisis cerrado, gate de Diseno habilitado.

