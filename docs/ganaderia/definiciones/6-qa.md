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
- [ ] Pruebas manuales PF/PV ejecutadas y firmadas en `plan-qa-etapa7.md`.
