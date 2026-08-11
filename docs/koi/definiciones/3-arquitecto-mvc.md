# 3 - Arquitecto MVC — Proyecto KOI

> Memoria acumulativa del agente arquitecto.
> Etapa: Arquitectura. Estado: ✅ Etapa 1 cerrada. Módulo E2-02 (Fichador) arquitecturado en §8 — contrato real de API confirmado (§8.8), gate de Implementación habilitado (cliente entregó ApiKey/IdEmpresa + documentación).
> Fecha: 2026-06-11. Última actualización: 2026-08-10 (sesión 2) — §8.2/8.3/8.8 corregidos contra la documentación real de QuickPass. Inputs: 1-analista-funcional.md §11 + 2-disenador-funcional.md §10.

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
