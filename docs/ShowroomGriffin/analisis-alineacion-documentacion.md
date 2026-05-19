# 📊 ANÁLISIS DE ALINEACIÓN DE DOCUMENTACIÓN
**Proyecto:** ShowroomGriffin  
**Fecha:** 2026-04-23  
**Propósito:** Validar alineación entre documentos existentes (2, 3, 4, 6) y plan de implementación nuevo (R1-R12).

---

## 🎯 RESUMEN EJECUTIVO

### Estado General: ⚠️ **DESALINEACIÓN PARCIAL**

Los documentos existentes (`2-disenador-funcional.md`, `3-arquitecto-mvc.md`, `4-presupuestador.md`, `6-qa.md`) están basados en un **análisis funcional ANTERIOR** (v1.1) que cubre **9 módulos completos** (M1-M9 + Dashboard).

El **nuevo plan de implementación** (`5-implementador.md` recién creado) está basado en **12 requerimientos puntuales** (R1-R12) que son **EXTENSIONES** o **CAMBIOS SOBRE EL SISTEMA YA IMPLEMENTADO**.

---

## 🔍 ANÁLISIS DETALLADO POR DOCUMENTO

### 📘 2-disenador-funcional.md (349 líneas)

**Contenido:**
- Diseño funcional de **9 módulos completos** (M1-M9 + Dashboard).
- Flujo de pantallas, wireframes textuales, ViewModels.
- Máquinas de estado de Compra, Venta, Devoluciones.
- Decisiones D1-D6 del análisis funcional v1.1.

**Requerimientos del nuevo plan cubiertos:**
- ❌ **R1 (Anotaciones en Venta):** NO mencionado.
- ❌ **R2 (Modal Crear Cliente):** NO mencionado.
- ❌ **R3 (Combos anidados Ventas):** NO mencionado.
- ❌ **R4 (Autocompletar Pago):** NO mencionado.
- ❌ **R5 (Combos anidados Compras):** NO mencionado.
- ❌ **R6 (Consulta Stock rápida):** NO mencionado.
- ❌ **R7 (Cambio/Devolución):** SÍ tiene diseño de "Devoluciones" (M7), pero es diferente al R7 (cambio desde venta finalizada).
- ❌ **R8 (Rol Empleado):** Solo menciona "Vendedor", no "Empleado".
- ❌ **R9 (Importes editables):** NO mencionado (el diseño asume cálculo automático).
- ❌ **R10+R12 (Refactor Modelo):** NO mencionado (usa el modelo anterior con Marca/Modelo en VarianteProducto).
- ❌ **R11 (Talles predefinidos):** NO mencionado.

**Decisión crítica encontrada:**
> "Decisión D1: Numeración de venta: `int` autoincremental gestionado por DB."

Esto **CONTRADICE** el nuevo plan (R10+R12) donde se define que el número de venta se genera con patrón "VTA-{Id:D5}".

**Conclusión:**
- ✅ El diseño funcional existente es **VÁLIDO** para los 9 módulos base (M1-M9).
- ⚠️ **NO cubre** los nuevos requerimientos R1-R12.
- 🔴 Hay **CONTRADICCIONES** con el nuevo modelo de datos (Marca/Modelo en Producto vs VarianteProducto).

---

### 📗 3-arquitecto-mvc.md (339 líneas)

**Contenido:**
- Arquitectura técnica de los 9 módulos (M1-M9).
- Impacto por capa (Domain, Application, Infrastructure, Web).
- Decisiones técnicas: bloqueo optimista (D6), persistencia de cuotas (D2), índices únicos, transacciones.
- Migraciones EF: M1-M6.

**Requerimientos del nuevo plan cubiertos:**
- ❌ **R1:** NO cubre (nueva columna `Anotaciones` en `Venta`).
- ❌ **R2:** NO cubre (modal AJAX no mencionado).
- ❌ **R3/R5:** NO cubre (combos anidados no diseñados).
- ❌ **R4:** NO cubre.
- ❌ **R6:** NO cubre (no hay pantalla de consulta stock rápida).
- ⚠️ **R7:** Cubre "Devoluciones" (M7) pero NO "Cambio/Devolución desde venta finalizada".
- ⚠️ **R8:** Cubre rol "Vendedor" pero NO rol "Empleado".
- ❌ **R9:** NO cubre (asume importes automáticos).
- 🔴 **R10+R12:** **CONTRADICE** el nuevo modelo:
  - Documento existente: Marca/Modelo en `VarianteProducto`.
  - Nuevo plan: Marca/Modelo en `Producto`.
- ❌ **R11:** NO cubre (no hay entidad `TalleZapatilla`).

**Decisiones técnicas clave encontradas:**

| Decisión | Doc Existente | Nuevo Plan R10+R12 | Alineación |
|----------|---------------|---------------------|------------|
| **Marca/Modelo** | En `VarianteProducto` | En `Producto` | 🔴 **CONTRADICTORIO** |
| **Numeración Venta (D1)** | `int` autogenerado DB → `NroVenta = $"VTA-{Id:D5}"` (two-save) | Migración M2 define `M2_RefactorProductoMarcaModelo` | ⚠️ Diferente |
| **RowVersion (D6)** | En `VarianteProducto` para aumento masivo | Mismo | ✅ Alineado |
| **Transacciones** | `IsolationLevel.Serializable` en Venta, Compra, Devolución | Mismo | ✅ Alineado |

**Migraciones definidas:**

| Doc Existente | Nuevo Plan |
|---------------|------------|
| M1-M6 (para 9 módulos base) | M2-M5 (para R1, R11, R10+R12, R7) |

⚠️ **CONFLICTO DE NUMERACIÓN**: Los documentos existentes usan M1-M6, el nuevo plan usa M2-M5. Hay que **renumerar**.

**Conclusión:**
- ✅ La arquitectura existente es **VÁLIDA** para los 9 módulos base.
- 🔴 **CONTRADICE** el nuevo modelo de datos (R10+R12).
- ⚠️ Las migraciones deben **re-numerarse** para evitar conflictos.

---

### 📙 4-presupuestador.md (241 líneas)

**Contenido:**
- Presupuesto PERT de los 9 módulos base.
- Total: **101.1 horas** / **USD 1,415**.
- Estimación detallada por módulo con autocorrección contra dataset histórico.

**Requerimientos del nuevo plan cubiertos:**
- ❌ **R1-R12:** NO presupuestados (son extensiones posteriores).

**Comparación:**

| Concepto | Doc Existente (9 módulos base) | Nuevo Plan (R1-R12) |
|----------|--------------------------------|---------------------|
| **Total horas** | 101.1 h | 49 h (~6.5 días) |
| **Total USD** | USD 1,415 | (No calculado en nuevo plan) |
| **Alcance** | Sistema completo (M1-M9 + Dashboard) | Extensiones sobre sistema existente |

**Conclusión:**
- ✅ El presupuesto existente es **VÁLIDO** para el sistema base.
- ⚠️ Los nuevos requerimientos R1-R12 requieren **presupuesto adicional** (49 horas).
- ⚠️ **TOTAL ACUMULADO**: 101.1 h (base) + 49 h (nuevas) = **150.1 horas**.

---

### 📕 6-qa.md (362 líneas)

**Contenido:**
- Plan de QA de los 9 módulos base.
- Criterios de aceptación (M1-CA-01 a M9-CA-06).
- Estado: mayoría `PASS-CR` (revisión de código) o `BLOCKED` (requiere smoke tests).
- Máquinas de estado validadas (Compra, Venta, Devolución).

**Requerimientos del nuevo plan cubiertos:**
- ❌ **R1-R12:** NO cubiertos (no hay casos de prueba para estas extensiones).

**Conclusión:**
- ✅ El plan de QA existente es **VÁLIDO** para el sistema base.
- ⚠️ Los nuevos requerimientos R1-R12 requieren **casos de prueba adicionales**.

---

## 🚨 CONFLICTOS CRÍTICOS DETECTADOS

### 🔴 CONFLICTO #1: Modelo de Datos (R10+R12 vs Docs Existentes)

| Concepto | Docs Existentes (2, 3, 4, 6) | Nuevo Plan (R10+R12) |
|----------|------------------------------|----------------------|
| **Marca** | En `VarianteProducto` | En `Producto` |
| **Modelo** | En `VarianteProducto` | En `Producto` |
| **Impacto** | 20 entidades ya implementadas | Requiere migración M4 (refactor crítico) |

**Decisión requerida:**
- ¿El sistema base YA ESTÁ IMPLEMENTADO con Marca/Modelo en `VarianteProducto`?
- Si SÍ → R10+R12 **DEBE ejecutarse** (refactor crítico) antes de R3/R5.
- Si NO → el nuevo plan (R10+R12) es la **versión correcta** y los docs existentes deben actualizarse.

---

### ⚠️ CONFLICTO #2: Numeración de Migraciones EF

| Doc | Migraciones Definidas |
|-----|-----------------------|
| Arquitectura existente (3) | M1-M6 |
| Nuevo plan (5) | M2-M5 |

**Decisión requerida:**
- Renumerar migraciones del nuevo plan como **M7-M10** para evitar conflictos.
- O renumerar docs existentes.

---

### ⚠️ CONFLICTO #3: Alcance de "Devoluciones"

| Doc | Definición |
|-----|------------|
| Docs existentes (M7) | Módulo completo de "Devoluciones y Cambios" con wizard 4 pasos |
| Nuevo plan (R7) | "Cambio/Devolución desde detalle de venta finalizada" |

**Decisión requerida:**
- ¿R7 es una **extensión** de M7?
- ¿O R7 **reemplaza** a M7?

---

### ⚠️ CONFLICTO #4: Rol "Empleado" vs "Vendedor"

| Doc | Rol Definido |
|-----|--------------|
| Docs existentes | `Vendedor` (acceso a Ventas, sin Compras/Maestros) |
| Nuevo plan (R8) | `Empleado` (acceso a Ventas, Cambios, Stock) |

**Decisión requerida:**
- ¿Son roles **diferentes**?
- ¿O "Empleado" **reemplaza** a "Vendedor"?

---

## 📋 RECOMENDACIONES

### ✅ Recomendación #1: Clarificar Estado del Sistema

**Preguntas clave para el cliente:**

1. **¿El sistema base (M1-M9 + Dashboard) YA ESTÁ IMPLEMENTADO?**
   - Si SÍ → Los docs existentes son la "versión 1.0" y R1-R12 son "versión 1.1".
   - Si NO → Hay confusión de versiones.

2. **¿La estructura de datos actual tiene Marca/Modelo en `VarianteProducto` o en `Producto`?**
   - Si en `VarianteProducto` → R10+R12 es **refactor obligatorio**.
   - Si en `Producto` → Los docs existentes están desactualizados.

3. **¿El módulo de "Devoluciones" (M7) ya existe?**
   - Si SÍ → R7 es una **extensión**.
   - Si NO → Hay duplicación de alcance.

---

### ✅ Recomendación #2: Renumerar Migraciones

**Propuesta:**
- Migraciones del sistema base (docs existentes): **M1-M6**.
- Migraciones del nuevo plan (R1-R12): **M7-M10**.

| Nueva Numeración | Migración | Requerimiento |
|------------------|-----------|---------------|
| **M7** | `AgregarAnotacionesVenta` | R1 |
| **M8** | `AgregarTalleZapatilla` | R11 |
| **M9** | `RefactorProductoMarcaModelo` | R10+R12 |
| **M10** | `AgregarVentaCambio` | R7 |

---

### ✅ Recomendación #3: Actualizar Plan de Implementación

**Opción A: Sistema Base YA Implementado**

Si el sistema base (M1-M9) ya está en producción:

1. **Validar** que el modelo de datos actual coincide con los docs existentes.
2. **Ejecutar R10+R12 PRIMERO** (refactor crítico de Marca/Modelo).
3. Luego ejecutar el resto de R1-R12 en el orden definido (FASE 1 → FASE 2 → FASE 3).
4. **Actualizar presupuesto** sumando 49 horas adicionales (total ~150 h).

**Opción B: Sistema Base NO Implementado**

Si el sistema base NO está implementado:

1. **Corregir** los docs existentes (2, 3, 4) para alinear con el nuevo modelo (Marca/Modelo en Producto).
2. Implementar primero M1-M9 (docs existentes corregidos).
3. Luego implementar R1-R12.

---

### ✅ Recomendación #4: Consolidar Documentación

**Crear archivo de trazabilidad de versiones:**

```
C:\Sistemas\Agentes-IA\docs\ShowroomGriffin\CHANGELOG.md
```

Con contenido:

```markdown
# CHANGELOG - ShowroomGriffin

## [1.1] - 2026-04-23 (NUEVA - R1-R12)
- R1: Campo Anotaciones en Venta.
- R2: Modal Crear Cliente desde Venta.
- R3: Combos anidados en Ventas.
- R4: Autocompletar Pago.
- R5: Combos anidados en Compras.
- R6: Consulta Stock rápida.
- R7: Cambio/Devolución desde venta finalizada.
- R8: Rol Empleado.
- R9: Importes editables en Venta.
- R10+R12: Refactor Modelo (Marca/Modelo a Producto).
- R11: Maestro Talles predefinidos.

## [1.0] - 2026-04-XX (BASE - M1-M9)
- M1: Seguridad y Acceso.
- M2: Maestros Comerciales.
- M3: Productos y Variantes.
- M4: Stock e Inventario.
- M5: Compras a Proveedores.
- M6: Ventas a Clientes.
- M7: Devoluciones y Cambios.
- M8: Resumen Semanal.
- M9: Aumento Masivo.
- Dashboard.
```

---

## 🎯 PRÓXIMOS PASOS CRÍTICOS

### 1️⃣ Validar Estado del Sistema (URGENTE)

Ejecutar contra la base de datos de desarrollo:

```sql
-- Verificar si las tablas del sistema base existen
SHOW TABLES LIKE '%Venta%';
SHOW TABLES LIKE '%Compra%';
SHOW TABLES LIKE '%Producto%';
SHOW TABLES LIKE '%VarianteProducto%';

-- Verificar estructura de VarianteProducto
DESCRIBE VarianteProducto;

-- Buscar columnas Marca y Modelo
SHOW COLUMNS FROM VarianteProducto LIKE 'Marca';
SHOW COLUMNS FROM VarianteProducto LIKE 'Modelo';

-- Verificar si existen migraciones aplicadas
SELECT * FROM __EFMigrationsHistory;
```

**Resultado esperado:**
- Si hay datos → Sistema base YA implementado.
- Si Marca/Modelo están en `VarianteProducto` → R10+R12 es refactor obligatorio.
- Si Marca/Modelo están en `Producto` → Los docs existentes están desactualizados.

---

### 2️⃣ Decisión del Cliente

**Preguntar al cliente:**

> "Hola, detecté que hay documentación existente (diseño, arquitectura, presupuesto, QA) para un sistema base de 9 módulos (101 horas), y ahora tenés un pedido de 12 nuevos requerimientos (49 horas adicionales).
>
> **Preguntas:**
> 1. ¿El sistema base (M1-M9) ya está implementado y en producción?
> 2. ¿La estructura actual tiene Marca y Modelo en la tabla `VarianteProducto` o en `Producto`?
> 3. ¿El módulo de Devoluciones (M7) ya existe, o R7 (Cambio/Devolución) es nuevo?
> 4. ¿El rol 'Empleado' (R8) es diferente del rol 'Vendedor' existente?"

---

### 3️⃣ Actualizar Plan de Implementación

Según las respuestas del cliente:

- **Escenario A (Sistema base ya implementado):**
  - Renumerar migraciones del nuevo plan como M7-M10.
  - Ejecutar FASE 1 → FASE 2 → FASE 3.
  - Presupuesto adicional: 49 horas.

- **Escenario B (Sistema base NO implementado):**
  - Corregir docs existentes (alinear con R10+R12).
  - Implementar primero M1-M9.
  - Luego implementar R1-R12.
  - Presupuesto total: ~150 horas.

---

## 📊 TABLA RESUMEN DE ALINEACIÓN

| Doc | Versión | Alcance | Alineación con R1-R12 | Acción Requerida |
|-----|---------|---------|------------------------|------------------|
| **1-analista-funcional.md** | Nuevo (2026-04-23) | R1-R12 | ✅ Base del nuevo plan | Ninguna |
| **2-disenador-funcional.md** | Existente v1.0 | M1-M9 | 🔴 NO alineado (modelo diferente) | Actualizar o crear v1.1 |
| **3-arquitecto-mvc.md** | Existente v1.0 | M1-M9 | 🔴 CONTRADICE R10+R12 | Actualizar o crear v1.1 |
| **4-presupuestador.md** | Existente v1.0 | M1-M9 (101 h) | ⚠️ Requiere presupuesto adicional (49 h) | Crear adendum v1.1 |
| **5-implementador.md** | Nuevo (2026-04-23) | R1-R12 | ✅ Plan completo | Validar con cliente |
| **6-qa.md** | Existente v1.0 | M1-M9 | ⚠️ Requiere casos de prueba adicionales | Crear adendum v1.1 |

---

**Fin del análisis. Esperando decisión del cliente para proceder.** 🚀
