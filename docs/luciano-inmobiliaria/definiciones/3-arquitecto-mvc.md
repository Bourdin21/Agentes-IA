# Memoria - Arquitecto MVC

## Proyecto: luciano-inmobiliaria
## Ultima actualizacion: 2026-08-14

---

## 0. Resultado del escaneo de reutilización

| Componente | Origen | Tratamiento |
|---|---|---|
| `AfipService`/`AfipTokenCache` (WSAA/WSFEv1) | `marihogar`→`delicias-naturales`→`la-platense` (código real leído) | Se porta la lógica SOAP tal cual. Pasa de leer `IOptions<AfipSettings>` (1 CUIT/certificado fijo) a recibir el certificado descifrado + CUIT **por parámetro**. `AfipTokenCache` pasa a `ConcurrentDictionary<string cuit, TokenCacheEntry>` — **crítico de seguridad, ver R5**. A escala ~100 CUIT (confirmado 2026-08-14), este diccionario puede tener hasta 100 entradas vivas simultáneas — sin problema de por sí (es liviano), pero refuerza que el keying tiene que ser perfecto. |
| `WhatsAppCredentialCipherService` (cifrado por tenant) | `century-21` | Mismo patrón de cifrado en reposo, aplicado a `Certificado.ArchivoCifrado`/`PasswordCifrado`. |
| `Plan`/`Grupo`/`ITenantContext` | `century-21` | Base conceptual para `Suscripcion` como unidad de aislamiento (filtro por `SuscripcionId`). |
| Endpoint Minimal API fuera de MVC | `crm-olvidata` (webhook en `Program.cs`) | **Ahora es el patrón de TODO el proyecto**, no de 3 endpoints — confirmado 2026-08-14 que el desarrollo es exclusivamente Web API, sin Identity ni Razor. |
| Ingesta de archivos por FTP compartido, extracción de datos de PDF con IA (Claude), operación a escala ~100 CUIT | — | Sin precedente. Arquitectura nueva, detallada abajo. |

**Cambio estructural (2026-08-14, primera reunión real con el cliente)**: se elimina **toda** la superficie MVC/Identity de la v1 (panel self-service + backoffice) — el proyecto es una Web API pura. ASP.NET Core Identity **no se usa en absoluto** (no hay login de ningún tipo) — toda autenticación es por API key (dos tipos, ver §3).

## 1. Alcance funcional resumido

Web API pura ASP.NET Core (.NET 10) — **sin MVC, sin Identity, sin vistas**. Minimal API endpoints en 3 áreas (Comprobantes, Administración, Contratos) + un `HostedService` de ingesta de certificados por FTP. EF Core 10 + MySQL. Dimensionada para ~100 CUIT con múltiples puntos de venta cada uno (confirmado por el cliente, cambia el orden de magnitud respecto de la v1).

## 2. Impacto técnico por capa

### Domain

Sin cambios de forma respecto de la v1 salvo lo señalado:
- `Suscripcion`, `Cuit`, `PuntoVenta` (con `TerminosEsperadosFacturacion`/`HorarioComercialDesde`/`Hasta` de la ampliación 2026-08-13), `Certificado`, `Comprobante` (con `IpOrigen`/`Concepto`), `Lote` — mismos campos que v1.
- `ApiKey` — **campo nuevo**: `Tipo` (enum `TipoApiKey{PuntoVenta,Administrativa}`) — antes solo existía para puntos de venta; ahora también cubre la credencial que usa Joaquín para `/api/v1/admin/*`, misma tabla, mismo mecanismo de cifrado.
- **`ApplicationUser` se elimina de este proyecto** — no hay Identity, no hay login, no hay usuarios en el sentido tradicional del portfolio. La v1 lo extendía con `SuscripcionId`; ya no aplica.

### Application

Sin cambios de forma respecto de la v1: `IAfipMultiTenantService`, `ICertificadoCipherService`, `IComprobanteService`, `IControlUsoService`, `ISenalesAntirreventaService`, `IApiKeyService` — mismas firmas. **Se agrega**:
- `ICertificadoIngestaService`: `ProcesarCarpetaAsync()` — escanea la carpeta FTP compartida, matchea archivos a CUIT (convención a definir con el cliente, ver Diseño §2.3), valida y persiste.
- `IContratoExtraccionService`: `ExtraerAsync(Stream pdf)` — arma la consulta a la API de Claude con el PDF adjunto, parsea la respuesta a `ContratoExtraidoDto`.

### Infrastructure

- `Services/AfipMultiTenantService.cs`, `Services/CertificadoCipherService.cs` — sin cambios respecto de v1.
- `Authentication/ApiKeyAuthenticationHandler.cs`: ahora resuelve **dos variantes** según `ApiKey.Tipo` — de punto de venta (scope: solo ese punto de venta) o administrativa (scope: todos los endpoints `/api/v1/admin/*`). Un mismo mecanismo, dos niveles de alcance.
- `HostedServices/CertificadoFtpIngestaHostedService.cs` (nuevo, reemplaza la idea de "subida desde panel" de la v1): corre periódicamente (propuesto cada 15 min, configurable), usa un cliente FTP (`FluentFTP` o similar, paquete NuGet nuevo) para listar/descargar archivos de la carpeta compartida, delega en `ICertificadoIngestaService`.
- `HostedServices/CertificadoVencimientoHostedService.cs`, `HostedServices/ControlUsoHostedService.cs` — sin cambios respecto de v1.
- `Services/ContratoExtraccionService.cs` (nuevo): cliente HTTP a la API de Claude (Anthropic), envía el PDF como documento adjunto en el mensaje, prompt fijo pidiendo JSON estructurado, parsea la respuesta. Requiere `IOptions<AnthropicSettings>` (ApiKey propia de Olvidata para este uso, distinta de las credenciales de ARCA).
- `AppDbContext`: 7 `DbSet` (sin `ApplicationUser`, ya no hereda de `IdentityDbContext` — es un `DbContext` estándar, primera vez en el portfolio que un proyecto no usa Identity). Índices sin cambios respecto de v1.
- **Paquete NuGet nuevo**: cliente FTP (ej. `FluentFTP`) para la ingesta de certificados.

### Web

- **Todo el proyecto es Minimal API** (`Program.cs`), sin `Controllers/`, sin `Views/`:
  - `POST /api/v1/comprobantes`, `POST /api/v1/comprobantes/lote` — **asíncronos (2026-08-14)**, responden 202 y encolan el procesamiento; `GET /api/v1/comprobantes/{id}` (y `/lote/{loteId}`) para consultar resultado — esquema `ApiKey` (tipo `PuntoVenta`).
  - `POST /api/v1/admin/clientes`, `POST /api/v1/admin/clientes/{id}/cuits`, `POST /api/v1/admin/cuits/{id}/puntos-venta`, `GET /api/v1/admin/control-de-uso`, `GET /api/v1/admin/control-de-uso/{puntoVentaId}` — esquema `ApiKey` (tipo `Administrativa`).
  - `POST /api/v1/contratos/extraer` — mismo esquema `ApiKey` de punto de venta (o uno propio, a definir si esta rama se cobra/audita distinto, ver Presupuesto).
- `Program.cs`: **un solo esquema de autenticación** (`ApiKey` custom, con las dos variantes de §3) — no hay `CookieAuthenticationDefaults`, no hay `AddIdentity`.

## 3. Modelo de permisos

| Actor | Mecanismo | Alcance |
|---|---|---|
| SaaS del cliente (por punto de venta) | `X-Api-Key` tipo `PuntoVenta` | Solo ese punto de venta — no ve otros, ni del mismo CUIT. |
| Joaquín (administración) | `X-Api-Key` tipo `Administrativa` | Acceso a `/api/v1/admin/*` — alta de clientes/CUIT/puntos de venta, control de uso. No hay usuario/contraseña, es una clave de servicio. |

## 4. Migraciones EF requeridas

**Sí** — proyecto nuevo. Migración inicial con las 7 tablas. **Sin tablas de Identity** (`AspNetUsers`, `AspNetRoles`, etc. no se generan — primer proyecto del portfolio sin Identity).

## 5. Riesgos y supuestos

- **R5 (crítico, seguridad, sin cambios)**: aislamiento de tokens WSAA por CUIT — caso de prueba obligatorio.
- **R6 — sin efecto (2026-08-14)**: individual y lote pasaron a asíncrono, ya no hay tope de tamaño de lote ni riesgo de timeout HTTP. **Reemplazado por**: necesidad de una cola de procesamiento en background (Hangfire u otro mecanismo) que procese los `Comprobante`/`Lote` en estado `Pendiente`, y de definir con el cliente si el resultado se consulta por polling o webhook.
- **R7 (sin cambios)**: custodia de certificados de terceros, respaldo legal recomendado.
- **R8 (2026-08-14, parcialmente resuelto)**: convención de nombre del certificado confirmada por el cliente — **nombre del archivo = número de CUIT** (ej. `30123456789.p12`). Sigue pendiente la contraseña del `.p12` (propuesta: archivo hermano `{cuit}.txt` en la misma carpeta, a confirmar) — no bloquea el resto del diseño, solo el detalle final de `CertificadoFtpIngestaHostedService`.
- **R11 (nuevo, 2026-08-14, research de facturación de honorarios)**: cuando la inmobiliaria factura alquileres "por cuenta y orden de terceros" (del propietario, obligación real desde RG AFIP 4004-E), el comprobante debe identificar al propietario como beneficiario — no es simplemente el inquilino como receptor. **No confirmado todavía el campo exacto de WSFEv1 para este caso** (el `AfipService.cs` ya portado en el estudio no cubre este escenario, solo ventas directas a un receptor) — antes de implementar el módulo 2 (API de emisión) hay que revisar el manual completo de WSFEv1 para el mecanismo de "facturación por cuenta y orden de terceros" (posible campo adicional en el request, o un tipo de comprobante distinto). Se agrega como tarea de investigación técnica previa a la implementación, no bloquea Diseño/Presupuesto pero sí el inicio de código del módulo 2.
- **R9 (nuevo, 2026-08-14, escala)**: a ~100 CUIT con múltiples puntos de venta cada uno, el volumen de filas en `PuntoVenta`/`Certificado`/`ApiKey` es notoriamente mayor al de cualquier proyecto multi-tenant previo del estudio (`century-21` fue diseñado para un número mucho menor de "Grupos"). No hay un problema de performance conocido a este volumen (sigue siendo chico para MySQL), pero **si el mantenimiento anual se cobrara por cantidad de tablas** (como el resto del portfolio) el criterio no aplicaría bien acá — el driver de costo real es cantidad de CUIT, no cantidad de tablas, confirma que el modelo de suscripción por packs (ya elegido) es el criterio correcto, no un error.
- **R10 (nuevo, 2026-08-14)**: costo variable de la rama de extracción de contratos — cada llamada a la API de Claude tiene costo de tokens, a diferencia del resto del sistema (costo fijo). Si esta rama se implementa, hay que decidir si se cobra por PDF procesado o se incluye en el pack — no resuelto, ver `4-presupuestador.md`.
- Hereda R1-R4, S1 de `1-analista-funcional.md`.

## 6. Gate de aprobación para pasar a Presupuesto

Dos puntos a resolver con Joaquín antes de cerrar el WBS (no son ajustes menores):
1. **Escala real (~100 CUIT) rompe la tabla de packs** definida en el presupuesto anterior (llegaba hasta "16+ CUIT, a cotizar caso por caso") — hay que definir el criterio de precio para este volumen antes de recalcular `4-presupuestador.md`.
2. **Alcance de la rama de extracción de contratos por PDF+IA**: el cliente preguntó viabilidad, no confirmó que lo quiere ya — presupuestar como ítem aparte/opcional, no mezclarlo en el núcleo.

## Historial de ajustes
- 2026-08-13: primera versión de la arquitectura técnica. 7 entidades nuevas, arquitectura híbrida (API pública + panel self-service + backoffice), extensión multi-tenant del motor AFIP con foco en el riesgo de aislamiento de tokens (R5).
- 2026-08-13 (ampliación, señales técnicas): agregados `Comprobante.IpOrigen`/`Comprobante.Concepto` y `PuntoVenta.TerminosEsperadosFacturacion`/horario. Nuevo `ISenalesAntirreventaService`.
- 2026-08-14 (rediseño mayor, primera reunión real): eliminada toda la superficie MVC/Identity (panel + backoffice) — proyecto 100% Web API con dos tipos de API key (punto de venta / administrativa), sin `AspNetUsers`. Agregada ingesta de certificados por FTP (`CertificadoFtpIngestaHostedService`, con dependencia bloqueante de convención de carpetas a acordar con el cliente) y la rama de extracción de contratos por PDF con IA (Claude). Documentado el quiebre de escala a ~100 CUIT (R9) y el costo variable de la nueva rama de IA (R10) como puntos a resolver antes de presupuestar.
- 2026-08-14 (research honorarios/certificado): R8 parcialmente resuelto (nombre del certificado = CUIT). Agregado R11: facturación "por cuenta y orden de terceros" (obligatoria para alquileres administrados) requiere identificar al propietario como beneficiario en el comprobante — campo exacto de WSFEv1 pendiente de confirmar contra el manual completo antes de codear el módulo de emisión.