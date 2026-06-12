# Propuesta de desarrollo — Sistema de Gestión para Escuela de Yoga
**OlvidataSoft · Junio 2026**

---

## 1. Descripción general

Sistema web de gestión para la escuela de yoga, accesible desde cualquier navegador (computadora, tablet o celular), con usuario y contraseña. Reemplaza el manejo informal actual por una plataforma que centraliza alumnos, suscripciones, cobranzas, pagos a profesores y la caja de la escuela.

El desarrollo se entrega en **dos etapas**, para que la escuela empiece a operar cuanto antes con lo esencial:

- **Etapa 1 — MVP (suscripciones y cobranza)**: planes de entrenamiento de 1 a 5 horas semanales, alumnos, suscripciones y cuotas mensuales con control de pagos, vencimientos y deudores. Con esta etapa la escuela ya gestiona su negocio en el sistema.
- **Etapa 2 — Profesores, caja y dashboard**: registro de clases dictadas y liquidación de profesores, cuenta corriente con todos los movimientos de dinero y el dashboard de inicio con los indicadores clave.

Cada etapa se cotiza y se abona por separado; la Etapa 2 puede contratarse junto con la primera o al terminar el MVP.

---

## 2. Usuarios y accesos

| Perfil | Cantidad | Qué puede hacer |
|---|---|---|
| **Administrador** | 1 | Acceso total: configurar planes, gestionar alumnos y suscripciones, generar y cobrar cuotas, registrar clases, liquidar profesores, registrar gastos y retiros, consultar la cuenta corriente y el dashboard |

El sistema es de uso exclusivo del administrador: los alumnos y profesores no acceden.

---

## 3. Etapa 1 — MVP: suscripciones y cobranza

### 3.1 Acceso y cuenta del administrador

- Ingreso al sistema con usuario y contraseña.
- Cambio y recuperación de contraseña.

### 3.2 Planes de entrenamiento

- Cinco planes: **1, 2, 3, 4 y 5 horas por semana**, cada uno con su nombre y su **precio mensual propio**, editable en cualquier momento.
- Cuando se cambia el precio de un plan, el cambio rige hacia adelante: **las cuotas ya generadas conservan su valor original**.

### 3.3 Gestión de alumnos

- Alta, edición y desactivación de alumnos (datos personales, contacto, observaciones).
- Buscador por nombre o teléfono.
- La ficha de cada alumno muestra su plan actual, el historial de suscripciones y el estado de sus cuotas.
- Los alumnos con historial nunca se eliminan: se desactivan y conservan todos sus datos.

### 3.4 Suscripciones a planes

- Suscripción de un alumno a un plan, con fecha de inicio.
- **Cambio de plan** en cualquier momento, conservando el historial de planes anteriores.
- **Pausa y reactivación** de la suscripción (durante la pausa no se generan cuotas) y **finalización** cuando el alumno deja la escuela.
- Un alumno tiene una sola suscripción activa a la vez.

### 3.5 Cuotas mensuales, pagos y deudores

- Con un clic, el sistema **genera las cuotas del mes** de todos los alumnos con suscripción activa, cada una con el precio de su plan y la fecha de vencimiento configurada. La operación es segura: repetirla no duplica cuotas.
- El administrador **registra el pago** de cada cuota (fecha y medio de pago).
- Las cuotas no pagadas a su vencimiento se muestran automáticamente como **vencidas**, sin intervención manual.
- Pestaña de **deudores**: todos los alumnos con cuotas vencidas, cuánto deben y desde cuándo.
- Un pago registrado por error puede anularse dejando registrado el motivo.

---

## 4. Etapa 2 — Profesores, caja y dashboard

### 4.1 Profesores y registro de clases dictadas

- Alta, edición y desactivación de profesores, cada uno con su **tarifa por hora**.
- Carga rápida de las **clases dictadas**: profesor, fecha y cantidad de horas.
- Total de horas del mes por profesor siempre visible.

### 4.2 Liquidación de pagos a profesores

- El sistema **calcula automáticamente** la liquidación mensual de cada profesor: horas dictadas en el mes × su tarifa por hora.
- Estados **Pendiente / Pagada**: al marcarla como pagada se registra la fecha y el egreso aparece automáticamente en la cuenta corriente.
- Una liquidación pagada queda protegida contra cambios, igual que las clases incluidas en ella.

### 4.3 Cuenta corriente

- Todos los movimientos de dinero de la escuela en una sola pantalla:
  - **Ingresos automáticos** por cada pago de cuota (incluidos, de manera retroactiva, los pagos registrados durante la Etapa 1: la caja nace completa).
  - **Egresos automáticos** por cada liquidación de profesor pagada.
  - **Egresos manuales**: gastos y retiros, con fecha, importe y descripción.
- **Saldo actual** siempre visible y saldo acumulado línea por línea.
- Filtros por tipo de movimiento, categoría y rango de fechas.
- Desde cada movimiento automático se puede ir directo a la cuota o liquidación que lo originó.

### 4.4 Dashboard de inicio (indicadores)

Al ingresar al sistema, un tablero con los indicadores clave:

- **Tarjetas del mes**: ingresos, egresos, resultado, saldo de caja, alumnos activos y cuotas vencidas (cantidad y monto).
- **Gráficos**:
  - Ingresos vs egresos de los últimos 12 meses.
  - Evolución del saldo de caja.
  - Comparativo anual de ingresos y egresos.
  - Distribución de alumnos activos por plan.
- Tabla con los últimos movimientos de caja.
- Los meses sin actividad se muestran como "sin datos del período", nunca con errores.

---

## 5. Qué no incluye este desarrollo

- Cobro online (Mercado Pago, tarjetas): los pagos se registran manualmente por el administrador.
- Reserva de clases, agenda y control de asistencia de alumnos.
- Envío de recordatorios o avisos a alumnos por correo o WhatsApp.
- Acceso de alumnos o profesores al sistema.
- Carga de datos históricos desde planillas anteriores (la carga inicial la realiza el administrador desde las pantallas del sistema).
- Facturación electrónica ante AFIP / ARCA.
- Aplicación móvil nativa (el sistema es totalmente usable desde el navegador del celular).
- Cambios de alcance posteriores al inicio (se presupuestan por separado).

---

## 6. Precio por área funcional

### Etapa 1 — MVP: suscripciones y cobranza

| Área | Precio |
|---|---:|
| Acceso y cuenta del administrador | USD 33 |
| Planes de entrenamiento (1 a 5 horas semanales) | USD 44 |
| Gestión de alumnos | USD 98 |
| Suscripciones a planes | USD 109 |
| Cuotas mensuales, pagos y deudores | USD 152 |
| **Subtotal Etapa 1** | **USD 436** |

### Etapa 2 — Profesores, caja y dashboard

| Área | Precio |
|---|---:|
| Profesores y registro de clases dictadas | USD 101 |
| Liquidación de pagos a profesores | USD 101 |
| Cuenta corriente (ingresos y egresos) | USD 84 |
| Dashboard de indicadores | USD 84 |
| **Subtotal Etapa 2** | **USD 370** |

| | |
|---|---:|
| **Total del proyecto (Etapa 1 + Etapa 2)** | **USD 806** |

**Mantenimiento anual — Plan PRO: USD 300/año.** Incluye servidor (hosting), actualizaciones de seguridad, soporte por WhatsApp y 1 ronda de ajuste por año. Rige desde la puesta en funcionamiento de la Etapa 1; es un servicio continuo posterior al desarrollo y no cubre cambios funcionales nuevos.

---

## 7. Condiciones generales

- El precio incluye desarrollo, pruebas internas y puesta en funcionamiento de cada etapa (la Etapa 1 se entrega con los 5 planes ya configurados).
- Moneda: dólares estadounidenses.
- Forma de pago: **50 % al inicio y 50 % a la entrega de cada etapa**.
- La Etapa 2 puede contratarse junto con la Etapa 1 o al finalizar el MVP.
- Dependencias del cliente: nombres y precios iniciales de los planes, día de vencimiento de las cuotas y, para la Etapa 2, listado de profesores con sus tarifas.
- El plazo de entrega de cada etapa se define en el acuerdo inicial según disponibilidad acordada.
