# 3 - Arquitecto MVC — Proyecto KOI

> Memoria acumulativa del agente arquitecto.
> Etapa: Arquitectura. Estado: 🟡 ACTUALIZADO — P-A01→P-A07 incorporadas. Gate de presupuesto requiere recalculación.
> Fecha: 2026-06-11. Inputs: 1-analista-funcional.md v2 + 2-disenador-funcional.md v2.

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
