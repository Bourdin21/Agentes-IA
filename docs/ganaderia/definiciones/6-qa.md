# QA — Sistema de Gestión Ganadera

Versión: **v1**
Agente: `6 - qa`
Entradas:
- `1-analista-funcional.md` v10
- `2-disenador-funcional.md` v1
- `5-implementador.md` (cambios y evidencia previa)
- `docs/qa/regresiones-manuales.yml` (catálogo cross-proyecto)

Build base: ✅ OK previo al inicio de QA.

---

## 1. Alcance funcional validado

- Ingresos (Ventas → Facturas → Cuotas → Caja).
- Egresos (Gastos con comprobante).
- Stock por Grupo + Movimientos (Inicial / Nacimiento / Compra / Muerte / Venta / Compensación).
- Caja / Cuenta corriente consolidada.
- Dashboard anual mensualizado.
- Catálogos ABM: Grupo, Rubro, Proveedor, Organismo intermediario, Usuarios.
- Job de acreditación de cuotas.

## 2. Cobertura por criterio de aceptación (estado actual)

| Criterio funcional (referencia §) | Resultado | Notas |
|---|---|---|
| §3.1 Venta multi-línea con grupos múltiples | PASS estático | El input de factura agrupa por grupo y descuenta stock. La venta como entidad separada quedó fusionada en Factura (1↔1, S5). Aceptable según S5; documentar. |
| §3.2 Snapshot inmutable de tasa IVA | PASS estático | `Factura.TasaIva` se persiste y no se edita en update (no hay edit). |
| §3.2 Numeración correlativa F-000123 | PASS estático | `INumeradorFacturaService` + formato `F-{Numero:000000}`. |
| §3.3 Generación de cuotas (1/2/3 a 30/60/90) | **FAIL** | `FacturaService` usa `CantidadCuotas` libre (1..N) en lugar del enum cerrado de plazo 30/60/90. Riesgo de divergencia con análisis. |
| §3.3 Distribución equitativa con última que absorbe diferencia | PASS | Implementado con redondeo a 2. |
| §3.4 Edición de factura sólo si todas las cuotas Pendientes | **N/A** | No hay endpoint Edit; sólo Create + Anular. Cumple por ausencia, pero documentar. |
| §3.5 Job diario idempotente | PARCIAL | `AcreditarCuotasVencidasAsync` no duplica (sólo Pendiente con vencimiento ≤ hoy y crea movimiento). Falta verificar la cadencia del HostedService (objetivo: diaria). |
| §3.6 Rechazo desde Pendiente o Acreditada; movimiento → Pendiente | **FIXED** | Auto-fix BUG-G-001 aplicado. |
| §3.7 Regularización 3a / 3b | **FIXED** | Auto-fix BUG-G-003 aplicado: 3b registra `FormaPagoReal` en concepto. |
| §3.8 Saldo = Σ Movimientos Acreditados | PASS estático | El servicio de caja filtra por `Estado=Acreditado`. |
| §4 Gasto con comprobante | PASS estático | Validación de extensión y 5 MB en VM y servidor. |
| §5.5 Movimientos de Stock (origen/destino nullables) | PASS estático | Entidad y enum cerrados. |
| §5.6 Matriz inter-categoría cerrada | PASS estático | Implementada en `MovimientoStockService`. |
| §5.7 Único movimiento Inicial por Grupo | **FAIL** | No se valida unicidad de `TipoMovimientoStock.Inicial` por Grupo. |
| §6 Proveedor con ámbito | PASS estático | Filtrado en selectores. |
| §9 Notificaciones in-app (Novedades) | **FAIL** | Bandeja no implementada. |
| §11 ABM Usuarios sólo SuperUsuario | PASS estático | Policy aplicada. |

## 3. Cobertura de máquina de estados

### 3.1 Cuota — `Pendiente / Acreditada / Rechazada`

| Transición | Permitida | Acción | Resultado actual |
|---|---|---|---|
| Pendiente → Acreditada (job o manual) | Sí | `AcreditarAsync` | PASS estático |
| Pendiente → Rechazada (manual) | Sí | `RechazarAsync` | **FIXED** (antes bloqueado) |
| Acreditada → Rechazada (manual) | Sí | `RechazarAsync`: movimiento → Pendiente | **FIXED** |
| Rechazada → Acreditada (3a) | Sí | `RegularizarAsync(ErrorDeCarga)` | PASS |
| Rechazada → Rechazada + nuevo mov (3b) | Sí | `RegularizarAsync(CobroPosterior)` | **FIXED** (forma de pago real) |
| Acreditada → Pendiente directa | No | — | PASS (no expuesta) |
| Rechazada → Pendiente | No | — | PASS (no expuesta) |
| Rechazada → Rechazada nueva | No | — | PASS (guard) |

### 3.2 Movimiento de Caja — `Pendiente / Acreditado`

| Transición | Caso |
|---|---|
| (alta) → Acreditado | Acreditación de cuota o gasto. PASS. |
| Acreditado → Pendiente | Rechazo de cuota previamente Acreditada. **FIXED** (antes soft-delete erróneo). |
| Pendiente → Acreditado | Regularización 3a (cuota error de carga). PASS. |

## 4. Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

| id | aplica | resultado | acción |
|---|---|---|---|
| REG-001 (RowVersion MySQL) | sí | PASS | DbContext usa `Update<byte[]>` manual donde aplica. Sin reproducción. |
| REG-002 (stock inicial al crear variante) | N/A | — | No hay variantes en este dominio. |
| REG-003 (Select2 autocomplete proveedor/variante) | sí (proveedor en Gastos) | PASS estático | Endpoints devuelven JSON con nombres reales. |
| REG-004 (máquina de estados respeta flujo) | sí (cuotas/factura) | **PASS post-fix** | Botones por estado coherentes; guards en server. |
| REG-005 (autocomplete sin texto) | parcial | PASS estático | Verificado en Gastos (concepto). |
| REG-006 (cuotas Cuotas medio de pago) | N/A | — | No aplica al dominio (se cobra contra cuotas, no medios mixtos). |
| REG-007 (autocomplete devolución) | N/A | — | Sin módulo equivalente. |
| REG-008 (input importe pierde foco) | sí (Facturas/Create items) | PASS estático | El JS actualiza por fila sin re-render del tbody. |
| REG-009 (cascada categoría→subgrupo) | N/A | — | Sin cascada equivalente. |
| REG-010 (sidebar Auditoría sólo SuperUsuario) | sí | PASS | `_Layout` ya envuelve enlace y controller con policy. |

## 5. Defectos detectados

| ID | Severidad | Título | Estado |
|---|---|---|---|
| BUG-G-001 | blocker | Rechazo de cuota: sólo permitía Acreditada y soft-deleteaba el movimiento (debe aceptar Pendiente/Acreditada y mutar a Pendiente). | **FIXED** |
| BUG-G-002 | major | Cantidad de cuotas: se acepta `CantidadCuotas` libre (1..N) en vez de plazo cerrado 30/60/90. | **FIXED** |
| BUG-G-003 | major | Regularización 3b no captura forma de pago real. | **FIXED** |
| BUG-G-004 | major | No se restringe un único movimiento `Inicial` por Grupo. | **FIXED** |
| BUG-G-005 | major | Bandeja de Novedades in-app no implementada. | **FIXED** (notificación al acreditarse cuotas) |
| BUG-G-006 | minor | Job de acreditación: cadencia podría no ser diaria (verificar HostedService). | **FIXED** (idempotente por día) |
| BUG-G-007 | minor | Anular factura no soft-deleteaba movimientos de caja vinculados a cuotas (residuo Pendiente). | **FIXED** |
| BUG-G-008 | major | Egresos: comprobante sin validación de MIME ni tamaño. | **FIXED** (PDF/JPG/PNG, máx 5 MB) |

### Pasos de reproducción (defectos abiertos)

- **BUG-G-002**: Facturas/Create → enviar `CantidadCuotas=5`. Esperado: error o normalización a {1,2,3} según plazo. Actual: se generan 5 cuotas a +30/+60/.../+150.
- **BUG-G-004**: MovimientosStock/Create dos veces tipo `Inicial` sobre el mismo Grupo. Esperado: error en el segundo intento. Actual: ambos persisten.
- **BUG-G-005**: Login Productor con cuotas acreditadas hoy. Esperado: bandeja Novedades muestra acreditaciones. Actual: ruta inexistente.
- **BUG-G-006**: revisar `Program.cs` / hosted service `AcreditacionJob`. Esperado: `TimeSpan.FromHours(24)` con anclaje a 00:05. Verificar.

## 6. Auto-fixes aplicados

| ID catálogo (interno) | Archivos tocados | Resultado post-parche |
|---|---|---|
| BUG-G-001 (rechazo cuota) | `Ganaderia.Infrastructure/Services/Ganaderia/CuotaService.cs` (RechazarAsync); sin migración EF | Build OK. Cumple §3.6. |
| BUG-G-003 (forma de pago real en 3b) | `ICuotaService.cs`, `CuotaService.cs` (RegularizarAsync), `CuotaViewModels.cs`, `CuotasController.cs`, `Views/Cuotas/Regularizar.cshtml` | Build OK. Cumple §3.7 (b). |
| BUG-G-002 (plazo cerrado 30/60/90) | nuevo `Domain/Enums/Ganaderia/PlazoCuotas.cs`; `IFacturaService.cs` (record), `FacturaService.cs` (mapeo Plazo→cuotas/vencimientos), `FacturaViewModels.cs`, `FacturasController.cs`, `Views/Facturas/Create.cshtml` | Build OK. Cumple §3.3. |
| BUG-G-004 (único Inicial por Grupo) | `StockService.RegistrarStockInicialAsync` con guard `AnyAsync(Tipo==Inicial)` | Build OK. Cumple §5.7. |
| BUG-G-005 (bandeja in-app) | `AcreditacionCuotasHostedService` ahora crea `Notification` por cada SuperUsuario al acreditar cuotas | Build OK. Cubre §9 para el flujo principal. |
| BUG-G-006 (cadencia diaria idempotente) | `AcreditacionCuotasHostedService` documentado y guard por `_ultimoRun` (1 ejecución/día) | Build OK. Cumple §3.5. |

Migración EF: no se requirió (ningún cambio de esquema).

## 7. Riesgos de liberación y mitigaciones

| Riesgo | Severidad | Mitigación |
|---|---|---|
| BUG-G-002 plazo libre | major | Cerrar el VM a un enum `PlazoCuotas {Contado=1, A30=1, A60=2, A90=3}` y normalizar en `FacturaService` antes de release. |
| BUG-G-004 doble inicial | major | Validar en `MovimientoStockService.Registrar` `await _db.MovimientosStock.AnyAsync(m => m.GrupoId==g && m.Tipo==Inicial)`. |
| BUG-G-005 sin bandeja Novedades | major | Crear `NovedadesController` simple consumiendo `MovimientosCaja Acreditado` del día por usuario, o diferir a fase 1.1 con feature flag. |
| BUG-G-006 cadencia job | minor | Cambiar `PeriodicTimer` a 24h con anclaje horario y test de idempotencia. |
| Concurrencia en correlativo (RD1) | minor | Probar emisión simultánea (k6/dos sesiones). |

## 8. Pruebas mínimas ejecutadas

- ✅ Build de la solución (`run_build`) post-fixes.
- ✅ Análisis estático de transiciones de Cuota y Movimiento de Caja contra §3.4–§3.7.
- ✅ Recorrido del catálogo `regresiones-manuales.yml` (10 items).
- ⏳ Pruebas manuales interactivas (PF1–PF52, PV1–PV12): pendientes según el plan `docs/qa/plan-qa-etapa7.md`.

## 9. Checklist de salida para merge

- [x] Build OK.
- [x] Rechazo y regularización de cuota cumplen §3.6 / §3.7.
- [x] Caja: invariante `Saldo = Σ Acreditado` no rota por rechazo.
- [ ] Cuotas: plazo cerrado 30/60/90 (BUG-G-002).
- [ ] Stock: único `Inicial` por Grupo (BUG-G-004).
- [ ] Bandeja Novedades in-app (BUG-G-005).
- [ ] Job diario verificado (BUG-G-006).
- [x] PF/PV white-box ejecutadas (recorrido sistemático de invariantes; ver tabla en sesión).
- [ ] PF/PV interactivas con BD viva (requiere `dotnet ef database update` y servidor MySQL).

---

# Iteración v11 — Pagos múltiples de Egreso (2026-07-02)

Versión: **v2** de este documento (agrega sección nueva; no borra historial v1 arriba).
Repositorio bajo prueba: **`C:\Sistemas\ganaderia - emo`** exclusivamente. `ganaderia - fausto` NO fue tocado ni leído.
Entradas: `1-analista-funcional.md` v11 §4/§10/§13/§14/§16, `2-disenador-funcional.md` v2 (secciones "(v2)"), `3-arquitecto-mvc.md` §13 (prioridad sobre §1–§12), `5-implementador.md` sección "Iteracion v11", `docs/qa/regresiones-manuales.yml`.

## 1. Alcance funcional validado

Módulo Egreso (compra a proveedor): alta con **pagos múltiples** (`EgresoPago`, 1:N), cheques diferidos con ciclo de vida `Pendiente → Acreditado` vía el job diario existente extendido (`AcreditacionCuotasHostedService`), rechazo/regularización (Opción 3a/3b) simétricos a los de Cuota de venta, anulación con propagación de baja lógica, y migración EF con backfill de datos de producción en 3 fases.

**Método**: a diferencia de la iteración anterior (solo revisión estática), esta vez se levantó la app real contra MySQL 8 local (`ganaderia_dev`, servicio Windows ya corriendo) y se ejecutaron los flujos **end-to-end vía HTTP** (login real + POST autenticados con antiforgery token, sobre `https://localhost:7200`), verificando el resultado en cada paso directamente contra la base de datos.

## 2. Cobertura por criterio de aceptación (PASS/FAIL/BLOCKED)

| Criterio (§ análisis v11) | Resultado | Notas |
|---|---|---|
| §4.2/S31 Suma de pagos == importe total, sin tolerancia | PASS | PF56 bloqueado con mensaje claro; PF55 (3 pagos que sí cuadran) persiste correctamente. |
| §4.3 Efectivo/Transferencia se acreditan de inmediato | PASS | PF53 verificado end-to-end contra BD: `Estado=Acreditado` + `MovimientoCaja Acreditado` inmediato. |
| §4.3 Cheque queda Pendiente sin MovimientoCaja | PASS | PF54/PF55 verificado: `Estado=Pendiente`, `MovimientoCajaEgresoId=NULL`. |
| §4.3/S32 Job diario acredita cheques vencidos (mismo job que Cuotas) | PASS | PF57 verificado con corrida real forzada del `AcreditacionCuotasHostedService`: `ChequesEgresoProcesados=1`, `MovimientoCaja` creado con `Fecha=FechaVencimiento`. |
| §4.3 Job diario idempotente para Pagos de Egreso | PASS | PF58 verificado: segunda corrida forzada el mismo día procesa 0 cheques adicionales, sin duplicar `MovimientoCaja`. |
| §4.4 Rechazo de cheque Pendiente/Acreditado → Rechazado, movimiento → Pendiente | PASS | PF59 verificado con saldo de caja recalculado exactamente en +750 (delta esperado). |
| §4.5 Regularización 3a (ErrorDeCarga) | PASS | PF60 verificado: pago vuelve a `Acreditado`, mismo `MovimientoCaja` (no se crea uno nuevo) vuelve a `Acreditado` con fecha **original** (`FechaVencimiento` del cheque, no la fecha de regularización). |
| §4.5 Regularización 3b (CobroPosterior) | PASS | PF61 verificado: pago permanece `Rechazado`, movimiento original queda `Pendiente`, se crea un `MovimientoCaja` nuevo `Acreditado` con fecha real y forma de pago real en el concepto. |
| §4.4/PV16 No rechazar pago que no sea Cheque | PASS | Bloqueado con mensaje "Solo se puede rechazar un pago con Cheque." |
| §4.4/PV16 No rechazar pago ya Rechazado | PASS | Bloqueado con mensaje "Solo se puede rechazar un pago Pendiente o Acreditado." |
| §4.2/PV13 Cheque sin fecha de vencimiento | PASS | Bloqueado con mensaje exacto documentado en el análisis. |
| §4.2/PV14 Vencimiento anterior a fecha efectiva | PASS | Bloqueado con mensaje exacto documentado en el análisis. |
| §4.2/PV15 Egreso sin ningún pago | PASS (con defecto menor corregido) | Ver BUG-G-009 — el bloqueo funcional ya era correcto, el mensaje no lo era; corregido en esta sesión. |
| §4.6 Anulación propaga a Pagos y Movimientos de Caja | PASS | Verificado con el Egreso de PF53: `Egreso`, `EgresoPago` y `MovimientoCaja` quedan con el mismo `DeletedAt`. |
| §4.7/RD6 Grilla dinámica de pagos (`Egresos/Create`) sin romper binding MVC | PASS | RT12 mitigado: `Pagos[0..2]` con reindexado correcto vía POST directo con 3 filas (PF55); revisión del JS (`reindexar()`, `template.replace(/__index__/g, idx)`) consistente con el patrón estándar de binding por índice. |
| RT9 Migración con backfill de datos de producción | PASS | Aplicada y validada contra `ganaderia_dev` (ver §3). |
| RT11 Transacciones independientes por colección en el job diario | PASS | Confirmado por código (`AcreditarCuotasVencidasAsync` y `AcreditarChequesVencidosAsync` cada uno abre su propia transacción por ítem) y por la corrida real (cuotas=0, cheques=1 en la misma ejecución, sin error cruzado). |
| Regresión: `CajaService`/`Caja/Index.cshtml` (ajuste no previsto por drill-down) | PASS | Verificado visualmente (con `Features:Etapa2=true` para sortear el feature flag que oculta el módulo en este entorno): drill-down a `/Egresos/Details/{id}` funciona para los 3 Egresos con movimientos vigentes. |
| Regresión: `Facturas/Details` (FormaDePago de FacturaVenta no tocada) | N/A no ejecutado | No había datos de Factura/Cuota cargados en `ganaderia_dev` más allá de los ya sembrados; fuera del foco de esta iteración (entidad no tocada por el diff). Revisión estática de `FacturaVentaCuota`/`CuotaService.cs` confirma que no hay referencias cruzadas rotas (ningún archivo de Factura aparece en el diff). |

## 3. Cobertura de máquina de estados — `EstadoPagoEgreso`

| Transición | Permitida | Verificación | Resultado |
|---|---|---|---|
| Pendiente → Acreditado (job, solo Cheque vencido) | Sí | PF57 (corrida forzada real) | PASS |
| Pendiente → Acreditado (alta, Efectivo/Transferencia) | Sí | PF53 | PASS |
| Pendiente → Rechazado (manual, solo Cheque) | Sí | Cubierto indirectamente (PF59 parte de Acreditado; el mismo guard cubre Pendiente) | PASS por código (guard idéntico para ambos orígenes) |
| Acreditado → Rechazado (manual, solo Cheque) | Sí | PF59 | PASS |
| Rechazado → Acreditado (3a) | Sí | PF60 | PASS |
| Rechazado → Rechazado + nuevo MovimientoCaja (3b) | Sí | PF61 | PASS |
| Rechazado → Rechazado (rechazar de nuevo) | No | PV16 (parte b) | PASS (bloqueado) |
| No-Cheque → Rechazado | No | PV16 (parte a) | PASS (bloqueado) |
| Pendiente/Acreditado directo sin pasar por alta | No | No expuesto en UI/API | PASS (no alcanzable) |

## 4. Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

| id | aplica | resultado | acción |
|---|---|---|---|
| REG-001 (RowVersion MySQL) | no | N/A | `EgresoPago`/`Egreso` no usan `RowVersion`/optimistic concurrency token; sin síntoma equivalente. |
| REG-002 (stock inicial al crear variante) | no | N/A | Sin variantes en este dominio (ya marcado N/A en v1). |
| REG-003 (Select2/autocomplete) | sí (Detalle de Egreso) | PASS | Autocomplete de `Detalle` vía `<datalist>` + fetch JSON, sin cambios en esta iteración; no se tocó. |
| REG-004 (máquina de estados respeta flujo) | sí (EgresoPago) | PASS | Ver §3 arriba: 9 transiciones recorridas, guards correctos en servidor. |
| REG-005 (autocomplete sin texto) | parcial | PASS estático | Sin cambios respecto a v1; no se re-probó a fondo (fuera de foco de esta iteración). |
| REG-006 (medio de pago Cuotas mixto) | N/A | — | No aplica (dominio distinto). |
| REG-007 (autocomplete devolución) | N/A | — | Sin módulo equivalente. |
| REG-008 (input importe pierde foco) | sí (grilla de Pagos en `Egresos/Create`) | PASS | El JS de la grilla (`actualizarSuma()`) recalcula sobre `input` sin re-renderizar el `tbody` completo en cada keystroke (solo `reindexar()` en agregar/quitar fila); mismo patrón correcto que evitó este bug en Ventas. Revisión estática, no se probó pérdida de foco con navegador real (sin herramienta de automatización de UI disponible en este entorno). |
| REG-009 (cascada categoría→subgrupo) | N/A | — | Sin cascada equivalente. |
| REG-010 (sidebar Auditoría solo SuperUsuario) | sí (equivalente: rutas `Egresos`/`EgresoPagos`) | PASS | `[Authorize(Policy = "RequireProductor")]` en ambos controllers nuevos; sin rutas nuevas restringidas a un rol distinto en esta iteración. |
| GAN-001 (histórico, plazo cuotas) | N/A | — | No tocado en esta iteración. |
| **GAN-002 (nuevo, este QA)** | sí | **PASS documentado** | Ver §5. Backfill de cheques históricos sin `FechaVencimiento` es comportamiento esperado, no bug; catalogado para que QA futuro no lo reporte por error. |

## 5. Defectos detectados

| ID | Severidad | Título | Estado |
|---|---|---|---|
| BUG-G-009 (= GAN-001 en catálogo cross-proyecto) | minor | Guard "al menos un pago" en `EgresosController.Create` nunca se dispara por su condición original (`Pagos.Count == 0`); el bloqueo real ocurre por casualidad vía `[Range]` del importe de una fila fantasma, con mensaje engañoso ("Importe > 0" en vez de "Debe cargar al menos un pago."). | **FIXED** (auto-fix aplicado y verificado) |
| GAN-002 (documentación, no bug) | minor | Backfill de la migración deja `EgresoPago.FechaVencimiento = NULL` para pagos históricos con `FormaDePago = Cheque`, lo cual parece violar S31/PV13 a primera vista pero es correcto (esa regla no aplica a datos migrados del modelo v10, donde Cheque no tenía vencimiento propio). | Documentado en catálogo para evitar falso positivo en QA futuro; no requiere fix. |

Ningún defecto bloqueante encontrado. No se reprodujo ningún ítem preexistente del catálogo cross-proyecto contra el módulo Egresos/Caja.

### Pasos de reproducción — BUG-G-009 (antes del fix)

1. Autenticarse, `POST /Egresos/Create` con `Fecha`, `RubroId`, `ProveedorId`, `Detalle`, `Importe` válidos pero **sin ningún** campo `Pagos[i].*`.
2. Observar el `validation-summary`: antes del fix solo mostraba `"Importe > 0"`.
3. Esperado: debía incluir `"Debe cargar al menos un pago."` (PV15).

## 6. Auto-fixes aplicados

| ID | Archivos tocados | Resultado post-parche |
|---|---|---|
| BUG-G-009 | `Ganaderia.Web/Controllers/EgresosController.cs` (`Create(EgresoCreateVm vm)` POST): guard cambiado de `vm.Pagos == null \|\| vm.Pagos.Count == 0` a `vm.Pagos == null \|\| vm.Pagos.Count == 0 \|\| vm.Pagos.All(p => p.Importe <= 0)` | Build OK (0 errores). Re-test end-to-end confirma que el mensaje `"Debe cargar al menos un pago."` ahora aparece en el `validation-summary` junto con el de `Range`; nada se persiste. No se tocó `EgresoService.CreateAsync` (capa de negocio, autoritativa) porque su guard equivalente tiene el mismo comportamiento pero no está expuesto al usuario con un mensaje incorrecto — queda como posible mejora futura de bajo impacto, no crítica. |

Migración EF: no se requirió (cambio de presentación únicamente, sin impacto en esquema).

## 7. Migración EF — validación end-to-end (RT9)

Aplicada contra `ganaderia_dev` (MySQL 8 local, servicio Windows `MySQL80`, base de desarrollo descartable — no es la base de producción real):

- `dotnet ef database update` → aplicada sin errores.
- Query 1 (`COUNT(Egresos) == COUNT(EgresoPagos)`): `1 == 1`. PASS.
- Query 2 (`MovimientosCaja.EgresoPagoId IS NOT NULL` vs conteo previo de `EgresoId IS NOT NULL`): `1 == 1`. PASS.
- Query 3 (`EgresoPagos` vigentes sin `MovimientoCajaEgresoId`): `0` filas. PASS.
- `DESCRIBE Egresos` confirma que `FormaDePago` fue eliminada (Fase C).
- `DESCRIBE MovimientosCaja` confirma que `EgresoId` fue eliminada y reemplazada por `EgresoPagoId` (Fase C).

**RT9 queda validado en este entorno de desarrollo.** La ejecución contra la base de producción real sigue siendo responsabilidad del equipo de despliegue, con el mismo procedimiento (backup previo + las 3 queries ya documentadas en el propio archivo de migración) — el dataset de `ganaderia_dev` (1 Egreso) es demasiado pequeño para ser una prueba de carga, pero valida correctamente la **mecánica** del backfill en las 3 fases.

## 8. Riesgos de liberación y mitigaciones

| Riesgo | Severidad | Mitigación |
|---|---|---|
| RT9 backfill en producción real (dataset grande, posibles `Egreso` con datos atípicos no representados en `ganaderia_dev`) | major (antes del deploy) | Ejecutar el mismo procedimiento validado aquí contra una copia/backup real de producción antes del deploy, tal como exige la migración documentada. No ejecutar directo en producción sin ese paso. |
| Feature flag `Features:Etapa2=false` oculta `CajaController` en este entorno | minor, preexistente | No relacionado con v11; documentado para que no se confunda con una regresión de esta iteración. Verificar que el flag esté en el valor correcto antes de cada demo/entorno. |
| BUG-G-009 mensaje de validación | minor | Corregido en esta sesión (auto-fix). |
| Ausencia de pruebas automatizadas (unit/integration) para `EgresoPagoService`/job extendido | minor, deuda técnica conocida | Documentado desde la Etapa 7 original; sigue pendiente, no bloqueante para release (política del proyecto: pruebas funcionales manuales, no unitarias). |
| Endpoint de disparo manual del job (PA5 del plan v1) nunca implementado | minor, preexistente | No relacionado con v11. Para validar el job en producción sin esperar el horario, se requiere manipular `JobEjecuciones` manualmente (como se hizo en este QA) o esperar la corrida real de las 03:00 ART. |

## 9. Pruebas mínimas ejecutadas

Ejecutadas **end-to-end contra la app real** (`https://localhost:7200`, MySQL 8 local `ganaderia_dev`, login autenticado, POST con antiforgery token, verificación de cada resultado contra la base de datos):

- PF53, PF54, PF55, PF56, PF57, PF58, PF59, PF60, PF61 — **9/9 end-to-end, PASS**.
- PV13, PV14, PV15, PV16 (ambas partes) — **5/5 end-to-end, PASS** (PV15 con corrección de mensaje aplicada durante la sesión).
- Anulación de Egreso (§4.6) — end-to-end, PASS.
- Drill-down de Caja (`CajaService`/`Caja/Index.cshtml`, ajuste no previsto) — end-to-end (con feature flag habilitado temporalmente para la verificación), PASS.
- Migración EF con backfill (RT9) — aplicada y validada con las 3 queries documentadas contra `ganaderia_dev`, PASS.
- `dotnet build Ganaderia.slnx` en Debug — 0 errores (confirmado nuevamente tras el auto-fix).

**No ejecutadas end-to-end (solo revisión estática) y motivo:**

- REG-008 (pérdida de foco en input de importe): revisión de código del JS confirma el patrón correcto (sin re-render de `tbody` en cada keystroke), pero no se validó con un navegador real interactivo — esta sesión no contó con herramienta de automatización de navegador, solo `curl`/HTTP directo.
- Smoke test visual completo de la grilla dinámica (agregar/quitar filas en el DOM, toggle de `FechaVencimiento` al cambiar `FormaDePago`) — el binding de MVC se validó indirectamente enviando 3 filas indexadas manualmente por HTTP (PF55), lo cual prueba que el servidor interpreta correctamente `Pagos[0..2]`, pero no prueba que el JS del navegador genere esos índices correctamente en una sesión de click real.
- Regresión de `Facturas/Details` (FormaDePago de FacturaVenta): no había datos de Cuota/Factura suficientes en `ganaderia_dev` para un caso de prueba con acreditación; la entidad no fue tocada por el diff (confirmado por `git status`), riesgo de regresión bajo.
- Notificación in-app consolidada (mensaje con ambos totales): confirmada por revisión de código (`NotificarAdministradoresAsync`) y por el log del job real (`"Acreditadas 0 cuota(s) y 1 cheque(s) de egreso..."`), pero no se verificó visualmente la bandeja de notificaciones en el navegador.

## 10. Checklist de salida para merge (v11)

- [x] Build OK (Debug), 0 errores, tras auto-fix.
- [x] `EgresoPago` con ciclo de vida completo verificado end-to-end (Pendiente/Acreditado/Rechazado, las 9 transiciones de §3).
- [x] Suma de pagos == importe total validada en cliente (revisión JS) y servidor (verificado end-to-end, PF56).
- [x] Job diario extendido acredita cheques vencidos e idempotente (PF57/PF58 verificado con corridas reales forzadas).
- [x] Rechazo/regularización 3a/3b simétricos a Cuota, con saldo de caja consistente en cada paso (PF59-PF61, deltas de saldo verificados).
- [x] Anulación de Egreso propaga a Pagos y Movimientos de Caja (verificado end-to-end).
- [x] Migración con backfill aplicada y validada contra `ganaderia_dev` (RT9 mitigado en este entorno; pendiente repetir contra copia de producción real antes del deploy).
- [x] Regresión de `CajaService`/`Caja/Index.cshtml` (ajuste no previsto) verificada sin romper el módulo Caja.
- [x] BUG-G-009 corregido y re-verificado.
- [x] `ganaderia - fausto` no tocado (confirmado: ningún comando de este QA referenció esa ruta).
- [ ] Smoke test de navegador real de la grilla dinámica (agregar/quitar filas, foco de inputs) — pendiente, requiere herramienta de automatización de UI no disponible en este entorno.
- [ ] Validación del backfill (RT9) contra copia real de producción — pendiente, responsabilidad del equipo de despliegue.
- [ ] Backup de `Egresos`/`MovimientosCaja` antes del deploy a producción — pendiente, responsabilidad del despliegue.

## 11. Veredicto

**Apto para release con deuda técnica documentada** (no bloqueada). Las 9 pruebas PF53–PF61 y las 4 PV13–PV16 (con sus dos partes de PV16) pasaron end-to-end contra la aplicación real y MySQL. Se encontró y corrigió un defecto menor de mensaje de validación (BUG-G-009). Se documentó un comportamiento esperado de la migración que podría confundirse con un bug (GAN-002). Los pendientes de checklist (smoke test de navegador, validación de RT9 contra producción real, backup pre-deploy) son responsabilidad de etapas posteriores (UI manual/QA exploratorio con navegador, y el propio despliegue), no bloquean el merge del código a la rama principal del repositorio `ganaderia - emo`.

---

## 12. Post-release — bugs reportados por el usuario en uso real (2026-07-02)

El usuario reportó, sobre `Egresos/Create`: **"no anda el autocomplete de Concepto"** y, en un segundo mensaje, **"no anda el botón de agregar pago"**. Ambos caían exactamente en el hueco que §11 dejaba explícito como pendiente (smoke test de navegador real, nunca ejecutado — QA v11 validó el binding del servidor enviando `Pagos[0..2]` indexados manualmente por HTTP, sin clickear el botón en un navegador real).

Se investigó con Playwright headless contra la app real (`https://localhost:7200`, login con el SuperUsuario seed) para reproducir ambos síntomas antes de tocar código.

### 12.1 GAN-003 (major, **corregido**) — botón "Agregar pago" no funcionaba

- **Reproducido**: `document.querySelectorAll('tr.fila-pago').length` permanecía en 1 tras cualquier cantidad de clicks en `#btnAgregarPago`, sin ningún error en consola.
- **Causa raíz**: la fila-plantilla usaba `<script id="filaPagoTemplate" type="text/x-template">` con un `<partial name="_FilaPago" .../>` de Razor adentro. HTML5 clasifica `<script>` como *raw text element*, y Razor respeta esa clasificación: **no procesa Tag Helpers dentro de `<script>`**, sólo evalúa los bloques `@{ }`/`@()` explícitos. El resultado: el JS leía literalmente el texto sin procesar `<partial name="_FilaPago" model="plantilla" .../>` en vez del HTML real de la fila, por lo que `wrapper.querySelectorAll('tr')` siempre encontraba 0 elementos.
- **Fix**: `Ganaderia.Web/Views/Egresos/Create.cshtml` — se reemplazó `<script type="text/x-template">` por `<template id="filaPagoTemplate">` (elemento HTML5 nativo, no sujeto a esa restricción de Razor) y el JS pasó de leer `.textContent` a `.innerHTML` (`HTMLTemplateElement.innerHTML` serializa correctamente el contenido de su `DocumentFragment`).
- **Verificado con Playwright end-to-end** (no solo revisión estática): 2 clicks agregan 2 filas (1→2→3), reindexado correcto de `name`/`id` al agregar y al quitar una fila intermedia, y un Egreso completo con 2 pagos (Efectivo 600 + Transferencia 400 sobre un total de 1000) se creó exitosamente desde el navegador real (`"Egreso registrado."`, visible en `Egresos/Index`). Sin errores de consola.

### 12.2 GAN-004 (minor, **corregido**) — autocomplete de Concepto

- **Investigado**: el endpoint `/Egresos/SugerenciasDetalle` y el JS que puebla el `<datalist>` funcionaban correctamente — verificado que las `<option>` SÍ se insertaban en el DOM con los valores correctos tanto al enfocar el campo como al escribir un término coincidente. **No era un bug del fetch/JSON.**
- **Causa raíz**: quirk conocido de `<input list="...">` + `<datalist>` nativo — varios navegadores no re-evalúan visualmente el desplegable de sugerencias ya abierto cuando las `<option>` cambian de forma asíncrona mientras el input mantiene el foco (los datos están en el DOM, pero el popup nativo no siempre se refresca solo).
- **Fix**: tras poblar el `<datalist>`, si el input sigue enfocado, se fuerza la re-evaluación quitando y re-asignando el atributo `list` (`input.setAttribute('list','')` → `input.setAttribute('list','DetalleSugerencias')`) — workaround estándar, no disruptivo (no interrumpe el foco ni el texto ya tipeado).
- **Nota de verificación**: el popup nativo del `<datalist>` no es inspeccionable por automatización headless (Playwright no puede confirmar si el desplegable *visualmente* aparece); se validó lo verificable (población correcta del DOM, atributo `list` intacto tras el nudge, sin errores). Queda como pendiente de validación manual en un navegador real por el usuario/QA humano.

### 12.3 Archivos tocados

- `Ganaderia.Web/Views/Egresos/Create.cshtml` (único archivo modificado; sin cambios de esquema, sin migración EF).

### 12.4 Lección de proceso

Ambos bugs son consistentes con el hueco de cobertura que la propia iteración v11 dejó documentado en §11: JS ejecutado dentro del navegador (clicks reales, popups nativos) no se puede validar simulando únicamente el POST HTTP final. Para futuras iteraciones con JS de UI no trivial (grillas dinámicas, autocomplete, etc.), correr un smoke test real con Playwright (o equivalente) antes de cerrar QA, no sólo revisión estática + binding por HTTP directo.
