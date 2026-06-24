# QA — KOI Dumplings · Memoria acumulativa del agente QA
> Última actualización: sesión 2026-06-18 · Etapa: QA inicial (E1–E9 implementados)

---

## 1. Alcance funcional validado

| Módulo / Pantalla | Estado |
|---|---|
| P-02 Dashboard | ✅ VALIDADO |
| P-03 ER Mensual (carga y recalcular) | ✅ VALIDADO (con defecto menor: IDs HTML duplicados) |
| P-04 ER Anual (grilla) | ⚠️ PARCIAL — falta export Excel y link en sidebar Inversor |
| P-05 Indicadores de venta | ✅ VALIDADO |
| P-06 Cámaras (ver + config) | ⚠️ PARCIAL — defecto KOI-001 (botón eliminar sin efecto) |
| P-07 Puntos de inversión (ABM) | ✅ VALIDADO |
| P-08 Liquidaciones + Cierre | ⚠️ PARCIAL — defecto KOI-004 (consumos > bruto sin bloqueo) |
| P-09 Mi Inversión | ✅ VALIDADO |
| P-10 Reparto General | ✅ VALIDADO |
| P-11 Tipo de cambio | ✅ VALIDADO |
| P-12 Configuración (Rubros/Subgrupos/Params) | ⚠️ PARCIAL — defecto KOI-001 (eliminar sin efecto) |
| P-13 Importación histórica | ✅ VALIDADO |
| P-14 Notificaciones de cierre | ✅ VALIDADO (fire-and-forget, reenvío manual, registro) |
| Autenticación / Roles | ✅ VALIDADO |
| Tema dark/light | ✅ VALIDADO |
| Sidebar por rol | ⚠️ PARCIAL — defecto KOI-003 (inversor no ve Vista Anual ER) |

---

## 2. Cobertura por criterio de aceptación

| Criterio | CU | Estado | Notas |
|---|---|---|---|
| Total Ventas = A + B | CU-06 | ✅ PASS | Validado en código y UI |
| Bases porcentuales correctas (VentasA vs VentasTotales) | CU-06 | ✅ PASS | Verificado en EstadoResultadosService |
| Resultado = Ventas - Gastos; sin /0 | CU-06 | ✅ PASS | Guard incluido |
| Valores USD = ARS / TC; aviso si falta TC | CU-06 | ✅ PASS | |
| Total anual = suma 12 meses | CU-06 | ✅ PASS | Calculado en ObtenerResumenAnualAsync |
| Inversor ve mismos totales que Excel migrado | CU-08 | BLOCKED (requiere datos de muestra) | Pendiente smoke con datos reales |
| Dark/light persiste por usuario | CU-08 | ✅ PASS | ToggleTema en AccountController |
| Cards de ventas, gastos, resultado, USD, indicadores, gráfico | CU-08 | ✅ PASS | |
| Suma puntos ≤ 100 | CU-09 | ✅ PASS | Validado en InversionesService línea 76 |
| Utilidad por punto = Resultado / 100 | CU-10 | ✅ PASS | |
| Liquidación = puntos × utilidad - consumos | CU-10 | ✅ PASS (cálculo OK) | ⚠️ Sin guard consumos > bruto — KOI-004 |
| Consumos no superan bruto (bloqueante) | CU-10 | ❌ FAIL | KOI-004 |
| Liquidación pagada es inmutable | CU-10 | ✅ PASS | InversionesService.MarcarPagadasAsync |
| Reabrir liquidación individual con motivo | CU-10 | ✅ PASS | LiquidacionesController.Reabrir |
| Inversor ve solo sus propios datos | CU-11 | ✅ PASS | MiInversionController.Forbid() |
| Historial reproduce valores Excel | CU-11 | BLOCKED (requiere datos de muestra) | |
| Inversor accede a cámaras si está configurado | CU-14 | ✅ PASS | CamarasController permisos OK |
| Email enviado al cerrar, fallo no bloquea cierre | CU-16 | ✅ PASS | fire-and-forget Task.Run |
| Re-cierre no duplica emails sin confirmación | CU-16 | ⚠️ MINOR | PeriodoTieneEnviosAsync existe pero no se usa como guard |
| Fallo de email queda registrado, Admin puede reenviar | CU-16 | ✅ PASS | RegistroEnvioNotificacion + ReenviarAsync |
| Exportar P-04 a Excel | CU-06/P-04 | ❌ FAIL | KOI-002 |

---

## 3. Máquina de estados

### Período mensual (Abierto → Cerrado)

| Transición | Condición | Implementada | Resultado |
|---|---|---|---|
| Abierto → Cerrado | TC cargado + ventas != 0 | ✅ Sí | GenerarPreviewCierreAsync + CerrarPeriodoAsync |
| Cerrado → Reabierto | ELIMINADO (D-04) | ✅ Correcto | EstadoPeriodo enum solo Abierto/Cerrado |
| Cerrar período sin TC | Bloqueante | ✅ Sí | Validacion en GenerarPreviewCierreAsync |
| Cerrar período con ventas = 0 | Bloqueante | ✅ Sí | Validacion en GenerarPreviewCierreAsync |
| Cerrar período con consumo > bruto | Bloqueante | ❌ NO | KOI-004 — falta validación |

### Liquidación (Pendiente ↔ Pagada)

| Transición | Condición | Implementada | Resultado |
|---|---|---|---|
| Pendiente → Pagada | Fecha de pago informada | ✅ Sí | MarcarPagadasAsync |
| Pagada → Pendiente (Reabrir) | Solo Admin + motivo obligatorio | ✅ Sí | ReabrirAsync con motivo |
| Pendiente → Pagada sin fecha | Bloqueante | ✅ Sí | ModelState Required en MarcarPagadasViewModel |
| Pagada → Pagada (doble mark) | No permitido | ✅ Sí | InversionesService filtra solo Pendientes |

---

## 4. Cobertura del catálogo cross-proyecto

| id | Aplica | Resultado | Acción |
|---|---|---|---|
| REG-001 RowVersion MySQL | N/A | — | Proyecto KOI no usa RowVersion |
| REG-002 StockInicial variante | N/A | — | No aplica (sin variantes/stock) |
| REG-003 Autocomplete sin resultados | N/A | — | No hay autocomplete crítico |
| REG-004 Filtro activo/inactivo | Sí | PASS | Soft delete activo en AppDbContext |
| REG-005 Exportar Excel vacío | Sí | FAIL → KOI-002 | P-04 export no implementado |
| REG-006 Total erróneo con decimales | Sí | PASS | Cálculo en decimal, redondeo Math.Round |
| REG-007 Cascada combo de selects | Sí | PASS | Combos Puntos/Subgrupos/TipoCambio OK |
| REG-008 Input pierde foco al tipear | Sí | PASS | Inputs ER/Preview no rerrenderizan DOM |
| REG-009 Cascada Categoria→Subgrupo | Sí | PASS | Un solo nivel; no aplica cascada multipaso |
| REG-010 Menu visible para rol incorrecto | Sí | FAIL → KOI-003 | Vista Anual ER visible solo a Admin; Inversor no la ve |

---

## 5. Defectos detectados

### KOI-001 — CRÍTICO: Eliminar no funciona en Rubros, Subgrupos, Parámetros, Cámaras
- **Severidad**: Critical
- **Archivos afectados**: `KoiDumplings.Web/wwwroot/js/site.js`, 4 vistas
- **Causa raíz**: `site.js` handler usa `btn.closest('form')` → retorna `null` cuando el `<form>` está fuera del botón. Las 4 vistas afectadas usan `data-form`, `data-form-id` o `data-action` para referenciar el form externo.
- **Pasos para reproducir**: Configuración → Rubros → clic en ícono eliminar → confirmar → nada ocurre.
- **Fix requerido**: Extender handler en `site.js` para resolver `data-form-id`, `data-form` (by id) y `data-action` (POST via fetch o form dinámico).

### KOI-002 — MAYOR: Export Excel faltante en P-04 Vista Anual ER
- **Severidad**: Major
- **Archivos afectados**: `EstadoResultados/Anual.cshtml`, `EstadoResultadosController.cs`
- **Causa raíz**: Funcionalidad no implementada (spec P-04: "Exportable a Excel").
- **Fix requerido**: Agregar acción `ExportarAnualExcel(int anio)` en el controller usando `IExportService` + botón en vista.

### KOI-003 — MAYOR: Inversor no ve "Vista Anual ER" en el sidebar
- **Severidad**: Major
- **Archivos afectados**: `_Layout.cshtml`
- **Causa raíz**: Link está dentro del bloque `@if (Administrador || SuperUsuario)` sin duplicarse para el rol `Inversor`.
- **Fix requerido**: Agregar link "Vista Anual ER" en el bloque `@if (Inversor)` del sidebar.

### KOI-004 — MAYOR: Consumos pueden superar bruto sin validación bloqueante
- **Severidad**: Major
- **Archivos afectados**: `PreviewCierre.cshtml`, `EstadoResultadosService.cs`
- **Causa raíz**: Input `consumo-input` sin `max`; JS no valida al submit; `CerrarPeriodoAsync` no valida `consumos <= bruto`.
- **Pasos para reproducir**: Admin → Cerrar período → ingresar consumo > bruto de cualquier inversor → Confirmar → cierre ejecutado con neto negativo.
- **Fix requerido**: Validación JS bloqueante + guard en `CerrarPeriodoAsync`.

### KOI-005 — MENOR: IDs HTML duplicados en P-03 Mensual
- **Severidad**: Minor
- **Archivos afectados**: `EstadoResultados/Mensual.cshtml`
- **Detalle**: `id="lblVentasA"` aparece en líneas 126 y 146; `id="lblVentasTotales"` en líneas 130 y 147. HTML inválido; jQuery actualiza ambos nodos (funciona), pero viola la spec HTML y puede fallar en contextos nativos (getElementById).
- **Fix requerido**: Renombrar uno de los pares a `id="tblVentasA"` / `id="tblVentasTotales"` y ajustar el selector en la función `recalcularTotalesVenta`.

### KOI-006 — MINOR: PeriodoTieneEnviosAsync no se usa como guard en EnviarNotificacionCierreAsync
- **Severidad**: Minor (teórico: Período no puede reabrirse por D-04)
- **Detalle**: El método existe en `INotificacionCierreService` pero `EnviarNotificacionCierreAsync` no lo llama antes de enviar → si se llama dos veces sobre el mismo período, se duplicarían los emails y los registros.
- **Fix recomendado**: Agregar guard al inicio de `EnviarNotificacionCierreAsync` (o al menos log de advertencia si `PeriodoTieneEnviosAsync` retorna `true`).

---

## 6. Plan de implementación de fixes

| # | Bug | Prioridad | Archivo principal | Estado |
|---|---|---|---|---|
| 1 | KOI-001 — Eliminar no funciona | P0 | `wwwroot/js/site.js` | ✅ APLICADO |
| 2 | KOI-004 — Consumos > bruto | P1 | `PreviewCierre.cshtml` + `EstadoResultadosService.cs` | ✅ APLICADO |
| 3 | KOI-003 — Inversor sin link Anual ER | P1 | `_Layout.cshtml` | ✅ APLICADO |
| 4 | KOI-002 — Export Excel P-04 | P2 | `Anual.cshtml` + `EstadoResultadosController.cs` | ⏳ PENDIENTE |
| 5 | KOI-005 — IDs duplicados Mensual | P3 | `Mensual.cshtml` | ✅ APLICADO |
| 6 | KOI-006 — Guard duplicado notif. | P3 | `NotificacionCierreService.cs` | ✅ APLICADO |

---

## 7. Riesgos de liberación y mitigaciones

| Riesgo | Severidad | Mitigación |
|---|---|---|
| KOI-001: Eliminar de Rubros/Subgrupos/Parámetros/Cámaras no funciona | 🔴 ALTO | Bloquear release hasta fix aplicado y validado |
| KOI-004: Neto negativo en liquidaciones puede generarse | 🟠 MEDIO | Bloquear cierre de período hasta fix; validar manualmente antes de cada cierre |
| KOI-002: Falta Export Excel P-04 | 🟡 BAJO | Funcionalidad esperada por spec; no bloquea operación diaria. Puede lanzarse sin ella con nota en backlog |
| KOI-003: Inversor navega a Anual ER solo por URL directa | 🟡 BAJO | URL directa funciona; solo falta el link en sidebar |
| KOI-005: IDs duplicados HTML | 🟢 MUY BAJO | Funciona con jQuery; no hay impacto real inmediato |
| Datos históricos sin validar contra Excel fuente | 🟠 MEDIO | CU-08 y CU-11 requieren smoke test con 3 meses de muestra real antes de go-live |

---

## 8. Pruebas mínimas ejecutadas

| Prueba | Módulo | Resultado |
|---|---|---|
| Ingreso y recálculo de ventas A/B en P-03 | ER Mensual | ✅ |
| GuardarVentas via AJAX actualiza totales en pantalla | ER Mensual | ✅ |
| Grilla anual muestra resumen de meses | ER Anual | ✅ |
| Navegación año anterior/siguiente | ER Anual | ✅ |
| Combo inversores en Puntos/Crear | Puntos | ✅ |
| Validación suma puntos ≤ 100 | Puntos | ✅ (código) |
| Combo rubros en Subgrupo/Crear | Configuración | ✅ |
| Selección cotización en TipoCambio | TipoCambio | ✅ |
| Dashboard cards y gráfico histórico | Dashboard | ✅ |
| Inversor no accede a datos de otro inversor | MiInversión | ✅ |
| Toggle dark/light persiste en cookie | Layout | ✅ |
| Email fuego-y-olvido al cerrar período | Cierre / CU-16 | ✅ (código) |
| Reenvío individual de notificación | Notif. cierre | ✅ (código) |
| Soft delete activo (query filter global) | General | ✅ |
| Anti-forgery en todos los POST | General | ✅ |
| Eliminar Rubro/Subgrupo/Parámetro/Cámara | Configuración | ❌ KOI-001 |
| Consumos > bruto bloqueados en preview cierre | Cierre | ❌ KOI-004 |
| Export Excel P-04 | ER Anual | ❌ KOI-002 |
| Link Vista Anual ER para rol Inversor | Sidebar | ❌ KOI-003 |

---

## 9. Checklist de salida para merge

- [ ] **KOI-001 RESUELTO** — `site.js` handler cubre `data-form`, `data-form-id` y `data-action`
- [ ] **KOI-004 RESUELTO** — Validación JS en submit + guard en `CerrarPeriodoAsync`
- [ ] **KOI-003 RESUELTO** — Link "Vista Anual ER" visible para Inversor en sidebar
- [ ] **KOI-002 RESUELTO o en backlog acordado** — Export Excel P-04
- [ ] **KOI-005 RESUELTO** — IDs HTML únicos en Mensual.cshtml
- [ ] **KOI-006 RESUELTO o documentado** — Guard en EnviarNotificacionCierreAsync
- [ ] Build limpio (`dotnet build` sin errores ni warnings)
- [ ] `dotnet ef migrations has-pending-model-changes` → sin cambios
- [ ] Smoke test con datos reales de 3 meses (CU-08 / CU-11) antes de go-live
- [ ] Validación manual del flujo completo de cierre: Mensual → TipoCambio → PreviewCierre → ConfirmarCierre → Liquidaciones
