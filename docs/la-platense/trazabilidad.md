# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-07-30 09:00 - orquestador / analista-funcional
- Etapa: Analisis
- Cambio: Creado el proyecto La Platense a partir del relevamiento presencial. Capturado el alcance completo de 16 módulos y detectada funcionalidad adicional no pedida explícitamente (devoluciones, reservas de stock, NC/ND AFIP, permisos de repartidor, multi-caja, historial de precios, alerta de lista vencida) — pendiente de confirmación con el cliente, no incluida en el presupuesto.
- Motivo: cumplir la secuencia obligatoria Discovery→Análisis antes de Diseño.
- Impacto en capas: Presentación, Negocio, Datos (alcance general).
- Riesgos/supuestos: modelado de unidades de medida con conversión compra/venta sin precedente exacto; migración de catálogo sin archivo de origen confirmado; workflow de venta editable pre-AFIP como mayor riesgo funcional. Alcance de "Cheques" reducido — el cliente aclaró que no hay pagos diferidos propios.

### 2026-07-30 09:30 - disenador-funcional
- Etapa: Diseno
- Cambio: Definidos los 4 flujos no triviales del sistema (conversión de unidades, venta Borrador→Facturada, importación de listas de proveedor, cuenta corriente de empleados) con pasos, ViewModels y validaciones de UI.
- Motivo: los cuatro flujos concentran la mayor parte de la novedad técnica y del riesgo funcional del proyecto.
- Impacto en capas: Presentación (ViewModels, validaciones), Negocio (Services de conversión, workflow, recargo, importación, autorización).
- Riesgos/supuestos: factor de conversión asumido fijo por producto (a validar si varía por proveedor); recálculo de saldo al editar venta con pagos ya cargados, a confirmar regla exacta con el cliente.

### 2026-07-30 10:00 - arquitecto-mvc
- Etapa: Arquitectura
- Cambio: Escaneada la reutilización cross-proyecto en `docs/*/definiciones/` antes de diseñar entidades nuevas. Mapa de reutilización definido: `marihogar` como base estructural principal (catálogo, stock, ventas+CC, AFIP, proveedores+compras, caja, gastos, presupuestos, entregas, aumento masivo); `delicias-naturales` como referencia conceptual de `UnidadMedida`; `vinosefue` (`MovimientoCCProveedor`), `ganaderia` (`CajaService`/`EgresoService`), `ShowroomGriffin` (`Marca`/`Modelo`) y `contadores-bma-conversor` (parser Excel) como donantes puntuales.
- Motivo: regla de reutilización cross-proyecto obligatoria en Diseño y Arquitectura (CLAUDE.md).
- Impacto en capas: Datos (20 entidades nuevas, migración inicial), Negocio (5 Services nuevos/extendidos).
- Riesgos/supuestos: 4 piezas identificadas sin precedente exacto (conversión de unidades, workflow de venta editable, CC de empleados con autoservicio, CC consolidada del negocio) — presupuestadas como desarrollo nuevo, no como reuse.

### 2026-07-30 10:30 - presupuesto-mvc
- Etapa: Presupuesto
- Cambio: WBS de 16 módulos (126h totales: Etapa 1 = 92h, Etapa 2 = 34h). Calculado R = 92h reuse / 126h total = 73% → Tier 1 (30% descuento) según `27-presupuesto-parametros.instructions.md`. Precio real de desarrollo (Tier 1 + Tokens IA 25%) ≈ USD 2.011. Aplicado adicionalmente un 15% de descuento por referido (decisión comercial de Joaquín, no ligado a la política de Tier) → precio final ≈ **USD 1.709** (Etapa 1 ≈ USD 1.248 / Etapa 2 ≈ USD 461).
- Motivo: el cliente pidió presupuesto modularizado por costo de implementación real, y usar el descuento de reutilización cross-proyecto según la política vigente del estudio.
- Impacto en capas: económico (sin impacto técnico directo).
- Riesgos/supuestos: R queda apenas por encima del umbral de Tier 1 (70%) — sensible a cuánto termine siendo "nuevo" en Ventas y Unidades de medida; revisar al cerrar Arquitectura definitiva. El precio real (USD 2.011) es sustancialmente mayor al monto informal de USD 1.100 barajado antes del relevamiento — la diferencia se explica por alcance real más amplio, no por un cambio de criterio de precio.

### 2026-07-30 11:00 - analista-funcional / disenador-funcional / arquitecto-mvc / presupuesto-mvc
- Etapa: Analisis → Diseno → Arquitectura → Presupuesto (ajuste en cadena)
- Cambio: Joaquín respondió las 6 preguntas abiertas del análisis v1. Resultado: (1) venta facturada admite anulación por NC — no es inmutable; (2) migración de catálogo confirmada en ~17.000 productos, formato aún no recibido, promovida a **Etapa 3 independiente** por pedido explícito del cliente; (3) punto de venta/caja único confirmado; (4) repartidor ve todas las entregas (no solo las asignadas); (5) aplican devoluciones de mercadería, NO cambios/canjes; (6) el dashboard es la pantalla de mayor prioridad ("foto completa del negocio"), se define en sesión de diseño dedicada en vez de un KPI-set fijo. Se agregó el módulo nuevo "Devoluciones + Notas de crédito/débito AFIP" (Etapa 2) y se amplió el módulo Dashboard (Etapa 1, 8h→12h).
- Motivo: cerrar las preguntas abiertas antes de comprometer un presupuesto final con el cliente.
- Impacto en capas: Datos (`NotaCreditoDebito`, `DevolucionMercaderia`), Negocio (`AnulacionVentaService`, `DevolucionMercaderiaService`, extensión de `AfipFacturacionService` para NC/ND), Presentación (flujo de anulación, dashboard de 3 niveles, importador de migración por lotes).
- Riesgos/supuestos: R de Etapa 1+2 bajó de 73% a **70,9%** (sigue en Tier 1, pero más ajustado) por el peso del nuevo módulo de bajo reuse. Etapa 3 (migración) se calcula con su propio R (16,7% → Tier 3, sin descuento) y lleva 25% de riesgo declarado por formato de archivo aún desconocido — precio provisional, sujeto a re-cotización real. Quedan 2 preguntas nuevas abiertas: quién puede anular una venta facturada (¿solo admin?) y si el archivo de migración incluirá el stock actual.

### 2026-07-30 11:30 - analista-funcional / disenador-funcional / arquitecto-mvc / presupuesto-mvc
- Etapa: Analisis → Diseno → Arquitectura → Presupuesto (ajuste en cadena)
- Cambio: Joaquín planteó el problema real de stock de La Platense — no tienen stock confiable hoy (se maneja de memoria por la rotación de artículos) y son ~17.000 productos a migrar. Se definió un plan de puesta a punto de stock inicial: clasificación ABC (sesión con el cliente, sin costo de desarrollo) + conteo físico solo de los productos "A" + arranque suave con stock negativo permitido para el resto (aviso, no bloqueo) + ajuste manual auditado + conteo cíclico post-arranque (hábito operativo, no funcionalidad). Se agregaron al sistema: `AjusteStock` (reutiliza patrón `ShowroomGriffin`), campos `Producto.clasificacionABC`/`stockVerificado`, y la extensión del importador de Etapa 3 para aceptar una columna de conteo real.
- Motivo: el cliente pidió una recomendación concreta para no arrancar el sistema nuevo con el mismo problema de stock no confiable que tiene hoy, y ponerlo como una etapa dentro del presupuesto.
- Impacto en capas: Datos (`AjusteStock`, campos nuevos en `Producto`), Negocio (`AjusteStockService`, validación de venta con stock negativo permitido en `VentaWorkflowService`), Presentación (pantalla de ajuste de stock, columna de conteo en el importador de migración).
- Riesgos/supuestos: Stock (Etapa 1) pasó de 6h a 8h; Etapa 3 pasó de 12h a 15h base. **R de Etapa 1+2 bajó de 70,9% a 70,6%** — sigue en Tier 1 pero el colchón sobre el umbral de 70% ya es mínimo; no conviene seguir sumando alcance nuevo de bajo reuse sin revisar este cálculo. Nueva pregunta abierta: quién hace la clasificación ABC (Olvidata en sesión con el cliente, o el cliente solo).

### 2026-07-30 12:00 - analista-funcional / disenador-funcional / arquitecto-mvc / presupuesto-mvc
- Etapa: Analisis → Diseno → Arquitectura → Presupuesto (ajuste en cadena)
- Cambio: dos decisiones de Joaquín. (a) **Nuevo alcance confirmado**: el cliente tiene una ticketeadora de código de barras (propios y de fábrica) — se agrega el módulo "Código de barras — etiquetado + lectura en venta" (7h, Etapa 1) para hacer la carga de la venta más dinámica. (b) **Se retira la migración de catálogo como etapa del presupuesto** — el problema de stock que la motivaba ya está resuelto por el módulo de puesta a punto de stock inicial (independiente de la migración); Joaquín va a hacer un segundo relevamiento tras aprobar este presupuesto para evaluar acceso directo a la base de datos actual del cliente, lo que bajaría mucho el costo real de importación frente a depender de un archivo Excel — se cotiza aparte, más adelante.
- Motivo: alinear el presupuesto con hardware real del cliente (ticketeadora) y no cobrar por adelantado una migración cuya incertidumbre está a punto de resolverse con mejor información (acceso a BD real).
- Impacto en capas: Datos (`Producto.codigoBarras`), Negocio (`EtiquetaService`, `CodigoBarrasLookupService`; se retira `CatalogoMigracionService` de este alcance), Presentación (impresión de etiquetas, campo de escaneo en venta).
- Riesgos/supuestos: **R de Etapa 1+2 bajó de 70,6% a 68,5% — el proyecto pasa de Tier 1 (30% descuento) a Tier 2 (15% descuento)**, tal como se había advertido en la ronda anterior (colchón sobre el umbral ya era mínimo). Nueva pregunta abierta: marca/modelo de la ticketeadora (define si la impresión de etiquetas es simple —impresora estándar de Windows— o requiere protocolo propietario ZPL/EPL, más costoso). Total del proyecto actualizado: Etapa 1 ≈ USD 1.649, Etapa 2 ≈ USD 597 — Total ≈ USD 2.246 (la migración queda fuera, se cotiza en una fase posterior).

### 2026-07-30 12:30 - presupuesto-mvc
- Etapa: Presupuesto
- Cambio: Joaquín aclaró que la ticketeadora es manual (no se integra con el sistema) — el módulo de código de barras se simplifica de 7h a 3h (solo vincular el código escaneado al producto, sin generación/impresión de etiquetas). Con eso, R de Etapa 1+2 sube de 68,5% a 69,8% (caso límite, a 0,2 puntos de Tier 1 — se mantiene Tier 2 por criterio estricto, declarado como zona gris). El precio según fórmula/política queda en ≈USD 2.183. **Joaquín fijó el precio final a cobrar en USD 1.800** (override comercial directo, ~17,5% por debajo de la fórmula), aportando su propia estimación de esfuerzo real: 30 horas reloj + USD 200 de tokens IA.
- Motivo: ticketeadora manual reduce el alcance real; precio de cierre fijado directamente por Joaquín para este cliente.
- Impacto en capas: Datos (`Producto.codigoBarras` sin cambios), Negocio (se retira `EtiquetaService`, queda solo `CodigoBarrasLookupService`), Presentación (sin pantalla de impresión de etiquetas).
- Riesgos/supuestos: chequeo de margen con los números de Joaquín (30h reales × USD 35/h + USD 200 tokens = USD 1.250 de piso de referencia) confirma que USD 1.800 da una tasa efectiva realizada de ≈USD 53,3/h — por encima del objetivo de USD 35/h, el override no compromete la rentabilidad esperada. Etapa 1 = USD 1.308 / Etapa 2 = USD 492 / Total = USD 1.800.

### 2026-07-30 13:00 - presupuesto-mvc
- Etapa: Presupuesto (cierre comercial)
- Cambio: Joaquín reestructuró el precio final como dos modalidades de pago del **total del proyecto** (ya no desglosado por etapa en el documento del cliente): **USD 1.500 en hasta 3 pagos**, o **USD 1.800 en hasta 12 pagos**. Además, simplificó el mantenimiento a un único plan **PREMIUM** desde el arranque — año 1 sin costo, USD 500/año desde el año 2 (reemplaza la transición PRO→PREMIUM de versiones anteriores).
- Motivo: cierre comercial — ofrecer flexibilidad de pago al cliente y simplificar el plan de mantenimiento dado que el sistema completo excede ampliamente el rango de tablas de PRO.
- Impacto en capas: económico/comercial, sin impacto técnico.
- Riesgos/supuestos: chequeo de margen con los números propios de Joaquín (30h reales + USD 200 tokens IA) confirma que ambas modalidades quedan por encima del objetivo de USD 35/h (≈USD 43,3/h en la de 3 pagos, ≈USD 53,3/h en la de 12 pagos) — ninguna compromete la rentabilidad esperada.

### 2026-07-30 14:00 - orquestador (cierre de presupuesto)
- Etapa: Presupuesto → Cierre (gate hacia Implementación)
- Cambio: **Cliente aprobó el presupuesto** — modalidad USD 1.500 en hasta 3 pagos, con plan de mantenimiento PREMIUM (año 1 sin costo).
- Motivo: aprobación formal del cliente, habilita el inicio de Implementación según la secuencia obligatoria de `CLAUDE.md` ("No iniciar Implementación sin Presupuesto aprobado por el cliente").
- Impacto en capas: ninguno técnico todavía — gate administrativo.
- Riesgos/supuestos: quedan preguntas abiertas de `1-analista-funcional.md` (§9) sin cerrar antes de Implementación: quién puede anular una venta facturada (admin/vendedor + límite de tiempo). La migración de catálogo sigue pospuesta a una fase posterior (pendiente el segundo relevamiento con acceso a BD real). Antes de desplegar, revisar capacidad de infraestructura disponible en SmarterASP (cupo de bases de datos 17/20 al 2026-07-30) — ver memoria `project-hosting-sharding-smarterasp.md`.

## Historial de ajustes de alcance
- 2026-07-30: se descarta el módulo "Cheques 30/60/90 días" como módulo aparte (el cliente no opera con pagos diferidos propios) — se absorbe como campo de forma de pago en Proveedores + Compras.
- 2026-07-30: mantenimiento acordado previo a este relevamiento (año 1 con Etapa 1 = PRO sin costo; desde Etapa 2 = PREMIUM USD 500/año) se mantiene sin cambios para este proyecto.
- 2026-07-30: agregado módulo "Devoluciones + Notas de crédito/débito AFIP" (Etapa 2, confirmado por el cliente: aplican devoluciones, no cambios). Migración de catálogo promovida de ítem dentro de Etapa 2 a **Etapa 3 independiente** (~17.000 productos, formato aún no recibido, precio provisional USD 315). Dashboard ampliado de 8h a 12h por pedido explícito del cliente de priorizar diseño y estructura de esa pantalla.
- 2026-07-30: agregado plan de puesta a punto de stock inicial (clasificación ABC + conteo focalizado + arranque suave + ajuste manual auditado + conteo cíclico). Stock (Etapa 1) 6h→8h. Etapa 3 12h→15h base, precio provisional USD 315→USD 394.
- 2026-07-30: agregado módulo "Código de barras — etiquetado con ticketeadora + lectura en venta" (Etapa 1, 7h). **Retirada la migración de catálogo como etapa del presupuesto** (se cotiza aparte más adelante, tras un segundo relevamiento con posible acceso a la base de datos real). Efecto combinado: el proyecto pasa de Tier 1 a Tier 2 (R bajó de 70,6% a 68,5%). Total: Etapa 1 USD 1.649 / Etapa 2 USD 597 / Total USD 2.246.
- 2026-07-30: ticketeadora confirmada como manual — módulo de código de barras simplificado a 3h (solo vinculación, sin etiquetado). Joaquín fijó el precio final de cierre en **USD 1.800** (Etapa 1 USD 1.308 / Etapa 2 USD 492), por debajo de los ≈USD 2.183 de la fórmula/política estándar, respaldado por su propio chequeo de margen (30h reales + USD 200 tokens IA → tasa efectiva ≈USD 53,3/h).
- 2026-07-30: precio final reestructurado como dos modalidades de pago del total del proyecto: **USD 1.500 en hasta 3 pagos** o **USD 1.800 en hasta 12 pagos**. Mantenimiento simplificado a un único plan PREMIUM (año 1 gratis, USD 500/año desde el año 2), reemplaza la transición PRO→PREMIUM anterior.
