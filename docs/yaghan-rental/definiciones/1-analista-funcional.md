# Memoria - Analista funcional

## Proyecto: yaghan-rental
## Ultima actualizacion: 2026-08-12

---

## 0. Salida mínima del agente (contrato `analista-funcional.agent.md`)

### 0.1 Alcance funcional resumido

Sistema de gestión integral para **Yaghan Rental** (Ushuaia) — agencia de alquiler y venta de indumentaria de nieve/térmica. Cubre: CRM de WhatsApp para atención de consultas entrantes con respuesta manual del usuario, cotización y reserva de artículos, control de vencimientos (próximos/hoy/semana), checklist operativo diario, comisiones por referido, compras a proveedores y talleres de reparación, caja diaria, y devoluciones por escaneo de QR con avisos automáticos por WhatsApp (reseña al completar, atraso si corresponde).

**Catálogo relevado de la web del cliente** (`https://yaghanrental.com.ar/tienda/`):
- Camperas (11 productos, alquiler diario y línea "antártica")
- Botas (10 productos: térmicas, antárticas, pre-ski)
- Pantalones térmicos (6 productos)
- Accesorios: antiparras ($9.000), anteojos deportivos ($25.000), guantes térmicos ($25.000), crampones/bastones ($15.000), botellas térmicas ($10.000)
- Equipos completos / bundles (campera + pantalón + botas + guantes): $28.900–$95.000
- Alquiler diario: $9.000–$15.000 por prenda; **alquiler x 3 días con descuento** ya visible en la web
- Venta directa de accesorios (no todo el catálogo es alquiler)
- Contacto: WhatsApp +5492901652524, mail yaghan.rental@gmail.com, Instagram @yaghan.rental, local en Gdor. Paz 892, Ushuaia
- Medios de pago: transferencia, MercadoPago, Prex, tarjetas (Visa/Master/Cabal/Naranja/Amex)
- La web **no publica** política de depósito/seña ni proceso formal de reserva → confirmado como vacío de información (ver §0.7).

### 0.2 Casos de uso principales

| # | Caso de uso | Actor | Resumen |
|---|---|---|---|
| CU-01 | Recibir y responder consultas de WhatsApp | Usuario | Bandeja de conversaciones entrantes del WhatsApp del negocio; el usuario responde desde el sistema (no bot automático). |
| CU-02 | Armar cotización | Usuario | A partir de la consulta, arma una cotización con artículos del catálogo, cantidad de días y precio resultante; la envía al cliente por WhatsApp. |
| CU-03 | Crear reserva | Usuario | Convierte una cotización aceptada (o carga directa) en reserva: nombre, apellido, DNI, teléfono, mail, fecha de retiro, fecha de devolución, pago, comprobante de pago. Genera QR único de la reserva. |
| CU-04 | Gestionar catálogo de artículos | Usuario/Admin | ABM de artículos: categoría, talla/variante, tipo (venta/alquiler/ambos), stock, tarifa por día/rango de días, estado físico (bueno/dañado/en taller). |
| CU-05 | Ver vencimientos | Usuario | Panel con alquileres por vencer: próximos, de hoy, de la semana. |
| CU-06 | Checklist diario | Usuario | Lista de tareas del día: pagos pendientes de clientes, ingresos pendientes por venta/alquiler, alquileres por vencer hoy, devoluciones a procesar. |
| CU-07 | Procesar devolución por QR | Usuario | Pantalla dedicada: escanea el QR del alquiler desde el celular, el sistema identifica la reserva y procesa la devolución (libera stock, cambia estado). |
| CU-08 | Enviar reseña automática | Sistema | Al pasar el alquiler a "Devuelto OK", dispara WhatsApp automático pidiendo reseña. |
| CU-09 | Avisar atraso automático | Sistema | Si a la fecha de hoy el alquiler sigue sin devolver y ya venció, dispara WhatsApp automático de aviso al cliente. |
| CU-10 | Registrar venta | Usuario | Venta directa de artículos del catálogo (sin devolución), con o sin comisión por referido. |
| CU-11 | Gestionar comisión por referido | Usuario/Admin | Alta de referentes (agencias, hoteles, guías), % de comisión por referente (default 20%), cálculo automático por venta/alquiler asociado a un referente. |
| CU-12 | Gestionar compras a proveedores | Usuario/Admin | ABM de proveedores, registro de compras de insumos/artículos, impacto en stock. |
| CU-13 | Gestionar talleres | Usuario/Admin | Envío de un artículo a taller de reparación, costo, tiempo estimado, retorno a stock disponible. |
| CU-14 | Caja diaria | Usuario | Apertura/cierre de caja del local, ingresos y egresos del día, balance. |
| CU-15 | Autorizar garantía con tarjeta | Usuario | Al retirar el equipo, autoriza una pre-autorización (hold) en la tarjeta del cliente por el monto de garantía, vía Mercado Pago, sin debitar fondos. |
| CU-16 | Liberar o capturar garantía | Usuario/Sistema | Al procesar la devolución: si todo vuelve OK, libera el hold automáticamente; si hay daño/falta un artículo, captura el monto (total o parcial, con tope el monto autorizado). |
| CU-17 | Registrar depósito alternativo | Usuario | Si el cliente no tiene tarjeta compatible con el hold (Visa/Master/Cabal/Amex), registra un depósito recibido por otro medio (efectivo/transferencia) como garantía. |

### 0.3 Criterios de aceptación verificables (por caso de uso, selección crítica)

- **CU-01**: toda consulta nueva de WhatsApp aparece en la bandeja del sistema sin refrescar manualmente; el usuario puede responder y el mensaje sale por el mismo número del negocio.
- **CU-03**: no se puede crear una reserva sin DNI, teléfono, fecha de retiro y fecha de devolución; la fecha de devolución no puede ser anterior a la de retiro. Al confirmar la reserva se genera un QR único vinculado a esa reserva (no al cliente ni al artículo).
- **CU-03 (disponibilidad)**: el sistema no permite reservar un artículo/talla que ya está comprometido (reservado o entregado) en un rango de fechas superpuesto — evita doble reserva del mismo ítem.
- **CU-07**: al escanear el QR correcto, el sistema muestra la reserva asociada y permite confirmar la devolución en un solo paso desde el celular; artículos con daño se marcan aparte y no vuelven a stock disponible hasta pasar por taller.
- **CU-08**: el mensaje de reseña se dispara una única vez por reserva, solo cuando el estado pasa a "Devuelto OK" (no se reenvía en reintentos).
- **CU-09**: el aviso de atraso se dispara la primera vez que el job diario detecta `FechaDevolucionPactada < hoy` y el estado sigue "En curso" — no se reenvía todos los días salvo que se defina lo contrario (ver pregunta abierta §0.7).
- **CU-11**: la comisión se calcula y queda registrada en el momento de cerrar la venta/alquiler asociado a un referente, usando el % vigente de ese referente (no un valor hardcodeado del 20% global).
- **CU-14**: la caja diaria no puede cerrarse dos veces el mismo día; el balance de cierre = ingresos − egresos del día, con posibilidad de ajuste manual justificado.
- **CU-15**: no se puede marcar una reserva como "Retirado/En curso" sin una garantía autorizada (hold de tarjeta) o un depósito alternativo registrado. El hold se crea recién al retiro (no al confirmar la reserva), para no arriesgar que venza antes de que el cliente pase a buscar el equipo.
- **CU-16**: al confirmar una devolución sin daños, el sistema libera el 100% del hold automáticamente, sin intervención manual. Si hay daño, el usuario ingresa el monto a capturar, que no puede superar el monto autorizado.
- **CU-16 (vencimiento)**: si el alquiler supera los 7 días entre retiro y devolución pactada, el sistema avisa con anticipación para re-autorizar la garantía antes de que el hold original venza (Mercado Pago limita la captura a 7 días desde la creación del hold).

### 0.4 Permisos, estados y validaciones identificados

**Actores:** por defecto se asume un único perfil "Usuario del local" con acceso completo (atención WhatsApp, reservas, caja, compras, talleres). Ver pregunta abierta §0.7 sobre si hace falta más de un rol.

**Máquina de estados — Reserva/Alquiler** (hipótesis a validar en Diseño):
`Cotizado → Reservado (seña/pago registrado) → Retirado/En curso → Devuelto OK | Devuelto con daño → (si daño) En taller → Disponible`
Estado lateral: `Atrasado` (se deriva de `En curso` + fecha vencida, no es una transición manual).

**Máquina de estados — Artículo:**
`Disponible → Reservado → Alquilado → Devuelto → Disponible` | `Dañado → En taller → Disponible`

**Validaciones críticas:**
- DNI y teléfono obligatorios en la reserva (WhatsApp de aviso/reseña depende del teléfono).
- No solapamiento de fechas para el mismo artículo/talla.
- Comprobante de pago: carga de archivo/imagen obligatoria antes de confirmar la reserva (a validar, ver §0.7).
- % de comisión por referido entre 0 y 100, editable por referente.

### 0.5 Riesgos y supuestos

- **R1**: el número de WhatsApp del negocio (+5492901652524) ya está en uso productivo en la app WhatsApp Business del teléfono — decisión confirmada en §0.7.2: se migra ese mismo número a la Business Platform/Cloud API. Por defecto un número opera en la app **o** en la API, no en ambas; la función de "coexistencia" de Meta podría evitar el corte, pero su elegibilidad no es garantizable desde el diseño y se verifica recién al iniciar la Implementación. Si no califica, Yaghan pierde la posibilidad de usar la app normal en ese número desde el día de la migración — riesgo operativo a comunicar al cliente antes de migrar en producción, externo al desarrollo. Se reutiliza la infraestructura ya probada de `crm-olvidata` (`WhatsAppClient`, webhook).
- **R2**: sin política de depósito/seña publicada, el flujo de pago de la reserva se define con el mínimo pedido (registrar pago y comprobante) sin lógica de seña parcial vs. pago total, salvo que el cliente confirme lo contrario.
- **R3**: la deduplicación de mensajes entrantes por reintentos de Meta hereda la limitación conocida de `crm-olvidata` (HashSet en memoria, no persistente) — aceptada como comportamiento estándar del estudio salvo pedido explícito de mejorarla.
- **R4**: el QR de devolución requiere acceso a cámara desde el navegador del celular (no app nativa) — a validar que el dispositivo/navegador del local lo soporte sin instalar nada adicional.
- **R7 (nuevo, garantía con tarjeta)**: el hold de Mercado Pago (Advanced Payments, `capture:false`) vence a los **7 días** de creado — si no se captura ni se libera antes, se cae solo. Se genera recién al retiro (no al confirmar la reserva) para minimizar el riesgo, pero un alquiler que dure más de 7 días entre retiro y devolución igual requiere re-autorizar la garantía a mitad de camino (confirmado con Joaquín 2026-08-12) — esto exige que el cliente vuelva a pasar la tarjeta, en persona o a distancia, algo que no siempre será posible operativamente.
- **R8 (nuevo, garantía con tarjeta)**: el hold solo funciona con tarjetas **Visa, Mastercard, Cabal y American Express** — no con débito ni otros medios. Para esos casos se registra un depósito alternativo por otro medio (confirmado con Joaquín), lo que agrega un flujo manual paralelo al automático.
- **R9 (nuevo, garantía con tarjeta)**: la tarjeta debe ingresarse siempre a través del formulario tokenizado de Mercado Pago (Checkout Bricks/Secure Fields embebido), nunca capturada ni almacenada por el sistema propio — evita que el sistema quede alcanzado por el nivel más exigente de cumplimiento PCI-DSS.
- **S1 (supuesto)**: un solo local físico (Gdor. Paz 892, Ushuaia) — no se contempla multi-sucursal salvo indicación contraria.
- **S2 (supuesto)**: la moneda de todo el sistema es ARS (pesos argentinos), sin conversión a USD (a diferencia de Koi/Ganadería).

### 0.6 Banderas tempranas

- **Requiere migración EF**: Sí — proyecto nuevo desde cero (entidades: Articulo, CategoriaArticulo, TarifaPorDias, Reserva/Alquiler, ItemReserva, Cliente, Referente, ComisionReferido, Proveedor, Compra, OrdenTaller, CajaDiaria, MovimientoCaja, ConversacionWhatsApp, MensajeWhatsApp, **GarantiaTarjeta**).
- **Integración externa**: Sí — (1) WhatsApp Business API (Meta), reutilizando `WhatsAppClient`/webhook de `crm-olvidata`. (2) **Mercado Pago — Advanced Payments API** (`capture:false`) para la garantía con tarjeta, confirmada en Etapa 1 (2026-08-12) — ver §0.8. Ya no es una integración opcional de Etapa 2: la garantía usa la misma pasarela que estaba prevista para el cobro online, adelantada a Etapa 1 solo para este uso (hold/captura/liberación), sin implicar todavía el cobro online completo de ítem 3 del análisis original (ese sigue en Etapa 2).
- **Máquina de estados**: Sí — Reserva/Alquiler, Artículo y **Garantía con tarjeta** (Autorizada → Liberada | Capturada | Vencida, ver §0.8).

### 0.8 Garantía con tarjeta de crédito (agregado 2026-08-12, pedido del cliente)

**Research realizado antes de diseñar** (no había precedente en el estudio): Mercado Pago soporta esto vía su Checkout API, **Advanced Payments** con `capture:false` — reserva el monto en la tarjeta sin debitarlo; luego se libera (0%) o se captura (parcial o total, hasta el monto reservado). Es el mismo mecanismo que usan las rentadoras de auto en Argentina para garantías de alquiler. Restricciones duras de la plataforma (no negociables desde el diseño):
- El hold vence a los **7 días** de creado si no se captura ni libera antes.
- Solo soporta tarjetas **Visa, Mastercard, Cabal y American Express**.
- La tarjeta debe ingresarse por el formulario tokenizado de Mercado Pago (Checkout Bricks/Secure Fields), nunca por un campo propio del sistema (evita alcance PCI-DSS pleno).

**Decisiones confirmadas con Joaquín (2026-08-12):**
1. El hold se genera **al retirar el equipo** (no al confirmar la reserva) — minimiza el riesgo de vencimiento por reservas hechas con anticipación.
2. Alquileres de **más de 7 días**: el sistema avisa para **re-autorizar** la garantía antes de que venza el hold original.
3. El monto de garantía es **fijo por reserva** (parámetro configurable a nivel sistema, no por artículo).
4. Si el cliente **no tiene tarjeta compatible**: se registra un **depósito alternativo** por otro medio (efectivo/transferencia) como flujo manual paralelo.

Impacto: nuevo CU-15/16/17 (§0.2), nuevos criterios de aceptación (§0.3), nueva máquina de estados `GarantiaTarjeta` (ver `2-disenador-funcional.md`), R7-R9 (§0.5).

### 0.9 CRM de WhatsApp — se implementa en Etapa 1, dentro del precio único (corregido 2026-08-13, decisión comercial de Joaquín)

El CRM de WhatsApp (CU-01, bandeja de conversaciones + envío/recepción, incluidos los avisos automáticos de reseña/atraso) **se implementa en Etapa 1**, junto con el resto del sistema — no hay ninguna diferencia funcional ni de alcance técnico respecto del diseño original. Tras dos idas y vueltas de facturación (primero "sale del build", después "factura aparte diferida"), Joaquín cerró en una **tercera versión, más simple**: un único precio final de USD 850 que cubre todo el sistema, CRM incluido, sin líneas de pago separadas ni cobro diferido — ver `4-presupuestador.md` para el detalle numérico.

### 0.7 Decisiones confirmadas (2026-08-12, Joaquín — gate de Análisis)

Reemplaza las hipótesis A/B planteadas en la primera versión de este documento. Cada punto indica alcance de Etapa 1 (MVP) y qué queda para Etapa 2 cuando aplica.

1. **Cotización**: armado **manual** por el usuario, eligiendo artículos y días desde el sistema. *Etapa 2 (opcional, no presupuestada en Etapa 1)*: sugerencia automática de combos a partir de palabras clave del chat.

2. **Número de WhatsApp**: se usa el número existente (**+5492901652524**), ya activo en WhatsApp Business App. **Riesgo técnico documentado** (ver R1 actualizado en §0.5): por defecto, un número de WhatsApp opera en la app de teléfono **o** en la Business Platform/Cloud API (que necesita el CRM), no en ambas a la vez — migrarlo corta el uso de la app normal en ese número salvo que califique para la función de "coexistencia" de Meta (sincroniza app + API), que tiene criterios de elegibilidad no garantizables desde el diseño. **Se verifica la elegibilidad de coexistencia en Meta Business Manager al inicio de la Implementación**, antes de migrar el número en producción; si no califica, Yaghan pasa a operar ese número exclusivamente desde el CRM (deja de poder contestar desde la app del teléfono).

3. **Registro de pago**: **manual** — el cliente paga por fuera del sistema (transferencia, Mercado Pago por link/QR propio, tarjeta en el local) y el usuario carga el comprobante (imagen) a mano. *Etapa 2 (opcional)*: integración de cobro con Mercado Pago (link de pago + confirmación automática por webhook).

4. **QR de devolución — ambos caminos**: el QR se envía al cliente por WhatsApp al confirmar la reserva (camino rápido de devolución), **y además** la pantalla de devolución permite buscar/seleccionar la reserva manualmente (por nombre, DNI o listado de alquileres del día) para el caso en que el cliente no tenga el QR a mano. No es "QR-only": el escaneo es el atajo, no el único camino.

5. **Comisión por referido**: cada referente (agencia, hotel, guía) tiene su **propio % configurable**, con 20% como valor por defecto al dar de alta uno nuevo — confirma la entidad `Referente` con % propio.

6. **Talleres**: seguimiento completo — taller, costo del arreglo, fecha estimada de retorno; el artículo queda bloqueado de stock disponible hasta que vuelve. Confirma la entidad `OrdenTaller` con estado propio.

7. **Usuarios del sistema**: **un solo perfil, Administrador**, con acceso completo a todas las pantallas (WhatsApp, reservas, caja, compras, comisiones, talleres). Sin ABM de roles en Etapa 1.

8. **Promoción por cantidad de días**: tarifas por **rangos fijos configurables** por artículo/categoría (ej.: 1 día = tarifa base, 3 días = precio o % propio, 7 días = precio o % propio) — confirma la entidad `TarifaPorDias`, editable por el usuario sin tocar código.

9. **Aviso de atraso**: se envía **una sola vez**, la primera vez que el job diario detecta el vencimiento sin devolución — no se reenvía en días sucesivos.

## Historial de ajustes
- 2026-08-12: creación del análisis funcional inicial (Discovery + Análisis en una sola etapa, según `analista-funcional.agent.md`). Incorporado el dato de "promociones de alquiler por cantidad de días" aportado por Joaquín durante la sesión (pregunta abierta §0.7-8).
- 2026-08-12 (post-presupuesto): agregada la garantía con tarjeta de crédito (pre-autorización), pedida por el cliente después del primer presupuesto. Research de viabilidad (Mercado Pago Advanced Payments) + 4 decisiones de diseño confirmadas con Joaquín — ver §0.8. Pasa a Etapa 1 por pedido explícito del cliente.
