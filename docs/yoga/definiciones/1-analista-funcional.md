# 1 - Analista funcional — Proyecto Yoga

> Memoria acumulativa del agente analista funcional.
> Etapa: Discovery + Análisis funcional. Estado: CERRADO (aprobado para diseño).
> Fecha: 2026-06-11.

## 1. Contexto del cliente

Escuela de yoga que gestiona hoy de manera informal (sin sistema) las suscripciones de sus alumnos, el cobro de cuotas mensuales y los pagos a los profesores que dictan las clases. Necesita un **sistema web de gestión** que:

1. Registre las **suscripciones de alumnos** a planes de entrenamiento.
2. Permita configurar **planes de 1, 2, 3, 4 y 5 horas semanales**, cada uno con un valor diferente.
3. Permita al administrador **registrar los pagos mensuales** de cada suscripción, con control de cuotas al día y vencidas.
4. Lleve una **cuenta corriente** con todos los movimientos de dinero: ingresos por pagos de alumnos y egresos por retiros, gastos y pagos a profesores.
5. **Liquide a los profesores** según las clases dictadas (tarifa por hora).
6. Tenga una **pantalla de inicio (dashboard)** con los KPIs importantes del sistema, con foco financiero.

El sistema será utilizado por **un único rol Administrador** (el responsable de la escuela).

## 2. Alcance funcional

### Incluido (alcance base)

1. **Autenticación y cuenta del administrador**: login con usuario y contraseña, cambio y recuperación de contraseña. Un único usuario operativo.
2. **Planes de entrenamiento**: catálogo de planes de 1 a 5 horas semanales, cada uno con nombre y precio mensual propio editable. Los cambios de precio rigen hacia adelante: las cuotas ya generadas conservan su monto original.
3. **Gestión de alumnos**: ABM de alumnos (datos personales y de contacto, estado activo/inactivo con baja lógica, observaciones).
4. **Suscripciones**: alta de suscripción de un alumno a un plan con fecha de inicio; cambio de plan (cierra la vigencia anterior y abre una nueva, conservando historial); pausa y finalización. Un alumno tiene como máximo una suscripción activa a la vez.
5. **Cuotas mensuales y pagos**: generación de las cuotas del mes para todas las suscripciones activas (monto según el precio vigente del plan, congelado en la cuota); estados Pendiente / Pagada, con Vencida derivada automáticamente por fecha de vencimiento; registro del pago (fecha y medio de pago) que genera el ingreso en cuenta corriente; listado de deudores.
6. **Profesores y clases dictadas**: ABM de profesores con tarifa por hora; registro de las clases dictadas (profesor, fecha, cantidad de horas).
7. **Liquidación de profesores**: liquidación mensual por profesor = horas dictadas del mes × tarifa por hora vigente; estados Pendiente / Pagada; al marcarla pagada se genera el egreso en cuenta corriente.
8. **Cuenta corriente**: registro de todos los movimientos de dinero — ingresos automáticos por pagos de cuotas, egresos automáticos por liquidaciones pagadas y egresos manuales tipificados (Gasto / Retiro) con descripción; saldo acumulado; filtros por tipo, categoría y rango de fechas; navegación desde cada movimiento a su origen.
9. **Dashboard de inicio (KPIs, foco financiero)**: tarjetas con ingresos del mes, egresos del mes, resultado del mes, saldo de cuenta corriente, alumnos activos y cuotas vencidas; gráficos de ingresos vs egresos de los últimos 12 meses, saldo acumulado y comparativo anual; distribución de alumnos activos por plan.

### No incluido (exclusiones)

- Pasarela de pagos online (Mercado Pago, tarjetas): los pagos se registran manualmente por el administrador.
- Reserva/agenda de clases y control de asistencia de alumnos: las clases dictadas se registran solo a efectos de liquidar profesores.
- Notificaciones por correo o WhatsApp a alumnos (recordatorios de vencimiento, avisos).
- Acceso de alumnos o profesores al sistema (rol único Administrador).
- Migración de datos desde planillas o sistemas anteriores (la carga inicial de alumnos/planes la realiza el administrador desde las pantallas del sistema).
- Facturación electrónica AFIP/ARCA.
- Aplicación móvil nativa (el sitio es responsive).
- Configuración y costo de servidor/hosting (cubierto por plan de mantenimiento anual).
- Cambios de alcance posteriores al inicio (se presupuestan aparte).

### Dependencias del cliente

- Definición de los nombres y precios iniciales de los 5 planes.
- Definición del día de vencimiento de las cuotas (ej.: día 10 de cada mes).
- Listado de profesores con sus tarifas por hora.
- Carga inicial de alumnos y suscripciones a cargo del administrador (el sistema se entrega con los catálogos sembrados).

## 3. Casos de uso principales

| # | Caso de uso | Actor | Resumen |
|---|---|---|---|
| CU-01 | Iniciar sesión | Admin | Acceso con usuario y contraseña; redirección al dashboard. |
| CU-02 | Configurar planes | Admin | Edición de los 5 planes (nombre, horas semanales, precio mensual). Cambio de precio rige hacia adelante. |
| CU-03 | Gestionar alumnos | Admin | ABM de alumnos con baja lógica; un alumno con historial nunca se elimina físicamente. |
| CU-04 | Suscribir alumno a un plan | Admin | Alta de suscripción (alumno + plan + fecha de inicio). Máximo una suscripción activa por alumno. |
| CU-05 | Cambiar / pausar / finalizar suscripción | Admin | Cambio de plan (cierra vigencia y abre nueva), pausa y finalización con fecha; historial visible. |
| CU-06 | Generar cuotas del período | Admin | Genera las cuotas del mes para todas las suscripciones activas, con monto congelado del plan vigente. Operación idempotente: no duplica cuotas ya generadas. |
| CU-07 | Registrar pago de cuota | Admin | Marca la cuota como pagada (fecha y medio de pago) y genera el ingreso en cuenta corriente. |
| CU-08 | Consultar deudores | Admin | Listado de cuotas vencidas/pendientes por alumno, con antigüedad de la deuda. |
| CU-09 | Gestionar profesores | Admin | ABM de profesores con tarifa por hora y baja lógica. |
| CU-10 | Registrar clases dictadas | Admin | Carga de clases (profesor, fecha, horas); editable mientras no estén liquidadas. |
| CU-11 | Liquidar profesor | Admin | Genera la liquidación mensual (Σ horas × tarifa vigente); al marcarla Pagada genera el egreso en caja y bloquea las clases incluidas. |
| CU-12 | Registrar egreso manual | Admin | Alta de gasto o retiro (categoría, fecha, importe, descripción) con impacto directo en cuenta corriente. |
| CU-13 | Consultar cuenta corriente | Admin | Movimientos con saldo acumulado, filtros por tipo/categoría/fechas y navegación al origen (cuota o liquidación). |
| CU-14 | Consultar dashboard | Admin | Pantalla de inicio con KPIs y gráficos financieros del mes y evolución histórica. |

## 4. Criterios de aceptación (verificables)

**CU-02 — Planes**
- Existen exactamente los planes de 1, 2, 3, 4 y 5 horas semanales, cada uno con precio propio.
- Al cambiar el precio de un plan, las cuotas ya generadas conservan su monto original; las cuotas generadas después usan el precio nuevo.

**CU-04 / CU-05 — Suscripciones**
- No se puede dar de alta una segunda suscripción activa para un alumno con suscripción vigente.
- El cambio de plan cierra la suscripción anterior con fecha de fin y crea una nueva; el historial de suscripciones del alumno muestra ambas.
- Una suscripción pausada o finalizada no genera cuotas en los períodos siguientes.

**CU-06 / CU-07 / CU-08 — Cuotas y pagos**
- La generación de cuotas del período crea exactamente una cuota por suscripción activa; ejecutarla dos veces no duplica cuotas.
- El monto de la cuota es el precio del plan vigente al momento de la generación.
- Una cuota Pendiente cuya fecha de vencimiento pasó se muestra como Vencida (sin proceso nocturno: estado derivado por fecha).
- Registrar el pago marca la cuota Pagada, registra fecha y medio de pago y crea un único ingreso en cuenta corriente por el monto de la cuota.
- Una cuota pagada no se puede volver a pagar; su anulación requiere motivo y revierte el movimiento de caja.
- El listado de deudores muestra todos los alumnos con cuotas vencidas y el total adeudado por alumno.

**CU-10 / CU-11 — Clases y liquidaciones**
- Una clase dictada se puede editar o eliminar solo mientras no esté incluida en una liquidación.
- La liquidación del mes de un profesor = Σ horas de sus clases del mes × su tarifa por hora vigente al generar; el monto queda congelado en la liquidación.
- Al marcar la liquidación como Pagada se genera un único egreso en cuenta corriente (categoría Pago a profesor) y la liquidación queda inmutable.
- No se puede generar dos veces la liquidación del mismo profesor y mes.

**CU-12 / CU-13 — Cuenta corriente**
- Saldo = Σ ingresos − Σ egresos; el saldo mostrado coincide con la suma de los movimientos listados.
- Todo movimiento automático (pago de cuota, liquidación pagada) referencia su origen y permite navegar a él.
- Los egresos manuales requieren categoría (Gasto / Retiro), importe > 0 y descripción.

**CU-14 — Dashboard**
- Los KPIs del mes (ingresos, egresos, resultado) coinciden con la suma de movimientos de caja del mes.
- El saldo de la tarjeta de caja coincide con el saldo de la cuenta corriente.
- Meses sin movimientos se muestran como "sin datos del período", nunca con errores de división por cero.

## 5. Permisos, estados y validaciones

**Roles**
- **Administrador**: único rol operativo; acceso total a todas las pantallas.
- (Super usuario interno del proveedor para soporte: fuera de la documentación al cliente.)

**Estados**
- Suscripción: `Activa` → `Pausada` (reversible) → `Finalizada` (terminal).
- Cuota: `Pendiente` → `Pagada`; `Vencida` = Pendiente con vencimiento pasado (derivado, no persistido). Anulación de pago con motivo.
- Liquidación de profesor: `Pendiente` → `Pagada` (inmutable; reapertura solo con motivo auditado).

**Validaciones críticas**
- Importes ≥ 0; horas de clase > 0; precio de plan > 0; tarifa de profesor > 0.
- Una suscripción activa por alumno; una cuota por suscripción y período; una liquidación por profesor y período.
- Bajas lógicas en alumnos, profesores y planes con historial.

## 6. Banderas para arquitectura y presupuesto

- Migración EF: **Sí** (esquema nuevo completo + seed de planes y roles).
- Integración externa: **No** (sin SMTP, sin pasarelas, sin APIs).
- Máquina de estados: **Sí, acotada** (suscripción, cuota, liquidación).
- Migración de datos: **No** (exclusión estándar; carga inicial manual por el administrador).
- Reportes/exportaciones: solo dashboard (sin export Excel en alcance base).

## Historial de ajustes
- 2026-06-11: discovery + análisis inicial v1 sobre el pedido del cliente y las tres decisiones de relevamiento confirmadas (liquidación de profesores por clases dictadas, control de morosidad por estado de cuota, dashboard con foco financiero). 14 casos de uso, alcance base de 9 bloques funcionales. Aprobado para diseño.
