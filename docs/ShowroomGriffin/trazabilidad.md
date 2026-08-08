# 🏗️ Trazabilidad de Conversación - ShowroomGriffin
**Proyecto:** ShowroomGriffin  
**Fecha inicio:** 2026-04-23  
**Última actualización:** 2026-07-31  

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

**Fin del documento - Trazabilidad**
