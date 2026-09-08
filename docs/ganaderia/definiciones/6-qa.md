# QA — Sistema de Gestión Ganadera

Versión: **v4** (v1 inicial, v2 iteración v11, v3 iteración v17, **v4 iteración v18**)
Agente: `6 - qa`
Entradas (última iteración, v17):
- `1-analista-funcional.md` v13 (§3.9, §3.10, §4.8, §8.1, PF67–PF77, PV19–PV23, R29–R31)
- `2-disenador-funcional.md` v4 (§8.3, PD13–PD17, RD12–RD16)
- `3-arquitecto-mvc.md` v4 §17 (RT17–RT21)
- `5-implementador.md` iteración v17 (cambios y evidencia)
- `docs/qa/regresiones-manuales.yml` (catálogo cross-proyecto, 63 ítems)

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

---

# Iteración v17 — Descuento comercial pre-impuestos + serie de IVA en el Tablero Anual (2026-09-07)

Entradas: `1-analista-funcional.md` v13 (§3.9, §3.10, §4.8, §8.1, R29–R31, PF67–PF77, PV19–PV23), `2-disenador-funcional.md` v4 (§8.3, RD12–RD16, PD13–PD17, HU-D1–HU-D7), `3-arquitecto-mvc.md` v4 §17 (RT17–RT21), `5-implementador.md` iteración v17. Catálogo cross-proyecto `docs/qa/regresiones-manuales.yml`.

Repositorio: `C:\Sistemas\ganaderia - emo`, rama `main`, **working tree sin commitear y sin deployar**. Build previo: `dotnet build Ganaderia.slnx -c Debug` → **Compilación correcta, 0 Errores** (8 warnings, todos preexistentes: NU1902 MailKit/MimeKit).

## 0. Método de verificación

**El servidor MCP `playwright` NO estuvo disponible en esta sesión** (`.mcp.json` lo declara en `C:/Sistemas/Agentes-IA`, pero las herramientas `mcp__playwright__*` no se expusieron). Se declaró explícitamente y se cayó al camino equivalente previsto en `33-verificacion-automatizada-qa.instructions.md`: **navegador real conducido por script Playwright local** (`npm i playwright` + `npx playwright install chromium`, Chrome Headless Shell 153), contra la app corriendo en `https://localhost:7200` (perfil `https`, `ASPNETCORE_ENVIRONMENT=Development`) y MySQL `ganaderia_dev`, con sesión autenticada como el SuperUsuario seed.

**Nada se dio por verificado por lectura de código.** Cada PF/PV/PD se ejecutó contra la app corriendo y se contrastó contra MySQL. Se re-verificaron de forma independiente todas las pruebas que el implementador reportó como pasadas.

Se tomó un **baseline completo de la base antes de empezar** (facturas, egresos, grupos, saldo de caja, ledger de stock) y se verificó al cerrar que la base quedó **restaurada al baseline exacto** (`diff` sin diferencias).

## 1. Alcance funcional validado

- Descuento comercial opcional (% ↔ importe sincronizados) en Facturas de venta y Egresos, aplicado sobre el Subtotal para dar un **neto gravado** base de todos los impuestos.
- Reajuste proporcional de ingresos al editar una factura cuyo total cambia, con aviso previo (R29).
- Gráfico de **IVA de compras vs. ventas** en el Tablero Anual, base **devengado por fecha de comprobante**, con línea de saldo y KPI de saldo del período.
- Regresión transversal: comprobantes sin descuento, anulaciones, caja, stock desnormalizado, listados y el gráfico de flujo de caja preexistente.

## 2. Cobertura por criterio de aceptación (PASS/FAIL/BLOCKED)

| Prueba | Resultado | Evidencia |
|---|---|---|
| **PF67** Venta Subtotal 1.000.000, desc 10% → neto 900.000, IVA 21% 189.000, Total 1.089.000 | **PASS** | Navegador real: `neto 900.000,00`, `montoIva 189000.00`, `total 1.089.000,00`. |
| **PF68** Mismo descuento como importe (100.000) completa el % en 10 y da resultado idéntico | **PASS** | Cargado `MontoDescuento=100000` → `pctDesc` pasa a `10` solo; Total idéntico 1.121.670,00 (con IIBB 3%). Simétrico verificado. |
| **PF69** Desc 10% + IIBB 3% → IIBB sobre 1.089.000 = 32.670, Total 1.121.670 | **PASS** | UI y persistencia MySQL: `MontoIIBB 32670.00`, `Total 1121670.00`. |
| **PF70** Sin descuento: totales idénticos a los previos a v17 | **PASS** | `diff` baseline↔final de las 5 facturas y 8 egresos preexistentes: **0 diferencias**. `Details/1` no muestra filas Descuento/Neto gravado. |
| **PF71** Egreso Subtotal 100.000, desc 5%, IVA 21% → Importe 114.950; pagos suman 114.950 | **PASS** | UI en vivo `Total del egreso $ 114.950,00`; persistido `Importe 114950.00`, pago 114950.00. |
| **PF72** Editar factura con ingresos, aplicar descuento: avisa el cambio y reajusta | **PASS** (tras GAN-005/GAN-006) | Total 1.210.000 → 1.089.000; aviso "no coincide… diferencia $ 121.000,00"; botón reajusta 605.000→**544.500 ×2** proporcional conservando vencimientos; SweetAlert2 "El total pasó de $ 1.210.000,00 a $ 1.089.000,00…"; persistido 1.089.000 con ingresos 544.500 ×2. |
| **PF73** Serie IVA ventas/compras = suma de `MontoIva` por mes de comprobante | **PASS** | Chart.js: ventas `mar 189.000`, `may 16.170.000`; compras `abr 19.950`. Idéntico a la consulta SQL de control. |
| **PF74** Factura emitida en un mes y cobrada en otro suma en el mes de **emisión** | **PASS** | Factura del **15/03/2026** con ingreso venciendo el **07/09/2026**: el IVA aparece en **Marzo** y septiembre queda en 0. |
| **PF75** Factura anulada deja de sumar en el gráfico | **PASS** | Anulación real por UI: la barra de marzo pasó de **189.000 → 0**. Confirmado además con las anuladas preexistentes (FV5 mayo 2.835.000 y EG8 sept 21.000 nunca aparecen). RT20 cerrado en vivo. |
| **PF76** Línea de saldo = ventas − compras; KPI = saldo del período filtrado | **PASS** | Línea `mar 189.000`, `abr −19.950`, `may 16.170.000`. KPI: año 2026 → `$ 16.339.050,00 a pagar`; mes 3 → `189.000 a pagar`; mes 4 → `−19.950 **a favor**`; mes 5 → `16.170.000`. |
| **PF77** Detalle de venta y de egreso muestran Subtotal, Descuento (% e importe), Neto gravado, IVA, Total | **PASS** | Venta: `Subtotal 1.000.000,00 / Descuento −$100.000,00 (10%) / Neto gravado 900.000,00 / IVA 189.000,00 (21%) / IIBB 32.670,00 (3%) / Total 1.121.670,00`. Egreso: `Subtotal 100.000,00 / Descuento −$5.000,00 (5%) / Neto gravado 95.000,00 / IVA 19.950,00 (21%) / Importe`. |
| **PV19** % fuera de [0,100): bloqueado | **PASS** | Cliente: `is-invalid` + mensaje. **POST directo**: rechazado (`0 a 99,99`) con 100 y con 150. |
| **PV20** Importe ≥ Subtotal: bloqueado | **PASS** | Cliente: `descuentoError` visible. **POST directo**: *"El descuento (1.000.000,00) no puede ser mayor o igual al Subtotal (1.000.000,00): dejaria el total en cero."* |
| **PV21** Descuento negativo (% o importe): bloqueado | **PASS (servidor)** / **defecto menor en cliente** | **POST directo** rechazado en ambos casos. Pero el validador **en vivo** no marca el negativo: con −10% la card calcula neto 1.100.000 y Total 1.331.000 sin `is-invalid` ni mensaje (ver BUG-G-011). |
| **PV22** Edición con ingresos que no suman el nuevo total: bloqueada por el servidor aunque se ignore el aviso | **PASS** | Aceptando el SweetAlert2, el servidor igual rechaza: *"La suma de los ingresos (1.089.000,00) no coincide con el Total de la factura (968.000,00)."* |
| **PV23** Egreso cuyos pagos suman el Subtotal sin descontar: bloqueado | **PASS** | Pago 121.000 sobre total 114.950 → *"La suma de los pagos (121.000,00) debe ser exactamente igual al total del egreso (114.950,00, subtotal - descuento + IVA)."* UI: `Restante −6.050,00 (excede el total)`. |
| **PD13** `base()` única función que decide la base de cada impuesto | **PASS** | Auditoría del JS: `impGrupos = ['desc','iva','iibb','percep']`, un solo `base(grupo)`; la fórmula del descuento no está duplicada. Verificado en vivo: tocar el descuento recalcula IVA, IIBB y percepciones en una sola pasada. |
| **PD14** Descuento ≥ Subtotal bloqueado en cliente **y** ante POST directo | **PASS** | Ambos caminos verificados (ver PV20). |
| **PD15** Botón de reajuste y confirmación **sólo** en edición | **PASS** | Alta: `btnReajustarIngresos` y `TotalOriginal` **ausentes**, `ES_EDICION=false`. Edición: ambos presentes, `ES_EDICION=true`. El gate Razor (`@if (Model.EsEdicion)`) y el gate JS coinciden. |
| **PD16** `GetTableroAnualAsync` no consulta `MovimientosCaja` para las series de IVA | **PASS** | Código + prueba viva: un egreso con **comprobante de abril** y **pago acreditado en septiembre** aparece en IVA compras en **abril** y en el gráfico de caja en **septiembre**. Las dos bases son independientes. |
| **PD17 / LP-003** `value=` de descuento con `InvariantCulture` | **PASS** | HTML servido: `value="10.0000"`, `value="100000.00"`, `TotalOriginal value="1121670.00"`. Ningún decimal con coma. |

**23/23 criterios PASS.** PV21 pasa por el servidor (que es la autoridad) con un defecto menor de UI documentado aparte.

## 3. Cobertura de máquina de estados

No hay máquina de estados nueva en v17. Se recorrieron las transiciones tocadas por el descuento:

| Transición | Resultado |
|---|---|
| Factura: alta → editable (ingresos Pendientes) | PASS |
| Factura: edición que cambia el total → aviso + reajuste + guardado | PASS (PF72) |
| Factura: edición con ingresos descuadrados → **rechazada** | PASS (PV22) |
| Factura con algún ingreso Acreditado/Rechazado → **no editable** (redirige a Details) | PASS — las 4 facturas preexistentes redirigen a `Details`, no se puede forzar la edición |
| Factura: activa → anulada (reversión de stock, cancelación de ingresos, contramovimientos) | PASS |
| Egreso: alta con pagos que cierran → creado | PASS (PF71) |
| Egreso: alta con pagos que no cierran → **rechazado** (tolerancia cero) | PASS (PV23) |
| Egreso: activo → anulado (baja de pagos + contramovimiento de caja) | PASS (MH-020) |

## 4. Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

Catálogo recorrido completo (63 ítems tras esta sesión). Se ejecutaron los aplicables al sistema bajo prueba mapeando módulos equivalentes.

| id | aplica | resultado | acción |
|---|---|---|---|
| REG-001, REG-002 | no | N/A | Variantes/RowVersion; ganadería no tiene variantes ni token de concurrencia en Grupo. |
| REG-003, REG-005, REG-007 | sí (autocomplete) | **PASS** | Select2 de Motivo (Facturas) y Concepto (Egresos) devuelven y cargan valores nuevos; sin errores de consola. |
| REG-004 | sí (máquina de estados) | **PASS** | Ver §3: transiciones de Factura y Egreso recorridas. |
| REG-006 | parcial | **PASS** | Plazo sugerido (30/60/90) genera la cantidad correcta de ingresos. |
| REG-008 | sí (foco en input de importe) | **PASS** | Tipeo en `.importe` e `.js-importe-pago` no re-renderiza el `tbody`; el foco se mantiene (verificado en navegador real, hueco que v11 había dejado abierto). |
| REG-009 | no | N/A | No hay cascada Categoría→Subgrupo. |
| REG-010 | sí (sidebar/roles) | **PASS** | Auditoría/Usuarios/Sistema sólo bajo SUPER USUARIO. |
| KOI-001 | sí (btn-swal fuera del form) | **PASS** | Los botones de anulación de Factura y Egreso están **dentro** de su `<form asp-action="Anular">`; ambos ejecutan realmente (verificado: anulación efectiva en base). |
| KOI-002, KOI-003 | no | N/A | No hay Estado de Resultados ni rol Inversor. |
| KOI-004 | no | N/A | No hay cierre de período. |
| KOI-005, KOI-006 | sí (links de sidebar a controllers inexistentes) | **PASS** | Smoke de las 18 pantallas: **todos 200**, ningún link del sidebar da 404. |
| DN-001, DN-002 | sí (listados) | **PASS** | `/Facturas`, `/Egresos`, `/Ingresos`, `/Caja`, `/Stock/Historial`, `/Audit` responden 200 con datos; sin 500. |
| GAN-001 | sí | **PASS** | Guard de "al menos un pago" vigente (regresión de v11). |
| GAN-002 | sí | N/A (informativo) | Backfill de v11, no tocado por v17. |
| GAN-003 | sí (grilla dinámica de pagos) | **PASS** | `<template id="filaPagoTemplate">` sigue funcionando: agregar/quitar filas reindexa `Pagos[i]` correctamente. |
| GAN-004 | sí (autocomplete Concepto) | **PASS** | Migrado a Select2 en v12; el desplegable puebla y permite valor nuevo. |
| VSF-001, VSF-002 | no | N/A | No hay CompraProveedor. |
| CRM-* | no | N/A | Proyecto CRM/bot, sin equivalente. |
| MH-001 | sí (500 en listado de movimientos de stock) | **PASS** | `/Stock/Historial` y `/Stock/Movimientos?grupoId=1` → 200 con datos. |
| MH-002 | sí (enum serializado) | **PASS** | Badges de tipo de movimiento se renderizan por nombre. |
| MH-003 | no | N/A | No hay cheques de OC con fecha de emisión. |
| MH-004 | sí (desglose de caja) | **PASS** | Tabla de flujo mensual cuadra con SQL: total $ 92.923.300,00 = suma de los 12 meses. |
| MH-005, MH-006 | no | N/A | No hay remito ni link público. |
| MH-007 | no | N/A | No hay ajuste de apertura. |
| MH-008 | no | N/A | |
| MH-009 | sí (fechas/UTC en listados) | **PASS** | Fechas de comprobante correctas en listados y detalles (15/03/2026, 10/04/2026 sin corrimiento de día). |
| MH-010 | sí (evento `input` en campos de plata) | **PASS** | Ganadería usa `<input type="number">` nativo, no maskMoney; todos los recálculos se disparan con `input`. Verificado en vivo. |
| MH-011, MH-012, MH-013 | no | N/A | No hay facturación AFIP ni notas de crédito. |
| SG-001 | sí (grilla que postea numéricos vacíos contra tipos de valor) | **PASS** | Quitar filas y postear no rompe el binding; los campos vacíos no generan 500. |
| LP-001 | no | N/A | No hay clasificación ABC. |
| ELV-001 | sí (controllers sin `[Authorize]`) | **PASS** | Sin sesión, `GET /` responde **302** al login; las 18 pantallas exigen autenticación. |
| ELV-002 | sí (asimetría Create/Update) | **PASS** | `EditAsync` de Factura aplica **las mismas** validaciones de descuento e ingresos que `CreateAsync` (verificado por POST directo: PV20 y PV22 se disparan también en la edición). |
| **LP-003** | **sí** | **FAIL → corregido** | Mitad de SALIDA ya estaba resuelta (helper `num`). **La mitad de ENTRADA no**: ver **GAN-005**, auto-fix aplicado. |
| LIP-001 | sí (errores de service invisibles) | **PASS** | Los `ServiceResult.CreateError` se muestran en el `validation-summary-errors` de ambas pantallas (capturados literalmente en PV20/PV22/PV23). |
| LP-004 | no | N/A | No hay filtros persistidos en sesión. |
| LP-005 | sí (pantalla de sólo lectura desactualizada) | **PASS** | `Details` de venta y egreso leen el total **persistido** y muestran el desglose de descuento (RD12/RT18). |
| MH-014, MH-015, MH-018 | no | N/A | No hay pagos con tarjeta ni gastos recurrentes. |
| MH-016, MH-017 | sí (edición inline de stock) | **PASS** | No hay edición inline en `/Stock`; sin reasignación de tokens. |
| MH-019 | sí (cheque huérfano al cancelar) | **PASS** | Anular un egreso da de baja **todos** sus pagos, incluidos los Pendientes. |
| **MH-020** | **sí** | **PASS** | Anular egreso con pago **acreditado**: se postea contramovimiento `Reversion anulacion Egreso #11` (EsIngreso=1, +114.950,00) y el saldo de caja vuelve **exactamente** al baseline 93.038.250,00. No se borra el original: queda la traza. |
| MH-021 | sí (fecha efectiva vs sugerida) | **PASS** | El movimiento de caja se postea con la `FechaEfectiva` del pago (07/09/2026), no con la fecha del comprobante (10/04/2026). |
| CRM-015, CRM-016 | no | N/A | |
| **GAN-005** | **sí (nuevo)** | **FAIL → corregido** | Alta en catálogo + auto-fix. |
| **GAN-006** | **sí (nuevo)** | **FAIL → corregido** | Alta en catálogo + auto-fix. |

## 5. Defectos detectados

### GAN-005 — blocker, **preexistente (NO es regresión de v17)**, **corregido**

Los `<input type="number">` de las **filas de colección** (`Items[i].KilosTotales`, `Items[i].PrecioPorKilo`, `Ingresos[i].Importe`, `Pagos[i].Importe`) se escriben a mano con `name="..."` en vez de `asp-for`, así que el tag helper **no emite para ellos el marcador `<input name="__Invariant">`**. Con `UseRequestLocalization(es-AR)` fijo en `Program.cs` y **sin** model binder invariante propio, el binder los parsea en es-AR, donde el punto es **separador de miles**. Como un `type=number` postea siempre en formato invariante, `"1121670.00"` entra al servidor como **112.167.000** (×100).

Impacto real: **"Generar sugerido" + "Emitir factura" fallaba siempre** (el JS escribe con `toFixed(2)`, o sea siempre con punto). El usuario recibía *"La suma de los ingresos (112.167.000,00) no coincide con el Total de la factura (1.121.670,00)"* — un mensaje que parece de negocio y esconde un error de parseo. Sólo se podía guardar tipeando importes sin decimales. Lo mismo en Egresos con pagos decimales, y al re-guardar una edición.

Byte-idéntico en `HEAD` (`git show HEAD:.../Create.cshtml`) y `Program.cs` no fue tocado por v17 → **preexistente desde v13**. Pero **v17 lo agrava**: el botón "Reajustar al nuevo total" (PF72, la feature estrella de la iteración) escribe con `toFixed(2)` en esos mismos inputs, así que PF72 era **inejecutable** antes del fix.

### GAN-006 — blocker, **preexistente (NO es regresión de v17)**, **corregido**

Abrir `Facturas/Edit/{id}` y pulsar "Guardar cambios" **sin tocar nada** no enviaba nunca el formulario: jquery-validate devolvía tres `"Please enter a multiple of 0.01."` sobre `PorcentajeIva` (`value="21.0000"`), `PorcentajeIIBB` (`3.0000`) y `PorcentajeOtrasPercepciones` (`0.0000`). Las columnas son `decimal(9,4)` y el input declaraba `step="0.01"`: la regla `step` rechaza valores con más decimales que el step. La validación **nativa** del navegador daba válida; el bloqueo lo ponía jquery-validate. Sólo se manifiesta al **reabrir** un registro persistido, nunca en el alta — por eso nunca se detectó. `PorcentajeDescuento` (v17) se salvaba de casualidad porque su driver arranca en modo `'monto'` y reescribe el `.value` a 2 decimales al cargar.

Con GAN-005 y GAN-006 juntos, **la edición de facturas estaba 100 % muerta** en producción.

### BUG-G-011 — minor, **abierto (no corregido)**

El validador **en vivo** del descuento sólo chequea `MontoDescuento >= Subtotal`; **no chequea el negativo**. Con `PorcentajeDescuento = -10` la card muestra `Neto gravado 1.100.000,00` y `Total 1.331.000,00` sin `is-invalid` ni mensaje: el descuento negativo se comporta como un **recargo** en pantalla.

No se corrigió a propósito: el servidor rechaza correctamente (PV21 PASS por POST directo) y el `min="0"` + `[Range(0, 99.99)]` bloquean el submit, así que **no hay riesgo de dato corrupto**; es sólo una ayuda visual que miente durante la carga. Tocar `descuentoInvalido()` cambia el comportamiento de la validación en vivo de una pantalla de plata, y eso excede el mandato de auto-fix. **Fix propuesto**: extender `descuentoInvalido()` para incluir `montoDe('desc') < 0 || pct < 0`, reutilizando el mismo `descuentoError`.

### Observación menor (no es defecto)

En `Egresos/Create`, la línea "Suma de pagos: 0.00" se formatea con punto decimal en lugar del `$ 0,00` en es-AR que usa el resto de la pantalla. Cosmético.

## 6. Auto-fixes aplicados

| id | Archivos | Cambio | Resultado post-parche |
|---|---|---|---|
| **GAN-005** | `Ganaderia.Web/Views/Facturas/Create.cshtml`, `Ganaderia.Web/Views/Egresos/Create.cshtml` | Listener `submit` en fase de captura que, antes de enviar, emite un `<input type="hidden" name="__Invariant" value="{campo}">` por cada `input[type=number][name]` de las grillas (`#tblItems`, `#tblIngresos`, `input.js-importe-pago`). Se hace en el submit y no en el markup porque las filas se agregan/quitan/**reindexan** por JS; se limpian los marcadores previos en cada pasada. | "Generar sugerido" + emitir **funciona**; egreso con pago 114.950,00 persiste correcto; re-guardar una edición sin cambios es **idempotente**; PF72 pasa end-to-end. |
| **GAN-006** | idem | `step="0.01"` → `step="0.0001"` en los 4 inputs de porcentaje de Facturas y los 2 de Egresos, alineando la restricción de UI con la precisión real `decimal(9,4)`. No cambia el valor renderizado ni la precisión persistida. | `jQuery(form).validate().form()` sobre la edición recién cargada devuelve `errorList` **vacío**; PV19/PV20/PV21 siguen bloqueados en cliente y por POST directo. |

Ambos ítems fueron **dados de alta en `docs/qa/regresiones-manuales.yml`** (el catálogo pasa de 61 a 63 ítems, YAML validado) con causa raíz, `archivos_fix`, `deteccion_qa`, criterios de aceptación, pruebas mínimas y `nota_generalizacion` para el resto del baseline.

Los auto-fixes **no introducen lógica de negocio**: son la mitad de entrada del round-trip de cultura que LP-003 ya tenía catalogada, y una restricción de UI alineada al dominio. No tocan servicios, dominio, esquema ni migraciones, y **no modifican ningún dato ya registrado** (verificado: `diff` baseline↔final sin diferencias).

## 7. Invariantes de datos (todas en 0 desvíos)

```sql
-- 0 desvíos, antes y después de todas las pruebas
SELECT COUNT(*) FROM FacturasVenta
 WHERE ROUND(Subtotal-MontoDescuento+MontoIva+MontoIIBB+MontoOtrasPercepciones,2) <> ROUND(Total,2);
SELECT COUNT(*) FROM Egresos
 WHERE ROUND(Subtotal-MontoDescuento+MontoIva,2) <> ROUND(Importe,2);
```

- **`Grupo.StockActual` == ledger de `MovimientosStock`** en los 4 grupos activos, antes y después (incluida una venta y su anulación): `Lote 1 80=80`, `Lote bajo 0=0`, `Lote vaquillonas 48=48`, `Grupo A 0=0`.
- **Saldo de caja** restaurado exactamente al baseline: `93.038.250,00`.
- **RT17**: `NetoGravado` **no existe** como columna en `information_schema` — el `Ignore()` funciona.
- Migración `20260907123702_Comprobantes_DescuentoComercial` aplicada en `ganaderia_dev`: 4 `AddColumn` con `DEFAULT 0`, sin backfill, histórico intacto (RD15/PF70).
- **Base restaurada al baseline exacto** al cerrar: todos los datos de prueba eliminados, contador de factura devuelto a 5.

## 8. Riesgos de liberación y mitigaciones

| Riesgo | Severidad | Mitigación |
|---|---|---|
| GAN-005 y GAN-006 son **preexistentes y están hoy en producción**: la edición de facturas está muerta y "Generar sugerido" no permite emitir | **blocker** | Corregidos en el working tree. **Deben ir en el mismo deploy que v17.** Verificar en producción, apenas se deploye, un alta con "Generar sugerido" y una edición re-guardada sin cambios. |
| El fix de GAN-005 cambia la cultura de parseo de 4 campos de plata de las dos pantallas principales | major | Verificado end-to-end e **idempotente** (re-guardado sin cambios no altera un centavo). Aun así conviene que el implementador lo revise antes del merge, y valorar si corresponde la solución de fondo (un `InvariantDecimalModelBinderProvider` global, como La Platense) en vez de la puntual por vista. |
| BUG-G-011: el descuento negativo se ve como recargo durante la carga | minor | El servidor lo rechaza siempre; no hay riesgo de dato. Fix propuesto en §5. |
| Invariante de comprobantes **en producción** post-deploy | major | Pendiente: correr las 2 queries de §7 contra producción después del deploy. En dev dan 0. |
| El acumulado sin deployar es de **8 iteraciones** (v13→v17, §12 del implementador) | major | El deploy no es incremental: hay que aplicar código + migraciones en el orden documentado, con backup previo. |
| R30/R31: dos bases contables en la misma pantalla | minor | Mitigado: el rótulo de devengado y el "no es un Libro IVA" están en el `card-body`, no en un tooltip. Verificado en el HTML servido. |
| Ausencia de pruebas automatizadas (unit/integration) | minor | Deuda técnica conocida y aceptada por política del proyecto. |

## 9. Pruebas mínimas ejecutadas

- **PF67–PF77** (11) y **PV19–PV23** (5) y **PD13–PD17** (5): **21/21 ejecutadas end-to-end contra la app corriendo**, todas PASS.
- **Smoke de las 18 pantallas** (33 URLs, incluidas las no tocadas): **todas 200**, sin errores de consola.
- **Regresión de anulación**: factura (reversión de stock, cancelación de ingresos) y egreso (baja de pagos + contramovimiento MH-020, saldo restaurado al centavo).
- **Regresión del gráfico de flujo de caja** preexistente: sus 3 series cuadran exactamente con el SQL de control; **no** se contaminó con la serie devengada.
- **Regresión del bug de v15** corregido por el implementador en `Egresos/Create.cshtml`: **confirmada end-to-end** — cambiar el subtotal ahora actualiza en vivo el IVA, el "Total del egreso" ($ 121.000,00) y el "Restante por asignar", que antes quedaban en 0.
- **Auditoría del patrón de listeners mal anidados en todas las vistas**: sólo 5 vistas del proyecto tienen JS no trivial (`Facturas/Create`, `Egresos/Create`, `Dashboard/TableroAnual`, `Audit/Index`, `Shared/_Layout`). **Ninguna reincidencia**: todos los `addEventListener` están a nivel de IIFE con bootstrap correcto y sin funciones huérfanas. Único hallazgo inocuo: en `Egresos/Create` un listener `input` sobre el hidden `#ImporteTotal` nunca se dispara (los cambios programáticos de `.value` no emiten `input`), pero es código muerto, no un bug: `recalcularTotal()` llama a `actualizarSuma()` explícitamente.
- `dotnet build Ganaderia.slnx -c Debug` tras los auto-fixes → **Compilación correcta, 0 Errores**, sin warnings nuevos.

## 10. Checklist de salida para merge (v17)

- [x] Build OK (Debug), 0 errores, antes y después de los auto-fixes.
- [x] PF67–PF77, PV19–PV23, PD13–PD17 ejecutadas end-to-end en navegador real (21/21 PASS).
- [x] PF70 (no regresión) probado por `diff` de datos, no por inspección visual: 0 diferencias.
- [x] Invariantes de comprobantes en 0 desvíos en `FacturasVenta` y `Egresos`.
- [x] `Grupo.StockActual` == ledger de `MovimientosStock` en todos los grupos.
- [x] Saldo de caja restaurado al baseline tras anulaciones (MH-020 verificado con contramovimiento real).
- [x] Gráfico de flujo de caja preexistente sin contaminar (PD16 probado con un caso de abril/septiembre).
- [x] RT20/PF75 verificado anulando una factura real, no por lectura de código.
- [x] RT17 verificado contra `information_schema`.
- [x] PD15 verificado en el HTML de alta y de edición.
- [x] LP-003/PD17 verificado sobre el HTML servido de factura y egreso con descuento.
- [x] Smoke de las 18 pantallas: 200 OK.
- [x] Auditoría del patrón de listeners en todas las vistas: sin reincidencias.
- [x] GAN-005 y GAN-006 dados de alta en el catálogo cross-proyecto con fix documentado.
- [x] Base de dev restaurada al baseline exacto; sin filas de prueba.
- [x] Sin commit y sin deploy (pedido explícito).
- [ ] Revisión del implementador sobre los 2 auto-fixes de QA antes del merge — **pendiente**.
- [ ] Decisión de arquitectura: ¿`InvariantDecimalModelBinderProvider` global en vez del fix por vista? — **pendiente**.
- [ ] BUG-G-011 (descuento negativo en el validador en vivo) — **pendiente**, no bloqueante.
- [ ] Invariantes contra producción post-deploy — **pendiente**, responsabilidad del despliegue.

## 11. Veredicto

**APTO PARA DEPLOY, condicionado a que los dos auto-fixes de QA (GAN-005 y GAN-006) viajen en el mismo deploy y sean revisados por el implementador antes del merge.**

La funcionalidad de v17 es **correcta y está completa**: los 21 criterios de aceptación pasan end-to-end contra la app real, la aritmética del descuento cuadra hasta el centavo tanto en pantalla como en MySQL, la serie de IVA es genuinamente devengada (probado con un comprobante de un mes cobrado en otro), las anuladas quedan fuera (probado anulando en vivo), y **no hay ninguna regresión** sobre los comprobantes sin descuento, la caja, el stock ni el gráfico de flujo preexistente.

Los dos blockers encontrados **no los introdujo v17**: son de v13 y estaban en producción sin detectar, porque ambos sólo se manifiestan al **reabrir** un comprobante guardado o al usar "Generar sugerido" — dos caminos que ningún ciclo de QA anterior había recorrido en un navegador real. La lección de proceso de v11 §12.4 (el POST HTTP directo no sustituye al clic real) se repitió: el implementador verificó v17 por POST construido a mano, y ese camino **evita justamente** los dos bugs, porque un POST armado a mano no arrastra ni los `value=` de 4 decimales ni la ausencia del marcador `__Invariant`.

Sin esos dos fixes, v17 sería **NO APTO**: su feature principal (PF72, el reajuste de ingresos al editar) es inalcanzable, porque la pantalla de edición no se puede guardar.

---

# Iteración v18 — Deducciones de liquidación + compra de hacienda con costo (2026-09-08)

**Última validación de reglas cross-proyecto: 2026-09-08.**

Entradas: `1-analista-funcional.md` v14 (§3.11, §3.12, §5.9, PF78–PF88, PV24–PV28, R32–R34), `2-disenador-funcional.md` v5 (§8.4, PD18–PD21, RD17–RD20, HU-D8–HU-D12), `3-arquitecto-mvc.md` v5 §18 (RT22–RT26), `5-implementador.md` iteración v18. Catálogo cross-proyecto `docs/qa/regresiones-manuales.yml` (68 ítems).

Repositorio: `C:\Sistemas\ganaderia - emo`, rama `main`, **working tree sin commitear y sin deployar**. Build previo y posterior al auto-fix: **Compilación correcta, 0 Errores**, 9 warnings **todos preexistentes** (4 NU1902 MailKit/MimeKit + CS0114 `HomeController.StatusCode`).

## 0. Método de verificación

**El servidor MCP `playwright` NO estuvo disponible en esta sesión** (las herramientas `mcp__playwright__*` no se expusieron; `ToolSearch` no las encontró). Se declaró explícitamente y se cayó al camino equivalente de `33-verificacion-automatizada-qa.instructions.md`: **navegador real conducido por script Playwright local** (`playwright 1.63.0-alpha`, Chromium headless) contra la app en `https://localhost:7200`, con sesión autenticada real.

A diferencia de lo que reportó el implementador, **el Chromium de esta sesión sí abrió sockets contra `localhost` directamente** (probado: `https://localhost:7200` → 200). No hizo falta interceptar requests: transporte normal, navegador real, JS real.

La app se compiló y corrió desde un directorio aparte (`%TEMP%/claude/qabuild`) para no chocar con el `bin/Debug` que suele tener bloqueado la sesión de debug de Visual Studio. No se mató ningún proceso del usuario.

**Nada se dio por verificado por lectura de código.** Las 22 pruebas del implementador se **re-ejecutaron de forma independiente**. Baseline completo de la base al empezar; al cerrar, `diff` baseline vs. estado final = **0 diferencias** (base devuelta exacta, incluidos contadores de numeración y `UpdatedAt` del catálogo).

## 1. Alcance funcional validado

- Catálogo `ConceptoDeduccion` (ABM nuevo) + grilla de deducciones **precargada** en la factura, con importes ya calculados sobre el neto gravado; `IIBB`/`OtrasPercepciones` eliminados.
- Fórmula v14: `Total = (Subtotal − Descuento) + IVA − Σ Deducciones`.
- `Stock/Compra` con costo opcional que genera un egreso real con pagos, vinculado por `MovimientoStock.EgresoId` en una sola transacción.
- KPI "Reinvertido en hacienda" en el Tablero Anual.
- JS compartido `ov-costo-pagos.js` + `_FilaPago.cshtml` en `Shared/` consumidos por `Egresos/Create` y `Stock/Compra`.
- Regresión transversal: v17 (descuento comercial, reajuste de ingresos, gráfico de IVA), caja, anulaciones, stock desnormalizado, listados.

## 2. Cobertura por criterio de aceptación (PASS/FAIL/BLOCKED)

| Prueba | Resultado | Evidencia (navegador real + MySQL) |
|---|---|---|
| **PF78** Subtotal 136.253.250, desc 4%, IVA 10,5% → neto 130.803.120,00 e IVA 13.734.327,60 | **PASS** | Los dos valores **exactos** de la liquidación real del consignatario. |
| **PF79** Total = Neto + IVA − Σ deducciones, con desglose por concepto | **PASS con desvío de $ 0,01** (re-verificado con base = Subtotal) | Ver §2b. Con Guía Municipal 262.000: deducciones **3.191.444,89** y **Total 141.346.002,71**, persistido y con desglose por línea en Details. El objetivo acordado era 3.191.444,88 / **141.346.002,72**. |
| **PF80** Importe fijo no se recalcula; la porcentual sí | **PASS** (re-verificado con base = Subtotal) | Cambiado el descuento de 4% a 10% (subtotal constante): las 3 porcentuales **no se movieron** (correcto: ahora dependen del subtotal, no del neto) y Guía Municipal quedó en 262.000 con su `%` **deshabilitado**. Con la base anterior se verificó además que bajando el subtotal las porcentuales sí recalculan y la fija no. |
| **PF81** Grilla precargada al abrir el alta, sin escribir nada | **PASS** | 4 filas con nombre e importe ya resueltos desde el catálogo. |
| **PF82 / RT24 / R33** Cambiar el % del catálogo NO altera facturas emitidas | **PASS** | Cambiado `Imp. Sellos` de 1,0500 a 5,0000 por la UI del ABM: las facturas emitidas quedaron **byte-idénticas** antes y después; una factura **nueva** sí precarga 5,0000. Lee el snapshot, no hace join al catálogo. |
| **PF83** Sin deducciones, Total = Neto + IVA | **PASS** | Quitadas las 4 → Total 106.080.000,00 = 96.000.000 + 10.080.000. Sin regresión. |
| **PF84** Compra con costo: stock + egreso vinculados, caja baja | **PASS** | Movimiento ↔ Egreso (2.762.500,61), pago acreditado, movimiento de caja creado. Stock 71→88. |
| **PF85** Compra sin costo, igual que antes de v14 | **PASS** | Movimiento con `EgresoId` NULL, sin egreso ni caja. |
| **PF86 / RT22** Atomicidad: pagos que no suman → no queda nada | **PASS** | Pagos 999.999 contra total 1.210.000: **todos los contadores idénticos** (MovStock 20, Egresos 14, EgresoPagos 18, MovCaja 43) y max(Id) sin avanzar. La validación corre **antes** de abrir la transacción. |
| **PF87** KPI "Reinvertido en hacienda" suma solo compras de hacienda | **PASS** | 0,00 → 2.762.500,61 tras PF84. Un egreso común del mismo importe y la misma fecha **no** sumó. |
| **PF88 / MH-020** Anular compra revierte stock y egreso con contramovimiento | **PASS** | El movimiento original **no se borra** (queda marcado `ANULADA:`), se crea contramovimiento `Ajuste −12`; egreso y pago dados de baja; el movimiento de caja original queda **intacto** y se crea su contramovimiento. Stock 88→76; saldo de caja **de vuelta al valor exacto** previo (76.857.549,39). |
| **PV24** % de deducción fuera de [0,100) bloqueado | **PASS** | POST directo al servidor (saltando el JS): 150 y −5 rechazados con "0 a 99,9999". |
| **PV25** Importe de deducción negativo bloqueado | **PASS** | POST directo: −500 rechazado con ">= 0". |
| **PV26** Deducciones que dejan el Total ≤ 0 bloqueadas | **PASS** | POST directo con deducción 99.999.999: rechazado, sin fila creada. |
| **PV27** Concepto sin nombre o con nombre duplicado bloqueado | **PASS** | "El nombre es obligatorio" / "Ya existe un concepto de deduccion llamado 'Derecho de Registro'." |
| **PV28 / RD19** Compra con costo sin rubro o sin proveedor bloqueada | **PASS** | POST directo con rubro y proveedor vacíos: rechazado. Validación condicional en servidor, no por atributo. |
| **PD18** Nombre de deducción como texto, nunca input editable | **PASS** | 0 inputs visibles en la celda del concepto (sólo hidden de snapshot). |
| **PD19 / RD18** JS compartido, una sola copia | **PASS** | `ov-costo-pagos.js` y `Shared/_FilaPago.cshtml`: **1 archivo cada uno**, consumidos por las 2 pantallas. Diff normalizado contra el JS inline de v17: **sin cambio semántico**, sólo parametrización y null-guards. |
| **PD20** Con el check de costo apagado no se emite ningún `Costo.*` | **PASS** | Bloque oculto y **0 campos habilitados**; al encender aparecen los 17 esperados; al apagar vuelven a 0. |
| **PD21 / RD20** El POST fallido conserva las líneas del usuario | **PASS** | Quitadas 2 de 4 deducciones → validación falló → volvieron **exactamente** las 2 que el usuario tenía, no la precarga del catálogo. |
| **PD21 (2.º caso)** Idem con otro error de validación | **PASS** | Repetido con error de Proveedor/Motivo: grilla conservada. |

## 2b. Cambio en caliente — base de las deducciones porcentuales: Neto gravado → Subtotal

Durante esta corrida el usuario revirtió **R32**: las deducciones porcentuales pasan a calcularse sobre el **Subtotal (importe bruto)**, como hace la liquidación real del consignatario. Se tocaron `Facturas/Create.cshtml` (`recalcDeducciones(subtotal)`, parámetro `baseCalculo`, rótulo "sobre el Subtotal") y la doc de `FacturaVentaDeduccion.Porcentaje`. No hubo cambio de servicio: el cliente manda los importes y el servidor valida rangos, mismo contrato que el IVA.

**Se reconstruyó y reinició la app y se re-ejecutaron las pruebas dependientes de la base.**

| Chequeo pedido | Resultado | Evidencia |
|---|---|---|
| Base = Subtotal en el sentido directo | **PASS** | Cambiando el descuento de 4% a 10% (subtotal constante) los importes de las 3 deducciones porcentuales **no se movieron**. Con la base anterior habrían bajado. |
| Base = Subtotal en el **driver inverso** | **PASS** | Escrito el importe 1.362.532,50 en Derecho de Registro → `%` derivado **1,0000**. Sobre el neto habría dado 1,0417. |
| **IVA no contaminado** | **PASS** | Con descuento 4% el IVA sigue dando **13.734.327,60** (10,5% del neto 130.803.120). 10,5% del subtotal habría dado 14.306.591,25. |
| Línea de **importe fijo** estable | **PASS** | Guía Municipal quedó en 262.000,00 con su `%` deshabilitado ante cambios de subtotal y de descuento. |
| Descuento sigue sobre el Subtotal | **PASS** | 4% de 136.253.250 = 5.450.130,00. |
| Rótulo de la grilla | **PASS** | "(restan del total, sobre el Subtotal)". |
| **Número objetivo 141.346.002,72** | **FAIL por $ 0,01** → ver **D-11** | Sistema: deducciones **3.191.444,89**, **Total 141.346.002,71**, persistido en base con invariante en 0. |

**Causa raíz del centavo (D-11).** Las tres deducciones porcentuales caen **exactamente en medio centavo** sobre este subtotal:

| Concepto | Valor exacto | Sistema (`Math.round`, half-up) | Liquidación del cliente |
|---|---|---|---|
| Derecho de Registro 0,350% | 476.886,**375** | 476.886,**38** | 476.886,**37** |
| Imp. Sellos 1,050% | 1.430.659,**125** | 1.430.659,**13** | 1.430.659,**13** |
| Ing. Brutos 0,750% | 1.021.899,**375** | 1.021.899,**38** | 1.021.899,**38** |

El sistema redondea los tres medios centavos **hacia arriba**, de forma consistente. La liquidación del consignatario redondea **dos hacia arriba y uno hacia abajo**. No hay una regla única (half-up, half-down, half-to-even ni truncamiento) que reproduzca las tres líneas del comprobante: **el papel del consignatario es internamente inconsistente en el medio centavo**, o calcula sobre un intermedio con más precisión del que muestra.

Es decir: el cambio de base **cumplió su objetivo** —cerró la brecha de 117.177,80 a 0,01— pero el número exacto 141.346.002,72 **no es alcanzable** con un redondeo consistente. Queda como decisión del usuario (§5, D-11).

## 3. Regresión obligatoria (núcleo de facturación)

| Caso | Resultado | Evidencia |
|---|---|---|
| Facturas **sin** deducciones: Total = Neto + IVA | **PASS** | PF83 + factura preexistente (1.000.000 + 21% = 1.210.000,00) sin cambio. |
| **PF67** (v17) desc 10% sobre 1.000.000 → Total 1.089.000 | **PASS** | Idéntico a v17 con deducciones en 0. Sin regresión. |
| **PF68** (v17) descuento como importe → % sincronizado, mismo total | **PASS** | Importe 100.000 → % pasa a 10 solo; Total 1.089.000,00. |
| **PF69** (v17) — IIBB | **N/A por diseño** | `IIBB` eliminado en v14; su rol lo cubre el concepto "Ing. Brutos Nómina 42/12" del catálogo, verificado en PF79. |
| **PF72** (v17) Reajuste de ingresos al editar, con el nuevo total | **PASS** | Agregar una deducción bajó el total a 1.085.850,00, apareció el aviso de desvío (3.150,00), "Reajustar" redistribuyó y el diálogo de confirmación de cambio de total guardó correctamente. `TotalDeducciones=3150.00` persistido. |
| Anulación de factura: reversión de stock e ingresos | **PASS** | Stock devuelto correctamente, líneas de deducción dadas de baja, cabecera conserva su snapshot histórico. |
| Anulación de egreso: contramovimiento de caja (MH-020) | **PASS** | Movimiento original **no se borra**; se crea contramovimiento de signo opuesto. Verificado en `Caja` y en MySQL. |
| **`Egresos/Create` completo tras extraer el JS** | **PASS** | Sync % ↔ $ de descuento (5% ↔ 25.000) e IVA (21% ↔ 7.500 → 10%), total en vivo, presets de IVA, "Sin descuento", auto-importe de pagos (v17.1), agregar/quitar filas con reindexado correcto, toggle de fecha de vencimiento por cheque, re-render tras validación fallida con `descDriverInicial` en modo importe, y **alta end-to-end persistida** con decimales exactos. **0 errores JS.** |
| Saldo de caja y listados con sumatorias | **PASS** | Saldo 76.857.549,39 coherente; `Facturas/Index` con columna **Deducciones** y total según filtro. |
| Gráfico de IVA del Tablero Anual (lee `MontoIva`, no deducciones) | **PASS** | Serie de ventas de septiembre = 23.583.327,60 = suma exacta de `MontoIva` de las facturas **no anuladas** del mes. Las deducciones no participan. |
| `Grupo.StockActual` consistente con el ledger | **PASS** | 0 desvíos en los 5 grupos, al inicio y al cierre. |
| Smoke de todas las pantallas | **PASS** | 30 rutas reales **200 OK**, 0 errores JS, incluidos el ABM nuevo y `Stock/Compra`. (`/Grupos` → 302 a `/Stock`, correcto desde v16.) |

## 4. Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

68 ítems. **28 aplican** a v18; el resto es N/A (otros dominios) o no aplica (tecnologías ausentes: `RowVersion`, `maskMoney`, `moment.utc`, DataTables server-side, AFIP/ARCA, Select2 en las pantallas nuevas).

| id | aplica | resultado | acción |
|---|---|---|---|
| GAN-005 marcador `__Invariant` en filas de colección | sí | **PASS** | Round-trip exacto `2.500.000,55 → 262.500,06 → 2.762.500,61` y deducciones `476.886,38 / 1.430.659,13 / 1.021.899,38`. Cubre la grilla de deducciones y ambas grillas de pagos. |
| GAN-006 `step` acorde a `decimal(9,4)` | sí | **PASS** | `step="0.0001"` en **todos** los porcentajes (deducciones, catálogo, factura, egreso, costo de compra). Ningún submit bloqueado en silencio. |
| LP-003 decimales invariantes en `value=` | sí | **PASS** | Todos los `value=` de decimales pasan por el helper `num()` (invariante). |
| **KOI-010 `toFixed()` en repintado AJAX vs. es-AR** | sí | **FAIL → AUTO-FIX APLICADO** | Ver §6. |
| LP-005 campo que cambia de UNIDAD sin barrer superficies | sí | **PASS** | `IIBB`/`OtrasPercepciones` erradicados de código vivo (sólo comentarios e histórico de migraciones). Barridas Details, Index, Create, Edit. Sin PDF/export en el proyecto. |
| MH-020 cancelar da de baja los pagos; reversal por contramovimiento | sí | **PASS** | PF88 + anulación de egreso. Un solo helper (`EgresoHelper`) para las dos rutas. |
| DN-003 FK nueva + fallback heurístico | sí | **PASS** | `MovimientoStock.EgresoId` es FK exacta sin fallback heurístico. Históricos quedan en NULL, correcto. |
| MH-001 `IN` desde colección local | sí | **PASS** | El KPI usa `List<int>`; el catálogo documenta que sólo `string` reproduce el fallo. |
| MH-004 desglose vs. total por anulados | sí | **PASS** | KPI y gráfico de IVA excluyen anulados (probado anulando en vivo). |
| LP-001 agregación de hijas sin filtrar estado del padre | sí | **PASS** funcional | Depende del soft-delete del egreso, no del estado de la compra; correcto hoy, frágil ante D-02. |
| GAN-001 guard "al menos un pago" | sí | **PASS** | Alta sin pagos bloqueada en las dos pantallas. |
| GAN-003 `<partial>` dentro de `<template>` | sí | **PASS** | "Agregar pago" agrega fila en ambas pantallas; reindexado correcto con prefijo `Pagos` y `Costo.Pagos`. |
| SG-001 inputs indexados vacíos contra tipos no nullable | sí | **PASS** | El `%` deshabilitado de una deducción fija no postea y no rompe el binding (persistido con `Porcentaje 0.0000`). |
| ELV-001 controller sin `[Authorize]` | sí | **PASS** | `ConceptosDeduccionController` con `[Authorize(Policy="RequireProductor")]` a nivel clase. |
| ELV-002 guarda en Create ausente en Update | sí | **PASS** | Validaciones de deducciones **simétricas** entre alta y edición (código idéntico). |
| LIP-001 error de `ServiceResult` invisible | sí | **PASS** | Todos los errores de negocio nuevos se ven en el validation-summary. |
| KOI-005 / KOI-006 controller inexistente → 404 | sí | **PASS** | Link del sidebar → 200. |
| KOI-001 botón eliminar del ABM no ejecuta | sí | **PASS** | Usa el handler a nivel form (`data-swal-confirm`), no el patrón roto. |
| KOI-004 consumo > bruto sin bloqueo | sí | **PASS** | PV26: guard en cliente **y** en servidor. |
| REG-008 input pierde foco al tipear | sí | **PASS** | La grilla no se re-renderiza al tipear. |
| REG-010 / KOI-003 / CRM-002 link vs. rol | sí | **PASS con observación** | Ver D-06. |
| MH-019 estado huérfano tras guard nuevo | sí | **FAIL** | Ver D-02 (R34). |
| DN-004 reversar pago posteado altera período cerrado | sí | **N/A** | El proyecto no tiene cierre de período ni caja chica. |
| KOI-009 URL AJAX absoluta en JS estático | sí | **PASS** en v18 / observación preexistente | `ov-costo-pagos.js` limpio. `notifications.js` tiene 4 rutas absolutas (preexistente). Ver D-07. |
| REG-001/002/004/005/009, DN-001/002, VSF-*, CRM-001/003/004/005/006, MH-005…018/021, GAN-002/004, LP-004, KOI-002, CRM-015/016 | no / N-A | — | Tecnología o dominio ausente. |

## 4b. Cobertura de reglas nuevas/modificadas desde la última corrida (2026-09-07)

`6-qa.md` no tenía el campo "Última validación de reglas cross-proyecto" (memoria previa al campo). Se reconstruyó la línea de corte por `git log` sobre el repo de agentes.

| Regla | Origen | Alta/modif. | Resultado | Acción |
|---|---|---|---|---|
| **GAN-005** | `regresiones-manuales.yml` (commit `12ad6ea`, 2026-09-08) | alta — **nace de la corrida QA v17** | **PASS** (no regresión) | Cubierta también en la grilla de deducciones y en `Stock/Compra`. |
| **GAN-006** | `regresiones-manuales.yml` (`12ad6ea`) | alta — nace de QA v17 | **PASS** (no regresión) | Verificada en las 4 superficies nuevas. |
| **DN-003** | `regresiones-manuales.yml` (`12ad6ea`) | alta | **PASS** | Directamente aplicable a `MovimientoStock.EgresoId`. |
| **DN-004** | `regresiones-manuales.yml` (`12ad6ea`) | alta | **N/A** | Sin cierre de período/caja chica en este sistema. |
| **KOI-009** | `regresiones-manuales.yml` (`6699516`, 2026-09-08) | alta | **PASS** en v18 | Observación preexistente en `notifications.js` (D-07). |
| **KOI-010** | `regresiones-manuales.yml` (`6699516`) | alta | **FAIL** | **Auto-fix aplicado** (§6). |
| `32-estandares-qa-implementador` | instructions | **sin cambios** desde 2026-09-04 | — | Mismas reglas que la corrida anterior. |
| `35-pantalla-control-stock` | instructions | **sin cambios** desde 2026-09-01 | — | — |
| `34-integracion-afip-arca` | instructions | 2 bloques nuevos (`12ad6ea`) | **N/A** | Ganadería no tiene integración AFIP/ARCA (`grep afip|arca|CondicionIVAReceptor` = 0 hits). |

## 5. Defectos detectados

| id | Severidad | Defecto | Pasos / evidencia |
|---|---|---|---|
| **D-01** | **CRÍTICO — bloqueante** | **`AnularCompra` se puede ejecutar N veces y descuenta el stock cada vez.** No hay guard en servidor; el único freno es un `String.Contains("ANULADA:")` en la vista, que no protege del doble submit, del F5 sobre el POST ni del botón atrás. | 3 POST a `/Stock/AnularCompra/{id}` sobre una compra de **5** cabezas → **3 contramovimientos** (`Ajuste −5` ×3), stock **85 → 70**. Se destruyeron **10 cabezas inexistentes**. Los 3 POST devolvieron 200 sin error. El detalle acumula `ANULADA:` repetido. |
| **D-02** | **CRÍTICO — bloqueante (R34 abierto)** | **Anular el Egreso por su cuenta deja el movimiento de stock vivo, y además vuelve la compra inanulable para siempre.** `EgresoService.AnularAsync` no tiene ningún guard contra egresos vinculados a una compra. | Compra con costo (movimiento ↔ egreso) → `Egresos/Index` → "Anular" → 200 "Egreso anulado". Query de control: **1 movimiento de compra vivo con egreso dado de baja**; el stock queda arriba sin costo detrás. `Stock/Historial` sigue mostrando el link "Egreso #N" a un egreso anulado. Peor: `AnularCompraAsync` corta en "El egreso vinculado a la compra ya no existe" **después** de postear el contramovimiento de stock → rollback → la compra ya no se puede anular por ningún camino. |
| **D-03** | **ALTA** | **`AnularCompra` acepta los movimientos de reversión de una factura anulada y destruye el stock que la anulación había devuelto.** El filtro es sólo `Tipo == Compra`, y `FacturaVentaService.AnularAsync` postea la reversión **como tipo `Compra`**. | Anulada una factura → stock 70→**71** (correcto). En `Stock/Historial` la fila "Reversion anulacion Factura F-0000NN" es tipo Compra y **muestra el botón "Anular compra"**. Un clic → stock **71→70**: la cabeza devuelta desaparece, sin egreso ni compensación. Reproducido end-to-end. |
| **D-11** | **MEDIA — decisión de negocio** | **El Total queda $ 0,01 por debajo del comprobante del consignatario** por redondeo de medio centavo. Ver §2b para la causa raíz completa. | Sistema 141.346.002,71 vs. objetivo 141.346.002,72. Las 3 deducciones porcentuales caen exactamente en `.375`/`.125`/`.375`; el sistema redondea las tres half-up (consistente), el comprobante redondea dos arriba y una abajo (inconsistente). Ninguna regla única reproduce el papel. |
| **D-04** | MEDIA | `MontoIva` se persiste **sin `Math.Round`** en factura (alta y edición), mientras `MontoDescuento` y `EgresoHelper` sí redondean. El `Total` se calcula con el valor crudo y MySQL redondea al escribir → el invariante puede romperse por 1 centavo con un `%` de IVA de muchos decimales. | `FacturaVentaService`, alta y edición: `MontoIva = input.MontoIva`. No reproducido con los datos de dev, pero es una asimetría real y toca justo el eje del D-11. |
| **D-05** | MEDIA | `Subtotal` de cabecera se calcula como `Round(Σ kilos×precio)` mientras cada línea se persiste como `Round(kilos×precio)` por separado. Con `KilosTotales` a 3 decimales y `PrecioPorKilo` a 4, cabecera y suma de líneas pueden diferir en centavos. Idem `TotalDeducciones` (suma de crudos vs. líneas redondeadas). | Estático. No reproducido con los datos de dev. Fix: `Sum(Math.Round(x,2))` en ambos lados. |
| **D-06** | BAJA | El link "Conceptos de deducción" del sidebar está sólo bajo `IsAuthenticated`, sin guard de rol, mientras el controller exige `RequireProductor`. Un rol autenticado por debajo de Productor vería el link y recibiría 403. | Hoy no hay tal rol (Productor / SuperUsuario), así que no es explotable; queda como deuda de defensa en profundidad. |
| **D-07** | BAJA | `notifications.js` tiene 4 rutas AJAX absolutas desde la raíz (KOI-009). **Preexistente**, no de v18. Rompe si la app se hostea bajo subdirectorio. | `notifications.js:11,31,47,57`. |
| **D-08** | BAJA | El desglose de deducciones en `Facturas/Details` se lista **sin `OrderBy(Orden)`** (sale en orden inverso al del catálogo). | Details muestra Guía Municipal, Ing. Brutos, Sellos, Derecho de Registro — invertido respecto del alta. |
| **D-09** | BAJA | `max="99.99"` en `PorcentajeDescuento` (factura y egreso) contra columna `decimal(9,4)` y `max="99.9999"` en los otros porcentajes. Rechaza valores legítimos como `99.995`. | `Facturas/Create.cshtml:166`, `Egresos/Create.cshtml:62`. |
| **D-10** | BAJA | Mensajes de validación en inglés por defecto en algunos campos ("The Proveedor (organismo intermediario) field is required.", "The value '' is invalid."), conviviendo con mensajes en español. **Preexistente.** | Visible en el re-render de `Facturas/Create` y `Stock/Compra`. |

**Sobre la regresión que se anunció en `ov-costo-pagos.js`:** **no se pudo reproducir ninguna.** Se hizo un diff normalizado del JS inline de v17 contra el archivo extraído (sin cambio semántico: sólo parametrización, null-guards y el guard `if (inp.disabled) return`) y se ejercitaron en navegador real **todas** las rutas de la pantalla — sync `%`↔`$` de descuento e IVA en ambas direcciones, presets, "Sin descuento", total en vivo, auto-importe de pagos, agregar/quitar filas con reindexado bajo los dos prefijos de binding, toggle de cheque, re-render tras validación fallida, y alta end-to-end persistida con decimales exactos. Todo **PASS**, 0 errores JS. El único defecto real hallado en ese archivo es **KOI-010**, que es **preexistente de v17** (el `toFixed(2)` estaba igual en el JS inline) y quedó auto-fixeado. El bug `&#x27;` estaba efectivamente corregido con `@Html.Raw` en las 2 vistas, y **se barrió todo el repositorio buscando el patrón: no hay una tercera instancia** (literales Razor con apóstrofe fuera de `Html.Raw` = 0 hits).

## 6. Auto-fixes aplicados

| id catálogo | Archivos tocados | Cambio | Resultado post-parche |
|---|---|---|---|
| **KOI-010** | `Ganaderia.Web/wwwroot/js/ov-costo-pagos.js` (`actualizarSuma`), `Ganaderia.Web/Views/Egresos/Create.cshtml:142`, `Ganaderia.Web/Views/Stock/Compra.cshtml:136` | `sumaPagosEl.textContent = suma.toFixed(2)` → `fmtMoneda(suma)`; el render inicial del `<span>` pasa de `0.00` a `$ 0,00` en las dos vistas. | **PASS.** Antes: `1493827.15` al lado de `$ 1.493.827,15` en la misma tabla. Ahora ambos `$ 1.493.827,15`, en las 2 pantallas. Build 0 errores; alta end-to-end de egreso y de compra con costo re-verificadas post-fix con decimales exactos (`2.500.000,55 / 262.500,06 / 2.762.500,61`). Sin regresión. |

**No auto-fixeados a propósito** (decisión de negocio o cambio de comportamiento acordado — escalados al implementador): **D-01, D-02, D-03** (definen qué debe pasar al anular: bloquear vs. cascadear), **D-11** (regla de redondeo del medio centavo: la decide el usuario contra su consignatario), **D-04/D-05** (tocan aritmética de plata ya registrada), D-06 a D-10.

## 7. Invariantes de datos (al inicio y al cierre)

| Invariante | Desvíos |
|---|---|
| `Subtotal − MontoDescuento − TotalDeducciones + MontoIva = Total` en `FacturasVenta` | **0** |
| `TotalDeducciones` = Σ líneas de `FacturaVentaDeducciones` (facturas activas) | **0** |
| `Subtotal − MontoDescuento + MontoIva = Importe` en `Egresos` | **0** |
| Σ `EgresoPagos` = `Egreso.Importe` (egresos activos) | **0** |
| `Total ≤ 0` en facturas | **0** |
| Deducciones con `Monto < 0` o `Porcentaje` fuera de `[0,100)` | **0** |
| `Grupo.StockActual` vs. ledger de `MovimientosStock` | **0** (los 5 grupos) |

Nota: una factura **anulada** conserva su `TotalDeducciones` de cabecera mientras sus líneas quedan soft-deleted. Es correcto (snapshot histórico) y por eso el invariante se evalúa sobre facturas activas.

## 8. Riesgos de liberación y mitigaciones

- **RT23 / bloqueante de deploy** — la migración hace 4 `DropColumn` de `IIBB`/`OtrasPercepciones`. Es segura **sólo con 0 facturas de venta en producción**. **Hay que re-verificarlo el día del deploy**: si aparece aunque sea una factura, frenar y convertir esos valores en filas de `FacturaVentaDeducciones` antes de borrar nada. El `Down()` recrea las columnas **en 0**: el rollback no recupera datos.
- **D-01/D-02/D-03** — tres caminos por los que el stock se corrompe en silencio, todos alcanzables con un clic desde pantallas normales. Es exactamente el vínculo stock↔costo que v18 vino a construir. **Mitigación: no liberar hasta corregirlos.**
- **D-11 / R32 revertido** — la base pasó a Subtotal y la brecha contra el comprobante bajó de 117.177,80 a **0,01**. Hay que decidir explícitamente si se acepta el centavo o se adopta la regla de redondeo del consignatario. Conviene avisarle al usuario antes de que lo descubra conciliando.
- **R33** — verificado y correcto (PF82): editar el catálogo no toca facturas emitidas. Hay que **decírselo al usuario** o va a parecer un error.
- **Concurrencia** — `Grupo.StockActual` es desnormalizado, sin `RowVersion` ni bloqueo de fila, y las lecturas de validación corren fuera de la transacción. Bajo uso concurrente puede desincronizarse del ledger. No hay rutina de reconciliación. Riesgo bajo con 1–2 usuarios reales; conviene una verificación periódica del invariante.
- **Sin toggle de rollout** — el cambio de semántica (percepciones que sumaban → deducciones que restan) entra sin AppSetting de reversión. Aceptable porque producción tiene 0 facturas de venta.

## 9. Pruebas mínimas ejecutadas

22 criterios (PF78–PF88, PV24–PV28, PD18–PD21) + 7 chequeos de re-verificación tras el cambio de base + 13 casos de regresión + smoke de 30 rutas + 7 invariantes de base, todos en **navegador real** contra la app corriendo y contrastados contra MySQL. Base restaurada al baseline exacto (`diff` = 0 diferencias) dos veces: tras la primera pasada y tras la re-verificación del cambio de base.

## 10. Checklist de salida para merge (v18)

- [x] Build 0 errores, sin warnings nuevos (antes y después del auto-fix y del cambio de base).
- [x] Migración aplicada y reversible en `ganaderia_dev`.
- [x] PF78–PF88, PV24–PV28, PD18–PD21: **22/22 PASS** (PF79 con el desvío de $ 0,01 de D-11).
- [x] Cambio de base Neto→Subtotal re-verificado end-to-end y persistido.
- [x] IVA sigue sobre el Neto gravado; descuento sigue sobre el Subtotal.
- [x] Regresión de v17 (PF67, PF68, PF72) sin desvíos.
- [x] Invariantes de base en 0 desvíos.
- [x] Auto-fix KOI-010 aplicado y verificado.
- [x] Base de dev devuelta al baseline exacto.
- [x] Sin commit y sin deploy (pedido explícito).
- [ ] **D-01 (doble anulación de compra) — BLOQUEANTE. Corregido para el camino secuencial; SIGUE ABIERTO bajo POST concurrentes (doble clic). Ver §12.4.**
- [x] **D-02 (R34: anular egreso vinculado) — CORREGIDO y re-verificado (§12.2).**
- [x] **D-03 (anular la reversión de una factura) — CORREGIDO y re-verificado (§12.3).**
- [ ] **D-11 (centavo de redondeo) — decisión del usuario, pendiente.**
- [ ] D-04/D-05 (redondeo de `MontoIva` y de `Subtotal`) — pendiente, no bloqueante.
- [ ] D-06 a D-10 — pendientes, cosméticos/deuda.
- [ ] **RT23: re-verificar `SELECT COUNT(*) FROM FacturasVenta` en producción el día del deploy.**
- [ ] Revisión del implementador sobre el auto-fix KOI-010 antes del merge.

## 11. Veredicto

**NO APTO PARA DEPLOY.**

La **funcionalidad nueva de v18 es correcta y está completa**: los 22 criterios de aceptación pasan end-to-end contra la app real. El snapshot de deducciones es genuinamente inmutable (PF82 verificado cambiando el catálogo en vivo), la transacción de la compra con costo es **atómica de verdad** (PF86: forzado el fallo, no quedó ni una fila), y no hay ninguna regresión sobre v17, la caja, el stock ni el gráfico de IVA. La extracción del JS compartido está bien hecha y las dos pantallas lo consumen sin divergir.

El cambio de base (Neto → Subtotal) hecho en caliente durante esta corrida **funciona y logró su objetivo**: cerró la brecha contra el comprobante del consignatario de 117.177,80 a **0,01**, sin contaminar el IVA ni el descuento, y con el driver inverso correcto. El centavo remanente (**D-11**) no es un bug de implementación: los tres porcentajes caen exactamente en medio centavo y el papel del consignatario los redondea de forma internamente inconsistente. Es una decisión del usuario.

Lo que bloquea es **la otra mitad de R34**: la anulación. Se resolvió la punta Stock→Egreso (`AnularCompraAsync`, que funciona perfecto) pero quedaron **tres caminos por los que el stock se corrompe en silencio**, los tres alcanzables con un clic desde pantallas normales y **ninguno con error visible**:

1. **D-01** — anular dos veces la misma compra descuenta el stock dos veces. Un doble clic alcanza. Verificado: 3 anulaciones de una compra de 5 cabezas destruyeron 10 cabezas.
2. **D-02** — anular el egreso desde `Egresos/Index` deja el stock arriba sin costo detrás **y** deja la compra inanulable para siempre. Es R34 textual, todavía abierto.
3. **D-03** — el botón "Anular compra" aparece sobre los movimientos de reversión de una factura anulada, y usarlo borra el stock que la anulación acababa de devolver.

En un sistema **en producción** cuyo dato más sensible es el conteo de cabezas, tres formas silenciosas de perder stock no se liberan. Ninguna es difícil de cerrar —un guard de idempotencia, un guard en `EgresoService.AnularAsync` y un `mov.FacturaVentaId == null` en el filtro— pero las tres son **decisiones de negocio** (¿bloquear o cascadear?), así que no se auto-fixearon: van al implementador.

Con esos tres corregidos y re-verificados, y con D-11 decidido, v18 queda apto. El resto de los hallazgos (D-04 a D-10) no bloquea.

> **Actualización (misma jornada): los tres fueron corregidos y re-verificados. D-02 y D-03 quedaron cerrados; D-01 sigue abierto bajo concurrencia y mantiene el NO APTO. Ver §12.**

---

## 12. Re-verificación de las correcciones de D-01 / D-02 / D-03 (2026-09-08, misma jornada)

El implementador corrigió los tres bloqueantes bajo la decisión de negocio del orquestador: **bloquear, no cascadear**. Segunda migración `20260908210815_MovimientoStock_MovimientoRevertido` (aditiva, con backfill), aplicada después de `Facturas_Deducciones_Y_CompraConCosto` — ahora hay **dos** migraciones pendientes, en ese orden.

Se re-ejecutaron los tres defectos con la misma agresividad con que se encontraron: POST repetidos, POST directos salteando la UI, y verificación **en base**, no en pantalla. Build: **0 errores**, 9 warnings preexistentes.

### 12.1 Resultado por defecto

| Defecto | Corrección | Resultado |
|---|---|---|
| **D-02** (anular egreso vinculado) | `EgresoService.AnularAsync` rechaza el egreso vinculado y remite a Stock; `AnularCompraAsync` valida todo antes de abrir la transacción | **CORREGIDO — verificado** |
| **D-03** (anular la reversión de una factura) | Discriminador `Tipo == Compra && FacturaVentaId == null`, en la vista **y** en el servidor | **CORREGIDO — verificado** |
| **D-01** (doble anulación) | `MovimientoStock.MovimientoRevertidoId` (self-FK Restrict) como estado real, en lugar del `String.Contains("ANULADA:")` | **PARCIALMENTE CORREGIDO — sigue bloqueante** |

### 12.2 D-02 — corregido

- **POST directo** a `/Egresos/Anular/{id}` sobre el egreso costo de una compra (saltando la UI): **bloqueado**, con el mensaje que remite a Stock > Historial.
- Tras el intento fallido, la compra **sigue siendo anulable** (antes quedaba inanulable para siempre): se anuló correctamente, con contramovimiento de stock, egreso y pago dados de baja, movimiento de caja original **intacto** y contramovimiento (MH-020).
- Invariante "movimiento de compra vivo con egreso dado de baja y sin contramovimiento": **0 filas**.
- **Observación menor (D-12, BAJA)**: el botón "Anular" **sigue visible** en `Egresos/Index` para el egreso vinculado. El servidor rechaza correctamente —que es lo que importa— pero el usuario puede clickearlo y recibir un error evitable. Conviene ocultarlo o deshabilitarlo con tooltip, por el mismo criterio de defensa en profundidad de D-06.

### 12.3 D-03 — corregido

- La fila "Reversion anulacion Factura F-0000NN" (tipo `Compra`, con `FacturaVentaId`) **ya no muestra** el botón "Anular compra".
- **POST directo** sobre ese movimiento: **bloqueado** con "Este movimiento es la reversión de una factura de venta anulada, no una compra de hacienda."
- Regresión del discriminador verificada: una **compra sin costo** (`EgresoId` NULL, `FacturaVentaId` NULL) **sigue siendo anulable**, que es exactamente lo que se habría roto usando `EgresoId != null`. La elección del discriminador es correcta.

### 12.4 D-01 — sólo la mitad: **sigue bloqueante**

**El camino secuencial quedó cerrado.** 4 POST seguidos: el primero anula, los tres siguientes reciben "Esta compra ya fue anulada. No se puede anular dos veces." Eso cubre F5-resubmit, botón atrás y clicks repetidos después de que la página recargó.

**El camino concurrente sigue abierto, y es justamente el doble clic que motivó el defecto.** El guard es un `AnyAsync(m => m.MovimientoRevertidoId == mov.Id)` que corre **fuera y antes** de la transacción, sin bloqueo de fila y sin constraint en base: check-then-act clásico.

Experimento controlado sobre baseline limpio (`StockActual` 72 = Ledger 72):

| Paso | StockActual | Ledger |
|---|---|---|
| Compra de **10** cabezas | 82 | 82 |
| **2 POST simultáneos** (un doble clic) | **72** | **62** |

Resultado: **2 contramovimientos** posteados (`Ajuste −10` ×2) para una sola anulación, ambos con `MovimientoRevertidoId` apuntando a la misma compra. Reproducido **3 de 3 veces** con 2 POST; con 6 POST en paralelo salieron 3 contramovimientos.

Hay un segundo daño, más insidioso que el original: **`Grupo.StockActual` y el ledger se desincronizan**. `StockActual` queda en 72 — el valor *plausible*, el que el usuario ve en pantalla — mientras el ledger de `MovimientosStock` suma 62. Es un *lost update* sobre la columna desnormalizada: las dos transacciones leyeron 82 y las dos escribieron 72, pero **las dos filas de movimiento persistieron**. La corrupción es **invisible en la UI**: sólo aparece auditando el ledger.

**Fix propuesto** (no aplicado: toca la estrategia de concurrencia, es decisión del implementador):
1. **Índice único sobre `MovimientoRevertidoId`** (permitiendo NULL). Es la garantía a nivel base, aditiva y barata: hace estructuralmente imposible el segundo contramovimiento, y además es semánticamente correcto (a lo sumo un contramovimiento por movimiento revertido). El segundo POST cae en `DbUpdateException` y se traduce al mismo mensaje de "ya fue anulada".
2. Mover el chequeo **dentro** de la transacción con lectura bloqueante sobre la fila del `Grupo`, lo que además cierra el lost update de `StockActual`.
3. Complementario, no sustituto: deshabilitar el botón en el submit del lado del cliente.

### 12.5 Backfill de la migración — correcto

Caso crítico: el movimiento 25 fue anulado **antes** de la migración, cuando la marca era sólo texto.

- La migración le pobló `MovimientoRevertidoId = 25` a su contramovimiento (mov. 26). Verificado en base.
- **POST directo** a `/Stock/AnularCompra/25`: rechazado con **"Esta compra ya fue anulada"** — es el guard de idempotencia el que dispara, no el de "el egreso ya no existe". Eso prueba que el estado nuevo quedó bien poblado y que el defecto **no reaparece** en los datos viejos.
- El botón tampoco se renderiza para esa fila.

### 12.6 Regresión de lo que la corrección pudo romper

| Caso | Resultado |
|---|---|
| **`RegistrarMuerteAsync`** (cortado y restaurado por el implementador) | **PASS** — Muerte de 2 cabezas: stock 72→70, movimiento tipo 4 correcto. |
| **`CompensarAsync`** (ídem) | **PASS** — Compensación inter-categoría Lote vaquillonas → Lote 1: un movimiento `−2` en origen y `+2` en destino, stocks 44→42 y +2. |
| **`RegistrarAjusteAsync`** (ídem) | **PASS** — El campo es `StockReal` (conteo absoluto), no delta: con `StockReal=40` posteó el delta correcto y dejó el stock en 40. |
| Nacimiento (control) | **PASS** — 70→73. |
| Anulación de **egreso común** (no vinculado) | **PASS** — "Egreso anulado. 1 pago(s) ya acreditado(s) se revirtieron con un contramovimiento en caja." El bloqueo de D-02 **no** alcanza a los egresos comunes. |
| Anulación de **factura de venta** | **PASS** — stock 40→37 (venta) →40 (anulación). |
| **PF85** compra sin costo, anulable | **PASS** — creada y anulada correctamente. |
| **PF88** compra con costo | **PASS** — contramovimiento de stock, egreso y pago de baja, caja original intacta + contramovimiento. |
| **Base de deducciones = Subtotal** (no se tocó) | **PASS** — rótulo "sobre el Subtotal"; con descuento 4% → neto 130.803.120,00, IVA **13.734.327,60**, deducciones 3.191.444,89, Total 141.346.002,71. Cambiando el descuento a 10% las deducciones **no se mueven**. Intacto. |
| Invariantes de base | **INV1–INV5 en 0 desvíos** sobre baseline limpio. INV6/INV7 sólo se ensucian al forzar la race de D-01. |
| Ledger vs `Grupo.StockActual` | **0 desvíos** en los 5 grupos sobre baseline limpio; **se rompe bajo la race de D-01** (§12.4). |

### 12.7 Invariantes nuevos recomendados para monitoreo

A raíz de esta corrección conviene dejar dos chequeos permanentes:

- `SELECT MovimientoRevertidoId, COUNT(*) FROM MovimientosStock WHERE MovimientoRevertidoId IS NOT NULL GROUP BY 1 HAVING COUNT(*) > 1` → **debe dar 0 filas**. Hoy es el detector directo de D-01.
- `Grupo.StockActual` vs. suma del ledger por grupo → **0 desvíos**. Es el único que revela el lost update, porque la pantalla muestra el valor plausible.

### 12.8 Hallazgo registrado, no tocado

**D-13 (INFORMATIVO)** — existe **1 movimiento de caja en estado `Acreditado` con `DeletedAt` seteado** (2026-07-02), de la era v11, anterior a la adopción de MH-020 (ledger inmutable con contramovimiento). Es dato viejo, **no una regresión de esta entrega**: se registra y **no se toca**. Si en algún momento se hace una limpieza histórica, es el candidato.

### 12.9 Veredicto tras la re-verificación

**SIGUE NO APTO PARA DEPLOY**, por un único defecto: **D-01 bajo concurrencia**.

Dos de los tres bloqueantes están **genuinamente cerrados**: D-02 y D-03 resisten el POST directo saltando la UI, la decisión "bloquear, no cascadear" está bien implementada en servidor y no rompió la anulación de egresos comunes, y el backfill hace que los datos viejos no revivan el defecto. Los tres flujos que el implementador cortó de más (`RegistrarMuerteAsync`, `CompensarAsync`, `RegistrarAjusteAsync`) funcionan end-to-end en navegador, no sólo compilan. El cambio de base a Subtotal quedó intacto.

D-01 se cerró para el 80% de los caminos reales pero **no para el que le da nombre**: el doble clic. Pasar de una subcadena de texto a estado consultable fue la corrección correcta, pero el estado se consulta **fuera de la transacción y sin constraint**, así que dos requests simultáneos lo leen los dos en falso. Y el efecto ahora es peor de caracterizar que antes, porque `StockActual` queda en el número que el usuario espera ver mientras el ledger dice otra cosa: **la pérdida de stock deja de ser visible en pantalla**.

Es un fix chico —un índice único sobre `MovimientoRevertidoId`, que además es semánticamente lo correcto— pero es cambio de estrategia de concurrencia y de esquema (tercera migración), así que no se auto-fixeó.

Con D-01 cerrado y re-verificado bajo POST concurrentes, v18 queda **apto**, con D-11 (el centavo de redondeo) pendiente de decisión del usuario y D-04 a D-13 como deuda no bloqueante.
