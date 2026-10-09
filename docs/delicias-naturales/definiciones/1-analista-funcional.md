# Memoria - Analista funcional

## Proyecto: delicias-naturales
## Ultima actualizacion: 2026-10-07 - relevamiento cuantitativo de la diferencia de caja mensual (seccion 9 de "Cierre de Caja Diaria y Mensual")

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
### 9. Relevamiento cuantitativo de la diferencia mensual (2026-10-07)

Segunda medicion, ahora sobre **septiembre 2026** y con conciliacion linea a linea reproducible (extracto XLS "detalle movimientos septiembre" vs `pagos` de produccion). Reemplaza las hipotesis de agosto por numeros cerrados: la conciliacion cuadra al centavo, asi que la lista de causas de abajo es exhaustiva para ese mes, no indicativa.

#### 9.1 Causa raiz #0 — el cliente compara dos magnitudes que no son comparables

El numero que el cliente llama "lo que dice el banco" **no es la suma de las cobranzas del mes**:

| Concepto | Importe |
|---|---|
| Total del archivo de extracto | 40.346.813,07 |
| (-) Depositos de efectivo propios al banco (3 lineas `DEPOSITO AUTOSERVICIO PLUS`, 29/09) | -5.000.000,00 |
| (-) Intereses ganados y ajustes | -301,83 |
| **= Transferencias de clientes realmente acreditadas (242 lineas)** | **35.346.511,24** |
| Sistema, `Pago` con `MetodoPago = Transferencia` de septiembre (245 pagos) | 36.019.758,88 |
| **Diferencia real (sistema - banco)** | **+673.247,64** |

El cliente venia reportando ~7.000.000 de diferencia: 5.000.000 de eso son **sus propios depositos de efectivo**, que el sistema ya contabilizo como `Efectivo` y el banco vuelve a mostrar como credito. Mientras el control siga siendo "total del extracto vs total de Transferencias", la caja **no puede dar nunca**, con o sin errores de carga. Ademas el archivo que usan es un listado **solo de creditos** (0 debitos en las 248 lineas), asi que tampoco sirve para arquear el saldo de la cuenta.

**Consecuencia de diseño (vinculante para la etapa 2):** la carga de extracto (CU2) tiene que **clasificar y excluir los creditos que no son cobranzas de clientes** antes de conciliar — no es un detalle de implementacion, es lo que hace que el numero final tenga sentido.

#### 9.2 Resultado del matcheo automatico sobre datos reales

Algoritmo probado: tolerancia escalonada ($1 → $2 → $25 → $150, por pasadas, el mas cercano primero), ventana de fecha ±4 dias, y despues combinaciones N:1.

| Resultado | Lineas de extracto | Importe |
|---|---|---|
| Concilia 1-a-1 | 215 | diferencia acumulada de centavos: $80,46 |
| Concilia N pagos → 1 credito (una transferencia paga varias ventas) | 6 | -$21,61 |
| **Subtotal automatico** | **221 de 242 (91,3 %)** | |
| Cruza pero por **otro importe** | 6 | -$14.111,93 |
| Credito sin pago en el sistema | 15 | -$1.160.554,56 |
| Pago sin credito en el banco | (11 pagos) | +$1.847.855,28 |
| **Total** | | **+$673.247,64** (cuadra exacto) |

**Dos requisitos nuevos que el analisis de agosto no contemplaba:**
1. **Matcheo N:1 obligatorio.** 6 de 242 creditos pagan 2-3 ventas en una sola transferencia (ej. 02/09 $618.038,00 = ventas 9250 + 9349 + 9388). El criterio original asumia 1 pago ↔ 1 linea; con 1:1 puro esas 6 lineas y sus 14 pagos caen a "pendiente" por error del algoritmo, no del dato.
2. **Tolerancia escalonada, no fija.** Los clientes transfieren el importe **redondeado** y el sistema guarda el importe facturado con centavos identificatorios. Con tolerancia unica de $0,50 (lo que decia el criterio de aceptacion preliminar) el matcheo baja de 91 % a ~86 %; con la escalonada, los 215 cruces 1-a-1 acumulan $80,46 de ruido total en el mes — despreciable.

#### 9.3 Taxonomia de las causas, con importe (septiembre)

| # | Causa | Evidencia | Efecto |
|---|---|---|---|
| C1 | **Pago bancario cargado como `Efectivo`** | $223.669,16 venta 9598, pago 15798 (17/09) — el banco lo acredita el 18/09 como TRANSFERENCIA | Infla Efectivo, desinfla Transferencia |
| C2 | **Borrar y recrear un pago por otro importe** en vez de editarlo | venta 9324: el banco acredito $92.550,00; en el sistema quedaron 3 pagos de $92.550,05 borrados y uno activo de $64.550,05 | -$28.000 |
| C3 | **Importe registrado distinto al acreditado** (se carga el total de la factura, no lo que entro) | 9080 (-6.556,21), 9209 (-7.897,76), 9318 (-5.816,25), 9457 (-3.617,03), 9639 (**+9.999,23**, tipeo de 10.000 de mas) | -$14.111,93 |
| C4 | **Corte de mes** — credito del 01/09 con pago fechado 31/08 | pagos 15098 ($152.599,96, venta 9257) y 15185 ($30.550,01, venta 9356) | -$183.149,97, se compensa con agosto |
| C5 | **Creditos duplicados en el extracto sin pago que los explique** | $107.350,02 (29/09) y $107.350,00 (30/09) con un solo pago; dos lineas de $58.222,00 el 14/09 con un solo pago | a investigar con el banco |
| C6 | **Pago marcado Transferencia sin acreditacion en el mes** (11 pagos) | el mayor: $434.000,00 venta 9581 (18/09), sin credito parecido en ±7 dias; tambien 9517, 9665, 9487 (x2), 9311, 8945, 8948, 9325, 9384, 9425 | +$1.847.855,28 |
| C7 | **Credito bancario sin ningun pago en el sistema** (15 lineas) | **7 de las 15 son del 18/09** ($107.167,50 / $90.934 / $39.838 / $39.792,80 / $33.775 / $20.942 / $20.000) — patron de dia entero mal cargado | -$1.160.554,56 |

#### 9.4 Causas estructurales, medidas mes a mes (abril–octubre 2026)

Esto es lo que contesta **"por que pasa todos los meses"**: no es un bug de calculo, son cinco huecos de validacion en el circuito de `Pago` que producen ruido de forma estable, mes tras mes.

| Hallazgo | Medicion |
|---|---|
| `Pago.Fecha` distinta del dia real de carga (`CreatedAt`) | **9,2 % – 20,0 %** de los pagos de cada mes (87–153 pagos/mes). Carga tardia de mas de 3 dias: 15–49 por mes |
| Pagos borrados | **82–116 por mes** (10–14 % del volumen mensual) |
| Borrar-y-recrear el mismo monto en la misma venta | **37–61 casos por mes** — septiembre: 40 casos, $4.336.253,16 |
| Uso real de **"Editar Pago"** (deployado 2026-09-07 para resolver exactamente esto) | **0 usos.** De los 840 pagos posteriores al deploy, ninguno tiene `PagoAnteriorId`; 1 solo tiene `Observacion`. La herramienta correcta existe y no se adopto |
| `MetodoPago.MercadoPago` | **0 pagos en todos los meses** desde junio 2026 — confirma el hallazgo 3 de agosto: MercadoPago sigue cayendo en Transferencia o Efectivo |
| `Pago.Fecha` sin validacion de rango | **3 pagos activos con fecha futura**: $688.425,33 con `Fecha` 16/10/2026 cargado el 29/09 (sale del cierre de septiembre y entra al de octubre), y 2 de diciembre 2026 cargados en enero 2026 ($163.780,83) que **no entran en ningun cierre** |

La C2 y la C3 son consecuencia directa de la fila de "Editar Pago": mientras el operador corrija por borrar-y-recrear, cada correccion es una oportunidad de dejar el importe mal. El modulo de conciliacion **detecta** eso despues; no lo evita.

#### 9.5 Dos frentes, no uno

El relevamiento parte el problema en dos entregas separables, y conviene hacerlas en este orden:

**Frente A — preventivo, sobre el circuito de Pagos ya en produccion (barato, ataca la causa):**
- A1. Validar `Pago.Fecha`: rechazar fecha futura, rechazar fecha anterior a la fecha de la venta, y avisar (no bloquear) si se aparta mas de N dias del dia de carga. Elimina de raiz la fila "fecha sin validacion" y acota el 9–20 % de desfasaje.
- A2. Cerrar el camino del borrar-y-recrear: pedir motivo en `EliminarPago` y dirigir al usuario a "Editar Pago" cuando lo que quiere es cambiar monto/metodo/fecha. Sin esto, A3 y el modulo de conciliacion trabajan sobre datos que se siguen ensuciando.
- A3. Advertir en el registro de pago cuando la suma de pagos no cierra contra el total de la venta (hoy septiembre tiene 2 ventas sobrepagadas y 9 con saldo).
- A4. Habilitar `MercadoPago` y `Cheque` como metodos reales (P5 ya decidido: `Cheque` con `FechaAcreditacion`), y dejar de usar Transferencia como cajon de sastre.
- A5. En la pantalla de Pagos, separar los metodos **bancarios** (Transferencia / Debito / Credito / MercadoPago / Cheque acreditado) de los de **caja** (Efectivo), para que el total que el cliente compara contra el banco sea el total correcto.

**Frente B — detectivo, el modulo de Cierre y Conciliacion (CU1–CU5 de las secciones 1–4), con el algoritmo ya validado al 91,3 %.** Requiere incorporar 9.1 (clasificar creditos que no son cobranzas), 9.2.1 (matcheo N:1) y 9.2.2 (tolerancia escalonada).

Hacer solo B deja al cliente conciliando el mismo ruido todos los meses, mas rapido. Hacer A primero baja el volumen de pendientes que B tiene que mostrar.

#### 9.6 Preguntas nuevas para el cliente

**P8 — Los depositos de efectivo propios al banco (los $5.000.000 del 29/09), se registran hoy en algun lado del sistema?**
- Hipotesis A: no se registran — el efectivo cobrado figura como `Pago` Efectivo y el deposito al banco no deja rastro. La conciliacion tendria que simplemente excluir esos creditos del matcheo (marcarlos "deposito propio") y, opcionalmente, cruzarlos contra el efectivo acumulado del periodo.
- Hipotesis B: el cliente espera que esos depositos se registren como movimiento (seria el `MovimientoCaja` que hoy no usa, o una entidad nueva) — amplia el alcance al modulo de Caja que hoy esta abandonado.

**P9 — Que paso el 18/09?** 7 creditos bancarios de ese dia ($576.118,46 en total, ninguno mayor a $110.000) no tienen pago que los explique, y el mismo dia hay 3 pagos Transferencia en el sistema sin credito ($936.925,24). Es el unico dia con ese patron en el mes.
- Hipotesis A: se cargaron esos cobros como `Efectivo` (misma causa C1, en bloque).
- Hipotesis B: son cobranzas de ventas que todavia no estaban registradas ese dia y se cargaron despues con otra fecha.
- Impacto: si es A, refuerza la prioridad de A5; si es B, refuerza A1.

**P10 — Los creditos duplicados del extracto (C5) son doble acreditacion del banco o dos clientes distintos con el mismo importe?** Sin el remitente (el XLS simplificado no lo trae) no se puede decidir desde los datos. Si el caso es frecuente, reabre P3 a favor del PDF (que si trae remitente) para esas lineas puntuales.

**P11 — Por que no se usa "Editar Pago"?** 0 usos en un mes de produccion.
- Hipotesis A: el operador no sabe que existe (falta de aviso/capacitacion) — se resuelve fuera del sistema.
- Hipotesis B: el boton pide algo que al operador le resulta caro (motivo obligatorio) o esta donde no lo ve.
- Hipotesis C: el riesgo DN-004 ya documentado (editar un pago exige caja chica abierta) lo bloquea en la practica.
- Impacto: A2 no sirve de nada si la alternativa a la que se dirige al usuario esta rota o escondida. **Esta pregunta condiciona el frente A completo.**


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

## Sesion: Agrupar por categoria en modal "Productos con stock bajo"

### Pedido
Pantalla Productos (`Views/Productos/Index.cshtml`), modal "Productos con stock bajo" (`ViewBag.ProductosBajoMinimo`, `ProductosController.Index`): hoy es una tabla plana ordenada por nombre, sin agrupar. Pedido explicito: "agregar conjunto o filtro por categoria... el usuario quiere ver los productos agrupados mas ordenadamente. algo que visualmente sea mas sencillo."

### Alcance
- Agrupar visualmente por Categoria dentro del modal (encabezado de grupo + productos debajo, orden alfabetico de categoria y de producto).
- Filtro/select de categoria en el modal (junto al buscador ya existente) para poder aislar una sola categoria.
- Mantener el buscador por nombre/codigo ya existente y el resto del comportamiento (colores sin-stock/bajo-minimo, boton editar Admin).
- Gap tecnico encontrado: la query de `ProductosBajoMinimo` en `ProductosController.Index` NO incluye `.Include(p => p.Categoria)` (a diferencia de la query principal de la pantalla) — hay que agregarlo para no disparar lazy-load por fila o traer null.

### No incluido
- Cambios al criterio de "que es stock bajo" (StockActual < StockMinimo o <=0) — solo presentacion.

### Criterios de aceptacion
- El modal muestra los productos agrupados por categoria, con nombre de categoria visible como separador.
- El select de categoria filtra el modal a esa categoria unicamente (o "Todas").
- Buscar por nombre/codigo sigue funcionando combinado con el filtro de categoria.
- Sin categoria asignada -> grupo "Sin categoria".

Analisis cerrado (alcance chico y sin ambiguedad, no requirio preguntas al cliente).

## Historial de ajustes
- Sesion Dashboard Ampliado: analisis cerrado, 5 items aprobados. Presupuesto USD 100 acordado (lista USD 125, descuento fidelidad USD 25). Documento cliente en repo del proyecto.
- 2026-09-23: Analisis cerrado de "Agrupar por categoria en modal Stock Bajo" — mejora de presentacion, sin cambios de reglas de negocio.
- 2026-09-01: Discovery/analisis preliminar de "Cierre de Caja Diaria y Mensual" a partir de investigacion extensa de la diferencia de cierre de agosto 2026. 7 preguntas abiertas para el cliente (P1-P7) antes de poder cerrar el alcance — gate de Diseno NO habilitado todavia.
- 2026-10-07: **Relevamiento cuantitativo de la diferencia de caja mensual** (seccion 9 de la sesion "Cierre de Caja Diaria y Mensual"). Conciliacion linea a linea de septiembre 2026 que cuadra al centavo: diferencia real $673.247,64 (no los ~7M que reportaba el cliente — 5M de eso son sus propios depositos de efectivo). 7 causas con importe (C1-C7) y 6 causas estructurales medidas mes a mes abril-octubre. Hallazgos que cambian el alcance previo: la carga de extracto debe clasificar y excluir los creditos que no son cobranzas; el matcheo necesita N:1 y tolerancia escalonada (91,3 % automatico medido); "Editar Pago" tiene 0 usos reales en un mes de produccion. El problema se parte en Frente A (preventivo, 5 items sobre el circuito de Pagos) y Frente B (el modulo de conciliacion ya relevado). 4 preguntas nuevas (P8-P11); P11 condiciona el Frente A completo. **Gate de Diseno sigue NO habilitado** (P1b, P3, P5b-d, P8-P11 abiertas).
- 2026-09-07: Discovery/analisis de "Ajuste directo de un Pago", a partir del incidente de la venta 9444 (Factura desconectada por reversion de estado sin guard). Patron PAT-020 (ledger inmutable) identificado como base de diseño. P1-P3 resueltas por Joaquin el mismo dia (Administrador+Vendedor, mostrar ambos pagos viejo/nuevo, sin limite de tiempo) — Analisis cerrado, gate de Diseno habilitado.

