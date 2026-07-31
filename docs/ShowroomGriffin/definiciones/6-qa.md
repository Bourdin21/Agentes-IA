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
