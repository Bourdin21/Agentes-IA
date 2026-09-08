# 3 - Arquitecto MVC — Proyecto KOI

> Memoria acumulativa del agente arquitecto.
> Etapa: Arquitectura. Estado: ✅ Etapa 1 cerrada. Módulo E2-02 (Fichador) arquitecturado en §8 — contrato real de API confirmado (§8.8), gate de Implementación habilitado (cliente entregó ApiKey/IdEmpresa + documentación). Sprint UX/UI Inversor + fixes arquitecturado en §9.
> Fecha: 2026-06-11. Última actualización: 2026-08-13 — §10 Mi Inversión: dividendos/recupero en pesos. Inputs: 1-analista-funcional.md §13 + 2-disenador-funcional.md §12.

## 1. Alcance resumido

Sistema nuevo sobre la base blankproject de OlvidataSoft: **ASP.NET Core MVC (.NET 10) + EF Core + MySQL 8**, tres capas (Domain / Application / Infrastructure / Web). Se reutiliza todo lo ya resuelto en la base: autenticación Identity, layout Olvidata, pipeline, DataTables/Select2/SweetAlert2, configuración y convenciones. **2 integraciones externas**: SMTP saliente (notificación de cierre) + API de cotización del dólar (ArgentinaDatos + DolarApi, mismo esquema que VirtualWallet). Sin servicios en background.

## 2. Impacto técnico por capa

### Domain (entidades nuevas)

| # | Entidad | Notas |
|---|---|---|
| 1 | `Inversor` | Nombre, capital aportado USD, usuario vinculado. |
| 2 | `PeriodoMensual` | Año, mes, estado (Abierto/**Cerrado** — Reabierto eliminado), TC del mes. |
| 3 | `VentaMensual` | Período, **VentasASalon, VentasBSalon, VentasADelivery, VentasBDelivery** (1:1 con período). Agregados (VentasA, VentasTotales, VentasSalon, VentasDelivery) calculados al vuelo, no persistidos. |
| 4 | `Rubro` | Catálogo (CMV, Fee Franquicia, Sueldos, Gastos Varios, Alquiler, Servicios, Impuestos, Previsión, Extras), orden, baja lógica. |
| 5 | `Subgrupo` | Rubro padre, nombre, tipo (manual / calculado por %), baja lógica. |
| 6 | `MovimientoGasto` | Período × subgrupo, importe (manual o calculado), snapshot del % aplicado. |
| 7 | `ParametroPorcentaje` | Concepto, %, base (VentasA / VentasTotales), vigencia desde. |
| 8 | `IndicadorVenta` | Período: **cantidad de comensales (manual)**, ticket promedio, ítems por ticket, cubierto promedio. |
| 9 | `PuntoInversion` | Número 1–100, valor de aporte, bonificado. |
| 10 | `AsignacionPunto` | Punto × inversor con vigencia (desde/hasta) — historial de cambios. |
| 11 | `Liquidacion` | Cabecera por período: utilidad por punto, TC, fecha generación. |
| 12 | `LiquidacionInversor` | Detalle: inversor, puntos, bruto, consumos, neto, USD, renta %, estado, fecha de pago. |
| 13 | `CamaraConfig` | URL web client Hik-Connect, cuenta de referencia, notas, activo. |
| 14 | `PreferenciaUsuario` | Tema dark/light por usuario. |
| 15 | `AuditoriaEvento` | Reaperturas de período/liquidación con motivo y usuario. |
| 16 | `NotificacionConfig` | Servidor SMTP, casilla emisora, nombre remitente, credencial (protegida). |
| 17 | `NotificacionEnvio` | Log por período × inversor: email, fecha/hora, estado (Enviado/Fallido), detalle de error. |
| 18 | `AjusteLiquidacion` | Motivo + monto ajustado + usuario cuando el Admin modifica el monto a repartir en preview (auditoría del ajuste manual). |

Más las tablas de Identity de la base (~6). **Total estimado del esquema entregado: ~24 tablas** → rango 16–30 (relevante para plan de mantenimiento PREMIUM).

### Application (servicios)

- `EstadoResultadosService`: carga/edición del período, cálculo de conceptos porcentuales según base configurada (comisiones/IIBB/débitos/tasa → VentasA; regalías/canon/previsiones → VentasTotales), totalizadores, rentabilidad, conversión USD. **Snapshot de % aplicado por movimiento**: los meses cerrados no se recalculan al cambiar parámetros.
- `CierrePeriodoService`: máquina de estados del período (**solo Abierto→Cerrado**; Reabierto eliminado). Al cerrar genera `Liquidacion` + `LiquidacionInversor` desde las asignaciones vigentes (Σ puntos ≤ 100); acepta consumos y ajuste de monto a repartir (con motivo) desde el preview. Tras confirmar el cierre dispara `NotificacionService` (post-commit: el envío nunca participa de la transacción del cierre). Re-apertura de liquidación **individual** conservada (Pagada→Pendiente, solo Admin, con motivo).
- `CotizacionService` (**nuevo, copiar de VirtualWallet**): `ICotizacionService` con `ObtenerCotizacionesPorCasaParaFecha`, `ObtenerPromedioBlue`, etc. Fuentes: DolarApi (hoy) + ArgentinaDatos (histórico). Cache 30 min (hoy) / 6 h (histórico). Registro en `IHttpClientFactory`.
- `NotificacionService`: arma el resumen del mes + liquidación personalizada por inversor, renderiza la plantilla HTML y despacha por SMTP; registra cada envío en `NotificacionEnvio`; reenvío manual individual; idempotencia por período (re-cierre no reenvía sin confirmación).
- `DashboardService`: agregaciones por mes/año/multi-año (ventas, gastos por rubro, resultado, rentabilidad, USD, indicadores) para los charts; tolerante a períodos sin datos.
- `InversionService`: puntos, asignaciones con vigencia, "Mi inversión" (dividendos, recupero, renta promedio) con aislamiento por inversor.
- `UsuarioService` (extiende base Identity): ABM inversores, blanqueo, vínculo usuario-inversor.
- `ImportacionInicialService`: carga inicial 2024–2026 (ver §5).

### Infrastructure

- DbContext + configuraciones EF de las 17 entidades, repositorios según convención de la base.
- Cliente SMTP (MailKit) detrás de una interfaz `IEmailSender` de Application; credencial protegida (user-secrets/appsettings cifrado según convención de la base). Envío síncrono acotado (≤15 destinatarios) con manejo de fallos por destinatario; sin colas ni BackgroundService.
- Hik-Connect se embebe del lado del navegador (iframe/link), no se consume API.

### Web

- Controllers: `Account` (base), `Dashboard`, `EstadoResultados`, `Configuracion` (rubros/parámetros/TC), `Indicadores`, `Puntos`, `Liquidaciones`, `RepartoGeneral`, `MiInversion`, `Camaras`, `Usuarios`, `Notificaciones` (config SMTP + historial de envíos + reenvío).
- Vistas según wireframes P-01…P-13; layout Olvidata + theme switcher dark/light (doble set de tokens CSS en `olvidata-theme` vía `[data-theme]`, persistido en `PreferenciaUsuario`).
- Una librería de charts JS para todo el sistema (Chart.js o equivalente ya usado en la base si existe).
- Export Excel de la vista anual (librería ya disponible en la base si existe; si no, ClosedXML).

## 3. Modelo de permisos

- Roles Identity: `Administrador`, `Inversor` (+ `SuperUsuario` interno del proveedor, fuera de la doc al cliente).
- Policies: `SoloAdministrador` (toda pantalla de carga/configuración/liquidación/usuarios), `ConsultaDashboard` (ambos roles), `MiInversion` (rol Inversor con filtro forzado por inversor vinculado al usuario; Admin accede a la vista de cualquier inversor desde Liquidaciones).
- Aislamiento de datos del inversor resuelto en Application (el servicio recibe el `InversorId` derivado del usuario autenticado, nunca de la request).

## 4. Migraciones EF

**Sí.** Una migración inicial con el esquema completo (~17 entidades nuevas + seed de catálogos: rubros/subgrupos del Excel, parámetros porcentuales iniciales, roles). Migraciones adicionales solo si la carga inicial revela ajustes de modelo (esperable: 1–2 menores).

## 5. Estrategia de carga inicial de históricos

- Importación única en implementación, vía `ImportacionInicialService` + planillas normalizadas (CSV/XLSX) derivadas de los dos Excel.
- Regla: se migran **valores**, no fórmulas (los meses históricos quedan cerrados con sus números tal cual el Excel, aunque sus bases de cálculo hayan sido inconsistentes).
- Validación de cierre: totales anuales 2024/2025 y acumulados por inversor contra los Excel fuente.

## 6. Riesgos y supuestos

- R-A1: iframe de Hik-Connect puede ser bloqueado por política del proveedor → la pantalla ya prevé fallback "abrir en pestaña nueva". Riesgo bajo, sin impacto de arquitectura.
- R-A2 ✅ CERRADO: los Excel históricos solo traen A/B sin apertura Salón/Delivery. Estrategia confirmada: `VentasADelivery = VentasBDelivery = 0`; `VentasASalon = VentasA`, `VentasBSalon = VentasB`. Cada período migrado recibe observación automática. Sin impacto en el modelo de entidades.
- R-A3: asignaciones de puntos con vigencia retroactiva (historial 2024–2026) deben reconstruirse al migrar → se valida contra hojas por inversor.
- S-A1: un solo entorno productivo, hosting del proveedor (plan de mantenimiento).
- S-A2: volumen bajo (12 períodos/año, 16 usuarios): sin requisitos especiales de performance ni caching.
- R-A4: entregabilidad del correo (spam/casilla emisora) depende del servicio SMTP que provea el cliente → se mitiga con correo de prueba en la configuración y log de envíos con reenvío manual; el envío nunca bloquea el cierre del período.

## 7. Gate de aprobación para presupuesto

- [x] Entidades y migración EF declaradas (24 tablas, incluye `AjusteLiquidacion` nuevo).
- [x] Permisos por rol y policies definidos.
- [x] Máquina de estados simplificada (solo Abierto→Cerrado para período; liquidación individual Pendiente↔Pagada).
- [x] Integraciones externas: SMTP saliente + **API dólar (ArgentinaDatos + DolarApi, sin colas)**. Ayres etapa 2 documentada.
- [x] `CotizacionService` copiado de VirtualWallet, misma interfaz, mismos endpoints, mismo cache.
- [x] Reutilización de la base blankproject confirmada.

**⚠️ Requiere recalculación de presupuesto** por adición de `CotizacionService`, 4 campos de ventas, dashboard mes abierto, `AjusteLiquidacion` y eliminación del Reabierto. Ver `4-presupuestador.md`.

---

## 8. Arquitectura — Módulo E2-02 "Fichador de empleados" (QuickPass)

### 8.0 Escaneo de reutilización cross-proyecto

Escaneados `docs/*/definiciones/{3-arquitecto-mvc,5-implementador}.md` de todos los proyectos — sin componente equivalente (ningún proyecto tiene hoy un `HttpClient` tipado contra un SaaS externo con Bearer token estático de solo lectura; lo más cercano es `CotizacionService` de VirtualWallet, pero ese usa APIs públicas sin autenticación). Se arquitectura desde cero, dejando el patrón documentado para reuso futuro (ver nota en 2-disenador-funcional.md §10.0).

### 8.1 Domain

Sin entidades nuevas — decisión de Análisis/Diseño (§11.4 del analista, §10.4 del diseñador): los datos de fichaje no se persisten localmente en esta etapa, QuickPass es la fuente de verdad.

### 8.2 Application

> **Actualizado 2026-08-10 — contrato real de la API confirmado** (documentación oficial QuickPass recibida del cliente: `InstructivoAPIEntidades-QuickPass.pdf` + `InstructivoAPIReportingQuickPass.pdf`, en `KoiDumplings/manual fichador/`). Difiere del supuesto original de §8.0-8.1 en dos puntos — **gatillo de reestimación evaluado: no aplica recargo**, el contrato real es más simple de integrar, no más complejo (ver §8.8).

- `IQuickPassService`:
  - `Task<IReadOnlyList<HoraTrabajadaDiaDto>> ObtenerHorasTrabajadasHoyAsync()` — mapea `GET /HorasTrabajadas` (API Reporting) acotado al día actual.
  - `Task<IReadOnlyList<ResumenHorasUsuarioDto>> ObtenerResumenPorRangoAsync(DateOnly desde, DateOnly hasta)` — mapea `GET /HorasTrabajadas/ResumenPorUsuario` (API Reporting). **La API ya devuelve el total de horas trabajadas, extras, tardanzas y ausencias consolidado — el sistema NO recalcula nada, solo proyecta la respuesta.**
  - `Task<IReadOnlyList<EmpleadoQuickPassDto>> ObtenerEmpleadosAsync()` — mapea `GET /Usuarios?excluirFotos=true` (API **Entidades**, distinta base URL — ver §8.3).
- DTOs nuevos en `Application/DTOs/QuickPassDtos.cs`: `HoraTrabajadaDiaDto` (turno, horas netas, horas extra, tardanzas, ausencia, detalle de fichadas del día), `ResumenHorasUsuarioDto` (totales del rango), `EmpleadoQuickPassDto` (nombre, legajo, sector, habilitado). El service mapea la respuesta cruda de QuickPass a estos DTOs — nunca se exponen los campos internos de QuickPass (`ParteParaReporteDTO` con sus ~40 campos, etc.) hacia el Controller/Vista.
- **Cambio respecto al diseño original:** ya no hace falta calcular "turno abierto"/"horas trabajadas" en el service — la API Reporting de QuickPass lo entrega calculado (`/HorasTrabajadas` y `/HorasTrabajadas/ResumenPorUsuario`). El service se simplifica a mapeo + manejo de errores, sin lógica de negocio propia de cálculo horario.

### 8.3 Infrastructure

- **Dos bases URL, dos HttpClient tipados** (la API real de QuickPass está dividida en dos servicios independientes, no relevado originalmente):
  - `QuickPassEntidadesClient` → `https://api.quickpassweb.com` (usado solo para `GET /Usuarios`, listado de empleados).
  - `QuickPassReportingClient` → `https://apireporting.quickpassweb.com` (usado para `/HorasTrabajadas` y `/HorasTrabajadas/ResumenPorUsuario`).
  - Ambos registrados vía `AddHttpClient<...>()` (`IHttpClientFactory`), consumidos desde una única implementación `QuickPassService : IQuickPassService` que inyecta los dos clientes.
- **Autenticación real (corrige el supuesto de Bearer token del relevamiento inicial):** dos headers estáticos en cada request — `ApiKey` e `IdEmpresa` — **sin login, sin token con expiración, sin refresh**. Más simple que lo arquitecturado originalmente. Se agregan como `DefaultRequestHeaders` al configurar cada `HttpClient` en `DependencyInjection.cs`.
- Configuración en `appsettings`: sección `QuickPass: { ApiKey, IdEmpresa, BaseUrlEntidades, BaseUrlReporting, TimeoutSeconds }`. Como la ApiKey de QuickPass no distingue entornos (a diferencia de la connection string de MySQL), va en `appsettings.json` (compartido dev/prod) siguiendo el mismo criterio ya usado en el proyecto para credenciales de servicio externo no versionadas por ambiente.
- **Formato de fechas — crítico, documentado explícitamente por QuickPass como la causa más frecuente de error de integración:**
  - API Entidades, query params: `yyyyMMdd` (sin hora).
  - API Reporting, todos los endpoints usados (`/HorasTrabajadas`, `/HorasTrabajadas/ResumenPorUsuario`): `yyyyMMddHHmm` (con hora).
  - **`/HorasTrabajadas` y `/HorasTrabajadas/ResumenPorUsuario` tienen límite duro de 31 días por consulta** (error 400 "No se pueden listar mas de 31 dias" si se excede) — la pantalla de Rango debe validar el spread de fechas del `daterangepicker` en el cliente y en el service antes de llamar a la API.
  - Encapsular el formateo de fechas en un helper único del service (`QuickPassDateFormatter` o método privado) para no repetir la lógica de formato en cada llamada — es el punto de mayor riesgo de bug de esta integración.
- Manejo de errores: timeout configurado (10s — SaaS externo), catch de `HttpRequestException`/`TaskCanceledException`/respuesta 401 (ApiKey/IdEmpresa inválidos) → excepción de dominio propia (`QuickPassIndisponibleException`) que el Controller traduce a mensaje SweetAlert2 (ver diseño §10.3). Logging estructurado con Serilog, **nunca loguear la ApiKey**.
- Sin reintentos automáticos ni Polly en esta primera versión (pantalla de consulta manual, no proceso crítico).

### 8.8 Evaluación del gatillo de reestimación (contrato real vs. relevado)

Diferencias encontradas al recibir la documentación real (2026-08-10) vs. lo asumido en la arquitectura original:

| Supuesto original | Contrato real | Impacto en esfuerzo |
|---|---|---|
| Autenticación Bearer token con posible expiración | Headers estáticos `ApiKey`/`IdEmpresa`, sin expiración ni refresh | 🟢 Menos esfuerzo — sin lógica de renovación de token |
| El service calcula "horas trabajadas" y "turno abierto" a partir de fichadas crudas | La API Reporting (`/HorasTrabajadas`, `/ResumenPorUsuario`) ya devuelve los totales calculados | 🟢 Menos esfuerzo — se elimina la lógica de cálculo horario del service, queda solo mapeo |
| Una sola API/base URL | Dos APIs con base URL distinta (Entidades + Reporting) | 🟡 Esfuerzo neutro — dos `HttpClient` en vez de uno, pero cada uno más simple |
| Formato de fecha único | 2 formatos distintos según API/endpoint (`yyyyMMdd` vs `yyyyMMddHHmm`), límite de 31 días en Reporting | 🟡 Esfuerzo neutro — un helper de formateo centralizado lo resuelve, riesgo de bug si no se encapsula |

**Decisión: no se reestima el presupuesto.** El balance neto es una integración más simple que la arquitecturada (menos lógica de negocio propia, autenticación más simple), compensado por dos clientes HTTP en vez de uno. Los USD 92 aprobados en `4-presupuestador.md` §16 se mantienen sin cambios. Se documenta el detalle real para que el implementador no repita el supuesto de Bearer token.

### 8.4 Web

- `FichadorController` nuevo, `[Authorize(Policy = "RequireAdministracion")]` (mismo criterio que Inversores/Configuración — dato de personal, no de inversión, pero el estudio ya usa esta policy para todo lo operativo del Admin).
- Acciones: `Index` (tab Hoy), `Rango` (GET con filtros, AJAX o submit estándar del proyecto), `Empleados`.
- Vista `Views/Fichador/Index.cshtml` con 3 tabs (Bootstrap nav-tabs), `daterangepicker` en el tab Rango, DataTables client-side en los 3 listados (volumen bajo — decenas de empleados, no requiere server-side).
- Link "Fichador" en sidebar (`Views/Shared/_Layout.cshtml`), sección "Gestión", visible solo para `Administrador`.

### 8.5 Migraciones EF

**No.** Sin entidades nuevas, sin cambios de esquema. No impacta el plan de mantenimiento vigente (el conteo de tablas del sistema no cambia).

### 8.6 Riesgos técnicos

- R-E2-02-T1: sin documentación formal de la API (Swagger no disponible según relevamiento) — el contrato exacto de los DTOs puede necesitar ajuste al integrar contra la API real. Mitigación: `QuickPassService` aislado detrás de la interfaz `IQuickPassService`, el resto del sistema no conoce el formato crudo de QuickPass.
- R-E2-02-T2 (bloqueante, no técnico): sin token de API ni credenciales admin del local — Implementación no puede arrancar ni siquiera para pruebas de integración hasta que el cliente los entregue (ver 1-analista-funcional.md §11.5).
- R-E2-02-T3: dependencia de un SaaS de terceros hosteado en AWS EE.UU. — si QuickPass tiene downtime, la pantalla queda no funcional pero no afecta el resto del sistema KOI (aislado en su propio Controller/Service, sin dependencias cruzadas).

### 8.7 Gate de aprobación para presupuesto

- [x] Sin entidades ni migración EF — confirmado por Análisis y Diseño.
- [x] Permisos definidos: solo Administrador (`RequireAdministracion`).
- [x] Integración externa definida: REST + Bearer token estático, `HttpClient` tipado vía `IHttpClientFactory`.
- [x] Escaneo de reutilización cross-proyecto: sin coincidencia, patrón nuevo documentado para reuso futuro.
- [x] Riesgo bloqueante para Implementación (no para Presupuesto) declarado explícitamente: token QuickPass pendiente.

---

## 9. Arquitectura — Sprint UX/UI Inversor + fixes (Agosto 2026)

### 9.0 Escaneo de reutilización cross-proyecto

Sin match — los 9 ítems son 100% reutilización interna de KOI (servicios/entidades ya existentes). Ninguno requiere buscar en otros proyectos.

### 9.1 Domain / Migraciones EF

**Ninguna migración.** Ningún ítem agrega entidades ni columnas:
- Rol "Encargado": `AspNetRoles` ya soporta roles arbitrarios vía `SeedData` — agregar una constante `RolEncargado = "Encargado"` y sembrarla es un cambio de datos (seed), no de esquema.
- Notificaciones: reutiliza `Notification`/`Notifications` (tabla ya existente).
- Todo el resto son cambios de Presentación (vistas/CSS) o un fix de Negocio (query).

### 9.2 Fix de código — `InversionesService.AsignacionesVigentesQuery` (Wang)

Ubicación: `KoiDumplings.Infrastructure/Services/InversionesService.cs:303-312`.

**Bug actual:**
```csharp
private IQueryable<AsignacionPuntos> AsignacionesVigentesQuery(int anio, int mes)
{
    return _db.AsignacionPuntos.AsNoTracking()
        .Include(a => a.Inversor)
        .Where(a => a.VigenteDesdeAnio < anio
                 || (a.VigenteDesdeAnio == anio && a.VigenteDesdesMes <= mes));
    // trae TODAS las vigencias ≤ período, no solo la última por inversor
}
```
Usado únicamente por `ObtenerResumenPuntosAsync` (`InversionesService.cs:30-46`, consumido por `PuntosController` — pantalla de solo lectura/reporte). **Confirmado que `EstadoResultadosService` (líneas 179-188 y 247-256), que es quien realmente genera las liquidaciones al cerrar un período, NO tiene este bug** — ahí sí se agrupa por `InversorId` y se toma `OrderByDescending(VigenteDesdeAnio).ThenByDescending(VigenteDesdesMes).First()`. **Ninguna liquidación histórica está mal calculada.**

**Fix:** aplicar el mismo patrón de deduplicación ya usado en `EstadoResultadosService` dentro de `AsignacionesVigentesQuery` (o en `ObtenerResumenPuntosAsync`, después de materializar la lista):
```csharp
var asignaciones = await _db.AsignacionPuntos.AsNoTracking()
    .Include(a => a.Inversor)
    .Where(a => a.Inversor.DeletedAt == null)
    .Where(a => a.VigenteDesdeAnio < anio || (a.VigenteDesdeAnio == anio && a.VigenteDesdesMes <= mes))
    .ToListAsync();

var vigentes = asignaciones
    .GroupBy(a => a.InversorId)
    .Select(g => g.OrderByDescending(a => a.VigenteDesdeAnio).ThenByDescending(a => a.VigenteDesdesMes).First())
    .ToList();
```
Verificación post-fix (ya validada manualmente contra producción antes de este cambio, ver `trazabilidad.md` 2026-08-12): para el período actual, `TotalAsignado` debe dar **95** sobre 15 inversores (antes: 102 sobre 16 filas, Wang contado dos veces). **No se toca ninguna fila de la tabla `asignacionpuntos` en producción** — es un fix de query, no de datos.

### 9.3 Pantalla "Mes actual" — impacto por capa

- **Presentación**: acción nueva en `DashboardController` (o controller separado — decisión del implementador, ambas opciones son válidas dado que reutiliza el mismo `IDashboardService`/`IIndicadoresService`), vista nueva mínima (4 KPIs, sin filtro).
- **Negocio**: ninguna lógica nueva — reutiliza el cálculo de KPIs de ventas que ya usa `DashboardService`/`IIndicadoresService` para el mes actual (mismo criterio de "mes actual" ya usado en la lógica de negocio existente del Dashboard, ej. huso horario Argentina).
- **Datos**: ninguna.
- Permisos: visible solo para rol Inversor (condicional en sidebar, sin policy nueva — reutiliza `[Authorize]` simple que ya tiene el `DashboardController`).

### 9.4 Rol "Encargado" — impacto por capa

- `SeedData.cs`: agregar `public const string RolEncargado = "Encargado";` al array de roles sembrados.
- `Program.cs`: nueva policy `RequireEncargado` o reutilizar la ya-existente `[Authorize]` simple en `FichadorController` + condición en sidebar — el control de acceso real (bloquear cualquier URL que no sea `/Fichador`) requiere revisar si `FichadorController` debe agregar el rol `Encargado` a su policy actual (`RequireAdministracion` hoy) o si se resuelve con una policy nueva que combine `RequireAdministracion` + `Encargado` solo para ese controller. El resto de los controllers (Dashboard, MiInversion, etc.) no necesitan cambios — ya excluyen implícitamente cualquier rol no contemplado en sus policies/condiciones (`Encargado` no está en ninguna, así que ya le deniegan acceso por defecto; lo único que hay que abrir es `/Fichador`).
- Sidebar (`_Layout.cshtml`): nuevo bloque condicional `@if (User.IsInRole("Encargado")) { <link a Fichador> }` — probablemente conviene que sea **excluyente** con el resto del sidebar (si es Encargado, no evaluar los demás bloques) para que no aparezcan headers de sección vacíos.

### 9.5 Notificaciones — impacto por capa

- **Presentación**: nueva vista de composición (ver Diseño §11.7), nuevo link persistente en sidebar. Acción `Crear` (GET, arma el ViewModel) y `Enviar` (POST) en `NotificationsController` (extender el existente) o un controller nuevo — a criterio del implementador dado que el controller actual ya está `[Authorize]` simple; **la acción de crear/enviar debe restringirse a Administrador/SuperUsuario** (nueva policy o chequeo explícito, el resto de acciones del controller —ver notificaciones propias— siguen abiertas a cualquier autenticado).
- **Negocio**: nuevo método en un servicio existente o uno nuevo (`INotificacionesAdminService` o extender `INotificationService`) que: (1) resuelve la lista de `ApplicationUser` para un `roleName` dado (`UserManager.GetUsersInRoleAsync`), (2) por cada destinatario final (lista ya filtrada por el admin en la UI) llama a `INotificationService.CreateAsync` si `CrearInApp` está tildado, y/o `IEmailService.SendEmailAsync` si `EnviarPorCorreo` está tildado. Reutiliza ambas interfaces tal cual existen hoy — no se les agrega nada.
- **Datos**: ninguna tabla nueva — usa `Notifications` ya existente. El envío de email no persiste nada adicional (a diferencia de `NotificacionCierre`, que sí registra `NotificacionEnvio` por auditoría de cierre de período — acá no se pide ese nivel de trazabilidad, así que no se replica esa entidad).
- Falla de un email individual no debe abortar el resto (mismo criterio que `NotificacionCierreService`).

### 9.6 Fix global — importes sin salto de línea (regla para Agentes-IA)

- Cambio de código: clase CSS `.ov-monto { white-space: nowrap; }` (o nombre equivalente) en `wwwroot/css/olvidata-theme.css`, aplicada en las vistas afectadas (Dashboard, MiInversion, RepartoGeneral, EstadoResultados, Liquidaciones, Puntos).
- **Regla nueva para el estudio** (a agregar en `C:/Sistemas/Agentes-IA/.github/instructions/25-frontend-design-system.instructions.md` o `26-checklists.instructions.md` — decisión del implementador según cuál archivo ya cubre convenciones de tabla/importes): toda celda de tabla que muestre un importe monetario (signo `$`/`U$D` + número) debe llevar una clase con `white-space: nowrap` desde el bootstrap del proyecto (blankproject base), no como fix reactivo por proyecto. Mismo patrón que el fix de tema oscuro de KOI Etapa 9, que ya generalizó una lección de UI al design system compartido — este es el segundo caso de "bug de UI descubierto en un proyecto, corregido en la base compartida".

### 9.7 Gate de aprobación para presupuesto

- [x] Sin migración EF en ningún ítem.
- [x] Rol nuevo y su alcance de permisos definidos.
- [x] Fix de Wang confirmado como bug de código, no de datos — sin riesgo para liquidaciones históricas.
- [x] Notificaciones: reutiliza 100% servicios existentes, sin entidades nuevas.
- [x] Regla de CSS global identificada y su documentación en Agentes-IA especificada.

---

## 10. Arquitectura — Mi Inversión: dividendos y recupero en pesos (Agosto 2026)

### 10.0 Escaneo de reutilización

Sin match — cálculo puntual, no hay componente equivalente en otro proyecto.

### 10.1 Application

`KoiDumplings.Application/DTOs/InversionesDtos.cs`, `MiInversionDto` — agregar:
```csharp
public decimal  DividendosPesos    { get; set; }   // suma Neto pagadas
public decimal? RecuperoPesosPorc  { get; set; }   // Σ (Neto_i / (CapitalAportadoUsd × TipoCambio_i)) × 100, solo liquidaciones con TC
```
Sin cambios en `MiInversionFilaDto` (el historial por fila no cambia).

### 10.2 Infrastructure

`InversionesService.ObtenerMiInversionAsync` (`InversionesService.cs:247-299`): junto al cálculo existente de `dividendosUsd`, agregar:
```csharp
var pagadas = liquidaciones.Where(l => l.Estado == EstadoLiquidacion.Pagada).ToList();

var dividendosPesos = pagadas.Sum(l => l.Neto);

var conTc = pagadas.Where(l => l.TipoCambio is > 0).ToList();
decimal? recuperoPesosPorc = inversor.CapitalAportadoUsd > 0 && conTc.Count > 0
    ? Math.Round(conTc.Sum(l => l.Neto / (inversor.CapitalAportadoUsd * l.TipoCambio!.Value)) * 100, 2)
    : null;
```
- `dividendosPesos` no depende de TC — suma directa de `Neto`, disponible siempre que haya liquidaciones pagadas.
- `recuperoPesosPorc` es `null` solo si no hay ninguna liquidación pagada con TC cargado (hoy no ocurre en producción — 264/264 tienen TC — pero se contempla el caso).
- Sin cambios en `AsignacionesVigentesAsync` ni en ningún otro método — el fix del bug de Wang (§9.2) no se toca ni se relaciona con este cambio.

### 10.3 Domain / Migraciones EF

Ninguna — todos los campos usados (`Neto`, `TipoCambio`, `CapitalAportadoUsd`) ya existen en el modelo.

### 10.4 Web

`Views/MiInversion/Index.cshtml` — 2 cards nuevas junto a las 3 existentes, según Diseño §12.1. Sin cambios de controller (`MiInversionController` ya pasa el `MiInversionDto` completo a la vista).

### 10.5 Riesgos

- El valor de `RecuperoPesosPorc` va a salir prácticamente igual a `RecuperoPorc` (USD) con los datos actuales — riesgo de que el cliente lo perciba como "no hace nada" al verlo en pantalla. Ya fue explicitado y aceptado en Análisis §13.2 — no es un riesgo técnico, es una expectativa a gestionar en la entrega.

### 10.6 Gate de aprobación para presupuesto

- [x] Sin migración EF.
- [x] Fórmula validada contra datos reales de producción antes de definir la arquitectura.
- [x] Sin impacto en el cálculo de liquidaciones/cierre de período — solo lectura, nuevo cálculo derivado.

---

## 11. Arquitectura — Sprint de correcciones y catálogo real (Agosto 2026)

### 11.1 Migraciones EF

**Ninguna.** Ningún ítem agrega entidades ni columnas. El ítem 4 es migración de **datos** (script SQL sobre producción), no de esquema.

### 11.2 Ítem 1 — FromName

`appsettings.Production.json` → `Olvidata_Email.Smtp.FromName` = `"KOI Dumplings"`. Archivo gitignored (contiene credenciales) → no se commitea, se publica directo con el deploy. Sin cambio de código.

### 11.3 Ítem 2 — Recupero acumulado + gráfico

- **Application**: `MiInversionFilaDto` agrega `RecuperoAcumuladoPorc` (decimal?).
- **Infrastructure** (`InversionesService.ObtenerMiInversionAsync`): el historial hoy se arma con un `Select` sobre la lista ordenada descendente. Para el acumulado hay que recorrer **ascendente** llevando un running total y después presentar descendente. Solo se acumulan liquidaciones `Pagada` con `NetoUsd` (mismo criterio que el KPI agregado, ver supuesto en Análisis §14.1).
- **Web**: columna nueva en la tabla + `<canvas>` con Chart.js (línea), alimentado desde el mismo modelo (no hace falta endpoint AJAX nuevo — el historial ya viaja completo a la vista).

### 11.4 Ítem 3 — Editar períodos cerrados

- **Infrastructure** (`EstadoResultadosService`): se quitan los dos guards de período cerrado — línea ~105 (`GuardarVentas`) y ~134 (`GuardarConceptoGastoAsync`). **NO se toca** el guard de línea ~227 (`ConfirmarCierre`: "El periodo ya esta cerrado") — cerrar dos veces sigue prohibido.
- Método nuevo `RecalcularLiquidacionesPendientesAsync(periodoId, userId)`, invocado después de cada guardado exitoso sobre un período cerrado:
  - Recalcula `UtilidadPorPunto = MontoRepartir / 100` con el nuevo `ResultadoEjercicio` (o el `MontoAjuste` si el cierre tenía ajuste manual — respetar el valor ajustado, no pisarlo con el resultado crudo).
  - Para cada `Liquidacion` del período con `Estado == Pendiente`: recalcula `Bruto = PuntosAplicados × UtilidadPorPunto`, `Neto = Bruto − Consumos`, `NetoUsd = Neto ÷ TipoCambio`. **No toca las `Pagada`.**
  - Devuelve el detalle (cuántas recalculadas, cuántas omitidas por estar pagadas, con nombres) para que el Controller lo muestre.
  - Reutiliza la misma fórmula que `ConfirmarCierre` — extraerla a un helper privado compartido para no tener dos implementaciones del cálculo que puedan divergir.
- **Auditoría**: registrar en la tabla `auditlogs` (ya existente) cada edición sobre un período cerrado: usuario, fecha/hora, período, subgrupo/campo, valor anterior → valor nuevo. Es requisito del Análisis, no opcional.
- **Riesgo declarado**: un período cerrado editado deja el `ResultadoEjercicio` distinto del que se usó para generar las liquidaciones ya **pagadas** — esa inconsistencia es intencional y aceptada (decisión del cliente), pero debe quedar visible en pantalla, no silenciosa.

### 11.5 Ítem 4 — Catálogo real + remapeo de históricos (RIESGO ALTO)

**Orden de ejecución obligatorio:**
1. **Backup de la base de producción** antes de tocar nada.
2. Snapshot de verificación: total de gastos por período (`SELECT PeriodoMensualId, SUM(ImporteManual) FROM conceptosgasto GROUP BY 1`) — guardado para comparar después.
3. Alta de los 8 rubros y ~40 subgrupos del PDF.
4. Remapeo de los 373 `conceptosgasto` históricos: `UPDATE conceptosgasto SET SubgrupoId = <nuevo> WHERE SubgrupoId = <viejo>`.
5. Baja lógica (`DeletedAt`) de los subgrupos genéricos ya remapeados.
6. **Verificación**: re-ejecutar la query del paso 2 y confirmar que los totales por período son idénticos. Si algún total cambió, revertir con el backup.

**Mapeo propuesto (requiere revisión del cliente antes de ejecutar):**

| Subgrupo actual | → Nuevo | Nota |
|---|---|---|
| CMV | Costo Mercadería Vendida / **Mercadería KOI** | ⚠️ El genérico agrupa lo que ahora se abre en 4 (Mercadería KOI, Barriles, Verdulería, Bebidas) — todo el histórico cae en "Mercadería KOI" salvo que el cliente prefiera otro criterio |
| Regalías (3 %) | Fee de Franquicia / Regalías (3 %) | directo, sigue calculado |
| Canon (2,5 %) | Fee de Franquicia / Cánon de publicidad (2,5 %) | directo, sigue calculado |
| Sueldos y Jornales | Sueldos y CCSS / Sueldos | directo |
| Cargas Sociales | Sueldos y CCSS / Cargas Sociales | directo |
| Honorarios | Servicios / **Contador** | ⚠️ a confirmar |
| Luz / Gas / Internet / Agua | Servicios / (mismos nombres) | directo |
| Alquiler del local | Alquiler / Alquiler | directo |
| Expensas | Alquiler / Alquiler | ⚠️ sin equivalente en el PDF — se fusiona con Alquiler |
| Mantenimiento | Gastos Varios / Mantenimiento y Reparaciones | directo |
| Publicidad | Impuestos / Publicidad y Propaganda | ⚠️ agrupación rara del Excel del cliente, pero es la suya |
| Otros gastos | Gastos Varios / **Almacén** | ⚠️ sin equivalente claro — a confirmar |
| Comisiones Tarjetas (5 %) | Servicios / Comisiones Tarjetas / Merc Pago | ⚠️ **cambia de calculado a manual** |
| IIBB (3,5 %) | Impuestos / Ingresos Brutos | ⚠️ **cambia de calculado a manual** |
| Débitos/Créditos (1,2 %) | Impuestos / Imp a los débitos y créditos | ⚠️ **cambia de calculado a manual** |
| Tasa Municipal (1 %) | Impuestos / Tasa Insp. Seg e Hig municipal | ⚠️ **cambia de calculado a manual** |
| Previsión I (1 %) | Previsión y Reservas / Fondo de juicios laborales (1 %) | sigue calculado |
| Previsión II (1 %) | Previsión y Reservas / Reposición maquinaria (1 %) | sigue calculado |

Los subgrupos nuevos sin equivalente histórico (Barriles, Verdulería, Bebidas, Sindicato, Aceite, Cristalería, Insumos Barra, Papelería, Limpieza, Fletes, Pastillas Horno, Alarma, Software de Ventas, Máquina AQA, Sanitización, Fumigación, Seguro, Reservas Online, Mantenimiento Cta Bancaria, Comisiones PedidosYa/Rappi, IVA, Anticipo Ganancias, Ocupación Esp Público, Serv Urbanos, Recolección Basura) se crean vacíos: aplican de acá en adelante.

**Cambio de `TipoConcepto` de calculado a Manual** (Comisiones, IIBB, Débitos/Créditos, Tasa Municipal): ojo — los `conceptosgasto` históricos de esos subgrupos guardaron el importe calculado en su momento. Al pasarlos a Manual, ese importe queda como valor manual fijo (correcto: preserva el histórico). Los meses nuevos se cargan a mano.

### 11.6 Ítem 5 — Importación recurrente

`ImportacionInicialService`: hoy cada bloque hace "si ya existe → advertencia + `continue`". Se agrega un flag `actualizarExistentes` (bool) al DTO de entrada que, cuando viene en `true`, en vez de saltear hace `UPDATE` de la fila existente. Aplica a los 6 bloques (períodos, ventas, conceptos de gasto, inversores, asignaciones, liquidaciones). El resultado pasa de dos listas (errores/advertencias) a distinguir también los actualizados.
- Si el período que se actualiza está **cerrado**, invocar el mismo `RecalcularLiquidacionesPendientesAsync` del ítem 3 — no puede haber dos caminos distintos para el mismo efecto.
- Sin cambios de esquema.

### 11.7 Ítem 6 — Orden Reparto General

Solo vista (`Views/RepartoGeneral/Index.cshtml`), idéntico al fix ya aplicado en `EstadoResultados/Anual.cshtml`. Sin cambios de código C#.

### 11.8 Gate de aprobación

- [x] Sin migración EF en ningún ítem.
- [x] Ítem 4 con procedimiento de backup + verificación definido, y mapeo explícito para revisión del cliente.
- [x] Ítem 3 con la fórmula de recálculo compartida con `ConfirmarCierre` (no se duplica lógica de cálculo financiero).
- [x] Ítem 5 reutiliza el recálculo del ítem 3 en vez de implementar el suyo.

---

## 12. Arquitectura — Módulo E2-01 "Integración Ayres POS" (Fase 6, Septiembre 2026)

Entrada: `1-analista-funcional.md` §15 (R-A01 resuelto, P-A08 confirmado) y `2-disenador-funcional.md` §14 aprobado.

### 12.1 Mapa por capa

| Capa | Archivo | Rol |
|---|---|---|
| **Domain** | — | **Sin cambios. Sin migración EF.** Las ventas se escriben en `VentasMensuales`, que ya existe |
| **Application** | `DTOs/AyresDtos.cs` | `VentasPeriodoAyresDto`, `PreviewVentasAyresDto` |
| | `Interfaces/IAyresService.cs` | `ObtenerVentasPeriodoAsync`, `ProbarConexionAsync` |
| | `Exceptions/AyresIndisponibleException.cs` | Mismo criterio que `QuickPassIndisponibleException` |
| | `Settings/FeatureFlags.cs` | **+ `public bool IntegracionAyres { get; set; } = false;`** — primer flag real del scaffold |
| **Infrastructure** | `Services/AyresSettings.cs` | POCO: `BaseUrl`, `Email`, `Pass`, `IdSucursal`, `TimeoutSeconds`, `DiasPorConsulta` (default 10), `MapeoCanales` |
| | `Services/AyresTokenCache.cs` | **Singleton.** Adaptado de `marihogar/AfipTokenCache.cs` |
| | `Services/AyresService.cs` | **Scoped.** Login, chunking, agregación, mapeo de canales |
| | `DependencyInjection.cs` | Cliente nombrado `"Ayres"` + registros |
| **Web** | `Controllers/EstadoResultadosController.cs` | `PreviewAyres`, `AplicarAyres` |
| | `Controllers/SystemController.cs` | **Se elimina `DiagnosticoAyres`**; se agrega `ProbarAyres` sobre `IAyresService` (HU-A08) |
| | `Models/EstadoResultadosViewModels.cs` | `ErMensualViewModel.AyresHabilitado` |
| | `Views/EstadoResultados/Mensual.cshtml` | Botón + modal de preview |
| **Config** | `appsettings.json` (versionado) | Sección `Ayres` **con credenciales vacías** + `Features.IntegracionAyres` |
| | `appsettings.Production.json` (gitignored) | Ya cargada con las credenciales reales |

### 12.2 Ciclo de vida en DI (crítico)

```
services.Configure<AyresSettings>(configuration.GetSection("Ayres"));
services.AddHttpClient("Ayres", (sp, client) => {
    var s = sp.GetRequiredService<IOptions<AyresSettings>>().Value;
    client.BaseAddress = new Uri(s.BaseUrl);
    client.DefaultRequestHeaders.Add("Accept", "application/json");
    client.Timeout = TimeSpan.FromSeconds(s.TimeoutSeconds);
});
services.AddSingleton<AyresTokenCache>();     // ← Singleton: el token sobrevive entre requests
services.AddScoped<IAyresService, AyresService>();
```

**`AyresTokenCache` DEBE ser Singleton y `AyresService` Scoped.** Registrarlos al revés hace que el token se pierda en cada request y se dispare un login por llamada — 4 logins por mes importado en vez de 1. Es el error clásico del patrón y no da error visible, solo tráfico y latencia de más.

**Sin `BaseAddress` con puerto omitido:** la URL es `http://koi.ayresit.com:8520` y el puerto es parte de la config, no del código.

### 12.3 Token: vigencia real, no asumida

Se porta el criterio de `AfipTokenCache` (PAT-006):
- La vigencia sale de **`content.aliveTime` que devuelve Ayres** (3599 s hoy), nunca de una constante.
- **Margen de seguridad de 60 s**: se considera vencido antes del vencimiento real, para no arrancar un chunk con un token que muere a mitad.
- `SemaphoreSlim(1,1)` + doble chequeo dentro del lock: dos requests concurrentes no disparan dos logins.
- `Invalidar()` ante un `UNAUTHORIZED_ACCESS` recibido con token que localmente creíamos vigente → un solo re-login y reintento. **Máximo un reintento**, para no entrar en bucle si la credencial cambió de verdad.

### 12.4 Chunking y agregación

```
rango del mes → tramos de DiasPorConsulta (10) días
  para cada tramo:
      GET /ventas?fechaContableDesde=yyyy-MM-dd&fechaContableHasta=yyyy-MM-dd
      acumular en el agregador
      DESCARTAR el detalle del tramo
  devolver el agregado
```

- **Secuencial, no en paralelo.** Son 3-4 llamadas contra el servidor del local; el paralelismo no compensa el riesgo de golpearlo.
- **Se acumula y se descarta**: nunca se sostienen en memoria las ~1.062 ventas del mes con sus `items[]` (R-A03).
- **Si un tramo falla, se propaga y no se aplica nada.** La agregación vive en memoria, así que no hay estado parcial que limpiar (HU-A05).
- Fechas: se envían `yyyy-MM-dd`; **se parsean de vuelta con `"dd/MM/yyyy"` y `CultureInfo.InvariantCulture`**, formato explícito. Nunca `DateTime.Parse` por cultura del servidor.

### 12.5 Contrato de deserialización

El sobre viene anidado y es la trampa principal:

```
content: { fechas: {...}, cantidad: int, ventas: [ { venta: { ... } } ] }
                                                    ^^^^^ nivel extra
```

DTO espejo con `[JsonPropertyName]` explícito en cada campo. **No confiar en el naming policy**: un campo mal mapeado devuelve 0 silenciosamente y el preview mostraría un total incorrecto sin ningún error.

Campos consumidos: `facturaMontoTotal`, `cantidadConsumidores`, `sectorTipo`, `items[].cantidad`, `fechaContable`, `estado`.

**`estado` (R-A04):** se lee y se expone en el agregado el conteo por estado. En agosto el total cerró al centavo contra la carga manual, así que aparentemente no hay anuladas que descontar — pero **queda instrumentado**: si aparece un estado distinto de `'C'`, el preview lo informa en vez de sumarlo sin criterio. Decisión de qué hacer con ellas: recién cuando aparezcan.

### 12.6 Mapeo de canales (P-A08 confirmado)

`ME` → Salón · `PE` → Pedidos · `MO` → Mostrador. **En configuración, no en código**:

```json
"MapeoCanales": { "ME": "Salon", "PE": "Pedidos", "MO": "Mostrador" }
```

Un `sectorTipo` ausente del diccionario no rompe ni se descarta: suma a `Otros` y el preview lo muestra con advertencia (HU-A07). Cambiar el mapeo no requiere redeploy.

Los importes van al lado **A** (`VentasASalon`, `VentasAPedidos`, `VentasAMostrador`), consistente con cómo está cargada la historia. El lado B queda en 0 y **no se pisa** si tuviera algo.

### 12.7 Mapeo de errores

| Origen | Excepción | Mensaje al usuario |
|---|---|---|
| `SocketException`, `HttpRequestException`, timeout | `AyresIndisponibleException` | "No se pudo conectar con Ayres. El período quedó sin cambios." **Se loguea el detalle técnico** (D-A01: si Ayres cambia de IP el síntoma es WSAEACCES y hay que poder diagnosticarlo rápido) |
| `resultCode = UNAUTHORIZED_ACCESS` tras reintento | `AyresIndisponibleException` con flag de credenciales | "Ayres rechazó las credenciales. Revisá la configuración." |
| `resultCode` distinto de `SUCCESS` | `AyresIndisponibleException` | Se propaga `resultDescription` |

`GlobalExceptionHandler` ya devuelve JSON para AJAX: se aprovecha, no se duplica manejo.

### 12.8 Escritura: reutilizar, no duplicar

`AplicarAyres` **no escribe directo** en `VentasMensuales`. Llama a `_erService.GuardarVentasAsync(...)`, el mismo método del guardado manual. Consecuencias:
- El recálculo de porcentuales sale gratis (`GuardarVentasAsync` ya llama a `RecalcularInternamente`).
- La validación de período cerrado ya está adentro: doble barrera con la del controller.
- Los overrides manuales de conceptos porcentuales (Etapa 19) se respetan solos.
- **Cero lógica financiera nueva.** Si mañana cambia la regla de cierre, cambia en un solo lugar.

`AplicarAyres` devuelve **la misma forma JSON que `GuardarVentas`**, para que el cliente reutilice el repintado existente sin JS nuevo de actualización.

### 12.9 Seguridad

- Ambas acciones: `[HttpPost]`, `[ValidateAntiForgeryToken]`, policy `SoloAdministrador`. **Verificar que los atributos queden pegados al método correcto** (incidente del 2026-09-08 con `TestEmail`).
- Las credenciales **solo** en `appsettings.Production.json` (gitignored). En el `appsettings.json` versionado la sección va con valores vacíos.
- El token **nunca** se devuelve al cliente ni se loguea.
- `ProbarConexionAsync` informa si conecta, sin exponer el token.
- **R-A02 sigue abierto** (HTTP sin TLS): documentado, no resoluble desde este código.

### 12.10 Checklist de gate

- [x] Sin cambios en Domain · sin migración EF
- [x] Sin lógica financiera nueva: la escritura reutiliza `GuardarVentasAsync`
- [x] Ciclos de vida de DI explicitados (el error de Singleton/Scoped documentado)
- [x] Cache de token portado de un patrón con implementación en producción (PAT-006)
- [x] Chunking secuencial con descarte de detalle (R-A03)
- [x] Fechas con formato y cultura explícitos
- [x] Mapeo de canales configurable, con degradación a "Otros"
- [x] Feature flag para apagar el módulo sin redeploy
- [x] Diagnóstico temporal marcado para eliminación
- [ ] **Presupuesto: SALTEADO por decisión del dueño del estudio (2026-09-08)**
