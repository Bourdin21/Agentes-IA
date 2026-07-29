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

## Historial de ajustes de alcance
- 2026-07-30: se descarta el módulo "Cheques 30/60/90 días" como módulo aparte (el cliente no opera con pagos diferidos propios) — se absorbe como campo de forma de pago en Proveedores + Compras.
- 2026-07-30: mantenimiento acordado previo a este relevamiento (año 1 con Etapa 1 = PRO sin costo; desde Etapa 2 = PREMIUM USD 500/año) se mantiene sin cambios para este proyecto.
- 2026-07-30: agregado módulo "Devoluciones + Notas de crédito/débito AFIP" (Etapa 2, confirmado por el cliente: aplican devoluciones, no cambios). Migración de catálogo promovida de ítem dentro de Etapa 2 a **Etapa 3 independiente** (~17.000 productos, formato aún no recibido, precio provisional USD 315). Dashboard ampliado de 8h a 12h por pedido explícito del cliente de priorizar diseño y estructura de esa pantalla.
- 2026-07-30: agregado plan de puesta a punto de stock inicial (clasificación ABC + conteo focalizado + arranque suave + ajuste manual auditado + conteo cíclico). Stock (Etapa 1) 6h→8h. Etapa 3 12h→15h base, precio provisional USD 315→USD 394.
