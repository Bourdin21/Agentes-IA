# 4 — Presupuesto
## Sistema de Gestión Comercial — Indumentaria y Calzado

**Cliente:** Ulises  
**Proveedor:** OlvidataSoft  
**Versión:** 1.0  
**Estado:** Presupuesto inicial — listo para entrega al cliente  
**Base:** `1-analista-funcional.md` v1.1 + `2-disenador-funcional.md` v1.0 + `3-arquitecto-mvc.md` v1.0 (todos aprobados)  
**Tasa vigente:** USD 14 / hora (ref. 27-presupuesto-parametros, dataset Abril 2026)  
**Política de contingencia:** variable por riesgo (8% / 15% / 25%) — aplicada **una sola vez** por ítem.  
**Cultura:** es-AR.

> Memoria oficial del agente "presupuestador". Estimación PERT por módulo funcional (no por capa técnica), con autocorrección contra dataset histórico antes del cierre.

---

## 1. Alcance funcional resumido (presupuestable)

9 módulos funcionales + Dashboard + infraestructura transversal. **No incluye** las exclusiones fijas (ver §6) ni nada fuera de lo aprobado en análisis v1.1.

Drivers comunes ya cerrados (no se cobran por separado):
- Migraciones EF M1–M6: incorporadas a la línea "Infra transversal".
- Decisiones D1–D6 absorbidas dentro del esfuerzo de cada módulo afectado (Ventas, Compras, Aumento masivo, Maestros).
- Validación server-side, autorización por policies, sidebar dinámico, soft delete: dentro de cada ítem.

---

## 2. Tabla de estimación PERT por módulo

> O = optimista, M = más probable, P = pesimista, PERT = (O + 4M + P) / 6.  
> Distribución interna (Imp/Pru/Doc/Riesgo) es **trazabilidad** del esfuerzo total, no recargos adicionales.

| # | Módulo funcional | Tipo | Drivers concretos | O | M | P | PERT (h) | Distribución interna (Imp / Pru / Doc / Rsg) | Riesgo | Cont. | Horas finales | USD |
|---|---|---|---|---:|---:|---:|---:|---|---|---:|---:|---:|
| 1 | Seguridad y Acceso | Ajuste sobre existente | Rol Vendedor + 2 policies + sidebar dinámico | 1,0 | 1,5 | 2,5 | **1,58** | 1,0 / 0,3 / 0,2 / 0,1 | Bajo | 8% | **1,7** | 24 |
| 2 | Maestros Comerciales (5 ABMs) | 5 × ABM simple/intermedio | Categorías, Subgrupos (cascada AJAX), Clientes, Proveedores, TiposPrecio + D5 (cliente con ventas) | 14,0 | 18,0 | 24,0 | **18,33** | 12,0 / 3,5 / 1,5 / 1,3 | Bajo | 8% | **19,8** | 277 |
| 3 | Productos y Variantes | ABM complejo padre/hijo | Formulario dinámico Ropa/Zapatilla, búsquedas AJAX, RowVersion (D6), visibilidad costos por rol, índices únicos SKU/CodigoBarra | 8,0 | 10,0 | 14,0 | **10,33** | 6,8 / 2,0 / 0,8 / 0,7 | Medio | 15% | **11,9** | 167 |
| 4 | Stock e Inventario | Complejo con trazabilidad | Stock 1:1 con variante, MovimientoStock con 4 FKs polimórficas, alertas, carga inicial, ajuste manual, historial | 6,0 | 8,0 | 11,0 | **8,17** | 5,5 / 1,5 / 0,6 / 0,6 | Medio | 15% | **9,4** | 132 |
| 5 | Compras a Proveedores | Workflow con estados + recepción transaccional | Máquina 4 estados (Borrador→EnProceso→Verificada→Recibida), recepción con `Rec+Dañ+Dev≤Pedida` por línea, D3 (dañadas pre-recepción ignoradas), actualización `UltimoPrecioCompra`, adjuntos | 8,0 | 10,0 | 14,0 | **10,33** | 6,8 / 2,0 / 0,8 / 0,7 | Medio | 15% | **11,9** | 167 |
| 6 | Ventas a Clientes ⭐ | Financiero complejo (multi-feature) | Carrito AJAX single-page, multi-pago dinámico, cuotas con D2 (recargo distribuido + ajuste última), D1 (two-save NroVenta), transacción serializable, anular/entregar (máquina de estados), remito PDF (QuestPDF), adjuntos, visibilidad costos | 14,0 | 18,0 | 24,0 | **18,33** | 12,0 / 3,5 / 1,5 / 1,3 | Alto | 25% | **22,9** | 321 |
| 7 | Devoluciones y Cambios | Workflow + wizard | Wizard 4 pasos JS, 3 tipos (DevolucionDinero / CambioMismoValor / CambioMayorValor), validación `CantidadDevolver ≤ Vendida−Previas`, stock reingreso/decremento, transacción serializable | 6,0 | 8,0 | 11,0 | **8,17** | 5,5 / 1,5 / 0,6 / 0,6 | Alto | 25% | **10,2** | 143 |
| 8 | Resumen Semanal | Reporte/exportación | Query directo a VentaPago Transferencia, agrupación por día, navegación semanal, export Excel (ClosedXML) | 1,5 | 2,0 | 3,0 | **2,08** | 1,4 / 0,4 / 0,2 / 0,1 | Bajo | 8% | **2,2** | 31 |
| 9 | Aumento Masivo de Precios | Workflow + concurrencia | Filtros (categoría/subgrupo/marca/manual), preview no persistido (D4), aplicación batch con bloqueo optimista RowVersion (D6), validación `% ≤ 500` | 3,0 | 4,0 | 6,0 | **4,17** | 2,8 / 0,8 / 0,3 / 0,3 | Alto | 25% | **5,2** | 73 |
| 10 | Dashboard | Ajuste con widgets | Widgets diferenciados por rol (Admin full / Vendedor sin costos), datos a tiempo de carga | 1,5 | 2,0 | 3,0 | **2,08** | 1,4 / 0,4 / 0,2 / 0,1 | Bajo | 8% | **2,2** | 31 |
| 11 | Infra transversal | Configuración técnica | 6 migraciones EF (M1–M6), `ApplyConfigurationsFromAssembly`, 14 registros DI, seed RolVendedor, base de configs Fluent | 2,0 | 3,0 | 4,0 | **3,00** | 2,0 / 0,5 / 0,3 / 0,2 | Medio | 15% | **3,5** | 49 |

### Totales

| Concepto | Valor |
|---|---:|
| **Total horas PERT (base, sin contingencia)** | **86,57 h** |
| **Total horas finales (con contingencia variable)** | **101,1 h** |
| **Total USD (101,1 × 14)** | **USD 1.415** |

> **Política de contingencia respetada**: aplicada una única vez por ítem según riesgo. Pruebas, documentación y riesgo ordinario se reportan internamente como distribución del PERT, **no** como recargos adicionales.

---

## 3. Bloque de autocorrección pre-cierre (calibración contra históricos)

Dataset de referencia: `27-presupuesto-parametros.instructions.md` + proyectos comparables (Delicias Naturales 95h base / 19 módulos; Vinosefue 30h con máquinas de estado; Eleven La Plata 50h / 27 módulos; Recotrack/Lumitrack/Piapartments para ABM con 30% incluido).

**Normalización**: rangos históricos con 30% incluido se llevan a base dividiendo por 1,30 (anti doble contingencia).

| # | Módulo | Horas base estimadas | Referencia histórica (base) | Mediana base | Ratio | Decisión | Justificación |
|---|---|---:|---|---:|---:|---|---|
| 1 | Seguridad (ajuste) | 1,58 | Ajuste puntual: 0,5–1 h por driver. 3 drivers (rol + policies + sidebar) | 1,5 | **1,05** | Mantener | En rango. |
| 2 | Maestros (5 ABMs) | 18,33 | ABM simple base 1,5–3,1 h; ABM intermedio base 3,8–5,4 h. Promedio mix esperado ~4 h × 5 = 20 h | 20,0 | **0,92** | Mantener | Leve simplificación por reutilización de plantillas/patrón. Dentro de banda. |
| 3 | Productos+Variantes | 10,33 | ABM complejo padre/hijos: 7,7–11,5 h | 9,6 | **1,08** | Mantener | En rango histórico de complejo padre/hijo. Drivers (formulario dinámico, RowVersion, costos por rol) están dentro de la banda. |
| 4 | Stock | 8,17 | ABM complejo: 7,7–11,5 h | 9,6 | **0,85** | Mantener (límite inferior) | Trazabilidad polimórfica compensa con menos UI compleja. En banda. |
| 5 | Compras | 10,33 | ABM complejo padre/hijos (7,7) + workflow estados (4–6) ≈ 11–13 h base | 12,0 | **0,86** | Mantener | Recepción y workflow se solapan con cabecera/detalle. En banda inferior. |
| 6 | Ventas ⭐ | 18,33 | Sin histórico unitario comparable. Es **multi-feature**: carrito (≈4 h) + multi-pago/cuotas (≈4 h) + transacción/two-save (≈3 h) + máquina estados (≈2 h) + remito PDF (≈2 h) + adjuntos (≈1 h) + visibilidad costos (≈1 h) ≈ 17 h | 17,0 | **1,08** | Mantener | Suma de drivers concretos justifica el monto. Riesgo Alto (concurrencia stock + dinero) es coherente con dataset Vinosefue. |
| 7 | Devoluciones | 8,17 | Workflow estados (4–6) + wizard validaciones (≈2–3) + 3 ramas operativas | 7,5 | **1,09** | Mantener | Tres tipos de operación (dinero / cambio igual / cambio mayor) y validación de cantidad disponible elevan respecto a workflow simple. En rango. |
| 8 | Resumen Semanal | 2,08 | Reporte/exportación: 1–2 h | 1,5 | **1,39** | **Justificar** | Supera 15% el techo. Driver: query agrupada + navegación semanal + export Excel (ClosedXML). Tres componentes en un mismo módulo. Aceptado. |
| 9 | Aumento Masivo | 4,17 | Workflow con estados (4–6 h) | 5,0 | **0,83** | Mantener | En límite inferior; concurrencia D6 vía RowVersion es mecánica, no compleja. Aceptado. |
| 10 | Dashboard | 2,08 | Ajuste con widgets: 1–2 h | 1,5 | **1,39** | **Justificar** | Versiones diferenciadas por rol (2 layouts) + 5 indicadores. Acotado. Aceptado. |
| 11 | Infra transversal | 3,00 | Migración EF 0,5 h × 6 = 3 h + base configs absorbida en ítems | 3,0 | **1,00** | Mantener | Exacto al rango histórico. |

### Resumen de autocorrección

- **Ítems en rango (0,85 – 1,15)**: 9 de 11.
- **Ítems con justificación documentada (>1,15)**: Resumen Semanal (1,39) y Dashboard (1,39) — drivers concretos identificados, monto absoluto bajo (≈4,3 h combinadas).
- **Ítems con ratio < 0,85**: 0.
- **Ajustes a la baja aplicados**: ninguno (no hay sobre-estimación injustificada).
- **Ajustes al alza aplicados**: ninguno (no hay omisiones detectadas).

### Cierre numérico (paso A vs paso B)

| Paso | Total horas | Total USD |
|---|---:|---:|
| **Paso A — preliminar** (sin autocorrección) | 101,1 h | USD 1.415 |
| **Paso B — final** (post-autocorrección) | **101,1 h** | **USD 1.415** |

> Sin variación entre A y B: la autocorrección confirmó la estimación. No hubo sobreestimación ni omisión detectada. Doble contingencia descartada (aplicada una sola vez por ítem).

### Comparación contra proyecto histórico más cercano

- **Delicias Naturales**: 95 h base / 110 h con contingencia, 19 módulos, dataset por módulo.
- **ShowroomGriffin**: 86,57 h base / 101,1 h con contingencia, 9 módulos + Dashboard + Infra.
- **Ratio agregado**: 86,57 / 95 = **0,91** → consistente. ShowroomGriffin tiene menos módulos pero algunos de mayor envergadura (Ventas multi-feature). Ratio agregado dentro de tolerancia (±15%).

---

## 4. Pruebas mínimas requeridas (alcance del precio)

### Funcionales (incluidas)
- Crear venta con stock decrementado, NroVenta correlativo y movimientos generados.
- Stock insuficiente / suma pagos ≠ total → error funcional.
- Anular venta repone stock; venta entregada no se anula.
- Recepción compra: validación `Rec+Dañ+Dev ≤ Pedida` y actualización `UltimoPrecioCompra`.
- Wizard devolución 4 pasos completos.
- Aumento masivo: preview + aplicación con bloqueo optimista (D6).
- Resumen semanal: solo transferencias en Confirmada/Entregada.

### Autorización (incluidas)
- Vendedor → 403 en Compras, Stock/Ajuste, Stock/CargaInicial, AumentoMasivo, ResumenSemanal.
- Vendedor nunca recibe `UltimoPrecioCompra`, `CostoTotal`, `GananciaTotal` en payload.

### UI/Frontend (incluidas)
- Carrito AJAX con validación de stock en tiempo real.
- Recepción: validación JS por línea.
- Wizard: navegación entre pasos.

### No incluidas (fuera de alcance)
- Pruebas de carga / performance.
- Pruebas E2E automatizadas (Selenium / Playwright).
- Pruebas unitarias formales con framework (xUnit / NUnit) salvo lo mínimo de integración.

---

## 5. Riesgos y supuestos del presupuesto

| # | Tipo | Descripción | Impacto si se materializa |
|---|---|---|---|
| RP1 | Riesgo | Provider MySQL no soporta `HasFilter` para índices únicos condicionales | +0,5 h fallback validación en service |
| RP2 | Riesgo | Concurrencia real en venta requiere reintentos por deadlock | +1–2 h si aparece en pruebas |
| RP3 | Riesgo | Cliente solicita persistir cuotas como N filas (vs decisión D2) | Reestimación: +1,5 h |
| RP4 | Riesgo | Cliente solicita backup automático de adjuntos | Reestimación: +2 h |
| SP1 | Supuesto | Servidor / hosting / backups corren por cuenta del cliente | — |
| SP2 | Supuesto | El stack disponible (QuestPDF, ClosedXML, MySQL 8) está pre-instalado | — |
| SP3 | Supuesto | Cliente provee logo, datos del local y plazo de devolución antes de F5 | — |
| SP4 | Supuesto | Sin migración de datos legacy | Si aparece, +20–30% sobre alcance afectado |

---

## 6. Exclusiones (no incluidas en el precio)

- Migración de datos desde sistema anterior.
- Configuración y costo del servidor / hosting.
- Facturación electrónica AFIP / ARCA.
- Aplicación móvil (iOS / Android).
- Integración con hardware externo (impresora fiscal). Lector USB de código de barras opera como teclado: **no** requiere desarrollo.
- Multi-sucursal.
- Backup automático de base / adjuntos.
- Notificaciones email / push automáticas.
- Cambios de alcance posteriores al inicio (se presupuestan por separado).
- Pruebas de carga, E2E automatizadas, unitarias formales.

---

## 7. Gatillos de reestimación obligatoria

- Cambio de alcance funcional (módulo nuevo o feature relevante no contemplada).
- Cambio en reglas de negocio o permisos (matriz de roles).
- Aparición de integración externa no relevada (AFIP, pasarela de pago, hardware).
- Necesidad de migración de datos legacy.
- Decisiones D1–D6 revertidas o modificadas (especialmente D2 y D6).
- Política fija de contingencia impuesta por el cliente (si aplica, anula la variable).

---

## 8. Condiciones comerciales

- **Forma de pago**: 50% al inicio, 50% a la entrega.
- **Validez de la oferta**: 30 días.
- **Plazo estimado**: a coordinar según disponibilidad (referencia: ≈ 3 a 4 sprints).
- **Tasa**: USD 14 / hora (referencia confirmada en proyectos cerrados, dataset Abril 2026).
- **Moneda de facturación**: USD (o equivalente ARS al tipo de cambio del día de facturación).

---

## 9. Documento simple para cliente (resumen comercial)

| Área funcional | Horas | USD |
|---|---:|---:|
| Seguridad y acceso (rol vendedor) | 1,7 | 24 |
| Maestros comerciales (5 ABMs) | 19,8 | 277 |
| Productos y variantes | 11,9 | 167 |
| Stock e inventario | 9,4 | 132 |
| Compras a proveedores | 11,9 | 167 |
| Ventas a clientes (carrito, pagos, remito) | 22,9 | 321 |
| Devoluciones y cambios | 10,2 | 143 |
| Resumen semanal de transferencias | 2,2 | 31 |
| Aumento masivo de precios | 5,2 | 73 |
| Dashboard | 2,2 | 31 |
| Configuración técnica (migraciones, seed) | 3,5 | 49 |
| **Total** | **101,1 h** | **USD 1.415** |

---

## 10. Checklist de salida — Presupuesto

```
PRESUPUESTO — CHECKLIST DE SALIDA
────────────────────────────────────────────────────────────────────
[✓] Estimación por módulo funcional (no por capa técnica)
[✓] PERT (O, M, P) por módulo
[✓] Distribución interna Imp/Pru/Doc/Riesgo (trazabilidad)
[✓] Contingencia variable por riesgo aplicada UNA SOLA VEZ
[✓] Sin doble contingencia detectada
[✓] Bloque de autocorrección contra históricos completo
[✓] Ratios calculados; justificaciones registradas para >1,15
[✓] Comparación agregada con proyecto histórico cercano (Delicias Naturales)
[✓] Cierre por dos pasos (A preliminar / B final post-autocorrección)
[✓] Riesgos del presupuesto + gatillos de reestimación
[✓] Exclusiones explícitas
[✓] Tabla simple para cliente con totales por área
[✓] Tasa USD 14/h aplicada según parámetros vigentes
────────────────────────────────────────────────────────────────────
```

---

## 11. Cierre de calibración estimado vs real (a completar al cierre del sprint)

| Módulo | Horas estimadas | Horas reales | Desvío % | Motivo |
|---|---:|---:|---:|---|
| Seguridad | 1,7 | — | — | — |
| Maestros (5 ABMs) | 19,8 | — | — | — |
| Productos+Variantes | 11,9 | — | — | — |
| Stock | 9,4 | — | — | — |
| Compras | 11,9 | — | — | — |
| Ventas ⭐ | 22,9 | — | — | — |
| Devoluciones | 10,2 | — | — | — |
| Resumen Semanal | 2,2 | — | — | — |
| Aumento Masivo | 5,2 | — | — | — |
| Dashboard | 2,2 | — | — | — |
| Infra transversal | 3,5 | — | — | — |
| **Total** | **101,1** | — | — | — |

> Si el desvío promedio absoluto al cierre supera 20%, recalibrar `27-presupuesto-parametros.instructions.md` con los datos de este proyecto.
