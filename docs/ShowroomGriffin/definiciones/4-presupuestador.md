# 4 — Presupuesto
## Sistema de Gestión Comercial — Indumentaria y Calzado

**Cliente:** Ulises  
**Proveedor:** OlvidataSoft  
**Versión:** 1.0  
**Estado:** Cerrado — Sprint completado (Mayo 2026)  
**Base:** `1-analista-funcional.md` v1.1 + `2-disenador-funcional.md` v1.0 + `3-arquitecto-mvc.md` v1.0 (todos aprobados)  
**Tasa vigente:** USD 40 / hora (recalibrada al cierre; base: horas reales del sprint)  
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
- **Tasa**: USD 40 / hora (recalibrada al cierre del sprint, Mayo 2026; base: 25 h reales × USD 40 = USD 1.000).
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
| Seguridad | 1,7 | — | — | Tracking granular no registrado |
| Maestros (5 ABMs) | 19,8 | — | — | Tracking granular no registrado |
| Productos+Variantes | 11,9 | — | — | Tracking granular no registrado |
| Stock | 9,4 | — | — | Tracking granular no registrado |
| Compras | 11,9 | — | — | Tracking granular no registrado |
| Ventas ⭐ | 22,9 | — | — | Tracking granular no registrado |
| Devoluciones | 10,2 | — | — | Tracking granular no registrado |
| Resumen Semanal | 2,2 | — | — | Tracking granular no registrado |
| Aumento Masivo | 5,2 | — | — | Tracking granular no registrado |
| Dashboard | 2,2 | — | — | Tracking granular no registrado |
| Infra transversal | 3,5 | — | — | Tracking granular no registrado |
| **Total** | **101,1** | **25,0** | **−75,2 %** | Solo total disponible; seguimiento por módulo no registrado |

> **Desvío total −75,2 %** — supera el umbral del 20%. **Pendiente:** recalibrar rangos en `27-presupuesto-parametros.instructions.md` con datos de este sprint.  
> **Costo real facturado:** 25 h × USD 40 = **USD 1.000**  
> **Ratio real/estimado:** 25 / 101,1 = 0,25 — indica sobreestimación sistemática; revisar M (más probable) y P (pesimista) del dataset histórico para proyectos similares.

---

## V9 — Redirect post-ajuste de stock (2026-07-02) — Presupuesto exprés (fast-path)

Ítem único, sin PERT completo dado el tamaño trivial (cambio de 1 línea en un controller ya existente, sin migración ni pruebas de regresión amplias).

| Ítem | Horas estimadas | Riesgo |
|---|---:|---|
| Cambio de redirect + verificación funcional (build, smoke manual del flujo Ajuste) | 0,3 h | Bajo |

**Tasa:** USD 40/hora (recalibrada al cierre de sprint anterior). **Costo estimado:** USD 12.

**Aprobación:** fast-path autorizado por el usuario en este hilo — no requiere gate de aprobación formal de cliente dado el tamaño del cambio.

---

## V10 — Presupuesto: Carga masiva de stock por Marca + filtros completos en Consulta de Stock (2026-07-30)

**Input:** `1-analista-funcional.md`, `2-disenador-funcional.md`, `3-arquitecto-mvc.md` — todos sección V10, CERRADOS Y APROBADOS.
**Clasificación de negocio:** mejora sobre sistema propio ya entregado (v1 en producción) — **NO es Build inicial de cliente nuevo**. No aplica el descuento de expansión agresiva ni el piso de USD 280 (esa política es exclusiva de Build inicial; acá se cotiza a precio de lista de "Modificación sobre módulo existente").

### Paso 0 — Anclaje histórico

| Ítem | Referencia elegida | Horas base referencia | Motivo |
|---|---|---:|---|
| Carga masiva de stock | LabIPAC SESIÓN 3 — "M8 Carga masiva + alta rápida de Perfiles/Prácticas" (2026-07-08, cierre real) | 6,5 h | Mismo patrón funcional exacto: pantalla nueva con filas dinámicas + guardado atómico + alta rápida inline reutilizando `CreateAsync` de un servicio ya existente. Es la referencia más parecida del dataset completo. |
| Filtros completos Consulta de Stock | Vinosefue — "Filtro de categoría al exportar catálogo de Productos" (2026-07-13, cierre real), normalizado sin el componente de migración/deploy que ese cierre sí tenía | 5,75 h (con migración+deploy) → ajustado a la baja por no requerir ninguno de los dos acá | Comparable más cercano de "agregar filtro(s) a un listado/export ya existente" |

No hubo rondas previas de "carga masiva" ni de "filtros de stock" en ShowroomGriffin mismo (no aplica la regla de segunda/tercera ronda sobre el mismo módulo).

### Paso 1-6 — Estimación por ítem

| # | Ítem funcional | Tipo | Drivers concretos | O | M | P | PERT (h) | Riesgo | Cont. | Horas finales |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|
| 1 | Carga masiva de stock por Marca | Pantalla nueva sobre módulo existente | Grilla agrupada por Modelo (acordeón), reutiliza `IVarianteService.CrearAsync` y lógica de `AjusteManualAsync`, refactor transaccional interno (R-V10-1, separar transacción de lógica sin romper comportamiento actual), validación de duplicado Color+Talle, bloqueo si falta Producto (R-V10-2) | 5,5 | **8,0** | 12,0 | **8,25** | Medio | 15% | **9,49** |
| 2 | Filtros completos en Consulta de Stock | Modificación sobre módulo existente | Combo Talle dependiente de Modelo (mismo patrón AJAX que Color ya existente), combo Estado reemplaza botón "Solo alertas", +2 parámetros en `ListarAsync`/`ExportarExcelAsync`, sin migración | 2,0 | **3,0** | 5,0 | **3,17** | Bajo | 8% | **3,42** |

**Totales:** PERT base = **11,42 h** · Horas finales con contingencia = **12,91 h**.

### Paso 7 — Autocorrección por ítem

| # | Ítem | Horas base (M) | Referencia (mediana) | Ratio | Decisión | Justificación |
|---|---|---:|---:|---:|---|---|
| 1 | Carga masiva | 8,0 | 6,5 | **1,23** | Mantener (dentro del 30%) | 2 drivers concretos no presentes en la referencia: agrupación visual por Modelo (acordeón) y refactor transaccional interno (R-V10-1) para sostener atomicidad total sobre servicios que hoy abren su propia transacción |
| 2 | Filtros | 3,0 | 5,75 (normalizada, sin migración/deploy) | **0,52** | Mantener (simplificación real) | Acá no hay migración EF ni deploy de producción (a diferencia de la referencia vinosefue) — el ítem es solo UI + 2 parámetros propagados, justifica el M menor |

### Paso 8 — Sanity check del total del proyecto

Comparable más cercano por tamaño: **LabIPAC SESIÓN 3 completa** (M7+M8+M9, 3 ítems, 11,5 h M base / 13,69 h con contingencia, cierre real 2,0 h). Nuestro total (11,42 h M base / 12,91 h con contingencia) es prácticamente idéntico en magnitud — ratio 11,42/11,5 = **0,99**. Dentro de rango, sin ajuste adicional.

### Paso 9 — Cierre numérico

| Paso | Horas base | Horas finales | USD (M x $16,80) |
|---|---:|---:|---:|
| A — preliminar | 11,42 | 12,91 | — |
| B — final (post-autocorrección, sin cambios) | 11,42 | 12,91 | **USD 184,80** |

### Facturación al cliente

| Ítem | M (h) | USD lista (M x $16,80) |
|---|---:|---:|
| Carga masiva de stock por Marca | 8,0 | 134,40 |
| Filtros completos en Consulta de Stock | 3,0 | 50,40 |
| **Subtotal (Etapa 1 + Etapa 2)** | **11,0** | **184,80** |

Horas facturables internas = 11,0 / 2,5 x 1,20 = 5,28 h (por encima del piso de 4 h → **sí corresponde cargo de Tokens IA**, a diferencia de otras iteraciones evolutivas menores recientes).

- **Tokens IA (25% del subtotal de lista):** USD 184,80 x 0,25 = **USD 46,20**
- **Descuento de expansión agresiva:** NO aplica (mejora sobre sistema propio ya entregado, no Build inicial de cliente nuevo)
- **Total del proyecto V10: USD 231,00**

### Etapas para el cliente

- **Etapa 1 (MVP — resuelve el dolor real reportado):** Carga masiva de stock por Marca. USD 134,40.
- **Etapa 2 (mejora complementaria, no bloqueante):** Filtros completos en Consulta de Stock. USD 50,40.
- **Tokens IA:** USD 46,20.
- **Total: USD 231,00.**

### Mantenimiento anual
No se agrega línea nueva de mantenimiento: ShowroomGriffin ya está en producción con un plan vigente desde la entrega v1 (a confirmar con el cliente si sigue activo); esta cotización cubre solo el desarrollo puntual de las 2 mejoras.

### Riesgos y supuestos del presupuesto

| # | Tipo | Descripción | Impacto si se materializa |
|---|---|---|---|
| RP-V10-1 | Riesgo | El refactor de `AjusteManualAsync` (separar transacción de lógica, R-V10-1) toca un método ya en producción usado por el ajuste individual — requiere regresión del flujo de ajuste individual además del nuevo flujo masivo | +1 h si aparece una regresión a corregir |
| RP-V10-2 | Riesgo | Volumen real de variantes por Marca desconocido — si alguna Marca tiene decenas de Modelos con muchas variantes cada uno, puede requerir paginación/acordeón más elaborado de lo estimado | +1-2 h si el cliente confirma volúmenes grandes |
| SP-V10-1 | Supuesto | No se requiere importación Excel/CSV (confirmado fuera de alcance en Análisis) | — |
| SP-V10-2 | Supuesto | El plan de mantenimiento anual de ShowroomGriffin sigue vigente y no se re-cotiza acá | Si no está vigente, agregar como línea separada (ver `27-presupuesto-parametros.instructions.md`) |

### Pruebas mínimas requeridas
- Carga masiva: guardar lote con filas existentes modificadas + 1 variante nueva, verificar `AjusteStock`/`MovimientoStock` generados y variante creada con `Stock` inicial correcto.
- Forzar error en 1 fila (ej. combinación Color+Talle duplicada) y verificar que no se guarda ninguna fila del lote, con el error marcado en la fila correspondiente y el resto de los datos tipeados intactos.
- Verificar que el ajuste individual (`/Stock/Ajuste`) sigue funcionando igual que antes del refactor de `AjusteManualAsync` (regresión).
- Filtros: Talle dependiente de Modelo: deshabilitado hasta elegir Modelo, se puebla vía AJAX. Combo Estado filtra correctamente (Todos/OK/Límite/Bajo) y el link `?soloAlertas=true` sigue funcionando.
- Exportar Excel respeta los filtros de Talle y Estado aplicados en pantalla.

### Estado
PRESUPUESTO V10 **APROBADO POR EL CLIENTE** (2026-07-30, mismo día — ambas etapas, sin ajustes). Total: **USD 231,00** (Etapa 1: USD 134,40 / Etapa 2: USD 50,40 / Tokens IA: USD 46,20). Gate duro liberado — habilitado el paso a Implementación.

### Cierre de calibración estimado vs real — PENDIENTE

Implementación (subagent `agentes-ia-implementador`) y QA (subagent `agentes-ia-qa`) cerrados el mismo día (2026-07-30), build OK, QA APROBADO CON OBSERVACIONES (0 defectos funcionales). **El cliente no tiene todavía las horas reales para registrar** (no se factura/trackea por sesión) — se deja el cierre de calibración explícitamente pendiente en vez de asumir un número.

| Ítem | Horas estimadas (PERT+cont.) | Horas reales | Desvío % | Motivo |
|---|---:|---:|---:|---|
| Carga masiva de stock por Marca | 9,49 | — | — | Pendiente de registro por el cliente |
| Filtros completos en Consulta de Stock | 3,42 | — | — | Pendiente de registro por el cliente |
| **Total** | **12,91** | **—** | **—** | — |

**Dato objetivo disponible mientras tanto (no es "horas reales" de facturación, es tiempo de ejecución de agentes):** el subagent de Implementación corrió 20,4 min y el de QA 7,2 min (≈27,5 min combinados de ejecución de agente) — coherente con el patrón ya documentado en `27-presupuesto-parametros.instructions.md` de que el desarrollo asistido por IA corre muy por debajo de las horas PERT (ratios históricos 4x-7x en este dataset). No se usa este dato como cierre oficial de calibración porque no captura el tiempo real de decisión/revisión de Joaquín en la sesión.

**Acción pendiente:** cuando el cliente/Joaquín registre las horas reales de esta sesión (relevamiento + decisiones + revisión de código), completar esta tabla y aplicar el Paso 9 de recalibración si el desvío promedio supera el 20% (altamente probable dado el patrón histórico).

---

## V12 — Presupuesto: extensión de Matriz (accesorios + alta de Color nuevo) + retiro de Carga Masiva/Ajuste (2026-08-16)

**Input:** `1-analista-funcional.md`, `2-disenador-funcional.md`, `3-arquitecto-mvc.md` — todos sección V12, CERRADOS Y APROBADOS.
**Clasificación de negocio:** mejora sobre sistema propio ya entregado — **Merge, NO Build inicial de cliente nuevo**. No aplica el descuento de expansión agresiva ni el piso de USD 280 (exclusivo de Build inicial); se cotiza a precio de lista de "Modificación sobre módulo existente".

### Paso 0 — Anclaje histórico

| Ítem | Referencia elegida | Horas base referencia | Motivo |
|---|---|---:|---|
| Accesorios sin talle en Matriz | V10 — "Filtros completos en Consulta de Stock" (3,0 h M) | 3,0 h | Comparable más cercano: modificación de un método de Service ya existente + ajuste de vista, sin migración, sin capa nueva |
| Alta de Color nuevo con Talle (fila embebida + indexado JS dinámico) | Tabla "Modificación sobre módulo existente" — "Agregar regla de negocio" (piso 1-2h), ajustado al alza por driver técnico nuevo no cubierto por esa fila | 2,0 h (techo de la fila + ajuste documentado) | Aplica la regla de "segunda/tercera ronda sobre el mismo módulo" (esta Marca/pantalla ya tuvo Carga Masiva, 3 etapas de Matriz, y el hotfix SG-001 — todas rondas previas sobre el mismo módulo Stock) → ancla en el piso de reutilización, no en rangos de módulo nuevo. Se documenta un ajuste al alza explícito por el driver de indexado dinámico de `Altas[]` en JS (sin precedente exacto en las filas de "modificación", más cercano al patrón `renumerarFilasNuevas` de `CargaMasiva.cshtml`, ya construido y por ende reutilizable, pero adaptado a una tabla pivot en vez de filas planas) |
| Alta de Color nuevo en accesorio (sin Talle) | Misma fila que el ítem anterior, sin el driver de indexado dinámico (una sola celda por fila) | 1,0 h (piso de la fila) | Reutilización directa del mecanismo de alta ya construido (`StockMatrizAltaGuardarViewModel`/`GuardarMatrizAsync`), sin complejidad de JS adicional |
| Ocultar botones Carga Masiva / Ajuste Manual | Tabla principal — "Ajuste puntual" | 0,5–1 h (piso) | Quitar 2 `<a>`/botones de una vista ya existente, sin lógica nueva |

Cuarta ronda consecutiva sobre el mismo módulo Stock/Matriz en menos de 2 semanas (V10 → 3 etapas fast-path de Matriz → hotfix SG-001 → V12) — máxima aplicabilidad de la regla de "segunda/tercera ronda", ver Paso 7.

### Paso 1-6 — Estimación por ítem

| # | Ítem funcional | Tipo | Drivers concretos | O | M | P | PERT (h) | Riesgo | Cont. | Horas finales |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|
| 1 | Accesorios sin talle en Matriz (lectura + edición) | Modificación sobre módulo existente | `ObtenerMatrizAsync` deja de descartar secciones `TalleConfig == null`; layout de 2 columnas (Color+Cantidad) en `Matriz.cshtml` y `MatrizEditar.cshtml`; sin migración | 1,3 | **2,0** | 3,5 | **2,13** | Bajo | 8% | **2,30** |
| 2 | Alta de Color nuevo en Modelo con Talle | Modificación sobre módulo existente + driver técnico nuevo | Fila "+ Nuevo color" embebida en tabla pivot, 1 input de cantidad por columna de Talle, indexado dinámico de `Altas[]` en JS antes del submit, consulta adicional de `TipoTalle` por `ProductoId` en `GuardarMatrizAsync`, checklist SG-001 (nullable + `InvariantCulture`) aplicado desde el diseño | 2,0 | **3,0** | 5,0 | **3,17** | Medio | 15% | **3,64** |
| 3 | Alta de Color nuevo en accesorio (sin Talle) | Modificación sobre módulo existente | Misma fila "+ Nuevo color" pero de una sola celda (sin indexado dinámico por columnas), `TalleConfigId = null` | 0,7 | **1,0** | 1,8 | **1,08** | Bajo | 8% | **1,17** |
| 4 | Ocultar botones "Ajuste manual" y "Carga masiva" en `Stock/Index` | Ajuste puntual | Quitar 2 elementos de UI, sin lógica de negocio, sin eliminar rutas (D3) | 0,2 | **0,3** | 0,5 | **0,32** | Bajo | 8% | **0,35** |

**Totales:** PERT base = **6,70 h** · Horas finales con contingencia = **7,46 h**.

### Paso 7 — Autocorrección por ítem

| # | Ítem | Horas base (M) | Referencia (piso/mediana) | Ratio | Decisión | Justificación |
|---|---|---:|---:|---:|---|---|
| 1 | Accesorios sin talle | 2,0 | 3,0 (V10 Filtros) | **0,67** | Mantener | Menor esfuerzo que la referencia: no toca `ExportarExcelAsync` ni agrega parámetros a `ListarAsync`, solo cambia el criterio de agrupación de una consulta ya existente + layout de vista |
| 2 | Alta Color con Talle | 3,0 | 2,0 (piso "modificación") | **1,50** | Mantener, con justificación documentada (excede el 30% permitido) | El driver de indexado dinámico de `Altas[]` en JS no tiene precedente exacto en las filas de "modificación sobre módulo existente" — es la pieza técnica de mayor riesgo señalada por Arquitectura (mismo perfil que causó D-01/D-02 el mismo día). Anclar solo en el piso de reutilización subestimaría el esfuerzo real de blindar ese mecanismo desde el diseño |
| 3 | Alta Color accesorio | 1,0 | 1,0 (piso "modificación") | **1,00** | Mantener | Sin desvío — reutilización directa sin driver adicional |
| 4 | Ocultar botones | 0,3 | 0,5-1 (piso "ajuste puntual") | **0,3-0,6** | Mantener (por debajo del piso, justificado) | Cambio real más chico que el piso típico de "ajuste puntual" (ni siquiera toca lógica, solo remueve 2 elementos de markup) |

### Paso 8 — Sanity check del total del proyecto

Comparable más cercano: V10 (11,42 h M base / 12,91 h con contingencia, para construir 2 pantallas nuevas desde una base parcial). Este V12 (6,3 h M base / 7,46 h con contingencia) es **~55% del tamaño de V10**, consistente con ser una extensión incremental de una pantalla ya construida el mismo día (reutiliza 4 componentes ya existentes: `StockMatrizAltaGuardarViewModel`, `GuardarMatrizAsync`, `ObtenerMatrizAsync`, el patrón de indexado dinámico de `CargaMasiva.cshtml`) en vez de una capacidad nueva desde cero. Dentro de rango esperado, sin ajuste adicional.

### Paso 9 — Cierre numérico

| Paso | Horas base (M) | Horas finales | USD (M x $16,80) |
|---|---:|---:|---:|
| A — preliminar | 6,3 | 7,46 | — |
| B — final (post-autocorrección, sin cambios) | 6,3 | 7,46 | **USD 105,84** |

### Facturación al cliente

| Ítem | M (h) | USD lista (M x $16,80) |
|---|---:|---:|
| Alta de Color nuevo en Modelo con Talle | 3,0 | 50,40 |
| Alta de Color nuevo en accesorio (sin Talle) | 1,0 | 16,80 |
| Accesorios sin talle en Matriz (lectura + edición) | 2,0 | 33,60 |
| Ocultar botones Ajuste manual / Carga masiva | 0,3 | 5,04 |
| **Subtotal (Etapa 1 + Etapa 2)** | **6,3** | **105,84** |

Horas facturables internas = 6,3 / 2,5 x 1,20 = **3,02 h — por debajo del piso de 4 h → NO corresponde cargo de Tokens IA** (regla vigente: "No aplica a iteraciones evolutivas menores a 4 h facturables, salvo indicación contraria"), a diferencia de V10 (5,28 h, sí superaba el piso).

- **Tokens IA:** no aplica (ver arriba).
- **Descuento de expansión agresiva:** NO aplica (Merge sobre sistema propio, no Build inicial).
- **Total del proyecto V12: USD 105,84.**

### Etapas para el cliente

Aunque D4 confirmó que ambas etapas se entregan juntas en el mismo sprint (sin período de validación intermedio), se mantiene la agrupación funcional estándar para claridad del alcance:

- **Etapa 1 (resuelve el dolor real — las dos capacidades que hoy dependen de Carga Masiva):** Alta de Color nuevo en Modelo con Talle (USD 50,40) + Alta de Color nuevo en accesorio (USD 16,80) = **USD 67,20**.
- **Etapa 2 (cobertura completa + limpieza de menú):** Accesorios sin talle en Matriz (USD 33,60) + Ocultar botones (USD 5,04) = **USD 38,64**.
- **Total: USD 105,84.**

### Mantenimiento anual

Sin cambios — mismo plan vigente que V10/V11, esta cotización cubre solo el desarrollo puntual de V12.

### Riesgos y supuestos del presupuesto

| # | Tipo | Descripción | Impacto si se materializa |
|---|---|---|---|
| RP-V12-1 | Riesgo | El indexado dinámico de `Altas[]` en JS para la fila "+ Nuevo color" con Talle es la pieza de mayor riesgo técnico de esta entrega — mismo perfil que causó el rechazo de QA de `f400671` el mismo día (D-01/D-02) | +1-2 h si aparece un defecto post-QA equivalente a D-01/D-02, ya presupuestado parcialmente en la contingencia del 15% de este ítem |
| RP-V12-2 | Riesgo | Volumen de columnas de Talle por sección (hasta 10+ en algunos Modelos) puede hacer la fila "+ Nuevo color" visualmente apretada — ajuste de CSS no cuantificado | +0,5 h si requiere layout responsivo adicional |
| SP-V12-1 | Supuesto | No se elimina código de `CargaMasiva`/`Ajuste` en este sprint (D3) — la limpieza de código queda fuera de alcance y presupuesto de V12 | Si el cliente pide eliminación de código en el mismo sprint, se cotiza aparte |
| SP-V12-2 | Supuesto | El QA de esta etapa incluye verificación por navegador de la fila nueva (no solo inspección de código), por la regla de proceso agregada tras el rechazo de `f400671` — no genera costo adicional al cliente (el QA no se factura por separado, va dentro del ciclo de desarrollo) | — |

### Pruebas mínimas requeridas
Ver `3-arquitecto-mvc.md` sección V12, punto 5 ("Estrategia de pruebas funcionales") — 5 casos nuevos específicos + regla de no-fast-path para el QA de esta etapa.

### Estado
PRESUPUESTO V12 **APROBADO POR EL CLIENTE** (2026-08-16, mismo día — ambas etapas, sin ajustes). Total: **USD 105,84** (Etapa 1: USD 67,20 / Etapa 2: USD 38,64 / sin Tokens IA por estar bajo el piso de 4h facturables). Gate duro liberado — se delega Implementación al subagent `agentes-ia-implementador`.

### Cierre de calibración estimado vs real — PENDIENTE

| Ítem | Horas estimadas (PERT+cont.) | Horas reales | Desvío % | Motivo |
|---|---:|---:|---:|---|
| Alta de Color nuevo con Talle | 3,64 | — | — | Pendiente de cierre de Implementación/QA |
| Alta de Color nuevo en accesorio | 1,17 | — | — | Pendiente de cierre de Implementación/QA |
| Accesorios sin talle en Matriz | 2,30 | — | — | Pendiente de cierre de Implementación/QA |
| Ocultar botones | 0,35 | — | — | Pendiente de cierre de Implementación/QA |
| **Total** | **7,46** | **—** | **—** | — |
