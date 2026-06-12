# 2 - Diseñador funcional — Proyecto Yoga

> Memoria acumulativa del agente diseñador funcional.
> Etapa: Diseño funcional. Estado: CERRADO (aprobado para arquitectura).
> Fecha: 2026-06-11. Input: 1-analista-funcional.md aprobado.

## 1. Alcance funcional resumido

Sistema web con un único rol Administrador. El Admin configura los planes (1–5 hs/semana), gestiona alumnos y suscripciones, genera y cobra las cuotas mensuales, registra clases dictadas y liquida profesores, registra egresos y consulta la cuenta corriente y el dashboard financiero de inicio. Design system Olvidata (Bootstrap 5 + olvidata-theme) sobre la base blankproject.

## 2. Lógica de distribución estándar (todo el sistema)

- **Layout**: sidebar de navegación (gradiente Olvidata) + topbar con selector de período donde aplique. Contenido en cards (`ov-card`).
- **Pantallas de consulta**: fila de cards KPI arriba → gráficos al medio → tabla de detalle abajo (DataTables dentro de `table-responsive`).
- **Pantallas ABM**: listado con buscador y filtros → modal o vista de alta/edición → baja lógica con confirmación (SweetAlert2).
- **Menú**: Dashboard · Alumnos · Suscripciones · Cuotas · Profesores · Clases · Liquidaciones · Cuenta corriente · Configuración (Planes).

## 3. Flujo de pantallas y wireframes textuales

### P-01 Login
Card centrada: usuario, contraseña, botón ingresar, enlace de recuperación. Errores con mensaje genérico. Redirección al Dashboard.

### P-02 Dashboard (pantalla de inicio)
Selector de mes/año (default: mes actual).
```
[ KPI Ingresos del mes ] [ KPI Egresos del mes ] [ KPI Resultado del mes ] [ KPI Saldo de caja ]
[ KPI Alumnos activos ]  [ KPI Cuotas vencidas (cant. y $) ]
[ Gráfico barras: Ingresos vs Egresos, últimos 12 meses ]
[ Gráfico línea: Saldo acumulado de caja ]   [ Gráfico barras agrupadas: comparativo anual ingresos/egresos ]
[ Gráfico dona: alumnos activos por plan ]   [ Tabla: últimos movimientos de caja ]
```
- Meses sin datos: card en estado vacío ("Sin datos del período"), nunca división por cero.
- Una sola librería de charts JS para todo el sistema.

### P-03 Alumnos (ABM)
Listado con buscador (nombre, teléfono) y filtro activo/inactivo. Alta/edición: nombre, apellido, documento, teléfono, email, observaciones, activo. La ficha del alumno muestra su suscripción vigente y el historial de suscripciones y cuotas.

### P-04 Planes (Configuración)
Grilla de los 5 planes: nombre, horas semanales (1–5), precio mensual vigente, activo. Edición de precio con aviso: "el cambio rige para las cuotas que se generen desde ahora". Solo lectura de la cantidad de suscripciones activas por plan.

### P-05 Suscripciones
Listado con filtros (estado, plan, alumno). Alta: alumno (autocomplete) + plan + fecha de inicio; bloquea si el alumno ya tiene suscripción activa. Acciones: **Cambiar plan** (cierra la vigente y crea una nueva desde la fecha indicada), **Pausar / Reanudar**, **Finalizar** (fecha de fin). Historial por alumno visible.

### P-06 Cuotas del período
Cabecera: selector de mes/año + botón **"Generar cuotas del período"** (resumen previo: cuántas se van a generar; idempotente). Grilla: alumno, plan, monto, vencimiento, estado (Pendiente / Pagada / **Vencida** resaltada), fecha y medio de pago. Acciones por fila: **Registrar pago** (modal: fecha, medio de pago) · Anular pago (con motivo). Tab **Deudores**: alumnos con cuotas vencidas, total adeudado y antigüedad.

### P-07 Profesores (ABM)
Listado: nombre, contacto, tarifa por hora vigente, activo. Edición de tarifa con aviso: "rige para las liquidaciones que se generen desde ahora".

### P-08 Clases dictadas
Carga rápida: profesor (select), fecha, horas, nota opcional. Grilla del mes con filtro por profesor; total de horas por profesor al pie. Clases incluidas en una liquidación: solo lectura (candado visible).

### P-09 Liquidaciones de profesores
Selector de mes/año. Por profesor: horas del mes, tarifa, monto calculado, estado (Sin generar / Pendiente / Pagada). Acciones: **Generar liquidación** (congela horas × tarifa) · **Marcar pagada** (fecha de pago → genera egreso en caja) · Detalle con las clases incluidas. Reapertura solo con motivo.

### P-10 Cuenta corriente
```
[ KPI Saldo actual ] [ KPI Ingresos del período ] [ KPI Egresos del período ]
[ Filtros: tipo (Ingreso/Egreso) · categoría · rango de fechas ]
[ Tabla: fecha | tipo | categoría | descripción | origen (link) | importe | saldo acumulado ]
[ Botón: + Registrar egreso (Gasto / Retiro) ]
```
Movimientos automáticos (Pago de cuota, Pago a profesor) con link al origen; egresos manuales con modal (categoría, fecha, importe, descripción).

## 4. ViewModels propuestos (campos y validaciones funcionales)

| ViewModel | Campos principales | Validaciones |
|---|---|---|
| LoginVM | Usuario, Password | requeridos |
| DashboardVM | Período, KPIs (ingresos, egresos, resultado, saldo, alumnos activos, vencidas), series 12 meses, comparativo anual, distribución por plan | solo lectura; períodos sin datos → vacío controlado |
| AlumnoVM | Nombre, Apellido, Documento, Teléfono, Email, Observaciones, Activo | nombre y apellido requeridos; email válido si se carga |
| PlanVM | Nombre, HorasSemana (1–5), PrecioMensual, Activo | precio > 0; horas 1–5 únicas |
| SuscripcionVM | Alumno, Plan, FechaInicio, Estado, FechaFin | una activa por alumno; fecha fin ≥ inicio |
| CuotaVM | Suscripción, Período, Monto, Vencimiento, Estado, FechaPago, MedioPago | monto congelado; pago requiere fecha y medio |
| GenerarCuotasVM | Período, resumen (a generar / ya generadas) | idempotente |
| ProfesorVM | Nombre, Contacto, TarifaHora, Activo | tarifa > 0 |
| ClaseDictadaVM | Profesor, Fecha, Horas, Nota | horas > 0; editable solo si no liquidada |
| LiquidacionProfesorVM | Profesor, Período, TotalHoras, Tarifa, Monto, Estado, FechaPago | única por profesor+período; pagada inmutable |
| MovimientoCajaVM | Fecha, Tipo, Categoría, Descripción, Importe, Origen | importe > 0; categoría requerida en manuales |

## 5. Máquina de estados

- **Suscripción**: `Activa` ⇄ `Pausada`; `Activa|Pausada` → `Finalizada` (terminal). Solo `Activa` genera cuota en la generación del período.
- **Cuota**: `Pendiente` → `Pagada` (registra fecha/medio + ingreso en caja). `Vencida` es estado **derivado**: Pendiente con vencimiento < hoy. Anular pago: motivo obligatorio, vuelve a Pendiente y revierte el movimiento.
- **Liquidación**: `Pendiente` → `Pagada` (egreso en caja, inmutable). Reapertura con motivo auditado revierte el egreso.

## 6. Historias de usuario

<!-- Fuente de verdad para la validación QA. Formato: "Como <rol>, quiero <acción> para <beneficio>". -->

**HU-01** — Como administrador, quiero ingresar al sistema con usuario y contraseña para que la información de la escuela esté protegida.
- CA: credenciales inválidas muestran error genérico; sesión activa redirige al dashboard; puedo cambiar mi contraseña.

**HU-02** — Como administrador, quiero configurar los planes de 1 a 5 horas semanales con su precio para reflejar la oferta de la escuela.
- CA: existen los 5 planes con precio propio; al cambiar un precio, las cuotas ya generadas no cambian y las nuevas usan el precio nuevo.

**HU-03** — Como administrador, quiero dar de alta, editar y desactivar alumnos para mantener el padrón al día.
- CA: el buscador encuentra por nombre/teléfono; un alumno con historial se desactiva (no se elimina); la ficha muestra suscripción vigente e historial.

**HU-04** — Como administrador, quiero suscribir un alumno a un plan para que el sistema le genere sus cuotas mensuales.
- CA: no puedo crear una segunda suscripción activa para el mismo alumno; la suscripción registra plan y fecha de inicio.

**HU-05** — Como administrador, quiero cambiar de plan, pausar o finalizar una suscripción para acompañar los cambios del alumno.
- CA: el cambio de plan conserva el historial (vigencia anterior cerrada + nueva abierta); una suscripción pausada o finalizada no genera cuotas.

**HU-06** — Como administrador, quiero generar las cuotas del mes con un clic para no cargarlas una por una.
- CA: se crea una cuota por suscripción activa con el precio vigente del plan y el vencimiento configurado; repetir la generación no duplica cuotas.

**HU-07** — Como administrador, quiero registrar el pago de una cuota para llevar el control de cobranza.
- CA: el pago registra fecha y medio; la cuota pasa a Pagada y aparece un ingreso en cuenta corriente por el mismo monto; una cuota pagada no se puede volver a pagar.

**HU-08** — Como administrador, quiero ver las cuotas vencidas y los deudores para reclamar los pagos atrasados.
- CA: una cuota pendiente con vencimiento pasado se muestra como Vencida sin intervención manual; el tab Deudores totaliza la deuda por alumno.

**HU-09** — Como administrador, quiero gestionar los profesores con su tarifa por hora para poder liquidarles las clases.
- CA: ABM con baja lógica; el cambio de tarifa rige para liquidaciones futuras.

**HU-10** — Como administrador, quiero registrar las clases dictadas por cada profesor para que la liquidación se calcule sola.
- CA: la carga pide profesor, fecha y horas (> 0); una clase ya liquidada no se puede editar ni borrar.

**HU-11** — Como administrador, quiero generar la liquidación mensual de cada profesor para saber cuánto pagarle.
- CA: monto = Σ horas del mes × tarifa vigente, congelado al generar; única por profesor y mes; al marcarla Pagada se genera el egreso en caja y queda inmutable.

**HU-12** — Como administrador, quiero registrar gastos y retiros para que la cuenta corriente refleje todos los movimientos.
- CA: el egreso manual exige categoría (Gasto/Retiro), importe > 0 y descripción; impacta el saldo de inmediato.

**HU-13** — Como administrador, quiero consultar la cuenta corriente con su saldo para conocer la situación de caja.
- CA: saldo = ingresos − egresos y coincide con la suma de los movimientos listados; cada movimiento automático tiene link a su origen; filtros por tipo, categoría y fechas.

**HU-14** — Como administrador, quiero ver al ingresar un dashboard con los KPIs del mes para entender la situación de la escuela de un vistazo.
- CA: ingresos/egresos/resultado del mes coinciden con caja; muestra saldo, alumnos activos y cuotas vencidas; gráficos de 12 meses, saldo acumulado, comparativo anual y distribución por plan; sin errores en meses vacíos.

## Historial de ajustes
- 2026-06-11: diseño funcional v1 — 10 pantallas con wireframes textuales, 11 ViewModels, máquinas de estado de suscripción/cuota/liquidación y 14 historias de usuario con criterios de aceptación. Aprobado para arquitectura.
