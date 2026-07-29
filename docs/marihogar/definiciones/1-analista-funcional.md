# Memoria - Analista funcional

## Proyecto: marihogar *(nombre provisional — confirmar con cliente)*
## Ultima actualizacion: 2026-07-06

---

## Análisis funcional v2 — CERRADO 2026-07-06

### Contexto del negocio
- Rubro: venta de productos de decoración y hogar
- Sistema actual: Contagram (gestión de ventas y compras) — a reemplazar completamente
- Canal de captación: anuncios de producto específico en Meta (Facebook / Instagram)
- Canal de contacto del lead: WhatsApp (clic en anuncio → mensaje al número del negocio)
- Cierre de venta: presencial en el local O entrega y cobro a domicilio
- Formas de cobro: efectivo, transferencia, MercadoPago
- Objetivo: sistema de gestión comercial completo que reemplaza Contagram + automatiza captación de leads

### Escala del sistema post-relevamiento
El relevamiento v1 describía un sistema de captación y ventas (10 módulos).
El relevamiento v2 describe un sistema de gestión comercial completo (18 módulos), comparable a Delicias Naturales en alcance.

---

## Módulos confirmados — 18 módulos

### Grupo 1 — Captación y ventas
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M1 | CRM de Leads | Leads desde WhatsApp, máquina de estados, historial | Media |
| M4 | Presupuestador | Cotización multi-línea, PDF, envío WhatsApp | Media |
| M5 | Gestión de ventas | Multi-pago, estados, impacto automático en CC del local | Alta |
| M6 | Entregas a domicilio | Dirección, fecha, cobro en destino, mobile-friendly | Media |
| M8 | Bot WhatsApp | Inbound webhook, reconocimiento de anuncio (referral Meta), preguntas de calificación por producto | **Muy alta** |

### Grupo 2 — Catálogo y stock
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M2 | Catálogo de productos | Precio compra, precio venta, tipo, marca, modelo, categoría, fotos, stock mínimo | Media |
| M3 | Control de stock | Movimientos: compras (M12), ventas (M5), ajuste manual. Alerta stock mínimo | Media |
| M16 | Aumento masivo de precios | Por marca / categoría / modelo · sobre precio compra o venta · previsualización previa obligatoria | Media |

### Grupo 3 — Compras y proveedores
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M12 | Compras a proveedores | Órdenes de compra (estados), líneas de producto, recepción completa → actualiza stock | Alta |
| M13 | Cuenta corriente proveedores | Saldo por proveedor, historial de pagos, deuda pendiente | Media |
| M14 | Gestión de cheques | Cheques 30/60/90 días, acreditación automática (job diario), alertas dashboard | **Alta** |

### Grupo 4 — Financiero del local
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M11 | Cuenta corriente del local | Balance: ingresos (ventas) − egresos (compras + gastos). Sin clientes deudores. | Media |
| M15 | Caja mensual | Ingresos vs egresos del período con filtro y comparativo mes anterior | Media |
| M18 | Gastos varios | Alquiler, servicios, sueldos, fletes, otros. Con categoría e impacto en CC y caja. | Baja-Media |
| M17 | Proyección financiera | Promedio histórico (últimos 3 meses) + compromisos futuros (cheques + OCs pendientes). Alerta de déficit. | Alta |

### Grupo 5 — Facturación
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M7 | Facturación ARCA | Selección de ítems individuales y cantidades de la venta. Factura A/B. CAE + PDF. | **Muy alta** |

### Grupo 6 — Infraestructura y visibilidad
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M10 | Usuarios y roles | Administrador / Vendedor | Baja |
| M9 | Dashboard | KPIs financieros básicos + cheques por vencer + stock crítico + conversión leads | Media |

---

## Procesos principales confirmados

### Proceso de venta
1. Meta Ad (producto específico) → cliente escribe WhatsApp → bot detecta anuncio (referral) → captura nombre + preguntas de calificación → registra Lead
2. Vendedor retoma desde CRM → arma Presupuesto → genera PDF → envía al cliente
3. Cliente aprueba → convierte a Venta → descuenta stock → genera movimiento en CC del local
4. Pago registrado (efectivo/transferencia/MP) → emite factura ARCA con los ítems seleccionados

### Proceso de compra a proveedores
1. Admin crea Orden de Compra → selecciona proveedor + productos + cantidades
2. OC pasa a Confirmada → al recibir mercadería → Recibida → stock se actualiza
3. Admin registra pago: efectivo / transferencia / cheque 30-60-90 / depósito
4. Cheque queda en estado Pendiente → job diario al vencer → pasa a Acreditado → notificación in-app
5. Pago impacta CC del proveedor y CC del local

### Proceso de caja y proyección
1. Ventas → movimientos de ingreso en CC y caja mensual
2. Pagos a proveedores + gastos varios → movimientos de egreso
3. Proyección: promedio últimos 3 meses + cheques por vencer + OCs pendientes = ingresos/gastos estimados próximo mes
4. Si gastos comprometidos > ingresos proyectados → alerta de déficit en dashboard

---

## Máquinas de estados confirmadas (6)

**Lead:** Nuevo → Contactado → Presupuesto enviado → Vendido / Perdido
*(también: Contactado → Visita programada / Entrega programada)*

**Presupuesto:** Borrador → Enviado → [Aprobado → Convertido | Rechazado | Expirado]

**Venta:** Pendiente → Pagada parcialmente → Pagada → [Con entrega pendiente → Entregada] / Cancelada

**Entrega:** Pendiente → En camino → Entregada / No entregada (reagendar)

**Orden de compra:** Borrador → Confirmada → Recibida / Cancelada

**Cheque:** Pendiente → Acreditado *(automático, job diario)* / Rechazado *(manual)*

---

## Criterios de aceptación — módulos nuevos

**M11 — CC Local**
- CA-N1: Cada venta genera automáticamente un movimiento de ingreso en la CC
- CA-N2: Cada pago a proveedor y gasto genera un movimiento de egreso en la CC
- CA-N3: El saldo actual de la CC es visible en todo momento con detalle de movimientos

**M12 — Compras a proveedores**
- CA-N4: OC con múltiples líneas de producto, cantidad y precio de compra
- CA-N5: Al marcar OC como "Recibida", el stock de cada producto se incrementa automáticamente
- CA-N6: Los pagos de la OC soportan efectivo, transferencia, cheque y depósito
- CA-N7: El saldo pendiente de pago de la OC actualiza la CC del proveedor

**M13 — CC Proveedores**
- CA-N8: Saldo adeudado por proveedor con historial de movimientos y pagos
- CA-N9: Los pagos registrados en OCs actualizan automáticamente el saldo del proveedor

**M14 — Cheques**
- CA-N10: Cheque con monto, fecha de vencimiento y cuota (30/60/90 días)
- CA-N11: Cheques con vencimiento en los próximos 30 días aparecen en el dashboard como alerta
- CA-N12: Al pasar la fecha de vencimiento, el cheque pasa automáticamente a "Acreditado" con notificación in-app
- CA-N13: El Administrador puede registrar manualmente un cheque como "Rechazado"

**M15 — Caja mensual**
- CA-N14: Ingresos y egresos del período con filtro de fechas y totales
- CA-N15: Comparativo con el mes anterior visible en la misma vista

**M16 — Aumento masivo de precios**
- CA-N16: Selección de criterio: por marca, por categoría o por modelo
- CA-N17: Selección de precio objetivo: precio de compra, precio de venta, o ambos
- CA-N18: Previsualización obligatoria antes de confirmar — muestra precio actual y nuevo precio para cada producto afectado
- CA-N19: El aumento se aplica solo al confirmar explícitamente después de la previsualización

**M17 — Proyección financiera**
- CA-N20: Promedio de ingresos y gastos de los últimos 3 meses calculado automáticamente
- CA-N21: Compromisos futuros mostrados: cheques por vencer + OCs pendientes de pago en el período
- CA-N22: Alerta visible si gastos comprometidos > ingresos proyectados
- CA-N23: El Administrador puede cambiar el período base de la proyección (1, 3 o 6 meses)

**M18 — Gastos varios**
- CA-N24: Gasto con monto, categoría (alquiler / servicios / sueldos / flete / otro), descripción, forma de pago y fecha
- CA-N25: Cada gasto genera movimiento de egreso en CC del local y en la caja del período

---

## Permisos por rol — actualizados

| Acción | Administrador | Vendedor |
|---|---|---|
| Gestionar catálogo y precios | ✓ | ✗ |
| Aumento masivo de precios | ✓ | ✗ |
| Gestionar stock manual | ✓ | ✗ |
| Ver/gestionar leads | ✓ | ✓ |
| Crear presupuestos | ✓ | ✓ |
| Registrar ventas | ✓ | ✓ |
| Registrar entregas y cobros | ✓ | ✓ |
| Emitir facturas ARCA | ✓ | ✓ |
| Gestionar compras a proveedores | ✓ | ✗ |
| Ver CC proveedores | ✓ | ✗ |
| Gestionar cheques | ✓ | ✗ |
| Registrar gastos varios | ✓ | ✗ |
| Ver CC local y caja mensual | ✓ | ✗ |
| Ver proyección financiera | ✓ | ✗ |
| Ver dashboard completo | ✓ | Parcial (sin financiero) |
| Gestionar usuarios | ✓ | ✗ |
| Configurar bot WhatsApp | ✓ | ✗ |

---

## Supuestos confirmados

- Sistema web responsivo — mobile-friendly obligatorio para vistas de entrega y cobro
- Un único punto de venta AFIP (local)
- Responsable Inscripto — emite Factura A y B
- Ventas solo al contado — no hay clientes con deuda / fiado (P5-A)
- CC del local = balance interno, sin deudores de clientes (P1-A)
- Gastos operativos (alquiler, servicios, sueldos, fletes) se registran en el sistema (P2-B)
- Recepciones de OC siempre completas — sin entregas parciales de proveedores (P3-A)
- Proyección calculada con promedio histórico + compromisos futuros (P4-B)
- Un solo local / una sola caja

## Exclusiones confirmadas
- App móvil nativa
- E-commerce / carrito de compras
- Integración con sistemas contables externos
- Multi-sede / multi-punto de venta
- Transportistas externos (OCA, Andreani)
- Clientes con cuenta corriente / fiado (P5-A)
- Recepciones parciales de OC (P3-A)

---

## Banderas tempranas — v2

| Bandera | Estado |
|---|---|
| Migración EF | Sí — proyecto nuevo, ~22 entidades estimadas |
| Integración ARCA WSAA + WSFE | Confirmada — con selección de ítems parciales |
| Integración WhatsApp Cloud API | Confirmada — referral Meta + preguntas por producto |
| IHostedService — acreditación automática cheques | **Nueva — job diario crítico** |
| 6 máquinas de estado | Confirmadas |
| Módulos financieros con lógica sensible | CC local, caja, cheques, proyección |
| QuestPDF — presupuestos y facturas | Confirmada |

---

## Riesgos y supuestos

| Riesgo | Nivel | Detalle |
|---|---|---|
| Job acreditación cheques: idempotencia | Alto | Debe acreditar exactamente una vez por cheque. Patrón idéntico al job diario de ganadería. |
| Proyección financiera: precisión percibida | Medio | El cliente puede esperar más precisión de la que un promedio simple puede dar. Fijar expectativas en el documento al cliente. |
| Hosting SMARTEASP: job diario compatible | Bajo | Ganadería ya usa el mismo patrón. Compatible confirmado. |
| Certificado ARCA (.p12) del cliente | Medio | Solicitar al cliente antes de iniciar módulo M7. |
| Número WhatsApp dedicado | Medio | Solicitar antes de iniciar M8. |
| Alcance de M9 dashboard puede crecer | Medio | Definir KPIs fijos antes del diseño — no dejar abierto. |

---

## Componentes reutilizables identificados

| Componente | Fuente | Reutilización en marihogar |
|---|---|---|
| `WhatsAppClient.cs` + `MessagingService.cs` | BotPublicitario | M8 — portar a .NET 10 MVC |
| Patrón AFIP WSAA + WSFE (.p12, token 24h) | delicias-naturales | M7 — reimplementar en .NET 10 |
| Job diario idempotente + IHostedService | ganadería | M14 — acreditación automática de cheques |
| Patrón cheques 30/60/90 (cuotas con vencimiento) | ganadería | M14 — referencia directa de implementación |
| Aumento masivo de precios con previsualización | ShowroomGriffin | M16 — reutilizar patrón |
| Stock manual con ajuste | ShowroomGriffin | M3 — reutilizar patrón |

---

## Discovery + Análisis v3 — Feedback de la primera demo (2026-07-27)

Etapa 1 ya en producción. El cliente usó el sistema y trajo 7 pedidos de cambio + 2 tareas de análisis. Se trata como **change request sobre un sistema ya entregado**, no como alcance nuevo desde cero — impacta el presupuesto ya cerrado de Etapa 1 y requiere re-presupuesto propio (ver `4-presupuestador.md`).

### Fuente de reutilización obligatoria
`ganaderia - emo` (`C:\Sistemas\ganaderia - emo`, ver `ruta_repositorio` en su `metadata.md`):
- `Ganaderia.Domain/Entities/Ganaderia/FacturaVenta.cs` — patrón exacto de impuestos editables (Subtotal, `PorcentajeIva`/`MontoIva`, `PorcentajeIIBB`/`MontoIIBB`, `PorcentajeOtrasPercepciones`/`MontoOtrasPercepciones`, Total) a reutilizar para CR-1. No modela tipo de comprobante A/B/C ni "facturado/en negro" — eso es concepto nuevo de este proyecto (no tiene precedente en ganadería, se documenta como tal).
- `Ganaderia.Domain/Entities/Ganaderia/FacturaVentaIngreso.cs` + `Enums/Ganaderia/PlazoCuotas.cs` — patrón de cuota calculada a 30/60/90 días desde una fecha base. Marihogar ya lo reutilizó parcialmente en Sprint 4 (`Cheque.Cuota`), pero sin un campo de fecha base explícito (`FechaEmision`) separado de `FechaVencimiento` — ver CR-2.

### CR-1 — Orden de compra: tipo de comprobante + impuestos discriminados
- **Contexto real**: el informe de Compras exportado (`Importacion/Informe de Compras...xlsx`, 239 compras / 464 líneas) confirma que cada compra tiene Tipo (A/B, a veces vacío = sin factura) y Nº de comprobante — el pedido del cliente de A/B/C + "facturado o en negro" es exactamente ese dato histórico.
- **CA-CR1.1**: Al confirmar/cargar una Orden de Compra, el Administrador elige: Facturada (Tipo A/B/C) o No facturada ("en negro"). Si es Facturada, Tipo es obligatorio; si es No facturada, no aplica.
- **CA-CR1.2**: La OC suma un bloque de impuestos editable: % IVA (+ monto calculado, editable), % Ingresos Brutos (+ monto), % Otros impuestos (+ monto) — mismo patrón que `FacturaVenta` de ganadería. Base de cálculo sugerida: Subtotal para IVA; Subtotal + IVA para IIBB y Otros (igual que ganadería).
- **CA-CR1.3**: `Total = Subtotal + MontoIVA + MontoIIBB + MontoOtrosImpuestos`. El `Subtotal` ya existe hoy como suma de líneas (`OrdenCompraItem`) — el cambio es agregar los 3 bloques de impuesto y que `OrdenCompra.Total` pase a ser este total con impuestos (hoy es solo la suma de líneas).
- **Impacto**: `OrdenCompra` gana `TipoComprobante` (enum: A/B/C, nullable), `Facturada` (bool), `PorcentajeIva`/`MontoIva`, `PorcentajeIIBB`/`MontoIIBB`, `PorcentajeOtrosImpuestos`/`MontoOtrosImpuestos`. **Rompe el criterio ya vigente `OrdenCompraDetailDto.MontoPagado`/Proyección financiera de que el saldo de OC se compara contra `Total`** — como `Total` va a incluir impuestos ahora, cualquier OC ya cerrada con pagos completos (Total = suma de pagos, sin impuestos) puede quedar con saldo "pendiente" fantasma tras la migración. Requiere decidir: ¿las OC ya cerradas se recalculan con impuesto 0% (no cambia su saldo), o quedan tal cual? — **se fija impuesto 0% por defecto en la migración para las OC históricas**, así ninguna OC ya cerrada cambia de saldo.

### CR-2 — Cheque: fecha de emisión + cálculo de vencimiento a 30/60/90
- **CA-CR2.1**: El formulario de pago con cheque (dentro de Pago de OC) pide **Fecha de emisión** del cheque (nueva) además de Cuota (30/60/90, ya existe). **Fecha de vencimiento** se calcula automáticamente como Emisión + Cuota, pero queda editable por si el cheque real no cae exacto en esa cuenta de días (mismo criterio de "sugerido pero editable" que ganadería usa para sus impuestos).
- **Impacto**: `Cheque` gana `FechaEmision` (DateTime, requerido). Sin impacto en la máquina de estados ni en `ChequeAcreditacionHostedService` (que sigue mirando `FechaVencimiento`, sin cambios por este ítem — el cambio de acreditación manual es CR-7, independiente).

### CR-3 — Nuevas formas de pago en Ventas
- **CA-CR3.1**: Nueva forma de pago "Tarjeta de crédito": exige elegir cantidad de cuotas (3/6/9/12) y permite cargar un % de interés por la financiación (puede quedar en 0/vacío — CA explícita del cliente: "el interés puede ser nulo"). El monto de la línea de pago es el monto financiado; el interés es informativo (no se sofistica un desglose de intereses por cuota en esta ronda — si el cliente lo pide, es un ítem aparte).
- **CA-CR3.2**: Nueva forma de pago "Banco Carrefour" — confirmado como medio real usado por el cliente (aparece en el histórico de Gastos importado: `Medio de pago = "carrefour"`).
- **Impacto**: `MetodoPago` (compartido Venta/OC, ver `3-arquitecto-mvc.md`) gana `TarjetaCredito` y `BancoCarrefour`. `PagoVenta` gana `CantidadCuotas` (int?, solo aplica si Metodo=TarjetaCredito) y `PorcentajeInteres` (decimal?, idem). **Riesgo de alcance**: `MetodoPago` es compartido con `PagoOrdenCompra` — Tarjeta de crédito/Banco Carrefour quedan disponibles también como forma de pago a proveedores salvo que se filtren explícitamente en el ViewModel de OC (igual patrón ya usado para excluir Cheque/Depósito de Ventas) — a definir en Diseño cuál es la lista permitida por contexto.

### CR-4 — Descargar y enviar comprobante por WhatsApp
- **CA-CR4.1**: Botón "Descargar PDF" en el detalle de Venta/Comprobante AFIP (ya existe para Comprobante AFIP desde Sprint 6; falta agregarlo también al Presupuesto — ya existe — y confirmarlo visible en Venta).
- **CA-CR4.2**: Botón "Enviar por WhatsApp", visible solo si `Venta.ClienteTelefono` tiene dato cargado. **Mecanismo confirmado con el cliente**: el botón genera un link `wa.me` con un mensaje prellenado que incluye un **link de descarga público** al PDF del comprobante (no adjunta el archivo directo — limitación real de WhatsApp, no es posible adjuntar un archivo automáticamente desde un link, confirmado explícitamente con el cliente).
- **Impacto nuevo (no trivial)**: requiere un endpoint de descarga de PDF **sin autenticación** (accesible desde el link que se comparte por WhatsApp, que el cliente del comprador abre fuera del sistema) protegido por un token opaco no adivinable (ej. GUID en la URL, no el Id incremental de la Venta/Comprobante) para no exponer comprobantes de otras ventas. Riesgo de seguridad a mitigar explícitamente en Arquitectura.

### CR-5 — Categorías de gasto fijas + catch-all
- **Contexto real**: el histórico de Gastos (`Importacion/Informe de Gastos...xlsx`, hoja "Gastos", 481 filas) tiene 16 categorías libres reales (Empleados 47, comisiones mercado pago 43, Oficina 37, Impuestos 35, APR 30, Marketing 27, tarjetas 24, Servicios Profesionales 23, cobro cheque 14, CONTAGRAM 9, comisión tarjeta naranja 6, NAFTA FLETE 5, Préstamo hipotecario 3, más "tato"/"oscar gasto"/"aclho" — retiros/gastos personales del dueño, 177 filas en total). Ninguna de las 5 categorías pedidas por el cliente (Sueldos/Impuestos/Luz/APR/Publicidad) cubre más de la mitad de estos casos reales.
- **CA-CR5.1**: `CategoriaGasto` pasa a: Sueldos, Impuestos, Luz, APR, Publicidad, **Otro** (agregado tras confirmar con el cliente — evita perder precisión en gastos reales que no encajan, ver pregunta resuelta arriba).
- **CA-CR5.2 (breaking change de datos)**: el enum actual (Alquiler=1/Servicios=2/Sueldos=3/Flete=4/Otro=5) cambia de significado en varios valores numéricos. Los 29 `Gasto` ya cargados (dev + producción, ver copia de datos del 27/07) deben re-mapearse explícitamente antes de aplicar la migración: Alquiler→Otro, Servicios→Luz *(a confirmar con el cliente caso por caso si corresponde)*, Sueldos→Sueldos (sin cambio de significado, pero cambia el valor int subyacente), Flete→Otro, Otro→Otro. **Mapeo automático 1 a 1 no es seguro sin revisar los 29 registros uno por uno** — se hace como paso explícito de la migración de datos, no una migración EF ciega de valores.
- **Mapeo propuesto histórico → nuevas categorías** (para el importador del histórico completo, CR-6): Empleados/tato/oscar gasto/aclho → Otro (retiros personales, no hay categoría "Retiro socio" pedida); comisiones mercado pago/tarjetas/comisión tarjeta naranja/cobro cheque → Otro; Oficina/Servicios Profesionales/CONTAGRAM/NAFTA FLETE/Préstamo hipotecario → Otro; Impuestos → Impuestos; APR → APR; Marketing → Publicidad. **Confirmado por el cliente (2026-07-27): "Marketing"→Publicidad y "APR"→APR son correctos.**

### CR-6 — Análisis de los archivos de `/Importacion` (tarea de análisis, no de implementación en esta ronda)
4 archivos Excel exportados del sistema anterior (Contagram), revisados con Excel COM:

| Archivo | Filas de detalle | Contenido | Gaps vs. sistema actual |
|---|---:|---|---|
| `Listado de Proveedores...xlsx` | 32 | Id, alias, Nombre/Apellido, Email, 2 Teléfonos, Dirección/Localidad/Provincia, DNI/CUIT, Condición de IVA, Razón Social, Domicilio/Localidad/Provincia/CP fiscal, Fecha y Saldo Inicial, Observaciones | `Proveedor` actual solo tiene RazonSocial/CUIT/Telefono/Email/Direccion — ver CR ampliación acordada arriba. |
| `Informe de Compras...xlsx` | 464 líneas / ~239 compras (Id repetido por línea de producto) | Id, Fecha, Vencimiento, Categoría, Proveedor, CUIT, Tipo (A/B/vacío), Nº Factura, Producto, Cantidad, Costo | Sin Tipo de comprobante/impuestos hasta CR-1. Los productos del histórico son texto libre (nombre), **no** coinciden 1 a 1 con el catálogo ya cargado (8 productos de demo) — importar Compras exige primero decidir cómo resolver/crear productos on-the-fly o requiere catalogar antes. |
| `Informe_de_Ventas_Detallado...xlsx` | 983 líneas / ~634 ventas | Id, Emisión, Vencimiento, Categoría, Cliente, CUIT/DNI, **ARCA** (estado envío AFIP: "Sin Enviar" en casi todas), Tipo, Tipo de Comprobante (FC/FCB), Nº Factura, Vendedor, Producto | La columna "ARCA" confirma que casi ninguna venta histórica fue facturada realmente ante AFIP — **no se re-facturan retroactivamente** (quedarían mal fechadas/duplicadas ante el fisco); se importan como Ventas confirmadas sin `ComprobanteAfip` asociado. Cliente casi siempre "Consumidor Final" genérico (CUIT 11111111) — no hay entidad Cliente en el sistema hoy (Venta solo tiene `ClienteNombre`/`ClienteTelefono` texto libre), consistente con el modelo actual. |
| `Informe de Gastos...xlsx` | 481 | Ver CR-5 | Categorías libres vs. enum fijo (CR-5). `Medio de pago` real (Mercado Pago, Caja del Local, Banco Provincia, cuenta DNI, Banco Galicia, tarjeta naranja, Cheque Propio, Banco Carrefour, etc.) es mucho más rico que el `FormaPagoGasto` actual (5 valores) — mismo tipo de gap que motivó CR-3 para Ventas; a resolver en Diseño con un mapeo explícito, no necesariamente ampliando el enum 1 a 1 con cada banco real. |

**Conclusión de CR-6**: la importación real del histórico (crear los 634+239+481+32 registros en el sistema) es un trabajo aparte de construir las pantallas de CR-1 a CR-5 — es un script de import dedicado (mismo patrón que `tools/SeedTestData/` ya usado, pero leyendo estos 4 Excel reales en vez de generar datos ficticios) que requiere las 3 decisiones ya resueltas con el cliente (WhatsApp, categorías, campos de Proveedor) más el mapeo Producto/histórico→catálogo antes de poder ejecutarse. Se presupuesta como ítem propio en `4-presupuestador.md`.

**Decisión del cliente (2026-07-27) — los Excel son la fuente de verdad, no lo que hay hoy en producción**: todo lo que hay actualmente en producción en Productos/Categorías/Marcas/Stock/Presupuestos/Ventas/CC Local/Proveedores/Compras/CC Proveedores/Cheques/Gastos es dato de prueba (la copia local→prod del 2026-07-27, más lo que el cliente cargó explorando el sitio — incluido su propio Proveedor "Prueba" y sus 2 Órdenes de Compra reales de prueba). Antes de correr el importador del histórico real, **se vacían esas tablas en producción por completo** (no un merge/dedupe con lo ya cargado). Ver plan de ejecución y salvaguardas en `3-arquitecto-mvc.md` (sección CR-6 actualizada) — acción destructiva sobre producción, requiere confirmación explícita del cliente en el momento de ejecutarla, no solo en el análisis.

### CR-7 — Cheques: acreditación manual, no automática
- **Cambio de arquitectura real**: hoy `ChequeAcreditacionHostedService` (Sprint 4) acredita el cheque automáticamente el día del vencimiento. El cliente pide que el job **solo avise** (notificación in-app, ya existe el mecanismo) al llegar la fecha de vencimiento, y que la acreditación sea siempre una acción manual del Administrador (botón "Acreditar" ya existe en la pantalla de detalle del cheque — hoy no se usa porque el job se adelanta solo).
- **CA-CR7.1**: El job diario, al detectar cheques `Pendiente` con `FechaVencimiento <= hoy`, **no cambia el Estado** — solo dispara la notificación in-app "Cheque Nº X venció, pendiente de acreditar" si todavía no se notificó ese cheque (evitar notificar todos los días de más una vez por cheque).
- **CA-CR7.2**: El Administrador acredita manualmente desde `Cheques/Index` o `Cheques/Details` — acción ya existe en el modelo (`EstadoCheque.Acreditado`), solo falta exponerla como acción de usuario en vez de dejarla exclusivamente al job.
- **Confirmación explícita ya vigente, sin cambio**: cheques solo aplican a Compras a proveedores (`PagoOrdenCompra`), nunca a Ventas — esto ya es así desde el diseño original (Sprint 4), el cliente lo reconfirma, no requiere cambio de código.
- **Impacto**: `Cheque` necesita un flag `Notificado` (bool) o reutilizar `Notification` existente con una consulta "¿ya se notificó este cheque?" antes de disparar una nueva. `ChequeAcreditacionHostedService.EjecutarSiCorrespondeAsync` cambia su lógica: de "acreditar" a "notificar sin acreditar".

## Discovery + Análisis v4 — Ampliación durante Sprint CR-A (2026-07-27, CR-8 y CR-9)

### CR-8 — Sugerir el total como monto por defecto al agregar un pago
- **Contexto**: hoy, tanto en el sub-formulario de pago de Venta como el de OrdenCompra, el campo Monto de una fila nueva de pago arranca vacío (o en 0) — el usuario siempre tiene que tipear el importe a mano, incluso cuando paga todo de una vez (el caso más común).
- **CA-CR8.1**: al agregar una fila de pago nueva (Venta o OC), el campo Monto se precompleta con el saldo pendiente de cobrar/pagar en ese momento (Total menos lo ya cargado en filas previas de la misma pantalla) — el usuario lo puede editar libremente si el pago es parcial o combinado.
- Alcance menor de UI (JS), sin impacto de datos ni de Service — coherente con los botones rápidos "Todo efectivo"/"Todo transferencia" que ya existen en Ventas (Sprint 2) y que hacen algo similar; CR-8 lo generaliza para que sea el comportamiento por defecto de cualquier fila nueva, no solo esos atajos.

### CR-9 — Reportes: distinguir ventas facturadas de no facturadas
- **Contexto**: con la Etapa 1 ya en producción, y confirmado por el histórico real (`Importacion/Informe de Ventas...xlsx`, columna "ARCA") que gran parte de las ventas de un negocio de este tipo no se facturan al momento, el cliente pide que el Dashboard, la Caja mensual y la Proyección financiera no traten todas las ventas como un bloque homogéneo — quiere poder ver cuánto de lo vendido está facturado y cuánto no.
- **CA-CR9.1**: el Dashboard Administrador (card "Ventas del período") desglosa el total en Facturadas / No facturadas (según si la Venta tiene un `ComprobanteAfip` con Estado=Emitido asociado, total o parcialmente).
- **CA-CR9.2**: Caja mensual agrega el mismo desglose en su resumen del período.
- **CA-CR9.3**: Proyección financiera deja explícito, en el promedio histórico de ingresos, qué proporción corresponde a ventas ya facturadas (informativo, no cambia la fórmula de proyección ya definida en M17 — evita que el cliente interprete el ingreso proyectado como "todo en blanco").
- No cambia ninguna regla de negocio existente (el ingreso en `MovimientoCCLocal` se sigue generando igual, facturada o no) — es exclusivamente una dimensión nueva de lectura en los reportes ya existentes.

## Discovery + Análisis v5 — Auditoría columna por columna de los 4 Excel históricos (2026-07-27)

Pedido explícito del cliente: no limitarse a las columnas ya usadas por `tools/ImportarHistorico/` (CR-6) — revisar **todas** las columnas de los 4 archivos de `Importacion/` (Proveedores, Compras, Ventas, Gastos), descartar las que están vacías, y para las que tienen datos reales sin propiedad equivalente hoy en el sistema, analizar cómo modelarlas. **Este análisis es independiente de la decisión pendiente de ejecutar CR-6 en producción (el cliente dijo "todavía no" el 2026-07-27) — no la asume ni la bloquea.** Auditoría hecha con Excel COM (fill-rate % y valores de muestra por columna, sobre las 4 hojas completas: 32 Proveedores, 464 líneas de Compras/239 compras, 983 líneas de Ventas/634 ventas, 481 Gastos).

### Columnas descartadas (vacías o sin variancia útil)
| Archivo | Columna | Fill rate | Motivo de descarte |
|---|---|---:|---|
| Proveedores | Nombre, Apellido, Email, Teléfono, Dirección, Localidad, Provincia, DNI, Observaciones | 0% | Sin un solo dato cargado en las 32 filas — el cliente nunca usó estos campos de contacto informal del proveedor (ya cubiertos por los campos fiscales reales, ver CR-6/Diseño v2). |
| Compras | Etiquetas | 0% | Sin dato en ninguna de las 464 líneas. |
| Ventas | Etiquetas | 0% | Ídem. |
| Compras / Ventas | Categoría | Compras: 96,7% "Productos Terminados" + 2,8% vacío / Ventas: 96,6% "Local" + 2,7% vacío + 0,5% "seña" + 0,2% "Online" | Sin variancia real de negocio en Compras (un único valor constante). En Ventas hay 5 filas con "seña" (posibles anticipos/señas, no ventas confirmadas) y 2 "Online" — volumen demasiado bajo (7 de 973 líneas) para justificar un campo nuevo ahora; se documenta como curiosidad de dato, no como gap a modelar. |
| Compras / Ventas | Afecta Stock | 100% "Sí" en ambos archivos (457/457 líneas de Compras, 973/973 de Ventas) | Uniforme en todo el dataset histórico — el comportamiento actual del importador (siempre suma/descuenta stock) no es un bug para estos datos. No se modela un flag editable ahora; si en el futuro el cliente carga una compra/venta que explícitamente no debe tocar stock (ej. servicio, no producto), es un pedido nuevo a evaluar en ese momento. |

### Columnas con dato real, ya cubiertas por CR-1 a CR-9 (sin gap nuevo)
Tipo de comprobante y N° de factura de Compras (CR-1), impuestos discriminados de Compras (CR-1), Total con impuestos de Compras/Ventas (decisión ya tomada en CR-1: se importa Subtotal, impuesto 0% para históricos), forma de pago con cheque (CR-2), categoría de Gasto (CR-5), estado ARCA de Ventas (CR-6, ya documentado — no se re-facturan retroactivamente).

### Columnas con dato real, sin propiedad equivalente hoy — gaps nuevos

**CR-10 — Orden de compra: Punto de Venta + Número de comprobante**
- **Contexto real**: `Informe de Compras...xlsx` tiene columnas "Punto de Venta" y "Nº Factura" 100% completas para las líneas con Tipo de comprobante cargado (A/B). Hoy `OrdenCompra` (post CR-1) sabe si está `Facturada` y su `TipoComprobante`, pero no guarda el número real del comprobante del proveedor — no hay forma de buscar/conciliar una compra puntual contra la factura física o un reclamo del proveedor.
- **CA-CR10.1**: cuando `Facturada = true`, el formulario de Orden de Compra permite cargar Punto de Venta (texto corto, ej. "0001") y Número de Comprobante (texto corto, ej. "00001234") — ambos opcionales (no bloquean guardar si el usuario no los tiene a mano en el momento), pero visibles en el listado/detalle para búsqueda.
- **Impacto**: `OrdenCompra` gana `PuntoVenta` (string?) y `NumeroComprobante` (string?). Sin impacto en cálculos ni migraciones de datos existentes (nullable, no rompe OC ya cargadas).

**CR-11 — Gasto: Subcategoría como campo propio (no solo texto de respaldo)**
- **Contexto real**: `Informe de Gastos...xlsx` tiene "Subcategoría" 100% completa con detalle real de negocio (ej. "Gastos Bancarios PCIA y payway", "Sueldo Empleado X") — mucho más rico que la `Categoria` fija de 6 valores (CR-5). El importador de CR-6 ya la usa como *fallback* de `Descripcion` cuando esta última viene vacía, pero queda mezclada en un campo de texto libre sin poder filtrar/reportar por subcategoría real.
- **CA-CR11.1**: `Gasto` gana un campo `Subcategoria` (string?, libre — no enum: el catálogo real tiene demasiada variedad como para forzar un cierre exhaustivo, mismo criterio que ya motivó el valor "Otro" en `CategoriaGasto`). Se muestra en el listado de Gastos y es filtrable por texto junto al filtro de categoría ya existente.
- **Impacto**: bajo. 1 campo nuevo en `Gasto` + ajuste al importador de CR-6 (que pasa a cargar `Subcategoria` = columna real, dejando `Descripcion` para lo que ya tenía) — **CR-6 todavía no se ejecutó en producción, así que este cambio no requiere tocar datos ya cargados, solo el script antes de la corrida real**.

**CR-12 — Venta: nota interna libre**
- **Contexto real**: `Informe_de_Ventas_Detallado...xlsx` tiene "Nota Interna" 68,2% completa (663 de 973 líneas) con detalle real de cómo se cobró o alguna aclaración de la venta (ej. "visa 6p", "transferencia bco galicia", "sena $10000 resto contra entrega"). Hoy `Venta` no tiene ningún campo de texto libre — ni para preservar este dato histórico, ni para que el Vendedor/Administrador anote algo similar a futuro (ej. "cliente pidió factura a nombre de otra persona").
- **CA-CR12.1**: `Venta` gana `NotaInterna` (string?, libre, visible en el detalle de Venta para Administrador/Vendedor — **nunca** en el remito/comprobante que ve el cliente final, es información interna del negocio).
- **CA-CR12.2**: el importador de CR-6 vuelca el texto real de "Nota Interna" en este campo en vez de descartarlo. No cambia la decisión ya tomada en CR-6 de importar un único `PagoVenta` consolidado en Efectivo (parsear el método real de pago desde texto libre para reconstruir múltiples líneas de pago históricas es fuera de alcance — la nota queda como referencia legible, no como dato estructurado de pago).
- **Impacto**: bajo. 1 campo nuevo en `Venta` + ajuste al importador de CR-6 (sin tocar datos ya cargados, mismo motivo que CR-11).

### Gaps identificados pero NO recomendados para esta ronda (documentados, no presupuestados)
- **IVA discriminado por alícuota (2,5/5/10,5/21/27%), Percepción IVA, Percepción IIBB, Impuestos Internos, Importe Neto Gravado/No Gravado/Exento** (Compras y Ventas, ~90-100% completos donde aplica): granularidad fiscal real del sistema anterior, pero CR-1 ya definió que las Órdenes de Compra históricas se importan con impuesto 0% (decisión ya tomada, no se reabre) y las Ventas no se re-facturan retroactivamente (CR-6). Modelar este nivel de detalle solo tendría valor si el cliente pide reportes fiscales históricos específicos — no hay ese pedido hoy. Se documenta para no perder el dato de origen (sigue existiendo en los Excel originales, no en el sistema).
- **Proveedor por línea de Venta** (99,5% completo en Ventas — indica de qué proveedor salió el producto vendido): trazabilidad venta→proveedor no existe hoy (`VentaItem` no tiene FK a `Proveedor`). Tendría valor para análisis de rentabilidad por proveedor, pero es un cambio estructural más grande (no un campo suelto) y no fue pedido por el cliente — se deja documentado como posible ítem de una futura ronda si el cliente pide ese análisis.
- **Descuento en % / Descuento en $** (Compras y Ventas, 100% completos pero casi siempre en 0 — variancia real baja): el `Total`/`Subtotal` histórico ya viene neto del descuento aplicado en su momento, así que no hay un monto "perdido" al no modelarlo aparte; solo se pierde la apertura informativa de cuánto fue descuento vs. precio de lista. Bajo valor, se descarta para esta ronda.

### Fuente de reutilización obligatoria
Ninguno de los 3 gaps (CR-10/11/12) tiene precedente de código en otros proyectos del estudio — son campos simples (string nullable) sobre entidades ya existentes, sin patrón externo que reutilizar más allá de lo que ya aplica el propio proyecto (mismo criterio de campo opcional ya usado en `Proveedor.Observaciones`).

## Discovery + Análisis v6 — CR-13: Ventas históricas con factura real (corrección a la conclusión de CR-6)

Pedido/corrección explícita del cliente: "todas las ventas que tienen número de comprobante y punto de venta están facturadas. Este dato se tiene que guardar en el modelo de facturación y migrar datos correspondientes."

### CR-13 — Ventas históricas: crear `ComprobanteAfip` real cuando hay Punto de Venta + Nº de Factura
- **Contexto real (reconteo hecho sobre el pedido del cliente)**: `Informe_de_Ventas_Detallado...xlsx` tiene columnas "Punto de Venta" (col. 10) y "Nº Factura" (col. 11) que la auditoría de columnas anterior (Análisis v5) no había separado como su propio hallazgo — quedaron mezcladas conceptualmente con la columna "ARCA" que motivó la conclusión original de CR-6 ("casi ninguna venta histórica fue facturada realmente ante AFIP"). Reconteo exacto: **487 de 973 líneas (286 de 634 Ventas, ~45%) tienen Punto de Venta="1" y Nº de Factura reales** (no el placeholder "-"), con "Tipo de Comprobante" siempre presente en esas mismas 487 líneas (FCA=19 líneas / FCB=468 líneas — mapeo directo a `TipoComprobanteAfip.FacturaA`/`FacturaB`, ya usado por Etapa 1). **La columna "ARCA" resultó ser "Sin Enviar" en el 100% de los casos, tengan o no factura real** — no es indicador válido de si la venta se facturó, es el estado de un envío electrónico del sistema anterior que aparentemente nunca se completaba, no si existía o no un comprobante real. **Esto corrige la conclusión de CR-6**: no es que "casi ninguna" venta histórica se facturó — casi la mitad sí, y el dato está en el Excel, solo que en una columna distinta a la que se usó originalmente como criterio.
- **Distinción importante de alcance (para no confundir con "re-facturar retroactivamente", que CR-6 ya descartó correctamente y sigue descartado)**: esto NO es llamar a la AFIP ahora para emitir comprobantes con fecha pasada — eso seguiría siendo incorrecto y no se hace. Es **registrar en el sistema el hecho histórico real de que esa venta ya tenía un comprobante fiscal en su momento** (con los datos que sí tenemos: tipo, punto de venta, número), igual que CR-6 ya hace con Compras/Proveedores/Gastos — no se inventa ni se re-emite nada, se importa un hecho ya ocurrido.
- **CA-CR13.1**: el importador de CR-6 (`tools/ImportarHistorico/Program.cs`, sección Ventas), al procesar cada línea con Punto de Venta + Nº de Factura reales, crea (o completa, si ya se creó por otra línea de la misma Venta) un `ComprobanteAfip` asociado a esa Venta: `Estado=Emitido`, `TipoComprobante` mapeado desde FCA/FCB, `PuntoVenta`/`NumeroComprobante` reales del Excel, `Total` = suma de líneas de esa Venta, `Fecha` = fecha de emisión de la Venta. `CAE=null`/`VencimientoCAE=null` — no hay CAE real disponible del sistema anterior (Contagram no integraba con AFIP vía web service, era otro mecanismo de facturación) — se documenta explícitamente como comprobante histórico importado, no uno emitido por este sistema.
- **CA-CR13.2**: verificado que ningún código existente asume `CAE != null` cuando `Estado == Emitido` — `ComprobanteAfipService.GenerarPdfAsync` interpola `CAE`/`VencimientoCAE` directamente en el PDF (`$"CAE: {c.CAE} ..."`), sin riesgo de excepción; el PDF de un comprobante histórico simplemente muestra "CAE: " en blanco — limitación cosmética aceptada, no un defecto a resolver en esta ronda.
- **Impacto en CR-9 (ya implementado en Sprint CR-B)**: el desglose Facturado/No facturado del Dashboard/Caja/Proyección financiera (`ComprobanteAfip.Estado=Emitido` asociado a la Venta) depende directamente de este dato — **sin CR-13, las 634 Ventas históricas figurarían 100% como "No facturadas" al importar**, lo cual sería incorrecto para el ~45% que sí lo estuvo. CR-13 no es solo un dato más: corrige la precisión de un reporte ya entregado y aprobado por el cliente.
- **Impacto de modelo**: **ninguno** — `ComprobanteAfip` ya tiene los 3 campos necesarios (`PuntoVenta` `int`, `NumeroComprobante` `long?`, `TipoComprobante` enum), sin necesidad de migración EF nueva. Cambio exclusivo en `tools/ImportarHistorico/Program.cs` (script todavía sin ejecutar contra `marihogar_dev` de nuevo ni contra producción).

### Nota de proceso
Este hallazgo se trata como corrección/ampliación del Change Request #1 ya en curso (mismo canal, mismo cliente, sin alcance nuevo de negocio — es una corrección de precisión sobre CR-6/CR-9 ya aprobados), no como un change request nuevo separado. Se implementa junto con CR-10/CR-11/CR-12 (Sprint CR-E), sin gate de presupuesto nuevo — mismo criterio ya usado para CR-8/CR-9 (adenda menor sobre trabajo ya aprobado, esfuerzo bajo por no requerir migración).

## Discovery + Análisis v7 — CR-14 a CR-18: mejoras post-migración pedidas por el cliente (2026-07-28)

Lote de 5 pedidos del cliente, algunos ya resueltos directamente como operación de datos, el resto a implementar en código.

### CR-14 — Saldo parcial (columna calculada) en CC Local y CC Proveedores
- **Contexto**: en los listados de movimientos de Cuenta Corriente del Local (M11) y de Cuenta Corriente de Proveedores (M13), hoy se ve cada movimiento individual (Ingreso/Egreso, monto) pero no el saldo acumulado hasta ese movimiento — el cliente necesita verlo para poder leer el estado de la cuenta en cualquier punto del historial, no solo el saldo final.
- **Aclaración de alcance**: no existe una "cuenta corriente del cliente" en el sistema (excluida desde el análisis original — ventas solo al contado, sin clientes con deuda). Se interpreta el pedido como aplicable a las 2 cuentas corrientes que sí existen: CC Local y CC Proveedores (por proveedor).
- **CA-CR14.1**: el listado de movimientos de CC Local (`Caja`/CC Local, orden cronológico) muestra una columna "Saldo" con el saldo acumulado (Σ Ingresos − Σ Egresos desde el primer movimiento hasta ese, inclusive) en cada fila.
- **CA-CR14.2**: el detalle de CC Proveedores (por proveedor, `Proveedores/Details` o pantalla equivalente) muestra la misma columna calculada, acumulada solo dentro de los movimientos de ese proveedor.
- **Impacto**: columna calculada en memoria (no persistida) — se ordena por Fecha (con desempate por Id para estabilidad) y se acumula en el servicio antes de mapear al DTO de listado, mismo criterio que otros cálculos derivados ya existentes en el proyecto (ej. `SaldoPendiente` de OC).

### CR-15 — OC: fecha de emisión de cheque por defecto hoy
- **Contexto**: confirmado con el cliente que los cheques **solo** se usan para pagar compras a proveedores, nunca se reciben como pago de una Venta (aclaración explícita del cliente — sin cambio en `Ventas/Create.cshtml`, que ya excluye Cheque de sus métodos de pago desde el diseño original).
- **Hallazgo real revisando el código de `OrdenesCompra/Details.cshtml`**: el campo "Fecha de emisión" del sub-formulario de pago con cheque (agregado en CR-2) arranca vacío — el usuario tiene que completarlo a mano siempre, y como el cálculo automático de "Fecha de vencimiento" depende de `Cuota` + `FechaEmision` (JS `autocalcularVencimientoCheque`), si el usuario no toca el select de Cuota (que visualmente ya muestra "30 dias" pero no escribe ese valor al estado hasta que el usuario lo cambia), el vencimiento tampoco se autocompleta.
- **CA-CR15.1**: al cambiar el método de una línea de pago a "Cheque", si no hay fecha de emisión cargada, se precompleta con la fecha de hoy (editable libremente) y la Cuota se precompleta en 30 días (editable), disparando el autocálculo de vencimiento ya existente. Múltiples líneas de pago en cheque ya están soportadas (cada fila del array `pagos` es independiente) — sin cambio ahí.
- **Impacto**: ajuste puntual de JS en `OrdenesCompra/Details.cshtml` (handler `change` de `.sel-metodo-oc`). "Pago parcial: $X de $Y" y "monto restante se autocompleta en la fila nueva" ya existen (CR-8, CA-CR8.1) — sin cambio ahí, el cliente los está redescubriendo/confirmando, no pidiendo algo nuevo.

### CR-16 — Normalización a mayúsculas: Proveedor y Producto
- **CA-CR16.1**: `Proveedor.RazonSocial` y `Producto.Nombre` se guardan siempre en mayúsculas — normalización server-side en el momento de crear/editar (`.ToUpperInvariant()` antes de persistir), no solo una limpieza de datos existentes.
- **Impacto**: cambio en `ProveedorService`/`ProductoService` (o el servicio equivalente de creación/edición de cada uno). Los datos ya cargados en `marihogar_dev` fueron normalizados directamente por el orquestador (ver `trazabilidad.md`, 2026-07-28) — sin filas pendientes.

### CR-17 — Unificar Proveedor duplicado (CUIT 30-50416354-3)
- **Contexto**: hallazgo de QA en Sprint CR-D (2 Proveedores con RazonSocial/CUIT idéntico, Id=1 e Id=2, "G P V SOCIEDAD ANONIMA"), ahora confirmado por el cliente como duplicado real a unificar.
- **Verificado antes de unificar**: los 2 registros son byte-idénticos en todos los campos fiscales (RazonSocial, CUIT, CondicionIva, domicilio/localidad/provincia/CP fiscal, SaldoInicial=0) — sin riesgo de pérdida de dato al elegir cuál sobrevive.
- **Resuelto directamente como operación de datos** (sin código nuevo — es un merge de filas, no un gap de funcionalidad): Id=1 sobrevive (26 Órdenes de Compra + 26 movimientos de CC previos), Id=2 se fusiona (18 OC + 18 movimientos reasignados a Id=1 mediante `UPDATE`, dentro de una transacción), Id=2 queda soft-deleted (`DeletedAt`, no se borra físicamente, mismo criterio `SoftDestroyable` del resto del sistema). CC Proveedor de Id=1 queda unificada automáticamente (el saldo se calcula como suma de movimientos por `ProveedorId`, ahora los 44 movimientos apuntan a Id=1). Ver `trazabilidad.md`, 2026-07-28, para el detalle de la operación y su verificación.

### CR-18 — Movimiento de ajuste de apertura: saldo en $0 después de importar el histórico
- **Contexto**: el cliente quiere que, una vez importado el histórico real (CR-6, todavía no ejecutado en producción), el saldo corriente de CC Local y de cada CC Proveedor arranque en $0 al momento en que el negocio empieza a operar de verdad con el sistema — sin perder el detalle histórico de movimientos (necesario para Caja mensual y Proyección financiera, que se basan en el histórico de `MovimientoCCLocal`).
- **Mecanismo acordado con el cliente**: movimiento de ajuste de apertura — al final de la importación, se calcula el saldo acumulado real de CC Local (Σ Ingresos − Σ Egresos de todo lo importado) y se postea un único movimiento adicional, con fecha igual a la del último movimiento importado (o el mismo instante de corte), de signo contrario y monto exactamente igual al saldo acumulado, con `Descripcion` explícita ("Ajuste de apertura — saldo migrado a $0 para inicio de operación real"). Mismo mecanismo, aplicado independientemente, para cada CC Proveedor con saldo != 0 tras la importación.
- **CA-CR18.1**: después de correr el ajuste, `SELECT SUM(caso Ingreso: Monto, caso Egreso: -Monto) FROM MovimientosCCLocal` = 0 exacto. Ídem por cada `ProveedorId` en `MovimientosCCProveedor`.
- **Impacto**: nuevo paso al final de `tools/ImportarHistorico/Program.cs` (después de las secciones existentes) — no toca ninguna entidad de negocio nueva, solo agrega movimientos de ajuste usando las mismas tablas ya existentes. **No se ejecuta el script en esta ronda** — se ajusta el código, mismo criterio que el resto de los cambios sobre este script pendientes de la corrida real (todavía en pausa por decisión del cliente).

### CR-13 (refinamiento) — Cliente CUIT en factura histórica
- Verificado (reconteo sobre el Excel) que el Cliente de las 487 líneas con factura real es uniformemente "Consumidor Final" con CUIT/DNI genérico "11111111" — no hay variancia real de cliente identificado. Se agrega de todos modos `ComprobanteAfip.ClienteCUIT` = ese dato tal cual viene del Excel (visible en el comprobante, aunque sea el valor genérico), completando "todos los datos que se dispongan" tal como pidió el cliente.

### CR-19 — Órdenes de Compra históricas: registrar pago total (pedido explícito del cliente, 2026-07-28)
- **Contexto**: pedido del cliente ("marcar todas las órdenes de compra como pagadas en su totalidad"). Las 239 OC importadas por CR-6 quedaban con `SaldoPendiente = Total` (limitación ya documentada: "el Excel no discrimina qué se pagó") — pero son compras reales del negocio, ya liquidadas en su momento con el proveedor. Mostrarlas como "pendientes de pago" en el sistema nuevo es engañoso.
- **CA-CR19.1**: el importador registra, para cada OC (todas quedan en estado `Recibida`), un pago total en Efectivo por el `Total` completo de la orden — mismo criterio ya usado para Ventas (un único pago consolidado cuando no hay detalle real de forma de pago, documentado desde CR-6).
- **Efecto en CC Proveedores**: al cubrir cada Cargo con su Pago exacto, el saldo de cada proveedor llega a $0 de forma natural — el movimiento de ajuste de apertura de CR-18 (que hasta ahora hacía ese trabajo con un único ajuste por proveedor) deja de ser necesario para CC Proveedores específicamente (su propia lógica lo detecta solo: si el saldo ya da 0, no postea nada). CC Local no se ve afectado — sigue necesitando su propio ajuste de apertura, ya que no depende de los pagos de OC.
- **Impacto**: cambio exclusivo en `tools/ImportarHistorico/Program.cs` (sección Compras) — sin cambio de modelo, sin migración EF.

## Discovery + Análisis v8 — CR-21/CR-22: doble precio de Producto + precio/subtotal editables en Ventas (2026-07-28)

Pedido explícito del cliente, ya en producción con datos reales. Impacta la pantalla de mayor uso diario del sistema (Ventas) — se trata con el mismo cuidado que la "Especificación UX elevada" original de esa pantalla.

### CR-21 — Producto: Precio Efectivo + Precio de Lista (+21%)
- **Pedido**: "el precio de venta de los productos tiene que ser 2, precio en efectivo y precio de lista. el precio de lista es con un 21% mas del precio en efectivo."
- **CA-CR21.1**: `Producto` pasa a tener un único precio de venta editable, **Precio Efectivo** (mismo campo que hoy es `PrecioVenta`, renombrado). **Precio de Lista** se muestra en el catálogo pero es **siempre calculado** como `PrecioEfectivo × 1,21`, redondeado a 2 decimales — no es un campo propio editable por separado, para que nunca pueda desincronizarse del Precio Efectivo (si el cliente hubiera pedido que ambos se puedan cargar de forma independiente, sería un campo nuevo con su propio riesgo de inconsistencia; tal como está pedido — "es con un 21% más" — es una regla fija, no un dato libre).
- **Impacto**: rename de columna (`PrecioVenta`→`PrecioEfectivo`, sin pérdida de datos, mismo valor). Todo lugar que hoy usa `Producto.PrecioVenta` para armar el precio por defecto de una línea (Ventas, catálogo, Aumento masivo de precios M16) sigue funcionando igual, solo cambia el nombre. `PrecioLista` es una propiedad de solo lectura (no mapeada a columna).

### CR-22 — Ventas: precio unitario y subtotal editables, con selector de IVA por línea
- **Pedido**: "al crear o editar una venta el usuario debe poder modificar el precio unitario del producto y el subtotal de la venta y que el total de la venta se calcule on demand [...] tener en cuenta esto a la hora de crear una venta para que el usuario pueda seleccionar precio efectivo y agregar o no el IVA."
- **Decisiones resueltas con el cliente** (`AskUserQuestion`):
  - El selector de "agregar IVA o no" es **por línea de producto**, no una única elección para toda la venta — cada producto del carrito puede independientemente cotizarse a Precio Efectivo o a Precio de Lista.
  - El Subtotal de cada línea es un **override manual real** (no solo un total que se recalcula solo) — se puede escribir un subtotal distinto de Cantidad × Precio Unitario (ej. para aplicar un descuento puntual), y ese valor pasa a ser lo que efectivamente se cobra por esa línea.
  - **Punto de seguridad crítico, identificado antes de tocar código**: hoy `VentaService.ConfirmarAsync` **nunca** confía en el precio que manda el navegador — siempre lo recalcula server-side desde `Producto.PrecioVenta`, a propósito, para que nadie pueda manipular el payload JSON (herramientas de desarrollador del navegador) y comprar más barato. Habilitar precio/subtotal editables implica sacar esa protección — **se resolvió con el cliente que solo el rol Administrador puede editar precio unitario y subtotal**; el Vendedor sigue viendo el precio de catálogo fijo, sin poder tocarlo, y el servidor sigue revalidando/forzando el precio de catálogo para cualquier request que no venga de un Administrador (nunca confiar solo en que la UI oculte el campo — la regla se aplica también server-side).
- **CA-CR22.1**: `VentaItem` gana un campo `Subtotal` propio (hoy no existe, el subtotal es un cálculo implícito Cantidad×PrecioUnitario) — así el override queda persistido como parte de la Venta, no solo como un cálculo de pantalla.
- **CA-CR22.2**: en `Ventas/Create`, si el usuario logueado es Administrador: Precio Unitario y Subtotal de cada línea son editables; un control por línea permite alternar el precio unitario entre Precio Efectivo y Precio de Lista del producto (ayuda rápida, sigue siendo editable a mano después); el Subtotal se recalcula automáticamente como Cantidad×PrecioUnitario mientras el usuario no lo haya tocado a mano — en cuanto lo edita directamente, ese valor queda fijo hasta que lo vuelva a tocar (no se pisa solo si cambia cantidad/precio después).
- **CA-CR22.3**: si el usuario logueado es Vendedor: sin cambios respecto de hoy — precio de catálogo fijo (Precio Efectivo), subtotal = Cantidad×PrecioUnitario, sin edición posible ni en pantalla ni server-side.
- **CA-CR22.4**: el Total de la venta = suma de los Subtotales de línea (ya no Cantidad×Precio recalculado aparte), y se actualiza en pantalla "on demand" (en vivo, sin recargar) a medida que se edita cualquier campo de cualquier línea — mismo patrón ya usado para cantidad.
- **Impacto**: `VentaItem.Subtotal` nuevo (migración con backfill `Cantidad×PrecioUnitario` para las 973 líneas ya existentes, sin cambiar ningún Total de Venta ya cerrada). `VentaService.ConfirmarAsync` cambia su regla de precio de "siempre servidor" a "servidor si Vendedor, cliente-validado si Administrador".

## Historial de ajustes
- 2026-07-28: Discovery + Análisis v8 — CR-21 (Producto: Precio Efectivo + Precio de Lista +21%, derivado) y CR-22 (Ventas: precio unitario/subtotal editables solo para Administrador, selector de IVA por línea, Total on-demand). Resueltas 2 decisiones de diseño con el cliente antes de tocar código: alcance del toggle de IVA (por línea) y naturaleza del subtotal editable (override manual real). Identificado y resuelto con el cliente un punto de seguridad real (el server hoy nunca confía en el precio del cliente) antes de implementar. Pendiente: Diseño, Arquitectura y Presupuesto.
- 2026-07-28: CR-19 — a pedido del cliente, el importador registra pago total (Efectivo) por cada Orden de Compra histórica. Verificado con la re-corrida real contra `marihogar_dev`: 239/239 OC con saldo pendiente $0, CC Proveedores en $0 sin necesitar ajuste de apertura (0 ajustes posteados, la lógica de CR-18 se auto-desactiva porque ya no hace falta), CC Local sin cambio (1 ajuste de apertura, sigue siendo necesario). Sin gate de presupuesto nuevo.
- 2026-07-28: Discovery + Análisis v7 — CR-14 (saldo calculado en CC Local/Proveedores), CR-15 (fecha de emisión de cheque por defecto en OC), CR-16 (mayúsculas Proveedor/Producto), CR-17 (unificación de Proveedor duplicado, resuelta directamente como dato), CR-18 (ajuste de apertura para saldo $0 post-import) y refinamiento de CR-13 (ClienteCUIT). CR-16 y CR-17 con componente de datos ya ejecutado en `marihogar_dev`. Sin gate de presupuesto nuevo — mismo criterio que CR-8/CR-9/CR-13 (adenda de bajo esfuerzo sobre el Change Request #1 ya aprobado).
- 2026-07-27: Discovery + Análisis v6 — CR-13, corrección del cliente sobre la conclusión de CR-6: ~45% de las Ventas históricas (286/634) sí tienen factura real (Punto de Venta + Nº de Factura), dato que estaba en el Excel pero no se había separado del análisis de la columna "ARCA" (que resultó no ser un indicador válido). Se crea `ComprobanteAfip` real para esas Ventas al importar — sin cambio de modelo, solo ajuste del importador. Corrige también la precisión futura de CR-9. Sin gate de presupuesto nuevo, se implementa junto a CR-10/11/12.
- 2026-07-27: Discovery + Análisis v5 — auditoría columna por columna de los 4 Excel de `/Importacion` (más allá de lo ya usado por CR-6), pedida explícitamente por el cliente. 3 gaps nuevos identificados y aceptados para presupuestar (CR-10 Nº de comprobante en OC, CR-11 Subcategoría de Gasto, CR-12 Nota interna de Venta), varios gaps documentados y descartados con motivo (IVA discriminado, Proveedor por línea de Venta, Descuento aparte). Independiente de la decisión pendiente de ejecutar CR-6 en producción. Pendiente: Diseño, Arquitectura y Presupuesto de esta ampliación.
- 2026-07-27: Discovery + Análisis v4 — CR-8 (sugerir total como monto de pago por defecto) y CR-9 (reportes de ventas/ingresos distinguen facturado vs. no facturado) agregados durante la ejecución del Sprint CR-A. Se presupuestan como adenda del Change Request #1, se implementan en Sprint CR-B.
- 2026-06-29: Discovery v1. 10 módulos. Sistema de captación y ventas.
- 2026-06-29: Análisis v1 cerrado. Presupuesto: $1,171 (con descuento 15% referido).
- 2026-07-06: Discovery v2. Relevamiento del sistema actual (Contagram). Alcance ampliado a 18 módulos — sistema de gestión comercial completo. Presupuesto v1 invalidado. P1-A/P2-B/P3-A/P4-B/P5-A confirmados. Análisis v2 cerrado. Pendiente: nuevo presupuesto.
- 2026-07-27: Discovery + Análisis v3 cerrado — feedback de la primera demo post-Etapa 1. 7 change requests (CR-1 a CR-7) + análisis de importación de datos históricos (`/Importacion`, 4 archivos Excel reales: 32 proveedores, 239 compras, 634 ventas, 481 gastos). 3 preguntas críticas resueltas con el cliente (mecanismo de envío WhatsApp, categoría "Otro" de resguardo en Gastos, ampliación de campos de Proveedor). Pendiente: Diseño, Arquitectura y Presupuesto de este change request.
