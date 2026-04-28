# Propuesta de desarrollo — Sistema de Gestión Ganadera
**OlvidataSoft · Abril 2026**

---

## Descripción general

Sistema web de gestión para un establecimiento ganadero que centraliza las operaciones de ingresos, egresos y stock de hacienda en una sola plataforma. Accesible desde cualquier navegador, con usuarios y contraseñas, y roles diferenciados según el perfil de cada persona.

El sistema cubre tres ejes principales:
- **Ingresos**: registro de ventas, emisión de facturas y seguimiento de cuotas de cobro.
- **Egresos**: registro de gastos con comprobante adjunto y control de proveedores.
- **Stock**: seguimiento de hacienda por grupo y categoría, con historial completo de movimientos.

Además incluye una **cuenta corriente / caja** unificada, un **tablero anual** con comparativo mensual, y **avisos automáticos** de acreditaciones del día.

---

## Usuarios y accesos

| Perfil | Cantidad máxima | Qué puede hacer |
|---|---|---|
| **Productor** | Hasta 5 | Operar todas las pantallas del sistema: ventas, facturas, gastos, stock, caja y tablero |
| **Administrador (SuperUsuario)** | 1 (proveedor del sistema) | Gestión de usuarios Productor: altas, bajas, modificaciones y restablecimiento de contraseña |

---

## Alcance funcional detallado

### 1. Catálogos operativos

Administración de las listas maestras que utilizan los demás módulos del sistema.

**Grupos de hacienda**
- Alta, edición y baja de grupos. Cada grupo pertenece a una categoría (Vaca, Toro, Vaquillona, Ternera, Ternero).
- Configuración de stock mínimo por grupo con alerta automática no bloqueante.
- La baja de un grupo solo se permite si su stock es cero.
- Los grupos dados de baja se conservan en el historial de movimientos anteriores.

**Rubros de egreso**
- Alta, edición y baja de rubros para clasificar los gastos del establecimiento.

**Proveedores**
- Alta, edición y baja de proveedores con razón social, CUIT y datos de contacto.
- Cada proveedor se clasifica por ámbito: aplica a Ingresos, a Egresos, o a ambos. Los selectores del sistema filtran automáticamente según el contexto de uso.

**Organismos intermediarios**
- Alta, edición y baja de los organismos a través de los cuales se emiten las facturas de venta.

---

### 2. Ventas, facturas y cuotas

**Registro de venta**
- Una venta puede incluir hacienda de varios grupos en una sola operación.
- Motivo de venta configurable: Faena, Vacía o Enfermedad.
- Al registrar la venta, el sistema descuenta el stock correspondiente de cada grupo de forma automática.
- Una venta puede editarse o anularse mientras no tenga factura asociada.

**Emisión de factura**
- Cada venta genera una factura vinculada al organismo intermediario correspondiente.
- La factura registra kilos totales, precio por kilo, IVA aplicado y precio total.
- El IVA se calcula automáticamente y queda registrado de forma permanente con la tasa vigente al momento de la emisión (no se puede cambiar retroactivamente).
- Numeración correlativa automática en formato F-000001, F-000002, etc. — única a nivel del sistema, no editable.
- Una factura puede editarse mientras ninguna de sus cuotas haya sido cobrada o rechazada.

**Cuotas de cobro**
- Al emitir la factura, el sistema genera las cuotas automáticamente según el plazo elegido: 1 cuota a 30 días, 2 cuotas a 30 y 60 días, o 3 cuotas a 30, 60 y 90 días.
- El importe se distribuye en partes iguales; la última cuota absorbe los centavos de redondeo para que la suma siempre sea exacta.
- Si se edita la factura, las cuotas se recalculan automáticamente.
- Estados de cuota: **Pendiente**, **Acreditada**, **Rechazada**.

**Acreditación automática diaria**
- El sistema revisa automáticamente cada noche las cuotas vencidas y las marca como Acreditadas, registrando el ingreso en caja.
- El proceso es idempotente: si se ejecuta más de una vez en el mismo día, no genera duplicados.
- Al iniciar sesión, el Productor recibe un aviso con las acreditaciones del día.

**Rechazo de cuota**
- El Productor puede rechazar manualmente una cuota en estado Pendiente o Acreditada (por ejemplo, ante un cheque rebotado).
- El rechazo registra la cuota como Rechazada y, si ya había ingresado en caja, suspende ese movimiento sin eliminarlo.

**Regularización de rechazo**
- Sobre una cuota rechazada, el sistema ofrece dos opciones:
  - **Corrección de error**: si el rechazo fue un error de carga, se revierte la cuota a Acreditada con la fecha original.
  - **Cobro posterior**: si el cliente finalmente pagó, se registra un nuevo ingreso con la fecha y forma de pago reales (reemplazo de cheque, transferencia, efectivo), preservando el historial del rebote original.

---

### 3. Egresos y comprobantes

- Registro de gastos con fecha, importe, rubro, proveedor, forma de pago (Efectivo, Transferencia, Cheque) y concepto libre.
- Campo de concepto con autocompletado basado en los valores ingresados anteriormente por el usuario.
- Los proveedores del selector se filtran automáticamente según su ámbito (solo proveedores de Egresos o de ambos).
- Opción de adjuntar un comprobante por gasto (PDF, JPG o PNG, hasta 5 MB).
- Cada gasto registrado impacta automáticamente en la caja como un egreso acreditado.

---

### 4. Stock de hacienda

**Categorías y grupos**
- El stock se lleva a nivel de grupo (no de categoría). El stock por categoría es una suma derivada que el sistema calcula y muestra.
- Categorías disponibles: Vaca, Toro, Vaquillona, Ternera, Ternero.

**Tipos de movimientos**
- **Stock inicial**: carga manual única por grupo para registrar la hacienda existente al momento de arrancar el sistema.
- **Nacimiento** y **Compra**: ingresos de animales a un grupo.
- **Muerte**: egreso de animales de un grupo.
- **Venta**: egreso automático vinculado al registro de venta (no se carga manualmente).
- **Compensación intra-categoría**: traslado de animales entre dos grupos de la misma categoría.
- **Compensación inter-categoría**: traslado de animales entre grupos de categorías distintas, siguiendo una tabla fija de transiciones permitidas (por ejemplo: Ternera puede pasar a Vaquillona, Vaquillona a Vaca, Ternero a Toro). Combinaciones no permitidas quedan bloqueadas.

**Consultas de stock**
- Vista del stock actual por grupo, con totalización por categoría.
- Historial completo de movimientos con filtros por fecha, tipo y grupo.

---

### 5. Caja y cuenta corriente

- Vista unificada de todos los movimientos de dinero del establecimiento: cobros de cuotas y gastos registrados.
- Saldo calculado en tiempo real sobre los movimientos acreditados (los pendientes no computan).
- Filtros por fecha, estado y tipo de movimiento.
- Cada movimiento incluye un acceso directo al documento de origen (cuota, factura o gasto).

---

### 6. Tablero anual

- Resumen de ingresos y egresos con desglose mes a mes.
- Selector de año para ver el ejercicio actual o el anterior en forma comparativa.
- Filtros por categoría y por grupo de hacienda.
- Incluye historia completa: los grupos dados de baja siguen apareciendo en los períodos en que tuvieron actividad, identificados visualmente como inactivos.

---

### 7. Avisos y novedades

- Al iniciar sesión, el Productor ve un listado con las cuotas acreditadas automáticamente durante el día.
- Los avisos son internos del sistema (no se envían por correo ni por otros canales externos).

---

### 8. Gestión de usuarios

- El Administrador (SuperUsuario) puede dar de alta, modificar, desactivar y restablecer la contraseña de cada usuario Productor.
- El sistema admite hasta 5 usuarios Productor activos simultáneamente.

---

## Qué no incluye este desarrollo

- Facturación electrónica ante AFIP.
- Aplicación móvil.
- Migración de datos históricos desde otro sistema u hoja de cálculo.
- Integraciones con sistemas de terceros (bancos, contabilidad externa, etc.).
- Trazabilidad individual de animales por caravana o RENSPA (queda como segunda etapa).
- Retenciones impositivas.
- Envío de correos electrónicos o notificaciones externas.

---

## Precio por módulo

| Módulo | Precio |
|---|---:|
| Catálogos operativos (grupos, rubros, proveedores, organismos) | USD 236 |
| Gestión de usuarios Productor | USD 88 |
| Stock y movimientos de hacienda | USD 212 |
| Ventas, facturas y cuotas | USD 272 |
| Rechazos, regularización y acreditación automática | USD 152 |
| Egresos y comprobantes | USD 112 |
| Caja y cuenta corriente | USD 70 |
| Tablero anual | USD 70 |
| **Total del proyecto** | **USD 1.212** |

---

## Condiciones generales

- El precio incluye desarrollo, pruebas internas y puesta en funcionamiento.
- El sistema funciona en un servidor web estándar (hosting o servidor propio del cliente).
- Moneda: dólares estadounidenses.
- Forma de pago: a convenir al inicio del proyecto.
- El plazo de entrega se define en el acuerdo inicial según disponibilidad acordada.

---

*Propuesta válida por 30 días desde la fecha de emisión.*
