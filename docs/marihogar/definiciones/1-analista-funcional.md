# Memoria - Analista funcional

## Proyecto: marihogar *(nombre provisional — confirmar con cliente)*
## Ultima actualizacion: 2026-08-15

## Definiciones vigentes

> Nota de consolidación (2026-08-16): esta sección agrupa lo que antes eran 12 secciones de nivel 2 apiladas por fecha ("Análisis funcional v2" + "Discovery + Análisis v3" a "v14"). Se mantiene el contenido completo tal cual (sin resumir ni comprimir, dado su volumen y densidad de decisiones de negocio con cifras/CUIT/porcentajes exactos) bajo un único encabezado de nivel 2, ordenado cronológicamente — cada bloque documenta explícitamente cuándo corrige o amplía a uno anterior (ver especialmente CR-13 sobre CR-6, CR-23 sobre CR-6/CR-22, CR-27 sobre CR-19, CR-40 sobre CR-38). Ver `## Historial de ajustes` para el resumen de una línea por versión.

### Análisis funcional v2 — CERRADO 2026-07-06

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

### Módulos confirmados — 18 módulos

### Grupo 1 — Captación y ventas
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M1 | CRM de Leads | Leads desde WhatsApp, máquina de estados, historial | Media |
| M4 | Presupuestador | Cotización multi-línea, PDF | Media |
| M5 | Gestión de ventas | Multi-pago, estados, impacto automático en CC del local, envío WhatsApp (CR-4) | Alta |
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

### Procesos principales confirmados

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

### Máquinas de estados confirmadas (6)

**Lead:** Nuevo → Contactado → Presupuesto enviado → Vendido / Perdido
*(también: Contactado → Visita programada / Entrega programada)*

**Presupuesto:** Borrador → Enviado → [Aprobado → Convertido | Rechazado | Expirado]

**Venta:** Pendiente → Pagada parcialmente → Pagada → [Con entrega pendiente → Entregada] / Cancelada

**Entrega:** Pendiente → En camino → Entregada / No entregada (reagendar)

**Orden de compra:** Borrador → Confirmada → Recibida / Cancelada

**Cheque:** Pendiente → Acreditado *(automático, job diario)* / Rechazado *(manual)*

---

### Criterios de aceptación — módulos nuevos

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

### Permisos por rol — actualizados

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

### Supuestos confirmados

- Sistema web responsivo — mobile-friendly obligatorio para vistas de entrega y cobro
- Un único punto de venta AFIP (local)
- Responsable Inscripto — emite Factura A y B
- Ventas solo al contado — no hay clientes con deuda / fiado (P5-A)
- CC del local = balance interno, sin deudores de clientes (P1-A)
- Gastos operativos (alquiler, servicios, sueldos, fletes) se registran en el sistema (P2-B)
- Recepciones de OC siempre completas — sin entregas parciales de proveedores (P3-A)
- Proyección calculada con promedio histórico + compromisos futuros (P4-B)
- Un solo local / una sola caja

### Exclusiones confirmadas
- App móvil nativa
- E-commerce / carrito de compras
- Integración con sistemas contables externos
- Multi-sede / multi-punto de venta
- Transportistas externos (OCA, Andreani)
- Clientes con cuenta corriente / fiado (P5-A)
- Recepciones parciales de OC (P3-A)

---

### Banderas tempranas — v2

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

### Riesgos y supuestos

| Riesgo | Nivel | Detalle |
|---|---|---|
| Job acreditación cheques: idempotencia | Alto | Debe acreditar exactamente una vez por cheque. Patrón idéntico al job diario de ganadería. |
| Proyección financiera: precisión percibida | Medio | El cliente puede esperar más precisión de la que un promedio simple puede dar. Fijar expectativas en el documento al cliente. |
| Hosting SMARTEASP: job diario compatible | Bajo | Ganadería ya usa el mismo patrón. Compatible confirmado. |
| Certificado ARCA (.p12) del cliente | Medio | Solicitar al cliente antes de iniciar módulo M7. |
| Número WhatsApp dedicado | Medio | Solicitar antes de iniciar M8. |
| Alcance de M9 dashboard puede crecer | Medio | Definir KPIs fijos antes del diseño — no dejar abierto. |

---

### Componentes reutilizables identificados

| Componente | Fuente | Reutilización en marihogar |
|---|---|---|
| `WhatsAppClient.cs` + `MessagingService.cs` | BotPublicitario | M8 — portar a .NET 10 MVC |
| Patrón AFIP WSAA + WSFE (.p12, token 24h) | delicias-naturales | M7 — reimplementar en .NET 10 |
| Job diario idempotente + IHostedService | ganadería | M14 — acreditación automática de cheques |
| Patrón cheques 30/60/90 (cuotas con vencimiento) | ganadería | M14 — referencia directa de implementación |
| Aumento masivo de precios con previsualización | ShowroomGriffin | M16 — reutilizar patrón |
| Stock manual con ajuste | ShowroomGriffin | M3 — reutilizar patrón |

---

### Discovery + Análisis v3 — Feedback de la primera demo (2026-07-27)

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

### Discovery + Análisis v4 — Ampliación durante Sprint CR-A (2026-07-27, CR-8 y CR-9)

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

### Discovery + Análisis v5 — Auditoría columna por columna de los 4 Excel históricos (2026-07-27)

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

### Discovery + Análisis v6 — CR-13: Ventas históricas con factura real (corrección a la conclusión de CR-6)

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

### Discovery + Análisis v7 — CR-14 a CR-18: mejoras post-migración pedidas por el cliente (2026-07-28)

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

### Discovery + Análisis v8 — CR-21/CR-22: doble precio de Producto + precio/subtotal editables en Ventas (2026-07-28)

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

### Discovery + Análisis v9 — CR-23: corrección exhaustiva del importe y forma de pago de Ventas históricas (2026-07-29)

Pedido explícito del cliente tras revisar los datos ya migrados en producción: "el precio de las ventas migradas que se cargaron no coincide con el precio en el sistema [...] el metodo de pago tampoco coincide [...] Hacer un analisis mas exaustivo sobre las ventas para emparejar los datos."

### Hallazgo 1 — el importe migrado no incluía IVA ni descuento
Reconteo exhaustivo con muestras reales cruzadas contra columnas no usadas hasta ahora en detalle: "Precio Unitario" (col. 18) es el **precio neto por unidad, sin IVA** — verificado exacto contra "Importe Neto Gravado" (col. 29) en filas con `Cantidad=1`, y contra `Cantidad×PrecioUnitario = Importe Neto Gravado` en filas con `Cantidad>1` (ej. fila real: `PU=$14.876,00 × 2 = $29.752,00 = Importe Neto Gravado`). **"Total Venta" (col. 40) = Importe Neto Gravado × 1,21** (IVA 21%) — verificado exacto en múltiples muestras (`$29.752,00 × 1,21 = $35.999,92 = Total Venta` real de esa fila). CR-6/CR-22 usaban `Cantidad×PrecioUnitario` (sin IVA) como el monto de cada línea — el sistema quedó sistemáticamente por debajo del monto real facturado en cada venta migrada.

### Hallazgo 2 — el campo "Descuento en $" ya está absorbido en "Total Venta", no hace falta modelarlo aparte
31 líneas reales (de 973) tienen `Descuento en $` distinto de 0 — verificado que `Importe Neto Gravado = Subtotal sin Descuento − Descuento` (ej. `$24.628,00 − $17.239,60 = $7.388,40 = Importe Neto Gravado` de esa fila) y que "Total Venta" ya se calcula sobre ese neto post-descuento. **No se necesita un campo `Descuento` nuevo en `VentaItem`** — al usar directamente "Total Venta" como `Subtotal` de la línea (campo ya existente desde CR-22), el descuento queda reflejado automáticamente en la diferencia entre `Cantidad×PrecioUnitario` (bruto, sin descuento) y `Subtotal` (neto real cobrado) — exactamente el mismo mecanismo de "override" que CR-22 ya había diseñado para otro propósito (descuentos manuales del Administrador), reutilizado acá para el dato histórico real. 4 líneas tienen descuento del 100% (venta regalada/ajuste) — dan `Total Venta=$0`, correctamente reflejado, no es un dato faltante.

### Hallazgo 3 — la forma de pago real está en "Nota Interna" en más de la mitad de las ventas
CR-6 asumía "el Excel no discrimina forma de pago" y cargaba todo como Efectivo. Auditoría exhaustiva sobre las 634 ventas: **432 (68%) tienen Nota Interna con datos reales**, catalogados por patrón:

| Patrón detectado | Ocurrencias | Mapeo a `MetodoPago` |
|---|---:|---|
| "eft"/"efec" | ~160 | Efectivo |
| "mpo"/"mp"/"mercado pago" | ~125 | MercadoPago |
| "visa" | ~79 | TarjetaCredito (con cuotas si trae "Np") |
| "debito" | 15 | Transferencia (no hay TarjetaDebito en el enum; débito es movimiento bancario directo, no crédito) |
| "transf carre"/variantes con typo | ~11 | BancoCarrefour (más específico que Transferencia genérica) |
| "naranja" | 9 | TarjetaCredito |
| "master" | 8 | TarjetaCredito |
| "transf"/"trasnf" sin "carre" | 7 | Transferencia |
| Resto (nombres propios, "saldo", "cheque" ×2, "donacion", texto ambiguo) | ~17 | Catch-all Efectivo (documentado, mismo criterio que `CategoriaGasto`/`FormaPagoGasto`) |
| Sin Nota Interna | 202 (32%) | Catch-all Efectivo (sin dato disponible) |

**8 ventas reales tienen más de una forma de pago** en la misma Nota Interna, en líneas separadas con monto explícito (ej. `"$100.000 mpo\n$250000 visa 6p"`, suma exacta contra el Total real) — se importan como múltiples `PagoVenta`, igual que si se hubieran cargado a mano en el sistema. **2 ventas reales declaran un saldo pendiente** (`"eft\nrestan$29999"`) — antes se marcaban `Pagada` a la fuerza; ahora quedan `PagadaParcial` con el monto pendiente real, sin contar ese saldo como pago.

### Confirmado — Nota Interna → `Venta.NotaInterna` ya estaba correctamente migrado desde CR-12
No requirió cambio — se verificó que el campo ya se guarda tal cual desde la corrida anterior (432/634 con dato). La corrección de este análisis es exclusivamente sobre el **uso adicional** de esa misma columna para derivar la forma de pago real, no sobre el guardado del texto en sí.

### Impacto
Cambio exclusivo en `tools/ImportarHistorico/Program.cs` (sección Ventas): `VentaItem.Subtotal` pasa a leerse de "Total Venta" (antes `Cantidad×PrecioUnitario`); nuevo parser `ParsearFormasPagoVenta`/`MapearMetodoPagoVenta` reemplaza el pago único Efectivo hardcodeado; `Venta.Estado` se resuelve después de parsear los pagos (antes hardcodeado `Pagada`). Sin cambio de modelo — todos los campos ya existían (creados por CR-6/CR-12/CR-22). Requiere una nueva corrida completa del importador (vaciar + reimport) tanto en `marihogar_dev` como, con confirmación explícita del cliente, en producción — misma operación ya repetida varias veces en este proyecto.

### Discovery + Análisis v10 — CR-24: corrección de IVA en Ventas, Total editable, pagos posteriores (2026-07-30)

Pedido del cliente sobre el sistema ya en producción con datos reales (post CR-23).

### CR-24.1 — Bug real: el toggle de IVA descarta el precio editado a mano
`Ventas/Create.cshtml` (CR-22): al activar el botón "IVA" de una línea, el precio unitario se pisa con `Producto.PrecioLista` (fijo del catálogo) — si el Administrador ya había escrito un precio negociado distinto, se pierde. **CA-CR24.1**: el precio con IVA pasa a ser un valor **calculado en vivo** sobre lo que esté cargado en el campo de precio (`precio × 1,21`), no un salto a un valor fijo del producto — coincide con el Precio de Lista solo cuando el precio no fue editado (caso por defecto).

### CR-24.2 — Layout de precio de línea: 4 elementos
"el precio del producto es un input abierto con el precio efectivo configurado del producto, el boton de IVA, el precio con IVA calculado [...], y el subtotal que es un input abierto." **CA-CR24.2**: la columna de precio pasa a tener: (1) Precio (input abierto, default `Producto.PrecioEfectivo`), (2) botón IVA, (3) "Precio c/IVA" — calculado, solo lectura, = Precio×1,21, visible siempre como referencia, (4) Subtotal (input abierto, ya existente desde CR-22). El botón IVA decide cuál de los dos precios (con o sin IVA) alimenta el subtotal por defecto — el Subtotal sigue siendo editable a mano por separado (override, sin cambio de esa parte).

### CR-24.3 — Total de la venta editable, con reparto proporcional
"El total tambien debe poder modificarse, agregar una ultima linea al listado que sea total". **CA-CR24.3**: fila especial "Total" al final de la tabla de productos, con un input abierto. Al editarlo, la diferencia contra la suma actual de subtotales se reparte **proporcionalmente entre todas las líneas** según el peso de cada una en el total (decisión confirmada con el cliente vía `AskUserQuestion`) — no hay un campo de "Total" independiente en el modelo, el reparto ajusta los `Subtotal` de cada línea para que la suma coincida exacto con el valor tipeado. El "Resumen de venta" se actualiza en vivo con este valor.

### CR-24.4 — Pagos posteriores a la creación (nueva capacidad, mirror de Compras)
"luego de crear la venta que redirija al detalle de la venta [...] en este detalle quiero que me deje realizar pagos parciales hasta cubrir el total. actualmente solo se deja cargar pagos en el alta." **Confirmado por el cliente**: hoy Ventas no tiene equivalente de `PagoOrdenCompraService.RegistrarPagoAsync` (Compras sí permite pagar en cuotas después de crear la OC). **CA-CR24.4**: nueva capacidad `IPagoVentaService.RegistrarPagoAsync` (mismo patrón exacto que Compras: registra 1+ líneas de pago sobre una Venta ya `Pendiente`/`PagadaParcial`, revalida server-side que no se supere el saldo pendiente, recalcula `Estado`) + sub-formulario de pago en `Ventas/Details.cshtml` (mismo patrón visual que `OrdenesCompra/Details.cshtml`). **CA-CR24.5**: al confirmar una Venta desde `Ventas/Create`, el flujo pasa a redirigir directo a `Ventas/Details` (antes se quedaba en una pantalla de éxito dentro de la misma página) — así el usuario cae naturalmente donde puede seguir cobrando el saldo.

### Impacto
Cambio de UI en `Ventas/Create.cshtml` (CR-24.1/24.2/24.3, sin cambio de modelo — usa los mismos campos ya creados por CR-22). Capacidad nueva `IPagoVentaService`/`PagoVentaService` + acción en `VentasController` + UI en `Ventas/Details.cshtml` (CR-24.4) — sin migración EF, reutiliza `PagoVenta`/`MovimientoCCLocal` ya existentes.

### Discovery + Análisis v11 — CR-25/CR-26: comprobante AFIP totalmente editable + rediseño de PDFs (2026-07-30)

### CR-25 — ComprobantesAfip/Create totalmente personalizable
Pedido: "quiero que en ComprobantesAfip/Create la factura sea totalmente personalizable, si el cliente quiere modificar cantidades, importes, subtotales y totales, dejar modificarlo, tener la venta como referencia no como fuente de verdad."
- **Contexto real**: hoy `ComprobanteAfipService.EmitirAsync` tiene 2 topes duros: la Cantidad a facturar no puede superar `pendiente = VentaItem.Cantidad − CantidadFacturada`, y el precio SIEMPRE se recalcula desde `VentaItem.PrecioUnitario` (el input nunca se usa). Si la venta ya está 100% facturada, la pantalla ni siquiera se puede abrir ("no tiene items pendientes de facturar").
- **Decisiones confirmadas con el cliente** (`AskUserQuestion`): (1) se saca el tope duro de cantidad — la Venta pasa a ser precarga/referencia, editable sin restricción, con un aviso informativo (no bloqueante) si se supera lo vendido/pendiente; (2) el editor sigue limitado a los productos que ya tenía la venta (sin buscador para sumar productos nuevos ajenos a la venta).
- **CA-CR25.1**: Cantidad, Precio Unitario y Subtotal de cada línea pasan a ser editables sin tope duro (mismo patrón de inputs abiertos ya usado en `Ventas/Create` desde CR-22/24).
- **CA-CR25.2**: fila "Total" editable al pie, con el mismo mecanismo de reparto proporcional entre líneas ya implementado en CR-24.3 (consistencia de UX entre las 2 pantallas).
- **CA-CR25.3**: la pantalla ya no bloquea el acceso cuando `Items.Count == 0` (venta ya facturada al 100%) — se puede volver a facturar igual, con los datos de la venta como referencia de precarga.

### CR-26 — Rediseño visual de los PDF (remito + factura) + hallazgo de cumplimiento: falta el código QR de AFIP
Pedido: "quiero mejorar el diseño grafico de los comprobantes remitos pdf y facturas pdf que entrega el sistema."
- **Estado actual**: ambos PDF (`VentaService.GenerarRemitoPdfInterno`, `ComprobanteAfipService.GenerarPdfAsync`) son visualmente básicos — sin datos del emisor (CUIT/razón social), sin logo, columnas numéricas sin alinear a la derecha, sin jerarquía visual del total.
- **Hallazgo de cumplimiento (no solicitado, encontrado al revisar el código)**: la factura AFIP real **no incluye el código QR obligatorio** desde la RG 4291/2019 — todo comprobante electrónico debe mostrar un QR que codifica (en base64, como parámetro de una URL de afip.gob.ar) CUIT emisor, tipo/punto de venta/número de comprobante, importe, tipo y número de documento del receptor, y CAE. El sistema ya tiene todos esos datos disponibles (`ComprobanteAfip`, `ResolverDocumentoAfip` ya calcula `DocTipo`/`DocNro`) — falta únicamente generar y embeber el QR.
- **CA-CR26.1**: ambos PDF suman un encabezado con datos del emisor (nombre, CUIT desde `AfipSettings`, logo `isotipo_sin_anillo_color.png` ya existente en `wwwroot/icons/`).
- **CA-CR26.2**: tablas con columnas numéricas alineadas a la derecha, total destacado visualmente (caja/borde), mismo criterio de jerarquía en ambos documentos para que se sientan de la misma familia visual.
- **CA-CR26.3**: la factura AFIP suma el código QR real según la especificación de AFIP, visible en el pie del documento.

### Discovery + Análisis v12 — CR-27: Cuenta Corriente de Proveedores real (impuestos + pagos reales, reemplaza CR-19)

Pedido: "Hacer importacion de los datos de las cuenta corrientes de los proveedores... analizar que datos esta cargando el usuario de cada compra y de cada pago, ver cuales columnas son utiles para que de bien los numeros de las cuentas corrientes y el modelo le sirva." Disparado por un archivo nuevo entregado por el cliente: `Informe Cuentas Corrientes Movimientos de Proveedores 30-07-2026 1052 Hs.xlsx` — ledger real de 572 movimientos (239 Compras + 333 Pagos, 17 proveedores), 34 columnas, con saldo corrido ("A pagar") que cierra exacto contra el propio archivo.

### Auditoría columna por columna (34 columnas)
- **Con datos reales, hoy no modelados o mal usados**: `Subtotal con Descuento`/`IVA 2,5-27%`/`Perc. IVA`/`Perc. IIBB`/`Imp. Internos`/`Imp. Municipales`/`Sellos`/`Total compra` (impuestos reales por Compra — ver hallazgo 1); `Medio de Pago`/`Emisión`/`Pagado`/`Id Compra` (pago real por Compra — ver hallazgo 2); `Descripción` (nota real en 135/239 Compras, ej. "echeq $396000 12/10" — plan de pago acordado con el proveedor); `Punto de Venta`/`N° de Comprobante` (el modelo ya tenía estos campos desde CR-10, pero el importador nunca los cargaba).
- **Constante, sin valor informativo**: `Categoría` (siempre "Productos Terminados" o vacía) — descartada.
- **Redundante**: `Aplicada en N° de Factura`/`Fecha Factura Aplicada` (duplican en texto lo que `Id Compra` ya da como FK numérica confiable) — descartadas, se usa `Id Compra`.

### Hallazgo 1 — el Total de las 239 OC históricas estaba subvaluado en ~$19,4M
El importador original (CR-6/CR-1) solo guardaba el subtotal de líneas de producto, sin IVA ni percepciones — decisión explícita en su momento ("Total = Subtotal, sin impuestos discriminados... fuera del alcance aprobado de CR-6"). Verificado contra `marihogar_dev`: `SUM(OrdenCompra.Total)` real = $97.830.036,43. El archivo nuevo trae el Total real (con impuestos) por Compra: $117.216.297,81. Sin corregir esto, los pagos reales del hallazgo 2 no cerrarían contra el saldo real.

### Hallazgo 2 — CR-19 había marcado las 239 OC como pagadas al 100% de forma ficticia
CR-19 (2026-07-28) registró un único pago en Efectivo por el Total completo de cada OC, "forma de pago real no discriminada por el Excel" en ese momento. El archivo nuevo trae el pago real: 333 pagos concretos (fecha, medio, monto), vinculados a la Compra exacta vía `Id Compra`. Real: Total Compras $117,22M − Total Pagado $95,44M = **$21,77M de saldo pendiente real** (211 de las 239 Compras tienen al menos 1 pago real; 28 quedan enteramente pendientes).

### Hallazgo 3 — Mercado Pago se usa realmente para pagarle a proveedores
71 de los 333 pagos reales ($18,7M, 20% del total pagado) se hicieron por Mercado Pago — método hoy excluido a propósito de `PagoOrdenCompraService.MetodosPermitidosOC` (decisión de CR-3, que asumía uso exclusivo de Ventas). **Decisión confirmada con el cliente** (`AskUserQuestion`): habilitar Mercado Pago también hacia adelante como opción real en la pantalla de pago a proveedores, no solo para el histórico.

### Decisión confirmada con el cliente sobre el hallazgo 1 (`AskUserQuestion`)
Corregir el Total de las 239 OC históricas para incluir impuestos reales (sube la deuda total registrada de $97,83M a $117,22M) — imprescindible para que los pagos reales del hallazgo 2 cierren contra el saldo real.

### CA-CR27.1 — Total real con impuestos en OC históricas
`OrdenCompra.Subtotal`/`MontoIva`/`MontoIIBB`/`MontoOtrosImpuestos`/`Total`/`PuntoVenta`/`NumeroComprobante` se cargan desde las columnas reales del archivo nuevo (`Total compra` tomado tal cual como autoritativo) en vez del subtotal-sin-impuestos usado hasta CR-19.

### CA-CR27.2 — Pagos reales por Compra, reemplaza el pago ficticio de CR-19
Por cada pago real del archivo (columna `Id Compra`), se crea un `PagoOrdenCompra` + `MovimientoCCProveedor` real (fecha/medio/monto reales). Las Compras sin pago real quedan con saldo pendiente real, no ficticio.

### CA-CR27.3 — Ajuste de apertura de CC Proveedores (CR-18) deshabilitado
Con cobertura 100% real y completa de las 239 Compras, el saldo que queda por proveedor tras CA-CR27.1/27.2 YA ES el saldo real (verificado que coincide con la columna "A pagar" del propio archivo) — el mecanismo de CR-18 que llevaba a $0 cualquier saldo remanente (parche para cuando no había forma de saber la deuda real) se deshabilita para CC Proveedores. CC Local no se toca (Ventas/Gastos no tienen todavía la misma cobertura 100% real).

### CA-CR27.4 — Mercado Pago habilitado para pagos a Proveedores
`MetodoPago.MercadoPago` se agrega a `PagoOrdenCompraService.MetodosPermitidosOC` y al selector de `OrdenesCompra/Details.cshtml`.

### CA-CR27.5 — Nota interna en OrdenCompra
`OrdenCompra.NotaInterna` (nuevo campo, mismo patrón que `Venta.NotaInterna` de CR-12) para no perder el detalle real de la columna `Descripción` (135/239 Compras, planes de pago informales tipo echeq acordados con el proveedor).

### Discovery + Análisis v13 — CR-32/CR-33/CR-34: precio dual + recargo por tarjeta, edición completa de Venta, acreditación diferida de tarjeta (2026-08-11)

Pedido del cliente sobre Ventas (pantalla de mayor uso diario), 3 ítems relacionados entre sí. 4 decisiones confirmadas vía `AskUserQuestion` antes de diseñar (ver debajo de cada CR).

### CR-32 — Precio contado/tarjeta visible para ambos roles + recargo real por método de pago mixto

**Estado actual**: `Ventas/Create.cshtml` (CR-21/22/24) ya tiene precio editable + botón IVA (toggle) + "c/IVA" calculado (×1,21) + Subtotal editable — pero el toggle es manual por línea y la edición es exclusiva de Administrador (Vendedor no ve ni interactúa con estos controles, server-side fuerza el precio de catálogo). El pedido pide 2 cambios: (1) que ambos precios (contado y tarjeta) sean siempre visibles, para Administrador y Vendedor; (2) que el precio efectivamente cobrado por cada ítem se resuelva **según el método de pago elegido al cobrar**, no por un toggle manual pre-cobro.

**Ejemplo real dado por el cliente** (clave para fijar la mecánica exacta): "se crea una venta con 3 items de 100 mil pesos cada uno, el cliente puede pagar 250 con tarjeta (se suma IVA) y 50 mil en efectivo (sin IVA)". Total contado = $300.000 (3×$100.000). El cliente paga: $250.000 de base cubiertos con tarjeta (recargo del 21% se suma → $302.500 realmente cobrados por esa línea) + $50.000 en efectivo (sin recargo, cubre $50.000 de base). $250.000 + $50.000 = $300.000 de base (cierra exacto contra el Total contado) — el recargo del 21% es dinero **adicional** cobrado por el medio tarjeta, no una deuda del cliente.

**Decisiones confirmadas**:
1. Ambas columnas (Precio contado / Precio tarjeta) visibles siempre para Administrador y Vendedor (no solo Administrador).
2. El recargo se aplica **al monto cubierto por cada línea de pago**, no a ítems fijos — el cliente puede repartir libremente cuánto paga con cada método (no existe "un método predominante para toda la venta").

**CA-CR32.1**: `Ventas/Create.cshtml` — columna de precio de línea rediseñada: "Precio contado/transf" (input, default `Producto.PrecioEfectivo`, edición sigue Administrador-only sin cambio del gate de CR-22) + "Precio tarjeta" (solo lectura, = precio contado × 1,21, visible para ambos roles) — se saca el toggle manual, ambas columnas quedan siempre visibles como referencia. El Subtotal de línea (input, ya existente) sigue por defecto en base al precio contado.

**CA-CR32.2**: `PagoVenta` gana `MontoBase` (decimal, nullable — null cuando `Metodo != TarjetaCredito`, igual a `Monto` en ese caso). Al agregar una línea de pago con `Metodo = TarjetaCredito`, el usuario ingresa el **monto base** que esa línea cubre del Total contado de la Venta; el sistema calcula y muestra en vivo `Monto = MontoBase × 1,21` (recargo, mismo % que `PrecioLista`/CR-21 — no un campo de interés de cuotas, `PorcentajeInteres` sigue siendo un concepto aparte y opcional). El "saldo pendiente" de la Venta se calcula sobre `Σ MontoBase` (o `Σ Monto` cuando `MontoBase` es null) contra `Venta.Total`, nunca sobre `Σ Monto` a secas — así el ejemplo del cliente cierra: $250.000 + $50.000 de base = $300.000, saldo pendiente $0, aunque el dinero real cobrado sea $352.500.

**CA-CR32.3**: `MovimientoCCLocal.Ingreso` posteado por cada línea de pago pasa a ser por `Monto` (el dinero real que efectivamente entra, incluido el recargo) — el recargo por tarjeta es ingreso real del negocio, debe verse en Caja. Esto es un cambio respecto del criterio actual (`VentaService.ConfirmarAsync` postea un único Ingreso por `venta.Total` completo) — ahora se postea **por línea de pago**, sumando exacto lo mismo cuando no hay tarjeta de por medio (ver también CR-34, que necesita este mismo cambio para diferir el Ingreso de tarjeta hasta la acreditación).

### CR-33 — Edición completa de una Venta ya creada

Pedido: "se deben poder editar los datos de la venta en su totalidad una vez generada." Hoy `Venta` está documentada explícitamente como inmutable post-creación ("No se edita despues de creada: solo puede pasar a Cancelada") — este CR cambia esa decisión de arquitectura.

**Riesgo identificado y confirmado con el cliente**: una Venta ya tiene impacto real en Stock (`MovimientoStock`) y CC Local (`MovimientoCCLocal`) al confirmarse, y puede tener un `ComprobanteAfip` ya emitido — modificar retroactivamente cantidades/precios de una venta ya facturada generaría un descuadre entre lo que el sistema dice y lo que AFIP tiene registrado (ilegal/no corregible sin una Nota de Crédito real, fuera de alcance).

**Decisión confirmada**: edición completa permitida (items, cantidades, precios, cliente, nota) sobre una Venta en cualquier estado (`Pendiente`/`PagadaParcial`/`Pagada`) **excepto si ya tiene un `ComprobanteAfip` asociado** — en ese caso la edición queda bloqueada. **Reutiliza tal cual `VentaService.TieneComprobanteAsociadoAsync`**, el guard que ya existe y ya usa `CancelarAsync` (`ComprobantesAfip.Any(c => c.VentaId == id && c.Estado == Emitido)`) — no se inventa un criterio nuevo basado en `CAE != null`: los ~286 comprobantes históricos migrados tienen `Estado=Emitido` pero `CAE=null` (Contagram no integraba AFIP), y ya quedan bloqueados para cancelar con el criterio existente — mismo criterio debe aplicar para editar, es la misma "factura real asociada" en espíritu.

**CA-CR33.1**: nueva pantalla `Ventas/Edit` (mismo layout que `Create`, precargada con los datos actuales de la Venta) — solo accesible si `Estado != Cancelada` y `TieneComprobanteAsociadoAsync(id) == false`.

**CA-CR33.2**: `VentaService.EditarAsync` — recibe el mismo `VentaInput` que `ConfirmarAsync`, dentro de una transacción: (1) revierte el efecto de stock de los items actuales (`MovimientoStock` de reversión, mismo patrón que `CancelarAsync`), (2) reemplaza el set de `VentaItem` (mismo patrón simple de reemplazo completo ya usado por `PresupuestoService`/`OrdenCompraService.UpdateAsync`), (3) aplica el stock de los items nuevos, (4) recalcula `Venta.Total`, (5) **no toca `PagoVenta` existentes** (los pagos ya registrados no se editan por esta vía — si el nuevo Total difiere del ya cobrado, el saldo pendiente/Estado se recalcula solo, pudiendo pasar a `PagadaParcial` o generar sobrepago informativo, sin bloquear el guardado).

**CA-CR33.3**: guard server-side explícito (nunca solo en la vista) — `if (await TieneComprobanteAsociadoAsync(id)) return error`, mismo método privado ya existente en `VentaService` (hoy usado solo por `CancelarAsync`), sin duplicar la consulta.

### CR-34 — Acreditación diferida de pagos con tarjeta

Pedido: "cuando la venta es pago con tarjeta, el pago se acredita en una fecha posterior [...] sumar a los pagos con tarjeta una fecha efectiva de pago [...] antes el pago debe quedar en estado pendiente o a acreditar."

**Precedente existente, deliberadamente NO reutilizado tal cual**: `Cheque` (M14) ya tiene una máquina de estados Pendiente→Acreditado/Rechazado, pero postea el movimiento de CC (Proveedor, en ese caso) **inmediatamente** al registrar el pago, revirtiendo solo si rechaza — filosofía "post ahora, revertí si falla". El cliente pidió explícitamente lo opuesto para tarjeta en Ventas: "antes el pago debe quedar en estado pendiente" — filosofía "no cuenta hasta que se confirma". **Confirmado con el cliente** vía `AskUserQuestion`: mientras un pago con tarjeta está pendiente de acreditar, NO cuenta como plata disponible en Caja/Proyección Financiera — mismo espíritu ya establecido por CR-29 para pagos con fecha futura (ese ingreso no se ve en el período actual, se ve en Proyección Financiera como "por acreditar").

**CA-CR34.1**: `PagoVenta` gana `EstadoAcreditacion` (enum nuevo `EstadoAcreditacionPago`: `Acreditado` = 1, `Pendiente` = 2 — default `Acreditado` para que Efectivo/Transferencia/MercadoPago/BancoCarrefour, que ya se cobran "ahora", no cambien de comportamiento) y `FechaAcreditacionEfectiva` (`DateTime?`, obligatoria y editable solo cuando `Metodo == TarjetaCredito` — el usuario carga la fecha real en la que el dinero entra a la cuenta, sugerida pero editable, ej. +18 días hábiles, sin autocálculo automático por ahora dado que cada resumen de tarjeta tiene su propio plazo real).

**CA-CR34.2**: al registrar un `PagoVenta` con `Metodo == TarjetaCredito`, queda en `EstadoAcreditacion = Pendiente` — el `MovimientoCCLocal.Ingreso` de esa línea (CA-CR32.3) **se postea recién cuando se marca Acreditado**, no al momento del cobro. Nueva capacidad `IVentaService.AcreditarPagoAsync` (acción manual del Administrador, mismo patrón que `IChequeService.AcreditarAsync`) — marca `EstadoAcreditacion = Acreditado` y postea el `MovimientoCCLocal.Ingreso` recién en ese momento, con `Fecha = FechaAcreditacionEfectiva` (no la fecha de hoy) para que el ingreso caiga en el período contable correcto.

**CA-CR34.3**: Proyección Financiera — el bloque ya agregado por CR-29 (`PagosVentaPorAcreditar`, hoy solo mira `Fecha` futura) se **amplía** para incluir también los `PagoVenta` con `EstadoAcreditacion = Pendiente` (aunque su `Fecha` de registro sea hoy) dentro del horizonte proyectado — mismo campo informativo ya existente, sin tocar la fórmula de `TieneDeficit`/`IngresosProyectados` (CA-N22, sin cambios).

**CA-CR34.4**: `Ventas/Details.cshtml` — la tabla de Pagos muestra el estado de acreditación por línea (badge "Acreditado"/"Pendiente hasta dd/mm/aaaa") y, si `EstadoAcreditacion = Pendiente`, un botón "Marcar acreditado" (Administrador only, mismo criterio de permisos que `Cheques`).

### Impacto conjunto (los 3 CR comparten cambios de modelo/servicio en Venta/PagoVenta)
Domain: `PagoVenta` gana `MontoBase` (CR-32) + `EstadoAcreditacion`/`FechaAcreditacionEfectiva` (CR-34), nuevo enum `EstadoAcreditacionPago`. Migración EF combinada. Application/Infrastructure: `VentaService.ConfirmarAsync`/`PagoVentaService.RegistrarPagoAsync` recalculados para postear `MovimientoCCLocal` por línea de pago (no más un único Ingreso por el Total) y respetar `EstadoAcreditacion`; nuevo `VentaService.EditarAsync` (CR-33); nuevo `IVentaService.AcreditarPagoAsync` (CR-34); `ProyeccionFinancieraService` ampliado (CR-34.3). Web: `Ventas/Create.cshtml` (columnas de precio CR-32.1, sin cambio de gate de edición cruda), nueva `Ventas/Edit.cshtml` (CR-33), `Ventas/Details.cshtml` (badges + acción de acreditar, CR-34.4).

### Discovery + Análisis v14 — CR-40: modelo de precios negro/con IVA/tarjeta, % descuento/recargo por producto, cuotas configurables (2026-08-15)

Pedido del cliente, explícito para quedar como regla de negocio permanente ("aplicar la siguiente lógica al sistema y también al modelo de agentes IA para futuros desarrollos") — no es solo una corrección puntual, es la forma en que MariHogar arma un precio, documentada acá como fuente de verdad para cualquier CR futuro que toque Producto/Venta/Pago.

### Modelo de precios

El negocio maneja 2 precios por producto, nunca 3 — la confusión inicial de "negro / con IVA / tarjeta" en el pedido del cliente se resuelve a 2 categorías porque, para MariHogar (alícuota única 21%), "con IVA" y "tarjeta" dan el mismo número:

1. **Precio efectivo** (`Producto.PrecioEfectivo`) — aplica pagando en efectivo **o con Tarjeta de Débito** (CR-57, 21/08/2026 — antes era exclusivo de efectivo).
2. **Precio transferencia** (`Producto.PrecioLista`, nombre visible «Precio transferencia» desde CR-51 — hasta CR-48 se calculaba siempre `PrecioEfectivo` + 21%, desde CR-48 es editable, desde CR-51 se completa a mano sin ninguna sugerencia) — aplica en **cualquier otro caso**: efectivo con factura, transferencia, MercadoPago, Banco Carrefour, o tarjeta de crédito (tarjeta de crédito SIEMPRE cobra este precio, sin excepción — a diferencia de débito).

**Decisión confirmada con el cliente** (`AskUserQuestion`, ya que el pedido original no mencionaba dónde caían Transferencia/MercadoPago/Banco Carrefour): esos 3 métodos van siempre con el precio "transferencia", igual que efectivo-con-factura — queda afuera del precio efectivo el efectivo sin factura y (desde CR-57) la Tarjeta de Débito.

Mecánica ya existente desde CR-38 (`VentaItem.TipoPrecio`, enum `Contado`/`Tarjeta`) sigue siendo la implementación correcta de esto — no fue necesario tocar el modelo de datos, solo la etiqueta visible («Precio efectivo» / «Precio transferencia (+21%)» en `Ventas/Create.cshtml`/`Edit.cshtml`/`Details.cshtml`) y documentar la regla acá. El selector por línea (radio, habilitado para Administrador y Vendedor) es la forma en que se fija qué precio corresponde a esa línea.

**CR-51 (renombre + sin sugerencia, 19/08/2026)**: el cliente pidió que los 2 precios del producto se llamen explícitamente «Precio efectivo» / «Precio transferencia» (en vez de «Precio de lista», nombre elegido en CR-47) y que el campo `PrecioLista` se complete siempre a mano — sin el "+21% sugerido" que CR-48 había agregado en `Productos/Create.cshtml`/`Edit.cshtml` (autocompletado en Create, link "usar sugerido" en Edit). Renombrado en todo el proyecto: `ProductoFormViewModel.PrecioLista` (`[Display(Name=...)]`), `Ventas/Create.cshtml`/`Edit.cshtml`/`Details.cshtml` (labels, badges, header de tabla), comentarios en `VentaService.cs`/`PagoVentaService.cs`/`ComprobanteAfipService.cs`, doc-comments de `Producto.cs`/`ProductoDtos.cs`/`VentaDtos.cs`/`TipoPrecioVentaItem.cs`. Sin migración EF (cambio de texto + eliminación de JS de autocompletado, sin cambio de esquema ni de lógica de negocio).

**CR-47 (renombre, 19/08/2026)**: el cliente hizo notar que en la práctica el 100% de las ventas terminan facturadas (con o sin `ComprobanteAfip` real emitido en el momento, pero facturadas igual) — la etiqueta original «Negro (efvo. s/factura)» / «Con IVA (21%)» sugería que el precio elegido determinaba si la venta se declaraba o no, algo que nunca fue cierto (es una política de precio, `ComprobanteAfipService.ObtenerPrecargaAsync` permite facturar cualquier línea sin importar qué `TipoPrecio` tenga). Renombrado en todo el circuito de Ventas a «Precio efectivo» / «Precio de lista (+21%)», igual que ya se mostraba en `Producto` (`Create`/`Edit.cshtml`) — sin tocar ninguna lógica ni validación (CA-CR40.3 sigue exactamente igual). Cambio de texto puro: `Ventas/Create.cshtml`, `Edit.cshtml`, `Details.cshtml`, comentarios en `VentaService.cs`/`PagoVentaService.cs`/`ComprobanteAfipService.cs`, y el doc-comment de `Producto.PrecioEfectivo`. Sin migración EF.

**CA-CR40.3 (hallazgo de esta revisión, cerrado el mismo día — 2 iteraciones)**: la primera versión de este CR dejaba la regla "no-efectivo siempre cobra con IVA" como una guía operativa sin candado real — CR-38 había sacado el recargo/ajuste automático del pago (`Monto` ya no se recalcula, se confía en que el `Subtotal` de la línea ya tiene el precio correcto segun `TipoPrecio`), lo que dejaba abierta la posibilidad de cobrar con un método no-efectivo líneas que quedaron en "Negro" (el default) sin que el 21% se aplicara nunca ni el sistema avisara.

Primera pasada del fix solo validaba Tarjeta. El cliente hizo notar el caso real que faltaba: **un mismo ítem "Con IVA" puede pagarse repartido entre efectivo + tarjeta + transferencia** — y de los 3, solo Efectivo puede además cubrir precio "Negro" (Transferencia/MercadoPago/Banco Carrefour, igual que Tarjeta, cobran siempre "Con IVA" por la decisión ya confirmada en la sección "Modelo de precios" de más arriba). El guard se amplió para cubrir los 4 métodos no-efectivo como un solo pool, no solo Tarjeta.

**Cerrado con una validación server-side real** en `VentaService.ConfirmarAsync` y `PagoVentaService.RegistrarPagoAsync`: `Σ (MontoBase ?? Monto)` de pagos con Tarjeta/Transferencia/MercadoPago/Banco Carrefour (existentes + nuevos) nunca puede superar `Σ Subtotal de las líneas marcadas TipoPrecio=Tarjeta` (="Con IVA") de esa venta — si lo supera, se bloquea pidiendo marcar más líneas "Con IVA" o cubrir la diferencia en efectivo. Efectivo queda sin tope porque es el único método flexible (cubre "Negro" o "Con IVA" indistintamente). No requirió cambios de modelo ni migración, solo el guard. `VentaService.EditarAsync` (CR-33) NO lleva este guard — mantiene su criterio ya documentado de "no bloquea por descalces con pagos existentes, el saldo se recalcula solo".

### % Descuento / % Recargo configurable por producto

**CA-CR40.1**: `Producto` gana `PorcentajeDescuento`/`PorcentajeRecargo` (decimal, default 0, editables en `Productos/Create`/`Edit`, Administrador-only) — son el **default de catálogo**, no un valor fijo: al agregar el producto a una Venta, precargan el "% Desc./% Rec." de esa línea (ya existente desde CR-38 para descuento; recargo es nuevo), y el vendedor/administrador los puede seguir ajustando por línea igual que antes. `VentaItem` gana `RecargoPorcentaje` (mismo criterio de trazabilidad que `DescuentoPorcentaje` de CR-38 — dato informativo de por qué el Subtotal es el que es, nunca la fuente de verdad).

**Orden de aplicación** (Subtotal de línea): `Cantidad × PrecioActivo × (1 − %Descuento) × (1 + %Recargo)` — primero descuento, después recargo sobre el resultado ya descontado (`Ventas/Create.cshtml`, `recalcularSubtotalSiCorresponde`).

### Cuotas de tarjeta con % interés configurable

**CA-CR40.2**: pedido — "los pagos con tarjeta pueden ser en cuotas de 3/6/9/12, cada una con su % de interés respecto a las cuotas seleccionadas". Antes de este CR, `PagoVenta.PorcentajeInteres` ya existía (CR-3) pero se tipeaba a mano en cada venta, sin ningún default. **Decisión confirmada con el cliente**: pantalla admin nueva (`ConfiguracionCuotas`, Administrador-only, `Configuración > Cuotas de tarjeta`) con las 4 filas fijas (3/6/9/12, sembradas por `SeedData.InitializeAsync`, sin Create/Delete — solo se edita el % de cada una). Al elegir la cantidad de cuotas en Formas de pago (`Ventas/Create.cshtml` y `Ventas/Details.cshtml` → "Registrar pago"), el `% Interés` se precarga solo con el valor configurado — el vendedor lo puede seguir ajustando por venta puntual (ej. una promo especial), igual criterio de "default editable" que el resto de este CR.

### Matemática de porcentajes — función invertible (regla de código, no solo de este proyecto)

Pedido explícito del cliente sobre cómo tiene que estar hecho el cálculo: "una función para poder sumar el % y luego restar el mismo % y que dé el mismo valor que tenía originalmente el producto". El error típico (y la razón del pedido) es revertir un recargo restando el mismo %, que NO es la operación inversa — ver `MariHogar.Domain.Helpers.PorcentajeHelper` (nuevo, CR-40) para la implementación correcta y el ejemplo numérico completo en su comentario de cabecera. Regla aplicada retroactivamente a todo el código que ya sumaba un %: `Producto.PrecioLista`, `VentaService.ConfirmarAsync`/`EditarAsync`/`ObtenerPrecargaDesdePresupuestoAsync` (antes `precio × 1.21m` inline, ahora `PorcentajeHelper.AplicarRecargo(precio, 21m)`). Esta regla queda documentada también como estándar de código general del estudio (no específico de MariHogar) en `C:/Sistemas/Agentes-IA/.github/instructions/20-domain.instructions.md` — cualquier proyecto futuro que necesite sumar/revertir un % de precio debe usar el mismo patrón (multiplicar por `1 + %/100` para aplicar, **dividir** por `1 + %/100` para revertir — nunca restar el mismo %).

### Impacto de modelo/servicio
Domain: `PorcentajeHelper` (nuevo), `Producto.PorcentajeDescuento`/`PorcentajeRecargo`, `VentaItem.RecargoPorcentaje`, `ConfiguracionCuotaTarjeta` (entidad nueva, sin `SoftDestroyable` — tabla de configuración de 4 filas fijas, no un documento con alta/baja). 3 migraciones EF. Application/Infrastructure: `IConfiguracionCuotaTarjetaService`/`ConfiguracionCuotaTarjetaService` (nuevo), `ProductoService`/`VentaService` ampliados. Web: `Productos/Create.cshtml`/`Edit.cshtml` (2 campos nuevos), `ConfiguracionCuotasController`/`Views/ConfiguracionCuotas/Index.cshtml` (pantalla nueva, link de sidebar bajo Catálogo), `Ventas/Create.cshtml`/`Edit.cshtml`/`Details.cshtml` (relabel + columna "% Rec." + precarga de cuotas).

### Nota de consistencia — patrón genérico "PAT-003" del estudio vs. comportamiento aprobado de marihogar

`32-estandares-qa-implementador.instructions.md` formalizó el 15/08/2026 un patrón genérico ("Venta con IVA + pago dividido en multiples metodos", PAT-003) que exige que la suma de los pagos de una venta sea **exactamente igual** al Total, bloqueando el guardado si no cierra "ni de más ni de menos" — aplicable, según esa instrucción, a todo proyecto con módulo de venta. MariHogar diverge de esa regla en 2 puntos **a propósito, ya aprobados con el cliente**, y no debe interpretarse como un incumplimiento en futuras auditorías:

1. **CR-39** permite confirmar una Venta con pagos sumando MENOS que el Total (o sin ningún pago) — queda `Pendiente`/`PagadaParcial`, cobrable después desde `Ventas/Details` ("Registrar pago", CR-24.4). Pedido explícito del cliente.
2. El sistema permite pagos sumando MÁS que el Total (vuelto en efectivo — caso real de comercio: el cliente paga con un billete más grande y se le da cambio) — la UI incluso lo etiqueta explícitamente ("Vuelto $X").

Lo que sí se mantiene sin excepción, y es donde aplica el espíritu real de PAT-003 en este proyecto: el server-side nunca confía en un pago no-Efectivo que exceda lo cargado a precio "de lista" en la venta (CA-CR40.3, validación en `VentaService.ConfirmarAsync`/`PagoVentaService.RegistrarPagoAsync`).

## CR-54 — Registrar pago con Transferencia: admite fecha pasada (backdatear) al cargar

Pedido explícito del cliente (21/08/2026): "registrar pago de las compras con transferencia el usuario quiere poder seleccionar fechas pasadas para cargar transferencias realizadas". Complementa CR-53 (que permite corregir la fecha después de registrado) con la posibilidad de cargarla bien desde el principio.

El campo "fecha tentativa de pago" (CR-44) ya existía en la pantalla de Registrar pago, pero tenía `min=hoy` — solo servía para programar un pago a futuro, cualquier fecha pasada quedaba descartada (el pago se registraba con `Fecha=ahora`, sin importar qué se hubiera tipeado). Para Transferencia específicamente (pedido explícito, mismo alcance que CR-53), ahora una fecha pasada en ese mismo campo **backdatea** el pago: queda `Estado=Pagado` de inmediato (no programado) pero con `Fecha` = la fecha real elegida, cascadeada también al `MovimientoCCProveedor.Pago` que se postea en el momento — mismo criterio de consistencia que el resto de los "fecha real" de esta sesión (CR-42/44/45/46/53). Una fecha futura sigue programando el pago exactamente como antes (CR-44 intacto); vacío sigue pagando "ahora". El `min=hoy` del datepicker se saca únicamente para Transferencia — el resto de los métodos (Efectivo/MercadoPago/Depósito) no fue pedido, mantienen el comportamiento anterior.

**Impacto en capas**: Infrastructure (`PagoOrdenCompraService.RegistrarPagoAsync`), Web (`OrdenesCompra/Details.cshtml`). Sin migración EF.

## CR-53 — Fecha de pago con Transferencia editable

Pedido explícito del cliente (21/08/2026), en la misma entrega que el cierre de CR-52: "hacer que se pueda modificar la fecha de pago con transferencia de las compras".

`PagoOrdenCompra.Fecha` se fijaba una única vez, a `DateTime.UtcNow`, al registrar el pago — sin forma de corregirla después (ej. el pago se carga hoy pero la transferencia real se hizo días antes). Nuevo método `IPagoOrdenCompraService.ActualizarFechaPagoTransferenciaAsync(pagoOrdenCompraId, nuevaFecha)`, acotado a `Metodo=Transferencia` (pedido explícito — los demás métodos ya tienen su propio mecanismo: Cheque vía acreditación desde CR-46, el resto no fue pedido), nunca futura. Si el pago ya está `Pagado` (con su `MovimientoCCProveedor.Pago` ya posteado), la corrección se cascadea a ese movimiento para que el ledger de Cuenta Corriente no quede con una fecha distinta a la del pago que lo originó — mismo criterio de consistencia ya aplicado en CR-42/44/45/46. Disponible en cualquier estado de la OC (mismo criterio que la nota interna de CR-50), acción propia en `OrdenesCompra/Details.cshtml`: un ícono de lápiz junto a la fecha de cada pago con Transferencia abre un selector de fecha (SweetAlert2, mismo patrón visual que "Marcar recibida").

**Impacto en capas**: Application (`IPagoOrdenCompraService`), Infrastructure (`PagoOrdenCompraService.cs`), Web (`OrdenesCompraController.cs`, `OrdenesCompra/Details.cshtml`). Sin migración EF.

## CR-60 — Cheques de compra: plazo de días editable a mano (deja de ser fijo 30/60/90)

Pedido explícito del cliente (27/08/2026): "en Orden de compra al agregar pagos con cheque el usuario quiere completar a mano la cantidad de días, y que en base a eso se calcule la fecha efectiva de cobro (en vez de 30/60/90 que la cantidad de días sea configurable a mano)."

**Investigación**: `Cheque.Cuota` (el campo real, "días de plazo") nunca tuvo una restricción de valores a nivel de `Domain`/`Service` — el único lugar donde el plazo quedaba limitado a 30/60/90 era el `<select>` de `OrdenesCompra/Details.cshtml` (3 `<option>` fijas). El autocálculo de vencimiento (`autocalcularVencimientoCheque`, CR-2) ya era genérico (`FechaVencimiento = FechaEmision + cuota días` con cualquier entero), así que no hizo falta tocarlo.

**Fix**: el `<select>` se reemplaza por un `<input type="number" min="1">` de días libre, con el mismo default sugerido de 30 días al pasar el método a Cheque (CR-15, sin cambios) — el autocálculo de vencimiento sigue disparando en cada cambio, ahora con `input` en vez de `change` para recalcular mientras el usuario escribe. Sin cambios en `Domain`, `Service` ni migración — el campo ya aceptaba cualquier entero.

**Impacto en capas**: Web (`OrdenesCompra/Details.cshtml`, solo JS/markup). Sin migración EF.

## CR-59 — Pagos con tarjeta de crédito a liquidar (listado dedicado + card Dashboard)

Pedido del cliente vía `/agentes-ia-orquestador` (27/08/2026), planteado como pregunta abierta: "el cliente quiere integrar en alguna pantalla un listado de pagos con tarjeta de crédito a liquidar, ¿o se necesita una pantalla nueva? ¿o podríamos ponerla en el dashboard?"

**Discovery**: el modelo ya tiene todo lo necesario, construido en CR-32/33/34/35 — `PagoVenta.EstadoAcreditacion` (Pendiente/Acreditado, solo aplica a `Metodo=TarjetaCredito`), `FechaAcreditacionEfectiva`, `IVentaService.AcreditarPagoAsync` (acción manual, Administrador-only) y el job diario `PagoVentaAcreditacionHostedService` (notifica cuando llega la fecha, nunca acredita solo — mismo patrón que `ChequeAcreditacionHostedService`). Hoy esos pagos solo son visibles uno por uno, adentro de cada `Ventas/Details` — no existe ningún lugar donde verlos todos juntos.

**Decisión de ubicación** (recomendada por el analista, confirmada por el cliente: "sí, implementar"): pantalla nueva dedicada, análoga a `Cheques/Index.cshtml` (mismo patrón exacto: listado filtrable + acción "Acreditar" inline) — no el Dashboard solo. El Dashboard tiene una regla fija (HU-9.1): cada card es un KPI numérico que carga solo, nunca una tabla con acciones (por eso "Cheques por vencer" es una card chica que linkea a su propia pantalla completa). Se agregan **las dos cosas**: pantalla nueva (el listado real, con el botón Acreditar) + una card en el Dashboard que linkea a ella (mismo patrón que ya usan "Cheques por vencer" y "Balance de caja").

**Alcance confirmado**:
- Pantalla nueva `PagosTarjeta/Index.cshtml` (Administrador-only, mismo criterio que `AcreditarPagoAsync`), clon del patrón `Cheques/Index.cshtml`: filtro por Estado (Pendiente/Acreditado — sin Rechazado, `PagoVenta` no tiene ese estado) y por rango de fecha de acreditación, columnas Venta (link a Details)/Cliente/Cuotas/Monto/Fecha de pago/Fecha de acreditación/Estado, resaltado de fila "vence próximo" (≤7 días, mismo criterio que Cheques), botón "Acreditar" (solo si Pendiente) que reutiliza `AcreditarPagoAsync` sin tocarlo.
- Nuevo método de solo lectura `IVentaService.ListarPagosTarjetaAsync(request, filtro)` — filtra `PagosVenta` por `Metodo=TarjetaCredito`, mismo patrón DataTable server-side que `ChequeService.ListarAsync`.
- Nueva entrada de menú lateral (`_Layout.cshtml`, junto a "Cheques").
- Nueva card "Pagos con tarjeta por acreditar" en `Dashboard/Admin.cshtml` (Administrador-only, mismo patrón AJAX independiente que "Cheques por vencer") — cantidad + monto de `PagosVenta` con `EstadoAcreditacion=Pendiente`, link a la pantalla nueva.

**Fuera de alcance**: no se toca `AcreditarPagoAsync`, `PagoVentaAcreditacionHostedService` ni ningún cálculo existente (Caja, Proyección financiera) — es una superficie de lectura + 1 acción ya existente, sin lógica de negocio nueva.

**Impacto en capas**: Application (`IVentaService` +1 método, DTOs nuevos `PagoTarjetaListItemDto`/`PagoTarjetaFiltro`/`PagosTarjetaPendientesDto`), Infrastructure (`VentaService.cs`), Web (`PagosTarjetaController` nuevo, `Views/PagosTarjeta/Index.cshtml` nuevo, `DashboardController.cs` +1 acción, `Dashboard/Admin.cshtml` +1 card, `_Layout.cshtml` +1 link de menú). **Sin migración EF** (todos los campos ya existen).

## CR-58 — Órdenes de compra: tag de facturación + Dashboard "vista CEO" (4 métricas nuevas)

Pedido explícito del cliente (26/08/2026), 3 partes en un mismo mensaje: "Órdenes de compra: agregar un tag para saber cuántas órdenes de compra están facturadas y cuántas no facturadas. Agregar mismo indicador en pantalla dashboard. Hacer un análisis de la estructura de datos del proyecto hasta el día de la fecha (ventas, compras, pagos, cheques) y sumar datos útiles para CEO del negocio en la pantalla dashboard del sistema".

**Parte 1 — Tag de facturación de OC**: `OrdenCompra.Facturada` ya existía (bool simple, cargado a mano al confirmar si el proveedor entregó su propia factura — sin relación con AFIP, que es exclusivamente del lado Ventas). Nuevo `IOrdenCompraService.ObtenerResumenFacturacionAsync(desde?, hasta?)` agrega cantidad/monto facturado y no facturado sobre las OC no canceladas, con un rango de fecha opcional. Consumido por la card "Compras del período" en `Dashboard/Admin.cshtml` — pedido explícito de ajuste del cliente (26/08/2026: "igualar el formato que tiene la card de ventas") para que se vea idéntica a "Ventas del período" (título, total grande, "xx compra(s)", badges Facturado/No facturado), filtrada por el mismo `desde`/`hasta` del Dashboard. El badge original en `OrdenesCompra/Index.cshtml` (histórico completo, sin fecha) se agregó primero y **se eliminó a pedido explícito del cliente el mismo día** (27/08/2026: "eliminar Facturadas/No facturadas... de la pantalla /OrdenesCompra") — junto con la acción `GetResumenFacturacion` de `OrdenesCompraController`, que quedó sin uso. El dato sigue disponible únicamente en la card del Dashboard.

**Parte 2 — 4 métricas nuevas "vista CEO" en el Dashboard**: se investigó la estructura de datos existente (Ventas, OC, CC Proveedor, Gastos, Cheques) y se propusieron 5 candidatas; el cliente confirmó 4 vía 2 `AskUserQuestion` (quedó afuera "Tasa de conversión Presupuesto→Venta"):
1. **Deuda total a proveedores**: nuevo `ICCProveedorService.ObtenerSaldoTotalAsync()` (Cargo − Pago de `MovimientoCCProveedor`, sin filtrar por proveedor — mismo cálculo que `ObtenerSaldoActualAsync` sin el `Where` por Id).
2. **Margen bruto del período**: nuevo `IDashboardService.ObtenerMargenBrutoAsync(desde, hasta)` — Subtotal de `VentaItem` (ventas no canceladas del período) menos `Cantidad × Producto.PrecioCompra` **actual**. Limitación aceptada explícitamente por el cliente al confirmar la métrica: el sistema no versiona el precio de compra histórico por ítem, así que un producto que cambió de costo distorsiona el margen de ventas pasadas.
3. **Gastos operativos del período**: nuevo `IGastoService.ObtenerTotalPeriodoAsync(desde, hasta)` — suma de `Gasto.Monto` no anulado en el rango.
4. **Ticket promedio de venta**: agregado directo a `VentasPeriodoDto.TicketPromedio` (Total/Cantidad del período) — sin endpoint nuevo, reutiliza el mismo fetch de la card "Ventas del período" ya existente.

Las 3 métricas nuevas con endpoint propio (Deuda, Margen bruto, Gastos operativos) siguen el mismo criterio de protección que Cheques/Balance de caja: `[Authorize(Policy = "RequireAdministracion")]` explícito en el endpoint, más allá de que la UI ya las oculte al Vendedor (regla REG-010).

**Impacto en capas**: Application (`OrdenCompraDtos.cs`, `DashboardDtos.cs`, `IOrdenCompraService`, `IDashboardService`, `ICCProveedorService`, `IGastoService`), Infrastructure (`OrdenCompraService.cs`, `DashboardService.cs`, `CCProveedorService.cs`, `GastoService.cs`), Web (`DashboardController.cs`, `OrdenesCompraController.cs`, `OrdenesCompra/Index.cshtml`, `Dashboard/Admin.cshtml`). Sin migración EF (todo agregados/consultas, sin columnas nuevas).

## CR-57 — Método de pago "Tarjeta de débito" en Ventas y Compras

Pedido explícito del cliente (21/08/2026): "agregar método de pago débito en las ventas y en las compras".

**Decisiones confirmadas con el cliente** (2 `AskUserQuestion` antes de implementar, porque contradicen a primera vista la regla ya vigente de "Modelo de precios"):
1. **Precio**: Débito cobra precio **"Efectivo"**, no "Transferencia (+21%)" — a diferencia de Tarjeta de Crédito/Transferencia/MercadoPago/Banco Carrefour (que siempre exigen precio de lista desde CR-40). Actualiza el "Modelo de precios": el precio efectivo ya no es exclusivo del método Efectivo, ahora lo comparten Efectivo y Débito.
2. **Acreditación**: Débito se acredita al instante (como Efectivo/Transferencia/MercadoPago), **nunca** el circuito de acreditación diferida de CR-34 (fecha efectiva, badge Pendiente, "Marcar acreditado") que sí tiene Tarjeta de Crédito.

**Alcance**: `MetodoPago` gana `TarjetaDebito = 8`, habilitado en **ambos** contextos — Ventas (`VentaService.MetodosPermitidosVenta`, `PagoVentaService.MetodosPermitidosVenta`) y Compras (`PagoOrdenCompraService.MetodosPermitidosOC`) — a diferencia de Tarjeta de Crédito/Banco Carrefour, que siguen exclusivos de Ventas. Como Débito **no** se agrega a `metodosRequierenConIva` (el array que exige precio "de lista"), automáticamente queda en el mismo grupo flexible que Efectivo para la validación de CR-40 (CA-CR40.3) — sin tocar esa validación. Como ningún chequeo de cuotas/acreditación diferida está keyado a `TarjetaDebito` (todos son `== TarjetaCredito` explícito), Débito no dispara ninguno — se comporta exactamente como un pago simple (igual que Efectivo/Transferencia/MercadoPago), sin cuotas ni fecha de acreditación.

**Impacto en capas**: Domain (`MetodoPago` enum), Infrastructure (3 archivos: `VentaService.cs`, `PagoVentaService.cs`, `PagoOrdenCompraService.cs` — solo agregar a las listas de métodos permitidos, sin lógica nueva), Web (`Ventas/Create.cshtml`, `Ventas/Details.cshtml`, `Ventas/Index.cshtml` — filtro, `OrdenesCompra/Details.cshtml` — mapas de métodos y opción de filtro). Sin migración EF (cambio de enum puro, sin columna nueva).

**Nota — no incluido en Entregas**: la pantalla de cobro en la entrega (`Entregas/Details.cshtml`) ya ofrece un subconjunto reducido de métodos (Efectivo/Transferencia/MercadoPago, sin Tarjeta de Crédito ni Banco Carrefour tampoco) — no se tocó, fuera del alcance pedido explícitamente ("en las ventas y en las compras").

## CR-56 — Venta con Factura anulada por Nota de Crédito ya no bloquea Cancelar (MH-013)

Pregunta directa del cliente (21/08/2026): "¿qué condiciones tiene el usuario para poder eliminar la venta? Si se generó una factura de una venta, una nota de crédito de esa factura, y se quiere eliminar la venta, ¿cuál es el proceso correcto?".

**Hallazgo al responder**: el guard de `VentaService.CancelarAsync`/`EditarAsync` (`TieneComprobanteAsociadoAsync`) contaba CUALQUIER `ComprobanteAfip.Estado=Emitido` asociado a la Venta — sin distinguir una Factura vigente de una Factura ya anulada por una Nota de Crédito, ni excluir a la propia NC (que tampoco debería bloquear, no es una obligación fiscal pendiente). Resultado real: una Venta con Factura + NC de esa factura (exactamente el caso "se corrigió una factura mal cargada") quedaba **bloqueada para cancelar**, contradiciendo el propio sentido de CR-55 (poder corregir y seguir operando la venta). Esto era el límite conocido ya documentado como riesgo abierto en el cierre de CR-55/MH-013 (QA lo había catalogado como "minor" al no ser bloqueante para ese release, pero la pregunta del cliente confirmó que sí importa en la práctica).

**Fix**: el criterio de "tiene comprobante que bloquea" pasa a exigir: `TipoComprobante` sea Factura A/B (no Nota de Crédito) **y** que no exista una Nota de Crédito `Emitido` con `ComprobanteAsociadoId` apuntando a esa factura. Aplicado de forma consistente en los 5 lugares donde se repetía el criterio viejo: `VentaService.TieneComprobanteAsociadoAsync` (guard de Cancelar/Editar), `VentaService` listado (`TieneComprobante`), `DashboardService`, `CajaService`, `ProyeccionFinancieraService` — cierra también MH-013 (catalogado en `docs/qa/regresiones-manuales.yml`).

**Condiciones vigentes para cancelar una Venta (documentado, no solo implícito)**:
1. No tiene ninguna Entrega asociada (en ningún estado).
2. No tiene ninguna Factura `Emitido` vigente (una Factura ya anulada por una NC `Emitido`, o un intento en `Estado=Error`, no bloquean).

**Proceso correcto para el escenario del cliente** (Factura + NC de esa factura, se quiere cancelar la Venta): ya no hace falta ningún paso adicional — una vez que la NC quedó `Emitido`, la Venta se puede cancelar directo desde "Cancelar venta", igual que cualquier venta sin facturar.

**Impacto en capas**: Infrastructure (5 archivos, ver arriba). Sin migración EF.

## CR-55 — Nota de Crédito para anular una Factura AFIP emitida por error

Pedido explícito del cliente vía `/agentes-ia-orquestador` (21/08/2026): "el usuario hizo la factura mal, por lo tanto tiene que generar una nota de crédito de la factura emitida para poder anularla, por definición de AFIP".

**Contexto y objetivo**: una factura electrónica con CAE real ya emitida no se puede corregir ni borrar — AFIP exige un documento fiscal separado (Nota de Crédito) que la anule formalmente. Sin esto, un error de carga (CUIT mal, monto mal, cliente equivocado) en la primera factura real recién emitida (CAE 86349291101930, hoy) queda sin forma de corregirse dentro del sistema.

**Decisiones confirmadas con el cliente** (3 `AskUserQuestion` antes de diseñar):
1. **Alcance: Nota de Crédito siempre TOTAL** (nunca parcial) — replica el 100% de ítems/montos/cliente de la factura original. Una NC parcial queda fuera de este alcance (ampliación futura si hace falta).
2. **Reabre la posibilidad de refacturar**: al emitirse con éxito la NC, se revierte `VentaItem.CantidadFacturada` de cada ítem por la cantidad que cubría la factura original — la Venta vuelve a estar disponible para facturarse de nuevo, ya con los datos correctos.
3. **Mismo acceso que Facturar**: Administrador y Vendedor por igual (policy `RequireVentas`, ya vigente en `ComprobantesAfipController` — no se agrega restricción nueva).

**Alcance incluido**:
- Acción "Generar Nota de Crédito" disponible únicamente desde un `ComprobanteAfip` en `Estado=Emitido` (Factura A o B) que todavía no tenga una NC asociada.
- Motivo obligatorio (texto libre, trazabilidad interna — nunca se envía a AFIP), mismo criterio que `Cancelar` de OrdenCompra/Cheque.
- Emisión real contra AFIP vía WSFEv1 (mismo circuito que Facturar), incluyendo el bloque `CbtesAsoc` (tipo/punto de venta/número de la factura original) — requisito de AFIP para vincular la NC a la factura que anula. Mismo Punto de Venta que la original (ya habilitado, Punto de Venta 7).
- Tipo de comprobante derivado automáticamente de la factura original: Factura A (1) → NC A (3); Factura B (6) → NC B (8) — códigos reales de AFIP, mismo criterio que `TipoComprobanteAfip` ya usa hoy (el valor del enum ES el CbteTipo de AFIP, sin mapeo intermedio).
- PDF de la NC reutilizando el diseño de Factura (CR-43), con el encabezado y código de comprobante correspondientes.
- Mismo patrón de reintento (`Estado=Error`, reintentable) que ya tiene `ComprobanteAfip` — si falla la emisión de la NC, la factura original sigue vigente (no se marca anulada hasta que la NC se emita con éxito de verdad).

**Alcance NO incluido (este sprint)**:
- Nota de Crédito parcial.
- Nota de Débito (documento inverso).
- Anular una Nota de Crédito ya emitida.
- Generar una NC sobre un comprobante que no esté `Estado=Emitido` (no tiene CAE real que asociar).

**Reglas funcionales**:
1. Un `ComprobanteAfip` (factura) puede tener a lo sumo 1 Nota de Crédito asociada — si ya la tiene, la acción deja de estar disponible.
2. La factura original queda "anulada" (inferido por tener una NC asociada con `Estado=Emitido`, no un campo booleano nuevo) recién cuando la NC se emite con éxito — no antes.
3. La Nota de Crédito es un `ComprobanteAfip` más (mismo modelo/tabla), no una entidad nueva — se distingue por `TipoComprobante` (NotaCreditoA/B) y por tener `ComprobanteAsociadoId` apuntando a la factura que anula.

**Impacto por capa (preliminar)**:
- Domain: `TipoComprobanteAfip` gana `NotaCreditoA=3`/`NotaCreditoB=8`; `ComprobanteAfip` gana `ComprobanteAsociadoId` (nullable, auto-FK) y `Motivo` (nullable).
- Application: `AfipComprobanteRequestDto` gana el bloque `CbteAsociado` (tipo/puntoventa/número); nuevo Input para "Generar Nota de Crédito" (comprobanteId + motivo).
- Infrastructure: `AfipService.ArmarFecaeSolicitarEnvelope` arma `CbtesAsoc` cuando corresponde; `ComprobanteAfipService` gana `GenerarNotaCreditoAsync` (crea la NC replicando ítems/montos/cliente de la original, emite, revierte `CantidadFacturada` si tiene éxito).
- Web: nueva acción + botón en `ComprobantesAfip/Details`, formulario de motivo (SweetAlert2, mismo patrón que Cancelar OC).
- 1 migración EF (2 columnas nuevas en `ComprobantesAfip`).

**Riesgos y supuestos**:
- Riesgo: el flujo de emisión real recién se validó hoy por primera vez (1 factura real con CAE) — la Nota de Crédito es un `CbteTipo`/bloque `CbtesAsoc` distinto, todavía sin probar contra AFIP real en este sistema. Recomendado probar con un monto bajo antes de confiar el flujo a un caso real de corrección.
- Supuesto: el Punto de Venta 7 (tipo "Web Services", ya habilitado y validado) cubre también la emisión de Notas de Crédito — AFIP no exige un alta separada por tipo de comprobante dentro del mismo punto de venta.

## CR-52 — Bug crítico: AFIP no podía emitir ningún comprobante real ("The system cannot find the file specified")

Reportado por el cliente en producción (20/08/2026): intento real de facturar la Venta #676 (Comprobante AFIP #304, Factura B) falló con "No se pudo emitir el comprobante: The system cannot find the file specified."

**Causa raíz**: `AfipSettings.CertificadoPath` en `appsettings.Production.json` es una ruta relativa (`"Certificados/marihogarprod.p12"`), pasada tal cual a `X509CertificateLoader.LoadPkcs12FromFile` en `AfipService.FirmarCms` — que la resuelve contra el directorio de trabajo ACTUAL del proceso (`Directory.GetCurrentDirectory()`), no necesariamente el `ContentRootPath` del sitio (depende del modelo de hosting IIS/ANCM). Ante cualquier discrepancia entre ambos, .NET lanza el error genérico "The system cannot find the file specified" aunque el archivo exista en el lugar correcto del servidor. Es probable que esta sea la **primera vez que se ejecutó de verdad** el camino real de emisión contra AFIP con el certificado de producción — las 6 facturas reales de CR-42/43 se cargaron directo en la base de datos, sin pasar por `AfipService.EmitirAsync`, así que el bug nunca se había disparado antes.

**Fix**: `AfipService` gana `IWebHostEnvironment` inyectado y resuelve siempre `CertificadoPath` contra `ContentRootPath` (`Path.Combine`, o respeta la ruta tal cual si ya viniera absoluta) — mismo patrón ya usado por `LocalFileStorageService` (con `WebRootPath`) para nunca depender del directorio de trabajo del proceso. Se agrega además un chequeo temprano (`File.Exists`) con un mensaje claro indicando la ruta resuelta exacta, para que un futuro problema de archivo faltante/permisos se diagnostique directo en el mensaje de error en vez de un "file not found" genérico.

**Sin pérdida de datos**: el Comprobante AFIP #304 quedó en estado `Error` (con `DetalleError` guardado, sin CAE — la falla ocurre localmente al cargar el certificado, antes de siquiera llamar al webservice de AFIP), estado ya diseñado para ser reintentable sin necesidad de ninguna corrección de datos — una vez deployado el fix, el Administrador puede reintentar la emisión directo desde la pantalla del comprobante ("Reintentar").

**2do hallazgo (mismo día, mismo comprobante #304 reintentado tras el primer fix)**: el error persistió **idéntico** — confirmado directo contra la base de producción (`ComprobanteAfip.DetalleError`), no solo por lo que reportó el cliente. Esto descarta que el 1er fix no se hubiera aplicado (un redeploy posterior confirmó, por diff de `msdeploy`, que los binarios ya estaban al día) y apunta a la causa real: `X509CertificateLoader.LoadPkcs12FromFile` sin flags usa `X509KeyStorageFlags.DefaultKeySet`, que en Windows intenta persistir la clave privada en el perfil de usuario del proceso (`%USERPROFILE%\AppData\...`). En hosting compartido (IIS), si el Application Pool no tiene "Load User Profile" habilitado, esa carpeta no existe — y CryptoAPI devuelve el mismo error genérico "The system cannot find the file specified", aunque el .p12 esté presente y bien ubicado.

**3er hallazgo (mismo día)**: el fix con `X509KeyStorageFlags.EphemeralKeySet` **tampoco** resolvió el problema (mismo error, reintentado por el cliente). El cliente aportó el dato decisivo: `delicias-naturales` — sistema hermano que factura contra AFIP producción de verdad, en **este mismo servidor** — sirvió de referencia real ya probada. Revisando su código (`Models/Afip/LoginTicket.cs`, `CertificadosX509Lib.ObtieneCertificadoDesdeArchivo`, proyecto .NET Framework 4.7.2 ya en producción) confirmó que usa `X509KeyStorageFlags.MachineKeySet`, no `Ephemeral`. Fix final: se cambia a `MachineKeySet` — la clave privada se guarda en el almacén de certificados de la máquina (no del perfil de usuario), evitando la misma dependencia sin necesitar que el Application Pool cargue un perfil, con la garantía adicional de ser el flag que **ya funciona de verdad en este servidor** para otro sistema.

**Impacto en capas**: Infrastructure (`AfipService.cs`). Sin migración EF, sin script de corrección de datos.

## CR-50 — Cheques de compra: fecha de emisión futura permitida + nota interna editable en cualquier estado

Pedido explícito del cliente (19/08/2026), 2 puntos en el mismo mensaje, en respuesta directa a CR-49:

**CA-CR50.1**: "Cheques con fecha de emisión futura también tienen que estar contemplados." Simétrico a CR-49 (que sacó el piso de fecha de vencimiento): se saca también el techo "no puede ser futura" de la fecha de emisión — tanto el `max=hoy` del datepicker (`OrdenesCompra/Details.cshtml`, `.inp-cheque-emision`) como la validación server-side equivalente en `PagoOrdenCompraService.RegistrarPagoAsync` (que además estaba catalogada como fix de bug en `docs/qa/regresiones-manuales.yml`, MH-003 — marcada ahí como `superseded_por` este CR, no una regresión). Permite cargar un cheque diferido con fecha de emisión futura (todavía no entregado, pero ya conocido de antemano). Se mantiene la única validación que sigue teniendo sentido pase lo que pase: emisión nunca posterior a vencimiento.

**CA-CR50.2**: "Las compras también deben tener un campo nota para cargar comentarios." Investigación: `OrdenCompra.NotaInterna` ya existía desde CR-27, pero solo era editable a través del formulario de Crear/Editar (`OrdenCompraService.UpdateAsync`), que a su vez solo funciona mientras la OC está en Borrador (`EstadosEditables`) — una vez Confirmada/Recibida/Cancelada, no había forma de cargar o corregir la nota. Nuevo método `IOrdenCompraService.ActualizarNotaInternaAsync(id, nota)`, independiente de la máquina de estados de la OC (a diferencia de Items/Proveedor/Comprobante/Impuestos, la nota es solo un comentario libre que nunca afecta stock ni Cuenta Corriente, así que no tiene sentido bloquearla junto con el resto). En `OrdenesCompra/Details.cshtml` (visible en cualquier estado, a diferencia de la pantalla de Editar) la nota pasa de mostrarse solo si no está vacía a ser siempre un campo editable con botón "Guardar nota" — acción propia (`ActualizarNotaInterna`), independiente del botón "Editar".

**Impacto en capas**: Application (`IOrdenCompraService.ActualizarNotaInternaAsync` nuevo), Infrastructure (`PagoOrdenCompraService.cs`, `OrdenCompraService.cs`), Web (`OrdenesCompraController.cs`, `OrdenesCompra/Details.cshtml`). Sin migración EF.

## CR-49 — Cheques de compra: fecha de vencimiento pasada permitida (cargar cheques ya vencidos)

Pedido explícito del cliente (19/08/2026): "al cargar los cheques, el usuario quiere poder seleccionar fechas anteriores dentro del datepicker, para poder cargar cheques ya emitidos días antes."

**Investigación**: la fecha de emisión del cheque (`inp-cheque-emision`) ya permitía cualquier fecha pasada (solo tenía `max=hoy`, tanto en el cliente como revalidado en el server). El bloqueo real estaba en la **fecha de vencimiento**: `PagoOrdenCompraService.RegistrarPagoAsync` rechazaba con "La fecha de vencimiento del cheque no puede ser anterior a hoy" — y el datepicker del cliente tenía `min=hoy`. Esto impedía cargar un cheque real emitido hace tiempo cuyo plazo de 30/60/90 días ya se cumplió (un cheque vencido pero todavía no acreditado es, desde CR-46, un estado perfectamente válido: sigue `Pendiente` hasta que se acredita, sin importar si ya pasó su fecha de vencimiento).

**Fix**: se saca el piso de "no anterior a hoy" tanto del datepicker (`OrdenesCompra/Details.cshtml`, ya no tiene `min`) como de la validación server-side (`PagoOrdenCompraService.RegistrarPagoAsync`) — se mantienen las otras 2 validaciones intactas (emisión nunca posterior a vencimiento, emisión nunca futura). Sin migración EF (cambio de validación puro).

## CR-48 — Precio de lista editable en Producto (dejó de ser calculado)

Pedido explícito del cliente (19/08/2026), corrigiendo el texto "(calculado automático, +21%)" que se mostraba junto a Precio de lista en `Productos/Create.cshtml`/`Edit.cshtml`: quiere poder editarlo directamente en la ficha del producto, no que dependa siempre y exclusivamente de Precio efectivo ×1,21.

**Decisión de implementación**: `Producto.PrecioLista` era `[NotMapped]` (propiedad calculada, `PrecioEfectivo × 1,21` vía `PorcentajeHelper.AplicarRecargo`, documentada explícitamente en CR-21 como "nunca un campo propio editable"). Pasa a ser una columna real editable — mismo patrón "sugerido pero editable" ya usado por `VentaItem.PrecioTarjeta` (CR-37/38): la UI sigue sugiriendo `PrecioEfectivo × 1,21` en vivo, pero el valor que se guarda es el que quede en el campo.

- **Alta de producto** (`Create.cshtml`): el campo se autocompleta con la sugerencia mientras el usuario no lo haya tocado a mano — apenas lo edita, deja de autocompletarse.
- **Edición de producto** (`Edit.cshtml`): el campo arranca con el valor ya guardado (nunca se pisa solo, para no perder un ajuste manual previo) — se muestra la sugerencia al lado con un link "usar sugerido" para copiarla si el usuario lo pide.
- **Aumento masivo de precios (M16)**: sigue ajustando únicamente `PrecioEfectivo` — `PrecioLista` **ya no lo sigue automáticamente**, queda tal como esté configurado por producto (consecuencia directa de que ahora es un valor independiente; si el aumento masivo también lo recalculara solo, dejaría de ser realmente editable).

**Impacto en capas**: Domain (`Producto.PrecioLista` deja de ser `[NotMapped]`), Infrastructure (`AppDbContext` — precisión de columna, `ProductoService.CreateAsync`/`UpdateAsync`/`ListarAsync`), Application (`ProductoInput.PrecioLista` nuevo), Web (`ProductoFormViewModel`, `ProductosController`, `Productos/Create.cshtml`/`Edit.cshtml`). **1 migración EF** (`AddPrecioListaColumn`) con backfill `PrecioEfectivo × 1,21` para los productos existentes — verificada contra `marihogar_dev` (221 productos, 0 diferencias contra el valor que se calculaba antes) antes de aplicar en producción.

## CR-46 — Producto: % descuento/recargo opcionales + Cheque de compra no cuenta como pagado hasta acreditarse

Pedido explícito del cliente (19/08/2026), 2 reportes en el mismo mensaje:

**CA-CR46.1 (Producto)**: "al crear y editar producto: % de descuento % de recargo deben ser campos opcionales." `ProductoFormViewModel.PorcentajeDescuento`/`PorcentajeRecargo` eran `decimal` no-nullable — ASP.NET Core exige un valor aunque no tengan `[Required]` explícito (un `decimal` no-nullable no admite bindear un campo vacío). Cambiados a `decimal?`; el controller (`ProductosController.MapInput`) coalesce a 0 antes de pasar al Service (mismo comportamiento final que si el usuario hubiera tipeado 0 — sin cambio de esquema ni de Domain).

**CA-CR46.2 (Cheque de compra)**: "se agregan pagos de tipo cheque a 30 días y el estado del pago de la compra es Pagado, no debería ser estado pendiente? [...] total saldo pendiente es 0 pero el cliente no pagó nada todavía" — reportado sobre OC #30 en producción. Investigación confirmó: el Estado Pendiente/Pagado de CR-44 dependía únicamente del campo "fecha tentativa de pago", que nadie completa en un pago con Cheque (ya tiene su propia fecha de vencimiento) — el pago quedaba `Pagado` y el `MovimientoCCProveedor.Pago` se posteaba de inmediato al entregar el cheque, sin importar si el banco ya lo había cobrado (diseño original de CR-7).

**Decisión confirmada con el cliente** (`AskUserQuestion`, opción recomendada elegida): un pago con Cheque a proveedor ahora **siempre** arranca `Estado=Pendiente` (independiente de la fecha tentativa, que ya no aplica a Cheque) y el `Pago` real en la Cuenta Corriente del proveedor recién se postea cuando el Administrador marca el cheque como **Acreditado** en la pantalla de Cheques (`ChequeService.AcreditarAsync`, ya existía como acción manual desde CR-7) — con `Fecha = Cheque.FechaVencimiento` (cuándo realmente salió el dinero, no el momento del click), mismo criterio que `ConfirmarPagoAsync` (CA-CR44.4). `ChequeService.RechazarAsync` deja de postear el contramovimiento de reversión que tenía: un cheque solo se puede rechazar desde Pendiente, y bajo el nuevo diseño un cheque Pendiente nunca llegó a postear el Pago real, así que no hay nada que revertir. El botón "Confirmar pago" genérico de `OrdenesCompra/Details.cshtml` se oculta para pagos con Cheque (con guard también server-side en `ConfirmarPagoAsync`) — un cheque se confirma exclusivamente acreditándolo.

**Bug de consistencia encontrado y corregido en el mismo paso**: `ProyeccionFinancieraDto.GastosComprometidos` sumaba `ChequesPorVencer + SaldoPendienteOrdenesCompra` — antes de CR-46 esto era seguro porque un cheque nunca quedaba en el saldo pendiente de la OC (se pagaba al entregarlo), pero ahora un cheque no acreditado queda en AMBOS lados (su OC lo cuenta en `SaldoPendienteOrdenesCompra` Y la consulta de cheques lo vuelve a contar en `ChequesPorVencer`), duplicando el monto. Corregido: `GastosComprometidos` pasa a ser solo `SaldoPendienteOrdenesCompra` (ya incluye los cheques no acreditados); `ChequesPorVencer` se mantiene como dato informativo (mismo criterio que `PagosCompraProgramados`/`PagosVentaPorAcreditar`), mostrando cuánto de ese saldo son cheques con vencimiento dentro del horizonte.

**Corrección retroactiva en producción** (confirmada con el cliente): 6 pagos con cheque ya cargados (OC #16, #20 ×3, #30 ×2 — proveedores Cardozo y Espumas Pilar SRL, cheques con vencimiento entre 28/08 y 12/10/2026, todos con `Cheque.Estado=Pendiente`) tenían el `Pago` real ya posteado. Corregidos con un script dedicado (dry-run primero, verificado, luego aplicado): cada uno vuelve a `Estado=Pendiente` y se postea un `Cargo` de reversión por el mismo importe (nunca se borra el movimiento original, mismo criterio ya usado por `MovimientoCCProveedor`) — el saldo pendiente de esas 3 órdenes de compra vuelve a reflejar la realidad.

**Impacto en capas**: Web (`ProductoFormViewModel`, `ProductosController.MapInput`, `OrdenesCompra/Details.cshtml`, `Cheques/Index.cshtml`, `ProyeccionFinanciera/Index.cshtml`), Application (`IChequeService` doc, `ProyeccionFinancieraDto.GastosComprometidos`), Infrastructure (`PagoOrdenCompraService.RegistrarPagoAsync`/`ConfirmarPagoAsync`, `ChequeService.AcreditarAsync`/`RechazarAsync`, `ProyeccionFinancieraService`). Sin migración EF (sin cambio de esquema). Corrección de datos en producción vía script dedicado, con backup previo y verificación posterior.

## CR-44 — Pagos de Orden de Compra programables con fecha tentativa + notificación de vencimiento

Pedido explícito del cliente vía `/agentes-ia-orquestador` (19/08/2026): "todos los métodos de pago de las compras deben tener una fecha tentativa de pago, donde el usuario puede cargar el pago para días próximos, y que cuando ingrese al sistema ese día, se informe a través de una notificación que tiene pagos por vencer el día de la fecha."

**Decisión de diseño confirmada con el cliente antes de implementar** (`AskUserQuestion`): al investigar el código existente se encontró que, hoy, un `PagoOrdenCompra` (cualquier método, incluido Cheque) impacta la Cuenta Corriente del proveedor **apenas se carga**, sin importar la fecha — el pedido del cliente habla de "pagos por vencer", que sugiere una obligación todavía no saldada. Se preguntó explícitamente si programar un pago debía descontar el saldo del proveedor ya mismo o recién al confirmarse — el cliente eligió **recién cuando se confirma**. Esto define el diseño: no es simplemente hacer editable `PagoOrdenCompra.Fecha` (como CR-29 hizo en Ventas), sino un estado propio con confirmación manual — mismo patrón arquitectónico ya usado por `Cheque` (Pendiente→Acreditado) y por `PagoVenta` con Tarjeta de crédito (CR-34, `EstadoAcreditacionPago` Pendiente→Acreditado, CC posteada recién al confirmar).

**CA-CR44.1**: `PagoOrdenCompra` gana `Estado` (`EstadoPagoOrdenCompra`: Pendiente=1/Pagado=2, default Pagado — no rompe los ~330 pagos históricos, todos pagos reales ya hechos), `FechaPagoTentativa` (nullable, obligatoria solo si Estado=Pendiente) y `Notificado` (bool, mismo patrón que `Cheque.Notificado`).

**CA-CR44.2**: al registrar un pago (`PagoOrdenCompraService.RegistrarPagoAsync`), una línea con `FechaPagoTentativa` estrictamente futura (comparada contra la fecha real de Argentina, `HorarioArgentino.Ahora`) queda `Estado=Pendiente` y **NO** postea el movimiento de `MovimientoCCProveedor` — el `Cheque` (si el método es Cheque) sí se crea igual en ese momento, con todos sus datos, porque es un documento físico ya decidido, independiente de si la CC ya lo contabiliza. Sin fecha, o con una fecha de hoy/pasada, el pago se registra exactamente igual que siempre (Estado=Pagado, CC posteada de inmediato) — comportamiento histórico intacto.

**CA-CR44.3**: `OrdenCompraDetailDto.MontoPagado`/`SaldoPendiente` excluyen los pagos `Estado=Pendiente` (además del criterio ya existente de excluir Cheque Rechazado) — el saldo que le debés al proveedor no baja hasta que el pago programado se confirme de verdad, consistente con la decisión del cliente.

**CA-CR44.4**: nuevo `IPagoOrdenCompraService.ConfirmarPagoAsync` (Administrador-only, mismo criterio que `Cheque.AcreditarAsync`/`Venta.AcreditarPagoAsync`) — recién ahí se postea el `MovimientoCCProveedor.Pago` real, con `Fecha = FechaPagoTentativa` (no el momento en que el Administrador confirma), mismo criterio que `CA-CR34.2`.

**CA-CR44.5**: nuevo job diario `PagoOrdenCompraVencimientoHostedService` (patrón idéntico a `ChequeAcreditacionHostedService`/`PagoVentaAcreditacionHostedService`, corrida a las 03:10 ART — 5 min después del de Ventas, para no competir por el mismo instante) que **solo notifica**, nunca cambia `Estado` — busca pagos `Pendiente` con `FechaPagoTentativa <= hoy` sin notificar todavía, marca `Notificado=true` y dispara una notificación in-app por pago a SuperUsuario + Administrador, con link directo a la Orden de Compra. Se mantiene como job separado de los otros 2 a propósito (mismo razonamiento ya documentado en `PagoVentaAcreditacionHostedService`: son 3 dominios distintos que conviene no acoplar).

**Impacto en capas**: Domain (`EstadoPagoOrdenCompra` nuevo, `PagoOrdenCompra` +3 propiedades), Application (`ICCProveedorService`/`IPagoOrdenCompraService` ampliados, `PagoOrdenCompraVencidoDto` nuevo), Infrastructure (`CCProveedorService`, `PagoOrdenCompraService`, `PagoOrdenCompraVencimientoHostedService` nuevo, `DependencyInjection.cs`), Web (`OrdenesCompraController` +1 acción, `OrdenesCompra/Details.cshtml` — fecha tentativa por línea de pago, badge Pendiente/Pagado + botón "Confirmar pago" en el historial). 1 migración EF (`AddPagoOrdenCompraFechaTentativa` — 3 columnas, `Estado` con default explícito a nivel de columna, verificada contra `marihogar_dev`: los 333 pagos existentes quedaron `Pagado` sin script de datos aparte).

**CA-CR44.6** (agregado el mismo día, pedido del cliente): `ProyeccionFinancieraService` gana `PagosCompraProgramados`/`PagosCompraProgramadosCantidad` — dato informativo, mismo criterio ya establecido por `PagosVentaPorAcreditar` (CR-29/34): **no** se suma a `GastosComprometidos`/`TieneDeficit`. Motivo explícito: ese monto ya está completo en `SaldoPendienteOrdenesCompra` (la OC sigue "debiendo" ese pago hasta que se confirme de verdad) — sumarlo aparte lo hubiera contado dos veces. **Bug de consistencia encontrado en el mismo paso**: el cálculo de `SaldoPendienteOrdenesCompra` (`ocsConSaldo` en `ProyeccionFinancieraService`) tenía su propia copia del criterio de exclusión de `OrdenCompraDetailDto.MontoPagado` (excluye Cheque Rechazado) pero **no** había sido actualizada con la exclusión nueva de `Estado=Pendiente` de CA-CR44.3 — corregido para que ambos cálculos nunca diverjan.

## CR-45 — Fecha de compra editable + fecha de recepción de mercadería

Pedido explícito del cliente, en paralelo al deploy de CR-44 (19/08/2026): "se solicita poder editar la fecha de la compra, o que se permitan cargar compras con fecha pasada. que sea fecha de compra y fecha de recepción de mercadería."

`OrdenCompra.Fecha` y `OrdenCompra.FechaRecepcion` ya existían en el modelo (cargados en producción desde el sprint original) pero ambos estaban hardcodeados a `DateTime.UtcNow` en el Service — sin campo de UI ni parámetro para elegirlos. No hizo falta migración EF, solo dejar de hardcodear ambos valores.

**CA-CR45.1**: `OrdenCompraInput` gana `Fecha` (nullable, solo día calendario) — mismo patrón ya usado por `VentaInput.Fecha` (CR-42): se combina el día elegido con la hora actual de Argentina y se convierte a UTC real vía `HorarioArgentino.ConvertirAUtc`. A diferencia de Venta, acá se permite explícitamente cualquier fecha pasada (es el pedido literal del cliente — "cargar compras con fecha pasada"), pero nunca futura. Sin fecha explícita, cae al comportamiento histórico (ahora mismo). Editable tanto al crear como al editar (mientras la OC sigue en Borrador, mismo guard `EstadosEditables` ya existente). Como el `OrdenesCompraController` completo ya exige la policy `RequireAdministracion` a nivel de clase, no hizo falta ningún gating adicional de rol (a diferencia de CR-42 en Ventas, donde sí hubo que distinguir Administrador de Vendedor).

**CA-CR45.2**: `IOrdenCompraService.RecibirAsync` gana un parámetro opcional `fechaRecepcion` (mismo criterio de validación: nunca futura). Al marcar una OC como Recibida, la fecha elegida se cascadea de forma consistente a `OrdenCompra.FechaRecepcion`, al movimiento de stock de cada línea (`IStockService.RegistrarMovimientoAsync`, que ya tenía el parámetro opcional `fecha` desde CR-42) y al Cargo posteado en la Cuenta Corriente del proveedor (`ICCProveedorService.RegistrarMovimientoAsync`, que ya tenía el parámetro opcional `fecha` desde CR-44) — para que una recepción backdateada no quede con fecha de hoy en el stock/CC y la fecha real solo en la OC (mismo criterio de consistencia ya aplicado en CR-42 sobre Ventas). En la UI (`OrdenesCompra/Details.cshtml`), el botón "Marcar recibida" pasó de un simple confirm a un SweetAlert2 con selector de fecha (vacío = hoy), mismo patrón visual ya usado por "Cancelar orden de compra" (motivo obligatorio).

**Impacto en capas**: Application (`OrdenCompraInput.Fecha` nuevo, `IOrdenCompraService.RecibirAsync` con parámetro opcional nuevo), Infrastructure (`OrdenCompraService.CreateAsync`/`UpdateAsync`/`RecibirAsync`, helper privado `CalcularFecha` compartido), Web (`OrdenCompraFormViewModel.Fecha`, `OrdenesCompraController.MapInput`/`Edit` GET/`Recibir`, `OrdenesCompra/Create.cshtml` — input de fecha junto al selector de Proveedor, `OrdenesCompra/Details.cshtml` — SweetAlert de fecha en "Marcar recibida"). **Sin migración EF** (ambas columnas ya existían en el esquema desde el sprint original, solo se dejó de hardcodear `DateTime.UtcNow`).

## Historial de ajustes
- 2026-08-27 — CR-60: ver sección completa "CR-60 — Cheques de compra: plazo de días editable a mano" más arriba. El `<select>` fijo de 30/60/90 días pasa a un número libre — el autocálculo de vencimiento y el modelo ya lo soportaban sin cambios. Sin migración EF.
- 2026-08-27 — CR-59 (Diseño + Arquitectura + Presupuesto, gate pendiente): ver sección completa "CR-59 — Pagos con tarjeta de crédito a liquidar" más arriba. Pedido vía orquestador, planteado como pregunta abierta sobre dónde ubicar el listado — resuelto con pantalla dedicada (clon de Cheques) + card de Dashboard. Sin migración EF. Presupuesto: ítem único, PERT 2.37h, horas finales 2.6h (riesgo Bajo, contingencia 10%), **USD 37**. Pendiente aprobación explícita del cliente sobre el presupuesto antes de Implementación.
- 2026-08-26 — CR-58: ver sección completa "CR-58 — Órdenes de compra: tag de facturación + Dashboard 'vista CEO' (4 métricas nuevas)" más arriba. Tag de OC facturadas/no facturadas (Index + Dashboard). 4 métricas CEO confirmadas por el cliente vía 2 `AskUserQuestion`: Deuda total a proveedores, Margen bruto del período (costo al precio de compra actual, limitación aceptada), Gastos operativos del período, Ticket promedio de venta. Sin migración EF.
- 2026-08-21 — CR-57: ver sección completa "CR-57 — Método de pago 'Tarjeta de débito' en Ventas y Compras" más arriba. `MetodoPago.TarjetaDebito=8`, habilitado en Ventas y Compras (no en Entregas). 2 decisiones confirmadas: cobra precio Efectivo (no transferencia) y se acredita al instante (no acreditación diferida como Tarjeta de Crédito) — se logra sin lógica nueva, solo agregándolo a las listas de métodos permitidos sin sumarlo a `metodosRequierenConIva` ni a ningún chequeo `== TarjetaCredito`. Sin migración EF.
- 2026-08-21 — CR-56: ver sección completa "CR-56 — Venta con Factura anulada por Nota de Crédito ya no bloquea Cancelar (MH-013)" más arriba. El cliente preguntó por el proceso correcto para eliminar una venta con Factura+NC y encontramos que hoy bloqueaba — corregido en 5 archivos (mismo criterio: Factura vigente sin NC asociada). Cierra MH-013. Sin migración EF.
- 2026-08-21 — CR-55 (Discovery + Análisis): ver sección completa "CR-55 — Nota de Crédito para anular una Factura AFIP emitida por error" más arriba. Pedido explícito del cliente vía orquestador. 3 decisiones confirmadas: NC siempre total (no parcial), reabre `CantidadFacturada` para refacturar, mismo acceso que Facturar (Administrador + Vendedor). Pendiente: Diseño, Arquitectura y Presupuesto (gate cliente) antes de implementar.
- 2026-08-20 — CR-52: ver sección completa "CR-52 — Bug crítico: AFIP no podía emitir ningún comprobante real" más arriba. Resumen: `AfipService` resolvía el certificado .p12 con una ruta relativa dependiente del directorio de trabajo del proceso — corregido para resolver siempre contra `IWebHostEnvironment.ContentRootPath`. Comprobante #304 queda reintentable sin corrección de datos. Sin migración EF.
- 2026-08-19 — CR-51: ver sección completa "CR-51" en "Modelo de precios" más arriba. Resumen: renombre "Precio de lista" → "Precio transferencia" en todo el proyecto (Producto, Ventas), y eliminación del autocompletado/sugerencia "+21%" que CR-48 había agregado — el campo se completa siempre a mano. Sin migración EF.
- 2026-08-19 — CR-50: ver sección completa "CR-50 — Cheques de compra: fecha de emisión futura permitida + nota interna editable en cualquier estado" más arriba. Resumen: se saca el techo "no puede ser futura" de la fecha de emisión del cheque (simétrico a CR-49), y `OrdenCompra.NotaInterna` gana una acción propia (`ActualizarNotaInterna`) que la hace editable sin importar el estado de la OC, no solo en Borrador. Sin migración EF.
- 2026-08-19 — CR-49: ver sección completa "CR-49 — Cheques de compra: fecha de vencimiento pasada permitida" más arriba. Resumen: se saca el piso "vencimiento no puede ser anterior a hoy" (datepicker + validación server) para poder cargar cheques ya emitidos que vencieron hace días — estado válido desde CR-46 (sigue Pendiente hasta acreditarse). También se investigó y confirmó de paso que `OrdenCompra.NotaInterna` ya existe desde CR-27 (campo colapsable "+ Agregar nota interna" en `Create.cshtml`/`Edit.cshtml`) — el cliente pidió lo mismo sin saber que ya estaba, no hizo falta ningún cambio de código para eso. Sin migración EF.
- 2026-08-19 — CR-48: ver sección completa "CR-48 — Precio de lista editable en Producto (dejó de ser calculado)" más arriba. Resumen: `Producto.PrecioLista` dejó de ser `[NotMapped]`/calculado — ahora es una columna real editable, con la sugerencia `PrecioEfectivo×1,21` precargada en la UI (Create autocompleta hasta que se toca a mano, Edit nunca pisa el valor guardado, solo sugiere). Aumento masivo de precios ya no actualiza PrecioLista automáticamente. 1 migración EF con backfill, verificada contra `marihogar_dev` (221 productos, 0 diferencias).
- 2026-08-19 — CR-46: ver sección completa "CR-46 — Producto: % descuento/recargo opcionales + Cheque de compra no cuenta como pagado hasta acreditarse" más arriba. Resumen: % descuento/recargo de Producto ahora opcionales (nullable). Un pago con Cheque a proveedor ya no cuenta como pagado al entregarlo — recién cuenta cuando se acredita en la pantalla de Cheques (decisión confirmada con el cliente). Bug de doble conteo encontrado y corregido en Proyección Financiera (`ChequesPorVencer` ya no se suma aparte de `SaldoPendienteOrdenesCompra`). Corrección retroactiva de 6 pagos con cheque ya cargados en producción (OC #16/#20/#30), con backup previo y verificación posterior. Sin migración EF.
- 2026-08-19 — CR-45: ver sección completa "CR-45 — Fecha de compra editable + fecha de recepción de mercadería" más arriba. Resumen: `OrdenCompraInput.Fecha` (nunca futura, permite pasada) editable en Create/Edit; `RecibirAsync` gana `fechaRecepcion` opcional, cascadeado a stock y a la CC del proveedor. Sin migración EF (columnas ya existían, solo se dejó de hardcodear `DateTime.UtcNow`).
- 2026-08-19 — CR-44: ver sección completa "CR-44 — Pagos de Orden de Compra programables con fecha tentativa + notificación de vencimiento" más arriba en este mismo archivo. Resumen: pagos de OC ahora se pueden programar con una fecha tentativa futura (cualquier método) — decisión confirmada con el cliente de que un pago programado NO impacta la CC del proveedor hasta confirmarse manualmente, mismo patrón ya usado por Cheque/PagoVenta-Tarjeta. Nuevo job diario notifica cuando un pago programado vence. 1 migración EF, verificada contra `marihogar_dev` (333 pagos históricos sin cambio de comportamiento).
- 2026-08-19 — CR-43: pedido explícito del cliente ("generar un reporte de factura lo más parecido a las facturas que se cargaron hoy... usar datos oficiales de ARCA como fuente de verdad"), comparado directamente contra las 6 facturas reales descargadas de la página de AFIP (mismo CUIT). **Hallazgo crítico no relacionado con el diseño**: `Afip:PuntoVenta` en `appsettings.Production.json` estaba en `1`, pero las 6 facturas reales muestran Punto de Venta **4** — si el sistema llegara a emitir un comprobante real antes de este fix, habría numerado con un punto de venta que no es el que el cliente usa de verdad en AFIP. Corregido a `4`. `AfipSettings` gana 5 campos nuevos de solo-impresión (nunca se envían al webservice WSFE, que solo necesita CUIT/PuntoVenta): `RazonSocial`, `DomicilioComercial`, `CondicionIva`, `IngresosBrutos`, `FechaInicioActividades` — cargados con los datos reales tal como figuran en las facturas ("MARI MARCOS VALENTIN", domicilio real, "IVA Responsable Inscripto", "20-33113613-2", 01/09/2011). `ComprobanteAfipService.GenerarPdfAsync` rediseñado por completo para replicar el formato oficial (reemplaza el diseño de marca propia "MariHogar" del rediseño anterior): caja "ORIGINAL", letra de tipo + "COD. 00X" en un box central, bloque de emisor/numeración/CUIT/IIBB/inicio de actividades, bloque de cliente con Condición frente al IVA ("IVA Responsable Inscripto" si Factura A, "Consumidor Final" si B) y Condición de venta (derivada: "Contado" si todos los pagos son Efectivo, "Otra" en cualquier otro caso), tabla de ítems con las mismas 8 columnas del formulario oficial, y la leyenda "Régimen de Transparencia Fiscal al Consumidor (Ley 27.743)" + "IVA Contenido" (obligatoria en Factura B desde 2024, presente en las 6 facturas reales, no existía en el diseño anterior). Verificado generando un PDF real (ComprobanteAfip Id=298, Gasparín) y comparándolo visualmente contra el original — 1 bug encontrado y corregido en el propio proceso: el CUIT del emisor se imprimía con guiones (mal, copiado por error de otro campo) en vez de sin guiones como muestra la factura real.
- Datos de "Domicilio" del cliente (no del emisor) NO se agregaron — el sistema no captura ese dato hoy y no fue parte del pedido explícito (que hablaba de los datos del emisor: razón social/domicilio/CUIT/condición IVA propios). Si se necesita a futuro, es una ampliación de alcance nueva (nuevo campo en `ComprobanteAfip` + UI de carga).
- Motivo: Pedido explícito del cliente, con los datos oficiales de ARCA como fuente de verdad.
- Impacto en capas: Application (`AfipSettings.cs`), Infrastructure (`ComprobanteAfipService.GenerarPdfAsync`), configuración (`appsettings.json`, `appsettings.Production.json`). Sin migración EF (settings + PDF, ningún cambio de esquema).
- Riesgos/supuestos: Sin smoke test por navegador (regla de proceso vigente) — verificado generando el PDF real y visualizándolo directamente. No deployado a producción todavía en este ciclo.
- 2026-08-19 — CR-42: el cliente está cargando ventas reales de la semana anterior que ya facturó por fuera del sistema (directo desde la página oficial de AFIP, con CAE real). 2 necesidades: (1) que la Venta quede con la fecha real en que ocurrió, no la fecha de carga; (2) cómo cargarlas sin duplicar la factura ante AFIP (el botón "Facturar" de `Ventas/Details` siempre solicita un CAE nuevo — usarlo para estas ventas emitiría una segunda factura real). **Decisión confirmada con el cliente**: dado que son pocas ventas puntuales (no un flujo que se vaya a repetir seguido) y el cliente tiene el CAE real a mano, no se construye una pantalla nueva — se registra directo en la base con un script de una sola vez, mismo patrón ya usado por `tools/ImportarHistorico/Program.cs` (CR-13): crea el `ComprobanteAfip` con `Estado=Emitido` y los datos reales (Tipo, PuntoVenta, NumeroComprobante, CAE, VencimientoCAE, Fecha) sin llamar al webservice de AFIP, y marca `VentaItem.CantidadFacturada = Cantidad`. La Venta en sí se carga por la pantalla normal (`Ventas/Create`, ahora con fecha elegible, ver más abajo) — el Administrador NO debe pasar por "Facturar" para estas ventas puntuales, evitando la re-emisión.
- 2026-08-19 — CR-42 (fecha de la venta editable): agregado `VentaInput.Fecha` (nullable, solo día) a `Ventas/Create.cshtml` — Administrador-only (mismo criterio que el resto de los overrides financieros/de fecha sensibles de la pantalla, para que un Vendedor no pueda alterar en qué día impacta una venta en Caja/reportes sin supervisión), nunca futura. Sin fecha explícita, cae al comportamiento histórico (hoy). Mismo patrón ya usado por `PagoVentaInput.Fecha` (CR-29): se combina el día elegido con la hora actual de Argentina y se convierte a UTC real vía `HorarioArgentino.ConvertirAUtc`. La fecha elegida se propaga de forma consistente a `Venta.Fecha`, `PagoVenta.Fecha` (de los pagos cargados junto con la venta), el movimiento de stock (`IStockService.RegistrarMovimientoAsync` gana parámetro opcional `fecha`) y el ingreso en Caja (`ICCLocalService.RegistrarMovimientoAsync`, que ya tenía el parámetro desde CR-29) — para que una venta backdateada no quede con fecha de hoy en unos lugares y la fecha real en otros. Sin migración EF (no hay columna nueva, solo deja de hardcodear `DateTime.UtcNow`).
- 2026-08-16 — CR-41: pedido explícito del cliente, ítems de Venta con 100% de descuento (ej. bonificación/regalo) deben poder cargarse y confirmarse igual. El guard server-side de `VentaService.ConfirmarAsync`/`EditarAsync` (Administrador-only) exigía `Subtotal > 0` sin excepción, bloqueando con "Precio o subtotal inválido" justo el caso de un ítem 100% bonificado (Subtotal calculado en $0 por diseño, `Cantidad × PrecioActivo × (1-100/100)`). Corregido a `Subtotal >= 0` (solo se bloquea negativo) — `PrecioUnitario` sigue exigiendo ser mayor a cero sin excepción (el precio base del producto nunca es $0, lo que puede llegar a 0 es el resultado después del descuento). El campo `% Descuento` ya admitía 100 en el cliente (`max="100"`) desde CR-40, así que no hizo falta cambio de UI — solo el guard del servidor. Sin migración EF (cambio de validación, sin cambio de esquema).
- 2026-08-15: Bug reportado por el cliente tras la auditoría — "al crear la venta con los pagos configurados, estos se guardan en un solo pago". Causa raíz real encontrada (no el sospechoso inicial de los botones "Todo efectivo/transferencia", descartado por el cliente): `jquery.maskMoney.js` intercepta cada tecla con `preventDefault()` y escribe el valor a mano, sin disparar nunca el evento `input` nativo del browser — el único evento que dispara es `change`, y solo al perder el foco. Los handlers de Precio contado/tarjeta, Subtotal, Monto de pago y Total editable en `Ventas/Create.cshtml` y `Ventas/Edit.cshtml` escuchaban únicamente `'input'`, así que el array JS que arma el payload de guardado quedaba "congelado" en el valor inicial de cada campo mientras el usuario tipeaba, aunque la pantalla mostrara el número correcto — si el usuario clickeaba "Confirmar"/"Agregar" sin que el campo llegara a perder el foco antes, se enviaba el valor viejo (o vacío) en vez del tipeado. Corregido escuchando también `'change'` en los 6 campos afectados, más una relectura defensiva de todos los campos `.money` justo antes de armar el payload final (por si algún campo no llega a hacer blur). Documentado también como estándar genérico del estudio en `23-web.instructions.md` para cualquier proyecto que reutilice este plugin vendored.
- 2026-08-15: Auditoría completa de los 18 módulos de Etapa 1 (código vs. documentación), pedida por el cliente. Corregidos: precarga de precio equivocada en Facturación AFIP (usaba precio Negro aun en líneas "Con IVA"); bug de terceros en `jquery.maskMoney.js` que pisaba montos de pago ya cargados; botón "Todo transferencia" de Ventas sin contemplar el tope "Con IVA" de CR-40 (ahora fuerza esa opción de precio en todas las líneas antes de armar el pago); falta de traza en el ledger de stock del script de reconciliación del 14/08 (ahora genera `MovimientoStock` tipo Ajuste); `ProductoService.UpdateAsync` sin capturar conflicto de concurrencia con Aumento masivo; fila de la tabla resumen de módulos que prometía envío WhatsApp desde Presupuesto (en realidad es de Venta, CR-4); fila de criterios de aceptación de Sprint 4 desactualizada respecto de CR-7 (acreditación de cheques). También, con confirmación explícita del cliente: unificado el Proveedor duplicado "CARDOZO, JUAN CRUZ" (Id=15 sobrevive, Id=22 se soft-deletea) pendiente desde la auditoría de CR-27 — verificado primero que ambos registros son byte-idénticos en todos los campos fiscales (mismo CUIT 20-38325877-5, mismo domicilio fiscal completo, mismo criterio de verificación que CR-17) y que Id=22 no tiene ninguna OrdenCompra ni MovimientoCCProveedor asociado (0/0), por lo que no hizo falta reasignar FKs como en CR-17, solo el soft-delete. **Aplicado en `marihogar_dev`, pendiente replicar en producción en el próximo despliegue** (no se toca producción sin autorización explícita separada). Hallazgo pendiente de confirmación del cliente, no auto-corregido: certificado AFIP de producción real ya cargado (28/07/2026) contradice la documentación vigente en varios documentos del agente, que sigue describiendo el certificado como pendiente. Detalle completo en el reporte de auditoría entregado al cliente.
- 2026-08-15: Discovery + Análisis v14 — CR-40, regla de negocio permanente pedida explícitamente por el cliente para quedar documentada (no solo implementada): modelo de precios en negro (solo efectivo sin factura) vs. con IVA/21% (efectivo con factura, transferencia, MercadoPago, Banco Carrefour, o tarjeta — decidido con el cliente que estos 3 métodos van siempre "con IVA"); % descuento/recargo configurable por Producto (precarga el default editable por línea que ya existía desde CR-38); pantalla admin nueva de % interés por cantidad de cuotas (3/6/9/12); y la matemática correcta de porcentajes invertibles (`PorcentajeHelper`, dividir para revertir un recargo, nunca restar el mismo %) aplicada retroactivamente y documentada también como estándar de código del estudio. **Mismo día, revisión de consistencia pedida por el cliente** ("revisar la lógica de ventas y pagos en base a las últimas definiciones"): encontrado y cerrado un hueco real (CA-CR40.3) — la regla "tarjeta siempre con IVA" no tenía candado server-side desde que CR-38 sacó el recargo automático del pago, se agregó la validación que lo garantiza de verdad.
- 2026-08-11: Discovery + Análisis v13 — CR-32 (precio contado/tarjeta visible para ambos roles + recargo real del 21% aplicado al monto cubierto por cada línea de pago, no por ítem fijo — mecánica fijada con un ejemplo numérico real del cliente), CR-33 (edición completa de Venta ya creada, bloqueada únicamente si ya tiene un Comprobante AFIP con CAE real emitido) y CR-34 (acreditación diferida de pagos con tarjeta — fecha efectiva + Estado Pendiente/Acreditado, el ingreso en CC Local se difiere hasta acreditar, a diferencia del precedente de Cheque que postea inmediato). 4 decisiones de diseño confirmadas con el cliente vía `AskUserQuestion` antes de diseñar. Los 3 comparten cambios de modelo en `PagoVenta` (`MontoBase`, `EstadoAcreditacion`, `FechaAcreditacionEfectiva`) — 1 migración EF combinada.
- 2026-07-30: Discovery + Análisis v12 — CR-27, disparado por un archivo nuevo del cliente (ledger real de Cuenta Corriente de Proveedores). 3 hallazgos: (1) el Total de las 239 OC históricas no incluía impuestos (subvaluado ~$19,4M); (2) CR-19 había marcado todo como pagado de forma ficticia, el archivo nuevo trae el pago real de 333 movimientos; (3) Mercado Pago se usa realmente para pagar a proveedores (excluido hasta ahora por decisión de diseño de CR-3). 2 decisiones confirmadas con el cliente (corregir el Total con impuestos reales; habilitar Mercado Pago también hacia adelante). Corrección del histórico (hallazgos 1/2, mismo criterio que CR-23 — dato ya migrado incorrecto) + 2 capacidades nuevas menores (Mercado Pago para OC, NotaInterna en OrdenCompra).
- 2026-07-30: Discovery + Análisis v11 — CR-25 (comprobante AFIP totalmente editable, venta como referencia no como fuente de verdad — 2 decisiones de diseño confirmadas con el cliente) y CR-26 (rediseño visual de remito/factura PDF + hallazgo de cumplimiento no solicitado: falta el código QR obligatorio de AFIP desde 2019, se suma al mismo alcance). Sin gate de presupuesto nuevo.
- 2026-07-30: Discovery + Análisis v10 — CR-24, 4 sub-ítems sobre Ventas ya en producción: (1) bug real del toggle de IVA que descartaba precios editados a mano; (2) layout de 4 elementos en la columna de precio; (3) Total editable con reparto proporcional (confirmado con el cliente); (4) nueva capacidad de registrar pagos sobre una Venta ya creada, mirror exacto de Compras — incluye redirect a Details tras crear. Sin gate de presupuesto nuevo, corrección + extensión de bajo-medio esfuerzo sobre CR-22 ya aprobado.
- 2026-07-29: Discovery + Análisis v9 — CR-23, corrección exhaustiva de Ventas históricas tras reporte del cliente de que el precio y la forma de pago migrados no coincidían con la realidad. 3 hallazgos: (1) el monto usado no incluía IVA (Precio Unitario es neto, Total Venta = neto×1,21); (2) el campo Descuento ya queda absorbido al usar Total Venta directo, sin necesitar modelarlo aparte; (3) la forma de pago real está en Nota Interna en 68% de las ventas, parseable con un catálogo de patrones (eft/mpo/visa/master/naranja/transf carre/debito), incluyendo 8 ventas con múltiples formas de pago y 2 con saldo pendiente real. Sin gate de presupuesto nuevo — corrección de un dato ya migrado, mismo criterio que MH-006/MH-007.
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
