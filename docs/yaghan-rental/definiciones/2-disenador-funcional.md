# Memoria - Diseñador funcional

## Proyecto: yaghan-rental
## Ultima actualizacion: 2026-08-12

---

## 0. Resultado del escaneo de reutilización

Escaneados `docs/*/definiciones/{2-disenador-funcional,5-implementador}.md` de todo el historial. Coincidencias tomadas como base:

| Flujo/pantalla de Yaghan | Proyecto de referencia | Qué se reutiliza |
|---|---|---|
| Caja diaria (apertura/cierre, ingresos/egresos) | `la-platense` (`5-implementador.md`, cierre Entrega 2 ola 2) | `CajaMovimiento` (Fecha/Tipo/Monto/OrigenTipo/OrigenId/Descripcion) + `CierreCajaDiario` (TotalIngresos/TotalEgresos/Saldo/CerradoPorUsuarioId/FechaCierre, índice único en Fecha). Se adapta `OrigenTipo` a `"Venta"\|"Alquiler"\|"Compra"\|"Ajuste"`. |
| Checklist diario / bandeja de pendientes al iniciar sesión | `ganaderia` (`2-disenador-funcional.md` §1.7 "Novedades") | Patrón "bandeja al iniciar sesión" + job diario idempotente (`AcreditacionCuotasHostedService`) que arma un resumen consolidado por día. Se adapta a un job que arma el checklist (pagos pendientes, ingresos pendientes, alquileres por vencer, devoluciones a procesar) en vez de acreditaciones. |
| Envío/recepción de WhatsApp (infra) | `crm-olvidata` (`3-arquitecto-mvc.md` §1) | `IWhatsAppClient`/`WhatsAppClient` (HttpClient a Meta Cloud API), webhook `/webhook/whatsapp`, deduplicación por `message_id` (HashSet en memoria, limitación conocida y aceptada). **No se reutiliza** `BotFlowService` (máquina de estados de bot automático) porque acá la respuesta es manual del usuario, no un flujo conversacional automatizado — solo se reutiliza la capa de transporte (mandar/recibir mensajes), no la lógica de negocio del bot. |
| Comisión por referido, QR de devolución, tarifas por rango de días, talleres | — | Sin precedente en el estudio. Se diseñan desde cero en este documento (quedan como nueva referencia para futuros proyectos de alquiler/turismo). |

## 1. Alcance funcional resumido

12 pantallas/flujos: Dashboard con checklist diario, Bandeja de WhatsApp, Cotización, Reserva (con generación de QR), Listado de reservas, Devolución (escaneo QR + búsqueda manual), Catálogo de artículos (con tarifas por rango de días), Referentes, Proveedores + Compras, Talleres, Caja diaria, Venta directa. Rol único: Administrador.

## 2. Flujo de pantallas y wireframe textual

### 2.1 `Dashboard/Index` (pantalla de inicio)
```
┌─ Yaghan Rental ──────────────────────────────┐
│ [Checklist de hoy]                            │
│  ☐ 3 pagos pendientes de cliente              │
│  ☐ 2 ingresos pendientes (venta/alquiler)     │
│  ☐ 4 alquileres vencen hoy                    │
│  ☐ 1 devolución atrasada                      │
│ [Vencimientos] Próximos (7d) | Hoy | Semana   │
│ [Accesos rápidos] Nueva reserva | WhatsApp | Devolución │
└────────────────────────────────────────────────┘
```
Se arma con un job diario (mismo patrón idempotente de `ganaderia`) que consolida al Administrador iniciar sesión, más un refresco manual.

### 2.2 `Whatsapp/Index` (bandeja) → `Whatsapp/Conversacion/{id}`
```
┌─ Conversaciones ──────────┬─ Detalle ──────────────┐
│ ● Juan Pérez  "¿tienen..." │ Juan Pérez  +54911...  │
│   Ana Gómez   "gracias!"   │ [historial de mensajes]│
│   ...                      │ [Cotizar] [Nueva reserva]│
│                            │ [caja de texto] [Enviar]│
└────────────────────────────┴─────────────────────────┘
```
Desde el detalle de una conversación, dos accesos directos: "Cotizar" (abre 2.3 con el contacto precargado) y "Nueva reserva" (abre 2.4).

### 2.3 `Cotizacion/Create`
Selección de artículos (buscador por categoría/talla), cantidad de días por ítem (calcula tarifa según `TarifaPorDias` del artículo), total. Botón "Enviar por WhatsApp" arma el mensaje con el detalle y lo manda por `IWhatsAppClient` a la conversación de origen (si vino de 2.2) o a un teléfono ingresado a mano.

### 2.4 `Reserva/Create` (desde cotización aceptada o directo)
Campos: Nombre, Apellido, DNI, Teléfono, Mail, ítems (heredados de la cotización o elegidos ahora), FechaRetiro, FechaDevolución, Referente (opcional, autocompleta % vigente), Pago (monto, método), ComprobantePago (upload imagen). Al confirmar: valida no-solapamiento de fechas por artículo/talla, genera QR único de la reserva, cambia artículos a `Reservado`, dispara WhatsApp de confirmación con el QR adjunto.

### 2.4b `Reserva/Retirar/{id}` (nueva — agregada 2026-08-12, garantía con tarjeta)
```
┌─ Retiro de equipo — Juan Pérez ──────┐
│ Ítems a retirar: 2                    │
│ Garantía: $XXX.XXX (monto fijo config)│
│ [Autorizar con tarjeta] → widget Mercado Pago (Bricks, tokenizado) │
│  — o si no tiene tarjeta compatible — │
│ [Registrar depósito alternativo] → monto + medio (efectivo/transferencia) │
│ [Confirmar retiro]                    │
└─────────────────────────────────────────┘
```
Pantalla obligatoria antes de pasar la reserva a `En curso`: sin garantía autorizada (hold) o depósito alternativo registrado, no se habilita "Confirmar retiro". El widget de Mercado Pago corre embebido (iframe/SDK tokenizado) — el sistema nunca ve el número de tarjeta, solo recibe el token para crear el Advanced Payment (`capture:false`).

### 2.5 `Reserva/Index`
Grilla con filtros por estado (Cotizado, Reservado, En curso, Devuelto OK, Devuelto con daño, Atrasado — este último calculado, no filtrable como estado propio en la tabla) y por fecha de retiro/devolución.

### 2.6 `Devolucion/Procesar` (mobile-first)
```
┌─ Procesar devolución ────────────┐
│ [📷 Escanear QR]                 │
│ — o —                            │
│ [Buscar por nombre / DNI]        │
│ [Listado de alquileres de hoy]   │
├───────────────────────────────────┤
│ Reserva: Juan Pérez — 2 ítems     │
│  ☑ Campera Antártica  [OK|Dañada] │
│  ☑ Pantalón térmico   [OK|Dañada] │
│ [Confirmar devolución]            │
└────────────────────────────────────┘
```
Cámara vía `getUserMedia` del navegador (sin app nativa) + librería JS de lectura de QR. Ítems marcados "Dañada" no vuelven a `Disponible`, quedan en `Dañado` a la espera de alta de `OrdenTaller` (2.10). Al confirmar con todos los ítems OK: dispara WhatsApp de reseña **y libera automáticamente el 100% de la garantía** (hold de Mercado Pago o marca el depósito alternativo como "a devolver"). Si hay ítems dañados, el sistema pide el monto a capturar (tope: el monto autorizado) antes de confirmar — la captura puede ser parcial (ej. costo real de reparación vía `OrdenTaller`) o total.

### 2.7 `Articulo/Index,Create,Edit`
ABM: Categoría, Talla/Variante, Tipo (Venta/Alquiler/Ambos), Stock, Estado físico (Disponible/Dañado/En taller), y grilla de `TarifaPorDias` (rango de días → precio o %).

### 2.8 `Referente/Index,Create,Edit`
ABM simple: Nombre, Tipo (Agencia/Hotel/Guía/Otro), % comisión (default 20% al crear), Teléfono/Mail de contacto.

### 2.9 `Proveedor/Index,Create,Edit` + `Compra/Index,Create`
ABM de proveedores + alta de compra (proveedor, artículos/insumos, monto, fecha) con impacto en stock del artículo comprado.

### 2.10 `OrdenTaller/Index,Create`
Alta: artículo dañado, taller, costo estimado, fecha estimada de retorno. Estados: Enviado → En reparación → Vuelto (al marcar "Vuelto", el artículo pasa a `Disponible`).

### 2.11 `Caja/Index` (cierre diario)
Grilla de `CajaMovimiento` del día (ventas, alquileres, compras, ajustes) + botón "Cerrar caja del día" que crea `CierreCajaDiario` (bloqueado a uno por fecha). Ajustes manuales requieren descripción obligatoria.

### 2.12 `Venta/Create`
Venta directa de artículos (tipo Venta/Ambos), sin reserva ni devolución. Referente opcional con cálculo de comisión.

## 3. ViewModels propuestos

**`ReservaCreateViewModel`**: `Nombre`, `Apellido`, `DNI` (requerido, formato numérico), `Telefono` (requerido), `Email` (formato válido, opcional), `Items[]` (ArticuloId, Talla, CantidadDias), `FechaRetiro` (requerida, ≥ hoy), `FechaDevolucion` (requerida, > FechaRetiro), `ReferenteId` (opcional), `MontoPago`, `MetodoPago` (enum), `ComprobantePago` (IFormFile, requerido antes de confirmar).

**`CotizacionCreateViewModel`**: `ContactoWhatsAppId` (opcional), `TelefonoDestino`, `Items[]` (ArticuloId, Talla, CantidadDias, PrecioCalculado readonly), `Total` (readonly, calculado server-side a partir de `TarifaPorDias`).

**`DevolucionViewModel`**: `ReservaId` (por QR o por selección manual), `Items[]` (ArticuloReservaId, EstadoDevolucion: OK/Dañado).

**`ArticuloEditViewModel`**: `Nombre`, `CategoriaId`, `Talla`, `Tipo` (Venta/Alquiler/Ambos), `Stock`, `TarifasPorDias[]` (RangoDiasDesde, RangoDiasHasta, Precio).

**`ReferenteEditViewModel`**: `Nombre`, `Tipo`, `PorcentajeComision` (0–100, default 20), `Telefono`, `Email`.

**`OrdenTallerCreateViewModel`**: `ArticuloId`, `Taller`, `CostoEstimado`, `FechaEstimadaRetorno`.

**`CajaCierreViewModel`**: `Fecha` (readonly, hoy), `TotalIngresos`/`TotalEgresos`/`Saldo` (readonly, calculados), `Movimientos[]` (readonly).

**`RetiroGarantiaViewModel`** (agregado 2026-08-12): `ReservaId`, `MontoGarantia` (readonly, parámetro fijo del sistema), `TokenTarjetaMercadoPago` (recibido del widget embebido, nunca un número de tarjeta crudo), `DepositoAlternativo` (opcional: `Monto`, `Medio` enum Efectivo/Transferencia — solo si no hay tarjeta compatible).

**`CapturaGarantiaViewModel`** (agregado 2026-08-12): `ReservaId`, `MontoACapturar` (requerido si hay ítems dañados, validado ≤ `MontoGarantia` autorizado), `Motivo`.

## 4. Máquina de estados

### 4.1 Reserva/Alquiler

| Estado origen | Evento | Estado destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| — | Crear cotización | Cotizado | — | Envía WhatsApp con la cotización | — |
| Cotizado | Confirmar reserva | Reservado | comprobante de pago cargado + sin solapamiento de fechas por artículo/talla | Genera QR único, marca artículos `Reservado`, envía WhatsApp de confirmación con QR | 409 si el artículo/talla ya está comprometido en ese rango de fechas |
| Reservado | Retirar en el local | En curso | fecha de hoy ≥ FechaRetiro | Marca artículos `Alquilado` | — |
| En curso | Procesar devolución (todos OK) | Devuelto OK | — | Libera stock (`Disponible`), envía WhatsApp de reseña | — |
| En curso | Procesar devolución (con daño) | Devuelto con daño | al menos un ítem marcado Dañado | Ítems OK → `Disponible`; ítems dañados → `Dañado` (esperan `OrdenTaller`) | — |
| En curso | *(derivado, no transición manual)* | Atrasado | `FechaDevolucion < hoy` y sigue En curso | Job diario dispara WhatsApp de aviso de atraso (una sola vez) | — |
| Atrasado | Procesar devolución | Devuelto OK / Devuelto con daño | igual que arriba | igual que arriba | — |

### 4.2 Artículo

`Disponible → Reservado → Alquilado → Devuelto OK → Disponible` (ciclo normal) · `Alquilado → Dañado → (vía OrdenTaller) En taller → Disponible` (ciclo con daño).

### 4.3 OrdenTaller

`Enviado → En reparación → Vuelto` (al llegar a Vuelto, dispara el retorno del artículo a `Disponible`).

### 4.4 GarantiaTarjeta (agregado 2026-08-12)

| Estado origen | Evento | Estado destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| — | Autorizar en el retiro | Autorizada | token de tarjeta válido (Visa/Master/Cabal/Amex) | Crea Advanced Payment `capture:false` en Mercado Pago, guarda `MercadoPagoPaymentId` y `FechaLimiteCaptura` (+7 días) | Rechazo del banco emisor → no habilita "Confirmar retiro" |
| — | Registrar depósito alternativo | Autorizada (vía depósito) | sin tarjeta compatible | Registra monto/medio manualmente, sin llamada a Mercado Pago | — |
| Autorizada | Devolución sin daño | Liberada | — | Libera el 100% del hold (o marca depósito "a devolver") | — |
| Autorizada | Devolución con daño | Capturada | monto a capturar ≤ monto autorizado | Captura el monto indicado en Mercado Pago (o descuenta del depósito alternativo) | 422 si el monto excede lo autorizado |
| Autorizada | *(derivado)* faltan ≤ 2 días para `FechaLimiteCaptura` y la reserva sigue En curso | — (alerta, no transición) | — | El checklist diario (2.1) avisa "garantía por vencer, re-autorizar" | — |
| Autorizada | Re-autorizar (alquiler largo) | Autorizada (nueva) | antes de `FechaLimiteCaptura` | Crea un nuevo Advanced Payment, libera el anterior | — |
| Autorizada | *(derivado, sin re-autorizar a tiempo)* | Vencida | `hoy > FechaLimiteCaptura` sin acción | Queda sin cobertura de garantía — alerta al Administrador | — |

## 5. Reglas de negocio y permisos por pantalla

Rol único **Administrador** con acceso a las 12 pantallas — sin restricciones de autorización por pantalla en Etapa 1 (confirmado en Análisis §0.7.7).

- No se puede confirmar una `Reserva` sin comprobante de pago cargado.
- No se puede reservar un artículo/talla con fechas superpuestas a otra reserva `Reservado`/`En curso` del mismo artículo/talla.
- La comisión de un `Referente` se calcula y persiste al cerrar la Venta/Reserva asociada, con el % vigente de ese referente en ese momento (no recalcula retroactivo si el % cambia después).
- `CierreCajaDiario` es único por fecha — no se puede cerrar dos veces el mismo día.
- El aviso de atraso por WhatsApp se dispara una única vez por reserva (flag `AvisoAtrasoEnviado`).
- El mensaje de reseña se dispara una única vez por reserva, solo en la transición a `Devuelto OK`.

## 6. Impacto funcional por capa

- **Presentación**: 12 grupos de pantallas MVC, subida de archivos (comprobante de pago), acceso a cámara del navegador (lectura QR), envío/recepción embebido de WhatsApp en la bandeja.
- **Negocio**: cálculo de tarifa por rango de días, validación de no-solapamiento de fechas, máquina de estados de Reserva/Artículo/OrdenTaller, cálculo de comisión por referente, job diario de checklist + aviso de atraso, generación de QR, envío de plantillas WhatsApp (confirmación/reseña/atraso).
- **Datos**: entidades nuevas — `Articulo`, `CategoriaArticulo`, `TarifaPorDias`, `Reserva`, `ItemReserva`, `Referente`, `Proveedor`, `Compra`, `OrdenTaller`, `CajaMovimiento`, `CierreCajaDiario`, `ConversacionWhatsApp`, `MensajeWhatsApp`, `Venta`, `ItemVenta`.

## 7. Riesgos y supuestos

- Ver R1–R4 y S1–S2 de `1-analista-funcional.md` (número de WhatsApp/coexistencia, ausencia de política de seña publicada, deduplicación heredada, acceso a cámara del navegador, single-sucursal, moneda ARS única).
- **Nuevo (Diseño)**: la lectura de QR por navegador (sin app nativa) requiere HTTPS y permisos de cámara otorgados por el usuario del celular — a validar en el dispositivo real del local durante Implementación/QA.
- **Nuevo (Diseño)**: `CajaMovimiento` se genera por cada pago de `Reserva`/`Venta` (no consolidado), siguiendo el mismo patrón de La Platense — el Administrador ve el desglose por medio de pago, no un único movimiento por operación.

## 8. Plan funcional por etapas (para Arquitectura/Presupuesto)

**Etapa 1 (MVP — mínimo para operar el negocio):** Catálogo de artículos con tarifas por rango de días, Cotización manual, Reserva con QR y comprobante de pago, Listado de reservas, Devolución (QR + búsqueda manual) con reseña/atraso automáticos por WhatsApp, Bandeja de WhatsApp (envío/recepción manual), Checklist diario / vencimientos, Comisión por referente, Caja diaria, Venta directa.

**Etapa 2 (fuera del MVP, mencionado explícitamente por el cliente como mejora futura):** sugerencia automática de combos en la cotización, integración de cobro con Mercado Pago.

**CRM de WhatsApp (2.2, CU-01/08/09):** se implementa en Etapa 1 igual que el resto, con todas sus funciones (bandeja, envío/recepción, avisos automáticos de reseña/atraso), dentro del precio único de USD 850 (ver `1-analista-funcional.md` §0.9 y `4-presupuestador.md`). Compras a proveedores y Talleres quedan en el núcleo comprometido (confirmado con Joaquín 2026-08-12).

## Historias de usuario

1. Como Administrador, quiero ver una bandeja con todas las conversaciones de WhatsApp entrantes para poder responder consultas sin salir del sistema. *Criterio:* toda consulta nueva aparece en la bandeja sin refrescar manualmente; puedo responder y el mensaje sale por el número del negocio.
2. Como Administrador, quiero armar una cotización eligiendo artículos y cantidad de días para poder mandarle el precio al cliente por WhatsApp. *Criterio:* el total se calcula según la tarifa por rango de días configurada; el botón "Enviar" manda el detalle al teléfono correcto.
3. Como Administrador, quiero crear una reserva con los datos del cliente y el comprobante de pago para formalizar el alquiler. *Criterio:* no puedo confirmar sin DNI, teléfono, fechas válidas y comprobante cargado; se genera un QR único al confirmar.
4. Como Administrador, quiero que el sistema me impida reservar un artículo/talla ya comprometido en esas fechas para evitar dobles reservas. *Criterio:* al intentar solapar fechas del mismo artículo/talla, el sistema rechaza con un mensaje claro.
5. Como Administrador, quiero procesar una devolución escaneando el QR desde mi celular para agilizar la entrega en el local. *Criterio:* al escanear un QR válido, veo la reserva y puedo confirmar la devolución en un paso.
6. Como Administrador, quiero poder buscar la reserva manualmente si el cliente no tiene el QR a mano para no bloquear la devolución. *Criterio:* puedo buscar por nombre, DNI o ver el listado de alquileres del día y elegir la reserva correcta.
7. Como Administrador, quiero marcar un ítem devuelto como dañado para que no vuelva a stock disponible hasta pasar por taller. *Criterio:* un ítem "Dañado" queda en estado `Dañado`, no aparece disponible para nuevas reservas.
8. Como cliente, quiero recibir un mensaje de WhatsApp pidiéndome una reseña cuando devuelvo todo en buen estado, para poder dejar mi opinión fácilmente. *Criterio:* el mensaje se dispara una sola vez, solo cuando el estado pasa a Devuelto OK.
9. Como cliente, quiero recibir un aviso de WhatsApp si me atraso con la devolución, para acordarme de devolver el equipo. *Criterio:* el aviso se manda una sola vez, el primer día que el sistema detecta el vencimiento sin devolución.
10. Como Administrador, quiero ver un checklist al iniciar el día con pagos pendientes, ingresos pendientes y alquileres por vencer, para saber qué hacer hoy sin revisar todo el sistema. *Criterio:* el checklist se arma automáticamente y se puede marcar cada ítem como resuelto.
11. Como Administrador, quiero ver los vencimientos próximos, de hoy y de la semana en un panel, para anticiparme a las devoluciones. *Criterio:* el panel separa claramente las tres categorías y se actualiza según la fecha del sistema.
12. Como Administrador, quiero configurar el % de comisión de cada referente, para que se calcule automáticamente en cada venta/alquiler asociado. *Criterio:* el % configurado en el referente es el que se usa al momento de cerrar la operación, no un valor fijo global.
13. Como Administrador, quiero registrar la caja diaria del local con ingresos y egresos, para cerrar el balance del día. *Criterio:* no puedo cerrar la caja dos veces el mismo día; el saldo se calcula automáticamente.
14. Como Administrador, quiero enviar un artículo dañado a un taller registrando costo y fecha estimada de retorno, para hacer seguimiento de la reparación. *Criterio:* el artículo queda bloqueado de stock disponible hasta que la orden de taller se marca "Vuelto".
15. Como Administrador, quiero registrar compras a proveedores de insumos/artículos, para mantener el stock actualizado. *Criterio:* al confirmar una compra, el stock del artículo comprado se actualiza.
16. Como Administrador, quiero configurar tarifas distintas según la cantidad de días de alquiler (1/3/7 días), para aplicar las promociones del negocio sin depender de que alguien programe un cambio. *Criterio:* puedo editar los rangos y precios desde el ABM de artículos sin tocar código.
17. Como Administrador, quiero autorizar una garantía con la tarjeta del cliente al momento del retiro, para cubrirme ante un robo o rotura sin cobrarle nada por adelantado. *Criterio:* no puedo confirmar el retiro sin una garantía autorizada o un depósito alternativo registrado; el hold no debita fondos hasta que yo decida capturarlo.
18. Como Administrador, quiero que la garantía se libere sola cuando el cliente devuelve todo en buen estado, para no tener que hacer ese trámite manualmente. *Criterio:* al confirmar una devolución sin daños, el sistema libera el 100% del hold sin intervención mía.
19. Como Administrador, quiero capturar un monto de la garantía cuando hay un artículo dañado o faltante, para cubrir el costo real sin superar lo que autoricé. *Criterio:* el sistema no me deja ingresar un monto mayor al autorizado.

## Nota de reutilización agregada (2026-08-12, garantía con tarjeta)

Sin precedente en el estudio — se investigó especialmente (ver `1-analista-funcional.md` §0.8) antes de diseñar. Mercado Pago Advanced Payments (`capture:false`) resolvió ser la vía técnica correcta; no hubo diseño equivalente que reutilizar de otro proyecto.

## Historial de ajustes
- 2026-08-12: primera versión del diseño funcional, a partir del análisis aprobado con las 9 decisiones confirmadas. Reutilización identificada de La Platense (caja diaria), Ganadería (checklist/job diario) y crm-olvidata (infraestructura de envío/recepción de WhatsApp).
