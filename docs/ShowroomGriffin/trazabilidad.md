# 🏗️ Trazabilidad de Conversación - ShowroomGriffin
**Proyecto:** ShowroomGriffin  
**Fecha inicio:** 2026-04-23  
**Última actualización:** 2026-07-02  

---

## 📌 Propósito de este Documento

Este archivo registra la trazabilidad de las conversaciones con el usuario, decisiones tomadas y el estado del ciclo de vida de cada feature (análisis → diseño → arquitectura → presupuesto → implementación → QA).

---

## 🔄 Estado del Proyecto

| Agente | Archivo | Estado |
|--------|---------|--------|
| **Analista Funcional** | `1-analista-funcional.md` | ✅ Creado (2026-04-23) |
| **Diseñador Funcional** | `2-disenador-funcional.md` | ✅ Completado |
| **Arquitecto MVC** | `3-arquitecto-mvc.md` | ✅ Completado |
| **Presupuestador** | `4-presupuestador.md` | ✅ Cerrado (2026-05-20) |
| **Implementador** | `5-implementador.md` | ✅ Completado |
| **QA** | `6-qa.md` | ✅ Completado (2026-05-18, BLOCKED items pendientes smoke manual) |

---

## 📋 Cierre de Sprint — Calibración Real

### Entrada 2026-05-20 — Cierre presupuestador

| Campo | Valor |
|---|---|
| **Fecha** | 2026-05-20 |
| **Agente / Etapa** | Presupuestador — Cierre de calibración |
| **Horas estimadas** | 101,1 h (con contingencia variable) |
| **Horas reales** | 25 h |
| **Desvío total** | −75,2 % |
| **Tasa recalibrada** | USD 40 / hora |
| **Costo real facturado** | USD 1.000 (25 h × USD 40) |
| **Motivo desvío** | Sobreestimación sistémica del M y P en los ítems PERT; el proyecto resultó significativamente más acotado en ejecución. Tracking granular por módulo no registrado. |
| **Impacto** | Recalibrar `27-presupuesto-parametros.instructions.md`: reducir rangos M y P para proyectos similares (ABM + workflow MVC); revisar multiplicadores de contingencia alta. |
| **Acción requerida** | Recalibrar dataset histórico con: base real = 25 h / 11 módulos ≈ 2,3 h/módulo promedio. |

---

### Entrada 2026-07-02 — QA puntual V9 (fast-path redirect post-ajuste de stock)

| Campo | Valor |
|---|---|
| **Fecha** | 2026-07-02 |
| **Agente / Etapa** | QA — verificación puntual de cambio acotado |
| **Feature** | V9 — `StockController.Ajuste` (POST) redirige a `Stock/Ajuste` en vez de `Stock/Index` tras un ajuste exitoso |
| **Alcance QA** | Cambio de una línea, sin regresión completa del proyecto (a pedido explícito). Verificación por inspección de código (controller, service, vista, layout) + build verde. |
| **Resultado** | **APROBADO**, 5/5 criterios PASS, 0 defectos, 0 auto-fixes. Diff coincide exactamente con lo documentado en `3-arquitecto-mvc.md` y `5-implementador.md` (sección V9 en ambos). |
| **Detalle** | Ver `6-qa.md` sección "V9 — Redirect post-ajuste de stock" y memoria acumulativa. |

---

## 📋 Features en Proceso

### Feature 1: Refactor del Modelo + 10 Funcionalidades

**Fecha de solicitud:** 2026-04-23  
**Solicitado por:** Usuario (pedido multi-funcionalidad)  
**Agente responsable actual:** Analista Funcional  

**Contenido del pedido:**

El usuario requirió en una sola solicitud:

1. Agregar campo **Anotaciones** en Venta.
2. Modal para **Crear Cliente** desde Venta.
3. **Combos anidados** para selección de productos en Ventas (Marca → Modelo → Color → Talle).
4. **Autocompletar importe** de pago con el total de la venta.
5. **Combos anidados** para selección de productos en Compras.
6. Pantalla **Consulta Stock** rápida.
7. **Cambio/Devolución** desde detalle de venta finalizada.
8. Rol **Empleado** con acceso restringido.
9. **Importes editables manualmente** en Venta.
10. **Refactor del modelo:** quitar Marca/Modelo de `VarianteProducto` → moverlos a `Producto`.
11. Configurar catálogo de **talles predefinidos**.
12. **Redefinición conceptual:** Categorías = Indumentaria/Zapatillas/Accesorios, Subgrupos = Marcas, Variantes = Modelo+Color+Talle.

**Decisiones funcionales tomadas:**

- ✅ **Decisión #1:** Modelo Producto + Variantes (justificado en `1-analista-funcional.md`).
- ✅ **Decisión #2:** Refactor Marca/Modelo de VarianteProducto a Producto (justificado en `1-analista-funcional.md`).

**Requerimientos funcionales identificados:**

- **R1:** Campo Anotaciones en Venta.
- **R2:** Modal Crear Cliente.
- **R3:** Combos anidados en Ventas.
- **R4:** Autocompletar importe de pago.
- **R5:** Combos anidados en Compras.
- **R6:** Pantalla Consulta Stock.
- **R7:** Cambio/Devolución de Ventas.
- **R8:** Rol Empleado.
- **R9:** Importes editables manualmente.
- **R10 + R12:** Refactor del modelo (Marca/Modelo a Producto).
- **R11:** Maestro de talles predefinidos.

**Preguntas pendientes de validación con el usuario:**

- ❓ **P1:** ¿Cambios/devoluciones requieren aprobación de supervisor?
- ❓ **P2:** ¿Edición manual de precios requiere doble autorización?
- ❓ **P3:** ¿Existe límite de descuento en edición manual?
- ❓ **P4:** ¿Rol Empleado puede ajustar stock?
- ❓ **P5:** ¿Consulta Stock debe permitir exportación a Excel/PDF?

**Estado actual:**

- ✅ **Análisis funcional completado** (`1-analista-funcional.md`).
- ⏳ **Esperando aprobación del cliente** de las decisiones y requerimientos.
- ⏳ **Pendiente:** Diseño funcional (mockups, flujos).
- ⏳ **Pendiente:** Arquitectura técnica (decisiones de implementación).
- ⏳ **Pendiente:** Presupuesto (estimación de horas).
- ⏳ **Pendiente:** Implementación (ETAPA 1 en adelante).

**Próximos pasos:**

1. Usuario valida las decisiones funcionales y responde las preguntas pendientes (P1-P5).
2. Si aprueba, derivar al **Diseñador Funcional** para generar `2-disenador-funcional.md`.
3. Luego derivar al **Arquitecto MVC** para `3-arquitecto-mvc.md`.
4. Luego derivar al **Presupuestador** para `4-presupuestador.md`.
5. Finalmente, el **Implementador** ejecuta las etapas de desarrollo.

---

## 📝 Historial de Conversaciones

### Conversación 1: Modelo Producto + Variantes (2026-04-23)

**Pregunta del usuario:**
> "Por qué fue que elegimos hacer variantes de productos en vez de productos en sí categorizados y qué diferencia hay estructuralmente en un producto categorizado como zapatilla y una categoría zapatillas con variantes del producto?"

**Respuesta del Agente Analista Funcional:**

Se explicó la diferencia entre:
- **Opción A (descartada):** modelo plano (producto categorizado) → explosión de filas, sin agrupador.
- **Opción B (elegida):** modelo Producto + Variantes → identidad comercial única, stock/precio en la variante.

**Justificación funcional:**
- Stock y precio viven en la unidad correcta (VarianteProducto).
- Facilita aumentos masivos de precio.
- Reportes distinguen ventas del modelo vs ventas de un talle específico.

**Decisión registrada en:** `1-analista-funcional.md` (Decisión #1).

**Estado:** ✅ Explicado y documentado.

---

### Conversación 2: Pedido de Plan de Implementación (2026-04-23)

**Pedido del usuario:**
> "Armar un plan de implementación para los siguientes cambios: [lista de 12 cambios]"

**Respuesta del Agente Implementador:**

Se generó un **Plan de Implementación** completo con:
- Alcance funcional resumido (12 requerimientos).
- Análisis de impacto por capas (Domain, Infrastructure, Application, Web).
- Plan de ejecución en 8 etapas técnicas.
- Migraciones EF requeridas (M2, M3, M4, M5).
- Evidencia de build y pruebas mínimas.
- Riesgos y supuestos.
- Checklist de salida para merge.

**Estado:** ✅ Plan generado, esperando que el usuario inicie ETAPA 0.

---

### Conversación 3: Inicio de ETAPA 0 (2026-04-23)

**Pedido del usuario:**
> "etapa 0"

**Acción del Agente Implementador:**

1. ✅ Verificó estructura de carpetas `/docs/ShowroomGriffin/definiciones/`.
2. ✅ Creó la carpeta (no existía).
3. ✅ Creó `1-analista-funcional.md` con:
   - Decisiones funcionales registradas (#1 y #2).
   - 12 requerimientos funcionales detallados (R1-R12).
   - 5 preguntas pendientes de validación (P1-P5).
   - Banderas tempranas (requiere migración EF, no requiere integración externa, requiere máquina de estados parcial).
   - Supuestos y restricciones.
   - Trazabilidad de cambios.
4. ✅ Creó `trazabilidad.md` (este archivo) para tracking del ciclo de vida.

**Estado actual de ETAPA 0:** ✅ **COMPLETADA**.

**Próximo paso:** Validar si existen archivos `2-disenador-funcional.md`, `3-arquitecto-mvc.md`, `4-presupuestador.md` aprobados.  
Si no existen, **detener implementación** y solicitar al usuario que active los agentes correspondientes.

---

## 🚦 Estado al Cierre (2026-05-18)

**Proyecto entregado a producción.** Ciclo completo completado:

1. ✅ Análisis funcional — `1-analista-funcional.md`
2. ✅ Diseño funcional — `2-disenador-funcional.md`
3. ✅ Arquitectura MVC — `3-arquitecto-mvc.md`
4. ✅ Presupuesto + calibración — `4-presupuestador.md` (cerrado 2026-05-20)
5. ✅ Implementación E0-E8 — `5-implementador.md` (incluye V6 + V7)
6. ✅ QA — `6-qa.md` (completado, items BLOCKED pendientes smoke manual en producción)

### Entradas post-entrega (2026-05-18)

#### V6 — Refactor modelo: Producto como entidad base (2026-05-18)
- `Producto` pierde `MarcaId`; la marca se resuelve via `Modelo.MarcaId`.
- `ModeloId` en `Producto` pasa a NOT NULL requerido.
- `VarianteProducto` elimina campos redundantes (Marca, Modelo, Numero, Talle, Temporada texto libre); reemplazados por `TalleConfigId` (FK catalogo), Color, Genero.
- Servicios actualizados: Aumento/Stock/Venta/Compra/Devolucion.
- EF Migration: `V6_RemoveRedundantFields`. Scripts SQL idempotentes para prod en `Migrations/Scripts/`.

#### V7 — Modelo con TipoTalle y TipoPrecio (2026-05-18)
- `Modelo` define `TipoTalle` (enum) y `TipoPrecioZapatillaId` (FK).
- `IModeloService` ampliado. `ModeloConfiguration` actualizado con indices.
- EF Migration: `V7_ModeloTipoTalleYPrecio`.
- Vistas `Modelos/Crear` y `Modelos/Editar` nuevas.
- `Cliente` con campo adicional. `VarianteProducto` con `RowVersion` (concurrencia optimista).

#### V9 — Redirect post-ajuste de stock (2026-07-02)
- `StockController.Ajuste` (POST): tras ajuste exitoso, redirige a `Stock/Ajuste` (GET) en vez de `Stock/Index`, para permitir cargar ajustes de varios productos sin renavegar.
- Cambio de una linea, sin migracion EF, sin cambios de permisos/validaciones.
- Build: OK, 0 errores.

---

## 📊 Métricas del Feature

| Métrica | Valor |
|---------|-------|
| **Total de requerimientos** | 12 (R1-R12) |
| **Requerimientos críticos** | 2 (R10+R12: Refactor Modelo, R7: Cambios/Devoluciones) |
| **Migraciones EF requeridas** | 4 (M2, M3, M4, M5) |
| **Migraciones de alto riesgo** | 1 (M2: RefactorProductoMarcaModelo) |
| **Preguntas pendientes** | 5 (P1-P5) |
| **Capas afectadas** | 4 (Domain, Infrastructure, Application, Web) |
| **Nuevas entidades** | 2 (`VentaCambio`, `TalleZapatilla`) |
| **Nuevos controllers** | 2 (`VentaCambiosController`, `StockController`) |
| **Estimación de complejidad** | 🔴 Alta (refactor de modelo + lógica de negocio compleja) |

---

## 📌 Entrada 2026-07-23 — Barrido cross-proyecto: mergeados runbook + metadata + as-built desde memoria local del repo

- **Cambio**: se detecto que `C:\Sistemas\ShowroomGriffin\docs\` (repo local del proyecto) tenia contenido no reflejado en Agentes-IA:
  1. Runbook operativo de migraciones en produccion (host `mysql5045.site4now.net`, credenciales, Camino A/B, rollback, script `Apply-ProdMigrations.ps1`) → copiado a `docs/ShowroomGriffin/runbook-migraciones-produccion.md` (no existia ningun runbook centralizado para este proyecto).
  2. `metadata.md` local (snapshot 2026-05-19) mucho mas completo y actualizado que el central (dated 2026-04-23, con items "⏳ Pendiente" ya completados) → `metadata.md` central reemplazado por el contenido as-built, preservando las decisiones tecnicas historicas del documento viejo en una seccion dedicada.
  3. Resumen as-built de convenciones/decisiones por modulo + tabla de etapas E0-E5 (que no existia en el plan pre-implementacion R1-R12 ya guardado en `5-implementador.md`) → agregado como seccion nueva al final de `definiciones/5-implementador.md`.
- **Motivo**: pedido explicito del usuario de auditar cada carpeta de proyecto individual en busca de especificaciones que debieran vivir en la memoria centralizada de Agentes-IA, y mergearlas.
- **Impacto en capas**: N/A (documentos de memoria/operativos).
- **Riesgos/supuestos**: el runbook copiado contiene una credencial de produccion en texto plano (ya presente en el repo del proyecto) — considerar rotarla periodicamente. Sigue pendiente sincronizar `2-disenador-funcional.md`/`3-arquitecto-mvc.md` con el modelo final (ver `analisis-alineacion-documentacion.md` para el detalle de discrepancias no resueltas).

---

## 🔗 Referencias

- **Código fuente:** `C:\Sistemas\ShowroomGriffin\`
- **Repositorio:** `https://gitlab.com/olvidata/ShowroomGriffin`
- **Branch actual:** `main`
- **Documentación de análisis funcional:** `/docs/ShowroomGriffin/definiciones/1-analista-funcional.md`
- **Plan de implementación:** (generado en conversación, pendiente de guardar como archivo).

---

**Fin del documento - Trazabilidad**
