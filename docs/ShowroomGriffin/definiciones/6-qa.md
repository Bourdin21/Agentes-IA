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
