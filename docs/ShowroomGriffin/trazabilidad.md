# 🏗️ Trazabilidad de Conversación - ShowroomGriffin
**Proyecto:** ShowroomGriffin  
**Fecha inicio:** 2026-04-23  
**Última actualización:** 2026-05-20  

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
| **QA** | `6-qa.md` | ⏳ Pendiente |

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

## 🚦 Próximas Acciones Requeridas

### ⚠️ Bloqueador Actual

**ETAPA 0 completada**, pero antes de continuar con ETAPA 1 (implementación técnica), se requiere:

1. ✅ **Análisis funcional aprobado** → `1-analista-funcional.md` creado.
2. ❌ **Diseño funcional aprobado** → `2-disenador-funcional.md` **NO EXISTE**.
3. ❌ **Arquitectura técnica aprobada** → `3-arquitecto-mvc.md` **NO EXISTE**.
4. ❌ **Presupuesto aprobado** → `4-presupuestador.md` **NO EXISTE**.

**Recomendación:**

🛑 **DETENER IMPLEMENTACIÓN** hasta que:

- El **Diseñador Funcional** genere mockups y flujos de pantallas (`2-disenador-funcional.md`).
- El **Arquitecto MVC** defina decisiones técnicas de implementación (`3-arquitecto-mvc.md`).
- El **Presupuestador** estime horas y riesgos (`4-presupuestador.md`).

**Alternativa:**

Si el usuario prefiere **avanzar directo a implementación** sin diseño/arquitectura previos, se asume el riesgo de:
- Retrabajo si el diseño cambia.
- Decisiones técnicas subóptimas.
- Estimación de esfuerzo imprecisa.

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

## 🔗 Referencias

- **Código fuente:** `C:\Sistemas\ShowroomGriffin\`
- **Repositorio:** `https://gitlab.com/olvidata/ShowroomGriffin`
- **Branch actual:** `main`
- **Documentación de análisis funcional:** `/docs/ShowroomGriffin/definiciones/1-analista-funcional.md`
- **Plan de implementación:** (generado en conversación, pendiente de guardar como archivo).

---

**Fin del documento - Trazabilidad**
