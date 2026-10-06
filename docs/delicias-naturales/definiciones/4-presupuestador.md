# Memoria - Presupuestador

## Proyecto: delicias-naturales
## Ultima actualizacion: 2026-06-03

## Datos de presupuesto

- Sistema: Gestion Comercial Delicias Naturales
- Modulos funcionales: 19
- Stack: ASP.NET MVC 5, .NET Framework 4.7.2, EF6, MySQL
- Horas estimadas base (sin contingencia): 95 h
- Horas totales con contingencia 15%: 110 h
- Costo total estimado: USD 1.540
- Tasa efectiva presupuesto original: USD 14 / hora
- Tasa vigente desde Junio 2026: USD 45 / hora
- Fecha de presupuesto: Junio 2025
- Estado: presupuestado. Estimacion retrospectiva validada por el cliente. Iteracion evolutiva Junio 2026 cerrada (4 h / USD 160).

## Perfil tecnico

- Entidades: 26
- Controladores: 19
- Migraciones EF evolutivas: 25
- Integraciones AFIP: 5
- Maquinas de estado: multiples
- Tecnologias adicionales: SignalR, reportes PDF, soft-delete

## Dataset de modulos reales (horas finales con 30% incluido)

| Modulo | Tipo | Horas finales (con 30%) |
|---|---|---|
| Notificaciones SignalR | Notificaciones | 4.5 h |
| Gestion de pedidos | Workflow | 10 h |
| ABM Pedidos | ABM complejo | 10.5 h |
| ABM Descuentos | ABM intermedio | 6.5 h |
| ABM Pagos | ABM intermedio | 5 h |
| ABM Compras | ABM complejo | 15 h |
| ABM Proveedores | ABM intermedio | 7 h |
| ABM Ventas | ABM complejo | 10 h |
| ABM Categorias | ABM simple | 2 h |
| Relevamiento de Stock | ABM intermedio | 5.5 h |

## Cierre de calibracion - Iteracion evolutiva Junio 2026

| Modulo | Tipo | Horas estimadas | Horas reales | Desvio | Motivo |
|---|---|---|---|---|---|
| Solicitudes Ingreso Stock (estados por item, verificacion deposito, filtro categoria, reemplazo stock) + Pedidos (estado Listo para Retirar + email cliente) | Workflow complejo con extensiones | 4 h | 4 h | 0% | Estimacion exacta. Alcance bien delimitado, sin sorpresas tecnicas. |

- Tasa cobrada: USD 40 / hora
- Total cobrado: USD 160
- Ratio calibracion estimado/real: 1.0

## Dataset de modulos reales - Actualizacion Junio 2026

| Modulo | Tipo | Horas reales | Tasa | USD |
|---|---|---|---|---|
| Mejoras evolutivas workflow Solicitudes + Pedidos | Extensiones sobre workflow existente | 4 h | USD 40/h | USD 160 |
| Relevamiento de Stock | ABM intermedio | 5.5 h | USD 40/h | USD 220 |

Nota: los modulos historicos anteriores (columna "Horas finales con 30%") mantienen su valor en horas como referencia de esfuerzo. El costo debe recalcularse a USD 45/h para presupuestos nuevos.

## Dataset de modulos reales - Iteracion evolutiva Junio 2026 (batch mejoras)

| Modulo | Tipo | M (h) | Horas PERT | Riesgo | USD cliente | Estado |
|---|---|---|---|---|---|---|
| F1 — Badge disponibilidad stock + SweetAlert en submit | Ajuste puntual + regla de negocio | 2 h | 2.25 h | Bajo +8% | USD 34 | Presupuestado |
| F2 — Rol Vendedor acceso Pedidos | Ajuste puntual (permisos) | 1 h | 1.08 h | Bajo +8% | USD 17 | Presupuestado |
| F3 — Totalizador Pagos (Efectivo + Transferencia + cards) | Modificacion modulo financiero + UI | 2 h | 2.16 h | Bajo +8% | USD 34 | Presupuestado |
| F4 — Layout Resumen Pedido integrado (2 col, panel expandido) | Rediseno layout vista compleja | 3 h | 3.64 h | Medio +15% | USD 50 | Presupuestado |
| **Total batch** | | **8 h** | **9.13 h** | | **USD 135** | |

- Cargo IA tokens: no aplica (facturables totales 3.84 h < 4 h umbral iteraciones evolutivas).
- Tasa vigente: USD 35/h. Formula: M x $16.80.
- Etapa 1 (operacionales): F2 + F3 = USD 51. Etapa 2 (UX): F1 + F4 = USD 84.

## Dataset de modulos reales - Iteracion Dashboard Ampliado (batch reportes)

| ID | Modulo | Naturaleza | O | M | P | PERT | Riesgo | H.Finales | USD PERT | USD cliente |
|---|---|---|---|---|---|---|---|---|---|---|
| RF-D01 | Detalle por Producto *(DT-01 incluida)* | Reporte nuevo | 1.7 | 2.5 | 4.0 | 2.62 | +8% Bajo | 2.83 | $42 | $30 |
| RF-D02 | Clientes + deuda historica | Reporte nuevo | 1.7 | 2.5 | 4.5 | 2.70 | +15% Medio | 3.11 | $42 | $30 |
| RF-D03 | Pedidos: estados y conversion | Reporte nuevo | 1.0 | 1.5 | 2.5 | 1.58 | +8% Bajo | 1.71 | $25 | $20 |
| RF-D04 | Rentabilidad: margen bruto real | Reporte financiero nuevo | 2.0 | 3.0 | 5.0 | 3.17 | +15% Medio | 3.64 | $50 | $35 |
| RF-D05 | Index Dashboard | Mejora modulo existente | 0.7 | 1.0 | 1.5 | 1.03 | +8% Bajo | 1.11 | $17 | $10 |
| **Total** | | | | **10.5h** | | **11.10h** | | **12.40h** | **$176** | **$100** |

- PERT base: USD 176. Precio de lista presentado al cliente: USD 125 (subtotal interno ajustado comercialmente).
- Descuento por fidelidad 15%: USD 25. Total cobrado al cliente: **USD 100**.
- Tokens IA: no facturado (decision comercial del cliente).
- Mantenimiento anual: no incluido (decision comercial del cliente).
- Facturables PERT: 5.04h > 4h (IA tokens aplicarian por regla, pero no se cobraron).
- Deuda tecnica DT-01 (`CantidadVendida` int→decimal): absorbida en RF-D01 sin costo adicional.
- No requiere migracion EF: todos los datos existen en el modelo actual.

### Referencias historicas usadas en este batch

| Referencia | Horas base | Motivo |
|---|---|---|
| DN batch F3 Totalizador Pagos (mismo proyecto) | M = 2h | Logica financiera + UI, mismo stack |
| ShowroomGriffin Resumen Semanal | M = 2h | Reporte con query + tabla + chart en MVC |
| Banda estandar "Nuevo reporte o exportacion" | 1-2h (med. 1.5h) | Base de partida para todos los modulos |

### Autocorreccion

| ID | PERT | Ref. base | Ratio | Decision |
|---|---|---|---|---|
| RF-D01 | 2.62h | 2.0h | 1.31 >1.15 | Justificado: selector dinamico + 2do nivel agregacion + DT-01 + UnidadMedida + grafico |
| RF-D02 | 2.70h | 2.0h | 1.35 >1.15 | Justificado: SaldoFavor + query historica + tabla ordenable 6 cols |
| RF-D03 | 1.58h | 1.5h | 1.05 OK | En rango. Sin ajuste. |
| RF-D04 | 3.17h | 2.0h | 1.59 >1.15 | Justificado: JOIN cross-entity + margen negativo + PrecioCompra=0 + grafico horizontal |
| RF-D05 | 1.03h | 0.75h | 1.37 >1.15 | Justificado: badge requiere query real en controller action |

Sanity check total: M promedio 2.1h/item vs batch anterior 2.0h/item. Ratio 1.05. OK.

---

## Presupuesto SALTEADO — Iteracion "Editar Pago" (2026-09-07)
Joaquin pidio avanzar directo a Implementacion sin presupuestar esta iteracion, tratandola explicitamente como **deuda tecnica interna** (no como feature facturable al cliente) — mismo criterio de excepcion de proceso ya usado en otros proyectos del estudio (ver `docs/vinosefue`, `docs/ganaderia` v17, `docs/kite-punta-lara`: "presupuesto salteado por pedido del cliente/usuario"). Arquitectura (iteracion 3, `3-arquitecto-mvc.md`) queda como el ultimo gate formal antes de Implementacion para esta iteracion. Sin costo/horas registradas para este item.

## Historial de ajustes
- 2025-06-01: presupuesto inicial registrado
- 2026-04-22: datos de modulos incorporados al dataset de calibracion Abril 2026
- 2026-06-xx: cierre iteracion evolutiva. 4 h reales, USD 160. Tasa actualizada a USD 40/h en parametros globales.
- 2026-06-03: Modulo Relevamiento de Stock cerrado con 5.5 h reales (5h 30min). Incorporado al dataset de modulos reales como ABM intermedio. USD 220 a tasa USD 40/h.
- 2026-06-03: Tasa actualizada a USD 45/h. Las horas ya no se exponen al cliente en documentos de presupuesto.
- 2026-06-28: Batch de 4 mejoras evolutivas presupuestado. M total 8 h, USD 135. Tasa vigente USD 35/h. Sin cargo IA tokens (facturables < 4 h).
- 2026-06-28: Presupuesto standalone F1 + F2 (mejoras propuestas por usuario). M total 3 h, USD 51. Sin cargo IA tokens (facturables 1.44 h < 4 h).
- Sesion actual: Dashboard Ampliado. 5 items, M total 10.5h, PERT USD 176. Precio comercial acordado USD 100 (descuento fidelidad $25 sobre lista $125). DT-01 absorbida en RF-D01.

---

## Iteracion 2026-10-06 — Cobro de Cuenta Corriente (ya entregado) + Presupuesto Usuarios inactivos

Dos items en una sola sesion, de naturaleza distinta:
- **Lote CC** — funcionalidad **ya implementada y en produccion** desde el 2026-07-31 que nunca se facturo. Se presupuesta retroactivamente para cobrar. Alcance = hecho, no estimado: se reconstruyo por `git show` de los commits reales.
- **Lote USR** — funcionalidad **a desarrollar**. Sin definiciones 1/2/3 escritas (el pedido llego como conversacion). Estimacion **preliminar con alcance declarado por el presupuestador**, sujeta a confirmacion — ver "Gate" abajo.

Linea de negocio de los dos lotes: **Merge / post-entrega sobre sistema propio ya entregado** → factor 2.5, `M x $16.80`, tasa USD 35/h.
**No aplica** descuento de expansion agresiva ni descuento por volumen (ambos excluyen Merge y post-entrega por definicion: ahi esta el margen del negocio). Precio de lista siempre.
**Paso 0.5:** no corresponde consulta a `olvidata-ceo` por tier — no es Build inicial de cliente nuevo, no hay tier que decidir.

### PASO 0 — Anclaje historico

| Referencia | Horas base | Motivo de la eleccion |
|---|---|---|
| DN batch F3 "Totalizador Pagos" (mismo proyecto, 2026-06-28) | M = 2 h, PERT 2.16 h | Modificacion de modulo financiero + UI, mismo repo, mismo stack. **Ancla primaria** del lote CC: mismo cliente, misma base de codigo, 4 meses de distancia. |
| DN batch Dashboard Ampliado (mismo proyecto) | 2.1 M/item | Ancla del sanity check total (PASO 8). |
| `dataset.yml` → "Nuevo ledger/cuenta corriente reutilizando patron ya existente" (vinosefue 2026-07-03, PAT-001) | M 1–1.5 h | Ancla secundaria de CC-01. **Chequeo de la regla 2026-10-06 (verificar que la base de reutilizacion EXISTE): falla parcialmente** — `Migrations/202608010201110_CuentaCorriente.cs` es la que **crea** `movimientos_cuenta_corriente`; antes de ella no habia ningun ledger en este repo. El patron existia en otro proyecto (reuso de **diseño**, no de codigo). Por eso CC-01 no se ancla en el piso de esa banda. |
| `dataset.yml` → "Agregar campo simple" + "Migracion EF" + "Agregar regla de negocio" | 0.5 + 0.5 + 1–2 h | Ancla de U-01. |
| `dataset.yml` → "Nuevo reporte o exportacion (sobre modulo existente)" | M 1–2 h (med 1.5) | Ancla de U-02. |

**Rondas previas del mismo proyecto: SI** (4+ cerradas: evolutiva Junio, batch F1-F4, Dashboard Ampliado, Editar Pago). Aplica la regla de "segunda/tercera ronda sobre el mismo modulo" → se usa el **piso** de las bandas de reutilizacion, no la mediana. Se aplico en U-01, U-02, CC-04 y CC-05.

### Lote CC — Cuenta Corriente de Clientes + Pagos a cuenta corriente (YA ENTREGADO)

Alcance reconstruido de los commits reales: `7430a66` (2026-07-31, 680 inserciones / 15 archivos) + `8f093ec` (2026-10-01).

| ID | Modulo | Naturaleza | O | M | P | PERT | Riesgo | H.Finales | Facturables | USD lista |
|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|
| CC-01 | Ledger de cuenta corriente: `MovimientoCuentaCorriente` + enum `TipoMovimientoCuentaCorriente` + migracion EF + `Cliente.GetSaldoCuentaCorriente` (monto signado) | Modulo financiero nuevo en el repo | 1.5 | 2.0 | 3.0 | 2.08 | Bajo +8% | 2.25 | 0.96 | 33.60 |
| CC-02 | Pantalla `Clientes/CuentaCorriente` (listado de movimientos + saldo) + `RegistrarAjusteCuentaCorriente` solo Administrador, con observacion obligatoria | Pantalla nueva reutilizando UI/AJAX del repo | 1.5 | 2.0 | 3.5 | 2.17 | Bajo +8% | 2.34 | 0.96 | 33.60 |
| CC-03 | Integracion con Pagos: sobrepago → Credito real (con clamp del excedente), `MetodoPago == SaldoFavor` → Debito validado contra saldo real, `EliminarPago` revierte el movimiento vinculado | Modificacion de modulo financiero, 3 reglas nuevas | 2.0 | 3.0 | 5.0 | 3.17 | Medio +15% | 3.64 | 1.44 | 50.40 |
| CC-04 | Indicadores de saldo: columna en `Clientes/Index`, bloque en `Clientes/Details`, aviso de saldo disponible en el modal Registrar Pago de Ventas | Ajuste puntual x3 vistas | 0.7 | 1.0 | 1.5 | 1.03 | Bajo +8% | 1.12 | 0.48 | 16.80 |
| CC-05 | Permitir cobrar de mas una venta ya cubierta (habilita el sobrepago desde la UI — `PagoService` + 2 vistas, 2026-10-01) | Regla de negocio sobre modulo existente | 0.7 | 1.0 | 1.8 | 1.08 | Bajo +8% | 1.17 | 0.48 | 16.80 |
| **Total** | | | | **9.0** | | **9.53** | | **10.52** | **4.32** | **151.20** |

Distribucion interna del esfuerzo (trazabilidad, NO adicionales): implementacion ~65%, pruebas ~20%, documentacion ~5%, riesgo ~10% — todo absorbido dentro del PERT + contingencia por riesgo ya aplicada.

**Migracion EF: SI** — `202608010201110_CuentaCorriente` (ya aplicada en produccion). Contemplada dentro de CC-01, no como linea aparte.

#### Lo que NO se cobra de este lote (garantia, decision explicita)

El hotfix `32fe140` (2026-08-21) corrige defectos **de la propia entrega** del 31/07 y por lo tanto **no se factura**: lock de concurrencia en `RegistrarPago` (race condition con 2 casos reales en produccion), reversion del movimiento en `VentasController.DeleteConfirmed`, guard server-side de `venta.Estado`, aviso visual de Nota de Credito con pagos registrados, mas la correccion manual de los 2 movimientos faltantes en la base de produccion. Esfuerzo real equivalente ~2 h M (~USD 34 a precio de lista) absorbido por la contingencia temporal del 20% que ya esta dentro de la formula. Se expone al cliente como linea "sin cargo" — es valor entregado, conviene que lo vea.

Tampoco se cobra la iteracion "Editar Pago" (`ab47dc3`, 2026-09-07): ya quedo registrada mas arriba en esta memoria como **deuda tecnica interna** por decision explicita de Joaquin, con presupuesto salteado. No se reabre.

### Lote USR — Desactivar usuarios que no usan el sistema (A DESARROLLAR)

Alcance **declarado por el presupuestador** (no hay definicion funcional previa). Estado verificado del codigo: `ApplicationUsersController` tiene Index/Create/Edit/Detalle/DeleteConfirmed/ResetPassword/AsignarPassword pero **ninguna accion de activar/desactivar**; `ApplicationUser : IdentityUser` tiene `CreatedAt/UpdatedAt/DeletedAt` pero **ningun campo de habilitacion**; el listado es un `.ToList()` en memoria filtrado por rol (no DataTables server-side); `login_audits` ya captura cada intento de login con `FechaHora`, `Exitoso` y `MotivoFalla`, y `LoginAuditsController` ya tiene su pantalla.

| ID | Modulo | Naturaleza | O | M | P | PERT | Riesgo | H.Finales | Facturables | USD lista |
|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|
| U-01 | Baja logica de usuario: campo `Activo` + migracion EF, boton Activar/Desactivar en el listado (AJAX + SweetAlert, patron ya existente), bloqueo en el login con motivo registrado en `login_audits`, guards (no desactivarse a si mismo, no dejar el sistema sin Administrador activo) | Campo + migracion + reglas de negocio sobre modulo existente | 1.4 | 2.0 | 3.2 | 2.10 | Bajo +8% | 2.27 | 0.96 | 33.60 |
| U-02 | Columna "Ultimo acceso" en el listado de usuarios + filtro "sin ingresar hace mas de N dias", sobre `login_audits` ya existente | Reporte/columna sobre modulo existente | 0.7 | 1.0 | 1.6 | 1.05 | Bajo +8% | 1.13 | 0.48 | 16.80 |
| **Total** | | | | **3.0** | | **3.15** | | **3.40** | **1.44** | **50.40** |

**Migracion EF: SI** — 1 migracion (`Activo` en `AspNetUsers`). Dentro de U-01.
**Opcional no incluido (si el cliente lo pide):** desactivacion **automatica** por inactividad (job programado + politica de N dias + aviso previo) → M ~1 h adicional, USD 17. No se incluye por defecto: desactivar una cuenta por error deja a alguien sin poder trabajar, y la decision manual es mas segura.

#### Gate del lote USR

Definiciones 1/2/3 **no existen** para este item: el pedido llego como conversacion y no hay relevamiento escrito. Se entrega estimacion preliminar con alcance declarado, segun la regla "si el discovery es incompleto, devolver rango y sugerir fase corta de relevamiento". **Tres puntos a confirmar con el cliente antes de comprometer el numero final:**
1. Desactivar = no puede entrar pero se conserva todo su historico (lo asumido), o eliminar la cuenta.
2. Quien decide: el Administrador a mano (lo asumido) o una regla automatica por dias de inactividad.
3. Si hace falta avisar al usuario (mail) cuando se lo desactiva. No incluido en los USD 50.

Si los tres se confirman como asumidos, el numero no se mueve. Si entra la regla automatica, el lote pasa a USD 67.

### PASO 7 — Autocorreccion por item

| ID | PERT | Referencia | Base ref | Ratio | Decision |
|---|---:|---|---:|---:|---|
| CC-01 | 2.08 | dataset "Nuevo ledger reutilizando patron" (med) | 1.25 | 1.67 | **Justificado al alza.** El chequeo de la regla 2026-10-06 mostro que en este repo no habia ledger previo: entidad, enum, migracion y saldo signado se escribieron de cero; el reuso fue de diseño (PAT-001 en otro proyecto), no de codigo. Usar el piso de esa banda habria sido el error de La Platense al reves: cotizar como reuso lo que no tuvo base. |
| CC-02 | 2.17 | DN F3 Totalizador Pagos (mismo proyecto) | 2.16 | 1.00 | En rango. Sin ajuste. |
| CC-03 | 3.17 | DN F3 Totalizador Pagos (mismo proyecto) | 2.16 | 1.47 | **Justificado al alza.** Tres reglas de negocio nuevas sobre el flujo de cobro, todas con efecto en dinero del cliente (clamp del excedente, validacion contra saldo real, reversion del movimiento al eliminar). Es el item de mayor riesgo del lote — confirmado a posteriori: es el unico que despues mostro un defecto real en produccion. |
| CC-04 | 1.03 | dataset "Ajuste puntual" (med) x3 vistas | 0.75 | 1.38 | **Justificado al alza** (son 3 vistas distintas), pero acotado por el piso de la regla de rondas repetidas: las 3 consumen el mismo `GetSaldoCuentaCorriente` ya construido en CC-01, sin logica propia. |
| CC-05 | 1.08 | dataset "Agregar regla de negocio" (med) | 1.5 | 0.72 | **Justificado a la baja.** Cambio acotado y verificado: 70 lineas en `PagoService` + 2 vistas, sin entidad ni migracion. No falta alcance. |
| U-01 | 2.10 | dataset campo (0.5) + migracion (0.5) + regla de negocio (med 1.5) | 2.5 | 0.84 | **Justificado a la baja.** El toggle AJAX + SweetAlert y el registro en `login_audits` ya existen en el repo; se reutilizan, no se construyen. |
| U-02 | 1.05 | dataset "Nuevo reporte o exportacion" (med) | 1.5 | 0.70 | **Justificado a la baja.** El dato ya se captura (`login_audits.FechaHora`) y el listado ya existe: es una columna mas un filtro, no un reporte nuevo. Aplica el piso por ronda repetida. |

### PASO 8 — Sanity check del total

| Lote | M/item | Comparable (mismo proyecto) | M/item ref | Ratio | Decision |
|---|---:|---|---:|---:|---|
| CC (5 items) | 1.80 | Dashboard Ampliado (5 items) | 2.10 | 0.86 | Dentro de 0.80–1.20. OK. |
| USR (2 items) | 1.50 | Dashboard Ampliado | 2.10 | 0.71 | Fuera por abajo. **Justificado, no se recalibra al alza:** los 2 items son modificaciones sobre un listado que ya existe, con el dato ya capturado, y aplica la regla de ronda repetida (DN lleva 4+ rondas) que manda usar el piso de las bandas. |

Cross-check contra el acumulado del proyecto: DN lleva 95 h base historicas + ~22 h de iteraciones evolutivas. Este lote suma 12 h M. Coherente con la escala de las rondas anteriores (8 h y 10.5 h).

### PASO 9 — Cierre numerico por dos pasos

- **Paso A (preliminar):** CC USD 151.20 + USR USD 50.40 = **USD 201.60**.
- **Paso B (final):** sin cambios por sanity check. Sin descuentos (Merge/post-entrega va siempre a precio de lista). Contingencia aplicada **una sola vez** (20% dentro de la formula; el riesgo por item se aplica sobre el PERT interno, que no toca el precio porque el precio sale de M). Redondeo comercial a la baja: **CC USD 150 + USR USD 50 = USD 200**.

### Tokens IA — NO se cobra (precedente del cliente)

Facturables del lote CC = 4.32 h > 4 h, asi que por la regla general el 25% **corresponderia** (USD 37.80, factor x1.25 distribuido dentro de cada modulo). **No se aplica**, por consistencia con las dos iteraciones anteriores de este mismo cliente, donde quedo registrado "Tokens IA: no facturado (decision comercial del cliente)". El lote USR no califica igual (1.44 h facturables < 4 h). Si Joaquin decide alinearse a la regla general, el total pasa de USD 200 a USD 238 — es una decision comercial, no un recalculo.

### Mantenimiento anual — fuera de alcance de esta iteracion

Sin linea en el documento cliente: DN ya declino el plan anual como decision comercial registrada, y esta no es una Build inicial. Dato para tenerlo a mano si se reabre: **28 tablas de negocio** (28 `DbSet` en `Data/ApplicationDbContext.cs`) → plan **PREMIUM, USD 600/año + IVA** por la tabla vigente 2026-09-19. La cantidad de usuarios no entra en ese calculo.

### PASO 10 — Costo interno de IA (NUNCA visible al cliente)

| Lote | Facturables | Costo_IA (x USD 4/h Opus) | 15% del precio de lista | Ajuste |
|---|---:|---:|---:|---|
| CC | 4.32 h | USD 17.28 | USD 22.68 | No aplica |
| USR | 1.44 h | USD 5.76 | USD 7.56 | No aplica |

`Costo_IA_overhead_proyecto` = 1.5 h Ask-mode x USD 1/h = **USD 1.50** (iteracion evolutiva, no proyecto nuevo: no corresponde el placeholder de 4 h).

**Nota estructural para proximos presupuestos:** en la linea Merge/Extras el umbral nunca se dispara por construccion — `Costo_IA = M x 0.48 x 4 = M x 1.92` contra un umbral de `M x 16.80 x 0.15 = M x 2.52`. En Build (factor 4.0) pasa lo inverso: umbral `M x 10.50 x 0.15 = M x 1.575` contra `M x 0.30 x 4 = M x 1.20`... tambien queda abajo. Revisado: el umbral no se dispara en ninguna de las dos lineas con las tarifas placeholder vigentes. Vale confirmar con `olvidata-ceo` si el placeholder de USD 4/h sigue siendo representativo ahora que Implementador y QA corren en Opus.

### Condiciones comerciales de esta iteracion

- Lote CC: **ya entregado y en produccion** — pago contra presentacion, sin anticipo (no hay nada por entregar).
- Lote USR: 50/50 (50% para arrancar, 50% contra entrega).
- Moneda USD. Sin clausula de validez de oferta.
- Si el alcance del lote USR crece sobre lo declarado (los 3 puntos del gate), se recotiza ese item.

## Historial de ajustes (continuacion)
- 2026-10-06: **Lote CC** (cuenta corriente + pagos a cuenta corriente, ya en produccion desde 2026-07-31) presupuestado retroactivamente para cobro: M 9 h, USD 151.20 lista → **USD 150** al cliente. Hotfix 21/08 declarado garantia sin cargo. **Lote USR** (desactivar usuarios inactivos) estimado preliminar: M 3 h, **USD 50**, con gate de 3 puntos a confirmar. Total **USD 200**. Tokens IA no cobrado por precedente del cliente (seria +USD 38). Sin descuentos: linea Merge/post-entrega a precio de lista.
