# Análisis Funcional — Sistema de Gestión Ganadera

Versión: **v12** (consolidada y validada por el agente `1 - analista-funcional`)
Agente: `analista-funcional` (`C:\Sistemas\Agentes-IA\.github\agents\analista-funcional.agent.md`)
Conversación: `2025-11-ganaderia-blankproject`
Proyecto: BlankProject (ASP.NET Core **MVC**, .NET 10, EF Core 10, MySQL 8, Identity, Serilog)
Repositorio de esta versión: **`C:\Sistemas\ganaderia - emo`** (cambio de v11/v12 exclusivo de este cliente; NO aplica a `ganaderia - fausto`).
Alcance: documento funcional. **No** define implementación técnica detallada.

---

## 0. Salida mínima del agente

> Contrato exigido por `analista-funcional.agent.md` (salida en 5 puntos). El detalle se desarrolla en §1–§18.

### 0.1 Alcance funcional resumido

Sistema de gestión para un productor ganadero argentino con **tres ejes**: **Ingresos** (Ventas → Facturas → Cuotas → Caja), **Egresos** (compras a proveedor con **pagos múltiples**: efectivo, transferencia y cheque diferido, con posible pago compensatorio) y **Stock** (por Grupo, con compensaciones intra/inter-categoría según matriz cerrada). Transversales: **Cuenta Corriente / Caja** y **Dashboard anual mensualizado**. Soporta hasta **5 usuarios Productor** + **1 SuperUsuario**. Catálogos ABM: Grupo, Rubro, Proveedor (con ámbito), Organismo intermediario. Job diario idempotente de acreditación de Cuotas de venta **y de Pagos de egreso con cheque diferido** + notificación in-app. **(v12)** Autocomplete de texto libre con sugerencias (Concepto de Egreso, Motivo de Factura de venta) implementado con **Select2**, no con `<datalist>` nativo.

### 0.2 Impacto técnico por capa

- **Presentación (MVC)**: 11 áreas de vistas (Ventas, Facturas, Cuotas, Egresos, Stock, MovimientosStock, Caja, Dashboard, Catálogos×4, Novedades), formularios con validación en español, selectores filtrados, uploader de comprobante, bandeja de novedades, autorización por rol. Egresos pasa de alta con forma de pago única a alta con **grilla de pagos múltiples** (agregar/quitar líneas de pago) + pantallas de rechazo/regularización de cheque diferido.
- **Negocio (Application + Services)**: reglas de ciclo de vida (Venta/Factura/Cuota), cálculo de IVA con snapshot inmutable, generación/regeneración de cuotas, matriz de transiciones, compensaciones, baja lógica con `stock==0`, regularización Opción 3a/3b (**ahora también para Pagos de egreso**), job diario idempotente (**extendido a Pagos de egreso con cheque**), autocomplete normalizado, filtrado de proveedores por ámbito, límite de 5 Productores, validación de suma de pagos == importe del egreso.
- **Datos (EF Core + MySQL)**: entidades nuevas bajo `Domain/Entities/Ganaderia`, snapshot `TasaImpuestoAplicada` en Factura, `MovimientoStock` con origen/destino nullables, `MovimientoCaja` con estado y FK polimórfica al documento de origen (**ahora incluye pago de egreso**), almacenamiento de archivo de comprobante fuera de DB, baja lógica vía `SoftDestroyable`. Nueva entidad **`EgresoPago`** (1:N con `Egreso`) reemplaza el campo único `FormaDePago` de `Egreso`.

### 0.3 Riesgos y supuestos clave

- **R16** Recálculo de cuotas al cambiar plazo en la factura · **R18** Mantenimiento de la matriz si aparecen nuevas categorías · **R20/R24** Concurrencia en venta multi-grupo · **R22** Variantes ortográficas en autocomplete de concepto · **R23** Matriz cerrada requiere deploy para extenderse · **R13** Movimientos en `Pendiente` por rechazo sin regularizar · **R25** Suma de pagos de un Egreso debe cuadrar exactamente contra el importe total · **R26** Job diario ahora corre dos colecciones (Cuotas + Pagos de egreso); debe mantener idempotencia independiente por colección.
- Supuestos S1–S30 consolidados (ver v10) + **S31–S34** (v11): pagos de Egreso admiten múltiples líneas con distinta forma de pago; cheque diferido de Egreso replica el ciclo Pendiente→Acreditado del job diario de Cuotas; rechazo/regularización de cheque de Egreso replica Opción 3a/3b de Cuotas; no se agrega edición de Egreso (se mantiene alta + anulación).

### 0.4 Pruebas mínimas requeridas

Casos **PF1–PF61** funcionales + **PV1–PV16** de validación/borde, detallados en §16. Cubren ciclos de vida, cálculos de IVA y cuotas, job diario idempotente (Cuotas y Pagos de egreso), rechazo y regularización (3a/3b) de Cuotas y de Pagos de egreso, compensaciones intra/inter con matriz, baja lógica, autocomplete, filtrado por ámbito, autorización por rol, formato/tamaño de comprobante, numeración correlativa de Factura, stock inicial como movimiento explícito, visibilidad histórica de Grupos inactivos y **pagos múltiples de Egreso con cheque diferido**.

### 0.5 Checklist de salida para merge

Ver **§17** (checklist completo, incluye ítems nuevos de v11 sobre pagos múltiples de Egreso).

---

## Nota sobre la versión

- **v8** — Cerró categoría `Ternero`, comprobante 1 archivo × 5 MB, Organismo intermediario como ABM.
- **v9** — Validación por el agente `analista-funcional`: se corrigió el stack (MVC, no Razor Pages) y se agregó el bloque §0 con el contrato del agente. Sin cambios de alcance funcional.
- **v11** — Egresos pasa de "forma de pago única, acreditación inmediata" a **pagos múltiples por Egreso** (efectivo, transferencia, cheque diferido y pago compensatorio), con ciclo de vida de cheque diferido (Pendiente → Acreditado vía job diario) y rechazo/regularización (Opción 3a/3b), simétrico al ya existente para Cuotas de venta. Cambio exclusivo del repositorio `ganaderia - emo`.
- **v12** — Autocomplete de "Concepto" (Egresos) migra de `<datalist>` nativo a **Select2** (estándar UI del estudio). En Facturas de venta, `Motivo` deja de ser enum cerrado (`Faena`/`Vacía`/`Enfermedad`) y pasa a **texto libre con autocomplete Select2** sobre motivos previamente registrados, mismo patrón que Concepto de Egresos. Cambio exclusivo del repositorio `ganaderia - emo`.

---

## 1. Contexto del negocio

Sistema solicitado por un productor ganadero argentino para ordenar su operatoria diaria y soportar la toma de decisiones. Se estructura en tres ejes principales:

1. **Ingresos** (ventas de hacienda, facturación y cobranza en cuotas).
2. **Egresos** (gastos y costos de producción).
3. **Stock** (hacienda, movimientos y trazabilidad por grupo/lote).

Transversales: **Cuenta Corriente / Caja** y **Dashboard**.

---

## 2. Usuarios y roles

- **Productor**: usuario operativo. Hasta **5 cuentas**. Acceso a todas las pantallas operativas.
- **SuperUsuario**: administrador del sistema (proveedor). Acceso exclusivo a la pantalla de administración de usuarios Productor (alta, baja, modificación, reset de contraseña, activar/desactivar).

---

## 3. Módulo Ingresos — Ventas

### 3.1 Venta
- **Motivo** — **(v12)** deja de ser enum cerrado. Pasa a ser **texto libre** (obligatorio, máx. 200 caracteres) con **autocomplete Select2** sobre motivos previamente registrados en cualquier Factura de venta (histórico distinct, normalizado: trim + comparación case-insensitive — mismo patrón que Concepto de Egreso, §4.1). Los tres valores históricos (`Faena`, `Vacía`, `Enfermedad`) quedan disponibles como sugerencias iniciales (se migran como texto) pero el usuario puede escribir cualquier motivo nuevo.
- Detalle multi-línea: cada línea referencia un **Grupo** y una **Cantidad**.
- Una venta puede descontar de **varios grupos** y de **distintas categorías** en líneas separadas.
- Relación **1 venta ↔ 1 factura**.

### 3.2 Factura
- Emitida por un **Organismo intermediario** (variable).
- **Numeración**: correlativo **interno único del sistema** con formato legible `F-000123` (padding a 6 dígitos). Único a nivel global del sistema, independiente del Organismo intermediario. Generado automáticamente al emitir la factura, no editable.
- Atributos: número (`F-000123`), categoría, kilos totales, peso promedio por unidad (calculado = kilos/unidades), precio por kg, precio total, precio total con impuestos, fecha.
- **Impuestos calculados por el sistema**:
  - Enum `TasaImpuesto`: `IVA21` (default), `IVA10_5` (preparado para uso futuro).
  - Fórmula: `TotalConImpuestos = Total + Total * Tasa`.
  - La **tasa aplicada se persiste en la factura** (snapshot) y es **inmutable**.
  - **No** se contemplan retenciones.

### 3.3 Cuotas
- Generadas automáticamente al emitir la factura, según plazo:
  - `30 días` → 1 cuota (a +30).
  - `60 días` → 2 cuotas (a +30 y +60).
  - `90 días` → 3 cuotas (a +30, +60 y +90).
- **Distribución en partes iguales** con redondeo a 2 decimales:
  - `ImporteBase = Round(TotalConImpuestos / N, 2)` para las primeras N−1 cuotas.
  - `ÚltimaCuota = TotalConImpuestos − (N−1) * ImporteBase` (absorbe la diferencia).
  - Suma exacta = TotalConImpuestos.
- **Estados** (enum `EstadoCuota`): `Pendiente`, `Acreditada`, `Rechazada`.

### 3.4 Ciclo de vida
| Entidad | Editable / Anulable | Condición |
|---|---|---|
| Venta | Sí | Mientras no tenga factura asociada |
| Factura | Sí | Mientras **todas** las cuotas estén en `Pendiente` |
| Factura | No | Si al menos una cuota está `Acreditada` o `Rechazada` |
| Cuota | Rechazo manual | Desde `Pendiente` o `Acreditada` |

- Al editar una factura con todas las cuotas `Pendiente`, las cuotas se **recalculan** (importes y fechas si cambió el plazo; se regeneran si cambia la cantidad).

### 3.5 Acreditación automática
- **Job programado diario**.
- Al vencer la fecha de una cuota `Pendiente`, la marca como `Acreditada` y crea el **Movimiento de Caja** asociado en estado `Acreditado`.
- **Notificación in-app** (no email) en pantalla/bandeja de novedades al iniciar sesión, listando los pagos acreditados del día.
- **Idempotente**: ejecutar el job dos veces el mismo día no duplica movimientos ni reactiva movimientos revertidos por rechazo.

### 3.6 Rechazo de cuota
- Acción manual del Productor sobre cuotas en `Pendiente` o `Acreditada`.
- Efecto:
  - Cuota pasa a `Rechazada` (permanece como registro histórico).
  - Si existía movimiento de caja asociado (cuota estaba `Acreditada`) → el movimiento pasa a `Pendiente` y **no computa en saldo**.
  - **No se genera contramovimiento** ni se elimina nada.

### 3.7 Regularización de rechazo (Opción 3 — adoptada)
Acción explícita sobre una cuota `Rechazada`. Dos variantes:

**a) Corrección de error de carga**
- Cuota vuelve a `Acreditada`.
- Movimiento de caja existente vuelve a `Acreditado` con **fecha original**.
- No se crea movimiento nuevo.
- Uso: cuando el rechazo fue cargado por error (nunca hubo rebote real).

**b) Cobro posterior efectivo**
- Cuota permanece en `Rechazada` (preserva auditoría del rebote).
- Movimiento de caja original permanece en `Pendiente`.
- Se **crea un nuevo movimiento de caja** en estado `Acreditado`, vinculado a la cuota, con **fecha y forma de pago reales**.
- Uso: cuando el deudor finalmente pagó (reemplazo de cheque, transferencia, efectivo, etc.).

Resumen tabular:

| Acción | Estado Cuota | Movimiento original | Nuevo movimiento |
|---|---|---|---|
| Rechazo | `Rechazada` | Pasa a `Pendiente` | No |
| Regularización – error de carga | `Acreditada` | Vuelve a `Acreditado` (fecha original) | No |
| Regularización – cobro posterior | `Rechazada` | Queda `Pendiente` | `Acreditado` con fecha real |
| Sin acción | `Rechazada` | `Pendiente` | No |

### 3.8 Saldo de Cuenta Corriente
- Invariante: `Saldo = Σ MovimientoCaja donde Estado == Acreditado`.
- Movimientos en `Pendiente` no computan.

---

## 4. Módulo Egresos — Compras a proveedor

> **v11**: se reemplaza el modelo de "forma de pago única con acreditación inmediata" por **pagos múltiples por Egreso**. Motivo del cliente: una compra suele pagarse combinando uno o varios cheques diferidos (que no siempre cubren el importe total) más un pago compensatorio (efectivo/transferencia) por la diferencia.

### 4.1 Atributos del Egreso (cabecera — se mantienen)
- Fecha (fecha de la compra / factura de compra)
- Importe total
- **Rubro** (FK a catálogo ABM de Rubros de egreso — entidad propia)
- **Concepto / Motivo**: string libre con **autocomplete** basado en valores previamente ingresados por el usuario (historial distinct, con normalización básica: trim y comparación case-insensitive). Incluye Descripción. **(v12)** El widget de autocomplete pasa de `<datalist>` nativo a **Select2** (tags + AJAX): mismo comportamiento funcional (escribir y ver sugerencias que matchean, o cargar un valor nuevo), pero con un desplegable confiable en todos los navegadores (el `<datalist>` nativo no siempre refrescaba el popup visible tras poblarse de forma asíncrona — ver `6-qa.md` §12/GAN-004).
- **Proveedor** (FK a catálogo único de Proveedores, filtrado por ámbito)
- **Comprobante** adjunto: PDF / JPG / PNG, opcional, **1 archivo por egreso**, tamaño máximo **5 MB**.
- ~~Forma de pago única~~ → reemplazada por la colección de **Pagos** (§4.2).

### 4.2 Pagos del Egreso (nuevo — entidad `EgresoPago`, 1 Egreso → N Pagos)

Cada Egreso requiere **uno o más pagos**. Cada pago tiene:
- **Forma de pago** (enum cerrado, reutiliza `FormaDePago`): `Efectivo`, `Transferencia`, `Cheque`.
- **Importe** del pago (> 0).
- **Fecha efectiva del pago**: fecha en la que se entrega/emite el pago (para Efectivo/Transferencia coincide con la acreditación real; para Cheque es la fecha de emisión/entrega al proveedor).
- **Fecha de vencimiento** del cheque: **obligatoria únicamente si Forma de pago = Cheque**; es la fecha en la que el cheque diferido se hace efectivo. No aplica a Efectivo/Transferencia.
- **Estado** (enum nuevo `EstadoPagoEgreso`): `Pendiente`, `Acreditado`, `Rechazado`.

**Regla de cierre**: la suma de los importes de todos los pagos de un Egreso debe ser **exactamente igual** al Importe total del Egreso (tolerancia 0, redondeo a 2 decimales). El alta del Egreso se bloquea si no cuadra. Esto habilita el caso de uso del cliente: varios cheques diferidos con fechas distintas que no cubren el total + un pago compensatorio final.

### 4.3 Ciclo de vida del pago

- **Efectivo / Transferencia**: se acreditan **inmediatamente** al guardar el Egreso. Estado inicial = `Acreditado`. Genera de inmediato su Movimiento de Caja egreso en `Acreditado`, con fecha = Fecha efectiva del pago.
- **Cheque**: queda en `Pendiente` al guardar el Egreso (no genera Movimiento de Caja todavía). El **mismo job diario** que hoy acredita las Cuotas de venta vencidas (§3.5) revisa también los Pagos de egreso tipo `Cheque` en `Pendiente` con Fecha de vencimiento `<=` hoy, los pasa a `Acreditado` y crea su Movimiento de Caja egreso en `Acreditado` con fecha = Fecha de vencimiento. Es **idempotente**, igual que hoy para Cuotas.
- La notificación in-app diaria de "acreditaciones del día" (§9) incluye también los cheques de Egreso acreditados por el job, no sólo las Cuotas de venta.

### 4.4 Rechazo de cheque diferido (Egreso)

Acción manual del Productor sobre un Pago de Egreso tipo `Cheque` en estado `Pendiente` o `Acreditado` (cheque rebotado / no debitado por el banco). Efecto, simétrico al rechazo de Cuotas (§3.6):
- El pago pasa a `Rechazado` (permanece como registro histórico).
- Si ya tenía Movimiento de Caja `Acreditado`, ese movimiento pasa a `Pendiente` y **no computa en saldo**.
- **No** se genera contramovimiento ni se elimina nada.

### 4.5 Regularización de rechazo (Egreso — Opción 3, simétrica a Cuotas §3.7)

Acción explícita sobre un Pago `Rechazado`. Dos variantes:

**a) Corrección de error de carga**
- El pago vuelve a `Acreditado`.
- El Movimiento de Caja existente vuelve a `Acreditado` con **fecha original**. No se crea movimiento nuevo.

**b) Pago posterior efectivo**
- El pago permanece en `Rechazado` (preserva auditoría del rebote).
- El Movimiento de Caja original permanece en `Pendiente`.
- Se **crea un nuevo Movimiento de Caja** en estado `Acreditado`, vinculado al pago, con **fecha y forma de pago reales** (por ejemplo: se terminó pagando en efectivo o con un cheque de reemplazo).

### 4.6 Alta / anulación del Egreso

- El Egreso se crea con su(s) pago(s) en una única operación (transaccional): si algún pago es inválido (importe, fecha de vencimiento faltante en cheque, suma que no cuadra) se rechaza el alta completa.
- **No se agrega edición** de Egreso ni de sus pagos individuales en este alcance (se mantiene el comportamiento actual: alta y anulación únicamente).
- Anular un Egreso anula (baja lógica) el Egreso, **todos** sus Pagos y **todos** los Movimientos de Caja asociados a esos pagos, sin importar su estado.

### 4.7 Impacto en Caja / Dashboard
- Cada pago genera (o generará, si es cheque, al vencer) su propio Movimiento de Caja egreso — un Egreso con 3 pagos puede aportar hasta 3 movimientos en fechas distintas, reflejando el impacto real en caja en el momento en que efectivamente ocurre (no en la fecha de la compra).
- Afecta saldo de cuenta corriente y dashboard del mes en que cada pago se acredita.

---

## 5. Módulo Stock

### 5.1 Granularidad
- **Stock por Grupo** (no por Categoría).
- El stock por Categoría es **derivado** (suma de sus Grupos) y no se persiste.
- La **trazabilidad individual** (caravana/RENSPA) queda **fuera de alcance v1** (fase 2).

### 5.2 Categorías (enum cerrado)
`Vaca`, `Toro`, `Vaquillona`, `Ternera`, `Ternero`.

### 5.3 Grupo (Lote)
- Subconjunto de una categoría. Ejemplos: `Vacas – Grupo 1`, `Toros – Grupo 1`.
- Entidad **ABM**: Nombre, Categoría, StockMínimo, Activo.
- Un Grupo pertenece a **una sola Categoría**.
- **Baja lógica** permitida sólo si `stock == 0`.
- Un grupo dado de baja no aparece en selectores operativos pero se conserva en historia.

### 5.4 Stock mínimo
- **Configurado por Grupo**.
- Alerta **no bloqueante** cuando `stock ≤ mínimo`.

### 5.5 Movimientos de Stock (enum `TipoMovimientoStock`)
| Tipo | Origen | Destino | Efecto neto total |
|---|---|---|---|
| Inicial | — | Grupo | +N (carga única de stock inicial por Grupo) |
| Nacimiento | — | Grupo | +N |
| Compra | — | Grupo | +N |
| Muerte | Grupo | — | −N |
| Venta | Grupo | — | −N (vinculado a la venta) |
| Compensación intra-categoría | Grupo A | Grupo B (misma categoría) | 0 |
| Compensación inter-categoría | Grupo A | Grupo B (distinta categoría) | 0 (cambia composición) |

- Compensación se registra como **un único movimiento** con origen y destino.
- El subtipo intra/inter se **infiere** comparando las categorías de los grupos.

### 5.6 Matriz de transiciones inter-categoría
Lista cerrada de pares permitidos `(CategoríaOrigen → CategoríaDestino)`:

| Origen | Destino permitido |
|---|---|
| Ternera | Vaquillona |
| Vaquillona | Vaca |
| Ternero | Toro |

- Toda compensación inter-categoría que no esté en la matriz queda **bloqueada**.
- La matriz es configuración cerrada en v1.

### 5.7 Stock inicial
- Carga manual **una sola vez por Grupo** mediante un **movimiento de stock explícito de tipo `Inicial`** (valor del enum `TipoMovimientoStock`).
- Queda auditable en la grilla de Movimientos de Stock como cualquier otro movimiento.
- **Restricción**: sólo se admite **un** movimiento `Inicial` por Grupo. Intentos posteriores deben rechazarse con error claro.
- No se permite `Inicial` sobre un Grupo dado de baja.

---

## 6. Proveedores

- **Catálogo único** administrable por ABM.
- Atributos mínimos: razón social, CUIT, contacto, **Ámbito**.
- **Ámbito** (enum): `Ingresos`, `Egresos`, `Ambos`.
- Selectores filtran por ámbito según contexto:
  - Gasto → proveedores con ámbito `Egresos` o `Ambos`.
  - Compra de stock / insumos → proveedores con ámbito `Ingresos` o `Ambos`.

---

## 7. Cuenta Corriente / Caja

- Única vista consolidada de **Movimientos de Caja**.
- Movimiento tiene **Estado** (enum `EstadoMovimientoCaja`): `Pendiente`, `Acreditado`.
- Fuentes de movimiento:
  - Cuota acreditada (ingreso, automático por job).
  - Regularización de cuota rechazada — cobro posterior (ingreso, manual).
  - Pago de Egreso en Efectivo/Transferencia (egreso, inmediato en `Acreditado`).
  - Pago de Egreso con Cheque diferido acreditado por vencimiento (egreso, automático por job — v11).
  - Regularización de pago de Egreso rechazado — pago posterior (egreso, manual — v11).
- Cada movimiento navega a su documento de origen (cuota/factura/venta o pago de egreso).
- Saldo = suma de movimientos en `Acreditado`.

---

## 8. Dashboard

- Vista **anual con desglose mensual**.
- **Selector de año**: año actual y año anterior (comparativo).
- Filtros por **Categoría** y por **Grupo**.
- **Grupos dados de baja**: siguen apareciendo en los filtros de años anteriores y en los detalles históricos de Ventas / Movimientos de Caja donde participaron (visibilidad histórica completa). Se sugiere marcarlos visualmente como inactivos.
- **Indicadores específicos**: a definir en **segunda etapa** (backlog fase 2, no bloquea v1).

---

## 9. Notificaciones

- **Canal único: in-app** (pantalla/bandeja de novedades al iniciar sesión).
- **Sin email**, sin canales externos.
- Evento mínimo: pagos acreditados del día por el job automático (Cuotas de venta **y**, desde v11, Pagos de Egreso con cheque diferido vencido).

---

## 10. Enums (listas cerradas)

| Enum | Valores |
|---|---|
| ~~`MotivoVenta`~~ | **(v12) Eliminado.** `Motivo` pasa a texto libre con autocomplete (§3.1); los 3 valores históricos quedan como datos migrados, no como enum. |
| `FormaDePago` (por pago, Ingresos y Egresos) | Efectivo, Transferencia, Cheque |
| `TasaImpuesto` | IVA21, IVA10_5 |
| `EstadoCuota` | Pendiente, Acreditada, Rechazada |
| `EstadoPagoEgreso` (nuevo, v11) | Pendiente, Acreditado, Rechazado |
| `OpcionRegularizacion` (reutilizado en Egresos, v11) | ErrorDeCarga, CobroPosterior |
| `EstadoMovimientoCaja` | Pendiente, Acreditado |
| `TipoMovimientoStock` | Inicial, Nacimiento, Compra, Muerte, Venta, Compensación |
| `CategoriaHacienda` | Vaca, Toro, Vaquillona, Ternera, Ternero |
| `Rol` | Productor, SuperUsuario |
| `ÁmbitoProveedor` | Ingresos, Egresos, Ambos |

---

## 11. Catálogos ABM

- **Grupo** (Stock) — entidad propia, vinculada a Categoría.
- **Rubro** (Egresos) — entidad propia, independiente de Grupo. Mismo patrón ABM, **entidades distintas**.
- **Proveedor** (único, con ámbito).
- **Usuarios Productor** (gestionados sólo por SuperUsuario).
- **Organismo intermediario** (emisor de factura) — entidad **ABM** propia. Atributos mínimos: razón social, CUIT, contacto, activo.

---

## 12. Impacto por capa (resumen)

### Presentación (ASP.NET Core MVC)
- ABM: Grupo, Rubro, Proveedor, Organismo intermediario, Usuarios (SuperUsuario).
- Operativa: Venta (multi-línea con selector de grupo), Factura + Cuotas, **Egreso con grilla de pagos múltiples** (agregar/quitar líneas: forma de pago, importe, fecha efectiva, fecha de vencimiento sólo si Cheque; validación de suma == importe total en cliente y servidor), con autocomplete de concepto y upload de comprobante, Movimientos de Stock (incl. compensación con origen/destino).
- Consulta: Cuenta Corriente, Stock (por Grupo con totalización por Categoría), Dashboard con selector de año y filtros por categoría/grupo.
- Acciones: Rechazo de cuota, Regularización de cuota (Opción 3 a/b), **Rechazo de pago de Egreso (cheque), Regularización de pago de Egreso (Opción 3 a/b — v11)**.
- Bandeja de novedades al iniciar sesión (incluye acreditaciones de Cuotas y de Pagos de egreso con cheque).
- Validaciones de UI: fechas coherentes, importes/cantidades > 0, stock no negativo, formato/tamaño de comprobante, transiciones de compensación según matriz, **fecha de vencimiento obligatoria y >= fecha efectiva cuando Forma de pago = Cheque, suma de pagos == importe del Egreso**.

### Negocio
- Reglas de ciclo de vida (edición/anulación) de Venta, Factura, Cuota.
- Cálculo de impuestos con tasa histórica persistida.
- Generación y recálculo de cuotas con distribución equitativa y redondeo a 2 decimales.
- Job diario idempotente de acreditación de Cuotas **y, desde v11, de Pagos de Egreso con cheque diferido vencido**.
- Regularización de rechazo (Opción 3) de Cuotas **y, desde v11, de Pagos de Egreso**.
- Validación de compensaciones contra matriz de transiciones.
- Baja lógica de Grupo con `stock == 0`.
- Autorización por rol (Productor vs SuperUsuario).
- Filtrado de proveedores por ámbito.
- Autocomplete de conceptos (distinct histórico, normalizado).
- **(v11)** Alta transaccional de Egreso + sus Pagos, con validación de suma exacta de importes.
- **(v11)** Anulación de Egreso propaga baja lógica a todos sus Pagos y Movimientos de Caja asociados.

### Datos
- Entidades: Venta, DetalleVenta, Factura, Cuota, MovimientoCaja, Egreso, **EgresoPago (nueva, v11)**, Rubro, Proveedor, Grupo, MovimientoStock, Categoria (enum), Usuario, OrganismoIntermediario, Comprobante (archivo).
- Snapshot de `TasaImpuestoAplicada` en Factura.
- MovimientoStock con `GrupoOrigen` y `GrupoDestino` (nullables según tipo).
- MovimientoCaja con `Estado` y FK al documento de origen (cuota o **pago de egreso** — v11 reemplaza la FK directa a Egreso por FK al pago).
- Egreso pierde el campo `FormaDePago` único; pasa a exponerlo por cada `EgresoPago`.
- Sin borrado físico; baja lógica donde corresponda.

---

## 13. Riesgos vigentes

- **R16** — Recálculo de cuotas ante cambio de plazo en la factura (60→30 elimina y regenera).
- **R18** — Mantenimiento de la matriz de transiciones si aparecen nuevas categorías.
- **R20/R24** — Concurrencia en venta multi-grupo: validar atómicamente stock al guardar.
- **R22** — Autocomplete de concepto: sensibilidad a variantes ortográficas; aplicar normalización.
- **R23** — Matriz como configuración cerrada requiere deploy para extenderse.
- **R13** — Movimientos en `Pendiente` por rechazo pueden quedar "huérfanos" si nunca se regularizan; considerar filtros/reportes (ahora aplica también a pagos de Egreso).
- **R25** (v11) — Suma de pagos de un Egreso debe cuadrar exactamente contra el importe total; redondeos de 2 decimales pueden generar diferencias de centavos si la UI calcula el compensatorio automáticamente (recomendado: usuario ingresa el compensatorio manual, sistema sólo valida).
- **R26** (v11) — El job diario pasa a procesar dos colecciones (Cuotas de venta y Pagos de Egreso); debe mantener idempotencia y notificación consolidada sin duplicar registros de `JobEjecucion`.
- **R27** (v12) — Migración de `FacturaVenta.Motivo` de enum (`int`) a texto libre (`string`) sobre datos ya cargados en producción: el backfill debe preservar el valor original de cada factura histórica (mapeo `1→"Faena"`, `2→"Vacía"`, `3→"Enfermedad"`), no perderlo ni dejarlo `NULL`.
- **R28** (v12) — Al eliminar el enum `MotivoVenta`, cualquier filtro/reporte futuro que hoy agrupe por esos 3 valores fijos deja de tener una lista cerrada para agrupar (motivo pasa a ser texto libre); no hay uso actual de ese tipo (verificado, `Motivo` no participa en Dashboard ni en ninguna regla de negocio), pero queda como consideración para diseño de reportes futuros.

---

## 14. Supuestos vigentes

- **S1–S30** (consolidados de rondas previas):
  - Un productor, hasta 5 usuarios Productor + 1 SuperUsuario.
  - Moneda única ARS.
  - 1 Venta ↔ 1 Factura.
  - Sin integración fiscal / AFIP. Sin retenciones.
  - Impuesto calculado por sistema; tasa vigente al emitir, inmutable.
  - Cuotas equitativas con redondeo a 2 decimales; última absorbe la diferencia.
  - Stock por Grupo; Categoría derivada.
  - Trazabilidad individual diferida a fase 2.
  - Comprobante de gasto: uno por gasto, PDF/JPG/PNG, 5 MB máx.
  - Rechazo: muta estado, no crea contramovimiento.
  - Regularización: Opción 3 (a/b).
  - Proveedores: catálogo único con ámbito.
  - Grupo (Stock) y Rubro (Egresos): entidades distintas con mismo patrón ABM.
  - Concepto de gasto: string libre con autocomplete.
- **S31–S34** (v11, pagos múltiples de Egreso):
  - **S31** Un Egreso admite 1..N pagos; la suma de importes debe ser exactamente igual al importe total del Egreso (sin tolerancia, redondeo a 2 decimales).
  - **S32** El cheque diferido de Egreso replica el ciclo Pendiente→Acreditado del job diario ya existente para Cuotas de venta (mismo horario, misma tabla `JobEjecucion`, misma notificación in-app consolidada).
  - **S33** El rechazo y la regularización (Opción 3 a/b) de un Pago de Egreso con cheque son simétricos a los de Cuota de venta (§3.6/§3.7), reutilizando el enum `OpcionRegularizacion`.
  - **S34** No se agrega edición de Egreso ni de pagos individuales en este alcance; sólo alta (transaccional, con sus pagos) y anulación (propaga a pagos y movimientos).
- **S35–S37** (v12, autocomplete Select2):
  - **S35** Select2 es la librería estándar del estudio para este tipo de widget (ya cargada globalmente en el layout de `ganaderia - emo`); no se introduce Selectize ni otra dependencia nueva.
  - **S36** El autocomplete de Motivo (Facturas de venta) reutiliza el mismo patrón de sugerencias que Concepto de Egreso: histórico distinct, normalizado (trim + case-insensitive), a nivel organización (no por usuario).
  - **S37** La conversión de `Motivo` a texto libre no afecta ninguna regla de negocio existente: se verificó que el valor de `Motivo` sólo se persiste y se muestra, sin participar en cálculos, filtros de Dashboard, ni condiciones de otros servicios.

---

## 15. Preguntas abiertas remanentes (menores)

1. Indicadores detallados del Dashboard — **confirmado**: pasa a **backlog fase 2**, no bloquea merge de v1.
2. Capa de presentación — **confirmado**: **ASP.NET Core MVC (Controllers + Views)**. La indicación de "Razor Pages" del workspace se considera desactualizada.

### 15.1 Decisiones cerradas en v10

- **PA1 — Numeración de Factura**: correlativo **interno único del sistema**, formato `F-000123` (6 dígitos), global, automático, no editable. Ver §3.2.
- **PA2 — Stock inicial por Grupo**: **movimiento explícito** tipo `Inicial` (nuevo valor del enum `TipoMovimientoStock`), auditable en la grilla de movimientos, uno por Grupo. Ver §5.5 y §5.7.
- **PA3 — Grupo dado de baja**: **visibilidad histórica completa** — aparece en filtros de Dashboard de años anteriores y en detalles de Ventas / Movimientos de Caja históricos. Se oculta sólo de selectores **operativos**. Ver §5.3 y §8.

### 15.2 Preguntas funcionales abiertas

_Ninguna al cierre de v10. Todas las preguntas previas fueron cerradas o diferidas a fase 2._

---

## 16. Pruebas mínimas requeridas

### Funcionales
- PF1 — Venta sin factura: editable y anulable.
- PF2 — Venta con factura: no editable ni anulable.
- PF3 — Factura sin pagos: editable y anulable.
- PF4 — Factura con cuota `Acreditada` o `Rechazada`: bloqueada.
- PF5 — Generación de cuotas: plazo 30→1, 60→2, 90→3.
- PF6 — Cálculo IVA 21% aplicado correctamente.
- PF7 — Cambio a IVA 10,5% refleja total correcto.
- PF8 — Job diario acredita cuotas vencidas + notifica in-app.
- PF9 — Rechazo: cuota `Rechazada`, movimiento a `Pendiente`, saldo consistente.
- PF10 — Gasto con comprobante PDF/JPG/PNG: persistido y recuperable.
- PF11 — Alerta de stock mínimo no bloquea.
- PF12 — Dashboard con selector año actual / anterior.
- PF13 — Roles: Productor sin acceso a admin de usuarios; SuperUsuario con acceso.
- PF14 — Gasto con `Cheque` + comprobante.
- PF15 — Rechazo de cuota `Acreditada`: efectos correctos en caja y dashboard.
- PF16 — Rechazo de cuota `Pendiente`: job no la acredita al vencer.
- PF17 — Job diario idempotente.
- PF18 — ABM Proveedor: alta/edición/baja; baja lógica conserva historia.
- PF19 — Gasto: seleccionar proveedor, forma de pago, adjuntar comprobante.
- PF20 — Editar factura con cuotas todas `Pendiente` recalcula cuotas.
- PF21 — Editar factura con alguna cuota no `Pendiente`: bloqueada.
- PF22 — Cambiar plazo 60→30 regenera cuotas.
- PF23 — Tasa IVA histórica conservada al editar factura vieja.
- PF24 — Productor no accede a admin de usuarios.
- PF25 — SuperUsuario gestiona usuarios.
- PF26 — Notificación in-app de acreditaciones del día al iniciar sesión.
- PF27 — ABM Grupo: alta/edición/baja lógica con stock = 0.
- PF28 — Nacimiento en grupo: sube stock grupo/categoría/total.
- PF29 — Compensación intra: sin cambios en total/categoría.
- PF30 — Compensación inter (transición válida): cambia composición, total estable.
- PF31 — Venta con Grupo: descuenta del grupo indicado + movimiento vinculado.
- PF32 — Compensación con cantidad > stock origen: bloqueada.
- PF33 — Baja de Grupo con stock > 0: bloqueada; con stock = 0: permitida.
- PF34 — Alerta no bloqueante por stock ≤ mínimo del grupo.
- PF35 — Total de categoría = suma de sus grupos en todo momento.
- PF36 — Venta multi-línea con múltiples grupos y categorías.
- PF37 — Compensación inter fuera de matriz: bloqueada.
- PF38 — Compensación inter dentro de matriz: permitida.
- PF39 — Baja de Grupo: condición `stock == 0`.
- PF40 — Autocomplete de concepto sugiere valores previos.
- PF41 — Selector de proveedor en Gasto filtra por `Egresos`/`Ambos`.
- PF42 — Selector de proveedor en Compra filtra por `Ingresos`/`Ambos`.
- PF43 — Cuota $100.000 / 3: 33.333,33 / 33.333,33 / 33.333,34 (suma exacta).
- PF44 — Dashboard filtra por Grupo.
- PF45 — Regularización "cobro posterior" (Opción 3b): cuota queda `Rechazada`, nuevo movimiento `Acreditado` con fecha real.
- PF46 — Regularización "error de carga" (Opción 3a): cuota vuelve a `Acreditada`, movimiento original a `Acreditado`.
- PF47 — Factura nueva recibe número correlativo único con formato `F-000123`, no editable por el usuario.
- PF48 — Dos facturas consecutivas reciben correlativos contiguos sin saltos ni duplicados.
- PF49 — Carga de stock inicial genera un movimiento de tipo `Inicial` auditable en la grilla de Movimientos de Stock.
- PF50 — Intento de segundo movimiento `Inicial` sobre el mismo Grupo: bloqueado con error claro.
- PF51 — Grupo dado de baja con historia previa: aparece en filtros del Dashboard de años anteriores y en el detalle histórico de Caja/Ventas donde participó.
- PF52 — Grupo dado de baja: no aparece en selectores operativos (alta de movimiento, venta, compensación, gasto).
- PF53 — Egreso con un único pago Efectivo: pago queda `Acreditado` y genera Movimiento de Caja `Acreditado` de inmediato.
- PF54 — Egreso con un cheque diferido que cubre el total: pago queda `Pendiente`, sin Movimiento de Caja hasta la fecha de vencimiento.
- PF55 — Egreso con dos cheques diferidos (fechas distintas) + un pago compensatorio en efectivo cuya suma == importe total: alta exitosa, 3 pagos creados con sus estados iniciales correctos.
- PF56 — Egreso donde la suma de pagos no coincide con el importe total: alta bloqueada con error claro, nada se persiste.
- PF57 — Job diario acredita un Pago de Egreso con cheque cuya fecha de vencimiento ya venció, genera su Movimiento de Caja `Acreditado` y notifica in-app junto con las Cuotas de venta acreditadas ese día.
- PF58 — Job diario es idempotente también para Pagos de Egreso con cheque (correrlo dos veces el mismo día no duplica movimientos).
- PF59 — Rechazo de Pago de Egreso con cheque `Acreditado`: pasa a `Rechazado`, su Movimiento de Caja pasa a `Pendiente`, no computa en saldo.
- PF60 — Regularización de Pago de Egreso — error de carga (3a): pago vuelve a `Acreditado`, Movimiento de Caja original vuelve a `Acreditado` con fecha original.
- PF61 — Regularización de Pago de Egreso — pago posterior (3b): pago permanece `Rechazado`, se crea nuevo Movimiento de Caja `Acreditado` con fecha y forma de pago reales.
- PF62 — (v12) Autocomplete Select2 de Concepto en Egresos: escribir un término con coincidencias muestra el desplegable con las opciones filtradas; seleccionar una opción la carga en el campo.
- PF63 — (v12) Autocomplete Select2 de Concepto en Egresos: escribir un valor sin coincidencias previas permite cargarlo igual como texto nuevo (no obliga a elegir de la lista).
- PF64 — (v12) Factura de venta: campo Motivo con autocomplete Select2 sugiere motivos previamente registrados en cualquier Factura de venta.
- PF65 — (v12) Factura de venta: Motivo acepta un valor nuevo (no limitado a Faena/Vacía/Enfermedad).
- PF66 — (v12) Facturas de venta históricas (pre-migración) muestran su Motivo original como texto (`Faena`/`Vacía`/`Enfermedad`) tras la migración, sin pérdida de dato.

### Validaciones / borde
- PV1 — Importes y kilos > 0.
- PV2 — Fechas de cuotas ≥ fecha de factura.
- PV3 — Peso promedio con unidades = 0 manejado.
- PV4 — Comprobante formato/tamaño validados.
- PV5 — No permitir edición/anulación fuera de estados habilitados.
- PV6 — Job idempotente.
- PV7 — Comprobante formato inválido → error claro.
- PV8 — No rechazar cuota ya `Rechazada`.
- PV9 — Comprobante extensión/tamaño inválido.
- PV10 — Gasto con proveedor inexistente/inactivo: bloqueado.
- PV11 — Compensación con origen = destino: bloqueada.
- PV12 — Nacimiento sin grupo destino: bloqueado.
- PV13 — Pago de Egreso tipo Cheque sin fecha de vencimiento: bloqueado.
- PV14 — Pago de Egreso con fecha de vencimiento anterior a la fecha efectiva del pago: bloqueado.
- PV15 — Egreso sin ningún pago cargado: bloqueado.
- PV16 — No regularizar/rechazar un Pago de Egreso que no sea de tipo Cheque, ni rechazar uno ya `Rechazado`.
- PV17 — (v12) Motivo de Factura de venta vacío: bloqueado (campo obligatorio).
- PV18 — (v12) Motivo de Factura de venta mayor a 200 caracteres: bloqueado.

---

## 17. Checklist de salida para merge

- [x] Pares de matriz de transiciones confirmados (incluye `Ternero → Toro`).
- [x] Política de comprobantes confirmada (1 archivo, 5 MB).
- [x] `Organismo intermediario` confirmado como ABM.
- [ ] Indicadores del Dashboard definidos (fase 2).
- [ ] ABM Organismo intermediario implementado.
- [ ] ABM Grupo implementado con condición `stock == 0` para baja.
- [ ] ABM Rubro implementado (independiente de Grupo).
- [ ] ABM Proveedor con ámbito y filtrado por contexto.
- [ ] ABM Usuarios restringido a SuperUsuario.
- [ ] Autocomplete de concepto con normalización.
- [ ] Snapshot de `TasaImpuestoAplicada` en Factura.
- [ ] Redondeo de cuotas con última absorbe diferencia.
- [ ] Recálculo de cuotas al editar factura (solo con cuotas 100% `Pendiente`).
- [ ] Rechazo de cuota muta estado sin contramovimiento.
- [ ] Regularización (Opción 3 a/b) implementada.
- [ ] Job diario idempotente con notificación in-app.
- [ ] Venta multi-grupo con control de concurrencia.
- [ ] Compensaciones intra/inter con validación por matriz.
- [ ] Dashboard con selector de año y filtros por Categoría/Grupo.
- [ ] Numeración correlativa única de Factura con formato `F-000123`.
- [ ] Movimiento `Inicial` de stock único por Grupo (valor del enum `TipoMovimientoStock`).
- [ ] Grupos inactivos visibles en consulta histórica (Dashboard/Caja) y ocultos en selectores operativos.
- [ ] Criterios de aceptación por pantalla redactados.
- [ ] Pruebas PF1–PF52 + PV1–PV12 aprobadas.
- [ ] **(v11)** Entidad `EgresoPago` reemplaza `FormaDePago` único de `Egreso`; suma de pagos == importe total validada en alta.
- [ ] **(v11)** Cheque diferido de Egreso: ciclo `Pendiente` → `Acreditado` vía job diario extendido (mismo job que Cuotas).
- [ ] **(v11)** Rechazo y regularización (Opción 3 a/b) de Pago de Egreso implementados, simétricos a Cuotas.
- [ ] **(v11)** Anulación de Egreso propaga a todos sus Pagos y Movimientos de Caja asociados.
- [ ] **(v11)** Pruebas PF53–PF61 + PV13–PV16 aprobadas.
- [ ] **(v12)** Autocomplete de Concepto (Egresos) migrado de `<datalist>` a Select2, sin regresión funcional.
- [ ] **(v12)** `FacturaVenta.Motivo` migrado de enum a texto libre con autocomplete Select2, datos históricos preservados (backfill validado).
- [ ] **(v12)** Pruebas PF62–PF66 + PV17–PV18 aprobadas.

---

## 18. Historial de versiones

- **v1** — Elicitación inicial.
- **v2** — Motivos de venta cerrados, IVA calculado por sistema, 5 usuarios Productor, estado `Rechazada`, selector de año en dashboard.
- **v3** — Forma de pago enum, trazabilidad individual diferida a fase 2, reglas de rechazo (estado del movimiento a `Pendiente`).
- **v4** — Proveedores con ABM, comprobantes PDF/JPG/PNG, cuotas equitativas, edición de factura con recálculo, IVA histórico, notificación in-app, admin de usuarios sólo SuperUsuario.
- **v5** — Stock por Grupo; compensaciones intra/inter-categoría formalizadas.
- **v6** — Stock mínimo por Grupo; matriz fija de transiciones; baja lógica con stock=0; venta multi-grupo; dashboard por Grupo; redondeo 2 decimales; catálogo único de proveedores con ámbito; autocomplete de concepto; sin estado `Anulada`.
- **v7** — Rubro (Egresos) y Grupo (Stock) como **entidades distintas con mismo patrón ABM**; **Opción 3** adoptada para regularización de rechazo (error de carga / cobro posterior).
- **v8** — Categoría `Ternero` confirmada (con transición `Ternero → Toro`); comprobante de gasto fijado en **1 archivo / 5 MB**; **Organismo intermediario** confirmado como entidad **ABM**.
- **v9** — Validación por el agente `analista-funcional`: stack corregido a MVC; agregado §0 con contrato de salida mínima del agente. Confirmadas: Dashboard a backlog fase 2 y capa de presentación MVC (Controllers + Views). Se abren PA1–PA3 como preguntas funcionales pendientes. Sin cambios de alcance funcional.
- **v10** — Cierre de PA1–PA3: numeración correlativa única de Factura (`F-000123`), stock inicial como movimiento explícito tipo `Inicial`, visibilidad histórica completa de Grupos dados de baja en Dashboard y detalles históricos. Agregadas PF47–PF52.
- **v11** — Pedido del cliente (proyecto `ganaderia - emo` únicamente): Egresos pasa de forma de pago única con acreditación inmediata a **pagos múltiples por Egreso** (nueva entidad `EgresoPago`), habilitando cheques diferidos con fecha de vencimiento propia + pago compensatorio, con validación de suma exacta contra el importe total. El cheque diferido replica el ciclo Pendiente→Acreditado del job diario ya usado para Cuotas de venta, y admite rechazo/regularización (Opción 3 a/b) simétricos a los de Cuota. No se agrega edición de Egreso. Agregadas PF53–PF61, PV13–PV16, riesgos R25–R26, supuestos S31–S34.
- **v12** — Pedido del cliente (proyecto `ganaderia - emo` únicamente): el autocomplete de Concepto (Egresos) migra de `<datalist>` nativo a **Select2** (estándar UI del estudio, sin agregar dependencias nuevas). En Facturas de venta, `Motivo` deja de ser un enum cerrado y pasa a **texto libre con autocomplete Select2**, mismo patrón que Concepto de Egreso; los 3 valores históricos se preservan como datos migrados. Agregadas PF62–PF66, PV17–PV18, riesgos R27–R28, supuestos S35–S37.
