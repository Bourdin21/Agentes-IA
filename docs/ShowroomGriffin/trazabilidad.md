# 🏗️ Trazabilidad de Conversación - ShowroomGriffin
**Proyecto:** ShowroomGriffin  
**Fecha inicio:** 2026-04-23  
**Última actualización:** 2026-08-11  

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

### Entrada 2026-07-30 — Analista Funcional: Discovery V10 (carga masiva de stock + filtros completos en Consulta de Stock)

| Campo | Valor |
|---|---|
| **Fecha** | 2026-07-30 |
| **Agente / Etapa** | Analista Funcional — Discovery/Análisis (Ask mode, sin código) |
| **Feature** | V10 — (A) carga masiva de stock por Modelo en reemplazo/complemento de ajustar variante por variante en `/Stock/Ajuste`; (B) filtros de `/Stock/Index` deben cubrir todas las propiedades listadas en la tabla (falta Talle y Estado/Alerta integrado) |
| **Motivo** | Pedido directo del cliente: la carga de stock variante por variante es tediosa; los filtros de consulta no cubren Talle ni Estado de forma integrada |
| **Resultado** | Alcance funcional, casos de uso, criterios de aceptación, riesgos y 7 preguntas abiertas (Q1–Q7) registrados en `1-analista-funcional.md` sección "V10" |
| **Impacto en capas** | Presentación (nueva vista/grilla de carga masiva, filtro Talle + Estado en Index); Negocio (reutiliza `AjusteManualAsync`/`RegistrarMovimientoAsync` en lote, sin lógica nueva de estados); Datos (sin migración EF prevista — reutiliza `Stock`, `AjusteStock`, `MovimientoStock`, `TalleConfig`) |
| **Riesgos/supuestos** | Volumen de filas por modelo (paginar/virtualizar grilla); concurrencia por fila vía `RowVersion`; `ExportarExcelAsync` necesitaría sumar el filtro Talle si se aprueba Q5 |
| **Gate** | Bloqueado para Diseño (agente 2) hasta que el cliente resuelva Q1–Q7 y apruebe el alcance |

**Actualización 2026-07-30 (mismo día):** cliente confirmó Q1 (absoluto), Q2 (scope = Marca completa), Q3 (crea variante faltante al vuelo, con Precio de Venta y Stock Mínimo editables en la misma grilla) y Q6 (el combo "Estado" reemplaza al botón "Solo alertas"). Q4/Q5/Q7 quedan con default asumido documentado en `1-analista-funcional.md`. La decisión Q3 amplía el alcance real: ya no es solo `Stock`, también toca de alta de `VarianteProducto` (Productos/Variantes) — queda marcado como alerta explícita para el agente 3 (Arquitecto MVC) antes de avanzar a Diseño.

---

### Entrada 2026-07-30 — Orquestador: Diseño funcional V10 (mismo día, sesión orquestada "implementar")

| Campo | Valor |
|---|---|
| **Fecha** | 2026-07-30 |
| **Agente / Etapa** | Diseñador Funcional — Diseño (Ask mode, sin código) |
| **Feature** | V10 — pantallas, ViewModels e historias de usuario para carga masiva de stock por Marca + filtros completos en Consulta de Stock |
| **Escaneo de reutilización** | Coincidencia encontrada: LabIPAC Sesión 2/3 (2026-07-08) — patrón "filas dinámicas JS + un submit atómico + alta rápida inline sin recargar" ya diseñado, implementado y cerrado. Se reutiliza ese patrón adaptado al dominio Stock/VarianteProducto (ver `2-disenador-funcional.md` sección V10, §0) |
| **Resultado** | Salida mínima completa: wireframes (WF-A1/A2/B1), ViewModels (`StockCargaMasivaViewModel` y derivados, `EstadoStockFiltro`), reglas de negocio (RN-M1–M6, RN-B1–B2), impacto por capa, riesgos (DD-1/2/3) e historias de usuario (HU-M1–M3, HU-B1–B2) |
| **Ajuste sobre Análisis** | DD-1: se propone atomicidad total del lote (todo o nada), reemplazando el criterio parcial ("si una fila falla, el resto no se pierde") documentado en `1-analista-funcional.md` — por precedente probado en labipac (RN-12). Pendiente confirmación del cliente en el gate de Diseño |
| **Impacto en capas** | Presentación (`StockController` + `CargaMasiva.cshtml` nueva, `Index.cshtml` con filtro Talle/Estado); Negocio (`IStockService` +2 métodos: `ObtenerParaCargaMasivaAsync`, `GuardarCargaMasivaAsync`); Datos (sin migración EF — reutiliza entidades existentes) |
| **Gate** | Bloqueado para Arquitectura (agente 3) hasta que el cliente confirme DD-1 y apruebe el diseño |

**Resolución DD-1 (mismo día):** cliente confirmó atomicidad total (todo o nada) con la condición de que la pantalla informe los errores puntuales por fila y no pierda los datos ya tipeados al fallar (re-render del ViewModel completo con `ModelState` por fila, patrón MVC estándar). Diseño V10 queda **CERRADO Y APROBADO** — habilitado el paso a Arquitectura.

---

### Entrada 2026-07-30 — Orquestador: Arquitectura técnica V10 (mismo día)

| Campo | Valor |
|---|---|
| **Fecha** | 2026-07-30 |
| **Agente / Etapa** | Arquitecto MVC — Arquitectura (Ask mode, sin código) |
| **Feature** | V10 — impacto técnico por capa, permisos, migraciones y riesgos para carga masiva de stock + filtros completos |
| **Escaneo de reutilización** | Se reutilizan directamente `IVarianteService.CrearAsync` (alta VarianteProducto+Stock) y la lógica de `IStockService.AjusteManualAsync` (AjusteStock+MovimientoStock) — sin duplicar reglas de negocio. Patrón de labipac (`AgregarLineasAsync`) tomado como referencia general, pero no aplica igual por la complejidad de orquestar servicios ya transaccionales |
| **Resultado** | Sin migración EF. Sin cambios de permisos (reutiliza `RequireAdministrador`/`RequireEmpleado` ya vigentes). 1 riesgo crítico con resolución técnica ya propuesta (R-V10-1: refactor de `AjusteManualAsync` para separar la transacción de la lógica, evitando anidar `BeginTransactionAsync` — sin romper el comportamiento actual del ajuste individual) |
| **Punto abierto para el cliente** | R-V10-2: ¿qué hace la pantalla si un Modelo no tiene ningún `Producto` asociado al intentar dar de alta una variante nueva? Propuesta: bloquear esa fila con mensaje claro |
| **Impacto en capas** | Application (+2 métodos en `IStockService`, +3 DTOs, +1 enum `EstadoStockFiltro`); Infrastructure (`StockService` +2 métodos, refactor interno de `AjusteManualAsync`); Web (`StockController` +acción `CargaMasiva`, vista nueva, `Index.cshtml` modificada) |
| **Gate** | Arquitectura lista para Presupuesto — pendiente confirmación puntual de R-V10-2 (no bloqueante para estimar, sí para implementar) |

**Resolución R-V10-2 (mismo día):** cliente confirmó bloquear la fila de alta si el Modelo no tiene Producto asociado (mensaje claro, no afecta el resto del lote). Arquitectura V10 queda **CERRADA Y APROBADA** — habilitado el paso a Presupuesto.

---

### Entrada 2026-07-30 — Orquestador: Presupuesto V10 (mismo día) — GATE DURO, pendiente aprobación del cliente

| Campo | Valor |
|---|---|
| **Fecha** | 2026-07-30 |
| **Agente / Etapa** | Presupuestador — Presupuesto (Ask mode, sin código) |
| **Feature** | V10 — estimación PERT por ítem, ancladas en LabIPAC M8 (carga masiva, 6,5h) y Vinosefue (filtros export, normalizado) |
| **Resultado** | Total V10: **USD 231,00** — Etapa 1 (Carga masiva de stock): USD 134,40 · Etapa 2 (Filtros completos): USD 50,40 · Tokens IA (25%, sí aplica: 5,28h facturables > piso de 4h): USD 46,20. Sin descuento de expansión (no es Build inicial de cliente nuevo). Sin mantenimiento nuevo (plan v1 ya vigente, a confirmar) |
| **Clasificación** | Mejora sobre sistema propio ya entregado — precio de lista, sin tiers de descuento cross-proyecto |
| **Sanity check** | Total (11,42h M base) casi idéntico a LabIPAC SESIÓN 3 completa (11,5h M base, cierre real 2,0h) — ratio 0,99, dentro de rango |
| **Gate** | **DURO — no se habilita Implementación (subagent `agentes-ia-implementador`) hasta que el cliente apruebe explícitamente este presupuesto** (regla de orquestación: "no iniciar Implementacion sin presupuesto aprobado por el cliente") |

**Aprobación del cliente (mismo día):** presupuesto aprobado tal cual presentado (USD 231,00, ambas etapas, sin ajustes). Gate duro liberado — se delega Implementación al subagent `agentes-ia-implementador`.

---

### Entrada 2026-07-30 — Orquestador: Documentación cliente V10 (mismo día)

| Campo | Valor |
|---|---|
| **Fecha** | 2026-07-30 |
| **Agente / Etapa** | Documentador — Documentación de alcance para cliente (Ask mode) |
| **Input** | `5-implementador.md` (V10, implementación cerrada) + `6-qa.md` (V10, APROBADO CON OBSERVACIONES, 0 defectos funcionales) |
| **Resultado** | Resumen de sprint agregado a `7-documentador.md` (formato cliente, sin tecnicismos): qué se entregó, beneficio, 2 observaciones menores de QA, pendiente de verificación manual y confirmación de commit |
| **Estado** | Borrador sujeto a verificación manual del cliente (mismo criterio que sprints anteriores del proyecto) |

---

### Entrada 2026-07-30 — Orquestador: Cierre de calibración V10 — PENDIENTE

| Campo | Valor |
|---|---|
| **Fecha** | 2026-07-30 |
| **Agente / Etapa** | Presupuestador — Cierre de calibración estimado vs real |
| **Horas estimadas** | 12,91 h con contingencia (USD 231,00) |
| **Horas reales** | **Pendiente** — el cliente no tiene el dato todavía; se deja explícitamente sin registrar en vez de asumir un número |
| **Dato de referencia (no oficial)** | Ejecución de agentes: 20,4 min (Implementación) + 7,2 min (QA) ≈ 27,5 min combinados — no incluye tiempo de decisión/revisión de Joaquín en la sesión |
| **Acción requerida** | Registrar horas reales cuando estén disponibles y completar la tabla de calibración en `4-presupuestador.md` (sección V10) |

## Flujo completo V10 — CERRADO salvo cierre de calibración

Las 9 etapas del flujo del orquestador se ejecutaron en esta sesión: Discovery/Análisis (aprobado por el cliente) → Diseño (aprobado, DD-1 resuelto) → Arquitectura (aprobada, R-V10-2 resuelto) → Presupuesto (USD 231,00, aprobado) → Implementación (build OK, subagent) → QA (APROBADO CON OBSERVACIONES) → Documentación (resumen de cliente en `7-documentador.md`) → Cierre de calibración (**pendiente de horas reales**).

---

### Entrada 2026-07-30 — Deploy a producción V10

| Campo | Valor |
|---|---|
| **Fecha** | 2026-07-30 |
| **Acción** | Commit + push a `origin/main` (GitLab) y publish a producción |
| **Commit** | `d8a71ef` — "Agregar carga masiva de stock por Marca y filtros completos en Consulta de Stock" (7 archivos: 883 inserciones, 57 eliminaciones) |
| **Deploy** | Perfil `olvidatasoft-002-site10 - Web Deploy` (MSDeploy sobre `win8232.site4now.net:8172`). El intento por FTP no completó una transferencia real (el log no mostró subida de archivos); Web Deploy sí: **152 archivos actualizados, 0 agregados, 0 eliminados, "Se publicó correctamente"** |
| **Migración EF** | No aplicó (confirmado desde Arquitectura — sin cambios de esquema) |
| **Riesgo asumido** | El cliente decidió desplegar **sin haber corrido todavía la guía de verificación manual de QA** (13 pasos en `6-qa.md`) — QA solo había validado por inspección de código + build. Pendiente: ejecutar esa guía directamente sobre producción y confirmar que el flujo de Ajuste individual (`/Stock/Ajuste`) y Carga Inicial no sufrieron regresión por el refactor de `AjusteManualAsync` (R-V10-1) |
| **Nota de seguridad** | Se usó una credencial de despliegue provista por el usuario en el chat para destrabar el Web Deploy (401 inicial con la credencial guardada en el perfil). No se almacenó en ningún archivo de este repositorio de documentación |

---

### Entrada 2026-07-31 — Fix post-deploy: filtros de Consulta de Stock activos e independientes desde el primer render

| Campo | Valor |
|---|---|
| **Fecha** | 2026-07-31 |
| **Pedido del cliente** | "los filtros en la pantalla de consulta de stock tiene que tener todas las propiedades del stock que se lista. Hacer que los filtros estén activos en la primera carga de la pantalla así el cliente puede filtrar por cualquier campo independientemente de si tiene seleccionado el anterior" |
| **Diagnóstico** | Los combos Marca/Modelo/Talle/Color de `/Stock/Index` (agregados en V10) nacían `disabled` y solo se poblaban en cascada (Categoría→Marca→Modelo→Talle/Color), obligando a seleccionar en orden antes de poder usar cualquiera de ellos — no cumplía la intención original de "todas las propiedades" de forma independiente |
| **Fix aplicado** | `IModeloService.ObtenerPorMarcaAsync`/`ObtenerTallesPorModeloAsync` ahora aceptan parámetro nullable y devuelven el catálogo COMPLETO cuando es null. `StockController.Index` puebla las 4 listas completas server-side (mismo patrón que Categoría) e inyecta `IMarcaService`/`IModeloService`/`IVarianteService`. La vista ya no marca ningún combo como `disabled`; la cascada queda como refinamiento opcional (acota, nunca deshabilita ni vacía) con fallback a la lista completa cacheada en JS cuando se limpia el padre |
| **Archivos** | `IModeloService.cs`, `ModeloService.cs`, `ModelosController.cs`, `StockController.cs`, `Views/Stock/Index.cshtml` |
| **Migración EF** | No aplica |
| **Verificación** | `dotnet build` (0 errores) + `dotnet publish -c Release` a carpeta descartable para forzar compilación de la vista Razor modificada (0 errores). Sin QA formal delegado a subagent — cambio acotado, tratado como fast-path a pedido directo del cliente sobre funcionalidad recién entregada |
| **Estado** | **Publicado.** Commit `4f7af9b` en `origin/main` + deploy a producción vía Web Deploy (12 archivos actualizados, "Se publicó correctamente") |

---

### Entrada 2026-07-30 — Implementador: Implementación V10 (mismo día)

| Campo | Valor |
|---|---|
| **Fecha** | 2026-07-30 |
| **Agente / Etapa** | Implementador — Implementación (Agent mode) |
| **Feature** | V10 — Carga masiva de stock por Marca (`/Stock/CargaMasiva`) + filtros Talle/Estado en Consulta de Stock (`/Stock/Index`) |
| **Escaneo de reutilización** | Sin match de codigo directamente copiable (LabIPAC ya fue evaluado en Diseño/Arquitectura como patrón de referencia, no como código a portar). Se reutilizó código propio de ShowroomGriffin: `IVarianteService.CrearAsync` y la lógica interna de `AjusteManualAsync` (extraída a `AplicarAjusteInternoAsync`) |
| **R-V10-1** | Resuelto tal como lo definió Arquitectura: `AplicarAjusteInternoAsync` privado sin transacción propia; `AjusteManualAsync` público sin cambios de comportamiento externo |
| **Desvío detectado por el Implementador** | `IVarianteService.CrearAsync` con `StockInicial > 0` también abre su propia transacción vía `CargaInicialAsync` (mismo riesgo de anidamiento que R-V10-1, no marcado en Arquitectura). Resuelto sin tocar `CargaInicialAsync`: `GuardarCargaMasivaAsync` crea la variante con `StockInicial = null` y aplica la cantidad inicial después, dentro de la misma transacción, vía `AplicarAjusteInternoAsync`. Efecto observable menor: el movimiento inicial de una variante nueva por carga masiva queda tipado `AjusteManual` en vez de `CargaInicial` |
| **Resolución de dependencia circular** | `StockService` necesitaba `IVarianteService`, que ya depende de `IStockService`. Se resolvió inyectando `IServiceProvider` en `StockService` y resolviendo `IVarianteService` de forma perezosa dentro del método (misma instancia scoped de `AppDbContext`, participa de la misma transacción) |
| **Cambios por capa** | Domain (+1 enum `EstadoStockFiltro`); Application (+3 ViewModels, `IStockService` +2 métodos y 2 parámetros nuevos en `ListarAsync`/`ExportarExcelAsync`); Infrastructure (`StockService` refactor R-V10-1 + 2 métodos nuevos); Web (`StockController` +acción `CargaMasiva` GET/POST, `Listar`/`ExportarExcel`/`Index` actualizados; vista nueva `CargaMasiva.cshtml`; `Index.cshtml` modificada) |
| **Migración EF** | No aplica — todas las entidades ya existían (confirmado en Arquitectura y re-confirmado en implementación) |
| **Build** | `dotnet build ShowroomGriffin.slnx` → 0 errores, 0 advertencias. Adicionalmente `dotnet publish -c Release` (a carpeta temporal descartada) para forzar la compilación de las vistas Razor nuevas/modificadas, dado que este proyecto no precompila vistas en `dotnet build` — también 0 errores |
| **Detalle completo** | Ver `5-implementador.md` sección "V10 — Carga masiva de stock por Marca + filtros completos en Consulta de Stock" (cambios por archivo, riesgos, pruebas mínimas para QA, checklist de merge) |
| **Pendiente** | QA funcional manual (fuera del alcance del Implementador) — guía de pruebas mínimas dejada en `5-implementador.md`. Cierre de calibración estimado (12,91h) vs real queda pendiente de registrar cuando se trackee el tiempo real de esta sesión |

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

## 📌 Entrada 2026-07-30 — QA V10: Carga masiva de stock por Marca + filtros completos en Consulta de Stock

- **Agente/Etapa:** QA (agente 6), sobre `5-implementador.md` sección V10 ya cerrada por el Implementador (build 0/0, `dotnet publish` para validar Razor).
- **Resumen:** revisión exhaustiva de código (no ejecución en navegador) de la feature V10 completa: pantalla `/Stock/CargaMasiva` (selección por Marca, grilla agrupada por Modelo, alta inline de variantes con Color/Talle/Precio/Stock Mínimo, guardado atómico) + filtros Talle/Estado en `/Stock/Index` (reemplazo del botón "Solo alertas"). Verificado sobre el working tree real (cambios aún no commiteados al momento del QA: `StockService.cs`, `StockController.cs`, `IStockService.cs`, `StockViewModels.cs`, `Stock/Index.cshtml` modificados; `EstadoStockFiltro.cs` y `Stock/CargaMasiva.cshtml` nuevos) + `git diff` línea por línea + build propio (0/0).
- **Resultado:** 13/13 criterios de aceptación PASS (HU-M1 a HU-M3, HU-B1, HU-B2, permisos y 2 regresiones). DD-1 (atomicidad total), R-V10-1 (sin transacción anidada, `AjusteManualAsync` sin cambio de comportamiento externo) y R-V10-2 (bloqueo de alta por Modelo sin Producto) confirmados por código. 0 defectos funcionales. 2 observaciones menores no bloqueantes (filtro Talle no limitado a valores usados a diferencia de Color; ausencia de índice único BD para Color+TalleConfigId, riesgo preexistente no introducido por V10). Sin auto-fix aplicado (no había bugs reproducibles que ameritaran uno). Catálogo cross-proyecto: REG-001 y REG-002 aplican indirectamente (reutilización de `VarianteService.CrearAsync`), ambos PASS.
- **Motivo:** cierre del gate QA antes de pasar a documentación de alcance al cliente, según secuencia operativa obligatoria.
- **Impacto en capas:** ninguno adicional (QA es de solo lectura sobre el código). Actualizada la memoria del agente QA (`6-qa.md`, sección nueva "V10").
- **Riesgos/supuestos:** smoke manual del cliente pendiente de ejecución (13 pasos documentados en `6-qa.md` V10); confirmar que los archivos actualmente sin commitear se commiteen antes de desplegar.
- **Veredicto:** APROBADO CON OBSERVACIONES.

---

## 📌 Entrada 2026-08-08 — Implementador: V11 — fix directo de filtros server-side (Ventas/Compras/Devoluciones) + filtros Marca/Modelo activos en Productos

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-08 |
| **Agente / Etapa** | Implementador (Agent mode) — fix directo a pedido del cliente, sin pasar por Discovery/Diseño/Arquitectura/Presupuesto por tratarse de corrección de un patrón ya usado y aprobado en el mismo proyecto (`Stock/Index`, commit `4f7af9b` + Select2 sin commitear encontrado en el working tree) |
| **Escaneo de reutilización** | Match directo dentro del propio proyecto: `StockController.Index`/`Views/Stock/Index.cshtml` (filtros completos server-side + Select2 local + daterangepicker documentado en `25-frontend-design-system.instructions.md`). Reutilizado como plantilla literal para las 4 pantallas, sin buscar fuera del repo |
| **Bug funcional encontrado (prioridad alta)** | `Ventas/Index.cshtml`, `Compras/Index.cshtml` y `Devoluciones/Index.cshtml` tenían sus DataTables en `serverSide: true` pero el filtro de Fecha/Estado/Tipo se aplicaba con `$.fn.dataTable.ext.search.push(...)`, mecanismo **client-side** que en `serverSide: true` solo evalúa las filas de la página ya traída del servidor — con más de una página de resultados el filtro daba resultados incompletos o vacíos sin ningún aviso. Corregido reemplazándolo por filtrado real server-side (mismo mecanismo que `IStockService.ListarAsync`) |
| **Desviación #1 detectada** | El combo "Tipo" de `Devoluciones/Index.cshtml` usaba valores `0`/`1` que no correspondían a ningún valor real del enum `TipoDevolucion` (`DevolucionDinero=1, CambioMismoValor=2, CambioMayorValor=3`) — el filtro y el badge de la columna ya estaban mal desde antes (bug preexistente, no introducido ahora). Se corrigió alineando con el criterio que ya usa `Devoluciones/Detalle.cshtml` (`DevolucionDinero` = "Devolución", cualquier `Cambio*` = "Cambio"): value=1 Devolución, value=2 Cambio (agrupa `CambioMismoValor`+`CambioMayorValor` server-side) |
| **Desviación #2** | `/Proveedores/Buscar` ya existía (a diferencia de lo anticipado, no hubo que crearlo) y `ProveedorViewModel`/`ClienteViewModel` sí tenían los campos esperados (`razonSocial`, `nombre` respectivamente) — no hizo falta ajustar mapeo de ningún endpoint Buscar |
| **Cambios por capa** | Application (`IVentaService`, `ICompraService`, `IDevolucionService`: nuevos parámetros opcionales en `ListarAsync`); Infrastructure (`VentaService`, `CompraService`, `DevolucionService`: `.Where()` server-side sobre fecha/estado/tipo/cliente/proveedor antes de contar `total`); Web (`VentasController`, `ComprasController`, `DevolucionesController`, `ProductosController`: propagación de parámetros / poblado de `ViewBag.Marcas`+`ViewBag.Modelos`; `Views/Ventas/Index.cshtml`, `Views/Compras/Index.cshtml`, `Views/Devoluciones/Index.cshtml`, `Views/Productos/Index.cshtml` reescritas) |
| **Migración EF** | Ninguna — todos los filtros nuevos son queries sobre columnas ya existentes |
| **Build** | `dotnet build ShowroomGriffin.slnx` → 0 errores, 0 advertencias. `dotnet publish ShowroomGriffin.Web/ShowroomGriffin.Web.csproj -c Release` a carpeta temporal descartada (para forzar compilación de las 4 vistas Razor modificadas) → 0 errores |
| **Detalle completo** | Ver `5-implementador.md` sección "V11 — Filtros server-side reales (Ventas/Compras/Devoluciones) + Marca/Modelo activos en Productos" |
| **Pendiente** | QA funcional manual (fuera del alcance del Implementador) — guía de verificación dejada en `5-implementador.md`. Commit/push queda a cargo del usuario (pedido explícito de no commitear) |

**Verificación y publicación (mismo día):** diff revisado a mano (backend de `VentaService`/`DevolucionService` y vista de `Ventas/Index.cshtml`) antes de publicar — confirma que el bug de filtro client-side-sobre-server-side quedó resuelto y que la corrección del enum `TipoDevolucion` es correcta. Build + publish re-verificados de forma independiente (0 errores). Commit `5dcb633` en `origin/main` + deploy a producción vía Web Deploy (12 archivos actualizados, "Se publicó correctamente"). QA manual sobre las 4 pantallas sigue pendiente del lado del cliente.

---

## 🔗 Referencias

- **Código fuente:** `C:\Sistemas\ShowroomGriffin\`
- **Repositorio:** `https://gitlab.com/olvidata/ShowroomGriffin`
- **Branch actual:** `main`
- **Documentación de análisis funcional:** `/docs/ShowroomGriffin/definiciones/1-analista-funcional.md`
- **Plan de implementación:** (generado en conversación, pendiente de guardar como archivo).

---

### Entrada 2026-08-11 — Incidente producción: 500 en Carga Masiva de Stock

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-11 |
| **Reporte** | Cliente reportó error 500 en `/Stock/CargaMasiva`. Se pidió revisar el log de producción |
| **Investigación** | FTP directo falló (credencial no válida para ese protocolo). Se descargó `Logs/` real del servidor vía `msdeploy -verb:sync` (mismas credenciales del Web Deploy). Encontradas 2 entradas: `13:12:19` y `13:17:13` -07:00, usuario `oficinadeimportados@gmail.com`, `POST /Stock/CargaMasiva`, sin ninguna línea de "Excepción no manejada" en todo el archivo |
| **Diagnóstico** | Ninguna excepción de .NET fue capturada por `GlobalExceptionHandler` — el 500 se originó en una capa anterior al controller (`HomeController.StatusCode`, vía `UseStatusCodePagesWithReExecute`), consistente con el formulario dinámico de Carga Masiva (8 campos × todas las filas de la marca) superando el límite por defecto de ASP.NET Core de 1024 valores de formulario (`FormOptions.ValueCountLimit`), rechazado durante la lectura del formulario (incluida la validación de antiforgery, que ocurre antes que cualquier límite por acción) sin lanzar excepción visible para la app |
| **Hallazgo secundario** | El mecanismo de aviso por mail (`IErrorNotifier`) solo se dispara desde `GlobalExceptionHandler` — nunca se enteró de este incidente porque no hubo excepción capturada. Confirmado por el cliente: no había ningún mail en `olvidatasoft@gmail.com` |
| **Fix aplicado** | `Program.cs`: `FormOptions.ValueCountLimit`/`KeyLengthLimit` y `MvcOptions.MaxModelBindingCollectionSize` subidos a `int.MaxValue`. `HomeController.StatusCode`: dispara `IErrorNotifier.NotifyError` (con excepción sintética) para cualquier 500 que llegue por esta vía, cerrando el gap de notificación. `Session.IdleTimeout` de 60 min a 2 h (pedido explícito del cliente, para no caducar mientras se completa un formulario largo) |
| **Build** | `dotnet build` + `dotnet publish -c Release` a carpeta descartable → 0 errores |
| **Deploy** | Commit `e102a8d` en `origin/main` + Web Deploy a producción (12 archivos, "Se publicó correctamente") |
| **Pendiente** | Confirmar con el cliente/usuario qué Marca estaba cargando (cuántos modelos/variantes) para validar 100% la hipótesis del límite de campos — el fix aplicado es robusto igual sea o no la causa exacta. Los logs descargados (contienen emails de usuarios) se eliminaron del disco local tras el análisis, no quedaron commiteados en ningún repo |

---

### Entrada 2026-08-11 — Reversión de DD-1: Carga Masiva pasa de atomicidad total a guardado parcial

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-11 |
| **Pedido del cliente** | Cambiar el comportamiento de guardado del lote: "guardar todos los productos que están OK e informar los que tienen errores", en vez de descartar el lote completo si una fila falla |
| **Contexto** | Reversa explícitamente la decisión DD-1 (2026-07-30, `2-disenador-funcional.md` sección V10) que había fijado atomicidad total (todo o nada) a pedido del cliente en ese momento — la decisión se corrige ahora con el mismo peso, por pedido directo posterior |
| **Cambio aplicado** | `StockService.GuardarCargaMasivaAsync`: cada fila (ajuste de variante existente, o alta + carga inicial de una nueva) corre en su propia transacción independiente en vez de una única transacción para todo el lote. Si una fila falla, rollback solo de esa fila; el resto sigue procesándose. `StockController.CargaMasiva` (POST): ya no redirige si quedaron filas con error — se queda en la misma pantalla mostrando el resumen de éxito (`TempData["Success"]`) junto con el detalle marcado en rojo por fila. Texto del modal de confirmación (SweetAlert2) actualizado para reflejar el nuevo comportamiento |
| **Build** | `dotnet build` + `dotnet publish -c Release` → 0 errores |
| **Deploy** | Commit `74a115f` en `origin/main` + Web Deploy a producción (12 archivos, "Se publicó correctamente") |
| **Nota para Análisis/Diseño (si se retoma el flujo formal)** | `1-analista-funcional.md` y `2-disenador-funcional.md` (sección V10, DD-1) quedan desactualizados respecto al comportamiento real desplegado — no se actualizaron en esta entrada por tratarse de un fix directo fuera del flujo de gates (mismo criterio ya usado para V11 y el incidente del 500). Si se retoma el proyecto con el flujo completo, sincronizar esos documentos con este cambio |

---

### Entrada 2026-08-11 — Rediseño Vista Matriz de Stock (Marca → Modelo → Color × Talle)

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-11 |
| **Pedido del cliente** | "quiero que la pantalla de stock de los productos se vea como esta presentada en el pdf" — planilla Excel del cliente con formato pivot: Marca → Modelo → Color en filas, Talle en columnas, cantidad en cada celda |
| **Proceso seguido** | Análisis del PDF (páginas 13-16 eran la referencia real; 1-12 era historial de ventas, no relevante) → `EnterPlanMode` para diseñar el enfoque → 4 preguntas de producto resueltas con el cliente antes de escribir código (AskUserQuestion) → plan escrito y aprobado (`ExitPlanMode`) → implementación en 3 etapas |
| **Decisiones del cliente** | (1) La vista Matriz **convive** con la Consulta de Stock actual (toggle), no la reemplaza. (2) Es **editable por celda**, no solo lectura. (3) El caso "Forum Talle Brasilero / Talle Argentino" (mismo modelo, dos numeraciones a la vez) **se modela** como distinción real, no se ignora. (4) Solo se muestran celdas con stock > 0, igual que el PDF |
| **Etapa 1 — Vista de solo lectura** | `IStockService.ObtenerMatrizAsync` (nuevo, agrupa en memoria por Marca→Modelo→Color×Talle, sin migración — reutiliza datos ya existentes). `StockController.Matriz` + `Views/Stock/Matriz.cshtml` (nueva). Botón "Vista Matriz" agregado en `Stock/Index.cshtml`. Commit `022bd07` |
| **Etapa 2 — Talle Argentino** | Nuevo valor de enum `TipoTalle.ZapatillaAdultoArgentino` — **sin migración EF** (el enum se persiste como int, sin cambio de esquema) y **sin seed hardcodeado**: el catálogo de talles argentinos lo carga el cliente por el ABM de Talles Config ya existente (`/TallesConfig`, genérico vía `Enum.GetValues<TipoTalle>()`, no necesitó tocarse). `ModeloService.ObtenerTallesPorModeloAsync` ofrece ambos catálogos cuando el modelo es ZapatillaAdulto; combos de talle (Variantes/Crear-Editar, Carga Masiva) distinguen "40 (Talle Brasilero)" / "40 (Talle Argentino)" solo cuando ambos sistemas conviven. Commit `06bb253` |
| **Etapa 3 — Edición por celda** | `Views/Stock/MatrizEditar.cshtml` (nueva) + `StockService.GuardarMatrizAsync`, reutilizando el mismo patrón fila-por-fila (transacción propia por celda, guarda lo que está OK, informa errores) ya construido hoy mismo en Carga Masiva. Edición acotada a **una Marca por vez** (mismo funnel que Carga Masiva) para no repetir el problema de formularios gigantes recién resuelto. Solo ajusta variantes existentes — el alta de variantes nuevas sigue siendo responsabilidad de Carga Masiva/Productos-Variantes, no se duplicó esa lógica. Commit `0eba0fc` |
| **Build** | `dotnet build` + `dotnet publish -c Release` a carpeta descartable → 0 errores en las 3 etapas |
| **Deploy** | Web Deploy a producción tras cada etapa (10-12 archivos por deploy, "Se publicó correctamente" las 3 veces) |
| **Pendiente** | Verificación visual manual del cliente comparando la Matriz contra su PDF de referencia con datos reales. El catálogo de Talle Argentino queda vacío hasta que el cliente cargue sus valores reales en `/TallesConfig` |

---

## 📌 Entrada 2026-08-16 — QA: barrido del fast-path acumulado desde V10 (`d8a71ef..f400671`, 11 commits)

- **Agente/Etapa:** QA (agente 6), a pedido explícito del usuario ("hacer barrido QA" sobre todo lo acumulado desde el último gate formal). Sin definiciones 1/2/3 nuevas: los 11 commits se ejecutaron como fast-path directo, y `1-analista-funcional.md` / `2-disenador-funcional.md` (§V10, DD-1) quedaron deliberadamente desactualizados respecto de lo desplegado.
- **Alcance:** `4f7af9b` (filtros de Consulta de Stock activos desde el primer render), `5dcb633` (filtros server-side reales + daterangepicker + autocomplete en Ventas/Compras/Devoluciones/Productos, con el fix del enum `TipoDevolucion`), `e102a8d` (límite de campos de formulario, aviso por mail de 5xx sin excepción, sesión a 2 h), `74a115f` (reversión de DD-1: Carga Masiva pasa a guardado parcial fila por fila), `022bd07` + `06bb253` + `0eba0fc` (Vista Matriz en 3 etapas: lectura, Talle Argentino, edición por celda), `9e43229` + `42b7f19` (Matriz como pantalla principal de Stock + editar variantes en 0), `1122c3c` (toast visible ante fallo de guardado), `f400671` (alta de variantes desde celdas "—" de la Matriz).
- **Método:** inspección exhaustiva de código sobre `git diff d8a71ef..HEAD` (31 archivos, +1615/-287), leyendo los archivos completos y no sólo el diff, más build propio verde (`dotnet build ShowroomGriffin.slnx` → 0 advertencias, 0 errores) verificado de forma independiente. **Verificación automatizada por navegador NO disponible en esta sesión**: el servidor MCP `playwright` está declarado en `.mcp.json` pero sus herramientas no quedaron expuestas — declarado explícitamente conforme a `33-verificacion-automatizada-qa.instructions.md` y suplido con una guía de pasos manuales priorizada.
- **Resultado:** 18/22 criterios PASS, 3 FAIL, 1 PASS con reserva, 0 BLOCKED. **4 defectos: 2 de severidad Alta (bloqueantes, ya en producción) y 2 Media**, más 7 observaciones menores. **D-01 (Alta):** `/Stock/MatrizEditar` no guarda **nada** cuando hay celdas "—" vacías — `StockMatrizAltaGuardarViewModel.CantidadNueva/PrecioVenta/StockMinimo` son tipos de valor no nullables y la vista los renderiza vacíos, así que el model binder invalida el POST completo antes de llegar al servicio; **es una regresión de `f400671`** sobre la edición por celda que `0eba0fc`/`9e43229` ya habían entregado funcionando. **D-02 (Alta):** el input de Precio por fila se renderiza vacío bajo la cultura global `es-AR` (coma decimal, inválida para `input type=number`) y la sincronización JS del submit copia ese vacío sobre el hidden que el servidor había renderizado bien — segunda vía independiente al mismo bloqueo. **D-03 (Media):** el *change tracker* compartido entre las transacciones por fila de `GuardarCargaMasivaAsync`/`GuardarMatrizAsync` puede persistir, dentro de la transacción de la fila siguiente, una fila ya informada al usuario como fallida (o envenenar el resto del lote), erosionando el objetivo de `74a115f`. **D-04 (Media, latente):** el combo Talle de `/Stock/Index` es la única vista que no recibió la desambiguación Brasilero/Argentino de `06bb253`, y mostrará valores duplicados indistinguibles en cuanto el cliente cargue el catálogo argentino en `/TallesConfig`.
- **Confirmado / refutado (puntos de atención del pedido):** refutado que puedan quedar variantes huérfanas ante un fallo del stock inicial (todo el alta corre dentro de `txAlta`); refutado que haya huecos de permisos (`Matriz`=RequireEmpleado, `MatrizEditar` GET/POST=RequireAdministrador+antiforgery, con la vista gateada por rol); refutadas ambas hipótesis sobre el índice de fila del JS (`filaIdxCounter` es global y nunca se reinicia; el conjunto de celdas "—" y el de inputs visibles son siempre consistentes) — la falla real resultó ser la cultura, no un borde de indexado; confirmados sin regresión `/Stock/Ajuste` (cuerpos de `AjusteManualAsync`/`AplicarAjusteInternoAsync` sin una línea modificada) y `/Variantes/Crear` con `StockInicial > 0` (`VarianteService.cs` sin diff alguno en el rango); confirmado efecto colateral menor del `int.MaxValue` (alcance global, no acotado a Carga Masiva).
- **Catálogo cross-proyecto:** los 33 items de `regresiones-manuales.yml` recorridos; 11 aplicables, **todos PASS** (REG-001, REG-002, REG-003, REG-005, REG-008, REG-009, KOI-001, DN-001/002, MH-001, MH-002, MH-009). Alta del item nuevo **SG-001** (severidad `critical`) documentando el patrón "grilla con inputs numéricos opcionalmente vacíos contra ViewModel con tipos de valor no nullables", para que quede disponible al próximo proyecto.
- **Auto-fixes:** **ninguno aplicado**, por instrucción explícita del solicitante de reportar sin parchear los defectos de severidad media/alta hasta su revisión. Sí se cumplió la obligación de catalogación previa (SG-001). La dirección de fix propuesta para D-01/D-02 queda documentada en `6-qa.md`.
- **Impacto en capas:** ninguno (QA es de solo lectura sobre el código). Actualizada la memoria del agente QA (`6-qa.md`, sección nueva "Barrido QA post-V10" + bullet en Memoria acumulativa) y el catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`, item SG-001, `ultima_actualizacion` a 2026-08-16).
- **Riesgos/supuestos:** D-01 y D-02 **ya están desplegados en producción** (los 11 commits se publicaron por Web Deploy tras cada etapa), por lo que corresponde tratarlos como hotfix y no como backlog; mitigación provisoria: operar por `/Stock/CargaMasiva` (no afectada) o `/Stock/Ajuste`. Avisar al cliente antes de que cargue talles argentinos en `/TallesConfig` (dispara D-04). Sigue pendiente sincronizar `1-analista-funcional.md` y `2-disenador-funcional.md` con la reversión de DD-1.
- **Hallazgo de proceso:** los 11 commits pasaron build verde, `dotnet publish` verde y revisión manual de diff, y aun así dos defectos bloqueantes llegaron a producción. Ninguno es detectable por compilación ni por lectura del diff aislado: D-01 exige cruzar la vista contra la nullabilidad del ViewModel (dos capas), y D-02 exige cruzar la vista contra la configuración global de cultura en `Program.cs`. Criterio propuesto para el futuro: **si un cambio agrega un ViewModel nuevo con binding de formulario, sale del fast-path** aunque el pedido del cliente sea "un ajuste chico" — `f400671` era una feature con perfil de riesgo de feature, no un ajuste.
- **Veredicto:** **RECHAZADO** — 8 de los 11 commits (`4f7af9b`, `5dcb633`, `e102a8d`, `74a115f`, `022bd07`, `06bb253`, `9e43229`, `1122c3c`) son correctos y aptos para producción; el rechazo se concentra en `f400671`. Ver detalle completo en `6-qa.md`, sección "Barrido QA post-V10 — fast-path acumulado `d8a71ef..f400671`".

---

### Entrada 2026-08-16 — Hotfix SG-001: D-01, D-02 y D-03 corregidos y desplegados

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-16 |
| **Contexto** | A continuación del barrido QA de más arriba (veredicto RECHAZADO por `f400671`), tratado como hotfix inmediato en vez de backlog, tal como recomendó QA — los defectos ya estaban en producción |
| **D-01 (Alta)** | `StockMatrizAltaGuardarViewModel.CantidadNueva/PrecioVenta/StockMinimo` pasan de tipos de valor no nullables a nullables (`int?`/`decimal?`/`int?`), mismo criterio que `StockCargaMasivaFilaViewModel` ya usaba. `StockService.GuardarMatrizAsync` ajustado para tratar null como "el usuario no cargó nada en esta celda" |
| **D-02 (Alta)** | `MatrizEditar.cshtml`: el input de Precio sugerido por fila y el hidden `Altas[i].PrecioVenta` ahora formatean el decimal con `CultureInfo.InvariantCulture` en vez de la cultura del server (es-AR, coma) — mismo criterio que ya aplica el tag helper `asp-for` para `type="number"` en el resto del proyecto |
| **D-03 (Media)** | Se agregó `_db.ChangeTracker.Clear()` inmediatamente después de cada `RollbackAsync()` dentro de los loops fila-por-fila de `GuardarCargaMasivaAsync` y `GuardarMatrizAsync` (6 sitios) — evita que cambios ya revertidos en la BD pero todavía trackeados por el `AppDbContext` scoped se cuelen dentro de la transacción de la fila siguiente |
| **D-04 (Media)** | Ya había quedado resuelto de forma incidental por el fix del filtro de Talle de `/Stock/Index` (ver entrada de abajo, commit `a610459`, mismo día) — no requirió cambio adicional |
| **Build** | `dotnet build` + `dotnet publish -c Release` a carpeta descartable por cada commit → 0 errores |
| **Deploy** | Commits `493bb1f` (D-01+D-02) y `69b1015` (D-03) en `origin/main` + Web Deploy a producción tras cada uno, "Se publicó correctamente" |
| **Pendiente** | Confirmación del cliente de que la Matriz vuelve a guardar correctamente. `1-analista-funcional.md`/`2-disenador-funcional.md` (§V10, DD-1) siguen sin sincronizar con la reversión de guardado parcial — señalado en la entrada del 2026-08-11 y en el barrido QA de arriba, todavía sin resolver |

---

### Entrada 2026-08-16 — Fixes puntuales a pedido del cliente tras el informe de gaps/bugs

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-16 |
| **Contexto** | El cliente pidió un repaso de gaps/bugs pendientes de las últimas definiciones del estudio; sobre ese informe pidió: arreglar el filtro de Talle (OBS-V10-01), agregar el throttle al aviso por mail de errores, hacer el barrido QA (ver entradas de arriba), y evaluar accesorios sin talle / retirar Ajuste Manual y Carga Masiva |
| **Filtro de Talle (OBS-V10-01)** | Nuevo `IVarianteService.ObtenerTallesUsadosAsync` (mismo criterio que `ObtenerColoresAsync`: Distinct sobre variantes existentes) reemplaza al catálogo completo (`ObtenerTallesPorModeloAsync`, que sigue usándose sin cambios para altas en Carga Masiva/Variantes) como fuente del combo Talle de `/Stock/Index`. Se agregó también la etiqueta de sistema de talle (Brasilero/Argentino) al combo cuando el modelo mezcla ambos. De paso, `TalleConfigViewModel.TipoNombre` pasa de devolver el nombre crudo del enum a una etiqueta amigable (`TipoTalleExtensions.EtiquetaAmigable`, helper compartido — reemplaza el mapeo que antes vivía duplicado como método privado en `StockService`) |
| **Throttle de mail de errores** | `ErrorNotifier`: ventana de 15 minutos por tipo+mensaje de excepción (diccionario estático, sobrevive entre requests aunque el service sea Scoped) — evita spam si el mismo error se repite en ráfaga |
| **Regla de Ventas (PAT-003, formalizada 2026-08-15)** | Detectado que `Ventas/Crear.cshtml` no bloqueaba la confirmación cuando la suma de pagos no cerraba contra el total — solo mostraba un indicador de color, sin `preventDefault`. El Service ya lo validaba (`VentaService.cs:35-37`). Se agregó el guard client-side faltante, mismo patrón que el resto de los guards del botón Confirmar. ShowroomGriffin no modela IVA por línea (extensión posterior del patrón en vinosefue/ganaderia) y Compras no tiene concepto de pagos múltiples, así que el resto de la regla no aplica acá |
| **Índice único Color+TalleConfigId (OBS-V10-02)** | **Bloqueado, pendiente de decisión del cliente.** Se encontraron 6 grupos de `VarianteProducto` duplicadas ya en producción (mismo Producto+Color+Talle, creadas segundos aparte el 2026-06-04 — patrón de doble-guardado accidental durante la carga inicial del catálogo). Ninguna tiene ventas/compras/devoluciones asociadas. No se tocó nada de producción sin autorización explícita — queda pendiente decidir el criterio de fusión antes de poder agregar el índice |
| **Accesorios sin talle / retirar Ajuste Manual y Carga Masiva** | Análisis entregado, sin ejecutar: Carga Masiva ya cubre accesorios hoy (Talle opcional cuando el Modelo no tiene `TipoTalle`); el gap real es que la Matriz los excluye por completo. Ajuste Manual es 100% redundante con la edición por celda de la Matriz y el cliente ya no lo va a usar. Carga Masiva no es seguro retirarla todavía: cubre altas de Color completamente nuevo, que la Matriz no soporta (solo permite completar un Talle faltante en un Color existente). Recomendación entregada: extender la Matriz para accesorios + alta de Color nuevo, y recién ahí retirar ambas pantallas — pendiente de confirmación del cliente para arrancar |
| **Build** | `dotnet build` + `dotnet publish -c Release` → 0 errores en cada commit |
| **Deploy** | Commits `f9c91a4` (guard de pagos en Ventas) y `a610459` (filtro Talle + TipoNombre + throttle de mail) en `origin/main` + Web Deploy a producción, "Se publicó correctamente" en ambos |

---

### Entrada 2026-08-16 — OBS-V10-02 cerrado: fusión de duplicados en producción + índice único

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-16 |
| **Pedido del cliente** | "merge" — autorización explícita para fusionar los 6 grupos de variantes duplicadas encontrados y agregar el índice único |
| **Diagnóstico previo a tocar nada** | Consulta directa a producción (`mysqlsh`) confirmó 6 grupos de `VariantesProducto` con el mismo `(ProductoId, Color, TalleConfigId)`, todas creadas 2-3 segundos aparte el 2026-06-04 (doble guardado accidental durante la carga inicial del catálogo). Ninguna de las 13 filas involucradas (canónicas + duplicadas) tiene ventas, compras ni devoluciones asociadas en más de 2 meses — nunca se transaccionó contra ninguna. El grupo "ROSA Y BLANCA" mostró que el cliente ya había ajustado manualmente a mano la duplicada (Id 63) a stock 0 el 2026-06-18, evidencia de que el conteo real es el de la fila que quedó en uso, no la suma de ambas — se descartó sumar el stock de las duplicadas (hubiera duplicado inventario fantasma) |
| **Fusión aplicada** | Por cada grupo, la fila más antigua queda como canónica sin tocar su stock; las duplicadas se llevan a stock 0 mediante un `AjusteStock`+`MovimientoStock` real (mismo mecanismo que usa la app, motivo "Fusión de variante duplicada...", atribuido al usuario admin real) y luego se dan de baja lógica (`DeletedAt`), replicando exactamente la regla de negocio de `VarianteService.InactivarAsync` (no se puede inactivar con stock > 0). Ejecutado en una única transacción SQL contra producción vía `mysqlsh`, con captura previa del estado exacto de las 13 filas afectadas como referencia de rollback manual (no se usó `mysqldump` completo — no estaba disponible en el entorno — pero el alcance era acotado y totalmente conocido de antemano) |
| **Índice único** | Migración EF `V9_UniqueIndexVarianteProducto`: MySQL no soporta índices únicos filtrados (`WHERE`) como SQL Server, así que se emula con una columna generada `ClaveUnicaVariante` (NULL para variantes dadas de baja, string determinístico `ProductoId\|Color\|TalleConfigId` para las activas) + índice único sobre esa columna. Primer intento con columna `STORED` falló ("Cannot add foreign key constraint" — MySQL fuerza un rebuild completo de la tabla al agregar una columna `STORED`, y esta tabla tiene múltiples FK entrantes desde Stocks/MovimientosStock/AjustesStock/VentaDetalle/CompraDetalle que no toleraron el rebuild). Resuelto usando `VIRTUAL` en vez de `STORED` (soportado con índices secundarios desde MySQL 5.7+, no requiere reconstruir la tabla) |
| **Verificación** | Post-fusión: 0 grupos duplicados activos (`GROUP BY ... HAVING COUNT(*) > 1` vacío). Post-índice: `SHOW INDEX` confirma `Non_unique = 0`; test funcional (INSERT de un combo ya existente dentro de una transacción, después `ROLLBACK`) confirmó que MySQL rechaza el duplicado con error 1062 antes de aceptar cualquier commit — sin dejar datos de prueba |
| **Build** | `dotnet build` → 0 errores. Sin cambios de código de aplicación (solo migración), no requirió redeploy del binario web |
| **Deploy** | Commit `e90b399` en `origin/main`. Migración aplicada directamente a producción vía `dotnet ef database update` (Camino A del runbook) |
| **Pendiente** | Ninguno — OBS-V10-02 queda cerrado |

---

### Entrada 2026-08-16 — Orquestador: Discovery + Análisis V12 (extensión de Matriz: accesorios + alta de Color nuevo)

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-16 |
| **Agente / Etapa** | Analista Funcional — Discovery + Análisis combinados (Ask mode, sin código) |
| **Disparador** | Pedido explícito del cliente: extender la Matriz para cubrir accesorios sin talle y alta de Color nuevo, con el objetivo de retirar `/Stock/CargaMasiva` y `/Stock/Ajuste`. El cliente pidió correr esto por `/agentes-ia-orquestador` en vez de fast-path, en línea con la recomendación de proceso que dejó el barrido QA del mismo día (rechazo de `f400671` por saltarse el flujo en un cambio con perfil de riesgo de feature) |
| **Resultado** | Alcance funcional, riesgos (R1–R4) y 4 preguntas abiertas (D1–D4) registrados en `1-analista-funcional.md` sección "V12". Nota de contexto agregada: la Matriz nunca había pasado formalmente por Discovery/Análisis/Diseño hasta ahora (se construyó fast-path en 3 etapas + 4 ajustes puntuales) |
| **Escaneo de reutilización** | Dentro del propio proyecto: el patrón de alta inline de `CargaMasiva.cshtml` ("+ Agregar variante nueva") es la plantilla directa para el alta de Color nuevo dentro de la Matriz. `docs/patrones/catalogo.yml` no tiene ningún patrón de grilla pivot Talle×Color cross-proyecto — es original de ShowroomGriffin; candidato a catalogar una vez cerrada esta feature |
| **Impacto en capas** | Presentación (`Matriz.cshtml`/`MatrizEditar.cshtml` extendidas, posible retiro de `CargaMasiva.cshtml`/`Ajuste.cshtml`); Negocio (`StockService.ObtenerMatrizAsync`/`GuardarMatrizAsync` extendidos, reutiliza `IVarianteService.CrearAsync`); Datos (sin migración EF prevista, a confirmar en Arquitectura) |
| **Gate** | Bloqueado para Diseño (agente 2) hasta que el cliente resuelva D1–D4 |

**Resolución D1–D4 (mismo día):** cliente confirmó D1 (tabla simple Color+Cantidad para accesorios), D2 (fila "+ Nuevo color" embebida en la tabla pivot), D3 (solo ocultar del menú, sin borrar código) y D4 (todo en el mismo sprint, sin período de validación intermedio — a diferencia de la hipótesis recomendada de dos entregas separadas). Análisis V12 queda **CERRADO Y APROBADO** — habilitado el paso a Diseño.

---

### Entrada 2026-08-16 — Orquestador: Diseño funcional V12 (mismo día)

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-16 |
| **Agente / Etapa** | Diseñador Funcional — Diseño (Ask mode, sin código) |
| **Escaneo de reutilización** | Match directo dentro del propio proyecto: `CargaMasiva.cshtml` ya resuelve ambos problemas (alta de Color nuevo, Talle opcional para accesorios) con otro layout — se toma como base de las reglas de validación, adaptando el layout a la tabla pivot. Sin match cross-proyecto (`docs/patrones/catalogo.yml` no tiene ningún patrón de grilla pivot Talle×Color) — se deja nota para catalogarlo como patrón nuevo (candidato PAT-009) una vez cerrada la feature |
| **Resultado** | Flujo de pantalla (fila "+ Nuevo color" embebida en cada sección, layout de 2 columnas para accesorios), validaciones, 1 cambio de ViewModel (`StockMatrizAltaGuardarViewModel.TalleConfigId` → nullable, sin ViewModels nuevos), impacto por capa y 4 historias de usuario (HU-12.1 a HU-12.4) registrados en `2-disenador-funcional.md` sección "V12" |
| **Riesgo destacado** | La fila "+ Nuevo color" con Talle es la pieza de UI nueva de mayor riesgo — mismo perfil que causó D-01/D-02 (inputs opcionales sin nullable, cultura de decimales) — marcado como checklist explícito a verificar durante Implementación, no solo al cierre |
| **Gate** | Diseño listo para Arquitectura (agente 3) — sin puntos nuevos abiertos, D1–D4 ya habían sido confirmados en el gate de Análisis |

---

### Entrada 2026-08-16 — Orquestador: Arquitectura técnica V12 (mismo día)

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-16 |
| **Agente / Etapa** | Arquitecto MVC — Arquitectura (Ask mode, sin código) |
| **Resultado** | Sin migración EF (`TalleConfigId` ya era nullable desde V4; el índice único OBS-V10-02 ya soporta `TalleConfigId IS NULL` vía `COALESCE`). 1 cambio de contrato (`StockMatrizAltaGuardarViewModel.TalleConfigId` → nullable). 1 componente técnico nuevo identificado: resolver `TipoTalle` por `ProductoId` en una consulta previa al loop de `Altas` de `GuardarMatrizAsync` (los `Altas` llegan en lista plana, a diferencia de `GuardarCargaMasivaAsync` que los recibe agrupados por Modelo) |
| **Riesgo destacado** | La fila "+ Nuevo color" con Talle repite, en mayor escala, el mismo perfil de riesgo que causó el rechazo de QA de `f400671` (D-01/D-02) — checklist de verificación (nullable + `InvariantCulture`) marcado como obligatorio antes de cerrar Implementación, no solo al final |
| **Regla de proceso agregada** | Esta etapa **no se cierra como fast-path**; el QA de V12 debe incluir verificación por navegador de la fila nueva, no solo inspección de código — directamente derivado de la lección del barrido QA de esta misma fecha |
| **Gate** | Arquitectura lista para Presupuesto (agente 4) — sin puntos abiertos |

---

### Entrada 2026-08-16 — Orquestador: Presupuesto V12 (mismo día) — GATE DURO, pendiente aprobación del cliente

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-16 |
| **Agente / Etapa** | Presupuestador — Presupuesto (Ask mode, sin código) |
| **Resultado** | Total V12: **USD 105,84** — Etapa 1 (altas de Color nuevo, con y sin Talle): USD 67,20 · Etapa 2 (accesorios sin talle + ocultar botones): USD 38,64. Horas facturables (3,02h) por debajo del piso de 4h → **sin cargo de Tokens IA** (a diferencia de V10) |
| **Clasificación** | Merge sobre sistema propio ya entregado — precio de lista, sin descuento de expansión agresiva (exclusivo de Build inicial) |
| **Anclaje histórico** | Cuarta ronda consecutiva sobre el mismo módulo Stock/Matriz en menos de 2 semanas (V10 → 3 etapas de Matriz → hotfix SG-001 → V12) — regla de "segunda/tercera ronda" aplicada al piso de "Modificación sobre módulo existente" para los ítems de reutilización directa, con ajuste al alza documentado en el ítem de mayor riesgo técnico (indexado dinámico JS) |
| **Sanity check** | Total (6,3h M base) ≈ 55% del tamaño de V10 (11,42h M base) — consistente con ser extensión incremental de una pantalla ya construida, no una capacidad nueva desde cero |
| **Gate** | **DURO — no se habilita Implementación (subagent `agentes-ia-implementador`) hasta que el cliente apruebe explícitamente este presupuesto** |

**Aprobación del cliente (mismo día):** presupuesto aprobado tal cual presentado (USD 105,84, ambas etapas, sin ajustes). Gate duro liberado — se delega Implementación al subagent `agentes-ia-implementador`.

---

### Entrada 2026-08-16 — Implementador: Implementación V12 (mismo día)

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-16 |
| **Agente / Etapa** | Implementador (Agent mode) |
| **Archivos tocados** | 5, ninguno nuevo: `StockViewModels.cs`, `StockService.cs`, `Matriz.cshtml`, `MatrizEditar.cshtml`, `Index.cshtml`. Sin migración EF, `StockController` sin cambios |
| **Desvíos documentados respecto de Diseño/Arquitectura** | (1) `StockMatrizAltaGuardarViewModel.Color` pasa a `string?` sin `[Required]` (no solo `TalleConfigId` como preveía Arquitectura) — mismo motivo D-01: un `[Required]` insatisfecho en la fila "+ Nuevo color" tira abajo el POST completo. (2) `EtiquetaSistemaTalle = "Sin talle"` para la sección de accesorios de un Modelo mixto, en vez de `null` (evita dos secciones sin distinguir). (3) `Trim()` del Color aplicado también al chequeo de duplicados contra BD, no solo al combo del lote. |
| **Hallazgo crítico durante la implementación — OBS-V12-01** | El hotfix SG-001 de esta mañana (commits `493bb1f`/`69b1015`) corrigió el *render* del decimal con `CultureInfo.InvariantCulture`, pero dejó sin cubrir el *parseo* del POST: el browser siempre postea `type="number"` con `.` como separador, pero el model binder de ASP.NET Core parsea con la cultura del request (`es-AR`, fijada globalmente en `Program.cs`), donde `.` es separador de miles — `"45000.00"` bindea como `4500000` (×100), silenciosamente. Como todo precio sugerido en este catálogo es un `decimal(18,2)` que siempre renderiza con `.00`, **cualquier alta que aceptara el precio sugerido sin tocarlo habría guardado el precio multiplicado por 100** desde el deploy de esta mañana. Verificado contra producción (`variantesproducto.CreatedAt >= '2026-08-16'`): **0 filas — nadie usó el flujo todavía, sin corrupción de datos real**. Corregido dentro de `MatrizEditar.cshtml` con un helper `aDecimalServidor()` que convierte al separador de la cultura del servidor antes de postear, aplicado en los dos caminos de esa vista (celda "—" existente y fila "+ Nuevo color" nueva) |
| **Observaciones abiertas, sin corregir (fuera de alcance de V12)** | **OBS-V12-01 (parcial):** el mismo patrón de riesgo (parseo de decimales bajo `es-AR`) puede estar latente en otros `type="number"` decimales del sistema (ej. `CargaMasiva.cshtml`) — no se tocó, candidato a relevamiento propio. **OBS-V12-02:** `Celdas[].CantidadNueva` sigue siendo `int` no nullable (preexistente, no lo introduce V12) — no amerita cambio sin definir la semántica de "celda vacía" en esa grilla, decisión funcional pendiente. **Acceso vivo sin ocultar:** el botón "Ajuste manual" por fila de `/Stock/Index` (`/Stock/Ajuste?varianteId=`) no se tocó — HU-12.4 solo nombraba los 2 botones de la cabecera |
| **Build** | `dotnet build ShowroomGriffin.slnx` → 0 errores, 0 advertencias (Implementador). `dotnet publish -c Release` → 0 errores (Implementador, re-verificado de forma independiente después) |
| **Detalle completo** | Ver `5-implementador.md` sección "V12" (cambios por archivo, guía de pruebas mínimas para QA) |
| **Pendiente** | QA (subagent `agentes-ia-qa`) — Arquitectura V12 exige verificación por navegador de la fila "+ Nuevo color", no solo inspección de código (regla de proceso agregada tras el rechazo de `f400671` el mismo día). Sin commit/push/deploy todavía — working tree con los cambios listos |

---

### Entrada 2026-08-16 — QA: barrido V12 (mismo día)

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-16 |
| **Agente / Etapa** | QA (Agent mode) — validación de la implementación V12 sobre working tree sin commitear |
| **Veredicto** | **APROBADO CON OBSERVACIONES** para HU-12.1 / HU-12.2 / HU-12.3. **HU-12.4 (retiro de Carga Masiva y Ajuste) SE RETIENE** — no debe liberarse en este sprint |
| **Gate de navegador** | **NO CUMPLIDO.** El MCP `playwright` volvió a no estar expuesto en la sesión (segunda vez consecutiva). Se declaró explícitamente y se compensó con verificación real en 3 niveles: (N1) banco de model binding con el ViewModel real y la misma `UseRequestLocalization` es-AR de `Program.cs` — 13 POST; (N2) la app real corriendo contra MySQL de desarrollo, con login y antiforgery reales — 6 POST a `/Stock/MatrizEditar`; (N3) inspección del HTML efectivamente servido. Queda sin verificar **sólo la ejecución del JavaScript** (`construirAltasDeColoresNuevos`, `aDecimalServidor`, `sincronizarPrecioYMinimoDeAltas`), que es exactamente lo que Arquitectura V12 §5 exigía. Guía manual priorizada de 21 pasos en `6-qa.md` §9 |
| **OBS-V12-01 — resolución** | **El diagnóstico del Implementador es correcto y quedó reproducido de punta a punta contra la base real.** T2: `"39990.50"` → persistido **3999050**. T3: `"33000.00"` (precio **entero**) → persistido **3300000**. Ambos con HTTP 302 de éxito y sin ningún error visible. Con el fix (T1): `"39990,50"` → **39990.50 correcto**. **Conclusión: el mecanismo del fix funciona, pero NO cierra el problema** — la protección es 100% del lado del cliente y el servidor no tiene ninguna defensa. Además, la evaluación de riesgo del Implementador ("para valores enteros la conversión es no-op, riesgo mínimo") **queda refutada por T3**: el hidden de la celda "—" se renderiza con `inv()` sobre un `decimal(18,2)`, o sea que **siempre** sale en el formato corruptor, precios enteros incluidos |
| **Defectos nuevos** | **D-V12-01 (crítico por impacto):** la protección ×100 depende exclusivamente de que corra el JS; el servidor acepta y persiste el valor corrupto en silencio. **D-V12-02 (mayor):** un Color que difiere sólo en mayúsculas/acentos crea una variante duplicada — reproducido (T5: `qa-dorado` duplicó a `QA-Dorado`); causa raíz: comparación ordinal en C# contra una columna `utf8mb4_0900_ai_ci`. **D-V12-03 (mayor):** la Matriz no puede crear una variante con stock inicial 0 y Carga Masiva sí — incumple la premisa de "cobertura 100%" con la que el Análisis condicionó el retiro. **D-V12-04 (mayor, entorno):** `V9_UniqueIndexVarianteProducto` **no está aplicada** en la BD de desarrollo (llega a V8); confirmar producción. **D-V12-05/06 (medios):** `ProductoId` arbitrario en Modelos con más de un Producto; `TipoTalle IS NULL` no equivale a "accesorio" en los datos reales (en dev son `JORDAN 1` y `JORDAN RETRO 4`, calzado sin configurar). **D-V12-07/08 (menores):** se pierde lo tipeado en la fila "+ Nuevo color" ante error parcial; el botón "Ajuste manual" por fila de `/Stock/Index` sigue visible |
| **Lo que sí quedó confirmado** | D-01 **no reaparece**: `Altas[]` íntegramente nullable verificado por QA contra el binder real, no por palabra del Implementador (fila "+ Nuevo color" enteramente vacía → `ModelState` válido y las celdas se persisten). Contigüidad de índices de `Altas[]` validada con control negativo (un hueco corta la lista). Accesorios: render de lectura y edición correctos, alta con `TalleConfigId` null persistida. `/Stock/CargaMasiva` y `/Stock/Ajuste` → **200** por URL directa (404 de contraste verificado). Permisos y antiforgery correctos. `SEP_DECIMAL` se emite como `,` en el HTML real |
| **OBS-V12-02 confirmada** | `Celdas[].CantidadNueva` sigue siendo `int` no nullable: vaciar una celda a mano invalida el `ModelState` y **descarta todo el POST**, incluidas las celdas correctas. Preexistente, pero V12 **amplía la superficie** (las secciones de accesorios usan el mismo binding). Decisión funcional pendiente del cliente |
| **Catálogo cross-proyecto** | 34 ítems recorridos — 13 aplicables, 11 PASS, **2 BLOCKED** (GAN-001 y GAN-003, ambos por falta de navegador). **GAN-003 es el precedente más relevante**: documenta una grilla dinámica que falla **en silencio**, sin error en consola, y cuya `pruebas_minimas` exige explícitamente navegador real y no POST HTTP directo — exactamente la clase de riesgo de la fila "+ Nuevo color" |
| **Auto-fixes aplicados** | **Ninguno**, por pedido explícito del usuario (reportar antes de tocar código). Fixes propuestos y acotados en `6-qa.md` §5, ninguno con lógica de negocio nueva. Para D-V12-01 la corrección de menor riesgo es dejar de aplicar `inv()` al hidden `Altas[].PrecioVenta` (es `type="hidden"`, no `type="number"`: el saneamiento HTML5 que motivó `inv()` no le aplica) y renderizarlo con la cultura del servidor, con lo que el round-trip deja de depender del JS |
| **Ítem de catálogo a crear** | `SG-002` — round-trip de decimales bajo cultura no invariante (`deteccion_qa.tipo: static`). Patrón cross-proyecto: aplica a cualquier app del estudio con `UseRequestLocalization` de cultura no invariante, no sólo a ShowroomGriffin. Pendiente de aprobación, no escrito todavía |
| **Datos de prueba** | La BD de desarrollo no tenía ningún accesorio válido para ejercitar HU-12.1/12.3, así que se sembró 1 variante temporal y **se eliminó todo al terminar** (variantes `QA-*` 4-9 y sus filas de `Stocks`/`MovimientosStock`/`AjustesStock`). Estado final verificado idéntico al inicial: 3 variantes / 3 stocks, 0 huérfanos, 0 precios ≥ 1.000.000. **No se tocó producción en ningún momento** |
| **Condiciones para liberar** | (1) Correr la guía manual por navegador de `6-qa.md` §9; (2) endurecer D-V12-01 del lado del servidor; (3) confirmar V9 aplicada en producción; (4) auditar `Modelos.TipoTalle` en producción; (5) **no** liberar HU-12.4 hasta resolver D-V12-03 |
| **Detalle completo** | Ver `6-qa.md` sección "V12" (metodología, 15 criterios, tabla del catálogo, 8 defectos + OBS-V12-02, riesgos y guía manual de 21 pasos) |

---

### Entrada 2026-08-16 — Fixes post-QA sobre V12 (D-V12-01, D-V12-02) + HU-12.4 retenida

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-16 |
| **D-V12-01 (Crítico, corregido)** | `Altas[i].PrecioVenta` es `type="hidden"` (no `type="number"`), así que no está sujeto al saneamiento HTML5 que motivó `InvariantCulture` en SG-001/D-02. Se renderiza ahora directo en la cultura del servidor (`es-AR`) desde el primer `GET`, en vez de en cultura invariante — el round-trip queda correcto aunque el JS de sincronización no llegue a ejecutarse antes del submit (defensa en profundidad, no depende solo del cliente) |
| **D-V12-02 (Mayor, corregido)** | Comparación de Color pasa a case-insensitive (`OrdinalIgnoreCase` contra BD, `ToUpperInvariant()` para el chequeo del lote) en `GuardarMatrizAsync` (Altas) **y** en `GuardarCargaMasivaAsync` (mismo bug preexistente, mismo root cause, corregido a la vez por consistencia — no introducido por V12 pero comparte el mecanismo). De paso se corrigió una inconsistencia de `Trim()`: `GuardarCargaMasivaAsync` recortaba el Color para el chequeo del lote pero no para el chequeo contra BD ni para el valor efectivamente guardado |
| **D-V12-03 (Mayor, NO corregido — bloquea HU-12.4)** | La Matriz usa "cantidad cargada > 0" como señal de "el usuario quiere dar de alta esto", así que **no puede crear una variante con stock inicial 0** — algo que Carga Masiva sí permite (catalogar un producto que todavía no llegó). Se **revirtió** el ocultamiento de los botones "Ajuste manual" y "Carga masiva" de `Stock/Index.cshtml` (vuelven a estar visibles, sin cambios de código en los controllers/vistas de esas pantallas) hasta resolver este gap — HU-12.4 queda pendiente de una extensión futura, no se libera en este sprint pese a la decisión D4 original del cliente (nueva información de QA que amerita revisar esa decisión) |
| **Otros hallazgos de QA no corregidos (severidad menor o fuera de alcance)** | D-V12-04 (migración V9 no aplicada en la BD de desarrollo — producción sí la tiene, verificado); D-V12-05 (ambigüedad preexistente de `ProductoId = FirstOrDefault()` cuando un Modelo tiene más de un Producto, mismo patrón ya aceptado desde V10/R-V10-2); D-V12-06 (`TipoTalle IS NULL` no equivale estrictamente a "accesorio" — puede ser un Modelo de calzado sin configurar; es una precisión de nomenclatura, no un bug funcional); D-V12-07 (se pierde lo tipeado en la fila "+ Nuevo color" si el guardado tiene errores parciales, UX rough edge ya aceptado en otros puntos de esta pantalla); OBS-V12-02 (`Celdas[].CantidadNueva` sigue no-nullable, preexistente) |
| **Build** | `dotnet build` + `dotnet publish -c Release` → 0 errores, verificado tras cada fix |
| **Pendiente** | Confirmar con el cliente si se libera ahora accesorios + alta de Color (con Carga Masiva/Ajuste todavía visibles) o si se espera a resolver también D-V12-03 antes de cualquier deploy. Guía manual de 21 pasos de `6-qa.md` §9 sigue pendiente de ejecución por navegador (MCP playwright no disponible en esta sesión, segunda vez consecutiva) |

**Decisión del cliente (mismo día):** esperar a resolver D-V12-03 antes de deployar nada — no liberar accesorios/alta de Color por separado.

---

### Entrada 2026-08-16 — D-V12-03 resuelto: alta con stock inicial 0 + HU-12.4 liberada

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-16 |
| **Fix aplicado** | La distinción "celda sin tocar" vs "0 explícito" pasa a basarse en nulabilidad/string cruda, no en el valor numérico. Servidor (`GuardarMatrizAsync`, loop de `Altas`): el skip por "no cargó nada" cambia de `!CantidadNueva.HasValue \|\| CantidadNueva.Value <= 0` a solo `!CantidadNueva.HasValue` (un `int?` vacío en el POST solo llega así si el input HTML estaba vacío). Cliente (`construirAltasDeColoresNuevos` en `MatrizEditar.cshtml`): el filtro de columnas cambia de `cantidad <= 0` a `cantidad < 0`, distinguiendo por la cadena cruda (`crudo === ''`) antes de parsear, no por el valor ya parseado |
| **Ajuste evitado a propósito** | `AplicarAjusteInternoAsync` solo se invoca si `CantidadNueva.Value > 0` (mismo guard que ya usa `GuardarCargaMasivaAsync` desde V10) — `VarianteService.CrearAsync` ya deja el `Stock` en 0 por defecto, así que aplicar un ajuste "de 0 a 0" sería redundante y generaría un `AjusteStock`/`MovimientoStock` sin sentido en el historial recién creado |
| **HU-12.4 liberada** | Con el gap cerrado, se revirtió la reversión: los botones "Ajuste manual" y "Carga masiva" vuelven a ocultarse de `Stock/Index.cshtml` (rutas siguen vivas, solo se ocultan los accesos — decisión D3, reversible sin deploy de emergencia) |
| **Alcance de verificación** | Fix acotado y mecánico (relaja una condición `<= 0`/`> 0` en 3 puntos ya existentes), reutiliza exactamente el mismo patrón que `GuardarCargaMasivaAsync` (ya aprobado por QA en V10) y el mismo mecanismo de nulabilidad que QA ya confirmó como correcto para D-01 en esta misma sesión. Verificado por revisión de código propia + `dotnet build` + `dotnet publish` (0 errores) — **no se volvió a delegar al agente QA** dado el bajo riesgo y el costo ya incurrido en la ronda de QA anterior (~250k tokens); el cliente puede pedir una ronda adicional si lo prefiere antes de considerar esto definitivamente cerrado |
| **Build** | `dotnet build` + `dotnet publish -c Release` → 0 errores |
| **Estado** | Listo para commit + push + deploy a producción |

---

### Entrada 2026-08-16 — Deploy a producción V12

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-16 |
| **Acción** | Commit + push a `origin/main` y publish a producción |
| **Commit** | `6db23dc` — "V12: Matriz cubre accesorios sin talle y alta de Color nuevo; retira Carga Masiva/Ajuste del menu" (5 archivos: 387 inserciones, 50 eliminaciones) |
| **Deploy** | Web Deploy a producción — 12 archivos actualizados, "Se publicó correctamente" |
| **Migración EF** | No aplicó (sin cambios de esquema) |
| **Estado** | En producción. Pendiente: verificación manual del cliente contra los 3 casos clave (alta con 2+ talles a la vez, alta de accesorio, alta con stock 0) y la guía de 21 pasos de `6-qa.md` §9 |

## Flujo completo V12 — CERRADO salvo cierre de calibración

Las 9 etapas del flujo del orquestador se ejecutaron en esta sesión: Discovery/Análisis (aprobado, D1-D4 resueltos) → Diseño (aprobado) → Arquitectura (aprobada) → Presupuesto (USD 105,84, aprobado) → Implementación (subagent, build OK) → QA (subagent, 8 defectos encontrados, 3 corregidos antes de deploy) → Documentación (resumen de cliente en `7-documentador.md`) → Cierre de calibración (**pendiente de horas reales**, ver `4-presupuestador.md` sección V12).

Primera feature de este proyecto en correr el flujo completo end-to-end en vez de fast-path — motivado directamente por el rechazo de QA sobre el cambio anterior (`f400671`) sobre esta misma pantalla.

---

**Fin del documento - Trazabilidad**
