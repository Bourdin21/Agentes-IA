# Memoria - Arquitecto MVC

## Proyecto: yaghan-rental
## Ultima actualizacion: 2026-08-12

---

## 0. Resultado del escaneo de reutilización

Escaneados `docs/*/definiciones/{3-arquitecto-mvc,5-implementador}.md` de todo el historial.

| Componente | Origen | Tratamiento |
|---|---|---|
| Baseline técnico (Identity, `SoftDestroyable`, `IRepository<T>`, health checks, Serilog, rate limiting, `.slnx`) | `blankproject` (`C:\Sistemas\blankproject`, template vigente del estudio, actualizado 2026-07-30 desde la base saneada de La Platense/ex-OlvidataCRM) | Se parte de este template sin modificarlo — es la base estándar de todo proyecto nuevo. |
| `WhatsAppClient` / `IWhatsAppClient` (HttpClient a Meta Cloud API), webhook `/webhook/whatsapp`, deduplicación por `message_id` (HashSet en memoria) | `crm-olvidata` (`C:\Sistemas\olvidatasoft-crm`, ver `3-arquitecto-mvc.md` §1) | Se porta **sin cambios de lógica de transporte**. Se **descarta** `BotFlowService` (máquina de estados de bot automático) — acá la conversación la lleva el Administrador manualmente, no un flujo conversacional. |
| `CajaMovimiento` / `CierreCajaDiario` (Fecha/Tipo/Monto/OrigenTipo/OrigenId, índice único en Fecha para el cierre) | `la-platense` (`C:\Sistemas\Ferreteria La Platense`, ver `5-implementador.md` cierre Entrega 2 ola 2) | Se porta la misma forma, `OrigenTipo` adaptado a `"Venta"\|"Alquiler"\|"Compra"\|"Ajuste"`. Un `CajaMovimiento` por pago (no consolidado por operación), mismo criterio que La Platense. |
| Patrón "bandeja al iniciar sesión" + job diario idempotente | `ganaderia` (`AcreditacionCuotasHostedService`, ver `3-arquitecto-mvc.md`) | Se adapta a `ChecklistDiarioHostedService`: corre una vez por día, arma el checklist (pagos pendientes, ingresos pendientes, alquileres por vencer) y dispara el aviso de atraso (una sola vez por reserva, con flag `AvisoAtrasoEnviado`, mismo patrón de idempotencia por flag que usa Ganadería para no reprocesar acreditaciones). |
| Patrón de índice único + captura de excepción de duplicado para evitar condiciones de carrera en alta concurrente | `crm-olvidata` (`Contacto.Telefono`) | Se aplica el mismo criterio a la validación de no-solapamiento de fechas por artículo/talla en `ReservaService.ConfirmarReservaAsync` — validación a nivel de Service antes del `INSERT`, con manejo de la excepción de conflicto si dos altas concurrentes colisionan (ventana de carrera aceptada como riesgo bajo, ver §5). |
| QR de reserva, comisión por referido, tarifas por rango de días, órdenes de taller | — | Sin precedente en el estudio. Arquitectura nueva (ver §2). Queda como referencia para futuros proyectos de alquiler/turismo. |
| **Garantía con tarjeta de crédito (pre-autorización)** — agregado 2026-08-12 | — | Sin precedente en el estudio. Research específico confirmó **Mercado Pago Advanced Payments** (`capture:false`) como vía técnica — ver `1-analista-funcional.md` §0.8. Arquitectura nueva (ver §2.d). Queda como primera referencia del estudio para integraciones de hold/captura de pago. |

## 1. Alcance funcional resumido

Proyecto nuevo desde cero sobre el template `blankproject` (.NET 10, Clean Architecture 4 capas, EF Core 10, MySQL, Identity). 14 entidades nuevas de dominio, reutilización de infraestructura de WhatsApp (`crm-olvidata`) y caja diaria (`la-platense`), rol único Administrador.

## 2. Impacto técnico por capa

### Domain (`YaghanRental.Domain`)

**Entidades nuevas** (todas heredan `SoftDestroyable` salvo indicación contraria):
- `CategoriaArticulo` (Nombre)
- `Articulo` (Nombre, CategoriaArticuloId FK, Talla, Tipo: enum `TipoArticulo{Venta,Alquiler,Ambos}`, Stock, EstadoFisico: enum `EstadoFisicoArticulo{Disponible,Reservado,Alquilado,Dañado,EnTaller}`)
- `TarifaPorDias` (ArticuloId FK, RangoDiasDesde, RangoDiasHasta, Precio) — N:1 con Articulo
- `Cliente` (Nombre, Apellido, DNI, Telefono, Email) — compartido entre Reserva y Venta
- `Reserva` (ClienteId FK, ReferenteId FK nullable, FechaRetiro, FechaDevolucion, FechaDevolucionReal nullable, Estado: enum `EstadoReserva{Cotizado,Reservado,EnCurso,DevueltoOk,DevueltoConDaño}`, QrToken (string, índice único), MontoPago, MetodoPago: enum, ComprobantePagoPath, PorcentajeComisionAplicado nullable, MontoComision nullable, AvisoAtrasoEnviado bool default false). **Nota de diseño:** `Atrasado` **no** es un valor del enum — se deriva en runtime (`Estado == EnCurso && FechaDevolucion < hoy`), mismo criterio que Ganadería usa para estados calculados vs. persistidos.
- `ItemReserva` (ReservaId FK, ArticuloId FK, Talla, CantidadDias, PrecioAplicado — snapshot de la tarifa al momento de reservar, mismo patrón que `TasaImpuestoAplicada` de Ganadería —, EstadoItem: enum `EstadoItemReserva{Reservado,Alquilado,DevueltoOk,DevueltoDañado}`)
- `Referente` (Nombre, Tipo: enum `TipoReferente{Agencia,Hotel,Guia,Otro}`, PorcentajeComision default 20, Telefono, Email)
- `Proveedor` (Nombre, Telefono, Email)
- `Compra` (ProveedorId FK, Fecha, MontoTotal)
- `ItemCompra` (CompraId FK, ArticuloId FK, Cantidad, PrecioUnitario)
- `OrdenTaller` (ArticuloId FK, Taller, CostoEstimado, FechaEstimadaRetorno, Estado: enum `EstadoOrdenTaller{Enviado,EnReparacion,Vuelto}`)
- `CajaMovimiento` (Fecha, Tipo: enum `TipoMovimientoCaja{Ingreso,Egreso}`, Monto, OrigenTipo: enum `OrigenMovimientoCaja{Venta,Alquiler,Compra,Ajuste}`, OrigenId, Descripcion)
- `CierreCajaDiario` (Fecha — índice único, TotalIngresos, TotalEgresos, Saldo, CerradoPorUsuarioId, FechaCierre)
- `ConversacionWhatsApp` (Telefono — índice único, NombreContacto, UltimoMensajeFecha)
- `MensajeWhatsApp` (ConversacionId FK, Direccion: enum `DireccionMensaje{Entrante,Saliente}`, Texto, Fecha, MessageIdMeta — para deduplicación, mismo criterio que `crm-olvidata`)
- `Venta` (ClienteId FK, ReferenteId FK nullable, Fecha, MontoTotal, PorcentajeComisionAplicado nullable, MontoComision nullable)
- `ItemVenta` (VentaId FK, ArticuloId FK, Cantidad, PrecioUnitario)
- **`GarantiaTarjeta`** (agregado 2026-08-12) — ReservaId FK (único, 1:1 con Reserva), Estado: enum `EstadoGarantia{Autorizada,Liberada,Capturada,Vencida}`, MercadoPagoPaymentId (nullable si es depósito alternativo), MontoAutorizado, MontoCapturado nullable, FechaAutorizacion, FechaLimiteCaptura (= FechaAutorizacion + 7 días), EsDepositoAlternativo bool, MedioDeposito: enum nullable `MedioDeposito{Efectivo,Transferencia}` (solo si `EsDepositoAlternativo`), MotivoCaptura nullable.

### 2.d Garantía con tarjeta — detalle de integración (agregado 2026-08-12)

- **`IMercadoPagoGarantiaClient`** (`Application/Interfaces`): `AutorizarAsync(token, monto)` → crea Advanced Payment `capture:false`, devuelve `MercadoPagoPaymentId`; `CapturarAsync(paymentId, monto)`; `LiberarAsync(paymentId)` (cancela/anula el hold); implementado en `Infrastructure/Services/MercadoPagoGarantiaClient.cs` sobre `HttpClient` (misma convención `IOptions<MercadoPagoSettings>` que `WhatsAppSettings`).
- **`IGarantiaService`**: orquesta la máquina de estados de §4.4 del Diseño — `AutorizarAsync` (llamada desde `Reserva/Retirar`), `LiberarAsync`/`CapturarAsync` (llamadas desde `Devolucion/Procesar`), `RegistrarDepositoAlternativoAsync`.
- **Tokenización**: la vista `Reserva/Retirar.cshtml` embebe el SDK de Mercado Pago (Checkout Bricks/Secure Fields) — el `Controller` **nunca** recibe ni procesa un número de tarjeta crudo, solo el token que genera el SDK del lado del cliente. Esto mantiene el sistema fuera del alcance PCI-DSS de nivel completo (SAQ A en vez de SAQ D).
- **Job de alerta de vencimiento**: se extiende `ChecklistDiarioHostedService` (ya definido para el checklist general) para incluir "garantías por vencer en ≤ 2 días" como parte del `ChecklistDiarioDto` — reutiliza la misma corrida diaria, no un `HostedService` nuevo.
- **Settings nuevos**: `MercadoPagoSettings { AccessToken, PublicKey }` — sección `appsettings.json` `Olvidata_MercadoPago`, mismo patrón que `Olvidata_WhatsApp`.
- **Paquete NuGet**: ninguno del lado servidor (HttpClient + `System.Text.Json`). Del lado cliente, SDK JS oficial de Mercado Pago (`sdk.mercadopago.com`) vía script tag, sin build step adicional.

### Application (`YaghanRental.Application`)

Interfaces nuevas: `IArticuloService` (disponibilidad por rango de fechas, CRUD), `IReservaService` (`CrearCotizacionAsync`, `ConfirmarReservaAsync`, `ProcesarDevolucionAsync`), `IVentaService`, `ICajaService` (`RegistrarMovimientoAsync`, `CerrarDiaAsync`), `IChecklistDiarioService`, `IWhatsAppClient` (reutilizada de `crm-olvidata`, misma firma `SendTextAsync/SendTemplateAsync`), `IQrService` (`GenerarToken`, `ValidarToken`) — implementación simple con GUID/token firmado, sin librería externa de QR del lado del servidor (la generación visual del QR se resuelve en Web con una librería JS liviana, el server solo genera y valida el token).

DTOs: `DisponibilidadArticuloDto`, `ChecklistDiarioDto` (PagosPendientes, IngresosPendientes, AlquileresPorVencer, DevolucionesAtrasadas), `CotizacionDto`.

### Infrastructure (`YaghanRental.Infrastructure`)

- `AppDbContext`: 17 `DbSet` nuevos (ver §2 Domain). Índices únicos: `Reserva.QrToken`, `CierreCajaDiario.Fecha`, `ConversacionWhatsApp.Telefono`. FKs `OnDelete(Restrict)` en catálogos (Articulo, Referente, Proveedor no se borran físicamente), `OnDelete(Cascade)` en detalle (ItemReserva, ItemVenta, ItemCompra).
- `Services/WhatsAppClient.cs`: portado de `crm-olvidata` sin cambios de lógica.
- `HostedServices/ChecklistDiarioHostedService.cs`: `IHostedService`, corrida diaria (horario a definir con el cliente, sugerido temprano en la mañana ART), arma el `ChecklistDiarioDto` del día y dispara avisos de atraso pendientes (idempotente por `AvisoAtrasoEnviado`).
- `DependencyInjection.cs`: registra los services nuevos + `AddHttpClient<IWhatsAppClient, WhatsAppClient>()` + `AddHostedService<ChecklistDiarioHostedService>()`.
- **Paquetes NuGet nuevos**: ninguno para WhatsApp (HttpClient + `System.Text.Json`, ya en el framework). Para lectura de QR desde el navegador: librería **JS** (client-side, ej. `jsQR` o `html5-qrcode` vía CDN/vendor local, sin paquete NuGet — coherente con el patrón de "sin dependencias de servidor" del design system del estudio).

### Web (`YaghanRental.Web`)

- **Controllers nuevos**: `DashboardController`, `WhatsappController` (bandeja, `[Authorize(Policy="RequireAdministracion")]`), `CotizacionController`, `ReservaController`, `DevolucionController`, `ArticuloController`, `ReferenteController`, `ProveedorController`, `CompraController`, `OrdenTallerController`, `CajaController`, `VentaController`.
- **Endpoint webhook**: `/webhook/whatsapp` como Minimal API en `Program.cs` (no MVC controller), mismo patrón que `crm-olvidata`.
- **ViewModels**: ver `2-disenador-funcional.md` §3 (`ReservaCreateViewModel`, `CotizacionCreateViewModel`, `DevolucionViewModel`, `ArticuloEditViewModel`, `ReferenteEditViewModel`, `OrdenTallerCreateViewModel`, `CajaCierreViewModel`).
- **Vista de escaneo QR** (`Devolucion/Procesar.cshtml`): usa `getUserMedia` + librería JS de lectura de QR — requiere HTTPS incluso en desarrollo local (ver bug conocido del template sobre `HttpsPort=443`, aplicar el fix de bindeo dual de puertos desde el arranque).

## 3. Modelo de permisos

Rol único **Administrador** (confirmado en Análisis §0.7.7) — una sola policy `RequireAdministracion` aplicada a todos los controllers. Sin ABM de roles/usuarios adicional en Etapa 1. Si en el futuro el cliente pide un segundo rol (ej. "Atención" sin acceso a Caja/Compras), es una extensión aditiva de policies sin romper lo construido — mismo criterio que documentó La Platense para su propia extensión de roles.

## 4. Migraciones EF requeridas

**Sí** — proyecto nuevo desde cero. Una migración inicial (`InitialCreate`, ya la trae el template `blankproject`) + una migración de dominio (`YaghanRental_CatalogoReservasCajaWhatsapp` o dividida en 2-3 migraciones por bloque funcional si el volumen de cambios lo justifica en Implementación) que agrega las 17 tablas nuevas de §2.

## 5. Riesgos y supuestos

- Hereda R1–R4 y S1–S2 de `1-analista-funcional.md` (número de WhatsApp/coexistencia, sin política de seña publicada, deduplicación heredada no persistente, cámara del navegador, single-sucursal, moneda ARS).
- **R5 (nuevo, arquitectura)**: la validación de no-solapamiento de fechas por artículo/talla en `ReservaService.ConfirmarReservaAsync` corre a nivel de Service (SELECT + validación antes del INSERT), no como constraint de base de datos (MySQL no tiene un constraint nativo de rango de fechas sin overlap simple) — queda una ventana de carrera teórica si dos reservas del mismo artículo/talla se confirman en el mismo instante. Riesgo aceptado como bajo dado el volumen de un solo local con un usuario operando; si en producción se detectan colisiones reales, la mejora futura es un lock optimista o una validación transaccional con `SELECT ... FOR UPDATE` (no se implementa preventivamente, mismo criterio YAGNI que usa `crm-olvidata` para su propio riesgo de concurrencia documentado).
- **R6 (nuevo, arquitectura)**: la máquina de estados de `Reserva`/`ItemReserva` valida transiciones en el Service (no en la entidad) — mismo patrón que usa Ganadería para su matriz de transiciones cerrada; agregar un nuevo estado en el futuro requiere deploy de código, no es configurable desde la UI (sin pedido explícito de que lo sea).
- **S3 (supuesto)**: `IQrService` genera un token opaco (no información sensible embebida — no lleva DNI ni monto) para que el QR compartido por WhatsApp no exponga datos del cliente si el mensaje se reenvía.
- **R7-R9 (garantía con tarjeta, heredados de `1-analista-funcional.md` §0.8)**: hold vence a los 7 días (mitigado con re-autorización, requiere acción del cliente), solo tarjetas Visa/Master/Cabal/Amex (mitigado con depósito alternativo manual), tokenización obligatoria vía SDK de Mercado Pago (mitiga alcance PCI, no elimina la dependencia de que el SDK esté disponible/no falle — si el SDK de Mercado Pago no carga, la pantalla de retiro debe degradar al flujo de depósito alternativo, no bloquear el retiro por completo).

## 6b. CRM de WhatsApp — se implementa en este build, dentro del precio único (2026-08-13)

El módulo de WhatsApp (`WhatsAppClient`, webhook, `ConversacionWhatsApp`/`MensajeWhatsApp`, disparo de avisos automáticos) **se implementa en este build**, sin ningún recorte técnico respecto de la arquitectura original (§0 tabla de reutilización, arriba). `AppDbContext` incluye `DbSet<ConversacionWhatsApp>`/`DbSet<MensajeWhatsApp>` desde la migración inicial; el bootstrap incluye portar `WhatsAppClient` desde `crm-olvidata`; `IWhatsAppClient` se registra normalmente en `DependencyInjection.cs`; `CotizacionController` tiene el botón "Enviar por WhatsApp" y `ChecklistDiarioHostedService` dispara los avisos de reseña/atraso. No hay diferencia de facturación entre este módulo y el resto — todo queda dentro del precio único de USD 850 (ver `4-presupuestador.md`).

## 6. Gate de aprobación para pasar a Presupuesto

Arquitectura lista para presupuestar. Puntos que Joaquín debe confirmar antes de avanzar a Presupuesto (afectan el WBS):
1. ¿Compras a proveedores y Talleres van en **Etapa 1** o se confirman como **Etapa 2** (como quedó anotado en el plan funcional del Diseño)?
2. ¿El proyecto se crea copiando+saneando un repo reciente (como se hizo con La Platense desde `olvidatasoft-crm`) o se parte directo de `C:\Sistemas\blankproject`? Afecta el M de "deploy inicial"/bootstrap, no el resto del WBS.

## Historial de ajustes
- 2026-08-12: primera versión de la arquitectura técnica, sobre el diseño funcional aprobado. 17 entidades nuevas, reutilización confirmada de `crm-olvidata` (WhatsApp) y `la-platense` (caja diaria), rol único Administrador.
- 2026-08-12 (post-presupuesto): agregada `GarantiaTarjeta` (18va entidad) e integración `IMercadoPagoGarantiaClient`/`IGarantiaService` para la garantía con tarjeta pedida por el cliente. Sin cambio de modelo de permisos (sigue Administrador único). Migración EF ahora incluye la tabla `GarantiaTarjeta` y el enum `EstadoGarantia`.
