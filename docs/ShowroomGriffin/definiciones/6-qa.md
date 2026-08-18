# 6 — QA
## Sistema de Gestión Comercial — ShowroomGriffin (Ulises / OlvidataSoft)

**Versión:** 1.0
**Estado:** Reporte QA inicial — Gate sobre handoff a documentación de cliente
**Inputs:**
- `analisis-funcional.md` (Módulos 1–9 + Dashboard, criterios de aceptación, decisiones D1–D6)
- `2-disenador-funcional.md` v1.0 (Máquinas de estados §4.1 Compra, §4.2 Venta, §4.3 Devolución, §4.4 Maestros, §4.5 Aumento masivo)
- `5-implementador.md` v1.0 (etapas E0–E8 cerradas, build verde 0/0)

**Convenciones de estado**:
- `PASS-CR` = verificado por **revisión de código + build verde + cierre del implementador**.
- `PASS-EJ` = verificado por **ejecución funcional** (smoke contra Dev/Prod tras migración M2).
- `FAIL` = defecto reproducido.
- `BLOCKED` = requiere ejecución manual con datos productivos / wizard JS / archivos reales y no puede cerrarse por inspección.
- `N/A` = fuera de alcance v1.

> Nota de alcance del agente: este reporte se construye sobre revisión estática del código (`5-implementador.md`), build limpio en Dev y Prod, y migraciones M1+M2 aplicadas en ambos entornos. Los criterios marcados como `BLOCKED` no implican defecto: requieren un humano ejecutando el wizard, generando PDF, subiendo adjuntos o forzando concurrencia real.

---

## 1. Alcance funcional validado

| Módulo | Cobertura por inspección | Cobertura por ejecución | Etapa origen |
|---|---|---|---|
| M1 Seguridad y acceso | ✅ | ⚠️ Pendiente smoke | E0 |
| M2 Maestros comerciales | ✅ | ⚠️ Pendiente smoke | E1 |
| M3 Productos y variantes | ✅ | ⚠️ Pendiente smoke | E2 |
| M4 Stock e inventario | ✅ | ⚠️ Pendiente smoke | E3 |
| M5 Compras a proveedores | ✅ | ⚠️ Pendiente smoke | E4 |
| M6 Ventas a clientes ⭐ | ✅ | ⚠️ Pendiente smoke (incluye R1 concurrencia y R4 retries) | E5 |
| M7 Devoluciones y cambios | ✅ | ⚠️ Pendiente wizard JS + escenarios reales | E6 |
| M8 Resumen semanal | ✅ | ⚠️ Pendiente export Excel real | E7 |
| M9 Aumento masivo | ✅ | ⚠️ Pendiente concurrencia D6 dos pestañas | E2/E7 |
| Dashboard | ✅ | ⚠️ Pendiente render con datos reales | — |
| Hardening (logging, rate limit, HSTS) | ✅ | ⚠️ Pendiente tests 429 y headers | E8 |

---

## 2. Cobertura por criterio de aceptación (PASS / FAIL / BLOCKED)

### M1 — Seguridad y acceso

| # | Criterio | Estado | Evidencia / Notas |
|---|---|---|---|
| M1-CA-01 | Rol Vendedor existe en seed | PASS-CR | E0 + revisión de seeds en Infrastructure (RolVendedor seedado). |
| M1-CA-02 | Sidebar muestra solo módulos según rol | PASS-CR | Sidebar dinámico verificado en E0; depende de policies `RequireAdministrador`/`RequireVendedor`. |
| M1-CA-03 | Vendedor en gestión de usuarios → 403 | PASS-CR | UsuariosController usa `RequireAdministracion`. **Smoke pendiente**. |

### M2 — Maestros comerciales

| # | Criterio | Estado | Evidencia / Notas |
|---|---|---|---|
| M2-CA-01 | Categoría duplicada → error de validación | PASS-CR | R-MAE-01 + índice único en CategoriaConfiguration. **Smoke pendiente**. |
| M2-CA-02 | Subgrupos filtrados por categoría vía AJAX | PASS-CR | Endpoint AJAX en MaestrosController; verificado en E1. **Smoke pendiente UX**. |
| M2-CA-03 | Vendedor ve clientes sin acciones CRUD | PASS-CR | `RequireAdministrador` en acciones de mutación; vista condicional. **Smoke pendiente**. |
| M2-CA-04 | Inactivar categoría con productos activos → error | PASS-CR | R-MAE-05 implementado en CategoriaService; cubierto E1. |
| M2-CA-05 | **D5**: Inactivar cliente con ventas → error | PASS-CR | Guard agregado en E1 a `ClienteService.InactivarAsync`. |

### M3 — Productos y variantes

| # | Criterio | Estado | Evidencia / Notas |
|---|---|---|---|
| M3-CA-01 | Form variante con campos dinámicos según categoría | PASS-CR | JS dinámico Ropa/Zapatilla en `Variantes/_Form.cshtml`; cubierto E2. **Smoke UX pendiente**. |
| M3-CA-02 | SKU duplicado → error | PASS-CR | Índice único filtrado (sólo activas), R-PRD-05. |
| M3-CA-03 | CódigoBarra duplicado → error | PASS-CR | Índice único filtrado, R-PRD-06. |
| M3-CA-04 | Vendedor no ve columnas de costo | PASS-CR | Vista usa branching por rol; ProductosController retorna VM sin costos para Vendedor. **Smoke pendiente**. |
| M3-CA-05 | Inactivar variante con stock>0 → error | PASS-CR | R-PRD-08 en VarianteService. |

### M4 — Stock e inventario

| # | Criterio | Estado | Evidencia / Notas |
|---|---|---|---|
| M4-CA-01 | Carga inicial incrementa stock + Movimiento `CargaInicial` | PASS-CR | E3, transacción explícita. |
| M4-CA-02 | Ajuste manual genera Movimiento `AjusteManual` con anterior/nueva | PASS-CR | E3, atomicidad confirmada. |
| M4-CA-03 | Historial muestra tipo, cantidad, anterior, resultante, fecha | PASS-CR | `MovimientoStockListItemViewModel` ya proyecta los campos. **Smoke pendiente**. |
| M4-CA-04 | Listado resalta visualmente stock<=mínimo | PASS-CR | Lógica en VM + clase CSS condicional. **Smoke pendiente**. |
| M4-CA-05 | Vendedor no accede a carga inicial / ajuste → 403 | PASS-CR | Acciones con `RequireAdministrador`. **Smoke pendiente**. |

### M5 — Compras a proveedores

| # | Criterio | Estado | Evidencia / Notas |
|---|---|---|---|
| M5-CA-01 | Compra creada en Borrador | PASS-CR | E4. |
| M5-CA-02 | Avance de estado lineal con SweetAlert | PASS-CR | UX con `swal.fire confirm` antes de POST. **Smoke UX pendiente**. |
| M5-CA-03 | Edición bloqueada en Verificada/Recibida | PASS-CR | Guarda en CompraService + UI sin botón Editar. |
| M5-CA-04 | Recepción valida Rec+Dañ+Dev ≤ Pedida por línea | PASS-CR | Validación JS + revalidación server-side (E4 pre-validación de TODAS las líneas antes de mutar). |
| M5-CA-05 | Recepción impacta stock solo con `CantidadRecibida` | PASS-CR | R-COM-05 + Movimiento `CompraRecepcion`. |
| M5-CA-06 | UltimoPrecioCompra se actualiza al recepcionar | PASS-CR | E4. |
| M5-CA-07 | Vendedor → 403 en cualquier ruta de compras | PASS-CR | CompraController completo con `RequireAdministrador`. **Smoke pendiente**. |
| M5-CA-08 | Adjuntos ≤ 5MB y formato válido | BLOCKED | Validación presente; requiere prueba real con archivos. |

### M6 — Ventas a clientes ⭐

| # | Criterio | Estado | Evidencia / Notas |
|---|---|---|---|
| M6-CA-01 | Venta creada en Confirmada con stock decrementado | PASS-CR | E5, transacción Serializable + `await using` + rollback explícito. |
| M6-CA-02 | Stock insuficiente → no se crea | PASS-CR | Guarda + rollback en early-return (E5). |
| M6-CA-03 | Suma pagos ≠ total → error | PASS-CR | Validación con tolerancia ±0.01 en VentaService. |
| M6-CA-04 | Anular Confirmada repone stock + cambia a Anulada | PASS-CR | E5 (`AnularAsync` con Movimiento `AnulacionVenta`). |
| M6-CA-05 | Venta Entregada NO se puede anular | PASS-CR | Guarda explícita en service + sin botón en UI. |
| M6-CA-06 | Remito PDF generado con QuestPDF | BLOCKED | Acción `EmitirRemito` presente; requiere descarga real para validar formato. |
| M6-CA-07 | Vendedor no ve costos ni ganancias | PASS-CR | E-08 (G-09 filtro por vendedor + VM sin Costo/Ganancia). |
| M6-CA-08 | Carrito AJAX con validación stock en tiempo real | BLOCKED | JS implementado; requiere ejecución navegador. |
| M6-CA-09 | Número correlativo sin duplicados | PASS-CR | Asignado dentro de la transacción Serializable + reintentos R4 en deadlock (E5). |

### M7 — Devoluciones y cambios

| # | Criterio | Estado | Evidencia / Notas |
|---|---|---|---|
| M7-CA-01 | Wizard de 4 pasos sin errores | BLOCKED | JS multistep; requiere ejecución navegador. |
| M7-CA-02 | Stock devuelto se reingresa | PASS-CR | E6 (Movimiento `DevolucionCliente`). |
| M7-CA-03 | Stock items nuevos (cambio) se decrementa | PASS-CR | E6 (G-08). |
| M7-CA-04 | Cantidad devuelta ≤ disponible | PASS-CR | Guarda en DevolucionService + rechazo defensivo de cantidades < 0 (E6). |
| M7-CA-05 | Diferencia en cambio mayor valor + medio de pago | PASS-CR | Guarda en service. **Smoke pendiente con datos**. |
| M7-CA-06 | Validación server-side completa al POST paso 4 | PASS-CR | R4 cumplido (`2-disenador §7`). |

### M8 — Resumen semanal

| # | Criterio | Estado | Evidencia / Notas |
|---|---|---|---|
| M8-CA-01 | Resumen sólo transferencias en Confirmada/Entregada | PASS-CR | Filtro en `ResumenSemanalService` (E7). |
| M8-CA-02 | Agrupación por día + total semanal | PASS-CR | VM con detalle por día y total. |
| M8-CA-03 | Export Excel ClosedXML funciona | BLOCKED | Acción `ExportarExcel` presente; requiere descarga real. |
| M8-CA-04 | Vendedor → 403 | PASS-CR | `RequireAdministrador` en controller. |

### M9 — Aumento masivo

| # | Criterio | Estado | Evidencia / Notas |
|---|---|---|---|
| M9-CA-01 | Filtros por categoría/subgrupo/marca funcionan | PASS-CR | `Preview` en AumentoMasivoController (E7). |
| M9-CA-02 | Preview muestra precio actual y nuevo | PASS-CR | VM `AumentoMasivoPreviewItemViewModel` proyecta ambos. |
| M9-CA-03 | Variantes excluidas no se actualizan | PASS-CR | Service procesa solo Ids seleccionados. |
| M9-CA-04 | Aumento aplicado con redondeo a 2 decimales | PASS-CR | Math.Round con MidpointRounding configurado. |
| M9-CA-05 | Vendedor → 403 | PASS-CR | `RequireAdministrador` en controller. |
| M9-CA-06 | **D6/R5**: concurrencia con dos pestañas → 2da re-previsualiza | PASS-CR | E2 (`RowVersion` + `IsRowVersion()` + `DbUpdateConcurrencyException` con mensaje específico). **Smoke pendiente con dos navegadores**. |

### Dashboard

| # | Criterio | Estado | Evidencia / Notas |
|---|---|---|---|
| D-CA-01 | Admin ve todos los indicadores | PASS-CR | DashboardController por rol. **Smoke pendiente**. |
| D-CA-02 | Vendedor ve versión limitada sin costos/ganancias | PASS-CR | VM diferenciado por rol. **Smoke pendiente**. |
| D-CA-03 | Datos cargan según rango temporal | BLOCKED | Requiere datos productivos para validar agregaciones. |

---

## 3. Cobertura de máquina de estados

### 3.1 Compra (§4.1 diseño funcional)

**Transiciones válidas**

| # | Origen | Evento | Destino | Estado | Notas |
|---|---|---|---|---|---|
| TC-01 | (∅) | CrearCompra (proveedor activo, ≥1 línea, costo>0, cantidad>0) | Borrador | PASS-CR | E4 verificado. |
| TC-02 | Borrador | EditarCompra | Borrador | PASS-CR | Permitido por guarda. |
| TC-03 | Borrador | Avanzar | EnProceso | PASS-CR | Transición lineal. |
| TC-04 | EnProceso | EditarCompra | EnProceso | PASS-CR | Permitido. |
| TC-05 | EnProceso | Avanzar | Verificada | PASS-CR | Transición lineal. |
| TC-06 | Verificada | Avanzar (Recepcionar) | Recibida | PASS-CR | E4 con pre-validación de todas las líneas + rollback en early-return. |
| TC-07 | * (no terminal) | AdjuntarArchivo (≤5MB válido) | (mismo) | PASS-CR | Acción presente. **Adjunto real BLOCKED**. |

**Transiciones inválidas (deben rechazarse con error claro)**

| # | Origen | Evento | Esperado | Estado | Notas |
|---|---|---|---|---|---|
| TC-INV-01 | Verificada | EditarCompra | "Solo se edita en Borrador o EnProceso" | PASS-CR | Guarda en service. |
| TC-INV-02 | Recibida | EditarCompra / Avanzar | "Compra recibida: solo lectura" | PASS-CR | Guarda + UI sin botones. |
| TC-INV-03 | Verificada | Recepcionar con Rec+Dañ+Dev > Pedida (alguna línea) | "Cantidades de recepción inválidas" + **rollback total** | PASS-CR | E4: validación de TODAS antes de mutar. |
| TC-INV-04 | Borrador | Avanzar a Verificada (saltando EnProceso) | "Transición no permitida" | PASS-CR | Guarda exige Origen = EnProceso. |
| TC-INV-05 | * | AdjuntarArchivo > 5MB o formato inválido | "Archivo inválido (formato o tamaño)" | BLOCKED | Validación presente; requiere subir archivo. |

### 3.2 Venta (§4.2)

**Transiciones válidas**

| # | Origen | Evento | Destino | Estado | Notas |
|---|---|---|---|---|---|
| TV-01 | (∅) | CrearVenta (válida) | Confirmada | PASS-CR | E5, Serializable + retries R4. |
| TV-02 | Confirmada | Anular | Anulada | PASS-CR | Reposición de stock con Movimiento `AnulacionVenta`. |
| TV-03 | Confirmada | MarcarEntregada | Entregada | PASS-CR | Cambio simple de estado. |
| TV-04 | Confirmada/Entregada | EmitirRemito | (mismo) | BLOCKED | PDF requiere descarga real. |
| TV-05 | Confirmada/Entregada | AdjuntarComprobante | (mismo) | BLOCKED | Subida real pendiente. |
| TV-06 | Confirmada/Entregada | RegistrarDevolucion | (mismo) + Devolución asociada | PASS-CR | E6 (delegado a DevolucionService). |

**Transiciones inválidas**

| # | Origen | Evento | Esperado | Estado | Notas |
|---|---|---|---|---|---|
| TV-INV-01 | Entregada | Anular | "Venta entregada: usar Devolución/Cambio" | PASS-CR | Guarda explícita E5. |
| TV-INV-02 | Anulada | * (cualquiera) | "Venta anulada: solo lectura" | PASS-CR | Guarda + UI bloqueada. |
| TV-INV-03 | (∅) | CrearVenta con stock insuficiente | "Stock insuficiente para variante X" + **rollback** | PASS-CR | Early-return con `RollbackAsync` (E5). |
| TV-INV-04 | (∅) | CrearVenta con suma pagos ≠ total | "Suma de pagos ≠ total" | PASS-CR | Validación pre-transacción. |
| TV-INV-05 | (∅) | CrearVenta con Cuotas y CantidadCuotas<2 | "Datos de cuotas inválidos" | PASS-CR | Validación de DataAnnotations + service. |
| TV-INV-06 | Confirmada | Anular bajo deadlock MySQL | Reintento R4 hasta 3, si persiste: "No se pudo confirmar la venta por contención de stock. Reintente." | PASS-CR | E5 (catch DbUpdateException 1213/1205, detach + backoff lineal). **Smoke con concurrencia BLOCKED**. |
| TV-INV-07 | Anulada | EmitirRemito | "Venta anulada: no genera remito" | PASS-CR | Guarda en service. |

### 3.3 Devolución / Cambio (§4.3)

| # | Caso | Estado | Notas |
|---|---|---|---|
| TD-01 | CrearDevolucionDinero válida → Registrada + reingreso stock | PASS-CR | E6, Movimiento `DevolucionCliente`. |
| TD-02 | CrearCambioMismoValor con stock nuevo OK | PASS-CR | Reingreso + decremento atómico (E6). |
| TD-03 | CrearCambioMayorValor con diferencia y medio de pago | PASS-CR | Guarda + persistencia VentaPago de la diferencia. |
| TD-INV-01 | Venta en Borrador/Anulada → "Venta no admite devolución" | PASS-CR | Guarda. |
| TD-INV-02 | CantidadDevolver > (Vendida − DevolucionesPrevias) → "Cantidad supera disponible" + **rollback** | PASS-CR | Early-return con rollback (E6). |
| TD-INV-03 | CambioMismoValor con valores ≠ → "Valores no coinciden" | PASS-CR | Guarda. |
| TD-INV-04 | CambioMayorValor sin medio de pago → "Medio de pago obligatorio" | PASS-CR | Guarda. |
| TD-INV-05 | Item nuevo con stock insuficiente → "Stock insuficiente nuevo" + **rollback** | PASS-CR | E6 G-08. |
| TD-INV-06 | CantidadDevolver < 0 → rechazo defensivo | PASS-CR | Agregado en E6. |
| TD-WIZ | Recorrido completo wizard 4 pasos en navegador | BLOCKED | Requiere ejecución manual. |

### 3.4 Maestros (§4.4)

| # | Caso | Estado |
|---|---|---|
| TM-01 | Inactivar Categoría sin productos → Inactivo | PASS-CR |
| TM-02 | Inactivar Categoría con productos → "Categoría con productos activos" | PASS-CR |
| TM-03 | Inactivar Cliente sin ventas (D5) → Inactivo | PASS-CR |
| TM-04 | Inactivar Cliente con ventas → "Cliente con ventas: no se puede inactivar" | PASS-CR (E1) |
| TM-05 | Inactivar Variante con Stock=0 → Inactivo | PASS-CR |
| TM-06 | Inactivar Variante con Stock>0 → "Variante con stock > 0" | PASS-CR |

### 3.5 Aumento masivo (§4.5)

| # | Caso | Estado | Notas |
|---|---|---|---|
| TA-01 | Previsualizar con %∈(0,500] y filtros válidos → tabla en memoria | PASS-CR | E7. |
| TA-02 | Previsualizar con %≤0 o %>500 → "Parámetros inválidos" | PASS-CR | Validación VM. |
| TA-03 | Aplicar con ≥1 variante → batch update + log AumentoMasivo | PASS-CR | E7. |
| TA-04 | Aplicar sin variantes → "Sin variantes seleccionadas" | PASS-CR | Guarda. |
| TA-05 | **D6/R5**: dos pestañas → 1ª aplica, 2ª recibe "Conflicto de concurrencia: re-previsualice" | PASS-CR | E2: RowVersion + DbUpdateConcurrencyException. **Smoke con dos navegadores BLOCKED**. |

---

## 4. Defectos detectados

> A la fecha del reporte, **0 defectos funcionales** abiertos. Listo defectos potenciales/observaciones detectados durante la revisión.

| # | Severidad | Tipo | Descripción | Capa | Mitigación / Acción |
|---|---|---|---|---|---|
| D-01 | Baja | Observación | El script `M2_AddRowVersionToVariante.sql` documentado para producción usa `DEFAULT (UNHEX(REPLACE(UUID(),'-','')))`, pero EF aplicó directamente `ALTER TABLE ... ADD NOT NULL` sin DEFAULT. Funcionó porque `VariantesProducto` estaba vacía o sql_mode permisivo. | Datos | Si en futuras réplicas la tabla tuviera filas y MySQL en modo strict, el `ADD NOT NULL` sin DEFAULT fallaría. Mantener el script como respaldo. |
| D-02 | Baja | ✅ CERRADO | EF Tools `dotnet ef` no respeta `ASPNETCORE_ENVIRONMENT` en design-time. Mitigado documentando en `docs/MIGRATIONS.md` el uso de `DOTNET_ENVIRONMENT` + `--connection` explícito. |
| D-03 | Media | ✅ CERRADO | `Program.cs` ahora crea `Logs/` con `Directory.CreateDirectory` antes del bootstrap logger; fallback a Console si falla. |
| **D-04** | **Media** | 🔴 **ABIERTO** | **Credenciales productivas en `appsettings.Production.json` (DB + SMTP). Bloqueante go-live (RR-01).** |
| D-05 | Baja | ✅ CERRADO | Rate limit `general` subido de 100 → 300/min con `QueueLimit` 10 para tolerar AJAX intensivo. |
| D-06 | Info | ✅ CERRADO | Despliegue M2 a Prod registrado en `trazabilidad.md` y agregado al historial de `docs/MIGRATIONS.md`. |

**No se detectaron defectos funcionales severos. La cobertura por inspección sumada al cierre por etapa del implementador apoya el gate hacia QA manual con datos.**

---

## 5. Riesgos de release y mitigaciones

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|---|
| RR-01 | **Credenciales en `appsettings.Production.json`** quedan en el repo (D-04) | Alta | Alto (filtración de DB/SMTP) | Mover a User Secrets o variables de entorno. **Bloqueante para go-live**. |
| RR-02 | Concurrencia real D6 (R5) en aumento masivo no probada con dos sesiones simultáneas | Media | Medio (datos inconsistentes si fallara) | Smoke obligatorio con dos navegadores antes de habilitar la opción a usuarios. |
| RR-03 | Concurrencia real R1 (deadlock R4) en VentaService no probada bajo carga | Baja | Alto (venta perdida) | Smoke con script paralelo o JMeter mínimo (opcional). Logs Serilog deben capturar reintentos. |
| RR-04 | Wizard de Devolución (M7) tiene estado JS extenso; nunca probado en navegador con flujo completo | Media | Medio | Smoke completo de los 3 tipos (Dinero / MismoValor / MayorValor) en QA. |
| RR-05 | Generación de PDF QuestPDF y exportación ClosedXML no validadas con datos reales | Media | Bajo | Smoke obligatorio: emitir remito y exportar Excel del resumen semanal. |
| RR-06 | Migración M2 aplicada sin backup pre-cambio documentado | Baja | Alto si hubiera datos | Confirmar con cliente que se cuenta con respaldo automático del hosting. |
| RR-07 | Logs de errores se enrutan a `olvidatasoft@gmail.com` (`Olvidata_ErrorEmail`) — verificar entrega | Media | Bajo | Forzar excepción controlada en QA y verificar mail. |
| RR-08 | Sesión en memoria (no Redis); si se escala horizontalmente, los filtros persistentes se pierden | Baja | Bajo (v1 monoinstancia) | Aceptado para v1; documentado en E8. |

---

## 6. Pruebas mínimas ejecutadas (este pase)

| Categoría | Prueba | Resultado |
|---|---|---|
| Build | `dotnet build` solución completa | ✅ 0 warnings / 0 errors |
| Migraciones | `dotnet ef migrations list` Dev | ✅ 3/3 aplicadas |
| Migraciones | `dotnet ef database update` Local Dev | ✅ M2 aplicada |
| Migraciones | `dotnet ef migrations list --connection` Prod | ✅ 3/3 aplicadas (M2 confirmada) |
| Migraciones | `dotnet ef database update --connection` Prod | ✅ M2 aplicada sin errores |
| Inspección | Revisión cruzada de criterios M1–M9 + Dashboard contra cierres E0–E8 | ✅ Sin gaps funcionales |
| Inspección | Recorrido transiciones válidas e inválidas §4.1–§4.5 | ✅ Cubiertas por código + guards |

### 6.1 Pruebas mínimas pendientes (a ejecutar por QA humano antes del gate de cliente)

**M1 Smoke**
- [ ] Login con SuperUsuario / Administrador / Vendedor → sidebar correcto cada uno.
- [ ] Vendedor a `/Usuarios` → 403.

**M5 Smoke**
- [ ] Crear compra Borrador → EnProceso → Verificada → Recibir con `Rec+Dañ+Dev` válido.
- [ ] Forzar línea con `Rec+Dañ+Dev > Pedida` → error y compra sigue en Verificada (rollback).
- [ ] Verificar `UltimoPrecioCompra` se actualizó.
- [ ] Adjuntar PDF ≤5MB OK; .exe → rechazado.

**M6 Smoke ⭐**
- [ ] Venta con 1 línea + 1 medio Efectivo → Confirmada, stock decrementado.
- [ ] Venta con stock insuficiente → error, sin movimientos.
- [ ] Venta con suma pagos ≠ total → error.
- [ ] Anular Confirmada → stock repuesto.
- [ ] Intentar anular Entregada → error.
- [ ] Generar remito PDF → descarga válida.
- [ ] Vendedor crea venta sin ver costos.
- [ ] Concurrencia: dos sesiones vendiendo última unidad → solo 1 confirma, otra recibe stock insuficiente o reintento.

**M7 Smoke (Wizard)**
- [ ] Devolución Dinero completa → stock reingresado, motivo guardado.
- [ ] Cambio MismoValor con stock destino OK → atómico.
- [ ] Cambio MayorValor → diferencia + medio de pago registrado.
- [ ] Cantidad > disponible → bloqueo en paso 2 + revalidación en paso 4.

**M8/M9 Smoke**
- [ ] Resumen semanal con fecha en miércoles → ventana lunes-domingo correcta.
- [ ] Export Excel descarga `.xlsx` legible con totales.
- [ ] Aumento masivo dos pestañas concurrentes → 2da pide re-previsualizar.

**Dashboard**
- [ ] Admin ve 5 indicadores; Vendedor ve solo ventas propias del día.

**Hardening (E8)**
- [ ] 11 logins/min misma IP → 429.
- [ ] Header `Strict-Transport-Security` presente en producción HTTPS.
- [ ] Forzar excepción y verificar mail de error a `olvidatasoft@gmail.com`.

---

## 7. Checklist de salida QA — Gate hacia documentación al cliente

```
QA — CHECKLIST DE SALIDA (Gate cliente)
────────────────────────────────────────────────────────────────────
[✓] Cobertura por criterio de aceptación documentada (M1–M9 + Dashboard)
[✓] Cobertura de transiciones válidas e inválidas (§4.1–§4.5)
[✓] Defectos clasificados por severidad (0 críticos, 0 funcionales abiertos)
[✓] Riesgos de release identificados con mitigación
[✓] Build verde Dev y Prod
[✓] Migraciones M1+M2 aplicadas en Dev y Prod
[ ] Smoke funcional M1, M5, M6, M7, M8, M9, Dashboard ejecutado por QA humano
[ ] Concurrencia D6 (Aumento masivo) verificada con dos navegadores
[ ] PDF Remito y Excel Resumen Semanal validados con datos reales
[ ] Adjuntos compras/ventas validados con archivos reales (límite 5MB + formato)
[ ] **RR-01: credenciales productivas migradas fuera de appsettings.Production.json**
[ ] Mail de error a olvidatasoft@gmail.com verificado
[ ] Logs Serilog rotando correctamente en Prod
────────────────────────────────────────────────────────────────────
```

### Resolución del gate

**Estado**: 🟡 **APROBADO TÉCNICAMENTE — APROBACIÓN CONDICIONAL para documentación al cliente.**

- ✅ La revisión estática + cierre del implementador + build verde + migraciones aplicadas en Prod permiten declarar **el sistema funcionalmente completo** y sin defectos críticos detectados.
- ⚠️ **Bloqueantes para go-live productivo (no para documentación al cliente)**:
  - **RR-01** (credenciales en repo) debe resolverse antes del despliegue público.
  - Smoke funcional manual de M6 y M7 debe ejecutarse antes de exponer a usuarios reales.
- ✅ Se puede **iniciar redacción del documento de alcance al cliente** en paralelo, siempre que se aclare que las pruebas finales con datos productivos están pendientes.

**Recomendación al orquestador**: avanzar a la etapa de documentación al cliente **en modo borrador**, reservando la firma final del entregable hasta cerrar los items pendientes del checklist §7.

---

## 8. Memoria acumulativa

- **2026-01-15** — QA inicial v1.0. Cobertura por inspección + cierre del implementador. 0 defectos funcionales, 6 observaciones. Gate aprobado **condicional** para iniciar documentación al cliente en modo borrador.
- **2026-01-15** — QA v1.1. Cierre de defectos D-02 (runbook `docs/MIGRATIONS.md`), D-03 (creación defensiva de `Logs/` en `Program.cs`), D-05 (rate limit general 100→300/min), D-06 (entrada de despliegue M2 en trazabilidad). Build verde. Quedan 0 defectos abiertos no críticos. **D-04 / RR-01 sigue abierto** y continúa siendo el único bloqueante de go-live productivo.
- **2026-07-02** — QA puntual V9 (fast-path redirect post-ajuste de stock). Alcance acotado: `StockController.Ajuste(AjusteStockViewModel vm)` [POST] cambia `RedirectToAction(nameof(Index))` → `RedirectToAction(nameof(Ajuste))`. Verificado por inspección exhaustiva de código (controller completo, `StockService.AjusteManualAsync` sin diff, vista `Ajuste.cshtml`, `_Layout.cshtml` con manejo global de `TempData["Success"]`/`TempData["Error"]` vía SweetAlert2) + build verde (0/0). Diff aplicado coincide 100% con lo documentado en `5-implementador.md` (V9) y `3-arquitecto-mvc.md` (V9). **5/5 criterios PASS, 0 defectos.** No se re-ejecutó la regresión completa del proyecto (fuera de alcance del pedido); del catálogo cross-proyecto ningún item aplica directamente a este cambio (ninguno cubre redirect post-POST en Stock). Ver detalle en sección "V9" más abajo.
- **2026-07-30** — QA V10 (carga masiva de stock por Marca + filtros completos en Consulta de Stock). Verificado por inspección exhaustiva de código + `git diff` (cambios aún no commiteados: `StockService.cs`, `StockController.cs`, `IStockService.cs`, `StockViewModels.cs`, `Stock/Index.cshtml`, `Stock/CargaMasiva.cshtml` nuevo, `EstadoStockFiltro.cs` nuevo) + build propio verde (0/0). **13/13 criterios de aceptación (HU-M1–M3, HU-B1–B2) PASS.** DD-1 (atomicidad total + errores por fila + no pérdida de datos tipeados) confirmado por lectura de código: `GuardarCargaMasivaAsync` hace una pasada de validación 100% de solo lectura antes de abrir cualquier transacción, y la pasada de escritura hace rollback total ante el primer fallo. R-V10-1 confirmado por `git diff`: `AplicarAjusteInternoAsync` es una extracción literal (copy-paste) de la lógica previa de `AjusteManualAsync` sin ningún cambio de comportamiento, y `AjusteManualAsync` público queda como envoltorio transaccional idéntico al original. R-V10-2 confirmado (bloqueo de alta para Modelo sin Producto, con el mensaje exacto pedido por el cliente, sin afectar el resto del lote). 0 defectos funcionales encontrados; 2 observaciones menores (no bloqueantes, sin auto-fix aplicado por no ser bugs reproducibles): filtro Talle en `/Stock/Index` no se limita a talles con stock real para ese Modelo (a diferencia de Color, que sí); ausencia de índice único en BD para Color+TalleConfigId por Producto (riesgo preexistente a V10, no introducido por esta feature). Del catálogo cross-proyecto, REG-001 (RowVersion MySQL) y REG-002 (Stock inicial en alta de variante) aplican indirectamente (V10 reutiliza `VarianteService.CrearAsync`) y ambos PASS sin regresión. Ver detalle completo en sección "V10" más abajo.
- **2026-08-16** — **Barrido QA del fast-path acumulado `d8a71ef..f400671`** (11 commits desde el QA de V10, ninguno con gate QA previo, todos ya desplegados a producción). Verificado por inspección exhaustiva de código sobre el diff completo (31 archivos, +1615/-287) leyendo los archivos enteros, más build propio verde (0/0). **Verificación automatizada por navegador NO disponible en esta sesión** (MCP `playwright` declarado en `.mcp.json` pero sin herramientas expuestas) — declarado explícitamente conforme a la instrucción 33 y suplido con guía manual. **18/22 criterios PASS, 3 FAIL, 1 PASS con reserva.** **4 defectos: 2 de severidad Alta (bloqueantes, en producción) y 2 Media.** D-01: `/Stock/MatrizEditar` no guarda **nada** cuando hay celdas "—" vacías, porque `StockMatrizAltaGuardarViewModel.CantidadNueva/PrecioVenta/StockMinimo` son tipos de valor **no nullables** y la vista los renderiza vacíos → error de model binding → `!ModelState.IsValid`; es una **regresión de `f400671`** sobre la edición por celda que ya funcionaba. D-02: el input de Precio por fila se renderiza vacío bajo cultura `es-AR` (coma decimal inválida para `input type=number`) y la sincronización JS del submit copia ese vacío sobre el hidden correcto, bloqueando el POST por segunda vía independiente. D-03: el *change tracker* compartido entre las transacciones por fila de `GuardarCargaMasivaAsync`/`GuardarMatrizAsync` puede persistir una fila informada como fallida dentro de la transacción de la fila siguiente (o envenenar el resto del lote). D-04: el combo Talle de `/Stock/Index` no desambigua Brasilero/Argentino (única vista que quedó sin el fix de `06bb253`), latente hasta que se cargue el catálogo argentino. 7 observaciones menores (OBS-01 a OBS-07). **Sin auto-fix aplicado por instrucción explícita del solicitante** (reportar sin parchear); sí se catalogó **SG-001** en `regresiones-manuales.yml`. Confirmado por inspección que **no** hay variantes huérfanas ante fallo del stock inicial, que los permisos son correctos, y que `/Stock/Ajuste` y `/Variantes/Crear` no sufrieron regresión (`VarianteService.cs` sin diff). **Veredicto: RECHAZADO** — 8 de 11 commits aptos; el rechazo se concentra en `f400671`, que debe tratarse como hotfix. Ver detalle en la sección "Barrido QA post-V10" al final del documento.

---

## V9 — Redirect post-ajuste de stock (2026-07-02)

**Fuente:** `1-analista-funcional.md` (sección V9), `3-arquitecto-mvc.md` (sección V9), `5-implementador.md` (entrada V9).

**Alcance QA:** cambio puntual de una línea en `StockController.cs`, sin regresión completa (a pedido explícito). Verificación por inspección de código + build, sin ejecución en navegador (no requerida: el cambio es de flujo HTTP puro, sin lógica condicional ni dependencia de datos/JS de estado).

### Cobertura por criterio de aceptación

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| 1 | Ajuste válido (Admin) → permanece en `Stock/Ajuste` (no `Index`), `TempData["Success"]` visible | PASS | `StockController.cs:84` `return RedirectToAction(nameof(Ajuste))`; `_Layout.cshtml:303-313` renderiza SweetAlert2 con `TempData["Success"]` en cualquier vista tras el redirect. |
| 2 | Se puede cargar un segundo ajuste inmediatamente sin renavegar | PASS | El GET `Ajuste(int? varianteId = null)` (línea 64-70) construye `new AjusteStockViewModel()` en cada request; el redirect es un GET fresco, formulario queda limpio. Select2 de variante se reinicializa en `Scripts` de `Ajuste.cshtml`. |
| 3 | Ajuste inválido (ModelState o error de negocio) sigue devolviendo vista `Ajuste` con errores, sin cambios | PASS | Líneas 76 y 82 del controller sin diff: `if (!ModelState.IsValid) return View(vm);` y `if (!result.Success) { ModelState.AddModelError(...); return View(vm); }` — intactas. |
| 4 | `CargaInicial` sigue redirigiendo a `Index` sin cambios | PASS | Línea 60: `return RedirectToAction(nameof(Index));` sin modificar. `git diff` confirma que solo la línea 84 (dentro de `Ajuste` POST) cambió. |
| 5 | Build verde + diff coincide con lo documentado | PASS | `dotnet build ShowroomGriffin.slnx` → "Compilación correcta. 0 Advertencia(s), 0 Errores." `git diff` de una sola línea, idéntico al descripto en `5-implementador.md` V9 y `3-arquitecto-mvc.md` V9. `StockService.cs` sin diff (capa de negocio no tocada, confirmado con `git status`). |

### Cobertura de máquina de estados

No aplica — el cambio no altera transiciones de estado de ninguna entidad (Venta, Compra, Devolución). Es un cambio de navegación (redirect target) dentro de una única acción sin máquina de estados propia.

### Cobertura del catálogo cross-proyecto (regresiones-manuales.yml)

| id | aplica | resultado | acción |
|---|---|---|---|
| REG-001 | no | N/A | RowVersion en variantes — no tocado por este cambio. |
| REG-002 | no | N/A | Stock inicial en variantes — módulo distinto (`CargaInicial`, no tocado). |
| REG-003 | no | N/A | Autocomplete Compras — no relacionado. |
| REG-004 | no | N/A | Máquina de estados de Compra — no relacionado. |
| REG-005 | no | N/A | Autocomplete Ventas — no relacionado. |
| REG-006 | no | N/A | Medio de pago Cuotas — no relacionado. |
| REG-007 | no | N/A | Autocomplete Devoluciones — no relacionado. |
| REG-008 | no | N/A | Foco de input en pagos — no relacionado. |
| REG-009 | no | N/A | Cascada AumentoMasivo — no relacionado. |
| REG-010 | no | N/A | Visibilidad menú Auditoría — no relacionado. |

Ningún item del catálogo cubre el patrón "redirect post-POST en Stock/Ajuste"; no se detectó bug reproducible que amerite alta de nuevo item. No se ejecutó el catálogo completo en este pase por ser QA puntual de alcance acotado (a pedido explícito); queda pendiente en la próxima regresión completa del proyecto.

### Defectos detectados

Ninguno.

### Auto-fixes aplicados

No aplica — no se reprodujo ningún defecto.

### Riesgos de liberación y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Verificación sin ejecución real en navegador | Baja | Bajo | El cambio es de flujo HTTP puro (redirect target), sin JS de estado ni dependencia de datos; la inspección de código + build cubre el 100% del comportamiento. Si se desea, un smoke manual de 1 minuto (cargar 2 ajustes seguidos) cierra el gap residual antes de producción. |
| Regresión completa del proyecto no re-ejecutada | Baja | Bajo | Cambio acotado a una línea sin impacto en Domain/Application/Infrastructure; confirmado que `StockService.cs` no tiene diff. Recomendado incluir en el próximo smoke completo (M4 Stock) del checklist pendiente en la sección 6 de este documento. |

### Pruebas mínimas ejecutadas

- Lectura completa de `StockController.cs` (controller entero, no solo el diff).
- `git diff` de `StockController.cs` — confirmado cambio de una sola línea.
- `git status` — confirmado que `StockService.cs` (Infrastructure) no tiene cambios pendientes.
- Lectura de `Views/Stock/Ajuste.cshtml` — confirmado formulario sin lógica condicional por origen de navegación.
- Lectura de `Views/Shared/_Layout.cshtml` — confirmado manejo global de `TempData["Success"]`/`TempData["Error"]` con SweetAlert2.
- `dotnet build ShowroomGriffin.slnx` — build verde, 0 warnings, 0 errores.
- Comparación línea por línea del diff aplicado contra lo documentado en `3-arquitecto-mvc.md` (V9) y `5-implementador.md` (V9) — coincidencia exacta.

### Checklist de salida para merge

```
[x] Diff coincide exactamente con lo documentado (implementador + arquitecto)
[x] Build verde (0 warnings, 0 errores)
[x] Sin migración EF (confirmado, no aplica)
[x] Sin cambios en permisos (RequireAdministrador intacto en Ajuste; RequireAdministrador intacto en CargaInicial)
[x] Sin cambios en validaciones (ModelState y result.Success guards intactos)
[x] Capa de negocio (StockService, AjusteManualAsync) sin diff
[x] Vista Ajuste.cshtml y _Layout.cshtml revisadas — TempData["Success"] se muestra correctamente vía SweetAlert2
[x] CargaInicial no afectado — sigue redirigiendo a Index
[ ] Smoke manual opcional en navegador (no bloqueante, cambio de bajo riesgo)
```

**Veredicto: APROBADO** — sin observaciones bloqueantes. Cambio de bajo riesgo, acotado a una línea, sin impacto en otras capas. Listo para merge.

---

## V10 — Carga masiva de stock por Marca + filtros completos en Consulta de Stock (2026-07-30)

**Fuente:** `1-analista-funcional.md` (sección V10, Q1–Q7 confirmadas), `2-disenador-funcional.md` (sección V10, DD-1 resuelto), `3-arquitecto-mvc.md` (sección V10, R-V10-1/R-V10-2 resueltos), `5-implementador.md` (entrada V10, incluye desvío documentado sobre `AjusteManual` vs `CargaInicial`).

**Alcance QA:** feature completa nueva (pantalla `/Stock/CargaMasiva` + filtros Talle/Estado en `/Stock/Index`). Verificación por **inspección de código exhaustiva** (líneas completas de Controller/Service/Views, no solo el diff) + `git diff` de los archivos aún no commiteados (working tree tenía cambios pendientes de un ciclo previo del Implementador) + build propio (`dotnet build ShowroomGriffin.slnx`, 0/0). No se ejecutó la app en navegador (fuera de las herramientas disponibles para el agente QA y de la regla de no automatizar UI); las verificaciones dependientes de ejecución real quedan como guía de pasos para el cliente.

### Cobertura por criterio de aceptación (Historias de Usuario)

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| HU-M1.AC1 | Al elegir una Marca veo todas sus variantes existentes agrupadas por Modelo, con stock actual y cantidad nueva editable | PASS-CR | `StockService.ObtenerParaCargaMasivaAsync` (líneas 326-385) agrupa por `Modelo` de la Marca, toma el primer `Producto` activo y arma `Filas` con `StockActual`/`CantidadNueva` precargados; `CargaMasiva.cshtml` renderiza un acordeón por Modelo. |
| HU-M1.AC2 | Puedo editar cualquier subconjunto de filas sin completar todas | PASS-CR | `GuardarCargaMasivaAsync` solo marca `huboCambios=true` para filas con `CantidadNueva != StockActual`; filas sin cambio no generan `AjusteStock`/`MovimientoStock` (líneas 425-436, 547). |
| HU-M1.AC3 | Un único botón guarda todas las filas modificadas en una sola operación | PASS-CR | Un solo `POST CargaMasiva` → `GuardarCargaMasivaAsync` procesa todo `vm.Modelos[].Filas[]` en una única transacción (líneas 506-577). |
| HU-M2.AC1 | Sección de Modelo con "+ Agregar variante nueva" pidiendo Color, Talle, Precio de Venta, Stock Mínimo y Cantidad inicial | PASS-CR | `CargaMasiva.cshtml` líneas 138-160 (columnas editables solo si `esNueva`) + JS `btn-agregar-variante` (líneas 270-295) genera la fila con los 4 campos. |
| HU-M2.AC2 | No se puede crear una combinación Color+Talle que ya existe para ese Modelo/Producto | PASS-CR | `GuardarCargaMasivaAsync` pasada 1: valida contra `combinacionesExistentes` (variantes ya persistidas del mismo `ProductoId`) **y** contra `combosEnEsteLote` (duplicados dentro del mismo submit) — líneas 402-490. |
| HU-M2.AC3 | Al guardar el lote, la variante nueva queda creada con esos datos y el stock inicial cargado | PASS-CR | Pasada 2: `IVarianteService.CrearAsync` (reutilizado) crea `VarianteProducto`+`Stock(0)`; inmediatamente después `AplicarAjusteInternoAsync` aplica la `CantidadNueva` cargada por el usuario, dentro de la misma transacción (líneas 515-545). Confirmado por lectura de `VarianteService.CrearAsync` (líneas 24-59): con `StockInicial=null` no abre transacción propia (`CargaInicialAsync` no se invoca), evitando el anidamiento. |
| HU-M3.AC1 | Si alguna fila tiene error, no se persiste ninguna fila del lote y se muestran los errores puntuales por fila | PASS-CR | Pasada 1 es 100% de solo lectura (no hay ningún `SaveChangesAsync`/`BeginTransactionAsync` antes de la línea 496); si `erroresGlobales.Count > 0` retorna sin abrir transacción. En la pasada 2 (escritura), cualquier fallo hace `tx.RollbackAsync()` antes de retornar (líneas 536-540, 558-563, 573-577) — no hay compromiso parcial en ningún camino de error. `fila.Error` queda seteado en el objeto vm devuelto, que el Controller re-renderiza tal cual (`return View(vm)` en ambos casos: `ModelState` inválido y `result.Success=false`, líneas 131-146 de `StockController.cs`), preservando todos los valores tipeados en las demás filas (los inputs usan `asp-for` sobre el mismo `vm` posteado, no un modelo nuevo). |
| HU-B1.AC1 | Combo Talle se habilita al elegir Modelo y filtra la grilla server-side sin recargar | PASS-CR | `Stock/Index.cshtml` línea 230-250: `$('#filModelo').change()` puebla `#filTalle` vía `GET /Modelos/TallesPorModelo` y `reloadTable()` recarga el DataTable vía AJAX (`ListarAsync` con `talleConfigId`, `StockService.cs` líneas 53-54). |
| HU-B2.AC1 | Combo Estado reemplaza al botón "Solo alertas" y se combina con el resto de los filtros | PASS-CR | Botón "Solo alertas" removido del diff de `Index.cshtml` (confirmado por `git diff`); combo `#filEstado` incluido en `getFilters()`/`buildAjaxUrl()` junto a Marca/Modelo/Talle/Color; `StockService.ListarAsync` aplica el filtro `estado` con `switch` (Bajo/Límite/OK/Todos, líneas 58-65) sobre la misma query ya filtrada por los demás combos. |
| HU-B2.AC2 | El link directo `?soloAlertas=true` sigue funcionando, precargando Estado=Bajo | PASS-CR | `StockController.Index` (línea 37): `ViewBag.EstadoInicial = (int)(soloAlertas ? EstadoStockFiltro.Bajo : EstadoStockFiltro.Todos)`; la vista hace `$('#filEstado').val('@estadoInicial')` **antes** de inicializar el DataTable (línea 113, se ejecuta antes de la línea 135), por lo que el primer `ajax.url()` ya incluye `estado=3`. |
| Permisos | `CargaMasiva` GET/POST con `RequireAdministrador`; `Index`/`Listar`/`ExportarExcel` con `RequireEmpleado` | PASS-CR | `StockController.cs`: clase con `[Authorize(Policy = "RequireEmpleado")]` (línea 17), `CargaMasiva` GET (línea 109) y POST (línea 125) con override explícito `[Authorize(Policy = "RequireAdministrador")]`, igual que `Ajuste`/`CargaInicial` preexistentes. |
| Regresión | `/Stock/Ajuste` (individual) sin cambio de comportamiento externo tras el refactor | PASS-CR | `git diff` de `StockService.cs` muestra que `AjusteManualAsync` es una extracción literal: el cuerpo que antes estaba inline ahora vive en `AplicarAjusteInternoAsync` sin ningún cambio de líneas de lógica (mismo orden de creación de `AjusteStock`, mismo cálculo de `anterior`, mismo `RegistrarMovimientoAsync`); el wrapper público abre la misma transacción externa y hace el mismo commit/rollback que antes. |
| Regresión | `/Stock/CargaInicial` (individual) sin cambio | PASS-CR | `CargaInicialAsync` no aparece en el diff de V10 (sin cambios); `VarianteService.CrearAsync` solo invoca `CargaInicialAsync` cuando `StockInicial.HasValue && > 0`, camino que V10 nunca ejercita (pasa `StockInicial = null` a propósito). |

**13/13 criterios PASS.** 0 FAIL. 0 BLOCKED (todos los puntos de riesgo señalados por el orquestador se pudieron cerrar por inspección de código + `git diff`, sin necesitar ejecución real).

### Cobertura de máquina de estados

No aplica — confirmado en `2-disenador-funcional.md` §V10.4: se reutilizan los flujos existentes de `AjusteStock`/`MovimientoStock` (sin estados propios) y el alta de `VarianteProducto` no tiene máquina de estados (entidad simple con soft delete). No hay transiciones que recorrer.

### Cobertura del catálogo cross-proyecto (`regresiones-manuales.yml`)

| id | aplica | resultado | acción |
|---|---|---|---|
| REG-001 (RowVersion MySQL en creación de variante) | sí | PASS | `AppDbContext.cs` línea 191 sigue asignando `variante.RowVersion = Guid.NewGuid().ToByteArray()` manualmente en el override de `SaveChanges`. V10 reutiliza `VarianteService.CrearAsync` sin tocarlo — las variantes nuevas creadas desde Carga Masiva pasan por el mismo mecanismo, sin riesgo de `DbUpdateException`. |
| REG-002 (Stock inicial al crear/editar variante) | sí (relacionado, no exacto) | PASS | El mecanismo de `StockInicial` en `VarianteViewModel`/`VarianteService.CrearAsync` permanece intacto; V10 lo reutiliza pasando `StockInicial = null` a propósito (para no anidar la transacción de `CargaInicialAsync`) y aplica la cantidad inicial vía `AplicarAjusteInternoAsync` en su lugar. El flujo original de `/Variantes/Crear` con `StockInicial > 0` no fue modificado. |
| REG-003 (Autocomplete Compras) | no | N/A | Módulo no tocado por V10. |
| REG-004 (Máquina de estados Compra) | no | N/A | Módulo no tocado por V10. |
| REG-005 (Autocomplete Ventas) | no | N/A | Módulo no tocado por V10. |
| REG-006 (Medio de pago Cuotas) | no | N/A | Módulo no tocado por V10. |
| REG-007 (Autocomplete Devoluciones) | no | N/A | Módulo no tocado por V10. |
| REG-008 (Foco de input en pagos) | no | N/A | Módulo no tocado por V10. `CargaMasiva.cshtml` no re-renderiza filas existentes en cada keystroke (solo agrega/quita filas nuevas vía botón), por lo que el patrón de pérdida de foco de REG-008 no aplica a esta pantalla. |
| REG-009 (Cascada AumentoMasivo) | no | N/A | Módulo no tocado; aunque comparte el patrón de cascada AJAX, `Marcas/PorCategoria` y `Modelos/PorMarca`/`TallesPorModelo` ya usan querystring (no segmento posicional), sin el bug de REG-009. |
| REG-010 (Menú Auditoría por rol) | no | N/A | Módulo no tocado por V10. |
| KOI-001 (botón Swal fuera del form) | no | N/A | Proyecto distinto (KoiDumplings); además el patrón de `CargaMasiva.cshtml` es diferente: el botón "Guardar todo el lote" está `type="submit"` **dentro** del `<form>`, y el handler intercepta el evento `submit` nativo del form (`$('#formCargaMasiva').on('submit', ...)`), no un click en un botón externo — el patrón que causaba KOI-001 no está presente. |
| KOI-002 a KOI-006, DN-001 y siguientes | no | N/A | Proyectos distintos (KoiDumplings, DeliciasNaturales), sin módulo equivalente tocado por V10. |

### Defectos detectados

**0 defectos funcionales (bugs reproducibles) encontrados.** 2 observaciones menores, no bloqueantes, sin auto-fix aplicado (no son bugs, son desviaciones de UX/robustez de bajo impacto — no se "adivinó" ningún parche de negocio nuevo):

| # | Severidad | Descripción | Recomendación |
|---|---|---|---|
| OBS-V10-01 | Minor (observación) | El combo Talle de `/Stock/Index` (RN-B1) reutiliza `ModelosController.TallesPorModelo` → `ModeloService.ObtenerTallesPorModeloAsync`, que devuelve el **catálogo completo** de `TalleConfig` para el `TipoTalle` del Modelo, no solo los talles que efectivamente tienen variantes/stock cargado para ese Modelo — a diferencia del combo Color (`Variantes/api/Colores`), que sí filtra a valores realmente usados (`Distinct()` sobre variantes existentes). El diseño (`2-disenador-funcional.md` WF-B1) pedía "mismo patrón que Color". Efecto observable: el usuario puede elegir un Talle sin ninguna variante cargada para ese Modelo y obtener una grilla vacía — funcionalmente correcto (no rompe nada), pero inconsistente con el comportamiento de Color. | No bloqueante para este release. Si se quiere alinear estrictamente con el diseño, crear un método análogo a `ObtenerColoresAsync` mockeado por Talle (`SELECT DISTINCT TalleConfigId` de variantes del Modelo) — cambio menor de Infrastructure, sin impacto en Domain/migraciones. |
| OBS-V10-02 | Minor (riesgo residual, preexistente) | No existe índice único en base de datos para `(ProductoId, Color, TalleConfigId)` en `VarianteProducto` (solo `CodigoBarra` tiene `HasIndex().IsUnique()`). La validación de duplicados de RN-M2 es 100% aplicativa (2 pasadas en memoria dentro de `GuardarCargaMasivaAsync`), sin constraint de base que la respalde. Esto ya era así antes de V10 para `/Variantes/Crear` individual (no es una regresión introducida por esta feature), pero la pantalla de Carga Masiva facilita altas más frecuentes, exponiendo más la ventana de una eventual condición de carrera entre dos sesiones administrativas simultáneas (Pasada 1 de lectura vs. Pasada 2 de escritura, o dos "Carga Masiva" concurrentes sobre la misma Marca). | No bloqueante (el uso típico de este comercio es un único administrador operando la carga de stock). Si se quiere blindar a futuro, agregar índice único filtrado `(ProductoId, Color, TalleConfigId) WHERE DeletedAt IS NULL` en una migración EF dedicada — fuera de alcance de V10 (el Analisis/Arquitectura no lo pidieron y no hay migración EF en este release). |

### Auto-fixes aplicados

Ninguno. No se reprodujo ningún defecto funcional que ameritara parche; las 2 observaciones de arriba son mejoras de robustez/UX de bajo impacto, no bugs, por lo que aplicar un "fix" sin pedido explícito violaría la regla de no introducir lógica de negocio nueva no solicitada.

### Riesgos de liberación y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Cambios aún no commiteados al momento de este QA (`git status` mostró 5 archivos modificados + 2 nuevos sin commit) | — | — | Confirmar que el commit se haga antes de desplegar; este reporte QA fue hecho sobre el working tree real, no sobre un commit anterior. |
| Sin ejecución real en navegador (grilla dinámica con JS de indexado de filas, acordeón, SweetAlert2) | Media | Bajo-Medio | El mecanismo de renumerado de índices (`renumerarFilasNuevas`) es la pieza más frágil de la vista (si fallara, el model binder de ASP.NET Core silenciosamente dejaría de bindear filas con índice faltante). Recomendado smoke manual: agregar 2-3 variantes nuevas en distintos Modelos, quitar una del medio, y confirmar que las 2 restantes se guardan igual. Ver guía de pasos abajo. |
| Movimiento de stock inicial de variantes nuevas creadas por Carga Masiva queda registrado como `TipoMovimiento.AjusteManual` en vez de `CargaInicial` (desvío documentado por el Implementador) | Baja | Bajo | Es una decisión técnica deliberada y documentada (evita anidar transacciones sin tocar `CargaInicialAsync` en producción). Efecto solo informativo en el historial de movimientos (`Stock/Historial`), no afecta el cálculo de `StockActual`. Si el cliente reporta confusión al ver "Ajuste Manual" en vez de "Carga Inicial" para una variante recién creada por lote, es un cambio cosmético de bajo esfuerzo (no requiere tocar la lógica). |
| OBS-V10-01 y OBS-V10-02 (ver tabla de defectos) | Baja | Bajo | Ver recomendaciones en la tabla de defectos. No bloqueantes. |
| Volumen de variantes por Marca no paginado (acordeón Bootstrap simple) | Baja | Bajo | Aceptado explícitamente en Diseño (DD-2) para el volumen típico de este comercio. |

### Pruebas mínimas ejecutadas (este pase — por inspección, sin navegador)

- `dotnet build ShowroomGriffin.slnx` → Compilación correcta, 0 Advertencia(s), 0 Errores (verificado de forma independiente por este agente QA, no solo tomado del reporte del Implementador).
- `git status` + `git diff --stat` + `git diff` completo de los 5 archivos modificados → confirmado que el diff real coincide con lo documentado en `5-implementador.md` V10, sin cambios no documentados.
- Lectura línea por línea de `StockService.cs` completo (no solo el diff): `ListarAsync`, `AjusteManualAsync`, `AplicarAjusteInternoAsync`, `ExportarExcelAsync`, `ObtenerParaCargaMasivaAsync`, `GuardarCargaMasivaAsync`.
- Lectura línea por línea de `StockController.cs` completo: permisos por acción, re-render de `View(vm)` en ambos caminos de error de `CargaMasiva` POST.
- Lectura línea por línea de `CargaMasiva.cshtml` y del delta de `Index.cshtml`: binding de filas dinámicas, renumerado de índices, deep-link `?soloAlertas=true`, cascada de filtros.
- Verificación cruzada de endpoints referenciados por las vistas (`Marcas/PorCategoria`, `Modelos/PorMarca`, `Modelos/TallesPorModelo`, `Variantes/api/Colores`) contra sus controllers reales — todos existen y con la policy esperada (`RequireEmpleado`).
- Verificación de `VarianteService.CrearAsync` (no modificado por V10) para confirmar que `StockInicial = null` no dispara `CargaInicialAsync` (evita la transacción anidada).
- Verificación de `AppDbContext.SaveChanges` (asignación manual de `RowVersion`, REG-001) y de la ausencia de índice único Color+TalleConfigId (OBS-V10-02).
- Verificación de `DependencyInjection.cs`: `IStockService`/`IVarianteService`/`ITalleConfigService`/`ICategoriaService` registrados como Scoped, sin necesitar registro nuevo para el `IServiceProvider` inyectado en `StockService`.

### Guía de pasos para prueba manual del cliente (pendiente de ejecución real)

Adaptada de `5-implementador.md` §"Pruebas mínimas requeridas para QA" (no re-ejecutada por este agente por no automatizar UI):

1. Como Admin, ir a `/Stock/CargaMasiva`, elegir una Marca con variantes existentes → verificar grilla agrupada por Modelo con stock actual correcto.
2. Modificar la "Cantidad nueva" de 2-3 variantes existentes de distintos Modelos + completar Motivo → guardar → verificar en `/Stock/Historial` que se generaron movimientos `AjusteManual` solo para las filas modificadas.
3. Agregar una variante nueva (Color+Talle+Precio+Stock Mínimo+Cantidad inicial) en un Modelo con Producto asociado → guardar → verificar que la `VarianteProducto` se crea con esos datos y el stock inicial queda cargado.
4. Intentar dar de alta una combinación Color+Talle ya existente para el mismo Producto → verificar que el lote completo NO se guarda (ninguna fila, ni las válidas) y que el error se muestra en la fila puntual sin perder el resto de lo tipeado.
5. Verificar que un Modelo sin Producto asociado muestra el mensaje "Este modelo no tiene un Producto asociado — crear uno primero desde Productos" y no ofrece "+ Agregar variante nueva", mientras el resto del lote (otros Modelos) se guarda igual.
6. Agregar 2-3 filas nuevas en un mismo Modelo, quitar la del medio con el botón "Quitar", y guardar — verificar que las 2 restantes se persisten correctamente (smoke del renumerado de índices JS).
7. Verificar regresión: `/Stock/Ajuste` (ajuste individual) sigue funcionando exactamente igual que antes.
8. Verificar regresión: `/Variantes/Crear` con Stock Inicial > 0 sigue funcionando igual que antes (no afectado por V10).
9. `/Stock/Index`: elegir Modelo → verificar que el combo Talle se habilita y filtra la grilla vía AJAX sin recargar la página.
10. `/Stock/Index`: combo Estado en Bajo/Límite/OK/Todos → verificar que filtra correctamente según `StockActual` vs `StockMinimo`.
11. Acceder a `/Stock/Index?soloAlertas=true` (link del Dashboard) → verificar que el combo Estado se precarga en "Bajo".
12. Exportar Excel desde `/Stock/Index` con Talle y Estado aplicados → verificar que el archivo respeta los mismos filtros que la grilla.
13. Como Vendedor/Empleado, intentar acceder directamente a `/Stock/CargaMasiva` → debe dar 403.

### Checklist de salida para merge

```
[x] Diff coincide exactamente con lo documentado (implementador + arquitecto + diseñador)
[x] Build verde (0 warnings, 0 errores) — verificado independientemente por QA
[x] Sin migración EF (confirmado — no aplica, entidades ya existían)
[x] Permiso RequireAdministrador en CargaMasiva GET/POST; RequireEmpleado en Index/Listar/ExportarExcel
[x] DD-1 (atomicidad total + errores por fila + no pérdida de datos tipeados) verificado por código
[x] R-V10-1 (sin transacción anidada) verificado por git diff — AjusteManualAsync sin cambio de comportamiento externo
[x] R-V10-2 (bloqueo de alta si falta Producto, sin bloquear el resto del lote) verificado
[x] RN-M2 (duplicados Color+TalleConfigId, en lote y contra BD) verificado
[x] RN-B2 (deep-link ?soloAlertas=true preserva Estado=Bajo) verificado
[x] Regresión /Stock/Ajuste y /Variantes/Crear (StockInicial) sin cambios de comportamiento
[x] Catálogo cross-proyecto (regresiones-manuales.yml) recorrido — 2 items aplicables (REG-001, REG-002), ambos PASS
[ ] Smoke manual del cliente pendiente (13 pasos arriba) — no ejecutado por este agente (no automatiza UI)
[ ] Confirmar commit de los archivos actualmente sin commitear antes de desplegar
```

**Veredicto: APROBADO CON OBSERVACIONES** — 0 defectos funcionales, 2 observaciones menores no bloqueantes (OBS-V10-01, OBS-V10-02), sin auto-fix aplicado por no corresponder (no son bugs reproducibles). Pendiente exclusivamente el smoke manual del cliente (regla del agente QA: no se automatiza UI) y la confirmación de que los archivos se commiteen antes de desplegar a producción.

---

## Barrido QA post-V10 — fast-path acumulado `d8a71ef..f400671` (2026-08-16)

**Fuente:** no hay definiciones 1/2/3 nuevas para este rango — los 11 commits se ejecutaron como **fast-path directo a pedido del cliente**, sin pasar por Discovery/Diseño/Arquitectura/Presupuesto (criterio ya usado y aceptado en este proyecto para correcciones y ajustes sobre funcionalidad ya entregada). La única fuente documental disponible es `trazabilidad.md` (entradas 2026-08-11) y el propio código. `1-analista-funcional.md` y `2-disenador-funcional.md` (§V10, DD-1) están **desactualizados a propósito** respecto de lo desplegado.

**Alcance QA:** los 11 commits posteriores al último QA formal (V10, `d8a71ef`, 2026-07-30), ninguno de los cuales pasó por gate QA:

| # | Commit | Título |
|---|---|---|
| 1 | `4f7af9b` | Filtros de Consulta de Stock activos e independientes desde el primer render |
| 2 | `5dcb633` | Filtros server-side reales con daterangepicker y autocomplete (Ventas, Compras, Devoluciones, Productos) |
| 3 | `e102a8d` | Límite de campos de formulario + aviso por mail de 500 sin excepción + sesión a 2 h |
| 4 | `74a115f` | Carga Masiva: reversión de DD-1 (atomicidad total → guardado parcial fila por fila) |
| 5 | `022bd07` | Vista Matriz de stock (Marca → Modelo → Color × Talle) — Etapa 1, lectura |
| 6 | `06bb253` | Talle Argentino como sistema paralelo al Brasileño — Etapa 2 |
| 7 | `0eba0fc` | Vista Matriz editable por celda, acotada a una Marca — Etapa 3 |
| 8 | `9e43229` | Matriz como pantalla principal de Stock + editar variantes en 0 (`soloConStock`) |
| 9 | `42b7f19` | Permitir editar en la Matriz variantes sin stock (en 0) |
| 10 | `1122c3c` | Aviso visible (toast) cuando falla el guardado en Matriz / Carga Masiva |
| 11 | `f400671` | Alta de variantes nuevas desde celdas "—" de la Matriz editable |

**Método:** inspección exhaustiva de código sobre `git diff d8a71ef..HEAD` (31 archivos, +1615/-287) leyendo los archivos completos y no sólo el diff, más build propio independiente.

> **Verificación automatizada por navegador NO disponible en esta sesión.** El servidor MCP `playwright` está declarado en `C:/Sistemas/Agentes-IA/.mcp.json` pero sus herramientas `mcp__playwright__*` no están expuestas en esta sesión del agente. Conforme a `33-verificacion-automatizada-qa.instructions.md` ("Si no hay herramienta de automatización disponible"), se declara explícitamente y se cae al procedimiento manual: los casos dependientes de ejecución real quedan como guía de pasos al final de esta sección. **Ningún caso se reporta PASS sin haberse verificado por inspección de código con evidencia citada (archivo:línea).**

**Build:** `dotnet build ShowroomGriffin.slnx` → *Compilación correcta. 0 Advertencia(s), 0 Errores.* (17,4 s, verificado de forma independiente por este agente, no tomado del reporte del Implementador).

### Cobertura por criterio (PASS / FAIL / BLOCKED)

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| C-01 | `4f7af9b`: los 4 combos de `/Stock/Index` nacen poblados y son independientes del orden de selección | PASS-CR | `StockController.cs:49-52` puebla Marcas/Modelos/Talles/Colores completos server-side; `Stock/Index.cshtml` elimina `disabled` de los 4 `<select>` y cachea el HTML original en `fullOptions` para restaurar la lista completa al limpiar el padre. |
| C-02 | `4f7af9b`: la cascada sigue funcionando como refinamiento opcional, sin deshabilitar ni vaciar el hijo | PASS-CR | `repoblar()` preserva la opción actual si sigue existiendo y repuebla vía AJAX; al limpiar el padre restaura `fullOptions.<hijo>`. Ningún `prop('disabled', true)` sobrevive en el diff. |
| C-03 | `4f7af9b`: `ObtenerPorMarcaAsync(null)` / `ObtenerTallesPorModeloAsync(null)` devuelven catálogo completo sin romper los llamadores existentes | PASS-CR | `ModeloService.cs:111-148`: firmas pasan a `int?` con guard `HasValue`; `ModelosController.PorMarca/TallesPorModelo` pasan a `int? = null`. La ruta con `marcaId`/`modeloId` explícito conserva el `Where` original. |
| C-04 | `5dcb633`: los filtros de Ventas/Compras/Devoluciones son **server-side reales** (antes `ext.search.push` client-side sobre `serverSide:true`) | PASS-CR | `VentaService.cs:294-303`, `CompraService.cs:234-242`, `DevolucionService.cs:174-182`: `.Where()` sobre fecha/estado/tipo/cliente/proveedor aplicados **antes** de `CountAsync()`, por lo que `RecordsTotal`/`RecordsFiltered` reflejan el filtro. |
| C-05 | `5dcb633`: el rango de fechas del daterangepicker llega correcto al server bajo cultura `es-AR` | PASS-CR | `Ventas/Index.cshtml:102-103` postea los hidden en `YYYY-MM-DD` (ISO), formato que `DateTime.TryParse` reconoce en cualquier cultura; el label visible usa `DD/MM/YYYY` sólo para el usuario. Rango cerrado correcto: `>= Desde.Date` y `< Hasta.Date.AddDays(1)`. |
| C-06 | `5dcb633`: fix del enum `TipoDevolucion` mal mapeado | PASS-CR | `DevolucionService.cs:180-182`: `tipo==1` → `DevolucionDinero`; `tipo==2` → `CambioMismoValor OR CambioMayorValor`. Coincide con la agrupación que ya usaba `Devoluciones/Detalle.cshtml`. Los valores `0`/`1` previos (que no correspondían a ningún miembro real del enum) quedaron eliminados. |
| C-07 | `e102a8d`: el límite de campos de formulario deja de producir el 500 silencioso en Carga Masiva | PASS-CR | `Program.cs:97-108`: `FormOptions.ValueCountLimit`/`KeyLengthLimit` y `MvcOptions.MaxModelBindingCollectionSize` en `int.MaxValue`. Cubre el rechazo durante la lectura del formulario (previo a antiforgery y al model binding por acción). Ver **OBS-02** por el efecto colateral. |
| C-08 | `e102a8d`: cualquier 5xx sin excepción capturada dispara aviso por mail | PASS-CR | `HomeController.cs:61-79`: `IErrorNotifier.NotifyError` con excepción sintética dentro del bloque `code >= 500`, sólo fuera de Development. Verificado que **no** genera mail duplicado para excepciones MVC normales: `GlobalExceptionHandler.TryHandleAsync` devuelve `false` para requests no-AJAX → `UseExceptionHandler("/Home/Error")` → `HomeController.Error` devuelve `View()` con **HTTP 200**, por lo que `UseStatusCodePagesWithReExecute` no re-ejecuta. Ver **OBS-04**. |
| C-09 | `e102a8d`: `Session.IdleTimeout` 60 min → 2 h | PASS-CR (sin efecto útil) | `Program.cs:169`. Cambio aplicado y benigno, pero **no cumple el objetivo declarado** ("que no caduque mientras se completa un formulario largo"): los formularios dependen de la cookie de autenticación, ya configurada en `ExpireTimeSpan = 90 días` + `SlidingExpiration = true` (`Program.cs:65-66`), no de `Session`. Ver **OBS-03**. |
| C-10 | `74a115f`: Carga Masiva guarda las filas OK e informa las que fallan (reversión de DD-1) | PASS-CR con reserva | `StockService.GuardarCargaMasivaAsync:438-466` (existentes) y `:521-573` (altas): una transacción propia por fila, `continue` tras el rollback. `StockController.cs:279-284`: si `huboErroresParciales` no redirige. Reserva: ver **D-03** (aislamiento no completo ante el camino de excepción). |
| C-11 | `022bd07`: matriz de lectura agrupa Marca → Modelo → Color × Talle y sólo muestra celdas con stock > 0 | PASS-CR | `StockService.ObtenerMatrizAsync:601-703`; `soloConStock` aplica `Where(s => s.StockActual > 0)` (línea 610-611). Secciones por `TalleConfig.Tipo`, columnas `DistinctBy(t => t.Id).OrderBy(t => t.Valor)`, filas por Color. |
| C-12 | `06bb253`: `TipoTalle.ZapatillaAdultoArgentino` sin migración EF y sin seed hardcodeado | PASS-CR | `TipoTalle.cs`: nuevo miembro `= 4` (enum persistido como int, sin cambio de esquema). `git diff --stat` confirma 0 archivos bajo `Migrations/`. `ModeloService.cs:126-135` ofrece ambos catálogos sólo cuando el Modelo es `ZapatillaAdulto`. |
| C-13 | `06bb253`: los combos de talle distinguen sistema cuando ambos conviven | **FAIL parcial** | Correcto en `CargaMasiva.cshtml:123`, `Variantes/Crear.cshtml:97-101` y `Variantes/Editar.cshtml` (usan `TipoNombre` cuando `mezclaSistemas`). **Falta en `/Stock/Index`** → ver **D-04**. |
| C-14 | `0eba0fc` / `9e43229` / `42b7f19`: la Matriz es editable por celda y permite reponer variantes en 0 | PASS-CR (lógica) / **FAIL (guardado)** | La lectura y el render son correctos: `StockController.MatrizEditar:136` pasa `soloConStock: false` y `PrecargarCantidades` precarga el input con `StockActual`. **Pero el guardado está roto por D-01 y D-02.** |
| C-15 | `9e43229`: Matriz pasa a ser la pantalla principal del menú Stock sin dejar huérfana la Consulta de Stock | PASS-CR | `_Layout.cshtml:136`: `asp-action="Index"` → `asp-action="Matriz"`. `Matriz.cshtml:21` conserva el link de vuelta a `Index`, y `Index.cshtml` tiene el botón "Vista Matriz" — el toggle es bidireccional, `/Stock/Index` sigue alcanzable. |
| C-16 | `1122c3c`: los errores de validación/guardado disparan el toast global de SweetAlert2 | PASS-CR | `_Layout.cshtml:314-323` renderiza el toast a partir de **`TempData["ErrorMessage"]`** — que es exactamente la clave que setean `StockController.cs:156, 166` (MatrizEditar) y `:256, 269` (CargaMasiva). Clave correcta, el fix funciona. (Nota: la clave `TempData["Error"]` **no** está contemplada en el layout — ver **OBS-01**.) |
| C-17 | `f400671`: alta de variantes nuevas desde celdas "—", cada alta en su propia transacción, con deduplicación | **FAIL** | La lógica de servicio es correcta (`GuardarMatrizAsync:789-872`: dedup en lote vía `combosEnEsteLote` + contra BD vía `combinacionesExistentes`, transacción por alta). **Pero la feature es inalcanzable en la práctica: el POST nunca supera la validación de modelo.** Ver **D-01** y **D-02**. |
| C-18 | Permisos: `RequireAdministrador` en `MatrizEditar`, `RequireEmpleado` en `Matriz` | PASS-CR | `StockController.cs:17` clase con `[Authorize(Policy="RequireEmpleado")]`; `Matriz` (línea 118) sin override → RequireEmpleado; `MatrizEditar` GET (131) y POST (142) con `[Authorize(Policy="RequireAdministrador")]` + `[ValidateAntiForgeryToken]`. Defensa en profundidad en vista: `Matriz.cshtml:15, 71` ocultan el botón Editar salvo `SuperUsuario`/`Administrador`. Coherente con `Ajuste`/`CargaInicial`/`CargaMasiva`. Sin links de sidebar nuevos que requieran rol. |
| C-19 | Regresión: `/Stock/Ajuste` (ajuste manual individual) sin cambio de comportamiento | PASS-CR | `git diff d8a71ef..HEAD` sobre `StockService.cs`: los cuerpos de `AjusteManualAsync` (159-179) y `AplicarAjusteInternoAsync` (186-209) **no tienen ninguna línea modificada** — sólo aparecen nuevas invocaciones desde `GuardarMatrizAsync`. `StockController.Ajuste` GET/POST sin diff. |
| C-20 | Regresión: `/Variantes/Crear` con `StockInicial > 0` no afectado por el `StockInicial = null` de Carga Masiva / Altas de Matriz | PASS-CR | `git diff --stat d8a71ef..HEAD -- ShowroomGriffin.Infrastructure/Services/VarianteService.cs` → **vacío** (0 cambios). `CrearAsync:24-59` conserva intacta la rama `if (vm.StockInicial.HasValue && > 0) → CargaInicialAsync`, camino que ni Carga Masiva ni las Altas de Matriz ejercitan. Sólo cambió el JS de etiqueta de talle en `Crear.cshtml`. |
| C-21 | Regresión: `/Stock/CargaMasiva` sigue guardando con celdas vacías (no sufre D-01) | PASS-CR | `StockCargaMasivaFilaViewModel.CantidadNueva/PrecioVenta/StockMinimo` son **nullable** (`int?`/`decimal?`, `StockViewModels.cs:85, 89, 93`) y el servicio usa `HasValue`. Ésa es exactamente la asimetría que rompe MatrizEditar. |
| C-22 | Build verde + sin migración EF pendiente | PASS-CR | `dotnet build ShowroomGriffin.slnx` → 0/0, verificado por este agente. `git diff --stat` sin archivos en `Migrations/` — coherente con lo declarado (el enum se persiste como int). |

**18/22 PASS · 3 FAIL (C-13 parcial, C-14 guardado, C-17) · 1 PASS con reserva (C-10) · 0 BLOCKED.**

### Cobertura de máquina de estados

No aplica. Ninguno de los 11 commits altera transiciones de `Venta`, `Compra` ni `Devolución`: `5dcb633` sólo agrega `Where` de lectura sobre `Estado` en los listados (`VentaService.cs:300`, `CompraService.cs:239`), y todo el bloque de Stock (`AjusteStock`, `MovimientoStock`, `VarianteProducto`) opera sobre entidades sin máquina de estados propia. Se verificó que los guards de estado preexistentes de Compras (`ComprasController.cs:65, 107`) no fueron tocados.

### Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

| id | aplica | resultado | acción |
|---|---|---|---|
| REG-001 (RowVersion MySQL al crear variante) | sí | PASS | Las altas de `f400671` reutilizan `VarianteService.CrearAsync` sin tocarlo; `AppDbContext.SaveChanges` sigue asignando `RowVersion` manualmente. Sin `DbUpdateException`. |
| REG-002 (stock inicial al crear/editar variante) | sí (relacionado) | PASS | `VarianteService.cs` **sin diff** en todo el rango. El mecanismo `StockInicial` de `/Variantes/Crear` intacto; las Altas de Matriz pasan `StockInicial = null` a propósito y cargan la cantidad vía `AplicarAjusteInternoAsync`. |
| REG-003 (autocomplete Compras) | sí | PASS | `5dcb633` agrega Select2 AJAX de Proveedor en `Compras/Index.cshtml` reutilizando `/Proveedores/Buscar` (endpoint preexistente, confirmado en trazabilidad). Mapeo a `razonSocial` real, no a `descripcion`. |
| REG-004 (máquina de estados Compra) | no | N/A | `ComprasController` sólo recibe parámetros de filtro nuevos; guards de estado sin diff. |
| REG-005 (autocomplete Ventas sin texto) | sí | PASS | Select2 de Cliente en `Ventas/Index.cshtml` mapea a `nombre` (campo real de `ClienteViewModel`), no a `descripcion`. |
| REG-006 (medio de pago Cuotas) | no | N/A | Módulo no tocado. |
| REG-007 (autocomplete Devoluciones) | no | N/A | `Devoluciones/Crear.cshtml` no tocado; el cambio es sobre `Index` (filtros). |
| REG-008 (input pierde foco al tipear) | sí | PASS | Patrón ausente: `MatrizEditar.cshtml` y `CargaMasiva.cshtml` no re-renderizan el `tbody` en cada keystroke. La única manipulación JS de valores (`sincronizarPrecioYMinimoDeAltas`) corre **una sola vez en el `submit`**, no en `input`/`change`. |
| REG-009 (cascada por segmento posicional) | sí | PASS | Todas las cascadas del rango usan querystring: `Marcas/PorCategoria?categoriaId=`, `Modelos/PorMarca?marcaId=`, `Modelos/TallesPorModelo?modeloId=`. Ninguna usa segmento posicional. |
| REG-010 (menú Auditoría por rol) | no | N/A | Sidebar tocado sólo en el destino del link Stock (`Index`→`Matriz`), ambos `RequireEmpleado`. Sin cambio de visibilidad por rol. |
| KOI-001 (botón Swal fuera del form) | sí | PASS | `MatrizEditar.cshtml:179` intercepta el evento `submit` **nativo del `<form>`** y el botón es `type="submit"` **dentro** del form (línea 151). No existe el patrón `btn-swal-confirm` + `closest('form')` que causaba KOI-001. |
| KOI-002 / KOI-003 / KOI-005 / KOI-006 | no | N/A | Proyecto KoiDumplings; sin módulo equivalente tocado. |
| KOI-004 (validación bloqueante de negocio) | no | N/A | Sin equivalente funcional en este rango. |
| DN-001 / DN-002 (Include de colección + OrderBy dinámico + Skip/Take) | sí (evaluado) | PASS | La `causa_raiz` es específica del provider **EF6-MySQL** (`MySql.Data.EntityFramework`, discontinuado); este proyecto usa **EF Core 10**. Además `DevolucionService.ListarAsync:190-197` proyecta con `.Select()` (`d.Detalles.Count`), por lo que el `Include` de colección se descarta y no hay materialización de colección con `Skip/Take`. `VentaService`/`CompraService` sólo incluyen navegaciones de referencia (`Cliente`, `Proveedor`). Ningún `OrderBy` dinámico. |
| GAN-001 (guard de servidor que nunca se dispara) | sí (patrón análogo) | **relacionado con D-01** | El patrón "el bloqueo real ocurre por un `Range`/binding de una fila fantasma con mensaje engañoso" es exactamente lo que ocurre en `MatrizEditar`: el guard de negocio de `GuardarMatrizAsync` nunca se alcanza porque el binding de las celdas "—" vacías rechaza antes con un mensaje genérico. Se cataloga el caso nuevo como **SG-001**. |
| GAN-002 / GAN-003 / GAN-004 | no | N/A | Proyecto ganadería; sin equivalente (no hay `<script type="text/x-template">` ni `<datalist>` en el rango). |
| VSF-001 / VSF-002 | no | N/A | Proyecto VSF; máquina de estados de compras no tocada. |
| CRM-001 … CRM-006 | no | N/A | Proyecto CRM/Bot; sin módulo equivalente. |
| MH-001 (IN sobre colección local en listado de movimientos) | sí (evaluado) | PASS | `GuardarMatrizAsync:727-729` usa `Contains` sobre `List<int>` local contra `_db.Stocks` — mismo patrón, pero con `int` (no `HashSet<string>`), traducido sin problema por Pomelo/EF Core 10; el proyecto ya usa este patrón (`GuardarCargaMasivaAsync:407`). Sin cambios en `Stock/GetData`. |
| MH-002 (enum serializado como int rompe badge) | sí | PASS | `DevolucionListItemViewModel.TipoOperacion` se sigue serializando igual que antes del rango; el fix del filtro es server-side y no cambió la forma del DTO. Badge de la columna alineado con la misma agrupación (1=Devolución, 2=Cambio). |
| MH-003 / MH-004 / MH-005 / MH-006 / MH-007 / MH-008 | no | N/A | Módulos (cheques, caja mensual, remito público, proyección financiera, pago de OC) inexistentes o no tocados en este proyecto/rango. |
| MH-009 (fecha calendario pura retrocede un día por conversión UTC) | sí (evaluado) | PASS | Los filtros nuevos comparan `DateTime` server-side contra columnas de BD (`>= .Date`, `< .Date.AddDays(1)`), sin pasar por el serializador JSON ni por moment.js. Las columnas de fecha ya visibles en esos listados no cambiaron de conversor en este rango. |

**Item nuevo a catalogar:** **SG-001** (ver "Auto-fixes aplicados").

### Defectos detectados

| # | Severidad | Descripción, archivo y línea | Escenario de falla |
|---|---|---|---|
| **D-01** | **Alta (blocker de la feature)** | `ShowroomGriffin.Web/Views/Stock/MatrizEditar.cshtml:110-111` renderiza el input de la celda "—" **sin atributo `value`** (`<input type="number" name="Altas[i].CantidadNueva" min="0" placeholder="—" ...>`), mientras `ShowroomGriffin.Application/DTOs/Stock/StockViewModels.cs:269` declara `public int CantidadNueva { get; set; }` — **no nullable**. Un `<input type=number>` vacío postea cadena vacía; el `SimpleTypeModelBinder` de ASP.NET Core convierte `""` en `null` y, al no ser el tipo nullable, agrega error de ModelState. Idéntico problema en `PrecioVenta` (`decimal`, línea 272) y `StockMinimo` (`int`, línea 275). | Como Administrador: `/Stock/MatrizEditar?marcaId=X` sobre cualquier marca donde una sección tenga ≥2 colores con cobertura de talles distinta (es decir, donde exista al menos una celda "—" — el caso normal, y la razón de ser de la feature). Modificar una o más celdas con stock, **dejar vacías las celdas "—"**, escribir el Motivo y pulsar "Guardar cambios". Resultado real: `StockController.cs:148` entra en `!ModelState.IsValid`, setea `TempData["ErrorMessage"]` con el **primer error de framework** (texto genérico/inglés tipo *"The value '' is invalid."*) y devuelve la vista. **No se guarda absolutamente nada** — ni las altas ni las celdas existentes que sí se habían editado correctamente. Resultado esperado: se guardan las celdas modificadas y se ignoran las celdas "—" vacías (criterio explícito del propio servicio: `StockService.cs:793` `if (alta.CantidadNueva <= 0) continue; // el usuario no cargó nada en esta celda "—"`). **Es una regresión introducida por `f400671` sobre la edición por celda que ya funcionaba en `0eba0fc`/`9e43229`.** Ver contraste en C-21: `StockCargaMasivaFilaViewModel` sí usa `int?`/`decimal?`. |
| **D-02** | **Alta (blocker, independiente de D-01)** | `MatrizEditar.cshtml:123-124`: `<input type="number" step="0.01" class="row-precio" id="rowPrecio_@filaIdx" value="@fila.PrecioVentaSugerido">`. `Program.cs:192-197` fija la cultura global en **`es-AR`**, por lo que Razor serializa el `decimal?` con coma decimal (p. ej. `45000,00`). Según el algoritmo de saneamiento de valor de HTML5, un `input type=number` cuyo valor no es un *valid floating-point number* queda **vacío** en el DOM. Acto seguido `sincronizarPrecioYMinimoDeAltas()` (líneas 167-176) copia ese valor vacío al hidden: `$(this).val($('#rowPrecio_' + rowIdx).val())` → sobrescribe con `""` el hidden `Altas[i].PrecioVenta` (línea 108) que **el servidor había renderizado correctamente**. | Mismo escenario que D-01, incluso si el usuario **sí** carga cantidades en las celdas "—". El input visible de Precio aparece en blanco (el usuario ve el placeholder "Precio" vacío en vez del precio sugerido de la fila), y al enviar, el hidden queda vacío → error de binding sobre `decimal PrecioVenta` no nullable → mismo bloqueo total del POST. La sincronización, cuyo propósito es *permitir* pisar el precio, en la práctica **destruye un valor que ya era correcto**. `StockMinimo` no sufre esto (`int?` no lleva separador decimal). |
| **D-03** | **Media** | Fuga del *change tracker* de EF Core entre transacciones por fila. `StockService.GuardarCargaMasivaAsync:438-466` y `:521-573`, y `StockService.GuardarMatrizAsync:745-771` y `:825-871`, abren `BeginTransactionAsync()` por fila **sobre el mismo `AppDbContext` scoped** (`_db`, inyectado en el constructor, línea 24). Cuando una fila falla por el camino de **excepción** (el `catch`), se hace `RollbackAsync()` de la transacción pero **no se revierte el change tracker**: si la excepción se produjo dentro de `SaveChangesAsync`, el `AjusteStock` queda en estado `Added` y la entidad `Stock` en `Modified`. El siguiente `AplicarAjusteInternoAsync` de una fila posterior ejecuta `await _db.SaveChangesAsync()` (línea 203), que **vuelca todos los cambios pendientes**, incluidos los de la fila que ya se informó como fallida — dentro de la transacción de la fila siguiente. | Escenario A (persistencia fantasma): la fila 3 falla por excepción (p. ej. violación de constraint o timeout) y se marca en rojo como "No se pudo actualizar el stock de esta variante"; la fila 4 se procesa OK y hace commit → **el ajuste de la fila 3 se persiste igual**, junto con su `AjusteStock` y su `MovimientoStock`. El usuario ve "fila con error" pero el stock cambió. Escenario B (lote envenenado): si la causa de la excepción persiste, cada `SaveChangesAsync` posterior vuelve a intentar la operación pendiente y falla, marcando **todas** las filas restantes como erróneas — anulando justamente el objetivo de `74a115f` (guardado parcial). Nota: el camino de retorno `!Success` (validación) **sí** es limpio — `AplicarAjusteInternoAsync` sólo devuelve `Success=false` en la línea 189 (`stock == null`), antes de cualquier mutación. Mitigante: requiere una excepción real de base, no ocurre en la operación normal. |
| **D-04** | **Media** | `StockController.cs:51` llama `ObtenerTallesPorModeloAsync(null)`, que tras `06bb253` devuelve el catálogo **completo** de `TallesConfig` — incluyendo ahora `ZapatillaAdulto` (brasileño) **y** `ZapatillaAdultoArgentino`. `Views/Stock/Index.cshtml` renderiza la opción como `<option value="@t.Id">@t.Valor</option>` (sólo el valor), y el repoblado por cascada hace `repoblar('#filTalle', data, 'id', 'valor')` — **en ningún caso usa `TipoNombre`**. Todos los demás combos de talle sí recibieron la desambiguación en `06bb253`: `CargaMasiva.cshtml:123`, `Variantes/Crear.cshtml:97-101`, `Variantes/Editar.cshtml`. | En `/Stock/Index`, el combo Talle muestra entradas visualmente idénticas y duplicadas (p. ej. dos opciones "40", una por sistema de numeración). El usuario no puede saber cuál elegir; cada una filtra por un `TalleConfigId` distinto y devuelve resultados distintos, lo que se percibe como un filtro errático. Agravante: `ModeloService.cs:126-135` ofrece **ambos** catálogos también al elegir un Modelo `ZapatillaAdulto`, así que el problema no se resuelve refinando por Modelo. **Latente**: sólo se manifiesta una vez que el cliente cargue valores del catálogo argentino en `/TallesConfig` (pendiente según `trazabilidad.md`), pero es certero en cuanto lo haga. |

### Observaciones (no defectos reproducibles, sin auto-fix)

| # | Severidad | Descripción | Recomendación |
|---|---|---|---|
| OBS-01 | Baja (preexistente, fuera del rango) | `_Layout.cshtml:303-323` sólo contempla `TempData["SuccessMessage"]`, `TempData["Success"]` y `TempData["ErrorMessage"]`. La clave `TempData["Error"]` **no se renderiza en ningún lado**: `ComprasController.cs:65` y `:107` la setean antes de redirigir y el mensaje **se pierde en silencio** (mismo tipo de bug que `1122c3c` corrigió para Stock). `StockController.cs:84` también la usa, pero ahí sí funciona porque `Stock/CargaInicial.cshtml:13-16` la renderiza localmente. Esto además corrige una afirmación inexacta del pase QA V9, que dio por hecho el manejo global de `TempData["Error"]`. | Unificar en `ErrorMessage` en los 3 call sites, o agregar `TempData["Error"]` al `@if` del layout. Fuera del alcance de este rango; requiere aprobación. |
| OBS-02 | Baja-Media | `Program.cs:99-108`: `ValueCountLimit`, `KeyLengthLimit` y `MaxModelBindingCollectionSize` en `int.MaxValue` aplican **globalmente a toda la aplicación**, no sólo a Carga Masiva, y eliminan la protección barata contra un POST con millones de claves. Blast radius acotado en la práctica por el tope de cuerpo de request (30 MB por defecto en Kestrel/IIS, no configurado explícitamente) y por el rate limiter general de 300 req/min (`Program.cs:146`), y la app es sólo para usuarios autenticados. `ValueLengthLimit` y `MultipartBodyLengthLimit` quedaron en su valor por defecto. `KeyLengthLimit = int.MaxValue` no aporta nada (las claves de estos formularios son cortas). | Acotar a un valor generoso pero finito (p. ej. `ValueCountLimit = 32768`) y/o mover el override a `[RequestFormLimits]` sobre las acciones `CargaMasiva` y `MatrizEditar` únicamente. |
| OBS-03 | Baja | `Session.IdleTimeout` a 2 h no cumple su objetivo declarado: los formularios largos dependen de la cookie de autenticación (`ExpireTimeSpan = 90 días`, `SlidingExpiration = true`, `Program.cs:65-66`) y del token antiforgery ligado a ella, no de `Session`. Efecto real: retención de estado de sesión en `AddDistributedMemoryCache` durante el doble de tiempo. | Benigno. Documentar que el 500 de Carga Masiva no era de sesión (ya está probado que era el límite de campos) y, si se quiere, revertir a 60 min. |
| OBS-04 | Baja | `HomeController.StatusCode` notifica por mail **cada** 5xx sin excepción, sin deduplicación ni throttling: una falla sistémica (p. ej. base caída) genera un mail por request. Además inyecta `IErrorNotifier` **scoped** (`DependencyInjection.cs:30`) directamente en el controller, mientras `NotifyError` es fire-and-forget (`Task.Run`) — la tarea puede sobrevivir al scope del request y a su `IEmailService` scoped. `GlobalExceptionHandler` mitiga parcialmente usando `IServiceScopeFactory`, con la misma ventana. | Agregar deduplicación por (path + código) con ventana de N minutos, y resolver `IErrorNotifier` desde un scope propio o registrarlo como Singleton. |
| OBS-05 | Baja | `StockService.ObtenerMatrizAsync:640` toma `ProductoId = grupoModelo.Select(...).FirstOrDefault()` — el **primer** Producto del Modelo. Peor: en la línea 681, `filaVm.Celdas[talleConfigId] = ...` **sobrescribe en silencio** si dos Productos del mismo Modelo tienen variantes con el mismo Color y el mismo Talle: una de las dos variantes **desaparece de la matriz** y un alta desde una celda "—" quedaría atribuida al Producto equivocado. Riesgo idéntico al ya aceptado en V10 para Carga Masiva, agravado aquí por la pérdida visual. | No bloqueante si se mantiene la convención 1 Modelo = 1 Producto. Si esa convención no está garantizada por datos, agregar índice único `(ProductoId, Color, TalleConfigId)` (ya sugerido como OBS-V10-02) y desambiguar la matriz por Producto. |
| OBS-06 | Baja | `Stock/Index.cshtml`: `repoblar()` termina con `$sel.trigger('change')`, lo que dispara el handler del combo hijo, que a su vez repuebla y vuelve a disparar — cada cambio de Categoría genera entre 2 y 4 llamadas redundantes a `reloadTable()` (y sus POST a `/Stock/Listar`). Funcionalmente inocuo (DataTables descarta draws viejos por el contador `draw`). | Usar `trigger('change.select2')` para refrescar sólo la etiqueta de Select2, o un flag de supresión durante el repoblado. |
| OBS-07 | Baja | `StockController.ReconstruirVistaEdicionAsync:193`: `guardar.Celdas.ToDictionary(c => c.VarianteId)` lanza `ArgumentException` no capturada (→ 500) si llegaran dos celdas con el mismo `VarianteId`. No es alcanzable con la forma de datos actual (una variante ocupa exactamente una celda), pero es un camino a 500 sin guard sobre datos **posteados por el cliente**. Además, el propio XML-doc reconoce que las altas con error pierden la cantidad tipeada. | Usar `GroupBy(...).ToDictionary(g => g.Key, g => g.First())`. Bajo esfuerzo, sin cambio funcional. |

### Puntos de atención planteados por el orquestador — confirmados / refutados

| Sospecha | Veredicto | Evidencia |
|---|---|---|
| ¿El guardado parcial aísla realmente cada fila/alta, sin estado inconsistente si una falla a mitad de camino? | **CONFIRMADO parcialmente** | El aislamiento **transaccional a nivel de base** es correcto, pero el **change tracker compartido** rompe el aislamiento por el camino de excepción → ver **D-03**. |
| ¿Puede quedar una variante creada con el ajuste de stock inicial fallido (huérfana)? | **REFUTADO** | El alta completa (`VarianteService.CrearAsync` → `VarianteProducto` + `Stock` en 0 → `AplicarAjusteInternoAsync`) ocurre **íntegramente dentro de `txAlta`** (`StockService.cs:825-863`). Ni `CrearAsync` ni `AplicarAjusteInternoAsync` abren transacción propia con `StockInicial = null` (verificado en `VarianteService.cs:24-59`). Un fallo en cualquier punto revierte también el `INSERT` de la variante: **no quedan variantes huérfanas en la base**. |
| ¿Los permisos están bien aplicados en todas las acciones nuevas? | **REFUTADO (están bien)** | Ver C-18. `Matriz` = `RequireEmpleado`, `MatrizEditar` GET y POST = `RequireAdministrador` + antiforgery, y la vista oculta el botón Editar por rol. Sin huecos. |
| ¿`int.MaxValue` tiene efecto colateral no documentado? | **CONFIRMADO (menor)** | Ver **OBS-02**: alcance global (no acotado a Carga Masiva) y pérdida de la protección de conteo de campos, acotada por el límite de cuerpo de request y el rate limiter. |
| ¿La sincronización JS de Precio/Stock Mínimo falla en algún caso borde? | **CONFIRMADO, pero por otra causa que la sospechada** | **Sospecha "fila sin ninguna celda '—'": REFUTADA.** `faltantes` (`MatrizEditar.cshtml:81`) cuenta exactamente los talles sin celda, y los inputs `Altas[...]` se renderizan exactamente para esos mismos talles (rama `else if` de la línea 100); si `faltantes == 0` no existen ni las altas ni los inputs visibles — los dos conjuntos son siempre consistentes. **Sospecha "dos secciones distintas del mismo Modelo con el mismo índice de fila": REFUTADA.** `filaIdxCounter` se declara **una sola vez** en la línea 9 y **nunca se reinicia** entre modelos ni secciones, por lo que los ids `rowPrecio_N` / `rowStockMin_N` son únicos en toda la página. **La falla real es la cultura `es-AR` → ver D-02**, que rompe el caso normal, no un borde. |
| Regresión `/Stock/Ajuste` | **PASS** | Ver C-19: cuerpos de `AjusteManualAsync` y `AplicarAjusteInternoAsync` sin una sola línea modificada en el rango. |
| Regresión `/Variantes/Crear` con `StockInicial > 0` | **PASS** | Ver C-20: `VarianteService.cs` sin diff alguno en `d8a71ef..HEAD`. |
| Catálogo cross-proyecto | **Ejecutado** | 33 items recorridos; 11 aplicables, todos PASS; 1 patrón análogo (GAN-001) que motiva el alta de **SG-001**. |

### Auto-fixes aplicados

**Ninguno — por instrucción explícita del solicitante** ("si encontrás un defecto reproducible con severidad media o alta, documentalo con claridad pero NO apliques ningún auto-fix de código sin que yo lo revise primero"). Esta instrucción **prevalece sobre la regla de auto-fix obligatorio** de `30-qa-regresiones.instructions.md`.

Se registró el item nuevo **SG-001** en `docs/qa/regresiones-manuales.yml` (la obligación de catalogación previa al fix sí corresponde cumplirla).

Dirección de fix propuesta para D-01/D-02 (**no aplicada, requiere aprobación**):
- `StockMatrizAltaGuardarViewModel`: pasar `CantidadNueva`, `PrecioVenta` y `StockMinimo` a `int?`/`decimal?`/`int?` (misma forma que `StockCargaMasivaFilaViewModel`, `StockViewModels.cs:85-93`) y ajustar los guards de `GuardarMatrizAsync:793, 803, 837, 851` a `HasValue`.
- `MatrizEditar.cshtml:123-124`: renderizar el precio con cultura invariante (`@fila.PrecioVentaSugerido?.ToString(System.Globalization.CultureInfo.InvariantCulture)`) y, en `sincronizarPrecioYMinimoDeAltas()`, **no sobrescribir** el hidden cuando el input visible esté vacío.
- Verificación post-parche: guardar la Matriz de una marca con celdas "—" vacías → deben persistirse las celdas modificadas; cargar una cantidad en una celda "—" → debe crearse la variante con el precio sugerido correcto.

### Riesgos de liberación y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| **D-01/D-02 ya están en producción** (los 11 commits fueron desplegados por Web Deploy tras cada etapa, según `trazabilidad.md`) | **Certeza** | **Alto** | La pantalla `/Stock/MatrizEditar` es hoy inoperante para su caso de uso principal. Agravante de percepción: gracias a `1122c3c` el usuario **ve** un toast rojo con un mensaje de framework en inglés, así que la falla es visible e inexplicable para el cliente. Mitigación inmediata: usar `/Stock/CargaMasiva` (no afectada, C-21) o `/Stock/Ajuste` hasta aplicar el fix. Prioridad de corrección: **la más alta del backlog**. |
| D-03 (persistencia fantasma / lote envenenado) | Baja | Medio | Requiere una excepción real de base. Mitigación de fondo: `_db.ChangeTracker.Clear()` en el `catch` de cada fila, o un `DbContext` por fila vía `IDbContextFactory`. No aplicar sin revisión: toca el corazón del guardado parcial de `74a115f`. |
| D-04 (talles duplicados en el filtro) | Media (al cargar el catálogo argentino) | Bajo-Medio | Latente hasta que el cliente cargue talles argentinos en `/TallesConfig`. **Avisar al cliente antes de que los cargue**, o aplicar la desambiguación en `Stock/Index.cshtml` primero (cambio de 2 líneas, mismo patrón que ya existe en las otras 3 vistas). |
| 11 commits desplegados a producción sin gate QA | Certeza | Medio | Este barrido es la contramedida. Ver "Conclusión sobre el fast-path". |
| `1-analista-funcional.md` y `2-disenador-funcional.md` (§V10, DD-1) desactualizados respecto de lo desplegado | Certeza | Bajo-Medio | Ya señalado por el Implementador en `trazabilidad.md`. Sigue pendiente: DD-1 documenta atomicidad total, y producción hace guardado parcial desde `74a115f`. Sincronizar si se retoma el flujo formal. |
| Verificación por navegador no ejecutada (MCP `playwright` no disponible en esta sesión) | Certeza | Bajo | Los 4 defectos se fundamentan en inspección de código con evidencia `archivo:línea` y comportamiento documentado del framework, no en suposiciones. La guía de pasos permite confirmarlos a mano en < 10 minutos. |

### Pruebas mínimas ejecutadas (este pase — por inspección, sin navegador)

- `git log --oneline d8a71ef..HEAD` y `git diff --stat d8a71ef..HEAD` → 11 commits, 31 archivos, +1615/-287; alcance cotejado contra `trazabilidad.md`.
- `dotnet build ShowroomGriffin.slnx` → **0 advertencias, 0 errores** (verificado de forma independiente).
- Lectura íntegra de `StockController.cs` (306 líneas): permisos por acción, ambos caminos de error de `MatrizEditar` y `CargaMasiva`, `ReconstruirVistaEdicionAsync`, `PrecargarCantidades`.
- Lectura íntegra de `StockService.cs` en las regiones nuevas y preexistentes: `CargaInicialAsync`, `AjusteManualAsync`, `AplicarAjusteInternoAsync`, `RegistrarMovimientoAsync`, `GuardarCargaMasivaAsync`, `ObtenerMatrizAsync`, `EtiquetaTipoTalle`, `GuardarMatrizAsync`.
- Lectura íntegra de `MatrizEditar.cshtml` (194 líneas) — origen de D-01 y D-02.
- Lectura de `VarianteService.CrearAsync/EditarAsync` (sin diff en el rango) para cerrar C-20 y REG-002.
- Diff completo de `Program.cs`, `HomeController.cs`, `ModeloService.cs`, `ModelosController.cs`, `VentaService.cs`, `CompraService.cs`, `DevolucionService.cs`, `ProductosController.cs`, `VentasController.cs`.
- Diff completo de las vistas: `Stock/Index.cshtml`, `Stock/CargaMasiva.cshtml`, `Stock/Matriz.cshtml`, `Ventas/Index.cshtml`, `Variantes/Crear.cshtml`, `_Layout.cshtml`.
- Verificación cruzada de claves `TempData` entre controllers y `_Layout.cshtml` (origen de C-16 y OBS-01).
- Verificación de tipos (nullable vs. no nullable) de `StockMatrizAltaGuardarViewModel` vs. `StockCargaMasivaFilaViewModel` — evidencia central de D-01.
- Verificación de la configuración de cultura (`Program.cs:192-197`, `es-AR`) — evidencia central de D-02.
- Verificación de `GlobalExceptionHandler` + `HomeController.Error` + orden de `UseExceptionHandler` / `UseStatusCodePagesWithReExecute` — descarta el mail duplicado (C-08).
- Verificación de lifetimes en `DependencyInjection.cs` (`IErrorNotifier`/`IEmailService` Scoped) — OBS-04.
- Recorrido de los 33 items de `docs/qa/regresiones-manuales.yml` con mapeo de módulo equivalente.
- Confirmación de ausencia de migraciones EF en el rango (`git diff --stat`, 0 archivos en `Migrations/`).

### Guía de pasos para confirmación manual (pendiente de ejecución real)

**Prioridad 1 — reproducir D-01/D-02 (2 minutos):**
1. Como Administrador, ir a `/Stock/Matriz`, elegir una Marca cuya tabla muestre al menos una celda vacía "—", y pulsar "Editar stock de esta marca".
2. Observar la última columna ("Talle nuevo (precio / mín.)"): **el campo Precio debe aparecer en blanco** aunque la fila tenga precio cargado → confirma **D-02**.
3. Cambiar la cantidad de una celda que sí tiene stock, dejar **todas** las celdas "—" vacías, escribir un Motivo y pulsar "Guardar cambios" → confirmar en el SweetAlert2.
4. Resultado esperado si D-01 existe: toast rojo de error con mensaje genérico y **ningún cambio persistido** (verificar en `/Stock/Historial` que no se generó movimiento).

**Prioridad 2 — regresiones (5 minutos):**
5. `/Stock/Ajuste`: cargar un ajuste individual → debe seguir funcionando igual (C-19).
6. `/Variantes/Crear` con Stock Inicial > 0 → la variante debe quedar con ese stock (C-20, REG-002).
7. `/Stock/CargaMasiva`: modificar 2-3 filas dejando otras vacías → **debe guardar** (contraste con D-01; confirma C-21).
8. Como Empleado/Vendedor: click en "Stock" del sidebar → debe abrir `/Stock/Matriz` con 200; `/Stock/MatrizEditar?marcaId=1` por URL directa → debe dar 403 (C-18).

**Prioridad 3 — filtros (5 minutos):**
9. `/Stock/Index`: filtrar por Talle sin haber elegido Marca ni Modelo → debe funcionar (C-01).
10. `/Ventas/Index`, `/Compras/Index`, `/Devoluciones/Index`: aplicar rango de fechas con más de una página de datos → el total del pie de la tabla debe reflejar el filtro (C-04).
11. `/Devoluciones/Index`: filtrar Tipo = "Cambio" → deben aparecer tanto los de mismo valor como los de mayor valor (C-06).
12. Cuando se carguen talles argentinos en `/TallesConfig`, revisar el combo Talle de `/Stock/Index` → confirmará **D-04**.

### Checklist de salida para merge

```
[x] Build verde (0 advertencias, 0 errores) — verificado independientemente por QA
[x] Sin migración EF en el rango (confirmado: enum persistido como int, 0 archivos en Migrations/)
[x] Permisos correctos en todas las acciones nuevas (Matriz=RequireEmpleado, MatrizEditar=RequireAdministrador+antiforgery)
[x] Regresión /Stock/Ajuste sin cambio de comportamiento (sin diff)
[x] Regresión /Variantes/Crear con StockInicial>0 sin afectar (VarianteService.cs sin diff)
[x] Regresión /Stock/CargaMasiva sigue guardando con celdas vacías (VM nullable)
[x] Catálogo cross-proyecto recorrido (33 items; 11 aplicables, todos PASS)
[x] Item nuevo SG-001 catalogado en regresiones-manuales.yml
[x] TempData["ErrorMessage"] verificado contra la clave real del layout (el fix de 1122c3c funciona)
[x] Sin mail duplicado por 5xx (HomeController.Error devuelve 200, no re-ejecuta status code pages)
[ ] D-01 — /Stock/MatrizEditar no guarda nada con celdas "—" vacías  ← BLOQUEANTE, EN PRODUCCIÓN
[ ] D-02 — precio de fila se vacía por cultura es-AR y la sincronización JS lo destruye  ← BLOQUEANTE, EN PRODUCCIÓN
[ ] D-03 — change tracker compartido entre transacciones por fila (revisión requerida)
[ ] D-04 — talles duplicados en el filtro de /Stock/Index (latente)
[ ] Verificación por navegador (MCP playwright no disponible en esta sesión) — guía manual arriba
[ ] Sincronizar 1-analista-funcional.md y 2-disenador-funcional.md (DD-1 revertida por 74a115f)
```

**Veredicto: RECHAZADO — requiere corrección antes de considerar el rango cerrado.**

No es un rechazo del rango completo: 8 de los 11 commits (`4f7af9b`, `5dcb633`, `e102a8d`, `74a115f`, `022bd07`, `06bb253`, `9e43229`, `1122c3c`) están **correctos y son aptos para producción**, con las observaciones menores listadas. El rechazo se concentra en **`f400671`** (el commit más reciente), que introduce dos defectos de severidad Alta que dejan `/Stock/MatrizEditar` inoperante — y que además **regresionan** la edición por celda que `0eba0fc`/`9e43229`/`42b7f19` ya habían entregado funcionando. Como el código ya está desplegado, D-01 y D-02 deben tratarse como **hotfix**, no como backlog.

### Conclusión sobre el fast-path sin QA previo

Hallazgo de proceso, no de código: los 11 commits pasaron build verde, `dotnet publish` verde y revisión manual de diff, y aun así **dos defectos bloqueantes llegaron a producción**. Ninguno de los dos es detectable por compilación ni por lectura del diff aislado: D-01 exige cruzar la vista contra la nullabilidad del ViewModel (dos archivos, dos capas), y D-02 exige cruzar la vista contra la configuración global de cultura en `Program.cs`. Es exactamente la clase de defecto que el gate QA existe para atrapar.

El fast-path sigue siendo razonable para cambios de una línea (V9) o de configuración (`e102a8d`), pero **`f400671` no era un fast-path**: agregaba un ViewModel nuevo, una rama de servicio nueva y binding de formulario nuevo — es una feature, con el perfil de riesgo de una feature. Criterio propuesto para el futuro: si el cambio agrega un **ViewModel nuevo con binding de formulario**, sale del fast-path aunque el pedido del cliente sea "un ajuste chico".

---

## V12 — Extensión de la Matriz (accesorios sin talle + alta de Color nuevo) + ocultamiento de Carga Masiva/Ajuste (2026-08-16)

**Input:** `1-analista-funcional.md` (V12, D1–D4), `2-disenador-funcional.md` (V12, HU-12.1 a HU-12.4), `3-arquitecto-mvc.md` (V12), `5-implementador.md` (V12, desvíos + OBS-V12-01/02). Working tree sin commitear, 5 archivos modificados. Build y `publish` re-verificados por QA de forma independiente: 0 errores, 0 advertencias.

**Veredicto: APROBADO CON OBSERVACIONES para HU-12.1 / HU-12.2 / HU-12.3 — HU-12.4 (retiro de Carga Masiva/Ajuste) SE RETIENE, no debe liberarse en este sprint.**

### 0. Metodología de este pase — qué se pudo verificar y qué no

Arquitectura V12 §5 exigió verificación **por navegador** de la fila "+ Nuevo color". **El servidor MCP `playwright` no está expuesto en esta sesión** (igual que en el barrido del mismo día: figura en `.mcp.json` pero no hay herramientas `mcp__playwright__*` disponibles). Se declaró explícitamente y se compensó con tres niveles de verificación real —no sólo inspección de código—, que cubren todo el stack **menos la ejecución del JavaScript**:

| Nivel | Qué se hizo | Qué cubre |
|---|---|---|
| **N1 — Banco de model binding real** | App ASP.NET Core mínima levantada en `127.0.0.1:5199`, referenciando el **ViewModel real** (`ShowroomGriffin.Application`) y con la **misma** `UseRequestLocalization` (es-AR fija) que `Program.cs` L191-198. 13 POST de formulario contra `StockMatrizGuardarViewModel` | Nulabilidad (D-01), cultura decimal (D-02/OBS-V12-01), contigüidad de índices de `Altas[]` |
| **N2 — App real end-to-end** | `ShowroomGriffin.Web` levantada en `https://127.0.0.1:5272` contra la BD de **desarrollo** (`localhost/showroomgriffin`), login real como SuperUsuario, 6 POST autenticados con antiforgery a `/Stock/MatrizEditar` | Controller + `StockService` + `VarianteService` + persistencia MySQL reales |
| **N3 — Inspección del HTML renderizado** | `curl` autenticado sobre `/Stock/Index`, `/Stock/Matriz`, `/Stock/MatrizEditar`, `/Stock/CargaMasiva`, `/Stock/Ajuste` | Layout de accesorios, presencia y forma de la fila "+ Nuevo color", `SEP_DECIMAL` emitido, `altasNextIndex`, botones ocultos, rutas vivas |
| **N4 — Ejecución del JS en navegador** | **NO REALIZADO — BLOCKED** | `construirAltasDeColoresNuevos()`, `aDecimalServidor()` y `sincronizarPrecioYMinimoDeAltas()` **en ejecución** |

**Por qué N4 importa y no es un formalismo:** el catálogo cross-proyecto ya tiene el precedente exacto — **GAN-003** (`Egresos/Create`, grilla dinámica de filas nuevas) documenta un fallo **silencioso**, sin excepción en consola, en el que el JS producía **0 filas** y el POST salía sin los datos. Su `pruebas_minimas` dice literalmente *"end-to-end real por navegador (no solo por POST HTTP directo)"*. La fila "+ Nuevo color" pertenece a esa misma clase de riesgo. Todo lo que este pase verificó es que **el payload correcto produce el resultado correcto**; lo que no verificó es que **el JS efectivamente produzca ese payload**.

**Dato de entorno relevante:** la BD de desarrollo está **desactualizada** — última migración aplicada `20260612155208_V8_MarcaStandalone`; `20260816155505_V9_UniqueIndexVarianteProducto` **no está aplicada**. Ver D-V12-04.

### 1. Alcance funcional validado

- Accesorios (`Modelo.TipoTalle == null`) visibles y editables en `/Stock/Matriz` y `/Stock/MatrizEditar` como tabla Color | Cantidad (D1).
- Fila "+ Nuevo color" al final de cada sección, con y sin talle (D2).
- Ocultamiento de los botones "Ajuste manual" y "Carga masiva" de la cabecera de `/Stock/Index`, con rutas vivas (D3/D4).
- Cambios de contrato en `StockMatrizAltaGuardarViewModel` (`Color` → `string?`, `TalleConfigId` → `int?`) y validación condicional de Talle en `GuardarMatrizAsync`.
- Fix OBS-V12-01 (`aDecimalServidor()`) — fuera del alcance literal de V12, incorporado por el Implementador.

### 2. Cobertura por criterio de aceptación

| # | Criterio (HU) | Resultado | Evidencia |
|---|---|---|---|
| C-V12-01 | HU-12.1 — Marca con accesorios muestra sección Color \| Cantidad en `/Stock/Matriz` | **PASS** | N3: `GET /Stock/Matriz?marcaId=4` → 200, `<th>Color</th>` + `<th>Cantidad</th>`, sin columnas de talle, con link `Historial?varianteId=5` |
| C-V12-02 | HU-12.1 — misma sección editable en `/Stock/MatrizEditar` | **PASS** | N3: tabla de 3 columnas (Color \| Cantidad \| Precio/mín.), `Celdas[0].VarianteId=5` + `Celdas[0].CantidadNueva=4` precargada |
| C-V12-03 | HU-12.1 — editar la Cantidad de un accesorio existente guarda | **PASS** | N2 (T4): POST `Celdas[0].CantidadNueva=7` → 302 redirect, `Stocks.StockActual` 4 → 7 en BD |
| C-V12-04 | HU-12.2 — alta de Color nuevo con cantidad en 2+ Talles a la vez | **PASS (servidor) / BLOCKED (JS)** | N1 (C1): `Altas[2]`+`Altas[3]` mismo Color, 2 talles, mismo precio → bindean correctamente. La **generación** de esos índices por JS no se pudo ejecutar |
| C-V12-05 | HU-12.2 — Color tipeado sin ninguna cantidad → no crea nada, sin error | **BLOCKED** | Es una decisión 100% del JS (`if (cargadas.length === 0) return;`). Correcta por lectura; no ejecutada |
| C-V12-06 | HU-12.2 — fila "+ Nuevo color" vacía no rompe el guardado del resto (modo de falla D-01) | **PASS** | N1 (B1, B2) + N2 (T4): `ModelState` **válido** con `Altas[0]` íntegramente vacío; las `Celdas` se persisten |
| C-V12-07 | HU-12.2 — cantidades sin Color → aviso y no se envía | **BLOCKED** | Validación exclusivamente de UI. El servidor tiene su red de contención (`"El color es obligatorio."`), verificada por lectura |
| C-V12-08 | HU-12.2 — Color+Talle ya existente → error puntual, sin perder el resto | **PASS** | N2 (T6): POST duplicado exacto → 200 con `<li>Color "QA-Dorado": Ya existe una variante con esa combinación…</li>`, resto del POST preservado |
| C-V12-09 | HU-12.3 — alta de Color nuevo de accesorio crea 1 variante con `TalleConfigId` null | **PASS** | N2 (T1): variante creada en MySQL con `TalleConfigId = NULL`, `StockActual = 3` |
| C-V12-10 | HU-12.3 — sin Precio / sin Mínimo → error puntual de esa alta | **PASS** | N1 (B2) + lectura de `GuardarMatrizAsync` L847-859: `decimal?`/`int?` → null → error de negocio por fila, no de binding |
| C-V12-11 | HU-12.4 — `/Stock/Index` sin botones "Ajuste manual" ni "Carga masiva" en la cabecera | **PASS parcial** | N3: 0 ocurrencias de "Carga masiva"; **1 ocurrencia de "Ajuste manual"** — el botón por fila de la grilla sigue presente. Ver D-V12-08 |
| C-V12-12 | HU-12.4 — `/Stock/Ajuste` y `/Stock/CargaMasiva` responden por URL directa | **PASS** | N2: ambas → **200** autenticado como Admin; sin sesión → 302 al login, mientras `/Stock/NoExiste` → **404** (prueba de que la ruta existe, no es un 404 disfrazado) |
| C-V12-13 | **OBS-V12-01** — el precio llega al Service sin corromperse ×100 | **PASS condicionado** | N2 (T1): `"39990,50"` → persistido **39990.50**. Pero ver D-V12-01: la protección es únicamente del lado del cliente |
| C-V12-14 | Regresión — celdas "—" siguen funcionando, sin colisión de índices con el JS | **PASS** | N3: `altasNextIndex value="2"` coincide exactamente con los 2 `Altas[]` estáticos renderizados (índices 0 y 1) |
| C-V12-15 | Permisos — `MatrizEditar` exige `RequireAdministrador` | **PASS** | Estático: `[Authorize(Policy="RequireAdministrador")]` en GET y POST + `[ValidateAntiForgeryToken]`. Runtime: sin sesión → 302 al login. **No verificado con un usuario Empleado real** (no hay cuenta sembrada con ese rol en dev) |

### 3. Cobertura de máquina de estados

**No aplica.** V12 no toca ninguna máquina de estados (Compra, Venta, Devolución). El único flujo con estados que atraviesa es el ajuste de stock, que es una transición simple sin máquina (`AplicarAjusteInternoAsync` + `MovimientoStock`), ya cubierta en pases anteriores y verificada sin cambios de comportamiento en N2 (T4).

### 4. Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`, 34 ítems)

| id | aplica | resultado | acción |
|---|---|---|---|
| REG-001 (RowVersion al crear variante) | sí | **PASS** | N2 (T1): variante creada sin `DbUpdateException` |
| REG-002 (stock inicial al crear variante) | sí | **PASS** | N2 (T1): `StockActual = 3` desde el alta |
| REG-003, REG-005, REG-007 (autocompletes Select2) | no | N/A | Módulos no tocados |
| REG-004 (máquina de estados Compra) | no | N/A | — |
| REG-006 (medio de pago Cuotas) | no | N/A | — |
| REG-008 (input pierde foco por re-render) | sí (patrón) | **PASS** | `MatrizEditar` no re-renderiza filas por keystroke; el JS sólo corre en el submit |
| REG-009 (cascada categoría→subgrupo) | no | N/A | — |
| REG-010 (link de sidebar sin guard de rol) | sí (patrón) | **PASS** | `_Layout.cshtml` sin cambios; el botón por fila de `/Stock/Index` sí está envuelto en `@if (SuperUsuario \|\| Administrador)` |
| KOI-001 (`btn-swal-confirm` fuera del form) | sí (patrón) | **PASS** | El submit se maneja por `$('#formMatrizEditar').on('submit')`, no por `data-form-id` |
| KOI-002, KOI-003, KOI-006 | no | N/A | Otro proyecto, módulos inexistentes acá |
| KOI-004 (validación bloqueante sólo en cliente) | sí (patrón) | **PASS** | La validación "cantidades sin Color" es de UI, **pero** el servidor la duplica (`"El color es obligatorio."`) — defensa en profundidad correcta |
| KOI-005 (controller/ruta inexistente detrás de un link) | sí (patrón) | **PASS** | Inverso de este caso: se verificó que las rutas sobreviven al retiro de los botones (C-V12-12) |
| DN-001, DN-002 (DataTables server-side) | no | N/A | — |
| GAN-001 (grilla dinámica de pagos) | sí (patrón) | **BLOCKED** | Mismo patrón que la fila "+ Nuevo color"; no verificable sin navegador |
| **GAN-003** (grilla dinámica que falla en silencio; exige navegador) | **sí (patrón)** | **BLOCKED** | **Ítem más relevante del catálogo para esta entrega.** Su `condicion_falla` sólo se evalúa en un navegador real. Ver §0 y la guía manual |
| GAN-002 (migración con backfill) | no | N/A | V12 no trae migración |
| GAN-004 (datalist nativo) | no | N/A | — |
| VSF-001, VSF-002 | no | N/A | — |
| CRM-001 … CRM-006 | no | N/A | Otro proyecto (bot/CRM) |
| MH-001 (`IN` de colección local en EF) | sí | **PASS** | `tipoTallePorProducto` usa `productoIds.Contains(p.Id)` — resuelto una sola vez antes del loop; ejecutado sin error en N2 |
| MH-002 … MH-008 | no | N/A | — |
| MH-009 (`moment.utc` en listados) | no | N/A | Listados no tocados |
| **SG-001** (POST completo bloqueado por ViewModel no nullable) | **sí** | **PASS** | N1 (B1/B2) + N2 (T4): no reaparece. Ver §5 para el matiz de `Celdas[]` |

**Resumen:** 34 ítems recorridos — 13 aplicables, **11 PASS**, **2 BLOCKED** (GAN-001 y GAN-003, ambos por falta de navegador), 21 N/A.

### 5. Defectos detectados

#### D-V12-01 — La protección contra la corrupción ×100 del precio es exclusivamente del lado del cliente — **CRÍTICO (riesgo residual)**

El diagnóstico del Implementador en OBS-V12-01 es **correcto y quedó reproducido de punta a punta**, pero el fix no cierra el problema: lo mitiga desde el navegador y deja al servidor sin ninguna defensa.

Reproducción (N2, app real + MySQL real, POST autenticado a `/Stock/MatrizEditar`):

| Test | `Altas[0].PrecioVenta` posteado | Persistido en `VariantesProducto.PrecioVenta` | HTTP |
|---|---|---|---|
| T1 (con el fix) | `39990,50` | **39990.50** ✔ | 302 (éxito) |
| T2 (control, sin el fix) | `39990.50` | **3999050.00** ✘ ×100 | 302 (éxito, **sin ningún error**) |
| T3 (control, precio **entero**) | `33000.00` | **3300000.00** ✘ ×100 | 302 (éxito, **sin ningún error**) |

**T3 es el hallazgo que corrige la evaluación de riesgo del Implementador.** En `5-implementador.md` se afirma: *"Para valores enteros (el caso dominante en producción) la conversión es no-op, así que el riesgo de regresión es mínimo"*. Eso es cierto para lo que el usuario **tipea a mano** en `.nc-precio`, pero **no** para el camino de la celda "—", que es el flujo dominante: el hidden se renderiza con `inv(fila.PrecioVentaSugerido)` sobre un `decimal(18,2)`, que **siempre** emite dos decimales. Verificado en el HTML real servido:

```
name="Altas[0].PrecioVenta" class="alta-precio" data-row-idx="0" value="50000.00"
name="Altas[1].PrecioVenta" class="alta-precio" data-row-idx="1" value="60000.00"
```

Es decir: **el servidor renderiza el valor ya en el formato que él mismo va a interpretar mal**, y la única cosa que lo salva es que `sincronizarPrecioYMinimoDeAltas()` lo sobrescriba antes del submit. Si por cualquier motivo ese handler no llega a correr (jQuery que no carga, una excepción JS anterior en el mismo `$(function(){...})`, una extensión de navegador), el POST sale con `"50000.00"`, el servidor responde **302 de éxito** y persiste **5.000.000**. Silencioso, sin error, sin traza.

Confirmado también contra el binder aislado (N1): `"45000.00"` → `4500000`; `"45000,00"` → `45000,00`. Y `SEP_DECIMAL` sí se emite como `,` en el HTML real, o sea que el helper está bien cableado.

- **Severidad:** crítica por impacto (corrupción silenciosa de datos), baja por probabilidad. No es una regresión de V12 — V12 **mejora** la situación anterior — pero deja el sistema dependiendo de que el JS corra siempre.
- **Fix propuesto (NO aplicado):** `Altas[i].PrecioVenta` es un `<input type="hidden">` (MatrizEditar.cshtml L194), **no** un `type="number"`. La razón que motivó `inv()` en SG-001 (el saneamiento HTML5 del `value` de un input numérico) **no aplica a un hidden**. Renderizarlo con la cultura del servidor (`@fila.PrecioVentaSugerido` directo) haría que el round-trip fuera correcto **sin depender de JS**; `inv()` queda sólo donde hace falta, en los visibles `#rowPrecio_X` y `.nc-precio`. Alternativa de raíz: un `IModelBinderProvider` de decimal invariante, que además cerraría el problema en todo el sistema.

#### D-V12-02 — Un Color que difiere sólo en mayúsculas/acentos crea una variante duplicada en silencio — **MAYOR**

Reproducido en N2 (T5): con la variante `QA-Dorado` ya existente para el mismo Producto y `TalleConfigId` null, se posteó un alta con Color `qa-dorado` → **302 de éxito y se creó la variante Id 9 `qa-dorado`**, duplicando la anterior.

- **Causa raíz:** `GuardarMatrizAsync` compara con `==` de C# (ordinal, sensible a mayúsculas): `combinacionesExistentes.Any(c => c.Color == colorAlta …)` (L869) y `combosEnEsteLote` (`HashSet<(int,string?,int?)>`, comparador ordinal por defecto). La columna `VariantesProducto.Color` es `utf8mb4_0900_ai_ci` — **insensible a mayúsculas y a acentos**.
- **Por qué es específico de V12:** hasta ahora el `Color` de un alta venía de un hidden con el valor exacto ya almacenado, así que jamás podía diferir en casing. Con la fila "+ Nuevo color" pasa a ser texto tipeado a mano. Agrava el problema que **ambas vistas muestran el color en minúscula** (`@fila.Color.ToLower()` con `text-capitalize`), de modo que el usuario **no puede ver** el casing real almacenado: ve "Dorado" y tipea "Dorado" aunque en la base diga "DORADO".
- **Dos modos de falla según el entorno:** sin el índice único V9 aplicado (caso de la BD de desarrollo hoy) → **se crea el duplicado**. Con V9 aplicado → la columna generada `ClaveUnicaVariante` hereda la collation `ai_ci`, el `INSERT` viola el índice, cae en el `catch` genérico y el usuario ve **"No se pudo crear la variante."** en lugar del mensaje correcto ("Ya existe una variante con esa combinación…"). En ninguno de los dos casos el comportamiento es el esperado.
- **Fix propuesto (NO aplicado):** comparar con `string.Equals(..., StringComparison.OrdinalIgnoreCase)` y usar `StringComparer.OrdinalIgnoreCase` en el `HashSet`. Cubre el casing; los acentos seguirían divergiendo de la collation `ai_ci` (aceptable, o normalizar).

#### D-V12-03 — La Matriz no puede crear una variante con stock inicial 0, pero Carga Masiva sí — **MAYOR (bloquea HU-12.4)**

- `GuardarMatrizAsync` L816: `if (!alta.CantidadNueva.HasValue || alta.CantidadNueva.Value <= 0) continue;` — sin cantidad no hay alta.
- El JS refuerza lo mismo: `if (isNaN(cantidad) || cantidad <= 0) return;`.
- `GuardarCargaMasivaAsync`, en cambio, **crea la variante igual** y sólo aplica el ajuste si hay cantidad: `if (fila.CantidadNueva.HasValue && fila.CantidadNueva.Value > 0)`.

Consecuencia: dar de alta un color/talle nuevo **sin stock todavía** (catálogo de temporada cargado antes de que llegue la mercadería) es un caso que hoy sólo resuelve `/Stock/CargaMasiva`. El Análisis condicionó el retiro a que *"la Matriz cubra el 100% de los casos de uso de ambas"* (§Alcance) y D4 eligió retirar **en el mismo sprint, sin período de validación**. Esa premisa **no se cumple**.

#### D-V12-04 — La migración `V9_UniqueIndexVarianteProducto` no está aplicada en desarrollo; falta confirmar producción — **MAYOR (entorno)**

`__EFMigrationsHistory` en `localhost/showroomgriffin` llega hasta `20260612155208_V8_MarcaStandalone`. `20260816155505_V9_UniqueIndexVarianteProducto` existe en el código pero **no está aplicada**. Tanto el Análisis V12 (§"Actores, permisos y reglas críticas heredadas") como Arquitectura V12 (§3) apoyan explícitamente el diseño de V12 en ese índice como respaldo de la deduplicación. Sin él, la única defensa contra duplicados es la aplicativa — que D-V12-02 demuestra que es insuficiente. **Confirmar en producción antes de deployar**, y sincronizar dev (si no, cualquier prueba manual que se corra sobre dev observará un comportamiento distinto al de producción).

#### D-V12-05 — `modelo.ProductoId` toma un Producto arbitrario cuando el Modelo tiene más de uno — **MEDIO (preexistente, amplificado)**

`ObtenerMatrizAsync` L649: `ProductoId = grupoModelo.Select(s => s.VarianteProducto.ProductoId).FirstOrDefault()`. La fila "+ Nuevo color" postea ese `ProductoId` para **todas** sus altas. En los datos de desarrollo ya existe el caso: el Modelo 1 (`JORDAN 1`) tiene los Productos 3 y 5 activos. Preexistente de la Etapa 3.1, pero V12 lo amplifica: antes se creaba un talle de un Color que ya vivía en ese Producto; ahora se puede crear un Color entero contra el Producto equivocado.

#### D-V12-06 — `TipoTalle IS NULL` no equivale a "accesorio" en los datos reales — **MEDIO**

El diseño asume que `Modelo.TipoTalle == null` identifica accesorios (bijou, carteras). En la base de desarrollo los únicos Modelos con `TipoTalle NULL` son **`JORDAN 1` y `JORDAN RETRO 4`** — calzado con el campo sin configurar. Antes de V12 esas secciones se descartaban en silencio; ahora se muestran como secciones "sin talle" **editables**, con una fila "+ Nuevo color" que crea variantes de calzado con `TalleConfigId = null`. **Confirmar el estado de `Modelos.TipoTalle` en producción** antes del deploy; si hay calzado sin configurar, V12 habilita cargar stock mal modelado.

#### D-V12-07 — Se pierde lo tipeado en la fila "+ Nuevo color" ante cualquier error parcial — **MENOR**

`ReconstruirVistaEdicionAsync` re-inyecta las `Celdas` por `VarianteId`, pero las altas sólo se exponen como lista en `ViewBag.AltasConError`; la fila "+ Nuevo color" se re-renderiza vacía (no tiene `name` ni `value` de servidor). Simplificación ya aceptada en la Etapa 3.1, pero el costo creció: ahora se puede perder un Color + N cantidades + precio + mínimo por un error en una celda no relacionada.

#### D-V12-08 — HU-12.4 cumplida sólo parcialmente: el botón "Ajuste manual" por fila sigue visible — **MENOR (decisión del cliente)**

Confirmado en el HTML servido de `/Stock/Index`: 0 ocurrencias de "Carga masiva", pero **1 de "Ajuste manual"** — el botón por fila de la grilla (`/Stock/Ajuste?varianteId=`, `Index.cshtml` L213), correctamente restringido a Admin/SuperUsuario. El Implementador ya lo dejó documentado como decisión pendiente. Se confirma el hallazgo: HU-12.4 dice *"no muestra los botones 'Ajuste manual' ni 'Carga masiva'"*, y la etiqueta "Ajuste manual" sigue presente en la pantalla.

#### OBS-V12-02 (confirmada) — `Celdas[].CantidadNueva` sigue siendo `int` no nullable — **MAYOR (preexistente, superficie ampliada por V12)**

Verificado en N1 (B4): con `Celdas[0].CantidadNueva=""`, el `ModelState` queda **inválido** con `"The value '' is invalid."` y **todo el POST se descarta**, incluida `Celdas[1]`, que era válida. Es literalmente el modo de falla D-01, todavía vivo en la colección `Celdas`. Atenuantes: el fix `1122c3c` garantiza un toast rojo visible (no es silencioso) y las celdas se renderizan siempre precargadas. **Pero V12 amplía la superficie**: las secciones de accesorios que agrega usan exactamente este mismo binding. El Implementador tiene razón en que resolverlo exige una decisión funcional (¿celda vacía = ignorar, o = error puntual?); queda como ítem propio para el cliente.

### 6. Auto-fixes aplicados

**Ninguno**, por pedido explícito del usuario en esta tarea (mismo criterio que en el barrido del rechazo de `f400671`): reportar antes de tocar código. Los fixes propuestos están descritos en D-V12-01, D-V12-02 y D-V12-03. Ninguno introduce lógica de negocio nueva.

**Ítem de catálogo nuevo a crear** (pendiente de aprobación, no escrito todavía): `SG-002 — "El round-trip de un decimal a través de un formulario bajo una cultura con coma decimal se corrompe ×100 si el valor se renderiza con InvariantCulture y se postea sin convertir"`, con `deteccion_qa.tipo: static` sobre el patrón *"input (hidden o number) cuyo `value` sale de un `decimal` renderizado con `InvariantCulture` y cuyo destino es un `decimal`/`decimal?` de un ViewModel, en una app con `UseRequestLocalization` de cultura no invariante"*. Es un patrón cross-proyecto: aplica a cualquier proyecto del estudio con `es-AR` fijado, no sólo a ShowroomGriffin.

### 7. Riesgos de liberación y mitigaciones

| # | Riesgo | Severidad | Mitigación |
|---|---|---|---|
| R1 | La fila "+ Nuevo color" nunca se ejecutó en un navegador. Precedente GAN-003: este tipo de grilla falla **en silencio** y no lo detecta ningún POST HTTP directo | **Alta** | Ejecutar la guía manual de §9 (15 min) antes del deploy. Es el gate que Arquitectura V12 §5 declaró obligatorio y que esta sesión **no pudo levantar** |
| R2 | Corrupción ×100 del precio si el JS no corre (D-V12-01) | Alta (impacto) / Baja (probabilidad) | Aplicar el fix de servidor propuesto. Mientras tanto: tras el primer uso real, verificar `SELECT Id, PrecioVenta FROM VariantesProducto WHERE CreatedAt >= CURDATE()` |
| R3 | Duplicados por casing (D-V12-02), agravados si V9 no está en producción (D-V12-04) | Alta | Confirmar V9 en producción **antes** del deploy + fix de comparación insensible a mayúsculas |
| R4 | Retirar `CargaMasiva` sin cubrir el alta con stock 0 (D-V12-03) | Alta | **No liberar HU-12.4 en este sprint.** Volver a D4 (opción A: dos entregas separadas) o cubrir el caso en la Matriz |
| R5 | Calzado con `TipoTalle` sin configurar expuesto como "accesorio" (D-V12-06) | Media | Auditar `Modelos.TipoTalle` en producción antes del deploy |
| R6 | El working tree no está commiteado y la BD de dev quedó desincronizada respecto de producción (V9) | Media | Sincronizar dev antes de que el cliente corra las pruebas manuales, o correrlas contra un entorno con V9 |

### 8. Pruebas mínimas ejecutadas en este pase

**N1 — binder real (13 POST):** A1-A6 cultura decimal · B1-B4 nulabilidad · C1-C3 forma del payload. Destacados: **A1** `"45000.00"` → `4500000`; **A2** `"45000,00"` → `45000,00`; **B2** fila enteramente vacía → `ModelState` **válido**; **B4** `Celdas[].CantidadNueva` vacía → **inválido** (OBS-V12-02); **C2** control negativo con hueco de índice (`Altas[0]` + `Altas[3]`) → el binder **corta en el hueco** y bindea 1 sola alta, confirmando que la contigüidad que genera el JS es una propiedad crítica y no un detalle.

**N2 — app real end-to-end (6 POST autenticados):** T1 alta de accesorio con precio decimal → **39990.50 correcto** · T2 control sin conversión → **3999050 ×100** · T3 control con precio entero → **3300000 ×100** · T4 fila "+ Nuevo color" vacía + celda modificada → guarda la celda, no crea nada · T5 duplicado por casing → **crea duplicado** · T6 duplicado exacto → error puntual correcto.

**N3 — HTML servido:** `/Stock/Index` (botones), `/Stock/Matriz` y `/Stock/MatrizEditar` con y sin talle, `/Stock/CargaMasiva`, `/Stock/Ajuste`, `/Stock/NoExiste` (404 de contraste), `SEP_DECIMAL = ','`, `altasNextIndex = 2` coherente con los `Altas[]` estáticos, `.nc-cantidad` de accesorio **sin** `data-talle-id` (correcto: el JS omite `TalleConfigId`).

**Datos de prueba:** la BD de desarrollo no tenía ningún accesorio válido (la única variante con `TalleConfigId NULL` cuelga del Producto 1, soft-deleted, por lo que el filtro global la excluye y `/Stock/MatrizEditar?marcaId=4` mostraba "Esta marca no tiene stock cargado para editar" — comportamiento **correcto**, no un defecto). Se sembró temporalmente 1 variante de accesorio para poder ejercitar HU-12.1/12.3 y **se eliminó todo al terminar**: variantes 4-9 (`QA-*`) y sus filas de `Stocks`, `MovimientosStock` y `AjustesStock`. Estado final verificado: 3 variantes / 3 stocks (idéntico al inicial), 0 registros huérfanos, 0 precios ≥ 1.000.000.

### 9. Guía de verificación manual por navegador — pendiente, prioridad ordenada (~15 min)

Requisitos: sesión como Administrador o SuperUsuario; una Marca con al menos un Modelo **con** talle y celdas "—", y otra con un Modelo **sin** `TipoTalle`. Correr preferentemente contra un entorno **con la migración V9 aplicada** (ver D-V12-04).

**(d) — PRIMERO, el de mayor severidad: precio decimal (OBS-V12-01)**
1. `/Stock/MatrizEditar?marcaId=X`. Antes de tocar nada, abrir DevTools → Network.
2. Cargar una cantidad en una celda "—" de una fila cuyo **Precio sugerido** aparezca con decimales (o escribirle `45000.50` al input de Precio de esa fila). Motivo → Guardar → confirmar.
3. En Network, abrir el POST → **Form Data** → buscar `Altas[N].PrecioVenta`. **Debe decir `45000,50` (coma). Si dice `45000.50` (punto), el fix NO se aplicó y el precio se va a guardar ×100.**
4. Verificar la variante creada en `/Productos` o por SQL: `PrecioVenta` debe ser **45000,50**, nunca **4.500.050**.
5. Repetir tipeando `45000.50` en el Precio de la fila "+ Nuevo color".
6. Repetir con un precio **entero** (ej. 45000) — es el caso dominante y el que T3 demostró que también se corrompe si el JS no convierte.

**(a) — Alta de Color nuevo con cantidad en 2+ Talles a la vez (HU-12.2)**
7. En un Modelo con talle, en la fila "+ Nuevo color": tipear un Color inexistente, cargar cantidad en **dos columnas de Talle distintas**, completar Precio y Mínimo. Guardar.
8. Esperado: se crean **2 variantes**, mismo Color, mismo Precio y mismo Mínimo, con sus stocks iniciales. En Network, el POST debe llevar **dos bloques `Altas[N]` con índices consecutivos** arrancando donde termina `altasNextIndex`. **Si el JS falla (patrón GAN-003), no aparece ningún `Altas[]` generado y el guardado "no hace nada" sin error.**
9. Cancelar el SweetAlert2, cambiar un valor y volver a guardar → **no** deben duplicarse las altas.

**(b) — Fila "+ Nuevo color" dejada vacía (el caso más frecuente; modo de falla D-01)**
10. Modificar 2 celdas con stock, dejar **todas** las filas "+ Nuevo color" intactas. Guardar.
11. Esperado: se guardan las 2 celdas, no se crea ninguna variante, **ningún** toast rojo. (Verificado ya en N2/T4 del lado servidor; falta confirmar que el JS no inyecta basura.)
12. Variante: tipear sólo el Color, sin ninguna cantidad → tampoco debe crearse nada ni aparecer error.
13. Variante: cargar cantidades **sin** Color → debe aparecer el aviso amarillo y el formulario **no** debe enviarse.

**(c) — Alta de Color nuevo en un accesorio (HU-12.3)**
14. Elegir una Marca con un Modelo sin `TipoTalle`. Confirmar que la sección se ve como tabla **Color | Cantidad** (sin columnas de talle) y que existe la fila "+ Nuevo color".
15. Cargar Color + Cantidad + Precio + Mínimo → debe crearse **1** variante con Talle vacío.
16. Probarla sin Precio y sin Mínimo → error puntual de esa alta, sin tirar abajo el resto del guardado.
17. **Además (D-V12-02):** tipear un Color que ya existe en esa tabla pero **cambiando mayúsculas** (si la grilla muestra "dorado", tipear "DORADO"). Esperado correcto: error "Ya existe una variante con esa combinación". Lo que se observó en dev: **se creó un duplicado**.

**(e) — Rutas ocultas siguen vivas (HU-12.4)**
18. `/Stock/Index` → confirmar que no están los botones de cabecera "Ajuste manual" ni "Carga masiva" (sí sigue el ícono de ajuste **por fila**, ver D-V12-08).
19. Navegar a `/Stock/CargaMasiva` y `/Stock/Ajuste` escribiendo la URL → ambas deben cargar normalmente. (Ya verificado en N2: 200 en ambas.)
20. **Regresión:** una Marca sólo con calzado debe verse y comportarse exactamente igual que antes de V12.
21. **Permisos:** con un usuario Empleado, `/Stock/Matriz` debe abrir y `/Stock/MatrizEditar?marcaId=1` debe rechazar. (No verificable en dev: no hay cuenta con ese rol sembrada.)

### 10. Checklist de salida para merge

```
[x] Build verde (0 errores, 0 advertencias) — re-verificado por QA de forma independiente
[x] Sin migración EF en V12 (confirmado contra Arquitectura)
[x] D-01 NO reaparece: Altas[] íntegramente nullable, verificado contra el binder real (N1 B1/B2 + N2 T4)
[x] Altas[].Color y Altas[].TalleConfigId confirmados nullable por QA en el código, no por palabra del Implementador
[x] Contigüidad de índices de Altas[] validada, incluido control negativo con hueco (N1 C2)
[x] altasNextIndex coherente con los Altas[] estáticos renderizados (N3)
[x] Permisos: RequireAdministrador + antiforgery en GET y POST de MatrizEditar
[x] /Stock/Ajuste y /Stock/CargaMasiva vivas por URL directa (200), 404 de contraste verificado
[x] Accesorios: render de lectura y de edición correcto, alta con TalleConfigId null persistida (N2 T1)
[x] Catálogo cross-proyecto recorrido (34 ítems; 13 aplicables, 11 PASS, 2 BLOCKED)
[x] Datos de prueba sembrados en dev y eliminados por completo (estado inicial restaurado, 0 huérfanos)
[ ] D-V12-01 — protección ×100 sólo del lado del cliente; el servidor acepta y persiste el valor corrupto  ← ENDURECER ANTES DEL DEPLOY
[ ] D-V12-02 — duplicado por casing crea variante duplicada en silencio  ← FIX PENDIENTE
[ ] D-V12-03 — la Matriz no cubre el alta con stock 0 que sí cubre CargaMasiva  ← BLOQUEA HU-12.4
[ ] D-V12-04 — confirmar V9_UniqueIndexVarianteProducto aplicada en producción; dev está en V8
[ ] D-V12-05 — ProductoId arbitrario en Modelos con más de un Producto (preexistente, amplificado)
[ ] D-V12-06 — auditar Modelos.TipoTalle en producción antes del deploy
[ ] D-V12-07 — se pierde lo tipeado en la fila "+ Nuevo color" ante error parcial (menor)
[ ] D-V12-08 — botón "Ajuste manual" por fila sigue visible (decisión del cliente)
[ ] OBS-V12-02 — Celdas[].CantidadNueva sigue int no nullable (confirmado, decisión funcional pendiente)
[ ] Verificación por navegador (MCP playwright no expuesto en esta sesión) — guía manual en §9  ← GATE OBLIGATORIO
[ ] Catalogar SG-002 (round-trip de decimales bajo cultura no invariante) — pendiente de aprobación
```

### 11. Conclusión de proceso

El flujo completo del estudio **funcionó**: V12 llegó a QA sin el defecto D-01 que hundió a `f400671`, y el Implementador encontró y documentó por su cuenta un bug de producción latente (OBS-V12-01) que el barrido anterior no había visto. Ese es exactamente el resultado que se buscaba al sacar esta feature del fast-path.

Dicho eso, quedan dos lecciones. La primera: **el fix de OBS-V12-01 se evaluó por su lado feliz.** La afirmación "para valores enteros la conversión es no-op, el riesgo es mínimo" no resiste la prueba T3 — el camino dominante renderiza `"33000.00"` desde un `decimal(18,2)` y se corrompe igual. Un fix de client-side sobre un valor que el servidor ya emitió mal es una mitigación, no una solución. La segunda: **el gate por navegador sigue sin poder ejecutarse.** Es la segunda vez consecutiva que se declara obligatorio y no hay herramienta para cumplirlo. Si el MCP `playwright` no va a estar disponible, conviene decidir explícitamente quién corre la guía manual y cuándo, en vez de dejar el gate marcado como obligatorio y sistemáticamente sin cumplir.
