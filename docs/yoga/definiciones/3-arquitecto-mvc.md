# 3 - Arquitecto MVC — Proyecto Yoga

> Memoria acumulativa del agente arquitecto.
> Etapa: Arquitectura. Estado: CERRADO (gate aprobado para presupuesto).
> Fecha: 2026-06-11. Inputs: 1-analista-funcional.md y 2-disenador-funcional.md aprobados.

## 1. Alcance resumido

Sistema nuevo sobre la base blankproject de OlvidataSoft: **ASP.NET Core MVC (.NET 10) + EF Core + MySQL 8**, capas Domain / Application / Infrastructure / Web. Se reutiliza todo lo resuelto en la base: autenticación Identity, layout Olvidata, pipeline, DataTables/Select2/SweetAlert2, convenciones (`SoftDestroyable`, `ServiceResult`, `IRepository<T>`). **Sin integraciones externas, sin BackgroundServices, sin USD/tipo de cambio** (moneda única ARS).

## 2. Impacto técnico por capa

### Domain (entidades nuevas)

| # | Entidad | Notas |
|---|---|---|
| 1 | `Alumno` | Nombre, apellido, documento, teléfono, email, observaciones, baja lógica. |
| 2 | `Plan` | Nombre, horas semanales (1–5, único), precio mensual vigente, activo. Seed de los 5 planes. |
| 3 | `Suscripcion` | Alumno × plan, fecha inicio/fin, estado (Activa/Pausada/Finalizada). Cambio de plan = cierre + alta nueva (historial). |
| 4 | `Cuota` | Suscripción × período (año/mes, único), monto **snapshot** del precio del plan al generar, vencimiento, estado (Pendiente/Pagada), fecha y medio de pago, motivo de anulación. `Vencida` se deriva por fecha (no se persiste). |
| 5 | `Profesor` | Nombre, contacto, tarifa por hora vigente, baja lógica. |
| 6 | `ClaseDictada` | Profesor, fecha, horas, nota; FK opcional a liquidación (al liquidar queda vinculada y bloqueada). |
| 7 | `LiquidacionProfesor` | Profesor × período (único), total horas, tarifa snapshot, monto, estado (Pendiente/Pagada), fecha de pago, motivo de reapertura. |
| 8 | `MovimientoCaja` | Fecha, tipo (Ingreso/Egreso), categoría (PagoCuota/PagoProfesor/Gasto/Retiro), importe, descripción, FK opcionales a `Cuota` y `LiquidacionProfesor` (navegación al origen). |

Más las tablas de Identity de la base (~6–7). **Total estimado del esquema entregado: ~14–15 tablas** → rango 6–15 (relevante para plan de mantenimiento PRO).

### Application (servicios)

- `SuscripcionService`: alta con validación de única activa por alumno; cambio de plan transaccional (cierra vigencia + crea nueva); pausa/reanudación/finalización.
- `CuotaService`: generación idempotente de cuotas del período (una por suscripción activa, monto = precio vigente del plan, vencimiento configurado); registro de pago transaccional (cuota Pagada + `MovimientoCaja` Ingreso); anulación con motivo y reversión del movimiento; consulta de deudores (Pendiente con vencimiento pasado).
- `LiquidacionProfesorService`: generación única por profesor+período (Σ horas no liquidadas del mes × tarifa vigente, snapshot); marca de pago transaccional (liquidación Pagada + `MovimientoCaja` Egreso + bloqueo de clases); reapertura auditada con reversión.
- `CajaService`: registro de egresos manuales; consulta de movimientos con saldo acumulado y filtros; saldo actual.
- `DashboardService`: agregaciones del mes y series (ingresos/egresos 12 meses, saldo acumulado, comparativo anual, alumnos activos por plan, cuotas vencidas); tolerante a períodos sin datos.

### Infrastructure

- DbContext + configuraciones EF de las 8 entidades, repositorios según convención de la base.
- Índices únicos: `Plan.HorasSemana`, `Cuota (SuscripcionId, Año, Mes)`, `LiquidacionProfesor (ProfesorId, Año, Mes)`.
- Query filters de baja lógica con `IgnoreQueryFilters()` en consultas históricas (alumnos/profesores inactivos en cuotas y liquidaciones pasadas).

### Web

- Controllers: `Account` (base), `Dashboard`, `Alumnos`, `Planes`, `Suscripciones`, `Cuotas`, `Profesores`, `Clases`, `Liquidaciones`, `Caja`.
- Vistas según wireframes P-01…P-10; layout Olvidata; una librería de charts JS (Chart.js o la ya disponible en la base).

## 3. Modelo de permisos

- Roles Identity: `Administrador` (+ `SuperUsuario` interno del proveedor, fuera de la doc al cliente).
- Policy única `SoloAdministrador` sobre todos los controllers (sistema mono-rol); sin lógica de aislamiento por usuario.

## 4. Migraciones EF

**Sí.** Una migración inicial con el esquema completo (8 entidades + seed: 5 planes, roles, usuario administrador inicial, día de vencimiento de cuotas como parámetro de configuración en appsettings o tabla de configuración simple si se prefiere editable).

## 5. Decisiones técnicas relevantes

- **Snapshot de montos**: el precio del plan se congela en la cuota al generarla y la tarifa del profesor en la liquidación al generarla — los cambios de precios/tarifas nunca recalculan documentos existentes (mismo patrón que KOI con porcentajes).
- **Estado Vencida derivado**: se calcula por comparación de fecha en consultas (sin job nocturno ni BackgroundService) — simplifica despliegue single-node.
- **Transaccionalidad**: pago de cuota, anulación, pago de liquidación y reapertura son operaciones transaccionales (documento + movimiento de caja juntos, nunca uno sin el otro).
- **Sin multimoneda**: importes decimales en ARS; sin tipo de cambio.
- **Entrega en dos etapas** (decisión comercial 2026-06-12): Etapa 1 (MVP) = módulos de acceso, planes, alumnos, suscripciones y cuotas/pagos; Etapa 2 = profesores, liquidaciones, caja y dashboard. En la Etapa 1 el pago de cuota solo marca la cuota (fecha/medio); al activar `MovimientoCaja` en la Etapa 2, `CajaService` genera retroactivamente (backfill) los ingresos de las cuotas pagadas — desde entonces rige la transaccionalidad documento + movimiento.

## 6. Riesgos y supuestos

- R-A1: volumen bajo (decenas de alumnos, 12 períodos/año, 1 usuario) → sin requisitos de performance ni caching.
- R-A2: la idempotencia de la generación de cuotas y la unicidad de liquidaciones se resuelven con índices únicos + validación en servicio (riesgo bajo).
- R-A3: si el cliente luego pide pagos parciales de cuota, requiere entidad `Pago` separada (cambio de alcance, se cotiza aparte).
- S-A1: un solo entorno productivo, hosting del proveedor (plan de mantenimiento).
- S-A2: carga inicial de datos por pantalla a cargo del administrador (sin módulo de importación).

## 7. Gate de aprobación para presupuesto

- [x] Entidades y migración EF declaradas (8 entidades, ~14–15 tablas con Identity).
- [x] Permisos por rol definidos (mono-rol, policy única).
- [x] Máquinas de estado del diseño soportadas (enums + transiciones en servicios + motivos auditados).
- [x] Sin integraciones externas en el alcance base.
- [x] Reutilización de la base blankproject confirmada (Identity, layout, librerías UI, pipeline).

**APROBADO para pasar a presupuesto.**

## Historial de ajustes
- 2026-06-11: arquitectura v1 — 8 entidades nuevas (~14–15 tablas con Identity), 5 servicios de Application, migración EF inicial + seed, snapshot de precios/tarifas, estado Vencida derivado sin jobs. Gate aprobado para presupuesto.
