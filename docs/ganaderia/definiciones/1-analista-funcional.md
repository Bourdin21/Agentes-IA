# Análisis Funcional — Sistema de Gestión Ganadera

Versión: **v10** (consolidada y validada por el agente `1 - analista-funcional`)
Agente: `analista-funcional` (`C:\Sistemas\Agentes-IA\.github\agents\analista-funcional.agent.md`)
Conversación: `2025-11-ganaderia-blankproject`
Proyecto: BlankProject (ASP.NET Core **MVC**, .NET 10, EF Core 10, MySQL 8, Identity, Serilog)
Alcance: documento funcional. **No** define implementación técnica detallada.

---

## 0. Salida mínima del agente

> Contrato exigido por `analista-funcional.agent.md` (salida en 5 puntos). El detalle se desarrolla en §1–§18.

### 0.1 Alcance funcional resumido

Sistema de gestión para un productor ganadero argentino con **tres ejes**: **Ingresos** (Ventas → Facturas → Cuotas → Caja), **Egresos** (Gastos con comprobante) y **Stock** (por Grupo, con compensaciones intra/inter-categoría según matriz cerrada). Transversales: **Cuenta Corriente / Caja** y **Dashboard anual mensualizado**. Soporta hasta **5 usuarios Productor** + **1 SuperUsuario**. Catálogos ABM: Grupo, Rubro, Proveedor (con ámbito), Organismo intermediario. Job diario idempotente de acreditación + notificación in-app.

### 0.2 Impacto técnico por capa

- **Presentación (MVC)**: 11 áreas de vistas (Ventas, Facturas, Cuotas, Gastos, Stock, MovimientosStock, Caja, Dashboard, Catálogos×4, Novedades), formularios con validación en español, selectores filtrados, uploader de comprobante, bandeja de novedades, autorización por rol.
- **Negocio (Application + Services)**: reglas de ciclo de vida (Venta/Factura/Cuota), cálculo de IVA con snapshot inmutable, generación/regeneración de cuotas, matriz de transiciones, compensaciones, baja lógica con `stock==0`, regularización Opción 3a/3b, job diario idempotente, autocomplete normalizado, filtrado de proveedores por ámbito, límite de 5 Productores.
- **Datos (EF Core + MySQL)**: 13 entidades nuevas bajo `Domain/Entities/Ganaderia`, snapshot `TasaImpuestoAplicada` en Factura, `MovimientoStock` con origen/destino nullables, `MovimientoCaja` con estado y FK polimórfica al documento de origen, almacenamiento de archivo de comprobante fuera de DB, baja lógica vía `SoftDestroyable`.

### 0.3 Riesgos y supuestos clave

- **R16** Recálculo de cuotas al cambiar plazo en la factura · **R18** Mantenimiento de la matriz si aparecen nuevas categorías · **R20/R24** Concurrencia en venta multi-grupo · **R22** Variantes ortográficas en autocomplete de concepto · **R23** Matriz cerrada requiere deploy para extenderse · **R13** Movimientos en `Pendiente` por rechazo sin regularizar.
- Supuestos S1–S30 consolidados: un productor, ARS única, 1 Venta ↔ 1 Factura, sin AFIP, sin retenciones, tasa IVA histórica inmutable, cuotas equitativas con última absorbiendo diferencia, stock por Grupo (categoría derivada), trazabilidad individual diferida a fase 2, comprobante 1 archivo × 5 MB, rechazo muta estado sin contramovimiento, regularización Opción 3a/3b, proveedor con ámbito, Rubro y Grupo entidades distintas con mismo patrón ABM, concepto de gasto libre con autocomplete.

### 0.4 Pruebas mínimas requeridas

Casos **PF1–PF52** funcionales + **PV1–PV12** de validación/borde, detallados en §16. Cubren ciclos de vida, cálculos de IVA y cuotas, job diario idempotente, rechazo y regularización (3a/3b), compensaciones intra/inter con matriz, baja lógica, autocomplete, filtrado por ámbito, autorización por rol, formato/tamaño de comprobante, numeración correlativa de Factura, stock inicial como movimiento explícito y visibilidad histórica de Grupos inactivos.

### 0.5 Checklist de salida para merge

Ver **§17** (checklist completo con 21 ítems verificables desde UI + Service + persistencia).

---

## Nota sobre la versión

- **v8** — Cerró categoría `Ternero`, comprobante 1 archivo × 5 MB, Organismo intermediario como ABM.
- **v9** — Validación por el agente `analista-funcional`: se corrigió el stack (MVC, no Razor Pages) y se agregó el bloque §0 con el contrato del agente. Sin cambios de alcance funcional.

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
- **Motivo** (enum cerrado): `Faena`, `Vacía`, `Enfermedad`.
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

## 4. Módulo Egresos — Gastos

### 4.1 Atributos del Gasto
- Fecha
- Importe
- **Rubro** (FK a catálogo ABM de Rubros de egreso — entidad propia)
- **Concepto / Motivo**: string libre con **autocomplete** basado en valores previamente ingresados por el usuario (historial distinct, con normalización básica: trim y comparación case-insensitive).
  - Descripción
- **Proveedor** (FK a catálogo único de Proveedores, filtrado por ámbito)
- **Forma de pago** (enum cerrado): `Efectivo`, `Transferencia`, `Cheque`
- **Comprobante** adjunto: PDF / JPG / PNG, opcional, **1 archivo por gasto**, tamaño máximo **5 MB**.

### 4.2 Impacto
- Genera **Movimiento de Caja** egreso en estado `Acreditado` al registrarse.
- Afecta saldo de cuenta corriente y dashboard del mes.

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
  - Gasto (egreso, inmediato en `Acreditado`).
- Cada movimiento navega a su documento de origen (cuota/factura/venta o gasto).
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
- Evento mínimo: pagos acreditados del día por el job automático.

---

## 10. Enums (listas cerradas)

| Enum | Valores |
|---|---|
| `MotivoVenta` | Faena, Vacía, Enfermedad |
| `FormaDePago` (Gasto) | Efectivo, Transferencia, Cheque |
| `TasaImpuesto` | IVA21, IVA10_5 |
| `EstadoCuota` | Pendiente, Acreditada, Rechazada |
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
- Operativa: Venta (multi-línea con selector de grupo), Factura + Cuotas, Gasto (con autocomplete de concepto y upload de comprobante), Movimientos de Stock (incl. compensación con origen/destino).
- Consulta: Cuenta Corriente, Stock (por Grupo con totalización por Categoría), Dashboard con selector de año y filtros por categoría/grupo.
- Acciones: Rechazo de cuota, Regularización (Opción 3 a/b).
- Bandeja de novedades al iniciar sesión.
- Validaciones de UI: fechas coherentes, importes/cantidades > 0, stock no negativo, formato/tamaño de comprobante, transiciones de compensación según matriz.

### Negocio
- Reglas de ciclo de vida (edición/anulación) de Venta, Factura, Cuota.
- Cálculo de impuestos con tasa histórica persistida.
- Generación y recálculo de cuotas con distribución equitativa y redondeo a 2 decimales.
- Job diario idempotente de acreditación.
- Regularización de rechazo (Opción 3).
- Validación de compensaciones contra matriz de transiciones.
- Baja lógica de Grupo con `stock == 0`.
- Autorización por rol (Productor vs SuperUsuario).
- Filtrado de proveedores por ámbito.
- Autocomplete de conceptos (distinct histórico, normalizado).

### Datos
- Entidades: Venta, DetalleVenta, Factura, Cuota, MovimientoCaja, Gasto, Rubro, Proveedor, Grupo, MovimientoStock, Categoria (enum), Usuario, OrganismoIntermediario, Comprobante (archivo).
- Snapshot de `TasaImpuestoAplicada` en Factura.
- MovimientoStock con `GrupoOrigen` y `GrupoDestino` (nullables según tipo).
- MovimientoCaja con `Estado` y FK al documento de origen (cuota o gasto).
- Sin borrado físico; baja lógica donde corresponda.

---

## 13. Riesgos vigentes

- **R16** — Recálculo de cuotas ante cambio de plazo en la factura (60→30 elimina y regenera).
- **R18** — Mantenimiento de la matriz de transiciones si aparecen nuevas categorías.
- **R20/R24** — Concurrencia en venta multi-grupo: validar atómicamente stock al guardar.
- **R22** — Autocomplete de concepto: sensibilidad a variantes ortográficas; aplicar normalización.
- **R23** — Matriz como configuración cerrada requiere deploy para extenderse.
- **R13** — Movimientos en `Pendiente` por rechazo pueden quedar "huérfanos" si nunca se regularizan; considerar filtros/reportes.

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
- **v10** — Cierre de PA1–PA3: numeración correlativa única de Factura (`F-000123`), stock inicial como movimiento explícito tipo `Inicial` (nuevo valor del enum `TipoMovimientoStock`), visibilidad histórica completa de Grupos dados de baja en Dashboard y detalles históricos. Agregadas PF47–PF52.
